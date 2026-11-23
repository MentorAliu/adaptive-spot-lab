import "@tanstack/react-start/server-only"
import { readFile } from "node:fs/promises"
import { getRequest } from "@tanstack/react-start/server"
import { draftSchema, fundingSchema, workspaceSchema } from "./schemas"
import type { Workspace } from "./schemas"

const workflowTimeoutMs = 5_000
const maxSuccessBytes = 8 * 1024 * 1024
const maxErrorBytes = 8 * 1024

export function workflowDeadline(): number {
  return performance.now() + workflowTimeoutMs
}

export class ApiError extends Error {
  constructor(
    public code: string,
    public status: number
  ) {
    super(code)
  }
}

async function boundedJson(
  response: Response,
  maximum: number,
  checkDeadline: () => void
): Promise<unknown> {
  const declared = Number(response.headers.get("content-length"))
  if (Number.isFinite(declared) && declared > maximum)
    throw new Error("Private engine response exceeded its size limit")
  if (!response.body) throw new Error("Private engine returned no body")
  const reader = response.body.getReader()
  const chunks: Uint8Array[] = []
  let length = 0
  try {
    for (;;) {
      checkDeadline()
      const { done, value } = await reader.read()
      checkDeadline()
      if (done) break
      length += value.byteLength
      if (length > maximum)
        throw new Error("Private engine response exceeded its size limit")
      chunks.push(value)
    }
  } catch (error) {
    void reader.cancel().catch(() => {})
    throw error
  } finally {
    reader.releaseLock()
  }
  const bytes = new Uint8Array(length)
  let offset = 0
  for (const chunk of chunks) {
    bytes.set(chunk, offset)
    offset += chunk.byteLength
  }
  return JSON.parse(new TextDecoder().decode(bytes)) as unknown
}

async function serviceKey(): Promise<string> {
  try {
    const value = (
      await readFile(
        process.env.ASL_INTERNAL_KEY_FILE ?? "/run/secrets/api_internal_key",
        "utf8"
      )
    ).trim()
    if (value) return value
  } catch {
    // Deliberately hide the secret path.
  }
  throw new Error("Private service identity unavailable")
}

// The service key is the API's only identity (ExecPlan 0042): the owner uses the app alone on the PC, with no
// sign-in. Only this server holds the key, and the web is published on 127.0.0.1 only.
export async function privateApi(
  path: string,
  method = "GET",
  data?: unknown,
  signal?: AbortSignal,
  deadlineAt = workflowDeadline()
): Promise<unknown> {
  const baseUrl = process.env.ASL_API_BASE_URL
  if (!baseUrl) throw new Error("Private engine unavailable")
  const remainingMs = Math.max(1, Math.ceil(deadlineAt - performance.now()))
  const requestSignal = AbortSignal.any([
    getRequest().signal,
    AbortSignal.timeout(remainingMs),
    ...(signal ? [signal] : []),
  ])
  const checkDeadline = () => {
    if (requestSignal.aborted || performance.now() >= deadlineAt) {
      throw new Error("Private engine unavailable")
    }
  }
  let response: Response
  try {
    const key = await serviceKey()
    checkDeadline()
    response = await fetch(new URL(path, baseUrl), {
      method,
      headers: {
        "X-Internal-Key": key,
        ...(data === undefined ? {} : { "Content-Type": "application/json" }),
        ...(method === "GET" ? {} : { "X-Request-ID": crypto.randomUUID() }),
      },
      body: data === undefined ? undefined : JSON.stringify(data),
      cache: "no-store",
      signal: requestSignal,
    })
  } catch {
    throw new Error("Private engine unavailable")
  }
  checkDeadline()
  if (!response.ok) {
    let code = "REQUEST_FAILED"
    try {
      const payload = await boundedJson(response, maxErrorBytes, checkDeadline)
      if (
        payload &&
        typeof payload === "object" &&
        "code" in payload &&
        typeof payload.code === "string" &&
        /^[A-Z_]+$/.test(payload.code)
      )
        code = payload.code
    } catch {
      // Do not expose arbitrary private error bodies.
    }
    checkDeadline()
    throw new ApiError(code, response.status)
  }
  const payload = await boundedJson(response, maxSuccessBytes, checkDeadline)
  checkDeadline()
  return payload
}

/**
 * A private engine stream (ExecPlan 0047): the engine's answer as it arrives, for a route that passes
 * its body on. Only its start is bounded, by the usual 5 s; the body then lasts until either side
 * leaves, and `signal` (the browser's request) ends it.
 */
export async function privateStream(
  path: string,
  headers: Record<string, string>,
  signal: AbortSignal
): Promise<Response> {
  const baseUrl = process.env.ASL_API_BASE_URL
  if (!baseUrl) throw new Error("Private engine unavailable")
  const started = new AbortController()
  const timer = setTimeout(() => started.abort(), workflowTimeoutMs)
  try {
    const key = await serviceKey()
    return await fetch(new URL(path, baseUrl), {
      headers: { ...headers, "X-Internal-Key": key },
      cache: "no-store",
      signal: AbortSignal.any([signal, started.signal]),
    })
  } catch {
    throw new Error("Private engine unavailable")
  } finally {
    clearTimeout(timer)
  }
}

export async function readWorkspace(): Promise<Workspace> {
  return workspaceSchema.parse(await privateApi("/v1/account/workspace"))
}

export async function readTopupDraft(amount: string) {
  return draftSchema.parse(
    await privateApi("/v1/account/topups/draft", "POST", { amount })
  )
}

export async function readFundingByKey(key: string) {
  return fundingSchema.parse(
    await privateApi(`/v1/account/requests/${encodeURIComponent(key)}`)
  )
}
