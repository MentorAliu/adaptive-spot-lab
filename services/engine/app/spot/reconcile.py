"""The spot account's reconciliation (ExecPlan 0060 section 4.4): every projection against its append-only sources.

Run by the execution worker under its fence (every five minutes and at its start) and by the API at its start, inside a
transaction that holds the account's row lock. A failed check sets both integrity flags (``reconciliation_failed`` and
``paused``) and writes the failed checks to the outbox; the execution worker clears them once a later run passes,
unless a failure was one a passing run does not prove repaired (``NAV_CHECKS``).

The journal also holds the retired sources' transactions (M3's spot fills and the futures account's events, whose
records are archived by migration 0041); their sums are part of the cash and holding totals checked here, and the
database takes no new transaction from them. The coins' dust those sales left (below each coin's minimum order) stays
in ``account_holdings`` against its postings; BTC's is the start of the spot account's holding.
"""

import json
from decimal import Decimal, localcontext
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.execution.numbers import CONTEXT, PRECISE
from app.spot.definitions import BASE

# A NAV failure is not proven repaired by a later pass, so it keeps the latch. The retired engines' names are kept
# too: a failure the futures account (``nav_futures_valuation``) or M3's engine (``nav_persisted_valuation``) recorded
# before migration 0041 keeps the latch the code that recorded it kept, and only a later clear ends it.
NAV_CHECKS = frozenset({"nav_cash_only", "nav_valuation", "nav_persisted_valuation", "nav_futures_valuation"})

