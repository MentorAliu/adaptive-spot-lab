import { useQuery } from "@tanstack/react-query"
import type { UseQueryResult } from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import {
  ArrowRight,
  ChevronRight,
  CircleCheck,
  CircleOff,
  CircleQuestionMark,
  Hand,
  Info,
  Pause,
  TriangleAlert,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"
import { DateTime } from "@/components/date-time"
import { Badge } from "@/components/ui/badge"
import { Button, buttonVariants } from "@/components/ui/button"
import {
  Item,
  ItemActions,
  ItemContent,
  ItemDescription,
  ItemGroup,
  ItemMedia,
  ItemTitle,
} from "@/components/ui/item"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet"
import { Skeleton } from "@/components/ui/skeleton"
import { useIsMobile } from "@/hooks/use-mobile"
import { cn } from "@/lib/utils"
import { RUN } from "@/spot/parts"
import { marketQuery, spotOverviewQuery } from "@/spot/spot.query"
import { spotStatus } from "@/spot/status"
import type { Note, Place, TradingStatus } from "@/spot/status"
import { statusQueryOptions } from "@/system/status.query"

// The Cockpit's status pill (ExecPlan 0048 section 4.1; the spot account's since ExecPlan 0060): one
// line that says whether the account trades. Nothing to see is a quiet badge; anything else opens a
// sheet with each note and the Settings section that handles it, from recorded state (spotStatus).

const STATUS_MS = 30_000

const PLACE: Record<Place, string> = {
  run: "Run",
  rule: "Rule",
  account: "Account",
  health: "Health",
}

const KIND: Record<Note["kind"], { word: string; icon: LucideIcon }> = {
  action: { word: "Needs you", icon: Hand },
  problem: { word: "Problem", icon: TriangleAlert },
  info: { word: "Info", icon: Info },
}

/** A read whose latest attempt failed is unknown, even with older data in the cache. */
function value<T>(query: UseQueryResult<T>): T | null {
  return query.isError || query.errorUpdatedAt > query.dataUpdatedAt
    ? null
    : (query.data ?? null)
}

/** The pill's words and icon for a status. */
export function pillOf(
  status: TradingStatus,
  word = "Trading"
): {
  text: string
  icon: LucideIcon
  tone: "ok" | "warning" | "danger"
  quiet: boolean
} {
  const needs = status.notes.filter((note) => note.kind === "action").length
  const problems = status.notes.filter((note) => note.kind === "problem").length
  const count =
    needs > 0
      ? `${needs} need${needs === 1 ? "s" : ""} you`
      : problems > 0
        ? `${problems} ${problems === 1 ? "problem" : "problems"}`
        : `${status.notes.length} ${status.notes.length === 1 ? "note" : "notes"}`
  if (status.state === "trading")
    return status.notes.length === 0
      ? {
          text: `${word} · all good`,
          icon: CircleCheck,
          tone: "ok",
          quiet: true,
        }
      : {
          text: `${word} · ${count}`,
          icon: needs + problems > 0 ? Hand : Info,
          tone: needs + problems > 0 ? "warning" : "ok",
          quiet: false,
        }
  if (status.state === "held")
    return {
      text: `On hold · ${count}`,
      icon: needs > 0 ? Hand : Pause,
      tone: "warning",
      quiet: false,
    }
  if (status.state === "stopped")
    return {
      text: `Not trading · ${count}`,
      icon: CircleOff,
      tone: "danger",
      quiet: false,
    }
  return {
    text: "Status unknown",
    icon: CircleQuestionMark,
    tone: "danger",
    quiet: false,
  }
}

const TONE = {
  ok: "text-muted-foreground",
  warning: "text-warning",
  danger: "text-destructive",
} as const

export function StatusPill() {
  const status = useQuery({
    ...statusQueryOptions,
    refetchInterval: STATUS_MS,
    retry: false,
  })
  const market = useQuery(marketQuery)
  const overview = useQuery(spotOverviewQuery)
  const mobile = useIsMobile()
  const settled = [status, market, overview].every(
    (query) => query.isFetched || query.isError
  )
  if (!settled)
    return (
      <Skeleton
        role="status"
        aria-label="Checking the trading status"
        className="h-7 w-44 rounded-full"
      />
    )
  const checked = Math.max(
    ...[status, market, overview].map((query) => query.dataUpdatedAt)
  )
  const result = spotStatus({
    overview: value(overview),
    market: value(market),
    status: value(status),
  })
  const run = value(overview)?.run ?? null
  const pill = pillOf(result, run ? RUN[run.state].text : "Trading")
  const Icon = pill.icon
  if (pill.quiet)
    return (
      <Badge
        variant="outline"
        className="h-7 gap-1.5 px-3 text-sm"
        title="The rule, the price feed and the trading engine are running"
      >
        <Icon className="text-positive" data-icon="inline-start" />
        {pill.text}
      </Badge>
    )
  return (
    <Sheet>
      <SheetTrigger
        render={<Button variant="outline" size="sm" />}
        aria-label={`${pill.text}: open the details`}
      >
        <Icon data-icon="inline-start" className={TONE[pill.tone]} />
        {pill.text}
        <ChevronRight
          data-icon="inline-end"
          className="text-muted-foreground"
        />
      </SheetTrigger>
      <SheetContent
        side={mobile ? "bottom" : "right"}
        className={cn(mobile && "max-h-[85svh] rounded-t-xl")}
      >
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Icon className={cn("size-4", TONE[pill.tone])} />
            {result.title}
          </SheetTitle>
          <SheetDescription>
            {checked > 0 ? (
              <>
                Checked <DateTime value={checked} />
              </>
            ) : (
              "Not checked yet"
            )}
          </SheetDescription>
        </SheetHeader>
        <ItemGroup className="gap-2 overflow-y-auto px-4 pb-4">
          {result.notes.map((note) => {
            const kind = KIND[note.kind]
            return (
              <Item
                key={note.text}
                role="listitem"
                variant={note.kind === "info" ? "muted" : "outline"}
                size="sm"
              >
                <ItemMedia variant="icon">
                  <kind.icon
                    className={
                      note.kind === "action"
                        ? "text-warning"
                        : note.kind === "problem"
                          ? "text-destructive"
                          : "text-muted-foreground"
                    }
                  />
                </ItemMedia>
                <ItemContent>
                  <ItemTitle>{kind.word}</ItemTitle>
                  <ItemDescription className="line-clamp-none">
                    {note.text}
                  </ItemDescription>
                </ItemContent>
                {note.place && (
                  <ItemActions>
                    <Link
                      to="/settings"
                      hash={note.place}
                      aria-label={`Open Settings: ${PLACE[note.place]}`}
                      className={buttonVariants({
                        variant: note.kind === "info" ? "ghost" : "outline",
                        size: "sm",
                      })}
                    >
                      {PLACE[note.place]}
                      <ArrowRight data-icon="inline-end" />
                    </Link>
                  </ItemActions>
                )}
              </Item>
            )
          })}
        </ItemGroup>
      </SheetContent>
    </Sheet>
  )
}
