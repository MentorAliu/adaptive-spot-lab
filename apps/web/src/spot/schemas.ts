import { z } from "zod"

// The spot account's reads, the Bitcoin spot market and the owner's run requests (ExecPlan 0060 section
// 4.9; the engine's app/spot/views.py, app/spot_market/views.py and app/spot/requests.py). Every amount
// is the engine's exact decimal string; a fraction (0.0612) is one too.
const time = z.iso.datetime({ offset: true })
const day = z.iso.date()
const decimal = z.string().regex(/^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/)
const signedDecimal = z.string().regex(/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/)
const seq = z.string().regex(/^[0-9]{1,20}$/)
const sha256 = z.string().regex(/^[a-f0-9]{64}$/)
const code = z.string().regex(/^[A-Z][A-Z0-9_]{0,63}$/)
const state = z.enum(["READY", "SCHEMA_PENDING"])

export const definitionRefSchema = z.strictObject({
  id: z.string().regex(/^[A-Z][A-Z0-9_]{0,63}$/),
  sha256,
})
export type DefinitionRef = z.infer<typeof definitionRefSchema>

export const runStateSchema = z.enum([
  "RUNNING",
  "PAUSED",
  "STOPPING",
  "STOPPED",
])
export type RunState = z.infer<typeof runStateSchema>
export const causeSchema = z.enum([
  "OWNER",
  "DAILY_LOSS",
  "DRAWDOWN",
  "INTEGRITY",
])
export type Cause = z.infer<typeof causeSchema>
export const stopReasonSchema = z.enum(["OWNER", "DRAWDOWN"])
export type StopReason = z.infer<typeof stopReasonSchema>
export const sideSchema = z.enum(["BUY", "SELL"])
export type Side = z.infer<typeof sideSchema>
export const tradeReasonSchema = z.enum(["RULE_BUY", "RULE_SELL", "STOP_SELL"])
export type TradeReason = z.infer<typeof tradeReasonSchema>

export const accountSchema = z.strictObject({
  initialized: z.boolean(),
  version: z.number().int(),
  cash: decimal,
  btc: decimal,
  btc_value: decimal.nullable(),
  equity: decimal.nullable(),
  // The share of the account's value held in Bitcoin, at the best bid.
  share: decimal.nullable(),
  bid: decimal.nullable(),
  valued_at: time.nullable(),
  valuation: z.enum(["VALID", "UNAVAILABLE"]),
  units: decimal,
  nav: decimal.nullable(),
  contributions: decimal,
  pnl: signedDecimal.nullable(),
  paused: z.boolean(),
  reconciliation_failed: z.boolean(),
})
export type SpotAccount = z.infer<typeof accountSchema>

// The run against holding Bitcoin, paired by day (ExecPlan 0061): the run's NAV per unit between its first and newest
// timely daily references (the first valuation after a UTC midnight) against Bitcoin's daily closes at those midnights.
export const sinceStartSchema = z.strictObject({
  from_at: time,
  from_price: decimal,
  at: time,
  price: decimal,
  account: signedDecimal,
  bitcoin: signedDecimal,
})
export type SinceStart = z.infer<typeof sinceStartSchema>

export const runSchema = z.strictObject({
  id: z.uuid(),
  seq,
  state: runStateSchema,
  causes: z.array(causeSchema),
  started_at: time,
  started_by: z.enum(["SYSTEM", "OWNER"]),
  start_equity: decimal,
  start_nav: decimal,
  high_water_nav: decimal,
  stopped_at: time.nullable(),
  stop_reason: stopReasonSchema.nullable(),
  version: z.number().int(),
  code_identity: z.string().min(1).max(200),
  rule: definitionRefSchema,
  policy: definitionRefSchema,
  cost: definitionRefSchema,
  since_start: sinceStartSchema.nullable(),
})
export type SpotRun = z.infer<typeof runSchema>

export const anchorSchema = z.strictObject({
  lookback_days: z.number().int().positive(),
  day,
  close: decimal.nullable(),
  sign: z.union([z.literal(-1), z.literal(0), z.literal(1)]),
})
export type Anchor = z.infer<typeof anchorSchema>

