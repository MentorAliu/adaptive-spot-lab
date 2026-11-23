import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"
import backtestSample from "@/spot/samples/backtest.json"
import { backtestQuery } from "@/spot/spot.query"
import { backtestSchema } from "@/spot/schemas"
import type { Backtest, BacktestSeries } from "@/spot/schemas"
import { backtestText, linePoints, tradeMarkers } from "./backtest-chart"
import { BacktestPage, yearRows } from "./backtest-page"

// ExecPlan 0060 sections 4.6 and 4.9: the Backtest page on the engine's own answer for the last 12
// months, worked out on the browser chain's scratch database from SYNTHETIC daily candles (src/spot/
// samples/backtest.json). Lightweight Charts is a stand-in: jsdom draws no canvas.
const chart = vi.hoisted(() => {
  const made: { options: object; setData: ReturnType<typeof vi.fn> }[] = []
  const markers = { setMarkers: vi.fn(), detach: vi.fn() }
  const timeScale = { fitContent: vi.fn() }
  const remove = vi.fn()
  return {
    made,
    markers,
    remove,
    createChart: vi.fn((_container: HTMLElement, _options: object) => ({
      addSeries: (_type: unknown, options: object) => {
        const series = { options, setData: vi.fn(), applyOptions: vi.fn() }
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
  LineSeries: {},
  PriceScaleMode: { Normal: 0, Logarithmic: 1 },
}))

const navigate = vi.hoisted(() => vi.fn())
vi.mock(import("@tanstack/react-router"), async (original) => ({
  ...(await original()),
  useNavigate: (() => navigate) as never,
}))

afterEach(() => {
  cleanup()
  chart.made.length = 0
  vi.clearAllMocks()
})

const backtest = backtestSchema.parse(backtestSample)
const series = backtest.series as BacktestSeries
const DAY = 86_400_000

function page(answer: Backtest) {
  const client = new QueryClient({
    defaultOptions: { queries: { enabled: false, retry: false } },
  })
  client.setQueryData(backtestQuery(answer.window).queryKey, answer)
  render(
    <QueryClientProvider client={client}>
      <BacktestPage
        search={answer.window === "SINCE_2019" ? {} : { window: answer.window }}
      />
    </QueryClientProvider>
  )
}

function card(heading: string): HTMLElement {
  const found = screen
    .getByRole("heading", { name: heading })
    .closest<HTMLElement>('[data-slot="card"]')
  if (found === null) throw new Error(`no card for ${heading}`)
  return found
}

function factOf(scope: HTMLElement, label: string): string[] {
  const term = within(scope).getByText(label, { selector: "dt" })
  const values: string[] = []
  let next = term.nextElementSibling
  while (next !== null && next.tagName === "DD") {
    values.push(next.textContent)
    next = next.nextElementSibling
  }
  return values
}

describe("the backtest's chart as numbers", () => {
  it("draws a point per day with a value, in time order", () => {
    expect(
      linePoints(
        [2 * DAY, DAY, 3 * DAY, 4 * DAY, 5 * DAY],
        ["10", "9", "x", "0", "12.5"]
      )
    ).toEqual([
      { time: 172800, value: 10 },
      { time: 432000, value: 12.5 },
    ])
    expect(linePoints(series.days, series.rule)).toHaveLength(365)
  })

  it("marks every trade of the window on the rule's line, the first reading's on the first day", () => {
    const marks = tradeMarkers(series)
    // The engine counts 12 buys and 14 sells in this window: every one is marked.
    expect(marks).toHaveLength(26)
    expect(marks.filter((mark) => mark.shape === "arrowUp")).toHaveLength(12)
    expect(marks[0]).toMatchObject({
      time: series.days[0] / 1000,
      position: "belowBar",
      shape: "arrowUp",
    })
    expect(
      marks.every((mark, n) => n === 0 || mark.time >= marks[n - 1].time)
    ).toBe(true)
    expect(backtestText(series)).toBe(
      "The rule's value and holding Bitcoin's, day by day, from 12 Nov 2025 to 11 Nov 2026: the rule ends at 11,179 USDT, holding at 21,617 USDT; 12 buys and 14 sells marked."
    )
    expect(backtestText({ ...series, days: [], rule: [], hold: [] })).toBe(
      "No backtest values."
    )
  })

  it("puts each year's returns side by side, newest first", () => {
    const result = backtest.computed?.windows.find(
      (item) => item.key === "LAST_12_MONTHS"
    )
    expect(result && yearRows(result)).toEqual([
      { year: 2026, rule: "0.11994730", hold: "1.03747654" },
      { year: 2025, rule: "-0.00179451", hold: "0.06096521" },
    ])
    expect(
      result &&
        yearRows({
          ...result,
          rule: { ...result.rule, years: [] },
        })
    ).toEqual([
      { year: 2026, rule: null, hold: "1.03747654" },
      { year: 2025, rule: null, hold: "0.06096521" },
    ])
  })
})

describe("the Backtest page", () => {
  it("shows the rule beside holding Bitcoin, the chart and each year", async () => {
    page(backtest)
    expect(
      screen
        .getAllByRole("tab")
        .map((tab) => [tab.textContent, tab.getAttribute("aria-selected")])
    ).toEqual([
      ["Since 2019", "false"],
      ["Since 2023", "false"],
      ["Last 12 months", "true"],
    ])
    expect(
      screen.getByText(
        /^From 10,000\.00 USDT on 12 Nov 2025 to 11 Nov 2026 \(365 days\)\. Each day the rule reads the day before/
      )
    ).toBeTruthy()
    const rule = card("The rule")
    expect(within(rule).getByText("11,179.38")).toBeTruthy()
    expect(factOf(rule, "Return")).toEqual(["+11.79%"])
    expect(factOf(rule, "Worst fall")).toEqual(["1.55%", "to 19 Jan 2026"])
    expect(factOf(rule, "Fees")).toEqual(["24.74 USDT"])
    expect(factOf(rule, "Trades")).toEqual(["12 buys, 14 sells"])
    expect(factOf(rule, "Days in Bitcoin")).toEqual(["100.0%"])
    expect(factOf(rule, "Share held")).toEqual([
      "11.8% on average",
      "at most 19.1%",
    ])
    const hold = card("Holding Bitcoin")
    expect(within(hold).getByText("21,616.92")).toBeTruthy()
    expect(factOf(hold, "Return")).toEqual(["+116.17%"])
    expect(screen.queryByText(/would have stopped/)).toBeNull()
    const rows = within(
      screen.getByRole("table", {
        name: "The return of each year, the rule beside holding Bitcoin",
      })
    ).getAllByRole("row")
    expect(rows.map((row) => row.textContent)).toEqual([
      "YearThe ruleHolding Bitcoin",
      "2026+11.99%+103.75%",
      "2025-0.18%+6.10%",
    ])
    expect(
      screen.getByText(
        /^Binance's daily Bitcoin candles from 17 Aug 2017 to 11 Nov 2026: 3,374 days\. Worked out/
      )
    ).toBeTruthy()
    // Both lines on one logarithmic scale, the rule's trades marked on its own line.
    await waitFor(() => expect(chart.made).toHaveLength(2))
    expect(chart.createChart.mock.calls[0][1]).toMatchObject({
      rightPriceScale: { mode: 1 },
    })
    expect(chart.markers.setMarkers).not.toHaveBeenCalled()
    expect(screen.getByRole("img").getAttribute("aria-label")).toBe(
      backtestText(series)
    )
  })

  it("moves to another window through the address, keeping the default out of it", () => {
    page(backtest)
    fireEvent.click(screen.getByRole("tab", { name: "Since 2023" }))
    expect(navigate).toHaveBeenLastCalledWith({
      search: { window: "SINCE_2023" },
      resetScroll: false,
    })
    fireEvent.click(screen.getByRole("tab", { name: "Since 2019" }))
    expect(navigate).toHaveBeenLastCalledWith({
      search: {},
      resetScroll: false,
    })
  })

  it("says where the run would have stopped", () => {
    const computed = backtest.computed
    if (computed === null) throw new Error("no computed sample")
    page({
      ...backtest,
      computed: {
        ...computed,
        windows: computed.windows.map((item) =>
          item.key === "LAST_12_MONTHS"
            ? {
                ...item,
                rule: {
                  ...item.rule,
                  stopped: { day: "2026-01-19", price: "91234.5" },
                },
              }
            : item
        ),
      },
    })
    expect(
      screen.getByText("The run would have stopped here: 19 Jan 2026")
    ).toBeTruthy()
    expect(
      screen.getByText(
        "The account fell to the drawdown stop below its high, sold everything at 91,234.50 USDT and held USDT for the rest of the window."
      )
    ).toBeTruthy()
  })

  it("says while the engine works it out, while the database updates and when a window has no result", () => {
    page({ ...backtest, state: "NOT_COMPUTED", computed: null, series: null })
    expect(screen.getByText("Working out the backtest")).toBeTruthy()
    expect(screen.getByText("Checks again every 10 seconds")).toBeTruthy()
    cleanup()
    page({ ...backtest, state: "SCHEMA_PENDING", computed: null, series: null })
    expect(screen.getByText("The database is being updated")).toBeTruthy()
    cleanup()
    const computed = backtest.computed
    if (computed === null) throw new Error("no computed sample")
    page({
      ...backtest,
      computed: {
        ...computed,
        windows: computed.windows.filter(
          (item) => item.key !== "LAST_12_MONTHS"
        ),
      },
    })
    expect(screen.getByText("No result for this window")).toBeTruthy()
  })
})
