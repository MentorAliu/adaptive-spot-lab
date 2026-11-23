# Architecture and trust boundaries

The shape of the spot app ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12), IMPLEMENTED and OBSERVED on the owner's PC since the install of 2026-11-12. One account trades Bitcoin spot on paper by a code rule; no model, agent runner, research runner or source fetcher exists. The design up to M11 (the agents' paths and roles, the research services, M3's and M5's shapes) is in the [archived copy](archive/contracts/ARCHITECTURE.md), history only.

## Services

| Service | Responsibility | Access |
|---|---|---|
| `web` | TanStack Start SSR pages (Cockpit, Trades, Backtest, Settings) and the same-origin BFF; relays the live trades as one event stream per browser | The private API with its internal key; no database or exchange access |
| `api` | Projections, the owner's requests (Pause, Resume, Stop and sell, Start) and top-ups; the account's starting 10,000 USDT at its first start; the live trades stream | Role `asl_api`: reads the spot and account tables, inserts the owner's requests and the funding requests |
| `market-worker` | Binance's public spot feed (`app.spot_market`): the order book each second, 1-minute candles, every final daily candle since 2017-08-17, the instrument and the clock | Role `asl_market_worker`: writes the spot market tables only; the `market_egress` network to Binance's market-data-only hosts ([MARKET_DATA](MARKET_DATA.md)) |
| `execution-worker` | The single fenced paper-execution authority (`app.spot.worker`): the one-second step, the fills, the postings, reconciliation every 5 minutes; the backtest beside it, outside the step | Role `asl_execution`; the private network only |
| `postgres` | The ledger, the account, the runs, readings, fills and backtests; the retired tables in the `archive` schema, readable by the migration role only | The private network only |
| `migrate` | Alembic to head, run by the update | The migration role |

```text
Binance's public spot data -> market-worker -> spot_quotes, spot_bars, spot_daily_bars, spot_instruments, spot_feed_state
                                                   |
execution-worker step, one fenced transaction a second:
  owner requests -> first run -> stopping run's sale -> valuation, day reference, latches -> run state -> SPOT_RULE_V1
                                                   |
        fill on the stored book (SPOT_COST_V1) -> journal postings (app.spot.ledger) -> account_state, account_holdings
                                                   |
        announcement on asl_spot_live -> api listener -> event stream -> web (toasts; pages read again)
execution-worker, outside the step: SPOT_BACKTEST_V1 on spot_daily_bars -> spot_backtests
```

The browser and the API cannot set a balance: the owner's requests are rows the engine validates and applies in its own transaction; top-ups go through M1's funding path ([LEDGER](LEDGER.md)). One-shot tooling and test services (`web-tools`, `engine-tools`, `engine-tests`) sit behind Compose profiles and never run with the app ([DOCKER](DOCKER.md)).

## The engine's code

One engine codebase and image serve the API and both workers, each under its own database identity ([SECURITY](SECURITY.md)); Alembic is the one migration owner.
- `app.spot`: the account's engine: the rule (`rule`), the definitions and their hashes (`definitions`), the fill and cost model on the stored book (`money`), the postings (`ledger`), the one-second step (`engine`) and its fenced writes (`store`), reconciliation (`reconcile`), the owner's requests (`requests`), the backtest (`backtest`), the pages' reads (`views`), the live announcements (`live`) and the worker (`worker`).
- `app.spot_market`: Binance's public spot feed and its reads ([MARKET_DATA](MARKET_DATA.md)).
- `app.execution`: the pieces of M3's engine the spot account keeps: the fenced execution lease (`store`), the exact number policy (`numbers`), the deterministic row identities (`lifecycle`), a frozen definition's canonical hash (`definitions`), the day's reference NAV (`risk`), and the `execution-worker` service's entry point and health check (`worker`, `health`).
- `app.accounting`: M1's account, top-ups, valuation of the holdings and reconciliation; the only code that posts funding to the ledger, as `app.spot.ledger` is for fills.
- `app.main`: the FastAPI service ([API_CONTRACTS](API_CONTRACTS.md)); `app.migrate`: the bounded migration run the update uses.

## Exact authority sequence

1. The execution worker holds the single execution lease, renews it every 2 s and stops issuing work once its last renewal is more than 7 s old; every step's writes check the account's fencing epoch, so a worker that lost the lease writes nothing.
2. Each step, in one transaction and in this order: the owner's requests, each answered once; the first run, once the account is funded; a stopping run's sale of everything; the valuation, the day's reference and the latches; the run's state; then `SPOT_RULE_V1`'s daily reading and its trade, at the first step at or after 00:05 UTC and every 15 minutes while the day is not spent.
3. A trade is sized and capped by `SPOT_POLICY_V1`, needs a book at most 2 s old, a clock the feed verified and an instrument checked in the last hour, is filled on the stored book with `SPOT_COST_V1`'s fee and posted by `app.spot.ledger` in the same transaction; without its inputs it is refused with its code and tried again, never guessed.
4. A latch, a paused run and an integrity hold stop buying, never selling: the drawdown stop's and the owner's Stop and sell need no model and no approval, only a valid book.
5. A failed step rolls back whole, is recorded and is not retried as it was; the worker backs off and recovers from the database. Reconciliation (every five minutes, and at the worker's and the API's start) checks every projection against its append-only sources; a failure sets the integrity hold until a later run passes.

## Server and frontend boundaries

Browser requests go through the same-origin Start BFF. Server functions and routes are thin adapters with the service key; loaders may run in the browser and are not automatically secret-safe [TS-03](REFERENCES.md#ts-03). Query caches are request-scoped on SSR. The engine validates every financial and control action independently. API data carries decimal strings, UTC timestamps, explicit quality states and generated transport types ([FRONTEND](FRONTEND.md)).

## Future portability

Only the paper broker exists, and no Binance account is integrated. Another broker, another coin, a model, or a paid transport would need a plan the owner approves, with its own authorization, tests, access controls and operational review. A clean interface does not itself authorize live execution.
