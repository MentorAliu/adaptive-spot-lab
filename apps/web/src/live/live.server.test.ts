// @vitest-environment node
import { readFile } from "node:fs/promises"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { liveStream } from "./live.server"

vi.mock("@tanstack/react-start/server-only", () => ({}))
vi.mock("node:fs/promises", () => ({ readFile: vi.fn() }))
vi.mock("@tanstack/react-start/server", () => ({ getRequest: vi.fn() }))

// ExecPlan 0047 section 4.3 (the spot stream since ExecPlan 0060): the web server passes the engine's live
// stream on, on SYNTHETIC engine answers. Only this server holds the service key; the browser names
// nothing but its last event's id.
const READY =
  'event: ready\nid: 41\nretry: 3000\ndata: {"state":"READY","cursor":"41"}\n\n'

function events(text: string) {
  return new Response(
    new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(new TextEncoder().encode(text))
        controller.close()
      },
    }),
    { headers: { "Content-Type": "text/event-stream; charset=utf-8" } }
  )
}

function browser(headers: Record<string, string> = {}, signal?: AbortSignal) {
  return new Request("http://localhost:3000/api/live", { headers, signal })
}

describe("the live trades' stream route", () => {
  beforeEach(() => {
    vi.stubEnv("ASL_API_BASE_URL", "http://api:8000")
    vi.mocked(readFile).mockResolvedValue("synthetic-service-key")
  })
  afterEach(() => {
    vi.useRealTimers()
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("passes the engine's events on, asked with the service key and the browser's last event id", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => events(READY))
    vi.stubGlobal("fetch", fetcher)
    const tab = new AbortController()
    const response = await liveStream(
      browser({ "Last-Event-ID": "40", Cookie: "theme=dark" }, tab.signal)
    )
    expect(response.status).toBe(200)
    expect(Object.fromEntries(response.headers)).toEqual({
      "cache-control": "no-store",
      "content-type": "text/event-stream; charset=utf-8",
      "x-accel-buffering": "no",
    })
    expect(await response.text()).toBe(READY)
    const [url, init] = fetcher.mock.calls[0]
    expect(String(url)).toBe("http://api:8000/v1/spot/live")
    expect(init?.headers).toEqual({
      Accept: "text/event-stream",
      "Last-Event-ID": "40",
      "X-Internal-Key": "synthetic-service-key",
    })
    expect(init?.cache).toBe("no-store")
    // The tab leaving ends the engine's request.
    expect(init?.signal?.aborted).toBe(false)
    tab.abort()
    expect(init?.signal?.aborted).toBe(true)
  })

  it("bounds only the stream's start: an open stream outlives the usual 5 s", async () => {
    vi.useFakeTimers()
    const fetcher = vi.fn<typeof fetch>(async () => events(READY))
    vi.stubGlobal("fetch", fetcher)
    const response = await liveStream(browser())
    expect(response.status).toBe(200)
    await vi.advanceTimersByTimeAsync(60_000)
    expect(fetcher.mock.calls[0][1]?.signal?.aborted).toBe(false)
    expect(fetcher.mock.calls[0][1]?.headers).toEqual({
      Accept: "text/event-stream",
      "X-Internal-Key": "synthetic-service-key",
    })
  })

  it("gives up on an engine that has not answered within 5 s", async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>(
        (_url, init) =>
          new Promise((_resolve, reject) =>
            init?.signal?.addEventListener("abort", () =>
              reject(init.signal?.reason)
            )
          )
      )
    )
    const pending = liveStream(browser())
    await vi.advanceTimersByTimeAsync(5_000)
    const response = await pending
    expect(response.status).toBe(503)
    expect(await response.text()).toBe("Live trades unavailable")
  })

  it("refuses an event id that is not one, without asking the engine", async () => {
    const fetcher = vi.fn<typeof fetch>()
    vi.stubGlobal("fetch", fetcher)
    for (const id of ["-1", "01", "4x", "1".repeat(20)]) {
      const response = await liveStream(browser({ "Last-Event-ID": id }))
      expect(response.status).toBe(400)
    }
    expect(fetcher).not.toHaveBeenCalled()
  })

  it.each([
    [
      "the engine's refusal",
      () =>
        Response.json(
          { code: "LIVE_UNAVAILABLE", retryable: true },
          { status: 503 }
        ),
    ],
    ["an answer that is not an event stream", () => Response.json({})],
    [
      "a failed request",
      () => {
        throw new TypeError("fetch failed: connect ECONNREFUSED api:8000")
      },
    ],
  ])("answers 503 with nothing of %s", async (_, answer) => {
    vi.stubGlobal(
      "fetch",
      vi.fn<typeof fetch>(async () => answer())
    )
    const response = await liveStream(browser())
    expect(response.status).toBe(503)
    expect(response.headers.get("cache-control")).toBe("no-store")
    expect(await response.text()).toBe("Live trades unavailable")
  })

  it("answers 503 without the service key or the engine's address", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => events(READY))
    vi.stubGlobal("fetch", fetcher)
    vi.mocked(readFile).mockRejectedValueOnce(new Error("ENOENT"))
    expect((await liveStream(browser())).status).toBe(503)
    vi.stubEnv("ASL_API_BASE_URL", "")
    expect((await liveStream(browser())).status).toBe(503)
    expect(fetcher).not.toHaveBeenCalled()
  })
})
