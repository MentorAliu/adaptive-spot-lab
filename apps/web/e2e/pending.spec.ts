import { expect, test } from "@playwright/test"

test("invalid valuation keeps a top-up pending until owner cancellation", async ({
  page,
}) => {
  test.skip(
    process.env.PLAYWRIGHT_PENDING_FIXTURE !== "1" ||
      process.env.ASL_TEST_ISOLATED !== "1",
    "Requires an isolated database with synthetic invalid valuation"
  )

  await page.goto("/settings")
  await expect(page.getByText("Valuation unavailable")).toBeVisible()
  await expect(page.getByRole("heading", { name: "Top-up" })).toBeVisible()

  await page.getByLabel("Amount in USDT").fill("55")
  await page.getByRole("button", { name: "Review top-up" }).click()
  const dialog = page.getByRole("alertdialog")
  await expect(
    dialog.getByText("It will stay pending", { exact: false })
  ).toBeVisible()
  await dialog.getByRole("button", { name: "Confirm funding" }).click()
  await expect(dialog).toBeHidden()
  await expect(
    page.getByText("Funding is pending a valid valuation", { exact: false })
  ).toBeVisible()
  await expect(
    page.getByText("12,277.00 USDT", { exact: false }).first()
  ).toBeVisible()

  let interrupted = false
  await page.route("**/*", async (route) => {
    if (
      !interrupted &&
      route.request().method() === "POST" &&
      route.request().url().includes("_server")
    ) {
      interrupted = true
      const committed = await route.fetch()
      expect(committed.status()).toBe(200)
      await route.abort("failed")
    } else await route.continue()
  })
  await page.getByRole("button", { name: "Cancel" }).click()
  await expect(
    page.getByText("Outcome unavailable", { exact: false })
  ).toBeVisible()
  expect(interrupted).toBe(true)
  await page.unrouteAll()
  await page.reload()
  await expect(page.getByText("CANCELED", { exact: true })).toBeVisible()
  await expect(
    page.getByText("12,277.00 USDT", { exact: false }).first()
  ).toBeVisible()
})
