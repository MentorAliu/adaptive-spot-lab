import { useQuery } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import {
  ArrowDownRight,
  ArrowLeftRight,
  ArrowUpRight,
  ChevronRight,
} from "lucide-react"
import { buttonVariants } from "@/components/ui/button"
import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import {
  Item,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import { Skeleton } from "@/components/ui/skeleton"
import { useNow } from "@/hooks/use-now"
import {
  formatAgo,
  formatMoney,
  formatPrice,
  formatQuantity,
} from "@/lib/display"
import { whyText } from "@/spot/parts"
import { RECENT_TRADES, recentTradesQuery } from "@/spot/spot.query"
import type { Trade } from "@/spot/schemas"
import { CardHeading, NothingYet, ReadFailed } from "./states"
import { IconTile } from "./visuals"

// The Cockpit's trades (ExecPlan 0060 section 4.9): the newest buys and sells, each with why it was made;
// Trades has them all.

function TradeRow({ trade, now }: { trade: Trade; now: number | null }) {
  const buy = trade.side === "BUY"
  const Icon = buy ? ArrowUpRight : ArrowDownRight
  return (
    <Item role="listitem" size="sm" className="px-0">
      <ItemMedia>
        <IconTile accent={buy}>
          <Icon className="size-4" />
        </IconTile>
      </ItemMedia>
      <ItemContent className="min-w-0">
        <ItemTitle className="w-full justify-between gap-2 tabular-nums">
          <span className="truncate">
            {`${buy ? "Bought" : "Sold"} ${formatQuantity(trade.quantity)} BTC`}
          </span>
          <span className="shrink-0 text-xs font-normal text-muted-foreground">
            {now === null ? "" : formatAgo(trade.filled_at, now)}
          </span>
        </ItemTitle>
        <ItemDescription className="line-clamp-2">
          {`At ${formatPrice(trade.price)} · ${formatMoney(trade.gross)} USDT · fee ${formatMoney(trade.fee)} · ${whyText(trade)}`}
        </ItemDescription>
      </ItemContent>
    </Item>
  )
}

export function RecentTrades({ className }: { className?: string }) {
  const trades = useQuery(recentTradesQuery)
  const now = useNow()
  return (
    <Card className={className}>
      <CardHeader>
        <CardHeading icon={ArrowLeftRight}>Latest trades</CardHeading>
        <CardAction>
          <Link
            to="/trades"
            search={{}}
            className={buttonVariants({ variant: "ghost", size: "xs" })}
          >
            All trades
            <ChevronRight data-icon="inline-end" />
          </Link>
        </CardAction>
      </CardHeader>
      <CardContent>
        {trades.isPending ? (
          <div aria-hidden="true" className="flex flex-col gap-3">
            {Array.from({ length: 3 }, (_, index) => (
              <Skeleton key={index} className="h-12 w-full" />
            ))}
          </div>
        ) : trades.isError ? (
          <ReadFailed what="the trades" onRetry={() => void trades.refetch()} />
        ) : trades.data.items.length === 0 ? (
          <NothingYet
            icon={ArrowLeftRight}
            title="No trades yet"
            detail="The rule buys or sells at most once a day, after its reading."
          />
        ) : (
          <ItemGroup
            aria-label={`The newest ${RECENT_TRADES} trades`}
            className="gap-0 divide-y"
          >
            {trades.data.items.map((trade) => (
              <TradeRow key={trade.id} trade={trade} now={now} />
            ))}
          </ItemGroup>
        )}
      </CardContent>
    </Card>
  )
}
