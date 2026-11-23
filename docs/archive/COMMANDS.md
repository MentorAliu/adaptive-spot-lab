# Command contract


## Removed by ExecPlan 0060 — 2026-11-12

The commands of the code ExecPlan 0060 removed (the agents' runner, the futures app's browser suites and the samples, reports and install checks of ExecPlans 0041 to 0059), moved from the [command contract](../COMMANDS.md) verbatim, one heading level down, their links rebased.

### Engine on a scratch PostgreSQL (cloud): the observations and baseline until ExecPlan 0060

The cluster's notes that named the futures', agents' and research suites, as [COMMANDS](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud) held them on 2026-11-12, with the scratch secrets the engine then read: `/run/secrets/postgres_password`, `api_db_password`, `market_worker_password`, `execution_db_password`, `evaluation_db_password`, `agent_db_password`, `source_db_password`; and the pytest baseline without a database: `2 failed`, `test_api.py::test_status_requires_service_identity_and_ready_database` and `test_database.py::test_migrated_database_is_ready`, every error a database case (`2 failed, 883 passed, 349 skipped, 389 errors` on 2026-10-21).

OBSERVED on 2026-10-31 ([ExecPlan 0048 §14](plans/0048-the-cockpit.md#14-progress)): the cluster's directory must be one the `postgres` user can reach (`/var/tmp/<dir>`; one under the session's scratchpad in `/tmp/claude-0` is refused). On a fresh database at `main`'s `793abdd`, `tests/test_m11_scores_db.py` has three failures (`test_a_twin_entry_is_scored_as_an_entry_of_its_side_with_its_candidate`, `test_the_decisions_page_shows_each_checkpoint_and_the_scorecard_adds_them_up`, `test_only_the_agent_identity_stores_a_score_that_describes_its_stored_subject`), the same on that tree and on 0048's.

OBSERVED on 2026-11-03 ([ExecPlan 0054 §14](plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md#14-progress)): run one database suite per cluster at a time. The roles belong to the cluster, not to a database, and the fixtures switch the identities' login on and off, so a run on another database of the same cluster makes tests of the first run fail. In one whole run so disturbed, `test_m11_twins_db.py`'s downgrade test failed after its first downgrade and left the database at `0023_twins` (it brings back the head only at its end), and every later suite that needs a newer table failed: the M5, M6 and M7 agent suites among them. A second cluster on another port (`initdb` and `pg_ctl` as above, with `-p 55453`) runs a parallel check safely.

OBSERVED on 2026-11-05 ([ExecPlan 0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)): in the cloud container, `tests/test_m2_stream_continuity.py::test_back_to_back_rotations_under_load_keep_the_fence` fails run alone, on `main`'s `fb3f191` as on that branch (a timeout waiting for a rotation under load); earlier whole runs passed it. A whole run with a database suite running on another database of the same cluster again failed a test on a role's login (`test_m7_agents.py`'s probe-decision test, which passes alone), as the paragraph above warns.

OBSERVED on 2026-10-23 ([ExecPlan 0038 §12](plans/0038-faster-market-data-cleanup.md#12-progress)), in a runner without the cloud's files: the suites also read `owner_setup_key`, `api_internal_key`, `agent_runner_key`, `research_bridge_db_password` and `research_db_password` from `/run/secrets` (scratch values; the last OBSERVED on 2026-10-23, [ExecPlan 0039 §15](plans/0039-bitcoin-futures-on-paper.md#15-progress), where its absence made 198 tests error), and the agent definitions read their prompts from `services/agent-runner/prompts` beside `services/engine`; without them about 200 tests fail on a missing file. Since [ExecPlan 0042](plans/0042-no-owner-sign-in.md) no suite reads `owner_setup_key`.

The agent and research suites need the `asl_m1_m6_` prefix; the M1 to M4 suites take any `asl_m1_` name. A migration's own check is `alembic upgrade head`, `alembic downgrade -1`, `alembic upgrade head` on a fresh database, then a refused downgrade once a record of the new kind exists.

Known baseline on this cluster (2026-10-21, [ExecPlan 0035](plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress)): `3 failed, 1547 passed, 74 errors`. The 74 errors are `test_m1_account.py`'s 13 and the research store's 61 (they need the research cluster and its secrets). Two failures are `main`'s: `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`, and `test_api.py::test_status_requires_service_identity_and_ready_database` on a database no earlier test emptied. The third, `test_m2_retention_faults.py::test_a_failed_start_up_retention_does_not_keep_the_stream_from_starting`, timed out once under load and passed alone (`6 passed`). Since ExecPlan 0035, `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research` passes; on M10 update 2's tree it fails, missing the scheduled research the plan removed. `test_m3_throughput.py`'s replay batch failed on 2026-10-20 and passed on 2026-10-21. OBSERVED on 2026-10-25 ([ExecPlan 0042 §13](plans/0042-no-owner-sign-in.md#13-progress)): the `test_api.py` status test fails on `main` at `92c7b7e` on a freshly migrated database too (`decisions` reads `inactive`), and the `test_m6_schema.py` downgrade fails only while other databases on the cluster hold objects of `asl_research`, whose role it drops; it passes on a cluster that holds its database alone. OBSERVED on 2026-10-25 ([ExecPlan 0040 §14](plans/0040-trade-reviews-and-a-coach.md#14-progress)): in a full run that downgrade also fails on five `MOCK_` source versions (`PROPOSED`) that the M6 suites before it leave in `agent_definitions`, which `0008`'s kind check refuses; and on the cloud machine `test_m2_stream_continuity.py::test_back_to_back_rotations_under_load_keep_the_fence` fails with `QUEUE_OVERLOAD`, with the M2 files alone too. OBSERVED on 2026-11-03 ([ExecPlan 0053 §14](plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress)): in one whole run, `test_m2_reference_checks.py::test_failed_clock_request_keeps_the_collection_and_fails_closed[rate-limit]` failed under load and passed alone; and `test_backtest_lane_db.py`'s scheduler test fails when it starts between HH:58:30 and HH:00:00 UTC, its test clock 8 minutes ahead of the database's (#172 fixes the test).

### Agent runner (cloud)

From `services/agent-runner`, with the system Python 3.13 and no package (standard library only). OBSERVED on 2026-10-23 ([ExecPlan 0039 §15](plans/0039-bitcoin-futures-on-paper.md#15-progress)): `Ran 20 tests`, 17 pass. The other three are the image's own (`/opt/runner` paths, no shell, an unprivileged user) and fail outside it; they run in the image.

```bash
PYTHONPATH=testing:. python3 -m unittest tests.test_units
```

ExecPlan 0049's providers (the four adapters against fake CLIs and fake vendor servers, the credential store, the gateway's ports, the Codex app server's windows), standard library only. OBSERVED on 2026-10-31: `Ran 28 tests … OK`; `tests.test_units` then `Ran 21 tests`, 19 pass and the two image tests fail outside the image. OBSERVED on 2026-11-05 ([ExecPlan 0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)): `Ran 32 tests … OK`, and `tests.test_units` as before:

```bash
PYTHONPATH=testing:. python3 -m unittest tests.test_providers
```

Ruff, from `services/engine` so that it takes the engine's `pyproject.toml` (the runner has no settings of its own; run from `services/agent-runner` it falls back to other settings and reports findings the project does not check). VERIFIED 2026-10-23:

```bash
.venv/bin/ruff check --no-cache ../agent-runner   # "All checks passed!"
```

### Browser suites (cloud), until ExecPlan 0060

Each suite on a freshly migrated and seeded database, with the API and the built web server on the same tree. VERIFIED (2026-10-21, M10 update 2):

```bash
# services/engine: seed, then serve the API as the api role
ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m10_browser_fixture seed    # or tests.m7_browser_fixture
ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_<run>_browser ASL_DB_ROLE=api \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
# apps/web: the production build, then the suite
NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs
ASL_M10_BROWSER=coins ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/m10.spec.ts --workers 1
```

The Coins suite needs `ASL_TEST_ISOLATED=1` in the API's environment. The scratch configuration is a copy of `playwright.config.ts` that names the preinstalled Chromium (`/opt/pw-browsers/chromium`), saved as `.mjs` under `apps/web/node_modules/.scratch/`: Node does not strip types from a `.ts` file under `node_modules`. The records reach the web server as `http://web:4318`, with `web` mapped to 127.0.0.1 in `/etc/hosts` (restored after) and added to `NO_PROXY`.

Since [ExecPlan 0035](plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress) the decision pages and the five pages run as one suite on `tests.m7_browser_fixture seed`, the API with `env -u ASL_TEST_ISOLATED` and Playwright with `ASL_TEST_ISOLATED=1` (the specs check it with the database name):

```bash
ASL_M7_BROWSER=decisions ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts e2e/pages.spec.ts e2e/local-time.spec.ts \
    --grep "@decisions|@pages|@local-time" --workers 1
# then on the same database: python -m tests.m7_browser_fixture new-runner, and
ASL_M7_BROWSER=profile ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @profile --workers 1
```

Since [ExecPlan 0037](plans/0037-clear-values-in-local-time.md#12-progress) (VERIFIED on 2026-10-22) the run adds `e2e/local-time.spec.ts` (`@local-time`), which sets the browser's zone to `Europe/Budapest` itself; `playwright.config.ts` sets every other suite's browser to UTC (`timezoneId: "UTC"`), and the scratch configuration copies that setting.

The other suites of that record, each on a fresh database with `ASL_TEST_ISOLATED=1` for Playwright:

- M5 (`ASL_M5_BROWSER=agents`, `e2e/m5.spec.ts`) on `asl_m1_browser_m5_<run>`, seeded by `python -m app.agents.acceptance agent-browser-fixture`; the workflow ID it prints goes in `ASL_M5_WORKFLOW`. Seed it outside HH:59:30 to HH:06:00 UTC: the fixture's orchestrator keeps the agents' quiet window, and inside it the workflow stays `QUEUED` and the fixture exits 1 (OBSERVED 2026-10-21 on `main` at `3dd5011` and on ExecPlan 0035's branch).
- M3 (`ASL_M3_BROWSER=inactive`, then `populated` after `python -m app.execution.browser_fixture`; `e2e/execution.spec.ts`) on `asl_m1_browser_m3_<run>`. The inactive phase expects the cluster's `asl_execution` role without login: on a cluster where an earlier run gave it one, `ALTER ROLE asl_execution NOLOGIN` first.
- M7 `@unavailable` on a database migrated only to `0008_m6_research`, the API isolated.
- `e2e/funding.spec.ts`, then with `PLAYWRIGHT_ACCOUNT_FIXTURE=1` the account suites (`request-envelope`, `account-recovery`, `foundation`), on `asl_m1_browser_<run>`, the API isolated. `ssr-isolation`, `logout-recovery` and `native-access` tested the sign-in and went with it ([ExecPlan 0042](plans/0042-no-owner-sign-in.md)); since then `funding.spec.ts` checks the account the API funded at its start, so it runs first on its database.
- With the API stopped: `ASL_M7_BROWSER=error` (`e2e/m7.spec.ts --grep @error`), `ASL_M4_BROWSER=error` (`e2e/m4.spec.ts`), `ASL_M5_BROWSER=error` (`e2e/m5.spec.ts`), `ASL_M3_BROWSER=error` (`e2e/execution.spec.ts`) and, since [ExecPlan 0036](plans/0036-a-clear-beautiful-app.md#12-progress), `PLAYWRIGHT_EXPECT_ERROR=1` (`e2e/foundation-error.spec.ts`). Each runs on a database named for its suite (`asl_m1_browser_m4_<run>`, `asl_m1_browser_m5_<run>`, `asl_m1_browser_m3_<run>`, and an `asl_m1_m6_<run>_browser` for M7): on another name the suite skips, which reports no failure (OBSERVED on 2026-10-25, [ExecPlan 0042 §13](plans/0042-no-owner-sign-in.md#13-progress)).

Since ExecPlan 0036 also, VERIFIED on 2026-10-22, the API isolated:

- M2's market pages on `asl_m1_browser_m2_<run>`: `ASL_M2_MARKET_EMPTY=1` (`e2e/markets-empty.spec.ts`) on a fresh database of its own, as it creates its own owner. On another fresh one, `e2e/funding.spec.ts`, then the synthetic feed in the background (`ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_browser_m2_<run> .venv/bin/python -m app.market_data.fixture_worker` in `services/engine`), then `ASL_M2_MARKET_STATE=live` (`e2e/markets.spec.ts`), `ASL_M2_COMPLETION=1` (`markets-freshness`, `markets-health-states`, `markets-races`, `markets-accessibility`) and `ASL_M2_MARKET_ERROR=1` (`markets-error`). Stop the feed's own Python process with SIGTERM (it releases its lease; a signal to a wrapper shell leaves it running), wait more than the quote's 5-second age limit, run `ASL_M2_MARKET_STATE=outage`, start the feed again and run `ASL_M2_MARKET_STATE=recovered`.
- M1's funding outcome suites on one fresh `asl_m1_browser_<run>`, after `e2e/funding.spec.ts` and nothing else, in this order: `PLAYWRIGHT_UNKNOWN_FIXTURE=1` with `e2e/unknown.spec.ts` (it expects 12,233 virtual USDT), then with `e2e/before-dispatch.spec.ts` (12,277); then `UPDATE account_state SET valuation_valid = false` on that database, `PLAYWRIGHT_PENDING_FIXTURE=1` with `e2e/pending.spec.ts`, and `valuation_valid` set back to true.

Since [ExecPlan 0039](plans/0039-bitcoin-futures-on-paper.md#15-progress) part A, VERIFIED on 2026-10-24, the futures card on Markets, on a fresh database seeded by `tests.m7_browser_fixture seed`, with the futures feed writing into it from a SYNTHETIC stand-in for Binance (a deterministic random walk; nothing is a market value):

```bash
# services/engine, in the background: the real feed as the market worker; stop its own process with SIGTERM
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m11_browser_fixture feed
# the API as above (env -u ASL_TEST_ISOLATED), the web server as above, then from apps/web
ASL_M11_BROWSER=futures ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/perp.spec.ts --workers 1
```

`ASL_M11_SCREENSHOTS=<dir>` also saves the card at 1m and 15m. The suite waits for the feed to say `Connected` (`CONNECTED` before [ExecPlan 0048 part 3](plans/0048-the-cockpit.md#413-markets-part-3)) and for the mark to change, so start it once the feed has run for about ten seconds.

Since part B, VERIFIED on 2026-10-24, the five futures pages, the toast when a trade closes and the owner's Pause, on a fresh database migrated to the head and seeded by `tests.m11_browser_fixture seed` (the owner, the agents' switch on, the 10,000 USDT account, run #1 with three SYNTHETIC trades and six decisions), with the feed writing a SYNTHETIC walk into it. Seed before the feed starts; no engine or agent worker runs, except that the toast test runs the fixture's `close` (one engine step that closes the open position) itself:

```bash
# services/engine
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m11_browser_fixture seed
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m11_browser_fixture feed   # background
# the API with ASL_AGENTS_OFFLINE_TEST=1 and the web server as above, then from apps/web
ASL_M11_BROWSER=pages ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/local-time.spec.ts e2e/pages.spec.ts --workers 1
```

Result: `12 passed` (`local-time.spec.ts` 2, `pages.spec.ts` 10). Retired since part B, skipped and so NOT RUN: `markets*.spec.ts`, `m10.spec.ts`, the `inactive` and `populated` phases of `execution.spec.ts` and the pilot test of `m4.spec.ts`; update 3 removes them with the spot code.

Since [ExecPlan 0040](plans/0040-trade-reviews-and-a-coach.md#14-progress) part 1, VERIFIED on 2026-10-25 on ExecPlan 0042's tree: each trade's review and the coach's note, on the same seeded database, with the feed, the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the web server as above, before `pages.spec.ts`. The suite runs the fixture's `reviews` command itself, once, from `services/engine` with its own environment: the real orchestrator, answered by a SYNTHETIC scripted model, reviews the two closed trades (one review recorded, one refused twice) and writes the coach's note:

```bash
# from apps/web, after seed and with the feed running
ASL_M11_BROWSER=reviews ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/reviews.spec.ts --workers 1
# then local-time.spec.ts and pages.spec.ts on the same database, as above
```

Result: `5 passed`, then `12 passed` for `local-time.spec.ts` and `pages.spec.ts`. The fixture's command, run by the suite, inherits Playwright's environment, so `ASL_DB_HOST` and `PGPORT` are exported in that shell too. It runs once per seeded database: to run the suite again, seed a fresh one.

Since [ExecPlan 0041](plans/0041-twins-and-a-veto.md#14-progress) part 1, VERIFIED on 2026-10-25: the league table, a twin's trades and the twins' health, on the same seeded database (the seed starts the twin set at run #1's first step and steps it beside the trader), after `reviews.spec.ts`, `local-time.spec.ts` and `pages.spec.ts`:

```bash
# from apps/web, on the same database and servers
ASL_M11_BROWSER=pages ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/twins.spec.ts --workers 1
```

Result: `3 passed` (18:04 UTC), and after the review's fixes `5 passed` for `reviews.spec.ts`, then `15 passed` for `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` together (18:45 UTC, on a fresh seeded database). OBSERVED the same day: on a database seeded at 18:39:50 UTC the fixture's stop tightening was refused (`NOT_TIGHTER`: the SYNTHETIC walk, set by the clock, fell more than one ATR in its five minutes) and `pages.spec.ts`'s Decisions test failed on it; seeded again at 18:44 UTC it was applied and the suite passed. The fixture's trader rows depend on the minute it is seeded. The web's samples of the twins' reads (`apps/web/src/futures/samples/twins-*.json`) are the engine's own answers on SYNTHETIC rows, written on purpose (the suite does not collect the file) by `ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_twin_samples.py` in `services/engine`.

Since [ExecPlan 0043](plans/0043-score-every-decision.md#14-progress) update 1, VERIFIED on 2026-10-26: what followed each decision, on the same seeded database and servers, after `twins.spec.ts`. The suite runs the fixture's `scores` command itself, from `services/engine` with Playwright's environment: the real scorer, as the agent identity, stores every checkpoint that is over, until a pass stores nothing. The reviews suite's scheduler passes run the scorer too, so the command may store no new row; it prints how many scores the database holds, and the suite expects more than none:

```bash
# from apps/web, on the same database and servers, with ASL_DB_HOST and PGPORT exported
ASL_M11_BROWSER=scores ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/scores.spec.ts --workers 1
```

The fixture dates its trader's decisions and the coach's workflows at their own seconds, so the scores read each decision at its time. The web's samples of the scores (`apps/web/src/futures/samples/scores-*.json`) are the engine's own answers on SYNTHETIC rows, written on purpose by `ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_score_samples.py` in `services/engine` (the suite does not collect the file).

Since [ExecPlan 0043](plans/0043-score-every-decision.md#14-progress) update 2, VERIFIED on 2026-10-26: the same command, `4 passed`; the fourth test checks a generation-9 decision's forecast and code's verdict on Decisions, Home's forecast counts and the day's review card on Decisions (its empty or waiting state on the fixture: the populated card depends on the time of day the database is seeded, so it is covered by the component tests). The fixture's short is now generation 9's, with a forecast, and its `reviews` command answers a decision review too when it is seeded between 01:30 and about 02:30 UTC. The decision review samples (`apps/web/src/futures/samples/decision-review-*.json`) are the engine's own answers on SYNTHETIC rows, written on purpose by `ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_decision_review_samples.py` in `services/engine`; the scores samples were written again by `tests/m11_score_samples.py` (their decisions now carry `expected_move` and `call`, and the scorecard `direction`), and ExecPlan 0040's review samples (`review-*.json`, which have no writer) gained the new fields as the engine answers them for generation 8's records: null. After the independent review's fixes the decision review samples were written again the same way (a cited scorecard row now carries its counts per window), and `review-coach.json` gained `"windows": null` on each cited item by hand.

Since [ExecPlan 0045](plans/0045-where-the-results-come-from.md#14-progress), VERIFIED on 2026-10-27: where the results come from, on the same seeded database and servers, after `scores.spec.ts`. The suite runs the fixture's `checks` command itself, from `services/engine` with Playwright's environment: the bar outcomes' pass and the day's four checks as the agent identity. The reviews suite's scheduler passes run the same stages, so today's result may already be stored (`DONE_TODAY`); the command accepts either. Run it after 00:20 UTC:

```bash
# from apps/web, on the same database and servers, with ASL_DB_HOST and PGPORT exported
ASL_M11_BROWSER=checks ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/checks.spec.ts --workers 1
```

Result: `3 passed`, after `5 passed` (`reviews.spec.ts`), `15 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`) and `4 passed` (`scores.spec.ts`) on the same fresh database. The check samples (`apps/web/src/futures/samples/checks.json`, and the trades' costs in `review-trades.json` and `review-trade.json`) are the engine's own answers on SYNTHETIC rows, written on purpose by `ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_check_samples.py` in `services/engine` (the suite does not collect the file); the review samples now have that writer. `tests/m11_twin_samples.py` wrote `twins-trades.json` again for its costs (its league sample, which changed only with the run's clock, was kept).

Since the agents' models in Settings ([DECISIONS](../DECISIONS.md#2026-10-28--the-agents-models-on-settings)), VERIFIED on 2026-10-28: `ASL_M11_BROWSER=pages` with `e2e/local-time.spec.ts` and `e2e/pages.spec.ts` on a freshly seeded database, `12 passed`; the Settings test checks the Models section. Then the whole chain above on another fresh one: `5 passed` (`reviews.spec.ts`), `15 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`). The database name must match `asl_m1_m6_<run>_browser`, or every test skips. The web's sample of the new read (`apps/web/src/agents/samples/models.json`) is the engine's own answer on SYNTHETIC rows, written on purpose by `ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/agent_model_samples.py` in `services/engine` (the suite does not collect the file).

Since [ExecPlan 0047](plans/0047-live-trades-and-pop-ups.md#14-progress), VERIFIED on 2026-10-30: the live trades, on a fresh database seeded by `tests.m11_browser_fixture flat` (the owner, the agents' switch on, the 10,000 USDT account and run #1 started, no trade yet), with the feed writing into it and the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the web server as above. The suite runs the fixture's `open` (the trader's long in one engine step, announced as the worker announces) and then its `close`, so it runs once per seeded database. It needs a secure context, as the PC's `http://localhost:3000` is: Web Locks and notifications exist only there, and at `http://web:4318` each tab opens its own stream.

```bash
# services/engine
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m11_browser_fixture flat
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser .venv/bin/python -m tests.m11_browser_fixture feed   # background
# the API and the web server as above, then from apps/web, with ASL_DB_HOST and PGPORT exported
PLAYWRIGHT_BASE_URL=http://localhost:4318 ASL_M11_BROWSER=live ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_<run>_browser \
    pnpm exec playwright test -c <scratch config> e2e/live.spec.ts --workers 1
```

Since 0047 the toast test of `pages.spec.ts` is served by the same stream.

Since [ExecPlan 0048](plans/0048-the-cockpit.md#14-progress), VERIFIED on 2026-10-31: the same chain without `reviews.spec.ts`, at `PLAYWRIGHT_BASE_URL=http://localhost:4318` for every suite, on a database seeded at 08:21 UTC with the feed, the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the web server as above: `15 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`); and `live.spec.ts` on a database seeded by `flat`, `4 passed`. OBSERVED the same morning, two limits of the fixture's clock:
- `reviews.spec.ts` failed at the fixture's `reviews` command ("the reviews are not as planned") on a database seeded at 07:46 UTC: `seed`'s run began the day before (23:50 UTC), the decision reviewer answered for that day, and the coach wrote its one note after the decision review instead of the trade review the command expects. By `seed`'s code (inferred, not run at each hour), its run begins the day before whenever it is seeded before 10:30 UTC (its first entry is 10 minutes before the last 8-hour boundary at least 2.5 hours old), so seed it after 10:30 UTC.
- Since [ExecPlan 0048 part 2](plans/0048-the-cockpit.md#14-progress), VERIFIED on 2026-10-31: the whole chain with `reviews.spec.ts` first, on a database seeded at 10:31 UTC: `5 passed`, `15 passed`, `4 passed`, and `checks.spec.ts` `3 passed` after its costs test was changed to open the trade by its address (a click before a script's `focus()` leaves the tooltip closed: it opens on keyboard focus only); `live.spec.ts` on a `flat` database, `4 passed`. A chain script that waits until 10:31 UTC before it seeds avoids the first limit above.
- Since [ExecPlan 0048 part 3](plans/0048-the-cockpit.md#14-progress), VERIFIED on 2026-10-31: the chain on a database seeded at 11:35:54 UTC (`5`, `15`, `4` and `3 passed`), `live.spec.ts` (`4 passed`), `perp.spec.ts` (`2 passed`), the funding and account suites, `m7.spec.ts @profile`, `m5.spec.ts`'s agents phase and the error phases with the API stopped, each on its own fresh database as above. Settings' agents are rows now: a spec picks a row by its exact title (`filter({ has: page.getByText(title, { exact: true }) })`), since a row's line may name another row, and a filter's inner locator starts from `page`, as it is queried inside each row.
- Run the chain at once after the seed. On a database whose `pages.spec.ts` ran 15 minutes after the seed, the SYNTHETIC walk reached the open long's tightened stop first, so the toast test's exit was refused (`POSITION_CHANGED`; the toast came from the stop) and `scores.spec.ts` found two refused decisions where it expects one.
- OBSERVED on 2026-11-03 ([ExecPlan 0053 §14](plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress)): the same on a chain run at once after a seed at 13:24:19 UTC. The walk's low (59,836.23) went under the tightened stop (59,872.0) before the toast test's exit, and `scores.spec.ts` failed on the two refused decisions. Seeded again at 13:36:06 UTC, the chain passed. The walk is a function of the minute (`walk` in `tests/m11_browser_fixture.py`), so the gap between the stop, about one ATR under the walk five minutes after the long's entry, and the walk's low up to the exit can be computed for a seed minute before seeding.

### ExecPlan 0049: the provider samples

The web's provider samples (`apps/web/src/agents/samples/providers-*.json` and `usage-*.json`) are the engine's own answers on SYNTHETIC records, written on purpose when the reads change (the suite does not collect the file). OBSERVED on 2026-10-31, `1 passed`, from `services/engine` on an isolated database:

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/agent_provider_samples.py
```

### ExecPlan 0041 part 2: the twin and scorecard samples

The web's samples of the twins' reads (`apps/web/src/futures/samples/twins-*.json`; `twins-vetoes.json` and `twins-veto-trades.json` are new) and of the scorecard (`scores-scorecard.json`) are the engine's own answers on SYNTHETIC rows, written on purpose when the reads change (the suite does not collect the files). VERIFIED on 2026-11-02 at 12:29 UTC, `1 passed` and `2 passed`, from `services/engine` on an isolated database migrated to `0030_veto_twins`:

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_twin_samples.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_score_samples.py
```

`m11_score_samples.py` also writes `scores-decisions.json`; when only its ids change it is kept as it was. The scorecard sample is read at a fixed instant ([ExecPlan 0041 §13](plans/0041-twins-and-a-veto.md#13-decision-log)), so it is the same on any day; the league sample changes with the run's clock and the set's hash.

The browser chain of [Browser suites](../COMMANDS.md#browser-suites-cloud), VERIFIED on 2026-11-02 on a database seeded at 12:38:33 UTC: `5 passed` (`reviews.spec.ts`), `16 passed` (`local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts`, now with the Veto tab by keyboard and by its address), `4 passed` (`scores.spec.ts`, with the Scorecard's longer rows) and `3 passed` (`checks.spec.ts`). OBSERVED the same day, three things the chain needed after [ExecPlan 0049](plans/0049-choose-the-agents-provider-and-see-usage.md), whose browser suites were not run:

- The fixture's `seed` stopped with `TypeError: Held.tick() takes 1 positional argument but 3 were given`: since 0049 the agent worker passes its in-force step the runtime's status and the provider, and the fixture's stand-in (`tests/m7_browser_fixture.py`) now takes them. `main` at `31cf9bd` has the same fixture and worker, so no fixture-seeded browser suite starts there.
- `pages.spec.ts`'s Settings test listed six sections; Settings has had seven since 0049 (Provider after Agents).
- Base UI's progress bar puts a visually hidden `x` in its own text, so a test reads a bar by its name, its `aria-valuetext` and the value it shows, not by its card's text.

Two scratch clusters in one session (ports 55452 and 55453, each set up as in [Engine on a scratch PostgreSQL](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)) let the full suite run on one while the other suites and the browser chain run on the other: no two suites share a cluster, whose roles they share.

### ExecPlan 0050: the replay's report and tests

The replay's suites, from `services/engine` on the scratch cluster ([above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). OBSERVED on 2026-11-03 ([0050 §14](plans/0050-replay-past-decisions-offline.md#14-progress)): `18 passed` without a database, `6 passed` on an isolated database:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_replay_unit.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_replay_db.py
.venv/bin/python -m app.agents.definitions_v13   # the seed lines migration 0031 freezes
```

The report on the owner's PC, read-only, as the API identity in the API's container, run by the thread on the owner's word (OBSERVED on 2026-11-03 at 11:16 UTC on the installed `0031`: exit 0, "REPLAY_SET_V1: 410 contexts, 920 items."; on a database before `0031` it prints `{"state": "SCHEMA_PENDING"}` and exits 1):

```bash
docker compose exec -T api python -m app.agents.replay_report
```

### ExecPlan 0052: the AI backtest's tests and progress

The backtest's suites, from `services/engine` on the scratch cluster ([above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). OBSERVED on 2026-11-03 ([0052 §14](plans/0052-backtest-the-ai-trader-on-history.md#14-progress)): the pure and lane unit suites pass without a database, the lane's database suite `6 passed` on an isolated database (it starts the real child process on the shipped archive):

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest_ai.py tests/test_backtest_ai_report.py tests/test_backtest_lane_unit.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest_lane_db.py
.venv/bin/python -m app.agents.definitions_v15   # the seed lines migration 0032 freezes
```

Generation 16 ([0052 §15](plans/0052-backtest-the-ai-trader-on-history.md#15-generation-16-the-backtest-up-to-80-of-the-week-2026-11-04)), the same way; OBSERVED on 2026-11-04 in §14:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest_allowance.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest_allowance_db.py tests/test_backtest_lane_db.py
.venv/bin/python -m app.agents.definitions_v16   # the seed lines migration 0035 freezes
```

Generation 17, the Claude run ([ExecPlan 0055](plans/0055-backtest-claude-on-the-same-history.md)), the same way; OBSERVED on 2026-11-05 in [0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress) (the database suite starts the real child process for each run):

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_claude_backtest.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_claude_backtest_db.py tests/test_backtest_allowance_db.py tests/test_backtest_lane_db.py
.venv/bin/python -m app.agents.definitions_v17   # the seed lines migration 0036 freezes
```

Generation 18, the latest design's run ([ExecPlan 0056](plans/0056-backtest-the-traders-latest-design.md)), the same way; OBSERVED on 2026-11-07 in [0056 §13](plans/0056-backtest-the-traders-latest-design.md#13-progress). `tests/test_backtest_latest_db.py` is the field check (E1 to E3): it runs ten of the live suites' database scenarios again with every pure part and live read watched, so it needs the live suites' fixtures and a database of its own:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_latest_backtest.py tests/test_backtest_latest.py
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest_latest_window.py   # the whole shipped window through the mask, about two minutes
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_latest_backtest_db.py tests/test_backtest_latest_db.py tests/test_claude_backtest_db.py tests/test_backtest_allowance_db.py tests/test_backtest_lane_db.py
.venv/bin/python -m app.agents.definitions_v18   # the seed lines migration 0037 freezes
```

The progress on the owner's PC, read-only (OBSERVED in use from 2026-11-04 09:20 UTC, then with the first and newest call in place of `queued_today`, and the calls and tokens by purpose and template; the thread runs it from the app's folder in Git Bash). The workflows count both generations' templates (`BACKTEST_*_V1` and `_V2`), which share the purpose. Since generation 17 the purpose also holds the Claude run's templates (`BACKTEST_CLAUDE_*_V1`), so the steps and the workflows are counted by run (PROPOSED: not yet run against an installed `0036`). Every statement runs in a read-only session:

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl <<'SQL'
SELECT state, code, detail, pairs, created_at, ended_at, summary FROM backtest_runs;
SELECT s.run_id, s.kind, count(*) AS steps, count(a.step_id) FILTER (WHERE a.outcome = 'ANSWERED') AS answered,
       count(a.step_id) FILTER (WHERE a.outcome = 'ABSTAINED') AS abstained,
       count(a.step_id) FILTER (WHERE a.outcome = 'UNANSWERED') AS unanswered, max(s.at) AS newest_step_time
FROM backtest_steps s LEFT JOIN backtest_answers a ON a.step_id = s.id GROUP BY s.run_id, s.kind ORDER BY s.run_id, s.kind;
SELECT params->'backtest'->>'run' AS run, count(*) FILTER (WHERE started_at IS NOT NULL) AS calls,  -- as each run's total counts them
       count(*) FILTER (WHERE created_at >= date_trunc('day', clock_timestamp() AT TIME ZONE 'UTC') AT TIME ZONE 'UTC') AS queued_today,
       count(*) FILTER (WHERE terminal_reason = 'YIELDED_TO_DECISION') AS yielded, max(created_at) AS newest
FROM agent_workflows WHERE purpose = 'BACKTEST' GROUP BY 1 ORDER BY 1;
SELECT read_at, ok, document FROM agent_usage_readings WHERE provider = 'CODEX_CLI' ORDER BY id DESC LIMIT 1;
SQL
```

The Claude run's spend, provider failures and pace (PROPOSED: not yet run against an installed `0036`; [ExecPlan 0055 §4.5](plans/0055-backtest-claude-on-the-same-history.md#45-the-money)). `counted_usd` is what the lane's cap counts (each call's cost from its tokens, nothing for a refused call, $0.20 for a call without a price); `priced_usd` is the calls' calculated cost alone:

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl <<'SQL'
SELECT count(c.id) AS calls, min(c.created_at) AS first_call, max(c.created_at) AS newest_call,
       COALESCE(sum(CASE WHEN o.status = 'FAILED' AND o.error_class IN ('AUTH_REQUIRED','QUOTA_BLOCKED','PERMISSION_DENIED',
           'RATE_LIMITED','REQUEST_REFUSED') THEN 0 WHEN o.cost_usd > 0 THEN o.cost_usd ELSE 0.20 END), 0) AS counted_usd,
       COALESCE(sum(o.cost_usd), 0) AS priced_usd
FROM agent_provider_calls c JOIN agent_steps s ON s.id = c.step_id JOIN agent_workflows w ON w.id = s.workflow_id
LEFT JOIN agent_provider_outcomes o ON o.call_id = c.id WHERE w.template_id LIKE 'BACKTEST\_CLAUDE\_%';
SELECT state, terminal_reason, count(*), max(finished_at) AS newest FROM agent_workflows
WHERE template_id LIKE 'BACKTEST\_CLAUDE\_%' GROUP BY 1, 2 ORDER BY 3 DESC;
SQL
```

The latest design's run (generation 18, [ExecPlan 0056 §4.6](plans/0056-backtest-the-traders-latest-design.md#46-the-calls-and-the-money)) the same way, with `BACKTEST\_GEN14\_%` in place of `BACKTEST\_CLAUDE\_%` in both statements, and why its lane waits, from the agent worker's log (`agent_backtest_waiting` with the run and its reason when the reason changes; `agent_backtest_design_changed` with the parts that differ while the design guard holds it). PROPOSED: not yet run against an installed `0037`:

```bash
docker compose logs --since 2h agent-worker | grep -E "agent_backtest_(waiting|design_changed)" | tail -20
```

The export for the report, read-only, one file a run into the app's folder, which the thread then copies to the cloud (`<run>` is `BACKTEST_AI_V1:TWO_MONTHS` or `BACKTEST_AI_V1:TWO_MONTHS_CLAUDE`). OBSERVED in use on the PC on 2026-11-07 at 07:58 UTC, written to `.cache/backtest-ai-export/claude-export.json` and `chatgpt-export.json` instead of `backtest-export.json`: exit 0 each, 79,415,818 bytes for the finished Claude run and 16,832,682 bytes for the ChatGPT run at 322 of its trader steps ([0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)), and again on 2026-11-08 at 14:35 UTC for the ChatGPT run into `chatgpt-export-2026-11-08.json`: exit 0, 25,359,800 bytes at 466 of its trader steps ([0056 §13](plans/0056-backtest-the-traders-latest-design.md#13-progress)):

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl -At -c "SELECT json_build_object('run', (SELECT row_to_json(r) FROM backtest_runs r WHERE r.id = '<run>'), 'steps', (SELECT json_agg(s ORDER BY s.n) FROM backtest_steps s WHERE s.run_id = '<run>'), 'answers', (SELECT json_agg(a) FROM backtest_answers a WHERE a.run_id = '<run>'))" > backtest-export.json
```

The report in the cloud, from `services/engine`, on one or both runs' exports and the shipped archive ([ExecPlan 0055 §4.8](plans/0055-backtest-claude-on-the-same-history.md#48-the-report-and-the-page)); `--opens` is C1's truths, BTC's 00:00 UTC opens read from the owner's archive and saved in the project's files (`backtest/c1-early-2026-11-05.json`). It replays each run from its stored answers and checks every step against the record; it exits 2 for an export that does not fit its run, 3 for an archive that differs from its manifest and 4 for a rebuilt step that differs from the stored one, printing no measure. VERIFIED on 2026-11-06 on SYNTHETIC exports of two scripted runs on the shipped archive ([0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)): exit 0 in about 2.5 minutes with 3 placebo accounts a run (`--placebos 3`); the default 200 add about 5.5 minutes a run. VERIFIED on 2026-11-07 on the two real exports above with the default 200: exit 0 in 4 minutes 48 seconds, every stored step rebuilt and matched ([0055 §13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)):

```bash
.venv/bin/python -m app.backtest_ai.report claude-export.json chatgpt-export.json --opens c1-early-2026-11-05.json --out backtest-ai-results.json
```

The latest design's run ([ExecPlan 0056 §4.8](plans/0056-backtest-the-traders-latest-design.md#48-the-measures-pre-registered-a-third-trial)) the same way, read-only, into `.cache/backtest-ai-export/latest-export.json`. Its export adds the workflow endings of its abstained steps (its child replays an abstention with its workflow's ending), its calls and their reported cost by template, its provider outcomes and its spend as the lane's cap counts it. OBSERVED on 2026-11-08 on a scratch database at `0038`, on a run the lane made there with generation 18's templates and a fake provider (SYNTHETIC answers, the coach abstaining; 68 steps): the statement as written, with `psql` on the scratch cluster in place of the container, exported every step, answer and ending; the report read it (exit 0, all 68 steps rebuilt and matched) and refused the same export without its endings (exit 2). OBSERVED in use on the PC on 2026-11-08 at 14:35 UTC, after the run finished: exit 0, 25,070,444 bytes, all 586 steps ([0056 §13](plans/0056-backtest-the-traders-latest-design.md#13-progress)):

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl -At -c "SELECT json_build_object('run', (SELECT row_to_json(r) FROM backtest_runs r WHERE r.id = 'BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE'), 'steps', (SELECT json_agg(s ORDER BY s.n) FROM backtest_steps s WHERE s.run_id = 'BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE'), 'answers', (SELECT json_agg(a) FROM backtest_answers a WHERE a.run_id = 'BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE'), 'endings', (SELECT json_agg(json_build_object('step_id', a.step_id, 'ending', w.terminal_reason)) FROM backtest_answers a JOIN agent_workflows w ON w.id = a.workflow_id WHERE a.run_id = 'BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE' AND a.outcome = 'ABSTAINED'), 'calls', (SELECT json_agg(t) FROM (SELECT w.template_id, count(DISTINCT w.id) AS workflows, count(c.id) AS calls, sum(o.cost_usd) AS usd, count(c.id) FILTER (WHERE o.status = 'FAILED') AS failed FROM agent_workflows w JOIN agent_steps s ON s.workflow_id = w.id JOIN agent_provider_calls c ON c.step_id = s.id LEFT JOIN agent_provider_outcomes o ON o.call_id = c.id WHERE w.template_id LIKE 'BACKTEST\_GEN14\_%' GROUP BY 1 ORDER BY 1) t), 'failures', (SELECT json_agg(t) FROM (SELECT o.status, o.error_class, count(*) AS calls FROM agent_provider_calls c JOIN agent_steps s ON s.id = c.step_id JOIN agent_workflows w ON w.id = s.workflow_id LEFT JOIN agent_provider_outcomes o ON o.call_id = c.id WHERE w.template_id LIKE 'BACKTEST\_GEN14\_%' GROUP BY 1, 2 ORDER BY 3 DESC) t), 'counted_usd', (SELECT COALESCE(sum(CASE WHEN o.status = 'FAILED' AND o.error_class IN ('AUTH_REQUIRED','QUOTA_BLOCKED','PERMISSION_DENIED','RATE_LIMITED','REQUEST_REFUSED') THEN 0 WHEN o.cost_usd > 0 THEN o.cost_usd ELSE 0.20 END), 0) FROM agent_provider_calls c JOIN agent_steps s ON s.id = c.step_id JOIN agent_workflows w ON w.id = s.workflow_id LEFT JOIN agent_provider_outcomes o ON o.call_id = c.id WHERE w.template_id LIKE 'BACKTEST\_GEN14\_%'))" > .cache/backtest-ai-export/latest-export.json
```

Its report in the cloud, from `services/engine` (`app.backtest_ai.report_latest`, [ExecPlan 0056 §4.8 and §4.9](plans/0056-backtest-the-traders-latest-design.md#49-a-partial-run)): it replays the third run from its stored answers with every step checked, as above, runs the code-only `HOLD` and `TREND_GATED` accounts over the same days, and reads M1 to M4 at 4 hours and M6 against the hourly Claude run (`--hourly`), and the family of fourteen with the ChatGPT run (`--chatgpt`); the same exits. VERIFIED on 2026-11-08 on the shipped archive with a SYNTHETIC two-day export of the third run and the two real exports above: exit 0 in 93 seconds, and again on the final code (112 seconds, beside a database check), and every figure of the earlier runs' registered readings it prints equal to 0055's report of 2026-11-07. VERIFIED on 2026-11-08 on the real exports (the finished third run, the hourly Claude run's export of 2026-11-07 and the ChatGPT run's of 2026-11-08): exit 0 in 210 seconds, all 586 stored steps of the third run rebuilt and matched ([0056 §13](plans/0056-backtest-the-traders-latest-design.md#13-progress)):

```bash
.venv/bin/python -m app.backtest_ai.report_latest latest-export.json --hourly claude-export.json --chatgpt chatgpt-export.json --out latest-results.json
```

### ExecPlan 0057: the slow trend twin's tests, samples and install check

The twin's suites, from `services/engine` on a scratch cluster ([above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). OBSERVED on 2026-11-07 ([0057 §14](plans/0057-a-slow-trend-twin.md#14-progress)): `34 passed` without a database; `136 passed` for the seven suites together on a fresh database of the second cluster (port 55453), and `138 passed` with the independent review's two new tests on a fresh database of the first:

```bash
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_slow_trend_unit.py
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_slow_trend_unit.py \
    tests/test_m11_slow_trend_db.py tests/test_m11_twins_db.py tests/test_m11_veto_db.py tests/test_m11_twins_unit.py \
    tests/test_m11_veto_unit.py tests/test_m11_perp_db.py
.venv/bin/python -m app.futures.twins v3   # the seed line migration 0038 freezes (TWIN_SET_V3, 3168e6a7…3e89)
```

The whole engine suite on a fresh database of the first cluster, OBSERVED the same evening: `6 failed, 2200 passed, 74 errors`, and after the independent review's fixes `5 failed, 2204 passed, 74 errors` (34:55), each failure and error one of the known baseline above ([0057 §14](plans/0057-a-slow-trend-twin.md#14-progress) names them). A whole run takes about 35 minutes here: a background job of the session with its default 30-minute limit stops it, so give it a longer one. After the rebase on ExecPlan 0056's merge (`8c8083c`), OBSERVED 2026-11-08: `5 failed, 2293 passed, 74 errors` (39:01), the same baseline; the 21 suites of [0057 §14](plans/0057-a-slow-trend-twin.md#14-progress) on another fresh database `3 failed, 309 passed`, `test_m11_scores_db.py`'s three; without a database `2 failed, 1375 passed, 504 skipped, 491 errors`, every error a database test refusing to run without its database.

The web's samples of the twins' reads, the engine's own answers on SYNTHETIC rows (`twins-league.json` and `twins-status.json` change; the trades samples stay V2's): `1 passed`, OBSERVED the same day on a fresh database. The five twins start under `TWIN_SET_V2` and the slow trend twin under `TWIN_SET_V3` at the next step, as on the owner's PC:

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/m11_twin_samples.py
```

The browser chain of [Browser suites](../COMMANDS.md#browser-suites-cloud) on a database seeded at 22:04:03 UTC (the seed now starts the six twins of `TWIN_SET_V3` together, and the feed's stand-in answers the daily candles, `DAILY_STORED` 400): `5 passed` (`reviews.spec.ts`), `16 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`), and after a later change to Trades' empty text `4 passed` for `twins.spec.ts` alone on the rebuilt web server. OBSERVED the same evening: `pages.spec.ts` runs once per seeded database, as `reviews.spec.ts` does: its toast test closes the open position that its Cockpit test expects, so a second run of it on that database fails the Cockpit test.

The offline check of [0057 §4.7](plans/0057-a-slow-trend-twin.md#47-the-offline-check-calculated-backtest_modeled_not_filled), in the project's shared folder `slow-trend/` (`CALCULATED`, `BACKTEST_MODELED_NOT_FILLED`): `python3 -I sim.py`, `review.py`, `review2.py`, `rebal.py` and `rebal2.py` (the twin's whole-position resize against trading the difference with the twin's own target), each writing its `.json`.

The install check on the owner's PC, read-only, after the update: the head, the twin sets, the six twins with their segments and sets, the daily candles and the slow twin's newest events. OBSERVED on 2026-11-08 at 09:21 UTC and again after the first reading on 2026-11-09 at 07:02 UTC, in a Remote Control session in Git Bash ([0057 §14](plans/0057-a-slow-trend-twin.md#14-progress) has the outputs).

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl <<'SQL'
SELECT version_num FROM alembic_version;
SELECT id, sha256 FROM execution_definitions WHERE kind = 'FUTURES_TWINS' ORDER BY version;
SELECT twin, segment, set_id, state, started_at FROM futures_twins ORDER BY seq;
SELECT count(*) AS days, to_timestamp(min(open_ms) / 1000) AS first_day, to_timestamp(max(open_ms) / 1000) AS last_day
FROM perp_daily_bars;
SELECT e.kind, e.code, e.at, e.detail FROM futures_twin_events e JOIN futures_twins t ON t.id = e.twin_id
WHERE t.twin = 'TREND_SLOW' ORDER BY e.at DESC LIMIT 5;
SELECT code, at, detail FROM perp_feed_events WHERE code LIKE 'DAILY%' ORDER BY at DESC LIMIT 3;
SQL
```

The twins' slow steps over the last 12 hours (the worker logs the first slow step of a run and every 60th after it), OBSERVED on 2026-11-09 at 07:02 UTC: `slow steps logged: n=1437 min=52.7 median=84.4 p90=90.4 max=1165.0` and `1437 "consecutive":1`:

```bash
docker compose logs --since 12h --no-log-prefix execution-worker 2>&1 | grep -o '"event":"futures_twins_step_slow"[^}]*' | grep -o '"duration_ms":[0-9.]*' | cut -d: -f2 | sort -n | awk '{a[NR]=$1} END {print "slow steps logged: n="NR, "min="a[1], "median="a[int((NR+1)/2)], "p90="a[int(NR*0.9)], "max="a[NR]}'
docker compose logs --since 12h --no-log-prefix execution-worker 2>&1 | grep -o '"event":"futures_twins_step_slow"[^}]*' | grep -o '"consecutive":[0-9]*' | sort | uniq -c
```

### ExecPlan 0058: the event calendar's tests and install check

The calendar's suite and the trader's, from `services/engine` on a scratch cluster ([above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). OBSERVED on 2026-11-09 ([0058 §14](plans/0058-the-event-calendar.md#14-progress)): `18 passed` for `test_m11_event_calendar.py` on a fresh database of the second cluster (port 55453). Each of the two checks at the finish (the bound context's and the second look's) was removed in turn and the database tests failed each time, then restored (`VERIFIED`, a mutation run):

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_event_calendar.py
.venv/bin/python -m app.agents.definitions_v19   # the seed lines migration 0039 freezes
```

The trader's, the generations', the migration head's and the backtests' 27 suites (the list in [0058 §14](plans/0058-the-event-calendar.md#14-progress)'s run) on a fresh database of the second cluster, the only run on that cluster: `3 failed, 532 passed` (11:32), the three `test_m11_scores_db.py` failures of the baseline above. A second suite started on the same cluster during an earlier run left `asl_agent`, `asl_execution`, `asl_research` and `asl_source` without login, and every later database test of the first run failed; the fixtures give each identity its login back at their start.

The whole engine suite on a fresh database, OBSERVED the same evening: `6 failed, 2323 passed, 74 errors` (57:14), the baseline above and `test_m11_slow_trend_db.py`'s downgrade test, which since then steps down `0039` first (`45 passed` for the two slow trend suites). A whole run's test modules are the ones it collected at its start, and its database holds the seed lines of the migration it was migrated with: a test or seed line changed during a run shows up as that run's failure (`generation-19 definition mismatch; downgrade refused`).

The web: `pnpm -s typecheck`, `pnpm -s lint`, `pnpm -s check`, `pnpm -s test` (`47 passed` files, `404 passed` tests), `pnpm -s build` and `pnpm -s api:check` (the engine's `openapi.json` regenerated first). Run `pnpm -s lint` before a build or after removing `.output`: a build's `.output` holds generated JavaScript that the linter reads (`192 errors` there, none in the sources).

The browser chain of [Browser suites](../COMMANDS.md#browser-suites-cloud) on a database seeded at 16:14:43 UTC: `5 passed` (`reviews.spec.ts`), `16 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`); after the trader card's wording changed, `16 passed` again for the second three on a database seeded at 16:19:34 UTC. `pages.spec.ts` reads the Settings tile "Release windows".

The install check on the owner's PC, read-only, after the update: the head, generation 19's definitions, the CPI and jobs report releases the app has stored, and the newest decisions with their trigger:

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl <<'SQL'
SELECT version_num FROM alembic_version;
SELECT id, kind, version, status FROM agent_definitions WHERE id LIKE '%\_V19' OR id = 'TRADER_PROMPT_M11_V7' ORDER BY id;
SELECT title, attribution->'supplied'->>'starts_at' AS starts_at, max(available_at) AS stored
FROM evidence_items WHERE title IN ('Consumer Price Index', 'Employment Situation')
AND attribution->'supplied'->>'starts_at' >= to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD')
GROUP BY 1, 2 ORDER BY 2 LIMIT 6;
SELECT w.template_id, d.trigger, d.action, d.context_at FROM futures_decisions d
JOIN agent_workflows w ON w.id = d.workflow_id ORDER BY d.context_at DESC LIMIT 8;
SQL
```

### ExecPlan 0059: the slow rule's tests and install check

The rule's suites, from `services/engine` ([above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). OBSERVED on 2026-11-10 ([0059 §14](plans/0059-the-slow-rule-trades-the-main-account.md#14-progress)): the rule's, the twins' and the live worker's ten suites together `173 passed` on a fresh database of the second cluster (port 55453):

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m11_twins_db.py \
    tests/test_m11_veto_db.py tests/test_m11_slow_trend_db.py tests/test_m11_twins_unit.py tests/test_m11_veto_unit.py \
    tests/test_m11_slow_trend_unit.py tests/test_m11_main_rule_db.py tests/test_m11_main_rule_unit.py \
    tests/test_m11_main_rule_agents_db.py tests/test_m11_live_unit.py
.venv/bin/python -m app.futures.definitions v2   # the seed lines migration 0040 freezes (MAIN_RULE_V1, FUTURES_POLICY_V2)
ASL_WRITE_RULE_SAMPLES=1 ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_m11_main_rule_db.py -k pages   # writes apps/web/src/futures/samples/rule-*.json (SYNTHETIC rows)
```

After the independent money-path review (OBSERVED on 2026-11-10, [0059 §13](plans/0059-the-slow-rule-trades-the-main-account.md#13-decision-log)): the same ten suites with `test_m11_futures_db.py` and `test_m11_futures_api.py` `205 passed` on a fresh database of the second cluster. Each fix was removed in turn and its test failed (`VERIFIED`, a mutation run): the stopping run's exit (`2 failed`), the refusal of a decision tagged V2 (`POSITION_OPEN` instead of `POLICY_CHANGED`) and the opener check's close reasons (migration `0040` downgraded and upgraded without the clause, `1 failed`), then restored. The samples were written again on a fresh database (only the two definitions' hashes changed). The browser chain again, on a database seeded at 17:08:04 UTC: `5`, `16`, `4` and `3 passed`, and `live.spec.ts` `4 passed` on a `flat` one.

The whole engine suite on the first cluster, OBSERVED the same day on the tree before the review's fixes (a fresh database, `0:56:14`): `15 failed, 2337 passed, 74 errors`. The 74 errors and `test_api.py`'s, `test_m6_schema.py`'s and `test_m11_scores_db.py`'s three failures are the baseline [above](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud). The others: the three stale futures tests the review named and the live worker's stand-in (fixed, in the `205`); `test_backtest_latest_db.py`'s two review sheets, whose suite did not set `trader_work` (it now takes `test_m11_reviews.py`'s fixture) and `test_m11_event_trader.py`'s overview, which now also says `trader_asked` (both fixed); `test_m7_schema.py`'s two downgrades, refused `main rule definition mismatch` because migration `0040`'s frozen rows were rewritten while the run was going (both pass on a fresh database); and one `test_m2_stream_continuity.py` test on a lock timeout. On a fresh database of the second cluster the five suites so named (`test_backtest_latest_db.py`, `test_m11_event_trader.py`, `test_m7_schema.py`, `test_m2_stream_continuity.py`, `test_m6_schema.py`) gave `4 failed, 97 passed`: the baseline's `test_m6_schema.py` and three stream tests, and the stream suite alone `1 failed, 15 passed` with another of its tests: timing under load, as on 2026-11-05 above; the build changes no market code.

Under `FUTURES_POLICY_V2` the agent worker starts none of the trader's lanes (`WorkflowGraph.trader_work` is false): the suites that drive the trader, its reviewers and the ChatGPT backtest set it true for themselves (an autouse fixture in each), and the browser fixture's `reviews` command sets it on its orchestrator; the seeded run is the trader's (`FUTURES_POLICY_V1`), while the pages show the policy in force.

The engine without a database, OBSERVED the same day: `3 failed, 1407 passed, 516 skipped, 500 errors` (7:49), the two failures of the baseline [above](../COMMANDS.md#engine-without-a-database-cloud) and `test_m11_live_unit.py`'s worker test, whose stand-in engine did not take the policy the worker now passes: fixed, `25 passed`.

The web: `pnpm -s typecheck`, `pnpm -s lint` (with no `.output`), `pnpm -s check`, `pnpm -s test` (`48` files, `419 passed`), `pnpm -s build` and `pnpm -s api:check` after `pnpm -s api:generate` on the regenerated `openapi.json`.

The browser chain of [Browser suites](../COMMANDS.md#browser-suites-cloud) on the second cluster, OBSERVED on 2026-11-10: `5 passed` (`reviews.spec.ts`), `16 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`) on a database seeded at 16:33:31 UTC; `live.spec.ts` `4 passed` on a `flat` database. The specs now read the pages as the rule shows them: Decisions opens on the readings, the trader's timeline is `?tab=timeline` (its tab "Trader"), the Cockpit keeps the league tile only, Settings' limits are V2's. The fixture's stop tightening is refused `NOT_TIGHTER` at some seed minutes (the walk is a function of the minute, as [above](../COMMANDS.md#browser-suites-cloud)): a script that seeds again each minute until the fixture prints `TIGHTEN_STOP ... APPLIED` avoids it.

The install check on the owner's PC, read-only, after the update (its SQL VERIFIED read-only on a scratch database of the second cluster; OBSERVED on the PC on 2026-11-10 at 17:31 UTC in a Remote Control session in Git Bash, every query unchanged, [0059 §14](plans/0059-the-slow-rule-trades-the-main-account.md#14-progress) has the outputs): the head, the frozen definitions, the runs (the trader's ending `NEW_POLICY` at the first flat bar, the rule's started by `SYSTEM`), the readings, the newest positions, the backtests' end and the newest agent workflows (no trader, reviewer or coach after the install):

```bash
docker compose exec -T -e PGOPTIONS="-c default_transaction_read_only=on" postgres psql -X -U asl -d asl <<'SQL'
SELECT version_num FROM alembic_version;
SELECT id, kind, version, sha256 FROM execution_definitions WHERE id IN ('MAIN_RULE_V1', 'FUTURES_POLICY_V2');
SELECT seq, policy_id, state, stop_reason, started_by, started_at, stopped_at FROM futures_runs ORDER BY seq DESC LIMIT 3;
SELECT utc_date, bar_open_ms, result, signal, volatility, target, held, action, outcome, codes, at
FROM futures_rule_readings ORDER BY seq DESC LIMIT 5;
SELECT seq, opened_by, side, leverage, quantity, notional, state, opened_at, closed_at, close_reason
FROM futures_positions ORDER BY seq DESC LIMIT 3;
SELECT id, state, code FROM backtest_runs ORDER BY id;
SELECT template_id, state FROM agent_workflows ORDER BY seq DESC LIMIT 10;
SQL
```

## Fix: the agents' check refused a release the brief cited from a search — 2026-10-21

Scope: a defect of the agents' check (`app.agents.check`, case `SC-01`) found by the read-only check after the second install of 2026-10-21 ([ExecPlan 0033 §13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log), [§14](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#14-progress)). Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `7440a89`, on Linux with no Docker daemon. No command addressed the normal application; `.env`, `secrets/` and `codex_home` were not read.

**What the PC showed** (`OBSERVED`, 11:13 to 11:20 UTC, read-only through the owner's device session: `SELECT`s in `READ ONLY` transactions): the second V3 check (probe run 32, 10:39:27 to 10:44:01 UTC) failed only in `SC-01`, "the assessment cites a reference the tools did not return". Its assessment cited 8 references: 6 were result references of its own tools, and 2 were release IDs that its `search_evidence` call returned in the envelope's `citable` list. The brief's own finish had accepted them. The next check (probe run 33, 11:14:02 to 11:18:47 UTC, on the new runner) passed; its search returned no release.

**Cause** (read in the code): the check, and probe CP-01 with it, counted only `agent_tool_results.result_ref`, while the workflow's finish rule (`_citable` in `app/agents/workflows.py`) also counts completions and each envelope's `citable` IDs.

**Run here (actual).** A scratch PostgreSQL 16 cluster on 127.0.0.1 port 55452 (`ASL_DB_HOST=127.0.0.1 PGPORT=55452 ASL_TEST_ISOLATED=1`). From `services/engine`:

```bash
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_scfix
ASL_DB_NAME=asl_m1_m6_scfix ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_scfix .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m8_check.py
# the new test against the old rule (git stash of check.py and probes.py), then restored
ASL_DB_NAME=asl_m1_m6_scfix .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m8_check.py -k search_returned
ASL_DB_NAME=asl_m1_m6_scfix .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m5_runtime.py \
    tests/test_m5_orchestrator.py tests/test_m6_agents.py tests/test_m7_agents.py tests/test_m8_check.py \
    tests/test_m8_in_force.py tests/test_m10_trading.py tests/test_m10_coins.py
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
python3 ../../tools/check_links.py ../..
```

Results, `OBSERVED`:
- **The new test** (`test_a_brief_may_cite_the_items_a_search_returned_as_its_own_finish_allows`: a check whose brief searches the sources and cites the release found instead of the search's own reference): on the old rule `1 failed` (`SC-01` not passed), on the new rule passed; it also shows that a reference returned only to the brief's review, not to the brief, still fails the case.
- **Independent review** (a separate reviewer, read-only): the new rule is the brief's finish rule for these cases and accepts nothing it refuses; refused, denied and late envelopes carry no citable IDs; `envelope` is `jsonb` in both tables. No defect. Its one suggestion, the negative case above citing another workflow's reference, is applied.
- **The check file:** `11 passed`, rerun after the review. **The agent, probe and check files:** `218 passed`.
- **Without a database:** `2 failed, 885 passed, 349 skipped, 390 errors`, the two known failures that need a database and only database errors; Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; links `0 broken link(s)`.

**NOT RUN:** the whole engine suite on a database (the change is the check's and CP-01's citation rule and one test), Docker and the images, PostgreSQL 17, a real model on the check.

**On the PC** (`OBSERVED` read-only, 13:10 to 13:25 UTC): merged as `2bf5b1e` on the owner's "Install today" (12:10 UTC) and installed by the owner's double-click: record `COMPLETE`, 12:41:48 to 13:09:45 UTC, no migration, nine services recreated, reconciliation OK, problems none, the seven pages `200`. No agents' check has run since probe run 33 passed at 11:18 UTC, so the new rule is not yet seen on the PC; the next check that searches and cites a release shows it.

## Fix: the runner refused generation 6's longer prompts — 2026-10-21

Scope: a defect of M10 update 2 ([ExecPlan 0033 §13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log), [§14](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#14-progress)) found by the read-only check after its install. Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `a5381ff`, on Linux with no Docker daemon. No command addressed the normal application; `.env`, `secrets/` and `codex_home` were not read.

**What the PC showed** (`OBSERVED`, 10:11 to 10:31 UTC, read-only, through the owner's device session: `SELECT`s in `READ ONLY` transactions and the containers' logs): update 2's record `COMPLETE` (09:43:13 to 10:10:54 UTC, `3dd5011`). The first agents' check under `AGENT_POLICY_V3` (probe run 31, 10:16:38 to 10:24:26 UTC) `FAILED`: the decision case passed; the brief's review (`BRIEF_REVIEW_V2`) sent steps 1 to 4 (prompts 42,357 to 62,283 bytes), and both attempts of step 5 (69,280 and 69,383 bytes) ended `OUTCOME_UNKNOWN` `NEVER_CONFIRMED`. The agent worker logged `agent_provider_submit_unknown` with `submit 400` 108 times for each attempt, about once a second until its deadline. Every prompt the runner accepted since 2026-10-19 was under 65,536 bytes.

**Cause** (read in the code): `POST /v1/jobs` in `services/agent-runner/runner/server.py` answers `400 INVALID_JOB` to a prompt over 65,536 bytes, while generation 6's `prompt_max_bytes` is 98,304.

**Run here (actual).** From the repository root unless stated:

```bash
# A scratch script (kept outside the repository) serves the runner's own Handler with a stub state and posts prompts
python3 -I <scratch>/check_prompt_bound.py "$PWD/services/agent-runner"     # before the fix (git stash), then after
# services/engine
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider \
    "tests/test_m10_trading.py::test_the_runner_accepts_the_longest_prompt_any_generation_composes"
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **The runner's job API:** before the fix, prompts of 65,536 bytes `202`, of 69,383 and 98,304 bytes `400`; after it, 65,536, 69,383 and 98,304 bytes `202` and 98,305 bytes `400`.
- **The new test:** `1 passed` (it reads the runner's `MAX_PROMPT` and asserts it is at least the largest `prompt_max_bytes` of any generation, 98,304).
- **Without a database:** `2 failed, 884 passed, 349 skipped, 389 errors`, the two known failures that need a database and only database errors; Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; links `0 broken link(s)`.

**NOT RUN.** The runner's own suites (they run inside its test image, on Docker); the database suites (the change touches no database code); a real model sent a prompt over 64 KiB (first seen on the PC after the install). No independent review: no money path changes.

## M10 update 2: ZEC, NEAR and XRP on paper — 2026-10-21

Scope: update 2 of [ExecPlan 0033 §9](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#9-implementation-sequence) (§5.2, [§13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log), [§14](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#14-progress)). Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `8f04b9b`, on Linux with no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. The only reads on the owner's PC were read-only `SELECT`s of the watchlist, the notes, the refused answers and the main account (about 06:30 and 06:35 UTC, each in one `READ ONLY` transaction, through the owner's device session). No model was called and no public endpoint was contacted from here: every model answer is scripted (`OFFLINE_TEST`) and every Binance answer SYNTHETIC.

**Run here (actual).** Two scratch PostgreSQL 16 clusters on 127.0.0.1, port 55452 (M9's) and port 55453 (this update's), each with `ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1`; never two database test runs on one cluster at once. From `services/engine` unless stated:

```bash
# Migration 0016 up, down and up again on a fresh database, then a refused downgrade (port 55453)
createdb -h 127.0.0.1 -p 55453 -U asl asl_m1_m6_m10u2mig
ASL_DB_NAME=asl_m1_m6_m10u2mig ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m10u2mig ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
psql -h 127.0.0.1 -p 55453 -U asl -d asl_m1_m6_m10u2mig -Atc "SELECT version_num FROM alembic_version; \
    SELECT string_agg(symbol, ',' ORDER BY symbol) FROM market_feed_state; SELECT string_agg(asset, ',' ORDER BY asset) FROM account_holdings"
ASL_DB_NAME=asl_m1_m6_m10u2mig ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
psql ... -Atc "INSERT INTO market_incidents (symbol, code) VALUES ('ZECUSDT', 'M10_DOWNGRADE_PROBE')"
ASL_DB_NAME=asl_m1_m6_m10u2mig ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1   # refused
# After the review: 0015 with an old row, 0016 adds its checks NOT VALID; a coin outside the list is still refused
#   ('ETHUSDT'); the downgrade validates the narrower checks; a held table makes the migration fail at its lock
#   timeout and the next attempt succeed (a second session holding ROW EXCLUSIVE on market_observations for 3 s)
# The modules this update touches, as they were built (port 55453)
ASL_DB_NAME=asl_m1_m6_m10u2t .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m10_trading.py
# The files the whole suite showed failing, after their fixes (port 55452)
ASL_DB_NAME=asl_m1_m6_m10u2full .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m2_stream_continuity.py \
    tests/test_m3_roles.py tests/test_m7_agents.py tests/test_m7_schema.py tests/test_m10_trading.py
ASL_DB_NAME=asl_m1_m6_m10u2full .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m2_reference_checks.py
# The whole suite on the final tree, on a freshly migrated database (port 55453)
ASL_DB_NAME=asl_m1_m6_m10u2final .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# The web (apps/web)
pnpm run typecheck
pnpm exec eslint . --ignore-pattern '.output/**'
pnpm run check
pnpm run api:check
pnpm exec vitest run
pnpm run build
# The browser suites, each on a fresh seeded database (port 55452), with the API and the built server on this tree
NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs   # apps/web
ASL_DB_NAME=asl_m1_m6_m10u2f_browser .venv/bin/python -m tests.m10_browser_fixture seed
ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_m10u2f_browser ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
ASL_M10_BROWSER=coins ASL_DB_NAME=asl_m1_m6_m10u2f_browser pnpm exec playwright test -c <scratch config> e2e/m10.spec.ts --workers 1
ASL_DB_NAME=asl_m1_m6_m10u2fd_browser .venv/bin/python -m tests.m7_browser_fixture seed
env -u ASL_TEST_ISOLATED ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_m10u2fd_browser ASL_DB_ROLE=api \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
ASL_M7_BROWSER=decisions ASL_DB_NAME=asl_m1_m6_m10u2fd_browser \
    pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @decisions --workers 1
# The update file (repository root; PowerShell 7, not Windows PowerShell 5.1)
pwsh -NoProfile -File tools/m8/update-model.ps1 -Repository . -Work <an empty scratch directory>
grep -nP '[^\x00-\x7F]' tools/update.ps1 tools/update.cmd tools/m8/update-model.ps1   # no output
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **Migration `0016`:** upgrade, downgrade to `0015` and upgrade again exit 0; after the downgrade the feeds and holdings are BTC's and SOL's only, after the upgrade `BTCUSDT,NEARUSDT,SOLUSDT,XRPUSDT,ZECUSDT`, the five holdings and `AGENT_POLICY_V3` stored. With one incident naming ZEC the downgrade exits 1 with `RuntimeError: M10 three-coin records exist; downgrade refused; fix forward` and the head stays `0016_m10_three_coins`. After the review's change the widened checks show `convalidated` false (`NOT VALID`), an `ETHUSDT` row is refused (`Failing row contains (2, ETHUSDT, …)`), the downgrade leaves `market_symbol` validated, and with `market_observations` held by another session the upgrade fails with `LockNotAvailable: canceling statement due to lock timeout`, leaving `0015_m10_coins`, and succeeds on the next try.
- **The update's own tests** (`test_m10_trading.py`): `23 passed`.
- **The whole engine suite** on the final tree but for one test fix (port 55453, 38 minutes): `4 failed, 1545 passed, 16 warnings, 74 errors`. Three failures and all 74 errors are `main`'s known baseline ([COMMANDS](../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)): `test_api.py`'s status, `test_m6_agents.py`'s priority, `test_m6_schema.py`'s downgrade, `test_m1_account.py`'s 13 errors and the research store's 61. The fourth, `test_m2_reference_checks.py::test_pending_adoption_does_not_re_open_a_feed_while_the_clock_is_unverified`, waited for two pending feeds where the worker now has five; it failed alone too (`1 failed, 25 passed`), the test now counts one per coin, and the file rerun alone gives `26 passed`. `test_m3_throughput.py`'s replay batch, failing in the 2026-10-20 baseline, passed.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 883 passed, 349 skipped, 389 errors`: the two failures are the known ones that need a database (`test_api.py`'s status and `test_database.py::test_migrated_database_is_ready`), and every error is a test that requires a prepared database (`Required M6 tests need a prepared isolated asl_m1_m6_ database` and the like).
- **Web:** typecheck and ESLint exit 0; Prettier `All matched files use Prettier code style!`; `Generated TypeScript API types match`; Vitest 26 of 26 test files and 270 of 270 tests passed; the build exits 0.
- **Browser:** the Coins suite `2 passed`; the Decisions suite `12 passed`.
- **The update file:** the model test `"failed":[]`, including each coin read out with its newest quote (`update`), and the plain-text check prints nothing.
- **Links:** `0 broken link(s)`.
- **Independent review** (a read-only subagent, no database): no ledger defect; four should-fix findings and one blocking gap, all fixed here ([0033 §13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log)):
  1. the retry detail could carry a key the model invented into the next prompt: it now names only the schema's own words (a test injects keys into schemas v2, v4 and v5);
  2. moving a flat V2 run to V3 restarted the 24-hour notional window and skipped V2's wait after a protective stop: V1, V2 and V3 now count together (`intents.counted_with`; the fill test checks it);
  3. dust in a new coin would have left any older policy's valuation invalid for good: the engine reads and values every coin it holds or has a position or order in (`test_a_step_of_a_two_coin_strategy_values_a_held_new_coin_at_its_bid`);
  4. migration `0016` re-validated a week of quotes under exclusive locks while the app runs: it locks up front in the workers' order and adds the checks `NOT VALID` (the checks above); its downgrade also counts runtime profiles that bind generation 6;
  5. the documents: AGENTS.md rule 1, PROJECT P02, ACCEPTANCE A01 ([DECISIONS](../DECISIONS.md#2026-10-21--m10-update-2-zec-near-and-xrp-traded-on-paper-execplan-0033)), the plan's §13 and §14 and the scope and contract documents.

  Its notes, recorded and not changed: a combined `exchangeInfo` answer that arrives but cannot be read fails all five coins until the next check; fills in the new coins use the same cost scenario as BTC and SOL (modeled); while anything is held, every quote of the five coins starts an engine step (about 2.5 times as many); the storage stop of 12 GiB was not checked against the PC's free disk. The update file's line about the move to V3 now shows only for a main run on an earlier operating policy.
- **Found here, fixed:** the agent-runtime view refused its own response (`extra_forbidden` on `budgets_v6`), which the Decisions browser suite found and would have broken the Agents page after the install; the risk view failed on a coin without a feed row on a database before `0016` (R29's check at `0008`); the tests that expected BTC and SOL only (two stream faults, a clock reference check's pending feeds, the account snapshot and the policy holdings) now expect the five coins, and the test profiles that cap a decision-family purpose bind the cap in generation 6 too (0033 §13).
- **Clean-up:** the API and the web server stopped by process ID; `apps/web/.output` removed (no `test-results` or `.scratch` left); the scratch databases dropped by exact name (on 55452 `asl_m1_m10u2_probe`, `asl_m1_m6_m10u2f_browser`, `asl_m1_m6_m10u2fd_browser`, `asl_m1_m6_m10u2full`; on 55453 `asl_m1_m6_m10u2t`, `asl_m1_m6_m10u2_browser`, `asl_m1_m6_m10u2_dec_browser`, `asl_m1_m6_m10u2final`; the migration check's database earlier); both clusters stopped with `pg_ctl -D <dir> -m fast stop` and their directories and logs removed by exact path; the update file's scratch work directories removed. No Docker resource was created.

**NOT RUN.** Anything on Docker, including the image build; PostgreSQL 17; Windows PowerShell 5.1; a real model sent a generation-6 step; the new coins' streams and quotes from Binance (first seen on the PC after the install); the PC's free disk against the 12 GiB stop; `pnpm exec shadcn info --json` (its registry host was refused here, [INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m10-update-2-zec-near-and-xrp-on-paper--2026-10-21)). On the PC the update is the same double-click on `update-app.cmd` ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)).

## Fix: the analyst's market view read every live quote as unavailable — 2026-10-20

Scope: a defect in M5's `get_snapshot` found by the read-only check of M10 update 1 on the PC, not a milestone change. Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `3ec85ec`.

**What the PC showed** (`OBSERVED`, 13:25 to 13:33 UTC, read-only, through the owner's device session): in every analyst MARKET view, BTCUSDT and SOLUSDT read `quote_quality` `UNAVAILABLE` with `FEED_OR_REFERENCE_UNAVAILABLE` under the live rule, while the feed was `CONNECTED` with valid telemetry and lease and the quotes were about 1 s old. **Cause:** a job's cutoff stores the feed state as JSON, so its `collection_id` and `instrument_id` came back as text, and the live rule (`app.execution.eligibility.live_quote_quality`) compared them with the quote's UUIDs, which never matched. **Fix:** `Orchestrator._feeds` reads both back as UUIDs. The coordinator's portfolio view, the engine's own eligibility and every order check read the database directly and were not affected; nothing about orders, fills or the ledger changes.

The same check saw the agents' self-check fail four times (11:36 to 13:12 UTC) and pass on the fifth (13:30:40). Under the build before M10 update 1, `query_market_features` for BTCUSDT failed with `TOOL_FAILED` on each brief (11:36, 11:52, 12:23), so the brief abstained or its abstention was refused as `SCHEMA_INVALID`; the worker's logs of that time were replaced with its container at 13:10, so the cause is NOT FOUND, and on the new build the same calls succeeded. At 13:12 the review of a sound brief ran out of its budget after one refused output. Neither is changed here.

**Run here (actual)**, the scratch PostgreSQL 16 cluster on 127.0.0.1 port 55452, from `services/engine`:

```bash
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_quotes
ASL_DB_NAME=asl_m1_m6_quotes ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_quotes .venv/bin/python -m pytest -q -p no:cacheprovider -rf tests/test_m5_orchestrator.py -k fresh_quote   # before and after the fix
ASL_DB_NAME=asl_m1_m6_quotes .venv/bin/python -m pytest -q -p no:cacheprovider -rf tests/test_m5_orchestrator.py tests/test_m5_runtime.py \
    tests/test_m6_agents.py tests/test_m7_agents.py tests/test_m8_check.py tests/test_m9_agents.py tests/test_m10_coins.py tests/test_m7_evaluation.py
.venv/bin/ruff check --no-cache .
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
```

Results, `OBSERVED`: the new test `test_a_fresh_quote_of_a_healthy_feed_is_valid_in_the_analysts_market_view` failed before the fix with the PC's reading (`UNAVAILABLE`, `FEED_OR_REFERENCE_UNAVAILABLE`) and passes after it. The eight agent modules: `2 failed, 208 passed`: `main`'s priority case, and `test_m6_agents.py::test_an_investigation_refreshes_a_source_waits_without_the_slot_and_cites_what_it_was_given`, which then passed alone and in its module (`1 failed, 48 passed`, the priority case only); the fix does not touch sources. Ruff `All checks passed!`; without a database `2 failed, 869 passed, 345 skipped, 392 errors`, `main`'s two failures. The database `asl_m1_m6_quotes` was dropped by name and the cluster stopped.

**NOT RUN.** Docker, PostgreSQL 17, a real model. The fix reaches the PC with the next update the owner runs. It changes no agent definition, so the runtime profile stays the one in force and the agents' check is not run again for it (the profile changes only with the definitions, `app.agents.profile.current`).

## M10 update 1: the coin watchlist and the notes — 2026-10-20

Scope: update 1 of [ExecPlan 0033 §9](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#9-implementation-sequence) (§5.1, [§13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log), [§14](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#14-progress)). Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `33a9297`, on Linux with no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. The only reads on the owner's PC were the read-only Binance requests of [INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m10-update-1-the-coin-watchlist-and-the-notes--2026-10-20). No model was called and no public endpoint was contacted from here: every model answer is scripted (`OFFLINE_TEST`) and every Binance answer a SYNTHETIC one shaped like the PC's.

**Run here (actual).** The scratch PostgreSQL 16 cluster of M9 update 2 on 127.0.0.1 port 55452 (`ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55452`). From `services/engine` unless stated:

```bash
# Migration 0015 up, down and up again on a fresh database, then a refused downgrade
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m10c
ASL_DB_NAME=asl_m1_m10c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
psql -h 127.0.0.1 -p 55452 -U asl -d asl_m1_m10c -Atc "SELECT version_num FROM alembic_version; \
    SELECT count(*) FROM agent_definitions WHERE id LIKE '%_V5' OR id LIKE '%_M10_V1' OR id = 'AGENT_STEP_SCHEMA_V4'; \
    SELECT has_table_privilege('asl_api','coin_daily_bars','SELECT'), has_table_privilege('asl_api','coin_scans','SELECT'), \
    has_table_privilege('asl_source','coin_daily_bars','INSERT')"
ASL_DB_NAME=asl_m1_m10c ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
ASL_DB_NAME=asl_m1_m10c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
psql -h 127.0.0.1 -p 55452 -U asl -d asl_m1_m10c -Atc "INSERT INTO coin_scans (id, rules_id, rules_sha256, started_at, completed_at, \
    state, failure, weight, requests, summary) VALUES (gen_random_uuid(), 'COIN_SCAN_V1', repeat('0', 64), now(), now(), 'FAILED', \
    'SYNTHETIC_DOWNGRADE_CHECK', 0, 0, '{\"label\":\"SYNTHETIC\"}') RETURNING state"
ASL_DB_NAME=asl_m1_m10c ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1   # refused
# The modules the review's fixes touch (a fresh database at 0015; ASL_M10_SAMPLE_COINS rewrites the web sample)
ASL_M10_SAMPLE_COINS=../../apps/web/src/coins/samples/coins.json ASL_DB_NAME=asl_m1_m6_m10b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_m10_coins.py tests/test_generations.py tests/test_m6_agent_units.py tests/test_m5_schema.py tests/test_m6_agents.py \
    tests/test_m6_schema.py tests/test_m6_sources.py tests/test_m7_schema.py tests/test_m9_agents.py
# The whole suite (a fresh database at 0015 each time)
ASL_DB_NAME=asl_m1_m6_m10final .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
python -m compileall -q <a copy of app/>                               # what the image's compile step does
# The web (apps/web)
pnpm run typecheck
pnpm exec eslint . --ignore-pattern '.output/**'
pnpm run check
pnpm run api:check
pnpm exec vitest run
pnpm run build
# The browser suites, each on a fresh seeded database, with the API and the built server on this tree
NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs   # apps/web
#  the Coins page: the API reads the fixture's OFFLINE_TEST notes
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_m10f_browser
ASL_DB_NAME=asl_m1_m6_m10f_browser ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m10f_browser .venv/bin/python -m tests.m10_browser_fixture seed
psql -h 127.0.0.1 -p 55452 -U asl -d postgres -Atc "SELECT rolcanlogin FROM pg_roles WHERE rolname = 'asl_source'"   # f
ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_m10f_browser ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
ASL_M10_BROWSER=coins ASL_DB_NAME=asl_m1_m6_m10f_browser \
    pnpm exec playwright test -c <a scratch copy of the config with the image's Chromium> e2e/m10.spec.ts --workers 1
#  the Decisions pages: the API without ASL_TEST_ISOLATED, as M9 ran it
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_m10m7_browser
ASL_DB_NAME=asl_m1_m6_m10m7_browser ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m10m7_browser .venv/bin/python -m tests.m7_browser_fixture seed
env -u ASL_TEST_ISOLATED ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_m10m7_browser ASL_DB_ROLE=api \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
ASL_M7_BROWSER=decisions ASL_DB_NAME=asl_m1_m6_m10m7_browser \
    pnpm exec playwright test -c <the same scratch config> e2e/m7.spec.ts --grep @decisions --workers 1
# The update file (repository root; PowerShell 7.4.6, not Windows PowerShell 5.1)
pwsh -NoProfile -File tools/m8/update-model.ps1 -Repository . -Work <an empty scratch directory>
grep -nP '[^\x00-\x7F]' tools/update.ps1 tools/update.cmd tools/m8/update-model.ps1   # no output
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **Migration `0015`:** upgrade, downgrade to `0014` and upgrade again exit 0. At the head the seven generation-5 rows are stored; the API can read `coin_scans` but not `coin_daily_bars` (`f|t|t`, the source identity inserting). After the downgrade the seven rows and the three `coin_` tables are gone (`0`, `0`). With one scan stored, the downgrade exits 1 with `RuntimeError: M10 coin records exist; downgrade refused; fix forward`, and the head and the seven rows stay.
- **The whole engine suite**, first on the tree before the review's fixes (ending 12:20 UTC): `8 failed, 1520 passed, 16 warnings, 74 errors`. The 74 errors and three of the failures are `main`'s on this cluster, as M9's updates recorded them: `test_m1_account.py`'s 13 errors, the research store's 61 (`test_m6_bridge.py`, `test_m6_runner.py`, `test_m6_shadows.py`, `test_m6_staging.py`, `test_m7_control_bridge.py`), `test_m3_throughput.py`'s replay batch, `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research` and `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`. The other five were this update's own: `test_m6_agent_units.py` still expected 34 seeded definitions (now 41), and the four privilege inventories, one each in `test_m5_schema.py`, `test_m6_agents.py`, `test_m6_schema.py` and `test_m6_sources.py`, met the new `coin_` tables. Those inventories now leave the coin tables to an exact M10 inventory (`test_each_identity_holds_exactly_its_m10_grants`); nothing an earlier inventory checks was loosened.
- **After the review's fixes**, the modules they touch: `2 failed, 348 passed, 16 warnings`, the two `main` failures above (priority, downgrade). Then the whole suite on the final tree, on a freshly migrated database (12:36 to 12:57 UTC): `4 failed, 1529 passed, 16 warnings, 74 errors`: the same 74 errors and three `main` failures, and `test_api.py::test_status_requires_service_identity_and_ready_database`, which expects no operating policy installed. Since M8 the migrations install `AGENT_POLICY_V2`, so on a database no earlier test has emptied that case answers `unapproved`; it passes alone on the database the suite left. The same case fails the same way with `main`'s own code (`33a9297`, a copy of the tree) on a fresh database at `0014`, so it is `main`'s and is left as it is.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 869 passed, 344 skipped, 1 warning, 392 errors`, the same two failures as `main` (`test_api.py::test_status_requires_service_identity_and_ready_database`, `test_database.py::test_migrated_database_is_ready`), every error a database case. **Byte-compiling** a copy of `app/` (183 files, local Python 3.13.16, not the image's 3.13.11) exit 0.
- **Web:** typecheck exit 0; ESLint exit 0 (`pnpm run lint` also reads the git-ignored build output `.output/` and reports its 166 problems there only; with the output removed, `pnpm run lint` exits 0); Prettier `All matched files use Prettier code style!`; `Generated TypeScript API types match`; Vitest `25 passed` files, `281 passed` tests; the build exit 0.
- **Browser:** `e2e/m10.spec.ts`, `1 passed`: the eight rows, "Not now" with "Evaluator: acceptable" on the first and "Writing a note…" on the second, "Notes today: 2 of 3", the failed attempt's code, the hostile summary shown as text, the 18 pairs left out, no sideways scroll or clipped card at 390 and 1440 px, and the note's workflow on the Agents page. `e2e/m7.spec.ts --grep @decisions`, `12 passed`. A first run of the Decisions suite with `ASL_TEST_ISOLATED=1` in the API's environment failed one case ("DECISION IN PROGRESS" where "POLICY RUN NOT LIVE" was expected): with that variable the API counts the fixture's offline test run as the policy run, which the suite does not expect; run as M9 ran it, all 12 pass. The Coins suite needs the variable for the opposite reason: the page shows only notes of the mode the API runs in.
- **The update file:** the model test `"failed":[]`, including the newest coin scan read out as succeeded (contract), failed with its code and the notes written (update) and not run yet (settings), and `/coins` among the pages checked; the plain-text check prints nothing.
- **Links:** `0 broken link(s)`.
- **Independent review** (a read-only subagent, no database, no suite): nothing blocking, no authority or money-path change; two should-fix and seven optional findings. Fixed:
  1. a lost request for one candidate's daily bars left that coin out and still ended the scan `SUCCEEDED`, so a network fault after the reference bars could replace the watchlist with a partial or empty one for the whole day: any failed request now fails the scan (`CANDIDATE_BARS_UNAVAILABLE:<code>`), which is retried an hour later; a spoiled answer still leaves only its coin out (`test_a_failed_request_for_the_listing_or_any_bars_fails_the_whole_scan`);
  2. the update file's new read-out had no answer in the model test, so its branches never ran, and the install did not check `/coins`: the model answers each branch and `/coins` is among the pages;
  3. a scan the store could not write left no trace and repeated hourly past the 4 attempts: it is recorded as a failed attempt `RECORD_FAILED:<error>` with its weight, and the parser now refuses a negative volume or trade count, which the table would have refused;
  4. the read-out said the app starts the scan by itself even with the source fetcher off: it now says the fetcher is off. The page's "No scan yet" keeps its words, since the page cannot tell whether the fetcher runs;
  5. "Notes today" counted the day's note workflows, not what the cap counts: it now counts notes started today plus those queued, as the cap does;
  6. "Writing a note…" showed while the review ran: it now shows only while the note is queued, running or waiting for a tool;
  7. the API and the agent worker could read `coin_daily_bars` without using them: the grant is gone (the inventory test above);
  9. the unnarrowed evidence search applied to any workflow without symbols: it now applies to the coin note only.

  Left as it is: (8) the cut to 30 candidates comes before the instrument check, so a halted pair that Binance still lists with recent volume can take one of the 30 places; the scan module, [RUNTIME_AGENTS](RUNTIME_AGENTS.md#m10-runtime-the-coin-notes-execplan-0033) and the plan's §14 say so. The review also noted, as existing M8 behavior, that installing generation 5 changes the runtime profile, so the agents' check must pass again before new entries reopen; exits and stops never wait.
- **Found here, fixed:** the browser fixture left the source identity able to log in, so migration `0008` refused the next scratch database ("M6 role has unexpected authority"). The fixture now returns it to `NOLOGIN` (`f` above).
- **Clean-up:** the API and the web server stopped by process ID, `apps/web/node_modules/.scratch`, `apps/web/test-results` and the build output `apps/web/.output` removed, the databases `asl_m1_m10base`, `asl_m1_m10c`, `asl_m1_m6_m10b`, `asl_m1_m6_m10_browser`, `asl_m1_m6_m10m7_browser`, `asl_m1_m6_m10f_browser`, `asl_m1_m6_m10final` and, from the status case's check, `asl_m1_m6_m10api` and `asl_m1_m6_mainapi` dropped by name, the copy of `main` removed, and the scratch cluster stopped.

**NOT RUN.** Anything on Docker, including the image build; PostgreSQL 17; Windows PowerShell 5.1; a real model sent a coin note; a real Binance scan from the app (its first one on the PC records its real weight and requests). On the PC the update is the same double-click on `update-app.cmd` ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)).

## M9 update 2: the agents act on news and price moves — 2026-10-20

Scope: update 2 of [ExecPlan 0032 §9](plans/0032-m9-news-and-events-the-agents-trade-on.md#9-implementation-sequence) (§5.2, §5.3, [§14](plans/0032-m9-news-and-events-the-agents-trade-on.md#14-progress)). Written by the project thread "Get M9 ready to build" on branch `claude/plan-m9-ob2ejk` from `main` at `89b9de2`, on Linux with no Docker daemon. No command addressed the normal application, the owner's PC or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called and no feed was fetched: every model answer is scripted (`OFFLINE_TEST`), every feed the loopback mock publisher and every market value a labeled fixture.

**Run here (actual).** A scratch PostgreSQL 16 cluster on 127.0.0.1 port 55452 (`initdb -A trust -U asl`, `ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55452`, random scratch password files under `/run/secrets`). From `services/engine` unless stated:

```bash
# Migration 0014 up, down and up again on a fresh database, then a refused downgrade
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_m9u2c
ASL_DB_NAME=asl_m1_m6_m9u2c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m9u2c ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
ASL_DB_NAME=asl_m1_m6_m9u2c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
psql -h 127.0.0.1 -p 55452 -U asl -d asl_m1_m6_m9u2c -Atc "INSERT INTO agent_triggers (id, family, dedupe_key, cooldown_until, detail) \
    VALUES (gen_random_uuid(), 'PRICE_MOVE', 'move:BTCUSDT:synthetic-downgrade-check', now(), '{\"label\":\"SYNTHETIC\"}'::jsonb) RETURNING family"
ASL_DB_NAME=asl_m1_m6_m9u2c ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1   # refused
psql -h 127.0.0.1 -p 55452 -U asl -d asl_m1_m6_m9u2c -Atc "SELECT version_num FROM alembic_version; \
    SELECT count(*) FROM agent_definitions WHERE id LIKE '%_V4' OR id LIKE '%_M9_V1'"
# The new and changed modules, then the whole suite (asl_m1_m6_m9u2 at 0014)
ASL_DB_NAME=asl_m1_m6_m9u2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m9_agents.py tests/test_m9_health.py tests/test_generations.py
ASL_DB_NAME=asl_m1_m6_m9u2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_agents.py tests/test_m6_agents.py \
    tests/test_m6_agent_units.py tests/test_m8_check.py tests/test_m7_api.py tests/test_m6_api.py
ASL_DB_NAME=asl_m1_m6_m9u2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# The web (apps/web)
pnpm run typecheck
pnpm exec eslint --ignore-pattern '.output/**'
pnpm run check
pnpm run api:check
pnpm exec vitest run
pnpm run build
# The browser suite on a fresh seeded database, the API and the built server on this tree
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_m9u2_browser
ASL_DB_NAME=asl_m1_m6_m9u2_browser ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m9u2_browser .venv/bin/python -m tests.m7_browser_fixture seed
ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m6_m9u2_browser ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs   # apps/web
ASL_M7_BROWSER=decisions ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_m9u2_browser PLAYWRIGHT_BASE_URL=http://web:4318 \
    pnpm exec playwright test -c <a scratch copy of the config with the image's Chromium> e2e/m7.spec.ts --grep @decisions --workers 1
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **Migration `0014`:** upgrade, downgrade to `0013` and upgrade again exit 0; at the head the six generation-4 rows are stored and the family check admits `PRICE_MOVE`, and after the downgrade both are gone. With one `PRICE_MOVE` trigger stored, the downgrade exits 1 with `RuntimeError: M9 agent records exist; downgrade refused; fix forward`. (A first try of that insert failed on the `NOT NULL` of `cooldown_until`, so that downgrade ran with no M9 record and passed, as it should; the insert was then made with `cooldown_until = now()`.)
- **The M9 modules** after the review's fixes (unchanged since): `test_m9_agents.py`, `test_m9_health.py` and `test_generations.py`, `29 passed`. Each of the review's fixed paths has a test that failed before its fix (below).
- **The whole engine suite**, first on the tree before the review (08:28 to 08:48 UTC): `3 failed, 1477 passed, 16 warnings, 74 errors`, every one `main`'s on this cluster, as update 1 recorded them: `test_m1_account.py`'s 13 errors, the research store's 61 (`test_m6_bridge.py`, `test_m6_runner.py`, `test_m6_shadows.py`, `test_m6_staging.py`, `test_m7_control_bridge.py`), `test_m3_throughput.py`'s replay batch, `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research` and `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`. Then on the final tree (09:06 to 09:28 UTC): `3 failed, 1488 passed, 16 warnings, 74 errors`, the same three failures and 74 errors, and the 11 new database cases passing.
- **After the review's fixes**, the modules they touch (08:53 to 08:57 UTC): `3 failed, 238 passed`. One was `main`'s priority case above. `test_m6_agents.py::test_calls_whose_work_never_ends_do_not_hide_the_ones_that_finished` failed (17 waiting calls, 22 expected) because its investigations now count under their own cap of 16, as the fix intends; the case now binds an `INVESTIGATION` cap of 24 and passes. `test_m7_agents.py::test_an_open_decision_holds_every_trigger_past_the_cooldown_and_a_held_position_event_stays_exempt` passed alone and in its module (`44 passed`); it is a time-of-day fault older than M9: started between HH:54:00 and HH:54:59 UTC, its second pass falls inside the quiet window (HH:59:30 to HH:06:00), because the case stepped past the window only when the minute after was inside it. Checked over every second of an hour with the code's own `in_quiet_window`: 60 bad starts with the old step, 0 when the moment itself is checked too, which the case now does.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 837 passed, 344 skipped, 1 warning, 382 errors`, the same two failures as `main` (`test_api.py::test_status_requires_service_identity_and_ready_database`, `test_database.py::test_migrated_database_is_ready`), every error a database case (update 1's 371 and the 11 new).
- **Web:** typecheck exit 0; ESLint exit 0 (`pnpm run lint` also reads the local build output `.output/`, which git ignores, and reports its 164 problems there only, so the run names it out); Prettier `All matched files use Prettier code style!`; `Generated TypeScript API types match`; Vitest `24 passed` files, `271 passed` tests; the build exit 0.
- **Browser:** `e2e/m7.spec.ts --grep @decisions` on a freshly seeded database and a build of the final tree, `12 passed`; the trigger card with no segment shows the feed table only, at both widths.
- **Links:** `0 broken link(s)`.
- **Independent review** (a read-only subagent, no database, no suite): no blocking finding; five should-fix and six optional findings. Fixed, each with a test:
  1. the trigger table did not show why a feed item or price move started no investigation: the feed table now counts each feed's triggers waiting, canceled and refused by cause (the investigations' daily cap, too old, one already open, other);
  2. "Decisions that traded" counted any decision that submitted, whatever the engine answered: the column is now "Decisions that submitted";
  3. an owner's M6 investigation was counted under the 24 that research and promotions share and not under the investigations' 16: it now counts under its purpose's own cap (`test_an_owners_m6_investigation_counts_under_the_investigations_own_cap_not_the_shared_one` failed before);
  4. the coordinator's snapshot dropped its own history before any release: releases now go first;
  5. the snapshot sends each release's title and status, while the recorded scope said times only: the scope (`profile.py`) and the plan now say so, with the label `RELEASE_TITLES_AND_STATUS_ARE_THE_PUBLISHERS_TEXT`;
  6. a calendar read that failed would have stopped every decision start: the decision now goes on without releases, labeled `RELEASES_UNAVAILABLE`;
  7. pressing the shown segment again jumped to the newest: it now stays (`pages.test.tsx` failed before);
  8. with no segment the card hid the feed table: the feeds now show;
  9. the realized-P&L sum now runs in the engine's decimal context.

  Left as they are: (10) the price-move check is blind for the first moments after each hour, until the bar just ended is final, and for up to about 15 hours after a missing hourly bar; it fails closed with the same rule as `query_market_features`, and [RUNTIME_AGENTS](RUNTIME_AGENTS.md#m9-runtime-news-and-price-moves-start-investigations-execplan-0032) says so. (11) `asl_source` and `asl_research` may insert a trigger of any family, `PRICE_MOVE` now included; that grant predates M9 for every family, and both are identities only the app's own code uses.
- **Clean-up:** the API and the web server stopped by process ID, `/etc/hosts` restored, `apps/web/node_modules/.scratch` and the build output `apps/web/.output` removed, the databases `asl_m1_m6_m9u2`, `asl_m1_m6_m9u2c`, `asl_m1_m9u2base` and `asl_m1_m6_m9u2_browser` dropped by name (no `asl` database left), and the scratch cluster stopped.

**NOT RUN.** Anything on Docker, including the image build with its new `compileall` step (a compile of the same files with local Python 3.13.16 exited 0, [INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m9-update-2--2026-10-20)); PostgreSQL 17; Windows PowerShell 5.1; a real model sent a generation-4 step; a real feed item or price move reaching an investigation. On the PC the update is the same double-click on `update-app.cmd` ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)).

## M9 update 1: the free feeds — 2026-10-19

Scope: update 1 of [ExecPlan 0032 §9](plans/0032-m9-news-and-events-the-agents-trade-on.md#9-implementation-sequence) ([§14](plans/0032-m9-news-and-events-the-agents-trade-on.md#14-progress)). Written by the project thread "Plan M9" on branch `claude/plan-m9-ob2ejk` from `main` at `a88b9da`, on Linux with no Docker daemon. No command addressed the normal application, the owner's PC or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called, and no feed was fetched by the app's code (the publishers were read once through the session's web-fetch tool, [INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m9-update-1-the-free-feeds--2026-10-19)).

**Run here (actual).** A scratch PostgreSQL 16.15 cluster on 127.0.0.1 port 55451 (`initdb -A trust -U asl`, `ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55451`, random scratch password files under `/run/secrets`). From `services/engine` unless stated:

```bash
# Migration 0013 up, down and up again on a fresh database
createdb -h 127.0.0.1 -p 55451 -U asl asl_m1_m6_m9u1c
ASL_DB_NAME=asl_m1_m6_m9u1c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m9u1c ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
ASL_DB_NAME=asl_m1_m6_m9u1c ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
# The new module, then the whole suite (asl_m1_m6_m9u1 at 0013)
ASL_DB_NAME=asl_m1_m6_m9u1b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m9_feeds.py tests/test_m6_source_units.py
ASL_DB_NAME=asl_m1_m6_m9u1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests
ASL_DB_NAME=asl_m1_m6_m9u1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE <the five failures above> tests/test_m9_feeds.py
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# The update file (repository root; PowerShell 7.4.6, not Windows PowerShell 5.1)
pwsh -NoProfile -File tools/m8/update-model.ps1 -Repository . -Work <an empty scratch directory>
grep -nP '[^\x00-\x7F]' tools/update.ps1 tools/update.cmd tools/m8/update-model.ps1   # no output
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **Migration `0013`:** upgrade, downgrade to `0012` (two source versions left, as before) and upgrade again exit 0; the head reads `0013_m9_news_feeds` with six source versions, and no public SQL or PL/pgSQL function is left without a fixed `search_path` (`0`; `27` after the downgrade).
- **The guard check:** on the scratch database, inside a rolled-back transaction, `ALTER FUNCTION asl_is_superuser() RESET search_path`, then as `asl_api` a temporary `pg_roles` holding `(current_user, true)`: `asl_is_superuser()` answered `t`. With the path pinned, the test's same steps answer false.
- **`test_m9_feeds.py` with `test_m6_source_units.py`:** `259 passed` (87 new cases, 10 of them on PostgreSQL). The changed `test_m6_source_units.py` case had failed against the new code before its change (`assert sorted(owned) == sorted(SEEDED)`), as expected.
- **The whole engine suite** on the final tree (21:32 to 22:16 UTC): `7 failed, 1461 passed, 16 warnings, 74 errors`. The 74 errors and three failures are `main`'s on this cluster, as M8's updates recorded them: `test_m1_account.py`'s 13 errors, the research store's 61, `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research` and `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds` (and no `test_m3_throughput` failure this time). `test_m6_sources.py::test_an_unreadable_time_or_an_unstorable_answer_never_leaves_a_request_running` was this change's: its stand-in reader did not take the receipt time the worker now passes, so the new backstop recorded `PARSE_FAILED` instead of `STORE_FAILED`; the stand-in now takes it. The other four were not: `test_m6_agents.py::test_an_investigation_refreshes_a_source_waits_without_the_slot_and_cites_what_it_was_given` hit a statement timeout while the no-database run shared the machine, and `test_m7_promotions.py`, `test_m7_schema.py` and `test_m8_check.py` each met `role "asl_agent" is not permitted to log in`, because a second harness run on another scratch database of the same cluster switched the shared roles off at its end. Run again alone afterwards, those five with `test_m9_feeds.py`: `92 passed`.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 825 passed, 344 skipped, 1 warning, 371 errors`, the same two failures as `main` (`test_api.py::test_status_requires_service_identity_and_ready_database`, `test_database.py::test_migrated_database_is_ready`), every error a database case (M8 update 3's 361 plus the 10 new).
- **The model test:** exit 0, `"failed":[]`, with the new expectation `the sources and the main run read out`; both PowerShell files parse with 0 errors and hold only ASCII.
- **Links:** `0 broken link(s)`.
- **Independent review** (a read-only subagent, no database): no blocking finding. Fixed, each with a test: an XML declaration naming an unknown encoding escaped as `LookupError`; calendar dates at the ends of Python's range escaped as `ValueError` or `OverflowError`; a line of two or more blanks between components failed the whole calendar; non-ASCII digits were read as times; a `Retry-After` on an answer that is not a limit still deferred the next poll; the read-out counted any approval as in force and waited for a fetcher whose flag is off. The worker now records any other fault of a reader as `PARSE_FAILED` (`PARSER_ERROR`) instead of leaving the request running. Left as it was: `plain_text`'s Markdown patterns can take seconds on a hostile 1 MiB description; changing them would change M6's stored extracts, and the answer cap bounds it.

**NOT RUN.** Anything on Docker; PostgreSQL 17; Windows PowerShell 5.1; the web checks and browser suites (no web file changed; the Evidence page lists sources generically); a fetch of any real feed by the app (the network here refuses the publishers; the PC's first fetch is printed by the update file). On the PC the update is the same double-click on `update-app.cmd` ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)).

## M8 update 3: the run the app keeps going — 2026-10-19

Scope: update 3 of [ExecPlan 0031 §9](plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) ([§15](plans/0031-m8-simple-app-that-runs-itself.md#15-progress)). Written by the project thread "Hands-off milestones" on branch `claude/hands-off-milestones-dsskxl` from `main` at `2834026`, on Linux with no Docker daemon. No command addressed the normal application or its database; on the owner's PC only the update records under `.cache/deployments` were read. `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** The scratch PostgreSQL 16 cluster on 127.0.0.1 port 55450 (`ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55450` and the scratch password files): first the database `asl_m1_m6_m8u3_mig` at `0012`, then, after the review's fixes changed `0012`, a fresh `asl_m1_m6_m8u3b`. From the repository root unless stated:

```bash
# Migration 0012 up, down and up again on a fresh database (services/engine)
createdb -h 127.0.0.1 -U asl asl_m1_m6_m8u3b
ASL_DB_NAME=asl_m1_m6_m8u3b ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m8u3b ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
ASL_DB_NAME=asl_m1_m6_m8u3b ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
# Engine (services/engine)
ASL_DB_NAME=asl_m1_m6_m8u3_mig .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests     # before the fixes
ASL_DB_NAME=asl_m1_m6_m8u3b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m8_runs.py \
    tests/test_m8_policy.py tests/test_m4_schema.py
ASL_DB_NAME=asl_m1_m6_m8u3b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_policy.py \
    tests/test_m7_evaluation.py tests/test_m7_binding.py tests/test_m3_throughput.py tests/test_m4_properties.py
ASL_DB_NAME=asl_m1_m6_m8u3b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_agents.py -k bar_close
ASL_DB_NAME=asl_m1_m6_m8u3b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m2_stream_continuity.py
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# Web (apps/web)
pnpm lint --ignore-pattern '.output/**' && pnpm typecheck && pnpm check && pnpm test && pnpm api:check && pnpm build
python3 tools/check_links.py .
```

Results, `OBSERVED`:
- **The whole engine suite** on the first commit's tree, before the review's fixes: `5 failed, 1373 passed, 16 warnings, 74 errors` (33 min). The 74 errors and three failures are `main`'s on this cluster, as update 2 recorded them: `test_m1_account.py`'s 13 errors and the research store's 61, `test_m3_throughput.py::test_only_the_replay_batch_commits_asynchronously_and_the_lease_stays_renewable`, `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research` and `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`. Two were new: `test_m4_schema.py::test_transition_guard_by_role` (`0012` let the execution identity stop a ready run of the reference; its guard now admits the app's moves only for a run of an operating policy, and the test passes) and `test_m2_stream_continuity.py::test_refresh_keeps_connected_and_transient_failure_fails_closed_without_rotation` (a market worker's task timed out while the review ran beside the suite; the module run alone gives `16 passed`).
- **Migration `0012`** on the fresh database: upgrade, downgrade to `0011` (no `AGENT_POLICY_V2` left) and upgrade again exit 0; the head reads `0012_m8_one_run`, and the check reads `detail -> 'flatten' = 'false'::jsonb`.
- **After the fixes**, on that database: `test_m8_runs.py`, `test_m8_policy.py` and `test_m4_schema.py` `27 passed`; the other targeted modules `1 failed, 133 passed` (the failure is `main`'s `test_m3_throughput` case above); the hourly trigger case `2 passed`; `test_m2_stream_continuity.py` `16 passed`.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 748 passed, 344 skipped, 1 warning, 361 errors`, the same two failures as `main` (`test_api.py::test_status_requires_service_identity_and_ready_database`, `test_database.py::test_migrated_database_is_ready`), every error a database case.
- **Web:** lint, typecheck, Prettier and `api:check` exit 0; `Test Files 24 passed (24)`, `Tests 266 passed (266)`; the build exit 0. **Links:** `0 broken link(s)`.
- **Browser** (B8a's procedure on this cluster, as update 2: a fresh `asl_m1_m6_m8u3_browser` at `0012`, `tests.m7_browser_fixture seed`, the API as `asl_api`, the production web build on port 4318 through `http://web:4318`, the preinstalled Chromium through a scratch Playwright configuration): M7's `@decisions` `12 passed (26.1s)`, its Experiments case now expecting `AGENT_POLICY_V2` among the policies offered and **Start run** for a policy's run. The API answered 188 `200`, two `404` and one `409`, the refusals the specs ask for, with no traceback. The servers were stopped and `/etc/hosts` restored; dropping the scratch databases was refused by the session's permission check, so `asl_m1_m6_m8u3b` and `asl_m1_m6_m8u3_browser` stay on the scratch cluster, which goes with the container.
- **Samples:** not rewritten. Regenerated after the browser run, they parse in the web unit tests, with `kept_by_app` on the manifests; three content expectations then fail as expected (two count the policies offered, now three, and one wants the open pause the specs had resumed). The repository keeps update 2's samples, and `approvals-page.test.tsx` covers a kept manifest.

**NOT RUN.** Anything on Docker; PostgreSQL 17; Windows PowerShell 5.1; R19 (`tests.m7_engine`, a replay database) and the M4, M5 and M6 browser suites (their fixtures need the Docker harness); the owner's PC until the third update, the same double-click on `update-app.cmd` ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)).

## M8 update 2: in-force records and latches that clear — 2026-10-19

Scope: update 2 of [ExecPlan 0031 §9](plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) ([§15](plans/0031-m8-simple-app-that-runs-itself.md#15-progress)). Written by the project thread "Hands-off milestones" on branch `claude/hands-off-milestones-dsskxl` from `main` at `18cdad3`, on Linux with no Docker daemon. No command addressed the normal application, the owner's PC or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** The scratch PostgreSQL 16 cluster on 127.0.0.1 port 55450 (`ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55450` and the scratch password files). From the repository root unless stated:

```bash
# Migration 0011 up, down and up again on a fresh database (services/engine)
dropdb -h 127.0.0.1 -U asl asl_m1_m6_m8u2_mig && createdb -h 127.0.0.1 -U asl asl_m1_m6_m8u2_mig
ASL_DB_NAME=asl_m1_m6_m8u2_mig ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_m8u2_mig ASL_DB_ROLE=migration .venv/bin/alembic downgrade -1
ASL_DB_NAME=asl_m1_m6_m8u2_mig ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
# Engine (services/engine)
ASL_DB_NAME=asl_m1_m6_m8u2_mig .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# Web (apps/web); lint before the build, or with --ignore-pattern '.output/**' while a build is there
pnpm lint && pnpm typecheck && pnpm check && pnpm test && pnpm api:check && pnpm build
python3 tools/check_links.py .
```

Results, `OBSERVED` on the final tree:
- **Migration `0011`:** upgrade, downgrade to `0010` and upgrade again exit 0; the head reads `0011_m8_in_force`.
- **Engine database tests:** the whole `tests` directory, `5 failed, 1360 passed, 16 warnings, 74 errors` (34 min). Two of the failures were older tests pinning what update 2 changes on purpose: `test_m3_roles.py::test_execution_role_cannot_fund_read_owner_clear_latches_or_rewind` (it set one flag, which `0011` now lets the execution identity clear when both end false; it now sets both and checks each flag alone is refused) and `test_m3_throughput.py::test_a_forward_step_reads_and_locks_exactly_what_it_did_before_run_state_reuse` (the approvals read now carries who recorded each row). Both pass after the change, run alone (`2 passed`). The other three failures and all 74 errors are `main`'s on this cluster, checked on `main` at `18cdad3` for the ones the earlier records do not name: `test_m3_throughput.py::test_only_the_replay_batch_commits_asynchronously_and_the_lease_stays_renewable` (a pooled connection keeps `synchronous_commit` off; also fails on `main`), `test_m1_account.py`'s 13 errors (they connect to the Docker host name `postgres`; also on `main`), and `test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research`, `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds` and the research store's 61 errors, as in update 1. Earlier in the work the targeted modules gave `16 passed` (`test_m8_in_force.py`, `test_m8_latches.py`) and, after their fixes, `25 passed` for `test_m5_schema.py`, `test_m5_runtime.py` and the changed `test_m6_api.py` case.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 743 passed, 334 skipped, 1 warning, 360 errors`, as `main` at `18cdad3` on the same tree layout (`2 failed, 741 passed, 329 skipped, 351 errors`, the same two failures: `test_api.py::test_status_requires_service_identity_and_ready_database` and `test_database.py::test_migrated_database_is_ready`) plus the 16 new database cases.
- **Web:** lint, typecheck, Prettier and `api:check` exit 0 (`Generated TypeScript API types match`); `Test Files 24 passed (24)`, `Tests 262 passed (262)`; the build exit 0.
- **Links:** `0 broken link(s)` in 104 Markdown files (the four known warnings of plan 0003).
- **Browser** (B8a's procedure on this cluster: a fresh `asl_m1_m6_m8u2_browser` at `0011`, `tests.m7_browser_fixture seed`, the API as `asl_api`, the production web build on port 4318 through `http://web:4318`, the preinstalled Chromium through a scratch Playwright configuration; all removed by exact name after): M7's `@decisions` `12 passed (26.5s)`, then `new-runner` (`PROBE_ONLY`, `CHECK_PENDING`, a second profile recorded by the app) and `@profile` `1 passed (4.2s)`. The API answered 205 `200`, two `404` and one `409`, the refusals the specs ask for, with no traceback.
- **The update file's record search** (after update 1 ran on the PC): its transcript showed the preflight parsing every file under `.cache/deployments`, dumps included (`ConvertFrom-Json` errors on `PGDMP`), because Windows PowerShell 5.1 ignores `-Include` beside `-LiteralPath`. `Get-PreviousCommit` and `Get-LastRecordFailed` now filter by name. With PowerShell 7.4.6 (`/opt/pwsh/pwsh`, not 5.1, where `-Include` works either way) a scratch script loaded both functions from the file's syntax tree over a scratch folder (an `update.json`, an older `m7-deploy.json`, a newer `COMPLETE` JSON under another name, a dump, a log, an `update-failed.json` with rollback tags): the previous commit is the `update.json`'s, then the `m7-deploy.json`'s once it is removed; the last record failed reads `False`, then `True`. The file parses and holds only ASCII, and the model test (`tools/m8/update-model.ps1`) exits 0 with `"failed":[]`.
- **Samples:** `tests.m7_browser_fixture samples` after the seed rewrote the 19 files of `apps/web/src/decisions/samples` from this API (the app's profile now comes first, and records carry who wrote them); the web unit tests pass on them and on the earlier ones (`262 passed` each), after `src/agents/controls.test.tsx` stopped assuming the first profile is the owner's.

**NOT RUN.** Anything on Docker; the M4, M5 and M6 browser suites (their fixtures need the Docker harness, whose profiles keep their older heads; from M8 the PC runs no harness); the owner's PC until its second update. On the PC the update is the same double-click on `update-app.cmd` as update 1 ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)); update 1 ran there 2026-10-19 17:01 to 17:13 UTC (`COMPLETE`, OBSERVED from its record).

## M8 update 1: the agents' check and the update file — 2026-10-19

Scope: update 1 of [ExecPlan 0031 §9](plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) ([§15](plans/0031-m8-simple-app-that-runs-itself.md#15-progress)). Written by the project thread "Hands-off milestones" on branch `claude/hands-off-milestones-dsskxl` from `main` at `0e47495`, on Linux with no Docker daemon. No command addressed the normal application or its database, except the read-only look at the PC's stored provider outcomes recorded in [0030 §14](plans/0030-agent-models-and-effort-per-role.md#14-progress-and-completion-evidence); `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** The scratch PostgreSQL 16 cluster on 127.0.0.1 port 55450 (`ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55450` and the scratch password files), the database `asl_m1_m6_m8u1_head` at `0010`. From the repository root unless stated:

```bash
# Engine (services/engine)
ASL_DB_NAME=asl_m1_m6_m8u1_head .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py tests/test_m8_*.py tests/test_generations.py
.venv/bin/ruff check .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests          # no database
# Runner (services/agent-runner)
PYTHONPATH=.:testing python3 -m unittest tests.test_units
PYTHONPATH=.:testing python3 -m unittest tests.test_process
# Web (apps/web); lint before the build, or with --ignore-pattern '.output/**' while a build is there
pnpm lint && pnpm typecheck && pnpm check && pnpm test && pnpm api:check && pnpm build
# The update file's model test (PowerShell 7.4.6 at /opt/pwsh/pwsh)
/opt/pwsh/pwsh -NoProfile -File tools/m8/update-model.ps1 -Repository . -Work <an existing scratch directory>
grep -nP '[^\x00-\x7F]' tools/update.ps1 tools/update.cmd tools/m8/update-model.ps1   # no output
python3 tools/check_links.py .
```

Results, `OBSERVED` on the final tree:
- **Engine database tests:** `2 failed, 1018 passed, 16 warnings, 61 errors` (14 min, with the review fix). The 2 failures (`test_m6_agents.py::test_priority_is_code_owned_probes_then_owner_then_promotion_then_triggers_then_research`, `test_m6_schema.py::test_downgrade_refuses_history_then_restores_only_m5_seeds`) and the 61 errors (the research store's server, which this cluster does not run) are the same names as on `main` at `0e47495` on the same cluster (`2 failed, 1008 passed`); the 10 new M8 cases pass.
- **Ruff** `All checks passed!`; **OpenAPI** `FastAPI OpenAPI schema matches`; **without a database** `2 failed, 741 passed, 329 skipped, 1 warning, 351 errors`, as `main` (`341 errors`) plus the 10 new database cases.
- **Runner:** `tests.test_units` 20 tests, `FAILED (failures=2, errors=1)`, the same three image-only tests as `main` (19 tests there); `tests.test_process` `OK (skipped=14)`.
- **Web:** lint, typecheck, Prettier and `api:check` exit 0; `Tests 251 passed (251)`; the build exit 0.
- **The model test:** exit 0, 10 scenarios and 32 expectations, `"failed":[]`; no non-ASCII byte in the three files; the parser reports 0 errors for both PowerShell files.
- **Links:** `0 broken link(s)` (the four known warnings of plan 0003).
- **Browser** (B8a's procedure on this cluster: a fresh `asl_m1_m6_m8u1_browser` at `0010`, `tests.m7_browser_fixture seed`, the API as `asl_api`, the production web build on port 4318 through `http://web:4318`, the preinstalled Chromium 141 through a scratch Playwright configuration; all removed by exact name after): M7's `@decisions` `12 passed (31.3s)`, then `revoke-profile` to `LOGIN_REQUIRED` and `@profile` `1 passed (4.4s)`. The fixture's own roles had their scratch passwords reset by its activation, as before.

**NOT RUN.** Anything on Docker; Windows PowerShell 5.1; the M5 browser suite (its fixture needs the Docker harness; its one changed line clicks Turn on instead of Allow probes), and the M6 and research browser suites; the owner's PC until its first update. On the PC the update is one double-click on `update-app.cmd` in the owner's main folder ([OPERATIONS](../OPERATIONS.md#the-update-file-m8)); it runs `tools/update.ps1` from GitHub's `main` with:

```bat
powershell.exe -NoProfile -ExecutionPolicy Bypass -File <a temporary copy of main's tools\update.ps1> -Repository <the folder>
```

## M8 part 1, the rules, documentation — 2026-10-19

Scope: part 1 of [ExecPlan 0031 §9](plans/0031-m8-simple-app-that-runs-itself.md#9-implementation-sequence) ([DECISIONS](../DECISIONS.md#2026-10-19--m8-part-1-the-rules-for-an-app-that-runs-itself-execplan-0031)). Written by the project thread "Hands-off milestones" on branch `claude/hands-off-milestones-dsskxl` from `main` at `9a4dd97`, on Linux with no Docker daemon. No command addressed the normal application, the owner's PC or any database.

**Documentation checks (actual).** From the repository root, on the branch after the edits:

```bash
python3 tools/check_links.py .
git diff --check origin/main...HEAD
```

Results: `check_links.py` found 0 broken links in 104 Markdown files (the four known pre-existing warnings in ExecPlan 0003), and `git diff --check` printed nothing. NOT RUN: the application checks, because no application file changed.

## A simple app that runs itself, documentation — 2026-10-19

Scope: the owner's messages of 2026-10-19, 11:08 to 11:15 UTC, and the owner's pick "Cut to essentials" at 11:37:19 UTC ([DECISIONS](../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)). The documents are [ExecPlan 0031](plans/0031-m8-simple-app-that-runs-itself.md) (approved for implementation), the M8 roadmap entries, the status notes on ExecPlans 0029 (withdrawn) and 0030 (trimmed), the plan list in README, a STATUS entry and this record.

Written by the project thread "Hands-off milestones" on branch `claude/hands-off-milestones-dsskxl` from `main` at `b7d51a6`, on Linux with no Docker daemon. No command addressed the normal application, the owner's PC or any database, and `.env`, `secrets/` and `codex_home` were not read. The plan's code facts were read from the files it cites at `b7d51a6`. Its sizes were counted on that tree with `grep -c '^@app.post' services/engine/app/main.py` (24), and with `wc -l` over `services/engine/app/**/*.py` (44,115) and over the 55 `.ps1`, `.psm1` and `.psd1` files under `tools/` (23,158), and `wc -w` over `docs/*.md docs/plans/*.md` (625,183).

**Documentation checks (actual).** From the repository root, on the branch after the edits:

```bash
python3 tools/check_links.py .
git diff --check
```

Results, on the branch after `main` at `2a9c240` was merged in and the pick recorded: `check_links.py` found 0 broken links in 103 Markdown files (the four known pre-existing warnings in ExecPlan 0003), and `git diff --check` printed nothing. NOT RUN: the application checks, because no application file changed. Every requirement of ExecPlan 0031 stays NOT RUN.

## ExecPlan 0026: the boundary and M7-B (2026-10-19)

OBSERVED on the owner's PC and reported by the PC session ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-boundary-m7-b-and-m7s-close-2026-10-19)). Two files of the PC session (not read here), which the owner double-clicked, ran these from the main folder on `09f4490`, each stopping at the first refusal (by the PC session's account), and put the folder back on its branch after. The arguments follow [OPERATIONS](OPERATIONS_M3_M7.md#m7-agent-driven-decision-operations-approved-contract-execplan-0026); the pilot's id in the first two is INFERRED, not reported:

```powershell
# start-boundary-m7.cmd, opened 09:38 UTC, waited for the HH:15 window
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\pilot-deactivate.ps1' -ExperimentId <the pilot>   # INFERRED d779fbf4-e1be-444c-ab55-7b61292eaa87; exit 0, 10:16:24 UTC
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-boundary.ps1' -ExperimentId <the pilot>       # INFERRED as above; exit 0, 10:17:59 UTC; COMPLETE (.cache\deployments\m7-boundary-20261019T101631Z)
# start-pilot-activate-m7.cmd, after the owner's approvals
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\pilot-activate.ps1' -ExperimentId a8b3ae07-0fe8-40b7-a59f-1a485c3dda43   # exit 0, 11:07:13 UTC
```

The approvals, the experiment, Start and Enable were the owner's, in the application. `NOT RUN`: the decision probes (a follow-up, [DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)). The PC session removed `m7-g1e`'s worktree after copying its evidence to `.claude\worktrees\m7-b0\.cache\m7\from-m7-g1e`.

## ExecPlan 0026: the gate passes, the release and research on (2026-10-19)

OBSERVED on the owner's PC and reported by the PC session ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-passes-on-m7-g1e-and-research-is-switched-on-2026-10-19)). The PC session's files (not read here), which the owner started by double-click, ran these from the main folder on `09f4490`, each in its window and each only after the step before it was `COMPLETE`:

```powershell
# 00:21 UTC: COMPLETE (.cache\deployments\m7-rollback-20261019T002119Z)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-deploy.ps1' -BaselineComposeFile <the pilot's baseline Compose file> -Rollback
# 05:27 UTC: COMPLETE (.cache\deployments\m7-deploy-20261019T052717Z)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-deploy.ps1' -BaselineComposeFile <the pilot's baseline Compose file>
# 06:10 UTC: exit 0 (backup research-activate-20261019T061005Z)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\research-activate.ps1'
```

The baseline Compose file each used is in its record; it is not copied here. `m7-g1e`'s phases ran as in the 2026-10-18 section below; its `Clean` removed 65 resources by exact name at 00:36 UTC. The owner's approvals and the capability probes followed in the application; the fourth run passed (§18). Next, PROPOSED and each the owner's: the live walk-through of [ExecPlan 0023 §13.3](plans/0023-m6-research-investigations.md#133-the-live-walk-through), then the boundary (§13.2) and M7-B (§13.3), with the commands of [OPERATIONS](OPERATIONS_M3_M7.md#m7-agent-driven-decision-operations-approved-contract-execplan-0026).

## Agent models and effort per role documentation — 2026-10-19

Scope: the owner's question of 2026-10-19 08:30 UTC on the agents' models and the delegation that followed ([DECISIONS](../DECISIONS.md#2026-10-19--the-owner-delegates-the-agents-model-choice-no-profile-change-during-m7s-switch-on)); [ExecPlan 0030](plans/0030-agent-models-and-effort-per-role.md) (PROPOSED), the sources in [REFERENCES](contracts/REFERENCES.md#model-and-effort-guidance--2026-10-19), the M8 roadmap line and this record. By the project thread "Agent setup and best models" on branch `claude/agent-model-review-vxjw87` from `main` at `66951e3`. Linux, no Docker daemon. No command addressed the normal application, the owner's PC or any database; `.env`, `secrets/` and `codex_home` were not read; no model was called by the application. The code facts in the plan were read from the files it cites at `66951e3`; the vendor facts from the pages REFERENCES lists, through a summarizing fetch.

**Documentation checks (actual).** From the repository root, on the branch after the edits:

```bash
python3 tools/check_links.py .
git diff --check
```

OBSERVED on the branch after the edits: `checked 102 Markdown files; 0 broken link(s)` with the four known historical warnings for absolute Windows links in ExecPlan 0003 (lines 21 and 130); `git diff --check` exited 0 with no output. A first pass found two wrong anchors in the new plan, fixed before this record.

NOT RUN: the documented read-only Docker run of the link checker (no Docker in the cloud), and the application checks (web lint, typecheck, unit tests and build, Ruff, the OpenAPI drift check, pytest), because no application file changed. Only Q07 documentation checking and Q10 source traceability apply; every requirement of ExecPlan 0030 stays NOT RUN.

## ExecPlan 0026: the gate run `m7-g1d` and its fix (2026-10-18)

`DecisionSaturation` failed on gate run `m7-g1d` on one line of the research runner's log, a lease renewal refused by its 2 s lock wait behind a batch ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1d-a-renewal-behind-a-slow-batch-2026-10-18)). Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (not acceptance evidence): the research fixture database on a second scratch PostgreSQL 16.15 cluster on 127.0.0.2 port 55450, which trusts local connections, so the password file is a placeholder; no Docker. `roomy` is a scratch pytest plugin, not committed, that reports 100 GiB free to `queue.storage` in that process, because this container has less than the research floor of 40 GiB free. From `services/engine`:

```bash
export PGPORT=55450 ASL_DB_HOST=127.0.0.2 ASL_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_ROLE=migration ASL_TEST_ISOLATED=1 \
  ASL_REPLAY_ISOLATED=1 ASL_RESEARCH_DB_HOST=127.0.0.2 ASL_RESEARCH_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_PASSWORD_FILE=<scratch>/pw
PYTHONPATH=$PWD:<scratch> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py -k slower_than_the_identity                 # on the code before the fix
PYTHONPATH=$PWD:<scratch> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py -k "slower_than_the_identity or long_batch"  # with the fix
PYTHONPATH=$PWD:<scratch> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py -k "renewal or heartbeat"   # after the review's fixes; once more with SET for SET LOCAL, reverted
PYTHONPATH=$PWD:<scratch> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
```

Results are in ExecPlan 0026 §18. The process-loss test of `test_m6_runner.py` fails here because its child process does not load `roomy` and cannot claim on this container's disk.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified ([DECISIONS](../DECISIONS.md#2026-10-18--the-owners-go-ahead-to-speed-up-m7-and-the-gates-rerun-on-the-renewal-fix)). `m7-g1d` runs `PerformanceResearch` only, not `PilotCoexistence`. Once it has ended (or at once, if it does not run), `m7-g1d` is stopped and cleaned up as its other runs were, its watch is ended by its end file (`.cache\m7\m7-g1d-seq.done`), and the worktree checks out the merged commit. Then, in Git Bash, one phase at a time:

```bash
cd /c/Users/owner/repos/adaptive-spot-lab/.claude/worktrees/m7-b0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase Prepare
# the owner starts the pilot watch for m7-g1e (below), then:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase ResearchRunner -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase Staging -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase DecisionSaturation -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase PilotCoexistence -WaitForWindow
# PerformanceResearch here too, only if it was not VERIFIED on m7-g1d (replaced by the owner's decision of 19:31 UTC: not run, see below)
# no Report: it refuses any run that started a gate phase (tools/m6/report.psm1); the evidence is the phase records
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId m7-g1e -Phase Clean
# the run is over: end its watch before the application update, which it would read as a change of the pilot
touch .cache/m7/m7-g1e-seq.done
until grep -q 'the run is over: the watch ends' .cache/m7/m7-g1e-pilot-watch.log; do sleep 30; done
```

**As set up on the PC after the merge** (OBSERVED there, reported 2026-10-18 about 15:35 UTC): `m7-g1e` was prepared on `09f4490` in a second worktree, `.claude\worktrees\m7-g1e`, so that `m7-g1d`'s tree is untouched while its `PerformanceResearch` runs; the commands above run from that worktree. A background script on the PC waits for the owner's `m7-g1e` watch and for the end of `m7-g1d`'s `PerformanceResearch`, then cleans up `m7-g1d` and runs `m7-g1e`'s phases one at a time. The owner starts that watch by double-clicking `.cache\m7\start-watch-m7-g1e.cmd` in the `m7-b0` worktree, which the PC session wrote. The line below was written for the `m7-b0` worktree before that setup, and that file takes its place.

**After the watch stopped `m7-g1d` at 19:18 UTC** (OBSERVED on the PC): the PC session cleaned up `m7-g1d` and cleared the stop files, and by the owner's decision of 19:31 UTC ([DECISIONS](../DECISIONS.md#2026-10-18--performanceresearch-counts-from-two-gate-runs-its-job-figures-from-m7-g1d-its-staging-figures-from-m7-g1a)) `m7-g1e` runs no `PerformanceResearch`. The owner started the watch again at 19:30:56 UTC with the PC session's watch for `m7-g1e`, run from the `m7-g1e` worktree with that worktree's end file `.cache\m7\m7-g1e-seq.done` and `-MaxHours 12` (the PC session offered its launcher file and its one-line command; which one the owner used is not recorded). At 19:36:02 UTC it stopped `m7-g1e` on a second `QUEUE_OVERLOAD` of the normal market worker. By the owner's decision of 20:16 UTC ([DECISIONS](../DECISIONS.md#2026-10-18--the-pilot-stops-before-the-rest-of-the-m7-gate-which-runs-without-the-pilot-watch)) the owner stops the pilot in the application and `m7-g1e`'s remaining phases run without a watch, so the watch command below is not run again for `m7-g1e`. For the same reason the block's line 28 (the watch) and its last two lines (`touch …m7-g1e-seq.done` and the `until grep …` wait for the watch's end line) are skipped for `m7-g1e`: with no watch running the wait would never end. `tools/pilot-deactivate.ps1` is not run before the application update: `tools/m7-deploy.ps1` refuses a deployment when a service named by `-ExpectedPilotImages` (the market, execution and evaluation workers) does not run on its expected image, and its after-check refuses when an open experiment (`READY` to `STOPPING`) changes during the run, so the deployment waits at least for `STOPPED`; the plan waits for `COMPLETED`.

**The rest of `m7-g1e`, without the watch** (OBSERVED on the PC, reported by the PC session, from the `m7-g1e` worktree with `Build` kept): `ResearchRunner` from 20:17:37 UTC, `VERIFIED` at 20:22; `Staging`, `VERIFIED` at 20:26; then `DecisionSaturation` (setup from 21:07 UTC), `PilotCoexistence` (from 23:07 UTC) and `Clean`, the block's lines 30 to 36, by the PC session's schedule (PROPOSED times). At 20:31:27 UTC the owner started the release file the PC session prepared, `.cache\m7\start-release-m7.cmd` in the `m7-b0` worktree (not read here; [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#m7-g1e-stopped-too-and-the-pilot-stops-first-2026-10-18)).

The owner's watch, in a second Git Bash window, can be started before the run is prepared: it waits for the run's manifest and then starts.

```bash
cd /c/Users/owner/repos/adaptive-spot-lab/.claude/worktrees/m7-b0 && until [ -f .cache/m7/m7-g1e/manifest.json ]; do sleep 60; done && powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m6-pilot-watch.ps1' -RunId m7-g1e -Harness m7 -MaxHours 16 -EndFile 'C:\Users\owner\repos\adaptive-spot-lab\.claude\worktrees\m7-b0\.cache\m7\m7-g1e-seq.done' -Execute
```

## ExecPlan 0026: the gate run `m7-g1c` and its fix (2026-10-18)

`DecisionSaturation` failed on gate run `m7-g1c`: every full test failed its holdout cell's report ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1c-a-report-with-an-entry-not-yet-filled-2026-10-18)). Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (not acceptance evidence): scratch PostgreSQL 16.15 on 127.0.0.1 port 55450, no Docker. The scratch scripts are the session's, not committed: `load.py` resets the replay database `asl_m1_replay_sp` and loads the saturation store's layout with `tests.m6_performance._load_dense`, seven days of part `a` from 2026-10-02 05:00 UTC and then one day of part `b` from 2026-10-09 05:00 UTC (its history hours overlap part `a` in time; its sequences follow part `a`'s); `job.py` hashes part `a`'s range, enqueues one full test of the held candidate at 8 hours (entry `CLOSE GT 0.0001` alone, stop 5, no signal exit) and runs it through `runner.run_once`, printing a failing cell's traceback. The cells named on its command line are replayed and the others answered with a stub. It reports 100 GiB free to `queue.storage` and claims in the quiet minutes, because this container has less than the research floor of 40 GiB free and a claim refuses between HH:58 and HH:07 UTC. Its first runs set the window to whole hours by hand; the later ones take the window `app.research.datasets.research_range` seals. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 PGPORT=55450 ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1
PYTHONPATH=$PWD .venv/bin/python <scratch>/load.py 1
PYTHONPATH=$PWD .venv/bin/python <scratch>/job.py '{"first_sequence": 1, "last_sequence": 1815038}'      # all six cells
PYTHONPATH=$PWD .venv/bin/python <scratch>/job.py '{"first_sequence": 1, "last_sequence": 1815038}' 4    # the holdout's H1 cell
PYTHONPATH=$PWD .venv/bin/python <scratch>/job.py '{"first_sequence": 1, "last_sequence": 1815038}' 4 5  # with the fix
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m4_evaluation.py   # before and after the fix
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
```

Results are in ExecPlan 0026 §18. `test_m6_runner.py`'s database tests are `NOT RUN` in this batch; they run in `ResearchRunner` on the PC.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. After the merge, a fresh gate run on the merged commit beside a pilot watch the owner starts, one phase at a time, in the order of `m7-g1c`: `Build`, `ResearchRunner` (the runner's log line changed), `Staging`, `DecisionSaturation`, `PerformanceResearch`, `PilotCoexistence`, then `Report`. The commands are those of the gate run `m7-g1b` below, with the new run's identifier. A feeder job is INFERRED to run about 660 to 720 s there, so `DecisionSaturation` may still fail as not showing staging beside a long job.

## Agent roles and coordinator idea documentation — 2026-10-18

Scope: the owner's request of 2026-10-18 09:06 UTC to record the idea of agent roles and a Coordinator agent as a note with suggestions ([note](ideas/agent-roles-and-coordinator.md)). By a cloud session on branch `claude/agent-roles-coordinator-note-mzb9cu` from `main` at `9917639`. Linux, no Docker daemon. No command addressed the normal application, the owner's PC or any database; `.env`, `secrets/` and `codex_home` were not read; no model was called by the application. The repository facts in the note were read from the files it links.

**Documentation checks (actual).** From the repository root, on a clean worktree of `main` at `9917639` and on the branch after the edits:

```bash
python3 tools/check_links.py .
git add -N docs/ideas && git diff --check
```

OBSERVED on `main`: `checked 99 Markdown files; 0 broken link(s)` with the four known historical warnings for absolute Windows links in ExecPlan 0003 (lines 21 and 130). OBSERVED on the branch: `checked 100 Markdown files; 0 broken link(s)` with the same four warnings; `git diff --check` exited 0 with no output, the new note included.

NOT RUN: the documented read-only Docker run of the link checker (no Docker in the cloud), and the application checks (web lint, typecheck, unit tests and build, ruff, the OpenAPI drift check, pytest), because no application file changed. Only Q07 documentation checking and Q10 source traceability apply; every suggestion in the note stays NOT RUN.

**Second pass, the enhancements E1–E4 (actual).** On the owner's "do it" (09:21 UTC), from `main` at `5e729a2` (after pull request 70), the same two commands. OBSERVED: `checked 100 Markdown files; 0 broken link(s)` with the same four warnings; `git diff --check` exited 0 with no output. The same NOT RUN list applies.

## ExecPlan 0026: the gate run `m7-g1b` and its two fixes (2026-10-18)

`DecisionSaturation` failed on its research side on gate run `m7-g1b` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1b-the-saturation-feeders-jobs-and-a-staging-read-that-runs-once-2026-10-18)). Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (not acceptance evidence): scratch PostgreSQL 16.15 on 127.0.0.1 port 55450, no Docker. The timing replays are scratch scripts of the session, not committed: `cells.py load` resets the replay database `asl_m1_replay_sp` and loads `tests.m6_performance._load_dense(admin, 7, T0)`, the saturation store's seven days; `cells.py run <candidate>` replays each of a full test's six cells (the protocol's partitions of those seven days, each cell's end the hold before its partition's end except the holdout's) from the first quote to the cell's end, with the experiment started at the cell's start and the driver's batch of 4,000 steps, as `app.research.runner.replay_cell` does without its fence; `collections.py load` adds one day as a second collection (`part="b"`), and `collections.py read` runs `EXPLAIN (ANALYZE, BUFFERS)` of the batch's collection read for each collection. After the review, `digest.py` times `app.research.datasets.content_digest` over the seven days three times, and `cells2.py run <candidate>` is `cells.py` with each cell's setup and its checks, fingerprint and evaluation after the replay timed as `replay_cell` runs them; `once_check.py` runs `staging._once` on a connection to `asl_m1_m7_speed` opened with `-c statement_timeout=2s`. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 PGPORT=55450 ASL_TEST_ISOLATED=1
ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD .venv/bin/python <scratch>/cells.py load
for c in ref29 always8s5 always12s5 always6s5; do
  ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD .venv/bin/python <scratch>/cells.py run $c
done
ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD:$PWD/tests .venv/bin/python <scratch>/collections.py load
ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD:$PWD/tests .venv/bin/python <scratch>/collections.py read
# the scratch cluster restarted (pg_ctl restart -m fast) and 3 written to /proc/sys/vm/drop_caches, then the read again
ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD .venv/bin/python <scratch>/digest.py
for c in ref29 always8s5; do
  ASL_DB_NAME=asl_m1_replay_sp ASL_REPLAY_ISOLATED=1 PYTHONPATH=$PWD .venv/bin/python <scratch>/cells2.py run $c
done
ASL_DB_NAME=asl_m1_m7_speed PYTHONPATH=$PWD .venv/bin/python <scratch>/once_check.py
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
```

The held candidate was checked through `_measured_candidate` on `asl_m1_m6_m7_b7r` from a short Python snippet. Results are in ExecPlan 0026 §18. `test_m6_staging.py`'s database tests are `NOT RUN`: they read the catalog's secrets under `/run/secrets`, which this session does not read.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. The owner chose the staging fix on the thread's card ([DECISIONS](../DECISIONS.md#2026-10-18--the-two-staging-reads-that-run-once-get-a-20-s-bound)). After the merge, a fresh gate run on the merged commit beside a pilot watch the owner starts, one phase at a time: `Staging` (the staging change's database tests) before the gate's phases, then `DecisionSaturation` first of those. In Git Bash, from the PC session's worktree:

```bash
cd /c/Users/owner/repos/adaptive-spot-lab/.claude/worktrees/m7-b0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Build -WaitForWindow
# the owner starts the pilot watch for <run> (tools\m6-pilot-watch.ps1 -RunId <run> -Harness m7 ... -Execute), then, one at a time:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase ResearchRunner -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Staging -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase DecisionSaturation -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase PerformanceResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase PilotCoexistence -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Report
```

`Staging` is a phase of the M7 profile (`tools/profiles/m7.psd1`: M6's `Staging`, on two fixture clusters, in a 15-minute window) and runs `test_m6_staging.py` with its two new database tests. Report refuses only an M7-A run that starts a phase of the activation gate (`tools/m6/report.psm1`), not a gate run that starts `Staging`, so it runs on the gate run after `ResearchRunner`, as `ResearchRunner` ran on `m7-g1a` and `m7-g1b`.

## ExecPlan 0025: the constant costs of a held step (2026-10-18)

The seven changes of [ExecPlan 0025 §5.9](plans/0025-research-job-cost-and-search.md#59-the-constant-costs-of-a-held-step-added-2026-10-18-after-gate-run-m7-g1a), after gate run `m7-g1a` projected the shadow advance over 21 days at 3,781.4 s against 3,600. Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (not acceptance evidence): scratch PostgreSQL 16.15 on 127.0.0.1 port 55450, no Docker. From `services/engine`:

```bash
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
export ASL_DB_HOST=127.0.0.1 PGPORT=55450 ASL_TEST_ISOLATED=1
ASL_DB_NAME=asl_m1_m7_speed .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs tests/test_m1_unit.py tests/test_m2_*.py tests/test_m3_*.py tests/test_m4_*.py
ASL_DB_NAME=asl_m1_m7_speed .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs tests/test_m3_throughput.py
ASL_DB_NAME=asl_m1_m6_m7_b7r .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py tests/test_generations.py
PYTHONPATH=$PWD:<plugin dir> ASL_DB_HOST=127.0.0.2 ASL_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_ROLE=migration ASL_REPLAY_ISOLATED=1 ASL_RESEARCH_DB_HOST=127.0.0.2 ASL_RESEARCH_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_PASSWORD_FILE=<pw> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py
```

Results, after the independent review's fixes, are in [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1a-and-the-held-steps-cost-2026-10-17-and-18): ruff and the OpenAPI check pass; the database-free pytest `2 failed, 736 passed, 329 skipped, 337 errors` (tests that need a database); M1 to M4 `322 passed`; `test_m3_throughput.py` `29 passed`; M5 to M7 `3 failed, 1003 passed, 57 errors` (two fail the same way on `main`, one passed alone, the errors need a research replay database); `test_m6_runner.py` on the research fixture database (`127.0.0.2`, a second scratch cluster; `roomy` is a scratch plugin, not committed, that reports 100 GiB free to `queue.storage` in that process, because this container has less than the research floor of 40 GiB) `1 failed, 29 passed`, the process-loss test, whose child process cannot claim here. `test_m6_shadows.py`, `test_m6_staging.py`, `test_m6_bridge.py` and `test_m7_control_bridge.py` are `NOT RUN`: they read the catalog's secrets under `/run/secrets`, which this session does not read. A research claim refuses between HH:58 and HH:07 UTC, so a run of the runner's file in that window fails its first replay test.

The timing replay (ExecPlan 0025 §14) is a scratch script of the session, not committed: it loads `tests/m3_density.py`'s seven-day fixture into `asl_m1_replay_sp` with `ASL_REPLAY_ISOLATED=1`, pins the code identity, and replays 64 hours with the research runner's batch, alternating a checkout of `main` at `5b9987b` and the changed tree.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. A fresh gate run on the merged commit, beside a pilot watch the owner starts, one phase at a time so that each result is read before the next starts, `DecisionSaturation` first because it has never run on Docker. In Git Bash, from the PC session's worktree:

```bash
cd /c/Users/owner/repos/adaptive-spot-lab/.claude/worktrees/m7-b0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Prepare
# the owner starts the pilot watch for <run> (tools\m6-pilot-watch.ps1 -RunId <run> -Harness m7 ... -Execute), then, one at a time:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase ResearchRunner -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase DecisionSaturation -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase PerformanceResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase PilotCoexistence -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'tools\m7-acceptance.ps1' -RunId <run> -Phase Report
```

## ExecPlan 0026: `DecisionSaturation` in the activation gate (2026-10-17)

`DecisionSaturation` is the condition of the M7-B activation in [ExecPlan 0026 §10](plans/0026-m7-agent-driven-main-decisions.md#10-verification-commands-proposed-not-implemented): the engine with intake keeps its step budget, and market publication its own, while the agent worker and the research services work at their limits. By the [owner's decision of 2026-10-17](../DECISIONS.md#2026-10-17--decisionsaturation-replaces-researchsaturation-in-the-m7-activation-gate) ("Combined") it replaces `ResearchSaturation` in the M7 profile's activation gate, which the owner's decision of 2026-10-08 had required before the M6-B activation ([OPERATIONS](OPERATIONS_M3_M7.md#m6-research-operations-approved-contract-execplan-0023)); `ResearchSaturation` is no longer a phase of `tools/m7-acceptance.ps1`. It keeps that phase's research, stream and fetcher load at the same limits, judged the same way, and replaces its execution fixture with `PerformanceEngine7`'s policy engine, feed and agent desk, judged on `PerformanceEngine7`'s budgets with intake; beside them the production agent worker, in a container of the product `agent-worker` service inside its limits, works through a UTC day's generation-3 `DECISION` and `BRIEF` budgets (36 decisions, 4 briefs) inside the loaded thirty minutes ([TESTING](TESTING.md#m7-activation-gate-decisionsaturation)). Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (not acceptance evidence): no Docker, no CPU or memory limit, scratch PostgreSQL 16.15 on 127.0.0.1 port 55450, no research, stream or engine load beside it, and the loaded thirty minutes written by hand into `/perf/ready.json` (`measured_from` 18:19:31, `measured_until` 18:49:31 UTC) in place of the policy feed. `<pw>` is a scratch file the local trust authentication ignores. From `services/engine`:

```bash
export PYTHONPATH=$PWD ASL_DB_HOST=127.0.0.1 PGPORT=55450 ASL_TEST_ISOLATED=1
ASL_DB_ROLE=migration ASL_DB_PASSWORD_FILE=<pw> ASL_DB_NAME=asl_m1_m5_m6_cloud_saturation .venv/bin/python -m tests.m7_saturation prepare asl_m1_m7_cloud_agents
ASL_DB_ROLE=migration ASL_DB_PASSWORD_FILE=<pw> ASL_DB_NAME=asl_m1_m7_cloud_agents .venv/bin/python -m app.research.migrate
export ASL_AGENTS_OFFLINE_TEST=1 ASL_DB_NAME=asl_m1_m7_cloud_agents
ASL_DB_ROLE=migration ASL_DB_PASSWORD_FILE=<pw> .venv/bin/python -m tests.m7_saturation agent-load 2700 &
ASL_DB_ROLE=agent .venv/bin/python -m tests.m7_saturation agent-worker 2500 &
```

`prepare` created the database and refused a second time and under a name outside `asl_m1_m7_*_agents`. The worker held the lease in one epoch from 18:18:01. By 18:30:12 UTC, twelve minutes after the worker started, the day's budgets were spent: 36 `PORTFOLIO_DECISION_V1` (35 the load's, one from the scheduler's reviewed brief) with 36 `INTENT_REVIEW_V1`, and 4 `MARKET_BRIEF_V1` (3 the load's, one the scheduler's) with 4 `BRIEF_REVIEW_V1`, all `SUCCEEDED`; the one more of each that the load queued ended `EXPIRED` `DAILY_BUDGET_EXHAUSTED`; 36 submissions, 36 answered; none failed. A decision took 16.2 s (p50 16.16, max 16.27) and a brief 11.7 s. The worker's record: 751 ticks, tick p95 100.1 ms and p99 116.18 ms, peak RSS 78.9 MiB, no failure, `passed` true. The load was stopped at 18:31 UTC by hand; its own final reading had a fault (a column named `ended_at`, which is `finished_at`), since fixed, and the fixed `read`, with the stricter verdict of the independent review (every chain started must succeed, a submission for each decision), run afterwards on the same database answered `"problems": []`, `"passed": true`; with one decision's row read as `EXPIRED` `DEADLINE_EXCEEDED` and one answer left out it named both problems. The worker, as role `agent` without `ASL_DB_PASSWORD_FILE`, read its password from the cluster's `/run/secrets` file, which the local trust authentication ignores.

From the repository root, after the review's fixes: `/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c` exit 0, "profiles/m7.psd1 is consistent (48 phases, 0 not built)"; the five changed PowerShell files parse without errors and are ASCII (PowerShell 7.4.6 on Linux, not Windows PowerShell 5.1); `python3 tools/check_links.py .` "0 broken link(s)"; from `services/engine`, `.venv/bin/ruff check --no-cache app tests alembic` and `.venv/bin/python -m app.export_openapi --check` pass.

**`NOT RUN`:** the phase on Docker: the agent worker at 0.5 CPU and 256 MiB, beside the research, stream, fetcher and policy-engine load, on PostgreSQL 17. At 0.5 CPU and with that load a decision may take longer than the sixteen seconds measured here (INFERRED, unmeasured). The workflows run one at a time, so the budgets are spent in time while a decision takes at most about 48 s (the thirty minutes less four briefs, over 36 decisions; the author's arithmetic): three times what was measured here. If they are not, the phase fails and says how many started.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. As the gate's commands below: `Prepare`, `Build`, `ResearchRunner`, `PerformanceResearch`, `DecisionSaturation` and `PilotCoexistence` on a fresh run of their own beside the pilot watch. To rerun just this phase on a run whose `Build` passed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase DecisionSaturation -WaitForWindow
```

## ExecPlan 0026 after B10: the M6-B gate on the M7 build (2026-10-17)

Under M7-OD10 (b) research is activated on the M7 installation, so M6-B's three gate phases must pass on the M7 build ([OPERATIONS](OPERATIONS_M3_M7.md#m6-research-operations-approved-contract-execplan-0023)). The M7 profile now holds them as its activation gate, with M6's values; `PilotCoexistence` migrates to the profile's head (`0009`). Nothing here addressed the normal application.

**Actual, in the cloud session that builds M7** (PowerShell 7.4.6 on Linux, not Windows PowerShell 5.1; not acceptance evidence), from the repository root:

```bash
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
```

Exit 0: "VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at 7b3e52c and their values; profiles/m7.psd1 is consistent (47 phases, 0 not built)." `tools/profiles/m7.psd1`, `tools/m7-acceptance.ps1`, `tools/m6/rollout.psm1`, `tools/m6/report.psm1` and `tools/lib/acceptance-harness.ps1` parse without errors (`[System.Management.Automation.Language.Parser]::ParseFile`) and hold only ASCII (`grep -nP '[^\x00-\x7F]'`, no match).

The candidate refusals `PilotCoexistence` asks of a main-shaped database, on schema `0009` (scratch PostgreSQL 16.15 on 127.0.0.1 port 55450; `asl_m1_m5_m6_m7gate_pilot` is a scratch database made for this, created empty as `asl_m1_m7_gate` and renamed to the name the helper accepts; `<pw>` is a scratch file the local trust authentication ignores). From `services/engine`:

```bash
export PYTHONPATH=$PWD ASL_DB_HOST=127.0.0.1 PGPORT=55450 ASL_DB_NAME=asl_m1_m5_m6_m7gate_pilot ASL_TEST_ISOLATED=1 ASL_DB_PASSWORD_FILE=<pw>
ASL_DB_ROLE=migration .venv/bin/python -m app.research.migrate
ASL_DB_ROLE=migration .venv/bin/python -m tests.m6_rollout refusals
```

The migration ended "VERIFIED: migration completed in 1 bounded attempt(s)" at `0009_m7_agent_decisions`; the refusals answered every one of the eight answers the phase requires (`candidate_requires_isolated_research_database` twice, `CONSTRUCTED` for the reference strategy, `candidate_requires_research_replay` three times, `candidate_manifest_requires_historical_research` twice), with `"problems": []` and the execution definitions unchanged at 9.

**`NOT RUN`:** `Report` with the new `GateActivation` (no run here to report on), `-Describe` of the three phases (the harness refuses any PowerShell but Windows PowerShell 5.1), and the three phases on Docker. The part reservations of `PerformanceResearch` are unchanged: nothing has measured them on the M7 build yet.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, on a fresh run of its own (the gate phases may not share an M7-A run), beside the pilot watch with `-Harness m7`, whose `-Execute` the owner asks for in chat. `ResearchRunner` goes first, because the renewal fix of pull request 63 changed the runner and has not run on PostgreSQL 17; each later phase starts only after the one before it passed, and the next waits for its window:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId <run> -Harness m7 -MaxHours 24 -EndFile <file that ends it> -Execute
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase ResearchRunner -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase PerformanceResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase DecisionSaturation -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase PilotCoexistence -WaitForWindow
```

**The normal application on the gate's commit, before the activation.** PROPOSED and `NOT RUN`; only on the owner's approval in chat. `tools/research-activate.ps1` starts the images already built (`--no-build`), and B10 built every image at `05d8ef9`, before pull request 63. Rebuilding only the research and source images is **not** enough (independent review, 2026-10-17): the code identity is one hash over the engine's whole `app/` tree, the agent worker requests a job with its own identity (`app/agents/tools/experiments.py:60-62`), and the queue refuses a job whose identity is not the runner's (`app/research/queue.py:106`, `CODE_IDENTITY_MISMATCH`). With a new runner beside the old agent worker every experiment an agent requests would end `FAILED`.

The whole release is therefore replaced with the existing script, in the order `BoundaryRehearsal` runs it (its step 1, `VERIFIED` on Docker in run `m7-b9c`, but isolated: all three runs from one tree, with `-Rehearsal`, which skips the windows and the clean-tree check, and on synthetic data; the real sequence across two commits is `NOT RUN`): `tools/m7-deploy.ps1 -Rollback` returns the installation to the M6-A release on `0008` (valid while research is off and no M7 record exists: both scripts' preflights require the installation inert, and the rollback refuses M7 records, which exist after the boundary), then `tools/m7-deploy.ps1` deploys M7 again from the gate's commit, which builds every image of the release from one tree. As for B10, the owner's main folder (`<repo>`) is switched to that commit, clean, and back afterwards to the branch read before the switch. Windows PowerShell 5.1 from `<repo>`; with api, web and agent-worker running the rollback is not a repair, so it begins between HH:15 and HH:45 UTC and its backup must end before HH:45; the deployment begins between HH:15 and HH:35. If the rollback ends after HH:35, or the deployment refuses, the application runs the M6-A release on `0008` until the deployment runs in a later hour; nothing of the pilot changes either way:

```powershell
git -C <repo> branch --show-current
git -C <repo> status --porcelain
git -C <repo> checkout --detach <commit>
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-deploy.ps1 -BaselineComposeFile .cache\deployments\m6-baseline-compose-ec1d78b.yaml -Rollback
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-deploy.ps1 -BaselineComposeFile .cache\deployments\m6-baseline-compose-ec1d78b.yaml
git -C <repo> checkout <the branch read first>
```

`status` must print nothing before the switch. Both records must end `COMPLETE`; the second is then the newest, so `tools/m7-boundary.ps1` must run from a checkout of that commit. After the boundary M7 records exist and `-Rollback` refuses ("fix forward"): a later change to the running release would need an update of the M7 installation on `0009`, which the script does not have.

## GitHub CI removal — 2026-10-17

Scope: the removal recorded under the [owner's decision](../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository). By a cloud session on branch `claude/remove-github-ci-vztuco` from clean `main` at `05d8ef9`. Linux, no Docker daemon. No command addressed the normal application, the owner's PC or any database; `.env`, `secrets/` and `codex_home` were not read; no repository setting was changed.

**The removal (actual).**

```bash
git rm .github/workflows/ci.yml .github/dependabot.yml tools/ci/compose.images.yaml
git grep -nI -E "\.github/workflows|dependabot|tools/ci|compose\.images" -- ':!docs/COMMANDS.md' ':!docs/STATUS.md'
git grep -nI "tools/ci\|compose.images" -- compose.yaml tools services apps
```

OBSERVED: the three files were the whole of `.github/` and `tools/ci/`. After the edits the first search finds only historical records and the entries that describe the removal; the second finds nothing, so no Compose file, tool or application file used the override.

**Documentation checks (actual).** From the repository root, on `05d8ef9` and after the edits:

```bash
python3 tools/check_links.py .
git diff --check
```

OBSERVED on `05d8ef9`: `checked 99 Markdown files; 0 broken link(s)` with the four known historical warnings for absolute Windows links in ExecPlan 0003 (lines 21 and 130). OBSERVED after the edits: the same result and warnings; `git diff --check` exited 0 with no output.

NOT RUN: the documented read-only Docker run of the link checker (no Docker in the cloud), and the application checks (web lint, typecheck, unit tests and build, Ruff, the OpenAPI drift check, pytest), because no application file changed. To restore CI later: `git checkout 05d8ef9 -- .github tools/ci`, then follow [ExecPlan 0016 §8](plans/0016-ci-checks.md#8-progress-and-evidence) (PROPOSED, not run).

## Builder and LLM-trading findings documentation — 2026-10-17

Scope: the documentation round recorded under the [owner's instruction](../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements): PROPOSED M8 analyses, M9-R25–R28, M10-R17 and the shared records, plus the optional read-only warm-up measurement. By a cloud session on branch `claude/research-findings-m8-m10-0tu7p0` from clean `main` at `400de44`. Linux, no Docker daemon. No command addressed the normal application, the owner's PC or any database; `.env`, `secrets/` and `codex_home` were not read; no model was called by the application. Source pages were opened with the session's web-fetch tool, not with a command ([evidence](contracts/INTEGRATION_EVIDENCE.md#builder-and-llm-trading-findings--2026-10-17)).

**The measurement (attempted; NOT RUN).** Public market data only, no credentials:

```bash
curl -sS -m 20 -o /dev/null -w '%{http_code}\n' 'https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=2'
curl -sS -m 20 -o /dev/null -w '%{http_code}\n' 'https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h&limit=2'
for h in data.binance.vision api1.binance.com api.binance.us; do curl -sS -m 15 -o /dev/null -w '%{http_code}' "https://$h/"; done
curl -sS "$HTTPS_PROXY/__agentproxy/status"
```

OBSERVED: every request ended `curl: (56) CONNECT tunnel failed, response 403` with code `000`; the proxy status lists each host as `connect_rejected` ("gateway answered 403 to CONNECT"). The session's network policy denies the hosts, so the measurement is NOT RUN and no script was written. It belongs to early M8, whose plan records its own commands.

**The arithmetic (actual).**

```bash
python3 -c "
for n in (100,150,200,300,720):
    print(n, 'ema50 %.4f%%'%(100*(49/51)**(n-50)), 'ema20 %.5f%%'%(100*(19/21)**(n-20)), 'atr14 %.4f%%'%(100*(13/14)**(n-15)))
print('ema200 at 200,300', (199/201)**0, (199/201)**100)
"
```

OBSERVED: EMA(50) 13.5299%, 1.8306%, 0.2477%, 0.0045% and 0.0000% at 100, 150, 200, 300 and 720 bars; ATR(14) 0.1838% at 100; EMA(200) 1.0 at 200 and 0.36788 at 300.

**Documentation checks (actual).** From the repository root, before the edits on `400de44` and after them:

```bash
python3 tools/check_links.py .
git diff --check
```

OBSERVED before the edits: `checked 99 Markdown files; 0 broken link(s)` with the four known historical warnings for absolute Windows links in ExecPlan 0003 (lines 21 and 130). OBSERVED after the edits: the same `checked 99 Markdown files; 0 broken link(s)` and the same four warnings; `git diff --check` exited 0 with no output. The new sections' anchors are among those checked. After the fixes from an independent read-only review of the first commit, both commands were run again with the same results.

NOT RUN: the documented read-only Docker run of the link checker (no Docker in the cloud), and the application checks (web lint, typecheck, unit tests and build, ruff, the OpenAPI drift check, pytest), because no application file changed. Only Q07 documentation checking and Q10 source traceability apply to this round; every new requirement stays NOT RUN.

## Agent readiness documentation — 2026-10-16

Scope: researched documentation refinement of existing M9/M10, the M8 prerequisite closure, canonical future evaluation requirements, and linked roadmap/acceptance/decision/source/evidence/status records. Started from clean `main` at `0a7866bddc1c18c27c97660a9b3b3e4def8fd1ee`. A sandboxed `git switch -c codex/m9-m10-readiness` failed to create its ref lock; the permission retry succeeded. No application implementation, normal-app operation, provider call or publication belongs to this delivery.

OBSERVED setup: the sandboxed image inspection could not access Docker Desktop's named pipe. The permission retry for the bounded documentation container succeeded. A subsequent image inspection returned cached image ID `sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0`; `--pull never` fetched no image. The read-only repository mount is for this authoring check, not exposed to a runtime agent. No app container or database was addressed.

Executed documentation commands:

```powershell
$m9ReadinessArgs = @(
  'run', '--rm', '--pull', 'never', '--name', 'asl-m9-m10-readiness-docs-20261016',
  '--network', 'none', '--read-only', '--tmpfs', '/tmp',
  '--cpus', '0.5', '--memory', '256m', '--pids-limit', '64',
  '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
  '-e', 'PYTHONDONTWRITEBYTECODE=1',
  '-v', 'C:\Users\owner\repos\adaptive-spot-lab:/repo:ro',
  'python:3.13.11-slim-bookworm', 'python', '/repo/tools/check_links.py', '/repo'
)
docker @m9ReadinessArgs
git diff --check
docker ps -a --filter 'name=^/asl-m9-m10-readiness-docs-20261016$' --format '{{.Names}}'
docker image inspect python:3.13.11-slim-bookworm --format '{{.Id}}'
```

VERIFIED first documentation pass: container exit 0, `checked 99 Markdown files; 0 broken link(s)`, with four unchanged historical Windows-path warnings in ExecPlan 0003. Whitespace check exited 0. Exact-name container lookup returned no names, confirming cleanup. Requirement-table review found 24 M9 rows and 16 M10 rows, with sequence/acceptance references updated. Diff review found only 11 existing Markdown files; no acceptance checkbox, application file, approved protocol hash or runtime setting changed.

Review refinements: clarified safety checks before activation versus forward evidence collected during authorized observation; retained status lookup or idempotent retry for unknown outcomes; recorded unavailable provider model provenance rather than demanding an invented exact version; declared intentional experimental differences in matched comparisons. VERIFIED closing pass with the same Docker command: 99 Markdown files, zero broken links, the same four historical warnings, exit 0 and no remaining exact-name container. The closing whitespace check also exited 0; changed paths remain documentation only.

All application, actual-model, database, performance, financial, remote CI, deployment and activation checks remain NOT RUN. Only Q07 documentation checking and Q10 specification/source consistency apply to this edit. Source retrieval and Markdown checks do not establish operational quality or profitability.

## M9/M10 documentation refinement — 2026-10-16

Scope: refine [ExecPlan 0027](plans/0027-m9-market-intelligence-and-event-driven-trading.md), add future [ExecPlan 0028](plans/0028-m10-coin-discovery-and-controlled-expansion.md), and update roadmap/index/acceptance/decision/status/source evidence. Started from clean `main` at `6bfe21ab85462e3b1df7f8f2ecd06ebb3bc66a06`; work is on `codex/m9-m10-roadmap`. Only documentation editing and its checks are authorized here. No application build/test, normal-app operation, source activation or deployment belongs to this record.

OBSERVED setup: sandboxed `git switch -c codex/m9-m10-roadmap` could not create its ref lock; the permission retry succeeded. An initial `docker image inspect python:3.12-alpine --format '{{.Id}}'` could not access Docker Desktop's named pipe; it does not establish that the image was absent. The permission retry using the previous documentation check's cached `python:3.13.11-slim-bookworm` succeeded and returned image ID `sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0`. No image was pulled and no app container was addressed.

VERIFIED command using the existing checker and cached image after the Docker permission retry. The repository mount is read-only for this authoring check, not exposed to a runtime agent; there is no network, secret mount or database:

```powershell
$m9m10DocsArgs = @(
  'run', '--rm', '--pull', 'never', '--name', 'asl-m9-m10-docs-20261016',
  '--network', 'none', '--read-only', '--tmpfs', '/tmp',
  '--cpus', '0.5', '--memory', '256m', '--pids-limit', '64',
  '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
  '-e', 'PYTHONDONTWRITEBYTECODE=1',
  '-v', 'C:\Users\owner\repos\adaptive-spot-lab:/repo:ro',
  'python:3.13.11-slim-bookworm', 'python', '/repo/tools/check_links.py', '/repo'
)
docker @m9m10DocsArgs
git diff --check
git diff --no-index --check -- NUL docs/plans/0028-m10-coin-discovery-and-controlled-expansion.md
docker ps -a --filter 'name=^/asl-m9-m10-docs-20261016$' --format '{{.Names}}'
```

VERIFIED: container exit 0, `checked 99 Markdown files; 0 broken link(s)`. Four unchanged historical warnings concern absolute Windows links in ExecPlan 0003 at lines 21 and 130. `git diff --check` exited 0. The untracked-plan no-index check exited 1 for the new-file difference with no whitespace-error diagnostics; Git emitted its LF-to-CRLF conversion warning. The exact-name container query exited 0 with no names, confirming `--rm` cleanup. Review of the changed-file list found only the nine existing Markdown documents and the new M10 plan; no app/configuration file was edited.

This is documentation evidence for the scoped Q07/Q10 checks. Earlier M9 results below remain historical. Link checking validates local Markdown targets/anchors, not remote provider behavior or implementation; all M9/M10 application/provider/evaluation/deployment checks remain NOT RUN. Application Q01–Q10 gates stay open for their implementation milestones.

### M9/M10 publication preparation — 2026-10-16

OBSERVED owner instruction: “Create pr and merge it”. This authorizes committing, publishing and merging the ten-file documentation update on `codex/m9-m10-roadmap`. It does not authorize application implementation, deployment, source activation or trading changes.

VERIFIED remote baseline: `git fetch origin main` succeeded with the network/filesystem permission retry. `origin/main` remains `6bfe21ab85462e3b1df7f8f2ecd06ebb3bc66a06`; `git rev-list --left-right --count HEAD...origin/main` returned `0 0` before committing. The GitHub connector could not access this repository, and the sandboxed GitHub CLI could not connect; the authenticated CLI permission retry succeeded. `gh pr list --repo MentorAliu/adaptive_spot_lab --head codex/m9-m10-roadmap --state all --json number,state,title,url` returned no existing PR. Repository metadata confirms normal merge commits are allowed and `main` is unprotected. No force push or administrator bypass is part of this publication.

OBSERVED CI limitation on the unchanged base: the latest three `main` runs ended in `startup_failure`. The latest, [run 38747979626](https://github.com/MentorAliu/adaptive_spot_lab/actions/runs/38747979626), has path `BuildFailed` and no jobs or check runs; `gh run view` reports a likely workflow-file issue, without a precise diagnostic. This is not evidence of passing or failing application tests. The new PR's actual check state must be reported separately; no workflow changes are included in this documentation PR.

VERIFIED publication check: repeated the read-only/network-disabled Docker link command above with container name `asl-m9-m10-pr-docs-20261016`; exit 0, `checked 99 Markdown files; 0 broken link(s)`, the same four historical warnings. `git diff --check` exited 0; the new-plan no-index check had no whitespace-error diagnostics (exit 1 for the new-file difference, with the existing LF-to-CRLF warning). The exact-name `docker ps -a` query returned no container. Commit/PR/merge completion is not asserted by this preparation entry.

## M9 roadmap documentation — 2026-10-15

Scope: [ExecPlan 0027](plans/0027-m9-market-intelligence-and-event-driven-trading.md) and its roadmap, index, decision, status, acceptance and source-reference links. Documentation only on `claude/m6-performance` from `50ef1c0`; no application build/test, migration, normal-app command or activation is part of this record.

OBSERVED initial sandboxed image lookup: `docker image inspect python:3.13.11-slim-bookworm --format '{{.Id}}'` could not connect to Docker Desktop's named pipe (permission denied). This is a documentation-check transport limitation, not an application failure or evidence that the image is missing.

VERIFIED bounded check, using the existing checker and cached image only, after the sandbox permission retry. The explicit container name is disposable; `--rm` removes it after completion. The repository is mounted read-only for this authoring check, not exposed to a runtime agent. No network, pull, secret mount, database or normal application service is used:

```powershell
$m9DocsArgs = @(
  'run', '--rm', '--pull', 'never', '--name', 'asl-m9-docs-20261015',
  '--network', 'none', '--read-only', '--tmpfs', '/tmp',
  '--cpus', '0.5', '--memory', '256m', '--pids-limit', '64',
  '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
  '-e', 'PYTHONDONTWRITEBYTECODE=1',
  '-v', 'C:\Users\owner\repos\adaptive-spot-lab:/repo:ro',
  'python:3.13.11-slim-bookworm', 'python', '/repo/tools/check_links.py', '/repo'
)
docker @m9DocsArgs
git diff --check
git diff --no-index --check -- NUL docs/plans/0027-m9-market-intelligence-and-event-driven-trading.md
```

VERIFIED: container exit 0, `checked 94 Markdown files; 0 broken link(s)`. Four known, unchanged warnings point to historical absolute Windows links in ExecPlan 0003 at lines 21 and 130. `git diff --check` exited 0. The no-index check of the untracked plan exited 1 for the new-file difference, with no whitespace-error diagnostics; adding `--no-exit-code` also returned 1. Git noted its existing LF-to-CRLF conversion behavior for STATUS and the new plan. Recheck closing evidence edits before delivery. The checker validates local Markdown files/anchors, not remote URL availability or M9 implementation. All M9 runtime/provider/evaluation/deployment checks remain NOT RUN.

### M9 publication preparation — 2026-10-15

OBSERVED owner instruction: `merge this to main`. The sandboxed `git ls-remote` and `gh pr list` could not reach GitHub. The authorized network retry succeeded: `git fetch origin main` advanced the local remote-tracking ref from `5e86b44` to `7b661a0`; `gh pr list --repo MentorAliu/adaptive_spot_lab --state open --json number,title,headRefName,baseRefName,url` returned no open PRs. Repository metadata confirmed normal merge commits are supported. The nine-file M9 documentation change will be published on `codex/m9-roadmap` against current main, preserving its newer M7 records. No force push, administrator bypass, application change or activation is authorized by this publication. Commit/PR/merge results are not claimed by this preparation record.

VERIFIED integration: committed the nine documents on `codex/m9-roadmap` and replayed the new local commit onto `origin/main` at `7b661a0`. Two insertion conflicts in COMMANDS and STATUS were resolved by retaining both the new M9 entries and all upstream M7 records; the resulting diff contains only the nine intended Markdown files. `git diff origin/main...HEAD --check` exited 0. Repeated the Docker link-check command above with container name `asl-m9-merge-docs-20261015`: exit 0, `checked 98 Markdown files; 0 broken link(s)`, the same four historical warnings. An exact-name `docker ps -a` query confirmed that container was removed. Application tests, normal-app operations and activation were not run for this documentation merge.

## ExecPlan 0026 B9: the start dialog on a phone (2026-10-17)

By the cloud session of B0 to B9d, on branch `claude/m7-b0-hjaahq` from `main` at `2508b18` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-start-dialog-on-a-phone-2026-10-17)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B8a's scratch browser stack ([B8a](#execplan-0026-b8a-the-decision-pages-and-the-frame-policy-2026-10-16)): the cluster on 127.0.0.1 port 55449, `asl_m1_m6_b8_browser` dropped, created, migrated and seeded with `tests.m7_browser_fixture seed` before each run, the API on port 8000, the production web build on port 4318, the scratch Playwright configuration and the `web` name in `/etc/hosts`. From `apps/web`:

```bash
# On the build without the fix (the new check at 700 px, then at 600 px), then rebuilt with it
pnpm build && NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs
NO_PROXY="$NO_PROXY,web" ASL_M7_BROWSER=decisions ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_b8_browser \
    PLAYWRIGHT_BASE_URL=http://web:4318 pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @decisions --workers 1
pnpm typecheck && pnpm exec eslint --ignore-pattern '.output/**' . && npx prettier --check src/agents/agents-page.tsx e2e/m7.spec.ts && pnpm test
python3 ../../tools/check_links.py ../..
```

Results (`OBSERVED`): without the fix, at 700 px `12 passed` (the dialog measured 685 px high), at 600 px `1 failed`, `10 passed`, `1 did not run`; with the fix `12 passed`; typecheck, lint and Prettier exit 0; `Tests 248 passed (248)`.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on the fix's build after `Build` and `Generate`, beside the pilot watch: `BrowserResearch`, `BrowserResearchError`, `BrowserDecisions`, `BrowserDecisionsError`, `BrowserRegression`, `PerformanceApi`, `PerformanceBrowser`, `AgentFaults6` (with the fault runner's hold below), `BoundaryRehearsal` (with the check of the boundary's images below), `SecretScan` and `Report`, each with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase <phase> -WaitForWindow
```

**The fault runner's hold (actual, after run `m7-b9a`'s `AgentFaults6`).** From `services/engine` ([plan §18](plans/0026-m7-agent-driven-main-decisions.md#the-fault-runners-hold-2026-10-17)):

```bash
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m6_held_runner.py
# Each of four parts of tests/m6_held_runner.py replaced in turn by a scratch script, the file restored and checked with cmp
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m6_schema.py tests/test_m5_schemas.py tests/test_m6_agent_units.py tests/test_m7_schema.py tests/test_m6_held_runner.py -k "$(/opt/pwsh/pwsh -NoProfile -Command '(Import-PowerShellDataFile ../../tools/profiles/m7.psd1).Build.StaticSelection')" -rs
.venv/bin/ruff check --no-cache tests/m6_held_runner.py tests/test_m6_held_runner.py
/opt/pwsh/pwsh -NoProfile -File ../../tools/profiles/check-profiles.ps1 -Baseline 7b3e52c     # from the repository root
```

Results (`OBSERVED`): `5 passed`; each part taken out failed one to five tests; `Build`'s static tests and selection `17 passed, 190 deselected`, no skip; ruff `All checks passed!`; the profile check `VERIFIED`.

**The boundary rehearsal's images (actual, after run `m7-b9a`'s `BoundaryRehearsal`).** From the repository root ([plan §18](plans/0026-m7-agent-driven-main-decisions.md#the-boundary-rehearsals-images-2026-10-17)); the stub is a scratch script, not committed, as in B9d:

```bash
git worktree add <scratch>/old 4a795fb          # the commit before the fix, for the stub's first run
/opt/pwsh/pwsh -NoProfile -File <scratch>/stub.ps1 <scratch>/run-old <scratch>/old
/opt/pwsh/pwsh -NoProfile -File <scratch>/stub.ps1 <scratch>/run-new "$PWD"
/opt/pwsh/pwsh -NoProfile -File <scratch>/content.ps1     # Get-M6ImageContent and Get-M6ImageStore against a fake docker
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m7/boundary-model.ps1 -Repository <wt> -Work <work>   # <wt>: HEAD with Protect-Path's ACL call skipped
git worktree remove --force <scratch>/old
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
```

Results (`OBSERVED`): before the fix `FAILED` with the PC's message; after it `VERIFIED` (also with the same IDs both runs), the names moved before the activation `FAILED` with its own message, and B9d's 18 faults each `FAILED`; the content helper's digests equal `sha256sum`'s; the boundary model 52 of 52; the profile check `VERIFIED`.

**The promotions of the API fixture (actual, after run `m7-b9b`'s `PerformanceApi`).** From `services/engine` ([plan §18](plans/0026-m7-agent-driven-main-decisions.md#the-promotions-of-the-api-fixture-2026-10-17)); the two scripts are scratch, not committed:

```bash
createdb -h 127.0.0.1 -p 55449 -U asl -T asl_m1_m6_b8_browser asl_m1_m6_b9old_browser    # and asl_m1_m6_b9new2_browser
PYTHONPATH=$PWD ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b9old_browser ASL_TEST_ISOLATED=1 .venv/bin/python <scratch>/promotions.py old
PYTHONPATH=$PWD ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b9new2_browser ASL_TEST_ISOLATED=1 .venv/bin/python <scratch>/promotions.py new
PYTHONPATH=$PWD ASL_DB_ROLE=migration ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b9new2_browser ASL_TEST_ISOLATED=1 .venv/bin/python <scratch>/agents.py
.venv/bin/ruff check --no-cache tests/m6_performance.py
dropdb -h 127.0.0.1 -p 55449 -U asl asl_m1_m6_b9old_browser    # each copy by its exact name
```

Results (`OBSERVED`): old `INVALID 99 validation errors for PromotionsView`; new `VALID 100 ['PROMOTION_V2']`, newest 50 by seq `MARKET_ASSESSMENT_V1`; the agent routes valid; ruff `All checks passed!`.

## ExecPlan 0026 B9d: the boundary script, its model and BoundaryRehearsal (2026-10-16)

By the cloud session of B0 to B9c, on branch `claude/m7-b0-hjaahq` from `main` at `08722b5` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9d--the-boundary-script-its-model-and-boundaryrehearsal-2026-10-16)). Linux, PowerShell 7.4.6, no Docker daemon, a scratch PostgreSQL 16 cluster on port 55449. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** `<wt>`, `<bin>` and the `Protect-Path` shim are B9c's ([above](#execplan-0026-b9c-the-inert-deployment-script-and-its-model-2026-10-16)); `<wt>` holds this branch's changed and new files, copied in. Every database command has `PGPORT=55449 ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1` and the database named:

```bash
cd services/engine
ASL_DB_NAME=asl_m1_m6_m7_b9d .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_boundary.py tests/test_m7_schema.py
# The boundary on a pilot database at 0009 seeded as B9b's (seed_m1, browser_fixture, seed_agents, seed_m4 and the
# pilot's start), the M7 API on port 8004 and the feed, as B9b; the workers as processes with a scratch password file
export ASL_DB_NAME=asl_m1_m5_m6_b9d_pilot ASL_M6_API_URL=http://127.0.0.1:8004
ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8004 --no-access-log &
.venv/bin/python -m tests.m6_migration feed 2400 &
ASL_DB_ROLE=execution ASL_DB_PASSWORD_FILE=<pw> ASL_EXECUTION_ENABLED=1 ASL_EXECUTION_ACTIVATION=MAIN ASL_EXECUTION_HEARTBEAT=<hb> .venv/bin/python -m app.execution.worker &
ASL_DB_ROLE=evaluation ASL_DB_PASSWORD_FILE=<pw> ASL_EVALUATION_ENABLED=1 ASL_EVALUATION_HEARTBEAT=<hb> .venv/bin/python -m app.evaluation.worker &
.venv/bin/python -m app.execution.identity boundary-check --experiment <pilot>
.venv/bin/python -m app.execution.identity install-definitions          # refused while the pilot runs
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_boundary stop
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_boundary state <pilot>   # until COMPLETED with FINAL
.venv/bin/python -m app.execution.identity boundary-check --experiment <pilot>
kill -TERM <workers>; .venv/bin/python -m app.execution.identity disable
.venv/bin/python -m app.execution.identity boundary-check --experiment <pilot>
.venv/bin/python -m app.execution.identity install-definitions          # twice
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_boundary activate COST_SCENARIO_HYPOTHETICAL_H1
.venv/bin/python -m app.execution.identity preflight --experiment <policy run>
# The logins: main_preflight and ALTER ROLE ... LOGIN in one transaction with the scratch password (a here-document
# calling app.execution.identity's own functions), in place of enable --main, which reads the secrets; then both
# workers started again as above
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_boundary start <policy run>
kill -TERM <workers, feed, api>; .venv/bin/python -m app.execution.identity disable
dropdb -h 127.0.0.1 -p 55449 -U asl asl_m1_m5_m6_b9d_pilot
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m7/boundary-model.ps1 -Repository <wt> -Work <work>
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m7/deploy-model.ps1 -Repository <wt> -Work <work>
# A scratch python3 script applies each of 15 replacements to <wt>'s tools/m7-boundary.ps1 in turn, runs the whole
# model, reads its last line, and writes the branch's file back (checked with cmp); then the four that passed, again
python3 <scratch>/mutate.py <scratch>
# The phase on stubbed Docker, owner scripts and product helpers, from the repository root: 20 cases
/opt/pwsh/pwsh -NoProfile -File <scratch>/boundary-stub.ps1 <scratch run root>
/opt/pwsh/pwsh -NoProfile -File <scratch>/parse.ps1        # every .ps1 and .psm1 of tools/ through the parser
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
cd services/engine && .venv/bin/ruff check --no-cache app tests alembic && .venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
python3 tools/check_links.py .
```

**Results (`OBSERVED`; scratch PostgreSQL 16 and models, no evidence about Docker, Compose or PostgreSQL 17).** The database tests: `38 passed`, then `40 passed` after the review's fixes. The walk: the check refused with the pilot running (five reasons) and the install was refused; the stop reached `COMPLETED` with `FINAL` about 8.5 minutes later; with the workers running the check named the two logins and the lease only; after them, allowed; `INSTALLED` then `PRESENT`; the activation `READY` with three approvals; the main preflight allowed; the workers bound `AGENT_POLICY_V1` under epoch 3; Start `RUNNING` with `ACTIVATED` in 4 s (the walk ran before the review's fixes, so without the sessions and newest-run reasons). The boundary model: exit 0, 7 scenarios, 39 of 39, then 43 of 43, then 52 of 52 after the review's fixes; of 15 changes 11 failed it at once and the other four after the four cases added for them, and each of the nine checks the review's fixes added failed it when taken out. M7's deploy model: 114 of 114. The stub: `VERIFIED`, also with one unreadable state during the wait, and 18 faults each `FAILED` with their own problem. 55 files parse; profiles `VERIFIED` (44 phases, 0 not built); ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; without a database `2 failed, 726 passed, 329 skipped, 1 warning, 336 errors` (B0's and B1's two failures; the rest `NOT RUN`).

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in B9's final run after `Build` and `Generate`, with the pilot watch running; the `PreM6` and `PreM7` images of `tools/profiles/m7.psd1` must be on the PC (the normal application runs them). The phase builds three times; its window is 45 minutes:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BoundaryRehearsal -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7\boundary-model.ps1 -Repository <repository> -Work <an existing empty directory>
```

The boundary itself is the owner's, on the normal application, after the pilot's stop in the UI and `tools/pilot-deactivate.ps1` from a fresh shell (the M4 tools clear no `ASL_` or `COMPOSE_` variable); PROPOSED, not verified, and not before M6-B and the probes (plan §13.1):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-boundary.ps1 -ExperimentId <the pilot's id>
```

## ExecPlan 0026 B9c: the inert deployment script and its model (2026-10-16)

By the cloud session of B0 to B9b, on branch `claude/m7-b0-hjaahq` from `main` at `3448a96` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9c--the-inert-deployment-script-and-its-model-2026-10-16)). Linux, PowerShell 7.4.6, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** `<wt>` is a scratch worktree of `3448a96` with `tools/m7-deploy.ps1` and `tools/m7/deploy-model.ps1` copied in, and a scratch-only line at the top of `Protect-Path` in its `tools/lib/Pilot.psm1` (`if (-not $IsWindows -and $PSVersionTable.PSEdition -eq 'Core') { return }`), never committed. `<bin>` holds links to `git`, `chmod`, `env`, `sha256sum` and `uname` only, so that no `docker` executable is on the `PATH`:

```bash
git worktree add --detach <wt> 3448a96
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m6/deploy-model.ps1 -Repository <wt> -Work <work>
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m7/deploy-model.ps1 -Repository <wt> -Work <work>
# One check of tools/m7-deploy.ps1 taken out at a time (a python3 one-line replacement in <wt>'s copy), then
# the scenarios concerned, and the copy restored from the branch with cp and checked with cmp
cd <wt> && env PATH=<bin>:/opt/pwsh /opt/pwsh/pwsh -NoProfile -File tools/m7/deploy-model.ps1 -Repository <wt> -Work <work> -Only 'M7 stays inert'
# After the review: a scratch python3 script applies each of 15 replacements to <wt>'s copy in turn, runs the
# whole model, counts its FAIL lines, and writes the branch's file back (checked with cmp)
python3 <scratch>/mutate.py <scratch>
/opt/pwsh/pwsh -NoProfile -Command '[System.Management.Automation.Language.Parser]::ParseFile(...)'   # both files
grep -nP '[^\x00-\x7F]' tools/m7-deploy.ps1 tools/m7/deploy-model.ps1   # no output
python3 tools/check_links.py .
# The script's SQL on scratch PostgreSQL 16 (cluster 55449): a scratch PowerShell file takes Get-DecisionFacts and
# Wait-WorkerStart out of the script with a stand-in Invoke-Psql that keeps each query, and psql runs them
psql -X -h /tmp -p 55449 -U asl -d asl_m1_m5_m6_b9c_pilot -At -v ON_ERROR_STOP=1 -f <queries>       # at 0009
psql -X -h /tmp -p 55449 -U asl -d asl_m1_m6_m7_b7_pre0009 -At -v ON_ERROR_STOP=1 -f <first query>  # at 0008
# In one transaction that ends with ROLLBACK: a non-fixture BAR_CLOSE trigger, the agent lease taken at a new
# epoch, a WORKER_STARTED row under that epoch and one under the epoch before; then the queries again
psql -X -h /tmp -p 55449 -U asl -d asl_m1_m5_m6_b9c_pilot -At -v ON_ERROR_STOP=1 -f <transaction>
```

**Results (`OBSERVED`; a model, no evidence about Docker, Compose or PostgreSQL 17).** M6's model on `3448a96`: exit 0, 17 scenarios, 76 of 76. M7's model before the review: exit 0, 20 scenarios, 92 of 92, about 17 s; each of eight checks taken out once failed its own scenario. After the review's fixes: exit 0, 25 scenarios, 114 of 114, about 21 s; each of 15 changes failed the model (§18). The SQL on scratch PostgreSQL 16: every query runs at `0009`, and the one without the decision tables at `0008`; in the rolled-back transaction the history count reads 1, and the start query counts the start under the held epoch only (1 of 2) and none before a later time; a `StartedAt` with nine fractional digits is accepted and rounded to microseconds. Both files parse without error and are ASCII. Links: 100 files, `0 broken link(s)`.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root; no Docker command runs, because the model takes every `docker` executable off its own `PATH` and refuses to start if one is still reachable. B9d's `BoundaryRehearsal` runs it too:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7\deploy-model.ps1 -Repository <repository> -Work <an existing empty directory>
```

The deployment itself is B10's, on the normal application, between HH:15 and HH:35 UTC, with the owner's word in the thread; PROPOSED, not verified. The baseline file is the compose file the pilot's newest container was created from, and the image parameters are what a read-only look shows first:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-deploy.ps1 -BaselineComposeFile <baseline compose file> -ExpectedPilotImages '<market-worker=...,execution-worker=...,evaluation-worker=...>' -ExpectedPreM7Images '<the ten names and their image IDs>'
```

## ExecPlan 0026 B9b: the mixed-version rollout beside the pilot (2026-10-16)

By the cloud session of B0 to B9a, on branch `claude/m7-b0-hjaahq`: the database checks ran on `9bd2eb5`, the gates on `main` at `c457261`, where B9b's files are byte-identical ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9b--the-mixed-version-rollout-beside-the-pilot-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** The scratch PostgreSQL 16 cluster on port 55449. The M6-A code is source `583a98a` in a scratch worktree, run with this branch's locked environment (its `uv.lock` and `pyproject.toml` are identical to `main`'s, checked with `diff`). `$V` is `services/engine/.venv/bin`; every command has `PGPORT=55449 ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m5_m6_b9_pilot`, and the second round `ASL_DB_NAME=asl_m1_m5_m6_b9c_pilot`:

```bash
git worktree add --detach <scratch>/m6a 583a98a
# The pilot database written by the M6-A code: migrated to 0008 and seeded as M6's fixtures seed it
createdb -h 127.0.0.1 -p 55449 -U asl asl_m1_m5_m6_b9_pilot
cd <scratch>/m6a/services/engine && ASL_DB_ROLE=migration $V/alembic upgrade head
ASL_DB_ROLE=api $V/python -c "from app.execution import acceptance, browser_fixture; acceptance.require_isolation(); acceptance.seed_m1(); browser_fixture.main(); from app.agents import acceptance as agents; agents.require_isolation(); agents.seed_agents()"
# The M6-A API on port 8001 (from the worktree) and the M7 API on port 8002 (from this branch), both as the api identity
ASL_DB_ROLE=api $V/uvicorn app.main:app --host 127.0.0.1 --port 8001 --no-access-log &
cd services/engine && ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8002 --no-access-log &
# Each state against its own API, and against the other one, which must fail (from services/engine)
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8001 .venv/bin/python -m tests.m7_rollout http m6-api-0008
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8002 .venv/bin/python -m tests.m7_rollout http m7-api-0008
# 0009 live under 5 ms lock sampling, then the 0009 states, the inert check, the way back and the refusal
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout dynamic-upgrade /perf/mixed7-locks.json
# The M6-A agent worker's own definitions check, from the worktree; m6a-defs.py prints
# json.dumps({"problems": app.agents.worker.check_definitions(app.db.get_engine())})
PYTHONPATH=. ASL_DB_ROLE=migration $V/python <scratch>/m6a-defs.py
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8001 .venv/bin/python -m tests.m7_rollout http m6-api-0009
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8002 .venv/bin/python -m tests.m7_rollout http m7-api-0009
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout inert
ASL_DB_ROLE=migration .venv/bin/alembic downgrade 0008_m6_research
ASL_DB_ROLE=migration .venv/bin/python -m app.research.migrate
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout real-row
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout downgrade-refused
# The helper as the review left it (a scratch worktree of 9bd2eb5 with B9b), on the first database, a database
# named asl, and a fresh one with the M7 API on port 8003
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout inert
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout worker-starts
ASL_DB_NAME=asl ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout inert
createdb -h 127.0.0.1 -p 55449 -U asl asl_m1_m5_m6_b9c_pilot   # then migrated and seeded by the M6-A code, as above
ASL_DB_ROLE=api .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8003 --no-access-log &
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8003 .venv/bin/python -m tests.m7_rollout http m7-api-0008
ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_rollout inert
ASL_DB_ROLE=migration ASL_M6_API_URL=http://127.0.0.1:8003 .venv/bin/python -m tests.m7_rollout http m7-api-0009
# The phase on stubbed Docker and product helpers, from the repository root: 16 cases
/opt/pwsh/pwsh -NoProfile -File <scratch>/mixed7-stub.ps1 <scratch run root>
cd services/engine && .venv/bin/ruff check --no-cache app tests alembic && .venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
python3 tools/check_links.py .
```

**Results (`OBSERVED` on scratch databases, with no pilot or agent worker running: no evidence for the owner's PC).** First database: `m6-api-0008` on the M6-A API and `m7-api-0008` on the M7 API passed, each failed against the other API; `dynamic-upgrade` reached `0009` in one attempt (0.27 s, 38 samples, 28 with the migration's locks, 180 protected relations, none stronger than `ACCESS SHARE`); the M6-A definitions check listed generation 3's nine definitions; `m6-api-0009` (ready 503 `database_or_migration_unavailable`) and `m7-api-0009` passed, each failed against the other API; `inert` passed; after the downgrade the definitions check listed none and `m6-api-0008` passed again; `app.research.migrate` `VERIFIED: migration completed in 1 bounded attempt(s).`; `real-row` wrote one trigger; `downgrade-refused` passed ("M7 agent history exists; downgrade refused; fix forward", nothing changed). The reviewed helper: `inert` failed on that database (one M7 trigger, exit 1), `worker-starts` gave 0, and the database `asl` was refused. Fresh database: `m7-api-0008` passed (generation-3 start 503, no workflow row), `inert` passed with every count of the downgrade's guard 0, `m7-api-0009` passed. The stubbed phase: `VERIFIED`, 14 faults each `FAILED` with their own problem, a missing `PreM7` image stopped before any change. ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; without a database `2 failed, 726 passed, 329 skipped, 1 warning, 329 errors` (B0's and B1's two failures; the rest `NOT RUN`); profiles `VERIFIED` (44 phases, 1 not built); links `0 broken link(s)`.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in B9's final run after `Build` and `Generate`, with the pilot watch running; the `PreM7` images of `tools/profiles/m7.psd1` must be on the PC (the normal application runs them):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase MixedVersion7 -WaitForWindow
```

## ExecPlan 0026 B9a: the engine's step budget with agent intake (2026-10-16)

By the cloud session of B0 to B8c, on branch `claude/m7-b0-hjaahq` from `main` at `f516d9b` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9a--the-engines-step-budget-with-agent-intake-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** The scratch PostgreSQL 16 cluster on port 55449 of the earlier batches, without container limits, from `services/engine`:

```bash
export PGPORT=55449 ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
# An empty database with the saturation target's catalog name (prepare checks its name), the workload's database
# created by the workload in the same cluster, then migrated (the harness uses app.research.migrate for both)
createdb -h 127.0.0.1 -U asl asl_m1_m5_m6_b9_saturation
ASL_DB_ROLE=migration ASL_DB_NAME=asl_m1_m5_m6_b9_saturation .venv/bin/python -m tests.m7_performance prepare asl_m1_m3_m6_b9_saturation
ASL_DB_ROLE=migration ASL_DB_NAME=asl_m1_m3_m6_b9_saturation .venv/bin/alembic upgrade head
# The smoke run: the feed in the background, then, once /perf/ready.json exists, the worker on the thirty
# minutes it names
export ASL_DB_NAME=asl_m1_m3_m6_b9_saturation
rm -f /perf/ready.json
ASL_DB_ROLE=migration .venv/bin/python -m tests.m7_performance feed 2220 > feed.out 2>&1 &
for i in $(seq 1 600); do [ -f /perf/ready.json ] && break; sleep 1; done
FROM=$(python3 -c 'import json;print(json.load(open("/perf/ready.json"))["measured_from"])')
ASL_DB_ROLE=execution ASL_EXECUTION_ENABLED=1 ASL_EXECUTION_ACTIVATION=MAIN \
    .venv/bin/python -m tests.m7_performance engine "$FROM" 1800 > engine.out 2>&1; wait
# The phase on stubbed Docker and product helpers, with a smoke run's two result lines, from the repository root:
# 20 cases, each a line edited from the real ones (limits set to 1 CPU and 512 MiB but in 'no-limits')
/opt/pwsh/pwsh -NoProfile -File <scratch>/perf7-stub.ps1 <scratch run root> <engine line> <feed line>
cd services/engine && .venv/bin/ruff check --no-cache app tests alembic && .venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
python3 tools/check_links.py .
```

**Results (`OBSERVED`, without the product's container limits, on the database's host: no evidence for the owner's PC).** The final smoke run, the workload as committed, 18:05 to 18:42 UTC: both processes exit 0. The feed `passed`: 30 requests, each with its planned answer, one stop update, both positions `CLOSED_WITH_DUST` as planned. The worker `passed`, bound to `AGENT_POLICY_V1` alone: 3,600 steps in the thirty minutes (18:07:20 to 18:37:20), p95 301.94 ms, p99 326.17 ms; 31 steps with intake, p95 281.51 ms, p99 301.92 ms; RSS at most 64.4 MiB, growth 2.75 MiB; 5,400 of 5,400 publications looked at, none stale; the lease kept. The first smoke run, on `c5e8279`, met the same budget, but its feed exited 1 on a position closed with dust (fixed in `f237230`). The stub: 20 cases; `VERIFIED` with the final run's lines and with a half-written `ready.json`, and each fault failed with its own message (§18). ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; pytest without a database `2 failed, 726 passed, 329 skipped, 1 warning, 329 errors in 53.69s` (B0's and B1's two failures), the rest `NOT RUN`, not passed; the profile check `VERIFIED` (44 phases, 2 not built); the link check `checked 100 Markdown files; 0 broken link(s)`.

**`NOT RUN`: for the owner's PC.** PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in B9's final run after `Build` and `Generate`, with the pilot watch running, between HH:07 and HH:09 UTC (the phase waits for that start with `-WaitForWindow`):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase PerformanceEngine7 -WaitForWindow
```

## ExecPlan 0026 B8c: the Agents page's M7 controls and the owner's two additions (2026-10-16)

By the cloud session of B0 to B8b, on branch `claude/m7-b0-hjaahq` from `main` at `2427af2` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8c--the-agents-pages-m7-controls-and-the-owners-two-additions-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B8b's scratch stack and commands ([B8b](#execplan-0026-b8b-the-owners-controls-2026-10-16)). Changed or added, from the repository root unless stated:

```bash
# After the @decisions selection, the fixture owner revokes the current runtime profile (from services/engine).
# On a database the fixture did not seed it is refused before any role changes (tried on a fresh 0009 database).
ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser \
    .venv/bin/python -m tests.m7_browser_fixture revoke-profile
# Then the new selection, from apps/web
NO_PROXY="$NO_PROXY,web" ASL_M7_BROWSER=profile ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_b8_browser \
    PLAYWRIGHT_BASE_URL=http://web:4318 pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @profile --workers 1
# The web's and the engine's checks as in B8b, without the M7 database files: B8c changes no engine code
npx vitest run src/agents/controls.test.tsx          # from apps/web; each mutation of §18 one at a time, restored after
# The harness functions on stubs: 12 @decisions, 1 @profile and 19 sample files; also 11, 0 and 18, each refused
/opt/pwsh/pwsh -NoProfile -File <scratch>/mock-b8c.ps1 <scratch run root> 12 1 19
/opt/pwsh/pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c
python3 tools/check_links.py .
```

Results (plan §18, B8c), `OBSERVED` on the final build: `@decisions` `12 passed`, `revoke-profile` to `LOGIN_REQUIRED`, `@profile` `1 passed`, M7 and M6 `@unavailable` and `@error` `1 passed` each; `revoke-profile` on a fresh `0009` database refused before any role changed; web `Tests 248 passed (248)`, typecheck, lint, Prettier, `api:check` and the build exit 0; 27 mutations each failing a test; ruff and the OpenAPI check pass; the database-free pytest `2 failed, 726 passed, 329 skipped, 329 errors` (B0's and B1's known failures; the rest `NOT RUN`); the harness on stubs `VERIFIED` with 12, 1 and 19 and refused with 11, 0 or 18; the profile check `VERIFIED`; `0 broken link(s)`.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B8c's build after `Build` and `Generate`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). B9's final run is that run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisions -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisionsError -WaitForWindow
```

## ExecPlan 0026 B8b: the owner's controls (2026-10-16)

By the cloud session of B0 to B8a, on branch `claude/m7-b0-hjaahq` from `main` at `3f1afa9` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8b--the-owners-controls-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B8a's scratch stack and commands ([B8a](#execplan-0026-b8a-the-decision-pages-and-the-frame-policy-2026-10-16)): the cluster on 127.0.0.1 port 55449, `asl_m1_m6_b8_browser` reset before each state, the API as `asl_api`, the production web build, the scratch Playwright configuration and the `web` name in `/etc/hosts`, each removed by exact name when the session's batches end. Changed or added, from the repository root unless stated:

```bash
# The seed and samples on a fresh database at head, then the API and web restarted (as in B8a)
(cd services/engine && ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser \
    .venv/bin/python -m tests.m7_browser_fixture seed)
(cd services/engine && ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser \
    .venv/bin/python -m tests.m7_browser_fixture samples ../../apps/web/src/decisions/samples)
# Each selection, from apps/web (the API stopped for @error); M6's @unavailable at 0007 and @error as in B8a
NO_PROXY="$NO_PROXY,web" ASL_M7_BROWSER=decisions ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_b8_browser \
    PLAYWRIGHT_BASE_URL=http://web:4318 pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @decisions --workers 1
# The web's checks, each mutation of §18 (one at a time, restored after), the engine's checks
cd apps/web && pnpm exec eslint --ignore-pattern '.output/**' . && pnpm typecheck && pnpm check && pnpm test && pnpm build && pnpm api:check
npx vitest run src/decisions/controls.test.tsx src/decisions/decisions.server.test.ts src/research/research.server.test.ts
cd services/engine && .venv/bin/ruff check --no-cache app tests alembic && .venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7 .venv/bin/python -m pytest -q -p no:cacheprovider \
    tests/test_m7_api.py tests/test_m7_schema.py tests/test_m7_intent_units.py tests/test_m7_intents.py tests/test_m7_agents.py
# The harness functions on stubs, B8a's script with 11 @decisions tests and 18 sample files (also 6 and 17, to see each refused)
/opt/pwsh/pwsh -NoProfile -File <scratch>/mock.ps1 <scratch run root>
python3 tools/check_links.py .
```

Results (plan §18, B8b), after the review's fixes: M7 `@decisions` `11 passed` (30.3 s), `@unavailable` at `0008` `1 passed`, `@error` `1 passed`; M6 `@unavailable` at `0007` `1 passed`, `@error` `1 passed`; M6 `@research` `NOT RUN` (its fixture's screenings refused `DISK_PRESSURE`: 29.5 GB free, below M6's 40 GiB). `Tests 220 passed (220)`; lint, typecheck, Prettier, the generated-type check and the build exit 0; each mutation failed its test. Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; without a database `2 failed, 726 passed, 329 skipped, 1 warning, 329 errors` (B0's and B1's two). The five M7 database files: `147 passed, 11 warnings, 1 error`, the error a role change racing this session's reseed on the same cluster (`tuple concurrently updated`); `test_m7_agents.py` alone afterwards `43 passed`. The stubbed phases `VERIFIED`; with 6 tests or 17 files, refused.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B8b's build after `Build` and `Generate`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). Run `m7-b8a`, started at 13:08 UTC on `3f1afa9`, runs B8a's six `@decisions` tests; B8b's eleven need a run on B8b's build, which B9's final run is:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisions -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisionsError -WaitForWindow
```

## ExecPlan 0026 B8a: the decision pages and the frame policy (2026-10-16)

By the cloud session of B0 to B7, on branch `claude/m7-b0-hjaahq` from `main` at `50aa702` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8a--the-decision-pages-and-the-frame-policy-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B6c's scratch PostgreSQL 16 cluster on 127.0.0.1 port 55449, the database `asl_m1_m6_b8_browser` (named as the harness's browser target names its own) dropped, created and migrated before each state; the M6 fixture also created `asl_m1_replay_m6_b8_browser_v2` there. Both are removed by exact name with the cluster when the session's batches end. The browser is the session's preinstalled Chromium, through a scratch Playwright configuration (the project's, with `launchOptions.executablePath` set to it and an output directory outside the repository) that was not committed. The name `web` was mapped to 127.0.0.1 in the container's `/etc/hosts` for the runs through `http://web:4318`, and that line is removed when the session's batches end. From the repository root unless stated:

```bash
# Each state's database (scratch script): dropdb --force, createdb, then from services/engine
ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser ASL_TEST_ISOLATED=1 ASL_DB_ROLE=migration \
    .venv/bin/alembic upgrade head            # or 0008_m6_research (M7 @unavailable), 0007_m5_agent_runtime (M6 @unavailable)
# The fixtures and the samples, from services/engine, on the database at head
ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser ASL_TEST_ISOLATED=1 ASL_DB_ROLE=migration \
    ASL_MODEL_EGRESS_INTERNAL=true .venv/bin/python -m tests.m7_browser_fixture seed
... .venv/bin/python -m tests.m7_browser_fixture samples ../../apps/web/src/decisions/samples
... ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m6_browser_fixture seed     # for M6's spec, on a fresh database
# The API and the production web build
(cd services/engine && ASL_DB_HOST=127.0.0.1 PGPORT=55449 ASL_DB_NAME=asl_m1_m6_b8_browser ASL_DB_ROLE=api ASL_TEST_ISOLATED=1 \
    .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log)
(cd apps/web && pnpm build && NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs)
# Each selection (the API stopped for @error), from apps/web
NO_PROXY="$NO_PROXY,web" ASL_M7_BROWSER=decisions ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_m6_b8_browser \
    PLAYWRIGHT_BASE_URL=http://web:4318 pnpm exec playwright test -c <scratch config> e2e/m7.spec.ts --grep @decisions --workers 1
#   ... ASL_M7_BROWSER=unavailable --grep @unavailable; ASL_M7_BROWSER=error --grep @error
#   ... ASL_M6_BROWSER=research e2e/m6.spec.ts --grep @research; unavailable; error
# The frame test without the policy: framed() taken out of src/server.ts, rebuilt, @decisions run, restored, rebuilt
# The harness functions on stubbed Docker, Compose, image and record helpers
pwsh -NoProfile -File <scratch>/mock.ps1 <scratch run root>
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # PowerShell 7.4.6
cd apps/web && pnpm lint && pnpm typecheck && pnpm check && pnpm test && pnpm build && pnpm api:check
cd services/engine && .venv/bin/ruff check --no-cache app tests alembic && .venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
python3 tools/check_links.py .
```

Results (plan §18, B8a):
- **M7's spec** on the final build through `http://web:4318`: `@decisions` `6 passed` (15.5 s), `@unavailable` at `0008` `1 passed`, `@error` `1 passed`. The fixture seeded in 7 s.
- **Without the frame policy:** test 5 `1 failed` (`Expected: "DENY"`, `Received: undefined`); restored, `6 passed`.
- **M6's spec on this web** through `http://web:4318`: `@research` `7 passed` (1.2 min), `@unavailable` at `0007` `1 passed`, `@error` `1 passed`. Through `http://127.0.0.1:4318` its first test failed on the forged-`Origin` check (`200`, not `403`): Chromium sends `Sec-Fetch-Site` to a loopback address, and Start's CSRF middleware then decides on it alone ([INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m7-b8a-decision-pages-and-the-frame-policy--2026-10-16-execplan-0026)).
- **After the review's fixes** (plan §17, B8a decision 10), the same commands on the rebuilt web: M7 `@decisions` `6 passed` (15.0 s), `@unavailable` `1 passed`, `@error` `1 passed`; M6 `@research` `7 passed` (1.3 min, its fixture seeded in 80 s); `pnpm test` `192 passed (192)`; each new test failed with its fix taken out; typecheck, Prettier, `api:check`, lint (with `--ignore-pattern '.output/**'` while the build served the browser runs), the profile check and the link check exit 0; the stubbed harness wrote `browser-results/decisions-fixture.json`.
- **The harness functions on stubs:** `BrowserDecisions` and `BrowserDecisionsError` `VERIFIED`, with the commands listed in plan §18; `BrowserResearchError`'s commands, labels and directories as before; a changed image refused. **The profile check** `VERIFIED` (44 phases, 3 not built).
- **The web:** lint, typecheck, Prettier, the generated-type check and the build exit 0; `Tests 190 passed (190)`. **The engine:** ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; without a database `2 failed, 724 passed, 329 skipped, 1 warning, 326 errors` (B0's and B1's failures; the rest `NOT RUN`). **Links** `0 broken link(s)`, with the known warnings of plan 0003.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B8a's build after `Build` and `Generate`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). `BrowserResearch` builds the images the two new phases use and must pass first in the same run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserResearch -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisions -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase BrowserDecisionsError -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

The same run can take B4's to B7's phases, which have not run on the owner's PC either ([B7](#execplan-0026-b7-the-owners-api-the-openapi-document-and-the-generated-types-2026-10-16)).

## ExecPlan 0026 B7: the owner's API, the OpenAPI document and the generated types (2026-10-16)

By the cloud session of B0 to B6c, on branch `claude/m7-b0-hjaahq` from `main` at `51e2454` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b7--the-owners-api-the-openapi-document-and-the-generated-types-2026-10-16)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B6c's three scratch PostgreSQL 16 clusters and its bridge environment ([B6c](#execplan-0026-b6c-the-control-replay-2026-10-12)), each holding only `asl_m1_` databases, kept for the next batch and removed by exact path when the session's batches end. Each database was dropped, created and migrated on the final `0009` as in B6c, after setting the M5 to M7 roles `NOLOGIN`, and given `python -m tests.m6_support api-login`; the `0008` database was migrated with `alembic upgrade 0008_m6_research` instead. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_api.py
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m7_b7r .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_generations.py tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m0m4_b7 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    $(ls tests/test_*.py | grep -v "test_m[567]\|test_generations")                  # M0 to M4
# In B6c's <copy>, refreshed from the tree, with B6c's bridge environment:
.venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_control_bridge.py tests/test_m6_shadows.py \
    tests/test_m6_bridge.py tests/test_m6_runner.py tests/test_m6_staging.py
# Each review fix taken out in turn, its test run on 55449, the file restored:
<scratch>/mutate.sh <file> <fixed text> <text without the fix> tests/test_m7_api.py::<test>
# M6's browser fixture on the M7 API; its samples put in place of the web's for one run of the page tests, then restored
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7samples ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m6_browser_fixture seed
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7samples ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m6_browser_fixture samples <dir>
cp <dir>/*.json ../../apps/web/src/research/samples/ && (cd ../../apps/web && npx vitest run src/research/pages.test.tsx); \
    git checkout -- ../../apps/web/src/research/samples
# The M7 API on a real 0008 database, as asl_api with a SYNTHETIC owner session (a scratch script with TestClient)
PYTHONPATH=. PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7_pre0009 .venv/bin/python <scratch>/check08.py
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .                                                     # repository root
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # repository root, PowerShell 7.4.6
cd apps/web && pnpm typecheck && pnpm lint && pnpm check && pnpm api:check && pnpm test && pnpm build
```

`Migration7`'s steps outside Docker ran as in [B6b](#execplan-0026-b6b-segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12), on 55449, on the recovery database `asl_m1_m5_m6_b7_recovery`.

Results (plan §18, B7):
- **The phase's file:** `21 passed, 1 warning` in 79 s on the final code, none skipped. Before the independent review: 13 tests, `13 passed` in 40 s.
- **The M5, M6 and M7 files** with `test_generations.py`: at `063fcf9`, `4 failed, 976 passed, 11 warnings, 56 errors` in 18 min. Two failures were B7's (the import checks, fixed by plan §17, B7 decision 11), two B1's; the errors need the bridge environment. On the final code: `4 failed, 984 passed, 11 warnings, 56 errors` in 18 min, at `92d098d`: B1's two; the revocation test, which read the raise's log after an in-process migration's Alembic `fileConfig` had disabled the module loggers (it passed alone; it now reads the log call, and the whole file then passed after `fileConfig('alembic.ini')` in the same process: `21 passed`); and M6's source-refresh test, which started at 10:05 UTC inside HH:59:30 to HH:06:00, where the test clock runs 8 minutes ahead (it passed alone at 10:23 and failed the same way with the shift forced, `assert fresh["available_at"] > cutoff`). The two by-hand runs, from `services/engine`:

```bash
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b7 .venv/bin/python -c "import sys, pytest; from logging.config import fileConfig; fileConfig('alembic.ini'); sys.exit(pytest.main(['-q', 'tests/test_m7_api.py']))"
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m7_b7r .venv/bin/python -c "<m5_agents.Clock with shift = 8 minutes, then pytest.main on the one test>"
```
.
- **The bridge-side files** (`test_m7_control_bridge.py` and M6's four), the copy refreshed from the final tree and the catalog database `asl_m1_m6_m7_b6c` migrated again on B7's `0009`: `67 passed, 87 warnings` in 368 s.
- **M0 to M4:** `324 passed, 1 warning, 13 errors` in 23 min, at `063fcf9`. The errors are `test_m1_account.py`'s 13, which need the host `postgres`; they are `NOT RUN`.
- **Each review fix matters:** each of the five taken out in turn, its test `1 failed`.
- **`0008`:** the policies `NOT_INSTALLED`, the status `unconfigured`, five more M5 and M6 reads `200`, an unknown request `404 REQUEST_NOT_FOUND`, the M7 routes and writes `503 DECISION_SCHEMA_PENDING`.
- **`Migration7`'s steps:** both `VERIFIED` on the final `0009`, in 25 s: the static step's downgrade refused; the live step migrated in 0.39 s at the first attempt, held nothing stronger than `AccessShareLock` on its 21 protected relations, restored exactly and found 28 declared changes.
- **Without a database:** `2 failed, 724 passed, 329 skipped, 1 warning, 326 errors` in 55 s; the two failures are B0's and B1's; `NOT RUN`, not passed.
- **The web's page tests on the M7 API's samples:** `17 passed`.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches`. **Links** `0 broken link(s)`, with the known warnings of plan 0003. **The profile check** `VERIFIED` (44 phases, 5 not built). **The web:** typecheck, lint, Prettier and the generated-type check exit 0 (`Generated TypeScript API types match`); `Tests 161 passed (161)` in 18 files; the production build exit 0. Lint first read the build output an earlier build had left in `apps/web/.output` (145 errors, all in that ignored directory) and passed once it was removed, as in earlier batches.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B7's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). `Migration7` again, since B7 changed `0009`'s workflow guard and its helper:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Migration7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase ApiAuth7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

The same run can take B4's to B6c's phases, which have not run on the owner's PC either ([B6c](#execplan-0026-b6c-the-control-replay-2026-10-12)). `test_m1_account.py` runs in `Regression`'s M0 to M2 step.

## ExecPlan 0026 B6c: the control replay (2026-10-12)

By the cloud session of B0 to B6b, on branch `claude/m7-b0-hjaahq` from `main` at `7b661a0`, with `main` at `0a7866b` (M9 and M10 documents only) merged in before the last checks ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6c--the-control-replay-2026-10-12)). The weekly usage limit paused the session from 2026-10-12 to 2026-10-16; the last checks ran on 2026-10-16. Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B6a's two scratch PostgreSQL 16 clusters (`/var/lib/postgresql/asl-m7-b6a` and `asl-m7-b6b`, 127.0.0.1 ports 55449 and 55450), and a third, `asl-m7-b6c-research` on 127.0.0.2 port 55450, standing in for the research cluster of M6's bridge tests. Each holds only `asl_m1_` databases; all three are kept for the next batch and removed by exact path when the session's batches end. Every database was dropped, created and migrated on the final `0009` as in [B6b](#execplan-0026-b6b-segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12), after setting the M5 to M7 roles `NOLOGIN`, and given `python -m tests.m6_support api-login`. The bridge tests read their secrets from `/run/secrets` and write their evidence to `/out`, as in their Compose target. Here they ran from a copy of `services/engine` whose two paths were rewritten to a scratch directory holding random values the session wrote, never the owner's. The research store's free-space floor (`min_available_bytes`, 40 GiB) was met by a 64 GiB `tmpfs` on `/research-data`, the path of the Compose volume. The container was restarted during the pause; the clusters were started again with `pg_ctl start` and the `tmpfs` mounted again. As root, then from `services/engine`:

```bash
R=/var/lib/postgresql/asl-m7-b6c-research
su postgres -c "/usr/lib/postgresql/16/bin/initdb -A trust -U asl -D $R/data"
su postgres -c "mkdir -p $R/sock && /usr/lib/postgresql/16/bin/pg_ctl -D $R/data -l $R/log -o '-p 55450 -k $R/sock -c listen_addresses=127.0.0.2' start"
mount -t tmpfs -o size=64g,mode=755 tmpfs /research-data
for n in postgres_password catalog_postgres_password api_db_password agent_db_password source_db_password research_db_password \
    execution_db_password evaluation_db_password research_bridge_db_password market_worker_password api_internal_key \
    owner_setup_key agent_runner_key; do python3 -c "import secrets;print(secrets.token_hex(32))" > <scratch>/secrets/$n; done
# <copy>: services/engine with "/run/secrets" -> <scratch>/secrets and "/out/" -> <scratch>/out/ in its Python files
psql -h 127.0.0.2 -p 55450 -U asl -d postgres -c "CREATE DATABASE asl_m1_replay_m6_b6c"
PGPORT=55450 ASL_DB_HOST=127.0.0.2 ASL_DB_NAME=asl_m1_replay_m6_b6c ASL_TEST_ISOLATED=1 ASL_REPLAY_ISOLATED=1 \
    ASL_DB_ROLE=migration .venv/bin/python -m app.research.runner --initialize       # in <copy>

export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6c .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_controls.py
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_generations.py tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m0m4_b6c .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    $(ls tests/test_*.py | grep -v "test_m[567]\|test_generations")                  # M0 to M4
# In <copy>, as the bridge tests' Compose target sets them (the catalog on 127.0.0.1:55450):
export PGPORT=55450 ASL_DB_HOST=127.0.0.2 ASL_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_ROLE=migration ASL_TEST_ISOLATED=1 \
    ASL_REPLAY_ISOLATED=1 ASL_RESEARCH_DB_HOST=127.0.0.2 ASL_RESEARCH_DB_NAME=asl_m1_replay_m6_b6c \
    ASL_CATALOG_DB_HOST=127.0.0.1 ASL_CATALOG_DB_NAME=asl_m1_m6_m7_b6c ASL_MARKET_ENABLED=0 ASL_EXECUTION_ENABLED=0 \
    ASL_EVALUATION_ENABLED=0 ASL_AGENTS_ENABLED=0 ASL_RESEARCH_ENABLED=0 ASL_SOURCES_ENABLED=0
.venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m7_control_bridge.py
.venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests/test_m6_shadows.py tests/test_m6_bridge.py \
    tests/test_m6_runner.py tests/test_m6_staging.py
.venv/bin/python <scratch>/mutate.py <copy> [<check> ...]   # each check switched off in <copy> in turn, its tests run, the file restored and compared
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .                                                     # repository root
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # repository root, PowerShell 7.4.6
```

`Migration7`'s steps outside Docker ran as in B6b's commands above, on 55450, on the recovery database `asl_m1_m5_m6_b6c_recovery`. A check of `0009` was switched off by editing the copy's migration, then dropping, creating and migrating `asl_m1_m6_m7_b6cmut` on 55450 before its tests ran. While investigating the bridge tests' first run below, the session also stopped both bridge-side clusters with `pg_ctl stop -m immediate` and started them again, mounted `/research-data` afresh, set the runner's storage reading four days back (`UPDATE research_control.storage SET observed_at = observed_at - interval '4 days'` in the research cluster's `postgres` database), and dropped the page cache (`echo 3 > /proc/sys/vm/drop_caches`), each before a run of the file.

Results, on the final code, after the independent review's fixes (plan §18, B6c):
- **The control tests:** `13 passed` in 23 s, twice, none skipped.
- **The control bridge tests:** the first run on the final code, the first after the clusters were started again, had `3 failed, 2 passed` in 17 s: in the first test the control's advance found the shadow's advance still with the runner (`{'outcome': 'SKIPPED', 'reason': 'RUNNER_BUSY'}`), and in the next two a runner pass left no mark (`IndexError: list index out of range` on the marks). Every later run passed: the first test alone (`1 passed`), then the file five times (`5 passed` in 23 to 26 s each), as it was and after each of the four changes above. The cause of the first run's failures was not found; that a runner pass did not finish its job in a process started just after the container's restart is inferred, not checked.
- **The M5, M6 and M7 files** with `test_generations.py`: `2 failed, 965 passed, 11 warnings, 56 errors` in 22 min, on the code at `e7212eb` (the application and `0009` unchanged since). The failures are B1's two. The errors are B1's four files, which need the two clusters (51), and `test_m7_control_bridge.py` (5); all ran in the bridge environment. B6c's first run, at `4f2991b`, also failed `test_m6_agents.py` and `test_m6_schema.py`, which listed every grant of an M7 table and now leave the two control tables to `test_m7_controls.py`.
- **M6's bridge-side files** (`test_m6_shadows.py`, `test_m6_bridge.py`, `test_m6_runner.py`, `test_m6_staging.py`): `62 passed, 77 warnings` in 323 s.
- **M0 to M4:** `324 passed, 1 warning, 13 errors` in 23 min, on the final code, as B6b's run. The errors are the 13 tests of `test_m1_account.py`, which needs the host `postgres`; they are `NOT RUN`.
- **`Migration7`'s steps:** both `VERIFIED` on the final `0009`, in 24 s: the static step's downgrade refused; the live step migrated in 0.27 s at the first attempt, held nothing stronger than `AccessShareLock` on its 21 protected relations, restored exactly and found 27 declared changes.
- **Each check matters.** 73 checks switched off one at a time: 70 failed at once; one switch was malformed and two did not fail, each a gap in the tests. With the added tests and the switch repaired, the three fail too (`1 failed` each), two on the guard's refusal (`a control period follows its ended predecessor`, `a control period starts after its freeze and before its run ended`).
- **Without a database:** `2 failed, 724 passed, 329 skipped, 1 warning, 305 errors` in 57 s: B6b's result plus B6c's one test that needs no database, and 17 in error for want of one (`Required M7 tests need a prepared isolated asl_m1_ database at migration 0009`, `Required B4 tests need the prepared isolated catalog and research fixtures`). The two failures are B0's and B1's. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches` (B6c changes no route or model). **Links** `0 broken link(s)`, with the three known warnings of plan 0003. **The profile check** `VERIFIED` (44 phases, 6 not built). B6c changes no web file, so the web checks were not run again.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B6c's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). `Migration7` again, since B6c changed `0009` and its helpers; `ShadowSchedule` again, since it now runs the control bridge tests as step `b6c-control-replay-tests` and records `b6c-control-replay.json`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Migration7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Comparison -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase ShadowSchedule -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

The same run can take B4's to B6b's phases, which have not run on the owner's PC either ([B6b](#execplan-0026-b6b-segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12)). `test_m1_account.py` runs in `Regression`'s M0 to M2 step.

## ExecPlan 0026 B6b: segments, decision measures, the single-coordinator variant and the comparison (2026-10-12)

By the cloud session of B0 to B6a, on branch `claude/m7-b0-hjaahq` from `main` at `a284329` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6b--segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** B6a's two scratch PostgreSQL 16 clusters (`initdb -A trust -U asl` under `/var/lib/postgresql/asl-m7-b6a` and `asl-m7-b6b`, on 127.0.0.1 ports 55449 and 55450 only, each holding only `asl_m1_` databases), kept for the next batch and removed by exact path when the session's batches end. Each database was dropped, created and migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head` on the final `0009`, then given `python -m tests.m6_support api-login` where a test signs in as `asl_api`. The suites change role logins cluster-wide, and a run stopped midway leaves them changed, so before each migration `asl_agent`, `asl_source`, `asl_research`, `asl_execution` and `asl_evaluation` were set `NOLOGIN` (`0008` refuses an M6 role that can log in), and `asl_market_worker` kept its login (M2's tests sign in as it). From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
# The phase's file, by its marker as the harness selects it, with its evidence file
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m7_b6b ASL_M7_COMPARISON_OUT=<dir>/comparison7.json \
    .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs -m comparison tests/test_m7_evaluation.py
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_generations.py tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m7_b6b .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    $(ls tests/test_*.py | grep -v "test_m[567]\|test_generations")                  # M0 to M4
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m7_schema.py tests/test_m7_binding.py tests/test_m7_policy.py          # after the schema test's fix
PGPORT=55449 ASL_DB_NAME=asl_m1_replay_m7_b6 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>   # R19 against B1's pinned values
.venv/bin/python <scratch>/mutate.py <copy of the tree>   # each check switched off in the copy, its tests run on 55450, the file restored and compared
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .                                                     # repository root
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # repository root, PowerShell 7.4.6
```

`Migration7`'s steps outside Docker, on 55450, as `tools/m6/engine.psm1` runs them on the recovery target (database `asl_m1_m5_m6_b6b_recovery`; `PREFIXES` widened in that one process so that `require_isolation` accepts the name):

```bash
ASL_DB_ROLE=migration .venv/bin/alembic upgrade 0007_m5_agent_runtime
.venv/bin/python -m tests.m6_migration seed-legacy
ASL_DB_ROLE=migration .venv/bin/python -c "import app.experiments.acceptance as a; a.PREFIXES += ('asl_m1_m5_m6_',); a.require_isolation(); a.seed_m4(); a.pilot_state()"
ASL_DB_ROLE=migration .venv/bin/alembic upgrade 0008_m6_research
.venv/bin/python -m tests.m6_migration seed-catalog
pg_dump -Fc <db> > before-0009.dump; createdb <db>_static; pg_restore -d <db>_static --exit-on-error before-0009.dump
ASL_DB_NAME=<db>_static .venv/bin/python -m tests.m7_migration static migration7-static.json
.venv/bin/python -m tests.m7_migration live migration7-locks.json migration7-live.json
```

A check of `0009` was switched off by editing the copy's migration, then dropping, creating and migrating `asl_m1_m6_m7_b6mut` on 55450 before its tests ran.

Results, on the final code, after the independent review's fixes (plan §18, B6b):
- **The phase's file:** `15 passed` in 71 s on a freshly migrated database, none skipped. Its evidence file was byte-identical to that of an earlier run on the same `app/` tree (SHA-256 `f0fecb53…`). Before the review: 13 tests, `13 passed` in 99 s.
- **The M5, M6 and M7 files** with `test_generations.py`: `3 failed, 950 passed, 10 warnings, 51 errors` in 12 min, on the code at `8680edb` (the application and `0009` unchanged since): B6a's result plus the fourteen tests of `test_m7_evaluation.py` at that commit, and one failure of B6b's own, `test_m7_schema.py`'s check of what `0009` adds, which did not know `evaluation_read`. With that test fixed, its file, `test_m7_binding.py` and `test_m7_policy.py` on the final code: `121 passed, 8 warnings` in 43 s. The other two failures and 51 errors are B1's to B6a's, which the plan names.
- **M0 to M4:** `324 passed, 1 warning, 13 errors` in 18 min, on the code at `8680edb`, as B6a's run. The errors are the 13 tests of `test_m1_account.py`, whose fixture connects to the host `postgres` by name (`failed to resolve host 'postgres'`); this session has no such host. Those 13 are `NOT RUN`.
- **R19:** The engine changed on the policy path (segments, the replay binding): `python -m tests.m7_engine`: `{"status": "VERIFIED", "failures": []}`, exit 0, in 160 s on the final code.
- **`Migration7`'s steps:** both `VERIFIED` on the code at `8680edb` (`0009` and the helpers unchanged since), in 19 s. Before the repair of its helpers (plan §17, B6b decision 10) the steps failed on generation 3's seed rows, then on `agent_approvals`' triggers and on `research_promotions`' state check.
- **Each change matters.** In a copy of the tree, 33 checks were switched off one at a time (26 in Python, and 7 in `0009`'s views and grants, each on a database migrated with the switched-off revision), each file restored and compared afterwards, and the tests written for each were run. 30 failed at once, each on the assertion written for it, or, for an hour paired across a gap, in the comparison's own arithmetic. Three did not, each a gap in the tests, now closed: the main account's policy engine kept its policy with no run (no test drove that engine there), a variant at `PROPOSED` passed (the test asked only for a status outside the list), and a decision probe whose snapshot binds the run was counted for it (no test had one). With the added tests, all three fail too.
- **Without a database:** `2 failed, 723 passed, 329 skipped, 1 warning, 288 errors` in 49 s: B6a's result plus B6b's six tests without a database, six skipped (`M3 integration requires an isolated asl_m1_ disposable database`) and three in error for want of a database (`failed to resolve host 'postgres'`). The two failures are B0's and B1's. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches` (B6b changes no route or model). **Links** 0 broken. **The profile check** `VERIFIED` (44 phases, 6 not built). B6b changes no web file, so the web checks were not run again.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B6b's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). `Migration7` again, since B6b changed `0009` and its helpers:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Migration7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Comparison -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

`Comparison` writes `comparison7.json` to the engine target's output directory and records its path and SHA-256 in the phase's record. The same run can take B4's to B6a's phases, which have not run on the owner's PC either ([B6a](#execplan-0026-b6a-promotion-approval-and-the-candidate-basis-2026-10-12)). `test_m1_account.py` runs in `Regression`'s M0 to M2 step.

## ExecPlan 0026 B6a: promotion approval and the candidate basis (2026-10-12)

By the cloud session of B0 to B5, on branch `claude/m7-b0-hjaahq` from `main` at `bf4e7bc` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6a--promotion-approval-and-the-candidate-basis-2026-10-12)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** Two scratch PostgreSQL 16 clusters of the session: `initdb -A trust -U asl` under `/var/lib/postgresql/asl-m7-b6a` and `asl-m7-b6b`, listening on 127.0.0.1 ports 55449 and 55450 only, each holding only `asl_m1_` databases; stopped and removed afterwards by exact path. Each database was migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head`, and dropped, created and migrated again after the review's fixes changed `0009`. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
# The phase's file, by its marker as the harness selects it
PGPORT=55450 ASL_DB_NAME=asl_m1_m6_m7_b6b .venv/bin/python -m pytest -q -p no:cacheprovider -m promotion_approval tests/test_m7_promotions.py
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_generations.py tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py
PGPORT=55449 ASL_DB_NAME=asl_m1_m6_m7_b6 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    $(ls tests/test_*.py | grep -v "test_m[567]\|test_generations")                  # M0 to M4
PGPORT=55450 ASL_DB_NAME=asl_m1_replay_m7_b6 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>   # R19 against B1's pinned values
.venv/bin/python <scratch>/mutate.py <copy of the tree>   # each check switched off in the copy, its tests run on 55450, the file restored and compared
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
.venv/bin/python -m app.agents.definitions_v3                                    # 0009's frozen rows, pasted after the prompts changed
python3 tools/check_links.py .                                                     # repository root
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # repository root, PowerShell 7.4.6
```

A check of 0009 was switched off by editing the copy's migration, then dropping, creating and migrating `asl_m1_m6_m7_b6mut` on 55450 before its tests ran.

Results, on the final code, after the independent review's fixes (plan §18, B6a):
- **The phase's file:** `11 passed` in 38 s, none skipped. Before the review: 7 tests, `7 passed`.
- **The M5, M6 and M7 files** with `test_generations.py`: `2 failed, 937 passed, 10 warnings, 51 errors` in 11 min: B5's result plus B6a's eleven tests. The same two failures and 51 errors as B1's to B5's, which the plan names. An earlier run, before the review, also failed an M6 source test at its first fetch, once; it passed in the final run (plan §18, B6a).
- **M0 to M4**, on the final code: `324 passed, 1 warning, 13 errors` in 18 min, as B5's run. The errors are the 13 tests of `test_m1_account.py`, whose fixture connects to the host `postgres` by name (`failed to resolve host 'postgres'`); this session has no such host. Those 13 are `NOT RUN`.
- **R19:** The engine changed only on the policy path (a candidate entry's declaration, its checks and its signal): `python -m tests.m7_engine`: `{"status": "VERIFIED", "failures": []}`, exit 0, in 179 s on the final code.
- **Each change matters.** In a copy of the tree, 28 checks were switched off one at a time (19 in Python, and 9 in `0009`'s guards, each on a database migrated with the switched-off revision), each file restored and compared afterwards, and the tests written for each were run: 27 fail, each on the assertion written for it or on the next layer's refusal (the guard, where the agent's own check was switched off). The one that does not is the probe's empty list of candidates: a probe's submission is refused in any case (`DispatcherAuth7`), so the list is hygiene, not authority. Before the review, 17 of 18 failed, the same one passing.
- **Without a database:** `2 failed, 717 passed, 323 skipped, 1 warning, 285 errors` in 49 s: B5's result plus B6a's eleven database tests, two skipped (`M3 integration requires an isolated asl_m1_ disposable database`) and nine in error for want of a database (`failed to resolve host 'postgres'`). The two failures are B0's and B1's. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches` (B6a changes no route or model). **Links** 0 broken. **The profile check** `VERIFIED` (44 phases, 7 not built). B6a changes no web file, so the web checks were not run again.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B6a's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase PromotionApproval -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

The same run can take B4's and B5's phases, which have not run on the owner's PC either ([B5](#execplan-0026-b5-generation-3-the-decision-loop-its-triggers-and-both-probe-suites-2026-10-11)). `test_m1_account.py` runs in `Regression`'s M0 to M2 step.

## ExecPlan 0026 B5: generation 3, the decision loop, its triggers and both probe suites (2026-10-11)

By the cloud session of B0 to B4, on branch `claude/m7-b0-hjaahq` from `main` at `d8000a6` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b5--generation-3-the-decision-loop-its-triggers-and-both-probe-suites-2026-10-11)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. No model was called.

**Run here (actual).** Two scratch PostgreSQL 16 clusters of the session: `initdb -A trust -U asl` under `/var/lib/postgresql/asl-m7-b5a` and `asl-m7-b5b`, listening on 127.0.0.1 ports 55447 and 55448 only, each holding only `asl_m1_` databases; stopped and removed afterwards by exact path. Each database was migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head`, and dropped, created and migrated again after the review's fixes changed `0009`'s frozen prompt row. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
# The five phases' markers, one at a time as the harness runs them; also with ASL_AGENTS_OFFLINE_TEST=1
for m in agent_offline7 dispatcher_auth7 agent_faults7 triggers7 decision_injection; do
  PGPORT=55447 ASL_DB_NAME=asl_m1_m6_m7_b5 ASL_AGENTS_OFFLINE_TEST=1 .venv/bin/python -m pytest -q -p no:cacheprovider -m $m tests/test_m7_agents.py
done
PGPORT=55447 ASL_DB_NAME=asl_m1_m6_m7_b5 .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_generations.py
PGPORT=55447 ASL_DB_NAME=asl_m1_m6_m7_b5 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    tests/test_generations.py tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py
PGPORT=55447 ASL_DB_NAME=asl_m1_m6_m7_b5 .venv/bin/python -m pytest -q -p no:cacheprovider -rfE \
    $(ls tests/test_*.py | grep -v "test_m[567]\|test_generations")                  # M0 to M4
PGPORT=55448 ASL_DB_NAME=asl_m1_replay_m7_b5 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>   # R19 against B1's pinned values
.venv/bin/python <scratch>/mutate.py <copy of the tree>   # each check switched off in the copy, its tests run on 55447, the file restored and compared
# The actual schema v3, measured and compared with B0's preview, without the CLI
.venv/bin/python ../../tools/m7/b5/schema_actual_v3.py --out <dir>/schema.json --report <dir>/report.json --outputs <dir>/outputs.json
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic ../../tools/m7/b5/*.py
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .                                                     # repository root
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c          # repository root, PowerShell 7.4.6
```

The decision suite's calls were read with a scratch pytest plugin that printed the probe run's row before the test's teardown cleared it (`-p` with `PYTHONPATH` set to the plugin's directory; not part of the repository).

Results, on the final code, after the independent review's fixes (plan §18, B5):
- **The five markers:** `AgentOffline7` `5 passed` in 14 s (the decision suite: `DECISION`, `calls_used` 26 of `calls_budget` 40, `PASSED`); `DispatcherAuth7` `17 passed` in 36 s; `AgentFaults7` `13 passed` in 31 s; `Triggers7` `6 passed` in 9 s; `DecisionInjection` `2 passed` in 5 s. `test_generations.py` `6 passed` in 1 s. Before the review: `5`, `15`, `11`, `5` and `2 passed`.
- **The M5, M6 and M7 files** with `test_generations.py`: `2 failed, 926 passed, 10 warnings, 51 errors` in 10 min: B4's result plus B5's 45 test cases. The same two failures and 51 errors as B1's to B4's, which the plan names. Before the review: `2 failed, 921 passed, 10 warnings, 51 errors` in 10 min.
- **M0 to M4**, before the review's fixes, which change no file they run: `324 passed, 1 warning, 13 errors` in 19 min. The errors are the 13 tests of `test_m1_account.py`, whose fixture connects to the host `postgres` by name (`failed to resolve host 'postgres'`); this session has no such host, and B4's command left the file out. Those 13 are `NOT RUN`.
- **R19:** `{"status": "VERIFIED", "failures": []}`, exit 0, in 154 s.
- **Each change matters.** Of 25 checks switched off one at a time, 24 make their tests fail; the review's hash in `submit_trade_intent` does not, because a draft is immutable (plan §18, B5).
- **The actual schema v3:** `OBSERVED` sha256 `47905a74…`, 10,755 bytes, 140 properties, depth 9, 85 enum values, within the documented limits, not identical to the preview; two runs gave the same report, and the review's fixes change no field of it ([INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m7-b5-agentstep-schema-v3-as-built--2026-10-11-execplan-0026)).
- **Without a database.** `2 failed, 717 passed, 321 skipped, 1 warning, 276 errors` in 49 s: B4's result plus B5's four tests that need no database, passed, and its 41 database cases in error for want of a database (`failed to resolve host 'postgres'`), as the M7 schema tests already were. The two failures are B0's and B1's. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches` (B5 changes no route or model). **Links** 0 broken. **The profile check** `VERIFIED` (44 phases, 8 not built). B5 changes no web file, so the web checks were not run again.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B5's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase AgentOffline7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase DispatcherAuth7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase AgentFaults7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Triggers7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase DecisionInjection -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

`AgentOffline7` also builds the CLI test image and the schema image of `tools/m7/b5` and runs the actual schema through the pinned CLI and the mock provider with no network; its record names the CLI's four runs. The same run can take B4's phases (`IntentEngine`, `IntentRaces`, `EngineParity7`, `Regression`) and `ResearchActivationRehearsal`, which have not run on B4's build ([B4](#execplan-0026-b4-stop-tightening-the-stop-in-force-and-the-trade-lists-exit-label-2026-10-11)). `test_m1_account.py` runs in `Regression`'s M0 to M2 step.

## ExecPlan 0026 B4: stop tightening, the stop in force and the trade list's exit label (2026-10-11)

By the cloud session of B0 to B3, on branch `claude/m7-b0-hjaahq` from `main` at `dbe17b1` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b4--stop-tightening-the-stop-in-force-and-the-trade-lists-exit-label-2026-10-11)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read.

**Run here (actual).** Four scratch PostgreSQL 16.15 clusters of the session, so that long runs need not wait for each other: `initdb -A trust -U asl` under `/var/lib/postgresql/asl-m7-b4`, `asl-m7-b4b`, `asl-m7-b4c` and `asl-m7-b4d`, listening on 127.0.0.1 ports 55443 to 55446 only, each holding only `asl_m1_` databases and one test run at a time; stopped and removed afterwards by exact path. Each database was migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head`. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 ASL_TEST_ISOLATED=1
M7="tests/test_m7_intents.py tests/test_m7_intent_races.py tests/test_m7_intent_units.py tests/test_m7_policy.py tests/test_m7_binding.py"
PGPORT=55443 ASL_DB_NAME=asl_m1_m6_m7_b4 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs $M7
PGPORT=55443 ASL_DB_NAME=asl_m1_m6_m7_b4 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs $M7   # both flags, as the harness sets them
PGPORT=55443 ASL_DB_NAME=asl_m1_m6_m7_b4 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py tests/test_generations.py
PGPORT=55444 ASL_DB_NAME=asl_m1_m7_b4 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m1_unit.py tests/test_m2_*.py tests/test_m3_*.py tests/test_m4_*.py
PGPORT=55445 ASL_DB_NAME=asl_m1_replay_m7_b4 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>   # R19 against B1's pinned values
PGPORT=55446 ASL_DB_NAME=asl_m1_m7_b4_checks .venv/bin/python <scratch>/mutate.py   # each change switched off, its tests run, the file restored and compared
env -u ASL_DATABASE_URL ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
python3 tools/check_links.py .                                                     # repository root
```

For the rehearsal's fix, PowerShell 7.4.6 (`/opt/pwsh/pwsh`) from the repository root: a scratch script that walks every function's and script's parameter block under `tools/` with `System.Management.Automation.Language.Parser` and lists assignments to a parameter's name; the two-line reproduction of the case collision; the module's parse; and `pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c`.

Results, on the final code:
- **The M7 files** with the policy and binding files: `148 passed`, with and without `ASL_REPLAY_ISOLATED=1` (115 s and 117 s); before the review's fixes `143 passed`, without the last races test.
- **The M5, M6 and M7 files** with `test_generations.py`: `2 failed, 881 passed, 51 errors` in 10 min: B3's result plus B4's 18 tests (before the review's fixes `876 passed`, without the last races test). The same two failures and 51 errors as B1's to B3's, which the plan names.
- **M1 to M4:** `318 passed` in 21 min on the final code and in 20 min before the review's fixes.
- **R19:** `{"status": "VERIFIED", "failures": []}`, exit 0, in 213 s on the final code (193 s before the review's fixes).
- **Each change matters.** Of sixteen changes switched off one at a time (ten of B4's first version, six of the review's fixes), fifteen make their tests fail; without the first-fill check they pass, because the state check refuses an unfilled position first (plan §18, B4).
- **Without a database.** `2 failed, 713 passed, 321 skipped, 1 warning, 235 errors` in 52 s: B3's result plus the 5 B4 unit tests passed and the 13 B4 database tests skipped. The two failures are B0's and B1's. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches` (B4 changes no route or model). **Links** `checked 94 Markdown files; 0 broken link(s)`. B4 changes no web file, so the web checks were not run again. **The rehearsal's fix:** the scan lists every assignment to a parameter's name (8 in functions and 23 in scripts before the fix, most of them a parameter normalizing its own value); read one by one, only the rehearsal's overwrote a parameter that is read afterwards as the original, and the fix removes that one; the reproduction prints `after: 0007_m5_agent_runtime`; the module parses with 0 errors and stays ASCII; the profile check prints `VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at 7b3e52c and their values; profiles/m7.psd1 is consistent (44 phases, 13 not built).`

**Observed on the owner's PC before B4** (by the session there, 2026-10-11 15:54 UTC, Windows PowerShell 5.1, no Docker): B1's step 3, `tools\m6\deploy-model.ps1`, exit 0, 17 scenarios, 76 of 76 expectations ([B1](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). Then, in run `m7-b3a` on B3's build beside the owner's pilot watch (16:34 to 17:45 UTC, Docker, PostgreSQL 17.11), B1's and B3's commands for `Build`, `EngineParity7`, `Migration7`, `PolicyDocument`, `IntentRaces`, `IntentEngine` and `Regression` passed on their first attempt with no skip, and `ResearchActivationRehearsal` failed on a check of the harness, fixed in B4's pull request ([plan §18](plans/0026-m7-agent-driven-main-decisions.md#run-m7-b3a-on-the-owners-pc-b1-to-b3s-phases-and-the-rehearsals-revision-2026-10-11)).

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root, in a run on B4's build after `Build`, under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase IntentEngine -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase IntentRaces -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase EngineParity7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Regression -WaitForWindow
```

The phases run the same files as for B3, which now hold B4's tests. Run `m7-b3a`, prepared from B3's code, does not include B4. Also for the PC, from the worktree of run `m7-b3a`:

```powershell
# The failed record's steps: rehearsal-revision-redeployed and rehearsal-rollback-refused-revision should read 0009
Get-Content .cache\m7\m7-b3a\ResearchActivationRehearsal-failed-20261011T174517042Z.json
# The run's containers, volumes and images, between HH:15 and HH:50 UTC; the evidence files stay
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId m7-b3a -Phase Clean -WaitForWindow
# The fixed profile check of #41
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c
```

`ResearchActivationRehearsal` again, on a build with the fix and a fresh run ID beside the pilot watch, after `Build`: `tools\m7-acceptance.ps1 -RunId <run> -Phase ResearchActivationRehearsal -WaitForWindow`.

## ExecPlan 0026 after B3: the profile check on a Windows checkout (2026-10-11)

By the cloud session of B0 to B3, on branch `claude/m7-b0-hjaahq` from `main` at `fd70434` (B3's merge) ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#after-b3--the-profile-check-on-a-windows-checkout-2026-10-11)). Linux, no Docker daemon.

**Run here (actual).** From the repository root, PowerShell 7.4.6:

```bash
git worktree add --detach <scratch dir> HEAD                       # then, in it, CRLF for every PowerShell file:
for f in tools/*.ps1 tools/profiles/*.ps1 tools/profiles/*.psd1; do sed -i 's/$/\r/' "$f"; done
pwsh -NoProfile -File <scratch dir>/tools/profiles/check-profiles.ps1 -Baseline 7b3e52c   # before and after the fix
pwsh -NoProfile -File tools/profiles/check-profiles.ps1 -Baseline 7b3e52c                 # the LF checkout
```

Before the fix, on the CRLF worktree: one line, `FAILED: the M6 entry's parameters: expected '...', found '...'`, as on the owner's PC. After it: `VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at 7b3e52c and their values; profiles/m7.psd1 is consistent (44 phases, 13 not built).` on both checkouts, and `FAILED: the M6 entry's parameters` again with one parameter renamed in the CRLF worktree (restored afterwards). The edited file stays ASCII.

**`NOT RUN`: for the owner's PC.** PROPOSED: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c` on Windows PowerShell 5.1, which should now print `VERIFIED: ...` and exit 0.

## ExecPlan 0026 B3: the engine's intake, the checks until the fill, the limits and the intent stream (2026-10-11)

By the cloud session of B0 to B2, on branch `claude/m7-b0-hjaahq` from `main` at `aea9d60` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b3--the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read. B0's PC steps, which ran before B3 on the owner's PC, are reported in the plan and under [B0](#execplan-0026-b0-m7-contracts-and-measurements-2026-10-10); their files stay on the PC.

**Run here (actual).** One scratch PostgreSQL 16.15 cluster of the session (`initdb` under `/var/lib/postgresql/asl-m7-b3`, listening on 127.0.0.1:55442 only) holding only `asl_m1_` databases, one test run at a time because roles belong to a cluster; stopped and removed afterwards. Each database was migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head`; the replay database was created through the migration role's own connection (`app.db.connection_options("migration")`, `AUTOCOMMIT`). From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 PGPORT=55442 ASL_TEST_ISOLATED=1
M7="tests/test_m7_intents.py tests/test_m7_intent_races.py tests/test_m7_intent_units.py tests/test_m7_policy.py tests/test_m7_binding.py"
ASL_DB_NAME=asl_m1_m6_m7_b3 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs $M7
ASL_DB_NAME=asl_m1_m6_m7_b3 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs $M7   # both flags, as the harness sets them
ASL_DB_NAME=asl_m1_m6_m7_b3 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py tests/test_generations.py
ASL_DB_NAME=asl_m1_m7_b3 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m1_unit.py tests/test_m2_*.py tests/test_m3_*.py tests/test_m4_*.py
ASL_DB_NAME=asl_m1_replay_m7_b3 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>   # R19 against B1's pinned values
env -u ASL_DATABASE_URL ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
pwsh -NoProfile -File ../../tools/profiles/check-profiles.ps1 -Baseline 7b3e52c   # PowerShell 7.4.6
pnpm run lint; pnpm run typecheck; pnpm run test:unit; pnpm run api:check; pnpm run check; pnpm run build   # apps/web
python3 tools/check_links.py .                                                     # repository root
```

All on the final code, after the review's fixes:
- **The M7 files.** The three B3 files with the policy and binding files: `130 passed`, with and without `ASL_REPLAY_ISOLATED=1` (99 s and 91 s). Before the review's fixes the same files gave `122 passed`. The M5, M6 and M7 files with `test_generations.py`: `2 failed, 863 passed, 51 errors` in 8 min 28 s, B2's result plus B3's 42 tests: the same two failures and the same 51 errors as B1's and B2's, which the plan names. Before the review's fixes it gave `2 failed, 855 passed, 51 errors`.
- **R19.** On B3's final code: `{"status": "VERIFIED", "failures": []}` in 187 s against B1's pinned values; also before the review's fixes.
- **Each change matters.** Switched off in place, each time restored from a copy and compared: with the cancel bar taken from the intent alone, with the cutoff quote read while the watermark is behind, without the validity check before a signal, and without the waiting reasons on an expiry, the test written for each fails.
- **M1 to M4.** Two runs on the final code, each `1 failed, 317 passed` (20 and 21 min), with a different test of the market worker failing each time; B2 had `318 passed`. The market worker loads none of the modules B3 changes (checked through `sys.modules` after importing it and the M2 test modules). In the first run `test_m2_integration.py`'s retention test found its old row still stored: the prune takes the 1,000 oldest rows a call, and the test does not clear market data first. Inferred cause: an earlier M1 to M4 run of this session, stopped part-way because it overlapped another run on the cluster, had left older fixture rows, which later tests cleared; the file passed alone afterwards (`6 passed`) and in the second run. In the second run `test_m2_reference_checks.py::test_rotation_waits_for_a_verified_clock[failed-request]`, which is timed by the wall clock, closed the feed later than it expects; it passed in the first run and three times alone (`2 passed` each). Neither is counted as passed in the run it failed.
- **Without a database.** `2 failed, 708 passed, 308 skipped, 1 warning, 235 errors`: B2's result plus the 11 B3 unit tests passed and the 31 B3 database tests skipped for want of a prepared isolated database. The two failures are B0's and B1's (`test_api.py` and `test_database.py` without a migrated database and the API's secret). These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches`. **Profiles** `VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at 7b3e52c and their values; profiles/m7.psd1 is consistent (44 phases, 13 not built).` The five edited PowerShell files parse and stay ASCII. **Web** lint and typecheck exit 0; `Tests 155 passed (155)`; `Generated TypeScript API types match`; `All matched files use Prettier code style!`; the production build exit 0, after removing a stale `apps/web/.output` that an earlier build of this session had left (lint read it: 67 parse errors; the directory is not tracked and was removed again). The web checks ran before the review's fixes, which changed no web file and left the OpenAPI schema as it was (checked again after them). **Links** `checked 94 Markdown files; 0 broken link(s)`.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root.

1. *The profile check and the phases' contracts* (no Docker): `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c`, then `tools\m7-acceptance.ps1 -RunId <run> -Phase IntentEngine -Describe` and the same for `IntentRaces`. `-Describe` refuses on PowerShell 7, so it was not run here.
2. *B3's phases*, in the same run as B1's and B2's and under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)), after `Build`, with `EngineParity7` and `Regression` again on B3's build:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase IntentEngine -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase IntentRaces -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase EngineParity7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Regression -WaitForWindow
```

   `IntentEngine` runs `tests/test_m7_intents.py` and `tests/test_m7_intent_units.py`, `IntentRaces` runs `tests/test_m7_intent_races.py`, each on the engine target, after the API login step, failing on any skip. Their windows (12 minutes each) are reserves, not measures.
3. *The step budget on an M6 or M7 build*, still not measured (plan §16): no command is proposed yet. The recommended way remains the unloaded `PerformanceEngine7` phase ([B0, step 5](#execplan-0026-b0-m7-contracts-and-measurements-2026-10-10)), which the profile assigns to B9.

## The live token-refresh check, first attempt: read-only reads of the normal application (2026-10-11)

By a session on the owner's PC (Windows, Git Bash and Windows PowerShell 5.1), on the owner's go-ahead of 10:53 UTC ([DECISIONS](../DECISIONS.md#2026-10-11--the-live-token-refresh-check-the-owners-go-ahead-and-why-it-could-not-start)). The check itself is NOT RUN ([ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#follow-up-after-closure--the-live-refresh-check-first-attempt-2026-10-11)). Every command below reads; none changes the normal application, and `codex_home`, `.env` and `secrets/` were not read.

**Run (actual), 11:03:43 to 11:06:54 UTC.**

```bash
docker ps -a --format '{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.CreatedAt}}'                     # 11:03:43
docker inspect --format '{{.Name}} started={{.State.StartedAt}} restarts={{.RestartCount}} health={{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}} failing={{if .State.Health}}{{.State.Health.FailingStreak}}{{else}}-{{end}} image={{.Image}}' \
  adaptive-spot-lab-agent-worker-1 adaptive-spot-lab-agent-runner-1 adaptive-spot-lab-agent-egress-1 adaptive-spot-lab-api-1 \
  adaptive-spot-lab-postgres-1 adaptive-spot-lab-execution-worker-1 adaptive-spot-lab-market-worker-1
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on -c statement_timeout=15000 -c lock_timeout=500" -e PGCONNECT_TIMEOUT=3 \
  adaptive-spot-lab-postgres-1 psql -X -U asl -d asl -At -v ON_ERROR_STOP=1 -f -              # 11:04:32; SELECTs inside BEGIN TRANSACTION READ ONLY
docker inspect --format '{{range .State.Health.Log}}{{.Start}} exit={{.ExitCode}} out={{.Output}}{{println}}{{end}}' adaptive-spot-lab-agent-worker-1   # 11:04:59
docker inspect --format 'health={{.State.Health.Status}} failing={{.State.Health.FailingStreak}} started={{.State.StartedAt}}' adaptive-spot-lab-agent-worker-1   # 11:06:54
docker ps --format '{{.Names}}'                                                                 # 11:06:54
```

```powershell
Get-CimInstance Win32_Process    # 11:05:21; filtered to codex, powershell, docker, bash, node, python and uv processes whose command line names a harness, Compose or a build
```

The SQL read `agent_runtime_state` (the state columns and the `runner` document's `reachable`, `busy`, `last_refresh`, `variant` and `codex_version`), the newest 14 rows of `agent_runtime_events`, `agent_provider_calls` with `agent_provider_outcomes` counted by provider, status and `auth_copyback`, and the newest five rows of `agent_probe_runs`.

**Results (OBSERVED).**
- **Containers.** The nine of the normal application, each `Up 28 hours`; ten of another project (`supabase_*_car-rental`), left alone; no `asl-` container, running or stopped. The seven inspected started at 2026-10-10T07:18:00Z with restart count 0. `agent-runner` `healthy` on `sha256:421793d7…`, `agent-egress` `healthy` on `sha256:ce07199d…`, `api` `healthy` on `sha256:44fd430f…`, `execution-worker` `healthy` on `sha256:5b02dbe1…`, `market-worker` on `sha256:31ee07e5…`.
- **`agent-worker`** on `sha256:64c0bad5…`: `unhealthy`, failing streak 44, then 66 at 11:06:54; the three newest checks (11:04:37, 11:04:45, 11:04:53) each `Health check exceeded timeout (3s)`.
- **Runtime.** `LOGIN_REQUIRED`, auth `PRESENT`, quota `UNKNOWN`, not latched, reason `PROFILE_DEFINITIONS_CHANGED`, version 6, updated 2026-10-08 22:20:10; no approved profile, no verification; heartbeat and runner observation 11:04:31. Runner: reachable, not busy, `last_refresh` `2026-10-02T11:20:20.365789819Z`, `REAL`, `codex-cli 0.159.2`.
- **Events.** Newest: 16 `WORKER_STARTED` 2026-10-10 07:18:09; 15 `STATE_CHANGED` and 14 `PROFILE_DRIFT` 2026-10-08 22:20:10; 13 and 12 `WORKER_STARTED` 2026-10-08 22:20:10 and 19:38:47; 11 `CAPABILITY_VERIFIED` 2026-10-02 13:12:24.
- **Calls.** 20, from 2026-10-02 13:07:49 to 13:12:09: `CODEX` 17 `COMPLETED`, 2 `TIMEOUT`, 1 `CANCELED`, `auth_copyback` empty on all. One probe run: `70099227…`, `PASSED`, 20 of 40 calls.
- **Host.** No harness, Compose or build process. Four `codex.exe` processes of the owner's Codex application, started 2026-10-10 11:53 to 11:56.
- **One statement of the read failed on the implementer's own mistake** (a `GROUP BY` that left out a selected column), in the read-only transaction, which ended there. The two statements after it, workflows by state and the newest runtime requests, were therefore not read.

**Re-read after the owner's `Continue`, 14:56:03 to 14:56:04 UTC (OBSERVED).** `docker ps -a` and the same forced read-only session, with the statement that failed left out and the newest five rows of `agent_runtime_requests` read this time. The nine containers `Up 32 hours`, every one with a health check `healthy`, `agent-worker` among them; no `asl-` container. Runtime as before: `LOGIN_REQUIRED`, version 6, heartbeat 14:56:03, runner reachable and not busy, `last_refresh` `2026-10-02T11:20:20.365789819Z`. Newest event still 16. 20 calls, the newest of 2026-10-02 13:12:09. One probe run. Three runtime requests in all, of 2026-10-02: `ACTIVATE` 11:12:31, `ENABLE` to `PROBE_ONLY` 13:07:38, `PROBE` 13:07:48.

**PROPOSED for the attempt that can run, NOT RUN.** After the owner has approved a new profile and started a probe run, the same forced read-only session, reading `auth_copyback` and `status` of the calls made since and `last_refresh` again. The recreate, on the owner's approval of that day, on the existing image, while the runner is not busy and outside HH:55–HH:10 UTC; its exact command is not fixed here and is shown to the owner before it runs.

**Documentation link check, 11:11 UTC, twice, the second time on the text with this paragraph, and at 14:57 UTC on the text with the re-read, VERIFIED.** In a read-only container without a network, the worktree mounted read-only (`tools/check_links.py`, the command of the earlier batches; no test container of this project ran beside it): `checked 93 Markdown files; 0 broken link(s)`, exit 0. Documents only: no application code, test, schema, image or setting changes, so no other check applies.

## ExecPlan 0026 B2: the policy documents, the manifest's slots and the engine's binding (2026-10-11)

By the cloud session of B0 and B1, on branch `claude/m7-b0-hjaahq` on top of B1's commits (`ae85361`) while B1's pull request waited for its merge; moved onto `main` after that merge (`ca09fba`, 2026-10-11) with its tree unchanged ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b2--the-policy-documents-the-manifests-slots-and-the-engines-binding-2026-10-11)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read.

**Run here (actual).** One scratch PostgreSQL 16.15 cluster of the session (`initdb` under `/var/lib/postgresql/asl-m7-b2`, listening on 127.0.0.1:55441 only) holding only `asl_m1_` databases, one test run at a time because roles belong to a cluster; stopped and removed afterwards. Each database was migrated with `ASL_DB_ROLE=migration .venv/bin/alembic upgrade head`. From `services/engine`:

```bash
export ASL_DB_HOST=127.0.0.1 PGPORT=55441 ASL_TEST_ISOLATED=1
ASL_DB_NAME=asl_m1_m6_m7_b2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs tests/test_m7_policy.py tests/test_m7_binding.py
ASL_DB_NAME=asl_m1_m6_m7_b2 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m7_policy.py tests/test_m7_binding.py                      # both flags, as the harness sets them
ASL_DB_NAME=asl_m1_m6_m7_b2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_*.py tests/test_generations.py
ASL_DB_NAME=asl_m1_m7_b2 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m1_unit.py tests/test_m2_*.py tests/test_m3_*.py tests/test_m4_*.py
# R19's baseline, on B1's tree (a worktree at ae85361 with tests/m7_engine.py copied in), then the comparison on B2's
ASL_DB_NAME=asl_m1_replay_m7_b1 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --measure --out <dir>
ASL_DB_NAME=asl_m1_replay_m7_b2 ASL_REPLAY_ISOLATED=1 .venv/bin/python -m tests.m7_engine --out <dir>
env -u ASL_DATABASE_URL ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
pwsh -NoProfile -File ../../tools/profiles/check-profiles.ps1 -Baseline 7b3e52c   # PowerShell 7.4.6
pnpm run lint; pnpm run typecheck; pnpm run test:unit; pnpm run api:check; pnpm run check; pnpm run build   # apps/web
python3 tools/check_links.py .                                                     # repository root
```

All on the final code, after the review's fixes:
- **The M7 files.** `test_m7_policy.py` and `test_m7_binding.py`: `88 passed`, with and without `ASL_REPLAY_ISOLATED=1`. Before the fix the review asked for, the install refusal test failed with that flag (`DID NOT RAISE`). The M5, M6 and M7 files with `test_generations.py`: `2 failed, 821 passed, 51 errors`, B1's result plus the 88; the same two failures and the same 51 errors as B1's, which the plan names.
- **R19.** On B1's tree, `--measure`: `OBSERVED`, the values now pinned in `tests/m7_engine.py`. On B2's: `{"status": "VERIFIED", "failures": []}` in 189 s, and again on the final code in 210 s. In a scratch copy with one `SELECT 1` added to every step it printed `FAILED` with exactly the twelve statement counts and digests, and nothing else; the copy was deleted.
- **Each check matters.** Switched off in place, each time restored from a copy and compared: with `check_binding` returning at once, four of the eleven binding tests fail; without the two new start refusals, their two tests fail; with the old slot rule, three tests fail.
- **M1 to M4.** `318 passed` in 22 min 37 s. B1 had `1 failed, 317 passed`; `test_m3_throughput.py`'s asynchronous commit test passed this time and is not counted as fixed.
- **Without a database.** `2 failed, 697 passed, 277 skipped, 1 warning, 235 errors`: B1's result plus the policy tests' 73 static tests passed, their 4 database tests erroring at setup and the 11 binding tests skipped for want of a prepared isolated database. These are `NOT RUN`, not passed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches`. **Profiles** `VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at 7b3e52c and their values; profiles/m7.psd1 is consistent (44 phases, 15 not built).` With `PolicyDocument`'s window and deadline removed, or its implementation renamed `B2_ISOLATED`, it printed `FAILED` lines; the file was restored from a copy and compared. Without `-Baseline` it now refuses, because `HEAD` holds no M6 values in code. **Web** lint and typecheck exit 0; `Tests 155 passed (155)`; `Generated TypeScript API types match`; `All matched files use Prettier code style!`; the production build exit 0. The five edited PowerShell files parse and stay ASCII. **Links** `checked 93 Markdown files; 0 broken link(s)`. The web checks ran before the review's fixes, which changed no web file and left the OpenAPI schema as it was (checked again after them).

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root.

1. *The profile check and the phases' contracts* (no Docker): `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c`, then `tools\m7-acceptance.ps1 -RunId <run> -Phase PolicyDocument -Describe` and the same for `EngineParity7`. `-Describe` refuses on PowerShell 7, so it was not run here.
2. *B2's phases*, in the same run as B1's and under the same rule for heavy slots ([B1, step 2](#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)), after `Build`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase PolicyDocument -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase EngineParity7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Regression -WaitForWindow
```

   `PolicyDocument` runs `tests/test_m7_policy.py` and `tests/test_m7_binding.py` on the engine target and fails on any skip. `EngineParity7` runs `python -m tests.m7_engine` on the research target and passes only on `VERIFIED` with no failure. `Regression` is M6's, kept: the M3 and M4 files on the fast path and the M0 to M2 database, account, market route and unit files, on the M7 build (the cloud run above was not on the fast path). Their windows (12 and 15 minutes) are reserves, not measures.

## ExecPlan 0026 B1: migration 0009, the generation lookup and the harness profile (2026-10-10)

By the cloud session of B0, on branch `claude/m7-b0-hjaahq` on top of B0's commits, then moved onto `main` after B0's merge (`7b3e52c`) with its tree unchanged ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b1--migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read.

**Run here (actual).** Scratch PostgreSQL 16.15 clusters of the session (`initdb` under `/var/lib/postgresql/<dir>`, started with `pg_ctl`, listening on 127.0.0.1 only), each holding only `asl_m1_` databases, one test run per cluster at a time because roles belong to a cluster; stopped and removed afterwards. From `services/engine`:

```bash
ASL_DB_HOST=127.0.0.1 ASL_DB_NAME=<asl_m1_ database> .venv/bin/alembic upgrade head        # also downgrade 0008_m6_research
ASL_DB_HOST=127.0.0.1 ASL_DB_NAME=<asl_m1_ database at 0009> ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs tests/test_m7_schema.py tests/test_generations.py
ASL_DB_HOST=127.0.0.1 ASL_DB_NAME=<...> ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m5_*.py tests/test_m6_*.py tests/test_m7_schema.py tests/test_generations.py
ASL_DB_HOST=127.0.0.1 ASL_DB_NAME=<...> ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_m1_unit.py tests/test_m2_*.py tests/test_m3_*.py tests/test_m4_*.py
ASL_DB_HOST=127.0.0.1 ASL_DB_NAME=<...> ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider -rfEs \
    tests/test_api.py tests/test_database.py tests/test_m1_account.py   # the host name postgres pointed at the scratch cluster for this run
env -u ASL_DATABASE_URL ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests   # no database
pg_dump --schema-only --no-owner <database migrated straight to 0008>    # compared with the same dump of a 0009 database downgraded to 0008
.venv/bin/ruff check --no-cache app tests alembic
.venv/bin/python -m app.export_openapi --check
pwsh -NoProfile -File ../../tools/profiles/check-profiles.ps1            # PowerShell 7.4.6
pnpm run lint; pnpm run typecheck; pnpm run test:unit; pnpm run api:check; pnpm run check; pnpm run build   # apps/web
python3 tools/check_links.py .                                           # repository root
```

- **Migration `0009` and its tests.** `test_m7_schema.py` and `test_generations.py`: `37 passed`. The M5, M6 and M7 files: `2 failed, 733 passed, 51 errors`; the M1 to M4 files: `1 failed, 317 passed`; `test_api.py`, `test_database.py` and `test_m1_account.py`: `19 passed`. Every failure and error is one the same files gave on code before B1 (`4 failed, 1018 passed, 64 errors` for the whole directory at `0008`); which and why is in the plan. The schema dump of a `0009` database downgraded to `0008` equals that of a database migrated straight to `0008`.
- **`Migration7`'s steps outside Docker** (a helper of the session, a third scratch cluster): static step and live step `VERIFIED`; figures in the plan.
- **Without a database.** `2 failed, 624 passed, 266 skipped, 1 warning, 231 errors`: B0's result plus `test_generations.py`'s 5 and `test_m7_schema.py`'s 4 static tests passed, and its 28 database tests erroring at setup for want of a prepared isolated database. These 499 are `NOT RUN`, not passed.
- **The harness review's fixes.** The profile check again after them: `VERIFIED` as below. In a scratch clone, fifteen changes of the two profiles (stem, run root, names, milestones, revisions, product kinds, required phases, static tests, a deadline) each made it exit 1. The five edited PowerShell files parse without error and stay ASCII. The other-stack refusal's parsing was tried on sample `docker ps` lines; the refusal itself needs Docker and is `NOT RUN`.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches`. **Profiles** `VERIFIED: profiles/m6.psd1 holds the 32 phases of tools/m6-acceptance.ps1 at HEAD and their values; profiles/m7.psd1 is consistent (44 phases, 17 not built).` **Web** lint and typecheck exit 0; `Tests 155 passed (155)`; `Generated TypeScript API types match`; `All matched files use Prettier code style!`; the production build exit 0. Lint read the build output a previous build had left in `apps/web/.output` and failed on it; with that ignored directory removed it passed. **Links** `checked 93 Markdown files; 0 broken link(s)`.
- A helper of the session ran `docker info` once by mistake; there is no daemon here and nothing ran.

**`NOT RUN`: for the owner's PC.** Each command below is PROPOSED, not verified. Windows PowerShell 5.1 from the repository root.

1. *The M6 profile reproduces today's harness* (reads files and git only; no run, no Docker): `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\profiles\check-profiles.ps1 -Baseline 7b3e52c` (B0's merge, the commit before B1). It prints `VERIFIED: ...` and exits 0, or lists each difference and exits 1. Then, also without Docker, `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Migration7 -Describe` and the same with `tools\m6-acceptance.ps1 -Phase Build`, which print a phase's contract under Windows PowerShell 5.1.
2. *B1's phases of the M7 profile.* These are heavy test stacks beside the pilot. They run in the next free heavy slot after any M6-B gate run waiting for it, decided on the owner's delegation on 2026-10-11 ([DECISIONS](../DECISIONS.md#2026-10-11--m7-b1-the-owner-has-b0-merged-and-leaves-the-heavy-run-timing-and-the-epoch-hold-to-the-implementer)); the pilot watch runs beside them with `-Harness m7`, and each `-Execute` of it is asked for in chat:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Migration7 -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase ResearchActivationRehearsal -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m7-acceptance.ps1 -RunId <run> -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId <run> -Harness m7 -MaxHours 12 -EndFile <file that ends it> -Execute
```

   `Build` runs `tests/test_m7_schema.py`'s static tests with M6's; `Migration7` runs the whole file on its engine database and `tests/m7_migration.py` on an M6 recovery copy. The M5 and M6 agent suites run in the kept phases `AgentOffline6`, `DispatcherAuth6` and `AgentFaults6`. The 17 phases later batches build answer `NOT RUN: <phase> is not implemented` and exit 1.
3. *The deploy model* with the new rollback case: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository <repo> -Work <scratch dir>`; it expects 76 expectations.
4. *M6 on the refactored harness.* The only full proof that M6's harness is unchanged is an M6 run on it. B1 also changes what an M6 run executes: `m6-deploy.ps1` and its model, and the refusal while another isolated stack runs (plan §18, harness review point 3). Step 3 runs first. The next M6-B gate run on a build with B1 is that proof; until then the profile check of step 1 and the static comparisons above are the evidence.

## ExecPlan 0026 B0: M7 contracts and measurements (2026-10-10)

By a cloud session on branch `claude/m7-b0-hjaahq` from `main` at `1da608f` ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b0--contracts-measurements-and-the-harness-sketch-2026-10-10)). Linux, no Docker daemon. No command addressed the normal application or its database; `.env`, `secrets/` and `codex_home` were not read.

**Run here (actual).** From `services/engine` with the locked environment (`uv run --frozen --no-sync`), and from `apps/web` after `pnpm install --frozen-lockfile --ignore-scripts` at the repository root:

```bash
uv run --frozen --no-sync python ../../tools/m7/b0/schema_preview_v3.py --out <scratch>/schema-v3-preview.json --report <scratch>/schema-v3-report.json
uv run --frozen --no-sync python ../../tools/m7/b0/schema_probe_v3.py --self-check <scratch>/schema-v3-preview.json
ASL_TRIAL_DSN="host=<socket dir> port=55432 dbname=asl_m1_m7_b0_epoch user=postgres" \
    uv run --frozen --no-sync python ../../tools/m7/b0/epoch_hold_trial.py --out <scratch>/epoch-hold-trial-pg16.json
.venv/bin/ruff check --no-cache app tests alembic ../../tools/m7/b0/*.py
uv run --frozen --no-sync python -m app.export_openapi --check
env -u ASL_DATABASE_URL ASL_TEST_ISOLATED=1 .venv/bin/python -m pytest -q -p no:cacheprovider tests
pnpm run lint; pnpm run typecheck; pnpm run test:unit; pnpm run api:check; pnpm run check; pnpm run build
python3 tools/check_links.py .
```

- **Schema v3 preview.** `OBSERVED`: 144 properties, depth 9, 1,878 characters, 49 enumeration values, strict, 10,488 bytes, SHA-256 `a9eeb963da3ff1e10630d35900a49da919c113d91406fabe1bd45a9e154dedbb`, `within_documented_limits: true`; schema v2 in the same run 111 properties, 8,309 bytes, SHA-256 `bb328865ac8158ef6199843023216b689a1585c8c29d80891155fd27583aa05b`. Run twice; the same hash both times. Self-check: both SYNTHETIC outputs valid.
- **Epoch trial, script check.** On a scratch PostgreSQL 16.15 cluster of the session (`initdb` with trust authentication, a socket directory, no TCP listener), stopped and its directory removed afterwards; run three times as the script gained cases after the review. `OBSERVED` in the last run: `g2_pass: true`, `g1_pass: false`, `g1_pass_one_engine_cases: false`; `NOT_STARVED` for one engine with a gap, back to back, and with sparse agent checks (with and without the API's timeouts); `STARVED` for one engine bridged by overlapping agent checks, for those agent checks alone, and for both stress cases; no case `INCONCLUSIVE`. The figures are in the plan. Not the gate, which is PostgreSQL 17.
- **The latency query** was run once on a second scratch cluster against stub tables holding one SYNTHETIC row, to check that it parses and runs; the cluster was stopped and removed.
- **Ruff** `All checks passed!`. **OpenAPI** `FastAPI OpenAPI schema matches`. **Web** lint and typecheck exit 0; `Tests 155 passed (155)`; `Generated TypeScript API types match`; `All matched files use Prettier code style!`; the production build exit 0. **Links** `checked 93 Markdown files; 0 broken link(s)`.
- **Engine tests without a database.** `2 failed, 615 passed, 266 skipped, 1 warning, 203 errors`. Every test that did not pass needs what this session lacks: 266 skip without an isolated `asl_m1_` database; 203 fail at setup with "Required M6 tests need a prepared isolated asl_m1_m6_ database" or "Required B4 tests need the prepared isolated catalog and research fixtures"; and two fail for the missing environment, `test_database.py` without a migrated database and `test_api.py` without the API's database secret (`/run/secrets/api_db_password`). These 471 are `NOT RUN`, not passed. `ASL_TEST_ISOLATED=1` marks this container as an isolated test environment, as the harness does; without it 53 transport tests refuse their test-only overrides.

**`NOT RUN`: for the owner's PC.** On 2026-10-10 the owner left steps 1, 2 and 4 to the implementer, who decided yes to each ([DECISIONS](../DECISIONS.md#2026-10-10--m7-b0-the-owner-leaves-the-latency-read-and-the-two-small-runs-to-the-implementer-and-approves-the-harness-profile)). Steps 1 and 2 run in one sitting before B3, with these conditions: only between HH:07 and HH:58 UTC; never while an M6-B gate run holds the one heavy slot (M7-OD1); one after the other; and the feed incidents of the Markets page (`http://127.0.0.1:3000/markets`, "Recent feed incidents") read before step 1 and after step 2. A `QUEUE_OVERLOAD` or `COLLECTION_GAP` stamped after the sitting began ends it: the next step is not run, and the incident is reported. The pilot watch stops harness runs only; these containers run a minute or two each and are removed at once. Step 4 may run at any time, preferably before B2. Windows PowerShell 5.1 from the repository root; `<repo>` is its full path. Each command below is PROPOSED, not verified.

1. *Schema v3 through the pinned CLI and the mock* (one container without a network; no model call, no credential):

```powershell
New-Item -ItemType Directory -Force .cache\m7\b0\schema-out | Out-Null
docker build --progress plain --target test -f services/engine/Dockerfile -t asl-m7-b0-engine-tests .
docker build --progress plain --target test -f services/agent-runner/Dockerfile -t asl-m7-b0-cli-test .
docker build --progress plain -f tools/m7/b0/Dockerfile --build-arg ENGINE_IMAGE=asl-m7-b0-engine-tests --build-arg CLI_IMAGE=asl-m7-b0-cli-test -t asl-m7-b0-schema-probe .
docker run --rm --network none --read-only --cpus 1 --memory 768m --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges:true --name asl-m7-b0-schema-once --tmpfs /tmp:rw,noexec,nosuid,nodev,size=134217728,uid=10002,gid=10002,mode=0700 --user 10002:10002 --mount "type=bind,source=<repo>\.cache\m7\b0\schema-out,target=/out" asl-m7-b0-schema-probe
```

   It writes `schema-probe-v3.json` with `VERIFIED` or `FAILED` and exits 1 on a failure.

2. *The epoch-hold gate on PostgreSQL 17* (a database on an internal network and in memory; the engine test image of step 1):

```powershell
$bytes = New-Object byte[] 24; [Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$pw = -join ($bytes | ForEach-Object { $_.ToString('x2') })
New-Item -ItemType Directory -Force .cache\m7\b0 | Out-Null
docker network create --internal asl-m7-b0-epoch
docker run -d --name asl-m7-b0-epoch-pg --network asl-m7-b0-epoch --tmpfs /var/lib/postgresql/data -e POSTGRES_PASSWORD=$pw -e POSTGRES_DB=asl_m1_m7_b0_epoch postgres:17.11-alpine3.24
docker exec asl-m7-b0-epoch-pg pg_isready -U postgres -d asl_m1_m7_b0_epoch   # repeat until it answers "accepting connections"
docker run --rm --network asl-m7-b0-epoch --read-only --tmpfs /tmp --cpus 1 --memory 512m --pids-limit 256 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 --name asl-m7-b0-epoch-trial -e "ASL_TRIAL_DSN=host=asl-m7-b0-epoch-pg dbname=asl_m1_m7_b0_epoch user=postgres password=$pw" --mount "type=bind,source=<repo>\tools\m7\b0,target=/opt/m7,readonly" --mount "type=bind,source=<repo>\.cache\m7\b0,target=/out" asl-m7-b0-engine-tests .venv/bin/python /opt/m7/epoch_hold_trial.py --out /out/epoch-hold-trial-pg17.json
docker rm -f asl-m7-b0-epoch-pg
docker network rm asl-m7-b0-epoch
```

   About two minutes. It prints `g1_pass`, `g1_pass_one_engine_cases`, `g2_pass` and a verdict per case; the JSON holds every timing. The script refuses a cluster that holds the application's database or identities.

3. *Clean-up of steps 1 and 2*, by exact name once their JSON is recorded: `docker image rm asl-m7-b0-schema-probe asl-m7-b0-cli-test asl-m7-b0-engine-tests`.

4. *The live step latency* — **a read-only command against the normal database, approved on the owner's delegation of 2026-10-10 for one run**:

```powershell
New-Item -ItemType Directory -Force .cache\m7\b0 | Out-Null
Get-Content -Raw -LiteralPath tools\m7\b0\probe-latency.sql | docker exec -i -e "PGOPTIONS=-c default_transaction_read_only=on -c statement_timeout=15000 -c lock_timeout=200" -e PGCONNECT_TIMEOUT=3 adaptive-spot-lab-postgres-1 psql -X -q -U asl -d asl -A -t -v ON_ERROR_STOP=1 -f - | Set-Content -Encoding ascii .cache\m7\b0\probe-latency.json
```

   One transaction, `READ ONLY`, as the API identity, on the agent tables only; it ends with `ROLLBACK`. It writes `.cache\m7\b0\probe-latency.json`: timings, models, token counts and states only, no prompt or output.

5. *The step budget on the M6 build*: no command is proposed yet. The recommended way is the unloaded `PerformanceEngine7` phase of the M7 harness profile, which does not exist before the owner answers on the profile (ExecPlan 0026 §18).

## ExecPlan 0025: research job cost and the analyst's search (2026-10-09)

By the session of [ExecPlan 0025](plans/0025-research-job-cost-and-search.md), on branch `claude/m6-performance` from
`main` at `105dd2d` (with `cb4bbd4` and later `ba2d560` merged in). Windows PowerShell 5.1, Docker Desktop. Every
stack was an isolated test run of `tools\m6-acceptance.ps1`: `m6-p1a` for the scratch measurements, `m6-p2a` for the
verification and its measurements. Nothing was deployed, enabled or approved, and `.env`, `secrets/` and `codex_home`
were not read.

**The one thing that addressed the normal application** was the pilot watch, read-only, beside every test run, as the
owner's rule of 2026-10-07 has it. It was started by this session without a separate approval in chat for each
start ([ExecPlan 0025 §14](plans/0025-research-job-cost-and-search.md#14-progress-and-completion-evidence) says
under which reading, and that this is reported to the owner):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId <run> -MaxHours 12 -EndFile <file that ends it> -Execute
```

OBSERVED in its logs (07:07 to 08:36, 11:07 to 13:08 and 13:08 to 16:25 UTC): lease epoch 5 held at every reading, no
`PROTECTION_UNAVAILABLE` row, every hourly `SNAPSHOT` report there. **At 16:24:56 UTC it recorded one `QUEUE_OVERLOAD`
of the normal market worker, wrote `.cache\m6\PILOT-DIFFERENCE.txt` and stopped every container of run `m6-p2a`**
(the harness's `Stop` phase, exit 0 at 16:25:02 UTC), as the owner's rule has it. The other market incidents it
recorded without judging them one by one are listed with their times in ExecPlan 0025 §14. No test run was started
after the stop.

**Phases** (each started by a scratch runner under `.cache\m6`, which only chooses what to ask the harness for next):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <run> -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <run> -Phase <Phase> -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <run> -Phase EngineParity -WaitForWindow -BaselineRun m6-b2base
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <earlier run> -Phase Clean -WaitForWindow
```

**Scratch measurements** (not a phase; the Compose calls `PerformanceResearch` makes, with other arguments, on run
`m6-p1a`'s engine and research targets; `<engine>` and `<research>` stand for
`docker compose --project-directory .cache\m6\<run>\<target> -f ...\compose.yaml -p asl-m6-<run>-<target> --env-file ...\compose.env`):

```powershell
<engine> up -d --wait --wait-timeout 60 fixture-postgres
<engine> run --rm --no-deps engine-tests .venv/bin/python -m app.research.migrate
<research> up -d --wait --wait-timeout 60 fixture-postgres
<research> run --rm --no-deps research-runner .venv/bin/python -m app.research.runner --initialize
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research load 10
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research seal 9.6
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research request SCREEN <dataset>   # or FULL
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research relay
<research> run --no-deps --name <name> -e ASL_RESEARCH_ENABLED=1 research-runner .venv/bin/python -m app.research.runner --once
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research relay
<research> run --rm --no-deps bridge-tests .venv/bin/python -m tests.m6_performance research job <job> 2760
```

The profiled passes ran the runner as `.venv/bin/python -m cProfile -s cumulative -m app.research.runner --once`.

**Development checks** (not acceptance evidence): lint and the tests that need no database, on the working tree or on
a patched copy of it, in a container of a run's test image without network; and named database tests with the tree
(or the copy) mounted read-only over that image, on the run's agent or research fixture database while no phase had
a container up:

```bash
tar cf - app tests pyproject.toml alembic | docker run --rm -i --network none asl-m6-<run>-engine-tests sh -c '<unpack to /tmp/w/services/engine; .venv/bin/python -m ruff check --no-cache app tests alembic/versions/0008_m6_research.py; .venv/bin/python -m pytest -q -p no:cacheprovider <files> -k <names>>'
```

```powershell
<agent> run --rm --no-deps -e ASL_TEST_FAST_PATH=1 -e ASL_REPLAY_ISOLATED=0 -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis -v <tree>\services\engine\app:/workspace/services/engine/app:ro -v <tree>\services\engine\tests:/workspace/services/engine/tests:ro engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider -x tests/test_m3_throughput.py -k "<names>"
<research> up -d --wait --wait-timeout 60 fixture-postgres
<research> run --rm --no-deps -v <copy>\app:/workspace/services/engine/app:ro -v <copy>\tests:/workspace/services/engine/tests:ro engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m6_runner.py -k "renewal or free_space"
docker stop asl-m6-m6-p2a-research-fixture-postgres-1
```

**Documentation link check** (a read-only container without a network, the repository mounted read-only):

```powershell
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <repository>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

At 14:12 UTC on the tree with `main` merged in, and again on these records before the merge:
`checked 93 Markdown files; 0 broken link(s)`, exit 0, both times.

**GitHub** (`gh`, the owner's login on this host): `git fetch origin main`, `git merge --no-ff --no-commit origin/main`
and its commit, `git push origin claude/m6-performance`, `gh pr create --draft`, `gh pr view 35 --json ...`,
`gh pr edit 35 --body-file <file>`, `gh pr ready 35`, and the merge, which follows this record and is not claimed
here: `gh pr merge 35 --merge --match-head-commit <head>`.

Results, with every figure against its bound, are in [ExecPlan 0025 §14](plans/0025-research-job-cost-and-search.md#14-progress-and-completion-evidence).

**The renewal change, rewritten (actual, 2026-10-17).** The cloud session that builds M7, on the research scratch cluster of the M7 batches (PostgreSQL 16.15 on 127.0.0.2 port 55450, socket directory `/tmp/pgsock-r`), the database `asl_m1_replay_m6_b6c` made there by B6c. `<pw>` is a scratch file the local trust authentication ignores; `<plugin>` is a scratch directory holding `roomy.py`, which sets `queue.storage` to report 100 GiB free (this container has 28 GB, under the research floor). From `services/engine`:

```bash
.venv/bin/ruff check --no-cache app/research/runner.py tests/test_m6_runner.py      # All checks passed!
.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m6_runner.py -k "(renew or reading or late_start) and not long_batch"   # 4 passed, 25 deselected
PYTHONPATH=$PWD:<plugin> PGPORT=55450 ASL_DB_HOST=127.0.0.2 ASL_DB_NAME=asl_m1_replay_m6_b6c ASL_DB_ROLE=migration \
    ASL_TEST_ISOLATED=1 ASL_REPLAY_ISOLATED=1 ASL_RESEARCH_DB_HOST=127.0.0.2 ASL_RESEARCH_DB_NAME=asl_m1_replay_m6_b6c \
    ASL_DB_PASSWORD_FILE=<pw> .venv/bin/python -m pytest -q -p no:cacheprovider -p roomy -rfE tests/test_m6_runner.py -k long_batch
# 1 passed in 25.04 s; with app/research/runner.py from main (05d8ef9): 1 failed, Refused FENCED after research_heartbeat_failed OperationalError
# the same command without -k: 28 passed, 1 failed in 159 s; the failure is test_real_worker_process_loss_one_retry_and_stale_fence,
# whose child process does not load the scratch plugin, so its claim refuses on this container's free space (assert j)
```

The two halves of the change were each taken out once in a scratch copy of `runner.py` and the database-free tests run: without the retry, `test_a_renewal_that_failed_is_asked_again_and_the_reading_goes_on` failed; without the refusal's end, `test_a_refused_renewal_ends_the_renewals_not_the_reading` failed. Proposed for the owner's PC (`NOT RUN`): `ResearchRunner` (in the M6 and M7 harnesses, `tools/m6/research.psm1`) on the build that carries the change, which runs `tests/test_m6_runner.py` on PostgreSQL 17 with no skip allowed.

## The pilot check counts market incident codes without regard to letter case (2026-10-09)

By the session of this change, in a worktree of the repository on branch `claude/vigilant-grothendieck-4a7403`,
from `main` at `105dd2d`. Windows PowerShell 5.1.26100.9444. No command addressed the normal `adaptive-spot-lab`
project, no script was run with `-Execute`, and nothing was built, deployed, enabled or approved
([DECISIONS](../DECISIONS.md#2026-10-09--the-pilot-check-counts-the-market-workers-codes-without-regard-to-letter-case)).

**The changed SELECT.** `tools\m6-pilot-check.ps1 -RunId <run> -Since <UTC>` without `-Execute` prints its command
scope and its fixed SELECT and makes no Docker call. The market incidents part, as it was and as it is; the rest
of the SELECT is unchanged:

```sql
-- until 2026-10-09
(SELECT code, count(*) AS n FROM market_incidents
 WHERE occurred_at >= TIMESTAMPTZ '<the given instant>' GROUP BY code) m
-- since
(SELECT upper(code) AS code, count(*) AS n FROM market_incidents
 WHERE occurred_at >= TIMESTAMPTZ '<the given instant>' GROUP BY upper(code)) m
```

**Checked without Docker, 06:35:42 to 06:37:26 UTC, on the final scripts** (`<work>` is an existing scratch
directory; each model makes a folder in it and removes it again):

```powershell
# the parser on every script and module under tools, and a count of the bytes outside ASCII
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6\pilot-check-model.ps1 -Repository <repository> -Work <work>
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository <repository> -Work <work>
```

OBSERVED:

- **The parser:** 46 files, 0 errors, no byte outside ASCII.
- **The pilot check model** (new): exit 0, 4 scenarios, 15 expectations, 0 failed. In it a function answers for
  `docker` and for the database; no Docker command runs and no SQL is executed.
- **The deploy model** (every reading now holds one market incident code in two spellings): exit 0, 17 scenarios,
  75 expectations, 0 failed.
- **`Test-M6PilotRules` and `Test-M6EnvFileRules`,** called inside `tools/m6/rollout.psm1` as loaded: 57 and 47
  cases, all held. The module was edited; these two functions were not.
- **The lines of `ResearchActivationRehearsal` that run the two models** (lines 1347 to 1367 of
  `tools/m6/rollout.psm1`), executed as they stand inside the loaded module, with a scratch run root under the
  checkout's ignored `.cache` that was removed afterwards: both calls exit 0, no problem recorded, the counts
  above, both error logs empty, nothing left under the scratch product root. This is not a run of the phase.

**The same models against the scripts as they were, 06:36:21 to 06:36:35 UTC.** The old files were written out of
git into a scratch directory (`git show <commit>:<path>`); the deploy script and its libraries into a scratch
repository of their own, because that script asks git for its commit.

- **The check as at `105dd2d`:** exit 1, 8 of 11 expectations failed. Its first reading stopped with "Cannot
  convert the JSON string because a dictionary that was converted from the string contains the duplicated keys
  'CLOCK_UNCERTAIN' and 'clock_uncertain'."
- **The deploy script as at `0c81349`,** before its fix in `583a98a`: exit 1, 37 of 45 expectations failed. The
  script said "STOPPED at stage 'preflight'" with the same error, as it did against the normal application on
  2026-10-08 at 20:15 UTC.

**The SELECT on a disposable PostgreSQL, 06:28:40 to 06:28:44 and again 06:29:02 to 06:29:06 UTC.** By a scratch
script that is not in the repository. One container of the product's database image, found locally
(`sha256:b0f9560a…`, nothing pulled), without a network and without a volume, initialized with the image's
defaults, as the product's Compose file initializes its own:

```powershell
docker image inspect --format "{{.Id}}" postgres:17.11-alpine3.24
docker ps -a --filter "name=^asl-pilot-check-sql-20261009$" --format "{{.ID}}"
docker run -d --rm --name asl-pilot-check-sql-20261009 --network none --tmpfs /var/lib/postgresql/data --memory 256m --cpus 1 -e POSTGRES_HOST_AUTH_METHOD=trust postgres:17.11-alpine3.24
docker logs asl-pilot-check-sql-20261009
docker exec asl-pilot-check-sql-20261009 pg_isready -U postgres
docker exec -i asl-pilot-check-sql-20261009 psql -X -q -U postgres -d postgres -v ON_ERROR_STOP=1
docker exec -i -e "PGOPTIONS=<the check's own options>" -e PGCONNECT_TIMEOUT=3 asl-pilot-check-sql-20261009 psql -X -U postgres -d postgres -A -t -v ON_ERROR_STOP=1
docker stop --timeout 5 asl-pilot-check-sql-20261009
```

The first `psql` call read, on standard input, scratch tables that hold only the columns the SELECT reads (they
are not the product's schema) and the rows of the model's first scenario: an `execution_lease` at epoch 5, one
forward checkpoint, five experiment events, 514 execution incidents, and seven market incidents, of which
`clock_uncertain`, `CLOCK_UNCERTAIN` and `QUEUE_OVERLOAD` lie before the given instant and `stream_silent`,
`COLLECTION_GAP`, `CLOCK_UNCERTAIN` and `clock_uncertain` after it. The second call read the SELECT on standard
input, once as the changed check prints it and once as the check at `105dd2d` printed it.

OBSERVED, both runs alike:

- **The server:** `PostgreSQL 17.11 on x86_64-pc-linux-musl`, collation and character type `en_US.utf8`;
  `upper('clock_uncertain')` is `CLOCK_UNCERTAIN`. (The first run's line for this failed on a mistake in the
  scratch query; the second run printed it.)
- **The changed SELECT:** `"market_incidents_since" : { "STREAM_SILENT" : 1, "COLLECTION_GAP" : 1,
  "CLOCK_UNCERTAIN" : 2 }`, and Windows PowerShell 5.1 reads the document. The model gives the same counts for
  the same rows.
- **The SELECT as it was:** `{ "COLLECTION_GAP" : 1, "stream_silent" : 1, "clock_uncertain" : 1,
  "CLOCK_UNCERTAIN" : 1 }`, and Windows PowerShell 5.1 does not read the document: the error quoted above.
- **A write under the check's connection options:** refused, "cannot execute INSERT in a read-only
  transaction".
- **Afterwards:** `docker stop` exit 0 and no container of that name. It was started with `--rm` and had no
  volume and no network, so nothing of it is left.

**Documentation link check, 06:41 UTC, and again at 06:45 UTC on the documents with the delivery recorded,** in
a read-only container without a network, the worktree mounted read-only (the command of the earlier batches):
`checked 91 Markdown files; 0 broken link(s)`, exit 0, both times.

```powershell
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

**Delivery, 06:44 UTC.** One commit with the scripts, the two models and the documents (`a93d718`), pushed
without force to its own branch, and pull request
[MentorAliu/adaptive_spot_lab#33](https://github.com/MentorAliu/adaptive_spot_lab/pull/33) opened against `main`
with `gh pr create`; its description shows the changed SELECT. A documentation-only commit then records this
number. Nothing was pushed to `main` and nothing was merged. Read back at 06:44 UTC: the pull request is open
and mergeable at head `a93d718`, with no check run reported.

```bash
git push -u origin claude/vigilant-grothendieck-4a7403
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head claude/vigilant-grothendieck-4a7403 --title "<title>" --body-file <file>
gh pr view 33 --repo MentorAliu/adaptive_spot_lab --json number,state,createdAt,headRefOid,baseRefName,mergeable,url
```

**Merge requested, 07:00 UTC** ([DECISIONS](../DECISIONS.md#2026-10-09--owner-asks-to-merge-the-pilot-check-pull-request)).
Read-only first, at 07:01 UTC:

```bash
git fetch origin
git rev-parse origin/main HEAD origin/claude/vigilant-grothendieck-4a7403
gh pr view 33 --repo MentorAliu/adaptive_spot_lab --json number,state,mergeable,mergeStateStatus,headRefOid,baseRefName,statusCheckRollup,reviewDecision
gh pr list --repo MentorAliu/adaptive_spot_lab --state open --json number,title,headRefName
```

OBSERVED: `origin/main` is `105dd2d`, as when the change was branched and checked; the local and the remote
branch are both `11b2061`; pull request 33 is `OPEN`, `MERGEABLE` and `CLEAN` at that head, with no check run
and no review decision, and it is the only open pull request. This record is one more documentation-only
commit on that head; the link check was run on it at 07:08 UTC (`checked 91 Markdown files; 0 broken
link(s)`, exit 0). The merge follows this record and is not claimed here. The command to be used, NOT RUN
when this was written: `gh pr merge 33 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <the
head that holds this record>`, an ordinary merge commit, without force, an administrator bypass or branch
deletion.

**Quality gates this change affects** ([ACCEPTANCE_CHECKLIST](../ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone);
a small scoped change records only those):

| Gate | Result |
|---|---|
| Q03 data correctness | VERIFIED: the counts by code of the same rows, in the model and on PostgreSQL 17.11 |
| Q04 security | VERIFIED in the model and on the disposable PostgreSQL: still one SELECT under the forced read-only mode; a write under those options is refused. The scope of the read is unchanged |
| Q05 failures | VERIFIED for the check: a reading with both spellings is taken. NOT RUN: the watch's loop |
| Q07 automated verification | VERIFIED: the parser and the two models, on the host's Windows PowerShell 5.1, which no container runs. NOT RUN: the rehearsal phase that now runs both models |
| Q08 visibility | A reading, and the watch's log, name a lower-case code in upper case; recorded in [OPERATIONS](../OPERATIONS.md) |
| Q09 deployment | NOT APPLICABLE: no product code, image, schema or running service changes; a checkout holds the tools once it holds the merge |
| Q10 maintainability | OPERATIONS, TESTING, DECISIONS and the plan's §19 updated; no dependency added |

No independent review was made: the change was read by the session that wrote it.

**NOT RUN:** `tools\m6-pilot-check.ps1 -Execute` and `tools\m6-pilot-watch.ps1 -Execute`, each of which reads the
normal application and needs the owner's approval in chat; so the changed SELECT has not read the normal
database. Any phase of `tools\m6-acceptance.ps1`, `ResearchActivationRehearsal` among them. The watch's loop
against a stand-in. Any `pytest`: no file under `apps/` or `services/` changed. GitHub CI has no job that runs a
PowerShell script.

## M6 B10: the inert deployment of M6-A to the normal application (2026-10-08)

By the M6 B9 and B10 session, from the primary checkout, on the owner's approval in chat
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b10-the-owner-approves-the-inert-deployment-before-the-merge)). Windows PowerShell 5.1.

**The read-only look, 19:40 to 19:44 UTC:**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-b0-observe.ps1 -RunId m6-b9s -ObserveSeconds 90 -Execute
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-check.ps1 -RunId m6-b9s -Since 2026-10-08T19:00:00Z -Label before -Execute
docker image inspect --format "{{.Id}}" adaptive-spot-lab-migrate
docker image inspect --format "{{.Id}}" adaptive-spot-lab-agent-admin
[IO.File]::WriteAllText((Join-Path (Get-Location) '.cache\deployments\m6-baseline-compose-ec1d78b.yaml'), ((git show 'ec1d78b:compose.yaml') -join "`n") + "`n")
```

OBSERVED. Three samples, no identity difference between them. Nine containers, each started at 19:38:42 or
19:38:43 UTC with restart count 0: the same container IDs and images as at 18:11:56 UTC, when they had been
running since 2026-10-01, 2026-10-02 and 2026-10-07 (the owner restarted Docker; confirmed in chat). Images:
`market-worker` `sha256:31ee07e5…`, `execution-worker` `sha256:5b02dbe1…`, `evaluation-worker` `sha256:6e2d4e6a…`,
`postgres` `sha256:b0f9560a…`, `api` `sha256:54368771…`, `web` `sha256:0801ab1c…`, `agent-worker` `sha256:d715d130…`,
`agent-runner` `sha256:421793d7…`, `agent-egress` `sha256:ce07199d…`; the names `migrate` `sha256:92baa492…` and
`agent-admin` `sha256:81711a46…`. The pilot at 19:42:10 UTC: lease epoch 5 and held (4 at 18:11:56), forward
checkpoint 2250466 and stepping, `EXECUTION_DOWNTIME` 4 as event and as incident (3 at 18:11:56),
`PROTECTION_UNAVAILABLE` 510 (unchanged), no market incident since 19:00 UTC. The baseline file is byte for byte
the blob `e046457` of `ec1d78b:compose.yaml`.

**First attempt, 20:15:00 to 20:15:04 UTC, commit `0c81349`:**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-deploy.ps1 -BaselineComposeFile .cache\deployments\m6-baseline-compose-ec1d78b.yaml -ExpectedPilotImages 'market-worker=sha256:31ee07e5,execution-worker=sha256:5b02dbe1,evaluation-worker=sha256:6e2d4e6a' -ExpectedPreM6Images 'api=sha256:54368771,web=sha256:0801ab1c,agent-worker=sha256:d715d130,migrate=sha256:92baa492,agent-admin=sha256:81711a46'
```

OBSERVED: exit 1. "[1/11] Preflight (read-only), pilot image tags and :pre-m6 rollback tags", then "STOPPED at
stage 'preflight': Cannot convert the JSON string because a dictionary that was converted from the string
contains the duplicated keys 'clock_uncertain' and 'CLOCK_UNCERTAIN'." Nothing was changed: afterwards no
`:pre-m6` tag exists, no `m6-deploy-*` directory, and `adaptive-spot-lab-market-worker:pilot-d779fbf4` still
names its old image `73df98a6…`. The console is kept in `.cache\deployments\m6-deploy-console-20261008T194625Z.log`.

**The fix and its check, 21:49 to 21:51 UTC** ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b10-a-deployment-that-stopped-in-its-read-only-preflight-and-the-fix-of-the-deploy-script)):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository <repository> -Work <a temporary directory>
```

OBSERVED: the changed script parses with 0 errors and holds no byte outside ASCII; the model test, which runs
no Docker command: exit 0, 17 scenarios, 74 expectations, 0 failed.

**The deployment, 22:15:01 to 22:20:13 UTC, commit `583a98a`.** The same line as the first attempt, started at
22:15 UTC by a waiting command that had been armed at 21:52 UTC and ended by itself.

OBSERVED: exit 0, eleven steps, record status `COMPLETE`. The console is kept in
`.cache\deployments\m6-deploy-console-20261008T215248Z.log`; the record and the backup are in
`.cache\deployments\m6-deploy-20261008T221514Z\` (`m6-deploy.json`, `asl.dump`, `asl.dump.sha256`).

| What | Recorded by the script |
|---|---|
| Source | commit `583a98a695bd5cead216cb2e2bbcb3abc24afc7a`, 0 uncommitted product files |
| Starting state | schema `0007_m5_agent_runtime`; lease epoch 5, held; experiment `d779fbf4…` `RUNNING`, version 3; 0 segments; 4 downtime events; 514 execution incidents (`EXECUTION_DOWNTIME` 4, `PROTECTION_UNAVAILABLE` 510); no service down; no research or source container, both flags `0` |
| Rollback tags, created | `:pre-m6` on `api` `54368771…`, `web` `0801ab1c…`, `agent-worker` `d715d130…`, `migrate` `92baa492…`, `agent-admin` `81711a46…` |
| Rendered configuration | the pilot's services, the private network and the database volume render the same from both compose files (`edfbe955…`); `postgres` and the three pilot workers were each created from what the file renders now |
| Backup | `asl.dump`, 479,947,415 bytes, SHA-256 `428265791ac0075373af1e4150edd79f652e13b6ffbd37f40b1719e0e35fe0a7`; the database held 3,017,807,539 bytes |
| Restore rehearsal | the copy migrated to `0008_m6_research`, reconciled `OK`, downgraded to `0007_m5_agent_runtime`; the M1 to M4 tables `75900994…` before, after and after the downgrade; the agent tables `b2fece4e…` before and after the downgrade; no helper container, network or volume left |
| Built | `migrate` `392b5cff…`, `api` `44fd430f…`, `web` `f8425683…`, `agent-worker` `64c0bad5…`, `agent-admin` `e18199d3…`, `source-fetcher` `fd5ea4cf…`, `research-runner` `9455403b…`, `research-migrate` `dac55159…`, `research-bridge` `f9a0fee7…`, `research-admin` `2e23bab7…` |
| Replaced, in this order | `web` (started 22:19:42), `api` (22:19:54), migration 0008 applied in 1 attempt, `agent-worker` (22:20:06) |
| Inert afterwards | no container of `research-postgres`, `research-runner`, `research-bridge` or `source-fetcher`; `ASL_RESEARCH_ENABLED` and `ASL_SOURCES_ENABLED` `0`; `asl_research` and `asl_source` exist without login |
| The pilot afterwards | `postgres`, `market-worker`, `execution-worker`, `evaluation-worker`, `agent-runner` and `agent-egress`: the container IDs, images, start times (19:38:42 or 19:38:43) and restart count 0 of the start; schema `0008_m6_research`; lease epoch 5, held; experiment `RUNNING`, version 3; 0 segments; 4 downtime events; the execution incidents unchanged; the four pilot image names not moved |
| Reported, not judged | market incidents recorded during the run: none; the newest publication 1 s old before and 0 s after |

**Read-only verification, 22:20:52 to 22:24 UTC:**

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-check.ps1 -RunId m6-b9s -Since 2026-10-08T22:15:00Z -Label after -Execute
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-b0-observe.ps1 -RunId m6-b9s -ObserveSeconds 90 -Execute
docker ps -a --format "{{.Names}}|{{.Image}}|{{.Status}}"
```

OBSERVED. At 22:20:54: lease epoch 5, held; forward checkpoint 2278110, last step 22:20:53 (2250466 at 19:42:10);
`EXECUTION_DOWNTIME` 4 as event and as incident, `PROTECTION_UNAVAILABLE` 510; no market incident since
22:15:00. Four samples from 22:20:54 to 22:22:27 without an identity difference. Nine containers, all running;
`api`, `web` and `agent-worker` report healthy.

The pages, in the session's browser at `http://localhost:3000`, without signing in: `/` shows the owner sign-in
form and the navigation with Research and Evidence; `/research`, `/evidence`, `/agents` and `/approvals` show
"Owner session required"; `/system` shows Account `funded`, Market data `ready`, Model runtime
`login_required`, Paper trading `running`, Evaluation reports `reporting`, Paper execution worker `running`,
Research `unapproved`, Evidence sources `unapproved`. No console error.

**Removing what the deployment superseded, 22:26:25 to 22:28:03 UTC**
([DOCKER](../DOCKER.md#cleaning-up-disposable-resources)):

```powershell
docker image rm adaptive-spot-lab-<name>:<tag>
docker image prune -f
docker buildx prune -f
```

The first line once for each of the fifteen rollback tags older than `:pre-m6`, by name and never forced, after
a check that the tag still named the image read at 22:24: of `api` and of `migrate` the tags `pre-0014`,
`pre-0017`, `pre-m3`, `pre-m4` and `pre-m5`; of `web` the tags `pre-approvals-key`, `pre-ended-causes`, `pre-m3`,
`pre-m4` and `pre-m5`.

OBSERVED: each of the fifteen exit 0, "Untagged" and "Deleted". The untagged images: exit 0, 82 before and 0
after, "Total reclaimed space: 1.318GB". The build cache: exit 0, "Total: 2.353GB". By `docker system df`:
images 151 to 54 (9.813 GB to 8.409 GB), build cache 654 to 121 entries (9.644 GB to 7.29 GB); nine containers
and eight volumes before and after, the containers unchanged. A pilot check at 22:28:20: lease epoch 5, held;
checkpoint 2279359; no market incident since 22:15:00. The log is `.cache\deployments\m6-cleanup-20261008T222624Z.log`.

- **Kept, and read again by image ID afterwards:** the five `:pre-m6` tags; the `:latest` name of every
  service; `:pilot-d779fbf4` of the three pilot workers; `pilot-admin`; `market-worker:pre-0024`; the five
  research and source images; the agent runner and the egress gateway; the PostgreSQL image.
- **Not touched:** the older tags of the pilot's services (this deployment deployed none of them), the test and
  tool images, every volume, every network.

**Documentation link check, 22:36 UTC, and delivery.** In a read-only container without a network, the
repository mounted read-only (`tools/check_links.py`, the command of the earlier batches):
`checked 91 Markdown files; 0 broken link(s)`, exit 0. The record is committed to the branch of pull request 32
and pushed without force. The pull request is then merged with an ordinary merge commit pinned to that head,
as the owner decided
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b10-the-owner-approves-the-inert-deployment-before-the-merge)). This
entry is written before the merge and does not claim it.

**NOT RUN:** the owner's signed-in pages (the session does not sign in as the owner); the reason of the
runtime's state on the normal application, which only the signed-in agents page or the database shows; the
rollback, which is rehearsed in isolation only; any activation, approval, model call or public endpoint.

## M6 B9: the acceptance run m6-b9s (2026-10-08)

By the M6 B9 session, from the primary checkout. Windows PowerShell 5.1. Isolated projects
`asl-m6-m6-b9s-<kind>` only; the normal application was read, never changed, by the pilot watch. No model call
and no public endpoint.

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9s -Phases Build,Generate,Checks,Migration,Regression,ResearchRunner,EngineParity,Staging,HoldoutIsolation,SourcePolicy,EvidenceInjection,ShadowSchedule,DispatcherAuth6,ResearchActivationRehearsal,AgentFaults6,MixedVersion,ApiAuth,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,AgentOffline6,SecretScan,Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9s -EndFile <repository>\.cache\m6\m6-b9s-pass.done -MaxHours 8 -Execute
```

The first command is the scratch runner: it calls `tools\m6-acceptance.ps1 -RunId m6-b9s -Phase <phase>
-WaitForWindow` for one phase at a time, the first of its list whose reserved minutes fit the rest of the
test window. The run had been prepared with `-Phase Prepare` earlier that day; its address ranges overlap no
existing test network.

OBSERVED: every phase exit 0, each in one attempt. Build of commit `cedb6d10e7632aba57d7c0c08d6512dc7b40fe18`,
0 uncommitted entries; engine test image `sha256:fa29176c…fea0c`, runtime images engine `sha256:35d6d7c5…dc0d`
and web `sha256:dec7c9ad…9f06`; tree digest at Build and at `Report` `afaba4b5…b449`.

| Phase | Began (UTC) | Ended (UTC) | Attempts | Result |
|---|---|---|---|---|
| `Build` | 15:15:47 | 15:16:21 | 1 | VERIFIED |
| `Generate` | 15:16:26 | 15:16:42 | 1 | VERIFIED |
| `Checks` | 15:16:47 | 15:18:37 | 1 | VERIFIED |
| `Migration` | 15:18:42 | 15:21:12 | 1 | VERIFIED |
| `Regression` | 15:21:16 | 15:36:51 | 1 | VERIFIED |
| `ResearchRunner` | 15:36:56 | 15:40:02 | 1 | VERIFIED |
| `EngineParity` | 15:40:07 | 15:43:39 | 1 | VERIFIED |
| `HoldoutIsolation` | 15:43:44 | 15:44:01 | 1 | VERIFIED |
| `SourcePolicy` | 15:44:06 | 15:45:20 | 1 | VERIFIED |
| `EvidenceInjection` | 15:45:25 | 15:46:25 | 1 | VERIFIED |
| `Staging` | 16:07:01 | 16:09:28 | 1 | VERIFIED |
| `ShadowSchedule` | 16:09:32 | 16:10:39 | 1 | VERIFIED |
| `DispatcherAuth6` | 16:10:43 | 16:12:21 | 1 | VERIFIED |
| `ResearchActivationRehearsal` | 16:12:26 | 16:32:47 | 1 | VERIFIED |
| `MixedVersion` | 16:32:51 | 16:38:23 | 1 | VERIFIED |
| `ApiAuth` | 16:38:28 | 16:40:29 | 1 | VERIFIED |
| `BrowserResearch` | 16:40:34 | 16:43:51 | 1 | VERIFIED |
| `AgentOffline6` | 16:43:56 | 16:47:05 | 1 | VERIFIED |
| `AgentFaults6` | 17:07:10 | 17:26:05 | 1 | VERIFIED |
| `BrowserResearchError` | 17:26:10 | 17:27:02 | 1 | VERIFIED |
| `BrowserRegression` | 17:27:06 | 17:31:25 | 1 | VERIFIED |
| `PerformanceApi` | 17:31:30 | 17:36:17 | 1 | VERIFIED |
| `PerformanceBrowser` | 18:07:22 | 18:09:33 | 1 | VERIFIED |
| `SecretScan` | 18:09:38 | 18:14:05 | 1 | VERIFIED |
| `Report` |  |  | 0 | VERIFIED |

`Report` (18:14:10 to 18:14:16 UTC, exit 0): "Report: scope M6-A, the inert deployment: 24 phases and this
report. Not required here, and the gate of the M6-B activation: PerformanceResearch, ResearchSaturation,
PilotCoexistence. Owed before the activation and not judged here: cutoff-filtered search over 10,000 evidence
items, p95, 211.99 ms (MISSED against at most 150 ms)." and "Report: 26 phase records VERIFIED on run m6-b9s;
24 phase attempts; 11 measurements, none missed."

| Phase | Measurement | Measured | Budget | Verdict |
|---|---|---|---|---|
| `PerformanceApi` | catalog and agent routes, sequential p95 | 38.91 ms | at most 250 ms | WITHIN |
| `PerformanceApi` | the same routes, five readers p95 | 145.08 ms | at most 500 ms | WITHIN |
| `PerformanceApi` | slowest route, sequential p95 (datasets_shadow) | 45.25 ms | at most 250 ms | WITHIN |
| `PerformanceApi` | slowest route, five readers p95 (system_status) | 211.95 ms | at most 500 ms | WITHIN |
| `PerformanceApi` | cutoff-filtered search over 10,000 items p95 | 211.99 ms | at most 150 ms, judged at the M6-B activation gate | NOT JUDGED HERE (MISSED against 150 ms) |
| `PerformanceApi` | searched items with an extract at the registered cap | 10000 items | at least 10000 items | WITHIN |
| `PerformanceBrowser` | slowest page, SSR p95 | 95 ms | below 1500 ms | WITHIN |
| `PerformanceBrowser` | slowest page, LCP | 172 ms | at most 2500 ms | WITHIN |
| `PerformanceBrowser` | worst page, CLS | 0 | at most 0.1 | WITHIN |
| `MixedVersion` | migration 0008 on a live database | 0.53 s | none declared | REPORTED (no budget) |
| `MixedVersion` | API replacement | 7.6 s | none declared | REPORTED (no budget) |

Lines of the phases: "PerformanceBrowser: 32 page measurements; worst SSR p95 95 ms (budget below 1500), LCP
172 ms (budget 2500), CLS 0 (budget 0.1)"; "SecretScan: 161 secrets in 808 forms; 46 databases (1575158 dumped
lines) in 10 clusters; 34 container logs; 14 images; 2929 evidence files (0 archive entries); 635 source files;
0 problem(s)"; `Checks`: "407 passed" and 155 web tests in 18 files; `Regression`: "172 passed, 1 warning in
892.40s".

The watch (log `.cache\m6\m6-b9s-pilot-watch.log`): 29 readings, no stop, lease epoch 4 held, checkpoint
advancing, 0 `PROTECTION_UNAVAILABLE` rows and 0 collection gaps in every thirty minutes, the reports of 15:00
to 18:00 UTC each created in its HH:05 minute. From its reading of 15:31:04 UTC on: "market incidents recorded
and not judged one by one: RETENTION_FAILED +1, RETENTION_RECOVERED +1 since the watch began"; the reading
before, at 15:26:02, has no note. The phase in progress was `Regression`.

**Cleanup, 18:15 to 18:21 UTC**, once each run's evidence was recorded:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <run> -Phase Clean
```

for `m6-b9l` (113 exact-name resources removed), `m6-b9n` (93), `m6-b9p` (9), `m6-b9q` (12), `m6-b9r` (38), `m6-b9s`
(112) and the two prepared, unused runs `m6-b9t` and `m6-b9u` (0 each): each exit 0, "evidence files retained".
OBSERVED afterwards: no container, network, volume or image whose name begins with `asl-m`. No prune, and
nothing of the normal application. A first start at 18:14 UTC did nothing: its own guard waits for HH:15.

**Delivery, 18:22 UTC.** The branch `claude/m6-b9-final-acceptance` was pushed without force and opened as one
pull request against `main`; it is not merged.

```bash
git push origin claude/m6-b9-final-acceptance
gh pr create --base main --head claude/m6-b9-final-acceptance --title "M6 B9: rollout, faults, measurements and the acceptance evidence for M6-A (inert)" --body-file <body file>
gh pr view 32 --json number,state,createdAt,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,additions,deletions,changedFiles
```

OBSERVED: pull request 32 of `MentorAliu/adaptive_spot_lab`, OPEN, created 2026-10-08T18:22:03Z, head
`8713bab0785a81cc55ded49244c1aafc3522e667`, base `main`, MERGEABLE and CLEAN, 104 files, 20,704 additions and
2,073 deletions, no status check configured. The B10 record is added to it after the deployment.

## M6 B9: the new build, its measurements, and the start of acceptance run m6-b9r (2026-10-08)

By the M6 B9 session, from the primary checkout. Windows PowerShell 5.1 and Git Bash. Isolated projects
`asl-m6-<run>-<kind>` only; the normal application was read, never changed, by the pilot watch. No model call.
One public endpoint was reached, by the owner's rule for any UI code: the shadcn registry, by `shadcn info`.

**Without a container beside the running measurements (06:30 to 09:05 UTC).** Lint of the changed engine code
and tests in a throwaway container of an existing test image, no network, the tree piped in:

```bash
cd services/engine && tar cf - app tests pyproject.toml alembic | docker run --rm -i --network none --cpus 1 --entrypoint sh asl-m6-m6-b9l-engine-tests -c 'mkdir -p /tmp/w/services/engine && cd /tmp/w/services/engine && tar xf - && /workspace/services/engine/.venv/bin/ruff check app tests'
```

OBSERVED each time it was run (08:22, 08:48, 09:04, 11:33 UTC): "All checks passed!". At 08:46 UTC, on the
stopped saturation fixture of run `m6-b9l` (an isolated container, started for this and stopped again):

```bash
docker start asl-m6-m6-b9l-saturation-postgres-1
docker exec asl-m6-m6-b9l-saturation-postgres-1 psql -X -U asl -d asl_m1_m5_m6_m6_b9l_saturation -c "SET statement_timeout=0" -c "SET ROLE asl_research" -c "EXPLAIN (ANALYZE, BUFFERS) SELECT p.sequence, to_jsonb(p)::text AS body, p.observation_id, p.confirmation_id, p.available_at FROM research_read.market_publications p WHERE p.sequence > 3000000 ORDER BY p.sequence LIMIT 160"
docker stop --timeout 15 asl-m6-m6-b9l-saturation-postgres-1
```

OBSERVED: 4,148,572 publications; the plan is a parallel index scan of the 1.15 million later rows, a subquery
scan, a top-N sort and the limit; execution 1,612 ms
([INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m6-b9-a-limit-is-not-carried-into-a-security-barrier-view--2026-10-08)).

**The new build, from 09:07 UTC.** Fresh runs were prepared with `tools\m6-acceptance.ps1 -RunId <run> -Phase
Prepare`. Run `m6-b9m` did not get past its Build: Docker refused its engine network ("Pool overlaps with
other one on this address space"), because a run's address ranges follow from its id and `m6-b9k`'s networks
still existed with the same range. From then on a new run's ranges were compared with the existing test
networks before it was used.

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9p -Phase Build -WaitForWindow
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\small-job.ps1 -RunId m6-b9p -PrefixFromRun m6-b9k -Tag new
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\small-job.ps1 -RunId m6-b9p -PrefixFromRun m6-b9k -Tag prof -DatasetId c71ea2a7-c68a-436c-ba9a-9f4247d9e934 -Profile -StartLate
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9n -Phases Build,Generate,Checks,Migration,ResearchRunner,Regression,EngineParity,ApiAuth,Staging,AgentOffline6,ShadowSchedule,HoldoutIsolation,SourcePolicy,EvidenceInjection,DispatcherAuth6,AgentFaults6,ResearchActivationRehearsal,MixedVersion,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9n -EndFile <repository>\.cache\m6\m6-b9n-pass.done -MaxHours 12 -Execute
```

`.cache\m6\small-job.ps1` is scratch tooling: it repeats the measurement phase's own Compose calls (fixture
databases, `tests.m6_performance research load|seal|request|relay|job`, one `app.research.runner --once`) for
one small job, outside the harness's lock, and stops at once when the watch records a difference. Two test
stacks ran side by side from 09:10 UTC: the Docker VM has 16 CPUs and about 5 GB of memory free.

OBSERVED on `m6-b9p` (a build of `b82a379`): load of 10 days 576.6 s; seal of 9.6 days 299.1 s; the screening
job 568.2 s, SUCCEEDED and VALID (320.7 s before its first cell; the DEV cell, 2.76 stepped days, 247.5 s).
The same job under cProfile: 712 s, 174,768 steps in that cell; the table is in
`.cache\m6\m6-b9p-prof-job\runner-job.stdout.log`. A small full test queued for 10:07 UTC did not start: the
script took a Compose path from the wrong run's log. It was not repeated; the acceptance run measures it.

OBSERVED on `m6-b9n` (a build of `b0e1ec1`; UTC): `Build` 09:10, `Generate` 09:11, `Checks` 09:13, `Migration`
09:16, `ResearchRunner` 09:20, `EngineParity` 09:41, `Staging` 09:43, `HoldoutIsolation` 09:44, `SourcePolicy`
09:45, `EvidenceInjection` 09:46, `ApiAuth` 10:09, `AgentOffline6` 10:12, `ShadowSchedule` 10:13,
`DispatcherAuth6` 10:15, `ResearchActivationRehearsal` 10:35, `AgentFaults6` 11:25 (the seven process cases
from 11:07), `MixedVersion` 11:31: each exit 0 and VERIFIED. `Regression` 09:20 to 09:37: exit 1; its login
step VERIFIED and "172 passed, 1 warning in 995.40s", then its guard on the market data code (see commit
`525c580`). The pass was ended by hand at 11:42 UTC while `BrowserResearch` waited for its window: that run's
source-bound phases could no longer run, because `services/` had changed after its Build.

**The pilot watch beside these runs, with a correction made at 13:20 UTC.** The watch of `m6-b9n` (log
`.cache\m6\m6-b9n-pilot-watch.log`, 36 lines, 09:10:30 to 12:13:41 UTC) stopped nothing: at every reading the
lease was held at epoch 4 and the checkpoint had advanced, with no `PROTECTION_UNAVAILABLE` row and no
collection gap. Its notes were not read when this section was first written. OBSERVED in them: the reading of
09:25:41 UTC shows "market incidents recorded and not judged one by one: RETENTION_FAILED +1", and every
reading from 09:30:42 on "RETENTION_FAILED +1, RETENTION_RECOVERED +1 since the watch began". One hourly
retention call of the normal market worker failed between 09:20:39 and 09:25:41 UTC and a later pass
completed by 09:30:42. At those minutes `m6-b9n` ran `Regression` (from 09:20:18) and the scratch measurement
on `m6-b9p` sealed its dataset (09:20:08 to 09:25:07). The watch does not stop on a market incident other
than `QUEUE_OVERLOAD`. No command was run against the normal application to look further.

**Cleanup, 11:33 to 11:40 UTC** (a first attempt at 09:36 was refused: a phase held the harness's lock):

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId <run> -Phase Clean
```

for `m6-b9obs`, `m6-b9a` to `m6-b9k` and `m6-b9m`, one after the other: each exit 0. Test networks 87 to 31,
test containers 173 to 63. Kept: `m6-b9l`, `m6-b9n`, `m6-b9p` (and later `m6-b9q`, `m6-b9r`). No prune.

**The projection without a database, 11:46 UTC** (scratch `exercise_projection.py`, piped into a throwaway
container of `asl-m6-m6-b9q-engine-tests` with no network, as the lint above): "EXERCISE PASSED: no exception,
every figure as expected". On the real screening reading of `m6-b9p` and synthetic full-test and advance
readings: screening at 21 days 2,963 to 3,391 s; full test at 14 days about 3,700 s and at 21 days about
7,400 s; shadow advance about 7,800 and 11,500 s.

**Fresh API samples and the web test, 11:44 to 12:12 UTC:**

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9q -Phases Build,Generate,BrowserResearch
docker run --rm asl-m6-m6-b9q-web-tools sh -c "cd apps/web && pnpm exec shadcn info --json"
docker run --rm --network none --mount "type=bind,source=<repository>\apps\web\src\research,target=/workspace/apps/web/src/research,readonly" asl-m6-m6-b9q-web-tools sh -c "cd apps/web && pnpm exec prettier --check src/research/pages.test.tsx && pnpm exec eslint src/research/pages.test.tsx && pnpm exec tsc --noEmit && pnpm exec vitest run src/research/samples.test.ts src/research/pages.test.tsx"
```

OBSERVED: `Build` and `Generate` exit 0; `BrowserResearch` exit 1 as expected, its fresh-sample check with 60
of 61 tests passed and the one known assertion failed; 41 sample files in `.cache\m6\m6-b9q\browser\out\samples`,
copied whole into `apps/web/src/research/samples`. `shadcn info`: exit 0, TanStack Start, style base-nova,
base `base`, lucide, Tailwind v4, preset `b2fms61Bqi`, 18 components. The last command, after the assertion
was changed: exit 0, "Tests 61 passed (61)".

**A trial of the fixed `SecretScan`, 12:09 to 12:12 UTC:**

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9n -Phase SecretScan -WaitForWindow
```

OBSERVED: exit 1 with two problems, both images that run never built (`asl-m6-m6-b9n-browser-api`,
`-browser-web`). Eight clusters, 34 databases searched, the search of each cluster's roles and settings
complete, no value found. On run `m6-b9j` the same phase had failed on those searches.

**Acceptance run `m6-b9r`, started 12:13:44 UTC** (Build of commit `2453f68`, clean tree):

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9r -Phases Build,Generate,Checks,Migration,PerformanceResearch,ResearchSaturation,Regression,ResearchRunner,EngineParity,Staging,HoldoutIsolation,SourcePolicy,EvidenceInjection,ShadowSchedule,DispatcherAuth6,AgentOffline6,ApiAuth,MixedVersion,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,ResearchActivationRehearsal,AgentFaults6,PilotCoexistence,SecretScan,Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9r -EndFile <repository>\.cache\m6\m6-b9r-pass.done -MaxHours 30 -Execute
```

The list is a priority order, not the order of running: the runner starts the first phase whose reservation
fits the rest of the window. Its results are recorded in a section of their own when it ends.

**Beside the acceptance run, 13:05 to 13:12 UTC: a rehearsal that was not run.** `PerformanceBrowser` has no
passing record in any run, and `BrowserResearch`, `PerformanceApi` and it come late in this run. To learn of
a defect hours earlier, a second checkout was made and a run prepared in it:

```powershell
git worktree add --detach .claude\worktrees\m6-b9-rehearsal HEAD
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\rehearsal-chain.ps1 -RunId m6-b9w -Phases Prepare
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\rehearsal-chain.ps1 -RunId m6-b9w -Phases Build,Generate,BrowserResearch,PerformanceApi,PerformanceBrowser
git worktree remove --force .claude\worktrees\m6-b9-rehearsal
```

OBSERVED: `Prepare` exit 0, "prepared 10 isolated targets with fresh fixture secrets; no Docker call"; none of
that run's 42 address ranges overlaps one of `m6-b9r`'s 42 or one of the 37 existing test networks. The third
command was REFUSED by the coding client's safety check before it started, as interference with running
workloads. It was not attempted in another form. No container, network, volume or image of `m6-b9w` exists; the
checkout was removed. NOT RUN, therefore: any rehearsal of the phases that have not passed before; they run
for the first time in the acceptance run itself. Also not run: a timing of the first collection read on the
old saturation fixture ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)), which
would have started a container beside the measurement.

**The watch beside the acceptance run, 13:29 UTC.** OBSERVED in `.cache\m6\m6-b9r-pilot-watch.log`: the reading of
13:24:24 UTC has no note; the reading of 13:29:25 UTC says "market incidents recorded and not judged one by
one: RETENTION_FAILED +1, RETENTION_RECOVERED +1 since the watch began". The phase in progress was the first
part of `PerformanceResearch`, the 27-day load (`perf-load-27d`, 13:07:17 to 13:36:50 UTC, "load_seconds"
1759.5, exit 0). No command was run against the normal application. The owner was asked in the question
dialog and answered at about 13:47 UTC: "Report only (Recommended)"
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-a-failed-retention-call-that-recovers-is-reported-and-does-not-stop-a-test-run)).

**The owner's scope decision at 14:03 UTC, and what was run after it**
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)). The
pass of run `m6-b9r` was ended at 14:04:30 UTC by stopping its background task, while `PerformanceResearch`
waited for its second window. OBSERVED before and after: no container of the run was running, and no process
of the pass or of its phase was left. Then, on that run, now an authoring run:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9r -Phases BrowserResearch,BrowserResearchError,PerformanceApi,PerformanceBrowser,BrowserRegression
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9r -EndFile <repository>\.cache\m6\m6-b9r-pass.done -MaxHours 2 -Execute
```

OBSERVED. A first start at 14:04:53 ended at 14:07:34 with exit 1 before any container started: "The harness
file tools/m6/report.psm1 changed after this process loaded it; start the phase again" (the module was being
edited while the phase waited for its window). The second start, with the watch beside it:

| Phase | Began | Ended | Result |
|---|---|---|---|
| `BrowserResearch` | 14:08:27 | 14:11:52 | exit 0, VERIFIED |
| `BrowserResearchError` | 14:11:53 | 14:12:48 | exit 0, VERIFIED |
| `PerformanceApi` | 14:12:48 | 14:17:40 | exit 1: "34 routes; sequential p95 39.12 ms (budget 250); five readers p95 168.14 ms (budget 500); search p95 213.36 ms (budget 150) on 10004 items with extracts of 42 to 16384 bytes" |
| `BrowserRegression` | 14:17:40 | 14:22:07 | exit 0, VERIFIED |
| `PerformanceBrowser` | not started | | it needs a passing `PerformanceApi` |

The watch: lease epoch 4 held, checkpoint advancing, no `PROTECTION_UNAVAILABLE` row, no collection gap, no
market incident noted. The owner's decision on the search budget followed at about 14:31 UTC
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)).

**The two harness changes, checked without a run, 14:05 to 14:40 UTC.** Both modules were parsed with
PowerShell's own parser (0 errors, no byte outside ASCII). The changed report was run by a scratch script
(`report-dry.ps1`) against copies of the records of `m6-b9r` under `.cache\m6\dry-*`, removed afterwards; its
only Docker calls are the report's own three image inspections. OBSERVED: it completes and refuses that run,
among its reasons "PerformanceResearch was started on this run: an M6-A acceptance run does not start the
phases of the activation gate"; with the trial's API record taken as passed, the search row reads "213.36 ms,
at most 150 ms, judged at the M6-B activation gate, NOT JUDGED HERE (MISSED against 150 ms)" and is no
problem. An independent read-only reviewer (a subagent, no Docker, no edit) read the first form of the
report change and ran extracted lines of it in a separate process: nothing that throws or misjudges a run
of the scoped list.

**`PerformanceApi` and `PerformanceBrowser` on run `m6-b9r`, 14:41 to 15:14 UTC** (after commit `460343b`):

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9r -Phases PerformanceApi,PerformanceBrowser
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9r -EndFile <repository>\.cache\m6\m6-b9r-pass.done -MaxHours 2 -Execute
docker run --rm --network none --cpus 2 --memory 2g --mount "type=bind,source=<repository>\apps\web\e2e,target=/workspace/apps/web/e2e,readonly" asl-m6-m6-b9r-web-tools sh -c "cd apps/web && pnpm exec prettier --check e2e/m6-performance.spec.ts; pnpm exec eslint e2e/m6-performance.spec.ts; pnpm exec tsc --noEmit"
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\perf-browser-replay.ps1
```

OBSERVED. `PerformanceApi` 14:41:48 to 14:46:38, exit 0: "34 routes; sequential p95 38.78 ms (budget 250);
five readers p95 182.26 ms (budget 500); search p95 234.55 ms on 10004 items with extracts of 42 to 16384
bytes (MISSED against its budget of 150 ms, which is judged at the M6-B activation gate)".
`PerformanceBrowser` began its work at 15:07, exit 1 at 15:08:43: "15 page measurements; worst SSR p95 84 ms
(budget below 1500), LCP 192 ms (budget 2500), CLS 0 (budget 0.1)" and "The browser measured 15 of 32 page
views"; the test's own error: no level-one heading on the sixteenth page, `/system`. The third command, on
the corrected test: prettier, eslint and tsc each exit 0. The fourth is scratch tooling: it repeats the
phase's three Compose calls from the run's command log (database; API and web; the browser test with its
four row identities) with the corrected file mounted read-only over the image's copy, and stops the stack.
15:11:43 to 15:13:44: "1 passed (1.8m)"; 32 page views, 16 at 390 px and 16 at 1440 px; worst SSR p95
101 ms, worst LCP 196 ms, worst CLS 0. The watch beside the trial (14:41 to 15:08 UTC): no stop and no note; the two minutes of the fourth command ran after it had ended.

## M6 B9 run m6-b9l, first record (2026-10-07 21:24 UTC onward; in progress)

By the M6 B9 session, from the primary checkout at commit `32de348` (clean at its Build). Windows PowerShell
5.1. Isolated projects `asl-m6-m6-b9l-<kind>` only, and one trial on the old run `m6-b9j`. The normal
application was read, never changed, by the watch.

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9l -Phase Prepare
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9l -OnlyWhatFits -Phases Build,Generate,Checks,Migration,ApiAuth,Staging,HoldoutIsolation,SourcePolicy,EvidenceInjection,ShadowSchedule,ResearchRunner,DispatcherAuth6,EngineParity
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9l -EndFile <repository>\.cache\m6\m6-b9l-pass.done -MaxHours 2 -Execute
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9j -Phase SecretScan -WaitForWindow
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9j -EndFile <repository>\.cache\m6\m6-b9j-secretscan.done -MaxHours 2 -Execute
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9l -Phases AgentFaults6,PerformanceResearch,ResearchSaturation,ResearchActivationRehearsal,MixedVersion,PilotCoexistence,Regression,AgentOffline6,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,SecretScan,Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9l -EndFile <repository>\.cache\m6\m6-b9l-pass.done -MaxHours 36 -Execute
```

The last four ran as one unattended sequence from 21:48 UTC (the session had reached its usage limit): the
trial with its watch, then the rest of the pass with its watch, each watch as a hidden process that ends with
its step. The scratch pass runner gained `-OnlyWhatFits` (end when nothing more fits the window) and holds
`PilotCoexistence` back until the three never-run phases have run.

OBSERVED (UTC): thirteen phases from `Build` 21:24:57 to `EngineParity` 21:45:29, each exit 0 and VERIFIED.
The `SecretScan` trial on `m6-b9j`: 22:07 to 22:10:40, exit 1, `SecretScan-failed-20261007T221035323Z.json`
(nine clusters' "roles and settings" not searched whole; two images that run never built).
`ResearchActivationRehearsal` 22:11:06 to 22:31:29 and `MixedVersion` to 22:37:07: exit 0, VERIFIED.
`AgentFaults6` 22:37:07 to 23:12:40: exit 1, `AgentFaults6-process-failed-20261007T231232231Z.json`.
`Regression` 23:12:41 to 23:29:16: exit 1, `Regression-failed-20261007T232859556Z.json` (46 failed, 115
passed, 8 errors in 964.76 s). `PerformanceResearch` started 23:29:16 and took its first window at 00:07;
its parts so far and the causes of the three failures are in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence). No Docker command was
issued by hand while it measured; the causes were found by reading the code and the run's logs.

## Verified ExecPlan 0024 normal deployment — 2026-10-07

Run with the owner's approval in chat ([DECISIONS](../DECISIONS.md#2026-10-07--market-worker-deployment-approved-then-the-merge-execplan-0024)), 21:04–21:23 UTC, from the worktree at pull-request head `65ba9a2` (source equal to the tested `9c7c87d`, clean tree) through Git Bash and Windows PowerShell 5.1. `<primary>` is the primary checkout, which is on the ExecPlan 0023 branch; its `.env` and secrets were passed to Compose and never read. The full record is in [ExecPlan 0024 §13.1](plans/0024-retention-failure-keeps-the-worker.md#131-executed-2026-10-07-21202122-utc-owner-approved).

```bash
# Read-only state (before and after) and pre-checks that change nothing
docker ps -a --filter label=com.docker.compose.project=adaptive-spot-lab
docker inspect --format <id, image, start time, restart count, status> <each container>
docker inspect --format <three compose labels, restart policy> adaptive-spot-lab-market-worker-1
docker image ls --filter reference=adaptive-spot-lab-market-worker
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on -c statement_timeout=15000" \
  adaptive-spot-lab-postgres-1 psql -U asl -d asl -At -v ON_ERROR_STOP=1 -f -      # SELECTs inside BEGIN TRANSACTION READ ONLY
docker exec adaptive-spot-lab-market-worker-1 sh -c 'cd /app/app && sha256sum <three files>; find . -type f | sort | xargs sha256sum | sha256sum'
git diff 0eb208a HEAD -- compose.yaml services/engine/Dockerfile services/engine/uv.lock services/engine/app   # what the new image changes
diff <primary>/compose.yaml compose.yaml
docker compose -f compose.yaml -p adaptive-spot-lab --profile market config --services
docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market config --services
docker compose --dry-run -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market \
  up -d --no-deps --force-recreate market-worker

# Protected backup (owner-only directory first: icacls <dir> /inheritance:r /grant:r <account>:(OI)(CI)F, as Protect-Path does)
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/retention-failure.dump
docker exec adaptive-spot-lab-postgres-1 sha256sum /tmp/retention-failure.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/retention-failure.dump <primary>/.cache/deployments/retention-failure-20261007T212001Z/asl.dump
docker exec adaptive-spot-lab-postgres-1 sh -c 'unlink /tmp/retention-failure.dump'

# Rollback tag, build one image, confirm the tested source, keep the old log, recreate one service
docker tag sha256:0d4d29bb4765ab288e893ce506c29c79ea5ff627b17bd79300a020bf110e6df3 adaptive-spot-lab-market-worker:pre-0024
docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker
docker run --rm --network none --entrypoint sh adaptive-spot-lab-market-worker:latest \
  -c "cd /app/app && find . -type f | sort | xargs sha256sum"            # compared file by file with the run's snapshot
docker run --rm --network none --entrypoint sh adaptive-spot-lab-market-worker:latest \
  -c "cd /app && python -c '<import the worker, print its retention constants>'"
docker logs --timestamps --since 2026-10-07T19:55:00Z adaptive-spot-lab-market-worker-1
docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market \
  up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker

# After the swap and for the soak (read-only)
docker logs --timestamps [--since <time>] adaptive-spot-lab-market-worker-1
docker exec adaptive-spot-lab-market-worker-1 sh -c 'cd /app/app && <the same hashes>; echo <four non-secret settings>'
```

All exited 0, with one exception that changed nothing: the first import check ran `python` from `/app/app`, where the package cannot be imported (`ModuleNotFoundError`). It was repeated from `/app`, the image's working directory, and passed.

Results:
- **Pre-checks.** Both compose files parse. The dry run named only `adaptive-spot-lab-market-worker-1`, and the container was the same afterwards. The worker's eight imported files differ from the running source in `worker.py` and `store.py` (this plan) and in two additive lines of `db.py` (M6); the service definition is unchanged.
- **Backup.** 444,703,335 bytes, SHA-256 `7a1e8f9c891ccf33803e31c3474eebc63f654e9fc128dc29d55351e9b4ec17b6`, equal inside the container and on the host; `pg_dump` took 57 s (21:20:01–21:20:58).
- **Images.** Market worker `sha256:31ee07e57436…`, whose `/app/app` tree (145 files, listing hash `20d67ad2…c06d`) equals, file by file, the source hashes the acceptance run recorded at `9c7c87d`. Rollback tag `:pre-0024` = `sha256:0d4d29bb4765…`.
- **Containers.** Market worker `117df6d29bda` → `82c8f5475b24`, started 21:22:06 UTC, restart count 0. Every other container of the project kept its container, image and start time.
- **Result.** Lease epoch 2193 at 21:22:07.8; start-up retention removed 6,013 records; stream connected at 21:22:21.1; no observation published for 19 s (21:22:03.04–21:22:22.03); publication lag 122 ms and both feeds `CONNECTED` at 21:23:04; the pilot unchanged; no incident.
- **Soak.** Two bounded background reads (`.cache/m2/ret-soak-read.sh`, not in Git) waited until 22:26 and 23:27 UTC, then read the worker's container state, its log since the previous read and the same read-only SQL, and ended. Both exited 0. Both hourly passes completed without a failed call (19,430 records at 22:22:34, 15,901 at 23:22:47); container `82c8f5475b24`, restart count 0, one collection, no market incident, the pilot unchanged.
- **Merge, as approved.** After this record is committed and pushed: `gh pr view 31 --repo MentorAliu/adaptive_spot_lab --json state,headRefOid,mergeable,mergeStateStatus` and `gh pr merge 31 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <head>`. An ordinary merge commit; no force, no admin bypass, no branch deletion, no auto-merge. This is written before the merge and does not claim it.
- **Evidence files.** In this worktree's ignored `.cache/deployments/retention-0024/`: the state before and after, the build and recreate output, the image's file listing, and the old worker's log since 19:55 UTC (831 lines).
- **A gap in the "before" file.** The first container listing was stored cut at 200 characters, so it holds the restart count of `api`, `postgres` and `web` (0) but not of the five containers with longer names. Their container id, image and start time are in it and are unchanged afterwards, and their restart count afterwards is 0.
- **Not done.** No older rollback tag, untagged image or build cache was removed. The 1 Hz continuity probe of the earlier soaks was not run.

## ExecPlan 0024 commands — 2026-10-07

Results and limits are in [ExecPlan 0024](plans/0024-retention-failure-keeps-the-worker.md#12-verification-isolated). Everything ran from the worktree of branch `claude/market-retention-timeout` through Windows PowerShell 5.1 and Git Bash, against the isolated Compose projects `asl-m2-ret-1007a-*`, `asl-m2-ret-1007d-*` and `asl-m2-ret-1007b-*` only. Synthetic data; no public endpoint was contacted. In the work this section records, no command built, recreated, restarted, stopped or queried the normal `adaptive-spot-lab` project, and `.env`, `secrets/` and `codex_home` were not read. The deployment that followed is the section above.

**One listing that named the normal app's containers.** At 14:05 UTC one `docker stats --no-stream` without a filter printed the resource figures of every running container, the normal app's among them. It read those figures and changed nothing. The other listings of containers were filtered: by Docker's name filter (`--filter name=asl-m2-ret-1007`), or, for a few `docker ps` calls, by dropping every name that starts with `adaptive-spot-lab-` from the output before it was shown.

**Isolated acceptance, run `ret-1007b`,** at commit `9c7c87d3eb2726ec0165ac2203d76de72fc2db2e`, fresh databases, 19:46–20:50 UTC:

```powershell
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase Prepare
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase PerformanceDensity -DensityLevels 1800000 -DensitySeconds 600 -RetentionFaults
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase PerformanceBurst
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId ret-1007b -Phase Stop
```

Between them, with the run's own isolation variables, through a scratch wrapper around the harness's own Compose call (`.cache/m2/ret-compose.ps1`, not in Git):

```powershell
docker compose -p asl-m2-ret-1007b-engine --profile test run --rm --no-deps engine-tests uv run --frozen ruff check .
docker compose -p asl-m2-ret-1007b-engine --profile test run --rm --no-deps engine-tests uv run --frozen python -m app.export_openapi --check
# The M0-M2 test files that WorkerFaults does not run
docker compose -p asl-m2-ret-1007b-engine --profile test run --rm engine-tests uv run --frozen python -m pytest -q --no-header -p no:cacheprovider tests/test_api.py tests/test_database.py tests/test_m1_account.py tests/test_m1_unit.py tests/test_m2_unit.py tests/test_m2_integration.py
# The M3 and M4 test files
docker compose -p asl-m2-ret-1007b-engine --profile test run --rm engine-tests uv run --frozen python -m pytest -q --no-header -p no:cacheprovider tests/test_m3_api.py tests/test_m3_engine.py tests/test_m3_indicators.py tests/test_m3_market_view.py tests/test_m3_properties.py tests/test_m3_replay.py tests/test_m3_roles.py tests/test_m3_throughput.py tests/test_m3_unit.py tests/test_m4_api.py tests/test_m4_engine.py tests/test_m4_evaluation.py tests/test_m4_properties.py tests/test_m4_replay.py tests/test_m4_reports.py tests/test_m4_schema.py
```

All exited 0.
- **Snapshot.** Both snapshots (19:46 and 20:49) record commit `9c7c87d3eb2726ec0165ac2203d76de72fc2db2e` and the same 540 source hashes.
- **WorkerFaults** (19:46–19:50). 75 passed in 181.72 s, none skipped: 69 before this plan, plus the 6 cases of `tests/test_m2_retention_faults.py`.
- **Ruff.** `All checks passed!` **OpenAPI check.** `FastAPI OpenAPI schema matches`.
- **M0–M2 files.** 76 passed in 21.26 s, with the one pre-existing Starlette test-client deprecation warning. 48 of them are `tests/test_m2_unit.py`, 13 of those new.
- **RecoveryMemory** (19:50–19:51). 30 measured recoveries, 444 KiB settled RSS growth, 0 retained market tasks.
- **PerformanceDensity with retention faults** (20:07–20:25). No budget failure. 1,780 of 1,780 frames published; receipt to publication p50 114.1 ms, p95 118.9 ms, p99 122.9 ms, maximum 143.3 ms; 593 of 593 samples usable; one collection and no gap. The database ended the first call of two attempts (`57014` in the observation delete, line 24; waits 60 s and 120 s). The third attempt completed the pass with 30 calls that removed 14,746 observations and 14,746 payloads, and `RETENTION_RECOVERED` closed the failures 3 min 56 s after the first. No other incident. A retention call on its own thread took 329 ms at the median and 646 ms at most (32 calls). The load took 485.4 s, the measurement 601.6 s.
- **M3 and M4 files** (20:25–20:44). 169 passed in 1,094.28 s, with the same one warning.
- **PerformanceBurst** (20:44–20:49). 30,000 of 30,000 frames published; receipt to publication p50 139.9 ms, p95 164.4 ms, p99 173.4 ms; schedule lag p99 2.0 ms; maximum RSS 73,264 KiB.
- **Order and timing.** `Prepare`, `Snapshot`, `WorkerFaults`, Ruff, the OpenAPI check, the M0–M2 files and `RecoveryMemory` ran from 19:46 to 19:51; `PerformanceDensity`, the M3 and M4 files, `PerformanceBurst` and `Snapshot` from 20:07 to 20:49; `Stop` at 20:49. Nothing of this task ran from 19:51:32 to 20:07:08 except two `docker compose stop postgres` of idle test databases of the earlier runs at 19:56 and one filtered listing. The last four steps ran as one scratch sequence (`.cache/m2/ret-final-sequence.ps1`, not in Git) that started at 20:07 UTC and ended by itself. Before each load step it read the newest phase marker of the M6 session's run on the same host and would not have started beside one of that run's measurement phases, or when the step could not end before HH:58 UTC. No heavy step ran between HH:58 and HH:07 UTC.

**Not run in this acceptance.**
- The harness's `Build`, and of `Checks` the web lint, typecheck, unit tests, API-contract check, format check and production build. No file under `apps/` and no API schema changed.
- The harness's `Regression` phase as one call. It runs every test file. The files of M0 to M4 ran by name, above and in `WorkerFaults`. `tests/test_m5_*.py` and `tests/test_m6_*.py` did not run: none of them imports `app.market_data.worker`, `app.market_data.store` or the density module.
- `PerformanceRetention`, `PerformanceFullRetention`, `PinnedExhaustion`, `PerformanceApi`, the recovery, browser and public-endpoint phases, and density levels other than 1.8 million.

**Development run `ret-1007a`,** the same worktree before the commit, 14:07–19:43 UTC: `Prepare`; then the same wrapper for `docker compose -p asl-m2-ret-1007a-engine` and `-density` with `--profile test build migrate engine-tests`, `up -d postgres`, `run --rm migrate`, `run --rm engine-tests uv run --frozen python -m pytest …`, `stop postgres` and `restart postgres`; `PerformanceDensity -DensityLevels 1800000 -DensitySeconds 30 -Observe` to load the density database; `WorkerFaults` twice.
- **Reproduction on the unchanged code.** `worker.py` and `store.py` of `0f395a9` and a copy of the new test file with the new constants written as numbers were mounted read-only over the built image (`-v <scratch>/unchanged/<file>:/workspace/services/engine/…:ro`), with `-k "database_ends or start_up or rotation_waits"`. In its last form, at 19:26 UTC: `4 failed, 2 deselected`. On the changed code at 19:27 UTC the new file and the unit file: `54 passed`.
- **Cost measurement** (14:10–14:39 UTC) on the density database of that run, 1.8 million synthetic observations loaded in 801.5 s: `docker compose -p asl-m2-ret-1007a-density exec -T postgres psql -U asl -d <that run's database> -X -f /tmp/<probe>.sql` after `docker compose … cp <probe>.sql postgres:/tmp/`, as the database owner of that disposable database. The probes read the catalog (references, indexes, `pg_settings`, `rolconfig`); took that database's market lease and called the retention function under `auto_explain` with nested statements and triggers, most calls rolled back and four committed as a pass commits them; ran the function's two selections under `EXPLAIN (ANALYZE, BUFFERS)`; and inserted synthetic `strategy_evaluations` rows, with triggers and reference checks off for the insert only, and removed them with `TRUNCATE`. Between probes `docker compose … restart postgres` ran twice, for empty buffers. The outputs are the `probe-*.log` files of that run.
- **A first density run with retention faults** (14:27–14:37 UTC, `python -m app.market_data.performance_density --existing --seconds 600 --retention-faults`, on the first form of the change) exited 0.
- **Two older tests.** The two `WorkerFaults` passes of this run ended `1 failed, 73 passed` and `1 failed, 74 passed`, each on one test of ExecPlan 0022. `tests/test_m2_reference_checks.py::test_imprecise_routine_clock_check_keeps_the_collection_and_fails_closed` then ran six times each on the unchanged and the changed worker (1 and 2 failures) and eight times corrected (0 failures). `…::test_nothing_re_opens_a_feed_while_the_clock_is_unverified` ran eight times each (3 and 3 failures).
- **Trial regression on an earlier form of the source** (19:07–19:25 UTC): the M0–M2 files 73 passed and the M3 and M4 files 169 passed. `worker.py` and the unit tests changed after these started, so they are not evidence for the commit.
- **My own load was paused once,** from 14:14:16 to 14:19:30 UTC (`docker pause` and `docker unpause` of this run's two density containers), around the minute in which the normal worker's hourly retention was expected. That minute was estimated from the log extract of 2026-10-06 and was not read from the normal app. The estimate was wrong: by the extract of the third exit the pass ran within a minute or two of the full hour that day ([the plan's §2.5](plans/0024-retention-failure-keeps-the-worker.md#25-a-third-exit-while-this-plan-was-being-verified-observed-by-the-session-of-execplan-0023)).

**Diagnosis run `ret-1007d`,** a fresh database at the same source, 19:38–19:43 UTC: `Prepare`, the same build, database and migration calls, the second older test twelve times (`1 passed` each), `WorkerFaults` (`75 passed in 182.89s`) and Ruff (`All checks passed!`).

**Other commands.**
- Relative documentation links and heading anchors, on the finished documents: `docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo` → `checked 91 Markdown files; 0 broken link(s)`.
- Read-only Git commands (`git fetch origin`, `git status`, `git diff`, `git log`, `git show origin/main:<file>`). One local work-in-progress commit was replaced by the code commit with `git reset --soft origin/main`, and that commit's message was corrected once with `git commit --amend` before the acceptance run; nothing had been pushed.
- Delivery: `git add` of the documents, `git commit`, `git push -u origin claude/market-retention-timeout` and `gh pr create --base main`, without force. That text was written before the push. The push and `gh pr create` ran at 20:52 UTC: commits `9c7c87d` and `5cae96e` are pull request [MentorAliu/adaptive_spot_lab#31](https://github.com/MentorAliu/adaptive_spot_lab/pull/31), open, mergeable and clean at head `5cae96e`, with no check run (`gh pr view 31 --json …`). A further documentation-only commit records this number and is pushed to the same branch. At that point the pull request was not merged and nothing was deployed.

**Cleanup of this task's Docker resources,** by the standing rule in [DOCKER](../DOCKER.md#cleaning-up-disposable-resources), after the evidence above was written. A scratch script (`.cache/m2/ret-clean.ps1`, not in Git) listed one run's resources with a name filter and then called `docker rm`, `docker network rm`, `docker volume rm` and `docker image rm` once per exact name, never forced. It refuses a name that does not start with `asl-m2-<run>-`, a running container, and a minute outside HH:15–HH:55 UTC.

- **`ret-1007a`** (20:26:29 UTC): 4 stopped containers, 2 networks, 2 volumes (one held the 1.8 million synthetic rows) and 4 images.
- **`ret-1007d`** (20:26:33 UTC): 2 containers, 1 network, 1 volume and 2 images.
- **`ret-1007b`** (20:49:47–20:50:03 UTC): its containers and networks by the harness's `Stop` (`docker compose down --remove-orphans` for each project of the run's manifest), then 3 volumes (one with 1.8 million synthetic rows) and 6 images.
- **Result.** Every call exited 0 and none was refused. Afterwards the filtered listings show no container, network, volume or image whose name starts with `asl-m2-ret-1007`.
- **Kept.** The evidence files of the three runs under the worktree's ignored `.cache/m2/`. The build cache and untagged images were left as they were. No prune ran, and no command named the normal project.

## M6 B9 authoring run m6-b9k, its stop by the pilot watch, and the market worker's log (2026-10-07)

By the M6 B9 session, from the primary checkout (Build at commit `a44ccb0`; tools and documents edited
afterwards, so this is an authoring run). Windows PowerShell 5.1. Isolated projects `asl-m6-m6-b9k-<kind>`
only. The normal application was read, never changed: by the watch's two read-only scripts, and by one
`docker logs` call that the owner allowed at about 20:17 UTC
([DECISIONS](../DECISIONS.md#2026-10-07--m6-b9-a-restart-of-the-market-worker-alone-beside-a-test-run-and-its-log)).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9k -Phase Prepare
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9k -Phases Build,Generate,Checks,AgentFaults6,Regression,AgentOffline6,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,ResearchSaturation,PerformanceResearch,SecretScan,Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9k -EndFile <repository>\.cache\m6\m6-b9k-pass.done -MaxHours 36 -Execute
```

OBSERVED (UTC): `Build` 19:11, `Generate` 19:12, `Checks` 19:14, `Regression` 19:14 to 19:31: each exit 0 and
a VERIFIED record. `AgentFaults6` started 19:31; its in-process part ended 19:32; its process part began at
20:07:00 and was cut at 20:11:47 by the watch's stop (exit 1,
`AgentFaults6-process-failed-20261007T201306277Z.json`). The watch at 20:11:45: "a normal container changed
its identity, start time or restart count": the market worker, started 2026-10-07T20:01:27.77Z with restart
count 3, was 2026-10-06T15:53:57.83Z with 2. It ran `tools\m6-acceptance.ps1 -RunId m6-b9k -Phase Stop` (exit
0); the pass runner ended with exit 3 and nothing pending was started.

What was read afterwards, between 20:12 and 20:19 UTC:

```powershell
docker ps -a --filter "name=asl-m" --format "{{.Names}}|{{.Status}}|{{.CreatedAt}}"
docker logs --since 2026-10-07T19:55:00Z --until 2026-10-07T20:05:00Z adaptive-spot-lab-market-worker-1
```

The first lists isolated test containers only (this session's and the other session's). The second is the one
read of the normal market worker for this restart, at 20:18:39 UTC, exit 0, 212 lines on stderr, kept as
`.cache\m6\market-worker-log-20261007T1955-2005.stderr.txt` (ignored by git). OBSERVED in it: the retention
delete of `asl_prune_market_evidence` canceled by its statement timeout at 20:01:23 UTC, then
`market_worker_fatal`, then a new collection ([ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence)).
The run's own command log was read for what it had in progress at 20:01:27 UTC: nothing between 19:32:51 and
20:07:00.

After the owner's answers the stop record was moved to
`.cache\m6\PILOT-DIFFERENCE-20261007T201145Z-m6-b9k.txt` and the run was started again at 20:20:56 UTC:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9k -Phases AgentOffline6,AgentFaults6,PerformanceResearch,ResearchSaturation,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,SecretScan,Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9k -EndFile <repository>\.cache\m6\m6-b9k-pass.done -MaxHours 36 -Execute
```

The watch with the rule of the morning ran from 20:21 to 20:27 UTC (one reading, no stop) and was then ended
and replaced by the watch with the rule of the evening. `AgentOffline6`: 20:20 to 20:24, exit 0, VERIFIED. The
rest is recorded here when the pass ends.

Checks of the new rule, without a stack (scratch scripts that load the functions out of the repository's
files; the second calls `docker logs` on an isolated fixture container of this run, never the normal one):

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\run-pilot-rules-from-harness.ps1
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\try-watch-logread.ps1 -Container <id of asl-m6-m6-b9k-research-fixture-postgres-1> -From 2026-10-07T20:07:00Z -To 2026-10-07T20:13:00Z
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9k
```

OBSERVED: "cases: 54; not holding: 0". The log read returned 75 lines of both streams; the cause for that
text is "UNKNOWN: the log holds 0 market_worker_fatal events", for the real extract of 2026-10-07
`RETENTION_STATEMENT_TIMEOUT`, and for the extract of 2026-10-06 that spans two restarts "UNKNOWN: the log
holds 2 market_worker_fatal events". The third prints the watch's scope and runs nothing. NOT RUN: the rule on
a real restart of the market worker; the rehearsal phase with 54 cases.

At 20:41 UTC the rest of the pass was stopped by hand (the task was ended while `AgentFaults6` waited for its
window; no process and no container of the run was left; the watch ended with the pass's end marker, written
by hand, after 4 readings and no stop). `m6-b9k` therefore ran no measurement phase. Then, from the tree of
commit `91b8612`, the two last phases were tried on runs that already exist, before a fresh run is started:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9j -Phase Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9k -Phase Report
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9j -Phase SecretScan -WaitForWindow
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9j -EndFile <repository>\.cache\m6\m6-b9j-secretscan.done -MaxHours 2 -Execute
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9l -Phase Prepare
```

OBSERVED: both `Report` calls exit 1 in under ten seconds with a FAILED record, as they must on these runs, and
without an error of their own. On `m6-b9j`: 45 problems (eleven phases without a record, seven product or
harness files changed since its Build, `AgentFaults6` ended as THREW, `Regression` never ended, and the rows
of the phases that did not run "not measured"). On `m6-b9k`: 63 problems, among them every attempt after the
Build on another tree, and `AgentFaults6` listed under `reruns` with two attempts, the first ended as THREW
with its cause ("Timed out after 120 s waiting for: the workflow waiting for its experiment") and the line
"FOR THE OWNER: accept or reject this rerun in the B9 report". `Prepare` for `m6-b9l`: exit 0, ten isolated
targets, no Docker call. The `SecretScan` trial and its watch were started at 20:44 UTC to wait for the 21:07
UTC window and were ended by hand at 21:03 UTC, before the window: the session of the retention fix reported
that it would recreate the normal market worker between 21:15 and 21:45 UTC on the owner's approval in that
session, and a market worker in a new container stops any test run by the owner's rule. No command of the
trial ran; the watch took 3 readings, no stop.

Checks after the fifth review's fixes, between 21:01 and 21:02 UTC, without a stack:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\run-pilot-rules-from-harness.ps1
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\try-cause-on-extracts.ps1
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <scratchpad>\timeout-test.ps1
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9k -Phase Report
```

OBSERVED: "cases: 57; not holding: 0". The three real restarts, each as its own slice of the kept extracts:
`RETENTION_STATEMENT_TIMEOUT` three times (296 and 1,062 characters between the cancellation and the function
name in the extract of 2026-10-06, which carries time stamps). The cut-off test: "timed out: True ... returned
after 5.6 s ... processes of the call still alive: 0". `Report` on `m6-b9k`: exit 1, FAILED, 63 problems as
before, the rerun of `AgentFaults6` with its cause.

## M6 B9 authoring run m6-b9j (2026-10-07)

By the M6 B9 session, from the primary checkout at commit `2f6a3a7` (clean). Windows PowerShell 5.1. Isolated
projects `asl-m6-m6-b9j-<kind>` only. The normal application was read, never changed, by the watch's two
read-only scripts (owner decision 8 of 2026-10-06 and the decision of 2026-10-07).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9j -Phase Prepare
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9j -EndFile <repository>\.cache\m6\m6-b9j-pass.done -MaxHours 48 -Execute
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File .cache\m6\m6-b9-pass.ps1 -RunId m6-b9j -Phases Build,Generate,Checks,ResearchActivationRehearsal,MixedVersion,PilotCoexistence,AgentFaults6,Migration,ApiAuth,Staging,ShadowSchedule,ResearchRunner,HoldoutIsolation,SourcePolicy,EvidenceInjection,DispatcherAuth6,EngineParity,Regression,AgentOffline6,BrowserResearch,BrowserResearchError,BrowserRegression,PerformanceApi,PerformanceBrowser,ResearchSaturation,PerformanceResearch,SecretScan,Report
```

The pass runner is scratch tooling under `.cache\m6`: it calls `tools\m6-acceptance.ps1 -RunId m6-b9j -Phase
<name> -WaitForWindow` for one phase at a time (`-BaselineRun m6-b2base` for `EngineParity`), in an order it
chooses from the list by what fits the current window, and goes on after a failed phase.

OBSERVED (UTC): `Build` 14:07, `Generate` 14:08, `Checks` 14:10, `ResearchActivationRehearsal` 14:10 to 14:31,
`MixedVersion` to 14:37, `Migration` to 14:39, `ApiAuth` to 14:42, `Staging` to 14:44, `HoldoutIsolation`
14:44, `SourcePolicy` to 14:46, `EvidenceInjection` to 14:47, `PilotCoexistence` 15:07 to 16:08,
`ShadowSchedule` 16:13, `ResearchRunner` 16:15, `DispatcherAuth6` 16:16, `EngineParity` 16:20: each exit 0 and a
VERIFIED record. `AgentFaults6` 16:08 to 16:12: exit 1, `AgentFaults6-process-failed-20261007T161154993Z.json`
(`A fault helper returned no result`; the helper's own error is `fixtures_require_disposable_asl_m1_database`).
`Regression` started 16:20:38: its first test command exited 0 at 16:35:46; its second started 16:35:47 and
never ended.

What was read to find the cause, at 18:47 UTC (the run's own isolated containers only):

```powershell
docker stats --no-stream asl-m6-m6-b9j-engine-engine-tests-run-f2c6d88c8efd asl-m6-m6-b9j-engine-fixture-postgres-1
docker logs --tail 25 asl-m6-m6-b9j-engine-engine-tests-run-f2c6d88c8efd
docker top asl-m6-m6-b9j-engine-engine-tests-run-f2c6d88c8efd
docker exec asl-m6-m6-b9j-engine-fixture-postgres-1 psql -X -U asl -d postgres -At -c "<pg_stat_activity and pg_locks of the test database>"
```

OBSERVED: the test container at 0.03 percent of a CPU with no output; in the isolated test database one
session idle in a transaction for 2 h 12 min after `SELECT id FROM account_state WHERE id=1 FOR UPDATE`, and one
waiting for it on `SELECT * FROM account_state WHERE id=1 FOR UPDATE`. On the host: the phase's PowerShell and
one `docker-compose.exe` (started 16:35:47) alive, its `docker.exe` gone.

How the run was stopped, 18:49 to 18:50 UTC: the pass runner's background task was ended; the left
`docker-compose.exe` was ended by its process number; then

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9j -Phase Stop
```

OBSERVED: exit 0; no container of the run running afterwards. The watch ended by its end file at 18:50:34 with
exit 0 after 50 readings and no stop.

The corrected timeout handling, tried without Docker at 18:54 UTC (a scratch script calls `Invoke-M6Docker`
with a PowerShell child that starts a grandchild sharing its output handles; both would sleep 180 s; limit
5 s): returned after 5.9 s with `timed_out` true, the output read so far, and no process of the call left. A
call that ends by itself: exit code and output as before.

NOT RUN in this run: `AgentOffline6`, `BrowserResearch`, `BrowserResearchError`, `BrowserRegression`,
`PerformanceApi`, `PerformanceBrowser`, `ResearchSaturation`, `PerformanceResearch`, `SecretScan`, `Report`,
`Clean`.

## M6 B9: the owner's decisions of 2026-10-07 implemented, and the market worker's log (2026-10-07)

By the M6 B9 session on branch `claude/m6-b9-final-acceptance`. Windows PowerShell 5.1 unless a block says Git
Bash. One command addressed the normal application: the log read below, which the owner approved in the
question dialog at about 13:26 UTC ([DECISIONS](../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log)).

The market worker's log, one read-only call with a time range, at 13:27:31 UTC, outside HH:58-HH:07 (Git Bash;
the output goes to two ignored scratch files):

```bash
MSYS_NO_PATHCONV=1 docker logs --timestamps --since 2026-10-06T13:40:00Z --until 2026-10-06T16:20:00Z adaptive-spot-lab-market-worker-1 \
  > .cache/m6/market-worker-log-20261006T1340-1620.txt 2> .cache/m6/market-worker-log-20261006T1340-1620.stderr.txt
```

OBSERVED: exit 0; nothing on standard output, 1,593 lines (247,550 bytes) on standard error, where the worker
logs. Two `market_worker_fatal` events with `UNEXPECTED_EXCEPTION`, at 13:51:57 and 15:53:56 UTC, each after a
`market_collection_gap` with `failure_type` `OperationalError` in phase `maintenance`; the traceback of each
ends in `psycopg.errors.QueryCanceled: canceling statement due to statement timeout` inside
`asl_prune_market_evidence`, at `DELETE FROM market_payloads WHERE id = ANY(payload_ids)`. Three
`market_retention_pruned` events (21,547, 21,330 and 21,426 records, at 13:52:23, 14:53:09 and 15:54:20), six
gaps with `failure_code` `stream_silent`. What ran on this host at those times was read from the 43 harness
command logs under `.cache/m6` (local files): between 13:30 and 14:07 UTC only the read-only observer
(13:48:37 to 13:49:40); between 15:14 and 16:08 only run `m6-b9c`, in `PilotCoexistence`.

Checked without a stack, between 13:37 and 13:45 UTC:

```powershell
# the parser on every script and module under tools: 45 files, 0 errors, no byte outside ASCII
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository (Get-Location).Path -Work $env:TEMP
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-watch.ps1 -RunId m6-b9i
```

OBSERVED: the deploy model exited 0 with 17 scenarios and 74 expectations (its first run with the new
expectations had one failing: the model's own check ignored the letter case; corrected, then all held). The
watch without `-Execute` printed its scope and ran nothing. `Test-M6PilotRules` and `Test-M6EnvFileRules`,
loaded out of `tools/m6/rollout.psm1` into a session that imported only `tools/lib/Research.psm1`: 31 and 47
cases held. A scratch script replayed the 161 recorded readings of the series with no test running through
`Get-PilotWatchVerdict`, and the reports the observer recorded on 2026-10-06 through `Get-ReportVerdict`
(local files only): no stop; at most six `PROTECTION_UNAVAILABLE` rows in thirty minutes; the reports pass at
13:48 and read "missing" at 14:10.

NOT RUN: any phase, any `pytest`, the watch with `-Execute`, the owner scripts against any Compose project.

## Env-file path PR merge recorded; main merged into the M6 B9 branch (2026-10-07)

By the M6 B9 session, in the primary checkout on branch `claude/m6-b9-final-acceptance`. No command addressed
the normal `adaptive-spot-lab` project and no Docker command was run for this section.

VERIFIED read-only at 13:01 UTC (Git Bash): pull request #30 is `MERGED`, `mergedAt` 2026-10-07T12:59:54Z, merge
commit `0f395a995880dc4ad43831570376eebc10c74c1e`, head `f0e8c89f80fd9a15bdb084f2696bbceda158b875`;
`origin/main` is `0f395a9`. This session did not merge it.

```bash
git fetch origin
git rev-parse --short origin/main
gh pr view 30 --json state,mergedAt,mergeCommit,headRefOid
```

The merge of `main` into the branch, local only (nothing pushed):

```bash
git merge --no-ff --no-commit origin/main
node resolve-merge.cjs          # scratch script: keeps both sides of the one conflict in STATUS, COMMANDS and DECISIONS
git add docs/STATUS.md docs/COMMANDS.md docs/DECISIONS.md
git commit -F commit-merge.txt  # 73789b9
```

OBSERVED: conflicts in `docs/STATUS.md`, `docs/COMMANDS.md` and `docs/DECISIONS.md` only, one place each, where
both sessions had added entries; `docs/OPERATIONS.md`, `docs/TESTING.md` and `tools/lib/Pilot.psm1` merged by
themselves. Every entry of both sides is kept (221, 452 and 177 lines).

Checked on the merged tree without a stack (Windows PowerShell 5.1, 13:03 to 13:10 UTC):

```powershell
# the parser on every script and module under tools: 44 files, 0 errors, no byte outside ASCII
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository (Get-Location).Path -Work $env:TEMP
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1 -WaitForWindow
```

OBSERVED: the deploy model exited 0 with 17 scenarios and 72 expectations, at 13:03 UTC and once more at 13:07
UTC after the repeated `Stop` line had been removed from `New-ProtectedBackup`; the M6 env file cases held
(47). `tools/env-file-path-check.ps1` printed `12 of 12 cases passed` and exited 0 at 13:10:15 UTC. In each of
its cases `docker` is a stand-in function and no docker program is on the reduced `PATH`; it was started at
13:06 UTC and waited for HH:10, because the tools it runs refuse part of every hour. Three of the four tools
take their backup through this branch's `New-ProtectedBackup`, so the check also shows that function in those
tools against the stand-in.

NOT RUN: any phase, any `pytest`, `ActivationRehearsal`, `AgentActivationRehearsal`, any push.

## Env-file path PR merge requested by the owner (2026-10-07)

OBSERVED owner instruction at about 12:58 UTC on 2026-10-07 in the same
session: `merge it`
([decision](../DECISIONS.md#2026-10-07--owner-asks-to-merge-the-env-file-path-pr)).
The delivery of the section below had happened as written there: commits
`aa12223`, `39d852c`, `a7ee675` and `d8534ffe19b902f6deede506af75b795fddffb7f`
pushed without force to pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30),
opened at 11:48:08 UTC.

VERIFIED read-only first, at 12:58 UTC: `main` at
`4ece326e29c7dd1239003b71ac8eca643159ee85`, unchanged since the change was
branched and checked; PR #30 `OPEN`, `MERGEABLE`, `CLEAN`, head `d8534ff`, no
check run, no review decision; working tree clean; no other pull request
open. No merge of `main` into the branch and no rerun is needed.

```bash
git fetch origin --prune
git rev-parse origin/main origin/claude/owner-tools-env-file-path HEAD
gh pr view 30 --repo MentorAliu/adaptive_spot_lab --json number,state,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision
gh pr list --repo MentorAliu/adaptive_spot_lab --state open --json number,title,headRefName
```

This record is committed and pushed to the branch as a documentation-only
commit, the scratch link check is run on it, and the pull request is then
merged pinned to that head:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md
git commit -m "docs: record the owner's merge request for the env-file path PR"
git push
gh pr merge 30 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <head>
gh pr view 30 --repo MentorAliu/adaptive_spot_lab --json state,mergedAt,mergeCommit
```

An ordinary merge commit; no force, no admin bypass, no branch deletion, no
auto-merge. This section is written before the merge and does not claim it. No
command addressed the normal `adaptive-spot-lab` project, and nothing was
deployed.

## Owner tools write the resolved env file (2026-10-07)

OBSERVED owner instruction in a separate Claude Code session
([decision](../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out)).
No command below addressed the normal `adaptive-spot-lab` project, started a
container or created a Docker resource. Windows PowerShell 5.1.26100.9444 for
every check; Git Bash for git and gh. The session worktree was used, on branch
`claude/owner-tools-env-file-path`.

**Preconditions (read-only).**

```bash
git fetch origin --prune
git rev-parse HEAD origin/main main
gh pr view 29 --repo MentorAliu/adaptive_spot_lab --json number,state,mergedAt,mergeCommit,headRefOid
gh pr list --repo MentorAliu/adaptive_spot_lab --state open --json number,title,headRefName
git ls-tree -r --name-only claude/m6-b9-final-acceptance tools/
git grep -n -E "Get-EnvSetting|Set-EnvSetting|Get-EnvValue|Set-EnvFlag" claude/m6-b9-final-acceptance -- tools docs
git switch -c claude/owner-tools-env-file-path
```

VERIFIED: pull request #29 is MERGED as
`4ece326e29c7dd1239003b71ac8eca643159ee85` at 12:49:48 UTC on 2026-10-06, from
head `26aad18`; `main` and `origin/main` are at that commit; no pull request
was open. `tools/lib/Research.psm1` is in no commit of `main`. It is in the
local branch `claude/m6-b9-final-acceptance`, whose commits name neither
`Get-EnvSetting` nor `Set-EnvSetting`: those two exist only in that branch's
working tree, which was read and not written.

**The check, on the tools as they were and as they are.** The first run reads
a copy of the five files at `4ece326`, unpacked in the session's scratch
directory:

```bash
git archive --format=tar -o <scratch>/main-tools.tar 4ece326 tools/lib/Pilot.psm1 tools/pilot-activate.ps1 tools/pilot-deactivate.ps1 tools/agent-activate.ps1 tools/agent-deactivate.ps1
tar -xf <scratch>/main-tools.tar        # in <scratch>/main
```

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1 -ToolsRoot <scratch>\main\tools
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1
```

Each case is one tool in a new PowerShell session, called with the call
operator and a relative `-EnvFile`, while the process directory is another
directory. A function stands in for `docker`, records its arguments and
answers with SYNTHETIC text; the session's PATH holds the Windows directories
only, and a case refuses to start while a docker program can be found. The
project name is `asl-envfile-check`, the env files are temporary, `-SkipBackup`
is given. The check shows which file a tool writes and what it passes on. It
is not evidence that a tool works against Docker.

| Tools | When (UTC, 2026-10-07) | Result |
|---|---|---|
| As at `4ece326` | 11:40:48 to 11:41:00 | exit 1, **0 of 8 cases passed**. In all eight the flags in the file given stayed as they were. In a session at its default error preference a file `case.env` was created in the process directory; the tool printed `Exception calling "ReadAllLines"` at the flag step and went on to start the workers. With the session preference `Stop` and a file of the same name in the process directory, that file was rewritten and the tool reported success |
| Changed | 11:41:00 to 11:41:11 | exit 0, **8 of 8 cases passed**: each tool, in both sessions, set its flags in the file given, wrote no other file, ended without an error, and every Compose call it made (4, 4, 12 and 2 per run) named the resolved file and the test project |

The check left nothing in the temporary directory. A first version of it
called the tools inside a `try`; that turns an error which a session only
prints into one that stops the tool, so it was rewritten to start one session
per case. The run above is on the final script and the final tools.

**What the unchanged writer and reader do (development observations on
temporary files in the scratch directory; the scripts are not in the
repository).**

- `Set-EnvFlag` on a file with LF line ends: every line end became CRLF. On a
  file with a byte-order mark: the mark was gone. `F=0` followed by `F: 0`, or
  by `export F=0`: only the first line was rewritten. `F=0 # note`: the
  comment was dropped.
- `Get-EnvValue`: `first` for a key assigned `first` then `last`; `"quoted"`
  with its quotes; `v # note` with the comment.
- A read-only env file, the changed tools, the stand-in (11:41:57 and 11:43:33):
  called from a session at its default preference, `pilot-activate.ps1`,
  `pilot-deactivate.ps1` and `agent-deactivate.ps1` printed
  `Exception calling "WriteAllLines"` at the flag step, went on and ended with
  exit code 0, the flags unchanged. With the session preference `Stop`,
  `pilot-activate.ps1` stopped at that step with exit code 1.
- Why: a script's `$ErrorActionPreference = 'Stop'` reaches a function of a
  module only when the script is started with `powershell.exe -File`, where it
  runs in the global scope. Called as `& tool.ps1`, the module sees `Continue`
  (shown with a two-file scratch module: exit 1 with `-File`, exit 0 and
  "continued" with the call operator). `tools/lib/Pilot.psm1` sets no
  preference of its own.
- A program that PowerShell starts gets the directory PowerShell stands in as
  its working directory, while .NET resolves a relative path in the process
  directory (shown with `cmd.exe /c cd` and `[IO.Path]::GetFullPath`). So
  `docker ... --env-file <relative>` and `Resolve-Path` agree, and only the
  .NET file calls of the writer did not.

**How Docker Compose v5.5.1 on this host reads an env file** (for the later
replacement of the reader and writer; not used by this change). One command
per case, on a compose file and an env file in the scratch directory, with
`ASL_*` and `COMPOSE_*` removed from the process environment. `config` only
renders text: it creates nothing.

```powershell
docker compose version
docker compose -f <scratch>\compose.yaml -p asl-envfile-check --env-file <scratch>\case.env config --format json
```

The compose file holds one service whose environment is
`V: "<${K-__UNSET__}>"`. OBSERVED value of `${K}`:

| Env file | Value |
|---|---|
| `K=0` then `K=1`; `K=0` then `export K: 1` | `1`: the last assignment |
| `K: 1`, `K:1`, `export K=7`, `export<TAB>K=3`, a line indented with spaces or a tab | assignments |
| `K=0 # c`, `K=0  # c`, `K=0 #` | `0`: a comment starts at a space followed by `#` |
| `K=0# c`; `K=0<TAB># c`; `K=0 <TAB># c` | `0# c`; `0<TAB># c`; `0 <TAB># c`: not comments |
| `K= # c` | `# c` |
| `K="0" # c`, `K="0"# c`, `K="0"<TAB># c`, `K='0' # c` | `0`: after a quoted value any `#` starts a comment |
| `k=lower` only | `lower`: on Windows a key that differs only in case is taken when the exact one is absent |
| `K=exact` and `k=variant`, in either order | `exact` |
| `K=` ; no line for `K`; `K` alone on a line | empty; unset; unset |
| `K=C:\secrets\dir`; `K='C:\a\b'` | kept as written |
| `K='C:\dir\'` | error: unterminated quoted value |
| `K="a\nb"`; `K=${X1}/x`; `K='${X1}/x'` | `a`, a line feed, `b`; the shell's value of `X1`, then `/x`; kept as written |
| `N="first`, `K=evil`, `last"` on three lines, and `K=good` before or after | `good`: a quoted value spans lines |
| A UTF-8 byte-order mark; CRLF line ends; no final line end | read |
| A UTF-16 file | error |
| A Latin-1 byte in a comment; a form feed before the key | read |
| `K=a<CR>OTHER=1<CR>` | `a<CR>OTHER=1`: a lone carriage return ends no line |

`config` prints a literal `$` as `$$`.

**Static checks.** The Windows PowerShell parser
(`[System.Management.Automation.Language.Parser]::ParseFile`) reports no error
in the four tools and the check script, and none of the five holds a byte
above 127. The difference of the four tools to `4ece326` is the six calls,
each with its path argument replaced, and five added comment lines.

**Documentation links.** The repository's link check runs in a container and
was NOT RUN. The same rules (relative target exists; a fragment matches a
GitHub heading slug, repeats numbered) were applied by a scratch PowerShell
script to every Markdown file under the repository root.

NOT RUN, with the reason: `tools/m4-acceptance.ps1 -Phase ActivationRehearsal`
and `tools/m5-acceptance.ps1 -Phase AgentActivationRehearsal`, which run the
four tools against Docker, because the owner limited this change to tests on
isolated files while the pilot runs; any test of `Set-EnvFlag` or
`Get-EnvValue` beyond the observations above, because they are unchanged;
GitHub CI. `.env`, `secrets/` and `codex_home/` were not read.

**Delivery.** Staged by an explicit path list, pushed without force, then a
pull request against `main` that is not merged:

```bash
git add -- tools/pilot-activate.ps1 tools/pilot-deactivate.ps1 tools/agent-activate.ps1 tools/agent-deactivate.ps1 tools/env-file-path-check.ps1 docs/COMMANDS.md docs/DECISIONS.md docs/OPERATIONS.md docs/STATUS.md docs/TESTING.md docs/plans/0015-evaluation-fixed-pilot.md docs/plans/0020-m5-agent-runtime.md
git commit -F <message file>
git push -u origin claude/owner-tools-env-file-path
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head claude/owner-tools-env-file-path --title "Pilot and agent tools write the resolved env file" --body-file <body file>
gh pr view 30 --repo MentorAliu/adaptive_spot_lab --json number,state,createdAt,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,url
```

VERIFIED after the push: commit
`aa12223fd28bb8ca2829780eab9ecd36eb0c4172` (12 files) is pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30),
created at 11:48:08 UTC on 2026-10-07, `OPEN`, `MERGEABLE`, `CLEAN`, without a
check run. It is not merged. This paragraph is committed to the branch as a
documentation-only commit.

### Second step the same day: a failed write stops the tool

OBSERVED owner decision at about 11:52 UTC, in this session's question dialog
([decision](../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out)):
`tools/lib/Pilot.psm1` is to stop on an error in its own functions also when
a tool is called by its path from a session, in pull request #30; the reader
and writer are replaced only after the B9 merge. The change is one assignment,
`$ErrorActionPreference = 'Stop'`, at the top of the module.

The check was extended first, from eight to twelve cases, and run before the
module was changed. Each tool is now also called with a read-only env file
from a session at its default preference: it must end with an error, leave
the file as it was and start no worker. The eight earlier cases no longer pass
`-SkipBackup`: the stand-in answers the backup's calls and writes a text file
in place of the dump, and the case requires that the database dumped is the
one the file given names (the file of the same name in the process directory
names another).

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1 -ToolsRoot <scratch>\main\tools -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\env-file-path-check.ps1 -WaitForWindow
```

| Tools | When (UTC, 2026-10-07) | Result |
|---|---|---|
| This branch at `39d852c`: the path correction alone | 11:53:18 to 11:53:36 | exit 1, **8 of 12**. The eight path cases passed, each backup dumping `asl_m1_envfile_check`. The four read-only cases failed: every tool ended without an error although its flags could not be written, and `pilot-activate.ps1` and `agent-activate.ps1` went on to start the workers |
| As at `4ece326` | 11:53:55 to 11:54:14 | exit 1, **0 of 12**. In the read-only cases the write went to a new file in the process directory, so the tool did not even meet the read-only file |
| This branch with the module change | queued at 11:54:14, ran from 12:10, ended 12:10:31 | exit 0, **12 of 12**. The eight path cases as in the first row. In the four read-only cases each tool stopped with an error, the file was as before, nothing else was written and no worker was started |

The second and third run were queued together; the third waited for the
tools' own time rule (`agent-activate.ps1` refuses from HH:55 to HH:10 UTC).
The check left nothing in the temporary directory.

**What the module change does not alter.** Started with `powershell.exe
-File`, a tool already ran the module's functions under `Stop` (the scratch
observation above), and that is how the rehearsals and both owner activations
ran. The functions that call a program (`docker`, `icacls`) set `Continue`
around that call themselves, as before.

**Static checks, links, delivery.** The parser reports no error in
`tools/lib/Pilot.psm1` and the changed check script, and neither holds a byte
above 127. The scratch link check was repeated on the final documents. The
second commit is staged by an explicit path list and pushed without force to
the same pull request, whose description is replaced:

```bash
git add -- tools/lib/Pilot.psm1 tools/env-file-path-check.ps1 docs/COMMANDS.md docs/DECISIONS.md docs/OPERATIONS.md docs/STATUS.md docs/TESTING.md docs/plans/0015-evaluation-fixed-pilot.md docs/plans/0020-m5-agent-runtime.md
git commit -F <message file>
git push
gh pr edit 30 --repo MentorAliu/adaptive_spot_lab --body-file <body file>
```

NOT RUN, as before: `ActivationRehearsal` and `AgentActivationRehearsal`.
`pilot-market-dump.ps1`, `agent-login.ps1` and `m5-deploy.ps1` use the module
too and were not run in any form.

VERIFIED after the push: commit
`a7ee675200cca4dc4667a275d97a66159559f65d` (9 files) is on the pull request's
branch since 12:12 UTC, and the description was replaced. The pull request is
not merged. This paragraph is committed as a documentation-only commit.

## M6 B9 authoring runs (2026-10-06, in progress; no acceptance run)

Actual commands of batch B9 so far. Every run named here is an authoring run on an uncommitted tree; results are
in [ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b9--rollout-measurements-faults-scan-and-report).
Windows PowerShell 5.1 unless a block says Git Bash. Isolated projects `asl-m6-<run>-<kind>` only; the one
exception is the approved read-only check of the normal app, shown last.

**A run and its phases** (VERIFIED as commands; each phase's result is in §18):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9i -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9i -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9i -Phase ResearchActivationRehearsal -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9i -Phase EngineParity -WaitForWindow -BaselineRun m6-b2base
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b9i -Phase Stop
```

The other phases take the same form with their name: `Generate`, `Checks`, `Regression`, `Migration`,
`MixedVersion`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule`, `SourcePolicy`,
`EvidenceInjection`, `AgentOffline6`, `DispatcherAuth6`, `AgentFaults6`, `ApiAuth`, `BrowserResearch`,
`BrowserResearchError`, `BrowserRegression`, `PerformanceApi`, `PerformanceBrowser`, `PilotCoexistence`,
`ResearchSaturation`, `PerformanceResearch`, `SecretScan`, `Report` (the last without `-WaitForWindow`). The
runs were `m6-b9a` to `m6-b9i`; `m6-b9g` was prepared and never built.

- **Windows.** A phase waits for an HH:07–HH:58 UTC window that holds its reserved minutes. Reservations added or
  changed in B9: rehearsal 42, `MixedVersion` 25, `PilotCoexistence` starts between HH:07 and HH:28 and runs
  through the next quiet window, `PerformanceApi` 35, `PerformanceBrowser` 25, `BrowserRegression` 32,
  `Regression` 33, `SecretScan` 40, `ResearchSaturation` two parts of 50, `PerformanceResearch` seven parts of
  40, 40, 48, 50, 48, 50 and 46. A part of 50 minutes fits only when it starts in the first minute of a window.
- **A phase needs this run's Build.** Ten phases started against `m6-b9g` before its Build and failed at once;
  that was a defect of a scratch runner, not of the harness.
- **Source and tools are bound to the Build.** `Generate`, the web checks, the browser phases and the rehearsal
  refuse a tree whose `apps/` or `services/` changed after the run's Build. `Report` also refuses a changed
  `tools/` file and a Build of an uncommitted tree.

**Checks between runs, without a stack** (VERIFIED; Git Bash; one container without a network):

```bash
cd services/engine
tar cf - app tests pyproject.toml alembic | MSYS_NO_PATHCONV=1 docker run --rm -i --network none asl-m6-m6-b9i-engine-tests \
  sh -c 'mkdir -p /tmp/w/services/engine && cd /tmp/w/services/engine && tar xf - && /workspace/services/engine/.venv/bin/ruff check --no-cache app tests'
```

The same form ran `pytest tests/test_m6_runner.py -k free_space` (1 passed, 7.4 s) and, in the browser test
image, Prettier and ESLint on the two edited e2e specs (both clean).

**Query plans on a disposable measurement database** (VERIFIED; Git Bash). After `PerformanceApi` had stopped
its stack, the fixture PostgreSQL of that run's `browser` target was started by name, read with `psql` inside
the container, and stopped again. On `m6-b9h` five trial indexes were created in that disposable database to
size the change; nothing of it reached a repository file before the owner was told.

```bash
docker start asl-m6-m6-b9i-browser-fixture-postgres-1
docker exec asl-m6-m6-b9i-browser-fixture-postgres-1 psql -X -U asl -d asl_m1_m6_m6_b9i_browser -c "EXPLAIN (ANALYZE, COSTS OFF) ..."
docker stop asl-m6-m6-b9i-browser-fixture-postgres-1
```

**The approved read-only check of the normal app** (decision 8 of 2026-10-06; VERIFIED from 20:45 UTC on; before
that the script could not run):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-check.ps1 -RunId m6-b9i -Since 2026-10-06T20:07:00Z -Label baseline
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-check.ps1 -RunId m6-b9i -Since 2026-10-06T20:07:00Z -Label baseline -Execute
```

Without `-Execute` it prints its command scope and runs nothing. With it, it lists the normal project's
containers, inspects their identity, and runs one fixed read-only SELECT in the normal PostgreSQL container. On
2026-10-06 it was run about seventy times with different `-Since` instants to locate the market worker's
incidents (§18), and then every five minutes by two scratch scripts under `.cache\m6` (a watch that stops the
isolated run on a difference, and a baseline series while no test runs). The B0 observer ran once, at 13:48 UTC.

NOT RUN: an acceptance run; `ResearchSaturation`, `PerformanceResearch`, the process part of `AgentFaults6`,
`SecretScan` and `Report` to the end; `Clean` of the runs `m6-b9e` to `m6-b9i` and `m6-b9obs` (their evidence is
still being read); `tools/m6-deploy.ps1`, `tools/research-activate.ps1` and `tools/research-deactivate.ps1`
against the normal app; any push or pull request.

**The second review's fix round, 2026-10-07 (VERIFIED as commands; no stack was started and no test ran).**
Windows PowerShell 5.1 unless a block says Git Bash.

The parser on every changed script (0 errors each):

```powershell
$t=$null;$e=$null;[void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path tools\m6-deploy.ps1).Path,[ref]$t,[ref]$e);"$($e.Count) parse errors"
```

The deploy script against a model of an installation (17 scenarios, 72 expectations, exit 0; last at 12:11
UTC, after the fourth review's fixes). A function answers for `docker`; the process cannot reach Docker. The
rehearsal runs the same file as one of its steps.

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools\m6\deploy-model.ps1 -Repository (Get-Location).Path -Work $env:TEMP
```

The scripts' env file and time rules on local files, by loading `Test-M6EnvFileRules` out of
`tools/m6/rollout.psm1` into a session that imported only `tools/lib/Research.psm1` (47 cases held; last at
12:11 UTC). No Docker call.

How the installed Compose reads an env file, on scratch files in the session's scratch directory (Git Bash,
11:36 UTC). `config` renders on the client: nothing is created, and the project name is one that does not
exist. `c.yaml` holds one service whose environment is `A: "${ASL_RESEARCH_ENABLED:-unset}"`.

```bash
docker compose version --short
MSYS_NO_PATHCONV=1 docker compose -f c.yaml -p asl-envfile-check --env-file e1 config --format json
```

OBSERVED with Docker Compose 5.5.1, the value of `A` for seven env files:

| Env file | `A` |
|---|---|
| `asl_research_enabled=1` | `1` |
| `ASL_RESEARCH_ENABLED=0`, then `asl_research_enabled=1` | `0` |
| `asl_research_enabled=1`, then `ASL_RESEARCH_ENABLED=0` | `0` |
| `Asl_Research_Enabled=1`, then `asl_research_enabled=2` | `1` |
| `OTHER="first`, `ASL_RESEARCH_ENABLED=1`, `last"` on three lines | `unset` |
| `OTHER=a`, a carriage return, `ASL_RESEARCH_ENABLED=1` on one line | `unset` |
| `ASL_RESEARCH_ENABLED=1`, a tab, `# c` | `1`, the tab and `# c` |

Whether a library function sees a script's error preference, on two scratch files (Windows PowerShell
5.1.26100, 11:39 UTC). OBSERVED: started with `-File` the function saw `Stop` and stopped at a failing cmdlet;
started with `-Command "& 'tool.ps1'"` it saw `Continue` and went on.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tool.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& 'tool.ps1'"
```

Lint and byte-compilation of the changed Python files, in one container without a network (Git Bash, at 06:52
and 06:56 UTC, and at 11:29 and 12:10 UTC for the whole of `app` and `tests` with `ruff check --no-cache app
tests`, the measurement fixtures included, the second time after the fourth review's fixes; outside
HH:58-HH:07; `ruff`: all checks passed each time):

```bash
cd services/engine
tar cf - app tests pyproject.toml alembic | MSYS_NO_PATHCONV=1 docker run --rm -i --network none --cpus 1 --memory 512m asl-m6-m6-b9i-engine-tests \
  sh -c 'mkdir -p /tmp/w/services/engine && cd /tmp/w/services/engine && tar xf - && /workspace/services/engine/.venv/bin/ruff check --no-cache app/execution/replay_path.py app/research/bridge.py app/research/runner.py app/research/stores.py tests/test_m6_bridge.py tests/test_m6_runner.py tests/m6_rollout.py && /workspace/services/engine/.venv/bin/python -m py_compile app/execution/replay_path.py app/research/bridge.py app/research/runner.py app/research/stores.py tests/test_m6_bridge.py tests/test_m6_runner.py tests/m6_rollout.py'
```

The whole tree must be in the container for the import order to be judged: with six files alone `ruff` reports
every first-party import as misplaced.

The read-only series of the normal app (decision 8), every five minutes outside HH:58 to HH:07 from 2026-10-06
21:25 UTC to 2026-10-07 13:14 UTC (161 readings, none failed), by a scratch script that calls only this and
writes one line a reading. The script loops until it is stopped; it was stopped at 13:15 UTC, and no process of
it was left:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-pilot-check.ps1 -RunId m6-b9i -Since 2026-10-06T21:25:18Z -Label baseline -Execute
```

The other session's pull request, read only (Git Bash, 12:15 UTC): OPEN, head `d8534ff`, 13 files.

```bash
gh pr view 30 --json number,state,title,headRefName,baseRefName,headRefOid,files
```

NOT RUN in this round: any phase; any `pytest`; the three owner scripts against any Compose project; `Clean`
of any run.

## M6 B9 preconditions and the B8 merge record (2026-10-06)

OBSERVED owner instruction in a Claude Code session: implement B9 and then
B10 of ExecPlan 0023, B10 only after B9 is accepted and the owner has said yes
in chat. This section records what the section below left for this
checkpoint. No command below addressed the normal `adaptive-spot-lab`
project. Git Bash.

VERIFIED read-only at 12:59 UTC on 2026-10-06: pull request #29 is MERGED as
`4ece326e29c7dd1239003b71ac8eca643159ee85` at 12:49:48 UTC, an ordinary merge
commit with parents `2043fc0a9ab777e36b250acd5dd311f1deb994af` and
`26aad187101d62ae41d6c9fd0ae37f1e57bedebd`; `origin/main` is at that commit
and no pull request is open. The primary checkout was still on the merged
branch `claude/m6-b8-owner-pages`; it was switched to `main`, fast-forwarded
from `2043fc0` to `4ece326` (clean tree), and B9 was branched from it.

```bash
git status --short --branch
git fetch origin --prune
git rev-parse origin/main
gh pr list --state open --json number,title,headRefName
gh pr view 29 --json number,state,mergedAt,mergeCommit,headRefName,baseRefName
git switch main
git merge --ff-only origin/main
git log -1 --format='%H %P %cI %s' 4ece326
git switch -c claude/m6-b9-final-acceptance
```

Nothing was built, run or deployed by these commands. The B9 phases and
their commands are recorded in their own section once they exist.

## M6 B8 PR merge requested by the owner (2026-10-06)

OBSERVED owner instruction at about 12:47 UTC on 2026-10-06 in the same
session: `merge it`
([decision](../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b8-pr)).
The delivery of the section below had happened as written there: commits
`fe85cecf715d4cdbfd125e30eb231a928f9fa285` (99 files) and `1ab82be` (the
record of the publication) pushed without force, and pull request
[MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29)
opened at 12:38:13 UTC on 2026-10-06.

VERIFIED read-only first, at 12:48 UTC: `main` at
`2043fc0a9ab777e36b250acd5dd311f1deb994af`, unchanged since B8 was branched
and accepted; PR #29 `OPEN`, `MERGEABLE`, `CLEAN`, head
`1ab82be0ddb981eccca601c9a832349f33e488ee`, no check run, no review decision;
working tree clean; no other pull request open. No merge of `main` into the
branch and no rerun is needed.

```bash
git fetch origin --prune
git rev-parse origin/main origin/claude/m6-b8-owner-pages HEAD
gh pr list --state open --limit 10
gh pr view 29 --json number,state,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision
```

This record is committed and pushed to the branch as a documentation-only
commit, the link check is run on it, and the pull request is then merged pinned
to that head:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md docs/plans/0023-m6-research-investigations.md
git commit -m "docs: record the owner's merge request for the M6 B8 PR"
git push
gh pr merge 29 --merge --match-head-commit <head>
gh pr view 29 --json state,mergedAt,mergeCommit
```

An ordinary merge commit; no force, no admin bypass, no branch deletion, no
auto-merge. This section is written before the merge and does not claim it. No
command addressed the normal `adaptive-spot-lab` project, and nothing was
deployed: deployment is B10.

## M6 B8 owner pages and same-origin functions (2026-10-06)

OBSERVED owner instruction in a Claude Code session: implement B8 of ExecPlan
0023 on a new branch from `main`, verify it in isolated stacks, open a pull
request and do not merge it
([decision](../DECISIONS.md#2026-10-06--m6-b8-skill-loading-consequence-lists-navigation-detail-routes-refresh-intervals-and-the-state-before-migration-0008)).
No command below addressed the normal `adaptive-spot-lab` project, a public
endpoint of the application or a model. Windows PowerShell 5.1 for the harness
and for Docker commands that take a container path; Git Bash for git and gh.

**Preconditions (read-only).** This records what the section below left for
this checkpoint: pull request #28 is MERGED as
`2043fc0a9ab777e36b250acd5dd311f1deb994af` at 06:12:45 UTC on 2026-10-06, from
head `c4dcec36d4819ea6f6cf18f1f52ad258174f6ae1`. `main` and `origin/main` are
at that commit, the tree was clean and no pull request was open. The primary
checkout was used. The nine running containers were the normal app's, which no
command touched.

```bash
git fetch origin --prune
git rev-parse HEAD origin/main
gh pr list --state open --limit 10
gh pr view 28 --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName
git switch -c claude/m6-b8-owner-pages
docker ps -a --format '{{.Names}}'
```

**Skills and project discovery, before any UI code.** The official shadcn and
Lightweight Charts skills are not registered for Claude Code in this session;
by the owner's decision the copies installed for Codex were read
(`~/.codex/skills/shadcn/`, `~/.codex/skills/lightweight-charts/`). Discovery
ran from `apps/web` in the authoring run's web tool image, on bridge
networking for this one command; it reached the shadcn registry only. Results
are in
[INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m6-b8-owner-pages-execplan-0023).

```powershell
docker run --rm asl-m6-m6-b8a-web-tools sh -c "cd apps/web && pnpm exec shadcn info --json"
docker run --rm asl-m6-m6-b8a-web-tools sh -c "cd apps/web && pnpm exec shadcn docs alert-dialog toggle-group empty table collapsible alert skeleton badge card dialog field"
docker run --rm asl-m6-m6-b8a-web-tools sh -c "cd apps/web && pnpm exec shadcn search @shadcn -q tabs -t ui"
```

**Official documentation read on 2026-10-06** with the authoring client's page
fetch: the Base UI alert dialog page and the TanStack Start middleware guide.
The TanStack Query `useQuery` reference answered HTTP 500 twice and was NOT
RE-READ; the installed typings were read instead.

**Authoring runs `m6-b8a` and `m6-b8b` (history, not acceptance).** Each
harness phase is `tools/m6-acceptance.ps1 -RunId <run> -Phase <phase>`, with
`-WaitForWindow` after Prepare.

```powershell
& tools\m6-acceptance.ps1 -RunId m6-b8a -Phase Prepare
& tools\m6-acceptance.ps1 -RunId m6-b8a -Phase Build -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b8a -Phase Generate -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b8a -Phase ApiAuth -WaitForWindow
```

- **Web development checks,** on a copy of the working tree's `src` and `e2e`
  inside the run's tool image, without a network (not acceptance evidence).
  The copy is needed because the route generator renames a file across
  devices, which fails on a bind mount. The formatter writes to a separate
  directory, which replaces files in the tree only after exit 0.

```powershell
docker run --rm --network none --cap-drop ALL --security-opt no-new-privileges:true `
    --mount "type=bind,source=<repo>\apps\web\src,target=/src-in,readonly" `
    --mount "type=bind,source=<repo>\apps\web\e2e,target=/e2e-in,readonly" `
    --mount "type=bind,source=<repo>\.cache\m6\m6-b8a\web-dev,target=/out" asl-m6-m6-b8a-web-tools sh -c `
    "cd /workspace/apps/web && cp -r /src-in/. src/ && cp -r /e2e-in/. e2e/ ; pnpm typecheck ; pnpm lint ; pnpm test:unit ; pnpm check ; pnpm build"
```

- **Browser development loop,** on the `browser` target of `m6-b8b` with the
  working tree's `e2e` directory mounted over the image's (not acceptance
  evidence). Only the Compose project `asl-m6-m6-b8b-browser` was addressed.

```powershell
$d = '.cache\m6\m6-b8b\browser'
$c = @('compose','--project-directory',$d,'-f',"$d\compose.yaml",'-p','asl-m6-m6-b8b-browser','--env-file',"$d\compose.env")
docker @c build api web browser-tests
docker @c up -d --wait --wait-timeout 60 fixture-postgres
docker @c exec -T fixture-postgres dropdb -U asl --maintenance-db postgres --if-exists asl_m1_m6_m6_b8b_browser
docker @c exec -T fixture-postgres createdb -U asl --maintenance-db postgres asl_m1_m6_m6_b8b_browser
docker @c run --rm --no-deps engine-tests .venv/bin/python -m app.research.migrate head
docker @c run --rm --no-deps engine-tests .venv/bin/python -m tests.m6_browser_fixture seed
docker @c run --rm --no-deps engine-tests .venv/bin/python -m tests.m6_browser_fixture samples /out/samples
docker @c up -d --wait --wait-timeout 120 api web
docker @c run --rm --no-deps -e ASL_M6_BROWSER=research -v "<repo>\apps\web\e2e:/workspace/apps/web/e2e:ro" browser-tests pnpm --filter web test:e2e e2e/m6.spec.ts --workers 1 --grep "@research"
docker @c stop --timeout 15
```

  For the two error selections the database is recreated and migrated to
  `0007_m5_agent_runtime` (`ASL_M6_BROWSER=unavailable`), and then the `api`
  service is stopped (`ASL_M6_BROWSER=error`). The fixture's samples were
  copied from `browser\out\samples` into `apps/web/src/research/samples/`.

**First full pass, run `m6-b8c` (08:43 to 09:40 UTC; history, not
acceptance).** Seventeen phases in this order, each at exit 0: Prepare, Build,
SourcePolicy, HoldoutIsolation, EvidenceInjection, Generate, BrowserResearch,
BrowserResearchError, AgentOffline6, Regression, Checks, ApiAuth, Staging,
ShadowSchedule, ResearchRunner, DispatcherAuth6, AgentFaults6. `Generate`
waited 21 minutes for its window. The counts are in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b8--owner-pages-and-same-origin-functions).

**Independent review.** Two read-only agents, one for the server functions
and the browser boundary and one for the pages and their tests; neither ran a
command. Their findings and what changed are in the plan's §18.

**After the review (development, not acceptance),** from 11:07 UTC:

- The web development checks above: typecheck and lint at exit 0; unit tests
  passed except the three sample checks, which needed samples from the changed
  API.
- Authoring run `m6-b8b`: `Build`, `ApiAuth` (5, 5 and 24 tests) and
  `Generate`, which rewrote `services/engine/openapi.json` and
  `apps/web/src/generated/api.ts` for the new field and exited 1 as it must.
- The browser loop above after a rebuild: the samples were written again from
  the new seed; the research selection passed with 7 tests at 11:30 UTC, the
  `unavailable` selection with 1 at 11:31 and the `error` selection with 1 at
  11:31. On the way it failed three times, each on a test that was wrong or on
  a defect it then showed: a row selector that matched a workflow without a
  review; an error test that started from a page without the owner's session
  read; and the new clipping check, which found disclosure buttons wider than
  their cards at 390 px (fixed) and one M4 card with the same defect (not
  changed; recorded in the plan's §19).
- The web development checks again, at 11:32 UTC: typecheck, lint, 155 unit
  tests, format and build at exit 0, and the route tree equal to the generated
  one.

**Acceptance, fresh run `m6-b8d` (11:33 to 12:32 UTC).** One sequence,
each phase with `-WaitForWindow` after Prepare, stopping at the first failure;
none failed. Only documents were edited while it ran.

```powershell
foreach ($phase in 'Prepare','Build','Generate','ApiAuth','Staging','ShadowSchedule','ResearchRunner',
        'DispatcherAuth6','AgentFaults6','SourcePolicy','HoldoutIsolation','EvidenceInjection',
        'BrowserResearch','BrowserResearchError','AgentOffline6','Regression','Checks') {
    if ($phase -eq 'Prepare') { powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b8d -Phase $phase }
    else { powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId m6-b8d -Phase $phase -WaitForWindow }
    if ($LASTEXITCODE -ne 0) { break }
}
```

VERIFIED, every phase at exit 0 on image
`sha256:2bd935cfe17ab463dc59ff2e52f68c3d01530321b4c6871809647df84b4b8ebf`:
Build; `Generate` (no difference, 495 product-source files equal to the Build
record); `ApiAuth` 5, 5 and 24; `Staging` 13; `ShadowSchedule` 11;
`ResearchRunner` 15 and 17; `DispatcherAuth6` 11 and 14; `AgentFaults6` 11
and 17; `SourcePolicy` 249; `HoldoutIsolation` 9; `EvidenceInjection` 24 and
2; `BrowserResearch` (waited from 11:45 for the 12:07 window: 41 fresh API
samples, 61 sample and page tests, 7 browser tests); `BrowserResearchError` 1
and 1; `AgentOffline6` 14, 84, 16 and 90 with the schema probe; `Regression`
169 in 932.27 s; `Checks` 407 engine tests and the six web checks (155 unit
tests). `Migration` and `EngineParity` were NOT RUN: their inputs are
unchanged.

**Cleanup, 12:34 to 12:35 UTC,** after the evidence was recorded, each run by
its exact name; the phase lists what it removes from the run's own manifests
and verifies each absence. No global prune.

```powershell
foreach ($run in 'm6-b8a','m6-b8b','m6-b8c','m6-b8d') {
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m6-acceptance.ps1 -RunId $run -Phase Clean -WaitForWindow
}
docker ps -a --format '{{.Names}}'
docker images --format '{{.Repository}}:{{.Tag}}'
docker volume ls --format '{{.Name}}'
docker network ls --format '{{.Name}}'
```

VERIFIED: 10, 15, 24 and 24 exact-name resources removed, 73 in all; no
`asl-m6-*` container, image, volume or network remains; the nine containers of
the normal app were running before and after and were not addressed. The
pinned Playwright base image `mcr.microsoft.com/playwright:v1.63.0-noble` is
kept with the other pinned base images.

**Documentation link check (after the cleanup, before the commit), VERIFIED.**
In a read-only container without a network, the repository mounted read-only:
`checked 90 Markdown files; 0 broken link(s)`, exit 0.

```powershell
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <repo>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

**Delivery.** The work is committed on `claude/m6-b8-owner-pages`, pushed
without force and opened as a pull request against `main`; it is not merged.
No product file changed after the Build of `m6-b8d`.

```bash
git add -A -- apps/web services/engine tools docs
git commit
git push -u origin claude/m6-b8-owner-pages
gh pr create --base main --head claude/m6-b8-owner-pages --title "M6 B8: owner pages and same-origin functions" --body-file <body file>
gh pr view 29 --json number,state,createdAt,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup
```

- OBSERVED: commit `fe85cecf715d4cdbfd125e30eb231a928f9fa285` (99 files) is
  pull request
  [MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29),
  created at 12:38:13 UTC on 2026-10-06: `OPEN`, `MERGEABLE`, `CLEAN`, base
  `main` at `2043fc0`, no check run. It is not merged, and no auto-merge is
  set.
- This record of the publication is a second, documentation-only commit on
  the branch; the link check was run on it.

## M6 B7 PR merge requested by the owner (2026-10-06)

OBSERVED owner instruction at about 06:09 UTC on 2026-10-06 in the same
session: `merge it`
([decision](../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b7-pr)).
The delivery of the section below had happened as written there: commits
`cf89f864f28bf80949a80193c4a45f6d262093f6` (46 files) and `79acde3` (the
record of the publication) pushed without force, and pull request
[MentorAliu/adaptive_spot_lab#28](https://github.com/MentorAliu/adaptive_spot_lab/pull/28)
opened at 23:18:56 UTC on 2026-10-05.

VERIFIED read-only first, at 06:09 UTC: `main` at
`d1f8d88c2672404ba081e76017ee82100ef5256c`, unchanged since B7 was branched
and accepted; PR #28 `OPEN`, `MERGEABLE`, `CLEAN`, head
`79acde37e52d4726a9ffdb721a9f4ddc1c8add4b`, no check run, no review decision;
working tree clean; no other pull request open. No merge of `main` into the
branch and no rerun is needed.

```bash
git fetch origin --prune
git rev-parse origin/main origin/claude/m6-b7-owner-api HEAD
gh pr list --state open --limit 10
gh pr view 28 --json number,state,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup,reviewDecision
```

This record is committed and pushed to the branch as a documentation-only
commit, the link check is run on it, and the pull request is then merged pinned
to that head:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md docs/plans/0023-m6-research-investigations.md
git commit -m "docs: record the owner's merge request for the M6 B7 PR"
git push
gh pr merge 28 --merge --match-head-commit <head>
gh pr view 28 --json state,mergedAt,mergeCommit
```

An ordinary merge commit; no force, no admin bypass, no branch deletion, no
auto-merge. This section is written before the merge and does not claim it. No
command addressed the normal `adaptive-spot-lab` project, and nothing was
deployed: deployment is B10.

## M6 B7 owner API, OpenAPI and generated types (2026-10-05)

OBSERVED owner instruction in a Claude Code session: implement B7 of ExecPlan
0023 on a new branch from `main`, verify it in isolated stacks, open a pull
request and do not merge it
([decision](../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)).
No command below addressed the normal `adaptive-spot-lab` project, a public
endpoint of the application or a model. Windows PowerShell 5.1 for the harness
and for Docker commands that take a container path; Git Bash for git and gh.

**Preconditions (read-only).** Pull request #27 is MERGED as
`d1f8d88c2672404ba081e76017ee82100ef5256c` at 14:06:19 UTC on 2026-10-05
(parents `7f0268a` and `2671935`); `main` and `origin/main` are at that
commit, the tree was clean and no pull request was open. The primary checkout
was used. `docker ps -a` showed no `asl-m6-*` container before the first
phase; the nine running containers were the normal app's, which no command
touched.

```bash
git fetch origin --prune
git rev-parse HEAD origin/main
gh pr list --state open --limit 20
gh pr view 27 --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName
git switch -c claude/m6-b7-owner-api
docker ps -a --format '{{.Names}}'
```

**Official documentation read on 2026-10-05** with the authoring client's page
fetch (results in
[INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m6-b7-owner-api-request-bodies-and-lock-waits--2026-10-05)):
the FastAPI request-parameter reference, the Pydantic unions page (its old
address redirects to the publisher's new site, which was then read) and the
PostgreSQL 17 page on `lock_timeout` and `statement_timeout`. After the
review, at about 21:48 UTC, the Pydantic strict-mode page and its conversion
table, for the strict integers of the new bodies.

**Authoring run `m6-b7a` (history, not acceptance).** Each phase is
`tools/m6-acceptance.ps1 -RunId m6-b7a -Phase <phase>`, with `-WaitForWindow`
after Prepare. Build ran six times as the source changed, each time with the
image build, the static tests and Ruff at exit 0.

```powershell
& tools\m6-acceptance.ps1 -RunId m6-b7a -Phase Prepare
& tools\m6-acceptance.ps1 -RunId m6-b7a -Phase Build -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b7a -Phase Generate -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b7a -Phase Checks -WaitForWindow
```

- Development checks, 16:08 to 16:22 UTC, on the run's `agent` target (the
  fixture database started, migrated once, used and stopped; not acceptance
  evidence). Run from PowerShell, because Git Bash rewrites the container
  path in `-e`:

```powershell
$r = '.cache\m6\m6-b7a\agent'
$c = @('compose','--project-directory',$r,'-f',"$r\compose.yaml",'-p','asl-m6-m6-b7a-agent','--env-file',"$r\compose.env")
docker @c up -d --wait --wait-timeout 60 fixture-postgres
docker @c run --rm --no-deps engine-tests .venv/bin/python -m app.research.migrate
docker @c run --rm --no-deps -e ASL_AGENTS_OFFLINE_TEST=0 -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider <selection>
docker @c stop fixture-postgres
```

  What they and the phases found, all fixed before any acceptance run:
  - **A model name used twice.** The first `Generate` (16:14 UTC) rewrote both
    generated files, as it must on changed source. Reading the result showed
    that the M4 `ExperimentDetail` type had disappeared from the generated
    types: B7 had defined a second class of that name in `app/main.py`, so the
    M4 experiment route would have built the M6 job model. Ruff does not flag
    a name that is used between its two definitions, and no M4 test had run
    yet. The M6 models were renamed, and a new pure test fails on any class,
    function or alias defined twice in that module; it then found a second
    `PageLimit` alias (identical, harmless), which was removed.
  - **A colon inside an SQL literal.** A `LIKE '%:register'` pattern in a
    `text()` statement would have been read as a bind parameter; the two
    patterns are now passed as parameters. Found by reading before the build.
  - **The trial list.** A refused candidate registration is a ledger row with
    the same outcome as a refused experiment request. The list now says which
    of the two an attempt was (`subject`) and includes accepted registrations.
  - **An older test.** `tests/test_api.py` pins the exact `SystemStatus`
    shape. It was updated for the two new fields and added to `ApiAuth`,
    because no M6 phase ran it.
  - The second `Generate` (16:18 UTC) rewrote the files again after the
    rename; the third (16:19 UTC) found no difference, and `Checks` then
    passed with 399 engine tests and the five web checks (50 web unit tests).

**First full pass, run `m6-b7b` (16:22 to 17:18 UTC; history, not
acceptance).** One PowerShell loop over the phases, each as
`& tools\m6-acceptance.ps1 -RunId m6-b7b -Phase <phase> -WaitForWindow`
(`Prepare` and `Snapshot` without the switch), stopping at the first failure:
Prepare, Snapshot, Build, AgentOffline6, Regression, HoldoutIsolation,
EvidenceInjection, Generate, Checks, DispatcherAuth6, AgentFaults6,
SourcePolicy, Staging, ShadowSchedule, ResearchRunner, ApiAuth. All sixteen
exited 0 without a skip; `Checks` waited from 16:42 to 17:07 UTC for its
window. Counts are in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence).

**Independent review.** Two read-only agents were started while that pass was
running, each given the files to read and no conclusion: one for the routes,
one for the read models and the harness. They ran no command that built,
tested or changed anything. Their findings and what changed are in §18 of the
plan.

**After the review: authoring run `m6-b7c` (21:33 to 21:47 UTC; history).**

```powershell
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase Prepare
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase Snapshot
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase Build -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase Staging -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase ShadowSchedule -WaitForWindow
& tools\m6-acceptance.ps1 -RunId m6-b7c -Phase Generate -WaitForWindow
```

- Build, `Staging` (21:37 to 21:39) and `ShadowSchedule` (21:40 to 21:41)
  exited 0. `Generate` (21:41) rewrote `services/engine/openapi.json` and
  `apps/web/src/generated/api.ts` and exited non-zero, as it must on changed
  models: 36 lines added to the types, none removed.
- Development checks on the run's `agent` target, with the commands shown for
  `m6-b7a` above and this run's paths:
  - `-m api_auth6 tests/test_m6_api.py`: 21 passed in 77.47 s.
  - `tests/test_m6_agents.py tests/test_m6_agent_units.py tests/test_m6_jobs.py`
    with `ASL_AGENTS_OFFLINE_TEST=1`: 154 passed in 198.21 s.
  - `tests/test_api.py tests/test_m5_api.py`: 10 passed.
- **The new tests against the code before the fixes.** The same M6 API
  selection on run `m6-b7b`'s `agent` target and image, with only the new test
  file mounted read-only over the image's copy
  (`-v <repo>\services\engine\tests\test_m6_api.py:/workspace/services/engine/tests/test_m6_api.py:ro`):
  11 failed, 10 passed. The ten that pass there assert behavior the fixes did
  not change, or cover what had no test.
- **The web checks on the regenerated types,** in the run's web tool image
  without a network, with the working tree's `apps/web/src` and
  `services/engine/openapi.json` mounted read-only: `api:check`, `typecheck`,
  `lint`, `test:unit` (52 passed) and `check` exited 0.

```powershell
$src = (Resolve-Path 'apps\web\src').Path; $api = (Resolve-Path 'services\engine\openapi.json').Path
docker run --rm --network none --cpus 2 --memory 3g -v "${src}:/workspace/apps/web/src:ro" -v "${api}:/workspace/services/engine/openapi.json:ro" --workdir /workspace asl-m6-m6-b7c-web-tools pnpm --filter web <check>
```

- Before the build, with no harness phase: Ruff and the pure unit file on the
  edited source, piped as a tar stream into a container of run `m6-b7b`'s
  image without a network (90 passed), and Prettier on two web files in that
  run's web tool image.
- **A mistake, corrected.** The first Prettier call ran in the wrong directory
  and failed, and the script around it copied the tool's error text over
  `apps/web/src/agents/schemas.ts` and `agents.test.tsx`. Both were restored
  before anything else used them: the schema file from the copy inside run
  `m6-b7b`'s web tool image (SHA-256
  `2d09121c0e31c4ab72949025ea1366e444fdd3781c07e77faab40bd31cad318a`, equal to
  the image's file), the test file from `git show HEAD:`, and the two intended
  edits were made again. The later calls write to a separate file and replace
  nothing unless the tool exits 0.

**First acceptance attempt, fresh run `m6-b7d` (21:47 to 22:10 UTC; failed,
history).** The same loop as for `m6-b7b`. Prepare, Snapshot and Build exited
0; `Generate` waited for its window and found no difference at 22:07, on 430
product-source files equal to the Build record; `Checks` passed at 22:08 with
407 engine tests and the five web checks (52 web unit tests).
`AgentOffline6` then failed at 22:10: of the 14 M5 offline tests one,
`tests/test_m5_runtime.py::test_activation_discovery_probes_verification_enable_and_drift`,
ended with `Fenced: LEASE_LOST`. The loop stopped there; no later phase ran on
this run.

- **Cause, measured.** That test builds one orchestrator, which takes the
  ten-second lease once, and then runs all twenty probes on it without the
  renewal the worker makes every two seconds. Six runs of the test alone on
  this run's image took 9.61 to 10.41 s; the three over ten seconds failed.

```powershell
docker @c run --rm --no-deps -e ASL_AGENTS_OFFLINE_TEST=1 -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis engine-tests sh -c "for i in 1 2 3 4 5 6; do .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m5_runtime.py -k test_activation_discovery --durations=1 2>&1 | grep -E 'call|passed|failed'; done"
```

- **Fix, in the test helpers only.** `tests/m5_agents.py` gains `Kept`, an
  orchestrator that renews its lease before each tick as the worker's keeper
  does; the shared `orchestrator()` helper and the M5 runtime test build it. A
  lease another holder took, or one that ran out, is still not renewed, so the
  fencing tests are unchanged. With the two changed files mounted read-only
  over the image's copies, eight runs of the test took 9.10 to 10.76 s and all
  passed. No product file changed.
- How long the test took before B7 was not measured. B6 added six probes to
  it and B7 added one read to every orchestrator tick; INFERRED that together
  they brought it to the length of one lease.

**Acceptance, fresh run `m6-b7e` (22:17 to 23:10 UTC), VERIFIED.** One image
(`sha256:f59c124a244c273a613906588571e3e593726164b778c5e2ddddea3bbb8d4963`),
the final source, sixteen phases at exit 0, no skipped test, no failed or
superseded record. The same loop, in this order so that each reservation fit
its window:

```powershell
$s = 'tools\m6-acceptance.ps1'
foreach ($p in 'Prepare','Snapshot','Build','Generate','Checks','AgentOffline6','ApiAuth','Staging','ShadowSchedule','ResearchRunner','Regression','SourcePolicy','EvidenceInjection','HoldoutIsolation','DispatcherAuth6','AgentFaults6') {
  if ($p -in 'Prepare','Snapshot') { & $s -RunId m6-b7e -Phase $p } else { & $s -RunId m6-b7e -Phase $p -WaitForWindow }
  if ($LASTEXITCODE -ne 0) { break }
}
```

| Phase | UTC | Result |
|---|---|---|
| Build | 22:17 | image, 8 static tests, Ruff |
| Generate | 22:17 | product source equal to the Build record (430 files); no difference in either generated file |
| Checks | 22:17–22:18 | 407 engine tests; web `api:check`, `typecheck`, `lint`, `test:unit` (52), `check` |
| AgentOffline6 | 22:18–22:22 | M5 14 and 84; new 16 and 90; schema probe |
| ApiAuth | 22:22–22:24 | 5, 5 and 21 |
| Staging | 22:24–22:26 | 13 |
| ShadowSchedule | 22:26–22:27 | 11 |
| ResearchRunner | 22:27–22:29 | 15 and 17 |
| Regression | 22:29–22:44 | 169 in 921.96 s |
| SourcePolicy | 22:44–22:45 | 249 |
| EvidenceInjection | 22:45–22:46 | 24 and 2 |
| HoldoutIsolation | 22:46–22:47 | 9 |
| DispatcherAuth6 | 23:07–23:08 (waited from 22:47 for its window) | 11 and 14 |
| AgentFaults6 | 23:08–23:10 | 11 and 17 |

- After the last phase, the SHA-256 of each of the 473 files under `apps/`,
  `services/` and `tools/` and of the root package files in the working tree
  was compared with this run's Build record: none differs, and the same 468
  files exist under the three directories. Only documents were edited while
  the run was in progress.
- NOT RUN: `Migration` (migration 0008, its seed lines and the grants are
  unchanged: `git diff main -- services/engine/alembic` is empty),
  `EngineParity` (the shared engine and the replay are unchanged), every B8
  and B9 phase, any model call, any public source, GitHub CI, any command
  against the normal app.

**Cleanup (23:15 to 23:16 UTC), VERIFIED.** Each run by its exact name, after
its evidence was recorded above; the phase waited for its HH:15 window.

```powershell
foreach ($run in 'm6-b7a','m6-b7b','m6-b7c','m6-b7d','m6-b7e') { & tools\m6-acceptance.ps1 -RunId $run -Phase Clean -WaitForWindow }
docker ps -a --format '{{.Names}}'; docker images --format '{{.Repository}}:{{.Tag}}'; docker volume ls --format '{{.Name}}'; docker network ls --format '{{.Name}}'
```

- Removed by exact name, with absence checked by the phase: 8 resources of
  `m6-b7a`, 16 of `m6-b7b`, 11 of `m6-b7c`, 8 of `m6-b7d` and 16 of `m6-b7e`
  (containers, volumes, networks and the runs' engine, schema-probe and web
  tool images). Evidence files under `.cache/m6/` are retained.
- Afterwards no container, image, volume or network named `asl-m6-*` exists.
  The nine running containers are the normal app's; no command touched them,
  and no global prune was used. Base images and build cache were not
  addressed.
- A first form of the cleanup loop did not parse in PowerShell (a `$t0:` in a
  string) and ran nothing.

**Documentation link check (after the cleanup, before the commit), VERIFIED.** In a read-only container
without a network, the repository mounted read-only: `checked 90 Markdown
files; 0 broken link(s)`, exit 0.

```powershell
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <repo>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

**Delivery (23:18 UTC).** One commit on the branch, pushed without force, and
one pull request against `main`. It is not merged; the owner decides.

```bash
git add -A apps/web/src docs services/engine tools
git diff --cached --check
git commit -F <message file>
git push -u origin claude/m6-b7-owner-api
git fetch origin --prune && git rev-parse origin/main
gh pr create --base main --head claude/m6-b7-owner-api --title "M6 B7: owner API, OpenAPI and generated types" --body-file <body file>
gh pr view 28 --json number,state,createdAt,headRefOid,baseRefName,mergeable,mergeStateStatus,statusCheckRollup
```

- OBSERVED: commit `cf89f864f28bf80949a80193c4a45f6d262093f6` (46 files) is
  pull request
  [MentorAliu/adaptive_spot_lab#28](https://github.com/MentorAliu/adaptive_spot_lab/pull/28),
  created at 23:18:56 UTC, `OPEN`, `MERGEABLE`, `CLEAN`, with no check run;
  `origin/main` is still `d1f8d88`, the commit the branch was made from.
- This record is a second, documents-only commit on the same branch. It
  changes no product, test or harness file, so no phase is rerun for it.

## Generation-1 trimming PR merge requested by the owner (2026-10-05)

OBSERVED owner instruction at about 14:05 UTC in the same session: `merge it`
([decision](../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-generation-1-trimming-pr)).
The delivery of the section below had happened as written there: commit
`8c0c7f04fd1c0a45faa8490a3e5210a28963c39f` (9 files) pushed without force, and
pull request
[MentorAliu/adaptive_spot_lab#27](https://github.com/MentorAliu/adaptive_spot_lab/pull/27)
opened at 13:29:08 UTC.

VERIFIED read-only first, at 14:05 UTC: `main` at
`7f0268a1c128ff83087e4fbb8bfc7ba339982f2f`, unchanged since the change was
branched and verified; PR #27 `OPEN`, `MERGEABLE`, `CLEAN`, head `8c0c7f0`, no
check run; working tree clean; no other pull request open. No merge of `main`
into the branch and no rerun is needed.

```bash
git fetch origin
git rev-parse origin/main origin/claude/g1-prompt-trim-order HEAD
gh pr view 27 --repo MentorAliu/adaptive_spot_lab --json number,state,mergeable,mergeStateStatus,headRefOid,baseRefName,reviewDecision,statusCheckRollup
gh pr list --repo MentorAliu/adaptive_spot_lab --state open --json number,title,headRefName
```

This record is committed and pushed to the branch as a documentation-only
commit, the link check is run on it, and the pull request is then merged pinned
to that head:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md docs/plans/0023-m6-research-investigations.md
git commit -m "docs: record the owner's merge request for the generation-1 trimming PR"
git push
gh pr merge 27 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <head>
gh pr view 27 --repo MentorAliu/adaptive_spot_lab --json state,mergedAt,mergeCommit
```

An ordinary merge commit; no force, no admin bypass, no branch deletion, no
auto-merge. This section is written before the merge and does not claim it. No
command addressed the normal `adaptive-spot-lab` project.

## Generation-1 prompt trimming order (2026-10-05)

OBSERVED owner instruction in a Claude Code session: confirm the open risk B6
recorded about generation-1 prompt trimming, propose, and change M5 behavior
only after approval; the owner then approved the correction
([decision](../DECISIONS.md#2026-10-05--generation-1-prompt-trimming-drops-the-oldest-result-first)).
No command below addressed the normal `adaptive-spot-lab` project, a public
endpoint or a model. Windows PowerShell 5.1 with a process-only Bypass; Git Bash
for git, gh and the one-off containers. Each harness phase is
`tools/m6-acceptance.ps1 -RunId <run> -Phase <phase>`.

**Confirmation before any change (11:54 to 12:08 UTC; development checks, not
acceptance evidence).** In the session worktree at `5da6b90`, which was `main`
when the session started, an uncommitted no-database test file and a sizing
script were run in one-off containers on the image of run `g1-trim-a`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-a -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-a -Phase Build -WaitForWindow
```

```bash
docker run --rm --network none --read-only --tmpfs /tmp:size=268435456 --cpus 1 --memory 768m --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges:true -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis -e ASL_TEST_ISOLATED=1 -e PYTHONDONTWRITEBYTECODE=1 asl-m6-g1-trim-a-engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider -v tests/test_m5_prompting.py
docker run --rm -i --network none --read-only --tmpfs /tmp:size=268435456 --cpus 1 --memory 768m --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges:true -e ASL_TEST_ISOLATED=1 -e PYTHONDONTWRITEBYTECODE=1 asl-m6-g1-trim-a-engine-tests .venv/bin/python - < .cache/m6/g1-trim-a/dev-check/measure.py
```

- Build waited from 11:54 for the 12:07 window: image `2a1243b1…38f3de8d`, 4
  static tests and Ruff passed.
- The test file: 4 passed in 0.83 s. One test asserted the behavior as it then
  was: of six results given newest first, over a reduced bound, the newest were
  hidden and the oldest stayed visible.
- The sizing, with SYNTHETIC values in the shape `query_market_features`
  returns (not a recorded workflow), at the real bound of 65,536 bytes:

| ANALYST prompt | Bytes | Hidden before the change | Hidden after it |
|---|---|---|---|
| No results | 13,188 | none | none |
| One result of 72 hourly bars and five other features | 31,216 | none | none |
| Two | 49,243 | none | none |
| Three | 67,270 untrimmed | the newest | the oldest |
| Six | 121,351 untrimmed | the four newest | the four oldest |

  The "after" column is the same script on the image of run `g1-trim-b`.
- Both commands were repeated at 13:05 UTC with the same results, to keep
  their outputs. The test file was then removed from the working tree and is
  not part of the change. A copy, the script and both outputs are kept under
  `.cache/m6/g1-trim-a/dev-check/` (git-ignored).

**Preconditions for the change (read-only, 13:06 UTC).**

```bash
gh pr view 26 --json number,state,mergedAt,mergeCommit,headRefOid
git fetch origin
git log --oneline -6 origin/main
gh pr list --state open --json number,title,headRefName,baseRefName
docker ps --format "{{.Names}}"
git switch -c claude/g1-prompt-trim-order origin/main
git branch --unset-upstream
```

VERIFIED: pull request #26 (B6) is MERGED as
`7f0268a1c128ff83087e4fbb8bfc7ba339982f2f` at 11:51:35 UTC, from head
`a4de2c7`, and `main` is at that commit. No pull request was open and no
`asl-m6-*` container of another session was running. The session's proposal
had still described #26 as open; see the decision.

**Run `g1-trim-b` on the changed source.** Phases ran one at a time through the
git-ignored wrapper `.cache/m6/g1-trim-sequence.ps1` (the B6 wrapper with this
worktree's paths), which stops at the first failure:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-b -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/g1-trim-sequence.ps1 -RunId g1-trim-b -Phases Snapshot,Build,AgentOffline6,DispatcherAuth6,AgentFaults6,Checks,EvidenceInjection
```

VERIFIED, 13:15:39 to 13:23:26 UTC, one image
(`24556e1b71043dc23ac8912ebcf6c4df14dee390951fe50ab20f20eea44baaa3`, built
from `7f0268a` plus this change), every phase exit 0, no skipped test:

| Phase | Result |
|---|---|
| Build | image built; 8 static tests passed in 2.29 s; Ruff passed |
| AgentOffline6 | M5: 14 passed in 45.47 s (offline, runtime, replay) and 84 passed in 36.43 s (schema, API, pure). New: 16 passed in 58.15 s and 72 unit tests in 7.08 s, one more than in B6: the new test. The schema probe through the pinned CLI passed |
| DispatcherAuth6 | M5: 11 passed in 20.77 s. New: 14 passed in 51.82 s |
| AgentFaults6 | M5: 11 passed in 20.81 s. New: 17 passed in 54.60 s |
| Checks | 389 passed in 11.26 s, one more than in B6 |
| EvidenceInjection | 24 passed in 29.91 s (B5 half); 2 passed in 9.66 s (dispatcher half) |

These are all the phases whose tests reach prompt composition: only
`test_m5_orchestrator.py`, `test_m5_runtime.py`, `test_m6_agents.py` and
`test_m6_agent_units.py` do, and `prompting.compose` is called only from
`orchestrator.py` and `workflows.py`.

**The new test against the old expression** (a one-off container without a
network; the code copied to a temporary directory inside it, nothing written
to the image or the repository):

```bash
docker run --rm --network none --read-only --tmpfs /tmp:size=268435456 --cpus 1 --memory 768m --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges:true -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis -e ASL_TEST_ISOLATED=1 -e PYTHONDONTWRITEBYTECODE=1 asl-m6-g1-trim-b-engine-tests sh -c '<copy app, tests and pyproject.toml to /tmp/e; run the two "oldest_result_first" tests; restore the old expression with sed; run them again>'
```

- On the copy as built: 2 passed.
- With the old expression restored:
  `test_a_generation_1_prompt_drops_its_oldest_result_first` FAILED on the
  newest result being hidden, and the generation-2 test passed.
- A first attempt failed before any assertion: Git Bash rewrote a container
  path passed with `-e`, so the prompts were not found. The variable is now set
  inside the container's shell.

NOT RUN, with the reason: `Regression`, `Migration`, `SourcePolicy`, `Staging`,
`ShadowSchedule`, `ResearchRunner`, `HoldoutIsolation` and `EngineParity`
(none of their tests composes a prompt, and no schema, seed, definition or
engine file changed); the M5 performance harness (`tests/m5_performance.py`),
which no M6 phase runs; process-level runner faults; any model call; GitHub
CI, which does not start on this repository. No read of the normal database
was made, so whether a stored M5 step was ever trimmed is not known.

**Closing checks.** The closing snapshot `source-003.json` (13:27:15 UTC, 532
entries) differs from the Build-bound `source-002.json` (13:15:43 UTC) in four
documentation files only (`docs/COMMANDS.md`, `docs/STATUS.md` and the two
plans). Every application, tool and test file is the one the tested image was
built from. The documentation link check, without a network and with the
worktree mounted read-only:

```powershell
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

VERIFIED at 13:28 UTC on the final documents: 90 Markdown files, zero broken
links, the four known historical Windows-link warnings in
`docs/plans/0003-market-data-charts.md`. (A first run at 13:27, before the
paragraphs below were added, gave the same result.)
(From Git Bash the same command failed to start, because the Windows mount
path was rewritten; it was run from PowerShell.)

**Cleanup.** Each run was cleaned by exact name inside HH:15 to HH:55 UTC;
evidence files stay under `.cache/m6/`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-a -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId g1-trim-b -Phase Clean -WaitForWindow
```

VERIFIED at 13:15:23 and 13:27:44 UTC: 3 exact-name resources removed from
`g1-trim-a` and 12 from `g1-trim-b`, no forced deletion, no global prune.
Afterwards no container, volume, network or image named `asl-m6-*` remained,
and the nine containers of the normal project were running as before; none was
addressed.

**Delivery.** One commit on `claude/g1-prompt-trim-order`, staged by an
explicit path list and pushed without force, then a pull request against
`main` that is not merged:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/RUNTIME_AGENTS.md docs/STATUS.md docs/TESTING.md docs/plans/0020-m5-agent-runtime.md docs/plans/0023-m6-research-investigations.md services/engine/app/agents/prompting.py services/engine/tests/test_m6_agent_units.py
git commit -F <message file>
git push -u origin claude/g1-prompt-trim-order
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head claude/g1-prompt-trim-order --title "Generation 1 prompt trimming drops the oldest result first" --body-file <body file>
```

This paragraph is written before the push and does not claim it; GitHub
records the pull request's number.


OBSERVED owner instruction at 11:49 UTC in the B6 session: `merge it`
([decision](../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-m6-b6-pr)).
VERIFIED read-only first: `main` at `5da6b90a3761abb6262dc040308cf7e9c4fb1d20`,
unchanged since B6 was branched and accepted; PR #26 `OPEN`, `MERGEABLE`,
`CLEAN`, head `6be9ed1cd55a7056127fce0022efb79e3f767d83`; working tree clean.
No merge of `main` into the branch and no rerun is needed.

```bash
git fetch origin
git rev-parse origin/main origin/claude/m6-b6-agent-workflows HEAD
gh pr view 26 --json number,state,mergeable,mergeStateStatus,headRefOid,baseRefName,reviewDecision
```

This record is committed and pushed to the branch as a documentation-only
commit, the link check is run on it, and the pull request is then merged pinned
to that head:

```bash
git add -- docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md docs/plans/0023-m6-research-investigations.md
git commit -m "docs: record the owner's merge request for the M6 B6 PR"
git push
gh pr merge 26 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <head>
gh pr view 26 --json state,mergedAt,mergeCommit
```

An ordinary merge commit; no force, no admin bypass, no branch deletion, no
auto-merge. This section is written before the merge and does not claim it.

## M6 B6 agent workflows and tools (2026-10-05)

OBSERVED owner instruction in a Claude Code session: implement B6 of ExecPlan
0023 on a new branch from `main`, verify it in isolated stacks, open a pull
request and do not merge it
([decision](../DECISIONS.md#2026-10-05--m6-b6-definition-generations-schedule-and-ended-shadows)).
No command below addressed the normal `adaptive-spot-lab` project, a public
endpoint or a model. Windows PowerShell 5.1 with a process-only Bypass; Git Bash
for git and gh.

**Preconditions (read-only).** PR #25 (B4) is MERGED as
`5da6b90a3761abb6262dc040308cf7e9c4fb1d20` at 22:30:14 UTC on 2026-10-04 and
`main` is at that commit; PR #23 is `6e8fbb6` and PR #24 is `52eab97`, both
already recorded. The primary checkout was clean and no other session was using
it, so the branch was created there. `docker ps` showed no `asl-m6-*` project
of another session before any heavy phase.

```bash
gh pr view 25 --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName
git fetch origin
git checkout --no-track -b claude/m6-b6-agent-workflows origin/main
docker ps --format "{{.Names}}\t{{.Status}}"
```

**Official documentation read on 2026-10-05** with the authoring client's page
fetch (results in
[INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m6-b6-agentstep-schema-v2-and-queries--2026-10-05)):
the Structured Outputs guide (the fetch ended before its "Supported schemas"
section, so the limits are carried from the B0 record and labeled INFERRED),
and the PostgreSQL 17 pages on JSON containment, the `SELECT` locking clause
and row-level locks.

**Authoring run `m6-b6a` (history, not acceptance).** Each phase is
`tools/m6-acceptance.ps1 -RunId m6-b6a -Phase <phase>`, with `-WaitForWindow`
after Snapshot.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6a -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6a -Phase Build -WaitForWindow
```

- 08:28 UTC: Build FAILED in its static step, as expected at that point: the
  image built and Ruff passed, and
  `test_migration_0008_freezes_the_same_agent_seed_rows_as_the_code` failed
  because the nine definition rows had not yet been frozen into migration 0008.
- The rows were then generated by the code in the run's own image and pasted
  into the migration as text. This is repeated whenever a v2 definition or an
  M6 prompt changes, and the test above compares the two:

```bash
docker run --rm --network none asl-m6-m6-b6a-engine-tests .venv/bin/python -m app.agents.definitions_v2
```

- Development checks, 08:30 to 08:56 UTC, on the same run's `agent` target and
  never inside HH:57 to HH:07 (the fixture database started, migrated, used
  and stopped each time; not acceptance evidence):

```bash
docker compose --project-directory .cache/m6/m6-b6a/agent -f .cache/m6/m6-b6a/agent/compose.yaml -p asl-m6-m6-b6a-agent --env-file .cache/m6/m6-b6a/agent/compose.env run --rm --no-deps -e ASL_AGENTS_OFFLINE_TEST=1 -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider <selection>
```

  What they found, all fixed before any acceptance run:
  - product: the latest approved profile was looked up among approvals of
    every kind (`approvals.py`); a completion body without a result would have
    raised (found by reading);
    the M5 agent read models refused schema 0008 (`views.py`);
  - tests and fixtures: B3's fixture helper leaves a queued workflow that
    already has a cutoff, which the orchestrator under test then tried to
    start; evidence availability cannot be backdated, so one cutoff test seeds
    its fixture dataset between two fetches; a path as an artifact ID is
    rejected by the step schema, not by the tool; and three expectations that
    did not count the scheduler's own research workflow.
  - M5 tests on schema 0008: two `test_m5_schema.py` tests and the routes of
    `test_m5_api.py` could not pass there. They were handled as recorded in
    [TESTING](TESTING.md#m6-b6-agent-workflows-and-tools-execplan-0023).

**Authoring passes of the phases on `m6-b6a`, 09:07 to 09:26 UTC (history).**
Phases are run one at a time by the git-ignored wrapper
`.cache/m6/m6-b6-sequence.ps1`, which stops at the first failure and logs to
`.cache/m6/<run>-sequence*.log`:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b6-sequence.ps1 -RunId m6-b6a -Phases Build,Checks,AgentOffline6,DispatcherAuth6,AgentFaults6,EvidenceInjection,SourcePolicy,Staging,ShadowSchedule,ResearchRunner,HoldoutIsolation,Migration
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b6-sequence.ps1 -RunId m6-b6a -Phases Build,Staging,ShadowSchedule,ResearchRunner,HoldoutIsolation,Migration -Log .cache/m6/m6-b6a-sequence2.log
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b6-sequence.ps1 -RunId m6-b6a -Phases Build,Migration -Log .cache/m6/m6-b6a-sequence3.log
```

- First pass, 09:07 to 09:17. Build (8 static tests, Ruff), Checks (378),
  AgentOffline6 (M5: 14 and 84; new: 11 and 61; the schema probe),
  DispatcherAuth6 (M5: 11; new: 12), AgentFaults6 (M5: 11; new: 11),
  EvidenceInjection (24 and 2) and SourcePolicy (249 and its probe) passed.
  Staging FAILED: 11 passed, 2 failed in 80.96 s. A B4 assertion lists the
  staging journal's row kinds exactly and did not know the storage observation
  B6 adds; and the new bridge test read a column that does not exist. Both are
  test-side; the assertion was updated in place and the new test corrected.
- Second pass, 09:18 to 09:24. Build, Staging (13 in 81.30 s), ShadowSchedule
  (10), ResearchRunner (15 and 17) and HoldoutIsolation (9) passed. Migration
  FAILED at `static-lock-retries` after its 19 schema tests had passed: the
  helper `tests/m6_migration.py` still expected only the M5 and research
  definition rows at revision 0008. It now expects what the code owns for both
  generations there, and the M5 set alone after a downgrade.
- Third pass, 09:25 to 09:26. Build passed. Migration stopped at
  `recovery-seed-legacy` with `OWNER_ALREADY_EXISTS`: the previous attempt had
  already seeded this run's recovery fixture. That is a property of the phase,
  which needs a fresh run, and says nothing about the code. The helper fix was
  therefore first exercised on the acceptance run below.

No product code changed during these passes. `m6-b6a` is an authoring run with failed
attempts and is not acceptance evidence.

**First full pass on fresh run `m6-b6b`, 09:26 to 10:19 UTC: every phase
passed.** Image
`sha256:f8203f380f3e1ae8edb1e92cc106d16a7d069642f79c2a9dbfe47748422f6629`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b6-sequence.ps1 -RunId m6-b6b -Phases Prepare,Snapshot,Build,Migration,Regression,Checks,AgentOffline6,DispatcherAuth6,AgentFaults6,EvidenceInjection,SourcePolicy,Staging,ShadowSchedule,ResearchRunner,HoldoutIsolation
```

| Phase | Result on `m6-b6b` |
|---|---|
| Build | 8 static tests, Ruff: exit 0 |
| Migration | 19 schema tests in 18.12 s; populated upgrade, downgrade, lock retries, old workers, dump and restore: VERIFIED |
| Regression | 169 passed, 1 existing warning, 942.29 s (09:29:21 to 09:45:16 UTC) |
| Checks | 378 passed in 11.97 s |
| AgentOffline6 | M5: 14 passed in 44.01 s and 84 passed in 35.43 s; new: 11 passed in 40.84 s and 61 unit tests in 7.35 s; schema probe VERIFIED |
| DispatcherAuth6 | M5: 11 passed in 20.19 s; new: 12 passed in 43.32 s |
| AgentFaults6 | M5: 11 passed in 20.09 s; new: 11 passed in 30.97 s |
| EvidenceInjection | 24 passed in 29.54 s; dispatcher half: 2 passed in 9.41 s |
| SourcePolicy | 249 passed in 43.35 s; Compose review and runtime probe |
| Staging | 13 passed in 81.08 s |
| ShadowSchedule | 10 passed in 44.76 s |
| ResearchRunner | 15 passed in 17.81 s; 17 passed in 64.44 s |
| HoldoutIsolation | 9 passed in 3.93 s |

The agent phases reserve up to 30 minutes of the HH:07 to HH:58 window, so the
phases after Checks waited from 09:45 for the 10:07 window.

**Independent review, 09:27 to about 09:55 UTC.** Three read-only reviewers
(separate agent sessions; `Read`, `Grep`, `Glob` and read-only `git` only; no
test, Docker or edit) read the working tree that `m6-b6b` was built from. Their
29 findings, 26 distinct, and the 24 fixes are listed in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b6--definitions-v2-tools-workflows-waiting-prompts-and-probes).
The fixes were developed from 10:00 to 10:45 UTC with the development checks
described above, again on `m6-b6a`'s `agent` target, after `m6-b6b` had
finished. The frozen seed rows were generated again, because two prompts
changed.

**Acceptance on fresh run `m6-b6c`, 10:45 to 11:38 UTC.** Image
`sha256:4b49f66765f29e67e7247b6f0898f61290ac6e1f960dfd395c861fb8f610ae5b`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b6-sequence.ps1 -RunId m6-b6c -Phases Prepare,Snapshot,Build,Migration,Checks,Regression,AgentOffline6,DispatcherAuth6,AgentFaults6,EvidenceInjection,SourcePolicy,Staging,ShadowSchedule,ResearchRunner,HoldoutIsolation
```

| Phase | Result on `m6-b6c` |
|---|---|
| Build | 8 static tests, Ruff: exit 0 |
| Migration | 19 schema tests passed in 17.62 s; populated 0007 to 0008 upgrade, downgrade to exactly the M5 seed set and re-upgrade, bounded lock retries, old-image fixture workers, dump and restore, downgrade refusal and the accounting, M3 and M4 invariants: VERIFIED |
| Checks | 388 tests passed in 10.96 s (the 317 of B2 to B5 and 71 new unit tests) |
| Regression | 169 M3 and M4 tests passed in 903.60 s, one existing warning (11:10:02 to 11:25:18 UTC) |
| AgentOffline6 | M5 on schema 0008: 14 passed in 45.18 s (`agent_offline`, `agent_runtime`, `agent_replay`) and 84 passed in 36.27 s (schema, API and schemas files). New: 16 workflow tests passed in 57.98 s and 71 unit tests in 7.86 s. Schema probe VERIFIED: the actual schema (111 properties, depth 9, 44 enumeration values, SHA-256 `bb328865…583aa05b`) is transmitted unchanged and strict by Codex CLI 0.159.2 to the loopback mock for both bundled test models, in a container without a network |
| DispatcherAuth6 | M5: 11 passed in 20.86 s. New: 14 passed in 51.81 s |
| AgentFaults6 | M5: 11 passed in 20.64 s. New: 17 passed in 54.80 s |
| EvidenceInjection | 24 passed in 30.36 s (B5 half); 2 passed in 9.74 s (dispatcher half) |
| SourcePolicy | 249 passed in 43.77 s; the Compose review and the runtime probe as in B5 |
| Staging | 13 passed in 84.64 s |
| ShadowSchedule | 10 passed in 45.30 s |
| ResearchRunner | 15 passed in 16.71 s (catalog); 17 passed in 63.99 s (runner) |
| HoldoutIsolation | 9 passed in 3.93 s |

`EngineParity` NOT RUN: no file of the shared engine, the strategy interface or
the replay path changed in B6. Build started at 10:46 UTC; Migration and the
phases after it waited for the 11:07 window.

The closing snapshot `source-002.json` (11:42:01 UTC, 532 entries) differs from the
Build-bound `source-001.json` (10:46:03 UTC) in eleven documentation files only. Every
application, tool and test file is the one the accepted image was built from.

**Documentation link check** (no network, the repository mounted read-only):

```bash
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

VERIFIED at 11:42 UTC on the final documents: 90 Markdown files, zero broken links, the four known historical Windows-link warnings in `docs/plans/0003-market-data-charts.md`. (A first run at 10:52 UTC, before the last document changes, gave the same result.)

**Cleanup.** Each run was cleaned by exact name inside HH:15 to HH:55 UTC,
after its evidence was recorded here; evidence files stay under `.cache/m6/`.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6a -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6b -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b6c -Phase Clean -WaitForWindow
```

VERIFIED at 11:39:37, 11:39:59 and 11:40:18 UTC: 21 exact-name resources removed from each of `m6-b6a`, `m6-b6b` and `m6-b6c` (containers, networks, volumes, the engine test image and the two schema-probe images), no forced deletion, no global prune. Afterwards no container, volume, network or image named `asl-m6-*` remained, and the nine containers of the normal project were running as before; none was addressed.

NOT RUN: any command against the normal `adaptive-spot-lab` project; any model
call or login; any public endpoint; `EngineParity`; the B7 to B9 phases;
GitHub CI.

**Delivery, 11:43 to 11:44 UTC.** `main` was still at `5da6b90`, so nothing had
to be merged into the branch. One commit,
`a65aafe2102c4107872ad7ffd12f9e24d3f0b3a3` (66 files, staged by an explicit
path list), pushed without force:

```bash
git fetch origin
git add -- docs services/engine services/agent-runner/prompts/m6 tools/m6-acceptance.ps1 tools/m6
git commit -F <message file>
git push -u origin claude/m6-b6-agent-workflows
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head claude/m6-b6-agent-workflows --title "M6 B6: definitions v2, tools, workflows, waiting, prompts and probes" --body-file <body file>
```

OBSERVED: pull request
[MentorAliu/adaptive_spot_lab#26](https://github.com/MentorAliu/adaptive_spot_lab/pull/26)
is open against `main` and mergeable, with no check run, since GitHub CI does
not start on this repository. It is not merged; the owner decides. This
paragraph was added by a documentation-only commit after the pull request
existed.

## M6 B4 merge of main and acceptance on the merged source (2026-10-04)

OBSERVED owner instruction at 21:30 UTC in the B4 session: `merge it`
([decision](../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b4-pr)).
VERIFIED read-only first: PR #24 (B5) is MERGED as
`52eab973d0de9365c8a820040aafeb53624b1ffa` (parents `6e8fbb6` and `c77e59d`) at
21:23:36 UTC, `main` is at that commit, and PR #25 reported `CONFLICTING`. So
`main` was merged into the B4 branch and the merged source accepted before the
PR is merged.

```bash
gh pr view 24 --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName
gh pr view 25 --json state,mergeable,mergeStateStatus,headRefOid
git fetch origin
git merge --no-ff --no-commit origin/main
git add -- tools/m6-acceptance.ps1 docs/COMMANDS.md docs/DECISIONS.md docs/STATUS.md docs/plans/0023-m6-research-investigations.md docs/README.md
git commit -m "Merge main (M6 B5, PR #24) into the M6 B4 branch"
```

Five files conflicted; local merge commit `35f25d9` (parents `38e14a1` and
`52eab97`). In `tools/m6-acceptance.ps1` both batches' phases are kept in the
two phase lists. In STATUS, COMMANDS, DECISIONS and the plan both sessions'
entries are kept, newest first; no entry of either side is dropped. Compose,
the contracts, migration 0008 and every other file merged without a conflict.
`git diff --check` was clean, the seven harness scripts parse under PowerShell
5.1 and are ASCII, and the shared engine and replay code is unchanged against
`6e8fbb6`.

Acceptance on fresh run `m6-b4c` (Windows PowerShell 5.1, process-only Bypass;
each phase is `tools/m6-acceptance.ps1 -RunId m6-b4c -Phase <phase>`, with
`-WaitForWindow` for every phase after Snapshot, run one at a time by the
git-ignored wrapper `.cache/m6/m6-b4c-sequence.ps1`, which stops at the first
failure):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b4c-sequence.ps1 -Phases Prepare,Snapshot,Build,Staging,ShadowSchedule,ResearchRunner,SourcePolicy,EvidenceInjection,HoldoutIsolation,Checks,Migration,Regression
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b4c-sequence.ps1 -Phases Snapshot,Build,Staging,SourcePolicy,EvidenceInjection,HoldoutIsolation,Checks,ShadowSchedule,ResearchRunner,Migration,Regression -Log .cache/m6/m6-b4c-sequence2.log
```

A first invocation of the wrapper at 21:34 UTC passed the phase list as one
string; the harness refused it as an unknown phase before preparing anything
(`m6-b4c-sequence-wrapper-error.log`). The wrapper was corrected.

**First attempt, 21:35–21:39 UTC, FAILED, kept as history.** Image
`sha256:2f13f9d289bcb57bdece106a2a5ef67bff5cd384512a413e6ba3c40126e20724`.
Build passed (4 static tests, Ruff). Staging passed (12 tests, 79.57 s).
ShadowSchedule passed (10 tests, 45.57 s). ResearchRunner FAILED in its catalog
tests: 14 passed, 1 failed (16.84 s). The sequence stopped there.

The failing test is `test_permission_lock_does_not_grant_epoch_mutation` in
`tests/test_m6_jobs.py`, a B3 test. Its last assertion expected `asl_source` to
be refused `research_hold_permission_epoch()`. B5 granted exactly that fixed
read to `asl_source` in migration 0008, records the grant in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b5--source-registry-fetcher-evidence-search-and-triggers)
and tests it in `tests/test_m6_sources.py`. B5's acceptance did not include
`ResearchRunner`, so the older assertion went stale when B5 merged. INFERRED,
not run: `main` at `52eab97` fails the same test, because B4 touches neither
file. This is not a B4 defect and no product code is involved.

Test-only correction: the B3 test now asserts what the merged contract says for
the source identity. It may take the fixed read, which returns the epoch and
changes nothing; it is still refused any change to the epoch; the epoch is
still 0 afterwards. The check on the research identity is unchanged.

**Final, on the rebuilt image, VERIFIED.** Image
`sha256:3327dd1e720e2bcbcea86717595c76fb0e0ad11dd970a8dda7c9316e5d75833e`,
21:40–22:27 UTC, every phase on that one image, inside the HH:07–HH:58 window,
one at a time, synthetic fixtures only, no skipped test:

| Phase | Actual result |
|---|---|
| Build | Image built; 4 selected static/registry tests passed (75 deselected, 1.80 s); Ruff passed |
| Staging | Research Compose review, bridge probe and default-disabled start passed; 12 tests in 79.66 s |
| SourcePolicy | Source Compose review, runtime probe and disabled fetcher passed; 249 tests in 43.39 s |
| EvidenceInjection | 24 tests in 31.63 s |
| HoldoutIsolation | 9 tests in 3.78 s |
| Checks | 317 tests in 7.61 s |
| ShadowSchedule | 10 tests in 43.30 s |
| ResearchRunner | 15 catalog tests (16.13 s), the runner isolation probe, 17 runner tests (59.04 s) |
| Migration | 19 schema tests in 17.43 s, 3 existing warnings; populated migration, bounded locks, old-image fixture workers, dump/restore, downgrade refusal and invariants VERIFIED |
| Regression | 169 M3/M4 tests in 872.85 s; one existing deprecation warning |

The counts equal those of the two batches' own acceptances (B4: 12, 10, 15 and
17, 9; B5: 249, 24, 317, 19; both: 169). The B3 six-cell result kept its
portable fingerprint `fca91e1d007880d0413331f2f3b30a6a7f1ea59926e94ee0c76583fd5c508858`.

NOT RUN: `EngineParity`. Neither batch changed `app/execution/`, `app/replay/`,
`app/strategies/` or `app/evaluation/`; B5's two lines in `app/db.py` add the
source identity to the role table. Also NOT RUN: every later-batch phase,
GitHub CI, any normal-app command, deployment, activation, a public endpoint
and a model call.

**Cleanup and closing checks.** At 22:28:39 UTC, 16 exact-name resources were removed from `m6-b4c`
(seven fixture containers, four networks, four volumes and the run's image); all eight project inventories are empty and both recorded
build image IDs are absent by exact ID. No prune ran and `Clean` addressed no
resource outside `asl-m6-m6-b4c-*`. `source-003.json` (22:28:22 UTC, 510 entries) differs from the Build-bound
`source-002.json` in documentation only, and the 447 non-documentation
files hashed again in the working tree before the commit all match it. The link
check passed: 86 Markdown files, zero broken links, the four known historical
Windows-link warnings.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4c -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4c -Phase Clean -WaitForWindow
docker image inspect --format '{{.Id}}' <each of the two recorded image IDs>
docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

The merge of PR #25 itself follows this record: an ordinary merge commit pinned
to the verified head, without force, an admin bypass or branch deletion. This
section does not claim it; GitHub records the merge commit.

## M6 B4 delivery (2026-10-04)

VERIFIED at 15:50 UTC. Plain `git` and `gh`, from the repository root on
`claude/m6-b4-bridge-staging-shadows`; no force, no merge, no admin bypass and
no branch deletion:

```bash
git add -- <the 34 B4 files, each named>
git diff --cached --check
git commit -F <message file>
git push -u origin claude/m6-b4-bridge-staging-shadows
git ls-remote origin refs/heads/claude/m6-b4-bridge-staging-shadows refs/heads/main
gh pr create --base main --head claude/m6-b4-bridge-staging-shadows --title "M6 B4: research bridge, staging, versioned stores and shadows" --body-file <body file>
gh pr view 25 --json number,state,mergeable,mergeStateStatus,headRefOid,baseRefName
gh run list --branch claude/m6-b4-bridge-staging-shadows --limit 5 --json name,status,conclusion,event,headSha
```

Results: commit `3e3c4776b8f23a8871dfdea32f383dc073b349b4` (34 files, 4,624
insertions, 98 deletions) with a clean worktree afterwards. The remote branch
is at the same hash and remote `main` is still `6e8fbb6`.
[PR #25](https://github.com/MentorAliu/adaptive_spot_lab/pull/25) is OPEN,
MERGEABLE and `CLEAN` at that head, created 15:50:33 UTC. Before the commit,
the 431 non-documentation files of the Build-bound `source-002.json` were
hashed again in the working tree: all match, so the committed source is the
tested source. GitHub CI did not run: the push run and the pull-request run
both ended in `startup_failure`, and the PR reports no checks. The merge is NOT
RUN. Read-only at 15:45 UTC, `gh pr list` showed one other open PR, #24 (B5),
against the same `main`.

This record is itself a documentation-only follow-up commit on the same branch;
it changes no product source and no acceptance scope.

## M6 B4 final-source acceptance (2026-10-04)

VERIFIED on fresh run `m6-b4b`, prepared from the final harness after the
independent review's fixes. Final image
`sha256:ffe756c4c45c7aa76a81cab5b28b393937b9a86c861063f404005d220308da0d`,
code identity `c747ddf7bbbf86d7f3901517b4eb1e261aa42f210eb7cbf065d67287e756b81d`.
Every phase below ran on that one image between 15:20 and 15:40 UTC, inside the
HH:07–HH:58 window, one at a time, on the run's `engine` (catalog) and `research` fixture projects; its six other prepared targets were not started. Synthetic fixtures only; no public endpoint, model call, original
credential or normal-project command. No test was skipped.

| Phase | Actual result |
|---|---|
| Build | Image built; 4 selected static/registry tests passed (75 deselected, 1.71 s); Ruff passed. `Build-b4.json` stays `PARTIAL` for full M6: later service images are not built |
| Staging | The four research Compose blocks rendered with fixture substitutions and checked (`ResearchCompose.json` VERIFIED; the normal project was not rendered). Runtime-shaped bridge probe VERIFIED: UID 10001, exactly two secrets, no volume, read-only root, no default route, both fixture databases reachable, every denied statement refused. The default command exited 0 with research disabled. 12 tests passed in 77.62 s |
| ShadowSchedule | 10 tests passed in 43.20 s |
| ResearchRunner | 15 catalog tests passed in 16.10 s; the runner isolation probe VERIFIED; 17 runner tests passed in 59.50 s |
| Regression | All 169 M3/M4 tests passed in 871.56 s; one existing Starlette/httpx deprecation warning |
| Checks | 145 tests passed in 6.77 s |
| HoldoutIsolation | 9 tests passed in 3.67 s |

The B3 six-cell deterministic result kept its portable fingerprint
`fca91e1d007880d0413331f2f3b30a6a7f1ea59926e94ee0c76583fd5c508858`, the value
recorded for B3: the runner's screening and full-test path is unchanged. The
B4 tests left two evidence files beyond their summaries, both labeled synthetic:
`research/out/b4-staging.json` (SHA-256 `14555e3c…39cdfd32`: 733 rows in 122
batches over 8 passes, every table equal to its published source, no pin and
no unpublished row) and `research/out/b4-shadow-r14.json` (SHA-256
`88b0cc9f…cf583e5f`: activation at the freeze 15:22:47.661845 UTC, bars opening
15:00, 16:00 and 17:00 evaluated and the bar that closed at 15:00 not, first
order decided at 18:00:01.27, and both subjects' first mark reproduced by the
second advance).

NOT RUN, with the reason: `Migration` and `EngineParity`. Migration 0008 and the
shared engine and replay code (`app/execution/`, `app/replay/`,
`app/strategies/`, `app/evaluation/`) are byte-identical to `main` at `6e8fbb6`;
B4 changed `app/research/` only. Also NOT RUN: every later-batch phase, GitHub
CI (it does not start on this repository), any deployment or activation.

Actual commands (Windows PowerShell 5.1, process-only Bypass), in order. The
first Staging attempt on this run failed on one of its own new tests (it
assumed rows were left after two full batches); the test was corrected, the
image rebuilt, and the whole sequence run on the rebuilt image:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Staging -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Staging -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase ShadowSchedule -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase ResearchRunner -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Regression -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Checks -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase HoldoutIsolation -WaitForWindow
```

The failed first attempt ran on image
`sha256:8fe629320208baf771ce73826d118b8805a2618258dc8c61812dc7623b1c57d9`
(Staging: 11 passed, 1 failed, 76.31 s) and stays in the run's journal.
Native argument arrays, exit codes and outputs are in
`.cache/m6/m6-b4b/commands.jsonl` and its timestamped logs.

**Cleanup and closing checks (15:45–15:50 UTC).** After the evidence above was
recorded, each run was cleaned by exact names, one after the other:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4b -Phase Clean -WaitForWindow
docker image inspect --format '{{.Id}}' <each of the ten recorded image IDs>
docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

VERIFIED: `m6-b4a` at 15:45:53 UTC and `m6-b4b` at 15:46:05 UTC each removed
seven exact-name resources (the catalog and research fixture containers, their
two networks, their two volumes and the run's image); every one of the eight
project inventories per run is empty afterwards. All ten recorded build image
IDs, the eight authoring images and both `m6-b4b` images, are absent by exact
ID. No prune of any kind ran, and `Clean` addressed no resource outside
`asl-m6-m6-b4a-*` and `asl-m6-m6-b4b-*`. `source-003.json` (15:45:09 UTC, 494 entries)
differs from the Build-bound `source-002.json` in `docs/COMMANDS.md` and
`docs/INTEGRATION_EVIDENCE.md` only. The link check on the completion
documentation passed: 86 Markdown files, zero broken links, the four known
historical Windows-link warnings. Evidence, failed attempts included, stays
under `.cache/m6/m6-b4a/` and `.cache/m6/m6-b4b/`.

## M6 B4 authoring iterations (2026-10-04)

OBSERVED start: clean `main` and `origin/main` at
`6e8fbb60fa2b7fc18576a3d67b273c9d8d5968b6`; created
`claude/m6-b4-bridge-staging-shadows`. Every Docker command of this section
selects the standalone `asl-m6-m6-b4a-*` fixture projects, fresh fixture
credentials and internal networks. No normal-project command, owner secret,
model or public endpoint was used. One host-wide `docker ps --format '{{.Names}}'`
was run once at 14:22 UTC before the first build, to see what was running; it
reads container names only, addresses no project and was not repeated.

Actual Windows PowerShell 5.1 commands (process-only Bypass), in order; the
three middle phases were repeated as described below:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase Staging
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b4a -Phase ShadowSchedule
docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo
```

These runs shaped the code and tests; none of them is acceptance evidence. The
final-source record is the section above. What happened, with
the image each attempt ran on (all tagged `asl-m6-m6-b4a-engine-tests` in turn):

| UTC | Image | Phase and actual result |
|---|---|---|
| 14:23 | `d30f338d…79db8c0` | Build: image and four static checks passed; Ruff FAILED on two import blocks (I001, formatting only) |
| 14:23 | `15397bfa…b40cad38` | Build passed. Staging FAILED in the new bridge probe: its privilege query resolved a table name before the schema filter applied (`relation "public.pg_statistic" does not exist`). Probe corrected to query by OID |
| 14:25 | `ba0afc6f…7981427c` | Build passed. Staging FAILED in the probe: a `CREATE DATABASE` refusal was tested inside a transaction, which PostgreSQL rejects for another reason. Probe corrected to test it on an autocommit connection |
| 14:26 | `e05eb257…40be0619` | Build passed. Staging: compose review, probe and default-disabled start passed; tests 10 passed, 1 FAILED (76.45 s): the rows a pass reported (82) were fewer than the rows its batches had counted (84), because the collection row was sent again with every batch. The inserts were no-ops; the count spent the 500-row bound. Staging now skips rows already in the store |
| 14:28 | `1387ce2a…d1588af5` | Build passed. Staging: 10 passed, 1 ERROR at fixture setup (72.39 s): a deadlock on the fixture store between the test reset's `GRANT` plus `TRUNCATE` transaction and another backend. Not a product path; the reset now truncates alone. ShadowSchedule: 7 passed, 1 ERROR (33.16 s): pytest collected a helper named `tested…`; renamed |
| 14:32 | `386bcb51…fb5008e` | Build, Staging (11 passed, 72.72 s) and ShadowSchedule (7 passed, 33.06 s) passed, no skips |
| 14:38 | `ab06e27b…689e5e4` | After review refinements (bridge schedule cadence and log volume, one engine pair per store in the runner, evidence files from the tests): Build, Staging and ShadowSchedule passed again, no skips |
| 15:15 | `dcea0409…bd92d82` | After the independent review's fixes (below): Build passed; ShadowSchedule passed, 10 tests, 43.00 s. Staging FAILED in the probe, as expected on this run: its fixture, prepared at 14:22, still mounted the data volume that the bridge no longer has. A fresh run was prepared for the final source |

**Independent review (14:42–15:05 UTC).** A separate read-only agent reviewed the
uncommitted code against the plan and the four owner decisions; it ran nothing.
It reported ten findings. Nine led to product changes, all before the
final-source run:

- an advance is recorded only for an idle runner, and one that never ran is recorded again the same day (several advances queued together would have lost their hour, which runs from the request);
- at a store's day cap, a shadow whose window is fully staged keeps its last advance;
- a failing stage, store, shadow or delivery no longer stops the bridge's other work, and a suspended shadow leaves an already rejected candidate as it is;
- a store that lost what was staged into it, or a dropped name offered again, is refused;
- the staging journal is written every five minutes, or at once when a gap was recorded, instead of every pass;
- a retention gap is also read from the journal at the next advance, so a bridge that stopped right after recording it still ends the shadow;
- a dataset is sealed once per UTC day whichever store is current, and never re-hashed when nothing new was staged;
- a failed store creation leaves no database and is not repeated for an hour;
- the bridge mounts no volume: the runner publishes the free space.

The tenth, a lookup through the collections view that may approach the 2 s
limit on the normal database, cannot be measured on fixtures and is recorded as
an open risk in [ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks),
with one B3 behavior the review surfaced (a job's hour runs from its request).

The link check at 14:48 UTC passed: 86 Markdown files, zero broken links, the
four known historical Windows-link warnings; `--rm` removed its container.
Native argument arrays, exit codes and outputs of every attempt, failed ones
included, are in `.cache/m6/m6-b4a/commands.jsonl` and its timestamped logs.

## M6 B5 source registry, fetcher, evidence and search (2026-10-04)

OBSERVED owner instruction to implement B5 only, in a second session beside B4
([decision](../DECISIONS.md#2026-10-04--owner-assigns-m6-b5-to-a-second-session-with-the-b5b6-split-of-evidenceinjection)).
The work is on branch `claude/m6-b5-source-registry`, in its own worktree
`.claude/worktrees/m6-b5-source-registry`, from `origin/main` at `6e8fbb6`.
Every command below ran from that worktree, against isolated `asl-m6-<run>-*`
projects only. No normal-app command, public endpoint, model call or real
credential was used, and no seeded source version was approved.

Preflight (all exit 0):

```powershell
git fetch origin
git worktree list
gh pr list --state open --json number,title,headRefName,baseRefName,updatedAt,isDraft
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Label "com.docker.compose.project"}}'
docker compose ls -a
```

OBSERVED: `origin/main` at `6e8fbb6`; no open pull request; the primary checkout
on `claude/m6-b4-bridge-staging-shadows` (B4, another session); only the nine
normal-app containers running, and no `asl-m6-*` project.

**One stack at a time.** The harness keeps `.cache/m6/<run>` and `heavy.lock`
under its own checkout, so two worktrees do not lock each other. The authoring
helper `.cache/m6/<run>/run-phase.ps1` (not part of the repository) waits until
the phase fits its window and `docker ps` shows no other session's `asl-m6-*`
container, then calls the harness. It was used for every phase after the first
Build.

**Authoring checks without a stack** (a one-off container with no network,
removed on exit; not acceptance evidence):

```bash
docker run --rm --network none -e PYTHONPYCACHEPREFIX=/tmp/pyc -v <worktree>/services/engine:/src:ro python:3.13.11-slim-bookworm sh -c 'cd /src && python -m py_compile app/sources/*.py … tests/test_m6_evidence.py'
docker run --rm --network none --read-only --tmpfs /tmp:size=268435456 --cpus 1 --memory 768m --pids-limit 128 --cap-drop ALL --security-opt no-new-privileges:true -e HYPOTHESIS_STORAGE_DIRECTORY=/tmp/hypothesis -e ASL_TEST_ISOLATED=1 -e PYTHONDONTWRITEBYTECODE=1 asl-m6-m6-b5a-engine-tests .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_m6_source_units.py
```

- Syntax check of every new Python file: exit 0. The seed documents in
  `app/research/definitions.py` and migration 0008 parse to equal values.
- 12:51:01 UTC, the unit file on the first image: FAILED at collection
  (`TypeError` in `app/sources/transport.py`: a dataclass field named `bytes`
  shadowed the built-in type). Fixed by renaming the field to `size`.
- 12:51:49 UTC, on the rebuilt image: 157 passed in 3.19 s.
- 12:52:03 UTC, the transport cases of `tests/test_m6_sources.py` against the
  loopback TLS mock: 53 passed in 10.97 s; one selected database-backed case
  errored at set-up, as it must without a database.

**Harness, run `m6-b5a`** (Windows PowerShell 5.1, process-only Bypass):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5a -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5a -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5a -Phase Build
```

- Prepare: eight isolated targets with fresh fixture secrets. Snapshot: `source-001.json`.
- Build, 12:50:49 UTC: image build, four static/registry checks and Ruff, exit 0.
- Build, 12:51:44 UTC, after the `size` rename: exit 0.
- SourcePolicy was queued at 12:52:42 UTC for the HH:07 window and canceled at
  13:05:10 UTC before any Docker call, because the trigger coalescing and two
  test files had changed since that image
  (`SourcePolicy-canceled-before-start.json`; no harness process remained).

**First full pass, run `m6-b5a`** (each phase through the helper, which calls
`tools/m6-acceptance.ps1 -RunId m6-b5a -Phase <phase>`):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase SourcePolicy
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase EvidenceInjection
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Checks
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Regression
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Migration
```

| Phase | Ended (UTC) | Result on image `a2e5d56e…62f93b5` |
|---|---|---|
| Build | 13:07:13 | exit 0 |
| SourcePolicy | 13:08:07 | Compose-block review; 230 passed in 29.37 s; runtime probe VERIFIED |
| EvidenceInjection | 13:08:37 | 23 passed in 18.78 s |
| Checks | 13:09:17 | 302 passed in 7.00 s |
| Regression | 13:23:51 | 169 passed, 1 existing warning, in 862.41 s |
| Migration | 13:26:08 | 19 schema tests passed in 17.24 s; populated migration VERIFIED |

No test was skipped. This run is history: an independent read-only review of
`services/engine/app/sources/` (a subagent of the same session; it ran no
command) then reported eight defects, listed in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b5--source-registry-fetcher-evidence-search-and-triggers).
The phase records were kept as `pre-review-*.json` before any rerun.

**Acceptance after the fixes, fresh run `m6-b5b`** (a product-code fix reruns
every phase; Migration also needs a fresh run because it creates its copies):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5b -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Build -RunId m6-b5b
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase SourcePolicy -RunId m6-b5b
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase EvidenceInjection -RunId m6-b5b
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Checks -RunId m6-b5b
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Migration -RunId m6-b5b
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Regression -RunId m6-b5b
```

| Phase | Ended (UTC) | Result on image `sha256:5cfcf2c911d1380b4217c797ec0991e939eafa94d23224e8405a514b5b9ec51f` | Evidence SHA-256 |
|---|---|---|---|
| Build | 13:29:39 | Image build, four static/registry checks, Ruff: exit 0 | `Build-b3.json` `e0056b5c…bcae4220` |
| SourcePolicy | 13:30:49 | Compose-block review (`SourceCompose.json` `0cb9457f…4a4e1c4a`); 249 passed in 43.29 s; probe: UID 10001, one secret, no default route, root write denied, one private address resolved, tick `DNS_NOT_PUBLIC`; identity back to NOLOGIN; disabled fetcher idle | `SourcePolicy.json` `1270405615e69f243e34584d26ebb9c6689789e2d717beca44a77e9616c25a53` |
| EvidenceInjection | 13:31:30 | 24 passed in 29.59 s | `EvidenceInjection.json` `46cb29f6f98a566a7d78beaff62f8557e566fa8077832105be00947fdc1987d8` |
| Checks | 13:31:49 | 317 passed in 7.45 s | `Checks.json` `cfd14891400d41ce8bff663b33841edb848ee1b732244e6f07f20bac50f54145` |
| Migration | 13:34:08 | 19 schema tests passed in 17.41 s, 3 existing warnings; populated migration, bounded locks, old-image fixture workers, dump/restore, downgrade refusal, invariants: VERIFIED | `Migration.json` `5f7c29cfe7147e30fa6285d2d80157ac4f0d60cf8d45a81b856a44ec69113ce6` |
| Regression | 14:22:03 | 169 passed, 1 existing warning, in 885.55 s (started 14:07:05, the first HH:07 window after Migration) | `Regression.json` `f7875b8746a38d678303d03e81786309016fe95ed9e782464e6c7b551f6ef670` |

No test was skipped. The mock source is a TLS server on the test container's
loopback; no request left an isolated network, and no model was called.

**Cleanup** (exact names from each run's manifest; no forced removal, no prune):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Clean -RunId m6-b5a
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b5a/run-phase.ps1 -Phase Clean -RunId m6-b5b
docker image inspect --format '{{.Id}}' <each recorded build image ID>
```

- `m6-b5a`, 13:34:47 UTC: 13 resources removed (six containers, three networks,
  three volumes, the engine image); every project inventory empty. Its three
  build image IDs (`71f54cec…`, `5ee210d0…`, `a2e5d56e…`) answer `No such image`.
  `Clean.json` `7fa1e497…c44721`.
- `m6-b5b`, 14:23:05 UTC, after its evidence was recorded: 13 resources removed
  (six containers, three networks, three volumes, the engine image); every
  project inventory empty. Its build image ID (`5cfcf2c9…5b9ec51f`) answers
  `No such image`. `Clean.json` `f77b577c…9a21eb6`. OBSERVED at the same time:
  the B4 session's `asl-m6-m6-b4a-*` container, network, volume and image were
  present; they belong to that session and were not touched.

**Source review before the commit** (all exit 0):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b5b -Phase Snapshot
node .cache/m6/m6-b5b/compare-source.js source-003.json
git fetch origin
git diff --stat origin/main
git diff --check
```

- VERIFIED at 14:22:42 UTC (`source-003.json`) and again at 14:24:51 UTC
  (`source-004.json`): the 437 non-documentation files have the hashes
  recorded when image `5cfcf2c9…5b9ec51f` was built
  (`SourceEquivalence.json`); only documentation changed after that Build.
  `compare-source.js` is an authoring helper, not part of the repository.
- OBSERVED: `origin/main` still at `6e8fbb6` and no open pull request, so no
  merge of `main` was needed. Twenty tracked files changed and eight paths are
  new; `app/market_data/`, `app/accounting.py`, every M1–M5 migration, the
  agent runner, its egress gateway, `app/research/projections.py`, the web
  app, `pyproject.toml`, `uv.lock` and the Dockerfile are unchanged.

**Documentation link check** (the base image the repository pins; no network,
read-only root, the staged documentation as its only mount):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6/b0/stage-docs.ps1 -RunId m6-b5b
docker run --rm --network none --read-only --tmpfs /tmp --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true -e PYTHONDONTWRITEBYTECODE=1 -v <worktree>/.cache/m6/m6-b5b/<staged docs>:/repo:ro python:3.13.11-slim-bookworm python /repo/check_links.py /repo
```

- VERIFIED on the final documents: 86 Markdown files, 0 broken links, the four
  known historical Windows-path warnings of ExecPlan 0003.

**Delivery** (plain `git` and `gh`, no force, all exit 0):

```powershell
git add <the 36 B5 paths, each named>
git commit -F .cache/m6/m6-b5b/commit-message.txt
git push -u origin claude/m6-b5-source-registry
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head claude/m6-b5-source-registry --title "M6 B5: source registry, fetcher, evidence corpus, search and triggers" --body-file .cache/m6/m6-b5b/pr-body.md
gh pr view 24 --repo MentorAliu/adaptive_spot_lab --json number,url,state,isDraft,headRefOid,baseRefName,mergeable,createdAt
```

- OBSERVED: commit `3a44777750a7c2422fb49a6b7908ad7d48346d52` (36 files); the
  branch is new on `origin`; pull request
  [MentorAliu/adaptive_spot_lab#24](https://github.com/MentorAliu/adaptive_spot_lab/pull/24)
  opened at 14:26:22 UTC against `main`, state `OPEN`, `MERGEABLE`, no check
  run. It is **not merged**: the owner decides that. This record is a second,
  documentation-only commit on the same branch.

**Merge request** (21:22 UTC; OBSERVED owner instruction `merge it`,
[decision](../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b5-pr)).
Preflight, all exit 0:

```powershell
git fetch origin
git rev-parse origin/main HEAD origin/claude/m6-b5-source-registry
gh pr list --repo MentorAliu/adaptive_spot_lab --state all --limit 4 --json number,title,state,headRefName,headRefOid,baseRefName,mergeable,mergedAt,mergeCommit
```

- OBSERVED: `origin/main` at `6e8fbb6`; PR #24 `OPEN` and `MERGEABLE` at head
  `1b5dd558430ea4f4e1a5c117a875c9efa81db39b`, equal to the local branch; the
  B4 PR #25 `OPEN` and unmerged. No merge of `main` into the branch was needed
  and no phase input changed since the `m6-b5b` acceptance.

PROPOSED sequence, written before it runs: commit and push this
documentation-only record without force; read the PR's new head; merge with
`gh pr merge 24 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <that head>`
(no `--admin`, no `--delete-branch`); read the merged state. This file does not
claim the merge; GitHub records the merge commit, and the next checkpoint's
documents record it.

NOT RUN: GitHub CI (it does not start on this repository), every other §10
phase, any normal-app command, deployment, activation, a public endpoint and a
model call.

## M6 B3 checkpoint PR and merge (2026-10-04)

OBSERVED owner request: `create pr and merge it`, after verified local B3 commit
`85104b712847b76b5674fec633c6e1adccaa0453`. VERIFIED clean worktree and branch
`codex/m6-b3-research-runner`. Actual preflight commands:

```powershell
git ls-remote origin refs/heads/main refs/heads/codex/m6-b3-research-runner
gh pr list --repo MentorAliu/adaptive_spot_lab --head codex/m6-b3-research-runner --state all --json number,url,state,headRefOid,baseRefName
gh repo view MentorAliu/adaptive_spot_lab --json nameWithOwner,defaultBranchRef,viewerPermission,mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed
git diff --check bdeac4f91c13e25ca190320a6def53dcd43c0817..HEAD
```

All exited 0. Remote main is `bdeac4f91c13e25ca190320a6def53dcd43c0817`;
the B3 remote branch and PR do not yet exist. Merge commits are supported.
The GitHub connector returned 404 for the repository and 422 for PR search;
the configured authoring CLI successfully accessed both. No login was needed.

PROPOSED publication sequence: fetch main; commit this documentation-only
authorization record; push the codex branch without force; create the PR with
the retained `pr-body.md`; inspect its actual head, mergeability and checks;
merge using `--merge --match-head-commit <verified-head>`; verify the merged PR
and fast-forward local main. The PS5.1 authoring helper and native command/output
journal are under `.cache/m6/m6-b3b/publication/`. Its `Merged.json` and
`Synced.json` record actual completion; this paragraph does not claim an unrun
merge or passing CI. No admin bypass, branch deletion, application retest,
normal-app command, deployment or activation is part of publication.

ACTUAL publication (2026-10-04, 11:47 UTC). The Codex session reached its usage
limit before the commit step. OBSERVED owner instruction in a Claude Code
session: `create a pr on this branch`. It asks for the PR only, so the merge,
verify and sync steps were NOT RUN. The helper was not used either: that client
refused to run it, so `.cache/m6/m6-b3b/publication/` holds only `publish.ps1`
and `pr-body.md`, with no command journal, `pr-url.txt`, `Merged.json` or
`Synced.json`. Actual commands, all exit 0:

```bash
git diff --check
git diff --check bdeac4f..HEAD
git add -- docs/DECISIONS.md docs/STATUS.md docs/COMMANDS.md docs/plans/0023-m6-research-investigations.md
git commit -F -   # 4cd4979, "docs: authorize the M6 B3 checkpoint PR"
git push -u origin codex/m6-b3-research-runner
git ls-remote --heads origin refs/heads/codex/m6-b3-research-runner
gh pr create --repo MentorAliu/adaptive_spot_lab --base main --head codex/m6-b3-research-runner --title "Implement M6 B3 isolated research runner and holdout boundaries" --body-file <pr-body.md plus the client attribution line>
gh pr view 23 --repo MentorAliu/adaptive_spot_lab --json number,url,state,baseRefName,headRefName,headRefOid,mergeable,mergeStateStatus,changedFiles,additions,deletions
gh run list --repo MentorAliu/adaptive_spot_lab --limit 200 --json conclusion,createdAt,headBranch,event,headSha
```

VERIFIED: the remote branch head equalled local `4cd49792ddfb5ae91b81d7569ee77f41d6e9c0f0`
after the push. [PR #23](https://github.com/MentorAliu/adaptive_spot_lab/pull/23)
was OPEN against `main`, MERGEABLE with merge state CLEAN, at that head with 27
changed files. GitHub CI did not run: the push and pull_request runs for that
head (37199896402, 37199905037) ended in `startup_failure` after 0 s, as have all
189 runs in the repository since 2026-09-29, the account-level cause recorded in
[ExecPlan 0016 §8](plans/0016-ci-checks.md#8-progress-and-evidence). The local
B3 acceptance below is therefore the only automated evidence. No force push,
admin bypass, normal-app command, deployment or activation was run.

VERIFIED after this record was written, exit 0:
`docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo`.
86 Markdown files, zero broken links and the four known historical Windows-link
warnings; `--rm` removed the container.

Merge (2026-10-04, 11:53 UTC). OBSERVED owner instruction in the same Claude
Code session: `merge it`. VERIFIED before it: clean worktree, PR #23 OPEN and
MERGEABLE with merge state CLEAN, remote main still `bdeac4f`. PROPOSED sequence,
written before the merge and not a claim that it ran:

```bash
git push
gh pr merge 23 --repo MentorAliu/adaptive_spot_lab --merge --match-head-commit <pushed head>
gh pr view 23 --repo MentorAliu/adaptive_spot_lab --json state,mergeCommit,mergedAt
git fetch origin main:main
```

No force, admin bypass, branch deletion or change of the checked-out branch.
GitHub records the actual merge commit and time. The link check above was rerun
on this text with the same result.

ACTUAL merge, VERIFIED read-only on 2026-10-04 at 12:05 UTC from the B4 session
(the merge commands themselves were run in the earlier session and are not
re-run here). All exit 0:

```bash
gh pr view 23 --repo MentorAliu/adaptive_spot_lab --json number,state,mergedAt,mergeCommit,headRefOid,baseRefName,headRefName
git ls-remote origin refs/heads/main
git rev-parse main origin/main
git log -1 --format='%H %P %cI %s' 6e8fbb6
```

PR #23 is MERGED into `main` at 2026-10-04T11:55:03Z as merge commit
`6e8fbb60fa2b7fc18576a3d67b273c9d8d5968b6`, an ordinary two-parent merge of
`bdeac4f91c13e25ca190320a6def53dcd43c0817` and the PR head
`56d8031aafada7945ea01df68421d5178f3c32e4`. Remote `main`, local `main` and
`origin/main` all resolve to that commit. The source branch still exists.

## M6 B3 corrected-source acceptance (2026-10-04)

VERIFIED final-source runtime gates and exact-name cleanup. Final primary image:
`sha256:2585ef231eee7cfbe148bd406f9d8e27308d116307d9769fd070e91122c8bf28`.
Build passed four selected static/registry checks and Ruff. ResearchRunner
passed 15 catalog tests in 16.36 s and 17 runner tests in 63.31 s; HoldoutIsolation
passed nine tests in 3.78 s; Checks passed 145 tests in 6.90 s; M3/M4 Regression
passed 169 tests in 872.39 s. No tests were skipped. Regression emitted one
existing Starlette/httpx deprecation warning. Runtime bootstrap/credential/
network probes and standalone validation of only the new Compose blocks passed.

EngineParity passed all three scenarios, pilot fast/per-step comparisons and
the unchanged pre-interface native baseline. Final `research/out/parity/evidence.json`
SHA-256 (bound by `EngineParity.json`):
`4b557b88b79d8463eb2bc205bd30e49ed0e06dbfc9442587fce9f52829949374`.
The retained six-cell deterministic result has code identity
`69b27b1c298e1f54ae95ca340db0998ef6624092f69f72e884c71a2c7d801057` and portable
fingerprint `fca91e1d007880d0413331f2f3b30a6a7f1ea59926e94ee0c76583fd5c508858`.
Two actual executions returned identical documents/hashes. All cells honestly
report INSUFFICIENT_SAMPLE; this is synthetic mechanics evidence, not profit.

Fresh migration fixture `m6-b3c` used image
`sha256:9c348b16929a413edaeec271c26290c73ee975d5633a615b7364ffa00e3a80c7`.
Build/static/Ruff and all 19 schema tests passed (17.53 s, no skips, three
existing Alembic path-separator warnings). Populated upgrade/downgrade/reupgrade,
bounded locks, old-image fixture worker continuity, dump/restore, downgrade
refusal and accounting/M3/M4 invariants passed; reconciliation OK.
`Migration.json` SHA-256:
`ac3032529ca85fbf392fe514dae2ae19039e8b55bb1ff0b9ff48d8179386fa63`.
`SourceEquivalence.json` binds all 421 non-doc source hashes to the primary build;
`ImageEquivalence.json` proves identical RootFS layers and Config except Compose
labels. Distinct image IDs are preserved. The fresh fixture avoided overwriting
the intermediate migration's populated acceptance data/dumps.

Actual final-source commands (Windows PowerShell 5.1, process-only Bypass):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase ResearchRunner
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Regression
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase HoldoutIsolation
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3c -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3c -Phase Build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3c -Phase Migration
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3c/compare-images.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase EngineParity -BaselineRun m6-b2base
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Checks
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3c -Phase Clean
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/clean-completed-run.ps1
```

VERIFIED cleanup completed at 11:35 UTC inside its unchanged reserved window.
The final helper first runs `m6-b3b -Phase Clean -WaitForWindow`, then verifies
all recorded B3b/B3c image IDs are absent. Clean removed ten resources from
`m6-b3c` and thirteen from `m6-b3b`; the earlier `m6-b3a` removed four. All eight
project inventories per run are empty. Seven recorded build image IDs are
absent across all three runs; no global prune or normal-project command ran.
The historical-image probes return expected exit 1 with `No such image`, not a
gate failure. Native arrays, timeouts, stdout/stderr, phase JSON, source/image
identities and failed attempts remain in the three `.cache/m6/m6-b3*/` folders.
The completion-documentation Docker check passed at 11:38 UTC: 86 Markdown
files, zero broken links and four historical Windows-link warnings. Its
network-disabled, read-only container mounts staged Markdown only and removes
itself on exit. Source review verifies all 421 non-doc hashes match the build,
protected source and prior Compose blocks are unchanged, and PS5.1/ASCII and
`git diff --check` pass.

Actual authoring/documentation commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/review-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/verify-delivery-scripts.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/b3-docs.ps1
```

Delivery procedure (the native receipt records the executed commands/results):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/commit-b3.ps1
```

The final documentation check is repeated after this result record; its first
pass is retained as `Docs-completion-initial.json`. Local delivery requires all
runtime/cleanup/documentation gates, an exact 26-file staged allowlist and a
clean final worktree, and retains `Delivery.json` plus `delivery.jsonl`.
NOT RUN: GitHub CI, B4 onward/full M6-A, normal deployment/activation and
publication. No further B3 owner decision is pending.

### Intermediate acceptance and correction history

At 11:03 UTC source review found a code-identity gap across a worker image
replacement. IMPLEMENTED a fresh execution-time identity check, plus a test
that accepts a durable job under a prior identity and then proves the current
worker refuses it before reset/replay. The queued Regression process was
canceled before any Docker call (session 31787, exit 1); its cancellation record
is `pre-execution-code-regression-cancel.json`. The passing records described
below were archived as `pre-execution-code-*`; they are not acceptance of this
new correction. Build was queued with `-WaitForWindow` for HH:07, followed by
the final-source gates recorded above.

OBSERVED owner continuation: `Don't stop until b3 is completed`. This authorizes
the grant-order correction and continued in-scope verification, retaining the
original B3 boundaries. Fresh run `m6-b3b` uses only its eight manifest fixture
projects. No normal project, original credentials, model call or public endpoint
is addressed. All script invocations use Windows PowerShell 5.1 and process-only
ExecutionPolicy Bypass; the full native argument arrays and outputs are in
`.cache/m6/m6-b3b/commands.jsonl` and timestamped files.

Actual commands, in sequence (some phases were rerun as explained below):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase ResearchRunner
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase HoldoutIsolation
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Checks
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Regression
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Stop
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase ResearchRunner
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase HoldoutIsolation
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Migration
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase EngineParity -BaselineRun m6-b2base
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3b/review-source.ps1
```

IMPLEMENTED review corrections: the new epoch-lock function grant now follows
role creation; sealed-range and actual mid-replay deadline cases were added;
the daily budget explicitly uses UTC midnight, tested with Pacific/Kiritimati
as the database session zone. The pre-UTC Regression was deliberately stopped
at 10:30 UTC (exit 137, no timeout or assertion failure). Its phase record is
`pre-utc-Regression.json`; earlier Build, runner, holdout, Checks and source
review records and the deterministic document are retained under `initial-*`,
`configuration-*` and `pre-utc-*`, without relabeling their results.

Recorded B3b image IDs, in build order:

- `sha256:59c7181298832001c6c39dc33376b7924cc2996d1956e52f6c8ac4c12d52bfc7`
- `sha256:8f9a68d8c7e75d16014b7162ccaec558248fbfe9967eb9c0eb088f928fcc35e1`
- Intermediate corrected source: `sha256:95b0b8d11156a05b55db06fb7743ff8b964f1fe0bf3c7de673b27479c5bb818b`
- Final source: `sha256:2585ef231eee7cfbe148bd406f9d8e27308d116307d9769fd070e91122c8bf28`

VERIFIED on the intermediate image at that checkpoint:

- Build: four selected static/registry checks and Ruff. `Build-b3.json` is
  explicitly PARTIAL for full M6 because later-batch service images are excluded.
- ResearchRunner: 15 catalog tests in 16.40 s and 16 runner tests in 60.13 s;
  no skips. Runtime-shaped bootstrap and the isolation probe passed. The actual
  three new Compose blocks were rendered only in a standalone fixture config,
  with fresh fixture paths; the normal project was never rendered.
- HoldoutIsolation: all nine tests passed without skips.
- Migration: all 19 schema tests passed in 18.25 s (three existing Alembic
  path-separator warnings). Populated upgrade/downgrade/reupgrade, bounded lock
  retries, old-image fixture worker continuity, dump/restore, non-fixture
  downgrade refusal and accounting/M3/M4 invariants passed; reconciliation OK.
  `Migration.json` SHA-256 is `15939feb99e6622c478858abe3ab3fa1bfb2f7f2c5cb77764c1184a301fa2d6e`.
- Authoring review: all 421 non-doc files matched that Build snapshot;
  protected source and every existing Compose block are unchanged. The three
  changed harness files pass ASCII/PS5.1 parsing; `git diff --check` passes.
- EngineParity: all three gapped-stop, quiet and pilot-lifecycle financial and
  per-bar comparisons passed; pilot fast/per-step checks passed and the
  pre-interface native baseline is unchanged. Parity evidence SHA-256:
  `a94c6d153a0e25c44d9fcc25242b59c0326250d93ad29ce59efdfa74b9323efe`.
- Corrected-source Checks: all 145 tests passed in 6.31 s, no skips. Existing
  Checks/Regression JSON labels retain `B2_ONLY` / `b2_result` because they run
  that suite on this B3 image; PARTIAL does not claim full M6 acceptance.

The retained intermediate synthetic deterministic result has code identity
`dafbf96d6017c1b469bb9327616022f09e56e98ffa4c48536339941b468c0c54` and portable
fingerprint `fca91e1d007880d0413331f2f3b30a6a7f1ea59926e94ee0c76583fd5c508858`.
Both executions produced the same document/hash across all six partition/cost
cells; each cell honestly reports INSUFFICIENT_SAMPLE. This verifies replay
mechanics, not returns or profitability.

Regression was queued with the following actual command. Its existing
25-minute reservation deferred execution until 11:07 UTC; no heavy work ran in
the protected interval.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Checks
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3b -Phase Regression -WaitForWindow
```

This queued Regression was subsequently canceled before start for the
execution-time identity correction noted above. At that checkpoint final-source
gates, documentation review, cleanup and local commit were pending; B3 was not
complete. The final-source record above supersedes this intermediate result.

## M6 B3 first acceptance attempt (2026-10-04)

OBSERVED start: clean `main` and `origin/main` at
`bdeac4f91c13e25ca190320a6def53dcd43c0817`; created
`codex/m6-b3-research-runner`. All Docker commands below select standalone
`asl-m6-m6-b3a-*` fixture projects, fresh fixture credentials and internal
networks. No normal-project command or owner secret read ran.

Actual Windows PowerShell 5.1 commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3a -Phase Prepare
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3a/authoring-build.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3a -Phase Build
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b3a -Phase ResearchRunner
```

VERIFIED Prepare and source snapshot. The first authoring build was blocked by
the filesystem/Docker-pipe sandbox before building (exit 1); the same reviewed
script succeeded with host Docker access. The staged Ruff authoring formatter
completed. That is distinct from the subsequent acceptance Build: image
`sha256:017399cfd3d102bd76b9b851351ea3e3b396c57571065c7e4a00776e1b3b9bb6`,
four static tests passed (75 deselected, 1.81 s), Ruff passed, fixture stop passed.
Full M6 Build remains partial because later service images are outside B3.

FAILED ResearchRunner at 10:09 UTC before its catalog tests. PostgreSQL reported
`role "asl_research" does not exist` for the new function grant in migration
0008; that role is created later in the same migration. Both fixture targets
stopped successfully. At that point the proposed correction was to move the
grant after role creation; no correction or rerun had been made. The owner's
original required-gate stop rule required approval first. The subsequent
continuation and verified correction are recorded in the preceding section.

Evidence: `.cache/m6/m6-b3a/{manifest.json,source-001.json,Build-b3.json,ResearchRunner.json,commands.jsonl}`
and timestamped stdout/stderr files. The native journal includes failed commands
as well as successful commands. The earlier authoring image is recorded as
`sha256:0767305b663fbf04a213ef1fc9cbe198c88a861693cb8ec36feedab1d801bbd0`.
At this first-attempt checkpoint, HoldoutIsolation, Checks, Regression,
EngineParity and Migration on the B3 source, completion-documentation checks
and local commit were NOT RUN. No B3 or M6-A acceptance was claimed. Earlier
B1/B2 results remain historical, and GitHub CI is not a pass.

Actual cleanup command, after the evidence above was retained:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b3a/clean-failed-run.ps1
```

VERIFIED at 10:15 UTC: its harness `Clean -WaitForWindow` removed four exact-name
resources (fixture container, network, volume and final image). Every manifest
project inventory is empty. The replaced authoring image was already absent;
its exact-ID absence check passed. `Clean.json`, its hashed inventory,
`Clean-historical-image.json` and the native journal retain the results.

## Status

The historical M0 commands below were run from the repository root in Windows PowerShell on 2026-09-26. M1 commands and actual results are recorded after the M0 section. M2 and M3 isolated commands/results are recorded below; M4 and later milestone commands remain **PROPOSED**. The original pack had no executable application.

## Environment inspection and bootstrap

Docker 29.7.2, Compose v5.5.1, Node 24.19.0, host pnpm 11.19.0, and uv 0.12.5 were observed. Application builds and tests run in pinned Docker tooling images. Host Python is not required.

M0 used [tools/bootstrap/Dockerfile](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/tools/bootstrap/Dockerfile), independent of application manifests, to run the exact [START_HERE.md](pack-2.0.0/START_HERE.md) shadcn command in a verified empty temporary directory. The official shadcn skill was installed and read in the active authoring client. This bootstrap image is an authoring tool, not a runtime service.

## Implemented M0 service conventions

Root [Compose](../../compose.yaml) runs only `web`, `api`, `postgres`, and one-shot `migrate`. `web-tools` and `engine-tools` use the `tools` profile; `engine-tests` and `browser-tests` use `test`. `worker`, `agent-runner`, and `research-worker` have no executable or credentials through M1. The normal web service now publishes only `127.0.0.1:3000`; API and PostgreSQL have no host ports. [tools/compose-test.ps1](https://github.com/MentorAliu/adaptive_spot_lab/blob/cf6360d/tools/compose-test.ps1) selects a separate Compose project, volume, subnets, and loopback port 4318. On hosts where the documented default subnets conflict, set `ASL_FRONTEND_SUBNET` and `ASL_PRIVATE_SUBNET` before normal Compose commands; edit the test helper's subnet values before starting its stack.

Normal stack, from repository root:

```powershell
& ./tools/setup-local.ps1
docker compose config --quiet
docker compose build
docker compose up -d
docker compose ps --all
# Open http://127.0.0.1:3000/
docker compose down
```

`setup-local.ps1` creates ignored random local Docker secrets only when absent. `down` stops services without deleting the PostgreSQL volume. Do not use `down -v` as routine cleanup. The default Docker subnet pool was exhausted on the measured host; the explicit project subnets in Compose allowed clean startup without altering unrelated Docker networks. Read logs with `docker compose logs --tail=100 api migrate web`; never print secret contents.

Checks verified with exit 0 on 2026-09-26:

```powershell
docker compose --profile tools build web-tools engine-tools
docker compose --profile tools run --rm web-tools pnpm --filter web lint
docker compose --profile tools run --rm web-tools pnpm --filter web typecheck
docker compose --profile tools run --rm web-tools pnpm --filter web test:unit
docker compose --profile tools run --rm web-tools pnpm --filter web api:check
docker compose --profile tools run --rm web-tools pnpm --filter web build
docker compose --profile tools run --rm engine-tools uv run --frozen ruff check .
docker compose --profile tools run --rm engine-tools uv run --frozen python -m app.export_openapi --check
```

Frontend unit tests: 4 passed; Ruff: all checks passed; generated API types and FastAPI OpenAPI schema matched; the production build emitted `.output/server/index.mjs`. Rolldown emitted nonfatal dependency `"use client"` directive warnings. After exact manifest pinning, a fresh `pnpm install --frozen-lockfile` in `web-tools` succeeded with unchanged resolved versions.

On 2026-09-27, the Query ESLint follow-up added an exact-pinned development dependency using the pnpm 10.28.2 Docker authoring image with `pnpm add -D @tanstack/eslint-plugin-query@5.104.0 --save-exact --lockfile-only` from `apps/web`. The following repository-root checks each exited 0 after a fresh frozen-install tooling image build:

```powershell
docker compose --profile tools build web-tools
docker compose --profile tools run --rm web-tools pnpm --filter web lint
docker compose --profile tools run --rm web-tools pnpm --filter web exec eslint --print-config src/system/status.query.ts
docker compose --profile tools run --rm web-tools pnpm --filter web typecheck
docker compose --profile tools run --rm web-tools pnpm --filter web test:unit
docker compose --profile tools run --rm web-tools pnpm --filter web build
```

The effective ESLint config enabled seven recommended Query rules; four frontend unit tests passed. The build again emitted nonfatal dependency `"use client"` warnings. An additional `docker compose --profile tools run --rm web-tools pnpm --filter web check` exited 1 because Prettier reported 11 unchanged files outside this follow-up; the targeted `docker compose --profile tools run --rm web-tools pnpm --filter web exec prettier --check eslint.config.js` exited 0. No browser behavior changed, and browser tests were not rerun for this lint-only update.

The 2026-09-27 Query options/cancellation follow-up ran these commands from the repository root with exit 0:

```powershell
docker compose --profile tools build web-tools
docker compose --profile tools run --rm web-tools pnpm --filter web typecheck
docker compose --profile tools run --rm web-tools pnpm --filter web lint
docker compose --profile tools run --rm web-tools pnpm --filter web test:unit
docker compose --profile tools run --rm web-tools pnpm --filter web exec prettier --check src/system/status.query.ts
docker compose --profile tools run --rm web-tools pnpm --filter web build
& ./tools/compose-test.ps1 up -d --build
& ./tools/compose-test.ps1 --profile test build browser-tests
& ./tools/compose-test.ps1 --profile test run --rm browser-tests
& ./tools/compose-test.ps1 down
```

Four frontend unit tests and two normal Chromium tests passed. The database-outage Chromium case was skipped because this run did not set `PLAYWRIGHT_EXPECT_ERROR=1`; no backend tests were rerun. The isolated stack was stopped without deleting its named volume. The production build retained nonfatal dependency `"use client"` directive warnings. See [INTEGRATION_EVIDENCE.md](../INTEGRATION_EVIDENCE.md) for the signal boundary and `select` rationale.

The 2026-09-27 built-in Query defaults follow-up removed the `QueryClient` override and ran these commands from the repository root with exit 0:

```powershell
docker compose --profile tools build web-tools
docker compose --profile tools run --rm web-tools pnpm --filter web lint
docker compose --profile tools run --rm web-tools pnpm --filter web typecheck
docker compose --profile tools run --rm web-tools pnpm --filter web test:unit
docker compose --profile tools run --rm web-tools pnpm --filter web exec prettier --check src/system/query-client.ts
docker compose --profile tools run --rm web-tools pnpm --filter web build
& ./tools/compose-test.ps1 up -d --build
& ./tools/compose-test.ps1 --profile test build browser-tests
& ./tools/compose-test.ps1 --profile test run --rm browser-tests
& ./tools/compose-test.ps1 stop postgres
& ./tools/compose-test.ps1 --profile test run --no-deps --rm -e PLAYWRIGHT_EXPECT_ERROR=1 browser-tests pnpm --filter web test:e2e --grep 'database outage'
& ./tools/compose-test.ps1 start postgres
& ./tools/compose-test.ps1 down
```

Four frontend unit tests, two normal Chromium cases, and the database-outage Chromium case passed. The production build completed with the previously observed nonfatal dependency `"use client"` warnings. The isolated database volume was preserved; backend tests were not rerun for this frontend-only change.

Isolated integration and browser checks:

```powershell
& ./tools/compose-test.ps1 up -d
& ./tools/compose-test.ps1 --profile test build engine-tests browser-tests
& ./tools/compose-test.ps1 --profile test run --rm engine-tests
& ./tools/compose-test.ps1 --profile test run --rm browser-tests
& ./tools/compose-test.ps1 stop postgres
& ./tools/compose-test.ps1 --profile test run --no-deps --rm -e PLAYWRIGHT_EXPECT_ERROR=1 browser-tests pnpm --filter web test:e2e --grep 'database outage'
& ./tools/compose-test.ps1 start postgres
& ./tools/compose-test.ps1 down
```

The backend suite passed 5 tests including a real migrated PostgreSQL revision check. Chromium passed 2 normal browser cases (SSR HTML, hydration/navigation, 390-pixel layout); its outage case passed when only the isolated test database was stopped. During that outage, private API liveness stayed HTTP 200, readiness returned HTTP 503, and the page displayed its error state. Restart restored readiness HTTP 200 and the empty overview. The backend test client emitted a Starlette `httpx` deprecation warning; no test failed.

## M1 verified isolated commands — 2026-09-27

All M1 mutation tests used ignored, randomly generated task secrets under `secrets/m1-0927a` or `secrets/m1-browser-0927b`. The PowerShell environment selected distinct Compose projects, PostgreSQL names, volumes, loopback ports and nonoverlapping subnets. The normal `adaptive-spot-lab` Compose database and owner account were never initialized or top-upped as a test.

For the engine suite, the verified PowerShell environment was:

```powershell
$env:ASL_SECRET_DIR='./secrets/m1-0927a'
$env:ASL_DB_NAME='asl_m1_0927a'
$env:ASL_TEST_ISOLATED='1'
$env:ASL_FRONTEND_SUBNET='10.241.28.0/27'
$env:ASL_PRIVATE_SUBNET='10.241.28.32/27'
$env:WEB_PORT='4329'
docker compose -p asl-m1-0927a --profile test run --rm engine-tests
```

The final actual migrated PostgreSQL suite passed **15 tests**. It covers idempotency and conflicting reuse, same/distinct-key initialization races, distinct-key top-up version races, pending retry/cancel races, reservations/fencing, rollback of unbalanced journals, discrepancy latching, high-water/pause preservation, owner authorization/session rotation, redacted correlation logging and oversized request rejection. The property test uses 100 Hypothesis examples. A Starlette TestClient `httpx` deprecation warning remained nonfatal.

OpenAPI was regenerated in isolated `engine-tools` with the engine directory mounted at `/out`; TypeScript types were regenerated in isolated `web-tools` with only the schema file and generated directory mounted. Final `app.export_openapi --check`, `api:check`, Ruff, web lint, typecheck, targeted Prettier check and production build exited 0; six web unit tests passed. Typecheck initially failed because its Docker image predated the regenerated types and was rebuilt. Ruff initially found a single Alembic import-order issue and the first targeted Prettier check found 14 changed files; both were fixed before the final pass. The production build retained nonfatal third-party Rolldown `"use client"` warnings. These intermediate failures are not passes.

For browser acceptance, the final fresh environment was:

```powershell
$env:ASL_SECRET_DIR='./secrets/m1-browser-0927b'
$env:ASL_DB_NAME='asl_m1_browser_0927b'
$env:ASL_TEST_ISOLATED='1'
$env:ASL_FRONTEND_SUBNET='10.241.28.128/27'
$env:ASL_PRIVATE_SUBNET='10.241.28.160/27'
$env:WEB_PORT='4331'
docker compose -p asl-m1-browser-0927b --profile test up -d postgres api web
docker compose -p asl-m1-browser-0927b --profile test run --rm browser-tests
docker compose -p asl-m1-browser-0927b stop postgres
docker compose -p asl-m1-browser-0927b --profile test run --no-deps --rm -e PLAYWRIGHT_EXPECT_ERROR=1 browser-tests pnpm --filter web test:e2e --grep 'database outage'
docker compose -p asl-m1-browser-0927b start postgres
docker compose -p asl-m1-browser-0927b --profile test run --rm browser-tests node scripts/measure-ssr.mjs
```

Three normal Chromium cases passed with expected skips for outage and fixture-gated pending/unknown cases; the separate outage, pending/cancel and lost-response/key-lookup cases each passed. The fresh normal suite exercised one-time owner setup, 10,000 virtual USDT initialization, 2,200 top-up, invalid amount, sign-out/expired session, Host/Origin rejection, accessibility-tree heading, measured text contrast, keyboard dialog dismissal, server rendering and 390-pixel layout. Synthetic pending and lost-response cases used only a disposable account. The warm isolated SSR workload was 30 sequential unauthenticated requests: median 11.9 ms, p95 14.5 ms, max 61.4 ms, under the predeclared 1,500 ms p95 budget. This measures the local Docker host only, not Core Web Vitals.

For the pending fixture, `docker compose -p asl-m1-browser-0927b exec -T postgres psql -U asl -d asl_m1_browser_0927b` set `valuation_valid=false` only on that disposable account; `docker compose -p asl-m1-browser-0927b --profile test run --rm -e PLAYWRIGHT_PENDING_FIXTURE=1 browser-tests pnpm --filter web test:e2e --grep 'invalid valuation keeps'` passed, and the synthetic flag was restored to true. The corresponding `PLAYWRIGHT_UNKNOWN_FIXTURE=1` run with `--grep 'lost confirmation response'` passed after Playwright delivered the top-up to the server but dropped the browser response; lookup found the posted request and 12,233 virtual USDT. Neither fixture reflects a live market mark.

The isolated backup/restart rehearsal used `docker compose -p asl-m1-browser-0927b exec -T postgres` with `pg_dump -U asl -d asl_m1_browser_0927b -Fc -f /tmp/asl_m1_browser_0927b.dump`, `createdb -U asl asl_m1_restore_0927b`, and `pg_restore -U asl -d asl_m1_restore_0927b /tmp/asl_m1_browser_0927b.dump`. The dump SHA-256 was `9c9f02fd734dc8da4c58957f3ceadb4b03c6210b564d8394a7a1da4e767ff6d9`. Source and restore SQL comparisons matched on cash/contributions 12,200.00000000, 122 units, NAV/high-water 100, two requests, two journal transactions, four postings and `reconciliation_failed=false`. Engine reconciliation on the restored database returned `OK`, cash 12,200.00000000 and reserved zero. Restarting only the disposable API left those totals unchanged and readiness HTTP 200. The temporary dump was inside the disposable PostgreSQL container; a real operator backup must be stored safely outside its volume.

A separate disposable database `asl_m1_migration_0927b` was explicitly migrated first to `0001_foundation`, then inspected: `system_metadata` existed and `account_state` did not. `alembic upgrade head` then applied only `0002_m1_account`; final inspection showed both tables, revision `0002_m1_account` and an unfunded account. Both Alembic commands exited 0. The normal owner database was untouched.

For normal local startup after delivery, run `./tools/setup-local.ps1`, `docker compose config --quiet`, `docker compose build`, then `docker compose up -d` from the repository root. Browse `http://127.0.0.1:3000/`. Read the one-time setup key from the ignored local `secrets/owner_setup_key` file, choose a passphrase, then review and confirm initialization **only when you intend to create that virtual account**. Do not run the isolated test commands against the normal project or reuse the test database name for owner data.

## Additional command requirements

M0 implemented reproducible OpenAPI generation/check and one-shot Alembic migration. `& ./tools/generate-api.ps1` was run successfully: it used limited authoring bind mounts for the engine output directory, schema input and generated TypeScript directory, then regenerated `services/engine/openapi.json` and `apps/web/src/generated/api.ts`. Review the diff after any deliberate API change and rerun both drift checks above. M1 adds reconciliation and the isolated backup/restore rehearsal above. Dataset import, replay and experiment export remain **PROPOSED** for later milestones.

Runtime Codex login/job invocation is covered in [RUNTIME_AGENTS.md](RUNTIME_AGENTS.md). It needs an explicit owner-controlled authentication procedure, effective tool-profile validation and no real market/API spending during routine offline tests.

## Completion reports

For each milestone record command, working directory/container, actual exit status, meaningful output/evidence and limitations. “Not run: Docker unavailable” is an acceptable honest result but does not pass a Docker acceptance gate. A successful documentation check is not a substitute for a browser, integration or market-data test.

## M2 isolated command record — 2026-09-27 (acceptance in progress)

All commands below ran from `C:\Users\owner\repos\adaptive-spot-lab` in Windows PowerShell and launched application/runtime/build/test tools only inside Docker. The wrapper's ignored `.cache/m2/<run-id>/manifest.json` records resolved project/database/secret/port/subnet identities; phase logs retain resolved Docker commands and output. No command targeted the normal Compose project or owner database.

```powershell
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Prepare
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase Build
& ./tools/m2-acceptance.ps1 -RunId m2-20260927a -Phase PublicSmoke
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Prepare
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Build
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Checks
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Regression
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Recovery
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase RecoveryCheck
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Performance -ProbeSeconds 10
```

The `a` public smoke passed for both symbols, REST candles and stream types; a separate invocation with `ASL_SMOKE_HOURLY=1` observed both finalized 1h closes at 17:00 UTC (1,895.877 seconds). A later final-code quick public smoke on `c` passed in 5.454 seconds after correcting the documented `permissionSets` schema; an earlier `c` smoke failed at the legacy permission interpretation and is retained in the same log. The isolated `c` PostgreSQL regression passed **36 tests** after stream batching, with one Starlette dependency deprecation warning. M1→M2 migration fingerprints, M2 dump/restore fingerprints and reconciliation passed on the recovery project; its first immediate API readiness probe raced startup, and `RecoveryCheck` with `up --wait` passed. The original 10-second burst probe published 1,000/1,000 events but accumulated 5.081 seconds of schedule lag. The revised bounded-batching probe published 1,000/1,000, p95 receipt-to-publication 55.467 ms and p99 schedule lag 2.07 ms; these short probes do not pass the declared full-duration Q06 workload. Full final checks, fresh browser, long performance and targeted fault/security/accessibility evidence are recorded as open in [ExecPlan 0003](plans/0003-market-data-charts.md).

The final `c` quick public smoke's first stream frames measured source-event-to-local-receipt delays of 116.214–118.403 ms across the two quote and two candle examples. These are four point-in-time provider/network samples, not a latency distribution or local publication timing. The separate synthetic ingestion workload measures receipt-to-publication and excludes provider/network time.

Subsequent isolated verification added transport/concurrency and API-denial cases: the final `c` PostgreSQL regression passed **42 tests** with one Starlette deprecation warning, including a 429/`Retry-After` case and 401 denials for all four market reads without both service and owner identities. The final `c` frozen Checks passed on the current code after correcting Ruff import order, TypeScript types, ESLint type imports and Prettier formatting: web lint, typecheck, unit, generated API drift, Ruff, OpenAPI drift, format check and production build. The build emitted the previously observed nonfatal third-party `"use client"` bundler warnings. Intermediate failed checks remain in the append-only ignored phase logs and are not counted as passes.

Actual additional wrapper invocations (each phase logs its resolved Docker commands in `.cache/m2/<run-id>/`):

```powershell
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Build
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Checks
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Regression
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PerformanceApi
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase Performance
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PerformanceBurst
& ./tools/m2-acceptance.ps1 -RunId m2-20260927d -Phase Browser
& ./tools/m2-acceptance.ps1 -RunId m2-20260927d -Phase BrowserMarket
& ./tools/m2-acceptance.ps1 -RunId m2-20260927d -Phase BrowserPerformance
& ./tools/m2-acceptance.ps1 -RunId m2-20260927d -Phase BrowserError
& ./tools/m2-acceptance.ps1 -RunId m2-20260927d -Phase PerformanceRetention
& ./tools/m2-acceptance.ps1 -RunId m2-20260927e -Phase Prepare
& ./tools/m2-acceptance.ps1 -RunId m2-20260927e -Phase Build
& ./tools/m2-acceptance.ps1 -RunId m2-20260927e -Phase BrowserEmpty
```

`m2-20260927d` Browser and BrowserMarket passed the existing M1 normal journey plus M2 synthetic live, worker-unavailable and recovered states, including provisional candle updates, 390-pixel layout, keyboard symbol selection, accessibility-tree heading/table and measured heading contrast. BrowserPerformance passed 30 symbol switches and 50 chart mount/unmount cycles at each desktop/mobile viewport: chart visible 265/266 ms, switch p95 144/146 ms, warm SSR p95 114/79 ms, lab LCP 148/156 ms and CLS 0. BrowserError subsequently passed after a failed refresh showed an error and treated the cached quote as unusable; the same test observed recovery when requests resumed. The earlier BrowserError attempts failed because the test intercepted GET or the wrong URL pattern; the trace showed actual `/_serverFn/...` POST transport, and the harness was corrected. `m2-20260927e` BrowserEmpty passed in a fresh database with no collection worker: disabled status, no quote/candle/chart, and desktop/mobile screenshots. These are fixture and browser observations, not live-worker evidence or a manual screen-reader pass.

`c` PerformanceApi passed 100 authenticated in-process sequential reads (p95 11.615 ms) and 100 five-way reads (p95 57.465 ms, p99 62.669 ms). `d` PerformanceRetention passed a seven-day **five-minute sampled** replay: 4,032 quotes and 336 finalized candles, 594 logically pruned records, a preserved pin, zero broken payload references and a deletion manifest. WAL grew 5,023,208 bytes; relation bytes were 188,416 before seeding, 3,121,152 after seeding and 3,137,536 after pruning. PostgreSQL did not immediately reclaim physical space. The separate `c` 60-minute synthetic normal run passed 10,800/10,800 publications in 3,599.045 seconds with receipt-to-publication p50/p95/p99 39.893/60.300/79.613 ms, p99 schedule lag 3.042 ms, maximum process RSS 66,984 KiB and 12,599,296 bytes added to market relations. Its following five-minute burst passed 30,000/30,000 in 299.967 seconds with p50/p95/p99 52.145/65.449/77.298 ms, p99 schedule lag 2.058 ms, maximum RSS 67,032 KiB and 26,394,624 bytes of market-relation growth. A separate final-image five-minute burst passed 30,000/30,000 with p95/p99 70.711/83.359 ms and recovered one deliberately persisted-but-unpublished observation after 2.049 seconds without making it visible early. These are isolated synthetic receipt-to-publication timings, not public-feed latency or seven-day full-density storage evidence.

The explicitly invoked `c` `PublicWorkerStart` built and started only its public project. Initial `PublicWorkerReport` found 1,440 public historical finalized candles, provisional stream candles, live ticker snapshots, two eligible instruments, both feeds `CONNECTED`, and 1,454 published observations. After the first reference refresh, publications rose to 1,662 with no feed error. Docker inspection showed one read-only market password mount, private plus market-egress networks, a read-only nonprivileged container, 1 CPU/512 MiB/128 PID limits, no binds and no host-published port. `PublicWorkerDbStop` stopped only that project's PostgreSQL for 12 seconds; `PublicWorkerDbStart` restored it. The worker failed visibly during the outage, Docker supervised four short restarts, then acquired lease epoch 2 (from 1), rechecked references, reconnected the stream and returned both feeds to `CONNECTED` with 1,813 publications. `PublicWorkerStop` ended public collection. A value-only scan of the five generated public-project secret files against all task `.log` files found no secret value. This is a bounded point-in-time integration check, not owner-stack activation or long-run provider reliability evidence.

Actual public-worker and fault commands:

```powershell
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerStart
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerReport
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerDbStop
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerDbStart
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerReport
& ./tools/m2-acceptance.ps1 -RunId m2-20260927c -Phase PublicWorkerStop
```

`m2-20260927b` preparation encountered an isolated subnet collision before the wrapper inspected existing Docker network ranges; the selector was fixed, and run `c` prepared successfully. No normal-stack resource was changed. The manifest-owned `Stop` phase completed with exit 0 for runs `a`, `b`, `d` and `e`, then for run `c` after public collection ended. A final `docker ps --format '{{.Names}}' --filter 'name=asl-m2'` returned no running M2 containers. Compose containers and task networks were removed; named volumes, ignored `.cache/m2/<run-id>/` manifests and logs were retained for recovery and evidence. No normal-stack service was stopped.

## M2 completion commands — 2026-09-27

The completion runs are named `m2-completion-0927a` through `m2-completion-0927f`, distinct from the initial M2 runs above. Runs `e` and `f` each have fresh engine, browser, recovery, performance, public, retention, capacity and `recoverym2` projects. Exact expanded commands, UTC times and exit results are appended to `.cache/m2/<run-id>/<phase-label>.log`; failed attempts remain retained. The detailed [completion record](plans/0003-market-data-charts.md#7-completion-run-record--2026-09-27) owns measurements, failures and gate status.

Executed from this repository in Windows PowerShell, with Docker Desktop access:

```powershell
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Prepare
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Build
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Checks
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Regression
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Recovery
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase RecoveryM2
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PerformanceFullRetention
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PinnedExhaustion
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Performance
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Browser
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase BrowserMarket
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase BrowserRaces
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase BrowserAccessibility
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase BrowserError
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase BrowserPerformance
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PublicWorkerStart
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PublicWorkerNetworkInterrupt
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PublicWorkerReport
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase PublicWorkerStop
./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Snapshot
```

The final `Performance` invocation completed its real elapsed 60-minute normal run, five-minute 100-event/second burst and API measurement, all exit 0 at 22:11 UTC. The normal run's successful path matches final source; its failure-log-only image difference is explicitly documented with AST comparison evidence. The storage phases use labeled synthetic accelerated fixtures, fixed production record shapes/caps and real retention/stop paths. `PinnedExhaustion` refuses to start without its host/Docker free-space preflight. `RecoveryM2` and `Recovery` wait for PostgreSQL health before their predecessor migrations. `BrowserEmpty` must use a separate fresh browser database; the harness prevents mixing its passphrase/state with the normal owner journey.

The initial final-browser suite in `e` passed. Subsequent screenshot review corrected incidents/storage loading. The affected final-source checks were executed in `c` to preserve the `e` manual-review session: `Build`, `Checks`, `BrowserMarket`, `BrowserRaces`, `BrowserAccessibility`, `BrowserError`, `BrowserPerformance`, `BrowserStates`, `Snapshot`. All returned exit 0. `BrowserStates` mutates synthetic health/history responses to verify queue warning/overload/unknown/recovery and unresolved interval presentation; it is independent of the real worker/store fault tests. The empty-feed case passed in `d`. A separate `d` public smoke with `ASL_SMOKE_HOURLY=1` observed both finalized bars at 21:00 UTC with the unchanged final parser/provider source.

Final backend follow-up in `f` ran `Build`, `Checks`, `WorkerFaults`, `Regression`, `RecoveryMemory`, `Recovery`, `RecoveryM2` and `Snapshot`, all exit 0 after the recorded fixes. This includes nonempty completion-table restore evidence and 19 targeted/62 total backend tests. Final public-worker interruption was repeated in `e`, with `PublicWorkerStop` in `finally`; the final `f` public smoke used `ASL_SMOKE_HOURLY=1` and observed both closes at 22:00 UTC. Final read-only isolation inspection and backup-preservation commands are retained in the run artifacts.

`Snapshot` creates source hashes and exact image IDs without reading secret values. `narrator-build.json` additionally records the actual running web/API/fixture image IDs, review URL and bound source-manifest hash. The final backend rebind at 22:04:36 UTC preserved the database, owner session and verified web image. The [manual checklist](m2-narrator-review.md) contains the commands needed to stop/restart that disposable synthetic feed for review. Do not run automated owner sign-ins against the review project while the owner is using it.

The final security inspection used read-only Docker inspection, public-asset marker scanning and value-only secret comparisons against task logs. It did not print secrets or use a real exchange credential. Initial cleanup invoked `Stop` for runs `a`, `b`, `c`, `d`, `f` and manifest-scoped `down --remove-orphans` for every `e` target except `browser`. All exited 0 at 22:14 UTC; named volumes, backup archives and local evidence remain. Inventory found an earlier `b` public collector still active; its stop/exit and retained log are disclosed in the completion record. The four `e` browser-review containers were retained for manual review.

On 2026-09-28 the owner reported all Narrator checks passed and identified Chrome. The final running image binding was reverified at 04:00:28 UTC; all 146 application/tool files matched the tested source manifest. Browser version and Narrator voice were not supplied. `git fetch origin main`, remote identity and ancestry checks passed: local and remote `main` both resolved to `434bc98a7b393d023e4351f0bc38b974109d44cf`, with zero divergence. No application behavior changed after the recorded tests; only review/delivery documentation changed.

`git commit -m 'Complete M2 market-data acceptance'` created implementation commit `4cfb8a4e0ba662cec0a9d8fbcc22f712b8c87ff2`. `git push origin main:main` exited 0 without force; `git ls-remote --exit-code origin refs/heads/main` matched the commit and `git status --porcelain` was empty at 04:06:24 UTC. Target: `https://github.com/MentorAliu/adaptive_spot_lab.git`, branch `main`. The exact receipt and push output are retained in `f/delivery-implementation.json` and `f/delivery-push.log`.

After delivery, `./tools/m2-acceptance.ps1 -RunId m2-completion-0927e -Phase Stop` exited 0 at 04:07:16 UTC. The last review services' logs were preserved first; final inventory showed zero task containers, all 28 task volumes retained and both recovery-dump hashes unchanged. `e/narrator-cleanup.json` records the closeout. Owner resources remained untouched, normal collection disabled, and M3 unstarted.

## Verified M2 normal deployment — 2026-09-28

The owner's [standing milestone rule](../DECISIONS.md#2026-09-28--completed-milestones-must-run-locally) authorized this update of normal project `adaptive-spot-lab`, URL `http://127.0.0.1:4317/`, from M0 to the accepted M2 source at `bb0fb0298ca56cedf191e3db2c494039a9d18d3f`. [ExecPlan 0004](plans/0004-milestone-local-delivery.md) records identities and preservation boundaries. Commands below actually ran; they are not a request to repeat the migration or overwrite current data.

The task-scoped `.cache/deployments/m2-local-20260928a/backup-restore.ps1` helper ran `pg_dump -U asl -d asl -Fc` inside normal PostgreSQL, copied the dump without binary shell redirection, and used `pg_restore --exit-on-error` in a fresh network-disabled PostgreSQL 17.11 container/volume. Its schema/table/metadata comparison passed at 04:21 UTC; the protected dump checksum and retained restore identity are in the plan. The first launch's folder-permission failure and correction remain recorded. The normal database was unchanged during backup/restore.

```powershell
$env:ASL_MARKET_ENABLED = '0'
./tools/setup-local.ps1
docker compose -p adaptive-spot-lab config --quiet
docker compose -p adaptive-spot-lab build migrate api web
docker compose -p adaptive-spot-lab stop web api
docker compose -p adaptive-spot-lab run --rm migrate
docker compose -p adaptive-spot-lab up -d --wait --wait-timeout 120 api web
docker compose -p adaptive-spot-lab ps
```

All exited 0. Setup created only missing secrets and preserved the original secret hashes. The build used frozen lockfiles and cached accepted build steps. Forward migrations reached `0004_m2_completion`; the existing PostgreSQL data volume remained attached. Read-only Docker/SQL inspection, private GET probes and the real reconciliation function verified preserved metadata, healthy services, empty initial account state and disabled collection. Concurrent normal-app owner/account setup was subsequently observed and preserved; the authoring agent did not perform it. Final reconciliation and readiness passed again at 04:31 UTC.

Source hashing matched all 146 accepted-manifest files and all 29 runtime API/migration files. Docker Node hashing matched all 64 compiled web files to the accepted Narrator image. `pnpm exec shadcn info --json` ran in the retained pinned `web-tools` image: its offline registry lookup failed, then the same command on `bridge` exited 0 and confirmed the unchanged preset/base/framework. The in-app browser's real sign-in page was inspected through its accessibility tree and screenshot without entering credentials. Prior M2 full tests were not repeated for unchanged runtime payloads.

After label verification, `docker stop asl-m2-delivery-20260928a-restore` and `docker rm asl-m2-delivery-20260928a-restore` exited 0. Its named recovery volume and dump remain; normal web/API/PostgreSQL were left healthy/running. Logs, source/artifact comparisons, protected state snapshots, failure records and cleanup receipt are retained under the task directory. No collection/trading/agent capability was enabled.

## Verified market/account UI follow-up — 2026-09-28

The changed frontend used the pinned `web-tools` image. `docker compose --profile tools build web-tools`, followed by `pnpm --filter web lint`, `typecheck`, `test:unit` and targeted `prettier --check` through `docker compose --profile tools run --rm --no-deps web-tools`, all exited 0 after formatting; 17 unit tests passed. The first targeted Prettier check failed on five changed files and was corrected in the pinned authoring image. `shadcn info --json` failed on the network-disabled tooling service, then succeeded in the same image on a read-only bridge-network run. `shadcn search` had no configured searchable registry; `shadcn docs toggle-group` succeeded.

Fresh isolated `ui-0928a` and `ui-0928b` M2 acceptance manifests supplied distinct secrets, projects, databases, ports and subnets. `ui-0928a` BrowserEmpty passed one Chromium case covering no invented chart, disabled explanation, URL filters, SOL active nav and reload. A separate `ui-0928b` Chromium funding case passed one owner setup/top-up journey with formatted values. Both isolated web images built successfully; their 64 compiled files matched the normal web candidate by aggregate SHA-256 `3e8f2a2f8578428e1a3db2eea7fcd7cbf9001521ee74d1f3ff0df8cfd1cc704f`. Both isolated stacks were stopped with `docker compose down --remove-orphans`; named volumes and logs remain.

The revised empty-market Back/Forward case passed again in `ui-0928a`. Fresh `ui-0928c` passed three foundation/funding Chromium cases, three market live/unavailable/recovered cases and four desktop/mobile loading/symbol/history race cases under cancellable and deliberately uncancellable transport. Its fixture stack was stopped with volumes retained. Final TypeScript check exited 0; the new empty-market test needed one Prettier formatting pass, with the final check recorded in ExecPlan 0005.

For the account/Markets badge clarification on 2026-09-28, the existing pinned Docker `web-tools` image was rebuilt; `pnpm --filter web lint`, `typecheck`, `test:unit` (17 passed) and targeted `prettier --check` all exited 0. Read-only `shadcn info --json` and `shadcn docs badge` succeeded in the existing authoring image on bridge networking; default registry search reported no configured searchable registry. A protected 83,533-byte pre-upgrade database dump was retained with SHA-256 `dba4a2314d680e16016b423da334f37ec22a0acc8e9cf3d6df98a327e2e5e4cb`. `docker compose build web --quiet` and `docker compose up -d --no-deps --wait --wait-timeout 120 web` exited 0. New normal web image `sha256:5b267d439a96c33940643a8a81f9566fef0921d174aa5536fe46769263f701c3` is healthy; API and PostgreSQL were unchanged and healthy, readiness was HTTP 200, schema `0004_m2_completion`, and market-worker count zero. The in-app browser verified both updated badges, and separate Chromium captured the Account sign-in view. The first Chromium host route returned HTTP 421 `Untrusted host`; the normal internal `web:3000` route returned 200. Manual Narrator was not rerun. Full evidence is in [ExecPlan 0005](plans/0005-market-account-ui-followup.md#owner-clarification--page-milestone-labels-2026-09-28).

Before normal deployment, `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/ui-comments-20260928a.dump` exited 0. `docker cp` placed the 83,269-byte dump in the protected `.cache/deployments/ui-comments-20260928a` folder; SHA-256 is `32b7beaefd34603a8bc16dad514b27b5657d3bba2938459366e0437bdefdb3be`. `docker compose build web --quiet` and `docker compose up -d --no-deps --wait --wait-timeout 120 web` exited 0. The running web image changed to `sha256:295e36ee7f4db21bda8506ee17f2a048bf64d803fa389853219258a25e563978`; normal API/PostgreSQL identities were unchanged, all services healthy, API readiness HTTP 200, schema `0004_m2_completion`, market-worker count zero. The in-app browser verified the updated account and disabled Markets pages. Exact state and limitations are in [ExecPlan 0005](plans/0005-market-account-ui-followup.md).

## Verified normal public-market activation — 2026-09-28

The owner explicitly requested enabling public collection. Read-only preflight found schema `0004_m2_completion`, healthy normal web/API/PostgreSQL, both feeds `DISABLED`, market-worker secret present, 660,541,841,408 host bytes free and 776,707,824 KiB available on PostgreSQL's Docker filesystem. The bounded `docker compose --profile public-smoke build public-smoke --quiet` and `docker compose --profile public-smoke run --rm --no-deps public-smoke` both exited 0. The latter checked Binance public clock, BTCUSDT/SOLUSDT Spot eligibility, three finalized candles each and both stream message types in 6.102 seconds; its log is protected under `.cache/deployments/market-activation-20260928a`.

`docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/market-activation-20260928a.dump` and `docker cp` exited 0. The protected external dump is 83,802 bytes, SHA-256 `d5f8ce1e1991a54f7bb8390950e7206d7d6cd7d8ab606c5af1036f87778780af`. Ignored local `.env` was created with only `ASL_MARKET_ENABLED=1`; `docker compose --profile market config --quiet` passed and effective config showed database `asl`, one worker secret, read-only root and only private plus market-egress networks. `docker compose --profile market build market-worker --quiet` and `docker compose --profile market up -d --no-deps market-worker` exited 0; no migration or other service recreation occurred.

The running worker image is `sha256:35a8399b108e7170e219e32b62872ad2ff945442199157953cc974848e257780`, with `unless-stopped` restart policy, no published port and only the market-worker secret. Its lease reached epoch 2; both feeds reached `CONNECTED`, published observations exceeded 1,486, and the normal API reported both quotes usable with no queue warning/overload. The authenticated in-app Markets browser showed a SOL hourly chart and exact values. A separate normal Chromium `/system` visit returned HTTP 200 and showed market data `ready`, paper trading `disabled`; screenshot `system-market-ready.png` is retained in the protected task directory. No new application test suite, schema migration or manual Narrator run was performed for this configuration-only activation. See [ExecPlan 0006](plans/0006-public-market-activation.md) for operating and recovery boundaries.

## Verified Markets refresh control — 2026-09-28

The official shadcn skill and project workflow were loaded. In Docker, `pnpm exec shadcn info --json` confirmed the fixed preset and installed Toggle Group after an initial networkless DNS failure. `pnpm exec shadcn search '@shadcn' -q toggle-group -t ui` found the official item, and `pnpm exec shadcn docs toggle-group` returned its Base UI guide. Official TanStack Query polling and Router search-param guidance were checked; no package or chart adapter changed.

`docker compose --profile tools build web-tools --quiet` exited 0. Final `docker compose --profile tools run --rm --no-deps web-tools pnpm --filter web typecheck`, `lint`, `check` and `test:unit` exited 0; 17 unit tests passed. An initial typecheck caught the default Markets link missing `refresh`, lint caught inline type imports, and formatting check found two files; all were corrected. The first isolated browser run caught Router serializing a timed rate string as a quoted URL value. Validated numeric rates fixed it. With fresh project `asl-refresh-0928a`, database `asl_m1_browser_m2_refresh_0928a`, separate networks/port and no market-worker profile, the final `browser-tests ... test:e2e --grep 'M2 shows an empty'` passed in Chromium. It checked URL persistence and Back/Forward, invalid fallback, mobile keyboard/overflow and actual Off/Live request behavior. The isolated services were stopped after testing, retaining their volume. No fixture output is presented as public-provider evidence.

Before normal deployment, `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/market-refresh-20260928a.dump` and `docker cp` exited 0. The protected backup `.cache/deployments/market-refresh-20260928a/market-refresh-20260928a.dump` is 3,420,546 bytes, SHA-256 `1ecfeea6243770fdf9a47e358f10937318d51f1707f527ac5fd8b732a3f27921`. `docker compose --profile market build web --quiet` and `docker compose --profile market up -d --no-deps --wait --wait-timeout 120 web` exited 0. Only web was recreated; final running web image `sha256:57b778442eccb0c698d1b2187618f6c95609532488653744ff5cc2f9fb87b936` has the same compiled payload hash `35eace0b86b9c87d6681d3399f667b5aee951fd1fff0b00ce954797a24e28687` as the isolated tested image. Normal API, PostgreSQL and public worker container identities remained unchanged. Web/API/PostgreSQL were healthy, schema remained `0004_m2_completion`, and the API reported both feeds `CONNECTED` with usable quotes, worker known and no queue warning/overload. After owner sign-in, the normal in-app browser showed the Live and 30-second URL states with a candlestick chart. Manual Narrator and the full M2 acceptance workloads were not rerun for this scoped UI change. See [ExecPlan 0007](plans/0007-market-refresh-control.md).

## Verified market candle table display — 2026-09-28

Docker `shadcn info --json`, `search '@shadcn' -q table -t ui` and `docs table` passed in the pinned authoring image on bridge networking. `docker compose --profile tools build web-tools --quiet`, then containerized `pnpm --filter web typecheck`, `lint` and `test:unit` passed (17 tests). The first Prettier check found one test assertion layout issue; after correction and rebuilding `web-tools`, `pnpm --filter web check` passed. `docker compose --profile market build web --quiet` passed.

Before the normal web-only rollout, `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/candle-table-20260928a.dump` and `docker cp` both passed. The protected copied dump is 4,581,372 bytes, SHA-256 `e0579f6db39d48a88e43e1375717313d7585fe5412a52e70f65b11880676369f`. `docker compose --profile market up -d --no-deps --wait --wait-timeout 120 web` exited 0 and reported healthy. The running web image is `sha256:7df510e657d195ccb14254c33ac0e9729f2214c4648d09b9fc0efa86682e5602`; API, PostgreSQL and worker container IDs were unchanged. The corrected `alembic_version` SQL query returned `0004_m2_completion` (an earlier `schema_migrations` query failed because that relation does not exist); `http://127.0.0.1:4317/` returned HTTP 200. The signed-in in-app browser reload showed the live chart and formatted BTC candle table. See [ExecPlan 0008](plans/0008-market-candle-table-display.md) for scope and unrun checks.

## Verified RHF form-state follow-up — 2026-09-28

From the repository root, Docker `shadcn info --json` passed in the web tooling image. Final `docker compose --profile tools build web-tools --quiet`, followed by `docker compose --profile tools run --rm --no-deps web-tools pnpm --filter web` with `lint`, `typecheck`, `test:unit` and `build`, all exited 0. The targeted `pnpm --filter web exec prettier --check src/account/owner-access.tsx src/account/account-home.tsx src/account/schemas.ts src/account/form-states.test.tsx` passed. The unit suite reported 21 passed. Initial lint/format/test failures were corrected before the final checks; build retained nonfatal upstream directive warnings.

Fresh isolated project `asl-rhf-0928a` used `ASL_SECRET_DIR=./secrets/rhf-0928a`, `ASL_DB_NAME=asl_m1_browser_rhf_0928a`, `ASL_TEST_ISOLATED=1`, frontend/private subnets `10.241.30.0/27` and `10.241.30.32/27`, and port 4334. `docker compose -p asl-rhf-0928a --profile test up -d --build --wait postgres api web`, `build browser-tests --quiet`, and `run --rm browser-tests pnpm --filter web test:e2e e2e/funding.spec.ts` exited 0; 1 Chromium case passed. `down` stopped its containers/networks and retained the test volume.

Normal backup commands `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/rhf-forms-20260928a.dump` and `docker cp adaptive-spot-lab-postgres-1:/tmp/rhf-forms-20260928a.dump .cache/deployments/rhf-forms-20260928a/rhf-forms-20260928a.dump` exited 0. The protected copied file is 6,228,707 bytes, SHA-256 `c6680d3cff28f273a2b540568a95644e3490a8a759f123c2ab2d43320859a131`. `docker compose --profile market build web --quiet` and `docker compose --profile market up -d --no-deps --wait --wait-timeout 120 web` exited 0; only web was recreated. The running web image is `sha256:497e20bb23b2839b783bae280af74b08cf9f8d46947b02a160e66725c9606d80`, schema `0004_m2_completion`, and root/System HTTP responses 200. The signed-in normal browser showed the Account top-up form. See [ExecPlan 0009](plans/0009-rhf-form-states.md).

## Verified release-readiness normal rollout and cleanup — 2026-09-28

These commands actually ran against the normal project after owner authorization; they are recorded evidence, not instructions to rerun a migration or overwrite current state. The clean `main` checkout fast-forwarded to `2801898486ae35dd373789a879d3c79fe81d39f0`, which contains application source `1949975f0f6af32a9f6f33a91a4665508bf89fdd`. All five existing secret files and the already-enabled public-market setting were preserved. A protected `pg_dump -Fc` was copied to `.cache/deployments/release-readiness-20260928a/release-readiness-20260928a.dump` (24,418,959 bytes, SHA-256 `bbd20e2f6a27f0ec470afb6702af308f4c994084710e7d7f9a5da6d431a40241`). A temporary network-disabled PostgreSQL 17.11 helper restored it with `pg_restore --exit-on-error`; revision `0004_m2_completion` and 23 public tables were observed. The helper and its temporary data were removed; the protected host dump remains. The first ACL and helper-copy attempts failed before the successful restricted-ACL and restore attempts; see [ExecPlan 0010](plans/0010-release-readiness.md#owner-authorized-normal-rollout-and-cleanup--2026-09-28).

The following normal Compose commands exited 0, in order, from the repository root:

```powershell
docker compose config --quiet
docker compose --profile market build --quiet migrate api market-worker
docker compose build --quiet web
docker compose --profile market stop web api market-worker
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 postgres
docker compose run --rm --no-deps migrate
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 web
docker compose --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
```

The schema stayed at `0004_m2_completion`, accounting reconciliation returned `OK`, and the normal web/API/PostgreSQL healthchecks passed. The worker ran without a Docker healthcheck, recovered its public lease and reported both BTCUSDT and SOLUSDT feeds connected with usable quotes; no collection/trading/agent activation changed. All 29 sampled deployed API/migration runtime files matched the checkout byte-for-byte. Unauthenticated host GETs to `/`, `/markets` and `/system` reached HTTP 200, and a fresh no-secret Chromium context reached those pages and verified the sign-in form's native `post` method. No owner login or funding action was used as a deployment test. The normal API log sample contained 244 structured request records and no traceback/error lines; one web socket-abort stack appeared during rapid navigation, followed by successful requests. The normal web image is `sha256:dd3778c6b26f4b9601177f260913f8e81958428e712bc1b5ddc62ad77500ae5b`, API `sha256:9be9e200d9ba0ea47b39a118ee81c909d561b16a8520d51842e0d7e72908b676`, and worker `sha256:b135fa9b6fbf161e98ef12393e561969f4e81e6fba1128dce6112da9904ab5d1`.

After exact identity inspection, `docker compose -p asl-refresh-0928a down --remove-orphans` removed four exited test containers and two empty task networks without `-v`; `docker rm dc92ed164b22` removed the old exited normal migration container. The normal app's four containers and three required networks remained, and all named database/test/cache volumes were retained. No broad Docker prune ran. The published host address is `http://127.0.0.1:4317/`: Compose maps its project-selected loopback default `WEB_PORT=4317` to production Nitro port 3000 inside the web container. It is not a Vite development server. Manual accessibility, full network-path workload timing, sustained real-provider capture and complete artifact-notice review remain open; this update does not constitute complete release sign-off.

## Verified normal web port alignment — 2026-09-28

At the owner's request, the normal host mapping now defaults to `127.0.0.1:3000→3000/tcp`, matching the production container port. The `WEB_PORT` override remains for isolated projects; `./tools/compose-test.ps1 config --quiet` passed with its distinct port. Before the web-only recreation, a fresh `pg_dump -Fc` was copied to the protected `.cache/deployments/release-readiness-20260928a/port-default-20260928a.dump` (25,701,076 bytes, SHA-256 `5ebedd49e90fc06f312c5e0f913bb34877cc1da50258aa032d6549235baad3b7`). Source/host dump hashes matched; the file ACL is protected with no broad allow rules. The temporary database-container copy was removed after verification. No migration or schema change was needed.

`docker compose config --quiet` and `docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 web` exited 0. New web container `10069793f9a7` is healthy on unchanged image `sha256:dd3778c6b26f4b9601177f260913f8e81958428e712bc1b5ddc62ad77500ae5b`; API `259fd336ce00`, worker `18979d2a516e` and PostgreSQL `83f227fc1a1c` kept their container identities. Revision stayed `0004_m2_completion`. Unauthenticated host GETs to `/`, `/markets` and `/system` each returned 200 at `http://127.0.0.1:3000/`; the old port 4317 had no listener. A fresh no-secret Chromium container reached all three routes and confirmed the hydrated Sign in button was enabled and the native form used POST. An initial browser assertion erroneously searched for the submit button inside the form; the button is associated through its `form` attribute, and the corrected check passed. No owner credentials, funding action or activation change was used.

## ExecPlan 0012 isolated stream-continuity commands — 2026-09-28

These ran from the repository root on Windows PowerShell 5.1.26100. No PowerShell 7 is installed on this host; `tools/m2-acceptance.ps1` was first made 5.1-compatible (see [ExecPlan 0012](plans/0012-market-stream-continuity.md#implementation-record--2026-09-28)). They are recorded evidence, not a normal deployment.

**B0 reproduction.** The unchanged worker with only the new fixtures and tests used run `continuity-b0` (`-Phase Prepare`, later `-Phase Stop`). Its engine target was built, migrated and tested through a scratch wrapper that sets the same manifest environment as `Invoke-Compose`: `docker compose -p asl-m2-continuity-b0-engine --profile test build --quiet migrate engine-tests`, `up -d --wait postgres`, `run --rm migrate`, then `--profile test run --rm engine-tests uv run --frozen python -m pytest -q tests/test_m2_stream_continuity.py`. The expected three failures are recorded in the plan.

**Acceptance run `continuity-0928a`.** These phases exited 0 unless noted:

```powershell
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase Prepare
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase PublicWorkerStart -RotationSeconds 600
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase Build
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase Checks
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase Regression
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase PublicWorkerContinuity -SampleSeconds 1560
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase Performance
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase PublicWorkerNetworkInterrupt
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase PublicWorkerStart -RotationSeconds 600
./tools/m2-acceptance.ps1 -RunId continuity-0928a -Phase PublicWorkerContinuity -SampleSeconds 3000
```

- `Checks` passed web lint, typecheck, unit tests, API-contract check, ruff, OpenAPI check, format check and production web build.
- **Regression.** The first run failed 9 new tests: an older integration test had published future-dated BTC quotes into the shared test database. After that test was corrected the rerun passed 84. The final source passed 85, with one pre-existing Starlette deprecation warning.
- **WorkerFaults.** 35 passed, then 36 on the final source; the M2 completion baseline was 20.
- **RecoveryMemory.** 30 measured recoveries; the final source settled at 428 KiB RSS growth with 0 retained market tasks.
- **Performance.** The normal run published 10,800/10,800 with p95 143.8 ms and p99 149.9 ms. The burst published 30,000/30,000 with p95 168.7 ms and p99 175.3 ms. API p95 was 12.1 ms sequential and 72.5 ms concurrent. All declared bounds passed.
- **Public worker.** It used the real Binance public endpoints with the isolated-only 600 s rotation override.
  - The first 1,560-sample window had 0 unusable samples, across rotations and the 20:00 UTC in-place adoption.
  - `PublicWorkerNetworkInterrupt` first failed its ownership check, before any disconnect, on a Windows PowerShell 5.1 quoting defect; after the fix it passed.
  - The second, 3,000-sample window found 9 unusable samples. Their analysis is in the plan; they led to the refresh-cadence fix.
  - The third window ran on the final image.

Where a phase was rerun, the earlier log was renamed with a `-pre-final` or `-pre-schedule` suffix beside the final log in `.cache/m2/continuity-0928a/`.

## Verified stream-continuity normal deployment — 2026-09-28

These ran against the normal project from the clean checkout at `ac38d156493b87ad9810d8e2f5855f4d5c8ac46f`. They are recorded evidence, not instructions to rerun.

**Rollback tags.** `docker image tag adaptive-spot-lab-{api,market-worker,migrate}:latest …:pre-0012` preserved the previous images (`sha256:9be9e200…`, `sha256:b135fa9b…`, `sha256:2b545ea2…`).

**Protected backup.**
- `docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/stream-continuity-20260928a.dump`, then `docker cp …` into `.cache/deployments/stream-continuity-20260928a/`, whose ACL was set with `icacls … /inheritance:r /grant:r` to SYSTEM, Administrators and the owner account.
- The dump is 56,600,662 bytes, SHA-256 `3a52c4b145cff398ef3d1f9f1191b2bb6c3da7017edaa946514539e8c504a207`; the container `sha256sum` and host `Get-FileHash` matched.
- The in-container copy was removed.

The following exited 0, in order:

```powershell
docker compose config --quiet
docker compose --profile market build --quiet migrate api market-worker
docker compose run --rm --no-deps migrate
docker compose up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
```

**Verification.**
- Running images: API `sha256:0a1664ca92b6c9fec0ebf620e9225f9bc93511e19e432fb4845abe76bd38dc86`, worker `sha256:348804f6633c1b44ff57e33adc7145ea684b0dc9793883ad18acbeca5d8cef25`.
- `docker exec … sha256sum` matched the checkout for 18 market-data source files.
- The API readiness route returned 200 from inside the API container.
- Schema stayed `0004_m2_completion` (read-only `SELECT`), and read-only account-latch and audit checks showed no reconciliation failure.
- Unauthenticated host requests to `/`, `/markets` and `/system` returned 200.
- The in-app browser showed the sign-in form, and System read Market data ready and Paper trading disabled.

**Soak.**
- `docker exec -e ASL_DB_ROLE=market_worker adaptive-spot-lab-market-worker-1 python -m app.market_data.continuity_probe --seconds 3600` ran twice, in consecutive hours.
  - 22:33:36–23:33:35 UTC: 3,600 samples, 0 unusable, across the 23:00 in-place adoption.
  - 23:33:58–00:33:57 UTC: 3,600 samples, 0 unusable, across the 00:00 adoption.
- The samples are retained as `soak-1.jsonl` and `soak-2.jsonl` beside the backup.
- Read-only market-table `SELECT`s, run with `PGOPTIONS="-c default_transaction_read_only=on"`, showed 0 incidents and one collection from the deployment through 00:34 UTC. No receipt gap exceeded Binance's own event spacing by more than 10 ms.

**Isolated public-worker third window.** `-Phase PublicWorkerStart -RotationSeconds 600` recreated the worker on the final image, and `-Phase PublicWorkerContinuity -SampleSeconds 3000` then recorded 3,000 samples with 4 unusable, analysed in the plan. `-Phase Snapshot`, `-Phase PublicWorkerStop` and `-Phase Stop` followed; volumes were kept.

## Verified M3 acceptance commands — 2026-09-29

From the M3 worktree in Windows PowerShell 5.1 (the harness no longer needs PowerShell 7). Final-source run `m3-0929e`; every phase exited 0 (logs and manifest in `.cache/m3/m3-0929e/`):

```powershell
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Prepare
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Snapshot          # before and after; 224 source files, 0 differences
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Build
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Generate
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Checks            # lint, typecheck, web unit, api:check, Ruff, OpenAPI --check, Prettier, web build
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Regression        # engine-tests + mode guard
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Migration         # 0004 predecessor -> 0005 with a concurrent writer; dump/restore
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase WorkerFaults      # kill, pair, pause/unpause, DB interrupt, 30 random kills
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Replay
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase ReplayIsolation
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Performance
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase BrowserInactive
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase BrowserPopulated
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase BrowserError
./tools/m3-acceptance.ps1 -RunId m3-0929e -Phase Stop              # never removes volumes
./tools/m3-replay.ps1 -RunId rp-<id> -Source fixture:gapped-stop -CostScenario COST_SCENARIO_HYPOTHETICAL_H1 -Repeat 2   # PROPOSED owner command; not separately run
```

Results (actual): 167 real-PostgreSQL engine tests passed with no skips (M1, M2 including ExecPlan 0012's continuity suite, and M3); 32 web unit tests; lint, typecheck, API/OpenAPI drift, Ruff, Prettier and the production build passed. The mode guard refused `OFFLINE_TEST` and `HISTORICAL_RESEARCH` rows in a scratch non-`asl_m1_` database. Migration: M1 table fingerprints were identical before and after 0005 while a synthetic market writer kept publishing (5 → 282 publications); reconciliation OK; populated M3 state (4 orders, fills, a latch) survived `pg_dump`/`pg_restore` with identical fingerprint `3427c0f3…e239` and reconciled as `asl_api`. Worker faults: kill → epoch 1→2; two workers held one stable epoch; the paused holder was fenced (`execution_authority_lost`, `lease_renewal_stale`) while the standby took epoch 3; a PostgreSQL stop/start recovered at epoch 4; 30 randomized kills ended at epoch 15 with publications still flowing and processed (checkpoint 672 → 1,262); invariants and reconciliation OK throughout. Replay: two `fixture:gapped-stop` runs produced the identical fingerprint `2500c8d1…61e`; a market-tables-only dump replayed with its SHA-256 recorded and labeled `RESTORED_SYNTHETIC_FIXTURE`; the replay network could not resolve or reach the normal project. Performance (1 CPU test container): strategy evaluation p95 3.24 ms over 17,520 bars (budget 500 ms); catch-up of 172,800 stale quotes after a restart 26.24 s (budget 120 s) with exactly one stale-detected stop obligation and no stale fill. Browser: inactive, populated and API-failure states each passed at 390 and 1440 px.

Development iterations are retained in `.cache/m3/m3-0929a`–`d`: they found and fixed a Windows PowerShell 5.1 stderr handling defect in the harness, a missing lease renewal in simulated/probe loops, a restored-replay evidence label that named synthetic data as public, a seeder whose synthetic history predated existing data, and a 390 px toggle-row overflow. Those earlier runs are not counted as the final pass.

## Verified M3 normal deployment — 2026-09-29

Under the standing milestone-deployment authorization, from the M3 worktree with the owner's secrets directory and `.env` (`ASL_MARKET_ENABLED` only):

```powershell
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/m3-paper-broker-20260929a.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/m3-paper-broker-20260929a.dump <owner checkout>\.cache\deployments\m3-paper-broker-20260929a\
# isolated rehearsal: internal-only helper cluster, restore, alembic upgrade head, reconcile as asl_api
docker tag adaptive-spot-lab-<api|web|market-worker|migrate> adaptive-spot-lab-<service>:pre-m3
$env:ASL_SECRET_DIR = '<owner checkout>/secrets'
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market --profile execution config --quiet
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market --profile execution build --quiet migrate api market-worker execution-worker web
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market stop web api market-worker
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env run --rm --no-deps migrate
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env up -d --no-deps --force-recreate --wait --wait-timeout 120 web
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
```

All exited 0. Results are recorded in [ExecPlan 0011](plans/0011-paper-broker-reference.md#normal-deployment--2026-09-29): schema `0005_m3_paper_broker`, reconciliation OK, zero orders/fills/positions/latches, `asl_execution` NOLOGIN, no execution-worker container, both public feeds connected with usable quotes, and the app at `http://127.0.0.1:3000/`.

## Verified M3 gate-closure commands — 2026-09-29

These ran from the primary checkout in Windows PowerShell 5.1 ([ExecPlan 0013](plans/0013-m3-gate-closure.md#7-results)).
- The final run `m3gate-0929b` ran every phase in one detached sequence, from `05b4d98`.
- The recheck `m3gate-0929c` ran from `2838424`.
- Logs, manifests, measurements and `secret-scan/secret-scan.json` are under `.cache/m3/<run>/`.

```powershell
# Order: Prepare, Build, Checks, Regression, Migration, WorkerFaults, Replay, ReplayIsolation, BrowserInactive,
# BrowserPopulated, BrowserError, Performance, then the ExecPlan 0013 phases below, SecretScan, Snapshot, Stop.
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase PerformanceApi      # 10,000 orders/fills, in-process reads
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase PerformanceBrowser  # Orders/Positions/Risk at 390 and 1440 px
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase PerformanceReplay   # seven days, 1,815,038 publications, twice
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase PerformanceEngine   # -EngineSeconds 3600 (default)
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase SecretScan          # before Stop
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase Snapshot
./tools/m3-acceptance.ps1 -RunId m3gate-0929b -Phase Stop                # never removes volumes
./tools/m3-acceptance.ps1 -RunId m3gate-0929c -Phase Prepare             # recheck: Build, Checks, PerformanceBrowser, SecretScan, Snapshot, Stop
```

Results (actual):
- **`0929b`**
  - Regression: 167 engine tests passed, no skips. Web unit: 32 passed.
  - Migration, WorkerFaults, Replay (fingerprint `2500c8d1…561e`, unchanged from M3), ReplayIsolation and the three browser states passed.
  - API reads: p95 19.7 ms sequential and 116.9 ms five-way concurrent.
  - Engine workload: p95 291 ms, p99 311 ms, RSS 63.4 MiB (+0.5 MiB over the final 30 min). Reconciliation OK afterwards.
  - Failed:
    - Checks, on one Prettier line
    - PerformanceBrowser, on Orders interactions 203/238 ms with Playwright tracing on
    - PerformanceReplay: I stopped it after 2,495 s at 433,997 of 1,815,038 publications
    - SecretScan: an isolated setup key inside a failure trace
- **`0929c`**: every check passed, including the Prettier format check and the web build. PerformanceBrowser passed with tracing off (Orders 118/98 ms, Positions 84/80 ms). SecretScan: 123 files, 0 findings.

## Verified ExecPlan 0014 commands — 2026-09-29

Isolated run `bq-0929a`, from the `../adaptive-spot-lab-quote` worktree in Windows PowerShell 5.1:

```powershell
./tools/m3-acceptance.ps1 -RunId bq-0929a -Phase <Prepare|Build|Checks|Regression|WorkerFaults|Replay>   # from 10bd026
./tools/m3-acceptance.ps1 -RunId bq-0929a -Phase <Build|Checks|PerformanceReplay|Snapshot|Stop>        # from 87b1996
```

Results (actual): 169 engine tests passed with no skips; WorkerFaults passed; `gapped-stop` fingerprint `2500c8d1…561e` unchanged. PerformanceReplay failed its budget and was stopped by the operator: the first attempt stalled in the test loader (fixed in `87b1996`), and the rerun ran about 46 ms per engine step once positions were open. See [ExecPlan 0014 §10](plans/0014-bounded-latest-quote.md#10-completion-evidence).

Normal deployment of `5a1f858`, from the same worktree with the owner's secrets directory and `.env`, through a scripted sequence that stops at the first failed step:

```powershell
docker image tag <running api image> adaptive-spot-lab-api:pre-0014   # likewise market-worker, migrate, execution-worker
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/bounded-quote-20260929a.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/bounded-quote-20260929a.dump <owner checkout>\.cache\deployments\bounded-quote-20260929a\
$env:ASL_SECRET_DIR = '<owner checkout>/secrets'
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market --profile execution config --quiet
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market --profile execution build --quiet migrate api market-worker execution-worker
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env run --rm --no-deps migrate
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose -p adaptive-spot-lab --env-file <owner checkout>\.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
```

All exited 0. Two earlier launches stopped at their first read-only `docker inspect`, before any change. Results are in [ExecPlan 0014 §10.5](plans/0014-bounded-latest-quote.md#105-normal-deployment-verified).

## Verified M4 acceptance commands — 2026-09-29

These ran from the primary checkout on branch `claude/m4-fixed-pilot` in Windows PowerShell 5.1. The final run `m4f-0929c` ran from `be61a32`, driven by a detached sequence that stops at the first failed phase. Logs, the manifest and the measurements are in `.cache/m4/m4f-0929c/`.

```powershell
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Prepare
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Snapshot              # 01 before, 02 after; 0 differences required
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Build
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Generate
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Checks
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Regression
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Migration             # populated 0005 (M3 image of c96726c) -> 0006; dump/restore
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase ActivationRehearsal
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase BrowserApprovals
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase ApprovalAuth
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase BrowserError
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PerformanceApi
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PerformanceReport
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PilotLifecycle        # real time; entries fill at the next hour boundary
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PilotFaults           # includes the 200-request control race
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PilotDowntime         # -DowntimeSeconds 300 (default)
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Evaluation
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase BrowserPilot
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PerformanceBrowser
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase PerformanceEngine     # -EngineSeconds 3600 (default); writes Replay's forward export
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Replay
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase ReplayIsolation
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase SecretScan            # before Stop
./tools/m4-acceptance.ps1 -RunId m4f-0929c -Phase Stop                  # never removes volumes
```

Results (actual): every phase passed on one snapshot. Measurements and the Q01–Q10 assessment are in [ExecPlan 0015 §16](plans/0015-evaluation-fixed-pilot.md#16-completion-evidence).

Earlier runs:
- `m4f-0929a` failed at Migration and was fixed in `10b48b1`.
- `m4f-0929b` failed at PilotFaults, because the synthetic feed died with the database outage. It was fixed in `be61a32`.

Neither counts as the final pass; see ExecPlan 0015 §14.

## Verified M4 normal deployment — 2026-09-29

This ran under the owner's authorization for the inert deployment, from the primary checkout at the pushed commit `be61a32`, with the owner's `.env` and secrets directory. It used a scripted sequence with one step per invocation that stops at the first failure and logs to `.cache/deployments/m4-fixed-pilot-20260929a/deploy.log`. These are its effective commands:

```powershell
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/m4-fixed-pilot-20260929a.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/m4-fixed-pilot-20260929a.dump <checkout>\.cache\deployments\m4-fixed-pilot-20260929a\
# rehearsal: restore into asl_m1_m4_owner_rehearsal in m4f-0929c's internal-only recovery cluster, run its migrate image,
# reconcile as asl_api, drop the copy
powershell -NoProfile -File tools/setup-local.ps1        # creates only evaluation_db_password
docker image tag adaptive-spot-lab-<api|web|market-worker|migrate|execution-worker> adaptive-spot-lab-<service>:pre-m4
$env:ASL_SECRET_DIR = '<checkout>/secrets'
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env --profile market --profile execution --profile admin config --quiet
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env --profile market --profile execution --profile admin build --quiet migrate api market-worker execution-worker evaluation-worker pilot-admin web
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env --profile market stop web api market-worker
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env run --rm --no-deps migrate
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env up -d --no-deps --force-recreate --wait --wait-timeout 120 web
docker compose -f compose.yaml -p adaptive-spot-lab --env-file .env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
```

All exited 0. The full record is in [ExecPlan 0015 §16](plans/0015-evaluation-fixed-pilot.md#normal-deployment--inert-verified-2026-09-29):
- the backup SHA-256 `523daa0a…9c91`;
- schema `0006_m4_fixed_pilot`, reconciliation OK;
- zero approvals, experiments and reports; `asl_execution` and `asl_evaluation` NOLOGIN; no pilot worker container;
- feeds back after 43.8 s;
- the app at `http://127.0.0.1:3000/`.

The execution and evaluation workers are built but deliberately not started. Activation (M4-B) uses `tools/pilot-activate.ps1` only after the owner's exact-hash approvals and an explicit instruction.

## Verified ExecPlan 0017 commands — 2026-09-29

Isolated runs from the `claude/replay-throughput` worktree in Windows PowerShell 5.1, one phase after another in a detached process that stops at the first failure:

```powershell
./tools/m3-acceptance.ps1 -RunId rt-0929a -Phase <Prepare|Build|Snapshot|ReplayBaseline>                          # baseline, 41b7cd4
./tools/m3-acceptance.ps1 -RunId rt-0929b -Phase <Prepare|Build|Snapshot|Checks|Regression>                         # I1, 9c97e5d
./tools/m3-acceptance.ps1 -RunId rt-0929b -Phase ReplayBaseline -BaselineRun rt-0929a
./tools/m3-acceptance.ps1 -RunId rt-0929c -Phase <Prepare|Build|Snapshot|Checks|Regression> ; -Phase ReplayVerify -BaselineRun rt-0929a   # I2/I3, 3ec2729
./tools/m3-acceptance.ps1 -RunId rt-0929c -Phase ReplayBaseline -ReplayMode <fast|batched> -BaselineRun rt-0929a
./tools/m3-acceptance.ps1 -RunId rt-0929d -Phase <Prepare|Build|Snapshot|PerformanceReplay|Checks|Regression|WorkerFaults|Replay|ReplayBaseline|ReplayVerify|PerformanceEngine> -ReplayMode fast -BaselineRun rt-0929a   # gate, 16590e3
./tools/m3-acceptance.ps1 -RunId <run> -Phase Stop
```

**Results (actual).**
- **Baseline.** `rt-0929a` recorded the digests in [ExecPlan 0017 §18.1](plans/0017-replay-throughput.md#181-baseline--run-rt-0929a-i0-engine-code-as-on-main-verified).
- **I1 (`rt-0929b`).** Regression was 173 passed, 1 failed (a test expectation, fixed). `ReplayBaseline` matched the baseline.
- **I2/I3 (`rt-0929c`).** Regression passed 181, and the fast-path rerun passed 42. `ReplayVerify`, and `ReplayBaseline` in fast and batched modes, all matched the baseline.
- **Gate (`rt-0929d`).** Every phase passed; details are in [ExecPlan 0017 §18.5](plans/0017-replay-throughput.md#185-gate--run-rt-0929d-16590e3).
  - `PerformanceReplay`: 409.81 s and 421.63 s, with an identical fingerprint and step trace.
  - Checks exited 0. Regression passed 182, and the fast-path rerun passed 43.
  - `WorkerFaults` ended at epoch 12 with reconciliation `OK`. `Replay` reproduced `2500c8d1…`.
  - `ReplayBaseline -ReplayMode fast` and `ReplayVerify` matched `rt-0929a`.
  - `PerformanceEngine`: p95 287 ms, p99 307 ms, RSS max 63.3 MiB with 0.96 MiB growth.
  - `-Phase Stop` exited 0 at 17:31 UTC, and the run's volumes are kept.

A fast-path profile ran in a separate isolated project (`rt-0929p`) through the harness's Compose helper, with a scratch profiling script mounted read-only. It is not a repository command.

**After the rebase onto M4.** The commits cited above are kept on `claude/replay-throughput-pre-m4`. The baseline ran from a detached worktree of the rebased tooling commit, and its record was copied into `.cache/m3/rt-0929e` without secrets:

```powershell
git worktree add --detach <scratch>/wt-baseline 1d416e9          # rebased I0 + M4-base tooling (pushed as 4177f86)
./tools/m3-acceptance.ps1 -RunId rt-0929e -Phase <Prepare|Build|Snapshot|ReplayBaseline>     # in that worktree: per step on M4's engine
./tools/m3-acceptance.ps1 -RunId rt-0929f -Phase <Prepare|Build|Snapshot|Checks|Regression|WorkerFaults|Replay>   # gate, 499bc71
./tools/m3-acceptance.ps1 -RunId rt-0929f -Phase <PerformanceReplay|ReplayBaseline|ReplayVerify|PerformanceEngine> -ReplayMode fast -BaselineRun rt-0929e
./tools/m3-acceptance.ps1 -RunId <run> -Phase Stop
```

**Results (actual).** Details are in [ExecPlan 0017 §18.6](plans/0017-replay-throughput.md#186-on-m4--baseline-rt-0929e-and-gate-rt-0929f-rebased-history).
- **Baseline (`rt-0929e`).** `gapped-stop` gave `2500c8d1…` over the M3 columns, and the M3-column fingerprints and step traces of `quiet` and the 48 h window equal `rt-0929a`'s. The window took 1,752.9 s per step.
- **Gate (`rt-0929f`).** Every phase passed:
  - Checks exited 0.
  - Regression passed 254 with no skips. The fast-path rerun of the M3 and M4 suites passed 79.
  - `WorkerFaults` ended at epoch 13 with reconciliation `OK`. `Replay` reproduced the baseline digests.
  - `PerformanceReplay`: 429.53 s and 428.95 s, with the pre-rebase M3-column fingerprint and step trace.
  - `ReplayBaseline -ReplayMode fast` (79.6 s window) and `ReplayVerify` (796.1 s) matched `rt-0929e`. `pilot-lifecycle` matched a per-step run of the same build on every digest.
  - `PerformanceEngine`: p95 291 ms, p99 309 ms, RSS max 64.7 MiB with 1.45 MiB growth.
  - `-Phase Stop` exited 0 at 22:08 UTC, with volumes kept.

## Verified ended-run cause note commands — 2026-09-30

[ExecPlan 0018](plans/0018-ended-run-cause-note.md). These ran from the worktree on branch `claude/ended-run-cause-note` at `0db0a2a`, in Windows PowerShell 5.1. A sequence stopped at the first failed phase. Logs are in the worktree's `.cache/m4/m4w-0930a/`.

```powershell
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Prepare
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Snapshot              # 01 before, 02 after: 0 differences
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Build
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Checks                # 41 web unit tests
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase PilotLifecycle
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase PilotFaults
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase PilotDowntime         # -DowntimeSeconds 300 (default)
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Evaluation
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase BrowserPilot          # 1 passed, 0 skipped
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Stop                  # never removes volumes
docker stop asl-m4-m4w-0930a-pilot-pilot-feed                           # the run's synthetic feed; down does not remove it
docker rm asl-m4-m4w-0930a-pilot-pilot-feed
./tools/m4-acceptance.ps1 -RunId m4w-0930a -Phase Stop                  # releases the feed's network
```

The web-only normal deployment ran under the owner's go-ahead once BrowserPilot passed. It built from the worktree, with the primary checkout's `.env` and secrets directory; no secret value was read. A scripted sequence, one step per invocation, stopped at the first failure and logged to `.cache/deployments/ended-run-causes-20260930a/deploy.log` in the primary checkout. These are its effective commands:

```powershell
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/ended-run-causes-20260930a.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/ended-run-causes-20260930a.dump <primary>\.cache\deployments\ended-run-causes-20260930a\
docker image tag adaptive-spot-lab-web adaptive-spot-lab-web:pre-ended-causes
$env:ASL_SECRET_DIR = '<primary>/secrets'
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env config --quiet
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env build --quiet web
# compiled payload: find /app/.output -type f | sort | xargs sha256sum | sha256sum, in the new and the tested image
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env up -d --no-deps --force-recreate --wait --wait-timeout 120 web
```

All exited 0.
- Backup SHA-256 `5e4902de…f99d`, 135,548,597 bytes.
- Web runs `sha256:3206fdae…b5da`, with a payload identical to the tested image.
- PostgreSQL, API and market worker are unchanged. Schema is `0006_m4_fixed_pilot`, readiness 200, and six pages return 200.

## Verified ExecPlan 0017 normal deployment — 2026-09-30

This ran under the owner's approval in chat ("Deploy, then merge"), from the `claude/replay-throughput` worktree at the pushed PR #6 head `2f7973a`, with the primary checkout's `.env` and secrets directory. It used Git Bash with `MSYS_NO_PATHCONV=1`, because without it Git Bash rewrites container paths such as `/tmp/...`.

```bash
"<user programs>\DockerDesktop\Docker Desktop.exe"          # the host had rebooted; Docker Desktop was not running
docker start adaptive-spot-lab-postgres-1                        # existing container, unchanged; no writer running
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/replay-throughput-20260930a.dump
docker exec adaptive-spot-lab-postgres-1 sha256sum /tmp/replay-throughput-20260930a.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/replay-throughput-20260930a.dump <primary>/.cache/deployments/replay-throughput-20260930a/
icacls <primary>\.cache\deployments\replay-throughput-20260930a /inheritance:r /grant:r "<owner>:(OI)(CI)(F)"   # PowerShell
docker image tag <running api image> adaptive-spot-lab-api:pre-0017     # likewise market-worker; migrate, execution-, evaluation-worker, pilot-admin from :latest
export ASL_SECRET_DIR='<primary>/secrets'
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market --profile execution --profile admin config --quiet
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market --profile execution --profile admin build --quiet migrate api market-worker execution-worker evaluation-worker pilot-admin
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env run --rm --no-deps migrate
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env up -d --no-deps --force-recreate --wait --wait-timeout 120 api
docker compose -f <worktree>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker
docker start adaptive-spot-lab-web-1                             # existing web container (ExecPlan 0018 image), unchanged
# source identity: sha256 over CRLF-normalized hashes of app/ and alembic/ *.py, in the new, the tested (rt-0929f) and the old image
# checks: readiness via the API container; reconcile() as asl_api; market_read.health(); psql counts and roles; six pages via curl
```

All exited 0; the first `pg_dump` attempt had failed before writing anything, because of Git Bash path conversion.
- **Backup.** SHA-256 `efd344d0…1fce`, 149,664,201 bytes.
- **Running images.** API `4fba1a87…` and market worker `73df98a6…`, whose app source equals the tested image (`144b776b…`, 82 files). Web and PostgreSQL are unchanged.
- **State.** Schema `0006_m4_fixed_pilot`, readiness 200, reconciliation OK, both feeds `CONNECTED`, six pages 200. The M4 state is still inert: zero approvals and experiments, both identities NOLOGIN, no pilot worker.
- **Record.** The full record is in [ExecPlan 0017 §13](plans/0017-replay-throughput.md#13-normal-deployment-and-rollback-proposed).

## Verified M4-B activation — 2026-09-30

These were owner-performed steps. The owner made the approvals, the experiment and Start in the authenticated UI at `http://127.0.0.1:3000/` (Approvals and Experiments pages), then ran the activation tool from the primary checkout (`main` `784a67d`):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<primary>/tools/pilot-activate.ps1" -ExperimentId d779fbf4-e1be-444c-ab55-7b61292eaa87
```

- **Result.** All six steps passed: preflight, protected backup, identity enable, `.env` flags, worker start, and the lease and state check. The tool printed "Lease held: True; experiment state: RUNNING".
- **Backup.** `.cache/deployments/pilot-activate-20260930T090919Z/asl.dump`, SHA-256 `e61e1e6e…b898`.
- **Agent's attempt.** An agent's run of the same command was refused by its auto-mode classifier before execution.

Afterwards, with the owner's approval, the agent ran only read-only checks through Git Bash with `MSYS_NO_PATHCONV=1`: `SELECT` queries through `docker exec adaptive-spot-lab-postgres-1 psql`, plus `docker ps` and `docker inspect`. They covered the experiment and its events, the ACTIVATED detail, the checkpoint and lease, strategy evaluations, valuations, the daily reference, account flags, incidents, reports, marks, roles and orders. `reconcile()` was not called, because it latches on a mismatch.

All §12 checks passed, including the first SNAPSHOT (as of 10:00 UTC, `cff38d2d…a377`). Details are in [ExecPlan 0015 §16](plans/0015-evaluation-fixed-pilot.md#m4-b-owner-approvals-and-activation-verified-2026-09-30).

## Verified M5-A acceptance commands — 2026-10-01

These ran from the worktree `.claude/worktrees/m5-agent-runtime` on branch `claude/m5-agent-runtime` in Windows PowerShell 5.1. Every heavy phase waits for, and must finish inside, HH:15–HH:55 UTC (`-WaitForWindow`). The final run `m5-b7j` ran from `9436127` as one ordered sequence that stops at the first failed phase. Logs, the manifest and the measurements are in `.cache/m5/m5-b7j/`.

```powershell
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Prepare
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Snapshot                  # 01 before, 02 after; 0 differences required
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Build -WaitForWindow      # also the pre-M5 images of 2f7973a and eb9f30b
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Generate -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Checks -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase RunnerProcess -WaitForWindow   # run three times in a row
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Regression -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Migration -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase MixedVersion -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase NativeInventory -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase EgressPolicy -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase RunnerIsolation -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase PilotCoexistence -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase NativeBehavior -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase AgentReplay -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase DispatcherAuth -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase ApiAuth -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase AgentOffline -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase AuthStore -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase AgentFaults -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase AgentActivationRehearsal -WaitForWindow   # runs m5-deploy, agent-activate/deactivate, pilot-deactivate
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase BrowserAgents -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase PerformanceBrowser -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase BrowserAgentsError -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase PerformanceAgents -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase PerformanceApi -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase SecretScan -WaitForWindow
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Snapshot
./tools/m5-acceptance.ps1 -RunId m5-b7j -Phase Stop                      # never removes volumes
```

Results (actual): every phase passed, and the closing snapshot showed 0 source differences at `9436127`. Measurements and the Q01–Q10 assessment are in [ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#17-completion-evidence).

Earlier runs:
- `m5-b0a` was the development run for B0–B7; every phase passed there after the fixes that §15 records.
- `m5-b7f` (from `a655564`) stopped at Regression on one stale test, fixed in `b0d43b9`.
- `m5-b7g` (from `b0d43b9`) passed 12 phases, was interrupted by a host restart, and then stopped at RunnerProcess (an oversize-request race, fixed in `c44b303`, and the process count below).
- `m5-b7h` (from `c44b303`) passed 24 phases; SecretScan then failed on a phase-order dependence, and a second PerformanceAgents run missed the orchestrator budget by 0.7 ms because of PostgreSQL JIT compilation. Both were fixed in `05b6cb0`.
- `m5-b7i` (from `05b6cb0`) passed 10 phases and stopped at RunnerProcess: the container healthcheck was counted as a job leftover. Fixed in `9436127`.

None of `m5-b7f` to `m5-b7i` counts as the final pass.

**Normal-app scripts.** `m5-deploy.ps1` was run against the normal app on 2026-10-02 (next section). The owner ran the two M5-B scripts on the normal app the same day (results in [ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#m5-b--activation-login-profile-and-capability-probes-2026-10-02)); `agent-deactivate.ps1` is **not run** there and was rehearsed only on the isolated rehearsal kind:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/agent-activate.ps1 -Stage Probe   # owner, 2026-10-02 11:11 UTC: six steps, LOGIN_REQUIRED, 4 pilot services unchanged
powershell -NoProfile -ExecutionPolicy Bypass -File tools/agent-login.ps1                   # owner, 11:20 UTC, after the activation (a run before it fails: the gateway is not up yet)
./tools/agent-deactivate.ps1                                                                # not run on the normal app
```

The implementer's run of `agent-activate.ps1` was refused by the desktop app's auto-mode check; the owner ran both scripts in their own terminal. `agent-activate.ps1` refuses between HH:55 and HH:10 UTC.

## Verified M5-A normal deployment — 2026-10-02

This ran with the owner's approval ([DECISIONS](../DECISIONS.md#2026-10-02--m5-a-inert-normal-deployment-b8-approved-before-the-merge-execplan-0020)), from the primary checkout detached at the pull-request head `07747ec`, with the owner's `.env` and secrets directory, between 08:22:13 and 08:25:47 UTC (inside HH:15–HH:45, with no open position):

```powershell
# the compose file the pilot was deployed from, written without re-encoding (SHA-256 8947d11b..., equal to the git blob)
[IO.File]::WriteAllText('.cache/deployments/m5-baseline-compose-eb9f30b.yaml', ((git show 'eb9f30b:compose.yaml') -join "`n") + "`n")
./tools/m5-deploy.ps1 -BaselineComposeFile .cache/deployments/m5-baseline-compose-eb9f30b.yaml
```

Exit code 0, all ten steps. These are the script's effective commands against the normal project; it selects no market, execution or admin profile and names no pilot service in a build, `up`, `stop` or `restart`:

```powershell
docker compose -p adaptive-spot-lab --env-file .env ps -a -q <service>                          # identities, before and after
docker compose ... --profile market --profile execution --profile admin config --format json    # rendered-config hash only
docker tag <running image> adaptive-spot-lab-<market-worker|execution-worker|evaluation-worker>:pilot-d779fbf4
docker tag adaptive-spot-lab-<migrate|api|web> adaptive-spot-lab-<service>:pre-m5
docker compose ... exec -T postgres pg_dump -U asl -d asl -Fc -f /tmp/pilot-backup.dump         # protected backup with SHA-256; the temporary file is removed
docker compose ... exec -T postgres pg_dumpall -U asl --roles-only --no-role-passwords          # for the helper rehearsal
# rehearsal in an internal-only postgres:17.11 helper: pg_restore, alembic upgrade head, reconcile as asl_api,
# alembic downgrade 0006_m4_fixed_pilot; the helper and its network are removed
docker compose ... build --quiet migrate
docker compose ... --profile agents --profile agent-auth --profile agent-admin build --quiet migrate api web agent-worker agent-runner agent-egress agent-auth agent-admin
docker compose ... up -d --no-deps --force-recreate --wait web
docker compose ... up -d --no-deps --force-recreate --wait api
docker compose ... run --rm --no-deps migrate                                                    # 0007, first attempt
docker compose ... exec -T postgres psql -U asl -d asl -At -c "<read-only checks>"
```

Results (actual), recorded in full in [ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#b8-completion-evidence--inert-normal-deployment-2026-10-02):
- the backup SHA-256 `4575c023…b581` (237,320,415 bytes), restored and migrated in the helper with equal static fingerprints and reconciliation OK;
- schema `0007_m5_agent_runtime`; the agent runtime DISABLED; `asl_agent` NOLOGIN; no agent container; zero agent workflows, profiles and approvals;
- postgres, market-worker, execution-worker and evaluation-worker with the same container, image, start time and restart count as before; lease epoch 4 unchanged; no new execution incident or experiment event;
- api `sha256:54368771…` and web `sha256:0801ab1c…` running and healthy; the api's code identity equals the tested `m5-b7j` api's;
- the app at `http://127.0.0.1:3000/` (sign-in page, HTTP 200).

The implementer's read-only verification afterwards used `docker exec` on the postgres, api and web containers, `docker inspect`, `docker ps`, `docker logs` and the in-app browser without signing in.

## ExecPlan 0021 isolated density commands — 2026-10-02

These ran on Windows PowerShell 5.1.26100 against the isolated Compose projects `asl-m2-lag-1002a-*` to `asl-m2-lag-1002d-*` only. No Docker or Compose command targeted the normal `adaptive-spot-lab` project, and no public market endpoint was contacted. They are recorded evidence, not a normal deployment. Results and limits are in [ExecPlan 0021](plans/0021-publication-cost-at-density.md#9-verification-isolated).

**Unfixed worker, run `lag-1002b`.** A scratch `git worktree` of `8fdc06a` received only this plan's harness script and the unfixed variant of the measurement module. `<scratch>` is that worktree.

```powershell
<scratch>/tools/m2-acceptance.ps1 -RunId lag-1002b -Phase Prepare
<scratch>/tools/m2-acceptance.ps1 -RunId lag-1002b -Phase PerformanceDensity -DensityLevels '250000,500000,750000,1000000,1400000,1800000' -DensitySeconds 600 -Observe
<scratch>/tools/m2-acceptance.ps1 -RunId lag-1002b -Phase Stop
```

- `PerformanceDensity -Observe` exited 0 after recording all six levels (09:08–10:17 UTC). The unfixed worker failed the budgets from 500,000 stored rows and recorded 42 `QUEUE_OVERLOAD` collection failures.

**Publication fix alone, run `lag-1002a`**, from this worktree at commit `0941756`: `Prepare`, `Build`, `Checks`, `WorkerFaults` (42 passed), `Regression` (260 passed), `RecoveryMemory` and `PerformanceDensity` with the six levels above. All exited 0, and the density budgets passed at every level (10:17–11:26 UTC). Two record-only runs of the measurement module against that run's 1.8-million-row database then exposed and checked the retention defect (`--existing --seconds 240 --retention-after 45 --observe`): the first, on `0941756`, recorded a `QUEUE_OVERLOAD`; the second, with retention on its own thread, recorded none.

**Final source, run `lag-1002c`**, from this worktree at commit `b40ac9a`:

```powershell
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Prepare
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Build
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Checks
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Regression
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase PerformanceDensity -DensityLevels '250000,500000,750000,1000000,1400000,1800000' -DensitySeconds 600
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase PerformanceBurst
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId lag-1002c -Phase Stop
```

All exited 0.
- **Snapshot.** Both snapshots record commit `b40ac9a3efaf914a782cad987b44e5b0f9c3d98d` and the same 291 source hashes.
- **Checks.** Web lint, typecheck, unit tests, API-contract check, Ruff, OpenAPI check, format check and the production web build. No web source changed.
- **WorkerFaults.** 43 passed, none skipped (36 before this plan, plus seven new tests).
- **Regression.** 261 passed, with the one pre-existing Starlette test-client deprecation warning.
- **RecoveryMemory.** 30 measured recoveries, 428 KiB settled RSS growth, 0 retained market tasks.
- **PerformanceDensity** (11:42–12:50 UTC). No budget failure at any of the six levels: receipt-to-publication p95 115–117 ms and p99 117–119 ms, every frame published, no incident, every sample usable. At the last level 32 retention calls deleted 16,000 observations and 16,000 payloads under the stream.
- **PerformanceBurst.** 30,000 of 30,000 published; p50 135.4 ms, p95 158.9 ms, p99 167.8 ms; schedule lag p99 2.0 ms; maximum RSS 71,576 KiB.

**Merged with `main`, run `lag-1002d`**, at merge commit `b3f8216` (`main` at `dd95775`, after M5-A): the same eleven phases as run `lag-1002c`. All exited 0 (13:02–14:17 UTC).
- **Snapshot.** Both snapshots record `b3f821684e7e943215d6b64bc134bed2a1be0453` and the same 374 source hashes.
- **WorkerFaults** 43 passed; **Regression** 381 passed with the one pre-existing warning; **RecoveryMemory** 392 KiB settled growth, 0 retained tasks.
- **PerformanceDensity.** No budget failure at any of the six levels: p95 115–117 ms, p99 117–120 ms, every frame published, no incident; 16,000 observations deleted under the stream at the last level.
- **PerformanceBurst.** 30,000 of 30,000 published; p95 161.2 ms, p99 173.8 ms.
- A later merge of `main` at `cd5a5e9` (`2b4aa11`) changed only five documentation files, so no phase was repeated for it.

**Other isolated commands.**
- Docker VM pressure and memory, from a throwaway container with no network: `docker run --rm --network none postgres:17.11-alpine3.24 sh -c 'cat /proc/pressure/cpu /proc/pressure/io /proc/pressure/memory; grep MemAvailable /proc/meminfo; uptime'`.
- Plan texts on the isolated density database of run `lag-1002a`: `docker exec <isolated postgres> psql -U asl -d asl_m1_m2_lag_1002a_density -c "EXPLAIN (ANALYZE, BUFFERS) …"` for the full pending scan and for the two retention selections.
- A 45-minute DNS lookup probe (`socket.getaddrinfo` once a second for both provider hosts) in a throwaway container on its own bridge network; container and network were removed afterwards.
- Relative documentation links: `docker run --rm --network none -v <worktree>:/repo:ro asl-m2-lag-1002d-engine-engine-tools python /repo/tools/check_links.py /repo`. 84 Markdown files, 0 broken links.

**Earlier attempts, disclosed.** Three shorter attempts were stopped and their disposable density volumes removed so the fixture could start on an empty database: a 60-second smoke run (`lag-1002s`) that exposed a fixture defect, a first run whose feed sent each second's frames as one burst, and a second whose REST answers were instant. Their partial logs are kept under `.cache/m2/lag-1002a` and `.cache/m2/lag-1002b`.

**Left in place.** The stopped runs' volumes: four density volumes of about 4.3 GB each (`asl-m2-lag-1002a-density_postgres_data`, `asl-m2-lag-1002b-density_postgres_data`, `asl-m2-lag-1002c-density_postgres_data`, `asl-m2-lag-1002d-density_postgres_data`) and five small ones (`asl-m2-lag-1002a-engine_postgres_data`, `asl-m2-lag-1002c-engine_postgres_data`, `asl-m2-lag-1002c-performance_postgres_data`, `asl-m2-lag-1002d-engine_postgres_data`, `asl-m2-lag-1002d-performance_postgres_data`); the runs' images; and the evidence under `.cache/m2/`. Removing the volumes and images is the owner's decision. **The volumes and images were removed on 2026-10-03** on the owner's instruction ([Test-run cleanup](#test-run-cleanup--2026-10-03)); the evidence stays.

## Verified ExecPlan 0021 normal deployment — 2026-10-02

Run with the owner's approval in chat ([DECISIONS](../DECISIONS.md#2026-10-02--market-worker-deployment-approved-execplan-0021)), 15:15–15:18 UTC, from the worktree at pull-request head `4003e75` through Git Bash and Windows PowerShell 5.1. `<primary>` is the primary checkout, which stayed on `main` at `cd5a5e9`; its `.env` and secrets were passed to Compose and never read. The full record is in [ExecPlan 0021 §11.1](plans/0021-publication-cost-at-density.md#111-executed-2026-10-02-15151518-utc-owner-approved).

```bash
# Read-only state (before, after and during the soak)
docker ps -a --filter label=com.docker.compose.project=adaptive-spot-lab
docker inspect <each container>            # service, image, start time, restart count
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on -c statement_timeout=15000" \
  adaptive-spot-lab-postgres-1 psql -U asl -d asl -At -f -      # SELECTs inside BEGIN TRANSACTION READ ONLY
docker logs --timestamps adaptive-spot-lab-market-worker-1
docker stats --no-stream <the project's containers>

# Protected backup (owner-only directory created first with tools/lib/Pilot.psm1 Protect-Path)
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/publication-density.dump
docker exec adaptive-spot-lab-postgres-1 sha256sum /tmp/publication-density.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/publication-density.dump <primary>/.cache/deployments/publication-density-20261002T151536Z/asl.dump
docker exec adaptive-spot-lab-postgres-1 sh -c 'unlink /tmp/publication-density.dump'

# Rollback tag, build one image, confirm the tested source, recreate one service
docker tag sha256:73df98a623ee49861fc7029caf1d3a74ae05fbc4dc42e7e02cdd60f5ef1d550c adaptive-spot-lab-market-worker:pre-0021
docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker
docker run --rm --network none --entrypoint sh adaptive-spot-lab-market-worker:latest \
  -c "cd /app/app && find . -type f | sort | xargs sha256sum | sha256sum"
docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market \
  up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker

# Soak (read-only, twice)
docker exec -e ASL_DB_ROLE=market_worker adaptive-spot-lab-market-worker-1 \
  python -m app.market_data.continuity_probe --seconds 3600
```

All exited 0, except that each probe hour exits 1 by design when it has seen any unusable sample.
- **Backup.** 240,352,091 bytes, SHA-256 `34b57448…66b3`, equal inside the container and on the host.
- **Images.** Market worker `sha256:0d6ac003d933…`, whose `/app/app` tree (103 files, `bc56f6cb…8bdc`) equals the tested image's. Rollback tag `:pre-0021` = `sha256:73df98a623ee…`.
- **Containers.** Market worker `a78b4a5405eb` → `1becbec082dc`, started 15:17:09 UTC. Every other container of the project kept its container, image, start time and restart count.
- **Result.** Quotes usable from 15:17:43 UTC; publication lag about 120 ms (1,152 ms before); no `QUEUE_OVERLOAD` since. The two-hour soak had 6,985 of 7,200 samples usable; the unusable ones came from two clock-check tear-downs, one run of REST budget waits and four short delivery stalls, not from publication.
- **The first form of the backup command** was refused by the coding client before it ran; nothing had been executed.

## ExecPlan 0022 commands — 2026-10-02

Results and limits are in [ExecPlan 0022](plans/0022-reference-checks-and-rest-budget.md#12-verification-isolated).

**One read-only query of the normal database,** with the owner's approval in chat ([DECISIONS](../DECISIONS.md#2026-10-02--execplan-0022-approved-for-implementation-clock-option-a-one-read-only-query)), at 19:57 UTC from Git Bash:

```bash
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on -c statement_timeout=15000" \
  adaptive-spot-lab-postgres-1 psql -U asl -d asl -At      # one SELECT inside BEGIN TRANSACTION READ ONLY
```

- The statement read the symbol, receipt time, size, top-level keys and `rateLimits` array of the two newest `market_payloads` rows with source `exchangeInfo`.
- Exit 0. Both answers, received at 19:00:42 UTC, carry `rateLimits` with `REQUEST_WEIGHT`, `MINUTE`, `intervalNum` 1 and `limit` 6000.
- No other command touched the normal `adaptive-spot-lab` project.

**Isolated acceptance, run `ref-1002b`,** from this worktree at commit `0eb208a`, on Windows PowerShell 5.1 against the Compose projects `asl-m2-ref-1002b-*` only. Synthetic data; no public endpoint was contacted.

```powershell
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Prepare
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Build
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Checks
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase WorkerFaults
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Regression
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase RecoveryMemory
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase PerformanceDensity -DensityLevels '1000000,1800000' -DensitySeconds 600 -ReferenceFaults
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase PerformanceBurst
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Snapshot
./tools/m2-acceptance.ps1 -RunId ref-1002b -Phase Stop
```

All exited 0 (21:17–22:17 UTC).
- **Snapshot.** Both snapshots record commit `0eb208aba5488cbf6cd15cf792f030243f76b524` and the same 375 source hashes.
- **Checks.** Web lint, typecheck, 49 unit tests, API-contract check, Ruff, OpenAPI check, format check and the production web build.
- **WorkerFaults.** 69 passed, none skipped: 43 before this plan, plus 26 cases of `tests/test_m2_reference_checks.py`.
- **Regression.** 421 passed, with the one pre-existing Starlette test-client deprecation warning.
- **RecoveryMemory.** 30 measured recoveries, 464 KiB settled RSS growth, 0 retained market tasks.
- **PerformanceDensity with reference faults.** No budget failure at either level. Four injected clock faults per level closed usability after 0.1–0.9 s and reopened it after 11.7–12.7 s, on one collection, with no unusable sample outside them. Receipt-to-publication p95 115.8 and 116.0 ms, p99 118.1 and 117.9 ms; every frame published; 16,000 observations deleted under the stream at the second level.
- **PerformanceBurst.** 30,000 of 30,000 published; p50 139.6 ms, p95 162.7 ms, p99 172.6 ms; schedule lag p99 2.0 ms; maximum RSS 72,552 KiB.

**Development run `ref-1002a`,** the same worktree before the commit: `Prepare`; then, with the run's own environment, `docker compose -p asl-m2-ref-1002a-engine --profile test build migrate engine-tests`, `up -d postgres`, `run --rm migrate` and `run --rm engine-tests uv run --frozen python -m pytest …` for the new tests and the worker-fault suites; `PerformanceDensity -DensityLevels '3000' -DensitySeconds 540 -ReferenceFaults` as a smoke run of the fault schedule; `Stop`.
- The three reproduction tests failed on the unchanged source at 20:03 UTC and passed after the change.
- The smoke run exited 1 on the retention minimum, which a 3,000-row level cannot meet. Its four faults closed and reopened as in the acceptance run.

**Unchanged-code run `ref-1002u`,** from a scratch `git worktree` of `dafc18d` that received only a copy of the new worker tests with the old imports and two direct checks: `Prepare`, the same build, database and `pytest` commands, then `docker compose -p asl-m2-ref-1002u-engine --profile test --profile tools down -v`, `docker image rm` for that run's two images, and `git worktree remove`.
- All 19 cases failed on the unchanged code. The two direct checks passed: a failed confirmation request ends the collection, and an empty answer raises an `IndexError`.
- Evidence is under `.cache/m2/ref-1002a/unchanged-code/`.

**Other isolated commands.** Relative documentation links: `docker run --rm --network none -v <worktree>:/repo:ro asl-m2-lag-1002d-engine-engine-tools python /repo/tools/check_links.py /repo`.

**Left in place, stopped.** The volumes and images of runs `ref-1002a` and `ref-1002b`: `asl-m2-ref-1002a-engine_postgres_data`, `asl-m2-ref-1002a-density_postgres_data`, `asl-m2-ref-1002b-engine_postgres_data`, `asl-m2-ref-1002b-density_postgres_data` (1.8 million synthetic rows) and `asl-m2-ref-1002b-performance_postgres_data`. Removing them is the owner's decision. **They were removed on 2026-10-03** on the owner's instruction ([Test-run cleanup](#test-run-cleanup--2026-10-03)).

## Verified ExecPlan 0022 normal deployment — 2026-10-03

Run with the owner's approval in chat ([DECISIONS](../DECISIONS.md#2026-10-03--market-worker-deployment-approved-execplan-0022)), 05:20–05:22 UTC, from the worktree at `60997d8` (source equal to the tested `0eb208a`) through Git Bash and Windows PowerShell 5.1. `<primary>` is the primary checkout, which stayed on `main` at `cd5a5e9`; its `.env` and secrets were passed to Compose and never read. The full record is in [ExecPlan 0022 §13.1](plans/0022-reference-checks-and-rest-budget.md#131-executed-2026-10-03-05200522-utc-owner-approved).

```bash
# Read-only state (before, after and during the soak), as for 0021
docker ps -a --filter label=com.docker.compose.project=adaptive-spot-lab
docker inspect <each container>            # image, start time, restart count, status
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on -c statement_timeout=15000" \
  adaptive-spot-lab-postgres-1 psql -U asl -d asl -At -f -      # SELECTs inside BEGIN TRANSACTION READ ONLY
docker logs --timestamps adaptive-spot-lab-market-worker-1
docker exec adaptive-spot-lab-market-worker-1 sh -c 'cd /app/app && sha256sum <changed files>; echo <four non-secret settings>'

# Protected backup (owner-only directory created first with tools/lib/Pilot.psm1 Protect-Path)
docker exec adaptive-spot-lab-postgres-1 pg_dump -U asl -d asl -Fc -f /tmp/reference-checks.dump
docker exec adaptive-spot-lab-postgres-1 sha256sum /tmp/reference-checks.dump
docker cp adaptive-spot-lab-postgres-1:/tmp/reference-checks.dump <primary>/.cache/deployments/reference-checks-20261003T052055Z/asl.dump
docker exec adaptive-spot-lab-postgres-1 sh -c 'unlink /tmp/reference-checks.dump'

# Rollback tag, build one image, confirm the tested source, recreate one service
docker tag sha256:0d6ac003d93358dd1041255a33bda93c1f307420da39a30083b0dc8bb99c74c9 adaptive-spot-lab-market-worker:pre-0022
docker compose -f compose.yaml -p adaptive-spot-lab --profile market build market-worker
docker run --rm --network none --entrypoint sh adaptive-spot-lab-market-worker:latest \
  -c "cd /app/app && find . -type f | sort | xargs sha256sum | sha256sum"
docker compose -f <primary>/compose.yaml -p adaptive-spot-lab --env-file <primary>/.env --profile market \
  up -d --no-deps --force-recreate --wait --wait-timeout 120 market-worker

# Soak (read-only, twice)
docker exec -e ASL_DB_ROLE=market_worker adaptive-spot-lab-market-worker-1 \
  python -m app.market_data.continuity_probe --seconds 3600
```

All exited 0, with three exceptions that changed nothing:
- Each probe hour exits 1 by design when it has seen any unusable sample.
- The first source check named the tested image `asl-m2-ref-1002b-engine-engine-tests` and failed with "can't cd to /app/app": that image keeps the source under `/workspace/services/engine/app`. The comparison used `asl-m2-ref-1002b-density-engine-tests` at that path.
- Two read-only `docker inspect` templates failed on the market worker, which reports no health state. They were rerun without that field.

Results:
- **Backup.** 282,957,442 bytes, SHA-256 `a491f820…b9cb`, equal inside the container and on the host.
- **Images.** Market worker `sha256:0d4d29bb4765…`, whose `/app/app` tree (103 files, `ba9dc949…9c65`) equals the tested image's. Rollback tag `:pre-0022` = `sha256:0d6ac003d933…`.
- **Containers.** Market worker `1becbec082dc` → `117df6d29bda`, started 05:22:21 UTC. Every other container of the project kept its container, image, start time and restart count, checked again at 07:27.
- **Result.** New quotes from 05:22:32 UTC; publication lag about 125 ms; the declared allowance of 6,000 read and logged; every completed clock sample traced.
- **Soak.** 7,169 of 7,200 samples usable. One routine clock failure cost 15 s and kept the collection; 16 SOL-only samples were stale while the provider published no SOL ticker. No `COLLECTION_GAP`, `QUEUE_OVERLOAD` or REST wait.

## Test-run cleanup — 2026-10-03

Run on the owner's instruction in chat ([DECISIONS](../DECISIONS.md#2026-10-03--test-volumes-and-images-of-the-0021-and-0022-runs-removed)), 07:56–08:02 UTC, from Git Bash. The removal named only the disposable volumes and images of runs `lag-1002a` to `lag-1002d`, `ref-1002a` and `ref-1002b`. No command named the normal `adaptive-spot-lab` project.

```bash
# What exists, and whether anything uses it (read-only; the output was filtered to the two run prefixes)
docker ps -a --format '{{.Names}}|{{.State}}|{{.Image}}|{{.Mounts}}'
docker volume ls --format '{{.Name}}'
docker network ls --format '{{.Name}}'
docker image ls --format '{{.Repository}}:{{.Tag}}|{{.ID}}|{{.Size}}'
docker system df -v                    # volume sizes and link counts

# Removal, by exact name from the recorded lists, never forced
docker volume rm <each of the 14 volumes>
docker image rm <each of the 65 images, as repository:tag>
```

- **Before.** No container of these runs in any state, and no network. 14 volumes, each with zero links, about 22.9 GB together: five density volumes of 4.19–4.32 GB and nine small ones. 65 images tagged `asl-m2-lag-1002a-…` to `asl-m2-lag-1002d-…`, `asl-m2-ref-1002a-…` and `asl-m2-ref-1002b-…`.
- **Result.** All 14 `docker volume rm` and all 65 `docker image rm` exited 0. Afterwards no volume, image, container or network with either prefix exists.
- **Shared layers stay.** An image was removed by its tag, without force, so a layer that another image still uses is kept. The image space freed was not measured.
- **Kept.** The runs' evidence files under `.cache/m2/` (logs and reports, not Docker resources).
- **Not touched.** The normal project, and the test volumes and images of every other run on the host, which the instruction did not cover.
- **Two things about the read-only checks.**
  - `docker system df -v` lists every volume on the host with its size, the normal project's included. It reads no data from them. It took several minutes.
  - A check that compared image identifiers across tags was still running when the removal started, and its result was not used. Removing by tag without force only untags an image that has another tag.
- **Consequence for the link check.** `asl-m2-lag-1002d-engine-engine-tools`, the image named in the 0021 and 0022 command records, is gone. Any engine tools image serves; this record's check used `asl-m2-continuity-0928a-engine-engine-tools`.

## Old test-run cleanup — 2026-10-03

Run on the owner's instruction in chat ([DECISIONS](../DECISIONS.md#2026-10-03--this-projects-old-test-runs-removed-other-projects-docker-resources-left-to-the-owner)), 08:08–08:38 UTC, from Git Bash. It removed the disposable volumes and images of **this project's** isolated test runs of M1 to M5. No command named the normal `adaptive-spot-lab` project.

```bash
# Inventory (read-only; saved to files and filtered by name)
docker ps -a --format '{{.Names}}|{{.State}}|{{.Image}}|{{.Label "com.docker.compose.project"}}'
docker volume ls --format '{{.Name}}|{{.Label "com.docker.compose.project"}}|{{.Label "com.docker.compose.volume"}}'
docker network ls --format '{{.Name}}|{{.Driver}}|{{.Label "com.docker.compose.project"}}'
docker image ls --format '{{.Repository}}:{{.Tag}}|{{.ID}}|{{.CreatedAt}}|{{.Size}}'
docker system df -v                 # sizes and link counts of every volume and image on the host
docker system df                    # totals, before and after

# Removal, one name at a time from the recorded lists, never forced, paced, only between HH:15 and HH:55 UTC
docker volume rm <each of the 188 volumes>
docker image rm <each of the 1,076 images, as repository:tag>
```

- **Scope.** Names starting `asl-m1-` to `asl-m5-`, `asl-m3dev`, `asl-refresh-` and `asl-rhf-`: the isolated Compose projects of the M1–M5 acceptance harnesses and three small development stacks. Every name on the host that starts with `asl-` was covered.
- **Before.** The only containers on the host were the nine of the normal app. The 188 volumes held 92.7 GB and none was attached to a container; no image on the list was used by a container; the newest was created on 2026-10-01. No network of these projects existed.
- **Result.** All 188 `docker volume rm` (08:15–08:19 UTC) and all 1,076 `docker image rm` (08:19–08:38 UTC) exited 0. Afterwards no volume, image or network starting with `asl-` exists.
- **Host totals** (`docker system df`): volumes 512 with 216.9 GB before, 324 with 124.2 GB after; images 1,398 with 47.0 GB before, 358 with 40.2 GB after. The nine containers were running before and after.
- **Kept.** The evidence files of every run under `.cache/` (logs, reports, manifests). The normal project with its volumes, images, rollback tags and networks. The `adaptive-spot-lab-test` images and volume and the `adaptive-spot-lab-pnpm-cache` volume. The build cache.
- **The exact list** was written before the removal to `.cache/cleanup/old-test-runs-20261003.md` in the worktree that ran it (not in Git).
- **Consequence.** Every earlier record that says a run's volumes or images were "retained" or "left in place" describes the state before this cleanup. No run's Docker resources remain; a rerun builds its images again. The documentation link check no longer has a run's tools image; it ran here in the base image the repository pins: `docker run --rm --network none -v <worktree>:/repo:ro python:3.13.11-slim-bookworm python /repo/tools/check_links.py /repo` (86 Markdown files, 0 broken links).
- **Read-only checks that are host-wide.** The four listing commands and `docker system df -v` report every project on the host, the normal one included. Their output was filtered by name. They read no data from any volume.

**The other projects' Docker resources: removed by the owner.** The owner then instructed the removal of everything on the host that is not this project. From the same inventory that was 320 volumes with 122.5 GB, 309 images and 135 networks, in the name families `m0-test-…`, `m1-test-…`, `m2-test-…`, `paper-trader…`, `signalbot…`, `crypto-signal-bot…` and `csb-phase0-…`, with 26 unattached anonymous volumes and 8 base images that this repository does not reference.

- **Not run by the implementer.** The coding client's safety check refused that removal as an irreversible deletion. The implementer wrote the exact names and a script into `.cache/cleanup/` of the same worktree (`other-projects-20261003.md`, three `other-*.txt` lists, `remove-other-projects.sh`) and ran the script only with `--dry-run`, which calls no Docker command.
- **Two forms did not start in the owner's PowerShell terminal** and removed nothing: a first PowerShell version (`running scripts is disabled on this system`), and `bash <script>`, which there is the WSL launcher (`execvpe(/bin/bash) failed`).
- **Run by the owner, 09:28:53–09:40:22 UTC:**

  ```powershell
  & "C:\Program Files\Git\bin\bash.exe" "<worktree>/.cache/cleanup/remove-other-projects.sh"
  ```

  The script calls `docker volume rm`, `docker image rm` and `docker network rm` once per listed name, never forced, and skips any name starting with `adaptive-spot-lab` or `asl-`. Its log: 320 volumes removed, 308 images removed and 1 "already gone", 135 networks removed, no failure, nothing skipped.
- **Verified by the implementer at 11:18 UTC (read-only listings and `docker system df`).**
  - Volumes: 4, all this project's (`adaptive-spot-lab_postgres_data`, `adaptive-spot-lab_codex_home`, `adaptive-spot-lab-test_postgres_data`, `adaptive-spot-lab-pnpm-cache`), 1.8 GB together.
  - Networks: the six of the normal project and Docker's three built-in ones.
  - Containers: the nine of the normal app, all running.
  - Images: 61 tagged ones: the 55 `adaptive-spot-lab…` images with their rollback tags, the five base and tool images this repository references, and one leftover (next point). `docker system df` counts 73 images with 9.6 GB, because it includes 15 untagged ones; they could not be attributed to a project and were left.
- **One image was not removed, and the script misreported it.** `testcontainers/ryuk:0.14.0` (4.8 MB) is stored under a tag-and-digest reference, so `docker image rm testcontainers/ryuk:0.14.0` answers "No such image". The script counts that answer as "already gone". The image is still there and can be removed by its ID, `7c1a8a9a47c7`. It belongs to no project on the host.
- **Not touched at that point:** the build cache, 52.7 GB, which all projects shared.

**Build cache pruned, 11:26–11:30 UTC, on the owner's instruction** ("prune the build cache"). Three steps, so that the deletions did not arrive at once beside the running pilot:

```bash
docker buildx prune -f --max-used-space 42gb
docker buildx prune -f --max-used-space 18gb
docker buildx prune -f
```

- All exited 0. `docker system df` showed the build cache at 1,833 records and 52.7 GB before, and at 123 records and 7.3 GB after. The first step removed about 24 GB, more than its limit asked for.
- The 7.3 GB that remain are shared with images that still exist.
- Images, volumes and containers were unchanged: 73 images, 4 volumes, and the nine containers of the normal app running before and after.
- Consequence: the next build of any image starts without cached layers and needs the network for its dependencies.
- Not checked: whether the three minutes of deletions affected the market worker. That needs a read-only command against the normal app, which was not asked for.

## M6 B0 — 2026-10-03 (in progress)

IMPLEMENTED authoring work only on `codex/m6-research-investigations`, based on the approved local plan branch `claude/m6-research-plan` at `b4438b9`. No application dependency, migration or normal Compose change. B0 is not accepted. The following are actual authoring commands/read operations; outputs are observations, not product acceptance.

| Commands / operations | Actual result |
|---|---|
| `Get-Content AGENTS.md`, `docs/AGENTS.md`, `services/engine/AGENTS.md`; ordered reads of STATUS, ExecPlan 0023, DECISIONS approval, README, PLANS, MIGRATION and named contracts | Read. Initial `main` lacked ExecPlan 0023; retrieved it from the approved local branch before proceeding. Nearest rules read before editing. Initial reads used the tool's default PowerShell 7.6.5; subsequent commands explicitly invoke Windows PowerShell 5.1 |
| `rg -n -i 'adaptive\|spot\|m6\|research'` on the memory registry | Exit 1, no relevant retained entry; no memory-derived implementation fact used |
| `git status --short`, `git branch --show-current`, `git log`, `git show`, `git diff --name-only 72ba76f HEAD -- services/engine/app/agents services/engine/app/execution services/engine/app/replay services/engine/alembic/versions/0007_m5_agent_runtime.py` | Initially clean `main` at `ed9fae3`; approved branch at `b4438b9`; no change in those plan-baseline source paths |
| `git switch -c codex/m6-research-investigations claude/m6-research-plan` | First attempt blocked by sandbox `.git/index.lock` access. With host access, exit 0; branch created. No commit, push, merge or PR yet |
| `rg --files -g AGENTS.md` and targeted `rg -n` / `Get-Content` reads of M5 acceptance, ExecPlan 0020, Compose, Dockerfiles, engine lockfile, agent schemas/definitions/worker, replay, evaluation migration and provider transport | Read-only discovery. Attempts to read `app/market_data/transport.py`, `app/replay/cli.py` and `app/replay/fixtures.py` reported missing files; actual implementations are `provider.py`, `run.py` and `app/execution/fixtures.py`. Missing-path errors were not successful checks |
| Official-document browser searches/opens for Structured Outputs, PostgreSQL 17, OWASP SSRF, Docker resources, chronological splits, GitHub releases/terms and the repository licenses | Pages read; [integration record](contracts/INTEGRATION_EVIDENCE.md#m6-b0-official-guidance--2026-10-03). No model/source API call or public release endpoint used by M6 runtime |
| `Get-CimInstance Win32_OperatingSystem` and `Get-PSDrive C` | CIM initially AccessDenied in sandbox; PSDrive did not provide a usable free-space figure. Host-authorized read-only CIM returned total visible 16,685,636 KiB and free 5,050,340 KiB. Combined drive formatting produced no disk measurement |
| `apply_patch` on the §8 named contracts, the two M6 scripts and these evidence records | IMPLEMENTED docs/scaffold. No runtime behavior verified by the edits |
| PowerShell parser (`[Management.Automation.Language.Parser]::ParseFile`) and byte checks on `tools/m6-acceptance.ps1`, `tools/m6-b0-observe.ps1` | VERIFIED no parse errors and no non-ASCII bytes, under Windows PowerShell 5.1 |
| `git diff --check` | Exit 0; autocrlf warning on RESEARCH_WORKFLOWS only, no whitespace error |

Actual repository script invocations use the executable `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive`. Before the owner's process-only bypass approval, local script execution was rejected by Windows policy; no script action occurred. After approval:

```powershell
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b0a -Phase Prepare
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b0a -Phase Snapshot
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b0a -Phase Build -Describe
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/m6-b0-observe.ps1 -RunId m6-b0a
powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File tools/m6-b0-observe.ps1 -RunId m6-b0a -Execute -ObserveSeconds 180 -IntervalSeconds 30
```

- `Prepare`: exit 0; eight isolated target layouts, no Docker or secrets.
- `Snapshot`: exit 0; `.cache/m6/m6-b0a/source-001.json`, source hashes only, no image evidence.
- `Build -Describe`: exit 0; prints the exact phase list and explicitly reports Build NOT_IMPLEMENTED; it does not run a build.
- Observer review mode: exit 0; prints full read-only scope and SQL; no Docker call.
- Executed observer: first sandbox attempt exit 1 at Docker pipe access, before any DB query. Repeated with owner-approved scope and host access, exit 0. `.cache/m6/m6-b0a/b0-observation-20261003T120500379Z/commands.jsonl` records each of the 25 actual Docker argv arrays, timestamps, outputs and exit codes (all 0); `summary.json` records six samples 12:05:00–12:08:01 UTC, zero differences across all nine normal container/image/start/restart identities. Query forced read-only, statement timeout 3 s and lock timeout 200 ms.
- PS5.1 `Get-Content` / `ConvertFrom-Json` / `Measure-Object` over that local observation journal: exit 0; available VM memory 6,052,900–6,101,636 KiB; the 12:05 report arrived 26.331392 s after HH:05. No loaded isolated phase ran. A baseline does not clear M6-OD4.

NOT RUN: isolated builds/tests/replay, v2 schema CLI/mock compatibility, loaded coexistence, narrower-window proof, B1–B9, deployment and activation. No command against the normal project beyond the approved read-only observer. No `.env`, repository secrets or runtime home was opened.

Subsequent B0 commands (actual, acceptance still pending):

| Command / operation | Actual result |
|---|---|
| .NET `New-Object IO.DriveInfo -ArgumentList 'C:\'`, selected capacity/free fields | Exit 0; 999,088,451,584 total and 553,867,051,008 available bytes |
| Further targeted reads of `tools/lib/Acceptance.psm1`, replay runner/scenarios, `tests/m3_performance.py`, current agent schema, runner invocation/testing fixtures, Dockerfiles and isolated-test Compose blocks | Read. The first `Get-Content tools/lib.ps1` exited 1 (missing path); the actual module was then read. A search named `tests/mock_provider.py`, which is absent; the actual `testing/mock_provider.py` was subsequently read |
| `tools/m6-b0-probe.ps1 -RunId m6-b0a -Phase Prepare` using the approved PS5.1 process-only bypass | Exit 0; standalone fixture Compose, new per-run fixture secrets and output directory. No Docker call |
| `tools/m6-b0-probe.ps1 -RunId m6-b0a -Phase Build` | First exit 1 before Docker started: `Get-Command docker` returned two application paths, producing an invalid process filename. Fixed discovery to the first `docker.exe`. Repeat exit 0: engine test build, pinned cluster image pull and selected image-ID read. All actual Docker argv/results are in `.cache/m6/m6-b0a/b0-probe/commands.jsonl` with separate stdout/stderr logs |
| Local read of the Build logs | OBSERVED dependency layers were cached, contrary to the supplied clean-cache assumption. This was not a cold build. Image ID `sha256:c6bf9e7c377022ee4742084bf3defab4a94f01b2c8ba375d825b7f6ca9318604`; a no-cache build is pending |
| `tools/m6-b0-probe.ps1 -RunId m6-b0a -Phase Replay` | In progress at this entry: isolated research-postgres start and fixture migration exited 0, then the unchanged M3 two-cycle synthetic density wrapper. No result claimed until its actual outcome is recorded |
| `tools/m6-b0-observe.ps1 -RunId m6-b0a -Execute -ObserveSeconds 180 -IntervalSeconds 30` during the isolated workload | Exit 0; seven samples, 28 Docker reads all exit 0, zero normal identity differences. Journal `.cache/m6/m6-b0a/b0-observation-20261003T121706655Z/`; available VM memory 5,995,600–6,169,940 KiB. No HH:05 boundary during this loaded sample |
| `docker.exe ps --filter label=com.docker.compose.project=asl-m6-m6-b0a-research --format '{{.ID}}'`, then `docker.exe stats --no-stream --format '{{json .}}'` for only those IDs | Exit 0; probe 64.43 MiB/768 MiB, cluster 650.5 MiB/1 GiB at this sample. This selected isolated query never enumerated the normal project |
| Forced-read-only metadata query through `docker.exe exec 13ef86b9a233 psql ... -d asl_m1_replay_m6_m6_b0a` at about 12:28 UTC | Exit 0; live isolated client sessions, no lock wait reported in the sample, market-table estimates about 1.815 million rows each, execution-step estimate 93,029. Estimates are not exact row counts. No query text, secret or financial row content read |
| `tools/m6-acceptance.ps1 -RunId m6-b0b -Phase Prepare`; `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Prepare` | Both exit 0; fresh isolated layout and fixture configuration with manifest hashes. No Docker operation |
| Repeated PS5.1 parser/ASCII and `git diff --check`; `Get-Content`/JSON summaries of local logs | Parser/ASCII and whitespace checks passed; only the known autocrlf warning. No acceptance gate passed by these authoring checks |
| Further official GitHub terms/API/rate-limit reads; `apply_patch` for B0 probe, schema preview/probe, measurement helper and evidence docs | OBSERVED documentation and IMPLEMENTED authoring helpers. The rights interpretation is explicitly INFERRED in INTEGRATION_EVIDENCE. B6 must recheck the preview against its actual runtime schema; no permission is granted by a schema preview |

Build-time registry/package/artifact downloads are application/tooling provisioning; the isolated runtime has no Internet route. No public source feed or real provider/model endpoint was invoked. Heavy isolated work remains sequential and within the original quiet-window rule. The B0 probe's separate phases are measurements, not substitutes for any §10 acceptance phase.

Further actual results, before the cutoff clarification:

| Command / operation | Actual result |
|---|---|
| Local JSON read of `m6-b0a/b0-probe/out/density-run1/report.json` and its UTC file timestamp | OBSERVED one completed seven-day synthetic report, load 338.3 s, written 12:29:07.7143076 UTC, fingerprint `18011c0e8d6eee05f76b7f99ca055a43798f4edf96b0392c2ececdf3d57f1198`. This does not supply the two-cycle wrapper's final timing/result |
| Filtered isolated `docker.exe ps` (project `asl-m6-m6-b0a-research`, service `research-probe`), then `docker.exe stop --time 15 e7578683cdc3` | Exit 0; intentionally canceled second cycle before the wrapper's bound. Deprecated `--time` warning; later commands use `--timeout`. The parent Replay invocation returned exit 1, with child exit 143 and `timed_out=false`. The series is incomplete, not passed |
| Filtered isolated `docker.exe ps` for the same project's `research-postgres`, then `docker.exe stop --timeout 15 13ef86b9a233` | Exit 0; fixture cluster stopped, volume retained. No normal service operation |
| `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Build -NoCache` | Exit 0: base engine test image, measurement image, pinned cluster pull and image-ID read. The application dependency/build steps executed without cached layers; the Python base image was reused. Engine image `sha256:56992cf506791dd0305e640e9c3c673edf74a59cac1b7eb07d29d06dbd527426`. Per-command timestamps/argv/results in the run's `commands.jsonl` |
| `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Schema` | Exit 0: pinned CLI test build, preview build, network-none mock probe. CLI 0.159.2; both gpt-6.1-sol/gpt-5.6-sol paths exit 0, strict schema transmitted unchanged, valid synthetic output, zero native tools/credentials. Preview SHA-256 `6df12a6e…37a06c`. CLI warnings say temporary helper aliases were refused; they did not prevent the mock probe. No real settings home or login used |
| `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Replay` | Exit 1: cluster start and fixture migration exited 0; the actual replay was NOT RUN because the 15-minute reservation did not fit before HH:54. The guard did not use the unverified narrow window |
| `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Stop` | Exit 0; idle fixture services stopped, volume retained |
| `tools/m6-b0-observe.ps1 -RunId m6-b0b -Execute -ObserveSeconds 1900 -IntervalSeconds 60` | Started with the unchanged owner-approved scope for the post-load HH:05 comparison. Subsequently stopped for the cutoff clarification before HH:05; native session exit 1. The partial journal records 62 Docker commands, all exit 0, 19 memory samples, first/last command 12:39:11/12:58:00 UTC. Final identity and HH:05 comparisons NOT RUN; `interrupted.json` records the incomplete outcome |
| `tools/m6/b0/stage-docs.ps1 -RunId m6-b0b` | Exit 0; 86 Markdown files allowlisted from Git, no private contents, non-Markdown references copied as existence markers only; `.cache/m6/m6-b0b/docs-20261003T124108035Z/staging.json` |
| `docker.exe run --rm --network none --read-only --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true --tmpfs /tmp:rw,size=67108864 --label com.docker.compose.project=asl-m6-m6-b0b-engine -e PYTHONDONTWRITEBYTECODE=1 -e UV_NO_CACHE=1 --mount type=bind,source=<that staged directory>,target=/docs,readonly asl-m6-m6-b0b-research-research-probe uv run --frozen --no-sync python /docs/check_links.py /docs` | Exit 0; 86 Markdown files, zero broken links; four warnings for the known historical Windows absolute links. No repository/home/secret mount and no external link fetch |
| Targeted `rg -n` and UTF-8 reads of §5.5/R11, §5.8 and time-scoped-read contracts; `git diff --check` | OBSERVED the own-refresh completion versus research-cutoff conflict, and its possible follow-on context path. Whitespace check passed. The owner was asked to clarify; no exception implemented and B1 has not started |

NOT RUN at the hold: complete single-cycle timing/size measurement, narrow-window proof, actual v2 runtime schema, B1–B9 acceptance, PR creation, deployment and activation. No research-envelope value has changed.

Cleanup and hold record (actual):
- Read-only Windows `Get-CimInstance` queries filtered by the observer's native executable/script/run/duration, followed by guarded `Stop-Process` on that authoring helper only. First attempt safely refused two matches (the query helper also matched); a second WQL `NOT LIKE` query was invalid and stopped nothing despite the shell's exit 0; a third safely refused a UTC/local date comparison. A metadata-only check confirmed PID 26088, exact native arguments and creation `2026-10-03T12:39:10.5699610Z`. With both date bounds normalized to UTC, `Stop-Process` exited 0 and the observer session ended with exit 1. No Docker service was stopped by these process commands.
- PS5.1 parsing and ASCII checks on all four new `.ps1` files: zero errors/non-ASCII bytes. `git diff --check` and source status checks exit 0 (known autocrlf warning only).
- Local JSON/`Measure-Object` summary of the interrupted journal: exit 0, 62 recorded commands with zero nonzero exits, available memory 6,039,040–6,171,416 KiB. This was post-load sampling, not a completed quiet-window comparison. All isolated fixture services and the observer are stopped; no volume removed.
- Two bounded PS5.1 `Get-Content` reads of STATUS, the B0 evidence/command record and the cutoff clauses: both exit 0. The first used the default text encoding and rendered UTF-8 punctuation incorrectly; the second used `-Encoding UTF8` and confirmed the unresolved conflict at ExecPlan §5.8 and AGENT_TOOL_CONTRACTS' time-scoped reads. These were file reads only; no additional Docker command or measurement ran. This record-only edit does not resolve the conflict.

### B0 resumed at 16:13 UTC (actual; incomplete until outcomes recorded)

| Command / operation | Actual result |
|---|---|
| PS5.1 UTC time, bounded UTF-8 reads of root/docs/engine AGENTS, B0 scripts, plan §§3/5/6/9/10/16 and named cutoff contracts; targeted `rg`, `git status --short` | Exit 0. Reconfirmed the original heavy window, 1-CPU research limits and ordered B0 gates. No product code changed |
| `apply_patch` adding whole-phase window preflight and timestamped per-command probe logs | IMPLEMENTED harness fixes. PS5.1 parser/ASCII checks exit 0; no dependency or protection changed |
| `tools/m6-b0-observe.ps1 -RunId m6-b0b -Execute -ObserveSeconds 3300 -IntervalSeconds 60` | Started at 16:14:41 UTC with existing chat approval. Journal `b0-observation-20261003T161441677Z`; completion pending. No result claimed yet |
| `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Replay` at 16:15 UTC | Setup/migration exit 0; measurement child exit 2 before replay: uv could not create its temporary lock under the read-only `/root/.cache/uv`. Parent exit 1; no timing gate passed |
| Local UTF-8 read of that command's journal/stdout/stderr; `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Stop` | Log read exit 0. Stop exit 0, fixture volume retained |
| Engine Dockerfile read and `rg` for uv cache configuration | Dockerfile read succeeded; `rg` exit 1 (no existing cache-path setting). This was discovery, not a passed test |
| `apply_patch` confining uv cache to `/tmp/uv-cache`; PS5.1 parser/ASCII; `tools/m6-b0-probe.ps1 -RunId m6-b0b -Phase Replay` | Parse/ASCII passed; setup/migration exit 0. Single-cycle measurement running. Read-only root, internal network and declared resource limits retained |
| Initial multi-file evidence patch | Failed validation against a whole-line plan paragraph; no file changed. Corrected patch subsequently applied |
| Owner async question and reply; contract/evidence patches | OBSERVED explicit approval of the cutoff clarification. IMPLEMENTED plan, DECISIONS, AGENT_TOOL_CONTRACTS, RESEARCH_WORKFLOWS, RUNTIME_AGENTS, TESTING and STATUS amendments. Product behavior NOT RUN |
| Local JSON extraction of observer baseline metadata | First attempt exit 1 because SELECT JSON spanned several output lines. Corrected by joining all lines: exit 0. Report offsets 14:05 27.782870 s, 15:05 28.607944 s, 16:05 29.355027 s. This reads only the local approved observation journal |

All script invocations continue using the owner-approved process-only PS5.1 bypass. The observer is a bounded read-only process; it is not a second heavy phase. Actual Docker argv, times and outputs are retained in each run's journal. The completed loaded comparison and research-rate/store measurements are still pending.

- PS5.1 child invocations of unimplemented `Report` and invalid `RunId '../normal'`: both exit 1 as required; parent verification exit 0. The Report artifact says `NOT_IMPLEMENTED`. No Docker call or acceptance occurred. `git diff --check` exit 0, known autocrlf warning only.
- Bounded UTF-8 source reads at the plan's agent/migration and engine/replay line ranges: exit 0; allowlisted source/hash evidence retained in `b0-source-facts-20261003T162025522Z.json` and `b0-engine-facts-20261003T162119994Z.json` under `m6-b0b`. The reference bindings, immutable cutoff, registry refusals and replay prefix guard match the stated baseline. No statement about runtime parity is made.
- Local observer/probe journal reads and selected JSON summaries while the sample runs: exit 0. At 16:21 UTC there were seven memory samples, 6,033,600–6,144,036 KiB available and zero nonzero exits among 26 observer commands. These are interim samples, not the complete resource gate. Tools session polls report the measurement still running.
- Contract/testing/plan record patches after the explicit cutoff answer: IMPLEMENTED clarification and required late-content cases. The release-source paragraph now states optional release update time and links the completed rights review; the unselected status feed remains unreviewed. No source was fetched or approved.
- B0 path guards extended to existing ancestor directories in the scaffold, observer, probe and staging helper; probe cleanup added for replay errors. IMPLEMENTED authoring safety changes only. Repeated PS5.1 parser/ASCII checks on all four scripts and `git diff --check` exit 0. `Snapshot` produced `source-001.json` and `source-002.json` in `m6-b0b`, retaining both. The running observer/replay began before these final path/cleanup edits; they retain their original loaded script behavior.
- Bounded integration-evidence and remaining code-fact reads, local journal inspection and tool-session polls: exit 0 for reads; the measurement still running at 16:27 UTC. Clock reads and a 40-second authoring wait performed no application operation. No timing result inferred from elapsed waiting time.
- Read-only host CIM/DriveInfo during the loaded sample, exit 0: at 16:28:35 UTC free physical memory 1,396,180 KiB; C: available 551,357,804,544 bytes. Retained `b0-host-20261003T162835908Z.json`; its exact name was subsequently confirmed by a bounded directory-metadata read.
- Resumed `Replay` completed: parent exit 0. Native density command 16:16:01–16:28:40 UTC, exit 0; helper `b0-replay-20261003T161602Z.json` records replay 402.68 s, load 340.47 s, cycle 756.763 s, 1,815,038 publications and 1,209,600 synthetic quotes. Fingerprint/trace match the earlier native report. Candidate/M4 research job throughput NOT RUN. Selected size/df/stop commands all exit 0: DB 2,292,979,379 bytes, data filesystem available 978,972,244 KiB; cluster stopped 16:28:43 UTC, volume retained.
- Local PowerShell sizing calculation succeeded: 57.5257 replay seconds/day; two scenarios at 42 days project to 4,832.16 s versus the unchanged 3,600-s job bound; at 21 days 2,416.08 s. 49-day database projection 16,050,855,653 bytes; 25% reserve rounded to 20 GiB. `rg` on other contracts found no duplicated numeric bounds (exit 1, not a check failure). Implemented the permitted B0 sizing in §5.5 and its configuration pointer; no other envelope value changed. A first patch included an incorrect CONFIGURATION heading and failed atomically; the corrected patch applied.
- Bounded `run.report` source/JSON reads: exit 0, native fixture summary has no experiment entry, so no M4 FINAL was generated in this density sample. Full future candidate/M4 result acceptance remains required. `git diff --stat` exit 0, known autocrlf warning only.
- Bounded contract/diff reads (including two independent calls with `Promise.allSettled`) exit 0; long diff outputs were truncated and relevant sections were then read directly. Corrected section placement of two existing M5 operations bullets; reconciled the general research-tool/lifecycle text with M6's screening-only request, SYSTEM full-test/shadow schedule and no MAIN_APPROVED state. These apply the approved plan, not new permissions.
- `stage-docs.ps1 -RunId m6-b0b` exit 0: `docs-20261003T164320192Z`, 86 Markdown files. The explicit network-none, read-only, 0.5-CPU/256-MiB/64-PID Docker link check using the existing isolated engine test image, only that staged mount, `/tmp` cache and no-new-privileges exited 0: zero broken links and four known historical Windows-link warnings. `git diff --check` exit 0. Subsequent record-only/contract wording edits still need their final snapshot check.
- Continued local observer JSON summaries and clock reads: exit 0. At 16:47 UTC there were 32 samples, 101 successful Docker reads, available VM memory 5,729,200–6,178,500 KiB; observer still incomplete. The plan's risk text now states the arithmetic consequence of the measured 21-day cap (20% partitions at most 100.8 hours before gaps) rather than implying that simply collecting five weeks removes insufficiency under that cap.

### B0 completion at 17:15 UTC (actual)

- Clock reads, session polls and bounded UTF-8 reads of AGENTS, STATUS, plan, harness, integration evidence, current agent definitions/dispatcher and local journals: actual file/clock reads succeeded. Observer session `62355` completed exit 0 at 17:09:44 UTC. Its original `commands.jsonl` records every Docker argv, output and exit code: 169 reads, all 0; 54 samples; all nine container/image/start/restart identities unchanged. No additional normal-app Docker command was issued.
- PS5.1 local journal aggregation and validation, exit 0: all schemas `0007_m5_agent_runtime`; available VM memory 5,729,200–6,178,500 KiB. Docker's rounded normal-container memory samples sum to approximately 1.45–1.59 GB. As-of 17:00 report created 17:05:30.318837 UTC, same pilot/generator, +0.963810 s offset from the preceding report. Recorded `.cache/m6/m6-b0b/b0-measurement-summary.json`, SHA-256 `3be4063fa81c83bdfd9c9e0426c8d252a1202f8c87d1a7120d3feef71a893b7a`. It binds observer-summary SHA-256 `8e3512fc8287189925d6f989be3b576620dae22bf42550796c21e60fe3535df0` and journal SHA-256 `ff848165a61b59b0859664d6361466538067dab8208d3dc6f0463840799928d0`. The sample ran 16:16–16:28, not during HH:05; no unchanged-millisecond-latency claim.
- First multi-file evidence/window patch failed validation against the plan's whole-line status paragraph; no file changed. Corrected patches applied. The conditional M6-OD4 gate is recorded, with the authoring harness enforcing HH:07–HH:58 and the B0 probe retaining a one-minute finishing reserve. Corrected an overly restrictive B0 lifecycle sentence to preserve the plan's defined-but-unreachable MAIN_APPROVED value. This restores the exact approved design; it does not make a transition reachable.
- PS5.1 AST parsing/ASCII over all four scripts and twelve heavy-window boundary cases: passed. `git diff --check` passed, known autocrlf warning only. That invocation's final `rg` used absent `services/engine/app/agents/registry.py`, so the shell exited 1 after the preceding checks passed. Corrected targeted `rg` under `app/agents`, followed by bounded reads of the actual `definitions.py` and `dispatcher.py`, exit 0: all four prohibited tools remain absent from the catalog and authorization rejects unknown names. This is observed source, not a new runtime permission test.
- `tools/m6-acceptance.ps1 -RunId m6-b0b -Phase Snapshot` and `tools/m6/b0/stage-docs.ps1 -RunId m6-b0b`, approved process-only PS5.1 bypass: exit 0. Retained `source-003.json` and `docs-20261003T171441044Z` (86 Markdown files).
- `docker.exe run --rm --network none --read-only --cpus 0.5 --memory 256m --pids-limit 64 --cap-drop ALL --security-opt no-new-privileges:true --tmpfs /tmp:rw,size=67108864 --label com.docker.compose.project=asl-m6-m6-b0b-engine -e PYTHONDONTWRITEBYTECODE=1 -e UV_NO_CACHE=1 -e UV_CACHE_DIR=/tmp/uv-cache --mount type=bind,source=<that staged directory>,target=/docs,readonly asl-m6-m6-b0b-research-research-probe uv run --frozen --no-sync python /docs/check_links.py /docs`: exit 0, zero broken links, four known historical Windows-link warnings. Only staged documentation was mounted.

VERIFIED B0 complete within its contract/scaffold/measurement scope. NOT RUN: B1–B9 product implementation, actual runtime v2 schema comparison, candidate/shadow throughput, every §10 acceptance phase and Q01–Q10, public source fetches, real model calls, PR creation, B10 deployment and B11 activation. The latter runtime/public/activation actions are excluded or owner-gated, not B0 tests. No further B0 decision is pending.

### B1 authoring (actual; verification NOT RUN)

- Bounded UTF-8 reads of engine AGENTS, PLANS, ExecPlan requirements/design/batch order, 0007, existing schema tests/support, Dockerfile, DB/identity helpers and M5 harness/module: read. First migration read used missing `services/engine/migrations/versions/0007_m5_agent_runtime.py` and exited 1; `rg --files` found the actual `alembic/versions` file, then it was read. One three-call independent-read batch exceeded the combined output allowance; relevant bounded sections were re-read. No mutation or runtime result arose from those reads.
- `apply_patch`: IMPLEMENTED `app/research` definitions/migration-retry helper, frozen migration 0008, test support/schema tests and `tools/m6/isolation.psm1`. Corrected two draft guard expressions during source review (exact owner-template pairs and trigger-table-specific field access). Source-read discovery confirmed published confirmation payloads need inclusion in the staging views; added that dependency. Added inert-role reuse for successive working databases in one research cluster. No new dependency.
- Targeted `rg` discovery named missing `app/experiments/pilot_fixture.py` and later `app/experiments/identity.py`; both reported missing paths while finding the other requested symbols. Subsequent `rg --files` confirmed the real fixture locations; M5's actual pilot setup uses `app.execution.identity` and the test feed. These are discovery errors, not test results. Reads of 0004, 0007's immutable trigger, Alembic env, pyproject and `.dockerignore` confirmed collection/confirmation columns, transaction scope and private-file build exclusions.
- Clock reads and `git diff --stat` succeeded (known autocrlf warning only). Contract/plan patches record the draft implementation and preserve B0's completed evidence. No B1 Docker call has run.

NOT RUN: all B1 checks; no acceptance claim. The normal pilot and runtime were not addressed.

### B1 isolated preflight (actual, 2026-10-03)

The preceding authoring record describes the state before these calls. All script calls below used the owner-approved process-only Windows PowerShell 5.1 bypass. Only standalone `asl-m6-m6-b1a-*` projects and freshly generated fixture secrets were addressed; no normal-app command ran. Exact Docker arguments, start/completion times, exit codes and stdout/stderr paths are retained in `.cache/m6/m6-b1a/commands.jsonl`.

| Actual command | Actual result |
|---|---|
| `tools/m6-acceptance.ps1 -RunId m6-b1a -Phase Prepare`, then `-Phase Snapshot` | Exit 0 each; eight fresh internal-only targets, manifest v2 and `source-001.json`. No Docker call in these two phases |
| PS5.1 parse/ASCII check for the harness/module; `git diff --check` | Exit 0; known autocrlf warning only |
| `tools/m6-acceptance.ps1 -RunId m6-b1a -Phase Build` | Exit 0, 9.6859 s observed. B1 engine image only; image inspect exit 0; two schema static tests passed, nine deselected. `Build-b1.json` explicitly says PARTIAL; full Build acceptance NOT RUN |
| Guarded isolated `engine-tests` Ruff preflight on `app/research`, migration 0008 and the two M6 test files | Exit 1: E731 for a local lambda and two I001 import-order errors. All three corrected with `apply_patch`; no schema/authority change |
| Repeated `-Phase Build`, 17:46 UTC | Exit 0; engine build, own-image inspect and the same two static tests exit 0 |
| Guarded isolated Ruff recheck, 17:47 UTC | Exit 0: `All checks passed!` |
| Single-lock, five-minute-window-reserved preflight: isolated `fixture-postgres up -d --wait --wait-timeout 60` | Exit 0 at 17:48:07 UTC; only `asl-m6-m6-b1a-engine` / `asl_m1_m6_m6_b1a_engine` |
| Same preflight: `engine-tests .venv/bin/python -m app.research.migrate` | Exit 1 at 17:48:11 UTC: `psycopg.errors.RaiseException: seeded definition hash mismatch` in 0008's post-seed check. No acceptance claim; transaction failed |
| Preflight `finally`: isolated `stop --timeout 15` | Exit 0 at 17:48:12 UTC; volumes retained; heavy lock released |
| Local journal/error-log reads | Initial double-quoted shell read expanded a PowerShell variable and reported missing `\\.FullName`; corrected single-quoted PS5.1 command read the exact logs, exit 0. No secret content was read |
| Bounded source reads of 0008 seed INSERT and the 0007 precedent | Exit 0. INFERRED cause: one new bind parameter is shared by the JSONB and canonical-text columns; 0007 binds those separately. This is a diagnosis, not a verified fix |
| Owner question after the failed gate | Requested approval for separating those new parameters and rerunning the isolated checks under the explicit stop-on-gate-failure rule. Answer pending at this record |
| Evidence/STATUS/progress patches; final PS5.1 parser/ASCII and `git diff --check` | Records updated while dependent work is held; both script/module checks passed, diff check exit 0 with the known autocrlf warning |

NOT RUN: database schema/role tests (the preflight stopped before pytest), populated migration, concurrent-writer/lock sampling, dump/restore, and full `Migration` acceptance. B1 remains incomplete; B2-B9 have not started. B0 remains VERIFIED complete. The proposed correction would preserve canonical bytes, hashes, envelope values and permissions.

### M6 checkpoint publication requested by the owner (2026-10-03)

- OBSERVED owner instruction: `push changes to main`. See [the decision record](../DECISIONS.md#2026-10-03--owner-requests-the-current-m6-checkpoint-on-main). The current B1 failure and NOT RUN checks remain visible; no migration correction or runtime operation is included in this publishing task.
- Windows PowerShell 5.1 reads of root/docs instructions, current STATUS/DECISIONS, `git status --short`, `git branch -vv`, `git remote -v`, `git log -5 --oneline`, `git diff --stat` and `git ls-files --others --exclude-standard`: exit 0. Current branch `codex/m6-research-investigations`, original HEAD `b4438b9`; pending changes are the M6 docs, engine draft and harness files only.
- `git fetch origin main`: exit 0. `git log --oneline --left-right HEAD...origin/main` and `git diff --name-status HEAD...origin/main`: exit 0; remote main is `4c10142`, carrying eleven commits after the shared M6 plan branch head, including the merged plan and cleanup records. Read remote AGENTS and relevant contract diffs before integration; existing records will be preserved.
- `git diff --check`: exit 0, known autocrlf warning only.
- PROPOSED next commands: stage the named M6 files, commit the current checkpoint, integrate `origin/main` without force, record and verify the result, then push `HEAD:main`. The commit/merge/push are NOT RUN at this entry. No Docker command or additional product test ran in this publishing task.
- OBSERVED first explicit-path `git add` succeeded, but `git diff --cached --check` failed for one extra blank line at EOF in three newly staged files (migration 0008, its schema test, and the isolation module); the wrapper exited 1 before commit. A first whitespace patch did not match and changed nothing. After reading the engine instructions and exact file endings, removed only those extra EOF blank lines with PS5.1; working-tree `git diff --check` exit 0. This does not repair or rerun the failed B1 migration.
- VERIFIED repeated explicit-path staging and staged whitespace check exit 0; `git commit -m 'WIP: record M6 B0 completion and B1 migration preflight failure'` exit 0, commit `2d17dff`, 36 files. Only source, contracts and harness files were staged; no cache or secret path.
- OBSERVED `git merge --no-ff --no-commit origin/main` exit 1 with append conflicts in COMMANDS, DECISIONS and ExecPlan 0023. Read the incoming root instructions and contract changes. Resolved each append conflict by retaining both sets of records, placing the earlier cleanup records before the M6 implementation records; no source-code conflict. `git diff --check` then exit 0. A broad conflict read exceeded the output allowance; the current branch's M6 records had already been read and the incoming contract/cleanup records were inspected directly.
- IMPLEMENTED integration of the standing cleanup policy and its planned `Clean` phase. NOT RUN: Docker cleanup and `Clean` implementation in this publishing checkpoint. The ongoing M6 task remains held at the B1 failure; this checkpoint does not claim completed M6-A or deployment. Historical B0 records retain their original observed stopped/retained state.
- VERIFIED resolved-document staging and `git diff --cached --check` exit 0; merge commit `8f2a120` created, `git merge-base --is-ancestor origin/main HEAD` exit 0, working tree clean. `git push origin HEAD:main` exit 0: remote main advanced without force from `4c10142` to `8f2a120`. This entry records that actual push; a documentation-only follow-up carries the publication record. No Docker command, migration, activation or product test ran for publication.

### M6 B1 continuation (2026-10-03)

- OBSERVED owner instruction `go ahead with b1`; the scoped correction and isolated rerun are authorized ([decision](../DECISIONS.md#2026-10-03--continue-m6-b1-after-the-migration-preflight-failure)). No unresolved approval blocks this correction.
- Windows PowerShell 5.1 ordered reads of root/docs/engine AGENTS, STATUS, ExecPlan 0023 requirements and B1 design, DECISIONS approval, README/PLANS and the M5 migration precedent; `git status --short`, branch/log and targeted source searches: exit 0. Clean branch `codex/m6-research-investigations` at `9241034`. Long combined outputs were bounded again where needed. Clock: 21:21:56 UTC at the start; heavy work must finish before HH:58.
- IMPLEMENTED the authorized bind separation in 0008 and synthetic M6 fixture INSERTs. The frozen seed serializer now explicitly uses the same ASCII canonical convention as the existing code. Intended seed bytes/hashes and envelope values are unchanged; the repeated static and real-database comparisons are NOT RUN at this entry.
- VERIFIED `tools/m6-acceptance.ps1 -RunId m6-b1a -Phase Build` exit 0; own-image build/inspect and both static checks passed. The bounded five-minute, single-lock rerun on `asl-m6-m6-b1a-engine` then passed database start, `app.research.migrate`, all **11 schema tests** (4.96 s, three Alembic `path_separator` deprecation warnings, no skip), and exact fixture stop; all exits 0. Native arguments/results remain in this run's `commands.jsonl`.
- IMPLEMENTED additional completion binding/reference/immutability cases and a full sixteen-table synthetic catalog fixture; the populated migration helper, old-image-only fixture services, bounded lock retry exercise, dynamic lock sampling, dump/restore checks, exact-name cleanup inventory and harness phases. Test-only recovery databases use the compatible `asl_m1_m5_m6_` namespace; normal and research-runner namespaces are unchanged. No dependency added.
- PS5.1 parser/ASCII checks on the acceptance script and the isolation/migration/cleanup modules: all passed. `git diff --check`: exit 0, autocrlf warnings only. Further bounded source reads of M5 fixture helpers, old-worker Compose blocks, M6 guards and cleanup rules succeeded; no original secret content was read.
- OBSERVED fresh `m6-b1b -Phase Prepare` first exit 1 before Docker or secret generation: nested forced module import removed `Initialize-M6Target` from the parent scope. Removed `-Force` from the child imports; repeated Prepare and Snapshot exit 0, manifest v3 and `source-001.json` retained.
- OBSERVED first `m6-b1b -Phase Build`: image build/inspect and two static tests passed, Ruff exit 1 with seven B023 closure findings in the new lock-retry helper. Bound the loop variables explicitly; repeated Build exit 0, including Ruff. Full Build remains PARTIAL, limited to B1's engine image.
- OBSERVED `tools/m6-acceptance.ps1 -RunId m6-b1b -Phase Migration`, 21:38-21:40 UTC: exit 1 at the final restore structure comparison. All 17 schema tests passed (17.04 s, three existing Alembic configuration warnings, no skip). Populated static upgrade/downgrade/reupgrade, bounded lock retries, concurrent old-image fixture workers, live migration lock sampling, unchanged container identities/lease, advancing checkpoint and worker-log checks passed. Every recorded native command exited 0; the PowerShell assertion then failed. The `finally` stop completed successfully at 21:40:55 UTC.
- VERIFIED offline comparison of the saved pre-dump/restored snapshots: all legacy row counts/hashes match (`130bb486dfcfd53db570b91a9d2efe398284c5ca6b38f06ed63e57f94658670f`), all sixteen M6 table counts/hashes match (`e81f3759dcc76f90bc6d266f25c4eed6d4257b1562b500114d882fca8ea12fb3`), and both revisions are 0008. OBSERVED protected-structure hashes differ: `b0e2d52d15f51c5d37de253d353dab1c187e4123463f75cf8b555b28becf50f0` versus `727efc79aa2e2f0d8a921f507e5b2a0a85921d9c6dc4dacfd498a33748017b6b`. Cause is not yet established. Requested owner approval under the explicit stop-on-gate-failure rule for isolated schema diagnosis and a harness-only correction if representation caused the difference. Any actual protected-schema change remains blocked.
- NOT RUN after that assertion: restored populated downgrade refusal, restored accounting invariants and final Migration acceptance. The latest failed run is stopped and retained for diagnosis under the cleanup policy.
- Local PS5.1 source/evidence reads and compact saved-fingerprint comparison succeeded. Two reads referenced a nonexistent root `tests/m6_migration.py` / engine-test AGENTS path and exited 1; the actual helper is under `services/engine/tests`, governed by engine AGENTS. Some combined output exceeded the display allowance; relevant details were reread in bounded form. No protected path was read.
- OBSERVED `tools/m6-acceptance.ps1 -RunId m6-b0a -Phase Clean`: exit 1 during the first existing container's metadata inspection, before any deletion. The new PowerShell helper turned its one-element `inspect` array into a scalar, concatenating `inspect--format`; Docker rejected that command. All preceding exact-project inventory reads exited 0. Evidence remains intact; no cleanup pass is claimed.
- IMPLEMENTED the cleanup argument fix with an explicitly typed string array. Added absolute per-phase Docker command deadlines (Build/Clean four minutes, Migration twelve plus three minutes reserved for stops), keeping bounded emergency stops available after the work deadline. PS5.1 parser/ASCII checks for all four files, a no-Docker expired-deadline refusal check, the exact argument-array check and `git diff --check` passed. Build/Migration must be rerun with this changed harness before B1 acceptance; no deadline behavior is claimed from the earlier Migration run.
- VERIFIED repeated `-RunId m6-b0a -Phase Clean` exit 0 at 21:46:15 UTC: 4 resources removed (one container, network, volume and image). Sequential `m6-b0b -Phase Clean` exit 0 at 21:46:36 UTC: 7 resources (one container/network/volume, four images). Sequential `m6-b1a -Phase Clean` exit 0 at 21:47:15 UTC: 4 resources (one of each). Each exact-name inventory was saved before deletion and empty project inventories/owned image absence verified afterwards. Expected `No such image` inspection exits are recorded as absence, not successful Docker calls. Every `.cache` evidence file, base/tool image and borrowed pilot image is retained. No normal-project command ran. Latest failed `m6-b1b` alone stays stopped for diagnosis.
- Saved live-migration evidence: 0.507470865995856 s, one attempt, 58 lock samples including 39 observing migration locks; no protected relation exceeded AccessShare. The isolated forward checkpoint advanced 652 to 696 on lease epoch 2, with identical pilot event/incident counts and container/image/start/restart identities. These are synthetic fixture observations, not a normal-pilot check or a completed Migration phase.
- Further bounded PS5.1 reads of actual helper paths, rules and saved evidence succeeded. One guessed documentation-staging path did not exist; `rg --files tools` located and the next read confirmed `tools/m6/b0/stage-docs.ps1`. Clean summary reads confirmed all three VERIFIED results/counts. Status and plan evidence were reconciled with the current restore failure and cleanup results; no protected schema or envelope was changed.
- VERIFIED `tools/m6/b0/stage-docs.ps1 -RunId m6-b1b` and the logged `b1-docs` Docker command exit 0 at 21:49 UTC: 86 staged Markdown files, zero broken links, four known historical Windows-path warnings. The named test container used `--network none`, bounded resources, a read-only root and only the staged documentation mount; `--rm` removed it. The exact native arguments/results are retained in `m6-b1b/commands.jsonl`.
- VERIFIED final local PS5.1 parser/ASCII checks on the four harness files and `git diff --check`: exit 0 (known autocrlf warnings only). `tools/m6-acceptance.ps1 -RunId m6-b1b -Phase Snapshot` exit 0, retaining `source-002.json` before this final command-record append. `git status --short` lists only the named B1 source/harness/docs changes; no cache or secret is staged. No new commit, push, PR, deployment or activation ran in this continuation. Approval for the restored-schema diagnosis remains pending; dependent work is held.

### M6 B1 restore diagnosis and final rerun (2026-10-03)

- OBSERVED owner instruction `don't stop until complete it`, approving the pending isolated diagnosis, representation-only harness correction and B1 completion. Recorded in DECISIONS; no renewed approval is needed for this same work. No normal-app command, protected-table change, envelope change or activation is authorized.
- PS5.1 reads of current root/docs/engine AGENTS, STATUS, plan B1 requirements, DECISIONS, README/PLANS, relevant testing/data contracts and `git status --short`: exit 0. Start clock 21:50:40 UTC. Inspected the implementation directly rather than relying on the plan's old line numbers.
- VERIFIED a five-minute-window-reserved, four-minute-deadline, single-lock diagnosis on only `asl-m6-m6-b1b-recovery`: fixture PostgreSQL start, two schema-metadata reads and the `finally` stop all exit 0. The reads used the existing test-image snapshot function with additional metadata output, against the original and restored disposable databases. No migration, grant or row mutation was requested. Native commands/logs are in this run's journal.
- OBSERVED initial comparison isolated 72 CHECK-expression cast reconstructions but flagged four index sections as unexplained (authoring comparison exit 1). Reading those exact predicates showed the same reconstruction. The final comparison covered all 49 protected tables: 72 constraints and four partial indexes differ only by `(ARRAY[varchar constants])::text[]` versus an array of individually text-cast constants; zero unexplained differences. Both diagnostic summaries and raw snapshots are retained; the initial result was not overwritten.
- Official PostgreSQL 17 documentation reads (system information functions and operator type conversion) succeeded. `pg_get_constraintdef` / `pg_get_indexdef` reconstruct SQL; the specific cast distribution is observed fixture evidence. Source link and exact correction scope were added to DATA_CONTRACTS and the tests, with no dependency change.
- IMPLEMENTED a restore-only fingerprint preserving every enum constant, type, operator and surrounding expression; exact in-place migration fingerprints remain unchanged. Each rewrite is retained. Added a negative comparison test and real-PostgreSQL allowed/disallowed/NULL equivalence check. Kept the initial NOLOGIN test before fixtures change login state. Added the existing M5 absent-tools registry test to Build and made Migration publish its pass only after successful fixture stop. This is a test/harness correction; no product or protected DDL changed in this diagnosis.
- `tools/m6-acceptance.ps1 -RunId m6-b1c -Phase Prepare`, then Snapshot: exit 0; eight fresh targets, manifest v3, `source-001.json`. After final harness/test edits, PS5.1 parser/ASCII checks on four files and `git diff --check` passed (known autocrlf warnings only); Snapshot exit 0 retained `source-002.json`.
- Started `tools/m6-acceptance.ps1 -RunId m6-b1c -Phase Build -WaitForWindow`. At this entry it is waiting for HH:07, with no Docker build started during the quiet period. Build/Migration results are NOT RUN yet.
- Bounded source/evidence review covered the catalog, guards, retry helper, image exclusions, deadlines, fixtures and existing registry refusals. A Windows `rg` path glob and guessed old M5 tool/test filenames failed; `rg --files` and the actual dispatcher, tools directory and `test_m5_schemas.py` resolved them. Some long diagnostic output was truncated for display; compact comparisons and exact predicate reads established the full result. Status was updated to the owner-authorized continuation.
- VERIFIED all 237 service/tool files matched `source-002.json` before the final metadata-serialization refinement; protected source diff checks against HEAD were empty for normal Compose, existing agents, execution, market, evaluation and migrations 0001–0007. Schema fingerprints now serialize each catalog row as explicit values. Snapshot and whitespace checks passed again, retaining `source-003.json` before the queued build begins. These are authoring checks, not additional product test passes.
- VERIFIED retained diagnosis artifacts: `schema-diagnosis-complete.json` SHA-256 `8cfa72fe5f4f88ee552fc59361d219c714e672345390e2d791a4f9d7da55888f`; before dump 601,320 bytes / `cf97e2626955c5094690dd7836d70b8081ae1ef1cb445e20d214d54939622172`; after dump 747,453 bytes / `ec606dcbbb679c53f77f7e47e4d183bb0c842c199b0531bc82995d1e59363599`. Evidence stays after Docker cleanup. The build remained idle through the 22:05 UTC quiet-window check.
- VERIFIED `m6-b1c -Phase Build -WaitForWindow` exit 0: actual Docker build 22:07:28.945–22:07:32.377 UTC; image `sha256:612250089a2d83c12b73bef6bb563866cfdc8d0b2bc57f836fda4b16667c8d67`. Four scoped static/registry tests passed (1.76 s, 75 deselected, zero skips); Ruff passed; the final fixture-running inventory exited 0. `Build-b1.json` remains explicitly PARTIAL for the full M6 milestone because later images are not implemented.
- VERIFIED `m6-b1c -Phase Migration` exit 0, 22:07:44.050–22:10:08.177 UTC. All 19 schema tests passed (18.09 s, three existing Alembic configuration warnings, zero skips). Populated 0007→0008→0007 comparisons preserved exact legacy rows and protected structure. A held M5 lock caused exactly five rolled-back failures (2.463 s); releasing it after one failure allowed attempt two (0.542 s). The live fixture migration took 0.521 s; 60 samples, 39 observing migration locks, none stronger than AccessShare on protected relations.
- VERIFIED all three fixture container/image/start/restart identities stayed equal; forward checkpoint 656→698 on lease epoch 2, unchanged pilot events, zero worker failure lines. All 16 new tables contained synthetic history (22 rows total). Dump/restore preserved every legacy/M6 row fingerprint and the full restore structure comparison; 76 explicit cast reconstructions retained. Populated downgrade was refused with the complete snapshot unchanged. Reconciliation was OK, with zero accounting, M3 or M4 invariant failures. Both fixture clusters stopped before the phase wrote VERIFIED.
- Final Migration evidence: `.cache/m6/m6-b1c/Migration.json`, SHA-256 `47dbcb1e55dc9ff72980f7f42166409f6c49f3190644297d0e1fcb29a4140f91`; legacy rows `7cce3ae9ea4444805346a3c99d6d748e609b5d4df088ed45ed2708e9ced56f5c`; M6 catalog `86c86b8843ad0d98d06888ff0894470888451eb5661c58077290421bd50e21f4`. Before dump: 601,701 bytes / `292293237138bdbb35a889b9170de2c413d47808bdbee59afde31526357dfa9e`; after dump: 747,897 bytes / `692715951a7e8dba13a5efc91fa5d031a3201c8906daf05c68488d21e10728a4`.
- VERIFIED a separate no-Docker PS5.1 check that the configured absolute deadline reaches both nested migration and cleanup modules. Bounded evidence reads and hashes above exited 0. Started `m6-b1b -Phase Clean -WaitForWindow`; at this entry it is waiting for HH:15. Final cleanup/recording remain before B1 completion; no further product test is missing from B1.
- VERIFIED `tools/m6/b0/stage-docs.ps1 -RunId m6-b1c` and the logged `b1-final-docs` Docker command: exit 0, 22:14:28–22:14:34 UTC. Snapshot `docs-20261003T221427634Z`: 86 Markdown files, zero broken links, four known historical Windows-link warnings. The exact-name `--rm` container used the tested engine image, no network, a read-only root, 0.5 CPU/256 MiB/64 PIDs, dropped capabilities, no-new-privileges and only the staged documentation mount. Subsequent source files were not edited; documentation changes record final evidence.
- VERIFIED untracked-file EOF/trailing-whitespace authoring checks on the four new fixture/harness files, exit 0. Root/docs instructions, bounded STATUS/plan/command-log reads, `rg --files` instruction discovery and `git status --short --branch` succeeded. Some combined output exceeded the display allowance; subsequent bounded evidence reads established the results. Tool-session polls merely collected the running phase outputs.
- VERIFIED `tools/m6-acceptance.ps1 -RunId m6-b1b -Phase Clean -WaitForWindow`: exit 0, completed 22:15:38 UTC, ten resources removed. Sequential `-RunId m6-b1c -Phase Clean -WaitForWindow`: exit 0, completed 22:17:36 UTC, ten resources removed. Each removed five stopped containers, two networks, two volumes and its own engine image. Exact-project post-removal inventories are empty; the expected missing-image inspections exited 1 and are recorded as absence. Final inventory hashes: `d27cdb2dbadf851814a239567422facd8cb097981cbc83dc000cfddb62dc01a7` and `41a86f5c481a45f80415d97a9a3b8f9e0e15a7901cbcc09df153ae672a0ba220`. No normal project, base/tool image or borrowed pilot image was addressed.
- VERIFIED PS5.1 evidence aggregation and hash validation, exit 0: all five Clean records are VERIFIED with 35 removals total, every removal exit 0 and every inventory hash matching. All 237 service/tool files match the tested `m6-b1c/source-003.json`; four harness files are ASCII and parse under Windows PowerShell 5.1.26100.9444. `git diff --exit-code HEAD -- compose.yaml services/engine/app/agents services/engine/app/execution services/engine/app/market services/engine/app/evaluation 'services/engine/alembic/versions/000[1-7]*'` exited 0 with an empty diff. The final documentation stdout/stderr logs were read, confirming the 86/0/4 result above.
- IMPLEMENTED final STATUS and plan §16/§18 reconciliation: B1 complete, B2 next, prior failures preserved. NOT RUN: B2–B9, full M6-A acceptance, new push/PR, normal deployment, runtime login, public source/model calls or activation. No further B1 decision is pending.
- VERIFIED final authoring check, exit 0: all 86 Markdown link-target sets are unchanged from the passing Docker snapshot, and no incoming link references the changed B1 heading. `git diff --check` passed; `git diff --stat` returned the expected B1 files, with known autocrlf warnings only. Retained `.cache/m6/m6-b1c/final-authoring.json`. The four untracked additions are included explicitly in the subsequent staging command.
- Local-delivery native commands and actual results are retained in `.cache/m6/m6-b1c/delivery.jsonl`: exact fifteen-path staging, staged whitespace/scope checks, the local B1 commit, HEAD and final worktree status. Every entry carries arguments, timestamps, exit code and output files. This delivery stays on `codex/m6-research-investigations`; it does not push, create the final M6-A PR, deploy or activate.

### M6 B1 branch publication (2026-10-04 Europe/Budapest)

- OBSERVED owner instruction `push changes`. Root/docs instructions and current STATUS were read. Windows PowerShell 5.1 `git status --short --branch`, `git branch -vv`, `git remote -v` and `git log -3 --oneline` all exited 0: clean branch `codex/m6-research-investigations`, B1 commit `7f327aef16eee8b32a9c2876c3205c550fee87ed`, origin `https://github.com/MentorAliu/adaptive_spot_lab.git`.
- VERIFIED `git push --set-upstream origin HEAD:refs/heads/codex/m6-research-investigations` exited 0 and created the remote branch. `git ls-remote --heads origin refs/heads/codex/m6-research-investigations` exited 0 and returned the exact B1 commit. No force or push to main was used.
- IMPLEMENTED publication records in COMMANDS, STATUS and plan sections 16/18. The subsequent documentation-only commit/push, whitespace check, remote-HEAD comparison and final worktree result are journaled with actual arguments, times, exit codes and output paths in `.cache/m6/m6-b1c/publication-20261004.jsonl`.
- NOT RUN for this publication: product tests (source unchanged), Docker, normal deployment, PR creation, merge or activation. M6-A completion and its single delivery PR remain after B2–B9.

### M6 B2 native baseline and implementation (2026-10-04)

- OBSERVED root/engine/docs instructions, STATUS, ExecPlan 0023, owner decisions,
  relevant strategy/research/evaluation/test contracts and existing engine/harness
  implementations. `git status --short --branch` and `git log -5 --oneline --decorate`
  exited 0: clean `codex/m6-research-investigations`, HEAD/origin `ffa4712`.
  Memory registry search found no relevant entries; no prior memory fact was used.
- VERIFIED `powershell.exe -NoProfile -Command '$PSVersionTable.PSVersion.ToString()'`
  returned 5.1.26100.9444. Repository scripts use this binary, process-only
  `-ExecutionPolicy Bypass`; persistent policy is unchanged.
- VERIFIED sequential `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tools/m6-acceptance.ps1 -RunId m6-b2base -Phase Prepare`, `Snapshot`, `Build`:
  exit 0 each. The pre-interface engine image is
  `sha256:9e454e0f3ef68e8480090cac85f8f433dc35d25aa12051ef2031a954910f3866`;
  four existing static/registry checks and B1 Ruff passed. These are baseline
  provisioning results, not B2 acceptance.
- OBSERVED `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tools/m6-native-baseline.ps1 -RunId m6-b2base`: exit 0. Fresh isolated research
  cluster migrated to 0008, then native gapped-stop, quiet and pilot-lifecycle
  replays passed. `.cache/m6/m6-b2base/NativeBaseline.json` retains exact
  full/M3/portable/trace fingerprints and counts; full replay reports remain in
  `research/out/baseline/`. Gapped-stop M3 hash is
  `2500c8d126e83c49976dd1ade3af27a1e4abd5bbddd44c5db03a6a1b8bf5561e`.
  The fixture database was stopped; no normal-project target was addressed.
- IMPLEMENTED source and contracts in this batch, using existing dependencies.
  `tools/m6-format.ps1 -RunId m6-b2base` via the same PS5.1 process-only command
  exited 0: containerized Ruff applied import/unused-import fixes to a staged
  source copy; changes to five files were copied back and reviewed. This was
  authoring formatting, not application verification. Logs remain in the
  baseline run journal. No unrestricted agent or public/model call ran.
- VERIFIED PS5.1 parser/ASCII checks for the baseline, formatter, acceptance
  and engine module files, and `git diff --check`, exit 0. A PowerShell brace
  path and several nonexistent file reads failed during exploration; they
  performed no mutation and were replaced with verified explicit paths.
- PROPOSED B2 acceptance commands: the same PS5.1 `m6-acceptance.ps1` invocation
  on fresh `m6-b2a`, phases Prepare, Snapshot, Build, Checks, Regression,
  EngineParity (`-BaselineRun m6-b2base`), Stop, Clean. One heavy phase at a time
  inside HH:07–HH:58 UTC with absolute deadlines/stop reserves; Clean uses the
  stricter HH:15–HH:55 window. Every required test skip fails its phase.
  At this entry these product acceptance commands are NOT RUN; no result is
  implied by their implementation or the baseline.

- OBSERVED first product run `m6-b2a`: Prepare and Snapshot exited 0. Build at
  03:22 UTC created image
  `sha256:18cec4c83938ea896f9f27a2bf04321ca076f100984d05447684ae6a0dc0eef7`
  and passed the four static/registry tests, then FAILED `b2-lint`, exit 1.
  `.cache/m6/m6-b2a/20261004T032222805Z-b2-lint.stdout.log` names exactly three
  I001 import-order findings in `m6_engine.py`, `test_m6_candidates.py` and
  `test_m6_strategy_guards.py`. No product-code lint finding was reported.
  The required Build was not accepted and subsequent phases did not start.
  Requested the owner's authorization for those three import blocks and an
  explicit staged Ruff app/tests import classification, then Build and remaining
  B2 checks. No correction or rerun ran while the answer was pending.
- VERIFIED `m6-b2base -Phase Clean` via PS5.1/process-only Bypass, exit 0,
  completed 03:23:26 UTC. Removed five exact-name resources: one stopped
  container, two networks, one volume and its engine image. Inventory SHA-256
  `f4c0aaacb0c5e1f30ce6fb8ba2a4867d7a2aca0b4f0c15c6e4a87a14c8682ced`;
  all removal commands exit 0, all post-removal inventories empty. Expected
  image-absence inspection exits 1. Baseline evidence remains. Only the latest
  failed `m6-b2a` image/network are retained for the proposed correction;
  no fixture workload is running.
- VERIFIED post-failure `git diff --check`, exit 0. NOT RUN: B2 Checks,
  Regression, EngineParity, completed-batch commit, B3–B9, B10/B11, push/PR,
  normal deployment, activation, runtime login or public/model calls.

### M6 B2 authorized correction and verification (2026-10-04)

- OBSERVED owner reply `go ahead`: authorization for the three test import blocks,
  explicit staged formatter classification and the remaining B2 checks. The
  earlier Build failure and pause above remain part of the evidence.
- IMPLEMENTED that scoped correction; no product behavior changed by it.
  VERIFIED PS5.1 parser/ASCII checks and `git diff --check`, exit 0.
- VERIFIED sequential `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Snapshot`, then `-Phase Build`:
  exit 0 each. Snapshot `source-002.json`; tested engine image
  `sha256:62ba733d593c2b76fbf52ae7a9067d1e811dcd41ba188c85ca80fc2b45f10a12`.
  Four static/registry tests and the app/tests/migration Ruff check passed.
  `Build-b2.json` remains PARTIAL for full M6, engine-only by design.
- VERIFIED the same invocation with `-Phase Checks`, exit 0, completed 06:47:36
  UTC. All **145 tests passed in 6.29 s**, no skips: grammar, Decimal operators,
  normalization/causality/reference properties, protection, manifest/activation
  refusals, actual database guards and existing schema/static refusals. Its
  fixture database was stopped in `finally`.
- VERIFIED `powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  tools/m6-format.ps1 -RunId m6-b2a`, exit 0 at 06:49:54 UTC. Explicit
  `lint.isort.known-first-party=['app','tests']` removes the earlier staging
  classification ambiguity; Ruff passed and zero files were copied back.
- OBSERVED `-Phase Regression -WaitForWindow` waiting for 07:07 UTC: the full
  25-minute reservation would not fit before 06:58. No phase work begins while
  waiting and the harness limits are unchanged. Regression and EngineParity
  results are pending at this entry.
- VERIFIED authoring-only `.cache/m6/m6-b2a/b2-source-review.ps1` through PS5.1,
  exit 0: all 405 application/tool/test files match the tested Build snapshot;
  unchanged protected source/dependency paths, four PS5.1/ASCII scripts,
  unchanged window functions and `git diff --check`. The initial path inventory
  probe named a nonexistent `app/market`; `rg --files` resolved the actual
  `app/market_data` and `accounting.py`/`execution/risk.py` paths before the
  successful check. This authoring probe changed no product or gate behavior.
  Evidence: `.cache/m6/m6-b2a/SourceReview.json`.
- OBSERVED the queued Regression begin at 07:07:21 UTC. Its database startup
  and migration exited 0. A bounded read-only progress check, filtered by exact
  `asl-m6-m6-b2a-engine` project and `engine-tests` service labels, exited 0 at
  07:21:28 and showed two failing tests. Subsequent acceptance work was held.
- FAILED Regression, exit 1, without timeout: **167 passed, two failed, no skips**,
  one existing Starlette test-client deprecation warning, **892.41 s**. Pytest
  finished at 07:22:22 UTC; the fixture database stop exited 0 at 07:22:25.
  Exact command and stdout/stderr are journaled in `commands.jsonl`; stdout is
  `20261004T070727260Z-b2-m3-m4-regression.stdout.log`.
  `Regression.json` SHA-256:
  `3399fa691c8940d1a7152cf291dcd5cc458c3ae3029aa03467df078b291f7a06`.
- OBSERVED failures and read-only source diagnosis:
  `test_m3_roles.py::test_identity_enable_refuses_non_isolated_projects` clears
  `ASL_TEST_ISOLATED`, but the new fixture recipe also supplies
  `ASL_REPLAY_ISOLATED=1`; unchanged `execution/identity.py` accepts either flag.
  `test_m4_api.py::test_experiment_lifecycle_over_http_returns_accepted_requests`
  receives HTTP 503 at System status, then fails on missing `trading`.
  `app/db.py` readiness accepts only 0006/0007 while this fixture is on 0008.
  No execution, identity, API test, schema or readiness source was corrected.
- PROPOSED owner-reviewed correction: explicitly set replay isolation to 0 for
  Regression's ordinary test database (its positive replay cases set their own
  required flags), and accept additive `0008_m6_research` in API readiness while
  preserving accepted 0006/0007 revisions. Rebuild, rerun focused failures and
  all B2 gates, then exact-name cleanup and local delivery. No financial cap,
  protected table, main identity/activation rule or normal operation would change.
  Answer pending; no product correction, acceptance rerun or EngineParity ran
  after the failure.
- OBSERVED only the latest failed `m6-b2a` run remains for diagnosis, with its
  fixture database stopped. The completed pre-interface baseline remains clean.
  Documentation/source review records are retained. NOT RUN: EngineParity,
  final Docker documentation check, final Clean, local commit, B3–B9, B10/B11,
  push/PR/merge, normal deployment, public/model calls or runtime login.
- VERIFIED post-failure authoring source/PS5.1/ASCII/whitespace review, exit 0:
  all 405 tested source hashes still match. STATUS and plan §16/§18 record the
  failure, concrete proposed correction and pending owner answer. No product
  source changed during diagnosis; the local completed-batch commit did not run.

### M6 B2 regression correction authorized (2026-10-04)

IMPLEMENTED after the owner's `Ok go ahead and fix` reply: Regression alone
overrides `ASL_REPLAY_ISOLATED=0`; API readiness accepts additive
`0008_m6_research` while retaining 0006/0007. Existing identity guards, financial
definitions, protected schema and test expectations are unchanged.
OBSERVED authoring-only preservation of the previous Build, Checks, Regression
and SourceReview JSON under `*-before-regression-fix.json`; the failed regression
digest remains `3399fa691c8940d1a7152cf291dcd5cc458c3ae3029aa03467df078b291f7a06`.
VERIFIED PS5.1/process-only Bypass commands, each exit 0:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-focused.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Checks -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-source-review.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-helper-review.ps1
```

- OBSERVED `source-003.json`; Build completed 07:41:42 UTC with image
  `sha256:37dea4ee2afca6cdbce7e24d3e5f773ef4103326c039624f300ae79d20f5ff98`.
  Four static/registry tests and full app/tests/migration Ruff passed.
- VERIFIED focused regression/readiness rerun: both failed cases and
  `test_migrated_database_is_ready`, 3 passed in 12.23 s, no skips; one existing
  Starlette dependency warning. Fixture stop passed.
- VERIFIED Checks on the rebuilt image: 145 passed in 6.01 s, no skips;
  completed 07:43:16 UTC, then fixture stop passed.
- VERIFIED authoring source review: all 405 tested application/tool/test hashes
  match; protected source/dependencies and quiet-window functions unchanged;
  tracked and four cached helpers pass PS5.1 parsing/ASCII; whitespace passes.
- OBSERVED Regression command dispatched with `-WaitForWindow`; its 25-minute
  reservation awaits 08:07 UTC. Regression, EngineParity and delivery remain
  pending actual results. No normal-app operation is authorized by this correction.

### M6 B2 Regression passed; EngineParity held (2026-10-04)

Actual PS5.1/process-only Bypass commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Regression -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase EngineParity -BaselineRun m6-b2base -WaitForWindow
```

- VERIFIED Regression, exit 0: database startup/migration passed at 08:07 UTC;
  all sixteen M3/M4 files passed, 169 tests in 872.26 s, no skips, one existing
  Starlette dependency warning. Completed 08:21:55 UTC; fixture stop passed.
  `Regression-before-binding-fix.json` SHA-256 (preserved before the later rerun)
  `e44195dba22f92e73c14a8c0717d05e49fcb34859b8640fdbe9c9789a14d833d`.
  Exact Docker commands/times/results are retained in `commands.jsonl`.
- FAILED EngineParity, exit 1, no timeout: startup/migration passed; native
  gapped-stop replay completed, then candidate definition installation raised
  `candidate_definition_conflict` before candidate execution or comparison.
  Docker command 08:22:27.780–08:22:35.559 UTC. Retained stderr:
  `20261004T082227780Z-engine-parity.stderr.log`. Research fixture stop passed
  at 08:22:36 UTC; both fixture databases are stopped.
- OBSERVED `EngineParity-before-binding-fix.json` SHA-256 (preserved before rerun)
  `8e5f4ee7de361a657ce2d3c34e8f8e883082e1eaf2c027aae5c95e68974a17b8`;
  runner `research/out/parity-before-binding-fix/evidence.json` SHA-256
  `8a57afa3f0be7411cf33f78363a4bde756691dcb71c4ef968545efac6d020eb0`.
- INFERRED source diagnosis: `app/research/strategy.py` reuses `:canonical`
  for `CAST(... AS jsonb)` and canonical text, allowing parameter-type inference
  to alter the stored canonical representation. The existing fixture installer
  binds JSONB and canonical text separately, as does the corrected B1 migration.
- PROPOSED only: `.cache/m6/m6-b2a/candidate-binding-proposed.diff` separates
  those two bindings. It preserves the strict canonical/hash conflict check,
  frozen definitions, research guards and schema. No product correction is applied.
  Owner approval is pending under the pasted stop-on-gate-failure instruction.
  After approval: preserve failed evidence, apply the fix, rebuild and rerun
  focused installation, Checks, Regression and EngineParity; retain evidence,
  exact-name Clean and commit the verified B2 batch locally.
- VERIFIED post-failure authoring source review, exit 0: all 405 tested hashes
  still match image `37dea4ee…0f5ff98`; protected paths/dependencies, quiet-window
  functions, PS5.1/ASCII and whitespace pass. Only read-only diagnosis, a proposed
  diff and evidence documentation followed this failure.
- NOT RUN: accepted EngineParity, final documentation check/Clean/local commit,
  B3–B9, B10/B11, push/PR/merge, normal-app command/deployment, real model/public
  runtime call or login. B2 and M6-A remain incomplete. The latest failed run's
  evidence/resources remain for diagnosis; the completed baseline is clean.

### M6 B2 candidate binding correction authorized (2026-10-04)

OBSERVED owner reply: `Approve the binding fix and complete B2`. IMPLEMENTED
the proposed two-line JSONB/text parameter separation; strict canonical/hash
conflict and actual research-database guards remain unchanged. Before reruns,
preserved prior gate JSON as `*-before-binding-fix.json` and copied all failed
parity outputs to `research/out/parity-before-binding-fix`. Their original
failure claims/hashes remain historical evidence.

Actual PS5.1/process-only Bypass commands, exit 0:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-preserve-binding-evidence.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Snapshot
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Build -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-focused-install.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-focused.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Checks -WaitForWindow
```

- OBSERVED `source-004.json`; Build completed 08:27:07 UTC with image
  `sha256:7cd93cff947f876cf97d7f1cda90309d8a801e2d0bdbe9bbb5341f1d76e64aea`.
  Four static/registry tests and full app/tests/migration Ruff pass.
- VERIFIED focused research installation: stored JSON and exact canonical bytes
  match, independently calculated SHA-256 matches, identical installation gives
  one row, and a conflicting synthetic immutable row is rejected without changing
  it. The negative fixture is rolled back to a savepoint. `FocusedInstall.json`,
  staged program `research/out/focused_install.py` and native command logs remain.
  The research fixture stop passed.
- VERIFIED prior focused cases again: 3 passed in 12.37 s, no skips, one existing
  Starlette warning. Fixture stop passed.
- VERIFIED Checks on the final image: 145 passed in 6.67 s, no skips; fixture
  stop passed. Full Regression dispatched at 08:30 UTC within the unchanged
  25-minute reservation, with startup/migration passed; its final result is pending.
- An authoring patch-format error was corrected before any edit or command
  executed; no product-gate failure or partial patch resulted.
- EngineParity, final documentation/Clean/local commit remain pending actual
  rerun results. No normal app, protected DDL, seed/envelope, dependency,
  activation or B3 change is authorized by this correction.

### M6 B2 final code gates (2026-10-04)

Actual PS5.1/process-only Bypass commands:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Regression -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase EngineParity -BaselineRun m6-b2base -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-source-review.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-helper-review.ps1
```

- VERIFIED final-image Regression, exit 0, no timeout: all sixteen existing
  M3/M4 files, 169 passed in 891.28 s (14:51), no skips, one existing Starlette
  warning. Docker test command 08:30:15.916–08:45:09.691 UTC; successful database
  startup/migration and fixture stop. Native stdout is
  `20261004T083015916Z-b2-m3-m4-regression.stdout.log`. `Regression.json` SHA-256
  `61da8baf94e90114a17757200540c19706867e09eba11cd45c6b63c4779a41e6`.
- VERIFIED EngineParity, exit 0, no timeout: Docker test command
  08:45:32.495–08:48:46.910 UTC; successful database startup/migration and fixture
  stop. Gapped-stop, quiet and pilot-lifecycle financial projections and every
  signal bar match (143/260/2 bars respectively); accounting/M4 invariants clean.
  Native M3/portable/trace fingerprints match the pre-interface baseline on all
  three scenarios; native full fingerprints also match on gapped-stop and quiet.
  Native and candidate pilot fast/per-step runs each match their own full/M3/
  portable/trace and FINAL report hashes. Actual declaration and reduced-fidelity
  labels were asserted. Native stdout is
  `20261004T084532495Z-engine-parity.stdout.log`.
- OBSERVED final `EngineParity.json` SHA-256
  `e9318772db6418cf53ed9f9b88478fa9843dfcc994f89a2396646c7b608ae47e`;
  runner `research/out/parity/evidence.json` SHA-256
  `9655beb2daf949fc986335b1c2a01c47cb4f44a5247cce527dfb10185f15c34a`.
  Financial rows, individual ledger postings, per-bar signals, mandates, reports
  and traces are retained. These are synthetic correctness tests, not performance
  or forward-trading results.
- VERIFIED authoring source review, exit 0: 405 source hashes still match final
  Build image `7cd93cff…6e64aea`; protected paths/dependencies unchanged; four
  tracked harness files and seven cached helpers pass PS5.1 parsing/ASCII.
  Original quiet-window functions and whitespace pass. Docs are outside the
  application source identity and are checked separately after final recording.
- OBSERVED Clean dispatched with the actual command below. Its unchanged
  five-minute reservation no longer fits this hour, so it awaits 09:15 UTC before
  any deletion. Both fixtures are stopped. Final documentation verification,
  exact-name fixture/replaced-image cleanup and local commit remain pending.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Clean -WaitForWindow
```

NOT RUN: B3–B9, full M6-A acceptance/PR, B10/B11, push/merge, normal-app command
or deployment, activation, runtime login and real model/public runtime calls.
No further B2 owner decision is pending.

VERIFIED preliminary documentation check, actual command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-docs.ps1
```

Exit 0, no timeout, completed 08:53:51 UTC: 86 staged Markdown files, zero broken
relative links and four known historical Windows-link warnings. Container uses
the already pinned `python:3.13.11-slim-bookworm`, network none, read-only root,
bounded CPU/memory/PIDs, dropped capabilities and only the staged documentation
mount. It removes itself; the exact isolated-project post-run query exited 0.
External URLs are not fetched. Final completion recording will be checked again
after Clean. Native command/output and staging hashes remain in `commands.jsonl`,
`Docs.json` and `docs-20261004T085342586Z/staging.json`.

### M6 B2 cleanup and local delivery (2026-10-04)

Actual PS5.1/process-only Bypass commands, exit 0:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/m6-acceptance.ps1 -RunId m6-b2a -Phase Clean -WaitForWindow
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-retired-build-clean.ps1
```

- VERIFIED Clean completed 09:15:24 UTC, after the unchanged HH:15–HH:55
  reservation. Seven resources removed by exact name: two stopped fixture
  containers, two private networks, two volumes and `asl-m6-m6-b2a-engine-tests`.
  Every removal exited 0. Every exact-project post-removal inventory is empty;
  the missing final image inspection exited 1 as expected. Inventory SHA-256
  `b58a92db8562cd5b6f0bd077421092036ed965628543d75ddb97f79f0195d176`;
  `Clean.json` SHA-256
  `e61b70113b68f29eba48adf5de75be1a4bb0847c80422116eb30815ec85b9132`.
- VERIFIED replaced-image absence completed 09:15:35 UTC: exact IDs of images
  `18cec4c8…c0eef7`, `62ba733d…5f10a12` and `37dea4ee…0f5ff98` were already absent.
  Each ID has exactly one successful historical ownership record. All six bounded
  inventory/absence inspections exited 1 with No-such-image, as expected; zero
  additional images were removed. `RetiredBuildClean.json` SHA-256
  `fa0323dcf6c6b1361c0c924cd2b45c78fd408ad11a495bf44e16a0856ae3efff`.
- VERIFIED baseline Clean previously removed five exact-name resources. Evidence
  for both runs and all failed attempts remains. No force, global prune,
  base/shared-image removal or normal-app command ran.

PROPOSED final completion-documentation and local Git delivery commands (not yet
claimed as executed in this entry):

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-docs.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-source-review.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-helper-review.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-delivery.ps1 -Step Stage
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-delivery.ps1 -Step Commit
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .cache/m6/m6-b2a/b2-delivery.ps1 -Step Verify
```

The authoring-only delivery helper checks all scoped evidence first, stages only
the 28-file B2 allowlist, checks the staged diff and creates the local commit
`Implement M6 B2 candidate grammar and engine parity`. Native Git arguments,
UTC times, exit codes and stdout/stderr are recorded in
`.cache/m6/m6-b2a/delivery.jsonl`; Verify requires a clean working tree. No
push/merge/PR or normal-app action is part of these commands. B3 is NOT RUN.

VERIFIED completion-documentation check via the listed `b2-docs.ps1` command,
exit 0/no timeout, completed 09:17:22 UTC. It checked all 86 staged Markdown
files with zero broken links and four unchanged historical Windows-link
warnings. Its disposable container removed itself; the scoped post-run query
exited 0. Evidence for that check remains at `docs-20261004T091714383Z` and in
the timestamped native logs. The closing status/evidence entries will receive
the same link check once more before local Git delivery; this is documentation
verification, not a repeated application test or full M6 acceptance.

### M6 B1/B2 checkpoint PR and merge (2026-10-04)

OBSERVED owner request: `create pr and merge into main`. This authorizes the
completed B1/B2 checkpoint publication before B3–B9, without deployment or
activation. VERIFIED clean branch at B2 source commit `431dff5`. Actual initial
commands/results:

- `gh --version`: exit 0, existing CLI 2.100.0. The first sandboxed `gh pr status`
  encountered restricted network access; the authorized network retry exited 0,
  confirming no open PR or PR associated with the branch.
- `git fetch origin main codex/m6-research-investigations`: exit 0. Main is
  `9241034127ad0dbead6a163da695ea00047a189a`; remote codex branch is `ffa4712`.
  `git merge-base --is-ancestor origin/main HEAD` exited 0. The three pending
  commits are completed B1, its publication record and completed B2.
- Repository API and installed `gh pr merge --help`: exit 0; merge commits are
  supported. The branch-protection API returned HTTP 403 because that feature
  needs GitHub Pro/public visibility. This is not proof that protections are
  absent; normal PR merge remains subject to GitHub's actual requirements.

PROPOSED next commands: commit this documentation-only authorization record,
push the codex branch without force, `gh pr create --base main --head
codex/m6-research-investigations --body-file <cached-body>`, then review the live
PR/head/checks and `gh pr merge --merge --match-head-commit <verified-head>`.
Use the installed CLI, retain native arguments/results under
`.cache/m6/m6-b2a/publication/`, and verify the merged PR and remote main.
No admin bypass, branch deletion, application retest or normal-app operation is
part of this publication. New code/check failures would need separate resolution.

## Agent-driven commands to implement at their milestones

Document actual containerized commands for provider/capability preflight, role/tool contract tests, recorded workflow replay, research-envelope validation, bounded research worker execution, policy/approval verification, permission revocation, workflow cancellation and full agent acceptance scenarios. Operator authority is required where the action changes policy/control state.

These command names/arguments are intentionally not guessed before implementation. Every future command must bind mode/account/policy and refuse to target main financial history accidentally. Routine verification uses recorded responses and no paid API. Do not run a free-form model-generated command or let the agent tool interface call this operator command surface directly.
