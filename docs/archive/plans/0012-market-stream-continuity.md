# ExecPlan 0012 — Market stream continuity across instrument drift and rotation

Number 0011 is reserved for the M3 paper-broker/reference plan. That plan does not modify the market worker and treats this defect as a blocker for M4 activation. The proposal below is the declared baseline; progress, verification results and completion evidence are appended in dated sections after it and take precedence for actual status.

The proposal was prepared in a planning-only session:
- No repository file was edited.
- Evidence came from source and git reads, `docker compose -p adaptive-spot-lab ps`, the cached websockets 17.0.1 package source, and `BEGIN TRANSACTION READ ONLY` SELECTs on public market tables.
- No secrets, sessions or ledger tables were read.

Labels used below: `OBSERVED` (seen in code or data), `INFERRED` (reasoned from observations), `PROPOSED` (the plan), `IMPLEMENTED`, `VERIFIED` and `NOT RUN`.

## Context

The owner activated public collection in ExecPlan 0006. Since then the normal app has lost BTCUSDT/SOLUSDT quote usability for about 1–1.5 minutes every hour, and for up to about 1 s every minute.

M3/M4 protective exits must be evaluated on fresh executable data:
- [RISK_POLICY.md](../../RISK_POLICY.md) sets a 5 s quote age limit.
- [OPERATIONS.md](../../OPERATIONS.md) requires protective exits to be evaluated against eligible fresh data.

This plan makes quotes continuous across Binance's hourly filter drift and across genuine stream rotations. It keeps the M2 rule: a quote is usable only when it was captured under the feed's current capture generation and instrument snapshot.

## 1. Goal and observable outcome (PROPOSED)

1. **Instrument drift causes no rotation.** A snapshot change with an unchanged subscription, such as Binance's hourly `MARKET_LOT_SIZE.maxQty` drift, causes no socket rotation, new collection or gap. `read.quote` stays VALID throughout.
2. **Routine refresh never downgrades a feed.** A 60 s reference refresh never downgrades a `CONNECTED` feed. A failed check still fails closed, and publication cannot silently re-enable it.
3. **Rotation is make-before-break.** This applies to rotation at 23 h age, on `serverShutdown`, or on a positive subscription change.
   - The old generation stays usable until each symbol's first quote from the new generation is published.
   - At most two sockets exist, with ≤ 10 s overlap measured from the start of the replacement's open.
   - A slow provider close never raises into the collection.
   - A replacement that never delivers leaves the old generation current, and a visible incident is recorded.
4. **Failure evidence is honest.**
   - Any remaining collection failure records its phase and the original failure code; a teardown timeout no longer masks it.
   - Retry backoff resets after a healthy collection.
5. **Normal deployment.** The normal app runs the accepted `api` and `market-worker` images with collection still enabled. Two consecutive hour boundaries then pass with no `STREAM_ROTATION` or `COLLECTION_GAP`.

## 2. Current facts

### Code (OBSERVED at HEAD `f7fad71`; `worker.py` last changed in `4cfb8a4`)

**Instrument snapshots and the rotation trigger**
- `parse_instrument` hashes the whole exchangeInfo symbol item (`parse.py:148-149`).
- `store.instrument_snapshot` is content-addressed and moves `market_feed_state.instrument_id` immediately (`store.py:122-132`).
- `maintain_references` rotates whenever `snapshots != self.instruments` (`worker.py:376-384`).
- A transient REST failure drops the symbol from `valid_symbols`, which also forces a rotation (`worker.py:221-227`).

**Where quotes get their instrument binding**
- `SocketState.instruments` is copied when the socket opens (`worker.py:439`).
- `_ingest_frames` stamps that binding at write time, not at receipt (`worker.py:170-171`).

**When `read.quote` is VALID** (`read.py:117-132`)
- The feed is `CONNECTED` and telemetry is valid.
- The quote's collection and instrument IDs equal the feed's.
- Clock and instrument checks are ≤ 120 s old.
- The quote, feed and watermark are read in separate READ COMMITTED statements.

**The rotation block** (`worker.py:456-482`) runs these steps in order:
1. Record `STREAM_ROTATION`.
2. `begin_collection`: advance the epoch, reset the feed to the new collection with `instrument_id` NULL and status `CHECKING`, and set telemetry `sampled_at` to NULL (`store.py:84-103`).
3. Refresh references.
4. Backfill 720 rows.
5. Open the replacement socket.
6. Wait for readiness under `asyncio.timeout(5)`.
7. In `finally`, run `asyncio.wait_for(close_socket(old), 5)`.

Then teardown closes the remaining sockets sequentially through `AsyncExitStack`. It does this before readers are cancelled, the feed is marked UNAVAILABLE, or the gap is recorded (`worker.py:421-433, 484-532`).

**websockets 17.0.1 close behaviour** (`asyncio/connection.py`)
- `close()` is self-bounded at `close_timeout` (5 s here, `provider.py:187-191`). It aborts the transport itself when the deadline passes (lines 939-959) and swallows `ConnectionClosed` (lines 643-646).
- An outer `wait_for` with the same 5 s fires first. It cancels the close inside a shielded wait, so the transport is not aborted and the socket leaks. The resulting `TimeoutError` is raised in `finally` and replaces any original exception.
- With `max_queue=16`, the receive buffer calls `pause_reading` once it is full (line 1005). Once the reader is cancelled, that can stall a delayed close.

**Status and publication**
- `refresh_references` writes `CHECKING` for both feeds every ~60 s (`worker.py:186-213`).
- `publish_pending` sets `CONNECTED` and clears `last_error` on any same-collection VALID quote, including over UNAVAILABLE (`store.py:301-305`). This is fail-open.

**Locking and fencing**
- `ingest()` holds `write_lock` across every chunk of a 720-row backfill (`worker.py:127-132`).
- Queue `overloaded` becomes sticky when the oldest frame is > 1 s old, and then `observe_queue` raises `QUEUE_OVERLOAD` (`pipeline.py:69-75`, `worker.py:364-374`).
- `write_frames` makes fenced `update_feed`, `record_incident` and `record_invalid` calls outside `write_lock` (`worker.py:333, 345, 359-361`). An epoch advance can land between them and raise `LostLease`.

**Retry backoff**
- `run()` resets `attempts` only when `consume()` returns normally (`worker.py:547-548`). That happens only on stop.

**Test coverage gaps**
- `ControlledProvider` closes instantly, returns one kline, ignores the requested symbols, and its fixture has no `MARKET_LOT_SIZE` filter (`acceptance.py:22-69`, `fixture_worker.py:29-38`).
- `test_actual_worker_overlaps_rotates_and_revalidates` asserts that quotes become non-VALID at rotation (`tests/test_m2_worker.py:152`).

### Runtime data (OBSERVED, normal DB, 2026-09-28 05:19–17:02 UTC)

**Rotations**
- There were 13 `STREAM_ROTATION` incidents, and all 13 ended in a `COLLECTION_GAP` with failure_type `TimeoutError`. No production rotation has succeeded.
- 12 were hourly, between HH:00:22 and HH:01:07, and each coincided with new INSTRUMENT rows.
- The 12:47 rotation followed a REST failure that made BTC `INSTRUMENT_UNAVAILABLE`.

