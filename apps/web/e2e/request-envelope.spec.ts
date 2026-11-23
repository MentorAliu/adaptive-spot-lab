import { request as httpRequest } from "node:http"
import { expect, test } from "@playwright/test"

function postChunked(url: string, body: string, finish: boolean) {
  return new Promise<number>((resolve, reject) => {
    const request = httpRequest(
      url,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Origin: new URL(url).origin,
          "Sec-Fetch-Site": "same-origin",
          "Transfer-Encoding": "chunked",
        },
      },
      (response) => {
        response.resume()
        response.on("end", () => {
          request.destroy()
          resolve(response.statusCode ?? 0)
        })
      }
    )
    request.on("error", reject)
    request.setTimeout(9_000, () =>
      request.destroy(new Error("Probe timed out"))
    )
    request.flushHeaders()
    if (finish) request.end(body)
    else request.write(body)
  })
}

test("server functions bound declared, chunked and stalled request bodies", async ({
  page,
  context,
}) => {
  test.skip(
    process.env.PLAYWRIGHT_ACCOUNT_FIXTURE !== "1" ||
      !process.env.ASL_DB_NAME?.startsWith("asl_m1_browser_"),
    "Requires an isolated account fixture"
  )
  // A POST server function's address, from the top-up's review (the owner has no sign-in since
  // ExecPlan 0042, so the review is the first POST a page sends).
  await page.goto("/settings")
  const rpc = page.waitForRequest(
    (request) =>
      request.method() === "POST" && request.url().includes("/_serverFn/")
  )
  await page.getByLabel("Amount in USDT").fill("1")
  await expect(
    page.getByRole("button", { name: "Review top-up" })
  ).toBeEnabled()
  await page.getByRole("button", { name: "Review top-up" }).click()
  const url = (await rpc).url()
  const origin = new URL(url).origin
  const declared = await context.request.post(url, {
    data: JSON.stringify({ data: { junk: "x".repeat(9 * 1024 * 1024) } }),
    headers: {
      "Content-Type": "application/json",
      Origin: origin,
      "Sec-Fetch-Site": "same-origin",
    },
  })
  expect(declared.status()).toBe(413)

  const chunked = await postChunked(
    url,
    JSON.stringify({ data: { junk: "x".repeat(9_000) } }),
    true
  )
  expect(chunked).toBe(413)

  const started = performance.now()
  const stalled = await postChunked(url, '{"data":', false)
  expect(stalled).toBe(408)
  expect(performance.now() - started).toBeLessThan(8_000)
})
