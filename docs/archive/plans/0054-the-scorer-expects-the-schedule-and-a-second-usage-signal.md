# ExecPlan 0054 — The scorer expects the schedule's moments, and a second usage-limit signal

**Status: APPROVED by the owner on 2026-11-03**, in the project thread "Analyze the agents' setup for performance": after the thread's review of the agents' setup, the owner picked the recommended "Small fixes now" on its decision card at 19:42:32 UTC ("One small update fixes the scorer's missed bars and the usage-limit signal; the trader is untouched and its test keeps running. I also read the veto's numbers on the PC, read-only.").

Labels: `OBSERVED`, `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `CALCULATED`, `NOT RUN`.

## 1. Goal

Two faults that cost nothing to fix and change nothing the trader sees:

1. Since generation 14 decides every four hours and on events ([ExecPlan 0053](0053-the-trader-every-four-hours-and-on-events.md)), the scorer (`DECISION_SCORING_V1`) still expects a decision at every finished 15-minute bar while the run is running or a position is open. The Scores page, the coach (its `scores:missed` row) and the decision reviewer (its day card) read about 88 bars a day as missed ([0053 §11](0053-the-trader-every-four-hours-and-on-events.md#11-failure-and-rollback)).
2. The live agents recognise Codex's usage limit only by the English sentence in a refused call's error text (`runner/jsonl.py`). The runner already reads the plan's limits every 10 minutes through the app server, but only the replay, the backtest and the Provider card use that reading.

Observable outcome:
- A bar is expected only when its close is one of the schedule's four-hour moments (00, 04, 08, 12, 16 and 20 UTC) and the run was running without a cause or a position was open. A bar an event decided at reads as decided; a moment with no decision reads as missed. The scorer stores every new score under `DECISION_SCORING_V2`; the scores already stored keep V1's flag and name V1.
- A Codex reading whose main snapshot names a reached limit, or that says ordinary usage is not allowed, sets the usage-limit block a refused call sets, once, never over a block that stands, with `source` `CODEX_APP_SERVER`, the reading's reason and its id in the `QUOTA_BLOCKED` event. The agents' check retries and the first completed call clears it, as after a refusal. A completed call that cleared a reading's block contradicts that reading: no reading blocks again until a later one has named no reached limit.

## 2. What the app has

`OBSERVED` on the owner's PC on 2026-11-03 at 19:48 UTC, read-only (every statement in a `default_transaction_read_only` session):
- Since 15:15 UTC, 15 finished bars were scored at 60 minutes, every one `expected`; 3 decided (15:15 by generation 11, 16:00 `BAR_4H` and 16:15 `TRADE_CLOSED` by generation 14), 12 `NO_JOB`. None of the 12 was a moment the schedule called for.
- Generation 14's two calls: completed, 11.9 s on average (12.8 s at most), 16,685 input tokens on average, none cached, 319 output, 0 reasoning. Each started about 1 s after its workflow; no replay or backtest call overlapped.
- The entry veto: 1 call ever (2026-11-02 16:00 UTC), completed in 11.4 s, `GO`, recorded 37 s after the request (about 25 s of it waiting behind the trader's 16:00 decision); 0 requests went ahead as `NO_ANSWER`.
- The newest Codex reading (19:43 UTC): the 5-hour window 0% used, the weekly window 51%, `reached` null, `ordinary_usage_allowed` true. No `QUOTA_BLOCKED` or `QUOTA_CLEARED` event has ever been recorded.

`VERIFIED` in code at `main` `2fd454a`: `decision_scores.subject_facts` sets `expected` from `run_expected` and the open position alone; `score_context.trader_scores_lean` leaves the missed bars out of the trader's view ([AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md)); `usage.block` is called only from the orchestrator's refused calls; `usage_readings.windows` already turns the main snapshot's `reached` into a `REJECTED` status for the pages.

## 3. Scope

In: `DECISION_SCORING_V2` (`app.futures.scoring`) and migration `0034_expected_bars`; `futures_schedule.scheduled_close`; the scorer's `expected` (`decision_scores`); `usage_readings.codex_limit_reached`, `usage.from_reading` and the worker's reading step; the schema lists in `app.db`; tests and documents.

Out: the trader, its prompt, context, model and generation 14; the coach's and the decision reviewer's prompts (both still say "every 15 minutes": a prompt change is a new generation, for the next trader bundle); the schedule block's unrounded distance (it is in the trader's context); the pages (the Scores page's "Bars without a decision" keeps its wording, which V2's rule makes true again); the veto's effort; any provider change.

## 4. Design

- **`DECISION_SCORING_V2`** is V1 with three keys changed and a `carried` note: `subjects.bar_expected` ("the run running without a cause or a position open at a close that is a moment of the installed trader's schedule"), `subjects.bar_moments` (`EVERY_4H_AND_EVENTS_V1`'s 4-hour boundaries; an event's bar is decided, not expected; a moment decided in a later bar leaves its own bar missed) and `scorecard.missed`. Every value the scorer computes with (checkpoints, test trades, labels, limits) is V1's. It is `PROPOSED` as V1 is, fixed before its first score.
- **Which scores carry V2.** The scorer stores under the definition in force, `scoring.CURRENT`, and fails closed until migration `0034` has stored V2 with this code's hash (`SCORING_NOT_STORED`), as V1 did before `0024`. Scores are immutable: the bars scored between generation 14's start (2026-11-03 15:15 UTC) and the install keep V1's `expected`, so the 24-hour window is clean a day after the install and the 7-day window a week after. Each checkpoint is its own score, so a bar's checkpoints scored after the install name V2 while its earlier ones name V1; for generation 11's last bars (before 15:15 UTC) that means their 24-hour scores read a bar between moments as not expected. That touches only the missed-bar counts of those checkpoints, for one day; no decision's score changes.
- **The moment rule.** `scheduled_close(close)` is true when the close is a whole multiple of four hours from the epoch, which is `next_base`'s and `bar_4h`'s boundary. A boundary the trader decided at later in the hour (`BAR_4H` late) leaves its own bar missed and its later bar decided: V2 says so, and that is what happened.
- **The second usage signal.** `usage_readings.codex_limit_reached(reading)` names the reason from a good reading: the main snapshot's `reached` (a string, as the app server's `rateLimitReachedType`), else `ordinary_usage_allowed` false. A secondary limit's own `reached` stays the pages' and the replay gate's. The worker calls `usage.from_reading` in its own transaction right after it stores a good reading; `from_reading` does nothing while a block stands, so a reading taken every 10 minutes during a block adds no event and leaves the retry where the first signal put it. `NOT VERIFIED`: no reading has been taken while the limit held, so the exact `rateLimitReachedType` values are unknown; any non-empty value is read as reached, and a false block is cleared by the check's first completed call, 10 minutes later. So that a value that stays set while calls work cannot stop the agents every 10 minutes, a reading's block that a completed call cleared (`QUOTA_CLEARED` with `CALL_COMPLETED`) holds further readings back until a good reading stored after it (by id, not by clock) names no reached limit; refused calls block as before. The worst case is therefore one false block of at most 10 minutes per spell in which the readings say "reached".

### 4.1 The trading review (TRADING.md)

Classified as **a yardstick**, by the [trading-review](../../../.claude/skills/trading-review/SKILL.md) procedure: the scorecard's missed-bar row is corrected; the trader's prompt, context, tools, model, effort, provider and policy are unchanged, so generation 14's paired test does not restart and the 16 November read is untouched. One path reaches the trader indirectly: the coach writes its note from the scorecard's rows, `scores:missed` among them, and the trader reads the note in force as model-authored advice. With V2 the coach stops reading about 88 false misses a day; that corrects the data of an input the coach already had, and the trader is shown nothing new or differently (opinion; the coach's notes have all been `EITHER` or `LOW` so far, `OBSERVED` in the setup review).

1. **Rules.** No exit, size, limit, stop or hold changes; code keeps all of them. The usage signal can only stop model calls earlier, never start one, and code's protection runs every second either way (rule 11).
2. **Costs.** No trade is added or removed; nothing to weigh.
3. **Horizon.** Unchanged: the schedule's moments are generation 14's own (`VERIFIED` in `futures_schedule`).
4. **The model's place.** Unchanged.
5. **The yardstick.** V2 counts a missed bar only where the schedule called for a decision; the decisions' and the bars' labels, checkpoints and test trades are V1's, so every paired comparison keeps its meaning.
6. **Pre-registration.** No new measure or pass rule. The 16 November read and generation 14's own reads use the decisions' scores, which V2 leaves as V1 computes them.
7. **The trial ledger.** No new variant.
8. **The clock and the cost.** No reset; no model call is added; a contradicted usage reading costs at most one 10-minute pause of model calls (§4).

## 5. Authority

Nothing an agent may do changes. The block is set by `SYSTEM` as before; no grant, tool, template, budget or prompt changes.

## 6. Requirements and tests

| ID | Requirement | Test |
| --- | --- | --- |
| X1 | `0034` stores exactly the code's V2; V1's row and hash are untouched; V2 differs from V1 only in the expected bars' keys | `test_m11_scores_unit.py::test_migration_0034_froze_v2_which_changes_only_which_bars_are_expected` |
| X2 | Only the 4-hour boundaries are moments | `test_m11_scores_unit.py::test_a_bar_is_expected_only_at_the_schedules_four_hour_moments` |
| X3 | An event's bar is decided and not expected; a moment with no decision is the one missed bar | `test_m11_scores_db.py::test_only_a_four_hour_moment_without_a_decision_is_a_missed_bar` |
| X4 | Bars between moments are not expected, flat or in a position | `test_m11_scores_db.py`'s first two tests and the scorecard test, updated |
| X5 | `0034` rolls back only before a V2 score; at `0033` the V2 scorer stores nothing | `test_m11_scores_db.py::test_0034_rolls_back_only_before_a_score_under_v2_and_applies_again` |
| X6 | A reached reading names its reason; a calm, failed or secondary-limit reading names none | `test_m11_usage_signal_unit.py` |
| X7 | The worker's reading sets the block once with its source and reading id, never over a standing block; the first completed call clears it; a reading a completed call contradicted blocks again only after a calm reading; another provider never reads Codex | `test_m11_usage_signal_db.py` |

## 7. Official sources

The app server's `account/rateLimits/read` response (`rateLimitReachedType`, `ordinaryUsageAllowed`), as [ExecPlan 0049 §5.4](0049-choose-the-agents-provider-and-see-usage.md) recorded it for the pinned Codex; no new dependency.

## 8. Data and trust boundaries

One new row in `execution_definitions`; no table, column, view, guard or grant. Runtime events gain optional detail keys on a reading's block (`source`, `reason`, `read_at`, `reading_id`); `usage_readings` returns the stored reading's id (`INSERT ... RETURNING id`, which the agent identity's existing `SELECT` grant allows).

## 9. Implementation sequence

1. V2, the moment rule, the scorer's `expected`; migration `0034`; the schema lists.
2. The usage signal in `usage_readings`, `usage` and the worker.
3. Tests; the cloud gates; one pull request; merge on the owner's word in the thread.
4. The owner double-clicks `update-app.cmd`; the thread checks, read-only: schema `0034_expected_bars`, V2 stored, the scorer's state `CURRENT` with `in_force`, new bar scores naming V2 with `expected` only at the moments.

## 10. Verification commands

From `services/engine`, on the scratch cluster ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)):

```bash
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
.venv/bin/python -m app.futures.scoring   # V1's seed line (0024), then V2's (0034)
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_scores_unit.py tests/test_m11_usage_signal_unit.py tests/test_m11_scores_db.py tests/test_m11_usage_signal_db.py
```

## 11. Failure and rollback

- The scorer stores nothing between the new engine's start and the migration (`SCORING_NOT_STORED`), a few minutes inside the update; the subjects wait and are scored after it.
- `0034` downgrades while no score names V2, and refuses after ("fix forward").
- A false usage block costs at most the check's 10-minute retry of model calls, once per spell of "reached" readings; positions keep code's protection.

## 12. Q01–Q10

Small scoped change: the affected gates are the cloud tests (lint, unit, database) and the update's own checks on the PC. No page, no browser suite, no money path (no review of a money path is needed: no ledger, order, sizing or protection code changes).

## 13. Decision log

- 2026-11-03, the thread under the owner's pick: V2 rather than a change to V1 (scores are immutable and every score names its definition); the moment rule from the schedule's own boundary rather than from the stored decisions (a missed moment must stay visible); the block only from the main snapshot and `ordinaryUsageAllowed` (a secondary limit is not the plan's); a contradicted reading holds back further readings' blocks until a calm one (the reading's meaning is `NOT VERIFIED`, and a completed call is the stronger evidence), compared by the readings' ids so a clock step cannot reopen it.

## 14. Progress

- 2026-11-03: `IMPLEMENTED` on branch `claude/project-thread-3r6uaq`.
- 2026-11-03, the cloud checks (`VERIFIED` unless marked), scratch PostgreSQL 16 ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)):
  - Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; `python -m app.futures.scoring` prints V1's seed line, then V2's (`e2809f22…638cbfd7`).
  - pytest without a database: `2 failed, 1245 passed, 488 skipped, 462 errors`, the two failures the documented baseline's (`test_api.py`'s status and `test_database.py`'s migrated database, both needing a database).
  - On a fresh database, the files that store readings or scores (`test_agent_providers_db.py`, `test_agent_providers_units.py`, `test_backtest_lane_db.py`, `test_m11_replay_db.py`, `test_m11_usage_signal_unit.py`, `test_m11_usage_signal_db.py`, `test_m11_scores_unit.py`, `test_m11_scores_db.py`): `3 failed, 99 passed`. The three are `test_m11_scores_db.py`'s that COMMANDS records for `main`, failing at the same assertions as on `main` at `2fd454a` (`11 passed, 3 failed` there before this plan's tests). `test_m11_twins_db.py`, `test_m11_usage_signal_db.py` and `test_m11_veto_db.py`: `45 passed`; `test_m5_orchestrator.py`: `32 passed`; `test_m5_runtime.py` and `test_m5_schema.py`: `26 passed`.
  - The web: ESLint without the build's output, `tsc --noEmit`, Prettier on the changed spec, Vitest `src/futures/scores.test.tsx` (`9 passed`), `api:check` (`Generated TypeScript API types match`) and the build.
  - The browser chain on a database seeded at 20:51:06 UTC, with the SYNTHETIC feed, the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the built web server: `reviews.spec.ts` 5 passed; `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` 16 passed; `scores.spec.ts` 4 passed (Settings shows `DECISION_SCORING_V2, as installed`); `checks.spec.ts` 3 passed. Every score the run stored names V2; of the scored bars, only those that closed at 16:00 and 20:00 UTC are expected (both `NO_JOB`: the fixture runs no trader), and the decided bars between them are decided and not expected.
  - `OBSERVED`: the first chain, seeded at 20:31:05 UTC, failed `scores.spec.ts`'s first test on the fixture's recorded clock limit: the SYNTHETIC walk reached the open long's tightened stop at 20:33:01, before the toast test's exit. The second seed's minute was picked from the walk (`walk` in `tests/m11_browser_fixture.py`), where its low stayed above the predicted stop.
  - `OBSERVED`: a first whole run on a shared cluster was disturbed by this session's parallel runs on another database of that cluster ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)); every file it failed passed when run alone, as above.
  - The whole engine suite on a fresh database, alone on its cluster, 20:52 to 21:52 UTC: `7 failed, 2116 passed, 74 errors`, every one the known cloud baseline ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). The 74 errors are `test_m1_account.py`'s 13 (it names the host `postgres`) and the research store's 61. The failures: `test_api.py`'s status test; `test_m11_scores_db.py`'s three `main` failures, as above; `test_m2_stream_continuity.py`'s rotations under load (`QUEUE_OVERLOAD`); `test_m6_schema.py`'s downgrade, which ran `0034`'s downgrade and the ones below it and stopped at the M6 kind check on rows the earlier M6 suites left; and `test_m2_reference_checks.py`'s clock-request test (`[rest]`), a timing check that passed alone afterwards (`4 passed`).
  - `NOT RUN` in the cloud, and done by the update or its check on the PC: the Docker build, the update itself, a Codex reading taken while the plan's limit holds.
- 2026-11-03 22:05:28 UTC, §9 step 3: [#174](https://github.com/MentorAliu/adaptive_spot_lab/pull/174) merged as `0cd1ba0` on the owner's "Merge it" on the thread's card (22:04:56 UTC), after the whole suite above.
- 2026-11-03 and 2026-11-04, §9 step 4: the owner's double-clicks of `update-app.cmd` ("Done" at 08:08 UTC on 2026-11-04). `OBSERVED` read-only on the PC on 2026-11-04 from 08:12 to 08:18 UTC by the thread's device session, which changed nothing (its SQL ran with `default_transaction_read_only=on`):
  - The record `update-20261103T220638Z\update.json`: `COMPLETE`, 2026-11-03 22:06:30 to 22:11:45 UTC, commit `0cd1ba0` (the app's previous install `22ab71a`), the migration `0033_event_trader` to `0034_expected_bars` in one attempt. Nine services replaced: api, web, the market, execution, evaluation and agent workers, agent-egress, agent-runner and source-fetcher. Its own checks: schema `0034_expected_bars`, reconciliation `OK`, the five pages answering 200, the agents `ENABLED` with their check passed, no problem. The backup is 81,564,790 bytes. Its tidy deleted this plan's merged branch and one other merged branch on GitHub.
  - A second double-click ran the same commit again: `update-20261104T071537Z\update.json`, `COMPLETE`, 2026-11-04 07:15:29 to 07:20:12 UTC, the schema `0034_expected_bars` before and after, the same nine services rebuilt and replaced with no setting changed, the same checks passed, nothing deleted on GitHub.
  - The folder at `0cd1ba0`, clean. All 10 containers up, 9 healthy (the market worker has no health check); PostgreSQL not recreated.
  - The schema `0034_expected_bars`. `execution_definitions` holds `DECISION_SCORING_V1` (`b61dae9f…`) and `DECISION_SCORING_V2` (`e2809f22…638cbfd7`), the code's V2, so the definition in force is stored.
  - The switch: the last V1 score was recorded at 22:00:02 UTC, before the update, and the first V2 score at 22:20:09 UTC, after it; 222 V2 scores followed to 08:15:37 UTC on 2026-11-04, and none under V1. Every score since the second run names V2 (12 bar scores, 3 at each checkpoint, and 5 decision scores).
  - The 1-hour bar scores of the bars closing since 2026-11-03 15:15 UTC. Under V1, to the 21:00 close: 20 bars expected and not decided from 15:30 to 21:00 (the false misses this plan ends; they stay as recorded), the 16:00 and 20:00 moments expected and decided, and 2 more decided bars (the 15:15 close, generation 11's last, and the 16:15 `TRADE_CLOSED` decision). Under V2, from the 21:15 close to the 07:00 close: 36 bars neither expected nor decided, 2 decided and not expected (the `MOVE` decisions at 03:00 and 06:30 UTC), and the 00:00 and 04:00 moments expected and decided. No V2 bar is expected and undecided.
  - Every expected V2 bar score at any checkpoint, 10 in all, is at 00:00, 04:00, 08:00 or 20:00 UTC and decided: the 24-hour scores of the 2026-11-03 00:00, 04:00 and 08:00 bars, the 4-hour score of its 20:00 bar, and the 15-minute, 1-hour and 4-hour scores of the 2026-11-04 00:00 and 04:00 bars.
  - Generation 14's decisions on 2026-11-04 to 08:00 UTC: `BAR_4H` at 00:00, 04:00 and 08:00 and `MOVE` at 03:00 and 06:30, all `HOLD`.
  - The usage signal: the newest three Codex readings (07:45 to 08:05 UTC) `ok`, the 5-hour window at 4 to 5% and the weekly at 1%, `reached` null, `ordinary_usage_allowed` true. No `QUOTA_BLOCKED` or `QUOTA_CLEARED` event has been recorded, and the worker logged no `agent_usage_limit_read`. The signal's behaviour while the limit holds stays `NOT VERIFIED`.
  - The agent worker logged 916 lines from its start at 07:19:07 UTC to 08:12 UTC, 17 of them `agent_decision_score`, with no `Traceback`, `ERROR` or failure. `NOT RUN`: its log from the first run to the second, which went with its container.
  - `NOT RUN`: Settings' scorer row. The page fills it in the browser (the served HTML holds none of its texts) and no browser was opened; its "as installed" reads the stored definition above.