**Instrument drift**
- For each symbol, all 13 snapshots hash identically once `MARKET_LOT_SIZE.maxQty` is removed.
- BTC maxQty went 139.00391379 → 139.69167145 → 133.01644604 (14:00–16:00). SOL went 72459.52978750 → 77641.08365416 → 79574.48870416.
- `LOT_SIZE.maxQty` stayed fixed at 9000 (BTC) and 90000 (SOL).

**Replacement timing**
- Every replacement socket captured and published quotes for both symbols under the new collection. For example, at 16:00 BTC was published at 46.289 and SOL at 47.064.
- Replacement frames stopped about 4–5.2 s after its first frame.
- The gap was recorded about 4.8–5.4 s after the last replacement frame.
- `captured_pending` was 0 and there was no drain failure.

**Queue overload**
- The 4 rotations with more than 1 s publication lag during refresh/backfill (12:00, 14:01, 16:00 and 17:01; lag 1.046–1.363 s) are exactly the 4 gaps whose detail shows `queue.overloaded=true`.
- The other 9 rotations had lag between 0.52 and 0.98 s and were not flagged overloaded.

**Retry backoff** — the pauses between failure and restart match an escalating backoff that never resets:
- 2.7 s, 4.1 s, 8.3 s, 16.3 s, then 60.0 s at 06:00–09:01; the cycle then restarts.
- 12:43–13:47 after a process recreation: 2.5, 4.4, 8.7, 16.2 and 60.0 s.
- 13:49–17:02: 2.8, 4.9, 8.4, 16.3 and 60.0 s.

**Recovery start**
- From collection start to first quote took 20–75 s after short waits, but about 9.6 s after each 60 s wait.

**Other gaps (out of scope)**
- Two `stream_silent` gaps (06:20 and 12:43).
- One REST outage at 12:44.
- The 107 s gap at 13:47: `CLOCK_UNCERTAIN`, then a 60 s wait at attempt 5, then `clock_recovery_pending`.

### Root cause

- **Trigger (OBSERVED).** Binance's hourly `maxQty` drift creates a new content-addressed snapshot, and `maintain_references` rotates on any snapshot change.
- **Failure in the rotation path itself (INFERRED, high confidence).** It affects 23 h and `serverShutdown` rotations too.
  - The outer `wait_for(close, 5)` always expires before websockets' own 5 s close deadline when the provider does not end TCP within 5 s. It raises `TimeoutError` and leaks the socket.
  - Teardown then waits about 5 s more on the replacement close.
  - Readiness did not time out. Replacement frames flowed about 5 s, not the 9–10 s a readiness expiry plus close would give.
  - In the 4 overloaded rotations, `QUEUE_OVERLOAD` ended the readiness loop, and the close `TimeoutError` masked it. The overload came from backfill `ingest` starving the writer.
- **Gap length (OBSERVED).**
  - The escalating, never-reset backoff sets most of the variation.
  - Recovery start-up is slow after short waits, consistent with REST weight-budget exhaustion. That cause is INFERRED: maintenance, rotation and recovery refreshes plus backfill total about 133 weight against a limit of 120 per minute.
- **Secondary (code-derived).**
  - The `CHECKING` write every minute makes quotes UNAVAILABLE for up to about 1.2 s.
  - Once hourly rotations stop, the hourly maintenance backfill would run against a live socket. Without per-chunk locking, it would recreate the > 1 s queue age.
- **Unresolved from database evidence.** Why Binance does not end TCP after a close. It could be the provider itself or `max_queue` pause-reading once the reader is cancelled. Batch B0 records close duration, close code and whether the close aborted. The design does not depend on the answer.

## 3. Scope and exclusions

**In scope:** market worker reference refresh, adoption, subscription, rotation, close/teardown, backoff, writer locking/fencing and failure evidence; the store functions they use; `read.quote`/`health` read consistency; test provider and fixtures; harness phases; contract text; normal deployment of `api` and `market-worker` with collection kept enabled.

**Excluded (listed as follow-ups):**
- Clock-uncertainty teardown policy (13:47).
- REST weight budgeting during recovery.
- `stream_silent` and REST outages.
- Narrowing backfill to missing ranges.
- Any web or UI change. `MarketIncident.code` is a free string (`openapi.json:952-985`), so new codes need no API schema change.
- M3/M4 broker, risk and exit logic.
- Enabling trading, agents or models.
- RISK_POLICY thresholds.
- Schema migrations. None are expected, because existing grants already cover the feed `collection_id`/`instrument_id` updates. If one proves necessary, stop and amend this plan.

## 4. Design (PROPOSED)

- **D1 — Receipt-time binding.**
  - `pipeline.py` gains an immutable, hashable `Binding(collection_id, instruments: tuple[(symbol, instrument_id)])`.
  - `read_socket` stores `Frame.binding = state.binding` at receipt.
  - `write_frames` groups frames by binding.
  - Adoption swaps `state.binding` by reference in one synchronous step with no `await`. Frames already queued keep their old snapshot.
  - `SERVER_SHUTDOWN` detail uses `frame.binding.collection_id`.
- **D2 — In-place adoption with deferred, publication-atomic activation.**
  - Triggered when a snapshot changes but the subscription does not.
  - The refresh resolves the new instrument ID with a lookup-only `store.resolve_instrument`. `instrument_snapshot` keeps its immediate pointer move for startup and fixture paths.
  - The worker registers a per-symbol target `{symbol: (collection, instrument_id, checked_at)}` and swaps the binding.
  - Every worker publication path goes through one `self.publish()` helper. That covers `ingest`, the writer and `confirm_conflicts`. The helper calls `store.publish_and_activate(targets)`.
  - In the same fenced transaction, after publishing, the helper moves the symbol's `(collection_id, instrument_id, last_instrument_check_at)` only when the latest published VALID quote carries the target. "Latest" uses `read.quote`'s ordering: `source_event_at DESC, received_at DESC, sequence DESC`.
  - The helper returns the symbols it activated. The pointer move is independent of the overload flag; overload affects status only.
  - `publish_pending()` stays as the unchanged count-returning wrapper.
  - Readers therefore see either the old pointer with the old quote or the new pointer with the new quote. The pointer lags the newest verified snapshot by at most one tick, well inside the 120 s reference tolerance.
- **D3 — Subscription changes only on a positive non-usable status.**
  - A positive non-usable status is: not `TRADING`, or no SPOT path.
  - A transient exchangeInfo or parse failure keeps the subscription and binding, sets that feed UNAVAILABLE (fail-closed), records the existing incident, and retries next cycle.
  - At startup, a symbol with no snapshot is still excluded.
- **D4 — Routine refresh keeps CONNECTED; publication fails closed.**
  - A new `store.reference_checked` sets status with `CASE WHEN status='CONNECTED' AND collection_id=:current THEN 'CONNECTED' ELSE 'CHECKING' END`.
  - It advances `last_instrument_check_at` only `WHERE instrument_id = :verified_id`.
  - Publication may set `CONNECTED` only from `CHECKING`, `CONNECTED` or `DEGRADED`, never from `UNAVAILABLE`, and only when not overloaded.
