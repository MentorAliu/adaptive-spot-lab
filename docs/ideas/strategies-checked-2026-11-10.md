# Three strategies checked on 2026-11-10, none passing

**PROPOSED, 2026-11-10.** The owner asked in the project thread "Find another profitable strategy to add" (later "Plan the slow rule for the main account") at 11:42 UTC: "what's a good profitable strategy that the app doesn't have yet, spot or futures". The thread checked the three families [TRADING](../TRADING.md) principle 12 names that the app does not run, and none passed. This note keeps the record so no thread repeats it; nothing in it is decided. What the owner chose next is [ExecPlan 0059](../archive/plans/0059-the-slow-rule-trades-the-main-account.md).

Method: the rules, the coin list rule, the opponents, the pass mark (three trials, a 98.33% interval) and the expectations were written down at 11:50 UTC before any number (`SPEC.md`). Data `OBSERVED`: Binance's public archive, 1-day candles and funding rates of ten USDT perpetuals, 2020-01 to 2026-10, downloaded on the owner's PC (1,758 files, every SHA-256 matching). Results `CALCULATED` and `BACKTEST_MODELED_NOT_FILLED`: fills at the daily close, both taker fees (0.05%), 1 bp of slippage, actual funding, from 10,000 USDT on 2022-01-01 to 2026-10-31. The coins: the ten most traded in October to December 2021 (BTC, ETH, 1000SHIB, SOL, SAND, MANA, DOGE, XRP, LUNA, GALA), fixed for the window; LUNA's archive ends on 2022-05-13. The scripts and results are in the project's shared folder `next-strategy/`.

| Idea | Result | Why it does not pass |
|---|---|---|
| The slow rule (0057) over ten coins, never short (TR-03; TR-38) | 12,205, against 20,815 for the same rule on Bitcoin alone | The coins move together (mean correlation 0.62), and the most-traded coins of late 2021 had just boomed: SAND, MANA and GALA lost under the rule. Paired against Bitcoin alone −11% a year (`UNCLEAR` at block 3, `WORSE` at block 20) |
| The same, long or short | 15,327, against 20,130 for Bitcoin alone long or short | `UNCLEAR`; it needs shorts on other coins, which [ROADMAP](../ROADMAP.md#later-and-separately-approved) keeps for later |
| Strongest against weakest: each week the three best coins of the last 21 days long, the three worst short (TR-39) | 24,762 on the registered weekday | The other six weekdays give 5,087 to 20,609; evenly over all seven, 14,438 and `UNCLEAR`. Two coins carry it. It needs shorts on other coins |
| Carry: collect the perpetual's funding with a hedged short (TR-13) | Bitcoin's funding paid 6.6% a year on the hedged amount (2024 12.0%, the last 365 days 3.5%); about 2 to 4% a year on a whole wallet | It needs a spot leg ([TRADING](../TRADING.md#what-not-to-propose)); on other coins funding turned negative for whole years (SOL 2022 −38%) |

A by-product, after the fact and descriptive: the app's slow rule on Bitcoin alone, never short, ended at 24,328 on spot costs (0.10% taker, `NOT VERIFIED` on Binance's spot page, no funding) against 20,815 on the perpetual (2,637 of funding paid). At the size [ExecPlan 0059](../archive/plans/0059-the-slow-rule-trades-the-main-account.md#48-futures-not-spot) can hold inside the account's 8% drawdown stop the difference shrinks to about 0.5% a year.

Follow-ups, none decided:
- **Spot for the slow rule**, if the rule runs on the main account for long and its funding shows: rule 1, a spot feed and a spot money path with its own review.
- **A coin list by another rule** (market value, or a fresh list each year): a new trial, with its own pass mark, only if a reason other than this result argues for it.
