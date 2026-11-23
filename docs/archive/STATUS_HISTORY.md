# Status history

Earlier states of [STATUS.md](../STATUS.md), newest first, each kept unchanged as the record.

## Until ExecPlan 0060 (2026-11-12)

The sections of [STATUS.md](../STATUS.md) that described the futures app, from [ExecPlan 0031](plans/0031-m8-simple-app-that-runs-itself.md)'s one screen until M12's build ([ExecPlan 0060](../plans/0060-spot-trading-only.md)), as they read on 2026-11-12. M12 retires the futures account, its AI agents and research; the follow-ups below that concern them closed with them.

### Running on the owner's PC

OBSERVED on 2026-10-25 at 15:13 to 15:16 UTC, read-only: [ExecPlan 0042](plans/0042-no-owner-sign-in.md) is installed (`3c2610a`, the update done at 15:09:40 UTC on the second try; the first, at 14:11 UTC, stopped before the migration). The futures app runs at schema `0021_no_owner` with no sign-in. The app funded its account itself at 15:05 UTC (`SYSTEM:INITIALIZE`, 10,000 virtual USDT, NAV 100), futures run #1 has run since 15:05 UTC, and the agents switched themselves on, their check passed at 15:08 UTC. Every service runs its new image; reconciliation `OK`, the five pages answering, the Bitcoin perpetual's feed `CONNECTED`, the news sources fetched ([§13](plans/0042-no-owner-sign-in.md#13-progress)). The database before the futures app stays kept as `asl_before_futures` ([0039 §15](plans/0039-bitcoin-futures-on-paper.md#15-progress)). The trader decided `HOLD` at 15:15 and 15:30 UTC. Since 15:38 UTC the PC runs `6dc1026`, with ExecPlan 0040's part 1 (below). Since 16:42 UTC it runs `267d033`: the charts keep Lightweight Charts' own look ([DECISIONS](../DECISIONS.md#2026-10-25--the-charts-keep-lightweight-charts-own-look), PR #129), the update's record `update-20261025T163744Z` `COMPLETE` (16:37 to 16:42 UTC) with its checks passed, as the thread "Use native chart styling" recorded; the pages were not looked at in a browser on the PC. Since 08:43 UTC on 2026-10-26 it runs `f7a96c3`, with [ExecPlan 0041](plans/0041-twins-and-a-veto.md)'s part 1, the twins and the league table, at schema `0023_twins` (record `update-20261026T083801Z` `COMPLETE`, 08:37 to 08:43 UTC, reconciliation `OK`, the five pages answering; [0041 §14](plans/0041-twins-and-a-veto.md#14-progress)). Since 15:10 UTC on 2026-10-26 it runs `de71f6e`, with [ExecPlan 0043](plans/0043-score-every-decision.md)'s update 1, the decision scores, at schema `0024_decision_scores` (record `update-20261026T150519Z` `COMPLETE`, 14:56 to 15:10 UTC, reconciliation `OK`, the five pages answering; at 15:38 UTC the scorer had stored 583 scores of the run's first day, none failed or incomplete; [0043 §14](plans/0043-score-every-decision.md#14-progress)). Since 19:17 UTC on 2026-10-26 it runs `9d1c5f6`, with 0043's update 2, generation 9 of the agents, at schema `0025_decision_reviews` (record `update-20261026T191227Z` `COMPLETE`, 19:12 to 19:17 UTC, reconciliation `OK`, the pages answering, the agents' check `PASSED` on the new trader at 19:16 UTC; the first decision reviews, of 25 and 26 October, recorded by 08:32 UTC on 2026-10-27; [0043 §14](plans/0043-score-every-decision.md#14-progress)). OBSERVED: the whole app was down from about 20:15 UTC on 2026-10-26 to 08:27 UTC on 2026-10-27 (every container, PostgreSQL included, started at 08:27 UTC), with no decision in between; the cause was not determined. Since 13:09 UTC on 2026-10-27 it runs `54c3002`, with [ExecPlan 0044](plans/0044-a-trader-that-commits.md), generation 10 of the agents, at schema `0026_committed_trader` (record `update-20261027T124108Z` `COMPLETE`, 12:41 to 13:09 UTC, reconciliation `OK`, the five pages answering, the agents' check `PASSED` on the new trader at 13:09 UTC); the trader's first entry, a long, filled at 13:15 UTC ([0044 §14](plans/0044-a-trader-that-commits.md#14-progress)). Since 09:37 UTC on 2026-10-28 it runs `717436f`: the charts follow the dark theme ([DECISIONS](../DECISIONS.md#2026-10-28--the-charts-follow-the-dark-theme-in-lightweight-charts-own-colours), PR #139), the update's record `update-20261028T093323Z` `COMPLETE` (09:33 to 09:37 UTC, no migration, reconciliation `OK`, the pages answering, the agents' switch on), as the thread "Add dark mode to the charts" read it; the pages were not looked at in a browser on the PC. Since 10:09 UTC on 2026-10-28 it runs `d6eccdb`, with [ExecPlan 0045](plans/0045-where-the-results-come-from.md)'s four result checks, at schema `0027_result_checks` (record `update-20261028T094210Z` `COMPLETE`, 09:42 to 10:09 UTC, reconciliation `OK`, the pages answering, the agents' check `PASSED`). By 10:13 UTC the builder had stored 172 bar outcomes, all scored. The first daily result was `DONE` at 10:08 UTC, with costs on the 3 closed trades and every other check too few. Every candle from 10:06 UTC carries its taker buy volume. Home's card was seen in a browser on the PC ([0045 §14](plans/0045-where-the-results-come-from.md#14-progress)). Since 13:44 UTC on 2026-10-28 it runs `b2cf8a9`, with [ExecPlan 0046](plans/0046-leaner-agents.md)'s leaner agents, generation 11, at schema `0028_leaner_trader` (record `update-20261028T133940Z` `COMPLETE`, 13:39 to 13:44 UTC, reconciliation `OK`, the pages answering, the agents' check `PASSED` on the new profile at 13:43 UTC). The first generation-11 decision, a `HOLD`, came at 13:45 UTC; the first two calls averaged 13,933 input tokens against generation 10's 23,685 ([0046 §14](plans/0046-leaner-agents.md#14-progress)). Since 22:09 UTC on 2026-10-28 it runs `bff1a33`: the agents' models in Settings ([DECISIONS](../DECISIONS.md#2026-10-28--the-agents-models-on-settings), PR #145), record `update-20261028T214446Z` `COMPLETE` (21:44 to 22:09 UTC, no migration, reconciliation `OK`, the five pages answering, the agents' check `PASSED`); a second run on the same commit, `update-20261029T070502Z`, was `COMPLETE` too (07:00 to 07:09 UTC on 2026-10-29). Read-only at 08:15 UTC on 2026-10-29, `curl` only: Settings answered with the Models section's five cards and the eight models the sign-in offers, and no read error; the trader had made 86 calls since its generation's first at 13:45 UTC on 2026-10-28, 84 answered and 2 failed, 14,433 input and 306 output tokens a call on average. Since 19:09 UTC on 2026-10-30 it runs `8908e14`, with [ExecPlan 0047](plans/0047-live-trades-and-pop-ups.md)'s live trades and pop-ups (record `update-20261030T190504Z` `COMPLETE`, 18:45 to 19:09 UTC, no migration, reconciliation `OK`, the five pages answering, the agents' switch on with `CHECK_PASSED`). Read-only at 19:16 UTC, `curl` only: the live stream `/api/live`, asked as the app's pages ask, answered with its `ready` event (cursor 44) and a ping 15 s later, and another site's request was refused with 403 ([0047 §14](plans/0047-live-trades-and-pop-ups.md#14-progress)). Since 21:42 UTC on 2026-10-30 it runs `424bb53`: no disclaimers on the pages, no PAPER badge and no paper or virtual wording ([DECISIONS](../DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages), PRs #149 and #150), record `update-20261030T213740Z` `COMPLETE` (21:37 to 21:42 UTC, no migration, reconciliation `OK`, the five pages answering, the agents' check passed). Read-only at about 21:47 UTC, `curl` only: the five pages answered 200 and none of their markup holds the removed notices; the title reads "Adaptive Spot Lab". The words "hindsight" and "model-authored" remain only in the agents' profile data that Settings receives and does not draw. Since 09:09 UTC on 2026-10-31 it runs `7058d6c`, with [ExecPlan 0048](plans/0048-the-cockpit.md)'s part 1, the Cockpit (PR #153), record `update-20261031T090510Z` `COMPLETE` (08:54 to 09:09 UTC, no migration, schema `0028_leaner_trader`, reconciliation `OK`, the five pages answering 200, the agents' check passed); the owner looked at the pages afterwards and asked for the others to be redrawn too ([DECISIONS](../DECISIONS.md#2026-10-31--the-new-design-for-trades-a-trade-and-decisions-execplan-0048-part-2)).

### In progress

