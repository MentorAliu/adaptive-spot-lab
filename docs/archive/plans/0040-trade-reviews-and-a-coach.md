# ExecPlan 0040 — An AI review of every trade, and a coach for the trader

**Status: APPROVED by the owner on 2026-10-24 at 09:17 UTC ([DECISIONS](../../DECISIONS.md#2026-10-24--an-ai-review-of-every-trade-and-a-coach-execplan-0040)): "Build it as proposed". Part 0 (this plan) done. Part 1 IMPLEMENTED on 2026-10-25 and checked in the cloud (§14); it is installed after [ExecPlan 0042](0042-no-owner-sign-in.md) (no sign-in), whose migration `0021` comes first, so part 1's is `0022` (§13). Installed on the owner's PC on 2026-10-25 (`6dc1026`), and the first three closed trades were reviewed there on 2026-10-27 (§14).** Written by the project thread "Add AI review of every trade" from `main` at `a90251a`. A part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)), built after its update 2: two agent templates, a record code builds for each closed trade, a change to the trader's template, and the pages. It changes no money path, limit or protection.

Labels: `OBSERVED`, `REPORTED` (by another project thread, not yet on `main`), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`. Every number in §4 is a `PROPOSED` engineering default.

## 1. Goal

The owner, 2026-10-24 08:41 UTC, in the project thread "Add AI review of every trade": "Also I want the app to have functionality that when trading, an ai agent analyzes each trade and circumstances, analyzes the factors that happened during that trade (external or internal) and write a summary or whats best possible way or format to save it in the database or as a log that somewhere, so then another agent can read those trades and suggest next trade to the agent that handles trades, feel free to be creative and suggest ideas and lets make sure you understand my requirements that im asking here"

The thread restated the ask and proposed this design in a Claude Doc, "Trade review and coach: proposal"; the owner picked "Build it as proposed" at 09:17 UTC. Asked at 09:17 UTC "How will this help with trading?", the thread answered: the trader remembers why trades won or lost, skill is told apart from luck, and each decision gets one clear tip; it is no guarantee of profit, and the app measures whether following the advice does better (§4.5).

Observable outcome:
1. For each closed futures position, code stores a **fact sheet**: the trade's numbers and what surrounded it, inside and outside the app.
2. A **reviewer** (EVALUATOR) reads it and records a review: the decision graded apart from the result, the factors, tags from a fixed list, whether the entry reason held, and one lesson. The Trades page shows it with the trade.
3. A **coach** (ANALYST) reads the recent reviews and code's scoreboard and records an advice note for the next trade, valid for up to 4 hours. Home shows it.
4. The trader reads the newest note at each decision and says whether it followed it. Code compares the trades that followed the advice with those that ignored it, and Home shows both.
5. Neither new agent can trade, change a rule or hold the trader back. Trading, protection and limits work as before while they are down.

## 2. What the app has

`OBSERVED` at `a90251a` (the five-coin spot app, which M11's update 2 replaces):
- **Outcome reviews.** For each closed position of a policy run the worker stores one outcome record with its hash (`decision_outcomes`), and SYSTEM queues one `OUTCOME_REVIEW_V2` (EVALUATOR, at most 8 a day), recorded through `record_review` as its FINISH ([AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md)). A decision is shown the four newest outcome reviews (`OUTCOME_REVIEWS_SHOWN` in `app/agents/decisions.py`). ExecPlan 0039 §5.5 drops them with eight of the nine agents.
- **The runtime.** One inference slot for all roles, with a code-owned priority; a refused output (`REJECTED_OUTPUT`) gets one retry ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md)). The runner cancels a running call on `POST /v1/jobs/{call_key}/cancel`, which the orchestrator uses for an owner's cancel and an epoch change (`app/agents/orchestrator.py`). `MODEL_TABLE_V1` gives the EVALUATOR high effort and the ANALYST medium (`app/agents/model_table.py`).
- **Roles.** [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md) already lets an EVALUATOR critique an artifact and an ANALYST record an assessment with no financial effect; neither may draft or submit a trade.

`REPORTED` by the thread "Bitcoin futures app plan" on 2026-10-24 at 08:51 UTC, not yet on `main`: update 2 part A (migration `0019`) stores `perp_bars` (1-minute candles, kept), `perp_quotes` (a 5-level book each second) and `perp_marks` (each second), both kept 7 days, `perp_funding_rates`, and the feed's state and events. Part B (migration `0020`) adds the futures account, positions, orders, fills and funding payments, and generation 7 with one trader template, `FUTURES_DECISION_V1`. The trader's context already holds the last 10 trades' results (0039 §5.5). Part 1 reads part B's code before building on it; where that code differs from this plan, the code governs and §13 records the change.

## 3. Scope

In: the fact sheet, the reviewer, the coach, the scoreboard, the trader's new decision fields, the pages; migration `0022` (planned as `0021`); generation 8. Not built: `FUTURES_POLICY_V2` (§13).

Out, each for later on the owner's word (the proposal's other ideas): trade replay on the chart; open interest, the long/short ratio and other traders' liquidations as outside factors; a daily review of the largest move the trader sat out; a daily journal on Home; recurring lessons offered to the owner as rules. No new data source, host, dependency or secret.

## 4. Design

### 4.1 The fact sheet (code)

For each futures position that closes, the worker's next pass stores one fact sheet with its hash in `trade_fact_sheets` (one per position; `canonical`, `document`, `sha256`, as `decision_outcomes` does), built only from stored rows, at most 8 KiB:
- **The trade:** side, leverage, the entry and exit fills (time, price, quantity), what ended it (stop, take-profit, time exit, liquidation, the trader's exit), fees, funding, realized P&L, and R: realized P&L after fees and funding divided by the risk the risk gate sized at the stop. The worst and best price between entry and exit, from the 1-minute bars, in price and in R. Hold time.
- **Outside the app:** the trend, ATR and volume features the trader's context uses (0039 §5.5), at entry and at exit; the spread and the mark-to-index gap at both; the funding rate and any funding time crossed; the headlines and scheduled releases of the collected feeds between entry and exit (at most 10, titles only, labeled as external text).
- **Inside the app:** the entry decision's reason, confidence and invalidation line (§4.4) and the decisions during the trade (time, action, reason); the time from bar close to decision start and from decision start to fill; each fill's slippage against its quote; feed gaps and reconnects, refused submissions, model calls refused for the usage limit, and latches and pauses during the trade.

Each value names its source (`FILL`, `FEATURE`, `FEED_ITEM`, `EVENT`, `MODEL_AUTHORED`). Nothing is estimated.

### 4.2 The reviewer: `TRADE_REVIEW_V1` (EVALUATOR)

- **Started by** SYSTEM, one per fact sheet, oldest first, at most 24 a UTC day. A fact sheet still unreviewed after 48 hours is marked `NOT_REVIEWED`.
- **Shown:** the fact sheet, the policy's summary and the tag list `TRADE_TAGS_V1`. No tools.
- **Answers** with its FINISH, a `TRADE_REVIEW` artifact: one model step, and one retry after a refusal.

| Field | Values |
|---|---|
| `target` | The fact sheet's ID and hash |
| `decision_quality` | `GOOD`, `OK`, `POOR` |
| `entry_reason_held` | `YES`, `PARTLY`, `NO`, and one line (at most 200 characters) |
| `invalidation_seen` | `YES`, `NO`, `NOT_STATED` |
| `factors` | 1 to 6, each with `where` (`INSIDE`, `OUTSIDE`), a tag, `effect` (`HELPED`, `HURT`, `NEUTRAL`), `evidence` (1 to 3 fact-sheet paths or feed-item IDs) and a note of at most 160 characters |
| `tags` | 1 to 5 from `TRADE_TAGS_V1` |
| `lesson` | One sentence, at most 200 characters |

- **Code checks** the schema (an unknown field is refused), the target, each evidence path against the fact sheet and each tag against the list. Code, not the model, places the trade in the grid, from `decision_quality` and the result (R above +0.1 a win, below −0.1 a loss, otherwise flat): good call and won, good call but unlucky, poor call but lucky, or a mistake. The pages show only the fact sheet's numbers; the review's words are shown as the model's.
- `TRADE_TAGS_V1`: outside, `WITH_TREND`, `AGAINST_TREND`, `RANGE_CHOP`, `VOLATILITY_SPIKE`, `NEWS_OR_RELEASE`, `FUNDING_COST`, `THIN_MARKET`; inside, `LATE_ENTRY`, `SLIPPAGE`, `STOP_TOO_TIGHT`, `STOP_TOO_WIDE`, `TARGET_TOO_FAR`, `EXIT_TOO_EARLY`, `HELD_TOO_LONG`, `DATA_PROBLEM`, `AGENT_UNAVAILABLE`, `GOOD_EXECUTION`.

### 4.3 The coach: `TRADE_COACH_V1` (ANALYST)

- **Started by** SYSTEM after each new review, one at a time, at most 24 a UTC day.
- **Shown:** the last 20 reviews (the grid, tags and lesson, with the trade's side, leverage, stop and R), the scoreboard of §4.5 as of its start, stored with the note by its hash, and the policy's sets. No tools.
- **Answers** with its FINISH, a `TRADE_ADVICE` artifact:

| Field | Values |
|---|---|
| `lean` | `LONG`, `SHORT`, `EITHER`, `SIT_OUT` |
| `setup` | `when`, at most 240 characters in the features the trader sees; optional `stop_atr_multiple`, `take_profit_multiple`, `leverage` and `max_hold_hours`, each from the policy's sets |
| `avoid` | 0 to 3 lines of at most 160 characters |
| `evidence` | 1 to 6 review IDs or scoreboard row keys from its context |
| `confidence` | `LOW`, `MEDIUM`, `HIGH` |

- **Code** refuses a value outside the policy's sets and a reference outside the context, adds each cited row's counts so no count is the model's, holds `confidence` at `LOW` while fewer than 10 trades are reviewed, and sets the expiry: 4 hours, or the next note.

### 4.4 The trader: `FUTURES_DECISION_V2` (generation 8)

Generation 7's trader with three changes. As planned, `FUTURES_POLICY_V2` would have kept every value of `FUTURES_POLICY_V1` and bound generation 8; as built, the run stays on `FUTURES_POLICY_V1`, which names no agent template (§13).
1. **Shown:** the newest unexpired note, labeled `MODEL_AUTHORED_ADVICE_NOT_A_RULE`, with code's counts; and with each of the last 10 trades, its grid, tags and lesson.
2. **Answers** `advice_use` (`FOLLOWED`, `PARTLY`, `IGNORED`, `NO_ADVICE`) and one line why, at every decision.
3. **With an entry:** `confidence` (`LOW`, `MEDIUM`, `HIGH`) and `invalidation`, one line of at most 160 characters on what would prove the trade wrong. If generation 7 already has a confidence, it is kept, not doubled.

Nothing else changes: the risk gate sizes and checks every order as before, and a note is never an order.

### 4.5 The scoreboard (code)

Computed from the fact sheets and reviews, in exact Decimal: for each row key, the count, wins, losses, flats, average R and net P&L, over the last 7 days and over all. Row keys: side; the 1-hour trend at entry; leverage; stop multiple; what ended the trade; each tag; the UTC hours 00–08, 08–16 and 16–24; and `advice_use`. A row of fewer than 5 trades is labeled as too few. The followed and ignored rows measure outcome 4 of §1; Home shows them with their counts and draws no conclusion while either has fewer than 20 trades.

### 4.6 When they run, and what they cost

- **The slot goes to the trader first.** A review or note starts only when no decision is queued or open and it can end (its 300-second deadline plus 60 seconds) before the next 15-minute bar closes. When a decision is queued while one runs, the worker cancels the call at the runner and queues it again, at most twice.
- **Calls:** at most 24 reviews and 24 notes a UTC day, each one model step with no tools: at most 48 calls a day (96 with every retry), beside the trader's up to 120 decisions (0039 §5.4). Fewer trades, fewer calls.
- **The usage limit or a stopped runner:** reviews and notes wait; the fact sheet is fixed at the close; once the note expires the trader decides without one. Code's protection never waits for either.
- **The model:** `MODEL_TABLE_V1`'s EVALUATOR and ANALYST pairs, as the outcome review and the brief used; the first days on the PC record each call's time (Q06).

### 4.7 The pages

UI work loads the shadcn skill, keeps preset `b2fms61Bqi` and reuses the preset's components; no new dependency.
- **Trades:** each closed trade shows its review: the grid as a badge, the tags, the lesson, and the factors with their evidence on demand. A pending, failed or `NOT_REVIEWED` review says so.
- **Home:** the coach's note (lean, setup, avoid, confidence, expiry, the cited rows with their counts) and the followed and ignored rows (count and average R, 7 days and all).
- **Decisions:** each decision's `advice_use` and its line.

## 5. Authority

[AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) change with part 1's code:
- `TRADE_REVIEW_V1` (EVALUATOR) and `TRADE_COACH_V1` (ANALYST) finish only with their own record; no tool and no view of the account beyond the fact sheets; started by SYSTEM, never by a model; no draft, submission, pause, stop, limit or policy. The matrix's existing rows (critique an artifact; create an evidence-linked assessment) cover them; no permission is added.
- The trader's authority is unchanged: it proposes within `FUTURES_POLICY_V1` (§13), and code sizes, checks and fills every order.
- A lesson or a note changes no rule ([AGENTS.md](../../../AGENTS.md) rule 4); a rule changes only in an update the owner installs.
- The reviewer is not independent: the three run on one model ([RUNTIME_AGENTS](../RUNTIME_AGENTS.md#model-roles)). The scoreboard, computed by code, is the check.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| T1 | One fact sheet per closed position, exact and hashed, from stored rows only; none for an open one; R, the worst and best price and the costs match hand-computed fixtures for a long and a short, a stop, a take-profit, a time exit, a liquidation and a funding time crossed | Database tests with fixtures |
| T2 | One review per fact sheet, at most 24 a day, oldest first; `NOT_REVIEWED` after 48 hours | Scheduler tests with a fake clock |
| T3 | A review or note never starts while a decision is queued or open, or when it cannot end before the next bar; a decision queued meanwhile cancels it at the runner, and it is queued again at most twice | Scheduler tests with a fake clock and the fake runner |
| T4 | A review with an unknown field, another target, an evidence path not in the fact sheet or a tag outside the list is refused, retried once, then ends without a review; code places the grid | Unit and database tests |
| T5 | A note with a value outside the policy's sets or a reference outside its context is refused; code adds the counts, holds the confidence at `LOW` under 10 reviewed trades and sets the expiry | Unit and database tests |
| T6 | The reviewer and the coach have no tool: every tool call is refused, and neither can draft, submit, pause or start a workflow | Role-grant tests, positive and negative |
| T7 | The trader is shown the newest unexpired note and the lessons, labeled; it must give `advice_use`, and `confidence` and `invalidation` with an entry; a note's values never change the risk gate's checks or sizing | Database tests; risk-gate tests with and without a note |
| T8 | The scoreboard's counts, averages and P&L are exact; rows under 5 trades are labeled | Unit tests with fixtures |
| T9 | Under the usage limit or with the runner stopped, reviews and notes wait, trading and protection go on, and an expired note is not shown | Database tests |
| T10 | The pages show each state (a review pending, done, failed or not reviewed; a note, none or expired) and the followed and ignored rows, by keyboard and in the accessibility tree | Component tests; the browser suite on seeded fixtures |
| T11 | Migration `0022` (planned as `0021`) up, down and up on a scratch database; the downgrade refuses while a profile binds generation 8 | Migration tests |
| T12 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host, data source or model: the Codex CLI, its pin and the model table stay as installed. The shadcn registry for the preset is read at build time against the installed version for the components the pages use.

## 8. Data and trust boundaries

- No new host, secret, volume or network path; the runner still has no database, repository or credential.
- New model-authored text: the review's lines and lesson, read by the coach and the trader, and the note, read by the trader. Each reaches a model labeled as model-authored, inside a bounded schema of choices and references, and only code's numbers are shown as numbers.
- External text: the headline titles in a fact sheet, labeled as external. A headline written to steer the reviewer can at most change its words within the schema.
- New stored data: the fact sheets, reviews and notes, kept with the trades and in every backup.

## 9. Implementation sequence

0. **Part 0, documents** (2026-10-24): this plan, approved by the owner's pick; [DECISIONS](../../DECISIONS.md), [ROADMAP](../../ROADMAP.md), [STATUS](../../STATUS.md) and the [docs index](../../README.md).
1. **Part 1, after M11's update 2 part B is installed and checked** (the thread "Bitcoin futures app plan" says when): read part B's code, then build §4 with migration `0022` (planned as `0021`) and generation 8, change the contracts of §5, and run the checks of §10. No money path changes, so rule 13's independent money-path review does not apply; T6 and T7 carry the authority change. It is installed after [ExecPlan 0042](0042-no-owner-sign-in.md), on top of its migration `0021_no_owner`.
2. **The owner's double-click** of `update-app.cmd`. The thread then checks, read-only on the PC, the first fact sheet, review and note after the first trade closes.

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): the web checks (lint, types, unit, build), Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL, the browser suites on seeded fixtures, the update model and the link check, with results recorded in §14. `NOT RUN` in the cloud and done by the update or its check on the PC: the Docker build, the agents' check against the real model, and the first real reviews and notes.

## 11. Failure and rollback

- A review or note fails or times out: the trade has no review (`NOT_REVIEWED` after 48 hours) or the trader decides without a note. Trades and Settings say so.
- The advice does worse: the scoreboard shows it, and switching the coach off is a later update.
- Rollback: the update's rollback tags bring back the images before it; migration `0022`'s downgrade removes its table, views and generation 8, and refuses once any fact sheet, generation-8 workflow, review or note exists or a profile binds generation 8, as `0016`'s did. The update's backup keeps the reviews.

## 12. Q01–Q10

All apply. Q01 and Q02: the three pages' new states in a real browser, by keyboard and in the accessibility tree (T10). Q03: T1 to T9. Q04: no new secret or host; model and external text labeled (§8). Q05: cancellation, retries, caps and the usage limit (T3, T9). Q06, budgets declared before measuring: a review and a note each end within 300 s on the PC, and the trader's time from bar close to decision start is no longer than before part 1. Q07: every cloud suite. Q08: the review and note states on Trades and in Settings. Q09: the migration and its rollback (T11). Q10: the contracts of §5; no new dependency.

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-24 | One review per closed position, not per fill | A round trip is what has a result to learn from |
| 2026-10-24 | Code writes the facts; the models only judge and advise | No model can get a number wrong, and each call stays small |
| 2026-10-24 | Records in the database, not log files | Backed up, hashed, shown on the pages, and read by the coach |
| 2026-10-24 | Code places the call-and-luck grid from the model's grade and the computed result | The model grades only the decision |
| 2026-10-24 | The coach cites scoreboard rows, and code adds their counts | A count in the model's words could be wrong |
| 2026-10-24 | Reviews and notes yield the slot to decisions, canceled at the runner when needed | The trader's pace comes first, and the runner's cancel exists |
| 2026-10-24 | Refined from the proposal: a 300-second deadline that ends before the next bar instead of 2 minutes; no scan of the words for prices, since only code's numbers are shown as numbers (the proposal was edited to match) | A Codex call at the evaluator's effort may take longer than 2 minutes, and free text cannot be cleanly scanned for prices |
| 2026-10-25 | Part 1's migration is `0022_trade_reviews`, on [ExecPlan 0042](0042-no-owner-sign-in.md)'s `0021_no_owner` | The owner asked at 08:10 UTC to remove the owner completely; that update is built and installed first |
| 2026-10-25 | No `FUTURES_POLICY_V2`: the run stays on `FUTURES_POLICY_V1` | The futures policy names no agent template or generation (`app/futures/definitions.py`), so generation 8 replaces the trader's template under it; a V2 with V1's values would only move the run to a new hash |
| 2026-10-25 | The trader's confidence and invalidation stay generation 7's `uncertainty_level` and `invalidation`, asked at every decision; generation 8 adds `advice_use` and `advice_note` (one line, at most 200 characters), and `NO_ADVICE` is accepted exactly when no note was shown | §4.4 said a confidence generation 7 already has is kept, not doubled |
| 2026-10-25 | The gate: not in the quiet window (HH:59:30 to HH:06:00 UTC), no decision queued or open, 30 seconds after the last decision ended, and the 300-second deadline plus 60 seconds before the next 15-minute bar | An entry's fill starts the trader's next decision at once, and 30 seconds leave it the slot; the quiet window is every template's but the trader's |
| 2026-10-25 | Yielding ends the reviewer's or coach's workflow `CANCELED` (`YIELDED_TO_DECISION`) after its call is canceled at the runner; its record gets a new start later, three starts in all (the first and two more). A start ended by the usage limit or a missing login does not count; a refusal after the retry, or an abstention, ends the record `FAILED` at once | "Queued again at most twice" (§4.6) as three starts of one record; the model's own answer is final, the allowance is not |
| 2026-10-25 | `NOT_REVIEWED` counts 48 hours from when the sheet was stored; a closed trade whose sheet is not built yet is pending, and not reviewed 48 hours after its close, on Trades and in Settings' counts alike | A sheet waits for its funding (below), and the reviewer cannot start before it |
| 2026-10-25 | A sheet is built a minute after the close (the exit minute's candle is final), once every funding time crossed is recorded and posted, or six hours after the close in any case; at most five a pass, from twenty tried, each in its own savepoint | A failing sheet must not hold back the trades after it. Known limit: a payment still `PENDING` after six hours is listed as pending and is not in the sheet's net, and a later posting does not change the sheet |
| 2026-10-25 | A sheet over 8 KiB drops the oldest feed items, then the oldest decisions, then the oldest run events, and names them in `omitted` | The trade's own numbers are never dropped |
| 2026-10-25 | The 1-hour trend at entry is the trader's own feature (`futures_context.trend_1h`, from 24 complete hourly candles), `UNKNOWN` with fewer | The sheet shows the trend as the trader could see it |
| 2026-10-25 | The scoreboard counts every fact sheet, reviewed or not; a review's tags add the tag rows; generation 7's trades are in no `advice_use` row | The results are code's whatever the reviewer does; only generation 8's trader says how it used a note |
| 2026-10-25 | The coach is shown at most 20 reviews, the oldest dropped first to fit the 32 KiB context | The newest review, which it answers, always stays |
| 2026-10-25 | The downgrade also refuses once any fact sheet, generation-8 workflow, review or note exists | Removing the table would lose the records; a restore from the update's backup is the way back |
| 2026-10-25 | Settings shows how many trades are in each review state and until when the note is in force, in the Agents section | Q08; one card, no new page |
| 2026-10-25 | The browser suite shows pending, reviewed and failed reviews and the note in force and none; an expired note and `NOT_REVIEWED` are shown by the component tests and read through the strict models by the database tests | They need four and 48 hours to pass, which a seeded browser run cannot wait for |

## 14. Progress

- 2026-10-24 08:50 UTC: the proposal and a decision card in the thread. 09:17:13 UTC: the owner picked "Build it as proposed" (APPROVED). This plan written (part 0); nothing implemented or run.
- 2026-10-25: part 1 IMPLEMENTED by the project thread in a cloud session with no Docker, first on `main` at `d51eece` (commits `14084be`, `cc3b7b8`, `cc9a0bf`, `3d4389a`), then moved onto [ExecPlan 0042](0042-no-owner-sign-in.md)'s commit `b4ee029` after the owner's ask of 08:10 UTC to remove the owner (§13): migration `0022` on `0021_no_owner`, and the coach's read takes the service key alone. PR #126, first stacked on 0042's PR #125, and on `main` since #125's merge at 12:34 UTC (`416cef8`). Every database check ran on a scratch PostgreSQL 16 cluster at 127.0.0.1:55452 with scratch secrets, each on a database created for it; nothing touched the owner's app.
  - Found by the database tests and fixed: `trade_facts.store()` bound one value both as text and as `CAST(... AS jsonb)`, which psycopg refused (`AmbiguousParameter: inconsistent types deduced for parameter $17`); `trade_records.scoreboard()` read its rows without `.mappings()` (`TypeError`). Found while writing the browser check: Settings' counts left out a closed trade whose sheet was not built yet, which Trades shows as pending; the coach's read now counts it as pending, and as not reviewed 48 hours after its close (§13).
  - VERIFIED on `d51eece`: `68 passed` at 10:08 UTC (`test_m11_reviews.py`, `test_m11_trader.py`, `test_m11_futures_db.py`, `test_m11_futures_api.py`), and T11's test alone `1 passed` at 10:13 UTC. Web: types, ESLint, Prettier and the API check pass, Vitest `280 passed` (33 files), and the build exits 0. Ruff, `test_m11_image_prompts.py` `2 passed`, 0 broken links, the update file's model (PowerShell 7.4.6) 21 scenarios and 98 expectations with none failed, and the agent runner `Ran 20` with its 3 image-only failures.
  - The full engine suite on `d51eece` (1 h 05 min): `10 failed, 1630 passed, 122 errors`. Errors: the research store's 61 and `test_m1_account.py`'s 13, both known ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)), and 48 after one failure: `test_m7_schema.py`'s downgrade test, which compared 0009's indexes at the head, met `0022`'s `agent_artifacts_one_trade_review` and left the database at `0008`. Failures: the known `test_api.py` status test and `test_m6_schema.py` downgrade; that downgrade test; the M5 and M6 privilege inventories, which did not know the new `trade_` relation; three `test_m9_feeds.py` tests on the database left at `0008`; `test_m2_reference_checks.py`'s confirmation test (a timeout; it passed when run again below); and `test_m4_engine.py`'s slow-step test, below.
  - A test-only fault, on `main` since 0039: `app.db.get_engine()` is cached with the identity of its first call. `test_m11_trader.py`'s decision test reads a workflow through `agent_views`, whose `schema_revision()` builds that engine as the migration identity the `m7` fixture sets, and the next test that expects the API's engine, `test_m4_engine.py`'s slow step, then waits on a row lock with no lock timeout. A scratch pytest plugin that records each build of the engine found it. VERIFIED: the pair hung until killed at 240 s (11:26 UTC); with the `m7` fixture disposing and forgetting the engine at its end, `2 passed` in 21 s (11:31 UTC).
  - VERIFIED on `b4ee029` with this part, each on a fresh database: `87 passed` at 11:22 UTC (the four suites above, `test_m11_no_owner.py`, `test_m11_clean_start.py` and the slow step); `122 passed` at 11:31 UTC (the two inventories, which skip `trade_` as they skip `futures_`, `test_m9_feeds.py`, the whole of `test_m7_schema.py`, whose downgrade test reads 0009's objects below `0021` since 0042, and the confirmation test). Web, 11:33 to 11:36 UTC: Prettier, types, the API check, Vitest `284 passed` (33 files) and the build pass; ESLint passes once `apps/web/.output` is removed (with a build present it reads the build, as [COMMANDS](../../COMMANDS.md#web-cloud) says). Ruff on the engine and the agent runner, the OpenAPI check, 0 broken links (127 files), plain-ASCII update files, and the agent runner `Ran 20` with its 3 image-only failures.
  - VERIFIED in a browser (Chromium 1243, `e2e/reviews.spec.ts`'s first run), on a database seeded by `tests.m11_browser_fixture seed`, with the feed, the API (`ASL_AGENTS_OFFLINE_TEST=1`) and the built web server: at 11:37 UTC the fixture's `reviews` command wrote what the suite expects (one review refused twice and failed, one recorded, the coach's note on it), and the suite failed on four of its own patterns, which the pages do not match: a price carries its unit, money keeps the decimals the app shows (`+0.035 USDT`), an average may be zero, and the tags list sits inside its term's definition in the accessibility tree. Corrected, on a fresh database at 11:42 UTC: `5 passed`; then `local-time.spec.ts` and `pages.spec.ts` on the same database, `12 passed`.
  - The full engine suite on `b4ee029` with this part, 11:43 to 12:42 UTC: `8 failed, 1698 passed, 74 errors`. The errors are the known 74 ([COMMANDS](../../COMMANDS.md#engine-on-a-scratch-postgresql-cloud)). Two failures are known: `test_api.py`'s status test, which fails on `main` too, and `test_m6_schema.py`'s downgrade, below. The other six were T11's: it ran Alembic in the test's own process, whose `fileConfig` disables every logger that exists by then (as `test_m7_binding.py` notes), so the six M2 tests after it that read `asl.market_worker`'s records through `caplog` saw none. The full run on `d51eece` had started at 10:10 UTC, before T11 was added at 10:12 UTC, so it never ran T11. VERIFIED: T11, then `test_m2_unit.py`'s retention test, `1 failed, 1 passed` at 12:43 UTC (on `3d4389a` too: the same pair at 13:26 UTC, and the long-rest test after the 268 tests the full run puts before it at 13:34 UTC); with T11's Alembic in a process of its own, as `test_m11_no_owner.py` runs it, `2 passed` at 12:44 UTC.
  - Found by a rerun and fixed: T4 failed once at 12:59 UTC, its coach's note missing. The M5 test clock leaves the quiet window (HH:59:30 to HH:06:00 UTC, when the reviewer and the coach do not start) only when it is made inside it, so a test begun seconds before HH:59:30 crossed into it midway. VERIFIED with a scratch plugin that sets where the test clock starts: T4 failed with it 1.5, 2 and 2.5 s before the window and passed at 1, 3.5, 4, 5, 8 and 120 s (13:12 to 13:13 UTC). The review tests and the browser fixture's review step now take a `ReviewClock`, which also leaves the window when it begins within a minute: T4 then passed at 1.5, 2, 2.5, 59 and 61 s, and the whole suite with every test's clock 2 s, then 30 s, before the window, `27 passed` twice (13:16 UTC).
  - OBSERVED while checking the rest, neither from this part. `test_m6_schema.py`'s downgrade passes alone on a fresh database (`1 passed`, 12:49 UTC) and fails after `test_m6_agent_units.py`, `test_m6_agents.py`, `test_m6_api.py` and `test_m6_evidence.py` (`1 failed, 190 passed`, 12:55 UTC): they leave five `MOCK_` source versions (`PROPOSED`) in `agent_definitions`, which `0008`'s downgrade does not remove, so its kind check is violated. `test_m2_stream_continuity.py::test_back_to_back_rotations_under_load_keep_the_fence` fails on this machine with `QUEUE_OVERLOAD` with the three M2 files alone too (`1 failed, 90 passed`, 12:58 UTC), and three other M2 timing tests each timed out in one of five runs; no thread is left alive after the review suite (13:22 UTC).
  - VERIFIED after these fixes, each on a fresh database: `test_m11_reviews.py` `27 passed` four times with T11's fix (13:04 to 13:07 UTC); with `ReviewClock`, the review suite and then the three M2 files, `2 failed, 116 passed` at 13:21 UTC, the two being the test under load and one of the timing tests above, with the logger enabled throughout; the browser fixture's `seed` and then `reviews`, one failed review, one `GOOD_CALL_UNLUCKY` and the coach's note (13:22 UTC); Ruff on the engine and the agent runner; without a database, `2 failed, 954 passed, 416 skipped, 408 errors` at 13:24 UTC, the two known failures, every error a database case; and the update file's model (PowerShell 7.4.6), 22 scenarios and 105 expectations with none failed (13:25 UTC).
  - VERIFIED for the update's order once 0042's fix (PR #127) is on `main`: the new api accepts `0021_no_owner`, so the update replaces the api and then the web before the migration, and the web's health check reads the home page through the api. On a database migrated to `0021_no_owner` and seeded by `tests.m11_browser_fixture seed`, both with `main`'s code at `416cef8`, this part's API (`ASL_AGENTS_OFFLINE_TEST=1`) and built web server, 14:41 to 14:46 UTC: the web's health check passed; Home, Trades, the three trades, Decisions, Markets and Settings answered 200 with no alert; the API's ready check, trades, a trade and decisions answered 200, and the coach `SCHEMA_PENDING`. Then the update's migration command, `python -m app.research.migrate 0022_trade_reviews`, with both still running: applied in one attempt. With no restart, the same pages answered 200 again, the closed trades showing "Review pending", and the coach `READY`. Read in the migration, not run: the old workers, which run on `0022` until the update replaces them, write nothing it refuses (it widens two checks, and its decision guard still accepts `FUTURES_DECISION_V1`).
  - NOT RUN: the Docker build; the update on the PC and its check; the agents' check against the real model on generation 8, which the update runs again before the trader opens a new trade; the first real fact sheet, review and note, and Q06's times on the PC; Windows PowerShell 5.1; the research store's suites; in a browser, an expired note and `NOT_REVIEWED` (§13); the browser suites whose pages this part does not change (`perp.spec.ts` and the suites 0042 ran); and `reviews.spec.ts` after the fixture's clock changed (its review step alone gave the same answer).
- 2026-10-25: part 1 **installed** on the owner's PC. PR #126 was merged at 15:18 UTC (`6dc1026`) on the owner's yes in the thread (the decision card, 14:08 UTC), once [ExecPlan 0042](0042-no-owner-sign-in.md)'s update was installed and checked. The owner's double-click: the update record `COMPLETE`, 15:33:47 to 15:38:31 UTC at `6dc1026`; the api and then the web replaced, then `0021_no_owner` to `0022_trade_reviews` in one attempt, then the other services. OBSERVED read-only on the PC at 15:50 to 15:55 UTC: the agents' runtime `ENABLED` with `CHECK_PASSED` at 15:37:41 UTC; the trader's first bar decision on `FUTURES_DECISION_V2` at 15:45 UTC (`HOLD`, `NO_ADVICE`); the ten containers running; Home, Trades, Decisions, Markets and Settings answered 200; no error or traceback line since the update. No futures position had opened yet, so there was no fact sheet, review or note.
- 2026-10-26 to 2026-10-28: the first real reviews, OBSERVED read-only on the PC. Until 2026-10-27 13:15 UTC the trader held at every decision (71 of 71 by 2026-10-26 07:06 UTC, each `NO_EDGE`; every answer `NOTED`, no latch), so nothing was reviewed. By then [ExecPlan 0043](0043-score-every-decision.md) and [ExecPlan 0044](0044-a-trader-that-commits.md) were installed, so the coach ran as `TRADE_COACH_V2` and then `V3`, and the trader as `FUTURES_DECISION_V3` and then `V4`; the fact sheets and `TRADE_REVIEW_V1` are this part's. On 2026-10-28 at about 13:36 UTC, at `d6eccdb` (schema `0027_result_checks`):
  - Three long 1x positions closed on 2026-10-27: 13:15 to 14:00 UTC by the trader's exit (`LOSS`, R `-0.7551`, net `-18.66335968` USDT), 14:30 to 18:30 UTC at its time exit (`WIN`, R `0.2490`, net `6.12243522`) and 19:45 to 22:00 UTC at its stop (`FLAT`, R `-0.0900`, net `-2.22748721`). Each has one fact sheet, built 61 to 70 s after its close, and one review.
  - The reviews: the first `MIXED` (decision `OK`; tags `WITH_TREND`, `GOOD_EXECUTION`, `DATA_PROBLEM`; lesson "For an hourly uptrend pullback, require short-term returns to confirm the rebound and define invalidation using features that can be checked."), the second `GOOD_CALL_WON` (`GOOD`), the third `MIXED` (`OK`, with `THIN_MARKET`). Two reviews carry `DATA_PROBLEM`; what their sheets showed was not checked.
  - Q06: the three `TRADE_REVIEW_V1` calls took 43.2, 31.3 and 23.7 s and the four `TRADE_COACH_V3` notes 15.1 to 17.3 s, within the 300 s budgeted; all `SUCCEEDED`. Each review was recorded 1 min 41 s to 6 min 32 s after its close; the longer waits fit the rule that a review starts only when no decision is queued or open (inferred from the times, not checked per decision).
  - The notes after the reviews lean `EITHER` at `LOW` confidence (fewer than ten reviewed trades) and cite six records each. Over the 30 hours before the check the trader's decisions said `FOLLOWED` 76 times, `PARTLY` twice and `NO_ADVICE` 49 times; the newest note had expired at 05:32 UTC with no trade closed since (inferred as the cause of the later `NO_ADVICE`, not checked per decision).
  - Each closed trade's page answered 200, and the first one's shows its lesson; Home, Trades, Decisions and Settings answered 200. No error or traceback line in the api, agent worker, agent runner or execution worker logs since their containers were recreated at 10:05 to 10:09 UTC (one `agent_result_checks` line with `"error":null`).
  - Still NOT RUN: the pages by keyboard and in the accessibility tree on the PC (Q01, Q02); an expired note and `NOT_REVIEWED` on the PC's pages; the trader's time from bar close to decision start against before part 1 (Q06's second budget); and whether following the advice helps, on which Home draws no conclusion before 20 trades on each side (§4.5).
