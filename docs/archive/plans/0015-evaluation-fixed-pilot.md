# ExecPlan 0015 — M4 evaluation and fixed-strategy forward pilot

**Status: M4-A ACCEPTED AND DEPLOYED (2026-09-29); M4-B ACTIVATED 2026-09-30 — the pilot is RUNNING; M4-C checkpoint on 2026-11-25.**
- **M4-A.** Final run `m4f-0929c` from `be61a32` passed every §10 phase, and the normal app was deployed inert with schema `0006_m4_fixed_pilot` (§16).
- **M4-B.** On 2026-09-30 the owner approved the definition hashes and the manifest in the UI, pressed Start, and instructed the activation, running `pilot-activate.ps1` themselves. Experiment `d779fbf4-e1be-444c-ab55-7b61292eaa87` was ACTIVATED at 09:09:52 UTC, and every §12 post-activation check passed (§16).
- **M4-C.** Per OD-13, M4 is complete once the checkpoint report of 2026-11-25 is recorded. Until then the pilot runs under OD-11 (it needs the PC and Docker running) and OD-12 (deployments only outside HH:00–HH:03 UTC, with a graceful worker stop).

Progress is in §14.

The plan was written in a read-only session: no file was edited, no Docker, build, install, migration, login, provider or network call was made, and `secrets/`, `.env` and owner/ledger data were not read. Sections 0–13 keep that planning text; implementation facts are recorded in §14–§16.

Labels:
- **OBSERVED:** repository files, git history or command output.
- **PROPOSED:** not built or run.
- **IMPLEMENTED:** built and committed, not yet verified by the named check.
- **VERIFIED:** passed the named check with recorded output.
- **NOT RUN.**

