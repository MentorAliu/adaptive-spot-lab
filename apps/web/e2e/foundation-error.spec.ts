import { expect, test } from "@playwright/test"

test("database outage exposes the M1 account error state", async ({ page }) => {
  test.skip(
    process.env.PLAYWRIGHT_EXPECT_ERROR !== "1",
    "Run after stopping the isolated test database"
  )

  await page.goto("/")
  await expect(page.getByText("Account unavailable")).toBeVisible()
  await expect(
    page.getByText("No account state is being shown.", { exact: false })
  ).toBeVisible()
})
