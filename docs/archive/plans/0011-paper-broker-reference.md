# ExecPlan 0011 — M3 deterministic paper broker and reference strategy

**Status: IMPLEMENTED — implementation authorized by the owner on 2026-09-29 ("implement M3 per ExecPlan 0011").** The sections below keep the approved design as written (PROPOSED labels are historical); §14 records what was actually built, every deviation, and the acceptance and deployment results, which take precedence. Planning session 2026-09-28 (read-only).

**Update 2026-09-29 (OBSERVED):** the hourly quote outage described in §0 and §2.4 now has its own plan, ExecPlan 0012 (`docs/plans/0012-market-stream-continuity.md`, not yet merged to `main`). It is implemented on branch `claude/market-stream-continuity` (commit `ac38d15`) and verified in isolation, but not yet deployed to the normal app. That plan also records provider-side SOL ticker pauses of 5–6 s, which correctly fail closed under the 5 s quote-age rule. Consequences for M3:
- The pre-M4 blocker becomes "ExecPlan 0012 deployed, with real-provider continuity verified on the normal app".
- M3 implementation must start from whichever baseline is current and recheck the §2 file/line citations, which describe `main` at `f7fad71`.
- The engine's quote-freshness and hourly-gap tests stay required regardless. Tags: **PROPOSED** (design or command not yet built or run), **OBSERVED** (seen in the repository, Docker state, official documentation or a read-only query during planning), **IMPLEMENTED**/**VERIFIED** (only for historical evidence recorded by earlier plans). Nothing in M3 is implemented or verified yet.

---

## 0. One-screen summary

**Scope (PROPOSED).** On the existing engine/web/PostgreSQL stack, M3 adds:
- an internal `PaperBroker` for marketable, IOC-style BTCUSDT/SOLUSDT spot orders over M2's sampled top-of-book quotes;
- a versioned cost model whose unknown inputs stay `UNSET`;
- point-in-time exchange-filter and rounding rules;
- a generalized double-entry ledger (trade postings, holdings, per-asset reservations, bid-marked valuations);
- the independent `PAPER_PILOT_V1` risk gate with persistent latches;
- immutable position mandates with engine-triggered protective exits;
- `TREND_REFERENCE_V1`;
- one fenced execution authority with deterministic step ordering and crash recovery;
- an isolated database-backed replay;
- read-only Orders, Positions and Risk pages.

It deploys to the normal app **inert**.

**Key decisions (PROPOSED).**
1. Only SYSTEM creates orders (reference-strategy signals and deterministic protection). There is no manual, agent, approval, run, start/pause/resume/flatten or new funding path. Main-account activation is structurally `BLOCKED` in M3; only a guarded test provider and the isolated replay can activate.
2. **Fill model — IOC.** Each order uses one eligible quote snapshot after a modeled arrival delay, at a capped share of the displayed best-level quantity minus liquidity already consumed at that level; the remainder is canceled.
   - Buys fill at the ask and sells at the bid, so the spread is counted once.
   - **Sampled top-of-book is sufficient; full depth is not needed**, because no order walks the book.
3. Commission is charged in the received asset (buy→base, sell→quote), as Binance documents without BNB. Rate, arrival delay, participation, slippage and entry envelope are `UNSET` until the owner approves a labeled hypothetical scenario (M4). `UNSET` blocks every non-fixture fill.
4. **Filters and rounding.**
   - Filters come from the instrument snapshot current at decision time, and are revalidated at fill against the fill quote's snapshot.
   - Quantities always round down, and any minimum failure is a no-trade.
   - Unknown filter types make the instrument ineligible.
   - Buy commission in base creates explicit, valued dust.
5. `PAPER_PILOT_V1` numbers apply exactly as written, to bid-marked equity including pending commitments. Daily and drawdown latches are append-only, survive restarts and top-ups, and have no clearing path in M3.
6. **Execution worker and identities.**
   - A new `execution-worker` (engine image, private network only) is the single fenced execution authority. It is **built but not started** on the normal app.
   - Its database role is created **NOLOGIN** until M4 activation.
   - Database triggers ensure that the API can post only funding journals and the worker only fill journals. Latches can never be cleared, the high-water mark can never fall, and the fencing epoch can never decrease through application roles.
7. Replay runs only in a separate Compose project and PostgreSQL cluster, with no route to the owner's database; every output is labeled modeled.

**Open owner decisions — none block M3; all are M4 activation gates.** Proposed values are in §5.4, §5.7 and §5.9.
- (a) Approve `PAPER_PILOT_V1` with the M3 interpretations: bid-marked NAV, the late-daily-reference rule and the planned-open-risk definition.
- (b) Approve `TREND_REFERENCE_V1` with its execution settings: entry reference = signal close, 600-second signal validity and a priority-ordered 60-second checkpoint.
- (c) Approve hypothetical cost scenario H1 (with stress scenario H2 kept separate), or keep the cost scenario `UNSET`.
- (d) Authorize the separate fix for the hourly quote outage (below) before any forward run.

**Contradictions found — none block M3.** One wording conflict and seven gaps are reconciled by documentation updates in I0 (§3.4). The wording conflict is MARKET_DATA's "quotes are never executable prices" against PAPER_EXECUTION's fills from ask/bid. It is not material because PAPER_EXECUTION owns fill modeling, and MARKET_DATA itself lists "quotes for execution".

**Implementation/provider conflict (OBSERVED).** Binance changes `MARKET_LOT_SIZE.maxQty` every hour. The M2 worker rotates its stream on any instrument change, and the rotation times out, leaving **50–85 s without quotes at the top of every hour**. That is exactly when 1h signals execute, and stops cannot be evaluated during the gap. M3 leaves the market worker unchanged, as instructed, and handles the gap honestly. The fix is a pre-M4 blocker for a separate ExecPlan; the owner started that separate planning task on 2026-09-29.

**Main risks.**
1. The hourly outage.
2. Milestone size. Mitigation: ten independently verifiable increments.
3. Concurrency and unknown-commit defects in money paths.
4. Dynamic filters and undocumented zero semantics.
5. Fidelity limits: 1-second samples; no queue position, market impact or exchange reference price.
6. A migration that alters M1 journal tables on the live owner database.
7. Replay isolation mistakes.
8. UI honesty: a planned stop must never read as guaranteed.

---

## 1. Goal and observable outcome

**PROPOSED.** After M3, in isolated acceptance projects:
- A labeled synthetic or replayed feed drives the full `TREND_REFERENCE_V1` path:
  - from finalized 1h bars, through a risk-checked and reserved modeled fill;
  - to a balanced journal and a position with an immutable mandate;
  - to a protective, time or trend exit.
- That path is exercised with partial fills, rejections, expiries, sell dust, and a gapped stop whose realized loss exceeds its planned loss. It also recovers after forced kills and when two workers compete.
- The same recorded events produce identical orders, fills, journal entries and positions, and replay cannot write to the owner's account.
- The UI shows orders, fills, positions, mandates and risk honestly: inactive, unapproved, `UNSET`, stale and unavailable states, plus modeled labels.

On the normal app after deployment:
- Schema is `0005_m3_paper_broker` and the new read-only pages are available.
- Activation shows as blocked, with reasons.
- There are zero orders, fills, positions and latches.
- The execution worker is built but not running, and its role is NOLOGIN.
- Funding and approvals are unchanged, and public collection is still enabled.

---

## 2. Current repository facts

### 2.1 Baseline (OBSERVED)
- **Repository and plans:**
  - `main` is at `f7fad71725f469070e8ccd6c14e90b1b33932daf`, with a clean working tree.
  - M0–M2 are complete ([STATUS.md:7-25](../../STATUS.md)). The M3 row reads "Not implemented by pack" ([STATUS.md:38](../../STATUS.md)).
  - Plans 0001–0010 exist, so the next number is 0011.
  - The inventory at [README.md:67-72](../../README.md) omits plans 0002, 0003, 0005 and 0010.
- **Normal Compose project (`adaptive-spot-lab`):**
  - `api`, `web` and `postgres` are healthy, and `market-worker` is running.
  - Only web is published, on `127.0.0.1:3000` ([compose.yaml:148](../../../compose.yaml)).
  - Running image IDs match the release recorded in [0010-release-readiness.md:111](0010-release-readiness.md).
- **Schema and database identities:**
  - Schema head is `0004_m2_completion`. API readiness requires an exact match ([db.py:8](../../../services/engine/app/db.py), [db.py:51-58](../../../services/engine/app/db.py)). The market worker neither checks the revision nor imports `read.py`.
  - The live revision was not queried directly: planning SQL was limited to market tables. It was observed indirectly. The running API image's healthcheck calls `/v1/health/ready` ([compose.yaml:88-89](../../../compose.yaml)), which passes only when `alembic_version` equals `0004_m2_completion`, and the API reported healthy.
  - The only identities are `migration` (`asl`, superuser), `api` (`asl_api`) and `market_worker` ([db.py:28-36](../../../services/engine/app/db.py)).
  - Statement, lock and idle timeouts apply only to `api` and `market_worker` ([db.py:19-25](../../../services/engine/app/db.py)).
- **Migrations:** Alembic runs all pending revisions in one transaction as the superuser. Hand-written revisions are required, because the ORM metadata maps only `system_metadata`.
- **Owner-supplied current state:** all five points were checked against the repository and found accurate — M0–M2 complete; app on `127.0.0.1:3000` at `0004_m2_completion`; collection on, with both feeds `CONNECTED`; paper trading off and model unconfigured (`SystemStatus` literals); no M3 ExecPlan, next number 0011.

### 2.2 Accounting and ledger (OBSERVED)
- **Journal schema:**
  - `journal_transactions.funding_request_id` is `NOT NULL UNIQUE` ([0002_m1_account.py:92](../../../services/engine/alembic/versions/0002_m1_account.py)), so no trade can be posted today.
  - CHECKs allow the book accounts `OWNER_CASH`, `VIRTUAL_CAPITAL`, `CLEARING` and `EXPENSE`, and the assets `USDT`, `BTC` and `SOL` ([0002:103-104](../../../services/engine/alembic/versions/0002_m1_account.py)).
  - A deferred trigger enforces per-asset balance with at least two postings, and append-only triggers protect journal, decision, audit and outbox rows ([0002:149-168](../../../services/engine/alembic/versions/0002_m1_account.py)).
- **Postings and reconciliation:**
  - `_post_funding` is the only journal writer ([accounting.py:191-243](../../../services/engine/app/accounting.py)).
  - Equity is cash ([accounting.py:101](../../../services/engine/app/accounting.py)).
  - Reconciliation assumes NAV = cash/units and USDT-only reservations. On a mismatch it latches both `reconciliation_failed` and `paused`, and funding is then refused ([accounting.py:191-197](../../../services/engine/app/accounting.py), [accounting.py:362-398](../../../services/engine/app/accounting.py)).
  - The high-water mark is never raised after initialization.
- **Fencing, reservations and grants:**
  - `account_state.fencing_epoch` exists, but nothing increments it.
  - `reserve_quote`/`release_quote` are unrouted stubs that support only `ACTIVE|RELEASED` ([accounting.py:317-359](../../../services/engine/app/accounting.py)).
  - `asl_api` holds journal INSERT and column UPDATE on `account_state`, including `fencing_epoch` ([0002:180-187](../../../services/engine/alembic/versions/0002_m1_account.py)).
- **Test fixtures:** they truncate a fixed M1 table list as `asl` in disposable `asl_m1_` databases ([test_m1_account.py:23-35](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/tests/test_m1_account.py)). Engines for other roles are created per test ([test_m2_integration.py:19-37](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/tests/test_m2_integration.py)).

### 2.3 Market data (OBSERVED)
- **Quote source and freshness:**
  - Quotes come from `@ticker`: 1-second snapshots of best bid/ask with displayed quantities and an event time.
  - `read.quote()` marks a quote STALE when its event or receipt age exceeds 5 s. It marks it UNAVAILABLE unless the lease, feed, telemetry, generation, instrument and clock checks all pass.
  - It uses wall-clock `now` and always returns `executable: false` ([read.py:96-158](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/market_data/read.py)).
  - The same rules are duplicated in `health()`.
- **Instruments, publications and candles:**
  - Filters are stored as raw JSONB, and unknown filter types are preserved.
  - Publications carry a commit-ordered `sequence` watermark.
  - `read.candles()` returns string DTOs and includes provisional bars.
