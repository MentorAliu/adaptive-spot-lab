import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react"
import type { ReactNode } from "react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import type { Account, Workspace } from "@/account/schemas"
import dayCandlesSample from "@/spot/samples/candles-1d.json"
import marketSample from "@/spot/samples/market.json"
import markersSample from "@/spot/samples/markers.json"
import overviewSample from "@/spot/samples/overview.json"
import statusSample from "@/spot/samples/status.json"
import tradesSample from "@/spot/samples/trades.json"
import valuationsSample from "@/spot/samples/valuations.json"
import * as functions from "@/spot/spot.functions"
import {
  SPOT_KEY,
  candlesQuery,
  marketQuery,
  recentTradesQuery,
  spotMarkersQuery,
  spotOverviewQuery,
  spotValuationsQuery,
} from "@/spot/spot.query"
import {
  candlesSchema,
  marketSchema,
  markersSchema,
  overviewSchema,
  tradePageSchema,
  valuationsSchema,
} from "@/spot/schemas"
import type { Overview } from "@/spot/schemas"
import type { TradingStatus } from "@/spot/status"
import { statusQueryOptions } from "@/system/status.query"
import { systemStatusSchema } from "@/system/status.schema"
import { CockpitPage } from "./cockpit-page"
import { changeText, equityPoints, equityText } from "./equity-chart"
import { leftOf, limitLevel, share } from "./geometry"
import { volatilityText } from "./reading-card"
import { pillOf } from "./status-pill"
import { toneOf } from "./value-card"

// ExecPlan 0060 section 4.9: the Cockpit's pictures as numbers, and the page on the engine's own answers
// on the browser chain's scratch database (src/spot/samples: SYNTHETIC prices, the real engine). Lightweight
// Charts is a stand-in, as in spot-chart.test.
const chart = vi.hoisted(() => {
  const made: { options: object; setData: ReturnType<typeof vi.fn> }[] = []
  const timeScale = {
    fitContent: vi.fn(),
    getVisibleRange: vi.fn(() => null),
    setVisibleRange: vi.fn(),
  }
  const remove = vi.fn()
  return {
    made,
    remove,
    markers: { setMarkers: vi.fn(), detach: vi.fn() },
    createChart: vi.fn((_container: HTMLElement, _options: object) => ({
      addSeries: (_type: unknown, options: object) => {
        const series = {
          options,
          setData: vi.fn(),
          update: vi.fn(),
          applyOptions: vi.fn(),
        }
        made.push(series)
        return series
      },
      timeScale: () => timeScale,
      applyOptions: vi.fn(),
      remove,
    })),
  }
})

vi.mock("lightweight-charts", () => ({
  createChart: chart.createChart,
  createSeriesMarkers: vi.fn(() => chart.markers),
  BaselineSeries: {},
  CandlestickSeries: {},
}))

vi.mock(import("@tanstack/react-router"), async (original) => ({
  ...(await original()),
  Link: (({ children, ...props }: { children: ReactNode }) => (
    <a href="/" aria-label={(props as { "aria-label"?: string })["aria-label"]}>
      {children}
    </a>
  )) as never,
}))

vi.mock("@/spot/spot.functions", async (original) => ({
  ...(await original<typeof functions>()),
  getSpotOverview: vi.fn(),
}))

beforeEach(() => {
  // jsdom has no matchMedia; the sheets ask it whether the screen is a phone's.
  window.matchMedia = ((query: string) => ({
    matches: false,
    media: query,
    addEventListener: () => {},
    removeEventListener: () => {},
  })) as never
  window.localStorage.clear()
})

afterEach(() => {
  cleanup()
  chart.made.length = 0
  vi.clearAllMocks()
})

const overview = overviewSchema.parse(overviewSample)
const valuations = valuationsSchema.parse(valuationsSample)
const days = candlesSchema.parse(dayCandlesSample)

const workspace = {
  account: { initialized: true, reconciliation_failed: false } as Account,
  funding: [],
} as unknown as Workspace

function cockpit(
  answer: Overview = overview,
  fill: (client: QueryClient) => void = () => {},
  account: Workspace = workspace
) {
  const client = new QueryClient({
    defaultOptions: { queries: { enabled: false, retry: false } },
  })
  client.setQueryData(
    statusQueryOptions.queryKey,
    systemStatusSchema.parse(statusSample)
  )
  client.setQueryData(marketQuery.queryKey, marketSchema.parse(marketSample))
  client.setQueryData(spotOverviewQuery.queryKey, answer)
  client.setQueryData(spotValuationsQuery("all").queryKey, valuations)
  client.setQueryData(
    recentTradesQuery.queryKey,
    tradePageSchema.parse(tradesSample)
  )
  client.setQueryData(candlesQuery("1d").queryKey, days)
  client.setQueryData(
    spotMarkersQuery(days.candles[0].open_ms).queryKey,
    markersSchema.parse(markersSample)
  )
  fill(client)
  render(
    <QueryClientProvider client={client}>
      <CockpitPage workspace={account} stale={false} />
    </QueryClientProvider>
  )
  return client
}

