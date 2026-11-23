"""The spot account's reads for the pages (ExecPlan 0060 section 4.9): the Cockpit's overview, the trades, the daily
readings, the chart's markers, the account's value curve, the toasts' feed and the backtest.

As the API identity, in one repeatable-read snapshot each; until migration 0041 is applied each reports the schema as
pending. Every number is a stored record or a calculation from stored records here (the share in Bitcoin, the fall
from the run's high, the change since the day's reference); none is a forecast.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal, localcontext
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.accounting import current_valuation
from app.execution.numbers import CONTEXT, ONE
from app.spot.definitions import BASE, POLICY, RULE
from app.spot_market.views import connect, database_now, iso, plain, ready

ACTIVITY_MAX = 20
MARKERS_MAX = 500
PAGE_MAX = 100
RATIO = Decimal("0.00000001")
# The Cockpit's value curve: each window's span and the width of the buckets it is drawn in, so a window holds at most
# a few hundred points; all of the account's history in four-hour buckets.
VALUATION_WINDOWS: dict[str, tuple[timedelta | None, int]] = {
    "24h": (timedelta(hours=24), 15 * 60), "7d": (timedelta(days=7), 60 * 60), "all": (None, 4 * 60 * 60)}
BACKTEST_WINDOWS = ("SINCE_2019", "SINCE_2023", "LAST_12_MONTHS")


def ratio(value: Decimal) -> str:
    with localcontext(CONTEXT):
        return plain(value.quantize(RATIO)) or "0"


def _now(connection: Connection, at: datetime | None) -> datetime:
    """The database's clock, or ``at`` (the tests' synthetic time)."""
    return at or database_now(connection)


def _identity(row: Any, prefix: str) -> dict[str, str]:
    return {"id": row[f"{prefix}_id"], "sha256": row[f"{prefix}_sha256"]}


# ---- the shared rows -----------------------------------------------------------------------------------------------

READING_SQL = ("SELECT r.*, f.side AS fill_side, f.quantity AS fill_quantity, f.price AS fill_price, "
               "f.fee AS fill_fee, f.gross AS fill_gross FROM spot_rule_readings r "
               "LEFT JOIN spot_fills f ON f.id = r.fill_id")


def _anchors(features: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"lookback_days": int(anchor["lookback_days"]),
             "day": datetime.fromtimestamp(int(anchor["day_open_ms"]) / 1000, tz=UTC).date().isoformat(),
             "close": anchor["close"], "sign": int(anchor["sign"])} for anchor in features.get("anchors") or []]


def _reading(row: Any) -> dict[str, Any]:
    anchors = _anchors(row["features"])
    return {
        "id": str(row["id"]), "seq": str(row["seq"]), "run_id": str(row["run_id"]),
        "utc_date": row["utc_date"].isoformat(),
        "day_read": datetime.fromtimestamp(row["day_open_ms"] / 1000, tz=UTC).date().isoformat(),
        "at": iso(row["at"]), "result": row["result"], "reason": row["reason"], "close": plain(row["close"]),
        "signal": plain(row["signal"]), "volatility": plain(row["volatility"]), "target": plain(row["target"]),
        "held": plain(row["held"]), "action": row["action"], "outcome": row["outcome"], "codes": list(row["codes"]),
        "spent": row["spent"], "anchors": anchors, "up": sum(1 for anchor in anchors if anchor["sign"] > 0),
        "fill": None if row["fill_id"] is None else {
            "id": str(row["fill_id"]), "side": row["fill_side"], "quantity": plain(row["fill_quantity"]),
            "price": plain(row["fill_price"]), "fee": plain(row["fill_fee"]), "gross": plain(row["fill_gross"])},
    }


TRADE_SQL = ("SELECT f.*, u.seq AS run_seq, u.stop_reason, r.utc_date AS reading_date, r.target AS reading_target, "
             "r.held AS reading_held, r.features AS reading_features FROM spot_fills f "
             "JOIN spot_runs u ON u.id = f.run_id LEFT JOIN spot_rule_readings r ON r.fill_id = f.id")


def _trade(row: Any) -> dict[str, Any]:
    reading = None
    if row["reading_date"] is not None:
        anchors = _anchors(row["reading_features"])
        reading = {"utc_date": row["reading_date"].isoformat(), "target": plain(row["reading_target"]),
                   "held": plain(row["reading_held"]), "up": sum(1 for anchor in anchors if anchor["sign"] > 0),
                   "anchors": len(anchors)}
    return {
        "id": str(row["id"]), "seq": str(row["seq"]), "run_id": str(row["run_id"]), "run_seq": str(row["run_seq"]),
        "reason": row["reason"], "side": row["side"], "quantity": plain(row["quantity"]), "price": plain(row["price"]),
        "average_price": plain(row["average_price"]), "slippage_bps": plain(row["slippage_bps"]),
        "gross": plain(row["gross"]), "fee": plain(row["fee"]), "fee_rate": plain(row["fee_rate"]),
        "cash_after": plain(row["cash_after"]), "quantity_after": plain(row["quantity_after"]),
        "filled_at": iso(row["filled_at"]), "book_second": iso(row["quote_second"]),
        "stop_reason": row["stop_reason"] if row["reason"] == "STOP_SELL" else None, "reading": reading,
    }


def _run(row: Any) -> dict[str, Any]:
    return {
        "id": str(row["id"]), "seq": str(row["seq"]), "state": row["state"], "causes": list(row["causes"]),
        "started_at": iso(row["started_at"]), "started_by": row["started_by"],
        "start_equity": plain(row["start_equity"]), "start_nav": plain(row["start_nav"]),
        "high_water_nav": plain(row["high_water_nav"]), "stopped_at": iso(row["stopped_at"]),
        "stop_reason": row["stop_reason"], "version": row["version"], "code_identity": row["code_identity"],
        "rule": _identity(row, "rule"), "policy": _identity(row, "policy"), "cost": _identity(row, "cost"),
    }


# ---- the Cockpit --------------------------------------------------------------------------------------------------

def _since_start(connection: Connection, run: Any, now: datetime) -> dict[str, Any] | None:
    """The run against holding Bitcoin, paired by day (ExecPlan 0061 section 4.3; ExecPlan 0060 section 4.10's
    descriptive comparison): between the run's first and newest TIMELY daily references (the account's first valid
    valuation within five minutes after a UTC midnight), the run's NAV per unit (a top-up moves neither side) against
    Bitcoin's daily close of the day before each (its last price at that midnight). Both sides are stored records that
    are kept, so the line holds for a run of any length; ``None`` until the run has two such days."""
    bounds = {"run": run["id"], "since": run["started_at"], "until": run["stopped_at"] or now}
    paired = ("SELECT v.valued_at, v.nav, b.close FROM spot_daily_references r "
              "JOIN spot_valuations v ON v.id = r.valuation_id "
              "JOIN spot_daily_bars b ON b.open_ms = (r.utc_date - DATE '1970-01-02')::bigint * 86400000 "
              "WHERE r.quality = 'TIMELY' AND v.run_id = :run AND v.quality = 'VALID' "
              "AND v.valued_at >= :since AND v.valued_at <= :until ORDER BY r.utc_date")
    first = connection.execute(text(f"{paired} LIMIT 1"), bounds).mappings().first()
    last = connection.execute(text(f"{paired} DESC LIMIT 1"), bounds).mappings().first()
    if first is None or last is None or first["valued_at"] == last["valued_at"]:
        return None
    with localcontext(CONTEXT):
        account, bitcoin = last["nav"] / first["nav"] - ONE, last["close"] / first["close"] - ONE
    return {"from_at": iso(first["valued_at"]), "from_price": plain(first["close"]), "at": iso(last["valued_at"]),
            "price": plain(last["close"]), "account": ratio(account), "bitcoin": ratio(bitcoin)}


def _pending_overview() -> dict[str, Any]:
    return {"state": "SCHEMA_PENDING", "evaluated_at": None, "account": None, "run": None, "latches": [],
            "limits": None, "today": None, "last_reading": None, "fills": 0}


def _account(connection: Connection) -> dict[str, Any]:
    """The account's cash and BTC with its newest valuation, as the account's own read shows it: a cash-only account
    values at its cash, one holding BTC at the execution worker's newest valuation (each minute while it holds)."""
    row = connection.execute(text("SELECT * FROM account_state WHERE id = 1")).mappings().one()
    btc = connection.execute(text("SELECT quantity FROM account_holdings WHERE asset = :asset"),
                             {"asset": BASE}).scalar_one_or_none() or Decimal(0)
    valuation = connection.execute(text(
        "SELECT valued_at, cash, quantity, bid, equity, nav, quality, account_version FROM spot_valuations "
        "ORDER BY valued_at DESC, recorded_at DESC LIMIT 1")).mappings().first()
    equity = nav = share = btc_value = bid = valued_at = None
    if btc == 0:
        if row["valuation_valid"]:
            equity, nav, share, btc_value = row["cash"], row["nav"], Decimal(0), Decimal(0)
    elif (shown := current_valuation(row, btc, valuation)) is not None:
        # The account's own read's value: the newest valuation, or after a top-up it has not seen, the cash and BTC
        # now at its bid.
        (equity, nav), bid, valued_at = shown, valuation["bid"], valuation["valued_at"]
        with localcontext(CONTEXT):
            btc_value = equity - row["cash"]
            share = btc_value / equity if equity > 0 else None
    if valuation is not None and valued_at is None and btc != 0:
        valued_at = valuation["valued_at"]
    with localcontext(CONTEXT):
        pnl = equity - row["contributions"] if equity is not None else None
    return {
        "initialized": row["initialized"], "version": row["version"], "cash": plain(row["cash"]), "btc": plain(btc),
        "btc_value": plain(btc_value), "equity": plain(equity), "share": None if share is None else ratio(share),
        "bid": plain(bid), "valued_at": iso(valued_at), "valuation": "VALID" if equity is not None else "UNAVAILABLE",
        "units": plain(row["units"]), "nav": plain(nav), "contributions": plain(row["contributions"]),
        "pnl": plain(pnl), "paused": row["paused"], "reconciliation_failed": row["reconciliation_failed"],
    }


