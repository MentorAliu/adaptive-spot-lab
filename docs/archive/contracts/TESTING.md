# Verification strategy and requirement coverage

## Status and rule

How the app is tested now. The milestone evidence maps and run records up to M10's update 1 are history, kept verbatim in [archive/TESTING.md](../TESTING.md); the commands are in [COMMANDS](../../COMMANDS.md).

- **Where tests run.** Every check runs in a cloud session on the change's own tree: the web lint, typecheck, unit tests and production build; Ruff, the OpenAPI drift check and pytest without a database; pytest and the browser suites against a scratch PostgreSQL cluster. Since M8 the owner's PC runs no test harness: it runs only the update file's own checks when the owner double-clicks it ([ExecPlan 0031 §4.8](../plans/0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). No multi-hour run on the PC.
- **Isolation.** Database tests run only on a disposable cluster that holds nothing but `asl_m1_` databases (`asl_m1_m6_` for the agent and research suites), with `ASL_TEST_ISOLATED=1` set; without it the suites refuse their test-only overrides. They never address the normal app, its database, `.env`, `secrets/` or `codex_home`. Scratch password files are random values written for the run. A finished run's databases, clusters, servers and Docker resources are removed by exact name once the evidence is recorded ([DOCKER](DOCKER.md#cleaning-up-disposable-resources)).
- **Fixtures.** Deterministic and labeled: model answers are scripted (`OFFLINE_TEST`), provider answers SYNTHETIC or a loopback mock, market values labeled fixtures. Ordinary tests contact no paid model, no public endpoint and no private exchange endpoint; public connectivity checks are explicit, bounded and separate. Production or forward ledger history is never reset by test setup.
- **Kinds of evidence.** Keep unit/integration/browser tests, provider connectivity checks, synthetic workload probes, simulation evaluation and documentation checks apart in every report. A mocked API test cannot establish real integration or trading profitability.
- **Results.** A check that did not run, or was skipped, is NOT RUN, never a pass. Each update's plan records the commands, their results and what was not run; a failure that `main` already shows is named as such, never hidden.

## Continuous integration

The repository has no hosted CI. The owner had it removed on 2026-10-17 ([DECISIONS](../../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository)): the GitHub Actions workflow of [ExecPlan 0016](../plans/0016-ci-checks.md) never ran on GitHub, and its files were deleted. ExecPlan 0016 keeps the design and names the commit to restore it from.

Until CI is added back, the checks run in the cloud session that changes the code, and a pull request's body records which ran, with their results, and which did not. The owner's PC runs no test suite or harness since M8; it runs the update file's own checks. Wherever a contract asks for executed CI checks, the same checks run in the cloud against the exact release source stand in until CI exists again.

## Requirement-to-test map

| Requirement | Required evidence |
|---|---|
| P01 Paper-only boundary | No live/private exchange credentials/routes/adapters; deny signed API destinations; no hidden live config; runtime image/config inspection |
| P02 spot scope (BTC, SOL and the coins the installed policy names) | Reject other symbols, shorts, borrowing and unsupported instrument/filter states; current instrument snapshots |
| P03 Initial funding/top-ups | Initialization exactly once, decimal validation, idempotent concurrent topups, pending valuation, flow/units atomicity, no startup reseed |
| P04 Independent risk | Boundary/rounding tests, portfolio/pending-order caps, model cannot raise limits, daily/global latch persistence, gapped-stop limitation |
| P05 Paper broker/replay | Order/fill state machine, partials/fees/reservations, unknown commit/restart, same recorded events produce same financial state |
| P06 Data integrity | Duplicate/gap/revision/out-of-order tests, finalized-bar timing, point-in-time inputs, no synthetic fallback |
| P07 Adaptation/approval | Exact approved versions, blocked range expansion, original exits retained, shadows isolated, switches only under frozen rules |
| P08 AI incremental evaluation | Recorded provider parity, non-AI and fixed baselines, paired comparisons, honest negative/inconclusive reports |
| P09 Required frontend/preset | Official skills loaded, actual preset retained, no duplicate primitives, SSR/hydration/forms/table/chart integration and browser evidence |
| P10 Docker/operations | Clean build, health/migration ordering, restart/fencing, forced-kill recovery, isolated backup restore, loopback ports/mounts |
| P11 Subscription runtime | Supported auth persistence, no paid fallback, tool isolation/injection tests, quota/timeouts/late jobs, no leaked credentials |
| P12 Honest results | Topups do not increase NAV return, no drawdown reset, cost/valuation unknowns visible, benchmark matched flows, modeled/synthetic labels |

## Financial property tests

Generate bounded event sequences with deposits, accepted/rejected orders, partial fills, fees, cancellations and restarts. After every committed transition verify per-asset journal balance, nonnegative available funds/holdings, reservation consistency, unique effects, projection reconciliation and finite values. Random test inputs are synthetic and labeled; property generation is not market evidence.

Test that arbitrary valid external contributions leave NAV unchanged at a fixed pre-flow mark and leave trading P&L unchanged. Test precision residual treatment and near-zero/invalid equity cases. Changes in prices can change P&L; changes in deposits cannot. High-water NAV and latched pauses survive deposits, UTC boundaries, restarts and reconstruction.

Verify two simultaneous orders cannot both spend the same free balance or risk budget. Kill a worker between reservation and fill/acknowledgment; restart and reconcile without duplicate financial posting. Reject a stale fenced worker even if it still holds an old in-memory lease.

## Strategy/data tests

Use independently calculated indicator fixtures, explicit warm-up and crossover boundaries. Confirm no same-event duplicate entries, no indicators after invalid gaps without recovery, and no execution before information availability. Test simultaneous exit reasons produce one closing intent.

Recorded public-data fixtures include source/version/retention metadata. Keep malformed/gap/latency scenarios separate from clean inputs. Verify a stale quote does not become fresh because a websocket heartbeat or UI render occurred. Historical backfill must not write missed forward trades.

## Agent tests

Use recorded outputs for normal tests; malformed JSON, unknown candidate/evidence IDs, stale snapshots, incorrect schema, oversized output, forbidden tool commands and attempts to change risk are rejected. Verify progress JSONL is not parsed as a final decision.

Explicit opt-in runtime smoke tests verify actual installed CLI/auth/profile. Include malicious evidence requesting file reads, credential extraction, shell/alternative exec, arbitrary browsing and ledger mutation. A denial written in the model's answer is not sufficient; prove the tool/process side effect could not occur. Test quota/auth errors, cancellation, process-tree cleanup and no API fallback.

## Frontend/browser tests

Use actual installed official shadcn and chart skills for implementation/review. Test server request isolation, no unexpected duplicate hydration fetch, query-key/URL dependencies, auth/cache cleanup, decimal form inputs, backend errors, topup confirmation/retries, strategy approvals and pause/flatten distinctions.

Render the actual preset in a real browser. Verify loading/empty/error/stale states, keyboard/focus behavior, responsive layout, financial number overflow, non-color status cues and chart text alternatives. Test chart mount/unmount/Strict Mode, resizing, symbol/timeframe changes, timestamp units, duplicate bar handling and missing intervals.

