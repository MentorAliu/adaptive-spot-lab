import { expect, test } from "@playwright/test"

test("an interrupted dispatch retains the exact intent for lookup and same-key replay", async ({
  page,
}) => {
  test.skip(
    process.env.PLAYWRIGHT_UNKNOWN_FIXTURE !== "1" ||
      process.env.ASL_TEST_ISOLATED !== "1",
    "Requires an isolated funded browser account"
  )

  await page.goto("/settings")
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()
  await page.getByLabel("Amount in USDT").fill("44")
  await page.getByRole("button", { name: "Review top-up" }).click()

  let savedAmountAtDispatch = ""
  let savedKeyAtDispatch = ""
  let intercepted = false
  await page.route("**/*", async (route) => {
    if (
      !intercepted &&
      route.request().method() === "POST" &&
      route.request().url().includes("_server")
    ) {
      intercepted = true
      const savedAtDispatch = await page.evaluate(
        () =>
          new Promise<{ amount: string; key: string } | null>(
            (resolve, reject) => {
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
            }
          )
      )
      savedAmountAtDispatch = savedAtDispatch?.amount ?? ""
      savedKeyAtDispatch = savedAtDispatch?.key ?? ""
      await route.abort("failed")
    } else await route.continue()
  })
  await page
    .getByRole("alertdialog")
    .getByRole("button", { name: "Confirm funding" })
    .click()
  await expect(
    page.getByText("The outcome is unknown", { exact: false })
  ).toBeVisible()
  expect(intercepted).toBe(true)
  expect(savedAmountAtDispatch).toBe("44.00000000")
  expect(savedKeyAtDispatch).toMatch(/^[a-f0-9-]{36}$/)
  await page.unrouteAll()

  await page.reload()
  await expect(page.getByText("Check uncertain request")).toBeVisible()
  await expect(
    page.getByRole("button", { name: "Review top-up" })
  ).toBeDisabled()
  await page.getByRole("button", { name: "Check authoritative result" }).click()
  await expect(
    page.getByText("No request is recorded yet", { exact: false })
  ).toBeVisible()
  await page
    .getByRole("button", { name: "Retry the same saved request" })
    .click()
  await expect(page.getByText("Funding posted.")).toBeVisible()
  await expect(
    page.getByText("12,277.00 USDT", { exact: false }).first()
  ).toBeVisible()
})
