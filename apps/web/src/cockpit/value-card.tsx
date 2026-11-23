import { useQuery } from "@tanstack/react-query"
import {
  Bitcoin,
  CalendarDays,
  ChartSpline,
  CircleDollarSign,
  Lock,
  TrendingDown,
  TrendingUp,
  Wallet,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { useState } from "react"
import type { ReactNode } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { useTimeZone } from "@/components/time-zone-provider"
import {
  formatAxisTime,
  formatDateTime,
  formatMoney,
  formatPercent,
  formatQuantity,
  navReturn,
} from "@/lib/display"
import { cn } from "@/lib/utils"
import { shareText } from "@/spot/parts"
import { spotValuationsQuery } from "@/spot/spot.query"
import { valuationWindowSchema } from "@/spot/schemas"
import type { Overview, SpotRun, ValuationWindow } from "@/spot/schemas"
import { EquityChart } from "./equity-chart"
import { share } from "./geometry"
import { useStoredChoice } from "./preference"
import { CardHeading, Hint, NothingYet, ReadFailed, StaleTag } from "./states"
import { Gauge, HeroGlow, Ring } from "./visuals"

// The Cockpit's hero (ExecPlan 0060 section 4.9, after ExecPlan 0048 section 4.2): the account's
// value, what it made since the start and today, its fall from the run's high against the drawdown
// stop, the USDT and the Bitcoin held with Bitcoin's share, and the value's curve since the run began.
// Every figure is the API's; the result since the start is the value less the contributions, and the
// return NAV / 100 - 1.

const WINDOWS = valuationWindowSchema.options
const WINDOW_TEXT: Record<ValuationWindow, string> = {
  "24h": "24h",
  "7d": "7d",
  all: "All",
}

/** Green for a gain, red for a loss, plain for nothing either way. */
export function toneOf(value: string | null): string {
  if (value === null || /^-?0(?:\.0+)?$/.test(value)) return ""
  return value.startsWith("-") ? "text-negative" : "text-positive"
}

/** The value flashes once when it changes after the page first showed it. */
function Flash({ value, children }: { value: string; children: string }) {
  const [first] = useState(value)
  return (
    <span
      key={value}
      className={cn(
        "rounded-md",
        value !== first && "motion-safe:animate-flash"
      )}
    >
      {children}
    </span>
  )
}

function Holding({
  icon: Icon,
  label,
  children,
  title,
}: {
  icon: LucideIcon
  label: string
  children: ReactNode
  title?: string
}) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Icon className="size-3.5" aria-hidden="true" />
        {label}
      </dt>
      <dd className="truncate font-medium tabular-nums" title={title}>
        {children}
      </dd>
    </div>
  )
}

/**
 * The run against holding Bitcoin, paired by day (ExecPlan 0061): the run's value per unit and Bitcoin's daily close
 * between the run's first and newest timely daily references, as the API computes them. Nothing until the run has two
 * such days.
 */
export function SinceStart({ run }: { run: SpotRun | null }) {
  const zone = useTimeZone()
  const since = run?.since_start ?? null
  if (run === null || since === null) return null
  const from = formatDateTime(since.from_at, zone, { seconds: false })
  const to = formatDateTime(since.at, zone, { seconds: false })
  return (
    <div className="flex flex-wrap items-center gap-1.5 text-sm">
      <Bitcoin className="size-3.5 text-muted-foreground" aria-hidden="true" />
      <span className="text-muted-foreground">
        {`Since ${formatAxisTime(since.from_at, zone, "day")} ${formatAxisTime(since.from_at, zone, "month")}`}
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className="text-muted-foreground">Run</span>
        <Hint
          label={`Run #${run.seq}'s value per unit from ${from} to ${to}, after fees; a top-up is not a gain`}
          className={cn("font-medium tabular-nums", toneOf(since.account))}
        >
          {formatPercent(since.account, { signed: true })}
        </Hint>
      </span>
      <span className="inline-flex items-center gap-1.5">
        <span className="text-muted-foreground">Bitcoin</span>
        <Hint
          label={`Holding Bitcoin over the same days: its daily close went from ${formatMoney(since.from_price)} to ${formatMoney(since.price)} USDT`}
          className={cn("font-medium tabular-nums", toneOf(since.bitcoin))}
        >
          {formatPercent(since.bitcoin, { signed: true })}
        </Hint>
      </span>
    </div>
  )
}