CHECKS: dict[str, str] = {
    "spot_fill_without_journal": """SELECT EXISTS(SELECT 1 FROM spot_fills f
        LEFT JOIN journal_transactions j ON j.spot_fill_id = f.id
        WHERE j.id IS NULL OR j.account_version <> f.account_version)""",
    # Each fill's postings: its cash, its BTC, its fee and the clearing of both assets, nothing else.
    "spot_fill_postings": """SELECT EXISTS(SELECT 1 FROM spot_fills f
        JOIN journal_transactions j ON j.spot_fill_id = f.id
        CROSS JOIN LATERAL (SELECT
            COALESCE(SUM(p.amount) FILTER (WHERE p.asset = 'USDT' AND p.book_account = 'OWNER_CASH'), 0) cash,
            COALESCE(SUM(p.amount) FILTER (WHERE p.asset = 'BTC' AND p.book_account = 'OWNER_ASSET'), 0) btc,
            COALESCE(SUM(p.amount) FILTER (WHERE p.asset = 'USDT' AND p.book_account = 'EXPENSE'), 0) fee,
            COALESCE(SUM(p.amount) FILTER (WHERE p.asset = 'USDT' AND p.book_account = 'CLEARING'), 0) usdt_clearing,
            COALESCE(SUM(p.amount) FILTER (WHERE p.asset = 'BTC' AND p.book_account = 'CLEARING'), 0) btc_clearing,
            COUNT(*) postings FROM journal_postings p WHERE p.tx_id = j.id) s
        WHERE s.cash <> CASE f.side WHEN 'BUY' THEN -f.gross - f.fee ELSE f.gross - f.fee END
           OR s.btc <> CASE f.side WHEN 'BUY' THEN f.quantity ELSE -f.quantity END
           OR s.fee <> f.fee
           OR s.usdt_clearing <> CASE f.side WHEN 'BUY' THEN f.gross ELSE -f.gross END
           OR s.btc_clearing <> CASE f.side WHEN 'BUY' THEN -f.quantity ELSE f.quantity END
           OR s.postings <> CASE WHEN f.fee > 0 THEN 6 ELSE 4 END)""",
    # Each amount recomputed from its own row: the gross rounds up on a buy and down on a sell, the fee up, at the
    # run's taker rate. A value m with eight decimals is ceil8(v) exactly when v <= m < v + 0.00000001, and floor8(v)
    # when v - 0.00000001 < m <= v, so no division or rounding is redone here.
    "spot_fill_amounts": """SELECT EXISTS(SELECT 1 FROM spot_fills f
            JOIN spot_runs r ON r.id = f.run_id
            JOIN execution_definitions d ON d.id = r.cost_id
        WHERE f.fee_rate <> CAST(d.definition->>'taker_fee_rate' AS numeric)
           OR f.fee < f.quantity * f.price * f.fee_rate
           OR f.fee - 0.00000001 >= f.quantity * f.price * f.fee_rate
           OR CASE f.side WHEN 'BUY' THEN f.gross < f.quantity * f.price
                                       OR f.gross - 0.00000001 >= f.quantity * f.price
                          ELSE f.gross > f.quantity * f.price
                            OR f.gross + 0.00000001 <= f.quantity * f.price END)""",
    # BTC changes only by spot fills: each fill's holding after it follows from the one before, the first from the
    # BTC the retired sources' postings left (M3's dust, by migration 0041 no longer changing).
    "spot_fill_chain": """SELECT EXISTS(SELECT 1 FROM (
            SELECT quantity_after, CASE side WHEN 'BUY' THEN quantity ELSE -quantity END delta,
                   LAG(quantity_after, 1, (SELECT COALESCE(SUM(p.amount), 0) FROM journal_postings p
                       JOIN journal_transactions j ON j.id = p.tx_id
                       WHERE j.spot_fill_id IS NULL AND p.asset = 'BTC' AND p.book_account = 'OWNER_ASSET'))
                   OVER (ORDER BY seq) before FROM spot_fills) c
        WHERE c.quantity_after <> c.before + c.delta)""",
    # The rule's fills are its readings' fills, one each; a stopping run's sells are no reading's.
    "spot_rule_fills": """SELECT EXISTS(SELECT 1 FROM spot_fills f
        LEFT JOIN spot_rule_readings r ON r.fill_id = f.id
        WHERE (f.reason IN ('RULE_BUY','RULE_SELL')) <> (r.id IS NOT NULL)
           OR (r.id IS NOT NULL AND (r.run_id <> f.run_id OR r.outcome <> 'FILLED'
               OR (f.side = 'BUY') <> (r.action = 'BUY'))))""",
    "journal_unbalanced": """SELECT EXISTS(SELECT 1 FROM journal_postings GROUP BY tx_id, asset
        HAVING SUM(amount) <> 0 OR COUNT(*) < 2)""",
    "funding_unmatched": """SELECT EXISTS(
        SELECT 1 FROM funding_requests f LEFT JOIN journal_transactions j ON j.funding_request_id = f.id
        WHERE (f.status = 'POSTED' AND (j.id IS NULL OR j.id <> f.journal_tx_id))
           OR (f.status <> 'POSTED' AND j.id IS NOT NULL))""",
    "journal_orphaned": """SELECT EXISTS(
        SELECT 1 FROM journal_transactions j LEFT JOIN journal_postings p ON p.tx_id = j.id
        WHERE p.id IS NULL)""",
}


def valuation_consistent(row: dict[str, Any]) -> bool:
    """A stored valuation reproduces its equity (``VALUATION_BID_V1``) and NAV from its own cash, BTC and bid."""
    if row["quality"] != "VALID":
        return True
    from app.spot.money import equity

    value = equity(row["cash"], row["quantity"], row["bid"])
    if value is None or value != row["equity"]:
        return False
    with localcontext(CONTEXT):
        return (row["equity"] / row["units"]).quantize(PRECISE) == row["nav"]


