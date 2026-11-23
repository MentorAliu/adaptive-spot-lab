# Adaptive Spot Lab

Adaptive Spot Lab is a self-hosted Bitcoin trading app that trades on paper. It runs on your own computer in Docker, watches Binance's public spot market every second, and once a day lets a fixed rule written in code decide how much of a virtual 10,000 USDT account to hold in Bitcoin. It fills each trade against the real order book, after fees, keeps the books like a bank ledger, and tests the same rule on Bitcoin's whole history since 2017 so you can see how it would have done.

It only ever uses virtual money: there are no exchange keys, no real orders and no live switch. No AI model takes part while the app runs; the rule is plain code, and every number on the page comes from the market data and the ledger.

## Contents

- [What it does](#what-it-does)
- [The rule](#the-rule)
- [How it's built](#how-its-built)
- [Run your own copy](#run-your-own-copy)
- [Updating your copy](#updating-your-copy)
- [Working on the code](#working-on-the-code)
- [How this project was made](#how-this-project-was-made)
- [Security and licence](#security-and-licence)

## What it does

- **Trades by itself.** On first start the app funds its account with 10,000 virtual USDT and starts a run. From then on it trades with no clicks, also with the browser closed, as long as the computer and Docker are on.
- **Fills against the real market.** Every trade walks the ten best levels of the order book stored that second, pays Binance's regular 0.10% fee and a small slippage, and respects the exchange's lot size and minimum order rules. With a missing or stale price the trade is refused with a reason and tried again, never guessed.
- **Protects what it holds.** Hard limits in code stop buying after a 2% fall in a day and stop the run after an 8% fall from its best value. Selling is never blocked.
- **Shows its work.** Four pages:
  - **Cockpit:** the account's value, today's reading of the rule, the newest trades, and the run against simply holding Bitcoin.
  - **Trades:** every buy and sell with its price, fee and reason, and every daily reading of the rule.
  - **Backtest:** the same rule on Bitcoin's daily history since 2019, since 2023 and over the last 12 months, refreshed each day.
  - **Settings:** the run's controls (Pause, Resume, Stop and sell, Start), the rule and its limits with their hashes, virtual top-ups, and the health of the feed, the engine and the database.
- **Never hides a failure.** A computer that was off is not replayed afterwards, a late reading is recorded as late, and reconciliation checks every balance against the ledger every five minutes.

## The rule

The rule (`SPOT_RULE_V1`) is a slow trend-following rule with volatility targeting, long or cash, never short:

1. **Direction.** Just after midnight UTC it compares yesterday's close with the closes 30, 91 and 365 days before. The share of those that are up (negative counts as zero) is how much of the target to hold.
2. **Size.** The target is scaled so the Bitcoin held moves the account by about 5% a year: the more Bitcoin's price has been moving, the less of it the account holds.
3. **Trade.** When the target and what's held differ by more than 3% of the account, it buys or sells the difference on the order book.

The rule, its limits and its cost model are code with a hash, stored in the database when they're installed. The engine refuses to run if what's stored differs from the code, and every run records which version it traded by. [docs/RISK_POLICY.md](docs/RISK_POLICY.md) has every number.

## How it's built

```text
Binance public spot data ──► market-worker ──► PostgreSQL ◄── execution-worker (one-second step, the rule, fills, ledger)
                                                   ▲
                       browser ──► web (TanStack Start) ──► api (FastAPI)
```

| Service | What it does |
| --- | --- |
| `web` | TanStack Start server-rendered pages and a same-origin back end for the browser, with a live event stream for new trades |
| `api` | FastAPI: the pages' reads, the owner's requests and top-ups, the live trades stream |
| `market-worker` | Binance's public spot feed: the order book each second, 1-minute candles, every daily candle since 2017 |
| `execution-worker` | The only part that can trade: a fenced one-second step that applies the owner's requests, values the account, runs the rule, fills and posts to the ledger in one transaction; the backtest runs beside it |
| `postgres` | The ledger, the account, runs, readings, fills and backtests |

- **Back end:** Python 3.13, FastAPI, SQLAlchemy 2, psycopg 3, Alembic (41 migrations), exact `Decimal` and `NUMERIC` money everywhere.
- **Front end:** React 19, TanStack Start, Router, Query and Table, Zod, React Hook Form, shadcn/ui on Tailwind CSS 4, and TradingView's Lightweight Charts.
- **Database safety:** each service connects as its own PostgreSQL role with only the grants it needs. The ledger is append-only, and a lease with a fencing epoch makes sure only one worker can ever trade.
- **Runtime:** Docker Compose, with non-root containers, read-only workers, Docker secrets, a private network for the database and the API, and the web published on `127.0.0.1` only.
- **Tests:** 216 engine tests on a real PostgreSQL (pytest and Hypothesis), 144 web unit tests (Vitest) and browser suites (Playwright), covering accounting invariants, rounding, stale data, concurrent workers and crash recovery.

[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains the design in full.

## Run your own copy

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine with Compose on Linux) and [Git](https://git-scm.com). The images take about 1.2 GB, and the first build takes a few minutes. The app was built for Windows, where the setup and update scripts run in Windows PowerShell; on macOS or Linux, use the shell commands.

1. **Get the code.**

   ```bash
   git clone https://github.com/MentorAliu/adaptive-spot-lab.git adaptive-spot-lab
   cd adaptive-spot-lab
   ```

2. **Create the secrets** (random database passwords and an internal key, in `secrets/`, which Git ignores).

   Windows PowerShell:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File tools\setup-local.ps1
   ```

   macOS or Linux:

   ```bash
   mkdir -p secrets
   for name in api_internal_key postgres_password api_db_password market_worker_password execution_db_password; do
     openssl rand -hex 32 | tr -d '\n' > "secrets/$name"
   done
   ```

3. **Turn on the market feed and the engine.** Create a file named `.env` in the app folder with these two lines:

   ```dotenv
   ASL_MARKET_ENABLED=1
   ASL_EXECUTION_ENABLED=1
   ```

4. **Build and start the app.**

   ```bash
   docker compose --profile market --profile execution up -d --build
   ```

5. **Let the engine sign in to the database, once.** The engine's database role is created without a login, so that nothing can trade until you allow it. This gives it the password from `secrets/`:

   Windows PowerShell:

   ```powershell
   $pw = Get-Content secrets\execution_db_password -Raw
   "ALTER ROLE asl_execution LOGIN PASSWORD :'pw';" | docker compose exec -T postgres psql -U asl -d asl -v "pw=$pw"
   ```

   macOS or Linux:

   ```bash
   echo "ALTER ROLE asl_execution LOGIN PASSWORD :'pw';" | docker compose exec -T postgres psql -U asl -d asl -v pw="$(cat secrets/execution_db_password)"
   ```

   It prints `ALTER ROLE`. Within a few seconds the engine takes over, funds the account and starts the first run.

6. **Open <http://localhost:3000>.** The market worker loads Bitcoin's daily history first, so the backtest and the rule's first reading appear once that's stored. The first trade comes at the first reading, just after midnight UTC, if the rule wants to hold Bitcoin.

To stop the app, run `docker compose --profile market --profile execution stop`. Your data stays in the `postgres_data` Docker volume; back it up together with `secrets/`.

## Updating your copy

**Windows:** copy `tools\update.cmd` to the app folder as `update-app.cmd`, and double-click it when you want the newest version. It fetches `main`, backs up the database, applies new migrations, recreates the changed services and checks that every page answers. It waits by itself if it's run during the daily reading (23:55 to 00:10 UTC).

**macOS or Linux:** back up the database, then:

```bash
git pull
docker compose --profile market --profile execution up -d --build
```

The `migrate` service brings the database to the newest schema before the other services start.

## Working on the code

From the repository root, after `pnpm install --frozen-lockfile`:

```bash
pnpm typecheck
pnpm lint
pnpm test:unit
pnpm build
```

The engine lives in `services/engine` and uses [uv](https://docs.astral.sh/uv/): `uv sync --frozen`, then `uv run ruff check .` and `uv run pytest`. Its database tests need a disposable PostgreSQL; [docs/COMMANDS.md](docs/COMMANDS.md) has the exact commands, including the browser suites.

## How this project was made

The app was built with AI coding agents, mostly Claude Code, working under written rules: one plan per change, every owner decision recorded, and nothing called done without the test output to prove it. That trail is all in `docs/`:

- [docs/STATUS.md](docs/STATUS.md): what's running now and what's next.
- [docs/DECISIONS.md](docs/DECISIONS.md): every decision, with the reasons.
- [docs/plans/](docs/plans/) and [docs/archive/plans/](docs/archive/plans/): the execution plans, from the first paper broker to today's spot-only app.
- [docs/TRADING.md](docs/TRADING.md): how trading ideas are judged before they reach the account: a claim needs a measurement, and most ideas are checked and rejected.
- [AGENTS.md](AGENTS.md): the rules the coding agents follow.

The project went through several designs along the way, including AI agents that researched and traded several coins and a simulated Bitcoin future. Each was measured, and the simpler code rule won. Those designs are retired, and their plans and results are kept in [docs/archive/](docs/archive/README.md).

## Security and licence

Please report security problems privately: see [SECURITY.md](SECURITY.md). Adaptive Spot Lab is released under the [MIT licence](LICENSE).

This is a paper-trading experiment, not financial advice. Its backtests are modelled on history, not real fills, and past results don't predict future ones.
