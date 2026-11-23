import { QueryClient } from "@tanstack/react-query"
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { AlertsMenu, LiveBadge } from "@/components/live-status"
import activitySample from "@/spot/samples/activity.json"
import { activitySchema } from "@/spot/schemas"
import type { Backtest, Trade } from "@/spot/schemas"
import {
  backtestQuery,
  definitionsQuery,
  readingsListQuery,
  recentTradesQuery,
  spotMarkersQuery,
  spotOverviewQuery,
  spotValuationsQuery,
  tradesListQuery,
} from "@/spot/spot.query"
import { LiveConnection, eventMessage, retryDelay } from "./live"
import type { LiveActivity, LiveMessage } from "./live"
import {
  CURSOR_KEY,
  DESKTOP_KEY,
  SEEN_WAIT_MS,
  plan,
  popups,
} from "./live-alerts"
import { liveState, setLiveState } from "./live-state"
import { startLiveTrades } from "./live-trades"
// ExecPlan 0047, the spot fills' since ExecPlan 0060: the live trades in the browser, on events shaped
// as the engine's /v1/spot/live stream sends them, around the fills the engine wrote on the browser
// chain's scratch database (src/spot/samples/activity.json: a buy, the owner's Stop and sell, a buy).
// The stream, the lock, the channel and the notifications are stand-ins: jsdom has none of them.
const feed = vi.hoisted(() => ({ read: vi.fn(), add: vi.fn() }))
vi.mock(import("@/spot/spot.query"), async (original) => ({
  ...(await original()),
  readSpotActivity: feed.read,
}))
vi.mock("@/components/ui/toast", () => ({ toast: { add: feed.add } }))

const [BUY, STOP_SELL] = activitySchema.parse(activitySample).items

function item(fields: Partial<Trade> = {}): Trade {
  return { ...BUY, seq: "6", ...fields }
}

function activity(
  after: string,
  cursor: string,
  items: Trade[],
  count = items.length
): LiveActivity {
  return { state: "READY", after, cursor, count, items }
}

const BOUGHT = "Bought 0.00835 BTC at 61,037.41 USDT"

// ---- stand-ins ------------------------------------------------------------------------------------

type Handler = (event: Event) => void

class FakeSource {
  static readonly CONNECTING = 0
  static readonly OPEN = 1
  static readonly CLOSED = 2
  static made: FakeSource[] = []
  readyState = FakeSource.CONNECTING
  private readonly handlers = new Map<string, Set<Handler>>()

  constructor(readonly url: string) {
    FakeSource.made.push(this)
  }

  addEventListener(name: string, handler: Handler) {
    const set = this.handlers.get(name) ?? new Set()
    set.add(handler)
    this.handlers.set(name, set)
  }

  close() {
    this.readyState = FakeSource.CLOSED
  }

  emit(name: string, data?: unknown) {
    const event =
      data === undefined
        ? new Event(name)
        : new MessageEvent(name, { data: JSON.stringify(data) })
    for (const handler of this.handlers.get(name) ?? []) handler(event)
  }

  open() {
    this.readyState = FakeSource.OPEN
    this.emit("open")
  }

  refuse() {
    this.readyState = FakeSource.CLOSED
    this.emit("error")
  }

  lose() {
    this.readyState = FakeSource.CONNECTING
    this.emit("error")
  }
}

class FakeChannel {
  static open = new Set<FakeChannel>()
  private readonly handlers = new Set<(event: { data: unknown }) => void>()

  constructor(readonly name: string) {
    FakeChannel.open.add(this)
  }

  addEventListener(_: string, handler: (event: { data: unknown }) => void) {
    this.handlers.add(handler)
  }

  postMessage(data: unknown) {
    for (const other of FakeChannel.open)
      if (other !== this && other.name === this.name)
        for (const handler of other.handlers)
          handler({ data: structuredClone(data) })
  }

  close() {
    FakeChannel.open.delete(this)
  }
}

type Waiting = {
  grant: () => Promise<unknown>
  done: (value: unknown) => void
  refuse: (error: unknown) => void
}

/** One lock, granted in order; a holder keeps it while its callback's promise is pending. */
class FakeLocks {
  private held = false
  private readonly waiting: Waiting[] = []

