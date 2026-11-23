import { z } from "zod"
import { activitySchema } from "@/spot/schemas"
import type { LiveState } from "./live-state"

// The browser's one live connection (ExecPlan 0047 section 4.4; the spot account's since ExecPlan
// 0060). Over HTTP/1.1 an open EventSource takes one of the browser's six connections to the app for as
// long as it lives, in every tab, so the tab holding the Web Lock opens the only one and relays its
// events and state to the others over a BroadcastChannel; when it closes, the next tab waiting for the
// lock takes over. EventSource reconnects by itself and resumes with Last-Event-ID; a refused stream
// (not 200) is closed for good by the browser, so this tab opens a new one after 5, 10, 20 … at most
// 60 s.
export const LIVE_URL = "/api/live"
const LOCK = "asl.spot.live"
const CHANNEL = "asl.spot.live"
const RETRY_MS = [5_000, 10_000, 20_000, 40_000, 60_000]

const seq = z.string().regex(/^[0-9]{1,20}$/)
const kinds = z.array(z.string().regex(/^[A-Z][A-Z_]{0,39}$/)).max(32)
export const liveReadySchema = activitySchema.pick({
  state: true,
  cursor: true,
})
export const liveActivitySchema = activitySchema.extend({ after: seq })
export type LiveActivity = z.infer<typeof liveActivitySchema>
export const liveChangeSchema = z.strictObject({
  source: z.literal("spot"),
  kinds,
})

const stateSchema = z.enum(["connecting", "live", "offline"])
export const liveMessageSchema = z.discriminatedUnion("type", [
  z.strictObject({ type: z.literal("state"), state: stateSchema }),
  z.strictObject({ type: z.literal("ready"), cursor: seq }),
  z.strictObject({
    type: z.literal("activity"),
    activity: liveActivitySchema,
  }),
  z.strictObject({
    type: z.literal("change"),
    source: liveChangeSchema.shape.source,
    kinds,
  }),
  // A tab with focus showed the toasts up to this cursor: the holder shows no desktop pop-up for them.
  z.strictObject({ type: z.literal("seen"), cursor: seq }),
  // A tab that starts asks the holder for its state.
  z.strictObject({ type: z.literal("hello") }),
])
export type LiveMessage = z.infer<typeof liveMessageSchema>

/** Parses one event of the stream into the message the tabs share, or null if it is not one. */
export function eventMessage(name: string, data: string): LiveMessage | null {
  let value: unknown
  try {
    value = JSON.parse(data)
  } catch {
    return null
  }
  if (name === "ready") {
    const ready = liveReadySchema.safeParse(value)
    return ready.success ? { type: "ready", cursor: ready.data.cursor } : null
  }
  if (name === "activity") {
    const activity = liveActivitySchema.safeParse(value)
    return activity.success
      ? { type: "activity", activity: activity.data }
      : null
  }
  if (name === "change") {
    const change = liveChangeSchema.safeParse(value)
    return change.success ? { type: "change", ...change.data } : null
  }
  return null
}

export function retryDelay(attempt: number): number {
  return RETRY_MS[Math.min(attempt, RETRY_MS.length) - 1] ?? RETRY_MS[0]
}

type Listener = (message: LiveMessage) => void

export class LiveConnection {
  state: LiveState = "connecting"
  /** Whether this tab holds the lock and so the connection. */
  holding = false
  private readonly listeners = new Set<Listener>()
  private readonly stopped = new AbortController()
  private channel: BroadcastChannel | null = null
  private source: EventSource | null = null
  private attempts = 0
  private timer: ReturnType<typeof setTimeout> | undefined
  private release: (() => void) | null = null

  constructor(private readonly url = LIVE_URL) {}

  subscribe(listener: Listener) {
    this.listeners.add(listener)
    return () => {
      this.listeners.delete(listener)
    }
  }

  start() {
    if (typeof BroadcastChannel === "function") {
      this.channel = new BroadcastChannel(CHANNEL)
      this.channel.addEventListener("message", (event: MessageEvent) =>
        this.receive(event.data)
      )
    }
    const locks = typeof navigator === "undefined" ? undefined : navigator.locks
    if (this.channel === null || typeof locks?.request !== "function") {
      // Without the lock or the channel, each tab keeps its own connection.
      this.hold()
      return
    }
    locks
      .request(
        LOCK,
        { signal: this.stopped.signal },
        () =>
          new Promise<void>((resolve) => {
            this.release = resolve
            this.hold()
          })
      )
      .catch(() => {
        // Stopped while waiting for the lock: nothing to release.
      })
    this.post({ type: "hello" })
  }

  stop() {
    this.stopped.abort()
    clearTimeout(this.timer)
    this.source?.close()
    this.source = null
    this.holding = false
    this.release?.()
    this.release = null
    this.channel?.close()
    this.channel = null
    this.listeners.clear()
  }

  /** Sends a message to the other tabs (the holder answers some of them). */
  post(message: LiveMessage) {
    try {
      this.channel?.postMessage(message)
    } catch {
      // The channel is closed: this tab is going away.
    }
  }

  private hold() {
    if (this.stopped.signal.aborted) return
    this.holding = true
    this.open()
  }

  private open() {
    if (this.stopped.signal.aborted) return
    this.setState(this.state === "offline" ? "offline" : "connecting")
    const source = new EventSource(this.url)
    this.source = source
    source.addEventListener("open", () => {
      this.attempts = 0
      this.setState("live")
    })
    for (const name of ["ready", "activity", "change"])
      source.addEventListener(name, (event) => {
        const message = eventMessage(name, String(event.data))
        if (message !== null) this.share(message)
      })
    source.addEventListener("error", () => {
      if (source.readyState === EventSource.CLOSED) {
        // Refused: the browser does not try this stream again; this tab does, later.
        source.close()
        if (this.source === source) this.source = null
        this.attempts += 1
        this.setState("offline")
        this.timer = setTimeout(() => this.open(), retryDelay(this.attempts))
      } else {
        // Lost: the browser reconnects by itself and resumes after the last event it had.
        this.setState(this.state === "live" ? "connecting" : "offline")
      }
    })
  }

  private setState(state: LiveState) {
    if (state === this.state) return
    this.state = state
    this.share({ type: "state", state })
  }

  /** The holder's message: to this tab's listeners and to the other tabs. */
  private share(message: LiveMessage) {
    this.deliver(message)
    this.post(message)
  }

  private deliver(message: LiveMessage) {
    for (const listener of this.listeners) listener(message)
  }

  private receive(data: unknown) {
    const parsed = liveMessageSchema.safeParse(data)
    if (!parsed.success) return
    const message = parsed.data
    if (message.type === "hello") {
      if (this.holding) this.post({ type: "state", state: this.state })
      return
    }
    // The holder's own state wins over what another tab says it has.
    if (message.type === "state") {
      if (this.holding) return
      this.state = message.state
    }
    this.deliver(message)
  }
}
