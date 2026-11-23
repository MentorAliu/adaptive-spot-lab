import { expect, test } from "@playwright/test"

test("lost confirmation response resolves by durable request key", async ({
  page,
}) => {
  test.skip(
    process.env.PLAYWRIGHT_UNKNOWN_FIXTURE !== "1" ||
      process.env.ASL_TEST_ISOLATED !== "1",
    "Requires an isolated funded browser account"
  )

  await page.goto("/settings")
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()
  await page.getByLabel("Amount in USDT").fill("33")
  await page.getByRole("button", { name: "Review top-up" }).click()
  const dialog = page.getByRole("alertdialog")
  await expect(dialog.getByText("33.00 USDT", { exact: false })).toBeVisible()

  let intercepted = false
  await page.route("**/*", async (route) => {
    if (
      !intercepted &&
      route.request().method() === "POST" &&
      route.request().url().includes("_server")
    ) {
      intercepted = true
      const committed = await route.fetch()
      expect(committed.status()).toBe(200)
      await route.abort("failed")
    } else await route.continue()
  })
  await dialog.getByRole("button", { name: "Confirm funding" }).click()
  await expect(
    page.getByText("The outcome is unknown", { exact: false })
  ).toBeVisible()
  expect(intercepted).toBe(true)
  await page.reload()
  await expect(page.getByText("Check uncertain request")).toBeVisible()
  const saved = await page.evaluate(
    () =>
      new Promise<{ amount: string; key: string } | null>((resolve, reject) => {
        const opened = indexedDB.open("asl_funding_intents_v1", 1)
        opened.onerror = () => reject(opened.error)
        opened.onsuccess = () => {
          const request = opened.result
            .transaction("intents", "readonly")
            .objectStore("intents")
            .get("owner:1")
          request.onerror = () => reject(request.error)
          request.onsuccess = () => {
            const intent = request.result as
              | { payload: { amount: string; idempotency_key: string } }
              | undefined
            resolve(
              intent
                ? {
                    amount: intent.payload.amount,
                    key: intent.payload.idempotency_key,
                  }
                : null
            )
            opened.result.close()
          }
        }
      })
  )
  expect(saved?.amount).toBe("33.00000000")
  expect(saved?.key).toMatch(/^[a-f0-9-]{36}$/)
  await page.getByRole("button", { name: "Check authoritative result" }).click()
  await expect(page.getByText("Funding posted.")).toBeVisible()
  await expect(
    page.getByText("12,233.00 USDT", { exact: false }).first()
  ).toBeVisible()
})