function card(heading: string): HTMLElement {
  const found = screen
    .getByText(heading)
    .closest<HTMLElement>('[data-slot="card"]')
  if (found === null) throw new Error(`no card for ${heading}`)
  return found
}

describe("the Cockpit's drawings as numbers", () => {
  it("fills a limit calm under half, amber from half and red from 80%", () => {
    expect([0, 0.49, 0.5, 0.79, 0.8, 1].map(limitLevel)).toEqual([
      "calm",
      "calm",
      "warning",
      "warning",
      "danger",
      "danger",
    ])
    expect(share(0.031, 0.08)).toBeCloseTo(0.3875)
    expect(share(2, 1)).toBe(1)
    expect(share(1, 0)).toBeNull()
    expect(share(Number.NaN, 1)).toBeNull()
    expect(leftOf(0, 100, 25)).toBe(0.75)
    expect(leftOf(100, 0, 25)).toBe(0)
  })

  it("draws the curve from the valuations in time order and reads the axis from the base", () => {
    const points = equityPoints({
      ...valuations,
      points: [
        ...valuations.points,
        // A repeated second and an unreadable value are left out.
        { time: valuations.points[1].time, nav: "105", equity: "10500" },
        { time: "2026-11-12T13:40:00Z", nav: "x", equity: "1" },
      ],
    })
    expect(points.map((point) => point.value)).toEqual([100, 99.9826779736])
    expect(changeText(104.862, 100)).toBe("+4.86%")
    expect(changeText(99.9826779736, 100)).toBe("-0.02%")
    expect(changeText(1, 0)).toBe("Unknown")
    expect(equityText(points, 100)).toBe(
      "Equity curve, NAV per unit against the window's start: now -0.02%, lowest -0.02%."
    )
    expect(equityText([], 100)).toBe("No equity curve yet.")
  })

  it("colours a gain, a loss and nothing either way", () => {
    expect([
      toneOf("1.5"),
      toneOf("-0.2"),
      toneOf("0.00"),
      toneOf(null),
    ]).toEqual(["text-positive", "text-negative", "", ""])
    expect(volatilityText("0.322037586544998647")).toBe("32% a year")
    expect(volatilityText(null)).toBe("Unknown")
  })

  it("says the status in the pill: quiet when all is good, else what needs the owner", () => {
    const status = (
      state: TradingStatus["state"],
      kinds: ("action" | "problem" | "info")[] = []
    ): TradingStatus => ({
      state,
      title: state,
      notes: kinds.map((kind) => ({ kind, text: kind })),
    })
    expect(pillOf(status("trading"))).toMatchObject({
      text: "Trading · all good",
      quiet: true,
      tone: "ok",
    })
    expect(pillOf(status("trading", ["info"]))).toMatchObject({
      text: "Trading · 1 note",
      tone: "ok",
      quiet: false,
    })
    expect(pillOf(status("held", ["action", "info"]), "Paused")).toMatchObject({
      text: "On hold · 1 needs you",
      tone: "warning",
    })
    expect(pillOf(status("held", ["problem", "problem"]))).toMatchObject({
      text: "On hold · 2 problems",
    })
    expect(pillOf(status("stopped", ["action"]))).toMatchObject({
      text: "Not trading · 1 needs you",
      tone: "danger",
    })
    expect(pillOf(status("unknown", ["problem"])).text).toBe("Status unknown")
  })
})

