# Strategy registry

Which trading rule is in force, and which ones came before it. The definitions' values live in [RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060) and the judgment behind them in [TRADING](TRADING.md). The earlier strategies' full texts (`TREND_REFERENCE_V1`, the M6 candidate grammar, the agents' policies) are in the [archived copy](archive/contracts/STRATEGIES.md), history only.

## Role

A strategy is a versioned executable contract: its code and values are hashed, frozen in `execution_definitions` and recorded with each run as `SYSTEM`. Free-form prose is never executable authority, and no model decides. A new strategy, another coin or a wider range is a plan the owner approves and an update the owner installs, after the trading review of [TRADING](TRADING.md#how-to-judge-a-trading-change) (in Claude Code, the `trading-review` skill); a backtest or a run never approves itself.

## In force: `SPOT_RULE_V1` (ExecPlan 0060)

A slow trend-following rule on Bitcoin's daily closes, long or cash, sized by volatility: once a UTC day it reads the sign of the last close against the closes 30, 91 and 365 days before it, takes their mean (never below zero) and holds that share of a 5%-a-year volatility target in Bitcoin, trading only when the holding is more than 3 points away from the target. Under `SPOT_POLICY_V1` and `SPOT_COST_V1`; the backtest `SPOT_BACKTEST_V1` runs the same code on every daily candle since 2017-08-17. Its exact definition is in [RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060); why it was chosen, and how it is measured, in [ExecPlan 0060 §4](plans/0060-spot-trading-only.md#4-design) and §4.10.

## Earlier strategies (history)

| Version | Where it ran | Until |
|---|---|---|
| `TREND_REFERENCE_V1` (EMA 20/50 crossing on 1-hour candles, ATR stop, 72-hour exit) | M3's broker and the M4 pilot, BTC and SOL spot | The pilot's stop ([DECISIONS](DECISIONS.md#2026-10-18--the-pilot-stops-before-the-rest-of-the-m7-gate-which-runs-without-the-pilot-watch)) |
| `AGENT_POLICY_V1` to `V3` | The agents' main account, BTC, SOL and three more coins (M7 to M10) | The futures switch (ExecPlan 0039) |
| `FUTURES_POLICY_V1` (the AI trader) and `FUTURES_POLICY_V2` with `MAIN_RULE_V1` (the slow rule on the perpetual) | M11's futures account | The spot switch (ExecPlan 0060) |

Their runs, decisions and fills are kept read-only in the database's `archive` schema; their texts are in the archived copy and in [docs/archive/plans/](archive/plans/).

## The holding and its mandate

The rule's holding has no separate mandate, stop, take-profit or time exit: it is whatever share the rule's daily reading targets, and it is sold by the rule's later readings, by a stopping run's sale, or by the owner's Stop and sell. Each reading records its inputs, the rule's id and hash, the target, the action and its outcome (`spot_rule_readings`), reproducibly; no explanation is a hidden reasoning transcript or an uncalibrated claim of certainty.
