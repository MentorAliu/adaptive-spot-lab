import { useQueryClient } from "@tanstack/react-query"
import type { QueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useEffect, useRef } from "react"
import { toast } from "@/components/ui/toast"
import { LiveConnection } from "./live"
import type { LiveActivity, LiveMessage } from "./live"
import {
  SEEN_WAIT_MS,
  after,
  desktopAlerts,
  moreText,
  plan,
  popupFor,
  popups,
  showPopup,
  storeCursor,
  storedCursor,
} from "./live-alerts"
import { setLiveState } from "./live-state"
import type { LiveState } from "./live-state"
import { toastFor } from "@/spot/parts"
import { SPOT_KEY, readSpotActivity } from "@/spot/spot.query"
import type { Activity } from "@/spot/schemas"

const AWAY = "while this page was away"
const NOW = "just now"
const SUMMARY = "Every buy and sell is on Trades."

/** Opens the Trades page. */
type Open = () => void

/**
 * Each tab's side of the live trades (ExecPlan 0047 sections 4.5 to 4.7, the spot fills' since ExecPlan
 * 0060): the stream's events refresh the reads on screen through Query's invalidation and show the
 * toasts in a visible tab; the tab holding the stream also shows the desktop pop-ups. Returns the way to
 * stop.
 */
export function startLiveTrades(
  queryClient: QueryClient,
  open: Open,
  connection = new LiveConnection()
): () => void {
  let stopped = false
  let busy = false
  // Reads of the feed asked for: one asked while another runs makes that one read again.
  let asked = 0
  let state: LiveState = connection.state
  let reconnected = false
  // The newest cursor a tab with focus said it showed (the holder's pop-ups skip those entries).
  let seenElsewhere: string | null = null
  const timers = new Set<ReturnType<typeof setTimeout>>()

  const visible = () => document.visibilityState === "visible"

  function refresh() {
    void queryClient.invalidateQueries({ queryKey: [SPOT_KEY] })
  }

  function toasts(activity: Pick<Activity, "count" | "items">, when: string) {
    const { shown, more } = plan(activity)
    for (const item of shown)
      toast.add({
        ...toastFor(item),
        actionProps: { children: "Trades", onClick: () => open() },
      })
    if (more > 0)
      toast.add({
        title: moreText(more, when),
        description: SUMMARY,
        type: "info",
        actionProps: { children: "Trades", onClick: () => open() },
      })
  }

  /** The entries up to `cursor` are on this tab's screen: the other tabs and the holder know it. */
  function showedUpTo(cursor: string) {
    storeCursor(cursor)
    if (document.hasFocus()) connection.post({ type: "seen", cursor })
  }

  // Reads the feed after the shared cursor and shows it: when the tab starts or comes back, and when
  // an event does not follow the cursor (a new holder, or entries no tab could show).
  async function catchUp() {
    asked += 1
    if (busy) return
    busy = true
    try {
      let read = 0
      while (read !== asked) {
        read = asked
        const seen = storedCursor()
        const activity = await readSpotActivity(seen)
        if (stopped) return
        if (seen !== null && activity.items.length > 0) toasts(activity, AWAY)
        if (seen === null || activity.cursor !== seen)
          showedUpTo(activity.cursor)
      }
    } catch {
      // The engine is away: the next event or return reads again; nothing is guessed.
    } finally {
      busy = false
    }
  }

  function onReady(cursor: string) {
    const seen = storedCursor()
    // A fresh browser starts at the newest entry; a ledger older than the cursor (a restore) too.
    if (seen === null || after(seen, cursor)) storeCursor(cursor)
    else if (after(cursor, seen) && visible()) void catchUp()
    if (reconnected) refresh()
    reconnected = true
  }

  function onActivity(activity: LiveActivity) {
    refresh()
    if (connection.holding) popupsFor(activity)
    // A hidden tab leaves the cursor: it shows these when it comes back, unless a visible one does.
    if (!visible()) return
    const seen = storedCursor()
    if (seen === null) storeCursor(activity.cursor)
    else if (seen === activity.after) {
      toasts(activity, NOW)
      showedUpTo(activity.cursor)
    } else if (after(activity.cursor, seen)) void catchUp()
  }

  function popupsFor(activity: LiveActivity) {
    if (desktopAlerts() !== "on") return
    const { shown: fills, more } = popups(activity)
    if (fills.length === 0) return
    const timer = setTimeout(() => {
      timers.delete(timer)
      const seenThere =
        seenElsewhere !== null && !after(activity.cursor, seenElsewhere)
      if (stopped || document.hasFocus() || seenThere) return
      for (const item of fills) showPopup(popupFor(item, toastFor(item)), open)
      if (more > 0)
        showPopup(
          { title: moreText(more, NOW), body: SUMMARY, tag: "asl-fills-more" },
          open
        )
    }, SEEN_WAIT_MS)
    timers.add(timer)
  }

  function receive(message: LiveMessage) {
    switch (message.type) {
      case "state":
        setLiveState(message.state)
        // Leaving live: read everything on screen now, which also brings back the short intervals.
        if (state === "live" && message.state !== "live") refresh()
        state = message.state
        break
      case "ready":
        onReady(message.cursor)
        break
      case "activity":
        onActivity(message.activity)
        break
      case "change":
        refresh()
        break
      case "seen":
        if (seenElsewhere === null || after(message.cursor, seenElsewhere))
          seenElsewhere = message.cursor
        break
      case "hello":
        break
    }
  }

  const wake = () => {
    if (visible()) void catchUp()
  }
  const unsubscribe = connection.subscribe(receive)
  document.addEventListener("visibilitychange", wake)
  connection.start()
  wake()
  return () => {
    stopped = true
    for (const timer of timers) clearTimeout(timer)
    document.removeEventListener("visibilitychange", wake)
    unsubscribe()
    connection.stop()
    setLiveState("connecting")
  }
}

export function LiveTrades() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const navigateRef = useRef(navigate)
  useEffect(() => {
    navigateRef.current = navigate
  }, [navigate])
  useEffect(
    () =>
      startLiveTrades(queryClient, () => {
        void navigateRef.current({ to: "/trades" })
      }),
    [queryClient]
  )
  return null
}
