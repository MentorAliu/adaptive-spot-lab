"""The spot account's postings (ExecPlan 0060 section 4.4): the only writer of its money.

Called by the spot engine inside its fenced step, with the account row and the BTC holding it locked. One call records
one fill and posts it as one journal transaction whose source is the fill (``spot_fill_id``), M3's per-asset double
entry with the fee in USDT (``SPOT_COST_V1``):

- a buy: ``OWNER_CASH`` -gross and ``CLEARING`` +gross in USDT; ``CLEARING`` -quantity and ``OWNER_ASSET`` +quantity
  in BTC;
- a sell: the reverse;
- the fee, when above zero: ``OWNER_CASH`` -fee and ``EXPENSE`` +fee in USDT.

The account's cash and version and the BTC holding change in the same transaction, under one new account version; the
database refuses negative cash or BTC and an unbalanced journal, and lets no other role post a spot fill.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.execution import store as xstore
from app.execution.lifecycle import stable_id
from app.execution.numbers import add
from app.execution.numbers import text as dtext
from app.spot import store
from app.spot.definitions import BASE, QUOTE
from app.spot.money import BUY, Fill


def postings(fill: Fill) -> list[tuple[str, str, Decimal]]:
    """(asset, book account, amount) of one fill, in the order they are written."""
    if fill.side == BUY:
        rows = [(QUOTE, "OWNER_CASH", -fill.gross), (QUOTE, "CLEARING", fill.gross),
                (BASE, "CLEARING", -fill.quantity), (BASE, "OWNER_ASSET", fill.quantity)]
    else:
        rows = [(BASE, "OWNER_ASSET", -fill.quantity), (BASE, "CLEARING", fill.quantity),
                (QUOTE, "CLEARING", -fill.gross), (QUOTE, "OWNER_CASH", fill.gross)]
    if fill.fee > 0:
        rows += [(QUOTE, "OWNER_CASH", -fill.fee), (QUOTE, "EXPENSE", fill.fee)]
    return rows


def post_fill(connection: Connection, account: dict[str, Any], held: dict[str, Decimal], fill: Fill, *,
              identity: UUID, run_id: UUID, reason: str, book: dict[str, Any], instrument_id: int, fee_rate: Decimal,
              slippage_bps: Decimal, at: datetime) -> int:
    """Record the fill and post it; returns the new account version. ``account`` and ``held`` are updated in place."""
    cash_after = add(account["cash"], fill.cash_delta)
    quantity_after = add(held["quantity"], fill.base_delta)
    if cash_after < 0 or quantity_after < 0 or held["reserved"] != 0 or account["reserved"] != 0:
        raise xstore.IntegrityFailure("spot_fill_projection_negative")
    version = account["version"] + 1
    store.insert_fill(connection, {
        "id": identity, "run_id": run_id, "reason": reason, "side": fill.side, "quantity": fill.quantity,
        "price": fill.price, "average_price": fill.average, "slippage_bps": slippage_bps, "gross": fill.gross,
        "fee": fill.fee, "fee_rate": fee_rate, "levels": fill.levels, "quote_second": book["second_at"],
        "instrument_id": instrument_id, "cash_after": cash_after, "quantity_after": quantity_after,
        "account_version": version, "filled_at": at})
    if xstore.bump_account(connection, account, cash_delta=fill.cash_delta) != version:
        raise xstore.IntegrityFailure("spot_journal_version_mismatch")
    connection.execute(text("UPDATE account_holdings SET quantity = :quantity WHERE asset = :asset"),
                       {"quantity": quantity_after, "asset": BASE})
    held["quantity"] = quantity_after
    tx = stable_id("spot-journal", identity)
    connection.execute(text(
        "INSERT INTO journal_transactions (id, spot_fill_id, account_version, event_at) "
        "VALUES (:id, :fill, :version, :at)"), {"id": tx, "fill": identity, "version": version, "at": at})
    for asset, book_account, amount in postings(fill):
        connection.execute(text(
            "INSERT INTO journal_postings (tx_id, asset, book_account, amount) VALUES (:tx, :asset, :book, :amount)"),
            {"tx": tx, "asset": asset, "book": book_account, "amount": amount})
    xstore.audit_outbox(connection, "SPOT_FILL_POSTED", identity, version, str(run_id), {
        "fill_id": str(identity), "run_id": str(run_id), "reason": reason, "side": fill.side,
        "quantity": dtext(fill.quantity), "price": dtext(fill.price), "gross": dtext(fill.gross),
        "fee": dtext(fill.fee), "modeled": True})
    return version
