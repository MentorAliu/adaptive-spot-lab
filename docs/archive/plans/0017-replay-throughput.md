# ExecPlan 0017 — Replay step throughput

**Status: IMPLEMENTED, verified on M4 and DEPLOYED to the normal app (2026-09-30); merge approved by the owner after the verified deployment.** The plan merged in PR #5 (`4c0a682`). Implementation is on branch `claude/replay-throughput` (PR #6). M4 (#7) and ExecPlan 0018 (#8) merged on 2026-09-30, and the branch is rebased onto `main` `9e84eff` (§14.1, §17). The isolated gate passed in full both before the rebase (`rt-0929d`, §18.5) and on the rebased code (`rt-0929f`, §18.6), including the seven-day budget and the forward engine's 60-minute workload. Progress and evidence are in §17 and §18.

The plan itself came from a read-only investigation:
- no code, contract or configuration file was edited;
- no Docker build, test, migration, login, provider call or normal-app command was run;
- only this file was written, on branch `claude/replay-throughput-plan`, delivered by pull request.

Owner request: after [ExecPlan 0014](0014-bounded-latest-quote.md#103-seven-day-replay-throughput-b4-failed) recorded the seven-day replay budget as still FAILED, the owner asked for an investigation of per-step cost with options. The recommendation (read-cost cuts in all modes, replay-only batched transactions, replay-only state reuse; keep the 20 min budget and decide any revision after measuring) was presented in chat. The owner answered "do the recommended" (§3).

Labels: `OBSERVED` (seen in code, data or command output), `INFERRED` (derived from observed facts, not measured directly), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal and observable outcome

Replay steps must get cheap enough that the seven-day full-density replay meets its declared budget, **without changing any replay result** and without weakening the forward engine's authority checks.

Observable outcomes:
- `PerformanceReplay` completes twice, each run ≤ 20 min, with identical fingerprints ([ExecPlan 0011 §10](0011-paper-broker-reference.md#10-verification-commands-and-measurements-proposed)).
- Every replay result is unchanged:
  - the `fixture:gapped-stop` fingerprint stays `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e`;
  - a new step-trace digest (§4.4) matches the pre-change baseline on fixtures and on a fixed density window.
- The forward engine keeps its M3 budgets (60-minute workload p95 ≤ 750 ms) and its per-step authority checks.
- If the 20 min budget is still missed, the measured per-step figures are recorded and the owner decides the budget (§3, OD-B).

## 2. Current facts

### 2.1 What the 0014 evidence measured (OBSERVED, INFERRED)

- **OBSERVED:** `.cache/m3/bq-0929a/replay/density-run1-partial.txt` (primary checkout) was captured from the replay database. Its `steps|36057|2026-08-25 17:00:00.15+00|…` line counts step records. The first `decided_at` equals the BTC instrument publication's availability: history start `T0 − 150 h` = 2026-08-25 18:00 UTC, instrument received one hour earlier, available +150 ms (`fixtures.py`, `m3_performance.py:302-406`, `scenarios.py:15`).
- **OBSERVED:** the engine writes an `execution_steps` row only when a step has effects (`engine.py:1122-1130`).
- **OBSERVED:** once base-asset holdings are nonzero, `needs_step` returns true for every quote of either symbol (`engine.py:247-252`). Non-final candles are skipped (`engine.py:253-257`). The density workload publishes, per symbol, one quote per second and a provisional candle every two seconds (`m3_performance.py:19-22`).
- **INFERRED:** with positions open the engine runs two step transactions per simulated second, and about half of them have effects. In the sampled minute (3,771 publications, 1,295 effect-bearing steps), about 2,514 step transactions ran: **about 24 ms per transaction**, not the 46 ms per step recorded in 0014 §10.3.
- **INFERRED:** most effect-bearing steps are `HIGH_WATER` valuations:
  - Equity is floored to 1e-8 USDT (`numbers.py:17`, `engine.py:864`) and NAV per unit is quantized to 1e-36 (`numbers.py:18, 89-93`).
  - Any bid uptick on a held asset therefore raises NAV above the high-water mark (`engine.py:876-888`).
  - Each such step writes a valuation row, the `account_state` NAV update and a step record.
  - The synthetic sine paths rise for long stretches.
  - This is correct M3 behavior and is not changed here (§4.5).
- **Budget arithmetic (INFERRED):**
  - A full week has 1,209,600 quote publications.
  - With positions open for most of it (maximum hold 72 h, `definitions.py:76`), that is roughly 0.9–1.2 million step transactions.
  - 20 minutes therefore allows **about 1 ms per step**, including the non-stepped publications.
  - The actual open fraction is unknown until a full run completes.
- **Remaining time at the old rate (INFERRED):** at 24 ms per transaction, the 1,272,114 publications left at the stop point need about 5.7 h if positions stay open. That matches 0014's "at least 5.7 more hours", which supports the reinterpretation.

0014's historical record is left as written; this plan carries the correction.

### 2.2 What one step executes (OBSERVED, code reading)

A no-effect quote step in replay, with positions open and `REPLAY` activation active (`activation.py:42-48`), issues **27 SQL statements plus a COMMIT, on three pooled connections**:

| Where | Statements | Code |
|---|---|---|
| Before the transaction, own connection | 2 × `latest_final_open_ms` (one per symbol) | `engine.py:420-427`, `market_view.py:213-219` |
| Transaction: authority | lease `FOR KEY SHARE`, `account_state FOR UPDATE`; recheck before COMMIT | `store.py:94-116`, `engine.py:323, 335` |
| Transaction: state | holdings, live positions, open orders, active obligations, latches, breaches (6) | `engine.py:483-488`, `store.py:126-169` |
| Transaction: market | 2 × `latest_quote`, 2 × `instrument`, 1 × `quote_at_sequence` | `engine.py:493-508`, `market_view.py:99-113, 159-164` |
| Transaction: other | daily reference, 2 × pending entry signals, checkpoint upsert | `engine.py:870, 972, 1101, 1120`, `store.py:172-199, 238-246` |
| After COMMIT, third connection | `refresh_summary`: 7 statements | `engine.py:181-216, 344` |

An effect-bearing `HIGH_WATER` step adds `insert_valuation`, `update_nav` and `insert_step` (`store.py:646-670, 249-258`).

- The replay engine uses `pool_pre_ping=True` (`replay/run.py:41`). SQLAlchemy pings at every checkout and rolls back on return (§8). So each connection adds round trips beyond the statements. The exact driver-level count (psycopg `BEGIN`) is not claimed here; it is measured in I0.
- The only query sampled as a single hotspot besides COMMIT is `latest_final_open_ms`. It computes `max(o.open_ms)` over a join of `market_observations` and `market_publications`.
  - **INFERRED from the query shape:** PostgreSQL's min/max index shortcut does not apply to a join, so the query visits every stored final candle of the symbol and probes its publication.
  - It runs twice per step.
  - It is verified by `EXPLAIN` in T1; it has not been run.

### 2.3 Constraints the design must respect (OBSERVED)

- **Timeouts:** the execution identity has `statement_timeout = 2000 ms`, `lock_timeout = 1000 ms` and `idle_in_transaction_session_timeout = 3000 ms` (`db.py:24`). The lease is 10 s with 2 s renewal (`store.py:25, 70-83`).
- **Replay lease:** replay renews the lease synchronously on its own pooled connection (`driver.py:25-26`).
- **Single writer:** replay always starts from reset state (`replay/run.py:75-107`, `m3_performance.py:415-420`). It has no resume path and no other writer.
- **Writers of step-read tables:**
  - The API has `SELECT` only on the M3 tables (`0005_m3_paper_broker.py:577`).
  - `account_holdings` holds only BTC and SOL rows and is writable only by `asl_execution` (`0005:114, 597`).
  - Every table read by `StepContext.load` and `refresh_summary` is therefore written only by the execution role.
  - The one exception is `account_state`, which the API's funding path also updates. In replay, funding runs only in `prepare`, before the run.
- **Triggers:** all M3 triggers are `BEFORE` guards that raise or return `NEW` unchanged (`0005:400-540`). None write another table or rewrite values.
- **Market rows:** market observations are immutable outside bounded retention (`0003:168-186`). Retention never deletes an instrument observation that another observation references (`0004:99`).
- **Clock defaults:** every `recorded_at` default is `clock_timestamp()` (`0005:93-362`). Statement order stays visible within one transaction, for example in the `last_decision` tie-break (`store.py:208-212`).
- **Fingerprint coverage:** the fingerprint covers orders, fills, positions, mandates, obligations, evaluations, outcomes, decisions, valuations, references, latches, breach events, account state, holdings and fill postings (`fingerprint.py:16-79`). It does **not** cover:
  - `execution_steps`
  - `execution_incidents`
  - `position_events`
  - `order_events`
  - `execution_checkpoints`

### 2.4 Per-step reads that grow with history in the forward engine (INFERRED)

- `latest_final_open_ms` visits every stored final candle. Final candles are retained 730 days ([MARKET_DATA](../../MARKET_DATA.md)), up to about 17,520 per symbol, and M4's pilot is open-ended (ExecPlan 0015 OD-13a). This plan fixes it (A1a).
- `pending_entry_signals` and the summary's pending-signal query scan the mode's `strategy_evaluations`: about 17,500 rows a year, three times per step. The fix needs a partial index, which is a schema migration, so it is left to M4's migration (§14).

## 3. Owner decisions (recorded 2026-09-29)

- **OD-A Scope:** "do the recommended". That means A (read-cost cuts, all modes), B1 (replay-only batched transactions) and B2 (replay-only state reuse with a verification mode).
- **OD-B Budget:** keep the declared 20 min budget. If T11 fails after I3, record the measured figures. The owner then chooses, before any new measurement:
  - (a) a revised time bound for the same workload;
  - (b) a different workload;
  - (c) no time bound, keeping two identical fingerprints.
- Contract records: add both decisions to [DECISIONS.md](../../DECISIONS.md) at implementation start.

## 4. Design (PROPOSED)

### 4.1 A — Read-cost cuts, result-identical, all modes

- **A1a Bounded latest-final read.**
  - Rewrite `latest_final_open_ms` as `SELECT o.open_ms … ORDER BY o.open_ms DESC LIMIT 1`, with the same predicates and `scalar_one_or_none`.
  - The existing partial index `market_candles_final (symbol, open_ms) WHERE kind = 'CANDLE' AND is_final` (`0004:61-62`) can then be walked backwards, stopping at the first visible final.
  - Cost is bounded by finals published after the watermark: none in forward mode, at most the remaining finals in a replay.
- **A1b Memoized evaluation preparation.**
  - `_prepare_evaluations` issues no SQL when nothing visible can have changed.
  - The engine keeps, per symbol, the last `latest_final_open_ms` result and recomputes (bounded SQL) only when:
    - a final `CANDLE` or `CONFIRMATION` publication for that symbol was seen since the last computation;
    - the decision time moved backwards;
    - the decision time reached the earliest close or availability time of a final that was seen but excluded by time.
  - Exactness requires that the engine saw every publication up to the watermark, in sequence order. The `SimulatedDriver` guarantees this. The recorded-step equivalence path (`replay/run.py:123-139`) does not, and always uses SQL.
  - The forward worker keeps SQL in this plan: A1a already bounds it, and it limits live behavior changes to A1a, A2, A3 and A4.
- **A2 Instrument cache.** `MarketView.instrument` caches non-null snapshots by observation id in a bounded LRU (256 entries). The rows are immutable and referenced instruments are never deleted (§2.3).
- **A3 Trigger-quote reuse.** When `latest_quote` for the trigger's symbol returned the trigger publication's own row (same sequence), reuse it instead of `quote_at_sequence`. Both read the same columns from the same join.
- **A4 Summary inside the step transaction.**
  - Run the existing seven summary statements unchanged inside the step transaction, after `persist` and before `recheck`.
  - Adopt the result into memory only after COMMIT, as today.
  - The result is identical because only the execution role writes those tables (§2.3).
  - This removes the third connection and is a prerequisite for B1: a separate connection cannot see a batch's uncommitted writes.
  - `start()` and `reconcile()` keep `refresh_summary()`.

### 4.2 B1 — Batched step transactions (replay only)

- **Batch shape.** The `SimulatedDriver` in `REPLAY` activation groups consecutive steps into one transaction.
  - A batch closes after N steps (default 500), after 250 ms of wall time, or before any operation that must see committed data.
  - All of these stay far inside the 2 s statement, 3 s idle-in-transaction and 10 s lease limits.
- **Authority.**
  - At batch start: the lease `FOR KEY SHARE`, `account_state FOR UPDATE`, and the fencing-epoch check.
  - Before COMMIT: `recheck`.
  - Every step still re-reads `account_state` inside the batch (its row is already locked). B2 replaces that read with the carried row.
  - The guarantee is unchanged: no write is durable unless authority is valid at COMMIT.
  - Lease renewal continues on its own connection. `FOR KEY SHARE` conflicts only with `FOR UPDATE`, and the renewal `UPDATE` takes `FOR NO KEY UPDATE` (§8).
- **Checkpoint.** Written once per batch, with exactly the values the batch's last step computed. The final checkpoint row equals the per-step path's.
- **Commit mode.** `SET LOCAL synchronous_commit = off` is issued only on the replay batch path. It lasts until the end of that transaction (§8).
  - A PostgreSQL crash can lose the last few committed batches but never corrupts or reorders them (§8).
  - Replay restarts from reset anyway, so nothing is lost that a rerun would not recreate.
- **Memory.** Each step adopts its memory changes when it finishes, because the next step needs them. A batch-start snapshot is restored if the batch fails; the replay run then fails, as today.
- **Structural isolation.** Batching is refused unless:
  - `activation.kind == "REPLAY"`,
  - `ASL_REPLAY_ISOLATED=1`,
  - and the database name starts with `asl_m1_replay_`.
  
  The forward worker (`worker.py`) never constructs it.
- **Toggles.** The replay runner and the probe take `--batch-steps` (1 = today's per-step path) and `--state-reuse on|off`. The report JSON records the engine mode used: batch size, state reuse and verification.

### 4.3 B2 — State reuse (replay only)

In replay the engine is the only writer of every table a step reads (§2.3). A table's rows therefore change only through the engine's own statements.

- **Cached reads:**
  - holdings, live positions, open orders, active obligations, latches, breaches, today's daily reference, pending entry signals and the summary are cached as immutable snapshots;
  - each step receives fresh copies, so in-place edits by the phase code never leak between steps;
  - the `account_state` row is carried through the batch; `bump_account` and `update_nav` already update it in place (`store.py:290-302, 662-670`).
- **Invalidation.**
  - A connection-level statement listener classifies every non-`SELECT` statement by its target table.
  - Writes to `valuations`, `execution_steps`, `execution_checkpoints` and `execution_incidents`, and `update_nav` on `account_state`, invalidate no cached read. The summary's `last_valuation_at` becomes `max(previous, valued_at)` after a valuation insert.
  - Any other write, or any statement the listener cannot classify, invalidates all caches. The next step then reads everything from the database.
- **Latest quote in memory.**
  - `publications_after` also returns the full quote columns (`QUOTE_COLUMNS`) for quote publications.
  - The replay `MarketView` keeps, per symbol, the newest seen quote by `(source_event_at, received_at, sequence)`. It holds back any quote whose event time is beyond `at + QUOTE_EVENT_LEAD` until the decision time allows it.
  - This reproduces `latest_quote` exactly when every publication up to the watermark was seen and `at` is monotonic, as in the `SimulatedDriver`. Otherwise SQL is used.
- **Result:** a quote step that writes nothing issues no SQL. A `HIGH_WATER` step issues its three writes. After a fill, order, position or obligation write, the next step re-reads.
- **Scope:** B2 changes where a replay step's state comes from, not how the phases decide. The phase code stays shared with the forward engine. The forward engine keeps reading state inside its fenced transaction on every step.

### 4.4 Verification mode and step-trace digest

- **Verification mode.** `ASL_REPLAY_VERIFY=1` (replay only). After every step, inside the transaction, it re-reads through the existing SQL and fails with `IntegrityFailure("replay_cache_divergence:<item>")` on any difference:
  - every cached state read (via the existing `store` functions);
  - the summary (the seven existing statements);
  - `latest_quote` and `latest_final_open_ms`;
  - the carried account row.
- **Step-trace digest.** A new read-only `fingerprint.trace(connection)` hashes, excluding `recorded_at`, lease epochs and identity-column values:
  - `execution_steps`: trigger, sequence, decision time, watermark, eligibility, outcome;
  - `execution_incidents`: code, symbol, event, time, detail;
  - `position_events`;
  - `order_events`;
  - the final `execution_checkpoints` row.
  
  The replay report includes it next to the fingerprint.

### 4.5 Rejected alternatives

- **Writing `HIGH_WATER` valuations less often.** It would change the drawdown audit trail and the forward engine's evidence; that is a semantic change, not throughput work.
- **New indexes for replay.** Not needed: A1a uses an existing partial index, and B2 removes the other reads.
- **`fsync = off` or a cluster-wide `synchronous_commit` setting.** Cluster-wide and not scoped to the replay code path; `SET LOCAL` in replay batches is enough.
- **A sharper `needs_step` pre-check.** It would duplicate the valuation, latch and breach logic outside the phases; B2 gets the same saving through the shared phase code.
- **psycopg pipeline mode for writes.** Unverified with SQLAlchemy 2.0.54; not needed for the estimates below.
- **Incremental replay loading.** Rejected in 0014 §3; unchanged.

### 4.6 Estimates (INFERRED, not measured; I0–I3 replace them)

These refine the figures given in chat before the plan was written.

| After | Statements per no-effect step | Estimated ms per step | Estimated full run |
|---|---|---|---|
| Today | 27 + COMMIT, 3 connections | about 24 | about 6 h |
| A | 22 + COMMIT, 1 connection; bounded candle read | 17–20 | 4–5 h |
| A + B1 | about 19; COMMIT, fence and checkpoint per batch; async commit | 12–15 | 3–4 h |
| A + B1 + B2 | 0 (effect step: 3 writes) | 0.2–0.5 no-effect; 1.5–2.5 effect | 12–30 min |

The last row assumes about half of the steps are `HIGH_WATER` steps while positions are open. It may or may not meet 20 min; OD-B covers a miss.

## 5. Scope and exclusions

In scope:
- `app/execution/engine.py`, `market_view.py`, `driver.py`, `store.py` (only if a listener hook or helper is needed)
- `app/replay/run.py`, `fingerprint.py`
- tests, harness and probe tooling
- contract sentences in [PAPER_EXECUTION](../../PAPER_EXECUTION.md) (replay batching, state reuse, report fields) and [TESTING](../TESTING.md)
- normal deployment of the rebuilt engine images

Excluded:
- schema changes, grants and new roles
- strategy, risk, fill, valuation and eligibility semantics
- the market worker and the M2 read path
- activation and worker enabling
- M4 work
- the pending-signal index (§2.4, left to M4)

## 6. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| T0 | Baseline recorded before any engine change: fingerprint and trace digest for `gapped-stop`, `quiet` and a fixed density window (`T0 − 150 h` to `T0 + 48 h`, which includes both entries); probe statistics at today's code | I0 `ReplayBaseline` and `ReplayProbe` phases |
| T1 | A1a: the same value as today's SQL for visible, conflicting, confirmed and late finals. With 1,000 stored finals ahead of the watermark, `EXPLAIN (ANALYZE, FORMAT JSON)` reads at most 1,001 rows from `market_candles_final` (vs. all stored finals now), and at most 5 at the live watermark | `tests/test_m3_market_view.py`, real PostgreSQL |
| T2 | A1b: equals SQL on every step in verification mode; SQL is always used by the recorded-step path | verification runs (T9) plus a unit test of the recompute triggers |
| T3 | A2: equals SQL; the LRU is bounded; null results are not cached | unit plus real-PostgreSQL test |
| T4 | A3: identical row to `quote_at_sequence`, including a late-arriving older event (no reuse) | `test_m3_market_view.py` |
| T5 | A4: a failure after the summary and before COMMIT leaves `memory.summary` unchanged; forward summaries are equal to the post-commit query | `test_m3_engine.py` fault hook |
| T6 | No result change: `gapped-stop` fingerprint `2500c8d1…61e`; T0 digests reproduced after each increment; full regression with no skips | `Regression`, `Replay`, `ReplayBaseline` phases |
| T7 | B1: batch sizes 1, 7 and 500 give identical fingerprints and digests. Lease loss mid-batch fails the recheck, leaves no partial batch, and fails the run with `LostAuthority`. `SHOW synchronous_commit` is `off` inside a replay batch and `on` in a forward step. Lease renewal succeeds while a batch holds `FOR KEY SHARE` | `test_m3_replay.py` |
| T8 | B1/B2 structurally unavailable to forward and fixture activations, outside `ASL_REPLAY_ISOLATED=1`, or outside `asl_m1_replay_` databases | `test_m3_replay.py` negative cases |
| T9 | B2: verification mode passes on `gapped-stop`, `quiet`, the restored market-dump replay and the density window (≥ 20,000 steps with open positions, including fills and stop, time and trend exits). A statement the listener cannot classify invalidates all caches | `ReplayVerify` phase plus unit tests |
| T10 | B2 latest quote equals SQL, including a late-arriving older event and a quote beyond the event-time bound | `test_m3_market_view.py` |
| T11 | `PerformanceReplay`: two runs ≤ 20 min each, identical fingerprints and digests | `PerformanceReplay` phase |
| T12 | Forward engine: the 60-minute workload stays within M3 budgets (p95 ≤ 750 ms, p99 ≤ 1.5 s, RSS < 256 MiB, < 10 MiB growth); worker faults pass | `PerformanceEngine`, `WorkerFaults` |
| T13 | Measurements recorded after I0, I1, I2 and I3: statements and ms per no-effect and effect step, steps per simulated second, share of effect steps | `ReplayProbe` output in §18 |

## 7. Invariants, concurrency and failure cases (PROPOSED)

- **Invariants:**
  - The M3 financial invariants hold after every committed batch and, in verification mode, after every step.
  - Fingerprint and trace digest equal the per-step path.
  - Idempotent UUIDv5 identifiers and `ON CONFLICT` behavior are unchanged.
- **Authority:** no replay write is durable unless the lease and fencing epoch are valid at COMMIT. The forward engine keeps its per-step fence and recheck.
- **Concurrency:** replay has one writer. Lease renewal runs concurrently on its own connection and is not blocked (T7).
- **Failure cases:**

  | Failure | Effect |
  |---|---|
  | Python exception mid-batch | Rollback; memory snapshot restored; run fails |
  | Lost authority | Recheck fails; rollback; run fails |
  | DB restart or connection loss | Run fails; async commit may drop the last committed batches (bounded by the WAL writer interval), which a rerun recreates from reset |
  | Idle-in-transaction or statement timeout | Prevented by the 250 ms batch cap; if hit, rollback and fail |
  | Cache divergence (verification mode) | `IntegrityFailure` |
- **Crash recovery:** the forward worker's recovery (reconcile, adopt exits, expire entries, rebuild memory, catch up) is unchanged. A4 adopts the summary only after COMMIT, as today.
- **Isolation:** replay guards are unchanged. Batching, state reuse and `SET LOCAL synchronous_commit` are reachable only through the guarded replay path (T8).

## 8. Official sources and versions

- **PostgreSQL 17.11** (`compose.yaml:5`, `postgres:17.11-alpine3.24`). Read 2026-09-29:
  - [Asynchronous commit](https://www.postgresql.org/docs/17/wal-async-commit.html). The risk is data loss, not corruption. Recovery replays WAL in commit order to a self-consistent state. The commit mode is selectable per transaction. The risk window is at most three times `wal_writer_delay`.
  - [SET](https://www.postgresql.org/docs/17/sql-set.html). `SET LOCAL` lasts until the end of the current transaction, committed or not. Outside a transaction block it only warns.
  - [Row-level locks, Table 13.3](https://www.postgresql.org/docs/17/explicit-locking.html#LOCKING-ROWS). `FOR KEY SHARE` conflicts only with `FOR UPDATE`. An `UPDATE` that does not take `FOR UPDATE` takes `FOR NO KEY UPDATE`. The execution lease renewal is therefore not blocked by a step's `FOR KEY SHARE`; the M3 worker already relies on this.
  - **Not verified from documentation:** the join limit of the min/max index optimization (§2.2). T1's `EXPLAIN` settles it.
  - At implementation, confirm that `asl_execution` may `SET LOCAL synchronous_commit` in the replay cluster (T7).
- **SQLAlchemy 2.0.54** (`services/engine/uv.lock:523-524`). Read 2026-09-29:
  - [Connection pooling](https://docs.sqlalchemy.org/en/20/core/pooling.html). `pool_pre_ping` emits a ping equivalent to `SELECT 1` at every checkout. Reset on return rolls back the connection.
  - At implementation, verify the `ConnectionEvents.before_cursor_execute` listener API against the installed version and record it in [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md).
- **psycopg 3.3.6** (`uv.lock:379-380, 396-397`). Driver-level round trips per transaction are measured in I0, not assumed.
- **No new dependency.**

## 9. Data and trust-boundary changes

- **Schema:** no migration, role or grant change.
- **Replay only:** `SET LOCAL synchronous_commit = off` in replay batch transactions, in isolated `asl_m1_replay_` databases.
- **Replay report:** new fields for the engine mode and the trace digest. Labels ("MODELED REPLAY — NOT THE OWNER'S ACCOUNT", cost-scenario labels) are unchanged.
- **Forward engine:** fewer statements per step (A1a, A2, A3, A4). The same fence, lock order, recheck and in-transaction state reads remain.
- **Network and secrets:** no new network paths, secrets or credentials.

## 10. Proposed file edits

- `services/engine/app/execution/market_view.py`:
  - A1a query;
  - A2 cache;
  - `publications_after` quote columns (B2);
  - a replay latest-quote tracker (B2).
- `services/engine/app/execution/engine.py`:
  - A1b memo;
  - A3;
  - A4;
  - batch-aware `handle` (B1);
  - cached state source and verification (B2).
- `services/engine/app/execution/driver.py` — batch control (B1).
- `services/engine/app/execution/store.py` — only if a statement-classification helper belongs there.
- `services/engine/app/replay/run.py`:
  - `--batch-steps`, `--state-reuse` and verify options;
  - report fields;
  - guards.
- `services/engine/app/replay/fingerprint.py` — `trace()`.
- `services/engine/tests/`:
  - `test_m3_market_view.py`, `test_m3_replay.py`, `test_m3_engine.py`;
  - `m3_performance.py`: `replay-probe` with a window and a step or time limit, plus statement counters (test image only).
- `tools/m3-acceptance.ps1` — new phases `ReplayBaseline`, `ReplayProbe` and `ReplayVerify`; `PerformanceReplay` reports digests.
- Docs:
  - `PAPER_EXECUTION.md`, `TESTING.md`, `DECISIONS.md` (OD-A, OD-B);
  - `COMMANDS.md`, `INTEGRATION_EVIDENCE.md`;
  - `STATUS.md`, `docs/README.md` (inventory);
  - this plan.
- ExecPlan 0015 gets a reconciliation note at M4 start (§14).

## 11. Implementation sequence (PROPOSED)

Each increment is committed separately and must reproduce the T0 baseline before the next one starts.

- **I0 — Instrument and baseline (no engine behavior change).**
  - Add `trace()`, the probe and the phases.
  - Record T0 digests and probe statistics at `c96726c` engine code.
  - Probe statistics are statement counts per step by table and kind, round trips, ms per no-effect and effect step, and steps per simulated second.
- **I1 — A1a–A4.**
  - T1–T6; probe.
  - Also T12, because A changes the forward path.
- **I2 — B1.** T7, T8, T6; probe.
- **I3 — B2.** T9, T10, T6; probe.
  - Profile-driven fixes confined to replay-only code and keeping T6 may be added here.
  - Anything broader is a new plan.
- **I4 — Gate.**
  - Full isolated sequence (§12) including `PerformanceReplay` (T11).
  - If T11 fails, record the figures and stop for OD-B.
- **I5 — Normal deployment** (§13), then documentation closure.

## 12. Verification commands (PROPOSED — the new phases are not implemented)

Isolated run `rt-<date>`, detached, Windows PowerShell 5.1:

```powershell
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Prepare
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Build
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Checks
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Regression
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase WorkerFaults
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Replay
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase ReplayBaseline     # new: T0/T6 digests
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase ReplayVerify       # new: T9 verification runs
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase ReplayProbe        # new: T13 statistics
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase PerformanceReplay  # T11
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase PerformanceEngine  # T12 (about 65 min)
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Snapshot
./tools/m3-acceptance.ps1 -RunId rt-<date> -Phase Stop
```

Optional, owner's choice: one full-week per-step run (`--batch-steps 1 --state-reuse off`, about 6 h) to compare full-week digests with the fast path.

## 13. Normal deployment and rollback (PROPOSED)

- **Procedure:** follows the [deployment procedure](../../OPERATIONS.md#milestone-completion-deployment), as ExecPlan 0014 did, because A changes code in the running `api` and `market-worker` images (`MarketView` is used by the risk view and live marks).
  1. Protected backup with checksum.
  2. `:pre-0017` image tags.
  3. Frozen builds of migrate, api, market-worker and execution-worker.
  4. A no-op migration.
  5. Recreate api and market-worker; the execution worker stays built but not started, and `asl_execution` stays NOLOGIN.
  6. Verify running source hashes, readiness, reconciliation, collection and the sign-in page.
- **Unchanged state:** public collection stays as it is. No account, activation, approval or pause state changes.
- **Rollback:** image-only. Re-tag `:pre-0017` and recreate api and market-worker; there is no schema change.

**Rechecked after M4 (2026-09-30, PROPOSED).**
- **Current normal app**, as recorded by ExecPlan 0015 §16 and ExecPlan 0018 and to be re-inspected before deploying. M4 is deployed inert: the API and market worker from `be61a32`, the web from `0db0a2a` (ExecPlan 0018), schema `0006_m4_fixed_pilot`. The execution, evaluation and pilot-admin images are built but not started, and `asl_execution` and `asl_evaluation` are NOLOGIN.
- **Build source.** This deployment builds from the verified PR #6 head, which contains both M4 and 0018. Its `services/engine/app` tree equals the gate build `499bc71`.
- **Deploy first, then merge.** The standing rule deploys the verified PR commit to the normal app and merges afterwards; both need the owner's approval in chat.
- **Steps:**
  1. Protected `pg_dump` with its SHA-256.
  2. `:pre-0017` tags of the running engine-code images: api, market-worker, migrate, and the built execution, evaluation and pilot-admin images.
  3. Frozen builds of those images from the PR head.
  4. `migrate`, a no-op at `0006`.
  5. Recreate only api and market-worker. The web is untouched, since 0017 changes no web code, and no worker is started.
  6. Verify:
     - the running source hashes against the PR head;
     - readiness, schema `0006` and reconciliation;
     - both public feeds connected with quotes flowing;
     - zero approvals and experiments unchanged, and both identities still NOLOGIN;
     - the app pages.
- **Rollback.** Unlike `:pre-m4`, the `:pre-0017` images are valid at schema 0006, so rollback is image-only: re-tag `:pre-0017` and recreate api and market-worker.

**Normal deployment — VERIFIED 2026-09-30.** The owner approved it in chat ("Deploy, then merge"). It ran from this worktree at the pushed PR head `2f7973a`, with the primary checkout's `.env` and `ASL_SECRET_DIR`; no secret value was read. The commands are in [COMMANDS](../COMMANDS.md#verified-execplan-0017-normal-deployment--2026-09-30).
- **Host state first (OBSERVED).**
  - The host had rebooted at 07:50 UTC, and Docker Desktop was not running. The four normal containers had exited with code 0 at about 07:43 UTC and did not restart on their own.
  - The last market publication was at 04:08:10 UTC, so collection had already stopped about 4 h before.
  - Docker Desktop was started at 08:19:45 UTC, and the engine answered at 08:19:53.
  - The existing PostgreSQL container was started unchanged at 08:21:04, for the preflight and the backup. No writer was running.
- **Preflight (08:21 UTC)** matched the recorded M4 state.
  - Images: API `2835309c…`, market worker `a8138cbb…`, web `3206fdae…`, migrate `3425bfb3…`, execution worker `ca763129…`, evaluation worker `a400ed3f…`, pilot-admin `c0b20689…`.
  - Schema `0006_m4_fixed_pilot`.
  - Zero approvals, experiments, experiment events, reports, orders, fills, positions and latches.
  - `asl_execution` and `asl_evaluation` NOLOGIN; lease epoch 0.
  - The account initialized, not paused, and with no reconciliation failure. The database was 781 MB.
- **Backup (08:22:22–08:22:44).** `pg_dump -Fc` of `asl`, 149,664,201 bytes, SHA-256 `efd344d0d3c30e4dd199de87f6aeaa578ad3d535ff7084eb9259bca51b3c1fce`.
  - The checksum matched inside and outside the container.
  - The backup is in the primary checkout's `.cache/deployments/replay-throughput-20260930a/`, whose ACL grants the owner account only.
  - A first attempt wrote nothing, because Git Bash rewrote the container path; it left only the empty folder.
- **Rollback tags.** The images above were tagged `:pre-0017`: API, market worker, migrate, and the execution, evaluation and pilot-admin workers.
- **Build (08:23:14–08:23:22).** Frozen builds of migrate, API, market worker and the execution, evaluation and pilot-admin workers.
  - The new IDs are: API `4fba1a87ba90…`, market worker `73df98a623ee…`, migrate `a51828730…`, execution worker `5b02dbe11ce8…`, evaluation worker `6e2d4e6a117c…`, pilot-admin `c62ac1385949…`.
  - Every layer came from the `rt-0929f` build cache: the image creation time is 2026-09-29T18:07:19Z, the gate's build.
- **Source identity (VERIFIED).** A SHA-256 was taken over the line-ending-normalized hashes of the 82 Python files under `app/` and `alembic/`.
  - It is `144b776beaa5b4e909b540d5ff9f4099c0f283bbbf8c0c5f51029a450f4d553f` in the new API and market-worker images, in the gate's tested image (`asl-m3-rt-0929f-recovery-api`) and in the PR head's tree.
  - M4's previous API image gives `9ca979dc…` over 81 files; `replay_path.py` is the new one.
- **Rollout (08:24:26–08:24:57).**
  1. `migrate` was a no-op at head.
  2. The API and the market worker were recreated, and both became healthy.
  3. The existing web container (`3206fdae…`, ExecPlan 0018) was started unchanged.
- **State after (VERIFIED, 08:25 UTC).**
  - Readiness 200; reconciliation as `asl_api` OK (cash 10000.00000000, reserved 0); schema `0006_m4_fixed_pilot`.
  - Approvals, experiments, orders, positions and latches still 0; both identities NOLOGIN; lease epoch 0.
  - No execution-worker, evaluation-worker or pilot-admin container.
  - Both feeds `CONNECTED` with usable quotes. The first new publication was at 08:24:41.93 UTC, and there were 80 in the first 40 s.
  - `/`, `/system`, `/approvals`, `/experiments`, `/risk?mode=FORWARD_PAPER` and `/orders?status=ALL&symbol=ALL` returned 200.
  - The System page in the in-app browser read: Account funded, Market data ready, Model runtime unconfigured, Paper trading disabled, Evaluation reports disabled, Paper execution worker not running.
  - No sign-in, funding, approval or activation was performed.
- **Collection gap.** Collection was down from 04:08:10 to 08:24:41 UTC while the host was unavailable. The deployment kept the worker down only from Docker's start to the rollout (08:19:53–08:24:36).

## 14. Effects on the forward engine and M4

- **Forward engine:**
  - It gains A1a (bounded growth of the candle read), A2, A3 and A4 (the summary no longer takes its own pooled connection after each step), with identical results.
  - B1, B2 and asynchronous commit are unreachable from `worker.py` (T8).
  - Its per-step authority model is unchanged.
- **M4 ([ExecPlan 0015](0015-evaluation-fixed-pilot.md)), planned and not authorized:**
  - Its §4.3 item 5 reruns the seven-day `PerformanceReplay` with M4 capture. It inherits this plan's result and the OD-B budget.
  - It edits the same files (`engine.py`, `app/replay/run.py`, `fingerprint.py`, `scenarios.py`, driver deadlines). This plan should land first.
  - B2's invalidation must cover M4's new engine-read tables, owner-control inputs replayed as timed events, and `HOURLY` capture writes. Unknown statements already invalidate everything, so M4 fails safe, but it should extend the whitelist deliberately and rerun T9.
  - M4's migration is the natural place for the pending-signal partial index (§2.4).
  - M4's H1/H2 cost-sensitivity replays of a restored week benefit directly.
  - At M4 start, add a reconciliation note to 0015 (§4.3 item 5, file list, budget reference).

### 14.1 Integration with M4 (rebase, 2026-09-29) (IMPLEMENTED)

The branch was rebased onto `claude/m4-fixed-pilot` (`10b48b1`) at the owner's decision (§16). The pre-rebase history, whose commits §18.1–18.5 cite, is kept as the branch `claude/replay-throughput-pre-m4` (`b9ca255`).
- **Summary (A4) and M4's run state.**
  - `load_summary` also reads M4's run summary, inside the step transaction.
  - The premise that this equals a read after COMMIT now covers only the tables the execution role writes. Owner requests, top-ups, approvals and FINAL reports come from other roles. M4's `poll()` refreshes the summary once per worker loop when any of them changed, which also covers a request committed while a step ran.
  - `poll()` and the `RunSummary` fields `pending`, `completion_pending` and `recheck` are unchanged.
- **Phase order.** The shared phase runner (renamed `StepContext.phases`, because M4's `StepContext` has a `run` attribute) runs M4's order: owner requests, fills, expiries, protection, flatten, evaluations, exit orders, valuation, capture, start and resume, entries, housekeeping, run state, checkpoint.
- **Timed owner controls.** `SimulatedDriver` commits the open replay batch before each timed input.
  - The input is written on another connection under the experiment row lock, which the batch may hold.
  - The steps after the input must read it.
- **Other flushes.** `lease_started` (M4's downtime and segment records) commits an open batch first, as `reconcile` and `shutdown` do.
- **Checkpoint jump.** After M4's run-start checkpoint jump, the engine rebuilds its quote tracker and final-candle memo, because the driver skips the jumped publications. The jump needs a live market view, which replays do not use.
- **B2 and M4's tables.**
  - Migration 0006 adds only BEFORE guard triggers, so the single-writer premise holds.
  - Engine writes to `experiments`, `experiment_events`, `evaluation_marks` and `risk_latch_resolutions` are not self-contained, so they invalidate the cache.
  - Every `HOURLY`, `STARTUP` or `RESUME` valuation is written together with one of those rows, so the summary is reloaded after it.
  - A batch reuses only the absence of an experiment. A present experiment is loaded and locked in every step, because the step changes its `Run` object in place.
  - Verification compares the run summary as well.
- **Fingerprint.** M4 extends the replay fingerprint with its tables and `run_id` columns. The report therefore also records `m3_fingerprint_sha256` over M3's columns, and `gapped-stop` must keep `2500c8d1…` there. `ReplayBaseline` and `ReplayVerify` add M4's `pilot-lifecycle` fixture and compare its FINAL report hash.
- **Not done.** Migration 0006 did not add the pending-signal partial index (§2.4). It remains a follow-up for a later migration.

## 15. Q01–Q10 (affected gates)

| Gate | Applicability |
|---|---|
| Q03 Data correctness | Applicable: T1–T10 (no result change, verified equality) |
| Q05 Reliability | Applicable: batch failure, lost authority, crash and timeout cases (§7) |
| Q06 Performance | Applicable: T11, T12, T13 |
| Q07 Automated verification | Applicable |
| Q09 Deployment | Applicable (§13) |
| Q10 Maintainability | Applicable: contract sentences, toggles, digest, this record |
| Q01, Q02, Q04, Q08 | Not affected: no UI, secret, authority or observability change beyond the replay report fields |

## 16. Decision log

- 2026-09-29: the 0014 "steps" figure counts effect-bearing step records; per-transaction cost is about 24 ms (§2.1).
- 2026-09-29: rejected cutting `HIGH_WATER` valuations, new indexes, cluster-wide durability settings, a duplicated pre-check and pipeline mode (§4.5).
- 2026-09-29: owner decisions OD-A (scope A + B1 + B2) and OD-B (keep 20 min; decide after measuring).
- 2026-09-29: A1b stays off in the forward worker for this plan, which limits live changes to A1a–A4. Revisit only with measured need.
- 2026-09-29 (implementation): A1b moved into B2. The final-candle memo is built from the final-candle publications the engine sees, not from memoized SQL results. It is active only on the fast path with state reuse. The per-step path therefore issues exactly today's reads, plus A1a–A4, and stays the comparison reference.
- 2026-09-29 (implementation): the fast path is also allowed for FIXTURE activation in disposable `asl_m1_` test databases, not only REPLAY; this amends §4.2 and T8.
  - **Reason.** The regression suite's scenarios (fills, partial fills, stop, time and trend exits, latches, breaches, catch-up, restarts) can then run on the fast path with per-step verification (`ASL_TEST_FAST_PATH=1`). That is far broader T9 evidence than the replay fixtures alone.
  - **Unchanged.** MAIN (forward) activation is still refused, and so is any non-disposable database.
- 2026-09-29 (implementation): batching is scoped to `SimulatedDriver.run`.
  - Direct `handle` and `timer` calls commit each step. The same code path runs with one step per batch.
  - A failed run aborts the open batch. Memory, including the new `last_trigger_at`, returns to the batch start. The driver clock resumes from there.
- 2026-09-29 (implementation): B1 and B2 were implemented in one change. They share the batch machinery in `app/execution/replay_path.py`.
  - They are verified and measured separately through the engine modes. `batched` is B1 only (`--state-reuse off`), and `fast` is B1 plus B2.
  - The per-step path is `--batch-steps 1 --state-reuse off`.
- 2026-09-29 (M4 integration): rebase onto M4 before it merges. The owner's decision was relayed by the M4 session and confirmed by the owner in this session's chat ("Rebase onto M4 now").
  - The pre-rebase head was pushed as an archive branch, so the commits cited in §18.1–18.5 stay reachable.
  - PR #6 is updated with `--force-with-lease`.
  - The integration is described in §14.1. The comparison reference is a new per-step baseline on M4's engine (§18.6), not `rt-0929a`, because M4 changed the fingerprint.

## 17. Progress

- 2026-09-29 PLANNED: read-only investigation of `engine.py`, `market_view.py`, `store.py`, `driver.py`, `replay/run.py`, `fingerprint.py`, the migrations and the `bq-0929a` evidence; recommendation presented in chat; owner chose "do the recommended".
- 2026-09-29: PR #5 merged at the owner's request ("merge it and start implementing 0017"). The M4 implementation (ExecPlan 0015) was running at the same time in the primary checkout on `claude/m4-fixed-pilot`, and its isolated stacks shared the Docker host during these runs.
- 2026-09-29 IMPLEMENTED I0 (`41b7cd4`): the step-trace digest, `ReplayProbe` tooling and the `ReplayBaseline`, `ReplayVerify` and `ReplayProbe` phases. No engine change.
- 2026-09-29 IMPLEMENTED I1 (`9c97e5d`): A1a–A4 and the T1, T3, T4 and T5 tests.
- 2026-09-29 IMPLEMENTED I2/I3: B1 and B2 (`replay_path.py`, engine and driver hooks), runner modes, and the T7–T10 tests. The regression phase adds a fast-path rerun.
- 2026-09-29 PR #6 opened from `claude/replay-throughput`. At 16:33 UTC the normal app was still on the 0014 images and schema `0005_m3_paper_broker`.
- 2026-09-29 VERIFIED: isolated gate `rt-0929d` (`16590e3`) passed every phase, ending with `PerformanceEngine` at 17:28 UTC (§18.5). Its stacks were then stopped with `-Phase Stop`; volumes and logs are kept.
- 2026-09-29 ON HOLD (owner: "hold as recommended and send the note"). The M4 branch `claude/m4-fixed-pilot` was in its final acceptance run with an owner-authorized inert deployment next.
  - **Why hold.** A trial merge conflicts in 7 files. Deploying 0017 first would be undone by M4's deployment from its branch, and deploying this branch after M4's migration 0006 would break API readiness. The owner chose to let M4 merge and deploy first.
  - **Then.** Merge `main` (with M4) into this branch and resolve the conflicts. Extend B2 to M4's tables and owner-control inputs, rerun the 0017 gate, and deploy once (§13). The M4 session was sent a coordination note.
  - **The M4 session's reply.** Its final run `m4f-0929b` (`10b48b1`) ran `PerformanceEngine` from 16:20 to about 17:30 UTC, overlapping `rt-0929d`, and records that overlap. Its inert normal deployment, including migration 0006, is expected about 19:30–20:30 UTC. No normal-project change may be made in that window.
  - **Merge requirement.** Keep M4's `ExecutionEngine.poll()` (a per-loop marker read that refreshes the summary; the worker and `SimulatedDriver` call it) and the `RunSummary` fields `pending`, `completion_pending` and `recheck`. Without them `needs_step` can skip committed owner requests. The fast path's cached summary must be refreshed by the same marker.

- 2026-09-29 REBASED onto `claude/m4-fixed-pilot` (`10b48b1`) at the owner's decision (§16). The pre-rebase head `b9ca255` is kept as `claude/replay-throughput-pre-m4`. The conflicts were resolved in 7 files, and the integration is described in §14.1.
  - **Baseline tooling.** A tooling commit on the rebased I0 records M3-column fingerprints and the `pilot-lifecycle` digests. The per-step baseline `rt-0929e` runs at that commit, from a separate detached worktree.
  - **Gate.** The gate `rt-0929f` runs on the integrated head (§18.6).
- 2026-09-29 PUSHED: PR #6 was force-pushed with lease on `be61a32`, M4's head after a test-tooling commit. The functional gate phases had passed on the same `services/engine/app` tree.
- 2026-09-29 VERIFIED: the rebased gate `rt-0929f` passed every phase.
  - The functional phases ran from 18:07 to 18:53 UTC.
  - `PerformanceReplay` took 429.5 s and 429.0 s.
  - `ReplayBaseline` fast and `ReplayVerify` matched `rt-0929e`.
  - `PerformanceEngine` measured p95 291 ms and p99 309 ms.
  - At the M4 session's request, the runner waited without load from 19:22 to 20:33 UTC while M4's measured phases ran.
  - The stacks were stopped at 22:08 UTC; volumes and logs are kept.
  - The M4 session deployed M4 inert to the normal project at 20:37–20:39 UTC from `be61a32`. This session did not touch the normal project.
- 2026-09-30 REBASED onto `main` `9e84eff` (owner: "ok, rebase when M4 is merged"). The M4 session merged M4 (#7, merge commit `7ae0217`) and ExecPlan 0018 (#8, `9e84eff`) at the owner's request.
  - `git rebase origin/main` dropped the branch's copy of the plan commit, which has the same patch-id as `559a9ee`.
  - The conflicts were in the docs indexes only: `README.md`, `COMMANDS.md` and `INTEGRATION_EVIDENCE.md`. Every section was kept, in date order.
  - `git diff 499bc71 HEAD -- services/engine/app` is empty. Under `services/`, the only difference is M4's `m4_pilot.py`.
  - The previous PR head differs from the new one exactly by `main`'s #7/#8 changes: the web, docs and 0018 plan.
  - PR #6 was force-pushed with lease on `e51f6f1`. It now shows 17 commits and 19 files, all 0017.
- 2026-09-30 DEPLOYED and VERIFIED on the normal app (§13), with the owner's approval in chat ("Deploy, then merge"). The API and market worker run the PR head `2f7973a`, whose source is byte-identical to the tested image; the web, schema and the inert M4 state are unchanged.
- NEXT: merge PR #6 as a merge commit (owner-approved, after the verified deployment).

## 18. Completion evidence

Isolated runs use `./tools/m3-acceptance.ps1 -RunId <run> -Phase <phase>` in Windows PowerShell 5.1, detached one phase after another. Logs are under `.cache/m3/<run>/` in the implementation worktree. §18.1–18.5 cite commits of the pre-rebase history, kept on `claude/replay-throughput-pre-m4`; §18.6 cites the rebased history. The M4 session's isolated stacks were running on the same Docker host during these runs, so timings carry that load. Digests do not depend on it.

### 18.1 Baseline — run `rt-0929a` (I0; engine code as on `main`) (VERIFIED)

- **Source.** The snapshot recorded `41b7cd4` at 13:37:10 UTC; the tree was clean at build.
  - The record's `commit` field reads `9c97e5d`: the harness read HEAD after I1 was committed.
  - The harness now takes the commit from the run's snapshot.
- **Digests** (`replay-baseline.json`, per-step engine):

  | Scenario | Fingerprint | Step trace |
  |---|---|---|
  | `gapped-stop` | `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e` (unchanged since M3) | `34899be83709f113ef3c1fe2e8a306eb954d7490a9bc36846830f681bdc14b49` |
  | `quiet` | `853759c8a9b0b9e45593553d6ea21bc9bf45e0b6bdb38eca61b4a655d65efa07` | `c2a69be08e933c367adca9a49f8c3f19f9d4abd3f784c76d523888083b207eb5` |
  | density window `T0 − 150 h` to `T0 + 48 h` | `1afd8ec49c05523f50cc0c87c8687bbf28ddfc8b36aa3033903a77fb196f84e7` | `4b969f85b1bbd53d3efe142b862f2cba5451517c755e42ccfa6eecf624b6394d` |

- **Density window** (`replay-baseline-density.log`):
  - Runtime: replay 1,545.4 s after a 307.9 s load.
  - Result: one BTC entry filled and the position still open; 2 entry signals and 2 trend-exit signals were evaluated.
- **Probe figures confirm §2.1 and §2.2** (per-step engine, one position open for 28,799 simulated seconds):

  | Steps | Count | Mean | p95 | Statements per step |
  |---|---|---|---|---|
  | open, no effect | 29,778 | 25.2 ms | 28.8 ms | 27.0 |
  | open, with effects | 27,842 | 27.4 ms | 31.2 ms | 30.0 |

  - **Step rate:** 2.001 steps per simulated second with the position open.
  - **Commits and connections:** 58,773 commits and 175,309 pool checkouts, three per step.
  - **Statement time, top four:**

    | Statement | Calls | Total | Per call |
    |---|---|---|---|
    | `max(open_ms)` candle read | 116,014 | 158.5 s | 1.37 ms |
    | latest quote | 116,014 | 122.0 s | |
    | pending entry signals | 116,014 | 69.1 s | |
    | instrument | 115,407 | 46.7 s | |

### 18.2 I1 — run `rt-0929b` (`9c97e5d`) (VERIFIED)

- **Build and checks.** Build and Snapshot ran at 13:45 UTC. All 8 checks exited 0: lint, typecheck, web unit, API check, Ruff, OpenAPI drift, format and web build.
- **Regression.** 173 passed and 1 failed.
  - The failure was the new T1 test's coverage assertion. It expected bar 3 to be the newest visible final at some grid point, which cannot happen: bar 3's late final is published after bar 4's.
  - Every one of the grid's equality checks against the replaced aggregate had passed first.
  - The expectation was corrected in `091d9ea`; the engine code is unchanged.
- **`ReplayBaseline -BaselineRun rt-0929a`.** Every digest matches the baseline (`matches_baseline: true`). The density window took 1,440.9 s.

### 18.3 I2/I3 — run `rt-0929c` (`3ec2729`) (VERIFIED)

- **Checks.** All exited 0.
- **Regression.** 181 passed, with no skips. The fast-path rerun (`ASL_TEST_FAST_PATH=1`: engine, replay, property and throughput suites) passed 42.
- **Digest comparisons** with `-BaselineRun rt-0929a`, covering `gapped-stop`, `quiet` and the 48 h density window:

  | Phase | Mode | Result | Density window |
  |---|---|---|---|
  | `ReplayVerify` | fast path, per-step verification | all digests match | 903.9 s |
  | `ReplayBaseline -ReplayMode fast` | B1 + B2 | all digests match | 88.7 s |
  | `ReplayBaseline -ReplayMode batched` | B1 only | all digests match | 765.0 s |

- **T13 figures** (48 h density window, one position open; M4 stacks active on the host):

  | Mode | Code | Replay | Open step, no effects | Open step, effects | Statements | Commits | Pool checkouts |
  |---|---|---|---|---|---|---|---|
  | per step (baseline) | `41b7cd4` | 1,545.4 s | 25.2 ms / 27.0 statements | 27.4 ms / 30.0 | 1,653,553 | 58,773 | 175,309 |
  | per step + A (I1) | `9c97e5d` | 1,440.9 s | 23.4 ms / 24.0 | 25.5 ms / 27.0 | 1,480,496 | 58,721 | 117,250 |
  | batched, B1 | `3ec2729` | 765.0 s | 12.0 ms / 21.3 | 13.6 ms / 24.2 | 1,320,678 | 3,288 | 61,818 |
  | fast, B1 + B2 | `3ec2729` | 88.7 s | 0.28 ms / 0.15 | 2.08 ms / 3.05 | 98,604 | 378 | 1,296 |

- **Fast-mode statement time.** Almost all of it is the three writes of a `HIGH_WATER` step:

  | Statement | Calls | Total |
  |---|---|---|
  | valuation insert | 27,837 | 11.2 s |
  | step record | 28,136 | 9.7 s |
  | account NAV update | 27,837 | 8.4 s |

### 18.4 Profile of the fast path — run `rt-0929p` (OBSERVED)

- **Method.** cProfile over the same 48 h window in fast mode, with identical digests. It is a scratch script, run through the harness's Compose helper, with the scratchpad file mounted read-only. It is not a repository tool.
- **Total.** 136 s under the profiler.
- **Where the time went:**
  - **Database round trips.** 46.6 s was psycopg waiting on the database.
  - **A classification bug.** 15.8 s was `TrackedConnection.execute` compiling every statement a second time. `getattr(statement, "text", str(statement))` evaluates its default eagerly.
  - **Other Python work.** Cache copies took 4.1 s, the per-publication `needs_step`/`next_deadline` about 8 s, and breach checks 5.1 s.
- **Fix.** `16590e3` reads `TextClause.text` directly.

### 18.5 Gate — run `rt-0929d` (`16590e3`)

Phase order: Build, Snapshot, `PerformanceReplay` first (the least concurrent load from this work), Checks, Regression, WorkerFaults, Replay, `ReplayBaseline -ReplayMode fast`, `ReplayVerify` (both with `-BaselineRun rt-0929a`), `PerformanceEngine`. The M4 session's stacks were running on the host throughout.

**T11 `PerformanceReplay` — PASSED (VERIFIED).** Two runs of the seven-day full-density dataset (1,815,038 publications) through the default replay (fast path: 500 steps / 250 ms batches, state reuse on). `passed: true`, `identical: true`.

| Run | Replay | Load | Fingerprint | Step trace |
|---|---|---|---|---|
| 1 | 409.81 s | 307.0 s | `cc611ce225907961377565429e61ffc3fc9ab5b4389fcac00f4515027b8d66ab` | `dd7b1915262f7718c055b5ace2872f7dca2b3e073f5d5b622a26788ec83c8f99` |
| 2 | 421.63 s | 324.6 s | same | same |

- **Budget.** Each run is 34–35% of the 20 min budget; replay time excludes the load, as declared in ExecPlan 0013.
- **Modeled outcome.** Both runs: 7 fills, all orders `FILLED`, 3 positions `CLOSED_WITH_DUST` and 1 `OPEN`, realized P&L −24.06443159 USDT under the hypothetical H1 cost scenario, 5 entry and 5 trend-exit signals, one `PROTECTION_UNAVAILABLE` start incident, no latches. These are modeled synthetic results, not performance evidence.
- **Probe, run 1:**
  - **Open positions.** Open for 460,859 simulated seconds, 76% of the week, at 1.612 steps per simulated second.
  - **Open steps:**

    | Open step | Count | Mean | p95 | Statements |
    |---|---|---|---|---|
    | no effects | 645,997 | 0.208 ms | 0.26 ms | 0.05 |
    | with effects | 97,035 | 1.799 ms | 2.17 ms | 3.06 |

  - **Totals.** 891,895 publications needed no step. Totals were 355,831 statements, 2,511 commits and 4,968 pool checkouts.
- **Per-step estimate.** At the baseline's per-step rate the same week would take roughly 5–6 h (INFERRED from §18.1: about 745,000 open steps at 25–27 ms).

**Other gate phases — all PASSED (VERIFIED).** Every phase ended `end ok` in `.cache/m3/rt-0929d-sequence.log`; the sequence ended `SEQUENCE DONE` at 17:28:51 UTC.

| Phase | Result |
|---|---|
| Checks | ESLint, `tsc --noEmit`, Prettier, web unit tests, web build, Ruff, the OpenAPI schema check and the generated API types check all exited 0 |
| Regression | 182 passed, no skips; mode guard `refused`: `FORWARD_PAPER` false, `HISTORICAL_RESEARCH` true, `OFFLINE_TEST` true; migration function matches. Fast-path rerun (`ASL_TEST_FAST_PATH=1` logged in the container; engine, replay, property and throughput suites): 43 passed |
| WorkerFaults (T12) | 30 kill cycles, pair, pause and database interruption; final lease epoch 12, lease held; `failed_checks: []`, `invariant_failures: []`, reconciliation `OK` |
| Replay (T6) | Runs 1 and 2 both `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e`; the restored market-dump replay produced `d61ca90661ffd289ad014926d0cdb95bb8af63bc96ccefaee95e0a33bee50a04` |
| `ReplayBaseline -ReplayMode fast` (T6, T7) | `gapped-stop`, `quiet` and the 48 h density window match `rt-0929a`; density window 78.16 s |
| `ReplayVerify` (T9) | the same three scenarios match `rt-0929a` with every reused value compared against its database read; density window 839.43 s |

**T12 `PerformanceEngine` — PASSED (VERIFIED).** The production `Worker.serve` loop ran in process for 3,600 s against the real-time synthetic feed (16:24:47 to 17:24:47 UTC). Container limits were 1 CPU and 512 MiB. The M4 session's own `PerformanceEngine` ran on the same host from about 16:20 to 17:30 UTC.

| Measure | Budget | `rt-0929d` | M3 gate (ExecPlan 0013) |
|---|---|---|---|
| Publication → commit latency, all measured steps | p95 ≤ 750 ms, p99 ≤ 1.5 s | 7,142 steps: p50 174 ms, p95 287 ms, p99 307 ms, max 328 ms | 7,144 steps: p50 176, p95 291, p99 311, max 337 ms |
| Steps with effects | same | 300 steps: p50 169 ms, p95 300 ms, p99 311 ms, max 322 ms | 300 steps: p95 287 ms |
| RSS | < 256 MiB; < 10 MiB growth in the final 30 min | max 63.34 MiB; growth 0.96 MiB (720 samples) | max 63.4 MiB; growth 0.5 MiB |
| CPU | — | 3.2% of the 1-CPU limit | 3.3% |

- **Scripted events.** BTC's `TIME_EXIT` at the 17:00 boundary and SOL's `PROTECTIVE_STOP` at the scripted dip each filled a modeled SELL. Both positions ended `CLOSED_WITH_DUST`. 829 step rows, 3 `PROTECTION_UNAVAILABLE` starts and 3 ends, no feed stall. Final invariants: `failed_checks: []`, `invariant_failures: []`, reconciliation `OK`.
- **Feed.** 7,680 quotes, 3,840 provisional and 2 final candles; publish p95 9.7 ms.
- **Reading.** Latency is still dominated by the worker's 250 ms poll interval, as it was at the M3 gate, so A's per-step saving does not show here.

### 18.6 On M4 — baseline `rt-0929e` and gate `rt-0929f` (rebased history)

**Sources.**
- **Baseline `rt-0929e`.** Built at `1d416e9`: the rebased I0 plus the M4-base tooling commit, so M4's per-step engine with only 0017's tooling.
  - It ran from a separate detached worktree, and its records were copied to `.cache/m3/rt-0929e` without secrets.
  - On the pushed history, the same commit is `4177f86`. The two differ only in M4's `services/engine/tests/m4_pilot.py`.
- **Gate `rt-0929f`.** Built at `499bc71` (snapshot `base_commit`).
  - The branch was then rebased onto `be61a32`. After that, `git diff 499bc71 <head> -- services/engine/app` is empty.
  - The later commits change docs, the host-side harness (the cross-build comparison of `pilot-lifecycle`) and M4's `m4_pilot.py`, which no 0017 phase uses.
- **Host load.** The M4 session's final acceptance run `m4f-0929c` shared the host throughout.

**T0 on M4 — `rt-0929e` `ReplayBaseline` (per step, VERIFIED).**

| Scenario | Fingerprint (M4 tables) | M3 columns | Portable | Step trace | FINAL report |
|---|---|---|---|---|---|
| `gapped-stop` | `3c948dc8660ae044846db747fc4d9483c54643b179d447d72af223b2c67774e1` | `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e` | `7a8558da…` | `34899be83709f113ef3c1fe2e8a306eb954d7490a9bc36846830f681bdc14b49` | — |
| `quiet` | `32c01c82d442d86298c9db9e501a5dce4478b870add5588f8799eea55da4a7ff` | `853759c8a9b0b9e45593553d6ea21bc9bf45e0b6bdb38eca61b4a655d65efa07` | `e50d48ca…` | `c2a69be08e933c367adca9a49f8c3f19f9d4abd3f784c76d523888083b207eb5` | — |
| `pilot-lifecycle` | `40ac6930c7104b751e63fb202a5b728d42bf74b4656438e0eae825650f791965` | `d4130198c142eb1ce47f9ae5b021ed3251181109fece9d23ce1e307e20132912` | `72c1af2372a81ce9699ed6b867458b6e947cafb7f09eda78c6e89df812486ad7` | `11963bf7d008a8038dc4fdcda6b11c9b1014cfcd015e19c9fe328e7dafa21181` | `5dbbfcd24d806999f2157d4a319186195af35b8a564ac6780112af15d8345602` |
| density, 48 h | `7764245849d615919a4d976d0488bed1b65246a2999c1e44fc44a6e68621d731` | `1afd8ec49c05523f50cc0c87c8687bbf28ddfc8b36aa3033903a77fb196f84e7` | `0e2b215c…` | `4b969f85b1bbd53d3efe142b862f2cba5451517c755e42ccfa6eecf624b6394d` | — |

- **Unchanged by M4.** `gapped-stop` keeps M3's value over the M3 columns. The M3-column fingerprints of `quiet` and the density window equal `rt-0929a`'s fingerprints (§18.1), and so do all three step traces.
- **Timing.** The density window took 1,752.94 s per step (`rt-0929a` on M3: 1,545.4 s).
- **Code identity.** `pilot-lifecycle`'s full fingerprint and FINAL report embed the code identity (the SHA-256 of `app/`). Other builds are therefore compared with it on the M3-column and portable fingerprints and the trace only.

**Gate `rt-0929f` — functional phases (VERIFIED).**

| Phase | Result |
|---|---|
| Checks (18:07–18:08 UTC) | ESLint, `tsc --noEmit`, Prettier, web unit tests and build, Ruff, the OpenAPI schema check and the generated API types check all exited 0 |
| Regression (18:08–18:46) | 254 passed, no skips (M1–M4 suites) |
| Fast-path rerun | 79 passed (`ASL_TEST_FAST_PATH=1` logged in the container). It covers the M3 engine, replay, property and throughput suites (including the owner-controls identity test) and the M4 engine, replay, property and report suites |
| Mode guard | `refused`: `FORWARD_PAPER` false, `HISTORICAL_RESEARCH` true, `OFFLINE_TEST` true; migration function matches |
| WorkerFaults (18:46–18:53) | 30 kill cycles, pair, pause and database interruption. Final lease epoch 13, lease held; `failed_checks: []`, `invariant_failures: []`, reconciliation `OK` |
| Replay (18:53) | Two default-mode (fast path) runs of `gapped-stop`: fingerprint `3c948dc8…`, M3 columns `2500c8d1…`, trace `34899be8…`, all equal to the per-step `rt-0929e` values |

The restored market-dump replay passed on its own source, `cc65fd89…`.

**T11 `PerformanceReplay` (18:56–19:22 UTC) — PASSED (VERIFIED).** It ran the default fast path (500 steps / 250 ms batches, state reuse on). `passed: true`, `identical: true`.

| Run | Replay | Load | Fingerprint (M4 tables) | M3 columns | Step trace |
|---|---|---|---|---|---|
| 1 | 429.53 s | 317.6 s | `18011c0e8d6eee05f76b7f99ca055a43798f4edf96b0392c2ececdf3d57f1198` | `cc611ce225907961377565429e61ffc3fc9ab5b4389fcac00f4515027b8d66ab` | `dd7b1915262f7718c055b5ace2872f7dca2b3e073f5d5b622a26788ec83c8f99` |
| 2 | 428.95 s | 319.56 s | same | same | same |

- **Budget.** Each run is 36% of the 20 min budget.
- **Unchanged decisions.** The M3-column fingerprint and the step trace equal the pre-rebase gate's (§18.5), so M4 and the rebase changed none of the week's decisions. The modeled summary is also the same: 7 fills, realized P&L −24.06443159 USDT under hypothetical H1, 3 positions `CLOSED_WITH_DUST` and 1 `OPEN`.
- **Probe, run 1:**

  | Open step | Count | Mean | p95 | Statements |
  |---|---|---|---|---|
  | no effects | 645,997 | 0.217 ms | 0.24 ms | 0.06 |
  | with effects | 97,035 | 1.900 ms | 2.28 ms | 3.07 |

  Totals were 365,697 statements, 2,587 commits and 5,046 pool checkouts (§18.5: 355,831, 2,511 and 4,968). The added statements are INFERRED to be M4's run-state reads, which repeat whenever a batch's cache is refilled.
- **Concurrent load.** It overlapped the M4 session's measured `PilotFaults`, which includes the 200-request control race. That session records the overlap.

**Hold.** At the M4 session's request, the runner waited without load from 19:22 to 20:33:43 UTC, when that session's final run `m4f-0929c` had finished. The owner's rule is that nothing else loads the host during measured phases. The wait was a local, uncommitted hold at the top of the harness, since removed; the committed harness is unchanged.

**T6, T7, T9 — `ReplayBaseline -ReplayMode fast` and `ReplayVerify`, both with `-BaselineRun rt-0929e` — PASSED (VERIFIED).** Both records show `matches_baseline: true` with no mismatches.

| Phase | Mode | `gapped-stop`, `quiet`, density | `pilot-lifecycle` against `rt-0929e` | `pilot-lifecycle` per step, same build | 48 h window |
|---|---|---|---|---|---|
| `ReplayBaseline` (20:33–20:42 UTC) | fast (B1 + B2) | fingerprint, M3 columns, portable and trace equal | M3 columns, portable and trace equal | equal on every digest | 79.6 s |
| `ReplayVerify` (20:42–21:02) | verify (per-step database cross-check) | same | same | equal on every digest | 796.12 s |

- **Build-specific digests.** `pilot-lifecycle` on this build has full fingerprint `b1979b54de98c8909ec13cea45b385a95a2ef2727446d855e222fddfc82787e8` and FINAL report `74cbebc4caf52ea7414a8fac0226611313daefba15e7a6bd584a9859acf12959`. The values are the same in fast, verify and per-step runs, and they differ from `rt-0929e`'s only through the code identity.
- **Speed.** The density window ran 22× faster in fast mode than per step on M4's engine (79.6 s against 1,752.94 s).

**T12 `PerformanceEngine` (21:02–22:07 UTC) — PASSED (VERIFIED).** The production `Worker.serve` loop ran in process for 3,600 s against the real-time synthetic feed (21:03:03 to 22:03:03 UTC). The container was limited to 1 CPU and 512 MiB, and no other measured workload was running.

| Measure | Budget | `rt-0929f` (rebased) | `rt-0929d` (pre-rebase) |
|---|---|---|---|
| Publication → commit latency, all measured steps | p95 ≤ 750 ms, p99 ≤ 1.5 s | 7,142 steps: p50 175 ms, p95 291 ms, p99 309 ms, max 323 ms | 7,142 steps: p50 174, p95 287, p99 307, max 328 ms |
| Steps with effects | same | 346 steps: p50 185 ms, p95 302 ms, p99 313 ms, max 320 ms | 300 steps: p95 300 ms |
| RSS | < 256 MiB; < 10 MiB growth in the final 30 min | max 64.74 MiB; growth 1.45 MiB (720 samples) | max 63.34 MiB; growth 0.96 MiB |
| CPU | — | 3.4% of the 1-CPU limit | 3.2% |

- **Scripted events.** BTC's `TIME_EXIT` at the 22:00 boundary and SOL's `PROTECTIVE_STOP` at the scripted dip each filled a modeled SELL, and both positions ended `CLOSED_WITH_DUST`. `PROTECTION_UNAVAILABLE` started 3 times and ended 3 times, and the feed never stalled. Final invariants: `failed_checks: []`, `invariant_failures: []`, reconciliation `OK`.
- **More effect steps.** The workload's time-exit boundary is the next wall-clock hour, so the two positions stayed open 57 minutes after ready, against 35 minutes in `rt-0929d`. The effect mix is otherwise identical. The only difference is valuations: 345 `VALUATION` and 335 `HIGH_WATER`, against 297 and 278.
- **One new `EXECUTION_DOWNTIME` incident.** It is M4's downtime disclosure at lease start, not a failure. The workload's setup lease (epoch 1, 384 steps) wrote its last checkpoint at 21:02:38, and the production worker took the lease 25.96 s later. That gap exceeds M4's 20 s threshold. 0017 changes `lease_started` only by committing an open replay batch first, which is a no-op in the forward worker.
- **Reading.** Latency is still dominated by the worker's 250 ms poll interval. The forward path keeps one fenced transaction per step, and the fast path is refused for it (T8).

**Result.** Every phase of the rebased gate passed. `rt-0929f` was then stopped with `-Phase Stop`; its volumes and logs are kept. The effect-step p95 of 300 ms against 287 ms is within that poll-driven spread, with a concurrent workload on the host. The forward path keeps one fenced transaction per step (the fast path is refused for it, T8).
