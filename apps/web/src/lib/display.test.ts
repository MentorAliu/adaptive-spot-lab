import { describe, expect, it } from "vitest"
import {
  addDecimals,
  dayHeading,
  zoneDay,
  formatAgo,
  formatAxisTime,
  formatBytes,
  formatCompact,
  formatCount,
  formatDate,
  formatDateTime,
  formatDuration,
  formatExact,
  formatFixed,
  formatLeft,
  formatMilliseconds,
  formatMoney,
  formatNumber,
  formatPercent,
  formatPoints,
  formatPrice,
  formatQuantity,
  formatTime,
  placesOf,
  pricePlaces,
  timeTitle,
  utcDayEnd,
  zoneName,
  zoneOffset,
  zonePlace,
  zoneTimeOfDay,
} from "./display"
import { isTimeZone } from "./time-zone"

// ExecPlan 0037: each kind of value has one format, from the exact decimal string; times are in
// the viewer's zone. A value that is not a plain decimal string is shown as the API sent it.
describe("number formats", () => {
  it("writes USDT amounts to the cent, with small amounts kept to two significant digits", () => {
    expect(formatMoney("10000.00000000")).toBe("10,000.00")
    expect(formatMoney("-1234.5")).toBe("-1,234.50")
    expect(formatMoney("154.64477561763339025747")).toBe("154.64")
    expect(formatMoney("0.00012345")).toBe("0.00012")
    expect(formatMoney("0.5")).toBe("0.50")
    expect(formatMoney("12.3", { signed: true })).toBe("+12.30")
    expect(formatMoney("-4.05", { signed: true })).toBe("-4.05")
    expect(formatMoney("-0.001", { signed: true })).toBe("-0.001")
    expect(formatMoney("0", { signed: true })).toBe("0.00")
    expect(formatMoney("not a number")).toBe("not a number")
  })

  it("writes prices to five significant digits and at least two decimals", () => {
    expect(formatPrice("64123.456")).toBe("64,123.46")
    expect(formatPrice("83490.20000000")).toBe("83,490.20")
    expect(formatPrice("145.25")).toBe("145.25")
    expect(formatPrice("2.45678")).toBe("2.4568")
    expect(formatPrice("2.34")).toBe("2.340")
    expect(formatPrice("90")).toBe("90.00")
    expect(formatPrice("0.16789123")).toBe("0.16789")
    expect(formatPrice("0.000012345")).toBe("0.000012345")
    expect(pricePlaces("64123.4")).toBe(2)
    expect(pricePlaces("2.45")).toBe(4)
    expect(pricePlaces("x")).toBe(2)
    expect(formatFixed(64123.456, 2)).toBe("64,123.46")
    expect(formatFixed(Number.NaN, 2)).toBe("Unknown")
  })

  it("writes coin quantities exactly, without trailing zeros", () => {
    expect(formatQuantity("0.00093000")).toBe("0.00093")
    expect(formatQuantity("100")).toBe("100")
    expect(formatQuantity("12345.67890001")).toBe("12,345.67890001")
    expect(formatQuantity("0.00000001")).toBe("0.00000001")
    expect(formatNumber("1380.39859000")).toBe("1,380.39859")
    expect(formatNumber("2.5", { min: 2, max: 2 })).toBe("2.50")
  })

  it("pads exact columns so their decimal points line up", () => {
    expect(placesOf(["1.5", "2.125", "x"])).toBe(3)
    expect(placesOf(["10", "20"], 0)).toBe(0)
    expect(formatExact("12.5", 4)).toBe("12.5000")
    expect(formatExact("12.123456", 2)).toBe("12.123456")
    expect(formatExact("1234", 0)).toBe("1,234")
  })

  it("writes fractions as percentages and differences as percentage points, exactly", () => {
    expect(formatPercent("0.0123")).toBe("1.23%")
    expect(formatPercent("0.0123", { signed: true })).toBe("+1.23%")
    expect(formatPercent("-0.05", { decimals: 1, signed: true })).toBe("-5.0%")
    expect(formatPercent("0.00125", { max: 4 })).toBe("0.125%")
    expect(formatPercent("0.1", { max: 4 })).toBe("10.00%")
    expect(formatPoints("0.0123")).toBe("+1.2 pts")
    expect(formatPoints("-0.001")).toBe("-0.1 pts")
    expect(formatPoints("0")).toBe("0.0 pts")
    expect(formatPoints("12.3456", { decimals: 2 })).toBe("+1,234.56 pts")
  })

  it("writes counts, short amounts, sizes and lengths of time", () => {
    expect(formatCount(1234567)).toBe("1,234,567")
    expect(formatCount(null)).toBe("Unknown")
    expect(formatCompact("90123456")).toBe("90.1M")
    expect(formatCompact("1234")).toBe("1.23K")
    expect(formatBytes(820)).toBe("820 B")
    expect(formatBytes(12800)).toBe("12.5 KiB")
    expect(formatBytes(1288490188)).toBe("1.2 GiB")
    expect(formatBytes(null)).toBe("Unknown")
    expect(formatMilliseconds(120.4)).toBe("120 ms")
    expect(formatMilliseconds(1500)).toBe("1.5 s")
    expect(formatMilliseconds(125000)).toBe("2 min 05 s")
    expect(formatDuration(8.55)).toBe("8.5 s")
    expect(formatDuration(245)).toBe("4 min 05 s")
    expect(formatDuration(8100)).toBe("2 h 15 min")
    expect(formatDuration(7200)).toBe("2 h")
    expect(formatDuration(273600)).toBe("3 d 4 h")
    expect(formatDuration(172800)).toBe("2 d")
    expect(formatDuration(-1)).toBe("Unknown")
  })
})