- **M11: Bitcoin futures on paper** ([ExecPlan 0039](plans/0039-bitcoin-futures-on-paper.md), the owner's ask of 2026-10-23 12:51 UTC, and a clean database allowed at 12:52 UTC): one simulated instrument, the BTCUSDT perpetual, long or short at up to 2x with modeled fees, funding and liquidation; a decision every 15 minutes and code protection every second; a toast for every fill and entry and exit markers on the chart; one trader agent instead of nine, on Codex; a clean database with the old one kept. **Approved** by the owner on 2026-10-23 at 13:09 UTC ([DECISIONS](../DECISIONS.md#2026-10-23--m11-approved-bitcoin-futures-on-paper-execplan-0039)); the rules are changed (part 0). Update 1 (Claude Code instead of Codex) was installed at 16:15 UTC; at 17:15 UTC, before its sign-in ran, the owner kept Codex ([DECISIONS](../DECISIONS.md#2026-10-23--the-owner-keeps-codex-for-the-agents-execplan-0039)). Update 1b put Codex back (PR #117, `e21ee6e`): installed at 19:11 UTC, and the agents' check passed at 19:14 UTC ([ExecPlan 0039 §15](plans/0039-bitcoin-futures-on-paper.md#15-progress)). Update 2 comes in two parts ([§9](plans/0039-bitcoin-futures-on-paper.md#9-implementation-sequence)). Part A, the perpetual's market data and its live chart on Markets (migration `0019`, PR #119, `fc65ffc`), was installed by the owner on 2026-10-24 (the update done at 10:10 UTC); the feed reads `CONNECTED` on the PC and the spot app keeps trading ([§15](plans/0039-bitcoin-futures-on-paper.md#15-progress)). A fix found on the PC rides with the next update: the futures client now reads Binance's futures weight allowance, so other clients on the owner's IP no longer make its clock check wait. Part B, the futures account, `FUTURES_POLICY_V1`, the one trader (generation 7), the toasts, the chart's marks and the futures pages (migration `0020`, PR #121), is built and tested in the cloud, and the independent money-path review found nothing blocking (its findings are fixed, each with a test; [§15](plans/0039-bitcoin-futures-on-paper.md#15-progress)). It was merged on the owner's yes of 2026-10-24 at 15:12 UTC. Its update starts the app on an empty database and keeps the old one renamed with a copy of the backup ([OPERATIONS](contracts/OPERATIONS.md#m11-the-futures-apps-clean-start-execplan-0039)); after it the owner sets up the owner, confirms the 10,000 virtual USDT and turns the agents on. The first install stopped at the empty database's migration: on the PC the source and research identities can log in, which migration `0008` refuses, and the undo put the old database back but could not start the stopped services again (observed above). The fix keeps those logins through the migration in one transaction, starts stopped containers by their ids, and lets the next run finish what a stopped one left; it was tested on a copy of the PC's database setup ([§15](plans/0039-bitcoin-futures-on-paper.md#15-progress)). A second try collided with a restart from this project's own session on the PC and undid itself. The third, on 2026-10-25, did the clean start, but the agent worker's image lacked the trader's prompt, so the worker did not start; the fix packed the prompt into the image (PR #123), and the fourth install completed at 07:38 UTC (observed above). The owner's setup, funding and agents' switch that remained are removed by ExecPlan 0042 (below).
- **No sign-in and no setup** ([ExecPlan 0042](plans/0042-no-owner-sign-in.md), the owner's ask of 2026-10-25 08:10 UTC, "remove the owner completely, no setup should be needed"; [DECISIONS](../DECISIONS.md#2026-10-25--no-owner-sign-in-and-no-setup-execplan-0042)): the owner's passphrase, sessions and setup key go; the app contributes the starting 10,000 virtual USDT itself when the API starts, the agents switch themselves on (the agents' check still enables them), and the first run starts by itself. Settings keeps the owner's controls without a sign-in: the agents' off switch, Pause, Resume and Stop, top-ups, and Start after a stop. Migration `0021`. Built and tested in the cloud, merged on the owner's yes (PR #125, 12:34 UTC). The first install stopped before the migration: the update replaced the web before the api, and the new web cannot work with the old api. The fix replaces the api first (PR #127, 14:54 UTC). The second install completed at 15:09 UTC, and the read-only check found the account funded by the app, run #1 running and the agents' check passed (observed above; [§13](plans/0042-no-owner-sign-in.md#13-progress)).
- **An AI review of every trade, and a coach** ([ExecPlan 0040](plans/0040-trade-reviews-and-a-coach.md), the owner's ask of 2026-10-24 08:41 UTC): after each closed futures trade, code writes a fact sheet, a reviewer agent grades the decision apart from the result and records one lesson, and a coach agent turns the recent reviews into an advice note the trader reads at each decision; code's scoreboard compares the trades that followed the advice with those that ignored it. Neither agent can trade or change a rule. **Approved** by the owner on 2026-10-24 at 09:17 UTC ([DECISIONS](../DECISIONS.md#2026-10-24--an-ai-review-of-every-trade-and-a-coach-execplan-0040)). Part 1 (migration `0022`, generation 8 of the agent definitions; PR #126, merged on the owner's yes at 15:18 UTC) is **installed** on the PC on 2026-10-25 (`6dc1026`, record `COMPLETE` at 15:38 UTC; the api and then the web replaced before the migration, `0021` to `0022` in one attempt). OBSERVED read-only at 15:50 to 15:55 UTC: the agents' check passed (`CHECK_PASSED` at 15:37:41 UTC), the trader's first bar decision on `FUTURES_DECISION_V2` at 15:45 UTC (`HOLD`), the five pages answer 200 and no error lines. The first three trades, closed on 2026-10-27, each have a fact sheet and a review (each review call within 44 s), and the coach's notes followed; OBSERVED read-only on 2026-10-28 ([0040 §14](plans/0040-trade-reviews-and-a-coach.md#14-progress)).
- **Twins and a veto** ([ExecPlan 0041](plans/0041-twins-and-a-veto.md), the owner's ask of 2026-10-25 07:22 UTC): three isolated paper accounts trade the perpetual beside the trader by fixed rules (hold BTC, a trend rule, the trend rule with a cost gate and a funding filter), with the same money, limits, costs and fills, and Home compares each with the trader in a league table, labeled too few until 30 days and 60 trades; then a fourth account whose entries a veto agent may refuse or halve but never start, checked against random verdicts at its own rates. Nothing of the owner's account, the trader or the rules changes. **Approved** by the owner on 2026-10-25 at 07:36 UTC ([DECISIONS](../DECISIONS.md#2026-10-25--twins-and-a-veto-the-first-experiment-on-whether-the-agents-help-execplan-0041)). Part 1, the three twins and the league table (migration `0023`, `TWIN_SET_V1`), was started on the owner's "Yes go ahead" of 17:02 UTC and is built and checked in the cloud, with an independent review of the twins' books: it found no twin code that reaches the owner's account, and one blocker (a held position's funding charged again once its marks are a week old) and three other findings, each fixed with a test ([0041 §14](plans/0041-twins-and-a-veto.md#14-progress)). **Installed** on the PC on 2026-10-26 (`f7a96c3`, PR #130 merged on the owner's yes at 08:36 UTC, the update's record `COMPLETE` at 08:43 UTC); the hold twin opened its long at 08:45 UTC and the trend twins wait for their rule. The twins run in their own step after the owner's each second, write nothing of the owner's account, and appear on Home (the league table), Trades (a filter by account) and Settings (their health). Part 2, on the owner's word of 2026-11-02 09:20 UTC ([DECISIONS](../DECISIONS.md#2026-11-02--twins-and-a-veto-part-2-the-veto-twin-a-weekly-momentum-twin-and-longer-scorecard-rows-execplan-0041)): a fourth twin whose trend-rule entries the veto agent (generation 12) may let in, halve or skip within 2 minutes, silence letting them in, with a daily placebo against random answers at its own rates; a fifth, weekly momentum twin (long or short on the last day's close against the close 8 days earlier, sized like hold BTC); and 4-hour and 24-hour rows of the trader's calls on the Scorecard, on the page only. `TWIN_SET_V2`, migration `0030`; the three twins of part 1 keep their history, and the trader is unchanged. Built and checked in the cloud, merged on the owner's yes (PR #160) and **installed** on the PC on 2026-11-02 at 14:22 UTC (`ab93f7d`, the update's record `COMPLETE`, schema `0030_veto_twins`, reconciliation `OK`, the pages answering); the five twins run, `TREND` among them, and generation 12 came into force at 14:21 UTC beside the unchanged trader ([0041 §14](plans/0041-twins-and-a-veto.md#14-progress)). The brainstorm behind it is kept as [an ideas note](ideas/agent-trading-edges.md).
- **Score every decision against what followed** ([ExecPlan 0043](plans/0043-score-every-decision.md), the owner's ask of 2026-10-26 11:34 UTC): code scores every trader decision (holds and waits included), every finished 15-minute bar and every twin entry against what the price did 15 minutes, 1 hour, 4 hours and 24 hours later, with a long and a short test trade after fees, slippage and funding, and labels each (a missed long, a hold into a loss, an early exit, an entry that only paid fees, and the rest); Decisions shows what followed each decision and Home a scorecard. Then the trader reads its scores and states the direction it expects, a daily decision review grades the day's misses, and the coach writes after it. Nothing of the account, the limits or the rules changes. **Approved** by the owner on 2026-10-26 at 11:51 UTC, "Yes, in two updates" ([DECISIONS](../DECISIONS.md#2026-10-26--score-every-decision-against-what-followed-execplan-0043)). Update 1 (the records and the pages, migration `0024`) was merged on the owner's word (PR #132) and **installed** on the PC on 2026-10-26 at 15:10 UTC (observed above). Update 2 (generation 9, migration `0025`: the trader shown its scored decisions and the 1-hour scorecard, and saying which way it expects the next hour at every decision; the daily decision reviewer; the coach reading both) was merged on the owner's word (PR #133) and **installed** on the PC on 2026-10-26 at 19:17 UTC (observed above), with an independent review in the cloud ([0043 §14](plans/0043-score-every-decision.md#14-progress)). Both updates are installed; acceptance is the owner's.
- **A trader that commits** ([ExecPlan 0044](plans/0044-a-trader-that-commits.md), the owner's question of 2026-10-27 10:47 UTC, "so far no trade or entry happened yet ? why is that"): a read-only check found every one of 139 decisions since run #1 began a `HOLD` with `NO_EDGE`, with no fault, explained by the trader's prompt, the coach's two `SIT_OUT` notes and the costs against 15-minute moves. Generation 10 (migration `0026`): the trader says `UP` or `DOWN` at every decision (`NO_VIEW` only when it abstains) and may enter in the direction of its call at `MEDIUM` or `HIGH` confidence, with a stop of 2 or 3 ATR and a time exit of 4 hours or more; code refuses any other entry; the coach no longer advises sitting out before ten trades are reviewed. Nothing of the policy, the limits, the sizing or the costs changes. **Approved** by the owner on 2026-10-27 at 10:57 UTC, "A" ([DECISIONS](../DECISIONS.md#2026-10-27--a-trader-that-commits-execplan-0044)); built and checked on the PC, merged on the owner's "I approve" (PR #135) and **installed** on 2026-10-27 at 13:09 UTC (observed above).
- **Where the results come from** ([ExecPlan 0045](plans/0045-where-the-results-come-from.md), the owner's pick of 2026-10-27 19:04:55 UTC, "Plan them as one update", after the r/ai_trading research; [DECISIONS](../DECISIONS.md#2026-10-27--four-checks-from-the-rai_trading-research-planned-as-one-update-execplan-0045)): four checks in code. The trader's entries are compared with 1,000 sets of random entries on the same days with the same exits. Its entries are replayed through every other exit generation 10 allows, with the gain or loss of its own early exits. Each trade's fees, slippage and funding are shown as a share of its risk. The taker buy volume Binance sends with each candle is stored and checked against what followed. Migration `0027`; no generation, prompt, model call or new source. **Approved** by the owner on 2026-10-27 at 21:09:40 UTC; built and tested in the cloud the same evening, with an independent review whose findings are fixed or recorded. Merged on the owner's "done" (PR #138) and **installed** on 2026-10-28 at 10:09 UTC (observed above; [§14](plans/0045-where-the-results-come-from.md#14-progress)).
- **Leaner agents** ([ExecPlan 0046](plans/0046-leaner-agents.md), the owner's ask of 2026-10-28 10:19 UTC to check and tune the agents against the official documentation; the owner's pick "Build leaner agents" at 10:35:32 UTC, [DECISIONS](../DECISIONS.md#2026-10-28--leaner-agents-execplan-0046)): the same model, efforts and rules in about 40% fewer input tokens. Every agent call carries the runner's own short base instructions instead of Codex's coding-agent instructions, and generation 11's trader (`FUTURES_DECISION_V5`, migration `0028`) a shorter prompt, the output schema once and a shorter summary of its scores. Built and checked, and one real call on the PC accepted; merged on the owner's yes of 12:21 UTC (PR #142) and **installed** on 2026-10-28 at 13:44 UTC (observed above; [0046 §14](plans/0046-leaner-agents.md#14-progress)).
- **Live trades and pop-ups** ([ExecPlan 0047](plans/0047-live-trades-and-pop-ups.md), the owner's ask of 2026-10-30 17:11 UTC, [DECISIONS](../DECISIONS.md#2026-10-30--live-trades-and-pop-ups-execplan-0047)): each fill and funding payment reaches every open page the moment the engine commits it, as a toast and in the pages on screen, and an answered decision, the run's state and the twins' trades refresh their pages. The futures worker announces each step on a PostgreSQL channel after its commit, the API serves the event stream, the browser keeps one connection for all its tabs, and TanStack Query refetches what is on screen. Desktop pop-ups for fills, off until turned on in the header's bell menu; a Live badge in the header. While live the lists poll every 60 s instead of 5. No migration, money path or dependency. Built and checked in the cloud (unit, scratch database and browser suites), merged on the owner's yes of 18:44 UTC (PR #147) and **installed** on 2026-10-30 at 19:09 UTC (observed above; [§14](plans/0047-live-trades-and-pop-ups.md#14-progress)).
- **The new design, starting with the Cockpit** ([ExecPlan 0048](plans/0048-the-cockpit.md), the owner's ask of 2026-10-31 06:37 UTC, [DECISIONS](../DECISIONS.md#2026-10-31--the-new-design-starting-with-the-cockpit-execplan-0048)): the owner's Claude Design for the five pages, one page per install with the app's own shadcn components. Part 1: Home becomes the Cockpit (a status pill, the equity with its result, return, drawdown gauge and curve, the open position on a price rail, the trader's latest call, the engine room, the chart, the latest trades in R and four tiles on whether the trader is any good); the scorecard, checks and coach's note move to Decisions and the league table to Trades; one new read, `GET /v1/futures/valuations`. No migration, money path or dependency. Built and checked in the cloud (unit, scratch database and browser suites; [§14](plans/0048-the-cockpit.md#14-progress)) and **installed** on 2026-10-31 at 09:09 UTC (observed above). Part 2, on the owner's ask of 09:18 UTC ([DECISIONS](../DECISIONS.md#2026-10-31--the-new-design-for-trades-a-trade-and-decisions-execplan-0048-part-2)): Trades (a count, the last 48 results as bars, short rows), each trade's page (a hero, the chart around the trade, the costs, the review, the decisions behind it) and Decisions (the coach's playbook, a timeline by day, a scorecard of rings and bars, every table one tap away); four shadcn components added with the CLI. Built and checked in the cloud ([§14](plans/0048-the-cockpit.md#14-progress)) and **installed** on 2026-10-31 at 12:09 UTC (`d630146`, `update-20261031T114342Z` `COMPLETE`, reconciliation `OK`, the pages answering). Part 3 ([DECISIONS](../DECISIONS.md#2026-10-31--the-new-design-for-markets-and-settings-execplan-0048-part-3)): Markets (a strip of the market's numbers over a taller chart with an interval switch) and Settings (rows with their controls for the agents, cards for the models and the run, tiles for the limits and the parts' health, the balances with the top-up inline), every detail one tap away. Built and checked in the cloud and **installed** on 2026-10-31 at 13:23 UTC (`5aa35ca`, `update-20261031T131908Z` `COMPLETE`, reconciliation `OK`, the pages answering; [§14](plans/0048-the-cockpit.md#14-progress)). All five pages now follow the owner's design.
- **Choose the agents' provider and see their usage** ([ExecPlan 0049](plans/0049-choose-the-agents-provider-and-see-usage.md), the owner's ask of 2026-10-31 07:49 UTC and pick "Yes, all four with a daily cap" at 08:03 UTC, [DECISIONS](../DECISIONS.md#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049)): Settings → Provider shows four cards (Codex CLI, Claude Code CLI, Claude API, OpenAI API) with each one's state, models, reported usage and key, and for the APIs a daily cap and the day's calculated cost; the owner's pick moves the agents after one passed test call, and the header and the Cockpit show the in-use provider's usage. Migration `0029`. Built in the cloud on 2026-10-31, checked offline and reviewed independently, with the review's fixes; **installed** on the PC on 2026-11-01 at 01:24 UTC and checked there at 08:00 UTC ([§16](plans/0049-choose-the-agents-provider-and-see-usage.md#16-progress)): Codex runs the agents on profile version 5, its 5-hour and weekly windows are read every 10 minutes, and no other provider has been picked yet. During a switch's test call the agents pause (at most 20 minutes) and the engine's stops keep guarding positions. Codex stays in force until the owner picks another provider.
- **Backtest the rule twins on history** ([ExecPlan 0051](plans/0051-backtest-the-rule-twins-on-history.md), the owner's ask of 2026-11-03 08:19 UTC and "you decide what would be best ... I want to see all the results" at 08:20 UTC, [DECISIONS](../DECISIONS.md#2026-11-03--backtest-the-rule-twins-on-binance-history-execplan-0051)): an offline simulator runs `HOLD`, `TREND`, `TREND_GATED` and `MOMENTUM_1W` through the twins' own code on Binance's public 1-minute BTCUSDT perpetual archive, 2020-01 to 2026-10, from 10,000 USDT. Run once on the untouched test window (2022-01 to 2026-10) on 2026-11-03 at `3f922a3`: hold 12,586, trend 9,606, gated 9,608, momentum 9,300; every rule `UNCLEAR` on both measures ([§14](plans/0051-backtest-the-rule-twins-on-history.md#14-progress); the results page). Code only, inert in the app: nothing to install.
- **Replay past decisions offline** ([ExecPlan 0050](plans/0050-replay-past-decisions-offline.md), the owner's pick "Replay first" of 2026-11-03 08:07 UTC, [DECISIONS](../DECISIONS.md#2026-11-03--replay-past-decisions-offline-execplan-0050)): the trader's 410 stored decision contexts of 2026-10-28 to 2026-11-01 are answered again by a replay agent (generation 13) with the trader's model, one at a time in the agents' free time, under two prompt variants (without the scores, the coach's note and the lessons; the same asked for a 4-hour call) and a control of 100; each answer is a `REPLAY` row, never a decision or a fill, and a report scores them against the free rule by the measure the plan pre-registered. It runs only on Codex with the trader's model, yields to the trader and the veto, and pauses while the Codex allowance is half used. Migration `0031`. The trader, generation 11, and the paired check due 2026-11-16 are unchanged. Installed on the owner's PC on 2026-11-03 (update `COMPLETE` at 11:09:49 UTC, `e293de4`) and checked read-only: the agents' check passed on the new profile, the first two replays were answered at 11:09 UTC and the trader stayed on time; the 920 answers take about 5 days ([§14](plans/0050-replay-past-decisions-offline.md#14-progress)). Paused by the Codex allowance from 2026-11-07 to the weekly reset of 2026-11-11; read on 2026-11-12 at 581 of 920 (63% of each arm), P1 and P2 `INCOMPLETE`, 95% of every arm `CALCULATED` around 2026-11-14 ([§14](plans/0050-replay-past-decisions-offline.md#14-progress)).
- **Backtest the AI trader on history** ([ExecPlan 0052](plans/0052-backtest-the-ai-trader-on-history.md), the owner's asks of 2026-11-03 09:15 and 09:28 UTC and pick "2 months on spare Codex, free" at 09:50 UTC, [DECISIONS](../DECISIONS.md#2026-11-03--backtest-the-ai-trader-on-two-months-of-history-on-spare-codex-execplan-0052)): the trader's model decides each finished hour of September and October 2026 for a simulated futures account from 10,000 USDT on Binance's archive (shipped with the update), with dates and prices masked, and the veto's model answers the simulated veto twin; 60 memory probes and up to 250 real-date shadows check what the model remembers. A child process of the agent worker runs the simulated accounts (no database, network or key); the agent worker asks the model one step at a time in the agents' free time, on Codex only, yielding to the live agents, in turns with the replay, and paused while the Codex allowance is half used: about 1,800 calls over about two weeks. Generation 15, migration `0032`. The trader, generation 11, and the paired check due 2026-11-16 are unchanged. Built and tested in the cloud on 2026-11-03 and installed on the owner's PC the same day (update `COMPLETE` at 14:09:57 UTC, `b9388e5`, schema `0032`), checked read-only: the agents' check passed on the new profile and the trader stayed on time. The backtest had not started by 15:11 UTC: the weekly Codex window was 51% used, and it asks the model only while every window is under half used ([§14](plans/0052-backtest-the-ai-trader-on-history.md#14-progress)). It started by itself on 2026-11-04 at 06:45 UTC, after the weekly reset. On the owner's pick of 09:35:17 UTC ([DECISIONS](../DECISIONS.md#2026-11-04--the-ai-backtest-may-use-up-to-80-of-the-weekly-codex-allowance-execplan-0052-section-15)), generation 16 ([§15](plans/0052-backtest-the-ai-trader-on-history.md#15-generation-16-the-backtest-up-to-80-of-the-week-2026-11-04), migration `0035`) lets the backtest go on until the weekly window is 80% used, every other window still under half, while the replay keeps half: CALCULATED about 2.5 weeks instead of about 4. Built and tested in the cloud on 2026-11-04 and installed on the owner's PC the same day (update `COMPLETE` at 13:15:41 UTC, `e4ad3d6`, schema `0035`), checked read-only: the agents' check passed on the new profile, generation 16's first calls succeeded and the trader stayed on time ([§14](plans/0052-backtest-the-ai-trader-on-history.md#14-progress)). Read on 2026-11-05: 200 calls in the first day, at the lane's own cap of 192 a day, with 20% of the week used by every lane together; the memory probe (C1) `NO_SIGN`, the model stating no price or direction for any of its 60 days; CALCULATED end around 2026-11-15. Read on 2026-11-07 ([§14](plans/0052-backtest-the-ai-trader-on-history.md#14-progress)): 321 of about 1,455 trader steps answered (to 2026-09-14), having waited while the Claude run went first; the weekly window at 47%, so the share between half and 80% is still NOT RUN; its first 13 days, read INTERIM by ExecPlan 0055's report, −1.8% (`MODELED`), M1 `LOSES_MONEY`, M2 `UNCLEAR`, M3 `TRAILS_RULE`, M4 `NO_DIFFERENCE`; CALCULATED end still around 2026-11-15. It ended `STOPPED` `TRADER_REPLACED` at [ExecPlan 0059](plans/0059-the-slow-rule-trades-the-main-account.md)'s install on 2026-11-10 at 17:29 UTC, its trader answered to 2026-10-03 15:00 UTC; from 2026-11-07 it used the share between half and 80% of the week (537 calls) until 80% at 15:00 UTC on 11-10 (`OBSERVED`). Read on 2026-11-12 on its 32 whole days, every stored step rebuilt and matched ([§14](plans/0052-backtest-the-ai-trader-on-history.md#14-progress); the results page): 9,544.15 USDT (−4.6%, `MODELED`) after 136 trades (−23 USDT before costs, 435 of fees), while holding BTC made +6.9% and the gated trend rule +2.4% on the same days; M1 `LOSES_MONEY`, M2 `UNCLEAR`, M3 `TRAILS_RULE`, M4 `NO_DIFFERENCE`, the same at 0052's, 0055's and 0056's levels. Closed; nothing in the app changes.
- **Backtest Claude on the same history** ([ExecPlan 0055](plans/0055-backtest-claude-on-the-same-history.md), the owner's pick "Yes, Claude backtest (~$60)" of 2026-11-05 12:04:27 UTC and ask "can the claude backtesting be done at once" at 12:18:18 UTC, [DECISIONS](../DECISIONS.md#2026-11-05--backtest-claude-on-the-same-two-months-on-a-claude-api-key-execplan-0055)): the same backtest as 0052 in a second run, answered by Claude Sonnet 5.5 (`claude-sonnet-5-5` at `medium`) on the Claude API with the key the owner saved on 2026-11-03, nonstop in the agents' free time, after every live agent and ahead of the ChatGPT backtest and the replay, which wait while it runs. It ends when every step is answered, or by itself before $120 of cost calculated from its tokens (CALCULATED, rough: $60 to $90 and 15 to 25 hours). Generation 17, migration `0036`. The live agents stay on Codex, and a Claude refusal or credit limit never holds them. The measures were pre-registered before any call ([§4.6](plans/0055-backtest-claude-on-the-same-history.md#46-the-measures-pre-registered-a-second-trial)): 0052's four on the Claude run and M5, Claude's 1-hour calls against ChatGPT's on the same hours, passing at 99.44%. Built and tested in the cloud on 2026-11-05 and independently reviewed (no money-path defect; two fixes made: a provider failure ends its workflow without spending the model's steps, and Claude first never holds the other lanes while its child process is down). Installed on 2026-11-05 at 18:22 UTC and checked ([§13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)): the API refused each Claude call so far over one detail of the answer format (an enum beside a list of types), at no cost, while the live agents, the ChatGPT backtest and the replay went on; the runner's fix (each list of types sent as `anyOf`, one type per branch) was installed at 22:10 UTC, and Claude has answered since 22:21 UTC: 144 calls by 23:41 UTC for $1.94, about 2 cents a trading step, so the run costs about $35 (`CALCULATED`) and ends around the evening of 2026-11-06 (UTC). The report's second run and M5 were written and tested on 2026-11-06, before it ends ([§4.8](plans/0055-backtest-claude-on-the-same-history.md#48-the-report-and-the-page)): the report reads one or both runs' exports, runs the window again from the stored answers with every step checked, and prints each run's measures, the family's readings and M5; a run still running is read `INTERIM`. It finished on 2026-11-06 at 18:55:37 UTC for $37.57 calculated from its tokens ($37.97 counted against the cap), and was read on 2026-11-07 from read-only exports, every stored step rebuilt and matched ([§13](plans/0055-backtest-claude-on-the-same-history.md#13-progress); the results page): Claude's simulated account ended at 9,197.42 USDT (−8.0%, `MODELED`), its 195 trades about even before costs (−94 USDT) and 709 USDT of fees; M1 `LOSES_MONEY`, M2 `UNCLEAR`, M3 `TRAILS_RULE` (the gated trend rule +2.5%, holding BTC −2.1%), M4 `NO_DIFFERENCE`; M5 against ChatGPT `NO_DIFFERENCE`, INTERIM until the ChatGPT run ended; final on 2026-11-12 over the 784 hours both answered, the two calling the same direction 83% of the time ([§13](plans/0055-backtest-claude-on-the-same-history.md#13-progress)). Nothing in the app changes.
- **Backtest the trader's latest design** ([ExecPlan 0056](plans/0056-backtest-the-traders-latest-design.md), the owner's questions of 2026-11-07 15:32 and 15:34 UTC, "why next hour? Should the longs and shorts be based on events?" and to make sure the backtest includes the latest changes, and the pick "Claude, about $25 (cap $40)" at 15:42:46 UTC, [DECISIONS](../DECISIONS.md#2026-11-07--backtest-the-traders-latest-design-on-claude-on-a-claude-api-key-execplan-0056)): the live design, generation 14's trader every four hours and on events with its scores, the trade reviewer, the daily decision reviewer and the coach, replayed on the same two masked months for one simulated account, asked of Claude in a third run after 0055's, ahead of the ChatGPT backtest. Every block is built by the live code's own functions (split into their reads and pure parts), and the run is tied to the live design by code: a fingerprint of the live templates, prompts, rules and modules, frozen in generation 18, must equal the installed code's before any call, or nothing starts. Graded 4 hours out (the decisions' own spacing) and on P&L after costs, against holding BTC, the gated trend rule, the last-4-hours rule and 0055's hourly run, pre-registered before any code (a third trial, a pass at 279/280). Cap $40 of the owner's credit (CALCULATED, rough: about $25 and 8 to 12 hours). Generation 18, migration `0037`. Built and tested in the cloud on 2026-11-07 ([§13](plans/0056-backtest-the-traders-latest-design.md#13-progress)); two gaps that would have held the run at the date mask were found before any spending and are fixed: a field-by-field check against the live database reads found the first (a coach's citation of a scorecard row or a day's review), and a dry run over the whole two months the second (a trade closed in the archive's missing days, near the end); four whole-window sweeps found no other. An independent review found no defect on a money path; its two findings are fixed (the design guard now covers 37 live files and the twin set, and a held run stays held for the worker's process). Installed on the owner's PC on 2026-11-07 (update `update-20261107T224927Z`, `8c8083c`, schema `0037`) and checked read-only on 2026-11-08 ([§13](plans/0056-backtest-the-traders-latest-design.md#13-progress)): the run started at 23:09 UTC with the design guard passing and by 03:39 UTC had answered 312 steps, half the window, for $9.97 counted against the cap (the provider's cost a workflow $0.027 to $0.048). The Claude API then refused its calls at the spend limit of the owner's Anthropic organization, at no cost, until the owner raised the limit; it went on at 09:40 UTC. The report's third run (M1 to M4 at 4 hours, M6 against the hourly run and the family of fourteen) was written and tested on 2026-11-08, before the run ends. It finished on 2026-11-08 at 13:38 UTC for $19.38 counted against the cap (652 calls, 6 of them refused at the spend limit at no cost) and was read the same day from read-only exports, all 586 stored steps rebuilt and matched ([§13](plans/0056-backtest-the-traders-latest-design.md#13-progress); the results page): the simulated account ended at 9,956.91 USDT (−0.4%, `MODELED`) after 7 trades in 456 decisions (449 holds), with 26 USDT of fees against the hourly run's 709; M1, M2 and M3 `UNCLEAR`, M4 `NO_DIFFERENCE` (its calls 4 hours out and the last-4-hours rule each right 47% of the time beyond the band) and M6 `UNCLEAR` (above zero at 95%, not at the family's 99.64%), each as the plan expected before the run. The family's ChatGPT column was read final on 2026-11-12, on that run's 32 days: M1 `LOSES_MONEY`, M2 `UNCLEAR`, M3 `TRAILS_RULE`, M4 `NO_DIFFERENCE`, and M5 `NO_DIFFERENCE` ([§13](plans/0056-backtest-the-traders-latest-design.md#13-progress)). Nothing in the app changes.
- **The event calendar** ([ExecPlan 0058](plans/0058-the-event-calendar.md), the owner's "yes do everything now" of 2026-11-09 15:22 UTC, [DECISIONS](../DECISIONS.md#2026-11-09--the-event-calendar-execplan-0058)): generation 19's trader (`FUTURES_DECISION_V7`, migration `0039`) is generation 14's with a calendar in code: no new entry from 240 minutes before the US CPI, the US jobs report or a Fed statement to 45, 30 and 120 minutes after it, refused at the finish and closed while the calendar cannot be read, and one more decision once each window ends (`RELEASE_OUT`); exits, tighter stops, holds and the engine's protection are unchanged. Home says when entries are closed; Settings shows the next window. Built and checked in the cloud on 2026-11-09 ([§14](plans/0058-the-event-calendar.md#14-progress)); installed with 0059 on 2026-11-10, where the slow rule replaced the trader at once, so generation 19 decided nothing live.
- **The slow rule trades the main account** ([ExecPlan 0059](plans/0059-the-slow-rule-trades-the-main-account.md), the owner's pick "Plan the slow rule for the main account" of 2026-11-10 14:35:46 UTC and "Approve the plan" at 15:05:57 UTC, then "I don't want to wait until everything completes november 15" at 15:08:23 UTC; [DECISIONS](../DECISIONS.md#2026-11-10--the-slow-rule-trades-the-main-account-execplan-0059)): `FUTURES_POLICY_V2` names `MAIN_RULE_V1`, code, as the main account's decider: once a UTC day it holds the perpetual long, never short, at most 1x, sized to a 5% a year volatility target by Bitcoin's daily close against its closes 30, 91 and 365 days earlier, or stays flat. The trader, its reviewers and the coach are no longer asked; the veto agent still answers its twin; the ChatGPT backtest (0052) ends `TRADER_REPLACED` at the install. The switch ends the trader's run at the first flat finished bar (`NEW_POLICY`) and starts the rule's run with its own high-water NAV; nothing of the ledger is wiped. Migration `0040`. Built and checked in the cloud on 2026-11-10, with an independent money-path review (no blocker; its three fixes built: a stopping run closes the rule's position at once) ([§13, §14](plans/0059-the-slow-rule-trades-the-main-account.md#14-progress)); it shipped with 0058 in one update, installed on the owner's PC on 2026-11-10 (the update of 17:24 to 17:30 UTC, `COMPLETE` on `93a2112`), in force since 17:30:01 UTC (OBSERVED): the trader's run #1 stopped `NEW_POLICY`, the rule's run #2 started by `SYSTEM`, the first reading `FLAT` (`NO_CHANGE`), the ChatGPT backtest `TRADER_REPLACED`.

- **A slow trend twin** ([ExecPlan 0057](plans/0057-a-slow-trend-twin.md), the owner's question of 2026-11-07 19:15 UTC, "What is a good profitable strategy that the app is missing?", and "decide whats best and go ahead" at 21:00 UTC, [DECISIONS](../DECISIONS.md#2026-11-07--a-slow-trend-twin-execplan-0057)): a sixth isolated paper twin, `TREND_SLOW` (`TWIN_SET_V3`, migration `0038`), holds long or short once a UTC day by Bitcoin's daily close against its closes 30, 91 and 365 days earlier, sized to a 40% a year volatility target at most 2x; the feed stores Binance's 1-day candles for it; its measure against holding Bitcoin is written before its first bar. Installed on the owner's PC on 2026-11-08 (the update of 09:01 to 09:10 UTC, `9f24174`, schema `0038`) and checked read-only at 09:21 UTC ([§14](plans/0057-a-slow-trend-twin.md#14-progress)); the twin started at 09:07 UTC, and its first daily reading, on 2026-11-09 at 00:15 UTC, went short a third of its wallet at 1x. Its measure is first read by the weekly review after 90 days.
- **The trader every four hours and on events** ([ExecPlan 0053](plans/0053-the-trader-every-four-hours-and-on-events.md), the owner's question of 2026-11-03 11:14 UTC, "is there a better practice to handle the decisions instead of checking every 15 minutes ?", the answer "yes, using the trading.md file, implement using best practices for our app" and the card's pick "Live as soon as it's built" at 11:51 UTC; [DECISIONS](../DECISIONS.md#2026-11-03--the-trader-every-four-hours-and-on-events-execplan-0053)): generation 14's trader decides at 00, 04, 08, 12, 16 and 20 UTC and at once on an event (a closed trade's cooldown ending, a move of 4 × the 15-minute ATR since its last decision, the first hourly close beyond the last 24 hours' range, a funding change of 0.01 points), at most 32 a day: about 8 to 9 decisions a day instead of about 100, with code's protection every second as before. Migration `0033`. The measure is pre-registered in [§4.5](plans/0053-the-trader-every-four-hours-and-on-events.md#45-the-measure-pre-registered). Installed on the owner's PC on 2026-11-03 at 15:28 UTC (`update-20261103T152357Z`, `22ab71a`) and checked read-only: the agents' check passed on the profile naming generations 1 to 15. Generation 11's run of the trader ended with its 15:00 bar decision. O1 passed on 2026-11-07: 11, 9 and 6 decisions on 2026-11-04 to 11-06, every four-hour moment on time, one trade (a short closed at its take profit) ([§14](plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress)). Its run ended when ExecPlan 0059 stopped asking the trader (last decision 2026-11-10 16:00 UTC), and M1 was read descriptively on 2026-11-12, short of its sample: 56 decisions, 39 of 120 decisive, paired −0.036% an hour against the last-hour rule, 95% −0.117 to +0.023, no verdict; generation 11's whole run, read the same day, +0.010% an hour, 95% −0.023 to +0.045 ([§14](plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress), [TRADING](../TRADING.md#the-record-so-far)).
- **The scorer expects the schedule, and a second usage-limit signal** ([ExecPlan 0054](plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md), the owner's pick "Small fixes now" of 2026-11-03 19:42 UTC after the agents' setup review, [DECISIONS](../DECISIONS.md#2026-11-03--small-fixes-now-the-scorers-expected-bars-and-a-second-usage-limit-signal-execplan-0054)): `DECISION_SCORING_V2` (migration `0034`) expects a decision at a finished bar only at generation 14's four-hour moments, where V1 read about 88 bars a day as missed, and a Codex usage reading that names a reached limit sets the usage-limit block a refused call sets. The trader is unchanged and its paired test keeps running. Installed on the owner's PC on 2026-11-03 at 22:11 UTC (`update-20261103T220638Z`, `0cd1ba0`; run again on the same commit on 2026-11-04 at 07:20 UTC) and checked read-only on 2026-11-04 at 08:12 UTC: V2 stored and in force, every score since names V2, and the only bars it expects are the four-hour moments, each decided ([§14](plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md#14-progress)).
- **Faster market-data cleanup** ([ExecPlan 0038](plans/0038-faster-market-data-cleanup.md), the owner's "yes" of 2026-10-23 09:06 UTC after "Market data unavailable" at 08:13 UTC): the hourly cleanup's slowest calls reach 1.9 s of their 2 s deadline (68 failed calls in seven days, each retried), because its search for unused raw payloads examines every expired payload in every call. A migration `0017` searches only where orphans can be and indexes five references; each `QUEUE_OVERLOAD` feed drop records which database call was slow. **Approved** by the owner on 2026-10-23 09:13 UTC; built, checked on an isolated database and **installed** on the PC on 2026-10-23 (`890ba30`, schema `0017`; the first pass's slowest call 704 ms against 1.0 to 1.4 s before, [0038 §12.3](plans/0038-faster-market-data-cleanup.md#123-installed-on-the-pc)).
- **Clear values in local time** ([ExecPlan 0037](plans/0037-clear-values-in-local-time.md), the owner's ask of 2026-10-22 11:59 UTC, [DECISIONS](../DECISIONS.md#2026-10-22--the-owner-asks-for-clear-values-in-local-time-execplan-0037)): one format for each kind of value (USDT to the cent, prices to five significant digits, quantities exact with their coin, percentages from the exact fraction), and every time in the browser's own time zone with UTC on hover, the charts' time labels included. The web only: no migration, no money path, no new dependency. Built and checked in the cloud; **installed** on the PC on 2026-10-22 (`8b5b898`, record `COMPLETE` at 20:11 UTC, [0037 §12](plans/0037-clear-values-in-local-time.md#12-progress)).
- **A clear, beautiful app** ([ExecPlan 0036](plans/0036-a-clear-beautiful-app.md), the owner's ask of 2026-10-22 07:40 UTC, [DECISIONS](../DECISIONS.md#2026-10-22--the-owner-asks-for-a-clear-beautiful-app-execplan-0036)): the same five pages in a sidebar app shell with a tab bar on phones, a light and a dark theme, Home led by the trading status and the account's value, states with an icon and a word, numbers lined up, limits drawn as bars, rising candles hollow. The web only: no migration, no money path, no new dependency. Built and checked in the cloud; **installed** on the PC on 2026-10-22 (`bfbe829`, record `COMPLETE` at 11:11 UTC, [0036 §12](plans/0036-a-clear-beautiful-app.md#12-progress)).
- **A simpler app that trades by itself** ([ExecPlan 0035](plans/0035-a-simpler-app-that-trades-by-itself.md), the owner's ask of 2026-10-21 06:29 UTC, [DECISIONS](../DECISIONS.md#2026-10-21--the-owner-asks-for-fewer-pages-and-no-research-execplan-0035)): five pages (Home, Trades, Decisions, Markets, Settings), research switched off in the agent worker, and the research containers retired by the update file. No migration. Built and tested in the cloud, with an independent review of the update file's new stage; **installed** on the PC on 2026-10-21 with M10's runner fix (`7440a89`, record `COMPLETE` at 11:11 UTC): the three research containers and their network removed, their data volume kept, the seven pages answering, nothing of research open or new ([0035 §12](plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress)). Nothing of it is left: the routes no page calls and M6's unused research code and tables go with the cleanup's part 3.
- **The cleanup** ([ExecPlan 0034](plans/0034-app-cleanup.md), the owner's go-ahead of 2026-10-20):
  1. part 1, the Docker clean-up file `docker-cleanup.cmd`: **run** by the owner on 2026-10-20 (Docker's disk 316 GB to 58 GB, 33 old backups and 195 old images removed);
  2. part 2, the code, scripts and documents: **installed** on 2026-10-20 (`62af44c`);
  3. part 3, the contract documents and the API file's layout: after M10's update 2 and ExecPlan 0035, with the routes no page calls since 0035 ([API_CONTRACTS](contracts/API_CONTRACTS.md#five-pages-routes-the-web-no-longer-calls-execplan-0035)).

### Open follow-ups

- [ExecPlan 0060](../plans/0060-spot-trading-only.md), `APPROVED` by the owner on 2026-11-12 at 10:19:26 UTC ([DECISIONS](../DECISIONS.md#2026-11-12--spot-trading-only-execplan-0060-m12)), on the ask of 09:59:43 UTC ("let's completely switch to spot trading and remove the futures completely"): M12, spot trading only, by the slow rule long or cash, with the app's own backtest of it; the build is in progress.
- [ExecPlan 0059](plans/0059-the-slow-rule-trades-the-main-account.md), `APPROVED` by the owner on 2026-11-10 ([DECISIONS](../DECISIONS.md#2026-11-10--the-slow-rule-trades-the-main-account-execplan-0059)): the main account would follow the slow trend rule, never short, at most 1x, sized to a 5% a year volatility target, instead of the AI trader. Built on 2026-11-10 (above): the owner's words at 15:08 UTC replaced the wait, so it ships with 0058 in one update and 0052's backtest ends at the install.
- From M7: the first live decision cycle and the walk-throughs of [ExecPlan 0026 §13.4](plans/0026-m7-agent-driven-main-decisions.md#134-the-live-walk-through) and [ExecPlan 0023 §13.3](plans/0023-m6-research-investigations.md#133-the-live-walk-through); M7-OD7's partial reduction; M7-OD5's selector, shadows and ablations.
- From M8: the agent's own entry-pause end and early lift, and promoted candidates as an entry basis, which need new agent definitions ([ExecPlan 0031 §14](plans/0031-m8-simple-app-that-runs-itself.md#14-decision-log)).
- From M9: what [ExecPlan 0032 §8](plans/0032-m9-news-and-events-the-agents-trade-on.md#8-not-in-m9) leaves out (web search, SEC filings, consensus forecasts, a no-entry window before releases), and the first investigation of a feed item or a price move on the PC. None has run yet (OBSERVED read-only on 2026-10-20 at about 21:50 UTC): the day's one matching feed item (the BLS numbers, 14:12 UTC) and its sharp moves (BTC and SOL about 3 hourly ATRs in 15 minutes, 14:07 to 14:15 UTC) came while the owner's Codex allowance was used up, so the item's two triggers were refused as `STALE` and no move was recorded, as designed. From 18:06 UTC, when the agents worked again, to 21:53 UTC the largest 15-minute moves were 0.26 % (BTC) and 0.64 % (SOL), and no `PRICE_MOVE` trigger was recorded.
- From M10: news and price-move investigations for ZEC, NEAR and XRP (generation 4's investigation and its `PRICE_MOVE_V1` rule name BTC and SOL only, so these need a later generation; the hourly decisions already see all five coins), and hourly candles for the watchlist coins the app does not trade ([0033 §13](plans/0033-m10-the-agents-look-beyond-btc-and-sol.md#13-decision-log)).

## Until ExecPlan 0031 (2026-10-19)

Entries up to 2026-10-19, newest first, as [STATUS.md](../STATUS.md) held them until [ExecPlan 0031](plans/0031-m8-simple-app-that-runs-itself.md) put the current state on one screen. Kept unchanged as the record.

**M8's plan: the owner picked "Cut to essentials" on 2026-10-19 at 11:37:19 UTC, so [ExecPlan 0031](plans/0031-m8-simple-app-that-runs-itself.md) is approved for implementation and the fast lane ([ExecPlan 0029](plans/0029-fast-lane-pc-runs.md)) is withdrawn. Documents only; nothing built or deployed, and M7's run is unchanged.** By the project thread "Hands-off milestones" ([DECISIONS](../DECISIONS.md#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)).
- **The plan:** the app keeps five protections (paper only; code-made fills at market prices in an exact ledger; hard limits and stops; version tags; an off switch) and does every other owner step itself, recorded as `SYSTEM`. M8 arrives as a documents-only part that changes the rules, then three updates, each one double-click for the owner: the update file, with agents that check themselves and resume after a usage limit; in-force records instead of approvals, with pauses that clear themselves; one continuous run, starting with `AGENT_POLICY_V2`. [ExecPlan 0030](plans/0030-agent-models-and-effort-per-role.md) keeps its model table and usage-limit block, without the profile approval.
- `NOT RUN`: all of it.

**M7 is closed by the owner's decision: the boundary and M7-B ran, run `a8b3ae07` is `RUNNING` on `AGENT_POLICY_V1` and the agents are enabled; the decision probes and the first live decision are follow-ups, because the owner's Codex usage ran out during the switch-on (2026-10-19). The same words are read as closing M6 too, its live walk-through a follow-up (an interpretation the owner can overrule, [DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)). Records only; every step on the PC was the owner's, started by double-click or pressed in the application, and checked read-only by the PC session.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `b7d51a6`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-boundary-m7-b-and-m7s-close-2026-10-19), [DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision), [COMMANDS](COMMANDS.md#execplan-0026-the-boundary-and-m7-b-2026-10-19).
- **The boundary** (OBSERVED on the owner's PC): `tools/pilot-deactivate.ps1` exited 0 at 10:16:24 UTC and `tools/m7-boundary.ps1` at 10:17:59, from `09f4490`. The pilot's workers stopped and their identities lost their login; the execution and evaluation workers, `pilot-admin` and `migrate` were built from `09f4490`, each computing the running `api`'s code identity (the market worker, which the boundary never builds, is unchanged by design); `AGENT_POLICY_V1` and `EVALUATION_PROTOCOL_V2` were installed and the script's checks passed. The account holds the pilot's dust only (BTC 0.00000484, SOL 0.002321).
- **M7-B** (OBSERVED in the application's database): the owner approved `AGENT_POLICY_V1` (`cf2519333007…`) at 10:58:59 UTC and `EVALUATION_PROTOCOL_V2` (`55340dff5e17…`) at 10:59:06, drafted experiment `a8b3ae07-0fe8-40b7-a59f-1a485c3dda43` at 11:03:43 and approved its manifest (`b74dbf62…`) at 11:04:30. The owner pressed Start at 11:06:05 and Enable at 11:06:34; `tools/pilot-activate.ps1` exited 0 at 11:07:13, its workers started at 11:07:10. The run read `RUNNING` at about 11:16:40, after the new execution worker had replayed the 51 minutes of publications since the pilot's workers stopped (10:16:18), deferring the start at each step; the runtime reads `ENABLED`.
- **Follow-ups, by the owner's decision of 11:18 UTC:** the decision probes, which did not run (the Agents page offers them once the run is `RUNNING`, and by then the usage was used up), so no decision workflow can start yet; then the first live decision cycle and the walk-through of [§13.4](plans/0026-m7-agent-driven-main-decisions.md#134-the-live-walk-through); M6's walk-through ([ExecPlan 0023 §13.3](plans/0023-m6-research-investigations.md#133-the-live-walk-through)). Since Enable, three workflows (two `EVENT_INVESTIGATION_V1`, one `RESEARCH_V1`) ended `FAILED` with `PROVIDER_UNAVAILABLE`, INFERRED to be the usage limit; nothing traded (OBSERVED at 11:15 UTC), and no decision workflow can start.
- **Closed with it:** M5's remaining follow-up, the live token refresh, was observed at 08:26:57 UTC ([§18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-passes-on-m7-g1e-and-research-is-switched-on-2026-10-19)).

**M6-B's gate and activation on the M7 build are done: gate run `m7-g1e` passed on `09f4490`, the M7 release runs on that commit, inert, and research is switched on; the capability probes passed on the new runtime profile at the fourth attempt (ExecPlan 0026 §18, 2026-10-19). Records only; the PC's steps were started by the owner and reported by the PC session.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `66951e3`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-passes-on-m7-g1e-and-research-is-switched-on-2026-10-19), [COMMANDS](COMMANDS.md#execplan-0026-the-gate-passes-the-release-and-research-on-2026-10-19).
- **The gate** (OBSERVED on the owner's PC): `Build`, `ResearchRunner`, `Staging`, `DecisionSaturation` (22:43 UTC) and `PilotCoexistence` (00:08 UTC) `VERIFIED`; `PerformanceResearch` counts from `m7-g1d` and `m7-g1a` by the owner's decision. `DecisionSaturation`: 36 of 36 decisions and 4 of 4 briefs, decision p95 16.8 s; engine step p95 310 ms; jobs of 407 s and 705 s; no failure line in the runner's or the bridge's log.
- **The release** (OBSERVED on the PC): the rollback `COMPLETE` at 00:23 UTC; the deployment from `09f4490` `COMPLETE` at 05:33 UTC (schema `0009`, lease epoch 8, no policy installed, the runtime `LOGIN_REQUIRED`); `tools/research-activate.ps1` exit 0 at 06:12 UTC. At 06:12 UTC every application service ran on the `09f4490` images, and the pilot's three workers ran as before; they keep running until the boundary. From 00:23 to 05:27 UTC the application ran the M6-A release with research off, because the PC's release file stopped after the rollback (INFERRED from the two records; nothing ran in between).
- **After research on** (OBSERVED by read-only checks on the PC, reported by the PC session): the research envelope reads approved and the evidence sources ready; research sealed its first dataset at 06:49 UTC. The owner composed and approved runtime profile `9a7e664d9186` (`gpt-6.1-sol`, `medium`) at 08:25 UTC and allowed probes (`PROBE_ONLY`). Capability run 2 (08:26:55 to 08:32:04 UTC) `FAILED` on the owner's Codex usage limit (every probe that calls the model ended `PROVIDER_UNAVAILABLE`; the cause is the owner's word). Runs 3 and 4 each failed one probe of 22, CP-01 (the model abstained on fresh data) and CP-20 (a step rejected `SCHEMA_INVALID` twice), each passed in the other run. **Run 5 `PASSED`** all 22 probes at 09:14:04 UTC (41 of 70 calls); the runtime reads `PROBE_ONLY` without a latch. Its step latency (p95 17.8 s, maximum 22.6 s) fits the policy's and the budgets' times, so nothing changes before the boundary. The pilot reads `COMPLETED` (since 2026-10-18 20:21:35 UTC).
- `NOT RUN`, each the owner's: the live walk-through of [ExecPlan 0023 §13.3](plans/0023-m6-research-investigations.md#133-the-live-walk-through); the boundary, M7-B and the first live decision. A browser check of the pages after the deployment was not reported; only the script's readiness check ran.

**Agent models per role: the owner delegated the choice of model and reasoning effort to the implementer and asked for no model picker (2026-10-19); recorded as [ExecPlan 0030](plans/0030-agent-models-and-effort-per-role.md), PROPOSED for M8. Documents only; nothing deployed, M7 and its profile unchanged.** By the project thread "Agent setup and best models", on branch `claude/agent-model-review-vxjw87` from `main` at `66951e3`. Evidence: [DECISIONS](../DECISIONS.md#2026-10-19--the-owner-delegates-the-agents-model-choice-no-profile-change-during-m7s-switch-on), [REFERENCES](contracts/REFERENCES.md#model-and-effort-guidance--2026-10-19), [COMMANDS](COMMANDS.md#agent-models-and-effort-per-role-documentation--2026-10-19).
- **Found (OBSERVED in code at `66951e3`):** one model and one effort for all four roles (`app/agents/profile.py:84`, `orchestrator.py:92`); `gpt-6.1-sol` at `medium` is the vendor's documented default and the right single setting, chosen on 2026-10-02 without a measurement. The vendor's guidance differs by task (review high, judgment medium, extraction low), which the profile cannot express. The role prompts and the invocation follow the vendor's prompting and caching guidance. Tokens per call are stored (`runner/jsonl.py:17-18`, `agent_provider_details.jsonl_summary`) and summed nowhere.
- **Found (OBSERVED by the owner, 2026-10-19 08:37 UTC):** the first M7 capability run failed on the Codex usage limit, which the agents share with the owner's own Codex use; the app's usage-limit pattern is unverified (`runner/jsonl.py:98-104`), so the refusal failed the probes and latched the runtime instead of blocking until the reset. Build M7 keeps the fix out of M7; ExecPlan 0030 §4.5 carries it.
- **Proposed for M8:** a code-owned table (`gpt-6.1-sol` for every role, `high` for the evaluator, `medium` otherwise, with fallbacks per role), the app composing the profile from it, the picker removed, a token summary, the usage-limit block, and the comparisons that must precede any change of default. `NOT RUN`: all of it.

**M6-B on the M7 build: `PerformanceResearch` met every judged figure on `m7-g1d` before the pilot watch stopped it in its staging part; by the owner's decision it counts from that run and `m7-g1a`'s staging figures. The watch then stopped `m7-g1e` after its `Build`, and by the owner's second decision the pilot stops before the gate's remaining phases, which run without the watch; `ResearchRunner` and `Staging` have passed since (ExecPlan 0026 §18, 2026-10-18). Documents only; nothing deployed or run against the normal application by this session; the pilot's stop is the owner's, in the app.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `07d4e72`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#performanceresearch-on-m7-g1d-stopped-by-the-pilot-watch-2026-10-18) and [its next subsection](plans/0026-m7-agent-driven-main-decisions.md#m7-g1e-stopped-too-and-the-pilot-stops-first-2026-10-18), [DECISIONS](../DECISIONS.md#2026-10-18--performanceresearch-counts-from-two-gate-runs-its-job-figures-from-m7-g1d-its-staging-figures-from-m7-g1a).
- **`PerformanceResearch` on `m7-g1d`** (OBSERVED on the owner's PC, 16:07 to 19:18 UTC, on `595e5aa`): every measured job `VALID` inside 3,600 s, the 21-day full test run to completion in 1,216.1 s; idle dispatch p95 4,810.1 ms against 5,000; every projection to 14 and 21 days inside 3,600 s, the shadow advance over 21 days at 3,487.4 s (3,781.4 s on `m7-g1a`). At 19:14:59 UTC, in the staging part, the normal market worker recorded a `QUEUE_OVERLOAD` and a collection gap, and the watch stopped the run; the staging rate was not measured. The pilot held its lease, with no `PROTECTION_UNAVAILABLE` row; five retention failures and three recoveries from 15:57 UTC. The phase wrote no record; its parts name no problem before staging, which the thread reads as the owner's condition met; the owner was told, and the update and research on go ahead on it unless the owner says otherwise.
- **Decided** (the owner, 19:31 UTC): no `PerformanceResearch` on `m7-g1e`. Its staging figures come from `m7-g1a` (2,266 rows/s, largest batch 481 rows), whose staging measurement is unchanged since and whose product staging differs only in two reads that run once and a field of a log line.
- **`m7-g1e`** (OBSERVED on the PC, on `09f4490`): the owner's watch from 19:30:56 UTC; `Build` `VERIFIED` at 19:32 UTC. At 19:32:21 UTC, as `ResearchRunner` started, a second `QUEUE_OVERLOAD` of the normal market worker; the watch stopped the run at 19:36:02 UTC, and the run is kept for a retry. Without the watch, `ResearchRunner` ran again from 20:17:37 UTC and was `VERIFIED` at 20:22, and `Staging` at 20:26 UTC. `NOT RUN` yet: `DecisionSaturation` and `PilotCoexistence`, then the application update and research on, from a release file the owner started at 20:31 UTC.
- **Decided** (the owner, 20:16 UTC): the owner said they were stopping the pilot in the application, and `m7-g1e`'s remaining phases run without a pilot watch; the pilot's workers keep running until the boundary, because a deployment refuses without them ([DECISIONS](../DECISIONS.md#2026-10-18--the-pilot-stops-before-the-rest-of-the-m7-gate-which-runs-without-the-pilot-watch)). The pilot's checkpoint report is written at this date. NOT OBSERVED here: when the pilot read `STOPPED` and `COMPLETED`, and whether its account is flat (2026-10-19: no experiment was open at 05:27 UTC; the flat account is inferred in [§18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-passes-on-m7-g1e-and-research-is-switched-on-2026-10-19)).

**M6-B on the M7 build: the gate run `m7-g1d` failed `DecisionSaturation` on one log line, a lease renewal that waited 2 s behind its job's batch and was asked again; a renewal now waits up to 5 s (ExecPlan 0026 §18, 2026-10-18). Product code and tests; not run on Docker; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `595e5aa`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1d-a-renewal-behind-a-slow-batch-2026-10-18), [COMMANDS](COMMANDS.md#execplan-0026-the-gate-run-m7-g1d-and-its-fix-2026-10-18).
- **The gate run** (OBSERVED on the owner's PC, 2026-10-18, 11:17 to 13:43 UTC, on `595e5aa`): `Build`, `ResearchRunner` and `Staging` `VERIFIED`; `DecisionSaturation` `FAILED` on one line of the research runner's log, with every other part passing: the agents, the policy engine, all three jobs `SUCCEEDED` (670 to 685 s), and staging beside a long job, shown for the first time. The line: the job's lease renewal timed out after its 2 s lock wait behind a batch that held the job's row, and was asked again; the job succeeded. The pilot beside it held its lease, with no collection gap; it logged two `PROTECTION_UNAVAILABLE` rows during `Build` and `ResearchRunner`, under the watch's stop limit, and one retention failure.
- **The fix.** The renewal waits up to 5 s for that row, a third of the lease, in its own transaction; every other statement keeps 2 s. A job's end waits for its renewal thread longer than one renewal can wait. A test reproduced the PC's error before the fix and passes with it.
- **The rerun, under the owner's go-ahead of 14:34 UTC** ([DECISIONS](../DECISIONS.md#2026-10-18--the-owners-go-ahead-to-speed-up-m7-and-the-gates-rerun-on-the-renewal-fix)): run `m7-g1e` on the merged commit with `Build`, `ResearchRunner`, `Staging`, `DecisionSaturation` and `PilotCoexistence`; `PerformanceResearch` stands from `m7-g1d` if it passes there. Then the application update and research on, with no further word from the owner. `NOT RUN`: all of it on the PC.

**M6-B on the M7 build: the gate run `m7-g1c` failed `DecisionSaturation` on a report that could not sort a position with no fill yet; fixed (ExecPlan 0026 §18, 2026-10-18). Product code and tests; not run on Docker; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `9917639`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1c-a-report-with-an-entry-not-yet-filled-2026-10-18), [COMMANDS](COMMANDS.md#execplan-0026-the-gate-run-m7-g1c-and-its-fix-2026-10-18).
- **The gate run** (OBSERVED on the owner's PC, 2026-10-18, 07:25 to 09:43 UTC, on `9917639`): `Build`, `ResearchRunner` and `Staging` `VERIFIED`; `DecisionSaturation` `FAILED`. Its agent load, policy engine and staging passed, with no staging error; each of its three finished jobs failed its holdout cell with a `TypeError` after 579 to 628 s, so none ran past the staging watch's 660th second. `PerformanceResearch` and `PilotCoexistence` `NOT RUN`. The pilot beside it stayed clean. Before it, `m7-g1b`'s database log showed its staging error was the read the 20 s bound covers (OBSERVED).
- **The cause and the fix.** A sealed dataset ends just after the last hour's final candle; the held candidate enters on it, and the holdout cell's report then held a position with no fill beside filled ones and sorted them on a naive bound against aware times (`app/evaluation/metrics.py`). It sorts on an aware bound now, with a test that failed before. Forward runs build their snapshots the same way, so one taken between an accepted entry and its fill could have failed too (INFERRED). A failed research attempt's log line also names the engine line it was raised at.
- **Checked in the cloud** (not acceptance evidence): a full job through the runner on the store's layout ran all six cells on a window set by hand; on the window the bridge seals, its holdout cells (the others left out) failed the same way at the same cell and pass with the fix. A feeder job is now INFERRED to run about 660 to 720 s on the PC, close to the 660 s the watch needs. `NOT RUN`: the gate's phases on the PC.

**Owner idea recorded: agent roles and a Coordinator agent — 2026-10-18; documentation only, application NOT IMPLEMENTED by this update.** At the owner's request, [a note](ideas/agent-roles-and-coordinator.md) quotes the idea, says what exists (four roles, with the COORDINATOR already deciding in the M7 build), and gives PROPOSED suggestions: evidence first in M8's agent-value report, then in M9 a fixed menu of follow-up work the coordinator may ask for, specialist analyst prompts and a read-only digest for the owner, with the evaluator kept independent. [M8](../ROADMAP.md#m8--reliability-review-sustained-evidence-and-handoff), [M9](../ROADMAP.md#m9--market-intelligence-and-event-driven-adaptive-paper-trading) and [ExecPlan 0027](plans/0027-m9-market-intelligence-and-event-driven-trading.md#5-background-agent-and-handoffs) link it. On the owner's "do it" the same day, the note gains four PROPOSED enhancements (E1–E4: mistakes as research questions, disagreement as a signal, confidence checked against outcomes, fresher inputs before more agents), with the honest frame that the structure alone does not raise accuracy and only a matched comparison can show a gain. No role, tool, grant, prompt, policy or requirement row changed; M7, ExecPlan 0026 and M7's records are untouched ([commands](COMMANDS.md#agent-roles-and-coordinator-idea-documentation--2026-10-18)). Earlier entries remain historical evidence.

**M6-B on the M7 build: the gate run `m7-g1b` failed `DecisionSaturation` on its research side; the saturation feeder's jobs are longer, and the two staging reads that run once get their own bound (ExecPlan 0026 §18, 2026-10-18). Test code, one staging change the owner chose, and the bridge's log line; not run on Docker; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `207deb7`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1b-the-saturation-feeders-jobs-and-a-staging-read-that-runs-once-2026-10-18), [COMMANDS](COMMANDS.md#execplan-0026-the-gate-run-m7-g1b-and-its-two-fixes-2026-10-18).
- **The gate run** (OBSERVED on the owner's PC, 2026-10-18, 02:24 to 04:43 UTC, on `207deb7`): `Build` and `ResearchRunner` `VERIFIED`; `DecisionSaturation` `FAILED` on its research side only, with its agent side passing on Docker for the first time (36 decisions and 4 briefs `SUCCEEDED` under the load) and the policy engine inside its budgets. No job ran long enough for the staging watch (410 to 430 s against the 660 s it needs), and the bridge logged one staging error. `PerformanceResearch` and `PilotCoexistence` `NOT RUN`. The pilot beside it stayed clean; retention failed four times and recovered twice.
- **What changed.** Every saturation job runs a candidate that holds a position nearly always, at a hold of 8 hours (test code; a whole job about twice the reference rule's time in the cloud, INFERRED about 820 to 870 s on the PC and at least about 700 s, against the 660 s needed). By the owner's answer "20 s limit" on the thread's card ([DECISIONS](../DECISIONS.md#2026-10-18--the-two-staging-reads-that-run-once-get-a-20-s-bound)): the read of a new collection and the read of where a new store version starts, which each run once and scan `market_observations` or the publications, raise their own statement bound to 20 s, and a new collection is read once instead of twice. The bridge's staging error now names its SQLSTATE. No judgment, bound of the identity, fixture size, grant or view changed.
- **Checked in the cloud** (not acceptance evidence): the six cells of a full test timed for four candidates, and a whole job's parts for two; the collection read timed (a sequential scan of 1.5 million rows, 285 to 317 ms on an idle host); the raised bound given back after the read, also after a read it canceled. `NOT RUN`: `test_m6_staging.py`'s database tests (in `Staging` on the PC) and the gate's phases.

**M6-B on the M7 build: the gate run `m7-g1a` missed one projection, and a held step is now cheaper (ExecPlan 0025 §5.9, 2026-10-18). Engine replay code and tests; not run on Docker; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `5b9987b`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1a-and-the-held-steps-cost-2026-10-17-and-18), [COMMANDS](COMMANDS.md#execplan-0025-the-constant-costs-of-a-held-step-2026-10-18).
- **The gate run** (OBSERVED on the owner's PC, 2026-10-17, 20:07 to 23:20 UTC): `Build` and `ResearchRunner` `VERIFIED`; `PerformanceResearch` `FAILED` on the shadow advance over 21 days, projected at 3,781.4 s against 3,600, with every other figure inside its bound; `DecisionSaturation` and `PilotCoexistence` `NOT RUN`. The pilot beside it stayed clean.
- **What changed.** Seven changes of the replay path that make a step with a position cheaper and leave a replay's rows identical, each with a test; the owner's card about this miss is not answered, and this is its recommended option. No bound, cap, fixture or charging changed.
- **Checked in the cloud** (not acceptance evidence): a 64-hour replay with a day held, 10% to 13% less time and 14% to 16% less CPU than `main`, with the same fingerprints. `NOT RUN`: `PerformanceResearch` on the PC, which alone judges the projection, and the gate's other phases.

**M7: `DecisionSaturation`, the M7-B activation's load check, is built (ExecPlan 0026 §10, 2026-10-17). Harness and test code only; not run on Docker; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `8a5ae8c`. Evidence: [COMMANDS](COMMANDS.md#execplan-0026-decisionsaturation-in-the-activation-gate-2026-10-17), [TESTING](TESTING.md#m7-activation-gate-decisionsaturation).
- **What changed.** `tools/m7-acceptance.ps1 -Phase DecisionSaturation`: `ResearchSaturation`'s research, stream and fetcher load and judgments, with `PerformanceEngine7`'s policy engine on its budgets and the production agent worker inside the product limits working through a UTC day's decision and brief budgets (36 decisions, 4 briefs) inside the loaded thirty minutes (`tests/m7_saturation.py`).
- **In the activation gate in place of `ResearchSaturation`,** by the owner's answer "Combined" on the thread's card ([DECISIONS](../DECISIONS.md#2026-10-17--decisionsaturation-replaces-researchsaturation-in-the-m7-activation-gate)): the gate is `PerformanceResearch`, `DecisionSaturation` and `PilotCoexistence`.
- **Checked in the cloud** (not acceptance evidence): the agent side alone, without limits or load beside it, spent the day's budgets in twelve minutes, 16 s a decision, none failed. `NOT RUN`: the phase on Docker on the owner's PC.

**M6-B on the M7 build: the M7 harness holds M6-B's three gate phases (ExecPlan 0026, 2026-10-17). Harness and documents only; none of the three has run on the M7 build; nothing deployed or run against the normal application.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `11d984a`. Evidence: [COMMANDS](COMMANDS.md#execplan-0026-after-b10-the-m6-b-gate-on-the-m7-build-2026-10-17), [ExecPlan 0026 §16](plans/0026-m7-agent-driven-main-decisions.md#16-progress).
- **What changed.** `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence` are phases of `tools/m7-acceptance.ps1`, with M6's values, as the M7 profile's activation gate: they run on a run of their own, and `Report` refuses an M7-A run that starts one. `PilotCoexistence` migrates to `0009` on that profile.
- **Checked in the cloud** (not acceptance evidence): the profile check `VERIFIED`, the four changed scripts parse and are ASCII, and the candidate refusals that phase requires answer as required on a scratch database at `0009`. `NOT RUN`: the three phases on Docker.
- **PROPOSED, `NOT RUN`, for the owner's approval in chat before the activation:** put the whole M7 release on the commit the gate passed on with the existing script, `tools/m7-deploy.ps1 -Rollback` then `tools/m7-deploy.ps1` (the sequence `BoundaryRehearsal` passed on Docker in isolation, from one tree), because `tools/research-activate.ps1` starts the images already built and the queue refuses a job whose code identity differs from the runner's. Rebuilding only the research images would make every agent's job fail. Valid only while research is off and before the boundary.
- **The report names the gate's activation.** On the M7 profile `Report` says the three phases are run for the M6-B activation (`GateActivation`), not for M7-B's.

**M7 B10: M7 deployed to the normal application switched off; B9's final run passed (ExecPlan 0026, 2026-10-17).** On the owner's `Deploy M7`, from the owner's main folder checked out at `05d8ef9`, the commit run `m7-b9c` accepted (39 of 39 phases `VERIFIED` on their first attempt, `Report` `VERIFIED`). The deployment record is `COMPLETE`: backup and restore rehearsal passed, migration `0009`, web, api and agent worker replaced, `:pre-m7` rollback tags kept, the pilot untouched and M7 inert (no policy installed, research off, decision tables empty). Evidence: [ExecPlan 0026 §16](plans/0026-m7-agent-driven-main-decisions.md#16-progress). Next: M6-B's remainder on this build ([ExecPlan 0025 §13](plans/0025-research-job-cost-and-search.md#13-decision-log)), then the boundary; every activation step waits for the owner.

**GitHub CI removed — 2026-10-17; no application change.** At the [owner's request](../DECISIONS.md#2026-10-17--github-ci-removed-from-the-repository) the GitHub Actions workflow, which never ran on GitHub, was deleted with its Dependabot configuration and its Compose override. [ExecPlan 0016](plans/0016-ci-checks.md) keeps the design and the commit to restore them from. Pull requests record their own evidence ([TESTING](TESTING.md#continuous-integration)), and contracts that asked for executed CI checks take the local harness's checks against the exact release source while no CI exists ([commands](COMMANDS.md#github-ci-removal--2026-10-17)). M7, ExecPlan 0026 and M7's records are untouched. Earlier entries remain historical evidence.

**M6-B: the research lease's renewal change, rewritten for the activation on the M7 build (ExecPlan 0025 §13, 2026-10-17). Not deployed; the job times and the activation are still owed.** By the session that builds M7, on branch `claude/m7-b0-hjaahq` from `main` at `05d8ef9`, under the owner's M7-OD10 (b) (M6-B's remainder after M7's B10). Evidence: [ExecPlan 0025 §14](plans/0025-research-job-cost-and-search.md#14-progress-and-completion-evidence).

- **What changed.** A renewal of a running research job's lease that fails without a refusal, such as a lock wait behind a batch that holds the job's row longer than 2 s, is asked again at the next tick instead of ending the renewals. A refused one still ends them. Before, one slow batch could cost a long job its lease and an attempt (`WORKER_LOST`).
- **Checked in the cloud** (scratch PostgreSQL 16, not acceptance evidence): the runner's four database-free tests and one new database test pass; the old loop fails the database test `FENCED`. `NOT RUN`: `ResearchRunner` on PostgreSQL 17 and Docker.
- **Merged after B10's deployment** (17:21 UTC), because it changes the research image and B10 deployed the commit its final run accepted. The running app does not carry it yet: `tools/research-activate.ps1` starts the images already built (`--no-build`), so a deployment of the merged code must rebuild the research image before research is switched on.

**Builder and LLM-trading findings recorded as PROPOSED M8–M10 requirements — 2026-10-17; documentation only, application NOT IMPLEMENTED by this update.** Under the [owner's instruction](../DECISIONS.md#2026-10-17--builder-and-llm-trading-findings-recorded-as-proposed-m8m10-requirements) no milestone is added. M8's roadmap entry and a [new EVALUATION section](EVALUATION.md#m8-onward-warm-up-sensitivity-and-decision-level-controls) propose an early real-candle measurement of indicator warm-up sensitivity (by calculation, the reference's EMA(50) still carries 13.5% of its seed at its 100-bar warm-up), a placebo control for entries and an exit what-if. [M9](plans/0027-m9-market-intelligence-and-event-driven-trading.md#9-requirements-mapped-to-verification) gains R25–R28 (remembered outcomes, decision repeatability, news base rates, search intensity on promotion requests) and [M10](plans/0028-m10-coin-discovery-and-controlled-expansion.md#9-requirements-mapped-to-verification) gains R17 (universe size as a declared factor). [Sources TB-01–TB-20](../REFERENCES.md#trading-bot-builder-and-llm-trading-research--2026-10-17) carry their types and limits; [evidence](contracts/INTEGRATION_EVIDENCE.md#builder-and-llm-trading-findings--2026-10-17) records what was opened. The optional measurement on Binance candles is NOT RUN: this session's network policy denied the hosts ([commands](COMMANDS.md#builder-and-llm-trading-findings-documentation--2026-10-17)). M7, ExecPlan 0026 and M7's records are untouched; no strategy, grammar, envelope, protocol or approval changed. Earlier entries remain historical evidence.

**M9/M10 readiness requirements strengthened — 2026-10-16; documentation only, application NOT IMPLEMENTED by this update.** Owner-authorized research/editing keeps the milestone order and makes existing-control closure explicit before M8 acceptance. [M9](plans/0027-m9-market-intelligence-and-event-driven-trading.md) now has R01–R24, including predecessor evidence, execution invalidation with workers down, advisory risk feasibility, measured latency/quota behavior, actual-model semantic/reviewer tests and runtime compatibility. [M10](plans/0028-m10-coin-discovery-and-controlled-expansion.md) has R01–R16, adding multi-asset verification and screening-coverage/scaled-workload tests. [EVALUATION](EVALUATION.md#future-m9m10-agent-quality-and-release-evidence) owns the new future quality protocol; [official research and limits](contracts/INTEGRATION_EVIDENCE.md#agent-readiness-refinement--2026-10-16) and [documentation verification](COMMANDS.md#agent-readiness-documentation--2026-10-16) are separate from all unrun application gates. No new agent, runtime change, activation, operational rating or profitability result is claimed. Earlier entries remain historical evidence.

**M9 refined and M10 specified — 2026-10-16; documentation only, application NOT IMPLEMENTED by this update.** [M9](plans/0027-m9-market-intelligence-and-event-driven-trading.md) now specifies active investigation/feedback, distinct assessment dimensions, token-benefit reasoning, comparable numeric features, evidence-backed working memory and outcome research, with M9-R01–R18. [M10](plans/0028-m10-coin-discovery-and-controlled-expansion.md) follows accepted/deployed M9 and separates discovery/research from controlled additional-coin paper eligibility, with M10-R01–R14. Both require a later implementation instruction. The current BTC/SOL scope, runtime/tool/source permissions and operating controls are unchanged; no new observation of the deployed app is claimed. [Documentation commands and checks](COMMANDS.md#m9m10-documentation-refinement--2026-10-16) are separate from all unrun application/provider/evaluation/deployment gates. Earlier entries remain historical evidence.

**M9 roadmap documented — 2026-10-15; application NOT IMPLEMENTED.** The owner authorized the future [M9 milestone](../ROADMAP.md#m9--market-intelligence-and-event-driven-adaptive-paper-trading) and [ExecPlan 0027 handoff](plans/0027-m9-market-intelligence-and-event-driven-trading.md). Implementation is deferred until M0–M8 are complete, M8 is accepted/deployed and M9 implementation is instructed. This is a documentation update on the current checkout, not a new observation of the deployed app or a claim that M8 is complete. No runtime settings, source grants, web-search capabilities or trading controls changed. Earlier implementation records below remain historical evidence.

**M7 B9: a fix for the final run's browser fault — the Agents page's start dialog scrolls inside a phone's viewport (ExecPlan 0026, 2026-10-17). M6's failing test has not run again yet; nothing deployed or run against the normal application; no model called.**
By the cloud session of B0 to B9d, on branch `claude/m7-b0-hjaahq` from `main` at `2508b18`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-start-dialog-on-a-phone-2026-10-17),
[COMMANDS](COMMANDS.md#execplan-0026-b9-the-start-dialog-on-a-phone-2026-10-17).
- **The fault.** B9's final run `m7-b9a` (on the owner's PC from 22:10 UTC, beside the pilot watch) failed
  `BrowserResearch` at 23:40 UTC: B8b and B8c made the start dialog too tall for M6's 390 by 700 check. That run
  cannot pass its report and goes on for the other phases' first Docker evidence.
- **Checks (`OBSERVED` in the cloud, PostgreSQL 16):** M7's `@decisions` with a new phone check failed it without
  the fix and passed `12 passed` with it; web typecheck, lint, Prettier and 248 unit tests. `NOT RUN`: M6's
  `@research` and every browser phase on Docker; they run again on the owner's PC.
- **A second fault, in the harness.** The same run's `AgentFaults6` timed out waiting for a job running: since
  ExecPlan 0025 a screening of its fault fixture ends in 3.7 s. Its fault cases now start the product runner with
  a 40 s hold before each attempt's last cell, reading the job's fence through one open session
  ([§18](plans/0026-m7-agent-driven-main-decisions.md#the-fault-runners-hold-2026-10-17)); five tests without a
  database. `NOT RUN`: the phase itself, on the owner's PC.
- **A third fault, in the boundary rehearsal's last check.** Its `BoundaryRehearsal` held in every step, the policy's
  run started and bound, but compared the started workers with the first boundary run's images while the second
  run had named others (INFERRED: a new image ID for the same build). The rehearsal now checks each boundary run's
  images, and the names before the activation, and expects the last run's
  ([§18](plans/0026-m7-agent-driven-main-decisions.md#the-boundary-rehearsals-images-2026-10-17)); verified on
  stubbed Docker. `NOT RUN`: the phase on the owner's PC.
- **The next run, `m7-b9b`, and a fourth fault, in a fixture.** `m7-b9a` ended `NOT ACCEPTED` (30 of 39). `m7-b9b`
  on the fixed build found `PerformanceApi` failing: its fixture's promotions sat on assessment workflows, which the
  promotions page, typed since B6a, rightly refuses. The fixture now gives each promotion a promotion workflow
  ([§18](plans/0026-m7-agent-driven-main-decisions.md#the-promotions-of-the-api-fixture-2026-10-17)), checked in the
  cloud on the M7 fixture's `PROMOTION_V2` workflow only. `NOT RUN`: the M6 fixture's `PROMOTION_V1` path and the
  phase on the owner's PC.

**M7 B9d: `tools/m7-boundary.ps1`, the script for the experiment boundary after the owner has stopped the pilot and switched its workers off, with a model that walks its branches, the engine's boundary check it asks, and `BoundaryRehearsal`, which runs the whole way from a running synthetic pilot to a started run of the operating policy on test containers (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; neither script nor the phase has run on Docker.**
By the cloud session of B0 to B9c, on branch `claude/m7-b0-hjaahq` from `main` at `08722b5`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9d--the-boundary-script-its-model-and-boundaryrehearsal-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b9d-the-boundary-script-its-model-and-boundaryrehearsal-2026-10-16).
- **The script** is the plan's boundary steps 2 to 4 and nothing else: a preflight that changes nothing (except the
  latch the check's reconciliation sets on a discrepancy) and names every refusal at once (a pilot worker running,
  a flag at `1`, the pilot not `COMPLETED` or not the newest forward run, a run still open or `STOPPED`, a signal
  without an outcome, a latch, a login or session, the lease, a document approved or of another hash, a checkout
  of another commit than the M7 deployment's, `DOCKER_HOST`); a backup; the four pilot images built from that
  commit, each shown to compute the API's code identity; the two
  documents installed and left unapproved; the check again. It starts, stops and approves nothing, and ends with
  the owner's next steps on the Approvals page and `tools/pilot-activate.ps1`.
- **The phase** deploys M7 beside a running synthetic pilot, takes it back and deploys it again; shows the boundary
  and the install refused while the pilot runs; stops the pilot as the owner would; runs the M4 switch-off tool, the
  boundary twice and a refused rollback; then the synthetic owner's approvals, the M4 switch-on tool and Start. The
  run must be `RUNNING` on the workers the boundary built, bound to the operating policy.
- **Checks (`OBSERVED` in the cloud, PowerShell 7.4.6 on Linux and scratch PostgreSQL 16):** the boundary and the
  activation on a scratch database with the real workers as processes, from the pilot running to the policy's run
  `RUNNING` (before the review's fixes); the model, 7 scenarios and 52 of 52 expectations, each of 24 checks shown
  to fail it when taken out; the phase on stubbed Docker with 18 faults; the engine's check, 40 database tests; M7's deploy model unchanged,
  114 of 114; ruff, OpenAPI, the database-free tests, profiles and links. An independent review found no blocker;
  its major point (an older completed run could stand for a newer stopped or failed one) and its other seven are fixed.
  `NOT RUN`: Windows PowerShell 5.1, Docker, PostgreSQL 17; the phase runs in B9's final run on the owner's PC.

**M7 B9c: `tools/m7-deploy.ps1`, the script that deploys M7 to the normal application switched off and takes it back, with a model that walks its branches; the owner chose to finish M6-B after this deployment (M7-OD10 (b)) (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; the script has not run on Docker.**
By the cloud session of B0 to B9b, on branch `claude/m7-b0-hjaahq` from `main` at `3448a96`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9c--the-inert-deployment-script-and-its-model-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b9c-the-inert-deployment-script-and-its-model-2026-10-16), [DECISIONS](../DECISIONS.md#2026-10-16--m7-od10-m6-b-finishes-after-m7-as-inert-deployment).
- **The script.** M6-A's deployment script, copied and adapted to the step from `0008` to `0009`: the same windows,
  backup, restore rehearsal, order and pilot checks; `:pre-m7` rollback tags for ten image names, the research and
  source names included; research kept inert; nothing of M7 installed or recorded and no model work, checked before
  and after; the new agent worker's start on `0009` shown by its own container's start and the lease it holds; the
  way back by the guarded downgrade, refused before any change while an M7 record exists.
- **B9 is four pull requests and one run:** B9a, B9b, B9c, then B9d (`tools/m7-boundary.ps1` and
  `BoundaryRehearsal`), then B9's final run on the owner's PC beside the pilot watch.
- **Checks (`OBSERVED` in the cloud, PowerShell 7.4.6 on Linux, a model of Docker):** 25 scenarios, 114 of 114
  expectations, each new check shown to fail the model when taken out (15 changes); the script's SQL on scratch
  PostgreSQL 16; M6's model unchanged, 76 of 76; links. An independent review found no blocker; its major point (a
  start of the replaced worker could pass for the new one's) and five minor points are fixed.
  `NOT RUN`: Windows PowerShell 5.1, Docker, PostgreSQL 17.

**M7 B9b: `MixedVersion7` rehearses M7's inert rollout from the release the normal application runs, beside a synthetic pilot: it deploys the M6-A release as the normal application received it, then the M7 web, the M7 API, a live `0009`, the earlier agent worker on `0009`, the earlier API on `0009`, the M7 release, the way back and the downgrade refused once an M7 record exists (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; the phase has not run on the owner's PC.**
By the cloud session of B0 to B9a, on branch `claude/m7-b0-hjaahq` from `main` at `c457261`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9b--the-mixed-version-rollout-beside-the-pilot-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b9b-the-mixed-version-rollout-beside-the-pilot-2026-10-16).
- **The phase.** It starts from the M6-A images the owner's PC runs (the profile's `PreM7`, by full ID from the
  read-only image check of 2026-10-16) and judges each state by the API's answers, the web's image and the
  agent workers' lease and runtime. The pilot's workers must run unchanged over the whole phase and over the
  minutes on `0009` alone. After the M7 release nothing of M7 may be installed or recorded, and research and
  sources have no login and no container.
- **Checks (`OBSERVED` in the cloud, scratch PostgreSQL 16, no workers running):** the helper against the M6-A code
  (`583a98a`) and the M7 API on two scratch databases, including `0009` under lock sampling, the M6-A worker's
  definitions check, the way back and the refused downgrade; the phase on stubbed Docker with 14 faults; ruff,
  OpenAPI, the database-free tests, profiles and links. An independent review's points are fixed or answered.
  `NOT RUN`: `MixedVersion7` on the owner's PC, PostgreSQL 17.

**M7 B9a: `PerformanceEngine7` measures the policy engine's step budget under an agent desk at about ten times the operating policy's rate, and a test database now gets 60 s to stop cleanly between phases (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; the phase has not run on the owner's PC.**
By the cloud session of B0 to B8c, on branch `claude/m7-b0-hjaahq` from `main` at `f516d9b`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b9a--the-engines-step-budget-with-agent-intake-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b9a-the-engines-step-budget-with-agent-intake-2026-10-16).
- **The phase.** Thirty minutes inside one HH:07–HH:58 window on the saturation target: the production execution
  worker bound to `AGENT_POLICY_V1` at 1 CPU and 512 MiB, judged on the existing, unchanged budget (step p95 750 ms, p99
  1,500 ms, RSS below 256 MiB, growth below 10 MiB) over every step and again over the steps with intake (R24).
  The load must happen as planned: SOL's entry accepted and filled inside the thirty minutes, every request its
  planned answer, a tightening accepted, both positions closed, 99 % of the feed's publications.
- **B9 is three pull requests and one run:** B9a, B9b (`MixedVersion7`), B9c (the deploy and boundary scripts and
  `BoundaryRehearsal`), then B9's final run on the owner's PC beside the pilot watch.
- **Checks (`OBSERVED` in the cloud, scratch PostgreSQL 16, no container limits):** the workload met the budget
  (step p95 301.94 ms, p99 326.17 ms; 31 steps with intake, p95 281.51 ms; RSS at most 64.4 MiB, growth 2.75 MiB);
  the phase's checks on stubbed Docker, 20 cases; ruff, OpenAPI, the database-free tests, profiles and links. An
  independent review's points are fixed. `NOT RUN`: `PerformanceEngine7` on the owner's PC, PostgreSQL 17.

**M7 B8c: the Agents page offers generation 3's starts (a market brief, a portfolio decision, an entry-basis request), the decision probe and the decision suite's results, and shows each generation's templates and role grants; the System page names a runtime waiting on the owner's profile approval and links to Agents, whose compose form starts from the newest approved profile (the owner's two additions of 2026-10-16) (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; nothing approved or started outside a disposable database.**
By the cloud session of B0 to B8b, on branch `claude/m7-b0-hjaahq` from `main` at `2427af2`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8c--the-agents-pages-m7-controls-and-the-owners-two-additions-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b8c-the-agents-pages-m7-controls-and-the-owners-two-additions-2026-10-16),
[FRONTEND](contracts/FRONTEND.md#m7-agents-page-and-the-runtimes-owner-step-execplan-0026-b8c).
- **Starts and probes.** Only what the API lists as the owner's to start, each with exactly its registered
  parameters (none takes a price, a quantity or text); a decision or an entry-basis request is not offered
  while no operating policy is installed. A market brief's text says a reviewed brief can lead to a decision
  that submits a trade intent. The decision probe waits for the policy installed, approved and running, and
  its dialog states what the suite does.
- **The owner's step.** "needs profile approval", then "profile approved, probes not enabled yet", each with
  a link to Agents; the compose form fills the newest approved profile's model and effort and composes nothing itself.
- **Checks (`OBSERVED` in the cloud, scratch PostgreSQL 16):** M7's browser spec on the final build, `@decisions` 12,
  `@profile` 1, `@unavailable` 1 and `@error` 1 passed, M6's `@unavailable` and `@error` 1 each; web 248 unit tests,
  typecheck, lint and build pass; 27 mutations each fail a test; an independent review's points are fixed. `NOT RUN`:
  `BrowserDecisions`, `BrowserDecisionsError` and `BrowserResearch` on the owner's PC (B9's run), PostgreSQL 17.

**M7 B8b: the owner's controls for agent-driven trading are in the web: the operating policy and its protocol apart on the Approvals page with what approving and revoking does, an entry-basis promotion approved by its hash and scope, a draft on the operating policy, the policy's action limits and the agents' entry pauses with the owner's resume on the risk page, and the stop in force and the agent's exit on the positions (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; nothing approved, installed or started outside a disposable database. The Agents page's controls and the owner's two additions of 2026-10-16 ([DECISIONS](../DECISIONS.md#2026-10-16--m7-the-owner-adds-a-clearer-runtime-label-and-a-pre-filled-profile-form)) come in B8c.**
By the cloud session of B0 to B8a, on branch `claude/m7-b0-hjaahq` from `main` at `3f1afa9`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8b--the-owners-controls-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b8b-the-owners-controls-2026-10-16),
[FRONTEND](contracts/FRONTEND.md#m7-owner-controls-execplan-0026-b8b), [API_CONTRACTS](contracts/API_CONTRACTS.md#m7-owner-routes-execplan-0026-b7).
- **Controls.** Each confirms in a dialog that states the API's consequences, sends one key, shows nothing as done
  before the API records it and resolves an unknown outcome by its key. A revocation whose permission-epoch raise
  was not seen can be sent again with the same key.
- **API.** The approvals view says what revoking the policy or its protocol does; the risk view shows the policy
  run's action limits as the engine counts them, and answers again on a database at `0008`.
- **OBSERVED in Chromium on scratch PostgreSQL 16** with the production web build: the M7 spec's 13 tests pass at
  390 and 1440 px, M6's `@unavailable` and `@error` pass; the web's 215 unit tests, lint, types and build, ruff,
  OpenAPI and 117 M7 database tests pass; each new check fails with its change taken out.
- **NOT RUN:** `BrowserDecisions` with its eleven tests on the owner's PC; M6's `@research` here (the container's
  free disk is below M6's research floor); PostgreSQL 17; the Agents page's controls (B8c). Run `m7-b8a`, B4's to
  B8a's phases on the PC beside the pilot watch, started at 13:08 UTC. Next: B8c, then B9.

**M7 B8a: the owner can read the agents' decisions in the web: each draft with what was requested, reviewed, permitted, submitted, answered and filled kept apart, the operating policies and a status row; every page and every answer of the web's server entry forbids framing; the harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; the owner's controls come in B8b. The owner chose to end the pilot early, once M7-A is deployed and probed (M7-OD2 (b), [DECISIONS](../DECISIONS.md#2026-10-16--m7-od2-the-pilot-ends-early-once-m7-a-is-deployed-and-probed)).**
By the cloud session of B0 to B7, on branch `claude/m7-b0-hjaahq` from `main` at `50aa702`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b8a--the-decision-pages-and-the-frame-policy-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b8a-the-decision-pages-and-the-frame-policy-2026-10-16),
[FRONTEND](contracts/FRONTEND.md#m7-decision-and-policy-pages-execplan-0026-b8a), [INTEGRATION_EVIDENCE](contracts/INTEGRATION_EVIDENCE.md#m7-b8a-decision-pages-and-the-frame-policy--2026-10-16-execplan-0026).
- **Pages.** `/decisions` lists the drafts with filters and pages in the URL; a decision's page shows one card a
  stage, with modeled fills, the cost scenario and each stop tightening labeled; `/policies` shows each policy's
  hash, the owner's decision and its runs. Model-authored text is shown as text. Before migration `0009` each
  page says the schema is pending; with the API down each shows its error.
- **Frame policy.** Every response of the web's server entry, errors included, carries `X-Frame-Options: DENY`
  and `Content-Security-Policy: frame-ancestors 'none'`. Static files (`public/`, `/assets/`; none of them HTML)
  are answered by Nitro before the entry, without them.
- **OBSERVED in Chromium on scratch PostgreSQL 16** with the production web build: the M7 spec's eight tests
  pass at 390 and 1440 px, and its frame test fails without the policy; M6's nine browser tests pass on this web;
  the harness functions issue the expected commands on stubs. The web's checks (190 unit tests), ruff, OpenAPI,
  the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** `BrowserDecisions` and `BrowserDecisionsError` on the owner's PC; PostgreSQL 17; the owner's
  controls (B8b). Next: B8b, then B9's final run on the owner's PC.

**M7 B7: the owner's private API now shows trade intents, operating policies, entry pauses and outcomes, takes the owner's resume of an entry pause, a decision probe and generation 3's starts, and raises the agents' permission epoch after a policy's revocation; the OpenAPI document, the generated types and the web's schemas follow, and no page uses the routes yet (ExecPlan 0026, 2026-10-16). Nothing deployed or run against the normal application; no model called; nothing installs the policy outside a disposable database.**
By the cloud session of B0 to B6c, on branch `claude/m7-b0-hjaahq` from `main` at `51e2454`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b7--the-owners-api-the-openapi-document-and-the-generated-types-2026-10-16),
[COMMANDS](COMMANDS.md#execplan-0026-b7-the-owners-api-the-openapi-document-and-the-generated-types-2026-10-16),
[API_CONTRACTS](contracts/API_CONTRACTS.md#m7-owner-routes-execplan-0026-b7).
- **Reads.** A trade intent shows what the model requested, its review, what was submitted or withdrawn, the
  engine's answer, what the risk gate permitted and what was filled, each from its own record. Policies show the
  code's documents before the install and the owner's decision after it; entry pauses, their resume and the
  engine's closing; outcomes as recorded. No route takes an intent, a price, a quantity or a stop from the browser.
- **Owner requests.** One resume per pause; a decision probe; the owner's decision starts only when the worker
  would start it and names nothing; briefs and entry-basis promotions; experiment drafts naming an installed
  policy. Each answers `503 TRY_AGAIN` while the database is busy, and records nothing then.
- **Revocation.** The owner's revocation of an operating policy is recorded first; the epoch is raised once
  after it, and a raise that fails is logged and tried again by resending.
- **Status.** `SystemStatus.decisions` says from recorded facts whether decisions run on the main account. The
  web accepts both API shapes, since it is deployed first.
- **Review.** An independent review found no blocker, two points to fix (two writes answered `500` when busy;
  tests that proved less than their names) and seven nits. Each is fixed or answered, with a test wherever
  behavior changed; taken out one at a time, each of the five fixes makes its test fail.
- **OBSERVED on scratch PostgreSQL 16:** the 21 owner-route tests pass; the M5 to M7 suite fails in B1's two tests, in an M6 test that fails when it starts in the minutes
  around the hour (found here, left as it is), and in one B7 test that read logs an earlier migration had
  switched off (fixed; its file passes); the bridge-side suites pass; M0 to M4 pass except
  `test_m1_account.py`, which needs the Compose host; on a real `0008` database the M7 routes answer
  `503 DECISION_SCHEMA_PENDING` and the policies show as not installed; `Migration7`'s steps pass outside Docker.
  Ruff, OpenAPI, the web's checks, the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** `ApiAuth7` and `Migration7` on the owner's PC; PostgreSQL 17 for these tests; the same-origin
  functions with their CSRF checks and the pages (B8). Next: B8, the pages.

**M7 B6c: the reference strategy is replayed, as research work, over each agent-driven main-account run's window, in 21-day periods, as the forward control the plan asks for; nothing shows it to the owner yet, and its tests wait for the owner's PC (ExecPlan 0026, 2026-10-12, last checks 2026-10-16). Nothing deployed or run against the normal application; no model called; no agent-driven run exists outside a disposable database.**
By the cloud session of B0 to B6b, on branch `claude/m7-b0-hjaahq` from `main` at `7b661a0`, with `main`'s M9 and
M10 documents merged in. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6c--the-control-replay-2026-10-12),
[COMMANDS](COMMANDS.md#execplan-0026-b6c-the-control-replay-2026-10-12).
- **Periods.** Each activated agent-driven run of the main account gets one period at a time, frozen at its
  activation plus a whole number of 504 hours, starting flat with 10000 of virtual funding once the period
  before it has ended. Research learns of the runs through one read-only view, and the database refuses a
  period that does not match the run, its policy, its activation or its predecessor.
- **Advances.** Once a day, on an idle runner and while research is approved, the bridge queues a `CONTROL` job
  beside the shadows' advances: the reference alone, replayed like a shadow's reference cell, outside the trial
  day and the queue of four, with no trial row. Each advance re-checks every earlier mark, and marks are
  immutable.
- **Endings.** A period succeeds when its window or its run ends; it is suspended when an earlier mark no longer
  reproduces; it ends incomplete when its store is lost, capped, gapped, starts after its freeze, or the period
  is not finished a week after its window. Store rotation keeps a store while a period is bound to it.
- **Hidden.** No owner read, owner cancel, dataset list or agent tool names control work. While one runs, the
  research status reads `running` with no job named. Nothing serves periods or marks in M7.
- **Review.** An independent review found one major point (a late period could replay from a store that did not
  cover its freeze), three minor points (the check's time zone, the owner's dataset list, a period whose advances
  kept failing) and three nits. Each is fixed or answered, with a test wherever behavior changed. Switched off
  one at a time, all 73 checks make their tests fail, three of them only after this round's fixes.
- **OBSERVED on scratch PostgreSQL 16:** the 13 control tests and the 5 bridge tests pass (the bridge tests'
  first run after a restart of the session's container failed three of them, cause not found; every later run
  passed); the M5 to M7 suite fails only in B1's two tests; M6's bridge-side suites pass; M0 to M4 pass except
  `test_m1_account.py`, which needs the Compose host; `Migration7`'s steps pass outside Docker. Ruff, OpenAPI,
  the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** `Comparison`, `ShadowSchedule` and `Migration7` on the owner's PC; PostgreSQL 17 for these tests;
  a period over a real agent-driven run. Next: B7, the owner's API.

**M7 B6b: an agent-driven run's report now shows its segments and its decision measures, and two isolated runs on one fixture can be compared; the single-coordinator variant exists for fixtures only; the harness phase waits for the owner's PC (ExecPlan 0026, 2026-10-12). Nothing deployed or run against the normal application; no model called; nothing installs the policy or the variant outside a disposable database.**
By the cloud session of B0 to B6a, on branch `claude/m7-b0-hjaahq` from `main` at `a284329`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6b--segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12),
[COMMANDS](COMMANDS.md#execplan-0026-b6b-segments-decision-measures-the-single-coordinator-variant-and-the-comparison-2026-10-12).
- **Segments.** The policy engine starts a new evaluation segment when a submission's context (runtime profile,
  approved sources, research envelope, approved candidates) differs from the run's previous submission's, in
  submission order. The report's segment list shows them; the reference engine never writes one.
- **Decision measures.** A report under `EVALUATION_PROTOCOL_V2` carries the protocol's nine measures, computed
  through eleven new read-only views for the evaluation identity: codes, states, counts and times, never a
  model's text. A run without agent workflows shows `NOT_RECORDED`, never zero. A V1 report is unchanged.
- **The comparison** of two `FINAL` reports of fixture runs: refused, naming every reason, unless they match in
  fixture, grid, start, costs, baselines, contributions and statistical rules; paired hourly log returns with
  the protocol's bootstrap at three block lengths; no threshold. On one synthetic fixture with scripted
  decisions, the reference, `AGENT_POLICY_V1` and `AGENT_POLICY_V1_SOLO` give three such comparisons. Scripted
  decisions show that the comparison works, not that a role helps.
- **Review.** An independent review found two minor points (a model's tool name could reach a report; a fixture
  engine kept its policy over a live position of the reference) and six nits. Each is fixed, with a test
  wherever behavior changed. Switched off one at a time, all 33 checks make their tests fail, three of them only
  after tests were added for gaps this round found.
- **OBSERVED on scratch PostgreSQL 16:** the phase's 15 tests pass; the M5 to M7 suite fails only in the two
  tests and four files that failed before, after one kept schema test was taught B6b's views; M0 to M4 pass
  except `test_m1_account.py`, which needs the Compose host; R19 is `VERIFIED`; `Migration7`'s steps, whose
  helpers B6b repaired for B5's and B6a's changes, pass outside Docker. Ruff, OpenAPI, the links and the
  profile check on PowerShell 7 pass.
- **NOT RUN:** `Comparison` and `Migration7` on the owner's PC; PostgreSQL 17 for these tests. The forward
  control replay is B6c.

**M7 B6a: the owner can approve a research candidate as an entry basis under the operating policy, by its hash, and revoke it; a decision may then enter on it with its stop and hold, only while its own entry signal holds; the harness phase waits for the owner's PC (ExecPlan 0026, 2026-10-12). Nothing deployed or run against the normal application; no model called; nothing installs the policy, so no promotion can be asked for outside a disposable database.**
By the cloud session of B0 to B5, on branch `claude/m7-b0-hjaahq` from `main` at `bf4e7bc`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b6a--promotion-approval-and-the-candidate-basis-2026-10-12),
[COMMANDS](COMMANDS.md#execplan-0026-b6a-promotion-approval-and-the-candidate-basis-2026-10-12).
- **The request.** Once `AGENT_POLICY_V1` is installed, SYSTEM asks the owner with `PROMOTION_V2` for each
  candidate whose evidence is ready and whose ATR period, stop multiple and hold lie in the policy's sets. The
  server writes the request's scope, policy and exit values; the model cannot. A request for consideration of
  M6 can still only be rejected, and the owner's rejection of one is always applied.
- **The decision.** Only the owner approves, rejects or revokes, by the request's exact hash, through the
  existing approval record; the agent worker applies it and the database guards repeat every rule. A
  revocation raises the permission epoch at once and suspends the candidate.
- **The basis.** A decision is shown up to four approved candidates with their computed signals and may name
  one as the basis of an entry, which takes the candidate's stop multiple and hold and still needs its review.
  The engine reads no research table: it checks the submitted declaration and takes the entry only on the
  candidate's own entry signal on the decision bar. A position keeps its terms after a revocation.
- **Review.** An independent review found one major point (an entry submitted before research suspended its
  candidate stayed open, since a suspension raises no epoch; the worker now withdraws it at its next pass),
  two minor points and three nits. Each is fixed or recorded, with a test wherever behavior changed. Switched
  off one at a time, 27 of 28 checks make their tests fail; the 28th is redundant.
- **OBSERVED on scratch PostgreSQL 16:** the phase's 11 tests pass; the M5 to M7 suite fails only in the two
  tests and four files that failed before B6a; M0 to M4 pass except `test_m1_account.py`, which needs the
  Compose host; R19 is `VERIFIED`. Ruff, OpenAPI, the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** `PromotionApproval` on the owner's PC; PostgreSQL 17 for these tests. The owner's start of a
  `PROMOTION_V2` and the promotions page model are B7's.

**M7 B5: generation 3: agents brief the market, decide on the policy's own run, have each entry reviewed, submit it to the engine and review each closed position; both probe suites are built; the harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-11). Nothing deployed or run against the normal application; no model called; nothing installs the policy or starts a decision outside a disposable database.**
By the cloud session of B0 to B4, on branch `claude/m7-b0-hjaahq` from `main` at `d8000a6`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b5--generation-3-the-decision-loop-its-triggers-and-both-probe-suites-2026-10-11),
[COMMANDS](COMMANDS.md#execplan-0026-b5-generation-3-the-decision-loop-its-triggers-and-both-probe-suites-2026-10-11).
- **The loop.** A reviewed market brief, a bar close or a position event starts one decision on the operating
  policy's running run. It is shown a stored snapshot of that run only, drafts intents from the policy's own
  choices (never a price, a quantity or a stop level), has each entry reviewed against the draft's exact hash,
  submits it and waits for the engine's answer. Exits need no review. The engine still checks everything itself.
- **Triggers** are written once, judged by their own staleness, coalesced, and held by one open decision, a
  cooldown and daily caps, and the newest event is the one kept; a newer bar ends a decision that has not
  submitted. A decision that ends any other way withdraws what the engine has not answered and any accepted
  entry that has not filled.
- **Outcomes.** Each closed policy position gets one record built from financial rows and one review of it.
- **Probes.** The capability suite adds CP-21 and CP-22. The owner's decision probe runs CP-23 to CP-27 on the
  policy; no decision starts without its `VERIFIED` result. Scripted, it uses 26 of its 40 calls.
- **Review.** An independent review of the batch found one major point (an accepted entry that had not filled
  was not withdrawn when its decision ended) and eight smaller ones. Each is fixed, with a test wherever
  behavior changed. Switched off one at a time, 24 of 25 checks make their tests fail; the 25th is redundant.
- **OBSERVED on scratch PostgreSQL 16:** the five phases' tests, 41 in 43 cases, pass by marker in 5 to 36 s
  each; the M5 to M7 suite fails only in the two tests and four files that failed before B5; M0 to M4 pass except
  `test_m1_account.py`, which needs the Compose host; the reference engine's parity check R19 is `VERIFIED`. The
  actual step schema v3 is within the documented limits and differs from B0's preview, so its CLI probe runs
  again in `AgentOffline7`. Ruff, OpenAPI, the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** the five phases on the owner's PC, with the schema through the pinned CLI; PostgreSQL 17 for these
  tests; the live probes, which are the owner's in M7-B.

**M7 B4: an agent can tighten a position's stop, protection holds quotes against the stop in force, and the trade list labels an agent's exit; the harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-11). Nothing deployed or run against the normal application; no engine is bound to a policy before B5.**
By the cloud session of B0 to B3, on branch `claude/m7-b0-hjaahq` from `main` at `dbe17b1`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b4--stop-tightening-the-stop-in-force-and-the-trade-lists-exit-label-2026-10-11),
[COMMANDS](COMMANDS.md#execplan-0026-b4-stop-tightening-the-stop-in-force-and-the-trade-lists-exit-label-2026-10-11).
- **On the owner's PC meanwhile** ([plan §18](plans/0026-m7-agent-driven-main-decisions.md#run-m7-b3a-on-the-owners-pc-b1-to-b3s-phases-and-the-rehearsals-revision-2026-10-11)). The deploy model of B1 met 76 of
  76 expectations. With the owner's pilot watch, run `m7-b3a` (B3's code, PostgreSQL 17.11) passed `Build`,
  `EngineParity7`, `Migration7`, `PolicyDocument`, `IntentRaces`, `IntentEngine` and `Regression` on their first
  attempt with no skip; the watch stayed clean and ended with the run. `ResearchActivationRehearsal` failed: B1's
  new `$Revision` parameter was overwritten by a local `$revision` (PowerShell ignores case), so two correct
  results were compared with the wrong revision. Fixed here; the rehearsal is `NOT RUN` again until the next PC run.
- **Tightening.** An agent chooses `BREAKEVEN` or `STOP_TEMPLATE`, never a level. The engine computes the level,
  takes it only on an open, filled position whose terms allow that template, above the stop in force and below
  the bid, and appends it as a new version; the mandate never changes. A stop crossed in the same step wins.
- **The stop in force** is what protection, the poll, planned risk and `GET /v1/risk` use. A quote older than an
  update is held against the stop before it, so a late quote cannot trigger a stop set after its time.
- **The trade list** labels an agent's early exit `AGENT_EXIT`; reference and candidate reports are unchanged.
- **OBSERVED on scratch PostgreSQL 16:** the M7 files 148 passed, also with the flags the harness sets; the M5 to
  M7 suite fails only where it failed before B3; M1 to M4
  318 passed twice; `EngineParity7` `VERIFIED`. Ruff, OpenAPI, the
  links and the profile check on PowerShell 7 pass. Fifteen of sixteen changes, each switched off, fail their test.
- **NOT RUN:** `IntentEngine`, `IntentRaces`, `EngineParity7` and `Regression` as harness phases on B4's build
  (Docker), PostgreSQL 17 for these tests.
- **Review.** An independent read-only review found no blocker, a gap in the tests and six nits, all taken with
  tests: planned risk to the stop in force is now tested; the bid is compared as its row stores it; the update
  row carries the submission's run; `BREAKEVEN` records its inputs; a template without a final bar waits; and
  the stop updates are read only when a position is live.

**M7 B3: the engine takes agent decisions: entries, exits, cancellations and the entry pause, checked until the fill and held to the action limits; the harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-11). Nothing deployed or run against the normal application; nothing installs the policy before B5, so no engine is bound to one yet.**
By the cloud session of B0 to B2, on branch `claude/m7-b0-hjaahq` from `main` at `aea9d60`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b3--the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11),
[COMMANDS](COMMANDS.md#execplan-0026-b3-the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11).
- **Before B3, on the owner's PC.** B0's steps 1 to 4 ran from `main` at `aea9d60`, inside the quiet window:
  the schema through the pinned CLI and a mock passed; on PostgreSQL 17.11 one engine alone did not starve a
  waiting epoch update, so the hold stays; the live probe's model steps took a median 13.7 s. The incidents
  read before and after was identical. The step budget on an M6 build is still not measured.
- **The intake.** Bound to a policy, the engine answers each submission and pause request once, in submission
  order, after checking the intent's authority, its choices (only the policy's own values), the run, the limits
  and the market. An entry becomes the reference's signal row and goes through the same risk gate, sizing,
  order and fill code, with two more upper bounds: the requested exposure and the window's remaining notional.
  An exit reuses the exit obligation; a cancellation the existing cancel. Nothing waits on an agent's lock.
- **Until the fill.** The epoch, a withdrawal, the expiry, a newer bar, the price's deviation and an open pause
  are checked again before each decision, attempt and fill. A step that cannot hold the epoch takes no intake,
  fills no policy entry and decides no policy signal.
- **Protection is untouched.** A pause or a limit refuses entries only; exits and protective exits run. An exit
  and a stop in one step give one sell.
- **Replay (R26).** A run's requests are recorded with their times and written back by a replay, which reaches
  the same fingerprints and the same answers.
- **OBSERVED on scratch PostgreSQL 16:** the B3 tests with the policy and binding files 130 passed, also with
  the flags the harness sets; the M5 to M7 suite fails only where it failed before B3; M1 to M4 ran twice,
  each time with one different market-worker test failing, in code B3 does not touch (each passed in the other
  run and alone); `EngineParity7` `VERIFIED`. Ruff, OpenAPI, the web checks, the links and the profile check on
  PowerShell 7 pass.
- **NOT RUN:** `IntentEngine`, `IntentRaces`, `EngineParity7` and `Regression` as harness phases (Docker),
  PostgreSQL 17 for these tests and Windows PowerShell 5.1.
- **Review.** An independent read-only review found no blocker, three points to fix and ten nits. Fixed with
  tests: a cancellation that named an old bar could end its own cooldown at once (it now runs from the bar the
  engine answered it in); the tests now cover the total and notional limits, a cancellation in the filling step,
  a locked epoch holding back a policy signal, a suppressed stop's cooldown and an epoch change in replay; the
  recorded stream keeps rows and epoch changes on one clock. Among the nits: an expired entry keeps what it
  waited on, and an engine behind the cutoff waits for it instead of reading it early.
- **Merged** on the owner's standing instruction to merge pull requests that are ready (`fd70434`, 2026-10-11).
- **Next:** B1's to B3's phases on the PC, run `m7-b3a` prepared from B3's code; they wait for the pilot watch,
  which the desktop app refused the session there. Then B4 (stop tightening).

**M5 follow-up, the live token-refresh check: first attempt NOT RUN, because the normal application cannot make a model call until a new runtime profile is approved (ExecPlan 0020, 2026-10-11, 11:07 UTC). Read-only; nothing changed, `agent-runner` not recreated.**
By a session on the owner's PC, on the owner's go-ahead of 10:53 UTC
([DECISIONS](../DECISIONS.md#2026-10-11--the-live-token-refresh-check-the-owners-go-ahead-and-why-it-could-not-start)).
Evidence: [ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#follow-up-after-closure--the-live-refresh-check-first-attempt-2026-10-11),
[COMMANDS](COMMANDS.md#the-live-token-refresh-check-first-attempt-read-only-reads-of-the-normal-application-2026-10-11).
- **OBSERVED, 11:03 to 11:07 UTC.** The agent runtime is `LOGIN_REQUIRED` with `PROFILE_DEFINITIONS_CHANGED` since
  the M6-A deployment of 2026-10-08 22:20 UTC, with no approved profile; auth is `PRESENT`. The last model call was
  the probe run of 2026-10-02. None of the 20 recorded calls has a copy-back, and the runner's `last_refresh` is
  still the login's, 2026-10-02 11:20:20 UTC.
- **NOT RUN:** the refreshing call with its recorded copy-back, the later call on the refreshed tokens, and the
  call after an `agent-runner` recreate.
- **What it waits for.** The owner composing and approving the new runtime profile and starting the probes, which
  [ExecPlan 0023 §13.2](plans/0023-m6-research-investigations.md#132-m6-b-activation-each-step-on-the-owners-instruction)
  places at step 3 of the M6-B activation. A probe run before the research services are active fails its research
  probes and sets the capability latch (read in the code, not run). Whether to bring the profile and a probe run
  forward was put to the owner; the implementer recommends leaving it with M6-B and reads the owner's `Continue`
  of 14:53 UTC as that. A re-read at 14:56 UTC showed the runtime unchanged and no model call.
- **Also OBSERVED, not examined further.** The seven containers inspected, `postgres` and the pilot's workers among
  them, started at 2026-10-10T07:18:00Z with restart count 0, after the records of 2026-10-08. `agent-worker` reads
  `unhealthy` in Docker, its health command exceeding its 3 s limit, while its heartbeat in the database is current.
  At 14:56 UTC it read `healthy` again.
- **Next:** the check with M6-B's probe run, or earlier on the owner's word.

**M7 B2: the policy's documents, the manifest's slots and the engine's binding are built; their harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-11). Nothing deployed or run against the normal application; nothing installs the policy before B5.**
By the cloud session of B0 and B1, on branch `claude/m7-b0-hjaahq` on top of B1 (`ae85361`) while B1's pull request waited for its merge; moved onto `main` after that merge (`ca09fba`, 2026-10-11) with its tree unchanged. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b2--the-policy-documents-the-manifests-slots-and-the-engines-binding-2026-10-11),
[COMMANDS](COMMANDS.md#execplan-0026-b2-the-policy-documents-the-manifests-slots-and-the-engines-binding-2026-10-11).
- **The documents.** `AGENT_POLICY_V1` holds the plan's policy values, rules and empty slots for the six
  generation-3 hashes; `EVALUATION_PROTOCOL_V2` adds §5.11's segments and nine measures to V1. A parser names
  every key and its rule, so a broken document is refused by name. The install takes both or neither and refuses
  while either is incomplete, which is so until B5.
- **Drafts and approvals.** A policy run is drafted with its strategy, protocol and baseline slots taken from the
  policy, and the owner approves each exact hash as for every draft. A draft beside another strategy's live
  position is refused when either is a policy. The owner's route takes no strategy until B7.
- **The binding.** The worker binds at each lease to the strategy of the mode's open experiment (the reference
  or an installed policy), else to a policy a live position names, else the reference. Every step compares its
  binding and, on a difference, writes nothing and hands the lease back to be bound again. A policy this build
  lacks is recorded as a failed step.
- **R19.** On EngineParity's three replays, the reference and a candidate send the same statements per step,
  in the same order, and reach the same fingerprints as on B1's build (`VERIFIED` on PostgreSQL 16).
- **OBSERVED on scratch PostgreSQL 16:** the policy and binding tests 88 passed, also with the flags the harness
  sets; the M1 to M7 suites fail only where they failed before B2; `EngineParity7` `VERIFIED`. Ruff, OpenAPI,
  the web checks, the links and the profile check on PowerShell 7 pass.
- **NOT RUN:** `PolicyDocument`, `EngineParity7` and `Regression` as harness phases (Docker), PostgreSQL 17 and
  Windows PowerShell 5.1.
- **Review.** An independent read-only review found no blocker, three points to fix and six nits; all are
  fixed with tests. Among them: the policy's rule fields can only restate V1's rules, the start refuses again
  what the draft refuses, and `PolicyDocument` now passes with the flags the harness's test service sets.
- **Next:** B2's pull request, for the owner to merge; B1's and B2's phases on the PC; B0's PC steps before B3;
  then B3.

**M7 B1: migration `0009`, the completed generation lookup and the harness's M7 profile are built; their harness phases wait for the owner's PC (ExecPlan 0026, 2026-10-10). Nothing deployed or run against the normal application.**
By the cloud session of B0, on branch `claude/m7-b0-hjaahq` on top of B0's merge (`7b3e52c`, 2026-10-11). Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b1--migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10),
[COMMANDS](COMMANDS.md#execplan-0026-b1-migration-0009-the-generation-lookup-and-the-harness-profile-2026-10-10).
- **Migration `0009`.** Ten insert-only `decision_*` tables with their guards, 20 read views of the policy's own
  runs for the agent identity, the engine's epoch hold, the guarded install function, grants, generation 3's values
  in M6's agent checks, and the two guards M6 left (R25). No M1–M4 table, grant or row changes. Nothing uses the
  tables before B2–B5. `install-definitions` refuses while the build holds no definition, which is so until B2.
- **The generation lookup.** Agent code reads named fields of a generation instead of its number; generations 1
  and 2 are byte-identical and the M5 and M6 agent suites give the same results as before.
- **Every revision comparison** accepts `0008` or `0009`, so M6-B can still be activated on the M7 build (R29).
- **The harness.** `tools/m6-acceptance.ps1` and the new `tools/m7-acceptance.ps1` share one body with a profile
  each. A check shows the M6 profile holds every value of today's 32 phases. `Migration7` is built; 17 M7 phases
  answer "not implemented" until their batch. The heavy lock stays M6's.
- **OBSERVED on scratch PostgreSQL 16:** `test_m7_schema.py` and `test_generations.py` 37 passed; the M1 to M6
  suites on `0009` fail only where they failed on `0008` before B1; a `0009` database downgraded to `0008` dumps
  identically to one migrated straight to `0008`; `Migration7`'s steps `VERIFIED` outside Docker. Ruff, OpenAPI,
  the web checks, the links and the M6 profile check on PowerShell 7 pass.
- **NOT RUN:** every harness phase (Docker), PostgreSQL 17, Windows PowerShell 5.1, and an M6 run on the
  refactored harness.
- **Reviews.** Two independent read-only reviews, of the engine diff and of the harness diff, found no blocker.
  The engine review's seven points and four of the harness review's five are fixed with checks; the fifth needs
  no change. Among them: a harness phase now also refuses while another isolated stack runs, from any
  checkout. B1 changes what an M6 rerun executes (`m6-deploy.ps1` and its model), so the deploy model runs
  before the next M6 run.
- **Decided on the owner's delegation, 2026-10-11** ([DECISIONS](../DECISIONS.md#2026-10-11--m7-b1-the-owner-has-b0-merged-and-leaves-the-heavy-run-timing-and-the-epoch-hold-to-the-implementer)): B1's heavy phases run
  in the next free heavy slot after any waiting M6-B gate run; B3 keeps the epoch hold if PostgreSQL 17 shows one
  engine alone does not starve the epoch update (§5.5's gate amended).
- **Next:** B1's pull request; B0's PC steps recorded once their files are attached; B1's harness phases on the
  PC; then B2.

**M7 B0: contracts reconciled and the B0 measurements recorded; three runs are decided and wait for the owner's PC (ExecPlan 0026, 2026-10-10). No application code changed; nothing deployed or run against the normal application.**
By a cloud session on branch `claude/m7-b0-hjaahq` from `main` at `1da608f`, started from the owner's question in
chat, `what about m7 ?`. Evidence: [ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#b0--contracts-measurements-and-the-harness-sketch-2026-10-10),
[COMMANDS](COMMANDS.md#execplan-0026-b0-m7-contracts-and-measurements-2026-10-10).
- **Contracts.** Every disagreement of the plan's §3.4 is written into the contract that held it: ROADMAP,
  DATA_CONTRACTS, AUTONOMY_MATRIX, API_CONTRACTS, AGENT_TOOL_CONTRACTS, OPERATIONS, FRONTEND, EVALUATION,
  SECURITY, CONFIGURATION and RESEARCH_WORKFLOWS. Eight have an M7 section marked PROPOSED; the other three carry
  the text in place, marked the same way. No authority is added.
- **OBSERVED.** §2 of the plan holds on `main` with moved lines; one statement of §2.1 was wrong and three more
  facts need a note (§2.8). Versions unchanged. The
  schema v3 preview is inside every structured-output limit: 144 properties, depth 9, 10,488 bytes.
- **OBSERVED on PostgreSQL 16, not the gate:** a waiting epoch update is starved for as long as share holders
  overlap without a gap, so G1 fails as written. One engine alone never starved it (back to back included); agent
  commit checks that overlap one another starved it with or without the engine. The plan's rule says the
  fallback follows; since the fallback would not remove that starvation, keeping the hold is put to the owner.
- **The harness's M7 profile, sized (INFERRED).** About 300 to 370 lines of harness code and 430 to 540 of
  profile data for the refactor, and about 1,020 to 2,035 lines for the new phases beyond definitions. Three
  findings need the owner before any harness code: the shared heavy lock, `ResearchActivationRehearsal` on
  revision `0009`, and the unknown pre-M7 images.
- **Checks run here.** Ruff, the OpenAPI check, web lint, typecheck, 155 unit tests, the API-type check, Prettier,
  the web build and the link check passed. Engine tests without a database: 615 passed; 471 need a database or the
  run's secrets and are NOT RUN.
- **NOT RUN:** the schema probe through the pinned CLI and the epoch gate on PostgreSQL 17 (Docker on the PC);
  the live-latency query against the normal database; a step-budget measure on the M6 build.
- **The owner's answers, 11:57 UTC:** `1. decide for me 2. decide for me 3. I approve`
  ([DECISIONS](../DECISIONS.md#2026-10-10--m7-b0-the-owner-leaves-the-latency-read-and-the-two-small-runs-to-the-implementer-and-approves-the-harness-profile)).
  The implementer decided yes to the latency read and to the two small runs, in one sitting before B3 under the
  conditions in COMMANDS; the owner runs them on the PC. The harness profile is approved. The epoch-hold choice
  for B3 is still the owner's.
- **Next:** B1.

**M6-B: the performance pull request is delivered and merged on the owner's decision; the four job times are not judged yet, and that does not hold M7 (ExecPlan 0025, 2026-10-09, 16:35 UTC).**
OBSERVED owner messages at about 16:30 UTC, after the session had reported where the verification stood:
`can this be done later ? I don't want this to block m7` and `I want to start m7 as early as possible`
([DECISIONS](../DECISIONS.md#2026-10-09--m6-b-the-performance-pull-request-is-merged-without-its-job-time-verdict-what-remains-is-done-later-and-does-not-hold-m7)).
Pull request [MentorAliu/adaptive_spot_lab#35](https://github.com/MentorAliu/adaptive_spot_lab/pull/35) is merged
as it stands, with an ordinary merge commit pinned to its head, without force, an administrator bypass or branch
deletion. This entry is written before the merge and does not claim it; the next documents on `main` record the
merge commit. The merge changes files only: nothing is deployed, enabled or approved, and research stays off.
Evidence: [ExecPlan 0025 §14](plans/0025-research-job-cost-and-search.md#14-progress-and-completion-evidence),
[COMMANDS](COMMANDS.md#execplan-0025-research-job-cost-and-the-analysts-search-2026-10-09).
- **What it changes.** The dataset hash takes a new definition (binary `COPY` rows in sequence chunks). A replay
  batch holds its row writes and sends them as one statement a table, passes quiet stretches from two reads,
  leaves out a step that can do nothing, and keeps the breach check's last answer; a job's results stay
  identical, held by tests and by a verification mode. The analyst's search ranks the newest 500 matching visible
  items. `PerformanceApi` and `PerformanceResearch` fail on a miss. No schema change; one change in code the
  forward engine runs (`numbers.mul/div/add/sub`).
- **VERIFIED on the fresh run `m6-p2a`, one Build of `35630db`:** 17 phases, among them `Regression` (263 tests),
  `EngineParity` against the M3 baseline, `ResearchRunner`, the browser phases, `Checks` and `PerformanceApi`.
- **MEASURED.** The search at p95: 87.36 ms against 150 ms, MET (211.99 ms on the M6-A build). A screening on
  9.6 days: 108.2 s on a ten-day scratch store, where the M6-A build took 568.2 s; 168.9 s on the store of 27 days
  that `PerformanceResearch` uses.
- **NOT JUDGED: the four job times at 14 and 21 days.** `PerformanceResearch` ended FAILED at 16:25 UTC, stopped
  by the pilot watch before its full test, shadow advance and projection had run. INFERRED by the implementer from
  the one screening: the shadow advance over 21 days probably still misses 3,600 s.
- **The pilot beside the runs** (the watch read the normal application read-only; the session started it without
  a separate approval in chat for each start, which is reported to the owner). Lease epoch 5 held and the
  checkpoint advancing at every reading; every hourly report there; no `PROTECTION_UNAVAILABLE` row. Recorded on
  the normal market worker: collection gaps at about 12:45, 13:41 and 16:22 UTC; a retention call that failed and
  recovered at about 12:50 and at about 14:52 UTC, the second with no test container up; and **one
  `QUEUE_OVERLOAD` between 16:19:55 and 16:24:56 UTC, while a full test ran on the 27-day store. By the owner's
  rule of 2026-10-07 the watch stopped the run at once.** Whether the load caused it is NOT KNOWN. No test run
  was started after it, and the pilot was not read after 16:24:56 UTC.
- **Left for a later pull request, still a condition of the M6-B activation:** the four job times measured on a
  store of full size; a further reduction if the shadow advance over 21 days misses; a renewal of the job's lease
  that is asked again after a failure (found by the second review, written and tested on a copy, not merged).
  When a heavy test runs beside the pilot again is the owner's decision.
- **Also recorded here:** pull request 34 (ExecPlan 0026, the M7 plan) was merged as `ba2d560` at 11:43 UTC
  (VERIFIED read-only in `git log origin/main`), and `main` at that commit is merged into this branch (`852c092`).
- **Next:** B0 of [ExecPlan 0026](plans/0026-m7-agent-driven-main-decisions.md), which this merge unblocks.

**M7: the plan is approved for implementation (ExecPlan 0026, 2026-10-09). NOT IMPLEMENTED; nothing run. Merge of pull request 34 requested.**
OBSERVED owner instruction of 2026-10-09, `start the M7 plan`
([DECISIONS](../DECISIONS.md#2026-10-09--m7-plan-requested-execplan-0026)), and, after the plan was reported as
pull request [MentorAliu/adaptive_spot_lab#34](https://github.com/MentorAliu/adaptive_spot_lab/pull/34), at
about 11:40 UTC: `approve with your recommendations, merge it`
([DECISIONS](../DECISIONS.md#2026-10-09--execplan-0026-approved-for-implementation-with-the-recommended-decisions)).
The plan is [ExecPlan 0026](plans/0026-m7-agent-driven-main-decisions.md).
- **Approved:** the plan, and each of its eleven decisions as recommended
  ([§3.3](plans/0026-m7-agent-driven-main-decisions.md#33-decisions-for-the-owner)). M7-A may start once the
  performance pull request is merged. When the pilot ends is decided once M7-A is deployed. No partial reduction
  in M7. M6-B comes first, on the M6 build.
- **Not approved:** any step of the boundary or of M7-B, any command against the normal application, any
  approval of a policy, protocol, profile or promotion. The M7-A inert deployment is asked for before it runs.
- **The merge.** VERIFIED read-only first: the pull request is open, mergeable and clean with no check run, and
  `main` is still at `cb4bbd4`. It is merged with an ordinary merge commit pinned to its head, without force, an
  administrator bypass or branch deletion. This entry is written before the merge and does not claim it; the
  next documents on `main` record the merge commit. The merge changes documents only: nothing is deployed.
- **Next:** B0 of the plan, once the performance pull request is merged.
- **What it proposes.** An operating policy the owner approves by exact hash. Trade intents that the execution
  worker validates and sizes inside its fenced step, on the risk and broker path a strategy signal takes today,
  and checks again until they are filled. Early exit and a stop that only moves up, under a position's own
  terms. Bar, position and assessment triggers. Outcome records and reviews. Approval of promotions.
- **Reviewed.** Two independent read-only reviews of the first draft found two blockers and about twenty major
  points; the second draft is revised for them
  ([§17.1](plans/0026-m7-agent-driven-main-decisions.md#171-what-the-two-reviews-of-2026-10-09-changed)).
- **What shapes it.** The running pilot holds the main account's one experiment slot. M7-A (build, isolated
  acceptance, inert deployment) changes nothing the pilot uses. Trading under the policy starts only after the
  owner has stopped the pilot and its workers are rebuilt
  ([the plan's §13](plans/0026-m7-agent-driven-main-decisions.md#13-deployment-the-experiment-boundary-and-activation)).
- **Made read-only,** in a worktree of its own, from `main` at `cb4bbd4`, beside the session of the performance
  pull request. No Docker or Compose command addressed the normal application.

**M6-B: the performance pull request is in progress (ExecPlan 0025, 2026-10-09). NOT IMPLEMENTED yet; nothing run.**
OBSERVED owner instruction of 2026-10-09, `start the performance PR`, and three decisions the same day
([DECISIONS](../DECISIONS.md#2026-10-09--m6-b-the-performance-pull-request-search-ranking-the-dataset-hash-and-measuring-before-deciding-the-21-day-jobs)):
the analyst's search ranks the newest 500 matching visible items; the dataset hash takes a new definition; the
changes are built and measured first. The plan is [ExecPlan 0025](plans/0025-research-job-cost-and-search.md).
- **What the kept profile of 2026-10-08 shows** (one screening on 9.6 days, 568.2 s): 320.7 s is the dataset
  hash, most of it the database rendering 2.49 million rows as JSON; the stepped cell's 247.5 s is mostly
  three row writes for each second a position is held, copies of cached state, and the lease and commit of
  each quarter-second batch.
- **INFERRED, not measured:** after the first round a screening on 21 days and a full test on 14 days fit the
  bound of 3,600 s; a full test on 21 days and the shadow advances over 14 and 21 days still miss. What closes
  those is a design change the owner decides with the measured figures.
- **Branch** `claude/m6-performance` from `main` at `105dd2d`. Isolated runs only; nothing addresses the
  normal application; the pull request deploys nothing.

**The pilot check pull request: merge requested (2026-10-09, 07:00 UTC).** OBSERVED owner instruction in the
same Claude Code session, after pull request 33 was reported: `merge it`
([decision](../DECISIONS.md#2026-10-09--owner-asks-to-merge-the-pilot-check-pull-request)). VERIFIED read-only
first: commits `a93d718` and `11b2061` are pull request
[MentorAliu/adaptive_spot_lab#33](https://github.com/MentorAliu/adaptive_spot_lab/pull/33), open, mergeable and
clean at head `11b2061` with no check run; `main` is still at `105dd2d`, the commit the change was branched
from and checked on, so nothing has to be merged into the branch and nothing has to be run again; no other
pull request is open. The pull request is merged as it stands, with an ordinary merge commit pinned to its
head, which is this record as one more documentation-only commit, without force, an administrator bypass or
branch deletion. This entry is written before the merge and does not claim it; GitHub records the actual
merge commit, and the next documents on `main` record it here. The merge changes files only: the check is
corrected in a checkout once that checkout holds the merge, and a checkout takes it between test runs, not
during one. The changed SELECT stays NOT RUN against the normal database, every `-Execute` of the check or of
the watch still needs the owner's approval in chat, and `ResearchActivationRehearsal` stays NOT RUN as a phase
with the two models in it. Nothing is deployed, enabled or approved, and no command addressed the normal
application.

**The pilot check reads the market worker's codes without regard to letter case (2026-10-09, 06:45 UTC); delivered as pull request 33, not merged.**
IMPLEMENTED and VERIFIED without the normal application. No command addressed it, no script ran with `-Execute`,
and nothing was deployed, enabled or approved. The owner's instruction and what it leaves as recorded:
[DECISIONS](../DECISIONS.md#2026-10-09--the-pilot-check-counts-the-market-workers-codes-without-regard-to-letter-case);
commands and every figure:
[COMMANDS](COMMANDS.md#the-pilot-check-counts-market-incident-codes-without-regard-to-letter-case-2026-10-09);
the record in the plan: [ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks).
- **The defect that was left open on 2026-10-08.** `tools/m6-pilot-check.ps1` read the market worker's incident
  codes since an instant into one object, as the deploy script did before its fix. A reading that held
  `clock_uncertain` and `CLOCK_UNCERTAIN` could not be taken. Read from the worker's code, not seen in a
  reading: one clock check that fails at the start of a collection writes both spellings. INFERRED from the
  watch's code, not observed: from then on every reading of a watch fails, and the third in a row stops the
  test run the watch stands beside, the phases of the M6-B gate among them.
- **The fix is one part of the check's fixed SELECT.** Market incident codes are counted by `upper(code)`.
  Execution incident codes and experiment event kinds are read as recorded: each is written in one spelling.
  The rule of the watch is unchanged; it already found and compared codes without regard to letter case.
- **Two models hold such rows now, and the rehearsal runs both.** New: `tools/m6/pilot-check-model.ps1`, 4
  scenarios with 15 expectations, where a function answers for `docker` and for the database. Changed: every
  reading of the deploy model holds one code in two spellings (17 scenarios, 75 expectations).
- **VERIFIED, 06:28 to 06:37 UTC.** The parser on all 46 scripts and modules under `tools`: 0 errors, no byte
  outside ASCII. Both models pass. Against the scripts as they were, both stop with the error of 2026-10-08
  (8 of 11 and 37 of 45 expectations fail). On a disposable PostgreSQL 17.11 of the product's image, with
  scratch tables, the changed SELECT gives `CLOCK_UNCERTAIN` 2 where the SELECT as it was gives two names that
  Windows PowerShell 5.1 does not read; the container is removed.
- **NOT RUN.** The changed SELECT against the normal database, and any `-Execute` of the check or the watch:
  each is the owner's to approve in chat. `ResearchActivationRehearsal` as a phase with the two models in it:
  its lines for them were executed inside the harness module, without Docker. Any other phase, any `pytest`.
- **For the owner.** The pull request shows the new SELECT. A checkout takes the change between test runs,
  not during one: the check is one of the files whose hashes `Report` compares with a run's Build. In a
  reading, and so in the watch's log, a code the worker writes in lower case now stands in upper case
  (`STREAM_SILENT`).
- **Delivered** as pull request
  [MentorAliu/adaptive_spot_lab#33](https://github.com/MentorAliu/adaptive_spot_lab/pull/33) against `main`,
  opened at 06:44 UTC and not merged: commit `a93d718` with the scripts, the two models and this record, and
  a documentation-only commit that records this number. The branch was pushed without force; nothing was
  pushed to `main`.

**M6-A is deployed inert to the normal application (B10, 2026-10-08, 22:15 to 22:20 UTC), VERIFIED read-only.**
`tools/m6-deploy.ps1` completed its eleven steps from commit `583a98a` (exit 0, record `COMPLETE`), on the owner's
approval. Record:
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b10--the-inert-deployment-to-the-normal-application-2026-10-08);
commands and every figure:
[COMMANDS](COMMANDS.md#m6-b10-the-inert-deployment-of-m6-a-to-the-normal-application-2026-10-08).
- **Runs now.** `web`, `api` and `agent-worker` on the images built from that commit; schema
  `0008_m6_research`. `postgres`, the market, execution and evaluation workers, the agent runner and the egress
  gateway are the containers they were: the same IDs, images, start times and restart counts.
- **Still off.** No research or source service has a container. `ASL_RESEARCH_ENABLED` and
  `ASL_SOURCES_ENABLED` are `0`; `asl_research` and `asl_source` exist without login; no envelope, source
  version or profile is approved. The agent runtime reads `login_required`: the M6 worker does not accept the
  profile approved for M5. That is expected and belongs to M6-B.
- **The pilot.** Lease epoch 5 and held, experiment `RUNNING` at version 3, 0 segments, 4 downtime events and
  the execution incidents as before; no market incident recorded during the deployment or the cleanup.
- **Backup and the way back.** `.cache\deployments\m6-deploy-20261008T221514Z\asl.dump`, SHA-256
  `428265791ac0075373af1e4150edd79f652e13b6ffbd37f40b1719e0e35fe0a7`; its copy was restored, migrated,
  reconciled and downgraded in isolation before anything was replaced. Rollback: `tools\m6-deploy.ps1 -Rollback`
  with the same image parameters, to the `:pre-m6` tags; valid until M6-B has produced a research row.
- **Removed afterwards,** as [DOCKER](../DOCKER.md#cleaning-up-disposable-resources) says: fifteen older rollback
  tags of `api`, `web` and `migrate`, 82 untagged images and 2.35 GB of build cache. No volume, no container.
- **For the owner to look at,** signed in at `http://localhost:3000`: `/system` (research and sources
  `unapproved`), `/agents` (`LOGIN_REQUIRED` with `PROFILE_DEFINITIONS_CHANGED`), `/research`, `/evidence` and
  `/approvals`. The implementer did not sign in.
- **Next: M6-B, the owner's.** Before any activation: `PerformanceResearch`, `ResearchSaturation` and
  `PilotCoexistence` on the build to be activated, the performance pull request for the four job times, the
  search budget, and the two staging reads timed read-only on the normal database
  ([ExecPlan 0023 §13.2](plans/0023-m6-research-investigations.md#132-m6-b-activation-each-step-on-the-owners-instruction),
  [§19](plans/0023-m6-research-investigations.md#19-open-risks)).

**M6 B9: the acceptance evidence for M6-A is complete on run `m6-b9s` (2026-10-08, 18:14 UTC). The inert deployment (B10) waits for the owner's yes.**
VERIFIED on one fresh run and one Build of commit `cedb6d1`: the 25 phases M6-A is accepted on, each in its
first attempt, with `Report` VERIFIED and no problem
([ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence),
[COMMANDS](COMMANDS.md#m6-b9-the-acceptance-run-m6-b9s-2026-10-08)). Acceptance and deployment are the owner's
decisions; nothing has addressed the normal application.
- **Measured against the budgets that are judged for M6-A.** API routes at p95: 38.91 ms sequential (250) and
  145.08 ms with five readers (500). Pages on a year of rows, 32 page views: SSR p95 at most 95 ms (below
  1,500), LCP at most 172 ms (2,500), CLS 0 (0.1). Migration 0008 on a live database 0.53 s.
- **Accepted without, and owed before the M6-B activation** (owner decisions of 2026-10-08):
  `PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence`; four research job times known to miss
  the one-hour bound; the analyst's search, MEASURED at 211.99 ms at p95 against 150 ms.
- **The pilot beside the run:** no stop; one hourly retention call failed and recovered between 15:26 and
  15:31 UTC, reported as the owner decided.
- **Delivered** as pull request 32 of `MentorAliu/adaptive_spot_lab` against `main` (opened 18:22 UTC, not
  merged). Every test run of the batch is removed by exact name; its evidence files are kept.
- **B10 approved by the owner at about 19:39 UTC** ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b10-the-owner-approves-the-inert-deployment-before-the-merge)): deploy the head of the pull request inert, then
  merge. OBSERVED in the read-only look before it: the owner had restarted Docker at 19:38:42 UTC; the same
  nine containers on the same images run again, the execution lease is at epoch 5 and held, and the pilot
  recorded one more downtime event. That is the starting state of the deployment, planned for 20:15 UTC.
- **The first deployment stopped at 20:15:04 UTC in its read-only preflight; nothing was changed.** The deploy
  script could not read the market worker's incident codes: the normal database holds one code in two
  spellings. One line of the script is fixed (those codes are counted without regard to case; they are
  reported, never judged), with its model test and the parser behind it, as the owner chose
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b10-a-deployment-that-stopped-in-its-read-only-preflight-and-the-fix-of-the-deploy-script)). Next start: 22:15 UTC.

**M6 B9: the owner scopes M6-A's acceptance to the inert deployment; the long acceptance run is stopped (2026-10-08, 14:04 UTC).**
NOT ACCEPTED yet. The owner asked for a simpler way to complete the pull request and decided
([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on)): M6-A is accepted on the phases the
inert deployment depends on, on one fresh run; `PerformanceResearch`, `ResearchSaturation` and
`PilotCoexistence` become the gate of the M6-B activation.
- **Why.** OBSERVED: the last full run took 11.3 hours, 9.2 of them in the first two of those phases, neither
  of which has passed in any run; the engine's product change of this batch is 673 lines, its harness and
  measurement code about 13,000. The inert deployment starts no research or source service.
- **Done.** Run `m6-b9r` stopped at 14:04 UTC with eleven phases VERIFIED and its measurement interrupted in
  its first part. `Report` requires the scoped list and names the three phases as the activation gate.
- **The trial on the stopped run, 14:08 to 14:22 UTC.** `BrowserResearch`, `BrowserResearchError` and
  `BrowserRegression` VERIFIED. `PerformanceApi` FAILED on one budget: MEASURED, the analyst's search at
  213.36 ms at p95 against 150 ms on 10,000 items at the extract cap; its routes at 39.12 and 168.14 ms
  against 250 and 500. The owner decided that the search budget is a condition of the activation
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-the-search-budget-is-a-condition-of-the-activation)): for M6-A it is recorded
  against its budget and not judged.
- **`PerformanceApi` and `PerformanceBrowser` tried, 14:41 to 15:14 UTC.** `PerformanceApi` VERIFIED with the
  search recorded as missed (234.55 ms). `PerformanceBrowser` ran for the first time: its test stopped at
  the system page, which has no level-one heading; that was a defect of the test and is corrected. MEASURED
  with the corrected test on the same stack: 32 page views, SSR p95 at most 101 ms (budget below 1,500),
  LCP at most 196 ms (2,500), CLS 0 (0.1).
- **Next.** One fresh run of the scoped list as the acceptance run (`m6-b9s`), then the pull request, the
  B9 report and the deployment plan.
- **Accepted without, and owed before activation:** the pilot's budgets under research load, the quiet
  window beside a pilot on the current build, the cost of research jobs, idle dispatch and staging
  ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)).

**M6 B9: the acceptance run `m6-b9r` is in progress (2026-10-08, started 12:13 UTC).**
NOT ACCEPTED yet. One fresh run and one Build, of commit `2453f68`; every phase of §10; the pilot watch beside
it. If every phase passes, with the four results the owner accepted as missed recorded as such, it ends at
about 00:30 UTC on 2026-10-09. Before it, OBSERVED on the same code in authoring runs: every functional phase
VERIFIED, `AgentFaults6` with its seven process cases for the first time, the fixed `SecretScan` complete on
eight clusters, the web tests with samples captured again
([ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence)). NOT RUN before it:
`PerformanceResearch` in its reworked form (its projection ran without a database), `ResearchSaturation` with
the staging fix, and `Report` on a complete run. `PerformanceBrowser` has not passed in any run either: its
one execution (`m6-b9i`) failed on a row lookup that was then fixed and not run again.
- **A correction of this morning's record (found 13:20 UTC).** One hourly retention call of the normal
  market worker failed at about 09:22 UTC and recovered by 09:30 (`RETENTION_FAILED`, `RETENTION_RECOVERED`),
  while two test stacks were at work. Nothing else of the pilot changed and the watch does not stop on it; the
  morning's entries said the pilot was untouched and left it out. INFERRED: the stacks' reads slowed the
  delete. Two heavy stacks at once are not used again beside the pilot without the owner's word
  ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)).
- **A second failed retention call, beside the acceptance run alone, and the owner's decision.** OBSERVED
  between 13:24:24 and 13:29:25 UTC, during the 27-day load of `PerformanceResearch`: failed, then recovered,
  nothing else of the pilot changed. The owner decided at about 13:47 UTC: a failed call that recovers is
  recorded with its time and phase and reported, and the run goes on; the run is stopped by hand when a call
  has not recovered ten minutes later or `RETENTION_STALLED` appears
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-a-failed-retention-call-that-recovers-is-reported-and-does-not-stop-a-test-run)).

**M6 B9: the new build passes its functional phases and cuts a stepped day from more than 608 s to about 230 s; the owner accepts four research job times as missed for M6-A and has it deployed inert (2026-10-08, 11:00 UTC).**
NOT ACCEPTED yet: the acceptance run has not started.
- **MEASURED on the new build** (run `m6-b9p`, a scratch measurement that repeats the measurement phase's own
  calls; 9.6-day dataset; isolated containers): a screening job completed in 568 s, results valid. Of that,
  321 s before the first cell (the runner's hash of the dataset, about 33 s a dataset day) and 247.5 s for a
  cell of 2.76 stepped days, about one of them with a position held (174,768 quote steps). The same job under
  a profiler: about half of the stepping is the engine's one valuation, one account update and one step row
  for each second of market time with a position; a quarter is the batch's cache copying the experiment's
  state at every step; the rest is heartbeats and commits.
- **INFERRED from that, for a candidate that almost always holds a position:** a screening on 21 days about
  2,800 s; a full test on 21 days about 5,700 s; a shadow advance over 14 or 21 days more than 6,000 s. A full
  test fits the hour at about 12 to 13 days.
- **OBSERVED owner decision at about 10:40 and 10:55 UTC**
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-research-job-times-beyond-the-one-hour-bound-are-accepted-as-missed-for-m6-a)):
  M6-A is accepted and deployed inert with the full test and the shadow advance at 14 and 21 days recorded as
  missed with their figures; everything else must pass on one fresh run; the remaining job cost is a separate
  pull request that must pass the same measurement before M6-B.
- **The functional phases of the new build, OBSERVED on run `m6-b9n`** (the tree of `b0e1ec1`): `Build`,
  `Generate`, `Checks`, `Migration`, `ResearchRunner` (with the new tests of the reuse), `EngineParity`,
  `Staging` (with the four new tests of the bounded read), `HoldoutIsolation`, `SourcePolicy`,
  `EvidenceInjection`, `ApiAuth` (with the job's workflow), `AgentOffline6`, `ShadowSchedule`,
  `DispatcherAuth6` and `ResearchActivationRehearsal` VERIFIED. `Regression`: its 172 tests passed, among
  them the statements of a forward step compared with the list as it was and the login step that removes the
  order dependency; the phase then stopped on its own guard, because merging `main` changed the market data
  code. The guard now names the merged `main` (`ec1d78b`), whose retention fix ran the market worker's fault
  tests in its own acceptance; a point for the owner, since decision 7 of 2026-10-06 names `ed9fae3`.
- **Next:** `PerformanceResearch` is being reworked so that its jobs complete inside a test window (small
  datasets measured, 14 and 21 days projected against the unchanged bound); the remaining checks of the new
  build (`AgentFaults6`, the browser phases, `SecretScan`); then the acceptance run.

**M6 B9: staging never worked on a large backlog (found by `ResearchSaturation`, fixed in code); the owner asks for the least waiting; the new build is being run (2026-10-08, 09:10 UTC).**
NOT ACCEPTED. Everything below about new code is NOT RUN unless it says OBSERVED.
- **`ResearchSaturation` ran to its end for the first time (run `m6-b9l`, 07:07 to 08:44 UTC) and FAILED.** The
  bridge logged 302 failed staging passes and staged no row while 2.3 million publications waited; the
  execution side passed its own run. The run's remaining phases were then stopped by hand.
- **The cause, OBSERVED on that fixture with the query plan** (as the research identity): the staging read asks
  for the next 160 publications through a security-barrier view, and the database does not carry a limit into
  such a view. It read and rendered every later row before it kept 160: 1.6 s with 1.1 million rows waiting,
  against that identity's 2 s statement timeout. On the normal database, which holds about a week of rows,
  staging would have failed from its first pass after activation. This is the risk B4 recorded, now shown.
- **Fixed in code** (commits `7705032`, `b82a379`): the read also has an upper bound, the next 160 sequence
  numbers, so it touches one batch whatever is waiting; where those numbers hold nothing, the numbers of the
  next batch are read without their rows and the rows by number. No schema change. Four tests added.
- **OBSERVED owner instruction at about 08:15 UTC**
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-the-owner-asks-for-the-least-waiting)): the least waiting, and
  correctly. The implementer's reading: test stacks side by side where memory allows, no rehearsal-only
  steps, reservations from measured durations, research jobs measured small and projected; the quiet period,
  the pilot watch and every budget unchanged.
- **Written and committed since 06:25 UTC, all without a container beside the measurements:** the research
  job's workflow (`40fc6b1`), the replay batch's reuse of the experiment's state (`1c49788`), `main` with the
  market worker's retention fix merged (`f967cbd`), the staging read. Lint passes on all of it. Two
  independent read-only checks traced the new engine tests and the statements of a forward step and found
  nothing that should fail.
- **In progress since 09:07 UTC, side by side:** the functional phases of the new build on run `m6-b9m`, and one
  small screening job run to completion on run `m6-b9p` for what the reuse is worth.

**M6 B9: research jobs miss the one-hour bound by far (first complete measurement); the owner decides to fix the cost in B9 (2026-10-08, 06:40 UTC).**
NOT ACCEPTED. `PerformanceResearch` ran to its end for the first time (run `m6-b9l`, an authoring run, 00:07 to
06:13 UTC) and FAILED. MEASURED on synthetic rows at full density, the research cluster at one CPU:

| Measurement | Result | Bound or budget |
|---|---|---|
| Screening job on 21 days | not finished at 2,160 s: 679 s before its first cell, then neither of 2 cells | 3,600 s a job |
| Full test on 14 days | not finished at 2,700 s: 454 s before its first cell, then none of 6 cells | 3,600 s a job |
| Shadow advance over 14 days | not finished at 2,700 s: 885 s before its first cell, then neither of 2 cells | 3,600 s a job |
| Full test and shadow advance on 21 days | not projected: no job completed to take a rate from | 3,600 s a job |
| Idle dispatch, p95 (inferred from measured parts) | 4,803 ms; eight direct samples, the longest 4,712 ms | 5,000 ms: met |
| Sealing 21 days, 14 days | 615 s, about 420 s | none set |
| Staging rate and largest batch | not measured: the read was canceled by the 2 s statement timeout | - |

- **The limits are the harness's, not the bound.** No job may run into a quiet window, so a job is cut after
  36 or 45 minutes; each figure is a lower bound of what the job needs. The full test spent 2,245 s on a first
  cell of 5.4 replayed days without completing it: more than 416 s a replayed day, against the 58 s the plan
  took from B0. INFERRED from that floor, a full test on 21 days needs more than 13,000 s.
- **Where the time goes, from the code** (a read-only analysis, no measurement of its own): before its first
  cell a job hashes its whole dataset once more, and with a position held every quote is a step that issues
  about ten reads the bare replay of B0 never issued. Rows before a cell's own window cost no read each.
- **Staging.** The first batch read of the measurement, through the `research_read` views as the research
  identity, was canceled by that identity's 2 s statement timeout after a backlog of one day had been loaded.
  Whether that is a cold cache or the query is NOT KNOWN. It is the risk recorded in B4, now OBSERVED on a
  fixture.
- **Two OBSERVED owner decisions at about 06:25 UTC**
  ([DECISIONS](../DECISIONS.md#2026-10-08--m6-b9-research-jobs-that-miss-the-one-hour-bound-and-a-jobs-workflow)):
  the cost is fixed in B9 (small jobs are measured to completion first; then the per-quote reads are cached
  within a batch on the replay path, with tests that results stay identical; then the measurement is
  repeated; any further step returns to the owner), and a research job is to record its workflow, with a
  test. The conditional answer of 2026-10-07 is replaced: that change would have altered results.
- **`main` merged into this branch (07:40 UTC).** `main` at `ec1d78b` carries the retention fix of the
  market worker (pull request #31, deployed to the normal market worker on 2026-10-07 at 21:22 UTC and merged
  at 23:28 UTC by the session that made it). Conflicts only in STATUS, COMMANDS and DECISIONS, where both
  sessions had added entries; every entry is kept, in order of time. The next Build is of the merged tree.
- **No acceptance run is started** until the measurement passes: `PerformanceResearch` would fail the same
  way. `m6-b9l` goes on with `ResearchSaturation`, which has never run to its end. The owner's estimate for
  this work: two to four days, the outcome not certain until measured.

**M6 B9: fresh run `m6-b9l` is an authoring run; three more harness and test defects found and fixed; a screening job on 21 days did not finish (2026-10-08, 03:15 UTC).**
NOT ACCEPTED. OBSERVED on run `m6-b9l` (Build 2026-10-07 21:24 UTC on the clean tree of commit `32de348`), which
is still running its measurements:
- **VERIFIED on their first attempt, fifteen phases:** `Build`, `Generate`, `Checks`, `Migration`, `ApiAuth`,
  `Staging`, `HoldoutIsolation`, `SourcePolicy`, `EvidenceInjection`, `ShadowSchedule`, `ResearchRunner`,
  `DispatcherAuth6`, `EngineParity`, `ResearchActivationRehearsal` (with the 57 pilot rule cases) and
  `MixedVersion`.
- **`AgentFaults6`, process part, FAILED on a defect of its own reading.** It waits for the workflow's queued
  experiment before it kills the worker, and found none in twelve readings although the workflow was waiting
  for one: the helper looked for the job by a column the product leaves empty. Fixed (the job is found
  through its hypothesis); NOT RUN again.
- **`Regression` FAILED on the order of phases.** 54 tests could not sign in as `asl_api`. Database roles
  belong to a cluster, the engine target's cluster is also the catalog of the research target, and the
  research helpers set role passwords there from their own secrets. `Regression` passed on `m6-b9k`, where it
  ran before them. Fixed: the phase sets that login from its own target's secret first; NOT RUN again.
- **`SecretScan`, tried on `m6-b9j`, FAILED on a defect of the harness.** The search of each cluster's roles
  and settings was handed to the shell as two arguments, so its second half never ran and nine clusters were
  reported "not searched whole". Fixed; NOT RUN again. Everything else in that trial held (the other two
  problems were images `m6-b9j` never built).
- **`PerformanceResearch`, in progress (00:07 to about 07:58 UTC).** MEASURED so far on synthetic rows of full
  density, the research cluster at one CPU: a load of 27 days in 1,713 s (8.3 GB); sealing 21 days in 615 s
  and 14 days in about 420 s (about 8,700 rows a second in a container of the bridge's size). **A screening
  job on 21 days did not finish in the 2,160 s the harness could give it:** 679 s passed before its first
  cell, and neither cell completed in the remaining 1,481 s, the first of them covering 9.6 stepped days. That
  is more than 154 s for a stepped day; the reservation estimate was 975 s for the whole job. A missed
  measurement is a failed phase and a point for the owner, not a changed budget: the complete figures and the
  options follow when the phase's remaining parts have run.
- **Order of phases.** INFERRED from the code, never run in that order: `Migration` would fail after
  `Staging`, `ShadowSchedule`, the process part of `AgentFaults6` or `PerformanceResearch`, because it asserts
  what the migration left on a cluster those phases then change. It ran first on this run and passed; it
  must stay before them.
- **A gap in the product, found and not changed.** A research job's own `workflow_id` is never written,
  although the job view returns it: a job requested by an agent shows no workflow. For the owner: fix it in
  this batch with a test, or record it as known and fix it afterwards.
- **The real pilot beside the run:** unchanged at every reading; one collection gap noted, no stop. Not this
  session's work: the session of the retention fix reports the normal market worker recreated from its fix at
  21:22:06 UTC on 2026-10-07 on the owner's approval in that session, two hourly retention passes without a
  failed call, and its PR merged, so `main` is ahead of this branch.

**Market worker: a retention call the database ends no longer ends the worker (ExecPlan 0024) — implemented and verified in isolation on 2026-10-07; delivered as pull request #31; DEPLOYED to the normal app's market worker on 2026-10-07 at 21:22 UTC with the owner's approval; the soak of two hourly retention passes passed, and the merge follows this record.** Pull request [MentorAliu/adaptive_spot_lab#31](https://github.com/MentorAliu/adaptive_spot_lab/pull/31) was opened at 20:52 UTC with the code commit `9c7c87d` and the documentation commit `5cae96e`; a further documentation-only commit records this number. OBSERVED owner instruction of 2026-10-07 ([decision](../DECISIONS.md#2026-10-07--market-worker-a-retention-call-the-database-ends-must-not-end-the-worker-execplan-0024)), with the finding it carries: the normal market worker exited twice on 2026-10-06, at 13:51:57 and 15:53:56 UTC, because the two-second statement deadline ended a call of its hourly retention, and Docker restarted it about 30 s later. It did so a third time at 20:01 UTC on 2026-10-07, while this change was being verified. The plan is [ExecPlan 0024](plans/0024-retention-failure-keeps-the-worker.md).

- **IMPLEMENTED** (branch `claude/market-retention-timeout`, code commit `9c7c87d`, from `main` at `0f395a9`; market worker code only, no schema change):
  - A database error in a retention call ends that attempt and nothing else. The socket, the generation, its epoch and the capture stay, and no `COLLECTION_GAP` is recorded.
  - The pass is tried again 60 s later. The wait doubles up to the normal hour only while attempts complete no call. No hour has more than 32 calls, failed and cancelled ones included.
  - Every failed attempt is one incident: `RETENTION_FAILED`, and `RETENTION_STALLED` once no call has completed for three hours. The first completed pass writes `RETENTION_RECOVERED`. The contract is in [MARKET_DATA](../MARKET_DATA.md), the reading of the records in [OPERATIONS](../OPERATIONS.md).
  - A lost lease still stops the worker, and the function's own lease refusal is raised as one.
  - A rotation or a new collection waits up to three seconds for a retention call that still runs. Without that wait a rotation that met such a call ended the worker on the lease row the call held. An independent review found this; it was reproduced on the unchanged worker.
- **VERIFIED in isolation** (run `ret-1007b` at that commit, fresh databases, synthetic data; [the plan's §12](plans/0024-retention-failure-keeps-the-worker.md#12-verification-isolated), commands in [COMMANDS](COMMANDS.md#execplan-0024-commands--2026-10-07)):
  - The two deadline cases, the start-up case and the rotation case failed on the unchanged worker with the database's error, the statement case at the statement and function line of 2026-10-06.
  - `WorkerFaults` 75 passed. The M0–M2 test files 76 passed. The M3 and M4 test files 169 passed. Ruff and the OpenAPI check passed. `RecoveryMemory` passed.
  - `PerformanceDensity -RetentionFaults` at 1.8 million stored observations: the database ended the first call of two retention attempts under the stream. No budget failed, 1,780 of 1,780 frames were published (receipt to publication p99 122.9 ms), every usability sample was usable, the collection stayed the same, and the third attempt removed 14,746 observations and wrote `RETENTION_RECOVERED` 3 min 56 s after the first failure.
  - `PerformanceBurst`: 30,000 of 30,000 frames published, receipt to publication p99 173.4 ms.
- **OBSERVED cost of one call** (isolated, 1.8 million synthetic observations; [§4](plans/0024-retention-failure-keeps-the-worker.md#4-why-one-call-can-pass-its-deadline)):
  - A warm call of 500 observations takes about 0.35 s, three quarters of it the checks of twelve references.
  - The first call after the database's buffers were emptied read 11,182 pages (87 MB), 9,384 of them for the selection of orphan payloads, which examines every expired payload whatever the call size. Both exits of 2026-10-06 were the first call of an hourly pass.
  - Both references to `market_payloads` are indexed. Five references from `strategy_evaluations`, `orders` and `fills` to `market_observations` are not, and their check grows with those tables: 15 ms a call at 0 rows, 119 ms at 2,700, 0.7–0.9 s at 17,500.
  - INFERRED, not measured on the normal app: the first call of a pass passes its deadline when those pages are not cached or the disk is busy. A smaller batch alone would not have prevented the two exits.
- **Two older tests corrected.** Two clock tests of ExecPlan 0022 failed by timing on the unchanged worker as well. One contradictory assertion is removed, and one assertion now waits for what it reads. Some of their failures on a database used for hours were time-outs whose cause is NOT KNOWN ([§8](plans/0024-retention-failure-keeps-the-worker.md#8-requirements-and-tests-implemented-results-in-12)).
- **NOT RUN:** the web part of `Checks` and the web build (no file under `apps/` changed); the test files of M5 and M6 (none imports the changed modules); density levels other than 1.8 million; a second review of the corrections made after the first.
- **Open with the owner** ([§7](plans/0024-retention-failure-keeps-the-worker.md#7-decisions-for-the-owner)): the retry with a smaller batch and the selection of orphan payloads need a new function, a schema change; indexes on the five M3 reference columns; optional read-only reads of the normal app (two queries, and the retention lines of the worker's log for 2026-10-07).
- **The normal app runs the change since 21:22:06 UTC on 2026-10-07** ([record](plans/0024-retention-failure-keeps-the-worker.md#131-executed-2026-10-07-21202122-utc-owner-approved), [decision](../DECISIONS.md#2026-10-07--market-worker-deployment-approved-then-the-merge-execplan-0024)). OBSERVED owner decision at about 21:00 UTC: deploy first, then merge after two hourly retention passes.
  - **What ran, 21:20–21:22 UTC:** a protected backup (444,703,335 bytes, SHA-256 `7a1e8f9c…17b6`, in the primary checkout's `.cache/deployments/retention-failure-20261007T212001Z/`), the rollback tag `adaptive-spot-lab-market-worker:pre-0024` on the previous image `sha256:0d4d29bb4765…`, one image built from the clean pull-request head (`sha256:31ee07e57436…`), and the recreate of `market-worker` alone.
  - **VERIFIED read-only:** the image's 145 application files equal the source hashes that the acceptance run recorded at `9c7c87d`; the eight other containers kept their container, image and start time; the new worker (`82c8f5475b24`, started 21:22:06) took lease epoch 2193, removed 6,013 expired records in its start-up pass and connected its stream at 21:22:21; no observation was published for 19 s; both feeds were `CONNECTED` and the pilot unchanged at 21:23 (RUNNING, version 3, lease epoch 4, no open position, no new incident).
  - **The hourly retention pass now runs at about HH:22**, moving about 16 s later each hour, because a restart starts its schedule again. It is no longer inside HH:58–HH:07.
  - **Soak PASSED (read-only, 22:26 and 23:27 UTC).** Both hourly passes completed without a failed call: 19,430 records at 22:22:34 (20 deleting calls) and 15,901 at 23:22:47 (17). Same container, restart count 0, one collection, no market incident since the swap, the pilot unchanged. No call failed, so the new handling itself has not yet been seen at work on the normal app.
  - **The merge** of pull request #31 follows this record, as approved, pinned to its head with an ordinary merge commit. Rollback of the deployment is the tag `:pre-0024` and the same recreate command.
  - **Before the deployment** the worker still ended when the database ended a retention call, at a cost of about 30 s of quotes:
  - **The third exit** (OBSERVED by the session of ExecPlan 0023, which read the log with the owner's approval): the collection ended at 20:01:23 UTC on 2026-10-07 with the same error at the same statement and function line, the container restarted at 20:01:27 (restart count 3), and the start-up pass removed 20,460 records.
  - No test load of either session ran at that minute. Both sessions' isolated stacks had been busy in the hour before. Whether that contributes is NOT KNOWN ([§2.5](plans/0024-retention-failure-keeps-the-worker.md#25-a-third-exit-while-this-plan-was-being-verified-observed-by-the-session-of-execplan-0023)).
  - Until the approval this session addressed no command to the normal app; one unfiltered `docker stats` listing at 14:05 UTC showed its containers' resource figures ([COMMANDS](COMMANDS.md#execplan-0024-commands--2026-10-07)).
- **Docker.** The three isolated runs of this task were removed by exact name once their evidence was recorded: 6 volumes, 12 images, and their containers and networks. Nothing whose name starts with `asl-m2-ret-1007` remains. The evidence files stay under the worktree's ignored `.cache/m2/`.

**M6 B9: the watch stopped run `m6-b9k` for a restart of the market worker; two owner decisions; the run goes on (2026-10-07, 20:30 UTC).**
NOT ACCEPTED. OBSERVED:
- **The stop.** The normal market worker restarted at 20:01:27 UTC (restart count 2 to 3, same container and
  image). The watch saw it at its first reading after the quiet window, 20:11:45 UTC, and stopped the run, as
  the rule of that morning says. The stop cut the process part of `AgentFaults6` four minutes after it began.
- **The run was idle at that minute.** Run `m6-b9k` had no container up and issued no Docker command from
  19:32:51 to 20:07:00 UTC. No command of any test run of this session was in progress at the two restarts of
  2026-10-06 either. The session of the retention fix reports that no load of its own ran from 19:51:32 to
  20:07:08 UTC, and that its test stacks were busy in the hour before.
- **The cause, from the market worker's log** (one read-only call, 19:55 to 20:05 UTC): the same failure as on
  2026-10-06. The delete in `asl_prune_market_evidence` was canceled by its statement timeout at 20:01:23 UTC,
  the worker took that as fatal, and it was collecting again after the restart, where the same delete then
  went through.
- **The pilot otherwise:** lease epoch 4 held, the forward checkpoint advancing, no new execution incident,
  segment or downtime event; one `COLLECTION_GAP` on the market side.
- **Two OBSERVED owner decisions at about 20:17 UTC**
  ([DECISIONS](../DECISIONS.md#2026-10-07--m6-b9-a-restart-of-the-market-worker-alone-beside-a-test-run-and-its-log)):
  one read-only log read for each restart of the market worker during B9; and a restart of the market worker
  alone whose log shows that retention failure is recorded and no longer stops a test run, while a second one
  within three hours does. IMPLEMENTED in `tools/lib/Research.psm1` and `tools/m6-pilot-watch.ps1`, with the
  pilot rule cases now 54 (all hold, run without Docker); the log read was tried on an isolated test container.
  NOT RUN: the rule on a real restart. The owner scripts are unchanged: they still stop on any container
  change.
- **The run goes on** since 20:20 UTC with the phases that have not passed, the never-run measurements first:
  `AgentOffline6` VERIFIED at 20:24 UTC, then `AgentFaults6`, `PerformanceResearch`, `ResearchSaturation`, the
  browser phases, `PerformanceApi`, `PerformanceBrowser`, `SecretScan`, `Report`. Before the stop, on this run:
  Build, Generate, Checks and `Regression` VERIFIED (`Regression` in 17 minutes; it hung for two hours on
  `m6-b9j`), and the fault helper's preparation step passed in the process part of `AgentFaults6`.
- **A risk the owner accepted, with what is known about it.** INFERRED by the session of the retention fix from
  its isolated measurement, not measured on the normal app: the first retention call of an hour reads about
  11,000 pages, and when other containers' work has pushed those pages out of the Docker VM's cache, the call
  can miss its statement timeout (two seconds by that session's account). If that is so, a heavy test phase makes a restart at the next hourly retention
  likelier even though it does not run at that minute. The hourly retention ran at about HH:01 UTC this
  evening.
- **Since then (20:45 UTC): the rest of `m6-b9k` was stopped by hand and a fresh run is prepared that can
  count.** The owner asked whether M6 can be shortened. `m6-b9k` could never be accepted, because its harness
  was edited while it ran, so a second full run of about a day would have followed it. The implementer's
  change of plan, told to the owner: the next full run, `m6-b9l`, starts fresh on the committed tree with the
  never-run phases first. If every phase passes it is put to the owner as the acceptance run; if a phase fails
  on a defect it is the authoring run it would have been. What that means for the evidence, for the owner to
  accept or reject in the B9 report: the accepted run would also be the first in which `PerformanceResearch`
  and `ResearchSaturation` ran to their end, and the independent reviews of the fix round were done before
  it. Before it starts: `Report` was tried on `m6-b9j` and `m6-b9k` (it runs through, lists the missing phases
  and the changed tree, and lists the cut attempt of `AgentFaults6` as a rerun with its cause); `SecretScan`,
  which has never run to its end, is tried on `m6-b9j` in the 21:07 UTC window; and two independent read-only
  reviews looked at the four harness commits made since the last review and at the fields `Report` reads from
  the measurement phases.
- **What the two reviews found (21:00 UTC).** The fields: no mismatch in the 53 rows of a full run, by a
  static trace of both sides (three of the four measurement phases have no passing record to compare with).
  The four commits: one defect that would have stopped a run wrongly. The watch recognised the retention
  failure only when at most 600 characters lay between the cancellation and the name of the retention
  function; at the restart of 2026-10-06 15:53 UTC the canceled statement ran over many lines and more lay
  between them. FIXED: the first function named after the cancellation decides, and each of the three real
  restarts is now classified as the retention failure from the kept extracts. Also fixed: `Report` now
  refuses a phase that was started again after an attempt that had passed (the owner allowed a rerun of a
  failed or interrupted phase only) and takes the cause of a rerun from the attempt's own error when no
  failed record names one; a restart that came with new `PROTECTION_UNAVAILABLE` rows stops a run, as the
  owner's text asks for execution incidents unchanged; the watch names the phase at a restart and begins no
  reading in the last half minute before HH:58; and a process number is checked against its creation time
  before a left-over child of a cut call is ended. The pilot rule cases are 57 now and all hold; `Report`
  on `m6-b9k` and the cut-off test without Docker were run again. NOT RUN: any of this in a phase.

**M6 B9: authoring run `m6-b9j`, sixteen phases passed, two harness defects found and fixed, stopped by hand (2026-10-07, 19:00 UTC).**
NOT ACCEPTED. OBSERVED on run `m6-b9j` (13:49 to 18:50 UTC, the tree of commit `2f6a3a7`):
- **Sixteen phases VERIFIED on their first attempt**, among them `ResearchActivationRehearsal` (the rewritten
  owner scripts against containers for the first time), `MixedVersion` and `PilotCoexistence`.
- **`AgentFaults6`, process part, FAILED** on a defect of its own fixture (it named the wrong database to a
  fixture guard). Fixed; NOT RUN again yet.
- **`Regression` HUNG for two hours**, and the pass with it. The six M0 to M2 files that B9 added ran under a
  database role without a lock timeout, and one test then waits for ever. Fixed: they run under the API role.
- **The hang exposed a defect of the harness, older than B9: a call that reached its limit did not end.** The
  harness ended the Docker client and not the client's child process, and then waited for it. A phase's
  deadline was therefore not enforced on such a call. This time two idle test containers stayed up through the
  quiet windows of 16:58 and 17:58 UTC. Fixed and tried without Docker (a cut call returns in seconds and
  leaves no process); NOT RUN in a phase yet.
- **The real pilot was not disturbed** by the watch's rule: 50 readings, every container and the lease as
  before, no execution incident, six hourly reports in their HH:05 minute, one collection gap recorded
  ([ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b9--rollout-measurements-faults-scan-and-report)).
- **NOT RUN yet in any form to its end:** `ResearchSaturation`, `PerformanceResearch`, `SecretScan`, `Report`;
  on this tree also `AgentOffline6`, the browser phases, `PerformanceApi` and `PerformanceBrowser`. A second
  authoring run with the three fixes comes next.
- **Since then (19:10 UTC):** the two phase fixes were checked on the stopped run's own containers (the six
  files: 64 passed in 21 s; the fault helper's `prepare`: passed) and committed as `a44ccb0`. A second authoring
  run, `m6-b9k`, started at 19:11 UTC with the phases that have not passed yet. Two more OBSERVED owner
  decisions
  ([DECISIONS](../DECISIONS.md#2026-10-07--m6-b9-a-full-test-at-the-21-day-cap-and-reruns-in-an-accepted-run)):
  a failed or interrupted phase may be started again on the same Build, on record, with each rerun put to the
  owner (IMPLEMENTED in `Report`, NOT RUN); and, if the measurement confirms that a full test at the 21-day cap
  misses the job bound, the replay is to be fixed provided results stay identical. On reading the code the
  implementer found that the change as it was named removes under a tenth of that job's work, because the
  warm-up is 302 hours; whether a deeper change keeps results identical is NOT ESTABLISHED, and whether any
  change is needed waits for the measured rates
  ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)).

**M6 B9: four owner decisions taken and implemented; the market worker's restarts explained; test runs may resume (2026-10-07, 14:00 UTC).**
OBSERVED owner answers at about 13:26 UTC in the M6 B9 session's question dialog
([DECISIONS](../DECISIONS.md#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log)).
B9 is still NOT ACCEPTED and no phase has run since 2026-10-06 21:18 UTC; what follows is IMPLEMENTED and checked
without a stack only.
- **What stops a test run beside the pilot.** At once: a container or lease change, a new segment or downtime
  event, `QUEUE_OVERLOAD`, a missing HH:05 report, or an execution incident other than `PROTECTION_UNAVAILABLE`.
  As a burst: more than two collection gaps or more than four `PROTECTION_UNAVAILABLE` pairs in thirty minutes.
  The rule is in `tools/lib/Research.psm1` with 31 cases; `tools/m6-pilot-watch.ps1` applies it
  ([OPERATIONS](../OPERATIONS.md)). Replayed through it, the 161 readings of the series with no test running give
  no stop.
- **The owner scripts report the pilot's own rows.** `tools/m6-deploy.ps1` and `tools/research-activate.ps1` name
  `PROTECTION_UNAVAILABLE` rows recorded during their run and go on; any other new execution incident still
  stops them.
- **The schema change stays in migration 0008**: three indexes and `research_datasets.purpose`.
- **OBSERVED from the real market worker's log** (one read-only call, 2026-10-06 13:40 to 16:20 UTC): both
  restarts of that day were its hourly retention canceled by the database statement timeout, which the worker
  takes as fatal. It was collecting again about 30 s later each time. At the first one no isolated test stack
  existed; at the second one stack was up and idle. Why the statement was slow is NOT KNOWN. It is a defect of
  the market worker, outside this batch, and was flagged as a separate task; the worker is not changed here
  ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)).
- **Next:** an authoring run with every fix, watched by the new watch; then one fresh acceptance run. Still open
  for the owner: the jobs at the 21-day cap once they are measured, and the rule that an accepted run starts
  every phase once.

**Env-file path PR merged; `main` merged into the M6 B9 branch (2026-10-07, 13:15 UTC).** VERIFIED read-only at
13:01 UTC by the M6 B9 session: pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30) is MERGED as
`0f395a995880dc4ad43831570376eebc10c74c1e` at 12:59:54 UTC, an ordinary merge commit with parents `4ece326` and
`f0e8c89`; `main` is `0f395a9`. The session that wrote that pull request merged it, on the owner's instruction of
the entry below; the M6 B9 session merged nothing on GitHub. It then merged `main` into its local branch
`claude/m6-b9-final-acceptance` (merge commit `73789b9`, not pushed, no pull request). Three documents held
entries of both sessions at one place; every entry is kept, here newest first.
- **The primary checkout now holds the corrected pilot and agent tools**, because it is on that branch: the four
  tools write the resolved env file and `tools/lib/Pilot.psm1` stops on an error in its own functions. This
  branch changes one function of that module, `New-ProtectedBackup`, which those tools call for their backup:
  it removes the dump from the `postgres` container also when the dump or its copy failed. The line this
  branch had added inside that function to stop on an error is removed, since the module now does that.
  In its present form the function has run against stand-ins only (NOT RUN against a PostgreSQL container:
  the M6 rehearsal that would do so has not run since the function changed). On success it makes the same
  calls as the function on `main`. `tools/pilot-deactivate.ps1 -SkipBackup` does not call it.
- **Checked after the merge, without a stack:** the parser on all 44 scripts under `tools` (0 errors); the M6
  env file cases (47 held); the M6 deploy script against its model (17 scenarios, 72 expectations);
  and `tools/env-file-path-check.ps1`, the check that came with #30, on the merged tools at 13:10 UTC (12 of 12 cases
  passed; a function stands in for `docker`). Three of the four tools it runs take their backup through this
  branch's `New-ProtectedBackup`.
- **NOT RUN:** any phase, any `pytest`, `ActivationRehearsal` and `AgentActivationRehearsal`. Nothing is
  deployed, enabled or approved, and no command addressed the normal application. The state of M6 B9 is the
  entry of 12:30 UTC below: not accepted, and no test run until the owner decides what stops one.

**Env-file path PR: merge requested (2026-10-07, 12:58 UTC).** OBSERVED owner
instruction in the same Claude Code session, after pull request #30 was
reported: `merge it`
([decision](../DECISIONS.md#2026-10-07--owner-asks-to-merge-the-env-file-path-pr)).
VERIFIED read-only first: commits `aa12223`, `39d852c`, `a7ee675` and
`d8534ff` are pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30),
open, mergeable and clean at head `d8534ff` with no check run; `main` is
still at `4ece326`, the commit the change was branched from and checked on,
so nothing has to be merged into the branch and nothing has to be run again;
no other pull request is open. The PR is merged with an ordinary merge commit
pinned to its verified head, without force, an admin bypass or branch
deletion. This entry is written before the merge and does not claim it;
GitHub records the actual merge commit, and the next documents on `main`
record it here. The merge changes files only: a tool is corrected in a
checkout once that checkout holds the merge, and the primary checkout is on
the M6 B9 branch. `ActivationRehearsal` and `AgentActivationRehearsal` stay
NOT RUN on the changed tools, and the writer and the reader stay as they are
until the follow-up after the B9 merge. Nothing is deployed, enabled or
approved, and no command addressed the normal application.

**M6 B9: the review findings are fixed in the tree; nothing run since 2026-10-06 21:18 UTC (2026-10-07, 12:30 UTC).**
NOT ACCEPTED, and no test has run since the watch of decision 8 stopped run `m6-b9i`. What is new:

- **OBSERVED, the real pilot with no test running** (read-only series, 2026-10-06 21:25 to 2026-10-07 13:14 UTC,
  161 readings, none failed, no isolated stack on the host; the series was ended at 13:15 UTC because it had
  served its purpose): `PROTECTION_UNAVAILABLE` rows went from 488 to 510, all in the first four hours; two
  collection gaps with a silent stream were recorded; the market worker recorded one `CLOCK_UNCERTAIN` and one
  `CLOCK_UNVERIFIED` row. No container restarted; the lease stayed at epoch 4 and held in every reading.
  The pilot writes these rows on its own, and decision 8 as written stops a test run on the first two kinds.
  **No test runs until the owner decides what stops one**
  ([ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks)).
- **Four read-only reviews so far.** The second (three reviewers on commit `da01a04`) gave 34 findings; the third
  read the reworked owner scripts and gave 13; the fourth read the reworked measurements and gave nine, none of
  which would stop a first run. Their fixes are IMPLEMENTED (local commits `3d87ba0` and `eb1bf82` on
  `claude/m6-b9-final-acceptance`, not pushed, no pull request) and checked only without a stack: the PowerShell parser on every script,
  `ruff` on the whole engine tree and byte-compilation, the scripts' env file rules on local files (47 cases),
  and the deploy script against a model of an installation (17 scenarios, 72 expectations; a function answers
  for `docker`). **NOT RUN: every new or changed test and every phase.** What changed is in
  [ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b9--rollout-measurements-faults-scan-and-report).
- **A defect of this batch's own env-file reader, found today before any run against an installation.**
  OBSERVED with Docker Compose 5.5.1 on this host: a key in another letter case is read as the key when the
  exact spelling is absent, so `asl_research_enabled=1` sets the research flag. The reader took that flag for
  unset, and the deploy script would have reported such an installation as inert. Fixed: the deployment and the
  activation refuse such a file, and the writer rewrites every spelling
  ([SECURITY](../SECURITY.md), [OPERATIONS](../OPERATIONS.md)). The older M4 and M5 tools read the env file with
  their own reader and are not changed in this batch; a separate pull request (#30, merged at 12:59 UTC, see
  the first entry) corrects their path.
- **A defect that could have left a test stack running into the quiet window, found by the fourth review by
  reading; fixed, NOT RUN.** Once a part's work deadline had passed, the cleanup of `PerformanceResearch`,
  `ResearchSaturation`, `PilotCoexistence` and the process part of `AgentFaults6` threw before it stopped its
  containers. The cleanups now lift the deadline first. The same review found two measurements that could
  pass without proving their claim (the 21-day shadow projection, and a worker that stops looking at
  publications near the end); both are judged more strictly now
  ([ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b9--rollout-measurements-faults-scan-and-report)).
- **The measurement phases changed shape.** `PerformanceResearch` now has eight parts of one test window each
  and `ResearchSaturation` two; with the rule that every phase is started once, an acceptance run is more than
  a day of windows ([TESTING](TESTING.md#m6-b9-rollout-saturation-performance-faults-and-final-acceptance-execplan-0023)).
- **Three more product defects found by the second review, fixed, their tests NOT RUN:** a second bridge process could
  record a healthy store as lost (it read the store before the catalog); the runner's free-space reading ended
  with its first failed lease renewal while the job went on; and, INFERRED, the replay held every quote before a
  late cell's start in memory, which at real quote density would have exhausted the runner's memory on any 21-day
  job. Research services had no log limits.
- **The deploy script was rewritten** where the review found it could strand a broken release: `-Rollback` now
  works from a release with a service down, an unreadable image name or a failing `git` is an error and no longer
  an answer, the restore rehearsal's fingerprints can no longer be an error text, and a rollback tag is created
  only from an image the caller names ([OPERATIONS](../OPERATIONS.md)).
- **Open for the owner, unanswered:** the schema change in migration 0008; what stops a test run, and whether the
  deploy and activation scripts stop on the same rows; permission to read the market worker's log; the INFERRED
  design points of research jobs at the 21-day cap. New on 2026-10-07: whether a projection may fall back to
  another figure when a job's cells do not give two rates (it fails the phase now); the saturation feeder's
  29-hour hold on the seven-day store; whether every phase must be started exactly once in an accepted run,
  now that one run is more than a day of windows. Listed in §19.
- **NOT DONE:** `Clean` of the runs `m6-b9obs` and `m6-b9e` to `m6-b9i` (the lint container of the static
  checks is `m6-b9i`'s engine test image); any push or pull request for this batch.

**Pilot and agent tools: a failed write stops the tool; added to pull request
#30, not merged (2026-10-07, 12:10 UTC).** OBSERVED owner decisions at about
11:52 UTC, in the question dialog of the session that opened pull request #30
([decision](../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out)):
the reader and writer replace `Set-EnvFlag` and `Get-EnvValue` only after the
M6 B9 pull request is merged, on that branch's code; and the point the entry
below left open is corrected in pull request #30. IMPLEMENTED:
`tools/lib/Pilot.psm1` sets `Stop` for its own functions, so an error in them
stops a tool also when it is called by its path from a PowerShell session.
Started with `powershell.exe -File`, as the rehearsals and both owner
activations were, nothing changes. `tools/env-file-path-check.ps1` now has
twelve cases: each tool is also called with a read-only env file, and the
path cases run the backup step against the stand-in and require the database
of the file given. OBSERVED: 0 of 12 cases passed on the tools as at
`4ece326`, and 8 of 12 with the path correction alone, where every tool ended
without an error although its flags could not be written and both activation
tools went on to start the workers. VERIFIED with the module change: 12 of
12. NOT RUN, as in the entry below: `ActivationRehearsal`,
`AgentActivationRehearsal`, the link check in its container, GitHub CI; and
`pilot-market-dump.ps1`, `agent-login.ps1` and `m5-deploy.ps1`, which use the
module too, in any form. NOT CHANGED: the writer and the reader themselves;
their limits stay as
[OPERATIONS](OPERATIONS_M3_M7.md#m4-pilot-operations-execplan-0015) states them
until the follow-up after B9, which is not started. No command addressed the
normal `adaptive-spot-lab` project, no container was started and nothing was
deployed, enabled or approved. Delivered as commit
`a7ee675200cca4dc4667a275d97a66159559f65d` (9 files), pushed to pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30)
at 12:12 UTC, whose description now covers both corrections. The pull request
stays open and unmerged; the owner decides. See
[COMMANDS](COMMANDS.md#second-step-the-same-day-a-failed-write-stops-the-tool).

**Pilot and agent tools write the resolved env file; on its branch, not merged
(2026-10-07, 11:41 UTC).** OBSERVED owner instruction in a separate Claude Code
session: correct two findings of an independent review of 2026-10-06 in the
owner tools that are older than M6
([decision](../DECISIONS.md#2026-10-07--pilot-and-agent-tools-the-env-file-path-and-what-was-left-out)).
VERIFIED read-only first, which also records what the entry below left open:
pull request #29 is MERGED as `4ece326e29c7dd1239003b71ac8eca643159ee85` at
12:49:48 UTC on 2026-10-06, from head `26aad18`; `main` and `origin/main` are
at that commit and no pull request was open. VERIFIED also: the reader and
writer the instruction names as existing (`tools/lib/Research.psm1`) are in no
commit of `main`; they are on the local, unpushed B9 branch, the two functions
only in its working tree. This change is therefore limited to what needs none
of that code. IMPLEMENTED on `claude/owner-tools-env-file-path` from
`4ece326`: the six calls of the flag writer in `tools/pilot-activate.ps1`,
`tools/pilot-deactivate.ps1`, `tools/agent-activate.ps1` and
`tools/agent-deactivate.ps1` take the resolved path that every Compose call of
the same run names, instead of the `-EnvFile` text as typed; and
`tools/env-file-path-check.ps1`, which calls the four tools from new
PowerShell sessions with a relative path, another process directory and a
stand-in for `docker`. OBSERVED with it on the tools as they are at `4ece326`:
0 of 8 cases passed; the flags in the file given stayed as they were, and a
file of the same name in the process directory was created or rewritten.
VERIFIED on the changed tools: 8 of 8. The default path was never affected,
and both owner activations (M4-B, M5-B) used it. NOT CHANGED: the writer and
the reader in `tools/lib/Pilot.psm1`. Their limits were OBSERVED on temporary
files and against Docker Compose v5.5.1 and are now stated in
[OPERATIONS](OPERATIONS_M3_M7.md#m4-pilot-operations-execplan-0015): a later
`KEY: value` or `export KEY=value` line is not rewritten and is the one
Compose reads; the file is rewritten with CRLF line ends, without a byte-order
mark and not in one step; the reader returns the first assignment, with its
quotes. OBSERVED and left open: called by its path from a session, a tool does
not stop when the write of a flag fails, so a deactivation can end without an
error while a flag still reads `1`; started with `powershell.exe -File` it
stops. NOT RUN: `ActivationRehearsal` (M4) and `AgentActivationRehearsal`
(M5), which run the tools against Docker, because the owner limited this
change to tests on isolated files; the documentation link check in its
container (the links of the changed documents were checked with a PowerShell
reading of the same rules); GitHub CI. No command addressed the normal
`adaptive-spot-lab` project, no container was started and no Docker resource
was created; `docker compose config` read temporary files under the project
name `asl-envfile-check`. Nothing was deployed, enabled or approved, and the
running pilot is not touched: the next call of a tool uses the changed file
only from a checkout that holds it. This is not a batch of ExecPlan 0023.
Delivered as commit `aa12223fd28bb8ca2829780eab9ecd36eb0c4172` (12 files) in
pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30),
created at 11:48:08 UTC on 2026-10-07, open, mergeable, without a check run
and not merged; the owner decides, and two points are put to the owner (when
the reader and writer are replaced, and whether a session call should stop on
an error). See
[COMMANDS](COMMANDS.md#owner-tools-write-the-resolved-env-file-2026-10-07) and
[ExecPlan 0015 §16](plans/0015-evaluation-fixed-pilot.md#correction-after-activation--which-env-file-the-tools-write-2026-10-07).

**M6 B9 implemented, not accepted; test runs stopped for owner decisions (2026-10-06, 21:30 UTC).**
IMPLEMENTED on branch `claude/m6-b9-final-acceptance` (local commit `3d10fec`, not pushed, no pull request yet):
the phases the plan left for B9 (`MixedVersion`, `PilotCoexistence`, `ResearchActivationRehearsal`,
`ResearchSaturation`, `PerformanceResearch`, `PerformanceApi`, `PerformanceBrowser`, `SecretScan`, `Report`), the
process-level faults of `AgentFaults6`, the phase `BrowserRegression`, and the owner scripts `tools/m6-deploy.ps1`,
`tools/research-activate.ps1`, `tools/research-deactivate.ps1` and `tools/m6-pilot-check.ps1`
([TESTING](TESTING.md#m6-b9-rollout-saturation-performance-faults-and-final-acceptance-execplan-0023),
[OPERATIONS](../OPERATIONS.md)). Eight owner decisions preceded the code
([DECISIONS](../DECISIONS.md#2026-10-06--m6-b9-phase-content-images-saturation-length-job-measurement-row-counts-quiet-window-lost-store-regression-and-the-read-only-look)).
**No acceptance run exists.** Every run so far is an authoring run on an uncommitted tree; what each showed is in
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b9--rollout-measurements-faults-scan-and-report).

- **OBSERVED on authoring run `m6-b9i`** (Build 20:07 UTC): the extended rehearsal passed (five deployments, two of
  them stopped at a blocked migration, two rollbacks, five activations, a lost cluster), as did `Generate`, `Checks`,
  `Migration`, `ApiAuth`, `Staging`, `ShadowSchedule`, `ResearchRunner`, `HoldoutIsolation`, `SourcePolicy`,
  `EvidenceInjection`, `DispatcherAuth6`, `EngineParity`, `BrowserResearch`, `BrowserResearchError` and
  `PerformanceApi`. `MixedVersion` and `BrowserRegression` passed on `m6-b9h`, `PilotCoexistence` on `m6-b9f`.
- **NOT RUN to the end on any run:** `ResearchSaturation`, `PerformanceResearch`, the process part of `AgentFaults6`,
  `SecretScan`, `Report`. `PerformanceBrowser` failed once on a defect of its own row lookup (fixed, not rerun).
- **Two product defects found by the first independent review, fixed with tests:** the bridge sent a queued job into
  a research cluster that had been lost and initialized again when its first pass relayed before it staged (it now
  compares a store with the catalog before anything is sent to it and reads recorded losses when it starts); the
  runner published its free-space reading only between jobs, so staging stopped ten minutes into a long job (it now
  publishes while a job runs).
- **A missed budget, put to the owner before the fix was kept (decision 4 of 2026-10-06):** on one year of rows at
  the envelope's caps five API routes missed the budget (`/v1/research/status` 369 ms sequential p95 against 250 ms,
  2,025 ms with five readers against 500 ms). The journal table `research_staging_runs` had no index, a dataset's
  purpose was read out of its manifest, and one status read compared a column with the running clock. With the fix
  the same measurement reads 43 ms and 245 ms for all routes together and 80 ms and 481 ms for the slowest route.
  The fix is PROVISIONAL: three indexes and a stored generated column in migration 0008 (never applied to the normal
  database), and query changes. The owner was asked whether it stays in 0008 in this pull request; no answer yet.
- **INFERRED, not measured:** every cell of a job replays the market from the dataset's first row, while the time
  reservation counts each partition once. A full test on the 21-day cap would replay about 88.8 recorded days, about
  5,100 s at B0's rate, above the 3,600 s job bound. `PerformanceResearch` measures the 14-day full test and
  projects 21 days; it has not run.
- **The real pilot.** The read-only check script had a defect until 20:45 UTC and had never run. Its first readings
  showed that the real market worker restarted twice on 2026-10-06 (last start 15:53:57 UTC) and recorded eight
  collection gaps between 13:50 and 16:12 UTC. The first three incidents happened while no isolated test container
  existed, and none happened after 16:12 while the tests went on; the cause is not known, and the worker's log is
  outside the approved read-only commands. Since 20:55 a watch stopped the test run on any difference, as decision 8
  is written. It stopped the run at 21:18:38 on one `PROTECTION_UNAVAILABLE` start and end pair, a kind of row the
  pilot also wrote at 20:51–20:54 with no test running. **No test has run since**, and none will until the owner
  decides how that row counts.

No command addressed the normal app except the approved read-only check. B10 is NOT RUN and waits for B9's
acceptance and its own approval.

**M6 B8 PR merged; B9 started (2026-10-06, 13:10 UTC).** OBSERVED owner
instruction in a Claude Code session: implement B9 of ExecPlan 0023 (the
remaining phases and the final M6-A acceptance) and then, only after B9 is
accepted and the owner has said yes in chat, B10 (the inert deployment).
VERIFIED read-only first, which records what the entry below left open: pull
request [MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29)
is MERGED as `4ece326e29c7dd1239003b71ac8eca643159ee85` at 12:49:48 UTC on
2026-10-06, an ordinary merge commit of head `26aad18` into `main` at
`2043fc0`; `main` and `origin/main` are at that commit with B0–B8, the tree is
clean and no pull request is open. The primary checkout was switched from the
merged B8 branch to `main` and fast-forwarded. B9 is branched from it as
`claude/m6-b9-final-acceptance`. Nothing of B9 is implemented or run yet: the
content of the phases the plan names without defining, and the points the plan
does not decide, are put to the owner before any code is written. No command
addressed the normal app. B10 is NOT RUN and waits for its own approval.

**M6 B8 PR: merge requested (2026-10-06, 12:47 UTC).** OBSERVED owner
instruction in the same Claude Code session, after the pull request was opened
and reported: `merge it`
([decision](../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b8-pr)).
VERIFIED read-only first: commits `fe85cec` and `1ab82be` are pull request
[MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29),
opened at 12:38:13 UTC on 2026-10-06, open, mergeable and clean at head
`1ab82be` with no check run; `main` is still at `2043fc0`, the commit B8 was
branched from and accepted on, so nothing has to be merged into the branch and
no phase has to be rerun. The PR is merged with an ordinary merge commit pinned
to its verified head, without force, an admin bypass or branch deletion. This
entry is written before the merge and does not claim it; GitHub records the
actual merge commit, and the next checkpoint's documents record it here. The
instruction decides none of the points the report left for the owner; they
stay open in
[ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks).
The merge deploys and activates nothing and approves nothing; B8 completes
neither M6-A nor any deployment, and B9 is NOT RUN.

**M6 B8 implemented and accepted in isolation (2026-10-06, 12:32 UTC).**
OBSERVED owner instruction in a Claude Code session: implement B8 of ExecPlan
0023 only (the owner pages for M6 and the same-origin server functions behind
them, verified by `BrowserResearch` and `BrowserResearchError` at 390 and
1440 px), on a new branch from `main`, in isolated stacks, delivered as a pull
request that is not merged until the owner says so. Six points were decided by
the owner before any code was written, and two B7 behaviors were decided the
same day
([decisions](../DECISIONS.md#2026-10-06--m6-b8-skill-loading-consequence-lists-navigation-detail-routes-refresh-intervals-and-the-state-before-migration-0008)).
VERIFIED read-only first, which also records what the entry below left open:
pull request #28 is MERGED as `2043fc0a9ab777e36b250acd5dd311f1deb994af` at
06:12:45 UTC on 2026-10-06, from head `c4dcec3`; `main` and `origin/main`
were at that commit, the tree was clean and no pull request was open.
IMPLEMENTED on `claude/m6-b8-owner-pages`: `/evidence` and one item;
`/research` with hypotheses, candidates with their lifecycle, every trial
including refused and failed ones, results one cell at a time in the M4 report
view under research labels, shadows, staging gaps and the research status; the
"Research and sources" section of Approvals, where a promotion offers Reject
only and says why; the three M6 templates in the start dialog, the grouped
profile diff and the two System rows; the same-origin functions behind them
with the session, Origin, CSRF, Host and strict-input rules of M4 and M5. Every
page has loading, empty, error, stale, pending and not-found states; what the
API marks as holdout or shadow is labeled; source and model text is plain
text; cancel, stop, reject, revoke, approve and refresh state the API's
consequence list before they are confirmed. The API gained additive
consequence lists only: no route, body, grant or migration changed. No
dependency or primitive was added; the official shadcn and Lightweight Charts
skills were read from the installed copies and project discovery was run
first. OBSERVED on run `m6-b8c`: all seventeen phases passed. Two independent
read-only reviews of that source rated no product finding high; one test
finding was high (the error browser test never reached an M6 page). Their
findings were fixed with tests: among them, the first revoke lists understated
what a revocation does, a stale read still offered its actions, and an unknown
outcome's key could be lost. VERIFIED on fresh run `m6-b8d`, one engine image
(`sha256:2bd935cf…`), without a skip and without a failed or superseded
record, 11:33 to 12:32 UTC: Build, `Generate` (no difference, on source equal
to the Build record), `ApiAuth` (5, 5 and 24), `Staging` (13),
`ShadowSchedule` (11), `ResearchRunner` (15 and 17), `DispatcherAuth6` (11
and 14), `AgentFaults6` (11 and 17), `SourcePolicy` (249),
`HoldoutIsolation` (9), `EvidenceInjection` (24 and 2), `BrowserResearch`
(61 sample and page tests on this run's own API responses, then 7 browser
tests), `BrowserResearchError` (1 before migration 0008, 1 with the API
stopped), `AgentOffline6` (M5: 14 and 84; new: 16 and 90, and the schema
probe), `Regression` (169) and `Checks` (407 engine tests; the web checks
with 155 unit tests and the build). `Migration` and `EngineParity` NOT RUN:
the migration, the grants and the shared engine are unchanged. NOT RUN and
not claimed: `PerformanceBrowser` and the other B9 phases, a screen reader, a
browser other than Chromium, the M5 browser phases. Every test used a
synthetic owner, fixtures, a scripted model on the recorded provider and the
loopback mock source: no model call, no public endpoint, no real source fetch.
Nothing was approved outside disposable fixture databases, nothing was
enabled, and no command addressed the normal app. The four runs were
cleaned by exact name (73 resources); the pinned Playwright base image is kept. GitHub CI
still does not run. B8 completes neither M6-A nor any deployment or
activation; B9 is NOT RUN. Delivered as commit
`fe85cecf715d4cdbfd125e30eb231a928f9fa285` (99 files) in pull request
[MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29),
created at 12:38:13 UTC on 2026-10-06, open, mergeable and not merged; the
owner decides. Points left for the owner are in
[ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks):
first among them a fourth consequence list beyond the three that were
approved, and three details implemented differently from the letter of the
decisions after the review. See
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b8--owner-pages-and-same-origin-functions)
and
[COMMANDS](COMMANDS.md#m6-b8-owner-pages-and-same-origin-functions-2026-10-06).

**M6 B7 PR: merge requested (2026-10-06, 06:09 UTC).** OBSERVED owner
instruction in the same Claude Code session, after the pull request was opened
and reported: `merge it`
([decision](../DECISIONS.md#2026-10-06--owner-asks-to-merge-the-m6-b7-pr)).
VERIFIED read-only first: commits `cf89f86` and `79acde3` are pull request
[MentorAliu/adaptive_spot_lab#28](https://github.com/MentorAliu/adaptive_spot_lab/pull/28),
opened at 23:18:56 UTC on 2026-10-05, open, mergeable and clean at head
`79acde3` with no check run; `main` is still at `d1f8d88`, the commit B7 was
branched from and accepted on, so nothing has to be merged into the branch and
no phase has to be rerun. The PR is merged with an ordinary merge commit pinned
to its verified head, without force, an admin bypass or branch deletion. This
entry is written before the merge and does not claim it; GitHub records the
actual merge commit, and the next checkpoint's documents record it here. The
instruction decides none of the points the report left for the owner; they
stay open in
[ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks).
The merge deploys and activates nothing and approves nothing; B7 completes
neither M6-A nor any deployment, and B8–B9 are NOT RUN.

**M6 B7 implemented and accepted in isolation (2026-10-05, 23:10 UTC).**
OBSERVED owner instruction in a Claude Code session: implement B7 of ExecPlan
0023 only (the owner API for M6, its OpenAPI document and the generated web
types), on a new branch from `main`, in isolated stacks, delivered as a pull
request that is not merged until the owner says so; three points were decided
by the owner before any code was written
([decision](../DECISIONS.md#2026-10-05--m6-b7-experiment-read-codes-canceled-jobs-and-rejected-promotions)).
VERIFIED read-only first: pull request #27 (the generation-1 trimming fix) is
MERGED as `d1f8d88c2672404ba081e76017ee82100ef5256c` at 14:06:19 UTC on
2026-10-05 and `main` is at that commit, which is the merge the entry below
was written before and did not claim. B7 was branched from it as
`claude/m6-b7-owner-api`. IMPLEMENTED: the eleven reads and three owner
requests of §5.9 and four routes a page cannot work without; exact-hash
approval, rejection and revocation of the research envelope and of a source
version, with the permission epoch raised in the transaction of a revocation;
rejection of a promotion, which is the only action a promotion takes and which
the agent worker applies as SYSTEM; owner starts of the three M6 templates
with their registered parameters; a job cancel, a shadow stop and an owner
refresh as recorded requests that another identity applies; owner read models
for sources, evidence, hypotheses, candidates, the trial ledger, results,
datasets, shadows and promotions, with marks on what rests on the holdout or a
shadow; `SystemStatus.research` and `.sources`; the regenerated OpenAPI
document and web types; and the harness phases `Generate` and `ApiAuth`.
Migration 0008 and every grant are unchanged. Run `m6-b7b` passed all sixteen
phases; two independent read-only reviews of that source found no path by
which holdout or shadow data reaches a tuning role and rated nothing high.
Their findings were fixed with tests: an owner cancel that was recorded as a
revocation, a shadow stop that could be followed by a mark, missing or wrong
holdout marks, two misleading status values, lax integers and query strings,
two unhandled errors, and `Generate` comparing an image with a tree that could
have changed after Build. A first acceptance attempt, run `m6-b7d`, failed in
one M5 test that runs twenty probes on a single ten-second orchestrator lease
it never renewed; the test helpers now keep the lease as the worker does, and
no product file changed for it. VERIFIED on fresh run `m6-b7e`, one final
image, without a skip: Build, `Generate` (no difference, on source equal to
the Build record), `Checks` (407 engine tests and the five web checks with 52
unit tests), `AgentOffline6` (14 and 84 M5 tests, 16 and 90 new and the schema
probe), `ApiAuth` (5, 5 and 21), `Staging` (13), `ShadowSchedule` (11),
`ResearchRunner` (15 and 17), `Regression` (169), `SourcePolicy` (249),
`EvidenceInjection` (24 and 2), `HoldoutIsolation` (9), `DispatcherAuth6`
(11 and 14) and `AgentFaults6` (11 and 17). `Migration` and `EngineParity`
NOT RUN:
the migration, the grants and the shared engine are unchanged. Every test used
a synthetic owner, fixtures, a scripted model on the recorded provider and the
loopback mock source: no model call, no public endpoint, no real source fetch.
Nothing was approved outside disposable fixture databases, nothing was
enabled, and no command addressed the normal app. The runs were cleaned by
exact name. GitHub CI still does not run. B7 completes neither M6-A nor any
deployment or activation: no browser path reaches these routes before the
pages and their same-origin functions exist (B8), and B8–B9 are NOT RUN.
Points left for the owner are in
[ExecPlan 0023 §19](plans/0023-m6-research-investigations.md#19-open-risks):
first among them that an owner's cancel of a screening now lets the workflow
that asked for it go on. See
[COMMANDS](COMMANDS.md#m6-b7-owner-api-openapi-and-generated-types-2026-10-05)
and
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b7--owner-api-openapi-and-generated-types).
Delivered as commit `cf89f86` in pull request
[MentorAliu/adaptive_spot_lab#28](https://github.com/MentorAliu/adaptive_spot_lab/pull/28),
open and not merged; the owner decides.

**Generation-1 trimming PR: merge requested (2026-10-05, 14:05 UTC).** OBSERVED
owner instruction in the same Claude Code session, after the pull request was
opened and reported: `merge it`
([decision](../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-generation-1-trimming-pr)).
VERIFIED read-only first: commit `8c0c7f0` is pull request
[MentorAliu/adaptive_spot_lab#27](https://github.com/MentorAliu/adaptive_spot_lab/pull/27),
opened at 13:29:08 UTC, open, mergeable and clean at that head with no check
run; `main` is still at `7f0268a`, the commit the change was verified on, so
nothing has to be merged into the branch and no phase has to be rerun. The PR
is merged with an ordinary merge commit pinned to its verified head, without
force, an admin bypass or branch deletion. This entry is written before the
merge and does not claim it; GitHub records the actual merge commit, and the
next checkpoint's documents record it here. The merge deploys and activates
nothing and completes no batch of ExecPlan 0023; B7–B9 are NOT RUN.

**Generation-1 prompt trimming corrected on its branch, not merged (2026-10-05, 13:25 UTC).**
OBSERVED owner decision in a separate Claude Code session: when a generation-1
(M5) prompt is over its size bound, hide the oldest tool result first, as
generation 2 does, instead of the newest
([decision](../DECISIONS.md#2026-10-05--generation-1-prompt-trimming-drops-the-oldest-result-first)).
VERIFIED read-only first: pull request #26 (B6) is MERGED as
`7f0268a1c128ff83087e4fbb8bfc7ba339982f2f` at 11:51:35 UTC and `main` is at
that commit, which records the merge the entry below left to GitHub.
IMPLEMENTED on `claude/g1-prompt-trim-order` from that commit: one expression
in `services/engine/app/agents/prompting.py` and one new pure test. VERIFIED on
fresh isolated run `g1-trim-b`, one image, without a skip: Build,
`AgentOffline6` (14 and 84 M5 tests, 16 and 72 new and the schema probe),
`DispatcherAuth6` (11 and 14), `AgentFaults6` (11 and 17), `Checks` (389) and
`EvidenceInjection` (24 and 2); the new test fails with the old expression
restored. NOT RUN: the phases whose tests compose no prompt (`Regression`,
`Migration`, `SourcePolicy`, `Staging`, `ShadowSchedule`, `ResearchRunner`,
`HoldoutIsolation`, `EngineParity`), any model call and GitHub CI. Every test
used synthetic fixtures and a scripted or recorded provider. No definition,
prompt file, schema, seed or profile hash changes, so no new profile approval
follows from it. Nothing was deployed: the normal app's agent worker keeps the
M5 code until the M6-A deployment, and no command addressed the normal app.
Whether a stored M5 step was ever trimmed is not known; that read was not
asked for. This is not a batch of ExecPlan 0023: it closes one of its open
risks, and B7–B9 remain NOT RUN. Delivery is a pull request from this branch
to `main`, opened after this entry and not merged; the owner decides. See
[COMMANDS](COMMANDS.md#generation-1-prompt-trimming-order-2026-10-05) and
[ExecPlan 0020 §17](plans/0020-m5-agent-runtime.md#correction-after-closure--which-results-an-oversized-prompt-hides-2026-10-05).

**B6 merge requested (2026-10-05, 11:49 UTC).** OBSERVED owner instruction in
the B6 Claude Code session, after pull request #26 was opened and reported:
`merge it` ([decision](../DECISIONS.md#2026-10-05--owner-asks-to-merge-the-m6-b6-pr)).
VERIFIED read-only first: `main` is still at `5da6b90`, the commit B6 was
accepted on, and PR #26 is open and mergeable at head `6be9ed1`. Nothing has to
be merged into the branch and no phase has to be rerun; the acceptance of run
`m6-b6c` below stands for the merged source. The PR is merged with an ordinary
merge commit pinned to its verified head, without force, an admin bypass or
branch deletion. This entry is written before the merge and does not claim it;
GitHub records the actual merge commit, and the next checkpoint's documents
record it here. The merge completes neither M6-A nor any deployment or
activation; B7-B9 are NOT RUN. The open points of the pull request stay open.

**M6 B6 implemented and accepted in isolation (2026-10-05, 11:38 UTC).**
OBSERVED owner instruction in a Claude Code session: implement B6 of ExecPlan
0023 on a new branch from `main`, verify it in isolated stacks, open a pull
request and do not merge it; four points the plan left open were decided by
the owner
([decision](../DECISIONS.md#2026-10-05--m6-b6-definition-generations-schedule-and-ended-shadows)).
VERIFIED read-only first: PR #25 (B4) is MERGED as
`5da6b90a3761abb6262dc040308cf7e9c4fb1d20` at 22:30:14 UTC on 2026-10-04 and
`main` is at that commit, so B6 was branched from it as
`claude/m6-b6-agent-workflows`. IMPLEMENTED: definitions v2 beside M5's
unchanged v1 (catalog v2 with seven more tools, role grants v2, AgentStep
schema v2, budgets v2), the tool handlers, the code-owned workflow graph with
waiting, one completion and one resume per queued call, the trigger scheduler,
code-owned priority, four M6 prompts and probes CP-15 to CP-20. Run `m6-b6b`
passed every phase; three independent read-only reviews of that source then
reported 26 distinct findings (3 high, 9 medium, 14 low). Twenty-four were
fixed with tests and two are recorded as risks. VERIFIED on fresh run
`m6-b6c`, one final image, without a skip: Build, `Migration` (19
schema tests and the populated migration), `Checks` (388),
`Regression` (169), `AgentOffline6` (14 and 84 M5 tests, 16 and 71 new and the schema
probe through the pinned CLI), `DispatcherAuth6` (11 and 14), `AgentFaults6`
(11 and 17), `EvidenceInjection` (24 and 2), `SourcePolicy`
(249), `Staging` (13), `ShadowSchedule` (10),
`ResearchRunner` (15 and 17) and `HoldoutIsolation` (9). The five
M5 agent test files run in these phases on schema 0008.
`EngineParity` NOT RUN: the shared engine and replay code is unchanged. Every
test used synthetic fixtures and a scripted or recorded provider: no model
call, no public endpoint, no real source fetch. No profile, envelope, source
version or promotion was approved outside disposable fixture databases, and
nothing was enabled. After deployment the profile approved in M5 is no longer
usable: the runtime waits for a new owner approval and a probe run. The runs
were cleaned by exact name. GitHub CI still does not run. B6 completes
neither M6-A nor any deployment or activation; B7–B9 are NOT RUN, and probes
CP-01 to CP-20 against a real model are an owner action in M6-B. See
[COMMANDS](COMMANDS.md#m6-b6-agent-workflows-and-tools-2026-10-05) and
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b6--definitions-v2-tools-workflows-waiting-prompts-and-probes).
Delivered as commit `a65aafe` in pull request
[MentorAliu/adaptive_spot_lab#26](https://github.com/MentorAliu/adaptive_spot_lab/pull/26),
open and not merged; the owner decides.

**B4 merge requested; `main` merged in and the merged source accepted (2026-10-04, 22:30 UTC).**
OBSERVED owner instruction at 21:30 UTC in the B4 session: `merge it`
([decision](../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b4-pr)).
VERIFIED read-only: PR #24 (B5) is MERGED as
`52eab973d0de9365c8a820040aafeb53624b1ffa` at 21:23:36 UTC and `main` is at that
commit; PR #25 conflicted with it. `main` was merged into the B4 branch with
both sessions' entries kept. VERIFIED on fresh run `m6-b4c`, one final image,
without a skip: Build, `Staging` (12 tests), `ShadowSchedule` (10),
`ResearchRunner` (15 and 17), `HoldoutIsolation` (9), `SourcePolicy` (249),
`EvidenceInjection` (24), `Checks` (317), `Migration` (19 schema tests and the
populated migration) and `Regression` (169). The first attempt FAILED one B3
test in `ResearchRunner`: it still expected the source identity to be refused a
read that B5 deliberately granted, and B5's acceptance had not rerun that
phase. The test was corrected to the merged contract; no product code changed.
`EngineParity` NOT RUN: the shared engine and replay code is unchanged by both
batches. The run was cleaned by exact name. PR #25 is then merged with an
ordinary merge commit pinned to the verified head, without force, an admin
bypass or branch deletion; this entry is written before the merge and does not
claim it. GitHub CI still does not run. The merge completes neither M6-A nor
any deployment or activation; B6–B9 are NOT RUN. See
[COMMANDS](COMMANDS.md#m6-b4-merge-of-main-and-acceptance-on-the-merged-source-2026-10-04).

**B5 merge requested (2026-10-04, 21:22 UTC).** OBSERVED owner instruction in
the same Claude Code session, after pull request #24 was opened: `merge it`
([decision](../DECISIONS.md#2026-10-04--owner-asks-to-merge-the-m6-b5-pr)). The PR
is merged with an ordinary merge commit pinned to its verified head, without
force, an admin bypass or branch deletion. This entry is written before the
merge and does not claim it; GitHub records the actual merge commit. `main` was
still at `6e8fbb6` and the B4 pull request (#25) was open, so B5 merges first
and B4 must then merge `main` and rerun every phase whose inputs changed (B5
changed migration 0008). GitHub CI still does not run, so the local B5
acceptance remains the only automated evidence. The merge completes neither
M6-A nor any deployment or activation.

**B4 PR opened, not merged (2026-10-04, 15:50 UTC).** VERIFIED: commit
`3e3c4776b8f23a8871dfdea32f383dc073b349b4` is on
`origin/claude/m6-b4-bridge-staging-shadows` (pushed without force, remote hash
checked), and [PR #25](https://github.com/MentorAliu/adaptive_spot_lab/pull/25)
against `main` is OPEN and MERGEABLE at that head. The merge was NOT RUN: the
owner's instruction asks for the PR and says not to merge until told. GitHub CI
did not run (both runs ended in `startup_failure`, the account-level cause in
[ExecPlan 0016 §8](plans/0016-ci-checks.md#8-progress-and-evidence)); the local
B4 acceptance below is the only automated evidence. PR #24 (B5) is open against
the same `main`; whichever merges second has to merge `main` and rerun the
phases it touches. Nothing was deployed or activated. See
[COMMANDS](COMMANDS.md#m6-b4-delivery-2026-10-04).

**M6 B4 complete on its branch, not merged (2026-10-04, 15:50 UTC).**
IMPLEMENTED on `claude/m6-b4-bridge-staging-shadows`: the research bridge,
staging into versioned append-only stores, sealed datasets, the hash-checked
relay of jobs and results, and shadows as deferred replays (ExecPlan 0023 B4;
R14, R20 and the bridge part of R16), with the owner's four decisions of the
day ([DECISIONS](../DECISIONS.md#2026-10-04--m6-b4-handed-over-and-four-points-the-plan-left-open-execplan-0023)).
VERIFIED on fresh isolated run `m6-b4b`, one final image, without a skip:
Build, `Staging` (12 tests and the bridge probe), `ShadowSchedule` (10 tests),
`ResearchRunner`, `Regression` (169 tests), `Checks` (145 tests) and
`HoldoutIsolation`. `Migration` and `EngineParity` were NOT RUN because
migration 0008 and the shared engine and replay code are unchanged. Both test
runs were cleaned by exact name. All evidence is synthetic fixture evidence;
it says nothing about real data volumes or any strategy's performance. GitHub
CI did not run. Nothing was deployed or activated, the research services were
not started in the normal app, and M6-A stays incomplete: B5 is separate work
in open PR #24, and B6–B9 are NOT RUN. Delivery is a PR from this branch to
`main`, opened after this entry and not merged; GitHub records its number. See
[ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#b4-final-source-acceptance)
and [COMMANDS](COMMANDS.md#m6-b4-final-source-acceptance-2026-10-04).

**B5 acceptance and cleanup VERIFIED within its batch scope (2026-10-04, ExecPlan 0023).**
IMPLEMENTED in a second session, beside B4, on `claude/m6-b5-source-registry`:
the source registry with hashed source versions, the `source-fetcher` service and
its `asl_source` identity, immutable fetch and evidence records with separate
publication, update, receipt and availability times, full-text search filtered
by cutoff and approval before ranking, polling, and `SOURCE_REVISION` trigger
records with dedupe and cooldown.
- **Result.** Run `m6-b5b`, image `5cfcf2c9…5b9ec51f`: Build (static checks and
  Ruff), 317 Checks, 169 Regression tests, Migration (19 schema tests and the
  populated upgrade, downgrade, restore and invariant checks), 249 SourcePolicy
  tests with the Compose-block review and the hardened-container probe, and 24
  EvidenceInjection tests. No test was skipped. Both runs' Docker resources
  were then removed by exact name (13 each) with the evidence kept, and the
  documentation link check found no broken link in 86 files.
- **Review.** The first run, `m6-b5a`, passed every phase. An independent
  read-only review then found eight defects in the new modules; each was
  fixed with a test, and the result above is the rerun of every phase on the
  fixed source.
- **Changed in migration 0008,** which the normal app does not have: the two
  seeded source versions gained the fields §5.7 names (their hashes changed;
  no approval of either exists), `asl_source` may execute the fixed epoch
  read, and a decision on a source version takes the publication lock. No
  table and no M1–M4 object changed; no dependency was added.
- **Still inert.** Both source versions are `PROPOSED`, `asl_source` is NOLOGIN
  and `ASL_SOURCES_ENABLED` is `0`. No real feed was fetched: tests use a
  loopback mock in isolated stacks, and that path stays NOT RUN until the
  owner's M6-B activation.
- **NOT RUN for B6:** the two tools, the completion for a waiting workflow, the
  dispatcher half of `EvidenceInjection` and the trigger scheduler. B4, B6–B9
  and full M6-A acceptance remain open; nothing was deployed or activated.

- **Delivery.** Commit `3a44777` is pull request
  [MentorAliu/adaptive_spot_lab#24](https://github.com/MentorAliu/adaptive_spot_lab/pull/24),
  opened at 14:26 UTC against `main` (still `6e8fbb6`) and **not merged**: the
  owner decides that. GitHub CI did not run.

[Evidence](plans/0023-m6-research-investigations.md#b5--source-registry-fetcher-evidence-search-and-triggers)
and [commands](COMMANDS.md#m6-b5-source-registry-fetcher-evidence-and-search-2026-10-04).

**B3 checkpoint merged (2026-10-04, 11:55 UTC).** VERIFIED on 2026-10-04 at
12:05 UTC, read-only: [PR #23](https://github.com/MentorAliu/adaptive_spot_lab/pull/23)
is MERGED as merge commit `6e8fbb60fa2b7fc18576a3d67b273c9d8d5968b6` (parents
`bdeac4f`, the B1/B2 merge, and `56d8031`, the PR head), merged at 11:55:03 UTC.
Local and remote `main` are both at that commit. B0–B3 are on `main`; B4 starts
from it on `claude/m6-b4-bridge-staging-shadows`. The merge completes neither
M6-A nor any deployment or activation. See
[COMMANDS](COMMANDS.md#m6-b3-checkpoint-pr-and-merge-2026-10-04).

**B3 checkpoint merge requested (2026-10-04, 11:53 UTC).** OBSERVED owner
instruction in the same Claude Code session, after PR #23 was opened: `merge it`.
The PR is merged with an ordinary merge commit pinned to its verified head,
without force, an admin bypass or branch deletion. This entry is written before
the merge and does not claim it; GitHub records the actual merge commit. GitHub
CI still does not run, so the local B3 acceptance remains the only automated
evidence. The merge completes neither M6-A nor any deployment or activation. See
[COMMANDS](COMMANDS.md#m6-b3-checkpoint-pr-and-merge-2026-10-04).

**B3 checkpoint PR opened, not merged (2026-10-04, 11:47 UTC).** The Codex
session reached its usage limit before the commit step described below. In a
Claude Code session the owner then asked `create a pr on this branch`. That
session committed the authorization record (`4cd4979`), pushed the branch without
force and opened [PR #23](https://github.com/MentorAliu/adaptive_spot_lab/pull/23)
against `main`: VERIFIED OPEN and MERGEABLE at that head. The merge was NOT RUN,
because that instruction asks for the PR only. GitHub CI did not run (both runs
ended in `startup_failure`, the account-level cause in
[ExecPlan 0016 §8](plans/0016-ci-checks.md#8-progress-and-evidence)). The helper
receipts named below were not produced;
[COMMANDS](COMMANDS.md#m6-b3-checkpoint-pr-and-merge-2026-10-04) records the
actual commands. M6-A stays incomplete and nothing was deployed or activated.

**B3 checkpoint publication authorized (2026-10-04 Europe/Budapest).** After
local commit `85104b7`, the owner requested a PR and merge to `main`. The branch
and worktree were verified clean; remote main remains the B1/B2 merge `bdeac4f`,
and no B3 PR exists at the preflight. Publication is in progress, with native
receipts retained under `.cache/m6/m6-b3b/publication/`. GitHub records the actual
PR/check/merge outcome. This does not complete M6-A or authorize deployment or
activation. See the [owner decision](../DECISIONS.md#2026-10-04--owner-requests-a-b3-checkpoint-pr-and-merge).

**B3 acceptance, review and cleanup VERIFIED complete (2026-10-04, ExecPlan 0023).** IMPLEMENTED
the isolated research runner, durable catalog jobs/reservations, leases/fencing,
immutable trials/results, bounded replay, reuse and holdout/cutoff projections
on `codex/m6-b3-research-runner`, from verified clean B1/B2 merge
`bdeac4f91c13e25ca190320a6def53dcd43c0817`. Final image `2585ef23…2c8bf28`
passed Build/static/Ruff, 15 catalog tests, 17 runner tests, 9 holdout tests,
runtime isolation, all 145 Checks, all 169 M3/M4 Regression tests and all three
EngineParity scenarios, without skips. A fresh migration image with identical
non-doc source, filesystem layers and runtime config except Compose labels
passed 19 schema tests and populated migration/restore/invariant checks.
All three B3 fixture runs passed exact-name cleanup: 27 resources removed,
seven recorded build image IDs absent, evidence and failed attempts retained.
The documentation check passed 86 Markdown files with zero broken links and
four historical warnings. Local delivery uses an explicit 26-file allowlist;
its commit and clean-tree result are recorded in `.cache/m6/m6-b3b/Delivery.json`
and the native Git journal. No normal-app command, activation, B4/B5 work or
publication ran; B3 alone does not complete
M6-A. [Evidence](plans/0023-m6-research-investigations.md#18-completion-evidence)
and [commands](COMMANDS.md#m6-b3-corrected-source-acceptance-2026-10-04).

**Specification pack:** 2.0.0, agent-driven architecture revision, prepared 2026-09-26.

**M6-A B0 and B1 complete (2026-10-03 UTC, ExecPlan 0023).** VERIFIED B0 contracts, offline schema preview and measured envelope sizing. IMPLEMENTED B1 migration 0008, sixteen catalog tables, roles, views, seeds and database guards. Final isolated run `m6-b1c` passed the B1 image build, four static/registry checks, Ruff, all nineteen schema tests and the full populated Migration phase. Exact in-place schema/data comparisons, bounded locks, old-image fixture-worker continuity, dump/restore, downgrade refusal and restored accounting/M3/M4 invariants passed. The restored SQL representation mismatch was diagnosed and corrected in the harness with owner authorization; the failed attempts remain recorded. All five completed fixture runs passed exact-name Clean, removing 35 resources and retaining their evidence. B2 progress is recorded below; B3–B9 and full M6-A acceptance are NOT RUN. No normal-app operation or activation ran in B1. B10 needs separate chat approval; B11 is owner-only. See [evidence](plans/0023-m6-research-investigations.md#18-completion-evidence) and [commands](COMMANDS.md#m6-b1-restore-diagnosis-and-final-rerun-2026-10-03). Historical milestone records below retain their original completion statements.

**VERIFIED publication (2026-10-04 Europe/Budapest):** B1 source commit `7f327ae` is on `origin/codex/m6-research-investigations`; its remote hash matches. The owner requested this branch push. M6-A acceptance and its delivery PR remain pending B2–B9.

**B2 acceptance and cleanup VERIFIED complete (2026-10-04).** IMPLEMENTED
the bounded candidate grammar, Decimal operators/interpreter and shared-engine
strategy interface. Final image `7cd93cff…6e64aea` passed Build/static/Ruff,
focused canonical storage/idempotency/conflict and readiness checks, all 145
B2 Checks and all 169 M3/M4 Regression tests without skips. EngineParity passed
gapped-stop, quiet and pilot-lifecycle financial/per-bar comparisons, both pilot
fast/per-step comparisons and the pre-interface native baseline. Earlier
failures and owner-approved corrections remain recorded. Clean removed seven
final-run resources at 09:15 UTC; all three replaced image IDs are absent.
The baseline's five resources were already cleaned; evidence remains. The
completion-documentation Docker check passed 86 Markdown files with no broken
links and four historical warnings. Local Git delivery uses the existing codex
branch and retains its native receipt. B3 is next and NOT RUN; full M6-A remains
incomplete pending B3–B9 and its separately gated deployment/activation.
No normal operation, deployment, B3 or activation ran.
[Evidence](plans/0023-m6-research-investigations.md#18-completion-evidence).

**Checkpoint publication authorized (2026-10-04 Europe/Budapest):** the owner
requested a PR and merge to `main` for this branch's completed B1/B2 work.
Publishing this checkpoint does not close full M6-A acceptance or authorize
normal deployment/activation. GitHub history and the native receipt under
`.cache/m6/m6-b2a/publication/` record the actual publication result. See the
[owner decision](../DECISIONS.md#2026-10-04--owner-requests-a-b1b2-checkpoint-pr-and-merge).

**Application implementation supplied by the original pack:** none. M0 was added on 2026-09-26. M1 owner access, virtual funding and accounting were added on 2026-09-27. No provider login, market-data fixture, simulated fill, or strategy performance is claimed.

M0 is implemented and locally verified through its applicable foundation checks. M1 is implemented and locally verified on disposable databases; see the [M1 run record](plans/0002-funding-ledger.md), [verified commands](COMMANDS.md), and [integration evidence](../INTEGRATION_EVIDENCE.md). **M2 is complete within its approved scope.** Worker faults, provenance, browser races, full-density storage, pinned exhaustion, repeated recovery, migration/restore, bounded public recovery and the full 60-minute/five-minute workloads passed. The owner reported all Windows Narrator checks passed in Chrome on 2026-09-28, closing Q02 against unchanged source/image identities. Browser version and voice were not supplied. See the [final gate assessment](plans/0003-market-data-charts.md#final-q01q10-reassessment) and [bound review record](m2-narrator-review.md). Normal owner public collection was subsequently activated at the owner's request; see [ExecPlan 0006](plans/0006-public-market-activation.md). **M3 is implemented, accepted in isolation and deployed inert (2026-09-29)**; see below and [ExecPlan 0011](plans/0011-paper-broker-reference.md#15-completion-evidence). **M4-A is implemented, accepted in isolation and deployed inert (2026-09-29)**; its activation (M4-B) awaits the owner's exact-hash approvals and an explicit instruction. See below and [ExecPlan 0015](plans/0015-evaluation-fixed-pilot.md#16-completion-evidence). **M5 is complete (2026-10-03)**: M5-A was implemented, accepted in isolation and deployed inert on 2026-10-02, and the M5-B capability probes passed the same day. On 2026-10-03 the owner closed M5 on those probes; the live token refresh is a follow-up check due on or after 2026-10-10. The runtime stays in `PROBE_ONLY`. See the M5 row below and [ExecPlan 0020](plans/0020-m5-agent-runtime.md#17-completion-evidence). M7 was closed by the owner on 2026-10-19 without the decision probes and the first live decision, and M6 is read as closed with it (top entry, [DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)); M8 and later remain unimplemented. Follow [MIGRATION.md](pack-2.0.0/MIGRATION.md) before merging another repository's state.

**M3 paper broker and reference strategy — accepted and deployed inert 2026-09-29:** a deterministic, fenced paper broker (IOC fills from sampled level-1 quotes, commission in the received asset, point-in-time filters), a per-asset ledger with holdings and reservations, bid-marked valuation, the `PAPER_PILOT_V1` risk gate with persistent latches, immutable position mandates with engine-triggered stop/time/trend exits, `TREND_REFERENCE_V1`, an execution worker, an isolated replay and read-only Orders, Positions and Risk pages. Final-source isolated run `m3-0929e` passed every phase (167 engine and 32 web unit tests, migration with a concurrent writer, populated dump/restore, worker kill/pause/DB-interrupt/30-kill faults, deterministic replay and isolation, strategy and 24 h catch-up budgets, and three browser states). The normal app at `http://127.0.0.1:3000/` now runs schema `0005_m3_paper_broker` with reconciliation OK, zero orders/fills/positions, the execution worker built but not started, its database identity NOLOGIN and main-account activation blocked; public collection continues. The release carries the committed ExecPlan 0012 changes so that deployed fix is not reverted. The code is on `main` (merged from branch `claude/m3-paper-broker`). [ExecPlan 0013](plans/0013-m3-gate-closure.md) closed the remaining gates on 2026-09-29:
- The owner retired the manual screen-reader review.
- A secret-value scan of logs, artifacts and client assets found no values after one trace-artifact fix.
- The long-running budgets passed, except the seven-day replay. The passing budgets were: 60-minute engine p95 291 ms, 10,000-record API reads, and browser SSR/LCP/CLS/interactions. ExecPlan 0017 brought the seven-day replay within budget on 2026-09-30 (below).

**M4 evaluation and fixed-strategy pilot — accepted and deployed 2026-09-29; pilot activated 2026-09-30 and RUNNING; checkpoint 2026-11-25.** M4 adds:
- exact-hash owner approvals, manifests with a code identity, and experiments;
- durable owner controls that the fenced execution step applies exactly once;
- hourly evaluation capture, a separate read-only evaluation worker, and reproducible SNAPSHOT, DAILY and FINAL reports against matched-flow baselines;
- identity, activation and deactivation tools, and the Approvals, Experiments and report pages.

Final-source run `m4f-0929c` (`be61a32`) passed every phase:
- 240 engine and 38 web unit tests;
- migration of populated 0005 data under a concurrent writer;
- a real-time pilot with faults, a 5-minute downtime and a completed evaluation;
- deterministic replay and isolation;
- every budget: engine p95 311 ms, control race p95 34.6 ms, 90-day report 19.9 s, API p95 23 ms, browser LCP ≤ 124 ms;
- a clean secret scan.

At the inert deployment on 2026-09-29, the normal app at `http://127.0.0.1:3000/` ran schema `0006_m4_fixed_pilot`, with reconciliation OK and public collection continuing. It had zero approvals, experiments and reports; both pilot identities were NOLOGIN, and neither pilot worker was started. GitHub CI could not run. Two report-reading findings were recorded for follow-up:
- The stale pause alert on finished runs is fixed; see below.
- A FINAL run return stops at the last full hour. This is a protocol property for the owner to weigh.

**M4-B pilot activation — verified 2026-09-30.** The fixed-strategy forward pilot is RUNNING on the main paper account.
- **Approvals and Start.** The owner approved nine definition hashes and the experiment manifest in the authenticated UI, pressed Start, and ran `tools/pilot-activate.ps1`.
- **Activation.** Experiment `d779fbf4-e1be-444c-ab55-7b61292eaa87` (FORWARD_PAPER, hypothetical cost scenario H1) was ACTIVATED at 09:09:52 UTC. It started at NAV 100 on 10,000 virtual USDT.
- **Checks.** Every post-activation check passed:
  - the start watermark, with no historical evaluations;
  - the STARTUP valuation and the daily reference;
  - no reconciliation failure or incident;
  - the first hourly SNAPSHOT report at 10:05 UTC.
- **Workers.** The execution and evaluation workers run with their identities enabled.
- **Completion.** Per OD-13, M4 is complete once the checkpoint report of **2026-11-25** is recorded (M4-C). M5 may start now.
- **While the pilot runs:**
  - Protection needs the PC and Docker running (OD-11). After a reboot, Docker Desktop did not start by itself on this host.
  - Deployments happen only outside HH:00–HH:03 UTC, with a graceful stop whenever the workers themselves are redeployed (OD-12). A changed engine code identity starts a new evaluation segment.
  - Weekly market-table dumps are due under OD-14.

See [ExecPlan 0015 §16](plans/0015-evaluation-fixed-pilot.md#m4-b-owner-approvals-and-activation-verified-2026-09-30).

**Market publication cost at stored density (ExecPlan 0021) — cause reproduced, fix verified in isolation and deployed to the normal app's market worker 2026-10-02; merged as `d075a78`.** While the pilot runs, the owner observed the normal app's `QUEUE_OVERLOAD` and `COLLECTION_GAP` incidents rising from about 1 an hour on 2026-09-29 to 31–53 an hour on 2026-10-02. Each one costs tens of seconds of quote usability.
- **Cause.** Every publication found unpublished rows with an anti-join over all stored observations and publications. On the unchanged worker (isolated run `lag-1002b`, synthetic history), one publication cost 61 ms at 250,000 stored rows, 424 ms at one million and 786 ms at 1.8 million.
  - From 500,000 rows a frame waits more than one second around a 45-second refresh, and the worker closes the collection.
  - At one million rows the gap detail matches the normal app's (`maintenance_refresh`, `QUEUE_OVERLOAD`, empty queue, lag about 1,250 ms), and quotes were usable in 24 of 578 seconds.
  - At 1.4 and 1.8 million rows quotes never became usable in ten minutes. The normal app held about 749,000 observations at the swap on 2026-10-02 and keeps growing until the seven-day retention starts deleting on 2026-10-05.
- **A second cause that is not active yet.** A retention call that deletes takes 300–400 ms, and up to 32 of them ran back to back on the writer's database thread. With the publication fix alone, a retention under the stream still closed the collection in isolation. On the normal app retention first deletes about 05:19 UTC on 2026-10-05, then every hour.
- **What the threshold measures.** The overload flag is the age of the oldest unpublished frame. At most 5 frames were pending and event-loop lag stayed under 2 ms at p99. It is receipt-to-publication delay, not backlog and not scheduler lag.
- **Fix.** The worker publishes the revisions it has just persisted by identity. The scan for every unpublished revision runs once per generation start, under its own deadline. Retention runs on its own database thread. There is no schema change.
- **Isolated evidence (run `lag-1002c`, commit `b40ac9a`).** With 250,000 to 1.8 million stored rows the same workload published every frame with receipt-to-publication p95 115–117 ms and p99 117–119 ms, with no gap or overload and every once-per-second sample usable. That includes the window at 1.8 million rows in which a retention deleted 16,000 observations under the stream. 43 worker-fault tests and 261 regression tests passed, as did the check, recovery-memory and burst phases. The whole verification was repeated on the branch merged with `main` after M5-A (run `lag-1002d`, commit `b3f8216`): the same density result, 43 worker-fault tests and 381 regression tests.
- **Deployed to the market worker only, 2026-10-02 15:17 UTC, with the owner's approval.** After a protected backup, one image was built from pull-request head `4003e75` and only `market-worker` was recreated. Its application source equals the tested image's. Every other container, the pilot's lease epoch 4 and its evaluation segment are unchanged. The normal database held about 749,000 observations at the swap.
  - **Before** (the preceding hour): 35 `QUEUE_OVERLOAD` and 37 `COLLECTION_GAP` incidents, publication lag 1,152 ms, both feeds unavailable.
  - **After** (two-hour soak, 15:18–17:18 UTC): no `QUEUE_OVERLOAD`; 21,220 stream observations published with receipt-to-publication p95 135 ms and p99 144 ms; restart count 0; quotes usable in 6,985 of 7,200 once-per-second samples (97.0%). Both 16:00 evaluation marks were `VALID`, the first valid hourly marks of the day.
- **What still interrupts quote usability (not changed by this plan).** The 215 unusable seconds of the soak had three older causes:
  - Two clock-check tear-downs of a healthy collection, when `/time` answered in just over a second (58 s and 35 s).
  - One run of REST weight-budget waits that aged the reference checks (115 s, no incident). Both 17:00:00 evaluation marks fell inside it and are `UNAVAILABLE`.
  - Four short stream delivery stalls (7 s in total).
  - For the first two, [ExecPlan 0022](plans/0022-reference-checks-and-rest-budget.md) has been deployed since 2026-10-03 (below).
- **Merged.** Pull request MentorAliu/adaptive_spot_lab#13 was merged as `d075a78` on 2026-10-02 at 18:32 UTC, on the owner's instruction. `main` now carries the source the market worker runs, so a rebuild of `market-worker` from `main` keeps the fix.
- **Open.** Rollback is the image tag `adaptive-spot-lab-market-worker:pre-0021`. The first retention that deletes is expected about 05:19 UTC on 2026-10-05 and has only isolated evidence so far. The overload policy remains the owner's decision. The stopped test volumes and images of the 0021 and 0022 runs were removed on the owner's instruction on 2026-10-03 ([DECISIONS](../DECISIONS.md#2026-10-03--test-volumes-and-images-of-the-0021-and-0022-runs-removed)).

See [ExecPlan 0021](plans/0021-publication-cost-at-density.md).

**Reference checks and REST budget (ExecPlan 0022) — verified in isolation and deployed to the normal app's market worker 2026-10-03; the two-hour soak passed.** The change covers the two older causes of unusable quotes that the 0021 soak showed. The owner approved it with clock option (a): an unmeasurable clock keeps failing closed at once.
- **Clock.** A routine clock check that cannot measure precisely, or whose request fails, keeps the stream collection. Quotes stay unusable until the clock is verified again, as before, with a recheck every five seconds. A clock that is measured out of bounds still closes the collection.
- **Measurement.** The check times only the request and its answer. It used to time the set-up of a connection too, which alone costs about a second on this host, the rule's whole allowance.
- **REST budget.** The worker's own ceiling of 120 weight a minute counts its own requests only. The IP-wide header is compared with half the provider's declared allowance, which the stored answers give as 6,000 a minute. A provider back-off holds every request.
- **Also fixed, found while checking the design:** a conflict-confirmation answer could end the collection or the process; a failed history request could re-open a feed that a failed instrument check had closed; a due rotation could end the collection while the clock stayed unverified.
- **Unchanged:** the usability rule, the clock rule, the schema, the API, the web app and everything the pilot's execution worker runs.
- **Isolated evidence (run `ref-1002b`, commit `0eb208a`, synthetic).**
  - The defects reproduce on the unchanged code and the same tests pass on the change.
  - 69 worker-fault tests and 421 regression tests passed, as did the check, recovery-memory and burst phases.
  - With 1.0 and 1.8 million stored rows, four injected clock faults at each level closed usability within a second and reopened it in 11.7–12.7 s on the same collection, with no gap. Receipt-to-publication stayed at p95 116 ms and p99 118 ms.
- **Deployed to the market worker only, 2026-10-03 05:22 UTC, with the owner's approval.** After a protected backup, one image was built from the tested source and only `market-worker` was recreated. Its application source equals the tested image's. Every other container, the pilot's lease epoch 4 and its evaluation segment are unchanged. New quotes stopped for 14–15 s during the swap.
  - **Against the provider.** The first `exchangeInfo` answer declared 6,000 weight a minute, so the IP guard is 3,000. Every completed clock sample was timed from the trace events: 246 ms at the median, while opening a connection took 0.7–2.7 s and is no longer counted.
  - **Two-hour soak (05:26–07:27 UTC): passed.** Quotes were usable in 7,169 of 7,200 once-per-second samples (99.6%, against 97.0% after 0021). One collection from start to end; no `COLLECTION_GAP` and no `QUEUE_OVERLOAD`; 19,595 stream observations published with receipt-to-publication p95 122 ms and p99 125 ms. All four hourly evaluation marks at 06:00 and 07:00 were `VALID`.
  - **The one routine clock failure,** at 06:00:03 (three provider answers of about 1.09 s), closed quotes for 15 s and kept the collection. The same event cost 58 s and 35 s in the 0021 soak, and the previous worker had six such tear-downs in the twelve hours before the swap.
  - **The other 16 unusable samples** were SOL only. The provider published no SOL ticker for more than five seconds, nine times; nothing was delayed, and the quote-age rule failed closed. This is not part of the change.
  - **Not exercised by the soak:** the REST budget against another client on the IP (none was active), a provider back-off, and a clock measured out of bounds.
- **Rollback** is the image tag `adaptive-spot-lab-market-worker:pre-0022`.
- **Two independent read-only reviews** checked the plan and then the code; their findings are in the plan's §18.

See [ExecPlan 0022](plans/0022-reference-checks-and-rest-budget.md). Pull request MentorAliu/adaptive_spot_lab#15 was merged as `ed9fae3` on 2026-10-03 at 07:32 UTC, on the owner's instruction to merge once the soak had passed ([DECISIONS](../DECISIONS.md#2026-10-03--market-worker-deployment-approved-execplan-0022)). `main` now carries the source the market worker runs, so a rebuild of `market-worker` from `main` keeps both this change and ExecPlan 0021's.

**Ended-run cause note — verified and deployed web-only 2026-09-30:** a `STOPPED`, `COMPLETED` or `FAILED` experiment now shows still-open causes as a neutral record ("Causes still recorded as open"). It no longer shows a red pause alert that offers a resume. Live runs claim a resume only while one is offered.
- Isolated run `m4w-0930a` from `0db0a2a` passed Checks (41 web unit tests), the real-time pilot phases and BrowserPilot.
- A protected backup preceded the rollout. Only web was recreated; its compiled payload matches the tested image.
- API, database, market worker, schema and the inert M4 state are unchanged.

See [ExecPlan 0018](plans/0018-ended-run-cause-note.md).

**Replay step throughput (ExecPlan 0017) — verified and deployed 2026-09-30.** The seven-day full-density replay now meets its 20-minute budget. On the M4 code, two runs of isolated gate `rt-0929f` took 429.5 s and 429.0 s, with identical fingerprints and step traces; the same week per step was estimated at 5–6 h.
- **Replay and fixture runs.** They share fenced batch transactions and reuse state reads. The results equal a per-step run's, including M4's owner-control scenario, and a verification mode checks every reused value against the database.
- **Forward engine.** It gets read-cost cuts only and keeps one fenced transaction per step. The 60-minute workload measured p95 291 ms and p99 309 ms.
- **Normal app.** After a protected backup, the API and market worker were recreated from PR #6's head `2f7973a`; their app source equals the tested image. Schema `0006_m4_fixed_pilot`, reconciliation OK, both feeds connected; the web and the inert M4 state are unchanged.
- **Collection gap.** Collection was down from 04:08 to 08:24 UTC while the host was off. After a reboot, Docker Desktop had not been running; it was started for the deployment.

See [ExecPlan 0017](plans/0017-replay-throughput.md).

[ExecPlan 0014](plans/0014-bounded-latest-quote.md) bounded the replay's `latest_quote` scan and was deployed to the normal app on 2026-09-29 (api and market-worker recreated from `5a1f858`, no schema change, protected backup first): the read no longer grows with future rows, results are unchanged (169 tests, identical `gapped-stop` fingerprint), and the first 435k replay publications now take about a minute instead of 40. The seven-day replay budget (20 min) is still FAILED. With positions open the engine steps once per simulated second at about 46 ms per step, so a full run needs hours; meeting the budget needs a replay design change or a revised budget (follow-up).

**Normal deployment — verified 2026-09-28:** under the owner's new milestone delivery rule, the normal app at the then-current `http://127.0.0.1:4317/` ran the accepted M2 release with schema `0004_m2_completion`. The upgrade from M0 followed a protected backup and matching isolated restore. Web/API/PostgreSQL were healthy; actual runtime files matched the accepted source/artifacts, reconciliation passed, and collection was disabled at deployment. The browser sign-in page was verified. See [ExecPlan 0004](plans/0004-milestone-local-delivery.md) for that deployment's identities, preserved state, evidence and limits.

**UI follow-up — verified locally 2026-09-28:** the normal web service was updated to explain the empty chart while collection was disabled, keep both market filters in validated URL search params, highlight Markets independently of those values, and render account values and UTC dates readably. No collector, API, schema or owner financial state was changed by that rollout. A protected backup, isolated browser checks, normal health/browser verification and runtime identity are in [ExecPlan 0005](plans/0005-market-account-ui-followup.md).

**Page badge clarification — verified locally 2026-09-28:** Account and Markets headers identify their paper purpose without M1/M2 milestone numbers, which described when those pages were introduced rather than the current application release. Collection was still disabled at that UI follow-up. Evidence is appended to [ExecPlan 0005](plans/0005-market-account-ui-followup.md#owner-clarification--page-milestone-labels-2026-09-28).

**Public market collection — activated on the normal app 2026-09-28:** after explicit owner instruction, protected backup and current public-provider preflight, the optional BTC/SOL worker was enabled. Both feeds became connected with usable quotes; the Markets browser rendered a candlestick chart and System reported market data ready. Paper trading remains disabled and the model runtime unconfigured. This is a point-in-time operating state, not a trading-readiness claim. See [ExecPlan 0006](plans/0006-public-market-activation.md).

**Markets refresh control — verified locally 2026-09-28:** the owner can select Live, 10, 30 or 60 seconds, or Off for browser snapshot polling. The validated choice persists in the Markets URL; it does not change the running public collector. Isolated Chromium verified URL persistence, mobile keyboard selection and timer-off behavior. The normal web-only update passed health and signed-in browser checks with the live chart still present; API, database and worker identities were unchanged. See [ExecPlan 0007](plans/0007-market-refresh-control.md).

**Candle table display — verified locally 2026-09-28:** UTC hour/availability cells omit the zone already named in their headers, and OHLCV cells group digits and remove redundant trailing zeroes without changing source decimal strings. Containerized checks, protected backup and the normal signed-in browser verification passed; the live chart and collector remained present. See [ExecPlan 0008](plans/0008-market-candle-table-display.md).

**RHF forms — verified locally 2026-09-28:** owner setup, sign-in and top-up review now use RHF submission pending state and root server errors, with readable validation/auth messages. Funding confirmation and unknown-outcome handling retain separate authority; a draft does not post funds. Docker checks, 21 unit tests, an isolated Chromium funding flow, protected backup and normal web-only deployment passed. The signed-in normal Account page displayed the top-up form after rollout. See [ExecPlan 0009](plans/0009-rhf-form-states.md).

**Current-release readiness remediation — normal rollout verified 2026-09-28:** commit `1949975` repairs credential submission before hydration, durable funding recovery, Decimal precision, instrument reference selection, cached failure/freshness, API deadlines, diagnostics and runtime bounds; documentation closure is at `2801898`. Final-source isolated Docker checks included 26 frontend unit tests, 69 real-PostgreSQL regression tests, 20 worker-fault tests, mandatory browser flows, migration/restore, full-density and pinned-exhaustion storage, 60-minute normal/five-minute burst performance, and a bounded public-provider smoke. The owner then authorized the normal update: a protected backup restored in a network-isolated helper; the clean checkout fast-forwarded to `2801898`; frozen Docker builds, the no-op migration owner, service recreation, reconciliation, public-feed recovery and unauthenticated Chromium smoke passed. The normal app ran those images at the then-current `http://127.0.0.1:4317/` with existing public collection still enabled. Obsolete stopped test containers/networks were removed without deleting volumes. [ExecPlan 0010](plans/0010-release-readiness.md#owner-authorized-normal-rollout-and-cleanup--2026-09-28) records exact identities and limitations. The owner-performed manual accessibility review was retired unrun by [owner decision on 2026-09-29](../DECISIONS.md#2026-09-29--manual-screen-reader-review-retired). Complete artifact notices, whole-network performance and full release sign-off remain open; this is not M3 or a trading-readiness claim.

**Current normal web address — verified 2026-09-28:** at the owner's request, the loopback host port changed from 4317 to 3000 without changing the production web image, database, API or public worker. The normal app is healthy at `http://127.0.0.1:3000/`; the old port has no listener. Protected backup, unchanged schema and unauthenticated HTTP/Chromium checks are recorded in [ExecPlan 0010](plans/0010-release-readiness.md#owner-requested-normal-port-alignment--2026-09-28). Isolated test projects still select their own nonconflicting ports.

**Market stream continuity (ExecPlan 0012) — deployed and soak-verified on the normal app 2026-09-28/29:** read-only analysis showed that every hourly Binance `MARKET_LOT_SIZE.maxQty` recomputation made the worker rotate its stream. All 13 production rotations on 2026-09-28 then failed with a `TimeoutError` gap; the outer close timeout raced websockets' own, and backfill sometimes starved the writer. Quotes were lost for about 1–1.5 minutes per hour.

The fix (commit `ac38d15`):
- adopts instrument changes on the live socket through publication-atomic pointer moves
- makes rotation make-before-break, with bounded, never-cancelled closes
- keeps routine checks from downgrading feeds, and failed checks fail closed
- samples queue telemetry every 250 ms, which removes a pre-existing sub-second usability flap
- schedules reference refreshes from their start every 45 s

Isolated evidence:
- Docker checks, 85 engine regression tests and 36 worker-fault/continuity tests passed.
- The recovery-memory, performance and real-network-interruption runs passed.
- An isolated worker on the real public provider completed 16 make-before-break rotations with no gap.

Normal deployment:
- A protected backup was taken with a matching checksum; the migration was a no-op.
- `api` and `market-worker` were recreated at 22:30 UTC with collection still enabled; web and PostgreSQL were untouched.
- Running images and source hashes were verified, reconciliation stayed unlatched, and the sign-in page rendered.
- The following two-hour soak recorded 7,200/7,200 usable once-per-second samples. It included the 23:00 and 00:00 UTC in-place adoptions, with 0 incidents and one connection generation throughout.

Residual limits (shared-IP REST budget saturation, provider ticker pauses above 5 s, clock-uncertainty teardown) are listed in [ExecPlan 0012](plans/0012-market-stream-continuity.md#completion-evidence). This resolves the hourly outage that [ExecPlan 0011](plans/0011-paper-broker-reference.md) lists as a pre-M4-activation blocker; it is not an M3 or trading-readiness claim.

The M3 rollout on 2026-09-29 rebuilt `api` and `market-worker` from the M3 release, which carries these committed 0012 changes; the running market-worker code stayed byte-identical to `ac38d15`. See [ExecPlan 0011](plans/0011-paper-broker-reference.md#normal-deployment--2026-09-29).

The 2026-09-27 post-M0 tooling follow-up added the official TanStack Query ESLint plugin to the web flat config. Containerized lint, typecheck, frontend unit tests and build passed; see the linked command and integration records. This did not advance a later application milestone.

A further 2026-09-27 Query integration cleanup forwards the query function's cancellation signal to the Start server-function request. Its applicable web and normal browser checks passed; see the same records. The subsequent QueryClient change removes the temporary app-wide freshness and retry overrides, leaving TanStack Query's built-in defaults. Containerized web checks and normal/outage browser cases passed for this change. Neither change implements later portfolio or agent capabilities.

## Record actual progress here during implementation

| Milestone | Initial pack status | Evidence needed |
|---|---|---|
| M0 Foundation | **Implemented and locally verified 2026-09-26** | Container builds and startup, migration, private health/status, typed Start BFF and SSR, shadcn preset discovery, 4 frontend unit tests, 5 backend integration tests, 2 normal Chromium tests and 1 outage Chromium test. See linked evidence above. |
| M1 Funding/ledger | **Implemented and locally verified 2026-09-27** | Owner bootstrap/sessions, exact virtual funding, ledger/reservations, reconciliation and account UI. Synthetic PostgreSQL/browser, outage, restart and backup/restore evidence is in [ExecPlan 0002](plans/0002-funding-ledger.md). No owner application data was funded for testing. |
| M2 Public data/charts | **Complete and scoped acceptance verified 2026-09-28** | Forward-only `0004_m2_completion`, bounded queue, capture provenance, conflict confirmations and loading/health behavior are implemented. All ten scoped gates passed, including owner-reported Narrator N01–N09. Measurements and evidence limits are in the [completion record](plans/0003-market-data-charts.md#7-completion-run-record--2026-09-27). The [normal deployment](plans/0004-milestone-local-delivery.md) was verified with collection disabled; the separate [owner-requested activation](plans/0006-public-market-activation.md) subsequently enabled public observations. |
| M3 Paper broker/reference | **Implemented; isolated acceptance verified and normal deployment verified (inert) 2026-09-29** | Broker, ledger, risk gate, mandates, protection, reference strategy, execution worker, replay and read-only pages; final-source run `m3-0929e` and the inert rollout are in the [completion record](plans/0011-paper-broker-reference.md#15-completion-evidence). Gates closed by [ExecPlan 0013](plans/0013-m3-gate-closure.md): screen-reader review retired by the owner, secret scan clean, and performance budgets met except the seven-day replay (its quote scan was bounded in ExecPlan 0014; the budget still fails on per-step cost with positions open). Merged to `main` from branch `claude/m3-paper-broker`. Activation remains an M4 owner decision. |
| M4 Fixed evaluation | **M4-A implemented; isolated acceptance verified and normal deployment verified (inert) 2026-09-29. M4-B activation not authorized.** | Approvals, experiments, controls, evaluation capture, reports and pilot tooling; final-source run `m4f-0929c` and the inert rollout are in the [completion record](plans/0015-evaluation-fixed-pilot.md#16-completion-evidence). Still needed: the owner's exact-hash approvals of the 8 definitions and the manifest in the UI, an explicit activation instruction, then Start (M4-B), and the checkpoint report (M4-C). Delivered by PR MentorAliu/adaptive_spot_lab#7. |
| M5 Model/tool runtime | **Complete 2026-10-03, closed by the owner on the capability probes ([DECISIONS](../DECISIONS.md#2026-10-03--m5-closed-on-the-capability-probes-live-token-refresh-becomes-a-follow-up-execplan-0020)).** M5-A implemented; isolated acceptance verified 2026-10-01 and normal deployment verified (inert) 2026-10-02. M5-B 2026-10-02: capability probes PASSED, runtime left in `PROBE_ONLY`. Follow-up: the live token refresh, on or after 2026-10-10 11:20 UTC; first attempt on 2026-10-11 NOT RUN, the runtime waits for a new profile ([record](plans/0020-m5-agent-runtime.md#follow-up-after-closure--the-live-refresh-check-first-attempt-2026-10-11)). | A recorded provider and a Codex provider behind one abstraction, the isolated runner and egress gateway, the bounded tool loop with read and assessment tools only, the owner API, the agent pages and additive migration 0007. Final run `m5-b7j` on `9436127` passed every phase on one snapshot; results, budgets and what was not run are in the [completion evidence](plans/0020-m5-agent-runtime.md#17-completion-evidence). The normal app at `http://127.0.0.1:3000/` runs schema `0007_m5_agent_runtime` with the agent runtime DISABLED, `asl_agent` NOLOGIN and no agent service; the M4 pilot's containers, lease epoch and evaluation segment are unchanged by the deployment ([B8 record](plans/0020-m5-agent-runtime.md#b8-completion-evidence--inert-normal-deployment-2026-10-02)). M5-B on 2026-10-02: the owner activated the runtime, logged in, approved profile `1df9c916…` (`gpt-6.1-sol`, effort `medium`) and ran the probes: 14 of 14 passed in 20 live calls with zero violations, although in ten probes the model declined rather than attempted the denied action, and the live market feed was unavailable or stale during the run ([M5-B record](plans/0020-m5-agent-runtime.md#m5-b--activation-login-profile-and-capability-probes-2026-10-02)). The pilot was unaffected. Follow-up: the live refresh check on or after 2026-10-10 11:20 UTC ([M5 closure](plans/0020-m5-agent-runtime.md#m5-closure-2026-10-03)). Enable stays the owner's choice. Delivered by PR MentorAliu/adaptive_spot_lab#12. |
| M6 Agent research | **Read as closed 2026-10-19 with M7 ([DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)); its live walk-through is a follow-up.** B0–B8 acceptance/cleanup VERIFIED within their batch scopes; B0–B6 merged (B6 as `7f0268a`, the generation-1 trimming fix as `d1f8d88`); B7 (PR #28) merged as `2043fc0` on 2026-10-06; B8 (PR #29) accepted on run `m6-b8d` and merged as `4ece326` on 2026-10-06; B9 IMPLEMENTED on its local branch and NOT accepted: authoring runs only, four reviews fixed without a run since, no acceptance run, test runs stopped for an owner decision (2026-10-07); B10 NOT RUN | Roles, sources, registered experiments/shadows, isolation. [ExecPlan 0023 §18](plans/0023-m6-research-investigations.md#18-completion-evidence); all seven recommended decisions accepted. B10 held for chat approval; B11 owner-only |
| M7 Agent trading | **Closed 2026-10-19 by the owner's decision ([DECISIONS](../DECISIONS.md#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision)):** M7-A deployed on `09f4490`, the boundary `COMPLETE`, `AGENT_POLICY_V1` approved, run `a8b3ae07` `RUNNING`, the runtime `ENABLED`; the decision probes and the first live decision cycle are follow-ups ([ExecPlan 0026 §18](plans/0026-m7-agent-driven-main-decisions.md#the-boundary-m7-b-and-m7s-close-2026-10-19)) | Approved discretionary policy, intent flow and adaptation tests |
| M8 Reliability/evidence | Not implemented by pack | Recovery/resource tests and complete forward evidence report |

## Activation settings still to resolve

Verify actual symbols/data availability, fees or explicitly approved fee scenarios, execution assumptions, runtime capabilities, source registry, measured hardware limits and workload budgets. Approve the proposed risk/reference settings before their first active run. Define and approve all agent-specific evidence, stop/hold, trigger, review, action/turnover and adaptation settings before main agent activation. Missing future settings do not block M0.

Use [CONFIGURATION.md](../CONFIGURATION.md) for gate ownership and [ACCEPTANCE_CHECKLIST.md](../ACCEPTANCE_CHECKLIST.md) for testable outcomes. [PACK_VALIDATION.md](pack-2.0.0/PACK_VALIDATION.md) records documentation checks only; it is never an implementation pass.
