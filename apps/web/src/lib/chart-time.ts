// The charts' time labels; their colours follow the theme in chart-theme.ts.

import type { Time, TickMarkType } from "lightweight-charts"
import { formatAxisTime, formatDateTime } from "@/lib/display"

// Lightweight Charts' TickMarkType values in order: Year, Month, DayOfMonth, Time, TimeWithSeconds.
const TICK_PARTS = ["year", "month", "day", "minute", "second"] as const

/**
 * The chart's time labels in the viewer's zone (ExecPlan 0037). Lightweight Charts has no time zone
 * option, so its axis and crosshair labels are written in the zone while the bars keep their UTC
 * times, as its documentation advises.
 */
export function chartTime(zone: string) {
  return {
    timeScale: {
      tickMarkFormatter: (time: Time, type: TickMarkType) =>
        typeof time === "number"
          ? formatAxisTime(time * 1000, zone, TICK_PARTS[type])
          : null,
    },
    localization: {
      timeFormatter: (time: Time) =>
        typeof time === "number"
          ? formatDateTime(time * 1000, zone, { seconds: false })
          : String(time),
    },
  }
}