export const readingResultSchema = z.enum(["LONG", "CASH", "WARMUP"])
export type ReadingResult = z.infer<typeof readingResultSchema>
export const readingActionSchema = z.enum([
  "BUY",
  "SELL",
  "SELL_ALL",
  "NO_CHANGE",
])
export type ReadingAction = z.infer<typeof readingActionSchema>
export const readingOutcomeSchema = z.enum([
  "NOT_READABLE",
  "NO_CHANGE",
  "FILLED",
  "REFUSED",
])
export type ReadingOutcome = z.infer<typeof readingOutcomeSchema>

export const readingSchema = z.strictObject({
  id: z.uuid(),
  seq,
  run_id: z.uuid(),
  // The UTC day the reading was for, and the day whose close it read (the day before).
  utc_date: day,
  day_read: day,
  at: time,
  result: readingResultSchema,
  reason: z.string().max(64).nullable(),
  close: decimal.nullable(),
  signal: signedDecimal.nullable(),
  volatility: decimal.nullable(),
  target: decimal.nullable(),
  held: decimal.nullable(),
  action: readingActionSchema.nullable(),
  outcome: readingOutcomeSchema,
  codes: z.array(code).max(16),
  spent: z.boolean(),
  anchors: z.array(anchorSchema).max(8),
  up: z.number().int().min(0),
  fill: z
    .strictObject({
      id: z.uuid(),
      side: sideSchema,
      quantity: decimal,
      price: decimal,
      fee: decimal,
      gross: decimal,
    })
    .nullable(),
})
export type Reading = z.infer<typeof readingSchema>

export const overviewSchema = z.strictObject({
  state,
  evaluated_at: time.nullable(),
  account: accountSchema.nullable(),
  run: runSchema.nullable(),
  latches: z.array(
    z.strictObject({
      cause: z.enum(["DAILY_LOSS", "DRAWDOWN"]),
      latched_at: time,
    })
  ),
  limits: z
    .strictObject({
      daily_loss: decimal,
      drawdown: decimal,
      today_change: signedDecimal.nullable(),
      fall_from_high: decimal.nullable(),
    })
    .nullable(),
  today: z
    .strictObject({
      utc_date: day,
      status: z.enum(["WAITING", "DUE", "RETRYING", "SPENT", "NONE"]),
      next_reading_at: time.nullable(),
      retry_seconds: z.number().int().positive(),
    })
    .nullable(),
  last_reading: readingSchema.nullable(),
  fills: z.number().int().min(0),
})
export type Overview = z.infer<typeof overviewSchema>
export type Today = NonNullable<Overview["today"]>
export type Limits = NonNullable<Overview["limits"]>

export const tradeSchema = z.strictObject({
  id: z.uuid(),
  seq,
  run_id: z.uuid(),
  run_seq: seq,
  reason: tradeReasonSchema,
  side: sideSchema,
  quantity: decimal,
  price: decimal,
  average_price: decimal,
  slippage_bps: decimal,
  gross: decimal,
  fee: decimal,
  fee_rate: decimal,
  cash_after: decimal,
  quantity_after: decimal,
  filled_at: time,
  book_second: time,
  stop_reason: stopReasonSchema.nullable(),
  reading: z
    .strictObject({
      utc_date: day,
      target: decimal.nullable(),
      held: decimal.nullable(),
      up: z.number().int().min(0),
      anchors: z.number().int().min(0),
    })
    .nullable(),
})
export type Trade = z.infer<typeof tradeSchema>

export const tradePageSchema = z.strictObject({
  state,
  items: z.array(tradeSchema),
  next_cursor: seq.nullable(),
})
export type TradePage = z.infer<typeof tradePageSchema>

export const readingPageSchema = z.strictObject({
  state,
  items: z.array(readingSchema),
  next_cursor: seq.nullable(),
})
export type ReadingPage = z.infer<typeof readingPageSchema>

export const activitySchema = z.strictObject({
  state,
  cursor: seq,
  count: z.number().int().min(0),
  items: z.array(tradeSchema).max(20),
})
export type Activity = z.infer<typeof activitySchema>

