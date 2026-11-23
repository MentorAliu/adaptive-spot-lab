# Independent risk policy

## Status and authority

The owner delegated an initial proposal. The numbers below are **untested paper-pilot limits selected for bounded experimentation**, not estimates of optimal risk, market probabilities, or guaranteed maximum losses. Show them for one explicit owner approval before an active forward run. Do not ask the owner to invent a profile from scratch, and do not silently treat a model response as approval.

Hard limits are enforced by deterministic engine code using current account state. The agent may choose flat or reduce discretionary exposure within them. Raising limits, expanding the universe, removing an exit rule or changing allowed ranges requires a reviewed version and owner approval. An agent's performance cannot grant it more authority.

**In force from [ExecPlan 0060](../../plans/0060-spot-trading-only.md)'s update: the M12 section that follows.** The sections after it are the earlier profiles, kept as history: M11's futures policies are retired with the futures account, whose records the migration archives in the database (no run's loss history is erased).

## M12: `SPOT_POLICY_V1`, `SPOT_RULE_V1` and `SPOT_COST_V1` (ExecPlan 0060)

IMPLEMENTED from the plan the owner approved on 2026-11-12 ([ExecPlan 0060 §4.1 to §4.3](../../plans/0060-spot-trading-only.md#41-the-rule-spot_rule_v1-code); [DECISIONS](../../DECISIONS.md#2026-11-12--spot-trading-only-execplan-0060-m12)). Three code-owned documents (`app.spot.definitions`) seeded by migration `0041` with their hashes; the spot worker starts only when the stored rows equal the code, and each run records the three hashes as `SYSTEM`. VERIFIED in the engine's tests on a scratch PostgreSQL; OBSERVED on the owner's PC since the install of 2026-11-12: the three stored with the code's hashes and spot run #1 started by `SYSTEM` ([ExecPlan 0060 §14](../../plans/0060-spot-trading-only.md#14-progress)); the rule's first reading, `CASH` for 2026-11-12, came once the daily history's fix was installed. They replace `FUTURES_POLICY_V2` and `MAIN_RULE_V1`: the migration ends a live futures run as `SYSTEM` (`STOPPED`, `NEW_POLICY`) and refuses to run while the futures account is not flat.

| `SPOT_POLICY_V1` | Value |
|---|---|
| Instrument | BTCUSDT spot; the account holds USDT and BTC, long or cash; no borrowing, shorting or leverage (1x by construction) |
| Who decides | `SPOT_RULE_V1`, code, as `SYSTEM`; no model decides, reads or vetoes anything |
| Actions | `RULE_BUY` and `RULE_SELL` (the rule's daily trade), `STOP_SELL` (a stopping run sells everything) |
| Size | The rule's target; a buy at most the free USDT after its fee and slippage; a sell at most the BTC held |
| Latches | Daily loss 2% of the UTC day's reference NAV (due within 5 minutes of midnight; late, the larger of the last valid NAV of the previous 24 hours and the first after midnight), cleared at the next day's reference; drawdown 8% from the run's own high-water NAV. Effect: no buy, sells continue; the drawdown stop makes the run stopping |
| Runs | `RUNNING`, `PAUSED` (a cause open), `STOPPING`, `STOPPED`. The first run starts by itself once the account is funded; a later one is the owner's Start. The owner's Pause, Resume, Stop and sell and Start are requests the engine applies at its next step. A stopping run (the drawdown stop or the owner's Stop and sell) buys nothing, sells the BTC held at once and is stopped once only USDT, or BTC too small to sell, is held |
| Data | A trade needs a book at most 2 s old, the clock verified by the feed and the instrument usable and checked in the last hour; the valuation needs a best bid at most 5 s old. A stale or missing price refuses the trade with its code and invalidates the valuation; nothing is guessed |
| Valuation | `VALUATION_BID_V1`, M3's: the USDT plus the BTC at the best bid, floored to 8 places; every 60 s while BTC that can be sold is held, hourly otherwise, and at each fill, each day's reference, each new high and the first step after a top-up (`ACCOUNT_CHANGE`). Until that step the account's pages show the cash and BTC now at the newest valuation's bid, so a top-up never reads as a loss |
| Dust | BTC whose sale of all of it fails the sale's own minimum quantity or notional check (the notional at the sale's fill price, on the book the step reads; without a book the minimum quantity alone) cannot be sold: it is valued with the holding and counts as nothing held for a sell-all. The other coins' dust left by M3 to M10's sales stays in the holdings with its postings and is not valued (no feed; worth cents) |
| Top-ups | NAV-neutral, at a valid valuation (rule 12) |
| Integrity | A failed reconciliation sets both account flags: no buy, sells continue. The execution worker clears them as `SYSTEM` when a later reconciliation passes (M8's `RECONCILIATION_PASSED`), except when a NAV check failed since the last clear (`nav_cash_only`, `nav_valuation`, and the retired engines' `nav_persisted_valuation` and `nav_futures_valuation`) or no failure is recorded: that latch waits for a fix an update ships |

| `SPOT_RULE_V1` | Value |
|---|---|
| When | Once a UTC day, at the engine's first step at or after 00:05 UTC once the previous day's final daily candle is stored. A day not readable yet, or a refused trade, is tried again every 15 minutes; a fill or a reading that changes nothing spends the day. A run started later in the day reads that day at once |
| Direction | `s` = the mean of the signs of the last complete day's close against the closes 30, 91 and 365 days before it (each the nearest stored day at or before it, within 7 days; else not readable), then `max(s, 0)`: never short |
| Volatility | `σ` = the annualized (365 days) exponentially weighted standard deviation of the daily log returns of the last 365 days, centre of mass 60 days (`var' = (60·var + r²) / 61`, seeded with the first `r²`; a return across missing days counts once); at least 300 days stored |
| Target | `f = max(s, 0) · min(1, 0.05 / σ)` of equity, quantized toward zero to 0.001; below 0.01 it is 0 |
| Acting | `held` = the BTC at the fresh best bid over equity. `f = 0` with BTC held: sell it all. Otherwise, when `|f − held| > 0.03`: buy or sell the difference, `|f − held| · equity / best bid` down to the lot step; else no change. BTC held without a fresh bid: refused (`BID_STALE`) and tried again |
| Gates | A latch, a paused run or an integrity hold: no buy, a sell still sells. A stale or thin book, an unverified clock or an unusable instrument: no trade, refused with its code and tried again |
| Exits | The rule's sells, a stopping run's sale of everything and the owner's Stop and sell; no stop, take-profit or time exit on the holding: its size and the latches protect it |
| Size | 5% a year, by 0059's limit rule: the largest of 40, 30, 20, 15, 10 and 5% whose worst fall from the high on daily lows stays at or below 4%, half the drawdown stop ([0060 §4.2](../../plans/0060-spot-trading-only.md#42-the-size-and-what-history-shows)) |

| `SPOT_COST_V1` | Value |
|---|---|
| Orders | Market only |
| Fill | Walks the ten levels of the newest stored book (asks for a buy, bids for a sell), at most 2 s old; refused `DEPTH_SHORT` when they cannot fill it |
| Slippage | 1 bp of the walked average price against the account (a scenario, not an observation) |
| Fee | 0.10% of the fill's notional, charged in USDT; no BNB discount or promotion (Binance's spot fee page, read on 2026-11-12, updated 2026-01-06: a regular user's rate 0.1%). Binance takes the fee in the asset received; the same value in USDT keeps BTC in whole lot steps |
| Rounding | Fill price to 8 places against the order; quantity down to the lot step; a buy's gross up and a sell's down to 8 places; the fee up to 8 places |
| Filters | `LOT_SIZE` and `MARKET_LOT_SIZE` (a zero market step or minimum adds nothing); `NOTIONAL` minimum and maximum at the fill price; read from the instrument at the trade |

**The backtest** (`SPOT_BACKTEST_V1`, `app.spot.backtest`, labeled `BACKTEST_MODELED_NOT_FILLED`) applies the same three documents on the stored daily candles: the live reading function, a fill at the day's close through the live fill code (the cost's slippage, fee, lot step, minimum quantity and notional), the drawdown stop at the price where the fall from the high reached 8% (the day's open when it opened below), cash for the rest of the window after it, and the daily loss counted without changing a trade (the live trade comes right after the day's reference). It changes nothing in the account.

## Proposed initial profile: PAPER_PILOT_V1

| Setting | Proposed rule |
|---|---|
| Instruments / direction | BTCUSDT and SOLUSDT, and from [M10's update 2](../../DECISIONS.md#2026-10-21--m10-update-2-zec-near-and-xrp-traded-on-paper-execplan-0033) (`AGENT_POLICY_V3`) also ZECUSDT, NEARUSDT and XRPUSDT, all under the same portfolio totals; spot long-only; no borrowed funds |
| Planned per-position entry-to-stop risk | At most 0.25% of current valid equity, including the configured cost reserve |
| Aggregate planned open risk | At most 0.50% of current valid equity, including committed pending entries |
| Per-asset notional | At most 25% of current valid equity, including pending buys |
| Total crypto notional | At most 50% of current valid equity, including pending buys |
| Position multiplicity | One strategy-owned position per symbol; no pyramiding/averaging down initially |
| Daily flow-neutral loss trigger | At least 2% NAV decline from that UTC day's valid opening reference latches an entry pause |
| Global drawdown trigger | At least 8% NAV decline from historical valid high-water NAV latches an entry pause |
| Quote freshness at an execution decision | Required quote age at most 5 seconds, with source/receipt/clock sanity checks |
| Risk-increasing changes | Never automatic; explicit reviewed owner approval |

The quote threshold is an engineering proposal, not a feed guarantee or claim that five seconds is safe for every market. Validate it against observed update behavior and execution fidelity. Market depth needs its own current synchronized state; a fresh best quote does not validate a broken book.

Loss triggers **block new exposure**, not magically guarantee a liquidation or cap loss. Existing protective exits continue according to their original mandate. Show the distinction in the UI. A separate owner-requested emergency flatten command can enqueue exits, but missing liquidity/data may leave positions unresolved.

## Position sizing

For a long candidate with entry reference p, protective stop s < p, valid equity E and approved cost reserve per unit c:

```text
risk_budget <= 0.0025 * E
quantity_from_risk = risk_budget / ((p - s) + c)
allowed_quantity = minimum of:
  quantity_from_risk,
  quantity remaining under aggregate risk,
  quantity remaining under symbol/portfolio notional caps,
  quantity affordable after fee/reservation requirements,
  quantity allowed by approved liquidity/execution constraints
```

Round down to applicable exchange quantity increments and recheck every constraint using the resulting quantity. A nonpositive stop distance, unavailable required cost estimate, invalid equity, insufficient warm-up, or minimum-size failure means no entry. Never manufacture a stop value to fit an order.

Planned stop risk is only a planning quantity. Gaps, execution costs, outages and unrealized changes can exceed it. Track observed exposure and stress scenarios separately. Do not equate an LLM's confidence score with a risk probability or position size.

## Invariants and passive breaches

Caps apply to new/increasing orders. Price changes can create passive notional/risk breaches without a new trade. Record them, block risk-increasing activity, and continue the predeclared position/exit policy. Do not silently force turnover under a new rule. Any automatic de-risking policy beyond the original exits must be separately specified and approved before a run.

Always check the entire portfolio and pending commitments, not strategies in isolation. Exposure in BTC, SOL and the other traded coins is not assumed independent; no invented correlation benefit expands the caps. New funds increase equity only after valid posting and valuation, not while a top-up is pending.

## Loss reference and pause semantics

Daily loss uses unitized NAV, not raw account equity. At the UTC day boundary obtain a valid reference from the continuous valuation stream. If no timely reference exists, preserve the gap and block activation/resume until a documented valid reference is established; do not substitute a convenient later price without recording the limitation. Global high-water NAV persists across days, deposits and restarts.

Daily or drawdown-triggered pauses remain latched through midnight, reconnects and top-ups. Owner resume requires reconciliation, valid data, review of the trigger and any breached policy. An unresolved global drawdown is not cleared by deleting the high-water mark. A separately approved new experiment can define a new evaluation episode, but the old account/experiment loss history remains visible and consolidated reporting cannot erase it.

Model/auth/quota unavailability blocks new AI-required decisions; it does not stop deterministic existing-position protection. Stale valuation, ledger mismatch, lost execution authority, invalid config and exhausted approved operating budgets also fail closed on new exposure.

## Policy testing and changes

Test all exact boundary comparisons, rounding, simultaneous orders, deposits, passive breaches, midnight gaps and restarts. Include a scenario demonstrating that a gapped stop can exceed planned loss; the UI must not mislabel the cap as guaranteed. Changes are immutable versions with rationale, scope and approval. No learning algorithm can write hard-policy settings directly.

## Agent-driven action enforcement

The numeric PAPER_PILOT_V1 ceilings above are unchanged in pack 2.0.0. The expanded decision role does not grant expanded risk. Apply these checks to fixed signals and all agent intents through the same fenced financial path.

Evaluate cumulative exposure including positions, accepted/pending orders, reservations and risk-increasing replacements across the whole portfolio. Many small requests, new IDs, separate agents, different strategy names or concurrent workflows cannot bypass a cap. Treat requested targets as upper bounds, not authority to trade exactly that size. Do not invent proceeds from an unfilled exit to fund a new entry.

Add a versioned **discretionary action policy** covering maximum new entries, gross traded notional/turnover window, per-symbol re-entry/cancel-replace cooldown and repeated-intent deduplication. Its numeric values are UNSET until explicitly declared/tested/approved before AGENT_DRIVEN activation; no false “best” threshold is supplied. Count actual and committed discretionary actions using a deterministic definition and persist counters across restarts and top-ups. Reject or defer excess discretionary work; do not split orders around a counter. Protection/mandatory risk-reducing exits are exempt from discretionary rate/turnover/model-work caps, not from valid holdings, data or idempotency.

**How the M7 engine counts them (ExecPlan 0026 B3, 2026-10-11; `OBSERVED` in tests on a scratch PostgreSQL 16 only).** The values are those of `AGENT_POLICY_V1` (plan §5.2), which the owner approves by hash at the boundary; until then they are proposals. Each count is read in the fenced step from immutable rows of the mode, over the 24 hours before the step's decision time, so it holds across restarts, new runs and top-ups: accepted entries per symbol and in total from the engine's `ACCEPTED` answers to `ENTER` (an accepted entry counts even when its order is later canceled), plus the entries taken earlier in the same step; submissions from every submission of the mode before this one, whatever its action and answer; committed notional as each policy entry order's reservation while it is open and its fills once it is final, plus the policy's exit fills, protective ones included. Re-entry is allowed from the second bar after the bar the symbol's last policy position closed in, the sixth when that close was a protective stop or suppressed one; after an accepted cancellation, not on its bar or the next, where its bar is the newest bar that had closed when the engine answered it (or the bar its intent names, if later), so a cancellation that names an old bar cannot shorten the cooldown. Sizing takes two further upper bounds besides the risk policy's: the requested exposure (the chosen fraction of equity) and the notional left in the window, each at the envelope price and checked again with the rounded quantity. A limit refuses an entry and nothing else: exits and protective exits are never counted against or blocked by one ([plan §18, B3](../plans/0026-m7-agent-driven-main-decisions.md#b3--the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11)).

Model-inferred urgency, evaluator agreement or higher confidence cannot override a check. Review-required drafts bind the exact hash; a revised amount, action, horizon or protection requires a new applicable review and current validation. Quantity rounding/cost buffers and final reservations are computed by code.

A position mandate may authorize discretionary early exit and monotonic tightening of a long stop. Those permitted state updates append history under version checks; they do not rewrite the original mandate. Never move a stop farther away, extend maximum hold, remove protection while replacing it, average down, or change the position owner. Synchronize discretionary and protective exits to prevent overselling.

**How the M7 engine enforces tightening (ExecPlan 0026 B4, 2026-10-11; `OBSERVED` in tests on a scratch PostgreSQL 16 only).** An agent chooses a template the position's terms allow, never a level; the engine computes the level in the step and appends it as a new version only when it is strictly above the stop in force and strictly below the bid of a usable quote, on an open position with a first fill and no exit obligation. The database guard checks the same again. The stop in force (the last update, else the mandate's) is what protection holds a quote against, for quotes whose source time is later than the update; an earlier quote is held against the stop before it, so an update never makes a past price a trigger. Planned open risk, in the breach check, in sizing and in `GET /v1/risk`, is measured to the stop in force. A tightening counts as a submission but no limit refuses it, as for exits, and a protective exit found in the same step comes first ([plan §18, B4](../plans/0026-m7-agent-driven-main-decisions.md#b4--stop-tightening-the-stop-in-force-and-the-trade-lists-exit-label-2026-10-11)).

Revocation invalidates uncommitted intents and cancels remaining cancellable discretionary entries, while reconciling any raced fills and retaining protection. No agent can clear a risk latch or issue an owner approval. Distinguish availability recovery from owner-controlled resume in [AUTONOMY_MATRIX.md](AUTONOMY_MATRIX.md).

## M3 interpretation fields (PROPOSED, not approved)

M3 enforces `PAPER_PILOT_V1` in code (`app/execution/risk.py`) with the interpretation fields below stored in the hashed definition (`execution_definitions`, status `PROPOSED`). They await the owner's M4 approval together with the numbers above; nothing here changes a limit. Rationale and boundary tests: [ExecPlan 0011 §5.7](../plans/0011-paper-broker-reference.md#57-risk-gate-paper_pilot_v1).

- **Equity** is bid-marked (`VALUATION_BID_V1`): USDT cash plus holdings at the best bid of a usable quote, floored to 8 decimals. Invalid equity rejects entries (`VALUATION_INVALID`).
- **Entry reference and envelope:** `p_ref` is the signal bar close; `p_max = ceil_tick(p_ref × (1 + envelope))` from the cost scenario.
- **Cost reserve per unit** `c = p_max·r + s·(r + slip) + tick`; planned risk per unit `(p_max − s) + c`. Open-position planned risk is `net_qty × max(0, avg_cost − s) + net_qty × (s·(r + slip) + tick)`; a pending entry contributes its remaining quantity × its per-unit risk.
- **Order of checks** is fixed (mode/universe/side, activation, latches, authority, reconciliation, data/instrument, valuation, daily reference, cost scenario, warm-up/stop, one position per symbol, passive breach, sizing, rounding, filters, final exact recheck). All comparisons are exact Decimal and inclusive.
- **Late daily reference:** the first valid NAV at or after 00:00 UTC; when it is more than 300 s late it is recorded `LATE_CONSERVATIVE` with value `max(last valid NAV in the prior 24 h, first post-midnight NAV)`. Without today's reference entries defer (`REFERENCE_MISSING`). Only valuations built from quotes fresh at processing time update references, high-water marks and triggers.
- **Latches** are append-only `risk_latches` rows, separate from the funding pause; a new latch cancels pending entries in the same transaction, exits continue, top-ups are allowed, and M3 has no clearing path (owner resume is M4). **Passive breaches** append `STARTED`/`ENDED` events, block new exposure and never force an exit.
- **Transient versus final reasons:** `DATA_STALE`, `INSTRUMENT_INELIGIBLE`, `VALUATION_INVALID`, `REFERENCE_MISSING` and `PASSIVE_BREACH` defer within the signal's 600 s validity window (a new `DEFER` decision is recorded only when the reasons change); latches, reconciliation, `COST_MODEL_UNSET`, stop validity and every sizing/filter rejection are final for the signal.

## M4 latch resolution (owner resume)

A latch row is never deleted or edited. An owner resume names the causes it asks to close. The execution worker closes a cause only in its fenced step, and only when reconciliation reports OK, a fresh valid valuation exists and the cause's rule is met. It then appends a `risk_latch_resolutions` row bound to the latch identities the owner reviewed (a newer latch stays open) and a `RESUME` valuation; otherwise it records `RESUME_REJECTED` with reasons. A resume never closes a cause it was not asked to close.

| Cause | Condition to close |
|---|---|
| `OWNER` | The owner's own pause or flatten; the general conditions above |
| `DAILY_LOSS` | Today's valid reference exists and NAV > 0.98 × that reference |
| `DRAWDOWN` | NAV > 0.92 × the persistent high-water mark ([OD-10](../../DECISIONS.md#2026-09-29--m4-pilot-decisions-execplan-0015)). A flat account cannot recover, so the SYSTEM stops the run (`DRAWDOWN_UNRECOVERABLE`) |
| `APPROVAL_REVOKED` | Every manifest hash is approved again |
| `INTEGRITY` | Never in M4; a separate reviewed repair plan is required |

The high-water mark never falls, and top-ups move neither it nor any latch. Transient blocks (`DATA_STALE`, `VALUATION_INVALID`, `REFERENCE_MISSING`, `PASSIVE_BREACH`, worker not running) are shown but never latched.

## M8 latch clears (ExecPlan 0031, update 2)

From M8's second update the `SYSTEM` closes two causes of the main paper run itself: a `CAUSE_CLOSED` event with actor `SYSTEM` and no request, and for `DAILY_LOSS` a resolution row citing it and the new day's valuation ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#m8-runtime-in-force-records-the-model-table-and-pauses-that-end-execplan-0031)):

| Cause | Cleared by `SYSTEM` when |
|---|---|
| `DAILY_LOSS` | The first reference of a later UTC day is taken on a valid valuation (rule `NEXT_UTC_DAY`). A latch of the same UTC day waits. The resolution row cites the `CAUSE_CLOSED` event |
| `INTEGRITY` | A reconciliation passes with no mismatched order (rule `RECONCILIATION_PASSED`), and every check that failed since the last clear is one a passing run proves repaired; both account flags clear together, and an `INTEGRITY_CLEARED` incident and outbox event are recorded. A latch a NAV check opened (`nav_cash_only`, `nav_persisted_valuation`) is never cleared by `SYSTEM`: those checks read only the newest valuation, and a wrong one may already have moved the high-water NAV or the day's reference, so it waits for a fix an update ships |

A run left `PAUSED` with no cause open and neither account flag set resumes in its next step (`RESUMED`, rule `NO_CAUSE_OPEN`). `OWNER` stays the owner's; `DRAWDOWN` still ends the run; `APPROVAL_REVOKED` keeps the rule above while the owner's approval routes remain as a recovery lever. Limits, the high-water mark and the drawdown stop are unchanged.

## M11: `FUTURES_POLICY_V1` (ExecPlan 0039)

**Retired by [ExecPlan 0060](../../plans/0060-spot-trading-only.md)** with the futures account (history; the M12 section above is in force).

IMPLEMENTED in update 2, part B, from the values the owner approved on 2026-10-23 ([ExecPlan 0039 §5.4](../plans/0039-bitcoin-futures-on-paper.md#54-futures_policy_v1-what-the-agent-may-do-and-how-often); [DECISIONS](../../DECISIONS.md#2026-10-23--m11-approved-bitcoin-futures-on-paper-execplan-0039)). A code-owned document (`app.futures.definitions`) seeded by migration `0020` with its hash; the worker starts only when the stored row equals the code, and each run records the hash as `SYSTEM`. NOT RUN on the owner's PC until the update is installed.

| Setting | Value |
|---|---|
| Instrument | One simulated BTCUSDT perpetual, isolated margin, one-way mode, one position at a time |
| Actions | Enter long, enter short, exit, tighten the stop, hold, abstain; no reversal in one step |
| Leverage | `1` or `2`; 2 is a hard cap in code |
| Risk at the stop | At most 0.25% of equity: the loss of an exit at the stop filled with the slippage scenario against it, with both taker fees (the exit's at the dearer of the stop and that fill) |
| Notional | At most leverage × equity |
| Funding reserve | The free wallet after an entry keeps its exit fee and 1% of the notional (the app's own buffer, not a provider value) |
| Stop | Required: 1.0, 1.5, 2.0 or 3.0 × the 15-minute ATR(14) (Wilder, over the newest contiguous complete 15-minute candles built from final 1m candles, at most 96), rounded to the tick away from the entry |
| Take-profit | Optional: 1, 1.5, 2 or 3 × the stop distance, rounded to the tick toward the entry |
| Longest hold | 1, 4, 12 or 24 hours (the time exit) |
| Liquidation buffer | The stop lies within the first third of the distance from the entry to the liquidation price, or the entry is refused |
| Tightening | The same multiples from the exit-side price, taken only if tighter |
| Day limits | 24 entries and 120 decisions a UTC day |
| Cooldowns | No entry until 2 whole 15-minute bars after the bar of a stop or a liquidation, 1 after any other exit |
| Decision age | A decision over 300 s old when the engine answers it is refused |
| Latches | Daily loss 2% of the UTC day's reference NAV; drawdown 8% from the run's own high-water NAV |
| No agent | No new entry; the open position stays protected by code |

**Sizing in code** (`app.futures.money.size_entry`). The quantity is the largest step that keeps the loss at the stop with both fees and the slippage within the risk, the notional within leverage × equity, the margin, both fees and the reserve within the free wallet, and within the instrument's largest quantity, each bounded at the worst price of the five levels; then the order is filled on the book and every rule is checked again on the actual fill. Refusals: `LEVERAGE_NOT_ALLOWED`, `STOP_MULTIPLE_NOT_ALLOWED`, `TAKE_PROFIT_MULTIPLE_NOT_ALLOWED`, `SIZE_BELOW_MINIMUM`, `DEPTH_SHORT`, `NOTIONAL_BELOW_MINIMUM`, `NOTIONAL_ABOVE_TIER_1`, `STOP_NOT_ABOVE_ZERO`, `TAKE_PROFIT_INVALID`, `RISK_ABOVE_CAP`, `NOTIONAL_ABOVE_CAP`, `MARGIN_UNAVAILABLE` and `STOP_NEAR_LIQUIDATION`.

**Runs and latches.** A run is `RUNNING`, `PAUSED` (a cause open), `STOPPING` (no entries; the position keeps its protection) or `STOPPED`. As M8: `DAILY_LOSS` is cleared by `SYSTEM` when a later UTC day's reference is taken; `INTEGRITY` when reconciliation passes; `OWNER` only by the owner's Resume; `DRAWDOWN` moves the run to `STOPPING`, and it stops once flat. A run's drawdown is measured from its own high-water NAV, which starts at its first NAV and never falls, so a new run the owner starts after a drawdown stop is a new evaluation episode; the account's high-water NAV and every earlier run stay as they were. Top-ups move no high-water mark, reference or latch.

## M11: `FUTURES_POLICY_V2` and `MAIN_RULE_V1` (ExecPlan 0059)

**Retired by [ExecPlan 0060](../../plans/0060-spot-trading-only.md)** with the futures account (history; the M12 section above is in force).

IMPLEMENTED from the plan the owner approved on 2026-11-10 ([ExecPlan 0059 §4.3](../plans/0059-the-slow-rule-trades-the-main-account.md#43-futures_policy_v2-what-changes-in-the-money-path); [DECISIONS](../../DECISIONS.md#2026-11-10--the-slow-rule-trades-the-main-account-execplan-0059)). Two code-owned documents (`app.futures.definitions`) seeded by migration `0040` with their hashes; the futures worker starts only when both stored rows equal the code, and each run records the policy's hash, and the rule's in its start event, as `SYSTEM`. Installed on the owner's PC on 2026-11-10, in force since 17:30:01 UTC (OBSERVED). `FUTURES_POLICY_V1` above stays as it was: the trader's records, the twins and the backtests are read against it, and the trader's code is kept for a rollback by a later update.

`FUTURES_POLICY_V2` is V1 with these changes and no other (a unit test compares every other value):

| Setting | Value |
|---|---|
| Who decides | `MAIN_RULE_V1`, code, as `SYSTEM`; no agent decision is answered: every one is refused `POLICY_CHANGED`, whatever policy it names (the money-path review) |
| Actions | `RULE_ENTRY` (long only), `RULE_RESIZE` (the whole position out, the new size in, in one step), `RULE_EXIT` (to flat) |
| Leverage | `1` only; the cap is 1 |
| The rule's position | No stop, no take-profit, no longest hold and no time exit; its risk is its notional and its cap the target's notional; at 1x long it has no liquidation price |
| A stopping run | The drawdown stop or the owner's Stop (without close) makes the run stopping; the rule's position has no exit of its own but a later reading's, so it exits whole at the next second as `RULE_EXIT`, and the run stops once flat (the money-path review, 2026-11-10). Under V1 the trader's position keeps its stop, take-profit and time exit instead |
| Unchanged | The latches (daily loss 2%, drawdown 8% from the run's high-water NAV) and their effect on the readings (no entry or increase; decreases and exits continue), the owner's Pause, Stop and Stop and close, the funding reserve, the book and staleness rules, `FUTURES_COST_V1`, valuation every 60 seconds, reconciliation |

`MAIN_RULE_V1` reads once a UTC day, at the first finished 15-minute bar (00:15 UTC, a minute after it closes), the stored daily closes of the perpetual:

| Value | Setting |
|---|---|
| Signal | The mean of the signs of the last close against the closes 30, 91 and 365 days before (each within 7 days); never short: its negative part is 0 |
| Volatility | Annualized (365 days) exponentially weighted standard deviation of the daily log returns over the last 365 days, centre of mass 60 days; at least 300 stored days |
| Target | signal × min(1, 0.05 / volatility) of equity, quantized toward zero to 0.001, 0 below 0.01, at most 1 |
| Resize | Only when the target is more than 0.03 of equity from what is held (marked at the bar) |
| Not readable | A missing close, anchor or day: stored `NOT_READABLE` with its reason and read again at the day's next bar; the position stays as it is |
| Refused or owed | A stale quote or mark, an unavailable instrument, a thin book or a size below the minimum is refused with its codes and tried again at the day's next bar; a paused, stopping or integrity-held run refuses an entry or an increase (a decrease's re-entry is stored `OWED` and entered at the day's next bar once the run runs again); an exit always goes |

Every reading is stored once a day in `futures_rule_readings` (append-only; a day is spent by `NO_CHANGE` or `FILLED`), with its features, the rule's id and hash, the outcome and its codes, the exit fill it made and the position it opened.

**The switch.** At the first finished bar at which the trader's run is `RUNNING` with no cause, the account flat, funded and validly valued, `SYSTEM` ends that run (`STOPPED`, `NEW_POLICY`, with a `POLICY_REPLACED` event) and starts the next under `FUTURES_POLICY_V2`; the new run's high-water NAV starts at the switch, as every run's. A trader's position still open keeps its stop, take-profit and time exit and closes by them first. A paused run waits: it is switched at the first finished bar after its causes clear. A stopping or stopped run is not switched: the next run is the owner's Start, as before.

**Protection of the rule's position** (the plan's one point for the review, rule 11): its size (at most 1x; on history at most 16.9% of the wallet), the latches, a stopping run's whole exit at once, the owner's Stop and close, and the daily reading, which exits when the target falls by more than the buffer. A per-trade stop is left out on purpose ([TRADING](../../TRADING.md) principle 8).
