"""Engine-only virtual USDT accounting authority.

All financial writes lock the singleton account and commit journal, projections,
owner decision, audit and outbox together. No browser-supplied balance is used.
The initial contribution is the app's own (ExecPlan 0042: no owner setup): the API
posts it once at its start (``fund_by_itself``); top-ups are the owner's.
Only the execution worker posts fill journals; this module posts funding journals only.

Since ExecPlan 0060 the account is spot only: USDT and BTC. A top-up values the
account at ``VALUATION_BID_V1`` (cash plus the BTC held at the newest best bid at
most 5 s old, floored to 0.00000001); without a fresh bid while BTC is held it stays
PENDING_VALUATION. The dust of SOL, ZEC, NEAR or XRP that M3 to M10's sales left
(below each coin's minimum order) is kept with its postings and not valued
(``SPOT_POLICY_V1``'s dust rule). The reconciliation is ``app.spot.reconcile``'s.
"""

import hashlib
import json
import re
from decimal import ROUND_HALF_EVEN, Context, Decimal, InvalidOperation, localcontext
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db import get_engine
from app.spot import reconcile as spot_reconcile
from app.spot.definitions import BASE, POLICY
from app.spot.money import equity as bid_equity

AMOUNT = Decimal("0.00000001")
PRECISE = Decimal("0.000000000000000000000000000000000001")
FINANCIAL_CONTEXT = Context(prec=96, rounding=ROUND_HALF_EVEN)
MONEY_MAX = Decimal(f"{'9' * 30}.{'9' * 8}")  # NUMERIC(38, 8)
PRECISE_MAX = Decimal(f"{'9' * 36}.{'9' * 36}")  # NUMERIC(72, 36)
INITIAL_AMOUNT = Decimal("10000.00000000")
INITIAL_NAV = Decimal("100")
KEY_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,80}$")
# The app's initial contribution (ExecPlan 0042 section 4.3): outside KEY_PATTERN, so no owner request can take it.
SYSTEM_FUNDING_KEY = "SYSTEM:INITIALIZE"
SYSTEM_CORRELATION = "SYSTEM_INITIAL_FUNDING"
DECIMAL_PATTERN = re.compile(r"^(?:0|[1-9][0-9]{0,21})(?:\.[0-9]{1,8})?$")


class AccountingError(Exception):
    def __init__(self, code: str, status: int = 400):
        self.code = code
        self.status = status
        super().__init__(code)


def _fit(value: Decimal, quantum: Decimal, maximum: Decimal) -> Decimal:
    """Reject values that PostgreSQL would round or cannot store exactly."""
    if not value.is_finite() or abs(value) > maximum:
        raise AccountingError("NUMERIC_LIMIT", 409)
    try:
        with localcontext(FINANCIAL_CONTEXT):
            if value != value.quantize(quantum):
                raise AccountingError("NUMERIC_LIMIT", 409)
    except InvalidOperation as exc:
        raise AccountingError("NUMERIC_LIMIT", 409) from exc
    return value


def parse_amount(raw: str) -> Decimal:
    if not DECIMAL_PATTERN.fullmatch(raw):
        raise AccountingError("INVALID_AMOUNT")
    value = Decimal(raw)
    if not value.is_finite() or value <= 0 or value > Decimal("9999999999999999999999"):
        raise AccountingError("INVALID_AMOUNT")
    with localcontext(FINANCIAL_CONTEXT):
        return _fit(value.quantize(AMOUNT), AMOUNT, MONEY_MAX)