export const markerSchema = z.strictObject({
  id: z.uuid(),
  reason: tradeReasonSchema,
  side: sideSchema,
  quantity: decimal,
  price: decimal,
  filled_at: time,
})
export type Marker = z.infer<typeof markerSchema>
export const markersSchema = z.strictObject({
  state,
  fills: z.array(markerSchema).max(500),
})
export type Markers = z.infer<typeof markersSchema>

export const valuationWindowSchema = z.enum(["24h", "7d", "all"])
export type ValuationWindow = z.infer<typeof valuationWindowSchema>
export const valuationsSchema = z.strictObject({
  state,
  window: valuationWindowSchema,
  bucket_seconds: z.number().int().positive(),
  since: time.nullable(),
  base_nav: decimal.nullable(),
  points: z.array(z.strictObject({ time, nav: decimal, equity: decimal })),
})
export type Valuations = z.infer<typeof valuationsSchema>

// ---- the owner's run requests --------------------------------------------------------------------

export const requestKindSchema = z.enum(["PAUSE", "RESUME", "STOP", "START"])
export type RequestKind = z.infer<typeof requestKindSchema>
export const idempotencyKey = z.string().regex(/^[A-Za-z0-9_-]{8,64}$/)
export const requestInput = z.strictObject({
  kind: requestKindSchema,
  // The run the page showed; a START names none.
  run_id: z.uuid().nullable(),
  idempotency_key: idempotencyKey,
})
export type RequestInput = z.infer<typeof requestInput>
export const requestSchema = z.strictObject({
  id: z.uuid(),
  idempotency_key: idempotencyKey,
  kind: requestKindSchema,
  run_id: z.uuid().nullable(),
  status: z.enum(["PENDING", "APPLIED", "REJECTED"]),
  reasons: z.array(code),
  created_at: time,
  answered_at: time.nullable(),
})
export type SpotRequest = z.infer<typeof requestSchema>

// ---- the definitions in force ----------------------------------------------------------------------

export const definitionsSchema = z.strictObject({
  code_identity: z.string().min(1).max(200),
  rule: definitionRefSchema,
  policy: definitionRefSchema,
  cost: definitionRefSchema,
  // The documents as frozen in migration 0041: plain JSON, read by Settings' words.
  rule_document: z.record(z.string(), z.json()),
  policy_document: z.record(z.string(), z.json()),
  cost_document: z.record(z.string(), z.json()),
})
export type Definitions = z.infer<typeof definitionsSchema>

// ---- the backtest (SPOT_BACKTEST_V1) ---------------------------------------------------------------

export const backtestWindowSchema = z.enum([
  "SINCE_2019",
  "SINCE_2023",
  "LAST_12_MONTHS",
])
export type BacktestWindowKey = z.infer<typeof backtestWindowSchema>

const yearsSchema = z.array(
  z.strictObject({ year: z.number().int(), return: signedDecimal })
)
const summary = {
  final: decimal,
  return: signedDecimal,
  a_year: signedDecimal.nullable(),
  worst_fall: decimal,
  worst_fall_day: day.nullable(),
  fees: decimal,
  years: yearsSchema,
}

export const backtestRuleSchema = z.strictObject({
  ...summary,
  buys: z.number().int().min(0),
  sells: z.number().int().min(0),
  refused: z.number().int().min(0),
  days_in_bitcoin: decimal.nullable(),
  average_held: decimal,
  max_held: decimal,
  stopped: z.strictObject({ day, price: decimal }).nullable(),
  daily_loss_days: z.number().int().min(0),
})
export type BacktestRule = z.infer<typeof backtestRuleSchema>
export const backtestHoldSchema = z.strictObject({
  ...summary,
  bought: z.boolean(),
})
export type BacktestHold = z.infer<typeof backtestHoldSchema>

export const backtestWindowResultSchema = z.strictObject({
  key: backtestWindowSchema,
  first_day: day.nullable(),
  last_day: day.nullable(),
  days: z.number().int().min(0),
  calendar_days: z.number().int().min(0),
  rule: backtestRuleSchema,
  hold: backtestHoldSchema,
})
export type BacktestWindow = z.infer<typeof backtestWindowResultSchema>

