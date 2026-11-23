# ExecPlan 0053 — The trader every four hours and on events

**Status: APPROVED by the owner on 2026-11-03, in the project thread "Switch the trader to event-driven decisions": at 11:17:08 UTC "yes, using the trading.md file, implement using best practices for our app", at 11:17:50 UTC "and make it live now instead of november 16 if it better", and at 11:51:15 UTC the pick "Live as soon as it's built" on the thread's card ([DECISIONS](../../DECISIONS.md#2026-11-03--the-trader-every-four-hours-and-on-events-execplan-0053)). The measure of §4.5 is pre-registered by this plan, which ships with the code, before the first generation-14 decision. Built from `main` at `3e8e378`, merged as `22ab71a` once ExecPlan 0052's update was installed and checked, and installed on the owner's PC on 2026-11-03 at 15:28 UTC (§14); O1 passed on its first three whole UTC days (§14, 2026-11-07).** A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)): the trader, generation 14, decides every four hours and at once on an event, about 8 to 9 decisions a day instead of about 100. It changes no money path, no limit, no protection and no policy.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `CALCULATED`, `NOT RUN`. Every value in §4.1 is a `PROPOSED` engineering default, chosen on counts alone (§4.2) before any reading, and never tuned on one.

## 1. Goal

The owner asked in the project chat on 2026-11-03 at 11:14:52 UTC: "is there a better practice to handle the decisions instead of checking every 15 minutes ?". The coordinator proposed a slower clock with event triggers, and the owner answered in this thread with the words of the status line. The thread's card asked "Switch to the new clock as soon as it's built, or after 16 November?", since a new trader generation ends generation 11's run, whose paired reading was due on 2026-11-16; the owner picked "Live as soon as it's built".

Observable outcome:
1. The trader (generation 14, `FUTURES_DECISION_V6`) decides at 00, 04, 08, 12, 16 and 20 UTC (within the hour after, when a decision could not start then) and at once on one of four events: its entry cooldown ending after a closed trade, a move of 4 times the 15-minute ATR since its last decision, the first hourly close beyond the last 24 hours' range, and a funding rate change of 0.01 percentage points since its last decision. About 7.5 decisions a day from the clock, the moves and the breaks (§4.2), at most 32 a day.
2. Every decision still starts at a finished 15-minute bar within the policy's decision age, as generation 11's bar decisions did. `FUTURES_POLICY_V1`, its hash, the run, the limits and code's protection are unchanged; the engine's stop, take profit, time exit and liquidation still run every second.
3. The trader is told when it decides (its prompt's "When you decide" and the context's `schedule` block), so it decides for the hours until its next look, not for the next 15 minutes.
4. Home shows when the next decision is due and what would start one sooner; Home and Settings say how the trader decides; Settings' decisions-today tile counts the schedule's 32.
5. The measure of §4.5 is written before the first decision.

## 2. What the app has