- **Evidence pins:** `market_evidence_pins` is keyed by `observation_id` alone, and M2 retention skips pinned rows.
- **Fidelity:** ExecPlan 0003 recorded that the ticker yields sampled top-of-book observations, not a book or trade tape, and that M3 must assess that fidelity ([0003-market-data-charts.md:57-59](0003-market-data-charts.md)).
- **Lease pattern to copy:** acquire only when expired, with an epoch increment; renewal extends only expiry; a `FOR KEY SHARE` fence; `UNIQUE(id, owner_id, epoch)` ([store.py:29-81](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/market_data/store.py)).

### 2.4 Measured feed behavior (OBSERVED)
Source: normal database, market tables only, read in `BEGIN TRANSACTION READ ONLY`, window 2026-09-28 10:53–16:53 UTC.

| Measure | BTCUSDT | SOLUSDT |
|---|---|---|
| Quotes | 20,705 | 20,451 |
| Inter-quote gap p50 / p90 / p99 | 1.000 / 1.001 / 1.002 s | 1 / 1.001 / 2 s |
| Gaps > 5 s: six hourly rotations (50–85 s), three gaps in two deployment windows (12:22; 12:43–12:48), one clock-uncertainty recovery (13:47, 107 s) | 10 (max 269 s; 847 s beyond 5 s age) | 10 (max 183 s; 761 s beyond 5 s age) |
| Receipt − source event p50 / p99 / p99.9 | 130 / 763 / 1,903 ms | 128 / 538 / 1,758 ms |
| Availability − receipt p50 / p99 | 141 / 163 ms | 144 / 168 ms |
| Spread p50 / max | 0.0012 bps (1 tick) / 0.56 bps | 0.84 bps (1 tick) / 0.85 bps |
| Displayed ask notional p1 / p10 / p50 | 175 / 19,470 / 452,075 USDT | 244 / 8,167 / 21,109 USDT |
| Consecutive quotes with unchanged best prices | 66% | 58% |
| Stream-finalized 1h bar available after close p50 / p99 | 0.31 / 0.42 s | 0.61 / 0.70 s |

- **Hourly outage.** Every hour there is one `STREAM_ROTATION`. About 20 s later come a `TimeoutError`, a `COLLECTION_GAP` and a new collection.
  - The rotation coincides with a new instrument snapshot in which only `MARKET_LOT_SIZE.maxQty` changed. Examples: BTC `139.00391379 → 139.69167145 → 133.01644604`; SOL `72459.52978750 → 77641.08365416 → 79574.48870416`.
  - The worker rotates on any snapshot change ([worker.py:376-390](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/market_data/worker.py)) and gives the replacement socket 5 s to become ready ([worker.py:456-473](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/market_data/worker.py)). Why readiness times out is a hypothesis for the follow-up plan.
- **Current filters** (snapshot received 16:00:34 UTC):

  | Filter | BTCUSDT | SOLUSDT |
  |---|---|---|
  | `LOT_SIZE` | min/step `0.00001`, max `9000` | min/step `0.001`, max `90000` |
  | `MARKET_LOT_SIZE` | min `0`, step `0`, max varies hourly | min `0`, step `0`, max varies hourly |
  | `NOTIONAL` | min `5`, max `9000000`, `applyMinToMarket=true`, `applyMaxToMarket=false`, `avgPriceMins=5` | same |
  | `PRICE_FILTER` | tick `0.01` | tick `0.01` |

  Both symbols also carry `PERCENT_PRICE_BY_SIDE`, `ICEBERG_PARTS`, `MAX_NUM_ORDERS=200`, `MAX_NUM_ALGO_ORDERS`, `MAX_NUM_ORDER_AMENDS`, `MAX_NUM_ORDER_LISTS` and `TRAILING_DELTA`. Commission precision is 8.

### 2.5 Web (OBSERVED)
- **Routes and status schema:**
  - Only `/`, `/markets` and `/system` exist, with inline nav that does not wrap ([__root.tsx:64-92](../../../apps/web/src/routes/__root.tsx)).
  - There is no Orders, Positions or Risk route, query, server function or OpenAPI path.
  - System status is strict, with `trading: z.literal("disabled")` ([status.schema.ts:4-11](../../../apps/web/src/system/status.schema.ts); API [main.py:44-52](../../../services/engine/app/main.py)).
- **shadcn:**
  - Preset `b2fms61Bqi`, Base UI, `base-nova`.
  - Installed primitives: alert-dialog, alert, badge, button, card, empty, field, input, label, separator, skeleton, spinner, table, toggle-group, toggle.
  - Not installed: DataTable, Tabs, Select, Tooltip, Pagination and Sidebar.
- **Reusable pieces:** TanStack Table v9 render loops are repeated in three files. `privateApi` has a 5-second deadline, bounded bodies and forwarded signals. `formatDecimal`/`formatUtc` exist.
- **Skills:**
  - The official shadcn skill was read from `C:\Users\owner\.codex\skills\shadcn\SKILL.md`.
  - `shadcn info --json` was **not run**, because it needs a registry download. It is deferred to implementation in the pinned `web-tools` image with bridge networking, as M2 did.
  - No chart change is planned, so the Lightweight Charts skill was not needed.

### 2.6 Order sources allowed by the contracts (OBSERVED)
- Only SYSTEM executes accepted paper orders and posts fills, in a fenced transaction ([AUTONOMY_MATRIX.md:38](../../AUTONOMY_MATRIX.md)).
- Coordinator intents belong to M7 ([AUTONOMY_MATRIX.md:29](../../AUTONOMY_MATRIX.md)).
- Manual paper orders are excluded ([API_CONTRACTS.md:49](../../API_CONTRACTS.md)).
- Start, pause, resume and flatten, plus run manifests, belong to M4 ([ROADMAP.md:33-37](../../ROADMAP.md); [API_CONTRACTS.md:40-45](../../API_CONTRACTS.md)).
- M3 forbids an automatically started forward experiment ([ROADMAP.md:31](../../ROADMAP.md)).

---

## 3. Scope, exclusions and milestone boundaries

### 3.1 In scope (PROPOSED)
- **Trading core:** broker, cost model, filter and rounding policy, ledger generalization, valuation, risk gate, mandates, protection engine, `TREND_REFERENCE_V1`.
- **Runtime:** execution worker and lease, deterministic ordering and recovery, replay.
- **Owner-facing:** read-only APIs and UI.
- **Delivery:** harness extensions, canonical contract updates, inert deployment.

### 3.2 Excluded (PROPOSED)
- **Owner controls:** manual orders; approvals or approval UI; run manifests or experiment tables; start, pause, resume and flatten; clearing any latch.
- **Money:** funding changes beyond holdings-aware valuation.
- **Execution and data:** resting limit orders; depth or trade-tape collection; any change to the market worker.
- **Later-milestone features:** model, agent and research code; evaluation metrics, baselines and performance reports; chart changes.
- **Real exchange access:** any live, Testnet or Demo path, credential or signed endpoint.

### 3.3 Boundaries with later milestones (PROPOSED)
| Milestone | Receives from M3 | Must add itself |
|---|---|---|
| M4 | Broker, risk gate, mandates, strategy, replay, hashed definitions, blocked-activation reasons | Owner approval of exact hashes; run manifests; start/pause/resume/flatten; latch clearance; activation for an approved run; enabling the execution identity (LOGIN) and worker; evaluation, baselines and reporting marks; downtime disclosure; the hourly-outage fix |
| M5 | Error codes, the fenced submission path | Model runtime and tool loop |
| M6 | A deterministic core usable by research | Shadow accounts (multi-account) and the research worker |
| M7 | A single broker path, mandate rules, cancel/fill race handling | Trade intents, discretionary exits, stop tightening, turnover limits |
| M8 | The recovery and fault harness | Sustained forward evidence and a reliability review |

### 3.4 Contract reconciliation (PROPOSED)
None of these blocks M3. Each is resolved by documentation updates in I0, before the code that depends on it.

1. **Quote executability wording.**
   - The texts: [MARKET_DATA.md:13](../../MARKET_DATA.md) says quotes are "never executable prices", and [API_CONTRACTS.md:13](../../API_CONTRACTS.md) says `executable` is always false. Meanwhile [PAPER_EXECUTION.md:27](../../PAPER_EXECUTION.md) models fills from ask/bid, and [MARKET_DATA.md:29](../../MARKET_DATA.md) lists "quotes for execution".
   - Why it is not material: PAPER_EXECUTION owns the fill model, and the M2 statement concerns real executability.
   - Clarification: sampled level-1 quotes are not guaranteed executable prices. They are the approved modeled-execution input at fidelity `SAMPLED_L1_TICKER`.
   - Market reads keep `executable: false`, and fills record `execution_fidelity`.
2. **Worker naming.** [ARCHITECTURE.md:11](../../ARCHITECTURE.md) and [DOCKER.md:7](../../DOCKER.md) describe one logical `worker`. Record the split into `market-worker` and `execution-worker`.
3. **Experiment reference on orders** ([PAPER_EXECUTION.md:13](../../PAPER_EXECUTION.md)). Experiments belong to M4, and the owner excluded run manifests from M3.
   - Orders therefore carry the account, the mode, the activation kind, the definition hashes and a nullable run reference that M4 will constrain.
   - The main account can hold no orders in M3.
4. **Intent timelines** ([FRONTEND.md:20](../../FRONTEND.md)). For the FIXED policy, the "intent" is the strategy signal plus its risk decision. Agent intents remain M7.
5. **Quality vocabulary** ([DATA_CONTRACTS.md:9](../../DATA_CONTRACTS.md)). M3 derives STALE, UNAVAILABLE and GAP at read time and persists no new market quality values.
6. **Equity** ([LEDGER.md:43](../../LEDGER.md)). M1 implements equity as cash only; M3 implements the marked-holdings contract.
7. **Open risk-policy points** ([RISK_POLICY.md:9-22,55](../../RISK_POLICY.md)). The mark side, "planned open risk" and late daily references are left open. M3 fixes them as explicit, versioned `PAPER_PILOT_V1` fields for owner approval (§5.7).
8. **Time-exit wording** ([STRATEGIES.md:22](../../STRATEGIES.md)). The exit intent is created at the first eligible observation at or after 72 h. The actual holding time is reported and may slightly exceed 72 h.

The hourly-outage conflict (§2.4) is **not** a contract contradiction. The M2 rule that a changed snapshot needs a new-generation quote ([MARKET_DATA.md:19](../../MARKET_DATA.md)) was implemented as a stream rotation that fails every hour. That undermines [RISK_POLICY.md:26](../../RISK_POLICY.md) and [OPERATIONS.md:11](../../OPERATIONS.md). A separate ExecPlan must fix it before M4 activation.

---

## 4. Requirements mapped to tests

**PROPOSED.** A-row checkboxes stay unchecked until the whole row is supported (M8).

| ID | M3 covers (planned evidence) | Deferred |
|---|---|---|
| A01 | Only BTCUSDT/SOLUSDT; only BUY entries; SELL ≤ free holdings; no borrow, short or leverage path; rejected requests leave no financial effect; main stays BLOCKED even with valid data; the test provider refuses non-disposable databases; no live or private adapter, credential or egress (code grep, image, network and mount inspection) | Agent/private-request denial (M5–M7); full row (M8) |
| A02 | Top-ups while holding BTC/SOL use fresh bid marks and are NAV-neutral, or stay `PENDING_VALUATION` and later retry successfully; high-water, daily references and latches are unchanged by top-ups and restarts; a top-up racing a fill cannot deadlock or corrupt either | Matched benchmark flows (M4) |
| A06 | Signals and fills bind a publication watermark; provisional or unconfirmed bars are never used; backfilled bars never open positions; provenance is copied inline and pinned; synthetic, replay and public evidence are labeled; gaps never create fills | External evidence (M6) |
| A07 | Journal, reservations, fills, fees and positions reconcile under concurrent steps, partial fills, retries, lost acknowledgments, kills between reservation and fill, and competing workers | Agent concurrency (M7); sustained runs (M8) |
| A08 | Every `PAPER_PILOT_V1` rule is enforced in code, with pending commitments, lost authority, passive breaches, top-ups and exact boundaries; a lease lost mid-step commits nothing; the UI labels stops as triggers; a gapped-stop loss exceeds plan | Owner pause/resume (M4); agent intents (M7) |
| A09 | Immutable definitions, mandates and signals for every role; a new strategy version cannot alter an open mandate or its history | Version approval (M4); switching (M7) |
| A12 | The Risk and System pages show worker absence, NOLOGIN identity, lease, freshness, unresolved exit obligations and incidents; M4 controls appear as unavailable; M3 tables survive backup/restore; the outbox cursor is monotonic | Owner controls (M4); an event stream if introduced |
| A29 | Simultaneous BTC/SOL entries share one headroom; new attempt keys or split calls cannot exceed caps or open a second position; exit proceeds are not spendable until the fill settles | Agent intents (M7) |
| A31 | A stop already crossed at the entry fill means no entry; a stop crossed during downtime exits at the next fresh quote; cancel-versus-fill race; a stale valuation blocks entry; stop tightening is recorded NOT APPLICABLE (the mandate does not allow it) | Tightening races and stale portfolio review (M7) |
| A34 | A synthetic HH:00:22–HH:01:56 outage, DB outage and engine downtime: stop crossings fill at the first fresh bid afterwards, never at the trigger; nothing is backdated; the execution worker has no egress | SSRF and malicious documents (M6) |

