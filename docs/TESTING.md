# Verification strategy and requirement coverage

## Status and rule

How the spot app is tested now ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12). The milestone evidence maps and run records up to M10's update 1 are in [archive/TESTING.md](archive/TESTING.md), and the sections of M10 to M11 (the futures, the agents, the twins, the scores, the replays, the AI backtests) in the [archived copy](archive/contracts/TESTING.md); the commands are in [COMMANDS](COMMANDS.md).

- **Where tests run.** Every check runs in a cloud session on the change's own tree: the web lint, typecheck, unit tests and production build; Ruff, the OpenAPI drift check and pytest without a database; pytest and the browser suites against a scratch PostgreSQL cluster. Since M8 the owner's PC runs no test harness: it runs only the update file's own checks when the owner double-clicks it ([ExecPlan 0031 §4.8](archive/plans/0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). No multi-hour run on the PC.
- **Isolation.** Database tests run only on a disposable cluster that holds nothing but `asl_m1_` databases, with `ASL_TEST_ISOLATED=1` set; without it the suites refuse their test-only overrides. They never address the normal app, its database, `.env`, `secrets/` or `codex_home`. Scratch password files are random values written for the run. A finished run's databases, clusters, servers and Docker resources are removed by exact name once the evidence is recorded ([DOCKER](DOCKER.md#cleaning-up-disposable-resources)).
- **Fixtures.** Deterministic and labeled: Binance's answers recorded or SYNTHETIC, market values labeled fixtures, a test clock for the engine's steps. Ordinary tests contact no public endpoint and no private exchange endpoint; public connectivity checks are explicit, bounded and separate. Production or forward ledger history is never reset by test setup.
- **Kinds of evidence.** Keep unit/integration/browser tests, provider connectivity checks, synthetic workload probes, simulation evaluation and documentation checks apart in every report. A mocked API test cannot establish real integration or trading profitability.
- **Results.** A check that did not run, or was skipped, is NOT RUN, never a pass. Each update's plan records the commands, their results and what was not run; a failure that `main` already shows is named as such, never hidden.

## Requirement-to-test map

| Requirement | Required evidence |
|---|---|
| P01 Paper-only boundary | No exchange credentials, signed or private routes or adapters; only the market-data hosts; no hidden live setting; the runtime images and configuration inspected |
| P02 Spot scope | Bitcoin spot only, long or cash: another symbol, a short, a borrow or leverage has no code path; the instrument's filters current |
| P03 Funding and top-ups | The starting 10,000 USDT exactly once, decimal validation, idempotent concurrent top-ups, a pending valuation, flows and units atomic, no reseed at start |
| P04 Independent risk | The policy's caps and rounding at their boundaries, the latches across restarts and UTC days, sells never refused by a latch |
| P05 The paper broker | Fills on the stored book with fees and slippage, refusals with their codes, a failed step rolled back whole, the fence refusing a stale epoch, the same inputs giving the same postings |
| P06 Data integrity | Strict parsing, final candles never changed, a book received after the step's time not read, a stale book or unverified clock refusing a trade, no synthetic fallback |
| P07 Code decides | The stored definitions equal to the code; nothing at run time changes the rule, its limits, policy or costs |
| P08 Honest results | Top-ups do not move NAV per unit or reset the high-water NAV; unknown values shown as unknown; the backtest labeled as modeled; the run against holding Bitcoin paired by day |
| P09 Required frontend and preset | The official skills loaded, the preset kept, no duplicate primitive; SSR, hydration, forms, tables, the chart and the stream in a real browser |
| P10 Docker and operations | The update's own checks: backup, forward migration, readiness, recreations, pages; the update file's model test on the PC |

## Financial property tests

After every committed step: each asset's journal balanced, cash and BTC never negative, each effect unique, the projections reconciled to the journal, every value finite. Any valid top-up leaves NAV per unit unchanged at a fixed mark; prices move the result, deposits never do. The high-water NAV and the latches survive deposits, UTC days, restarts and reconstruction. A worker killed between a step's writes and its commit leaves nothing half-done; a stale fenced worker is refused even while it still believes it holds the lease. Random or synthetic inputs are labeled, and are not market evidence.

## Rule and data tests

The rule's reading against independently calculated fixtures: its anchors and their tolerance, the volatility's warm-up and recursion, the target's quantization, the flat band and the buffer. No reading before the day's final candle is stored, one acted-on reading a day, no trade on a stale book. The backtest reads the same rule on the same day as the live account and stamps a trade on the day whose close it traded at. Historical candles never write a missed forward trade.

## Frontend and browser tests

