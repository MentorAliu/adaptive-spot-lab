# Decisions and authority

Revised 2026-09-26 for pack 2.0.0. This replaces the 1.0.0 selector-only architecture and earlier Next.js/API-only proposals. It does not authorize real trading or assert that implementation is complete.

## 2026-11-23 — Open source as a one-commit public copy

OBSERVED: in the project thread "Open source Adaptive Spot Lab and add to portfolio", the owner wrote at 12:59:52 UTC "what if I wanted also this repo: https://github.com/MentorAliu/adaptive_spot_lab to make it public and add to my portfolio, identical how we did with job agent ?".
- **Read as:** the same path as the owner's other open-sourced project: this repository stays private with its history, pull requests and the author email its commits carry, and a new public repository gets the committed tree as one fresh commit, made by `tools/export-public.mjs`.
- **Prepared:** the MIT licence ([LICENSE](../LICENSE)), a security policy ([SECURITY.md](../SECURITY.md)), a README for people who run their own copy (with the one-time login of `asl_execution` a fresh database needs), the export script, and the PC's Windows user folder replaced by `C:\Users\owner` in the documents. A scan of the tree and of all 839 commits found no secret: the key prefixes the documents name are prefixes only.
- **Nothing in the app changes.** The public repository's name and its creation are the owner's to confirm.

## 2026-11-13 — Keep the spot rule; eight faster or wider strategies checked