### 4.1 Required scenarios (PROPOSED; all automated unless noted)
- **Execution** ([PAPER_EXECUTION.md:43](../../PAPER_EXECUTION.md)):
  - partial fills; rounding and minimums; insufficient funds; sell dust;
  - duplicate, same-time and conflicting quotes, and out-of-order quotes;
  - late quotes (receipt age > 5 s); fee assets per side;
  - disconnects and restarts; a lost acknowledgment resolved by lookup; two concurrent workers;
  - order totals equal fill totals, and fills equal postings.
- **Risk** ([RISK_POLICY.md:63](../../RISK_POLICY.md)):
  - every inclusive boundary (§5.7);
  - simultaneous entries; deposits while holding positions;
  - passive breaches starting and ending without forced exits;
  - no quotes from 23:59 to 00:06, giving a `LATE` reference; a restart across midnight;
  - latch persistence through restart and top-up;
  - the gapped-stop loss exceeds plan.
- **Strategy** ([TESTING.md:40-44](../TESTING.md)):
  - independently hand-calculated EMA and ATR fixtures, including the initialization rows;
  - the previous fast == slow boundary; 99 versus 100 warm-up bars;
  - a gap or conflict resets warm-up, which recovers after confirmation;
  - simultaneous exit reasons produce one obligation;
  - a heartbeat never refreshes a stale quote; a backfilled bar produces no entry;
  - no execution before availability.
- **Financial properties** ([TESTING.md:32-38](../TESTING.md)): a Hypothesis stateful generator (quotes, bars, top-ups, kills, retries) checks §5.14 after every commit.
- **Roles:**
  - `asl_api` cannot write fill journals, orders or latches;
  - `asl_execution` cannot write funding journals, read `owner`/`owner_sessions`, clear latches, lower high-water, decrease the epoch or change units/contributions;
  - the market role is denied every new table;
  - NOLOGIN blocks connections until enabled.
- **Process:**
  - `docker kill` of the lease holder; `docker pause` beyond lease expiry, then unpause (the stale holder is fenced);
  - PostgreSQL stop/start mid-commit; 30 randomized kill cycles.
- **Replay:** two identical runs; forward/replay equivalence on a recorded disposable run; no network route to the owner's project.
- **UI:** each state in Q01; keyboard and zoom; late or failed reads. Manual Narrator review is owner-performed.

---

## 5. Design (PROPOSED)

### 5.1 Order sources, modes and activation
- **Allowed creators.** The `TREND_REFERENCE_V1` evaluator creates entries and trend exits. The protection engine creates protective-stop, time and follow-up exits. Both run only inside the execution worker or the replay runner, under the execution lease. No HTTP route creates, cancels or changes orders.
- **Modes.** The existing names from [ARCHITECTURE.md:65](../../ARCHITECTURE.md) are used:
  - `FORWARD_PAPER` — main account;
  - `OFFLINE_TEST` — guarded fixture activation;
  - `HISTORICAL_RESEARCH` — replay, displayed as "REPLAY".
  
  A database trigger rejects `OFFLINE_TEST` and `HISTORICAL_RESEARCH` rows outside `asl_m1_%` databases.
- **Activation providers.** Activation is checked every step and again inside every order and fill transaction.
  - `MainActivation` is always `BLOCKED` in M3, with the reasons `RISK_POLICY_UNAPPROVED`, `STRATEGY_UNAPPROVED`, `COST_SCENARIO_UNSET`, `NO_STARTED_RUN (M4)` and `EXECUTION_IDENTITY_DISABLED`.
  - `FixtureActivation` requires `ASL_TEST_ISOLATED=1`, a database name starting `asl_m1_`, and fixture-only definitions written by the guarded loader.
  - `ReplayActivation` requires the replay entrypoint, `ASL_REPLAY_ISOLATED=1` and a database named `asl_m1_replay_…`.

### 5.2 Order lifecycle
**Order record.** Each order records:
- **Identity and context:** account; mode; activation kind; nullable run reference (M4); client order ID.
- **Origin:** `ENTRY`, `PROTECTIVE_STOP`, `TIME_EXIT` or `TREND_EXIT`.
- **Strategy and position:** strategy version and hash; mandate; position; side; symbol; requested base quantity (`BASE_QUANTITY_EXACT`); entry envelope.
- **Decision evidence:** the decision quote (inline copy plus sequence); the instrument snapshot; the signal and watermark.
- **Policy:** risk-policy and cost-scenario hashes.
- **Timestamps:** `decided_at`, `arrival_at`, `fill_deadline` (entries), `terminal_at`, `recorded_at`.

**Allowed transitions.** A `BEFORE UPDATE` trigger enforces the table below, and every change appends an immutable `order_events` row.

| From → To | When | Same-transaction effects |
|---|---|---|
| (new) → `PENDING_VALIDATION` | SYSTEM decision | Order and event; mandate for entries |
| `PENDING_VALIDATION` → `ACCEPTED` | All checks pass | Reservation `ACTIVE`; `RiskDecision` ACCEPT; pins |
| `PENDING_VALIDATION` → `REJECTED` | Any check fails | `RiskDecision` REJECT with reason codes; no reservation |
| `ACCEPTED` → `FILLED` | One eligible snapshot fills the full quantity | Fill, journal, reservation `CONSUMED`, projections |
| `ACCEPTED` → `PARTIALLY_FILLED` | The snapshot fills part of the quantity | Fill, journal, partial consumption |
| `PARTIALLY_FILLED` → `CANCELED` | IOC remainder, in the same step | Release the remainder; the order keeps its fills |
| `ACCEPTED`/`PARTIALLY_FILLED` → `CANCEL_PENDING` | Latch, pre-fill revalidation failure, graceful stop | Reason recorded |
| `CANCEL_PENDING` → `CANCELED` | Effective, in the same transaction in M3 | Release the reservation |
| `ACCEPTED` → `EXPIRED` | Zero fillable quantity; no eligible quote before `fill_deadline`; envelope exceeded; stop already crossed at the fill snapshot | Release the reservation; reason recorded |
| Any non-terminal → `RECONCILIATION_REQUIRED` | The worker's reconciliation finds this order inconsistent | Reservation released; never fills; integrity latch |

- `REJECTED`, `FILLED`, `CANCELED` and `EXPIRED` are terminal and can never reopen.
- `RECONCILIATION_REQUIRED` freezes the order record for a future reviewed repair. It never stops protection: the position's exit obligation continues with new orders sized from journal-derived holdings.

**Identity and idempotency.**
- **Client order ID:** `client_order_id = "c" + base32(SHA-256(canonical{account, mode, origin_kind, origin_key, attempt}))[0:31]`, which is 32 characters and unique per account.
  - Entry `origin_key` = strategy version + symbol + signal bar open time + bar observation ID.
  - Exit `origin_key` = position ID + obligation ID.
- **Attempts:**
  - Entries: an attempt ending `EXPIRED` for `NO_ELIGIBLE_QUOTE` or `ZERO_LIQUIDITY` may be followed by attempt *n*+1, fully re-sized, while the signal is still valid (at most 3 attempts).
  - Final for the signal: `ENVELOPE_EXCEEDED`, `STOP_ALREADY_CROSSED`, and any risk or filter rejection.
  - Exits: attempts increment per follow-up IOC order.
- **Deterministic row IDs:** order, reservation, fill, journal, signal and mandate IDs are UUIDv5 over canonical keys; the fill key is the order ID plus the quote's publication sequence. Each has a unique constraint.
- **Database uniqueness** (partial unique indexes):
  - one live position per symbol;
  - one open entry order per symbol;
  - one active exit obligation per position;
  - one open exit order per position;
  - one decision per signal attempt.
- **Timestamps:** engine rows carry step-clock times. The database `recorded_at` is excluded from fingerprints.

**Commit failures.**
- A trigger or constraint error at COMMIT (SQLSTATE `P0001` or `23xxx`) is a deterministic failure. It records an incident and is not retried as-is.
- A connection loss or unknown result marks the attempt `UNKNOWN`. The worker then reconnects, confirms it still holds the lease, and looks up the deterministic IDs:
  - if present, the step is treated as committed;
  - if absent, the step is rerun from current state with a new `decided_at`, and an incident links the unknown attempt.
- If the lease expired meanwhile, the worker stops, and the next holder reconciles from the database.

### 5.3 Execution model
- **Decision.** At step time `t_d` there is one database clock read per step. The step needs a usable quote for the symbol: age ≤ 5 s (inclusive), plus the M2 lease, feed, telemetry, generation, instrument and clock conditions. Usability comes from one shared predicate (§5.12).
- **Arrival.** `t_a = t_d + arrival_delay`.
- **Fill candidates.**
  - Candidates are scanned in **publication-sequence order**.
  - A quote is eligible when:
    - `source_event_at ≥ t_a` and `available_at ≥ t_a`;
    - its source time is later than the last accepted source time for that symbol;
    - it is still fresh (≤ 5 s) at the processing step.
  - Skipped candidates are recorded with reasons. Stale candidates found after downtime are skipped, so nothing is filled retroactively.
- **Pre-fill revalidation**, inside the fill transaction ([PAPER_EXECUTION.md:15-17](../../PAPER_EXECUTION.md)):
  - lease and epoch; account and risk latches (entries only);
  - symbol status, permissions and every filter against the fill quote's `instrument_id` (the stricter of the decision and fill snapshots wins);
  - reservation coverage and free holdings.
  - On failure: `EXPIRED`, or `CANCEL_PENDING`→`CANCELED`, with a reason code.
- **Price.**
  - Buys use the best ask and sells the best bid, then the scenario's adverse slippage, then adverse tick rounding.
  - The spread is embedded once. Reports may attribute `fill − mid` as a spread component, but never charge it separately.
- **Liquidity.**
  - Fillable quantity = `floor_step(min(remaining, participation × max(0, displayed_best_qty − consumed_at_level)))`.
  - `consumed_at_level` resets when that side's best price changes, and is rebuilt from recent fills after a restart.
- **IOC and entries.**
  - Each order uses at most one snapshot. A zero fill is `EXPIRED`; a partial fill becomes `PARTIALLY_FILLED`, then `CANCELED` in the same step.
  - For entries, `p_max = ceil_tick(entry_reference × (1 + envelope))`. An entry expires with no fill if:
    - the fill price is above `p_max`;
    - the fill snapshot's bid is at or below the stop;
    - no eligible quote arrives before `fill_deadline = t_a + fill_window`.
- **Exits.** Exits have no envelope and no deadline. An exit obligation persists and issues follow-up IOC orders, each with a new arrival delay, until the position closes or only unsellable dust remains.
- **Fidelity verdict.** Sampled 1-second level-1 quotes are sufficient, because orders never take more than a capped share of displayed level-1 quantity and never walk the book. No depth collection is scoped.
  - Recorded limits: 1-second sampling; displayed quantity may already be gone; no queue position, market impact, price-range execution rules or exchange reference price.
  - EV-01 documents comparable paper-trading limits and a broker that fills beyond available liquidity. This model is deliberately stricter.

### 5.4 Cost model `PAPER_COST_V1`
**Structure (sourced).**
- **Commission:** a taker rate on fill notional, charged in the **received asset** without BNB (EX-04).
- **Fees:** round **up** to the instrument's commission precision (8 observed).
- **Spread:** the executable side, counted once.
- **Liquidity:** a single top-of-book snapshot, with a participation cap and depletion.
- **Rounding:** quantities floor to the step. Buy debits round up and sell proceeds round down, to 8 decimals.
- **Reservations:** `qty × p_max`.

**Parameters** (every one is `UNSET` on the main account):