def unitize(amount: Decimal, equity_before: Decimal, units_before: Decimal) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Return pre-flow NAV, issued units, rounding residual and post-flow NAV."""
    if amount <= 0 or equity_before <= 0 or units_before <= 0:
        raise AccountingError("INVALID_VALUATION", 409)
    with localcontext(FINANCIAL_CONTEXT):
        nav_before = (equity_before / units_before).quantize(PRECISE)
        if nav_before <= 0:
            raise AccountingError("INVALID_VALUATION", 409)
        issued = (amount / nav_before).quantize(PRECISE)
        if issued <= 0:
            raise AccountingError("INVALID_VALUATION", 409)
        residual = (amount - issued * nav_before).quantize(PRECISE)
        nav_after = ((equity_before + amount) / (units_before + issued)).quantize(PRECISE)
        for value in (nav_before, issued, residual, nav_after):
            _fit(value, PRECISE, PRECISE_MAX)
    return nav_before, issued, residual, nav_after


def amount_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _hash(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _locked_account(connection):
    return connection.execute(text("SELECT * FROM account_state WHERE id=1 FOR UPDATE")).mappings().one()


def _holdings(connection) -> dict[str, dict[str, Decimal]]:
    rows = connection.execute(text(
        "SELECT asset, quantity, reserved FROM account_holdings ORDER BY asset = :base DESC, asset"),
        {"base": BASE}).mappings().all()
    return {row["asset"]: {"quantity": row["quantity"], "reserved": row["reserved"]} for row in rows}


def _btc(held: dict[str, dict[str, Decimal]]) -> Decimal:
    return held.get(BASE, {"quantity": Decimal(0)})["quantity"]


def _fresh_bid(connection) -> dict[str, Any] | None:
    """The newest stored best bid when at most ``SPOT_POLICY_V1``'s 5 s old by the database's clock."""
    row = connection.execute(text(
        "SELECT bid, second_at, abs(extract(epoch FROM clock_timestamp() - received_at)) * 1000 <= :age AS fresh "
        "FROM spot_quotes ORDER BY second_at DESC LIMIT 1"), {"age": POLICY.bid_max_age_ms}).mappings().first()
    return dict(row) if row is not None and row["fresh"] else None


def _latest_valuation(connection) -> dict[str, Any] | None:
    row = connection.execute(text(
        "SELECT valued_at, equity, nav, quality, reason, account_version, bid FROM spot_valuations "
        "ORDER BY valued_at DESC, recorded_at DESC LIMIT 1"
    )).mappings().first()
    return dict(row) if row else None


def current_valuation(row, quantity: Decimal, latest: dict[str, Any] | None) -> tuple[Decimal, Decimal] | None:
    """The equity and NAV an account holding BTC shows: the newest persisted valuation's (the execution worker values
    it at the best bid every minute, and at its next step after a top-up). When the account changed after it (a
    top-up the engine has not valued yet), its cash and BTC now at that valuation's bid (``VALUATION_BID_V1``), so a
    contribution never reads as a loss. None while no valid valuation can be shown."""
    if latest is None or latest["quality"] != "VALID" or not row["valuation_valid"]:
        return None
    if latest["account_version"] == row["version"]:
        return latest["equity"], latest["nav"]
    if latest["bid"] is None or row["units"] <= 0:
        return None
    equity = bid_equity(row["cash"], quantity, latest["bid"])
    with localcontext(FINANCIAL_CONTEXT):
        return equity, (equity / row["units"]).quantize(PRECISE)


def _account_payload(row, held: dict[str, dict[str, Decimal]], latest: dict[str, Any] | None) -> dict:
    """A cash-only account (no BTC) values at cash; one holding BTC shows its current valuation
    (``current_valuation``)."""
    with localcontext(FINANCIAL_CONTEXT):
        available = _fit(row["cash"] - row["reserved"], AMOUNT, MONEY_MAX)
    if _btc(held) == 0:
        source = "CASH_ONLY"
        valid = row["valuation_valid"]
        equity = row["cash"] if valid else None
        nav = row["nav"] if valid else None
        valued_at = None
    elif (shown := current_valuation(row, _btc(held), latest)) is not None:
        source = "PERSISTED_VALUATION"
        (equity, nav), valued_at, valid = shown, latest["valued_at"], True
    else:
        source = "UNAVAILABLE"
        equity, nav, valued_at, valid = None, None, latest["valued_at"] if latest else None, False
    with localcontext(FINANCIAL_CONTEXT):
        pnl = _fit(equity - row["contributions"], AMOUNT, MONEY_MAX) if equity is not None else None
    return {
        "id": 1,
        "denomination": "USDT (virtual)",
        "initialized": row["initialized"],
        "version": row["version"],
        "cash": amount_text(row["cash"]),
        "reserved": amount_text(row["reserved"]),
        "available": amount_text(available),
        "contributions": amount_text(row["contributions"]),
        "equity": amount_text(equity),
        "valuation_status": "VALID" if valid else "UNAVAILABLE",
        "valuation_source": source,
        "valued_at": valued_at.isoformat() if valued_at else None,
        "units": amount_text(row["units"]),
        "nav": amount_text(nav),
        "high_water_nav": amount_text(row["high_water_nav"]),
        "pnl": amount_text(pnl),
        "paused": row["paused"],
        "reconciliation_failed": row["reconciliation_failed"],
        # BTC first; the other coins' rows are M3 to M10's dust, kept with its postings and not valued.
        "holdings": [
            {"asset": asset, "quantity": amount_text(value["quantity"]),
             "reserved": amount_text(value["reserved"]),
             "available": amount_text(value["quantity"] - value["reserved"]),
             "valued": asset == BASE}
            for asset, value in held.items() if asset == BASE or value["quantity"] != 0
        ],
    }


def _snapshot(connection) -> dict:
    row = connection.execute(text("SELECT * FROM account_state WHERE id=1")).mappings().one()
    return _account_payload(row, _holdings(connection), _latest_valuation(connection))


def account_snapshot() -> dict:
    with get_engine().connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        return _snapshot(connection)


def workspace_snapshot(limit: int = 50) -> dict:
    """Return account and bounded funding history from one database snapshot."""
    with get_engine().connect().execution_options(isolation_level="REPEATABLE READ") as connection:
        account = _snapshot(connection)
        funding = connection.execute(
            text("SELECT * FROM funding_requests ORDER BY created_at DESC, id DESC LIMIT :limit"),
            {"limit": limit},
        ).mappings().all()
    return {"account": account, "funding": [_funding_payload(row) for row in funding]}


def funding_by_key(key: str) -> dict | None:
    # The app's own key is read too: the initial contribution is shown by it (ExecPlan 0042).
    if key != SYSTEM_FUNDING_KEY and not KEY_PATTERN.fullmatch(key):
        raise AccountingError("INVALID_IDEMPOTENCY_KEY")
    with get_engine().connect() as connection:
        row = connection.execute(
            text("SELECT * FROM funding_requests WHERE idempotency_key=:key"),
            {"key": key},
        ).mappings().first()
    return _funding_payload(row) if row else None


def _funding_payload(row) -> dict:
    return {
        "id": str(row["id"]),
        "kind": row["kind"],
        "amount": amount_text(row["amount"]),
        "status": row["status"],
        "idempotency_key": row["idempotency_key"],
        "expected_version": row["expected_version"],
        "preflow_nav": amount_text(row["preflow_nav"]),
        "issued_units": amount_text(row["issued_units"]),
        "unit_residual": amount_text(row["unit_residual"]),
        "journal_tx_id": str(row["journal_tx_id"]) if row["journal_tx_id"] else None,
        "created_at": row["created_at"].isoformat(),
        "completed_at": row["completed_at"].isoformat() if row["completed_at"] else None,
    }


def _payload(kind: str, amount: Decimal, version: int) -> dict:
    return {"account_id": 1, "amount": amount_text(amount), "denomination": "USDT (virtual)", "kind": kind,
            "version": version}


def draft(kind: str, raw_amount: str | None = None) -> dict:
    """The owner's top-up draft. ``kind`` is TOPUP: the initial contribution is the app's (``fund_by_itself``)."""
    if kind != "TOPUP":
        raise AccountingError("INVALID_FUNDING_KIND")
    amount = parse_amount(raw_amount or "")
    with get_engine().connect() as connection:
        row = connection.execute(text("SELECT * FROM account_state WHERE id=1")).mappings().one()
    if not row["initialized"]:
        raise AccountingError("ACCOUNT_NOT_INITIALIZED", 409)
    payload = _payload(kind, amount, row["version"])
    return {**payload, "draft_hash": _hash(payload), "valuation_status": "VALID" if row["valuation_valid"] else "UNAVAILABLE"}


def _audit_outbox(connection, event: str, request_id: UUID, version: int, correlation_id: str,
                  detail: dict[str, Any] | None = None) -> None:
    connection.execute(
        text("INSERT INTO audit_events(id,event,correlation_id,object_id) VALUES (:id,:event,:correlation,:object)"),
        {"id": uuid4(), "event": event, "correlation": correlation_id, "object": request_id},
    )
    payload = {"request_id": str(request_id), "status": event, **(detail or {})}
    connection.execute(
        text("INSERT INTO outbox_events(event,object_id,account_version,payload) VALUES (:event,:object,:version,CAST(:payload AS json))"),
        {"event": event, "object": request_id, "version": version, "payload": json.dumps(payload, sort_keys=True)},
    )


def _preflow_equity(connection, account) -> tuple[Decimal | None, dict[str, Any]]:
    """``VALUATION_BID_V1``: cash plus the BTC held at the newest best bid at most 5 s old; None while BTC is held
    without one. The other coins' dust is not valued (``SPOT_POLICY_V1``)."""
    quantity = _btc(_holdings(connection))
    if quantity == 0:
        return account["cash"], {"valuation": "CASH_ONLY"}
    bid = _fresh_bid(connection)
    evidence = {"valuation": "VALUATION_BID_V1", "btc": amount_text(quantity),
                "bid": amount_text(bid["bid"]) if bid else None,
                "bid_second": bid["second_at"].isoformat() if bid else None}
    if bid is None:
        return None, {**evidence, "reason": "BID_STALE"}
    return _fit(bid_equity(account["cash"], quantity, bid["bid"]), AMOUNT, MONEY_MAX), evidence