Branch `claude/m4-fixed-pilot` was created from `main` at `c96726c` after ExecPlans 0013, 0014 and 0015 merged (PRs #1, #3, #4), and is delivered by GitHub pull request via `gh`. The file:line citations were rechecked against that base (§14).

## 0. Summary

M4 turns the inert M3 broker into an owner-controlled, measured forward pilot of `TREND_REFERENCE_V1`. It adds no authority (PROPOSED):
- **Approvals:** exact-hash owner approvals for the hashed M3 definitions and for two new proposals, `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1`.
- **Experiments:**
  - immutable experiment manifests;
  - the OPERATIONS state machine, `DRAFT` through `FAILED`;
  - owner start, pause, resume, flatten and stop, recorded as durable intents that the SYSTEM applies inside its fenced step.
- **Activation:** main-account activation is derived from approved database state instead of the hard-coded M3 block.
- **Evaluation:** a separate read-only worker produces point-in-time evaluation: run-relative unitized NAV, drawdown, costs, matched-flow baselines, a dependence-aware bootstrap and downtime disclosure.
- **UI:** Approvals, Experiments and report pages.

M4 deploys inert. A forward pilot starts only after three things happen:
1. The owner answers §3.3.
2. The owner approves exact hashes in the authenticated UI.
3. The owner explicitly instructs activation in chat.

The pilot may be negative or inconclusive. No report is a profitability, promotion or live-trading claim.

## 1. Goal and observable outcome (PROPOSED)

Three stages, recorded separately:

1. **M4-A — capability (implementer).**
   - In isolated projects, a test owner approves exact hashes. A `FORWARD_PAPER` experiment on a labeled synthetic feed then runs start → entry → pause → resume → flatten → stop → final report.
   - Latches resolve only under their rules.
   - Kills, database interruptions and multi-hour downtime recover without backdating.
   - Reports regenerate identically as-of any past time, and replays are deterministic.
   - The normal app then runs schema `0006_m4_fixed_pilot` inert:
     - no approvals or experiments;
     - activation blocked with its reasons;
     - both worker identities NOLOGIN;
     - both workers built but not started;
     - collection unchanged.
2. **M4-B — pilot activation (owner-gated).**
   - After the approvals and an explicit instruction, the identities are enabled and the workers started.
   - The owner presses Start.
   - The first activated step records the start watermark, start valuation and daily reference, with reconciliation OK.
3. **M4-C — measured pilot.**
   - At the owner's checkpoint (OD-13), the frozen protocol's report is recorded with every limitation.
   - STATUS marks M4 complete only then, unless OD-13 decides otherwise.

## 2. Current repository facts (OBSERVED)

**Branches and plans**
- `main` is `77e2830`. `claude/m3-gate-closure` (`05b4d98`) carries ExecPlan 0013, which is in progress:
  - only its cleanup is VERIFIED (0013-m3-gate-closure.md:145-147);
  - its seven-day replay failed on a `latest_quote` scan (:125-143).
- `claude/bounded-latest-quote` holds 0014's implementation commit `b9b0369`. That commit adds a decision-time bound to `latest_quote` with a 60 s lead. The plan still reads PLANNED, and its completion evidence is unfilled (0014-bounded-latest-quote.md:3, 107-113).
- Plans 0001–0014 exist, so this plan is 0015. README.md:67-79 lists plans only up to 0012.

**Normal app (from the M3 record; not re-queried)**
- M3 is accepted and deployed inert. The M4 row reads "Not implemented", with evidence needed "Approved run configuration and measured fixed pilot" (STATUS.md:64-65). Public collection continues (STATUS.md:9, 17).
- After the M3 rollout (0011-paper-broker-reference.md:1028):
  - schema 0005;
  - reconciliation OK with cash 10,000.00000000;
  - zero orders, fills, positions, latches and valuations;
  - lease epoch 0;
  - `asl_execution` NOLOGIN;
  - account initialized.

**Activation and authority**
- MAIN is always inactive, with blockers RISK_POLICY_UNAPPROVED, STRATEGY_UNAPPROVED, COST_SCENARIO_UNSET, NO_STARTED_RUN and EXECUTION_IDENTITY_DISABLED (`services/engine/app/execution/activation.py:10-16, 33-35`).
- The worker:
  - resolves activation once, from the environment (`worker.py:117-118`);
  - exits unless `ASL_EXECUTION_ENABLED=1` (`:198-201`).
- The engine:
  - requires a complete cost scenario taken from the activation (`engine.py:166-179`);
  - creates no entries while inactive (`:968-970`);
  - cancels latched BUY orders before they fill (`:538-540`);
  - on graceful stop, cancels unfilled entries and keeps obligations (`:385-406`).
- Every recorded latch stays active ("M3 has no clearing path", `store.py:157-162`).
- `identity.py:36-38` refuses LOGIN outside `asl_m1_` databases.
- The `migrate` service has no `execution_db_password` (compose.yaml:46-49). The execution worker uses `restart: on-failure` (:174).
- The risk view hard-codes three values, and the web schema mirrors each as a strict literal (`schemas.ts:257-264, 308, 352`):
  - blocked activation (`views.py:344-347`);
  - `clearable_in_m3: False` (`:361-362`);
  - `active_scenario: "UNSET"` (`:371`).
- `SystemStatus.trading` is `Literal["disabled"]` (`main.py:54`; `status.schema.ts:10`).
- The standing deployment authorization excludes enabling trading, changing approvals and clearing pauses (AGENTS.md:20).

**Schema**
- `execution_definitions` is append-only, with status only `PROPOSED` or `FIXTURE_ONLY` (`0005_m3_paper_broker.py:40-44, 56-66`). Approvals therefore need their own records.
- M1 `owner_decisions` is funding-only (`0002_m1_account.py:120-131`).
- `orders.run_ref varchar(64)` is nullable and never written (`0005:232`; `store.py:414-422`).
- Obligation reasons and order origins allow only ENTRY, PROTECTIVE_STOP, TIME_EXIT and TREND_EXIT (`0005:217, 234`).
- Valuation purposes include the reserved `STARTUP` (`0005:319-320`).
- There is one checkpoint per mode (`0005:75-82`).
- The `account_state` guard stops application roles from clearing `paused` or `reconciliation_failed` (`0005:433-454`).
- Funding refuses while `paused` (`accounting.py:249-252`), and a reconciliation mismatch sets both flags (`:478-479`). A run pause must not reuse `paused`.

**Definitions (hashed, PROPOSED)** — seeded at `0005:24-31`, defined in `definitions.py:19-178`:
- `PAPER_PILOT_V1` `25ba32b5…77d2`;
- `TREND_REFERENCE_V1` `393a4950…9e01`;
- `COST_SCENARIO_HYPOTHETICAL_H1` `c3fe1259…21a5`;
- `…H2_STRESS` `eddc7ed3…153a`;
- `PAPER_COST_V1`, `VALUATION_BID_V1` and `FILTER_POLICY_V1`.

H1 and H2 are labeled unsourced (`definitions.py:119, 134`). The owner's real account fee is available only from authenticated endpoints (EX-04, as recorded at 0011:786).

**Time and data**
- The 5 s quote age is a policy field (`definitions.py:36`) and is also duplicated as constants (`eligibility.py:13`; `engine.py:231, 295`).
- A first `FORWARD_PAPER` start has no checkpoint, so `last_sequence` begins at 0 (`engine.py:99, 145-147`). The worker would scan all publication history, and catch-up evaluates up to 168 past bars (`engine.py:64, 420-452`).
- Unpinned quotes are deleted after seven days (MARKET_DATA.md:35). An experiment must keep a reproducible dataset or be marked not fully reproducible (:55).
- Known residuals (0012-market-stream-continuity.md:600-604): SOL ticker pauses of 5–6 s, clock-uncertainty teardown, and back-to-back REST waits.

**Web and tooling**
- shadcn:
  - preset `b2fms61Bqi`, `base-nova` (`apps/web/components.json`);
  - 15 installed primitives.
- Start Host and CSRF middleware (`start.ts:8-23`). Idempotent funding mutations resolve unknown outcomes (`account.functions.ts:96-140`).
- Lightweight Charts adapter pattern: `markets/candle-chart.tsx:116, 132, 167, 238`.
- Harness conventions: `tools/m3-acceptance.ps1:1-34`.
- Locked versions (`uv.lock`, `package.json`); the engine has no numerical library:
  - FastAPI 0.141.1, SQLAlchemy 2.0.54, Alembic 1.20.0, psycopg 3.3.6, Pydantic 2.13.5;
  - pytest 9.1.1, Hypothesis 6.168.2, Ruff 0.16.9;
  - Start 1.168.58, Router 1.170.39, Query 5.104.0, Table 9.2.4;
  - RHF 7.89.0, Zod 4.6.5, shadcn 4.21.0, Base UI 1.8.0;
  - Lightweight Charts 5.2.1, Playwright 1.63.0, Vitest 4.1.11;
  - PostgreSQL 17.11 (compose.yaml:5).

**Contracts**
- ROADMAP.md:17, 33-37
- EVALUATION.md:25-29, 33, 37, 43-45, 58
- RISK_POLICY.md:5, 57
- OPERATIONS.md:5, 17-19
- CONFIGURATION.md:30, 58, 60, 67
- API_CONTRACTS.md:43-49, 57-59
- AUTONOMY_MATRIX.md:34-36
- DECISIONS.md:58-68

## 3. Scope and exclusions

### 3.1 In scope (PROPOSED)
- **Approvals and controls:**
  - exact-hash approvals;
  - experiment manifests, states and owner controls;
  - latch resolution;
  - owner flatten.
- **Engine:**
  - activation derived from the database;
  - the run-start boundary;
  - hourly valuation and mark capture, plus flow marks;
  - code-identity segments;
  - downtime records.
- **Evaluation:**
  - an evaluation worker, report generator and report API;
  - evaluation of replays;
  - labeled cost-sensitivity replays.
- **Tooling:**
  - guarded identity and activation tools;
  - Compose services;
  - `tools/m4-acceptance.ps1`.
- **UI:** the Approvals, Experiments and experiment/report pages, and updates to Risk, System, Account and the nav.
- **Delivery:**
  - contract updates;
  - an inert normal deployment;
  - an owner-gated activation runbook.

### 3.2 Excluded
- Model or agent runtime, research, selectors, and shadow or multi-account work (M5–M7).
- Live exchange, Testnet, Demo, credentials or signed endpoints.
- Manual orders.
- New strategies or changed limits, except V2 definitions the owner requests (OD-2, 3, 5, 6).
- Clearing the integrity latch (`reconciliation_failed`/`paused`). That needs a separate reviewed repair plan.
- Market-worker changes (including the clock-uncertainty follow-up), depth or trade collection, and retention changes.
- Annualized or Sharpe metrics, and acceptance thresholds unless the owner sets them in OD-7.
- New dependencies.

### 3.3 Owner decisions required before a forward pilot

The values below are existing hashed proposals or labeled engineering proposals, not calibrated optima.

| ID | Question | Options | Recommendation |
|---|---|---|---|
| OD-1 Denomination and capital | Run on the existing main account in `USDT (virtual)`, measured from the NAV at activation, with top-ups allowed and matched in the baselines? | (a) yes. (b) yes, but no top-ups during the pilot (needs a funding guard). (c) a separate pilot account — unsupported by the single-account schema. | (a) |
| OD-2 Risk profile | Approve `PAPER_PILOT_V1` exactly as hashed (RISK_POLICY.md:9-22 plus the interpretation fields at :81-89)? | Approve; change it through `PAPER_PILOT_V2` (new code, tests and hash); or reject (no pilot). | Approve |
| OD-3 Strategy | Approve `TREND_REFERENCE_V1` exactly as hashed (seed values, 600 s validity, 60 s checkpoint, 3 attempts, BTC then SOL priority)? | Same as OD-2. | Approve. It is an untested control seed, not a profitability claim. |
| OD-4 Execution assumptions | Approve the three execution definitions below? `PAPER_COST_V1`: IOC one-snapshot fills from sampled level-1 quotes, a participation cap with level depletion, spread counted once, commission in the received asset, rounding against the account. `VALUATION_BID_V1`: bid-marked valuation. `FILTER_POLICY_V1`: percent-price rules and exchange average-price notional not modeled. | Approve; require a stricter V2; or reject. | Approve, keeping the fidelity labels on every fill and report. |
| OD-5 Fee/cost scenario | Which scenario governs modeled fills? The app cannot verify the owner's account rate. | (a) H1: 0.10% taker, 1,000 ms arrival, 50% participation, 1 bp slippage, 20 bps envelope, 5,000 ms fill window. Labeled HYPOTHETICAL everywhere, with H2 as a separate replay sensitivity. (b) A new scenario whose commission comes from Binance's official public spot fee schedule for an owner-named tier (URL, retrieval time and page hash recorded at implementation). Labeled "published schedule — not the owner's account rate"; other values as H1. (c) keep `UNSET` (no pilot). | (a) |
| OD-6 Quote freshness | Keep the 5 s maximum quote age despite 5–6 s SOL pauses? | (a) keep: entries defer inside the 600 s window, and short `PROTECTION_UNAVAILABLE` intervals are recorded. (b) measure pauses read-only on the normal market tables, then approve a V2 value; this also removes the duplicated constants. | (a), reporting the pause counts |
| OD-7 Protocol freeze | Approve `EVALUATION_PROTOCOL_V1` as specified in §5.5? | Approve; change the listed values before start; or add predeclared acceptance criteria (then frozen, which enables a G3 judgment). | Approve as a descriptive protocol with no threshold |
| OD-8 Baselines | Approve `BASELINE_SET_V1` as specified in §5.5? | Approve; change weights or rebalancing before start; or drop B4. | Approve |
| OD-9 Control authority | Who may start, pause, resume, flatten and stop? | (a) owner only, in the UI. SYSTEM enforces latches. The implementer performs only graceful worker stops for authorized deployments, and runs activation or deactivation only on explicit chat instruction. (b) (a) plus an implementer emergency pause, never a resume; this needs an AUTONOMY_MATRIX change. | (a) |
| OD-10 Drawdown latch | What happens after an 8% drawdown latch? | (a) owner resume only once current valid NAV is back above 0.92 × high-water mark. A flat account cannot recover, so the run then stops. (b) a later run may define an episode-relative reference through a new approved policy, with history and the high-water mark kept. (c) immediate resume — contradicts RISK_POLICY.md:57. | (a) |
| OD-11 Local downtime | After PC sleep, power loss or a Docker stop, may the pilot continue automatically once checks pass? The owner acknowledges that protection needs the PC and Docker running (OPERATIONS.md:5). | (a) yes, as a transient block, with the downtime disclosed. (b) downtime above an owner-named threshold latches a `DOWNTIME` pause. | (a) |
| OD-12 Deployments during a pilot | May fixes or milestones deploy while the pilot runs? | (a) yes: outside HH:00–HH:03 UTC, with a graceful worker stop, and a new evaluation segment when the code identity changes. (b) only while the owner has it paused. (c) only after `STOPPED`. | (a) |
| OD-13 Horizon and completion | When is the pilot measured, and when is M4 complete? No universal duration is implied. | (a) open-ended pilot; the owner names a checkpoint date; M4 is complete once that report is recorded; M5 may start after M4-B. (b) a fixed end date, then stop. (c) M4 complete at M4-B. | (a) |
| OD-14 Reproducibility | Unpinned quotes are deleted after seven days. | (a) weekly protected, checksummed dumps of the market tables only, sized after measuring disk space. (b) inline marks only: the experiment is marked "not fully replayable" beyond seven days. | (a) if the measured disk allows, otherwise (b) |

**How answers are recorded**
- Chat answers to OD-1 and OD-9–14 become dated DECISIONS entries.
- Hash approvals (OD-2–5, 7, 8 and the manifest) count only when the owner clicks them in the authenticated UI. Chat text or model output is never approval (ROADMAP.md:17; RISK_POLICY.md:5).
- OD-7 and OD-8 should ideally be answered before batch B2 seeds those definitions. Later answers only add V2 rows.

**Owner answers (2026-09-29).** "accept all recommendations".
- OD-1 and OD-9–OD-14 are recorded as [DECISIONS](../../DECISIONS.md#2026-09-29--m4-pilot-decisions-execplan-0015).
- OD-2–OD-8 are recorded as the owner's stated intent. They still need the exact-hash approvals in the UI.

### 3.4 What can be built now versus what the decisions block
- **Buildable now (all of M4-A):**
  - schema, engine, API, evaluation, UI and tooling;
  - isolated acceptance, using fixture owners and approvals in `asl_m1_` databases;
  - `PROPOSED` protocol and baseline seeds;
  - the inert deployment;
  - rehearsed activation tooling.
- **Blocked by the decisions:**
  - approvals on the normal app, the manifest, identity and worker activation, Start, and all M4-B and M4-C evidence;
  - V2 definitions, if OD-2, 3, 5 or 6 change values;
  - OD-5b's official-page verification;
  - OD-14a dumps.

## 4. Requirements mapped to tests (PROPOSED)

A-rows stay unchecked until M8.

| ID | Requirement | A-IDs | Planned tests |
|---|---|---|---|
| R01 | Approvals bind exact hashes and require the owner session, service key, CSRF and an idempotency key. A stale hash, a same key with a different payload, or no session is rejected. A revocation blocks entries at the next step; exits continue. | A09, A27 | `test_m4_approvals.py` (real PostgreSQL, API role); API contract tests; `e2e/pilot.spec.ts` |
| R02 | Manifests are canonical and immutable. `UNSET` fields are listed with their owning document. A code-identity mismatch refuses activation. | A09, A10 | Unit; immutability trigger; engine refusal |
| R03 | MAIN activation comes only from an approved experiment and is checked every step and in every order or fill transaction. An environment cost-scenario override is refused for MAIN. | A01, A08 | `test_m4_engine.py` (simulated clock); role tests |
| R04 | State machine and controls follow §5.2–5.3. Each intent is applied exactly once by SYSTEM. Locks are taken in a fixed order, with no deadlock. | A12, A27 | Commit-point hooks; Hypothesis stateful sequences |
| R05 | Latches resolve only under their rules. They are never deleted, the high-water mark never falls, and the integrity latch is not resumable. | A08 | Engine and role tests |
| R06 | Flatten creates `OWNER_FLATTEN` obligations with precedence and never double-sells. It stays unresolved without usable quotes. | A08, A31 | Scenarios: crossed stop, stale data, dust |
| R07 | Run-start boundary: checkpoint at W0 with no historical scan. No evaluation or entry for bars closed before activation. A start valuation and a daily reference are recorded. | A06 | Engine scenarios; first-activation probe |
| R08 | Downtime is recorded. Nothing is backdated. Missed signals are `MISSED`. Exposed hours without a valuation are gaps. | A12, A34 | `PilotDowntime` phase |
| R09 | Metrics match hand-computed Decimal fixtures. | A02, A10 | `test_m4_metrics.py` |
| R10 | Baselines use matched flows, and a flow at fixed marks leaves the baseline's NAV unchanged. | A02, A10 | Fixtures; Hypothesis |
| R11 | The bootstrap is seeded and deterministic, applies the sample rules, and never annualizes. | A10 | `test_m4_bootstrap.py` |
| R12 | Reports are reproducible as-of any time. The evaluation role writes only reports. | A06, A10 | As-of determinism after later inserts; denial matrix |
| R13 | A code change starts a new segment; segments are never stitched together. | A36 | Engine and report tests |
| R14 | Replay determinism; forward/replay equivalence including control events; labeled sensitivity runs. | A07, A10 | `Replay` phase |
| R15 | UI states and labels are honest, with no optimistic control results. | A12 | Web unit tests; e2e |
| R16 | Least privilege; NOLOGIN until activation; no secrets in logs or client assets. | A01 | Denial matrix; `SecretScan` |
| R17 | The deployment is inert. | A12 | §12 verification |

### 4.1 Financial invariants (checked after every commit in property, fault and replay tests)
- **I1 — Approved run.** Every `FORWARD_PAPER` order and mandate references the non-terminal experiment. All of that experiment's manifest hashes must have been approved at decision time.
  - Entries also need `RUNNING` with no active pause cause.
  - Exits also run in `PAUSED` or `STOPPING`, or after an approval is revoked.
- **I2 — Pauses stop entries.** No BUY fill or new entry happens in a step whose snapshot shows a pause cause or a pending pause request.
- **I3 — Exits are not blocked by controls.** Exits are never blocked by pause, stop, flatten or revocation — only by data, holdings or filters.
- **I4 — State and history.**
  - Experiment transitions follow §5.2, and terminal states never reopen.
  - Events, approvals, manifests, resolutions, marks and reports are append-only.
- **I5 — Latch closure.** A latch closes only through a resolution that references its ID, and only with reconciliation OK and a fresh valid valuation. The high-water mark never decreases.
- **I6 — Manifest.** The manifest hash is verified at activation.
- **I7 — Reports.** Reports are pure functions of (manifest, protocol, as-of, watermark). The evaluation role can change no financial or execution row.
- **I8 — Baseline flows.** Baseline flows equal posted ledger flows in amount and time, and are NAV-neutral.
- **I9 — Top-ups.** Top-ups never move NAV (beyond the existing residual rule), the high-water mark, latches or experiment state.
- **I10 — No backdating.**
  - For every fill, `decided_at ≤ arrival_at ≤ modeled_at`.
  - Every control application comes after its request's commit.
- **M3 invariants** still hold: journal balance, reservations, uniqueness, pins, and no overselling.

### 4.2 Concurrency and failure cases

| Case | Required behavior | Test |
|---|---|---|
| A pause commits while a step is accepting an entry | The entry's decision predates the pause. The next step cancels it before any fill (`POLICY_PAUSED`). | Hook between load and commit |
| Parallel duplicate controls | One is applied. The same key returns the original result; a different key gets 409. | Parallel API calls |
| API lock wait during a slow step | Retryable error. The UI resolves the outcome by looking up the idempotency key. | Induced slow step |
| Resume races a new latch | The resolution binds only the old latch ID. | Hook |
| Flatten while a stop is crossing | One obligation; the other reason is recorded as suppressed; no double sell. | Engine scenario |
| Flatten without usable quotes | Unresolved, with `PROTECTION_UNAVAILABLE`; no invented price. | Engine scenario |
| Approval revoked mid-run | `APPROVAL_REVOKED` opens; entries are canceled; exits continue. | Engine and API |
| Kill after a request commits | The request is applied once, after recovery. | `PilotFaults` |
| Pause, kill, DB stop, or 30 random kills | Fenced; invariants hold. | `PilotFaults` |
| Hours of downtime while exposed | Interval recorded; exits at the first fresh quote; `MISSED` signals; gap hours. | `PilotDowntime` |
| Top-up while holding and marks are stale | `PENDING_VALUATION`; no baseline flow until the top-up posts. | Engine and report |
| Code identity changes | A new segment starts. | Engine |
| Reconciliation mismatch | `INTEGRITY` pause; entries and funding blocked; exits continue. | Fault injection |
| Report generation fails | An incident is recorded; the prior report stays; no financial effect. | Evaluation fault |

### 4.3 Replay evidence
1. **Determinism.** A "pilot lifecycle" fixture replayed twice gives identical fingerprints. The fingerprint is extended to experiment events, resolutions, marks and `HOURLY` valuations.
2. **Forward/replay equivalence.** Checked on a recorded isolated forward run, with owner control events replayed as timed inputs.
3. **Cost sensitivity.** The same restored source is replayed under H1 and H2, each labeled `MODELED REPLAY — NOT THE OWNER'S ACCOUNT` and `HYPOTHETICAL`.
4. **Report determinism.** A report built on replay output is identical across two runs.
5. **Seven-day replay.** Once 0014 is accepted, the seven-day `PerformanceReplay` is rerun with M4 capture enabled.

## 5. Design (PROPOSED)

### 5.1 Approvals and definitions
- **The `owner_approvals` table** is append-only. Each row records:
  - the target kind (`DEFINITION` or `EXPERIMENT_MANIFEST`), ID and SHA-256;
  - the action: `APPROVE`, `REJECT` or `REVOKE`;
  - the owner and session reference;
  - the idempotency key and canonical request hash;
  - the expected state version and correlation ID.
  
  The current state is the latest action for each (kind, ID, hash).
- **What the owner sees.** The UI shows the full canonical content, a diff against any predecessor, and the consequences (CONFIGURATION.md:58).
- **New seeds.** `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1` are seeded `PROPOSED` through the existing hashed-seed path. `execution_definitions.kind` gains `EVALUATION_PROTOCOL` and `BASELINE_SET`.
- **OD-5b** adds a new verified cost scenario only if chosen.

### 5.2 Experiments, manifests and states
- **Tables:**
  - `experiment_manifests`: canonical JSON plus SHA-256, immutable.
  - `experiments`: at most one non-terminal experiment per mode; holds `state` and `version`.
  - `experiment_events`: append-only. A trigger makes `OWNER` events come only from `asl_api` and `SYSTEM` events only from the workers.
- **The manifest records:**
  - mode, account and denomination;
  - (id, hash) of the risk policy, strategy, cost model, cost scenario, valuation, filter, protocol and baselines;
  - a **code identity**: the SHA-256 of the runtime `app/` tree, computed at process start;
  - data rules;
  - the bootstrap-seed rule;
  - an account snapshot: contributions, units, NAV, high-water mark and integrity flags;
  - known limitations.
  
  `UNSET` fields block `READY` (CONFIGURATION.md:60).

| From → To | Actor | Condition |
|---|---|---|
| — → `DRAFT` | OWNER | Manifest composed |
| `DRAFT` → `READY` | OWNER | Manifest hash and every referenced definition hash approved |
| `READY` → `RUNNING` | OWNER (Start) | Approvals still active; reconciliation OK; no other active experiment; no integrity latch |
| `RUNNING` ↔ `PAUSED` | SYSTEM | A cause opens / the last cause closes |
| `RUNNING`/`PAUSED` → `STOPPING` | SYSTEM | Owner stop applied (optionally with flatten) |
| `STOPPING` → `STOPPED` | SYSTEM | No live positions, open orders or active obligations |
| `DRAFT`/`READY` → `STOPPED` | OWNER | Discarded before start |
| `STOPPED` → `COMPLETED` | SYSTEM | Final report recorded |
| non-terminal → `FAILED` | OWNER or SYSTEM | Evidence invalid (e.g. identity mismatch); protection continues |

### 5.3 Controls and pause causes
- **Owner requests are durable intents.** Start, pause, resume, flatten, stop and discard are idempotent. The SYSTEM applies the execution-affecting ones in its fenced step, once per request ID.
  - A committed pause request is an active cause immediately.
  - Flatten and stop return "accepted", not "completed".
- **Latched causes:** `OWNER`, `DAILY_LOSS`, `DRAWDOWN`, `INTEGRITY` and `APPROVAL_REVOKED`.
- **Transient blocks are shown but never latched:** `DATA_STALE`, `VALUATION_INVALID`, `REFERENCE_MISSING`, `PASSIVE_BREACH`, and worker-not-running.
- **Resume names the causes to close.**
  - The API's pre-check is advisory only.
  - The worker re-checks authoritatively: reconciliation OK, usable quotes, a fresh valuation, and the rule for each cause:

    | Cause | Condition to close |
    |---|---|
    | `DAILY_LOSS` | Today's valid reference exists and NAV > 0.98 × reference |
    | `DRAWDOWN` | Per OD-10 |
    | `APPROVAL_REVOKED` | A fresh approval exists for the same hash |
    | `INTEGRITY` | Never in M4 |

  - The worker then appends either `risk_latch_resolutions` or `RESUME_REJECTED` with reasons.
  - Clearing one cause never clears another.
- **Flatten** is an owner pause plus one `OWNER_FLATTEN` obligation per open position.
  - Precedence is `PROTECTIVE_STOP > OWNER_FLATTEN > TIME_EXIT > TREND_EXIT`.
  - The M3 follow-up IOC and dust rules apply.
- **Lock order.** `account_state` is always locked before `experiments`. The worker locks lease → account → experiments → rows.

### 5.4 Engine integration
- **Activation each step.** MAIN activation is recomputed inside the fenced transaction from the non-terminal `FORWARD_PAPER` experiment, its causes and its approvals. The cost scenario comes from the manifest. FIXTURE and REPLAY activation are unchanged.
- **First activated step.**
  - If the worker's code identity differs from the manifest, it refuses.
  - Otherwise it appends `ACTIVATED` with watermark W0.
  - It persists a `STARTUP` valuation, deferring while the valuation is invalid.
  - It records the daily reference, labeled `LATE_CONSERVATIVE` if later than 300 s past midnight.
- **Run-start boundary.** If there are no live positions, orders or obligations, the checkpoint jumps to W0. Only bars that close after activation are evaluated; earlier bars feed the indicators only.
- **Capture while `RUNNING`, `PAUSED` or `STOPPING`:**
  - at the first step at or after each UTC hour:
    - a `HOURLY` valuation;
    - one `evaluation_marks` row per symbol, holding inline bid, ask, quantities, times and quality;
  - at activation and after each posted top-up, `FLOW` marks from the first usable quote after flow time plus the scenario's arrival delay.
  
  The replay driver's deadlines include these times.
- **At lease acquisition:**
  - a changed code identity appends `SEGMENT_STARTED`;
  - a gap longer than 10 s plus the lease period appends an `EXECUTION_DOWNTIME` incident and event.
- **Run linkage.**
  - `run_id` becomes required on `FORWARD_PAPER` orders and mandates, replacing `run_ref`.
  - It is nullable on evaluations, decisions, valuations and incidents.
  - Read routes gain an `experiment` filter.

### 5.5 Evaluation: protocol, baselines and reports
- **Report generator.** A pure core plus a data loader, deterministic from (manifest, protocol, as-of, watermark). Every input row is bounded by as-of.
- **`EVALUATION_PROTOCOL_V1` (for OD-7). Every value here is a labeled engineering proposal.**
  - **Grid:** hourly UTC.
  - **Strategy NAV:** from `HOURLY` valuations. An invalid valuation is a gap. Returns across a gap count toward the cumulative return but are excluded from the paired samples.
  - **Metrics:** EVALUATION.md:33, plus:
    - run-relative return, N_t/N_start − 1;
    - run maximum drawdown, shown separately from the account's drawdown against its persistent high-water mark;
    - realized and unrealized P&L;
    - fees per asset, with base-asset fees valued at their fill price as a labeled calculation;
    - cost components (spread up to the touch, then slippage and tick), never double-counted;
    - time in market;
    - turnover = gross filled notional / mean valid equity;
    - holding durations;
    - trade-outcome distribution;
    - signal outcomes and rejection reasons;
    - planned versus realized loss;
    - gaps, downtime and owner interventions.
  - **Uncertainty:**
    - a stationary block bootstrap (mean block length 24 h, with 6 h and 72 h sensitivity) of paired hourly log-return differences against each baseline;
    - 90% percentile intervals from 2,000 resamples;
    - seed derived from the manifest and protocol hashes;
    - floats only inside these statistics.
  - **Minimum sample:** intervals need ≥ 168 paired hours; trade statistics need ≥ 10 closed positions. Below that, the report says "insufficient sample".
  - **Reporting:**
    - no annualization and no Sharpe ratio;
    - an hourly snapshot, a daily full report, and a final report at stop;
    - no acceptance threshold.
- **`BASELINE_SET_V1` (for OD-8).**
  - Five baselines:
    - B0: cash;
    - B1: 100% BTC;
    - B2: 100% SOL;
    - B3: 50/50 BTC/SOL;
    - B4: 25% BTC / 25% SOL / 50% cash (the notional caps).
  - All are buy-and-hold and never rebalanced.
  - Acquisition happens at activation and after each posted top-up (pro rata), from the `FLOW` marks: at ask plus the run's slippage and commission, floored to the lot step.
  - Holdings are marked at bid, in exact Decimal, with units issued at matched flows.
  - Displayed-quantity participation is not applied to baselines; that idealization is labeled.
- **`evaluation_reports`.**
  - Each report records its kind (`SNAPSHOT`, `DAILY` or `FINAL`), canonical JSON, SHA-256, as-of time, watermark, protocol hash and generator code identity.
  - Labels: `MODELED FILLS`, `SAMPLED_L1_TICKER`, the cost-scenario label, the evidence acquisition kinds and the segments.
  - Each report carries a limitations section.
- **Evaluation worker.** It writes a snapshot at HH:05, a daily report at 00:10 UTC, and the final report on `STOPPED`. It idles when there is no experiment. Replays call the same generator through a CLI, labeled `HISTORICAL_RESEARCH`.

### 5.6 Identities, processes and tooling
- **`asl_evaluation`:** a new role, created NOLOGIN, with a new secret `evaluation_db_password`. It gets SELECT on the tables it needs and INSERT on `evaluation_reports` only.
- **Identity enabling:**
  - `app.execution.identity enable --main --experiment <id>` covers both the execution and evaluation identities. It runs as the migration role, through a new one-shot `pilot-admin` Compose service.
  - It refuses unless the experiment is `READY` or `RUNNING` with complete approvals and reconciliation OK.
  - `disable` refuses while positions are live, unless given an explicit owner-instructed override flag.
- **The `evaluation-worker` Compose service:**
  - profile `evaluation`, on the private network only;
  - a read-only root filesystem;
  - limits of 0.5 CPU, 256 MiB and 64 PIDs;
  - only its own secret.
- **Restart policy.** Check Docker's documented behavior of `on-failure` across daemon and PC restarts. If it does not restart the workers, run them with `unless-stopped` and make a disabled worker idle instead of exiting.
- **`tools/pilot-activate.ps1` and `pilot-deactivate.ps1`** run:
  1. preflight and a protected backup;
  2. the identity changes;
  3. the `.env` flags `ASL_EXECUTION_ENABLED` and `ASL_EVALUATION_ENABLED`;
  4. worker start or stop;
  5. verification.

  Both refuse to run between HH:00 and HH:03 UTC.

### 5.7 UI (the skills must be loaded at implementation time)
- **Skills and components:**
  - Load the official **shadcn skill** and run `shadcn info --json`, `search` and `docs` in `web-tools` over bridge networking.
  - Preserve `b2fms61Bqi`, `base-nova` and the pointer behavior.
  - Reuse the 15 installed primitives. Add a missing one (for example Checkbox) only through the CLI, after registry discovery and a dry-run.
  - Load the official **Lightweight Charts skill** for the NAV chart.
- **Pages:**
  - `/approvals`:
    - shows each definition's content, hash, status and consequences;
    - approve, reject and revoke go through an AlertDialog bound to the exact hash.
  - `/experiments`: the experiment list, draft creation, and the manifest with its `UNSET` fields.
  - `/experiments/$experimentId`:
    - state, causes, timeline and pending or rejected requests;
    - control dialogs; the Start dialog shows the OPERATIONS.md:5 downtime notice;
    - report tables: metrics, baselines, paired intervals or "insufficient sample", costs, downtime and limitations;
    - a run-relative NAV line chart of the strategy and baselines:
      - whitespace for gaps;
      - TradingView attribution;
      - an exact-value table as the text alternative;
      - client-only, disposed on unmount.
  - Updates elsewhere:
    - Risk: live blockers and latch resolutions;
    - System: trading state and the evaluation worker;
    - Account: experiment identity and run-relative return;
    - the nav wraps at 390 px.
- **Data handling:**
  - validated search params;
  - query keys of the form `["experiments", …, "M4"]`;
  - 5 s polling while visible;
  - RHF and Zod for forms.
- **Mutations:**
  - nothing is optimistic;
  - affected keys are invalidated afterwards;
  - an unknown outcome is resolved by looking up its idempotency key.

## 6. Official source and version evidence
- **OBSERVED.** Locked versions are listed in §2. No new dependency is proposed. No official page was read in this session, because no network calls were made.
- **To verify at implementation and record in INTEGRATION_EVIDENCE:**
  - **Binance:** EX-03 and EX-04. The official public fee-schedule page is needed only for OD-5b, and would become a new REFERENCES entry.
  - **Docker:** restart policies and Compose secrets (OPS-02).
  - **PostgreSQL 17:**
    - row-lock conflicts;
    - `ALTER ROLE … LOGIN PASSWORD`;
    - `CHECK … NOT VALID` / `VALIDATE`;
    - `REPEATABLE READ`;
    - `pg_dump -t --data-only`.
  - **Bootstrap reproducibility:** Python 3.13 `random` (use only the API with a documented reproducibility guarantee), and the stationary bootstrap's primary source, Politis & Romano (1994) — verify and record the full citation.
  - **TanStack:**
    - Start server functions and CSRF (1.168.58);
    - Router search params (1.170.39);
    - Query mutations (5.104.0);
    - Table 9.2.4.
  - **Forms:** RHF 7.89.0 with the Zod 4.6.5 resolver.
  - **UI:** the shadcn component docs; Lightweight Charts 5.2.1 line series, whitespace data and NOTICE/attribution.
  - **Standards:**
    - the OWASP ASVS 5.0.0 areas already mapped in SECURITY (V1.2.4/V2.2.1, V3.5.1/V7.2, V8.2, V14.3), plus logging;
    - WCAG 2.2.

## 7. Data and trust-boundary changes (PROPOSED)

**Migration `0006_m4_fixed_pilot`.**
- **Form.** Forward-only: the downgrade raises. It uses `SET LOCAL lock_timeout`, and CHECK constraints are added `NOT VALID` then validated.
- **New tables:**
  - `owner_approvals`, `experiment_manifests`, `experiments`, `experiment_events`;
  - `risk_latch_resolutions`, `evaluation_marks`, `evaluation_reports`.
- **Triggers:** append-only on every new table except `experiments`, which gets a transition-and-actor guard; mode guards where a table carries a mode.
- **Alterations:**
  - `orders.run_ref` becomes `run_id uuid` with a foreign key. A precondition refuses to migrate if any `run_ref` is non-NULL.
  - `run_id` is required for `FORWARD_PAPER` orders and mandates, and nullable elsewhere.
  - `OWNER_FLATTEN` is added to obligation reasons and order origins.
  - The `HOURLY` valuation purpose and the two new definition kinds are added.
  - A partial unique index allows at most one active experiment per mode.
  - `store.active_latches` excludes resolved latches.
- **Seeds.** The two `PROPOSED` definitions, with their hashes checked by code at startup.
- **Roles:**
  - `asl_api`:
    - gains SELECT on the new tables;
    - gains INSERT on approvals, manifests, experiments and OWNER events;
    - gains UPDATE on `experiments(state, version, timestamps)` for owner transitions only;
    - gets nothing on orders, obligations or latches.
  - `asl_execution` gains:
    - SELECT on approvals and experiments;
    - INSERT on SYSTEM events, resolutions, marks and `HOURLY` valuations;
    - UPDATE on `experiments(state, version)` for SYSTEM transitions only.
  - `asl_evaluation` (new, NOLOGIN) may only INSERT into `evaluation_reports`.
  - The market role is denied all of the new tables.
- **Configuration:**
  - `db.py` bumps the revision and adds the `evaluation` identity with bounded timeouts.
  - `setup-local.ps1` creates only a missing `evaluation_db_password`.
  - A new setting, `ASL_EVALUATION_ENABLED`, defaults to `0`.
  - MAIN rejects `ASL_EXECUTION_COST_SCENARIO`.

## 8. Proposed file edits

**Engine**
- Changed at the top level: `alembic/versions/0006_m4_fixed_pilot.py`, `app/db.py`, `app/main.py`.
- New packages:
  - `app/experiments/`: `manifest`, `approvals`, `controls`, `states`, `code_identity`, `views`;
  - `app/evaluation/`: `series`, `metrics`, `baselines`, `bootstrap`, `report`, `worker`, `views`.
- Changed in `app/execution/`: `activation`, `engine`, `store`, `driver`, `views`, `identity`, `worker`, `definitions`, `fixtures`, `acceptance`.
- Changed in `app/replay/`: `run`, `fingerprint`, `scenarios`.
- Tests: `tests/test_m4_*.py` and the performance probes.

**Web**
- New `src/experiments/`:
  - the data layer: server, functions, query, schemas, search;
  - the UI: pages, controls, report view and `nav-chart.tsx`.
- New routes: `approvals.tsx`, `experiments.tsx`, `experiments_.$experimentId.tsx`.
- Changed: `__root.tsx`, `system/*`, `execution/risk-page.tsx`, `execution/schemas.ts`, `account/account-home.tsx`, plus regenerated types and OpenAPI.
- New browser tests: `e2e/pilot*.spec.ts`.

**Tooling**
- `compose.yaml` and `tools/setup-local.ps1`;
- `tools/lib/Acceptance.psm1` and `tools/m4-acceptance.ps1`;
- `tools/pilot-activate.ps1` and `tools/pilot-deactivate.ps1`.

**Docs**
- Contracts: EVALUATION, OPERATIONS, API_CONTRACTS, DATA_CONTRACTS, RISK_POLICY, STRATEGIES, PAPER_EXECUTION, MARKET_DATA, CONFIGURATION, SECURITY, TESTING, FRONTEND.
- Records:
  - DECISIONS, INTEGRATION_EVIDENCE, COMMANDS;
  - ACCEPTANCE_CHECKLIST, STATUS;
  - README (add plans 0013–0015);
  - this plan.

## 9. Implementation sequence (PROPOSED)

| # | Batch | Independent verification |
|---|---|---|
| B0 | Contract updates; harness skeleton; new secret | Link check; `git diff --check`; M3 `Checks` and `Regression` |
| B1 | Pure evaluation core | Ruff; hand-computed fixtures; Hypothesis |
| B2 | Migration 0006, roles, triggers, seeds; manifests, approvals, code identity | Denial and transition matrices; 0005→0006 on populated data; dump/restore |
| B3 | Engine: activation, boundary, controls, resolutions, flatten, capture, segments, downtime | Simulated-clock §4.2 cases; stateful property; replay determinism |
| B4 | Owner API and views | Contract and negative tests; OpenAPI drift |
| B5 | Evaluation worker, identity commands, Compose, pilot tools | Report determinism; denial; container inspection; activation rehearsal |
| B6 | Web (skills loaded) | Lint, types, unit; browser at 390 and 1440 px |
| B7 | Final-source acceptance; documentation | All §10 phases on one manifest; Q01–Q10 resolved |
| B8 | Inert normal deployment (§12) | Identities and inert state |
| B9 | Owner-gated activation and checkpoint report | Only on explicit owner instruction |

## 10. Verification commands and budgets (PROPOSED; the harness is not implemented)

`tools/m4-acceptance.ps1` follows the M3 conventions:
- `-RunId` plus a `ValidateSet` of phases;
- isolated Compose projects, clusters, secrets, `asl_m1_` databases, ports and subnets for each target kind;
- no allowed skips;
- `Stop` never removes volumes;
- Windows PowerShell 5.1.

```powershell
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Prepare
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Snapshot              # before and after; zero differences
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Build
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Generate
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Checks
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Regression            # M1-M4 suites + mode guard
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Migration             # populated 0005 -> 0006, concurrent writer, restore
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase ApprovalAuth
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PilotLifecycle
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PilotFaults
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PilotDowntime
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Evaluation
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Replay                # determinism, equivalence, H1/H2
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase ReplayIsolation
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase ActivationRehearsal
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase BrowserApprovals
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase BrowserPilot
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase BrowserError
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PerformanceEngine -EngineSeconds 3600
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PerformanceApi
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PerformanceReport
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase PerformanceBrowser
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase SecretScan
./tools/m4-acceptance.ps1 -RunId m4-<id> -Phase Stop
```

Budgets (PROPOSED, declared before measuring):

| Area | Workload | Budget |
|---|---|---|
| Engine | M3 60-minute workload plus a `RUNNING` experiment, hourly capture and 5 controls | M3 budgets unchanged: p95 ≤ 750 ms, p99 ≤ 1.5 s, RSS < 256 MiB, < 10 MiB growth |
| Controls | 200 randomized requests racing steps | p95 ≤ 500 ms; 0 deadlocks; every outcome resolvable by key |
| Reports | 90 synthetic days, 5 baselines, 3 × 2,000 resamples, at 0.5 CPU / 256 MiB | ≤ 180 s; identical hash on rerun |
| API | New reads over 10,000 records | p95 ≤ 250 ms sequential; ≤ 500 ms five-way concurrent |
| Browser | Experiment and report pages at 390×844 and 1440×900 | SSR p95 < 1,500 ms; LCP ≤ 2.5 s; CLS ≤ 0.1; no chart leak over 20 remounts |

## 11. Q01–Q10 matrix (PROPOSED)

| Gate | Applicability and acceptance condition | Planned evidence |
|---|---|---|
| Q01 | Applicable. Every state is shown for approvals, experiments and reports: awaiting worker; pending, rejected or unknown controls; latch resolution; insufficient sample, gaps and stale data; API failure. Filters survive reload and Back; the nav works at 390 px. | Real-browser journeys at both viewports, plus the implementer's own inspection |
| Q02 | Applicable, targeting WCAG 2.2 AA: keyboard reach, dialog focus and return, names, headings and table semantics, non-color status, contrast, 200% zoom, narrow layouts, and a chart table alternative. | Automated browser checks plus implementer browser inspection. No manual screen-reader review (DECISIONS 2026-09-29); no screen-reader or conformance claim. |
| Q03 | Applicable: R01–R14, invariants I1–I10, exact Decimal arithmetic, and reconciliation after every fault. | Unit, property, real-PostgreSQL, concurrency and replay suites |
| Q04 | Applicable. Owner mutations use session, service key, CSRF, Host checks, strict bodies, the 8 KiB cap, idempotency, exact hash and expected version. Also least-privilege roles, NOLOGIN until activation, no worker egress, and log redaction. | Denial matrix; container inspection; `SecretScan`; ASVS mapping. Not a penetration test. |
| Q05 | Applicable: unknown outcomes, lock timeouts, kills, DB outage, downtime, stale quotes, report failure, cache invalidation. | Fault and downtime phases; browser failure states |
| Q06 | Applicable: the §10 budgets. | Measured results with host facts |
| Q07 | Applicable: frozen Docker checks with no required skips. | Harness logs |
| Q08 | Applicable: experiment state and causes; heartbeats; lease and identity state; downtime, protection and report incidents; correlation IDs; local alerts. | Incident and UI assertions; sampled logs |
| Q09 | Applicable: 0005→0006 on populated data; restore with M4 tables; protected owner backup and isolated rehearsal; inert deployment; activation rehearsal; rollback tags. | Fingerprints, checksums, running identities |
| Q10 | Applicable: module boundaries; guidance checked against locked versions; no new dependency; updated contracts and runbooks. | Review; INTEGRATION_EVIDENCE; link check |

## 12. Normal local deployment — mandatory completion step (inert; per OPERATIONS.md:50-59)

1. **Preflight.**
   - Confirm `adaptive-spot-lab` image IDs, schema (0005 or the 0014 release), health and collection enabled.
   - Record free disk space.
   - Stay outside HH:00–HH:03 UTC.
2. **Backup and rehearsal.**
   - Take a `pg_dump -Fc` backup into `.cache/deployments/m4-<date>/`, with SHA-256 and a restricted ACL.
   - Restore it into an internal-only PostgreSQL 17.11 helper, apply 0006, and reconcile as `asl_api` (must be OK).
   - Remove the helper.
3. **Secrets and tags.** `setup-local.ps1` creates only the new secret, and existing secret hashes stay unchanged. Tag the current images `pre-m4`.
4. **Build and recreate.**
   - Frozen builds of `migrate`, `api`, `market-worker`, `execution-worker`, `evaluation-worker` and `web`.
   - Stop `web`, `api` and `market-worker`, then run one migration.
   - Recreate `api`, `web` and `market-worker` with the same `.env`.
   - **Start neither worker, and enable neither identity.**
5. **Verify.**
   - Running images and source files match the accepted manifest.
   - Schema is `0006_m4_fixed_pilot`, and reconciliation is OK.
   - Zero approvals, experiments and reports; seeds are `PROPOSED`; both identities are NOLOGIN; activation is blocked with its reasons.
   - Feeds are usable again after the recorded rollout gap.
   - Unauthenticated HTTP and Chromium reach every route behind the sign-in gate.
   - The agent performs no owner login, approval, funding or activation.
6. **Record and publish.** Record identities, the backup checksum and `http://127.0.0.1:3000/` in this plan, STATUS and COMMANDS, and publish through the pull request. If verification fails, report the delivery as blocked.

**Owner-gated activation (M4-B).** This is not a deployment step. It runs only on explicit instruction, after the owner has approved every hash:
1. Run `pilot-activate.ps1`.
2. Verify the lease is held and MAIN shows "awaiting Start".
3. The owner presses Start.
4. Verify:
   - the `ACTIVATED` event;
   - the W0 checkpoint, with no historical evaluations;
   - the `STARTUP` valuation and the daily reference;
   - reconciliation OK;
   - the first snapshot report.

Deactivation follows `STOPPED`.

## 13. Failure and rollback plan
- **Code.** Revert by batch. History is never rewritten; corrections use compensating records.
- **After 0006.**
  - M3 images are not a fallback, because readiness pins the revision (`db.py:52-59`).
  - Fix forward, with the workers stopped and the identities NOLOGIN.
  - Last resort, with owner consent: restore the protected backup into a fresh volume, accepting the loss of later observations.
- **Rehearsal failure.** The normal database is not touched.
- **During the pilot:**
  - A reconciliation mismatch latches the account; there is no automatic repair and exits continue.
  - An evaluation failure has no financial effect.
  - For an emergency, the owner uses Pause or Flatten.
  - Deactivation is refused while positions are live.
  - An unrunnable worker shows as `PROTECTION_UNAVAILABLE` and "worker not running".

## 14. Progress
- **2026-09-29 — PLANNED (read-only).**
  - Read:
    - the instructions and contracts listed in §2;
    - ExecPlans 0011–0014;
    - the execution, replay, accounting and migration code;
    - the web execution code;
    - the harness.
  - No file was changed.
- **2026-09-29 — Owner answered §3.3** with "accept all recommendations" (see §3.3 and DECISIONS). Implementation remains unauthorized until the owner approves this plan for implementation.
- **2026-09-29 — Implementation authorized; preconditions (OBSERVED).**
  - The owner approved this plan for implementation and the inert §12 deployment, and excluded every activation step (status line).
  - `gh pr list` showed PR #1 (0013, merge `fec2a07`), PR #3 (0014, merge `159a92f`) and PR #4 (0015, merge `c96726c`) merged into `main`; PR #2 (ExecPlan 0016 CI) is also merged.
  - The normal app runs the 0014 fix: in `adaptive-spot-lab-api-1` (image `sha256:86bf8e40…7a602`) the CRLF-normalized `app/execution/market_view.py` hashes to `c253ed06…8554`, the same as `main`. It was deployed at 12:47–12:48 UTC from PR head `5a1f858`, per [ExecPlan 0014 §10.5](0014-bounded-latest-quote.md).
  - Branch `claude/m4-fixed-pilot` was created from `c96726c`. Between the planning base `971cd4a` and `c96726c`, among `services/engine/app`, `apps/web/src`, `tools` and `compose.yaml`, only `tools/ci/compose.images.yaml` changed.
- **2026-09-29 — Citation recheck against `c96726c` (OBSERVED).** Every code citation in §2 matches its line, with these differences:
  - `engine.py:295` → the duplicated 5 s constant is at `engine.py:296` (`seen + timedelta(milliseconds=5001)`); `:231` is correct.
  - STATUS.md:64-65 → the M4 row is now STATUS.md:70 (M3 at :69).
  - README.md:67-79 → the plan list now covers 0001–0016 (README.md:67-82).
  - 0013-m3-gate-closure.md: the replay finding is now §5.3 at :128-148 and the cleanup §4 at :39-43; 0013 is merged with results in §7.
  - 0014-bounded-latest-quote.md:3 now reads "IMPLEMENTED and deployed to the normal app … B4 FAILED": the bounded read is verified, but the seven-day replay still misses its 20 min budget for a different reason (about 46 ms per engine step once positions are open; §10.3 there). §4.3 item 5 (rerun the seven-day replay once 0014 is accepted) therefore stays conditional: 0014's B4 is not accepted.
  - DECISIONS.md:58-68 is the 2026-09-29 screen-reader decision; the M4 pilot decisions are at DECISIONS.md:70.
  - Contract citations (ROADMAP, EVALUATION, RISK_POLICY, OPERATIONS, CONFIGURATION, API_CONTRACTS, AUTONOMY_MATRIX) match.
  - 0014's finding also bears on M4 (OBSERVED): per-step work added by run state and capture raises replay step cost, so M4 keeps its per-step reads small (one experiment row lock; approvals and causes only when a run exists).
- **2026-09-29 — B0 contracts, harness skeleton, new secret (IMPLEMENTED; VERIFIED as below).**
  - Contract sections added: EVALUATION (protocol, baselines, reports), OPERATIONS (pilot operations, OD-11/12/14, activation runbook), API_CONTRACTS (M4 routes), DATA_CONTRACTS (M4 records), RISK_POLICY (latch resolution), CONFIGURATION, SECURITY, PAPER_EXECUTION, STRATEGIES and MARKET_DATA. FRONTEND and TESTING are updated with B6/B7, when the pages and suites exist. STATUS's M4 row now reads in progress.
  - Secret `evaluation_db_password`: `tools/lib/Acceptance.psm1` (so `tools/setup-local.ps1` and every isolated run create it only if missing), `compose.yaml` top-level secrets and `engine-tests`, and the CI secret loop in `.github/workflows/ci.yml`.
  - `tools/m4-acceptance.ps1` skeleton: `Prepare` (seven targets: engine, browser, recovery, worker, replay, pilot, rehearsal; subnets `10.253.x`), `Snapshot` (numbered snapshots; a later one fails on any source difference or commit change), `Build`, `Generate`, `Checks` (the M3 checks plus `docs-links`), `Regression`, `Report`, `Stop` (no `-v`). Every other phase throws "not implemented yet" until its batch lands; none can be skipped.
  - `tools/check_links.py`: relative Markdown links and GitHub-style anchors. It reports four pre-existing absolute Windows-path links in the historical 0003 record as known warnings rather than rewriting that record.
  - Verification, run `m4b0-0929a` on the B0 working tree (base `c96726c`): `Checks` exit 0 in 54 s (lint, typecheck, web unit, api check, ruff, OpenAPI check, format check, web build, docs-links: 76 files, 0 broken, 4 known warnings); `Regression` exit 0 in 322 s (**169 passed**, no skips; mode guard refuses `OFFLINE_TEST` and `HISTORICAL_RESEARCH` outside `asl_m1_`, allows `FORWARD_PAPER`); `git diff --check` clean; `Stop` removed containers and networks only.
- **2026-09-29 — B1 pure evaluation core (IMPLEMENTED; VERIFIED as below).**
  - `app/evaluation/`: `bootstrap` (seeded stationary bootstrap, nearest-rank percentiles from exact fractions), `baselines` (matched-flow buy-and-hold, atomic flow application that changes nothing while a FLOW mark is pending), `series` (hourly grid, gaps, log returns, paired differences, drawdown), `metrics` (trades rebuilt from fills with the ledger's sell-cost rule, fees, cost split, turnover, exposure union) and `report` (pure `build` plus canonical JSON and SHA-256). Decimal arithmetic uses the engine's 96-digit context throughout; floats appear only in the bootstrap.
  - `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1` added to `app/execution/definitions.py` with `m4_seed_rows()` (seeding is B2).
  - Verification (engine test image, source mounted read-only): ruff clean; `tests/test_m4_evaluation.py` **19 passed**, together with `tests/test_m3_unit.py` (28 passed). Hand-computed fixtures: the BTC baseline purchase (price 100.01, quantity 99.99000, gross 9999.99990000, fee 0.09999000 BTC, NAV 99.890011), a buy/two sells/dust replay (realized −0.24485500), the spread/slippage split (0.04 / 0.06), drawdown 0.1 and paired log differences. Hypothesis: unit issuance at fixed marks is NAV-neutral to the 1E-36 unit quantum, and for every baseline each matched flow enters at its ledger amount with cash = contributions − purchases.
  - One test defect was found and fixed during the run: the first property test added 36-decimal units in Python's default 28-digit context; it now uses the engine's exact helpers.
  - Early timing probe (not the §10 measurement): one 2,000-resample interval over 2,160 hourly samples took 1.3 s in a container limited to 0.5 CPU and 256 MiB.
- **2026-09-29 — B2 migration 0006, approvals, manifests and controls (IMPLEMENTED; VERIFIED as below).**
  - `alembic/versions/0006_m4_fixed_pilot.py`:
    - refuses to run if any M3 order carries a non-null `run_ref`, then replaces it with `run_id` (FK to `experiments`, `FORWARD_PAPER` only); `run_id` is also added to mandates, evaluations, risk decisions, valuations and incidents;
    - new tables `owner_approvals`, `experiment_manifests`, `experiments` (one active experiment per mode by partial unique index), `experiment_events` (a request is applied at most once by unique `request_id`), `risk_latch_resolutions`, `evaluation_marks`, `evaluation_reports`;
    - `OWNER_FLATTEN` origin and exit reason; `HOURLY` and `RESUME` valuation purposes;
    - triggers: append-only history, no experiment delete, the transition-and-actor guard (the API may only go DRAFT→READY/STOPPED and READY→STOPPED; everything else is the execution identity's; versions advance by exactly one; COMPLETED/FAILED are frozen), event actor checks and the mode guard;
    - seeds `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1` as `PROPOSED`, with a digest check;
    - `asl_evaluation` is created NOLOGIN with SELECT on what reports need and INSERT on `evaluation_reports` only. Downgrade raises.
  - `app/experiments/`: code identity (SHA-256 of the `app/` tree, CRLF-neutral), states, manifest composition, open causes, exact-hash approvals (advisory lock, expected version, idempotency; manifest approval moves DRAFT→READY) and owner controls (durable requests bound to the experiment version; a lock wait fails fast as `EXPERIMENT_BUSY_RETRY`).
  - Also: `db.py` (revision `0006_m4_fixed_pilot`, the `evaluation` identity with its timeouts), the engine's seeded check over all seeds, the M4 invariant queries I1–I10 in `app/execution/acceptance.py`, the M4 acceptance helper `app/experiments/acceptance.py`, and the `Migration` harness phase. The synthetic market writer's database guard now also accepts the M4 isolated prefixes, as M3 did for its own.
  - Tests: `tests/test_m4_schema.py` (12): seeds, code identity, draft manifest, approvals, one active experiment, idempotent version-bound requests, the transition guard by role, actor/append-only/market-role denial, constraints, evaluation identity limited to reports.
  - Verification:
    - Run `m4b2-0929a` failed at the concurrent writer: the synthetic writer refused the `asl_m1_m4_` database name. Fixed as above. `Stop` keeps volumes, so the rerun used a fresh run.
    - Run `m4b2-0929b`: `Migration` exit 0. Populated 0005 (M1, M2 and M3 seeds; 3 filled orders and a `DAILY_LOSS` latch), then 0006 while the synthetic writer published. M1/M2 table digests and the M3 fingerprint (`96f91612…`) were identical before and after; the writer made progress; reconciliation OK. The M4 seed (READY experiment, a start request, a HOURLY mark, a FAILURE report, a latch resolution) passed every M3 and M4 invariant. The dump (`48bfdc4c…`) restored with identical fingerprints and OK reconciliation; the API reported ready.
    - `Regression` exit 0: **200 passed** in 336 s, no skips (31 of them M4: 12 schema, 19 evaluation); the mode guard as in B0. Ruff clean.
- **2026-09-29 — B3 engine integration (IMPLEMENTED; VERIFIED as below).**
  - `app/execution/engine.py`: the step loads the mode's experiment after the account (lock order lease → account → experiment) and applies owner requests exactly once: pause, flatten and stop before fills; start and resume after the step's valuation. It also covers:
    - W0 activation with a `STARTUP` valuation and daily reference, deferring while the valuation is invalid;
    - code-identity and definition checks at Start, and the MAIN cost taken from the manifest;
    - latch resolutions bound to the reviewed latch IDs, with a `RESUME` valuation;
    - `OWNER_FLATTEN` obligations after protection;
    - hourly and flow capture, run state (pause sync, stop, OD-10, completion);
    - `EXECUTION_DOWNTIME` and `SEGMENT_STARTED` at lease acquisition;
    - `run_id` on every run-linked row.
  - `app/execution/pilot.py` (new): run state and SYSTEM events. `store.py`: unresolved latches only, and `run_id` parameters. `lifecycle.py`: `OWNER_FLATTEN` origin and precedence. `activation.py`: MAIN refuses an environment cost scenario. `worker.py`: a disabled worker idles with a 5 s heartbeat, and jumped publications are skipped. `driver.py`: timed inputs.
  - Replay: `fingerprint.py` (`M3_TABLES` and the extended `TABLES`), the `pilot-lifecycle` scenario, `app/replay/experiment.py` and timed controls in `run.py` (decision 21). The M3 fingerprint helper keeps the M3 columns.
  - Found and fixed during B3: decisions 19 and 20, plus `request_by_key` returning the `CAUSE_OPENED` event instead of the application.
  - Tests:
    - `test_m4_engine.py` (26): activation and refusals; controls; the §4.2 cases (pause during an accepting step, parallel duplicates, a lock wait during a slow step, resume racing a new latch, flatten crossing a stop, flatten without quotes, revocation mid-run, a kill after a commit, integrity, drawdown on a flat account, downtime, a new code identity, a top-up while holding);
    - `test_m4_replay.py` (2): pilot-lifecycle determinism and recorded-run equivalence with controls;
    - `test_m4_properties.py` (1): a Hypothesis sequence of controls, quotes and restarts, checking I1–I10, the M3 invariants, reconciliation and exactly-once application after every step.
  - Verification on the `m4b2-0929b` engine target, with the working-tree source mounted read-only: ruff clean; M4 tests **41 passed** in 572 s; full suite **229 passed**, no skips, in 1006 s. The machine was shared with another session's M3 suites, so these times are not budget measurements. A one-line effect for a flatten request that finds no live run was added after the full run started; B4's full run covers it.
- **2026-09-29 — B4 owner API and views (IMPLEMENTED; VERIFIED as below).**
  - `app/main.py`:
    - routes `GET/POST /v1/approvals`, `GET /v1/approvals/requests/{key}`, `GET/POST /v1/experiments`, `GET /v1/experiments/{id}`, `POST /v1/experiments/{id}/{start|pause|resume|flatten|stop|discard}`, `GET /v1/experiments/{id}/requests/{key}` and `GET /v1/experiments/{id}/reports/{report_id|latest}`;
    - `ExperimentError` in the shared error envelope (a 503 is retryable); `approvals` and `experiments` as log areas; no-store on both paths;
    - `experiment` filters on orders and positions, with `experiment_id` on their summaries;
    - `OWNER_FLATTEN` in origins and exit reasons; `SystemStatus.trading` and `evaluation`.
  - Risk view (`app/execution/views.py`, new `app/experiments/views.py`): main activation and its blockers are derived from the database (unapproved policy or strategy, no experiment, unapproved or `UNSET` manifest entries, experiment state, open causes, execution identity NOLOGIN). It also shows latch resolutions, the policy's approval state and the running cost scenario. This replaces M3's `clearable_in_m3` field. The static `MAIN_BLOCKERS` remain only in the worker's start log.
  - Web contract alignment only; the UI is B6. The strict Zod schemas for status, risk, orders and positions match the new API, and their unit fixtures were updated. `e2e/execution.spec.ts` still expects the M3 blocker text and is updated with the B6 pages.
  - Tests: `test_m4_api.py` (5) covers dual identity, strict queries and bodies, the 8 KiB cap, no-store, 404s, exact-hash and version conflicts, lookup by key, the HTTP lifecycle returning `ACCEPTED` until the SYSTEM applies it, experiment filters, a non-resumable `INTEGRITY`, system status, derived blockers and the running cost, one forward draft at a time, the refused fixture cost, and discard. The M3 risk-view test now expects the derived blocker codes.
  - Verification (run `m4b2-0929b`): `test_m4_api.py` plus `test_m3_api.py` **8 passed**; `Build`, `Generate` (OpenAPI 7 new M4 paths; `api.ts` regenerated), `Build` again, then `Checks` exit 0 in 64 s (lint, typecheck, web unit 32 passed, API check, ruff, OpenAPI check, format, web build, docs links: 76 files, 0 broken).
  - Harness note: `Generate` rewrites source files, so the images must be rebuilt before `Checks`. In the final run the generated files are already current, so `Generate` changes nothing and the snapshot comparison proves it.
  - Gap found in B5: B4 ran only the API test modules. The full suite later showed `test_api.py` still expected the M3 `SystemStatus` shape; that assertion was updated in B5 (below).
- **2026-09-29 — B5 evaluation worker, identity commands, Compose and pilot tools (IMPLEMENTED; VERIFIED as below).**
  - `app/evaluation/loader.py` and `worker.py`:
    - point-in-time report inputs;
    - the hourly capture window, a decision taken while implementing: the grid point for hour H is read from captures in [H, H + 300 s], so a report as of H reads hourly rows up to H + 300 s, and a report is written only once the execution checkpoint passes that bound (`loader.complete_at`);
    - SNAPSHOT at HH:05, DAILY at 00:10 and FINAL after STOPPED;
    - a FAILURE record and log line on failure, with no financial effect;
    - a 5 s heartbeat thread, so a long pass never fails the healthcheck, and `app/evaluation/health.py`.
  - Engine: the pre-check poll also watches FINAL reports, so a flat STOPPED run reaches COMPLETED.
  - `app/execution/identity.py`: JSON output; `enable --main --experiment` gated by `main_preflight` (experiment READY or RUNNING, every approval active, reconciliation OK); `disable`, which refuses over live forward exposure unless overridden; `preflight` and `state`; the evaluation identity.
  - `compose.yaml`:
    - `execution-worker` is now `unless-stopped`;
    - new `evaluation-worker` (profile `execution`, disabled by default, read-only root, 0.5 CPU, 256 MiB, 64 PIDs, private network only, its own secret);
    - one-shot `pilot-admin` (profile `admin`).
  - Tools: `tools/pilot-activate.ps1`, `tools/pilot-deactivate.ps1`, `tools/pilot-market-dump.ps1` and `tools/lib/Pilot.psm1` (explicit compose file, the database name read from the env file, an owner-only protected backup with SHA-256). Harness phase `ActivationRehearsal`.
  - Contracts: OPERATIONS (deactivation after COMPLETED; rehearsal), EVALUATION (capture window), INTEGRATION_EVIDENCE (restart policy, bootstrap and Python `random` sources, observed hardening).
  - Tests: `test_m4_reports.py` (6): a report reproducible as of a past hour after later activity; the checkpoint rule; one report per (kind, as-of); failure isolation; the main-identity preflight; disable refused over live positions; FINAL completing a STOPPED run.
  - Verification:
    - `test_m4_reports.py` **6 passed**. Its first run failed two assertions that had not expected a DAILY report, which the multi-day synthetic run legitimately makes due; the assertions were corrected.
    - `ActivationRehearsal` on run `m4b5-0929a` exit 0 in 75 s:
      - refusal of an unknown experiment, with both identities still NOLOGIN;
      - activation with a checksummed backup (`82a2db14…`) in an owner-only directory, both identities LOGIN and both flags set;
      - both workers healthy, hardened as specified (`container-inspection.json`), with the lease held and the experiment READY with no activation;
      - deactivation refused while READY, then discard;
      - deactivation with a backup, workers stopped, both identities NOLOGIN, both flags `0`, invariants and reconciliation OK.
    - The first rehearsal attempt failed because the tool read the trailing status line instead of the preflight result. `preflight` and `state` now print only their own result.
    - `Regression` (images rebuilt from the working tree): 238 passed, 2 failed. Both were exact-shape assertions: `SystemStatus` (from B4) and `identity.status`. After the fix, those two modules passed 12 of 12. B7 reruns the full suite on the final snapshot.
- **2026-09-29 — B6 web (IMPLEMENTED; VERIFIED as below).**
  - Skill workflow (OBSERVED):
    - read the official shadcn skill from `~/.codex/skills/shadcn` (its rules files included) and the Lightweight Charts skill from `~/.codex/skills/lightweight-charts`;
    - ran `pnpm dlx shadcn@latest info --json` in `apps/web`: preset `b2fms61Bqi`, style `base-nova`, base `base`, Lucide, 15 components;
    - `search @shadcn` found tabs, accordion, collapsible, dialog, alert-dialog, checkbox, scroll-area, select, native-select and tooltip; `docs` returned Base UI guides for collapsible, checkbox, alert-dialog and toggle-group;
    - `add collapsible checkbox` was dry-run, viewed, then added. They use the installed `@base-ui/react`, `lucide-react` and `cn` packages, so there is no new dependency.
    - `lightweight-charts` 5.2.1 (package.json) with the v5 `addSeries(LineSeries, …)` API, following the existing candle-chart adapter: lazy import, token colors, `autoSize`, `remove()` on unmount, TradingView attribution.
  - Pages and routes: `/approvals`, `/experiments` and `/experiments/$experimentId`, with nav entries, the report view, the NAV chart and its exact-value table, and the owner controls. See [FRONTEND](../contracts/FRONTEND.md#m4-approvals-experiments-and-reports).
  - Other page updates: the risk page shows derived blockers, open versus resolved latches and the running cost; its cost badge no longer claims "not approved". System shows an evaluation row. The M3 browser spec's three stale expectations were updated.
  - Fixture: `report.sample.json` is a real SNAPSHOT document that the engine test produced from labeled synthetic inputs (opt-in `ASL_M4_SAMPLE_REPORT`). Its `contributions` reads 0 only because the fixture funding row carries today's wall-clock time while the simulated run is dated 2026-09-07.
  - Harness: `BrowserApprovals` (recreates the disposable browser database, funds it synthetically, runs one test) and `BrowserError`; helper action `fund`.
  - Fixed during verification:
    - the report schema used loose objects, which Start's server-function serialization check rejects; it now strips keys the page does not show;
    - an always-true condition in the chart;
    - the route tree could not be regenerated through a bind mount (EXDEV), so the source is copied into the container for the build;
    - my own inspection found Start still offered while a Start request was pending (the API would refuse it). Such controls are now disabled and labeled "(requested)", and the pending alert says when no worker is running to apply requests.
  - Verification (`web-tools` of run `m4b5-0929a`): build exit 0; lint 0; typecheck 0; web unit **38 passed** (11 files; 6 new M4 tests); Prettier check 0. `BrowserApprovals` 1 passed in Chromium: create draft (with validation), 8 definition approvals and the manifest through confirmation dialogs, Escape returning focus to the trigger, Start staying "Accepted, waiting for the execution worker" after a reload, derived risk blockers, no horizontal overflow at 390 px on all three pages, Back navigation. `BrowserError` 1 passed.
  - Own inspection in the in-app browser at 1440 and 390 px: the approvals and experiment pages have no horizontal overflow at 390 px.
  - NOT RUN in B6: a populated pilot page with reports and the chart in a real browser, and SSR/LCP/CLS and chart-leak measurements. These are B7's `BrowserPilot` and `PerformanceBrowser` on real pilot data. No screen-reader review (DECISIONS 2026-09-29); no conformance claim.
- **2026-09-29 — B7 acceptance tooling (IMPLEMENTED).**
  - Harness phases:
    - `PilotLifecycle`, `PilotFaults`, `PilotDowntime` and `Evaluation`: one real-time pilot on the pilot target, with the synthetic feed `tests/m4_pilot.py`, the real approval and activation commands, and the workers `unless-stopped`;
    - `BrowserPilot`, `ApprovalAuth` (`tests/m4_probes.py`), `Replay`, `ReplayIsolation`;
    - `PerformanceEngine`, `PerformanceApi`, `PerformanceReport` and `PerformanceBrowser` (`tests/m4_performance.py`, `e2e/m4-performance.spec.ts`);
    - `SecretScan`.
  - Helper actions: `control-race` (200 randomized requests racing the running worker; p95, deadlocks, resolvability by key), `fund`, and stops in `pilot-state`.
  - A replay whose research run stops records the hash of its FINAL evaluation report, so report determinism on replay output is part of `Replay`.
  - Dry runs on development runs (not measurements):
    - the 90-day report took about 20 s per build at 0.5 CPU / 256 MiB, with an identical hash;
    - all 11 live auth refusals passed;
    - the pilot-lifecycle replay CLI accepted all 5 controls, reached STOPPED and recorded a FINAL report hash;
    - replay tests: 6 passed.
  - First final run `m4f-0929a` (from `3cbb76b`):
    - Build, Generate (no source change), Checks, and Regression (**240 passed**, no skips) passed.
    - `Migration` failed: its synthetic M3 seed ran the M4 engine on schema 0005, and that engine reads `experiments`, which exists only from 0006 (it passed in B2, before the engine changed).
    - Fix (`10b48b1`): the phase builds the merge-base commit's (`c96726c`) engine runtime image from a clean `git archive`, taking from this tree only the fixture's database-name guard (its only difference), and seeds the 0005 state with that M3 code.
    - Scratch run `m4mig-0929a` then passed `Migration` in 97 s. Because the harness changed, the final run restarted as `m4f-0929b` on a new snapshot.
  - Second final run `m4f-0929b` (from `10b48b1`, 15:54–18:08 UTC):
    - Build, Generate (no source change), Checks, Regression (**240 passed**), Migration, ActivationRehearsal, BrowserApprovals, ApprovalAuth, BrowserError, PerformanceApi, PerformanceReport, PerformanceEngine, Replay, ReplayIsolation and PilotLifecycle passed. Its measurements are superseded by the final run below.
    - `PilotFaults` failed at its last wait (`faults-running`). The control race itself had passed: 200 requests, p95 36.6 ms, 0 deadlocks, every key resolvable.
    - Cause: the synthetic feed `tests/m4_pilot.py` exited when the phase stopped PostgreSQL (`failed to resolve host 'postgres'`), so no quote followed the outage. Every owner resume after it was refused with `RESUME_REJECTED` (`MARK_UNAVAILABLE_SOL`), and the run stayed `PAUSED` with both positions held. That is the specified fail-closed behavior; the defect was in the test feed.
    - The event log and the feed's exit log are kept in `.cache/m4/m4f-0929b/pilot/`.
    - Fix (`be61a32`): on `OperationalError` the feed disposes its pool, retries every second and skips the quote seconds it missed.
    - Scratch check (not evidence): the fixed feed ran on a fresh database in the stopped `m4f-0929b` pilot cluster. PostgreSQL was stopped for about 20 s; the feed retried 17 times, exited 0, and its only SOL quote gap was the outage (18:15:33–18:15:51).
    - The final run restarted as `m4f-0929c` on a new snapshot. Its order puts the real-time pilot phases before the 19:00 UTC entry boundary.
- **2026-09-29 — B7 final acceptance run `m4f-0929c` (VERIFIED).** It ran from `be61a32`, with snapshot 01 at 18:13:29 UTC. Every §10 phase passed on that snapshot; results, budgets and the Q01–Q10 assessment are in §16.
  - Phase order:
    1. Build, Generate, Checks, Regression and Migration.
    2. ActivationRehearsal, BrowserApprovals, ApprovalAuth, BrowserError, PerformanceApi and PerformanceReport.
    3. PilotLifecycle, PilotFaults, PilotDowntime, Evaluation, BrowserPilot and PerformanceBrowser.
    4. PerformanceEngine, Replay, ReplayIsolation, SecretScan, then the closing Snapshot.
  - One ordering error, mine: the first driver had placed `Replay` before `PerformanceEngine`.
    - `Replay` needs the forward export that `PerformanceEngine` writes, so it refused to start after 1 s, before doing any work. The log is kept as `phase-…-Replay-order-refusal.log`.
    - The remaining phases then ran in dependency order on the same snapshot.
  - Before the measured 60-minute engine workload, the run's own idle containers were stopped with `docker stop`, not removed, so `SecretScan` still read their logs. These were the completed pilot's workers, its API and web, and the synthetic feed.
  - Machine sharing: ExecPlan 0017's isolated `rt-0929f` PerformanceReplay ran from 18:56 to 19:22:31 UTC.
    - It overlapped the end of PilotLifecycle and all of PilotFaults (including the control race), PilotDowntime, Evaluation, BrowserPilot and PerformanceBrowser.
    - That session then held every further workload until this run finished, by agreement. PerformanceEngine started at 19:22:59 on a machine running only the normal app and that session's idle databases.
  - My own inspection of the completed pilot, in the in-app browser, found the two items listed in §16. `Stop` then removed the run's containers and networks and kept its 7 volumes.
- **2026-09-29 — B8 inert normal deployment (VERIFIED).** The pushed commit `be61a32` was deployed to `adaptive-spot-lab` at 20:37 UTC:
  - protected backup and an isolated restore rehearsal;
  - migration 0006;
  - api, web and market-worker recreated;
  - neither pilot worker started, both identities NOLOGIN.

  The identities and checks are in §16. GitHub CI could not run.
- **2026-09-30 — merges.** PR #7 (M4) and PR #8 (ExecPlan 0018) were merged as merge commits at the owner's request (`7ae0217`, `9e84eff`), then PR #6 (ExecPlan 0017, `784a67d`) after its normal deployment.
- **2026-09-30 — M4-B activation (VERIFIED).**
  - The owner made 10 exact-hash approvals in the UI: 9 definitions and the manifest.
  - The owner created experiment `d779fbf4…`, pressed Start, and ran `tools/pilot-activate.ps1`.
  - It was ACTIVATED at 09:09:52 UTC, and every §12 check passed, including the first SNAPSHOT at 10:05 UTC.
  - The checkpoint date is 2026-11-25 (OD-13).
  - Details are in §16.

## 15. Decision log (PROPOSED)
1. **Durable intents.** Owner controls are durable intents, and the SYSTEM applies their effects in the fenced step. The API never writes latches, obligations or orders.
2. **Separate approvals.** Approvals live in a separate append-only exact-hash table; definitions stay immutable.
3. **Pause and integrity latch.** Run pauses never reuse `account_state.paused`. The integrity latch cannot be cleared in M4.
4. **W0 boundary.** No historical scan, and entries only on bars that close after activation.
5. **Hourly capture.** Replayable hourly valuation and mark capture happens inside the step, with marks stored inline and no new pins.
6. **Evaluation worker.** A separate read-only worker and role, with a pure-Python bootstrap and no new dependency.
7. **Code identity.** The manifest carries a code-identity digest. A mismatch refuses activation; later changes start new segments.
8. **Flatten precedence.** `OWNER_FLATTEN` ranks just below `PROTECTIVE_STOP`.
9. **Cost scenario.** MAIN ignores environment cost scenarios.
10. **Restart policy.** Chosen only after reading the Docker documentation.

Implementation decisions (IMPLEMENTED; the batch is named in each):

11. **`RESUME` valuation purpose (B2).** The plan named only `HOURLY`. A resume's fresh valuation is its own audited `RESUME` row, which each latch resolution references.
12. **`FAILED` is a SYSTEM transition (B2).** §5.2 allows OWNER or SYSTEM; M4 exposes no owner control for it, and the database guard lets only the execution identity set it.
13. **`DRAFT` → `READY` inside the manifest approval (B2).** Approving the manifest, with every referenced definition approved and no `UNSET` field, marks the experiment `READY` in the same transaction. There is no separate ready action.
14. **API lock scope (B2).** Owner control requests lock only the experiment row, never the account; the worker keeps lease → account → experiment. A lock wait over 1 s returns `EXPERIMENT_BUSY_RETRY` (503), and the idempotency key resolves the outcome.
15. **I2 ordering (B2).** The pause invariant orders cause events and fills by `recorded_at` (clock time inside the transaction): a cause opened earlier in the same step counts, and a latch the step raises after the fill does not.
16. **OD-10 interpretation (B3).** With `DRAWDOWN` open, no live position, open order or active obligation, and NAV ≤ 0.92 × high-water, the SYSTEM appends `DRAWDOWN_UNRECOVERABLE` and moves the run through `STOPPING` to `STOPPED`.
17. **Run-start boundary details (B3).** W0 is the activation step's trigger watermark. When the account is flat, the checkpoint jumps to the current maximum publication and the worker skips the jumped publications; a first MAIN start with no checkpoint and no exposure also begins there. The evaluation floor is the bar that closed at the start of the activation hour.
18. **Downtime threshold (B3).** A lease acquisition more than 20 s (10 s plus the 10 s lease) after the checkpoint's last step time records `EXECUTION_DOWNTIME`. The worker persists the checkpoint at least every 5 s while it runs.
19. **Concurrent duplicate requests (B3).** A request whose key committed while it waited for the lock returns the original result: the key is read again after the lock (and after a unique violation on create).
20. **Pre-check poll (B3).** Once per worker loop, not per publication, the worker reads the latest owner event, the posted-funding count and the latest approval. When they change it refreshes its no-effect pre-check, so a control committed between steps is never skipped; an approval change forces the next step of a live run.
21. **Replay research experiments (B3).** A replay with controls runs under a research experiment in the activation's mode (`HISTORICAL_RESEARCH`; `OFFLINE_TEST` in fixture tests). It is composed like an owner draft and written `READY` at version 1 without owner approval, which isolated research does not need; the engine still checks every manifest hash and the code identity at Start. Requests are written at their replay time under the API's rules. An equivalence replay re-inserts a recorded run's requests before the earlier of their request time and the step that applied them.
22. **Fingerprint tables (B3).** `M3_TABLES` keeps the ExecPlan 0011 column set for M3 comparisons, including the populated-0005 fingerprint in the `Migration` phase. `TABLES` adds run linkage, experiment events, latch resolutions and marks.
23. **Risk-view blockers (B3 → B4).** M3's static `MAIN_BLOCKERS` stay until B4 derives the risk view's blockers from the database; the engine never used them to decide.

## 16. Completion evidence
To be recorded:
- **M4-A:** run ID, source manifest, phase results, budgets, Q01–Q10 results and deployment identities (below).
- **M4-B:** approval IDs and hashes, and activation evidence. VERIFIED 2026-09-30 (below).
- **M4-C:** checkpoint report hash, limitations and the next decision. NOT RUN: due at the owner's checkpoint, 2026-11-25 (OD-13).

### M4-A isolated acceptance — `m4f-0929c` (VERIFIED 2026-09-29)
- **Source.** Commit `be61a32` on `claude/m4-fixed-pilot`.
  - Snapshot 01 (18:13:29 UTC) and snapshot 02 (20:32:58 UTC) cover 288 source files, with 0 differences and the same commit. Only documentation was uncommitted, which the snapshot excludes.
  - Logs, the manifest and the measurements are in `.cache/m4/m4f-0929c/`, and the phase logs in the session scratchpad.
- **Host.** Windows 11 Home 10.0.26200 with Docker Desktop, driven by Windows PowerShell 5.1.
  - The normal app kept running with public collection enabled throughout, as it did for the M3 measurements.
  - Machine sharing is described in §14.
- **Phases.** Every phase exited 0.

| Phase | Seconds | Result (actual) |
|---|---|---|
| Build, Generate | 48, 8 | Generate changed no source (the snapshot comparison proves it) |
| Checks | 67 | lint, typecheck, web unit **38 passed** (11 files), API check, Ruff, OpenAPI `--check`, Prettier check, web build, docs links (76 files, 0 broken) |
| Regression | 1,045 | **240 passed**, no skips (M1–M4); mode guard as in B0 |
| Migration | 94 | Populated 0005 (seeded by the `c96726c` M3 engine image) → 0006 while the synthetic writer published. M1/M2 table digests and the M3 fingerprint `0f7307a3…3499` were identical before and after. The M4 seed passed every M3 and M4 invariant. The dump `5f1efdb9…c1d3` restored with the same fingerprint (`2f30fc41…20f5`) and reconciled OK; the API reported ready. |
| ActivationRehearsal | 76 | An unknown experiment was refused (`EXPERIMENT_NOT_FOUND`) with both identities NOLOGIN. Activation took a checksummed backup (`2974ed40…2c1f`); after it both identities were LOGIN, the lease was held and the experiment READY with no activation. Deactivation was refused while READY; after a discard it succeeded with a backup (`b0bebd41…f7be`): both identities NOLOGIN, invariants and reconciliation OK. |
| BrowserApprovals | 60 | Chromium: draft with validation, 8 exact-hash definition approvals and the manifest through confirmation dialogs; Escape returns focus to the trigger; Start stays "Accepted, waiting for the execution worker" across a reload; derived risk blockers; no horizontal overflow at 390 px; Back |
| ApprovalAuth | 7 | 11/11 live refusals: missing service key, missing session or forged session on reads, approvals and controls (401); an oversized body (413); an untrusted Host (421) |
| BrowserError | 31 | With the private API down, all three M4 pages say "unavailable" and never show an empty-state guess |
| PerformanceApi | 44 | see budgets |
| PerformanceReport | 43 | see budgets |
| PilotLifecycle | 1,291 | Real time: approvals, activation command, both workers, Start → `ACTIVATED`. Entries BTC 161.52 and SOL 61.51 filled on the 19:00:01 quote; a 250 top-up `POSTED` while holding; pause then resume applied; invariants and reconciliation OK. Most of the time is the wait for the 19:00 boundary. |
| PilotFaults | 248 | Covered: a pause committed with no worker and applied once after the restart (requests = applications); a 20 s frozen holder; a 15 s PostgreSQL stop (the feed retried 17 times); 30 randomized kills with racing pause/resume; then the control race (see budgets). Back to `RUNNING`; invariants and reconciliation OK after each step. |
| PilotDowntime | 323 | Worker down 19:04:47–19:09:50: `EXECUTION_DOWNTIME` 302.75 s. SOL's protective stop filled on the first fresh quote after the restart (19:09:51, 54.09); no backdated step; invariants OK. |
| Evaluation | 351 | Covered: SNAPSHOT as of 19:00 (`464c232d…`); flatten (BTC `OWNER_FLATTEN` 161.81); stop; FINAL as of 19:10:19 (`434e2033…`); `COMPLETED`. Both stored reports regenerated to the same hash (`changed: []`); invariants and reconciliation OK. |
| BrowserPilot | 33 | Chromium on the completed pilot: COMPLETED row with its FINAL report; the timeline shows pause, downtime, flatten and completion; MODELED FILLS and HYPOTHETICAL labels; NAV chart with canvas and its exact-value table; SNAPSHOT report URL survives reload and Back; 390 px without overflow |
| PerformanceBrowser | 36 | see budgets |
| PerformanceEngine | 3,861 | Production `Worker.serve` loop in process (1 CPU, 512 MiB container), real-time synthetic feed, entries at the 20:00 boundary, hourly capture, 5 owner controls (two pause/resume pairs and a flatten), a SOL protective stop. Every control applied; no incident; invariants and reconciliation OK; forward export for Replay written (75 steps, 24 events). |
| Replay | 323 | Determinism: two `fixture:pilot-lifecycle` replays gave fingerprint `a10c084f…0aad` and FINAL report `bf06d65d…ce7f` twice, labeled MODELED REPLAY, reaching STOPPED. Equivalence: the recorded forward run replayed step by step to its forward portable fingerprint `e712cd5f…77f6`. H1/H2: sensitivity replays on the restored source (`c500e2e6…4d20`) give fingerprints `146efe53…` and `72eeabc5…`; BTC fees 0.00332130 and 0.00632470. |
| ReplayIsolation | 3 | The replay network could not resolve the normal project's PostgreSQL or API (`UNREACHABLE … gaierror`) |
| SecretScan | 11 | Scanned 439 files for 49 secrets in 3 forms each (raw, uppercase, base64): container logs, harness logs, artifacts, 3 dumps and the web client and server output. 0 findings. The one allowed text is the path `secrets/owner_setup_key` in client assets (1 occurrence). |
| Snapshot | 2 | Snapshot 02: 0 source differences from snapshot 01; commit `be61a32` → `be61a32` |

- **Budgets** (declared in §10 before measuring):

| Area | Measured (actual) | Budget | Result |
|---|---|---|---|
| Engine, 60 min with a RUNNING experiment, hourly capture and 5 controls | 2,791 steps: p50 190.07 ms, p95 310.85 ms, p99 332.06 ms, max 401.81 ms (latency = step commit return − publication `available_at`); RSS max 63.5 MiB, +1.65 MiB over the final 30 min; average CPU 2.6% | p95 ≤ 750 ms, p99 ≤ 1.5 s, RSS < 256 MiB, < 10 MiB growth | passed |
| Controls, 200 randomized requests racing the running worker | p95 34.6 ms, max 38.3 ms; 0 deadlocks, 0 errors, 0 inconsistent keys (5 recorded, 171 `REQUEST_ALREADY_PENDING`, 23 `EXPERIMENT_VERSION_CONFLICT`, 1 `IDEMPOTENCY_CONFLICT`) | p95 ≤ 500 ms; 0 deadlocks; every outcome resolvable by key | passed |
| Reports, 90 days, 5 baselines, 15 intervals × 2,000 resamples, 0.5 CPU / 256 MiB | 19.91 s and 19.91 s, identical SHA-256 `71e7979e…cbfd`, max RSS 51.0 MiB | ≤ 180 s; identical hash | passed |
| API reads over 10,000 orders/fills and 10,000 experiment events | sequential p95 23.05 ms (slowest route: risk, 23.94 ms); five-way concurrent p95 148.98 ms | ≤ 250 ms; ≤ 500 ms | passed |
| Browser, experiments, FINAL and SNAPSHOT pages at 390×844 and 1440×900 | SSR p95 48–91 ms, LCP 80–124 ms, CLS ≤ 0.0255; 20 chart remounts: 7 canvases and 1 chart before and after | SSR p95 < 1,500 ms; LCP ≤ 2.5 s; CLS ≤ 0.1; no chart leak | passed |

  - The single `IDEMPOTENCY_CONFLICT` is correct: the race re-sent an earlier key with a newer expected version, which is a different request body. A lookup by key stayed consistent.
  - The control race and the browser budgets overlapped ExecPlan 0017's replay workload (§14).

- **Q01–Q10 (actual).**

| Gate | Result | Evidence |
|---|---|---|
| Q01 | Passed | States shown: awaiting worker, accepted requests never shown as applied, derived blockers, the completed pilot's timeline and reports, API failure. Report URL state survives reload and Back; the nav works at 390 px. Covered by BrowserApprovals, BrowserPilot and BrowserError, plus my own inspection. My inspection found one misleading state, finding 1 below; it is recorded rather than fixed on this snapshot. |
| Q02 | Passed within its scope | Automated: confirmation-dialog focus and return, named tables and chart (`img` with a name plus an exact-value table), non-color status text, no overflow at 390 px. My own inspection covered B6 (approvals and experiments) and the completed pilot at 800 px and 375 px: chart canvases present, the exact-value table offered, `scrollWidth` equal to the viewport. No screen-reader review (DECISIONS 2026-09-29) and no WCAG conformance claim; 200% zoom and a full contrast audit were not separately measured. |
| Q03 | Passed | 240 tests including R01–R14, the §4.2 cases and a Hypothesis property run of I1–I10. Invariants and reconciliation were OK after every pilot fault step, the migration, the rehearsal and the engine workload. Exact Decimal throughout. |
| Q04 | Passed (not a penetration test) | 11/11 live refusals; exact hash and expected version (`test_m4_api`, BrowserApprovals); NOLOGIN before activation and after deactivation; worker hardening in `container-inspection.json`; SecretScan 0 findings over 439 files |
| Q05 | Passed | Pause with no worker, frozen holder, database outage, 30 kills, 5-minute downtime with a protective exit after the restart, API failure pages, report regeneration |
| Q06 | Passed | Budgets table above |
| Q07 | Passed | Frozen Docker checks with no skips (Checks, Regression, the browser phases) |
| Q08 | Passed | Experiment state, causes and SYSTEM events (`EXECUTION_DOWNTIME`, `RESUME_REJECTED` with reasons), worker heartbeats (healthy containers), lease epochs, report failure count 0, and the UI timeline |
| Q09 | Passed | 0005 → 0006 on populated data with a concurrent writer; M4 dump and restore with identical fingerprints; activation and deactivation rehearsal with protected backups; the owner backup rehearsal and inert deployment below |
| Q10 | Passed | Module boundaries (`app/experiments`, `app/evaluation`); no new dependency (shadcn `collapsible` and `checkbox` use installed packages); guidance checked against locked versions (INTEGRATION_EVIDENCE); contracts and runbooks updated; docs links 0 broken |

- **Findings from my own inspection** of the completed pilot (OBSERVED; neither affects money handling):
  1. **Misleading pause alert on a finished run.** The experiment detail page of a `COMPLETED` run still shows the red "Paused by latched causes" alert: "OWNER since 19:10:13 UTC — an owner resume can close it", then "New entries are blocked; exits continue".
     - The owner cause that the flatten opened is still open in the data, because stop does not close causes. The page's controls correctly say "No control is available in state COMPLETED".
     - The alert should be suppressed or reworded for terminal states. This is a follow-up web fix. It was not made on this snapshot, because any source change needs a new full acceptance run.
     - FIXED 2026-09-30 by [ExecPlan 0018](0018-ended-run-cause-note.md): an ended run shows its open causes as a neutral record, and no resume is claimed unless offered. Verified by isolated run `m4w-0930a` (Checks, the pilot phases and BrowserPilot) and deployed web-only to the normal app.
  2. **FINAL run return excludes the last partial hour.** The FINAL report as of 19:10:19 shows run return 0.000% while realized P&L is −26.56 virtual USDT.
     - This follows `EVALUATION_PROTOCOL_V1` as written: the run return is the last valid hourly grid NAV over the start NAV, and there is no grid point at the stop time. So a loss after the last full hour appears in realized P&L but not in the run return or the run drawdown.
     - This is a protocol property, not a code defect. The owner should weigh it before approving the protocol hash. Changing it needs a new protocol definition version.
- **NOT RUN or limits:**
  - GitHub CI. Every Actions run in the repository ends in `startup_failure` (ExecPlan 0016 §8). The same containerized Checks and Regression ran locally.
  - The seven-day `PerformanceReplay` rerun of §4.3 item 5. It stays conditional on ExecPlan 0014 B4, which ExecPlan 0017 (PR #6, rebased on this branch) addresses.
    - Update 2026-09-30: ExecPlan 0017 merged and was deployed. Its seven-day replay meets the budget on M4's code (429.5 s and 429.0 s).
    - That dataset runs no experiment, so a rerun with M4's hourly capture enabled remains NOT RUN.
  - A pilot on real public data, the owner's approvals and activation (M4-B) and the checkpoint report (M4-C).
    - Update 2026-09-30: M4-B is done; see "M4-B owner approvals and activation" below.
    - M4-C is due at the 2026-11-25 checkpoint.
  - A screen-reader review, a WCAG conformance claim and a penetration test.

### Normal deployment — inert (VERIFIED 2026-09-29)
This ran under the owner's authorization for the §12 inert deployment, from the primary checkout at the pushed, verified commit `be61a32` (PR MentorAliu/adaptive_spot_lab#7). The owner's `.env` and secrets directory stayed in place; no secret value was read. A step-by-step scripted sequence stopped at the first failure and logged to `.cache/deployments/m4-fixed-pilot-20260929a/deploy.log`.
- **Preflight (20:33 UTC).** Before the rollout:
  - images: API `sha256:86bf8e40…a602`, web `sha256:8efe8e5b…a8b7`, market worker `sha256:ff1f854f…4118` (the 0014 release);
  - schema `0005_m3_paper_broker`, both feeds `CONNECTED` with a current quote;
  - database 667 MB, 555 GiB free.
- **Backup.** `pg_dump -Fc` of `asl`, 127,483,805 bytes, SHA-256 `523daa0a1ad2c2ed1d64acac34a13eb7b275ba2b153f48372f2eb218e0369c91`. The checksum matched inside and outside the container. The backup is in `.cache/deployments/m4-fixed-pilot-20260929a/`, whose ACL is the owner account only.
- **Rehearsal.** The backup was restored into a new `asl_m1_m4_owner_rehearsal` database of the accepted run's internal-only recovery cluster (PostgreSQL 17.11), and the accepted migrate image applied `0006_m4_fixed_pilot`.
  - It showed 0 approvals, experiments, reports and orders, both seeds `PROPOSED`, and reconciliation OK. The copy was then dropped.
  - Roles are cluster-wide and not part of a dump, so the rehearsal's role check describes the test cluster, not the owner's.
- **Rollout (20:37:13–20:37:54 UTC).**
  1. `tools/setup-local.ps1` created only `evaluation_db_password`. The 6 existing secrets kept their length and write time, and no value was read.
  2. The previous images were tagged `pre-m4` (api, web, market-worker, migrate, execution-worker).
  3. Frozen builds of migrate, api, market-worker, execution-worker, evaluation-worker, pilot-admin and web.
  4. Web, api and market-worker were stopped; one migration ran; api, web and market-worker were recreated.
  5. **Neither pilot worker was started, and neither identity was enabled.**
- **Running identity (VERIFIED).**
  - Running: API `sha256:2835309c3326c98b66684a4fa5ee3409df25fec2175d79422631c661cb82a4dc`, web `sha256:833a512ba3aacfda9888258857e15d60fb9a4b470aae484d4a3f1e5e3f0a2c43`, market worker `sha256:a8138cbb2fd960057ca8eb4f430b5563878c7308c9821b07510690b36b4da641`.
  - Built, not running: migrate `sha256:3425bfb3…e64d`, execution worker `sha256:ca763129…94f2`, evaluation worker `sha256:a400ed3f…b6ba2`, pilot-admin `sha256:c0b20689…a87`.
  - `engine.py`, `experiments/controls.py`, `evaluation/worker.py` and `main.py` in the API container match the tree byte for byte (CRLF-normalized SHA-256).
- **State (VERIFIED).**
  - Schema `0006_m4_fixed_pilot`; reconciliation as `asl_api` OK with no failed check.
  - Approvals, experiments, experiment events, reports, marks and orders all 0.
  - `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1` are `PROPOSED`.
  - `asl_execution` and `asl_evaluation` are NOLOGIN; the execution lease was never taken (epoch 0); no execution-worker, evaluation-worker or pilot-admin container exists.
  - Both feeds are `CONNECTED` again. The rollout cost 43.8 s of capture: the last quote was at 20:37:25.13 and the first new one at 20:38:08.92.
- **Surface.**
  - The API is ready (200).
  - Unauthenticated HTTP returned 200 for `/`, `/system`, `/approvals`, `/experiments`, `/risk?mode=FORWARD_PAPER` and `/orders?status=ALL&symbol=ALL`.
  - In the in-app browser, `/experiments` showed "Owner session required". System read Account funded, Market data ready, Model runtime unconfigured, Paper trading disabled, Evaluation reports disabled, Paper execution worker not running.
  - No owner sign-in, funding, approval, Start or activation was performed on the normal app.
- **Rollback.** Stop api, web and market-worker. The `pre-m4` images are not a fallback after 0006, because readiness pins the revision (§13). Fix forward with both workers stopped and both identities NOLOGIN. As a last resort, with owner consent, restore the protected backup into a fresh volume.

### M4-B owner approvals and activation (VERIFIED 2026-09-30)

The owner instructed this in chat ("ok I approve all to finish m4") after M4 (#7), ExecPlan 0018 (#8) and ExecPlan 0017 (#6) had merged. Chat text is not an approval; the approvals below were made by the owner in the authenticated UI. The M4 implementation session had ended without recording M4-B, so the ExecPlan 0017 session recorded it at the owner's request.

**Approvals (OWNER, `APPROVE`, 09:04:35–09:05:34 UTC)**

| Seq | Approval ID | Target | SHA-256 |
|---|---|---|---|
| 1 | `b9ea4d69-5029-4597-80eb-fbc555bc3f88` | `BASELINE_SET_V1` | `ed78ef720cdd5ea414c66b12fcfa5b33c6c0a62667e7b6e661cca12634e1e2f3` |
| 2 | `c118a8b0-54bf-4074-ae66-9a9b04eed825` | `PAPER_COST_V1` | `9beb9aac8372dd778077a9b640cc28c284aaff374cb55c4ccb32cd49763b45b3` |
| 3 | `8969a4c0-e6e4-4425-8e42-9014b4486690` | `COST_SCENARIO_HYPOTHETICAL_H1` | `c3fe1259df180e1a4891c06eeb03d0e0bf2375e0cf43ba49a226f23ea09821a5` |
| 4 | `45eabc8d-f622-4c73-a979-f88973905500` | `COST_SCENARIO_HYPOTHETICAL_H2_STRESS` | `eddc7ed3c48d333da65ea2a1fd2f94fa463651ca2950f3605b5a41743b77153a` |
| 5 | `a458dc9c-084f-4a97-bb5d-71a1f3bd3532` | `EVALUATION_PROTOCOL_V1` | `5385feb9bdc9fe513edb06a08615d6e06cf8586bd688602b29f32cd1ed60db4c` |
| 6 | `c7591d1b-3995-4e12-a31d-3e3d0e8d938f` | `FILTER_POLICY_V1` | `00157b2619de4b23358dc351d15f6364c657e2b27032db9bdc155dc61fbdc023` |
| 7 | `f6f1bbdc-6eed-479d-a460-d08b473460d0` | `PAPER_PILOT_V1` | `25ba32b51808c0b13178c1fb551d782f90913d4e795e36906cc222e4bb6277d2` |
| 8 | `328bdc95-ba94-42ff-9019-47fc8a03b559` | `TREND_REFERENCE_V1` | `393a49502c0d5004f6c8b1342a2b3a566d714cbd09ef1ab57fafbb11f53e9e01` |
| 9 | `ea320dc6-eed3-4a3d-b708-210384577336` | `VALUATION_BID_V1` | `84c4a0fbc50be54b051c9724403951ee2be045db12a381f10cd1cd8aaf4071ab` |
| 10 | `98eabad8-16c0-43c8-aeca-8d4642cb4046` | experiment manifest `3170761e-ded6-41c0-9cb9-554162084171` | `b6546e94fb27ab6414a7eeb99af7347df3a8ee173b92347e7d10dff675e3236e` |

- The owner also approved the H2 stress scenario, which OD-5 intended only as a replay sensitivity. The running experiment's manifest uses H1.
- Every approval matches its seeded definition's hash. §2 lists four of these hashes (`PAPER_PILOT_V1`, `TREND_REFERENCE_V1`, H1 and H2), and all four match.

**Experiment `d779fbf4-e1be-444c-ab55-7b61292eaa87`**
- `FORWARD_PAPER` mode, cost scenario `COST_SCENARIO_HYPOTHETICAL_H1`.
- Code identity `82c361543f7ad920999fe176ccca02984e021e70da17267e1e589fa13bb006c2`. Before activation, the running API and the execution-worker and evaluation-worker images (built from `2f7973a` in the ExecPlan 0017 deployment) all computed this same value.
- Events: owner `CREATED` 09:05:19.58, `MARKED_READY` 09:05:34.18 and `START_REQUESTED` 09:05:55.02 (request 3); SYSTEM `ACTIVATED` 09:09:52.29 for request 3.

**Activation**
- The ExecPlan 0017 session tried to run `tools/pilot-activate.ps1`. Its Claude Code auto-mode classifier refused the command as a production deployment before it ran.
- The owner then ran the tool from the primary checkout, at `main` `784a67d`. It reported all six steps and "Lease held: True; experiment state: RUNNING".
- Backup: `.cache/deployments/pilot-activate-20260930T090919Z/asl.dump`, 151,107,774 bytes, SHA-256 `e61e1e6efcb0c7792895b51dabe92e2b70eb08e4054951671f4ba5e4f7c2b898`.
- Workers: the execution worker (`sha256:5b02dbe1…`) and the evaluation worker (`sha256:6e2d4e6a…`) started at 09:09:50 UTC. Both are healthy with restart policy `unless-stopped`.
- `asl_execution` and `asl_evaluation` now have LOGIN. The tool set the two enable flags in `.env`; the agent did not read that file.

**§12 post-activation checks (VERIFIED).** These were read-only queries, with the owner's approval, at 09:13–09:14 and 10:06 UTC.
- **ACTIVATED event.**
  - w0 481801, equal to the checkpoint jump.
  - NAV 100 with 10000.00000000 cash and equity, 100 units and high-water NAV 100.
  - Daily reference NAV 100, `LATE_CONSERVATIVE`.
  - Evaluation floor `1790755200000` (the 08:00 UTC bar) for both symbols.
  - Startup valuation `c1076d41-d5bc-5f14-9b86-58fb0c418c7d`.
- **W0 checkpoint.** `FORWARD_PAPER` at last sequence 482369 by 09:13:51, with lease epoch 1 valid. There were no strategy evaluations before the first bar closed after activation, so there were no historical evaluations.
- **STARTUP valuation and daily reference.** The startup valuation is at 09:09:52.29, NAV 100, `VALID`. The daily reference for 2026-09-30 is NAV 100, `LATE_CONSERVATIVE`, lateness 32,992,287 ms, source `RUN_ACTIVATION`.
- **Reconciliation.** After the worker's reconciliation at lease acquisition, `paused` and `reconciliation_failed` stayed false, and there was no execution incident from 09:00 on. There was no downtime incident either, because no earlier `FORWARD_PAPER` checkpoint existed. `reconcile()` was not called, because it latches on a mismatch.
- **First snapshot.**
  - `SNAPSHOT` as of 10:00 UTC, created 10:05:24.61, SHA-256 `cff38d2dc8a055d0b9162cbab4062fbbd1fe4d14af0ee8833bfecce041a1a377`.
  - The `HOURLY` valuation at 10:00:00.59 is NAV 100, `VALID`. Evaluation marks: `HOURLY` 2 and `FLOW` 2.
  - The first evaluations (the 09:00 bar) were `NO_SIGNAL` for both symbols. There are no orders.

**Checkpoint (OD-13).** The owner chose 2026-11-25 (8 weeks) in chat. M4-C records that checkpoint report, with its limitations and the next decision.

**Operating notes.**
- **Downtime before activation.** The host rebooted at 07:50 UTC, and Docker Desktop did not start by itself; collection had been down since 04:08 UTC. The ExecPlan 0017 session started Docker Desktop at 08:19 UTC for its deployment, before activation. Protection needs the PC and Docker running (OD-11), so the owner was advised to let Docker Desktop start at sign-in and to prevent sleep.
- **Deployments during the pilot.** They follow OD-12. At 10:11 UTC, ExecPlan 0019 (PR #9, the Approvals-page fix) redeployed only the web container; its session reports no worker restart and no change to the engine's code identity, so no new segment.
- **Market-table dumps.** They are due weekly under OD-14, with `tools/pilot-market-dump.ps1`.

### Correction after activation — which env file the tools write (2026-10-07)

**Found by an independent review on 2026-10-06.** `pilot-activate.ps1` and `pilot-deactivate.ps1` gave the writer of the flags the `-EnvFile` text as the caller typed it, while every Compose call used the resolved path. The writer uses .NET file methods, which take a relative path from the process directory, not from the directory PowerShell stands in.

**Not covered by acceptance, and not met by the activation.** `ActivationRehearsal` gives the tools an absolute path, and the owner's activation above used the default, which is absolute. OBSERVED on 2026-10-07 on the tools as they were at `4ece326`, with a relative path, another process directory and a stand-in for `docker`: the flags in the file given stayed as they were, and a file of the same name in the process directory was created or rewritten; called from a session at its default error preference the tool printed the error and went on to start the workers.

**Change.** The four calls of the writer in the two tools take the resolved path ([decision](../../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out)).

**A second finding of the same day, and its change.** OBSERVED with a read-only temporary env file: called by its path from a session, a tool printed the writer's error and went on, because a tool's `Stop` reaches the functions of `tools/lib/Pilot.psm1` only when the tool is started with `powershell.exe -File`. `pilot-activate.ps1` went on to start the workers, and `pilot-deactivate.ps1` ended with exit code 0 while both flags still read `1`. By the owner's decision the module now sets `Stop` for its own functions, so the tool stops at the flag step in both ways of starting it.

**Evidence.** `tools/env-file-path-check.ps1`, twelve cases on temporary files with a stand-in for `docker`; the results for the tools at `4ece326`, with the path correction alone and with both changes are in [COMMANDS](../COMMANDS.md#owner-tools-write-the-resolved-env-file-2026-10-07).

**What it does not change.** The writer and the reader themselves, whose limits [OPERATIONS](../OPERATIONS_M3_M7.md#m4-pilot-operations-execplan-0015) now states and whose replacement follows the M6 B9 merge by the owner's decision; any schema, image, service or approval; the running pilot. Nothing was deployed, and no command addressed the normal application: the next call of either tool uses the changed files once the pull request is merged into the checkout it is run from.

**Gates affected.** Q05: a write to the wrong file is closed for a relative path, and a failed write stops the tool however it is started. Q07: the check above; `ActivationRehearsal` NOT RUN on the changed tools, because the owner limited this correction to tests on isolated files. Q09 and Q10: the operator text in OPERATIONS. Not affected: Q01, Q02 (no UI), Q03 (no ledger or state transition), Q04 (no authority or secret surface), Q06, Q08.

## 17. Open risks
- **SOL quote freshness.** SOL ticker pauses of 5–6 s exceed the 5 s quote age. Expect deferred entries and short protection gaps (OD-6).
- **Clock uncertainty.** A clock-uncertainty failure still tears down collection, causing quote and protection gaps. Its fix is a separate follow-up.
- **Unfinished upstream work.** Catch-up after long downtime relies on 0014 (`b9b0369`), whose acceptance and deployment are not yet recorded. 0013's performance and secret-scan evidence is also still open.
- **Local downtime.** Protection runs only while the PC and Docker run. PC sleep, power loss or the worker restart policy can leave positions unprotected. Downtime is disclosed, never hidden.
- **Seven-day retention** limits full replay unless OD-14a is chosen.
- **Weak evidence.** Hypothetical costs, idealized baselines, sampled level-1 fidelity and likely short samples may leave results inconclusive. They are not trading evidence.
- **One main experiment per account.** M7 will need to stop or migrate the pilot.
- **Shared-IP REST budget saturation** can age reference checks and fail feeds closed.
- **Report reading.** A FINAL report's run return and run drawdown stop at the last full hourly grid point (§16, finding 2). The stale pause alert on a finished run (finding 1) was fixed by [ExecPlan 0018](0018-ended-run-cause-note.md).
