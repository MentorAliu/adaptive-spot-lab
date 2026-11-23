# ExecPlan 0048 — The Cockpit (the new design, part 1), then Trades, a trade and Decisions (part 2), then Markets and Settings (part 3)

**Status: APPROVED by the owner's ask on 2026-10-31 at 06:37:59 UTC ([DECISIONS](../../DECISIONS.md#2026-10-31--the-new-design-starting-with-the-cockpit-execplan-0048)); the design choices are the thread's, under the owner's standing "decide for me" (§13). Part 1, Home as the Cockpit, installed on the PC on 2026-10-31 at 09:09 UTC (§14). Part 2, Trades, a trade's page and Decisions, on the owner's ask of 09:18 UTC ([DECISIONS](../../DECISIONS.md#2026-10-31--the-new-design-for-trades-a-trade-and-decisions-execplan-0048-part-2)), merged on the owner's yes at 11:26 UTC and installed at 12:09 UTC (§14). Part 3, Markets and Settings (§4.13–§4.15), merged on the owner's yes at 13:18 UTC and installed at 13:23 UTC (§14).** Written by the project thread "Build the new Claude Design redesign" from `main` at `793abdd`. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)): the owner's new design for the five pages, built one page per install with the app's own shadcn components. Nothing changes of the trader, the policy, the limits, the money paths, the protection or the database's tables.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`.

## 1. Goal

The owner asked on 2026-10-31 at 06:37:59 UTC: "Implement this design in this codebase: <a Claude Design link> Read the design's files from that link. Match how it looks, using this codebase's own components and conventions." The design (a Claude Design page, read with the Artifact tool's read on 2026-10-31) redraws all five pages with less text and fewer numbers, the key figures first, more icons and pictures instead of sentences; its Home is a "Cockpit".

Observable outcome of part 1:
1. Home is the **Cockpit**: one screen that says whether the app trades (a status pill), what the account is worth and made (the equity, its result and return since the start, today, the drawdown against its limit, and the equity curve over 24 hours, 7 days or all), the open position (its result at the mark and a price rail from liquidation through stop and entry to the target), the trader's latest call and its last twelve decisions, the engine room (agents, allowance, mark, funding, feed), the 15-minute chart with its marks, the latest closed trades in R, and four tiles that answer "Is the trader any good?" (its 1-hour calls against a coin flip, the league, the coach's lean, the luck check).
2. The detail Home held moves to the page each tile opens: the scorecard, the result checks and the coach's note to Decisions (`#scorecard`, `#checks`, `#coach`), the league table to Trades (`#league`).
3. The menu names Home "Cockpit" with a gauge icon; Decisions has a brain icon; the brand mark is a flask, the subtitle "BTCUSDT · perpetual".
4. Every number is still an engine read; nothing on the page writes.

## 2. What the app has

`OBSERVED` in the code at `793abdd`:
- **Home** (`src/home/home-page.tsx`, `src/futures/home-cards.tsx`): a long page of cards: the trading status with its notes, the account's facts, the open position's facts, the chart, the latest trades table, the scorecard, the result checks, the league table and the coach's note.
- **The reads** (`src/futures/futures.query.ts`): the overview (equity, NAV, contributions, today, drawdown, limits, latches, mark, position) every 2 s; trades, decisions, scorecard, checks, league, coach on their own intervals; the live stream's invalidation ([ExecPlan 0047](0047-live-trades-and-pop-ups.md)). There is no read of the account's value over time.
- **NAV per unit** starts at 100 (`INITIAL_NAV` in `services/engine/app/accounting.py`), so the return since the start is NAV / 100 − 1, top-ups left out. The futures engine records a valuation at each step (`futures_valuations`, `quality` `VALID` or not).
- **The UI kit**: shadcn's `base-nova` preset `b2fms61Bqi` on Base UI 1.8.0 with 28 components installed; no `HoverCard`, `Popover`, `Tabs` or `Switch`. The content area is a Tailwind container (`@container/main`). Lightweight Charts 5.2.1.

## 3. Scope

In (part 1): the Cockpit at `/` (§4.1–§4.8); the read `GET /v1/futures/valuations` (§4.2); the cards' new places on Decisions and Trades with their anchors; the menu's name and icons; three colour tokens (`--positive`, `--negative`, `--warning`) and one animation; the unit and browser tests.

In (part 2, §4.9–§4.12): Trades, a trade's page and Decisions redrawn; four shadcn components added with the official CLI on the owner's PC (`Tabs`, used by Decisions; `HoverCard`, `Popover` and `Switch`, for part 3); the web's list reads asking for a page size; the unit and browser tests. Out of part 2: Markets and Settings (part 3, one install); any engine change, migration, money path or dependency.