def reconcile_locked(connection: Connection, account: dict[str, Any]) -> dict[str, Any]:
    """Compare the projections with their sources inside a transaction that holds the account lock."""
    failed: list[str] = []
    journal_cash = connection.execute(text(
        "SELECT COALESCE(SUM(amount), 0) FROM journal_postings WHERE asset = 'USDT' AND book_account = 'OWNER_CASH'"
    )).scalar_one()
    posted = connection.execute(text(
        "SELECT COALESCE(SUM(amount), 0), COALESCE(SUM(issued_units), 0) FROM funding_requests "
        "WHERE status = 'POSTED'")).one()
    assets = {row[0]: row[1] for row in connection.execute(text(
        "SELECT asset, COALESCE(SUM(amount), 0) FROM journal_postings WHERE book_account = 'OWNER_ASSET' "
        "GROUP BY asset")).all()}
    held = {row[0]: (row[1], row[2]) for row in connection.execute(text(
        "SELECT asset, quantity, reserved FROM account_holdings")).all()}
    last_fill = connection.execute(text(
        "SELECT quantity_after FROM spot_fills ORDER BY seq DESC LIMIT 1")).scalar_one_or_none()
    if journal_cash != account["cash"]:
        failed.append("cash")
    if posted[0] != account["contributions"] or posted[1] != account["units"]:
        failed.append("funding_totals")
    if account["reserved"] != 0:
        failed.append("usdt_reserved")
    for asset, (amount, reserved) in held.items():
        if assets.get(asset, Decimal(0)) != amount:
            failed.append(f"holding_{asset}")
        if reserved != 0:
            failed.append(f"reserved_{asset}")
    if any(value != 0 for asset, value in assets.items() if asset not in held):
        failed.append("holdings_rows")
    quantity = held[BASE][0] if BASE in held else None
    if quantity is None or (last_fill is not None and last_fill != quantity):
        failed.append("holding_spot_fills")
    for name, query in CHECKS.items():
        if connection.execute(text(query)).scalar_one():
            failed.append(name)
    if account["initialized"] and account["valuation_valid"] and account["units"] > 0:
        if quantity == 0:
            with localcontext(CONTEXT):
                if (account["cash"] / account["units"]).quantize(PRECISE) != account["nav"]:
                    failed.append("nav_cash_only")
        else:
            latest = connection.execute(text(
                "SELECT cash, quantity, bid, equity, units, nav, quality FROM spot_valuations "
                "ORDER BY valued_at DESC, recorded_at DESC LIMIT 1")).mappings().first()
            if latest is not None and not valuation_consistent(dict(latest)):
                failed.append("nav_valuation")
    if failed:
        connection.execute(text("UPDATE account_state SET reconciliation_failed = true, paused = true WHERE id = 1"))
        correlation = str(uuid4())
        connection.execute(text(
            "INSERT INTO audit_events (id, event, correlation_id) VALUES (:id, 'RECONCILIATION_FAILED', :correlation)"),
            {"id": uuid4(), "correlation": correlation})
        connection.execute(text(
            "INSERT INTO outbox_events (event, object_id, account_version, payload) "
            "VALUES ('RECONCILIATION_FAILED', :object, :version, CAST(:payload AS json))"),
            {"object": uuid4(), "version": account["version"],
             "payload": json.dumps({"failed_checks": failed, "correlation_id": correlation})})
    return {"status": "DISCREPANCY" if failed else "OK", "cash": format(journal_cash, "f"), "failed_checks": failed}


def failed_since_clear(connection: Connection) -> list[str]:
    """Every check a reconciliation failed since the last clear (``reconcile_locked`` writes each failure to the
    outbox in the transaction that sets the flags; a clear writes its own boundary)."""
    boundary = connection.execute(text(
        "SELECT COALESCE(max(id), 0) FROM outbox_events WHERE event = 'INTEGRITY_CLEARED'")).scalar_one()
    failed: set[str] = set()
    for payload in connection.execute(text(
            "SELECT payload FROM outbox_events WHERE event = 'RECONCILIATION_FAILED' AND id > :boundary"),
            {"boundary": boundary}).scalars():
        failed.update((payload or {}).get("failed_checks") or [])
    return sorted(failed)
