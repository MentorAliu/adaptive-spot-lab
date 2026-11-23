# Capability and control acceptance checklist

**Status:** the quality gates below apply to every change. The acceptance rows are the spot app's ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12); A04 is verified (M0, 2026-09-26, [run record](archive/plans/0001-foundation.md), [configuration fingerprints](INTEGRATION_EVIDENCE.md#historical-m0-a04-configuration-fingerprints)), and every other row stays unchecked until its whole condition has linked tests, actual command output and a run record. The agent rows (A13 to A38), the M9 and M10 additions and the per-milestone gate records of M2 to M6 are in the [archived copy](archive/contracts/ACCEPTANCE_CHECKLIST.md), history only. This checklist is not a certification, a promise of profit or permission to trade real funds.

## Quality gates for every milestone

Adopted on 2026-09-27 as the owner's production-readiness standard. Assess Q01–Q10 in each milestone plan and completion record; a small scoped change records only the gates it affects. Keep detailed requirements in the linked canonical contracts. Historical milestone evidence remains as recorded; these gates require evidence for the current change and intended release scope.

| ID | Gate | Required outcome and evidence |
|---|---|---|
| Q01 | Complete user experience | Relevant workflows include loading, empty, success, error, stale and unavailable states; navigation, responsive layout, form feedback and retained input are reviewed in the actual browser. Follow [FRONTEND.md](FRONTEND.md) and [SHADCN_WORKFLOW.md](SHADCN_WORKFLOW.md). |
| Q02 | Accessibility | Use [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/) as the shipped UI target. Verify applicable keyboard, focus, labels, accessibility-tree semantics, contrast and responsive behavior with automated browser checks and the implementer's own browser inspection; component choice alone is not conformance evidence. Manual screen-reader review is not required ([owner decision 2026-09-29](DECISIONS.md#2026-09-29--manual-screen-reader-review-retired)), so do not claim screen-reader behavior as verified. Follow [FRONTEND.md](FRONTEND.md#accessibility-and-honest-presentation). |
| Q03 | Business and data correctness | Validate boundaries, transactions, constraints, concurrency, idempotency and state transitions. Financial work proves exact accounting and reconciliation; permission work proves code-enforced boundaries. Use [TESTING.md](TESTING.md) and the applicable A01–A12 rows. |
| Q04 | Security and privacy | Review authorization, Host/CSRF controls, input limits, injection defenses, secrets and log redaction for the changed surface. Map applicable [OWASP ASVS](https://owasp.org/projects/asvs) requirements to evidence under [SECURITY.md](SECURITY.md); record the reference version and any unverified controls. |
| Q05 | Reliable data and failures | Verify appropriate caching/invalidation, retry safety, timeouts, supported cancellation, freshness, disconnection and recovery behavior, including duplicate or unknown mutation outcomes. Follow [FRONTEND.md](FRONTEND.md#server-state-ownership), [DATA_CONTRACTS.md](DATA_CONTRACTS.md) and [OPERATIONS.md](OPERATIONS.md#recovery-sequence). |
| Q06 | Measured performance | Declare relevant workloads, supported hardware/devices and acceptance budgets before measuring affected interactions, queries or jobs. Record results and regressions; use [Core Web Vitals](https://web.dev/articles/vitals) for web experience and [OPERATIONS.md](OPERATIONS.md) for engine/resource bounds. |
| Q07 | Automated verification | Run applicable lint, type, unit/property, integration, browser and production-build checks, in Docker or, from M8, in the cloud on a scratch PostgreSQL; the owner's PC runs only the update's own checks ([ExecPlan 0031 §4.8](archive/plans/0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). Cover real user journeys and failure cases with isolated data; record exact results and missing checks under [TESTING.md](TESTING.md) and [COMMANDS.md](COMMANDS.md). Automate repeatable release checks where supported. |
| Q08 | Operational visibility | Changed services/jobs expose truthful health and failure states, useful structured logs and correlation IDs with redaction. Verify applicable measurements and actionable alerts under [OPERATIONS.md](OPERATIONS.md#monitoring-and-incident-record). |
| Q09 | Deployment and recovery | Verify reproducible builds, validated configuration, migration compatibility and a practical rollback/recovery path. Changes to persistent state include applicable backup and isolated restore evidence. For milestone delivery, the update verifies that the normal local app is running the accepted source and images with its operating controls preserved. Follow [DOCKER.md](DOCKER.md) and [OPERATIONS.md](OPERATIONS.md#milestone-completion-deployment). |
| Q10 | Maintainable engineering | Review module responsibilities, official integration guidance against locked versions, dependency purpose/license obligations, and updated contracts/operator instructions. Follow [LIBRARIES.md](LIBRARIES.md), [INTEGRATION_EVIDENCE.md](INTEGRATION_EVIDENCE.md) and [PLANS.md](PLANS.md). |

For each assessed gate record scope/applicability, the concrete acceptance condition, planned verification, and final result with linked evidence. Use `VERIFIED`, `FAILED`, `NOT RUN`, or `NOT APPLICABLE` with a reason. A deferred or unrun applicable requirement remains open and prevents a readiness claim for that scope; it is not `NOT APPLICABLE`. Scale verification to the changed behavior and preserve milestone boundaries rather than activating future capabilities to satisfy unrelated gates.

Before a production-readiness claim, review these gates across the complete intended release and its applicable A01–A12 outcomes. Record unresolved findings and the supported operating environment. Passing one milestone, installing libraries, or writing these requirements does not establish full application readiness.

## The spot app's acceptance rows

| Status / ID | Requirements ([TESTING](TESTING.md#requirement-to-test-map)) | Observable acceptance condition |
|---|---|---|
| [ ] A01 | P01, P02 | Only Binance's public market data and paper fills of BTCUSDT spot, long or cash; a private or live request, another symbol, a short, a borrow or leverage has no code path and no financial effect |
| [ ] A02 | P03, P08 | 10,000 USDT contributed exactly once; owner-confirmed top-ups keep NAV per unit and cannot reset the result, the high-water NAV or a latch |
| [ ] A03 | P10 | Docker build, start and update work on the owner's PC; the services persist and recover without host runtimes or a mounted Docker socket |
| [x] A04 | P09 | The preset `b2fms61Bqi`, template `start`, pointer behaviour and required libraries are verified; UI tasks load the official shadcn skill and reuse the available primitives |
| [ ] A05 | P09 | Query SSR isolation, Table, RHF and Zod, Lightweight Charts' lifecycle and attribution, lint and browser behaviour pass installed-version checks |
| [ ] A06 | P06 | The feed's provenance, receipt times, gaps and staleness, and real against synthetic data, stay visible and tested |
| [ ] A07 | P05 | The journal, the cash, the BTC holding, fills and fees reconcile under concurrent steps, retries and a forced restart |
| [ ] A08 | P04 | The policy's limits and latches are enforced by code against the current account, through top-ups and restarts; a loss limit is never shown as a guaranteed maximum loss |
| [ ] A09 | P07 | The rule, its policy and costs are versioned and hashed; a new version ends the old run first and rewrites no record |
| [ ] A10 | P08 | The backtest and the forward run are measured with costs, without cherry-picking, and reported as modeled; negative results stay visible |
| [ ] A11 | P10, P08 | The run's state, controls, downtime and refused trades are shown accurately; a restore and the live stream's resynchronisation work |
| [ ] A12 | P01, P06 | Malformed provider answers, a redirect or non-public address, and data gaps never become invented prices, fills or backdated events |

## Evidence record per item

Record the commit, the test and run ids, each command and its actual result, the data's mode (real, recorded or SYNTHETIC), the environment and versions, the definitions' hashes, the failures observed and the checks not run. Report the software's acceptance and the trading evidence separately ([TRADING](TRADING.md)).