In (part 3, §4.13–§4.15): Markets and Settings redrawn with the components part 2 added; the unit and browser tests. Out of part 3: any engine change, migration, money path or dependency, and any control the engine does not have.

Out of part 1: the redesign of Trades, a trade, Decisions, Markets and Settings (later parts, each on the owner's word); a new shadcn component (the design's hover cards and popovers become `Tooltip` and `Sheet`; adding a component needs the shadcn CLI, whose registry this cloud machine cannot reach, §7); a migration, a money path, a new dependency.

## 4. Design

### 4.1 The status pill

`StatusPill` (`src/cockpit/status-pill.tsx`) words the same recorded state as Home's card did (`futuresStatus`, `src/home/trading-status.ts`): "Trading · all good" as a quiet `Badge` when there is nothing to see; otherwise a `Button` ("Trading · 2 notes", "On hold · 1 needs you", "Not trading · 1 problem", "Status unknown") that opens a `Sheet` (bottom on a phone, right otherwise) with each note, its kind (Needs you, Problem, Info) and a link to the Settings section that handles it ("Open Settings: Health"), and when it was checked.

### 4.2 The equity card and its curve

The hero: the equity in USDT, the result since the start (equity − contributions, exact) and the return (NAV / 100 − 1, exact, with `BigInt`), today's net, and a gauge of the drawdown against the policy's limit (a lock when the daily loss latch holds). The curve is a Lightweight Charts `BaselineSeries` of NAV per unit with its base at the window's first point, so gains fill above and losses below in the theme's colours, the axis in percent from the base; 24h, 7d or All in a `ToggleGroup`, kept per browser.

`GET /v1/futures/valuations?window=24h|7d|all` (service key; `services/engine/app/futures/views.py` `valuations_view`): the `VALID` valuations of the window, the newest of each bucket (15 minutes, 1 hour, 4 hours), plus the window's first as the base; `{state, window, bucket_seconds, since, base_nav, points: [{time, nav, equity}]}`. Read-only, one repeatable-read snapshot; `SCHEMA_PENDING` before the futures schema.

### 4.3 The position card

Open: the side and leverage as a badge, a ring for the time left to the time exit, the result at the mark (or "—" with "No fresh mark"), the price rail (`price-rail.tsx`: liquidation, stop, entry, target and the mark, with the distance to the stop) and a Details `Sheet` with the exact figures and a link to the trade. Flat: a radar while the run waits for a setup, or a lock or pause tile with why (daily loss limit with its reset, cooldown, paused, stopped), the next decision's time and the entries used today as pips.

### 4.4 The trader card

The latest decided call: its verb and icon, the expected move and its horizon, confidence pips, the rationale (three lines), what followed (the 1-hour call's verdict or "Call due"), a Reasoning `Sheet` with the full text and a link to the decision; a ring to the next quarter-hour decision (a hand when the agents' authority is missing, fuel when the usage limit holds); a strip of the last twelve decisions, each a tooltip and a link to Decisions.

### 4.5 The engine room

One strip: live state, each agent with its state dot and model, the Codex allowance, the mark (stale when old), the funding rate with a ring to the next 8-hour settlement, and the feed.

### 4.6 The chart and the latest trades

The 15-minute candle chart with the trades' marks (the existing `PerpChart`, 340 px), linked to Markets ("Full chart"). The latest closed trades: a strip of bars by R (capped at 2.5R), then rows with side, entry → exit, age, net, R, how it closed and the review's grade, each a link to the trade.

### 4.7 Is the trader any good?

Four tiles, each a link to its detail: 1-hour calls (a ring of the share right against the coin flip, or too few) → `/decisions#scorecard`; League (bars of each account's return) → `/trades#league`; Coach (its lean, confidence and time left) → `/decisions#coach`; Luck check (where the entries fall against the luck floor's cuts at 5% and 95%) → `/decisions#checks`. A tile whose read failed says so.

### 4.8 Layout

A bento grid on the content area's container queries: one column on a phone; two from 672 px; from 896 px seven to five columns, the equity card spanning two rows beside the position and the trader. Loading shows `Skeleton`s, an empty read an `Empty`, a failed read a retry; nothing is guessed in a read's place. Times are in the viewer's zone and drawn after hydration.

### 4.9 Trades (part 2)

`src/trades/`: the `h1` with the trades' count ("3 trades", "Latest 50 trades" while more remain) and the account as a `ToggleGroup` of short words with icons (Trader, Hold, Trend, Gated; the address keeps `?account=`). A **Last N** card: the last 48 closed trades as bars by R, with their net after fees and funding, the share won and the average R, worked out from the trades the page read. Then the trades, newest first, fifty at a time with Load more: a table from 672 px of content (closed or Open, side, entry → exit to the dollar, net (an open trade's at the mark), R with a small bar, how it closed, the review's grade), a list of items below it; each row links to its trade. Leverage, costs, fills and funding move to the trade's page; a twin's trade has no page, so its rows keep their costs. The league table stays below.

