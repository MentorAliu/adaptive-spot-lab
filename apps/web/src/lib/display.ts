/**
 * Display only (ExecPlan 0037). The API's values stay exact decimal strings and UTC instants in
 * every request and cache; these functions only shape what the eye reads. Digits use the inputs'
 * separators (1,234.56) and Intl's exact string formatting, so no value passes through a float.
 * A value that is not a plain decimal string is shown as the API sent it, never guessed at.
 */

const DECIMAL = /^-?\d+(?:\.\d+)?$/

type Decimal = `${number}`

function decimal(value: string): Decimal | null {
  return DECIMAL.test(value) ? (value as Decimal) : null
}

/** Decimal places that show `digits` significant digits of the value; zero needs none. */
function placesFor(value: Decimal, digits: number): number {
  const [whole, fraction = ""] = value.replace("-", "").split(".")
  const integer = whole.replace(/^0+/, "")
  if (integer.length > 0) return Math.max(0, digits - integer.length)
  const zeros = /^0*/.exec(fraction)![0].length
  return zeros === fraction.length ? 0 : zeros + digits
}

function fractionLength(value: Decimal): number {
  return (value.split(".")[1] ?? "").replace(/0+$/, "").length
}

const numberFormats = new Map<string, Intl.NumberFormat>()

function numberFormat(
  min: number,
  max: number,
  signed = false,
  style: "decimal" | "percent" = "decimal"
): Intl.NumberFormat {
  const key = `${min}:${max}:${signed}:${style}`
  let format = numberFormats.get(key)
  if (!format) {
    format = new Intl.NumberFormat("en-US", {
      style,
      minimumFractionDigits: min,
      maximumFractionDigits: Math.max(min, max),
      // A loss that rounds to zero reads 0.00, never -0.00.
      signDisplay: signed ? "exceptZero" : "negative",
    })
    numberFormats.set(key, format)
  }
  return format
}

/** USDT amounts: cents; an amount under 0.10, such as a small fee, keeps two significant digits. */
export function formatMoney(
  value: string,
  { signed = false }: { signed?: boolean } = {}
): string {
  const exact = decimal(value)
  if (exact === null) return value
  return numberFormat(2, Math.max(2, placesFor(exact, 2)), signed).format(exact)
}

/**
 * A coin's price in USDT: up to five significant digits and at least two decimals, so a column of
 * one coin's prices keeps one length (64,123.46; 145.25; 2.4567; 0.16789). Trailing zeros are kept
 * to four significant digits (90.00, 2.340).
 */
export function formatPrice(value: string): string {
  const exact = decimal(value)
  if (exact === null) return value
  const max = Math.max(2, placesFor(exact, 5))
  const min = Math.max(2, Math.min(max, placesFor(exact, 4)))
  return numberFormat(min, max).format(exact)
}

/** The decimals `formatPrice` shows at most for a price of this size, for a chart's price axis. */
export function pricePlaces(value: string): number {
  const exact = decimal(value)
  return exact === null ? 2 : Math.max(2, placesFor(exact, 5))
}

/** A chart's own number (already a display conversion) at fixed decimals: 64,123.46. */
export function formatFixed(value: number, places: number): string {
  return Number.isFinite(value)
    ? numberFormat(places, places).format(value)
    : "Unknown"
}

/** A coin amount, exactly as held: every nonzero digit, no trailing zeros (0.00093, 100). */
export function formatQuantity(value: string): string {
  const exact = decimal(value)
  if (exact === null) return value
  return numberFormat(0, Math.min(20, fractionLength(exact))).format(exact)
}

/** Any other decimal: grouped, with `min` to `max` decimals. */
export function formatNumber(
  value: string,
  {
    min = 0,
    max = 20,
    signed = false,
  }: { min?: number; max?: number; signed?: boolean } = {}
): string {
  const exact = decimal(value)
  if (exact === null) return value
  return numberFormat(min, max, signed).format(exact)
}

/** Exact digits padded to `places` decimals, for a table whose column should line up. */
export function formatExact(value: string, places: number): string {
  const exact = decimal(value)
  if (exact === null) return value
  return numberFormat(
    places,
    Math.max(places, Math.min(20, fractionLength(exact)))
  ).format(exact)
}

/** The decimals the longest of the values needs, at least `min`, for `formatExact`. */
export function placesOf(values: string[], min = 2): number {
  let places = min
  for (const value of values) {
    const exact = decimal(value)
    if (exact !== null) places = Math.max(places, fractionLength(exact))
  }
  return Math.min(20, places)
}

/**
 * A fraction (0.0123) as a percentage (1.23%), exact before rounding; `max` allows more decimals
 * where they matter, as in a limit of 0.125%, and `signed` marks a change (+1.23%).
 */