  request(
    _: string,
    options: { signal?: AbortSignal },
    callback: () => Promise<unknown>
  ) {
    return new Promise((done, refuse) => {
      const entry: Waiting = { grant: callback, done, refuse }
      options.signal?.addEventListener("abort", () => {
        const index = this.waiting.indexOf(entry)
        if (index >= 0) {
          this.waiting.splice(index, 1)
          refuse(new DOMException("Aborted", "AbortError"))
        }
      })
      this.waiting.push(entry)
      this.next()
    })
  }

  private next() {
    if (this.held) return
    const entry = this.waiting.shift()
    if (entry === undefined) return
    this.held = true
    void entry.grant().then((value) => {
      this.held = false
      entry.done(value)
      this.next()
    })
  }
}

const shown: { title: string; options: NotificationOptions }[] = []

class FakeNotification {
  static permission: NotificationPermission = "granted"
  static requestPermission = vi.fn(async () => FakeNotification.permission)
  onclick: (() => void) | null = null
  closed = false

  constructor(
    readonly title: string,
    readonly options: NotificationOptions
  ) {
    shown.push(this)
    made.push(this)
  }

  close() {
    this.closed = true
  }
}
const made: FakeNotification[] = []

let focused = true
let visibility: DocumentVisibilityState = "visible"

beforeEach(() => {
  vi.useFakeTimers()
  window.localStorage.clear()
  FakeSource.made = []
  FakeChannel.open = new Set()
  shown.length = 0
  made.length = 0
  FakeNotification.permission = "granted"
  focused = true
  visibility = "visible"
  vi.stubGlobal("EventSource", FakeSource)
  vi.stubGlobal("BroadcastChannel", FakeChannel)
  vi.stubGlobal("Notification", FakeNotification)
  Object.defineProperty(navigator, "locks", {
    configurable: true,
    value: new FakeLocks(),
  })
  Object.defineProperty(document, "visibilityState", {
    configurable: true,
    get: () => visibility,
  })
  vi.spyOn(document, "hasFocus").mockImplementation(() => focused)
  setLiveState("connecting")
})

afterEach(() => {
  cleanup()
  vi.useRealTimers()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
  feed.read.mockReset()
  feed.add.mockReset()
})

async function settle() {
  await act(async () => {
    await vi.advanceTimersByTimeAsync(0)
  })
}

// ---- one connection --------------------------------------------------------------------------------

describe("the browser's one live connection", () => {
  it("is opened by one tab and shared with the others; the next tab takes over when it closes", async () => {
    const tabs = [
      new LiveConnection(),
      new LiveConnection(),
      new LiveConnection(),
    ]
    const heard = tabs.map(() => [] as LiveMessage[])
    tabs.forEach((tab, n) => tab.subscribe((message) => heard[n].push(message)))
    for (const tab of tabs) tab.start()
    await settle()
    expect(FakeSource.made).toHaveLength(1)
    expect(FakeSource.made[0].url).toBe("/api/live")
    expect(tabs.map((tab) => tab.holding)).toEqual([true, false, false])
    FakeSource.made[0].open()
    expect(tabs.map((tab) => tab.state)).toEqual(["live", "live", "live"])
    const fill = activity("4", "6", [item()])
    FakeSource.made[0].emit("activity", fill)
    for (const messages of heard)
      expect(messages).toContainEqual({ type: "activity", activity: fill })
    // The holder closes: the next tab opens the connection.
    tabs[0].stop()
    await settle()
    expect(FakeSource.made).toHaveLength(2)
    expect(tabs.map((tab) => tab.holding)).toEqual([false, true, false])
    FakeSource.made[1].open()
    expect(tabs[2].state).toBe("live")
    // A tab that starts later learns the holder's state at once.
    const late = new LiveConnection()
    late.start()
    await settle()
    expect(late.state).toBe("live")
    expect(FakeSource.made).toHaveLength(2)
    for (const tab of [...tabs, late]) tab.stop()
  })

  it("lets the browser resume a lost stream and opens a refused one again after 5, 10 … s", async () => {
    const tab = new LiveConnection()
    tab.start()
    await settle()
    const first = FakeSource.made[0]
    first.open()
    first.lose()
    expect(tab.state).toBe("connecting")
    first.open()
    expect(tab.state).toBe("live")
    first.refuse()
    expect(tab.state).toBe("offline")
    expect(first.readyState).toBe(FakeSource.CLOSED)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(4_999)
    })
    expect(FakeSource.made).toHaveLength(1)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1)
    })
    expect(FakeSource.made).toHaveLength(2)
    FakeSource.made[1].refuse()
    expect(retryDelay(2)).toBe(10_000)
    expect(retryDelay(9)).toBe(60_000)
    await act(async () => {
      await vi.advanceTimersByTimeAsync(10_000)
    })
    FakeSource.made[2].open()
    expect(tab.state).toBe("live")
    tab.stop()
  })

  it("keeps one connection per tab where the browser has no Web Locks", async () => {
    Object.defineProperty(navigator, "locks", {
      configurable: true,
      value: undefined,
    })
    const tabs = [new LiveConnection(), new LiveConnection()]
    for (const tab of tabs) tab.start()
    expect(FakeSource.made).toHaveLength(2)
    for (const tab of tabs) tab.stop()
  })

  it("passes on only the events it knows, in their shape", () => {
    expect(eventMessage("ready", '{"state":"READY","cursor":"41"}')).toEqual({
      type: "ready",
      cursor: "41",
    })
    expect(
      eventMessage("change", '{"source":"spot","kinds":["FILL","RUN"]}')
    ).toEqual({ type: "change", source: "spot", kinds: ["FILL", "RUN"] })
    expect(eventMessage("ready", "not json")).toBeNull()
    expect(eventMessage("ready", '{"state":"READY","cursor":"-1"}')).toBeNull()
    // The futures app's sources are gone with it.
    expect(eventMessage("change", '{"source":"twins","kinds":[]}')).toBeNull()
    expect(eventMessage("change", '{"source":"owner","kinds":[]}')).toBeNull()
    expect(
      eventMessage(
        "activity",
        JSON.stringify({ ...activity("4", "6", []), extra: 1 })
      )
    ).toBeNull()
    expect(eventMessage("message", '{"cursor":"1"}')).toBeNull()
  })
})

