import type { UTCTimestamp } from "lightweight-charts"
import { describe, expect, it } from "vitest"
import { chartTime } from "./chart-time"

describe("chart times in the viewer's zone (ExecPlan 0037)", () => {
  const at = Date.parse("2026-10-22T11:58:04Z") / 1000
  const { timeScale, localization } = chartTime("Europe/Budapest")
  // Lightweight Charts' TickMarkType values: Year, Month, DayOfMonth, Time, TimeWithSeconds.
  const tick = (type: number) =>
    timeScale.tickMarkFormatter(at as UTCTimestamp, type)

  it("labels the time axis in the zone, by the kind of tick the chart asks for", () => {
    expect([0, 1, 2, 3, 4].map(tick)).toEqual([
      "2026",
      "Oct",
      "22",
      "13:58",
      "13:58:04",
    ])
    expect(timeScale.tickMarkFormatter("2026-10-22", 2)).toBeNull()
  })

  it("writes the crosshair's time in the zone", () => {
    expect(localization.timeFormatter(at as UTCTimestamp)).toMatch(
      /^22 Oct( 2026)?, 13:58$/
    )
    expect(
      chartTime("UTC").localization.timeFormatter(at as UTCTimestamp)
    ).toMatch(/^22 Oct( 2026)?, 11:58$/)
  })
})