def _post_funding(connection, account, request_id: UUID, kind: str, amount: Decimal, correlation_id: str) -> None:
    if account["reconciliation_failed"]:
        raise AccountingError("RECONCILIATION_REQUIRED", 409)
    if account["paused"]:
        raise AccountingError("POLICY_PAUSED", 409)
    if not account["valuation_valid"]:
        return
    evidence: dict[str, Any] = {"valuation": "CASH_ONLY"}
    if kind == "INITIALIZE":
        if account["initialized"]:
            raise AccountingError("ALREADY_INITIALIZED", 409)
        nav_before = INITIAL_NAV
        equity_before = Decimal(0)
        issued = Decimal(100)
        high_water = INITIAL_NAV
    else:
        if not account["initialized"] or account["units"] <= 0:
            raise AccountingError("INVALID_VALUATION", 409)
        equity_before, evidence = _preflow_equity(connection, account)
        if equity_before is None:
            return  # holdings without fresh marks: remain PENDING_VALUATION
        if equity_before <= 0:
            raise AccountingError("INVALID_VALUATION", 409)
        nav_before, issued, residual, new_nav = unitize(amount, equity_before, account["units"])
        # Top-ups never move the high-water mark, daily references or latches.
        high_water = account["high_water_nav"]
    with localcontext(FINANCIAL_CONTEXT):
        new_cash = _fit(account["cash"] + amount, AMOUNT, MONEY_MAX)
        new_contributions = _fit(account["contributions"] + amount, AMOUNT, MONEY_MAX)
        new_units = _fit(account["units"] + issued, PRECISE, PRECISE_MAX)
        if kind == "INITIALIZE":
            residual = (amount - issued * nav_before).quantize(PRECISE)
            new_nav = (new_cash / new_units).quantize(PRECISE)
        _fit(residual, PRECISE, PRECISE_MAX)
        _fit(new_nav, PRECISE, PRECISE_MAX)
    version = account["version"] + 1
    tx_id = uuid4()
    connection.execute(
        text("INSERT INTO journal_transactions(id,funding_request_id,account_version) VALUES (:id,:request,:version)"),
        {"id": tx_id, "request": request_id, "version": version},
    )
    for book, signed in (("OWNER_CASH", amount), ("VIRTUAL_CAPITAL", -amount)):
        connection.execute(
            text("INSERT INTO journal_postings(tx_id,asset,book_account,amount) VALUES (:tx,'USDT',:book,:amount)"),
            {"tx": tx_id, "book": book, "amount": signed},
        )
    connection.execute(
        text("""UPDATE account_state SET version=:version, initialized=true, cash=:cash,
            contributions=:contributions, units=:units, nav=:nav, high_water_nav=:high_water
            WHERE id=1"""),
        {"version": version, "cash": new_cash, "contributions": new_contributions, "units": new_units, "nav": new_nav, "high_water": high_water},
    )
    connection.execute(
        text("""UPDATE funding_requests SET status='POSTED', preflow_equity=:equity,
            preflow_nav=:nav, issued_units=:units, unit_residual=:residual,
            journal_tx_id=:tx, completed_at=now() WHERE id=:id"""),
        {"equity": equity_before, "nav": nav_before, "units": issued, "residual": residual, "tx": tx_id, "id": request_id},
    )
    _audit_outbox(connection, "FUNDING_POSTED", request_id, version, correlation_id, evidence)


