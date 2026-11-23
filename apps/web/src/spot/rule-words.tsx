import { useQuery } from "@tanstack/react-query"
import {
  CalendarClock,
  Fingerprint,
  Gauge,
  Receipt,
  Scale,
  ShieldAlert,
  TrendingUp,
  Turtle,
} from "lucide-react"
import { LoadingRows, ReadError } from "@/components/page-parts"
import { shortHash } from "@/components/request-outcome"
import { Card, CardContent } from "@/components/ui/card"
import { formatPercent } from "@/lib/display"
import { SettingRow, SettingsList } from "@/settings/parts"
import { definitionsQuery } from "./spot.query"
import type { Definitions } from "./schemas"

// Settings' "Rule and limits" (ExecPlan 0060 section 4.9): the rule, its limits and its costs in words,
// written from the definitions the installed code put in force, so the words change only with them. A
// value a later version no longer has is left out of its sentence, not guessed.

type Document = Record<string, unknown>

/** A document's value at `path` as text, or null when it is not a plain string or number. */
export function valueAt(document: Document, ...path: string[]): string | null {
  let value: unknown = document
  for (const key of path) {
    if (value === null || typeof value !== "object" || Array.isArray(value))
      return null
    value = (value as Document)[key]
  }
  if (typeof value === "string" && value.length > 0) return value
  if (typeof value === "number" && Number.isFinite(value)) return String(value)
  return null
}

/** A document's number at `key`, or NaN when it has none (`Number(null)` would be 0). */
function numberAt(document: Document, key: string): number {
  const value = valueAt(document, key)
  return value === null ? Number.NaN : Number(value)
}

function numbersAt(document: Document, key: string): number[] {
  const value = document[key]
  return Array.isArray(value)
    ? value.filter((item): item is number => Number.isInteger(item))
    : []
}

function percent(fraction: string | null, fallback: string): string {
  return fraction === null
    ? fallback
    : formatPercent(fraction, { decimals: 0, max: 2 })
}

function list(items: string[]): string {
  return items.length <= 1
    ? (items[0] ?? "")
    : `${items.slice(0, -1).join(", ")} and ${items[items.length - 1]}`
}

/** The rule, the limits and the costs in sentences, from the documents in force. */
export function ruleWords(definitions: Definitions) {
  const rule = definitions.rule_document
  const policy = definitions.policy_document
  const cost = definitions.cost_document
  const lookbacks = numbersAt(rule, "lookback_days")
  const after = numberAt(rule, "read_after_ms")
  const retry = numberAt(rule, "retry_seconds")
  const readAt = Number.isFinite(after)
    ? `00:${String(Math.round(after / 60_000)).padStart(2, "0")} UTC`
    : "midnight UTC"
  const fee = valueAt(cost, "taker_fee_rate")
  const slippage = valueAt(cost, "slippage", "adverse_bps")
  const levels = valueAt(cost, "book", "levels")
  return {
    when: `Once a UTC day, just after ${readAt}, it reads the last complete day's close${Number.isFinite(retry) ? `; a day it cannot trade yet is tried again every ${Math.round(retry / 60)} minutes` : ""}.`,
    trend: `It compares that close with ${lookbacks.length > 0 ? `the closes ${list(lookbacks.map(String))} days before` : "earlier closes"}. It holds Bitcoin only while the close is above more of them than below, and never borrows or sells short.`,
    size: `The share it holds aims for the account to swing about ${percent(valueAt(rule, "volatility_target"), "a set amount")} a year: the more of those closes it is above and the calmer Bitcoin has been, the larger the share, up to all of the account.`,
    trade: `It buys or sells the difference only when its target is more than ${percent(valueAt(rule, "rebalance_buffer"), "a set margin")} of the account away from what is held; a target of nothing sells everything.`,
    dailyLoss: `When the account falls ${percent(valueAt(policy, "daily_loss_fraction"), "its limit")} below the UTC day's reference value, it buys nothing more that day; sells still go through, and the limit clears at the next day's reference.`,
    drawdown: `When the account falls ${percent(valueAt(policy, "drawdown_fraction"), "its limit")} below the run's high, the run sells everything at once and stops. Only you can start a new one.`,
    costs: `Market orders priced from ${levels === null ? "the order book" : `the top ${levels} levels of the order book`}${slippage === null ? "" : `, ${slippage} basis point${slippage === "1" ? "" : "s"} of slippage against each`}${fee === null ? "" : `, and a ${percent(fee, "set")} fee`}, paid in USDT.`,
  }
}

export function RuleSettings() {
  const definitions = useQuery(definitionsQuery)
  if (definitions.isPending)
    return <LoadingRows label="Loading the rule in force" />
  if (definitions.isError) return <ReadError what="The rule in force" />
  const words = ruleWords(definitions.data)
  const data = definitions.data
  return (
    <Card>
      <CardContent>
        <SettingsList label="The rule and its limits">
          <SettingRow
            icon={Turtle}
            title="Who trades"
            description="The rule, in code: no person and no AI decides a trade."
          />
          <SettingRow
            icon={CalendarClock}
            title="When"
            description={words.when}
          />
          <SettingRow
            icon={TrendingUp}
            title="Trend"
            description={words.trend}
          />
          <SettingRow icon={Scale} title="Size" description={words.size} />
          <SettingRow icon={Gauge} title="Trades" description={words.trade} />
          <SettingRow
            icon={ShieldAlert}
            title="Daily loss limit"
            description={words.dailyLoss}
          />
          <SettingRow
            icon={ShieldAlert}
            title="Drawdown stop"
            description={words.drawdown}
          />
          <SettingRow icon={Receipt} title="Costs" description={words.costs} />
          <SettingRow
            icon={Fingerprint}
            title="In force"
            description={`${data.rule.id} ${shortHash(data.rule.sha256)} · ${data.policy.id} ${shortHash(data.policy.sha256)} · ${data.cost.id} ${shortHash(data.cost.sha256)}`}
          />
        </SettingsList>
      </CardContent>
    </Card>
  )
}
