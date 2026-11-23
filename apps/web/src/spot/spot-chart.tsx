import { useEffect, useId, useMemo, useRef, useState } from "react"
import type {
  CandlestickData,
  IChartApi,
  ISeriesApi,
  ISeriesMarkersPluginApi,
  SeriesMarker,
  Time,
  UTCTimestamp,
  WhitespaceData,
} from "lightweight-charts"
import { useTimeZone } from "@/components/time-zone-provider"
import { cn } from "@/lib/utils"
import { chartColors, useDarkTheme } from "@/lib/chart-theme"
import { chartTime } from "@/lib/chart-time"
import { formatFixed, pricePlaces } from "@/lib/display"
import { INTERVAL_MS } from "./schemas"
import type { Candle, Interval, Markers } from "./schemas"

// Bitcoin's spot chart (ExecPlan 0060 section 4.9, after the futures chart of ExecPlan 0039): the
// stored candles of the chosen interval, with each buy and sell of the account marked on its bar.

export type SpotBar =
  CandlestickData<UTCTimestamp> | WhitespaceData<UTCTimestamp>

// Lightweight Charts' own rising and falling candle colours, for the markers, which must name one.
const UP = "#26a69a"
const DOWN = "#ef5350"
// A candle that is not complete is grey, so it does not read as a finished one.
const PROVISIONAL = "#9e9e9e"

function priceFormat(places: number) {
  return {
    type: "custom" as const,
    minMove: 10 ** -places,
    formatter: (price: number) => formatFixed(price, places),
  }
}

/**
 * The chart's bars: one a candle, a time without a candle as whitespace, and a candle that is not
 * complete (still open, or missing a minute) in the provisional colour.
 */
export function spotBars(
  candles: Candle[],
  interval: Interval,
  provisionalColor: string
): SpotBar[] {
  const step = INTERVAL_MS[interval]
  const bars: SpotBar[] = []
  let previous: number | null = null
  for (const candle of [...candles].sort((a, b) => a.open_ms - b.open_ms)) {
    if (candle.open_ms % step !== 0) continue
    if (previous !== null && candle.open_ms <= previous) continue
    const values = [candle.open, candle.high, candle.low, candle.close].map(
      Number
    )
    if (values.some((value) => !Number.isFinite(value) || value <= 0)) continue
    if (previous !== null)
      for (let gap = previous + step; gap < candle.open_ms; gap += step)
        bars.push({ time: (gap / 1000) as UTCTimestamp })
    bars.push({
      time: (candle.open_ms / 1000) as UTCTimestamp,
      open: values[0],
      high: values[1],
      low: values[2],
      close: values[3],
      ...(candle.complete
        ? {}
        : {
            color: provisionalColor,
            borderColor: provisionalColor,
            wickColor: provisionalColor,
          }),
    })
    previous = candle.open_ms
  }
  return bars
}

/**
 * One marker per fill, on the bar it fell in: an arrow under the bar for a buy and over it for a sell.
 * A fill outside the drawn bars has no bar to sit on and is left out (the chart would drop it silently).
 */
export function fillMarkers(
  markers: Markers | null,
  bars: SpotBar[],
  interval: Interval
): SeriesMarker<UTCTimestamp>[] {
  if (!markers) return []
  const step = INTERVAL_MS[interval]
  const times = new Set(bars.map((bar) => bar.time))
  const marks: SeriesMarker<UTCTimestamp>[] = []
  for (const fill of markers.fills) {
    const filled = Date.parse(fill.filled_at)
    if (!Number.isFinite(filled)) continue
    const time = ((filled - (filled % step)) / 1000) as UTCTimestamp
    if (!times.has(time)) continue
    const buy = fill.side === "BUY"
    marks.push({
      id: fill.id,
      time,
      position: buy ? "belowBar" : "aboveBar",
      shape: buy ? "arrowUp" : "arrowDown",
      color: buy ? UP : DOWN,
      text: buy ? "Buy" : "Sell",
    })
  }
  return marks.sort((a, b) => a.time - b.time)
}

/** What the marks say, for a reader who cannot see the canvas. */
export function markersText(markers: Markers): string {
  const buys = markers.fills.filter((fill) => fill.side === "BUY").length
  const sells = markers.fills.length - buys
  return `Marked: ${buys} ${buys === 1 ? "buy" : "buys"} and ${sells} ${sells === 1 ? "sell" : "sells"}.`
}

function signature(candles: Candle[]): string {
  return candles
    .map(
      (item) =>
        `${item.open_ms}:${item.open}:${item.high}:${item.low}:${item.close}:${item.minutes}:${item.complete}`
    )
    .join("|")
}

