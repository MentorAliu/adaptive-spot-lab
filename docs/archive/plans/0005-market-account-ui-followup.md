# ExecPlan 0005 — market and account display follow-up

## Goal and observed state

Address the four owner browser comments on the running M2 app. The normal market collector is disabled and has no stored candles, so the chart correctly has no series to draw. The market route validated `symbol` in search params but kept the 30/90-day filter in component state. The Markets nav link included a BTC search value in its active match, and account balances displayed fixed-scale ledger strings directly.

## Scope and authority

This is a UI correction within accepted M2 and M1 behavior. Keep collection disabled and preserve the owner account, ledger, approvals, secrets, API, schema and operating controls. No synthetic or external prices may fill the empty chart. Financial strings remain authoritative; formatting is display-only. No new dependencies, migrations or shadcn primitives are needed. The normal web-only update follows the standing local delivery rule with a protected backup and service verification.

## Changes and acceptance

| Requirement | Implementation | Verification |
|---|---|---|
| Explain missing chart | Name disabled collection when the feed is `DISABLED`; keep the chart absent with zero observed candles. | Fresh isolated empty-feed Chromium check. |
| URL owns every market filter | Validate `symbol` and `days`, include both in loader dependencies, update one while retaining the other. Future market filters follow the same rule. | Browser selection, SOL switch and reload; invalid values default safely. |
| Stable Markets nav | Match the path without search values. | Browser assertion after SOL selection. |
| Readable values and dates | Group exact decimal strings, suppress redundant zero precision, and render explicit readable UTC timestamps. Keep all nonzero precision and canonical request strings. | Formatting unit tests and isolated owner funding browser journey. |

## Integration evidence and gates