def _today(connection: Connection, run: Any, now: datetime) -> dict[str, Any]:
    """Today's reading: ``WAITING`` before 00:05 UTC, ``DUE`` once it may be read, ``RETRYING`` after a reading that
    tries again (every 15 minutes), ``SPENT`` once read; ``NONE`` without a run that reads."""
    midnight = now.astimezone(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    read_at = midnight + timedelta(milliseconds=RULE.read_after_ms)
    today = midnight.date()
    if run is None or run["state"] in ("STOPPING", "STOPPED"):
        return {"utc_date": today.isoformat(), "status": "NONE", "next_reading_at": None,
                "retry_seconds": RULE.retry_seconds}
    rows = connection.execute(text(
        "SELECT spent FROM spot_rule_readings WHERE run_id = :run AND utc_date = :day"),
        {"run": run["id"], "day": today}).scalars().all()
    if now < read_at:
        status, next_at = "WAITING", read_at
    elif any(rows):
        status, next_at = "SPENT", read_at + timedelta(days=1)
    else:
        status, next_at = ("RETRYING" if rows else "DUE"), None
    return {"utc_date": today.isoformat(), "status": status, "next_reading_at": iso(next_at),
            "retry_seconds": RULE.retry_seconds}


def overview(engine=None, at: datetime | None = None) -> dict[str, Any]:
    """The Cockpit's and Settings' read: the account, the run, its latches and limits, and the rule's day."""
    if not ready():
        return _pending_overview()
    with connect(engine) as connection:
        now = _now(connection, at)
        account = _account(connection)
        run = connection.execute(text("SELECT * FROM spot_runs ORDER BY seq DESC LIMIT 1")).mappings().first()
        latches, last_reading, reference = [], None, None
        if run is not None:
            latches = connection.execute(text(
                "SELECT cause, latched_at FROM spot_latches WHERE run_id = :run AND resolved_at IS NULL "
                "ORDER BY latched_at"), {"run": run["id"]}).mappings().all()
            last_reading = connection.execute(text(
                f"{READING_SQL} WHERE r.run_id = :run ORDER BY r.seq DESC LIMIT 1"), {"run": run["id"]}
            ).mappings().first()
        reference = connection.execute(text("SELECT nav FROM spot_daily_references WHERE utc_date = :day"),
                                       {"day": now.astimezone(UTC).date()}).scalar_one_or_none()
        today = _today(connection, run, now)
        since_start = None if run is None else _since_start(connection, run, now)
        fills = connection.execute(text("SELECT count(*) FROM spot_fills")).scalar_one()
    nav = Decimal(account["nav"]) if account["nav"] is not None else None
    with localcontext(CONTEXT):
        fall = (ONE - nav / run["high_water_nav"]) if nav is not None and run is not None \
            and run["state"] != "STOPPED" else None
        change = (nav / reference - ONE) if nav is not None and reference is not None else None
    return {
        "state": "READY", "evaluated_at": iso(now), "account": account,
        "run": None if run is None else {**_run(run), "since_start": since_start},
        "latches": [{"cause": row["cause"], "latched_at": iso(row["latched_at"])} for row in latches],
        "limits": {"daily_loss": plain(POLICY.daily_loss), "drawdown": plain(POLICY.drawdown),
                   "today_change": None if change is None else ratio(change),
                   "fall_from_high": None if fall is None else ratio(max(fall, Decimal(0)))},
        "today": today, "last_reading": None if last_reading is None else _reading(last_reading),
        "fills": int(fills),
    }


def system_states(engine=None) -> dict[str, str]:
    """Settings' status rows: the newest run's state (``inactive`` before the first), whether the execution worker
    holds its lease, and whether the backtest has been computed."""
    if not ready():
        return {"trading": "unavailable", "execution_worker": "not_running", "backtest": "unavailable"}
    with connect(engine) as connection:
        state = connection.execute(text("SELECT state FROM spot_runs ORDER BY seq DESC LIMIT 1")).scalar_one_or_none()
        lease = connection.execute(text(
            "SELECT owner_id IS NOT NULL AND expires_at > clock_timestamp() FROM execution_lease WHERE id = 1"
        )).scalar_one_or_none()
        computed = connection.execute(text("SELECT EXISTS (SELECT 1 FROM spot_backtests)")).scalar_one()
    return {"trading": state.lower() if state else "inactive", "execution_worker": "running" if lease else "not_running",
            "backtest": "computed" if computed else "not_computed"}


# ---- the lists ----------------------------------------------------------------------------------------------------

def trades(cursor: int | None = None, limit: int = 25, engine=None) -> dict[str, Any]:
    """Every buy and sell, newest first, by its sequence number."""
    if not ready():
        return {"state": "SCHEMA_PENDING", "items": [], "next_cursor": None}
    with connect(engine) as connection:
        rows = connection.execute(text(
            f"{TRADE_SQL} WHERE (CAST(:cursor AS bigint) IS NULL OR f.seq < :cursor) ORDER BY f.seq DESC "
            "LIMIT :limit"), {"cursor": cursor, "limit": limit + 1}).mappings().all()
    page = rows[:limit]
    return {"state": "READY", "items": [_trade(row) for row in page],
            "next_cursor": str(page[-1]["seq"]) if len(rows) > limit else None}


def readings(cursor: int | None = None, limit: int = 25, engine=None) -> dict[str, Any]:
    """Every daily reading, newest first, by its sequence number."""
    if not ready():
        return {"state": "SCHEMA_PENDING", "items": [], "next_cursor": None}
    with connect(engine) as connection:
        rows = connection.execute(text(
            f"{READING_SQL} WHERE (CAST(:cursor AS bigint) IS NULL OR r.seq < :cursor) ORDER BY r.seq DESC "
            "LIMIT :limit"), {"cursor": cursor, "limit": limit + 1}).mappings().all()
    page = rows[:limit]
    return {"state": "READY", "items": [_reading(row) for row in page],
            "next_cursor": str(page[-1]["seq"]) if len(rows) > limit else None}


def activity(after: int | None, limit: int = ACTIVITY_MAX, engine=None) -> dict[str, Any]:
    """The fills after sequence ``after`` (the toasts' feed): the newest ``limit``, oldest first, with how many there
    were in all. Without ``after`` it returns only the cursor to start from."""
    if not ready():
        return {"state": "SCHEMA_PENDING", "cursor": "0", "count": 0, "items": []}
    with connect(engine) as connection:
        cursor = connection.execute(text("SELECT COALESCE(max(seq), 0) FROM spot_fills")).scalar_one()
        if after is None or after >= cursor:
            return {"state": "READY", "cursor": str(cursor), "count": 0, "items": []}
        count = connection.execute(text("SELECT count(*) FROM spot_fills WHERE seq > :after"),
                                   {"after": after}).scalar_one()
        rows = connection.execute(text(
            f"SELECT * FROM ({TRADE_SQL} WHERE f.seq > :after ORDER BY f.seq DESC LIMIT :limit) newest "
            "ORDER BY seq"), {"after": after, "limit": limit}).mappings().all()
    return {"state": "READY", "cursor": str(cursor), "count": int(count), "items": [_trade(row) for row in rows]}


def markers(since_ms: int, engine=None) -> dict[str, Any]:
    """The chart's marks: the fills since ``since_ms`` (the chart's first candle; at most the newest 500)."""
    if not ready():
        return {"state": "SCHEMA_PENDING", "fills": []}
    since = datetime.fromtimestamp(since_ms / 1000, tz=UTC)
    with connect(engine) as connection:
        rows = connection.execute(text(
            "SELECT id, reason, side, quantity, price, filled_at FROM spot_fills WHERE filled_at >= :since "
            "ORDER BY filled_at DESC, seq DESC LIMIT :limit"), {"since": since, "limit": MARKERS_MAX}
        ).mappings().all()
    return {"state": "READY", "fills": [
        {"id": str(row["id"]), "reason": row["reason"], "side": row["side"], "quantity": plain(row["quantity"]),
         "price": plain(row["price"]), "filled_at": iso(row["filled_at"])} for row in reversed(rows)]}


def valuations(window: str, engine=None, at: datetime | None = None) -> dict[str, Any]:
    """The Cockpit's value curve: the account's VALID valuations in the window, the newest of each bucket, with the
    window's first valuation as the curve's base. NAV per unit leaves top-ups out, so the curve's change from its base
    is the account's return; the equity beside it is what the account was worth."""
    span, step = VALUATION_WINDOWS[window]
    if not ready():
        return {"state": "SCHEMA_PENDING", "window": window, "bucket_seconds": step, "since": None, "base_nav": None,
                "points": []}
    with connect(engine) as connection:
        now = _now(connection, at)
        since = None if span is None else now - span
        bounds = {"since": since, "now": now, "step": step}
        window_sql = ("quality = 'VALID' AND valued_at <= :now "
                      "AND (CAST(:since AS timestamptz) IS NULL OR valued_at >= :since)")
        first = connection.execute(text(
            f"SELECT id, valued_at, nav, equity FROM spot_valuations WHERE {window_sql} "
            "ORDER BY valued_at, recorded_at, id LIMIT 1"), bounds).mappings().first()
        rows = connection.execute(text(
            "SELECT id, valued_at, nav, equity FROM (SELECT DISTINCT ON (bucket) valued_at, nav, equity, recorded_at, "
            "id FROM (SELECT valued_at, nav, equity, recorded_at, id, floor(extract(epoch FROM valued_at) / :step) "
            f"AS bucket FROM spot_valuations WHERE {window_sql}) v "
            "ORDER BY bucket, valued_at DESC, recorded_at DESC, id DESC) newest ORDER BY valued_at, recorded_at, id"),
            bounds).mappings().all()
    points = [{"time": iso(row["valued_at"]), "nav": plain(row["nav"]), "equity": plain(row["equity"])}
              for row in ([first] if first is not None and (not rows or rows[0]["id"] != first["id"]) else [])
              + list(rows)]
    return {"state": "READY", "window": window, "bucket_seconds": step, "since": iso(since),
            "base_nav": points[0]["nav"] if points else None, "points": points}


# ---- the backtest -------------------------------------------------------------------------------------------------

def _series(raw: dict[str, Any] | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    return {"days": [int(day) for day in raw["days"]], "rule": raw["rule"], "hold": raw["hold"],
            "target": raw["target"],
            "trades": [{"day_ms": int(day), "side": side, "price": price, "quantity": quantity}
                       for day, side, price, quantity in raw["trades"]]}


def backtest(window: str = "SINCE_2019", engine=None) -> dict[str, Any]:
    """The newest computation of ``SPOT_BACKTEST_V1``: every window's summary and the chosen window's daily series."""
    if window not in BACKTEST_WINDOWS:
        raise ValueError("unknown_backtest_window")
    if not ready():
        return {"state": "SCHEMA_PENDING", "window": window, "computed": None, "series": None}
    with connect(engine) as connection:
        row = connection.execute(text(
            "SELECT id, seq, computed_at, method, label, rule_id, rule_sha256, policy_id, policy_sha256, cost_id, "
            "cost_sha256, code_identity, candles_sha256, result, series -> :window AS series FROM spot_backtests "
            "ORDER BY seq DESC LIMIT 1"), {"window": window}).mappings().first()
    if row is None:
        return {"state": "NOT_COMPUTED", "window": window, "computed": None, "series": None}
    result = row["result"]
    return {
        "state": "READY", "window": window,
        "computed": {
            "id": str(row["id"]), "seq": str(row["seq"]), "computed_at": iso(row["computed_at"]),
            "method": row["method"], "label": row["label"], "rule": _identity(row, "rule"),
            "policy": _identity(row, "policy"), "cost": _identity(row, "cost"), "code_identity": row["code_identity"],
            "candles_sha256": row["candles_sha256"], "start_cash": result["start_cash"], "data": result["data"],
            "instrument": result["instrument"], "windows": result["windows"]},
        "series": _series(row["series"]),
    }