// ---- each tab ----------------------------------------------------------------------------------------

function stubConnection(holding = true) {
  const listeners = new Set<(message: LiveMessage) => void>()
  const posted: LiveMessage[] = []
  const connection = {
    state: "connecting",
    holding,
    posted,
    subscribe(listener: (message: LiveMessage) => void) {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    start: vi.fn(),
    stop: vi.fn(),
    post: (message: LiveMessage) => posted.push(message),
    send(message: LiveMessage) {
      for (const listener of listeners) listener(message)
    },
  }
  return connection
}

function trades(holding = true) {
  const connection = stubConnection(holding)
  const queryClient = new QueryClient()
  const invalidate = vi.spyOn(queryClient, "invalidateQueries")
  const open = vi.fn()
  const stop = startLiveTrades(
    queryClient,
    open,
    connection as unknown as LiveConnection
  )
  return { connection, invalidate, open, stop }
}

describe("each tab's live trades", () => {
  it("starts at the newest entry, then shows a new fill at once with its way to Trades", async () => {
    feed.read.mockResolvedValueOnce({
      state: "READY",
      cursor: "4",
      count: 0,
      items: [],
    })
    const { connection, invalidate, open, stop } = trades()
    await settle()
    expect(feed.read).toHaveBeenCalledWith(null)
    expect(feed.add).not.toHaveBeenCalled()
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("4")
    connection.send({
      type: "activity",
      activity: activity("4", "6", [item()]),
    })
    expect(feed.add).toHaveBeenCalledTimes(1)
    const toast = feed.add.mock.calls[0][0]
    expect(toast).toMatchObject({
      title: BOUGHT,
      description: "Trend up 2 of 3: target 5.1%, held 0.0%. Fee 0.51 USDT.",
      type: "info",
    })
    expect(toast.actionProps.children).toBe("Trades")
    toast.actionProps.onClick()
    expect(open).toHaveBeenCalledWith()
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["spot"] })
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("6")
    // The tab has focus: the holder hears that these are seen.
    expect(connection.posted).toContainEqual({ type: "seen", cursor: "6" })
    expect(feed.read).toHaveBeenCalledTimes(1)
    stop()
    expect(connection.stop).toHaveBeenCalled()
  })

  it("leaves a hidden tab's cursor, then shows three and a summary when it comes back", async () => {
    window.localStorage.setItem(CURSOR_KEY, "4")
    visibility = "hidden"
    const { connection, stop } = trades()
    connection.send({
      type: "activity",
      activity: activity("4", "16", [item({ seq: "16" })], 5),
    })
    expect(feed.add).not.toHaveBeenCalled()
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("4")
    feed.read.mockResolvedValueOnce({
      state: "READY",
      cursor: "16",
      count: 5,
      items: ["8", "10", "12", "14", "16"].map((seq) => item({ seq })),
    })
    visibility = "visible"
    document.dispatchEvent(new Event("visibilitychange"))
    await settle()
    expect(feed.read).toHaveBeenCalledWith("4")
    expect(feed.add).toHaveBeenCalledTimes(4)
    expect(feed.add.mock.calls[3][0].title).toBe(
      "2 more entries while this page was away"
    )
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("16")
    stop()
  })

  it("reads the feed after its cursor when an event does not follow it, and starts again after a clean start", async () => {
    window.localStorage.setItem(CURSOR_KEY, "2")
    feed.read.mockResolvedValue({
      state: "READY",
      cursor: "2",
      count: 0,
      items: [],
    })
    const { connection, stop } = trades()
    await settle()
    feed.read.mockClear()
    feed.read.mockResolvedValueOnce({
      state: "READY",
      cursor: "6",
      count: 2,
      items: [item({ seq: "3" }), item({ seq: "6" })],
    })
    connection.send({
      type: "activity",
      activity: activity("4", "6", [item()]),
    })
    await settle()
    expect(feed.read).toHaveBeenCalledWith("2")
    expect(feed.add).toHaveBeenCalledTimes(2)
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("6")
    // A clean database starts its entries again: the stream's first cursor is behind this one.
    connection.send({ type: "ready", cursor: "1" })
    expect(window.localStorage.getItem(CURSOR_KEY)).toBe("1")
    stop()
  })

  it("refreshes every spot read for a change, and everything on screen when the stream goes away", async () => {
    feed.read.mockResolvedValue({
      state: "READY",
      cursor: "4",
      count: 0,
      items: [],
    })
    const { connection, invalidate, stop } = trades()
    await settle()
    connection.send({ type: "change", source: "spot", kinds: ["RUN"] })
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["spot"] })
    invalidate.mockClear()
    connection.send({ type: "state", state: "live" })
    expect(liveState()).toBe("live")
    expect(invalidate).not.toHaveBeenCalled()
    connection.send({ type: "state", state: "offline" })
    expect(liveState()).toBe("offline")
    expect(invalidate).toHaveBeenCalledWith({ queryKey: ["spot"] })
    stop()
    expect(liveState()).toBe("connecting")
  })
})

