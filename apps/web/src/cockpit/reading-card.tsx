import { Link } from "@tanstack/react-router"
import {
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  CalendarClock,
  Minus,
  Timer,
} from "lucide-react"
import { useTimeZone } from "@/components/time-zone-provider"
import { Badge } from "@/components/ui/badge"
import { buttonVariants } from "@/components/ui/button"
import { Card, CardAction, CardContent, CardHeader } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Facts, priceText } from "@/components/page-parts"
import { useNow } from "@/hooks/use-now"
import {
  formatAgo,
  formatDate,
  formatLeft,
  formatPercent,
  formatTime,
} from "@/lib/display"
import { readingText, shareText, todayText } from "@/spot/parts"
import type { Anchor, Overview, Reading } from "@/spot/schemas"
import { leftOf } from "./geometry"
import { CardHeading, Hint, NothingYet } from "./states"
import { Pips, Ring } from "./visuals"

// The Cockpit's reading (ExecPlan 0060 section 4.9): the rule's newest daily reading in words, the three
// closes it compared, the target it set and what was held, and when the next reading comes.

const DAY_MS = 86_400_000

function NextReading({ next }: { next: string | null }) {
  const zone = useTimeZone()
  const now = useNow()
  const at = next === null ? null : Date.parse(next)
  const gone =
    at === null || now === null ? null : 1 - leftOf(at - DAY_MS, at, now)
  return (
    <Hint
      className="rounded-full"
      label={
        at === null || now === null
          ? "The rule reads once a day, just after midnight UTC"
          : `Next reading ${formatTime(at, zone, { seconds: false })} · in ${formatLeft(at, now)}`
      }
    >
      <Ring value={gone} label="Time to the next reading">
        <Timer className="size-3.5" aria-hidden="true" />
      </Ring>
    </Hint>
  )
}

function AnchorBadge({ anchor }: { anchor: Anchor }) {
  const Icon =
    anchor.sign > 0 ? ArrowUpRight : anchor.sign < 0 ? ArrowDownRight : Minus
  const word =
    anchor.sign > 0 ? "above" : anchor.sign < 0 ? "below" : "level with"
  return (
    <Badge
      variant={anchor.sign > 0 ? "secondary" : "outline"}
      title={`The close was ${word} the close of ${anchor.day}${anchor.close === null ? "" : `, ${priceText(anchor.close)}`}`}
    >
      <Icon data-icon="inline-start" />
      {`${anchor.lookback_days} days`}
    </Badge>
  )
}

/** Annualized volatility as a percentage a year: 48% a year. */
export function volatilityText(value: string | null): string {
  return value === null
    ? "Unknown"
    : `${formatPercent(value, { decimals: 0, max: 0 })} a year`
}

function Latest({ reading }: { reading: Reading }) {
  const zone = useTimeZone()
  const readable = reading.outcome !== "NOT_READABLE"
  return (
    <>
      <p className="font-heading text-lg leading-snug font-semibold">
        {readingText(reading)}
      </p>
      {readable && (
        <div className="flex flex-wrap items-center gap-2">
          <Pips
            filled={reading.up}
            total={reading.anchors.length}
            label={`The close was above ${reading.up} of the ${reading.anchors.length} earlier closes`}
          />
          {reading.anchors.map((anchor) => (
            <AnchorBadge key={anchor.lookback_days} anchor={anchor} />
          ))}
        </div>
      )}
      {readable && (
        <Facts
          items={[
            ["Target", shareText(reading.target)],
            ["Held before", shareText(reading.held)],
            ["Volatility", volatilityText(reading.volatility)],
            [
              `Close of ${formatDate(`${reading.day_read}T00:00:00Z`, "UTC")}`,
              priceText(reading.close),
            ],
          ]}
        />
      )}
      <p className="text-xs text-muted-foreground">
        {`Read ${formatTime(reading.at, zone, { seconds: false })} on ${formatDate(reading.at, zone)}`}
      </p>
    </>
  )
}

export function ReadingCard({
  overview,
  className,
}: {
  overview: Overview
  className?: string
}) {
  const now = useNow()
  const zone = useTimeZone()
  const reading = overview.last_reading
  const today = overview.today
  return (
    <Card className={className}>
      <CardHeader>
        <CardHeading icon={CalendarClock}>
          The rule&apos;s reading
          {reading && now !== null && (
            <span
              className="font-sans text-xs font-normal text-muted-foreground tabular-nums"
              title={formatTime(reading.at, zone, { seconds: false })}
            >
              {formatAgo(reading.at, now)}
            </span>
          )}
        </CardHeading>
        <CardAction>
          <NextReading next={today?.next_reading_at ?? null} />
        </CardAction>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        {reading === null ? (
          <NothingYet
            icon={CalendarClock}
            title="No reading yet"
            detail="The rule reads Bitcoin's daily close once a day, just after midnight UTC, and sets how much of the account to hold in Bitcoin."
          />
        ) : (
          <Latest reading={reading} />
        )}
        <Separator />
        <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
          <span>
            {todayText(today, (iso) =>
              formatTime(iso, zone, { seconds: false })
            )}
          </span>
          <Link
            to="/trades"
            search={{ tab: "readings" }}
            className={buttonVariants({ variant: "ghost", size: "xs" })}
          >
            All readings
            <ArrowRight data-icon="inline-end" />
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
