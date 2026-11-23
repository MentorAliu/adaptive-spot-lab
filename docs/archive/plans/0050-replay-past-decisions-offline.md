# ExecPlan 0050 — Replay past decisions offline

**Status: APPROVED by the owner on 2026-11-03 at 08:07 UTC, by the pick "Replay first" on the card of the project thread "Improve the trader's accuracy" ([DECISIONS](../../DECISIONS.md#2026-11-03--replay-past-decisions-offline-execplan-0050)). The measure of §4.5 is pre-registered by this plan's first commit, before any replay call. Built in the project thread "Replay past decisions offline" from `main` at `429a0cc`, merged as `e293de4` and installed on the owner's PC on 2026-11-03 at 11:09 UTC; running, its report read when complete (§9 step 5, §14).** A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)): the trader's stored decision contexts of 2026-10-28 to 2026-11-01 go through two prompt variants and a control, one call at a time in the agents' free time, each answer recorded as a `REPLAY` and scored against what the price did. It changes no money path, no limit, no protection and nothing the trader sees or does.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `CALCULATED`, `NOT RUN`. Every threshold in §4 is a `PROPOSED` engineering default, declared before any reading and never tuned on one.

## 1. Goal

The owner asked on 2026-11-03 at 07:52 UTC, in the project thread "Improve the trader's accuracy": "Use docs/TRADING.md file, research the app implementation of what can be added/removed to enhance and improve the accuracy of the current implementation". The thread's answer (a document) found the trader's 1-hour calls at the price-only ceiling and ranked eleven changes; the only one that yields new evidence before the paired check due 2026-11-16 without restarting it is an offline replay of the stored contexts. The owner picked "Replay first" at 08:07 UTC.

Observable outcome:
1. Each of generation 11's 411 stored decision contexts of the window (§4.1) is answered again by the same model and effort as the live trader, under two prompt variants: without the feedback blocks (the scores, the coach's note and the trade lessons), and the same asked for a 4-hour call; 100 of them also under the live prompt unchanged, as a control.
2. Every answer is a `REPLAY` row: never a decision the engine answers, never a fill, never read by the trader, the coach, a reviewer, a twin or a page.
3. The calls run only in the agents' free time and yield to the trader and the veto; they never run on a paid provider or another model, and they stop while the Codex allowance is half used.
4. A report computes the pre-registered measure (§4.5): each variant's mean move in its called direction against the free rule on the same contexts, paired, with a block-bootstrap interval, and a verdict of `PASS`, `WORSE` or `NO_DIFFERENCE`.
5. The live trader, generation 11, and the paired check due 2026-11-16 are untouched.

## 2. What the app has

`OBSERVED` on the PC on 2026-11-01 at 10:15 UTC, read-only (the thread "Review trader accuracy with Fable 5.1", `second-opinion/readonly.sql` Q3 in the project's files): 411 `futures_decisions` rows of `FUTURES_DECISION_V5`, each with its context stored in its workflow's cutoff (`cutoff.futures.context`, 9.5 MB in all), none with its scores or headlines omitted. Their 1-hour record ([TRADING](../../TRADING.md#the-record-so-far)): 148 right, 108 wrong (57.8%); the last-hour rule 147 and 107; the paired difference −0.008% an hour, interval −0.055 to +0.042.

`VERIFIED` on `main` at `429a0cc`:
- The trader binds its context at its start (`futures_trader._bind_futures`) and sees it in its job context's `futures` block with the cutoff's `as_of` and `watermark`; its two reads (`query_futures_candles`, `read_headlines`) read at the workflow's cutoff (`agents/tools/futures.py`); its finish is checked by `_prepare_futures` and written as one `futures_decisions` row.
- Every call goes through the orchestrator's one inference slot (`orchestrator.py`), with the profile's `COORDINATOR` pair (`gpt-6.1-sol` at `medium` on Codex, per the profile of 2026-10-27, [ExecPlan 0046 §2](0046-leaner-agents.md#2-what-the-app-has)).
- The scorer (`agents/decision_scores.py`, [ExecPlan 0043](0043-score-every-decision.md)) stores each decision's move at 15, 60, 240 and 1,440 minutes (`futures_decision_scores.move_percent`), from the stored 1-minute candles. A replay of a context shares its decision's moves, so it needs no new scorer.
- The reviewers, the coach and the veto already take the slot only when the trader is idle and are canceled at the runner when a decision is queued (`trade_reviews._trade_gate`, `yield_to_decisions`).
- Codex's usage windows (5-hour and weekly, percent used) are read every 10 minutes while Codex runs the agents (`agents/usage_readings.py`, [ExecPlan 0049](0049-choose-the-agents-provider-and-see-usage.md)).

## 3. Scope

In: generation 13, one replay agent in three templates (§4.2); the replay set and its scheduler (§4.1, §4.3); the `futures_decision_replays` table and the `DECISION_REPLAY` artifact (§4.4); the report (§4.6); migration `0031_decision_replays`; two prompt files; the contracts.

Out: any change to the trader, its prompt, context, model, effort, policy or generation; a page (the thread reads the report and tells the owner; a page can follow on the owner's word); contexts after the window; another model; promoting anything (a `PASS` is evidence for the next trader generation's own ExecPlan, which the owner installs or not). No new host, dependency, secret, data source or permission.

## 4. Design

### 4.1 The replay set `REPLAY_SET_V1` (code, in `TEMPLATES_V13`)

- **Contexts:** every `futures_decisions` row whose workflow ran `FUTURES_DECISION_V5` with purpose `DECISION`, with `context_at` before 2026-11-01 10:15:00 UTC and its context stored: the 411 of §2 (the report counts them; the window, not the count, is what is fixed).
- **Arms:**

| Arm | Template | Prompt | Context | Contexts |
|---|---|---|---|---|
| `CONTROL` | `DECISION_REPLAY_CONTROL_V1` | `trader.v5.md` unchanged | as stored | 100, the seeded sample below |
| `NO_FEEDBACK` | `DECISION_REPLAY_NO_FEEDBACK_V1` | `trader-replay.no-feedback.v1.md`: v5 without the sections on the coach's note, the lessons and the scores | as stored without `scores`, `advice` and each recent trade's `review` | all |
| `CALL_4H` | `DECISION_REPLAY_CALL_4H_V1` | `trader-replay.call-4h.v1.md`: the no-feedback prompt with the call over the next 4 hours, scored at the 4-hour close | as `NO_FEEDBACK` | all |

- **Order and sample:** contexts in the order of `sha256("REPLAY_SET_V1|" + decision_id)`, each context's arms in the order `CONTROL`, `NO_FEEDBACK`, `CALL_4H`, so a partial replay stays balanced across arms and days. `CONTROL` takes the 100 contexts with the smallest `sha256("REPLAY_SET_V1|CONTROL|" + decision_id)`. Both depend on the IDs only, never on an outcome.
- **Calls:** 922 items; each item at most 3 started workflows (a yield, an expiry, a refusal after its retry or a provider failure starts it again later); a model's own abstention is its answer (§4.5).

### 4.2 The replay agent: generation 13

- Three templates, one per arm, role `COORDINATOR` (the trader's, so the profile gives them the trader's model and effort), purpose `REPLAY`, started by `SYSTEM` only. Step schema v8 (the trader's), the trader's two reads and its finish tool exactly as catalog v11 shows them, so the model sees the trader's job; the catalog document records that in generation 13 a finish is a replay record. Budgets: the trader's (3 model steps, 2 tool calls, 180 s, 120 s a step, one retry after a refusal); 192 a UTC day.
- **The job context** is the trader's, built from the stored decision: `futures.context` is the stored context (transformed for the arm), the cutoff's `as_of` and `watermark` are the original's, so both reads answer as of the original cutoff, and the parameters shown are the original's `symbols` and `trigger`. What differs from the live call: the job and step IDs, the template and purpose names, and the arm's changes.
- **The finish** is checked by the trader's own rules (one action with only its choices, citations, the position it saw, the coach's note pairing, and generation 10's four commit rules), extracted from `_prepare_futures` without change, except the agents' check, which only gates live entries. It is recorded as a `DECISION_REPLAY` artifact and one `futures_decision_replays` row (§4.4), never a `futures_decisions` row.

### 4.3 When a replay runs (the pacing)

SYSTEM queues at most one replay workflow at a time, the next unanswered item, only when all of these hold; otherwise it waits and logs why:
1. The runtime is enabled and nothing blocks it (auth, usage limit, profile), as for every agent.
2. The provider in force is the Codex CLI (`CODEX_CLI`), and the profile's `COORDINATOR` pair equals the pair of the original decision's call. No replay runs on a paid API or another model.
3. The reviewers' gate (`_trade_gate`): not in the HH:59:30 to HH:06 quiet window, no decision queued or open, 30 s since the last decision ended, no veto waiting, and the workflow can end 60 s before the next 15-minute bar. No reviewer, decision reviewer, coach or veto is queued or open: they go first.
4. At most 2 replays started in the current 15-minute bar, and 192 a UTC day.
5. The newest good Codex usage reading is at most 20 minutes old, names at least one window with a percent, none reached, and every window below 50% used. No reading means no replay.

A replay call in flight is canceled at the runner when a decision is queued or a veto is waiting (`YIELDED_TO_DECISION`), as the reviewers' are; its item runs again later. The orchestrator's priority puts `REPLAY` last.

### 4.4 The record

`futures_decision_replays` (append-only, written only by the agent identity from its own running replay workflow bound to that decision and arm, with its artifact): the set, the arm, the original decision and its context time, the replayed context's hash, the action, `expected_move`, `uncertainty_level`, `reason_code`, the call's horizon (60 or 240 minutes), the model and effort, the free rules' signs (the sign of the stored `returns_percent` 1h and 4h), the original's `expected_move`, and the database's time; labeled `REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL`. One row per set, arm and decision. Nothing the trader, the coach, the reviewers, the twins or the pages read touches it (a test reads every agent module).

### 4.5 The measure, pre-registered

For each item the score at horizon `h` is the move at `h` in the called direction: `+move_h` for `UP`, `−move_h` for `DOWN`, `0` for no call (`NO_VIEW`, an abstention). `move_h` is the original decision's `futures_decision_scores.move_percent` at `h` minutes, `SCORED`; an item without one is left out and counted. The free rule's score is the same with the sign of the stored feature (`returns_percent` 1h for the last-hour rule, 4h for the last-4-hours rule), `0` when it is zero. Items are in time order (`context_at`).

**Primary, one per variant** (the trial ledger counts two; each interval is 97.5%, Bonferroni for two):
- **P1** `NO_FEEDBACK` at 60 minutes against the last-hour rule: the mean of the paired differences (arm minus rule) over the arm's answered items, with a stationary bootstrap interval (`app.evaluation.bootstrap`, mean block 8 calls, 2,000 resamples, seed `derive_seed("REPLAY_SET_V1", "P1")`).
- **P2** `CALL_4H` at 240 minutes against the last-4-hours rule: the same with mean block 16 and seed `"P2"`.
- **Verdict:** `PASS` when the interval's lower end is above 0, `WORSE` when its upper end is below 0, otherwise `NO_DIFFERENCE`. Read only once the arm has an answer for at least 95% of its items; before that `INCOMPLETE`.

**Secondary**, 95% intervals, never a verdict: S1 each arm's hit rate at its horizon (right and wrong beyond the 0.12% band, Wilson interval before overlap) and its rule's on the same items; S2 `CALL_4H` against `NO_FEEDBACK`'s calls judged at 240 minutes (the 4-hour question alone, block 16); S3 `NO_FEEDBACK` against the live calls at 60 minutes (block 8); S4 the replay's fidelity: `CONTROL`'s agreement with the live calls on its 100 contexts and its paired score against them, and each arm's agreement with its rule; S5 each arm's confidence shares and the entries it would have proposed; S6 the live calls against the last-hour rule on this set (the yardstick's own reproduction).

What a verdict means: `PASS` makes the variant a candidate for the next trader generation's own ExecPlan; `WORSE` drops it; `NO_DIFFERENCE` means the replay cannot tell it from the rule. Nothing in the app changes from a verdict.

### 4.6 The report

`python -m app.agents.replay_report`, run in the API's container as the API identity (read-only), prints the progress (items answered, missing with their reasons, per arm) and the measures of §4.5 as JSON and as a short text. Pure functions over the rows, tested on fixtures. The thread runs it on the PC on the owner's word and tells the owner the result in plain words.

### 4.7 The trading review (TRADING.md's eight questions)

1. **Rules:** paper only; the replay writes no decision, no order and no fill, and moves no limit. Research, on the owner's word (the pick of 08:07 UTC) and this plan (`OBSERVED`).
2. **Class:** research, a replay; the trader sees and does nothing differently, so the 2026-11-16 reading does not restart (`VERIFIED` by design: no trader file, prompt, context or definition changes). The install composes a new profile (generation 13's hashes) and the agents' check runs again, as for every agent update.
3. **Costs:** no trade; the cost is model calls (question 8).
4. **Horizon:** `CALL_4H` asks the question at the hold's own horizon (principle 4), the one change the record points to (46% at 4 hours from a 1-hour call).
5. **The model's place:** both variants are still the model forecasting from numbers (principle 5); the replay tests whether they do worse or better than the rule, not whether they read text.
6. **The yardstick:** the free rule at the same horizon on the same contexts, paired, as TRADING.md names it; `CALCULATED` from TR-36's interval (±0.048 at 95% on 391 hours), a variant needs about +0.055% an hour over the rule to `PASS` at 97.5%, two-thirds of the rule's own +0.082%: the replay catches a large difference or a worse variant, and a small edge stays `NO_DIFFERENCE`.
7. **Pre-registration:** §4.5, committed before the first call. **Trial ledger:** two trials (`NO_FEEDBACK`, `CALL_4H`); `CONTROL` is a calibration, not a trial. Added to TRADING.md.
8. **Clock and cost:** no reset. 922 workflows, about 950 calls with retries; at generation 11's measured 13,933 input and about 300 output tokens a call (0.77 Codex credits, [0046 §14](0046-leaner-agents.md#14-progress)), about 730 credits, eight to nine days of the trader's own use (`CALCULATED`), spread over at least 5 days by the 192 a day; paused by the allowance rule of §4.3.

## 5. Authority

[AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) change with the code:
- The replay templates are started by `SYSTEM` only, never by a model or the owner's pages; they hold the trader's two reads at the original cutoff and finish only with a replay record. They cannot record a decision the engine answers (the decision guard accepts only the trader templates), start a workflow, use another tool, or reach the owner's account, a run, a limit, a policy or a twin.
- The trader is unchanged: `FUTURES_POLICY_V1`, generation 11, the risk gate and code's protection stay as they are.
- Rule 13's money-path review: no money path changes (no ledger, journal, reservation, account state or engine code), so the independent review is not required; the extraction from `_prepare_futures` is covered by the trader's existing tests.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| R1 | The set is the window's decisions; the order and the `CONTROL` sample follow from the IDs alone; 922 items for 411 contexts | Unit tests on fixtures |
| R2 | Each arm's context is the stored one with exactly its blocks removed; `CONTROL`'s is byte-identical; the prompts differ from v5 only where §4.1 says | Unit tests; a prompt diff test |
| R3 | The job context shows the original `as_of`, `watermark`, `symbols`, `trigger` and the trader's tools; the reads answer at the original cutoff | Database tests |
| R4 | A finish is checked by the trader's rules and written as one replay row with its artifact; never a `futures_decisions` row, a fill or a trader context change; a second row for the same item is refused | Database tests, positive and negative; the guard's refusals |
| R5 | §4.3's conditions each hold back a replay, and each alone; a call in flight is canceled when a decision is queued or a veto waits; at most 2 a bar and 192 a day; at most 3 starts an item | Scheduler tests with a fake clock and the fake runner |
| R6 | No replay on a provider other than `CODEX_CLI`, on a pair other than the original's, without a fresh reading, or with a window at 50% or more | Scheduler tests |
| R7 | The report's scores, pairings, intervals, verdicts and counts match hand-computed fixtures; the seeds reproduce | Unit tests |
| R8 | No agent module but the replay's reads `futures_decision_replays` | A test over every agent module's source |
| R9 | Migration `0031` up, down and up on a scratch database; its downgrade refuses once a replay workflow or row exists or a profile binds generation 13 | Migration tests |
| R10 | The trader's own tests pass unchanged after the extraction | The existing M11 suites |
| R11 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host, data source or model. The bootstrap is Politis and Romano (1994), implemented in `app.evaluation.bootstrap`; the Wilson interval is Wilson (1927), as the earlier reviews used. Codex's usage windows are ExecPlan 0049's (`account/rateLimits/read`).

## 8. Data and trust boundaries

- No new host, secret, volume or network path; the runner still has no database, repository or credential.
- New stored data: the replay rows and their workflows, artifacts and calls, kept in every backup.
- The stored contexts hold headlines (external text, labeled as before); a headline written to steer the model can at most change one replay row.

## 9. Implementation sequence

1. This plan, committed before any code (the pre-registration).
2. Generation 13's definitions and prompts; the replay module (set, bind, finish, scheduler, yield); migration `0031`; the report.
3. Tests (§6), the cloud checks (§10), the contracts and STATUS.
4. The pull request; the owner's word to merge; the owner's double-click of `update-app.cmd`; the thread checks the install read-only on the PC (the agents' check passed on the new profile, the first replay rows, the trader's decisions on time).
5. The thread reads the report on the PC after about 5 days, or when it says complete, and tells the owner the result with its labels; TRADING.md's record gains the rows.

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL (the new suites, the M11 agent suites and the full engine suite), the update model and the link check, with results in §14. The web gains only the runtime read's `budgets_v13` (§13), so its checks run too. `NOT RUN` in the cloud and done by the update or its check on the PC: the Docker build, the agents' check against the real model, the replay's real calls and the report on the PC's data.

## 11. Failure and rollback

- A replay fails, is canceled or refused: its item runs again later, at most 3 starts; then it is counted as missing in the report.
- The allowance or the provider changes: the replay waits; nothing else changes.
- Rollback: the update's rollback tags bring back the previous images; migration `0031`'s downgrade refuses once a replay workflow or row exists (fix forward). An older worker on a database at `0031` simply starts no replay.

## 12. Q01–Q10

Q01, Q02: no page. Q03: R1 to R7. Q04: no new secret or host. Q05: the yield, the expiry, the retry, the usage pause (R5, R6). Q06, budgets declared before measuring: the trader's time from a bar's close to its decision's start is no longer than before (read on the PC from the decisions of the first replay day against the day before); a replay call ends within 180 s; the report runs within 30 s. Q07: the cloud suites. Q08: the scheduler's waiting reasons in the agent worker's log; Settings' Codex card counts the replay's calls with every other call. Q09: the migration and its downgrade (R9); the update's backup. Q10: the contracts of §5 and the data contract; no new dependency.

## 13. Decision log

- 2026-11-03, by the thread under the owner's "decide for me" (2026-10-19), each the recommended engineering choice:
  - **In the app, on the agents' slot**, not a script calling the runner: the slot, the yield, the quiet window, the usage block and the profile come for free, and nothing runs beside the trader's calls.
  - **A control of 100 contexts** (the coordinator's brief named two variants): it measures how far a replay drifts from the live call, which no variant can measure itself; about 100 calls more than the "about 800" of the card.
  - **`CALL_4H` without the feedback blocks:** the scores are of 1-hour calls and would contradict a 4-hour question; built on `NO_FEEDBACK`, the pairing S2 isolates the question itself.
  - **The trader's tools and catalog shown unchanged**, answering at the original cutoff: the control then sees the live job; the replay templates' grant names the trader's finish tool, but their finish writes only a replay row and the decision guard refuses any other.
  - **No view scores 0** in the primary: a variant cannot gain by abstaining on hard hours.
  - **Generation 13 is the replay;** the trader bundle of the accuracy document (its items 3, 4, 5, 8 and 9) becomes generation 14 when the owner approves it.
- 2026-11-03, while building (§9 step 2), by the thread under the same word; none touches the measure of §4.5:
  - **The 4-hour arm's answer format** is step schema v8 with one sentence of the decision's description changed ("over the next 4 hours"), stored as `AGENT_STEP_SCHEMA_V8_CALL_4H` beside v8, with the same fields and parser: otherwise the format the runner sends would ask for the next hour while the prompt asks for 4 hours. `CONTROL` and `NO_FEEDBACK` answer in v8 exactly. A generation may now name a template's own format (`Generation.template_schemas`); only this template does.
  - **The model pair of an item** is the requested model and effort of the original decision's last provider call; a call from before ExecPlan 0049 names no provider and is the Codex CLI's.
  - **What counts as a start:** a workflow that started, or failed at its start. One that yielded or expired before it started is not counted, and its item is queued again under the next identity.
  - **A queued replay waits at its start** while its gate is closed or the profile's pair is no longer the item's, as the reviewers do, and expires otherwise.
  - **The ready queue ranks `REPLAY` 6**, after every other purpose (the others keep 0 to 5).
  - **The trader's finish rules** are extracted from `_prepare_futures` as `futures_trader.check_finish` in the same order; the trader's tests run unchanged (R10).
  - **The report withholds the numbers** of a primary measure (`INCOMPLETE`, no mean or interval) and of each arm's secondary measures until the arm has 95% of its items, so that no partial reading is seen before the rule of §4.5 allows it. S6 (the live calls against the rule) is always shown: it reads no replay.
  - **`CONTROL` keeps the stored `advice`,** so its pairing of `advice_use` follows what the original call saw; the other arms are told no note is shown (`NO_ADVICE`).
  - **The database tests' stored decisions** are made by a scripted generation-11 trader on synthetic rows and then dated into the window (the window is in the past); their rows and cutoffs are changed only there, as the superuser of the scratch database.
  - **The runtime read names generation 13's budgets.** The API's `AgentRuntimeView` and the web's `runtimeSchema` are strict and list every generation's `budgets_vN`; without `budgets_v13` the Agents page's one read failed (`OBSERVED` in the cloud by `test_m11_no_owner.py` and `test_m10_trading.py`, then fixed). The field is added to both, `openapi.json` and `apps/web/src/generated/api.ts` regenerated; no page shows it, so this is not a page change (§3).
  - **No page shows a replay.** The API's workflow models name the purposes up to `DECISION_REVIEW` (`AgentWorkflowSummary`; `ENTRY_VETO` is not among them either, `OBSERVED` on `main` at `429a0cc`), so a replay workflow's detail is not readable through them; no page links one, and the plan keeps the web out of scope (§3). The report is how the replay is read.

## 14. Progress

- 2026-11-03 08:08 UTC: thread started from `main` at `429a0cc`; the plan written and committed before any code (the pre-registration).
- 2026-11-03, 08:15 to 10:15 UTC: §9 steps 2 and 3 `IMPLEMENTED`: generation 13 (`definitions_v13`, the two prompt files, `AGENT_STEP_SCHEMA_V8_CALL_4H`), `app.agents.decision_replays`, `futures_trader.check_finish`, migration `0031_decision_replays`, `app.agents.replay_report`, the runtime read's `budgets_v13`, the tests of §6 and the contracts. The cloud checks, in this session, on a disposable PostgreSQL 16 cluster on 127.0.0.1 with scratch secrets only:
  - `VERIFIED`: Ruff `All checks passed!`; `FastAPI OpenAPI schema matches` (after `openapi.json` gained `budgets_v13`); pytest without a database `2 failed, 1154 passed, 484 skipped, 444 errors`, the two failures the documented baseline's (`test_api.py`'s status and `test_database.py`'s migrated database, both needing a database).
  - `VERIFIED` on the scratch cluster: `0031` up, down and up on a fresh database; `test_m11_replay_unit.py` `18 passed`; `test_m11_replay_db.py` `6 passed`.
  - `OBSERVED`, then fixed: the M11, generation and agent suites (`tests/test_m11_*.py tests/test_generations.py tests/test_agent_*.py tests/test_m6_agent_units.py`) gave `6 failed, 539 passed`. Three were `main`'s known `test_m11_scores_db.py` failures ([COMMANDS](../../COMMANDS.md)); three were this change's: the API's strict `AgentRuntimeView` refused `budgets_v13` (`test_m11_no_owner.py`; `test_m10_trading.py` without a database), the definitions count (`test_m6_agent_units.py`, 94 to 101) and `test_m11_futures_db.py`'s grant inventory meeting the new table. After the fixes (§13), those files with the replay suites: `110 passed`.
  - `VERIFIED` on a fresh database, the whole engine suite at the final code: `6 failed, 2004 passed, 74 errors` in 68 minutes. Every failure and error is the documented baseline: `test_api.py`'s status, `test_m6_schema.py`'s downgrade, `test_m2_stream_continuity.py`'s `QUEUE_OVERLOAD` on the cloud machine, `test_m11_scores_db.py`'s three; the 74 errors are `test_m1_account.py`'s 13 and the research store's 61 (`test_m6_bridge`, `test_m6_runner`, `test_m6_shadows`, `test_m6_staging`, `test_m7_control_bridge`), which need the research cluster.
  - `VERIFIED` web (`apps/web`, after `pnpm install --frozen-lockfile`): `typecheck`, ESLint (exit 0), Prettier, `api:check` (`Generated TypeScript API types match`), Vitest `47` files and `401` tests passed, `build`.
  - `VERIFIED` runner (standard library): `tests.test_providers` `Ran 29 tests … OK`; `tests.test_units` `Ran 21 tests`, the two image tests failing outside the image as documented.
  - `VERIFIED`: `tools/check_links.py` `0 broken link(s)`.
  - `NOT RUN`: the Docker build and images, the update model (no PowerShell in the cloud; `tools/` unchanged), the browser suites (no page changed), the agents' check against the real model, any real replay call, the report on the PC's data, and Q06's timing budgets, all on the PC after the install. No money path changed, so no independent review applies (AGENTS.md rule 13).
- 2026-11-03 10:40 UTC: the owner's word to merge (the thread's card, "Merge, I'll double-click"); [#167](https://github.com/MentorAliu/adaptive_spot_lab/pull/167) merged as `e293de4`.
- 2026-11-03, the owner's double-click of `update-app.cmd`. `OBSERVED` read-only on the PC from 11:13 to 11:17 UTC, in a session that changed nothing (its SQL ran with `default_transaction_read_only=on`):
  - The record `update-20261103T104146Z\update.json`: `COMPLETE`, 10:41:38 to 11:09:49 UTC, commit `e293de4` (the app's previous install `51f9929`), the migration `0030_veto_twins` to `0031_decision_replays` in one attempt. Nine services replaced: api, web, the market, execution, evaluation and agent workers, agent-egress, agent-runner and source-fetcher. Its own checks: schema `0031_decision_replays`, reconciliation `OK`, the five pages answering 200, the agents `ENABLED` with their check passed, no problem. The backup is 79,899,919 bytes.
  - All 10 containers up with no restart, 9 healthy (the market worker has no health check), each on the image the record names; PostgreSQL was not recreated.
  - The profile in force is the app's new one (seq 24, recorded by SYSTEM at 11:08:39 UTC, naming generations 1 to 13); its check (seq 10) `PASSED` at 11:08:51 UTC, 1 of 12 calls; the decision and capability verifications `VERIFIED`.
  - The replay: `DECISION_REPLAY_NO_FEEDBACK_V1` queued at 11:08:55 and `DECISION_REPLAY_CALL_4H_V1` at 11:09:10 UTC, both `SUCCEEDED`, each with its row (11:09:06 and 11:09:22 UTC), both for the same decision and both `ENTER_SHORT` / `DOWN`; that decision is not in the `CONTROL` sample. The worker then logged `agent_replay_waiting` with `BAR_SPENT`, `NEXT_BAR_TOO_CLOSE`, `DECISION_OPEN` and `AFTER_A_DECISION`, in that order; no yield, and no `Traceback`, `ERROR` or `_failed` line.
  - The trader: 13 decisions from 08:15 to 11:15 UTC, one each bar, none missing, all `SUCCEEDED`. From the bar's close to the start: 1.8 to 16.1 s (mean 9.1 s) for the 10 before the update, 12.2 and 15.8 s for the two during it on the old worker, 5.2 s for 11:15 on the new one. Q06's budget (no later than before) holds on this one decision; the first replay day against the day before is still to read.
  - The report (`python -m app.agents.replay_report`, exit 0): "REPLAY_SET_V1: 410 contexts, 920 items."; `CONTROL` 0 of 100, `NO_FEEDBACK` and `CALL_4H` 1 of 410 each; P1 and P2 `INCOMPLETE`. S6, the live calls against the last-hour rule at 60 minutes over the 410 (`CALCULATED`, reads no replay): mean −0.0077% an hour, 95% interval −0.0514% to +0.0386%.
  - **The set holds 410 contexts, not 411.** By its rule (§4.1, purpose `DECISION`, context before 2026-11-01 10:15 UTC) the PC holds 410, and 410 before 10:15:07 too; the 10:15 bar's decision was stored at 10:15:15. The 411 of the accuracy document came from a count without the purpose filter (`second-opinion/readonly.sql` Q3), so it most likely included one decision of the agents' check (`PROBE`), which the rule leaves out (inferred, not checked row by row). The rule, not the count, defines the set; the items are 920 (410 × 2 + 100), and the measure of §4.5 is unchanged.
  - `NOT RUN`: the replay's progress after 11:17 UTC; Q06's replay call time (the two calls took 11 and 12 s) and report time beyond this one run.
- 2026-11-08, `OBSERVED` read-only on the PC at 09:22 UTC by the thread's check-in, on the owner's "Go" (recorded here from that read's notes): 461 of 920 answered (`NO_FEEDBACK` 205, `CALL_4H` 205, `CONTROL` 51), none failed, every row on the trader's model at its effort; the lane paused since 2026-11-07 11:06 UTC on `USAGE_HALF_USED`, the weekly Codex window at 58% (ExecPlan 0052's backtest may use it to 80%), until the weekly reset of 2026-11-11 06:45 UTC.
- 2026-11-12, `OBSERVED` read-only on the PC from 09:29 to 09:30 UTC (thread "Bring the app up to date now", on the owner's "don't wait for anything on the future" of 09:23 UTC; one READ ONLY transaction rolled back, and the report): `python -m app.agents.replay_report` exit 0, 581 of 920 answered, `NO_FEEDBACK` and `CALL_4H` 259 of 410 each, `CONTROL` 63 of 100 (63% each), the rest `NOT_STARTED`; P1 and P2 `INCOMPLETE`; S6 unchanged (−0.0077% an hour, 95% −0.0514% to +0.0386%). Answers a day: 44 on 2026-11-11 (the app ran again from about 18:30 UTC, [0059 §14](0059-the-slow-rule-trades-the-main-account.md#14-progress)) and 76 on 2026-11-12 to 09:15 UTC: 8 an hour, the lane's two a bar. The Codex windows at 14% (5 hours) and 7% (week). `CALCULATED`: 95% of every arm around 2026-11-14 at that pace; the 2026-11-14 08:00 UTC check-in reads the verdicts. Since ExecPlan 0059 the trader is not asked, so the replay no longer yields to it, and the ChatGPT backtest (0052) no longer takes turns with it.
