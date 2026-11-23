import { expect, test } from "@playwright/test"
import type { Locator, Page } from "@playwright/test"

// The spot app's four pages (ExecPlan 0060 section 4.9), on the database tests/spot_browser_fixture.py
// seeds: a daily Bitcoin history since 2017 and a month of minutes, all a SYNTHETIC walk in Binance's
// format, the 10,000 USDT the app adds by itself, run #1 bought on today's reading, the owner's Stop and sell sold it, run #2 (the
// owner's Start) bought again, and the backtest worked out. The fixture's feed writes the SYNTHETIC
// order book while the suite runs, and the real engine worker, API and web server run on it. The Pause
// test changes the run and puts it back, through the engine.
const state = process.env.ASL_SPOT_BROWSER ?? ""
const isolated =
  process.env.ASL_TEST_ISOLATED === "1" &&
  /^asl_m1_[a-z0-9_]+_browser$/.test(process.env.ASL_DB_NAME ?? "")

/** Page errors and console errors, such as a hydration mismatch React reports. */
function watchErrors(page: Page): string[] {
  const errors: string[] = []
  page.on("pageerror", (error) => errors.push(error.message))
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text())
  })
  return errors
}

function card(page: Page, heading: string | RegExp): Locator {
  return page
    .locator("main [data-slot='card']")
    .filter({
      has: page.locator("[data-slot='card-title']", { hasText: heading }),
    })
    .first()
}

async function noSidewaysScroll(page: Page) {
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth)
  ).toBeLessThanOrEqual(await page.evaluate(() => window.innerWidth))
}