export function formatPercent(
  fraction: string,
  {
    decimals = 2,
    max = decimals,
    signed = false,
  }: { decimals?: number; max?: number; signed?: boolean } = {}
): string {
  const exact = decimal(fraction)
  if (exact === null) return fraction
  return numberFormat(decimals, max, signed, "percent").format(exact)
}

/** The decimal times 100, exactly, by moving its point two places: 0.0123 is 1.23. */
function hundredfold(value: Decimal): Decimal {
  const sign = value.startsWith("-") ? "-" : ""
  const [whole, fraction = ""] = value.replace("-", "").split(".")
  const digits = `${whole}${fraction.padEnd(2, "0")}`
  const point = whole.length + 2
  const shifted = `${digits.slice(0, point).replace(/^0+(?=\d)/, "")}${point < digits.length ? `.${digits.slice(point)}` : ""}`
  return `${sign}${shifted}` as Decimal
}

/** A difference of fractions (0.0123) in percentage points (+1.2 pts); signed by default. */
export function formatPoints(
  fraction: string,
  { decimals = 1, signed = true }: { decimals?: number; signed?: boolean } = {}
): string {
  const exact = decimal(fraction)
  if (exact === null) return fraction
  return `${numberFormat(decimals, decimals, signed).format(hundredfold(exact))} pts`
}

export function formatCount(value: number | null): string {
  return value !== null && Number.isFinite(value)
    ? numberFormat(0, 0).format(value)
    : "Unknown"
}

/** Large amounts in short form (1.23M), for overviews whose exact figure is a hover away. */
const compactFormat = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumSignificantDigits: 3,
})

export function formatCompact(value: string): string {
  const exact = decimal(value)
  return exact === null ? value : compactFormat.format(exact)
}

const BYTE_UNITS = ["B", "KiB", "MiB", "GiB", "TiB"]
const byteFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 })

/** A size in bytes: 820 B, 12.5 KiB, 1.2 GiB. */
export function formatBytes(bytes: number | null): string {
  if (bytes === null || !Number.isFinite(bytes) || bytes < 0) return "Unknown"
  let size = bytes
  let unit = 0
  while (size >= 1024 && unit < BYTE_UNITS.length - 1) {
    size /= 1024
    unit += 1
  }
  return `${byteFormat.format(unit === 0 ? size : Math.round(size * 10) / 10)} ${BYTE_UNITS[unit]}`
}

/** A short delay: 120 ms under a second, longer ones as durations (1.5 s, 2 min 05 s). */
export function formatMilliseconds(ms: number): string {
  if (!Number.isFinite(ms) || ms < 0) return "Unknown"
  return ms < 1000 ? `${Math.round(ms)} ms` : formatDuration(ms / 1000)
}

