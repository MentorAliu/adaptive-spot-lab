# ExecPlan 0013 — M3 gate closure: secret scan, performance budgets, screen-reader review retirement

**Status: COMPLETE (2026-09-29).** One budget failed: the seven-day replay, fixed separately in ExecPlan 0014. See §7–§9. Owner request on 2026-09-29: "start with the M3 checks, but turn off the screen-reader review for this and the rest of the application, cleanup". Branch `claude/m3-gate-closure`; delivered by pull request.

Labels: `OBSERVED` (seen in code, data or command output), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal and observable outcome

[ExecPlan 0011](0011-paper-broker-reference.md#15-completion-evidence) accepted M3 with three open items: an owner Narrator review (Q02), a secret-value scan of logs and client assets (Q04), and the long-running performance budgets (Q06). This plan closes them:

1. **Q02:** the owner retired manual screen-reader review for M3 and all later work ([decision](../../DECISIONS.md#2026-09-29--manual-screen-reader-review-retired)). The contracts say so, and nothing claims screen-reader behavior as verified.
2. **Q04:** a repeatable harness phase scans every log and artifact of an isolated M3 run, and the built web client assets, for that run's secret values and for credential markers. It records counts and file hashes only, never values. Expected result: zero occurrences.
3. **Q06:** the four workloads declared in ExecPlan 0011 §10 but never implemented (item 13) are implemented and measured against the declared budgets, and failures are retained:
   - the 60-minute real-time engine workload
   - seven-day full-density replay
   - 10,000-record API reads
   - browser SSR/LCP/CLS/interaction timing
4. **Cleanup** of obsolete local Docker state, recorded below.

## 2. Current facts (OBSERVED)

- `main` is at `77e2830`: M3 (`01b065a`) plus the ExecPlan 0012 history. The normal app runs M3 inert on schema `0005_m3_paper_broker`.
- ExecPlan 0011 §10 declares the budgets. Its item 13 records that the 60-minute engine workload, seven-day replay, 10,000-record API reads and browser LCP/CLS were not implemented. The existing `Performance` phase measured only strategy timing (p95 3.24 ms) and 24 h catch-up (26.24 s).
- The accepted run `m3-0929e` has 128 logs, 9 JSON files, one dump and per-target `secrets/` directories under `.cache/m3/m3-0929e/`. Its web image `asl-m3-m3-0929e-browser-web` (`5555d73cdfde`) is still present.
- M2's security inspection compared secret values against task logs and scanned public assets for markers, but by hand; no harness phase exists ([COMMANDS](../COMMANDS.md)).

## 3. Scope and exclusions

In scope:
- harness phases and measurement helpers for the secret scan and the four workloads
- isolated runs
- contract and record updates for the Q02 decision

Excluded:
- application behavior changes. If a budget fails, the failure is recorded; a fix is separate work unless trivially confined to test tooling.
- the normal app's secrets: the value scan uses isolated run secrets only
- M4 work

## 4. Cleanup record — 2026-09-29 (VERIFIED)

- Deleted three `pre-0012` image tags (`adaptive-spot-lab-{api,market-worker,migrate}:pre-0012`; IDs `9be9e200d9ba`, `b135fa9b6fbf`, `2b545ea2f4f0`). No container used them and they had no other tags. They were built for schema `0004` and are no rollback path after `0005`.
- Deleted the four isolated volumes of runs `continuity-b0` and `continuity-0928a`. No container or network remained. The evidence under `.cache/m2/continuity-*` is kept.
- The `pre-m3` rollback tags and all other isolated test volumes are unchanged. The normal app's four containers stayed up and healthy throughout.

## 5. Design (PROPOSED)

### 5.1 Secret scan (Q04) — IMPLEMENTED

A `SecretScan` phase in `tools/m3-acceptance.ps1`, run before `Stop`:
1. **Capture container logs.** Write the logs of every container in the run's Compose projects, running or stopped, to `secret-scan/` under the run root.
2. **Extract the web build output.** Copy the run's web image `.output` (browser `public/` and `server/`) into `secret-scan/web-output/`.
3. **Load secret values.** Read each target's secret files (6 per target, 30 in total) in memory only.
4. **Scan every file** under the run root except the `secrets/` directories. That covers harness logs, container logs, artifacts, dumps, reports and the web build output. Zip files are scanned by their decompressed entries, because Playwright traces record typed values. Each value is searched in three forms:
   - raw
   - upper-case
   - Base64
5. **Check browser files for markers.** Files under `web-output/public` must not name `/run/secrets`, `postgresql://`, `postgresql+psycopg`, `X-Internal-Key` or any secret file name. The one exception is the owner setup page's documented instruction naming `secrets/owner_setup_key`, which is allowed and counted.
6. **Record results** in `secret-scan/secret-scan.json`:
   - secret names, forms and marker names
   - file classes and sizes
   - every scanned file's SHA-256
   - any findings

   Values are never written. The phase fails on any finding.

### 5.2 Performance workloads (Q06) — IMPLEMENTED

The measurement code lives in `services/engine/tests/m3_performance.py` and `apps/web/e2e/execution-performance.spec.ts`. Only the engine *test* image contains `tests/`, so the runtime images and the running app do not change. Each workload is a harness phase in `tools/m3-acceptance.ps1`. The budgets are ExecPlan 0011 §10's, unchanged.

**Read-load dataset** (for the API and browser workloads)
- `browser_fixture` first writes two engine-produced synthetic round trips (BTC and SOL): 4 orders, 4 fills and 2 closed positions with mandates, obligations, events and reservations.
- `seed-reads` then clones them 2,499 times in foreign-key order, reading column lists from the live schema. The clones get deterministic RFC 9562 version-3 UUIDs; the web schemas reject other UUIDs.
- Resulting row counts:

  | Table | Rows |
  |---|---|
  | orders | 10,000 |
  | fills | 10,000 |
  | positions | 5,000 |
  | order events | 32,500 |
  | position events | 25,000 |
  | reservations | 10,000 |

- It is read-load data only. The clones have no ledger postings, so the app's startup reconciliation reports a mismatch, as expected. It is never accounting evidence.

**Workloads**

- **`PerformanceApi`** — 10,000-record API reads.
  - Resets the engine database, seeds the read-load dataset, then times 16 owner read routes in-process as the `api` role:
    - orders, fills and positions pages, with filters and mid-history cursors
    - order and position details
    - risk for both modes
  - 160 sequential reads, and 5 clients × 32 concurrent reads. The clients are opened one at a time because each runs the app's startup reconciliation under the account lock.
  - Budget: p95 ≤ 250 ms sequential, ≤ 500 ms concurrent.
- **`PerformanceBrowser`** — Orders, Positions and Risk pages, with a signed-in owner session.
  - Resets and reseeds the browser database, then runs the Playwright spec at 390×844 and 1440×900.
  - For each page and viewport:
    - lab LCP and CLS after load, before any input
    - 30 warm authenticated SSR requests
    - on Orders and Positions, 30 table interactions: 24 symbol-filter switches plus 6 paging clicks
  - The pages keep the previous rows visible while loading, so each interaction's timer stops only when every row matches the new filter, or when the first row changes after paging.
  - Budget: SSR p95 < 1,500 ms; LCP ≤ 2.5 s; CLS ≤ 0.1; interactions p95 ≤ 200 ms.
- **`PerformanceReplay`** — seven days of full-density synthetic data.
  - The dataset is bulk-loaded in availability order:
    - 150 warm-up hourly bars
    - per symbol, one quote per second and one provisional candle every two seconds
    - every final hourly bar
  - That is 1,209,600 quotes, 604,800 provisional candles and 1,815,038 publications in total, labeled `SYNTHETIC_FIXTURE`. Deterministic price cycles give the strategy several entries and exits.
  - The data is replayed twice through the production replay path (`app.replay.run.replay` and `report`), with cost scenario `COST_SCENARIO_HYPOTHETICAL_H1`.
  - Budget: each replay ≤ 20 min, and identical fingerprints.
- **`PerformanceEngine`** — real-time engine workload for `-EngineSeconds`, default 3,600.
  - A feed container resets the worker database, then seeds a TREND_REFERENCE_V1 history through the engine's own simulated driver:
    - BTC's entry bar closes exactly 72 h before the next hour boundary, so its TIME_EXIT falls inside the run.
    - SOL enters at the current hour.
  - It then writes `ready.json` and acts as a live feed:
    - one quote per symbol per second
    - a provisional candle per symbol every 2 s
    - final candles at each hour
    - a healthy feed state every 250 ms
    - SOL bids dip below its stop 10 minutes before the end, forcing a PROTECTIVE_STOP exit
  - A second container, with the same 1 CPU / 512 MiB limits as the execution worker, runs the production `Worker.serve` loop in-process.
    - `ExecutionEngine.handle` is wrapped to record, for every publication step, the time from publication `available_at` to the step's commit returning.
    - The first 30 s, while the backlog is processed, are excluded.
    - `/proc/self/status` RSS is sampled every 5 s.
  - Afterwards, `invariants` runs reconciliation plus the SQL invariants on the engine-written data.
  - Budget: p95 ≤ 750 ms and p99 ≤ 1.5 s; RSS < 256 MiB, with < 10 MiB growth over the final 30 min.

### 5.3 Replay finding (OBSERVED, run `m3gate-0929a`)

`PerformanceReplay` loaded all 1,815,038 publications, then failed at 43,511 publications, 2.4% of the way through the first replay. A step's `latest_quote` read exceeded the execution identity's 2 s `statement_timeout`. The call path was `SimulatedDriver.run` → `ExecutionEngine.handle` → `StepContext.load` → `MarketView.latest_quote` (`engine.py:494`).

**Root cause (EXPLAIN on the loaded data).** The query selects the newest quote at or below the watermark:
- It filters `o.kind = 'QUOTE' AND o.symbol = :symbol AND p.sequence <= :watermark`.
- It orders by `o.source_event_at DESC, o.received_at DESC, p.sequence DESC` with `LIMIT 1`.
- PostgreSQL walks the `market_observations_quotes` index (symbol, source_event_at) backwards from the newest stored quote. It then discards every quote published after the watermark.

With watermark 200,000, that meant 538,248 index rows and about 1.19 s. At the replay's actual position, it exceeds 2 s.

**Scope of the defect.**
- A forward worker in steady state is unaffected, because its watermark is always the newest publication.
- Any replay of preloaded history grows linearly with the data beyond its current position. That includes a seven-day `restored` replay of recorded public data, which is M4 evaluation tooling.
- The same scan applies while a restarted worker is still behind its backlog (INFERRED, not measured). Most backlog quotes are stale and skip steps, which is why the 24 h catch-up probe passed. A step that does run pays roughly 2 µs per newer quote of that symbol. That puts the 2 s timeout at a backlog of several days.

**Fix (separate work).** It changes execution-authority code, so this plan's exclusions apply. The replay budget is recorded here as **FAILED**.

The owner asked for the fix next. It is [ExecPlan 0014](0014-bounded-latest-quote.md):
- It bounds the event time by the step decision time plus a 60 s margin. That relies on the market worker's existing 2 s `future_source_event` rule.
- Only `StepContext.load` passes a decision time. `valuation.live_marks` and the risk view read at the live watermark, where no later rows exist.

## 6. Progress

- 2026-09-29 VERIFIED: cleanup (§4). Q02 decision recorded in DECISIONS, ACCEPTANCE_CHECKLIST, TESTING, README, STATUS and the retired M3 checklist.
- 2026-09-29 IMPLEMENTED: the workloads (§5.2) and the secret scan (§5.1). Development run `m3gate-0929a` found and fixed several tool defects, none in the application:
  - an int4 overflow in the clone offset
  - non-RFC UUIDs rejected by the web schemas
  - a sign-in race in the spec
  - a quote gap that correctly blocked SOL's entry on an invalid valuation
  - duplicate provisional-candle identities
  - a missing feed-stall watchdog
- 2026-09-29 VERIFIED: final run `m3gate-0929b` and recheck `m3gate-0929c` (§7).

## 7. Results

**Final run `m3gate-0929b`** (08:44–10:54 UTC). It built from `05b4d98`; `Snapshot` recorded that base commit and 226 source files. Nothing else ran on the host during measured phases, except that a lint container ran for a few seconds during `PerformanceBrowser` (see below).

| Phase | Result |
|---|---|
| Build | Passed |
| Checks | **FAILED on format-check only**: the new spec needed one Prettier join. Lint, types, 32 web unit tests, API/OpenAPI drift and Ruff passed. The web build was not reached (see recheck). |
| Regression | 167 engine tests passed, no skips (322.8 s). Mode guard passed. |
| Migration | Passed |
| WorkerFaults | Passed; final lease epoch 14, checkpoint 1,278 of 1,288 publications |
| Replay | Two `fixture:gapped-stop` runs gave fingerprint `2500c8d1…561e`, identical to M3's accepted run `m3-0929e`. The restored replay was labeled `RESTORED_SYNTHETIC_FIXTURE`. |
| ReplayIsolation | Passed |
| Browser inactive, populated, error | Passed |
| Performance (existing) | Strategy p95 3.48 ms (≤ 500 ms); 24 h catch-up 22.62 s (≤ 120 s) |
| PerformanceApi | Passed (below) |
| PerformanceBrowser | **FAILED**: Orders interactions p95 203 ms (390 px) and 238 ms (1440 px), against 200 ms |
| PerformanceReplay | **FAILED**; stopped after 2,495 s at publication 433,997 of 1,815,038 |
| PerformanceEngine | Passed (below). Afterwards reconciliation OK, no invariant failures. |
| SecretScan | **FAILED**: 1 finding (below) |
| Snapshot, Stop | Passed |

**Recheck `m3gate-0929c`** (10:55–10:59 UTC) from `2838424`. That commit is the Prettier join plus `trace: "off"` for the performance spec.
- Checks passed, including format-check and the web build.
- PerformanceBrowser passed.
- SecretScan: 123 files, 0 findings.

**Measurements**

| Workload | Measured | Budget | Result |
|---|---|---|---|
| API, 10,000 orders and 10,000 fills | Sequential p95 19.7 ms (160 reads); five-way concurrent p95 116.9 ms (160 reads) | ≤ 250 ms / ≤ 500 ms | PASS |
| Browser, `0929b` (Playwright tracing on) | SSR p95 73–151 ms; LCP 124–308 ms; CLS 0; Positions interactions p95 126/144 ms; Orders interactions p95 **203/238 ms** | SSR < 1,500 ms; LCP ≤ 2.5 s; CLS ≤ 0.1; interactions ≤ 200 ms | **FAIL** (Orders) |
| Browser, `0929c` (tracing off) | SSR p95 59–112 ms; LCP 92–192 ms; CLS 0 (also after interactions); interactions p95 Orders 118/98 ms, Positions 84/80 ms | Same | PASS |
| Seven-day replay | 433,997 of 1,815,038 publications, about 1.7 simulated days, before it was stopped at 41.6 min | ≤ 20 min per run; identical fingerprints | **FAIL** (§5.3) |
| Engine, 60 min real time | See below | p95 ≤ 750 ms, p99 ≤ 1.5 s; RSS < 256 MiB, < 10 MiB growth | PASS |

Engine workload detail:
- **Latency:** 7,144 measured publication steps. p50 176 ms, p95 291 ms, p99 311 ms, max 337 ms. Steps with effects (300): p95 287 ms.
- **Resources:** RSS max 63.4 MiB, final-30-min growth 0.5 MiB. CPU averaged 3.3% of the 1-CPU limit (cgroup `cpu.max` 100000/100000, `memory.max` 512 MiB).
- **Events:** BTC's TIME_EXIT at the 10:00 boundary and SOL's PROTECTIVE_STOP at the scripted dip, each with a modeled SELL fill. Both positions ended `CLOSED_WITH_DUST`.
- **Feed:** 7,680 quotes, 3,840 provisional and 2 final candles. Publish p95 7.4 ms.
- **Latency composition:** mostly the worker's 250 ms poll interval.

**Why the browser result changed.**
- **Tracing.** The `0929b` failure was measured with Playwright tracing on (`retain-on-failure` records during every test), and without tracing the same interactions took roughly half as long.
- **Concurrent load.** During `0929b`, my 0014 lint container also ran for a few seconds.
- **Conclusion.** The failed measurement is kept as recorded. Orders updates two tables per filter change and is the slowest interaction.

**Secret-scan finding.**
- **What:** the isolated browser target's one-time `owner_setup_key` appeared, raw, inside the retained Playwright failure trace of the `0929b` performance spec. The spec typed that key because the phase's database reset removed the owner.
- **Exposure:** the trace sits in the same ignored run directory as the key file, so there was no additional exposure. No log, container log, dump or web file contained any secret value, in any form, across 267 files.
- **Fix:** tracing is off for that spec.
- **Residual:** other specs that type the setup key still record it in their failure traces. See §9.

## 8. Gate dispositions (scoped to this change)

| Gate | Result |
|---|---|
| Q02 | **CLOSED by owner decision**. Manual screen-reader review is retired. Automated checks and implementer browser inspection remain the evidence, and no screen-reader or conformance claim is made. |
| Q04 | **VERIFIED (scoped)**. Value and marker scan with 0 findings on the recheck. The final run's one finding (§7) is disclosed and fixed. Not a penetration test. |
| Q06 | **VERIFIED, except the seven-day replay (FAILED)**. Engine, API and browser pass. The browser result passes only with tracing off; the traced run failed on Orders. The replay failure is §5.3; ExecPlan 0014 fixes it. |
| Q07 | **VERIFIED** on `2838424`: all checks. The new tooling passed Ruff, ESLint, types and Prettier. |
| Q09 | Not affected. No runtime image changes, so no normal deployment is needed. |

## 9. Residuals and follow-ups

- **Seven-day replay.** It is fixed by ExecPlan 0014 and re-measured there.
- **Failure traces.** Playwright failure traces record typed values. Specs that type the one-time setup key (`e2e/execution.spec.ts`, and the M1/M2 owner-setup flows) keep `retain-on-failure` tracing. The key is disposable and isolated, and the traces sit beside its secret file. Setting `trace: "off"` for those steps, or seeding the owner without typing, is a small follow-up.
- **Orders page.** It is the slowest interaction: two tables and two server round trips per filter change.
- **Evidence retention.** The isolated volumes of runs `m3gate-0929a`–`c` are kept. Their evidence is under `.cache/m3/`.

## 10. Next task

- ExecPlan 0014: verify, deploy and merge the bounded latest-quote read.
- ExecPlan 0015: M4, whose owner decisions are recorded.
