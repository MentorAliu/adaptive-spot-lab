# ExecPlan 0051 — Backtest the rule twins on Binance history

**Status: APPROVED by the owner on 2026-11-03 ([DECISIONS](../../DECISIONS.md#2026-11-03--backtest-the-rule-twins-on-binance-history-execplan-0051)). Part 0 (this plan, the pre-registration) written before any backtest ran; §14 records each run.** Written by the project thread "Backtest the rule twins on history" from `main` at `429a0cc`. Research, on the owner's word: an offline replay of fixed rules on public history. It adds no model call, host, service, migration or dependency to the app, and changes no money path, limit, protection, policy, cost, prompt, twin or generation. The running trader and its paired reading due 2026-11-16 are untouched.

Labels: `OBSERVED` (seen in code, records or official pages), `PROPOSED`, `IMPLEMENTED`, `VERIFIED`, `MODELED` (a simulation choice where history lacks what the app sees live), `NOT RUN`.

## 1. Goal

The owner asked on 2026-11-03 at 08:19:21 UTC, in the project chat: "Can the implementation be tested based on timeframe from previous time frames, for example if i select the timeframe 2023 january to february or march based on the binance candles, without seeing the results, want to let the system simulate for example with 10k usdt how would it perform? Whats that called and is it a good idea?" The coordinator answered that it is a backtest, a good idea for the rule twins and a weak one for the AI trader (its model may remember 2023, and two months of 15-minute decisions are about 5,800 calls), and recommended backtesting the rules on several years of Binance candles from 10,000 USDT with real fees and funding. At 08:20:40 UTC the owner wrote in this thread: "Yes, the dates i mentioned were used as an example, you decide what would be best for this case, also I want to see all the results".

Observable outcome:
1. A pure, offline simulator (`app.futures.backtest`) that runs `TWIN_SET_V2`'s rule twins minute by minute on Binance's public archive of the BTCUSDT perpetual, through the twins' own functions (`app.futures.twins`, `app.futures.money`) with `FUTURES_POLICY_V1` and `FUTURES_COST_V1` unchanged, each account starting at 10,000 USDT.
2. The runs of §4.4 on the windows of §4.3, measured by §4.5's pre-registered measures, written to one results file with the data's checksums and the code's commit.
3. A results page for the owner: equity curves, a table per year and per quarter, each rule against holding BTC, the costs, and the verdict in plain words. All results are shown, the development window's and the stress run's too.

What it will probably show, said before it runs (the thread's expectation, an opinion): holding wins the bull years and loses 2022; the 1-hour trend rule, with its 2 ATR stop on 15-minute candles and a 24-hour time exit, trades often for little and pays a fifth or more of each trade's risk in costs, so it ends near or below 10,000 in most years (principles 1 and 8, TR-04, TR-07); the gated trend rule trades less and loses less; the weekly momentum rule swings like holding, beats it in 2022 and lags it in steady rises (TR-02); no rule clears §4.5's adjusted pass. A result either way is the finding.

## 2. What the app has

`VERIFIED` on `main` at `429a0cc`:
- **The rule twins** ([ExecPlan 0041](0041-twins-and-a-veto.md)): `TWIN_SET_V2` in `app.futures.twins` (hash `ff907a4a…2c29` per the twins' record), run by `app.futures.twin_engine` once a second on the PC. `HOLD`: long once at the first finished 15-minute bar, the whole wallet at 1x, no stop, no latch. `TREND`: the 20/50 EMA cross of complete 1-hour candles (the newest contiguous run, at most 720 hours, warm after 100), read at each finished 15-minute bar; an entry on a cross of the hour that finished last at any of the next hour's four bars, sized by `money.size_entry` at 1x with a 2.0 × ATR15(14) stop, no take profit and a 24-hour time exit; an exit at a bar whose last hour's fast EMA is against the side; the policy's cooldowns (2 bars after a stop, 1 after another exit), 24 entries a UTC day, the 2% daily-loss and 8% drawdown latches, and the drawdown stop once flat. `TREND_GATED`: `TREND` plus the 3 × round-trip cost gate and the 0.03% funding filter. `TREND_VETO`: `TREND` whose entries the veto agent may skip or halve, silence letting them in. `MOMENTUM_1W`: at the first finished bar of each UTC day, long if the last complete day's close is above the close 8 days before it, short if below, the whole wallet at 1x, exits only on a flip.
- **The costs** (`FUTURES_COST_V1`): taker 0.05% a fill, a 1 bp slippage scenario on the walked five-level book, funding every 8 hours at the settled rate on the settled mark, Binance's isolated-margin liquidation with tier 1.
- **The league table** (`app.futures.league`): paired daily log-return differences with the seeded stationary bootstrap of `app.evaluation.bootstrap` (mean block 3 days, 2,000 resamples, 95%).
- **The feed's candles** are Binance's own 1-minute klines of the perpetual (`app.perp.market`, `fapi.binance.com`); the twins build 15-minute, 1-hour and daily candles from them (`app.perp.bars`).
- **What is not there:** no history older than the feed's seven days, no backtest, and research is off in the agent worker since [ExecPlan 0035](0035-a-simpler-app-that-trades-by-itself.md#42-research-off-in-the-agent-worker). This plan starts no agent work.

## 3. Scope

In: the archive reader (§4.1), the simulator (§4.2), the runs (§4.3, §4.4), the measures (§4.5), the command-line entry point, tests, the results file, the owner's results page, and this plan's records (DECISIONS, REFERENCES, TRADING's record table once read).

Out:
- **The AI trader.** Its model's training text includes these years and their prices, so it may recall outcomes (TB-01, TR-21; [TRADING](../../TRADING.md#what-not-to-propose)), and a replay would spend thousands of calls of the shared allowance.
- **The veto agent's answers**, for the same reason. `TREND_VETO` without its answers is `TREND` (silence lets every entry in), so its rule part is measured as `TREND`; only the answers' two-minute delay before a fill is left out.
- Anything in the running app: no service runs the backtest, no page reads it, no table holds it. Showing results in the app is a later step on the owner's word.
- Tuning: no value of `TWIN_SET_V2`, `FUTURES_POLICY_V1` or `FUTURES_COST_V1` is changed, tried or searched; no new rule is tested.

## 4. Design

### 4.1 The data

Binance's public data archive, `https://data.binance.vision/data/futures/um/` (§7): for BTCUSDT, the monthly 1-minute klines (`klines/BTCUSDT/1m`), the monthly 1-minute mark-price klines (`markPriceKlines/BTCUSDT/1m`) and the monthly funding rates (`fundingRate/BTCUSDT`), each zip with Binance's SHA-256 `.CHECKSUM`, from the first month published to 2026-10; daily files for a month whose monthly file is not out yet. The instrument's filters (tick, steps, minimum notional) come from the public `GET /fapi/v1/exchangeInfo`, read once. No key, no sign-in, no private endpoint.

The cloud's network policy refuses Binance's hosts (proxy `CONNECT` 403 for `data.binance.vision` and `fapi.binance.com`, 2026-11-03 08:24 UTC, as recorded for 2026-10-17 in [INTEGRATION_EVIDENCE](../../INTEGRATION_EVIDENCE.md)). The owner's PC reaches them: a device session there downloads the files into the git-ignored `.cache/backtest-data/` of the owner's folder (kept out of every image by `.dockerignore`), checks every checksum, and the thread copies them to the cloud, where the backtest runs. No Docker command, no app container and no database is involved; the download does not touch the app.

The reader (`app.futures.backtest_data`) is strict: every row has the documented columns, exact decimal prices with at most 8 places, minute-aligned UTC milliseconds (microseconds are refused unless exactly divisible), no two different rows for one minute; a header row is skipped; anything else stops the run with the file and line. Every file's SHA-256 must equal Binance's `.CHECKSUM`. A minute the archive lacks stays missing, as it would in the feed: no candle is guessed.

**Days a monthly file leaves out** (amended on 2026-11-03 after the development run's first read of the data, before any test-window run, on the data's completeness alone): the monthly files lack whole days that Binance publishes as daily files: the trade klines' 2026-10-28, and the mark's 2021-07-01, 2021-07-24 to 07-27, 2022-07-31, 2022-10-02, 2023-02-24, 2026-06-29 and 2026-10-28 to 10-29 (15,895 mark minutes and 1,440 trade minutes in all; the other gaps are 29, 24 and 2 minutes). Without them the backtest would treat an archive's hole as a feed outage: no protection and no entry for a day, and the trend rule's 100 hours of warm-up again after it. The daily files of those days are read too, each with its checksum; a minute both a monthly and a daily file hold must be identical, or the run stops. OBSERVED on 2026-11-03 08:51:59 to 08:52:13 UTC on Mentor's PC: Binance publishes 9 of those 12 days as daily files (1,440 minutes each, every checksum OK); the trade klines' 2026-10-28 and the mark's 2026-10-28 and 2026-10-29 answer 404 in the daily archive too, while the days around them exist. Those minutes stay missing, and the run treats them as the live twins treat a feed outage: nothing is filled without a quote, no liquidation is checked without a mark, no entry is made on a stale quote or mark, and the trend rule waits for its warm-up again. They fall in the test window's last week, and the results count them.

### 4.2 The simulator (code)

`app.futures.backtest` steps one account per twin through each minute, in the live step's order (`twin_engine.TwinWork.advance`), calling the twins' and the account's own functions for every rule and amount: `twins.trend`, `twins.momentum`, `twins.against`, `twins.cross_side`, `twins.cost_gate`, `twins.funding_refused`, `twins.size_whole`, `twins.size_hold`, `twins.book_left`, `money.size_entry`, `money.atr`, `money.exit_fill`, `money.beyond_liquidation`, `money.liquidated`, `money.funding_delta`, `money.cooldown_end`, `money.pnl`, and `app.execution.risk.daily_reference`. Exact Decimal throughout; the price arrays are integers in units of 10⁻⁸ so nothing passes through a float.

In each minute, for each twin:
1. **Funding.** A position open at a funding time's minute owes that time's funding: `funding_delta` on the settled rate and the mark-price kline's open at that minute (`MODELED`: the archive's funding file has no mark; the live account takes the settled rate's mark). Payments the free wallet covers are posted; the others wait, counted in the value as owed, and are tried again after each fill and funding time, as the live account's rule says. A funding time without a settled rate in the archive stays pending, nothing guessed, and is counted.
2. **Protection at the minute's open.** Liquidation if the mark's open is at or beyond the liquidation price; a stop if the minute opens beyond it (a gapped open fills there); the time exit at the first minute at or after it; an exit the rule asked for that waited for a quote.
3. **The rule** at a finished 15-minute bar, at the next minute's open, as the twin reads it within the bar's first minute: the hold twin's one entry, the momentum twin's day signal, or the trend rule's exit and entry with its checks, cooldowns, day's limit, latches, gate and funding filter. A refused entry is spent or not by the twin's own rule (`RULE_CODES`).
4. **Protection inside the minute.** The stop if the minute's low (a long) or high (a short) reaches it, filled at the stop's level; else liquidation if the mark's low or high reaches its price. The stop is checked first because it lies nearer than liquidation (the policy's liquidation buffer). A minute that touches both the stop and an entry made at its open counts the stop, as the placebo and the scores do.
5. **Valuation, the day's reference and the latches** at the minute's close mark, as `TwinWork.value` does; the drawdown stop ends the twin once it is flat, and it stays flat for the rest of the window.

`MODELED` where history lacks what the live account sees:
- **The quote.** The archive has no order book. A minute's quote is bid = the minute's open, ask = bid + one tick, one level as deep as the market order's maximum quantity, so every fill walks one level and takes the slippage scenario on top, as live. A stop fills at its level (bid for a long, ask for a short), or at a gapped open.
- **Time.** The live step runs each second; here each minute, with the candle's high and low standing for the seconds inside it.
- **The funding filter's rate.** Live, the mark stream's announced rate; here the last settled rate before the minute (no look-ahead).
- **The instrument's filters** are today's for every year.
- **Missing minutes** have no quote and no mark: nothing is filled or valued in them, as in a feed outage, and the trend rule's run restarts after a missing hour, as live.

Each run ends with the live wallet check per account: the start plus realized P&L, less fees, plus posted funding, equals the cash; the reserved margin equals the open position's. A difference stops the run.

### 4.3 The windows (pre-registered)

- **Development window:** every minute before 2022-01-01 00:00 UTC that the archive holds, the accounts starting at the first UTC midnight from which all three series exist: 2020-01-01, the archive's first monthly file of each (§14). Used to build and check the simulator end to end. Its results are reported, labeled development.
- **Test window:** 2022-01-01 00:00 UTC to 2026-11-01 00:00 UTC, 58 months: the 2022 fall, the 2023 recovery, the 2024 rise and what followed. Run **once**, after the simulator is frozen at a commit recorded in the results. If a bug is found after that run, the fix and the new run are recorded as a second trial beside the first, both shown.
- **Fresh starts:** every calendar year (2020 to 2025, and 2026 to 31 October) and every calendar quarter (2020 Q1 to 2026 Q3, and October 2026) as its own set of accounts from 10,000 USDT, like the owner's example. History before each start is visible to the rules, as the live twins see the feed's past. Those inside the development window are labeled so.
- **The regime** of a quarter is BTC's change from its first minute's open to its last minute's close: `RISE` at +15% or more, `FALL` at −15% or less, `SIDEWAYS` between; of a year, ±30%. It reads the price only, never a twin's result.

The rules' values were fixed in `TWIN_SET_V2` on 2026-11-02 and in V1 on 2026-10-25, before this plan, and nothing here changes them. The model behind this thread has read about Bitcoin's past up to its training; that cannot tune fixed values, and every choice in this plan (windows, thresholds, the stress) is written before any run. The months after that training, 2026-07 to 2026-10, are reported by quarter as the one stretch no model behind this thread could have seen.

### 4.4 The runs

1. The development window, continuous.
2. The test window, continuous (the verdict).
3. The fresh starts of §4.3.
4. **Cost stress:** the test window with the slippage scenario at 5 bp a fill instead of 1 bp (`FUTURES_COST_V1` with that one value replaced, labeled `STRESS_NOT_THE_COST_IN_FORCE`), the gate seeing the same cost. It bounds how much the modeled fills could flatter the rules.
5. **Without the drawdown stop:** for a twin the stop ended in the test window, the same window with the drawdown latch and stop off (the daily-loss latch kept), to show what the rule did after the live rule would have stopped it. Descriptive only.

`HOLD`, `TREND`, `TREND_GATED` and `MOMENTUM_1W` run in every run. `TREND_VETO` is `TREND` (§3).

### 4.5 The measures (pre-registered)

For each rule (`TREND`, `TREND_GATED`, `MOMENTUM_1W`) on the test window, from each account's equity at every UTC midnight (its last valuation in the 65 minutes before, as the league table counts a day):
- **M1, does it make money after costs?** The mean daily log return, with the stationary bootstrap of the league table (mean block 3 days, 2,000 resamples, seed from the set's hash, the twin and the window). `MAKES_MONEY` when the lower end of the 98.4% interval is above zero (95% shared by the three rules, Bonferroni); `LOSES_MONEY` when the upper end of the 95% interval is below zero; otherwise `UNCLEAR`.
- **M2, does it beat holding BTC?** The paired daily log-return difference, the rule minus `HOLD`, with the same bootstrap and the same three outcomes (`BEATS_HOLD`, `TRAILS_HOLD`, `UNCLEAR`).

Descriptive, no pass rule: the final equity, the yearly growth rate, the annualized volatility and Sharpe ratio (daily log returns, √365), the largest fall from a high (daily values), the number of trades, the share that won, the mean net result per trade in R (net P&L over the risk at entry) for the trend rules, fees, funding paid and received, time in a position, the latches and the drawdown stop's date, the refusals by code, and the trend rule's candidates a day (what the veto twin would have been asked). The same for the fresh starts and the stress run, and each against `HOLD`.

Trial ledger: three rules, one test-window run each, so three trials; the stress and no-stop runs carry no pass rule. Nothing is promoted or changed by any result: a rule that passes is evidence for a later plan, on the owner's word.

### 4.6 What it costs

No model call, no token, no app resource. One download of about 0.3 GB of public files on the PC through a device session; the runs in the cloud, minutes each (Q06 budget: the whole set within 60 minutes of the cloud container's time).

## 5. Authority

The backtest's accounts are simulations in memory, labeled `BACKTEST_MODELED_NOT_FILLED`: no ledger, no journal, no twin row, no database at all. Nothing reads them but the report. The code imports only pure modules and opens only the files it is given.

## 6. Requirements and tests

`tests/test_backtest.py`, database-free, on synthetic minutes built in the test (labeled synthetic):
- R1 the reader refuses a bad checksum, a malformed row, an unaligned or duplicated minute, and keeps a missing minute missing; it reads both header and headerless files.
- R2 the hold twin enters once at the first bar with `size_hold`'s plan and never trades again; its equity follows the mark.
- R3 the trend twin enters on a cross at the first bar of the next hour, exits at a bar when the fast EMA turns against it, and its stop fills at the level or at a gapped open, with the slippage against it; the cooldown and the 24-a-day limit hold an entry without spending the cross.
- R4 the gate and the funding filter refuse and spend the cross; the stress cost refuses more.
- R5 funding is paid by a position open at a funding time and not by one opened after it; an unpayable payment waits as owed and posts once the wallet covers it.
- R6 the momentum twin flips on the day's reading and holds on an equal close; a day with a missing hour is not read.
- R7 the daily-loss latch blocks entries until the next UTC day; the drawdown latch stops the twin once flat; the no-stop variant keeps trading.
- R8 the wallet check holds after every run and a tampered account fails it.
- R9 the measures: daily values, log returns, the bootstrap's seed and outcome labels on a known series; a fresh start uses history before its start.

## 7. Official sources

- Binance, "Binance Public Data", <https://github.com/binance/binance-public-data> (the archive's paths, the kline columns, the `.CHECKSUM` files); and the archive itself, <https://data.binance.vision/?prefix=data/futures/um/>. To be read and recorded in [REFERENCES](../../REFERENCES.md) with the date it is opened.
- Binance USDⓈ-M futures API, "Exchange Information", the public `GET /fapi/v1/exchangeInfo` the app already reads ([MARKET_DATA](../../MARKET_DATA.md)).
- Politis and Romano (1994), the stationary bootstrap, as cited in `app.evaluation.bootstrap`.

## 8. Data and trust boundaries

Public market data only, downloaded on the PC into a git-ignored folder outside every image and copied to the cloud. The archive's files are untrusted input, read by the strict parser of §4.1 in a fresh process, never executed. Nothing enters the app's database, the agents' inputs or any image.

## 9. Implementation sequence

1. This plan, committed and pushed before any run (the pre-registration).
2. The reader, the simulator and the measures, with §6's tests; ruff and the database-free suite.
3. The download on the PC and the copy to the cloud; the checksums recorded.
4. The development window run; fixes found there are ordinary engineering.
5. The simulator frozen: commit and push; then the test window, the fresh starts and the stress, once, with that commit in the results.
6. The results page and the records; the pull request; the owner's word before merging.

## 10. Verification commands

From `services/engine` (PROPOSED until §14 records a run):

```bash
.venv/bin/ruff check --no-cache .
env -u ASL_DATABASE_URL -u ASL_DB_HOST -u PGPORT -u ASL_DB_NAME ASL_TEST_ISOLATED=1 \
    .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_backtest.py
.venv/bin/python -m app.futures.backtest --data <folder of the archive's files> --window development --out <file>
.venv/bin/python -m app.futures.backtest --data <folder> --window test --out <file>
```

## 11. Failure and rollback

A run that cannot read a file, finds a checksum mismatch or fails its wallet check stops and says so; nothing is half-written. The code is inert in the app (no service imports it), so a rollback is the revert of the merge.

## 12. Q01–Q10

- Q01, Q02: the results page, read in a browser at desktop and phone width (it is not part of the app).
- Q03: R1 to R9; the wallet check of every account.
- Q04: no new host, secret or input in the app; the archive is parsed strictly (R1).
- Q05: missing minutes and pending funding are counted, never guessed.
- Q06: §4.6's budget.
- Q07: ruff, the database-free suite, the backtest's tests. The database and browser suites do not touch this code (NOT RUN, nothing of theirs changed).
- Q08: each run prints its counts and its wallet checks.
- Q09: no migration, no image change that runs; nothing to back up.
- Q10: this plan, REFERENCES, the results file's schema.

## 13. Decision log

- 2026-11-03, the owner: the backtest of the rule twins, not of the AI trader; the periods and the method are the thread's to choose ("you decide what would be best"), and every result is shown.
- The thread, under that word and the owner's "decide for me" (2026-10-19): calendar years and quarters as fresh starts, because the owner's example was a two- to three-month window from 10,000 USDT; a development window before 2022 and one untouched test window after it, because nothing is tuned and the split guards the simulator's own choices; Bonferroni over the three rules; the stress at 5 bp; the archive downloaded on the PC, because the cloud refuses Binance's hosts; the results page outside the app first, since the app's pages measure the live accounts.

## 14. Progress

- 2026-11-03 08:21 UTC: the thread started from `main` at `429a0cc`. 08:24 UTC: `data.binance.vision` and `fapi.binance.com` refused from the cloud and from the desktop's sandbox (proxy 403).
- The download, OBSERVED (the device session's record, `manifest.txt`): 08:26:37 to 08:28:52 UTC on the owner's PC, 516 requests at most 4 at a time, no key; for each of the three series 82 monthly zips, 2020-01 to 2026-10 with none missing, and 2019-09 to 2019-12 not published (404); 246 of 246 zips equal Binance's SHA-256 `.CHECKSUM`; `exchangeInfo` read at 08:27:00 UTC (BTCUSDT `PERPETUAL`, `TRADING`, tick 0.10, step 0.001, minimum 0.001, market maximum 120, minimum notional 50). Packed as three tar files (SHA-256 `702e55f4…dbd3` klines, `b4d2adb9…d3d5` mark, `23259ec1…a344` funding), copied to the cloud at 08:33 to 08:35 UTC, where the same three hashes were read. The app, Docker and git were not touched.
- 08:47 UTC, the development run's first pass (OBSERVED, code not yet committed): it read the monthly files and found the archive's holes that §4.1's amendment covers. Fixes found there, ordinary engineering: the funding files write some rates in scientific notation (`8.4E-7`), which the reader now accepts; the start's value is the first day's opening value (the league would leave the first day out).
- 08:51:59 to 08:52:13 UTC, the daily files (OBSERVED, the device session's record): 9 mark days found, each 1,440 minutes, every checksum OK; the trade klines' 2026-10-28 and the mark's 2026-10-28 and 2026-10-29 answer 404. Packed as `daily.tar` (360,960 bytes, SHA-256 `454410e5…6deb`), copied to the cloud at 08:54 UTC, where the same hash and the nine checksums were read.
- 08:55:57 UTC, the development run (OBSERVED, 4 processes, 113 s; 256 files read in 65 s): over the whole archive 1,440 trade minutes and 2,935 mark minutes missing (the three days above, and gaps of 29, 24 and 2 minutes); in the development window 0 trade minutes and 53 mark minutes missing, no funding time without a rate. BTC 7,189.43 to 46,210.56 (+542.8%, `RISE`). From 10,000 USDT on 2020-01-01:
  - `HOLD` 39,498.23 (largest fall 69.2%). Its whole wallet is margin, so 1,575 funding payments, 24,087.98 USDT, wait as owed; the equity counts them.
  - `TREND` 9,794.61: 134 trades, 27.6% won, mean −0.058 R; fees 405.66 against a gross 227.01; the drawdown stop on 2020-12-08.
  - `TREND_GATED` 10,012.91: 254 trades, mean 0.0001 R; fees 606.08 against a gross 586.55; 10 gate and 22 funding-filter refusals.
  - `MOMENTUM_1W` 5,068.75 (largest fall 72.3%): 117 flips; funding paid 4,006.48, received 865.29.
  - M1 and M2 `UNCLEAR` for each rule (development, no pass rule). Every wallet check held.
- 08:57:41 UTC, the simulator frozen: `3f922a3` committed and pushed (ruff, and 28 passed for `tests/test_backtest.py`). 08:58 to 09:01:11 UTC, the test window, the fresh starts and the two checks, **once** (OBSERVED, 4 processes, 196 s; the results file records `3f922a3` with no uncommitted change). In the test window 1,440 trade minutes and 2,882 mark minutes missing (the three days of §4.1), no funding time without a rate. BTC 46,210.57 to 77,522.60 (+67.8%, `RISE`). From 10,000 USDT on 2022-01-01:
  - `HOLD` 12,585.90 (largest fall 68.7%; 4,110.79 USDT of funding, 4,005.82 of it owed at the end; the open long worth +6,701.64 at the mark).
  - `TREND` 9,606.46: 120 trades, 24.2% won, mean −0.130 R; −94.78 before costs, fees 293.49; the drawdown stop on 2022-09-02 03:03 UTC.
  - `TREND_GATED` 9,608.17: 120 trades, mean −0.130 R; 1 gate refusal; the drawdown stop on 2022-09-02 11:11 UTC.
  - `MOMENTUM_1W` 9,299.72 (largest fall 62.5%): 282 flips, 34.8% won; +1,947.81 before costs, fees 2,295.47, funding −749.75, the open short +397.13.
  - **The verdict, M1 and M2 (§4.5): `UNCLEAR` for all three rules.** As yearly growth (the mean daily log return ×365), M1's 98.4% interval: `TREND` −3.3% to +1.9%, `TREND_GATED` −3.5% to +2.1%, `MOMENTUM_1W` −40.0% to +65.7%; M2's, against `HOLD`: −48.4% to +69.5%, −48.8% to +74.3%, −59.1% to +108.0% (4 days left out, on which `HOLD` had no valuation). The trial ledger holds three trials, none passed; nothing is promoted or changed. The expectation of §1 held (holding won the rising years and lost 2022; momentum beat it in 2022, −27.7% against −66.3%, and lagged it in 2023), except that the gated rule neither traded less nor lost less in the test window: the gate refused 1 trade at 1 bp. Without the drawdown stop it did both.
  - Cost stress at 5 bp (descriptive): `HOLD` 12,569.88, `TREND` 9,705.45 (stopped 2022-06-06, earlier and so higher), `TREND_GATED` 9,491.74, `MOMENTUM_1W` 7,485.79 (−25.1%). M1 and M2 `UNCLEAR`.
  - Without the drawdown stop (descriptive): `TREND` 6,621.70 (819 trades, mean −0.201 R, fees 2,374.29), `TREND_GATED` 7,290.52 (701 trades, 114 gate refusals); M1 reads `LOSES_MONEY` for both (the 98.4% interval −13.9% to −1.4% and −12.0% to −0.4% a year); M2 `UNCLEAR`.
  - Fresh starts: every year and quarter in the results file and on the page. The trend rule's drawdown stop in 5 of the 6 full years (2020, 2022, 2023, 2024, 2025), the gated one's in 4. The quarter the owner gave as an example, 2023 Q1: `HOLD` +68.4%, `TREND` −0.2%, `TREND_GATED` +0.5%, `MOMENTUM_1W` +24.1%. The months after the model's training: 2026 Q3 `HOLD` +40.0%, `TREND` +1.1%, `TREND_GATED` +0.5%, `MOMENTUM_1W` −7.9%; October 2026 −7.5%, −0.9%, +0.1%, −1.4%.
- 09:10 UTC, the results page in the owner's Claude account (Q01, Q02: read at 1280 and 390 px, light and dark, no horizontal overflow, no console error); the two results files in the project's files, `backtest/backtest-results-test.json` and `backtest/backtest-results-development.json`. §7's sources recorded in [REFERENCES](../contracts/REFERENCES.md#backtest-data--2026-11-03) as BT-01 to BT-03; the result in [TRADING](../../TRADING.md#the-record-so-far).
- 09:16 UTC, VERIFIED in the cloud on the branch (main merged in): `ruff check --no-cache .` All checks passed; the database-free suite with §10's environment, `2 failed, 1164 passed, 484 skipped, 438 errors`, the two failures and every error the database cases of [COMMANDS](../../COMMANDS.md)' baseline.
- NOT RUN: the database and browser suites (nothing of theirs changed, Q07); any run on the PC (nothing to install: no service imports the backtest).
