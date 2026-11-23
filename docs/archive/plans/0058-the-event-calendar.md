# ExecPlan 0058 — The event calendar

**Status: APPROVED by the owner on 2026-11-09, in the project thread "Add the event calendar to the trader": "yes do everything now" at 15:22:51 UTC, which moved the event calendar of the research thread "Research an event calendar for the trader" (2026-11-04) ahead of the paired reading of 2026-11-16 ([DECISIONS](../../DECISIONS.md#2026-11-09--the-event-calendar-execplan-0058)). The windows' ends were measured on 2026-11-04 before this plan (§2), and the measure of §4.6 is pre-registered by this plan, which ships with the code, before the first generation-19 decision.** A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)): the trader, generation 19, is generation 14's ([ExecPlan 0053](0053-the-trader-every-four-hours-and-on-events.md)) with a calendar of the three scheduled releases that move Bitcoin most, no new entry around each, and one more decision once each is out. It changes no money path, no limit, no protection and no policy.

Labels: `OBSERVED` (seen in records, code or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `CALCULATED` (the thread's arithmetic, assumptions stated), `NOT RUN`.

## 1. Goal

The research thread measured, on Binance's archive, what Bitcoin does around the US consumer price index (CPI), the US jobs report and the Fed's decisions (§2): it moves several times its normal range in the hour after, in a direction set by the surprise, and a position held through it is stopped out more often. The trader knows neither the surprise nor when the next release is. The owner asked for the calendar to be built now.

Observable outcome:
1. The trader (generation 19, `FUTURES_DECISION_V7`) cannot open a position from 240 minutes before a first-rank release to 45 minutes after the CPI, 30 after the jobs report and 120 after a Fed statement. An entry there is refused at the finish (`ENTRY_IN_EVENT_WINDOW`); `EXIT`, `TIGHTEN_STOP`, `HOLD` and `ABSTAIN` stay open, and an open position keeps its stop, take profit, time exit and liquidation price.
2. Once a window ends, the trader decides once more (`RELEASE_OUT`), at the first finished 15-minute bar at or after the end, up to an hour late, unless a decision started at or after the end already covers it. Every other moment of generation 14 (every four hours, a closed trade, a big move, a range break, a funding jump) is unchanged.
3. The trader is told: the context's `events` block (the window in force, the next and the last release), two rows of its `limits`, and its prompt's section "Around scheduled releases".
4. Home says when entries are closed and until when; Settings' limits show the next window; the model card says the trader also decides after each big scheduled release.
5. A calendar that cannot be read closes entries (`CALENDAR_UNREAD`) and stops no decision.

## 2. What the app has

`VERIFIED` on `main` at `a5f5ecc`:
- Generation 14's trader `FUTURES_DECISION_V6` decides on `SCHEDULE_V1` ([0053 §4.1](0053-the-trader-every-four-hours-and-on-events.md#41-the-schedule-schedule_v1-code-in-templates_v14)); its moments come from stored records alone (`app.agents.futures_schedule`). Its finish checks refuse an entry while a position is open, in the policy's cooldown, without the agents' check, or outside generation 10's four rules (stop 2 or 3 × ATR, time exit 4, 12 or 24 hours).
- The app stores the BLS release calendar (`CALENDAR_BLS_V1`, [ExecPlan 0032](0032-m9-news-and-events-the-agents-trade-on.md)) as evidence items with the publisher's start in UTC, and shows its scheduled releases in the trader's `releases` block. Nothing in the app knows the Fed's meetings; the Fed's monetary policy feed carries statements after they are out.
- `futures_decisions.trigger` and `futures_decision_scores.trigger` are `varchar(12)` with checks of `BAR`, `FILL`, `SHARP_MOVE` and generation 14's five kinds; the decision guard of `0033` accepts generations 7 to 11's and 14's traders.

`OBSERVED` on the owner's PC on 2026-11-04 at 08:45 UTC (read-only, [the research files](#14-progress)): the stored calendar held 26 events to 2026-12-18; among them "Consumer Price Index" on 2026-11-10 and 2026-12-10 and "Employment Situation" on 2026-11-06 and 2026-12-04, each at 13:30 UTC (08:30 Eastern).

`CALCULATED` by the research thread on 2026-11-04 (Binance's BTCUSDT perpetual 1-minute candles, 2022-01 to 2026-10, [BT-02](../contracts/REFERENCES.md#backtest-data--2026-11-03); 57 CPI and 57 jobs-report dates from the BLS archive, 39 Fed statements from the Fed's calendar (one, 2026-10-28, missing from the archive's month); each event against matched non-event days at the same time of day; modeled fills at 5 bp a side and 1 bp of slippage, not fills; [EC-01](../contracts/REFERENCES.md#event-calendar--2026-11-04-and-2026-11-09)):

| | CPI | Jobs report | Fed statement |
|---|---|---|---|
| Range in the 60 minutes after, median against matched days | 2.70× | 1.94× | 3.43× |
| Range in the 60 minutes before | 1.26× | 0.91× | 1.55× |
| An entry at the 4-hour mark before the release, either side, 2 × ATR stop, 4-hour time exit: stopped out (event against matched) | 77% against 67% | 78% against 67% | 70% against 39% |
| The same entry's net R, either side (paired difference, 95% interval) | +0.09 (−0.28 to +0.50) | −0.26 (−0.52 to +0.02) | −0.29 (−0.60 to +0.05) |
| Minutes after until the median 15-minute volatility stays under 1.5× matched days (the study's rule, capped at 120) | 45 | 30 | 165, so 120 |

The windows close 1.80% of all hours, and 93 of the 2,052 moves of 4 × ATR since a 4-hour boundary (4.5%) fall inside one. The stop-out rates differ beyond chance at each event; the net results do not (each interval crosses zero), so the window is a risk rule against a move whose sign nobody here knows, not a claim of profit.

## 3. Scope

In: generation 19's definitions (`definitions_v19.py`) and prompt (`trader.v7.md`); the calendar (`app.agents.event_calendar`) and its BLS read (`app.sources.evidence.calendar_titled`); the finish rule and its second look; the scheduler's `RELEASE_OUT`; migration `0039`; the overview's `schedule.calendar` and the runtime read's `budgets_v19`; Home's trader card, Settings' limits and model card, the decision label; tests; the contracts.

Out: the policy and its limits; forced exits before a release (§13); the second-rank releases (PPI, jobless claims and the rest stay in `releases` without a window); unscheduled news; the coach, the reviewers, the veto, the replay, the twins and the backtests, which keep their generations; the rest of the bundle after the 2026-11-16 reading.

## 4. Design

### 4.1 The calendar `EVENT_CALENDAR_V1` (code, in `TEMPLATES_V19`)

- **CPI and the jobs report:** the stored BLS calendar, titled exactly "Consumer Price Index" and "Employment Situation", each event's newest revision available by the cutoff, a cancelled one (`STATUS:CANCELLED`) left out, so a moved release moves its window. Read from 12 hours before the cutoff to 60 days after, through the calendar sources in force as `scheduled_releases` reads them.
- **The Fed:** a table of statement times in the code, each the second day of a meeting at 14:00 New York time in UTC (a test converts each with the IANA zone America/New_York): 2026-12-09, the eight 2027 meetings and 2028-01-26, read on 2026-11-09 from the Fed's calendar page, whose dates are "tentative until confirmed at the meeting immediately preceding it" ([EC-02](../contracts/REFERENCES.md#event-calendar--2026-11-04-and-2026-11-09)). Settings shows how far the table reaches; an update adds dates.
- **What it is not:** a forecast, a result or a consensus. It holds the publishers' times only, labeled so in the context.

### 4.2 The window `EVENT_WINDOW_V1`

From 240 minutes before a release (the shortest time exit an entry may take, so an entry made inside it would still be open at the release) to 45 minutes after the CPI, 30 after the jobs report and 120 after a Fed statement (§2's measured ends, the Fed's capped at 120 by the study's rule). The start is inside, the end is not; windows that touch or overlap are joined, and the one that ends last names the closure.

- **The finish rule:** generation 19's finish refuses an entry (`ENTRY_IN_EVENT_WINDOW`) when its bound context's `limits.entries_closed_for` is set; the retry is told why and records a `HOLD`. A second look at the finish reads the calendar again at the database's time, so a window that opened, or a release the publisher moved, after the context was built still refuses the entry.
- **Fail closed:** a calendar the database cannot read (`read_or_none`, inside a savepoint) closes entries with `CALENDAR_UNREAD`; the decision itself still runs, and exits never wait.
- **Always open:** `EXIT`, `TIGHTEN_STOP`, `HOLD`, `ABSTAIN`; the engine's stop, take profit, time exit and liquidation every second.

### 4.3 The look after a release `SCHEDULE_V2`

`SCHEDULE_V1` with one kind added: `RELEASE_OUT` is due at a finished bar's close at or after a window's end, up to 3,600 s late, while no decision started at or after that end. Its facts (`release`: the event, its name, the release time, the window's end, the lateness and the BLS item's ID) ride on the trigger. In the naming order it comes third, after `BAR_4H` and `TRADE_CLOSED` and before `MOVE`, `RANGE_BREAK` and `FUNDING_JUMP`; the others due are listed in `also`, and the key is `schedule-v2:<the bar's close>`. Without a readable calendar `RELEASE_OUT` is not due and every other moment still is. The schedule's 32 a day and the policy's 120 stay; `CALCULATED`, about 2.6 windows a month (153 in 58 months), many ending at a moment already due.

### 4.4 What the trader is told

`trader.v7.md` is `trader.v6.md` with five lines changed and three added (`VERIFIED` by a test of the diff): the title; `RELEASE_OUT` among the triggers; the `events` block; `entries_closed_until` and `entries_closed_for` in `limits`; the section "Around scheduled releases" (what the three releases do, the window, an entry refused inside it while exits stay open, and the one more decision after it, where a headline may already carry the number: read it as data and enter only on the usual rules); "Flat" holds when `entries_closed_for` is set; and the one-position rule names a release's window. Every rule line, the 1-hour call, the reads, the budgets and the other finish checks are generation 14's.

The context's `events` block (`event_calendar.shown`): `id`, `label`, `before_minutes`, `after_minutes`, `entries_closed_until` and `closed_for` while a window is open, `next` (its time, minutes to go, and when its window opens and ends) and `last` (within 12 hours, minutes ago); when unread, `omitted: READ_FAILED`. A full context with it fits the prompt limit with 12,307 bytes to spare (53,229 of 65,536, `VERIFIED` by a test at the snapshot's whole 36 KiB; generation 14's 51,972).

### 4.5 The pages and the API

- Home's trader card: while a window is open, "No new entries until 15:15" with "US CPI at 14:30. Exits, tighter stops and holds stay open." (times in the viewer's zone); when the calendar cannot be read, "No new entries for now".
- Settings: the limits' "Release windows" tile, the next release and its window, "Entries closed" while one is open, or the reason it cannot be read; the model card's trader "Every 4 hours, at once on a big move, and after each big scheduled release".
- Decisions labels the kind "After a release".
- The API: the futures overview's `schedule.calendar` (`calendar`, `readable`, `before_minutes`, `after_minutes`, `fed_dates_until`, `entries_closed_until`, `closed_for`, `next` with up to three releases) and `RELEASE_OUT` among `schedule.events`; the runtime read's `budgets_v19`.

The shadcn skill was loaded and the project discovered before the edits; the card reuses the project's `Alert` and Settings its own `Tile`; no component was added and preset `b2fms61Bqi` is kept ([INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0058-the-event-calendar--2026-11-09)).

### 4.6 The measure, pre-registered

The window's own effect cannot be read live in any useful time: about 2.6 windows a month, and the archive measure of §2 is its evidence. So the measures are the trader's, as 0053's, plus the calendar's operation.

**O1, the operational check** (read-only on the PC, at the install check and after the first windows): every first-rank release after the install has its window (no generation-19 entry filled inside one, `OBSERVED` from the fills against the calendar; a miss is a bug, fixed forward or §11's rollback); each window's end has a `RELEASE_OUT` decision within the hour after, or another decision started at or after it; refused entries counted (`ENTRY_IN_EVENT_WINDOW` steps); on each whole UTC day with the run `RUNNING`, between 4 and 16 decisions as 0053's O1; no `CALENDAR_UNREAD` outside a database fault. The first windows after the install (`OBSERVED` in the stored calendar on 2026-11-04, read again at the install): the CPI of 2026-11-10 (09:30 to 14:15 UTC), the jobs report of 2026-12-04 (09:30 to 14:00 UTC), the Fed of 2026-12-09 (15:00 to 21:00 UTC), the CPI of 2026-12-10.

**M1, the primary measure** (the trial ledger counts one more): [0053 §4.5](0053-the-trader-every-four-hours-and-on-events.md#45-the-measure-pre-registered)'s M1 on generation 19's decisions (purpose `DECISION`, never the agents' check), in time order: the mean of the paired differences at 60 minutes (the trader's score minus the last-hour rule's), a stationary bootstrap interval (`app.evaluation.bootstrap.interval`, mean block 2 decisions, 10,000 resamples, seed `derive_seed("SCHEDULE_V2", "M1")`) at 95% and at 99.444% (1 − 0.05/9: Bonferroni for the nine variants of §4.7). Read once 120 of generation 19's decisions are decisive at 1 hour (beyond the 0.12% band): about 3 to 4 weeks after the install. **Verdict:** `PASS` when the 99.444% interval's lower end is above 0; `WORSE` when the 95% interval's upper end is below 0; otherwise `NO_DIFFERENCE`. Read-only on the PC, on the owner's "Go"; nothing changes by itself from a verdict, as in 0053.

**Secondary**, 95% intervals, never a verdict:
- S1 to S6 as [0053 §4.5](0053-the-trader-every-four-hours-and-on-events.md#45-the-measure-pre-registered), on generation 19's decisions, with `RELEASE_OUT` as one more kind in S3 and S5.
- S7, pooled: generations 14 and 19 together (the same prompt but for the calendar, which closes 1.8% of hours), the same paired score at 1 hour, labeled as two trials pooled. It reads sooner and is descriptive only.
- S8, the windows: the decisions inside windows and after them (`RELEASE_OUT`), their calls' paired score at 1 hour, and the refused entries; too few for a year.
- Descriptive only: generation 14's M1 over its whole run, 2026-11-03 15:28 UTC to the install, as 0053 computes it; it ends short of its sample.

### 4.7 The trading review (TRADING.md's eight questions)

1. **Rules:** paper only; the window only refuses (an entry), so it is tighter than `FUTURES_POLICY_V1`, never looser; code keeps every exit, size and limit; the calendar reads stored records and a code-owned table; nothing a model returns reaches it (`VERIFIED` by §6's tests). Passes.
2. **Class:** a new generation: the trader sees the `events` block, a changed prompt, and one more moment. It ends generation 14's run at the install, so 0053's M1 is read descriptively over its days (§4.6); the 2026-11-16 reading of generation 11 is not affected.
3. **Costs:** no trade's fees, slippage or funding change. Fewer entries around releases mean fewer of the stop-outs that §2 measured; about 2.6 more decisions a month at most, and one more model step when a refused entry is retried.
4. **Horizon:** the 4- to 24-hour holds are where the release's move lands: 240 minutes is the shortest of them. The 1-hour call is unchanged, the known weakness of principle 4.
5. **The model's place:** the calendar is code's; the model is told it and cannot open around a release. A prompt adds no information on a surprise, and none is claimed.
6. **The yardstick:** the last-hour rule at 1 hour on the same decisions (M1); the windows' evidence is the archive's paired event study (§2), stop-outs against matched days; "too few" for any live reading of the windows (S8).
7. **Pre-registration and the trial ledger:** §4.6, in this plan before the first decision; the window's ends were measured before the plan and are not tuned on any live result. The ledger: generation 19 is the ninth variant of the trader (generations 7 to 11 live, the replay's `NO_FEEDBACK` and `CALL_4H`, generation 14, generation 19), so M1's `PASS` is deflated by nine; the backtests' arms count in their own plans.
8. **The clock and the cost:** M1 restarts and reads in about 3 to 4 weeks; S7 pools sooner. Calls: about the same as generation 14's 8 to 9 a day.

## 5. Authority

No permission, tool, limit or grant changes. Generation 19's role grants are generation 14's (the `COORDINATOR`'s two reads and `record_futures_decision`); its finish checks are generation 14's plus one that only refuses; the database holds its rows to generation 10's rules (migration `0039`'s guard). The calendar and the window are code's, hashed in the template; no model can change them or when it is called. [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) record generation 19.

Rule 13's money-path review: no money path changes (no ledger, journal, reservation, account, engine or risk-gate code; the engine answers a generation-19 decision exactly as a generation-14 one), so the independent review is not required.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| K1 | A window runs from 240 minutes before to its event's end, start in and end out; windows that touch or overlap are joined | `tests/test_m11_event_calendar.py`, unit tests |
| K2 | `RELEASE_OUT` is due at the first bar at or after a window's end, up to an hour late, until covered; generation 14's moments unchanged around it, in `KINDS` order; not due without a readable calendar | Unit tests; a database test of the scheduler |
| K3 | The context's `events` block and `limits`' two rows; an unread calendar says so and closes entries | Unit test; database tests |
| K4 | An entry is refused while entries are closed, by the bound context and by the second look at the finish; exits, tightening, holds and abstentions are not; generation 14 is not held to it | Unit test; database tests (each fails when its own check is removed, `VERIFIED` by a mutation run on 2026-11-09) |
| K5 | The Fed table is 14:00 New York time on each date, in order, to 2028-01-26 | Unit test |
| K6 | Generation 19 is generation 14 but its prompt, schedule, added finish rule and `replaces`; the same budgets, caps and quiet-window exemption; the prompt differs where §4.4 says; a full context fits with 12 KiB to spare | Unit tests |
| K7 | Migration `0039` froze generation 19's documents; the two trigger checks gain `RELEASE_OUT`; the guard gains `FUTURES_DECISION_V7` and nothing else; the database holds a V7 row to generation 10's rules; the downgrade refuses once a generation-19 workflow, profile or `RELEASE_OUT` decision exists, then restores `0033`'s guard and checks exactly | Unit and database tests; migration test |
| K8 | The BLS read: each event's newest revision by the cutoff, exact titles, a cancelled one left out, a moved one at its new time | Database test |
| K9 | The overview's calendar; Home's card, Settings' tile and model card, the decision label | API test; Vitest; the browser suite `pages.spec.ts` |
| K10 | Generation 14's schedule still runs when the scheduler names its trader (§11's rollback path) | `tests/test_m11_event_trader.py`'s scheduler tests, naming generation 14 |
| K11 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host or data source: the BLS calendar is the app's stored `CALENDAR_BLS_V1` ([M9U1-02](../contracts/REFERENCES.md#m9-update-1-feeds-and-terms--2026-10-19)). The Fed's dates and statement time were read on 2026-11-09 from the Fed's own pages (EC-02). The measurement is the research thread's (EC-01) on Binance's public archive (BT-02).

## 8. Data and trust boundaries

- No new host, secret, volume or network path; the Fed table is code.
- New stored data: generation 19's workflows and decisions, `RELEASE_OUT` rows and their `release` facts, the context's `events` block; kept in every backup.
- The calendar reads only the calendar evidence the agent identity can read, as of the cutoff; nothing a model returns reaches it.

## 9. Implementation sequence

1. This plan, with the code, migration `0039`, the tests and the contracts, in one pull request (§14).
2. Merged by the thread on `main` once its checks pass; the owner's double-click of `update-app.cmd`.
3. The install check, read-only on the PC: the profile and the agents' check on `FUTURES_DECISION_V7` (SC-03); the stored calendar's next CPI and jobs report; Settings' tile; the first generation-19 decisions.
4. O1 after the first window (the CPI of 2026-11-10 if the update is in by 09:30 UTC that day), read-only.
5. M1 once its sample is reached, on the owner's "Go".

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL (the new suite, the M11 agent suites, those that name the newest generation or the migration head, and the whole engine suite), the web checks (lint, types, Prettier, Vitest, build, `api:check`), the browser chain, and the link check, with results in §14. `NOT RUN` in the cloud and done by the update or its check on the PC: the Docker build, the update, the agents' check against the real model, real generation-19 decisions and windows.

## 11. Failure and rollback

- The calendar cannot be read: entries closed (`CALENDAR_UNREAD`) until it can; Home and Settings say so; every other moment runs.
- The BLS source is not in force, or its calendar lacks a release: only the Fed's windows apply, and Settings' tile shows which release is next, so a missing CPI is visible there (a known gap: no alarm).
- A Fed meeting moves, or the table runs out (after 2028-01-26): an update changes the table; an unscheduled meeting has no window.
- The trader does worse: M1's `WORSE`, a card for the owner.
- **Rollback:** an update that names generation 14's trader in `futures_trader.FuturesGraph.futures_trader` and `futures.views.SCHEDULE` again; generation 14's schedule (`futures_schedule.due`) is kept for it, and K10 tests it. `0039`'s downgrade refuses once generation 19 has left a workflow, a profile or a `RELEASE_OUT` decision, as `0033`'s does: a rollback goes forward with an update.

Known gaps, stated and not fixed here:
- ExecPlan 0056's backtest ran generation 14's design; its design guard now names the difference (the calendar's parts). A backtest of generation 19's design is its own plan, on the owner's word.
- The coach's and the reviewers' prompts do not mention the windows; a held entry reads to them as any `HOLD` with `LIMIT_OR_COOLDOWN`.

## 12. Q01–Q10

Q01, Q02: Home's card, Settings' tile and model card, the decision label; no new page (K9). Q03: K1 to K10. Q04: no new secret or host (§8). Q05: §11. Q06: the calendar is read once per scheduler pass and per decision (one indexed query, inside a savepoint), and the context gains under 1 KiB. Q07: the cloud suites (§14). Q08: each refusal's reason in the step; `agent_event_calendar_unread` in the worker's log; the `release` facts on the trigger. Q09: migration `0039` and its downgrade (K7); the update's backup. Q10: the contracts of §5 and the data contract; no new dependency.

## 13. Decision log

2026-11-09, by the thread under the owner's words of the status line and "decide for me" (2026-10-19), each the recommended engineering choice:
- **Three events only** (the CPI, the jobs report, the Fed): the research measured them as first rank; PPI and the rest stay as before.
- **240 minutes before:** the shortest time exit, so any entry made in the window would still be open at the release.
- **45, 30 and 120 after:** §2's measured calm by the study's rule, written before it ran, which caps the Fed's 165 at 120.
- **No forced exit:** a position keeps its stop and time exit, and the trader may exit or tighten; a forced exit would be a new rule with its own fee and its own trial.
- **Fail closed** on an unread calendar, for entries only.
- **A second look at the finish,** since a release can move between the context and the answer.
- **The Fed in a table, not a feed:** the feed reports statements after they are out; the calendar page gives the dates ahead.
- **One more decision after a window,** not a new agent; it comes third in the naming order so a 4-hour decision or a closed trade still names a bar they share.
- **The kind fits the column:** `RELEASE_OUT` (11 characters).
- **Live at the install,** ending generation 14's run: the owner's "do everything now".

## 14. Progress

- 2026-11-04: the research thread's measurement (`CALCULATED`, §2) and the read of the stored BLS calendar (`OBSERVED`); the files are in the project's files, `event-calendar/`, and the archive on the PC in `.cache\backtest-data`.
- 2026-11-09 15:22:51 UTC: the owner's "yes do everything now" (APPROVED).
- 2026-11-09, IMPLEMENTED on `claude/project-thread-lue0wk`, from `main` at `a5f5ecc`: §4.1 to §4.5, migration `0039` (revising `0038_slow_trend`), the contracts of §5, and the tests of K1 to K10 (`tests/test_m11_event_calendar.py`, 18 tests; the older tests that name the newest generation or the migration head; the web's Vitest files and `pages.spec.ts`).
- 2026-11-09, VERIFIED in the cloud on that tree ([COMMANDS](../COMMANDS.md#execplan-0058-the-event-calendars-tests-and-install-check)): Ruff `All checks passed!`; the OpenAPI drift check and the web's `api:check` match; the link check finds none broken; `tests/test_m11_event_calendar.py` `18 passed` on a fresh database, and each of the finish's two checks, removed in turn, failed the database tests (a mutation run, then restored); the web's typecheck, lint and Prettier clean, Vitest `47` files and `404 passed`, the build passes; the browser chain on a database seeded at 16:14:43 UTC, `5 passed` (`reviews.spec.ts`), `16 passed` (`local-time.spec.ts`, `pages.spec.ts`, `twins.spec.ts`), `4 passed` (`scores.spec.ts`), `3 passed` (`checks.spec.ts`), and after the trader card's wording changed `16 passed` again on a database seeded at 16:19:34 UTC. The 27 trader, generation, migration-head and backtest suites on a fresh database of the second cluster (port 55453), alone on it: `3 failed, 532 passed` (11:32), the three `test_m11_scores_db.py` failures of `main`'s baseline. An earlier run of the same suites was disturbed by a second suite started on the same cluster (the fixtures switch the identities' login, as [COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud) says) and is not counted; before the disturbance it had found the two older tests that name the newest generation's guard message and model card (`test_m11_event_trader.py`, `test_agent_models.py`), updated to generation 19.
- 2026-11-09, VERIFIED: the whole engine suite on a fresh database of the second cluster, on `788b1de`: `6 failed, 2323 passed, 74 errors` (57:14). The 74 errors and five failures are the known baseline of [COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud) (`test_api.py`'s status test, `test_m6_schema.py`'s downgrade, `test_m11_scores_db.py`'s three); the sixth, `test_m11_slow_trend_db.py`'s downgrade test, still expected `0038` as the head, and since `1724a7f` it steps down `0039` first: the two slow trend suites `45 passed` on a fresh database of the first cluster. The failed files of an earlier whole run (`16 failed, 2295 passed, 74 errors`, 1:03:05, started before the prompt's last trim, so its database held the earlier seed lines and its test modules were the earlier ones), rerun on a fresh database of the first cluster: `6 failed, 187 passed`, the same six.
- 2026-11-10: on the owner's words of 15:08 UTC ("can everything stop … and update the app to latest changes", "I don't want to wait until everything completes november 15"), this update is installed together with [ExecPlan 0059](0059-the-slow-rule-trades-the-main-account.md) in one update, never on its own. Under 0059's `FUTURES_POLICY_V2` the scheduler starts no trader decision, so generation 19 decides nothing live: only the agents' check asks its trader its probe (no decision is written). §4.6's measure therefore gets no days and is closed unread, not "too few" against a sample; the calendar's code, its template and migration `0039` stay installed for a rollback to a trader ([0059 §13](0059-the-slow-rule-trades-the-main-account.md#13-decision-log)).
- 2026-11-10, installed with 0059 by the owner's double-click (the update of 17:24 to 17:30 UTC, `COMPLETE` on `93a2112`; OBSERVED read-only at 17:31 UTC in a Remote Control session): migration `0039` with `0040`. The newest `FUTURES_DECISION_V7` workflow is of 17:29:02 UTC, after the agent worker started on its new image and before the switch at 17:30:01 UTC; by the code, the agents' check's `SC-03` probe, which writes no decision (its purpose not read). No generation-19 decision was answered live: the rule decides since 17:30:01 UTC.