### 4.10 A trade's page (part 2)

`src/trade/`: a hero with the side and leverage as the `h1` ("Long · 2x"), when it opened and closed and how long it ran, how it ended (how it closed and the review's grade, as icons and words) and its net with its R; then a grid of twelve columns from 896 px of content. The chart: the trade's candles at the finest of 5 minutes, 15 minutes or 1 hour whose candles reach back to its entry, its fills as marks, and its stop, target and liquidation as lines while it is open. The price rail at the close (or now, while open), the costs as a share of the risk with each part, the review (its grade as a tile, its lesson and tags; code's numbers, the reviewer's answers and its factors in a `Sheet`), the decisions behind it as a timeline ending with the fill that closed it (each opens its reasoning), and the fills and funding as a table.

### 4.11 Decisions (part 2)

`src/decisions/`: the **Playbook** first (`#coach`): the coach's note in force as which way it leans and how sure, the setup it suggests as badges, what to avoid, and the lesson of the last day's decision review, with the time the note has left; what it rests on and whether following it helped open in a `Sheet`. Then `Tabs` in the address (`?tab=scorecard`):
- **Timeline**: the decisions by local day, newest first, a hundred at a time with Earlier decisions. A row is the decision's verb as a tile on the timeline's line, the time, why it ran, the forecast, the confidence as pips, its reason in a line, the engine's answer and how it looked after 15 minutes, 1 hour, 4 hours and 24 hours (right, wrong, neither or pending, from code's labels of [0043 §4.2](0043-score-every-decision.md#42-the-labels-code)); a legend says what the icons mean. Each row opens its reasoning: the rationale, the forecast, its choices, its invalidation, the coach's note's use, the reason code, the engine's answer and every checkpoint's label and move. A job that ended without a decision stays as a "No decision" row linked to its workflow. A day's count shows once the whole day is loaded.
- **Scorecard** (`#scorecard`, `#checks`): the 1-hour calls of 24 hours, 7 days and all time as rings against the coin flip; the calls by how sure the trader was as bars with the coin flip marked; the luck check on a band from below the luck floor to above, with the costs per trade. Every table and check Decisions held (the scorecard, the day's review, the four checks) is one tap away under "Every score and check".

### 4.12 Reads and components (part 2)

The trades', a twin's and the decisions' server functions pass a page size (1 to 100, the API's own range) to the existing reads; the lists are TanStack Query infinite queries under `["futures"]`, so the live stream's invalidation refreshes them; a refetch reads each loaded page again in order. The Cockpit keeps its own reads. No engine change.

### 4.13 Markets (part 3)

`src/perp/futures-card.tsx`, `src/routes/markets.tsx`: the `h1` alone, then a strip of the market's numbers, each a term and its value: the mark and the index (to the cent), the spread (the bid and ask in its tooltip), funding (the rate now to two decimals, a ring and the words for the time to the next funding; the exact rate, the next funding and the last settled one in its tooltip) and the feed (a dot and a word). What holds the data (the schema not installed, a failed read, the feed down and why) stays an alert under the strip. Then the chart card, "BTCUSDT perpetual", edge to edge and taller (440 px, 640 px from 768 px of content), with the interval as a `ToggleGroup` in the card's action (1m, 5m, 15m, 1h; named "1 min" to "1 hour" for screen readers). It opens on 15m, the trader's own bars, as the design does; the address keeps any other (`?interval=1h`). The account's fills and open levels stay on the chart.

### 4.14 Settings (part 3)

`src/settings/`: the `h1` alone and the sections' links as small outline buttons (a row that scrolls sideways on a phone), each section an `h2` with its icon.
- **Agents**: one card holding a list of rows (`ItemGroup` of `Item`s: an icon tile, a word, at most one line, its control or state on the right): the agents' switch as a `Switch` (the same requests and confirmations as before, showing the recorded state); the agents' check (its state as a badge, the cases, calls and new entries in a `Popover`); the ChatGPT sign-in (a badge, and the way to sign in again on the PC when it is missing or refused); the usage limit (Available, or paused until a time); the trade reviews (the trades reviewed as a badge, a line for what waits and the coach's note, every count in a `Popover`); the worker (a dot and a word).
- **Models**: a card per agent, two across (four from 1280 px of content): its icon as an `Avatar`, its state as a dot, its model as a badge and five lines (runs, effort as pips, last call, calls, tokens); what it does, its version, per-call figures and fallbacks in a `Popover`. Codex's card keeps the table of the models the sign-in offers.
- **Trading run**: the run's state as an icon tile and a word ("Trading"), what holds it in a line, its buttons (Stop and close and its confirmation in the destructive colour) and four facts (started, from, drawdown, stopped). The dialogs keep the run's number.
- **Limits**: eight tiles (the leverage cap with pips for the open position's leverage; risk per trade with its amount at the stop at the current equity, a display figure; entries and decisions today as bars; the daily loss as reached or not, with a lock when latched; the drawdown as a gauge against its limit; the entry cooldown; the costs), then the policy's name as a badge.
- **Account**: one card with the six balances as figures and their unit, the valuation's line and the top-up form inline; the funding history as a table (date, flow, amount, NAV before, state).
- **Health**: the app's parts as tiles (an icon, the name, a dot and its state, the meaning in a tooltip), then the twins' and the scorer's cards, the scorer's words shorter.

### 4.15 Components (part 3)

`Switch`, `Popover`, `Item`, `Avatar`, `ToggleGroup`, `Progress`, `Card`, `Badge`, `Tooltip` and `AlertDialog`, as installed; no new component. Two small parts of the app's own: `SettingRow` and `Tile` (`src/settings/parts.tsx`). The run card, the limits, the balances and the health tiles reuse the Cockpit's pictures (`IconTile`, `Pips`, `Gauge`, `Ring`, `StatusDot`).

## 5. Authority

None changes. The new read is a read of records the engine writes; the page writes nothing; the cards that moved keep their reads.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| C1 | The valuations read: windows, buckets, the base, `VALID` only, 422 for another window | engine, scratch PostgreSQL: `tests/test_m11_futures_api.py` |
| C2 | The equity, result and return exact from the reads; the curve's points and text | unit: `src/lib/display.test.ts`, `src/cockpit/cockpit.test.tsx` |
| C3 | The pill, the position (open and flat), the trader, the engine room, the trades and the tiles from the engine's own sample answers; a failed read says so | unit: `src/cockpit/cockpit.test.tsx` |
| C4 | The menu: Cockpit, Trades, Decisions, Markets, Settings; links name only routes the app has | unit: `src/components/app-nav.test.tsx`; browser: `foundation.spec.ts`, `pages.spec.ts` |
| C5 | The Cockpit on the seeded app: why it does not trade with each note linked, the equity and its curve, the open position and its details, the chart's marks, the latest closed trades, no sideways scroll at 390 and 1440 px | browser: `pages.spec.ts`, `local-time.spec.ts` |
| C6 | The tiles open their details on Decisions and Trades | browser: `scores.spec.ts`, `checks.spec.ts`, `reviews.spec.ts`, `twins.spec.ts` |
| C7 | A position that opens shows on the Cockpit without a reload | browser: `live.spec.ts` |
| C8 | Trades: the count, the account switch, the results strip, the rows and Load more; a twin's rows with their costs | unit: `src/trades/trades.test.tsx`; browser: `pages.spec.ts`, `twins.spec.ts`, `local-time.spec.ts` |
| C9 | A trade's page: the hero, the chart's interval and marks, the costs, the review and its sheet, the decisions behind it, the fills and funding | unit: `src/trade/trade.test.tsx`; browser: `pages.spec.ts`, `reviews.spec.ts`, `checks.spec.ts` |
| C10 | Decisions: the playbook and its sheet, the timeline by day with each row's reasoning, Earlier decisions, the scorecard tab and every score and check | unit: `src/decisions/futures-decisions.test.tsx`, `src/futures/scores.test.tsx`, `src/futures/review.test.tsx`; browser: `pages.spec.ts`, `reviews.spec.ts`, `scores.spec.ts`, `checks.spec.ts`, `local-time.spec.ts` |
| C11 | Markets: the strip's numbers and the feed, the interval switch kept in the address, the chart at each interval | unit: `src/settings/settings.test.tsx`; browser: `perp.spec.ts`, `pages.spec.ts` |
| C12 | Settings: the switch row and its dialogs, the check's and the reviews' details, the model cards, the run card and its buttons, the limits' tiles, the balances and the top-up, the health tiles | unit: `src/agents/controls.test.tsx`, `src/agents/model-cards.test.tsx`, `src/futures/review.test.tsx`, `src/futures/decision-review.test.tsx`, `src/settings/settings.test.tsx`; browser: `pages.spec.ts`, `reviews.spec.ts`, `funding.spec.ts` and the account suites, `m5.spec.ts`, `m7.spec.ts @profile` |

## 7. Official sources

`OBSERVED` on 2026-10-31, at the installed versions ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0048-the-cockpit--2026-10-31)):
- The official shadcn skill (`skills/shadcn/SKILL.md` in `shadcn-ui/ui`, SHA-256 `93951e5e…3d27592`) and the project's discovery (`shadcn info --json`: TanStack Start, Tailwind v4, `base-nova`, base `base`, Lucide, preset `b2fms61Bqi`). `shadcn add hover-card popover --dry-run` answered that the registry item was not found at the raw GitHub registry this machine can reach, so no component was added.
- The official Lightweight Charts skill (`.github/skills/lightweight-charts/SKILL.md` in `tradingview/lightweight-charts`, SHA-256 `921fd3be…acfaf1eb00`, 28,121 bytes) and the installed 5.2.1 typings: `BaselineSeries` with `baseValue: { type: "price", price }`, a custom `priceFormat`, `autoSize`, `chart.remove()` on unmount.

Part 2, `OBSERVED` on 2026-10-31 ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0048-part-2-trades-a-trade-and-decisions--2026-10-31)): the shadcn skill as above, re-read before the first edit; `Tabs`, `HoverCard`, `Popover` and `Switch` added on the PC with the official CLI 4.23.0 on preset `b2fms61Bqi`; the shadcn documentation of `Tabs`, `Progress` and `Sheet` for the Base UI flavour; TanStack Query's guides on infinite queries and prefetching, with the installed 5.104.0 typings; Base UI 1.8.0's `Progress` typings.

