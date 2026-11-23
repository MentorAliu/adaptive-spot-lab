# Autonomy, permission and approval matrix

## Canonical authority

This document owns **who may request an action and when approval is needed**. [RISK_POLICY.md](RISK_POLICY.md) owns the rule's definitions and the financial limits, and [TRADING.md](TRADING.md) the trading judgment behind a change. Since [ExecPlan 0060](plans/0060-spot-trading-only.md)'s update (M12, installed on the owner's PC on 2026-11-12) the account trades Bitcoin spot by a code rule and the app has no runtime agents: the [section below](#execplan-0060-spot-trading-only-m12) is in force. The matrices of M5 to M11 (the agents' roles and tools, the research, the twins, the futures trader) are in the [archived copy](archive/contracts/AUTONOMY_MATRIX.md), history only.

The owner installs the code that defines the operating envelope: the rule, its policy and costs, the backtest and the measure. Within it the account trades unattended while the PC and the services run. The app records each version it runs with its hash, as `SYSTEM` and never as the owner; installing an update is the owner's consent to what it ships, not a promise of profitability ([ExecPlan 0031](archive/plans/0031-m8-simple-app-that-runs-itself.md)). Favorable results never expand authority.

## Actors

- **SYSTEM:** the code: the market feed, the spot engine's step (the rule, the policy, the fills, the postings, the valuations, the latches, reconciliation), the first run's start and the backtest.
- **OWNER:** the person who installs updates (the double-click on `update-app.cmd`) and holds the account's controls on the Settings page: Pause, Resume, Stop and sell, Start after a stopped run, and top-ups. There is no sign-in since [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md): the controls are reached through the web on the PC's loopback.

No model, agent or research process has any role at run time.

## Never at run time

| Action | Boundary |
|---|---|
| A real exchange order, a withdrawal, an exchange key, Testnet or Demo | Prohibited capability, not an owner toggle ([AGENTS](../AGENTS.md) rule 1) |
| Short, borrow, margin or leverage; a coin other than Bitcoin | Prohibited; long or cash only |
| Set a balance, post a fill or a price from the browser, run SQL | No such route ([API_CONTRACTS](API_CONTRACTS.md)); only the engine's step posts fills and only M1's funding path posts top-ups |
| Change the rule, its limits, the policy, the costs or the code; raise a hard cap; clear a latch the code does not clear | Only in an update the owner installs; the stored definitions must equal the code |
| Modify production code, install packages, reach a shell or credentials | Prohibited runtime capability; development is a different environment |

## Expiry, revocation and protection

The owner can pause buying or stop the run at once from the Settings page; each request is applied at the engine's next step and answered once (`APPLIED` or `REJECTED` with reasons). A latch, a paused run and an integrity hold stop buying, never selling: protection of what is held never waits for the owner, a model or an approval, only for a running engine and a valid book. A definition the account relies on is never removed while it holds what that definition protects; an update that changes the rule ends the run under the old one first.

## Checkable meaning of hard boundaries

"No authorized path around a rule" is a design invariant tested in the app. It is not a claim of immunity to all bugs, or a promise that losses cannot exceed a stop. The engine's tests cover stale books, an unverified clock, parallel steps (the lease and fencing), idempotent requests, a run changed under a request and a refused trade; every refusal leaves the account unchanged.

## ExecPlan 0060: spot trading only (M12)

IMPLEMENTED ([ExecPlan 0060 §5](plans/0060-spot-trading-only.md#5-authority)); installed on the owner's PC on 2026-11-12 ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)). `SPOT_POLICY_V1` names `SPOT_RULE_V1`, code, as the account's only decider ([RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060)). The actors are `SYSTEM` and the `OWNER`: ANALYST, RESEARCHER, EVALUATOR and COORDINATOR have no process, no tool and no row below; the agents' worker, runner, egress and sign-in services are removed, and every earlier section's agent rows are history.

| Action | Who | Bound by |
|---|---|---|
| Read the day and buy or sell the difference to the target, or sell everything when the target is zero | `SYSTEM` (the spot engine's step, in code), at its first step at or after 00:05 UTC once the day's final candle is stored, again every 15 minutes while the day is not spent | `SPOT_RULE_V1`, `SPOT_POLICY_V1` and `SPOT_COST_V1`, frozen in migration `0041`; long or cash; a buy refused under a latch, a paused or stopping run or an integrity hold; any trade refused on a stale or thin book, an unverified clock or an unusable instrument, each refusal stored with its codes; a sell still sells under a latch |
| Store each reading and its outcome | `SYSTEM` | `spot_rule_readings`, one row per day acted on; a day not readable or refused once a day per reason |
| Sell everything when the run is stopping (the drawdown stop or the owner's Stop and sell) | `SYSTEM`, at each step | `STOP_SELL` of the BTC that can be sold; the run stops once only USDT or unsellable dust is held |
| Start the first run | `SYSTEM`, once the account is funded | The run records the three definitions' hashes as `SYSTEM`; the account keeps its money and units, the run's high-water NAV starts with it |
| Retire the futures account | `SYSTEM`, in migration `0041` | Refused unless the futures account is flat with nothing reserved; a live futures run ends `STOPPED`, `NEW_POLICY`, with a `FUTURES_RETIRED` event; the retired tables move to the `archive` schema with every row, readable by the migration role only |
| Compute the backtest | `SYSTEM` (the execution worker, outside the money step), after the install and after each new final day | `SPOT_BACKTEST_V1` on the stored daily candles; it writes only `spot_backtests` and changes nothing in the account |
| Pause, Resume, Stop and sell, Start, top-ups | The owner only, as requests on the Settings page that the engine applies at its next step | Pause opens an `OWNER` cause (no buy; sells continue); Resume closes it; Stop and sell makes the run stopping; Start begins a new run after a stopped one, the drawdown stop's included; top-ups are NAV-neutral at a valid valuation ([LEDGER](LEDGER.md)) |
| Change the rule, its values, the policy, the cost, the backtest or the measure, or act on the measure's verdict | Nobody at run time: a new version is an update the owner installs | The stored definitions must equal the code; the measure of [0060 §4.10](plans/0060-spot-trading-only.md#410-the-measure-pre-registered) changes nothing by itself |
| Ask a model anything | Nobody: no model runs in the app | A model's return is a new plan the owner approves |
