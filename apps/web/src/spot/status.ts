import { formatPercent } from "@/lib/display"
import type { SystemStatus } from "@/system/status.schema"
import { codesText, stopText } from "./parts"
import type { Market, Overview } from "./schemas"

// The Cockpit's status (ExecPlan 0060 section 4.9, after ExecPlan 0035's S2): whether the spot account
// trades, and what needs the owner, worked out from recorded state only. A read that failed is `null`:
// its value is unknown, so the status never says the account trades while one is missing (rule 11); the
// notes still say what the other reads show.

/** Where in Settings the owner acts on a note. */
export type Place = "run" | "rule" | "account" | "health"

export type Note = {
  /** action: only the owner can do it; problem: something is wrong; info: nothing to do. */
  kind: "action" | "problem" | "info"
  text: string
  place?: Place
}

export type TradingState = "trading" | "held" | "stopped" | "unknown"

export type TradingStatus = {
  state: TradingState
  title: string
  notes: Note[]
}

/** The notes in the order the owner reads them: what needs them first, then problems, then the rest. */
export const ORDER: Record<Note["kind"], number> = {
  action: 0,
  problem: 1,
  info: 2,
}

export const TITLE: Record<TradingState, string> = {
  trading: "Trading by itself",
  held: "Buys on hold",
  stopped: "Not trading",
  unknown: "Status unknown",
}

const FEED_TEXT: Record<Market["status"], string> = {
  STARTING: "is starting",
  CONNECTED: "is connected",
  DEGRADED: "is behind",
  UNAVAILABLE: "is down",
}

export type StatusReads = {
  overview: Overview | null
  market: Market | null
  status: SystemStatus | null
}

function percent(fraction: string): string {
  return formatPercent(fraction, { decimals: 0, max: 2 })
}

function listText(items: string[]): string {
  return items.length < 2
    ? items.join("")
    : `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`
}

export function spotStatus(reads: StatusReads): TradingStatus {
  const unread = [
    reads.overview === null && "the account",
    reads.market === null && "the Bitcoin price feed",
    reads.status === null && "the app's health",
  ].filter((item): item is string => typeof item === "string")
  const known = spotNotes(reads)
  if (unread.length === 0) return known
  return {
    state: "unknown",
    title: TITLE.unknown,
    notes: [
      {
        kind: "problem",
        text: `The app could not read ${listText(unread)}. Nothing is guessed; the page reads again by itself.`,
        place: "health",
      },
      ...known.notes,
    ],
  }
}

/** The status from the reads that answered; `spotStatus` makes it unknown while one did not. */
function spotNotes({ overview, market, status }: StatusReads): TradingStatus {
  const notes: Note[] = []
  const done = (state: TradingState): TradingStatus => ({
    state,
    title: TITLE[state],
    notes: notes.sort((a, b) => ORDER[a.kind] - ORDER[b.kind]),
  })
  if (overview === null) return done("unknown")
  if (overview.state !== "READY") {
    notes.push({
      kind: "problem",
      text: "The database is being updated; the account shows once it is done.",
      place: "health",
    })
    return done("unknown")
  }
  const account = overview.account
  const run = overview.run
  let state: TradingState = "trading"

  if (status !== null && status.execution_worker !== "running") {
    notes.push({
      kind: "problem",
      text: "The trading engine is not running, so nothing trades and no limit is checked.",
      place: "health",
    })
    state = "held"
  }
  if (market !== null && market.status !== "CONNECTED") {
    notes.push({
      kind: "problem",
      text: `The Bitcoin price feed ${FEED_TEXT[market.status]}, so trades wait for a fresh order book.`,
      place: "health",
    })
    state = "held"
  }

  if (account === null || !account.initialized) {
    notes.push({
      kind: "info",
      text: "The app adds the starting 10,000 USDT by itself, then the first run starts.",
      place: "account",
    })
    return done("stopped")
  }
  if (account.reconciliation_failed)
    notes.push({
      kind: "problem",
      text: "A reconciliation check of the account failed: buys wait until it passes.",
      place: "health",
    })
  if (account.valuation === "UNAVAILABLE")
    notes.push({
      kind: "problem",
      text: "The account can't be valued now (no fresh Bitcoin price), so the rule waits.",
      place: "health",
    })

  if (run === null) {
    notes.push({
      kind: "info",
      text: "The first run starts by itself within a few seconds.",
      place: "run",
    })
    return done("stopped")
  }
  if (run.state === "STOPPED") {
    notes.push({
      kind: "action",
      text: `Run #${run.seq} was stopped by ${stopText(run.stop_reason)}. Nothing trades until you start a new run.`,
      place: "run",
    })
    return done("stopped")
  }
  if (run.state === "STOPPING") {
    notes.push({
      kind: "info",
      text: `Run #${run.seq} is stopping, by ${stopText(run.stop_reason)}: it sells the Bitcoin at the order book, then stops.`,
      place: "run",
    })
    state = "held"
  }
  const limits = overview.limits
  for (const cause of run.causes) {
    if (cause === "OWNER")
      notes.push({
        kind: "action",
        text: "You paused the run: it buys nothing until you resume. The rule's sells still go through.",
        place: "run",
      })
    else if (cause === "DAILY_LOSS")
      notes.push({
        kind: "info",
        text: `The account fell ${limits ? percent(limits.daily_loss) : "its limit"} today, so it buys nothing until the next UTC day.`,
        place: "rule",
      })
    else if (cause === "DRAWDOWN")
      notes.push({
        kind: "info",
        text: "The drawdown stop tripped: the run sells everything and stops.",
        place: "rule",
      })
    else
      notes.push({
        kind: "problem",
        text: "A reconciliation check failed: buys wait until it passes.",
        place: "health",
      })
  }
  if (run.state === "PAUSED") state = "held"

  const reading = overview.last_reading
  if (
    overview.today?.status === "RETRYING" &&
    reading !== null &&
    reading.utc_date === overview.today.utc_date &&
    !reading.spent
  )
    notes.push({
      kind: "info",
      text:
        reading.outcome === "NOT_READABLE"
          ? `Today's reading waits: ${codesText(reading.reason ? [reading.reason] : [])}. It tries again every ${Math.round(overview.today.retry_seconds / 60)} minutes.`
          : `Today's trade was refused: ${codesText(reading.codes)}. It tries again every ${Math.round(overview.today.retry_seconds / 60)} minutes.`,
    })
  return done(state)
}