Part 3, `OBSERVED` on 2026-10-31 ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0048-part-3-markets-and-settings--2026-10-31)): the shadcn skill as above (the same SHA-256, read again); the shadcn documentation of `Item`, `Switch`, `Popover`, `Avatar`, `ToggleGroup` and `Card` for the Base UI flavour; the components as part 2 installed them.

## 8. Data and trust boundaries

The browser reads the new route only through a server function with the service key on the server, as every futures read; its answer is validated with a strict Zod schema. The equity window and nothing else is kept in the browser (`localStorage`, `asl.cockpit.equity-window`). No new secret, host, port or permission.

## 9. Implementation sequence

1. Engine: `valuations_view`, the route and its models, `openapi.json`, the web's generated types; the test.
2. Web: `src/cockpit/` (the page and its cards, `geometry.ts`, `meaning.ts`, `visuals.tsx`, `states.tsx`, `preference.ts`), `src/hooks/use-now.ts`, `src/hooks/use-hash-scroll.ts`, the read (`futures.server.ts`, `futures.functions.ts`, `futures.query.ts`, `schemas.ts`), exact helpers in `src/lib/display.ts`, the tokens in `src/styles.css`, the menu, the moved cards on Decisions and Trades; `src/home/home-page.tsx` and `src/futures/home-cards.tsx` removed.
3. Tests (§6), then the contracts: [API_CONTRACTS](../../API_CONTRACTS.md), [FRONTEND](../../FRONTEND.md), [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md), [STATUS](../../STATUS.md), [COMMANDS](../../COMMANDS.md).

