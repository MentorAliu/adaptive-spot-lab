# Security and trust boundaries

The spot app's boundaries ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md)). The boundaries of M1 to M11 that went with their code (the sign-in, the research cluster and bridge, the agents' runtime, gateway, sources and provider keys, the coins, the futures) are in the [archived copy](archive/contracts/SECURITY.md), history only.

## Threat model

Protect the owner's PC, the financial simulation's integrity and the app's records from browser requests from other sites, malformed or hostile market data, untrusted dependencies, stale or concurrent workers and accidental misconfiguration. The app has no exchange access, no model and no credential of an outside service, which reduces the risk but does not remove it.

Repository instruction files guide developers; runtime validation and the database's grants enforce behaviour. A sentence in a prompt or a document is not a security control.

## Local owner access

**There is no sign-in since [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md)** (the owner's decision of 2026-10-25, [DECISIONS](DECISIONS.md#2026-10-25--no-owner-sign-in-and-no-setup-execplan-0042)): the owner uses the app alone on the PC. The owner boundary is the PC: the web is published on `127.0.0.1:3000` only, refuses a `Host` outside its allowlist (`421`, against DNS rebinding) and a cross-site mutation (Start's CSRF and Origin checks), and is the only holder of the service key the private API requires on every route but its health probes. Whoever can use a browser or a program on the PC acts as the owner; the app is paper only. The sign-in's passphrase, sessions and setup key are gone; the key file left on the PC is read by nothing. M1's sign-in and its ASVS review are in the [archived copy](archive/contracts/SECURITY.md#m1-observed-controls-and-asvs-mapping).

Do not expose the UI to the LAN or the internet. Requests are bounded (8 KiB bodies, strict Pydantic and Zod fields, an exact decimal parser, parameterized SQL); no admin token travels in a URL or a client bundle; private reads answer `private, no-store`. A network location or a guessed id is not permission to top up or to resume a paused run.

## The market feed

The market worker accepts only Binance's market-data-only spot hosts (`data-api.binance.vision`, `data-stream.binance.vision`) and fixed unauthenticated paths: `time`, `exchangeInfo`, `klines` and one combined stream (the book's ten levels and the 1-minute candle). It rejects signed or private parameters and redirects, resolves only its fixed hosts, refuses non-public address results and connects to the checked address with the original TLS name; answers and stream frames have byte limits, short timeouts, bounded retries and the provider's documented weights under the worker's own ceiling. Every answer is parsed strictly. The browser never contacts the provider. The worker holds only its `asl_market_worker` password and reaches the internet only through the `market_egress` network.

## Dependency and container controls

Review upstream skill and package changes before installing them in the coding environment; a skill can run tooling and deserves dependency-level scrutiny. Record official sources and resolved versions ([LIBRARIES](LIBRARIES.md)). Runtime services install nothing.

No secret in images, build arguments or fixtures. `.dockerignore` and `.gitignore` exclude local secrets, build outputs, test artifacts and data directories. Inspect final image layers and mounts. Pin verified versions or digests when actually known; no fictional audit or digest values. No Docker socket, `--privileged`, host home or repository mount in a runtime service ([DOCKER](DOCKER.md)).

## Audit and privacy

The owner's requests and their answers, top-ups, run events, latches, refused trades and reconciliation failures are recorded with stable correlation ids. Logs are structured and carry no secret, request body or path parameter. Account data is never publicly cached. Restores and corrections are recorded; a backup that lives only on the same PC is not a full backup strategy ([OPERATIONS](OPERATIONS.md#backup-and-restore)).

## Required abuse tests

Oversized JSON, unknown fields and query parameters, duplicate funding and run requests, client-side balance or price changes, cross-origin and wrong-Host requests, a stale fenced worker, concurrent steps, a forged or oversized live notification, a non-public provider address or a redirect, and secrets in logs. The expected outcome is a refusal with a safe record and no financial or credential side effect.

## Live trades (ExecPlan 0047)