test.describe("The spot pages (ExecPlan 0060)", () => {
  test.describe.configure({ mode: "serial" })
  test.skip(
    state !== "pages" || !isolated,
    "Explicit spot pages phase on a disposable browser database, seeded by tests.spot_browser_fixture"
  )
  test.beforeEach(async ({ page }) => {
    test.setTimeout(90_000)
    await page.setViewportSize({ width: 1440, height: 1000 })
  })

  test("the Cockpit shows the value, the rule's reading, the latest trades and Bitcoin's chart @spot", async ({
    page,
  }) => {
    const errors = watchErrors(page)
    await page.goto("/")
    await expect(
      page.getByRole("heading", { name: "Cockpit", level: 1 })
    ).toBeVisible()
    await expect(page.getByText("Trading · all good")).toBeVisible()
    const value = card(page, "Account value")
    await expect(value).toContainText(/\d{1,2},\d{3}\.\d{2}USDT/)
    // The fixture's book follows its walk through the day, so how much BTC run #2 bought depends on the
    // hour it was seeded (0.00835 BTC at 13:30 UTC, 0.0084 at 14:40 on 2026-11-12): the reading's words
    // must name the BTC the account holds, which run #2's one buy is.
    await expect(value).toContainText(/0\.\d+ BTC/)
    const held = (await value.textContent())?.match(/(0\.\d+) BTC/)?.[1]
    expect(held).toBeTruthy()
    const reading = card(page, "The rule's reading")
    await expect(reading).toContainText(
      new RegExp(
        `Trend up [123] of 3: hold \\d+\\.\\d% in Bitcoin; bought ${held?.replace(".", "\\.")} BTC`
      )
    )
    await expect(reading).toContainText(
      /Done for today\. Next reading at 00:05\./
    )
    const trades = page.getByRole("list", { name: "The newest 6 trades" })
    await expect(trades.getByRole("listitem")).toHaveCount(3)
    await expect(trades.getByRole("listitem").nth(1)).toContainText(
      "Sold everything when the run stopped, by you"
    )
    // Both charts drew: the value since the start, and the daily candles with the buys and sells.
    await expect(
      page.getByRole("img", { name: "Bitcoin spot 1d candlestick chart" })
    ).toBeVisible()
    await expect(
      card(page, "Bitcoin").getByText("Loading the Bitcoin chart…")
    ).toHaveCount(0)
    await expect(
      page.locator("main [role='img'][aria-label^='Bitcoin spot'] canvas")
    ).not.toHaveCount(0)
    await expect(page.getByText("Marked: 2 buys and 1 sell.")).toBeAttached()
    // A shorter candle reads its own interval, and the choice is kept.
    await card(page, "Bitcoin").getByRole("button", { name: "1h" }).click()
    await expect(
      page.getByRole("img", { name: "Bitcoin spot 1h candlestick chart" })
    ).toBeVisible()
    await page.reload()
    await expect(
      page.getByRole("img", { name: "Bitcoin spot 1h candlestick chart" })
    ).toBeVisible()
    expect(errors).toEqual([])
  })

  test("Trades lists the buys and sells, and the daily readings on their tab @spot", async ({
    page,
  }) => {
    const errors = watchErrors(page)
    await page.goto("/trades")
    const trades = page.getByRole("table", {
      name: "The account's buys and sells, newest first",
    })
    await expect(trades.getByRole("row")).toHaveCount(4)
    await expect(trades.getByRole("row").nth(1)).toContainText("Daily rule")
    await expect(trades.getByRole("row").nth(2)).toContainText("Run stopped")
    await page.getByRole("tab", { name: "Daily readings" }).click()
    await expect(page).toHaveURL(/\/trades\?tab=readings$/)
    const readings = page.getByRole("table", {
      name: "The rule's daily readings, newest first",
    })
    await expect(readings.getByRole("row")).toHaveCount(3)
    await expect(readings.getByRole("row").nth(1)).toContainText(
      /Trend up [123] of 3.*Traded.*Bought 0\.\d+ BTC/
    )
    // An address the page refuses is dropped, not passed on.
    await page.goto("/trades?tab=everything")
    await expect(page.getByRole("tab", { name: "Trades" })).toHaveAttribute(
      "aria-selected",
      "true"
    )
    expect(errors).toEqual([])
  })

  test("Backtest shows the rule beside holding Bitcoin over each window, from the server's first answer @spot", async ({
    page,
    request,
  }) => {
    const errors = watchErrors(page)
    // The server writes the stored result in the page itself.
    const html = await (await request.get("/backtest")).text()
    expect(html).toContain("Holding Bitcoin")
    expect(html).toContain("Each year")
    await page.goto("/backtest")
    await expect(page.getByRole("tab", { name: "Since 2019" })).toHaveAttribute(
      "aria-selected",
      "true"
    )
    await expect(
      page.getByText(/^From 10,000\.00 USDT on 1 Jan 2019 to /)
    ).toBeVisible()
    await expect(card(page, "The rule")).toContainText(/\d+ buys, \d+ sells/)
    await expect(card(page, "Holding Bitcoin")).toContainText("Worst fall")
    await expect(
      page.locator("main [role='img'][aria-label^=\"The rule's value\"] canvas")
    ).not.toHaveCount(0)
    await page.getByRole("tab", { name: "Last 12 months" }).click()
    await expect(page).toHaveURL(/\/backtest\?window=LAST_12_MONTHS$/)
    await expect(page.getByText(/\(365 days\)/)).toBeVisible()
    const years = page.getByRole("table", {
      name: "The return of each year, the rule beside holding Bitcoin",
    })
    await expect(years.getByRole("row")).toHaveCount(3)
    await expect(
      page.getByText(/^Binance's daily Bitcoin candles from 17 Aug 2017 to /)
    ).toBeVisible()
    // A window the page does not know is dropped: the first window shows.
    await page.goto("/backtest?window=EVERYTHING")
    await expect(page.getByRole("tab", { name: "Since 2019" })).toHaveAttribute(
      "aria-selected",
      "true"
    )
    await expect(
      page.getByText(/^From 10,000\.00 USDT on 1 Jan 2019 to /)
    ).toBeVisible()
    expect(errors).toEqual([])
  })

  test("Settings pauses the run and resumes it through the engine, and says the rule in words @spot", async ({
    page,
  }) => {
    const errors = watchErrors(page)
    await page.goto("/settings")
    await expect(
      page
        .getByRole("navigation", { name: "Settings sections" })
        .getByRole("link")
    ).toHaveText(["Trading run", "Rule and limits", "Account", "Health"])
    const run = page.locator("section#run")
    await expect(run.getByRole("heading", { name: "Run #2" })).toBeVisible()
    await expect(run).toContainText("Trading")
    await run.getByRole("button", { name: "Pause" }).click()
    const dialog = page.getByRole("alertdialog")
    await expect(dialog).toContainText("Pause: run #2?")
    await dialog.getByRole("button", { name: "Pause" }).click()
    await expect(run).toContainText("Pause accepted.")
    // The engine applies it within a second; the page shows the run's new state by itself.
    await expect(run).toContainText("Held by your Pause", { timeout: 10_000 })
    await expect(run.getByRole("button")).toHaveText([
      "Resume",
      "Stop and sell",
    ])
    await run.getByRole("button", { name: "Resume" }).click()
    await page
      .getByRole("alertdialog")
      .getByRole("button", { name: "Resume" })
      .click()
    await expect(run.getByRole("button")).toHaveText(
      ["Pause", "Stop and sell"],
      {
        timeout: 10_000,
      }
    )
    const rule = page.locator("section#rule")
    await expect(rule).toContainText(
      "It compares that close with the closes 30, 91 and 365 days before."
    )
    await expect(rule).toContainText(
      /SPOT_RULE_V1 [a-f0-9]{12}… · SPOT_POLICY_V1 [a-f0-9]{12}… · SPOT_COST_V1 [a-f0-9]{12}…/
    )
    const health = page.locator("section#health")
    await expect(health).toContainText("App version")
    expect(errors).toEqual([])
  })

  test("the menu has four sections and every page fits a phone @spot", async ({
    page,
  }) => {
    await page.goto("/")
    const menu = page.getByRole("navigation", { name: "Primary" })
    await expect(menu.getByRole("link")).toHaveText([
      "Cockpit",
      "Trades",
      "Backtest",
      "Settings",
    ])
    await menu.getByRole("link", { name: "Backtest" }).click()
    await expect(page).toHaveURL(/\/backtest$/)
    await expect(menu.getByRole("link", { name: "Backtest" })).toHaveAttribute(
      "aria-current",
      "page"
    )
    await page.setViewportSize({ width: 390, height: 844 })
    for (const path of ["/", "/trades", "/backtest", "/settings"]) {
      await page.goto(path)
      await expect(page.getByRole("heading", { level: 1 })).toBeVisible()
      await noSidewaysScroll(page)
    }
  })
})
