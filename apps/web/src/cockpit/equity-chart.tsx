import { useEffect, useRef, useState } from "react"
import type {
  BaselineData,
  IChartApi,
  ISeriesApi,
  UTCTimestamp,
} from "lightweight-charts"
import { useTimeZone } from "@/components/time-zone-provider"
import { chartColors, useDarkTheme } from "@/lib/chart-theme"
import { chartTime } from "@/lib/chart-time"
import { formatPercent } from "@/lib/display"
import type { Valuations } from "@/spot/schemas"

// The Cockpit's value curve (ExecPlan 0048 section 4.2): NAV per unit, so a top-up is not a gain,
// as a Lightweight Charts baseline series at the window's first NAV. Above it the line is the library's
// rising colour, under it its falling colour, and the price axis reads in percent from that start.

export type EquityPoint = BaselineData<UTCTimestamp>

/**
 * The curve's points: one per valuation the engine sent, in time order with no repeated second (the
 * library drops or refuses those). A value that is not a finite number is left out, not guessed.
 */
export function equityPoints(valuations: Valuations): EquityPoint[] {
  const points: EquityPoint[] = []
  let previous = -Infinity
  for (const point of valuations.points) {
    const ms = Date.parse(point.time)
    const value = Number(point.nav)
    if (!Number.isFinite(ms) || !Number.isFinite(value)) continue
    const time = Math.floor(ms / 1000)
    if (time <= previous) continue
    points.push({ time: time as UTCTimestamp, value })
    previous = time
  }
  return points
}

/** A NAV as its change from the base, for the axis and the crosshair: +4.86%. */
export function changeText(value: number, base: number): string {
  if (!Number.isFinite(value) || !Number.isFinite(base) || base <= 0)
    return "Unknown"
  return formatPercent((value / base - 1).toFixed(6), {
    decimals: 2,
    signed: true,
  })
}

function priceFormat(base: number) {
  return {
    type: "custom" as const,
    minMove: 0.0001,
    formatter: (value: number) => changeText(value, base),
  }
}

/** What the curve shows, for a reader who cannot see the canvas. */
export function equityText(points: EquityPoint[], base: number): string {
  if (points.length === 0) return "No equity curve yet."
  const last = points[points.length - 1].value
  const low = Math.min(...points.map((point) => point.value))
  return `Equity curve, NAV per unit against the window's start: now ${changeText(last, base)}, lowest ${changeText(low, base)}.`
}

export function EquityChart({
  valuations,
  className,
}: {
  valuations: Valuations
  className?: string
}) {
  const zone = useTimeZone()
  const dark = useDarkTheme()
  const base = Number(valuations.base_nav)
  const points = equityPoints(valuations)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<"Baseline"> | null>(null)
  const latestRef = useRef({ points, base, zone, dark })
  const [failed, setFailed] = useState(false)
  const signature = points
    .map((point) => `${point.time}:${point.value}`)
    .join("|")

  useEffect(() => {
    latestRef.current = { points, base, zone, dark }
  })

  useEffect(() => {
    chartRef.current?.applyOptions(chartTime(zone))
  }, [zone])

  useEffect(() => {
    chartRef.current?.applyOptions(chartColors(dark))
  }, [dark])

  // Created once; the data and the base follow below.
  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let active = true
    let chart: IChartApi | null = null
    void import("lightweight-charts")
      .then(({ createChart, BaselineSeries }) => {
        if (!active) return
        const latest = latestRef.current
        const time = chartTime(latest.zone)
        chart = createChart(container, {
          autoSize: true,
          ...chartColors(latest.dark),
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            ...time.timeScale,
          },
          localization: time.localization,
          handleScroll: false,
          handleScale: false,
        })
        const series = chart.addSeries(BaselineSeries, {
          baseValue: { type: "price", price: latest.base },
          priceFormat: priceFormat(latest.base),
        })
        series.setData(latest.points)
        chart.timeScale().fitContent()
        chartRef.current = chart
        seriesRef.current = series
      })
      .catch((error: unknown) => {
        console.error("Equity chart initialization failed", error)
        if (active) setFailed(true)
      })
    return () => {
      active = false
      chartRef.current = null
      seriesRef.current = null
      chart?.remove()
    }
  }, [])

  useEffect(() => {
    const series = seriesRef.current
    if (!series) return
    const latest = latestRef.current
    series.applyOptions({
      baseValue: { type: "price", price: latest.base },
      priceFormat: priceFormat(latest.base),
    })
    series.setData(latest.points)
    chartRef.current?.timeScale().fitContent()
  }, [signature, base])

  return (
    <div className={className}>
      <div
        ref={containerRef}
        role="img"
        aria-label={equityText(points, base)}
        className="size-full"
      />
      {failed && (
        <p className="px-4 text-sm text-destructive">Chart unavailable.</p>
      )}
    </div>
  )
}
