# ExecPlan 0014 — Bounded latest-quote reads for replay and catch-up

**Status: IMPLEMENTED and deployed to the normal app (2026-09-29, §10.5). B1–B3 VERIFIED; B4 FAILED (the seven-day replay still misses its 20 min budget for a different reason, see §10.3).** Owner request: "fix the query next", after ExecPlan 0013 recorded the seven-day replay budget as FAILED ([finding](0013-m3-gate-closure.md#53-replay-finding-observed-run-m3gate-0929a)). Branch `claude/bounded-latest-quote`, stacked on `claude/m3-gate-closure` because the replay workload that measures the fix lives there. Delivered by pull request.

Labels: `OBSERVED`, `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal and observable outcome

`MarketView.latest_quote` must cost the same wherever the replay position is, without changing which quote it returns for any data the system can store.

Observable outcomes:
- The seven-day full-density replay (`PerformanceReplay`) completes twice with identical fingerprints, each run within the 20 min budget.
- The existing `fixture:gapped-stop` replay keeps its recorded fingerprint `2500c8d1…61e`.
- The M3 regression suite passes.

## 2. Current facts (OBSERVED)

- `market_view.py:89-98`: `latest_quote(connection, symbol, watermark, at=None)`.
  - It filters `o.kind = 'QUOTE' AND o.symbol = :symbol AND p.sequence <= :watermark AND (:at IS NULL OR p.available_at <= :at)`.
  - It orders by `o.source_event_at DESC, o.received_at DESC, p.sequence DESC` with `LIMIT 1`.
  - PostgreSQL 17 walks `market_observations_quotes` (symbol, source_event_at, received_at) backwards from the newest stored quote. It discards everything published after the watermark: 538,248 rows and about 1.19 s at watermark 200,000 of 1,815,038.
- The only engine caller that runs in replay is `StepContext.load` (`engine.py:494`). It calls once per symbol per step and always passes `at`, the step decision time.
- `valuation.live_marks` and `views.risk` use a live view at the maximum watermark, where no newer rows exist.
- The market worker rejects any stream message whose provider event time is more than 2 s after its local receipt (`future_source_event`, `market_data/worker.py:466-467`). Publication follows receipt: `available_at = clock_timestamp()` at publish time. Receipt and publication clocks are the same host kernel clock in this Docker deployment. REST backfill produces no quotes. Fixture quotes use event time earlier than receipt.
- The execution role has `statement_timeout = 2000 ms` (`db.py:24`).

## 3. Design (PROPOSED)

When `at` is given, add the predicate `o.source_event_at <= CAST(:at AS timestamptz) + QUOTE_EVENT_LEAD`, with `QUOTE_EVENT_LEAD = 60 s`.

Why it cannot drop a visible quote:
- A quote returned for `at` satisfies `available_at <= at`.
- Every stored stream quote satisfies `source_event_at <= received_at + 2 s <= available_at + 2 s`.
- So `source_event_at <= at + 2 s`. The 60 s margin is 30 times that bound. The predicate only moves the index scan's starting point to the decision time.
- If a stored quote ever broke the rule by more than a minute, the read would return the newest quote at or before the bound. That quote is never fresher, so quality checks fail closed rather than open.

Calls without `at` are unchanged: the live callers, and the API risk view.

Rejected alternatives:
- Adding symbol and kind to `market_publications` plus a new index. That is a schema migration and a backfill for a read-path problem.
- Bounding by the watermark's `available_at`. That needs monotonic availability across lease handovers and clock steps, which nothing enforces.
- Loading replay data incrementally. That changes replay semantics and every restored-source run.

## 4. Scope and exclusions

In scope:
- `app/execution/market_view.py` (the query and a documented constant)
- `docs/DATA_CONTRACTS.md` (state the event-time bound the engine relies on)
- tests
- normal deployment of the rebuilt engine images

Excluded:
- schema changes
- the M2 market read path (`read.py`), which runs only at the live watermark
- strategy, risk and fill semantics
- activation

## 5. Requirements and tests (PROPOSED)

| ID | Requirement | Test |
|---|---|---|
| B1 | With `at` given, the read ignores quotes published after the watermark or available after `at`. It returns the newest visible quote by event time, including a late-arriving quote with an older event time published after a newer one. | New `tests/test_m3_market_view.py`, real PostgreSQL, MarketFixture quotes |
| B2 | The index scan no longer grows with future rows. | Same file: 5,000 future quotes; `EXPLAIN (ANALYZE, FORMAT JSON)` shows at most 50 rows read from `market_observations_quotes` |
| B3 | No result change for valid data | `fixture:gapped-stop` replay fingerprint unchanged (Replay phase); full M3 regression |
| B4 | The seven-day replay meets its budget | `PerformanceReplay`: two runs ≤ 20 min each, identical fingerprints |

## 6. Verification commands (PROPOSED)

Run on an isolated run `bq-<date>`:

```powershell
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Prepare
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Build
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Checks
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Regression
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase WorkerFaults
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Replay
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase PerformanceReplay
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Snapshot
./tools/m3-acceptance.ps1 -RunId bq-<date> -Phase Stop
```

## 7. Normal deployment and rollback (PROPOSED)

This follows the [milestone deployment procedure](../../OPERATIONS.md#milestone-completion-deployment). There is no schema change, so the migration is a no-op.

1. Take a protected backup and record its checksum.
2. Tag the current images `pre-0014`.
3. Rebuild `migrate`, `api`, `market-worker` and `execution-worker`.
4. Recreate `api` and `market-worker`. The execution worker stays built but not started.
5. Verify the running files, readiness and a browser check.

Rollback is image-only: re-tag the `pre-0014` images.

## 8. Q01–Q10 (affected gates)

| Gate | Applicability |
|---|---|
| Q03 Data correctness | Applicable: B1, B3 |
| Q05 Reliability | Applicable: replay and long-downtime catch-up no longer time out at this read |
| Q06 Performance | Applicable: B2, B4 |
| Q07 Automated verification | Applicable |
| Q09 Deployment | Applicable (§7) |
| Q10 Maintainability | Applicable: contract sentence plus a code comment |
| Q01, Q02, Q04, Q08 | Not affected (no UI, authority or observability change) |

## 9. Progress

- 2026-09-29 PLANNED: design from the 0013 finding and a read-only code review. Implementation waits for 0013's final evidence run to take its source snapshot, so the tested files stay unchanged.
- 2026-09-29 IMPLEMENTED: `b9b0369` (query bound, contract sentence, B1/B2 tests); `10bd026` merges `main` (0013).
- 2026-09-29 VERIFIED B1–B3 in isolated run `bq-0929a` from `10bd026`.
- 2026-09-29 The first `PerformanceReplay` attempt stalled in the test loader, not in the engine (§10.2). `87b1996` fixes the loader (test image only); Build, Checks, `PerformanceReplay`, Snapshot and Stop were rerun from it.
- 2026-09-29 B4 FAILED: with positions open the replay runs about 22 engine steps per second (§10.3). At the owner's choice ("Stop, deploy, merge") the replay was stopped after 30 min, and 0014 proceeds to deployment with B4 recorded as failed.
- 2026-09-29 DEPLOYED: PR head `5a1f858` to the normal app, 12:47–12:48 UTC (§10.5).

## 10. Completion evidence

### 10.1 Isolated run `bq-0929a` (VERIFIED)

Detached sequence in Windows PowerShell 5.1, `./tools/m3-acceptance.ps1 -RunId bq-0929a -Phase <phase>`. Logs and the source snapshot are under `.cache/m3/bq-0929a/` (sequence log `.cache/m3/bq-0929a-sequence.log`).

| Phase | Source | Result |
|---|---|---|
| Prepare, Build, Checks | `10bd026` | exit 0 (lint, typecheck, Ruff, Prettier, OpenAPI drift, web build and unit tests) |
| Regression | `10bd026` | 169 passed, 0 skipped (167 M1–M3 plus the 2 new B1/B2 tests), 327.92 s |
| WorkerFaults | `10bd026` | exit 0; kill, pause, database-interrupt and 30 random kills ended at epoch 11 with reconciliation OK and no invariant failures |
| Replay | `10bd026` | two `fixture:gapped-stop` runs, fingerprint `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e`, identical to M3 (B3). The restored market-dump replay passed (`0505f256…0078`); it is not comparable to M3's because each run dumps the live market data at a different time. |
| Build, Checks | `87b1996` | exit 0 (32 s, 43 s) |
| PerformanceReplay | `87b1996` | FAILED budget, stopped by the operator (§10.3) |
| Snapshot, Stop | `87b1996` | exit 0; `source-images.json` records `base_commit 87b199634c311f4f1b03f17c0a83ec7d1f2f892a` |

- **B1 (VERIFIED):** the newest visible quote by event time, including a late-arriving older event, and point-in-time visibility (`tests/test_m3_market_view.py`, real PostgreSQL).
- **B2 (VERIFIED):** with 5,000 future quotes, `EXPLAIN (ANALYZE)` reads at most 50 rows from `market_observations_quotes`.
- **B3 (VERIFIED):** the regression suite and the unchanged `gapped-stop` fingerprint.

### 10.2 Loader stall in the first `PerformanceReplay` attempt (OBSERVED, fixed)

The first attempt ran 2,657 s (11:18:50–12:03:07 UTC) without finishing the data load.
- An autoanalyze ran at 11:19:43, inside the loader's single uncommitted per-symbol transaction. It counted the uncommitted rows as absent and set `market_payloads` to `reltuples = 1` over 16,347 pages.
- The next insert's foreign-key checks then planned an index scan on `market_payloads_retention (received_at, id)`, whose leading column is not the key. They scanned the whole 49 MB index once per row: the 302,400-row BTC candle insert spent 37 minutes and more in its end-of-statement checks.
- The M3 run with the same loader did not hit this timing race.

`87b1996` commits each bulk insert separately and runs `ANALYZE` on the table before the next one. The loaded data and its order are unchanged. The rerun loaded all 1,815,038 publications in about 5 minutes.

### 10.3 Seven-day replay throughput (B4 FAILED)

Measured on the rerun, which replayed from 12:11:25 UTC (`.cache/m3/bq-0929a/replay/density-run1-partial.txt`):
- **The fixed read is flat.** From sequence 104 to 434,922 took about 61 s (311 steps, no open position). The unfixed M3 run needed about 40 minutes to reach 433,997.
- **Positions change the step rate.** After both reference positions opened (simulated 2026-09-02 ~16:00), the engine steps once per simulated second. The rate held steady at 21.6 steps and about 63 publications per second (for example 522,039 → 525,810 and +1,295 steps in 60 s), about 46 ms per step, with no degradation.
- **Where the time goes.** In 300 samples of the replay database's active query, the per-step `COMMIT` was 16% (I/O wait), a `max(open_ms)` candle read 9% and the bounded quote read 7%, with the rest spread over the step's other reads. The database was active in about half of the samples; the rest is engine Python time.
- **Stopped.** At 12:42:05 UTC at sequence 542,924 of 1,815,038, with 36,057 steps, 2 filled entries and 2 open positions. At the measured rate run 1 needed at least 5.7 more hours.

The seven-day density fingerprint comparison was therefore not run. Replay determinism remains verified on `gapped-stop` only.

The 20 min budget needs under 2 ms per step if a position is open for most of the week. Meeting it needs a design change: for example several replay steps per transaction in replay mode, fewer reads per step, or a revised budget (an owner decision). This is a follow-up, outside this plan.

### 10.4 Gates

| Gate | Result |
|---|---|
| Q03 | VERIFIED: B1, B3 |
| Q05 | IMPROVED: the bounded read no longer grows with future rows; replay and catch-up still pay about 46 ms per step with positions open |
| Q06 | B2 VERIFIED; B4 FAILED (§10.3) |
| Q07 | VERIFIED: §10.1 |
| Q09 | VERIFIED: §10.5 |
| Q10 | VERIFIED: [DATA_CONTRACTS](../../DATA_CONTRACTS.md) event-time bound and the `QUOTE_EVENT_LEAD` comment |

### 10.5 Normal deployment (VERIFIED)

Deployed 2026-09-29 12:47–12:48 UTC under the standing milestone-deployment authorization and the owner's "deploy the query fix", before merge. Source was the pushed PR head `5a1f858ba4a55c9d28bb4f42a68aec1b2dd64dc7`, a clean tree in `../adaptive-spot-lab-quote`. It differs from the tested `87b1996` only in docs and CI files, which go into no image. Commands are in [COMMANDS](../COMMANDS.md#verified-execplan-0014-commands--2026-09-29); the log is `.cache/deployments/bounded-quote-20260929a/deploy.log`.

- **Rollback tags (`:pre-0014`):** api `sha256:ea2e8795…`, market-worker `sha256:76993dfa…`, migrate `sha256:6243e693…`, execution-worker `sha256:2f0256bb…`.
- **Protected backup:** `.cache/deployments/bounded-quote-20260929a/bounded-quote-20260929a.dump`, 102,007,873 bytes, SHA-256 `c4834a406fdf3e756ae77a05c3d854e2df10cd71bb9ff96d957518663b7cceeb`. The container `sha256sum` and host `Get-FileHash` matched. The ACL is limited to SYSTEM, Administrators and the owner account. The in-container copy was removed.
- **Rollout:** `config`, `build` of migrate, api, market-worker and execution-worker, a no-op `migrate`, then `up --force-recreate --wait` of api and market-worker. All exited 0. Web and PostgreSQL were not recreated.
- **Running images:** api `sha256:86bf8e40742a20208da9437febd942ab3404f7e9819de37fd6543a0b77d7a602`, market-worker `sha256:ff1f854f6f160bf6736c88db79131dd1d6563ffcfdf30f2589dd4aff2b964118`. Also built: migrate `sha256:9d31a21e…`, execution-worker `sha256:f2bc6ee9…`. Web `sha256:8efe8e5b…` and PostgreSQL are unchanged.
- **Running source:** `app/execution/market_view.py` in both containers is SHA-256 `85a301aa…f059`, byte-identical to the worktree file, which is checked out with CRLF line endings. With carriage returns removed it is `c253ed06…8554`, the commit's blob. It contains `QUOTE_EVENT_LEAD`.
- **State:**
  - API readiness returned 200.
  - The schema is `0005_m3_paper_broker`, unchanged.
  - `account_state`: initialized true, paused false, reconciliation_failed false, valuation_valid true.
  - `asl_execution` has `rolcanlogin = false`, and there is no execution-worker container.
- **Collection:** both feeds were `CONNECTED` at 12:48:46 UTC with quotes under 0.5 s old. The restart handover cost about 36 s of capture (last quotes 12:48:04, first new 12:48:40), with no market incident.
- **Browser:** `GET http://127.0.0.1:3000/` returned 200. The in-app browser showed the unauthenticated owner sign-in page.
- **Rollback:** image-only. Re-tag the `:pre-0014` images and recreate api and market-worker.
