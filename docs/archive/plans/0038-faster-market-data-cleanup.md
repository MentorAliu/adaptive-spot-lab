# ExecPlan 0038 — Faster market-data cleanup, and a named cause for each feed drop

**Status: APPROVED by the owner on 2026-10-23 at 09:13 UTC ([DECISIONS](../../DECISIONS.md#2026-10-23--the-owner-approves-a-faster-market-data-cleanup-execplan-0038)); IMPLEMENTED and checked on 2026-10-23 on an isolated PostgreSQL 17 on the owner's PC ([§12](#12-progress)); installed on the PC the same day (`890ba30`, record `COMPLETE`, [§12.3](#123-installed-on-the-pc)).** Written by the project thread "Market data unavailable" from `main` at `2672888`. Not a milestone: it changes the market worker's hourly cleanup (the retention function, in a new migration `0017`) and what the worker records when it drops the price feed. No money path, protection, limit, policy, agent definition, API route or page changes.

Labels: `OBSERVED` (seen in code, records or on the PC), `INFERRED`, `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal

The owner saw "Market data unavailable" on 2026-10-23 at 08:13 UTC and answered "yes" at 09:06 UTC to: "Should I write an ExecPlan to fix the slow cleanup so these drops stop?"

Observable outcome:
1. A cleanup call finishes far inside its two-second deadline whatever the size of the backlog, and `RETENTION_FAILED` stops appearing in normal running.
2. Every feed drop for `QUEUE_OVERLOAD` records which database call was slow and for how long, so the next drop names its cause instead of leaving it to inference.

What this plan does not promise: that the feed drops stop. The cleanup is close to its deadline (§2.2), but only some drops coincide with a cleanup pass (§2.3). Item 2 above is there to settle the rest.

## 2. What was observed on 2026-10-23

All `OBSERVED` with read-only queries (`BEGIN READ ONLY`) on the normal database and the logs of the running containers, 08:14 to 09:30 UTC.

### 2.1 The drop the owner saw

- 08:12:03 UTC: `COLLECTION_GAP` with `QUEUE_OVERLOAD` (a received frame waited more than one second to be written, `pipeline.py:102`). The worker started a new collection at 08:12:08.
- 08:13:02 to 08:19:48: the owner's update of `8b5b898` (record `update-20261023T081310Z`, `COMPLETE`). It recreated `market-worker` at about 08:17; a second `QUEUE_OVERLOAD` came at 08:13:38, during its backup.
- At 08:20:17 all five feeds were `CONNECTED` with quotes under a second old.
- The system status says `unavailable` when no feed is connected (`main.py:1390`), so each reconnect shows "Market data: unavailable" on the Settings page for a few seconds, and Home says "Live prices are unavailable".

### 2.2 The cleanup is at its deadline

- **One hourly pass:** 19 to 25 calls of `asl_prune_market_evidence`, deleting about 10,000 observations and 10,000 payloads (46 passes, 2026-10-21 10:07 to 2026-10-23 08:17, from `market_retention_manifests`).
- **Call times:** 360 to 680 ms on average per pass; the slowest call of a pass up to 1,968 ms (2026-10-22 11:08), 1,913 ms (2026-10-23 06:12) and 1,888 ms (2026-10-22 20:08), against the market identity's 2,000 ms statement deadline (`app/db.py`).
- **Failures:** 68 `RETENTION_FAILED` in seven days (23 on 2026-10-18, 18 on 2026-10-19, 9 on 2026-10-22). Each was retried and recovered, as [ExecPlan 0024](0024-retention-failure-keeps-the-worker.md) designed. The PostgreSQL log names the statement of four of them (2026-10-22 13:13:16, 13:14:47, 13:17:11, 2026-10-23 08:13:17): three times line 27, the search for orphan payloads, and once line 39, the payload delete.
- **Why line 27 is slow** (ExecPlan 0024 §4.4, measured in isolation then, and consistent with these counts): it looks for unreferenced payloads among *all* payloads older than seven days, one index lookup in `market_observations_payload` each, in every call. There are 10,341 such payloads today. About 1,700 of them are kept for good (instrument snapshots and final candles keep their payloads, about 96 a day since 2026-09-28) and are examined again in every call; that part only grows. The rest is the hour's backlog.
- **The database:** `shared_buffers` is PostgreSQL's default 128 MB; the three market tables hold 2.4 million rows each and 4.2 GB together (`market_payloads` 2.1 GB, `market_observations` 1.7 GB, `market_publications` 0.4 GB). Those random index lookups therefore mostly miss PostgreSQL's own buffers (INFERRED).
- **The five unindexed references** of ExecPlan 0024 §4.2 are still unindexed: `strategy_evaluations` has 860 rows, `orders` 20, `fills` 20. Each deleted observation is checked against them by a scan.

### 2.3 What the feed drops coincide with

Eight `COLLECTION_GAP`s from 2026-10-22 00:00 to 2026-10-23 08:20, and the update's recreate:

| When (UTC) | Code | At the same time |
|---|---|---|
| 2026-10-22 01:00:09 and 2026-10-23 01:00:09 | `stream_silent` | Nothing of ours: the stream went quiet at 01:00 both days (INFERRED: on the provider's side) |
| 2026-10-22 12:43:44 | `QUEUE_OVERLOAD` | Nothing found |
| 2026-10-22 13:15:31 | `QUEUE_OVERLOAD` | A cleanup pass that failed four times (13:13 to 13:17) |
| 2026-10-22 20:01:36 | `QUEUE_OVERLOAD` | The owner's update of 19:47 to 20:11 |
| 2026-10-23 08:12:03 | `QUEUE_OVERLOAD` | Four seconds after a PostgreSQL checkpoint whose sync took 0.515 s; the cleanup pass began about a minute later |
| 2026-10-23 08:13:38 | `QUEUE_OVERLOAD` | The update's backup, and a failing cleanup pass |
| 2026-10-23 08:16:50 | (recreate) | The update recreated the worker |

A checkpoint with a slower sync (0.589 s, 2026-10-23 02:11:59) came with no drop, so the checkpoint is not a clear cause either. Each reconnect took about five seconds (`market_collections`). `QUEUE_OVERLOAD` was recorded 25 times in 14 days.

**Not known:** which database call was slow in each drop. The worker records the queue's state when it drops the feed, not which call stalled it. §4 D3 adds that.

## 3. Scope and exclusions

**In scope:** a new migration `0017_market_retention_cost` (the retention function's payload search, its bookkeeping row, five indexes); the market worker's overload record (`worker.py`, `pipeline.py`); their tests; the contract text in [MARKET_DATA](../../MARKET_DATA.md); the update to the PC.

**Not touched:** the retention rules (seven days, 730 days, pins, confirmations, instrument snapshots, manifests and their digest format), the call size of 500 observations, the function's two-argument signature and grants, the statement, lock and idle deadlines, the fence, the overload threshold of one second, the retry schedule of ExecPlan 0024, PostgreSQL's configuration, the API, the web app and every other worker.

## 4. Design (PROPOSED)

**D1 — Look for orphan payloads only where they can be.** `CREATE OR REPLACE FUNCTION asl_prune_market_evidence(uuid, bigint)` in migration `0017`, same signature, owner, `SECURITY DEFINER`, `search_path` and grants, so the worker that runs during the update keeps calling it unchanged.
- The observation selection and its rules are unchanged (lines 10 to 24 today). The observation delete returns the payload ids of the observations it deleted.
- **Payloads of this call's observations:** a payload among those ids is deleted when no observation and no confirmation refers to it any more. A payload shared by two observations goes with the second one. At most 500 lookups, all for payloads whose pages the delete has just touched.
- **A bounded sweep for every other orphan** (payloads stored without an observation, such as an `INVALID` frame's, and the orphans left by the old function when it is replaced): each call examines at most 200 payloads older than seven days, in `(received_at, id)` order after a position kept in a new one-row table `market_retention_cursor`, deletes those that nothing refers to, and moves the position to the last one examined. It uses the existing index `market_payloads_retention (received_at, id)`. A payload that is kept (it still has an observation) is examined once, when the position passes it, never again in every call. Deleted payloads leave the index, so the sweep walks only what stays: about 96 kept payloads a day plus the orphans, far below 200 a call.
- The table is written only by the function: no role is granted anything on it. The worker reads nothing from it.
- **The manifest** is unchanged: one row per call that deleted something, its digest over the deleted observations' and payloads' ids and hashes in the present format.
- **Expected effect (INFERRED from §2.2, to be measured in §5):** the payload search goes from about 10,000 index lookups a call to at most about 700, and its cost no longer grows with the kept payloads or with a backlog after the PC was off.

**D2 — Index the five references** of ExecPlan 0024 §7 item 2, in the same migration: `strategy_evaluations (bar_observation_id)`, `orders (decision_quote_observation_id)`, `orders (instrument_observation_id)`, `fills (quote_observation_id)`, `fills (instrument_observation_id)`. The tables are small today (900 rows together), so each index builds in milliseconds inside the migration; without them every deleted observation scans them, a cost that grows with every evaluation and trade.

**D3 — Name the slow call.** The worker times each database call of the stream path (`ingest_frames`, `update_feed`, `telemetry` and the control calls). When a collection fails (`QUEUE_OVERLOAD` among other causes), the `COLLECTION_GAP` detail and the `market_collection_gap` log line gain `slowest_call`: the call's name, its duration in ms, when it started and whether it was still running, over the last 30 seconds, taken before the teardown's own calls; and `retention_running`: whether a cleanup call was in flight. The incident detail is free JSON, so this needs no schema or API change. Nothing else of the overload rule changes.

**Considered and not chosen:**
- *A longer statement deadline for cleanup calls:* a call holds the lease row shared, and a new generation's epoch update waits for it under a one-second lock deadline (ExecPlan 0024 §3).
- *Smaller calls:* they shorten the deletes in proportion and leave the search, which examines the whole backlog whatever the call size (ExecPlan 0024 §4.7).
- *More PostgreSQL memory (`shared_buffers`):* it would help every query, the stream's writes included, and is a change of the database's configuration on the owner's PC with its own memory budget (the Docker VM has about 7.7 GiB). Left for a separate decision once D3 shows whether the drops are I/O waits.
- *Turning JIT compiling off in the function:* measured inside the noise of a call in ExecPlan 0024 §6.

## 5. Requirements and tests

Engine tests on a scratch PostgreSQL 17 (`services/engine/tests/`, beside `test_m2_retention_faults.py`):

| ID | Requirement | Test |
|---|---|---|
| R1 | A deleted observation's payload goes in the same call when nothing else refers to it | Two expired quotes with their own payloads: one call deletes both observations and both payloads |
| R2 | A shared payload stays until its last observation goes | Two observations on one payload, one pinned: the payload stays; unpin and expire: it goes |
| R3 | Kept evidence stays | A confirmation's payload, an instrument snapshot's payload and a final candle's payload are never deleted |
| R4 | Orphans with no observation go through the sweep | An expired `INVALID` payload is deleted within the calls the sweep needs to reach it |
| R5 | The sweep is bounded and moves on | 1,000 expired kept payloads: each call examines at most 200 (position moves by 200), and after five calls none is examined again |
| R6 | The old function's leftovers are drained | 300 expired orphans that the replaced function left: the sweep deletes all of them |
| R7 | Rules, lease and manifest unchanged | The existing retention tests pass unchanged; a lost lease raises `market retention lease lost`; the manifest digest of R1 matches the present formula |
| R8 | Cost | On a store with 2.4 million payloads of which 10,000 are expired and 1,700 kept (synthetic, in production shapes): `EXPLAIN (ANALYZE, BUFFERS)` of a call's payload statements reads at most about 700 index entries; the call time on cold and warm buffers is recorded against ExecPlan 0024's 357 and 576 ms |
| R9 | The migration | `0016 → 0017 → 0016 → 0017` on a copy with data: the downgrade restores the `0004` function body, drops the table and the five indexes; the schema fingerprint after the second upgrade equals the first |
| R10 | The slow call is named | A worker test with a database call held for 1.5 s: the `COLLECTION_GAP` detail carries `slowest_call` with that call's name and a duration of at least 1,500 ms, and `retention_running` |
| R11 | Nothing else changes | `ruff`, the OpenAPI drift check (no change expected) and the database-free pytest pass |

## 6. Official sources

- PostgreSQL 17: `CREATE FUNCTION` / `CREATE OR REPLACE FUNCTION` (keeps the owner and grants of an existing function of the same signature), `DELETE … RETURNING`, foreign-key checks on `DELETE` (a referencing column without an index is scanned per deleted row), `EXPLAIN (ANALYZE, BUFFERS)`. Checked against the installed `postgres:17.11-alpine3.24` before implementation and recorded in [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md).
- Alembic, the version pinned in `services/engine/uv.lock`, for the migration.

## 7. Data and trust-boundary changes

- One new table, `market_retention_cursor` (one row: a timestamp and a payload id), written only by the `SECURITY DEFINER` function; no grant to any role.
- Five new indexes on M3 tables. No column, row or rule of an M3 table changes.
- Fewer statements are run by the market identity's calls; its permissions do not change.
- The `COLLECTION_GAP` incident detail gains two fields. The API serves incident details as they are; the web shows only their code.

## 8. Implementation sequence

1. Migration `0017` with D1 and D2, and its downgrade; R1 to R7 and R9.
2. The cost measurement R8, compared with ExecPlan 0024 §4.3 and §4.4.
3. D3 in the worker; R10.
4. MARKET_DATA, TESTING, INTEGRATION_EVIDENCE, STATUS; this plan's progress.
5. PR with Verified, Not run and Before merging sections; an independent review of the migration.
6. The update to the PC: one double-click of `update-app.cmd` (backup, forward migration, recreated services, verification).
7. After the update, read-only on the PC: the next 24 hours of manifests (the slowest call of each pass), `RETENTION_FAILED` count, and the `slowest_call` of any feed drop.

## 9. Verification commands

PROPOSED, from `services/engine`: `uv run --frozen ruff check .`, `uv run --frozen python -m app.export_openapi --check`, `uv run --frozen python -m pytest -q` (database-free), and the database suite on a scratch PostgreSQL as [COMMANDS](../../COMMANDS.md) describes, with the new tests. Results are recorded in §12 when run; none is run yet.

## 10. Failure and rollback

- The migration runs in one transaction: if it fails, the update stops and the schema stays at `0016`.
- A wrong function is visible as `RETENTION_FAILED` with the new line numbers, or as a market table that grows past the hourly volume; the worker keeps collecting either way (ExecPlan 0024).
- Rollback: the downgrade to `0016` restores the `0004` function and drops what `0017` adds; it deletes no market data. It needs the owner's word in chat, like any command against the normal app.

## 11. Q01–Q10 (affected gates)

Affected: the market data and storage gates (R1 to R9 on a scratch database), the migration gate (R9), and the delivery gate (§8 steps 6 and 7). No money path, agent, UI or authority gate is affected: no ledger, order, fill, protection or permission changes.

## 12. Progress

- 2026-10-23 09:06 UTC: the owner asked for this plan.
- 2026-10-23: §2 observed read-only on the PC; plan PROPOSED.
- 2026-10-23 09:13 UTC: APPROVED by the owner ("Approve"); docs PR #111 merged as `0cff620`.
- 2026-10-23: IMPLEMENTED. Migration `0017_market_retention_cost` (D1, D2; the downgrade restores 0004's function text byte for byte); `app/db.py` accepts `0017`; D3 in `worker.py` (`timed`, `slowest_call`, the gap's two fields); `app.execution.fixtures.reset_state` reseeds the sweep's row; `tests/test_m2_retention_cost.py` (R1 to R6, R10); `tests/test_m2_retention_faults.py` names the new function's lines (observation delete 25, payload delete 49). The function also starts the sweep again if its row is missing (a test fixture's `TRUNCATE` found that case).

### 12.1 Where it was checked

The cloud recipe ([COMMANDS](../../COMMANDS.md)) on the owner's PC, isolated: Docker network `asl-t0038-net`, PostgreSQL `postgres:17.11-alpine3.24` (container `asl-t0038-pg`, 2 CPUs, 2 GiB, the normal app's limits) and a runner `python:3.13.11-slim-bookworm` (`asl-t0038-py`) holding a copy of `services/engine` with `uv sync --frozen` (uv 0.12.5), scratch secret files and `ASL_TEST_ISOLATED=1`, databases `asl_m1_*` only. Nothing reached the normal app, its database, `.env` or `secrets/`.

### 12.2 Results

| Check | Result |
|---|---|
| `ruff check --no-cache .`; `python -m app.export_openapi --check` | VERIFIED: `All checks passed!`; `FastAPI OpenAPI schema matches` |
| R1 to R7, R10 (`test_m2_retention_cost.py`, `test_m2_retention_faults.py`, `test_database.py`) | VERIFIED: `14 passed` on the final code |
| R9: `0016 → 0017 → 0016 → 0017` | VERIFIED: after the downgrade the function's `pg_get_functiondef` MD5 (`21afe5e4…`) and the public index list equal a database migrated by `main` to `0016`, and the cursor table is gone; both upgrades give the same function (`360838b6…`) and indexes |
| R8: cost, synthetic store of 2,401,700 payloads, 54,916 of them expired (1,700 kept for good), five calls each rolled back, PostgreSQL restarted before each set (its own buffers empty; the VM's file cache warm) | VERIFIED: the function of 0004 took 1,344 and 581 ms for the first call of a set and 410 to 450 ms after; 0017's took 336 and 293 ms for the first call and 239 to 285 ms after. Each call deleted 500 observations and 500 payloads. Per statement (`auto_explain`, warm): the payload search 7 ms over 700 primary-key lookups, the observation delete 234 ms and the payload delete 50 ms (their reference checks) |
| R8, a first version | OBSERVED and fixed before the results above: finding the sweep's last row with `ORDER BY … DESC LIMIT 1` over `id = ANY(…)` scanned the receipt-time index backwards (272 ms of a 576 ms call, 3,177 ms on a cold first call); the row now comes from the sweep's own query |
| Generic plans | VERIFIED: the ninth call of a session (when PL/pgSQL may use generic plans) keeps the index plans: the sweep an index-only scan of `market_payloads_retention` stopping at 200, the payload search one primary-key lookup and one `market_observations_payload` lookup per candidate (`auto_explain`) |
| The tests test the freed path | VERIFIED: with the function's `freed` replaced by an empty array, `test_a_deleted_observations_payload_goes_in_the_same_call…` fails; restored, all 7 pass |
| Full engine suite on a fresh database | VERIFIED: the known baseline, see below |

The engine suite (`pytest -q -rfE tests`) on this runner first failed in large numbers for its setup: scratch files the cloud recipe names were missing (`owner_setup_key`, `api_internal_key`, `agent_runner_key`, `research_bridge_db_password`) and the agent prompts must lie at `/services/agent-runner/prompts`. With both in place, the affected files gave `3 failed, 617 passed, 1 skipped, 74 errors`: the 74 errors and two failures are [COMMANDS](../../COMMANDS.md)' known baseline (`test_m1_account.py` and the research cluster; `test_api.py::test_status_requires_service_identity_and_ready_database`, `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`). The third, `test_m2_stream_continuity.py::test_back_to_back_rotations_under_load_keep_the_fence`, also fails on `main`'s code in this runner (2 of 2). `test_hourly_instrument_drift_is_adopted_without_rotation_or_unusable_quotes` failed 2 times in 21 runs on this change and 1 in 20 on `main`: flaky here, not this change.

VERIFIED on the final code (`db1f154`; the later commit changes two tests only, re-run alone: `7 passed`), on a fresh database with both in place: `3 failed, 1555 passed, 1 skipped, 74 errors` in 57 minutes. The 74 errors are the known 13 of `test_m1_account.py` and 61 of the research suites; the three failures are the two of `main`'s baseline and `test_back_to_back_rotations_under_load_keep_the_fence`, which fails on `main` in this runner too.

### 12.3 Installed on the PC

OBSERVED on 2026-10-23 through the update record and read-only queries (`BEGIN READ ONLY`) at 13:50 UTC:
- The owner's `update-app.cmd`, 12:52 to 13:12 UTC (record `update-20261023T130501Z`, `COMPLETE`): backup, `Migrated 0016_m10_three_coins -> 0017_market_retention_cost` at the first attempt, web, api, market-worker, execution-worker, evaluation-worker, agent-egress, agent-runner, agent-worker and source-fetcher recreated; verify: api ready, reconciliation OK, pages answer, the five feeds `CONNECTED`. An earlier run at 11:55 to 12:12 UTC installed `0cff620` (this plan's proposal only).
- The first pass under 0017 (the market worker's start-up pass, 13:08:58 UTC): 21 calls, 9,783 observations and 9,783 payloads, about 462 ms a call, the slowest 704 ms. The four passes before the update on the same day: 483 to 790 ms a call, the slowest 1,002 to 1,444 ms.
- The sweep passed every kept payload in that pass: its position stood at 2026-10-16 13:09 UTC, the newest expired payload; 9,005 payloads older than seven days remained, the hour's backlog and the kept ones.
- No market incident without a symbol (no `COLLECTION_GAP`, no `RETENTION_FAILED`) from 12:50 to 13:50 UTC.

- The second pass (14:09:10 to 14:09:20 UTC, read at 14:20): 22 calls, 10,553 observations and 10,425 payloads; the calls whose time the manifests show took 337 to 484 ms, except the second, 1,934 ms (the first call's time is not recorded). No market incident from 13:15 to 14:20 UTC. So the payload search no longer fails, but one early call of a pass can still come close to the two-second deadline: INFERRED from §12.2, the time is in the deletes' reference checks reading pages that are not in PostgreSQL's 128 MB of buffers, the `shared_buffers` question this plan left out (§4). ExecPlan 0039's BTC-only app would store about a fifth of today's rows if one coin's stream stays the size it is (INFERRED), which would shrink those reads; the passes are worth reading again after it.

NOT RUN: the 24 hours of passes of §8 step 7, and a `slowest_call` seen on a real feed drop (none happened yet). The project's next plan, [ExecPlan 0039](0039-bitcoin-futures-on-paper.md), rebuilds the app from a clean database; its next migration has to name `0017` as its parent (passed to that thread on 2026-10-23).

## 13. Decision log

- 2026-10-23: the sweep size of 200 a call and the window of 30 seconds for `slowest_call` are ordinary engineering choices, not owner decisions.
- 2026-10-23: `shared_buffers` is left out (§4); D3's records will show whether it is worth a decision.
- 2026-10-23, independent review (a separate agent reading the diff, no test run): nothing that deletes a referenced or young payload; the downgrade text equals 0004's; two callers serialize on the cursor row. Acted on: two tests claimed more than they checked (the own payloads lay inside the first sweep; the grant test read only `SELECT`), now fixed; generic plans checked (above). Accepted as they are: a pass ends at its first call that deletes nothing, so behind a run of kept payloads the sweep advances 200 a pass and the old function's leftover orphans go more slowly (storage only); a database clock that jumps more than seven days forward during a call could leave later invalid-frame payloads behind the sweep (storage only, never a wrong deletion); the downgrade's `DROP INDEX` may meet its 200 ms lock deadline under load and be retried.
