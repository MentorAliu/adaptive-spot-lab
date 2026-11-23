# HTTP, event and service contracts

The engine's private API as the spot app ships it ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md)). The routes of M1 to M11 that went (the owner's sign-in, the approvals and experiments, the agents, the research, the coins, the futures) and their sections are in the [archived copy](archive/contracts/API_CONTRACTS.md), history only.

## Boundary

The browser talks only to the same-origin TanStack Start server (the BFF). The BFF calls the private FastAPI service with the service key (`X-Internal-Key`), which the browser never receives; there is no owner sign-in since [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md), and the BFF on the PC's loopback is the owner. Private networking alone is not financial authority: the engine validates every request against current state inside its own transaction ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md)).

Routes are versioned under `/v1`. The OpenAPI schema `services/engine/openapi.json` is generated from the implemented DTOs (drift check `python -m app.export_openapi --check`), and the web's types `apps/web/src/generated/api.ts` from it (`pnpm run api:check`); the web validates the responses it relies on with Zod at runtime. Amounts are exact decimal strings, times UTC ISO strings, statuses enums; a value that is unavailable is `null`, with its reason where it could be misread ([DATA_CONTRACTS](DATA_CONTRACTS.md)). Every route but the two health probes needs the service key and answers `Cache-Control: private, no-store`. Unknown query parameters are refused with `422`, and request bodies over 8 KiB with `413`.

There is no route that sets a balance, places an order, runs SQL, changes the rule, its policy or its costs, uploads an exchange key or deploys code.

## The routes in use

| Route | Answers |
|---|---|
| `GET /v1/health/live`, `GET /v1/health/ready` | The process and the database's readiness (the schema `0041_spot`); no key |
| `GET /v1/system/status` | The services' health: the feed, the execution worker, the database's schema |
| `GET /v1/account`, `GET /v1/account/workspace`, `GET /v1/account/requests/{key}` | The account and its funding history (M1) |
| `POST /v1/account/topups/draft`, `POST /v1/account/topups`, `POST /v1/account/topups/{id}/retry`, `POST /v1/account/topups/{id}/cancel` | The owner's top-up: review, confirm by idempotency key, retry, cancel a pending one (M1's semantics, [LEDGER](LEDGER.md)) |
| `GET /v1/market` | Bitcoin's spot book (best bid and ask with their ages), the instrument and the feed's state |
| `GET /v1/market/candles?interval=&limit=` | Candles for the chart: `1m`, `5m`, `15m`, `1h`, `4h` from the stored 1-minute candles, `1d` from the daily candles |
| `GET /v1/spot` | The overview: the account (equity, USDT, BTC and its value, the share in Bitcoin, performance), the run with its `since_start` (below), its limits, today's reading and the next one's time, the feed |
| `GET /v1/spot/trades?cursor=&limit=`, `GET /v1/spot/readings?cursor=&limit=` | The fills and the daily readings, newest first, a page at a time |
| `GET /v1/spot/activity?after=` | The toasts' feed: the fills after a cursor |
| `GET /v1/spot/live` | Server-sent events (below); `Last-Event-ID` resumes |
| `GET /v1/spot/markers?since_ms=` | The buys and sells for the chart's markers |
| `GET /v1/spot/valuations?window=24h\|7d\|all` | The account's value over the window |
| `GET /v1/spot/backtest?window=SINCE_2019\|SINCE_2023\|LAST_12_MONTHS` | The newest stored backtest's window (`READY`, `NOT_COMPUTED` or `SCHEMA_PENDING`): the rule's and holding Bitcoin's totals, a row a year, the daily values and the trades |
| `GET /v1/spot/definitions` | The three definitions with their hashes and the running code's identity |
| `POST /v1/spot/requests` | The owner's `PAUSE`, `RESUME`, `STOP` (Stop and sell) or `START`, by idempotency key and bound to the run the owner saw; the answer is "accepted", and the engine applies it at its next step (`APPLIED` or `REJECTED` with reasons) |
| `GET /v1/spot/requests/{key}` | A request's outcome |

## The run against holding Bitcoin (ExecPlan 0061)

