# Product contract

The spot app's product contract ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12; the owner's decision of 2026-11-12, [DECISIONS](DECISIONS.md#2026-11-12--spot-trading-only-execplan-0060-m12)). The contract of M0 to M11 (the agent-driven research application, its roles and requirements P13 to P20) is in the [archived copy](archive/contracts/PROJECT.md), history only.

## Goal and audience

A local, single-owner paper-trading application that trades by itself: one account holds USDT and Bitcoin and buys and sells Bitcoin spot by a code rule, `SPOT_RULE_V1`, and the app backtests the same rule on Bitcoin's history by itself. The owner delegates trading judgment to Claude as the project's systematic trader ([TRADING](TRADING.md)). The objective is capital growth after costs under a fixed risk policy; no return target, payout, success probability or guaranteed loss ceiling has been established.

## Release scope

Real public Binance market data and an internal paper broker. The app contributes 10,000 virtual USDT once, by itself, and accepts owner-confirmed top-ups; USDT is the denomination, not an assumed USD conversion. Withdrawals are out of scope. Four pages: the Cockpit, Trades, the Backtest and Settings ([FRONTEND](FRONTEND.md)). The rule trades without an approval for each trade; the owner's controls are Pause, Resume, Stop and sell, Start after a stopped run, and top-ups. A new rule, coin or wider limit reaches the account only in an update the owner installs ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md)).

## Requirements

| ID | Requirement | Primary acceptance evidence |
|---|---|---|
| P01 | Paper only, no exchange account access | Static capability checks and refused requests |
| P02 | Bitcoin spot, long or cash ([DECISIONS](DECISIONS.md#2026-11-12--spot-trading-only-execplan-0060-m12)) | No code path for another symbol, a short, a borrow or leverage |
| P03 | One-time funding and idempotent top-ups | Ledger and NAV-neutrality tests |
| P04 | Independent hard risk | Boundary, concurrency, fencing and latch tests |
| P05 | Faithful paper execution and accounting | Fill, rounding and reconciliation tests |
| P06 | Verifiable data lineage | Parsing, finality, staleness and provenance tests |
| P07 | Code decides, versions are fixed | Definitions' hashes equal to the code; no run-time change |
| P08 | Honest performance | NAV-per-unit returns, costs included, the backtest labeled as modeled, the run against holding Bitcoin |
| P09 | The required frontend, skills and preset | Official integration and real-browser evidence |
| P10 | Local Docker operation and recovery | The update's own checks, restart and restore |

[ACCEPTANCE_CHECKLIST.md](ACCEPTANCE_CHECKLIST.md) maps them to observable conditions and [TESTING.md](TESTING.md) to tests. An empty checkbox is not a completed test.

## Exclusions and preserved boundaries

No other coin, stocks, derivatives, margin, shorting, leverage, staking, real deposits or withdrawals, exchange credentials, Testnet or Demo, public multi-user product, remote hosting, external notifications, paid API or model at run time. No browsing or shell tool, automatic plugin installation, or code changing itself. A live Binance adapter would be a separately approved project, not a switch.

## Product success and trading success

Operational correctness and trading advantage are separate. A faithful app can lose money, and a rule can fail its measure ([ExecPlan 0060 §4.10](plans/0060-spot-trading-only.md#410-the-measure-pre-registered)); a profitable curve with unknown fills or cherry-picked trials is not a success. Trading claims follow [TRADING](TRADING.md): a claim without a paired measurement is "too few".
