# ExecPlan 0059 — The slow rule trades the main account

**Status: APPROVED by the owner on 2026-11-10 at 15:05:57 UTC, on the thread's card "Approve the plan for the slow rule to trade the main account?": "Approve the plan", which the thread recommended.** Written in the project thread "Plan the slow rule for the main account" (first "Find another profitable strategy to add") after the owner's pick of 2026-11-10 14:35:46 UTC on the thread's card "Add another strategy to the app now, or leave it as it is?": "Plan the slow rule for the main account", whose text read "I write a plan for the slow rule, in spot and never short, to trade the main account instead of the AI trader. That ends the trader's running test." The thread had recommended "Add nothing now" ([DECISIONS](../../DECISIONS.md#2026-11-10--the-slow-rule-trades-the-main-account-execplan-0059)). The approved card read "I merge the plan and build it. It reaches the app in one update after the ChatGPT backtest ends (about 15 Nov) and the new trader update is installed." Nothing is built yet: the build follows in its own pull request with the independent review of §9, and its install waits for §9's conditions. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)).

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `CALCULATED` (the thread's arithmetic, assumptions stated), `NOT RUN`.

## 1. Goal

The owner asked on 2026-11-10 at 11:42 UTC for "a good profitable strategy that the app doesn't have yet, spot or futures". The thread checked three new candidates offline and none passed (§4.7); its by-product was that the app's own slow trend rule ([ExecPlan 0057](0057-a-slow-trend-twin.md)), held never short, kept more of its gain where no funding is paid. The owner chose to plan that rule for the main account instead of the AI trader.

Observable outcome, after one update:
1. The main account holds Bitcoin's perpetual long or not at all, once a UTC day, by `MAIN_RULE_V1` (§4.1): the slow trend twin's signal and volatility, never short, sized to a 5% a year volatility target (§4.2), at most 1x; code decides, no model.
2. The AI trader (generation 19 or whichever is installed then), the trade reviewer, the daily decision reviewer and the coach stop being asked; their code stays (§4.4).
3. The account's latches stay as they are: a 2% daily loss and an 8% fall from the run's high-water NAV stop new entries; the owner's Pause, Stop and Stop-and-close work as before (§4.3).
4. Home, Trades, Decisions and Settings say that the main account follows the slow rule and show each daily reading (§4.5).
5. The twins, the veto twin and the league table keep running as yardsticks; the measure of §4.6 is written here before the first reading.

## 2. What the app has

`VERIFIED` on `main` at `65dd372` (2026-11-10):
- The main account is the futures account of [ExecPlan 0039](0039-bitcoin-futures-on-paper.md): `FUTURES_POLICY_V1` and `FUTURES_COST_V1` (`app.futures.definitions`), one position at a time, entered only on an agent's `ENTER_LONG` or `ENTER_SHORT` decision (`app.futures.engine.Step.enter`) sized by `money.size_entry` to lose at most 0.25% of equity at a stop of 1 to 3 × the 15-minute ATR; `futures_positions` requires a stop, a stop multiple, a maximum hold of 1 to 24 hours and a time exit (migration `0020`). The engine protects every position each second, posts every amount through `app.futures.ledger`, and starts the first run by itself; "any later one needs the owner" (`Step.auto_start`).
- `TREND_SLOW` (`TWIN_SET_V3`, migration `0038`, [ExecPlan 0057](0057-a-slow-trend-twin.md)) runs the slow rule on an isolated twin account: `app.futures.twins.slow_trend` reads the stored daily closes (`perp_daily_bars`, which `asl_execution` may select) and returns the signal, the volatility, the target and the wanted action in exact Decimal; `twins.size_whole` sizes a target fraction of equity on the book; the twin step resizes as a whole exit and a whole entry, retries a resize whole at the day's next bar, and owes an entry refused after its exit (`app.futures.twin_engine`).
- The agents' worker asks the trader on its schedule (`app.agents.futures_schedule`), then the trade reviewer, the coach and the daily decision reviewer; the veto agent answers `TREND_VETO`'s held entries.
- [ExecPlan 0052](0052-backtest-the-ai-trader-on-history.md)'s ChatGPT backtest is still running (its end `CALCULATED` about 2026-11-15); a change to the futures context, the money rules, the policy, the costs or the twins would stop it at its next restart, so such a change waits until the run ends ([0052 §13](0052-backtest-the-ai-trader-on-history.md#13-decision-log), the first steps' tripwire). [ExecPlan 0058](0058-the-event-calendar.md) (generation 19) was merged on 2026-11-09; its install was pending when this plan was written.