`GET /v1/spot`'s `run` carries `since_start` ([ExecPlan 0061 §4.3](plans/0061-clean-up-after-the-spot-switch.md#43-the-cockpits-comparison)), ExecPlan 0060 §4.10's descriptive comparison, paired by day. Between the run's first and newest `TIMELY` daily references (`spot_daily_references` joined to its `VALID` valuation of this run, valued from the run's start up to its stop, or now): `account` is the newest NAV over the first NAV minus one, and `bitcoin` is the daily close of the day before the newest reference over the same of the first, minus one (each close is Bitcoin's last price at that UTC midnight). Both are ratios to 8 places, as the page's other ratios; `from_at` and `at` are the two valuations' times and `from_price` and `price` the two closes. A top-up does not move `account` (NAV per unit). `since_start` is `null` until the run has two such days; a reference made late (`LATE_CONSERVATIVE`, the PC off at midnight) is left out rather than paired with a price from another moment. It is read only: nothing here writes, and the comparison is not a pass or fail.

## Mutation semantics

Every mutation (a top-up and its retry or cancel, a run request) carries an idempotency key (`[A-Za-z0-9_-]{8,64}`) stored with a canonical hash of its body: the same key and body answer the original record, the same key with another body is `409 IDEMPOTENCY_CONFLICT`. Idempotency records survive restarts and are kept with the financial history. A top-up confirms the exact draft it reviewed (amount, account version and hash); a stale draft is `409 DRAFT_MISMATCH` or `ACCOUNT_VERSION_CONFLICT`. A run request names the run the owner saw; another run is `409 RUN_CHANGED`.

Accepting a run request is not its effect: the answer is the recorded request, and the page reads the outcome the engine records at its next step (`GET /v1/spot/requests/{key}`). Cursors page over a stable order with bounded limits; no route accepts a column name or SQL from a filter.

## Errors

A refused request answers `{code, message, correlation_id, retryable}` with the status that fits: `422` for a malformed input, `409` for stale state or an idempotency collision, `404` for an unknown request, `401` without the service key, `503` while a dependency is unavailable. The domain codes include `NOT_FUNDED`, `RUN_REQUIRED`, `RUN_LIVE`, `RUN_NOT_LIVE`, `RUN_STOPPING`, `RUN_CHANGED`, `SPOT_SCHEMA_PENDING`, `POLICY_PAUSED`, `RECONCILIATION_REQUIRED`, `VALUATION_UNAVAILABLE`, `INVALID_VALUATION`, `NUMERIC_LIMIT` and `IDEMPOTENCY_CONFLICT`. `X-Request-ID` (when well formed) becomes the correlation id, echoed as `X-Correlation-ID`. Errors carry no SQL, path, token or credential; the request log records the area, method, status, correlation id and duration, never bodies, credentials or path parameters. A rule that holds still, or a request the engine rejects, is an auditable result, not a crash.

## The live stream

`GET /v1/spot/live` ([ExecPlan 0047](archive/plans/0047-live-trades-and-pop-ups.md), kept for spot by 0060) is an event stream (`text/event-stream`, `X-Accel-Buffering: no`, a `: ping` comment after 15 s idle; the first event carries `retry: 3000`):
- `ready`, `id` the ledger's newest sequence, data `{state, cursor}`: the first event without `Last-Event-ID` or with one that nothing followed; again when the ledger is older than the stream's cursor (a restored database).
- `activity`, `id` the newest sequence, data `{after, state, cursor, count, items}`: what `GET /v1/spot/activity?after=` answers after the stream's cursor.
- `change`, no `id`, data `{source, kinds}`: a committed step that changed more than the valuation but posted no fill.

`422` for a `Last-Event-ID` that is not a sequence (digits, at most 19, no leading zero); `503 LIVE_UNAVAILABLE` (retryable) while the API's listener is not listening, `503 LIVE_BUSY` while 8 streams are open. After each committed step that changed more than the valuation, the execution worker runs `pg_notify('asl_spot_live', '{"source":"spot","kinds":[…]}')` in a transaction of its own; the API listens as its own identity and wakes the streams, which read the records again. The payload names kinds, never a value; a lost announcement costs at most the listener's 30 s sweep, and an announcement can never fail a trade. A stream ends when its client leaves, when the listener loses its connection (the browser resumes it), after a failed read, and within 3 s of the API's stop. A closed stream never interrupts the worker's step.

## Required contract tests

Decimal round trips, null and unavailable values, UTC precision, idempotent top-ups and run requests (same key, other body), stale drafts and runs, the service key, unknown query parameters and oversized bodies, safe errors, the stream's events, resumption and limits, and the generated types' drift (`services/engine/tests/test_spot_api.py`, `test_api.py`, `test_spot_live_unit.py` and the web's schema tests; [TESTING](TESTING.md)). A response that matches its schema is not thereby correct.