export function ValueCard({
  overview,
  className,
}: {
  overview: Overview
  className?: string
}) {
  const [range, choose] = useStoredChoice<ValuationWindow>(
    "asl.cockpit.equity-window",
    WINDOWS,
    "all"
  )
  const curve = useQuery(spotValuationsQuery(range))
  const account = overview.account
  const equity = account?.equity ?? null
  const result = account?.pnl ?? null
  const growth = account?.nav ? navReturn(account.nav) : null
  const limits = overview.limits
  const today = limits?.today_change ?? null
  const fall = limits?.fall_from_high ?? null
  const fraction =
    fall === null || limits === null
      ? null
      : share(Number(fall), Number(limits.drawdown))
  const latched = overview.latches.length > 0
  const drawdownText =
    limits === null
      ? "Fall from the run's high: unknown"
      : `Fall from the run's high ${fall === null ? "not measured" : formatPercent(fall)} of the ${formatPercent(limits.drawdown, { decimals: 0, max: 2 })} stop${latched ? ", a limit has tripped" : ""}`
  const Rising = result?.startsWith("-") ? TrendingDown : TrendingUp
  const inBitcoin = account?.share ?? null
  return (
    <Card className={cn("relative", className)}>
      <HeroGlow />
      <CardHeader className="relative">
        <CardHeading icon={Wallet}>Account value</CardHeading>
        <CardAction>
          <ToggleGroup
            aria-label="Value curve range"
            value={[range]}
            onValueChange={(values) => {
              const next = valuationWindowSchema.safeParse(values[0])
              if (next.success) choose(next.data)
            }}
            variant="outline"
            size="sm"
            spacing={0}
          >
            {WINDOWS.map((item) => (
              <ToggleGroupItem key={item} value={item}>
                {WINDOW_TEXT[item]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </CardAction>
      </CardHeader>
      <CardContent className="relative flex flex-1 flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex min-w-0 flex-col gap-1.5">
            {equity === null ? (
              <p className="font-heading text-4xl font-semibold tracking-tight text-muted-foreground">
                —
                <StaleTag className="ml-2 align-middle">
                  No fresh price
                </StaleTag>
              </p>
            ) : (
              <p
                className="font-heading text-[32px] leading-none font-semibold tracking-tight tabular-nums @md/main:text-4xl @4xl/main:text-5xl"
                title="The USDT plus the Bitcoin at the best bid"
              >
                <Flash value={equity}>{formatMoney(equity)}</Flash>
                <span className="ml-1.5 text-sm font-medium tracking-normal text-muted-foreground">
                  USDT
                </span>
              </p>
            )}
            <div className="flex flex-wrap items-center gap-1.5 text-sm">
              {result !== null && (
                <Hint
                  label="Result since the start: the value less what was added"
                  className={cn("font-medium tabular-nums", toneOf(result))}
                >
                  <Rising className="size-3.5" aria-hidden="true" />
                  {`${formatMoney(result, { signed: true })} USDT`}
                </Hint>
              )}
              {growth !== null && (
                <Badge
                  variant="secondary"
                  className={cn("tabular-nums", toneOf(growth))}
                  title="Return since the start: NAV per unit / 100 - 1, so a top-up is not a gain"
                >
                  {formatPercent(growth, { signed: true })}
                </Badge>
              )}
              {(result !== null || growth !== null) && (
                <span className="text-muted-foreground">since start</span>
              )}
            </div>
            <div className="flex items-center gap-1.5 text-sm">
              <CalendarDays
                className="size-3.5 text-muted-foreground"
                aria-hidden="true"
              />
              <span className="text-muted-foreground">Today</span>
              {today === null ? (
                <span className="text-muted-foreground">Unknown</span>
              ) : (
                <span
                  className={cn("font-medium tabular-nums", toneOf(today))}
                  title="Change since the UTC day's reference value, after fees"
                >
                  <Flash value={today}>
                    {formatPercent(today, { signed: true })}
                  </Flash>
                </span>
              )}
            </div>
            <SinceStart run={overview.run} />
          </div>
          <Gauge
            fraction={fraction}
            label={drawdownText}
            caption="From the high"
          >
            {latched ? (
              <Lock className="size-4.5" aria-hidden="true" />
            ) : undefined}
          </Gauge>
        </div>
        {account !== null && (
          <>
            <Separator />
            <dl className="grid grid-cols-[minmax(0,1fr)_minmax(0,1fr)_auto] items-center gap-3 text-sm">
              <Holding
                icon={CircleDollarSign}
                label="USDT"
                title={`${account.cash} USDT`}
              >
                {formatMoney(account.cash)}
              </Holding>
              <Holding
                icon={Bitcoin}
                label="Bitcoin"
                title={`${account.btc} BTC${account.btc_value === null ? "" : `, ${account.btc_value} USDT at the best bid`}`}
              >
                {`${formatQuantity(account.btc)} BTC`}
                {account.btc_value !== null && (
                  <span className="ml-1 text-xs text-muted-foreground">
                    {`${formatMoney(account.btc_value)} USDT`}
                  </span>
                )}
              </Holding>
              <Ring
                value={inBitcoin === null ? null : Number(inBitcoin)}
                label={`In Bitcoin: ${shareText(inBitcoin)} of the account's value`}
                size="sm"
                className="size-12"
              >
                <span className="text-[10px] font-medium text-foreground tabular-nums">
                  {shareText(inBitcoin)}
                </span>
              </Ring>
            </dl>
          </>
        )}
        <div className="-mx-4 -mb-4 flex h-48 flex-col @4xl/main:h-auto @4xl/main:min-h-75 @4xl/main:flex-1">
          {curve.isPending ? (
            <Skeleton aria-hidden="true" className="mx-4 mb-4 flex-1" />
          ) : curve.isError ? (
            <div className="px-4 pb-4">
              <ReadFailed
                what="the value curve"
                onRetry={() => void curve.refetch()}
              />
            </div>
          ) : curve.data.points.length < 2 ? (
            <div className="px-4 pb-4">
              <NothingYet
                icon={ChartSpline}
                title="No curve yet"
                detail="It draws once the account has two valuations in this range."
              />
            </div>
          ) : (
            <EquityChart valuations={curve.data} className="flex-1" />
          )}
        </div>
      </CardContent>
    </Card>
  )
}