`VERIFIED` on `main` at `3e8e378`:
- The scheduler (`futures_trader.schedule_futures`, `_futures_trigger`) starts generation 11's trader `FUTURES_DECISION_V5`, one decision at a time while the run is `RUNNING` or a position is open, at most the policy's 120 a UTC day counted with generations 7 to 10's traders: at each finished 15-minute bar once its last 1-minute candle is final; right after a fill (an entry; an exit only when no entry cooldown follows it); and at once on a sharp move of the mark (more than 1.5 times the 15-minute ATR within 5 minutes). A trigger is covered by any decision started after its event; one older than the policy's decision age (300 s) is never started.
- `FUTURES_POLICY_V1` ([RISK_POLICY](../contracts/RISK_POLICY.md#m11-futures_policy_v1-execplan-0039)) says nothing of when the trader decides beyond the 120 decisions a day and the decision age; the cooldowns are 1 whole 15-minute bar after an exit's bar and 2 after a stop or a liquidation.
- `futures_decisions.trigger` and the scores' copy `futures_decision_scores.trigger` are `varchar(12)` with a check of `BAR`, `FILL` and `SHARP_MOVE` (migrations `0020` and `0024`); the decision guard of `0028` accepts generations 7 to 11's traders.
- The quiet window (HH:59:30 to HH:06:00 UTC) does not hold the trader back (`BUDGETS_V11.quiet_window_utc.except`).
- The scorer ([ExecPlan 0043](0043-score-every-decision.md)) scores every decision and every finished bar; a bar is linked to the trader's workflow created within its 15 minutes, and a bar with none is `NO_JOB`, counted as without a decision while the run was running or a position was open.
- The result checks ([ExecPlan 0045](0045-where-the-results-come-from.md)) take their window from the newest decision's template (`result_checks.read_inputs`), so a new trader generation starts a new window.
- Home's "Next decision" counts down to the next 15-minute bar (`geometry.nextQuarter`); the position card and the run controls say "The trader decides at each finished 15-minute bar".

`CALCULATED`: generation 11 makes about 100 decisions a day: 96 bars, plus the fills and sharp moves that no bar's decision covers (the PC's count is read at the install check, §9). Each costs about 13,933 input and 291 output tokens, about 0.77 Codex credits (`OBSERVED` on the PC on 2026-10-28, [0046 §14](0046-leaner-agents.md#14-progress)): about 77 credits a day of the owner's shared ChatGPT allowance.

`OBSERVED` by the weekly review on 2026-11-03 ([TRADING](../../TRADING.md#the-record-so-far)): generation 11's 1-hour calls 53.8% right against the last-hour rule's 51.9%, the paired difference +0.007% an hour (interval −0.028 to +0.044); at 4 hours 49.2%; its 10 closed trades lost 28.56 USDT after 28.55 USDT of fees.

## 3. Scope

In: generation 14's definitions (`definitions_v14.py`) and prompt (`trader.v6.md`); the schedule (`app.agents.futures_schedule`); the scheduler's switch to it (`futures_trader`); the context's `schedule` block; migration `0033`; the overview's `schedule` and the runtime read's `budgets_v14`; Home's countdown and position card, Settings' run controls, limits and model cards, the decision labels; tests; the contracts.

Out: the policy and its limits; the call's 1-hour horizon (§4.3); the coach, the reviewers, the veto, the replay and the twins, which keep their generations; the scorer and the Scores page's bars without a decision (§11, known gaps); the backtest of [ExecPlan 0052](0052-backtest-the-ai-trader-on-history.md).

## 4. Design

### 4.1 The schedule `SCHEDULE_V1` (code, in `TEMPLATES_V14`)

Generation 14's template carries its schedule as a hashed document (`EVERY_4H_AND_EVENTS_V1`). At a finished 15-minute bar, once its last 1-minute candle is final and within the policy's decision age, `futures_schedule.due` decides from stored records alone which moments are due: when the trader's last decision started (any generation), the stored final 1-minute candles, the newest marks and the last closed position. Nothing a model returns reaches it.

| Kind | Due at a finished bar's close when | Late up to |
|---|---|---|
| `BAR_4H` | The newest 4-hour boundary (00, 04, 08, 12, 16, 20 UTC) has no decision started at or after it | 1 hour |
| `TRADE_CLOSED` | The account is flat and the entry cooldown after the last closed position ended (the policy's: 1 whole bar after an exit's bar, 2 after a stop or a liquidation), with no decision started since that end | 1 hour |
| `MOVE` | The bar's close is at least 4 × the 15-minute ATR(14) at it from the close of the bar that ended at or before the last decision started | — |
| `RANGE_BREAK` | The 1-hour candle that just closed closed above the highest high or below the lowest low of the 24 complete 1-hour candles before it, and the hour before it did not in that direction; no decision since the hour's close | 15 minutes (the hour's bar or the next) |
| `FUNDING_JUMP` | The funding rate of the newest mark at the close moved by at least 0.0001 from the newest mark's when the last decision started, each mark at most 60 s old | — |

- **Coalescing.** A moment is covered by any decision started at or after it, so a finished bar starts at most one decision and a late moment none once another decision has seen it.
- **Naming.** The first kind due in the table's order names the decision (`trigger.kind`); the others due are listed in `also`, each with its facts (`base`, `closed`, `move`, `range_break`, `funding`). The key is the bar's close, so a bar queues one workflow.
- **Missing data.** An event without its candles, its ATR or fresh marks is not due; the 4-hour decision and the closed trade's still are, and the decision's own context shows what is stale.
- **The day.** At most 32 of generation 14's decisions a UTC day (queued, or started that day): a guard against an event storm, well above §4.2's busiest day. The policy's 120 a day still count every trader's decisions.
- **One at a time**, while the run is `RUNNING` or a position is open, and while the agents' check passed when flat, as before.
- **Not started any more:** at every finished bar, right after a fill, on the policy's sharp move. The scheduler of generations 7 to 11 (`_futures_trigger`) stays in the code for a rollback that names an earlier trader (§11).

Why each kind (opinion, with the evidence of [TRADING](../../TRADING.md#the-principles-with-the-evidence)):
- `BAR_4H`: the look matches the hold. Entries' time exits are 4, 12 or 24 hours, so a position is looked at one to six times in its life instead of 16 to 96; calls four hours apart barely overlap at the one-hour horizon, so each is nearly independent evidence (principle 10). Predictability at 15 minutes is a tenth of a taker fee (TR-05) and decays fast (TR-06); the evidence is at slow horizons (principle 4).
- `TRADE_CLOSED`: the useful half of the fill trigger. After an exit the trader can do nothing until the cooldown ends, so it looks then; right after its own entry it has just decided, and code protects the position.
- `MOVE`: replaces the sharp move, which fired in about 8 five-minute windows a day (§4.2): 4 × the ATR from the price at the last decision is a move large enough that its premise may no longer hold.
- `RANGE_BREAK`: the information a 4-hour look could miss most, a break of the day's range.
- `FUNDING_JUMP`: funding is a priced cost (principle 7, TR-13); a change of one basis point per settlement changes what holding costs.

### 4.2 The calibration (`CALCULATED`, counts only)

Binance's public 1-minute candles and settled funding of the BTCUSDT perpetual, 2022-01-01 to 2026-11-01 (1,765 days, 169,344 15-minute bars): the archive [ExecPlan 0051](0051-backtest-the-rule-twins-on-history.md) downloaded on the owner's PC, staged into the cloud with its checksums matched. The rules of §4.1 ran over it in a script in the session's scratch space, counting how often each kind would start a decision, with each decision covering what §4.1 says. No return, hit rate or result of any kind was computed: the values were chosen on how often they fire, so that §4.5 stays a clean test.

| Measure | Value |
|---|---|
| The 15-minute ATR(14) as a share of the price | Median 0.306%, 10th percentile 0.149%, 90th 0.586% |
| Decisions a day at 4 × ATR (`BAR_4H`, `MOVE`, `RANGE_BREAK`) | 7.47: `BAR_4H` 6.0, `MOVE` 0.62, `RANGE_BREAK` 0.86 |
| The same per UTC day | Median 7, 90th percentile 9, 99th 11, most 13 |
| At 3, 5 and 6 × ATR | 8.53, 7.12 and 6.99 a day (`MOVE` alone at 3 and 5: 1.73 and 0.22) |
| First hourly closes beyond the last 24 hours | 1.22 a day, 0.94 of them off the 4-hour marks; beyond 48 hours 0.81, 72 hours 0.63, 168 hours 0.36 |
| Settled funding changes of at least 0.0001 | 5.0% of settlements, about 0.15 a day (0.9% in 2025 and 2026) |
| The policy's sharp move today, on 1-minute data | About 8.1 windows a day |

The predicted funding rate in the marks moves more often than the settled rate; its frequency is `NOT CALCULATED` (the archive has settled rates only), and the 32-a-day guard bounds it. `TRADE_CLOSED` adds at most one decision per closed trade: generation 11 closed 10 in its first 5.8 days (`OBSERVED`, 2026-11-03). So about 8 to 9 decisions a day: about 92% fewer than generation 11's.

4 × ATR and 24 hours were picked as the moves and breaks a 4-hour look would otherwise miss, at under one a day each; 3 × ATR nearly triples the moves, and 5 or 6 × barely changes the total.

### 4.3 What the trader is told

`trader.v6.md` is `trader.v5.md` with four lines changed and one section added (`VERIFIED` by a test of the diff):
- the title;
- the `trigger` kinds and `also`, and the `schedule` block in the context's list;
- `limits` are "under the policy";
- "When you decide": every four hours and at once on an event, one at a time, at most 32 a day; between decisions nobody looks, a `HOLD` holds until the next decision and only the engine's protection acts; so decide for the hours until the next look; after an entry it may not look again for up to four hours, which its time exit of 4, 12 or 24 hours matches;
- in a position, `TIGHTEN_STOP` "to protect a gain you would not give back before your next decision".

Unchanged: the 1-hour call (`expected_move`), the entry rules (`MEDIUM` or `HIGH`, the side of the call, a stop of 2 or 3 × the ATR, a time exit of at least 4 hours), the confidence switch, the policy's sets, the reads, the budgets, the finish checks and the shorter scores block. The call stays at one hour because the scorer, the scorecard, the coach's and the reviewers' views and generation 11's record all judge it there, which keeps §4.5's measure the same as generation 11's; the Scores page also judges it at 4 hours ([ExecPlan 0041](0041-twins-and-a-veto.md) part 2). A 4-hour call is a trial of its own, the replay's `CALL_4H` arm ([ExecPlan 0050](0050-replay-past-decisions-offline.md)).

The context's `schedule` block, built at the decision's cutoff (`futures_schedule.shown`): `id`, `every_hours`, `next_base_at`, `per_utc_day`, `move` (the price the next `MOVE` is measured from, the multiple and the distance), `range_next_hour` (the 24-hour high and low the next hourly close must break, or null without 24 stored hours) and `funding_step`. A full context with it fits the prompt limit with 12 KiB to spare (51,975 of 65,536 bytes, `VERIFIED` by a test).

### 4.4 The pages

- Home's trader card: "Next decision 16:00 · in 2h 41m, or sooner on a closed trade, a big move, a range break or a funding jump", the ring running over the four hours (`geometry.nextScheduled`); before the first decision it says how the trader decides: "The trader decides every 4 hours, and at once on a closed trade, a big move, a range break or a funding jump." Home's position card, when flat, counts down to the next scheduled decision instead of the next bar.
- Settings: the run controls' Start ends with the same sentence; the limits' "Decisions today" tile counts generation 14's decisions of the UTC day against the schedule's 32; the model cards say the trader runs "Every 4 hours, and at once on a big move".
- Decisions labels the kinds "4-hour check", "Trade closed", "Big move", "Range break" and "Funding jump", and its empty list says when the first decision comes.
- The API: the futures overview's `schedule` (`trader`, `every_minutes`, `events`, `decisions_per_day`, `decisions_today`); the runtime read's `budgets_v14`.

The shadcn skill was loaded and the project discovered before the edits; no component was added and preset `b2fms61Bqi` is kept ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0053-the-trader-every-four-hours--2026-11-03)).

### 4.5 The measure, pre-registered

On generation 14's decisions (purpose `DECISION`, never the agents' check), in time order (`context_at`). The score of a call at horizon `h` is the move at `h` in the called direction: `+move_h` for `UP`, `−move_h` for `DOWN`, 0 for `NO_VIEW`; `move_h` is the decision's `futures_decision_scores.move_percent` at `h` minutes, `SCORED`; a decision without one is left out and counted. The free rule's score is the same with the sign of the context's stored return (`returns_percent` 1h for the last-hour rule, 4h for the last-4-hours rule), 0 when it is zero.

**O1, the operational check** (read-only on the PC, at the install check and after three whole UTC days). On each whole UTC day with the run `RUNNING`: between 4 and 16 decisions; every decision's trigger one of the five kinds; each 4-hour boundary with a decision within the hour after it, or a waiting reason (the allowance, the agents' check, an open decision) in the agent worker's log; the time exits, stops and take profits of the positions closed in the window filled as before. A miss is a bug: fixed forward, or §11's rollback.

**M1, the primary measure** (the trial ledger counts one):
- The mean of the paired differences at 60 minutes (the trader's score minus the last-hour rule's), with a stationary bootstrap interval (`app.evaluation.bootstrap.interval`, mean block 2 decisions, 10,000 resamples, seed `derive_seed("SCHEDULE_V1", "M1")`) at 95% and at 99.375% (1 − 0.05/8: Bonferroni for the eight variants on the trial ledger, §4.6).
- Read once 120 of the decisions are decisive at 1 hour (right or wrong beyond the 0.12% band): about 22 to 25 days after the install (`CALCULATED` at 7.5 to 8.5 decisions a day, 64% of them decisive as generation 11's). Read-only on the PC, on the owner's "Go". Before that: "too few".
- **Verdict:** `PASS` when the 99.375% interval's lower end is above 0; `WORSE` when the 95% interval's upper end is below 0; otherwise `NO_DIFFERENCE`. A sign of harm is acted on with less evidence than a claim of edge.
- `CALCULATED`, the expected width: generation 11's paired differences had a spread of about 0.23% a call (from TR-36's interval on about 100 non-overlapping hours and the weekly review's on about 150); at about 190 gen-14 calls the 95% interval is about ±0.03% and the 99.375% one about ±0.05%. A `PASS` needs about +0.05% an hour over the rule, more than half of the rule's own +0.08%. Event calls come in volatile hours, so the spread, and the width, may be larger.
- What a verdict means: `PASS` is evidence that the trader adds something to the free rule at this cadence; it stays. `WORSE` puts a card in front of the owner: §11's rollback, or the rule in code with the model as a reader. `NO_DIFFERENCE` is the expected result, as generation 11's: generation 14 stays, since it does the same at about a twelfth of the calls. Nothing changes by itself from a verdict.

**Secondary**, 95% intervals, never a verdict:
- S1, at 240 minutes against the last-4-hours rule (mean block 2): the hold's horizon (principle 4).
- S2, the hit rates at 1 and 4 hours (Wilson intervals), the trader's and each rule's on the same decisions.
- S3, by trigger kind: decisions, hit rate and the paired mean at 1 hour, `BAR_4H` against the events.
- S4, the trades: count, net R and USDT after costs, costs as a share of the risk, how each closed; the result checks and the league table (too few until 30 entries and 30 days).
- S5, the cadence: decisions a day by kind against §4.2; the delay from a boundary to its decision; the waiting reasons.
- S6, the cost: calls and input, cached and output tokens a day, against generation 11's last whole UTC days.
- Descriptive only, never paired (different hours): generation 11's M1 over its whole run, 2026-10-28 13:45 UTC to the install, as the 2026-11-16 reading computes it.

### 4.6 The trading review (TRADING.md's eight questions)

1. **Rules:** paper only. Every decision is one of the moments `FUTURES_POLICY_V1` already allows (a finished bar, within its decision age); code keeps every exit, size and limit; the schedule reads stored records only and adds a tighter limit (32 a day); nothing is loosened and no authority moves to a model (`VERIFIED` by §6's tests). Passes.
2. **Class:** a new generation: the trader is told and does something different (when it decides, the "When you decide" section, the `schedule` block). It ends generation 11's run at the install, so the 2026-11-16 reading reads generation 11's days from 2026-10-28 13:45 UTC to the install (about 6 days instead of 19); the owner chose this on the card. The result checks start a new window with generation 14 (`VERIFIED`, §2).
3. **Costs:** a trade's fees, slippage and funding are unchanged. Entries can happen only at decisions, so there are fewer chances to trade on noise, while generation 11's trades made nothing before costs and lost their fees (§2): principle 1 says never trade faster, and this trades slower. No cost gate is added; that would be its own trial.
4. **Horizon:** the look now matches the hold (4- to 24-hour time exits). The 1-hour call stays, the known weakness of principle 4; its fix is the replay's `CALL_4H` trial and a later generation.
5. **The model's place:** unchanged: it still forecasts from numbers (principle 5). Code decides when it looks; the change takes away chances to act on 15-minute noise, and adds no information the features lack.
6. **The yardstick:** the last-hour rule on the same decisions at 1 hour, as generation 11's, and the last-4-hours rule at 4 hours (S1); 120 decisive calls; "too few" until then (principle 10).
7. **Pre-registration and the trial ledger:** §4.5, in this plan before the first decision; the post-hoc cuts earlier reviews logged (TR-36) stay hypotheses. The ledger: generation 14 is the eighth variant of the trader (generations 7 to 11 live, the replay's `NO_FEEDBACK` and `CALL_4H`, generation 14), so M1's `PASS` is deflated by eight; ExecPlan 0052's backtest arms count in its own plan.
8. **The clock and the cost:** the 2026-11-16 reading shortens (question 2); M1 reads in about 3 to 4 weeks. Calls: about 8 to 9 a day instead of about 100; about 6 to 7 Codex credits a day instead of about 77 (`CALCULATED` at 0.77 a call); the allowance freed goes to the replay and the backtest, which run in the agents' free time.

## 5. Authority

No permission, tool, limit or grant changes. Generation 14's role grants are generation 11's (the `COORDINATOR`'s two reads and `record_futures_decision`); its finish checks are generation 11's and the database holds its rows to generation 10's rules (migration `0033`'s guard). The schedule is code's, hashed in the template, and reads stored records through the agent identity's read views; no model can change when it is called. The schedule's 32 a day is one more limit, tighter than the policy's 120, which is unchanged. [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) record generation 14.

Rule 13's money-path review: no money path changes (no ledger, journal, reservation, account, engine or risk-gate code; the futures engine answers a generation-14 decision exactly as a generation-11 one), so the independent review is not required.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| E1 | Each kind is due exactly when §4.1 says: at its moment, up to its lateness, not when covered, not without its data | `tests/test_m11_event_trader.py`, five unit tests |
| E2 | The first kind due names the trigger and the others come in `also` with their facts, keyed by the bar's close | Unit test |
| E3 | Generation 14's trader is generation 11's but its prompt, parameters, schedule and `replaces`; the same budgets, the quiet window's exemption, the caps 120 and 32, the policy unchanged; the prompt differs from v5 only where §4.3 says, and a full context fits | Unit tests |
| E4 | Migration `0033` froze generation 14's documents as the code has them; the two trigger checks gain the five kinds; the guard gains `FUTURES_DECISION_V6` and nothing else | Unit test of the migration's text |
| E5 | The scheduler starts generation 14 once at a boundary's bar and not at a plain bar; a boundary held back by an open decision starts within the hour after | Database tests |
| E6 | `MOVE`, `RANGE_BREAK`, `FUNDING_JUMP` and `TRADE_CLOSED` each start a decision at their bar, and the next `MOVE` is measured from it; half a funding step starts none | Database tests |
| E7 | The schedule's 32 hold the 33rd until the next UTC day; the policy's day counts every trader's | Database test |
| E8 | The context's `schedule` block; the prompt with schema v8 as its format; the row records the kind and the bar; the guard holds a V6 row to generation 10's rules and the checks take the kinds; the scores keep the kind and decide the bar; the overview counts the day's decisions | Database and API tests |
| E9 | `0033` up, down and up; the downgrade refuses once a generation-14 workflow, profile or decision exists, then restores `0028`'s guard and checks | Migration test |
| E10 | Generations 7 to 11's schedule still runs when the scheduler names their trader (§11's rollback path) | `tests/test_m11_trader.py`'s three schedule tests, naming generation 11 |
| E11 | Home's countdown and its sentence, the position card, Settings' run controls, limits and model cards, the decision labels | Vitest; the browser suite `pages.spec.ts` (§14) |
| E12 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host, data source or model. The calibration reads Binance's public archive as [ExecPlan 0051](0051-backtest-the-rule-twins-on-history.md#7-official-sources) does. The evidence of §4.1 and §4.6 is [TRADING](../../TRADING.md)'s, with its sources in [REFERENCES](../../REFERENCES.md#trading-research--2026-11-01-and-2026-11-02): TR-01, TR-02 and TR-04 (slow horizons), TR-05 and TR-06 (15-minute predictability), TR-07 (costs at short horizons), TR-13 (funding), TR-35 and TR-36 (the samples and the paired test). The bootstrap is Politis and Romano (1994) in `app.evaluation.bootstrap`; the Wilson interval is Wilson (1927).

## 8. Data and trust boundaries

- No new host, secret, volume or network path.
- New stored data: generation 14's workflows and decisions; their trigger kinds and facts in the decision rows and the stored contexts; the context's `schedule` block. Kept in every backup.
- The schedule reads only the agent identity's read views (`agent_read.futures_bars`, `futures_marks`, `futures_positions`) and the trader's own workflows, as of the bar's close; nothing a model returns reaches it.

## 9. Implementation sequence

1. This plan, with the code, migration `0033`, the tests and the contracts, in one pull request (§14).
2. When [ExecPlan 0052](0052-backtest-the-ai-trader-on-history.md) merges (migration `0032`, generation 15): `0033` revises `0032_ai_backtest`, generation 14 goes before 15 in `generations.GENERATIONS`, and the backtest thread's tripwire test (`tests/test_backtest_lane_unit.py::test_the_first_steps_are_the_ones_a_running_backtest_rebuilds`) runs here; if it fails, the two threads decide together before this merges.
3. The owner's word to merge; merged after 0052's update is installed and checked; the owner's double-click of `update-app.cmd`.
4. The install check, read-only on the PC: the agents' check passed on the new profile; the first generation-14 decisions and their triggers; generation 11's decisions a day over its last whole UTC days; O1's first part.
5. After three whole UTC days: O1, read-only. The thread tells the reading of 2026-11-16 where generation 11's run ended.
6. M1 once its sample is reached, on the owner's "Go".

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL (the new suite, the M11 agent suites and those that name the newest generation or the migration head), the web checks (lint, types, Prettier, Vitest, build, `api:check`), the browser suites that cover Home, and the link check, with results in §14. `NOT RUN` in the cloud and done by the update or its check on the PC: the Docker build, the update, the agents' check against the real model, real generation-14 decisions.

## 11. Failure and rollback

- A moment the agents could not take (the allowance used up, the check pending, an open decision): the 4-hour decision starts within the hour after; after that, the next boundary. Code protects the position meanwhile; no exit waits for the model.
- An event storm: the schedule's 32 a day, then the policy's 120.
- The schedule fires wrongly or too seldom: O1 shows it; fixed forward.
- The trader does worse at this cadence: M1's `WORSE`, a card for the owner.
- **Rollback:** an update that names generation 11's trader in `futures_trader.FuturesGraph.futures_trader` and `futures.views.SCHEDULE` again; generation 11's schedule (`_futures_trigger`) is kept for it, and E10 tests it. The older images do not know schema `0033`, and `0033`'s downgrade refuses once generation 14 has left a workflow, a profile or a decision, as `0028`'s does: so a rollback goes forward with an update, not back.

Known gaps, stated and not fixed here:
- The Scores page's "Bars without a decision" counts about 88 bars a day as "no trader job" while the run is running: the scorer's `expected` (`DECISION_SCORING_V1`) is "the run was running or a position was open", so a bar the schedule did not call for reads like one it missed. The coach and the decision reviewer see the same count; the trader's shorter block does not show it. A scoring version that knows the schedule is a later change; until then the count means what the page says. Fixed by [ExecPlan 0054](0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md) (`DECISION_SCORING_V2`).
- The coach's prompt (generation 10) and the decision reviewer's (generation 9) still say the trader decides at every 15-minute bar; they change only with a new generation of those agents.
- The reviewers and the coach still wait before each 15-minute bar (`NEXT_BAR_TOO_CLOSE`): kept on purpose, since an event can start a decision at any bar.
- The funding jump's frequency on the marks' predicted rate is `NOT CALCULATED` (§4.2).

## 12. Q01–Q10

Q01, Q02: Home's countdown and sentences, Settings' tile and the decision labels change; no new page (E11). Q03: E1 to E10. Q04: no new secret or host; the schedule reads stored records only (§8). Q05: §11. Q06, budgets declared before measuring: the scheduler reads 27 hours of 1-minute candles at most once per bar close and state (`_schedule_memo`); a decision still starts within the policy's 300 s of its bar's close; the context gains about 400 bytes. Q07: the cloud suites (§14). Q08: each decision's trigger kind and facts in its row and context; the agent worker's waiting reasons (`SCHEDULE_DAY_FULL` added). Q09: migration `0033` and its downgrade (E9); the update's backup. Q10: the contracts of §5 and the data contract; no new dependency.

## 13. Decision log

2026-11-03, by the thread under the owner's words of §1 and "decide for me" (2026-10-19), each the recommended engineering choice:
- **Four hours as the base:** the time exits are 4, 12 and 24 hours; six looks a day; calls four hours apart barely overlap. The coordinator's proposal.
- **The policy unchanged:** a new policy would need a new run, which is the owner's; every generation-14 decision is one of the moments `FUTURES_POLICY_V1` allows.
- **The events and their values chosen on counts only** (§4.2), before any reading.
- **Dropped:** the 15-minute bar (96 looks a day at a horizon whose predictability is a tenth of a fee), the entry's fill (the trader just decided), the policy's sharp move (about 8 windows a day; `MOVE` replaces it, measured from the last decision's price).
- **`TRADE_CLOSED` at the cooldown's end,** not at the exit's fill: the trader can do nothing before; generation 11 already skipped an exit's fill when a cooldown followed.
- **The call stays at one hour** (§4.3).
- **The kinds fit the column:** `TRADE_CLOSED` rather than a longer name, so `trigger` stays `varchar(12)` and only the checks change.
- **32 a day,** above the busiest day of 1,765 (13) and below the policy's 120.
- **The prompt says when the trader decides,** since a `HOLD` now holds for hours.
- **The decisions-today tile counts the schedule's 32,** the limit that binds the trader now; the policy's 120 stays in the trader's `limits`.
- **Live at the install,** ending generation 11's run early: the owner's pick on the card (11:51:15 UTC).
- **Numbering:** generation 14 and migration `0033` after ExecPlan 0052's generation 15 and `0032`, agreed with the backtest thread at 11:42 UTC; whoever merges second moves the head asserts and the generation order.

## 14. Progress

- 2026-11-03 11:14 to 11:52 UTC: the ask, the coordinator's proposal, the owner's words and the card's pick (APPROVED).
- 2026-11-03 from 11:20 UTC: §4.2's counts on the archive staged from the PC (`CALCULATED`).
- 2026-11-03, IMPLEMENTED on `claude/project-thread-i8dp0p`: §4.1 to §4.4, migration `0033` (revising `0031_decision_replays` until 0052 merges), the contracts of §5, and the tests of E1 to E11 (`tests/test_m11_event_trader.py`, 21 tests; the older tests that name the newest generation or the migration head; the web's Vitest files).
- `VERIFIED` in the cloud (no Docker), with the commands of [COMMANDS](../../COMMANDS.md), on scratch databases of a PostgreSQL 16 cluster:
  - Ruff on the engine's `app`, `tests` and `alembic`: "All checks passed!"; `python -m app.export_openapi --check`: the schema matches; the web's `api:check`, typecheck and ESLint pass.
  - Vitest on the changed areas (cockpit, settings, futures, agents, decisions): 20 files, 206 tests passed.
  - `tests/test_m11_event_trader.py` on fresh databases: 21 passed, in six full runs (three of them on a database migrated just before the first).
  - `tests/test_m11_trader.py`, `test_agent_models.py`, `test_m11_replay_db.py`, `test_m11_replay_unit.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_generations.py`, `test_m6_agent_units.py`, `test_m11_futures_api.py`, `test_m11_clean_start.py` and `test_m11_checks_db.py`: 187 passed.
  - `tests/test_m11_decision_reviews.py`, `test_m11_scores_db.py`, `test_m11_veto_db.py`, `test_m11_reviews.py` and `test_m11_twins_db.py`: 102 passed and 3 failed, the three of `test_m11_scores_db.py` that [COMMANDS](../../COMMANDS.md) records for `main` (a twin entry scored, the decisions page's checkpoints, only the agent identity stores a score).
  - Migration `0033` up, down and up on a scratch database.
  - OBSERVED once and not reproduced: in the first full run of the new suite (12:44:28 to 12:45:00 UTC) E8's end-to-end test failed beside two tests whose own faults were then fixed, and its traceback was not kept. It passed in every later run: the six full runs, three alone, six across 13:00 UTC, and once with its data written a quarter before its clock (a probe of the 15-minute boundary, not committed). The cause is unknown.
- 2026-11-03 13:20 UTC: `main` merged at `c53e44b` (#169 and #170, the Claude Console's keys); one web schema file changed on both sides and merged without a conflict.
- `VERIFIED` on the merged tree, the same way:
  - Ruff on the engine and on the runner: "All checks passed!"; the OpenAPI drift check: the schema matches; the runner's `test_providers`: 30 tests OK.
  - The web: typecheck, Prettier, `api:check`, Vitest (47 files, 402 tests) and the production build pass, and ESLint passes on the source. OBSERVED: run after a build, `pnpm lint` also reads `apps/web/.output` and reports 192 errors there and none in the source; `eslint --ignore-pattern '.output/**'` passes.
  - The browser suites, each on a fresh database with the feed, the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the built web server: `live.spec.ts` on a `flat` database, 4 passed; `perp.spec.ts` on `tests.m7_browser_fixture seed`, 2 passed; and the chain on a database seeded at 13:36:06 UTC: `reviews.spec.ts` 5 passed, `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` 16 passed, `scores.spec.ts` 4 passed, `checks.spec.ts` 3 passed.
  - OBSERVED: the same chain on a database seeded at 13:24:19 UTC failed `scores.spec.ts`'s first test (two refused decisions where it expects one; its other three did not run). The fixture's SYNTHETIC walk went under the open long's tightened stop (its low 59,836.23, the stop 59,872.0) before the toast test's exit, which was refused `POSITION_CHANGED`: the limit of the fixture's clock that [COMMANDS](../../COMMANDS.md#browser-suites-cloud) records, in the engine's unchanged protection.
  - The whole engine suite on a fresh database, started at 13:20:29 UTC, was stopped at about 42% when ExecPlan 0052 merged, to run on the merged tree instead (below).
  - A trial merge with #166's `1ed15cd` (ExecPlan 0052), local and not pushed. 27 files conflicted, all on the numbering, and were resolved as §9 step 2 says. On it:
    - the backtest thread's `test_the_first_steps_are_the_ones_a_running_backtest_rebuilds` passed;
    - without a database, `test_generations.py`, `test_backtest_lane_unit.py`, `test_m11_replay_unit.py`, `test_backtest_ai.py`, `test_backtest_ai_report.py` and `test_backtest.py`: 104 passed;
    - on a scratch database, `test_m11_event_trader.py`, `test_backtest_lane_db.py`, `test_backtest_lane_unit.py`, `test_m11_replay_db.py`, `test_m11_replay_unit.py`, `test_m11_veto_db.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_m11_decision_reviews.py`, `test_m11_scores_db.py`, `test_m11_checks_db.py`, `test_m11_clean_start.py`, `test_m6_agent_units.py`, `test_generations.py`, `test_m11_trader.py` and `test_agent_models.py`: 274 passed and 4 failed. Three are `test_m11_scores_db.py`'s of `main`. The fourth was the backtest's downgrade test, which named `0032` as the head; once it stepped down from `0033` first, it and E9 passed (2 passed);
    - the web's typecheck and Vitest on the changed areas (14 files, 137 tests) passed, and the links had none broken.
- 2026-11-03 13:50 UTC, §9 step 2: ExecPlan 0052 merged at 13:37 UTC (#166, `main` at `b9388e5`, its head `ee8aeff`) and was merged here (`5c82751`). Git reused the trial's resolutions for every conflicted file (`rerere`). The merged tree differs from the trial's only by 0052's last commit and this plan's own record. Three edits outside the conflicts were made again: `0033`'s parent, E4's assert of it, and the backtest's downgrade test, which steps `0033` down first.
- `VERIFIED` on the merged tree:
  - Ruff (engine and runner), the OpenAPI drift check, the links (0 broken), and the web's typecheck, ESLint, Prettier, `api:check`, Vitest (47 files, 402 tests) and the production build.
  - The browser suites, each on a fresh database: the chain seeded at 13:54:01 UTC (`reviews.spec.ts` 5 passed; `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` 16 passed; `scores.spec.ts` 4 passed; `checks.spec.ts` 3 passed), `live.spec.ts` 4 passed and `perp.spec.ts` 2 passed.
  - On a scratch database, run from 13:57:51 to 14:03:55 UTC, the trial's sixteen suites plus `test_backtest_ai.py`, `test_backtest_ai_report.py` and `test_backtest.py`: 334 passed and 4 failed. The backtest thread's `test_the_first_steps_are_the_ones_a_running_backtest_rebuilds` passed. Three of the failures are `test_m11_scores_db.py`'s of `main`.
  - The fourth failure is `OBSERVED` as a time-of-day failure of `main`'s own test, not of this change. `test_backtest_lane_db.py::test_the_scheduler_waits_for_its_gate_and_its_turn_and_says_why` got `KeyError: 'waiting'` where it expects `BAR_SPENT`. A test begun between HH:58:30 and HH:00:00 UTC gets `ReviewClock`'s clock 8 minutes ahead, so the backtest's two-a-bar count starts at the next hour's first bar, while the workflows' `created_at` is the database's unshifted time. `VERIFIED` by reproduction: the test passed alone at 14:07:10 UTC, and failed the same way at 14:07:16 with the shift forced by a scratch pytest plugin, with nothing in the repository changed. `backtests.py`, `ReviewClock` and that test are `main`'s, unchanged here. The app is not affected, because its clock and the database's agree. The backtest thread was told, reproduced it on `main` and fixed the test in #172 (the test alone), which merges with ExecPlan 0052's install record.
  - The whole engine suite on a fresh database, from 13:51:24 to 14:51:57 UTC: 6 failed, 2109 passed, 74 errors. The 74 errors and five of the failures are the baseline that [COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud) records: `test_m1_account.py`'s 13 errors and the research store's 61; `test_api.py`'s status test, `test_m6_schema.py`'s downgrade and `test_m11_scores_db.py`'s three. The backtest's scheduler test passed in this run.
  - The sixth failure is `OBSERVED` as a timing failure under the whole suite's load. `test_m2_reference_checks.py::test_failed_clock_request_keeps_the_collection_and_fails_closed[rate-limit]` found a `VALID` quote among its samples timed before the second clock check. Its sampler takes the time before its two reads, so a slow read made after the check can carry an earlier time (a hypothesis from the code, not reproduced). Alone, its file had 26 passed, and that case passed twice more. This change does not touch the market feed or that test.
- 2026-11-03 14:53:42 UTC: the owner tapped "Yes, merge it then" on the card "Merge the four-hour trader once the backtest update is installed?". The merge waits for ExecPlan 0052's install to be checked on the PC (§9 step 3).
- 2026-11-03 15:12:44 UTC, §9 step 3: [#171](https://github.com/MentorAliu/adaptive_spot_lab/pull/171) merged as `22ab71a`, once the backtest thread had checked ExecPlan 0052's install (`update-20261103T140501Z`, and a second run on the same commit, `update-20261103T150518Z`, both `COMPLETE`).
- 2026-11-03, §9 step 4: the owner's double-click of `update-app.cmd` ("done" at 15:31 UTC). `OBSERVED` read-only on the PC by the thread's device session, finished at 15:37 UTC, which changed nothing (its SQL ran with `default_transaction_read_only=on`):
  - The record `update-20261103T152357Z\update.json`: `COMPLETE`, 15:23:50 to 15:28:44 UTC, commit `22ab71a` (the app's previous install `b9388e5`), the migration `0032_ai_backtest` to `0033_event_trader` in one attempt. Nine services replaced: api, web, the market, execution, evaluation and agent workers, agent-egress, agent-runner and source-fetcher. Its own checks: schema `0033_event_trader`, reconciliation `OK`, the five pages answering 200, the agents `ENABLED` with their check passed, no problem. The backup is 80,977,628 bytes. Its tidy deleted this plan's merged branch on GitHub.
  - All 10 containers up with no restart, 9 healthy (the market worker has no health check), each on the image the record names; PostgreSQL was not recreated.
  - The profile in force is the app's new one (seq 28, recorded by `SYSTEM` at 15:27:41 UTC, naming generations 1 to 15 and `TRADER_PROMPT_M11_V6`). Its check (seq 12) `PASSED` at 15:27:54 UTC, 1 of 12 calls: its one probe, on `FUTURES_DECISION_V6` (SC-03), `SUCCEEDED`, and the verification is `VERIFIED`.
  - Generation 11's last decision is the 15:00 bar's, at 15:15:15 UTC. Its decisions a UTC day over its whole days, 2026-10-29 to 2026-11-02: 112, 104, 99, 106 and 103, each day with its 96 bar decisions and the rest on sharp moves and fills. In all 642, from 2026-10-28 13:45 to 2026-11-03 15:15 UTC, with no bar missed.
  - No decision at the 15:30 bar, as the schedule says. The agent worker logged no `Traceback`, `ERROR` or failure from its start at 15:27:38 to 15:35:37 UTC. All five pages answered 200. Home's trader card read "Next decision 17:00 · in 23 min, or sooner on a closed trade, a big move, a range break or a funding jump" (Budapest time, so 16:00 UTC).
  - The first generation-14 decision, read at 16:09 to 16:11 UTC: the 16:00 bar's, `BAR_4H` with nothing else due, queued at 16:00:07 and finished at 16:00:20 UTC in one model step. `HOLD`, with the forecast `UP` at `LOW` and the reason `LIMIT_OR_COOLDOWN` (the entry cooldown after the stop-out below); the workflow `SUCCEEDED`. Its context's schedule block named the next 4-hour decision at 20:00 UTC, the move's reference 77,664.30, and the next hour's range of 76,351.60 to 77,857.00. No generation-11 workflow ran after the install, and none started at the 15:30 and 15:45 bars or after the 15:41 close, as the schedule says. The worker logged no `Traceback`, `ERROR` or failure to 16:09 UTC. Home then read "Next decision 21:00 · in 3 h 50 min, …" (20:00 UTC).
  - The first event decision, read at 16:20 UTC: `TRADE_CLOSED` at the 16:15 bar close, the moment the entry cooldown after that stop-out ended (`event_at` 16:15:00 UTC, not late) with the account flat, nothing else due. Queued at 16:15:02 and finished at 16:15:16 UTC; `HOLD`, the forecast `UP` at `LOW`, the reason `NO_EDGE`; the workflow `SUCCEEDED`. Its trigger names the closed position, its `STOP` close at 15:41:17 UTC and the cooldown's end. The worker logged no `Traceback`, `ERROR` or failure from 16:10 to 16:20 UTC.
  - Generation 11's last position, its short of 14:03 UTC (a `SHARP_MOVE` entry), closed at its stop at 15:41:17 UTC by the engine's protection: −20.76 USDT realized and 3.87 in fees, −24.63 (−1.0 R) on Trades.
  - `OBSERVED`, a small gap, not fixed: the schedule block's move `distance` (4 × the 15-minute ATR, `futures_schedule.shown`) goes into the prompt unrounded, with about 95 decimal places. It costs prompt bytes and changes nothing else; rounding it to cents with the next engine update is `PROPOSED`.
- 2026-11-07, §9 step 5: **O1 `PASS`** on its three whole UTC days, 2026-11-04 to 2026-11-06. `OBSERVED` read-only on the PC by the thread's device session from 08:03 to 08:10 UTC, which changed nothing (its SQL ran with `default_transaction_read_only=on`):
  - Decisions a day: 11, 9 and 6, each within 4 to 16; the most on one day 11, against the 32. By trigger: 11-04 `BAR_4H` 6, `RANGE_BREAK` 3, `MOVE` 2; 11-05 `BAR_4H` 6, `MOVE` 2, `TRADE_CLOSED` 1; 11-06 `BAR_4H` 6. No `FUNDING_JUMP`, and no trigger outside the five kinds. All 26 are `FUTURES_DECISION_V6` and `SUCCEEDED`; so did the window's three agents' checks. The mean, 8.7 a day, is the 8 to 9 of §4.2.
  - Each of the 18 four-hour moments had its `BAR_4H` decision, started 0 to 24 s after the moment, `late_seconds` 0 every time, so no waiting reason was needed. The two slowest starts (14 and 15 s, at 2026-11-04 and 11-05 00:00 UTC) each coincide with the agent worker taking its lease again (`WORKER_STARTED` at 00:00:23 and 00:00:15 UTC, no update running); the cause is `NOT READ`, since those containers' logs went with later updates. It did not recur at the 11-06 and 11-07 midnights.
  - The run stayed `RUNNING`, with no pause, latch or stop. The agents' switch left `ENABLED` only during two updates' profile checks (13 s and 14 s, at 2026-11-04 13:14 and 11-05 18:21 UTC), at no four-hour moment.
  - One trade, generation 14's first: a `MOVE` decision entered short at 1x at 2026-11-05 12:45:25 UTC (79,759.92, 0.041 BTC, stop 80,271.8, take profit 78,992.2, time exit 16:45), which closed at its take profit at 14:38:48 UTC, its exit fill 78,996.50 (1 bp of slippage): 31.30 USDT before 3.25 of fees. The `TRADE_CLOSED` decision followed at 15:00:11 UTC. The take profit filled as before.
  - Six updates ran in the window, all `COMPLETE` (`0034` to `0036`; ExecPlans 0054, 0052's generation 16 and 0055); a seventh attempt stopped before its backup. None changed the trader or its schedule.
  - The agent worker's log, from its current container's start on 2026-11-05 22:08:50 UTC: 64,279 lines with no `Traceback`, `ERROR`, `Exception` or failure line from the trader. The window before that, about 46 of its 72 hours, is `NOT READ`: those containers were replaced by updates.
  - Still open: the schedule block's unrounded `distance` (above), unchanged by the updates since.
- 2026-11-12, §9 step 6: **M1 read descriptively**, short of its sample, over generation 14's whole run. ExecPlan 0059's install (2026-11-10 17:30 UTC) stopped asking the trader; generation 14's last decision was the `BAR_4H` of 16:00 UTC that day, and generation 19 (ExecPlan 0058) decided nothing live. Read on the owner's "don't wait for anything on the future" (2026-11-12 09:23 UTC, [DECISIONS](../../DECISIONS.md#2026-11-12--read-now-what-was-waiting-on-a-date)) instead of the 2026-11-26 check-in. `OBSERVED` read-only on the PC from 09:29 to 09:30 UTC (one READ ONLY transaction, rolled back; the app at `93a2112`, schema `0040_main_rule`), `CALCULATED` in the cloud with `app.evaluation.bootstrap.interval` (mean block 2, 10,000 resamples, seed `derive_seed("SCHEDULE_V1", "M1")`; S1 seed `derive_seed("SCHEDULE_V1", "S1")`); the query, the script and their outputs are in the project's files (`catch-up/`):
  - 56 decisions from 2026-11-03 16:00 to 2026-11-10 16:00 UTC, every one `SCORED` at 15, 60, 240 and 1,440 minutes, none left out: `BAR_4H` 43, `MOVE` 7, `RANGE_BREAK` 4, `TRADE_CLOSED` 2; 55 `HOLD` at `LOW` and 1 `ENTER_SHORT` at `MEDIUM`; 24 `UP`, 32 `DOWN`; the stated direction the last hour's in 48 of 56. **39 decisive** calls at 1 hour, against the 120 the reading needed.
  - **M1** (descriptive, no verdict): the paired mean at 60 minutes −0.0358% an hour (trader −0.0050%, the last-hour rule +0.0307%), 95% −0.1172 to +0.0230, 99.375% −0.1575 to +0.0347. Read as a verdict it would be `NO_DIFFERENCE`.
  - **S1**, 240 minutes against the last-4-hours rule: −0.0755% (trader −0.0632%, rule +0.0123%), 95% −0.3448 to +0.1941. **S2**: at 1 hour the trader 18 right and 21 wrong (46.2%, Wilson 32 to 61%), the last-hour rule the same; at 4 hours the trader 18 and 24 (42.9%), the last-4-hours rule 19 and 22 (46.3%). **S3**, at 1 hour: `BAR_4H` 14 and 13 (paired −0.047%), `MOVE` 1 and 5, `RANGE_BREAK` 1 and 3, `TRADE_CLOSED` 2 and 0 (each of the events paired 0.000%: the trader called the last hour's way every time). **S4**: one trade, the short of 2026-11-05 (above); the result checks `TOO_FEW` on its one entry. S5 and S6: read by O1 above; not read again.
  - Generation 11's M1 over its whole run, descriptive and never paired with these (TR-36's method, as the 2026-11-16 reading was to compute it): 631 calls after dropping the 11 `FILL` decisions made within a minute of the one before on the same inputs; paired on 620 hours +0.0101% an hour (trader +0.0392%, rule +0.0292%), 95% −0.0227 to +0.0447 (circular blocks of 8). Recorded in [TRADING](../../TRADING.md#the-record-so-far).
  - This closes the plan's measure: under `FUTURES_POLICY_V2` the trader is not asked, so M1 has no later reading.
