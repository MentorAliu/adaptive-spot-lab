import { infiniteQueryOptions, queryOptions } from "@tanstack/react-query"
import { liveState } from "@/live/live-state"
import {
  getCandles,
  getMarket,
  getSpotActivity,
  getSpotBacktest,
  getSpotDefinitions,
  getSpotMarkers,
  getSpotOverview,
  getSpotReadings,
  getSpotTrades,
  getSpotValuations,
} from "./spot.functions"
import type { BacktestWindowKey, Interval, ValuationWindow } from "./schemas"

// The engine steps every second; the rule reads once a UTC day just after 00:05 and a stopping run sells
// at once. The overview follows at 2 s for the value at the bid, the lists at 5 s. While the live
// stream is open it says when a fill or a run's state changes, and each change refreshes these reads,
// so their polls only back it up (ExecPlan 0047). Query pauses polling in background tabs.
const LIVE_MS = 2_000
const LIST_MS = 5_000
const BACKUP_MS = 60_000

function backedUp(ms: number) {
  return () => (liveState() === "live" ? BACKUP_MS : ms)
}

// Every spot read shares this first key: the live stream's changes refresh them all.
export const SPOT_KEY = "spot"

export const spotOverviewQuery = queryOptions({
  queryKey: [SPOT_KEY, "overview", "M12"] as const,
  queryFn: ({ signal }) => getSpotOverview({ signal }),
  refetchInterval: LIVE_MS,
  retry: false,
})

/** The Cockpit's latest trades. */
export const RECENT_TRADES = 6

export const recentTradesQuery = queryOptions({
  queryKey: [SPOT_KEY, "recent-trades", "M12"] as const,
  queryFn: ({ signal }) =>
    getSpotTrades({ data: { cursor: null, limit: RECENT_TRADES }, signal }),
  refetchInterval: backedUp(LIST_MS),
  retry: false,
})

/** Trades shows fifty at a time; Load more reads the older ones. */
export const TRADES_PAGE = 50

export function tradesListQuery() {
  return infiniteQueryOptions({
    queryKey: [SPOT_KEY, "trades-list", "M12"] as const,
    queryFn: ({ pageParam, signal }) =>
      getSpotTrades({
        data: { cursor: pageParam, limit: TRADES_PAGE },
        signal,
      }),
    initialPageParam: null as string | null,
    getNextPageParam: (last) => last.next_cursor,
    refetchInterval: backedUp(LIST_MS),
    retry: false,
  })
}

/** The daily readings, newest first, about two months a page. */
export const READINGS_PAGE = 60

export function readingsListQuery() {
  return infiniteQueryOptions({
    queryKey: [SPOT_KEY, "readings-list", "M12"] as const,
    queryFn: ({ pageParam, signal }) =>
      getSpotReadings({
        data: { cursor: pageParam, limit: READINGS_PAGE },
        signal,
      }),
    initialPageParam: null as string | null,
    getNextPageParam: (last) => last.next_cursor,
    refetchInterval: backedUp(LIST_MS),
    retry: false,
  })
}

export function spotMarkersQuery(sinceMs: number | null) {
  return queryOptions({
    queryKey: [SPOT_KEY, "markers", sinceMs, "M12"] as const,
    queryFn: ({ signal }) =>
      getSpotMarkers({ data: { sinceMs: sinceMs ?? 0 }, signal }),
    enabled: sinceMs !== null,
    refetchInterval: backedUp(LIST_MS),
    retry: false,
  })
}

// The engine values the account each minute while it holds Bitcoin it can sell, and each hour while it
// holds only USDT; the curve's buckets are 15 minutes and longer, so a minute is fresh enough.
const VALUATIONS_MS = 60_000

export function spotValuationsQuery(window: ValuationWindow) {
  return queryOptions({
    queryKey: [SPOT_KEY, "valuations", window, "M12"] as const,
    queryFn: ({ signal }) => getSpotValuations({ data: { window }, signal }),
    refetchInterval: VALUATIONS_MS,
    retry: false,
  })
}

// The backtest is computed once after the install and again once a new final day is stored, so a
// minute is fresh enough; until it is computed the page reads again every 10 s.
const BACKTEST_MS = 60_000
const BACKTEST_WAIT_MS = 10_000

export function backtestQuery(window: BacktestWindowKey) {
  return queryOptions({
    queryKey: [SPOT_KEY, "backtest", window, "M12"] as const,
    queryFn: ({ signal }) => getSpotBacktest({ data: { window }, signal }),
    refetchInterval: (query) =>
      query.state.data?.state === "READY" ? BACKTEST_MS : BACKTEST_WAIT_MS,
    retry: false,
  })
}

/** The rule, policy and costs in force: they change only with an update. */
export const definitionsQuery = queryOptions({
  queryKey: [SPOT_KEY, "definitions", "M12"] as const,
  queryFn: ({ signal }) => getSpotDefinitions({ signal }),
  staleTime: 5 * 60_000,
  retry: false,
})

// The market's state: the book every second, the instrument and the clock every few minutes.
const MARKET_MS = 2_000

export const marketQuery = queryOptions({
  queryKey: ["market", "overview", "M12"] as const,
  queryFn: ({ signal }) => getMarket({ signal }),
  refetchInterval: MARKET_MS,
  retry: false,
})

/** How many candles each interval draws: a year of days, about a month of 4-hour candles. */
export const CANDLE_LIMIT: Record<Interval, number> = {
  "1m": 360,
  "5m": 288,
  "15m": 384,
  "1h": 336,
  "4h": 180,
  "1d": 365,
}

// A daily candle's today part moves with each minute; shorter ones each minute too.
const CANDLES_MS: Record<Interval, number> = {
  "1m": 2_000,
  "5m": 5_000,
  "15m": 5_000,
  "1h": 10_000,
  "4h": 30_000,
  "1d": 30_000,
}

export function candlesQuery(interval: Interval) {
  return queryOptions({
    queryKey: ["market", "candles", interval, "M12"] as const,
    queryFn: ({ signal }) =>
      getCandles({
        data: { interval, limit: CANDLE_LIMIT[interval] },
        signal,
      }),
    refetchInterval: CANDLES_MS[interval],
    retry: false,
  })
}

/** The toasts' feed: read directly by the live trades (`live-trades.tsx`), which keep their cursor. */
export function readSpotActivity(after: string | null) {
  return getSpotActivity({ data: { after } })
}