describe("times in the viewer's zone", () => {
  const at = "2026-10-22T11:58:04Z"
  const now = Date.parse("2026-10-22T12:00:00Z")

  it("writes an instant in the zone, with the year only outside the current one", () => {
    expect(formatDateTime(at, "Europe/Budapest", { now })).toBe(
      "22 Oct, 13:58:04"
    )
    expect(formatDateTime(at, "Europe/Budapest", { now, seconds: false })).toBe(
      "22 Oct, 13:58"
    )
    expect(formatDateTime(at, "UTC", { now })).toBe("22 Oct, 11:58:04")
    expect(formatDateTime(Date.parse(at), "UTC", { now })).toBe(
      "22 Oct, 11:58:04"
    )
    expect(
      formatDateTime(at, "Europe/Budapest", {
        now: Date.parse("2027-01-02T00:00:00Z"),
      })
    ).toBe("22 Oct 2026, 13:58:04")
    expect(formatDateTime(at, "UTC", { year: true, now })).toBe(
      "22 Oct 2026, 11:58:04"
    )
    expect(formatDateTime("not a time", "UTC")).toBe("Unknown")
  })

  it("follows the zone's summer and winter time", () => {
    // Central European summer time ends on 25 October 2026 at 01:00 UTC.
    expect(formatTime("2026-10-25T00:30:00Z", "Europe/Budapest")).toBe(
      "02:30:00"
    )
    expect(formatTime("2026-10-25T01:30:00Z", "Europe/Budapest")).toBe(
      "02:30:00"
    )
    expect(zoneOffset("2026-10-25T00:30:00Z", "Europe/Budapest")).toBe("UTC+2")
    expect(zoneOffset("2026-10-25T01:30:00Z", "Europe/Budapest")).toBe("UTC+1")
    expect(zoneOffset(at, "Asia/Kolkata")).toBe("UTC+5:30")
    expect(zoneOffset(at, "America/St_Johns")).toBe("UTC-2:30")
    expect(zoneOffset(at, "UTC")).toBe("UTC")
  })

  it("names the zone and gives the full time with UTC on hover", () => {
    expect(zoneName("Europe/Budapest")).toBe("Budapest")
    expect(zoneName("America/New_York")).toBe("New York")
    expect(zoneName("Etc/UTC")).toBe("UTC")
    expect(zonePlace("Europe/Budapest")).toBe("Budapest time")
    expect(zonePlace("UTC")).toBe("UTC")
    expect(timeTitle(at, "Europe/Budapest")).toBe(
      "22 Oct 2026, 13:58:04 Budapest (UTC+2) · 22 Oct 2026, 11:58:04 UTC"
    )
    expect(timeTitle(at, "UTC")).toBe("22 Oct 2026, 11:58:04 UTC")
    expect(formatDate(at, "Europe/Budapest")).toBe("22 Oct 2026")
  })

  it("places UTC schedules and day ends on the zone's clock", () => {
    expect(utcDayEnd(Date.parse(at))).toBe(Date.parse("2026-10-23T00:00:00Z"))
    expect(zoneTimeOfDay("00:30", "Europe/Budapest", now)).toBe("02:30")
    expect(
      zoneTimeOfDay("00:30", "Europe/Budapest", Date.parse("2026-11-02T05:00Z"))
    ).toBe("01:30")
    expect(zoneTimeOfDay("ab:cd", "Europe/Budapest", now)).toBe("ab:cd")
  })

  it("labels a chart's time axis in the zone", () => {
    expect(formatAxisTime(at, "Europe/Budapest", "year")).toBe("2026")
    expect(formatAxisTime(at, "Europe/Budapest", "month")).toBe("Oct")
    expect(
      formatAxisTime("2026-10-21T23:30:00Z", "Europe/Budapest", "day")
    ).toBe("22")
    expect(formatAxisTime(at, "Europe/Budapest", "minute")).toBe("13:58")
    expect(formatAxisTime(at, "Europe/Budapest", "second")).toBe("13:58:04")
  })

  it("accepts only zone names this runtime knows", () => {
    expect(isTimeZone("Europe/Budapest")).toBe(true)
    expect(isTimeZone("UTC")).toBe(true)
    expect(isTimeZone("Mars/Olympus_Mons")).toBe(false)
    expect(isTimeZone("Europe/Budapest; Path=/")).toBe(false)
    expect(isTimeZone("A".repeat(65))).toBe(false)
    expect(isTimeZone(undefined)).toBe(false)
  })

  it("says how long ago and how long left in short words (ExecPlan 0048)", () => {
    const noon = Date.parse("2026-10-31T12:00:00Z")
    expect(formatAgo("2026-10-31T11:59:30Z", noon)).toBe("just now")
    expect(formatAgo("2026-10-31T11:53:00Z", noon)).toBe("7 min ago")
    expect(formatAgo("2026-10-31T08:00:00Z", noon)).toBe("4 h ago")
    expect(formatAgo("2026-10-28T12:00:00Z", noon)).toBe("3 d ago")
    expect(formatAgo("not a time", noon)).toBe("Unknown")
    expect(formatLeft("2026-10-31T11:00:00Z", noon)).toBe("now")
    expect(formatLeft("2026-10-31T12:00:45Z", noon)).toBe("45 s")
    expect(formatLeft("2026-10-31T12:08:00Z", noon)).toBe("8 min")
    expect(formatLeft("2026-10-31T17:08:00Z", noon)).toBe("5 h 08 min")
    expect(formatLeft("2026-11-02T15:00:00Z", noon)).toBe("2 d 3 h")
  })
})

