// @vitest-environment node
import { describe, expect, it } from "vitest"
import { FRAME_ANCESTORS, FRAME_OPTIONS, framed } from "./frame-policy"

describe("the frame policy (ExecPlan 0026 section 5.12)", () => {
  it("forbids framing on a page, an error and an empty answer", () => {
    for (const response of [
      new Response("<html></html>", {
        headers: { "Content-Type": "text/html" },
      }),
      new Response("Request is too large", { status: 413 }),
      new Response(null, { status: 204 }),
    ]) {
      const sent = framed(response)
      expect(sent.headers.get("Content-Security-Policy")).toBe(FRAME_ANCESTORS)
      expect(sent.headers.get("X-Frame-Options")).toBe(FRAME_OPTIONS)
      expect(sent.status).toBe(response.status)
    }
    expect(FRAME_ANCESTORS).toBe("frame-ancestors 'none'")
    expect(FRAME_OPTIONS).toBe("DENY")
  })

  it("copies a response whose headers cannot change, keeping its status and headers", async () => {
    const redirect = Response.redirect("http://127.0.0.1:4318/", 307)
    expect(() => redirect.headers.set("X-Test", "1")).toThrow()
    const sent = framed(redirect)
    expect(sent).not.toBe(redirect)
    expect(sent.status).toBe(307)
    expect(sent.headers.get("Location")).toBe("http://127.0.0.1:4318/")
    expect(sent.headers.get("X-Frame-Options")).toBe("DENY")
    expect(sent.headers.get("Content-Security-Policy")).toBe(FRAME_ANCESTORS)
    const body = framed(new Response("kept body", { status: 418 }))
    await expect(body.text()).resolves.toBe("kept body")
  })

  it("keeps a policy the response already has and adds its own beside it", () => {
    const sent = framed(
      new Response("x", {
        headers: {
          "Content-Security-Policy": "default-src 'self'",
          "Cache-Control": "private, no-store",
        },
      })
    )
    // Two policies, each enforced: the existing one is not weakened or replaced.
    expect(sent.headers.get("Content-Security-Policy")).toBe(
      `default-src 'self', ${FRAME_ANCESTORS}`
    )
    expect(sent.headers.get("Cache-Control")).toBe("private, no-store")
  })
})