OBSERVED: in the project thread "Find a more profitable, more active strategy", the owner asked at 08:17:44 UTC for the most profitable strategy, trading as often as a profitable one allows.
- **Checked.** Eight variants of `SPOT_RULE_V1` (signals read every 4 hours or every hour, shorter lookbacks, a tighter buffer, stepping aside for or following the US CPI, jobs and Fed releases, Solana beside Bitcoin) were tested offline against it on Binance spot history, pre-registered before any number: none `BETTER`, the two release variants `WORSE`, the faster ones losing their gains to fees ([ideas/strategies-checked-2026-11-13.md](ideas/strategies-checked-2026-11-13.md); `CALCULATED`, `BACKTEST_MODELED_NOT_FILLED`).
- **Decided.** At 08:58:47 UTC the owner picked "Keep today's rule" (the thread's recommendation) on the card "Which strategy should your account trade?", over "Add 1- and 2-week signals". `SPOT_RULE_V1`, `SPOT_POLICY_V1` and `SPOT_COST_V1` stay as installed; M1 to M3 of [ExecPlan 0060 §4.10](plans/0060-spot-trading-only.md#410-the-measure-pre-registered) keep running. Nothing in the app changes.

## 2026-11-12 — Clean up after the spot switch (ExecPlan 0061)

OBSERVED: in the project thread "Clean up the app after the spot switch", the owner wrote at 22:45:11 UTC "now do a full app cleanup since we moved to spot trading, make sure to cleanup,refactor anything that is a leftover and improve, enhance the app".
- **Decided.** At 22:57:09 UTC the owner picked "Approve" (the thread's recommendation) on the card "Approve the cleanup plan for the spot app?", over "Approve, cleanup only" and "Approve, delete old records": [ExecPlan 0061](plans/0061-clean-up-after-the-spot-switch.md), `APPROVED`. The leftovers of the futures, the agents and the research go from the code, the tools and the current documents (their history moves to the archive); updates wait only around the daily close and the rule's reading; the Cockpit shows the run's return beside Bitcoin's over the same span. The futures app's records stay read-only in the database's `archive` schema. No rule, policy, cost, limit or money path changes.

## 2026-11-12 — Spot trading only (ExecPlan 0060, M12)

OBSERVED: in the project thread "Switch the app to spot trading only", the owner wrote at 09:59:43 UTC "let's completely switch to spot trading and remove the futures completely, also the new spot trading should have a profitable strategy to trade buy/sell, also make sure to cleanup everything and the tests and backtests, app should start backtests with new spot trading". It reverses the owner's "Keep futures" of 2026-11-05 (a read-only thread, not entered here) and ends M11 ([ExecPlan 0039](archive/plans/0039-bitcoin-futures-on-paper.md)).
- **Decided.** At 10:19:26 UTC the owner picked "Approve" (the thread's recommendation) on the card "Approve the plan to switch the app to spot trading?", over "Approve, keep the AI": [ExecPlan 0060](plans/0060-spot-trading-only.md), `APPROVED`. The main account will hold USDT and BTC and buy and sell Bitcoin spot on paper by `SPOT_RULE_V1` (the slow rule's signal, long or cash, at 0059's 5% a year volatility target, trading the difference once a day); the app backtests the same rule on Bitcoin's spot daily history by itself and refreshes it each day; the futures account, the perpetual's feed and everything that served them go, with the AI agents (every job they had was a futures job), the pre-futures spot engine, the research, the coin scan and the news sources, their tests and backtests; their records are archived in the database, not deleted. Rule 1 returns to spot only, long or cash, no leverage or shorting. The build follows in its own pull request with an independent money-path review, then one update.
- **Chosen by the thread** as the trader ([plan §13](plans/0060-spot-trading-only.md#13-decision-log)): the 5% target by 0059's limit rule; difference trades and selling everything when the target is zero; the latches unchanged and no per-trade stop; the account keeps its money (no fresh 10,000).
- **As built** ([plan §13](plans/0060-spot-trading-only.md#13-decision-log), the thread's trading judgment): the backtest models the latches as the live engine acts, against §4.6's text: the drawdown stop sells where the fall reached 8% (the day's open when it opened below), and the daily loss limit is counted without changing a trade, since the live trade comes right after the day's reference. The independent money-path review found no defect that posts a wrong amount; its fixes (one dust test for every sale, a top-up valued at the next step, the step's own clock, the retired NAV checks' latch kept) are built. No limit, size or rule value moved.
- **After the install** ([plan §13 item 16](plans/0060-spot-trading-only.md#13-decision-log), the thread's trading judgment): Binance's daily candle of 2018-02-08, a day the exchange closed early when trading halted, is stored as Binance records it, its close the last trade before the halt, rather than counted as a missing day; it changes no definition, limit or measure.

## 2026-11-12 — Read now what was waiting on a date

OBSERVED: in the project thread "Bring the app up to date now", the owner wrote at 09:23:43 UTC "let's keep the app up to date with all the changes, don't wait for anything on the future".
- **Read as:** install whatever `main` holds that the PC lacks, and do now, read-only, every reading that was only waiting for a date. The PC ran `93a2112`; `main`'s two newer commits (`6998e95`) are documents only, so no update was needed.
- **Done on these words** (read-only, nothing in the app changes): generation 11's paired reading against the last-hour rule, due 2026-11-16, and generation 14's M1, due 2026-11-26, read over their whole runs, both ended ([TRADING](TRADING.md#the-record-so-far), [0053 §14](archive/plans/0053-the-trader-every-four-hours-and-on-events.md#14-progress)); the replay's progress ([0050 §14](archive/plans/0050-replay-past-decisions-offline.md#14-progress)); the stopped ChatGPT backtest's records exported for its report ([ExecPlan 0052](archive/plans/0052-backtest-the-ai-trader-on-history.md)).
- **Cannot be read early, by their samples:** the replay's verdicts (95% of each arm, about 2026-11-14); the twins' league table (30 days); the veto twin's placebo (60 candidates; 3 by 2026-11-09); the slow trend twin's and the slow rule's own measures (90 days). The weekly review keeps its Mondays.
- **Nothing for the owner to decide:** the trader changes that were to follow the 2026-11-16 reading (a cost gate, dropping the scores block) stay superseded while [ExecPlan 0059](archive/plans/0059-the-slow-rule-trades-the-main-account.md) is in force, as its §4.4 says.

## 2026-11-10 — The slow rule trades the main account (ExecPlan 0059)

OBSERVED: in the project thread "Find another profitable strategy to add" (renamed "Plan the slow rule for the main account"), the owner asked at 11:42:15 UTC "what's a good profitable strategy that the app doesn't have yet, spot or futures". The thread, as the project's trader ([TRADING](TRADING.md)), wrote three candidates and their pass mark down before any result and checked them on Binance's public 2022 to 2026 archive: the slow rule over ten coins, the strongest coins against the weakest, and the perpetual's funding as carry. None passed ([the ideas note](ideas/strategies-checked-2026-11-10.md)); the thread recommended adding nothing. On its card "Add another strategy to the app now, or leave it as it is?" the owner picked at 14:35:46 UTC "Plan the slow rule for the main account", whose text read "I write a plan for the slow rule, in spot and never short, to trade the main account instead of the AI trader. That ends the trader's running test."
- **Decided.** At 15:05:57 UTC the owner picked "Approve the plan" (the thread's recommendation) on the card "Approve the plan for the slow rule to trade the main account?", over "Keep the AI trader" and "Approve, but in spot": [ExecPlan 0059](archive/plans/0059-the-slow-rule-trades-the-main-account.md), `APPROVED`. The main account will follow `MAIN_RULE_V1` (the slow trend twin's signal, never short, at most 1x, sized to a 5% a year volatility target so that its worst fall on 2021 to 2026 history stayed at half the 8% drawdown stop) instead of the AI trader, on the perpetual; the trader, its reviewers and the coach will stop being asked, their code kept. The build follows in its own pull request with an independent money-path review; its one update waits until ExecPlan 0052's ChatGPT backtest has ended and generation 19's update is installed and checked.
- **Chosen by the thread** as the trader (each in [plan §13](archive/plans/0059-the-slow-rule-trades-the-main-account.md#13-decision-log)): the perpetual rather than spot (about 0.5% a year less at this size, against a new money path), the size by the limit, the latches unchanged.
- **Install now (the owner's words).** At 15:08:06 UTC the owner wrote in the project chat "can everything stop, if necessary start fresh with $10k and update the app to latest changes ?" and at 15:08:23 UTC "I don't want to wait until everything completes november 15 or whatever the time is". The thread took them as the owner's say over the plan's install conditions (§9): the build ships with generation 19's (ExecPlan 0058) in one update as soon as it is reviewed, without waiting for ExecPlan 0052's ChatGPT backtest, which ends at the install with the code `TRADER_REPLACED` and is read as it stands; "fresh" is the new run the switch starts, with its own high-water NAV (no ledger is reset; a top-up to show 10,000 again waits for the owner's ask); and the switch happens at the first finished bar with the account flat, not only at 00:15 UTC ([plan §13](archive/plans/0059-the-slow-rule-trades-the-main-account.md#13-decision-log)).
- **Installed.** At 17:24 UTC the owner wrote in the thread "I wanted to click merge it now but clicked Not yet accidentally" (PR #190 merged), and at 17:30 UTC "done" after the double-click: the update finished `COMPLETE` on `93a2112` and the rule's run started at 17:30:01 UTC (OBSERVED, [plan §14](archive/plans/0059-the-slow-rule-trades-the-main-account.md#14-progress)).

## 2026-11-09 — The event calendar (ExecPlan 0058)

OBSERVED: the research thread "Research an event calendar for the trader" measured on 2026-11-04, on Binance's 2022 to 2026 archive, that Bitcoin's range in the hour after the US consumer price index, the US jobs report and the Fed's decisions is 1.9 to 3.4 times a normal hour's, and that a position entered before them is stopped out more often (Fed days 70% against 39%), and proposed a calendar in code; the project's memory held it for the bundle after the 2026-11-16 reading. In the project thread "Add the event calendar to the trader" the owner wrote at 15:22:51 UTC "yes do everything now".
- **Decided.** [ExecPlan 0058](archive/plans/0058-the-event-calendar.md): the trader, generation 19 (`FUTURES_DECISION_V7`, migration `0039`), is generation 14's with a calendar in code (the CPI and the jobs report from the stored BLS calendar, the Fed's statements from a table read on the Fed's page), no new entry from 240 minutes before such a release to 45 minutes after the CPI, 30 after the jobs report and 120 after a Fed statement (refused at the finish, checked again at the finish, and closed when the calendar cannot be read), and one more decision once each window ends (`RELEASE_OUT`). Exits, tighter stops and holds stay open, and a position keeps its stop, take profit and time exit. Home and Settings show the windows.
- **Chosen by the thread** under the owner's words and "decide for me", each in [plan §13](archive/plans/0058-the-event-calendar.md#13-decision-log): three events only; no forced exit before a release; fail closed for entries; the Fed in a table, not the feed; one more decision, not a new agent; live at the install, which ends generation 14's run, so 0053's measure is read descriptively and generation 19's is pre-registered in the plan (the ninth variant on the trial ledger).
- **Unchanged:** paper only; `FUTURES_POLICY_V1` and every limit; the engine's protection; the coach, the reviewers, the veto, the twins, the replay and the backtests (0056's design guard now names the calendar's parts; its run had finished); the 2026-11-16 reading of generation 11; the agents' provider and model.

## 2026-11-07 — A slow trend twin (ExecPlan 0057)

OBSERVED: in the project thread "Find a profitable strategy the app lacks" (renamed "Add a slow trend twin"), the owner asked at 19:15:42 UTC "What is a good profitable strategy that the app is missing?". The thread answered, as the project's trader ([TRADING](TRADING.md)), with slow trend-following sized by volatility ([TR-01, TR-03](REFERENCES.md#trading-research--2026-11-01-and-2026-11-02)), its rule written down at 19:19 UTC before a free offline check on 2022 to 2026 history, and a card: a twin beside the trader, the main account, or not now. The owner wrote "review this" at 20:57:37 UTC and "decide whats best and go ahead" at 21:00:45 UTC; the thread chose the card's recommended "Add it as a twin".
- **Decided.** [ExecPlan 0057](archive/plans/0057-a-slow-trend-twin.md): a sixth isolated paper twin, `TREND_SLOW`, `SYSTEM`'s by `TWIN_SET_V3` (migration `0038`). Once a UTC day it holds long or short a fraction of its wallet: the sign of Bitcoin's daily close against its closes 30, 91 and 365 days earlier, sized to a 40% a year volatility target, at most 2x, changed only when the target moves by more than a quarter of the wallet; no stop, no latch, no model. The feed stores Binance's public 1-day candles for it. Its measure against holding Bitcoin, the `HOLD` twin paired by day, is written in the plan before its first bar, with `UNCLEAR` expected for at least a year.
- **Chosen by the thread** under "decide whats best and go ahead", each in [plan §13](archive/plans/0057-a-slow-trend-twin.md#13-decision-log): one twin, long or short; a resize as a whole exit and entry (offline it ended 965 USDT lower than trading the difference over 4.8 years: 736 more in fees, about 1.5% of the start a year); the pre-registered buffer kept although a wider one scored better afterwards; `TWIN_SET` kept at V2 for the running backtests; the placebo reading the veto twin's requests under V3 too; after the independent review, a resize tried whole at the day's next bar when its exit cannot fill, a day stored a minute after its close, and the daily job's notes left out of the agents' view. The update ships after [ExecPlan 0056](archive/plans/0056-backtest-the-traders-latest-design.md)'s own is installed and checked.
- **Unchanged:** paper only; the trader, generation 14, its schedule, prompt, context and limits; `FUTURES_POLICY_V1`; the other five twins in their segments; the veto, the scorer, the backtests and their design guard; the owner's account and ledger. Nothing changes from the twin's verdict: a `BEATS_HOLD` is evidence for a later plan the owner would approve.

## 2026-11-07 — Backtest the trader's latest design on Claude, on a Claude API key (ExecPlan 0056)

OBSERVED: in the project chat on 2026-11-07, after Claude's hourly backtest was read, the owner asked at 15:32:56 UTC "But why next hour? Should the longs and shorts be based on events ?" and at 15:34:25 UTC "Yes, also make sure the backtesting should include the latest changes not to be surprised again with "you're right its using old" because that causes api drainage and waste of api tokens". The coordinator relayed both to the thread "Backtest the trader's latest design", which listed what the earlier backtests did not copy and what no backtest can, and asked on a card (15:40:35 UTC) "Which model should backtest the trader's latest design?"; at 15:42:46 UTC the owner picked "Claude, about $25 (cap $40)" over the recommended "ChatGPT, stop the old hourly run".
- **Decided.** [ExecPlan 0056](archive/plans/0056-backtest-the-traders-latest-design.md): a new run (`BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE`) on ExecPlan 0052's window, archive and mask, in which a simulated account is traded by generation 14's design as it runs live: the live prompt, schedule (every four hours and on events), context (with its own scores, the coach's note and each trade's review) and finish rules, and the trade reviewer, the decision reviewer and the coach on its own trades, all built from the live code; answered by `claude-sonnet-5-5` at `medium` on the Claude API; generation 18, migration `0037`. A design guard: nothing starts while the installed live design differs from the one the run copies. A hard cap of $40 calculated from the tokens; CALCULATED, rough: about $25 and 8 to 12 hours. Measures pre-registered before any code or call: M1 to M3 as 0052's, M4 its calls graded 4 hours out against the last-4-hours rule, and M6 the latest design against Claude's hourly run, in a family of fourteen tests with 0052's and 0055's (a pass at 279/280).
- **Unchanged:** paper only; the live trader, its provider (Codex), model, prompt and schedule; the reviewers, the coach, the veto, the twins, the policy, the limits and the money paths; 0052's and 0055's runs and measures; the 2026-11-16 reading. The ChatGPT backtest goes on (the owner's pick) and waits while this run goes first, so it ends about half a day later. No paid call outside this run and no fallback to another provider.

## 2026-11-05 — Backtest Claude on the same two months, on a Claude API key (ExecPlan 0055)

OBSERVED: in the thread "Backtest the twins and the AI trader", after the coordinator relayed the owner's "what if we use claude api key ?" (11:59:51 UTC), the owner offered at 12:03:34 UTC a Claude API key whose credit was about to expire. The thread asked on a card (12:03:58 UTC) "Use the Claude credit for a Claude backtest of the same two months?"; at 12:04:27 UTC the owner picked the recommended "Yes, Claude backtest (~$60)". At 12:18:18 UTC the owner asked "can the claude backtesting be done at once"; the thread answered that it runs nonstop and finishes within about a day of the install.
- **Decided.** [ExecPlan 0055](archive/plans/0055-backtest-claude-on-the-same-history.md): a second run of ExecPlan 0052's backtest (`BACKTEST_AI_V1:TWO_MONTHS_CLAUDE`), the same window, archive, mask, accounts, prompts, tools and budgets, answered by `claude-sonnet-5-5` at `medium` on the Claude API with the key the owner saved on 2026-11-03; generation 17, migration `0036`. Nonstop in the agents' free time (no count a bar or a day), ahead of the ChatGPT backtest and the replay, after every live agent. A hard cap of $120 calculated from the tokens, under the key's remaining credit; CALCULATED, rough: about $60 to $90 and about 15 to 25 hours. Measures pre-registered before any call: 0052's four on the Claude run and M5, Claude's 1-hour calls against ChatGPT's on the same hours, passing at 99.44% (the two runs' family of nine).
- **Unchanged:** paper only; the live trader, its provider (Codex), model, prompt and schedule; the veto, the twins, the policy, the limits and the money paths; the ChatGPT run's answers and measures; the 2026-11-16 reading. A Claude refusal or credit limit never holds the live agents. No paid call outside this run and no fallback to another provider. The ChatGPT run waits while Claude goes first, so it ends about a day later.

## 2026-11-04 — The AI backtest may use up to 80% of the weekly Codex allowance (ExecPlan 0052 section 15)

OBSERVED: the backtest started by itself at 06:45:21 UTC, after the weekly Codex window reset. In the project chat at 09:18:37 UTC the owner asked "now with the tuning of the models, what will be the usage if we do backtesting now ?". The thread "Backtest the twins and the AI trader" answered that under the half-used rule it would take about 4 weeks, and asked on a card (09:23 UTC) "Let the backtest use up to 80% of each week's Codex allowance?". At 09:35:17 UTC the owner picked the recommended "Yes, up to 80% a week".
- **Decided.** [ExecPlan 0052 §15](archive/plans/0052-backtest-the-ai-trader-on-history.md#15-generation-16-the-backtest-up-to-80-of-the-week-2026-11-04): generation 16's four backtest templates continue the same run with one changed rule: a backtest call starts while the weekly Codex window is under 80% used, every other window under half and none reached. CALCULATED, rough: about 2.5 weeks instead of about 4, with 20% of each week left for the live agents and the owner's own use. Migration `0035`.
- **Unchanged:** paper only, Codex only, no paid call; the run, its window, mask, measures and the answers already given; the replay's half-used rule; the live trader, the veto, the twins, the policy, the limits and the money paths. If the owner's own Codex use takes the rest of a week, the limit can be reached before the reset: the live agents' calls are then refused until it resets (code's stops still protect a position), and the backtest waits too.

## 2026-11-03 — Small fixes now: the scorer's expected bars and a second usage-limit signal (ExecPlan 0054)

OBSERVED: in the project thread "Analyze the agents' setup for performance", after the thread's review, the owner picked the recommended "Small fixes now" on its decision card at 19:42:32 UTC.
- **Decided.** [ExecPlan 0054](archive/plans/0054-the-scorer-expects-the-schedule-and-a-second-usage-signal.md): the scorer expects a decision only at the schedule's four-hour moments (`DECISION_SCORING_V2`), and a Codex reading that says the limit is reached sets the usage-limit block; one update, installed with a double-click.
- **Unchanged:** the trader, its prompt, context, model and generation 14, so its paired test keeps running; the coach's and the decision reviewer's prompts; the next trader generation waits for the replay's verdict and the 16 November read.

## 2026-11-03 — The trader every four hours and on events (ExecPlan 0053)

OBSERVED: at 11:14:52 UTC, in the project chat, the owner asked "is there a better practice to handle the decisions instead of checking every 15 minutes ?"; the coordinator proposed a slower clock with event triggers. At 11:17:08 UTC, in the project thread "Switch the trader to event-driven decisions", the owner wrote "yes, using the trading.md file, implement using best practices for our app", and at 11:17:50 UTC "and make it live now instead of november 16 if it better". The thread's card asked "Switch to the new clock as soon as it's built, or after 16 November?"; at 11:51:15 UTC the owner picked the recommended "Live as soon as it's built".
- **Decided.** [ExecPlan 0053](archive/plans/0053-the-trader-every-four-hours-and-on-events.md): generation 14's trader (`FUTURES_DECISION_V6`, migration `0033`) decides every four hours (00, 04, 08, 12, 16 and 20 UTC) and at once on an event (its entry cooldown ending after a closed trade, a move of 4 times the 15-minute ATR since its last decision, the first hourly close beyond the last 24 hours' range, a funding rate change of 0.01 percentage points), at most 32 a UTC day: about 8 to 9 decisions a day instead of about 100. Live at the install, which comes after ExecPlan 0052's update is installed and checked; generation 11's run ends there, and the reading due 2026-11-16 reads its days up to the install.
- **Chosen by the thread** under the owner's words and "decide for me" (2026-10-19), each in [plan §13](archive/plans/0053-the-trader-every-four-hours-and-on-events.md#13-decision-log): `FUTURES_POLICY_V1` unchanged, every decision still at a finished 15-minute bar it allows; the events' values chosen on how often they fire on 2022 to 2026 history, before any reading; the 1-hour call kept; the measure pre-registered in [§4.5](archive/plans/0053-the-trader-every-four-hours-and-on-events.md#45-the-measure-pre-registered) (the paired score against the last-hour rule, read at 120 decisive calls, a pass deflated by the eight variants tried).
- **Unchanged:** paper only; the policy and its limits, code's protection every second, the run, the twins, the coach, the reviewers, the veto and the replay.
## 2026-11-03 — Backtest the AI trader on two months of history, on spare Codex (ExecPlan 0052)

OBSERVED: in the project thread "Backtest the rule twins on history", after 0051's results, the owner wrote at 09:15:02 UTC "I want also to have the models included as well, this is the main reason after all, I want to see how the models perform, but limit it to 1 year", and at 09:28:16 UTC "what about 2 months ?". The thread asked on a card (09:29 UTC): two months on the OpenAI API (recommended, about 55 USD), two months on spare Codex allowance (free, about two weeks), or one year on the API (about 300 USD). At 09:50:45 UTC the owner picked "2 months on spare Codex, free".
- **Decided.** Research on the owner's word: [ExecPlan 0052](archive/plans/0052-backtest-the-ai-trader-on-history.md) lets the live trader's model, at its effort, decide hourly for a simulated futures account on Binance's archive from 2026-09-01 to 2026-11-01, from 10,000 USDT, with the dates shifted and the prices rescaled so the model cannot tell which days it sees, and the veto agent answer a simulated veto twin; code sizes, fills and protects as live. The measures are pre-registered in the plan before any call.
- **Who pays:** Codex with the owner's ChatGPT login, as the live agents: no API key, no paid call. Backtest calls run only in the trader's idle minutes and while every allowance window is below half used (0050's rule), after the live trader and the reviewers; when the allowance runs low the backtest waits and the live agents go on. CALCULATED: about 1,800 calls, roughly two weeks of spare allowance.
- **Unchanged:** paper only; the live trader, its prompt, context and generation, the veto, the twins, the policy, the limits, the money paths and the paired reading due 2026-11-16. A backtest answer moves only the simulated account; a result changes nothing in the app, and a pass is evidence for a later plan on the owner's word. The year (2025-11 to 2026-09) runs only on a later word, as a second trial.

## 2026-11-03 — Backtest the rule twins on Binance history (ExecPlan 0051)

OBSERVED: at 08:19:21 UTC, in the project chat, the owner asked "Can the implementation be tested based on timeframe from previous time frames, for example if i select the timeframe 2023 january to  february or march based on the binance candles, without seeing the results, want to let the system simulate for example with 10k usdt how would it perform? Whats that called and is it a good idea?". The coordinator answered that it is a backtest, recommended it for the rule twins and not for the AI trader, and asked "Should I start that?"; at 08:20:40 UTC the owner wrote, in the project thread "Backtest the rule twins on history": "Yes, the dates i mentioned were used as an example, you decide what would be best for this case, also I want to see all the results".
- **Decided.** Research on the owner's word ([TRADING](TRADING.md#how-to-judge-a-trading-change): a backtest is research, off since [ExecPlan 0035](archive/plans/0035-a-simpler-app-that-trades-by-itself.md) until the owner asks): [ExecPlan 0051](archive/plans/0051-backtest-the-rule-twins-on-history.md) replays `TWIN_SET_V2`'s rule twins (hold, trend, gated trend, weekly momentum; the veto twin's rule part is the trend rule) on Binance's public archive of the BTCUSDT perpetual from 2020, from 10,000 USDT, with `FUTURES_POLICY_V1`'s and `FUTURES_COST_V1`'s values unchanged, offline, and shows every result.
- **Chosen by the thread** under that word: a development window before 2022 and one untouched test window from 2022-01-01 to 2026-11-01, run once; calendar years and quarters as fresh starts; the measures and pass rules written in the plan before any run; the AI trader and the veto agent's answers left out (their model may recall these years); the archive downloaded on the owner's PC through a device session, since the cloud refuses Binance's hosts.
- **Unchanged:** paper only; nothing in the running app, the trader, generation 11 or 12, the twins, the policy, the limits or the paired reading due 2026-11-16. A result changes no rule; a rule that passes is evidence for a later plan on the owner's word.

## 2026-11-03 — Replay past decisions offline (ExecPlan 0050)

OBSERVED: at 07:52:14 UTC, in the project thread "Improve the trader's accuracy", the owner asked "Use docs/TRADING.md file, research the app implementation of what can be added/removed to enhance and improve the accuracy of the current implementation". The thread's document put a decision card with three options; at 08:07 UTC the owner picked the recommended "Replay first": "A build thread adds an offline replay: the 411 stored contexts through two prompt variants and the free rule, about 800 model calls on your PC; the live trader and the 11-16 check stay untouched."
- **Decided.** [ExecPlan 0050](archive/plans/0050-replay-past-decisions-offline.md): generation 11's stored contexts of 2026-10-28 to 2026-11-01 are answered again, in the agents' free time, by a replay agent (generation 13) under two prompt variants (without the feedback blocks; asked for a 4-hour call) and a control, each answer a `REPLAY` row scored against the free rule by the measure the plan pre-registers. This is the owner's word for this research, which [ExecPlan 0035](archive/plans/0035-a-simpler-app-that-trades-by-itself.md#42-research-off-in-the-agent-worker) left off; it starts no other research.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each in [plan §13](archive/plans/0050-replay-past-decisions-offline.md#13-decision-log): in the app on the agents' slot, a control of 100 contexts, the 4-hour variant built on the no-feedback one, and the pacing of §4.3 (only on Codex with the trader's model, yielding to the trader and the veto, paused while the Codex allowance is half used).
- **Unchanged:** paper only; the trader, its prompt, context, model and generation 11, `FUTURES_POLICY_V1` and its limits, code's protection, the twins and the paired check due 2026-11-16. Nothing in the app changes from the replay's verdict; a variant that passes is evidence for the next trader generation's own plan.

## 2026-11-02 — Settings drops the "Evaluation reports" tile

OBSERVED: at 16:11:38 UTC, in the project thread "Find why evaluation reports are idle", the owner asked "why is evaluation reports idle ?". The answer: the evaluation worker (`app.evaluation.worker`) writes its hourly and daily reports only for a spot forward run (`experiments`, mode `FORWARD_PAPER`), and the futures app that started on a clean database on 2026-10-25 has none, so it has nothing to report and the API's `evaluation` reads `idle` (no report within 2 hours) for good. The futures app's own reports (trade reviews, decision scores, result checks) run elsewhere and were never this tile's. At 16:13:47 UTC the owner picked "Remove it" on the thread's card.
- **Decided.** Settings' health no longer shows the "Evaluation reports" tile, as it stopped showing Research's ([ExecPlan 0035](archive/plans/0035-a-simpler-app-that-trades-by-itself.md)); [FRONTEND](archive/contracts/FRONTEND.md#settings-drops-the-evaluation-reports-tile--2026-11-02).
- **Unchanged:** the API still sends `evaluation`, and the evaluation worker still runs and finds nothing to do; the engine, the trader, the policy, the money paths and the protection; no migration or dependency.
- **Installed** (PR #162, `51f9929`), OBSERVED read-only on the PC at about 16:52 UTC: the record `update-20261102T162905Z` `COMPLETE` (16:28:57 to 16:34:08 UTC, from `ab93f7d`, no migration, schema `0030_veto_twins`; api, web, the market, execution, evaluation and agent workers, agent-egress, agent-runner and source-fetcher replaced; reconciliation `OK`, the five pages answering 200, the agents' switch on with `CHECK_PASSED`, no problem). The web container (created 16:30:20 UTC) runs this update's image; `/settings` answered 200 without "Evaluation reports" and with the other health tiles, and no file in the web's built `.output` holds that text. NOT RUN: the page looked at in a browser.

## 2026-11-02 — Claude is the project's systematic trader (the trading knowledge)

OBSERVED: at 09:39:15 UTC, in the project thread "Give Claude a professional trader's knowledge", the owner asked Claude to hold the project's trading knowledge and judgment, as a professional trader would, and asked how best to set that up, and at 09:40:15 UTC "I just assumed the professional trader and I may be wrong, feel free to fill on this".
- **Decided.** Claude holds the project's trading knowledge and judgment, as a **systematic trader**: part quant researcher, part risk manager, not a discretionary caller ([TRADING](TRADING.md#the-role-a-systematic-trader-not-a-discretionary-one) says why: that is the trader who loses as a group, while the app's money handling already matches systematic funds). The knowledge lives in [TRADING](TRADING.md), distilled from the three reviews of 1 and 2 November with their sources in [REFERENCES](REFERENCES.md#trading-research--2026-11-01-and-2026-11-02); rule 15 of [AGENTS.md](../AGENTS.md) makes every thread that touches the trader, the policy, sizing, exits, costs, the twins, the scores or a trading idea read it first; the `trading-review` skill in `.claude/skills/` holds the checklist and loads only then. `.claude/` is kept out of every image, as the AGENTS files are.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19) and this thread's "feel free to fill on this", each the recommended option: the systematic role rather than the discretionary one the owner guessed; the three pieces the official Claude Code documentation describes (facts that apply every session in the instruction file, kept short; procedures and long reference in a skill that loads on demand; sources in a register) rather than one long instruction file; no subagent, since the documentation reserves subagents for noisy side work and the review is read by the thread itself.
- **Unchanged:** paper only; nothing in the running app, the trader, its generation, the policy, the limits, the twins or the running paired test due 2026-11-16; the document grants no permission and moves no limit.

## 2026-11-02 — Twins and a veto, part 2: the veto twin, a weekly momentum twin and longer scorecard rows (ExecPlan 0041)

OBSERVED: at 09:18:05 UTC, in the project thread "Compare the long/short trader with professionals", the owner asked "can anything be integrated into the app", and at 09:20:01 UTC wrote "I don't mind and approve changing whatever is best for the app, that includes changing the trader if it's worth". At 09:22 UTC the coordinator relayed both to the project thread "Build twins and a veto" as the word [ExecPlan 0041](archive/plans/0041-twins-and-a-veto.md)'s part 2 was waiting for, with two additions from that thread's research (a Claude Doc), its spec for the first kept here: "At the first finished 15-minute bar after 00:00 UTC each day, it goes long if the last complete UTC day's close is above the close 8 days earlier, short if below, and makes no change if equal. Size it like HOLD: whole wallet at 1x, no stop, no time exit, latches NONE, liquidation and funding as the trader's. It exits only on a flip, warms up for 8 complete UTC days, and builds daily candles in code from the stored 1-minute candles."
- **Decided.** Part 2 is built as one update with one double-click (`TWIN_SET_V2`, generation 12, migration `0030`): the veto twin `TREND_VETO`, whose trend-rule entries the entry veto `ENTRY_VETO_V1` may let in, halve or skip within 2 minutes, silence letting them in, and the daily placebo that compares its answers with the plain rule and with random answers at its own rates ([§4.3](archive/plans/0041-twins-and-a-veto.md#43-the-veto-agent-update-2-entry_veto_v1-evaluator-generation-12)); the weekly momentum twin `MOMENTUM_1W` ([§4.1](archive/plans/0041-twins-and-a-veto.md#41-the-twins-code)); and the 4-hour and 24-hour rows of the trader's direction calls on the Scorecard page, on the page only ([§4.5](archive/plans/0041-twins-and-a-veto.md#45-the-scorecards-longer-rows-part-2-folded-in-on-2026-11-02)).
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19) and the coordinator's design points, each in [plan §13](archive/plans/0041-twins-and-a-veto.md#13-decision-log): the three twins of part 1 go on in their segments with their history; the trader is not changed (a cost gate or a funding filter on its entries would restart its paired check due 2026-11-16); the longer rows need more calls than the hour's, since calls 15 minutes apart overlap. After the independent review: the momentum twin reads no day on the day it starts (the owner's "first finished 15-minute bar after 00:00 UTC"), reads a day not complete yet again at the next bar instead of spending it, and a flip enters on the levels its exit left; a rollback to images from before part 2 first stops the two new twins.
- **Unchanged:** paper only; the owner's account and its ledger, the trader, its prompt and generation 11, `FUTURES_POLICY_V1` and its limits, code's protection, and the three carried twins' rules and values. The twins are not the owner's account, and nothing in the league table or the placebo changes a rule.

## 2026-10-31 — The agents' provider, as built (ExecPlan 0049)

OBSERVED: the redesign's Settings part was installed (`5aa35ca`) and that thread said ExecPlan 0049 could start; the plan was built on the owner's approval of 08:03:30 UTC.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each the recommended option ([plan §14](archive/plans/0049-choose-the-agents-provider-and-see-usage.md#14-decision-log)): the two APIs called with the runner's own standard-library HTTP client instead of the vendors' SDKs (no package in the runner image); each card with its own "Use" button and a confirmation instead of a `RadioGroup`, which is not installed and suits a form value rather than a confirmed switch; the header's usage button outlined like the bell beside it; Codex's windows read every 10 minutes while Codex runs the agents and after a refused call; the agents pause during a switch's check (at most 20 minutes; corrected after the independent review: the first draft said they kept running on the provider in force, which the runtime does not do once the new profile is composed); after a refused switch the provider in force is put back at once with the usage-limit block it had, while the owner's own pick always runs the check; the credential routes behind their own key, which the agent worker does not hold.
- **Changed with this update:** rule 10 of [AGENTS.md](../AGENTS.md) and the rows Authoring/runtime and Deployment below, [CONFIGURATION](CONFIGURATION.md), and the contracts the plan names (§10 step 3).
- **Unchanged:** paper only; the trader, its prompt and generation, `FUTURES_POLICY_V1` and its limits, the sizing, the costs, the twins, the scores, the reviewers, the coach and code's protection. Codex stays in force until the owner picks another provider.

## 2026-10-31 — The new design for Markets and Settings (ExecPlan 0048, part 3)

OBSERVED: the owner's asks of 09:18 UTC (the other pages with less text and fewer numbers, "feel free to be creative", shadcn through its skill and CLI) cover part 3 as they did part 2; at 11:26 UTC the owner tapped "Yes, merge and install" for part 2.
- **Decided.** [ExecPlan 0048](archive/plans/0048-the-cockpit.md) part 3 ([§4.13–§4.15](archive/plans/0048-the-cockpit.md#413-markets-part-3)): Markets becomes a strip of the market's numbers over a taller chart with an interval switch, opening on 15m; Settings becomes rows with their controls for the agents (the switch a `Switch`), cards for the models, a card for the run, tiles for the limits and the parts' health, and the balances with the top-up inline. Every detail stays one tap away in a `Popover` or tooltip.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each the recommended option ([plan §13](archive/plans/0048-the-cockpit.md#13-decision-log)): only what the engine has (no reviews switch, no sign-in button, no daily-loss gauge, since the engine has none of them or the read does not serve it); the switch as an `Item` row's action; the account summary card folded into the balances.
- **Unchanged:** paper only; the engine, its reads, requests and labels, the trader, the policy and its limits, the money paths and the protection; no migration, no new dependency, component, secret or host.

## 2026-10-31 — The new design for Trades, a trade and Decisions (ExecPlan 0048, part 2)

OBSERVED: at 09:18:29 UTC, after part 1 was installed, the owner wrote "other than the main page (pilot) rest of the pages haven't changed at all, I want other pages as well to have a great modern UX and UI that is meaningful, right now too much text and numbers are displayed, feel free to be creative for other pages as well", and at 09:18:56 UTC "leverage shadcn components using skills and cli of shadcn using official documentation"; the coordinator passed both to the project thread "Build the new Claude Design redesign".
- **Decided.** [ExecPlan 0048](archive/plans/0048-the-cockpit.md) part 2 ([§4.9–§4.12](archive/plans/0048-the-cockpit.md#49-trades-part-2)): Trades becomes a count, a results strip and short rows; each trade's page a hero ("Long · 2x", how it ended, its net and R) over a chart, the price rail, the costs, the review, the decisions behind it and the fills; Decisions a playbook of the coach's note, then a timeline by day and a scorecard of pictures, every earlier table one tap away. Markets and Settings follow as part 3. `Tabs`, `HoverCard`, `Popover` and `Switch` were added with the official shadcn CLI.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each the recommended option ([plan §13](archive/plans/0048-the-cockpit.md#13-decision-log)): two installs for the remaining five pages; the calls split by the trader's confidence where the design splits them by market condition, which the API does not serve; the scorecard tab in the address; short account words with icons; leverage in the trade's heading instead of the rows; the chart's level lines only while a trade is open; nothing removed.
- **Unchanged:** paper only; the engine, its reads and labels, the trader, the policy and its limits, the money paths and the protection; no migration, no new dependency, secret or host.

## 2026-10-31 — The agents' provider: four to choose from, the two APIs with a daily cap (ExecPlan 0049)

OBSERVED: at 07:49:33 UTC, in the project thread "Choose agent provider and show usage", the owner asked "When the new design implementation is finished, I want the app to have ability to select between codex cli, claude cli, claude api, openai api in settings somewhere to handle the agents, probably show them as cards and add some details with great ux, also somewhere in the app best for ux I want the app to show the details for example usage, session usage, 5hour usage, weekly, make sure to display them for best ux leveraging shadcn". At 08:03:30 UTC, in the same thread, the owner picked **"Yes, all four with a daily cap"** on the card "Include the two pay-per-token APIs (Claude API, OpenAI API)?". The option read: "API keys go in Settings. Paid calls stop at a daily cap (prefilled at $10, you can change it). At today's pace, about $3-7 a day while an API is in use."
- **Decided.** [ExecPlan 0049](archive/plans/0049-choose-the-agents-provider-and-see-usage.md) is approved as part of M11, built after the redesign (ExecPlan 0048) has installed its Settings part: Settings gets four provider cards (Codex CLI with the ChatGPT login, Claude CLI with a Claude plan token, Claude API and OpenAI API with keys the owner pastes); the owner's pick moves the agents after one passed test call; the header, the Cockpit and the cards show the usage each provider reports, and for the APIs the cost the app calculates. Each API needs a daily cap before it can be picked.
- **The owner's yes to paid APIs for the agents**, which [ROADMAP](ROADMAP.md#later-and-separately-approved) kept "later and separately approved": only the owner's pick starts one, under its daily cap; paid data and the rest of that list stay there.
- **Kept:** no fallback from one provider to another; a limit, a cap or an error blocks new entries as the usage limit does today, and code's protection continues. Rule 10 of [AGENTS.md](../AGENTS.md), the row Authoring/runtime below and the contracts change with the update that builds it; until then the Codex CLI with the ChatGPT login is the only runtime.
- **Unchanged:** paper only; the trader, its prompt and generation, `FUTURES_POLICY_V1` and its limits, the sizing, the costs, the twins, the scores, the reviewers, the coach and code's protection. Threads never read or enter a key.

## 2026-10-31 — The new design, starting with the Cockpit (ExecPlan 0048)

OBSERVED: at 06:37:59 UTC, in the project thread "Build the new Claude Design redesign", the owner asked "Implement this design in this codebase: <a Claude Design link> Read the design's files from that link. Match how it looks, using this codebase's own components and conventions." The coordinator relayed the owner's wishes for the work: less text and fewer numbers, the key figures on Home, more icons and pictures, and one page per install with before and after screenshots, Home first.
- **Decided.** [ExecPlan 0048](archive/plans/0048-the-cockpit.md), a part of M11, part 1: Home becomes the **Cockpit**, one screen with a status pill, the equity with its result, return, drawdown gauge and curve, the open position on a price rail, the trader's latest call and last twelve decisions, the engine room, the chart, the latest trades in R and four tiles on whether the trader is any good. The scorecard, the result checks and the coach's note move to Decisions, the league table to Trades, each opened from its tile. One new read, `GET /v1/futures/valuations`, for the curve. The menu names Home "Cockpit".
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each the recommended option ([plan §13](archive/plans/0048-the-cockpit.md#13-decision-log)): the app's own shadcn components, with `Tooltip` and `Sheet` where the design draws hover cards and popovers; NAV per unit for the curve; the detail moved, not removed; Trades, a trade, Decisions, Markets and Settings in later installs, each on the owner's word.
- **Unchanged:** paper only; the trader, the policy and its limits, the money paths and the protection; no migration, no new dependency, secret or host.

## 2026-10-30 — No disclaimers on the pages

OBSERVED: at 21:00:14 UTC, in the project thread "Remove disclaimers from the app", the owner asked "remove all disclaimers that are financial or whatever".
- **Decided.** The pages, the menu and the trade pop-ups lose every notice whose only job is to warn or qualify: the menu's "Paper trading · virtual USDT · simulated Bitcoin futures, at most 2x · No real exchange access", Home's "no funds move, and a top-up is not profit" with its PAPER ACCOUNT badge, the badges `PAPER` (on the cards), `MODELED FILL(S)`, `HINDSIGHT`, `MODELED TEST TRADES`, `MODELED ON 1-MINUTE CANDLES`, `NOTHING HERE CHANGES A RULE`, `ISOLATED TWIN(S)`, `FIXED RULES, NO AGENT` and `MODEL-AUTHORED`, and sentences such as "nothing is placed on an exchange", "not your account", "It cannot trade or change a rule", "a model's advice, not a rule" and "No real USDT is transferred" ([FRONTEND](FRONTEND.md#no-disclaimers-on-the-pages--2026-10-30)).
- **Nothing kept.** At 21:26:33 UTC, after the first pass kept the bar's PAPER badge and the "virtual USDT" unit, the owner wrote "I said literally leave nothing": the badge goes, money reads "USDT", and no page, title or label says "paper", "virtual" or "simulated" ("Top-up", "Holdings", "Trading", "Execution worker", "Costs"). What stays is what says how a number is made (after fees and funding, the order book and 1 bps a fill is priced from, cash as the zero line) and every state, error and warning about the app itself.
- **Unchanged:** paper only, the one simulated perpetual at up to 2x; the engine, the API and its labels, the trader, the policy, the limits and the protection; no migration, money path or dependency.

## 2026-10-30 — Live trades and pop-ups (ExecPlan 0047)

OBSERVED: at 17:11:25 UTC, in the project thread "Show every trade live with pop-ups", the owner asked "I need all trades to be realtime, if a position is opened, I want it to show on the app, and notification popup, implement it using most modern best practices for performance and library integration, use tanstack@react-query based on official documentation to implement this".
- **Decided.** [ExecPlan 0047](archive/plans/0047-live-trades-and-pop-ups.md), a part of M11: the futures worker announces each committed change on a PostgreSQL channel after its transaction; the API streams the trades to the web server as server-sent events, and the browser holds one live connection for all of the app's tabs. Each event refreshes the pages on screen through TanStack Query's invalidation and shows a toast for each fill and funding payment; desktop pop-ups for fills come on only when the owner turns them on in the header's bell menu, and only while no tab of the app has focus. While the connection is live, the lists poll every 60 s; when it is down, every page polls as before.
- **Chosen by the thread** under the owner's "decide for me" (2026-10-19), each the recommended option ([plan §13](archive/plans/0047-live-trades-and-pop-ups.md#13-decision-log)): server-sent events rather than WebSockets, `LISTEN`/`NOTIFY` after the commit rather than inside the money transaction, invalidation rather than cache writes, pop-ups off by default.
- **Unchanged:** paper only; the trader, the policy and its limits, the money paths and the protection; no migration, no new dependency, secret or host.

## 2026-10-28 — The agents' models on Settings

OBSERVED: at 14:16:52 UTC, in a project thread, the owner asked "in settings or somewhere appropriate, show the models as cards and what they do and show relevant information that can be extracted by codex".
- **Decided.** Settings gets a sixth section, **Models**, after Agents; no new page. One card per agent the app runs now (Trader, Trade reviewer, Decision reviewer, Coach): what it does and when it runs, the model and reasoning effort the profile in force gives its role, its template and generation, its newest call, its calls and tokens over the last 24 hours, its average per call and the models the app moves to if the one in force leaves the sign-in. One card for Codex: the CLI's version, the models the ChatGPT sign-in offers as the app's discovery read them, the usage limit as the app knows it, and all agent calls of the last 24 hours, the agents' check included. No decision card: Settings is the place the owner named first, and the words leave one reading.
- **What Codex gives.** OBSERVED in the code: `codex exec` reports a call's token counts once, at its end (`turn.completed`'s `usage`), and nothing about the allowance left; the app knows the limit only from a refused call ([`app.agents.usage`](https://github.com/MentorAliu/adaptive_spot_lab/blob/44b9a8a/services/engine/app/agents/usage.py)). The page shows the tokens as Codex reported them and says that Codex does not report the allowance left, instead of estimating it. The models offered come from the app's own discovery (`codex debug models`), already recorded.
- **Unchanged:** paper only; the models, efforts and rules in force; no migration, money path or dependency. The new read (`GET /v1/agent-models`) reads only records the worker and the runner already write; nothing calls Codex or a model.

## 2026-10-28 — Leaner agents (ExecPlan 0046)

OBSERVED: at 10:19:30 UTC, in the project thread "Optimize the trading agents", the owner asked "are the agents optimized for performance, efficiency, accuracy and other important things for the app goal, research and optimize and configure agents using official documentation". The thread measured the agents read-only on the PC, read OpenAI's and Codex's documentation and the pinned Codex source, and gave its findings in a document for the owner. At 10:35:32 UTC, in the same thread, the owner picked **"Build leaner agents"** on the card "Which agent update should I build?". The option read: "Same model and rules, about 45% fewer tokens per decision (about 135 to 80 credits a day). I make one test call on the PC first, then you get one update to double-click."
- **Decided.** [ExecPlan 0046](archive/plans/0046-leaner-agents.md) is approved as part of M11, built before ExecPlan 0041's part 2. Every agent call carries the runner's own short base instructions instead of Codex's built-in instructions for a coding agent, and no permissions, collaboration-mode or environment block. Generation 11 of the agent definitions (migration `0028`) is generation 10's trader as `FUTURES_DECISION_V5`, under the same rules, with a shorter prompt, the output schema only as the structured output format, and a shorter summary of its scores. One real call with the owner's own Codex sign-in on the PC comes before the merge; the update reaches the PC as one update the owner starts. ExecPlan 0041's part 2 moves to generation 12 and migration `0029`.
- **Noted.** Codex's configuration schema "STRONGLY DISCOURAGED" replacing its base instructions; the call on the PC checks that the model accepts them, and the scorecard and the refusals show any loss ([plan §13](archive/plans/0046-leaner-agents.md#13-decision-log)). ExecPlan 0045's result checks read the newest trader template's entries, so generation 11's first decision starts a new window: they count from zero entries and read "too few" until enough are filled, and generation 10's last result stays readable. The thread tells the owner before it asks for the merge.
- **Unchanged:** paper only; the model (`gpt-6.1-sol`) and every role's effort; the trader's rules and finish checks, `FUTURES_POLICY_V1` and its limits, the sizing, `FUTURES_COST_V1`, the twins, the scores, the reviewers, the coach and code's protection.
- **Merge approved.** OBSERVED: at 12:21:43 UTC the owner picked "Yes, merge it" on the card "Merge the leaner agents update so you can install it?". The card said that the test call with the owner's Codex sign-in worked and the app's own checks accept its answer; that a decision should take about 14,500 input tokens instead of 23,700, about 40% fewer and a bit less than the 45% estimated, so about 90 credits a day instead of 135; that after the update the agents check themselves again, entries waiting and exits never; and that the result checks start again from zero with the new trader. The option read: "I merge once the last engine tests pass (about 30 minutes), then tell you when to double-click update-app.cmd."

## 2026-10-28 — The charts follow the dark theme in Lightweight Charts' own colours

OBSERVED: at 06:50:56 UTC, in the project thread "Add dark mode to the charts", the owner asked "implement lightweight charts dark mode as well using official documentation for reference".
- **Decided.** The three charts follow the app's theme and switch live when it changes, the System choice included. In the light theme they keep the library's defaults (background `#FFFFFF`, text `#191919`, grid `#D6DCDE`); in the dark theme they take the colours Lightweight Charts' customization tutorial, "Chart colors", gives "to better suit a dark theme": background `#222`, text `#DDD`, grid `#444`, through `createChart` and `applyOptions` as that tutorial shows. No decision card: the words leave one reading.
- **Kept from [2026-10-25](#2026-10-25--the-charts-keep-lightweight-charts-own-look):** the candle, marker, provisional, price-line and NAV line colours, the crosshair and the scales' borders stay the library's own in both themes. Only the sentence "In the dark theme the chart stays white" no longer holds.
- **Unchanged:** the preset `b2fms61Bqi`, every other page, the data, the times in the viewer's zone; no dependency, server or money path changes.

## 2026-10-27 — Four checks from the r/ai_trading research, planned as one update (ExecPlan 0045)

OBSERVED: at 15:01 UTC, in the project thread "Research r/ai_trading", the owner asked "research reddit subreddit ai_trading posts and comments and check what other people are using that could benefit the app". The thread read the subreddit through a public archive from the owner's PC and delivered its findings ([ideas note](archive/ideas/ai-trading-reddit.md)). At 17:26:59 UTC the owner asked "is there anything that the app can leverage ?". At 19:04:55 UTC, in the same thread, the owner picked **"Plan them as one update"** on the card "Turn the best Reddit ideas into an app update?". The option read: "I write the plan for the four checks. You approve it before anything is built, and it reaches your PC as one update you double-click."
- **Decided.** [ExecPlan 0045](archive/plans/0045-where-the-results-come-from.md) is written as one code-only update with four checks:
  - a luck floor of random entries that use the trader's own exits;
  - a replay of the trader's entries through the other exits, with the gain or loss of its own early exits;
  - the cost of each trade as a share of its risk;
  - the taker buy volume Binance sends with each candle, stored and checked against what followed.
- **Approved.** At 21:09:40 UTC, in the same thread, the owner picked **"Yes, approve and build"** on the card "Approve the plan for the four checks and build it?". The option read: "I merge the plan, build and test the update in the cloud, and tell you when to double-click update-app.cmd." ExecPlan 0045 is approved as part of M11 and built before ExecPlan 0041's part 2. It takes migration `0027`, and 0041's part 2 moves to `0028`.
- **Unchanged:** paper only; the account and its ledger, the risk gate, the policy, the costs, the twins, the trader, the reviewer, the coach and code's protection. No check is shown to an agent or changes a rule.

## 2026-10-27 — A trader that commits (ExecPlan 0044)

OBSERVED: at 10:47:08 UTC, in the project thread "Find why the futures trader never trades", the owner asked "so far no trade or entry happened yet ? why is that". The thread answered from a read-only check of the PC: every one of 139 decisions since 2026-10-25 15:15 UTC was `HOLD` with `NO_EDGE`, with no refusal or fault; the trader's prompt, the coach's two `SIT_OUT` notes and a round trip's costs against 15-minute moves explain it ([ExecPlan 0044 §2](archive/plans/0044-a-trader-that-commits.md#2-what-the-app-has)). At 10:57:37 UTC, in the same thread, the owner answered **"A"** to the card "What to do about a trader that always holds". The option read: "A new trader version that has to state a direction and may act on it. The policy, the 0.25% risk per trade, the 24 entries a day and the loss limits stay as they are. Expect small losses to fees at first unless it shows real skill."
- **Decided.** [ExecPlan 0044](archive/plans/0044-a-trader-that-commits.md) is approved as part of M11, built before ExecPlan 0041's part 2: generation 10 of the agent definitions (migration `0026`). The trader says `UP` or `DOWN` at every decision (`NO_VIEW` only when it abstains), may enter in the direction of its call at `MEDIUM` or `HIGH` confidence with a stop of 2 or 3 times the 15-minute ATR and a time exit of 4 hours or more, and its prompt no longer says holding is right most of the time; the coach no longer advises sitting out before ten trades are reviewed. Code refuses an entry against the trader's own call, at `LOW` confidence, or with a shorter stop or time exit. It reaches the PC as one update the owner starts. ExecPlan 0041's part 2 moves to generation 11 and migration `0027`.
- **Unchanged:** paper only; the account and its ledger, the risk gate and its sizing (0.25% of equity at the stop), `FUTURES_POLICY_V1`'s sets and limits (24 entries and 120 decisions a UTC day, the cooldowns, the 2% daily loss and 8% drawdown latches), `FUTURES_COST_V1`, the scoring, the twins and code's protection. No forecast, confidence or note is read by code that trades.

## 2026-10-26 — Score every decision against what followed (ExecPlan 0043)

OBSERVED: at 11:34:27 UTC, in the project thread "Score every decision against what followed", the owner asked "I want functionality of app that also tracks what happened for the decision, for example if it decided to hold and price went up for the specific time, I want that to record too and let agent analyze that if it's useful, same would go if it decided to hold and price went down for the time, include all combinations, be creative and how would this help the agent or the app ?". The thread answered with a Claude Doc, "Score every decision: proposal", and at 11:51:05 UTC, in the same thread, the owner picked **"Yes, in two updates"** on the card "Build the decision scorecard as proposed?". The option read: "I write ExecPlan 0043 and build update 1 (the records). Update 2 (the agents learn) follows once update 1 is checked on your PC."
- **Decided.** [ExecPlan 0043](archive/plans/0043-score-every-decision.md) is approved as part of M11, built before ExecPlan 0041's part 2: code scores every decision of the trader, every finished 15-minute bar and every twin entry against what the price did 15 minutes, 1 hour, 4 hours and 24 hours later, with a long and a short test trade after fees, slippage and funding and one label per checkpoint; Decisions shows what followed each decision and Home a scorecard (update 1, migration `0024`). Once update 1 is checked on the PC, the trader reads its scored decisions and the scorecard and states the direction it expects, a daily decision review grades the day's largest misses and worst decisions on whether they were knowable then, and the coach also writes after it (update 2, generation 9, migration `0025`). ExecPlan 0041's part 2 moves to generation 10 and migration `0026`.
- **Unchanged:** paper only; the account and its ledger, the risk gate, the policy's values and limits, the twins' rules and code's protection. A score, a scorecard row or a lesson changes no rule; the scores are hindsight, labeled so.

## 2026-10-25 — The charts keep Lightweight Charts' own look

OBSERVED: at 16:01:21 UTC, in the project thread "Use native chart styling", the owner asked "remove the additional styling of lightweight charts, and use native lightweight charts styling".

- **Decided.** The three charts (the futures chart on Home, the coin chart on Markets, a test report's NAV chart) drop the colours taken from the preset's tokens, the theme switch's repaint, the hollow rising candles, the grey last-price line, the price lines' own colours and styles, the NAV lines' widths and the border around the chart. They use Lightweight Charts' defaults: a white chart with dark text and its grid, green rising and red falling candles, red dashed price lines with their titles.
- **Kept, because each carries information:** the data, the gaps as whitespace, the entry and exit markers (a marker must name a colour, so they take the library's own candle green `#26a69a` and red `#ef5350`), the grey of a candle that is open or incomplete (`#9e9e9e`), one colour per NAV line so the strategy and its baselines can be told apart (the first is the library's line blue `#2196f3`), the price format, the times in the viewer's zone, and the sizes. In the dark theme the chart stays white: that is the library's default and it is readable.
- **Unchanged:** every other page keeps the shadcn preset `b2fms61Bqi`; no dependency, server or money path changes.

## 2026-10-25 — No owner sign-in and no setup (ExecPlan 0042)

OBSERVED: at 08:08:07 UTC, in the project thread "Bitcoin futures app plan", the owner asked what was needed to resolve the thread, and was given the three steps M11's update 2 left (set up the owner with the setup key and a passphrase, confirm the 10,000 virtual USDT, turn the agents on in Settings). At 08:10:03 UTC, in the same thread: "remove the owner completely, no setup should be needed, as I will use this app only".
- **Decided.** [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md), as one update of M11 with one double-click: no sign-in, passphrase, session or setup key; the API's routes need the service key alone, which only the web holds, and the web stays on the PC's loopback. The app contributes the initial 10,000 virtual USDT itself, once, when the API starts, and the agents switch themselves on (the agents' check still enables them). No decision card: the words leave one reading.
- **Changed now:** rules 12 and 14 of [AGENTS.md](../AGENTS.md). The earlier texts, kept here: rule 12 "**Top-ups are contributions:** owner-confirmed virtual funding only; deposits do not create P&L or reset high-water NAV and safety latches."; rule 14's "it does not cover creating or funding the owner account, the off switch or Stop, an `OWNER` pause, or a new run after a drawdown stop."
- **Unchanged:** paper only; the money rules and the funding journal; the owner's controls in Settings, now without a sign-in (the agents' off switch, Pause, Resume and Stop, top-ups, Start after a drawdown stop); what is recorded as the owner's. The setup key file on the PC is left where it is; nothing reads it.

## 2026-10-25 — Twins and a veto: the first experiment on whether the agents help (ExecPlan 0041)

OBSERVED: at 07:22 UTC, in the project thread "Find an AI agent trading edge", the owner asked "On everything so far related to trading crypto or stocks in general, is there a possible way to use ai agents to create an edge, think of this as an inventor and be creative". The thread answered with a Claude Doc, "Where AI agents could earn a trading edge" (its ranking kept as [an ideas note](archive/ideas/agent-trading-edges.md)), and at 07:36:24 UTC, in the same thread, the owner picked **"Plan it now, build after the coach"** on the card "Plan 'twins and a veto' as the next experiment?". The option read: "A planning thread writes ExecPlan 0041 now; it is built once 0040's first part (the trade reviews and coach) is installed."
- **Decided.** [ExecPlan 0041](archive/plans/0041-twins-and-a-veto.md) is approved as part of M11, built after ExecPlan 0040's part 1: three isolated paper accounts (hold BTC, a trend rule, the trend rule with a cost gate and a funding filter) trade the perpetual beside the trader with the same money, limits, costs and fills, and Home compares them with the trader in a league table; then a fourth account whose rule's entries a veto agent may refuse or halve but never start, checked against random verdicts at the agent's own rates. Two updates, each with one double-click. Where the plan's design differs materially from the Doc's description of the experiment, the thread asks the owner.
- **Unchanged:** paper only; the owner's account and its ledger, the trader, its policy and limits, and code's protection. The twins are not the owner's account, nothing in the table changes a rule, and the brainstorm's other ideas wait for the owner's word; the hypothesis-factory idea would reopen the research switched off on 2026-10-21 and is not approved.

## 2026-10-24 — An AI review of every trade, and a coach (ExecPlan 0040)

OBSERVED: at 08:41 UTC, in the project thread "Add AI review of every trade", the owner asked for an AI agent that analyzes each trade, its circumstances and the factors inside and outside the app, a stored summary in the best format, and another agent that reads those reviews and suggests the next trade to the agent that trades, with ideas welcome. At 09:17:13 UTC, in the same thread, the owner picked **"Build it as proposed"** on the card "Build the trade reviewer and the next-trade coach as proposed?". The option read: "After the futures trading is installed, I build the reviewer, the coach and the scoreboard as one update; about 2 small AI calls per closed trade."
- **Decided.** [ExecPlan 0040](archive/plans/0040-trade-reviews-and-a-coach.md) is approved as part of M11: a fact sheet code builds for each closed futures position; a reviewer (EVALUATOR) and a coach (ANALYST) that only write records; the trader shown the coach's note and recording whether it followed it; and a scoreboard that compares the trades that followed the advice with those that ignored it. Built after M11's update 2 and delivered with one double-click.
- **Unchanged:** paper only; the trader's authority, the risk gate, the policy's values and limits, and code's protection; no new data source, host or secret. Lessons and advice change no rule. The proposal's other ideas wait for the owner's word.

## 2026-10-23 — The owner keeps Codex for the agents (ExecPlan 0039)

OBSERVED: at 17:15 UTC, in the project chat, after M11's update 1 (Claude Code instead of Codex) was installed at 16:15 UTC and before its sign-in ran: "actually keep the codex cli instead, I changed my mind".
- **Decided.** The agents stay on the Codex CLI with the owner's ChatGPT login. Update 1b puts Codex back as a forward update ([ExecPlan 0039 §5.6.2](archive/plans/0039-bitcoin-futures-on-paper.md#562-update-1b-codex-back)); the rest of [ExecPlan 0039](archive/plans/0039-bitcoin-futures-on-paper.md) stands, with its one trader on Codex.
- **Changed now:** rule 10 of [AGENTS.md](../AGENTS.md) and the row Authoring/runtime below name the Codex CLI's ChatGPT login again. The texts of the morning, kept here: rule 10's "the Codex CLI's refreshable ChatGPT login until M11's first update, then Claude Code's CLI with the owner's own Claude subscription"; the row's "Runtime: Codex CLI with the owner's ChatGPT login until M11's first update, then Claude Code's CLI with the owner's own Claude subscription".
- **Kept:** migration 0018's two Claude definitions stay stored and in code, unused, since the worker starts only when the two agree; update 1's `claude_auth` volume stays on the PC, empty, until the owner says.

## 2026-10-23 — M11 approved: Bitcoin futures on paper (ExecPlan 0039)

OBSERVED: at 12:51 UTC, in the project thread "Bitcoin futures app plan", the owner asked for an app that trades only bitcoin, on futures and very often, with a toast for every trade, entries and exits on the chart, Claude's CLI instead of Codex's for the agents, and fewer agents, and asked what decides how often futures should trade; at 12:52 UTC, in the project chat: "also its authorized by me to drop eveything so far, basically a clean database is fine". At 13:09:17 UTC, in the same thread, the owner picked **"Yes, 15-minute decisions"** on the card "Build the Bitcoin futures app with shorts and up to 2x leverage?". The option read: "I record your yes for shorts and up to 2x leverage, update the rules, then build: the Claude update first, the futures app second."
- **Decided.** [ExecPlan 0039](archive/plans/0039-bitcoin-futures-on-paper.md) is approved as written, as M11: one simulated BTCUSDT perpetual on paper from Binance's public data, long or short, at most 2x leverage, isolated margin, modeled fees, funding and liquidation; a decision every 15 minutes and after a sharp move, code protection every second, at most 24 entries a UTC day; one trader agent instead of nine; Claude Code's CLI with the owner's own Claude subscription instead of Codex; a clean database. Two updates: Claude first, then the futures app.
- **The owner's explicit yes** to shorts and to leverage up to 2x, on paper, which [ROADMAP](ROADMAP.md#later-and-separately-approved) kept "later and separately approved". Leverage above 2x, live trading and the rest of that list stay there.
- **The clean start is authorized** by the 12:52 UTC message: the futures app starts from an empty database on a new volume. Nothing is deleted: the old volume `postgres_data` and a dump in `backups/before-futures/` stay until the owner says otherwise.
- **Changed now**, each worded to hold before and after the two updates: rule 1 and rule 10 of [AGENTS.md](../AGENTS.md), [PROJECT](PROJECT.md) P02, [ACCEPTANCE_CHECKLIST](ACCEPTANCE_CHECKLIST.md) A01, and the rows Scope and Authoring/runtime below. The earlier texts, kept here: rule 1 "**Paper only:** spot, long-only, for BTC, SOL and the coins the installed operating policy names. No real exchange credentials, signed/private exchange APIs, live adapter, hidden live switch, Testnet, Demo, leverage or shorting."; rule 10's "Codex login is private and refreshable; paid API fallback is disabled."; P02 "Spot, long-only, for BTC, SOL and the coins the installed operating policy names"; A01 "Only spot observations and paper execution of BTC, SOL and the coins the installed operating policy names are available; rejected private/live/short/leverage requests create no financial effects."; Scope "BTC and Solana only, spot only for now."; Authoring/runtime "Codex or Claude Code for development; Codex CLI with the owner's ChatGPT login as initial runtime option." The contracts (RISK_POLICY, AUTONOMY_MATRIX, LEDGER, PAPER_EXECUTION, MARKET_DATA, RUNTIME_AGENTS, SECURITY) change with the update that changes their code.
- **Unchanged:** paper only; no exchange credentials, signed or private APIs, live adapter, Testnet or Demo; the money rules; the daily loss latch and the drawdown stop; the owner's own controls; rule 14, under which creating and funding the owner account stay the owner's steps.

## 2026-10-23 — The owner approves a faster market-data cleanup (ExecPlan 0038)

OBSERVED: at 08:13 UTC the owner reported "Market Data is being display as unavailable" in the project chat; in the project thread "Market data unavailable" the owner answered "yes" at 09:06 UTC to planning a fix of the slow hourly cleanup, and "Approve" at 09:13 UTC to [ExecPlan 0038](archive/plans/0038-faster-market-data-cleanup.md) as proposed (docs PR #111, merged as `0cff620`).
- **Decided.** Migration `0017` replaces the retention function's payload search and adds five indexes on references to `market_observations`; each `QUEUE_OVERLOAD` feed drop records its slowest database call. Delivered through one `update-app.cmd`.
- **Unchanged:** the retention rules, the call size, the deadlines, the fence, the overload threshold and PostgreSQL's configuration.

## 2026-10-22 — The owner asks for clear values in local time (ExecPlan 0037)

OBSERVED: at 11:59 UTC, in the project chat, passed to the project thread "Beautiful, clear app design", the owner wrote "I want all the values formatted for best ux, dates, price etc, and displayed on my local time".
- **Decided.** The message asks for the change itself, so [ExecPlan 0037](archive/plans/0037-clear-values-in-local-time.md) is approved as Claude writes it, and Claude makes the format calls under the owner's standing delegation ([2026-10-19](#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031); 0037 §11): one format for each kind of value, from the API's exact string; every time in the browser's own time zone (Budapest on the owner's PC), with the offset and UTC on hover. The owner's rules of [the same morning](#2026-10-22--the-owner-asks-for-a-clear-beautiful-app-execplan-0036) hold: only the preset's shadcn components, no library added or changed.
- **Unchanged:** the API and its exact decimal strings and UTC instants in every request; the rules that run on the UTC day (the daily loss limit, the coin scan), which the pages now give on the owner's clock; every owner control, accounting, the five protections and every limit.

## 2026-10-22 — The owner asks for a clear, beautiful app (ExecPlan 0036)

OBSERVED: from 07:40 to 07:42 UTC, in the project thread "Beautiful, clear app design", the owner asked what a professional application like this has for UX, UI and library integration by official documentation, and wrote "I want to refactor the UI for beautiful UX and display the data in the best possible way to be clear"; then "research the web for best practices, UX and make sure it integrates very well with libraries, also make sure to use shadcn skills to generate components", "use only native shadcn styling and components and don't modify other libraries as well", "feel free to use icons to make the UX better" and "make sure to be creative".
- **Decided.** The messages ask for the change itself, so [ExecPlan 0036](archive/plans/0036-a-clear-beautiful-app.md) is approved as Claude writes it, and Claude makes the design calls under the owner's standing delegation ([2026-10-19](#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031); 0036 §11): a sidebar app shell with a bottom tab bar on phones, a light and a dark theme, Home led by the trading status and the account's value, and states shown with an icon and a word. Components come from the shadcn CLI and the preset; no library is added or changed.
- **Unchanged:** the five pages and their addresses, every owner control, the API, accounting, the five protections and every limit.

## 2026-10-21 — The owner asks for fewer pages and no research (ExecPlan 0035)

OBSERVED: at 06:29 UTC, in the project thread "Simpler app for trading", the owner wrote "why are there so many pages, I don't think I need all these pages, also why is there a research page, and what it does, I think there are to many pages that as a User I don't care to see, it makes it to complicated, I don't think this app is on research anymore hence I want the app to let it trade on it's own, make a great refactor of the app and leave only the most important parts that as a User I may want to see".
- **Decided.** The message asks for the change itself, so [ExecPlan 0035](archive/plans/0035-a-simpler-app-that-trades-by-itself.md) is approved as Claude writes it, and Claude makes its calls under the owner's standing delegation ([2026-10-19](#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031); 0035 §11). Five pages: Home, Trades, Decisions, Markets and Settings. Research is switched off in the code that starts agent work, and the update retires the three research containers; their data volume and the `asl_research` role stay.
- **Changed with the update:** the mission and rules 3, 4 and 14 of [AGENTS.md](../AGENTS.md). The earlier texts, kept here: the mission "a local, single-owner, **agent-driven paper-trading research application**"; rule 3 "agents may investigate evidence from the sources in force, request bounded experiments and propose trade/position actions under the policy in force."; rule 4 "Research inside the envelope in force may run automatically."; rule 14 "The owner's authorization covers leaving collection, trading, research and the agents running".
- **Unchanged:** the five protections, the owner's own controls (the agents' switch, Pause, Stop, a new run after a drawdown stop, top-ups, the passphrase and the Codex sign-in), accounting and reconciliation, every limit, policy and generation of agent definitions, and the database's tables and rows.
- **Installed.** OBSERVED: asked on a card in the same thread "Install the simpler five-page app now, or undo the merge first?", after the thread had merged the change itself, the owner picked "Install it now" at 10:49:56 UTC; the update of 10:50 to 11:11 UTC installed it ([ExecPlan 0035 §12](archive/plans/0035-a-simpler-app-that-trades-by-itself.md#12-progress)).

## 2026-10-21 — M10 update 2: ZEC, NEAR and XRP traded on paper (ExecPlan 0033)

OBSERVED: at 06:24 UTC, in the project thread "Get M9 ready to build", the owner wrote "go" to building M10's update 2, which the owner's "Research and trade" of [2026-10-20](#2026-10-20--m10-approved-research-and-trade) approved.
- **Decided by Claude under the owner's delegation, by 0033 §5.2's rule:** the three coins are ZEC, NEAR and XRP, the three best-ranked watchlist coins whose latest note has an `ACCEPTABLE` review and is not `RULE_OUT`. ETH, ranked first, has no note: its note ended `QUOTA_BLOCKED` (0033 §13).
- **Changed when update 2 is installed:** rule 1 of [AGENTS.md](../AGENTS.md), [PROJECT](PROJECT.md) P02 and [ACCEPTANCE_CHECKLIST](ACCEPTANCE_CHECKLIST.md) A01 name "BTC, SOL and the coins the installed operating policy names" instead of BTC and SOL. The earlier texts, kept here: rule 1 "**Paper only:** BTC/SOL spot, long-only."; P02 "BTC/SOL spot, long-only"; A01 "Only approved BTC/SOL spot observations and paper execution are available; rejected private/live/short/leverage requests create no financial effects."
- **Unchanged:** every limit and cadence value of `AGENT_POLICY_V2`, which `AGENT_POLICY_V3` keeps for all five coins together; paper only, spot only, long only; the five protections and the money rules. A coin's note or rank still adds no coin, limit or order.

## 2026-10-20 — The owner asks for a full cleanup (ExecPlan 0034)

OBSERVED, in the project thread "App cleanup": at 19:11 UTC the owner wrote "I want you to deeply research the app and do a thorough cleanup of the app as because it has been running and developed for quite some time and a lot has been added, what would be the most important things to cleanup ?"; at 19:13 UTC "Cleanup without my approval, cleanup everything that is redundant, leftovers and other"; and at 19:29 UTC, after Claude offered to shrink Docker's disk file on the PC, "Yes clean up docker as well".
- **Decided.** [ExecPlan 0034](archive/plans/0034-app-cleanup.md) is approved as Claude writes it, and Claude picks the items. This is the owner's explicit authorization, which [OPERATIONS](OPERATIONS.md#backup-and-restore) requires, to delete this app's old backups and its leftover Docker volumes and images, each by exact name.
- **Unchanged:** the five protections, the money rules, every limit and policy, the database's tables and rows, and other projects' Docker resources ([2026-10-03](#2026-10-03--this-projects-old-test-runs-removed-other-projects-docker-resources-left-to-the-owner)).

## 2026-10-20 — M10 approved: research and trade

OBSERVED: at 11:03:32 UTC, in the project thread "Get M9 ready to build", the owner picked **"Research and trade"** on the card "Build M10 so the agents may also trade three new coins on paper?". The option read: "I build two updates. After the first one runs, I pick three watchlist coins, and the agents may trade them on paper under the same total limits."
- **Decided.** [ExecPlan 0033](archive/plans/0033-m10-the-agents-look-beyond-btc-and-sol.md) is approved with both updates, which settles its §12. Update 1 (the daily watchlist, the coin notes and the Coins page) is built first and adds no coin to trading. Update 2 is built only after update 1 has run on the PC, from the watchlist and the notes the PC holds then (0033 §5.2).
- **Unchanged until update 2 is installed:** rule 1 of [AGENTS.md](../AGENTS.md) (BTC and SOL only), every limit of `AGENT_POLICY_V2`, the five protections and the money rules.

## 2026-10-20 — M9 accepted; M10 planned under ExecPlan 0033

OBSERVED: at 10:34:53 UTC, in the project thread "Get M9 ready to build", the owner picked **"Go"** on the card "Accept M9 and plan M10, where the agents research coins beyond BTC and SOL?". The option read: "I write M10's plan in the same simple style as M9, then ask you to tap once before building; trading any new coin still needs your yes."
- **Decided.** M9 ([ExecPlan 0032](archive/plans/0032-m9-news-and-events-the-agents-trade-on.md)) is accepted as installed: both updates are `COMPLETE` on the PC (0032 §14). [ExecPlan 0033](archive/plans/0033-m10-the-agents-look-beyond-btc-and-sol.md) re-scopes M10 ([ExecPlan 0028](archive/plans/0028-m10-coin-discovery-and-controlled-expansion.md)) under M8's rules. It is PROPOSED, and nothing is built before the owner's next pick (0033 §12).
- **Calls Claude made in the plan**, under the owner's delegation: D1 to D8 (0033 §4). Binance's own listing is the only source; a watchlist of 8 by liquidity rank; coin notes with their own count of 3 a day; three more tradable coins at most, named from the PC's data; every total limit unchanged; no automatic rotation; research first.
- **Unchanged:** rule 1 of [AGENTS.md](../AGENTS.md) (BTC and SOL only) until the owner picks trading and M10's update 2 is installed; the five protections and the money rules.

## 2026-10-19 — M8 accepted; M9 built under ExecPlan 0032

OBSERVED: at 20:47:35 UTC, in the project thread "Plan M9", the owner picked **"Go"** on the card "Start building M9, the agents that read news and trade on it?". The option read: "I build it now and tell you when each of the two updates is ready to double-click. This also signs off M8 as done."
- **Decided.** M8 ([ExecPlan 0031](archive/plans/0031-m8-simple-app-that-runs-itself.md)) is accepted as installed. [ExecPlan 0032](archive/plans/0032-m9-news-and-events-the-agents-trade-on.md) is approved for implementation as written, with D1 to D8 (its §4).
- **Calls Claude made while building update 1**, under the same delegation (0032 §4 and §13):
  - CoinDesk's feed is dropped, because its terms forbid automated access. No other crypto news outlet and no Solana status feed was confirmed from the publisher's own pages, so update 1 carries none.
  - Every feed in update 1 concerns both coins, so the name filter of 0032 §5.1 is not built yet. A feed either starts work for both coins or starts nothing (the calendar). The Atom reader waits for a feed that needs it.
  - A feed's first fetch is its baseline: items already published before the update start no investigation.
  - The ECB feed waits 12 hours between investigations, because it also carries every speech and interview.
  - The older database guards now look names up on a fixed path (0032 §6), because every app identity can create temporary tables.
- **Unchanged:** the five protections, the money rules (D8) and the owner's own steps listed under M8 part 1 above.

## 2026-10-19 — M8 part 1: the rules for an app that runs itself (ExecPlan 0031)

Under the owner's pick of 11:37:19 UTC ([below](#2026-10-19--the-owner-cuts-the-app-down-to-what-paper-trading-needs-execplan-0031)), the first part of [ExecPlan 0031](archive/plans/0031-m8-simple-app-that-runs-itself.md) changes the rules; its three updates change the app.
- **Changed:** [AGENTS.md](../AGENTS.md) rules 3, 4, 13 and 14 and its work discipline; [AUTONOMY_MATRIX](archive/contracts/AUTONOMY_MATRIX.md#m8-the-app-runs-itself-execplan-0031), which says what each update moves from the owner to the app; the quality gates Q07 and Q09 ([ACCEPTANCE_CHECKLIST](ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone)); [PLANS](PLANS.md); [STATUS](STATUS.md) on one screen, its entries kept in [STATUS_HISTORY](archive/STATUS_HISTORY.md); [ExecPlan 0030](archive/plans/0030-agent-models-and-effort-per-role.md) trimmed.
- **Superseded, each only where it makes a step the owner's that M8 gives the app** (the entries are not edited):
  - the founding "Approval" row ([Owner-confirmed](#owner-confirmed)) and the [agent-driven revision authorization](#agent-driven-revision-authorization): new strategies, wider ranges, tools and sources still come from the owner, as an update the owner installs rather than an approval in the app;
  - [Completed milestones must run locally](#2026-09-28--completed-milestones-must-run-locally) (2026-09-28): delivery is an update the owner double-clicks, which leaves collection, trading, research and the agents running and writes the app's in-force records;
  - [M4 pilot approvals, activation and checkpoint](#2026-09-30--m4-pilot-approvals-activation-and-checkpoint-execplan-0015) and [M5-A implementation authorized](#2026-09-30--m5-a-implementation-authorized-execplan-0020) (2026-09-30): the activation scripts and the approval in chat per command give way to the update file, and read-only checks need no approval;
  - [M5-B started](#2026-10-02--m5-b-started-runtime-profile-gpt-61-sol-at-medium-effort-execplan-0020) (2026-10-02) and [the owner delegates the agents' model choice](#2026-10-19--the-owner-delegates-the-agents-model-choice-no-profile-change-during-m7s-switch-on) (2026-10-19): the profile is composed from the model table and recorded in force, with no owner approval;
  - [M5 closed on the capability probes](#2026-10-03--m5-closed-on-the-capability-probes-live-token-refresh-becomes-a-follow-up-execplan-0020) (2026-10-03), as to the probe suites as gates: the short check replaces them;
  - [ExecPlan 0026 approved](#2026-10-09--execplan-0026-approved-for-implementation-with-the-recommended-decisions) (2026-10-09), as to the owner's approvals of the policy, the protocol, the manifest and `PROMOTION_V2`, the owner's Start, the decision probes and the owner-only resume of the entry pause;
  - [M8 starts with hourly entry checks](#2026-10-18--m8-starts-with-hourly-entry-checks-when-the-app-holds-no-position) (2026-10-18), as to its own approval and experiment;
  - [the fast lane](#2026-10-18--the-fast-lane-for-pc-test-runs-from-m8-on) (2026-10-18), withdrawn.
- **Unchanged:** rules 1, 2 and 5 to 12; the five protections; the owner's off switch, Stop, top-ups, an `OWNER` pause and a new run after a drawdown stop; the Codex sign-in; the Claude desktop app's check on production updates (rule 9). Until each update is installed, the app's controls it replaces work as before.

## 2026-10-19 — The owner cuts the app down to what paper trading needs (ExecPlan 0031)

OBSERVED owner messages of 2026-10-19:
- 11:08 UTC, the root of the project thread "Hands-off milestones": "why am I doing all of this tinkering when you could decide for me, I don't want any of this enable, disable, start, do this do that, I want you to handle it, you have my authorization for everything";
- 11:10 UTC, in the project chat: "I want you do complete m7 as soon as possible and simplify the app as much as possible so I don't have to do all of this";
- 11:15 UTC, in the project chat: "this is to complex and honestly unecessary, why can't the app just use agents, why does it need all of this complexity ?";
- 11:37:19 UTC, in the thread, the owner's pick on the card "Cut the app down to the protections paper trading actually needs?": "Cut to essentials".

Before these, the owner had written in "Build M7" (2026-10-18 14:34 UTC): "I approve whatever needs to be done to speedup and resolve m7".

- **Read as.** The owner wants the app to run its agents by itself, without the owner's approvals, starts, probes, enables, starter files and reports. The owner asks why the app needs its layers at all. The rules that make these steps the owner's are the owner's own (AGENTS.md, this file), so the owner can change them.
- **The answer given** (the thread, 11:19 UTC). The founding rules treat the app as if real money and untrusted AI were at stake, and each milestone added a layer. On paper money, five things do the real protecting:
  1. paper only;
  2. the agents propose and the code fills at market prices, with exact accounting;
  3. hard limits and stops, in code;
  4. version tags on every trade;
  5. an off switch.
- **The card** (11:19 UTC):
  - **"Cut to essentials"** (recommended, and picked): "The app runs itself and you only double-click updates. A bad change trades on paper until it's fixed."
  - **"Automate, keep all"**: "Every layer stays and runs by itself: about two actions per milestone, and the long PC test runs stay."
- **Decided.** [ExecPlan 0031](archive/plans/0031-m8-simple-app-that-runs-itself.md) is approved for implementation as M8's plan, its §4 to §9 as written; its §13 records the option not picked. M8 keeps the five protections and makes every other owner step the app's own, recorded as `SYSTEM` and never as the owner. It arrives as three updates, each one double-click for the owner, after a documents-only part that changes the rules (0031 §4.9 and §9). Until each part is merged and installed, the app and the rules that part changes stay as they are. The first part names the entries this one supersedes.
- **Withdrawn.** The fast lane ([ExecPlan 0029](archive/plans/0029-fast-lane-pc-runs.md)), which the owner chose on [2026-10-18](#2026-10-18--the-fast-lane-for-pc-test-runs-from-m8-on) and the coordinator session held until the pick: the multi-hour PC gate runs it would shorten go ([ExecPlan 0031 §4.8](archive/plans/0031-m8-simple-app-that-runs-itself.md#48-tests-and-the-fast-lane)). [ExecPlan 0030](archive/plans/0030-agent-models-and-effort-per-role.md) loses the profile approval, Allow probes, the probe suites as gates and Enable, and keeps its model table, composition, usage-limit block and token summary (0031 §4.7).
- **Decided now, under the owner's authorization of 11:08 UTC:**
  - A thread or a session on the owner's PC may run read-only checks of the normal application without asking in chat first. This is the owner's approval in chat that [the 2026-09-30 rule](#2026-09-30--m5-a-implementation-authorized-execplan-0020) asks for, given as standing.
  - Threads check each step's result on the PC themselves. They do not ask the owner to report a step, write "done" or paste an id.
- **Not covered by the authorization until ExecPlan 0031's parts change the app and the rules:**
  - Pressing an owner control in the application. The application would record the owner's session for a click that was Claude's (rule 5), and rule 4 reserves approvals to the owner.
  - Changes to the normal application beyond what an approved deployment does.
- **Not covered after M8 either:**
  - The Codex sign-in, which is the owner's own account (rule 10).
  - Weakening the Claude desktop app's check on production updates (rule 9). That check is why each update stays one double-click.
- **Unchanged.** M7, closed under [ExecPlan 0026](archive/plans/0026-m7-agent-driven-main-decisions.md) by [the entry below](#2026-10-19--m7-closes-without-the-decision-probes-and-the-first-live-decision), its run and its records; every rule of AGENTS.md until ExecPlan 0031's first part.

## 2026-10-19 — M7 closes without the decision probes and the first live decision

OBSERVED owner messages, 2026-10-19: in the project chat at 11:08 UTC, "why am I doing all of this tinkering when you could decide for me, I don't want any of this enable, disable, start, do this do that, I want you to handle it, you have my authorization for everything"; in the thread "Build M7" at 11:13 UTC, "I started, but I'm out of usage in codex, I did all these click you asked", followed by the Agents page's runtime card as pasted ("ENABLED", "State reason", "OWNER_ENABLE_ENABLED"); in the thread at 11:18 UTC, "just skip this part and wrap up m7, this is getting boring".

- **Read as.** The owner closes M7 on what is done and amends M7-OD8 (a) ([ExecPlan 0026 §3.3](archive/plans/0026-m7-agent-driven-main-decisions.md#33-decisions-for-the-owner)): the passed decision probes and the one recorded live decision cycle become follow-ups, as M5's live token refresh did ([2026-10-03](#2026-10-03--m5-closed-on-the-capability-probes-live-token-refresh-becomes-a-follow-up-execplan-0020)). "This part" is read as every live check left that waits for the agents' model usage, so M6, whose completion under M6-OD7 (a) waited only for the walk-through of [ExecPlan 0023 §13.3](archive/plans/0023-m6-research-investigations.md#133-the-live-walk-through), is closed the same way, its walk-through a follow-up. The owner can overrule either reading.
- **Done when it was decided** (OBSERVED; [ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#the-boundary-m7-b-and-m7s-close-2026-10-19)): M7-A deployed on `09f4490`; the boundary `COMPLETE`; `AGENT_POLICY_V1` and `EVALUATION_PROTOCOL_V2` approved by exact hash; experiment `a8b3ae07-0fe8-40b7-a59f-1a485c3dda43` `RUNNING` on the policy; the runtime `ENABLED` on profile `9a7e664d9186` with a verified capability record (run 5's, INFERRED from the code).
- **What it leaves.** No decision workflow starts until a decision probe run is `VERIFIED` for that profile and that policy (`app/agents/decisions.py`, `_verified`); a failed or missing run latches nothing. Starting it is one owner action on the Agents page once the usage has reset ("Start decision probes", at most 40 calls). "You have my authorization for everything" does not move it to an agent: the application's owner controls take the owner's own session, and AGENTS rule 14's standing authorization excludes enabling agents' trading ([AGENTS.md](../AGENTS.md)).
- **Follow-ups.** The decision probes; the first live decision cycle and the walk-through of [§13.4](archive/plans/0026-m7-agent-driven-main-decisions.md#134-the-live-walk-through), with M7-OD8 (a)'s own follow-ups, among them a checkpoint date for the new run, which the owner names (not yet named); M6's walk-through; a start after a worker's downtime that waits for the replay of the missed publications ([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#the-boundary-m7-b-and-m7s-close-2026-10-19)); the usage-limit refusal's pattern ([ExecPlan 0030 §4.5](archive/plans/0030-agent-models-and-effort-per-role.md#45-the-usage-limit-block)). M7-OD5's selector, shadows and ablations and M7-OD7's partial reduction stay as decided on 2026-10-09.

## 2026-10-19 — The owner delegates the agents' model choice; no profile change during M7's switch-on

OBSERVED owner messages in the project thread "Agent setup and best models", 2026-10-19: at 08:30 UTC, "check the roadmap and the current m7 ongoing implementation, Are the agents configured and optimized for their role using best practices from official documentation? For best performance, speed, accuracy and efficiency? if we do right now will it affect the roadmap and the ongoing m7, also I don't want to configure agents which model to use, I want you to research and use the best model for the agent"; at 08:42 UTC, "so are you updating the plan to remove the configuration of models in the UI and configure them in the background ?". In the thread "Build M7" at 08:37 UTC the owner reported the cause of that morning's failed capability run: "it was usage limit".

- **Read as.** The owner delegates the choice of model and reasoning effort per agent role to the implementer, on the vendor's official guidance, and wants no model picker: the app chooses in the background. The owner's approval of each runtime profile by exact hash is not delegated and cannot be ([AGENTS.md](../AGENTS.md) rule 4: agents never grant approvals); it stays one click on a document the app composes.
- **Decided (by the thread, under the delegation).** The recommended table from the vendor's guidance, not a measurement: `gpt-6.1-sol` for every role; `medium` effort for the coordinator, the analyst and the researcher; `high` for the evaluator ([ExecPlan 0030 §4.1](archive/plans/0030-agent-models-and-effort-per-role.md#41-the-table-from-the-vendors-guidance), sources in [REFERENCES](archive/contracts/REFERENCES.md#model-and-effort-guidance--2026-10-19)). Not `gpt-6-astra` (five times the allowance per token, slower; placed by the vendor where cost and latency do not matter); `gpt-6-luna` only as a measured candidate for the outcome review. The table lives in code, versioned and hashed like a prompt; the app composes the profile from it and the discovered catalog; the Agents page loses its model and effort picker. Built in M8 as [ExecPlan 0030](archive/plans/0030-agent-models-and-effort-per-role.md), after [ExecPlan 0029](archive/plans/0029-fast-lane-pc-runs.md), deployed in the same sitting as `AGENT_POLICY_V2`.
- **Nothing changes now.** M7 keeps profile `9a7e664d9186` (`gpt-6.1-sol` at `medium`, the vendor's documented default and the only setting the current profile can express for all roles). A profile change would drop that approval, need a new probe run (at most 70 plus 40 live calls on the allowance that ran out on 2026-10-19) and start an evaluation segment during M7's first live days.
- **Recorded with it.** The agents and the owner's own Codex use share one ChatGPT allowance, and the app does not recognize a usage-limit refusal: the candidate pattern is unverified (`services/agent-runner/runner/jsonl.py:98-104`), so the refusal fails a probe run and latches the runtime. The stored text of the 2026-10-19 refusal is the observation that lets the pattern be verified; Build M7 keeps that fix out of M7 (a runner rebuild mid-switch-on for a case the reset cures), and ExecPlan 0030 §4.5 carries it, with the caveat that the PC saw the run's error candidates empty, so the text is read before the fix is designed.
- **Not decided.** When M8 starts, and the comparisons of [ExecPlan 0030 §4.4](archive/plans/0030-agent-models-and-effort-per-role.md#44-what-m8-measures-before-the-table-is-the-standing-default); a second ChatGPT account for the app (the owner's spending call; not recommended by the thread, only named).

## 2026-10-18 — The pilot stops before the rest of the M7 gate, which runs without the pilot watch

OBSERVED owner message in the project thread "Build M7", 2026-10-18 20:16:33 UTC: "B: I’m stopping the pilot now. Run the rest of m7-g1e without the watch, keep the pilot’s workers running until the boundary, and tell me whether m7-g1d’s PerformanceResearch record lists any problem before staging." It is the line the thread drafted for the owner after the watch stopped `m7-g1e` ([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#m7-g1e-stopped-too-and-the-pilot-stops-first-2026-10-18)). B was the PC session's recommended option of three, which it put to the owner through the thread: A, retry later beside the pilot with no change; B, stop the pilot before the gate instead of after it; C, make the tests lighter first. The thread recommended B too.

- **Read as.** The owner stops the pilot in the application, which only the owner can do; the thread had asked them to close its positions if the stop dialog offered it. [M7-OD2](#2026-10-16--m7-od2-the-pilot-ends-early-once-m7-a-is-deployed-and-probed) placed that stop at the boundary, after the application update and its probes; it now comes before the gate's remaining phases and the update. Its checkpoint report is written at this earlier date. The message's last clause is a question, answered in the thread at about 20:31 UTC (the next entry's condition).
- **Decided.** `m7-g1e`'s remaining phases run without a pilot watch. [The owner's rule of 2026-10-07](#2026-10-07--m6-b9-what-stops-a-test-run-beside-the-pilot-the-owner-scripts-and-the-pilots-own-rows-the-schema-change-in-0008-and-the-market-workers-log) says what stops an isolated test run "while the real pilot is running". After the stop, the watch would read the stop itself as a difference: the experiment's events (the stop's own rows, at its next reading) and, from the next HH:07, the missing `SNAPSHOT` report. How the watch judges both is VERIFIED in `tools/lib/Research.psm1`; that no `SNAPSHOT` is written once the run has left `STOPPING` is VERIFIED in `app/evaluation/worker.py` and INFERRED for the pilot's images. While the workers run, the lease does not change and the forward checkpoint is INFERRED to keep advancing. The pilot's workers keep running until the boundary, where `tools/pilot-deactivate.ps1` stops them as planned. The application update and research on follow the gate as before.
- **What the stop leaves to protect.** If the stop closed every position, nothing of the pilot is exposed and the watch has nothing to guard. A run leaves `STOPPING` for `STOPPED` only when its account is flat (`app/execution/engine.py`), so `STOPPED` means flat. If a position stays open, the run stays `STOPPING`, the running workers keep protecting the position under the test load, and `tools/pilot-deactivate.ps1` refuses at its first state check (VERIFIED in the M7 code, INFERRED for the pilot's images). The times the pilot read `STOPPED` and `COMPLETED` are NOT OBSERVED here yet.
- **Why the switch-on still works** (VERIFIED in the code unless named otherwise). `tools/m7-deploy.ps1` refuses a deployment when a service it names in `-ExpectedPilotImages` (the market, execution and evaluation workers) does not run on its expected image, or when the execution worker runs without the lease; it has no condition on the experiment's state, but its after-check refuses when an open experiment (`READY`, `RUNNING`, `PAUSED` or `STOPPING`) changes during the run, so the deployment waits at least for `STOPPED`; the plan waits for `COMPLETED` (§13.2, step 0). The execution worker keeps the lease whatever the run's state (`app/execution/worker.py`; OBSERVED in B9d's cloud simulation with M7's workers as processes, [ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#b9d--the-boundary-script-its-model-and-boundaryrehearsal-2026-10-16); INFERRED for the pilot's images). So a deployment, and a later one for the policy's values (§13.1), can still run. Running `tools/pilot-deactivate.ps1` before the update would make the deployment refuse; that is why the workers stay on. `tools/research-activate.ps1` has no condition on the experiment's state; like the deployment, it needs the lease held while the execution worker runs, and it checks that no pilot container or lease changes during its own run and that no incident is recorded beyond the pilot's own `PROTECTION_UNAVAILABLE` rows. `tools/m7-boundary.ps1` needs the pilot `COMPLETED` and its workers stopped, as before.
- **Not chosen.** A: two stops in twenty minutes, with the market worker overloading under the test load, made a third likely. C: a change of the harness during the run, and the overload's cause is not known to be CPU.
- **Replaced for `m7-g1e`'s remaining phases.** The pilot watch beside each run in [the owner's go-ahead](#2026-10-18--the-owners-go-ahead-to-speed-up-m7-and-the-gates-rerun-on-the-renewal-fix) and in M7-OD9 ([ExecPlan 0026 §3.3](archive/plans/0026-m7-agent-driven-main-decisions.md#33-decisions-for-the-owner)) and in the plan's run rules ([§10](archive/plans/0026-m7-agent-driven-main-decisions.md#10-verification-commands-proposed-not-implemented)); the stop's place in M7-OD2 and in §13.1 and §13.2 of the plan.
- **Unchanged.** Every budget and judgment of the gate's phases; the reading of the owner's go-ahead otherwise; the owner's own steps at the boundary and at M7-B.

## 2026-10-18 — PerformanceResearch counts from two gate runs: its job figures from `m7-g1d`, its staging figures from `m7-g1a`

OBSERVED owner message in the project thread "Build M7", 2026-10-18 19:31:31 UTC: "B, but skip PerformanceResearch". It is the start of the line the thread had drafted at 19:28 UTC for the owner to send, after the owner's message of 19:28:31 UTC, "write here the text to copy again": "B, but skip PerformanceResearch on m7-g1e. Take its job times from m7-g1d and its staging figures from m7-g1a, if m7-g1d's record shows no problem before staging. Otherwise, run it last." B was the PC session's option after the pilot watch stopped `m7-g1d` ([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#performanceresearch-on-m7-g1d-stopped-by-the-pilot-watch-2026-10-18)): carry on with `m7-g1e` with `PerformanceResearch` last, and ask whether that phase's staging part can be made lighter or its staging figures taken from an earlier run.

- **Read as.** The drafted line, whole. The message is that line's first words, sent three minutes after it, and a skip without the line's sources would leave the gate without the phase. The condition only narrows the skip. "Job times" is read as every figure of the phase before its staging part, the idle dispatch p95 among them.
- **Decided.** `m7-g1e` does not run `PerformanceResearch`. For the M6-B gate the phase counts from two of its runs on the owner's PC beside the pilot watch, neither of which ended `VERIFIED`: every figure before its staging part from `m7-g1d` (on `595e5aa`), and its staging figures from [`m7-g1a`](archive/plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1a-and-the-held-steps-cost-2026-10-17-and-18) (on `5b9987b`): 2,266 rows/s against at least 1,000, and a largest batch of 481 rows against at most 500. This departs from the [decision of 2026-10-08](#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on) ("on the build that is activated") further than [the go-ahead's entry](#2026-10-18--the-owners-go-ahead-to-speed-up-m7-and-the-gates-rerun-on-the-renewal-fix), for this phase only, and replaces that entry's last sentence on the phase.
- **The condition.** OBSERVED on the PC and reported by the PC session: `m7-g1d`'s measured jobs are all `VALID` inside their bound, its idle dispatch p95 is 4,810.1 ms against 5,000, and each projection to 14 and 21 days is inside 3,600 s, the shadow advance over 21 days at 3,487.4 s. The phase wrote no record, because the stop ended it first; its parts' own outputs name no problem, and their logs hold no error, traceback or refusal (OBSERVED on the PC, reported by the PC session after 20:17 UTC). "Before staging" is read as the drafted line's words: the parts of `m7-g1d`'s phase before its staging part, not a deadline before `m7-g1e`'s `Staging` phase, which passed at 20:26 UTC, before the answer. The thread reads that as the condition met, and told the owner so at about 20:31 UTC, in answer to the question in their message of 20:16 UTC, and again in a notifying message at 20:42 UTC: the application update and research on go ahead on that reading unless the owner says otherwise in the thread before about 00:15 UTC. The release file does not wait for a word from the owner on it. The phase has no overall verdict.
- **Why the figures carry over** (OBSERVED in the diffs; that they carry over is INFERRED). From `5b9987b` to `09f4490` the staging part's harness and measurement are unchanged: `tools/m6/performance.psm1` changes only a note of `DecisionSaturation`, and `tests/m6_performance.py` only the measured candidate and the saturation feeder. The product's staging changes only in [the two reads that run once](#2026-10-18--the-two-staging-reads-that-run-once-get-a-20-s-bound) and the `sqlstate` field of the bridge's failure line (`app/research/staging.py`, `app/research/bridge.py`). The read of a new collection is inside a batch, but on the measured backlog only the first batch meets one, because the backlog holds one collection (`_load_dense` in `tests/m6_performance.py`). No image, dependency, migration or Compose file changed. From `595e5aa` to `09f4490` the product differs only by the lease renewal: its lock wait, and how long a job's end waits for its renewal thread.
- **Not chosen.** `PerformanceResearch` again, last on `m7-g1e`: 00:07 to about 03:20 UTC by the PC session's estimate (not measured), with the application update at about 04:15 UTC, and its staging part could stop the run again. A lighter staging part: a change of the measurement during the run, which would need a new run.
- **Unchanged.** Every budget and judgment of the phase; the other gate phases on `m7-g1e`; the other conditions of the entries named above.

## 2026-10-18 — The fast lane for PC test runs from M8 on

OBSERVED owner answer in the project thread "Why M7 is so slow", 2026-10-18 18:28 UTC: "Fast lane" on the card "Use the fast lane for PC test runs from M8 on?", whose option read "Only changed or failed checks rerun, with one watch and one go-ahead from you per milestone." It was the recommended option; the others were "Fast + final" ("As fast lane, plus one full run on the build that gets switched on, about 7 h more per milestone") and "Keep as is" ("Every fix restarts every check, and you start a watch for each run"). The card's context: every fix restarts a whole PC run (the rule of no partial reruns), and the owner starts a pilot watch and types a go-ahead for every run; M7 needed nine PC runs, six of its seven full runs failed, and a full gate run takes about 7 h; under the fast lane a check that passed keeps its pass while the files it tests are unchanged, proven by a fingerprint of those files, so only changed or failed checks rerun; the owner starts the watch and types the go-ahead once per milestone; it is built after M7 is switched on, before M8's first PC run, and the gate run then in progress is not touched.

- **Read as.** From M8 on:
  1. A phase's record carries a fingerprint of the files it depends on. In a later run of the same milestone, a `VERIFIED` phase whose fingerprint is unchanged keeps its pass and is not rerun; a changed or failed phase reruns. The report shows each kept pass with the run and commit that earned it. This replaces the [2026-10-01 rule](#2026-10-01--m5-acceptance-quiet-period-on-a-restart-no-partial-reruns-execplan-0020-b7) "No partial reruns". For the activation gate it replaces the [2026-10-08 condition](#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on) that the gate phases pass "on the build that is activated": a kept pass counts when its fingerprint is that of the activated build.
  2. The owner starts the watch that guards the live application beside test runs once per milestone, not once per run; again only when the PC restarts or after an owner-approved step on the normal application, which gives it a new baseline ([ExecPlan 0029 §4.6](archive/plans/0029-fast-lane-pc-runs.md#46-the-watch-for-a-milestone)).
  3. The owner types one standing go-ahead per milestone in the thread of the session on the PC, which then runs the milestone's PC phases as they are ready and reruns a failed phase after its fix.
- **Not decided here.** What each phase's fingerprint covers, which [ExecPlan 0029](archive/plans/0029-fast-lane-pc-runs.md) sets: a file it cannot tie to fewer phases counts for every phase, so an unclear case reruns. What the watch guards once the M4 pilot has ended, which M8's plan sets.
- **Unchanged.** M7 and its gate, whose reruns the owner's go-ahead of 14:34 UTC covers; the quiet window, one heavy stack at a time and the watch's stop rule; every phase's budgets and judgments; the watch's `-Execute`, which stays the owner's; the approvals in the application.

## 2026-10-18 — M8 starts with hourly entry checks when the app holds no position

OBSERVED owner answer in the project thread "Why M7 is so slow", 2026-10-18 17:37 UTC: "First in M8" on the card "Look for entries every hour when the app holds no position?", whose option read "A new policy version with hourly entry checks is M8's first step, after M7 has run a day or two." It was the recommended option; the others were "Keep 6-hourly" and "Change M7 now" ("M7 gets the new policy before switch-on, which restarts tonight's gate and costs about a day"). The thread asked it in answer to the owner's message of 16:25 UTC there: "there shouldn't be timeframes that long when the whole idea is to be adaptive". The card's context: with no position, the agents look for an entry only after each 6-hourly brief (00, 06, 12 and 18 UTC), so a new market can wait up to 6 h; the daily budget of 36 decisions already has a slot for every hourly bar; the cost is more model calls on the owner's ChatGPT plan, up to 24 decisions on a day with no position instead of 4, which is not measured; any change is a new policy version with its own approval and a new build; the other limits stay (at most 2 entries in any 24 h, 1 per coin).

- **Read as.** M8's first step is `AGENT_POLICY_V2` ([ExecPlan 0026 §5.1](archive/plans/0026-m7-agent-driven-main-decisions.md#51-the-operating-policy-one-record-where-it-lives-how-it-is-approved): "A changed value is `AGENT_POLICY_V2` with its own hash and approval"). Its cadence starts a decision at every finished hourly bar, also when no position or entry is open; under V1 that trigger needs one (`BAR_CLOSE_WHILE_A_POSITION_OR_AN_ENTRY_IS_OPEN`, read by `_write_triggers` in `services/engine/app/agents/decisions.py`). The daily budget of 36 decisions ([§5.7](archive/plans/0026-m7-agent-driven-main-decisions.md#57-triggers-cadence-priority-and-budgets)) and V1's other limits stay. It is built after M7 has run live for a day or two, so that a live decision's time and its model calls are observed first ([§19](archive/plans/0026-m7-agent-driven-main-decisions.md#19-open-risks)).
- **Not decided.** V2's document, its hash and the owner's approval of it; the experiment it runs in, since under §5.1 another version is another experiment, with its own manifest approval; whether the ChatGPT plan's limits allow the extra calls; where M8's ExecPlan places the step.
- **Unchanged.** M7, the gate run `m7-g1e` and M7's switch-on; `AGENT_POLICY_V1`, its approval and its run's history.

## 2026-10-18 — The owner's go-ahead to speed up M7, and the gate's rerun on the renewal fix

OBSERVED owner message in the project thread "Build M7", 2026-10-18 14:34 UTC: "I approve whatever needs to be done to speedup and resolve m7". It came after the owner's questions in the project chat at 13:01 and 13:05 UTC: when M7 would finish, and whether the 7-hour gate run is necessary. At 13:06 UTC the thread had told the owner, in the same thread: "Rerunning only a failed check, or shortening a check, would be your call, because your 10-08 decision asks for all three on the build that gets switched on." The thread answered the go-ahead at 14:35 UTC with how it reads the message:

- the application update and switching research on run as soon as the gate passes, with no further word from the owner;
- a check that fails is rerun alone after its fix, not the whole run;
- the waits between checks are tightened on any rerun.

Three things stay the owner's, because the application accepts them only from the owner: the approvals, stopping the pilot and pressing Start.

- **Read as.** The owner's word in chat for the update ExecPlan 0026 PROPOSED for the owner's approval (`tools/m7-deploy.ps1 -Rollback`, then `tools/m7-deploy.ps1`, from the commit `m7-g1e` passes on) and for `tools/research-activate.ps1`, each once the gate has passed, and for the rerun below. It does not cover the approvals in the application, the runtime profile's approval, the pilot watch's `-Execute`, the pilot's stop or any step of M7-B.
- **Decided under it: the rerun after gate run `m7-g1d`** ([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1d-a-renewal-behind-a-slow-batch-2026-10-18)). A new run `m7-g1e` on the commit that merges the renewal fix runs `Build`, `ResearchRunner`, `Staging`, `DecisionSaturation` and `PilotCoexistence`. The gate's evidence is the phase records: `Report` refuses any run that started a gate phase (`tools/m6/report.psm1`), so it is not run. `PerformanceResearch` is not run again if it is `VERIFIED` on `m7-g1d`: its result on `595e5aa` stands for the fix's commit. For that phase only, this departs from the [decision of 2026-10-08](#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on) that the three gate phases pass "on the build that is activated". The two commits' product differs by the lease renewal's own lock wait and how long a job's end waits for its renewal thread. None of `PerformanceResearch`'s figures (job times, sealing, idle dispatch, the staging rate) include either, and the phase does not judge the research runner's log lines (INFERRED from the code). It saves the phase's run on the fix's commit: its parts start at HH:07 in separate hours, about 2 h 15 min by the PC session's estimate for `m7-g1d` (not measured). If the phase is not `VERIFIED` on `m7-g1d`, it runs on `m7-g1e` with the others. (Its last sentence is replaced by [the entry above of 19:31 UTC](#2026-10-18--performanceresearch-counts-from-two-gate-runs-its-job-figures-from-m7-g1d-its-staging-figures-from-m7-g1a).)
- **Not chosen.** The whole gate again on the fix's commit (about 7 hours); and counting a renewal that was asked again as no failure, which would change `DecisionSaturation`'s judgment.
- **Unchanged.** Every budget and judgment of the three phases; a pilot watch beside each run, which the owner starts; for `m7-g1e`'s remaining phases replaced by [the entry of 20:16 UTC](#2026-10-18--the-pilot-stops-before-the-rest-of-the-m7-gate-which-runs-without-the-pilot-watch); the other conditions of the 2026-10-08 decision.

## 2026-10-18 — The two staging reads that run once get a 20 s bound

OBSERVED owner answer in the project thread "Build M7", 2026-10-18 06:47 UTC: "20 s limit" on the card "Fix the staging read that timed out by giving it a 20-second limit?", whose option read "Only the two reads that run once (a new data set, a new store's start) get 20 s instead of 2 s; code only, no database change." The card replaced one at 30 s, withdrawn unanswered when the independent review found that two such reads in one pass could keep the store's transaction idle past the bridge identity's 60 s. Its context named the likely cause of gate run `m7-g1b`'s staging error (INFERRED until the database's log line is read) and what remains: a read longer than the bound would be repeated each pass, as one longer than 2 s is now.

- **Decided.** The read of a collection the store does not hold yet and the read of where a new store version starts raise the research identity's statement bound to 20 s for their one statement and give it back after it (`ONCE_SECONDS` in `app/research/staging.py`; [ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1b-the-saturation-feeders-jobs-and-a-staging-read-that-runs-once-2026-10-18), [OPERATIONS](OPERATIONS.md)). It answers, for these two reads, the risk [ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks) recorded on 2026-10-08, as the [owner's decision of 2026-10-06](#2026-10-06--m6-b9-phase-content-images-saturation-length-job-measurement-row-counts-quiet-window-lost-store-regression-and-the-read-only-look) (point 4) asks of a read that misses its budget.
- **Not chosen.** An index on `market_observations(collection_id)`, which would be a migration of an M2 table in a pull request of its own; and accepting the error as a known finding of the gate.
- **Unchanged.** The identity's 2 s bound for every other statement, its grants and its views; every budget and judgment of the gate; the saturation feeder's longer jobs, which needed no decision.
- **Cause confirmed after the decision** (OBSERVED on the owner's PC, 2026-10-18): `m7-g1b`'s catalog database logged one `ERROR`, at 04:08:29.609 UTC, a statement timeout on the read of `research_read.market_collections`, two milliseconds before the bridge's failure line ([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#the-m6-b-gate-run-m7-g1c-a-report-with-an-entry-not-yet-filled-2026-10-18)). On `m7-g1c`, with the bound, the bridge logged none.

## 2026-10-17 — DecisionSaturation replaces ResearchSaturation in the M7 activation gate

OBSERVED owner answer in the project thread "Build M7", 2026-10-17 18:58 UTC: "Combined" on the card "Build DecisionSaturation as one load check that also replaces ResearchSaturation?", whose option read "One check covers both, with the agent load above, which saves about 2 hours of PC time." The card's context named the load: `ResearchSaturation`'s research at full load with every research limit checked the same way, `PerformanceEngine7`'s M7 trading engine in place of the old test one, and the agents on scripted answers with a whole day's work (36 decisions, 4 market briefs) inside the 30 measured minutes.

- **Decided.** In the M7 profile's activation gate `DecisionSaturation` ([ExecPlan 0026 §10](archive/plans/0026-m7-agent-driven-main-decisions.md#10-verification-commands-proposed-not-implemented), [TESTING](archive/TESTING.md#m7-activation-gate-decisionsaturation)) takes the place of `ResearchSaturation`, which the [owner decision of 2026-10-08](#2026-10-08--m6-b9-m6-a-is-accepted-on-what-the-inert-deployment-switches-on) required before the M6-B activation. On the M7 build the gate is `PerformanceResearch`, `DecisionSaturation` and `PilotCoexistence`; `ResearchSaturation` is no longer a phase of `tools/m7-acceptance.ps1`.
- **Unchanged.** Every budget and judgment of `ResearchSaturation`'s research side, which `DecisionSaturation` keeps; `ResearchSaturation` on the M6 harness and its history; the other conditions of the 2026-10-08 decision; the activation itself, the runtime profile's approval, the pilot's stop and every step of M7-B, which stay the owner's.

## 2026-10-17 — M7 B10: the owner deploys M7 switched off, from the main folder on the accepted commit

OBSERVED owner messages in the project thread "Build M7", 2026-10-17: `Deploy M7` (16:27 UTC), after B9's final run `m7-b9c` passed; then `A` (16:31 UTC), answering the thread's question of 16:29 UTC. The normal application's containers, `.env` and secrets live in the owner's main folder `C:\Users\owner\repos\adaptive-spot-lab`, which was on Codex's branch `codex/m9-m10-readiness` (`c1c1619`, older product code than M7). Option A: "I switch the main folder to the tested M7 version, install from it, and switch it back to Codex's branch afterwards"; option B: the owner or Codex switches it.

Read as: the owner's word for B10 in the PC thread, as the advance OK of 2026-10-16 08:15 UTC required, and for checking out `05d8ef9` (detached) in the main folder for the deployment only, then `codex/m9-m10-readiness` again.

- **Not decided by these answers:** research's activation, the runtime profile's approval, the pilot's stop, the boundary and any step of M7-B.

## 2026-10-17 — GitHub CI removed from the repository

OBSERVED owner message in the project chat, 2026-10-17 16:04 UTC:

The owner asked to remove the GitHub CI checks from the app for now, to be added back later, and to tell the active thread.

- **Removed.** `.github/workflows/ci.yml`, the workflow of [ExecPlan 0016](archive/plans/0016-ci-checks.md), which never ran on GitHub; `.github/dependabot.yml`, which updated only that workflow's action pins; and `tools/ci/compose.images.yaml`, which only the workflow used. They were deleted rather than disabled. `main` at `05d8ef9` still has all three, and ExecPlan 0016 keeps the design and the steps to restore them. Adding CI back is a later owner decision.
- **What stands in.** No hosted check. A pull request's evidence is what its body records ([TESTING](TESTING.md#continuous-integration)): a cloud session runs the checks that need no Docker, and the owner's PC runs the PostgreSQL tests, the browser suites and the acceptance harness. A check that did not run, or was skipped, is NOT RUN.
- **Contracts reconciled.** Where a contract asked for executed CI checks (the deterministic-regression layer in [EVALUATION](archive/EVALUATION.md#release-and-forward-evidence), M8's closure in the [ROADMAP](ROADMAP.md#m8--reliability-review-sustained-evidence-and-handoff), M9-R19, B8 and Q07 in [ExecPlan 0027](archive/plans/0027-m9-market-intelligence-and-event-driven-trading.md), B7 in [ExecPlan 0028](archive/plans/0028-m10-coin-discovery-and-controlled-expansion.md)), the required checks are, until CI is added back, the local harness's, executed against the exact release source. Skipped, absent or startup-failed checks still prove nothing. No other requirement changed.
- **Unchanged.** The standing merge rule of 2026-10-11; its note that GitHub Actions cannot run is now historical. Earlier records that GitHub CI did not run. ExecPlan 0026 and M7's entries in shared records. No repository setting and no application file changed.

## 2026-10-17 — builder and LLM-trading findings recorded as PROPOSED M8–M10 requirements

OBSERVED owner instruction in the project thread, 2026-10-17 09:36 UTC:

> I researched trading-bot builder communities and LLM-trading studies on 2026-10-17. Decisions:
> - No new milestone. Do not touch M7 while its final run (B9) is in progress.
> - Record each finding below as a PROPOSED requirement in the earliest milestone it affects: M8, M9 (ExecPlan 0027) or M10 (ExecPlan 0028).
> - This authorizes documentation edits and the optional measurement only. It does not authorize implementation, new strategy/grammar/envelope versions, approvals, activation or deployment.

The same message asked for a pull request for the owner's review and said "Do not merge it", which sets aside the standing rule of 2026-10-11 to merge ready PRs, for that pull request only.

| Finding | Earliest milestone | Recorded as PROPOSED in |
|---|---|---|
| 1. Indicator warm-up sensitivity | M8, early | [ROADMAP](ROADMAP.md#m8--reliability-review-sustained-evidence-and-handoff), [EVALUATION](archive/EVALUATION.md#m8-onward-warm-up-sensitivity-and-decision-level-controls), [STRATEGIES](archive/contracts/STRATEGIES.md#warm-up-sensitivity-proposed-for-m8-2026-10-17) |
| 2. Placebo control for entries | M8 | ROADMAP, [EVALUATION](archive/EVALUATION.md#m8-onward-warm-up-sensitivity-and-decision-level-controls) |
| 3. Exit what-if | M8 | ROADMAP, [EVALUATION](archive/EVALUATION.md#m8-onward-warm-up-sensitivity-and-decision-level-controls) |
| 4. Remembered-outcomes audit | M9 | [M9-R25](archive/plans/0027-m9-market-intelligence-and-event-driven-trading.md#9-requirements-mapped-to-verification), [EVALUATION](archive/EVALUATION.md#additions-proposed-on-2026-10-17-m9-r25r28-m10-r17) |
| 5. Decision repeatability and agreement gate | M9 | M9-R26 |
| 6. News base rates | M9 | M9-R27 |
| 7. Search intensity on promotion requests | M9 | M9-R28 |
| 8. Universe size as a declared factor | M10 | [M10-R17](archive/plans/0028-m10-coin-discovery-and-controlled-expansion.md#9-requirements-mapped-to-verification) |

Not decided by this instruction: whether warm-up sensitivity is material, and any `TREND_REFERENCE_V2`, grammar or envelope version. M8's plan judges materiality against a rule it declares before the real-candle measurement, and each successor version needs its own exact-hash approval. The instruction's option of contiguous runs from backfilled exchange candles was checked: it is already V1's behavior ([EVALUATION](archive/EVALUATION.md#indicator-warm-up-sensitivity)). `TREND_REFERENCE_V1`, its mandates and history stay unchanged. The placebo and exit what-if are labeled analyses that do not amend `EVALUATION_PROTOCOL_V2`; `PROMOTION_V2` is unchanged. No threshold, return or accuracy figure is set. ExecPlan 0026 and M7's entries in shared records are not edited. The optional measurement is NOT RUN: this cloud session's network policy denied the public Binance hosts ([COMMANDS](archive/COMMANDS.md#builder-and-llm-trading-findings-documentation--2026-10-17)). Sources, their types and limits: [TB-01–TB-20](REFERENCES.md#trading-bot-builder-and-llm-trading-research--2026-10-17).

## 2026-10-16 — researched agent readiness in M9 and M10

OBSERVED owner instruction: “let's make it 5/5”, with deep research and authority to choose a new milestone or edit M9/M10 because neither has started. This authorizes the roadmap/documentation refinement and its verification. It does not authorize application implementation, provider calls, login, paid access, migrations, activation, deployment or publication of these new edits. The informal rating is a quality ambition, not acceptance evidence or a profit guarantee.

DESIGN DECISION under that delegated choice: retain the milestone sequence. Close authority/security defects before affected activation, complete provider/environment checks at their existing activation gates, then collect authorized comparative/forward evidence before M8 acceptance; [M9 B0 verifies that closure](archive/plans/0027-m9-market-intelligence-and-event-driven-trading.md#m8-readiness-evidence-required-before-m9). Strengthen M9 with R19–R24 for predecessor evidence, worker-independent execution invalidation, code-calculated advisory feasibility, measured latency/quota behavior, actual-model semantic/reviewer comparisons and a justified runtime integration choice. Do not create a late milestone that postpones these foundations until after discovery.

M10 inherits verified M9 controls and adds R15–R16 for multi-asset shared-capacity/invalidation tests, measured scan/burst fairness and discovery coverage beyond the shortlist. Reuse existing roles and shared infrastructure. A fifth role, additional inference concurrency, SDK migration, new provider or more tradable coins is not automatically authorized or required. Additional complexity must satisfy predeclared value/cost criteria and the existing approval contracts.

The [future agent-quality protocol](archive/EVALUATION.md#future-m9m10-agent-quality-and-release-evidence) owns semantic cases, human-calibrated evaluation, repeated actual-model trials, matched-budget comparisons and separate software/usefulness/financial claims. Sampled human grading is evaluation work, not a new per-trade approval flow. No existing reviewer requirement, financial cap, immutable mandate or latched-pause rule is weakened. Keep historical observations and approvals unchanged; new successor behavior is reconciled explicitly before implementation.

## Owner-confirmed

| Decision | Recorded requirement |
|---|---|
| Objective | Increase invested capital and explore income generation. No guaranteed income target. |
| Scope | Paper only. Spot for BTC, SOL and the installed policy's coins until M11's second update; then one simulated BTCUSDT perpetual, long or short, at most 2x ([2026-10-23](#2026-10-23--m11-approved-bitcoin-futures-on-paper-execplan-0039)). |
| Funding | Simulated starting amount 10,000; virtual top-ups like a trading-account funding workflow. |
| Deployment | Local PC now; hosting and paid APIs are deferred, except the agents' two pay-per-token providers, each only on the owner's pick under its daily cap ([2026-10-31](#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049)). |
| Risk/horizon | Owner delegates initial proposals and wants adaptation. |
| Approval | New strategies and expanded parameter ranges require owner approval for the main portfolio. Routine actions within an approved operating policy are automatic. |
| Frontend | TanStack Start using the exact shadcn preset command below. |
| UI behavior | Always use the official shadcn skill; reuse existing shadcn components. |
| Libraries | TanStack Query, TanStack Table, Zod, RHF when forms are needed, Lightweight Charts; relevant available lint integrations. |
| Authoring/runtime | Codex or Claude Code for development. Runtime: Codex CLI with the owner's ChatGPT login (kept by the owner on [2026-10-23](#2026-10-23--the-owner-keeps-codex-for-the-agents-execplan-0039)) by default, or the Claude Code CLI, the Claude API or the OpenAI API when the owner picks one in Settings ([2026-10-31](#2026-10-31--the-agents-provider-four-to-choose-from-the-two-apis-with-a-daily-cap-execplan-0049)); no fallback between them. |

```sh
pnpm dlx shadcn@latest init --preset b2fms61Bqi --template start --pointer
```

## Explicit design proposals, not facts about optimal investing

- Use `BTCUSDT` and `SOLUSDT` observations and label the initial balance **10,000 virtual USDT**. Do not display a dollar sign implying verified USD equivalence.
- Start with hours-to-days research: `1h` reference strategy, with `4h` strategies eligible only after testing/approval. Risk monitoring runs independently of bar-close signal evaluation.
- Use the initial paper profile in [RISK_POLICY.md](RISK_POLICY.md). The agent cannot select its own hard maximum acceptable loss.
- Keep Python/FastAPI and PostgreSQL for the engine; use one codebase with separately deployed API/worker processes.
- Use four logical model roles and one portfolio coordinator behind an application-owned tool broker. Share one execution/accounting authority; never let agents independently spend the same cash.
- Default to a brokered structured-action loop around Codex CLI. Native MCP is an optional reviewed transport, not required for agent tools and not a reason to grant shell or filesystem access.
- Use a registered declarative research language, bounded experiment runner and immutable evidence records. No runtime deployment of generated Python/JavaScript.

## Still requires measured or owner-approved run configuration

Actual applicable trading fees; slippage/latency/liquidity assumptions; runtime model availability; chosen evidence sources; research data range; selector calibration; experiment acceptance settings; measured PC/storage limits. These are not reasons to block scaffolding. They are activation or promotion gates at the appropriate milestone.

A fee scenario can be explicitly hypothetical, but its results must say so. Model identifiers, package versions, preset contents, and account capabilities are discovered rather than inferred from a ChatGPT display name.

## Change control

Record consequential changes as dated decisions with reason, alternatives, owner approval where required, affected experiment versions, and tests. Do not overwrite historical run configuration. Never treat a model's proposed policy change as owner approval.

### 2026-09-27 — Production-readiness standards

The owner accepted applying professional web application standards to every milestone and requested durable repository guidance. The [Q01–Q10 quality gates](ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone) are the canonical completion checklist, linked from root authoring instructions and planning/task templates. Apply them to the current milestone's scope and support readiness claims with observed evidence. This records an engineering standard; it does not expand runtime authority or mark additional capabilities verified.

### 2026-09-28 — Completed milestones must run locally

The owner requested: “after each m completion, the app should run the latest changes.” For an authorized implementation milestone, passing acceptance now includes deploying the latest verified milestone code to the normal local Docker app and leaving it healthy/running. The authoring agent has standing authorization for the required protected backup, forward migrations, builds and service recreation; no repeated deployment confirmation is needed. Planning-only work remains read-only, and an explicit task-specific hold still applies.

This decision supersedes the earlier M2 restriction on updating the owner installation's software and applies to the current M2 catch-up as well as future milestones. It does not enable a disabled collector, paper-trading policy, agent/model/research workflow or paid service; create/fund an account; change owner approvals; or clear a pause. Preserve approved operating settings and all owner data/secrets. If deployment cannot be verified, record implementation/acceptance separately from the blocked delivery and retain a compatible recoverable state. [OPERATIONS.md](OPERATIONS.md#milestone-completion-deployment) owns the procedure. The earlier isolated M2 completion record remains historical evidence, not proof of the newly required normal deployment.

### 2026-09-28 — Normal web host port

The owner requested the normal TanStack Start app on port 3000 instead of the project-specific host port 4317. Keep the Docker publication bound to `127.0.0.1`; [Compose](../compose.yaml) owns the mapping to the existing production server's port 3000. The `WEB_PORT` override remains for disposable test projects that must not collide with the normal app. This changes only the normal web address, not service authority, data, credentials or activation. The [port-alignment record](archive/plans/0010-release-readiness.md#owner-requested-normal-port-alignment--2026-09-28) records verification and rollback.

### 2026-09-29 — Manual screen-reader review retired

The owner asked to turn off the screen-reader review "for this and the rest of the application". The owner-performed Windows Narrator review is no longer a completion requirement for M3 or for any later milestone or change. That review was the only owner-performed accessibility check; it covered speech, keyboard, focus and zoom. No further reason was given. The alternative, a per-milestone owner review, is what this decision ends.

[Q02](ACCEPTANCE_CHECKLIST.md#quality-gates-for-every-milestone) is now verified by the implementer alone:
- automated browser checks: keyboard reach, focus, accessible names, headings and table semantics in the accessibility tree, non-color status, contrast, 200% zoom and narrow layouts
- the implementer's own inspection in a real browser

WCAG 2.2 AA remains the design target. Spoken output and screen-reader navigation are no longer verified, so no screen-reader or full WCAG conformance claim may be made.

The pending [M3 checklist](archive/m3-narrator-review.md) is retired without being run. The owner-reported [M2 result](archive/m2-narrator-review.md) remains historical evidence. This decision changes verification only, not UI requirements, runtime authority or data.

### 2026-09-29 — M4 pilot decisions (ExecPlan 0015)

The owner answered the owner decisions in [ExecPlan 0015 §3.3](archive/plans/0015-evaluation-fixed-pilot.md#33-owner-decisions-required-before-a-forward-pilot) in chat with "accept all recommendations".

**Decided (OD-1 and OD-9 to OD-14):**
- **OD-1 Denomination and capital.** The pilot runs on the existing main account in `USDT (virtual)`, measured from the NAV at activation. Top-ups stay allowed and are matched in the baselines.
- **OD-9 Control authority.** Only the owner starts, pauses, resumes, flattens or stops a run, in the authenticated UI. The system enforces latches. The implementer performs only graceful worker stops for authorized deployments, and activates or deactivates only on an explicit chat instruction.
- **OD-10 Drawdown latch.** After the 8% drawdown latch, the owner may resume only once the current valid NAV is back above 0.92 × the high-water mark. A flat account cannot recover, so the run then stops.
- **OD-11 Local downtime.** After PC sleep, power loss or a Docker stop, the pilot continues automatically once its checks pass. The downtime is a disclosed transient block, not a latch. The owner acknowledges that protection needs the PC and Docker running.
- **OD-12 Deployments during a pilot.** Fixes and milestones may deploy while a pilot runs, outside HH:00–HH:03 UTC, with a graceful worker stop. A changed code identity starts a new evaluation segment.
- **OD-13 Horizon and completion.** The pilot is open-ended. The owner names a checkpoint date, and M4 is complete once that checkpoint report is recorded. M5 may start after activation (M4-B).
- **OD-14 Reproducibility.** Take weekly protected, checksummed dumps of the market tables, sized after measuring disk space. If the measured disk cannot hold them, the experiment is marked not fully replayable beyond seven days.

**Stated intent, not approval (OD-2 to OD-8).** The owner intends to approve, exactly as ExecPlan 0015 describes them:
- `PAPER_PILOT_V1`, keeping the 5 s maximum quote age and reporting SOL pause counts (OD-2, OD-6)
- `TREND_REFERENCE_V1` (OD-3)
- `PAPER_COST_V1`, `VALUATION_BID_V1` and `FILTER_POLICY_V1` (OD-4)
- `COST_SCENARIO_HYPOTHETICAL_H1`, labeled hypothetical, with H2 as a replay sensitivity (OD-5)
- `EVALUATION_PROTOCOL_V1` with no acceptance threshold (OD-7)
- `BASELINE_SET_V1` (OD-8)

Under [ROADMAP](ROADMAP.md) and [RISK_POLICY](RISK_POLICY.md), these become approvals only when the owner approves the exact hashes in the authenticated UI that M4 builds. Chat text is not an approval. This entry does not authorize implementing M4 or activating anything.

### 2026-09-29 — Replay throughput scope and budget (ExecPlan 0017)

After the seven-day replay still missed its budget, the owner reviewed the recommendation in [ExecPlan 0017](archive/plans/0017-replay-throughput.md#3-owner-decisions-recorded-2026-09-29) and answered "do the recommended", then "merge it and start implementing 0017".

- **OD-A Scope.** The work covers three parts:
  - result-identical read-cost cuts in every mode;
  - replay-only batched step transactions with asynchronous commit;
  - replay-only state reuse behind a verification mode.
  
  The forward engine keeps one fenced transaction per step, with its state read inside that transaction.
- **OD-B Budget.** The declared 20 min seven-day replay budget stays. If the measured result still misses it, the owner chooses one of three options before any new measurement:
  - a revised time bound for the same workload;
  - a different workload;
  - no time bound, keeping two identical fingerprints.

This changes replay execution and verification only. It does not change strategy, risk, fill or valuation semantics, activation or any approval.

### 2026-09-30 — M4 pilot approvals, activation and checkpoint (ExecPlan 0015)

After M4 merged, the owner answered "ok I approve all to finish m4" in chat. As recorded above, chat text is not an approval, so the approvals and controls were made in the authenticated UI.
- **Approvals (UI, 09:04–09:05 UTC).** The owner approved the exact hashes of `PAPER_PILOT_V1`, `TREND_REFERENCE_V1`, `PAPER_COST_V1`, `VALUATION_BID_V1`, `FILTER_POLICY_V1`, `COST_SCENARIO_HYPOTHETICAL_H1`, `EVALUATION_PROTOCOL_V1` and `BASELINE_SET_V1`. These carry out the stated intent of OD-2 to OD-8. The owner also approved `COST_SCENARIO_HYPOTHETICAL_H2_STRESS`, which OD-5 kept for replay sensitivity; the pilot's manifest uses H1.
- **Experiment and Start.** The owner created experiment `d779fbf4-e1be-444c-ab55-7b61292eaa87` with cost scenario H1, approved its manifest `b6546e94…` and pressed Start.
- **Activation (OD-9).** The owner ran `tools/pilot-activate.ps1`, after an agent's attempt was refused by its auto-mode classifier. The run was ACTIVATED at 09:09:52 UTC.
- **OD-13 checkpoint.** The owner chose **2026-11-25** (8 weeks) as the checkpoint date. M4 is complete once that checkpoint report is recorded, and M5 may start now.

The evidence is in [ExecPlan 0015 §16](archive/plans/0015-evaluation-fixed-pilot.md#m4-b-owner-approvals-and-activation-verified-2026-09-30). This entry does not approve any other definition, strategy, domain or tool. It also does not change risk limits, pauses or funding.

### 2026-09-30 — M5-A implementation authorized (ExecPlan 0020)

After [ExecPlan 0020](archive/plans/0020-m5-agent-runtime.md) merged as `8fdc06a`, the owner wrote in chat: "I authorize implementing M5-A as specified in docs/plans/0020-m5-agent-runtime.md". The scope is batches B0–B7, in isolated test stacks only.
- **Not authorized yet.** B8, the normal deployment including migration 0007, and every M5-B step wait for a separate owner instruction in chat. M5-B covers the runtime start, Codex login, discovery, profile approval, probes and enabling the runtime.
- **Binding conditions** (from the same instruction):
  - The running M4 pilot is untouched, and plan 0020 §12 ("Coexistence") is binding.
  - No Docker or Compose command runs against the normal `adaptive-spot-lab` project without owner approval in chat, not even a read-only one.
  - Isolated stacks follow plan 0020 §10:
    - `asl-m5-<run>-<kind>` projects, `asl_m1_` databases and `10.254.x` subnets;
    - a per-run env file that sets every pilot and agent flag;
    - synthetic market data only;
    - a memory preflight;
    - one heavy stack at a time, and no heavy phase between HH:55 and HH:15 UTC.
  - No `codex login`, live model call or API key.
  - `.env`, `secrets/` and the owner's Codex home are never read. The only exception is the official shadcn and Lightweight Charts skill files, for UI work.
  - Migration 0007 is additive, as in plan §7.
  - The runtime gets no authority beyond the plan.
  - Delivery is one draft pull request with a commit per batch.
- **Stop and ask** on:
  - a material contradiction between contracts;
  - an M5-OD1 or M5-OD2 trigger;
  - anything that would touch the normal app or the pilot.

This entry authorizes building and testing only. It approves no runtime profile, enables nothing, and changes no M4 approval, pause, limit or funding. Chat text is still not an approval.

### 2026-09-30 — M5-OD1 resolved: code-mode-only models (ExecPlan 0020 B3)

At B3, the pinned Codex (codex-cli 0.159.2), run against the synthetic mock provider, exposed `apply_patch` for a model without `tool_mode: code_mode_only` (gpt-5.5). The mock requested the patch and Codex rejected it through the read-only sandbox, but configuration cannot remove the tool from the offer. For `code_mode_only` models (gpt-6.1-sol, gpt-6-luna, gpt-5.6-sol), Codex sent no tools at all: Code Mode fails closed. The evidence is in plan 0020 §15 (B3) and [INTEGRATION_EVIDENCE](archive/contracts/INTEGRATION_EVIDENCE.md#m5-agent-runtime-execplan-0020).

The implementer stopped and asked, as the M5-A authorization requires. The owner chose, in chat, the option offered as **"Code-mode-only models"**:
- The runner's baked configuration adds `features.code_mode_host=false`.
- Profile composition refuses any discovered model whose authenticated catalog entry is not `tool_mode: code_mode_only`, with the stable code `MODEL_EXPOSES_NATIVE_TOOLS`.
- A later change of the discovered catalog counts as drift and returns the runtime to `PROBE_ONLY`.
- The native capability set therefore stays empty by configuration, as RUNTIME_AGENTS requires. Models like gpt-5.5 cannot be used, and the M5-B probes still verify the live surface.

In the same exchange the owner allowed B4 to continue while B3 finishes, still in isolated stacks only. This decision approves no runtime profile or model, and enables nothing.

### 2026-10-01 — M5 acceptance: quiet period on a restart; no partial reruns (ExecPlan 0020 B7)

The final one-snapshot pass had been restarted four times for defects it found, each restart costing about 2.5 hours under the HH:55–HH:15 UTC rule for heavy isolated phases. Asked whether it could be shortened, the implementer recommended three things, and the owner answered in chat: "ok I approve your recommendation".
- **The running pass is not changed.** The window is part of the acceptance script, which the source snapshot covers.
- **Only if another restart is needed,** the same commit may add an explicit script option for a narrower quiet period of **HH:58–HH:07 UTC**, for isolated stacks only. The pilot's bar close and HH:05 report stay clear.
- **No partial reruns.** After any source fix, every §10 phase runs again on one snapshot.

This changes nothing for the normal app: no Docker or Compose command against it without owner approval in chat, and the deployment window in plan 0020 §12 is unchanged.

### 2026-10-02 — M5-A inert normal deployment (B8) approved, before the merge (ExecPlan 0020)

After the final isolated pass, the implementer reported the B0–B7 results and put three decisions to the owner: a read-only check of the normal app, the inert normal deployment (B8) and its timing, and when to merge the pull request. The owner answered in chat on 2026-10-01: "I approve all". The implementer stated its reading before acting: the read-only check first, then B8 from the verified pull-request commit before the merge, then the merge once B8 is verified.

The read-only check on 2026-10-02 found the pilot healthy with no open position, and one thing unrelated to M5: the market worker's collection was cycling 30–50 times an hour. The implementer stopped and asked again. The owner chose "Deploy, then merge": run B8 in the next HH:15–HH:45 UTC window if no position is open, verify, then merge; the market worker is handled separately.

- **What this approves:** `tools/m5-deploy.ps1` against the normal app (plan 0020 §13, steps 1–10), including migration 0007, and the read-only commands needed to verify it; then merging MentorAliu/adaptive_spot_lab#12.
- **What it does not approve:** any M5-B step. No agent service is started, `asl_agent` stays NOLOGIN, `ASL_AGENTS_ENABLED` stays 0, and no Codex login, profile approval, probe or enabling happens without a separate owner instruction. The market worker, postgres and the pilot workers are not touched.

### 2026-10-02 — M5-B started; runtime profile `gpt-6.1-sol` at `medium` effort (ExecPlan 0020)

After the merge of M5-A the owner asked what M5-B needs, then instructed in chat: "run agent-activate and let's see what happens". The desktop app refused the implementer's run, so the owner ran `agent-activate.ps1` and then `agent-login.ps1` personally.

Asked which discovered model fits, the implementer recommended `gpt-6.1-sol` at reasoning effort `medium`, and the owner answered "ok let's do it". The basis was the vendor's published descriptions and the runtime's limits, not a measurement:
- the vendor describes the model as near its top model for complex, repeated, long-running work at a lower cost ([INTEGRATION_EVIDENCE](archive/contracts/INTEGRATION_EVIDENCE.md#model-catalog-and-model-descriptions-m5-b-2026-10-02));
- the runtime's volume is low (at most 12 parent workflows a day), so a high-volume efficiency model gains little;
- the model's own default effort is `low`; `medium` was chosen for factual care, and the higher efforts were avoided because each step has a 120 s deadline (an inference, not a test).

As recorded for M4, chat text is not an approval: the owner composed and approved the exact profile hash `1df9c916…f395`, allowed probes and started the probe run in the authenticated UI. The alternatives were `gpt-6-astra` (more capable, more allowance) and `gpt-6-luna` (cheaper). A different model needs a new profile, a new approval and a new probe run.

Not decided: enabling the runtime. It stays the owner's UI action.

### 2026-10-02 — Market-worker deployment approved (ExecPlan 0021)

The report on pull request MentorAliu/adaptive_spot_lab#13 put four decisions to the owner: the deployment of the market-worker fix, the overload policy, two read-only confirmation queries, and the stopped test volumes. The owner answered in chat: "I approve the deployment in the next HH:15–HH:45 window".

- **What this approves:** the steps of [ExecPlan 0021 §11](archive/plans/0021-publication-cost-at-density.md#11-normal-deployment-run-2026-10-02) against the normal app: the read-only state checks, a protected backup, building and recreating `market-worker` only, and the read-only verification and soak.
- **What it does not approve:** merging the pull request; changing the overload or the clock-check policy; removing any volume or image; or touching postgres, the pilot workers, the API, the web or the agent services.

The deployment ran at 15:15–15:18 UTC on 2026-10-02. The pilot's containers, lease epoch and evaluation segment are unchanged; the evidence is in the plan.

### 2026-10-02 — Pull request #13 merged; follow-up plan requested (ExecPlan 0022)

After the deployment report the owner wrote in chat: "merge PR #13 and draft the follow-up plan".

- **What this approves:** merging MentorAliu/adaptive_spot_lab#13, and writing the follow-up plan as a proposal. The pull request was merged as `d075a78` at 18:32 UTC. `services/engine` on `main` has the same git tree as at `4003e75`, the commit the running market-worker image was built from, so nothing was redeployed.
- **What it does not approve:** implementing [ExecPlan 0022](archive/plans/0022-reference-checks-and-rest-budget.md), any command against the normal app, any deployment, or a change to the clock rule, the overload policy or the REST ceiling. The plan puts its decisions to the owner in its §7.

### 2026-10-02 — ExecPlan 0022 approved for implementation; clock option (a); one read-only query

The plan put its decisions to the owner in its §7. The owner answered in chat: "approve the plan, option (a), run the read-only query".

- **Approved for implementation.** [ExecPlan 0022](archive/plans/0022-reference-checks-and-rest-budget.md) is built and verified on isolated stacks only.
- **Clock, option (a).** A routine clock check that cannot measure precisely, or cannot be made, keeps making quotes unusable at once. No grace inside the 120 seconds. The plan's design follows that option, including the rotation path it makes stricter.
- **One read-only query of the normal database:** the `rateLimits` array of the latest stored `exchangeInfo` answers. It ran at 19:57 UTC inside a read-only transaction and found the declared allowance in the documented shape (the plan's §18 has the result).
- **Not approved by this:** the deployment of the change, which stays a separate decision (plan §13); the two optional reads the plan also lists; any other command against the normal app.

### 2026-10-03 — Market-worker deployment approved (ExecPlan 0022)

The report on pull request MentorAliu/adaptive_spot_lab#15 left the deployment of [ExecPlan 0022](archive/plans/0022-reference-checks-and-rest-budget.md) to the owner. The owner answered in chat at 05:20 UTC: "I approve the deployment in the next HH:15–HH:45 window".

- **What this approves:** the steps of [the plan's §13](archive/plans/0022-reference-checks-and-rest-budget.md#13-normal-deployment-run-2026-10-03) against the normal app: the read-only state checks, a protected backup, the rollback tag, building and recreating `market-worker` only, and the read-only verification and soak.
- **What it does not approve:** merging the pull request; changing the clock rule, the usability rule or the REST ceiling; removing any volume or image; or touching postgres, the pilot workers, the API, the web or the agent services.

The deployment ran at 05:20–05:22 UTC on 2026-10-03. The pilot's containers, lease epoch and evaluation segment are unchanged; the evidence is in the plan.

**Merge.** At 05:36 UTC, while the soak was running, the owner wrote: "merge PR #15 once the soak passes". That approves merging MentorAliu/adaptive_spot_lab#15 when the soak's pass conditions (the plan's §13.2, step 8) are met and recorded, and not otherwise. The soak passed at 07:27 UTC, the records were pushed, and the pull request was merged as `ed9fae3` at 07:32 UTC.

### 2026-10-03 — M5 closed on the capability probes; live token refresh becomes a follow-up (ExecPlan 0020)

The owner asked what it would take to complete M5, and said the milestone was taking too long. The answer: the only open criterion was one observed live token refresh. The CLI performs a refresh only during a model call, once the login is 8 days old, which here is 2026-10-10 11:20 UTC. The owner chose the option put to them and wrote in chat: "close M5 on the probes, refresh as a follow-up".

- **What this decides:**
  - M5 is complete on the live capability probes of 2026-10-02 (run `70099227…`, PASSED, 14 of 14), with the limits recorded in [ExecPlan 0020 §17](archive/plans/0020-m5-agent-runtime.md#m5-closure-2026-10-03).
  - The plan's completion criterion ("one token refresh has been observed") and the [ROADMAP](ROADMAP.md) M5 gate item "Verify token refresh" are carried for now by the isolated copy-back evidence.
  - The live refresh, a later call that uses the refreshed tokens, and a runner recreate become a follow-up check on or after 2026-10-10 11:20 UTC.
- **Why it was acceptable, as put to the owner:**
  - The copy-back is verified in isolation.
  - A failed refresh shows `AUTH_REQUIRED`, which blocks only new model work, and is recovered by a re-login.
  - M5's agents hold read and assessment tools only.
  - The risk: a fault the isolated tests missed would stop model work about 2026-10-10 until it is fixed.
- **What it does not decide:**
  - Enable.
  - Any command against the normal app. The follow-up's read-only verification and its runner recreate each need the owner's approval in chat.
  - The start of M6, which needs its own plan and approval.
  - Checking any acceptance-checklist row; rows are checked only at M8.

### 2026-10-03 — Pull request #16 merged; M6 plan requested (ExecPlan 0023)

After the M5 closure was recorded in pull request MentorAliu/adaptive_spot_lab#16, the owner wrote in chat: "merge PR #16 and draft the M6 plan".

- **What this approves:** merging #16, which was merged as `72ba76f` at 05:46 UTC, and writing the M6 plan as a proposal.
- **What it does not approve:** implementing [ExecPlan 0023](archive/plans/0023-m6-research-investigations.md), any command against the normal app, any activation, or any of the decisions the plan puts to the owner in its §3.3.

### 2026-10-03 — ExecPlan 0023 approved for implementation with the recommended decisions

The plan put seven decisions to the owner in its §3.3, each with a recommendation. The owner answered in chat: "approve the plan with your recommendations, and I want to use chatgpt 6 asta to implement this plan".

- **Approved for implementation.** [ExecPlan 0023](archive/plans/0023-m6-research-investigations.md) (M6) is built batch by batch and verified on isolated stacks.
- **The seven decisions, each as the plan recommends:**
  - **M6-OD1, (a), non-blocking.** One documented, key-less external source family for the live walk-through. Its rights and retention review in B0 is still a gate; if it fails, (b) applies.
  - **M6-OD2, (b).** No research on bar history in M6.
  - **M6-OD3.** The research-envelope values of the plan's §5.5 are built in as written, including the points the plan leaves to the B0 measurements. This is not the exact-hash approval of the envelope, which the owner gives in the UI in M6-B.
  - **M6-OD4, both rules, for M6's isolated acceptance.** After a fix that changes only tests or harness files, the failed phase and the phases that use the changed file are rerun; a product-code fix still reruns every phase. The quiet period HH:58–HH:07 UTC applies to every isolated heavy phase only once B0 has recorded that such a phase does not move the pilot's HH:05 report. Both change the [rule of 2026-10-01](#2026-10-01--m5-acceptance-quiet-period-on-a-restart-no-partial-reruns-execplan-0020-b7), for M6.
  - **M6-OD5, (a).** In M6 the owner can reject a promotion request or leave it pending. Approving one arrives with M7.
  - **M6-OD6, (a).** Until the pilot ends, a shadow is a deferred replay and is labeled as one.
  - **M6-OD7, (a).** M6 is complete when M6-A is deployed and the live walk-through of the plan's §13.3 is recorded. The first live pending promotion is a follow-up, so the roadmap gate clause "a promotion request remains pending rather than self-approved" has isolated evidence only at completion.
- **Implementer.** The owner hands the implementation to another authoring client. The repository instructions, this file and the plan bind it as they bind any implementer.
- **Merge.** In a second chat the same day the owner repeated the approval and wrote: "approve the plan with your recommendations, merge PR #17". That approves merging MentorAliu/adaptive_spot_lab#17, which holds the plan and these records. It was merged as `1509072` at 07:54 UTC.
- **Not approved by this:**
  - Any step of M6-B (plan §13.2): activation, the exact-hash approvals of the envelope, a source version and the new runtime profile, the probes, and Enable.
  - Any command against the normal app. The M6-A inert deployment stays its own step under the plan's §13.1, and the read-only measurements of the normal app that B0 needs are asked for first.
  - Approving a promotion, a strategy for the main portfolio, or any trading authority. M6 adds none.
  - Checking any acceptance-checklist row; rows are checked only at M8.

### 2026-10-03 — Test volumes and images of the 0021 and 0022 runs removed

The reports on ExecPlans 0021 and 0022 left the stopped test volumes and images of their isolated runs to the owner. After the M6 plan was merged the owner wrote in chat: "remove the stopped test volumes and images too".

- **What this covers:** the Docker volumes and images of runs `lag-1002a`, `lag-1002b`, `lag-1002c`, `lag-1002d`, `ref-1002a` and `ref-1002b`, which are the ones those reports named. They were removed on 2026-10-03 between 08:00 and 08:02 UTC: 14 volumes with about 22.9 GB of synthetic data, and 65 images ([COMMANDS](archive/COMMANDS.md#test-run-cleanup--2026-10-03)).
- **What it does not cover:** the evidence files of those runs under `.cache/m2/`, which stay; the test volumes and images of every other run on the host; and anything of the normal app.

### 2026-10-03 — This project's old test runs removed; other projects' Docker resources left to the owner

After the first cleanup the report named the test data still on the Docker host. The owner wrote in chat: "remove all old test runs", and then: "make sure to cleanup everything except for this project, all other project files are deprecated and removed from the computer".

- **Done under the first instruction:** the Docker volumes and images of this project's isolated test runs of M1 to M5 and of three small development stacks were removed on 2026-10-03 between 08:15 and 08:38 UTC: 188 volumes with 92.7 GB, and 1,076 images ([COMMANDS](archive/COMMANDS.md#old-test-run-cleanup--2026-10-03)). Their evidence files under `.cache/` stay.
- **What the second instruction covers:** the Docker resources of other projects on the host: 320 volumes with 122.5 GB, 309 images and 135 networks. Among them are the database, backup and secret volumes of `paper-trader` and `crypto-signal-bot`. The owner states that those projects are deprecated and that their files are removed from the computer.
- **Not done by the implementer:** the coding client's safety check refused that removal as an irreversible deletion, also after the owner had chosen to allow it. The implementer left the exact list and a script.
- **Done by the owner:** the owner ran that script on 2026-10-03 between 09:28 and 09:40 UTC. It removed the 320 volumes, 135 networks and 308 of the 309 images. One 4.8 MB helper image, `testcontainers/ryuk`, is left; the script could not address it by its tag. Afterwards the host holds only this project's resources and the shared build cache ([COMMANDS](archive/COMMANDS.md#old-test-run-cleanup--2026-10-03)).
- **Build cache.** The owner then wrote: "prune the build cache". It was pruned between 11:26 and 11:30 UTC, from 52.7 GB to the 7.3 GB that existing images share.
- **Kept in every case:** the normal app with its volumes, images, rollback tags and networks; `adaptive-spot-lab-test`; the pnpm cache volume; the five base and tool images this repository references. The build cache was not touched.

### 2026-10-03 — Docker test resources are removed after each implementation

After the host cleanup of the same day the owner wrote in chat: "everytime something get's implemented, you chose what's most important, I want to cleanup docker images and volumes to prevent building up".

- **What this decides:** a standing rule. When a piece of work is implemented, the Docker resources of its isolated test runs are removed, and what matters is kept. The implementer makes that choice by the lists in [DOCKER](DOCKER.md#cleaning-up-disposable-resources) and does not ask for each cleanup.
- **Kept:** the normal app with its volumes, networks and current images; the latest rollback tag of each service and the images a running experiment is pinned to; the base and tool images the repository pins; every run's evidence files; protected backups.
- **Removed:** a finished run's containers, networks, volumes and images once its evidence is recorded; every run of a task before the task is reported; and, after a verified milestone deployment, older rollback tags, untagged images and the build cache.
- **What it changes:** the acceptance harnesses kept every run's volumes and images until now. Each harness gets a `Clean` phase; `Stop` still removes nothing.
- **What it does not change:** no Docker or Compose command against the normal app without the owner's approval in chat. Removing a rollback tag is therefore a step of an approved deployment. No global prune of volumes or tagged images, ever.

### 2026-10-03 — M6 B0 bounded read-only measurements and process-only script execution

OBSERVED owner replies in the implementation chat: "Approve these read-only measurements" and "Approve process-only script execution".

- Approved `tools/m6-b0-observe.ps1` for normal-app memory and HH:05 report timing, baseline and loaded repeats: filtered Docker `ps`, selected `inspect` and `stats`, selected `info`, `/proc/meminfo`, the database name and a fixed metadata SELECT forced read-only with short timeouts. The script's review mode prints the full scope. No normal Compose command, service change, migration, secret read, approval or activation is included.
- Approved process-only `-ExecutionPolicy Bypass` when invoking reviewed repository M6 scripts with Windows PowerShell 5.1. Persistent policy and existing service security settings are unchanged.
- B10 is not authorized by these replies. B11 remains owner-only. M6-OD4 still requires its measured loaded comparison before the narrower quiet window can be used.

### 2026-10-03 — M6 B0 research cutoff clarification

OBSERVED owner continuation instruction: "don't stop until it's completed". Independent B0 measurements resumed under the existing bounded observer and process-only script approvals. The implementer kept the specific cutoff question pending while those measurements ran.

The owner then answered "Approve the cutoff clarification (recommended)" to this question: may RESEARCH_V1 refresh completions and follow-on source context obey the hypothesis cutoff, while EVENT_INVESTIGATION_V1 may receive its own refresh? This resolves ExecPlan 0023 §5.8 against §5.5/R11 and the time-scoped tool contract: research source content available after the hypothesis cutoff is withheld from completions, initial/follow-on context, summaries and artifact projections. An investigation may receive its own refresh through its completion without moving its cutoff or widening searches. The exception grants no research access to late source content or hidden results. B10 and B11 are unchanged.

INFERRED implementation implication of the plan's already-permitted DEV/VALIDATION experiment reads: a derived typed artifact is governed by its authorized underlying data provenance, rather than excluded merely by being calculated later. This is not an additional owner permission or an exception for late source evidence; its semantics must be verified by the required isolation cases.

### 2026-10-03 — Owner requests the current M6 checkpoint on main

OBSERVED owner instruction in the implementation chat: "push changes to main". This supersedes the earlier PR-only/no-direct-push instruction for this checkpoint and authorizes committing the current changes, preserving the newer remote main commits, and pushing the result to main without force.

The checkpoint contains VERIFIED B0 completion and IMPLEMENTED draft B1 code whose migration preflight failed the seeded-definition hash check. It is not M6-A acceptance. The scoped B1 correction/rerun question remains pending. This publishing instruction grants no B10 deployment, normal-app command, B11 activation or trading authority.

### 2026-10-03 — Continue M6 B1 after the migration preflight failure

OBSERVED owner instruction in the implementation chat: "go ahead with b1", following the explanation of the proposed canonical-text binding correction, isolated migration/role/trigger/restore checks and the newly merged `Clean` requirement. This approves the scoped correction and completing B1 in isolation. The prior failed seed-hash check remains evidence; it is not relabeled as passed. The instruction grants no normal-app command, deployment, B11 activation, envelope change or trading authority.

### 2026-10-03 — Continue B1 through the isolated restore diagnosis

OBSERVED owner instruction: "don't stop until complete it", replying to the request to diagnose the isolated restored-schema metadata mismatch, correct the harness if it is representation-only, and rerun B1. This authorizes that diagnosis, correction and completion of B1's isolated checks without another confirmation for the same work. It does not authorize a change to protected M1–M4 tables, the research envelope, normal services, B10 or B11. The failed comparison remains recorded; acceptance still requires actual passing evidence and cleanup.

### 2026-10-04 — Owner requests a B1/B2 checkpoint PR and merge

OBSERVED owner instruction after B2 completion: "create pr and merge into main".
This authorizes publishing `codex/m6-research-investigations`, creating a PR to
`main` and merging the completed B1/B2 checkpoint. The branch contains B1 source
commit `7f327ae`, its publication record and B2 source commit `431dff5`.

This checkpoint publication supersedes the earlier instruction to wait until
B0–B9 acceptance before creating a PR for this work. Full M6-A acceptance and
its remaining batches stay open. Publication grants no normal-app Docker or
Compose command, B10 deployment, B11 activation, envelope change or trading
authority. Preserve the tested source, existing main history and failed-run
evidence; do not force-push or weaken repository merge requirements.

### 2026-10-04 — Owner requests a B3 checkpoint PR and merge

OBSERVED owner instruction after verified local B3 commit `85104b7`:
"create pr and merge it". This authorizes publishing
`codex/m6-b3-research-runner`, opening a PR to `main` and merging the completed
B3 checkpoint. It supersedes the preceding local-commit-only instruction for
this batch and the plan's later full-M6-A PR timing for this checkpoint.

Preserve the tested source and failed-run evidence, use an ordinary merge
without force or an administrator bypass, and record the actual GitHub check
results. B4 onward and full M6-A acceptance remain open. This publication grants
no normal-app Docker/Compose command, deployment, activation, envelope change
or trading authority.

### 2026-10-04 — M6 B4 handed over, and four points the plan left open (ExecPlan 0023)

OBSERVED owner instruction in a Claude Code session: continue M6-A with batch B4
only (bridge, staging, versioned stores, sealed datasets, job and result relay,
shadows as deferred replays), on a new branch from `main` at `6e8fbb6`, verified
in isolated Compose projects with synthetic fixtures, delivered as a pull request
that is not merged until the owner says so. B5 onward, deployment and activation
stay out of scope, and no command may address the normal app.

The owner asked to be consulted where the plan does not decide something. Four
such points were put to the owner in that session, each with a recommendation,
and the owner took every recommendation:

| Point | Decided |
|---|---|
| **Store rotation.** [§5.4](archive/plans/0023-m6-research-investigations.md#54-datasets-stores-and-staging) rotates a store "when it reaches its size cap", and §4.1 says a shadow keeps its version until it ends; a job on a store at the cap is already refused (`STORE_CAP`) | **Rotate early.** A new version becomes current once the current one spans 28 days (49 less the 21-day shadow) or the same share of 20 GiB. The old version is fed only while a running shadow is bound to it, never past the cap, and is dropped whole once no queued or running job or shadow uses it. No envelope value changes |
| **What one shadow advance replays.** §5.6 names the reference replay as the comparison but neither its cost scenarios nor when it runs | **The candidate and the reference strategy, under H1**, over the same window and rule: two replays per advance. `H2_STRESS` is not run in shadows, and every mark says so |
| **When a dataset is sealed** | **Once per UTC day** after staging has caught up, covering at most the last 21 days of the current store version. The same pass advances the shadows |
| **Whether shadow advances spend the trial budget** | **No.** They do not count toward the 12 jobs a UTC day or the queue of 4. Their own bounds apply: 4 active shadows, one queued or running advance per shadow, one scheduled advance per shadow per UTC day, and still one running job at a time overall |

These decide implementation behavior inside the approved envelope. They change
no envelope value, grant no approval and authorize no deployment or activation.

### 2026-10-04 — Owner assigns M6 B5 to a second session, with the B5/B6 split of EvidenceInjection

OBSERVED owner instruction in a Claude Code session on 2026-10-04: "Implement batch B5 of ExecPlan 0023 for Adaptive Spot Lab M6-A … The plan is approved; do not write a new one." The scope given is "the source registry with hashed source versions, the source-fetcher service and its asl_source identity, immutable fetch and evidence records with their separate times, PostgreSQL full-text search with the cutoff filter and role projection applied before ranking, polling, and SOURCE_REVISION trigger records with dedupe and cooldown".

- **Parallel work.** B4 may run in another session; B5 uses its own worktree and branch, and only one isolated stack runs on the host at a time. The record of the PR #23 merge is left to the B4 session.
- **EvidenceInjection is split.** "The plan puts EvidenceInjection in B5, but the tools that hand evidence to a role and the scheduler that consumes triggers are B6 (section 5.8). Deliver what does not need definitions v2, record the remaining cases as NOT RUN for B6".
- **Sources stay unapproved.** "A source version stays PROPOSED; never approve one, and never enable asl_source." Tests use the loopback mock source in isolated stacks only: "Never fetch from GitHub or any public endpoint, and make no model call; the real unauthenticated fetch path stays NOT RUN until I activate it in M6-B."
- **Verification.** Build, Checks, Regression, SourcePolicy and EvidenceInjection; Migration on a schema change; HoldoutIsolation if the B3 projection code is touched. GitHub CI does not run, so the local acceptance is the only automated evidence.
- **Delivery.** A pull request to `main` when B5's gates pass; "Do not merge the PR until I say so." No command against the normal app, no deployment, no activation, no real credential.

This changes who implements this one batch; the handoff of 2026-10-03 named another implementer for M6-A. It grants nothing else: B10 and B11 keep their own approvals.

### 2026-10-04 — Owner asks to merge the M6 B5 PR

OBSERVED owner instruction in the same Claude Code session, after pull request
[MentorAliu/adaptive_spot_lab#24](https://github.com/MentorAliu/adaptive_spot_lab/pull/24)
was opened and reported: "merge it". This lifts the "Do not merge the PR until I
say so" condition for B5 only.

Use an ordinary merge commit pinned to the verified head, without force, an
administrator bypass or branch deletion. `main` was still at `6e8fbb6` and the
B4 pull request (#25) was open and unmerged, so B5 merges first; B4 then merges
`main` into its branch, keeps both sessions' entries and reruns every phase
whose inputs changed. The merge grants no normal-app command, deployment,
activation, source approval, `asl_source` login or trading authority, and it
completes neither M6-A nor any later batch.

### 2026-10-04 — Owner asks to merge the M6 B4 PR

OBSERVED owner instruction in the B4 Claude Code session at 21:30 UTC, after pull
request [MentorAliu/adaptive_spot_lab#25](https://github.com/MentorAliu/adaptive_spot_lab/pull/25)
was opened and reported and after B5 had merged as `52eab97`: "merge it". This
lifts the "Do not merge until I say so" condition for B4 only.

The pull request conflicted with `main` at that point. Before it is merged,
`main` is merged into the B4 branch with both sessions' entries kept, and every
phase whose inputs changed is rerun on the merged source; the pull request is
merged only if they pass. Use an ordinary merge commit pinned to the verified
head, without force, an administrator bypass or branch deletion. The merge
grants no normal-app command, deployment, activation, source approval, identity
enablement or trading authority, and it completes neither M6-A nor any later
batch.

### 2026-10-05 — M6 B6 definition generations, schedule and ended shadows

OBSERVED owner instruction in a Claude Code session: implement batch B6 of
ExecPlan 0023 only (definitions v2, the seven tools, the code-owned workflow
graph, waiting and completions, budgets v2 and priority, the trigger scheduler,
the M6 prompts and probes CP-15 onward defined and tested offline), on a new
branch from `main` at `5da6b90`, verified in isolated Compose projects with
synthetic fixtures, the recorded provider, the fake CLI, the mock provider and
the loopback mock source. No public endpoint, no model call, no normal-app
command. B7 onward, deployment and activation stay out of scope. The pull request
is not merged until the owner says so.

The owner asked to be consulted where the plan does not decide something. Four
such points were put to the owner in that session, each with a recommendation,
and the owner took every recommendation:

| Point | Decided |
|---|---|
| **Which definitions the M5 templates run under.** Definitions v2 could have replaced v1 for `MARKET_ASSESSMENT_V1` and its review | **Keep v1 as approved.** A template belongs to the generation that defines it. The two M5 templates keep catalog, grants, schema and budgets v1; the five M6 templates use v2. The runtime profile binds both sets of hashes |
| **When `RESEARCH_V1` starts "by schedule".** [§5.8](archive/plans/0023-m6-research-investigations.md#58-agent-runtime-definitions-v2) names the start but no rule | **One per new daily dataset.** When the bridge has sealed a new research dataset, one scheduled research workflow is queued, at most one a UTC day, and only while the runtime is `ENABLED` and the envelope is approved |
| **A candidate whose shadow ended without the evidence minimum.** B4 left it in `SHADOW_RUNNING` with the reason on the shadow | **Retire it.** The candidate moves to `RETIRED` with the shadow's end reason as gate evidence. It does not become `EVIDENCE_READY` and no promotion workflow starts for it |
| **M5 tests that assert an M5-only database.** A few assert the M5 definition set or grant inventory exactly, which schema 0008 extends | **Update in place.** They keep asserting everything M5 claimed and now compare against what the code owns for both generations. What they can no longer cover has its own M6 test, named in [TESTING](archive/TESTING.md#m6-b6-agent-workflows-and-tools-execplan-0023) |

These decide implementation behavior inside the approved plan and envelope. They
change no envelope value, approve no profile, envelope, source or promotion, and
authorize no deployment, activation or login.

### 2026-10-05 — Owner asks to merge the M6 B6 PR

OBSERVED owner instruction in the B6 Claude Code session at 11:49 UTC, after
pull request [MentorAliu/adaptive_spot_lab#26](https://github.com/MentorAliu/adaptive_spot_lab/pull/26)
was opened and reported with its open points: "merge it". This lifts the "Do not
merge the PR until I say so" condition for B6 only.

`main` was still at `5da6b90`, the commit B6 was branched from and accepted on,
so nothing has to be merged into the branch and no phase has to be rerun. Use
an ordinary merge commit pinned to the verified head, without force, an
administrator bypass or branch deletion. The merge grants no normal-app
command, deployment, activation, profile, envelope or source approval, identity
enablement or trading authority, and it completes neither M6-A nor any later
batch. The points the pull request left for the owner (the two review findings
kept as the contract states them, the proposed budget values, the shared daily
count, the agent read models accepting schema 0008) were not decided by this
instruction; they stay open in
[ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks).

### 2026-10-05 — Generation 1 prompt trimming drops the oldest result first

OBSERVED owner instruction in a separate Claude Code session on 2026-10-05:
confirm the finding B6 recorded as an open risk (when a generation-1 prompt
exceeds its size bound, the M5 composer hides the newest tool result first),
write a proposal, and change no M5 behavior without the owner's approval. If
approved: a new branch from `main`, a test, the affected phases in an isolated
run, the documents, and a pull request that is not merged. The running normal
application is not to be touched.

The finding was confirmed in the code and by a no-database test, and the
proposal was put to the owner with a recommendation on each of two questions.
The owner answered both in that session's question dialog at about 13:05 UTC
and took both recommendations:

| Question | Answer |
|---|---|
| **What happens to the behavior.** Fix it, keep it and correct the description, or leave everything | **Fix it.** Generation 1 drops the oldest result first, as generation 2 does |
| **Where to build it.** The proposal said pull request #26 was still open | **After #26 merges.** |

The proposal's statement about pull request #26 was out of date when it was
put: the session had read the pull request as open shortly before it was merged
at 11:51:35 UTC as `7f0268a`, and did not read it again before asking. VERIFIED
read-only after the answer; the owner's condition was therefore already met,
and the work was done from `main` at that commit.

The decision changes one behavior that M5 acceptance covered without
exercising it: which results a generation-1 prompt hides when it is over its
bound. It changes no definition, prompt file, schema, budget, seed or profile
hash, and it approves no profile, deployment, activation, merge or command
against the normal application. A read of the normal database for stored steps
that were trimmed was offered and not asked for; none was made.

### 2026-10-05 — Owner asks to merge the generation-1 trimming PR

OBSERVED owner instruction in the same Claude Code session at about 14:05 UTC,
after pull request [MentorAliu/adaptive_spot_lab#27](https://github.com/MentorAliu/adaptive_spot_lab/pull/27)
was opened and reported with what was not run and what is not known: "merge
it". This lifts the "do not merge" condition for that pull request only.

`main` was still at `7f0268a`, the commit the change was branched from and
verified on, so nothing has to be merged into the branch and no phase has to be
rerun. Use an ordinary merge commit pinned to the verified head, without force,
an administrator bypass or branch deletion. The merge grants no normal-app
command, deployment, activation, profile approval or read of the normal
database, and it completes no batch of ExecPlan 0023. Whether a stored M5 step
was ever trimmed stays unknown.

### 2026-10-05 — M6 B7: experiment read codes, canceled jobs and rejected promotions

OBSERVED owner instruction in a Claude Code session: implement batch B7 of
ExecPlan 0023 only (the owner API for M6, its OpenAPI document and the
generated web types, verified by `ApiAuth` and the contract and drift checks),
on a new branch from `main` at `d1f8d88`, in isolated Docker stacks, with no
model call, no public endpoint and no command against the running normal
application. Pages (B8), the B9 phases, deployment (B10), activation and any
approval stay out of scope. The pull request is not merged until the owner says
so.

The owner asked to be consulted before any code was written, on the two points
B6 left open in [ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks)
and on anything else the plan does not decide for B7. Three questions were put
in that session's question dialog, after `main` had been verified at `d1f8d88`
and before any file was edited, each with a recommendation, and the owner took
every recommendation:

| Question | Decided |
|---|---|
| **`read_experiment` answers an unknown ID with `SCOPE_DENIED` and a locked experiment with `HOLDOUT_LOCKED`.** One code for both would hide from a tuning role that an ID it holds exists | **Keep both codes.** Job and shadow IDs are random and no result a tuning role receives carries the ID of a full test or a shadow, so the second code confirms nothing new, and it is the owner's signal that a tuning role reached for locked results. No B6 behavior, tool contract or probe wording changes |
| **A job canceled before it ran is final for its input.** Whether a never-started job may be queued again | **It stays final.** Of the three ways it happens, a retry would serve only a job that aged out behind other work: after a permission-epoch change the requesting workflow has already failed, and an owner's cancel is final by intent. The age-out case is decided with B9's measurement of when a job's hour starts. B7 changes nothing in B3 or B6 and the owner read models say what a cancel means |
| **What an owner's rejection of a pending promotion does.** The plan lets the owner reject or leave it pending (M6-OD5) and migration 0008 lets only the agent identity move the row; nothing applied a rejection | **SYSTEM applies it.** The API records the `REJECT` as an exact-hash owner record. The agent worker then moves the promotion to `REJECTED` and its candidate to `REJECTED`, which is terminal and keeps its history, citing that record. Until the worker has run, the read model shows the decision as recorded and not yet applied. M7 can therefore approve only a promotion the owner left pending |

Choices the session reported as ordinary and took without a question, stated
before any code was written: the three owner-startable M6 templates and their
parameters come from the code-owned template definitions (`PROMOTION_V1` takes
the ID of an `EVIDENCE_READY` candidate, never a declaration); a job cancel and
a shadow stop record one request and are not blocked by a stale version,
because they only remove work; an owner refresh equal to an outstanding one is
refused instead of being answered without a stored key; two key-lookup routes
resolve unknown outcomes; the owner reads holdout and shadow results, labeled
with what is locked for the tuning roles; `SystemStatus.research` and
`.sources` come from recorded facts; the web change is limited to schemas; the
new routes answer 503 before migration 0008.

These decide implementation behavior inside the approved plan. They change no
envelope value, definition, prompt or profile hash, approve no profile,
envelope, source or promotion, and authorize no deployment, activation, login
or command against the normal application.

### 2026-10-06 — Owner asks to merge the M6 B7 PR

OBSERVED owner instruction in the same Claude Code session at about 06:09 UTC
on 2026-10-06, after pull request [MentorAliu/adaptive_spot_lab#28](https://github.com/MentorAliu/adaptive_spot_lab/pull/28)
was opened and reported with its per-phase results, what was not run and the
points left for the owner: "merge it". This lifts the "do not merge" condition
for that pull request only.

`main` was still at `d1f8d88`, the commit B7 was branched from and accepted
on, so nothing has to be merged into the branch and no phase has to be rerun.
Use an ordinary merge commit pinned to the verified head, without force, an
administrator bypass or branch deletion.

The instruction decides none of the points that report left for the owner.
They stay open in [ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks),
and the merged code behaves as the pull request describes until the owner says
otherwise: an owner's cancel of a screening lets the workflow that asked for
it go on; a recorded shadow stop takes no further mark; a runtime-profile
approval needs the profile ID in its stored spelling; four routes exist beyond
the list in §5.9.

The merge grants no normal-app command, deployment, activation or approval of
a profile, the envelope, a source version or a promotion. B7 completes neither
M6-A nor any deployment (B10), and B8–B9 are NOT RUN.

### 2026-10-06 — Two B7 behaviors kept: an owner cancel lets the workflow go on, a recorded shadow stop takes no further mark

OBSERVED owner decisions of 2026-10-06, stated in the B8 task prompt the owner
pasted into a Claude Code session that day, on two points B7 left open in
[ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks).
Neither changes code: both keep what B7 shipped (PR #28, merged as `2043fc0`).

| Point B7 left open | Decided |
|---|---|
| **An owner's cancel of a screening.** B7's review changed it: the job records `OWNER_CANCEL` and the workflow that asked for it goes on, where before it ended `FAILED` as revoked | **Keep the B7 behavior.** The job records `OWNER_CANCEL` and the workflow that asked for it continues with a `CANCELED` completion. It is not ended as revoked, because nothing was revoked |
| **A recorded shadow stop.** B7's review changed it: a result that arrives after the owner's request, before the research identity has applied it, is kept as history and is not a mark | **Keep the B7 behavior.** A recorded stop takes no further mark. A stop recorded during the last advance therefore ends the shadow `STOPPED` and retires its candidate, even if that advance would have completed the evidence |

The B8 dialogs state both before the owner confirms, from the consequence
lists the API returns (`THE_REQUESTING_WORKFLOW_RESUMES_WITH_A_CANCELED_COMPLETION`;
`CANDIDATE_RETIRED_UNLESS_EVIDENCE_READY` and
`A_RESULT_AFTER_THIS_REQUEST_IS_HISTORY_ONLY`) and one sentence each. The other
points B7 left for the owner are not decided by this entry and stay open in
§19: the profile ID spelling, the four routes beyond §5.9 and the low-rated
risks.

### 2026-10-06 — M6 B8: skill loading, consequence lists, navigation, detail routes, refresh intervals and the state before migration 0008

OBSERVED owner instruction in a Claude Code session: implement batch B8 of
ExecPlan 0023 only (the owner pages for M6 and the same-origin server
functions behind them, verified by `BrowserResearch` and `BrowserResearchError`
at 390 and 1440 px), on a new branch from `main` at `2043fc0`, in isolated
Docker stacks, with no model call, no public endpoint and no command against
the running normal application. The B9 phases, deployment (B10), activation
and any approval outside disposable fixture databases stay out of scope. The
pull request is not merged until the owner says so.

The owner asked to be consulted before any code was written on anything the
plan does not decide for B8. Six questions were put in that session's question
dialog, after `main` had been verified at `2043fc0` with a clean tree and no
open pull request, and before any file was edited. Each had a recommendation,
and the owner took every one:

| Question | Decided |
|---|---|
| **The official shadcn skill is not registered for Claude Code in that session** (the Skill tool does not list it; no copy under the repository, `apps/web` or `~/.claude/skills`). The official copy installed for Codex is at `~/.codex/skills/shadcn`, with the `SKILL.md` hash of the M0 record | **Read the Codex copy explicitly,** with its CLI reference and rules, as the M3 to M5 sessions did, and run `shadcn info`, `search` and `docs` from `apps/web` in the run's web tool image on bridge networking. That reaches the shadcn registry only; the application and its tests contact no public endpoint. The Lightweight Charts skill is read the same way |
| **Reject and revoke have no consequence list in the B7 API.** The owner's rule for B8 is that cancel, stop, reject and revoke state their consequences from the lists the API returns; B7 returns lists for a job cancel and a shadow stop only | **Add the lists to the API in B8.** One additive read-only field, `decision_consequences`, on the envelope, a source version and a promotion, as stable codes like the existing lists. No route, body, grant or migration changes; `Generate`, `Checks` and `ApiAuth` are rerun with every other engine phase on the acceptance run |
| **How the two new pages are reached.** The primary navigation has nine links and wraps at 390 px | **Two new primary links,** Research and Evidence, after Experiments: eleven in all, wrapping as before. No new primitive |
| **Where the detail of a research experiment, a candidate and an evidence item lives** | **Own routes:** `/research/experiments/$id` with `?cell=<index>` selecting the one cell shown, `/research/candidates/$id` and `/evidence/$id`, the pattern of `/experiments/$id?report=` and `/agents/$id` |
| **Refresh intervals.** M3 to M5 poll every 5 s; M6 state moves at job and fetch cadence, and §19 records the M6 read models as not indexed for growth | **5 s for what is open, 30 s for lists.** 5 s for the research status with its queue and for a detail whose job is still open; 30 s for the lists; never for an immutable document (an evidence revision, a result cell, an ended job). Always a refetch after a mutation and on focus. Each page shows when it last read and marks a failed refresh as stale |
| **What an M6 page shows before migration 0008** (`503 RESEARCH_SCHEMA_PENDING`), or against an API released before B7 (no such route). B10 deploys the web first | **A named unavailable state.** The links stay. Each M6 page and the new Approvals section name the cause, offer no control, and are distinct from the error state. The M4 and M5 parts of Approvals, Agents and System are unaffected |

Taken by the implementer as ordinary reversible choices and reported with the
questions, without objection: `/research` is one route whose `view` search
parameter selects overview, hypotheses, candidates, trials, shadows or
datasets on the installed Toggle Group; the pages call research jobs "trials"
and "research experiment" to keep them apart from the M4 Experiments page;
`PROMOTION_V1` in the start dialog picks from the listed `EVIDENCE_READY`
candidates and no ID is typed; no primitive is added; a status field the API
does not send reads "not reported by this API release".

These decisions grant no deployment, activation, normal-app command or
approval of a profile, the envelope, a source version or a promotion.

IMPLEMENTED differently in three details after the independent review of the
first pass. None of them is an owner decision; each is reported with the pull
request for the owner to keep or change:

- **A fourth list.** Each source version also carries `refresh_consequences`,
  because a refresh and a source approval can start event investigations and
  the dialogs said nothing of it. It is the same kind of field as the three
  the owner approved.
- **An ended job without a result is read every 30 s.** The decision names an
  ended job among the documents that are never polled. The bridge records a
  late result for a canceled, expired or failed job, so only an ended job that
  has its result is treated as immutable.
- **The state before migration 0008 is named by what the API answered**
  ("research schema pending", "no such route in this API") instead of a cause
  the page cannot know, and a read in that state is polled every 30 s so that
  "this page reads again by itself" is true on every page.

### 2026-10-06 — Owner asks to merge the M6 B8 PR

OBSERVED owner instruction in the same Claude Code session at about 12:47 UTC
on 2026-10-06, after pull request [MentorAliu/adaptive_spot_lab#29](https://github.com/MentorAliu/adaptive_spot_lab/pull/29)
was opened and reported with its per-phase results, what was not run and the
points left for the owner: "merge it". This lifts the "do not merge" condition
for that pull request only.

`main` was still at `2043fc0`, the commit B8 was branched from and accepted
on, so nothing has to be merged into the branch and no phase has to be rerun.
Use an ordinary merge commit pinned to the verified head, without force, an
administrator bypass or branch deletion.

The instruction decides none of the points that report left for the owner; the
reply that preceded it said so. They stay open in
[ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks),
and the merged code behaves as the pull request describes until the owner says
otherwise: each source carries a fourth consequence list,
`refresh_consequences`; an ended job without a result is read every 30 s; the
state before migration 0008 is named "research schema pending" and is polled.

The merge grants no normal-app command, deployment, activation or approval of
a profile, the envelope, a source version or a promotion. B8 completes neither
M6-A nor any deployment (B10), and B9 is NOT RUN.

### 2026-10-06 — M6 B9: phase content, images, saturation length, job measurement, row counts, quiet window, lost store, regression and the read-only look

OBSERVED owner instruction in a Claude Code session on 2026-10-06: implement
B9 of [ExecPlan 0023](archive/plans/0023-m6-research-investigations.md) and then, only
after B9 is accepted and the owner has said yes in chat, B10. The owner asked
to be asked before any code was written: about the content of the phases the
plan names without defining, about every point the plan does not decide, about
the final regression, and about how the real pilot is known to be undisturbed,
with the exact read-only commands. The implementer put the proposed phase
content and eight questions with a recommendation each. The owner answered at
about 13:40 UTC: "use as recommended".

The implementer reads that answer as accepting every recommendation, including
the two that needed a yes of their own (the read-only commands of point 8 and
test containers running through one quiet window in point 5), and said so in
its next message. That reading is the implementer's; the owner can withdraw
either at any time.

1. **Pre-M6 images.** `MixedVersion` and the rehearsal use the exact images
   the normal app runs, referenced by image ID inside isolated projects, as
   `Migration` already does for the two pilot workers. The test only reads
   them. `Clean` removes its own project-scoped tags by name, never forced.
2. **`ResearchSaturation`.** Thirty measured minutes: the M2 stream workload
   at its normal rate with the five-minute burst of 100 frames a second inside
   it, and the M3 execution fixture for the same time, while the runner
   replays jobs back to back on a seven-day full-density store, the bridge
   stages a full-density backlog at its 20 batches a pass and the fetcher
   polls a mock source at the highest registered rate. Limits are those of
   §5.1. The budgets are the existing ones and none is relaxed: no
   `QUEUE_OVERLOAD` or `COLLECTION_GAP`, every frame published, publication
   p95 at most 250 ms and p99 at most 1 s, execution step p95 at most 750 ms
   and p99 at most 1,500 ms. The stream workload and the execution fixture
   use two databases of one main PostgreSQL container.
3. **The largest job.** A 21-day full test and a 21-day shadow advance do not
   fit one test window. Measured to completion: a screening on 21 days, a full
   test on 14 days and a shadow advance on 14 days. The 21-day full test and
   advance are reported as projections labeled INFERRED, and the 21-day full
   test is also run to completion in its own window if the measured rate
   projects it under 40 minutes. The phase fails if a measured job or a
   projection exceeds 3,600 s. No job is allowed to run into a quiet window.
4. **Realistic row counts.** One year at the envelope's caps, cloned from the
   browser fixture's real rows: 4,380 jobs and trials; 365 research datasets
   and as many shadow datasets; 1,000 hypotheses; 5,000 candidates; 110,000
   staging journal rows; 10,000 evidence items; 10,000 workflows, 50,000 tool
   calls and 10,000 artifacts, 2,000 of them candidate reviews; 200
   promotions. A read that misses its budget is a failed phase and is put to
   the owner before any fix. The implementer's default for a fix: an index on
   a table that 0008 creates goes into 0008 in the same pull request; an index
   on an M1–M4 table goes into its own migration and pull request.
5. **Quiet windows on the real clock.** `PilotCoexistence` keeps its small
   stack running from about HH:50 to HH:10 UTC with a short job queued and a
   staging backlog waiting. The harness builds, starts and stops nothing
   between HH:58 and HH:07. The recorded rows must show no job start, staging
   batch, seal, advance or fetch in that interval.
6. **A lost research cluster.** The bridge records the loss once in the
   staging journal and a job request on a lost store is refused when it is
   made. Recovery is an owner command, `tools/research-activate.ps1
   -ReplaceLostStore`: it refuses unless the loss is recorded and the research
   services are stopped, takes a backup, initializes the cluster, registers
   the next store version and never the lost name, and starts the services.
   Staging refills from what main still keeps. Rebuilding older data from the
   weekly dumps stays manual. If this needs a schema change the implementer
   asks before touching migration 0008.
7. **The final regression.** `Regression` also runs the M0–M2 route and unit
   files no M6 phase ran (`test_database`, `test_m1_account`, `test_m1_unit`,
   `test_m2_integration`, `test_m2_completion`, `test_m2_unit`). The four M2
   worker-fault files stay out: `app/market_data` is unchanged since
   `ed9fae3`. A new phase `BrowserRegression` follows `BrowserResearchError`
   in the §10 list and runs `m5.spec.ts`, the approvals and error tests of
   `m4.spec.ts`, `execution.spec.ts` and `foundation.spec.ts` on the run's
   images. Not joined: the M4 pilot browser test, the M2 market specs and the
   M3–M5 performance specs.
8. **The read-only look at the normal app.** The B0 observer approved on
   2026-10-03, unchanged, and one more fixed SELECT in a new script
   `tools/m6-pilot-check.ps1` with the observer's guards: lease, checkpoints
   and counts of experiment events, execution incidents and market incidents.
   No Compose, `.env` or secret is read. "Not disturbed" means every normal
   container keeps its identity, the lease epoch is unchanged and held, the
   forward checkpoint advanced, no new segment, downtime, failure or
   execution incident, no `QUEUE_OVERLOAD` or `COLLECTION_GAP` during the
   phase, and the next SNAPSHOT report in its HH:05 minute. Any difference
   stops the work; the research limits are lowered and the owner is told.

The proposed content of `MixedVersion`, `PilotCoexistence`,
`ResearchActivationRehearsal`, the three performance phases, `SecretScan`,
`Report` and the process-level faults (inside `AgentFaults6`) was accepted
with the same answer; [ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)
records it as built.

Nothing here approves B10, a deployment, an activation, or a profile, an
envelope, a source version or a promotion. The points
[ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks)
leaves from B8 stay as they are.

### 2026-10-07 — Pilot and agent tools: the env-file path, and what was left out

OBSERVED owner instruction in a separate Claude Code session on 2026-10-07, as
a task text that names an independent review of 2026-10-06 as the source of
two findings older than M6:

1. `tools/pilot-activate.ps1`, `tools/agent-activate.ps1` and their
   deactivation counterparts pass the caller's unresolved `-EnvFile` to the
   writer, while every read uses the resolved path.
2. The writer (`Set-EnvFlag` in `tools/lib/Pilot.psm1`) rewrites every line
   end, drops a byte-order mark and is not atomic, and it and the reader
   (`Get-EnvValue`) do not read a key as Compose does.

The instruction: make the four tools read and write their flags through the
resolved path with the reader and writer that `tools/lib/Research.psm1` "now
has" (or move those two functions to a shared module); keep the old functions
only where a caller needs the old behavior; a deactivation never refuses
because of a duplicated key; run nothing against the normal project, because
the M4 pilot runs there; test on isolated files only; update
[OPERATIONS](OPERATIONS.md) and record the commands; deliver a pull request
and do not merge it.

**What the instruction rested on does not hold on `main`.** VERIFIED
read-only: `tools/lib/Research.psm1`, the two functions, the research tools
and `tools/m6/rollout.psm1` are in no commit of `main` (`4ece326`). The module
exists on the local, unpushed branch `claude/m6-b9-final-acceptance` since its
commit `3d10fec`; the reader and the writer exist only in that branch's
working tree. The session that works on that branch, and that had prepared
the task text, said the same in a message to this session and advised against
a second reader and writer, which that branch would have to be merged with.
That message is information from a peer session, not an owner decision.

**What was done first, as this session's own choice inside the instruction.**
Only the part that needs none of that code: the six `Set-EnvFlag` calls of the
four tools take the resolved path. Finding 1 is corrected by it. Finding 2 is
not: the writer and the reader are unchanged, and their limits are stated in
[OPERATIONS](archive/OPERATIONS_M3_M7.md#m4-pilot-operations-execplan-0015).

**Put to the owner, and decided the same day.** After pull request
[MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30)
was opened with the path correction alone, two questions were put to the
owner in this session's question dialog, each with a recommendation. The
owner answered at about 11:52 UTC and took both recommendations:

| Question | Answer |
|---|---|
| **When the reader and writer replace `Set-EnvFlag` and `Get-EnvValue`.** After the B9 pull request is merged, on its code; now, as a shared module on `main` that the B9 branch then adopts; or by the B9 session inside its branch | **After B9 merges.** No second reader or writer is written. Until then the limits stated in OPERATIONS stay |
| **A tool called by its path from a PowerShell session does not stop when the write of a flag fails** (OBSERVED: both deactivation tools ended with exit code 0 while the flags still read `1`; [COMMANDS](archive/COMMANDS.md#owner-tools-write-the-resolved-env-file-2026-10-07)). Correct it in pull request #30; not now; or in a separate pull request | **In pull request #30.** `tools/lib/Pilot.psm1` sets `Stop` for its own functions |

The second answer changes one behavior: an error inside a function of
`tools/lib/Pilot.psm1` now stops the tool also when it is called by its path
from a session, as it always did when the tool was started with
`powershell.exe -File`, which is how the rehearsals and both owner
activations ran. It applies to every tool that uses the module, so also to
`pilot-market-dump.ps1`, `agent-login.ps1` and `m5-deploy.ps1`. The first
answer leaves finding 2 open until a follow-up after the B9 merge; that
follow-up is not started.

The instruction and the answers grant no command against the normal
application, no deployment, activation or merge, and none was made.

### 2026-10-07 — Owner asks to merge the env-file path PR

OBSERVED owner instruction in the same Claude Code session at about 12:58 UTC
on 2026-10-07, after pull request [MentorAliu/adaptive_spot_lab#30](https://github.com/MentorAliu/adaptive_spot_lab/pull/30)
was reported with its results, what was not run and what it leaves
unchanged: "merge it". This lifts the "do not merge" condition for that pull
request only.

`main` was still at `4ece326`, the commit the change was branched from and
checked on, so nothing has to be merged into the branch and nothing has to be
run again. Use an ordinary merge commit pinned to the verified head, without
force, an administrator bypass or branch deletion.

The merge changes files only. A tool is corrected in a checkout once that
checkout holds the merge; the primary checkout is on the M6 B9 branch, which
has to merge `main` for that, keeping both sessions' entries in STATUS,
COMMANDS and this file. The two rehearsals that run the tools against Docker
stay NOT RUN on the changed tools, and the replacement of the writer and the
reader stays for after the B9 merge, as decided above.

The merge grants no command against the normal application, no deployment,
activation or approval, and it is not a batch of ExecPlan 0023.

### 2026-10-07 — M6 B9: what stops a test run beside the pilot, the owner scripts and the pilot's own rows, the schema change in 0008, and the market worker's log

OBSERVED owner answers in the question dialog of the M6 B9 session, at about
13:26 UTC on 2026-10-07. Four questions were put, each with a recommendation,
after the fix round of [ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)
and a read-only series of the real pilot with no test running (161 readings
from 2026-10-06 21:25 to 2026-10-07 13:14 UTC). The owner took the
recommended option each time. The option texts are quoted as they were shown.

| Question | Answer |
|---|---|
| **What should stop an isolated test run while the real pilot is running?** Decision 8 of 2026-10-06 stops a run on any new execution incident or collection gap; with no test running the pilot wrote such rows itself 13 times between 21:25 and 02:46 UTC | **Stop on a burst.** "Stop at once on a container or lease change, a new segment or downtime event, QUEUE_OVERLOAD, a missing HH:05 report, or any execution incident other than PROTECTION_UNAVAILABLE. Record collection gaps and PROTECTION_UNAVAILABLE pairs with time and phase; stop on more than two gap episodes or more than four pairs in thirty minutes. With no test running, the baseline's densest half hour had three pairs and one gap." |
| **Should `tools/m6-deploy.ps1` and `tools/research-activate.ps1` stop when the pilot records a PROTECTION_UNAVAILABLE pair or a collection gap during their run?** | **Report, don't stop.** "The script names such rows by code in its output and record and goes on. Any other new execution incident, and any container, lease, segment or downtime change, still stops it. I change both scripts, their mock scenarios and the rehearsal before the next run." |
| **The year-of-rows API measurement needs three indexes and a stored generated column (`research_datasets.purpose`) on tables that migration 0008 creates. Where do they go?** | **All in 0008.** "0008 has never been applied to the normal database, so nothing is changed after the fact. Your decision 4 already puts the indexes there; the column is what lets the dataset list filter use an index." |
| **May I read the real market worker's log, read-only, to look for why it restarted twice on 2026-10-06 (last start 15:53:57 UTC)?** | **Yes, read-only.** "One docker logs call with a time range on the normal market-worker container, outside HH:58-HH:07. Nothing is started, stopped or changed. The cause is unknown; a restart during B10 would stop the deployment at its last check." |

**What the first answer replaces and what it keeps.** It replaces, in the
"not disturbed" sentence of decision 8 of 2026-10-06, "no new ... execution
incident, no QUEUE_OVERLOAD or COLLECTION_GAP during the phase". The rest of
that sentence stays: every normal container keeps its identity, the lease
epoch is unchanged and held, the forward checkpoint advanced, no new segment
or downtime event, and the next SNAPSHOT report in its HH:05 minute. As
implemented, any change of the experiment's events stops a run, which is
stricter than "a new segment or downtime event": such a change means the
experiment itself changed. A count of PROTECTION_UNAVAILABLE rows that fell
also stops. "More than four pairs" is read as more than eight rows.

**What the answers do not decide.** They relax no pilot budget and no
measurement budget. They approve no deployment, activation, test of the
normal application or change to the market worker. The second answer applies
to the two scripts' own comparison of the real pilot; the harness's
comparison of its fixture pilot inside an isolated stack stays as strict as
it was. The fourth answer allowed one read; it is used
([ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)
records what the log shows). The other points of
[ExecPlan 0023 §19](archive/plans/0023-m6-research-investigations.md#19-open-risks)
stay open, among them the jobs at the 21-day cap and the rule that an
accepted run starts every phase once.

### 2026-10-07 — Market worker: a retention call the database ends must not end the worker (ExecPlan 0024)

OBSERVED owner instruction in a separate Claude Code session on 2026-10-07, as
a task text. It carries a finding read that day from the normal market
worker's log with the owner's approval of one read-only `docker logs` call:
the worker exited twice on 2026-10-06, at 13:51:57 and 15:53:56 UTC, because
the statement timeout ended a call of its hourly retention, and Docker
restarted it.

The instruction:

1. Reproduce in an isolated test that a retention call ended by the statement
   timeout, and separately by a lock timeout, must not end the worker. Decide
   the handling with the code and the M2 contracts: a failed maintenance pass
   that is recorded and retried on the next pass with a smaller batch, without
   closing the stream and without a collection gap, while fencing and the
   retention bound stay intact. A stalled retention stays visible, as an
   incident or a status, never silent.
2. Look at why one call of 500 observations can exceed the statement
   deadline. If an index or another schema change is needed, say so and ask
   whether it goes into its own migration and pull request.
3. Unit and isolated integration tests; no test against the normal app.
4. A pull request that is not merged and not deployed. Deploying to the normal
   market worker needs the owner's explicit approval and the HH:15–HH:45 UTC
   window.

Its limits: no build, recreate, restart or stop of the normal project's market
worker or of any pilot service without the owner's approval in chat; isolated
stacks only; no heavy Docker work between HH:58 and HH:07 UTC; `.env`,
`secrets/` and `codex_home` are never read.

**One premise is not on `main`.** The task text cites "decision 4 of
2026-10-06" for the rule that an index on an M1–M4 table goes into its own
migration and pull request. VERIFIED read-only: that decision is item 4 of the
entry "M6 B9: phase content …" on the local, unpushed branch
`claude/m6-b9-final-acceptance`, where it is the implementer's default for a
fix after a missed read budget. It reaches `main` with that branch. This entry
does not restate it as a decision of its own.

**What follows from it here.** The change of
[ExecPlan 0024](archive/plans/0024-retention-failure-keeps-the-worker.md) is code of
the market worker only and needs no schema change. The "smaller batch" does:
the database function fixes its call size, and nothing the worker's identity
may do changes it. That part, and what the cost measurement found, is put to
the owner in [the plan's §7](archive/plans/0024-retention-failure-keeps-the-worker.md#7-decisions-for-the-owner)
and is not implemented.

The instruction grants no command against the normal application, no
deployment, no merge and no schema change, and none was made.

### 2026-10-07 — M6 B9: a full test at the 21-day cap, and reruns in an accepted run

OBSERVED owner answers in the question dialog of the M6 B9 session, at about
19:10 UTC on 2026-10-07, after the first authoring run of the fix round
(`m6-b9j`) had stalled for two hours on a harness defect. Two questions were
put, each with a recommendation; the owner took the recommended option each
time. The option texts are quoted as they were shown.

| Question | Answer |
|---|---|
| **If tonight's measurement confirms that a full test on 21 days takes longer than the one-hour job bound (inferred: about 5,100 s against 3,600 s), what should I do?** The other options: shorter datasets (the cap lowered from 21 days to what fits the hour), a longer bound for full tests, or to decide only after the measurement | **Fix the replay.** "Change the runner so that each cell is replayed from its own start with its warm-up instead of from the dataset's first row; about two thirds of a 21-day full test is rows read before a cell starts. A product change with tests and a parity check, roughly a day before the acceptance run. I first confirm by reading the code that results stay identical, and come back to you if they cannot." |
| **In the acceptance run, may a phase that fails or is interrupted be started again on the same build?** The other option: every phase must pass on its first and only attempt | **Allow, on record.** "A failed or interrupted phase may be started again on the same build and the same tree. Every attempt stays in the record; the report lists each rerun with its cause, and I put each one to you in the B9 report to accept or reject. The report still refuses a run whose tree changed. Saves about a day each time a phase fails for a reason outside the product." |

**What the first answer is conditional on.** The measurement: decision 3 of
2026-10-06 stays as it is (a measured job or a projection over 3,600 s fails
the phase, and the budget is not changed). If the measurement does not
confirm the inferred figure, no product change follows from this answer. If
it does, the change is the one named, and only if the results of a job stay
identical; otherwise the question returns to the owner. The dataset cap and
the job bound stay as approved.

**What the second answer changes and what it keeps.** It replaces the rule
that `Report` refuses a run in which a phase was started more than once or
has a failed or superseded record. It keeps: one Build, a committed tree, the
tree of every attempt equal to the Build's, every phase VERIFIED in its last
attempt, the secret scan after every other phase. A rerun is not accepted by
`Report`: it is listed with its cause, and the owner accepts or rejects it in
the B9 report.

### 2026-10-07 — M6 B9: a restart of the market worker alone beside a test run, and its log

OBSERVED owner answers in the question dialog of the M6 B9 session, at about
20:17 UTC on 2026-10-07. The pilot watch had stopped authoring run `m6-b9k`
at 20:11:45 UTC, as the rule of that morning says, because the normal market
worker had restarted at 20:01:27 UTC (restart count 2 to 3, same container
and image). The run had no container up and had issued no Docker command
from 19:32:51 to 20:07:00 UTC. Two questions were put, each with a
recommendation; the owner took the recommended option each time. The option
texts are quoted as they were shown.

| Question | Answer |
|---|---|
| **The market worker restarted at 20:01:27 UTC and I have not read why. May I read its log for that restart?** The other options: this once only, or not at all | **Yes, each restart.** "One read-only docker logs call with a time range on the normal market-worker container for this restart, and one for each later restart during B9, outside HH:58-HH:07. Nothing else on the normal app is addressed." |
| **If the log shows the same retention failure as on 2026-10-06, what should a restart of the market worker alone do to a test run from now on? (If it shows anything else, I start nothing and come back to you.)** The other options: the rule stays and the session resumes by itself when the run was idle; the rule stays and every stop waits for the owner; no test run until the retention fix is deployed to the market worker | **Record, stop on a second.** "A restart of the market worker alone (same container and image, count +1; lease, epoch, segments, downtime events and execution incidents unchanged) is recorded with time and phase and reported, and the run goes on. A second restart within three hours stops it. Risk: if a run's own load slowed the delete, that run continues until the second restart." |

**What the second answer changes and what it keeps.** It changes one part of
the first answer of that morning: "a container ... change" no longer stops a
test run when the change is a restart of the market worker alone and its log
shows the retention failure. Everything else in that answer stays: any other
container change, a lease or epoch change, a new segment or downtime event,
QUEUE_OVERLOAD, a missing HH:05 report, any execution incident other than
PROTECTION_UNAVAILABLE, and the two bursts. As implemented, the answer is
read strictly in five places. The log decides each time, and a log that
could not be read counts as "anything else". "The same retention failure"
is exactly one `market_worker_fatal` event with a statement of
`asl_prune_market_evidence` canceled by its statement timeout. More than one
restart between two readings stops. A restart before the watch began counts
as the first of "a second restart within three hours". And "execution
incidents unchanged" is taken as written: a restart that came with
PROTECTION_UNAVAILABLE rows gained since the reading before stops the run,
although such rows alone are only recorded.

**What the answers do not decide.** They apply to test runs. The owner
scripts `tools/m6-deploy.ps1` and `tools/research-activate.ps1` still stop
on any container change, the market worker's among them, as decided that
morning. They approve no change to the market worker and no deployment of
the retention fix, which is the work of
[ExecPlan 0024](archive/plans/0024-retention-failure-keeps-the-worker.md) in another
session (its own decisions are recorded beside these). They relax no
pilot budget and no measurement budget. The log read is one call for each
restart and nothing else on the normal application.

### 2026-10-07 — Market worker deployment approved, then the merge (ExecPlan 0024)

OBSERVED in the Claude Code session that delivered pull request
[MentorAliu/adaptive_spot_lab#31](https://github.com/MentorAliu/adaptive_spot_lab/pull/31),
after its report. At about 20:55 UTC the owner asked: `is this safe to merge ?`
The answer was yes for the merge as such, with a recommendation to deploy
first, as for ExecPlans 0021 and 0022. The owner then wrote: `go ahead`.
Because that could mean the merge or the recommended order, the session asked
once in its question dialog, "Which do you want me to go ahead with for pull
request #31?", and the owner chose at about 21:00 UTC:

> Deploy first, then merge (Recommended): Recreate only market-worker from the
> PR head in an HH:15-HH:45 UTC window (backup, rollback tag :pre-0024, plan
> section 13), watch two hourly retention passes, then merge. I tell the B9
> session beforehand, because a recreate within three hours of the 20:01
> restart would otherwise stop its run.

What this approves:

- the steps of [the plan's §13](archive/plans/0024-retention-failure-keeps-the-worker.md#13-normal-deployment-run-2026-10-07)
  for the market worker alone, with the read-only commands that verify them;
- the merge of pull request #31 once two hourly retention passes have
  completed on the new worker.

What it does not approve: touching postgres, the pilot workers, the API, the
web app or the agent services; a schema change; decisions 1 to 3 of the
plan's §7; removing a rollback tag, an image or a volume of the normal
project.

### 2026-10-08 — M6 B9: research jobs that miss the one-hour bound, and a job's workflow

OBSERVED owner answers in the question dialog of the M6 B9 session, at about
06:25 UTC on 2026-10-08, after `PerformanceResearch` had run to its end for
the first time (run `m6-b9l`, an authoring run) and failed: a screening job
on 21 days, a full test on 14 days and a shadow advance over 14 days each
ended unfinished at the harness's limit of 2,160 or 2,700 s with no cell
complete, the full test after more than 416 s for a replayed day against the
58 s the plan had assumed
([ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)).
Two questions were put, each with a recommendation; the owner took the
recommended option each time. The option texts are quoted as they were shown.

| Question | Answer |
|---|---|
| **Research jobs miss the one-hour bound by a wide margin at the designed dataset sizes. How do you want to proceed with M6-A?** The other options: deploy M6-A inert with `PerformanceResearch` recorded as failed and fix before activation; lower the dataset cap to what fits; or measure first and decide then | **Fix the cost in B9.** "I first measure small jobs to completion to get the real rates, then change the stepping path so the per-quote reads are cached within a batch, with tests that results stay identical, and re-measure. If that is not enough I come back with the next step (starting cells from a saved state; reusing the dataset hash). Product changes, so a new build and run. Adds roughly two to four days; the outcome is not certain until measured." |
| **A research job never records which agent workflow requested it, although the API returns that field (so it is always empty). Fix it now?** The other option: record it as known and fix it in a follow-up PR | **Fix in B9 with a test.** "A small product change at the point where a job is created, with a test, in the same new build that the other fixes need anyway." |

**What the first answer replaces.** The conditional answer of 2026-10-07
("Fix the replay": each cell replayed from its own start with its warm-up).
Reading the code showed that that change alters a job's results, because
two indicators run over the whole history and the stored fingerprints would
differ, and that it saves about 170 s; by its own condition it was not to be
built if results could not stay identical. **What it authorizes:** the
measurement of small jobs, and one product change, the caching of the
per-quote reads within a batch on the replay path, provided a job's results
stay identical and tests show it. **What it does not authorize:** starting a
cell from a saved state, reusing a dataset's verified hash across jobs
(which weakens what the per-job hash proves), any change of the 3,600 s
bound or of the 21-day dataset cap, or any change to how the live forward
engine reads its state. Each of those returns to the owner with the measured
figures.

### 2026-10-08 — M6 B9: the owner asks for the least waiting

OBSERVED owner instruction in chat in the M6 B9 session, at about 08:15 UTC on
2026-10-08, after asking why a running task was said to last until 17:00 UTC:
"do what needs to be done to reduce the massive wait times because I don't
have that much of a time to wait 1 week to finish m6, do whatever it takes to
complete m6 in the least amount of time and correctly".

**How the implementer reads it (the implementer's reading, not the owner's
words).** It asks for less waiting in everything that is the session's own
way of working, and it keeps "correctly". Changed on that reading: isolated
test stacks run side by side where the Docker VM's memory allows it (16
CPUs, about 5 GB free; two heavy stacks at a time), the functional phases of
a new build beside a measurement on another run; no step is run only as a
rehearsal when the same run could count; phase time reservations are to be
set from measured durations; and the research measurement is to run jobs
small enough to complete inside a test window and project 14 and 21 days
from them, against the unchanged bound of 3,600 s, because a job between 45
and 60 minutes can never complete inside a window. **Not changed, because
the instruction does not name them:** the quiet period from HH:58 to HH:07
UTC, the rule that stops a test run when the real pilot is not as it was,
every pilot and measurement budget, the rule that nothing addresses the
normal application before the owner's yes for B10, and the owner's decisions
of that morning on what may be changed in the product. Each of these stays
until the owner says otherwise.

### 2026-10-08 — M6 B9: research job times beyond the one-hour bound are accepted as missed for M6-A

OBSERVED owner answers in the question dialog of the M6 B9 session on
2026-10-08, at about 10:40 and 10:55 UTC, after the first measurements of the
build with the replay batch's reuse of the experiment's state (run `m6-b9p`,
a scratch measurement on isolated containers): a screening job on a 9.6-day
dataset completed in 568 s with valid results, 321 s of it the runner's hash
of the dataset before the first cell, and about 230 s for a day with a
position held, where the build before needed more than 608 s
([ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)).
INFERRED from those figures for the worst case, a candidate that holds a
position almost always: a screening on 21 days about 2,800 s, a full test on
21 days about 5,700 s. Each question had a recommendation; the owner took it
each time. The option texts are quoted as they were shown.

| Question | Answer |
|---|---|
| **A 21-day full test needs about 5,700 s against the 3,600 s bound even with the cache. How should M6-A proceed?** The other options: lower the dataset cap to what a full test fits (about 12 days), or keep going in B9 with a deeper change of the engine's writes | **Deploy inert, fix before activation.** "Accept M6-A with that one measurement recorded as MISSED with its measured figures. Every other phase must still pass on one fresh run. Deploy inert (research stays off). The remaining performance work becomes its own PR and must pass the measurement before M6-B activation. Fastest: acceptance run tonight, deployment plan tomorrow morning." |
| **One point of scope before I build the exception: the shadow advance (the daily forward test of a candidate) misses the same one-hour bound for the same reason, by my estimate over 6,000 s at 14 and 21 days. Is it covered by your decision too?** The other option: only the 21-day full test, with the shadow advance to meet the bound before M6-A is accepted | **Yes, same exception.** "The accepted miss covers the research job times that the stepping cost causes: the full test and the shadow advance at 14 and 21 days. Each is recorded as MISSED with its measured or projected figure, and the performance PR must bring all of them under the bound before activation. Everything else must pass." |

**What this changes.** The owner's rule for B9 that a missed budget is a
failed phase, for exactly four results of `PerformanceResearch`: the full
test at 14 and at 21 days and the shadow advance at 14 and at 21 days. Each
is recorded as missed with its figure and named as accepted by the owner in
the phase's record and in `Report`; none of them fails the run. It replaces
the first answer of that morning ("Fix the cost in B9") for what is left
after the reuse of the experiment's state, which stays in M6-A.
**What it keeps.** The bound of 3,600 s, the dataset cap of 21 days and every
other budget. A screening on 21 days must meet the bound. Every other phase
passes on one fresh run, or M6-A is not accepted. The deployment is inert:
research, sources and their identities stay off. **What it puts before
M6-B.** A separate pull request for the remaining job cost, which must bring
those four results under the bound in the same measurement before research
is activated. Not decided: how that work is done.

### 2026-10-08 — M6 B9: a failed retention call that recovers is reported and does not stop a test run

OBSERVED owner answer in the question dialog of the M6 B9 session on
2026-10-08, at about 13:47 UTC. What was put to the owner first: twice that
day the pilot watch beside a test run noted that an hourly retention call of
the normal market worker had failed and that a later pass had completed
(`RETENTION_FAILED`, then `RETENTION_RECOVERED`): between 09:20:39 and
09:25:41 UTC beside two test stacks, and between 13:24:24 and 13:29:25 UTC
beside the acceptance run `m6-b9r` alone, during its 27-day load. Nothing
else of the pilot had changed at either time. Since the fix of ExecPlan 0024
this failure is an incident and no longer a restart of the worker. The
owner's rule for a test run beside the pilot names restarts and does not
name this incident; the watch notes it and does not stop. At 13:27 UTC the
implementer had told the owner that it would, by hand, stop a run at a second
failed call within three hours, as for restarts, and asked to be told if that
should be otherwise.

The question, as shown: "The normal market worker's hourly retention call
failed again at about 13:26 UTC and recovered within three minutes, this time
beside the acceptance run alone (its 27-day load). Nothing else of the pilot
changed. The next hourly call is at about 14:26 UTC, while the run seals its
datasets, and may fail the same way. What should a failed retention call that
recovers do to a test run?"

The owner chose the first of three options, quoted as it was shown:
**"Report only (Recommended)"**: "A failed call that recovers is recorded with
its time and the phase in progress, and reported to you; the run goes on.
Since yesterday's fix the worker neither restarts nor loses anything: it
retries after a minute, and both failures today were completed within five
minutes. I stop the run at once if a call has not recovered ten minutes later,
on RETENTION_STALLED, and on everything your stop rule already names
(container, lease, checkpoint, segment, downtime, overload, gap burst, missing
report). Cost: the normal database's incident list gains a failed/recovered
pair in some hours while tests run."

The two options not chosen: "Stop at a second in 3 h" (the measure set for
restarts from this cause; the run would have been stopped if the next hourly
call failed) and "Stop the run now".

**What this changes.** The by-hand measure the implementer had announced at
13:27 UTC: a second failed call within three hours no longer stops a run.
**What it keeps.** Every stop the owner's rule already names, as the watch
applies it. A restart of the market worker is still judged by the decision of
2026-10-07. Two heavy test stacks at once are still not used beside the pilot
without the owner's word; that was not asked and is the implementer's own
restraint. **How it is applied.** The watch's code is not changed during the
acceptance run: it already notes these incidents and goes on. The implementer
reads its notes and stops the run by hand when a failed call is not followed
by a recovery ten minutes later, or when `RETENTION_STALLED` appears. Every
failed call beside a run is listed in the B9 report with its time and phase.
**Not decided here:** whether the retention itself is changed so that load on
the host cannot make its first call fail (the open decisions of ExecPlan
0024), and what applies during the B10 deployment, whose script lists market
incidents and judges none.

### 2026-10-08 — M6 B9: M6-A is accepted on what the inert deployment switches on

OBSERVED owner instruction in chat in the M6 B9 session on 2026-10-08, at
about 13:55 UTC, while the acceptance run `m6-b9r` was in its first long
measurement: "I think this implementation is too complicated and time
wasting, I want you to research deeply and propose solution to simplify the
implementation and complete this branch PR".

**What the implementer found, read-only, and told the owner.** OBSERVED from
the branch and from the runs' own command logs:

- The branch is 104 files and 20,208 added lines against `main`. The engine's
  product code is 673 of them, in 14 files. About 13,000 are harness and
  measurement code and 2,400 are documents.
- The last full run (`m6-b9l`) took 11.3 hours for 4.8 hours of commands.
  `PerformanceResearch` and `ResearchSaturation` took 9.2 hours of the
  elapsed time; on the current build the 19 other phases that had run needed
  about 1.4 hours of commands.
- Of 33 failed phase records of B9, by the implementer's count about twenty
  were defects of the harness or of its test code, three to five pointed at
  the product, and the rest were expected or interrupted.
- Neither of those two measurements had passed in any run, nor had
  `PerformanceBrowser`. Their bulk loads were at work beside both failed
  retention calls of that day.

**The proposal, and the owner's answer.** The question, as shown: "How should
I complete the M6 B9 pull request?" The owner chose the first of three
options at about 14:03 UTC, quoted as it was shown: **"Scope to inert
(Recommended)"**: "M6-A is accepted on the 25 phases the inert deployment
depends on, on one fresh run (about 3.5 hours). PerformanceResearch,
ResearchSaturation and PilotCoexistence move to the M6-B activation gate with
the performance pull request. I stop the current run's measurement now.
Acceptance about 6 hours after your yes if nothing fails." Not chosen: "Scope,
but finish measuring" (the running measurement finished first, as a baseline)
and "Keep the full scope".

**What this changes.** The acceptance of B9 in
[ExecPlan 0023 §9](archive/plans/0023-m6-research-investigations.md#9-implementation-sequence-proposed),
which was every phase of §10. M6-A is accepted on `Build`, `Generate`, `Checks`, `Regression`, `Migration`, `MixedVersion`, `EngineParity`, `ResearchRunner`, `HoldoutIsolation`, `Staging`, `ShadowSchedule`, `SourcePolicy`, `EvidenceInjection`, `AgentOffline6`, `DispatcherAuth6`, `AgentFaults6` with its process part, `ResearchActivationRehearsal`, `ApiAuth`, `BrowserResearch`, `BrowserResearchError`, `BrowserRegression`, `PerformanceApi`, `PerformanceBrowser`, `SecretScan` and `Report`: 25 with `Report`.
`PerformanceResearch`, `ResearchSaturation` and `PilotCoexistence` are not
part of M6-A. They are the gate of the M6-B activation: they must pass, on
the build that is activated, before `tools/research-activate.ps1` is run on
the normal application, together with the performance pull request the owner
decided earlier that day. For M6-A, R17 and the budgets of research jobs, of
idle dispatch and of staging are therefore NOT RUN, and Q06 is resolved for
what the inert deployment runs: the API and page budgets.

**Why the implementer proposed it (its reasoning, as given to the owner).**
The inert deployment starts no research or source service; `asl_research` and
`asl_source` stay without login and both flags stay 0. Nothing the three
phases measure can run in the normal application before the activation. The
owner had already accepted four of their results as missed, and the
performance work changes the engine, so they are measured again in any case.

**What the owner gives up, as the implementer said it.** M6-A is accepted
without evidence that the pilot's budgets hold under research load, and
without the staging fix proven at full density; both become conditions of the
activation. The pull request still carries the measurement code, which has
never passed, as the tooling of that gate.

**What it keeps.** One fresh run and one image for the acceptance; every
budget; the bound of 3,600 s for a job and the cap of 21 days; the rules for
the pilot; the record of commands, results and what was not run. The owner's
acceptance of four missed job times stays as decided. It has no row in an
M6-A report now, because the phase that produces those figures is not run for
M6-A; the performance pull request must still bring them under the bound
before the activation.

**Said by the implementer with the proposal, and not asked:** nothing further
is added to the harness, and the record is kept to result tables and
decisions.

### 2026-10-08 — M6 B9: the search budget is a condition of the activation

OBSERVED owner answer in the question dialog of the M6 B9 session on
2026-10-08, at about 14:31 UTC, after a trial of the browser and volume
phases on the stopped run `m6-b9r` (14:08 to 14:22 UTC; isolated containers,
synthetic rows). `BrowserResearch`, `BrowserResearchError` and
`BrowserRegression` passed. `PerformanceApi` failed on one budget: MEASURED,
the analyst's cutoff-filtered search over 10,004 evidence items took 213.36 ms
at p95 (median 68.65 ms) against the declared 150 ms. Its routes were inside
their budgets: 39.12 ms sequential and 168.14 ms with five readers at p95,
against 250 and 500. The search is measured in its worst case since the fix
round of 2026-10-07: 10,000 items with an extract at the registered cap of
16,384 bytes, and queries of one or two plain words, three of them words that
every item holds. On 2026-10-06, with the fixture's short extracts, the same
measurement had read 32 ms. `PerformanceBrowser` could not run: it needs a
passing `PerformanceApi`.

The question, as shown: "The trial found one missed budget. The analyst's
evidence search takes 213 ms at p95 against the declared 150 ms, in its worst
case (10,000 items, every extract at the 16 KB cap, query words that every
item holds). Everything else in that phase is well inside: API routes 39 ms
and 168 ms against 250 and 500. BrowserResearch, BrowserResearchError and
BrowserRegression passed. The search only runs once sources are approved, so
not before activation. How should I treat it?"

The owner chose the first of three options, quoted as it was shown: **"Gate of
activation (Recommended)"**: "Recorded as MISSED with its figure and owed
before M6-B activation, like the research job times. For M6-A the phase judges
the API routes and reports the search figure without failing on it. One more
small harness change, then the trial of PerformanceBrowser (it could not run
yet, because it needs this phase to pass) and the fresh acceptance run,
starting 16:07 UTC." Not chosen: "Fix the search now" (a product change in
this pull request) and "Keep it a failed phase".

**What this changes.** The owner's rule that a missed budget is a failed
phase, for one result: the p95 of the cutoff-filtered search in
`PerformanceApi`. For M6-A that figure is recorded against its budget as met
or missed, shown in `Report` as not judged here, and listed there as owed
before the activation. The budget of 150 ms is not changed. **What it keeps.**
Everything else in `PerformanceApi`: the route budgets, and what makes the
search figure worth reading (10,000 items at the registered extract size, no
failed search, a figure that is there) still fail the phase. **What it puts
before M6-B.** The search must meet 150 ms in that measurement before sources
are activated, with the three phases of the activation gate. Why it is slow is
INFERRED from the query and not measured: it ranks every matching item, and a
query word that every item holds makes that all 8,004 items visible at the
cutoff, each with a search vector of about 166 words. Not decided: how it is
made faster.

### 2026-10-08 — M6 B10: the owner approves the inert deployment, before the merge

OBSERVED owner messages in chat in the M6 B9 and B10 session on 2026-10-08,
after the B9 report and the deployment plan of about 18:30 UTC
([ExecPlan 0023 §18](archive/plans/0023-m6-research-investigations.md#18-completion-evidence)).
At about 19:33 UTC: "is it safe to merge ?". The implementer answered that
merging changes nothing that runs and that the merged tree is the one the
acceptance run tested, with one caveat (until the deployment, `main` would be
ahead of the running schema, so nothing may be rebuilt from it for the normal
application), and named two orders, recommending the first: deploy, then merge
with the deployment record in the same pull request; or merge now and deliver
the record in a second one. At about 19:39 UTC the owner answered: "do your
recommendation".

**How the implementer reads it (its reading, not the owner's words).** It is
the yes for B10 as planned: the inert deployment of the head of pull request
32 to the normal application with `tools/m6-deploy.ps1`, at the next start
the script allows, and then, after the read-only verification and with the
deployment record in the pull request, the merge of that pull request. If the
deployment stops or is rolled back, nothing is merged and it is reported as
blocked.

**A restart found by the read-only look, and the owner's answer.** OBSERVED at
19:40 to 19:42 UTC with the two approved read-only scripts: all nine
containers of the normal application had been started again at 19:38:42 UTC
(the same containers on the same images, restart counts unchanged), the
execution lease had gone from epoch 4 to 5, and one `EXECUTION_DOWNTIME` event
had been added (3 to 4). The lease was held and the checkpoint advancing. No
command of the session ran between 19:33:32 and 19:39:48 UTC. The implementer
did not deploy and asked. The question, as shown: "Before I deploy: all nine
containers of the normal app were restarted at 19:38:42 UTC. Same containers
and images, restart counts unchanged, which looks like Docker Desktop itself
restarting. The pilot recorded it: one new downtime event (3 to 4) and the
execution lease went from epoch 4 to 5. It is running again: lease held,
checkpoint advancing. None of my commands ran between 19:33 and 19:39 UTC. Did
you restart Docker or the PC, and should I go ahead at 20:15 UTC?" The owner
chose, at about 19:45 UTC, the first of three options, quoted as shown: **"I
did it; deploy at 20:15"**: "The restart was yours (for example with the
update). I deploy at 20:15 UTC as planned, record the restart and the new
lease epoch as the starting state, then merge after the verification."

**What this approves.** The deployment of §13.1 and the merge after it. **What
it does not approve.** The activation (M6-B), either flag, either identity,
any approval of an envelope, a source version, a profile or a promotion, any
migration after 0008, and any rebuild, recreation, restart or stop of
`postgres`, `market-worker`, `execution-worker`, `evaluation-worker` or
`pilot-admin`.

### 2026-10-08 — M6 B10: a deployment that stopped in its read-only preflight, and the fix of the deploy script

OBSERVED on 2026-10-08 at 20:15:00 to 20:15:04 UTC: `tools/m6-deploy.ps1`,
started against the normal application on the owner's approval, stopped at
stage `preflight` four seconds after it began: "Cannot convert the JSON
string because a dictionary that was converted from the string contains the
duplicated keys 'clock_uncertain' and 'CLOCK_UNCERTAIN'". It had read the
containers' identities and was reading the pilot's facts. Nothing was changed:
no tag was set, no backup taken, no image built and no container touched
(OBSERVED afterwards: no `:pre-m6` tag, no `m6-deploy-*` directory, and the
pilot tag of the market worker still on its old image).

**Cause.** The script reads the market worker's incident counts by code, for
its report. The normal database holds one code in two spellings, and Windows
PowerShell 5.1 cannot read a JSON object whose keys differ only in letter
case. No fixture held both spellings, so the rehearsal could not show it. It
is a defect of the deploy script, not of the product or of the pilot.

**The question, as shown, and the owner's answer.** "The deployment is blocked
until that one line is fixed. Changing an accepted script is your call. How
much re-checking do you want before I run the fixed script against the normal
app?" The owner chose the first of three options, quoted as shown: **"Fix and
deploy at 21:15 (Recommended)"**: "I change the one line, run the script's own
model test (no Docker, a few minutes) and the parser check, commit, and deploy
at 21:15 UTC. A mistake in the fix can only stop the script again in its
read-only preflight, before anything changes. Then the verification and the
merge, as planned." Not chosen: "Fix, rehearse, then deploy" (the isolated
rehearsal phase on a fresh run first) and "Full acceptance run again". The
answer arrived at about 21:48 UTC, after the start it names: the deployment is
started at the next one the script allows, 22:15 UTC. That is the
implementer's reading of the same instruction.

**What this changes.** One accepted owner script after the acceptance run: in
`tools/m6-deploy.ps1` the market worker's incident codes are counted without
regard to letter case. Those counts are reported and never judged. The
execution incidents, which are judged, are read as they are recorded, and the
rest of the script is unchanged. The product tree is not touched, and the
acceptance evidence of run `m6-b9s` is for the script as it was: the changed
line has the script's model test (17 scenarios, 74 expectations, none failed,
no Docker) and PowerShell's parser behind it, and no isolated run on real
containers. **Not changed:** `tools/m6-pilot-check.ps1`, which reads the
market worker's codes since an instant in the same form and would fail the
same way if both spellings fell into one reading; it has not, in any reading.

### 2026-10-09 — M6-B: the performance pull request: search ranking, the dataset hash, and measuring before deciding the 21-day jobs

OBSERVED owner instruction of 2026-10-09 in a Claude Code session, after the
session had listed what the M6-B activation needs and had said it would bring
a short plan before writing code: `start the performance PR`. The session
then read the profile and the search record kept from 2026-10-08, wrote no
code, and put a plan with three questions, each with a recommendation. The
owner took the recommended option each time, at about 06:40 UTC. The option
texts are quoted as they were shown. The plan is
[ExecPlan 0025](archive/plans/0025-research-job-cost-and-search.md).

| Question | Answer |
|---|---|
| **The analyst's search ranks every matching item, which is what costs 212 ms. May it rank only the newest 500 matching visible items?** | **Rank newest 500.** "Cost stays bounded however large the corpus grows. Hidden items are still removed before selection. A very common word can no longer surface an old item over 500 newer matches. Recorded as a change to the search tool's contract." |
| **The hash every job recomputes costs about 33 s per day of data. May its definition change so the database streams raw rows instead of rendering JSON?** | **New definition.** "Expected about 5 s per day of data (my estimate). It still changes when any stored value changes. Hash values differ from today's; the normal app holds no sealed dataset, so nothing has to be converted." |
| **By my estimate the full test on 21 days and the shadow advances over 14 and 21 days still miss after these changes. How should I proceed?** | **Measure first.** "Build the four changes, run the measurement, then come back with measured figures and one concrete proposal for whatever still misses." |

Not chosen: "Keep ranking all"; "Keep definition"; "Go further now" (a full
test that reuses the two cells its screening already replayed and a shadow
advance that continues from its last mark, built without waiting for
figures); "Prepare staged activation".

**What the plan said the first round holds,** and the owner approved with it:
the new hash; on the replay path only, the three writes of a held second sent
together, cheaper copies of cached state, the research lease renewed by time
and a longer batch for research jobs, with tests that results stay identical
and the forward engine's statements untouched; the search bound; and a harness
that judges the four job times and the search. Isolated runs only, one stack
at a time with the pilot watch; the pull request is not merged until the owner
says so and deploys nothing.

**What the answers do not decide.** They change no bound, cap or budget: 3,600 s
a job, 21 days, 150 ms. They approve none of the design changes that could
close the three job times the session expects to miss; those return to the
owner with measured figures. They approve no deployment and no activation.
The figures in the questions (212 ms, 33 s, 5 s) are one measured search
record, one measured job and the session's estimate; the estimate is INFERRED
until the measurement of ExecPlan 0025.

### 2026-10-09 — The pilot check counts the market worker's codes without regard to letter case

OBSERVED owner instruction of 2026-10-09, in the task given to the session that
made this change. It names what the entry above left open ("Still unfixed:
`tools/m6-pilot-check.ps1`") and instructs: "Apply the smallest fix: group
market incident codes by `upper(code)` in the pilot check's fixed SELECT (the
execution incident codes are judged elsewhere and are recorded in one spelling;
leave them as recorded unless the same risk is shown)." The script says that
its SELECT is the one the owner was shown on 2026-10-06, so: "the changed
SELECT is an owner-visible change, so show the new text in the pull request
description." The instruction also asks for a test without Docker "so that this
class of defect is caught in isolation", for the parser check and the model
tests, and for no command against the normal application.

**What this changes.** The fixed SELECT of decision 8 of 2026-10-06, in one
place. Its market incidents part now reads `SELECT upper(code) AS code,
count(*) AS n FROM market_incidents WHERE occurred_at >= <the given instant>
GROUP BY upper(code)`. In a reading every market incident code therefore
stands under its upper-case name, and `clock_uncertain` and `CLOCK_UNCERTAIN`
are one count. The rule of the watch is not changed: it looks for
`QUEUE_OVERLOAD` and `COLLECTION_GAP`, which the worker writes in upper case
only, and it finds and compares every code without regard to letter case, as
it did before.

**Left as recorded, because the same risk is not shown.** The execution
incident codes: the engine writes six, each as one upper-case literal
(`EXECUTION_DOWNTIME`, `RECONCILIATION_FAILED`, `STEP_FAILED`,
`PROTECTION_UNAVAILABLE`, `RISK_LATCH_DAILY_LOSS`, `RISK_LATCH_DRAWDOWN`), and
the normal database held two of them on 2026-10-08. The experiment event
kinds: the table's own check constraint holds them to a fixed list. The market
worker is different: it also records, as a code, the reason it gives when a
collection cannot go on, and for a clock check that reason is spelled
`clock_uncertain` while the measurement itself is recorded as
`CLOCK_UNCERTAIN`.

**What it does not approve.** Any reading of the normal application: each
`-Execute` of the check or of the watch still needs the owner's approval in
chat. The changed SELECT has NOT RUN against the normal database. The
implementer's reading: the owner accepts the changed text by merging the pull
request that shows it.

### 2026-10-09 — Owner asks to merge the pilot check pull request

OBSERVED owner instruction in the same Claude Code session at about 07:00 UTC
on 2026-10-09, after pull request [MentorAliu/adaptive_spot_lab#33](https://github.com/MentorAliu/adaptive_spot_lab/pull/33)
was reported with its results, what was not run and three points for the
owner: "merge it". This lifts the "do not merge unasked" condition for that
pull request only.

The report had named what the pull request holds beyond the literal task: one
code in two spellings in the deploy model, the two models run by
`ResearchActivationRehearsal`, the entry above and the counts in TESTING, and
one disposable PostgreSQL container that was started and removed. It had
offered to take the first four out of the pull request. The owner asked for the
merge instead, so the pull request is merged as it stands. That is the
implementer's reading of "merge it" after that offer.

`main` was still at `105dd2d`, the commit the change was branched from and
checked on, so nothing has to be merged into the branch and nothing has to be
run again. Use an ordinary merge commit pinned to the verified head, without
force, an administrator bypass or branch deletion.

The merge changes files only. The check is corrected in a checkout once that
checkout holds the merge, and a checkout takes it between test runs, not
during one. The merge grants no command against the normal application: no
`-Execute` of the check or of the watch, no deployment, activation or
approval. The changed SELECT stays NOT RUN against the normal database, and
`ResearchActivationRehearsal` stays NOT RUN as a phase with the two models in
it.
### 2026-10-09 — M6-B: the owner authorizes completing the performance pull request in the shortest possible time

OBSERVED owner messages of 2026-10-09 in the same session, at about 07:17 and
07:20 UTC, while the first isolated run of ExecPlan 0025 was in progress. The
owner asked: `whats after this pr? and how long is going to take to complete
this branch and pr?` The session answered with its estimates, among them that
three job times are expected to miss after the first round and that closing
them is either a design change of about a week or a staged activation. The
owner then wrote: `I authorize you to complete this pr in the shortest
possible time so the app can move to m7`.

**The implementer's reading, stated to the owner in the same reply. It is the
implementer's, not the owner's words.**
- The implementer takes the remaining engineering decisions of this pull
  request itself and does not return for each: which further change is built
  when the measurement shows one is needed, provided a job's results stay
  identical. This replaces the answer "Measure first" of the entry above in
  one respect: the figures are still measured first, and the proposal that
  would have followed them is carried out instead of being put.
- The implementer merges the pull request once it is verified.
- The order of work is the fastest one: a single job on the new build for a
  first figure, and the long measurement once that figure warrants it.

**What the reading does not include.** No bound, cap or budget changes: 3,600 s
a job, 21 days, 150 ms. A job time that cannot be brought under its bound is
reported, and what is measured is not changed to make it pass. The pilot
rules stay: one heavy test stack at a time, the quiet window, the watch and
its stop rule. It approves no deployment, no activation step, no approval in
the UI and no command against the normal application: the M6-B activation
stays a sequence of steps on the owner's instruction
([ExecPlan 0023 §13.2](archive/plans/0023-m6-research-investigations.md#132-m6-b-activation-each-step-on-the-owners-instruction)).

### 2026-10-09 — M7 plan requested (ExecPlan 0026)

OBSERVED owner messages of 2026-10-09 in a Claude Code session opened at about
07:20 UTC. The owner asked: "can m7 be started while the other session is
still active?" The session answered that planning can start beside the other
session, which is at work on the performance pull request, and that code and
test runs should wait for it. It named two points as the owner's: the order of
the milestones, and the pilot. The owner then wrote: "start the M7 plan".

- **What this approves:** writing the M7 plan as a proposal,
  [ExecPlan 0026](archive/plans/0026-m7-agent-driven-main-decisions.md), in a worktree
  and on a branch of its own, read-only against the code.
- **What it does not approve:** implementing the plan; any test run; any
  command against the normal application; any deployment, activation or
  approval; any of the decisions the plan puts to the owner in its §3.3.
  Among those are whether M7's implementation may start before M6 is complete
  (M7-OD1) and when the pilot ends (M7-OD2).
- **Not changed by it:** the M6-B activation stays a sequence of steps on the
  owner's instruction, and the running pilot stays as it is.

### 2026-10-09 — ExecPlan 0026 approved for implementation with the recommended decisions

The plan put eleven decisions to the owner in its §3.3, each with a
recommendation. The session delivered it as pull request
[MentorAliu/adaptive_spot_lab#34](https://github.com/MentorAliu/adaptive_spot_lab/pull/34)
and reported it with those decisions in a table, with the fact that agent
trading can start only after the pilot is stopped, and with which of its last
changes no second reader had seen. The owner answered in chat at about
11:40 UTC: "approve with your recommendations, merge it".

- **Approved for implementation.** [ExecPlan 0026](archive/plans/0026-m7-agent-driven-main-decisions.md)
  (M7) is built batch by batch and verified on isolated stacks, beginning with
  B0 once the performance pull request is merged.
- **The eleven decisions, each as the plan recommends:**
  - **M7-OD1, (a).** M7-A may start before M6 is complete, once the
    performance pull request is merged. Its test runs yield the one heavy
    slot to the M6-B gate runs.
  - **M7-OD2, left open as recommended.** When the pilot ends is decided once
    M7-A is deployed. Nothing before that depends on it, and nothing of M7-A
    touches the pilot.
  - **M7-OD3.** The values of the plan's §5.2 and §5.7 are built in as
    written, among them a daily count of its own for decision work. This is
    not the exact-hash approval of the policy or of `EVALUATION_PROTOCOL_V2`,
    which the owner gives in the UI in M7-B.
  - **M7-OD4, (a).** An approved promotion makes its candidate an entry
    basis, checked by code, inside the policy's own sets.
  - **M7-OD5, (a).** M7 builds the comparison on fixtures, the
    single-coordinator variant and the deferred replay of the reference. A
    selector, live shadow accounts and forward ablations are not in M7; they
    need a plan of their own, which the roadmap does not place yet.
  - **M7-OD6, (a).** The coordinator and the intent reviewer are shown the
    paper account of the policy's own run. It goes to the model provider,
    bound by the runtime profile's data scope.
  - **M7-OD7, (b).** No partial reduction in M7. Acceptance row A21 stays
    open for it.
  - **M7-OD8, (a).** M7 is complete with M7-A deployed, the boundary done,
    the policy approved, the experiment `RUNNING`, the decision probes passed
    and one live decision cycle recorded, for which an abstention is enough.
    The first live submission, fill and outcome review are follow-ups.
  - **M7-OD9.** M6's acceptance rules carry over, and M7-A's acceptance is
    scoped from the start to what the inert deployment and the boundary
    switch on.
  - **M7-OD10, (a).** M6-B comes first, on the M6 build.
  - **M7-OD11, (a).** The policy's hash binds the trading rules and the
    generation-3 definitions; the model is bound by the separately approved
    runtime profile.
- **Implementer.** The owner named none in this answer.
- **Merge.** "merge it" lifts the "do not merge until the owner says so"
  condition for pull request 34 only. VERIFIED read-only first: the pull
  request is open, mergeable and clean, with no check run, and `main` is still
  at `cb4bbd4`, the commit the plan was written from, so nothing has to be
  merged into the branch. Use an ordinary merge commit pinned to the verified
  head, without force, an administrator bypass or branch deletion. This entry
  is written before the merge and does not claim it.
- **Not approved by this:**
  - Any step of the boundary or of M7-B (the plan's §13.2 and §13.3):
    stopping the pilot, installing the definitions, the exact-hash approvals
    of the policy, the protocol, a runtime profile or a promotion, the
    activation, Start, the probes and Enable.
  - Any command against the normal application. The M7-A inert deployment is
    asked for before it runs, as M5's and M6's were, and a read-only read of
    the normal database that B0 wants is asked for first.
  - Any step of M6-B.
  - Checking any acceptance-checklist row; rows are checked only at M8.

### 2026-10-09 — M6-B: the performance pull request is merged without its job-time verdict; what remains is done later and does not hold M7

OBSERVED owner messages of 2026-10-09 in the session of ExecPlan 0025, between
about 16:00 and 16:35 UTC, while the last phase of the verification run was in
progress and then just after the pilot watch had stopped it
([ExecPlan 0025 §14](archive/plans/0025-research-job-cost-and-search.md#14-progress-and-completion-evidence)).
The session had reported that the first job figure on the store of full size
was slower than its scratch measurements, that by its own estimate the shadow
advance over 21 days would still miss the bound, and had asked whether to
merge with that miss reported or to hold the pull request. The owner wrote:
`if it closes earlier, will it break anything, is it worth to merge earlier ?`,
then `can this be done later ? I don't want this to block m7`, and, after the
session had reported the stop and said it would merge, `I want to start m7 as
early as possible`.

**The implementer's reading, stated to the owner in the reply. It is the
implementer's, not the owner's words.**
- Pull request 35 is merged as it stands, with what is verified and what is
  not said plainly in its records.
- What remains is a later pull request: the measurement of the four job times
  on a store of full size, a further reduction if the shadow advance over 21
  days still misses, and the change of the lease renewal that the second
  review led to.
- It stays a condition of the M6-B activation, as the owner decided on
  2026-10-08
  ([entry](#2026-10-08--m6-b9-research-job-times-beyond-the-one-hour-bound-are-accepted-as-missed-for-m6-a)):
  the job times must pass the same measurement before M6-B. It is no
  condition of M7-A's start.

**What the reading does not include.** No bound, cap or budget changes. No
test run is started after the pilot difference of 16:24:56 UTC: whether and
when a heavy test runs beside the pilot again is the owner's decision. No
deployment, no activation step, no approval in the UI and no command against
the normal application.

### 2026-10-10 — M7 B0: the owner leaves the latency read and the two small runs to the implementer, and approves the harness profile

OBSERVED owner message of 2026-10-10 at 11:57 UTC in the project thread of
ExecPlan 0026's B0, answering the three questions of the B0 report (pull
request [MentorAliu/adaptive_spot_lab#36](https://github.com/MentorAliu/adaptive_spot_lab/pull/36)):
`1. decide for me 2. decide for me 3. I approve`. The questions were: (1) may
one read-only query of the normal database read the live step latency; (2)
when may the schema probe and the epoch trial on PostgreSQL 17 run beside the
pilot; (3) may B1 build the M7 harness as a profile of M6's, at the size the
report stated, with its three findings.

**The implementer's decisions on the owner's delegation, stated to the owner
in the reply. They are the implementer's, not the owner's words.**
- **The latency read: yes,** once, as step 4 of the
  [B0 commands](archive/COMMANDS.md#execplan-0026-b0-m7-contracts-and-measurements-2026-10-10)
  gives it, preferably before B2 builds the policy's values in, so that an
  expiry or cadence that does not fit the measured latency is changed as code
  and not as a new policy version (M7-OD3). It is one transaction, `READ
  ONLY`, as the API identity, on the agent tables only, ending in `ROLLBACK`,
  with a 15 s statement and a 200 ms lock timeout. It waits on no pilot
  writer.
- **The two runs: yes, both, in one sitting before B3.** The run on
  PostgreSQL 17 is B3's gate; the schema probe is the first evidence that the
  pinned CLI carries schema v3. Conditions: between HH:07 and HH:58 UTC; not
  while an M6-B gate run holds the heavy slot; one after the other; the feed
  incidents of the Markets page read before and after, and a new
  `QUEUE_OVERLOAD` or `COLLECTION_GAP` after the start ends the sitting and is
  reported. They are not heavy test stacks: each is one container capped at
  one CPU, runs a minute or two and is removed by exact name. This decides
  nothing about when a heavy test runs beside the pilot again; that stays the
  owner's.
- **Who runs them.** The owner on the PC, or a session there on the owner's
  word: a cloud session has no Docker. The results come back as the JSON files
  the commands write.

**The owner's approval.** B1 builds the M7 harness as a profile of the M6
harness (ExecPlan 0026 §10, §18): about 300 to 370 lines of harness code and
430 to 540 of profile data, with a check that M6's profile reproduces today's
values. With it the three findings stand as the report gave them: the heavy
lock stays `.cache/m6/heavy.lock` for both profiles; B1 reshapes
`ResearchActivationRehearsal` for revision `0009`; and the images
`MixedVersion7` starts from are observed on the normal application, read-only,
before B9 needs them. The same report sized the new M7 phases beyond
definitions at about 1,020 to 2,035 lines, most of it `MixedVersion7` and
`BoundaryRehearsal`; the approval is read as covering them at that size, and
harness code well beyond it goes back to the owner before it is written (§10).

**Not decided by this message:**
- Whether B3 keeps the engine's epoch hold or takes §5.5's fallback. It was
  put to the owner on a card of its own.
- Any heavy test run beside the pilot, B1's own acceptance phases among them.
- Any other command against the normal application, any deployment,
  activation step or approval in the UI.

### 2026-10-11 — M7 B1: the owner has B0 merged and leaves the heavy-run timing and the epoch hold to the implementer

OBSERVED owner message of 2026-10-11 at 08:40 UTC in the project chat,
answering the implementer's list of 08:39 UTC in the thread of ExecPlan 0026
(merge pull request 36; answer the two open cards; run the latency read on the
PC): `I done those, merge #36, for the answers chose what's best`. The cards
asked when B1's heavy test phases may run beside the pilot, and whether B3
keeps the engine's permission-epoch hold or takes §5.5's fallback. Pull
request [MentorAliu/adaptive_spot_lab#36](https://github.com/MentorAliu/adaptive_spot_lab/pull/36)
was merged by the implementer on that word at 08:42 UTC.

**The implementer's decisions on the owner's delegation, stated to the owner
in the thread. They are the implementer's, not the owner's words.**
- **B1's heavy phases** (`Build`, `Migration7`, `ResearchActivationRehearsal`,
  `Clean` of the M7 profile) run in the next free heavy slot after any M6-B
  gate run that is waiting for it, under the rules of every heavy run beside
  the pilot: one stack at a time, between HH:07 and HH:58 UTC, with the pilot
  watch (`-Harness m7`) and its stop rule. They run on the PC, by the owner or
  a session there on the owner's word; each `-Execute` of the watch is still
  asked for in chat. This decides nothing about later batches' heavy runs.
- **The epoch hold stays** for B3, on one condition: the run on
  `postgres:17.11-alpine3.24` (B0's step 2) shows, as on 16, that one engine
  stepping alone does not starve a waiting epoch update. §5.5's gate is
  amended accordingly: B0 found that agent commit checks overlapping one
  another starve the update with or without the engine, today and under the
  fallback, so the gate as first written could not tell the hold from the
  fallback, and the fallback would give up the guarantee that no fill commits
  after a revocation. The update keeps a statement timeout and Disable keeps
  its retry. If 17 shows one engine alone starving the update, the choice goes
  back to the owner.

**Not settled by this message.** "I done those" most likely reports B0's steps
on the PC, but no result file had reached the thread when this entry was
written, so those steps stay `NOT RUN` in the records until their files are
read. No deployment, activation step, approval in the UI or command against
the normal application is decided here.

### 2026-10-11 — M7 B2 merged on the owner's word; B0's PC steps run on the PC; B3 keeps the epoch hold

OBSERVED owner messages of 2026-10-11 in the thread of ExecPlan 0026:
- 10:45 UTC, `merge #37`: pull request
  [MentorAliu/adaptive_spot_lab#37](https://github.com/MentorAliu/adaptive_spot_lab/pull/37)
  (B1) was merged by the implementer on that word (`ca09fba`), as B2's records
  state.
- 10:53 UTC, `do whatever is needed`, answering the implementer's note that
  B2's pull request [#38](https://github.com/MentorAliu/adaptive_spot_lab/pull/38)
  held nothing for the owner to decide. The implementer read it as the
  merge of #38 and of nothing else, and merged it (`aea9d60`, 10:55 UTC). It
  is no standing permission: later pull requests wait for the owner as before.
- About 11:00 UTC the owner allowed, on the card, a Claude session on the
  owner's PC in the folder `~\repos\adaptive-spot-lab`, briefed to run B0's
  PC steps only, as COMMANDS gives them, and nothing against the normal
  application. That session found that none of the steps had run (the
  checkout had not fetched B0's scripts), and ran them from a separate
  worktree of `main` at `aea9d60` (`.claude\worktrees\m7-b0`), leaving the
  owner's own folder on its branch.
- 11:09 UTC, `B`, choosing of three ways to watch the feed during the
  sitting: one read-only query of the normal database's incidents, once
  before the runs and once after (B), rather than the Markets page signed in
  by the owner (A) or read by the owner (C). It approves those two reads and
  nothing else against the normal application.

**What the PC session reported (OBSERVED there, 11:10 to 11:14 UTC; the
result files stay on the PC under `.cache\m7\b0\`).** The figures are in
[ExecPlan 0026 §18, B3](archive/plans/0026-m7-agent-driven-main-decisions.md#b3--the-engines-intake-the-checks-until-the-fill-the-limits-and-the-intent-stream-2026-10-11).
On PostgreSQL 17.11 one engine stepping alone, back to back included, never
starved a waiting epoch increment (longest wait 0.104 s), and the epoch read
returned nothing while an increment was in flight. That is the condition the
implementer set in the entry above, so **B3 keeps the epoch hold**. As on 16,
agent holders that overlap one another starve the increment, with or without
the engine; Disable keeps its statement timeout and gains its retry. No new
feed incident appeared between the two reads, and every container, network
and image of the runs was removed by exact name.

### 2026-10-11 — The live token-refresh check: the owner's go-ahead, and why it could not start

OBSERVED owner message of 2026-10-11 at 10:53 UTC in the thread of the
reminder for the check, answering the description of 10:47 UTC there (three
steps on the PC: a model call that refreshes the Codex tokens with the
copy-back recorded, a second call on the refreshed tokens, and a recreate of
`agent-runner` followed by a third call; the recreate named as a Docker
command on the normal application that needs the owner's yes):
`yes go ahead, codex is running`.

**What the go-ahead covered, as the implementer read it.** The read-only
verification of the follow-up in
[ExecPlan 0020 §17](archive/plans/0020-m5-agent-runtime.md#m5-closure-2026-10-03), and
one recreate of `agent-runner` for it on that day. Nothing else: no profile
approval, probe start, Enable, activation step or other command against the
normal application. "codex is running" is taken to mean the Codex application
open on the owner's PC; that is INFERRED, and that application has no part in
the check.

**What was done under it.** Read-only reads of the normal application between
11:03 and 11:07 UTC: its containers, its agent tables through a forced
read-only session, and the host's processes. No command that changes the
application. The recreate was **not** done, because the check could not
start: the agent runtime waits for a new profile and can make no model call
([record](archive/plans/0020-m5-agent-runtime.md#follow-up-after-closure--the-live-refresh-check-first-attempt-2026-10-11)).

**Put to the owner at about 11:07 UTC, not decided when this entry was
written.** When the check runs:
- with M6-B's probe run, where
  [ExecPlan 0023 §13.2](archive/plans/0023-m6-research-investigations.md#132-m6-b-activation-each-step-on-the-owners-instruction)
  step 3 places the new profile and the probes. This is the implementer's
  recommendation and what the implementer follows until the owner says
  otherwise; or
- now, by the owner approving a new profile and starting a probe run ahead of
  the M6-B gate, at the price of a failed probe run and the capability latch
  until a later run passes.

**The owner's next message, 14:53 UTC:** `Continue`. It names neither option.
The implementer reads it as going on with the recommendation, the check with
M6-B's probe run, and said so to the owner in the thread. That is the
implementer's reading, not the owner's words; "now" stays the owner's to say.
A read-only re-read at 14:56 UTC showed the runtime as before: no profile
approved, no probe request and no model call since 2026-10-02.

**Not carried forward.** The approval of the recreate was for the attempt of
2026-10-11. The next attempt asks again.

### 2026-10-11 — Ready pull requests are merged by their thread; M7 B3 merged; the M7 run on the PC waits for the pilot watch

OBSERVED owner messages of 2026-10-11:
- 15:46 UTC in the project chat: `automatically merge PR's that are ready to
  merge`. A standing instruction: it replaces "later pull requests wait for
  the owner as before" in the entry above. The implementer's reading, not the
  owner's words: a pull request is ready when it has no conflict with `main`,
  no open review thread and nothing left for the owner to decide, and its body
  records what was verified and what was not (GitHub Actions does not run on
  the account). The thread that drives it merges it and
  says so in that thread. It decides no deployment, activation step, approval
  in the UI or command against the normal application.
- Under it, pull request
  [MentorAliu/adaptive_spot_lab#40](https://github.com/MentorAliu/adaptive_spot_lab/pull/40)
  (B3) was merged at 15:51 UTC as an ordinary merge commit pinned to its head
  `08b94b3` (`fd70434`).
- 15:46 UTC in the thread of ExecPlan 0026: `do it`, answering the
  implementer's note that the B1 to B3 harness phases had never run on the PC
  and that `.cache\m6\PILOT-DIFFERENCE.txt`, written when the watch stopped
  run `m6-p2a` on 2026-10-09 (`QUEUE_OVERLOAD`, 16:24:56 UTC), needed the
  owner's decision first. Read as: run them, and move the file aside as the
  watch asks before it watches another run.

**What the session on the owner's PC reported (OBSERVED there, 15:47 to
15:53 UTC).** It moved the file aside, kept as
`.cache\m6\PILOT-DIFFERENCE-20261009T162456Z-m6-p2a.txt`, as was done on
2026-10-07, and prepared run `m7-b3a` from `08b94b3` in the worktree
`.claude\worktrees\m7-b0`, with no Docker resource. The desktop app's safety
check refused that session the pilot watch (`tools\m6-pilot-watch.ps1 ...
-Execute`), so no phase started: every heavy run beside the pilot has the
watch and its stop rule. The owner was asked to start the watch, to allow it
for the session, or to leave the run for another day.

**Not decided by these messages.** Whether the test load caused the overload
of 9 October (still not known: the market worker's rows were not read); any
later run's timing beyond the B1 entry's rule for heavy slots.

### 2026-10-11 — The owner starts the pilot watch for the M7 run on the PC

OBSERVED owner messages of 2026-10-11, answering the entry above:
- 16:08 UTC in the thread of ExecPlan 0026, on the card: `I start it`, of the
  options to start the watch themselves (recommended), to allow it for the
  PC session, or to leave the run for another day.
- 16:25 UTC in the project chat: `I just started it and it says Watching the
  pilot beside run m7-b3a`; 16:33 UTC in the thread: `watch started`, so that
  the session on the PC, which reads only the thread, could begin.

The session on the PC then ran the B1 to B3 phases of run `m7-b3a` between
HH:07 and HH:58 UTC, one at a time, under the watch's stop rule (16:34 to
17:45 UTC): seven of eight passed, and `ResearchActivationRehearsal` failed on
a check of B1's harness code, fixed with B4
([ExecPlan 0026 §18](archive/plans/0026-m7-agent-driven-main-decisions.md#run-m7-b3a-on-the-owners-pc-b1-to-b3s-phases-and-the-rehearsals-revision-2026-10-11)).
The watch ended by itself with the run, with no difference file. **Not
decided by these messages:** any later run, which keeps the B1 entry's rule
for heavy slots, and the removal of the run's Docker resources, kept for the
diagnosis.

### 2026-10-16 — The owner gives the OK for M7's B10 in advance

OBSERVED owner message of 2026-10-16, 08:15 UTC in the project chat:
`I give OK from now so make sure to continue`. It answers the coordinator's
post of 08:05 UTC, which listed what remains before M7's thread can close:
the thread builds B6c to B9 and merges each when ready; the owner runs B9's
long final test on the PC beside the pilot watch; and the owner gives an OK
for B10, which installs M7 into the normal app switched off, since any Docker
step on the normal app needs the owner's word.

Read as the owner's word for **B10 as ExecPlan 0026 plans it**: the
[milestone deployment procedure](OPERATIONS.md#milestone-completion-deployment)
with M7 installed and switched off and the pilot untouched, once B9 has
passed. The session on the PC reads approvals only in the thread, so it asks
the owner to say it there before it touches the normal app. **Not decided by
this message:** B9's run on the PC, which the owner starts beside the pilot
watch; switching M7 on, installing a policy, activating a run or changing any
approval, each still the owner's separate decision.

### 2026-10-16 — M7-OD2: the pilot ends early, once M7-A is deployed and probed

OBSERVED owner message of 2026-10-16, 11:12 UTC in the project thread "What
comes after M7": `can you do everything to complete m7 asap`. The M7 thread
then asked on a decision card (11:15 UTC): "End the pilot before its 25
November checkpoint so M7 can switch on sooner?", with the options "End
early" (recommended: "The pilot stops once M7 is deployed and checked; its
checkpoint report is written then, and M7 switches on weeks sooner"), "Wait
for 25 Nov" and "Keep the pilot". The card said that nothing stops on a tap,
that the stop stays the owner's step in the app after M7 is deployed and its
checks pass, and that the fixed reference keeps going as a replay either way.
The owner chose "End early" at 11:16 UTC.

Read as **M7-OD2 (b)** of [ExecPlan 0026](archive/plans/0026-m7-agent-driven-main-decisions.md)
§3.3: the pilot is stopped once M7-A is deployed and probed, and its
checkpoint report is written at that earlier date. The reference continues
only as the deferred replay of M7-OD5.

- **Not decided by this answer:** the stop itself, which the owner makes in
  the UI at the boundary (plan §13.2, step 0) after B10's inert deployment and
  its probes; the boundary's other steps; any step of M7-B. Each still waits
  for the owner's word at that step. The pilot keeps running as it does until
  then, and nothing of M7-A touches it. (On 2026-10-18 the owner moved the
  stop to before the rest of the M7 gate and the application update, with the
  pilot's workers left running until the boundary:
  [the entry of 20:16 UTC](#2026-10-18--the-pilot-stops-before-the-rest-of-the-m7-gate-which-runs-without-the-pilot-watch).)
- **The 2026-11-25 checkpoint reminder** stays set. It reports on whatever
  the pilot recorded, whenever the pilot stopped.

### 2026-10-16 — M7: the owner adds a clearer runtime label and a pre-filled profile form

OBSERVED owner message of 2026-10-16, 11:35 UTC in the project thread "Model
runtime login_required", about the System page's `login_required`: `how to
make it automatic to resolve this so it doesn't appear again ?`. The thread
answered that it cannot be made automatic: the state means the runtime waits
for the owner's approval of a new runtime profile, which every deployment
that changes the agents' definitions requires again, and only the owner gives
it ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md), rule 4 of the repository
instructions). It then asked on a decision card (11:39 UTC): "Add a clearer
runtime label and a pre-filled profile form to M7?", with the options "Add to
M7" (recommended: "Build M7 adds both to its owner-controls batch, which
already changes the Agents page") and "Leave as is". The card said that the
approval stays the owner's either way, and that the label would replace
`login_required` with "needs profile approval" and a link to the Agents page,
while the form would start from the owner's last approved model and reasoning
effort. The owner chose "Add to M7" at 11:49 UTC.

Read as two additions to M7's approved scope, built in **B8c** of [ExecPlan
0026](plans/0026-m7-agent-driven-main-decisions.md) (§17, B8b decision 1),
web only: the System page names a runtime that waits for the owner's profile
approval "needs profile approval" and links to the Agents page; the Agents
page's compose form starts from the latest approved profile's model and
reasoning effort when both are still discovered. **Not decided by this
answer:** who approves, what a profile holds, or any approval. The owner
still composes, reviews and approves each profile; nothing is approved, sent
or started for the owner, and a real sign-in fault is still shown as it is.

### 2026-10-16 — M7-OD10: M6-B finishes after M7-A's inert deployment

OBSERVED owner answer of 2026-10-16, 19:39 UTC in the project thread "Build
M7", on a decision card. The plan's approval of 2026-10-09 had recorded
**M7-OD10 (a)**: "M6-B comes first, on the M6 build". The M7 thread's order of
11:15 UTC that day, after the owner's `can you do everything to complete m7
asap`, put M7-A's inert deployment (B10) first and M6-B after it, which is
option (b). The thread found the contradiction while writing B9c's install
script and asked (19:35 UTC): "Finish M6-B after M7 goes into your app
switched off, instead of before?", with the options "After M7" (recommended:
"B10 installs M7 switched off first; M6-B's fix and timing runs use the M7
build, and you approve one model profile instead of two") and "Before M7"
("M6-B's fix is built on the old M6 code and installed first; B10 and
everything after it wait until M6-B's checks pass"). The card said that
`main` now holds M7, so M6-B first would need a separate M6-only branch and
one extra install, and that the plan already supports switching research on
with the M7 build (R29). The owner chose "After M7" at 19:39 UTC.

Read as **M7-OD10 (b)** of [ExecPlan 0026](archive/plans/0026-m7-agent-driven-main-decisions.md)
§3.3, in place of (a): M7-A is deployed inert first, with research and
sources staying inert as on the M6-A release (`tools/m7-deploy.ps1`, B9c).
M6-B's remainder then runs on the M7 build, before the boundary: the
rewritten lease-renewal fix, its job-time runs on the PC, research switched
on and its probes. M6's completion waits for M7-A, and the M6-B gate phases
must pass on the M7 build.

- **Not decided by this answer:** research's activation, the runtime
  profile's approval, the pilot's stop, the boundary and any step of M7-B.
  Each still waits for the owner's word at that step.

## Agent-driven revision authorization

The owner requested maximum useful automation with non-bypassable rules and authorized a consolidated replacement pack. Interpret this as end-to-end **bounded** agent workflows, not unlimited risk, unrestricted tools, an approval to spend on APIs, or approval to run new strategies in the main account. Keep the original hard-risk proposal pending explicit activation confirmation.

`AGENT_DRIVEN` is an added policy kind, alongside `FIXED` and `ADAPTIVE_SELECTOR`. Under a versioned approved policy, trade decisions need not follow the reference EMA rule; they must still satisfy the declared evidence, management, permission and execution contracts. New tools, sources or parameter/strategy domains require the corresponding owner approval. Exact logical-role responsibilities and runtime details are engineering proposals, not vendor recommendations or established profitable methods.

Full-agent capability is measured against P13–P20 and the acceptance checklist, not called a standardized “5/5” rating. All library and financial settings inherited from v1 remain unless this revision explicitly changes their authority/workflow semantics. Numeric hard-risk ceilings are unchanged.

## 2026-10-15 — M9 roadmap and future implementation handoff

OBSERVED owner request: “ok, let's wrap up m9 roadmap and write it in best practices using official documentation to be implemented with claude code or chatgpt after m8 is completed”. This supersedes the earlier discussion-only restriction **for documentation editing only**. It does not authorize application changes, login, installation, provider calls, source/tool activation, paid services or trading-policy activation.

Record [M9](ROADMAP.md#m9--market-intelligence-and-event-driven-adaptive-paper-trading) after completion of M0–M8, including M8 acceptance and verified normal-local deployment. [ExecPlan 0027](archive/plans/0027-m9-market-intelligence-and-event-driven-trading.md) is the deferred implementation handoff; the implementer must refresh it against the actual post-M8 tree and obtain an implementation instruction before beginning application work. No current milestone is declared complete by this decision.

The requested scope combines efficient approved API/RSS/page collection with a background intelligence agent that still performs bounded web research. It covers the six discussed categories: crypto news, economic calendar, selected macro/financial news, price-movement investigations, original announcements and selected SEC filings. Coverage should extend beyond BTC/SOL keywords, while the approved tradable universe remains BTC/SOL spot, long-only paper trading. This is not a promise to obtain every paid Benzinga item for free.

The intended behavior is autonomous entry/hold/exit consideration when approved criteria match, rather than an obligatory hourly decision schedule. Holding periods can differ between trades. The objective is better after-cost outcomes and risk management, not maximum trade count. M9 must explicitly reconcile existing scheduling constraints, policy limits and approval boundaries, preserve original position mandates and keep financial authority/protection in code. Any successor policy or scope expansion follows the existing approval contracts.

Include the agreed enhancements: current-state revalidation, source provenance and corrections, uncertainty/abstention, bounded priorities and resource budgets, full decision/no-action/outcome records, compact UI, point-in-time evaluation with matched baselines and honest failure/coverage reporting. Reuse existing agent roles where suitable. Claude Code/ChatGPT are authoring clients; this decision does not change the application runtime provider or enable unrestricted native browsing. Conditional execution plans remain an optional later enhancement requiring their own design and approval.

## 2026-10-16 — M9 refinements and separate M10 discovery specification

OBSERVED owner instruction: “continue editing now”, followed by continuation after a usage-limit interruption. This authorizes the discussed roadmap/documentation edits. It does not authorize application implementation, runtime changes, additional asset/source activation, spending, login, migrations or deployment. The owner clarified that using agents fully means **the application's agents**, not delegating this authoring research to additional agents.

Keep M9 after accepted/deployed M8, with a subsequent implementation instruction. Refine [ExecPlan 0027](archive/plans/0027-m9-market-intelligence-and-event-driven-trading.md) to include active evidence gathering, bounded review/follow-up, separate assessment dimensions, token-benefit uncertainty, code-calculated relative features, evidence-backed working memory and outcome-driven research. Preserve the six information categories and event-driven entry/hold/exit goal. Success is better evidence and measured after-cost decisions under approved risk, not maximizing activity or promising profit.

Record [M10](archive/plans/0028-m10-coin-discovery-and-controlled-expansion.md) after M9 acceptance/deployment and a separate implementation instruction. Stage A discovers/researches assets; Stage B adds controlled paper-universe expansion. M9 remains independently deliverable for BTC/SOL. This is a future design decision, **not approval to collect or trade particular new coins**. Before behavior exceeds current scope, explicitly reconcile root instructions, PROJECT P02, acceptance A01 and all affected canonical contracts; preserve their historical approvals and evidence.

The initial engineering proposal is a dedicated discovery workflow under ANALYST authority, reusing existing researcher/evaluator/coordinator roles and shared evidence. Its specialization, stopping rules and resource use must be evaluated against simpler approaches. A distinct fifth role, provider, process or agent per coin is not an owner requirement. Discovery/watchlisting, technical eligibility, owner universe approval, strategy approval and a valid trade decision remain separate; model recommendations grant none of these permissions.

Use official documentation and primary research for source, orchestration and evaluation claims, with dates and limitations in [REFERENCES](archive/contracts/REFERENCES.md#m9m10-agent-and-discovery-research--2026-10-16) and [INTEGRATION_EVIDENCE](archive/contracts/INTEGRATION_EVIDENCE.md#m9m10-design-refinement--2026-10-16). Current implementation facts must be refreshed at each future milestone's B0. No source price/quota, numeric policy value, model accuracy or financial return is invented by this specification.
