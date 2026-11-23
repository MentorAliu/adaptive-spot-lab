import { useQuery } from "@tanstack/react-query"
import { ChartCandlestick } from "lucide-react"
import { Card, CardAction, CardHeader } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { SpotChart } from "@/spot/spot-chart"
import { candlesQuery, spotMarkersQuery } from "@/spot/spot.query"
import type { Interval } from "@/spot/schemas"
import { useStoredChoice } from "./preference"
import { CardHeading, NothingYet, ReadFailed } from "./states"

// The Cockpit's chart (ExecPlan 0060 section 4.9): Bitcoin's spot candles with every buy and sell
// marked, edge to edge at the card's foot. The rule reads once a day, so the daily candles come first.

export const CHART_INTERVALS = [
  "1d",
  "4h",
  "1h",
  "15m",
] as const satisfies readonly Interval[]
type ChartInterval = (typeof CHART_INTERVALS)[number]
const INTERVAL_TEXT: Record<ChartInterval, string> = {
  "1d": "Day",
  "4h": "4h",
  "1h": "1h",
  "15m": "15m",
}

export function ChartCard({ className }: { className?: string }) {
  const [interval, choose] = useStoredChoice<ChartInterval>(
    "asl.cockpit.chart-interval",
    CHART_INTERVALS,
    "1d"
  )
  const candles = useQuery(candlesQuery(interval))
  const rows = candles.data?.candles ?? []
  const first = rows.length > 0 ? rows[0].open_ms : null
  const markers = useQuery(spotMarkersQuery(first))
  return (
    <Card className={className}>
      <CardHeader>
        <CardHeading icon={ChartCandlestick}>Bitcoin</CardHeading>
        <CardAction>
          <ToggleGroup
            aria-label="Candle length"
            value={[interval]}
            onValueChange={(values) => {
              const next = CHART_INTERVALS.find((item) => item === values[0])
              if (next) choose(next)
            }}
            variant="outline"
            size="sm"
            spacing={0}
          >
            {CHART_INTERVALS.map((item) => (
              <ToggleGroupItem key={item} value={item}>
                {INTERVAL_TEXT[item]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>
      <div className="-mb-4">
        {candles.isPending ? (
          <Skeleton aria-hidden="true" className="mx-4 mb-4 h-80" />
        ) : candles.isError ? (
          <div className="px-4 pb-8">
            <ReadFailed
              what="Bitcoin candles"
              onRetry={() => void candles.refetch()}
            />
          </div>
        ) : rows.length === 0 ? (
          <div className="px-4 pb-8">
            <NothingYet
              icon={ChartCandlestick}
              title="No candles yet"
              detail="They appear once the price feed has stored Bitcoin's history."
            />
          </div>
        ) : (
          <SpotChart
            key={interval}
            interval={interval}
            candles={rows}
            overlay={markers.data ?? null}
            height="h-85"
          />
        )}
      </div>
    </Card>
  )
}
