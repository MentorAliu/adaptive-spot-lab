# Frontend architecture and user experience

The spot app's four pages ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md)). The pages of M2 to M11 (Home, Markets, Decisions, the coins, the agents, the research, the futures) and their sections are in the [archived copy](archive/contracts/FRONTEND.md), history only.

## Mandatory workflow

Use [SHADCN_WORKFLOW.md](SHADCN_WORKFLOW.md) for every UI change, and [LIBRARIES.md](LIBRARIES.md) for dependency and integration policy. The preset `b2fms61Bqi` is authoritative for visual primitives; the official Lightweight Charts skill applies to every chart change. The app's primitives are the 22 in `src/components/ui/` (ExecPlan 0061 removed the ten no page used); add another only with the shadcn CLI.

## The four pages (ExecPlan 0060)

IMPLEMENTED by [ExecPlan 0060 §4.9](plans/0060-spot-trading-only.md#49-the-pages) with the preset's shadcn primitives and Lightweight Charts; VERIFIED by the Vitest suites (`src/**/*.test.ts(x)`, on the engine's own answers from the browser chain, `src/spot/samples`) and the browser suites on a scratch database ([TESTING](TESTING.md)); OBSERVED on the owner's PC since the install of 2026-11-12. The menu (`src/components/app-nav.tsx`) has four items; the page shown carries `aria-current="page"`. The futures, decisions, markets, coins, agents, research and experiments pages are gone and answer "Page not found", like any unknown address; `app-nav.test.tsx` checks every `to="…"` in the source against the routes the app has.

| Item | Address | Shows |
|---|---|---|
| **Cockpit** | `/` | The status pill (`src/spot/status.ts`: trading, held, stopped or unknown, with a note for each cause; a read that failed makes it unknown and is named); the account's value with the USDT, the BTC at the best bid, the share in Bitcoin, the change since the run began and the value since then on a chart, and, once the run has two timely daily references, the run against holding Bitcoin over the same days ([below](#the-run-against-holding-bitcoin-execplan-0061)); the rule's reading of the day in words ("Trend up 2 of 3: hold 5.1% in Bitcoin; bought 0.00835 BTC") with the next reading's time; the newest trades; Bitcoin's spot chart (1d, 4h, 1h or 15m candles, the choice kept in the browser) with a marker for each buy and sell, told in words below it |
| **Trades** | `/trades`, `/trades?tab=readings` | Each buy and sell (time, side, quantity, price, fee, why), newest first, with Load more; the **Daily readings** tab, every reading of the rule with its trend, target, outcome and trade |
| **Backtest** | `/backtest`, `?window=SINCE_2023` or `LAST_12_MONTHS` | The three windows as tabs (since 2019, since 2023, the last 12 months); the rule beside holding Bitcoin on one chart from 10,000 USDT with the rule's trades marked; each one's final value, return, return a year, worst fall, fees and trades; a row per year; the data's dates and how the backtest is made. The server writes the stored result into the page itself |
| **Settings** | `/settings` | Four sections: **Trading run** (the run with Pause, Resume, Stop and sell, or Start after a stopped run, each confirmed in a dialog, by idempotency key, the outcome shown as the engine reports it), **Rule and limits** (the rule, the limits and the costs in words from the stored definitions, with their hashes), **Account** (the top-up and its history, M1's), **Health** (the feed, the engine, the database and the app's version) |

The header keeps the live badge and trade alerts (ExecPlan 0047's stream, the spot fills' toasts and desktop pop-ups), the time zone note (ExecPlan 0037) and the theme switch. An address a page does not know (`?tab=everything`, `?window=EVERYTHING`) is dropped by the route's search validation, not passed on. No page carries a disclaimer ([DECISIONS](DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)).

## The run against holding Bitcoin (ExecPlan 0061)

IMPLEMENTED by [ExecPlan 0061 §4.3](plans/0061-clean-up-after-the-spot-switch.md#43-the-cockpits-comparison) after loading the official shadcn skill and the project's discovery (preset `b2fms61Bqi`, no component added; [INTEGRATION_EVIDENCE](INTEGRATION_EVIDENCE.md)). On the Cockpit's value card, under "Today" (`SinceStart` in `src/cockpit/value-card.tsx`): "Since 13 Nov · Run +0.42% · Bitcoin −2.10%", from the overview's `run.since_start` ([API_CONTRACTS](API_CONTRACTS.md#the-run-against-holding-bitcoin-execplan-0061)). Each value is signed and coloured by its sign (`--positive`, `--negative`), with a tooltip: the run's value per unit over the two days, after fees, a top-up not being a gain; Bitcoin's two daily closes in USDT. The day is the first reference's, in the viewer's zone. Nothing shows while `since_start` is `null`. It is a description, not a verdict: no badge says better or worse. Tested in `src/cockpit/cockpit.test.tsx` on a SYNTHETIC pair and on the sample answer without one.

## The look

The shell, from [ExecPlan 0036](archive/plans/0036-a-clear-beautiful-app.md) and [0048](archive/plans/0048-the-cockpit.md), with only the preset's shadcn components and Lucide icons:
- **The shell** (`src/routes/__root.tsx`): shadcn's Sidebar (`inset`, collapsible to icons, Ctrl/Cmd+B) from 768 px with the app's name, the menu (`src/components/app-nav.tsx`) and the time zone of the pages' times; below 768 px a tab bar at the bottom with the same four links, so exactly one `Primary` navigation is visible at any width. The bar above every page (`src/components/site-header.tsx`) has the sidebar's toggle, the app's name on a phone, the live badge, the trade alerts' bell and the theme switch. The Sidebar's inset is the page's only `main`.
- **Links stay links.** A menu item, a tab or an action that looks like a button is a router `Link` or an `<a>` styled with `cn(buttonVariants(…))`; Base UI's Button would give it `role="button"`.
- **Theme:** shadcn's TanStack Start dark mode (`theme-provider.tsx`, `mode-toggle.tsx`): Light, Dark or System, System by default, stored in `localStorage` under `theme` and set on `<html>` before hydration. The charts keep Lightweight Charts' own look and follow the theme live (`src/lib/chart-theme.ts`).
- **Colours:** Lightweight Charts' green rising and red falling candles, the open candle grey (`#9e9e9e`); `--positive`, `--negative` and `--warning` tokens (`src/styles.css`) for money won and lost and for what needs a look, AA as text in both themes.
- **States** (`ToneBadge` in `src/components/page-parts.tsx`): the API's word with a tone, each a badge variant and an icon; colour is never the only cue. **Tables:** tabular digits; a column marked `numeric` in its meta is right-aligned.

## Values and times

From [ExecPlan 0037](archive/plans/0037-clear-values-in-local-time.md), display only: requests, forms and caches keep the API's exact decimal strings and UTC instants.
- **One format per kind of value** (`src/lib/display.ts`), from the exact string through `Intl.NumberFormat`, never through a float: USDT to the cent (gains and losses signed), prices to at least two decimals, BTC quantities exact, NAV to four decimals, percentages from the exact fraction. A value that is not a decimal string is shown as the API sent it.
- **Times** in the viewer's time zone, "22 Oct, 13:58:04" with the year only outside the current one, as a `<time>` element (`DateTime`, `src/components/date-time.tsx`) whose hover text gives the offset and the instant in UTC. A rule that runs on the UTC day says so and gives its moment on the viewer's clock.
- **Server rendering:** the server writes the zone the `asl_time_zone` cookie names, UTC until the browser has set it; `TimeZoneProvider` hydrates with it, then the browser's own zone takes over and the cookie remembers it.
- **Charts:** the time axis and crosshair through `tickMarkFormatter` and `localization.timeFormatter` in the viewer's zone (`src/lib/chart-time.ts`). Browser tests run in UTC; `e2e/local-time.spec.ts` runs in Budapest.

## Live trades and pop-ups

From [ExecPlan 0047](archive/plans/0047-live-trades-and-pop-ups.md), kept for the spot fills by 0060. Read-only: every number on a page is still the engine's read.
- **The stream** (`src/routes/api.live.ts`, `src/live/live.server.ts`): `GET /api/live`, behind the Host check and Start's `createCsrfMiddleware` (a request whose Fetch Metadata is not `same-origin`, or has none, is refused with 403), asks the engine's `GET /v1/spot/live` with the service key, forwards a `Last-Event-ID` that is a sequence (400 otherwise) and passes the events through with `Cache-Control: no-store`; any refusal or failure of the engine is a 503 with no detail.
- **One connection per browser** (`src/live/live.ts`): the tab holding the Web Lock `asl.spot.live` opens the one `EventSource` and relays its events, parsed with strict Zod schemas, and its state to the other tabs over the `BroadcastChannel` of that name; when it closes, the next tab waiting for the lock takes over. A lost stream resumes by itself with `Last-Event-ID`; a refused one is opened again after 5, 10, 20, 40, then every 60 seconds. Without Web Locks or `BroadcastChannel` each tab opens its own.
- **Each tab** (`src/live/live-trades.tsx`): an event invalidates the queries under `["spot"]`; the reads on screen refetch. While the stream is live the lists poll every 60 s instead of 5 (`src/spot/spot.query.ts`); the overview keeps 2 s. A visible tab shows the toasts after the browser's shared cursor (`asl.spot.toast-cursor`); a database older than the cursor (a restore) starts it again.
- **Desktop pop-ups** (`src/live/live-alerts.ts`): off until turned on in the header's bell menu, which asks the browser's permission on that click and keeps the choice in this browser (under the futures app's key `asl.futures.desktop-alerts`, so the choice carried over). Then, when fills arrive and no tab of the app has focus 400 ms later, the tab holding the stream shows one `Notification` per fill (the newest three, then a summary).
- **Header** (`src/components/live-status.tsx`): a status `Badge`: **Live**, **Connecting** (`Spinner`) or **Offline**; on a phone only the icon shows, and its sentence stays for screen readers.

## Server-state ownership

TanStack Query owns fetched server data and mutation state; Router owns navigation and validated URL search state; RHF owns form state; React state owns transient local interaction. Financial authority stays in the backend.

All current and future user-selected filters on a view belong in validated Router search params. Changing one filter retains the others, so the selected view survives refresh, sharing and browser history. Keep only temporary interaction state in React state. Format display values and timestamps for readability without changing canonical decimal strings, provenance or UTC event identity.

Implement Start's current official Query SSR integration with a fresh QueryClient per router/server request and a stable client for browser navigation [TS-01](REFERENCES.md#ts-01). Do not construct a module-global server cache or independently dehydrate the same data twice. Keep server-only credentials and backend clients out of client bundles [TS-03](REFERENCES.md#ts-03).

Define shared query options and keys containing the resource, interval, window, cursor and filters where they affect results; every spot read shares the first key `spot`, so the live stream's changes refresh them all. Router loader dependencies must match validated search inputs. Query freshness is a UI policy, not permission to trade on stale data. Record a rationale for freshness intervals rather than copying documentation sample numbers.

For Query-backed I/O, consume the `queryFn` context's `signal` and forward it through the supported transport, including Start server-function call options; document any downstream cancellation boundary that cannot receive it. The app constructs `QueryClient` without `defaultOptions` (`src/system/query-client.ts`) and uses TanStack Query's built-in defaults. If a later feature needs app-wide overrides, configure them at `QueryClient` initialization rather than repeating them in shared `queryOptions`. Use `select` when an observer needs a derived slice or transformation while the cache should retain the canonical response; do not add an identity projection when callers use the complete payload. Check the installed TanStack versions and official Query/Start guidance when composing these APIs, including documented Suspense cancellation limits.

On an owner-confirmed mutation, reconcile with the authoritative response and invalidate the actual affected Query keys. Do not optimistically add funding, fills or a run's change to financial totals; a run request is shown as accepted until the engine reports its outcome. Idempotency prevents repeated clicks and retries from posting twice.

## Transport and incremental updates

Use same-origin Start server functions and routes as the BFF to the private API, with the Host check and origin/CSRF controls on mutations and on the live stream. Private account responses must not be publicly cached. Do not expose internal API addresses, service credentials or DB access to the browser.

Canonical snapshots with bounded polling, and one event stream per browser through the BFF ([above](#live-trades-and-pop-ups)). Stream events carry the ledger's ordered sequence as their id; the browser refetches its snapshots on every event and on a reconnect, and never applies a financial delta itself. The browser never opens a Binance connection.

The pages report the book's age and the last valuation's time separately from the page's render time. A cached value is never relabeled fresh merely because the UI rerendered.

## Forms

Use the official shadcn/RHF pattern compatible with the generated base and installed versions [UI-05](REFERENCES.md#ui-05). Use Zod through the compatible resolver; distinguish input/output types if transformations occur. Server-side Pydantic/domain validation remains authoritative.

For RHF forms, use `formState.isSubmitting` for the submission request, Zod/`FieldError` for field validation, and `setError("root.server", …)` for safe form-wide server failures. Clear stale server errors when an input changes. Keep post-review financial confirmation, unknown-outcome resolution and other independent account actions in their own state; a prepared top-up draft is not a posted contribution. Reset the top-up input only after the authoritative result is `POSTED`.

Financial amounts remain canonical decimal strings; do not round-trip through `Number`, `parseFloat`, or `valueAsNumber` before posting. Reject NaN/infinity, negative/zero top-ups, unsupported precision and malformed locale input. Show explicit validation rather than guessing whether a comma was a decimal or grouping separator.

A top-up and each run control (Pause, Resume, Stop and sell, Start) are confirmed in a dialog that says what happens, and each uses a stable idempotency key for retries of the same submission. An outcome the BFF could not read is checked by its key, never resubmitted blindly.

## Tables and chart composition

Use TanStack Table's headless API with shadcn Table and controls [UI-06](REFERENCES.md#ui-06). Define typed columns and stable row IDs. Financial sorting must use authoritative numeric/order keys, not lexicographic formatted strings. Paginate large histories on the server; filter/sort parameters are validated and bounded. Virtualization is optional after measurement, not a default dependency.

Lightweight Charts runs only in a client-safe boundary. Guard DOM access, create charts in the correct React lifecycle, clean up listeners/ResizeObserver/chart instances, and handle Strict Mode remounts. Test resizing, route transitions, empty/error states and the installed chart API. Do not assume old series-creation signatures [FE-02](REFERENCES.md#fe-02), [FE-04](REFERENCES.md#fe-04).

Use UTC in storage and event identity; a chart shows its times in the viewer's zone through its formatters (`chartTime` in `src/lib/chart-time.ts`), never by shifting the timestamps. Convert milliseconds/seconds explicitly to the chart's expected time representation. Keep chart points sorted/unique; handle provisional candle updates separately from final bars. Convert decimal strings to finite JavaScript numbers only at the visual rendering boundary; those numbers must never return as financial inputs. Preserve gaps and stale intervals instead of drawing them as confirmed executable prices. Show required TradingView attribution and license notices.

## Accessibility and honest presentation

Use preset semantic tokens; color must not be the only indicator of profit/loss, feed status, or order state. Support keyboard navigation, focus return, chart text/table alternatives, readable precision, reduced motion and responsive layouts. Use existing shadcn primitives for alerts, dialogs, loading and empty states.

Differentiate zero from unknown and provisional from final. Label synthetic tests. Since 2026-10-30 the pages carry no disclaimer: no PAPER badge, no "paper" or "virtual" wording, and no notice that fills are modeled or that a page changes nothing ([below](#no-disclaimers-on-the-pages--2026-10-30)). Equity growth caused by contributions must be visibly separated from profit. Show the result and the fees without double-counting. If daily return cannot be validly computed, show unavailable with reason—not `0%`.

## No disclaimers on the pages — 2026-10-30

The owner's rule ([DECISIONS](DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)), in force: no PAPER badge, money reads "USDT", and no title or label says paper, virtual or simulated (the tab's title is "Adaptive Spot Lab"; the app's name reads "Trades by itself"). What stays is every sentence that says how a number is made (after fees, the book a fill walks, the fee rate) and every state, error and warning about the app itself. The text of each page as it was on 2026-10-30 is in the [archived copy](archive/contracts/FRONTEND.md#no-disclaimers-on-the-pages--2026-10-30).

## Required integration checks

SSR private data isolation, hydration without duplicate reads, mutation reconciliation, decimal form behaviour, sorting and paging, stale-data display, refused trades and requests, top-up retries, the chart's lifecycle and accessibility; real browser evidence for the preset ([TESTING](TESTING.md)). Installing a package is not UI verification.