def confirm(kind: str, raw_amount: str, expected_version: int, draft_hash: str, key: str, correlation_id: str) -> dict:
    """The owner's confirmation of a top-up draft (``kind`` TOPUP, as ``draft``)."""
    if kind != "TOPUP":
        raise AccountingError("INVALID_FUNDING_KIND")
    amount = parse_amount(raw_amount)
    if not KEY_PATTERN.fullmatch(key):
        raise AccountingError("INVALID_IDEMPOTENCY_KEY")
    payload = _payload(kind, amount, expected_version)
    if draft_hash != _hash(payload):
        raise AccountingError("DRAFT_MISMATCH", 409)
    request_hash = _hash({**payload, "draft_hash": draft_hash})
    with get_engine().begin() as connection:
        account = _locked_account(connection)
        existing = connection.execute(text("SELECT * FROM funding_requests WHERE idempotency_key=:key"), {"key": key}).mappings().first()
        if existing:
            if existing["request_hash"] != request_hash:
                raise AccountingError("IDEMPOTENCY_CONFLICT", 409)
            return _funding_payload(existing)
        if account["version"] != expected_version:
            raise AccountingError("ACCOUNT_VERSION_CONFLICT", 409)
        if not account["initialized"]:
            raise AccountingError("ACCOUNT_NOT_INITIALIZED", 409)
        if account["reconciliation_failed"]:
            raise AccountingError("RECONCILIATION_REQUIRED", 409)
        request_id = uuid4()
        initial_status = "PENDING_VALUATION"
        connection.execute(
            text("""INSERT INTO funding_requests(id,kind,amount,idempotency_key,request_hash,
                draft_hash,expected_version,status) VALUES (:id,:kind,:amount,:key,:hash,:draft,:version,:status)"""),
            {"id": request_id, "kind": kind, "amount": amount, "key": key, "hash": request_hash, "draft": draft_hash, "version": expected_version, "status": initial_status},
        )
        connection.execute(
            text("INSERT INTO owner_decisions(id,funding_request_id,action,target_hash,account_version) VALUES (:id,:request,'CONFIRM',:hash,:version)"),
            {"id": uuid4(), "request": request_id, "hash": draft_hash, "version": expected_version},
        )
        _audit_outbox(connection, "FUNDING_PENDING", request_id, expected_version, correlation_id)
        _post_funding(connection, account, request_id, kind, amount, correlation_id)
        row = connection.execute(text("SELECT * FROM funding_requests WHERE id=:id"), {"id": request_id}).mappings().one()
    return _funding_payload(row)


