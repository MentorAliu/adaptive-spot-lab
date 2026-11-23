# Independent risk policy

## Status and authority

**In force since [ExecPlan 0060](plans/0060-spot-trading-only.md)'s update (M12, installed on 2026-11-12): the M12 section below.** Its values are the rule's and the policy's as the owner approved them in that plan, chosen by [TRADING](TRADING.md)'s review; they are not estimates of optimal risk, market probabilities or guaranteed maximum losses. The earlier profiles (M3's `PAPER_PILOT_V1` and its sizing, the agents' enforcement, M4's and M8's latch resolution, M11's futures policies) are in the [archived copy](archive/contracts/RISK_POLICY.md), history only; the futures account's records are archived in the database, so no run's loss history is erased.

Hard limits are enforced by deterministic engine code using current account state. Raising a limit, widening the universe, removing an exit or changing the rule needs a new version that the owner installs as an update ([AUTONOMY_MATRIX](AUTONOMY_MATRIX.md)); favorable results never grant more authority.

## M12: `SPOT_POLICY_V1`, `SPOT_RULE_V1` and `SPOT_COST_V1` (ExecPlan 0060)

IMPLEMENTED from the plan the owner approved on 2026-11-12 ([ExecPlan 0060 §4.1 to §4.3](plans/0060-spot-trading-only.md#41-the-rule-spot_rule_v1-code); [DECISIONS](DECISIONS.md#2026-11-12--spot-trading-only-execplan-0060-m12)). Three code-owned documents (`app.spot.definitions`) seeded by migration `0041` with their hashes; the spot worker starts only when the stored rows equal the code, and each run records the three hashes as `SYSTEM`. VERIFIED in the engine's tests on a scratch PostgreSQL; OBSERVED on the owner's PC since the install of 2026-11-12: the three stored with the code's hashes and spot run #1 started by `SYSTEM` ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)); the rule's first reading, `CASH` for 2026-11-12, came once the daily history's fix was installed. They replace `FUTURES_POLICY_V2` and `MAIN_RULE_V1`: the migration ends a live futures run as `SYSTEM` (`STOPPED`, `NEW_POLICY`) and refuses to run while the futures account is not flat.

| `SPOT_POLICY_V1` | Value |
|---|---|
| Instrument | BTCUSDT spot; the account holds USDT and BTC, long or cash; no borrowing, shorting or leverage (1x by construction) |
| Who decides | `SPOT_RULE_V1`, code, as `SYSTEM`; no model decides, reads or vetoes anything |
| Actions | `RULE_BUY` and `RULE_SELL` (the rule's daily trade), `STOP_SELL` (a stopping run sells everything) |
| Size | The rule's target; a buy at most the free USDT after its fee and slippage; a sell at most the BTC held |
| Latches | Daily loss 2% of the UTC day's reference NAV (due within 5 minutes of midnight; late, the larger of the last valid NAV of the previous 24 hours and the first after midnight), cleared at the next day's reference; drawdown 8% from the run's own high-water NAV. Effect: no buy, sells continue; the drawdown stop makes the run stopping |
| Runs | `RUNNING`, `PAUSED` (a cause open), `STOPPING`, `STOPPED`. The first run starts by itself once the account is funded; a later one is the owner's Start. The owner's Pause, Resume, Stop and sell and Start are requests the engine applies at its next step. A stopping run (the drawdown stop or the owner's Stop and sell) buys nothing, sells the BTC held at once and is stopped once only USDT, or BTC too small to sell, is held |
| Data | A trade needs a book at most 2 s old, the clock verified by the feed and the instrument usable and checked in the last hour; the valuation needs a best bid at most 5 s old. A stale or missing price refuses the trade with its code and invalidates the valuation; nothing is guessed |
| Valuation | `VALUATION_BID_V1`, M3's: the USDT plus the BTC at the best bid, floored to 8 places; every 60 s while BTC that can be sold is held, hourly otherwise, and at each fill, each day's reference, each new high and the first step after a top-up (`ACCOUNT_CHANGE`). Until that step the account's pages show the cash and BTC now at the newest valuation's bid, so a top-up never reads as a loss |
| Dust | BTC whose sale of all of it fails the sale's own minimum quantity or notional check (the notional at the sale's fill price, on the book the step reads; without a book the minimum quantity alone) cannot be sold: it is valued with the holding and counts as nothing held for a sell-all. The other coins' dust left by M3 to M10's sales stays in the holdings with its postings and is not valued (no feed; worth cents) |
| Top-ups | NAV-neutral, at a valid valuation (rule 12) |
| Integrity | A failed reconciliation sets both account flags: no buy, sells continue. The execution worker clears them as `SYSTEM` when a later reconciliation passes (M8's `RECONCILIATION_PASSED`), except when a NAV check failed since the last clear (`nav_cash_only`, `nav_valuation`, and the retired engines' `nav_persisted_valuation` and `nav_futures_valuation`) or no failure is recorded: that latch waits for a fix an update ships |

| `SPOT_RULE_V1` | Value |
|---|---|
| When | Once a UTC day, at the engine's first step at or after 00:05 UTC once the previous day's final daily candle is stored. A day not readable yet, or a refused trade, is tried again every 15 minutes; a fill or a reading that changes nothing spends the day. A run started later in the day reads that day at once |
| Direction | `s` = the mean of the signs of the last complete day's close against the closes 30, 91 and 365 days before it (each the nearest stored day at or before it, within 7 days; else not readable), then `max(s, 0)`: never short |
| Volatility | `σ` = the annualized (365 days) exponentially weighted standard deviation of the daily log returns of the last 365 days, centre of mass 60 days (`var' = (60·var + r²) / 61`, seeded with the first `r²`; a return across missing days counts once); at least 300 days stored |
| Target | `f = max(s, 0) · min(1, 0.05 / σ)` of equity, quantized toward zero to 0.001; below 0.01 it is 0 |
| Acting | `held` = the BTC at the fresh best bid over equity. `f = 0` with BTC held: sell it all. Otherwise, when `|f − held| > 0.03`: buy or sell the difference, `|f − held| · equity / best bid` down to the lot step; else no change. BTC held without a fresh bid: refused (`BID_STALE`) and tried again |
| Gates | A latch, a paused run or an integrity hold: no buy, a sell still sells. A stale or thin book, an unverified clock or an unusable instrument: no trade, refused with its code and tried again |
| Exits | The rule's sells, a stopping run's sale of everything and the owner's Stop and sell; no stop, take-profit or time exit on the holding: its size and the latches protect it |
| Size | 5% a year, by 0059's limit rule: the largest of 40, 30, 20, 15, 10 and 5% whose worst fall from the high on daily lows stays at or below 4%, half the drawdown stop ([0060 §4.2](plans/0060-spot-trading-only.md#42-the-size-and-what-history-shows)) |

| `SPOT_COST_V1` | Value |
|---|---|
| Orders | Market only |
| Fill | Walks the ten levels of the newest stored book (asks for a buy, bids for a sell), at most 2 s old; refused `DEPTH_SHORT` when they cannot fill it |
| Slippage | 1 bp of the walked average price against the account (a scenario, not an observation) |
| Fee | 0.10% of the fill's notional, charged in USDT; no BNB discount or promotion (Binance's spot fee page, read on 2026-11-12, updated 2026-01-06: a regular user's rate 0.1%). Binance takes the fee in the asset received; the same value in USDT keeps BTC in whole lot steps |
| Rounding | Fill price to 8 places against the order; quantity down to the lot step; a buy's gross up and a sell's down to 8 places; the fee up to 8 places |
| Filters | `LOT_SIZE` and `MARKET_LOT_SIZE` (a zero market step or minimum adds nothing); `NOTIONAL` minimum and maximum at the fill price; read from the instrument at the trade |

**The backtest** (`SPOT_BACKTEST_V1`, `app.spot.backtest`, labeled `BACKTEST_MODELED_NOT_FILLED`) applies the same three documents on the stored daily candles: the live reading function, a fill at the day's close through the live fill code (the cost's slippage, fee, lot step, minimum quantity and notional), the drawdown stop at the price where the fall from the high reached 8% (the day's open when it opened below), cash for the rest of the window after it, and the daily loss counted without changing a trade (the live trade comes right after the day's reference). It changes nothing in the account.

## Loss reference and pause semantics

Daily loss uses NAV per unit, not raw equity, so a top-up is never a gain or a loss. At each UTC midnight the day's reference is the first valid valuation: `TIMELY` within five minutes, otherwise `LATE_CONSERVATIVE` (the larger of the last valid NAV of the previous 24 hours and the first after midnight), which can only make the daily loss latch sooner, never later. The run's high-water NAV persists across days, top-ups and restarts and never goes down.

The daily loss latch holds until the next day's reference; the drawdown stop ends the run, and only the owner's Start begins a new one, with its own high-water NAV. Neither is cleared by a top-up, a reconnect or a restart, and deleting a high-water mark is never a way to clear one. A new run defines a new episode, but the old run's loss history stays visible ([ExecPlan 0061 §13](plans/0061-clean-up-after-the-spot-switch.md#13-decision-log): the owner kept the archive for this reason).

A stale valuation, a reconciliation failure, a lost execution lease or a definition that differs from the code fails closed on buying; none of them stops the sells that protect what is held, which need only a running engine and a valid book.

## Invariants

The policy's limits apply to each trade at the moment of the trade, on the current account. Price changes can move the share held away from the target without a trade: the rule corrects it at its next daily reading, beyond its flat band, and nothing forces turnover in between. New funds raise equity only once posted and valued, never while a top-up is pending.

The loss limits block buying; they do not guarantee a sale at a price or cap a loss. A fall between two steps, a stale book or the PC off can take the loss beyond the 2% and 8% marks, and the pages never present a limit as a guaranteed maximum loss.

## Policy testing and changes

Every boundary comparison and rounding, top-ups at a valid valuation, UTC midnight with and without a timely reference, restarts, a stale book and a thin book are tested (`test_spot_rule.py`, `test_spot_money.py`, `test_spot_db.py`; [TESTING](TESTING.md)). A change is a new immutable version with its rationale, scope and the trading review of [TRADING](TRADING.md); no learning algorithm writes a policy value.