## 3. Scope

In: `MAIN_RULE_V1` and `FUTURES_POLICY_V2` (definitions seeded with their hashes, as V1); the engine's daily rule step on the main account; the switch from the trader to the rule (§4.4); migration `0040` (the definitions, positions without a stop or time exit when the rule opened them, the daily readings); the agents' worker not asking the trader, the reviewers or the coach while V2 is in force; the pages' texts and one reading card; the contracts (§5); the measure. One update, after the conditions of §9.

Out: spot (§4.8); shorts; leverage above 1; a stop, take profit or time exit on the rule's position; any change to the latches, `FUTURES_COST_V1`, the twins, the veto twin, the scorer's past rows, the backtests' code or the replay; removing the trader's code; partial resizes (a resize stays a whole exit and entry, as the twin's); the ten-coin, cross-coin and carry ideas the thread checked (§4.7, [the ideas note](../../ideas/strategies-checked-2026-11-10.md)). No new host, dependency, secret or model call.

## 4. Design

### 4.1 The rule `MAIN_RULE_V1` (code)

0057's rule, with three changes, each `PROPOSED` and fixed here before the first reading: never short (0057's pre-registered second trial, T2), at most 1x, and the size of §4.2.

| Part | Rule | From |
|---|---|---|
| When | At the first finished 15-minute bar of each UTC day, on the main account, from the day after the switch (§4.4); a day not readable yet is read again at the day's next bar | 0057 §4.1 |
| The direction | `s` = the mean of the signs of the last complete day's close against the closes 30, 91 and 365 days before it (`twins.slow_trend`, unchanged), then `max(s, 0)`: never short | TR-03; 0057's T2 |
| The volatility | `σ` as 0057: the annualized exponentially weighted standard deviation of daily log returns, centre of mass 60 days, at least 300 of the 366 days stored | TR-01 |
| The target | `f = max(s, 0) · min(1, 0.05 / σ)`, quantized toward zero to 0.001; flat when `f` is below 0.01 or its notional below the instrument's minimum | §4.2 |
| Acting | `held` = the open position's notional at the fresh mark over equity. When `|f − held| > 0.03`: the position exits whole (`RULE_RESIZE` or `RULE_EXIT`) and, when `f > 0`, the target enters whole in the same step (`RULE_ENTRY`); else nothing. An exit that cannot fill is tried whole at the day's next bar; an entry refused after its exit filled is owed at the day's next bars, as the twin's | 0057 §4.1 and §13 |
| Size | Notional = `f` × equity at the fill, leverage 1, margin the notional; the entry fee, the exit fee with the slippage and the policy's funding reserve within the free wallet (`twins.size_whole` with the fraction) | 0057 §4.4 |
| Exits | Only the rule's resize or exit, the owner's Stop-and-close, or a liquidation (none can happen at 1x long: the long's liquidation price is not above zero, `FUTURES_COST_V1`) | §4.3 |
| Costs | `FUTURES_COST_V1` unchanged: both taker fees, 1 bp of slippage, funding paid and received every 8 hours | 0039 §5.3 |

Each reading is stored (§4.4) with the day, its close, the three anchors, `s`, `σ`, `f`, `held` and the action, so every day can be recomputed from the stored candles.

### 4.2 The size: 5% a year, chosen by the account's limit

The main account keeps its drawdown stop: new entries stop when the account falls 8% from the run's high-water NAV, and only the owner starts a new run then (AGENTS.md rule 14). The twin's 40% target fell 25% (2021 to 2026, intraday) and would have hit that stop again and again. The size is therefore chosen by the limit, by a rule written in the thread before the sizing run (`sizing2.py`, its docstring): **the largest of 40, 30, 20, 15, 10 and 5% a year whose worst fall from the high-water NAV, counted on each day's intraday low, stays at or below 4% (half the drawdown stop) over 2021-01-01 to 2026-10-31.** Half, so that a fall twice as deep as the worst of six years still stops short of the latch. A larger target made more money in every window seen, so this rule can only pick by the limit, never by the return.

`CALCULATED` (`BACKTEST_MODELED_NOT_FILLED`, never-short arm on the perpetual, whole resizes, fills at the daily close; files in the project's shared folder `next-strategy/`):

| Target | Worst fall, intraday | Ended at, from 10,000 on 2021-01-01 | A year |
|---|---|---|---|
| 40% | 25.1% (2022-11-09) | 21,355 | 13.9% |
| 20% | 13.5% | 15,484 | 7.8% |
| 10% | 6.8% (2022-11-09) | 12,675 | 4.2% |
| **5%** | **3.4%** | **11,301** | **2.1%** |

The rule picks 5%. With the plan's exact values (the quantization, the flat band and the 0.03 buffer of §4.1; `plan_numbers.py`), from 10,000 on 2021-01-01 to 2026-10-31: 11,245 (2.0% a year, volatility 2.9%, Sharpe 0.70), worst fall 3.4% intraday, worst day −1.2%, 136 resizes (about two a month), fees 93 and funding 392, Bitcoin held on 79% of days at 3.9% of the wallet on average and 16.9% at most. By year: 2021 +1.9%, 2022 −1.2%, 2023 +4.4%, 2024 +6.5%, 2025 +0.4%, 2026 to October +0.1%. Started on 2023-01-01: 11,252; on 2024-01-01: 10,706; on 2025-01-01: 10,049. At 5 bp of slippage: 11,180. September and October 2026 (the AI backtests' window): +0.25%.

Read plainly: inside the account's limits the rule is small. It holds a few percent of the money in Bitcoin and made about 2% a year on history, with a worst fall of about 3%, where holding Bitcoin fell 69% (2022). The 10% target (4% a year, worst fall 6.8%) is not chosen: it came within 1.2 points of the stop. The limit is not loosened ([TRADING](../../TRADING.md#what-not-to-propose)).

### 4.3 `FUTURES_POLICY_V2`: what changes in the money path

`FUTURES_POLICY_V2` is V1 with:
- `decider`: `MAIN_RULE_V1` (code, `SYSTEM`); no agent decision is answered (an agent decision left over is refused `POLICY_CHANGED`, as today).
- actions: `RULE_ENTRY` (long only), `RULE_RESIZE`, `RULE_EXIT`; leverage 1; positions 1.
- the rule's position has no stop, no take profit, no maximum hold and no time exit; its risk is its notional (the whole of it at 1x long), and its cap is the target's notional; migration `0040` lets `futures_positions` hold such a row only when its `opened_by` is `RULE` (a database check), and every agent-opened row keeps today's checks.
- unchanged: the latches (2% daily loss, 8% from the run's high-water NAV, their effect: no entry, exits and protection continue), the owner's Pause, Stop and Stop-and-close, the funding reserve, the book and staleness rules, `FUTURES_COST_V1`, valuation every 60 seconds, reconciliation.

Protection of the rule's position: its size (at most 1x; on history at most 16.9% of the wallet, so from a new high a fall of 47% in Bitcoin before the next reading would be needed to reach the 8% stop), the latches, liquidation (unreachable at 1x long) and the owner's Stop-and-close. A per-trade stop is left out on purpose: on a slow trend a stop mostly sells noise (TRADING principle 8, TR-12), and the twin's history has none. This is the one point the independent review must judge against rule 11 (§9).

The engine's step gains one phase after the latches and the run's state, `rule()`, at the first finished 15-minute bar of each UTC day: read the stored daily closes, call `twins.slow_trend` with `MAIN_RULE_V1`'s values, apply `max(s, 0)` and the cap, store the reading, and act through the same `close` and a new `enter_fraction` that use `money` and `ledger` as `Step.enter` does (the fills, the margin reservation, the fee, the account version), refused under a latch, a stale quote or mark, a thin book, an integrity fault or a paused or stopped run, each refusal noted with its reason and tried again at the day's next bar.

### 4.4 The switch from the trader to the rule

- **At the install:** the agents' worker stops asking the trader, the trade reviewer, the daily decision reviewer and the coach (they are asked only while `FUTURES_POLICY_V1` is in force); the veto agent keeps answering `TREND_VETO`. An open position keeps its stop, take profit and time exit (24 hours at most) and closes by them; no forced exit.
- **At the first 00:15 UTC bar with the account flat:** `SYSTEM` ends the running run (`POLICY_REPLACED`) and starts the next under `FUTURES_POLICY_V2` and `MAIN_RULE_V1`, recording both hashes, and the rule reads its first day. If the run is latched by the drawdown stop then, the switch waits for the owner's new run (rule 14). The new run's high-water NAV starts at the switch, as every run's.
- **Readings:** a table `futures_rule_readings` (migration `0040`), one row per UTC day: the reading's features, the action, the outcome (`FILLED`, `NO_CHANGE`, `REFUSED` with its codes, `OWED`), the fills; append-only.
- **What keeps running:** the six twins, the veto twin and its placebo, the league table (each twin against the main account, paired by day), the feed, the daily candles, the BLS calendar's fetch. The scorecard, the result checks, the trade reviews and the coach's notes keep their history and add nothing; the Decisions page shows the readings instead of new calls.
- **Generation 19's measure** ([0058 §4.6](0058-the-event-calendar.md#46-the-measure-pre-registered)) ends at the install short of its sample and is read descriptively over its days, as 0053's was. The 2026-11-16 reading of generation 11 is read-only on past days and unaffected. The trader bundle planned after that reading is superseded while this plan is in force.

### 4.5 The pages

Home: the status pill says "Slow rule"; the trader's latest-call card becomes the day's reading (the signal in thirds, the volatility, the target and held as percentages of the wallet, the action); the open position shows no stop line. Trades: the rule's trades with "Daily resize" or "Rule exit", no stop and no R. Decisions: the daily readings in a table; the scorecard and the coach's last note under "Before 2026-11-…" with their history. Settings: the agents' card says the trader and its reviewers are off while the main account follows the slow rule; the veto agent stays listed. The shadcn skill is loaded for the web change; no new page, section or component, only existing primitives and the generated API types.

### 4.6 The measure, pre-registered

- **M1, the money:** the main account's daily log return under V2 against cash, stationary bootstrap (mean block 3 days, 10,000 resamples), 95%: `MAKES_MONEY`, `LOSES_MONEY` or `UNCLEAR`; too few under 90 days; read by the weekly review from 90 days, then quarterly. Expected `UNCLEAR` for years (`CALCULATED`: 2% a year at a volatility of about 3% is a Sharpe near 0.7, which needs about eight years to reach t = 2, TR-35).
- **M2, the limit:** the run's worst fall from its high-water NAV, read weekly. Above 4% is a design breach the weekly review reports with a card; the 8% stop still acts in code whatever it reads.
- **M3, the implementation:** each reading equals `slow_trend` recomputed on the stored candles of that day (code's test, and the weekly review on the PC's rows); each fill's notional within the instrument's step of `f` × equity.
- Descriptive, beside: the account against `HOLD` and against `TREND_SLOW`, paired by day, by the league's rule.

Trial ledger: no new signal trial. The never-short arm is 0057's pre-registered T2 (with T1 live as the twin and today's three checks, five trials of the slow-rule family); the size is set by the limit, not by a result. Nothing changes from a verdict without an update the owner installs.

### 4.7 The thread's offline check (`CALCULATED`, `BACKTEST_MODELED_NOT_FILLED`)

Written in the thread on 2026-11-10 before any number (`next-strategy/SPEC.md`, 11:50 UTC), on Binance's public archive downloaded on the owner's PC (1d candles and funding rates, 2020-01 to 2026-10, 1,758 files, every SHA-256 matching), daily-close fills, both taker fees, 1 bp of slippage, actual funding. From 10,000 on 2022-01-01 to 2026-10-31, against the slow rule on Bitcoin alone never short (20,815):
- the slow rule over the ten perpetuals most traded in late 2021 (fixed by volume, one of them LUNA), never short: 12,205, paired against Bitcoin alone −11% a year (`UNCLEAR` at block 3, `WORSE` at block 20); long or short: 15,327, `UNCLEAR`;
- the three strongest coins long against the three weakest short, weekly: 24,762 on the registered weekday, but 5,087 to 20,609 when the reshuffle falls on any of the six other days (`UNCLEAR`); it needs shorts on other coins;
- carry (a calculation): Bitcoin's funding paid a hedged short 6.6% a year on the hedged amount (3.5% in the last 365 days); it needs a spot leg.

None passed. The full record is the [ideas note](../../ideas/strategies-checked-2026-11-10.md) and the shared folder `next-strategy/`.

### 4.8 Futures, not spot

The card said spot. The plan keeps the main account on the perpetual:
- at the size of §4.2 spot would have ended at 11,585 against 11,245 from 2021 (`CALCULATED`, about 0.5% a year: the perpetual pays about 390 of funding while long, spot pays about 80 more in fees at its 0.10% taker rate, `NOT VERIFIED` on Binance's spot fee page);
- spot needs rule 1 changed, a spot feed, a spot money path with its own reconciliation and its independent review, and moving the account: several updates over weeks, against one update here;
- the owner chose "Keep futures" on 2026-11-05 at 11:47 UTC in the read-only project thread "Decide whether to switch back to spot" (for the trader then; not entered in DECISIONS, since nothing changed).

Spot stays a follow-up in the ideas note, worth its build only if the rule runs for long and the funding it pays shows on the account.

### 4.9 The trading review ([TRADING.md](../../TRADING.md#how-to-judge-a-trading-change)'s eight questions)

1. **Rules:** paper only; code decides every entry, size and exit; no model; leverage lowered to 1 and shorts removed for the main account; the latches unchanged. The rule's position has no per-trade stop (§4.3): it is a different rule installed by the owner, not a stop loosened on an open position, and the independent review judges it. Passes, with that point for the review.
2. **Costs:** about two resizes a month at a few percent of the wallet: fees about 16 and funding about 68 a year on 10,000 (`CALCULATED`); the gain of §4.2 is after both.
3. **Horizon:** signals of 1 to 12 months, holds of weeks: where the evidence is (principle 4).
4. **The model's place:** none on the main account; the veto agent stays on its twin.
5. **The yardstick:** cash and the 4% limit (§4.6), with `HOLD` and `TREND_SLOW` beside; "too few", then `UNCLEAR`, said in advance.
6. **Pre-registration:** §4.1, §4.2's choice rule (written before the sizing run) and §4.6, before the first reading.
7. **The trial ledger:** no new signal trial (§4.6); the trader's ledger closes at nine variants.
8. **The clock and the cost:** the trader's test ends at the install (the owner's pick said so); model calls fall from about 8 to 9 a day plus reviews to the veto's few a week; no tokens for the main account; a readable M1 takes years.

## 5. Authority

- `MAIN_RULE_V1` and `FUTURES_POLICY_V2` are `SYSTEM`'s, frozen in migration `0040`; nobody changes them at run time; a new version is an update the owner installs ([AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md)).
- Contracts changed by the build, before or with its code: [AGENTS.md](../../../AGENTS.md)'s mission line ("an agent-driven paper-trading application" becomes one whose main account follows the rule the installed policy names, the agents reading and testing beside it) and rule 3 (agents propose trade actions only where the installed policy names an agent as the decider); [RISK_POLICY](../../RISK_POLICY.md) (`FUTURES_POLICY_V2`, `MAIN_RULE_V1`); [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md) (the main account's rows: `SYSTEM` decides under V2, the trader's row in force under V1 only); [RUNTIME_AGENTS](../RUNTIME_AGENTS.md); [TRADING](../../TRADING.md) ("What the trader does today"); [ROADMAP](../../ROADMAP.md) M11; STATUS. Rule 1 is unchanged: the main account still trades the one simulated BTCUSDT perpetual, within its leverage.
- Rule 13's money-path review: the main account's entries, exits and positions change, so an independent review reads the build before its merge.

## 6. Requirements and tests

| ID | Requirement | Test (`PROPOSED`) |
|---|---|---|
| R1 | The reading equals `slow_trend` with `MAIN_RULE_V1`'s values on fixed closes; never short; at most 1x; the quantization, flat band and buffer as §4.1 | unit, `tests/test_m11_main_rule_unit.py` |
| R2 | A resize exits whole and enters whole in one step; an exit that cannot fill is retried whole; an owed entry is entered at the day's next bars | scratch database, the engine step on fixtures |
| R3 | A latch, a paused or stopped run, a stale quote or mark, a thin book or an integrity fault refuses the entry and keeps exits and protection | scratch database |
| R4 | The ledger: each rule fill posts the fee, the margin, the realized P&L and funding as today; reconciliation `OK`; a top-up stays NAV-neutral | scratch database, the existing ledger and reconciliation suites on rule fills |
| R5 | `futures_positions` refuses a row without a stop unless `opened_by = 'RULE'`; an agent-opened row keeps every check | migration `0040` tests and its downgrade |
| R6 | The switch: no new trader decision after the install; the open position closes by its own exits; the next run starts under V2 at the first flat 00:15 UTC bar; a latched run waits for the owner | scratch database with a clock |
| R7 | The agents' worker asks no trader, reviewer or coach under V2 and still answers the veto twin | agent worker unit tests |
| R8 | The pages show the reading and the rule's trades; no stop line; the agents' card | Vitest and the browser chain |

## 7. Official sources

No new provider fact: the perpetual's fees, funding, liquidation and instrument rules are `FUTURES_COST_V1`'s, read on 2026-10-24 ([0039 §7](0039-bitcoin-futures-on-paper.md#7-official-sources)). The rule's sources are TR-01, TR-03, TR-10 and TR-12; the thread's two new sources are TR-38 and TR-39 in [REFERENCES](../../REFERENCES.md#trading-research--2026-11-01-and-2026-11-02).

## 8. Data and trust boundaries

The engine reads `perp_daily_bars` (granted to `asl_execution` by `0038`); it writes `futures_rule_readings` and the existing futures tables only. No agent reads the readings. No new host, secret or credential; nothing of the agents' runtime changes except who is asked.

## 9. Implementation sequence

1. The owner approves this plan (its card); the contracts of §5 change in the build's pull request with the code.
2. Build in the cloud: the definitions, migration `0040`, the engine's rule phase and switch, the worker's schedule, the pages, the tests of §6.
3. An independent review of the money path (rule 13), with §4.3's missing stop as its named question.
4. Merge and one update, only when (a) ExecPlan 0052's ChatGPT backtest has ended, (b) generation 19's update is installed and checked, and (c) no other update waits: the owner's double-click of `update-app.cmd`.
5. The thread checks the install read-only on the PC: the definitions' hashes, the trader not asked, the switch, the first reading and its fills.

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL (the new suite, the futures and twin suites, the agent worker's, the whole engine suite), the web checks (lint, types, Prettier, Vitest, build, `api:check`), the browser chain and the link check. `NOT RUN` in the cloud: the Docker build, the update, real readings on the PC.

## 11. Failure and rollback

- The daily candles are missing: the day is not readable and is read again at the next bar; Home says so; the position stays as it is.
- The rule loses: M1 `LOSES_MONEY` or M2's breach goes to the owner on a card; nothing changes by itself.
- **Rollback:** an update that installs `FUTURES_POLICY_V1` with a trader generation again (the trader's code is kept for this); the switch runs the other way at a flat 00:15 UTC bar. Migration `0040`'s downgrade refuses once a rule reading or a rule position exists: a rollback goes forward.

## 12. Q01–Q10

Q01, Q02: Home's reading card, Trades' labels, Decisions' table, Settings' agents card; no new page (R8). Q03: R1 to R8. Q04: no new secret or host. Q05: §11. Q06: one indexed read of about 400 daily rows once a day. Q07: the cloud suites. Q08: each refusal's codes on the reading; the switch as a run event. Q09: migration `0040` and its downgrade; the update's backup. Q10: the contracts of §5; no new dependency.

## 13. Decision log

- 2026-11-10, the owner: the card's "Plan the slow rule for the main account" (14:35:46 UTC), against the thread's recommended "Add nothing now".
- 2026-11-10, the owner: the card's "Approve the plan" (15:05:57 UTC), the thread's recommended option, against "Keep the AI trader" and "Approve, but in spot".
- 2026-11-10, the thread (trading judgment the owner delegates, [DECISIONS](../../DECISIONS.md#2026-11-02--claude-is-the-projects-systematic-trader-the-trading-knowledge)): the perpetual, not spot (§4.8); never short and at most 1x (the card's words, 0057's T2); the 5% target by the limit rule written before the sizing run (§4.2); the latches unchanged; no per-trade stop, for the review to judge (§4.3); whole resizes, as the twin; the trader's code kept for a rollback; the switch at a flat 00:15 UTC bar with a new run by `SYSTEM`, except after a drawdown stop.
- 2026-11-10, the owner, in the project chat: "can everything stop, if necessary start fresh with $10k and update the app to latest changes ?" (15:08:06 UTC) and "I don't want to wait until everything completes november 15 or whatever the time is" (15:08:23 UTC). §9 step 4's conditions are replaced by these words: the build ships at once, with generation 19 (ExecPlan 0058, never installed) in the same update, and ExecPlan 0052's ChatGPT backtest ends `TRADER_REPLACED` at the install instead of being waited for. "Fresh" is read as the switch's new run with its own high-water NAV; nothing of the ledger is wiped, and a top-up to show 10,000 again is the owner's to ask for (rule 12).
- 2026-11-10, the thread, deviations in the build (each in the contracts with the code):
  1. **The switch** happens at the first finished 15-minute bar the rule reads with the account flat and funded, its valuation valid and the run running without a cause, not only at 00:15 UTC, so the rule reads its first day on the day of the switch. The run ends with `stop_reason` `NEW_POLICY` and a run event `POLICY_REPLACED` (the plan's word) carrying both policies' and the rule's hashes. A run with a cause open waits; a stopped run's next is the owner's Start, which starts under V2.
  2. **Readings** gain the outcome `NOT_READABLE` (a day whose closes are missing); a day not readable or refused is stored once per reason and codes, not at every bar it tries again.
  3. **The pages:** Settings gets a "Who trades" row instead of a changed agents' card; Decisions opens on a "Readings" tab under the rule, and the trader's history stays in its tabs (the timeline, labeled "Trader", with the playbook; the scorecard; the veto) instead of under a "Before 2026-11-…" heading; Home keeps of the trader's four quality tiles only the league, under "How it compares" (the calls, the coach and the luck check are the trader's history, on Decisions); the league and Trades' account switch name the account "Slow rule" once its newest run is the rule's (the engine's league row "The slow rule"), and "Trader" until the switch; Settings' limits show the rule's volatility target instead of the trader's risk at the stop, and leave out its decisions, cooldown and release windows; the agents' models say the trader and its reviewers are not asked; the dialog that starts a new run says when the rule reads.
  4. **The reverse switch** (§11's rollback) is not built: under V1 the engine's rule phase does nothing, so a rollback update must add the switch back to a trader's run.
  5. **The agents' check** is unchanged: it still binds `FUTURES_POLICY_V1` and asks generation 19's trader its `SC-03` probe (no decision is written), so a pass enables the agents for the veto.
  6. **ExecPlan 0056's guard:** `futures/engine.py` is one of the live design's fingerprinted modules, so 0056's lane now reads `LIVE_DESIGN_CHANGED`; its run has finished, so nothing is lost (the tests name the part).
- 2026-11-10, the independent money-path review (rule 13, a reviewer with no part in the build, on the diff from `98f02c6`): no blocker. Fixed in the build, each with a test that fails without it (a mutation run):
  1. **A stopping run** (the drawdown stop, or the owner's plain Stop) left the rule's position open with no exit but a reading the stopping run would not make. Now the protection phase exits it whole at once as `RULE_EXIT` and the run stops once flat; RISK_POLICY, AUTONOMY_MATRIX, the definitions' wording (new hashes) and the pages' Stop, Pause and stopping texts say so.
  2. **An agent decision tagged `FUTURES_POLICY_V2`** (which no trader writes) would have been answered as if V2 had an agent decider. Now every agent decision is refused `POLICY_CHANGED` while the rule decides, whatever policy it names.
  3. **An agent's position closing as the rule's** (`RULE_RESIZE` or `RULE_EXIT`) was allowed by `futures_position_opener`; now the check refuses it.
  4. Three older tests read V1 as the only policy and did not list the readings' table: updated (`test_m11_futures_db.py`, `test_m11_futures_api.py`).
- 2026-11-10, the review's notes kept as follow-ups, not built (each low on paper at 1x long; a later update can take them):
  1. No incident is raised when the daily closes stop arriving while the rule holds a position: the reading stores `NOT_READABLE` each day and the position stays, as §4.3 says; the pages show the reading, not an alert.
  2. `INSTRUMENT_UNAVAILABLE` refuses a decrease as it refuses an entry; an exit to flat still goes.
  3. The funding reserve is V1's (1% of notional), sized for holds of 24 hours or less; the rule holds for weeks. Only near 1x could a hold of several weeks use up the free wallet and leave funding `PENDING` (which the NAV leaves out), and the target nears 1x only when Bitcoin's volatility falls to about 6% a year; at 20% the target is at most 0.25.

## 14. Progress

- 2026-11-10: the plan written, `PROPOSED`; nothing built; approved by the owner at 15:05:57 UTC. The thread's files: `next-strategy/` in the project's shared folder (`SPEC.md`, `README.md`, `sim.py`, `run_check.py`, `robust.py`, `venue.py`, `sizing.py`, `sizing2.py`, `plan_numbers.py` and their JSON results; `data/` with the closes, funding and daily highs and lows; the zips on the owner's PC in `.cache\next-strategy\`).
- 2026-11-10, IMPLEMENTED on `claude/project-thread-spf33c`, from `main` at `98f02c6`, on the owner's words of 15:08 UTC (§13): §4.1 to §4.5, migration `0040`, the contracts of §5 (AGENTS.md, RISK_POLICY, AUTONOMY_MATRIX, DATA_CONTRACTS, RUNTIME_AGENTS, TRADING, ROADMAP, STATUS, DECISIONS) and the tests of R1 to R8: `tests/test_m11_main_rule_unit.py`, `tests/test_m11_main_rule_db.py` (the engine's samples `rule-*.json` for the web), `tests/test_m11_main_rule_agents_db.py`, the web's `src/futures/rule.test.tsx` and the browser specs as the rule shows the pages.
- 2026-11-10, VERIFIED in the cloud ([COMMANDS](../COMMANDS.md#execplan-0059-the-slow-rules-tests-and-install-check)): Ruff `All checks passed!`; the OpenAPI drift check and the web's `api:check` match; the link check finds none broken; the rule's, the twins' and the live worker's ten suites `173 passed` on a fresh database of the second cluster; the engine without a database, the baseline's two failures and one stand-in fixed (`25 passed` for its suite); the web's typecheck, lint and Prettier clean, Vitest `48` files and `419 passed`, the build passes; the browser chain `5`, `16`, `4` and `3 passed` on a database seeded at 16:33:31 UTC, and `live.spec.ts` `4 passed` on a `flat` one. NOT RUN in the cloud: the Docker build, the update, real readings on the PC.
- 2026-11-10, after the independent money-path review (§13), VERIFIED in the cloud ([COMMANDS](../COMMANDS.md#execplan-0059-the-slow-rules-tests-and-install-check)): its three fixes, each with a test that fails without it; the rule's, the twins', the live worker's and the futures suites `205 passed` on a fresh database; the whole engine suite read (the baseline, the stale tests fixed, a stream test's timing); Ruff, the OpenAPI drift check, `api:check` and the link check clean; the web's typecheck, lint and Prettier clean, Vitest `48` files and `421 passed`, the build passes; the browser chain `5`, `16`, `4` and `3 passed` and `live.spec.ts` `4 passed`. NOT RUN in the cloud: the Docker build, the update, real readings on the PC.
- 2026-11-10, merged as `93a2112` (PR #190) on the owner's words in the thread at 17:24 UTC ("I wanted to click merge it now but clicked Not yet accidentally") and installed by the owner's double-click (17:30 UTC "done"). OBSERVED read-only at 17:31 UTC in a Remote Control session ([COMMANDS](../COMMANDS.md#execplan-0059-the-slow-rules-tests-and-install-check)): the update `COMPLETE` on `93a2112` (`update-20261110T172454Z.log`; backup, migration `0038_slow_trend` to `0040_main_rule`, reconciliation OK, the pages answer); ten services running, each with a health check healthy; the stored `MAIN_RULE_V1` and `FUTURES_POLICY_V2` hashes the code's (`60f3d58e0fc4…bf72`, `08a6bd62cf64…6728`); run #1 (`FUTURES_POLICY_V1`) `STOPPED` `NEW_POLICY` at 17:30:01 UTC with the account flat, run #2 (`FUTURES_POLICY_V2`) `RUNNING`, started by `SYSTEM` the same second at 9,959.88 USDT in the wallet; the first reading (the day's 17:15 UTC bar) `FLAT`, signal −1/3, volatility 0.378, target 0, `NO_CHANGE` with no codes; no open position; `BACKTEST_AI_V1:TWO_MONTHS` `STOPPED` `TRADER_REPLACED`; the execution worker's log of the last 20 minutes has no error, and its one step of the switch shows `RUN_STOPPED` `NEW_POLICY`, `RUN_STARTED` by `SYSTEM` and the reading. NOT RUN: the page contents, the next day's reading at 00:15 UTC.
- 2026-11-12, `OBSERVED` read-only on the PC at 09:29 UTC (thread "Bring the app up to date now"; one READ ONLY transaction, rolled back): the folder at `93a2112` (main's two newer commits are documents only, so nothing to install), schema `0040_main_rule`, all ten services running and every one with a health check healthy, each up about 15 hours. Run #2 `RUNNING`, flat, 9,959.88 USDT at 09:00 UTC. The rule's readings: 2026-11-10 at 17:30:01, 2026-11-11 at 18:30:02 and 2026-11-12 at 00:15:01 UTC, each `FLAT`, `NO_CHANGE`, signal −1/3, volatility 0.378, 0.379 and 0.375. The 2026-11-11 reading came at 18:30 UTC, not at the day's first bar, most likely because the app was not running at the day's first bar (inferred: its containers had started again about 15 hours before the read, at about 18:30 UTC). When it stopped is `NOT READ`; with the account flat, nothing was owed.
