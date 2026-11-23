# A sideways-market mode checked on 2026-11-17, not passing

**PROPOSED, 2026-11-17.** The owner asked in the project thread "Design an adaptive multi-strategy trader" at 07:40:28 UTC: "What would it take to create an adaptive trading that can leverage all these strategies based on conditions? What conditions would it need to adapt and use any of these strategies based on a condition?", after the project chat had named five strategies that trade often: market making, arbitrage, short-term momentum and breakouts, mean reversion in ranges and event trading. This note keeps the thread's answer and its one check so no thread repeats them; nothing in it is decided.

## The five strategies under the app's limits

| Strategy | The condition it wants | Under paper, spot, long or cash, 0.10% a trade |
|---|---|---|
| Trend following | A clear trend (price above its level of 1, 3 and 12 months ago) | Runs today: `SPOT_RULE_V1`, long in a rising trend, cash otherwise, smaller when volatility rises |
| Short-term momentum and breakouts | A quiet range that breaks | Checked on 2026-11-13: the hourly and 4-hourly versions paid 1,400 to 1,800 USDT of fees against the rule's 126 ([the note](strategies-checked-2026-11-13.md)) |
| Mean reversion in ranges | A calm, sideways market | The buying half only; checked here, not passing |
| Event trading | Scheduled US releases | Checked twice ([ExecPlan 0058](../archive/plans/0058-the-event-calendar.md), 2026-11-13): bigger moves, no direction, both versions `WORSE` |
| Market making | A wide spread and a steady order flow | Out: it needs resting orders at maker fees and speed; the paper broker fills market orders at the taker fee, and a resting order's fill cannot be known without inventing it (rule 5) |
| Arbitrage | A futures premium, or a price gap between exchanges | Out: it needs a short leg or a second venue (rule 1; the carry check of [2026-11-10](strategies-checked-2026-11-10.md)) |

What a switch between them would take: a condition detector in code (trend strength, volatility, whether moves continue or reverse, the release calendar); strategies that each pay a round trip's 0.22% in their own condition; a detector that is not late (in the app's own record the hour-to-hour moves turned from continuing to reversing at the end of October 2026 without warning, [TRADING](../TRADING.md#the-record-so-far)); and a proof that survives the trial ledger. An AI as the detector was advised against: naming the condition from prices is the number forecast the retired trader showed no edge at, and a model cannot be backtested on dates before its cutoff ([TRADING](../TRADING.md) principles 5 and 11).

## The check: a range mode beside the rule

The owner tapped "Run the check" at 07:47:02 UTC on the card "Test a sideways-market mode on Bitcoin's history before building anything?". Method: the six trials, the measure, the pass rule and the expectations were written down before the price files reached the thread and before any number (`SPEC.md`, saved 07:50:00 UTC). Data `OBSERVED`: the 2026-11-13 thread's download on the owner's PC, Binance's public archive, spot BTCUSDT 1-hour and 1-day candles 2017-08-17 to 2026-11-12 (246 files, every SHA-256 matching that download's list). Results `CALCULATED` and `BACKTEST_MODELED_NOT_FILLED`: the 2026-11-13 thread's simulator unchanged (hourly bars, fills at the bar's close, `SPOT_COST_V1`'s 0.10% fee and 1 bp of slippage, the 8% drawdown stop and the 2% daily loss latch as `SPOT_POLICY_V1`), from 10,000 USDT, 2019-01-01 to 2026-11-12; it returned the rule's recorded result first (13,326.03, 197 trades, worst fall 6.10%). The scripts, the specification and the results are in the project's shared folder `range-mode/`.

The two-mode account: the trend mode is the rule, unchanged; the range mode buys, up to the size the rule itself takes at a full signal, at a bar's close below the lower Bollinger band (the 20-bar mean less 2 standard deviations) and sells at the first close at or above the 20-bar mean or after 20 bars; the account holds the larger of the two targets. "Sideways" is Wilder's ADX(14) below 25 on the same bars. The measure: the difference in annualized Sharpe ratio against the rule on the same days, stationary bootstrap (mean block 3 days), at 99.167% for six trials; `BETTER`, `WORSE` or `UNCLEAR`.

| Trial | Ends at | Worst fall | The 8% stop | Sharpe (rule 1.20) | Verdict | Range trades | Gained | Mean a trade before costs | After costs |
|---|---|---|---|---|---|---|---|---|---|
| The rule, `SPOT_RULE_V1` | 13,326 | 6.1% | no | 1.20 | | | | | |
| Daily bars, dip and sideways | 9,990 | 8.7% | 2020-03-12 | 0.00 | `WORSE` | 26 | 50% | −3.83% | −4.04% |
| 4-hour bars, dip and sideways | 12,603 | 7.2% | no | 0.86 | `UNCLEAR` | 216 | 62% | −0.07% | −0.29% |
| Hourly bars, dip and sideways | 9,938 | 8.0% | 2020-03-12 | −0.04 | `WORSE` | 906 | 61% | +0.02% | −0.20% |
| Daily bars, any dip | 9,991 | 8.0% | 2020-03-12 | 0.00 | `WORSE` | 46 | 63% | −0.59% | −0.81% |
| 4-hour bars, any dip | 9,984 | 9.1% | 2020-03-12 | 0.00 | `WORSE` | 327 | 63% | −0.01% | −0.23% |
| Hourly bars, any dip | 9,905 | 9.3% | 2020-03-12 | −0.07 | `WORSE` | 1,410 | 61% | +0.00% | −0.22% |

