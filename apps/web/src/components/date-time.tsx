import { formatDateTime, timeTitle, toDate } from "@/lib/display"
import { useTimeZone } from "./time-zone-provider"

/**
 * An instant in the viewer's time zone (22 Oct, 13:58:04), with the full date, the zone's offset
 * and the same instant in UTC on hover (ExecPlan 0037).
 */
export function DateTime({
  value,
  seconds = true,
  fallback = "Not recorded",
}: {
  value: string | number | null
  seconds?: boolean
  fallback?: string
}) {
  const zone = useTimeZone()
  if (value === null) return fallback
  const date = toDate(value)
  if (date === null) return "Unknown"
  return (
    <time dateTime={date.toISOString()} title={timeTitle(date, zone)}>
      {formatDateTime(date, zone, { seconds })}
    </time>
  )
}
