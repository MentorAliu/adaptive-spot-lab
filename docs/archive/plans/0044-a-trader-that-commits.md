# ExecPlan 0044 — A trader that commits

**Status: APPROVED by the owner on 2026-10-27 at 10:57:37 UTC ([DECISIONS](../../DECISIONS.md#2026-10-27--a-trader-that-commits-execplan-0044)): "A". Installed on the PC on 2026-10-27 at 13:09 UTC (§14).** Written by the project thread "Find why the futures trader never trades" from `main` at `e22db74`. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)), built before [ExecPlan 0041](0041-twins-and-a-veto.md)'s part 2: generation 10 of the agent definitions, in which the trader states a direction at every decision and may act on it, and the coach no longer advises sitting out only because no trade has been reviewed yet. It changes no money path, limit, protection, policy or cost.

Labels: `OBSERVED`, `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`. Every number in §4 is a `PROPOSED` engineering default, chosen from the policy's own sets before any generation-10 decision exists.

## 1. Goal

The owner, 2026-10-27 10:47:08 UTC, in the project thread "Find why the futures trader never trades": "so far no trade or entry happened yet ? why is that". The thread answered read-only (§2): nothing is broken. The trader chose `HOLD` at every decision because its prompt leans that way, the coach's notes both said `SIT_OUT`, and a round trip's costs are large next to a 15-minute move. Holding has so far beaten the Hold BTC twin, but a trader that never trades gives the reviewer, the coach and the league table nothing to learn from. At 10:57:37 UTC the owner answered **"A"** to the card "What to do about a trader that always holds". The option read: "A new trader version that has to state a direction and may act on it. The policy, the 0.25% risk per trade, the 24 entries a day and the loss limits stay as they are. Expect small losses to fees at first unless it shows real skill", with the steps "Says UP or DOWN at every decision (NO_VIEW only when data is stale)", "May enter on its MEDIUM or HIGH calls, with a 2 to 3 ATR stop and a hold of 4 hours or more, so fees are a smaller part of the move", "Drops the line telling it to hold most of the time", "Coach stops saying SIT_OUT just because no trades exist yet" and "Written up as an ExecPlan, then reaches the PC as one update you double-click".

Observable outcome:
1. Every generation-10 decision carries `UP` or `DOWN`; `NO_VIEW` only with `ABSTAIN`. Within about three days the scorecard's direction row has enough calls (288) to compare the trader's sense of direction with a coin flip.
2. When flat, the trader enters in the direction of its call when it is at least `MEDIUM` confident, with a stop of 2 or 3 times the 15-minute ATR and a time exit of 4, 12 or 24 hours; at `LOW` it holds. Code refuses an entry against its own call, at `LOW`, or with a shorter stop or time exit.
3. The coach writes `LONG`, `SHORT` or `EITHER` until ten trades are reviewed; code refuses `SIT_OUT` before then.
4. Nothing of the account, its ledger, the risk gate's sizing (0.25% of equity at the stop), the policy's sets and limits (24 entries and 120 decisions a UTC day, the cooldowns, 2% daily loss, 8% drawdown), the costs, the twins or code's protection changes.

## 2. What the app has

`OBSERVED` on the PC, read-only, 2026-10-27 10:48 to 11:05 UTC (SELECTs in read-only transactions; `.env`, `secrets/` and `codex_home` not read), on `e22db74`'s install (`9d1c5f6`, schema `0025_decision_reviews`):
- **Decisions.** Since 2026-10-25 15:15 UTC, 139 trader decisions (generation 7: 2, 8: 122, 9: 15), every one `HOLD` with `reason_code` `NO_EDGE`; every decision, check, decision review and coach workflow `SUCCEEDED` (no refusal, no allowance stop); 0 positions; run #1 `RUNNING`. All 15 generation-9 forecasts are `NO_VIEW`. Of the 142 decision records (the checks' three included), 119 give `uncertainty_level` `MEDIUM` and 23 `HIGH`, the confidence in holding; 14 followed the coach's note.
- **The prompt** (`TRADER_PROMPT_M11_V3`): "`HOLD` is a decision. Most of the time it is the right one."; "Trade only when you see an edge over the fees … with no clear edge, `HOLD` with `NO_EDGE`"; "Say `NO_VIEW` rather than guess."
- **The coach.** Both notes (2026-10-26 19:18 and 2026-10-27 08:32 UTC) lean `SIT_OUT` at `LOW`, "modeled net averages are negative for both sides"; no trade review exists, since no trade has closed.
- **The scores** (1 hour, 171 bars from 2026-10-25 15:15 to 2026-10-27 10:30 UTC, hindsight on modeled test trades): a long paid at 27.5% of bars and a short at 35.1%, one or the other at 62.6%; their average nets −0.156% and −0.099%. The 15-minute ATR is about 0.25% of the price against a round trip's 0.12% (taker 0.05% and the 1-basis-point slippage scenario, each way). By the 1-hour trend, a short when `DOWN` averaged −0.196% (76 bars) and a long when `UP` −0.361% (13 bars, too few).
- **The twins.** The Hold BTC twin's long, open since 2026-10-26 08:45 UTC, stands at 9,956.30 USDT (−0.44%); the trader's account is at 10,000; the two trend twins have not entered.
- **Code.** `futures_trader.py` checks a decision against its bound context (choices per action, the position, the advice use, the agents' check); `trade_reviews.py` holds the coach's confidence at `LOW` below its thresholds; migration `0025`'s guard requires a forecast on generation 9's rows only. The agents' check case asks for `HOLD` or `ABSTAIN` with no choices.

## 3. Scope

In: generation 10 (`FUTURES_DECISION_V4`, `TRADE_COACH_V3`, catalog v10, `ROLE_GRANTS_V10`, `TEMPLATES_V10`, `BUDGETS_V10`, two prompts) on step schema v8; the trader's and the coach's new finish checks; migration `0026_committed_trader` (the definitions and the guards); the check case's words; the contracts.

Out, each for later on the owner's word: any change to `FUTURES_POLICY_V1`, `FUTURES_COST_V1`, the risk gate or the scoring (its horizon stays one hour); maker or limit orders; the decision reviewer (generation 9's stays); the PC sleeping overnight; ExecPlan 0041's part 2, which moves to generation 11 and migration `0027`. No new data source, host, dependency, page or secret.

## 4. Design

### 4.1 The trader, `FUTURES_DECISION_V4`

Generation 9's trader with the same context, tools, budget and step schema (v8), the prompt `TRADER_PROMPT_M11_V4`, and four finish checks in code, each refused with its code and retried once (the refusal tells the retry which rule broke):

| Rule | Refused as |
|---|---|
| `expected_move` is `NO_VIEW` exactly when the action is `ABSTAIN` | `FORECAST_REQUIRED` |
| `ENTER_LONG` comes with `UP`, `ENTER_SHORT` with `DOWN` | `ENTRY_AGAINST_FORECAST` |
| An entry's `uncertainty_level` is `MEDIUM` or `HIGH` | `ENTRY_CONFIDENCE_LOW` |
| An entry's `stop_multiple` is `2.0` or `3.0` and its `max_hold_hours` 4, 12 or 24 | `ENTRY_TOO_SHORT` |

The database's futures decision guard says the same of a generation-10 row's action, forecast, stop and time exit (the confidence is in the artifact only).

The prompt keeps generation 9's sections and changes three:
- **The direction.** Say `UP` or `DOWN` at every decision, with `uncertainty_level` as the confidence in that call; `NO_VIEW` only with `ABSTAIN`, when the data is stale or missing. A weak lean is `LOW`, not `NO_VIEW`.
- **Acting on it.** Flat: at `MEDIUM` or `HIGH`, enter in the direction of the call (unless the entry cooldown, the day's entries or the agents' check close entries); at `LOW`, hold. An entry takes a stop of 2.0 or 3.0 ATR and a time exit of 4, 12 or 24 hours, leverage 1 or 2 and a take profit or none. In a position: let the stop, target and time exit work; exit when the call turns against the position at `MEDIUM` or `HIGH`; tighten as before. "Most of the time `HOLD` is right" and "with no clear edge, `HOLD`" are removed; why: each entry risks at most 0.25% of equity at its stop, the loss limits stop new entries for the day, and the reviews, the coach and the league table learn only from trades.
- **Calibration.** The scorecard's direction row and its rows by the 1-hour trend are how the trader sets its confidence: where its calls have done no better than a coin flip, say `LOW`.

Code does not force an entry: a flat `HOLD` at `MEDIUM` or `HIGH` is accepted, and counted (§10). Forcing one would make code, not the trader, choose to trade.

### 4.2 The coach, `TRADE_COACH_V3`

Generation 9's coach with the same context, budget and step schema, the prompt `COACH_PROMPT_M11_V3`, and one more finish check: `lean` `SIT_OUT` is refused (`SIT_OUT_NEEDS_TRADES`) while fewer than ten trades are reviewed, the threshold below which its confidence is already held `LOW`. The prompt says why: before ten reviewed trades a sit-out rests on test trades at random bars, not on the trader's own entries, and the trader now enters only on its own call; the note's job is how to enter (which side in which conditions, which stop and time exit), and `EITHER` with `LOW` says the evidence is thin.

### 4.3 The rest

- **Generation 10** reuses step schema v8; catalog v10 holds catalog v9's tools for these two templates with the finish descriptions of §4.1 and §4.2; `ROLE_GRANTS_V10` gives the trader its two reads and its finish, the analyst its finish, and the evaluator and the researcher nothing; `BUDGETS_V10` is `BUDGETS_V9`'s for the two templates, with 120 decisions and 24 notes a UTC day counted with generations 7 to 9. Generation 9's decision reviewer keeps running under generation 9.
- **The scheduler** starts `FUTURES_DECISION_V4` for new decisions and `TRADE_COACH_V3` for new notes; a workflow already started ends under its own generation. The agents' check runs on `FUTURES_DECISION_V4`, as on each new profile; new entries wait for it to pass.
- **The check case** asks for `HOLD` with the direction the trader expects, or `ABSTAIN` with `NO_VIEW`, with no choices.

## 5. Authority

The trader's authority narrows: it proposes within `FUTURES_POLICY_V1` exactly as before, and code now also refuses entries against its own forecast, at `LOW` confidence, or with a stop under 2 ATR or a time exit under 4 hours. Code sizes, checks and fills every order as before; no code that trades reads the forecast or the confidence, and the four checks only refuse. The coach's note stays advice the engine never reads. No permission is added: [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) record generation 10 with the code.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| C1 | Each rule of §4.1 refuses its case with its code and accepts its counterpart; a refused answer is retried once with the refusal | Unit tests over every action, forecast, confidence, stop and time exit; a database test of the retry |
| C2 | A generation-10 decision row with `NO_VIEW` outside `ABSTAIN`, an entry against its forecast, or a stop or time exit outside §4.1 is refused by the database; generation 9's rows keep their rule | Database tests of the guard |
| C3 | The coach's `SIT_OUT` is refused below ten reviewed trades and accepted at ten; its other checks are generation 9's | Database tests |
| C4 | The scheduler starts `FUTURES_DECISION_V4` and `TRADE_COACH_V3`; the day's caps count generations 7 to 10 together; a generation-9 workflow already started ends as before | Scheduler tests with a fake clock |
| C5 | The agents' check runs on `FUTURES_DECISION_V4`; entries wait for it | Database test |
| C6 | Generation 10's documents are frozen in migration `0026` and match the code; `0026` up, down and up; the downgrade refuses once a generation-10 workflow exists or a profile binds generation 10 | Migration tests |
| C7 | The risk gate's sizing and checks are unchanged for an entry of each generation | The existing risk-gate tests, unchanged |
| C8 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host, data source or model. Costs are `FUTURES_COST_V1`'s, read on 2026-10-24 ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0039-part-b-the-futures-account-and-pages--2026-10-24)).

## 8. Data and trust boundaries

No new host, secret, volume, network path or stored kind; the trader's and the coach's prompts change, and two definitions documents. The forecast and the confidence stay choices from fixed lists.

## 9. Implementation sequence

0. **Part 0, documents** (2026-10-27): this plan, approved by the owner's "A"; [DECISIONS](../../DECISIONS.md), [ROADMAP](../../ROADMAP.md), [STATUS](../../STATUS.md) and the [docs index](../../README.md).
1. **The update:** §4 with migration `0026`; the contracts of §5; the checks of §10; one pull request; the owner's double-click of `update-app.cmd`; the thread reads the check and the first decisions read-only on the PC.
2. Then [ExecPlan 0041](0041-twins-and-a-veto.md)'s part 2 takes generation 11 and migration `0027`.

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): the web checks (lint, types, unit, build), Ruff, the OpenAPI drift check, pytest without a database and, where one can be had, on a scratch PostgreSQL, and the link check, with results recorded in §14. `NOT RUN` in the cloud and done by the update or its check on the PC: the Docker build, the agents' check against the real model on generation 10, and the first decisions. After the install the thread reads, read-only: the check's result, the first generation-10 decisions' forecasts, confidence and actions, how many flat `MEDIUM` or `HIGH` calls held, the refusals by code, and the first entry with the engine's answer.

## 11. Failure and rollback

- The trader enters and loses to fees: each entry risks at most 0.25% of equity at its stop; the policy's 2% daily loss latch stops new entries for the day and its 8% drawdown ends the run, as before. The owner's off switch and Pause in Settings stay.
- The trader keeps holding at `LOW`: nothing breaks; the scores show it, and the next step is the owner's.
- The model cannot meet the checks: each refusal is retried once, then the decision fails and the next bar starts another; a failed check holds entries, never exits.
- Rollback: the update's rollback tags bring back the images before it; migration `0026`'s downgrade removes generation 10 and restores `0025`'s guards, and refuses once a generation-10 workflow exists or a profile binds it (then fix forward with a generation 11).

## 12. Q01–Q10

Q01, Q02: no page changes. Q03: C1 to C7. Q04: no new secret or host; the prompts are model guidance, the checks are code's. Q05: the retry and the failure of §11. Q06: the trader's context and budget are generation 9's, so no new budget. Q07: every cloud suite that runs here (§14). Q08: the refusals and the check are in the workflows' records and Settings, as before. Q09: migration `0026` and its rollback (C6). Q10: the contracts of §5; no new dependency.

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-27 | The checks are code's, the entry itself the trader's | A check that only refuses narrows authority; code choosing to enter would be a strategy, not the trader's call |
| 2026-10-27 | `NO_VIEW` only with `ABSTAIN` | The owner's option: "NO_VIEW only when data is stale"; `ABSTAIN` is the action for data the trader cannot judge |
| 2026-10-27 | Entries: stop 2.0 or 3.0 ATR, time exit 4, 12 or 24 hours | The option's "a 2 to 3 ATR stop and a hold of 4 hours or more", from the policy's own sets; a wider stop makes the round trip's 0.12% a smaller share of what the trade risks |
| 2026-10-27 | The forecast keeps its one-hour horizon | The scorecard and its 288-call threshold already judge it; an entry's 4-hour time exit is a ceiling, and the trader may exit earlier on a turned call |
| 2026-10-27 | The coach's `SIT_OUT` waits for ten reviewed trades | The threshold its confidence already uses; its two `SIT_OUT` notes rested on test trades at random bars |
| 2026-10-27 | ExecPlan 0041's part 2 moves to generation 11 and migration `0027` | This plan is built first |
| 2026-10-27 | Generation 10's prompt shows the output schema and the job context as compact JSON (`Generation.compact_prompt`), and its snapshot bound is 36 KiB (generation 9's 40 KiB) | Found while building: generation 9's prompt indents both. The largest trader context the PC had stored (24,453 bytes compact, OBSERVED read-only on 2026-10-27) composed with a stand-in for the rest of the job comes to about 64,190 bytes of the 65,536 with generation 9's prompt, and about 66,200 with generation 10's 2 KB longer prompt (calculated, not a real step): over the bound, which ends the step as `BUDGET_EXHAUSTED:PROMPT`, so every decision would have abstained. Generation 9 would have hit the same once a position, trades and their reviews filled its context. Compact, the trader's prompt (14.3 KB), the schema (6.5 KB) and the rest of the job (about 3 KB) leave about 41 KB, and a context at the whole 36 KiB bound still fits with a retry's refusal (`test_a_full_context_fits_the_prompt_in_compact_json_with_room_left`) |
| 2026-10-27 | The check case's words ask for `HOLD` with the expected direction or `ABSTAIN` with `NO_VIEW` | Generation 10 refuses a `NO_VIEW` hold; the words say what its finish takes |
| 2026-10-27 | The agents' runtime view and the web's Zod schema add `budgets_v10` | The view lists every generation's budgets under its key and both models refuse an unknown key; no page or component changes |