| Parameter | Main | Proposed hypothetical H1 | Proposed stress H2 |
|---|---|---|---|
| Taker commission rate | `UNSET` | 0.10% | 0.20% |
| Arrival delay | `UNSET` | 1,000 ms | 2,000 ms |
| Participation of displayed best quantity | `UNSET` | 50% | 25% |
| Adverse slippage | `UNSET` | 1 bp | 5 bps |
| Entry envelope above entry reference | `UNSET` | 20 bps | 20 bps |
| Entry fill window after arrival | `UNSET` | 5,000 ms | 5,000 ms |

- **H1 and H2 are unsourced, round sensitivity values.** They are not Binance's schedule and not the owner's fee: real account rates need an authenticated endpoint this app must not use (EX-04). Both are stored as immutable, labeled `PROPOSED` definitions; approving one is an M4 gate.
- **`UNSET` blocks every order and fill outside fixture mode** (`COST_MODEL_UNSET`). Fixture scenarios exist only in guarded test databases.
- **Replay** never runs with `UNSET`. It requires an explicitly named scenario, labels every output "hypothetical — unapproved", and has no default.

### 5.5 Filters, rounding and dust
- **Instrument eligibility.** Filters come from the snapshot current at decision time (recorded on the order) and are revalidated at fill (§5.3). The instrument must be `TRADING`, spot-eligible under the M2 rule, and checked within the last 120 s.

| Filter | M3 treatment |
|---|---|
| `LOT_SIZE` | Applied: min, max and step |
| `MARKET_LOT_SIZE` | Applied: effective min = the larger min; effective max = the smaller positive max; step from `LOT_SIZE`, plus the `MARKET_LOT_SIZE` step if positive (incommensurate positive steps make the instrument ineligible). Zero min/step add nothing, because applying `LOT_SIZE` is at least as strict under either reading of the undocumented zero semantics. Zero max makes the instrument ineligible |
| `NOTIONAL`, `MIN_NOTIONAL` | Applied to market orders regardless of `applyMin/MaxToMarket` (stricter), at the decision-quote executable price. The exchange's reference/average price over `avgPriceMins` is not observed (documented limitation) |
| `PRICE_FILTER` | Applied to modeled fill prices (bounds and tick) |
| `MAX_POSITION` | Applied to buys if present |
| `MAX_NUM_ORDERS` | Checked (M3 allows at most one open order per symbol) |
| `ICEBERG_PARTS`, `MAX_NUM_ALGO_ORDERS`, `MAX_NUM_ICEBERG_ORDERS`, `MAX_NUM_ORDER_AMENDS`, `MAX_NUM_ORDER_LISTS`, `TRAILING_DELTA` | Not applicable: these govern order types M3 never creates (iceberg, algo, amend, list, trailing) |
| `PERCENT_PRICE`, `PERCENT_PRICE_BY_SIDE` | **Not modeled**: limit-price rules; the price-range execution rules for market orders are not reproduced (documented limitation) |
| Any other type | The instrument is ineligible (`UNSUPPORTED_FILTER`) until reviewed |

- **Rounding.**
  - Quantities always round **down**.
  - Prices, cash debits and fees round against the account: buy price and debit up; sell price and proceeds down; fees up.
  - A rounded quantity below the minimum quantity or notional is `REJECTED` (`FILTER_REJECTED`), never rounded up.
- **Dust.** Buy commission in base leaves net quantities off the step grid.
  - Exits sell `floor_step(min(position remaining, free holdings))`.
  - A remainder below the minimums closes the position as `CLOSED_WITH_DUST`.
  - Dust becomes an **account-level residual lot**, excluded from any later position's quantity and cost basis. It is valued at bid and counted in notional exposure, and is shown as "unallocated dust — not sellable under current filters".
  - Dust makes the account non-flat, so later top-ups need fresh marks.

### 5.6 Ledger, reservations and valuation
- **Postings per fill** (each balances per asset):

  | Leg | Buy | Sell |
  |---|---|---|
  | Asset exchange | USDT `OWNER_CASH −cost` / `CLEARING +cost`; base `CLEARING −qty` / `OWNER_ASSET +qty` | Base `OWNER_ASSET −qty` / `CLEARING +qty`; USDT `CLEARING −gross` / `OWNER_CASH +gross` |
  | Fee | `OWNER_ASSET −fee` / `EXPENSE +fee` | `OWNER_CASH −fee` / `EXPENSE +fee` |

- **Accounts and sources.** The new `OWNER_ASSET` book account is for BTC/SOL only. CHECKs tie `OWNER_CASH` and `VIRTUAL_CAPITAL` to USDT. Every journal transaction has exactly one source: a funding request **or** a fill.
- **Projections and reservations.**
  - `account_state.cash/reserved` (USDT) and the new `account_holdings` table (BTC and SOL: quantity and reserved) are derived and reconciled.
  - Buy reservations hold `qty × p_max` in USDT. Sell reservations hold the base quantity, so holdings cannot be sold twice and unfilled sell proceeds are never spendable.
  - The new reservation path for exits must not reuse M1's `paused` refusal (§5.8).
- **Account version.** Only balance and reservation changes increment `account_state.version`. Valuation, NAV and high-water updates do not, so an owner's top-up draft is not invalidated every minute.
- **Valuation policy `VALUATION_BID_V1`.**
  - Equity = cash + Σ holdings × fresh best bid, computed exactly, then floored to 8 decimals for risk.
  - NAV = equity / units, with the existing 36-decimal half-even quantization.
  - Any held asset without a usable bid makes the valuation invalid. The M1 `valuation_valid = false` override still forces it invalid.
  - The high-water mark changes only through valuation events, never through funding residuals.
- **Valuation records.**
  - Records are appended every 60 s and at fills, latches, daily references and top-ups, and every high-water raise is persisted immediately.
  - Marks are stored inline, and valuations do not pin quotes, which would grow M2's pinned storage.
  - The account view serves equity, NAV and P&L from the latest persisted valuation, with source, age and quality. It never recomputes them from live marks at startup.
  - The Risk page may show a separately labeled indicative live estimate.
- **Provenance and retention.**
  - Orders, fills, signals and mandates copy the exact quote or candle values and times inline. They also pin the referenced observations and instrument snapshots in `market_evidence_pins` (`ON CONFLICT DO NOTHING`), in the same transaction, behind foreign keys.
  - M2 retention therefore skips them, and M2's retention function stays unchanged.
  - Reconciliation asserts that every referenced observation is pinned.
- **Funding.**
  - Confirm and retry compute a live valuation inside the funding transaction.
  - With holdings and no fresh marks, the request stays `PENDING_VALUATION` (the existing branch). With valid marks, unit issuance is NAV-neutral.
  - Top-ups never touch latches, high-water or references.
- **Reconciliation v2.** It runs at API startup, on the owner route, when the worker acquires the lease, and then every 5 min. It compares:
  - USDT cash;
  - per-asset `OWNER_ASSET` holdings;
  - active reservations per asset;
  - one source per journal transaction;
  - fill fields against postings;
  - order filled quantity against fills;
  - position quantity and cost against fills;
  - funding totals (existing check);
  - NAV: cash/units when flat, otherwise the internal consistency of the latest persisted valuation (stored marks × stored holdings);
  - pin coverage.
  
  A mismatch sets the existing account latch. The worker also moves implicated non-terminal orders to `RECONCILIATION_REQUIRED` (§5.2).

### 5.7 Risk gate `PAPER_PILOT_V1`
**Definitions.** The numbers come from [RISK_POLICY.md:9-22](../../RISK_POLICY.md). These interpretation fields are stored explicitly, for owner approval:
- `E` is bid-marked equity (§5.6). An invalid `E` rejects with `VALUATION_INVALID`.
- **Entry reference and stop:** `p_ref` = signal bar close; stop `s = p_ref − 2 × ATR14`, with `0 < s < p_ref`; `p_max` as defined in §5.3.
- **Cost reserve per unit:** `c = p_max·r + s·(r + slip) + tick`. This is a conservative first-order reserve covering the entry fee, exit fee, exit slippage and exit tick rounding.
- **Planned risk:**
  - per unit = `(p_max − s) + c`;
  - for an open position = `net_qty × max(0, avg_cost_per_net_unit − s) + net_qty × (s·(r + slip) + tick)`;
  - for a pending entry = remaining quantity × its per-unit risk.

**Order of checks.** Deterministic; the first failure sets the primary reason, and every failure is recorded:
1. mode, universe and side
2. activation
3. risk latches
4. execution authority
5. reconciliation
6. data freshness and instrument eligibility
7. valuation
8. today's daily reference
9. cost scenario set
10. strategy warm-up and stop validity
11. one position per symbol
12. passive breach
13. sizing
14. rounding
15. filters
16. recheck of every constraint with the final quantity

**Sizing** ([RISK_POLICY.md:30-43](../../RISK_POLICY.md)). `q = floor_step(min(q_risk, q_aggregate, q_asset, q_total, q_cash, q_liquidity, q_lot))`, where:

| Term | Formula |
|---|---|
| `q_risk` | `0.0025E / unit_risk` |
| `q_aggregate` | `max(0, 0.005E − open − pending) / unit_risk` |
| `q_asset` | `max(0, 0.25E − asset_notional − pending_buys_asset) / p_max` |
| `q_total` | `max(0, 0.50E − crypto_notional − pending_buys) / p_max` |
| `q_cash` | `free USDT / p_max` |
| `q_liquidity` | `participation × displayed ask quantity at decision` |
| `q_lot` | effective maximum lot |

Notional uses holdings (including dust) × bid, plus pending buys × `p_max`. All comparisons use exact Decimal and are inclusive (`≤`).

**Loss references and latches.**
- **Daily reference.** It is the first valid NAV at or after 00:00 UTC.
  - If that NAV is more than 300 s late, the reference is recorded as `LATE`. Its value is the conservative `max(last valid NAV in the prior 24 h, first post-midnight NAV)`, and the gap is recorded.
  - Until today has a reference, entries are blocked (`REFERENCE_MISSING`).
- **Triggers.** The daily latch fires at `NAV ≤ 0.98 × reference`, and the drawdown latch at `NAV ≤ 0.92 × high-water`.
- **What feeds references and triggers.** Only valuations built from quotes that are fresh at processing time update references, high-water and triggers. Recorded quotes scanned after downtime never do.
- **Latches.**
  - Latches are append-only `risk_latches` rows, separate from `account_state.paused`. They block entries but not top-ups.
  - A new latch cancels pending entries in the same transaction.
  - M3 has no clearing path; owner resume is M4.
  - An `account_state` guard trigger stops application roles from clearing `paused` or `reconciliation_failed`, lowering `high_water_nav` or decreasing `fencing_epoch`.
- **Passive breaches.** When notional or aggregate risk is exceeded by price or equity moves, the gate appends start and end events. A breach blocks entries and never forces an exit.
- **Exposure display.** The Risk page shows planned risk and observed exposure (market value at bid) separately, noting that gaps can exceed planned risk. A daily return that cannot be computed validly is shown as unavailable, never 0%.
- **Boundary tests:**
  - exactly 0.25%, 0.50%, 25% and 50%;
  - exactly 2% and 8% declines;
  - quote age 5.000 s versus 5.001 s;
  - notional exactly 5 versus 4.99999999;
  - quantity exactly at the minimum and step;
  - 100 versus 99 warm-up bars;
  - exactly 72 h;
  - a late reference at exactly 300 s.

### 5.8 Position mandates and protection
- **Mandate.** It is created at entry acceptance and is append-only. It records:
  - strategy ID, version and hash;
  - the signal and feature snapshot, entry reason and entry reference;
  - the stop price and policy (`ENGINE_TRIGGER_MARKET_EXIT`, not exchange-hosted);
  - a time exit 72 h from the first fill, and the symmetric trend exit;
  - the cost scenario, risk policy and planned risk.
  
  State changes append `position_events`, and no later version alters a mandate.
- **Protective stop.**
  - It triggers when a usable quote's **bid ≤ stop**.
  - The exit fills at the next eligible quote after arrival, so a gap fills below the stop.
  - Required test: stop at 100, bids 101 → 90 → 89 with a 1 s delay. The fill at 89 makes the realized loss exceed the planned loss, and both the UI and the replay report show it.
- **Precedence.** `PROTECTIVE_STOP > TIME_EXIT > TREND_EXIT`. Each position has at most one active obligation; later reasons are recorded as suppressed, and there is never a double sell.
- **Order within a step.**
  1. fills of open orders, exits before entries;
  2. stop and time triggers;
  3. obligations issue orders;
  4. valuation, references and latches;
  5. entries;
  6. expiries.
