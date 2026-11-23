import { ArrowDownRight, ArrowUpRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { formatPercent, formatPrice, formatQuantity } from "@/lib/display"
import { moneyText } from "@/components/page-parts"
import type {
  Cause,
  Reading,
  RunState,
  Side,
  StopReason,
  Today,
  Trade,
  TradeReason,
} from "./schemas"

// The spot account's words (ExecPlan 0060 section 4.9): what a run's state, a reading, a refusal and a
// trade mean, from the engine's recorded values only. A code the page does not know is shown as the
// engine wrote it, never guessed at.

export const RUN: Record<RunState, { text: string; detail: string }> = {
  RUNNING: {
    text: "Trading",
    detail:
      "The rule reads Bitcoin's trend once a day and trades the difference.",
  },
  PAUSED: {
    text: "Paused",
    detail: "No buy until the hold clears; the rule's sells still go through.",
  },
  STOPPING: {
    text: "Stopping",
    detail:
      "Selling the Bitcoin at the order book; the run stops once only USDT is held.",
  },
  STOPPED: {
    text: "Stopped",
    detail: "Nothing trades until you start a new run.",
  },
}

export const CAUSE_TEXT: Record<Cause, string> = {
  OWNER: "your Pause",
  DAILY_LOSS: "the daily loss limit",
  DRAWDOWN: "the drawdown stop",
  INTEGRITY: "a failed reconciliation check",
}

/** What holds the run, in a line: "Nothing holds it", "Held by your Pause and the daily loss limit". */
export function holdText(causes: Cause[]): string {
  if (causes.length === 0) return "Nothing holds it"
  const words = causes.map((cause) => CAUSE_TEXT[cause])
  const list =
    words.length === 1
      ? words[0]
      : `${words.slice(0, -1).join(", ")} and ${words[words.length - 1]}`
  return `Held by ${list}`
}

export function stopText(reason: StopReason | null): string {
  return reason === "DRAWDOWN"
    ? "the drawdown stop"
    : reason === "OWNER"
      ? "you"
      : "the app"
}

// Why a reading or a request was refused, in words.
const CODE_TEXT: Record<string, string> = {
  BID_STALE: "no fresh Bitcoin price to value the holding",
  VALUATION_UNAVAILABLE: "the account could not be valued",
  VALUATION_OVERRIDE_INVALID: "the account's valuation is switched off",
  BOOK_STALE: "the order book is not fresh",
  CLOCK_UNVERIFIED: "the clock is not checked against Binance's",
  INSTRUMENT_UNAVAILABLE:
    "Binance's trading rules for BTCUSDT are not confirmed",
  RUN_NOT_RUNNING: "the run is paused, so it buys nothing",
  INTEGRITY: "a reconciliation check failed, so it buys nothing",
  SIZE_BELOW_MINIMUM: "the trade is below Binance's minimum quantity",
  DEPTH_SHORT: "the order book is too thin for the trade",
  NOTIONAL_BELOW_MINIMUM: "the trade is below Binance's minimum value",
  CASH_SHORT: "not enough USDT for the buy and its fee",
  RUN_NOT_LIVE: "there is no run going",
  RUN_CHANGED: "the run changed since the page showed it",
  RUN_STOPPING: "the run is already stopping",
  ALREADY_PAUSED: "you already paused it",
  NOT_PAUSED_BY_OWNER: "you have not paused it",
  RUN_LIVE: "a run is already going",
  NOT_FUNDED: "the account has no money yet",
  REQUEST_NOT_FOUND: "the engine has no such request",
  CLOSE_MISSING: "the day's close is not stored yet",
}

export function codeText(code: string): string {
  const known = CODE_TEXT[code]
  if (known) return known
  const missing = /^ANCHOR_MISSING_([0-9]+)$/.exec(code)
  if (missing) return `the close ${missing[1]} days before is not stored`
  const few = /^TOO_FEW_DAYS_([0-9]+)$/.exec(code)
  if (few)
    return `too few days stored (${few[1]}) to measure how much Bitcoin moves`
  return code.replaceAll("_", " ").toLowerCase()
}

export function codesText(codes: string[]): string {
  return codes.length === 0
    ? "no reason recorded"
    : codes.map(codeText).join("; ")
}

/** A share of the account (0.0612) as 6.1%. */
export function shareText(fraction: string | null): string {
  return fraction === null
    ? "unknown"
    : formatPercent(fraction, { decimals: 1, max: 1 })
}

/** The trend in words: "Trend up 2 of 3". */
export function trendText(up: number, of: number): string {
  return `Trend up ${up} of ${of}`
}

function sideWord(side: Side): string {
  return side === "BUY" ? "bought" : "sold"
}

/** What a reading did after its target, in words: "bought 0.0021 BTC", "no trade needed". */
function actedText(reading: Reading): string {
  if (reading.outcome === "FILLED" && reading.fill)
    return `${sideWord(reading.fill.side)} ${formatQuantity(reading.fill.quantity)} BTC`
  if (reading.outcome === "REFUSED")
    return `no trade: ${codesText(reading.codes)}`
  if (reading.action === "NO_CHANGE") return "no trade needed"
  return "no trade"
}

/**
 * A daily reading in one line (ExecPlan 0060 section 4.9): "Trend up 2 of 3: hold 6.1% in Bitcoin;
 * bought 0.0021 BTC". A day that cannot be read yet says why.
 */
export function readingText(reading: Reading): string {
  if (reading.outcome === "NOT_READABLE")
    return `Not readable yet: ${codeText(reading.reason ?? "UNKNOWN")}`
  const trend = trendText(reading.up, reading.anchors.length)
  const target =
    reading.target === null
      ? "target unknown"
      : /^0(?:\.0+)?$/.test(reading.target)
        ? "hold no Bitcoin"
        : `hold ${shareText(reading.target)} in Bitcoin`
  return `${trend}: ${target}; ${actedText(reading)}`
}

/** The outcome of a reading in a word or two, for the readings table. */
export const OUTCOME_TEXT: Record<Reading["outcome"], string> = {
  FILLED: "Traded",
  NO_CHANGE: "No trade needed",
  REFUSED: "Refused, tries again",
  NOT_READABLE: "Not readable yet",
}

/** Today's reading in a line: when the next one comes, or why it waits. */
export function todayText(
  today: Today | null,
  format: (iso: string) => string
): string {
  if (today === null) return "No reading: the account is not set up yet."
  switch (today.status) {
    case "WAITING":
      return today.next_reading_at
        ? `Today's reading at ${format(today.next_reading_at)}.`
        : "Today's reading comes just after midnight UTC."
    case "DUE":
      return "Today's reading is due now."
    case "RETRYING":
      return `Today's reading tries again every ${Math.round(today.retry_seconds / 60)} minutes.`
    case "SPENT":
      return today.next_reading_at
        ? `Done for today. Next reading at ${format(today.next_reading_at)}.`
        : "Done for today."
    case "NONE":
      return "No reading while the run is stopping or stopped."
  }
}

export const REASON_TEXT: Record<TradeReason, string> = {
  RULE_BUY: "Daily rule",
  RULE_SELL: "Daily rule",
  STOP_SELL: "Run stopped",
}

/** Why a trade was made, in a line: "Trend up 2 of 3: target 6.1%, held 3.0%". */
export function whyText(trade: Trade): string {
  if (trade.reason === "STOP_SELL")
    return `Sold everything when the run stopped, by ${stopText(trade.stop_reason)}`
  const reading = trade.reading
  if (reading === null) return "The rule's daily reading"
  return `${trendText(reading.up, reading.anchors)}: target ${shareText(reading.target)}, held ${shareText(reading.held)}`
}

export function SideBadge({ side }: { side: Side }) {
  const Icon = side === "BUY" ? ArrowUpRight : ArrowDownRight
  return (
    <Badge variant={side === "BUY" ? "secondary" : "outline"}>
      <Icon data-icon="inline-start" />
      {side === "BUY" ? "Buy" : "Sell"}
    </Badge>
  )
}

export type ToastContent = {
  title: string
  description?: string
  type: "success" | "error" | "warning" | "info"
}

/** A fill's toast and desktop pop-up (ExecPlan 0047 section 4.6). */
export function toastFor(trade: Trade): ToastContent {
  const what = `${trade.side === "BUY" ? "Bought" : "Sold"} ${formatQuantity(trade.quantity)} BTC at ${formatPrice(trade.price)} USDT`
  if (trade.reason === "STOP_SELL")
    return {
      title: what,
      description: `The run stopped, by ${stopText(trade.stop_reason)}. Fee ${moneyText(trade.fee)}.`,
      type: "warning",
    }
  return {
    title: what,
    description: `${whyText(trade)}. Fee ${moneyText(trade.fee)}.`,
    type: "info",
  }
}
