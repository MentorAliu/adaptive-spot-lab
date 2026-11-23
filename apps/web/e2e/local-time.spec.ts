import { expect, test } from "@playwright/test"
import type { Page } from "@playwright/test"
import { formatDateTime, formatTime } from "../src/lib/display"

// ExecPlan 0037: every time on the pages is in the viewer's zone. This browser is in Budapest, on the
// spot pages' database (tests/spot_browser_fixture.py seed, ExecPlan 0060); the spec only reads. The
// server writes UTC until the browser has named its zone in a cookie, then writes the zone from the start.
// The rule's days stay UTC days: they are named as such.
const state = process.env.ASL_SPOT_BROWSER ?? ""
const ZONE = "Europe/Budapest"

const isolated =
  process.env.ASL_TEST_ISOLATED === "1" &&
  /^asl_m1_[a-z0-9_]+_browser$/.test(process.env.ASL_DB_NAME ?? "")

test.use({ timezoneId: ZONE })

/** Page errors and console errors, such as a hydration mismatch React reports. */
function watchErrors(page: Page): string[] {
  const errors: string[] = []
  page.on("pageerror", (error) => errors.push(error.message))
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(message.text())
  })
  return errors
}

test.describe("Times in the viewer's zone (ExecPlan 0037)", () => {
  test.skip(
    state !== "pages" || !isolated,
    "Explicit spot pages phase on a disposable browser database"
  )

  test("the first page is written in UTC, the browser's zone takes over without a hydration error, and the next page is written in it @local-time", async ({
    page,
    context,
  }) => {
    test.setTimeout(120_000)
    const errors = watchErrors(page)
    const first = await page.goto("/settings")
    expect(await first!.text()).toContain("Times in UTC")
    // The sidebar's note, after hydration: the browser's zone.
    await expect(
      page.getByText("Times in Budapest time").filter({ visible: true })
    ).toBeVisible()
    const cookie = (await context.cookies()).find(
      (item) => item.name === "asl_time_zone"
    )
    expect(cookie?.value).toBe("Europe%2FBudapest")
    expect(cookie?.sameSite).toBe("Lax")

    // The server prefetches the trades, so their times come in the page itself, in Budapest time.
    const response = await page.goto("/trades")
    const html = await response!.text()
    expect(html).toContain("Times in Budapest time")
    const time = page.locator("main table time").first()
    await expect(time).toBeVisible()
    const instant = (await time.getAttribute("datetime"))!
    const local = formatDateTime(instant, ZONE)
    await expect(time).toHaveText(local)
    expect(html).toContain(`>${local}</time>`)
    // On hover: the full date, the zone's offset and the same instant in UTC.
    const title = (await time.getAttribute("title"))!
    expect(title).toMatch(/^.+ Budapest \(UTC\+[12]\) · .+ UTC$/)
    expect(title).toContain(formatDateTime(instant, ZONE, { year: true }))
    expect(title).toContain(
      `${formatDateTime(instant, "UTC", { year: true })} UTC`
    )
    expect(errors).toEqual([])
  })

  test("the run's start, the reading's time and the next reading read in Budapest time; the rule's days stay UTC days @local-time", async ({
    page,
  }) => {
    test.setTimeout(120_000)
    const errors = watchErrors(page)
    await page.goto("/settings")
    const started = page
      .locator("section#run")
      .getByText(/^Started$/)
      .locator("xpath=following-sibling::dd[1]//time")
    await expect(started).toBeVisible()
    await expect(started).toHaveText(
      formatDateTime((await started.getAttribute("datetime"))!, ZONE, {
        seconds: false,
      })
    )

    // The Cockpit: the reading was read at a Budapest time; the next one is at 00:05 UTC, 01:05 in
    // Budapest in winter.
    await page.goto("/")
    const reading = page
      .locator("main [data-slot='card']")
      .filter({ hasText: "The rule's reading" })
    await expect(reading).toContainText(
      /Read \d{2}:\d{2} on \d{1,2} \w{3} \d{4}/
    )
    await expect(reading).toContainText(
      `Next reading at ${formatTime(nextReading(), ZONE, { seconds: false })}.`
    )
    // The readings name the UTC day each was for.
    await page.goto("/trades?tab=readings")
    const day = page
      .getByRole("table", { name: "The rule's daily readings, newest first" })
      .getByRole("row")
      .nth(1)
      .getByRole("cell")
      .first()
    await expect(day).toHaveText(/^\d{1,2} \w{3} \d{4}$/)
    expect(errors).toEqual([])
  })
})

/** The next reading: 00:05 UTC of the next UTC day, as the seeded run has read today. */
function nextReading(): string {
  const now = new Date()
  return new Date(
    Date.UTC(
      now.getUTCFullYear(),
      now.getUTCMonth(),
      now.getUTCDate() + 1,
      0,
      5
    )
  ).toISOString()
}
