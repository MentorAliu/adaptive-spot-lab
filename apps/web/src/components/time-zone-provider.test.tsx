import { act, cleanup, render, screen } from "@testing-library/react"
import { hydrateRoot } from "react-dom/client"
import { renderToString } from "react-dom/server"
import { afterEach, describe, expect, it, vi } from "vitest"
import { DateTime } from "./date-time"
import { TimeZoneProvider, ZoneNote, useTimeText } from "./time-zone-provider"
import type * as TimeZone from "@/lib/time-zone"

// The browser here is in Budapest; the server writes UTC until the cookie names the zone.
vi.mock("@/lib/time-zone", async (importOriginal) => ({
  ...(await importOriginal<typeof TimeZone>()),
  browserTimeZone: () => "Europe/Budapest",
}))

const AT = "2026-10-22T11:58:04Z"
// The year shows only outside the current one, so these hold in any year.
const BUDAPEST = /^22 Oct( 2026)?, 13:58:04$/
const UTC = /^22 Oct( 2026)?, 11:58:04$/

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  document.body.innerHTML = ""
})

function Sentence({ value }: { value: string | null }) {
  const time = useTimeText()
  return <p>Next try {time(value, { seconds: false })}</p>
}

describe("times in the viewer's zone (ExecPlan 0037)", () => {
  it("writes a time in the browser's zone, with its offset and UTC on hover", () => {
    render(
      <TimeZoneProvider serverZone="UTC">
        <DateTime value={AT} />
        <ZoneNote />
        <Sentence value={AT} />
      </TimeZoneProvider>
    )
    const time = screen.getByText(BUDAPEST)
    expect(time.tagName).toBe("TIME")
    expect(time.getAttribute("datetime")).toBe("2026-10-22T11:58:04.000Z")
    expect(time.getAttribute("title")).toBe(
      "22 Oct 2026, 13:58:04 Budapest (UTC+2) · 22 Oct 2026, 11:58:04 UTC"
    )
    expect(screen.getByText("Times in Budapest time")).toBeTruthy()
    expect(screen.getByText(/^Next try 22 Oct( 2026)?, 13:58$/)).toBeTruthy()
    // The cookie lets the server write the next page in this zone from the start.
    expect(document.cookie).toContain("asl_time_zone=Europe%2FBudapest")
  })

  it("says what is missing instead of guessing a time", () => {
    render(
      <TimeZoneProvider serverZone="UTC">
        <p>
          <DateTime value={null} />
        </p>
        <p>
          <DateTime value={null} fallback="Not yet" />
        </p>
        <p>
          <DateTime value="not a time" />
        </p>
        <Sentence value={null} />
      </TimeZoneProvider>
    )
    expect(screen.getByText("Not recorded")).toBeTruthy()
    expect(screen.getByText("Not yet")).toBeTruthy()
    expect(screen.getByText("Unknown")).toBeTruthy()
    expect(screen.getByText("Next try Not recorded")).toBeTruthy()
  })

  it("hydrates the server's text, then switches to the browser's zone without a mismatch", async () => {
    const page = (
      <TimeZoneProvider serverZone="UTC">
        <DateTime value={AT} />
        <ZoneNote />
      </TimeZoneProvider>
    )
    const container = document.createElement("div")
    container.innerHTML = renderToString(page)
    document.body.append(container)
    expect(container.querySelector("time")?.textContent).toMatch(UTC)
    expect(container.textContent).toContain("Times in UTC")
    const errors = vi.spyOn(console, "error")
    const recoverable = vi.fn()
    await act(async () => {
      hydrateRoot(container, page, { onRecoverableError: recoverable })
    })
    expect(recoverable).not.toHaveBeenCalled()
    expect(errors).not.toHaveBeenCalled()
    expect(container.querySelector("time")?.textContent).toMatch(BUDAPEST)
    expect(container.textContent).toContain("Times in Budapest time")
  })
})
