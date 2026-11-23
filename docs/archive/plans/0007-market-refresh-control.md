# ExecPlan 0007 — Markets refresh control

## Goal and scope

Add an owner-selected polling rate to the Markets page. Keep the choice in validated URL search params alongside symbol and history, and preserve it across navigation, refresh and sharing. This controls only browser reads of stored observations; it does not change the Binance WebSocket worker, storage, quote quality rules or paper-trading authority.

## Starting facts and decision

- OBSERVED: the accepted normal app runs M2 source `8104f26984894c9f928eae8c383be36131b78b2a` with the optional public worker active. TanStack Query 5.104.0 currently polls health and quote every 2 seconds and candles every 5 seconds; instruments have no interval. Router validates `symbol` and `days` in `/markets` search state.
- OBSERVED: the official shadcn skill was loaded; Docker CLI `shadcn info --json` resolved TanStack Start, Base UI, preset `b2fms61Bqi`, and an installed Toggle Group. The official `@shadcn/toggle-group` registry item and Base UI docs were found. The installed Lightweight Charts skill was read; no chart API change is proposed.
- DECISION: choices are Live (existing 2-second quote/health and 5-second candles), 10 seconds, 30 seconds, 1 minute, and Off (no periodic timer). The URL value is `refresh=live|10|30|60|off`, with timed rates validated as numbers and invalid/missing values falling back to Live. Timed choices beyond Live apply to all three polled resources. Off still permits initial load and ordinary Query focus/reconnect fetches; the UI must say so. The data keys do not include refresh because rate does not change result identity.

## Requirements and implementation

| Requirement | Implementation and check |
|---|---|
| URL state | Validate `refresh` on the Markets route and retain other params on every control change. Browser test direct invalid URL, selection, reload, back/forward and symbol/history preservation. |
| Bounded page polling | Move interval scheduling to the page's Query observers while retaining shared initialized `queryOptions` for SSR/client data identity. Browser observation checks that Off stops timed requests and timed selections resume. |
| Honest and accessible UI | Reuse the installed shadcn Toggle Group with a label and text explaining Live and Off. Check desktop/mobile, keyboard and browser errors. |
| Preserve market behavior | No worker, API, DB, chart-adapter, account or schema changes. Verify chart/empty/error rendering remains truthful and collector stays active. |

Official integration references: [TanStack Query polling](https://tanstack.com/query/latest/docs/framework/react/guides/polling), [TanStack Router search params](https://tanstack.com/router/latest/docs/guide/search-params), [shadcn Base UI Toggle Group](https://ui.shadcn.com/docs/components/base/toggle-group). The Query guide states interval timers are observer-scoped, independent of stale time, and `false` stops polling; default background behavior pauses when the tab loses focus.

## Sequence and verification

1. Add the validated search value and page control. Keep server query options initialized and reuse their keys/functions, with observer-specific intervals.
2. Add focused browser coverage for URL persistence and actual timer behavior. Run containerized lint, typecheck, unit tests, build and the applicable isolated browser test. Record commands and results, including failures.
3. Back up the normal database before rebuilding the web service, preserve the running worker and owner data, deploy only the verified web image, and verify normal health/browser and image identity.
4. Review source and documentation changes, commit, and publish with the required branch/remote checks.

## Gates, risk and recovery

Affected M2 gates: Q01 data identity/freshness, Q02 accessibility, Q03 browser race/navigation, Q05 runtime integration and Q10 observed normal deployment. Finance/worker/provider/storage performance gates are unchanged. Excessive requests, a URL mismatch, stale-display wording or an unintended worker recreation are the main risks. If the web rollout fails, restore the prior verified web image without restoring an old database over newer observations. Record any unrun check explicitly.

## Progress and completion evidence

- IMPLEMENTED: the Markets route validates `refresh=live|10|30|60|off`, treating timed values as numbers; invalid and missing values default to Live. The existing Symbol and History selections retain the refresh value and vice versa. The installed Toggle Group is reused with accessible label/description. Health, quote and candle Query observers receive the selected interval; the shared initialized query options retain their keys/functions without timers. The chart adapter, API, worker, schema and account behavior were unchanged.
- VERIFIED: Docker shadcn 4.21.0 `info --json` resolved preset `b2fms61Bqi`, Base UI and the installed Toggle Group. Registry search and component docs succeeded. The first offline info lookup failed DNS; retry on an isolated egress network succeeded. Official Query polling and Router search guidance supported the implementation.
- VERIFIED: final containerized typecheck, lint and Prettier checks exited 0; 17 unit tests passed. The first pass found a missing default-link search value, type import style and formatting errors; all were fixed. The first isolated browser run found numeric-looking string rates serialized with quotes; timed URL values were changed to validated numbers.
- VERIFIED: a fresh `asl-refresh-0928a` isolated database/browser project passed the targeted Chromium case. It checked selection and persistence across reload and Back/Forward, symbol/history retention, invalid URL fallback, actual absence of periodic server-function requests with Off, resumed requests at Live, 390-pixel layout and keyboard selection. The isolated production web image built successfully. No full new M2 worker/performance suite or manual Narrator run was performed.
- VERIFIED: before normal web deployment, schema was `0004_m2_completion`; normal web/API/PostgreSQL were healthy and the public worker was running. A protected 3,420,546-byte PostgreSQL custom dump is retained at `.cache/deployments/market-refresh-20260928a/market-refresh-20260928a.dump`, SHA-256 `1ecfeea6243770fdf9a47e358f10937318d51f1707f527ac5fd8b732a3f27921`. Only web was rebuilt/recreated; final image `sha256:57b778442eccb0c698d1b2187618f6c95609532488653744ff5cc2f9fb87b936`, zero restarts. Its aggregate compiled-payload hash `35eace0b86b9c87d6681d3399f667b5aee951fd1fff0b00ce954797a24e28687` exactly matched the isolated tested image. API, PostgreSQL and market-worker container identities were unchanged. Web/API/PostgreSQL stayed healthy; API read showed both BTC/SOL feeds connected with usable quotes, worker known, no queue warning/overload. After owner sign-in, normal browser direct Live and 30-second URLs showed selected state and a public candlestick chart. The in-app browser's direct control clicks did not navigate on this automation surface; isolated Chromium verified those interactions.

Q01 data identity/freshness: PASS for scoped page changes; polling rate is not part of result keys and Off is described as a last-read view. Q02 accessibility: PASS for automated keyboard/label/mobile assertions; manual Narrator UNRUN. Q03 navigation/races: PASS for validated URL persistence and existing market behavior in the targeted browser case; full prior race matrix UNRUN. Q05 integration: PASS for pinned Docker checks and matching production payload. Q10 local deployment: PASS for protected backup, running image, health, public feed and signed-in browser verification. Broader trading readiness is outside this change.