def resolve_pending(request_id: UUID, action: str, correlation_id: str) -> dict:
    if action not in ("RETRY", "CANCEL"):
        raise AccountingError("INVALID_ACTION")
    with get_engine().begin() as connection:
        account = _locked_account(connection)
        row = connection.execute(text("SELECT * FROM funding_requests WHERE id=:id FOR UPDATE"), {"id": request_id}).mappings().first()
        if row is None:
            raise AccountingError("REQUEST_NOT_FOUND", 404)
        if row["status"] == "CANCELED" and action == "CANCEL":
            return _funding_payload(row)
        if row["status"] != "PENDING_VALUATION":
            raise AccountingError("REQUEST_NOT_PENDING", 409)
        if action == "CANCEL" and row["kind"] == "INITIALIZE" and not account["initialized"]:
            # The initial contribution is the app's (ExecPlan 0042): canceled, nothing could fund the account.
            raise AccountingError("INITIAL_FUNDING_NOT_CANCELABLE", 409)
        connection.execute(
            text("INSERT INTO owner_decisions(id,funding_request_id,action,target_hash,account_version) VALUES (:id,:request,:action,:hash,:version)"),
            {"id": uuid4(), "request": request_id, "action": action, "hash": row["request_hash"], "version": account["version"]},
        )
        if action == "CANCEL":
            connection.execute(text("UPDATE funding_requests SET status='CANCELED', completed_at=now() WHERE id=:id"), {"id": request_id})
            _audit_outbox(connection, "FUNDING_CANCELED", request_id, account["version"], correlation_id)
        else:
            if not account["valuation_valid"]:
                raise AccountingError("VALUATION_UNAVAILABLE", 409)
            _post_funding(connection, account, request_id, row["kind"], row["amount"], correlation_id)
            posted = connection.execute(text("SELECT status FROM funding_requests WHERE id=:id"), {"id": request_id}).scalar_one()
            if posted != "POSTED":
                raise AccountingError("VALUATION_UNAVAILABLE", 409)
        result = connection.execute(text("SELECT * FROM funding_requests WHERE id=:id"), {"id": request_id}).mappings().one()
    return _funding_payload(result)



