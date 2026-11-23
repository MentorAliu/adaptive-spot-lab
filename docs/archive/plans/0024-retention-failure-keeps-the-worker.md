# ExecPlan 0024 — A retention call the database ends does not end the market worker

**Status: IMPLEMENTED and VERIFIED in isolation on 2026-10-07; delivered as pull request [#31](https://github.com/MentorAliu/adaptive_spot_lab/pull/31), not merged yet; DEPLOYED to the normal app's market worker on 2026-10-07 at 21:22 UTC with the owner's approval (§13.1); the soak of two hourly retention passes passed, and the merge follows this record.** Owner request of 2026-10-07 ([DECISIONS](../../DECISIONS.md#2026-10-07--market-worker-a-retention-call-the-database-ends-must-not-end-the-worker-execplan-0024)): the normal market worker exited twice on 2026-10-06 because the statement timeout ended a call of its hourly retention; make that a failed maintenance pass instead of the end of the process, find out why one call can pass its deadline, and deliver a pull request that is neither merged nor deployed. Branch `claude/market-retention-timeout`, from `main` at `0f395a9`.

Labels: `OBSERVED` (seen in code or data), `INFERRED` (reasoned from observations), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

**The owner's constraints for this work.** No build, recreate, restart or stop of the normal `adaptive-spot-lab` project's market worker or of any pilot service without the owner's approval in chat. Isolated stacks only. No heavy Docker work between HH:58 and HH:07 UTC. `.env`, `secrets/` and `codex_home` are never read. Everything below about the normal app comes from one log extract the owner had approved before this work started (§2). Everything measured here comes from isolated runs with synthetic data.

## 1. Goal and observable outcome

1. **Reproduce** in an isolated test what happened on 2026-10-06: the database ends a retention call by its statement deadline, and the worker process ends. Separately, the same for the lock deadline.
2. **Keep the worker and its collection.** A retention call the database ends is a failed attempt of a maintenance pass. The socket, the generation, its epoch and the capture stay, and no collection gap is recorded.
3. **Record and retry.** Every failed attempt leaves a record, and the pass is tried again by itself.
4. **Keep the fence and the bound.** A lost lease still stops the worker. No hour has more than 32 calls of at most 500 observations and 500 payloads, under the unchanged two-second statement and one-second lock deadlines.
5. **A retention that stays behind stays visible,** as an incident that keeps being written, never silently.
6. **No other way for retention to end the process.** A rotation that meets a retention call still in flight waits for it.
7. **Explain the cost.** Say why one call of 500 observations can pass two seconds: what refers to the tables it deletes from, whether those references are indexed, and which deadline applies.
8. **Deployable beside the running pilot** by recreating `market-worker` alone: no schema change, and the execution worker's image and code identity stay as they are.

**Observable on the normal app after an approved deployment** (targets for the read-only check in §13):
- The market worker's restart count does not rise because of retention, and no `COLLECTION_GAP` has the failure `OperationalError` in phase `maintenance` with a `market_worker_fatal` after it.
- When the database ends a retention call again, there is one `RETENTION_FAILED` and, a minute or two later, one `RETENTION_RECOVERED`, on an unchanged collection.

## 2. What was observed on the normal app

Source: one owner-approved, read-only `docker logs --since 2026-10-06T13:40:00Z --until 2026-10-06T16:20:00Z adaptive-spot-lab-market-worker-1`, taken on 2026-10-07 by the session that works on ExecPlan 0023. Its extract (1,593 lines) lies in the primary checkout's ignored `.cache/m6/`; this plan read it there and ran nothing against the normal app. Times are UTC on 2026-10-06.

### 2.1 Two exits (OBSERVED)

Both tracebacks end the same way: `worker.run` → `consume` → `maintain_references` → `maintain` → `maintain_retention` → `store.prune_retention` → `SELECT asl_prune_market_evidence(…)` → `psycopg.errors.QueryCanceled: canceling statement due to statement timeout`. The database's context names the statement: `DELETE FROM market_payloads WHERE id = ANY(payload_ids)`, at `PL/pgSQL function asl_prune_market_evidence(uuid,bigint) line 39`, inside the reference check `SELECT 1 FROM ONLY "public"."market_payloads" x WHERE "id" … FOR KEY SHARE OF x`.

| | First exit | Second exit |
|---|---|---|
| Routine refresh ended (`market_references_checked`) | 13:51:53.716 | 15:53:52.563 |
| Last frame received before the exit | 13:51:55.136 | 15:53:54.143 |
| `market_collection_gap`, failure `OperationalError`, phase `maintenance` | 13:51:55.786 | 15:53:54.629 |
| Socket closed (2.0 s, timed out), then `market_worker_fatal` | 13:51:57.806 | 15:53:56.647 |
| New process holds the lease | 13:52:01.281 | 15:53:59.922 |
| Start-up retention done (`market_retention_pruned`) | 13:52:23.364, 21,547 records | 15:54:20.068, 21,426 records |
| Stream connected | 13:52:26.594 | 15:54:22.407 |
| From the last frame to the stream connected again | 31.5 s | 28.3 s |

- **It was the first call of the hourly pass both times.** The gap record comes 2.070 s and 2.066 s after the refresh ended, and the pass starts right after the refresh. That is the two-second statement deadline of the first call (INFERRED from the timing; the log does not mark single calls).
- **The same work succeeded half a minute later.** Each new process ran its start-up pass over the same rows and removed all of them.

### 2.2 Passes that completed (OBSERVED)

| Pass | From | To | Records | Calls (INFERRED: 500 + 500 a call, and one last call that removes nothing) | Time |
|---|---|---|---|---|---|
| Hourly, under the stream | 14:52:58.631 (refresh ended) | 14:53:09.011 | 21,330 | 23 | 10.4 s |
| Start-up, after the first exit | after 13:52:14.429 (last history answer) | 13:52:23.364 | 21,547 | 23 | at most 8.9 s |
| Start-up, after the second exit | after 15:54:08.931 | 15:54:20.068 | 21,426 | 23 | at most 11.1 s |

A call takes 0.3–0.5 s on average there. Two seconds for the first call is four to six times that.

### 2.3 Not part of this plan

The six other collection gaps of the extract have the failure code `stream_silent`: the provider's stream delivered nothing for ten seconds and the worker reconnected. That is a different matter.

### 2.4 Not known about the normal app

- How long single calls take, and whether the first call of a pass is always the slow one. The table `market_retention_manifests` has one row per deleting call with its transaction start time, so one read-only query would answer it (§7, decision 3).
- Whether an autovacuum, a checkpoint, a backup or other load ran at 13:51 and 15:53. At the first exit no isolated test stack existed on the host; at the second one was up and idle (the finding as handed over).
- How many rows `strategy_evaluations`, `orders` and `fills` hold (§4.5).

### 2.5 A third exit, while this plan was being verified (OBSERVED by the session of ExecPlan 0023)

The normal worker exited again on 2026-10-07 at about 20:01:25 UTC. The session that works on ExecPlan 0023 saw the restart in its pilot watch, read the worker's log once under the owner's approval of one read-only log read per restart, and told this session at about 20:13 and 20:20 UTC. Its extract (212 lines, without line times) lies in the primary checkout's ignored `.cache/m6/`; this plan read it there and ran nothing against the normal app.

- **The same failure.** `market_collection_gap` started at 20:01:23.956 and ended at 20:01:24.795, failure `OperationalError`, phase `maintenance`; the collection had begun at 14:47:41.686. The traceback is the one of §2.1, with the same context: `QueryCanceled`, `DELETE FROM market_payloads WHERE id = ANY(payload_ids)`, line 39. Then `market_worker_fatal`.
- **The restart, as that session read it from the container:** started 20:01:27.77, restart count 2 to 3. The start before it was 2026-10-06 15:53:57.83, so the worker did not exit between the second and the third time.
- **The same work succeeded at once.** The new process took the lease (epoch 2191), started its collection (epoch 2192), and its start-up pass removed 20,460 records.
- **Whether it was the first call of its pass** cannot be read from an extract without line times. The gap line follows a `market_references_checked` line directly, as in §2.1.
- **What ran on the host.** No test load of either session ran at that minute. That session's run had no container and issued no Docker command from 19:32:51 to 20:07:00. This plan's stacks ran nothing from 19:51:32 to 20:07:08; one idle test PostgreSQL was up. In the hour before, both had been busy: this plan's runs from 19:07 to 19:51 (the M3 and M4 test files, image builds, `WorkerFaults` three times, all on small test databases), that session's `Regression` from 19:14 to 19:31.
- **NOT KNOWN: whether such work on the same host contributes,** by pushing the normal database's rarely read pages out of the Docker VM's page cache before the next hourly pass. It would fit §4.4. Against it: by the restart count the passes of 15:00 to 19:01 completed, the first of them half an hour after this plan's 3 GB density load of 14:10–14:24.
- **When the hourly pass runs.** A pass is due an hour after the previous one completed and starts at the next routine refresh (§3), so its minute moves later every hour and starts again with every restart. Between the start of 2026-10-06 15:53:57 and the failed pass of 2026-10-07 20:01:23 lie 28 passes and 7 min 26 s more than 28 hours: about 16 s an hour (INFERRED by that session from these two instants; it agrees with the code). On 2026-10-07 the pass therefore ran within a minute or two of the full hour, inside the HH:58–HH:07 period that the owner keeps free of heavy Docker work. This plan had estimated HH:14–HH:20 from the intervals of §2.1 and paused its load once for it (COMMANDS); that estimate was wrong.

## 3. Current facts (OBSERVED in code at `0f395a9`)

**The pass.**
- `maintain_retention` runs at the end of every routine refresh (`worker.py:762`) and once at each process start before the stream opens (`worker.py:1091`). It does something when more than 3,600 s have passed since the last pass.
- One pass is up to 32 calls of `store.prune_retention`, back to back, on the worker's own maintenance thread and connection (`worker.py:765-778`; [ExecPlan 0021](0021-publication-cost-at-density.md), D6).
- `store.prune_retention` checks the fence, calls the function and checks the fence again, in one transaction (`store.py:650-659`).

**What an error in a call does.**
- Nothing catches it. It ends the maintenance task; the collection loop raises it again (`worker.py:986`); the teardown marks the feeds interrupted, records `COLLECTION_GAP` and closes the socket.
- `run()` lists the provider and network errors it recovers from. A database error is not among them, so it logs `market_worker_fatal` and the process ends (`worker.py:1118-1121`). Docker restarts the container.
- The start-up pass has the same path without a stream. A call that fails at every start would end every new process before it opens the stream (INFERRED; not observed, because the retry succeeded both times).

**The function** (`asl_prune_market_evidence`, replaced by migration `0004_m2_completion`; line numbers as PostgreSQL reports them):

| Line | Statement |
|---|---|
| 7 | Lock the lease row `FOR KEY SHARE` and check owner, epoch and expiry; otherwise `RAISE EXCEPTION 'market retention lease lost'` |
| 10 | Select the 500 oldest observations older than seven days that the rules allow to go |
| 23, 24 | Delete their publications, then the observations |
| 27 | Select up to 500 payloads older than seven days that no observation and no confirmation refers to |
| 39 | Delete those payloads |
| 43 | Write the manifest |

The call size is written into the function. The worker's identity has no `DELETE` on these tables and no setting that changes the 500.

**The deadlines.**
- The market identity's connections are opened with `statement_timeout=2000`, `lock_timeout=1000` and `idle_in_transaction_session_timeout=3000` (`app/db.py:28`). They are connection options. The role itself has no setting (§4.2).
- The statement the deadline measures is the whole `SELECT asl_prune_market_evidence(…)`: every statement of the function and every trigger they fire.
- The lock deadline applies to each lock wait separately (§9).

**Why two seconds is not simply raised.** Every fenced statement holds the lease row `FOR KEY SHARE` until its transaction ends, and so does a retention call. A new generation updates the lease's epoch, which must wait for those locks (migration 0004 made it so on purpose), under the control connection's one-second lock deadline. A retention call that is allowed to run longer would let a rotation or a restart of the collection meet that deadline and fail.

**A rotation can already meet it.** The stream's own writes are kept on one side of a generation change by two locks. Retention is not: its call runs on its own thread, and a rotation cancels the maintenance task without waiting for a call that is in flight (`worker.py:998-1001`). If that call still runs a second later, the epoch update fails with a lock timeout, which `run()` does not recover from either. Found by the independent review; REPRODUCED in isolation (§8).

**What is already visible.** `read.health()` reports `latest_retention_at` from the manifests, the storage size with a warning at 4 GiB, and the last 20 incidents. The Markets page shows the retention time. The worker stops collecting at 5 GiB.

**The contract.** [MARKET_DATA](../contracts/MARKET_DATA.md#implemented-m2-observation-boundary): at most 500 observations and 500 orphan payloads per call, up to 32 calls at start-up and hourly, worker statements and lock waits bounded. [ExecPlan 0003](0003-market-data-charts.md) records that M2 met the same deadline once before in its acceptance ("retention hit the existing two-second statement deadline while searching orphan payloads") and answered with indexes and the 500-row calls, not with a longer deadline.

## 4. Why one call can pass its deadline

Measured on the isolated run `ret-1007a`: PostgreSQL 17.11 in its default configuration with the normal app's limits (2 CPUs, 2 GiB), schema at head, 1.8 million published synthetic observations with one payload each, in production record shapes, the oldest 15,264 of them older than seven days. The statements were run as the database owner of that disposable database, without a deadline, so that their whole time shows. The evidence files are under `.cache/m2/ret-1007a/` in this worktree.

### 4.1 Which deadline (OBSERVED)

The statement deadline of two seconds, on the whole function call (§3). The lock deadline did not fire: the error of 2026-10-06 is `QueryCanceled` (SQLSTATE `57014`), not `LockNotAvailable` (`55P03`).

### 4.2 What refers to the tables a call deletes from (OBSERVED in the catalog)

| Deleted from | Referencing column | Index that starts with it | Rows there |
|---|---|---|---|
| `market_payloads` | `market_observations.payload_id` | `market_observations_payload` | 1.8 million |
| `market_payloads` | `market_candle_confirmations.payload_id` | `market_confirmations_payload` | few |
| `market_observations` | `market_publications.observation_id` | its unique index | 1.8 million |
| `market_observations` | `market_observations.instrument_id` | `market_observations_instrument` (partial) | 1.8 million |
| `market_observations` | `market_evidence_pins.observation_id` | its primary key | few |
| `market_observations` | `market_candle_confirmations.observation_id` | `market_confirmations_observation` | few |
| `market_observations` | `market_feed_state.instrument_id` | none | 2 |
| `market_observations` | `strategy_evaluations.bar_observation_id` | **none** | grows with the pilot |
| `market_observations` | `orders.decision_quote_observation_id` | **none** | grows with trades |
| `market_observations` | `orders.instrument_observation_id` | **none** | grows with trades |
| `market_observations` | `fills.quote_observation_id` | **none** | grows with trades |
| `market_observations` | `fills.instrument_observation_id` | **none** | grows with trades |

- **Both references to `market_payloads` are indexed.** The statement the deadline ended on 2026-10-06 is therefore not slow because of a missing index on them.
- **Five references to `market_observations` come from M3 tables and have no index** (migration `0005_m3_paper_broker`). Nothing refers to `market_publications`.
- All twelve are `NO ACTION` references, so every deleted row is checked against each of them after the delete.
- The role `asl_market_worker` has no setting of its own (`rolconfig` is empty). `jit` is on, with PostgreSQL's default thresholds.

### 4.3 Where the time of one call goes (OBSERVED)

One call that removes 500 observations and 500 payloads, repeated on the same rows with every page already in PostgreSQL's buffers: **357 ms**. Four committed calls after it took 328–449 ms.

| Part | Time | Of which reference checks |
|---|---|---|
| Delete 500 observations (line 24) | 246 ms | 243 ms: ten references, 15–55 ms each |
| Select the payloads (line 27) | 53 ms | — (15 ms of it is compiling the statement, §4.6) |
| Delete 500 payloads (line 39) | 49 ms | 47 ms: two references |
| Select the observations, delete the publications, the manifest | under 10 ms | — |

- **About three quarters of a call are reference checks:** twelve references, 500 rows each, 30 to 110 microseconds a check. The check of a reference costs that much even when its table is empty: the five M3 references together cost about 80 ms a call with empty tables.
- This is the 300–400 ms that [ExecPlan 0021 §4.6](0021-publication-cost-at-density.md#46-a-second-cost-in-the-same-path-retention-under-the-stream-observed) measured and attributed to "per-row triggers and foreign-key checks".

### 4.4 What the first call of a pass adds (OBSERVED in isolation; INFERRED for the normal app)

The same call as the first statement after the database was restarted, so that PostgreSQL's own buffers were empty: **576 ms**, and it read **11,182 pages (87 MB)** from outside those buffers. The repeated call read 2.

| Statement | Pages read from outside PostgreSQL's buffers |
|---|---|
| Select the payloads (line 27) | 9,384 |
| Delete the publications | 540 |
| Delete the observations | 537 |
| Delete the payloads | 530 |

- **The payload selection reads every expired payload, not 500.** It looks for payloads older than seven days that no observation refers to. It found its 500 and still examined all 15,022 expired payloads, each with one lookup in the index on `market_observations.payload_id`. Payload identities are random, so those lookups touched 7,941 of that index's 9,017 pages.
  - With the plan PostgreSQL chose here, the selection sorts within equal receipt times and cannot stop before it has seen the row after its 500th, which does not exist. It chooses that plan when it expects fewer than 500 results.
  - With the other plan it chooses, an ordered index scan, the selection stops at the 500th orphan only if each of the call's 500 observations had a payload of its own. A stream batch with two frames of one symbol and kind stores one payload for two observations. Whether the normal app has such payloads among its expired rows was not read (§7, decision 3).
- **Its cost follows the backlog, not the call size.** Run alone with nothing to find, the selection examined 15,334 payloads in 573 ms on empty buffers. With the horizon moved so that more payloads lie past it, and with warm buffers: 80,136 payloads (about 7 hours) in 575 ms, 144,936 (13 hours) in 449 ms, 274,540 (25 hours) in 685 ms. The first of those includes 280 ms of compiling (§4.6).
- **On this host these 11,182 pages came from the operating system's cache within 0.22 s.** The first call has about 1.6 s left under its deadline for them, which is about 150 microseconds a page.
- **INFERRED for 2026-10-06:** the first call of an hourly pass is the call that touches the hour's expired rows and almost the whole payload index for the first time. When those pages are not cached, or the disk is busy, their reads take more than the 1.6 s that are left. The failed call leaves the pages cached, which is why the same call succeeded half a minute later. Nothing was measured on the normal app to confirm this; it fits both the timing in §2.1 and the half-minute recovery.

### 4.5 What grows (OBSERVED in isolation with synthetic rows; INFERRED for the normal app)

- **The unindexed M3 references.** Each of a call's 500 deleted observations is looked up in `strategy_evaluations` by a scan of the whole table. With synthetic rows of about 700 bytes:

  | Rows in `strategy_evaluations` | That reference's check, per call | Whole call, warm |
  |---|---|---|
  | 0 | 15 ms | 328–445 ms |
  | 350 (about seven days of two rows an hour) | 29 ms | 336 ms |
  | 2,700 (the pilot at its checkpoint of 2026-11-25) | 119 ms | 429–461 ms |
  | 17,500 (a year) | 691–889 ms | 1,025–1,265 ms |

  That is 0.04–0.05 ms per stored row and call. At that rate the call alone reaches two seconds somewhere between 30,000 and 45,000 rows. `orders` and `fills` grow with trades and behave the same. The real rows' size and number were not read.
- **The backlog after downtime.** After the PC was off for a day, 25 hours of payloads lie past the horizon, and every call examines all of them (§4.4): 0.7 s warm on top of the deletes, and their pages on the first call.
- **Payloads that stay.** The selection starts at the oldest payload each time. Payloads older than seven days that keep an observation (instrument snapshots, finalized candles) are examined again in every call, and their number only grows. The normal app is nine days old, so this is small today. Not measured.

### 4.6 Compiling the statements (OBSERVED)

PostgreSQL compiles a statement with LLVM when its estimated cost passes 100,000, and optimizes it harder past 500,000. The payload selection's estimate was 131,245 for 15,000 expired payloads: 15–18 ms of compiling in every call. With an estimate past 500,000 a single execution spent 67–280 ms compiling. The estimate depends on table statistics that are refreshed only after a tenth of a table has changed. The research and source identities of M6 turn compiling off for the same reason; the market identity does not.

### 4.7 What follows for a smaller batch

A call of fewer rows makes the deletes and their reference checks cheaper in proportion: about 0.6 ms a row. It does not change the payload selection, which examines the whole backlog whatever the call size, and it does not change which pages the first call of a pass reads. **A smaller batch alone would not have prevented the two exits** if §4.4's inference holds.

## 5. Scope and exclusions

**In scope:** the retention path of the market worker (`worker.py`), the lease refusal of the retention call (`store.py`), their tests, a fault option for the density workload, the contract text, and a deployment proposal for the running pilot.

**Excluded:**
- **Any schema change:** the retention function, its call size, an index. §7 puts them to the owner.
- The statement, lock and idle deadlines of the market identity, and PostgreSQL's configuration.
- The retention rules: seven days, 730 days, pins, confirmations, instrument snapshots, manifests.
- Every other database error in the worker. A failed stream write still ends the collection and the process, as designed in M2.
- `stream_silent`, the overload policy, the clock and REST behaviour of ExecPlans 0012, 0021 and 0022.
- The API, the web app, `read.py`, everything under `app/execution/`, and both pilot workers.
- Normal deployment, until the owner approved it on 2026-10-07 (§13.1).

## 6. Design (IMPLEMENTED)

The principle is the one ExecPlans 0012 and 0022 applied to instrument and clock checks: **routine work that fails on a healthy collection fails by itself.** Retention is housekeeping. The stream does not depend on it within an hour or a day.

**D1 — A call the database ends is a failed attempt.**
- `maintain_retention` catches a database error of a call (`sqlalchemy.exc.DBAPIError`: statement deadline, lock deadline, a violated reference, a lost connection, any other error the database or its driver reports). The attempt ends there.
- PostgreSQL has rolled the failed call back. The calls before it in the same attempt are committed, as they always were: each call is its own transaction.
- Nothing else is touched: no feed status, no generation, no socket. The maintenance task returns to its loop.
- An error that is not a database error is not caught and still ends the process: the M2 rule that unexpected failures are visible stays.

**D2 — A lost lease still stops the worker.**
- `LostLease` from either fence check passes through `maintain_retention` unchanged.
- The function's own refusal (`market retention lease lost`, SQLSTATE `P0001`) can come when the lease ends between the caller's check and the function's. `store.prune_retention` now raises it as `LostLease`. Before, it was an unexpected error, which also ended the process; as a failed attempt it would have been misread.

**D3 — Retry.**
- After a failed attempt the pass is due again 60 s later. Retention runs inside the routine refresh, which comes every 45 s, so the retry happens at the first refresh at least 60 s later.
- **Only an attempt that completed no call lengthens the wait:** 60, 120, 240, 480, 960, 1,920 s, then the normal 3,600 s. An attempt that completed at least one call before it failed shows that the database can do this work, and the pass is tried again after 60 s. Otherwise occasional failures in the middle of a pass would slow retention down to one short attempt an hour.
- A completed pass sets the normal schedule again: the next pass an hour later.
- The state (retry time, counts of failed attempts, when they began) lives on the worker, not in the maintenance task, which is cancelled around every rotation.
- The retry time is set before anything is awaited.

**D4 — The bound.**
- No hour has more than 32 calls, failed ones included: the worker keeps the time of every call of the last 3,600 s and sends none while there are 32.
- A retry uses the calls that are left. With none left it waits until the oldest call is an hour old, and its record says that wait, not 60 s.
- A call counts when it is sent: after a cancellation for a rotation it still runs to its end on its thread.
- A pass without a failure is as before: up to 32 calls back to back, and the next pass an hour after it completed, when all of them are more than an hour old.
- The call size and both deadlines are unchanged, so the time for which a call holds the lease row is bounded as before.

**D5 — Start-up.** The pass before the stream opens follows D1: a failed call lets the stream start, and the pass is tried again under the stream. A start-up pass can therefore no longer keep a process from collecting.

**D6 — Evidence.**
- **Every failed attempt is one incident and one log event.** `RETENTION_FAILED` with: the error class; the SQLSTATE; `where`, the outermost frame of the database's own context (the function and its line; never a parameter or a row); the phase (`startup` or `maintenance`); the calls and records the attempt completed; the number of failed attempts; when they began; the wait; the collection.
- **Stalled.** Once no call has completed for three hours, the code of every further failed attempt is `RETENTION_STALLED`. With the waits of D3 that is the ninth attempt in a row that completed nothing, and then one an hour. A retention that removes nothing therefore stays among the newest incidents that the health read shows. A retention that keeps failing after some calls is behind, not stalled: its records stay `RETENTION_FAILED` and show the calls each attempt completed.
- **Recovered.** The first pass that completes after failed attempts writes `RETENTION_RECOVERED` with their start, their end and their count.
- **The log.** `market_retention_failed` (with `stalled`), `market_retention_recovered`, and the existing `market_retention_pruned`, now also for the records a failed attempt removed before its failed call.
- **Retention's records use its own database thread,** like its calls. Nothing of a failed retention goes through the stream writer's thread.
- A record that cannot be written is logged (`market_retention_record_failed`) and fails nothing; only a lost lease does. The log line is written before the record.
- No new table or column. Incident codes are free text in the schema, the API and the web app.

**D7 — A new generation waits for a retention call that is still running.**
- The worker keeps the call it has sent. A cancelled maintenance task leaves that call running; the call is no longer anybody's attempt, and its result is dropped.
- Before a generation is registered or begun, the worker waits for such a call to end, for at most three seconds. The call ends by itself within its two-second statement deadline.
- A rotation that falls into a slow retention call therefore starts up to two seconds later. The current generation keeps publishing meanwhile, as it does during the rest of a rotation.
- The same wait runs before the process releases its lease at the end, so that a call in flight ends under the lease it was sent with.

**What does not change.** The function and every rule in it. The call size. The statement, lock and idle deadlines. The fence. When a pass is due without a failure. The retention thread. Stream capture, publication, rotation, the clock and REST behaviour. `read.py` and the API.

**Considered and not chosen.**
- *A longer deadline for retention calls.* §3: a call holds the lease row shared, and a generation change waits for it under a one-second lock deadline.
- *Retrying at once.* The failed call has warmed the cache, so it would probably work. If the cause is a lock or real overload it doubles the load at the worst moment. A minute costs nothing: retention is hours ahead of the storage limit.
- *A read by the worker that only warms the cache before a pass.* It would write the function's access pattern a second time into the worker, and the selection would still examine the backlog in every call.
- *Turning compiling off for the retention transaction* (`SET LOCAL jit = off`). Measured on the same warm call, six times each way: 264–375 ms with compiling (median about 285 ms) and 251–352 ms without (median about 265 ms). The difference is inside the spread of single calls and does not decide whether a call meets its deadline. It belongs with the function's rewrite, if that is planned (§7).
- *Making a database error anywhere in the maintenance path non-fatal.* History, confirmations and reference writes are the stream's own data; their failure rules are M2's and were not asked about.
- *A status column or a health field for a stalled retention.* It needs a schema or API change and a web deployment. The incident and the retention time already shown reach the owner without either.
- *Counting failed attempts across restarts from the incident table.* The incidents of the earlier process stay; a restarted worker starts at one.

## 7. Decisions for the owner

Nothing below is implemented or run. Each item names what was measured for it.

1. **The smaller batch, and the function's payload selection (a schema change).** The instruction asks for a retry "with a smaller batch". The function fixes its call size, and the worker's identity can change nothing about it, so this needs a new function signature in a migration.
   - **What the measurement says (§4.7):** a smaller call shortens the deletes, and does nothing about the selection that examines the whole backlog or about the pages the first call reads.
   - **(a) Recommended: plan both in one migration of its own.** The function takes its call size as an argument (the two-argument form stays for the worker that runs today), and it looks for orphan payloads among the payloads of the observations it has just deleted instead of among all expired payloads. That removes 9,384 of the first call's 11,182 page reads and 50–145 ms of every call in the isolated measurement, and makes the cost independent of the backlog. It is its own ExecPlan and pull request, with the migration rehearsal that a change beside the pilot needs. Note for its planning: migration 0008 (M6) is on `main` and not applied to the normal app, so a new migration can reach the normal app only with or after M6's.
   - (b) Only the call-size argument.
   - (c) Neither now: this plan's retry is what completed the pass on 2026-10-06, half a minute after each failure.
2. **Indexes on the five M3 reference columns (a schema change on M1–M4 tables).** `strategy_evaluations.bar_observation_id`, `orders.decision_quote_observation_id`, `orders.instrument_observation_id`, `fills.quote_observation_id`, `fills.instrument_observation_id`. Without them a retention call scans those tables once per deleted observation (§4.5): 15 ms at 0 rows, 119 ms at 2,700, 0.7–0.9 s at 17,500 in the isolated measurement. By the rule the task text cites, an index on an M1–M4 table goes into its own migration and pull request. **Recommended: yes, in the same migration as decision 1 or in one of its own, as the owner prefers.** It is not what failed on 2026-10-06.
3. **Read-only reads of the normal app (optional).** They would replace inferences with observations and send nothing anywhere. Two queries in one `BEGIN TRANSACTION READ ONLY` with a statement deadline, as for ExecPlans 0021 and 0022, and one read of the worker itself:
   - the time between the manifests of each pass since 2026-10-05, which is the duration of every deleting call, and shows whether the first call of a pass is the slow one (§2.4);
   - the row counts of `strategy_evaluations`, `orders` and `fills`, the last autovacuum and analyze times of the three market tables, and how many expired payloads carry more than one observation (§4.4, §4.5);
   - the retention lines of the market worker's log for the hours of 2026-10-07 in which this plan's isolated loads ran (one `docker logs` call): whether the passes after those loads took longer than the others (§2.5).
4. **Deployment.** Recreating `market-worker` beside the running pilot needs explicit approval in chat (§13). Until then the normal worker keeps the behaviour of §2: a retention call the database ends restarts it, at a cost of about 30 s of quotes. It has done so three times in two days, the third time while this plan was being verified (§2.5). **Approved by the owner on 2026-10-07 at about 21:00 UTC and executed (§13.1).**

Not asked of the owner: the 60-second retry, its doubling, the three hours and the handling of the lease refusal are ordinary, reversible engineering choices. They are recorded in §17.

## 8. Requirements and tests (IMPLEMENTED; results in §12)

| # | Requirement | Evidence |
|---|---|---|
| R1 | A retention call ended by the statement deadline keeps the socket, the generation, the epoch and the capture. No `COLLECTION_GAP`. Quotes stay usable throughout. | W1 `statement`, sampled every 50 ms |
| R2 | The same for the lock deadline, with the worker's own connection settings. | W1 `lock` |
| R3 | The failed call's deletes are rolled back; the retry removes the rows. | W1, W2 |
| R4 | A failed call in the start-up pass does not end the process and does not keep the stream from opening. | W2 |
| R5 | A lost lease in the retention path is raised and is not a failed attempt. The function's own refusal is a lost lease. | W3, W4, U6 |
| R6 | Any database error is a failed attempt. An error that is not a database error is raised as before. | U2, U6 |
| R7 | The retry waits 60 s after a failed attempt, and nothing is tried before it. The wait doubles to the normal hour only while attempts complete no call. | U1, U3, U9, W1 |
| R8 | No hour has more than 32 calls. A retry gets what is left, a failed call counts, and so does a call that was cancelled. A retry without a call left waits for one, and its record says so. | U4, U5 |
| R9 | Every failed attempt is recorded with class, SQLSTATE, function line, phase, calls, records, count and wait. Once no call has completed for three hours the code is `RETENTION_STALLED`. One record closes the failures. | U1, U3, U8, U9, W1, W2 |
| R10 | Retention's calls and records run on its own database thread, never the stream writer's. | W1 |
| R11 | A record that cannot be written fails nothing; a lost lease while recording is raised. | U7 |
| R12 | Without a failure, retention, start-up, rotation, publication and every earlier fault behave as before. | `WorkerFaults` and the test files of M0 to M4 (§12.1) |
| R13 | At 1.8 million stored observations and under the stream, two attempts whose first call the database ends are followed by an attempt that removes at least 10,000 observations, on one collection, inside the publication budgets. | `PerformanceDensity -RetentionFaults` |
| R14 | No file under `app/execution/`, no `read.py`, no migration and no API or web file changes. | The diff |
| R15 | A rotation asked for while a retention call still runs registers its generation only after that call has ended, and completes without a gap. The wait is bounded. | W5, U5 |
| R16 | A stopping worker leaves its pass due and records nothing false. | U10 |

**Worker tests on the real loopback path** (`tests/test_m2_retention_faults.py`, in `WorkerFaults`; 5 tests, 6 cases). Each first removes what earlier tests left expired and then inserts its own expired fixture quotes, so its rows are the ones the retention rule takes.
- W1 `test_a_retention_call_the_database_ends_keeps_the_worker_and_its_collection`, two cases.
  - `statement`: another transaction holds one expired payload `FOR KEY SHARE`. The retention call runs with a statement deadline that ends its wait, so the database cancels the function in its payload delete: SQLSTATE `57014` at line 39, the statement and line of 2026-10-06. The worker's own connections would end that wait by their lock deadline first, which is why this one call uses a connection without one.
  - `lock`: the same lock on an expired observation, with the worker's own settings. The lock deadline ends the call in its observation delete: `55P03` at line 24. A pin that is being written holds this lock.
- W2 `test_a_failed_start_up_retention_does_not_keep_the_stream_from_starting`, through `MarketWorker.run()`.
- W3 `test_a_lost_lease_in_retention_is_raised_and_is_not_a_failed_attempt`.
- W4 `test_the_retention_function_refusing_the_lease_is_a_lost_lease`.
- W5 `test_a_rotation_waits_for_a_retention_call_that_is_still_running`: a held payload keeps one retention call inside the function for 2.5 s; a rotation is asked for 0.2 s after the call began.

**Without a database** (`tests/test_m2_unit.py`, 10 new tests, 13 cases), on a clock the test moves:
- U1 `test_a_database_failure_ends_the_retention_attempt_and_nothing_else`
- U2 `test_any_database_error_in_retention_is_a_failed_attempt` (a violated reference, a refused permission, no connection)
- U3 `test_failed_retention_attempts_back_off_to_the_normal_period_and_then_read_as_stalled`
- U4 `test_no_hour_has_more_than_the_declared_retention_calls` (also six simulated hours of refreshes with failures spread over the first)
- U5 `test_a_new_generation_waits_for_a_retention_call_its_cancelled_task_left_running` (the call completes, or fails; and a call that never ends is not waited for without a bound)
- U6 `test_a_lost_lease_or_an_unexpected_error_in_retention_is_raised_as_before`
- U7 `test_a_retention_record_that_cannot_be_written_fails_nothing`
- U8 `test_database_failure_reports_class_sqlstate_and_function_line_only`
- U9 `test_an_attempt_that_completed_a_call_does_not_lengthen_the_wait` (also four simulated hours in which every attempt completes a call and fails: never stalled, never more than 32 calls an hour)
- U10 `test_a_stopping_worker_leaves_its_retention_pass_due`

**Reproduced on the unchanged code** (run `ret-1007a`, isolated, synthetic; the unchanged `worker.py` and `store.py` of `0f395a9` mounted over the built image, and the test file with the new constants written as numbers). The selection was W1, W2 and W5 (`-k "database_ends or start_up or rotation_waits"`); in its final form, at 19:26 UTC, all four cases failed. W3 and W4 were not run on the unchanged code.
- W1 `statement`: `MarketWorker.consume()` ended with `OperationalError (psycopg.errors.QueryCanceled) canceling statement due to statement timeout … SQL statement "DELETE FROM market_payloads WHERE id = ANY(payload_ids)" PL/pgSQL function asl_prune_market_evidence(uuid,bigint) line 39 at SQL statement`.
- W1 `lock`: it ended with `OperationalError (psycopg.errors.LockNotAvailable) canceling statement due to lock timeout … line 24`.
- W2: `MarketWorker.run()` ended with the same error and the stream never opened.
- W5: the rotation's registration ended the worker with `OperationalError (psycopg.errors.LockNotAvailable) canceling statement due to lock timeout … while updating tuple (0,23) in relation "market_lease"`. The retention call that the cancelled maintenance task had left running still held the lease row shared.

**Two older tests that failed by timing (OBSERVED; corrected here).** Both are tests of ExecPlan 0022 in `tests/test_m2_reference_checks.py`, and both failed on the unchanged worker as well.
- `test_imprecise_routine_clock_check_keeps_the_collection_and_fails_closed` failed in the first full pass of `WorkerFaults`. Run alone six times each, it failed once on the unchanged worker and twice on the changed one. Its last sample assertion required that no sample before the second recheck is usable, while its sampler starts before the failed check: a sampling round that finishes before the worker notices the due refresh, which takes up to a quarter of a second, is rightly usable. The assertion three lines above it already states the property for the samples after the close. The contradictory line is removed; the corrected test passed eight of eight runs. It asserts nothing less about the worker.
- `test_nothing_re_opens_a_feed_while_the_clock_is_unverified` failed in a later pass. Run alone eight times each on the database of run `ret-1007a`, it failed three times on the changed worker and three times on the unchanged one. One of its assertions read the provider's count of instrument calls at one instant, right after the clock check that triggers them, before the worker can have made them. It now waits for that count (`eventually`, 10 s) and asserts the same thing.
- **Not explained.** Of those six failures, two were that assertion and four were a time-out while the test waited for the worker (in `step` and in `eventually(all_valid)`): two on the changed worker and two on the unchanged one. The database of `ret-1007a` had been used for hours by then (at 19:42 UTC: 26,497 observations, none expired, 12 manifests). On the fresh database of run `ret-1007d` the corrected test passed twelve of twelve runs, and the whole phase passed there and on the final run (§12). The cause of the time-outs is NOT KNOWN: the uncorrected test was not run on a fresh database, and the time-outs were not looked into further.

## 9. Official sources and versions

Read on 2026-10-07 through the authoring client's web fetch, which returns extracts of a page.

| Source | What it says | Used for |
|---|---|---|
| PostgreSQL 17, [Client Connection Defaults](https://www.postgresql.org/docs/17/runtime-config-client.html) | `statement_timeout`: "Abort any statement that takes more than the specified amount of time." "The timeout is measured from the time a command arrives at the server until it is completed by the server." `lock_timeout`: "Abort any statement that waits longer than the specified amount of time while attempting to acquire a lock on a table, index, row, or other database object. The time limit applies separately to each lock acquisition attempt." "Unlike `statement_timeout`, this timeout can only occur while waiting for locks." | §3, §4.1, W1 |
| PostgreSQL 17, [Constraints, foreign keys](https://www.postgresql.org/docs/17/ddl-constraints.html) | "Since a `DELETE` of a row from the referenced table or an `UPDATE` of a referenced column will require a scan of the referencing table for rows matching the old value, it is often a good idea to index the referencing columns too." | §4.2, §4.5, decision 2 |
| PostgreSQL 17, [Error Codes](https://www.postgresql.org/docs/17/errcodes-appendix.html) | `57014` `query_canceled`, `55P03` `lock_not_available`, `P0001` `raise_exception`, `23503` `foreign_key_violation`. | D1, D2, D6 |
| psycopg 3, [errors](https://www.psycopg.org/psycopg3/docs/api/errors.html) | `Error.sqlstate`: "The code of the error, if received from the server." `Error.diag`: a `Diagnostic` object whose attributes, `context` among them, are the server's error fields. `QueryCanceled` and `LockNotAvailable` are `OperationalError`; `RaiseException` is `ProgrammingError`; `ForeignKeyViolation` is `IntegrityError`. | D1, D2, D6 |
| SQLAlchemy 2.0, [Core Exceptions](https://docs.sqlalchemy.org/en/20/core/exceptions.html) | `DBAPIError` "Wraps exceptions raised by the DB-API underlying the database operation", with the original in `orig`. `OperationalError`, `IntegrityError`, `ProgrammingError` and `InternalError` derive from `DatabaseError`, which derives from `DBAPIError`; `InterfaceError` derives from `DBAPIError`. `TimeoutError`, the pool's, is not a `DBAPIError`. | D1 |

Checked on the installed stack, not taken from the pages: the SQLSTATE and the context of both deadlines (W1); that the function's refusal arrives as `P0001` (W4); the line numbers PostgreSQL reports for the function (W1 and the log of 2026-10-06 agree on line 39); the plans and page counts of §4 (`EXPLAIN (ANALYZE, BUFFERS)` and `auto_explain` with nested statements and triggers).

Versions: PostgreSQL 17.11 (`postgres:17.11-alpine3.24`), SQLAlchemy 2.0.54 and psycopg 3.3.6 (`services/engine/uv.lock`). **No new dependency, no version change.**

## 10. Data and trust-boundary changes

- **No schema change, no new grant, role, destination or credential.** The worker calls the same function with the same identity.
- **New evidence rows.** Incident codes `RETENTION_FAILED`, `RETENTION_STALLED` and `RETENTION_RECOVERED`, written through the existing fenced insert. Their detail holds an error class, a SQLSTATE, a function name with a line number, counts and times. It holds no statement parameter and no row value: the engine hides parameters, and only the outermost frame of the database's context is kept.
- **What is deleted and when** follows the same rules. After a failed attempt the remaining rows are deleted a minute or more later than they would have been.
- **Logs.** Three new events with the same fields. The worker has no secret.
- **Fixtures.** The new tests insert expired synthetic quotes as the database owner of a disposable test database and use the loopback provider. The density option changes no stored data.

## 11. Implementation sequence

- **B0 — Reproduction. DONE.** W1, W2 and W5 failed on the unchanged code (§8).
- **B1 — Worker and store. IMPLEMENTED.** D1–D7.
- **B2 — Tests and harness. IMPLEMENTED.** W1–W5, U1–U10; the new file in `WorkerFaults`; `-RetentionFaults` for the density workload, which also times retention's own thread now.
- **B3 — Cost measurement. DONE** (§4).
- **B4 — Contracts. DONE.** MARKET_DATA, OPERATIONS, TESTING, INTEGRATION_EVIDENCE, COMMANDS, STATUS, DECISIONS and the docs index.
- **B5 — Independent review and isolated acceptance on the final source. DONE.** The review and its corrections are in §12.3, the acceptance of the committed source in §12.1.
- **B6 — Pull request. DONE:** [MentorAliu/adaptive_spot_lab#31](https://github.com/MentorAliu/adaptive_spot_lab/pull/31), opened with `gh pr create` from branch `claude/market-retention-timeout` at 20:52 UTC on 2026-10-07, neither merged nor deployed at that point. This task's Docker resources were removed first (COMMANDS).
- **B7 — Normal deployment. DONE 2026-10-07, 21:20–21:22 UTC,** on the owner's approval (§13.1). The soak passed at 23:27 UTC; the merge follows this record.

## 12. Verification (isolated)

Everything here ran on isolated Compose projects (`asl-m2-ret-1007a-*`, `asl-m2-ret-1007d-*`, `asl-m2-ret-1007b-*`) with synthetic data and the loopback provider, on Docker Desktop 29.8.1 (16 CPUs, 7.7 GiB) under Windows. Commands and evidence files are in [COMMANDS](../COMMANDS.md#execplan-0024-commands--2026-10-07). No command was addressed to the normal app; one unfiltered `docker stats` listing at 14:05 UTC showed its containers' resource figures, which COMMANDS records.

### 12.1 Acceptance on the committed source (VERIFIED)

Run `ret-1007b`, code commit `9c7c87d3eb2726ec0165ac2203d76de72fc2db2e`, fresh databases, 2026-10-07 19:46–20:50 UTC. Every step exited 0.

| Step | Result |
|---|---|
| `Snapshot`, before and after | Both record commit `9c7c87d3eb2726ec0165ac2203d76de72fc2db2e` and the same 540 source hashes |
| `WorkerFaults` | 75 passed in 181.72 s, none skipped: the 69 cases before this plan and the 6 of `tests/test_m2_retention_faults.py` (W1–W5) |
| Ruff | `All checks passed!` |
| OpenAPI check | `FastAPI OpenAPI schema matches` |
| The M0–M2 test files outside `WorkerFaults` | 76 passed, one pre-existing Starlette deprecation warning; 48 of them `tests/test_m2_unit.py`, 13 of those new (U1–U10) |
| `RecoveryMemory` | 30 measured recoveries, 444 KiB settled RSS growth, 0 retained market tasks |
| `PerformanceDensity -RetentionFaults`, 1.8 million stored observations, 600 s | No budget failure. 1,780 of 1,780 frames published; receipt to publication p50 114.1 ms, p95 118.9 ms, p99 122.9 ms, maximum 143.3 ms; 593 of 593 samples usable; one collection and no gap. The database ended the first call of two attempts (`57014` in the observation delete, line 24; waits 60 s and 120 s). The third attempt completed the pass with 30 calls that removed 14,746 observations and 14,746 payloads, and `RETENTION_RECOVERED` closed the failures 3 min 56 s after the first. No other incident. A retention call on its own thread took 329 ms at the median and 646 ms at most (32 calls). |
| The M3 and M4 test files | 169 passed in 1,094.28 s, with the same one warning |
| `PerformanceBurst` | 30,000 of 30,000 frames published; receipt to publication p50 139.9 ms, p95 164.4 ms, p99 173.4 ms; schedule lag p99 2.0 ms; maximum RSS 73,264 KiB |

### 12.2 Before the commit (OBSERVED; development runs `ret-1007a` and `ret-1007d`)

- **Reproduction on the unchanged code:** §8. Four cases failed with the database's error; the same cases pass on the change.
- **The cost measurement:** §4.
- **A first density run with retention faults,** 14:27–14:37 UTC, on the first form of the change (before the corrections of §12.3) and on the database the cost probes had used: no budget failure; 1,791 of 1,791 frames published; receipt to publication p50 113.6 ms, p95 118.2 ms, p99 121.5 ms, maximum 128.8 ms; 597 of 597 samples usable; one collection. The only incidents were two `RETENTION_FAILED` (`57014`, waits 60 s and 120 s) and one `RETENTION_RECOVERED` after 30 calls that removed 14,926 observations and 14,926 payloads, 3 min 56 s after the first failure. A retention call under the stream took 334 ms at the median and 531 ms at most.
- **A trial of the regression lists** (19:07–19:25 UTC) passed, 73 and 169 tests, but `worker.py` and the unit tests changed after it started. It is not evidence for the commit; §12.1 is.
- **A fresh database at the final source** (`ret-1007d`, 19:38–19:43 UTC): `WorkerFaults` 75 passed, and the second corrected older test twelve of twelve.

### 12.3 Independent review

One read-only review by a separate agent of the authoring client, started at 18:52 UTC. It was given the worktree, the purpose of the change and what to look for, and it read the diff against `origin/main` itself. A first attempt at 14:31 UTC was stopped unfinished. Its findings and what was done:

| Finding | Disposition |
|---|---|
| A rotation that meets a retention call still in flight fails on the lease row under its lock deadline and ends the worker. | Reproduced on the unchanged worker (W5). Corrected: D7. |
| The wait doubled after every failed attempt, also when attempts completed calls. | Corrected: D3, U9. |
| The bound of 32 calls held per hour that began with an attempt, not in any hour. | Corrected: D4, U4. |
| A retry without a call left recorded a wait of 60 s that was not the real one. | Corrected: D4, U4. |
| "Stalled" is measured on the monotonic clock, `failing_since` is wall-clock time. | Kept; recorded in §17. |
| The density option caught every exception, patched outside its `try`, and mixed the timing keys of two threads. | Corrected. |
| Wording in TESTING and INTEGRATION_EVIDENCE that said more than was observed. | Corrected. |
| Rows that earlier tests left expired could be the ones a test's call takes. | Each worker test now removes them first. |
| The plan said STATUS and COMMANDS were updated when they were not yet. | Written with this delivery. |

**The corrections were not reviewed a second time.** They are covered by the tests named above and by §12.1.

### 12.4 Not run, and limits

- **Nothing on the normal app during the verification:** no query, no log read, no build, start or stop. The deployment came afterwards (§13.1). What is known about it comes from the two log extracts of §2, both taken by the session of ExecPlan 0023 with the owner's approval.
- **The harness's `Build`, the web part of `Checks`, and the browser phases.** No file under `apps/` and no API schema changed.
- **The harness's `Regression` as one call.** The test files of M0 to M4 ran by name. `tests/test_m5_*.py` and `tests/test_m6_*.py` did not: none imports the changed modules.
- **`PerformanceRetention`, `PerformanceFullRetention`, `PinnedExhaustion`, `PerformanceApi`, the recovery phases, the public-endpoint phases,** and density levels other than 1.8 million.
- **The slow first call itself is not reproduced as slow reads.** The tests end the same statement at the same function line through a held row lock, and the density option through a 100 ms deadline on the first call of an attempt. §4.4's explanation of 2026-10-06 stays INFERRED.
- **Synthetic rows.** Sizes, payload sharing and the M3 tables' row counts on the normal app were not read (§7, decision 3).
- **Three hours of failures and the hourly bound** are verified on a clock the unit tests move, not in real time.

## 13. Normal deployment (run 2026-10-07)

This section was the proposal. The owner approved it on 2026-10-07 ([DECISIONS](../../DECISIONS.md#2026-10-07--market-worker-deployment-approved-then-the-merge-execplan-0024)), and §13.1 records what ran. The procedure is the one that ran for ExecPlans 0021 and 0022 ([0022 §13.1](0022-reference-checks-and-rest-budget.md#131-executed-2026-10-03-05200522-utc-owner-approved)), with the rollback tag `:pre-0024`.

**Why only `market-worker`.** The change is in `worker.py` and in one function of `store.py`, which only the market worker executes. There is no schema change, so readiness is untouched. The API keeps its image. The execution and evaluation workers are not rebuilt or recreated, so the pilot's code identity stays and no new evaluation segment starts.

**Cost of the swap.** A market-worker restart stopped new quotes for 14–15 s on 2026-10-03. With a position open, the execution engine records one `PROTECTION_UNAVAILABLE` interval of about that length.

1. **Window.** HH:15–HH:45 UTC, never 23:50–00:20, and not in the minutes of the running worker's hourly retention, which moves by up to a minute an hour: read its last `market_retention_pruned` line first.
2. **Starting state, read-only.** Containers, images, schema revision, pilot state, the worker's restart count and its last retention line.
3. **Protected backup** with its SHA-256. No schema change, so no isolated restore.
4. **Rollback tag** `:pre-0024` on the running market-worker image.
5. **Build one image** from a clean tree at the pull request's head, and compare its `app/` tree with the tested image.
6. **Recreate one service:** `market-worker`, with `--no-deps`.
7. **Verify, read-only.** Every other container unchanged; the pilot's lease epoch and experiment version unchanged; quotes usable; the start-up pass logged (`market_retention_pruned`, or `market_retention_failed` followed by `market_retention_recovered`).
8. **Watch the next two hourly passes, read-only:** each ends in `market_retention_pruned` or in a failed attempt that recovers; no `COLLECTION_GAP` with `OperationalError`; restart count 0.
9. **Record** the commands, backup, image identities and results in this plan, STATUS and COMMANDS.

### 13.1 Executed 2026-10-07, 21:20–21:22 UTC (owner-approved)

**Approval.** After the report on pull request #31 the owner asked whether it was safe to merge, wrote `go ahead`, and chose in the question dialog at about 21:00 UTC: "Deploy first, then merge": recreate only `market-worker` from the pull request's head in an HH:15–HH:45 UTC window with a backup and the rollback tag `:pre-0024`, watch two hourly retention passes, then merge ([DECISIONS](../../DECISIONS.md#2026-10-07--market-worker-deployment-approved-then-the-merge-execplan-0024)). It does not approve touching postgres, the pilot workers, the API, the web app or the agent services, a schema change, or removing a tag, an image or a volume.

**Source.** This worktree at `65ba9a2`, clean. Its `services/`, `tools/` and `compose.yaml` equal the tested commit `9c7c87d`; the two commits after it are documents.

**What the new image changes for the worker (OBSERVED before the build).** The running image had been built from `0eb208a` (ExecPlan 0022), and `main` has gained M6's engine code since.
- The market worker imports eight files of the engine: `app/__init__.py`, `app/db.py` and six in `app/market_data/`. Between `0eb208a` and this head three of them differ.
  - `worker.py` and `store.py`: by this plan only. `main` did not change them in between.
  - `db.py`: two additive lines of M6. It also accepts schema `0008_m6_research`, and it names one more database identity. The normal database is at `0007_m5_agent_runtime`, which it accepted before and accepts now.
- The dependency lock is unchanged. The Dockerfile copies M6's prompt files in addition.
- The image holds the whole engine tree of `main` (145 files in `/app/app` against 103), of which this service runs `python -m app.market_data.worker`.
- The `market-worker` service definition in `compose.yaml`, its secret and its two networks are the same in the file the old container was created from (`cd5a5e9`), at this head, and in the primary checkout's file. The primary checkout is on the ExecPlan 0023 branch; its file differs from this head's only inside M6 services.

**Read-only starting state (21:04–21:07 UTC; OBSERVED).**
- Schema `0007_m5_agent_runtime`. Experiment `d779fbf4…` FORWARD_PAPER RUNNING, version 3; execution lease epoch 4, held; checkpoint 2,015,317, 0.6 s old. No open position (six `CLOSED_WITH_DUST`). The last `experiment_events` row is 71 (2026-10-01) and the last `execution_incidents` row is 577 (2026-10-07 01:19).
- Market: both feeds `CONNECTED` on collection `43efe2e3…`; market lease epoch 2192; `publication_lag_ms` 131. One market incident in the six hours before: the `COLLECTION_GAP` of 20:01:24 (§2.5).
- Retention passes by their manifests: 18:00:58–18:01:04 (19 deleting calls), 19:01:10–19:01:17 (20), the start-up pass after the third exit 20:01:43–20:01:52 (22), and 21:01:54–21:02:02 (18). The old worker logged `market_retention_pruned` with 20,460 records at 20:01:52 and 17,839 at 21:02:02.
- The market worker: container `117df6d29bda`, image `sha256:0d4d29bb4765…` (ExecPlan 0022), started 20:01:27.77, restart count 3. Its `/app/app` tree: 103 files, `ba9dc949…9c65`, the value of the 0022 record.
- Both compose files parsed (service names only were printed). A dry run of the recreate command named only `adaptive-spot-lab-market-worker-1` and changed nothing.

**Steps (all exit 0).**

| Step | Time (UTC) | Result |
|---|---|---|
| Protected backup | 21:20:01–21:21:05 | `pg_dump -Fc` in the postgres container (57 s), copied to the primary checkout's `.cache/deployments/retention-failure-20261007T212001Z/asl.dump`: 444,703,335 bytes, SHA-256 `7a1e8f9c891ccf33803e31c3474eebc63f654e9fc128dc29d55351e9b4ec17b6`, identical inside the container and on the host, and written beside it as `asl.dump.sha256`. The directory's ACL grants only the owner's Windows account. The temporary copy in the container was removed. No isolated restore: there is no schema change. |
| Rollback tag | 21:21:13 | `adaptive-spot-lab-market-worker:pre-0024` = `sha256:0d4d29bb4765ab288e893ce506c29c79ea5ff627b17bd79300a020bf110e6df3`, the running image. |
| Build one image | 21:21:14–21:21:17 | `docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker` → `sha256:31ee07e57436b44e0e7bd526be930cdfb70971c0d1ae529539220ccf3868e351`. Every layer came from the build cache: this day's isolated runs had built the same `runtime` target from the same files. |
| Tested source in the image | 21:21:20–21:21:45 | The image's `/app/app` tree has 145 files, and each has the SHA-256 that the acceptance run's snapshot recorded for the same file under `services/engine/app/` at commit `9c7c87d`: none missing, extra or different. The listing hashes to `20d67ad2c5002bd97ce0c441fb02613cc42bd653f327b299d91512a3f306c06d`. The tested images had been removed with their run (COMMANDS), so the comparison is with the snapshot's source hashes, not with an image. The worker module imports in the image and carries the new constants. |
| Old worker's log saved | 21:22:02 | 831 lines since 19:55 UTC, in this worktree's ignored `.cache/deployments/retention-0024/`. A recreate removes the container and its log. |
| Recreate one service | 21:22:02.6–21:22:07.1 | `docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker`. New container `82c8f5475b24`, started 21:22:06.11. |

As for 0021 and 0022, the image was built from this worktree, and the service was recreated with the primary checkout's `compose.yaml`, `.env` and secrets directory. `.env` and the secrets were not read. `compose.yaml` was compared as a file.

**Verified after the swap (read-only; OBSERVED).**
- **Only the market worker changed.** `postgres`, `api`, `web`, `execution-worker`, `evaluation-worker`, `agent-egress`, `agent-runner` and `agent-worker` have the same container, image and start time as before, and restart count 0.
- **The running code is the tested code.** Inside the running container the `/app/app` tree is the 145 files of the image (`20d67ad2…c06d`); `worker.py` `0252ff26…`, `store.py` `2b61c471…` and `db.py` `e6247c4e…` equal the commit's files. Its settings: collection enabled, `ASL_TEST_ISOLATED=0`, database `asl`, no rotation override.
- **Start-up.** Lease epoch 2193 at 21:22:07.80 and collection `6b0eb57f…` with epoch 2194 at once. The allowance of 6,000 was declared at 21:22:11.59. The start-up retention pass removed 6,013 records in 7 deleting calls (21:22:17.18–21:22:19.97; `market_retention_pruned` at 21:22:20.05). Stream connected at 21:22:21.10. No traceback.
- **The gap.** No new observation was published between 21:22:03.04 and 21:22:22.03: 19 s. The swap wrote no incident.
- **At 21:23:04.** Both feeds `CONNECTED` on the new collection; `publication_lag_ms` 122; market lease epoch 2194, held.
- **The pilot at 21:23:04.** RUNNING at version 3, the lease at epoch 4 and held, the checkpoint 0.1 s old at 2,018,260, no open position, and no new `experiment_events` or `execution_incidents` row. No position was open, so the swap produced no `PROTECTION_UNAVAILABLE` interval.

**The hourly pass moved with the restart.** Its schedule starts again with every process (§2.5): about 22:22:30, 23:22:50, then about 16 s later each hour. It now lies inside the hours' test window and no longer in HH:58–HH:07. The session of ExecPlan 0023 was told before the swap and after it; it had cleared the window of its own work.

**Soak (read-only): PASSED.** Two bounded reads after the first two hourly passes of the new worker.

| Pass | Deleting calls, by their manifests | The worker's log | Read at (UTC) |
|---|---|---|---|
| First | 20, from 22:22:27.23 to 22:22:34.59 | `market_retention_pruned`, 19,430 records, at 22:22:34.78 | 22:26:03 |
| Second | 17, from 23:22:41.91 to 23:22:47.85 | `market_retention_pruned`, 15,901 records, at 23:22:47.92 | 23:27:07 |

- **At both reads:** container `82c8f5475b24`, started 21:22:06.11, restart count 0. One collection, `6b0eb57f…`, and market lease epoch 2194 since the start. No market incident since 21:20 UTC. Both feeds `CONNECTED`; `publication_lag_ms` 135 and 133.
- **The pilot:** RUNNING at version 3, lease epoch 4 and held, the checkpoint advancing (2,028,931, then 2,038,738), no open position, and no new `experiment_events` or `execution_incidents` row.
- **Beside other work.** The session of ExecPlan 0023 had announced isolated test work for both passes' minutes (a secret-scan trial from 22:07, a fault phase from 23:07). This plan did not check what ran.
- **What the soak does not show.** No call failed in these two passes, so the new handling was not exercised on the normal app: there is no `RETENTION_FAILED` or `RETENTION_RECOVERED` yet. The soak shows that the passes, the stream and the pilot behave as before. The first call the database ends will show the rest (targets in §1).
- **The merge** follows this record, as the owner approved: pull request #31 pinned to its head, with an ordinary merge commit. GitHub records the merge commit; this section does not claim it.

**Not done.** Older rollback tags, untagged images and the build cache were left as they were; removing them is not part of this approval. The 1 Hz continuity probe of the 0021 and 0022 soaks was not run: this plan's targets are the retention passes and the restart count.

## 14. Failure and rollback

- **Rollback** is the previous image: tag `:pre-0024` back to `:latest` and recreate `market-worker` with the same command. No schema or data change has to be undone. Incident rows with the new codes stay as history; the old worker ignores them.
- **If `RETENTION_STALLED` appears:** quotes are unaffected. The record's SQLSTATE and line say what fails. Storage grows towards the 4 GiB warning and the 5 GiB stop over days, so there is time for decision 1 or 2 of §7.
- **If a retention failure still ends the process after the change:** roll back and keep the log; the error was then not a database error (D1).
- **The pilot** is not touched by the deployment or by a rollback.

## 15. Q01–Q10 (affected gates)

[Gate definitions](../../ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone).

| Gate | Applies | Acceptance condition | Evidence |
|---|---|---|---|
| Q01 UX, Q02 Accessibility | No | No UI change. The new incident codes appear as text in the existing incident list. | — |
| Q03 Data correctness | Yes | A failed call leaves nothing half deleted; the rules, the manifests and the fence are unchanged (R3, R5). | W1–W5, `WorkerFaults`, the test files of M0 to M4 |
| Q04 Security | Limited | No new destination, grant or credential; the records hold no parameter or row value. | U8; diff review |
| Q05 Reliability | Yes, core | R1–R8: no process or collection lost to a retention call; persistent failures back off inside the bound. | W1–W5, U1–U10, density with faults |
| Q06 Performance | Yes | The existing publication budgets with retention failing under the stream (R13). | `PerformanceDensity -RetentionFaults` |
| Q07 Automated verification | Yes | Every phase of §12 in Docker with no skipped test. | §12 |
| Q08 Visibility | Yes | R9: each failed attempt, a stall and the recovery are records and log events. | U1, U3, U9, W1, W2 |
| Q09 Deployment | Yes | §13: approval, backup, one image, one service, tested source, rollback tag. | §13.1 |
| Q10 Maintainability | Yes | Contracts updated with the code; official sources read (§9); no new dependency. | Diff review |

**Results.** Q03, Q05, Q06, Q07 and Q08 are met by §12.1 in isolation, with the steps that did not run listed in §12.4. Q04 and Q10 rest on U8, the review of §12.3 and the diff. Q09 is met by §13.1, with the soak recorded there. Q01 and Q02 do not apply.

## 16. Files

- `services/engine/app/market_data/worker.py` — the retention attempt, its schedule, its hour of calls and its records.
- `services/engine/app/market_data/store.py` — the function's lease refusal raised as `LostLease`.
- `services/engine/app/market_data/performance_density.py` — the retention fault option; retention's thread is timed.
- `services/engine/tests/test_m2_retention_faults.py` (new), `services/engine/tests/test_m2_unit.py`.
- `services/engine/tests/test_m2_reference_checks.py` — two tests that failed by timing corrected: one contradictory assertion removed, one assertion made to wait (§8).
- `tools/m2-acceptance.ps1` — the new test file in `WorkerFaults`; `-RetentionFaults`.
- `docs/MARKET_DATA.md`, `docs/OPERATIONS.md`, `docs/TESTING.md`, `docs/INTEGRATION_EVIDENCE.md`, `docs/COMMANDS.md`, `docs/STATUS.md`, `docs/DECISIONS.md`, `docs/README.md`, this plan.

Not touched: every migration, `services/engine/app/db.py`, `services/engine/app/market_data/read.py`, `services/engine/app/execution/**`, `apps/web/**`, `compose.yaml`.

## 17. Decision log

- **Housekeeping fails by itself.** 0012 chose "fail the feed closed, keep the subscription" for instruments, 0022 applied it to the clock. A retention call that fails closes nothing at all, because no quote depends on it.
- **Any database error, not only the two deadlines.** A violated reference or a lost connection in retention is no better reason to stop the stream than a deadline. A reference the rule does not know about would otherwise restart the worker at every start-up pass, at the same row.
- **A non-database error still ends the process.** That is a defect in the code, and M2's rule for it is to be visible.
- **The lease refusal is mapped in the store, not in the worker.** The store knows the function's message; the worker only knows `LostLease`.
- **Sixty seconds, doubling to the hour.** Both failures of 2026-10-06 were followed by a successful pass half a minute later. A persistent failure is tried seven times in the first two hours and then hourly, each try costing the database at most the two seconds of one call.
- **The wait grows only while nothing completes** (review). The first form doubled it after every failed attempt. Failures in the middle of passes would then have slowed a working retention down to one short attempt an hour, by the worker's own doing.
- **Any hour, not aligned hours** (review). The first form counted calls in hours that began with an attempt, which allowed up to 59 calls within 33 minutes across two such hours. The worker now keeps the send times of the last hour.
- **A retry without a call left says so** (review). Its record carries the real wait, and nothing is entered silently every 45 s meanwhile.
- **Three hours without a completed call for "stalled".** Long enough that a failure with one or two retries never reads as stalled; short against the days storage needs to reach its warning. Measured on the worker's monotonic clock like the rest of its schedule; `failing_since` is wall-clock time, so after the host has slept the two can disagree.
- **A new generation waits for a running retention call** (review). It was the one remaining way for retention to end the process, and it was reproduced. The alternative, not starting a pass while a rotation is asked for, covers one of the three rotation triggers.
- **The code changes instead of a second record.** One incident per failed attempt; the code says whether it is the first or the tenth hour.
- **No smaller batch in this change.** It needs the function to change (§7), and the measurement says it is not what the first call of a pass needs (§4.7).
- **The start-up pass stays where it is.** It delays the stream by the length of the pass. Moving it behind the stream start would shorten every restart, and is a change of M2's start-up order that was not asked for.
- **The older tests are corrected, not retried.** A test that fails one run in five on unchanged code makes every acceptance of this worker a matter of luck. In the first, the remaining assertions cover what the removed line meant; in the second, the assertion is the same and waits for what it reads.
- **The statement-deadline test uses a connection without a lock deadline for one call.** No statement can wait two seconds for a lock under the worker's own settings, and slowing the real function down needs either rows by the hundred thousand or a trigger added by the test. A held lock ends in the same statement, at the same line, with the same error as on 2026-10-06.

## 18. Progress and completion evidence

All times UTC on 2026-10-07.

- **13:43–14:10.** Task read; code, contracts and ExecPlans 0021 and 0022 read; official pages read (§9). Run `ret-1007a` prepared. The first three behaviour tests failed on the unchanged worker and passed on the first form of the change.
- **14:10–14:39.** Density database loaded (1.8 million synthetic observations) and the cost probes of §4 run. The first density run with retention faults passed (§12.2).
- **14:42.** The authoring client reached a usage limit. One local work-in-progress commit; nothing pushed.
- **About 18:50–19:43.** Work resumed. Two older tests found failing by timing on unchanged code and corrected (§8). The independent review and its corrections (§12.3): D7, the wait that grows only while nothing completes, the bound in any hour. Reproduction repeated in its final form (four cases failed on the unchanged code). Fresh-database check on run `ret-1007d`.
- **19:44.** Code commit `9c7c87d`, replacing the work-in-progress commit.
- **19:46–20:50.** Acceptance run `ret-1007b` on that commit (§12.1), with no load between 19:51 and 20:07.
- **20:01.** The normal worker exited a third time with the same error (§2.5); the session of ExecPlan 0023 reported it.
- **20:26 and 20:50.** The Docker resources of the three runs removed by exact name (COMMANDS).
- **20:50–20:54.** The documents completed, the link check, the documentation commits, the push and pull request #31.
- **About 21:00.** The owner approved the deployment and, after two hourly passes, the merge.
- **21:04–21:07.** Read-only starting state and the checks of what the new image changes for the worker.
- **21:20–21:22.** Backup, rollback tag, build, source check and the recreate of `market-worker` (§13.1). Verified by 21:23.

**Completion evidence:** §12.1 for the committed source; the pull request for the delivery; §13.1 for the deployment. **Open:** decisions 1 to 3 of §7. The merge follows this record, as approved.
