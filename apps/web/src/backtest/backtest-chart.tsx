import { useEffect, useRef, useState } from "react"
import type {
  IChartApi,
  ISeriesApi,
  ISeriesMarkersPluginApi,
  LineData,
  SeriesMarker,
  Time,
  TickMarkType,
  UTCTimestamp,
} from "lightweight-charts"
import { chartColors, useDarkTheme } from "@/lib/chart-theme"
import { formatAxisTime, formatDate, formatFixed } from "@/lib/display"
import type { BacktestSeries } from "@/spot/schemas"

// The backtest's chart (ExecPlan 0060 section 4.6): the rule's value and holding Bitcoin's, day by day
// from the same 10,000 USDT, on one logarithmic scale so both read at any size; the rule's buys and
// sells are marked on its line. The days are UTC days, so the axis and the crosshair write them in UTC.

// Lightweight Charts' default line colour for the rule, an orange for Bitcoin held, and its own rising
// and falling colours for the marks.
export const RULE_COLOR = "#2962FF"
export const HOLD_COLOR = "#FF9800"
const UP = "#26a69a"
const DOWN = "#ef5350"

const TICK_PARTS = ["year", "month", "day", "minute", "second"] as const

function dayLabel(time: Time): string {
  if (typeof time === "number") return formatDate(time * 1000, "UTC")
  if (typeof time === "string") return formatDate(`${time}T00:00:00Z`, "UTC")
  return formatDate(Date.UTC(time.year, time.month - 1, time.day), "UTC")
}

const DAY_TIME = {
  timeScale: {
    timeVisible: false,
    // Since 2019 is about 2,900 days: the default minimum of half a pixel a day would leave the earliest years
    // outside the chart on a laptop's width, so the whole window fits.
    minBarSpacing: 0.05,
    tickMarkFormatter: (time: Time, type: TickMarkType) =>
      typeof time === "number"
        ? formatAxisTime(time * 1000, "UTC", TICK_PARTS[type])
        : null,
  },
  localization: { timeFormatter: dayLabel },
}

const PRICE_FORMAT = {
  type: "custom" as const,
  minMove: 0.01,
  formatter: (value: number) => formatFixed(value, 0),
}

/** A series' points: one per day with a finite value, in time order. */
export function linePoints(
  days: number[],
  values: string[]
): LineData<UTCTimestamp>[] {
  const points: LineData<UTCTimestamp>[] = []
  let previous = -Infinity
  days.forEach((day, index) => {
    const value = Number(values[index])
    const time = Math.floor(day / 1000)
    if (!Number.isFinite(value) || value <= 0 || time <= previous) return
    points.push({ time: time as UTCTimestamp, value })
    previous = time
  })
  return points
}

/**
 * The rule's trades on its line: an arrow under it for a buy, over it for a sell. The engine dates a
 * rule's trade by the close it traded at, the day before its reading; the window's first reading trades
 * at the close of the day before the window, so that trade is marked on the window's first day.
 */
export function tradeMarkers(
  series: BacktestSeries
): SeriesMarker<UTCTimestamp>[] {
  const days = new Set(series.days.map((day) => Math.floor(day / 1000)))
  const first = series.days.length > 0 ? Math.floor(series.days[0] / 1000) : 0
  return series.trades
    .map((trade) => {
      const buy = trade.side === "BUY"
      return {
        time: Math.max(first, Math.floor(trade.day_ms / 1000)) as UTCTimestamp,
        position: buy ? ("belowBar" as const) : ("aboveBar" as const),
        shape: buy ? ("arrowUp" as const) : ("arrowDown" as const),
        color: buy ? UP : DOWN,
        size: 0.6,
      }
    })
    .filter((marker) => days.has(marker.time))
    .sort((a, b) => a.time - b.time)
}

/** What the chart shows, for a reader who cannot see the canvas. */
export function backtestText(series: BacktestSeries): string {
  const last = series.days.length - 1
  if (last < 0) return "No backtest values."
  const marked = tradeMarkers(series)
  const buys = marked.filter((marker) => marker.shape === "arrowUp").length
  const sells = marked.length - buys
  return `The rule's value and holding Bitcoin's, day by day, from ${dayLabel(Math.floor(series.days[0] / 1000) as UTCTimestamp)} to ${dayLabel(Math.floor(series.days[last] / 1000) as UTCTimestamp)}: the rule ends at ${formatFixed(Number(series.rule[last]), 0)} USDT, holding at ${formatFixed(Number(series.hold[last]), 0)} USDT; ${buys} buys and ${sells} sells marked.`
}

export function BacktestChart({
  series,
  className,
}: {
  series: BacktestSeries
  className?: string
}) {
  const dark = useDarkTheme()
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const ruleRef = useRef<ISeriesApi<"Line"> | null>(null)
  const holdRef = useRef<ISeriesApi<"Line"> | null>(null)
  const markersRef = useRef<ISeriesMarkersPluginApi<Time> | null>(null)
  const latestRef = useRef({ series, dark })
  const [failed, setFailed] = useState(false)
  const signature = `${series.days.length}:${series.days[0] ?? ""}:${series.days.at(-1) ?? ""}:${series.rule.at(-1) ?? ""}:${series.trades.length}`

  useEffect(() => {
    latestRef.current = { series, dark }
  })

  useEffect(() => {
    chartRef.current?.applyOptions(chartColors(dark))
  }, [dark])

  // Created once; the data follow below.
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let active = true
    let chart: IChartApi | null = null
    void import("lightweight-charts")
      .then(
        ({ createChart, createSeriesMarkers, LineSeries, PriceScaleMode }) => {
          if (!active) return
          const latest = latestRef.current
          chart = createChart(container, {
            autoSize: true,
            ...chartColors(latest.dark),
            ...DAY_TIME,
            rightPriceScale: { mode: PriceScaleMode.Logarithmic },
          })
          const hold = chart.addSeries(LineSeries, {
            color: HOLD_COLOR,
            lineWidth: 2,
            priceFormat: PRICE_FORMAT,
            title: "Holding",
          })
          const rule = chart.addSeries(LineSeries, {
            color: RULE_COLOR,
            lineWidth: 2,
            priceFormat: PRICE_FORMAT,
            title: "Rule",
          })
          hold.setData(linePoints(latest.series.days, latest.series.hold))
          rule.setData(linePoints(latest.series.days, latest.series.rule))
          markersRef.current = createSeriesMarkers(
            rule,
            tradeMarkers(latest.series)
          )
          chart.timeScale().fitContent()
          chartRef.current = chart
          ruleRef.current = rule
          holdRef.current = hold
        }
      )
      .catch((error: unknown) => {
        console.error("Backtest chart initialization failed", error)
        if (active) setFailed(true)
      })
    return () => {
      active = false
      markersRef.current?.detach()
      markersRef.current = null
      chartRef.current = null
      ruleRef.current = null
      holdRef.current = null
      chart?.remove()
    }
  }, [])

  useEffect(() => {
    const rule = ruleRef.current
    const hold = holdRef.current
    if (!rule || !hold) return
    const latest = latestRef.current.series
    hold.setData(linePoints(latest.days, latest.hold))
    rule.setData(linePoints(latest.days, latest.rule))
    markersRef.current?.setMarkers(tradeMarkers(latest))
    chartRef.current?.timeScale().fitContent()
  }, [signature])

  return (
    <div className={className}>
      <div
        ref={containerRef}
        role="img"
        aria-label={backtestText(series)}
        className="size-full"
      />
      {failed && (
        <p className="px-4 text-sm text-destructive">Chart unavailable.</p>
      )}
    </div>
  )
}
