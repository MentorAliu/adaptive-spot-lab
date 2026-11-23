# What r/ai_trading uses, and what fits the Bitcoin trader

**PROPOSED, 2026-10-27.** On 2026-10-27 at 15:01 UTC, in the project thread "Research r/ai_trading", the owner asked: "research reddit subreddit ai_trading posts and comments and check what other people are using that could benefit the app". The thread delivered the findings as a page in the thread. This note keeps their substance. Nothing in it is decided. Four of its items became [ExecPlan 0045](../plans/0045-where-the-results-come-from.md), approved by the owner at 21:09:40 UTC ([DECISIONS](../../DECISIONS.md#2026-10-27--four-checks-from-the-rai_trading-research-planned-as-one-update-execplan-0045)).

**How it was read.** Reddit and the public archives are blocked from the cloud, so a read-only script on the owner's PC fetched the subreddit from the Arctic Shift archive. The download holds 58,480 posts (September 2020 to 2026-10-27) and 35,991 comments, with no user names. It is kept in the PC's ignored `.cache/ai-trading-research/` folder. Code screened every post:
- about 50,000 match none of the 30 search words other than Tickeron, the product the subreddit describes itself as powered by (4,517 posts name it);
- 1,554 posts were kept as most relevant, and about 230 were read in full;
- a few thousand lower-scored posts were not read.

Everything about other people's results is `OBSERVED` in their posts, not checked here. Nothing here has run on the app.

**The verdict.** No post shows a proven AI trading edge. The most careful posts found none. One builder pre-registered 12 crypto strategies and none survived costs and a placebo. In one benchmark, 5 of 9 models lost money and the best trailed its benchmark. Most of the plumbing the careful builders recommend the app already has: money and exits in code, a direction stated before each trade, scores against a coin flip, a review of every trade, and fixed-rule twins.

The shortlist, ranked by what each would tell for what it costs:

| # | Idea | Cost | Where |
|---|---|---|---|
| 1 | Read the trader's direction calls against a coin flip after about 30 confident calls | A reading, nothing to build | 0043's decision review already has the row |
| 2 | A luck floor: random entries with the trader's own exits | Code | [0045](../plans/0045-where-the-results-come-from.md) §4.3 |
| 3 | Replay the trader's entries through the other exits, and without its own early exits. Posts report the same entries turning from loss to gain with a new exit, and an early-exit monitor that changed nothing (+2.25R against +2.22R) | Code | [0045](../plans/0045-where-the-results-come-from.md) §4.4 |
| 4 | The cost share of each trade; one post reports the same SPY breakout entries over 25 years making 7.8% with 1 ATR stops and 92.1% with 3 ATR stops | Code for the share; a wider-stop twin is a later update | [0045](../plans/0045-where-the-results-come-from.md) §4.5 |
| 5 | Longs and shorts scored apart | Already in 0040's scoreboard (by side) | — |
| 6 | Judge each coach note against the one before, with a control kept running | Code | Later; idea 10 of [the trading-edge ideas](agent-trading-edges.md) |
| 7 | Ask the same decision twice and count the flips | Model calls on the shared allowance | Later, on the owner's word |
| 8 | Order flow: the buy/sell split of volume, then free positioning data (open interest, long/short ratios) | The split is code (Binance already sends it); positioning data is a new source | The split in [0045](../plans/0045-where-the-results-come-from.md) §4.6; the rest later |
| — | Upbit altcoin event trades | Low fit: spot altcoins, not the BTC perpetual | Not planned |
