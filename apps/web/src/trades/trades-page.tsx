import { useInfiniteQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { createColumnHelper } from "@tanstack/react-table"
import { ArrowLeftRight, CalendarClock } from "lucide-react"
import { CardHeading, NothingYet, ReadFailed } from "@/cockpit/states"
import { DateTime } from "@/components/date-time"
import {
  DataTable,
  moneyText,
  priceText,
  quantityText,
} from "@/components/page-parts"
import type { PlainFeatures } from "@/components/page-parts"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { Spinner } from "@/components/ui/spinner"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { formatDate } from "@/lib/display"
import {
  OUTCOME_TEXT,
  REASON_TEXT,
  SideBadge,
  codesText,
  codeText,
  shareText,
  trendText,
  whyText,
} from "@/spot/parts"
import { readingsListQuery, tradesListQuery } from "@/spot/spot.query"
import type { Reading, Trade } from "@/spot/schemas"

// Trades (ExecPlan 0060 section 4.9): every buy and sell of the account, newest first, with its time,
// side, quantity, price, fee and why; and a tab with every daily reading of the rule.

export const TRADES_TABS = ["trades", "readings"] as const
export type TradesTab = (typeof TRADES_TABS)[number]
export type TradesSearch = { tab?: "readings" }

const tradeHelper = createColumnHelper<PlainFeatures, Trade>()
const tradeColumns = tradeHelper.columns([
  tradeHelper.accessor("filled_at", {
    header: "Time",
    cell: (info) => <DateTime value={info.getValue()} />,
  }),
  tradeHelper.accessor("side", {
    header: "Side",
    cell: (info) => <SideBadge side={info.getValue()} />,
  }),
  tradeHelper.accessor("quantity", {
    header: "Quantity",
    cell: (info) => quantityText(info.getValue(), "BTC"),
    meta: { numeric: true },
  }),
  tradeHelper.accessor("price", {
    header: "Price",
    cell: (info) => priceText(info.getValue()),
    meta: { numeric: true },
  }),
  tradeHelper.accessor("gross", {
    header: "Value",
    cell: (info) => moneyText(info.getValue()),
    meta: { numeric: true },
  }),
  tradeHelper.accessor("fee", {
    header: "Fee",
    cell: (info) => moneyText(info.getValue()),
    meta: { numeric: true },
  }),
  tradeHelper.display({
    id: "why",
    header: "Why",
    cell: ({ row: { original } }) => (
      <span className="flex min-w-48 flex-col gap-0.5 whitespace-normal">
        <span className="font-medium">{REASON_TEXT[original.reason]}</span>
        <span className="text-xs text-muted-foreground">
          {whyText(original)}
        </span>
      </span>
    ),
  }),
])

function dayText(day: string): string {
  return formatDate(`${day}T00:00:00Z`, "UTC")
}

const readingHelper = createColumnHelper<PlainFeatures, Reading>()
const readingColumns = readingHelper.columns([
  readingHelper.accessor("utc_date", {
    header: "Day",
    cell: (info) => dayText(info.getValue()),
  }),
  readingHelper.accessor("close", {
    header: "Close read",
    cell: ({ row: { original } }) =>
      original.close === null ? "—" : priceText(original.close),
    meta: { numeric: true },
  }),
  readingHelper.display({
    id: "trend",
    header: "Trend",
    cell: ({ row: { original } }) =>
      original.outcome === "NOT_READABLE"
        ? "—"
        : trendText(original.up, original.anchors.length),
  }),
  readingHelper.accessor("target", {
    header: "Target",
    cell: (info) => {
      const value = info.getValue()
      return value === null ? "—" : shareText(value)
    },
    meta: { numeric: true },
  }),
  readingHelper.accessor("held", {
    header: "Held before",
    cell: (info) => {
      const value = info.getValue()
      return value === null ? "—" : shareText(value)
    },
    meta: { numeric: true },
  }),
  readingHelper.display({
    id: "outcome",
    header: "Done",
    cell: ({ row: { original } }) => (
      <span className="flex min-w-48 flex-col items-start gap-1 whitespace-normal">
        <Badge
          variant={original.outcome === "FILLED" ? "secondary" : "outline"}
        >
          {OUTCOME_TEXT[original.outcome]}
        </Badge>
        <span className="text-xs text-muted-foreground">
          {outcomeDetail(original)}
        </span>
      </span>
    ),
  }),
  readingHelper.accessor("at", {
    header: "Read",
    cell: (info) => <DateTime value={info.getValue()} seconds={false} />,
  }),
])

/** What a reading did, in a line under its outcome. */
function outcomeDetail(reading: Reading): string {
  if (reading.outcome === "FILLED" && reading.fill)
    return `${reading.fill.side === "BUY" ? "Bought" : "Sold"} ${quantityText(reading.fill.quantity, "BTC")} at ${priceText(reading.fill.price)}`
  if (reading.outcome === "REFUSED") return codesText(reading.codes)
  if (reading.outcome === "NOT_READABLE")
    return codeText(reading.reason ?? "UNKNOWN")
  return reading.target !== null && /^0(?:\.0+)?$/.test(reading.target)
    ? "Holds no Bitcoin"
    : "Close enough to the target"
}

function MoreButton({
  more,
  loading,
  onMore,
  label,
}: {
  more: boolean
  loading: boolean
  onMore: () => void
  label: string
}) {
  if (!more) return null
  return (
    <CardFooter className="justify-center">
      <Button variant="outline" size="sm" disabled={loading} onClick={onMore}>
        {loading && <Spinner data-icon="inline-start" />}
        {label}
      </Button>
    </CardFooter>
  )
}

function TradesTable() {
  const read = useInfiniteQuery(tradesListQuery())
  const pages = read.data?.pages ?? []
  const items = pages.flatMap((page) => page.items)
  return (
    <Card>
      <CardHeader>
        <CardHeading icon={ArrowLeftRight}>Buys and sells</CardHeading>
        <CardDescription>
          Market orders priced from the order book, after slippage and the fee,
          which is paid in USDT.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {read.isPending ? (
          <Skeleton aria-hidden="true" className="h-64 w-full" />
        ) : read.isError ? (
          <ReadFailed what="the trades" onRetry={() => void read.refetch()} />
        ) : pages[0]?.state === "SCHEMA_PENDING" ? (
          <NothingYet
            icon={ArrowLeftRight}
            title="The database is being updated"
            detail="The trades show once the update has finished."
          />
        ) : items.length === 0 ? (
          <NothingYet
            icon={ArrowLeftRight}
            title="No trades yet"
            detail="The rule buys or sells at most once a day, after its reading."
          />
        ) : (
          <DataTable
            columns={tradeColumns}
            data={items}
            getRowId={(trade) => trade.id}
            caption="The account's buys and sells, newest first"
          />
        )}
      </CardContent>
      <MoreButton
        more={read.hasNextPage}
        loading={read.isFetchingNextPage}
        onMore={() => void read.fetchNextPage()}
        label="Earlier trades"
      />
    </Card>
  )
}

function ReadingsTable() {
  const read = useInfiniteQuery(readingsListQuery())
  const pages = read.data?.pages ?? []
  const items = pages.flatMap((page) => page.items)
  return (
    <Card>
      <CardHeader>
        <CardHeading icon={CalendarClock}>Daily readings</CardHeading>
        <CardDescription>
          Once a UTC day the rule compares Bitcoin&apos;s last daily close with
          earlier closes and sets the share of the account to hold in Bitcoin. A
          day it cannot trade yet is tried again later the same day.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {read.isPending ? (
          <Skeleton aria-hidden="true" className="h-64 w-full" />
        ) : read.isError ? (
          <ReadFailed what="the readings" onRetry={() => void read.refetch()} />
        ) : pages[0]?.state === "SCHEMA_PENDING" ? (
          <NothingYet
            icon={CalendarClock}
            title="The database is being updated"
            detail="The readings show once the update has finished."
          />
        ) : items.length === 0 ? (
          <NothingYet
            icon={CalendarClock}
            title="No reading yet"
            detail="The first comes just after the next UTC midnight."
          />
        ) : (
          <DataTable
            columns={readingColumns}
            data={items}
            getRowId={(reading) => reading.id}
            caption="The rule's daily readings, newest first"
          />
        )}
      </CardContent>
      <MoreButton
        more={read.hasNextPage}
        loading={read.isFetchingNextPage}
        onMore={() => void read.fetchNextPage()}
        label="Earlier readings"
      />
    </Card>
  )
}

export function TradesPage({ search }: { search: TradesSearch }) {
  const navigate = useNavigate({ from: "/trades" })
  const tab: TradesTab = search.tab ?? "trades"
  return (
    <>
      <h1 className="font-heading text-xl font-semibold tracking-tight">
        Trades
      </h1>
      <Tabs
        value={tab}
        onValueChange={(value) => {
          void navigate({
            search: value === "readings" ? { tab: "readings" } : {},
            resetScroll: false,
          })
        }}
        className="gap-4"
      >
        <TabsList aria-label="Trades view">
          <TabsTrigger value="trades">
            <ArrowLeftRight data-icon="inline-start" />
            Trades
          </TabsTrigger>
          <TabsTrigger value="readings">
            <CalendarClock data-icon="inline-start" />
            Daily readings
          </TabsTrigger>
        </TabsList>
        <TabsContent value="trades">
          <TradesTable />
        </TabsContent>
        <TabsContent value="readings">
          <ReadingsTable />
        </TabsContent>
      </Tabs>
    </>
  )
}