## 14. Progress

- 2026-10-27 10:48 to 11:05 UTC: the read-only diagnosis on the PC (§2), the answer and the card in the thread. 10:57:37 UTC: the owner's "A" (APPROVED). This plan written (part 0) from `main` at `e22db74`.
- 2026-10-27, on `claude/project-thread-s8cp24`, `IMPLEMENTED`: generation 10 (`definitions_v10`, catalog v10, `ROLE_GRANTS_V10`, `TEMPLATES_V10`, `BUDGETS_V10`, `TRADER_PROMPT_M11_V4`, `COACH_PROMPT_M11_V3`), the trader's four finish checks (`futures_trader.committed`), the coach's `SIT_OUT` check, the compact prompt (`Generation.compact_prompt`), migration `0026_committed_trader`, the check case's words, `budgets_v10` in the runtime view and the web's schema, the contracts and the tests (`test_m11_committed_trader.py`, and the suites that name the scheduler's trader and coach or the head revision). No page or component changed, so the shadcn skill was not needed; no dependency was added. Built on the owner's PC in this project's worktree, not in the cloud.
- 2026-10-27, VERIFIED on the PC (Windows, the locked `.venv` from `uv sync --frozen`; the web's locked `node_modules`): from `services/engine`, Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; pytest without a database `3 failed, 1035 passed, 451 skipped, 422 errors` in 92 s, the two of the baseline (`test_api.py`'s status test, `test_database.py`'s migrated database) and `test_m6_sources.py::test_dns_failure_and_a_closed_port_are_recorded_as_failures`, whose closed port reads `TIMEOUT` on Windows and which passed on Linux below. From `apps/web`: `pnpm run typecheck`, `pnpm run lint` (with `.output` removed first) and `pnpm run check` clean, `pnpm exec vitest run` `308 passed` in 36 files, `pnpm run build` built. `pnpm run api:check` could not spawn the generator's `.bin` shim on Windows (`ENOENT`), so the same comparison was made by hand: `openapi-typescript` run again on `openapi.json` gives `src/generated/api.ts` byte for byte, line ends aside. Links: `0 broken link(s)`.
- 2026-10-27 11:24 to 11:40 UTC, VERIFIED on a throwaway PostgreSQL 17.11 on the PC, apart from the app (container `asl-0044-test-pg` on network `asl-0044-test-net`, scratch secrets, the engine's own `test` image built from this branch as `asl-0044-engine-test:local`; nothing of the normal app touched): on a fresh `asl_m1_m6_s44`, `0026` applied after `0025` and the agents' suites (`test_m11_committed_trader.py`, `test_m11_trader.py`, `test_m11_reviews.py`, `test_m11_decision_reviews.py`, `test_generations.py`, `test_m6_agent_units.py`) gave `1 failed, 170 passed`: `0025`'s downgrade test still expected `0025` as the head after its restore; fixed to the head, `0026`. On a fresh `asl_m1_m6_s44b`, those six with `test_m11_scores_db.py`, `test_m11_scores_unit.py`, `test_m11_clean_start.py`, `test_m11_futures_db.py`, `test_m11_twins_db.py`, `test_m6_agents.py`, `test_m8_check.py`, `test_m6_sources.py`, `test_database.py` and `test_api.py`: `1 failed, 419 passed` in 11 min 56 s, the failure the baseline's (`test_api.py`'s status test, `decisions` reading `inactive` on a freshly migrated database, as since 2026-10-25). The rest of the full suite and the browser suites were not run (no page changed); the test resources were removed by exact name afterwards.
- NOT RUN, for the PC: the Docker build of the app and the update itself; the agents' check against the real model on generation 10; the first generation-10 decisions, refusals and entry.
- 2026-10-27: PR #135 opened. My merge was refused by the session's safety check; at 12:35:10 UTC the owner wrote "I approve", and it was merged at 12:35:52 UTC (`54c3002`).
- 2026-10-27, OBSERVED on the PC, read-only (13:52 to 13:55 UTC; SELECTs in read-only transactions and the update's record; `.env`, `secrets/` and `codex_home` not read): the owner's double-click ran the update `update-20261027T124108Z`, `COMPLETE` (12:41:00 to 13:09:48 UTC) on `54c3002`: the backup taken, `0025_decision_reviews` to `0026_committed_trader` in one bounded attempt, the services recreated, reconciliation `OK`, the five pages `200`, no problem listed. The agents' check (`CHECK`, seq 4) `PASSED` on `FUTURES_DECISION_V4` from 13:08:41 UTC and the decision verification `VERIFIED` at 13:09:01 UTC. The last `FUTURES_DECISION_V3` decision started at 13:00 UTC and the first `FUTURES_DECISION_V4` at 13:15 UTC. By 13:45 UTC, 5 generation-10 decisions, every workflow `SUCCEEDED` and no step refused: at 13:15 UTC a bar's `ENTER_LONG` (`UP`, `MEDIUM`, leverage 1, stop 2.0 ATR, take profit 2, time exit 4 hours), `FILLED` (0.055 BTC at 80,241.12331, notional 4,413.26 USDT, stop 79,879.80, take profit 80,963.70, time exit 17:15:33 UTC, risk 24.72 USDT, entry fees 2.21 USDT); then `HOLD`s after the fill (`UP`, `MEDIUM`), at the 13:30 bar (`DOWN`, `LOW`), on a sharp move at 13:35 (`UP`, `LOW`) and at the 13:45 bar (`UP`, `LOW`), each `NOTED`. The first entry of the futures account since run #1 began on 2026-10-25. NOT RUN: the pages looked at in a browser on the PC; the trade's outcome, its review and the next coach's note.
