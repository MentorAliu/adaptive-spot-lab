import { afterEach, expect, it, vi } from "vitest"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import { chartColors } from "@/lib/chart-theme"
import hourCandlesSample from "./samples/candles-1h.json"
import markersSample from "./samples/markers.json"
import { SpotChart, fillMarkers, markersText, spotBars } from "./spot-chart"
import { candlesSchema, markersSchema } from "./schemas"
import type { Candle, Markers } from "./schemas"

// ExecPlan 0060 section 4.9: Bitcoin's spot chart with the account's buys and sells, after the futures
// chart's test (ExecPlan 0039). The candles and marks are the engine's answers on the browser chain's
// scratch database (src/spot/samples); the single candles below are SYNTHETIC. Lightweight Charts is
// replaced by a stand-in: jsdom draws no canvas.
const chart = vi.hoisted(() => {
  const series = {
    setData: vi.fn(),
    update: vi.fn(),
    applyOptions: vi.fn(),
  }
  const markers = { setMarkers: vi.fn(), detach: vi.fn() }
  const timeScale = {
    fitContent: vi.fn(),
    getVisibleRange: vi.fn(() => ({ from: 60, to: 240 })),
    setVisibleRange: vi.fn(),
  }
  const remove = vi.fn()
  const applyOptions = vi.fn()
  return {
    series,
    markers,
    timeScale,
    remove,
    applyOptions,
    createChart: vi.fn((_container: HTMLElement, _options: object) => ({
      addSeries: () => series,
      timeScale: () => timeScale,
      applyOptions,
      remove,
    })),
  }
})

vi.mock("lightweight-charts", () => ({
  createChart: chart.createChart,
  createSeriesMarkers: vi.fn(() => chart.markers),
  CandlestickSeries: {},
}))

function candle(openMs: number, close = "60000.5", complete = true): Candle {
  return {
    open_ms: openMs,
    open: "60000",
    high: "60010",
    low: "59990",
    close,
    volume: "12.5",
    minutes: complete ? 60 : 30,
    expected_minutes: 60,
    complete,
  }
}

const HOUR = 3_600_000
const hours = candlesSchema.parse(hourCandlesSample).candles
const fills = markersSchema.parse(markersSample)

afterEach(() => {
  cleanup()
  document.documentElement.className = ""
  vi.restoreAllMocks()
  vi.clearAllMocks()
})

it("draws a missing interval as whitespace and an incomplete candle grey", () => {
  const bars = spotBars(
    [candle(HOUR), candle(4 * HOUR, "60001", false), candle(2 * HOUR)],
    "1h",
    "grey"
  )
  expect(bars.map((bar) => bar.time)).toEqual([3600, 7200, 10800, 14400])
  expect(bars[2]).toEqual({ time: 10800 })
  expect(bars[3]).toMatchObject({
    close: 60001,
    color: "grey",
    wickColor: "grey",
  })
  expect(bars[0]).not.toHaveProperty("color")
  // A candle off the interval's grid, a repeated one and an unreadable one are left out.
  expect(
    spotBars(
      [
        candle(HOUR),
        candle(HOUR + 60_000),
        candle(HOUR),
        candle(2 * HOUR, "x"),
      ],
      "1h",
      "grey"
    )
  ).toHaveLength(1)
  // The engine's hourly candles draw one bar each, the newest still open.
  const drawn = spotBars(hours, "1h", "grey")
  expect(drawn.length).toBeGreaterThanOrEqual(hours.length)
  expect(drawn.at(-1)).toMatchObject({ color: "grey" })
})

it("marks each buy under its bar and each sell over it, and leaves out a fill with no bar", () => {
  const bars = spotBars(hours, "1h", "grey")
  const marks = fillMarkers(fills, bars, "1h")
  expect(marks.map((mark) => [mark.text, mark.position, mark.shape])).toEqual([
    ["Buy", "belowBar", "arrowUp"],
    ["Sell", "aboveBar", "arrowDown"],
    ["Buy", "belowBar", "arrowUp"],
  ])
  // Each fill sits on the hour it was made in.
  const hour = Math.floor(Date.parse(fills.fills[0].filled_at) / HOUR) * 3600
  expect(marks.map((mark) => mark.time)).toEqual([hour, hour, hour])
  const early: Markers = {
    ...fills,
    fills: [{ ...fills.fills[0], filled_at: "2020-01-01T00:00:00Z" }],
  }
  expect(fillMarkers(early, bars, "1h")).toEqual([])
  expect(fillMarkers(null, bars, "1h")).toEqual([])
  expect(markersText(fills)).toBe("Marked: 2 buys and 1 sell.")
})

it("updates only the newest candle as it changes and removes the chart when it goes", async () => {
  const first = [candle(HOUR), candle(2 * HOUR, "60001", false)]
  const view = render(<SpotChart interval="1h" candles={first} />)
  await waitFor(() => expect(chart.series.setData).toHaveBeenCalledTimes(1))
  expect(screen.queryByText("Loading the Bitcoin chart…")).toBeNull()
  view.rerender(
    <SpotChart
      interval="1h"
      candles={[candle(HOUR), candle(2 * HOUR, "60002", false)]}
    />
  )
  await waitFor(() => expect(chart.series.update).toHaveBeenCalledTimes(1))
  expect(chart.series.update).toHaveBeenCalledWith(
    expect.objectContaining({ time: 7200, close: 60002 })
  )
  expect(chart.series.setData).toHaveBeenCalledTimes(1)
  view.unmount()
  expect(chart.remove).toHaveBeenCalledTimes(1)
  expect(chart.markers.detach).toHaveBeenCalledTimes(1)
})

it("paints the marks, tells them in words and replaces them when they change", async () => {
  const view = render(
    <SpotChart interval="1h" candles={hours} overlay={fills} />
  )
  await waitFor(() =>
    expect(chart.markers.setMarkers).toHaveBeenLastCalledWith(
      expect.arrayContaining([expect.objectContaining({ text: "Sell" })])
    )
  )
  expect(screen.getByText("Marked: 2 buys and 1 sell.")).toBeTruthy()
  // The newest candle leaves room on the right for its marks' words.
  expect(chart.createChart.mock.calls[0][1]).toMatchObject({
    timeScale: { rightOffsetPixels: 28 },
  })
  view.rerender(
    <SpotChart
      interval="1h"
      candles={hours}
      overlay={{ ...fills, fills: fills.fills.slice(0, 1) }}
    />
  )
  await waitFor(() =>
    expect(chart.markers.setMarkers).toHaveBeenLastCalledWith([
      expect.objectContaining({ text: "Buy" }),
    ])
  )
})

it("draws in the theme's colours and repaints the backdrop alone when the theme switches", async () => {
  document.documentElement.classList.add("dark")
  render(<SpotChart interval="1h" candles={[candle(HOUR)]} />)
  await waitFor(() => expect(chart.series.setData).toHaveBeenCalledTimes(1))
  expect(chart.createChart.mock.calls[0][1]).toMatchObject(chartColors(true))

  document.documentElement.classList.remove("dark")
  await waitFor(() =>
    expect(chart.applyOptions).toHaveBeenCalledWith(chartColors(false))
  )
  expect(chart.series.applyOptions).not.toHaveBeenCalled()
  expect(chart.series.setData).toHaveBeenCalledTimes(1)
})