// ---- desktop pop-ups ---------------------------------------------------------------------------------

describe("desktop pop-ups", () => {
  async function fillWhile(options: {
    wanted?: boolean
    focus?: boolean
    holding?: boolean
    seenElsewhere?: boolean
  }) {
    if (options.wanted ?? true) window.localStorage.setItem(DESKTOP_KEY, "on")
    feed.read.mockResolvedValue({
      state: "READY",
      cursor: "4",
      count: 0,
      items: [],
    })
    focused = options.focus ?? false
    const context = trades(options.holding ?? true)
    await settle()
    context.connection.send({
      type: "activity",
      activity: activity("4", "6", [item({ ...STOP_SELL, seq: "5" }), item()]),
    })
    if (options.seenElsewhere)
      context.connection.send({ type: "seen", cursor: "6" })
    await act(async () => {
      await vi.advanceTimersByTimeAsync(SEEN_WAIT_MS)
    })
    return context
  }

  it("shows one for each fill while no tab of the app has focus, and a click opens Trades", async () => {
    const { open, stop } = await fillWhile({})
    expect(
      shown.map((popup) => [popup.title, popup.options.body, popup.options.tag])
    ).toEqual([
      [
        "Sold 0.00835 BTC at 61,025.20 USDT",
        "The run stopped, by you. Fee 0.51 USDT.",
        "asl-fill-5",
      ],
      [
        BOUGHT,
        "Trend up 2 of 3: target 5.1%, held 0.0%. Fee 0.51 USDT.",
        "asl-fill-6",
      ],
    ])
    const focus = vi.spyOn(window, "focus").mockImplementation(() => {})
    made[1].onclick?.()
    expect(focus).toHaveBeenCalled()
    expect(open).toHaveBeenCalledWith()
    expect(made[1].closed).toBe(true)
    stop()
  })

  it("shows none when they are off, when this tab or another has focus, or in a tab that does not hold the stream", async () => {
    for (const options of [
      { wanted: false },
      { focus: true },
      { seenElsewhere: true },
      { holding: false },
    ]) {
      const { stop } = await fillWhile(options)
      expect(shown).toEqual([])
      stop()
      window.localStorage.clear()
    }
    FakeNotification.permission = "denied"
    const { stop } = await fillWhile({})
    expect(shown).toEqual([])
    stop()
  })

  it("plans the newest three fills and a summary, as the toasts do", () => {
    const items = ["1", "2", "3", "4", "5"].map((seq) => item({ seq }))
    expect(plan({ count: 5, items }).shown.map((row) => row.seq)).toEqual([
      "3",
      "4",
      "5",
    ])
    // Every entry is a fill: the pop-ups are the toasts' plan, the entries the read left out included.
    expect(popups({ count: 5, items })).toEqual(plan({ count: 5, items }))
    expect(popups({ count: 9, items }).more).toBe(6)
    expect(popups({ count: 0, items: [] })).toEqual({ shown: [], more: 0 })
  })
})

