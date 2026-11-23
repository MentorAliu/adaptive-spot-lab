# Internal paper broker and execution model

How the spot account's trades are filled on paper ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12). M3's broker (orders, reservations, positions and their lifecycle), M4's changes and M11's simulated perpetual are in the [archived copy](archive/contracts/PAPER_EXECUTION.md), history only.

## Spot market orders on the stored book (ExecPlan 0060)

IMPLEMENTED by [ExecPlan 0060 §4.3 and §4.4](plans/0060-spot-trading-only.md#43-spot_policy_v1-and-spot_cost_v1) (`app.spot.money`, `app.spot.engine`); VERIFIED in the engine's tests on a scratch PostgreSQL; installed on the owner's PC on 2026-11-12 ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)).

- **Who trades:** only the execution worker's fenced step, once a second, under the execution lease and the account's fencing epoch: the rule's daily `RULE_BUY` or `RULE_SELL`, and `STOP_SELL` (everything) when a run is stopping. No order is resting: each trade is a market order filled in the step that decides it, or refused with its codes.
- **The fill** (`SPOT_COST_V1`, [RISK_POLICY](RISK_POLICY.md#m12-spot_policy_v1-spot_rule_v1-and-spot_cost_v1-execplan-0060)): the quantity walks the ten levels of the newest stored book, at most 2 s old (asks for a buy, bids for a sell); 1 bp of slippage moves the walked average price against the account; the fee is 0.10% of the notional, in USDT. A buy's quantity is the target's, cut to what the free USDT pays with its fee and slippage. Quantity down to the lot step (`LOT_SIZE` and `MARKET_LOT_SIZE`), checked against the minimum quantity and the `NOTIONAL` minimum and maximum at the fill price.
- **Refusals** (stored on the day's reading, the trade not made, tried again at the next 15 minutes): `BOOK_STALE`, `CLOCK_UNVERIFIED` and `INSTRUMENT_UNAVAILABLE` before a fill is planned; `BOOK_UNAVAILABLE`, `SIZE_BELOW_MINIMUM` (below the minimum quantity), `DEPTH_SHORT`, `NOTIONAL_BELOW_MINIMUM`, `NOTIONAL_ABOVE_MAXIMUM` and `CASH_SHORT` from the plan; `BID_STALE` or `VALUATION_UNAVAILABLE` when the account cannot be valued; and for a buy `RUN_NOT_RUNNING` (a run paused by a latch or the owner's Pause, or stopping) or `INTEGRITY`. A sell is never refused for a latch or a pause. A stopping run whose sale cannot be made yet waits (`STOP_SELL_WAITS`, or `STOP_SELL_REFUSED` with the plan's codes) and tries again at the next step.
- **The step's time** is the database's clock, read inside the fenced transaction after the account's lock; the step reads no book received after it.
- **Dust:** BTC whose sale of all of it fails the sale's own minimum quantity or notional check at its fill price cannot be sold, and counts as nothing held for a sell-all or a stopping run's sale (the backtest asks the same of its one-level book).
- **Valuation:** `VALUATION_BID_V1`, the USDT plus the BTC at the best bid of a book at most 5 s old, floored to 8 places; without one the valuation is invalid and nothing is guessed.
- **Modeled, not filled:** every fill is the stored book's, not an exchange's; the pages show the fills as trades without a disclaimer ([DECISIONS](DECISIONS.md#2026-10-30--no-disclaimers-on-the-pages)), and the records keep the book's id, the levels walked, the slippage and the fee.
- **The backtest** fills at each day's close through the same code on a one-level book at the close (`BACKTEST_MODELED_NOT_FILLED`); it is never a fill of the account.

## Scope and fidelity

There is only the paper broker, with no live implementation. Market data is real (Binance's public book and candles); execution is modeled, and its limits are reported, not hidden: a broker's own paper-trading documentation lists such differences as market impact and queue position [EV-01](REFERENCES.md#ev-01). Only marketable trades exist; there is no resting order, and no stop is an exchange-hosted guaranteed stop.

## The number policy

`app.execution.numbers`: exact `Decimal` with one explicit context (96 digits, half-even), never binary floating point. Amounts are kept to 8 places (`0.00000001`), units and NAV to 36. Quantities round down to the lot step; cash debits and fees round against the account (a buy's gross and every fee up, a sell's gross down). A rounded quantity that fails a minimum is a refusal, never a reason to raise the size; sells are protected against selling more than is held, and dust is explicit (above).

## Filters and costs

The instrument's current filters (`LOT_SIZE`, `MARKET_LOT_SIZE`, `NOTIONAL`), read from the stored `exchangeInfo` at the trade [EX-03](REFERENCES.md#ex-03), not a hard-coded minimum. `SPOT_COST_V1` names every cost input: the fee rate and the asset it is charged in, the slippage scenario and the depth rule; nothing missing becomes zero. The fee is Binance's published regular rate, not the owner's verified account fee (the app has no account); Binance's documentation examples are fictional [EX-04](REFERENCES.md#ex-04). The slippage of 1 bp is a scenario, not an observation, and the book's quantities are displayed liquidity, not a promise of a fill.

## Ordering and failures

The rule reads only daily candles final before its decision and trades on a book received no later than the step's time, never retroactively at an earlier, better price. Within a step the owner's requests and a stopping run's sale come before the rule ([ARCHITECTURE](ARCHITECTURE.md#exact-authority-sequence)). A stale or missing book blocks the trade and invents no price; the next valid book after recovery is used, and the missed time stays visible. An unknown commit is reconciled by its keys before anything is retried; a restarted worker takes a new fenced lease, and a stale holder cannot commit.

## Minimum acceptance evidence

Real arithmetic and state under rounding and minimums, short cash, sell dust, a thin book, a stale book, a late book, restarts and two concurrent workers; fills reconciled to the journal's postings (`test_spot_money.py`, `test_spot_db.py`; [TESTING](TESTING.md)). Tests use labeled fixtures; a fixture that passes is not proof of realistic market execution.
