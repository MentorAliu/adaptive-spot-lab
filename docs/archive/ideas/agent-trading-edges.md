# Where AI agents could earn a trading edge: the ranked ideas

**PROPOSED, 2026-10-25.** The owner asked, in the project thread "Find an AI agent trading edge" at 07:22 UTC: "On everything so far related to trading crypto or stocks in general, is there a possible way to use ai agents to create an edge, think of this as an inventor and be creative". The thread answered with a Claude Doc, "Where AI agents could earn a trading edge", whose ranking this note keeps so the ideas can be found later. A note grants no permission: an idea reaches the app only through an ExecPlan the owner approves. Idea 2, 3 and parts of 1 and 4 are [ExecPlan 0041](../plans/0041-twins-and-a-veto.md), approved the same day.

**The verdict.** An agent is unlikely to beat Bitcoin by guessing the next 15-minute move: BTC's median 15-minute move over 30 days was 0.074%, below the 0.10% a round trip costs in taker fees ([0039 §15](../plans/0039-bitcoin-futures-on-paper.md#15-progress)); long and live tests of LLM traders mostly lose to holding, and two-week results are luck (the sources in the Doc and [TB-01 to TB-20](../../REFERENCES.md#trading-bot-builder-and-llm-trading-research--2026-10-17)). Where an agent can help: saying no to code's trades, reading slow text (releases, scheduled numbers, protocol and exchange events), sizing by the market's structure (fees, funding, time of day), and running honest tests. Hold-BTC is the benchmark every idea must beat.

Ranked by how plausible a measurable, repeatable after-fee gain is, then by cost; "model calls" are per day on the shared Codex allowance (the trader may use up to 120).

| # | Idea | Plausible edge | Model calls | How to test it on paper | Where |
|---|---|---|---|---|---|
| 1 | Cost gate: no trade whose expected move cannot pay its fees | High as a loss cut, none as alpha | 0 | The same rule with and without the gate, paired | 0041's `TREND_GATED` twin; on the trader's own entries, a later policy ExecPlan |
| 2 | Twins: fixed-rule paper accounts beside the trader | The measuring stick | 0 | It is the test: hold BTC, a trend rule, the trend rule gated | [0041](../plans/0041-twins-and-a-veto.md) update 1 |
| 3 | Veto, don't predict: the agent may only say no or halve | Medium | 10–20 | Paired against the rule left alone; random vetoes at the same rate as the placebo | [0041](../plans/0041-twins-and-a-veto.md) update 2 |
| 4 | Funding-aware holding | Medium as a cost cut, low as a signal | 0 | Replay with and without; a funding-fade rule as a twin | The filter in 0041's `TREND_GATED` twin; a funding-fade twin later |
| 5 | Confidence calibration | High as a diagnostic | 0 | HIGH versus LOW trades' results from 0040's fields | After [0040](../plans/0040-trade-reviews-and-a-coach.md) runs |
| 6 | Event-window sit-out before releases | Medium against stop-outs, low for direction | 0–4 | Code's event study on the stored feeds (M9-R27); replay with positions flattened before releases | Later |
| 7 | Explain the move: does a stored feed item account for a sharp move? | Low to medium | 2–6 | Code tracks whether explained and unexplained moves continue or revert | Later |
| 8 | Fade or follow a sharp move, as fixed rules | Low to medium | 0 | Replay on the 1-minute perp candles at the existing trigger | Later; a twin each |
| 9 | Regime labeler every 4 hours | Low to medium | 6 | The label against a volatility rule and against no switching | Later |
| 10 | Coach as a tuner, with a shadow A/B | Low to medium | Within 0040's 48 | One policy value a week, tried in an isolated run first | Later, after 0040 |
| 11 | Hypothesis factory with honest testing | Medium to learn, low to find alpha | 5–10, plus PC compute | Walk-forward with fees, a trial ledger, a locked holdout | Needs the owner's word: research is off since [0035](../plans/0035-a-simpler-app-that-trades-by-itself.md) |
| 12 | Time-of-day and weekend windows | Low | 0 | Replay on the app's own candles with fees; expect it to fade | Later; a twin |
| 13 | Headline surprise score | Low | 10–24 | Event study first; no trade until the base rate holds out of sample | Later |
| 14 | Protocol and exchange event reader | Low | 2–5 | Mostly a no-trade filter; needs new sources | Later |
| 15 | Cross-coin lead-lag from the watchlist | Low | 0 | Code only, on the stored candles | Later |
| 16 | Several models voting | Low: noise reduction, not alpha | Paid APIs | — | Later and separately approved |
| 17 | Faster trading, 1 to 5 minutes | Very low | 3 to 15 times today's | The fee arithmetic of [0039 §2](../plans/0039-bitcoin-futures-on-paper.md#2-the-owners-question-what-decides-how-often-futures-should-trade) already answers it | Not planned |

**Unlikely to beat the market, and why:** trading faster (fees are fixed per trade while moves shrink with the square root of time); the model reading candles (tests over months and decades show LLM timing fading below buy-and-hold, and hosted models answer the same prompt differently); agreement between models (noise reduction, not alpha); tuning prompts (a better prompt for a game with no edge is still a game with no edge); published anomalies (measured without costs, they fade); historical tests of the model (it may remember what came after the date it is shown); news on a single coin (the sentiment results came from choosing among thousands of stocks).

**Later and separately approved** ([ROADMAP](../../ROADMAP.md#later-and-separately-approved)): stocks on paper, prediction markets on paper, cross-exchange funding and basis with a simulated spot leg, paid data (liquidations, open interest, on-chain flows), several model vendors, live trading.
