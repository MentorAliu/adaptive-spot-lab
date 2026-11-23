# ExecPlan 0021 — Market publication cost at stored-observation density

**Status: root cause reproduced; a second, not yet active cause found; both fixes IMPLEMENTED and VERIFIED in isolation, then DEPLOYED to the normal app's market worker on 2026-10-02 at 15:17 UTC with the owner's approval and VERIFIED by a two-hour soak ([§11](#11-normal-deployment-run-2026-10-02)). The pull request was merged as `d075a78` on 2026-10-02. The soak also showed two older causes of unusable quotes that this plan does not change ([§12](#12-findings-outside-this-change-and-proposed-follow-ups), items 2 and 10); [ExecPlan 0022](0022-reference-checks-and-rest-budget.md) proposes their fix.** Owner request of 2026-10-02: find why the market worker's overload incidents keep growing while the M4 pilot runs, reproduce it on an isolated stack with a realistically sized dataset, and propose a fix as an ExecPlan and pull request. Branch `claude/gallant-bassi-5685bb`, from `main` at `8fdc06a`. `main` moved to `dd95775` during the work, when M5-A was merged and deployed inert, and then to `cd5a5e9` (a documentation record of M5-B). The branch was merged with both, and the verification was repeated on the first merge, `b3f8216`, which is the last one that changes code (§9.4).

Labels: `OBSERVED` (seen in code or data), `INFERRED` (reasoned from observations), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

The owner's constraints for this work: no Docker or Compose command against the normal `adaptive-spot-lab` project, not even a read-only one; no build, recreate, restart or stop of its services; no read of `.env` or `secrets/`; isolated stacks only, with synthetic data or approved public data; delivery by pull request without merging. Everything below about the normal app is the owner's own observation, quoted in §2. Everything measured here comes from isolated runs.

## 1. Goal and observable outcome

1. **Explain** the growing `QUEUE_OVERLOAD` and `COLLECTION_GAP` incidents with evidence, and say what the overload threshold measures.
2. **Reproduce** the failure on an isolated stack whose stored history has the size the normal app reaches, with the unchanged worker.
3. **Fix** it so that receipt-to-publication delay does not grow with stored history. With up to seven days of full-density observations stored, the declared normal workload meets the M2 budgets (p95 ≤ 250 ms, p99 ≤ 1 s), with no collection interruption, including while the hourly retention deletes.
4. **Keep the publication rules:** raw payloads and revisions commit first; a separate fenced, serialized transaction assigns availability and sequence; nothing persisted is ever left unpublished silently.
5. **Deployable to the running pilot** by recreating only `market-worker`: no schema change, and the execution worker's image and code identity stay as they are.

## 2. Symptoms on the normal app (OBSERVED by the owner, read-only, 2026-10-02 08:17 UTC)

- `QUEUE_OVERLOAD` and `COLLECTION_GAP` per hour: about 1 on 2026-09-29, 5–13 on 2026-09-30, 6–21 on 2026-10-01, 31–53 on 2026-10-02 00:00–08:00 UTC. No isolated stack ran after 2026-10-01 15:33 UTC.
- Each recent gap: phase `maintenance_refresh`, `failure_code` `QUEUE_OVERLOAD`, queue `{"age": 0, "bytes": 0, "count": 0, "lag": 1000–1800, "overloaded": true}`, gap about 1.2–1.6 s.
- The worker log cycles `market_collection_started` → `market_stream_connected` → `market_collection_unavailable` → `market_collection_gap` → `market_socket_closed`, with REST calls to `/api/v3/time`, `/klines` and `/exchangeInfo` in each cycle.
- One market-worker container restart at 03:11 UTC on 2026-10-02. Nine `BACKFILL_FAILED` on 2026-10-02. `provider_dns_unavailable` bursts on 2026-09-30 04:00–11:00, 2026-10-01 10:00 and 2026-10-02 01:00.
- Docker VM: CPU pressure `some avg300=10.7` with only the normal app running, I/O pressure 0, memory fine. 504 local volumes (214 GB) and 1,367 images from earlier acceptance runs; 555 GiB free on the host.
- Later the same day, from [ExecPlan 0020's M5-B record](0020-m5-agent-runtime.md#m5-b--activation-login-profile-and-capability-probes-2026-10-02) (another session's read-only check at 13:20 UTC): 33–42 `COLLECTION_GAP` incidents an hour; the market-worker container had restarted again by itself at 10:47 UTC (restart count 3); and during the agent probe run the feed read `UNAVAILABLE` at 13:07:49 and `QUOTE_STALE` with a quote 39.6 s old at 13:11:55.
- Pilot effect on 2026-09-30, with BTC and SOL positions open: 11 `PROTECTION_UNAVAILABLE` intervals, mostly `FEED_OR_REFERENCE_UNAVAILABLE` lasting seconds, and one `QUOTE_STALE` of about 4 minutes that coincided with `stream_silent` and DNS incidents.

## 3. Current facts (OBSERVED at `8fdc06a`; the same files are unchanged on `main` at `dd95775`)

**The publication statement.** `store.publish_and_activate` (`store.py:367-453`) finds what to publish with:

```sql
SELECT … FROM market_observations o LEFT JOIN market_publications p ON p.observation_id = o.id
WHERE p.observation_id IS NULL ORDER BY o.received_at, o.id LIMIT 100
```

- Nothing bounds it: "unpublished" is the absence of a row in another table, and no index can answer that.
- It runs on every writer batch (`worker.py:272`), on every 32-row chunk of a REST ingest (`worker.py:231`), and after every candle confirmation (`worker.py:397`).

**One database thread and one writer lock.**
- All of the worker's data statements run on a single-thread executor (`worker.py:99`, `db()` at `worker.py:134-138`). Lease renewal and telemetry have their own thread.
- `ingest()` holds `write_lock` for a chunk's persistence and publication (`worker.py:227-231`). The stream writer takes the same lock for its batch (`worker.py:452`).
- A maintenance refresh runs every 45 s (`worker.py:515`). For each symbol it calls `ingest()` on the instrument snapshot, then `resolve_instrument` and `reference_checked` (`worker.py:306-319`). An unchanged snapshot persists nothing, but its publication statement still runs.

**The overload rule.**
- `ReceiveQueue.pending` holds every frame from receipt until its batch is published, including the batch being written (`pipeline.py:81-97`).
- `metrics()` sets the sticky `overloaded` flag when the oldest pending frame is older than 1,000 ms (`pipeline.py:99-105`). `observe_queue` samples it every 50 ms and raises `QUEUE_OVERLOAD` (`worker.py:491-501`).
- The collection is then torn down. The gap detail is written after the queue has drained, so it shows `count 0` and `age 0`; `lag` is the receipt-to-publication time of the last batch (`pipeline.py:97`, `worker.py:792-808`).
- Readers apply the same bound earlier: `telemetry_valid` requires the sampled oldest age plus the sample's own age to stay within 1,000 ms (`read.py:35-39`, `market_view.py:152-156`). A slow publication therefore makes quotes `FEED_OR_REFERENCE_UNAVAILABLE` for readers before the worker itself gives up.

**Recovery.** `run()` starts a new generation: `begin_collection`, a reference refresh (three `/time`, two `/exchangeInfo`), a 720-row backfill per symbol (two `/klines`, 46 chunks, each with a publication), retention, then the stream (`worker.py:824-831`).

**Retention.** `maintain_retention` runs at start-up and hourly inside the maintenance task. It issues up to 32 `prune_retention` calls back to back on the same single database thread as the stream writer (`worker.py:534-545`).

**Statement deadline.** The market worker's connections use `statement_timeout=2000` (`db.py:24`). A statement that exceeds it raises an error that `run()` does not expect, so the process logs `market_worker_fatal` and exits (`worker.py:855-858`); Compose restarts it.

**What M2 measured.**
- The 60-minute and burst workloads (`performance.py`) start on an empty database and send each second's frames as one burst.
- The full-density storage fixture (`performance_storage.py`) loads 1.8 million rows and times only `read.candles`.
- No test or workload ran the publication path against stored history. The retention function already carries a comment about this exact hazard for its own statement (`0004_m2_completion.py:112-113`).

## 4. Root cause

**The publication statement reads all stored history, on every batch.** §4.1 to §4.5 were measured on the isolated run `lag-1002b`: the unchanged worker at `8fdc06a` plus only the new measurement module, on PostgreSQL 17.11 with the normal app's limits (2 CPUs, 2 GiB, default configuration) and the worker's limits (1 CPU, 512 MiB). The data is a synthetic COPY in production record shapes; the feed and REST timing are the assumptions in §15.

### 4.1 The plan and its cost (OBSERVED)

PostgreSQL runs the statement in §3 as a parallel hash anti-join with a sequential scan of `market_observations` and of `market_publications`, at every stored size from 250,000 to 1,800,000 rows. With nothing to publish it still reads both tables.

| Stored observations | Publication statement in the worker, p50 / p95 (ms) | Receipt to publication p50 / p95 / p99 (ms) | Overload gaps in 600 s | Frames published / sent | Usable once-per-second samples | Oldest unpublished frame at worst | Event-loop lag p99 (ms) |
|---|---|---|---|---|---|---|---|
| 253,219 | 61 / 85 | 166 / 191 / 222 | 0 | 1,777 / 1,777 | 592 of 592 | 259 ms, 1 frame pending | 1.8 |
| 504,925 | 245 / 275 | 369 / 504 / 651 | 1 | 1,708 / 1,708 | 535 of 585 | 1,049 ms, 4 frames | 1.7 |
| 755,972 | 321 / 360 | 457 / 674 / 1,002 | 9 | 1,045 / 1,060 | 119 of 582 | 1,370 ms, 3 frames | 1.6 |
| 1,006,718 | 424 / 466 | 616 / 932 / 1,252 | 10 | 746 / 751 | 24 of 578 | 1,459 ms, 5 frames | 1.6 |
| 1,406,784 | 607 / 665 | 954 / 1,242 / 1,528 | 12 | 66 / 86 | never usable | 1,765 ms, 4 frames | 1.4 |
| 1,805,458 | 786 / 852 | 1,144 / 1,536 / 1,543 | 10 | 52 / 77 | never usable | 1,637 ms, 2 frames | 1.4 |

- "Usable samples" counts `read.health()` once a second after the first usable sample. At 1.4 and 1.8 million rows the quotes never became usable in ten minutes.
- Each overload gap records one `COLLECTION_GAP` and one `QUEUE_OVERLOAD` incident. All 42 collection failures in the run were `QUEUE_OVERLOAD`.
- The other per-batch statements stayed flat across all sizes: `storage_bytes` ≤ 2.5 ms p95, `persist_batch` ≤ 18 ms p95, `update_feed` ≤ 8 ms p95, `unresolved_candles` ≤ 8 ms p95.
- The statement cost quadruples between 250,000 and 500,000 rows (61 → 245 ms) and then grows about linearly. At 505,007 rows the join's hash no longer fits its memory budget (`work_mem` 4 MB, `hash_mem_multiplier` 2): the plan shows `Batches: 4` and about 9,000 temporary pages (70 MB) written and read back in every execution (OBSERVED, `full-scan-plan-505k.txt`). That this spill is the step is INFERRED; the 250,000-row plan text was not captured.
- With statistics that predate a batch of inserts, the planner instead chose a nested-loop anti-join over the receipt-time index. It probed the publication index once per stored row and took 845 ms at 556,020 rows (OBSERVED once, during a fixture load, `full-scan-plan-556k-during-load.txt`). Either plan reads all history.

### 4.2 How it becomes an overload (OBSERVED, with the code in §3)

- A stream batch waits for its 100 ms batching window, then for `storage_bytes`, one `persist_batch` per symbol and kind, the publication statement and the feed update. So receipt-to-publication is about 100 ms plus one publication statement: 166 ms at 250,000 rows, 616 ms at one million.
- Frames arrive at several phases each second. Once a publication takes longer than the spacing between batches, the next batch waits for the previous one.
- Every 45 s the maintenance refresh adds two more publication statements, one per instrument snapshot, on the same database thread and under the same lock. From about 500,000 rows that pushes a waiting frame past one second.
- The worker then closes the collection and starts a new generation, whose 46 backfill chunks each run the same statement. The first usable quote came 9 s after start at 250,000 rows, 23 s at one million, and not within ten minutes at 1.4 million. Forty-five seconds after the new generation's first refresh, the next refresh does it again: at 750,000 and one million rows the gaps recur about every 50–60 s.

**The signature matches the normal app.** At 1,006,718 rows, six of the ten gaps read phase `maintenance_refresh`, `failure_code` `QUEUE_OVERLOAD`, queue `{"age": 0, "bytes": 0, "count": 0, "lag": 1235–1281, "overloaded": true}`. The owner's rows in §2 read the same, with `lag` 1000–1800. At smaller sizes the bound is crossed just after the refresh and the phase reads `maintenance` or `streaming`; at 1.4 million rows and more it is crossed before the first refresh. The label is the phase at the instant the bound is crossed, which depends on REST round-trip times that this run only assumes.

**The growth matches too (INFERRED row counts).** The normal database's row counts were not read. Two indirect measures agree on roughly 0.5 million rows on the morning of 2026-09-30 and 0.75–0.85 million on the morning of 2026-10-02:
- the hours of collection since about 05:19 UTC on 2026-09-28 at the declared 10,800 observations an hour, less the recorded outages (4.3 h on 2026-09-30 and 7.6 h overnight to 2026-10-01) and the time lost to the gaps themselves;
- the size of the protected dumps, which grew from 56.6 MB (2026-09-28 22:30) to 149.7 MB (2026-09-30 08:24) and 237.3 MB (2026-10-02 08:22), as ExecPlans 0012, 0017 and 0020 record.

The owner's hourly incident counts (about 1, then 5–13, 6–21 and 31–53) rise along the same curve as the isolated gap counts: none in ten minutes at 250,000 rows, one at 500,000 and nine at 750,000, which is 54 an hour. Two read-only queries would replace the inference (§12).

### 4.3 What the overload threshold measures

Neither backlog nor scheduler lag.

- **Not backlog.** At the moment of every overload at most 5 frames were pending, of a capacity of 4,096. The queue was never deep; one small batch was slow.
- **Not scheduler lag.** A probe on the worker's event loop measured p99 lag of 1.4–1.8 ms and a maximum of 33 ms at every size, while frames aged past 1,000 ms. The loop was idle and waiting for the database thread.
- **What it is.** The flag is the age of the oldest frame that has not finished publication, including the batch being written (§3). It is a receipt-to-publication deadline. That is a real delay in making a quote available, so failing closed on it is correct; the defect is the statement that causes the delay.
- **Why the detail looks empty.** The gap detail is written after the queue has drained, so it always shows `count 0` and `age 0`. Its `lag` is the last batch's receipt-to-publication time.
- **Readers see it first.** With the telemetry sample up to 250 ms old, a reader marks quotes `FEED_OR_REFERENCE_UNAVAILABLE` once a frame has waited about 750 ms. That is consistent with the pilot's short `PROTECTION_UNAVAILABLE` intervals on 2026-09-30, at about half a million rows.

### 4.4 Ruled out or not reproduced

- **Test load:** none ran on the host after 2026-10-01 15:33 UTC (owner), and the isolated run reproduces the failure with no other load.
- **Blocking calls on the event loop:** see the loop probe above. DNS lookups run in a thread (`provider.py:39`); REST and socket I/O are asynchronous; parsing is sub-millisecond.
- **REST and DNS timing:** the reproduction uses a loopback provider with no network at all. REST waits happen outside the writer lock. A separate probe from an isolated container resolved both provider hosts 2,700 times each between 09:20 and 10:05 UTC with no failure (p50 2 ms, p99 99 ms and 30 ms). The DNS bursts in §2 are a separate matter (§12).
- **Disk:** I/O pressure was 0 on the normal app, and the statement's cost in isolation does not depend on the 214 GB of old volumes.
- **The container restart was not reproduced.** No statement reached the two-second deadline in that run; the slowest publication took 1,022 ms. The normal database also serves the API and both pilot workers inside the same 2-CPU limit, which this run does not model.

### 4.5 Why acceptance did not catch it

The M2 budgets were met on an empty database (§3). The cost only appears with hundreds of thousands of stored rows, which the normal app reached two days after collection was enabled. No workload ran a retention that deletes while a stream was publishing either (§4.6).

### 4.6 A second cost in the same path: retention under the stream (OBSERVED)

The fixed-code density run showed something the normal app has not reached yet. Retention deletes nothing until observations are seven days old, which on the normal app is about 05:19 UTC on 2026-10-05.

- **Cost of a retention call.** A call that deletes 500 observations and their payloads took 300–400 ms at 1.8 million stored rows, on both the unfixed and the fixed worker. Its two selection statements are index-driven (1.4 ms and 15 ms, `retention-plans-1800k.txt`); the time goes into the deletes themselves, with their per-row triggers and foreign-key checks. The function belongs to the schema and is not changed here.
- **Where it ran.** `maintain_retention` issued up to 32 such calls back to back on the writer's database thread (`worker.py:540-541` at `8fdc06a`). The thread takes work in arrival order, so the writer's statements and the retention calls alternate: every statement of a stream batch waits behind one retention call, and a batch has four or more statements.
- **Experiment 1** (`retention-exp-1-fixed-publication.log`): commit `0941756`, which has the publication fix only, on the 1.8-million-row isolated database, with retention made due 45 s after the first usable sample. Six deleting calls (2,670 observations) took about 300 ms each (maximum 325 ms). A frame reached 1,161 ms, the worker recorded `QUEUE_OVERLOAD` in phase `maintenance`, and quotes were unusable for 50 s. Publication itself stayed at 5 ms.
- **Expected on the normal app (INFERRED).** At the declared density one hour makes 10,800 observations due, which is 22 deleting calls. Without a change, the hourly retention would close the collection once an hour from 2026-10-05, even with the publication fix.
- **Experiment 2** (`retention-exp-2-own-thread.log`): the same database with retention on its own thread (D6). Three deleting calls (1,344 observations), no incident, receipt-to-publication p99 115 ms and maximum 117 ms, every sample usable. The final acceptance run exercises a full-size retention (§9).

## 5. Scope and exclusions

**In scope:** the publication path of the market worker and its store functions; a density workload and harness phase; tests; contract text; a deployment proposal for the running pilot.

**Excluded:**
- Any schema migration. It would need the migration owner and a new revision in the release beside the running pilot, for a defect that code alone can fix.
- The overload policy itself (tear-down at one second). §12 proposes an owner decision.
- DNS and clock-check failure handling, the REST weight budget, `stream_silent`. See §12.
- PostgreSQL configuration and container limits; the normal app's Docker volumes and images.
- The API, the execution and evaluation workers, the web app, strategy, risk and fill semantics.
- Normal deployment. It is proposed in §11 and needs the owner's approval.

## 6. Design (IMPLEMENTED)

**D1 — Publish by identity.** `persist_batch` already returns the identities of the revisions it created. The worker keeps them in `MarketWorker.unpublished` and passes at most 100 per transaction to `publish_and_activate(observation_ids=…)`. The store selects exactly those rows that are not yet published:

```sql
SELECT … FROM market_observations o WHERE o.id = ANY(CAST(:ids AS uuid[]))
AND (SELECT p.sequence FROM market_publications p WHERE p.observation_id = o.id) IS NULL
ORDER BY o.received_at, o.id
```

- The publication check is a scalar subquery on purpose. It is one unique-index lookup per identity; a join could be planned as a scan of every publication. The retention function uses the same form for the same reason.
- An identity leaves the list only after its publication transaction has committed. A failed attempt keeps it.
- Everything else in the transaction is unchanged: the advisory writer lock, both fence checks, receipt order inside the batch, `available_at`, the feed-state updates and the pointer activation for pending targets.

**D2 — The full scan becomes the recovery scan.** `store.publish_recovered` loops the old statement, 100 rows per transaction, until nothing is left. `MarketWorker.begin_collection` calls it at every generation start, under `write_lock`, after the new generation is registered and before any reference refresh, backfill or stream. It then clears the identity list. It covers:
- a process that died between its persistence commit and its publication;
- a persistence commit whose outcome the process never learned (the identities were never returned);
- a publication that failed, which ends the generation;
- a capture drain that failed during teardown.

**D3 — The recovery scan has its own deadline.** Its transaction sets `statement_timeout` to 20 s with `set_config(…, is_local => true)`; every other statement keeps the two-second bound. Lease renewal runs on its own thread and connection and is not delayed. The scan runs while no frame is waiting, so its duration costs recovery time, not quote usability.

**D4 — Confirmations.** In the identity path the pending-confirmation statement runs only when the caller has just written a confirmation (`confirm_candle` returned true). The recovery scan always includes it.

**D5 — Unchanged entry points.** `publish_pending` and `publish_and_activate()` without identities keep the full-scan behaviour. Test fixtures and the browser fixture feed use them on small disposable databases.

**D6 — Retention on its own database thread.** `prune_retention` runs on a dedicated single-thread executor (`market-maintenance`) with its own connection. The writer's statements no longer queue behind retention calls (§4.6).
- PostgreSQL runs both at once without blocking: retention deletes rows older than seven days and takes the lease `FOR KEY SHARE` like every fenced statement; it does not take the writer's advisory lock.
- The calls, their 500-row bound, their fence and the retention rules are unchanged.
- A call that is in flight when its task is cancelled finishes on that thread, as it did before on the writer's thread.

**Invariant.** After a generation start, every unpublished revision is in `MarketWorker.unpublished`. Each persistence is followed by a publication under the same lock hold, and any exception from either one ends the generation, whose successor starts with the recovery scan. So no revision stays unpublished past the next generation start, which is the old guarantee restated: before, the next publication of any kind found it.

**Rejected alternatives.**
- *Bound the scan by receipt time.* An index range from a time floor would be cheap, but receipt times come from the worker's wall clock. No floor is provably below every unpublished row across clock steps and lease handovers.
- *A pending-publication table or a `published` flag.* Exact and cheap, but it is a schema migration beside the running pilot, an extra write per observation and a new grant.
- *Raise the one-second bound or make the flag non-sticky.* The statement would still cost more with every stored row and would reach the two-second statement deadline; see §4. The policy question is separate (§12).
- *PostgreSQL tuning* (more CPU, `work_mem`, no parallel workers). It needs a database restart, which the owner excluded, and only moves the point of failure.
- *Shorter retention.* It lowers the ceiling and changes the retention contract without removing the dependence on stored history.

## 7. Requirements and tests

| ID | Requirement | Evidence |
|---|---|---|
| R1 | Identity publication publishes exactly the given revisions, in receipt order, once | `test_identity_publication_publishes_exactly_the_given_revisions` |
| R2 | A fenced-out owner publishes nothing, by identity or by scan | same test |
| R3 | The identity statement reads only the given identities, with 20,000 stored rows | `test_identity_publication_reads_only_the_given_revisions` (`EXPLAIN ANALYZE`) |
| R4 | A generation start publishes an earlier process's leftovers under its own fence, before streaming | `test_generation_start_recovers_leftovers_and_the_stream_publishes_by_identity` |
| R5 | Stream publication never falls back to the full scan | same test |
| R6 | A revision stranded by an unknown persistence outcome or a failed publication is recovered by the next generation; recovery does not make the new generation usable | `test_revisions_a_failure_left_unpublished_are_recovered_by_the_next_generation` (two cases) |
| R7 | The recovery deadline applies to its transaction only | `test_recovery_scan_deadline_is_local_to_its_transaction` |
| R8 | Activation, confirmations, fencing, drains, rotations and faults behave as before | existing `WorkerFaults` suites and the full regression |
| R9 | With stored history up to 1,800,000 observations: p95 ≤ 250 ms, p99 ≤ 1 s, every frame published, no gap or overload, no unusable sample, no worker stop; identity publication reads no table sequentially and costs ≤ 50 ms at p95; recovery scan ≤ 5 s | `PerformanceDensity` (§9) |
| R10 | Retention calls that delete do not delay stream publication, and run on their own thread | `test_hourly_retention_under_stream_load_never_delays_the_writer` |
| R11 | At 1,800,000 stored observations a retention run that deletes at least 10,000 observations under the stream stays inside the R9 budgets | `PerformanceDensity`, last stage (§9) |

## 8. Official sources and versions

- **PostgreSQL 17.11** (`postgres:17.11-alpine3.24`, `compose.yaml`), default configuration, 2 CPUs and 2 GiB as in the normal app.
  - `set_config(setting_name, new_value, is_local)`: "If `is_local` is `true`, the new value will only apply during the current transaction." ([Configuration Settings Functions](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADMIN-SET)). Checked on the installed stack by R7.
  - `statement_timeout`: "Abort any statement that takes more than the specified amount of time." and "The timeout is measured from the time a command arrives at the server until it is completed by the server." ([Client Connection Defaults](https://www.postgresql.org/docs/17/runtime-config-client.html#GUC-STATEMENT-TIMEOUT)).
  - Plans are OBSERVED with `EXPLAIN (ANALYZE, BUFFERS)` on the isolated database at each density, not taken from documentation.
- **SQLAlchemy 2.0.54 and psycopg 3.3.6** (`services/engine/uv.lock`). A Python list of UUIDs binds to `CAST(:ids AS uuid[])`; exercised by R1 and R3.
- **No new dependency.**

## 9. Verification (isolated)

Host: Windows 11, Windows PowerShell 5.1, Docker Desktop (Engine 29.8.1), Docker VM with 16 CPUs and 7.7 GiB. Containers ran under the Compose limits of the normal app: PostgreSQL 2 CPUs and 2 GiB, the worker's test container 1 CPU and 512 MiB. Times are UTC on 2026-10-02. Commands are in [COMMANDS.md](../COMMANDS.md#execplan-0021-isolated-density-commands--2026-10-02); logs are under `.cache/m2/<run>/` in this worktree.

**The workload (`PerformanceDensity`).**
- **Stored history.** A guarded COPY loads synthetic observations that are already published, in production record shapes: two tickers a second with the public 24-hour-ticker field set, and two candle updates every other second. It loads in stages to 250,000, 500,000, 750,000, 1,000,000, 1,400,000 and 1,800,000 rows, then `VACUUM (ANALYZE)`.
- **The worker.** At each stage `MarketWorker.run()` itself runs for 600 real seconds against a loopback provider: lease, generation start, reference refresh, 720-row backfill per symbol, stream, the 45-second maintenance refresh, and its own failure recovery and backoff.
- **The feed.** Three frames a second arrive at four phases inside each second. Each REST answer takes an assumed 150 ms.
- **Measurements.** Receipt-to-publication time of every frame from the database; `read.health()` once a second; every store statement's time; the oldest pending frame and the event-loop lag every 20 ms; incidents and generations.

### 9.1 Unfixed worker, run `lag-1002b` (record-only)

A scratch `git worktree` of `8fdc06a` with only the harness script and the measurement module added; the module's idle timing used the statement text of §3. `PerformanceDensity -Observe` ran 09:08–10:17. Results are in §4.1.

### 9.2 Publication fix alone, run `lag-1002a` (commit `0941756`)

`PerformanceDensity` with the budgets enforced ran 10:17–11:26 and exited 0 with no budget failure at any of the six levels: receipt-to-publication p95 115–117 ms and p99 117–120 ms, every frame published, every sample usable. `Checks`, `WorkerFaults` (42 passed), `Regression` (260 passed) and `RecoveryMemory` passed on that commit. The run did not exercise retention under the stream; the two experiments of §4.6 then ran against its 1.8-million-row database.

### 9.3 Final source, run `lag-1002c` (commit `b40ac9a`)

Every phase exited 0. The two `Snapshot`s, at 11:42 and 12:56, record commit `b40ac9a3efaf914a782cad987b44e5b0f9c3d98d` and the same 291 source hashes.

- **Checks** (11:43): web lint, typecheck, unit tests, API-contract check, Ruff, OpenAPI check, format check and the production web build. No web source changed.
- **WorkerFaults:** 43 passed, none skipped (36 before this plan, plus the seven new tests).
- **Regression:** 261 passed, with the one pre-existing Starlette test-client deprecation warning.
- **RecoveryMemory:** 30 measured recoveries, 428 KiB settled RSS growth, 0 retained market tasks, the same as ExecPlan 0012 recorded.
- **PerformanceBurst:** 30,000 of 30,000 published in 300 s; receipt-to-publication p50 135.4 ms, p95 158.9 ms, p99 167.8 ms; schedule lag p99 2.0 ms; maximum RSS 71,576 KiB. ExecPlan 0012 recorded p95 168.7 ms and p99 175.3 ms.
- **PerformanceDensity** (11:42–12:50): exit 0, no budget failure at any stage.

| Stored observations | Publication statement p50 / p95 (ms) | Receipt to publication p50 / p95 / p99 / max (ms) | Overload gaps | Frames published / sent | Usable once-per-second samples | Oldest unpublished frame at worst | Event-loop lag p99 (ms) | Recovery scan at generation start (ms) |
|---|---|---|---|---|---|---|---|---|
| 253,228 | 5 / 10 | 111 / 115 / 117 / 130 | 0 | 1,786 / 1,786 | 595 of 595 | 138 ms, 1 frame | 1.6 | 58 |
| 505,020 | 7 / 10 | 113 / 117 / 119 / 124 | 0 | 1,794 / 1,794 | 597 of 597 | 162 ms, 1 frame | 1.6 | 290 |
| 756,818 | 7 / 9 | 113 / 116 / 118 / 171 | 0 | 1,794 / 1,794 | 597 of 597 | 179 ms, 1 frame | 1.6 | 308 |
| 1,008,611 | 7 / 9 | 113 / 116 / 118 / 172 | 0 | 1,793 / 1,793 | 597 of 597 | 211 ms, 1 frame | 1.6 | 447 |
| 1,410,401 | 7 / 9 | 113 / 116 / 117 / 122 | 0 | 1,792 / 1,792 | 597 of 597 | 147 ms, 1 frame | 1.6 | 663 |
| 1,796,193 | 7 / 9 | 113 / 116 / 118 / 131 | 0 | 1,790 / 1,790 | 596 of 596 | 135 ms, 1 frame | 1.6 | 818 |

- **One generation per stage.** No collection failure, no incident and no worker stop occurred in the six windows. The first usable sample came 4–6 s after start.
- **Retention under the stream** (last stage). The retention became due 125 s into the window. Its 32 deleting calls removed 16,000 observations and 16,000 payloads while the stream ran, which is why the last row stores fewer observations than were loaded. That window's figures are the last row: p99 118 ms, maximum 131 ms, every sample usable.
- **Against the unfixed worker** (§4.1): at one million rows receipt-to-publication p95 fell from 932 ms to 116 ms, and at 1.8 million rows the quotes went from never usable to always usable.

Statement plans and idle cost at each stage, before the stage's workload:

| Stored observations | Full scan (ms) | Pages the full scan reads | Identity statement (ms) | Identity publication p95 (ms) | Recovery publication, slowest of 5 (ms) |
|---|---|---|---|---|---|
| 250,002 | 72 | 10,887 | 0.30 | 4.1 | 70 |
| 503,226 | 288 | 21,707 | 0.33 | 8.6 | 480 |
| 755,022 | 372 | 32,513 | 0.42 | 7.0 | 2,417 |
| 1,006,818 | 515 | 43,285 | 0.59 | 6.6 | 430 |
| 1,408,609 | 795 | 60,470 | 0.47 | 6.5 | 667 |
| 1,810,403 | 1,119 | 77,644 | 2.66 | 8.9 | 811 |

- **The identity statement** reads the 32 given identities through the primary key and 32 publication index entries at every size. It never scans a table.
- **The full scan** is still the parallel hash anti-join of §4.1 at every size; at 1.8 million rows its hash runs in 16 batches and writes about 34,000 temporary pages (`full-scan-plan-1800k.txt`). It now runs once per generation start.
- **One slow recovery publication:** 2,417 ms at 755,022 rows; the other four took at most 345 ms. It is inside its 20 s deadline and the 5 s budget. The unfixed worker runs the same statement under the two-second deadline, where it would have ended the process (§12, item 3).
- **The activation statement** (latest published quote) reads 2 rows at every size, and the pending-confirmation statement takes 0.04–0.06 ms.

### 9.4 Merged with `main`, run `lag-1002d`

`main` moved to `dd95775` while this work ran: the M5-A pull request was merged after its inert deployment. The branch was merged with it as `b3f8216`. The conflicts were documentation only: each side had added a COMMANDS section and an entry in the docs index. The market worker's files (`store.py`, `worker.py`, `pipeline.py`, `provider.py`, `read.py`) are identical on both bases; the merge brings the M5 code, migration 0007 and the M5 tests into the tree under test.

Every phase was repeated on `b3f8216` (13:02–14:17) and exited 0. The two `Snapshot`s record that commit and the same 374 source hashes.

- **Checks:** pass.
- **WorkerFaults:** 43 passed, none skipped.
- **Regression:** 381 passed (the suite now includes the M5 tests), with the one pre-existing warning.
- **RecoveryMemory:** 30 measured recoveries, 392 KiB settled RSS growth, 0 retained market tasks.
- **PerformanceBurst:** 30,000 of 30,000 published; p50 136.2 ms, p95 161.2 ms, p99 173.8 ms; schedule lag p99 2.1 ms; maximum RSS 72,592 KiB.
- **PerformanceDensity** (13:03–14:11): exit 0, no budget failure at any stage.

| Stored observations | Publication statement p50 / p95 (ms) | Receipt to publication p50 / p95 / p99 / max (ms) | Overload gaps | Frames published / sent | Usable once-per-second samples | Recovery scan at generation start (ms) |
|---|---|---|---|---|---|---|
| 253,228 | 6 / 10 | 112 / 115 / 117 / 125 | 0 | 1,786 / 1,786 | 595 of 595 | 79 |
| 505,019 | 8 / 10 | 114 / 117 / 119 / 126 | 0 | 1,793 / 1,793 | 597 of 597 | 459 |
| 756,811 | 7 / 9 | 113 / 117 / 120 / 131 | 0 | 1,790 / 1,790 | 596 of 596 | 596 |
| 1,008,604 | 7 / 9 | 114 / 117 / 119 / 128 | 0 | 1,793 / 1,793 | 597 of 597 | 478 |
| 1,410,394 | 7 / 10 | 114 / 117 / 119 / 139 | 0 | 1,792 / 1,792 | 597 of 597 | 671 |
| 1,796,189 | 7 / 10 | 114 / 117 / 120 / 127 | 0 | 1,791 / 1,791 | 597 of 597 | 828 |

At the last stage the retention became due 124 s into the window, and its 32 deleting calls removed 16,000 observations and 16,000 payloads under the stream. The identity statement used index scans only at every stage; idle identity publication p95 was 4.7–9.7 ms, and the slowest idle recovery publication was 868 ms.

### 9.5 Not run, and limits of this evidence

- **Normal deployment and soak:** RUN after this section was written (§11.1).
- **The 60-minute M2 normal workload:** NOT RUN. The density phase runs the same frame rate for six ten-minute windows against stored history; the five-minute burst was rerun.
- **Public-provider phases:** NOT RUN. Nothing here contacts the provider, so the feed phases and the REST round trip are assumptions, and the hourly instrument adoption and backfill-under-stream are covered only by the existing `WorkerFaults` tests.
- **Other database clients:** the isolated PostgreSQL serves only the worker and a once-per-second health read. The normal one also serves the API and both pilot workers.
- **Browser and UI phases:** not applicable; no UI or API change.
- **GitHub CI:** did not run (§16).

### 9.6 Load on the shared host

The isolated work ran while the pilot was live, across the 09:00 to 14:00 UTC hour boundaries. Docker VM pressure, read from throwaway containers:

| Time | CPU `some avg300` | I/O `some avg300` | Memory available | Load average (1 min) | Isolated work at that moment |
|---|---|---|---|---|---|
| 08:32 | 10.75 | 0.13 | 6.2 GB | 2.00 | none yet |
| 08:49 | 7.91 | 0.31 | 5.6 GB | 4.55 | fixture load and the regression suite |
| 09:53 | 11.21 | 0.00 | 6.0 GB | 2.59 | unfixed worker at one million rows |
| 11:02 | 8.66 | 0.07 | 6.0 GB | 2.42 | fixed worker at one million rows |

The isolated containers have their own CPU limits on a 16-CPU VM; the pressure stayed in the range it had before any isolated work started. Only one density database ran at a time, to keep the page cache of the normal PostgreSQL from being squeezed.

## 10. Data and trust-boundary changes

- **No schema change, no new grant, no new role or destination.** The identity statement and the recovery scan read and write the same tables with the same market-worker privileges as before.
- **Session setting.** The recovery transaction changes its own `statement_timeout`; PostgreSQL lets any role do that for itself.
- **Connections.** The worker holds one more connection, for retention, under the same market-worker role and deadlines.
- **Evidence rules unchanged:** observations stay append-only and deduplicated, publication stays fenced and serialized, no quote is fabricated or backdated, and incidents are immutable.
- **Fixtures.** The density fixture refuses any database that is not the run's disposable `asl_m1_m2_…_density` database, and writes only `FIXTURE` rows.

## 11. Normal deployment (RUN 2026-10-02)

### 11.1 Executed 2026-10-02, 15:15–15:18 UTC (owner-approved)

**Approval.** After the report on pull request #13 the owner wrote in chat: "I approve the deployment in the next HH:15–HH:45 window". That approves the steps of §11.2 for the market worker, including the read-only commands that verify them. It does not approve merging the pull request, changing the overload policy, or removing any volume.

**Source.** Pull-request head `4003e754f9c0da45c88e9b8a15877307216d562e`, with a clean tree for `services/`, `tools/` and `compose.yaml`; no source file differs from the tested merge `b3f8216`.

**Read-only starting state (14:54 and 15:15 UTC; OBSERVED).**
- Schema `0007_m5_agent_runtime`. Experiment `d779fbf4…` FORWARD_PAPER RUNNING, version 3; execution lease epoch 4, held; checkpoint 2–4 s old. No open position (two `CLOSED_WITH_DUST`). The last `experiment_events` row is 71 and the last `execution_incidents` row is 89, both of 2026-10-01 06:57.
- Agent runtime `PROBE_ONLY`; 13 workflows, all terminal; none in flight.
- Market: both feeds `UNAVAILABLE` with `QUEUE_OVERLOAD`; the newest quotes 70–155 s old; 37 `COLLECTION_GAP` and 35 `QUEUE_OVERLOAD` incidents and 38 new generations in the preceding hour; `publication_lag_ms` 1,152; market lease epoch 2136.
- Stored rows (planner estimates): 749,332 observations and 749,053 publications; 1.29 GB of market relations. This replaces the inference of §4.2: the normal app was at the size where the isolated unfixed worker recorded nine gaps in ten minutes.
- The market worker: container `a78b4a5405eb`, image `sha256:73df98a623ee…`, started 13:26:36 with restart count 4.

**Steps (all exit 0).**

| Step | Time (UTC) | Result |
|---|---|---|
| Protected backup | 15:15:44–15:16:22 | `pg_dump -Fc` in the postgres container, copied to the primary checkout's `.cache/deployments/publication-density-20261002T151536Z/asl.dump`: 240,352,091 bytes, SHA-256 `34b57448e9def617054f9a40056305ea1d6e8272e9aa67a8ea1c3c96809d66b3`, identical inside the container and on the host. The directory's ACL grants only the owner's Windows account. The temporary copy in the container was removed. No isolated restore: there is no schema change. |
| Rollback tag | 15:16:40 | `adaptive-spot-lab-market-worker:pre-0021` = `sha256:73df98a623ee…`. The existing `:pilot-d779fbf4` tag names the same previous image. |
| Build one image | 15:16:40–15:16:42 | `docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker` → `sha256:0d6ac003d93358dd1041255a33bda93c1f307420da39a30083b0dc8bb99c74c9`. |
| Tested source in the image | 15:16:57 | The image's `/app/app` tree (103 files) hashes to `bc56f6cb…8bdc`, equal to the tree of the tested image `asl-m2-lag-1002d-density-engine-tests`; `store.py` `a324bc0d…` and `worker.py` `c52a4389…` are equal too. |
| Recreate one service | 15:17:04–15:17:10 | `docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker`. New container `1becbec082dc`, started 15:17:09. |

**Two differences from §11.2 as proposed.**
- **Where the image was built.** Step 5 named the primary checkout at the pull-request head. The image was built from this worktree at the same commit instead, because its files are the ones the tested images were built from, and the owner's primary checkout stayed on `main` at `cd5a5e9`, untouched. The service was recreated with the primary checkout's `compose.yaml`, which is identical to the pull request's, and with its `.env` and secrets directory, neither of which was read.
- **The backup commands.** The first form of the backup command was refused by the coding client before it ran; the same steps then ran as recorded above.

**Verified after the swap (read-only; OBSERVED).**
- **Only the market worker changed.** `postgres`, `api`, `web`, `execution-worker`, `evaluation-worker`, `agent-egress`, `agent-runner` and `agent-worker` have the same container, image, start time and restart count as before.
- **The running code is the tested code.** Inside the running container the `/app/app` tree hashes to `bc56f6cb…8bdc`. Its settings: collection enabled, `ASL_TEST_ISOLATED=0`, database `asl`, no rotation override.
- **Start-up.** Lease epoch 2138 at 15:17:19, generation 2139, stream connected at 15:17:40. Nothing was pending for the recovery scan (no `market_publications_recovered` event; zero unpublished rows since).
- **Quotes.** The first new quotes were received at 15:17:41.0 (SOL) and 15:17:41.2 (BTC) and published 0.12 s later; both feeds `CONNECTED` and usable at 15:17:43.
- **The gap.** The old worker's last quotes were received at 15:15:49, when it failed with its own `QUEUE_OVERLOAD` and entered its backoff. It was stopped at 15:17:04. The interval without quotes was therefore 15:15:49–15:17:41, of which the swap itself accounts for 37 s.
- **Publication.** `publication_lag_ms` 122; over the first 73 stream observations receipt-to-publication p50 118 ms, p95 131 ms, p99 135 ms.
- **The pilot.** At 15:18:09 the experiment was RUNNING at version 3, the lease at epoch 4 and held, the checkpoint 0.5 s old, with no new `experiment_events` or `execution_incidents` row, so no `SEGMENT_STARTED`, `EXECUTION_DOWNTIME` or step failure.

**Soak (read-only).** Two consecutive hours of the continuity probe at 1 Hz, 15:18:11–17:18:28 UTC, across the 16:00 and 17:00 boundaries, and read-only SQL up to 17:18:54. The probe files are in this worktree's `.cache/deployments/publication-density-20261002T151536Z/`.

- **No overload.** No `QUEUE_OVERLOAD` since the swap, against 573 earlier that day and 35 in the hour before. One process, restart count 0. `publication_lag_ms` read 122–138 at every check. Over the 21,220 stream observations received since the swap, receipt-to-publication was p50 118.1 ms, p95 134.9 ms, p99 143.9 ms and at most 207.5 ms, and none was left unpublished.
- **Usability.** 6,985 of 7,200 samples were usable (97.0%). The 215 unusable ones have three causes, none of them publication:

| Interval (UTC) | Samples | What the probe read | Cause |
|---|---|---|---|
| 15:21:13–14, 15:59:17–18, 16:11:13, 16:24:53–54 | 7 | `QUOTE_STALE` | Delivery stalls on the stream. At 15:21 the frames with events 15:21:08–14 arrived in two bursts at 15:21:13 and 15:21:14 and were published within 0.17 s of receipt; a REST request in the same minute took 13 s. INFERRED: network or provider. The 5 s quote-age rule failed closed. |
| 15:37:15–15:38:12 | 58 | `FEED_OR_REFERENCE_UNAVAILABLE`, then `QUOTE_STALE` | `clock_uncertain`: three `/time` answers of about 1.06 s each failed the clock check, and the worker closed a healthy collection (phase `maintenance_refresh`). Recovery waited through `clock_recovery_pending` and an 18 s `/klines` request. |
| 16:01:38–16:02:12 | 35 | the same | `clock_uncertain` again, with `/time` answers of 1.0 and 2.6 s. |
| 16:58:43–17:00:37 | 115 | `FEED_OR_REFERENCE_UNAVAILABLE` | No incident, and quotes at most 3 s old. Three consecutive REST requests each waited about 60 s (16:57:29 → 16:58:31 → 16:59:32 → 17:00:34), so the instrument and clock checks aged past their 120 s bound: SOL was unusable in 111 of the samples, BTC in 69, both in 65. This is the REST weight-budget wait that ExecPlan 0012 lists as a residual. |

- **Both remaining causes predate this change** (§12, items 2 and 10): `CLOCK_UNCERTAIN` was recorded 9–18 times a day since 2026-09-29. The overload gaps had been hiding them.
- **Hour boundaries.** The changed instrument snapshots were adopted in place at 16:00:49.8 and 17:00:37.5 and activated within a second, with no gap from either. The hourly backfill ran under the stream at 17:02 without an incident. Retention has nothing to delete before 2026-10-05.
- **The pilot.** Unchanged through the soak: RUNNING at version 3, lease epoch 4 and held, checkpoint advancing (760,135 → 781,285), no `experiment_events` or `execution_incidents` row. The SNAPSHOT reports for 16:00 and 17:00 were created at 16:05:10 and 17:05:11.
- **Hourly evaluation marks.** Both marks at 16:00 were `VALID`, the first valid ones of the day: the 32 earlier hourly marks of 2026-10-02 were 31 `STALE` and 1 `UNAVAILABLE`. Both marks at 17:00:00 were `UNAVAILABLE`; that instant lies inside the 115 s interval above.
- **Every other container** was identical to the starting state at 17:18.
- **Host.** PostgreSQL used 3–11% of one CPU after the swap, and the Docker VM's load average fell from about 2 (before any isolated work) to about 1 or less. Its CPU pressure did not change (`some avg300` 11–12 before and after), so that pressure has another source than this app's containers (§12, item 5).

**Rollback (not needed so far).** `docker tag adaptive-spot-lab-market-worker:pre-0021 adaptive-spot-lab-market-worker:latest`, then the recreate command above.

### 11.2 The steps as proposed

This is the proposal as it stood before the approval. It is kept unchanged as the record of what was approved; §11.1 says what was done.

**State of the normal app, from [ExecPlan 0020's B8](0020-m5-agent-runtime.md#b8-completion-evidence--inert-normal-deployment-2026-10-02) and M5-B records, not re-read here.** Schema `0007_m5_agent_runtime` since 08:25 UTC on 2026-10-02; `api` and `web` are the M5 builds; the agent runtime is inert. At 08:25 UTC the market worker was container `a78b4a5405eb`, image `sha256:73df98a623ee…`; it restarted by itself again at 10:47 UTC (restart count 3). The execution and evaluation workers are unchanged (`sha256:5b02dbe11ce8…`, `sha256:6e2d4e6a117c…`), and the pilot's recorded code identity is `82c36154…`. No position was open at 08:17 UTC. Since 11:12 UTC the M5-B agent services run beside the pilot, with the runtime in `PROBE_ONLY` (the same plan's M5-B record). Step 2 reads the state again.

**Why only `market-worker`.** The change is in `store.py` publication functions and `worker.py`, which only the market worker executes. There is no schema change, so readiness is untouched. The API keeps its current image; it never publishes. The execution and evaluation workers are not rebuilt or recreated, so the pilot's code identity stays the same and no `SEGMENT_STARTED` is appended. The new market-worker image is built from `main` after this pull request, so its `app/` tree also contains the M5 code; that container runs only `app.market_data.worker`. This is the first change to the market worker since the pilot started: ExecPlan 0020 deliberately never touched it.

**Cost of the swap.** A market-worker restart stops quotes for about 20 s (ExecPlan 0012 measured 19–20 s; the new start-up no longer runs a full scan per backfill chunk). With a position open, the execution engine records one `PROTECTION_UNAVAILABLE` interval of about that length. The unfixed worker currently produces that many times an hour (§2, §4).

**Proposed steps.**
1. **Window.** Between HH:15 and HH:45 UTC, never between 23:50 and 00:20, as [OPERATIONS](../OPERATIONS_M3_M7.md#m5-agent-runtime-operations-execplan-0020) sets for deployments beside the pilot (OD-12 itself requires outside HH:00–HH:03). If the owner prefers, at a moment with no open position and no agent workflow in flight.
2. **Starting state (read-only).** `docker compose -p adaptive-spot-lab ps`; container ID, image ID, start time and restart count of every service; schema revision; incident counts for the last hour.
3. **Protected backup** per [OPERATIONS](../../OPERATIONS.md#milestone-completion-deployment): `pg_dump -Fc` to `.cache/deployments/publication-density-<ts>/` in the primary checkout, with its SHA-256. No schema change, so an isolated restore is optional.
4. **Rollback tag.** Tag the running market-worker image `:pre-0021`.
5. **Build one image.** In the primary checkout at this pull request's head commit, with a clean tree: `docker compose --profile market build market-worker`. Only the `market` profile is selected, and only this service is named.
6. **Recreate one service.** `docker compose --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker`. `--no-deps` leaves PostgreSQL and every other service alone. The old worker stops gracefully, drains and releases its lease.
7. **Verify.**
   - The running market-worker image is the built one, and the in-container `app/market_data/store.py` and `worker.py` hash to this commit's files.
   - `postgres`, `api`, `web`, `execution-worker` and `evaluation-worker` have the same container IDs, images, start times and restart counts as in step 2; the lease epoch of the execution worker is unchanged; and the experiment has no new `SEGMENT_STARTED`, `EXECUTION_DOWNTIME` or failure event.
   - Both feeds become `quote_usable`; the log shows `market_collection_started` and, if anything was pending, `market_publications_recovered`.
8. **Soak across two hour boundaries.** The read-only continuity probe at 1 Hz, plus read-only SQL: no `QUEUE_OVERLOAD` or `COLLECTION_GAP` since the swap, `publication_lag_ms` near the isolated values in §9, and the in-place `maxQty` adoptions at HH:00. The first retention that deletes is expected about 05:19 UTC on 2026-10-05; check the hour after it the same way (`market_retention_pruned` in the log, no incident).
9. **Record** the commands, backup, image IDs and soak in this plan, STATUS and COMMANDS.

**Rollback.** Retag `:pre-0021` and recreate `market-worker` the same way. It is image-only: the old worker's full scan publishes whatever exists, and the new worker leaves nothing behind that the old one cannot read.

**If the owner does not deploy.** Stored observations keep growing until the seven-day retention starts deleting on 2026-10-05: at the declared density up to 1.8 million rows, less what the outages lose. §4 shows what the unfixed worker does at 1.0, 1.4 and 1.8 million rows.

## 12. Findings outside this change, and proposed follow-ups

These were seen while investigating. None is changed by this plan.

1. **Overload policy (owner decision, PROPOSED).** When the oldest unpublished frame is older than one second, the worker closes the collection. Recovery then takes tens of seconds and seven REST requests, so a 1.2 s delay becomes a much longer outage, and with a persistent cause it repeats at every refresh.
   - (a) Keep the rule. It is the current contract ([MARKET_DATA](../contracts/MARKET_DATA.md#implemented-m2-observation-boundary)).
   - (b) Keep quotes ineligible for as long as the delay lasts, which readers already do through telemetry, and close the collection only on capacity exhaustion (4,096 frames or 8 MiB) or when the delay passes a second bound such as the 5 s quote age.
   - Recommendation: (b), as its own plan with fault tests. With this plan's fix the trigger should not occur in normal operation under either rule.
2. **A slow or failed clock request ends a healthy collection (OBSERVED on the normal app during the soak).** The routine clock check takes three `/time` requests and fails when the best round trip is over one second. That check is not guarded (`worker.py:283`, `:517` at `8fdc06a`), so the worker tears the stream down although the socket is fine.
   - It happened twice in the two-hour soak and cost 58 s and 35 s of usable quotes (§11.1). `CLOCK_UNCERTAIN` was recorded 1, 9, 16, 18 and 16 times on 2026-09-28 to 2026-10-02.
   - A failed DNS lookup has the same effect (INFERRED from code): every REST request resolves the host again (`provider.py:119`), and a failed lookup raises `provider_dns_unavailable` without a retry (`provider.py:39-41`). The normal app recorded that code 996 times on 2026-09-30, 9 times on 2026-10-01 and 100 times on 2026-10-02. A 45-minute probe from an isolated container found no failed lookup (§4.4), so those belong to particular times rather than to a standing resolver fault.
   - ExecPlan 0012 already lists clock and REST outages as follow-ups. Recommendation: a plan that treats a failed *routine* check like 0012 treats a transient instrument failure: fail the feed closed, keep the socket, retry. Drafted as [ExecPlan 0022](0022-reference-checks-and-rest-budget.md).
3. **The container restarts (OBSERVED in part).** A statement that exceeds the two-second deadline raises a database error the worker treats as fatal (§3).
   - Two collection gaps on 2026-10-02, at 09:16:28 and 10:47:17 UTC, have `failure_type` `OperationalError` in phase `maintenance_refresh`. The second matches the restart ExecPlan 0020 recorded at 10:47. The restart count had reached 4 by 13:26 UTC.
   - The SQLSTATE is not in the incident, so the statement timeout itself is INFERRED. The unfixed isolated run did not reproduce it (§4.4); in the final run one idle execution of the same full scan took 2,417 ms at 755,022 rows (§9.3), which is past the deadline the unfixed worker applied to it.
   - The new worker's restart count was 0 after the soak.
4. **`BACKFILL_FAILED` (INFERRED).** Every restart runs a backfill with two `/klines` requests. Dozens of restarts an hour multiply the exposure to any transient REST or DNS failure. Not verified. The normal app recorded 11 on 2026-10-02 and none on earlier days.
5. **CPU pressure (not explained by this defect).** The expectation was that the pressure in the Docker VM came from the publication scan. After the swap PostgreSQL used 3–11% of one CPU and the VM's load average fell from about 2 to about 1, but its CPU pressure stayed at `some avg300` 11–12 (§11.1). Its source is something other than this app's containers and was not identified.
6. **Docker volumes and images.** The 504 volumes and 1,367 images are not a cause: I/O pressure is 0 and the host has 555 GiB free. Removing them is an owner decision ([OPERATIONS](../../OPERATIONS.md#backup-and-restore)).
7. **Acceptance coverage.** Any later change to the market worker or its store should run `PerformanceDensity` with the other M2 performance phases.
8. **Other readers at density.** ExecPlans 0014 and 0017 bounded the execution engine's market reads. The API and execution statements were not measured again here.
9. **Confirmation on the normal database (DONE with the deployment).** The read-only starting state of §11.1 read the planner's row estimates and the worker telemetry: 749,332 observations, `publication_lag_ms` 1,152. The owner had approved the deployment and its read-only checks, not this item by name; the row estimates were read as part of that starting state. The incident history by day confirms §2: `QUEUE_OVERLOAD` 1, 93, 165 and 573 on 2026-09-29 to 2026-10-02 (the last up to the swap).
10. **REST weight-budget waits age the reference checks (OBSERVED on the normal app during the soak).** The worker caps itself at 120 request weight a minute and counts the provider's `X-MBX-USED-WEIGHT-1M` header against that cap. The header covers the whole public IP. When it is high, each request waits up to a minute.
    - Once in the soak, three requests in a row waited about 60 s each and the checks aged past 120 s. For 115 s a feed read `FEED_OR_REFERENCE_UNAVAILABLE` with fresh quotes and no incident: SOL for 111 s, BTC for 69 s, both together for 65 s. The pilot's 17:00:00 evaluation marks fell inside the 65 s and are `UNAVAILABLE`. (Corrected on 2026-10-02 after the merge, from the probe file: this item first said both feeds for 115 s.)
    - The worker's own use is about 57 weight a minute. INFERRED: another client on the same public IP used the rest; the owner's Docker host also runs another project's containers. Not verified: the header values are not logged.
    - ExecPlan 0012 lists this as a residual and scheduled refreshes 45 s apart so that one such wait is harmless. Two or three in a row are not.
    - Recommendation: the same follow-up plan as item 2 should cover it: log the observed header, and decide how the local cap relates to an IP-wide figure. Drafted as [ExecPlan 0022](0022-reference-checks-and-rest-budget.md).

## 13. Q01–Q10 (affected gates)

| Gate | Applicability | Result | Evidence or missing check |
|---|---|---|---|
| Q01 UX | Not applicable | NOT APPLICABLE | No UI, route or API change. |
| Q02 Accessibility | Not applicable | NOT APPLICABLE | No shipped UI change. |
| Q03 Data correctness | Applicable (core) | VERIFIED in isolation | R1–R7: exact identity publication, fencing, receipt order, recovery of stranded revisions, nothing left unpublished. Existing activation, confirmation, conflict and drain tests pass unchanged. |
| Q04 Security | Limited | VERIFIED by review | No new destination, credential, grant or role. One more connection under the same role. The fixture refuses non-disposable databases. |
| Q05 Reliability | Applicable (core) | VERIFIED in isolation and on the normal app for this defect | Isolated: no collection interruption at any stored size, including a full retention under the stream; `WorkerFaults` and the regression pass. Normal app: no `QUEUE_OVERLOAD` in the two-hour soak (§11.1). Two older causes still interrupt usability there (§12, items 2 and 10); the first retention that deletes has not happened yet. |
| Q06 Performance | Applicable (core) | VERIFIED in isolation | Declared budgets in R9 and R11, met at every stage of run `lag-1002c`; the burst workload passed. |
| Q07 Automated verification | Applicable | VERIFIED locally | `Checks`, `WorkerFaults`, `Regression`, `RecoveryMemory` in Docker with no skipped test. GitHub CI did not run (§16). |
| Q08 Visibility | Limited | IMPLEMENTED | New log event `market_publications_recovered`; OPERATIONS explains reading `publication_lag_ms` against queue count. No test asserts the log line, and the normal deployment had nothing to recover, so the event has not been seen outside the isolated runs. |
| Q09 Deployment | Applicable | VERIFIED | §11.1: owner approval, protected backup with checksum, one image built and one service recreated, running source equal to the tested image, every other container unchanged, two-hour soak, image-only rollback tag. |
| Q10 Maintainability | Applicable | VERIFIED | MARKET_DATA, OPERATIONS, TESTING, COMMANDS and STATUS updated with the change; PostgreSQL 17 behaviour checked against the official documentation and on the installed stack; no new dependency. |

Related acceptance outcomes: P06 (data integrity) and P10 (operations) for the changed path only. No trading-readiness or profitability claim follows from this plan.

## 14. Files

- `services/engine/app/market_data/store.py`: named publication statements, `publish_recovered`, identity path and optional deadline in `publish_and_activate`.
- `services/engine/app/market_data/worker.py`: `unpublished` identities, identity publication, recovery at generation start, retention executor.
- `services/engine/app/market_data/acceptance.py`: the test session shuts the retention executor down.
- `services/engine/app/market_data/performance_density.py` (new): density fixture and workload.
- `services/engine/tests/test_m2_publication_density.py` (new).
- `tools/m2-acceptance.ps1`: `density` database, `PerformanceDensity` phase, the new test file in `WorkerFaults`.
- `docs/MARKET_DATA.md`, `docs/OPERATIONS.md`, `docs/TESTING.md`, `docs/COMMANDS.md`, `docs/STATUS.md`, `docs/README.md`, this plan.

## 15. Decision log

- **Identity publication with a generation-start recovery scan** was chosen over the alternatives in §6 because it is exact, needs no schema change and touches only the market worker.
- **The recovery scan stays a full scan.** Its cost grows with history, but it runs while nothing waits, and it is the only statement that can find a row nobody remembers.
- **The density workload sends frames at four phases per second and gives each REST answer an assumed 150 ms.** The M2 workload's single burst per second and instant REST hid where the refresh's database work falls between stream batches. Both values are stated assumptions, not measurements of the provider.
- **Retention moved to its own thread rather than paced or locked.** Taking the writer lock per call would bound the delay to one call, about 400 ms, which leaves little of the one-second bound. Pacing the calls stretches the effect over minutes. A separate thread adds no delay.
- **The retention function is not changed.** Its cost per call is in the schema-owned deletes; changing it would need a migration.
- **The overload policy is not changed here.** It is an owner-approved contract; §12 states the question.
- **The deployed image was built from this worktree, not from the primary checkout.** The worktree at the pull-request head holds the files the tested images were built from, and the owner's primary checkout stayed on `main`, untouched. The source in the image was compared with the tested image before the recreate (§11.1).
- **The clock-check and REST-budget gaps the soak showed were not fixed in this change.** The approval covered the deployment of this plan's fix only, and both behaviours are owner-approved fail-closed contracts of ExecPlan 0012 (§12, items 2 and 10).

## 16. Progress and completion evidence

**2026-10-02 (UTC).**
- 08:17: the owner's observations (§2) and the request.
- 08:30–09:07: code reading; the measurement module and harness phase; a 60-second smoke run found a fixture defect (a staged load collided with finals the worker's own backfill had stored). Two attempts at the unfixed run were stopped to make the workload more faithful: the first sent each second's frames as one burst, the second answered REST at once. Their partial logs are kept.
- 09:08–10:17: unfixed worker, run `lag-1002b` (§4).
- 10:17–11:26: publication fix, commit `0941756`, run `lag-1002a` (§9.2).
- 11:27–11:41: the retention cost found in that run's statement timings; two experiments (§4.6); D6, commit `b40ac9a`.
- 11:42–12:57: final source, run `lag-1002c` (§9.3).
- 13:00: pull request MentorAliu/adaptive_spot_lab#13 opened. It conflicted with `main`, which had moved to `dd95775`.
- 13:01–14:17: merge `b3f8216` and the repeated verification, run `lag-1002d` (§9.4).
- 14:20: `main` had moved again to `cd5a5e9`, a documentation-only change (five files under `docs/`); merged as `2b4aa11` with no conflict and no code difference from `b3f8216`.
- 14:51: the owner approved the deployment for the next HH:15–HH:45 window.
- 14:54–15:15: read-only starting state.
- 15:15–15:18: backup, rollback tag, build, source check and the recreate of `market-worker` (§11.1).
- 15:18–17:19: soak across the 16:00 and 17:00 boundaries (§11.1).
- 18:32: on the owner's instruction, pull request #13 merged as `d075a78`. `services/engine` on `main` has the same git tree as at `4003e75`, so the merge needs no redeployment.
- After the merge: [ExecPlan 0022](0022-reference-checks-and-rest-budget.md) drafted for §12's items 2 and 10 (PROPOSED).
- **GitHub CI did not run.** The workflow run for the first push ended as `startup_failure` after 0 s, as the runs on `main` and on other branches did the same day. STATUS records that Actions has not started on the account since 2026-09-29. The local harness is the only automated evidence.

**Completion evidence.** R1–R11 are VERIFIED in isolation on commit `b40ac9a` (§9.3) and again on the merge with `main`, `b3f8216` (§9.4). The change was delivered as pull request MentorAliu/adaptive_spot_lab#13 and merged as `d075a78` on 2026-10-02 at 18:32 UTC. Since 15:17 UTC that day the normal app's market worker runs the pull request's commit `4003e75` (§11.1), whose engine source is identical to `main`'s; its soak recorded no overload.

**Disposable resources.**
- Removed during the work, so that reruns could start on an empty database: the density volumes of the smoke run and of the two stopped attempts, the smoke run's images, and the DNS probe's container and network. All were created by this task minutes earlier.
- Left in place, stopped: four density volumes of about 4.3 GB each (`asl-m2-lag-1002a-density_postgres_data`, `asl-m2-lag-1002b-density_postgres_data`, `asl-m2-lag-1002c-density_postgres_data`, `asl-m2-lag-1002d-density_postgres_data`), five small engine and performance volumes of runs `lag-1002a`, `lag-1002c` and `lag-1002d`, and the runs' images. Removing the volumes and images is the owner's decision. The evidence is under `.cache/m2/lag-1002a` to `lag-1002d`. *(The volumes and images were removed on 2026-10-03 on the owner's instruction; the evidence stays. See [COMMANDS](../COMMANDS.md#test-run-cleanup--2026-10-03).)*
- The scratch `git worktree` of `8fdc06a` used for the unfixed run was removed after its evidence was copied to `.cache/m2/lag-1002b/`.

**Residual limitations.**
- The isolated evidence is synthetic. The normal app was measured for two hours after the swap, at about 750,000 stored rows; it has not yet reached the sizes above one million rows or a retention that deletes (expected about 05:19 UTC on 2026-10-05).
- On the normal app, clock-check tear-downs and REST budget waits still make quotes unusable for a minute or two at a time (§12, items 2 and 10). In the soak that was 3% of the seconds, and it included one hourly evaluation mark.
- The feed's arrival phases and the 150 ms REST round trip are assumptions. With one burst a second the unfixed worker fails later than with staggered frames.
- The isolated PostgreSQL has no other clients. The container restart at 03:11 UTC was not reproduced (§4.4).
- The recovery scan still reads all history: 0.8–1.1 s at 1.8 million rows, once per generation start, with no frame waiting.
- A retention call still takes 300–400 ms; it no longer delays publication, but it runs up to 32 times an hour on its own connection.
- The overload policy, DNS and clock-check handling, and the other findings in §12 are unchanged.
- The 60-minute M2 normal workload and the public-provider phases were not rerun (§9.5).

**Next.** The owner decides on: [ExecPlan 0022](0022-reference-checks-and-rest-budget.md), the proposed fix for the clock-check and REST-budget behaviour (§12, items 2 and 10); the overload policy (§12, item 1); and whether to remove this task's stopped volumes and images. *(Since then ExecPlan 0022 was approved, deployed and merged, and the volumes and images were removed on 2026-10-03. The overload policy is still open.)* The hour after 05:19 UTC on 2026-10-05 is worth a read-only look, as §11.2 step 8 describes.