Render the actual preset in a real browser: loading, empty, error and stale states, keyboard and focus, phone and desk widths, long numbers, status cues beyond colour, the chart's text alternative, its mount and unmount, resizing and interval changes. Test the server's request isolation, no duplicate hydration read, query keys against the URL's search, decimal form inputs, the engine's errors, the top-up's confirmation and retries, and the run controls' confirmation and outcomes.

## Continuous integration


The repository has no hosted CI. The owner had it removed on 2026-10-17 ([DECISIONS](DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository)): the GitHub Actions workflow of [ExecPlan 0016](archive/plans/0016-ci-checks.md) never ran on GitHub, and its files were deleted. ExecPlan 0016 keeps the design and names the commit to restore it from.

Until CI is added back, the checks run in the cloud session that changes the code, and a pull request's body records which ran, with their results, and which did not. The owner's PC runs no test suite or harness since M8; it runs the update file's own checks. Wherever a contract asks for executed CI checks, the same checks run in the cloud against the exact release source stand in until CI exists again.

## Since ExecPlan 0060: spot trading only

[ExecPlan 0060](plans/0060-spot-trading-only.md) replaces the engine's suites: the futures, perpetual, agents, research, coins, sources, evaluation, AI backtest, replay and pre-futures spot suites went with their code (153 test files and fixtures), and their sections are in the [archived copy](archive/contracts/TESTING.md). What tests the app now (engine files in `services/engine/tests`, web suites in `apps/web`):

