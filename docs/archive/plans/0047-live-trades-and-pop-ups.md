# ExecPlan 0047 — Live trades and pop-ups

**Status: APPROVED by the owner's ask on 2026-10-30 at 17:11:25 UTC ([DECISIONS](../../DECISIONS.md#2026-10-30--live-trades-and-pop-ups-execplan-0047)); the design choices are the thread's, under the owner's standing "decide for me" (§13). Built and checked in the cloud, merged on the owner's yes (PR #147) and installed on the owner's PC on 2026-10-30 at 19:09 UTC, where a read-only check found the live stream answering (§14).** Written by the project thread "Show every trade live with pop-ups" from `main` at `89954ed`. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)): the app shows each trade the moment the engine saves it, on every open page and, if the owner turns them on, as desktop pop-ups. Nothing changes of the trader, the policy, the limits, the money paths, the protection or the database's tables.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal

The owner asked on 2026-10-30 at 17:11:25 UTC: "I need all trades to be realtime, if a position is opened, I want it to show on the app, and notification popup, implement it using most modern best practices for performance and library integration, use tanstack@react-query based on official documentation to implement this".

Observable outcome:
1. Within about a second of the engine committing a fill or a funding payment, every open page of the app shows it: a toast in each visible tab ("Long opened …", "Long closed by …: +1.23 USDT"), and the pages on screen (Home, Trades, a trade, the chart's marks) read it again. The same holds for the trader's answered decisions, the run's state and the twins' trades, which refresh their pages without a toast.
2. The browser holds one live connection for all of the app's tabs; when the tab that holds it closes, another takes it over.
3. Desktop pop-ups, off until the owner turns them on in the header's bell menu: one per fill (an opened, closed or liquidated position) while no tab of the app has focus; a click opens the trade.
4. The header shows whether the app is live. When the connection is down, the pages poll as they do today, so nothing is missed; when it is up, the lists poll every 60 s instead of every 2 to 5 s.

## 2. What the app has

`OBSERVED` in the code at `89954ed`:
- **The toasts** (`apps/web/src/futures/trade-toasts.tsx` at `89954ed`, which this plan replaces; ExecPlan 0039 §5.7): every open, visible tab reads `GET /v1/futures/activity?after=<cursor>` through a server function every 2 s; after a sleep it shows three toasts, then a summary; the cursor is kept per browser in `localStorage` (`asl.futures.toast-cursor`). A fill reaches the page 0 to 2 s after its commit, plus a read.
- **The reads** ([`futures.query.ts`](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/apps/web/src/futures/futures.query.ts)): the overview and the chart's marks every 2 s, the trades, a trade, the decisions and the twins every 5 s, the coach and the league every 15 s, the scorecard and checks every 60 s; Query pauses intervals in background tabs. Nothing tells a page that something changed: each list is read about 12 times a minute to catch a trade that comes a few times a day.
- **The engine**: the futures worker steps every second ([`worker.py`](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/futures/worker.py)); each step is one fenced transaction whose effects (`FILL`, `FUNDING`, `DECISION_ANSWERED`, `STOP_TIGHTENED`, `RUN_*`, `INCIDENT`, `VALUATION`, …) are known after its commit; the twins step after it in a transaction of their own. The API is one uvicorn process; the web server reaches it with the service key ([ExecPlan 0042](0042-no-owner-sign-in.md)).
- **The web**: TanStack Start 1.168.58 on Nitro (srvx's Node adapter), served over HTTP/1.1 on `127.0.0.1:3000`; no server route yet, only pages and server functions.
- **Shutdown**: `OBSERVED` in a scratch experiment on 2026-10-30 (FastAPI 0.141.1, uvicorn 0.54.0, the API's `@app.middleware("http")` shape): an open event stream ends cleanly when its client leaves (the generator's `finally` runs at once), but on SIGTERM uvicorn waits for open connections with no limit by default; srvx closes them after 5 s.

## 3. Scope

In: an announcement from the futures worker after each committed step that changed something (§4.1); a listener in the API and the event stream `GET /v1/futures/live` (§4.2); the web's same-origin stream `GET /api/live` (§4.3); the browser's one connection, toasts, page refreshes and polling (§4.4–§4.6); desktop pop-ups (§4.7); the header's state and bell menu (§4.8); `--timeout-graceful-shutdown 3` on the API.

Out: a WebSocket (nothing is sent from the browser); prices on the stream (the overview keeps its 2 s read: the mark moves every second, and a price feed to the browser is a larger change); pushing the reviews, scores, coach or checks (they keep their intervals); a service worker or Push API (pop-ups need an open tab of the app); a migration, a new table or a change to any money path; a new dependency.

## 4. Design

### 4.1 The announcement

After `engine.step` commits, the worker sends `SELECT pg_notify('asl_futures_live', <payload>)` in a transaction of its own when the step's effects hold any kind other than `VALUATION`; the payload is `{"source":"owner","kinds":[…]}`. The same after a twin step with effects (`"source":"twins"`), and once after recovery (`"kinds":["RECOVERED"]`). PostgreSQL delivers a notification only when its transaction commits, and a full notification queue fails the transaction at commit (§7), so the announcement stays out of the step's money transaction: a failed announcement is logged (the first, then every 60th in a row) and costs at most the listener's sweep (§4.2). A notification carries no money value; the stream reads the records.

### 4.2 The listener and the engine's stream

The API's lifespan starts one listener: a psycopg `AsyncConnection` in autocommit that runs `LISTEN asl_futures_live` and waits on `notifies(timeout=30)`. Each notification wakes the streams with its source and kinds; every 30 s without one, a sweep wakes them too, so a lost announcement shows within 30 s. A lost connection is retried after 1, 2, 4 … at most 30 s, and the streams end until it is back (the browsers fall back to polling, §4.4).

`GET /v1/futures/live` (service key) is an event stream (FastAPI's `EventSourceResponse`; FastAPI sends a `: ping` comment every 15 s). It answers 503 `LIVE_UNAVAILABLE` when the listener is down and 503 `LIVE_BUSY` when 8 streams are open. Its events:
- `ready`, `id` = the ledger's newest sequence: the first event when the request names no cursor, or names one and nothing followed it; data `{"state","cursor"}`. Sent again when the ledger is older than the stream's cursor (a restored database).
- `activity`, `id` = the newest sequence: the fills and funding payments after the cursor, as `GET /v1/futures/activity` gives them (the newest 20 and the count), with `after`, the cursor they follow. A request with `Last-Event-ID` (the browser's own resume) starts with the activity it missed, or `ready` when there is none.
- `change`, no `id`: `{"source","kinds"}` for an owner's step without a fill or payment (a decision answered, a stop tightened, the run's state) and for the twins.

The first event carries `retry: 3000`. Each wake reads the activity after the stream's cursor in the thread pool (one indexed `max(seq)` when nothing is new). A stream ends when its client leaves or the listener stops. The API's container stops in at most 3 s with `--timeout-graceful-shutdown 3` instead of waiting for open streams until Docker kills it.

### 4.3 The web's stream

A TanStack Start server route, `GET /api/live`, behind the app's Host check (421 on a foreign host) and, on this route, Start's own CSRF middleware, which checks the Fetch Metadata header: only a same-origin request passes (403 otherwise). It forwards `Last-Event-ID` (digits only) to the engine with the service key, aborts the engine's request when the browser leaves, and passes the engine's event stream through unchanged with `Cache-Control: no-store`; an engine refusal or error is a 503. The frame policy applies to it as to every response.

### 4.4 One connection per browser

`EventSource` over HTTP/1.1 takes one of the browser's six connections to the site for as long as it is open, in every tab (§7). The tab that holds the Web Lock `asl.futures.live` opens the one `EventSource` and relays its events and its state to the other tabs over the `BroadcastChannel` `asl.futures.live`; the others wait for the lock, so when the holder closes, the next tab takes over and the toasts' cursor (§4.6) covers the gap. `EventSource` reconnects by itself and resumes with `Last-Event-ID`; a refused stream (503, or the web server away) fails it for good (§7), so the holder opens a new one after 5, 10, 20 … at most 60 s. A browser without Web Locks opens one connection per tab. Web Locks (like notifications) exist only in a secure context: `http://localhost:3000` and `http://127.0.0.1:3000`, the only hosts the web answers on the PC, are; the browser suites' `http://web:4318` is not (§14). The states are `connecting`, `live` and `offline`.

### 4.5 Query

Each event invalidates what it changed: an owner's `activity` or `change` the queries under `["futures"]`, a twins' `change` the twins', league's and twin trades' keys. Invalidation marks those queries stale and refetches only the ones on screen; others refetch when shown (TanStack Query's guide, and TkDodo's "Using WebSockets with React Query", §7). The events carry no page data, so nothing is written into the cache by hand: every number still comes from the engine's reads. While the state is `live`, the trades, a trade, the decisions, the twins, a twin's trades and the chart's marks poll every 60 s (a safety net) instead of 2 to 5 s, through `refetchInterval` as a function; the overview keeps 2 s for the mark price, the others their own. When the state changes, everything under `["futures"]` on screen is refetched once, which also sets the new intervals.

### 4.6 Toasts

Each visible tab shows the toasts (`toastFor`, as today) for the entries after the shared cursor `asl.futures.toast-cursor`, which then moves on; a hidden tab leaves it. When an `activity` event follows the tab's cursor, its items are shown directly; otherwise (a tab coming back, a new holder, a reload) the tab reads `GET /v1/futures/activity?after=<cursor>` once and shows three plus a summary, as today. A browser without a cursor starts at the stream's first cursor and shows nothing old. Each toast's Open goes to the trade.

### 4.7 Desktop pop-ups

Off by default; the bell menu in the header turns them on for this browser (`localStorage`), asking the browser's permission on that click, the only place it is asked. When an `activity` event brings fills (entries, exits, liquidations; not funding) and no tab of the app has focus, the tab holding the stream shows one notification per fill (the newest three, then one summary of the other fills and of the entries the read left out; a funding payment counts in neither), each tagged `asl-fill-<sequence>` so a fill shows once; a click focuses that tab and opens the trade. A tab that has focus when it shows the toasts tells the holder over the channel, and the holder waits 400 ms for that before it shows a pop-up. A denied permission shows in the menu as blocked, with the way to allow it in the browser's site settings.

### 4.8 The header

A badge beside PAPER with the role of a status: "Live" with a radio icon when the stream is open, "Connecting" with a spinner while it starts, and "Offline" (the secondary badge) when it is down. On a phone only the icon shows; its sentence stays for screen readers ("Offline: the pages refresh every few seconds until the live connection is back"). As built, no tooltip: a status a screen reader announces needs no hover. A bell button ("Trade alerts") opens a menu with "Desktop pop-ups" (a checkbox item that keeps the menu open) and a line on its state: on, off, blocked with the way to allow it in the browser's site settings, or not offered by this browser. shadcn's `Badge`, `Spinner`, `Button`, `DropdownMenu` and `DropdownMenuCheckboxItem` from the preset `b2fms61Bqi`; no new component.

## 5. Authority

None changes. The stream is a read of records the API already serves; the browser can neither write through it nor change what it reads (the cursor is digits only, and only the engine's activity read answers it). The announcement is not an order, a decision or a record: losing it delays a page by at most 30 s. Pop-ups are the owner's choice in the browser and need the browser's permission.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| L1 | The worker announces after commit, only for steps with a change, and a failed announcement neither stops nor slows the step | engine, without a database: the worker's announcement for each kind of effect, none for valuations, a failing one swallowed and counted |
| L2 | The listener wakes the streams on a notification, a sweep and a reconnection; it stops cleanly | engine, scratch PostgreSQL: a real `LISTEN`, `pg_notify` from another connection, the sweep, the connection killed and restored |
| L3 | The stream: service key, 503 when down or full, `ready`/`activity`/`change`, `Last-Event-ID` resume, ids are the ledger's sequence | engine, without a database: the events from a scripted listener and reader, and the route served by a real uvicorn and read on the wire; scratch PostgreSQL: a fill the engine commits reaches an open stream with its feed entry |
| L4 | `/api/live`: same-origin only, Host checked, the engine's refusal a 503, frame policy, no caching | browser suite |
| L5 | One connection for all tabs; another tab takes over when the holder closes | browser suite: three tabs, one `/api/live` request; close the holder, a new one starts |
| L6 | A position opened and closed shows as a toast and on Home within seconds, with its Open link | browser suite: the fixture's new `open` and its `close`, each announced |
| L7 | Desktop pop-ups only when turned on, permission asked on the click, none while a tab has focus, one per fill, a click opens the trade | unit (the planner) and browser suite (a recording `Notification`) |
| L8 | Polling: 60 s while live, today's intervals otherwise; a state change refetches | unit |
| L9 | The API stops within its grace when a stream is open | engine, without a database: the image's command carries the flag; scratch: SIGTERM with an open stream |

## 7. Official sources

`OBSERVED` on 2026-10-30, at the installed versions, from the projects' own repositories where their sites refuse this machine:
- TanStack Query 5.104.0 docs ([`TanStack/query@d4033eb`](https://github.com/TanStack/query/tree/d4033eb1e5bdef3c8aa72a6cc614bcdd98b1ddca/docs/framework/react/guides)): "Query Invalidation" — an invalidated query "is marked as stale" and "If the query is currently being rendered via `useQuery` or related hooks, it will also be refetched in the background"; "Polling" — `refetchInterval` as a function "receives the `Query` object", and "By default, polling pauses when the browser tab loses focus". The installed `QueryObserver` recomputes the interval on every query update and option change.
- TkDodo, "Using WebSockets with React Query" ([`TkDodo/blog@9c64b98`](https://github.com/TkDodo/blog/blob/9c64b980586a4c2e8fd7b9ac87d39332d3d8c5ea/content/posts/using-web-sockets-with-react-query/index.mdx)), of the series the Query docs' "Community Resources" list ("TkDodo, a maintainer of TanStack Query, writes a series of blog posts about the library"): "Query Invalidation plays really nice together with WebSockets. This approach avoids the problem of over pushing". `experimental_streamedQuery` was read and not used: it fits one finite stream per query, not one endless stream that touches many queries.
- TanStack Start 1.168.58 ([`TanStack/router@ddad69a`](https://github.com/TanStack/router/blob/ddad69a4a4b18c19e3fcc510ac1e21f9dab883a7/docs/start/framework/react/guide/server-routes.md)), "Server Routes": a `server.handlers` map on `createFileRoute`, with `middleware` for the route; the installed `createCsrfMiddleware` passes a request whose `Sec-Fetch-Site` is `same-origin` by default.
- FastAPI 0.141.1, the installed `fastapi.sse`: `EventSourceResponse` with an async generator of `ServerSentEvent` (`event`, `id`, `retry`, `data` JSON-encoded), a `: ping` comment after 15 s idle.
- psycopg 3.3.6, the installed `AsyncConnection.notifies(*, timeout=None, stop_after=None)`.
- PostgreSQL 17, `NOTIFY` ([`postgres/postgres@2acade9`, `REL_17_STABLE`](https://github.com/postgres/postgres/blob/2acade963cb1c6c81c6f09a018ceca43958e1be9/doc/src/sgml/ref/notify.sgml)): "if a NOTIFY is executed inside a transaction, the notify events are not delivered until and unless the transaction is committed"; "If this queue becomes full, transactions calling NOTIFY will fail at commit."
- HTML, server-sent events ([`whatwg/html@404b3eb`](https://github.com/whatwg/html/blob/404b3eb14a7a936dddefb2d78e224dbeb01d2358/source)): "if res's status is not 200, or if res's `Content-Type` is not `text/event-stream`, then fail the connection" (closed, no reconnection); otherwise a lost connection is re-established with `Last-Event-ID`.
- MDN ([`mdn/content@0a744ed`](https://github.com/mdn/content/tree/0a744eda257f0612d704454fea045065aaed1349/files/en-us/web/api)): `EventSource` — "When not used over HTTP/2, SSE suffers from a limitation to the maximum number of open connections … (6)"; Web Locks — "The first queued request will be granted only when the lock is released", a held lock lasts while the callback's promise is pending; Notifications — "You should only request consent to display notifications in response to a user gesture", and a notification with the same `tag` replaces the earlier one.
- uvicorn 0.54.0, the installed `--timeout-graceful-shutdown INTEGER`: "Maximum number of seconds to wait for graceful shutdown."

## 8. Data and trust boundaries

The browser reaches only `/api/live` on its own origin; the web server alone holds the service key and talks to the API on the private network; the API alone talks to PostgreSQL. The notification channel carries kinds, never values. The stream's payloads are the activity read's own (validated in the browser with the same Zod schema as today) and two small objects. No new secret, host, port or permission; the listener uses the API's database identity.

## 9. Implementation sequence

1. Engine: `app/futures/live.py` (announcement, listener, events), the worker's announcements, `GET /v1/futures/live`, the lifespan's listener, the image's flag, the fixture's `flat` and `open` commands and its announcements; OpenAPI and the web's generated types. Tests: `tests/test_m11_live_unit.py`, `tests/test_m11_live_db.py`.
2. Web: `src/routes/api.live.ts` and its server helper `src/futures/live.server.ts` (with `privateStream` in `src/account/account.server.ts`); `src/futures/live.ts` (connection, lock, channel), `live-state.ts` (the state the header and the intervals read), `live-alerts.ts` (toasts and pop-ups planner, the cursor, the pop-ups' setting), `live-trades.tsx` (replacing `trade-toasts.tsx`), `src/components/live-status.tsx` (the header's badge and bell menu), the intervals in `futures.query.ts`. Tests: `src/futures/live.test.tsx`, `src/futures/live.server.test.ts`, `e2e/live.spec.ts`.
3. Tests (§6), then the contracts: [API_CONTRACTS](../../API_CONTRACTS.md), [FRONTEND](../../FRONTEND.md), [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md), [SECURITY](../../SECURITY.md), [STATUS](../../STATUS.md), [COMMANDS](../../COMMANDS.md).

## 10. Verification commands

Cloud, as in [COMMANDS](../../COMMANDS.md): from `apps/web`, `pnpm typecheck`, `pnpm lint`, `pnpm check`, `pnpm api:check`, `pnpm test`, `pnpm build`; from `services/engine`, `ruff check`, `python -m app.export_openapi --check`, the suite without a database, then on a scratch PostgreSQL the new tests and the futures suites, and the browser suites of `tests.m11_browser_fixture` (`pages.spec.ts`, `local-time.spec.ts` and `twins.spec.ts` on `seed`; the new `live.spec.ts` on `flat`, at `PLAYWRIGHT_BASE_URL=http://localhost:4318`, a secure context). On the PC: the update's own checks, then a read-only look that the API serves the stream and the page shows "Live".

## 11. Failure and rollback

- The listener down, the stream refused or the web server away: the header says Offline and every page polls as today; nothing is lost, the toasts catch up from the cursor.
- A lost announcement: shown at the next sweep, within 30 s.
- A browser that blocks Web Locks or `BroadcastChannel`: one connection per tab, as many tabs as the browser allows.
- Rollback: the previous image. No migration, so no data to restore; `asl.futures.toast-cursor` keeps its meaning.

## 12. Q01–Q10

Q01: the header's three states and the bell menu, checked in the browser at both widths. Q02: the badge and menu are shadcn's, labelled; the toasts are the existing region. Q03: no money path; L1–L3. Q04: same-origin and Host checks, the service key on the server only, the cursor digits only, at most 8 streams (L3, L4). Q05: §11, L5, L8. Q06: a fill reaches the page in about a second instead of 0 to 2 s plus a read; the lists' reads drop from about 12 to 1 a minute while live (§14). Q07: §10. Q08: the listener logs its loss and return; the header shows the state. Q09: no migration; the previous image is the rollback. Q10: the contracts of §9; no new dependency.

## 13. Decision log

The owner delegates engineering choices ("decide for me", 2026-10-19); the thread took the recommended option each time:
- **Server-sent events, not WebSockets**: the browser only listens; `EventSource` reconnects and resumes by itself; FastAPI 0.141.1 has native support. WebSockets add an upgrade path through Start and Nitro for no gain.
- **PostgreSQL `LISTEN`/`NOTIFY`, after commit**: the worker and the API are separate processes; a notification needs no table or migration, and outside the step's transaction it can never fail a trade. A 30 s sweep covers a lost one.
- **Invalidate, don't write into the cache**: the pages' numbers stay the engine's reads; only the queries on screen refetch.
- **One connection per browser** (Web Locks + `BroadcastChannel`) because of HTTP/1.1's six connections.
- **Desktop pop-ups off until turned on**, for fills only, never while the app has focus; no service worker.
- **Keep the 2 s overview read** for the mark price; slow only what the stream announces.

## 14. Progress

- 2026-10-30: the plan written; design checked against the sources of §7 and a scratch experiment (§2).
- 2026-10-30, `IMPLEMENTED` as §9 lists, on the branch `claude/project-thread-76bl5m` from `main` at `89954ed`, and `VERIFIED` in the cloud session (no Docker), commands as in [COMMANDS](../../COMMANDS.md):
  - **Web**, from `apps/web`: `pnpm typecheck` clean; `pnpm lint` clean (with the build's `.output` removed first, as COMMANDS says); `pnpm check` "All matched files use Prettier code style!"; `pnpm test` `41 passed` files, `347 passed` tests (`live.test.tsx` 14, `live.server.test.ts` 8); `pnpm api:generate`, then `pnpm api:check` "Generated TypeScript API types match"; `pnpm build` exit 0, and the browser bundle holds none of `privateStream`, `X-Internal-Key`, `liveStream` or `api_internal_key`. The two new unit files were also run against deliberate faults, one at a time (the pop-ups' focus and "seen" checks, the holder's answer to a new tab, the retry delays, the open-position interval, the refetch on leaving live, the restored-database cursor, a hidden tab's cursor; the route's start bound, its event-id check, its type check and the tab's abort): each failed a test.
  - **Engine**, from `services/engine`: `ruff check` "All checks passed!"; `python -m app.export_openapi --check` "FastAPI OpenAPI schema matches"; `tests/test_m11_live_unit.py` `25 passed`, five runs in a row; the suite without a database (`ASL_TEST_ISOLATED=1`): `2 failed, 1105 passed, 466 skipped, 1 warning, 425 errors`, the 2 failures COMMANDS' known database cases and every error a database case (the 3 more skips are `test_m11_live_db.py`'s).
  - **Scratch PostgreSQL** 16.15, migrated to `0028_leaner_trader`. OBSERVED first: the session's locale is `C`, so `initdb` as COMMANDS gave it made a `SQL_ASCII` cluster, on which SQLAlchemy could not read the server's version and every test errored; the cluster was made again with `-E UTF8 --locale=C.UTF-8` (COMMANDS now says so). `tests/test_m11_live_db.py` `3 passed`, five runs in a row: an announcement arrives after its commit and a rolled-back `pg_notify` never does; a fill the engine commits reaches an open stream as its `activity` with the feed's entry (`FILL` among the step's kinds, no `VALUATION`, the worker's `Announcer` reporting nothing); a listener whose connection `pg_terminate_backend` ends closes its streams, listens again and hears the next announcement. `tests/test_m11_*.py` with `tests/test_api.py`: `2 failed, 361 passed`; the failures are `test_api.py::test_status_requires_service_identity_and_ready_database` (COMMANDS' known failure on `main`) and `test_m11_committed_trader.py::test_a_refused_view_is_retried_with_its_rule_and_then_recorded`, a statement timeout on `agent_read.market_feeds` during that run, which passed alone and with its file (`10 passed`).
  - **The stream by hand** on a seeded database: the API's `GET /v1/futures/live` and the web's `GET /api/live` (same-origin) answered `ready` with the ledger's cursor (13); with `Last-Event-ID: 5`, the `activity` after it; `/api/live` with no Fetch Metadata and cross-site 403, with a foreign Host 421; the web's answer `no-store`, `X-Accel-Buffering: no` and the frame policy.
  - **L9**: SIGTERM to the scratch API with a stream open: uvicorn logged "Cancel 1 running task(s), timeout graceful shutdown exceeded", the stream ended 3.15 s after the signal and the process exited after 4.32 s, inside Docker's 10 s.
  - **Browser suites** (the preinstalled Chromium, build 1243; the production build; the API with `ASL_AGENTS_OFFLINE_TEST=1`; the SYNTHETIC feed). On a database seeded by `seed`: `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts`, `15 passed`, the toast when a trade closes now served by the stream. On a database seeded by `flat`: `live.spec.ts` at `http://localhost:4318`, `4 passed`, three times on three fresh databases; the new position's toast was on screen 16 to 29 ms after the fixture's command returned (its step commits and announces before it returns). OBSERVED on the first try at `http://web:4318`, where the page is not a secure context: three tabs opened three streams, §4.4's fallback; the suite now checks the secure context first.
  - **Q06**, `VERIFIED` by the unit tests: while live, the trades, a trade and the decisions read every 60 s instead of 5, the chart's marks instead of 2; a trades page or a trade with an open position keeps 5 s, the overview 2 s. A fill reached the page within 30 ms of its commit in the browser suite, against 0 to 2 s plus a read before.
  - `NOT RUN`: the Docker builds of the api and web images (no Docker in the cloud) and the update on the PC; the engine's full suite on the scratch cluster (only the futures and API files); the `reviews`, `scores` and `checks` browser suites (their pages read nothing new); Firefox and Safari; a real desktop notification (the suite records the page's `Notification` calls: a headless browser shows none); a count of reads a minute on the PC.
  - No independent review: no money path changed (§5); the announcement runs after the step's commit, in its own transaction.
- 2026-10-30, **installed** on the owner's PC. PR #147 was merged at 18:44:47 UTC (`main` at `8908e14`) on the owner's yes in the thread (the decision card, 18:44:30 UTC). The owner's double-click: the update record `update-20261030T190504Z` `COMPLETE`, 18:45:35 to 19:09:47 UTC, from `bff1a33` to `8908e14`. Its backup is stamped 19:05:04 UTC, after the wait the update file makes before the hourly bar close (inferred from its code and the times; the transcript was not read). No migration (`0028_leaner_trader` before and after). The api, the web, the market, execution and evaluation workers, the agents' egress, runner and worker and the source fetcher recreated on their new images, no settings changed. Its verify step: reconciliation `OK`, `/`, `/trades`, `/decisions`, `/markets` and `/settings` 200, the agents' switch on (`ENABLED`, `CHECK_PASSED`), no problem. So the Docker builds of the api and web images, `NOT RUN` in the cloud, ran in the update.
  - `OBSERVED` read-only on the PC at 19:16 UTC through the owner's device (no Docker command, `curl` only): the folder on `main` at `8908e14` with no change. `GET http://localhost:3000/api/live` with `Sec-Fetch-Site: same-origin` answered 200 with `text/event-stream; charset=utf-8`, `no-store`, `X-Accel-Buffering: no` and the frame policy, then `event: ready`, `data: {"state": "READY", "cursor": "44"}`, `id: 44` and `retry: 3000`, and a `: ping` about 15 s later, until `curl`'s 20 s limit. The same request with `Sec-Fetch-Site: cross-site` answered 403. The five pages answered 200 in 0.22 to 0.42 s. No trade happened during the 20 s.
  - `NOT RUN` on the PC: a fill reaching an open page (none happened during the check; the browser suite showed it in the cloud), the desktop pop-ups in the owner's browser (off until the owner turns them on in the bell's menu), Firefox and Safari, and a count of reads a minute.