[ExecPlan 0047 §8](archive/plans/0047-live-trades-and-pop-ups.md#8-data-and-trust-boundaries), kept for the spot fills. Read-only: nothing on these paths writes.
- **The browser** reaches only `GET /api/live` on its own origin, behind the Host check (421) and Start's `createCsrfMiddleware`: a request whose `Sec-Fetch-Site` is not `same-origin`, or that has no Fetch Metadata, is refused with 403. The browser names nothing but the last event's id, digits only (400 otherwise); the response is `no-store`, carries the frame policy and holds no detail of the engine's refusals (503).
- **The web server** alone holds the service key and asks the engine's `GET /v1/spot/live` with it; only the request's start is bounded (5 s), and the browser's leaving aborts the engine's request.
- **The API** answers the stream with the service key, `private, no-store` and a strict query, at most 8 streams at a time (`503 LIVE_BUSY`); its listener connects as the API's own database identity, in autocommit, holding no transaction.
- **The announcement** is a `pg_notify` on `asl_spot_live` that the execution worker sends as `asl_execution` after the step's commit, in a transaction of its own, so it can neither fail nor delay a trade; its payload names a source and kinds, never an amount, and the listener drops anything else on the channel (a payload over 1,000 bytes, unknown fields, a source other than `spot`, a kind other than up to 40 upper-case letters and underscores). A forged or lost notification can only make the streams read again, or later.
- **Desktop pop-ups** need the browser's own permission, asked only on the owner's click in the bell menu, and show only what the toasts show.

## M12 spot account boundary (ExecPlan 0060)

IMPLEMENTED ([ExecPlan 0060 §8](plans/0060-spot-trading-only.md#8-data-and-trust-boundaries)); VERIFIED in the engine's tests on a scratch PostgreSQL; installed on the owner's PC on 2026-11-12 ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)) and in force since. Paper only: the account is simulated from Binance's public spot data, with no key, signed or private endpoint, Testnet, Demo or model.
- **Fewer processes, secrets and identities.** `compose.yaml` runs `postgres`, `migrate`, `api`, `market-worker`, `execution-worker` and `web` (and the tools' and tests' profiles), with five secrets: `postgres_password`, `api_db_password`, `market_worker_password`, `execution_db_password` and `api_internal_key`. The agent worker, the runner, its egress gateway, the source fetcher and the evaluation worker, with their secrets and networks, are gone from Compose; the update of 2026-11-12 stopped and removed their containers and networks (none was left on the PC, `OBSERVED` in its record), and since [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md) the update file no longer handles them. The agents' sign-in files and provider keys left on the PC are read by nothing (rule 10).
- **Who writes money.** Only `asl_execution`, in the spot engine's fenced step under the execution lease and epoch, inserts runs, fills, valuations, references, latches, readings and backtests and their journal transactions, and updates only the columns its grants name (a run's state, causes, high-water NAV and stop; a request's one answer; a latch's one resolution; a backtest's old series). Migration `0041` grants these per column.
- **The market worker** (`asl_market_worker`) writes the spot market tables (books, candles, instruments, the feed's state and events) and reads nothing else of the account; it reaches only M2's market-data hosts through its egress network, as before.
- **The owner's API** (`asl_api`) reads the spot tables and inserts owner requests with only a request's own columns (`id`, `kind`, `run_id`, `idempotency_key`, `request_hash`), so it cannot insert an answered one; top-ups keep M1's path. The browser reaches the API only through the web's server functions and `/api/live`, with the Host and CSRF checks of M1 and ExecPlan 0047.
- **The archive.** Migration `0041` moves the futures, agents' and research tables into the schema `archive`, which no application identity can use (`REVOKE ALL ON SCHEMA archive FROM PUBLIC`); only the migration role reads it.

## ExecPlan 0061

No new secret, setting, service, network, host or grant; one field more in one read (`since_start`, read as `asl_api` from tables it already reads). Removed: the `argon2-cffi` package, imported by nothing since the sign-in went; `app.migrate --keep-logins`, which the futures' clean start used to keep the retired identities' logins (the migration runner grants no login or activation); the update file's handling of the retired services. Migration `0008`'s guard, which refuses to adopt the source and research identities while they can log in, keeps its test (`tests/test_migration_guard.py`).
