// @vitest-environment node
import { readFile } from "node:fs/promises"
import { getRequest } from "@tanstack/react-start/server"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { ApiError, privateApi } from "./account.server"

vi.mock("@tanstack/react-start/server-only", () => ({}))
vi.mock("node:fs/promises", () => ({ readFile: vi.fn() }))
vi.mock("@tanstack/react-start/server", () => ({
  getRequest: vi.fn(),
}))

describe("private API request deadline", () => {
  let elapsed = 0
  beforeEach(() => {
    elapsed = 0
    vi.stubEnv("ASL_API_BASE_URL", "http://api:8000")
    vi.spyOn(performance, "now").mockImplementation(() => elapsed)
    vi.mocked(readFile).mockResolvedValue("synthetic-service-key")
    vi.mocked(getRequest).mockReturnValue(
      new Request("http://localhost/markets")
    )
  })
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
    vi.unstubAllEnvs()
  })

  it("accepts an on-time response and preserves safe API errors", async () => {
    const fetcher = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ symbol: "BTCUSDT" }))
      .mockResolvedValueOnce(
        Response.json({ code: "INVALID_FUNDING_KIND" }, { status: 400 })
      )
    vi.stubGlobal("fetch", fetcher)
    await expect(privateApi("/v1/markets/quote")).resolves.toEqual({
      symbol: "BTCUSDT",
    })
    await expect(privateApi("/v1/markets/quote")).rejects.toEqual(
      new ApiError("INVALID_FUNDING_KIND", 400)
    )
    expect(fetcher.mock.calls[0][1].signal).toBeInstanceOf(AbortSignal)
  })

  it("sends the service key as the only identity: no owner session (ExecPlan 0042)", async () => {
    const fetcher = vi.fn<typeof fetch>(async () => Response.json({ ok: true }))
    vi.stubGlobal("fetch", fetcher)
    await privateApi("/v1/account/workspace")
    await privateApi("/v1/account/topups/draft", "POST", { amount: "25" })
    const [read, write] = fetcher.mock.calls.map(
      ([, init]) => init?.headers as Record<string, string>
    )
    expect(read).toEqual({ "X-Internal-Key": "synthetic-service-key" })
    expect(Object.keys(write).sort()).toEqual([
      "Content-Type",
      "X-Internal-Key",
      "X-Request-ID",
    ])
  })

  it.each(["headers", "success body", "error body"])(
    "rejects an uncancellable late %s response",
    async (stage) => {
      vi.stubGlobal(
        "fetch",
        vi.fn(async () => {
          if (stage === "headers") elapsed = 5_001
          if (stage === "headers") return Response.json({ symbol: "BTCUSDT" })
          return new Response(
            new ReadableStream<Uint8Array>(
              {
                pull(controller) {
                  elapsed = 5_001
                  controller.enqueue(
                    new TextEncoder().encode('{"symbol":"BTCUSDT"}')
                  )
                  controller.close()
                },
              },
              { highWaterMark: 0 }
            ),
            { status: stage === "error body" ? 503 : 200 }
          )
        })
      )
      await expect(privateApi("/v1/markets/quote")).rejects.toThrow(
        "Private engine unavailable"
      )
    }
  )

  it("rejects oversized private responses even if the upstream omits a length header", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(
            new ReadableStream<Uint8Array>({
              start(controller) {
                controller.enqueue(new Uint8Array(8 * 1024 * 1024 + 1))
                controller.close()
              },
            })
          )
      )
    )
    await expect(privateApi("/v1/markets/quote")).rejects.toThrow(
      "Private engine response exceeded its size limit"
    )
  })

  it.each(["incoming", "forwarded"])(
    "rejects a response that ignores the %s cancellation signal",
    async (source) => {
      const controller = new AbortController()
      if (source === "incoming") {
        vi.mocked(getRequest).mockReturnValue(
          new Request("http://localhost/markets", { signal: controller.signal })
        )
      }
      vi.stubGlobal(
        "fetch",
        vi.fn(async () => {
          controller.abort()
          return Response.json({ symbol: "BTCUSDT" })
        })
      )
      await expect(
        privateApi(
          "/v1/markets/quote",
          "GET",
          undefined,
          source === "forwarded" ? controller.signal : undefined
        )
      ).rejects.toThrow("Private engine unavailable")
    }
  )
})