- **Stale data.** Exits wait for a usable quote. The gap is recorded as a `PROTECTION_UNAVAILABLE` incident with its interval, and no liquidation price is invented.
- **After engine downtime.** The worker scans missed publications in sequence order.
  - A stop crossing in recorded valid quotes, a passed time deadline, or a downward crossing creates the obligation now, with the missed interval recorded.
  - Fills use only fresh post-restart quotes.
  - Entry signals whose validity lapsed become `MISSED`.
- **Integrity latch.** It blocks entries and, as today, funding. Protective exits continue whenever journal-derived free holdings cover them.

### 5.9 `TREND_REFERENCE_V1`
- **Exact seed** ([STRATEGIES.md:13-27](../../STRATEGIES.md)).
  - EMA20 and EMA50 are seeded by the SMA of the first complete period, then use `alpha = 2/(n+1)`.
  - Wilder ATR14 uses true ranges from the second bar onward, seeded by the mean of the first 14.
  - Arithmetic is Decimal (precision 96, half-even) with no intermediate quantization, stored at full precision.
- **Input series.**
  - The input is the maximal contiguous run of valid finalized bars. An unresolved conflict breaks the run unless its confirmation is visible.
  - Each bar must close before `t_d`, be available by `t_d` and have a sequence at or below the step watermark.
  - Indicators start at the run's first bar, and any missing hour resets the run.
  - Signals need a run length of at least 100. Feature snapshots record the input bounds, count and digest.
- **Signals.** An entry needs previous fast ≤ slow and current fast > slow. A trend exit needs previous fast ≥ slow and current fast < slow.
- **Checkpoint for bar H.** Symbols are processed in priority order (`BTCUSDT`, then `SOLUSDT`). A symbol's decision runs once its own bar-H final is visible and every higher-priority symbol's bar-H final is visible or has passed `H_close + 60 s`. Trend exits run before entries.
- **Validity.**
  - Entries may be decided only until `H_close + 600 s`.
  - Transient blocks defer within that window: `DATA_STALE`, `AUTHORITY_LOST`, `VALUATION_INVALID`, `REFERENCE_MISSING`.
  - A bar that becomes visible later — for example a REST backfill — is used for indicators only, and its signal is recorded as `MISSED` with reason `LATE_BAR`. Backfilled bars therefore never open positions.
  - The window covers the observed ~2-minute hourly outage.
- **Re-entry and records.**
  - Re-entry needs a new upward crossing on a bar that closes after the position closed. Signals arriving while a position is open are recorded as suppressed.
  - Signal records are immutable, and later candle corrections affect only later decisions.
- The 60-second and 600-second values are engineering choices stored in the definition for owner approval. They are not claimed to be optimal.

### 5.10 Execution authority, ordering and recovery
- **Lease.**
  - A singleton `execution_lease` (10 s lease, 2 s renewal, epoch increment, `UNIQUE(id, owner_id, epoch)`) follows the market-lease pattern.
  - Renewal runs on a separate connection.
  - The worker stops issuing work once its last successful renewal is more than 7 s old.
  - Acquisition raises `account_state.fencing_epoch` to the new epoch.
- **Step transactions.**
  - Each step locks in a fixed order: lease (`FOR KEY SHARE`) → `account_state` (`FOR UPDATE`) → orders, positions and holdings.
  - The fence (owner, epoch, expiry, fencing epoch) is re-checked immediately before COMMIT, as `store.py` does.
  - The `execution` identity uses statement 2 s, lock 1 s and idle-in-transaction 3 s timeouts, so a paused holder's locks die before the lease can be taken over.
  - Every table the worker locks carries a column UPDATE grant, as row locks require.
- **Loop.**
  - The worker polls `market_publications` by sequence every 250 ms and processes each publication as one step.
  - After 1 s without publications it runs a timer step, which handles expiries, checkpoint timeouts and cash-only daily references.
  - `decided_at` is the database `clock_timestamp()`, read once when the step starts.
  - The sequence checkpoint commits in the same transaction as the step's effects.
  - Steps with effects record their trigger, watermark, eligibility snapshot and outcome.
- **Tie-breaks.** Publication sequence first, then the phase order in §5.8. Exits come before entries, symbols are processed in ascending order, and `client_order_id` breaks any remaining tie.
- **Recovery.** After (re)acquiring the lease, the worker:
  1. reconciles;
  2. adopts exit orders;
  3. expires older-epoch entry orders that are past their deadline, releasing reservations;
  4. rebuilds its in-memory state: open orders, obligations, positions, and depletion rebuilt from recent fills;
  5. runs the catch-up scan;
  6. resumes.
  
  A graceful stop cancels unfilled entries, keeps obligations and releases the lease.

### 5.11 Replay
- **Engine and clock.**
  - One engine core serves both modes. `MarketView` has a live implementation and a replay implementation, which reads published observations from the replay database in sequence order.
  - The replay clock sets `decided_at` to each publication's `available_at`. This is idealized — zero processing latency — and labeled as such. Timer steps are scheduled at exact deadlines.
- **Isolation.**
  - Replay runs in a separate Compose project and PostgreSQL cluster, with its own secrets, network and volume. Its database is `asl_m1_replay_<id>`, compatible with the existing fixture guards, and `ASL_REPLAY_ISOLATED=1` is set.
  - The mode trigger (§5.1) applies. There is no network path to the owner's project.
- **Replay account.** It is initialized by a guarded function with a labeled 10,000 virtual USDT contribution. The function writes **no** `owner_decisions` row, so it cannot fabricate an owner action.
- **Inputs.**
  - (a) Built-in synthetic scenarios (`SYNTHETIC_FIXTURE`).
  - (b) Recorded public observations. These come from a **market-tables-only data dump** of the normal database, taken with the existing `pg_dump` mechanism (read-only on the owner database) or taken from the deployment's protected backup, then restored into the replay cluster.
  - Acceptance uses an isolated public-worker database, not owner data.
- **Output.**
  - A report in JSON and Markdown is written under `.cache/replay/<id>/`, labeled "MODELED REPLAY — NOT THE OWNER'S ACCOUNT".
  - It names the cost scenario ("HYPOTHETICAL — UNAPPROVED" or fixture), the evidence kind and the source SHA-256. It also records the watermark range, counts, gaps and incidents, code commit, definition hashes and financial fingerprint.
  - It reports raw sums only; evaluation metrics stay in M4.
- **Fidelity.** Historical lease, telemetry and clock state are not recorded, so replay uses reduced eligibility: valid quality, publication order, 5 s age on the replay clock, generation continuity and the point-in-time instrument. Forward decisions store their full eligibility snapshot.
- **Determinism.**
  - The same source restored twice yields identical fingerprints, which use UUIDv5 IDs and exclude `recorded_at`.
  - An equivalence test replays a recorded disposable forward run with its recorded step times and eligibility snapshots.

### 5.12 Trust boundaries
- **Process.**
  - New Compose service `execution-worker`: engine runtime image, command `python -m app.execution.worker`, profile `execution`.
  - `ASL_EXECUTION_ENABLED` defaults to `0`; when disabled the worker exits cleanly. It uses `restart: on-failure`, so a disabled worker does not loop.
  - Private network only (no egress), and only the `execution_db_password` secret.
  - Read-only root, tmpfs `/tmp`, 1 CPU / 512 MiB / 128 PIDs, no published port, JSON log rotation and a heartbeat-file healthcheck.
  - Enabling the flag never trades by itself, because activation stays blocked.
- **Execution role (`asl_execution`).**
  - Created **NOLOGIN** by migration 0005, which needs no new secret.
  - A guarded `app.execution.identity enable` command, run as the migration role from the secret file, grants LOGIN only in isolated projects. On the main database, enabling it is an M4 activation step.
  - Grants:
    - SELECT on market and ledger tables;
    - INSERT on the M3 tables, fill-sourced journal rows, audit, outbox and evidence pins;
    - column UPDATE on `account_state` (version, fencing epoch, cash, reserved, nav, high-water, paused, reconciliation flag), projections, order status and the lease;
    - USAGE on the new sequences;
    - no access to `owner`/`owner_sessions`, and no UPDATE of contributions, units or initialization.
