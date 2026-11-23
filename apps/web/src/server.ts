import handler, { createServerEntry } from "@tanstack/react-start/server-entry"
import { limitRequestBody } from "srvx/body-limit"
import { framed } from "./frame-policy"

const maximumBodyBytes = 8_192
const maximumBodyReadMs = 5_000

function requestTooLarge() {
  return new Response("Request is too large", { status: 413 })
}

type Fetch = typeof handler.fetch

export default createServerEntry({
  // Every response of this entry leaves with the frame policy: pages, server functions, refusals and
  // errors. Nitro answers public/ and the built /assets/ before the entry, without it; none is HTML.
  // An error that escapes Start (this release's entry has no error converter) or the body check
  // becomes a plain 500 here, so that answer carries the policy too; it names nothing private.
  async fetch(request, options) {
    try {
      return framed(await bounded(request, options))
    } catch (error) {
      // A request the client gave up on is not a fault of this server.
      if (!request.signal.aborted) console.error(error)
      return framed(
        new Response("Internal Server Error", {
          status: 500,
          headers: { "Content-Type": "text/plain; charset=utf-8" },
        })
      )
    }
  },
})

async function bounded(
  request: Parameters<Fetch>[0],
  options: Parameters<Fetch>[1]
): Promise<Response> {
  const declared = request.headers.get("content-length")
  if (declared !== null) {
    if (!/^\d+$/.test(declared))
      return new Response("Invalid content length", { status: 400 })
    if (Number(declared) > maximumBodyBytes) {
      void request.body?.cancel().catch(() => {})
      return requestTooLarge()
    }
  }
  if (!request.body) return handler.fetch(request, options)

  // Inspect a bounded clone before Start deserializes server-function input.
  // The original body remains available to the framework after this check.
  const reader = limitRequestBody(
    request.clone(),
    maximumBodyBytes
  ).body!.getReader()
  const timeout = new AbortController()
  const timer = setTimeout(() => {
    timeout.abort()
    void reader.cancel().catch(() => {})
    void request.body?.cancel().catch(() => {})
  }, maximumBodyReadMs)
  try {
    for (;;) {
      const { done } = await reader.read()
      if (timeout.signal.aborted)
        return new Response("Request body timed out", { status: 408 })
      if (done) break
    }
  } catch (error) {
    if (
      error !== null &&
      typeof error === "object" &&
      "code" in error &&
      error.code === "ERR_BODY_TOO_LARGE"
    ) {
      void request.body.cancel().catch(() => {})
      return requestTooLarge()
    }
    throw error
  } finally {
    clearTimeout(timer)
    reader.releaseLock()
  }
  return handler.fetch(request, options)
}
