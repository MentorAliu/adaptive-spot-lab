# Market data and ingestion

Bitcoin's public spot data, as the spot app collects it ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12). The feeds of M2 to M11 (M2's observation boundary for BTC and SOL, the coins and their scan, the news feeds, the perpetual) are in the [archived copy](archive/contracts/MARKET_DATA.md), history only.

## Bitcoin's spot feed (ExecPlan 0060)

IMPLEMENTED by [ExecPlan 0060 §4.5](plans/0060-spot-trading-only.md#45-the-market-data-appspot_market); the parsing and storage VERIFIED in the engine's tests on recorded and SYNTHETIC payloads on a scratch PostgreSQL; NOT RUN against Binance in the cloud (it cannot reach it); OBSERVED on the owner's PC from the install of 2026-11-12: the stream, the clock, the instrument and the minutes, and since the fix below (installed 18:11 UTC) the whole daily history, 3,374 days to 2026-11-11 ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)). The market worker runs `app.spot_market.worker`.

- **Hosts:** Binance's market-data-only hosts M2 used ([EX-01](REFERENCES.md#ex-01)): REST `data-api.binance.vision`, stream `data-stream.binance.vision`, with M2's client checks: fixed hosts resolved to public addresses only, TLS, no redirect, no credential or private parameter, bounded answers, the worker's own weight ceiling and the IP-wide guard set from `exchangeInfo`'s allowance (weights read 2026-11-12: `time` 1, `exchangeInfo` 20, `klines` 2).
- **Stream:** one combined connection: `btcusdt@depth10@100ms` (the ten best levels a side; the newest book of each second is stored in `spot_quotes` once the second is over) and `btcusdt@kline_1m` (each 1-minute candle as it changes, at most once a second, final once Binance marks it closed, in `spot_bars`). The plan's `bookTicker` stream is not used: the book's best levels give the best bid and ask. A connection is rotated after 23 hours and reconnected after 10 seconds of silence.
- **REST:** the clock (`/api/v3/time`, every minute, the best of three samples; verified when the offset is at most 1,000 ms and the uncertainty at most 500 ms, for 150 s); the instrument (`exchangeInfo`, at the start and every 30 minutes, usable for an hour; the filters `PRICE_FILTER`, `LOT_SIZE`, `MARKET_LOT_SIZE`, `NOTIONAL` and `MIN_NOTIONAL` are applied, every other filter kept and named); missing 1-minute candles of the last 30 days (at the start and every 5 minutes, every minute while some are lacking; a REST row is final only when it closed before the provider's clock at the answer); and every final daily candle since 2017-08-17 into `spot_daily_bars` (1,000 a request, four the first time, then 90 seconds after each UTC midnight; a day is final a minute after its end). A day's close time must lie inside its day; a day the exchange closed early is stored as Binance records it, its close the last trade before the halt, and noted once (`DAILY_CLOSED_EARLY`, with the close time Binance gives): BTCUSDT's 2018-02-08 closes at 00:28:14.788 UTC, the only such day to 2026-11-12 ([0060 §13 item 16](plans/0060-spot-trading-only.md#13-decision-log)). A 1-minute candle must close at its minute's end. A candle more than 2 s ahead of the measured clock is dropped.
- **State:** `spot_feed_state` is `CONNECTED` only while the stream delivers, the clock is verified, the instrument is usable and was checked in the last hour, and the newest book is at most 5 s old; every failure is recorded in `spot_feed_events` with its cause and retried after a wait. The account decides from the stored times itself ([RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060): a book at most 2 s old to trade, a best bid at most 5 s old to value); the state is what the pages show.
- **Retention:** books older than 2 days and 1-minute candles older than 30 days are deleted every hour; daily candles are kept for good (the rule and the backtest read them).
- **Charts:** the Cockpit's Bitcoin chart reads 1-minute candles grouped to 1m, 5m, 15m, 1h or 4h, and the daily candles for 1d.

## Permitted access

Only Binance's public market data for BTCUSDT spot, from the market-data-only service, which documents unauthenticated public endpoints [EX-01](REFERENCES.md#ex-01). Never a private, account or signed endpoint, Binance Demo, Testnet, or a trading SDK that asks for credentials. A point-in-time observation of the provider (such as M2's public smoke of 2026-09-27, [ExecPlan 0003](archive/plans/0003-market-data-charts.md)) is not a guarantee of later availability.

## Ingestion responsibilities

One worker owns the one connection; no browser, page or strategy opens its own. It collects what the account and the rule need: the instrument and its filters, the book for fills and valuations, the 1-minute candles for the chart, and every final daily candle for the rule and the backtest. It keeps timeouts, bounded retries with back-off, reconnection, clock checks, duplicate suppression, the provider's rate limits and gap detection as the provider documents them [EX-02](REFERENCES.md#ex-02). Freshness is decided where the engine trades and values, not by how often a page polls: a socket that looks connected can still deliver a book too old to use.

## Connection failure and recovery

On losing the book the engine stops trading and valuing until a fresh one arrives; nothing is filled at a guessed price, and the pages show the book's age. After a reconnection the worker checks the clock and the instrument again and catches up the final candles it lacks. A historical candle repairs the chart and the rule's history; it never shows that the account was awake and trading while it was not, and no missed trade is made up at a historical price.

## Retention and resources

The financial records, the readings and the backtests are never pruned. Books are kept 2 days and 1-minute candles 30 days (deleted hourly, above); the daily candles and the instruments are kept for good, so the rule and the backtest can always be recomputed from what is stored. A losing run's records are never deleted to improve what is reported.

## Other market factors

The app reads only Bitcoin's own spot prices. No news, derivatives, on-chain, sentiment or macro source is collected (the news and event feeds of M9 and the event calendar of ExecPlan 0058 went with the agents), and the app does not claim to observe everything that moves the price. Adding a source would be a plan the owner approves, with its own hypothesis, timing and test against [TRADING](TRADING.md).