- **API role (`asl_api`).** Gains SELECT on the M3 tables. Loses the unused reservation INSERT/UPDATE and `fencing_epoch` UPDATE. Keeps `valuation_valid` UPDATE for the M1 pending fixture.
- **Journal source by role.** `BEFORE INSERT` triggers on `journal_transactions` and `journal_postings` enforce this, preferred over RLS because RLS's default-deny would hide rows from reconciliation and the deferred balance trigger:
  - `asl_api` may insert only funding-sourced rows, and `asl_execution` only fill-sourced rows;
  - postings are accepted only for a header created in the same transaction (the PostgreSQL 17 mechanism — for example, comparing the header's `xmin` with the current transaction ID — is verified in I2);
  - any other non-superuser is rejected.
- **`account_state` guard trigger** (for non-superusers):
  - latch flags never go from true to false;
  - `high_water_nav` never decreases;
  - `fencing_epoch` never decreases;
  - units, contributions and initialization change only through `asl_api` funding.
- **Market role (`asl_market_worker`).** Unchanged.
- **Shared quote eligibility.** One predicate module is used by `read.quote()`, `health()`, the risk API and the engine. M2 read regression tests prove the API results are unchanged.
- **API.**
  - Read-only routes: `GET /v1/orders`, `/v1/orders/{id}`, `/v1/fills`, `/v1/positions`, `/v1/positions/{id}` and `/v1/risk`.
  - Each requires the service key plus the owner session, and responses are no-store.
  - Query parameters are strict and bounded: status/symbol enums, an opaque decimal-string cursor over a stable identity, and a limit of 1–100.
  - Decimals are strings, times are UTC milliseconds, nulls carry reasons, and errors use the domain envelope.
  - `SystemStatus` keeps `trading: "disabled"` and adds `execution_worker`.
  - **No new mutation route.**
- **Secrets.** `setup-local.ps1`, both harnesses and the `execution-worker`/`engine-tests` services gain `execution_db_password`, created only if missing and never overwritten.

### 5.13 UI
- **shadcn workflow at implementation.**
  - Read the skill, and run `shadcn info --json`, `search` and `docs` in `web-tools` with bridge networking.
  - Reuse Card, Table (TanStack v9), Badge, Alert, Empty, Skeleton, Separator, ToggleGroup and Button.
  - No new primitive is expected. A small feature-level `DataTable` composition is allowed.
- **Routes:**
  - `/orders`: status, symbol and cursor filters in validated search params; orders and fills tables.
  - `/orders/$orderId`: event timeline; risk decision and sizing inputs; reservation; fills; quote and filter provenance; cost scenario; mandate link.
  - `/positions` and `/positions/$positionId`: the immutable mandate card, events, exits, gap disclosures, and planned versus realized loss.
  - `/risk`:
    - activation blockers, each with its owning milestone;
    - `PAPER_PILOT_V1` rules with current usage or an "unavailable" reason;
    - NAV, daily reference, high-water and drawdown, with valuation age;
    - latches and their history; passive breaches;
    - lease, worker and identity status; per-symbol quote usability;
    - the cost scenario (`UNSET`), with the proposed scenarios labeled "proposed — not approved".
- **Other pages.** The nav gains Orders, Positions and Risk, and wraps at 390 px. System gains a paper-execution row. Account shows holdings and dust with mark age.
- **Honesty.**
  - Badges: `MODELED FILL`, `SYNTHETIC TEST`, `REPLAY`, `HYPOTHETICAL COST SCENARIO`.
  - Stops read "Planned stop trigger — not a guaranteed exit price; modeled market exits can fill below it".
  - Zero is distinguished from unknown.
  - Stale values keep their original timestamps and become unusable.
  - Text accompanies color.
- **Polling.** Pages refresh every 5 s while visible. The rationale: execution state changes at step cadence, and the UI is display-only.
- **Data plumbing.**
  - `*.server.ts` reuses `privateApi`.
  - Inputs and responses are validated with strict Zod that mirrors the generated OpenAPI types.
  - Query keys follow `[domain, resource, …params, "M3"]` and include every filter and the cursor.
  - SSR prefetch happens only in the owner phase, as `/markets` does.
  - Nothing is optimistic.

### 5.14 Financial invariants and failure behavior
**Invariants.** Checked after every committed step in property, fault and replay tests (PROPOSED):
1. **Journal balance.** Every journal transaction balances per asset, has at least 2 postings per asset, and has exactly one source.
2. **Projections.** Cash, holdings and reserved projections equal their sources. Free cash and free holdings are never negative; `cash ≥ reserved` and `holding ≥ reserved`.
3. **Fills, orders and positions.** Each fill has exactly one journal transaction that reproduces its quantity, price, gross, fee and fee asset. An order's filled quantity equals the sum of its fills. A position's quantity and cost equal its fills.
4. **Uniqueness and holdings.**
   - at most one live position and one open entry order per symbol;
   - at most one active obligation and one open exit order per position;
   - sells never exceed free holdings;
   - unfilled sell proceeds are never spendable.
5. **Immutability.** Terminal orders never change. Mandates, events, fills, signals, decisions, valuations, references and latches are append-only.
6. **Top-ups.** They change contributions and units only at an unchanged NAV (existing residual rule), and never alter high-water, references or latches.
7. **Provenance.** Every order, fill and valuation cites the observations, definitions and lease epoch it used. Every referenced observation is pinned. No fill cites a quote older than 5 s at processing time.

**Failure matrix (PROPOSED):**

| Condition | Behavior |
|---|---|
| Quote stale or unavailable, clock uncertain, instrument check too old | No new orders or fills; exits wait; `PROTECTION_UNAVAILABLE` incident while positions are exposed |
| Hourly outage (§2.4) | Same as above; entry decisions defer within the 600 s window; incidents recorded every hour |
| Filters change between decision and fill | The stricter snapshot applies |
| Unknown filter type, or zero `MARKET_LOT_SIZE.maxQty` | Instrument ineligible |
| Cost scenario `UNSET` | `COST_MODEL_UNSET`; no order or fill (fixture mode excepted) |
| Deterministic commit failure (`P0001`/`23xxx`) | Incident; no blind retry |
| Commit outcome unknown | Look up deterministic IDs (§5.2) |
| Lease lost, or a stale holder wakes | The fence refuses its commit; the worker stops or becomes standby |
| Worker killed mid-step | Rollback; the successor reconciles, adopts and catches up |
| PostgreSQL unavailable | The lease expires and nothing is processed; recovery on return |
| Reconciliation mismatch | Account latch; implicated orders become `RECONCILIATION_REQUIRED`; entries and funding blocked; exits continue on journal holdings |
| Daily or drawdown trigger | Append-only latch; pending entries canceled; exits continue; no clearing path in M3 |
| Candle conflict or missing hour | The contiguous run breaks; warm-up restarts |
| Late or backfilled bar | Indicators only; the signal is `MISSED` (`LATE_BAR`) |
| Top-up while holding assets, marks stale | `PENDING_VALUATION` (existing owner retry/cancel) |
| Execution worker not running (normal app in M3) | Nothing executes; the Risk page says so |

---

## 6. Data and trust-boundary changes (PROPOSED)

**Migration `0005_m3_paper_broker`.**
- **Form.** Forward-only and hand-written, with `down_revision = "0004_m2_completion"`. The downgrade raises. `CURRENT_REVISION` is bumped. `SET LOCAL lock_timeout` guards DDL. CHECK swaps use `NOT VALID` followed by `VALIDATE`.
- **New tables:**
  - execution control: `execution_lease`, `execution_steps`, `execution_checkpoints`, `execution_incidents`;
  - `execution_definitions`: risk policy, strategy, cost model, scenarios, valuation and filter policies; canonical JSON plus SHA-256; append-only;
  - accounts, orders and fills: `account_holdings`, `orders` (with an identity column for stable paging), `order_events`, `fills`;
  - positions: `position_mandates`, `positions`, `position_events`, `exit_obligations`;
  - decisions and risk state: `strategy_signals`, `risk_decisions`, `valuations`, `daily_references`, `risk_latches`, `risk_breach_events`.
- **Altered tables:**
  - `journal_transactions`: nullable `funding_request_id`; a new `fill_id UNIQUE` foreign key; `CHECK num_nonnulls(funding_request_id, fill_id) = 1`, following the [0004:50-54](../../../services/engine/alembic/versions/0004_m2_completion.py) pattern.
  - `journal_postings`: `OWNER_ASSET` plus asset/book compatibility CHECKs.
  - `reservations`: order link; `CONSUMED`; consumed and released amounts; close time.
  - New triggers for transitions, append-only enforcement, source-by-role, the `account_state` guard and the mode guard.
  - Partial unique indexes per §5.2.
- **Market tables and retention.** No market table is altered, M2's retention function is unchanged, and new foreign keys reference market rows that are always pinned.
- **Seeds.** `PAPER_PILOT_V1`, `TREND_REFERENCE_V1`, `PAPER_COST_V1`, scenarios H1 and H2, `VALUATION_BID_V1` and `FILTER_POLICY_V1`. Every seed is `PROPOSED`; none is approved. At startup, code checks the seeded hashes against its canonical definitions.
- **Roles.** `asl_execution` is NOLOGIN (§5.12), with `execution` identity timeouts added in `db.py`.
- **Precision.** Amounts and prices are `NUMERIC(38,8)`. Units and NAV stay `NUMERIC(72,36)`. Indicators are unconstrained `NUMERIC`.

**Compose and tooling.**
- The `execution-worker` service.
- The new secret, top-level and in `engine-tests`.
- A shared PowerShell acceptance module, used by:
  - `m2-acceptance.ps1`, which must also generate the new secret so its projects keep working;
  - the new `m3-acceptance.ps1` and `m3-replay.ps1`.
- Test truncation lists are generated from `pg_tables`, excluding market tables and `alembic_version`, and checked for completeness, so tables with no FK link cannot leak between tests. Application roles never get TRUNCATE.

---

## 7. Official source and version evidence

- **OBSERVED 2026-09-28**, read during planning:
  - [EX-03](../../REFERENCES.md#ex-03) filters: the rule definitions used in §5.5. Zero is documented as disabling only `PRICE_FILTER` rules. Market-order notional uses a reference price, or a VWAP over `avgPriceMins`.
  - [EX-04](../../REFERENCES.md#ex-04) commission FAQ: MARKET orders pay taker; without BNB the commission is deducted from the received asset; the examples are labeled fictional; account rates come only from authenticated endpoints.
  - [EV-01](../../REFERENCES.md#ev-01) Alpaca paper trading: no market impact, latency slippage or queue position; fills can exceed available liquidity; 10% random partial fills.
  - [PostgreSQL 17 row security](https://www.postgresql.org/docs/17/ddl-rowsecurity.html): default deny when no policy applies; superusers bypass it, and owners bypass it unless forced; permissive policies combine with OR; FK and unique checks bypass it. This supports choosing triggers over RLS (§5.12).
- **Locked versions (OBSERVED; unchanged — no new dependency is PROPOSED):**
  - Engine and database: Python 3.13.11, FastAPI 0.141.1, SQLAlchemy 2.0.54, Alembic 1.20.0, psycopg 3.3.6, PostgreSQL 17.11.
  - Engine tooling: pytest 9.1.1, Hypothesis 6.168.2, Ruff 0.16.9.
  - Web: Start 1.168.58, Router 1.170.39, Query 5.104.0, Table 9.2.4, Zod 4.6.5, RHF 7.89.0, shadcn CLI 4.21.0, Base UI 1.8.0, Tailwind 4.3.3.
  - Web tooling: Vitest 4.1.11, Playwright 1.63.0.
- **PROPOSED at implementation:** recheck the pages above, plus SQLAlchemy 2.0 transactions, PostgreSQL 17 locking, SELECT … FOR UPDATE privileges, and `pg_dump`/`pg_restore` table selection, TanStack Router search params and TanStack Table v9, against the locked versions. Record the results in INTEGRATION_EVIDENCE.

---

## 8. Proposed file edits

- **Engine:**
  - Changed:
    - `services/engine/alembic/versions/0005_m3_paper_broker.py`;
    - `app/db.py` — revision, `execution` identity, timeouts;
    - `app/accounting.py` — holdings-aware funding valuation and reconciliation v2; reservation stubs replaced;
    - `app/main.py` — read routes, DTOs, `SystemStatus`;
    - `app/market_data/read.py` — shared eligibility only.
  - New `app/execution/` package: `decimal_policy`, `definitions`, `filters`, `costs`, `eligibility`, `valuation`, `risk`, `sizing`, `orders`, `fills`, `ledger`, `mandates`, `protection`, `market_view`, `lease`, `engine`, `worker`, `identity`, `fixtures` (guarded).
  - New `app/strategies/trend_reference_v1.py`.
  - New `app/replay/`: `run`, `clock`, `report`.
  - Every module takes an injectable `Engine`, following the `store.py` pattern.
  - Tests: `tests/test_m3_*.py` (unit, indicators, ledger, risk, broker, engine, replay, grants, API). The M1/M2 fixtures switch to generated truncation lists, and the M1 reservation-stub test becomes a broker reservation test.
- **Web:**
  - New `src/execution/` feature module: server, functions, query, schemas, tables and pages.
  - New routes `orders.tsx`, `orders.$orderId.tsx`, `positions.tsx`, `positions.$positionId.tsx`, `risk.tsx`.
  - Changed: `__root.tsx` nav; `system/status.schema.ts` and the status table; the account holdings view; regenerated `src/generated/api.ts` and `services/engine/openapi.json`.
  - New browser tests `e2e/execution-*.spec.ts`.
- **Tooling:** `compose.yaml`, `tools/setup-local.ps1`, `tools/lib/Acceptance.psm1`, `tools/m2-acceptance.ps1`, `tools/m3-acceptance.ps1`, `tools/m3-replay.ps1`.
- **Docs:**
  - Contracts: PAPER_EXECUTION, RISK_POLICY (interpretation fields marked proposed), STRATEGIES, LEDGER, MARKET_DATA (§3.4-1), DATA_CONTRACTS, API_CONTRACTS (routes including `/v1/risk`), CONFIGURATION, SECURITY (roles, triggers, ASVS 5.0.0 mapping), DOCKER, ARCHITECTURE, OPERATIONS (worker, replay, recovery runbook), TESTING, FRONTEND, LIBRARIES.
  - Evidence and status: INTEGRATION_EVIDENCE, COMMANDS, ACCEPTANCE_CHECKLIST, STATUS, this plan.
  - New: an M3 Narrator checklist.

---

## 9. Implementation sequence — independently verifiable increments (PROPOSED)

| # | Increment | Independent verification |
|---|---|---|
| I0 | Contract updates for §3.4 and every new parameter as a proposed, hashed value; shared harness module and new secret | Docs link check and `git diff --check`; `m2-acceptance.ps1` Prepare, Build and Regression still pass through the shared module |
| I1 | Pure core with no database: rounding, filters, costs/`UNSET`, indicators, signals, precedence, sizing and risk math, state machine, fill model, ordering, deterministic IDs | Ruff; unit and Hypothesis tests; hand-calculated EMA/ATR/crossing fixtures; exact-boundary table |
| I2 | Migration 0005: tables, triggers, NOLOGIN role, grants, ledger posting primitives, holdings, reservations, reconciliation v2, shared eligibility | Real PostgreSQL under the real roles: transition and denial matrices, guard triggers, per-asset balance, pin coverage; retention continues past referenced quotes; 0004→0005 upgrade on a seeded predecessor with M1/M2 fingerprints; dump/restore; M1/M2 suites green |
| I3 | Valuation, funding with holdings, latches, daily references, high-water, passive breaches | Midnight and `LATE` cases, latch persistence through restart and top-up, NAV-neutral top-ups while holding, version separation, top-up racing a fill |
| I4 | Fenced broker: create, validate, reserve, revalidate, fill, cancel, expire; lease; idempotency; commit classification | Parallel entries sharing headroom, split and new-key calls, stale epoch, crash hooks before and after commit, lost acknowledgment, stateful property runs |
| I5 | Engine loop and worker: strategy checkpoint, protection, obligations, catch-up, incidents, graceful stop, guarded scenario feed, Compose service | Simulated-clock scenarios (gapped stop, hourly outage, dust, partials, precedence, missed and late bars, downtime); process kill, pause, two-worker and DB-interrupt phases; 60-minute workload; container inspection |
| I6 | Replay runner, market-only restore, report, isolation guards | Two identical fingerprints; forward/replay equivalence; isolation proof (no route; mode trigger; owner-database fingerprint unchanged) |
| I7 | Read APIs, OpenAPI and types, BFF/Zod, pages, nav, System and Account updates | API contract tests, drift checks, web unit tests, browser states, accessibility and performance at 390×844 and 1440×900 |
| I8 | Full final-source acceptance, snapshot, owner Narrator review, docs completion | Every phase in §10 against one source manifest; Q01–Q10 resolved |
| I9 | Normal inert deployment (§12) | Running identities, schema, reconciliation as `asl_api`, blocked activation, browser checks |

---

## 10. Verification commands and measurements (PROPOSED)

All commands run from the repository root in Windows PowerShell. Every build, test and tool runs in Docker. Each run ID gets its own Compose projects and PostgreSQL clusters, secrets, `asl_m1_…` databases, loopback ports and subnets. `Stop` never removes volumes.

```powershell
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Prepare
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Build
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Generate
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Checks            # lint, types, web unit, API/OpenAPI drift, Ruff, format, build
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Regression        # M1+M2+M3 real-PostgreSQL suites under real roles, no skips
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Migration         # seeded 0004 predecessor -> 0005 with a concurrent fixture writer; pg_locks captured
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Recovery          # dump/restore with populated M3 tables, reconciliation, API restart
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase BrokerFaults      # crash hooks, lost acknowledgment, commit classification
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase WorkerKill        # 30 randomized kill/restart cycles with invariant checks
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase WorkerContention  # two workers; docker pause/unpause fencing
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase DbInterrupt
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Replay            # determinism x2, equivalence, report labels
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase ReplayIsolation
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Browser
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase BrowserStates
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase BrowserAccessibility
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase BrowserPerformance
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Performance       # 60-minute engine workload, catch-up, strategy timing
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase PerformanceApi
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Snapshot
./tools/m3-acceptance.ps1 -RunId m3-<id> -Phase Stop
./tools/m3-replay.ps1 -RunId rp-<id> -Source fixture:gapped-stop -CostScenario HYPOTHETICAL_H1 -Repeat 2
```

- **Underlying command forms** follow [COMMANDS.md:34-41](../COMMANDS.md) and the M2 harness:
  - `docker compose -p <project> --profile tools run --rm web-tools pnpm --filter web <lint|typecheck|test:unit|api:check|build>`;
  - `engine-tools uv run --frozen ruff check .` and `python -m app.export_openapi --check`;
  - `--profile test run --rm engine-tests`;
  - `browser-tests pnpm --filter web test:e2e e2e/<spec>.ts`.
- **Skipped tests.** The wrapper fails if any required test is skipped.

**Declared workloads and budgets.** These are PROPOSED for the local Docker Desktop host and are recorded before measuring.

| Area | Workload | Budget |
|---|---|---|
| Engine | 60-minute real-time synthetic feed: 2 symbols at 1 quote/s, 2 open positions, periodic stop/time exits and fills | Publication→step-commit p95 ≤ 750 ms and p99 ≤ 1.5 s; worker RSS < 256 MiB with < 10 MiB growth over the final 30 min; within 1 CPU / 512 MiB |
| Catch-up | Scanning 24 h of recorded quotes (~172,800) | ≤ 120 s |
| Strategy | Indicator evaluation over 17,520 bars per symbol | p95 ≤ 500 ms |
| Replay | Seven days of full-density synthetic quotes | ≤ 20 min; two runs identical |
| API | Orders, fills, positions and risk reads with 10,000 seeded records, in-process | p95 ≤ 250 ms sequential; ≤ 500 ms five-way concurrent |
| Browser | 30 requests per page at 390×844 and 1440×900 | Warm SSR p95 < 1,500 ms; lab LCP ≤ 2.5 s; CLS ≤ 0.1; table interactions p95 ≤ 200 ms |

---

## 11. Q01–Q10 matrix (PROPOSED)

| Gate | Applicability and acceptance condition | Planned evidence |
|---|---|---|
| Q01 | Applicable. Orders, Positions, Risk and the detail pages show every relevant state: loading, empty/inactive, populated fixture, partial, rejected, expired, dust, gapped stop, latch, passive breach, stale, unavailable and error. Filters survive reload and Back; the nav is usable at 390 px | Real-browser journeys with screenshots at both viewports; manual review |
| Q02 | Applicable, scoped to WCAG 2.2 AA: keyboard reach of filters, tables and detail links; accessible names; table semantics; non-color status; 200% zoom; no page-wide overflow | Automated accessibility-tree, keyboard, contrast and zoom tests, plus an owner-performed Narrator checklist for the new pages; no full-conformance claim |
| Q03 | Applicable. Exact Decimal accounting, per-asset balance, reservations, state machine, idempotency, fencing, guard triggers, risk boundaries, indicator fixtures, replay determinism, no fictitious funds | Unit, property, real-PostgreSQL, concurrency and replay suites; reconciliation after every fault case |
| Q04 | Applicable. Dual-identity read routes, strict parameters, no mutations, least-privilege roles, NOLOGIN, source-by-role and guard triggers, no worker egress, secret isolation, log redaction | Per-role denial matrix, container/network/mount inspection, secret-value scan of logs and client assets; ASVS 5.0.0 mapping in SECURITY |
| Q05 | Applicable. Unknown commits, retries, kills, lease loss, DB outage, stale quotes, hourly outage, and late or failed UI reads | Fault phases, catch-up tests, browser late/failed-read tests |
| Q06 | Applicable. The §10 budgets | Measured results with host facts; failures retained |
| Q07 | Applicable. Frozen Docker lint, type, unit, property, integration, browser, build and drift checks | Harness logs with counts and no required skips |
| Q08 | Applicable. Worker heartbeat, lease, identity state, last step, `PROTECTION_UNAVAILABLE` incidents, reconciliation state, structured logs with step/order correlation IDs, local alerts on the Risk page | Assertions against incidents, API and UI; sampled logs |
| Q09 | Applicable. 0004→0005 on nonempty data with a concurrent writer; backup/restore with M3 rows; rollback plan; the §12 deployment | Fingerprints, checksums, restore reconciliation, running-identity records |
| Q10 | Applicable. Module boundaries, official guidance checked against locked versions, no new dependencies, updated contracts and runbooks | Diff/source review, integration evidence, link check |

---

## 12. Normal local deployment — inert (PROPOSED; per [OPERATIONS.md:41-50](../../OPERATIONS.md))

This runs only after every applicable gate passes, under the owner's standing milestone rule.

1. **Preflight.** Confirm project `adaptive-spot-lab`: running image IDs, schema `0004_m2_completion`, healthy services, collection enabled in the ignored `.env`, and host and Docker free space. Pick a window away from HH:00–HH:03 UTC.
2. **Protected backup and rehearsal.**
   - `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/m3-<date>.dump`, then `docker cp` to `.cache/deployments/m3-<date>/`, with SHA-256 and a restricted ACL.
   - Restore it into a network-disabled PostgreSQL 17.11 helper.
   - **Apply 0005 to that copy** and run reconciliation there **as `asl_api`**. The result must be `OK`.
   - Remove the helper.
3. **Secrets.** Run `./tools/setup-local.ps1`. It creates only the missing `execution_db_password`; record that existing secret hashes are unchanged.
4. **Build.**
   ```powershell
   docker compose config --quiet
   docker compose --profile market --profile execution build --quiet migrate api market-worker execution-worker
   docker compose build --quiet web
   ```
5. **Stop, migrate, recreate.**
   - `docker compose --profile market stop web api market-worker`, then `docker compose run --rm --no-deps migrate`.
   - Recreate `api`, then `web`, then `market-worker` (same `.env`, still enabled), each with `up -d --no-deps --force-recreate --wait --wait-timeout 120`.
   - **Do not start `execution-worker`, and do not enable its identity.**
6. **Verify.**
   - Running image IDs match the tested source manifest; schema is `0005_m3_paper_broker`; reconciliation returns `OK`.
   - There are zero orders, fills, positions and latches. `/v1/risk` shows activation `BLOCKED` with its reasons. There is no execution-worker container, and `asl_execution` is NOLOGIN.
   - Feeds return to `CONNECTED` with usable quotes; the planned collection gap is recorded as an incident.
   - Unauthenticated HTTP and Chromium reach `/`, `/orders`, `/positions`, `/risk` and `/system` behind the sign-in gate.
   - The agent performs no owner login, funding, approval or activation.
7. **Record and publish.** Record commands, the backup checksum, identities, the URL `http://127.0.0.1:3000/` and any limits in this plan, STATUS and COMMANDS. Publish according to the owner's Git instructions. A failed verification is reported as a blocked delivery.

---

## 13. Failure and rollback plan (PROPOSED)

- **Code.** Revert by increment. Historical ledger rows are never rewritten.
- **After 0005.**
  - The M2 API image is no longer a fallback, because readiness pins the revision. Fix forward with a schema-compatible image, with the execution worker stopped and its identity NOLOGIN.
  - Last resort, and only with owner consent: restore the protected backup into a fresh volume, accepting the loss of observations collected after it.
- **If the rehearsal on the restored owner copy fails**, the normal database is not touched.
- **Reconciliation mismatch.** It latches and stops; there is no automatic repair.
- **Stopping the execution worker** never affects API, web or collection.

---

## 14. Progress and decision log

- **OBSERVED 2026-09-28.**
  - **Done:** inventory of repository and Docker state; contracts, subtree AGENTS files and the shadcn skill read; official EX-03, EX-04, EV-01 and PostgreSQL row-security pages read; read-only market measurements, including root-cause correlation of the hourly outage; independent adversarial design review, whose findings are incorporated.
  - **Not done:** no file other than this plan was written. Nothing was built, installed or migrated; nothing was logged into or restarted; no paid or provider API was called. A separate planning task for the hourly outage was offered and started by the owner on 2026-09-29.
- **Decisions (PROPOSED).**
  - **Activation.** SYSTEM is the only order source, and main-account activation is structurally blocked.
  - **Execution model.**
    - IOC fills from single-snapshot top-of-book, with no depth.
    - Commission in the received asset; `UNSET` parameters, with labeled hypothetical proposals.
    - Point-in-time filters, revalidated at fill.
  - **Valuation and risk.**
    - Bid-marked valuation for risk, references and high-water, with valuation writes that never bump the account version.
    - Append-only latches, kept separate from the funding pause.
    - A conservative late-reference rule.
    - Entry reference = signal close, with envelope sizing.
  - **Strategy timing.** A priority-ordered 60 s checkpoint, a 600 s validity window from bar close, and bounded retry attempts.
  - **Database enforcement.** Source-by-role and `account_state` guard triggers instead of RLS; inline provenance plus pins, with M2 retention unchanged.
  - **Runtime and deployment.** The execution identity is NOLOGIN until M4; the worker is not started at deployment; replay runs only in isolated clusters, restored from fixtures or market-only dumps.
  - **Excluded.** No run table (owner exclusion). The hourly outage is left to a separate plan before M4. No chart or dependency changes.

### Implementation record — 2026-09-29 (IMPLEMENTED)

Worktree `C:\Users\owner\repos\adaptive-spot-lab-m3`, branch `claude/m3-paper-broker` from `31e2d73`; uncommitted at acceptance, then committed as `01b065a` on that branch and merged to `main` with the 0012 history at the owner's instruction (2026-09-29).

- **Engine** (`services/engine/app/execution/`): `numbers`, `definitions` (hashed canonical seeds), `filters`, `fill_model`, `risk`, `lifecycle` (transition table, UUIDv5 ids, client order ids), `eligibility` (the one quote-usability predicate, now also used by `market_data/read.py`), `market_view`, `store` (fenced writes, lease, `KeepAlive`), `engine` (step phases, recovery, reconciliation, graceful stop), `driver` (simulated/replay clock), `worker` + `health`, `activation`, `identity`, `valuation`, `views` (read models), `fixtures` (guarded), `browser_fixture`, `acceptance` and `performance` (guarded harness helpers); `app/strategies/` (indicators, `TREND_REFERENCE_V1`); `app/replay/` (`run`, `scenarios`, `fingerprint`). Migration `0005_m3_paper_broker`. `accounting.py`: holdings-aware funding and reconciliation v2; the M1 reservation stubs were removed.
- **API/Web:** six read routes, `SystemStatus.execution_worker`, `AccountView` holdings; `src/execution/` pages and routes, nav, System and Account updates; regenerated OpenAPI and TypeScript types.
- **Tooling:** `tools/lib/Acceptance.psm1` (Windows PowerShell 5.1 compatible; used by `setup-local.ps1`, `m2-acceptance.ps1` and the new `m3-acceptance.ps1`/`m3-replay.ps1`), `execution-worker` Compose service and `execution_db_password` secret.

**Deviations from the approved design (all conservative; none changes a limit):**
1. The proposed `strategy_signals` table became `strategy_evaluations` (every evaluated bar, append-only) plus `signal_outcomes` (one terminal outcome per entry signal).
2. A retry after `NO_ELIGIBLE_QUOTE`/`ZERO_LIQUIDITY` is re-sized on a *later* snapshot, never on the snapshot that just expired the attempt (which would size to zero and make the signal final).
3. An entry fill candidate must also have its source time at or before `fill_deadline`; latest-quote reads are bounded by `available_at <= decided_at` as well as the watermark (point-in-time safety when publication order differs from time order).
4. The simulated/replay driver runs timer steps at order deadlines, time exits, validity lapses, hourly checkpoint timeouts and the moment an exposed symbol's latest quote becomes stale, so protection-gap intervals are recorded in replay too.
5. Forward catch-up uses one database clock read per publication batch for the no-effect pre-check (stale quotes can only reveal a stop crossing, checked from fields carried on the publication); any step that can have an effect reads the clock again when it starts.
6. Top-up valuation evidence (marks, quality, sequence) is stored on the funding request's pre-flow values and outbox payload; the API role writes no `valuations` rows. `valuations.purpose = 'TOPUP'` is reserved.
7. A failed step records a `STEP_FAILED` incident and backs off exponentially (at most 60 s) before recovering from the database; it is never retried blindly.
8. The mode guard cannot be exercised in an `asl_m1_` test database, so acceptance runs its trigger logic in a scratch non-`asl_m1_` database and checks the migration function carries the same predicate.
9. **ExecPlan 0012 integration.** 0012 (market stream continuity) was deployed to the normal app on 2026-09-28 22:30 UTC from `ac38d15` and was not yet on `main` at the time. An M3 release built from `main` would have reverted its API and worker changes, so its committed changes (`02f3790` relative to `31e2d73`) were brought into the M3 working tree: a plain patch for files M3 did not touch and 3-way merges for `compose.yaml`, `read.py`, `fixture_worker.py`, `m2-acceptance.ps1` and four documents (the two PowerShell conflicts both fixed Windows PowerShell 5.1 behavior; the shared-module version was kept). The other session's uncommitted edits in the primary checkout were not taken.
10. Simulated, replay and probe loops renew the lease synchronously (`store.KeepAlive`, every 2 s); only the forward worker uses the renewal thread.
11. Restored replay sources are labeled by the observations' actual acquisition (`RESTORED_SYNTHETIC_FIXTURE`, `RECORDED_PUBLIC_OBSERVATIONS` or `MIXED_PUBLIC_AND_SYNTHETIC`), never by the restore path.
12. The UI shows long unconstrained decimals (stops, ATR, planned risk) at 8 places followed by "…"; API and stored values keep full precision. The activation blocker is named `NO_STARTED_RUN` (owning milestone M4).
13. Not implemented in M3 (unchanged scope, recorded for M4+): the 60-minute real-time engine workload, seven-day full-density replay, 10,000-record API read and browser LCP/CLS budgets (see §15 Q06); a forward-run/replay equivalence across processes (equivalence is verified in-process against recorded step times and eligibility snapshots).

## 15. Completion evidence

### Acceptance — run `m3-0929e`, 2026-09-29 (VERIFIED)

- **Source identity.** Worktree `C:\Users\owner\repos\adaptive-spot-lab-m3`, branch `claude/m3-paper-broker` at base `31e2d73` plus uncommitted M3 changes and the integrated 0012 changes. Source/image manifest `.cache/m3/m3-0929e/source-images.json` (SHA-256 `6a422ef1ba1e9325ef3fd9466d613984119195267df81b85b89450e920bb1fe1`): 224 source files, identical at the start and end of the run, and 19 built images.
- **Results.** Every phase exited 0; commands and figures are in [COMMANDS](../COMMANDS.md#verified-m3-acceptance-commands--2026-09-29). Highlights: 167 engine tests and 32 web unit tests with no skips; M1 fingerprints unchanged across 0005 under a concurrent writer; populated M3 dump/restore fingerprint `3427c0f3479f74a54a3056e334f5c7d3a341984ac61e18f544c371f179d7e239` identical with reconciliation OK as `asl_api`; worker kill/pair/pause/DB-interrupt/30-kill phases with fenced stale holders and invariants OK; deterministic replay fingerprint `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e` twice; isolation probe unable to resolve the normal project; strategy p95 3.24 ms; 172,800-quote catch-up 26.24 s; browser inactive/populated/error states at 390 and 1440 px.
- **Earlier iterations** (`m3-0929a`–`d`) are retained and are not counted as passes; §14 items 10–12 and the harness fixes came from them.

### Q01–Q10

| Gate | Result | Evidence and limits |
|---|---|---|
| Q01 | **VERIFIED (scoped)** | Real-browser inactive, populated (modeled fills, IOC remainder, gapped stop with loss above plan, dust, daily-loss latch) and API-failure states; filter state survives reload and Back; nav usable at 390 px. Screens were inspected in the in-app browser against the isolated app. |
| Q02 | **VERIFIED (automated); manual review retired** | Keyboard selection, accessibility-tree table headers, 390 px no page-wide overflow, 200% CSS zoom. The owner Narrator checklist ([m3-narrator-review](../m3-narrator-review.md)) was retired unrun by [owner decision on 2026-09-29](../../DECISIONS.md#2026-09-29--manual-screen-reader-review-retired). No screen-reader or full WCAG conformance claim. |
| Q03 | **VERIFIED** | Exact Decimal policy, per-asset journal, reservations, state machine, idempotent UUIDv5 rows, fencing, guard triggers, risk boundaries, hand-calculated indicators, Hypothesis quote-path/restart property (12 examples), replay determinism, reconciliation after every fault phase. |
| Q04 | **VERIFIED (scoped)** | Dual-identity read routes, strict params, no mutation route (405), per-role denial tests, NOLOGIN, source-by-role/guard triggers, private-network worker with one secret; ASVS mapping in SECURITY. The secret-value scan of logs, artifacts and client assets was run in [ExecPlan 0013](0013-m3-gate-closure.md#7-results). The final run found one isolated test key inside a Playwright failure trace; after tracing was disabled for that spec, the recheck had 0 findings. This is not a penetration test. |
| Q05 | **VERIFIED** | Lost authority mid-step, stale epoch, kill/pause/DB interruption, stale quotes, hourly-outage deferral, downtime catch-up, protection-gap incidents, API failure in the browser. |
| Q06 | **VERIFIED except the seven-day replay (FAILED)** | Measured: strategy p95 3.24 ms (≤ 500 ms), 24 h catch-up 26.24 s (≤ 120 s). [ExecPlan 0013](0013-m3-gate-closure.md#7-results) added the rest; all passed except the replay: the 60-minute engine workload (p95 291 ms, p99 311 ms, RSS 63 MiB, +0.5 MiB), 10,000-record API reads and browser SSR/LCP/CLS/interactions. The seven-day replay exceeded 20 min on a `latest_quote` scan, which is fixed in [ExecPlan 0014](0014-bounded-latest-quote.md). |
| Q07 | **VERIFIED** | Frozen Docker lint, types, unit, property, integration, browser, build and drift checks with no required skips. |
| Q08 | **VERIFIED (scoped)** | Heartbeat healthcheck, lease/identity/last-step on Risk and System, `PROTECTION_UNAVAILABLE` and `STEP_FAILED`/`RECONCILIATION_FAILED` incidents, structured worker logs with trigger/sequence/effects/duration. No external alerting. |
| Q09 | **VERIFIED** | 0004→0005 on non-empty data with a concurrent writer; populated backup/restore; protected owner backup, isolated rehearsal and normal deployment below; rollback tags `pre-m3`. |
| Q10 | **VERIFIED (scoped)** | No new dependency; official sources rechecked (INTEGRATION_EVIDENCE); contracts, runbooks and this record updated. The 0012 integration is disclosed in §14. |

### Normal deployment — 2026-09-29

Standing milestone authorization ([OPERATIONS](../../OPERATIONS.md#milestone-completion-deployment)); inert per §12.

- **Preflight (01:26 UTC).** Project `adaptive-spot-lab`: API `sha256:0a1664ca…dc86` and market worker `sha256:348804f6…cef25` (ExecPlan 0012 release), web `sha256:dd3778c6…ae5b`, PostgreSQL healthy; schema `0004_m2_completion`; readiness 200; collection enabled; database 339 MB; about 600 GB free on the host drive.
- **Protected backup.** `.cache/deployments/m3-paper-broker-20260929a/m3-paper-broker-20260929a.dump` in the owner checkout: 65,739,115 bytes, SHA-256 `4509ac8c967342ba3c14271fd5f58283a1f9133f4e6605b038e505eb904d5bce`, identical in the container and on the host; the directory ACL grants only SYSTEM, Administrators and the owner account; the in-container copy was removed.
- **Rehearsal.** The backup was restored into an internal-only PostgreSQL 17.11 helper; the accepted migrate image applied `0005_m3_paper_broker`; `asl_execution` was NOLOGIN, orders 0, definitions 7; reconciliation as `asl_api` returned OK. The helper, network and temporary secrets were removed.
- **Secrets.** Only `execution_db_password` was created; all existing secret hashes were unchanged.
- **Rollout (01:27:35–01:28:01 UTC).** Previous images tagged `pre-m3`. Frozen Docker builds from the accepted source; web, API and market worker stopped; one forward migration; API, web and market worker recreated. The execution worker was built (`sha256:2f0256bb…c31f`) and **not started**.
- **Running identity (VERIFIED).** API `sha256:ea2e879500d5286abc5126b9a3431f14efd7c2099a32c89405b303ad9e0fa7ad`, web `sha256:8efe8e5bb3954293d266e0f18410e62fc6627c9cccc59314c83f8c70bbd4a8b7`, market worker `sha256:76993dfadff147218b696eea16da56e5a5c46159eba8695ae0cc037fc383719e`, migrate `sha256:6243e6934f187a134bdee0777b3443ebcf839a478c1a61ba812093054a04cdce`, PostgreSQL unchanged. Seven checked engine files in the API container and the market worker's `worker.py` match the accepted tree byte for byte; 0012's market-worker code is identical to its deployed commit `ac38d15`.
- **State (VERIFIED).** Schema `0005_m3_paper_broker`; reconciliation OK (cash 10,000.00000000, reserved 0); orders, fills, positions, latches, evaluations and valuations 0; execution lease never taken (epoch 0); `asl_execution` NOLOGIN; account initialized, not paused, not reconciliation-failed. Both public feeds `CONNECTED` with usable quotes; the rollout cost about 34 s of capture (last quotes 01:27:35, first new 01:28:09 UTC) and recorded no market incident.
- **Surface.** Unauthenticated HTTP returned 200 for `/` and `/system` and redirected `/orders`, `/positions`, `/risk` (and `/markets`) to their canonical search URLs, which returned 200. The in-app browser showed the Risk page behind "Owner session required" and System reading Account funded, Market data ready, Model runtime unconfigured, Paper trading disabled, Paper execution worker not running. No owner login, funding, approval or activation was performed.
- **Rollback.** Stop `api`/`web`/`market-worker` and restore the `pre-m3` images only with a schema-compatible fix-forward; the M2/0012 API image requires `0004` and is not a fallback after 0005. Last resort (owner consent): restore the protected backup into a fresh volume.

### Remaining limits

- The normal app was built from the M3 worktree (`C:\Users\owner\repos\adaptive-spot-lab-m3`); that exact accepted source is commit `01b065a`, now merged to `main` together with the ExecPlan 0012 history (the merge changes documentation only).
- M4 activation gates are unchanged: approve `PAPER_PILOT_V1` and `TREND_REFERENCE_V1` with their interpretation fields, choose a cost scenario (or keep `UNSET`), enable the execution identity and start a run.
- Closed by [ExecPlan 0013](0013-m3-gate-closure.md) on 2026-09-29, with these outcomes:
  - Q02 manual Narrator review: retired by owner decision.
  - Q04 secret scan: run.
  - Q06 budgets: measured. The seven-day replay budget failed, and the fix is ExecPlan 0014.

## 16. Immediately after approval (documentation only; then stop)

1. Save this plan as `docs/plans/0011-paper-broker-reference.md`.
2. In `docs/README.md`, add ExecPlans 0002, 0003, 0005, 0010 and 0011 to the document inventory.
3. In `docs/STATUS.md`, mark M3 **planned (ExecPlan 0011); implementation not yet authorized**.
4. Stop. No implementation, commit or push happens until it is explicitly authorized.