export const backtestSchema = z.strictObject({
  state: z.enum(["READY", "NOT_COMPUTED", "SCHEMA_PENDING"]),
  window: backtestWindowSchema,
  computed: z
    .strictObject({
      id: z.uuid(),
      seq,
      computed_at: time,
      method: z.literal("SPOT_BACKTEST_V1"),
      label: z.literal("BACKTEST_MODELED_NOT_FILLED"),
      rule: definitionRefSchema,
      policy: definitionRefSchema,
      cost: definitionRefSchema,
      code_identity: z.string().min(1).max(200),
      candles_sha256: sha256,
      start_cash: decimal,
      data: z.strictObject({
        first_day: day,
        last_day: day,
        days: z.number().int().min(0),
        missing_days: z.number().int().min(0),
      }),
      instrument: z.strictObject({
        step_size: decimal,
        min_qty: decimal,
        max_qty: decimal,
        min_notional: decimal,
        max_notional: decimal.nullable(),
      }),
      windows: z.array(backtestWindowResultSchema),
    })
    .nullable(),
  series: z
    .strictObject({
      days: z.array(z.number().int().min(0)),
      rule: z.array(decimal),
      hold: z.array(decimal),
      target: z.array(decimal.nullable()),
      trades: z.array(
        z.strictObject({
          day_ms: z.number().int().min(0),
          side: sideSchema,
          price: decimal,
          quantity: decimal,
        })
      ),
    })
    .nullable(),
})
export type Backtest = z.infer<typeof backtestSchema>
export type BacktestSeries = NonNullable<Backtest["series"]>

// ---- the Bitcoin spot market -------------------------------------------------------------------------

export const intervalSchema = z.enum(["1m", "5m", "15m", "1h", "4h", "1d"])
export type Interval = z.infer<typeof intervalSchema>
export const INTERVAL_MS: Record<Interval, number> = {
  "1m": 60_000,
  "5m": 300_000,
  "15m": 900_000,
  "1h": 3_600_000,
  "4h": 14_400_000,
  "1d": 86_400_000,
}

const level = z.tuple([decimal, decimal])
export const marketSchema = z.strictObject({
  state,
  symbol: z.literal("BTCUSDT"),
  evaluated_at: time.nullable(),
  status: z.enum(["STARTING", "CONNECTED", "DEGRADED", "UNAVAILABLE"]),
  reason: code.nullable(),
  stream_connected: z.boolean(),
  heartbeat_at: time.nullable(),
  book: z
    .strictObject({
      bid: decimal,
      bid_quantity: decimal,
      ask: decimal,
      ask_quantity: decimal,
      bids: z.array(level).max(20),
      asks: z.array(level).max(20),
      second_at: time,
      received_at: time,
      age_seconds: z.number().min(0),
    })
    .nullable(),
  last_candle_at: time.nullable(),
  clock: z
    .strictObject({
      verified: z.boolean(),
      offset_ms: signedDecimal.nullable(),
      uncertainty_ms: decimal.nullable(),
      checked_at: time.nullable(),
    })
    .nullable(),
  instrument: z
    .strictObject({
      status: z.string().max(32),
      usable: z.boolean(),
      tick_size: decimal,
      step_size: decimal,
      min_quantity: decimal,
      max_quantity: decimal,
      min_notional: decimal,
      max_notional: decimal.nullable(),
      checked_at: time.nullable(),
    })
    .nullable(),
  daily: z
    .strictObject({
      days: z.number().int().min(0),
      first_day: day.nullable(),
      last_day: day.nullable(),
      checked_at: time.nullable(),
    })
    .nullable(),
  history_checked_at: time.nullable(),
  labels: z.array(code),
})
export type Market = z.infer<typeof marketSchema>

export const candleSchema = z.strictObject({
  open_ms: z.number().int().min(0),
  open: decimal,
  high: decimal,
  low: decimal,
  close: decimal,
  volume: decimal,
  minutes: z.number().int().min(0),
  expected_minutes: z.number().int().positive(),
  complete: z.boolean(),
})
export type Candle = z.infer<typeof candleSchema>
export const candlesSchema = z.strictObject({
  state,
  symbol: z.literal("BTCUSDT"),
  interval: intervalSchema,
  evaluated_at: time.nullable(),
  candles: z.array(candleSchema).max(1000),
  labels: z.array(code),
})
export type Candles = z.infer<typeof candlesSchema>