- **D5 — Bounded writer starvation.**
  - `ingest()` takes `write_lock` per 32-row chunk plus its publish, with the binding captured once per call.
  - All fenced calls in `write_frames` run under `write_lock`, with `ingest_frames` as the lock-free hook.
  - Registration holds `write_lock` and `control_lock`, and sets `self.epoch` before releasing them.
- **D6 — Close and teardown.**
  - One shared constant `STREAM_CLOSE_TIMEOUT = 2` for `provider.py` and `ControlledProvider`.
  - Closes run as tracked `market-close` tasks and are never cancelled. The worker waits up to `close_timeout + 1` without cancelling; an overrun is logged, and the socket stays counted until it ends.
  - A two-socket gate prevents another replacement while a close is pending.
  - Teardown order:
    1. Cancel readers.
    2. Set the feeds `UNAVAILABLE COLLECTION_INTERRUPTED`.
    3. Drain the queue.
    4. Record the gap.
    5. Close sockets concurrently, with a bound.
  - A close log event records duration, close code and whether the close aborted.
- **D7 — Make-before-break rotation** (23 h, `serverShutdown`, D3 subscription change). The contract order is register, then revalidate, then open.
  1. Cancel maintenance.
  2. `store.register_collection(metrics)`: epoch+1 and the collection row, plus a fresh `market_worker_state` telemetry sample carrying the live `overloaded` flag. No feed reset.
  3. Revalidate the clock and instruments.
  4. Open the replacement, with its open timeout inside a 7 s budget measured from the start of the open.
  5. On the replacement's first frame, cancel the old reader synchronously and start the old socket's close in the background.
  6. Activate each symbol through D2 targets.
  7. The rotation is complete when every bound symbol has activated.

  No backfill runs during a rotation; hourly maintenance covers history.

  Failure handling:
  - **No first frame within budget:** close the replacement, keep the old generation current (pointers never moved), and record `STREAM_REPLACEMENT_FAILED {trigger, phase, elapsed_ms}`. Retry with backoff of at least 60 s and a cap of 5 attempts, then hand over to normal failure and recovery.
  - **First frame, but a symbol not activated within budget:** fail the collection with `phase=activation`. Unactivated symbols age into STALE (fail-closed).
  - A `serverShutdown` seen on the replacement queues the next rotation behind the close gate.
- **D8 — Failure evidence and backoff.**
  - `STREAM_ROTATION` detail: `{trigger, pending_collection_id}`.
  - `COLLECTION_GAP` detail adds `phase` and `failure_code`, taken from the first exception.
  - `attempts` resets once a collection has activated every bound symbol.
- **D9 — Read consistency.** `read.quote()` and `read.health()` use REPEATABLE READ, like `instruments()` at `read.py:50`.
- **D10 — Isolated-only rotation-age override.** A setting such as `ASL_MARKET_ROTATION_SECONDS` is refused unless `ASL_TEST_ISOLATED=1` and `ASL_DB_NAME` starts with `asl_m1_`, following the `fixture` guard at `worker.py:43-44`. It lets the guarded isolated public worker exercise real-provider rotations.

**Contract amendment.** Replace the MARKET_DATA.md:19 sentence "A reconnect or changed instrument snapshot requires a quote from the new generation before usability returns" with the rule stated in D2 and D7:
- A quote is usable only when its capture generation and instrument snapshot equal the feed's pointers.
- After a reconnect, pointers are reset.
- On a rotation or a changed snapshot, a symbol's pointers move only atomically with publication of that symbol's first quote bound to the new generation or snapshot.
- Rotation order is register, then revalidate, then open; it cuts over at the first replacement frame, with a 2 s close bound.

Update OPERATIONS.md:25-27 to match. The fallback if this is rejected is strict invalidation: move the pointer immediately, accepting ≤ 1 tick of fail-closed each hour.

## 5. Requirements and tests (PROPOSED)

New file `services/engine/tests/test_m2_stream_continuity.py`, plus revisions to existing tests.

**Fixture extensions**
- `fixture_worker.instrument(symbol, market_max_qty=…)` gains a `MARKET_LOT_SIZE` filter.
- `ControlledProvider` gains:
  - a configurable exchangeInfo sequence and call counter
  - an optional 720-row `klines`
  - symbol-aware `stream()`
  - a loopback TCP relay whose per-connection `freeze()` stops relaying but keeps both ends open, to reproduce a provider that never ends TCP
  - a background frame sender, needed because injected-clock jumps otherwise trip `stream_silent` at `worker.py:289-292`
- Values are synthetic and labelled FIXTURE, not copied from owner data.

| ID | Test | Asserts | Covers |
|---|---|---|---|
| T1 | Hourly drift: maxQty a→b→c→a, +61 s steps, streaming | No `STREAM_ROTATION`; collection and epoch unchanged; `maximum_connections==1`; feed `instrument_id` follows a,b,c,a (a reused); `read.quote` sampled every 50 ms is never non-VALID; status never `CHECKING` | Goal 1; D1, D2, D4 |
| T2 | Receipt-time binding (writer stalled across adoption) | A quote received before adoption keeps the old ID; one after gets the new ID; in every REPEATABLE READ sample, the pointer equals the latest quote's snapshot | D1, D2, D9 |
| T3 | Unchanged refresh / transient SOL failure / SOL `BREAK` | Timestamps advance with status still CONNECTED. Transient failure: no rotation, SOL fails closed despite new quotes, BTC VALID, then recovery. `BREAK`: subscription-change rotation to BTC only, SOL UNAVAILABLE | D3, D4 |
| T4 | Maintenance backfill under load (720 rows, ~50 frames/s) | No `QUEUE_OVERLOAD` or gap; sampled maximum queue age < 1000 ms | D5, Q06 |
| T5 | Rotation under load (23 h and `serverShutdown`) with a frozen-relay slow close | No gap or `TimeoutError`; quotes continuously VALID; per-symbol collection switch; no old-collection rows after the cut; old socket gone ≤ 3 s after the cut; overlap ≤ 10 s from open start; `maximum_connections==2` | Goal 3; D6, D7 |
| T6 | Silent replacement / replacement open failure (revised `test_supervised…` replacement_failure branch) | Old generation stays usable; `STREAM_REPLACEMENT_FAILED` recorded; retry after ≥ 60 s backoff (injected); pointers never move to the failed generation; ≤ 2 sockets | D7, D8 |
| T7 | Partial replacement (BTC only) | Gap has `phase=activation` and a `failure_code`; SOL fails closed; recovery restores both | D7, D8 |
| T8 | Overload during a slow-close rotation; close guard overrun | Gap `failure_code=QUEUE_OVERLOAD`, not `TimeoutError`; an overrun close is logged and still counted; no third socket | D6, D8 |
| T9 | Epoch race (5 back-to-back rotations, high frame rate); store unit tests | No `LostLease` or stop. Store: activation ordering when a later old quote is in the same batch; fail-closed transition; overload affects status only; `register_collection` keeps telemetry valid and carries `overloaded`; old epoch fenced out; `publish_pending` unchanged when there are no targets | D2, D4, D5, Q03 |
| T10 | Backoff reset; rotation-override guard | After a healthy collection, the next retry uses the first-attempt delay. The override is refused without isolation and honoured in the isolated run | D8, D10, Q04 |
| T11 | Existing-test revisions | `test_m2_worker.py:152` becomes a continuity assertion. Update Frame/SocketState constructors in the queue test and the stall hooks in the slow-writer, byte-saturation and `performance_recovery.py` code. `test_instrument_reversion…` unchanged | Regression |

