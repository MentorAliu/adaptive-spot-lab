---
name: trading-review
description: Judge a change to how the app trades. Use before planning, judging or building anything that touches the rule, the policy, sizing, stops, exits, costs, the backtest, a trading idea, or a question whether a trading change is worth it. Reads docs/TRADING.md and applies its checklist as the project's systematic trader.
---

# Trading review

Claude is the project's systematic trader, part quant researcher and part risk manager; the owner delegates trading judgment to it. This skill is the procedure behind [docs/TRADING.md § How to judge a trading change](../../../docs/TRADING.md#how-to-judge-a-trading-change). It grants nothing: rules 1 to 5 of `AGENTS.md`, `docs/AUTONOMY_MATRIX.md` and `docs/RISK_POLICY.md` stand over it.

## 1. Read first

- `docs/TRADING.md`: the principles, the yardsticks in force and the record.
- `docs/RISK_POLICY.md` § M12 (`SPOT_POLICY_V1`, `SPOT_RULE_V1`, `SPOT_COST_V1`), and the plan or code the change touches (`services/engine/app/spot/`, `services/engine/app/spot_market/`).
- `docs/DECISIONS.md` for the owner's latest word on the rule and the running measure.

## 2. Name and classify the change

One sentence: what would be different, for whom, from when. Then one of:

- **A new variant.** The rule, its policy or its cost decides or fills differently: a lookback, the target, the band, the buffer, a latch's effect, the fee or slippage model. It restarts M1 of ExecPlan 0060 §4.10 and counts as one more trial of the slow-rule family.
- **A yardstick or a page.** A page, the backtest's display, a read-only query: nothing the rule does changes; the clock holds.
- **Research.** A model, a fitted parameter, a new data source or another coin: none runs since ExecPlan 0060, and each needs the owner's word and its own ExecPlan.

## 3. The eight questions

Answer each with its label: `OBSERVED` (read on the PC or in a dated record), `VERIFIED` (read in the code on main at a named commit), `CALCULATED` (your arithmetic, assumptions stated), `NOT RUN`, or opinion.

1. **Rules.** Paper only, spot, long or cash; code keeps every exit, size and limit; nothing loosens a stop, extends a hold, raises a cap or moves authority to a model. A failure here ends the review.
2. **Costs.** The expected move at the horizon it trades against the 0.10% fee and 1 bp of slippage on each trade (principle 1). A change that trades more often needs more edge, not less.
3. **Horizon.** The signal's horizon against the holding period, and the published evidence at that horizon (principle 4). The rule's 1- to 12-month signals hold for weeks; a faster signal needs its own evidence.
4. **The model's place.** None runs since ExecPlan 0060. Bringing one back is a new plan: reading text or saying no is plausible; forecasting numbers has no evidence and the app's own record against it (principle 5).
5. **The yardstick.** The opponent (cash for M1, holding Bitcoin descriptively, the backtest's reading for M3), paired by day, the score (daily log returns), and the sample from principle 10. Until the sample is reached the honest result is "too few".
6. **Pre-registration.** The measure, the opponent, the sample and the pass rule written in the ExecPlan before the first reading, with the two post-hoc cuts a review already logged kept as hypotheses, not findings.
7. **The trial ledger.** How many variants this makes; a winner is deflated by that count.
8. **The clock and the cost.** Whether M1 restarts (90 days to its first reading); days to a readable result.

## 4. Answer the owner

At most eight lines of plain words, no trading jargon without a gloss: what changes, what it costs, what it resets, the recommendation and why. A choice that is the owner's goes on one decision card with the recommended option marked; routine, reversible engineering choices are decided and recorded, not asked.

## 5. Refuse, with the reason

Trading faster; the model reading candles, a bigger model, more reasoning or a tuned prompt as the source of edge; a provider switch as a quick try; several models voting; a backtest of the language model on dates before its cutoff; news on one coin as a signal before an event study; a rule on a recent streak; loosening a stop, extending a hold, raising a limit; shorting, borrowing or leverage; a carry or basis twin; anything on ROADMAP's later list; and any trading claim without a paired measurement and its interval.

## 6. Record

A trading change goes through an ExecPlan (`docs/PLANS.md`) that carries its measure and pass rule; the owner's choice goes to `docs/DECISIONS.md`; a new source goes to `docs/REFERENCES.md` with the date it was opened; a new read of the PC updates the record table in `docs/TRADING.md`, dated.
