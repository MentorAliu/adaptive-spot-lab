# ExecPlan 0008 — Market candle table display

## Goal and observed starting point

Make the Markets candle table easier to scan: omit the repeated `UTC` suffix where the column header already identifies the zone, and group decimal digits while hiding redundant trailing zeroes. The live table previously showed `Sep 28, 2026, 05:00 UTC` and `83490.20000000`. The shared display formatter already performs lossless string-based decimal grouping; the table had not used it.

## Scope, decision and trust boundary

- Files: `apps/web/src/markets/candle-table.tsx` supplies per-column rendering; `apps/web/src/lib/display.ts` adds an optional zone suffix setting; `apps/web/src/lib/display.test.ts` verifies representative precision and UTC output. The documentation map, frontend contract, integration evidence, status and command record capture the rollout.
- Sequence: inspect existing Table/formatters and official sources; edit display cells; run containerized checks and build; back up owner data; recreate only web; verify the normal browser and service identities.
- IMPLEMENTED: `UTC hour` and `Available UTC` cells use the shared UTC formatter without its suffix. Other date displays keep the explicit suffix. Open, high, low, close and volume cells use the shared decimal-string formatter. `83490.20000000` displays as `83,490.20`; nonzero fractional digits remain visible.
- The table's source decimal strings, API records, chart inputs, financial authority, polling, URL state, collector and database are unchanged. No component, dependency, preset or schema migration was added.
- The installed shadcn Table and existing TanStack Table column definitions were reused. Official [shadcn Base UI Table guidance](https://ui.shadcn.com/docs/components/base/table) and [TanStack column definitions](https://tanstack.com/table/latest/docs/guide/column-defs) were checked against installed shadcn 4.21.0 and TanStack Table 9.2.4.

## Verification and deployment

- VERIFIED: the official shadcn skill was read. Docker `shadcn info --json` confirmed TanStack Start, Base UI, preset `b2fms61Bqi`, and installed Table; registry search found `@shadcn/table` and CLI `docs table` resolved the official guide. No UI primitive was installed or changed.
- VERIFIED: Docker web typecheck and lint passed; 17 unit tests passed, including the decimal and UTC cases. Initial Prettier check found one assertion layout issue; it was corrected and the final check passed. The Docker production web build passed. `git diff --check` passed with only Windows line-ending notices.
- VERIFIED: before web deployment, a protected PostgreSQL custom dump was saved at `.cache/deployments/candle-table-20260928a/candle-table-20260928a.dump` (4,581,372 bytes; SHA-256 `e0579f6db39d48a88e43e1375717313d7585fe5412a52e70f65b11880676369f`). The folder has protected ACLs. Only the normal web service was rebuilt and recreated. It is healthy at `http://127.0.0.1:4317/` on image `sha256:7df510e657d195ccb14254c33ac0e9729f2214c4648d09b9fc0efa86682e5602`. API, PostgreSQL and market worker container IDs remained unchanged. Schema remained `0004_m2_completion`, and the root URL returned HTTP 200.
- VERIFIED: after reloading the signed-in normal Markets browser, the accessibility tree and screenshot showed the live candlestick chart and table with headers `UTC hour`/`Available UTC`, date cells without `UTC`, and grouped/trimmed OHLCV values. The BTC feed was connected and quote valid. The provisional close and volume changed during observation, as expected for a live bar.
- A read-only schema query initially targeted nonexistent `schema_migrations`; the corrected `alembic_version` query returned `0004_m2_completion`. The market worker has no Docker healthcheck, so `docker compose ps` reported it running rather than healthy. Neither observation indicates a deployment failure.

Affected gates: Q01 precision preserved by string formatting and unit checks; Q02 automated accessibility tree and visual browser inspection passed, manual Narrator not rerun; Q05 containerized build/checks passed; Q10 protected backup and running web/browser verification passed. Full M2 acceptance workloads and isolated provider tests were not rerun for this display-only change. Rollback is the prior verified web image without restoring an older database over ongoing public observations.