The installed official shadcn skill and CLI discovery confirm TanStack Start, Base UI/base-nova, preset `b2fms61Bqi`, and existing Toggle Group, Card, Empty, Alert and Table components. `shadcn search` reports no configured searchable registry; `shadcn docs toggle-group` resolves the official Base UI docs. The installed Lightweight Charts skill and `lightweight-charts` 5.2.1 were checked; the chart adapter itself is unchanged. [TanStack Router search guidance](https://tanstack.com/router/latest/docs/guide/search-params) supports validated URL state and functional search updates; [navigation guidance](https://tanstack.com/router/latest/docs/guide/navigation) documents `activeOptions.includeSearch: false`. No dependency or license change.

Q01/Q02: use existing primitives and browser check for empty state, selection, reload, active nav and funding. Q03/Q04: no backend or financial mutation; keep exact strings and normal secrets/data. Q05/Q06/Q07: no collector/chart engine change; relevant format unit tests and production build apply. Q08: disabled feed remains visible. Q09: protected backup, web-only recreation and normal health/browser verification. Q10: record actual checks, deployment identity and remaining limits. An isolated fixture result is not public collection evidence.

## Run record

- VERIFIED: pinned Docker frontend lint and typecheck exited 0; 17 unit tests passed. Initial targeted Prettier check found five changed files; they were formatted in the pinned authoring image.
- VERIFIED: isolated `ui-0928a` empty-market Chromium case passed, including disabled chart explanation, URL filter persistence, nav active styling and reload. Isolated `ui-0928b` owner funding Chromium case passed with formatted account values. These used fresh test secrets/databases; no normal owner mutation was made.
- VERIFIED: the isolated production web image built. Its nonfatal third-party `use client` directive warnings match prior builds.
- VERIFIED: final pinned Docker lint, typecheck, all 17 unit tests and targeted Prettier check exited 0 after formatting. The isolated production web build passed; all 64 compiled files in both tested images and the normal candidate have the same SHA-256 aggregate `3e8f2a2f8578428e1a3db2eea7fcd7cbf9001521ee74d1f3ff0df8cfd1cc704f`.
- VERIFIED: after URL history changed, the fresh `ui-0928c` fixture project passed three foundation/funding browser cases, three market live/unavailable/recovered cases, and four desktop/mobile cancellable/uncancellable symbol/history race cases. Back/Forward assertions now cover 30/90-day URL entries. A repeated empty-market case in `ui-0928a` passed after adding Back/Forward assertions. These tests did not activate the normal collector.
- VERIFIED: before the normal update, schema was `0004_m2_completion`, web/API/PostgreSQL were healthy and the web image was `sha256:6ea3f051483313374dcfe6fe1fea3f4a178886b1dfc3200508ecbb12c78ff581`. A protected custom database backup is retained at `.cache/deployments/ui-comments-20260928a/ui-comments-20260928a.dump` (83,269 bytes; SHA-256 `32b7beaefd34603a8bc16dad514b27b5657d3bba2938459366e0437bdefdb3be`). This web-only update did not require a schema restore rehearsal.
- VERIFIED: only normal `web` was rebuilt/recreated; its running image is `sha256:295e36ee7f4db21bda8506ee17f2a048bf64d803fa389853219258a25e563978`. API and PostgreSQL container IDs remained unchanged. All three services were healthy, API readiness returned HTTP 200, schema remained `0004_m2_completion`, and the normal market-worker count remained zero. The real local browser at `http://127.0.0.1:4317/` displayed `10,000.00 virtual USDT`, `100.00` units/NAV and a readable UTC funding date. The normal `/markets?symbol=BTCUSDT&days=30` page showed the disabled worker, no candle chart, and the specific collection-disabled explanation. The two isolated browser stacks were stopped without deleting their volumes or evidence.
- Direct selection of filter controls in the normal in-app browser did not trigger navigation through that browser automation surface; the matching built payload passed the isolated real Chromium interaction tests. Manual Narrator checks were not rerun for this follow-up. Git publication is recorded separately in the protected delivery receipt after the final commit.

## Failure and recovery

Keep the current normal web image identity until the new image is verified. Preserve the normal database and secrets. If web health fails, restore the prior schema-compatible web image without changing the database or activating collection. Retain the backup and test evidence. Do not claim the normal UI changed until its running image and browser are checked.

## Owner clarification — page milestone labels (2026-09-28)

- OBSERVED: the account header still hard-coded `PAPER ACCOUNT · M1` because owner funding was introduced in M1. The Markets header similarly hard-coded `PAPER RESEARCH · M2`. These labels describe feature origin, not the current application milestone, and can imply that the account page is outdated. The normal app is still the accepted M2 release with collector disabled.
- IMPLEMENTED: the existing shadcn Badge components now show `PAPER ACCOUNT` and `PAPER RESEARCH`; milestone history stays in STATUS and the plans. No component, dependency, API, schema, financial operation or operating setting changed.
- VERIFIED: the official installed shadcn skill was read. CLI `info --json` confirmed TanStack Start, Base UI/base-nova, preset `b2fms61Bqi` and the installed Badge; registry search reported no configured searchable registry, and `shadcn docs badge` resolved the official Base UI page. Pinned Docker `lint`, `typecheck`, targeted Prettier and all 17 unit tests passed. The normal web-only Docker build and recreation completed healthy.
- VERIFIED: before the update, a protected database backup was saved to `.cache/deployments/account-badge-20260928a/account-badge-20260928a.dump` (83,533 bytes; SHA-256 `dba4a2314d680e16016b423da334f37ec22a0acc8e9cf3d6df98a327e2e5e4cb`). The prior web image was `sha256:295e36ee7f4db21bda8506ee17f2a048bf64d803fa389853219258a25e563978`; the new running image is `sha256:5b267d439a96c33940643a8a81f9566fef0921d174aa5536fe46769263f701c3`. API and PostgreSQL container IDs stayed the same and all three services are healthy. API readiness returned HTTP 200, schema remained `0004_m2_completion`, and no market-worker container is running.
- VERIFIED: the normal in-app browser displayed both updated badges; the authenticated Account view still showed `10,000.00 virtual USDT` and readable UTC history. A separate Docker Chromium visit to the normal Account sign-in view returned HTTP 200 and saved `account-badge.png` in the protected task evidence folder. Its first attempt through `host.docker.internal` returned HTTP 421 `Untrusted host`; the allowed internal `web:3000` route succeeded. No account sign-in or funding was performed by that browser check.
- UNRUN: manual Narrator checks were not repeated for this text-only badge change. The prior M2 milestone acceptance evidence is not relabeled or expanded by this correction.
