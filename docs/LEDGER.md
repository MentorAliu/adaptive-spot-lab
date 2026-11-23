# Financial ledger and virtual funding

The spot account's money ([ExecPlan 0060](plans/0060-spot-trading-only.md), M12). M3's broker ledger (orders, reservations, positions), M11's futures ledger and the twins' books are in the [archived copy](archive/contracts/LEDGER.md), history only.

## The spot account's postings (ExecPlan 0060)

IMPLEMENTED by [ExecPlan 0060 §4.4](plans/0060-spot-trading-only.md#44-the-money-path) (`app.spot.ledger`, `app.spot.reconcile`); VERIFIED in the engine's tests on a scratch PostgreSQL; installed on the owner's PC on 2026-11-12, reconciliation `OK` ([ExecPlan 0060 §14](plans/0060-spot-trading-only.md#14-progress)). The futures ledger's tables are archived by migration `0041`; its journal transactions, and M3's spot fills', stay in the journal, which takes no new one from a retired source.

- **One writer:** `app.spot.ledger`, called by the execution worker's fenced step with the account row and the BTC holding locked. Each fill (`spot_fills`) posts one journal transaction whose source is the fill (`spot_fill_id`), M3's per-asset double entry: a buy moves `OWNER_CASH` −gross and `CLEARING` +gross in USDT, `CLEARING` −quantity and `OWNER_ASSET` +quantity in BTC; a sell the reverse; the fee `OWNER_CASH` −fee and `EXPENSE` +fee in USDT. The account's cash, its version and the BTC holding (`account_holdings`) change in the same transaction; the database refuses negative cash or BTC and an unbalanced journal, and lets no other role post a spot fill.
- **The account carries over:** the spot run #1 starts with the account's cash and units as the futures account left them, so the NAV continues; nothing is reset or funded again. The other coins' dust left by M3 to M10's sales stays in `account_holdings` against its postings, unvalued.
- **Reconciliation** (every 5 minutes and at the worker's start, and at the API's start, under the account's row lock): the cash and each holding against the journal's `OWNER_CASH` and `OWNER_ASSET` sums and the fills', every fill with its journal transaction, no open reservation, the NAV checks. A failure sets `reconciliation_failed` and `paused` (the run gets an `INTEGRITY` cause: no buy, sells continue) and writes the failed checks to the outbox; a later passing run clears them, except a NAV failure a passing run does not prove repaired (also one recorded under the retired engines' names, `nav_persisted_valuation` and `nav_futures_valuation`, which the earlier code kept latched).
- **Top-ups** are unchanged: M1's funding path, NAV-neutral at a valid valuation (`VALUATION_BID_V1` with BTC held; a flat account needs no price); a top-up never moves the run's high-water NAV or a latch (rule 12). The engine values the changed account at its next step (`ACCOUNT_CHANGE`); until then the account's reads show its cash and BTC at the newest valuation's bid, never the valuation from before the top-up against the contributions after it.

## Authority and representation

Only the engine posts financial events: `app.spot.ledger` for fills, in the execution worker's fenced step, and `app.accounting` for funding, in the API's transaction. The browser cannot write a balance row. Python `Decimal` and PostgreSQL `NUMERIC` with explicit precision and rounding; PostgreSQL distinguishes exact numeric from inexact floating types [BE-04](REFERENCES.md#be-04). Transactions and locking are explicit [BE-03](REFERENCES.md#be-03).

The journal is append-only double entry with per-asset postings: every journal transaction balances **within each asset**, and BTC and USDT are never added into one scalar. Capital (`VIRTUAL_CAPITAL`), clearing (`CLEARING`) and expense (`EXPENSE`) accounts are system counterparties, not spendable assets. The cash (`account_state.cash`) and the BTC holding (`account_holdings`) are reconciled projections of the journal, not independent editable truth. A journal transaction has exactly one source (a funding request, a spot fill, or one of the retired sources); triggers let `asl_api` insert only funding-sourced journals and `asl_execution` only fill-sourced ones, and postings are accepted only in the transaction that created their header. Cash and BTC can never be negative.

## Initialization and top-ups

The quote denomination is virtual USDT. The initial 10,000.00 contribution is made exactly once by an idempotent initialization; restarting containers or rerunning migrations never funds the account again. Since [ExecPlan 0042](archive/plans/0042-no-owner-sign-in.md#43-the-account-funds-itself) the app makes it itself when the API starts: the posting under the key `SYSTEM:INITIALIZE`, its events naming `SYSTEM`, not while the reconciliation has failed or the account is paused; while refused or held for a valuation, the API tries again every minute until it posts.

Only the owner can request a positive, finite top-up, on the Settings page (the web's server functions are the only holder of the API's service key). It is reviewed as a draft (amount, account version and hash) and confirmed with that exact draft and an idempotency key; the same key and body return the original result, the same key with another body is a conflict. No GET request funds the account.

A top-up is posted at a valid valuation (`VALUATION_BID_V1`: the BTC held at a fresh best bid; an account holding only USDT needs no price). Without one, it waits as `PENDING_VALUATION` with no spendable cash; the owner can retry or cancel it. The app's initial contribution cannot be canceled (`INITIAL_FUNDING_NOT_CANCELABLE`). Posted funding is immutable; a correction would be an explicit compensating event, never a deletion. No real deposit, withdrawal or wallet exists, and withdrawals are out of scope.

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

## Result and valuation

Equity is the cash plus the BTC held at the best bid (`VALUATION_BID_V1`, floored to 8 places), net of the fees already posted. The result is equity minus net contributions; the fees are shown beside it and never counted twice. A valuation without a fresh bid while BTC is held is `INVALID` with its reason: the pages keep the last valid one with its age, and nothing reports a new equity or NAV from it. Valuations are persisted by the engine and served from the newest one; the pages never recompute equity from live prices. Deposits never reset the high-water NAV or a latch, and the rule sizes against a top-up only once it is posted and valued.

## Atomic execution and recovery

Each fill is one transaction inside the engine's step: the account's version and the fencing epoch checked, the fill, its journal transaction and its postings, the cash, the BTC holding and the account version, together or not at all. Uniqueness, asset identity, finite values and immutable references are database constraints. Reconciliation rebuilds the cash, the holdings and the NAV checks from the journal and the fills every five minutes; a discrepancy sets the integrity hold and is recorded. An unknown outcome is reconciled by its durable ids, never retried blindly. Corrections append compensating entries with their reason; a fill is never edited to match a chart.
