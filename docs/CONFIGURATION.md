# Configuration and activation gates

The settings the spot app reads ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md), which dropped from this document the settings nothing reads any more). The settings of M3 to M11 (the experiments' activation and cost scenarios, the evaluation worker, the agents' runtime, profiles and provider keys, the research envelope, the sources, the coins, the AI backtests) are in the [archived copy](archive/contracts/CONFIGURATION.md), history only.

## Layers and source of truth

- **The definitions** `SPOT_RULE_V1`, `SPOT_POLICY_V1` and `SPOT_COST_V1` are code with canonical hashes, frozen by migration `0041` in `execution_definitions`; the engine refuses to run when a stored definition differs from the code. The policy names the valuation (`VALUATION_BID_V1`); the backtest (`SPOT_BACKTEST_V1`) records the rule's and the cost's hashes with each result. Their values live in [RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060); a change is an update the owner installs, never a setting.
- **Permissions** live in [AUTONOMY_MATRIX](AUTONOMY_MATRIX.md); nothing in the environment grants one.
- **Environment settings** (below) only turn services on, name the database and the paths. A missing mandatory value is refused, never replaced by zero. There is no live switch, exchange key or model setting.
- **Secrets** are files under `secrets/` (or `ASL_SECRET_DIR`), outside Git, images and logs.

## Fixed scope

| Setting | Value |
|---|---|
| Product | A local single-owner paper-trading app that trades Bitcoin spot by itself |
| Funding | `10000.00` USDT, contributed by the app once; owner-confirmed top-ups only |
| Universe | BTCUSDT spot, long or cash; no short, borrow, margin or leverage |
| Decider | `SPOT_RULE_V1`, code; no model |
| Market data | Binance's market-data-only spot hosts, unauthenticated ([MARKET_DATA](MARKET_DATA.md)) |

## Environment settings

| Setting | Read by | Meaning |
|---|---|---|
| `ASL_MARKET_ENABLED` | `market-worker` | `1` collects Binance's public spot data; anything else idles the worker. Default `0` in `compose.yaml`; `1` in the owner's `.env` |
| `ASL_MARKET_MODE` | `market-worker` | Only `PUBLIC` (the default) is accepted |
| `ASL_EXECUTION_ENABLED` | `execution-worker`, the update file | `1` runs the spot engine under the execution lease; anything else idles the worker with a `DISABLED` heartbeat. Default `0`; `1` in the owner's `.env` |
| `ASL_EXECUTION_HEARTBEAT` | `execution-worker` | The heartbeat file its health check reads (default `/tmp/execution-heartbeat.json`) |
| `ASL_DB_HOST`, `ASL_DB_NAME` | the engine's services, the tests | The database (defaults `postgres` and `asl`) |
| `ASL_DB_ROLE` | the engine's services | Which identity to connect as: `api` (default), `market_worker`, `execution` or `migration` |
| `ASL_DB_PASSWORD_FILE` | the engine | Overrides the identity's password file (tests only) |
| `ASL_INTERNAL_KEY_FILE` | the API, the web server | Overrides the service key's file (default `/run/secrets/api_internal_key`; tests only) |
| `ASL_API_BASE_URL` | the web server | The private API (`http://api:8000` in Compose) |
| `ASL_SECRET_DIR` | Compose, the update file | Where the secret files are (default `./secrets`) |
| `ASL_FRONTEND_SUBNET`, `ASL_PRIVATE_SUBNET`, `ASL_MARKET_EGRESS_SUBNET` | Compose | The three networks' subnets |
| `WEB_PORT` | Compose | The web's port on `127.0.0.1` (default `3000`) |
| `ASL_TEST_ISOLATED` | the tests | `1` permits the test-only overrides, and only on an `asl_m1_` database; never set on the owner's installation |

The secrets: `postgres_password` (the migration role), `api_db_password`, `market_worker_password`, `execution_db_password` and `api_internal_key`. `tools/setup-local.ps1` creates a missing one with random bytes and never overwrites one; the update file runs it when the env file names no other secret directory. The secrets and sign-in files of the retired services left on the PC are read by nothing.

## Activation and readiness

The app needs no activation step since [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md): once the update has applied the migration, the API contributes the starting 10,000 USDT at its first start and the engine starts the first run by itself. Readiness requires the schema the code was built for (`0041_spot`), the execution lease and its fencing, a reconciled account and, for any trade, a fresh book, a verified clock and a checked instrument ([ARCHITECTURE](ARCHITECTURE.md#exact-authority-sequence)). An unknown fee is never zero: `SPOT_COST_V1` names its rate.

## Operational settings and changes

Resource limits, health checks, polling intervals and retention are set from observations of the PC and recorded where they are used ([DOCKER](DOCKER.md), [MARKET_DATA](MARKET_DATA.md)). A change of any of them is an update: it never rewrites an earlier run's records. Top-ups change contributed capital only; they do not reset the latches or the high-water NAV.