## 6. Official sources and versions

- **websockets 17.0.1.** The locked version in `services/engine/uv.lock:598-599`; the cached source was inspected read-only.
  - Official docs: https://websockets.readthedocs.io/en/stable/reference/asyncio/client.html
  - Re-verify inside the built image: `close_timeout`, `max_queue` high/low water marks, and cancellation safety of `recv`/`close`. Update the [INTEGRATION_EVIDENCE.md](../../INTEGRATION_EVIDENCE.md) websockets row.
- **Binance EX-02 streams and EX-03 filters** ([REFERENCES.md](../../REFERENCES.md)).
  - Re-check `serverShutdown`, connection lifetime and `MARKET_LOT_SIZE` semantics.
  - Do not claim a documented hourly cadence unless the source states one; the design is cadence-independent.
- **Python `asyncio.Lock` fairness and `asyncio.timeout` semantics.** Verify against the image's Python version.
- **No new dependency.**

## 7. Data and trust-boundary changes

- **No schema change.**
- **Market worker DB role** gains new fenced write paths inside existing grants: `register_collection`, `publish_and_activate` and `reference_checked`.
- **API** changes to REPEATABLE READ reads only; it stays read-only.
- **Network:** no new destinations, credentials, private endpoints or browser-facing sockets. The provider allowlist is unchanged.
- **Test-only override** of rotation age is inert on the normal app.
- **Evidence rules unchanged:** observations stay append-only and deduplicated; there are no fabricated or backdated quotes; incidents are immutable.

## 8. Proposed file edits

- `services/engine/app/market_data/worker.py` — D1–D8, D10. Most of the change is in `read_socket`, `write_frames`, `ingest`, `refresh_references`, `maintain_references`, `consume` and `run`.
- `services/engine/app/market_data/store.py`:
  - `register_collection`, reused by `begin_collection`
  - `resolve_instrument`
  - `reference_checked`
  - `publish_and_activate`, with `publish_pending` kept as a wrapper
  - the fail-closed CONNECTED predicate
- `services/engine/app/market_data/pipeline.py` — `Binding`, `Frame.binding`, `SocketState` first-frame and activation tracking.
- `services/engine/app/market_data/provider.py` — `STREAM_CLOSE_TIMEOUT`, and an open-timeout parameter.
- `services/engine/app/market_data/read.py` — REPEATABLE READ in `quote()` and `health()`.
- `services/engine/app/market_data/acceptance.py` and `fixture_worker.py` — fixture extensions from §5.
- `performance_recovery.py` — hook update.
- `services/engine/tests/test_m2_stream_continuity.py` (new), `tests/test_m2_worker.py`, `tests/test_m2_completion.py` (only if needed).
- `tools/m2-acceptance.ps1`:
  - add the new test file to `WorkerFaults`
  - add an optional rotation-override parameter to `PublicWorkerStart`
  - add a new read-only `PublicWorkerContinuity` phase: a 1 Hz `read.health()`/`read.quote()` sampler plus incident, collection and instrument queries
- Docs:
  - `docs/MARKET_DATA.md` (contract amendment)
  - `docs/OPERATIONS.md`, `docs/TESTING.md:9`, `docs/INTEGRATION_EVIDENCE.md`
  - `docs/COMMANDS.md`, `docs/STATUS.md`
  - this plan file
  - Historical ExecPlan 0003 evidence stays unedited.

## 9. Implementation sequence (PROPOSED)

- **B0 — Reproduce first.**
  - Add the fixture extensions.
  - Add `phase`/`failure_code` to the gap detail and the close log event.
  - Write T5 (slow close) and T1 (drift) against the current code, and record that they fail with today's `TimeoutError` gap and rotation, in an isolated run.
  - Optionally review timestamped normal-app worker logs, read-only, for `market_collection_unavailable` attempts.
- **B1 — Close, teardown, masking and backoff** (D6, D8). This alone stops the close-timeout gaps.
- **B2 — Writer locking and fencing** (D5, excluding the ingest chunking).
- **B3 — Bindings and store functions** (D1, D2 store side, D4 store side, `register_collection`), plus `read.py` (D9). Store unit tests T9.
- **B4 — Adoption, subscription rule, routine refresh and per-chunk ingest** (D2–D5 worker side). Tests T1–T4.
- **B5 — Make-before-break rotation and isolated override** (D7, D10). Tests T5–T8, T10, T11.
- **B6 — Contracts and harness, then full isolated acceptance** (§10). Then run the isolated public worker across a real hour boundary, with rotation override 600 s, for at least 75 min.
- **B7 — Protected backup, normal deployment and soak** (§11). Then record the results in this plan, STATUS and COMMANDS.

## 10. Verification commands (PROPOSED — not yet run)

Isolated runs, with a fresh run ID:
```
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Prepare
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Build
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Checks
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Regression
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Performance
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PerformanceBurst
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PublicWorkerStart            # with rotation override, spans an HH:00
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PublicWorkerContinuity       # new, read-only
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PublicWorkerNetworkInterrupt # real-loss recovery still advances the generation
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PublicWorkerReport
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase PublicWorkerStop
./tools/m2-acceptance.ps1 -RunId continuity-<date> -Phase Stop
```

`WorkerFaults` must report 0 skipped. Record the pass counts versus the prior 20.

**Isolated acceptance budgets:**
- no `COLLECTION_GAP` or `STREAM_ROTATION` caused by drift
- at least one successful make-before-break rotation against the real provider, with the close duration and abort flag recorded
- the 1 Hz sampler shows `quote_usable` continuously across HH:59:30–HH:02:00, except for any logged, bounded rotation cut-over

## 11. Normal deployment with collection kept enabled (PROPOSED)

