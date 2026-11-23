import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { createColumnHelper } from "@tanstack/react-table"
import {
  Bitcoin,
  CalendarRange,
  ChartLine,
  FlaskConical,
  OctagonX,
  Turtle,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import type { ReactNode } from "react"
import { CardHeading, NothingYet, ReadFailed } from "@/cockpit/states"
import { toneOf } from "@/cockpit/value-card"
import { DateTime } from "@/components/date-time"
import { DataTable, moneyText, priceText } from "@/components/page-parts"
import type { PlainFeatures } from "@/components/page-parts"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  formatCount,
  formatDate,
  formatMoney,
  formatPercent,
} from "@/lib/display"
import { cn } from "@/lib/utils"
import { shareText } from "@/spot/parts"
import { backtestQuery } from "@/spot/spot.query"
import { backtestWindowSchema } from "@/spot/schemas"
import type {
  Backtest,
  BacktestHold,
  BacktestRule,
  BacktestWindow,
  BacktestWindowKey,
} from "@/spot/schemas"
import { BacktestChart, HOLD_COLOR, RULE_COLOR } from "./backtest-chart"

// Backtest (ExecPlan 0060 sections 4.6 and 4.9): the live rule on Binance's daily Bitcoin candles over
// three windows, against holding Bitcoin from the same start: the values day by day on one chart, the
// totals, and a row per year. The engine works it out after each install and each new day; the page
// only shows what it stored.

export type BacktestSearch = {
  window?: Exclude<BacktestWindowKey, "SINCE_2019">
}

export const WINDOW_TEXT: Record<BacktestWindowKey, string> = {
  SINCE_2019: "Since 2019",
  SINCE_2023: "Since 2023",
  LAST_12_MONTHS: "Last 12 months",
}

function dayText(day: string | null): string {
  return day === null ? "—" : formatDate(`${day}T00:00:00Z`, "UTC")
}

function signedPercent(value: string | null): string {
  return value === null ? "—" : formatPercent(value, { signed: true })
}

function Figure({
  label,
  value,
  detail,
  tone,
}: {
  label: string
  value: string
  detail?: string
  tone?: string
}) {
  return (
    <div className="flex min-w-0 flex-col gap-0.5">
      <dt className="text-xs text-muted-foreground">{label}</dt>
      <dd className={cn("font-medium tabular-nums", tone)}>{value}</dd>
      {detail && <dd className="text-xs text-muted-foreground">{detail}</dd>}
    </div>
  )
}

function Side({
  icon: Icon,
  title,
  color,
  result,
  children,
}: {
  icon: LucideIcon
  title: string
  color: string
  result: BacktestRule | BacktestHold
  children?: ReactNode
}) {
  return (
    <Card size="sm">
      <CardHeader>
        <CardHeading icon={Icon} level={3}>
          <span
            aria-hidden="true"
            className="size-2.5 rounded-full"
            style={{ backgroundColor: color }}
          />
          {title}
        </CardHeading>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <p className="font-heading text-3xl leading-none font-semibold tracking-tight tabular-nums">
          {formatMoney(result.final)}
          <span className="ml-1.5 text-sm font-medium tracking-normal text-muted-foreground">
            USDT
          </span>
        </p>
        <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-sm @md/main:grid-cols-3">
          <Figure
            label="Return"
            value={signedPercent(result.return)}
            tone={toneOf(result.return)}
          />
          <Figure
            label="A year"
            value={signedPercent(result.a_year)}
            tone={toneOf(result.a_year)}
          />
          <Figure
            label="Worst fall"
            value={formatPercent(result.worst_fall)}
            detail={
              result.worst_fall_day
                ? `to ${dayText(result.worst_fall_day)}`
                : undefined
            }
          />
          <Figure label="Fees" value={moneyText(result.fees)} />
          {children}
        </dl>
      </CardContent>
    </Card>
  )
}

const yearHelper = createColumnHelper<
  PlainFeatures,
  { year: number; rule: string | null; hold: string | null }
>()
const yearColumns = yearHelper.columns([
  yearHelper.accessor("year", { header: "Year" }),
  yearHelper.accessor("rule", {
    header: "The rule",
    cell: (info) => (
      <span className={toneOf(info.getValue())}>
        {signedPercent(info.getValue())}
      </span>
    ),
    meta: { numeric: true },
  }),
  yearHelper.accessor("hold", {
    header: "Holding Bitcoin",
    cell: (info) => (
      <span className={toneOf(info.getValue())}>
        {signedPercent(info.getValue())}
      </span>
    ),
    meta: { numeric: true },
  }),
])

/** A row per calendar year of the window, the rule's return beside holding's. */
export function yearRows(result: BacktestWindow) {
  const years = new Map<
    number,
    { year: number; rule: string | null; hold: string | null }
  >()
  for (const row of result.rule.years)
    years.set(row.year, { year: row.year, rule: row.return, hold: null })
  for (const row of result.hold.years)
    years.set(row.year, {
      year: row.year,
      rule: years.get(row.year)?.rule ?? null,
      hold: row.return,
    })
  return [...years.values()].sort((a, b) => b.year - a.year)
}

