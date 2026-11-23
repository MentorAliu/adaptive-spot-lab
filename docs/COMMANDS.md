# Command contract

The commands in use now. `VERIFIED (date)` means the command ran with the result shown in the dated record of [archive/COMMANDS.md](archive/COMMANDS.md); `PROPOSED` means it is the intended form and has no recorded run in that form. Every run before 2026-10-20, with its output, is in that archive. A new run's commands and results go into its plan's progress section, not here; this page changes only when a command itself changes.

Never point a test command at the normal app, its database, `.env`, `secrets/` or `codex_home`. A skipped or unrun check is NOT RUN ([TESTING](TESTING.md#status-and-rule)).

## Web (cloud)

From `apps/web`, after `pnpm install --frozen-lockfile` at the repository root. VERIFIED (2026-10-21, [M10 update 2](archive/COMMANDS.md#m10-update-2-zec-near-and-xrp-on-paper--2026-10-21)):

```bash
pnpm run typecheck
pnpm exec eslint . --ignore-pattern '.output/**'   # pnpm run lint also reads the git-ignored build output; remove .output first
pnpm run check                                      # Prettier
pnpm run api:check                                  # generated TypeScript API types match the engine's OpenAPI file
pnpm exec vitest run                                # same as pnpm run test
pnpm run build
```

From the repository root the same scripts run as `pnpm --dir apps/web run <script>`, for example `pnpm --dir apps/web run lint` (PROPOSED: the same scripts, no recorded run in this form).

## Engine without a database (cloud)

From `services/engine`. `uv sync --frozen` installs the locked environment (PROPOSED: the records use the locked `.venv` and `uv run --frozen --no-sync`). VERIFIED (2026-10-21, [M10 update 2](archive/COMMANDS.md#m10-update-2-zec-near-and-xrp-on-paper--2026-10-21)):

```bash
.venv/bin/ruff check --no-cache .
.venv/bin/python -m app.export_openapi --check
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests
```

Expected: Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`. Since [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md#14-progress) the pytest baseline without a database is `1 failed, 133 passed, 82 skipped` (2026-11-12; `84 skipped` under ExecPlan 0060 with the daily history's fix): the failure is `test_database.py::test_migrated_database_is_ready`, which needs a database, and every skip is a database case. Any other failure is new. The baselines before it, with the futures' and the agents' suites, are in [the archive](archive/COMMANDS.md#removed-by-execplan-0060--2026-11-12).

## Engine on a scratch PostgreSQL (cloud)

A disposable PostgreSQL 16 cluster that holds only `asl_m1_` databases, listening on 127.0.0.1 only. VERIFIED (2026-10-21, [M10 update 2](archive/COMMANDS.md#m10-update-2-zec-near-and-xrp-on-paper--2026-10-21)):

```bash
# once per session, as the postgres user; the port is the session's choice (55452 in the records)
/usr/lib/postgresql/16/bin/initdb -A trust -U asl -E UTF8 --locale=C.UTF-8 -D <scratch dir>
# -E UTF8 since 2026-10-30 (ExecPlan 0047 §14): in a session whose locale is C, initdb otherwise makes a SQL_ASCII
# cluster, on which SQLAlchemy cannot read the server's version and every database test errors
pg_ctl -D <scratch dir> -o "-p 55452 -c listen_addresses=127.0.0.1" start   # PROPOSED form of the start
# random scratch files of at least 32 characters, one per file the engine and its tests read (since ExecPlan 0060):
# /run/secrets/postgres_password, api_db_password, market_worker_password, execution_db_password and
# api_internal_key (scratch values, never the owner's)
export ASL_DB_HOST=127.0.0.1 PGPORT=55452 ASL_TEST_ISOLATED=1

# per run, from services/engine: a fresh database, migrated by the migration role
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_<run>
ASL_DB_NAME=asl_m1_m6_<run> ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider -rfE tests   # 216 passed in 39 s (2026-11-12, ExecPlan 0061; 218 under ExecPlan 0060)
```

OBSERVED on 2026-10-31 ([ExecPlan 0048 §14](archive/plans/0048-the-cockpit.md#14-progress)): the cluster's directory must be one the `postgres` user can reach (`/var/tmp/<dir>`; one under the session's scratchpad in `/tmp/claude-0` is refused).

OBSERVED on 2026-11-03 ([ExecPlan 0054 §14](archive/plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md#14-progress)): run one database suite per cluster at a time. The roles belong to the cluster, not to a database, and the fixtures switch the identities' login on and off, so a run on another database of the same cluster makes tests of the first run fail. A second cluster on another port (`initdb` and `pg_ctl` as above, with `-p 55453`) runs a parallel check safely.

Every database suite needs `ASL_TEST_ISOLATED=1` and a database whose name starts with `asl_m1_`, the same name in `ASL_DB_NAME` (the spot suites refuse any other, `spot_tests_require_a_disposable_asl_m1_database`). A migration's own check is `alembic upgrade head`, `alembic downgrade -1`, `alembic upgrade head` on a fresh database, then a refused downgrade once a record of the new kind exists; since ExecPlan 0060, `tests/test_spot_migration.py` runs `0041_spot`'s on the suite's database: down to `0040_main_rule`, refused while a spot fill exists or the futures account is not flat, and back to the head.

## Browser suites (cloud)

Since [ExecPlan 0060](plans/0060-spot-trading-only.md) the spot pages run on a database `tests/spot_browser_fixture.py` seeds (a daily Bitcoin history since 2017 and a month of minutes, all a SYNTHETIC walk in Binance's answer format, the funding, run #1's buy, the owner's Stop and sell, run #2's buy and the backtest), with the fixture's SYNTHETIC book, the real execution worker, the API and the built web server on the same tree. Playwright 1.63 finds the session's preinstalled Chromium by itself: no scratch configuration. VERIFIED (2026-11-12, [TESTING](TESTING.md#since-execplan-0060-spot-trading-only)):

```bash
# services/engine, with ASL_DB_HOST=127.0.0.1 PGHOST=127.0.0.1 PGPORT=55452 exported: a fresh database at head, seeded
createdb -h 127.0.0.1 -p 55452 -U asl asl_m1_<run>_browser
ASL_DB_NAME=asl_m1_<run>_browser ASL_DB_ROLE=migration .venv/bin/alembic upgrade head
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_<run>_browser .venv/bin/python -m tests.spot_browser_fixture seed
# in the background, each its own process (stop each by its own process ID with SIGTERM):
ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_<run>_browser .venv/bin/python -m tests.spot_browser_fixture feed
ASL_EXECUTION_ENABLED=1 ASL_DB_ROLE=execution ASL_DB_NAME=asl_m1_<run>_browser .venv/bin/python -m app.execution.worker
ASL_DB_ROLE=api ASL_DB_NAME=asl_m1_<run>_browser .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
# apps/web: the production build and its server
pnpm run build
NODE_ENV=production HOST=127.0.0.1 PORT=4318 ASL_API_BASE_URL=http://127.0.0.1:8000 node .output/server/index.mjs
# apps/web: the pages (the Pause test pauses and resumes the run), then the live suite, once per seeded database
# (it stops run #2 with Stop and sell and starts run #3) on http://localhost:4318, a secure context
NO_PROXY=127.0.0.1,localhost ASL_SPOT_BROWSER=pages ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_<run>_browser \
    pnpm exec playwright test e2e/spot.spec.ts e2e/local-time.spec.ts e2e/foundation.spec.ts --workers 1 --trace off
NO_PROXY=127.0.0.1,localhost PLAYWRIGHT_BASE_URL=http://localhost:4318 ASL_SPOT_BROWSER=live ASL_TEST_ISOLATED=1 \
    ASL_DB_NAME=asl_m1_<run>_browser pnpm exec playwright test e2e/live.spec.ts --workers 1 --trace off
```

The web server reads its assets from `.output` at each request: removing `.output` while it runs (for the lint) answers every script and stylesheet with 500 and the pages never hydrate (OBSERVED on 2026-11-12). Lint with `pnpm exec eslint . --ignore-pattern '.output/**'`, or after the server stops.

The account suites keep M1's databases, the API isolated (`ASL_TEST_ISOLATED=1` in its environment) and nothing seeded, the web server as above. VERIFIED (2026-11-12):

```bash
# services/engine: a fresh asl_m1_browser_<run> at head (createdb and alembic as above), then the API, which funds it
ASL_TEST_ISOLATED=1 ASL_DB_ROLE=api ASL_DB_NAME=asl_m1_browser_<run> .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
# apps/web: funding first, then the account suites on the same database
NO_PROXY=127.0.0.1,localhost ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_browser_<run> \
    pnpm exec playwright test e2e/funding.spec.ts --workers 1 --trace off
NO_PROXY=127.0.0.1,localhost PLAYWRIGHT_ACCOUNT_FIXTURE=1 ASL_TEST_ISOLATED=1 ASL_DB_NAME=asl_m1_browser_<run> \
    pnpm exec playwright test e2e/request-envelope.spec.ts e2e/account-recovery.spec.ts e2e/foundation.spec.ts --workers 1 --trace off
```

M1's funding outcome suites on another fresh `asl_m1_browser_<run>`, after `e2e/funding.spec.ts` and nothing else, in this order: `PLAYWRIGHT_UNKNOWN_FIXTURE=1` with `e2e/unknown.spec.ts` (it expects 12,233 USDT), then with `e2e/before-dispatch.spec.ts` (12,277); then `UPDATE account_state SET valuation_valid = false` on that database, `PLAYWRIGHT_PENDING_FIXTURE=1` with `e2e/pending.spec.ts`, and `valuation_valid` set back to true. With the API stopped, `PLAYWRIGHT_EXPECT_ERROR=1` with `e2e/foundation-error.spec.ts`. Each with `ASL_TEST_ISOLATED=1` and the database's name for Playwright; on another name a suite skips, which reports no failure.

## Documents and the update file's model (cloud)

VERIFIED (2026-10-21, M10 update 2):

```bash
python3 tools/check_links.py .                       # expected last line: "...; 0 broken link(s)"
pwsh -NoProfile -File tools/m8/update-model.ps1 -Repository . -Work <empty scratch dir>   # "failed":[]; VERIFIED again 2026-10-24 for ExecPlan 0039 part B: 19 scenarios, 86 expectations, the clean start's four among them; and for the clean start's fix: 21 scenarios, 98 expectations; for ExecPlan 0042 (2026-10-25): 22 scenarios, 105 expectations; and for its fix that replaces the api before the web: 23 scenarios, 109 expectations
grep -nP '[^\x00-\x7F]' tools/update.ps1 tools/update.cmd   # no output: the update file stays plain ASCII
```

Where the session has no `pwsh`, the records install PowerShell 7.4.6 (MIT License) from its GitHub release, checked against the release's own `hashes.sha256` before it is unpacked; a test tool of the session, not of the app. VERIFIED (2026-10-21, [ExecPlan 0035](archive/plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress)):

```bash
curl -sSLO https://github.com/PowerShell/PowerShell/releases/download/v7.4.6/powershell-7.4.6-linux-x64.tar.gz
curl -sSLO https://github.com/PowerShell/PowerShell/releases/download/v7.4.6/hashes.sha256
sha256sum powershell-7.4.6-linux-x64.tar.gz   # 6f6015203c47806c5cc444c19d8ed019695e610fbd948154264bf9ca8e157561, as hashes.sha256 lists it
mkdir -p /opt/pwsh && tar -xzf powershell-7.4.6-linux-x64.tar.gz -C /opt/pwsh   # then /opt/pwsh/pwsh
```

The model runs PowerShell 7; the PC runs the update file in Windows PowerShell 5.1, which no cloud session has.

For [ExecPlan 0060](plans/0060-spot-trading-only.md#14-progress) (2026-11-12) the model is NOT RUN in the cloud: the session had no `pwsh` and its permission check refused the install. It runs on the owner's PC instead, in Windows PowerShell 5.1, from a fresh clone of the branch in a temporary folder outside the app's (removed after), and takes every `docker` out of its own process's PATH before anything runs, so the app is not touched. VERIFIED (2026-11-12, by a Remote Control session on the owner's word; PowerShell 5.1.26100.9818): exit 0, 25 scenarios, 115 expectations, `"failed":[]`, in 139 s:

```powershell
# in a new empty folder under $env:TEMP: git clone --branch <branch> --single-branch https://github.com/MentorAliu/adaptive_spot_lab.git repo
# then, from repo's root, with an empty work folder beside it:
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\m8\update-model.ps1 -Repository . -Work <empty dir> > model.log 2>&1
```

VERIFIED again for [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md#14-progress) (2026-11-13, the same way, PowerShell 5.1.26100.9818): the spot model, exit 0, 14 scenarios, 61 expectations, `"failed":[]`, in 63 s. The result line has no count fields: the counts are of its entries.

OBSERVED on the 0060 run: the model writes its whole result as one JSON line; with `2>&1` in Windows PowerShell 5.1, the `-Show` output's first stderr line comes back wrapped as a `NativeCommandError`, which is not an error of the script.

## On the owner's PC

Only the owner starts these, by double-click in the app folder ([OPERATIONS](OPERATIONS.md#the-update-file-m8)).

- **`update-app.cmd`** (a copy of `tools/update.cmd`) runs `tools/update.ps1` as GitHub's `main` holds it: backup, forward migrations, the changed services recreated, then the checks of the running source, readiness and pages. VERIFIED (2026-10-21): three runs that day, each `COMPLETE` as read-only checks saw: M10 update 2 (`3dd5011`, 10:11 UTC), the runner fix with ExecPlan 0035 (`7440a89`, 11:11 UTC, the research containers retired) and the check's citation fix (`2bf5b1e`, 13:09 UTC; schema `0016_m10_three_coins`, 10 containers up).
- **`docker-cleanup.cmd`** (a copy of `tools/docker-cleanup.cmd`) runs `tools/docker-cleanup.ps1`: backup, this app's unused images and two leftover volumes removed by exact name, Docker's disk compacted, old dumps deleted after a clean run ([ExecPlan 0034 §4.1](archive/plans/0034-app-cleanup.md#41-part-1-the-docker-clean-up-file)). Its read-only preview is PROPOSED, not yet run on Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools\docker-cleanup.ps1 -DryRun
```

## Cleaning up after a test run

VERIFIED (2026-10-21, M10 update 2; the exact `dropdb` and `pg_ctl` forms are PROPOSED): stop the API and web server by process ID; remove `apps/web/.output`, `apps/web/test-results` and `apps/web/node_modules/.scratch`; drop each scratch database by its exact name (`dropdb -h 127.0.0.1 -p 55452 -U asl asl_m1_m6_<run>`); stop the scratch cluster (`pg_ctl -D <scratch dir> stop`) and remove its directory by exact path. Docker resources of a test run are removed by exact name, never with a prune ([DOCKER](DOCKER.md#cleaning-up-disposable-resources)).

## ExecPlan 0060: the spot suites and install check

The rule's definitions and the seed lines migration `0041` freezes, from `services/engine` (the tests check that the migration's lines equal the code's):

```bash
.venv/bin/python -m app.spot.definitions   # SPOT_RULE_V1, SPOT_POLICY_V1 and SPOT_COST_V1 with their hashes
```

The new suites alone, on a fresh database of the scratch cluster ([above](#engine-on-a-scratch-postgresql-cloud)); the whole engine suite is the same command on `tests`:

```bash
ASL_DB_NAME=asl_m1_m6_<run> .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_spot_rule.py \
    tests/test_spot_money.py tests/test_spot_db.py tests/test_spot_account.py tests/test_spot_backtest.py \
    tests/test_spot_market_unit.py tests/test_spot_market_db.py tests/test_spot_migration.py tests/test_spot_api.py \
    tests/test_spot_live_unit.py tests/test_spot_live_db.py
```

The install check on the owner's PC, read-only, after the update: the schema, the definitions' hashes, the archive's moves, the futures run retired, the account, the spot run, the feed, the daily history, the newest readings, fills and backtests. VERIFIED on the PC on 2026-11-12 at 17:24 UTC in Git Bash ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)), through `docker exec` on the postgres container found by its Compose labels, which reads no env file (`docker compose` reads `.env`); the queries also VERIFIED on a scratch database at `0041_spot`. The update's record is the newest `update.json` under `.cache/deployments`.

```bash
pg=$(docker ps --filter label=com.docker.compose.project=adaptive-spot-lab --filter label=com.docker.compose.service=postgres --format '{{.Names}}')
docker exec -i -e PGOPTIONS="-c default_transaction_read_only=on" "$pg" psql -X -U asl -d asl <<'SQL'
SELECT version_num FROM alembic_version;
SELECT id, kind, version, sha256 FROM execution_definitions WHERE id IN ('SPOT_RULE_V1', 'SPOT_POLICY_V1', 'SPOT_COST_V1') ORDER BY id;
SELECT kind, count(*) FROM archive.moved_objects GROUP BY kind ORDER BY kind;
SELECT seq, state, stop_reason, kind, at FROM archive.futures_runs r JOIN archive.futures_run_events e ON e.run_id = r.id
WHERE e.kind = 'FUTURES_RETIRED';
SELECT cash, units, nav, valuation_valid, paused, reconciliation_failed FROM account_state;
SELECT seq, state, causes, started_by, started_at, start_equity, stopped_at, stop_reason FROM spot_runs ORDER BY seq DESC LIMIT 3;
SELECT status, reason, stream_connected, clock_verified, last_quote_at, instrument_checked_at, daily_checked_at FROM spot_feed_state;
SELECT count(*) AS days, to_timestamp(min(open_ms) / 1000) AS first_day, to_timestamp(max(open_ms) / 1000) AS last_day FROM spot_daily_bars;
SELECT utc_date, result, round(signal, 4) AS signal, round(volatility, 4) AS volatility, target, round(held, 4) AS held,
    action, outcome, codes, at FROM spot_rule_readings ORDER BY seq DESC LIMIT 5;
SELECT seq, reason, side, quantity, price, fee, filled_at FROM spot_fills ORDER BY seq DESC LIMIT 5;
SELECT seq, computed_at, method, to_timestamp(first_day_ms / 1000) AS first_day, to_timestamp(last_day_ms / 1000) AS last_day, days
FROM spot_backtests ORDER BY seq DESC LIMIT 2;
SQL
```