/** A length of time: 8.5 s, 4 min 05 s, 2 h 15 min, 3 d 4 h. */
export function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "Unknown"
  if (seconds < 10) return `${(Math.floor(seconds * 10) / 10).toFixed(1)} s`
  if (seconds < 60) return `${Math.floor(seconds)} s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60)
    return `${minutes} min ${String(Math.floor(seconds % 60)).padStart(2, "0")} s`
  const hours = Math.floor(minutes / 60)
  if (hours < 24)
    return minutes % 60 === 0 ? `${hours} h` : `${hours} h ${minutes % 60} min`
  const days = Math.floor(hours / 24)
  return hours % 24 === 0 ? `${days} d` : `${days} d ${hours % 24} h`
}

// Times: the viewer's time zone, written from Intl's numeric parts with fixed month names, so the
// server and the browser write the same text whatever their ICU data.
const MONTHS = [
  "Jan",
  "Feb",
  "Mar",
  "Apr",
  "May",
  "Jun",
  "Jul",
  "Aug",
  "Sep",
  "Oct",
  "Nov",
  "Dec",
]

type Clock = {
  year: number
  month: number
  day: number
  hour: number
  minute: number
  second: number
}

const dateFormats = new Map<string, Intl.DateTimeFormat>()

function clock(date: Date, zone: string): Clock {
  let format = dateFormats.get(zone)
  if (!format) {
    format = new Intl.DateTimeFormat("en-US", {
      timeZone: zone,
      year: "numeric",
      month: "numeric",
      day: "numeric",
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      hourCycle: "h23",
    })
    dateFormats.set(zone, format)
  }
  const parts: Record<string, number> = {}
  for (const part of format.formatToParts(date))
    if (part.type !== "literal") parts[part.type] = Number(part.value)
  return parts as Clock
}

const two = (value: number) => String(value).padStart(2, "0")

/** An API instant (ISO text or milliseconds) as a Date, or null when it is not one. */
export function toDate(value: string | number | Date): Date | null {
  const date = value instanceof Date ? value : new Date(value)
  return Number.isNaN(date.getTime()) ? null : date
}

export type TimeOptions = {
  /** Show seconds (13:58:04) or stop at minutes (13:58). */
  seconds?: boolean
  /** Write the year even in the current year. */
  year?: boolean
  /** The current time, for the current year; tests pass it. */
  now?: number
}

/** 22 Oct, 13:58:04 in the given zone; another year adds it (22 Oct 2025, 13:58:04). */
export function formatDateTime(
  value: string | number | Date,
  zone: string,
  { seconds = true, year = false, now = Date.now() }: TimeOptions = {}
): string {
  const date = toDate(value)
  if (date === null) return "Unknown"
  const at = clock(date, zone)
  const shown = year || at.year !== clock(new Date(now), zone).year
  return `${at.day} ${MONTHS[at.month - 1]}${shown ? ` ${at.year}` : ""}, ${formatClock(at, seconds)}`
}

function formatClock(at: Clock, seconds: boolean): string {
  return `${two(at.hour)}:${two(at.minute)}${seconds ? `:${two(at.second)}` : ""}`
}

/** 13:58:04 in the given zone. */
export function formatTime(
  value: string | number | Date,
  zone: string,
  { seconds = true }: { seconds?: boolean } = {}
): string {
  const date = toDate(value)
  return date === null ? "Unknown" : formatClock(clock(date, zone), seconds)
}

/** A time of day the API gives in UTC (00:30) as the zone's clock reads it on the day of `on`. */
export function zoneTimeOfDay(utc: string, zone: string, on: number): string {
  const [hour, minute] = utc.split(":").map(Number)
  const day = new Date(on)
  if (Number.isNaN(day.getTime()) || !Number.isInteger(hour + minute))
    return utc
  return formatTime(
    Date.UTC(
      day.getUTCFullYear(),
      day.getUTCMonth(),
      day.getUTCDate(),
      hour,
      minute
    ),
    zone,
    { seconds: false }
  )
}

/** One part of an instant for a chart's time axis, in the given zone: 2026, Oct, 22, 13:00. */
export function formatAxisTime(
  value: string | number | Date,
  zone: string,
  part: "year" | "month" | "day" | "minute" | "second"
): string {
  const date = toDate(value)
  if (date === null) return "Unknown"
  const at = clock(date, zone)
  if (part === "year") return String(at.year)
  if (part === "month") return MONTHS[at.month - 1]
  if (part === "day") return String(at.day)
  return formatClock(at, part === "second")
}

/** 22 Oct 2026 in the given zone. */
export function formatDate(
  value: string | number | Date,
  zone: string
): string {
  const date = toDate(value)
  if (date === null) return "Unknown"
  const at = clock(date, zone)
  return `${at.day} ${MONTHS[at.month - 1]} ${at.year}`
}

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

/** The zone's calendar day of an instant (2026-10-30), to group a list by local day. */
export function zoneDay(
  value: string | number | Date,
  zone: string
): string | null {
  const date = toDate(value)
  if (date === null) return null
  const at = clock(date, zone)
  return `${at.year}-${two(at.month)}-${two(at.day)}`
}

/**
 * A calendar day (2026-10-30) as a heading (ExecPlan 0048 part 2): Today · Fri 30 Oct, Yesterday ·
 * Thu 29 Oct, or Wed 28 Oct; another year than today's adds it. Without `now` (while the server
 * renders and during hydration) it is the plain day.
 */
export function dayHeading(
  day: string,
  zone: string,
  now: number | null
): string {
  const [year, month, date] = day.split("-").map(Number)
  const weekday =
    WEEKDAYS[new Date(Date.UTC(year, month - 1, date)).getUTCDay()]
  const today = now === null ? null : zoneDay(now, zone)
  const other = today !== null && Number(today.slice(0, 4)) !== year
  const plain = `${weekday} ${date} ${MONTHS[month - 1]}${other ? ` ${year}` : ""}`
  if (today === null) return plain
  if (day === today) return `Today · ${plain}`
  const [y, m, d] = today.split("-").map(Number)
  const before = new Date(Date.UTC(y, m - 1, d - 1))
  const yesterday = `${before.getUTCFullYear()}-${two(before.getUTCMonth() + 1)}-${two(before.getUTCDate())}`
  return day === yesterday ? `Yesterday · ${plain}` : plain
}

/** The zone's offset from UTC at that instant: UTC+2, UTC+5:30, UTC-3 or UTC. */
export function zoneOffset(
  value: string | number | Date,
  zone: string
): string {
  const date = toDate(value)
  if (date === null) return "UTC"
  const at = clock(date, zone)
  const local = Date.UTC(
    at.year,
    at.month - 1,
    at.day,
    at.hour,
    at.minute,
    at.second
  )
  const minutes = Math.round(
    (local - Math.floor(date.getTime() / 1000) * 1000) / 60000
  )
  if (minutes === 0) return "UTC"
  const size = Math.abs(minutes)
  return `UTC${minutes > 0 ? "+" : "-"}${Math.floor(size / 60)}${size % 60 ? `:${two(size % 60)}` : ""}`
}

/** The zone's place name: Budapest for Europe/Budapest, UTC for UTC. */
export function zoneName(zone: string): string {
  if (zone === "UTC" || zone === "Etc/UTC") return "UTC"
  return (zone.split("/").pop() ?? zone).replaceAll("_", " ")
}

/** How a sentence names the zone's clock: UTC, or Budapest time. */
export function zonePlace(zone: string): string {
  const name = zoneName(zone)
  return name === "UTC" ? "UTC" : `${name} time`
}

/** The end of the UTC day that holds `now` (the next 00:00 UTC), when daily limits reset. */
export function utcDayEnd(now: number): number {
  const day = 86_400_000
  return (Math.floor(now / day) + 1) * day
}

/** The hover text of a time: the full local time with its offset, and the same instant in UTC. */
export function timeTitle(value: string | number | Date, zone: string): string {
  const utc = `${formatDateTime(value, "UTC", { year: true })} UTC`
  const offset = zoneOffset(value, zone)
  return offset === "UTC" && zoneName(zone) === "UTC"
    ? utc
    : `${formatDateTime(value, zone, { year: true })} ${zoneName(zone)} (${offset}) · ${utc}`
}

/**
 * How long ago an instant was, for text that reads faster than a clock time (ExecPlan 0048): just now,
 * 7 min ago, 4 h ago, 2 d ago. A time in the future reads "just now"; the exact time is a hover away.
 */
export function formatAgo(value: string | number | Date, now: number): string {
  const date = toDate(value)
  if (date === null) return "Unknown"
  const seconds = (now - date.getTime()) / 1000
  if (seconds < 45) return "just now"
  const minutes = Math.round(seconds / 60)
  if (minutes < 60) return `${minutes} min ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 48) return `${hours} h ago`
  return `${Math.floor(hours / 24)} d ago`
}

