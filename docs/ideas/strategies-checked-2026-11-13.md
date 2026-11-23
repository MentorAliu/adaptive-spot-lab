# Eight faster or wider strategies checked on 2026-11-13, none passing

**PROPOSED, 2026-11-13.** The owner asked in the project thread "Find a more profitable, more active strategy" at 08:17:44 UTC: the most profitable strategy, trading as often as a profitable one allows. The thread tested, against the app's own `SPOT_RULE_V1`, whether trading more often, reacting to scheduled US releases or adding Solana would make more money for the same risk. None passed. This note keeps the record so no thread repeats it; nothing in it is decided.

Method: the eight trials, the measure, the pass rule and the expectations were written down at 08:23 UTC before any number (`SPEC.md`). Data `OBSERVED`: Binance's public archive, spot BTCUSDT 1-hour and 1-day candles from 2017-08 and SOLUSDT from 2020-08, to 2026-11-12, downloaded on the owner's PC (420 files, every SHA-256 matching). Results `CALCULATED` and `BACKTEST_MODELED_NOT_FILLED`: hourly bars, fills at the bar's close, `SPOT_COST_V1`'s 0.10% fee and 1 bp of slippage, the 8% drawdown stop and the 2% daily loss latch as `SPOT_POLICY_V1`, from 10,000 USDT, 2019-01-01 to 2026-11-12. The simulator was checked first: the app's own `app.spot.backtest.compute` on these candles returned the install's numbers exactly (since 2019 +33.20%, worst fall 6.10%, 197 trades; [0060 §14](../plans/0060-spot-trading-only.md#14-progress)), and the thread's engine matched it (13,326 against 13,320, the same trades). The measure: the difference in annualized Sharpe ratio against the rule on the same days, stationary bootstrap (mean block 3 days), at 99.375% for eight trials; `BETTER`, `WORSE` or `UNCLEAR`. The scripts, the specification and the results are in the project's shared folder `strategy-search/`.

| Trial | Ends at | Worst fall | Trades a year | Fees | Sharpe (rule) | Verdict |
|---|---|---|---|---|---|---|
| The rule, `SPOT_RULE_V1` | 13,326 | 6.1% | 25 | 126 | 1.20 | |
| Daily, the 30/91/365-day signs plus 7 and 14 days | 13,428 | 3.1% | 46 | 201 | 1.39 | `UNCLEAR` |
| The rule's signal read every 4 hours | 13,545 | 6.0% | 57 | 285 | 1.21 | `UNCLEAR` |
| Every 4 hours on 1-, 3-, 7- and 14-day signs (TR-02's week horizon) | 11,399 | 6.4% | 380 | 1,819 | 0.58 | `UNCLEAR` |
| Every hour, a 20/50-hour EMA cross, long or cash | 12,252 | 7.7% | 160 | 1,378 | 0.70 | `UNCLEAR` |
| The rule with a 1% buffer instead of 3% | 13,106 | 5.1% | 37 | 142 | 1.18 | `UNCLEAR` |
| Cash from 4 hours before each US CPI, jobs report and FOMC statement to its window's end ([0058](../archive/plans/0058-the-event-calendar.md)'s windows), 2022-01 to 2026-10 (the rule: 11,432, Sharpe 1.03) | 10,906 | 3.4% | 55 | 193 | 0.69 | `WORSE` |
| After each release, the full size if the price rose through it, cash if not, until the next daily reading (same window) | 10,963 | 3.4% | 63 | 238 | 0.69 | `WORSE` |
| The rule on Bitcoin and Solana, equal risk, from 2021-09 (the rule: 11,465, Sharpe 0.97) | 11,347 | 3.9% | 26 | 63 | 0.82 | `UNCLEAR` |

Why none passes: the faster rules paid 1,400 to 1,800 USDT of fees the signal could not earn ([TRADING](../TRADING.md) principle 1); stepping aside for the releases, or following their first move, lost about 1% a year against holding the rule's position through them (the 0058 event study had found bigger moves after releases but no direction); Solana under the same rule made 11,299 alone and added nothing to Bitcoin (the coins move together, as on 2026-11-10). The daily rule with the 7- and 14-day signs traded twice as often for the same money and half the worst fall, but led only in 2020 and 2021 and its interval spans zero (−0.25 to +0.65): a hypothesis, not a finding.

Descriptive, not a trial: the rule at bigger sizes. At a 7.5% a year volatility target it ends at 15,063 with a worst fall of 7.97%, a hair under the 8% stop; at 10% the stop ends the run on 2020-03-09 (10,590); at 15% and 20% in 2019. More money needs a bigger slice of Bitcoin, and the 8% stop caps the slice near today's size ([ExecPlan 0060 §4.2](../plans/0060-spot-trading-only.md#42-the-size-and-what-history-shows)).

Trial ledger: eight trials here, on top of the slow-rule family's six variants and 2026-11-10's three ([strategies-checked-2026-11-10.md](strategies-checked-2026-11-10.md)).
