# ExecPlan 0045 — Where the results come from: a luck floor, an exit replay, the cost of each trade and the buy/sell split

**Status: APPROVED by the owner on 2026-10-27 at 21:09:40 UTC ([DECISIONS](../../DECISIONS.md#2026-10-27--four-checks-from-the-rai_trading-research-planned-as-one-update-execplan-0045)): "Yes, approve and build". Part 0 (this plan) done; part 1 built and tested in the cloud on 2026-10-27, and installed on the owner's PC on 2026-10-28 at 10:09 UTC (§14). What remains is §9's reading, once a check leaves too few.** At 19:04:55 UTC the owner had chosen "Plan them as one update". Written by the project thread "Research r/ai_trading" from `main` at `f950fd6`. It is a part of M11 ([ExecPlan 0039](0039-bitcoin-futures-on-paper.md)). Four checks, all in code, that say how much of the trader's result comes from its entries, its exits, its costs and luck, and whether Binance's buy/sell split of volume carries any information. The update adds no model call, data source, host or dependency. It changes no money path, limit, protection, policy, cost, prompt or generation.

Labels: `OBSERVED` (seen in code, records or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `NOT RUN`. Every number in §4 is a `PROPOSED` engineering default, declared before any result and never tuned on one.

## 1. Goal

The owner asked on 2026-10-27 at 15:01 UTC, in the project thread "Research r/ai_trading": "research reddit subreddit ai_trading posts and comments and check what other people are using that could benefit the app". The thread downloaded all 58,480 posts of the subreddit and its 35,991 comments through a public archive from the owner's PC. Code screened every post; about 230 posts were read in full. The verdict ([docs/ideas](../ideas/ai-trading-reddit.md)): the subreddit shows no proven AI trading edge, and most of what it recommends the app already has. Four of its methods are missing here, and each is code only.

At 17:26:59 UTC the owner asked "is there anything that the app can leverage ?". At 19:04:55 UTC they picked **"Plan them as one update"** on the card "Turn the best Reddit ideas into an app update?". The option read: "I write the plan for the four checks. You approve it before anything is built, and it reaches your PC as one update you double-click."

Observable outcome:
1. **A luck floor.** Home says whether the trader's entries beat 1,000 sets of random entries that use the same exits, on the same days, after costs. Until 30 entries it says **too few**.
2. **An exit replay.** Home compares the trader's chosen stop, take profit and time exit with every other exit generation 10 allows, replayed on the same entries. It also shows what the trader's own early exits and stop tightenings gained or lost in R. Any "better exit" claim must be picked on the first 30 entries and then win again on the next 30.
3. **The cost of each trade.** Trades shows each closed trade's fees, slippage and funding as a share of what the trade risked at its stop. Home shows the average, the result before and after costs, and how many of the trader's entries the `TREND_GATED` twin's cost gate would have refused.
4. **The buy/sell split.** The perpetual's feed stores the taker buy volume Binance already sends with every candle. Home says whether bars with more buying were followed by better longs than bars with more selling, labeled **too few** until 30 days.
5. Nothing reaches the trader, the reviewer or the coach, and nothing changes a rule. Showing any of this to an agent would be a later generation with its own ExecPlan, on the owner's word, and only if a check finds something beyond luck.

What it will probably show, said before it runs: the entries sit inside the luck floor; costs take a fifth to a third of each trade's risk; no other exit wins again on the second 30 entries; and the buy/sell split shows no link beyond the noise at 30 days. A result either way is the finding.

## 2. What the app has

`OBSERVED` at `f950fd6`:
- **The trader**, generation 10 ([ExecPlan 0044](0044-a-trader-that-commits.md)), from 2026-10-27 13:00 UTC. It says `UP` or `DOWN` at each decision. It enters at `MEDIUM` or `HIGH` confidence with a stop of 2.0 or 3.0 times the 15-minute ATR, a take profit of 1, 1.5, 2 or 3 times the stop's distance or none, and a time exit of 4, 12 or 24 hours (`FUTURES_POLICY_V1`'s sets, narrowed by 0044 §4.1). The engine sizes each entry to at most 0.25% of equity lost at the stop, fees and slippage included (`app.futures.money.size_entry`). The first generation-10 entry came at 13:15 UTC: entry fees of 2.21 USDT on a risk of 24.72 USDT.
- **Costs**, `FUTURES_COST_V1`: a 0.05% taker fee per fill, a 1 bps slippage scenario per fill on top of the five-level walk of the book, and funding every 8 hours from the settled rate.
- **Fact sheets** ([ExecPlan 0040](0040-trade-reviews-and-a-coach.md) §4.1, `app.agents.trade_facts`). Each closed position has one `TRADE_FACT_SHEET_V1` in `trade_fact_sheets`, hashed and never changed. It holds the fills with their distance from the top of the book, the fees, the funding, the risk, net R, the worst and best price in R, and the spread at entry and at exit. The reviewer, the coach and 0040's scoreboard read it. The scoreboard already splits trades by side, stop multiple and what ended them.
- **Decision scores** ([ExecPlan 0043](0043-score-every-decision.md), `app.futures.scoring`, `app.agents.decision_scores`). Every decision, every finished 15-minute bar and every twin entry is scored 15 minutes, 1 hour, 4 hours and 24 hours later, on 1-minute candles. The candle model is `scoring.walk`: the stop first when a minute touches both stop and target, a minute that opens beyond either fills at its open, and a time limit at the open of the first minute at or after it. `scoring.model_trade` prices one unit with both fees, the slippage scenario and the settled funding, and gives R against the loss at the stop with costs. An `EXIT` is labeled `EARLY_EXIT`, `GOOD_EXIT` or `NEUTRAL_EXIT` from holding's advantage over exiting (`scoring.held`), and a `TIGHTEN_STOP` is labeled `SAVED`, `SHAKEN_OUT`, `NOT_HIT` or `NOT_APPLIED`. The scorer runs in the agent worker's scheduler pass, at most 20 subjects a pass, each in a savepoint. It stores `INCOMPLETE` after seven days. `DECISION_SCORING_V1` is seeded into `execution_definitions` with its hash.
- **The twins and the league table** ([ExecPlan 0041](0041-twins-and-a-veto.md), `app.futures.twins`, `league`). `TWIN_SET_V1`'s cost gate refuses an entry whose stop distance per unit is under 3 times the round trip's cost per unit. That cost is two taker fees and two slippage scenarios on the entry price, plus the quote's spread. `app.evaluation.bootstrap` is the seeded stationary block bootstrap. Part 2 (the veto agent) is approved and not built; it holds generation 11 and migration `0027`.
- **The feed** (`app.perp.market`, `feed`, `store`). It stores every 1-minute candle of the BTCUSDT perpetual in `perp_bars`: open, high, low, close, volume, quote volume, trades. A final candle is never changed (migration `0019`'s guard). The stream parser reads `o`, `h`, `l`, `c`, `v`, `q` and `n` (`market.py:269`); the REST parser reads indexes 0 to 8. Binance also sends the taker buy volume (stream field `V`, REST index 9, §7), which the app drops.
- **[EVALUATION](../EVALUATION.md)** declared a placebo control for entries and an exit what-if on 2026-10-17 as `PROPOSED` analyses for a later plan to version. Neither has run.

## 3. Scope

In: `RESULT_CHECKS_V1` (§4.1); the bar outcomes (§4.2); the four checks (§4.3 to §4.6); the taker buy volume in the feed and in `perp_bars`; migration `0027`; Home's card, Trades' cost column and the checks' line in Settings (§4.8); the contracts of §5.

Out, each for later on the owner's word:
- Showing a check's result, the cost share or the buy/sell split to the trader, the reviewer or the coach (a new generation).
- A cost gate on the trader's own entries (a policy change).
- Random entries for the twins.
- More data from Binance: open interest, long/short ratios, liquidations (a new source, item 8 of the research page).
- Repeating a decision to measure the model's spread (it uses the Codex allowance).
- Changing a fact sheet that already exists.

## 4. Design

### 4.1 `RESULT_CHECKS_V1` (code)

A code-owned document (`app.futures.checks`, kind `FUTURES_CHECKS`), seeded into `execution_definitions` with its hash by migration `0027`, as `DECISION_SCORING_V1` is. The builder and the daily job start only when the stored row equals the code. Every result records the hash. It declares each value of §4.2 to §4.6: the exit grid, the candle model, the seeds, the counts, the statistics, the minimums and the reading rules. A new version is an update the owner installs.

### 4.2 The bar outcomes (code)

`futures_bar_outcomes` has one row for each finished 15-minute bar since the first futures run started, oldest first. It is built when the 24 hours after the bar are final.
- **The reference** is the bar's last 1-minute close.
- **ATR15(14)** comes from the trader's own features at the bar (`futures_context.features`, as the scorer reads it).
- **The bar's taker buy share** is the sum of its 15 minutes' taker buy volume over their volume. It is null when any of those minutes lacks the value or the volume is zero.
- **For each side and each of the 30 exits** of generation 10's set (stop 2.0 or 3.0 ATR × take profit none, 1, 1.5, 2 or 3 × time exit 4, 12 or 24 hours), the row stores the modeled trade: its end (`STOP`, `TARGET`, `TIME_LIMIT`), net R, cost R, and whether a minute touched both the stop and the target.

The model is `scoring.model_trade` with a take profit and a time limit: one unit at the reference, with the slippage scenario against the side; the stop at the multiple × ATR from the entry fill; the target at its multiple of the stop's distance; `scoring.walk` from the next minute; both taker fees; and funding at each settled time crossed. R is net over the loss at the stop with both fees and slippage, as scoring computes risk. Cost R is the fees, the slippage and the funding paid, over that risk. Everything is in exact Decimal and per unit. The leverage cap, the quantity's step and the tick are left out, and the row says so.

A bar whose candles or ATR are missing waits. After seven days it is stored `INCOMPLETE` with the reason, as the scorer does. Rows are written once and never changed.

### 4.3 Check 1: the luck floor (entries against random entries)

- **The window** holds the entries of the trader's current generation, from its first decision, across runs. A new generation starts a new window, and the old window's last result stays readable.
- **An entry's bar** is the bar its decision saw. For a `BAR` trigger that is the decision's bar. For `SHARP_MOVE` or `FILL`, it is the newest finished bar before the decision's context time.
- **An entry counts** once every bar of its UTC day is stored, with its outcomes or `INCOMPLETE` (on the first run's first day, from the bar that closes at its start). Entries count in fill order, so one that waits holds the later ones, and the exit pick is made on the first 30 (amended at build, §13).
- **The trader's side of the comparison** is the outcome at its bar for its side, stop, take profit and time exit. That is its entries as chosen, on the candle model, without its early exits.
- **A random stream** gives each trader entry a bar drawn uniformly from the same UTC day's stored bars, a side by a fair coin, and the entry's own stop, take profit and time exit. There are 1,000 streams, seeded from the definition's hash, the generation and the window's newest entry. Random entries may overlap; R is summed per entry.
- **The statistic** is total net R. The percentile is the share of streams whose total is below the trader's, ties counted half.
- **The secondary row**, labeled so, is the same with the trader's own side: timing alone.
- **Reading:** at the 95th percentile or above, **above the luck floor**. At the 5th or below, **below the luck floor**. Otherwise **inside the luck floor**. Under 30 entries counted, **too few**.

### 4.4 Check 2: the exit replay

- **Other exits.** For each entry in the window and each of the 29 other exits of the grid, Δ is that exit's net R minus the chosen exit's, both from the bar outcomes.
  - Before 30 entries, each exit's mean Δ is shown as **too few to pick**.
  - At the 30th entry, code picks the exit with the highest mean Δ over entries 1 to 30, ties going to the earlier exit in the grid, and stores the pick.
  - **The check** is the pick's mean Δ over the entries after the 30th. It comes with a 95% interval from the stationary bootstrap (mean block 5 entries, 2,000 resamples, seeded as §4.3). It reads **too few** until 30 such entries exist. The reading is **better beyond luck** when the interval is above zero, **worse** when below, and **no difference shown** otherwise.
  - This one pick and one check replace 29 separate tests, so a winner by luck in the first half has to win again in the second.
- **Early exits and tightenings.** These come from 0043's 24-hour scores of the window's `EXIT` and `TIGHTEN_STOP` decisions that the engine applied. The check counts each label and sums the advantage of what the trader did over holding, converted to its position's R (per unit × quantity ÷ risk). A positive total means the trader's own exits gained. No new replay is needed.
- **Calibration.** For entries that ended by stop, take profit or time exit with no early exit or tightening, the check shows the fact sheet's net R minus the candle model's chosen exit (mean, lowest, highest). This is how far the candle model sits from the book fills, and the card says so.

### 4.5 Check 3: the cost of each trade

The check runs on closed positions of the trader and the two trend twins. The hold twin has no stop, so it has no share of its risk: its costs are shown as an amount (amended at build, §13).
- **Costs** are the fees, plus the slippage against the top of the book on both fills (quantity × the fill's distance from the best level it took; a liquidation on the mark has none), plus the funding paid net of the funding received.
- **The cost share** is costs ÷ risk. **R before costs** is net R plus the cost share.
- **Planned at entry** (the trader only, from its fact sheet) is the round trip of `TWIN_SET_V1`'s gate: two taker fees and two slippage scenarios on the entry price, plus the entry's spread, over the risk per unit. The gate **would have refused** an entry when its stop distance per unit was under 3 times that round trip. This measures the trader's entries; it gates nothing.
- **The window's rows:** the count, the mean cost share, the mean R before and after costs, and the entries the gate would have refused, also split by stop multiple and by side.

Everything is computed at read from stored rows. No fact sheet changes.

### 4.6 Check 4: the buy/sell split

- **The feed.** The stream parser reads `V` and the REST parser index 9 into `Bar.taker_buy_volume`, stored in `perp_bars.taker_buy_volume`.
  - A missing value, a negative one or one above the candle's volume is stored as null and logged (the first and every 60th). The candle itself is never refused, so the new field cannot stop the trader's data.
  - Candles stored before the update keep null. They are final and are never changed.
- **The check.** It uses the window's bars with a taker buy share, from the first such bar.
  - The bars are split into thirds at the window's 33rd and 67th percentiles of the share.
  - The bar's outcome is the long's net R minus the short's at the reference exit: stop 2.0 ATR, take profit 2, time exit 4 hours, the first generation-10 trade's choice.
  - The statistic is the mean outcome in the top third minus the mean in the bottom third.
  - Its 95% interval comes from the stationary bootstrap over the bars in time order (mean block 16 bars, 4 hours; 2,000 resamples; seeded), with the thirds' bounds fixed.
- **Reading:** under 30 UTC days of bars with a share, **too few**. When the interval is above zero, **more buying was followed by better longs**. When it is below zero, **more buying was followed by better shorts**. Otherwise, **no link shown**. Each third's share of bars whose long paid is shown beside the base rate.

### 4.7 When it runs, and what it costs

- **The bar outcomes** are built in the agent worker's scheduler pass, after the scorer. At most 20 bars are built a pass, each in a savepoint, and only when no trader decision is queued or open. The trader's slot comes first, as in [0040 §4.6](0040-trade-reviews-and-a-coach.md#46-when-they-run-and-what-they-cost).
- **The daily results** are computed once a UTC day from 00:20 UTC, under the same rule. They are stored in `futures_check_results`: one row per day with the definition's hash, the window, the four results' document, its canonical form and SHA-256, and `DONE` or `FAILED` with the error's class. A failure is logged and tried again in the next pass. The last result stays shown with its date.
- **No model call.** The work is bounded: about 96 bar rows a day; and once a day, 1,000 streams and two bootstraps of 2,000 resamples.

### 4.8 The pages

UI work loads the shadcn skill and uses the project's discovery. It keeps preset `b2fms61Bqi` and reuses the preset's components. No new dependency.
- **Home:** a card "Where the results come from", below the scorecard. It has four rows, each with its reading, its count and **too few** where it applies:
  - entries against random entries (the percentile and the secondary row);
  - exits (the pick and its check, or each exit's mean Δ while too few; the early exits' and tightenings' total in R; the calibration);
  - costs (the mean share, R before and after costs, the gate's would-have-refused count);
  - the buy/sell split.
  - The card's labels are `PAPER`, `MODELED ON 1-MINUTE CANDLES`, `HINDSIGHT` and `NOTHING HERE CHANGES A RULE`.
- **Trades:** a "Costs" column with each closed trade's cost share of its risk, and fees, slippage and funding on hover or focus, for the trader and the twins.
- **Settings:** in the scorer's card, the checks' last run, its state, and the oldest bar still waiting for its outcomes.

## 5. Authority

- **The checks are code's.** No agent reads, writes or is shown any of them, and the trader's context does not change.
- **The feed change is a data path.** A failure in the new field stores null and never refuses a candle (§4.6, R2).
- **No money path changes:** not the ledger, the reservations, `account_state`, the risk gate, the fills or the protection. Rule 13's money-path review is therefore not required. A separate read-only reviewer still reads the feed change and the checks' arithmetic, because the readings rest on them.
- [AUTONOMY_MATRIX](../../AUTONOMY_MATRIX.md), [AGENT_TOOL_CONTRACTS](../AGENT_TOOL_CONTRACTS.md) and [RUNTIME_AGENTS](../RUNTIME_AGENTS.md) do not change.
- [DATA_CONTRACTS](../../DATA_CONTRACTS.md), [API_CONTRACTS](../../API_CONTRACTS.md), [FRONTEND](../../FRONTEND.md) and [EVALUATION](../EVALUATION.md) change with the code. EVALUATION's placebo and exit what-if are versioned here for the futures trader.

## 6. Requirements and tests

| ID | Requirement | Test |
|---|---|---|
| R1 | The stream and REST parsers read the taker buy volume exactly; it is stored in `perp_bars` and in an open candle's replacement | Unit tests on recorded payloads; database test of the upsert |
| R2 | A missing, negative or too large value is stored null and logged; the candle is still stored and the feed's state is unchanged | Unit and database tests |
| R3 | The trader's context and its hash are byte-identical before and after the migration on the same rows | Database test |
| R4 | Each bar outcome equals a hand-computed fixture for each end (stop, target, time limit, a gap through the stop, both touched), with fees, slippage and funding; a bar waits on a missing candle and is `INCOMPLETE` after seven days; rows are written once | Unit tests with candle fixtures; database tests of the guard |
| R5 | The luck floor's 1,000 streams are reproduced from their seed; same-day bars, a fair side, the entry's own exits; the percentile, ties and readings at their thresholds; **too few** under 30 | Unit tests |
| R6 | The exit pick is made once at the 30th entry and stored; the check reads only later entries; the interval is reproduced from its seed; the early-exit total matches 0043's stored advantages; the calibration matches fact sheets | Unit tests; a database test with seeded decisions, scores and sheets |
| R7 | Each trade's cost share, R before costs and planned round trip equal hand-computed fixtures for a long and a short, a funding time paid and one received, a liquidation and a twin; the gate's count is at the threshold exactly | Unit and database tests |
| R8 | The buy/sell split's thirds, statistic, interval and readings are exact and reproducible; **too few** under 30 days | Unit tests |
| R9 | The builder and the daily job start no work while a trader decision is queued or open; a failure leaves the last result and is retried; nothing is written by the API or a model | Scheduler tests with a fake clock; role-grant tests, positive and negative |
| R10 | Home's card, Trades' column and Settings' line show each state (a reading, **too few**, waiting, failed), by keyboard and in the accessibility tree | Component tests; the browser suite on seeded fixtures |
| R11 | Migration `0027` up, down and up on a scratch database; the downgrade refuses once a bar outcome exists (fix forward) | Migration tests |
| R12 | Every relative link resolves | `python3 tools/check_links.py .` |

## 7. Official sources

No new library, host, data source or model.
- Binance's USDⓈ-M futures documentation, read on 2026-10-27:
  - The [Kline/Candlestick stream](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#kline-candlestick-streams) lists `V`, "Taker buy base asset volume", and `Q`, "Taker buy quote asset volume", in the `k` object, beside `v`, "Base asset volume".
  - [`GET /fapi/v1/klines`](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data) lists index 9, "Taker buy base asset volume", and index 10, "Taker buy quote asset volume".
  - Both are on the streams and the endpoint the feed already uses (0039's evidence in [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md)).
- The bootstrap is Politis and Romano (1994), already in `app.evaluation.bootstrap`.
- The shadcn registry for the preset is read at build time for the components the pages use.

## 8. Data and trust boundaries

- No new host, secret, volume or network path.
- The new stored data is the taker buy volume per candle, the bar outcomes (about 96 rows a day) and one result row a day. All of it is kept with the market data and the trades, and in every backup.
- No model-authored text is added. The taker buy volume is exchange data, checked like the candle's other numbers, and it never refuses a candle.
- The checks are hindsight on modeled trades, labeled so. They are never a fill, a ledger entry or a reason code acts on.

## 9. Implementation sequence

0. **Part 0, documents** (2026-10-27): this plan; [DECISIONS](../../DECISIONS.md), [STATUS](../../STATUS.md), [ROADMAP](../../ROADMAP.md), the [docs index](../../README.md), the [ideas note](../ideas/ai-trading-reddit.md) and 0041's renumbering (§13).
1. **Part 1, one update, after the owner approves this plan:**
   - the feed change and migration `0027` (the column, the view's new last column, the two tables, the definition);
   - the builder;
   - the four checks;
   - the API;
   - the pages;
   - the contracts;
   - the independent review (§5);
   - the checks of §10;
   - then the owner's double-click of `update-app.cmd`.
   
   The thread then reads the first bar outcomes and the first daily result read-only on the PC.
2. **The reading.** When a check first has enough entries or days to leave **too few**, the thread reads it on the PC read-only and reports it to the owner with its labels. A change to the trader from a reading would be its own ExecPlan.

## 10. Verification commands

The commands of [COMMANDS](../../COMMANDS.md): the web checks (lint, types, unit, build), Ruff, the OpenAPI drift check, pytest without a database and on a scratch PostgreSQL, the browser suites on seeded fixtures, the update model and the link check. Results are recorded in §14.

`NOT RUN` in the cloud and left to the update or its check on the PC: the Docker build, the feed against Binance (the cloud cannot reach it), the builder's and the daily job's times on the PC, and the first real outcomes.

## 11. Failure and rollback

- **The feed's new field fails:** the value is null and the candle is stored. **The builder or the daily job fails:** it is logged and retried, the last result stays, and Settings says so. **A bar has missing candles:** it waits, then is stored `INCOMPLETE`.
- No path here moves money or protection.
- Rollback: the update's rollback tags bring back the previous images. Migration `0027`'s downgrade drops the two tables, the view's column and the column, and refuses once a bar outcome exists (fix forward). The update's backup keeps the records.

## 12. Q01–Q10

All apply.
- Q01 and Q02: the card's, the column's and the line's states in a real browser, by keyboard and in the accessibility tree (R10).
- Q03: R1 to R9.
- Q04: no new secret or host; the new field is validated (R2).
- Q05: waits, `INCOMPLETE`, retries and the trader's slot (R4, R9).
- Q06, budgets declared before measuring: a bar's outcomes are built within 200 ms on the PC (logged above it); the daily job finishes within 30 s; Home's card answers within 300 ms; Trades' column adds at most 100 ms to its read.
- Q07: every cloud suite.
- Q08: Settings' line and the API's state.
- Q09: the migration and its downgrade (R11), and the update's backup.
- Q10: the contracts of §5 and `RESULT_CHECKS_V1`'s hash.

## 13. Decision log

| Date | Decision | Why |
|---|---|---|
| 2026-10-27 | One update, code only: no generation, prompt, model call or new source | The owner's pick; nothing reaches an agent until a check finds something beyond luck |
| 2026-10-27 | Migration `0027`; ExecPlan 0041's part 2 moves to migration `0028` and keeps generation 11 | This plan is built next if approved; it takes no generation ([0041 §13](0041-twins-and-a-veto.md#13-decision-log)) |
| 2026-10-27 | One stored grid of outcomes per bar serves the luck floor, the exit replay and the buy/sell split | One fill model for both arms of every comparison, built once a bar and read cheaply |
| 2026-10-27 | Entries are compared on the candle model from their decision's bar, not on their book fills | Random entries have no book fill; the calibration row shows the gap |
| 2026-10-27 | Random entries keep the day and the trader's own exits; the side is a fair coin, with the trader's side as a secondary row | The same market days and the same exits, so only the entry is random |
| 2026-10-27 | Exits are picked on the first 30 entries and checked on the later ones | 29 exits tested at once would find a winner by luck |
| 2026-10-27 | Early exits are measured from 0043's scores, not replayed again | They already price holding against exiting at every applied `EXIT` and `TIGHTEN_STOP` |
| 2026-10-27 | The cost share is computed at read; fact sheets stay as they are | A sheet is hashed and never changes, and the reviewer's input stays the same |
| 2026-10-27 | A bad taker buy value is stored as null; the candle is never refused | A new, optional field must not be able to stop the trader's data (rule 11) |
| 2026-10-27 | The buy/sell split's reference exit is stop 2.0 ATR, take profit 2, time exit 4 hours | Generation 10's first trade's choice, fixed before any result |
| 2026-10-27 | At build, after the independent review: an entry counts once every bar of its UTC day is stored, in fill order, and one that waits holds the later ones (`RESULT_CHECKS_V1`'s window, hash `5c924ba6…013e40`) | Bars are built a day after they close, so at 00:20 the previous day's bars were mostly missing and an entry on that day drew its random entries from a part of its day; the exit pick is made on exactly the first 30 |
| 2026-10-27 | At build: the hold twin's costs are shown as an amount (fees, slippage and funding), with no share | §4.5 said only its fees; its funding is its main cost, and with no stop it has no risk to divide by. The contracts say the same |
| 2026-10-27 | At build, after the independent review: migration `0027` locks `agent_read.futures_bars` before changing `perp_bars` | The agents read the view, then its table; taking them in the same order keeps an agent's read during the update from a deadlock with the migration |

## 14. Progress

- 2026-10-27 15:01 UTC: the owner's ask. The subreddit was downloaded and read; the research page was delivered, and a second reading pass followed the owner's question at 17:26:59 UTC. At 19:04:55 UTC the owner picked "Plan them as one update". This plan was written (part 0). Nothing is implemented or run.
- 2026-10-27 21:09:40 UTC: the owner picked **"Yes, approve and build"** on the card "Approve the plan for the four checks and build it?" (APPROVED). The option read: "I merge the plan, build and test the update in the cloud, and tell you when to double-click update-app.cmd."
- 2026-10-27, part 1 IMPLEMENTED by the same thread from `main` at `18e6d26`, as §9 lists:
  - the feed reads `V` and REST's index 9 (`app.perp.market`) and stores them (`app.perp.store`, `app.perp.feed`);
  - migration `0027_result_checks` (the column with the market worker's `UPDATE` on it, the view's last column, the two tables and their guard, and `RESULT_CHECKS_V1`, hash `5c924ba6…013e40`);
  - the builder and the daily job (`app.agents.result_checks`, in the agent worker's scheduler pass after the scorer, `app.agents.workflows`) and the four checks (`app.futures.checks`);
  - the API: `GET /v1/futures/checks` and each trade's `costs`, for the trader and the twins (`app.futures.check_views`);
  - the pages (`src/futures/checks.tsx`): Home's card, Trades' "Costs" column and the line in Settings' scorer card, from the preset's `Item`, `Tooltip`, `Button`, `Badge` and `Card`;
  - the contracts: [DATA_CONTRACTS](../contracts/DATA_CONTRACTS.md#migration-0027_result_checks-execplan-0045), [API_CONTRACTS](../contracts/API_CONTRACTS.md#execplan-0045-where-the-results-come-from), [EVALUATION](../EVALUATION.md#where-the-results-come-from-execplan-0045), [FRONTEND](../contracts/FRONTEND.md#execplan-0045-where-the-results-come-from), [INTEGRATION_EVIDENCE](../contracts/INTEGRATION_EVIDENCE.md#execplan-0045-where-the-results-come-from--2026-10-27) and [COMMANDS](../../COMMANDS.md).
- 2026-10-27, found by the tests during the build: the feed's replacement of an open candle (`ON CONFLICT DO UPDATE`) needs `UPDATE` on the new column, which 0019's column-by-column grants do not give. Without it the market worker's every open candle would have failed after the update. Fixed with the grant in `0027`; test R1 checks it.
- 2026-10-27 ~22:10 UTC, the independent review (§5), read-only, by a separate reviewer on the feed change, the grants, the update's order and the arithmetic of the four checks: **no blocker**. Its findings:
  - **Should-fix, fixed:** an entry counted as soon as its own bar had outcomes, so at 00:20 an entry of the previous day drew its random entries from the few bars of that day built so far, and the exit pick could skip an entry still waiting. An entry now counts once every bar of its UTC day is stored, in fill order, and one that waits holds the later ones (§4.3, §13; the definition's window says so, hence the new hash). Tests: `test_r5_an_entry_counts_once_every_bar_of_its_day_is_stored_and_one_that_waits_holds_the_later_ones` (unit) and `test_r5_the_entry_counts_once_its_day_is_stored_from_the_bar_that_closes_at_the_runs_start` (database).
  - **Minor, kept and recorded:** the hold twin's costs show its slippage and funding as well as its fees (§4.5 amended, §13).
  - **Minor, fixed:** the migration took `perp_bars` before `agent_read.futures_bars`, the reverse of an agent's read; it now locks the view first, in the upgrade and the downgrade (§13). At worst it had made one agent read fail during the update.
  - Checked and found right: the parsers and their nulls, the upsert, the grants, the view, the downgrade, the update's order, the bar outcomes against the scorer's model, the luck floor's percentile and seeds, the exit pick and its bootstrap, the early exits, the calibration, the costs and the gate, the buy/sell thirds and bootstrap, and the daily job's snapshot and gates.
- 2026-10-27, VERIFIED in the cloud on the final tree, on a scratch PostgreSQL 16 (127.0.0.1:55452) with SYNTHETIC rows only ([COMMANDS](../../COMMANDS.md)):
  - Ruff `All checks passed!`; `FastAPI OpenAPI schema matches`; `python3 tools/check_links.py .` 0 broken links.
  - pytest without a database: `2 failed, 1071 passed, 463 skipped, 420 errors`, the baseline's two failures (both need a database) and database cases only.
  - `tests/test_m11_*.py` on a fresh database `asl_m1_m6_c45b`: `318 passed` in 6 min 23 s (`test_m11_checks_unit.py` 34, `test_m11_checks_db.py` 12).
  - Migration `0027` up, down and up on that fresh database; on an older scratch database whose stored definition was the earlier hash, the downgrade refused ("checks definition mismatch; downgrade refused"), and the database was made again.
  - Web, from `apps/web`: `pnpm run typecheck`, `pnpm exec eslint . --ignore-pattern '.output/**'`, `pnpm run check`, `pnpm run api:check` and `pnpm run build` pass; `pnpm exec vitest run` `317 passed` in 37 files (`checks.test.tsx` 9).
  - Browser, the preinstalled Chromium on a fresh `asl_m1_m6_c45_browser` seeded by `tests.m11_browser_fixture seed` with the SYNTHETIC feed running: `reviews.spec.ts` 5, `local-time.spec.ts`, `pages.spec.ts` and `twins.spec.ts` 15, `scores.spec.ts` 4 and the new `checks.spec.ts` 3 passed (27). The Home card at 390 and 1440 px and the Costs tooltip on hover and focus, by keyboard and in the accessibility tree (R10).
  - Q06, OBSERVED on the cloud's CPU and not the PC: 73 bars' outcomes built in 3.8 s with the test's setup (about 50 ms a bar, budget 200 ms); the daily compute on a SYNTHETIC 90 days of bars and 300 entries took 1.40 s (luck floor), 0.08 s (exit replay) and 3.83 s (buy/sell split), within the 30 s budget. The split's bootstrap grows with the window's bars; each result stores its `elapsed_ms`, and the PC's are read after the install.
  - The whole engine suite on a fresh database `asl_m1_m6_c45_full`, started at 22:10 UTC on the tree before the review's fixes (its M11 part is superseded by the run above): `5 failed, 1875 passed, 74 errors` in 53 min 38 s. The 74 errors are the baseline's (`test_m1_account.py` 13 and the research store's 61). Failures:
    - `test_api.py`'s status test is the baseline's.
    - `test_m6_schema.py`'s downgrade and two `test_m7_schema.py` downgrades were refused by `0027` ("checks definition mismatch"): the run's database held the earlier definition, which the review's fix changed while the run went on.
    - `test_m3_throughput.py::test_quiet_stretches_leave_what_one_publication_at_a_time_leaves` failed while the M11 run and the browser stack ran beside it.

    The three files again on another fresh database `asl_m1_m6_c45d` on the final tree: `1 failed, 79 passed`. The one failure is `test_m6_schema.py`'s downgrade, for the baseline's reason: other databases on the cluster hold objects of `asl_research`, whose role it drops. It reached that point through `0027`'s downgrade.
- NOT RUN in the cloud, left to the update and its check on the PC: the Docker build, the feed against Binance (the cloud cannot reach it), the builder's and the daily job's times on the PC, the first real bar outcomes and the first daily result.
- 2026-10-28 09:28:49 UTC: the owner wrote "done" in the thread while the card "Publish the four-checks update so you can install it?" was open; it was taken as the go-ahead and the card closed as "Yes, publish it". The chart dark mode (PR #139) was merged first, at 09:29 UTC, and installed and checked by its own thread (09:33 to 09:37 UTC), so that two updates never ship in one double-click. Then `main` was merged into this branch (the web checks again: `322 passed` in 38 files; typecheck, eslint, Prettier and the build pass), and PR #138 was merged at 09:41 UTC (`d6eccdb`).
- 2026-10-28, the owner's double-click of `update-app.cmd`. OBSERVED read-only on the PC at 10:11 to 10:20 UTC, in a session that changed nothing (its SQL ran with `default_transaction_read_only=on`):
  - The record `update-20261028T094210Z\update.json`: `COMPLETE`, 09:42:03 to 10:09:50 UTC, commit `d6eccdb` (from `717436f`), the migration `0026_committed_trader` to `0027_result_checks` in one attempt. Nine services were replaced: api, web, the market, execution, evaluation and agent workers, agent-egress, agent-runner and source-fetcher. Its own checks: schema `0027_result_checks`, reconciliation `OK`, `/`, `/trades`, `/decisions`, `/markets` and `/settings` answering 200, the agents `ENABLED` with their check `PASSED`, no problem. The backup `asl.dump` is 28,634,360 bytes.
  - Every container runs and is healthy, the market worker has no health check, and PostgreSQL was not recreated.
  - The stored `RESULT_CHECKS_V1` is `5c924ba6…013e40`, as the code.
  - The taker buy volume is on every candle from 10:06 UTC, the first the new market worker finalized (started 10:06:46), the open one included. None before it has one: a final candle never changes. The market worker logged no missing value, no `Traceback` and no `ERROR`.
  - The builder's first passes, from 10:08:43 UTC: 172 bar outcomes, all `SCORED`, from the 15:00 bar of 2026-10-25 (the first run's start) to the 09:45 bar of 2026-10-27, the newest past its 24 hours. None failed or was incomplete.
  - The first daily result was stored at 10:08:47 UTC: day 2026-10-28, `DONE`, `elapsed_ms` 9. The agent worker logged no `_failed`, `Traceback` or `ERROR`.
  - The trader kept deciding: 6 `DECISION` workflows `SUCCEEDED` in the 90 minutes to 10:13 UTC, the newest decision at 10:00:16 UTC.
  - Home in a browser on the PC shows "Where the results come from" directly below "What followed the decisions", with no console error:
    - Entries against random entries: 0 of 30, **Too few**.
    - Exits: 0 of 30, **Too few**.
    - Costs: 3 closed trades. "Fees, slippage and funding took 19.1% of a trade's risk on average: -0.0074 R a trade before costs and -0.1987 R after." The twins' cost gate would have refused 0 of 3.
    - Buy/sell split: 0 of 30 days, **Too few**.
    - The four labels.
    - The footer: "Worked out 28 Oct, 11:08:47 on 0 entries since 27 Oct, 14:15; 3 more wait until every bar of their day has its outcomes".
  - Trades answers with its "Costs" column, and Settings answers.
  - Q06 on the PC: the daily job 9 ms against 30 s. The bar outcomes' time per bar is not in the log, so the 200 ms budget is NOT RUN on the PC: 172 bars were built within the first minutes after the worker started.
- Still to come (§9 step 2): generation 10's 3 entries since 2026-10-27 count once every bar of their days is stored: those of 2026-10-27 in the daily result of 2026-10-29. Each check is read and reported when it first leaves **too few**.