Why none passes: a dip bounced back to its average about six times in ten, but the losing trades were larger than the winning ones, so before costs the average trade made nothing at the hourly and 4-hour bars and lost at the daily bar, and every round trip costs 0.22% ([TRADING](../TRADING.md) principle 1). In five of the six accounts the range mode had bought Bitcoin up to the rule's full size in the days before 2020-03-12, and that day's fall took the account 8% under its high: the drawdown stop sold everything and ended the run, which then holds cash to the window's end. The sideways condition changed nothing measurable per trade; the one account it kept out of the market that day ended at 12,603, behind the rule, with a worst fall of 7.2% against 6.1%. The checks the pass rule keeps for a `BETTER` trial (both halves of the window, neighbouring values, random entries) were not run.

Cuts after the fact, hypotheses and not findings: the daily dips gained in 2023 to 2026 (+1.3% and +2.2% a trade before costs) and lost in 2019 to 2022; no state of the rule's signal at the entry shows a gain that pays the costs at more than one bar length.

Trial ledger: six trials here, on top of the slow-rule family's six variants, 2026-11-10's three and 2026-11-13's eight: 23.

## How professionals and bots run several strategies

The owner asked at 08:06:53 UTC for a researched answer; the sources, opened that day, are TR-40 to TR-54 in the [register](../REFERENCES.md#trading-research--2026-11-01-and-2026-11-02), each with its kind and limits.

- **Professionals run strategies side by side, they do not switch between them.** Multi-manager funds split capital across many independent teams under a central risk desk (TR-40), cut a losing team's capital and then dismiss it (typically at about 5% and 7%, TR-43; the limits differ by firm, TR-41), and hold long and short positions together at 5 to 10 times their capital (TR-42). Systematic funds feed a library of signals into one risk budget (TR-40) and combine strategies that win at different times (TR-44); trend funds blend speeds, and the faster ones earn materially less after costs (TR-47; TR-03).
- **Timing which strategy to use has weak support.** No robust evidence for timing factors by their valuation (TR-45); timing the stock market added little and nothing significant (TR-46). What is adjusted is the size: less exposure when volatility rises (TR-48, which also argues that some timing skill exists; TR-10).
- **The firms that trade fastest** need more data than others, a large balance sheet and speed (TR-49), and pay no maker fee or receive a rebate of 0.004% to 0.008% a trade from 25,000,000 USD of weekly maker volume (TR-50), against the app's 0.10% taker fee.
- **Bots are tools for one strategy each.** An exchange's bots are a grid for sideways markets, regular buying, rebalancing and order splitting, and the user picks the one for the condition (TR-51); the classic grid's expected return is about zero under simple assumptions (TR-52), which the check above found for dip buying; the open-source bots give a dry run, backtests and optimization (TR-53) or market making and arbitrage (TR-54), not an edge.

Read for the app: what carries over is already built (a blend of slow trend signals, a smaller position when volatility rises, loss limits in code, a backtest, paper mode); what professionals have beyond it is breadth, short selling and near-zero fees, which rule 1 and the owner's decisions keep out.

## Why the account is quiet

The owner at 08:21:07 UTC: "our current strategy is not making any trades, thats my concern". `CALCULATED` with the app's rule code on the same daily closes, to 2026-11-12: the rule's target has been zero since the reading of 2026-10-21 (it would have held Bitcoin from 2026-08-21 to 2026-10-20), its signal −1/3 on the last days, the close above the close 91 days earlier and below those 30 and 365 days earlier. On history since 2019 the target was zero on 97% of the days of 2022 and 74% of 2026 to that date, against 16% to 38% in the other years; the longest stretch in cash was 176 days (2022-04-11 to 2022-10-03). For a buy the close must stand above two of the three earlier closes: about 77,300 to 81,500 at the readings of the next four weeks, against the 65,351 of 2026-11-15 ([TRADING](../TRADING.md#the-record-so-far)). The daily signs with 7 and 14 days added (2026-11-13's first trial) read cash too. Nothing here is a fault: the weekly review of 2026-11-16 found each live reading equal to the backtest's.

## What the owner chose

At 08:05:26 UTC the owner picked "Keep discussing" on the card "Save this check's record in the project notes and close the thread?", and at 08:32:15 UTC "Save the record and close" (the thread's recommendation) on the card "Wrap up this conversation how?", over "Save it and show the buy price" and "Close without saving". The thread's advice stands as given: keep `SPOT_RULE_V1`, build no switch. Nothing in the app changes.