// ---- polling -----------------------------------------------------------------------------------------

describe("the reads' polling", () => {
  type Interval = (query: unknown) => number | false
  const every = (options: { refetchInterval?: unknown }, data?: unknown) =>
    (options.refetchInterval as Interval)({ state: { data } })

  it("slows to a minute what the stream tells while it is live, and nothing that moves with the bid", () => {
    const told = [
      recentTradesQuery,
      tradesListQuery(),
      readingsListQuery(),
      spotMarkersQuery(1),
    ]
    setLiveState("live")
    for (const options of told) expect(every(options)).toBe(60_000)
    // The value at the bid moves without a fill: the overview keeps its 2 s.
    expect(spotOverviewQuery.refetchInterval).toBe(2_000)
    for (const state of ["connecting", "offline"] as const) {
      setLiveState(state)
      for (const options of told) expect(every(options)).toBe(5_000)
      expect(spotOverviewQuery.refetchInterval).toBe(2_000)
    }
    // The curve follows the engine's minute valuations, the rule's documents only an update.
    expect(spotValuationsQuery("all").refetchInterval).toBe(60_000)
    expect(definitionsQuery.refetchInterval).toBeUndefined()
    // The backtest reads every 10 s until the engine has worked it out, then each minute.
    const backtest = (state: Backtest["state"]) => ({ state }) as Backtest
    expect(every(backtestQuery("SINCE_2019"), backtest("NOT_COMPUTED"))).toBe(
      10_000
    )
    expect(every(backtestQuery("SINCE_2019"), backtest("READY"))).toBe(60_000)
  })
})

// ---- the header ----------------------------------------------------------------------------------------

describe("the header's live badge and bell", () => {
  it("says whether the trades are live", () => {
    render(<LiveBadge />)
    const status = () => screen.getByRole("status").textContent
    expect(status()).toBe("Connecting to the live trades")
    act(() => setLiveState("live"))
    expect(status()).toBe("Live: trades show the moment the engine saves them")
    act(() => setLiveState("offline"))
    expect(status()).toMatch(/^Offline: the pages refresh every few seconds/)
  })

  it("turns the pop-ups on with the browser's permission, asked on that click", async () => {
    vi.useRealTimers()
    FakeNotification.permission = "default"
    FakeNotification.requestPermission.mockClear()
    FakeNotification.requestPermission.mockImplementation(async () => {
      FakeNotification.permission = "granted"
      return "granted"
    })
    render(<AlertsMenu />)
    expect(FakeNotification.requestPermission).not.toHaveBeenCalled()
    // Base UI opens a menu on the trigger's mousedown, as a pointer does; a checkbox item keeps it open.
    fireEvent.mouseDown(screen.getByRole("button", { name: "Trade alerts" }))
    const checkbox = await screen.findByRole("menuitemcheckbox", {
      name: /Desktop pop-ups/,
    })
    expect(checkbox.getAttribute("aria-checked")).toBe("false")
    fireEvent.click(checkbox)
    expect(FakeNotification.requestPermission).toHaveBeenCalledTimes(1)
    expect(window.localStorage.getItem(DESKTOP_KEY)).toBe("on")
    await waitFor(() =>
      expect(checkbox.getAttribute("aria-checked")).toBe("true")
    )
    // Off again: the browser's permission stays, the choice goes.
    fireEvent.click(checkbox)
    await waitFor(() =>
      expect(checkbox.getAttribute("aria-checked")).toBe("false")
    )
    expect(window.localStorage.getItem(DESKTOP_KEY)).toBeNull()
    expect(FakeNotification.requestPermission).toHaveBeenCalledTimes(1)
  })
})
