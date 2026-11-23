import { expect, test } from "@playwright/test"
import type { BrowserContext, Locator, Page } from "@playwright/test"

// Live trades and pop-ups (ExecPlan 0047; the spot fills' since ExecPlan 0060), on the database
// tests/spot_browser_fixture.py seeds (run #2 holding the BTC of its one buy), with the fixture's SYNTHETIC feed,
// the real engine worker, the API and the web server running on it. L1: the stream's route refuses what
// is not the page's own; L2: one stream per browser, taken over when its tab closes; L3: the owner's
// Stop and sell shows at once as a toast; L4: the buy of the run the owner starts next is a desktop
// pop-up while no tab has focus. L3 and L4 change the run through the engine, so the suite runs once
// per seeded database, after the pages' suites.
const state = process.env.ASL_SPOT_BROWSER ?? ""
const isolated =
  process.env.ASL_TEST_ISOLATED === "1" &&
  /^asl_m1_[a-z0-9_]+_browser$/.test(process.env.ASL_DB_NAME ?? "")

declare global {
  interface Window {
    popups: {
      title: string
      options: NotificationOptions
      onclick: (() => void) | null
    }[]
  }
}

/** The header's badge: whether this tab's trades are live. */
function badge(page: Page): Locator {
  return page.locator("header [role='status'][data-state]")
}

function toasts(page: Page, title: RegExp): Locator {
  return page.locator("[data-slot='toast']").filter({
    has: page.locator("[data-slot='toast-title']", { hasText: title }),
  })
}

/** The live streams this context's tabs open. */
function streams(context: BrowserContext): string[] {
  const opened: string[] = []
  context.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/live")
      opened.push(request.url())
  })
  return opened
}

/** A page, live, with the toasts' cursor kept: what the feed already holds is not toasted. */
async function livePage(page: Page, path = "/") {
  await page.goto(path)
  // Web Locks and notifications exist only in a secure context, as http://localhost:3000 is on the PC;
  // http://127.0.0.1:4318 is not one, so this suite runs on http://localhost:4318.
  expect(
    await page.evaluate(() => window.isSecureContext),
    "a secure context: PLAYWRIGHT_BASE_URL=http://localhost:4318"
  ).toBe(true)
  await expect(badge(page)).toHaveAttribute("data-state", "live")
  await expect
    .poll(() =>
      page.evaluate(() => window.localStorage.getItem("asl.spot.toast-cursor"))
    )
    .toMatch(/^\d+$/)
}

/** Settings' run control, confirmed in its dialog. */
async function control(page: Page, name: string) {
  await page.locator("section#run").getByRole("button", { name }).click()
  await page.getByRole("alertdialog").getByRole("button", { name }).click()
}