describe("addDecimals", () => {
  it("adds the API's decimals exactly, at the most places any has", () => {
    expect(addDecimals(["-6.70530559", "5.12454979"])).toBe("-1.58075580")
    expect(addDecimals(["0.1", "0.2"])).toBe("0.3")
    expect(addDecimals(["10", "-10.00"])).toBe("0.00")
  })

  it("refuses a value that is not a plain decimal, and an empty list", () => {
    expect(addDecimals(["1", "1e3"])).toBeNull()
    expect(addDecimals([])).toBeNull()
  })
})

describe("a day's heading", () => {
  it("groups by the zone's calendar day and names today and yesterday once the time is known", () => {
    // 22:30 UTC on 30 Oct is 23:30 in Budapest (UTC+1 from 25 Oct) and already 31 Oct in Tokyo.
    expect(zoneDay("2026-10-30T22:30:00Z", "Europe/Budapest")).toBe(
      "2026-10-30"
    )
    expect(zoneDay("2026-10-30T22:30:00Z", "Asia/Tokyo")).toBe("2026-10-31")
    expect(zoneDay("not a time", "UTC")).toBeNull()
    const now = Date.parse("2026-10-31T09:00:00Z")
    expect(dayHeading("2026-10-31", "UTC", now)).toBe("Today · Sat 31 Oct")
    expect(dayHeading("2026-10-30", "UTC", now)).toBe("Yesterday · Fri 30 Oct")
    expect(dayHeading("2026-10-28", "UTC", now)).toBe("Wed 28 Oct")
    expect(dayHeading("2025-12-31", "UTC", now)).toBe("Wed 31 Dec 2025")
    expect(dayHeading("2026-10-31", "UTC", null)).toBe("Sat 31 Oct")
    // Across a month's start.
    expect(
      dayHeading("2026-10-31", "UTC", Date.parse("2026-11-01T08:00:00Z"))
    ).toBe("Yesterday · Sat 31 Oct")
  })
})