## 10. Verification commands

Cloud, as in [COMMANDS](../../COMMANDS.md): from `apps/web`, `pnpm typecheck`, `pnpm lint` (with the build's `.output` removed), `pnpm check`, `pnpm api:check`, `pnpm test`, `pnpm build`; from `services/engine`, `ruff check`, `python -m app.export_openapi --check`, the suite without a database, then on a scratch PostgreSQL `tests/test_m11_futures_api.py` and the futures suites, and the browser suites on `tests.m11_browser_fixture` (`reviews`, `local-time` + `pages` + `twins`, `scores`, `checks` on `seed`; `live` on `flat`). On the PC: the update's own checks, then a read-only look that `/` answers with the Cockpit.

## 11. Failure and rollback

- The valuations read fails or is empty: the curve says so ("Couldn't load the equity curve" with a retry, or "No curve yet"); the rest of the card is the overview's.
- Any other read fails: its card or tile says so; the others stand.
- Rollback: the previous image. No migration, so no data to restore.

## 12. Q01–Q10

Q01: the Cockpit at 390 and 1440 px, light and dark, in screenshots and the browser suites. Q02: shadcn's components, every picture with a text equivalent (`role="img"` with a label, or a tooltip), status as a button that opens a dialog. Q03: no money path; C1. Q04: the service key on the server only; the window a closed set. Q05: §11. Q06: one new read, once a minute per open Cockpit and again after each live change (its key is under `["futures"]`, [ExecPlan 0047 §4.5](0047-live-trades-and-pop-ups.md#45-query)). Q07: §10. Q08: nothing new to log. Q09: no migration; the previous image is the rollback. Q10: the contracts of §9; no new dependency.

## 13. Decision log

The owner delegates engineering choices ("decide for me", 2026-10-19); the thread took the recommended option each time:
- **One page per install, Home first**, as the coordinator relayed the owner's wish; Trades, a trade, Decisions, Markets and Settings follow, each on the owner's word.
- **The app's own components**, not the design's generated markup: `Tooltip` for the design's hover cards and `Sheet` for its popovers and drawers, since no new shadcn component can be added from this cloud machine (§7).
- **The detail moves, it is not removed**: the scorecard, checks and coach to Decisions, the league to Trades, each tile linking to its anchor.
- **NAV per unit for the curve**, so a top-up neither lifts it nor counts as return; the equity beside it is what the account is worth.
- **Three tokens** (`positive`, `negative`, `warning`), checked for AA contrast as text on the background, cards and muted in both themes, instead of fixed colours.

Part 2, on the owner's ask at 09:18 UTC ("I want other pages as well to have a great modern UX and UI that is meaningful, right now too much text and numbers are displayed, feel free to be creative") and "leverage shadcn components using skills and cli of shadcn":
- **Two installs, not four**: Trades, a trade and Decisions together, then Markets and Settings, so the owner waits for two double-clicks instead of four.
- **The components added on the PC.** The cloud machine's registry has no `base-nova` hover card (§7), so `Tabs`, `HoverCard`, `Popover` and `Switch` were added with the CLI where it answers, as one commit before the pages.
- **By how sure it was, not by market condition.** The design splits the calls by market condition; the API serves no condition per call, so the card splits them by the trader's own confidence, which the scorecard serves.
- **The tab in the address**, so a tile, a link or a reload opens the same view.
- **Short account words** (Trader, Hold, Trend, Gated) with icons in the switch; the tables keep the full names.
- **The trade's side and leverage as its heading** ("Long · 2x"), so the rows can leave leverage out.
- **The chart's level lines only while open**: a closed trade's stop may have been tightened since its entry, and the trade's read keeps only the levels in force.
- **Nothing removed**: the full scorecard, the day's review and the four checks under "Every score and check", the coach's note in full in the playbook's sheet, a job without a decision as its own row, every checkpoint in each decision's sheet.
- **"The last day's lesson"**, not "today's": the decision review covers the last finished UTC day.

Part 3, under the same ask and "decide for me":
- **What the engine has, not what the design draws.** The design draws a trade reviews switch and a ChatGPT sign-in button; the engine has no reviews switch and the sign-in is made on the PC, so the reviews row shows its counts and the sign-in row its state and the way to sign in again. It draws a daily-loss gauge; the read serves the latch, not the day's starting value, so the tile says reached or not.
- **The switch as a row's control.** shadcn's docs put a form's input in a `Field`; the agents' switch sends no form: a change asks in a dialog and shows the state the worker records, so it is the action of an `Item` row like the others.
- **Markets opens on 15m**, as the design does and the trader decides; the address keeps another interval.
- **The account summary card goes** (`src/account/account-summary.tsx`): its figures are the balances' strip; the history keeps its name, "Funding history".
- **Nothing hidden**: every count, case and figure the cards showed is in a `Popover` or a tooltip one tap away.

## 14. Progress

- 2026-10-31: the design read; the plan written.
- 2026-10-31, `IMPLEMENTED` as §9 lists, on the branch `claude/project-thread-9zpkc5` from `main` at `793abdd`, and `VERIFIED` in the cloud session (no Docker), commands as in [COMMANDS](../../COMMANDS.md):
  - **Web**, from `apps/web`: `pnpm typecheck` clean; `pnpm lint` clean (with the build's `.output` removed first); `prettier --check` over `src` and `e2e` "All matched files use Prettier code style!"; `pnpm api:generate`, then `pnpm api:check` "Generated TypeScript API types match"; `pnpm test` `42 passed` files, `359 passed` tests (`cockpit.test.tsx` 11); `pnpm build` exit 0.
  - **Engine**, from `services/engine`: `ruff check --no-cache .` "All checks passed!"; `python -m app.export_openapi --check` "FastAPI OpenAPI schema matches"; the suite without a database (`ASL_TEST_ISOLATED=1`): `2 failed, 1105 passed, 467 skipped, 425 errors`, the 2 failures COMMANDS' known database cases and every error a database case.
  - **Scratch PostgreSQL** 16.15, migrated to `0028_leaner_trader`: `tests/test_m11_futures_api.py` `10 passed`, with the new valuations test (C1). `tests/test_m11_*.py` with `tests/test_api.py` on a fresh database: `5 failed, 359 passed`. The failures: `test_api.py`'s status test (COMMANDS' known failure on `main`); `test_m11_committed_trader.py::test_a_refused_view_is_retried_with_its_rule_and_then_recorded`, which passed alone on a fresh database (as in [0047 §14](0047-live-trades-and-pop-ups.md#14-progress)); and three in `test_m11_scores_db.py`, which fail the same way on `main`'s tree at `793abdd` on a fresh database (OBSERVED; recorded in COMMANDS). None reads the new route.
  - **Browser suites** (the preinstalled Chromium, build 1243; the production build at `http://localhost:4318`; the API with `ASL_AGENTS_OFFLINE_TEST=1`; the SYNTHETIC feed). On a database seeded by `seed` at 08:21 UTC: `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` `15 passed`, then `scores.spec.ts` `4 passed`, then `checks.spec.ts` `3 passed` (C4–C6). On a database seeded by `flat`: `live.spec.ts` `4 passed` (C7). OBSERVED on the way: the first `pages.spec.ts` run failed where its links test clicked the last row in `main` on Trades, now the league table's; the test now names the trades' table (and the decisions' on Decisions). A run of `scores.spec.ts` on a database whose `pages.spec.ts` ran 15 minutes after its seed failed on the fixture's data, not the page (COMMANDS records both limits of the fixture's clock).
  - **Screenshots**, before (`main` at `793abdd`) and after, at 1440 and 390 px, light and dark, of both production builds against a stand-in for the engine that answers the web's reads with SYNTHETIC values (a scratch script of the session, not in the repository); the comparisons are in the project's files (`cockpit-redesign/`). The stand-in has no live stream, so the header reads Offline there.
  - `NOT RUN`: `reviews.spec.ts` (its fixture needs a database seeded after 10:30 UTC; COMMANDS); the Docker builds of the api and web images and the update on the PC; a look at the Cockpit on the PC's real data; Firefox and Safari; the older suites whose first wait changed from Home's "Trading status" to the Cockpit's heading and settled pill (`execution.spec.ts`, `m4.spec.ts`, `m5.spec.ts`; COMMANDS lists parts of them as retired since [0039 part B](0039-bitcoin-futures-on-paper.md#15-progress)) and `foundation.spec.ts`, whose database fixtures were not set up.
  - No independent review: no money path changed (§5); the new route reads `futures_valuations` only.
- 2026-10-31, part 1 **installed** on the PC: PR #153 merged on the owner's yes at 08:52 UTC (`7058d6c`); the owner's double-click ran `update-20261031T090510Z`, `COMPLETE` (08:54 to 09:09 UTC; no migration, schema `0028_leaner_trader`; reconciliation `OK`; `/`, `/trades`, `/decisions`, `/markets` and `/settings` answering 200; the agents' check `CHECK_PASSED`), read from its record through the folder the owner shares. NOT RUN: `reviews.spec.ts` for part 1 alone; part 2's run below covers the moved coach's note, on part 2's pages.
- 2026-10-31, part 2 `IMPLEMENTED` as §4.9–§4.12 list, on the same branch after `dba2cb4` (the four components), and `VERIFIED` in the cloud session (no Docker), commands as in [COMMANDS](../../COMMANDS.md):
  - **Web**, from `apps/web`: `pnpm typecheck` clean; `pnpm lint` clean (with `.output` removed first); Prettier run on the changed files only (the engine's sample JSONs untouched); `pnpm test` `45 passed` files, `378 passed` tests (`trades.test.tsx`, `trade.test.tsx` 4, `futures-decisions.test.tsx` 8, `display.test.ts` 16 among them); `pnpm build` exit 0; `pnpm api:check` "Generated TypeScript API types match".
  - **Engine**: unchanged (no file under `services/`), so its suites were not run again.
  - **Browser suites** (the preinstalled Chromium; the production build at `http://localhost:4318`; the API with `ASL_AGENTS_OFFLINE_TEST=1`; the SYNTHETIC feed), on a fresh database seeded by `seed` at 10:31 UTC: `reviews.spec.ts` `5 passed`, then `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` `15 passed`, then `scores.spec.ts` `4 passed`, then `checks.spec.ts` `1 failed, 1 passed, 1 did not run`: its costs test opened the trade's page by a click, after which a script's focus is not a keyboard's and the tooltip (which opens on keyboard focus) stayed closed; the test now opens the page by its address, and `checks.spec.ts` on the same database and servers gave `3 passed`. On a fresh database seeded by `flat`: `live.spec.ts` `4 passed`.
  - **Screenshots**, before (`main` at `7058d6c`, its own production build) and after, at 1440 and 390 px, light and dark, both against the same API on the seeded database (SYNTHETIC values); the comparisons are in the project's files (`redesign-part2/`), no page error printed.
  - `NOT RUN`: the Docker build of the web image and the update on the PC; a look at the pages on the PC's real data; Firefox and Safari; `foundation.spec.ts` and the older suites (as part 1). No independent review: no money path changed.
- 2026-10-31, part 2 merged on the owner's yes ("Yes, merge and install", 11:26 UTC): PR #154, `main` at `d630146`. **Installed** on the PC by the owner's double-click: `update-20261031T114342Z`, `COMPLETE` (11:43 to 12:09 UTC; the build waited for 12:05 UTC, outside the hourly bar's window; no migration, schema `0028_leaner_trader`; nine services on their new images; reconciliation `OK`; the pages answering; the agents' switch on; the futures feed `CONNECTED`; run #1 running, no open position), read from its record through the folder the owner shares. NOT RUN: a look at the new pages on the PC's real data.
- 2026-10-31, part 3 `IMPLEMENTED` as §4.13–§4.15 list, on the branch `claude/project-thread-9zpkc5` restarted from `main` at `d630146`, and `VERIFIED` in the cloud session (no Docker), commands as in [COMMANDS](../../COMMANDS.md):
  - **Web**, from `apps/web`: `pnpm typecheck` clean; `pnpm lint` clean (with `.output` removed first); Prettier run on the changed files only; `pnpm test` `45 passed` files, `383 passed` tests (`settings.test.tsx` new; `account-summary.test.tsx` removed with its component); `pnpm build` exit 0; `pnpm api:check` "Generated TypeScript API types match". `python3 tools/check_links.py .` 0 broken links.
  - **Engine**: unchanged (no file under `services/`), so its suites were not run again.
  - **Browser suites** (the preinstalled Chromium; the production build at `http://localhost:4318`; the API with `ASL_AGENTS_OFFLINE_TEST=1`, isolated where COMMANDS says; the SYNTHETIC feed), each on a fresh scratch database:
    - On a database seeded by `seed` at 11:35:54 UTC: `reviews.spec.ts` `5 passed`, then `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` `15 passed`, then `scores.spec.ts` `4 passed`, then `checks.spec.ts` `3 passed`. The first run, on a database seeded at 11:27:46 UTC, gave `5 passed`, then `1 failed, 3 did not run, 11 passed` (the Settings test picked the check's row by the text "Agents' check", which the switch row's line also holds; the rows are now picked by their exact titles), `4 passed`, `3 passed`.
    - `live.spec.ts` on a `flat` database: `4 passed`. `perp.spec.ts` on `tests.m7_browser_fixture seed` with the feed: `2 passed` (the strip, the 15m default, each interval in the address).
    - With the API isolated, on `asl_m1_browser_<run>`: `funding.spec.ts` `1 passed`, then the account suites (`request-envelope`, `account-recovery`, `foundation`) `4 passed`; on another, `funding.spec.ts`, `unknown.spec.ts`, `before-dispatch.spec.ts` and `pending.spec.ts` `1 passed` each, in that order.
    - `m7.spec.ts @profile` after the fixture's `new-runner`: `1 passed`; its first run failed on this fixture's check row ("No trading run": no futures run), and the test now reads "New entries" in the check's details. `m5.spec.ts` agents phase: `1 passed, 1 skipped` (the error phase's test); its first run failed on a row filter rooted at the list instead of the page.
    - With the API stopped: `m4.spec.ts` `1 passed, 1 skipped`, `m5.spec.ts` `1 passed, 1 skipped`, `execution.spec.ts` `1 passed, 2 skipped`, `foundation-error.spec.ts` `1 passed`, and `m7.spec.ts @error` `1 passed` after its Decisions line was changed to part 2's words ("Couldn't load the decisions"): it expected "Decisions unavailable" and had not been run for part 2.
  - **Screenshots**, before (`main` at `7058d6c`) and after, at 1440 and 390 px, light and dark, both production builds against a stand-in for the engine that answers the web's reads with SYNTHETIC values (a scratch script of the session, not in the repository); the comparisons are in the project's files (`redesign-part3/`).
  - `NOT RUN`: the skipped tests above (the retired pilot, `inactive` and `populated` phases, and each file's test for the other phase); the Docker build of the web image and the update on the PC; a look at the pages on the PC's real data; Firefox and Safari. No independent review: no money path changed; the switch and the run's buttons send the requests they sent before.
- 2026-10-31, part 3 merged on the owner's yes ("Yes", 13:18 UTC): PR #155, `main` at `5aa35ca`. **Installed** on the PC by the owner's double-click: `update-20261031T131908Z`, `COMPLETE` (13:19 to 13:23 UTC; no migration, schema `0028_leaner_trader`; nine services on their new images; reconciliation `OK`; the pages answering; the agents' switch on; the futures feed `CONNECTED`; run #1 running, no open position), read from its record through the folder the owner shares. NOT RUN: a look at Markets and Settings on the PC's real data. The five pages now all follow the owner's design.

