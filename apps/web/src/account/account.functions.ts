import { createServerFn } from "@tanstack/react-start"
import { setResponseHeader } from "@tanstack/react-start/server"
import { z } from "zod"
import {
  ApiError,
  privateApi,
  readFundingByKey,
  readTopupDraft,
  readWorkspace,
} from "./account.server"
import { confirmInput, fundingSchema, idInput, keyInput } from "./schemas"

function noStore() {
  setResponseHeader("Cache-Control", "private, no-store")
  setResponseHeader("Vary", "Cookie")
}

function safeError(error: unknown) {
  return error instanceof ApiError ? error.code : "SERVICE_UNAVAILABLE"
}

export const getWorkspace = createServerFn({ method: "GET" }).handler(
  async () => {
    noStore()
    return readWorkspace()
  }
)

export const getTopupDraft = createServerFn({ method: "POST" })
  .validator((input: unknown) =>
    z.object({ amount: z.string().min(1).max(32) }).parse(input)
  )
  .handler(async ({ data }) => {
    noStore()
    return readTopupDraft(data.amount)
  })

async function confirm(path: string, data: z.infer<typeof confirmInput>) {
  try {
    const funding = fundingSchema.parse(await privateApi(path, "POST", data))
    return { kind: "RESULT" as const, funding }
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.status >= 400 &&
      error.status < 500 &&
      ![408, 425, 429].includes(error.status)
    )
      return { kind: "REJECTED" as const, code: error.code }
    return { kind: "UNKNOWN" as const, key: data.idempotency_key }
  }
}

export const confirmTopup = createServerFn({ method: "POST" })
  .validator((input: unknown) => confirmInput.parse(input))
  .handler(async ({ data }) => {
    noStore()
    return confirm("/v1/account/topups", data)
  })

export const resolveFundingKey = createServerFn({ method: "GET" })
  .validator((input: unknown) => keyInput.parse(input))
  .handler(async ({ data }) => {
    noStore()
    try {
      return {
        kind: "RESULT" as const,
        funding: await readFundingByKey(data.key),
      }
    } catch (error) {
      if (error instanceof ApiError && error.status === 404)
        return { kind: "NOT_FOUND" as const }
      return { kind: "UNKNOWN" as const, code: safeError(error) }
    }
  })

async function pendingAction(id: string, action: "retry" | "cancel") {
  try {
    return {
      kind: "RESULT" as const,
      funding: fundingSchema.parse(
        await privateApi(`/v1/account/topups/${id}/${action}`, "POST")
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
    return { kind: "UNKNOWN" as const, request_id: id }
  }
}

export const retryPending = createServerFn({ method: "POST" })
  .validator((input: unknown) => idInput.parse(input))
  .handler(async ({ data }) => {
    noStore()
    return pendingAction(data.id, "retry")
  })

export const cancelPending = createServerFn({ method: "POST" })
  .validator((input: unknown) => idInput.parse(input))
  .handler(async ({ data }) => {
    noStore()
    return pendingAction(data.id, "cancel")
  })
