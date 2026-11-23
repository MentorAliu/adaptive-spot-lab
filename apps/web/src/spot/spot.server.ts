import "@tanstack/react-start/server-only"
import { ApiError, privateApi } from "@/account/account.server"
import {
  activitySchema,
  backtestSchema,
  candlesSchema,
  definitionsSchema,
  markersSchema,
  marketSchema,
  overviewSchema,
  readingPageSchema,
  requestSchema,
  tradePageSchema,
  valuationsSchema,
} from "./schemas"
import type {
  BacktestWindowKey,
  Interval,
  RequestInput,
  ValuationWindow,
} from "./schemas"

// The spot account's and the market's reads through the private API (ExecPlan 0060 section 4.9). Only
// this server holds the service key; each answer is parsed before a page sees it.

export async function readOverview() {
  return overviewSchema.parse(await privateApi("/v1/spot"))
}

function page(cursor: string | null, limit = 25) {
  const params = new URLSearchParams({ limit: String(limit) })
  if (cursor) params.set("cursor", cursor)
  return params
}

export async function readTrades(cursor: string | null, limit?: number) {
  return tradePageSchema.parse(
    await privateApi(`/v1/spot/trades?${page(cursor, limit)}`)
  )
}

export async function readReadings(cursor: string | null, limit?: number) {
  return readingPageSchema.parse(
    await privateApi(`/v1/spot/readings?${page(cursor, limit)}`)
  )
}

export async function readActivity(after: string | null) {
  const query = after === null ? "" : `?${new URLSearchParams({ after })}`
  return activitySchema.parse(await privateApi(`/v1/spot/activity${query}`))
}

export async function readMarkers(sinceMs: number) {
  const params = new URLSearchParams({ since_ms: String(sinceMs) })
  return markersSchema.parse(await privateApi(`/v1/spot/markers?${params}`))
}

export async function readValuations(window: ValuationWindow) {
  const params = new URLSearchParams({ window })
  return valuationsSchema.parse(
    await privateApi(`/v1/spot/valuations?${params}`)
  )
}

export async function readBacktest(window: BacktestWindowKey) {
  const params = new URLSearchParams({ window })
  return backtestSchema.parse(await privateApi(`/v1/spot/backtest?${params}`))
}

export async function readDefinitions() {
  return definitionsSchema.parse(await privateApi("/v1/spot/definitions"))
}

export async function readMarket() {
  return marketSchema.parse(await privateApi("/v1/market"))
}

export async function readCandles(interval: Interval, limit: number) {
  const params = new URLSearchParams({ interval, limit: String(limit) })
  return candlesSchema.parse(await privateApi(`/v1/market/candles?${params}`))
}

/** A request's outcome: recorded, refused, or unknown (resolve it by its key). */
export type Outcome<T> =
  | { kind: "RESULT"; value: T }
  | { kind: "REJECTED"; code: string }
  | { kind: "UNKNOWN"; key: string }

export async function postRequest(input: RequestInput) {
  try {
    const { run_id, ...rest } = input
    return {
      kind: "RESULT" as const,
      value: requestSchema.parse(
        await privateApi(
          "/v1/spot/requests",
          "POST",
          run_id === null ? rest : input
        )
      ),
    }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status >= 400 &&
      error.status < 500 &&
      ![408, 425, 429].includes(error.status)
    )
      return { kind: "REJECTED" as const, code: error.code }
    return { kind: "UNKNOWN" as const, key: input.idempotency_key }
  }
}

export async function requestByKey(key: string) {
  try {
    return {
      kind: "RESULT" as const,
      value: requestSchema.parse(
        await privateApi(`/v1/spot/requests/${encodeURIComponent(key)}`)
      ),
    }
  } catch (error) {
    if (error instanceof ApiError && error.status === 404)
      return { kind: "NOT_FOUND" as const }
    return { kind: "UNKNOWN" as const, key }
  }
}
