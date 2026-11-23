# Financial ledger and virtual funding

## M12: the spot account's postings (ExecPlan 0060), in use

IMPLEMENTED by [ExecPlan 0060 §4.4](../../plans/0060-spot-trading-only.md#44-the-money-path) (`app.spot.ledger`, `app.spot.reconcile`); VERIFIED in the engine's tests on a scratch PostgreSQL; installed on the owner's PC on 2026-11-12, reconciliation `OK` and no spot fill yet ([ExecPlan 0060 §14](../../plans/0060-spot-trading-only.md#14-progress)). The futures ledger of M11 below is history: its tables are archived by migration `0041`, and its journal transactions stay in the journal, which takes no new one from a retired source.

- **One writer:** `app.spot.ledger`, called by the execution worker's fenced step with the account row and the BTC holding locked. Each fill (`spot_fills`) posts one journal transaction whose source is the fill (`spot_fill_id`), M3's per-asset double entry: a buy moves `OWNER_CASH` −gross and `CLEARING` +gross in USDT, `CLEARING` −quantity and `OWNER_ASSET` +quantity in BTC; a sell the reverse; the fee `OWNER_CASH` −fee and `EXPENSE` +fee in USDT. The account's cash, its version and the BTC holding (`account_holdings`) change in the same transaction; the database refuses negative cash or BTC and an unbalanced journal, and lets no other role post a spot fill.
- **The account carries over:** the spot run #1 starts with the account's cash and units as the futures account left them, so the NAV continues; nothing is reset or funded again. The other coins' dust left by M3 to M10's sales stays in `account_holdings` against its postings, unvalued.
- **Reconciliation** (every 5 minutes and at the worker's start, and at the API's start, under the account's row lock): the cash and each holding against the journal's `OWNER_CASH` and `OWNER_ASSET` sums and the fills', every fill with its journal transaction, no open reservation, the NAV checks. A failure sets `reconciliation_failed` and `paused` (the run gets an `INTEGRITY` cause: no buy, sells continue) and writes the failed checks to the outbox; a later passing run clears them, except a NAV failure a passing run does not prove repaired (also one recorded under the retired engines' names, `nav_persisted_valuation` and `nav_futures_valuation`, which the earlier code kept latched).
- **Top-ups** are unchanged: M1's funding path, NAV-neutral at a valid valuation (`VALUATION_BID_V1` with BTC held; a flat account needs no price); a top-up never moves the run's high-water NAV or a latch (rule 12). The engine values the changed account at its next step (`ACCOUNT_CHANGE`); until then the account's reads show its cash and BTC at the newest valuation's bid, never the valuation from before the top-up against the contributions after it.

## Authority and representation

Only the engine accounting service can post financial events. The browser, LLM and general research jobs cannot write balance rows. Use Python Decimal and PostgreSQL NUMERIC with explicit domain precision/rounding; PostgreSQL distinguishes exact numeric from inexact floating types [BE-04](REFERENCES.md#be-04). Transactions and locking are explicit [BE-03](REFERENCES.md#be-03).

Maintain an append-only double-entry journal, per-asset postings, reserved funds and reconciled projections. Every journal transaction balances **within each asset**. Never add BTC and USDT quantities into one scalar balancing equation. Use explicit capital, clearing/counterparty and expense accounts; system counterparties are not user spendable assets. Positions, cash and available/reserved funds are derived projections, not independent editable truth.

For a modeled buy, quote currency leaves the user's cash account and base currency enters its asset account against the appropriate clearing accounts; fees create their own asset-specific postings. A sell reverses the asset exchange with separately recorded fees. User available funds cannot become negative. Specify whether execution fees are charged in quote/base for each cost model and reserve accordingly. Initial scope excludes BNB fee balances and automatic conversions.

## Initialization and top-ups

The proposed quote denomination is **virtual USDT**, not verified USD. Create the initial 10,000.00 contribution exactly once through an idempotent account-initialization transaction. Restarting containers or rerunning migrations must not fund the account again. Since [ExecPlan 0042](../plans/0042-no-owner-sign-in.md#43-the-account-funds-itself) the app makes it itself, when the API starts (the owner's decision of 2026-10-25): the same posting under the key `SYSTEM:INITIALIZE`, with no owner decision, its events naming `SYSTEM`, not while the reconciliation has failed or the account is paused; while refused or held for a valuation, the API tries again every minute until it posts.

Only the owner can request a positive finite virtual top-up (in Settings; there is no sign-in since ExecPlan 0042, and the web's server functions are the only holder of the API's service key). The form confirms account, amount and virtual denomination. Posting includes owner identity, request ID, idempotency key, canonical request hash, timestamp and external-flow category. Repeating the same key/payload returns the original result; the same key with a different payload returns a conflict. Do not use a GET request for funding.

If portfolio valuation required for unit issuance is stale/unavailable, retain the request as `PENDING_VALUATION` without posting spendable cash. The owner can cancel a pending top-up; the app's initial contribution cannot be canceled (`INITIAL_FUNDING_NOT_CANCELABLE`), as nothing else would fund the account. A flat quote-only account does not need a BTC/SOL mark to value its quote balance. Once posted, funding is immutable; corrections use explicit reviewed compensating events, not deletion.

Virtual top-ups do not transfer real funds. No real deposit/withdrawal API or wallet is present. Withdrawals/distributions are outside initial scope; future flow support must extend the same accounting and unitization rules before UI actions are added.

## Unitized cashflow-neutral performance

Track account equity E in virtual USDT, performance units U and NAV N = E / U. Set the initial NAV base to 100 as a reporting convention, not an investment assumption. With initial equity 10,000, issue 100 units.

For a top-up D at a valid pre-flow valuation:

```text
N_before = E_before / U_before
new_units = D / N_before
U_after = U_before + new_units
E_after = E_before + D
N_after = E_after / U_after = N_before   (apart from controlled numeric rounding)
```

Post the flow and unit issuance atomically using one account version/valuation. Precision and residual handling must be specified and invariant-tested. When NAV/equity/units make unitization invalid, fail closed and require review; do not divide by zero or reset the account.

Example, explicitly arithmetic rather than a return forecast: E=11,000 and U=100 means NAV=110. A top-up of 2,200 issues 20 units. E becomes 13,200 and U becomes 120; NAV stays 110. Total contributions are 12,200 and trading profit is still 1,000, not 3,200.

Compute flow-neutral cumulative return as N_t / N_initial - 1. Track high-water NAV H = max(valid historical NAVs). Drawdown = 1 - N_t / H. The initial base choice does not affect returns. Retain external-flow timing and valuations so alternative money-weighted reporting can be added later without corrupting these primary metrics.

## P&L and valuation

Equity includes cash plus valid marked holdings, net of already posted trading costs. Trading P&L = equity minus net contributed capital for the initial no-withdrawal scope. Break out realized P&L, unrealized P&L and fees without counting the same fee twice. Adopt weighted-average cost for the initial spot position model and test partial disposals/re-entries; it is a research accounting choice, not a tax report.

Use a declared mark policy and freshness rules; show valuation source and age. Distinguish mid-market reporting marks from executable bid-side liquidation estimates. A marked P&L is not a realized fill. If a required holding lacks a valid mark, preserve last valid valuation as stale and do not report a newly authoritative equity/NAV.

Risk uses conservative valid valuation inputs and includes pending commitments. Deposits never reset NAV high-water marks, latched risk stops or experiment history. Policy may size future trades against newly contributed capital only after the top-up is posted and valuation/risk checks pass.

## Atomic execution and recovery

Inside a transaction: lock/check account version and execution authority; validate spendable funds and risk reservations; create the order/reservation or reject; publish durable outbox events with the same commit. Fills atomically release/consume reservations and post journal/position updates. Idempotency is per request/order/fill, not a promise that the queue delivers exactly once.

Use constraints for uniqueness, asset identity, finite values and immutable references. Periodically rebuild/reconcile cash, holdings, fees, reservations and NAV projections from journal/flow records. A discrepancy pauses new exposure and reports an incident. Recovery must reconcile unknown transaction outcomes rather than blindly retry posting.

Financial corrections append reversing/compensating entries with reason and authorization. Never edit historical fills to match a chart or an agent's narrative. Export ledger and experiment reports without credentials.

## M3 implementation (ExecPlan 0011)

IMPLEMENTED in migration `0005_m3_paper_broker` and `app/execution`:

- Journal transactions have exactly one source: a funding request **or** a fill (`CHECK num_nonnulls(...) = 1`). Triggers allow `asl_api` to insert only funding-sourced journals and `asl_execution` only fill-sourced journals; postings are accepted only in the transaction that created their header.
- `OWNER_ASSET` holds each traded coin as its own asset (BTC and SOL, and from M10's update 2 also ZEC, NEAR and XRP); `OWNER_CASH` and `VIRTUAL_CAPITAL` are USDT only. A buy posts USDT `OWNER_CASH −gross / CLEARING +gross`, base `CLEARING −qty / OWNER_ASSET +qty`, and the base fee `OWNER_ASSET −fee / EXPENSE +fee`; a sell mirrors it with the fee in USDT. Buy debits round up and sell proceeds round down to 8 decimals.
- `account_holdings` (BTC, SOL quantity and reserved) joins `account_state.cash/reserved` as reconciled projections. Buy reservations hold `qty × p_max` USDT; sell reservations hold the base quantity, so holdings cannot be sold twice and unfilled proceeds are never spendable. Reservations close as `CONSUMED` (with consumed and released amounts) or `RELEASED`.
- Only balance and reservation changes increment `account_state.version`; valuation, NAV and high-water updates do not, so an owner's top-up draft is not invalidated every minute.
- **Valuation `VALUATION_BID_V1`:** equity = USDT cash + Σ holdings × best bid of a usable quote, floored to 8 decimals; any held asset without a usable bid makes the valuation invalid. Valuations are persisted every 60 s while exposed and at fills, latches, daily references and new high-water marks; the account view serves equity/NAV from the latest persisted valuation (`valuation_source`) and never recomputes them from live marks.
- **Top-ups while holding** value holdings at fresh bids inside the funding transaction; without usable marks the request stays `PENDING_VALUATION` and the owner's retry posts it NAV-neutrally later. Top-ups never move high-water, daily references or latches. The account-state guard trigger stops application roles from clearing `paused`/`reconciliation_failed`, lowering `high_water_nav`, decreasing `fencing_epoch` or changing units/contributions outside funding.
- **Dust:** a remainder below exchange minimums closes the position as `CLOSED_WITH_DUST`; the residual stays in holdings as an account-level lot valued at the bid, and the position's realized P&L writes off its remaining cost basis.
- **Reconciliation v2** (API start, owner route, worker lease acquisition) compares USDT cash, per-asset holdings and reservations, fill ↔ journal postings, order filled quantity ↔ fills, position quantities/costs ↔ fills, holdings ↔ positions, funding totals, NAV (cash/units when flat; the latest persisted valuation's internal consistency otherwise) and evidence-pin coverage. A mismatch latches the account; the worker moves implicated open orders to `RECONCILIATION_REQUIRED` and releases their reservations.

## M11: the futures ledger (ExecPlan 0039)

IMPLEMENTED in migration `0020_futures` and `app.futures.ledger` (update 2, part B; [ExecPlan 0039 §5.3.1](../plans/0039-bitcoin-futures-on-paper.md#531-part-bs-design-2026-10-24)). NOT RUN on the owner's PC until the update is installed.

- **Shared with the spot ledger.** `account_state` (cash is the futures wallet, `reserved` the open position's margin), the owner's funding and units, the journal and reconciliation. The futures account holds USDT only: no coin enters `OWNER_ASSET`.
- **Events** (`futures_ledger_events`, append-only, exact `numeric`), posted only by the futures engine inside its fenced step, with the account version they create:

| Event | Posts | Effect |
|---|---|---|
| `MARGIN_RESERVED` | Nothing | Reserves the margin (notional ÷ leverage, rounded up); one `USDT` reservation per position holds it, so the reserved-cash check holds as it is |
| `MARGIN_RELEASED` | Nothing | Releases that reservation at the close |
| `TRADING_FEE` | `OWNER_CASH −fee`, `EXPENSE +fee` | Each fill's taker fee, rounded up |
| `REALIZED_PNL` | `OWNER_CASH ±pnl`, `TRADING_PNL ∓pnl` | At an exit: quantity × (exit − entry) for a long, × (entry − exit) for a short, rounded down |
| `LIQUIDATION` | `OWNER_CASH −margin`, `TRADING_PNL +margin` | The whole margin, with no fee on top |
| `FUNDING_PAID`, `FUNDING_RECEIVED` | `OWNER_CASH ∓amount`, `FUNDING ±amount` | Quantity × the settled mark × the settled rate; a payment rounded up, a receipt down |

- **Journal.** Each posting event has exactly one journal transaction whose new source column `futures_event_id` only the execution identity may write; a journal transaction still has exactly one source. `TRADING_PNL` and `FUNDING` are new book accounts. A zero amount posts no event.
- **Equity** is the wallet plus the unrealized P&L at the newest mark at most 5 s old, persisted by the engine (the account view's `valuation_source` reads `FUTURES_VALUATION` while a position is open); with a position open and no such mark the valuation is `INVALID`, and nothing that needs it acts (a top-up waits as `PENDING_VALUATION`). NAV stays unitized, and a top-up issues units at the pre-flow NAV and moves no P&L, high-water mark or latch.
- **Funding not yet settled** stays `PENDING` and is listed by the valuation; nothing is guessed. A payment the free wallet cannot cover waits pending until it can. Equity leaves a pending amount out until it posts, so while a payment is pending equity, NAV and a top-up's pre-flow NAV are higher by that amount (a few USDT at most for this account's sizes); the payment then lowers them when it posts.
- **Reconciliation** adds: every posting event has exactly its postings and every margin event none; the reserved margin equals the open position's; each position's fees and P&L equal its events; each fill has its events; each posted funding row has its one event with its amount; a persisted futures valuation reproduces its equity and NAV from its stored wallet and unrealized P&L. It also recomputes each amount from its own row (`futures_amounts`, from the money-path review on 2026-10-24): a fill's fee at the run's taker rate (none on a liquidation), a position's margin from its value and leverage, a closed position's realized P&L from its entry and exit (the whole margin on a liquidation), and a posted funding amount from its quantity, mark and rate, each rounded as the engine rounds it. Limit: a funding time the engine never recorded is not found by reconciliation, which compares recorded rows only.

## ExecPlan 0041: the twins' books are not the ledger

IMPLEMENTED in migration `0023_twins` and `app.futures.twin_engine` ([ExecPlan 0041 §4.1](../plans/0041-twins-and-a-veto.md#41-the-twins-code)). NOT RUN on the owner's PC until the update is installed.

- **Isolated paper accounts.** Each twin keeps its own wallet, margin and high-water equity on its `futures_twins` row and its own positions, fills, funding and valuations. A twin posts no journal transaction, holds no reservation, writes no `account_state` and no futures ledger event; the owner's reconciliation is unchanged and reads nothing of the twins.
- **The same arithmetic as the trader's** (`app.futures.money`, `FUTURES_COST_V1`): an entry's fee comes out of the wallet and its margin is reserved; at an exit the realized P&L and the exit's fee move the wallet and the margin is released; a liquidation loses the whole margin with no fee; funding is quantity × the settled mark × the settled rate, a payment rounded up and a receipt down, `PENDING` until settled and while the free wallet cannot pay it. A payment that waits for the free wallet is counted as owed in the twin's value (its valuations' `funding_owed`), so a held position's unpaid funding does not raise its result; the trader's NAV is unchanged. A funding time is recorded once per position: the search starts two days before the newest recorded time and skips a time within the rate's match of one recorded.
- **The hourly check.** Each hour the step recomputes each twin's wallet from its own rows (10,000 + realized P&L − fees + posted funding) and its margin from its open position; a difference marks that twin `FAULTED`, ends its segment and shows its code in Settings. The other twins and the owner's account go on.
- **Part 2** (migration `0030_veto_twins`, [ExecPlan 0041 §4.1 and §4.3](../plans/0041-twins-and-a-veto.md#43-the-veto-agent-update-2-entry_veto_v1-evaluator-generation-12)). The veto twin and the weekly momentum twin are isolated paper accounts of the same kind, with the same arithmetic and the same hourly check; the three twins of part 1 go on in their segments. A veto twin's entry at `HALVE` is sized at half the policy's risk fraction by the same `size_entry`; the momentum twin's entry is the hold twin's whole-wallet sizing on the asks for a long or the bids for a short, and a flip is the exit's settlement, then the new entry on the wallet it left, in one step. The veto's requests and answers and the placebo's results are records, not books: they move no wallet, and the placebo's R figures are a model on 1-minute candles, never posted anywhere. NOT RUN on the owner's PC until the update is installed.

