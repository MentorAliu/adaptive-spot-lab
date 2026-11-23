import { createServerFn } from "@tanstack/react-start"
import { setResponseHeader } from "@tanstack/react-start/server"
import { z } from "zod"
import {
  postRequest,
  readActivity,
  readBacktest,
  readCandles,
  readDefinitions,
  readMarkers,
  readMarket,
  readOverview,
  readReadings,
  readTrades,
  readValuations,
  requestByKey,
} from "./spot.server"
import {
  backtestWindowSchema,
  idempotencyKey,
  intervalSchema,
  requestInput,
  valuationWindowSchema,
} from "./schemas"

function noStore() {
  setResponseHeader("Cache-Control", "private, no-store")
  setResponseHeader("Vary", "Cookie")
}

const cursor = z
  .string()
  .regex(/^[0-9]{1,20}$/)
  .nullable()

// A list's page size, within the API's own 1 to 100; left out, the API's reads take 25.
const pageLimit = z.number().int().min(1).max(100).optional()

export const getSpotOverview = createServerFn({ method: "GET" }).handler(
  async () => {
    noStore()
    return readOverview()
  }
)

export const getSpotTrades = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ cursor, limit: pageLimit }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readTrades(data.cursor, data.limit)
  })

export const getSpotReadings = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ cursor, limit: pageLimit }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readReadings(data.cursor, data.limit)
  })

export const getSpotActivity = createServerFn({ method: "GET" })
  .validator((value: unknown) => z.strictObject({ after: cursor }).parse(value))
  .handler(async ({ data }) => {
    noStore()
    return readActivity(data.after)
  })

export const getSpotMarkers = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ sinceMs: z.number().int().min(0) }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readMarkers(data.sinceMs)
  })

export const getSpotValuations = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ window: valuationWindowSchema }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readValuations(data.window)
  })

export const getSpotBacktest = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ window: backtestWindowSchema }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readBacktest(data.window)
  })

export const getSpotDefinitions = createServerFn({ method: "GET" }).handler(
  async () => {
    noStore()
    return readDefinitions()
  }
)

export const getMarket = createServerFn({ method: "GET" }).handler(async () => {
  noStore()
  return readMarket()
})

export const getCandles = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z
      .strictObject({
        interval: intervalSchema,
        limit: z.number().int().min(1).max(1000),
      })
      .parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return readCandles(data.interval, data.limit)
  })

// The owner's run requests: a POST server function behind Start's Host and CSRF middleware. The
// engine applies each in its fenced step; the result is "accepted", never "done".
export const postSpotRequest = createServerFn({ method: "POST" })
  .validator((value: unknown) => requestInput.parse(value))
  .handler(async ({ data }) => {
    noStore()
    return postRequest(data)
  })

export const resolveSpotRequest = createServerFn({ method: "GET" })
  .validator((value: unknown) =>
    z.strictObject({ key: idempotencyKey }).parse(value)
  )
  .handler(async ({ data }) => {
    noStore()
    return requestByKey(data.key)
  })