test.describe("Live trades and pop-ups (ExecPlan 0047, 0060)", () => {
  test.describe.configure({ mode: "serial" })
  test.skip(
    state !== "live" || !isolated,
    "Explicit live phase on a disposable browser database, seeded by tests.spot_browser_fixture"
  )
  test.beforeEach(async ({ page }) => {
    test.setTimeout(90_000)
    await page.setViewportSize({ width: 1440, height: 900 })
  })

  test("the stream's route answers the page's own request with events, and refuses another site's and a foreign Host @live", async ({
    page,
    browser,
    baseURL,
  }) => {
    await livePage(page)
    const own = await page.evaluate(async () => {
      const response = await fetch("/api/live")
      const reader = response.body!.getReader()
      let text = ""
      while (!text.includes("\n\n")) {
        const { done, value } = await reader.read()
        if (done) break
        text += new TextDecoder().decode(value)
      }
      await reader.cancel()
      return {
        status: response.status,
        type: response.headers.get("content-type"),
        cache: response.headers.get("cache-control"),
        text,
      }
    })
    expect(own.status).toBe(200)
    expect(own.type).toBe("text/event-stream; charset=utf-8")
    expect(own.cache).toBe("no-store")
    expect(own.text).toMatch(/^event: ready$/m)
    expect(own.text).toMatch(
      /^data: \{"state": ?"READY", ?"cursor": ?"\d+"\}$/m
    )
    // A request that no page of the app made: another site's, or one with no Fetch Metadata at all.
    const other = await browser.newContext()
    const requests: Record<string, string>[] = [
      { "sec-fetch-site": "cross-site" },
      {},
    ]
    for (const headers of requests) {
      const refused = await other.request.get(`${baseURL}/api/live`, {
        headers,
      })
      expect(refused.status()).toBe(403)
    }
    await other.close()
    const foreign = await page.request.get("/api/live", {
      headers: { host: "untrusted.example", "sec-fetch-site": "same-origin" },
    })
    expect(foreign.status()).toBe(421)
  })

  test("one stream for every tab of the browser; when its tab closes, another opens it @live", async ({
    context,
    page,
  }) => {
    const opened = streams(context)
    await livePage(page)
    const second = await context.newPage()
    await second.goto("/trades")
    await expect(badge(second)).toHaveAttribute("data-state", "live")
    const third = await context.newPage()
    await third.goto("/backtest")
    await expect(badge(third)).toHaveAttribute("data-state", "live")
    expect(opened).toHaveLength(1)
    await page.close()
    await expect.poll(() => opened.length).toBe(2)
    await expect(badge(second)).toHaveAttribute("data-state", "live")
    await expect(badge(third)).toHaveAttribute("data-state", "live")
  })

  test("the owner's Stop and sell shows at once: a toast for the sale, with the way to Trades @live", async ({
    page,
  }) => {
    await livePage(page, "/settings")
    const run = page.locator("section#run")
    await expect(run.getByRole("heading", { name: "Run #2" })).toBeVisible()
    await expect(page.locator("[data-slot='toast']")).toHaveCount(0)
    const started = Date.now()
    await control(page, "Stop and sell")
    // All of run #2's BTC, whose amount depends on the hour the fixture seeded (its book follows the walk).
    const toast = toasts(page, /^Sold 0\.\d+ BTC at [\d,]+\.\d+ USDT$/)
    // The feed's backup read is a minute away while live: only the stream shows it this soon.
    await expect(toast).toHaveCount(1, { timeout: 10_000 })
    test.info().annotations.push({
      type: "toast after the Stop and sell was confirmed",
      description: `${Date.now() - started} ms`,
    })
    await expect(toast).toContainText(
      /The run stopped, by you\. Fee [\d.]+ USDT\./
    )
    await expect(run).toContainText("Stopped")
    await expect(run.getByRole("button")).toHaveText(["Start trading"])
    await toast.getByRole("button", { name: "Trades" }).click()
    await expect(page).toHaveURL(/\/trades$/)
    await expect(
      page
        .getByRole("table", {
          name: "The account's buys and sells, newest first",
        })
        .getByRole("row")
        .nth(1)
    ).toContainText("Run stopped")
  })

  test("a desktop pop-up for the buy of the run the owner starts while no tab of the app has focus @live", async ({
    page,
  }) => {
    // The browser's notifications and focus, recorded: a headless browser shows neither.
    await page.addInitScript(() => {
      window.popups = []
      class Recorded {
        static permission: NotificationPermission = "default"
        static requestPermission() {
          Recorded.permission = "granted"
          return Promise.resolve(Recorded.permission)
        }
        onclick: (() => void) | null = null
        constructor(
          public title: string,
          public options: NotificationOptions
        ) {
          window.popups.push(this)
        }
        close() {}
      }
      Object.defineProperty(window, "Notification", {
        configurable: true,
        value: Recorded,
      })
      document.hasFocus = () => false
    })
    await livePage(page, "/settings")
    await page.getByRole("button", { name: "Trade alerts" }).click()
    const desktop = page.getByRole("menuitemcheckbox", {
      name: /Desktop pop-ups/,
    })
    await expect(desktop).toHaveAttribute("aria-checked", "false")
    await desktop.click()
    await expect(desktop).toHaveAttribute("aria-checked", "true")
    await page.keyboard.press("Escape")
    // The new run reads today at once: the rule's target is above what is held, so it buys.
    await control(page, "Start trading")
    const title = /^Bought [\d.]+ BTC at [\d,]+\.\d+ USDT$/
    await expect(toasts(page, title)).toHaveCount(1, { timeout: 15_000 })
    await expect
      .poll(() =>
        page.evaluate(() =>
          window.popups.map((popup) => [popup.title, popup.options.tag])
        )
      )
      .toEqual([
        [expect.stringMatching(title), expect.stringMatching(/^asl-fill-\d+$/)],
      ])
    await expect(
      page.locator("section#run").getByRole("heading", { name: "Run #3" })
    ).toBeVisible()
    await page.evaluate(() => window.popups[0].onclick?.())
    await expect(page).toHaveURL(/\/trades$/)
  })
})