describe("the Cockpit", () => {
  it("shows the value, the reading, the latest trades and the chart from the engine's answers", async () => {
    cockpit()
    expect(screen.getByRole("heading", { name: "Cockpit" })).toBeTruthy()
    expect(screen.getByText("Trading · all good")).toBeTruthy()

    const value = card("Account value")
    expect(within(value).getByText("9,998.27")).toBeTruthy()
    expect(within(value).getByText("-1.73 USDT")).toBeTruthy()
    // The return since the start (NAV 99.98) and today's change (from the day's reference) both round to it.
    expect(within(value).getAllByText("-0.02%")).toHaveLength(2)
    expect(within(value).getByText("9,488.71")).toBeTruthy()
    expect(within(value).getByText("0.00835 BTC")).toBeTruthy()
    expect(within(value).getByText("509.56 USDT")).toBeTruthy()
    expect(within(value).getByText("5.1%")).toBeTruthy()
    expect(
      within(value).getByRole("img", {
        name: "Fall from the run's high 0.01% of the 8% stop",
      })
    ).toBeTruthy()

    const reading = card("The rule's reading")
    expect(
      within(reading).getByText(
        "Trend up 2 of 3: hold 5.1% in Bitcoin; bought 0.00835 BTC"
      )
    ).toBeTruthy()
    expect(
      within(reading)
        .getAllByText(/^\d+ days$/)
        .map((badge) => [badge.textContent, badge.getAttribute("title")])
    ).toEqual([
      [
        "30 days",
        "The close was below the close of 2026-10-12, 62,220.37 USDT",
      ],
      [
        "91 days",
        "The close was above the close of 2026-08-12, 48,525.61 USDT",
      ],
      [
        "365 days",
        "The close was above the close of 2025-11-11, 28,060.78 USDT",
      ],
    ])
    expect(within(reading).getByText("32% a year")).toBeTruthy()
    expect(within(reading).getByText("60,726.19 USDT")).toBeTruthy()
    expect(
      within(reading).getByText("Done for today. Next reading at 00:05.")
    ).toBeTruthy()

    const trades = within(
      screen.getByRole("list", { name: "The newest 6 trades" })
    ).getAllByRole("listitem")
    expect(
      trades.map(
        (row) => row.querySelector("[data-slot=item-description]")?.textContent
      )
    ).toEqual([
      "At 61,037.41 · 509.66 USDT · fee 0.51 · Trend up 2 of 3: target 5.1%, held 0.0%",
      "At 61,025.20 · 509.56 USDT · fee 0.51 · Sold everything when the run stopped, by you",
      "At 61,037.41 · 509.66 USDT · fee 0.51 · Trend up 2 of 3: target 5.1%, held 0.0%",
    ])

    // The value's curve and Bitcoin's daily candles, each buy and sell marked.
    await waitFor(() => expect(chart.made).toHaveLength(2))
    await waitFor(() =>
      expect(chart.markers.setMarkers).toHaveBeenLastCalledWith([
        expect.objectContaining({ text: "Buy" }),
        expect.objectContaining({ text: "Sell" }),
        expect.objectContaining({ text: "Buy" }),
      ])
    )
    expect(
      screen.getByRole("img", { name: "Bitcoin spot 1d candlestick chart" })
    ).toBeTruthy()
  })

  it("keeps the chosen candle length for the next visit", () => {
    cockpit()
    fireEvent.click(screen.getByRole("button", { name: "1h" }))
    expect(window.localStorage.getItem("asl.cockpit.chart-interval")).toBe("1h")
  })

  it("sets the run against holding Bitcoin once it has two days, and nothing before", () => {
    // The browser chain's run is hours old: the engine answers no pair yet, and the card shows no line.
    cockpit()
    expect(overview.run?.since_start).toBeNull()
    expect(within(card("Account value")).queryByText(/^Since /)).toBeNull()
    cleanup()
    // ExecPlan 0061: a SYNTHETIC pair, as the engine's scratch-database test computes one (63,500 / 61,000 - 1).
    cockpit({
      ...overview,
      run: overview.run && {
        ...overview.run,
        since_start: {
          from_at: "2026-11-03T00:01:00Z",
          from_price: "61000",
          at: "2026-11-04T00:01:00Z",
          price: "63500",
          account: "-0.0012",
          bitcoin: "0.04098361",
        },
      },
    })
    const value = card("Account value")
    expect(within(value).getByText("Since 3 Nov")).toBeTruthy()
    const run = within(value).getByRole("button", {
      name: "Run #2's value per unit from 3 Nov, 00:01 to 4 Nov, 00:01, after fees; a top-up is not a gain",
    })
    expect(run.textContent).toBe("-0.12%")
    expect(run.className).toContain(toneOf("-0.0012"))
    const bitcoin = within(value).getByRole("button", {
      name: "Holding Bitcoin over the same days: its daily close went from 61,000.00 to 63,500.00 USDT",
    })
    expect(bitcoin.textContent).toBe("+4.10%")
    expect(bitcoin.className).toContain(toneOf("0.04098361"))
  })

  it("says what holds the run, and where to act, when it is stopped", () => {
    cockpit({
      ...overview,
      run: overview.run && {
        ...overview.run,
        state: "STOPPED",
        stop_reason: "DRAWDOWN",
        stopped_at: "2026-11-12T13:40:00Z",
      },
      today: overview.today && {
        ...overview.today,
        status: "NONE",
        next_reading_at: null,
      },
    })
    expect(screen.getByText("Not trading · 1 needs you")).toBeTruthy()
    expect(
      screen.getByText("No reading while the run is stopping or stopped.")
    ).toBeTruthy()
  })

  it("shows each state of the account without guessing", async () => {
    cockpit(overview, () => {}, {
      account: { initialized: false },
      funding: [],
    } as unknown as Workspace)
    expect(screen.getByText("No account yet")).toBeTruthy()
    cleanup()

    cockpit({ ...overview, state: "SCHEMA_PENDING" })
    expect(screen.getByText("The database is being updated")).toBeTruthy()
    cleanup()

    // The overview's read fails: the page says so and offers to read again; nothing is shown as known.
    vi.mocked(functions.getSpotOverview).mockRejectedValue(new Error("down"))
    cockpit(overview, (client) => {
      client.removeQueries({ queryKey: spotOverviewQuery.queryKey })
      client.setQueryDefaults([SPOT_KEY, "overview"], { enabled: true })
    })
    expect(await screen.findByText("Couldn't load the account")).toBeTruthy()
    expect(screen.getByRole("button", { name: "Retry" })).toBeTruthy()
    expect(screen.queryByText("Account value")).toBeNull()
  })
})
