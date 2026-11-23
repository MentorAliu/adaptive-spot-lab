# ExecPlan 0006 — normal public market collection activation

## Goal and owner authority

Enable the already accepted M2 public BTCUSDT/SOLUSDT observation worker on the normal local paper app, then verify real feed and browser states. The owner explicitly requested activation on 2026-09-28 after asking why collection was disabled. This authority covers public collection only. Paper trading, model runtime, strategies, valuation posting, private/signed exchange access and owner financial controls remain disabled or unchanged.

## Observed starting state and boundaries

- OBSERVED: source `bdf8c163b7aa0ba93c5efe2ee2dbdd9c82266821`, clean `main`; normal web/API/PostgreSQL healthy, schema `0004_m2_completion`, no market-worker container, and BTCUSDT/SOLUSDT feed rows `DISABLED`. The existing market-worker secret was present. Host C: free space was 660,541,841,408 bytes and PostgreSQL's Docker filesystem reported 776,707,824 KiB available.
- The worker is an optional Compose `market` profile, with `ASL_MARKET_ENABLED` defaulting to `0`, its own market database role/secret, private and market-egress networks, read-only root, no published port, 1 CPU, 512 MiB and 128 PID limits. It does not own accounting tables. The normal app remains paper-only.
- The source documents and installed implementation permit only fixed unauthenticated Binance Spot market-data endpoints. The [official market-data-only documentation](https://developers.binance.com/en/docs/products/spot/faqs/market_data_only) was checked on 2026-09-28; current reachability and eligibility still required a live preflight.

## Activation requirements and evidence

| Requirement | Result |
|---|---|
| Backup, schema and storage | VERIFIED: protected normal PostgreSQL custom dump at `.cache/deployments/market-activation-20260928a/market-activation-20260928a.dump`, 83,802 bytes, SHA-256 `d5f8ce1e1991a54f7bb8390950e7206d7d6cd7d8ab606c5af1036f87778780af`. Schema `0004_m2_completion`; no migration was run. Host/Docker free space exceeded the worker's 5 GiB market-table stop cap. |
| Current public-provider preflight | VERIFIED: the bounded `public-smoke` Docker tool exited 0 in 6.102 seconds with clock offset 9.369 ms and uncertainty 126.994 ms; both instruments were `TRADING`, Spot eligible, and yielded three finalized REST klines plus live quote and candle stream frames. No database write or owner credential was involved. Log retained under the protected task directory. |
| Explicit public-only configuration | IMPLEMENTED: ignored local `.env` now contains only `ASL_MARKET_ENABLED=1`. Effective Compose config confirmed database `asl`, profile `market`, one worker secret, read-only root and only `private` plus `market_egress` networks. No `COMPOSE_PROFILES` setting or synthetic fixture flag was added. |
| Normal worker and data | VERIFIED: `docker compose --profile market build market-worker --quiet` and `docker compose --profile market up -d --no-deps market-worker` exited 0. Image `sha256:35a8399b108e7170e219e32b62872ad2ff945442199157953cc974848e257780` runs with `unless-stopped`; lease epoch advanced to `2`, collection ID `ad48bcda-4576-4430-a78d-6b795d0b2841`. Both feeds reached `CONNECTED`, publications rose to at least 1,486, and the normal API reported both quotes usable, no queue warning or overload. |
| Browser and other capabilities | VERIFIED: the authenticated in-app Markets view rendered a SOLUSDT hourly candlestick chart and exact-value table from public observations; the normal System page returned HTTP 200 with market data `ready` and paper trading `disabled`. A Chromium screenshot is retained at `.cache/deployments/market-activation-20260928a/system-market-ready.png`. Model runtime stayed `unconfigured`. |

## Operation and recovery

The ignored `.env` retains the enable flag for future Compose invocations in this checkout. The optional `market` profile must still be selected to create the service; the current container has Docker's `unless-stopped` restart policy. Future normal app recreation should include `docker compose --profile market up -d` when public collection is intended. Continue to inspect feed quality, quote usability, original source/receipt times, lease/queue state, incidents and storage; `CONNECTED` alone is not proof of usable data. The 90-day view initially has only the bounded historical backfill, so missing earlier hours remain visible rather than invented.

PROPOSED rollback if collection fails: stop `market-worker` through the normal Compose project, set the ignored `.env` flag back to `0`, and preserve all captured evidence and the account database. Do not restore the pre-activation dump over newer owner data or market observations. API/web/account remain available with an unavailable or disabled market feed. No rollback was needed in this run.

## Limits and completion

This is point-in-time activation evidence, not a guarantee of continuous provider availability or a trading readiness claim. The preflight checked current public access; no full new 60-minute run, hourly close, manual Narrator pass or backup restore was rerun because no schema or application code changed. The normal worker remains running. Git publication records the operating-state documentation only; the ignored local `.env`, database, secret and evidence stay local.