| Requirement ([0060 §6](plans/0060-spot-trading-only.md#6-requirements-and-tests)) | Tests |
|---|---|
| R1 the reading | `test_spot_rule.py` (13): the anchors and their tolerance, the volatility's warm-up and recursion, never short, the quantization, the flat band, the buffer, sell-all at zero |
| R2 the fill | `test_spot_money.py` (19): buys and sells on the stored book with the fee and slippage, lot steps, the minimums and maximums, a thin or missing book, every rounding against the account; dust is what a sale of all of it fails by the sale's own minimum checks, at its fill price |
| R3 the postings | `test_spot_db.py` (34, with R4) and `test_spot_account.py` (28: M1's funding and top-ups on the spot account, the funding at the API's start): balanced per-asset journal, cash and BTC never negative, the account version, reconciliation after buys, sells, a top-up and a restart |
| R4 the step | `test_spot_db.py` on a scratch database with a test clock: the first run by itself, a day spent once, not readable or refused tried again, latches and a paused or stopping run refuse a buy and keep sells, a stopping run sells and stops, Stop and sell, a new run reads the day at once, the fencing refuses a stale epoch; since the review (0060 §13 items 10 to 14): a top-up while BTC is held never reads as a loss and is valued at the next step, a book received after the step's time is not read, a NAV failure under a retired check's name keeps its latch, a reading not readable stores no share or action, the API cannot insert an answered request |
| R5 the backtest | `test_spot_backtest.py` (13): the live reading on the same day, the trade stamped on the day whose close it traded at, the drawdown stop and the daily loss count, the three windows, holding Bitcoin, one stored row per new final day |
| R6 the feed | `test_spot_market_unit.py` (43, recorded and SYNTHETIC payloads, strict parsing, the client's host and weight checks; since 0060 §13 item 16 Binance's real rows of 2018-02-07 to 2018-02-09, the middle one a day the exchange closed early, kept, final after the day's end and noted once) and `test_spot_market_db.py` (6: the second's book, the candles, the daily history in four requests, states and events) |
| R7 the migration | `test_spot_migration.py` (2): an empty database to head and back to `0040`, and a futures-era database: the refusal when not flat, the retired run, every row archived, the definitions, the downgrade's refusal once a spot fill exists |
| R8 the API | `test_spot_api.py` (7) and `test_api.py` (6), the OpenAPI drift check; `test_spot_live_unit.py` (26) and `test_spot_live_db.py` (3) for the live stream |
| R9 the pages | Vitest (20 files, 143 tests; the page tests render the engine's own answers from the browser chain, `src/spot/samples`) and the browser suites below |
| R10 the whole | The whole engine suite on a scratch database (also `test_execution_core.py`, `test_migration_guard.py`, named `test_clean_start.py` until ExecPlan 0061, `test_migrate_unit.py`, `test_m1_unit.py`, `test_database.py`), the web checks and the link check |

**The browser chain** (`tests/spot_browser_fixture.py`): `seed` fills a fresh `asl_m1_<run>_browser` database at head with a daily Bitcoin history since 2017 and a month of minutes, all a SYNTHETIC walk in Binance's answer format (no market value), the starting 10,000 USDT, run #1's buy on today's reading, the owner's Stop and sell, run #2's buy and the backtest; `feed` writes a SYNTHETIC order book while the suites run, beside the real execution worker, the API and the web server. `ASL_SPOT_BROWSER=pages` runs `e2e/spot.spec.ts`, `e2e/local-time.spec.ts` and `e2e/foundation.spec.ts` (only reads, but the Pause test pauses and resumes the run); then `ASL_SPOT_BROWSER=live` runs `e2e/live.spec.ts` on `http://localhost:4318` (a secure context), which stops run #2 with Stop and sell and starts run #3, so it runs once per seeded database. The account suites keep their M1 databases ([COMMANDS](COMMANDS.md)).

VERIFIED on 2026-11-12 in the cloud on the branch of ExecPlan 0060, on a scratch PostgreSQL 16: the whole engine suite `216 passed` on a fresh database (`218 passed` with the daily history's fix, §13 item 16, and without a database `1 failed, 133 passed, 84 skipped`); without a database `1 failed, 131 passed, 84 skipped` (the failure is `test_database.py::test_migrated_database_is_ready`, which needs one; the M10-era baseline's other database-only failure, `test_api.py`'s status test, now skips without a database); the web lint, typecheck, Prettier, Vitest (`143 passed`), build and `api:check`; the browser suites: pages `9 passed`, live `4 passed`, `funding.spec.ts` then the account suites (`request-envelope`, `account-recovery`, `foundation`) `1` and `4 passed` on one database, `funding.spec.ts`, `unknown.spec.ts`, `before-dispatch.spec.ts` and `pending.spec.ts` (with `valuation_valid` false, then true again) each `1 passed` on another, and `foundation-error.spec.ts` with the API stopped `1 passed`; each again after the independent review's fixes, on fresh databases, with the same results. The browser suites found two defects the page tests had not: the Trades and Backtest routes passed an address's unknown value through (TanStack Router keeps a raw search key that the validation leaves out), fixed by naming each key and setting it undefined when refused. The update file's model ran on the owner's PC in Windows PowerShell 5.1 (25 scenarios, 115 expectations, none failed, after a fix to one of its own checks; [0060 §14](plans/0060-spot-trading-only.md#14-progress)). NOT RUN: the Docker build and `docker compose config`, the update, Binance's live answers, and every other check on the owner's PC.

## Since ExecPlan 0061: the clean-up

[ExecPlan 0061 §6](plans/0061-clean-up-after-the-spot-switch.md#6-requirements-and-tests)'s requirements and their tests:

| Requirement | Tests |
|---|---|
| R1 nothing imports what was removed; the engine and the web build | Ruff, `tsc`, ESLint, the production build, the whole engine suite on a scratch database, Vitest |
| R2 `since_start` paired by day on the daily references and the daily candles | `test_spot_db.py::test_the_run_against_holding_bitcoin_is_paired_by_day` (a late first reference left out, two timely days, the ratio to 8 places, the same answer hours later); the OpenAPI drift check and `api:check` |
| R3 the value card's line | `src/cockpit/cockpit.test.tsx`, "sets the run against holding Bitcoin once it has two days, and nothing before"; the browser chain's Cockpit (its seeded runs are younger than two days, so no line), and one inspection in the browser on two SYNTHETIC references ([§14](plans/0061-clean-up-after-the-spot-switch.md#14-progress)) |
| R4 the update file | `tools/m8/update-model.ps1` on the owner's PC (the spot model's scenarios and the quiet time's window in both tools) |
| R5 the documents | `tools/check_links.py`; a search of the current documents for the removed names |

Results on 2026-11-12, in the cloud ([ExecPlan 0061 §14](plans/0061-clean-up-after-the-spot-switch.md#14-progress)): R1, R2, R3 and R5 `VERIFIED` (the engine's `216 passed` on a scratch PostgreSQL, two tests fewer for the removed `--keep-logins` and one more for `since_start`; the web's 144 unit tests and its checks; the browser chain's 22 tests; 0 broken links). R4 `VERIFIED` on the owner's PC on 2026-11-13 (Windows PowerShell 5.1: 14 scenarios, 61 expectations, `"failed":[]`).

## Release evidence

Run lint, type checks, unit/property tests, database integration/concurrency, real-browser tests, production builds and operational recovery appropriate to the milestone. Report exact commands and failures/not-run checks. Security/dependency audits must identify the actual tool/version/date and findings; never claim “secure” based on a passing linter.

Tests may validate arithmetic and operation, but only [TRADING](TRADING.md#how-to-judge-a-trading-change) governs evidence about strategies (since ExecPlan 0060; [EVALUATION](archive/EVALUATION.md) did before it). Neither documentation quality nor coverage percentages establish profitability.