function WindowView({
  backtest,
  span,
}: {
  backtest: Backtest
  span: BacktestWindowKey
}) {
  const computed = backtest.computed
  const result = computed?.windows.find((item) => item.key === span) ?? null
  if (computed === null || result === null)
    return (
      <NothingYet
        icon={FlaskConical}
        title="No result for this window"
        detail="The stored history does not reach this window yet."
      />
    )
  const rule = result.rule
  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-muted-foreground">
        {`From ${moneyText(computed.start_cash)} on ${dayText(result.first_day)} to ${dayText(result.last_day)} (${formatCount(result.days)} days). Each day the rule reads the day before, as it does live, and buys or sells at that day's close after the fee and slippage of a live trade. Holding Bitcoin buys once at the first close and keeps it.`}
      </p>
      {rule.stopped && (
        <Alert>
          <OctagonX />
          <AlertTitle>{`The run would have stopped here: ${dayText(rule.stopped.day)}`}</AlertTitle>
          <AlertDescription>
            {`The account fell to the drawdown stop below its high, sold everything at ${priceText(rule.stopped.price)} and held USDT for the rest of the window.`}
          </AlertDescription>
        </Alert>
      )}
      <div className="grid grid-cols-1 gap-4 @3xl/main:grid-cols-2">
        <Side icon={Turtle} title="The rule" color={RULE_COLOR} result={rule}>
          <Figure
            label="Trades"
            value={`${formatCount(rule.buys)} buys, ${formatCount(rule.sells)} sells`}
            detail={
              rule.refused > 0
                ? `${formatCount(rule.refused)} refused by the size limits or the cash`
                : undefined
            }
          />
          <Figure
            label="Days in Bitcoin"
            value={shareText(rule.days_in_bitcoin)}
          />
          <Figure
            label="Share held"
            value={`${shareText(rule.average_held)} on average`}
            detail={`at most ${shareText(rule.max_held)}`}
          />
        </Side>
        <Side
          icon={Bitcoin}
          title="Holding Bitcoin"
          color={HOLD_COLOR}
          result={result.hold}
        />
      </div>
      <Card>
        <CardHeader>
          <CardHeading icon={ChartLine}>Value day by day</CardHeading>
          <CardDescription>
            In USDT, on a logarithmic scale; the rule&apos;s buys and sells are
            marked on its line.
          </CardDescription>
        </CardHeader>
        <CardContent className="px-0">
          {backtest.series === null || backtest.series.days.length < 2 ? (
            <div className="px-4">
              <NothingYet
                icon={ChartLine}
                title="No daily values"
                detail="The chart draws once the window has two days."
              />
            </div>
          ) : (
            <BacktestChart
              key={span}
              series={backtest.series}
              className="h-80 @3xl/main:h-96"
            />
          )}
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardHeading icon={CalendarRange}>Each year</CardHeading>
          <CardDescription>
            The return of each calendar year in the window; the first and last
            years count from the window&apos;s first and to its last day.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={yearColumns}
            data={yearRows(result)}
            getRowId={(row) => String(row.year)}
            caption="The return of each year, the rule beside holding Bitcoin"
          />
        </CardContent>
      </Card>
    </div>
  )
}

function DataLine({ backtest }: { backtest: Backtest }) {
  const computed = backtest.computed
  if (computed === null) return null
  const data = computed.data
  return (
    <p className="text-xs text-muted-foreground">
      {`Binance's daily Bitcoin candles from ${dayText(data.first_day)} to ${dayText(data.last_day)}: ${formatCount(data.days)} days${data.missing_days > 0 ? `, ${formatCount(data.missing_days)} missing` : ""}. Worked out `}
      <DateTime value={computed.computed_at} seconds={false} />.
    </p>
  )
}

export function BacktestPage({ search }: { search: BacktestSearch }) {
  const navigate = useNavigate({ from: "/backtest" })
  const chosen: BacktestWindowKey = search.window ?? "SINCE_2019"
  const backtest = useQuery(backtestQuery(chosen))
  return (
    <>
      <div className="flex flex-col gap-1">
        <h1 className="font-heading text-xl font-semibold tracking-tight">
          Backtest
        </h1>
        <p className="max-w-3xl text-sm text-muted-foreground">
          What the rule trading the account now would have made on
          Bitcoin&apos;s history, beside simply holding Bitcoin.
        </p>
      </div>
      <Tabs
        value={chosen}
        onValueChange={(value) => {
          const next = backtestWindowSchema.safeParse(value)
          if (!next.success) return
          void navigate({
            search: next.data === "SINCE_2019" ? {} : { window: next.data },
            resetScroll: false,
          })
        }}
        className="gap-4"
      >
        <TabsList aria-label="Window">
          {backtestWindowSchema.options.map((key) => (
            <TabsTrigger key={key} value={key}>
              {WINDOW_TEXT[key]}
            </TabsTrigger>
          ))}
        </TabsList>
        {backtestWindowSchema.options.map((key) => (
          <TabsContent key={key} value={key} className="flex flex-col gap-4">
            {key !== chosen ? null : backtest.isPending ? (
              <Skeleton aria-hidden="true" className="h-96 w-full" />
            ) : backtest.isError ? (
              <ReadFailed
                what="the backtest"
                onRetry={() => void backtest.refetch()}
              />
            ) : backtest.data.state === "SCHEMA_PENDING" ? (
              <NothingYet
                icon={FlaskConical}
                title="The database is being updated"
                detail="The backtest shows once the update has finished."
              />
            ) : backtest.data.state === "NOT_COMPUTED" ? (
              <NothingYet
                icon={FlaskConical}
                title="Working out the backtest"
                detail="It runs once Bitcoin's daily history is stored, within minutes of the app starting."
              >
                <Badge variant="outline">Checks again every 10 seconds</Badge>
              </NothingYet>
            ) : (
              <>
                <WindowView backtest={backtest.data} span={key} />
                <DataLine backtest={backtest.data} />
              </>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </>
  )
}
