/**
 * The viewer's time zone (ExecPlan 0037). The browser names it in this cookie, so the server
 * writes a page's times in the same zone and hydration sees the same text; before the first
 * visit, and for any value this runtime does not know as an IANA zone, the server uses UTC.
 */
export const TIME_ZONE_COOKIE = "asl_time_zone"

export function isTimeZone(value: unknown): value is string {
  if (
    typeof value !== "string" ||
    value.length > 64 ||
    !/^[A-Za-z][A-Za-z0-9_+\-/]*$/.test(value)
  )
    return false
  try {
    new Intl.DateTimeFormat("en-US", { timeZone: value })
    return true
  } catch {
    return false
  }
}

let browserZone: string | null | undefined

/** The browser's own zone, such as Europe/Budapest, or null when it names none this runtime knows. */
export function browserTimeZone(): string | null {
  if (browserZone === undefined) {
    const zone = Intl.DateTimeFormat().resolvedOptions().timeZone
    browserZone = isTimeZone(zone) ? zone : null
  }
  return browserZone
}