Browser integration tests use the real local services/test database where validating end-to-end behavior. Component mocks alone do not pass those checks. Pin Playwright/browser image compatibility [FE-08](REFERENCES.md#fe-08).

## Since ExecPlan 0035: five pages, research off

[ExecPlan 0035](../plans/0035-a-simpler-app-that-trades-by-itself.md) changed what the suites cover, not how they run:

- **Browser.** `e2e/pages.spec.ts` (tag `@pages`) covers the menu of five, the removed pages answering "Page not found", Home's trading status and Settings' five sections with a new run. `e2e/m6.spec.ts` went with the research pages; its fixture stays, because it writes the API samples the web's schema tests parse. M4's approvals phase went; its error phase reads Settings and a run's page. M5 reads the agents' part of Settings and a workflow's page; M7 reads the decision pages, and its `@profile` test reads Settings. The entry pause's Resume is tested in components only: the M7 fixture's pause is on its synthetic test run, and Settings shows the main account's limits.
- **Engine.** The research modules and their tests stay until [ExecPlan 0034](../plans/0034-app-cleanup.md)'s part 3. The agent suites prove that the worker starts no research and ends what was open with `RESEARCH_OFF`; the promotion tests start a promotion themselves, since the scheduler no longer does.
- **Update file.** The model (`tools/m8/update-model.ps1`) covers the retirement of the research containers and their network: by exact label and id after the main services, the stopped containers too, and another Compose project's containers and network of the same names left alone; a refused container or network removal, a network that cannot be read, and a container or network that remains are its failure cases.

## Since ExecPlan 0037: times in the viewer's zone

[ExecPlan 0037](../plans/0037-clear-values-in-local-time.md) writes every time in the browser's own zone, so a browser's zone is now part of a test's setup:

- **Browser.** `playwright.config.ts` sets `timezoneId: "UTC"`, so every suite reads times as before; a test that expects a time builds it with `formatDateTime` of `src/lib/display.ts` in its browser's zone. `e2e/local-time.spec.ts` (tag `@local-time`, in the M7 decisions phase) sets `Europe/Budapest` itself and checks the first page written in UTC, the switch to Budapest time without a hydration or console error, the cookie, the next page written in Budapest time by the server, a time's hover text, and the times of a decision draft and of Home.
- **Unit.** `src/lib/display.test.ts` covers each value format and the zone rules, summer and winter time included; `src/components/time-zone-provider.test.tsx` the server render in UTC, hydration without a mismatch and the switch; `src/lib/chart-time.test.ts` the charts' time labels.

## Since ExecPlan 0038: retention's payload search

[ExecPlan 0038](../plans/0038-faster-market-data-cleanup.md) adds `tests/test_m2_retention_cost.py` (database suite): a deleted observation's payload goes in the same call and a shared one with its last observation; kept evidence keeps its payload and the sweep passes it once, 200 a call; orphans without an observation go through the sweep and a younger one stays; the manifest's digest; no identity reads the sweep's position; a collection gap names its slowest call, and (database-free) a call still running counts. `tests/test_m2_retention_faults.py` names the new function's lines (25 for the observation delete, 49 for the payload delete). `app.execution.fixtures.reset_state` reseeds the sweep's row with the other singletons.

## Since ExecPlan 0039: the futures account

[ExecPlan 0039 §6](../plans/0039-bitcoin-futures-on-paper.md#6-requirements-and-tests)'s requirements and where part B tests them; the results are in [0039 §15](../plans/0039-bitcoin-futures-on-paper.md#15-progress).

| Requirement | Tests |
|---|---|
| F1 money posts and reconciles; a top-up moves no P&L | `test_m11_futures_unit.py` (rounding against the account, funding signs, every sized entry within the policy's bounds over generated cases); `test_m11_futures_db.py` (entry, stop, take-profit, time exit, liquidation and funding posted and reconciled; a tampered position found) |
| F2 no fill without a fresh quote; no funding without the settled rate | `test_m11_futures_unit.py` (the book walk waits), `test_m11_futures_db.py` (funding waits; each entry rule refused, stale data included) |
| F3 leverage, missing stop, stop near liquidation, 25th entry, cooldown refused | `test_m11_futures_unit.py`, `test_m11_futures_db.py` (`test_an_entry_is_refused_for_each_rule_the_code_holds`), `test_m11_trader.py` (the schema offers only the policy's sets) |
| F4 protection in code with the agent off; a gapped stop | `test_m11_futures_db.py` (stop on the bid, take-profit on the ask, time exit, liquidation on the mark without a fresh book, exits in any run state) |
| F5 one decision per bar, one after a fill, one at a sharp move, never two | `test_m11_trader.py` (scheduler with a fake clock, coalescing, fills that let the trader act) |
| F6 only the trader starts | `test_m11_trader.py` (`test_in_futures_mode_only_the_trader_starts`) |
| F9 a toast for each fill and funding payment | `src/futures/futures.test.tsx`; `test_m11_futures_api.py` (one feed item per payment); `e2e/pages.spec.ts` (a toast when a trade closes) |
| F10 the chart's marks and lines | `src/perp/perp-chart.test.tsx`; `test_m11_futures_api.py` (the open position's levels are the chart's lines); `e2e/pages.spec.ts` |
| F11 the clean start keeps the old data | `tools/m8/update-model.ps1` (`clean`, `cleanundo`, `cleanrename`, `cleankept`, and from the PC's first install `cleanpc` and `cleanrecreate`); `test_m11_clean_start.py` (the migration from the start keeps the identities' logins, in one transaction) |
| F12 links | `tools/check_links.py` |

F7 and F8 (the runner's isolation and the sign-in) are update 1b's and unchanged. The database privileges of every identity on the futures tables are asserted exactly (`test_each_identity_holds_exactly_its_futures_grants`). No Docker build runs in the cloud, so `test_m11_image_prompts.py` builds the engine image's prompt folder from the Dockerfile's `COPY` lines and computes every code-owned definition from it: part B's runtime image had no M11 folder, so its agent worker never started on the owner's PC. The browser suites of the spot pages the futures app no longer shows (`markets*.spec.ts`, `m10.spec.ts`, the spot Trades phases of `execution.spec.ts`, the spot run in `m4.spec.ts`) are skipped as retired and count as NOT RUN; update 3 removes them with the spot code.

## Since ExecPlan 0042: no sign-in

[ExecPlan 0042](../plans/0042-no-owner-sign-in.md) removes the owner's sign-in: the app funds its account and switches its agents on by itself. Its requirements and their tests are in [§5 of the plan](../plans/0042-no-owner-sign-in.md#5-requirements-and-tests); the money path among them:

| Requirement | Tests |
| --- | --- |
| The initial 10,000 virtual USDT posts once: the exact journal, NAV 100, 100 units, no owner decision, idempotent across starts and concurrent processes, nothing posted while the reconciliation has failed or the account is paused, a refused or held contribution tried again every minute while the API runs, read by its key | `test_m11_no_owner.py` |
| The initial contribution of an account not yet funded cannot be canceled (one an older app left pending beside the funded account can); top-ups stay owner-confirmed | `test_m11_no_owner.py`, `test_m1_account.py`, `src/account/form-states.test.tsx`, `e2e/funding.spec.ts` |
| An owner row needs no session and keeps every other requirement; `0021` up, down and up, and its refused downgrades; on `0020` (the update's minute before the migration) the owner's requests answer `503` `OWNER_SCHEMA_PENDING` and record nothing | `test_m11_no_owner.py`; `test_m7_schema.py`'s downgrade now meets `0021`'s refusal first |
| The agents switch on by themselves, never `ENABLED` without a passing check, and stay off once the owner turns them off; Turn off is offered once the app has the profile a Turn on needs | `test_m5_runtime.py`, `test_m8_in_force.py`, `test_m5_api.py`, `src/agents/controls.test.tsx`, `src/futures/futures.test.tsx` |
| The update accepts the account the app funded and the switch turning itself on, and reads a first state the owner turned off as off | `tools/m8/update-model.ps1` (`clean`, `firston`, `settings`) |

The suites that signed in now open the app directly. `e2e/native-access.spec.ts`, `ssr-isolation.spec.ts` and `logout-recovery.spec.ts` tested the sign-in and are removed. With the API stopped, the decision list and a decision state their own failed read under the page (no session is read first), and Settings its page-level error (`e2e/m7.spec.ts @error`).

## Since ExecPlan 0041 part 1: the twins

[ExecPlan 0041 §6](../plans/0041-twins-and-a-veto.md#6-requirements-and-tests)'s requirements for part 1 and where they are tested; the results are in [0041 §14](../plans/0041-twins-and-a-veto.md#14-progress). T7 to T9 and `0024` are part 2's.

| Requirement | Tests |
| --- | --- |
| T1 each twin's wallet recomputed hourly from its own rows; a difference faults that twin alone; each funding time owed once; a payment the free wallet cannot cover waits and counts as owed | `test_m11_twins_db.py` (a long and a short, a stop, a time exit, a liquidation, funding paid; `test_a_wallet_difference_faults_that_twin_alone_and_shows_only_its_code`; `test_a_funding_time_is_owed_once_after_the_marks_that_announced_it_are_deleted`; `test_funding_the_free_wallet_cannot_cover_waits_and_counts_in_the_hold_twins_value`) |
| T2 a twin's fill, fee, funding, margin and liquidation price equal the trader's | One code path: the twins call `app.futures.money` and the engine's fill and funding functions; `test_m11_twins_unit.py` checks the hold entry's plan against them by property over the best ask and each level's depth, and the cost gate's line by property over prices and spreads; `test_m11_twins_db.py` checks the trend twins' entries against the trader's `size_entry` on the same book. No second code path exists to compare |
| T3 no journal, reservation, `account_state` or futures ledger write; the twin tables written by the execution identity alone | `test_no_twin_module_names_the_owners_ledger`, `test_each_identity_holds_exactly_its_twin_grants_and_the_guards_hold`; the owner's rows unchanged by each twin fill in `test_the_set_starts_once_as_system_and_each_twin_enters_by_its_rule` |
| T4 the hold enters once; the trend rule's cross on complete 1-hour candles after 100 hours, long and short; the gate and the filter at their thresholds; cooldowns, entries and latches; an hour the feed fills later is read again | `test_m11_twins_unit.py` (the rule, the warm-up, the gate and the filter at the line); `test_m11_twins_db.py` (each twin's entry, the gated twin's refusals, an operational refusal, the reverse entry after the cooldown, `test_an_hour_the_feed_fills_later_is_read_again_at_the_next_bar`) |
| T5 stops, time exits and liquidations in the step with the agents off; no fill without a fresh quote; a passing database error retried, not a stop | `test_m11_twins_db.py` (the stop on the bid, the 24-hour exit, the short liquidated on the mark, a lost lease, another set stored; `test_a_lock_wait_is_tried_again_the_next_second_and_faults_the_twin_only_at_the_limit` with a real lock held by another session) |
| T6 the league's counts, P&L, drawdown, time in a trade, paired days and interval from the seed; too few; gap days counted | `test_m11_twins_unit.py` (exact log returns, the window, the seed's interval, too few); `test_m11_twins_db.py` (`test_the_league_reads_every_account_and_says_too_few`, `test_the_league_counts_a_gap_day_from_the_stored_valuations`) |
| T10 the pages in each state, by keyboard and in the accessibility tree; a twin that stops stepping reads as late | `src/futures/twins.test.tsx`; `e2e/twins.spec.ts`; `test_a_live_twin_whose_step_stops_reads_as_late` |
| T11 `0023` up, down and up; the downgrade refused once a twin exists | `test_the_downgrade_is_refused_once_a_twin_exists_and_then_restores_0022` |
| T12 links | `tools/check_links.py` |

The futures suites that count definitions or tables (`test_m11_clean_start.py`, `test_m11_reviews.py`, `test_m11_futures_db.py`) count `0023`'s too. The independent review's findings each have a test that failed on the code before its fix (OBSERVED on 2026-10-25 by reverting each fix alone: the funding search, the retry rule and the gap rule).

## Since ExecPlan 0043 update 1: the decision scores

[ExecPlan 0043 §6](../plans/0043-score-every-decision.md#6-requirements-and-tests)'s requirements for update 1 and where they are tested; the results are in [0043 §14](../plans/0043-score-every-decision.md#14-progress). T9 to T12 are update 2's.

| Requirement | Tests |
| --- | --- |
| T1 the reference, the path and each checkpoint; a missing minute or an unanswered decision waits and is `INCOMPLETE` after seven days, never filled; nothing scored before its last candle is final; a score never changes; another stored definition stores nothing | `test_m11_scores_unit.py` (the frozen definition, the path both ways, the UTC times and signs); `test_m11_scores_db.py` (`test_a_gap_or_an_unanswered_decision_waits_and_is_tried_again_five_minutes_later`, `test_a_checkpoint_still_waiting_a_week_later_is_stored_incomplete_with_its_reason`, `test_an_unanswered_decision_keeps_the_position_it_saw_and_its_execution_unknown`, `test_only_the_agent_identity_stores_a_score_that_describes_its_stored_subject`, `test_nothing_is_scored_unless_the_stored_definition_has_this_codes_hash`) |
| T2 the test trades' end, net and R by hand: target, stop and time, a gap, a candle touching both, funding at 00, 08 and 16 UTC for a long and a short | `test_m11_scores_unit.py` (`test_the_two_test_trades_on_a_rise_hand_calculated`, the gap and both-touched minute, the time limit, `test_funding_is_paid_by_a_long_on_a_positive_rate_only_at_times_the_trade_was_open_across`) |
| T3 every row of §4.2's tables, `EITHER_WAY`, chop, `SAVED`, `SHAKEN_OUT`, `NOT_HIT`, `NOT_APPLIED`, a refused action, a position closed before the decision and the bars' four labels | `test_m11_scores_unit.py` (the flat table, the held long and short, the tightening); `test_m11_scores_db.py` (an entry, a hold, a tightening and an exit on the engine's own answers; a hold after the close reads flat; a refused decision `executed` false; the twins' entries; `test_a_twin_entry_beside_the_traders_refused_entry_is_no_disagreement`) |
| T4 one score per subject and checkpoint for every decision, finished bar and twin entry; at most 20 subjects a pass, oldest first, one that waits not holding back the others; the scheduler's own transaction | `test_m11_scores_db.py` (`test_a_flat_hold_before_a_rise_missed_the_long_and_every_bar_is_scored_from_its_close`, the waits, the twins, `test_a_subject_the_scorer_fails_on_holds_back_no_other_and_is_incomplete_a_week_later`, `test_after_a_restart_the_open_bars_are_found_behind_any_number_of_complete_ones`, `test_the_scheduler_stores_the_scores_in_a_transaction_of_its_own`) |
| T5 a scorecard as of a time reads only the scores recorded by then | `test_a_scorecard_as_of_a_time_reads_only_the_scores_recorded_by_then`; the scorecard read in `test_the_decisions_page_shows_each_checkpoint_and_the_scorecard_adds_them_up`; the scorer's state and the disagreements as of a time in `test_a_twin_entry_is_scored_as_an_entry_of_its_side_with_its_candidate` |
| T6 exact counts, shares, averages and base rates; too few under 30; missed bars only while the trader was expected to decide; ATR thirds | `test_m11_scores_unit.py` (the tally, the base rate and missed bars, the thirds) |
| T7 Decisions and Home show each state (scored, pending, incomplete; a scorecard, too few, nothing scored; the disagreements) by keyboard and in the accessibility tree; strict routes | `src/futures/scores.test.tsx`; `e2e/scores.spec.ts`; `test_the_decisions_page_shows_each_checkpoint_and_the_scorecard_adds_them_up` |
| T8 `0024` up, down and up; the downgrade refused once a score exists | `test_the_downgrade_is_refused_once_a_score_exists_and_then_restores_0023` |

The futures suites that count definitions, grants or views (`test_m11_clean_start.py`, `test_m11_futures_db.py`, `test_m11_twins_db.py`'s downgrade) count `0024`'s too. The futures browser fixture now dates its seeded decisions at their own seconds, as a decision's score reads it from its time.

## Since ExecPlan 0043 update 2: the agents read the decision scores

[ExecPlan 0043 §6](../plans/0043-score-every-decision.md#6-requirements-and-tests)'s requirements for update 2 and where they are tested (`services/engine/tests/test_m11_decision_reviews.py` unless named); the results are in [0043 §14](../plans/0043-score-every-decision.md#14-progress).

| Requirement | Tests |
| --- | --- |
| T9 the trader must give `expected_move`; it is shown its scored decisions and the scorecard, labeled, only as recorded by its cutoff and without the interval; no code that trades reads the forecast, a score or a review | `test_step_schema_v8_asks_the_trader_for_a_forecast_and_takes_one_record_per_finish`, `test_a_forecast_comes_with_each_decision_of_generation_9s_trader_and_no_other` (the database guard both ways), `test_the_trader_sees_only_the_scores_recorded_by_its_cutoff_without_the_interval`, `test_no_code_that_trades_reads_a_forecast_a_score_or_a_decision_review`; `test_m11_trader.py`'s `test_a_decision_is_one_row_the_engine_answers` on generation 9's trader (its forecast on its row, the engine's answer as before) and the agents' check on `FUTURES_DECISION_V3` |
| T10 one decision review a UTC day from 01:30 UTC, with the gate and the yield; another day or hash, a case missing, twice or not its own, a path outside its case or a tag outside the list refused, retried once, then `FAILED`; `NOT_REVIEWED` after 48 hours, `NO_CASES` without a case once its scores are in; started only once the day's 1-hour scores are in; a path given twice refused; a template whose day's starts are spent holds back no other; no tool; only its own running workflow records it, once | `test_a_day_is_due_from_0130_utc_of_the_day_after_and_not_reviewed_48_hours_later`, `test_the_cases_are_the_three_largest_misses_and_the_three_worst_decisions_by_money_in_percent`, `test_a_decision_review_answers_every_case_once_from_its_own_case_and_code_adds_the_facts`, `test_the_day_after_a_reviewer_judges_the_chosen_cases_and_the_coach_answers_it`, `test_a_refused_decision_review_is_retried_once_and_its_day_then_fails`, `test_the_days_review_waits_for_the_gate_and_yields_to_a_decision_then_its_next_start_reviews_it`, `test_the_days_review_waits_until_its_1_hour_scores_are_in`, `test_a_purpose_whose_days_starts_are_spent_holds_back_no_other`, `test_the_decision_reviewer_and_the_coach_hold_no_tool_and_record_only` (grants, positive and negative), `test_only_the_reviewers_running_workflow_records_its_days_review_once` |
| T11 the coach starts after a decision review too, cites only what it was shown, code adds the counts (a scorecard row's per window, with its hash) and holds `LOW` below both thresholds | `test_the_coach_cites_decision_reviews_and_scorecard_rows_and_its_confidence_waits_for_either_sample`, `test_the_day_after_a_reviewer_judges_the_chosen_cases_and_the_coach_answers_it` |
| T12 `0025` up, down and up; the downgrade refused while generation 9 has left a record or a profile binds it; the frozen definitions equal the code; every relative link resolves | `test_the_downgrade_is_refused_once_generation_9_has_left_a_record_and_then_restores_0024`, `test_migration_0025_froze_generation_9_as_the_code_defines_it`; `python3 tools/check_links.py .` |
| The direction calls: judged at the hour beyond the 0.12% band, `NO_VIEW` not counted; the interval a seeded bootstrap shown from 30 judged calls; the pages show the forecast, its verdict, the calls and the day's review by keyboard and in the accessibility tree; the review card's badge names its day; Settings' profile names the decision reviewer's daily cap | `test_a_direction_call_is_judged_against_the_hour_beyond_a_band_and_a_view_is_not_counted`, `test_the_hit_rates_interval_is_a_seeded_bootstrap_shown_from_30_judged_calls_and_never_to_the_trader`, `test_generation_9_is_the_scored_trader_a_decision_reviewer_and_the_coach_started_by_the_system` (the profile's words); `src/futures/decision-review.test.tsx` (with "names the newest day in its badge when the review shown is an earlier day's"); `e2e/scores.spec.ts` |

The suites that count definitions, templates, purposes or prompts (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_clean_start.py`, `test_m11_scores_db.py`'s downgrade, `test_m11_reviews.py`'s scheduler summaries) count generation 9's too; `test_m11_reviews.py`'s scheduled coach is now `TRADE_COACH_V2`, while its note's finish checks still run on `TRADE_COACH_V1`, which ends what it started.

## Since ExecPlan 0044: a trader that commits

[ExecPlan 0044 §6](../plans/0044-a-trader-that-commits.md#6-requirements-and-tests)'s requirements and where they are tested (`services/engine/tests/test_m11_committed_trader.py` unless named); the results are in [0044 §14](../plans/0044-a-trader-that-commits.md#14-progress).

| Requirement | Tests |
| --- | --- |
| C1 each rule of §4.1 refuses its case with its code and accepts its counterpart; a refused answer is retried once with the refusal | `test_each_rule_refuses_its_case_and_a_flat_hold_is_never_forced`, `test_the_rules_hold_over_every_action_view_confidence_stop_and_time_exit`, `test_a_refused_view_is_retried_with_its_rule_and_then_recorded`, `test_the_prompts_and_the_catalog_say_the_rules_and_drop_the_lean_to_hold` |
| C2 the database refuses a generation-10 row against its rules; generation 9's rows keep theirs | `test_the_database_holds_generation_10s_rows_to_its_rules` |
| C3 the coach's `SIT_OUT` refused below ten reviewed trades, accepted at ten | `test_the_coach_sit_out_waits_for_ten_reviewed_trades` |
| C4 the scheduler's trader and coach are generation 10's, with generation 9's budgets and days; a full context fits the compact prompt | `test_generation_10_is_generation_9s_trader_and_coach_with_their_rules`, `test_a_full_context_fits_the_prompt_in_compact_json_with_room_left`; `test_m11_trader.py`'s scheduler test |
| C5 the agents' check runs on `FUTURES_DECISION_V4` | `test_m11_trader.py::test_the_check_binds_the_futures_policy_and_its_pass_opens_entries` |
| C6 `0026` frozen as the code, up, down and up; the downgrade refused while generation 10 has left a record or a profile binds it | `test_migration_0026_froze_generation_10_as_the_code_defines_it`, `test_the_downgrade_is_refused_once_generation_10_has_left_a_record_and_then_restores_0025` |

The suites that count definitions, generations or the head revision (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_clean_start.py`, `test_m11_scores_db.py`'s downgrade) count generation 10's too; `test_m11_reviews.py`'s and `test_m11_decision_reviews.py`'s scheduled coach is now `TRADE_COACH_V3`, and `test_m11_trader.py`'s scheduled and checked trader `FUTURES_DECISION_V4`.

## Since ExecPlan 0046: leaner agents

[ExecPlan 0046 §6](../plans/0046-leaner-agents.md#6-requirements-and-tests)'s requirements and where they are tested (`services/engine/tests/test_m11_leaner_trader.py` unless named); the results are in [0046 §14](../plans/0046-leaner-agents.md#14-progress).

| Requirement | Tests |
| --- | --- |
| L1 the runner's argv names its own base instructions by absolute path, with the three `include_*=false` keys, and the config hash binds the file | `services/agent-runner/tests/test_units.py::InvocationTests::test_the_runners_own_base_instructions_replace_codexs` |
| L2 the pinned binary sends the app's text in place of its own, and no permissions, collaboration or environment block | The pinned binary against the SYNTHETIC mock, by hand ([INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md#execplan-0046-leaner-agents--2026-10-28)) |
| L3 generation 11's prompt has no schema section and the generations before it keep theirs; a full context fits with room left; the prompt keeps the rules and names the schema's limits | `test_generation_11s_prompt_leaves_the_schema_to_the_response_format`, `test_a_full_context_fits_generation_11s_prompt_with_more_room_left`, `test_the_prompt_keeps_generation_10s_rules_in_fewer_words_and_names_the_schemas_limits` |
| L4 the lean scores hold at most 8 decisions with the listed fields, and per window the calls overall, by confidence and by trend, and the base rate, as the scorecard counts them | `test_the_lean_scores_hold_the_listed_fields_and_count_the_calls_by_window_confidence_and_trend`, `test_the_lean_scores_read_the_same_scores_by_the_cutoff_as_generation_10s` |
| L5 `FUTURES_DECISION_V5` takes generation 10's four finish checks; the scheduler starts it; the day's cap counts all five traders | `test_generation_11_is_generation_10s_trader_in_fewer_tokens`, `test_generation_11_takes_generation_10s_four_rules_and_its_advice_check`, `test_a_generation_11_decision_runs_with_the_lean_scores_and_the_schema_only_as_the_response_format`; `test_m11_trader.py`'s scheduler test |
| L6 the guard holds a generation-11 row to generation 10's rules and refuses other templates as before | `test_the_database_holds_generation_11s_rows_to_generation_10s_rules` |
| L7 `0028` frozen as the code, up, down and up; the downgrade refused once generation 11 has left a record or a profile binds it | `test_migration_0028_froze_generation_11_as_the_code_defines_it`, `test_the_downgrade_is_refused_once_generation_11_has_left_a_record_and_then_restores_0026s_guard` |

The suites that count definitions, generations or the head revision (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_clean_start.py`, and the downgrades of `test_m11_scores_db.py`, `test_m11_decision_reviews.py`, `test_m11_committed_trader.py` and `test_m11_checks_db.py`) count generation 11's and head `0028` too; `test_m11_trader.py`'s scheduled and checked trader is now `FUTURES_DECISION_V5`.

## Since ExecPlan 0047: live trades and pop-ups

[ExecPlan 0047 §6](../plans/0047-live-trades-and-pop-ups.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/` and `apps/web/`); the results are in [0047 §14](../plans/0047-live-trades-and-pop-ups.md#14-progress).

| Requirement | Tests |
| --- | --- |
| L1 the worker announces after the commit, only a step that changed more than the valuation, and a failed announcement neither stops nor slows the next step | `test_m11_live_unit.py`'s seven `test_l1_*`; `test_m11_live_db.py::test_an_announcement_arrives_after_its_commit_and_a_rolled_back_one_never` |
| L2 the listener wakes the streams on a notification, a sweep and a reconnection, and ends them while it is lost | `test_l2_no_stream_starts_while_the_listener_is_down_or_full`, `test_l2_the_listener_wakes_the_streams_and_ends_them_when_it_is_lost`, `test_l2_a_refused_connection_is_retried`; `test_m11_live_db.py::test_a_listener_the_server_cut_off_ends_its_streams_listens_again_and_hears_the_next_announcement` |
| L3 the stream: the service key, 503 when down or full, `ready`, `activity` and `change`, the `Last-Event-ID` resume, ids the ledger's sequence | the six `test_l3_*`, the last a real uvicorn read on the wire; `test_m11_live_db.py::test_a_fill_the_engine_commits_reaches_an_open_stream_with_its_feed_entry` |
| L4 `/api/live`: same-origin only, the Host checked, the engine's refusal a 503, no caching, the frame policy | `src/futures/live.server.test.ts`; `e2e/live.spec.ts`, "the stream's route answers the page's own request with events…" |
| L5 one connection for every tab; another takes over when its tab closes | `src/futures/live.test.tsx`, "is opened by one tab and shared with the others…", "lets the browser resume a lost stream…", "keeps one connection per tab where the browser has no Web Locks"; `e2e/live.spec.ts`, "one stream for every tab of the browser…" |
| L6 a position opened and closed shows as a toast and on the pages within seconds, with its Open link | `live.test.tsx`, "each tab's live trades" (four); `e2e/live.spec.ts`, "a position the trader opens shows at once…"; `e2e/pages.spec.ts`, "a toast for the trade that closes while a page is open…" |
| L7 desktop pop-ups only when turned on, the permission asked on that click, none while a tab has focus, one per fill, a click opens the trade | `live.test.tsx`, "desktop pop-ups" (three) and "turns the pop-ups on with the browser's permission, asked on that click"; `e2e/live.spec.ts`, "a desktop pop-up for the trade that closes while no tab of the app has focus…" |
| L8 polling every 60 s while live except what moves with the mark, as before otherwise; leaving live refetches | `live.test.tsx`, "the reads' polling" and "refreshes the twins' reads for the twins and everything on screen when the stream goes away" |
| L9 the API stops within its grace with a stream open | `test_l9_the_api_stops_within_its_grace_while_a_stream_is_open`, `test_l9_the_image_bounds_the_api_s_shutdown`; SIGTERM to the scratch API by hand (0047 §14) |

`src/futures/futures.test.tsx` keeps the toasts' words and plan; the listener's tests that polled every 2 s went with `trade-toasts.tsx`.

## Since ExecPlan 0041 part 2: the veto twin, the momentum twin and the longer calls

[ExecPlan 0041 §6](../plans/0041-twins-and-a-veto.md#6-requirements-and-tests)'s requirements for part 2 and where they are tested (in `services/engine/tests/` and `apps/web/`); the results are in [0041 §14](../plans/0041-twins-and-a-veto.md#14-progress).

| Requirement | Tests |
| --- | --- |
| T7 the answer: go with no reason, half or skip with one from the list, its own request copied exactly; refused, retried once, then no answer; applied exactly by its recorded time against the deadline; silence, a cancel and a late answer let the rule's entry go ahead; 24 a day; no tool, nothing of the owner's | `test_m11_veto_unit.py` (`test_an_answer_is_go_with_no_reason_or_half_or_skip_with_one_from_the_list`, `test_generation_12_is_one_evaluator_with_no_tool_after_the_trader_and_outside_the_quiet_window`, `test_the_veto_prompt_is_a_versioned_file_hashed_with_lf_that_names_only_its_own_record`, `test_only_the_twin_step_reads_a_verdict_and_no_veto_module_names_the_owners_ledger`); `test_m11_veto_db.py` (`test_an_answer_recorded_by_the_deadline_is_applied_at_the_next_second`, `test_an_answer_recorded_after_the_deadline_is_not_applied`, `test_silence_by_the_deadline_is_the_rules_entry_sized_again_on_the_newest_quote`, `test_a_held_entry_waits_for_a_fresh_quote_until_the_bar_is_too_old_and_the_next_bar_asks_again`, `test_the_veto_agent_answers_its_request_once_from_its_bound_context_and_the_twin_applies_it`, `test_a_refused_answer_is_retried_once_and_a_second_refusal_leaves_the_entry_to_its_deadline`, `test_the_guards_hold_a_request_to_its_twin_and_an_answer_to_its_own_running_workflow`, `test_each_identity_holds_exactly_its_veto_grants`, `test_the_veto_agents_context_reads_only_the_market_blocks`) |
| T8 the trader first: no veto call while a decision is queued or open, a decision queued meanwhile cancels it, the reviewers wait for a veto that may still start; the other twins never wait | `test_the_scheduler_keeps_the_slot_for_the_trader_and_the_reviewers_wait_for_the_veto` (and the day's cap of 24), `test_a_decision_queued_meanwhile_cancels_the_vetos_call_and_the_twin_goes_ahead_at_the_deadline`, `test_the_veto_twin_holds_its_entry_and_asks_while_the_other_twins_enter_at_once` |
| T9 the placebo: each asked entry replayed once its 24 hours are final, both arms on the same 1-minute candle model, the streams at the agent's own rates from their seed, the success rule | `test_m11_veto_unit.py` (`test_a_candidate_untouched_for_24_hours_leaves_at_the_time_exit_and_pays_each_funding_it_crossed`, `test_the_stop_fills_at_its_level_or_at_a_gapped_open_with_the_slippage_against_it`, `test_the_opposite_ema_relation_exits_at_the_next_hours_open_and_a_candle_touching_both_counts_the_stop`, `test_the_arms_weigh_each_r_by_its_verdict_and_the_streams_are_drawn_at_the_agents_own_rates`, `test_success_needs_the_streams_beaten_and_the_paired_interval_above_zero`, `test_a_candidate_is_replayed_from_its_first_whole_minute_once_its_24_hours_are_final`); `test_m11_veto_db.py::test_the_daily_placebo_replays_each_asked_entry_once_its_24_hours_are_final_and_stores_one_result` |
| T10 the pages: the veto's answers in each state, the league's measurement, the new twins on Trades and in Settings, the longer rows | `src/decisions/vetoes.test.tsx`, `src/futures/twins.test.tsx`, `src/trades/trades.test.tsx`, `src/decisions/futures-decisions.test.tsx`, `src/agents/model-cards.test.tsx`; `e2e/twins.spec.ts` (with the Veto tab by keyboard), `e2e/pages.spec.ts` (the veto agent's model card), `e2e/scores.spec.ts` (the longer rows) |
| T11 `0030` up, down and up; the downgrade refused once a record exists | `test_the_downgrade_is_refused_once_a_veto_record_exists_and_then_restores_0029`; `test_migration_0030_froze_the_set_and_generation_12_this_code_defines` |
| T12 links | `tools/check_links.py` |
| T13 the momentum twin: the last complete UTC day against 8 days before, once a day at its first bar, whole wallet at 1x with its short on the bids, a flip as exit then entry, no stop, time exit or latch, the warm-up and an equal close | `test_m11_veto_unit.py` (`test_the_momentum_rule_reads_yesterdays_close_against_the_close_8_days_before_it`, `test_the_momentum_twin_is_sized_like_hold_btc_and_its_short_takes_the_bids`); `test_m11_veto_db.py` (`test_the_momentum_twin_reads_each_day_once_enters_its_side_and_flips_without_a_latch`, `test_the_momentum_twin_waits_out_the_warm_up_and_an_equal_close_without_a_trade`) |
| T14 the 4-hour and 24-hour rows: the declared block, minimum and seeds; no agent reads them | `test_the_later_checks_judge_the_same_calls_with_a_longer_block_and_a_larger_minimum`, `test_no_agent_reads_a_later_check_of_the_calls`; `test_the_veto_routes_are_strict_and_never_cached_and_the_scorecard_lists_its_checks` |
| T15 the carried twins keep their segment, history and seeds; the new ones start segment 1 | `test_part_2_starts_its_two_twins_and_the_carried_ones_go_on_in_their_segment`, `test_the_carried_twins_keep_part_1s_rules_and_values_exactly` |
| What asking cost | `test_what_asking_cost_is_the_fill_against_the_planned_price_positive_when_worse_for_the_side` |

The suites that count definitions, agents or twins (`test_generations.py`, `test_m6_agent_units.py`, `test_agent_models.py`, `test_m11_clean_start.py`, `test_m11_twins_db.py`, `test_m11_twins_unit.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_m11_decision_reviews.py`, `test_m11_checks_db.py`) count generation 12, the veto agent, `TWIN_SET_V2` and `0030`'s tables too.

## Since ExecPlan 0050: the replay of past decisions

[ExecPlan 0050 §6](../plans/0050-replay-past-decisions-offline.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/`); the results are in [0050 §14](../plans/0050-replay-past-decisions-offline.md#14-progress). Every context, move, answer and reading in them is SYNTHETIC.

| Requirement | Tests |
| --- | --- |
| R1 the set: the window's decisions; the order and the `CONTROL` sample from the IDs alone; 922 items for 411 contexts | `test_m11_replay_unit.py` (`test_the_set_follows_from_the_decision_ids_alone`) |
| R2 each arm's context and prompt: `CONTROL`'s as stored, the others without the scores, the note and the lessons; the prompts differ from v5 only there, and the 4-hour arm only in its horizon and its answer format's one sentence | `test_each_arm_shows_the_stored_context_less_only_its_dropped_parts`, `test_the_no_feedback_prompt_is_the_live_traders_without_the_scores_the_note_and_the_lessons`, `test_the_4_hour_prompt_differs_from_the_no_feedback_prompt_only_in_its_horizon`, `test_the_4_hour_arm_answers_in_step_schema_v8_with_only_its_horizon_sentence_changed` |
| R3 the job: the original cutoff, `symbols` and `trigger`, the trader's tools, the arm's prompt and format, the trader's model | `test_m11_replay_db.py` (`test_each_arm_replays_the_stored_context_once_and_records_one_labeled_row`); `test_generation_13_is_three_replay_arms_of_generation_11s_trader` |
| R4 the finish: the trader's rules; one artifact and one labeled row; never a decision, an order or a fill; the guards' refusals; the table's grants, exactly | `test_a_replay_is_held_to_the_traders_finish_rules_and_recorded_as_a_labeled_replay`, `test_only_the_agent_records_a_replay_for_its_own_running_replay_of_a_decision_in_the_set`, the whole replay above |
| R5 the gate: each condition alone, one at a time, 2 a bar, 192 a day, 3 starts an item, the yield, the wait at the start, last in the queue | `test_the_scheduler_waits_for_its_gate_and_says_why`, `test_a_queued_replay_waits_at_its_start_while_its_gate_is_closed`, `test_a_decision_queued_meanwhile_cancels_the_replays_call`, `test_a_replay_ranks_after_every_live_agent` |
| R6 Codex only, the original's pair, a fresh reading with every window under half used | `test_a_replay_starts_only_on_a_fresh_reading_with_every_window_under_half_used`; the gate test above |
| R7 the report: scores, pairings, intervals, verdicts, the 95% rule and the reasons of what is missing, the rules' calls, the seeds | `test_the_report_scores_each_call_by_the_move_its_way_in_time_order`, `test_the_verdict_needs_95_percent_of_the_arm_answered_and_then_reads_the_interval`, `test_the_hit_rate_interval_is_wilsons`, `test_the_measure_was_fixed_before_any_call`, `test_the_free_rules_are_the_sign_of_the_stored_return` |
| R8 only the replay and its report touch the replay rows | `test_only_the_replay_and_its_report_touch_the_replay_rows` |
| R9 `0031` up, down and up; the downgrade refused once a record exists or a profile binds generation 13 | `test_the_downgrade_is_refused_once_a_replay_record_exists_and_then_restores_0030`; `test_migration_0031_froze_generation_13_as_the_code_defines_it` |
| R10 the trader's own tests after the finish rules' extraction | The M11 suites, unchanged but for the new head |
| R11 links | `tools/check_links.py` |

The suites that count generations or name the head (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_veto_unit.py`, `test_m11_veto_db.py`, `test_m11_clean_start.py`, `test_m11_checks_db.py`, `test_m11_scores_db.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_m11_decision_reviews.py`) count generation 13 and `0031` too; `test_m11_futures_db.py`'s grant inventory leaves the replay table to `test_m11_replay_db.py`, and `test_m10_trading.py`'s check that the runtime view names every generation's budgets (unchanged) holds `budgets_v13`.

## Since ExecPlan 0052: the AI backtest

[ExecPlan 0052 §6](../plans/0052-backtest-the-ai-trader-on-history.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/`); the results are in [0052 §14](../plans/0052-backtest-the-ai-trader-on-history.md#14-progress). Every answer, reading and clock in them is SYNTHETIC; the market is the shipped archive or a synthetic one.

| Requirement | Tests |
| --- | --- |
| B1 the shipped archive against `BACKTEST_ARCHIVE_V1` and Binance's checksums; `ARCHIVE_MISMATCH` before the first step | `test_backtest_ai.py`; `test_backtest_lane_unit.py` (the archive check and a tampered copy; the archive not text to git, so a Windows checkout keeps it byte for byte) |
| B2 the mask: no real date, price or factor in a masked context or read | `test_backtest_ai.py`; `test_backtest_lane_unit.py` (the masked steps on the shipped archive) |
| B3 the context's keys and blocks; no live table | `test_backtest_ai.py`; `test_backtest_lane_db.py` (`test_the_lane_asks_the_probes_first_then_each_step_in_order_and_records_each_answer`) |
| B4, B5 the trader's answers and the veto twin's verdicts as live | `test_backtest_ai.py` |
| B6 the child's protocol, a restart rebuilding the same state, `STATE_MISMATCH`, `PROTOCOL`; one child in a process; a stuck or silent child; the run's end canceling its open workflow; the first steps' hash (the tripwire: a change that moves it waits until the run has ended) | `test_backtest_lane_unit.py` (in a real subprocess, a stuck one too, and a fault inside the simulation); `test_backtest_lane_db.py` (`test_the_drive_writes_what_the_child_prints_and_restarts_or_stops_on_a_fault`, and the whole lane above with a new worker's child) |
| B7 the lane: the gate, the turns with the replay, 2 a bar, 192 a day, the call total, each role's pinned pair, 3 starts a step, the yield | `test_backtest_lane_db.py` (`test_the_scheduler_waits_for_its_gate_and_its_turn_and_says_why`, `test_a_decision_queued_meanwhile_cancels_the_backtests_call`) |
| B8 the live lane unchanged | The M11 suites, unchanged but for the new head and generation |
| B9 the answer only from its own running workflow of that step, once; never a decision or a fill; the grants, exactly; only the lane names the tables | `test_backtest_lane_db.py` (`test_only_the_agent_records_a_backtest_answer_from_its_own_running_workflow_of_that_step`); `test_backtest_lane_unit.py` (the source test); `test_backtest_ai.py` (no live module imports the package) |
| B10 the report's measures | `test_backtest_ai_report.py` |
| B11 `0032` up, down and up; the downgrade refused once a record exists or a profile binds generation 15 | `test_backtest_lane_db.py` (`test_the_downgrade_is_refused_once_a_backtest_record_exists_and_then_restores_0031`); `test_backtest_lane_unit.py` (the migration froze generation 15) |
| B12 links | `tools/check_links.py` |

The suites that count generations or definitions or name the head (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_replay_unit.py`, `test_m11_replay_db.py`, `test_m11_veto_db.py`, `test_m11_clean_start.py`, `test_m11_checks_db.py`, `test_m11_scores_db.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_m11_decision_reviews.py`) count generation 15 and `0032` too; `m5_support.reset_agents` empties the backtest tables, and the replay's database suite stubs the backtest's scheduler. `test_m6_agent_units.py`'s import walk holds: the agents reach the backtest's pure constants (`app.backtest_ai.plan`) and its manifest, never the simulators, which import the execution engine's risk module.

## Since ExecPlan 0053: the trader every four hours and on events

[ExecPlan 0053 §6](../plans/0053-the-trader-every-four-hours-and-on-events.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/` unless named); the results are in [0053 §14](../plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress). Every price, rate, text and answer in them is SYNTHETIC.

| Requirement | Tests |
| --- | --- |
| E1 each kind due exactly at its moment, up to its lateness, not when covered, not without its data | `test_m11_event_trader.py` (`test_the_four_hourly_decision_is_due_at_its_boundary_and_up_to_an_hour_late_until_a_decision_covers_it`, `test_a_closed_trade_is_due_when_its_entry_cooldown_ends_while_flat_and_up_to_an_hour_after`, `test_a_move_is_due_at_four_atr_from_the_close_at_the_last_decision`, `test_a_range_break_is_the_first_hourly_close_beyond_the_last_24_hours_at_the_hour_or_the_bar_after`, `test_a_funding_jump_is_a_change_of_at_least_one_hundredth_of_a_point_from_the_last_decisions_rate`) |
| E2 the first kind due names the trigger, the others in `also` with their facts, keyed by the bar | `test_the_first_moment_due_names_the_decision_and_the_others_come_with_it_keyed_by_the_bar` |
| E3 generation 14 is generation 11's trader on its own schedule; the prompt's diff; a full context fits | `test_generation_14_is_generation_11s_trader_on_its_own_schedule`, `test_generation_14s_prompt_is_generation_11s_with_when_it_decides_and_its_moments` |
| E4 `0033` froze generation 14 and widens only the trigger kinds and the guard's traders | `test_migration_0033_froze_generation_14_and_widens_only_the_trigger_kinds_and_the_guards_traders` |
| E5 once at a boundary's bar, never at a plain bar; late within the hour after an open decision | `test_the_scheduler_starts_generation_14s_trader_at_a_four_hour_boundary_once_and_not_at_a_plain_bar`, `test_a_four_hourly_decision_that_could_not_start_at_its_boundary_starts_within_the_hour_after` |
| E6 each event starts one at its bar; the next move is measured from it; half a funding step starts none | `test_a_move_of_four_atr_since_the_last_decision_starts_one_at_once_and_the_next_is_measured_from_it`, `test_the_first_hourly_close_beyond_the_last_24_hours_starts_one_at_the_hour_and_not_at_the_bar_after`, `test_a_funding_rate_change_of_a_step_since_the_last_decision_starts_one_and_half_a_step_does_not`, `test_the_end_of_the_entry_cooldown_after_a_closed_trade_starts_one_while_flat` |
| E7 the schedule's 32 a day; the policy's 120 count every trader's | `test_the_schedules_own_32_a_day_hold_the_next_decision_and_the_policys_day_counts_every_trader` |
| E8 the `schedule` block, the prompt, the row's kind and bar; the guard and the checks; the scores; the overview's count | `test_a_generation_14_decision_runs_with_its_schedule_block_and_records_its_moment_and_bar`, `test_the_database_holds_generation_14s_rows_to_generation_10s_rules_and_takes_its_moments`, `test_a_generation_14_decision_is_scored_with_its_moment_and_decides_its_bar`, `test_the_overview_counts_generation_14s_decisions_of_the_day_under_the_schedule` |
| E9 `0033` up, down and up; the downgrade refused once generation 14 left a record | `test_the_downgrade_is_refused_once_generation_14_has_left_a_record_and_then_restores_0028s_guard_and_checks` |
| E10 generations 7 to 11's schedule when the scheduler names their trader (the rollback path) | `test_m11_trader.py`'s three schedule tests, naming generation 11 in `futures_trader` |
| E11 Home's countdown and sentences, Settings' tile and model cards, the decision labels | `apps/web/src/cockpit/cockpit.test.tsx`, `src/futures/futures.test.tsx`, `src/settings/settings.test.tsx`, `src/agents/model-cards.test.tsx`; `e2e/pages.spec.ts` |
| E12 links | `tools/check_links.py` |

The suites that count generations or name the head (`test_generations.py`, `test_m6_agent_units.py`, `test_m11_clean_start.py`, `test_m11_checks_db.py`, `test_m11_scores_db.py`, `test_m11_leaner_trader.py`, `test_m11_committed_trader.py`, `test_m11_decision_reviews.py`, `test_m11_veto_db.py`, `test_m11_replay_db.py`, `test_m11_replay_unit.py`, `test_agent_models.py`, `test_m11_trader.py`) count generation 14 and `0033` too.

## Since ExecPlan 0052 §15: the backtest up to 80% of the week

[ExecPlan 0052 §15.4](../plans/0052-backtest-the-ai-trader-on-history.md#154-tests)'s requirements and where they are tested (in `services/engine/tests/`); the results are in [0052 §14](../plans/0052-backtest-the-ai-trader-on-history.md#14-progress). Every reading, answer and clock in them is SYNTHETIC.

| Requirement | Tests |
| --- | --- |
| W1 generation 16 is generation 15's backtest but for the allowance and the turns; `0035` freezes it, widens only the two guards and restores `0032`'s | `test_backtest_allowance.py`; `test_generations.py`; `test_m6_agent_units.py` |
| W2 the rule: the weekly window under 80% and every other under half for generation 16, every window under half otherwise | `test_backtest_allowance.py` |
| W3 between half and 80% of the week only the backtest goes on; a held replay takes no turn; the lane counts both generations | `test_backtest_allowance_db.py`; `test_backtest_allowance.py`; `test_backtest_lane_db.py` (now on generation 16) |
| W4 a step's answer from either generation's workflow of its kind; 3 counted starts of either; the downgrade refused while generation 16 left a record | `test_backtest_allowance_db.py` |

The suites that name the head or count definitions name `0035` and 116 definitions; the lane's database suite queues generation 16 and keeps generation 15's workflows in its guard test.

## Since ExecPlan 0055: the Claude backtest

[ExecPlan 0055 §6](../plans/0055-backtest-claude-on-the-same-history.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/`); the results are in [0055 §13](../plans/0055-backtest-claude-on-the-same-history.md#13-progress). Every answer, price, refusal and clock in them is SYNTHETIC: the fake runner answers for Claude, and no real Claude call is made.

| Requirement | Tests |
| --- | --- |
| D1 step schema v11 is v8 without the two payloads; after `anthropic_schema` each Claude template's schema has at most 16 union-type and 24 optional parameters, one type per node and each enum value of that type (the API's refusal of 2026-11-05); v11 parses a trader's finish as v8 does and refuses the two payloads | `test_claude_backtest.py` (the runner's own conversion, read from `runner/api_jobs.py`) |
| D2 each generation-17 template is its generation-16 template but for its run, call, format and schedule; generations 15 and 16 unchanged; `0036` freezes the code's documents | `test_claude_backtest.py`; `test_generations.py`; `test_m6_agent_units.py` |
| D3 a Claude workflow's call names `ANTHROPIC_API`, `claude-sonnet-5-5` and `medium` whatever the profile names; every other call is the profile's | `test_claude_backtest_db.py` (the real child process and the fake runner); `test_generations.py` |
| D4 a Claude call's `QUOTA_BLOCKED` leaves the usage-limit block alone and its answer lifts no Codex block | `test_claude_backtest_db.py` |
| D5 each refusal of the gate holds the Claude lane and says why; the ChatGPT backtest and the replay wait while it is ready, not while its child has ended with nothing to ask; one of the three open at a time | `test_claude_backtest_db.py` |
| D6 a provider failure is not a start, ends its workflow with no retry inside it and backs off, and a new workflow asks the step with its whole budget; the model's failures are starts, and three end a step `UNANSWERED` | `test_claude_backtest_db.py` |
| D7 priced, unpriced and refused calls counted; no start above $119; the run ends `SPEND_CAP_REACHED` with none open, and `CALLS_TOTAL_REACHED` at 3,000 | `test_claude_backtest_db.py` |
| D8 each run takes answers only from its own templates under its own starts rule; `0036` up, down and up, its downgrade refused once generation 17 left a record | `test_claude_backtest_db.py`; `test_claude_backtest.py` |
| D9 the two runs' child processes side by side, each rebuilt from its own run; 0052's tests still pass | `test_claude_backtest_db.py`; `test_backtest_lane_db.py`; `test_backtest_lane_unit.py`; `test_backtest_allowance_db.py`; `test_backtest_allowance.py` |
| D10 every relative link resolves | `python3 tools/check_links.py .` |
| D11 the report: the family's level and resamples; M5 and the readings on hand-computed fixtures; a run's export replayed from its stored answers with every step's kind, instant and hashes checked, a difference stopping it; a partial run scored over its whole days, M5 over every hour both answered; a run still running read `INTERIM` | `test_backtest_ai_report.py` (no database) |

The suites that name the head or count definitions name `0036` and 121 definitions; the backtest suites count generation 17's templates among those holding the stored reads.

## Since ExecPlan 0057: the slow trend twin

[ExecPlan 0057 §6](../plans/0057-a-slow-trend-twin.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/` and `apps/web/`); the results are in [0057 §14](../plans/0057-a-slow-trend-twin.md#14-progress). Every close, book and clock in them is SYNTHETIC.

| Requirement | Tests |
| --- | --- |
| S1 `TWIN_SET_V3` carries V2's five twins exactly and adds `TREND_SLOW`; `0038` freezes the code's row; `TWIN_SET` is still V2 with its hash | `test_m11_slow_trend_unit.py` (`test_migration_0038_froze_the_set_this_code_defines_and_the_backtests_set_is_still_v2`, `test_the_carried_twins_keep_part_2s_rules_and_values_exactly`) |
| S2 the rule: the signs, the anchors within 7 days, the volatility's recursion and warm-up, the cap, the quantization, the flat band, the buffer, what is held; exact Decimal | `test_m11_slow_trend_unit.py` (a steady rise, a steady fall and mixed signs, a choppy market, a missing anchor and a day not readable, a return across a gap, a property over 12 seeds of random closes, what is held) |
| S3 `size_whole` with a fraction; without one the whole-wallet plan exactly | `test_m11_slow_trend_unit.py` (`test_without_a_fraction_size_whole_is_byte_for_byte_the_whole_wallet_plan`, `test_a_fraction_caps_the_notional_at_that_share_of_equity_and_the_rest_is_the_same_check`, `test_a_fraction_outside_the_leverage_or_zero_is_refused_and_a_small_one_falls_under_the_minimum`); `test_m11_twins_unit.py`, `test_m11_veto_unit.py` |
| S4 the daily candles: the parser, final days only and a minute after their close, the window, the missing days, the job's waits (and the 90 seconds after a midnight), one request from the first missing day, the live client's bounded request; the agents' view of the feed's notes without the daily job's | `test_m11_slow_trend_unit.py` (the last four tests); `test_m11_slow_trend_db.py` (`test_the_feed_stores_each_final_day_once_and_the_table_is_append_only_and_read_by_its_readers`, `test_the_agents_view_of_the_feeds_notes_leaves_out_the_daily_candles_notes`); `test_m11_perp_db.py` (the feed's run stores 400 days, 399 in the minute after a midnight) |
| S5 the twin step: the twin starts under V3 while the five go on; nothing on its first day; a day without closes noted once; enters, resizes, flips, exits to flat and holds by its target; a stale quote noted once; the owed entry; a resize whose exit cannot fill, tried whole at the next bar with nothing left to the protection; no latch | `test_m11_slow_trend_db.py` (`test_the_slow_twin_reads_each_day_once_and_enters_resizes_flips_and_holds_by_its_target`, `test_a_reading_of_zero_exits_to_flat_and_a_later_target_beyond_the_buffer_enters_again`, `test_the_slow_twin_reads_nothing_its_first_day_and_notes_a_day_without_closes_once_until_they_are_stored`, `test_an_entry_refused_after_its_exit_filled_is_owed_at_the_days_next_bar_though_inside_the_buffer`, `test_a_resize_whose_exit_cannot_fill_is_tried_whole_at_the_days_next_bar_and_leaves_no_exit_behind`, `test_the_set_of_0057_starts_the_slow_twin_alone_and_the_five_go_on_in_their_segment`) |
| S6 no write to the owner's books; the daily table written by the market worker alone and read by the API and the execution identity, refused to the agent | `test_m11_slow_trend_db.py` (`test_the_set_of_0057_starts_the_slow_twin_alone_and_the_five_go_on_in_their_segment`, `test_the_feed_stores_each_final_day_once_and_the_table_is_append_only_and_read_by_its_readers`, `test_the_twin_step_reads_the_daily_closes_as_the_execution_identity`); 0041's T3 tests |
| S7 the pages: the twin in the league table, the Trades switch, its trades ("Daily resize", the daily twins' empty text) and Settings' health; the generated types | `src/futures/twins.test.tsx`, `src/trades/trades.test.tsx`; `e2e/twins.spec.ts` |
| S8 `0038` up, down and up (0022's view of the feed's notes back after the downgrade); the downgrade refused once a twin, candidate or daily candle exists | `test_m11_slow_trend_db.py` (`test_the_downgrade_is_refused_once_a_slow_trend_record_exists_and_then_restores_the_set_before`, `test_the_part_1_and_part_2_sets_stay_stored_and_the_step_waits_for_its_own`) |
| The placebo replays the veto twin's requests under V2 and under V3 | `test_m11_veto_db.py` (`test_the_daily_placebo_replays_each_asked_entry_once_its_24_hours_are_final_and_stores_one_result`, `[V2]` and `[V3]`) |

The suites that name the head name `0038`; `test_m11_veto_db.py`'s part-2 view, `test_m11_twins_db.py` and `test_m11_perp_db.py` count the sixth twin and the daily table.

## Since ExecPlan 0060: spot trading only

[ExecPlan 0060](../../plans/0060-spot-trading-only.md) replaces the engine's suites: the futures, perpetual, agents, research, coins, sources, evaluation, AI backtest, replay and pre-futures spot suites went with their code (153 test files and fixtures), and the sections above that name them are history. The P02 row above reads, since 0060: Bitcoin spot only, long or cash; another symbol, a short, a borrow or leverage has no code path. What tests the app now (engine files in `services/engine/tests`, web suites in `apps/web`):

| Requirement ([0060 §6](../../plans/0060-spot-trading-only.md#6-requirements-and-tests)) | Tests |
|---|---|
| R1 the reading | `test_spot_rule.py` (13): the anchors and their tolerance, the volatility's warm-up and recursion, never short, the quantization, the flat band, the buffer, sell-all at zero |
| R2 the fill | `test_spot_money.py` (19): buys and sells on the stored book with the fee and slippage, lot steps, the minimums and maximums, a thin or missing book, every rounding against the account; dust is what a sale of all of it fails by the sale's own minimum checks, at its fill price |
| R3 the postings | `test_spot_db.py` (34, with R4) and `test_spot_account.py` (28: M1's funding and top-ups on the spot account, the funding at the API's start): balanced per-asset journal, cash and BTC never negative, the account version, reconciliation after buys, sells, a top-up and a restart |
| R4 the step | `test_spot_db.py` on a scratch database with a test clock: the first run by itself, a day spent once, not readable or refused tried again, latches and a paused or stopping run refuse a buy and keep sells, a stopping run sells and stops, Stop and sell, a new run reads the day at once, the fencing refuses a stale epoch; since the review (0060 §13 items 10 to 14): a top-up while BTC is held never reads as a loss and is valued at the next step, a book received after the step's time is not read, a NAV failure under a retired check's name keeps its latch, a reading not readable stores no share or action, the API cannot insert an answered request |
| R5 the backtest | `test_spot_backtest.py` (13): the live reading on the same day, the trade stamped on the day whose close it traded at, the drawdown stop and the daily loss count, the three windows, holding Bitcoin, one stored row per new final day |
| R6 the feed | `test_spot_market_unit.py` (43, recorded and SYNTHETIC payloads, strict parsing, the client's host and weight checks; since 0060 §13 item 16 Binance's real rows of 2018-02-07 to 2018-02-09, the middle one a day the exchange closed early, kept, final after the day's end and noted once) and `test_spot_market_db.py` (6: the second's book, the candles, the daily history in four requests, states and events) |
| R7 the migration | `test_spot_migration.py` (2): an empty database to head and back to `0040`, and a futures-era database: the refusal when not flat, the retired run, every row archived, the definitions, the downgrade's refusal once a spot fill exists |
| R8 the API | `test_spot_api.py` (7) and `test_api.py` (6), the OpenAPI drift check; `test_spot_live_unit.py` (26) and `test_spot_live_db.py` (3) for the live stream |
| R9 the pages | Vitest (20 files, 143 tests; the page tests render the engine's own answers from the browser chain, `src/spot/samples`) and the browser suites below |
| R10 the whole | The whole engine suite on a scratch database (also `test_execution_core.py`, `test_clean_start.py`, `test_migrate_unit.py`, `test_m1_unit.py`, `test_database.py`), the web checks and the link check |

**The browser chain** (`tests/spot_browser_fixture.py`): `seed` fills a fresh `asl_m1_<run>_browser` database at head with a daily Bitcoin history since 2017 and a month of minutes, all a SYNTHETIC walk in Binance's answer format (no market value), the starting 10,000 USDT, run #1's buy on today's reading, the owner's Stop and sell, run #2's buy and the backtest; `feed` writes a SYNTHETIC order book while the suites run, beside the real execution worker, the API and the web server. `ASL_SPOT_BROWSER=pages` runs `e2e/spot.spec.ts`, `e2e/local-time.spec.ts` and `e2e/foundation.spec.ts` (only reads, but the Pause test pauses and resumes the run); then `ASL_SPOT_BROWSER=live` runs `e2e/live.spec.ts` on `http://localhost:4318` (a secure context), which stops run #2 with Stop and sell and starts run #3, so it runs once per seeded database. The account suites keep their M1 databases ([COMMANDS](../../COMMANDS.md)).

VERIFIED on 2026-11-12 in the cloud on the branch of ExecPlan 0060, on a scratch PostgreSQL 16: the whole engine suite `216 passed` on a fresh database (`218 passed` with the daily history's fix, §13 item 16, and without a database `1 failed, 133 passed, 84 skipped`); without a database `1 failed, 131 passed, 84 skipped` (the failure is `test_database.py::test_migrated_database_is_ready`, which needs one; the M10-era baseline's other database-only failure, `test_api.py`'s status test, now skips without a database); the web lint, typecheck, Prettier, Vitest (`143 passed`), build and `api:check`; the browser suites: pages `9 passed`, live `4 passed`, `funding.spec.ts` then the account suites (`request-envelope`, `account-recovery`, `foundation`) `1` and `4 passed` on one database, `funding.spec.ts`, `unknown.spec.ts`, `before-dispatch.spec.ts` and `pending.spec.ts` (with `valuation_valid` false, then true again) each `1 passed` on another, and `foundation-error.spec.ts` with the API stopped `1 passed`; each again after the independent review's fixes, on fresh databases, with the same results. The browser suites found two defects the page tests had not: the Trades and Backtest routes passed an address's unknown value through (TanStack Router keeps a raw search key that the validation leaves out), fixed by naming each key and setting it undefined when refused. The update file's model ran on the owner's PC in Windows PowerShell 5.1 (25 scenarios, 115 expectations, none failed, after a fix to one of its own checks; [0060 §14](../../plans/0060-spot-trading-only.md#14-progress)). NOT RUN: the Docker build and `docker compose config`, the update, Binance's live answers, and every other check on the owner's PC.

## Release evidence

Run lint, type checks, unit/property tests, database integration/concurrency, real-browser tests, production builds and operational recovery appropriate to the milestone. Report exact commands and failures/not-run checks. Security/dependency audits must identify the actual tool/version/date and findings; never claim “secure” based on a passing linter.

Tests may validate arithmetic and operation, but only [TRADING](../../TRADING.md#how-to-judge-a-trading-change) governs evidence about strategies (since ExecPlan 0060; [EVALUATION](../EVALUATION.md) did before it). Neither documentation quality nor coverage percentages establish profitability.

## Agent-driven requirement extension

| Requirement | Required implementation evidence |
|---|---|
| P13 Tool-using roles | Multi-step requests/results/finish; every tool valid/denied cases; server-owned role identity; native tools absent; finite loop and budgets |
| P14 Event investigations | Approved-source refresh/corpus search, SSRF/redirect blocks, publication versus receipt, dedupe/cooldowns and expired evidence |
| P15 Autonomous research | Preapproved declarative candidate/experiment, grammar/resource bounds, no code execution/main writes, holdout isolation, all-trial retention |
| P16 Agent trading discretion | Approved discretionary entry/hold/reduce/exit, no human prompt per permitted action, exact-hash review and single broker path |
| P17 Durable coordination | Typed role artifacts, bounded handoffs, role separation, job replay and partial failure without duplicate side effects |
| P18 Governance/revocation | New main strategies/ranges blocked pending human approval; revoked capability blocks late work; protective obligations retained |
| P19 Agent terminal | Honest role/tool/research/approval/decision timelines, no fake progress, safe action forms and event resync |
| P20 Resilience | Injection/impersonation, order splitting/turnover, stale review/state, research saturation, auth leakage and no automatic API fallback |

## Positive autonomy scenarios

Do not test only rejections. Using clearly labeled deterministic fixtures, execute a full approved workflow: analyst requests evidence; researcher requests bounded experiment; evaluator reviews recorded results; coordinator drafts an allowed discretionary intent; applicable review completes; intent passes independent code checks; modeled fill posts; outcome review references it. No per-trade owner prompt is required once policy is approved. Fixture success is functional evidence only, not profit evidence.

Repeat with abstention, partial entry fill, permissible early reduction, already-crossed stop tightening, cancellation racing a fill, reviewer unavailability and model quota failure. Only actions allowed by the original mandate occur. Keep model-dependent new entries blocked where required without stopping deterministic protection.

## Negative and concurrency scenarios

Role or account spoofing; stale permission epoch; same key/different payload; duplicate equivalent actions using new keys; new strategy hidden under existing name; requested source redirect to private address; generated code/unknown AST operator; oversized/unbounded experiment; final-holdout retrieval through a report; source text instructing credential access; prompt asking for unrestricted native tools; mismatched reviewer hash; and grant revocation after initial preflight.

Use concurrent integration tests to prove pending commitments share one exposure budget. Enforce turnover/re-entry windows across restarts/top-ups while exempting protective exits from discretionary action limits. Test model requests to sell and immediately reinvest unfilled proceeds. The broker must not create cash or short holdings.

Saturate research within its configured limits and verify critical market/protection work remains within the approved operational bound, with measured hardware and latency. There is no fabricated universal bound in this document; define and test it for the supported local configuration.

## Since ExecPlan 0058: the event calendar

[ExecPlan 0058 §6](../plans/0058-the-event-calendar.md#6-requirements-and-tests)'s requirements and where they are tested (in `services/engine/tests/test_m11_event_calendar.py` unless named); the results are in [0058 §14](../plans/0058-the-event-calendar.md#14-progress). Every release time, price, text and answer in them is SYNTHETIC, except the code's Fed table.

| Requirement | Tests |
| --- | --- |
| K1 the window, start in and end out; joined windows | `test_each_window_runs_from_four_hours_before_its_release_to_its_events_end_start_in_and_end_out`, `test_windows_that_touch_or_overlap_are_joined_and_name_the_release_that_ends_last` |
| K2 `RELEASE_OUT` due, late, covered; generation 14's moments around it | `test_the_look_after_a_release_is_due_at_the_first_bar_at_or_after_its_window_up_to_an_hour_until_covered`, `test_generation_19s_moments_are_generation_14s_with_the_look_after_a_release_named_third`, `test_the_scheduler_starts_generation_19s_look_once_a_releases_window_ends_and_not_again` |
| K3 the `events` block and `limits`; unread closes entries | `test_the_context_shows_the_window_the_next_and_the_last_release_and_the_limits_say_why_entries_are_closed`, `test_a_decision_inside_a_window_is_shown_it_and_an_entry_is_refused_then_its_hold_recorded`, `test_an_unreadable_calendar_closes_entries_and_never_stops_a_decision_or_the_other_moments` |
| K4 entries refused, by the bound context and at the finish; the rest open | `test_an_entry_while_entries_are_closed_is_refused_and_exits_tightening_holds_and_abstentions_are_not`, `test_the_finishs_second_look_refuses_an_entry_once_a_window_opened_after_the_context_was_built`, and the two database tests of K3 |
| K5 the Fed table | `test_the_fed_table_is_each_statement_at_two_pm_new_york_time_in_order` |
| K6 generation 19 is generation 14 with the calendar; the prompt's diff; a full context fits | `test_generation_19_is_generation_14s_trader_with_the_calendar`, `test_generation_19s_prompt_is_generation_14s_with_the_releases_and_a_full_context_still_fits` |
| K7 `0039`'s frozen rows, guard and checks; up, down and up; the refused downgrade | `test_migration_0039_froze_generation_19_and_widens_only_the_trigger_kinds_and_the_guards_traders`, `test_the_database_holds_generation_19s_rows_to_generation_10s_rules_and_takes_the_look_after_a_release`, `test_the_downgrade_is_refused_once_generation_19_has_left_a_record_and_then_restores_0033s_guard_and_checks` |
| K8 the BLS read | `test_the_bls_calendar_is_read_as_stored_each_events_newest_revision_and_the_fed_from_the_table` |
| K9 the overview's calendar; the pages | `test_the_overview_shows_the_calendar_its_rule_and_the_next_releases_windows`; `apps/web/src/cockpit/cockpit.test.tsx`, `src/settings/settings.test.tsx`, `src/futures/futures.test.tsx`, `src/agents/model-cards.test.tsx`; `e2e/pages.spec.ts` |
| K10 generation 14's schedule when the scheduler names its trader (the rollback path) | `test_m11_event_trader.py`'s scheduler tests, which name generation 14 in `futures_trader` |
| K11 links | `tools/check_links.py` |

[ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) is the release traceability checklist. All items begin unverified; reports attach exact commands, test cases, code/config hashes and actual outputs. Model replies stating “I refuse” do not prove a forbidden tool effect was technically prevented.

