import { expect, test } from "@playwright/test"

test("server renders the shell with its menu of four", async ({
  page,
  request,
}) => {
  const response = await request.get("/")
  expect(response.ok()).toBeTruthy()
  const html = await response.text()
  expect(html).toContain("Adaptive Spot Lab")
  expect(html).not.toContain(">PAPER<")
  expect(html).not.toContain("$100")

  await page.goto("/")
  await expect(
    page.getByRole("heading", { name: "Cockpit", level: 1 })
  ).toBeVisible()
  // The owner had every notice removed, the bar's PAPER badge too (DECISIONS 2026-10-30).
  await expect(page.getByText("No funds move", { exact: false })).toHaveCount(0)
  await expect(page.getByText("No real exchange access")).toHaveCount(0)
  const menu = page.getByRole("navigation", { name: "Primary" })
  // ExecPlan 0060: the spot app's four sections.
  await expect(menu.getByRole("link")).toHaveText([
    "Cockpit",
    "Trades",
    "Backtest",
    "Settings",
  ])
  await expect(menu.getByRole("link", { name: "Cockpit" })).toHaveAttribute(
    "aria-current",
    "page"
  )
  await menu.getByRole("link", { name: "Settings" }).click()
  await expect(page).toHaveURL(/\/settings$/)
  await expect(
    page.getByRole("heading", { name: "Settings", level: 1 })
  ).toBeVisible()
  await expect(menu.getByRole("link", { name: "Settings" })).toHaveAttribute(
    "aria-current",
    "page"
  )
})

test("small viewport shows the page without the PAPER badge or sideways scroll", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto("/")
  await expect(
    page.getByRole("heading", { name: "Cockpit", level: 1 })
  ).toBeVisible()
  await expect(page.getByText("PAPER", { exact: true })).toHaveCount(0)
  const width = await page.evaluate(() => document.documentElement.scrollWidth)
  expect(width).toBeLessThanOrEqual(390)
})