/** Time left until an instant (ExecPlan 0048): 45 s, 8 min, 5 h 08 min, 2 d 3 h; none left reads "now". */
export function formatLeft(value: string | number | Date, now: number): string {
  const date = toDate(value)
  if (date === null) return "Unknown"
  const seconds = Math.ceil((date.getTime() - now) / 1000)
  if (seconds <= 0) return "now"
  if (seconds < 60) return `${seconds} s`
  const minutes = Math.ceil(seconds / 60)
  if (minutes < 60) return `${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 48) return `${hours} h ${two(minutes % 60)} min`
  const days = Math.floor(hours / 24)
  return `${days} d ${hours % 24} h`
}

function scaled(value: Decimal, places: number): bigint {
  const [whole, fraction = ""] = value.replace("-", "").split(".")
  const digits = BigInt(`${whole}${fraction.padEnd(places, "0")}`)
  return value.startsWith("-") ? -digits : digits
}

function unscaled(value: bigint, places: number): string {
  const digits = (value < 0n ? -value : value)
    .toString()
    .padStart(places + 1, "0")
  const point = digits.length - places
  return `${value < 0n ? "-" : ""}${digits.slice(0, point)}${places > 0 ? `.${digits.slice(point)}` : ""}`
}

/**
 * `a - b` exactly, as a decimal string, for a figure the page shows beside the API's own (ExecPlan
 * 0048): the result since the start is the equity less what was added. Null when either is not one.
 */
export function subtractDecimal(a: string, b: string): string | null {
  const x = decimal(a)
  const y = decimal(b)
  if (x === null || y === null) return null
  const places = Math.max(
    (x.split(".")[1] ?? "").length,
    (y.split(".")[1] ?? "").length
  )
  return unscaled(scaled(x, places) - scaled(y, places), places)
}

/** NAV per unit started at 100 (INITIAL_NAV), so its return is NAV / 100 - 1, exactly: 104.86 is 0.0486. */
export function navReturn(nav: string): string | null {
  const change = subtractDecimal(nav, "100")
  if (change === null) return null
  const places = (change.split(".")[1] ?? "").length
  return unscaled(scaled(change as Decimal, places), places + 2)
}

/**
 * The exact sum of decimal strings (ExecPlan 0048 part 2): the net of the trades a page shows, added
 * up as the API wrote each. Null when any is not a plain decimal, or there are none.
 */
export function addDecimals(values: string[]): string | null {
  const exact = values.map(decimal)
  if (exact.length === 0 || exact.some((value) => value === null)) return null
  const places = Math.max(
    ...exact.map((value) => ((value as string).split(".")[1] ?? "").length)
  )
  return unscaled(
    exact.reduce((sum, value) => sum + scaled(value as Decimal, places), 0n),
    places
  )
}