def fund_by_itself() -> dict[str, Any]:
    """The account's initial contribution, by the app itself (ExecPlan 0042 section 4.3; the owner's decision of
    2026-10-25: no setup). On an account nothing has funded it records the initial funding request under
    ``SYSTEM_FUNDING_KEY``, with the hashes the owner's confirmation computed, and posts it through
    ``_post_funding`` as before: ``INITIAL_AMOUNT`` virtual USDT, NAV 100, 100 units. No owner decision is recorded.

    The API runs it at its start, and again every minute while it is refused (``main.keep_funding``). A funded
    account stays funded, so it is read first without the lock; under the account's row lock a second process finds
    the account funded. Nothing is posted while the reconciliation has failed or the account is paused; a request an
    operator's valuation override holds (``PENDING_VALUATION``) is posted by a later call (``resolve_pending`` refuses
    to cancel it while the account is not funded). Returns ``{"status": ...}``: ``FUNDED`` (nothing to do),
    ``POSTED``, ``PENDING_VALUATION``, ``RECONCILIATION_REQUIRED``, ``POLICY_PAUSED``, or the status of the app's own
    request when it ended otherwise (``CANCELED`` only by an app from before ExecPlan 0042, after a rollback)."""
    with get_engine().connect() as connection:
        if connection.execute(text("SELECT initialized FROM account_state WHERE id=1")).scalar_one():
            return {"status": "FUNDED"}
    with get_engine().begin() as connection:
        account = _locked_account(connection)
        if account["initialized"]:
            return {"status": "FUNDED"}
        if account["reconciliation_failed"]:
            return {"status": "RECONCILIATION_REQUIRED"}
        if account["paused"]:
            return {"status": "POLICY_PAUSED"}
        row = connection.execute(text(
            "SELECT * FROM funding_requests WHERE kind='INITIALIZE' AND status='PENDING_VALUATION' "
            "ORDER BY created_at, id LIMIT 1 FOR UPDATE")).mappings().first()
        if row is None:
            ours = connection.execute(text("SELECT status FROM funding_requests WHERE idempotency_key=:key"),
                                      {"key": SYSTEM_FUNDING_KEY}).scalar_one_or_none()
            if ours is not None:
                return {"status": ours}
            payload = _payload("INITIALIZE", INITIAL_AMOUNT, account["version"])
            draft_hash = _hash(payload)
            request_id = uuid4()
            connection.execute(
                text("""INSERT INTO funding_requests(id,kind,amount,idempotency_key,request_hash,
                    draft_hash,expected_version,status) VALUES (:id,'INITIALIZE',:amount,:key,:hash,:draft,:version,
                    'PENDING_VALUATION')"""),
                {"id": request_id, "amount": INITIAL_AMOUNT, "key": SYSTEM_FUNDING_KEY,
                 "hash": _hash({**payload, "draft_hash": draft_hash}), "draft": draft_hash,
                 "version": account["version"]},
            )
            _audit_outbox(connection, "FUNDING_PENDING", request_id, account["version"], SYSTEM_CORRELATION,
                          {"by": "SYSTEM"})
            amount = INITIAL_AMOUNT
        else:
            request_id, amount = row["id"], row["amount"]
        _post_funding(connection, account, request_id, "INITIALIZE", amount, SYSTEM_CORRELATION)
        status = connection.execute(text("SELECT status FROM funding_requests WHERE id=:id"),
                                    {"id": request_id}).scalar_one()
    return {"status": status, "request_id": str(request_id)}


def reconcile_with(engine: Engine) -> dict[str, Any]:
    """``app.spot.reconcile``'s checks under the account's row lock (the API's start; the execution worker runs them
    under its fence)."""
    with engine.begin() as connection:
        return spot_reconcile.reconcile_locked(connection, dict(_locked_account(connection)))


def reconcile() -> dict:
    """Rebuild comparisons from append-only source records; latch on mismatch."""
    result = reconcile_with(get_engine())
    return {"status": result["status"], "cash": result["cash"], "failed_checks": result["failed_checks"]}
