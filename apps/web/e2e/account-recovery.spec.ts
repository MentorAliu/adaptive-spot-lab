import { expect, test } from "@playwright/test"

test("cached account failure blocks funding and recovers after revalidation", async ({
  page,
}) => {
  test.setTimeout(100_000)
  test.skip(
    process.env.PLAYWRIGHT_ACCOUNT_FIXTURE !== "1" ||
      process.env.ASL_TEST_ISOLATED !== "1",
    "Requires an isolated funded browser account"
  )

  const hydrationErrors: string[] = []
  page.on("pageerror", (error) => hydrationErrors.push(error.message))
  await page.goto("/settings")
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()
  // The top-up opens once the page has hydrated and read its recovery record.
  await expect(page.getByRole("button", { name: "Review top-up" }))
    .toBeEnabled({ timeout: 5_000 })
    .catch(() => {
      throw new Error(
        `Top-up form hydration failed: ${hydrationErrors.slice(0, 2).join("; ")}`
      )
    })

  let intercepted = 0
  await page.route("**/*", async (route) => {
    if (
      route.request().method() === "GET" &&
      ["fetch", "xhr"].includes(route.request().resourceType())
    ) {
      intercepted++
      await route.abort("failed")
    } else await route.continue()
  })
  // As a real tab switch does, the event bubbles to the window, where the query client listens for it.
  await page.evaluate(() =>
    document.dispatchEvent(new Event("visibilitychange", { bubbles: true }))
  )
  await expect.poll(() => intercepted, { timeout: 40_000 }).toBeGreaterThan(0)
  // Settings' other sections poll, so a request is caught at once. The account itself is read again
  // within 30 seconds (on a tab switch once it is stale), and three retries follow before the read counts
  // as failed (ExecPlan 0035).
  await expect(page.getByText("Account refresh failed")).toBeVisible({
    timeout: 45_000,
  })
  expect(intercepted).toBeGreaterThan(0)
  await expect(
    page.getByRole("button", { name: "Review top-up" })
  ).toBeDisabled()

  await page.unrouteAll({ behavior: "wait" })
  await page.getByRole("button", { name: "Retry account check" }).click()
  await expect(page.getByText("Account refresh failed")).toBeHidden({
    timeout: 10_000,
  })
  await expect(
    page.getByRole("button", { name: "Review top-up" })
  ).toBeEnabled()
})