This follows [OPERATIONS §Milestone completion deployment](../../OPERATIONS.md#milestone-completion-deployment) and the [2026-09-28 local-deployment decision](../../DECISIONS.md#2026-09-28--completed-milestones-must-run-locally). It covers routine software updates only: collection stays enabled as previously activated in ExecPlan 0006, trading stays disabled, and no owner login or funding is involved.

1. **Confirm the starting state.**
   - Check the project, volumes, current image IDs and schema `0004_m2_completion`.
   - Check that `.env` has `ASL_MARKET_ENABLED=1` without printing secrets.
   - Tag the current `api` and `market-worker` images as `pre-0012` for rollback.
2. **Protected backup.**
   - Run `pg_dump -Fc` into `.cache/deployments/0012-<ts>/` and record a SHA-256 checksum.
   - There is no schema change, so an isolated restore is optional. Run a quick restore check anyway if time allows.
3. **Build and roll out.**
   - `docker compose config --quiet`
   - `docker compose --profile market build --quiet migrate api market-worker`
   - `docker compose run --rm --no-deps migrate` (a no-op that confirms head)
   - `docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 api`
   - `docker compose --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker`
   - Web is untouched.
4. **Verify the running release.**
   - Running image IDs match the build.
   - The in-container SHA-256 of the changed engine files matches the accepted commit.
   - The container environment shows collection enabled.
   - Readiness `read.health()` shows both feeds `quote_usable`, using the existing `exec -T -e ASL_DB_ROLE=market_worker market-worker python -c …` pattern.
   - An unauthenticated Chromium check of the sign-in page at `http://127.0.0.1:3000/` passes.
   - Record the one expected restart handover gap: a `COLLECTION_GAP` or lease handover of about 10–60 s.
5. **Soak across at least two consecutive hour boundaries.**
   - A 1 Hz health sampler runs from HH:59:30 to HH:02:00.
   - Read-only SQL since deployment should show:
     - no `STREAM_ROTATION`, `COLLECTION_GAP` or `STREAM_REPLACEMENT_FAILED`
     - new INSTRUMENT rows with changed `maxQty` under an unchanged `collection_id`
     - quotes after adoption carrying the new `instrument_id`
     - per-symbol maximum receipt gap between consecutive quotes ≤ 2.5 s around each HH:00
6. **Record** the commands and results, backup path and checksum, commit, image IDs, schema, URL, operating state and soak evidence in this plan, STATUS and COMMANDS.

**Rollback.**
- Re-tag the `pre-0012` images and recreate `api` and `market-worker`. No schema change means the rollback is image-only.
- Keep collection enabled and all observations and incidents.
- If isolated acceptance or the soak fails:
  - record the gate as FAILED
  - leave or restore the prior release
  - report the deployment as blocked
  - do not claim the M4 blocker is cleared

## Q01–Q10 applicability (PROPOSED)

| Gate | Applicability | Acceptance condition | Planned evidence |
|---|---|---|---|
| Q01 UX | Limited (no UI edits) | Markets and System stay live/ready across HH:00. New incident codes render through the existing generic list. | Unauthenticated Chromium check of the normal sign-in page. Signed-in Markets/System check across HH:00 by the owner, otherwise recorded as NOT RUN. No shadcn work. |
| Q02 Accessibility | NOT APPLICABLE | No shipped UI change | Reason recorded |
| Q03 Data correctness | Applicable (core) | Receipt-time binding; content-addressed reuse; publication-atomic activation; fencing/epoch ordering; fail-closed status; dedup; no fabricated quotes | T1–T3, T9; SQL evidence |
| Q04 Security | Limited | No new destinations, credentials or grants; override refused outside isolation; allowlist unchanged | Review, T10, `compose config` |
| Q05 Reliability | Applicable (core) | Drift continuity; make-before-break; bounded, non-raising close; replacement failure keeps the old generation; honest gaps; real-loss recovery unchanged | T1–T11, WorkerFaults, isolated public run, normal soak |
| Q06 Performance | Applicable | Declared budgets: queue age < 1 s at 50 frames/s during backfill and rotation; adoption causes no non-VALID sample; overlap ≤ 10 s; no regression in the 60-min and 5-min workloads | T4, T5, Performance, PerformanceBurst |
| Q07 Automated verification | Applicable | Engine lint, type, unit and integration checks pass in Docker, with no skipped tests | Checks, Regression, WorkerFaults |
| Q08 Visibility | Applicable | Trigger, phase, `failure_code`, elapsed time and close outcome are recorded; health stays truthful | T6–T8; soak incidents and logs |
| Q09 Deployment | Applicable | Backup and checksum; no-op migration; `api` and `market-worker` recreated; collection enabled; IDs match; soak passes; image-only rollback path | §11 record |
| Q10 Maintainability | Applicable | Contracts amended with the change; websockets 17.0.1 and Binance sources re-verified; no new dependency | Doc diffs, INTEGRATION_EVIDENCE |

**Related acceptance IDs**
- Addressed here: A06, A12, P02, P06.
- Unblocked, but not claimed, here: A30–A32 and A34 (protective exits on valid data).

## Decision log

- **Chosen: in-place adoption with deferred activation.** Rejected alternatives:
  - Removing `maxQty` from the hash, because it would store filter values that differ from the provider's.
  - Strict immediate invalidation, because it fails closed for up to a tick every hour; it stays the fallback.
  - Keeping the rotation and fixing only the close, because that still gives an hourly cut-over and extra REST weight.
- **Chosen: cut over at the first replacement frame.** Rejected: dual readers until full activation, because deduplication can starve the new generation and partial activation would need pointer rollback.
- **No backfill during rotation, 2 s close timeout, no migration, no UI change.**
- **Follow-ups, each outside this plan:**
  - Clock-uncertainty handling without teardown (the 13:47 gap).
  - REST weight budget during recovery.
  - `DEGRADED` status semantics.
  - Narrowing the backfill window.

## Progress

- OBSERVED (2026-09-28): the root-cause evidence above was gathered read-only.
- 2026-09-28: implementation started on branch `claude/market-stream-continuity` from `f7fad71`. Dated entries below record actual commands and results.

### Implementation record — 2026-09-28

**Harness portability (IMPLEMENTED).** This host has only Windows PowerShell 5.1.26100; no PowerShell 7 was found. `tools/m2-acceptance.ps1` used .NET Core-only `RandomNumberGenerator.Fill`/`Convert.ToHexString`. It also piped docker's stderr under `$ErrorActionPreference = 'Stop'`, which 5.1 turns into a terminating error. Secret generation now uses `RandomNumberGenerator.Create().GetBytes` with hex formatting. `Invoke-Compose` relaxes the preference only around the native call, and the exit code still decides failure. Both APIs also exist in PowerShell 7.

**B0 reproduction (OBSERVED, isolated run `continuity-b0`, unchanged worker).** The new fixture extensions and tests were run against the unchanged `4cfb8a4` worker:
- Synthetic `MARKET_LOT_SIZE.maxQty` drift made maintenance rotate (new collection, epoch 21→22). The writer then failed with `LostLease`, because a fenced writer call raced the epoch advance. The result was a `COLLECTION_GAP` with failure type `LostLease` and a `LostLease` drain failure. This confirms both the drift trigger and the writer epoch race.
- A 23 h rotation against a relay that stops answering the old socket ended in a `TimeoutError` gap. The queue was overloaded, with 256 frames captured and pending, and the drain failed with `LostLease`.
- A `serverShutdown` rotation against the same relay ended in the production signature: `COLLECTION_GAP` with `TimeoutError`, `captured_pending` 0 and no drain failure.

Logs: `.cache/m2/continuity-b0/b0-reproduction.log` and `b0-drift-detail.log`.

**Code (IMPLEMENTED).** D1–D10 were implemented as designed, with these specifics:
- **Receipt-time binding.** `pipeline.py` gains `Binding`. Each `Frame` records the socket's binding at construction, which happens at receipt.
- **Store.** `store.py` adds:
  - `register_collection` (fence advance with a fresh telemetry sample and no feed reset)
  - `resolve_instrument` (lookup only)
  - `clock_checked` and `reference_checked` (a successful check never downgrades `CONNECTED`)
  - `publish_and_activate`
  Publication may set `CONNECTED` only from `CHECKING`/`CONNECTED`/`DEGRADED`, only for a quote matching both feed pointers, and only when not overloaded.
- **Worker.** `worker.py` implements:
  - in-place adoption
  - the subscription rule
  - per-chunk ingest locking and writer calls under `write_lock`
  - make-before-break rotation with a first-frame cut
  - tracked, never-cancelled closes with a two-socket gate
  - teardown that records the gap before closing sockets
  - `phase`/`failure_code` in gap detail
  - backoff reset after a collection has delivered every bound symbol for 60 s
  - the isolated-only `ASL_MARKET_ROTATION_SECONDS` override
- **Provider.** `provider.py` uses `STREAM_CLOSE_TIMEOUT = 2`.
- **Read path.** `read.py` reads `quote()` and `health()` in REPEATABLE READ.
- **Compose.** `compose.yaml` passes `ASL_TEST_ISOLATED` and the override to `market-worker`, and the worker refuses the override outside a disposable database. The normal `.env` defines only `ASL_MARKET_ENABLED`.
- **Probe.** `continuity_probe.py` is a read-only 1 Hz sampler of the published quote/health path.

**Additional finding during verification (OBSERVED, then IMPLEMENTED).** The new samplers caught short windows in which both symbols read `UNAVAILABLE` while their feeds were `CONNECTED`:
- `read.health()` reported telemetry known, but the extrapolated oldest queue age was 1011–1048 ms.
- Cause: readers add a sample's age to its oldest pending frame. The worker sampled telemetry only about every 1.05 s, and a healthy writer usually holds a frame in its 100 ms batch window. So the extrapolated age crossed the 1000 ms bound for roughly 50–150 ms per second.
- This predates this plan and applies to the normal app at lower frame rates. Its production frequency was not measured.
- Fix: the worker now samples queue telemetry every 250 ms. The read rule and the one-second overload bound are unchanged.

**Test hygiene (IMPLEMENTED).** `tests/test_m2_integration.py::test_batched_frames_preserve_individual_receipt_and_lossless_raw` published BTC quotes up to 100 s in the future so each run's event times were unique. In a shared test database that correctly made BTC unusable for later tests until those quotes aged out. It now uses a unique past event time; its assertions are unchanged.

**Gap evidence precision (IMPLEMENTED after the first public window).** Rotations now happen inside one `consume` call. The gap detail's `collection_started_at` therefore now records the current generation's start rather than the start of the connection loop, and `started_at` records the last stream receipt. Before this change the first public run's network-interruption gap reported the loop start (19:28). The change affects failure detail only.

### Isolated verification — run `continuity-0928a`, 2026-09-28

Commands are recorded in [COMMANDS.md](../COMMANDS.md#execplan-0012-isolated-stream-continuity-commands--2026-09-28).

**Checks and suites**
- VERIFIED: `Checks` passed web lint, typecheck, unit tests, API-contract check, ruff, OpenAPI check, format check and production web build. No web source changed.
- VERIFIED, final source: `Regression` passed 84 engine tests on real PostgreSQL, with one pre-existing Starlette test-client deprecation warning.
- VERIFIED, final source: `WorkerFaults` passed 35 tests with none skipped; the M2 completion baseline was 20. The run covered `test_m2_completion.py`, `test_m2_worker.py` and the new `test_m2_stream_continuity.py` (T1–T11).
- VERIFIED: `RecoveryMemory` measured 30 recoveries after 5 warm-ups. Settled RSS growth was 436 KiB (70,560 → 70,996 KiB) with 0 retained market tasks.

**Real public provider, first window.** The public worker used unchanged public endpoints with the isolated-only `-RotationSeconds 600`, on source that predates only the gap-evidence change above. The read-only probe took 1560 samples at 1 Hz from 19:41:41 to 20:07:41 UTC: 0 unusable, longest unusable run 0.
- VERIFIED: four scheduled make-before-break rotations completed, at 19:38, 19:48, 19:58 and 20:08.

  | Rotation | Open → first frame | Cut → activation |
  |---|---|---|
  | 19:38 | 1232 ms | 1119 ms |
  | 19:48 | 1617 ms | 347 ms |
  | 19:58 | 1574 ms | 1116 ms |
  | 20:08 | 1052 ms | 911 ms |

- OBSERVED: every old-socket close received close code 1000 but no TCP end, so websockets aborted it at 2001–2002 ms (`timed_out: true`). This is direct provider evidence for the root cause: a TCP teardown longer than the old 5 s close bound.
- VERIFIED: the 20:00 UTC recomputation was adopted in place at 20:00:41 on unchanged collection epoch 5. BTC `MARKET_LOT_SIZE.maxQty` went 104.43982050 → 100.16429245 and SOL 87144.14274583 → 87169.55195833. Probe samples show quote snapshots switching between 20:00:41.7 and 20:00:42.7 with every sample usable.
- Incidents were exactly three `STREAM_ROTATION` (the scheduled ones inside the window) and no gap.
- OBSERVED, provider cadence: the largest receipt intervals between stored SOL quotes were 2.0–3.0 s, and each matched an equal source-event interval (for example 19:54:17.796 → 19:54:20.796). None coincided with a rotation or adoption, so these are provider event spacing, not capture gaps. The §11 soak criterion is refined accordingly: a worker-caused gap is a receipt interval that exceeds the matching source-event interval by more than 1 s, or any unusable probe sample.

**Real network interruption.**
- VERIFIED: `PublicWorkerNetworkInterrupt` passed.
- Both feeds were usable before, unusable 15 s into the disconnect, and usable again after reconnect on a new fenced generation (epoch 6 → 8).
- The gap recorded `failure_code: stream_silent`, `phase: streaming`. The dead socket's teardown close was bounded at 2003 ms with close code 1006, and recovery followed `stream_silent` (attempt 1) and `provider_dns_unavailable` (attempt 2).
- Two Windows PowerShell 5.1 quoting defects in this phase were fixed first: a double-quoted Docker template and double-quoted Python dictionary keys in native arguments. The first attempt failed at the ownership check, before any disconnect.

**Performance (Q06).** VERIFIED: `Performance` passed every declared bound: 250 ms p95, 1 s p99, 1 s schedule lag, 512 MiB RSS. The image was built at 19:41 UTC, before the failure-detail-only change above.

| Workload | Published | p50 | p95 | p99 | Schedule-lag p99 | Max RSS | CPU | Storage growth |
|---|---|---|---|---|---|---|---|---|
| Normal, 60 min | 10,800 / 10,800 | 137.0 ms | 143.8 ms | 149.9 ms | 2.04 ms | 71,652 KiB | 84.1 s | 14,843,904 bytes |
| Burst, 5 min | 30,000 / 30,000 | 146.9 ms | 168.7 ms | 175.3 ms | 1.98 ms | 74,236 KiB | 67.8 s | — |

The in-process API read measurement gave p95 12.1 ms sequential and 72.5 ms concurrent (concurrent p99 77.9 ms).

Against the [ExecPlan 0010](0010-release-readiness.md) final-source baseline there is no material regression:
- Normal p95: 141.8 → 143.8 ms.
- Burst p95: 162.3 → 168.7 ms.
- API concurrent p95: 76.6 → 72.5 ms.

This holds even though queue telemetry is now written about four times a second. The isolated public worker and its probe shared the host during these runs.

**Real public provider, second window.** The public worker was recreated at 20:15 on the image with the gap-evidence change. The probe took 3000 samples at 1 Hz from 20:16:01 to 21:06:01 UTC. Nine samples in four episodes were unusable, so this window is FAILED, and it led to the fix below.
- VERIFIED: five make-before-break rotations completed, at 20:25:50, 20:36:56, 20:48:01, 20:58:05 and 21:08:11.
  - Open → first frame: 1049–1829 ms.
  - Cut → activation: 346–1905 ms.
  - Every old close received code 1000, then was aborted at about 2001 ms.
- VERIFIED: the 21:00 UTC recomputation was adopted in place at 21:01:10 on the unchanged collection.
- Incidents were exactly five `STREAM_ROTATION`, with no gap and no replacement failure.
- OBSERVED, provider — SOL `STALE` at 20:34:55 and 20:45:29–30. SOL's Binance ticker event times paused 5.0 s and 6.0 s, and receipt intervals matched to the millisecond. The 5 s quote-age rule correctly failed closed. Provider event spacing above 5 s is a RISK_POLICY validation input ([RISK_POLICY.md](../../RISK_POLICY.md) calls the 5 s threshold a proposal to validate); it is not changed here.
- OBSERVED, worker defect — both symbols `UNAVAILABLE` with fresh quotes at 20:37:52–54 and 20:48:58–49:00.
  - Cause: the 20:35:50 and 20:46:56 rotations each spent about 60 s in revalidation. Their SOL exchangeInfo request waited on the local REST weight budget (for example 20:35:52 → 20:36:52).
  - Why the budget ran out (INFERRED): the budget honours Binance's IP-level `X-MBX-USED-WEIGHT-1M` header, and the unchanged normal worker shares this host's public IP. A single worker's own usage stays under the local 120 budget.
  - The schedule then broke the bound: the next refresh was due 60 s after the previous refresh *ended*, so the clock check made at the start of the delayed refresh aged to about 121 s. That crossed the 120 s reference bound for about 2 s.
- IMPLEMENTED: refreshes now start `REFERENCE_REFRESH_SECONDS = 45` after the previous refresh *started*.
  - A unit test pins this: a refresh that spent 60 s in REST still schedules from its start. `45 + 60 < 120`.
  - Local REST usage rises from about 43 to about 57 weight per minute, within the unchanged 120 budget.
  - Residual: back-to-back full-minute budget waits caused by other clients on the same IP can still age a check past 120 s; that fails closed.
- VERIFIED, final source (with the scheduling change):
  - `Regression`: 85 passed, one pre-existing warning.
  - `WorkerFaults`: 36 passed.
  - `RecoveryMemory`: 30 cycles, 428 KiB growth, 0 retained tasks.
  - `Performance` was not rerun: the only changes since are failure-detail fields and the refresh interval, which is served by the synthetic REST fake in that workload.

**Real public provider, third window (final source `ac38d15`).** The public worker was recreated at 21:15 on the final image. The probe took 3000 samples at 1 Hz from 21:15:33 to 22:05:33 UTC: 4 unusable.
- VERIFIED: seven rotations completed — five inside the window (21:25, 21:35, 21:45, 21:55, 22:05) and two after it — plus the 22:00 UTC in-place adoption. Incidents were exactly seven `STREAM_ROTATION`, with no gap and no replacement failure. Across the three windows, 16 real-provider rotations completed make-before-break with no gap.
- OBSERVED, provider: one SOL `STALE` sample at 21:29:41, during a 6.000 s provider event gap.
- OBSERVED, residual: 3 s of BTC-only `UNAVAILABLE` at 22:02:55–57.
  - BTC's changed snapshot had been verified at 22:00:55 early in one refresh. That refresh's SOL request then waited 60 s on the REST budget.
  - The next refresh started immediately, and its BTC request also waited 60 s, until 22:02:58.
  - This is the back-to-back-wait residual recorded above, and it failed closed. It needs IP-level saturation from a second client, here the unchanged normal worker, whose hourly failure and recovery added REST weight around 22:00.

The isolated containers were then stopped (`PublicWorkerStop`, `Stop`, no `-v`), and the task volumes and evidence were retained. `Snapshot` recorded base commit `ac38d156493b87ad9810d8e2f5855f4d5c8ac46f` with 165 source hashes and 15 image identities in `.cache/m2/continuity-0928a/source-images.json`.

### Normal deployment — 2026-09-28

The deployment ran from the checkout at `ac38d156493b87ad9810d8e2f5855f4d5c8ac46f`, with a clean working tree at build time.

- **Starting state.** Schema was `0004_m2_completion`. API image `sha256:9be9e200d9ba0ea47b39a118ee81c909d561b16a8520d51842e0d7e72908b676`, market-worker `sha256:b135fa9b6fbf161e98ef12393e561969f4e81e6fba1128dce6112da9904ab5d1`, migrate `sha256:2b545ea2f4f01b8ae0757509707581517094e3da4c7dc4543b3af4c7e382d2cd`. All three were tagged `pre-0012` for rollback. The local `.env` defines only `ASL_MARKET_ENABLED`.
- **Protected backup.** `pg_dump -Fc` was copied to `.cache/deployments/stream-continuity-20260928a/stream-continuity-20260928a.dump`: 56,600,662 bytes, SHA-256 `3a52c4b145cff398ef3d1f9f1191b2bb6c3da7017edaa946514539e8c504a207`, identical in the container and on the host. The directory's ACL grants only SYSTEM, Administrators and the owner account, as for earlier deployments. The in-container temporary copy was removed afterwards. No isolated restore was run because there was no schema change (NOT RUN).
- **Rollout.** `docker compose config --quiet`, `docker compose --profile market build --quiet migrate api market-worker`, `docker compose run --rm --no-deps migrate` (no-op), then `docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 api` (22:30:10 UTC) and `docker compose --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker` (22:30:18 UTC). All exited 0. Web and PostgreSQL were not recreated.
- **Running identity (VERIFIED).**
  - API container `231102aa8b6c` runs image `sha256:0a1664ca92b6c9fec0ebf620e9225f9bc93511e19e432fb4845abe76bd38dc86`.
  - Market-worker container `6c1bc1f91ea7` runs `sha256:348804f6633c1b44ff57e33adc7145ea684b0dc9793883ad18acbeca5d8cef25`, and migrate is `sha256:64129823f59c8d943ac11df863273e2602b1b858b3a14fe72bbea33bf74f45e8`.
  - All 18 compared in-container market-data source files (nine per service) matched the checkout byte-for-byte.
  - Worker environment: `ASL_MARKET_ENABLED=1`, `ASL_TEST_ISOLATED=0`, database `asl`, empty rotation override.
- **State after rollout (VERIFIED).**
  - Schema stayed `0004_m2_completion` and the API readiness route returned 200.
  - The API's startup reconciliation left the account initialized, unpaused and not reconciliation-failed, with 0 `RECONCILIATION_FAILED` audit events (read-only check).
  - Unauthenticated host GETs to `/`, `/markets` and `/system` returned 200. The in-app browser showed the owner sign-in form and a System page reading Account funded, Market data ready, Model runtime unconfigured and Paper trading disabled.
  - No owner login, funding or activation change was performed.
- **Handover (OBSERVED).**
  - The new worker took lease epoch 46 at 22:30:29.95, started collection epoch 47 and connected at 22:30:37.43.
  - The last quotes from the old worker were received at 22:30:18.1 (BTC) and 22:30:18.9 (SOL); the first new quotes at 22:30:38.1 and 22:30:37.9. The restart therefore cost about 19–20 s of capture. A graceful stop records no `COLLECTION_GAP`.
  - A 60-sample probe right after startup found 0 unusable samples.
  - The last pre-deployment hourly failure is visible at 22:01:08–22:01:27: `STREAM_ROTATION` followed by a `TimeoutError` gap.

### Normal soak — 2026-09-28/29

A read-only probe inside the normal market-worker container sampled the published quote/health path once per second for two consecutive hours. During the soak no isolated worker shared the public IP.

| Window (UTC) | Samples | Unusable | Hour boundary | In-place adoption (unchanged collection epoch 47) |
|---|---|---|---|---|
| 22:33:36–23:33:35 | 3,600 | 0 | 23:00 | 23:00:37. BTC `maxQty` 97.53480451 → 99.55691645, SOL 83073.37581171 → 79159.42732500. Probe snapshots switched at 23:00:38 (SOL) and 23:00:39 (BTC). |
| 23:33:58–00:33:57 | 3,600 | 0 | 00:00 | 00:00:48. BTC 99.55691645 → 98.76033441, SOL 79159.42732500 → 80822.22639583. Both snapshots switched at 00:00:49. |

VERIFIED from read-only market-table queries covering 22:30 to 00:34 UTC:
- 0 incidents: no `STREAM_ROTATION`, `COLLECTION_GAP` or `STREAM_REPLACEMENT_FAILED`.
- One collection, the one the deployment started.
- Feeds `CONNECTED` on the adopted snapshots, with check times advanced at each adoption.
- By the refined criterion, no worker-caused gap: no receipt interval exceeded its matching Binance source-event interval by more than 10 ms. Among intervals whose first quote was after 22:30:40, the largest receipt gaps were 3.0 s (BTC) and 5.0 s (SOL), each equal to the provider's own event spacing.
- The largest sampled SOL quote age was 4.48 s.

## Completion evidence

**Gate dispositions**

| Gate | Result | Evidence |
|---|---|---|
| Q01 UX | VERIFIED (limited scope) | No UI change. System showed Market data ready after rollout, and the sign-in form rendered. A signed-in Markets view across HH:00 was NOT RUN; no owner session was used. |
| Q02 Accessibility | NOT APPLICABLE | No shipped UI change. |
| Q03 Data correctness | VERIFIED | Store activation, fail-closed status and receipt-binding tests (T2, T9). Real-provider adoptions at 20:00, 21:00, 22:00, 23:00 and 00:00 moved pointers only with bound quotes. Reconciliation was unlatched after rollout. |
| Q04 Security | VERIFIED | No new destinations, credentials or grants. The override test refuses a non-isolated database. The normal container's override is empty and `ASL_TEST_ISOLATED=0`. |
| Q05 Reliability | VERIFIED, with residuals below | 36 worker faults; 16 real-provider rotations and the network-interruption recovery; two-boundary normal soak with 7,200/7,200 usable samples. |
| Q06 Performance | VERIFIED | Declared budgets passed with no material regression. The backfill-under-load test kept queue age under 1 s. |
| Q07 Automated verification | VERIFIED | `Checks`, `Regression` (85 passed) and `WorkerFaults` (36 passed) in Docker, with no skips. |
| Q08 Visibility | VERIFIED | Rotation, adoption, activation and close events. Gap `phase`/`failure_code` were verified in tests and the network interruption. The continuity probe was added. |
| Q09 Deployment | VERIFIED | Protected backup and checksum, no-op migration, image identities, file hashes, collection enabled, two-boundary soak; `pre-0012` rollback tags retained. Isolated restore was NOT RUN because there was no schema change. |
| Q10 Maintainability | VERIFIED | MARKET_DATA, OPERATIONS, TESTING, INTEGRATION_EVIDENCE, COMMANDS and STATUS were updated. websockets 17.0.1 semantics were checked in the built image. No new dependency. |

**Residual limitations and follow-ups**
- **Back-to-back REST waits.** Two consecutive full-minute REST weight-budget waits, possible only when another client saturates the shared IP's Binance weight, can age a reference check past 120 s for a few seconds. The feed fails closed. Folded into the existing REST-budget follow-up.
- **Provider ticker pauses.** Binance's SOL ticker occasionally pauses 5–6 s. It was observed three times in isolated windows, and each time SOL read `STALE` for one or two samples. The 5 s quote-age proposal in RISK_POLICY is a validation input for M4; it is not changed here.
- **Clock uncertainty.** A clock-uncertainty failure still tears down the collection (for example the 13:47 gap); this was excluded and remains a follow-up.
- **Rotation age.** The 23 h scheduled rotation against the real provider was exercised only with the isolated 600 s override, not at 23 h.

**Git.** `ac38d15` (implementation, deployed) was merged with the documentation-only `31e2d73` (M3 ExecPlan 0011, pushed from another worktree during this work) as `02f3790`. This record is committed on top. Publication of `main` follows this commit and is not itself recorded here.

**Next task.** M3 per [ExecPlan 0011](0011-paper-broker-reference.md), once authorized. The hourly quote outage that plan lists as a pre-M4-activation blocker is resolved on the normal app by this deployment, subject to the residual limitations above.

**Cleanup — 2026-09-29 (owner request).** The M3 rollout moved the database to schema `0005_m3_paper_broker`, and the `pre-0012` images were built for `0004`, so they were no longer a rollback path (see ExecPlan 0011's rollback note). The three `pre-0012` image tags (`api`, `market-worker`, `migrate`) were deleted after checking that no container used them. The four isolated task volumes of runs `continuity-b0` and `continuity-0928a` were also deleted; no containers or networks remained. The run evidence under `.cache/m2/continuity-*` is kept. The M3 release's own rollback tags are `pre-m3` ([ExecPlan 0011](0011-paper-broker-reference.md)).