export function SpotChart({
  interval,
  candles,
  overlay = null,
  height = "h-85",
}: {
  interval: Interval
  candles: Candle[]
  overlay?: Markers | null
  height?: "h-96" | "h-85" | "h-64"
}) {
  const zone = useTimeZone()
  const dark = useDarkTheme()
  const places = useMemo(
    () =>
      Math.min(8, Math.max(2, ...candles.map((bar) => pricePlaces(bar.close)))),
    [candles]
  )
  const containerRef = useRef<HTMLDivElement | null>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null)
  const markersRef = useRef<ISeriesMarkersPluginApi<Time> | null>(null)
  const latestRef = useRef({ candles, zone, places, overlay, dark })
  const previousRef = useRef<{ signature: string; bars: SpotBar[] } | null>(
    null
  )
  const [ready, setReady] = useState(false)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    latestRef.current = { candles, zone, places, overlay, dark }
  }, [candles, zone, places, overlay, dark])

  useEffect(() => {
    chartRef.current?.applyOptions(chartTime(zone))
  }, [zone])

  useEffect(() => {
    chartRef.current?.applyOptions(chartColors(dark))
  }, [dark])

  useEffect(() => {
    seriesRef.current?.applyOptions({ priceFormat: priceFormat(places) })
  }, [places])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let active = true
    let chart: IChartApi | null = null
    void import("lightweight-charts")
      .then(({ createChart, createSeriesMarkers, CandlestickSeries }) => {
        if (!active) return
        const time = chartTime(latestRef.current.zone)
        chart = createChart(container, {
          autoSize: true,
          ...chartColors(latestRef.current.dark),
          timeScale: {
            timeVisible: true,
            secondsVisible: false,
            // Room on the right for the newest candle's buy and sell marks and their words.
            rightOffsetPixels: 28,
            ...time.timeScale,
          },
          localization: time.localization,
        })
        const series = chart.addSeries(CandlestickSeries, {
          priceFormat: priceFormat(latestRef.current.places),
        })
        chartRef.current = chart
        seriesRef.current = series
        markersRef.current = createSeriesMarkers(series, [])
        const latest = latestRef.current
        const bars = spotBars(latest.candles, interval, PROVISIONAL)
        series.setData(bars)
        previousRef.current = { signature: signature(latest.candles), bars }
        paintOverlay(bars)
        chart.timeScale().fitContent()
        setReady(true)
      })
      .catch((error: unknown) => {
        console.error("Bitcoin chart initialization failed", error)
        if (active) setFailed(true)
      })
    return () => {
      active = false
      markersRef.current?.detach()
      markersRef.current = null
      chartRef.current = null
      seriesRef.current = null
      previousRef.current = null
      chart?.remove()
    }
    // paintOverlay reads only refs.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [interval])

  // The markers follow the bars and the trades; they are replaced as a whole.
  function paintOverlay(bars: SpotBar[]) {
    markersRef.current?.setMarkers(
      fillMarkers(latestRef.current.overlay, bars, interval)
    )
  }

  useEffect(() => {
    const bars = previousRef.current?.bars
    if (!seriesRef.current || !bars) return
    paintOverlay(bars)
    // paintOverlay reads only refs. An overlay that arrives before the chart exists is painted by
    // the chart's first draw, which reads the latest one.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [overlay])

  useEffect(() => {
    const chart = chartRef.current
    const series = seriesRef.current
    if (!chart || !series) return
    const next = signature(candles)
    const previous = previousRef.current
    if (previous?.signature === next) return
    const bars = spotBars(candles, interval, PROVISIONAL)
    const prior = previous?.bars ?? []
    const same = (length: number) =>
      prior
        .slice(0, length)
        .every(
          (bar, index) => JSON.stringify(bar) === JSON.stringify(bars[index])
        )
    // The newest candle changed, or one more began: update it alone, so the view stays put.
    if (
      bars.length > 0 &&
      previous &&
      ((bars.length === prior.length && same(prior.length - 1)) ||
        (bars.length === prior.length + 1 && same(prior.length)))
    ) {
      series.update(bars[bars.length - 1])
      if (bars.length !== prior.length) paintOverlay(bars)
    } else {
      const visible = chart.timeScale().getVisibleRange()
      series.setData(bars)
      if (visible) chart.timeScale().setVisibleRange(visible)
      else chart.timeScale().fitContent()
      paintOverlay(bars)
    }
    previousRef.current = { signature: next, bars }
    // paintOverlay reads only refs.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [candles, interval])

  const described = useId()
  return (
    <div className="flex flex-col gap-2">
      <div
        ref={containerRef}
        role="img"
        aria-label={`Bitcoin spot ${interval} candlestick chart`}
        aria-describedby={overlay ? described : undefined}
        className={cn(height, "w-full")}
      />
      {overlay && (
        <p id={described} className="sr-only">
          {markersText(overlay)}
        </p>
      )}
      {!ready && !failed && (
        <p role="status" className="text-sm text-muted-foreground">
          Loading the Bitcoin chart…
        </p>
      )}
      {failed && <p className="text-sm text-destructive">Chart unavailable.</p>}
    </div>
  )
}
