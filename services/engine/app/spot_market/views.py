"""BTCUSDT's spot market for the pages (ExecPlan 0060 section 4.9; ``app.perp.views`` until then): the feed's state with
the newest book, and the chart's candles.

As the API identity, in one repeatable-read snapshot each. Until migration 0041 is applied both report the schema as
pending. Every value is the provider's, as received, or a calculation from it here (the longer candles, today's daily
candle so far, the ages); nothing here is executable or a forecast, and the book's quantities are displayed liquidity
only.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import text

from app.db import SPOT_REVISIONS, get_engine, schema_revision
from app.spot_market import market
from app.spot_market.bars import aggregate

# The feed writes its state every second; older than this the worker is taken to be down.
HEARTBEAT_SECONDS = 10
# A fill's bound on the book's age (``SPOT_COST_V1`` ``book.max_age_ms``).
BOOK_FILL_SECONDS = 2
CANDLES_MAX = 1000
# The chart's intervals: the 1-minute candles and those built from them (kept 30 days), and the final daily candles
# (kept for good) with today's so far.
INTERVALS = {**market.INTERVALS, "1d": market.DAY_MS}
LABELS = ["PROVIDER_VALUES_AS_RECEIVED", "LONGER_CANDLES_CALCULATED_FROM_1M", "DISPLAYED_LIQUIDITY_ONLY",
          "NOT_EXECUTABLE"]


def ready() -> bool:
    return schema_revision() in SPOT_REVISIONS


def iso(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat().replace("+00:00", "Z")


def plain(value: Decimal | None) -> str | None:
    """A decimal string without exponent or trailing zeros."""
    if value is None:
        return None
    digits = format(value, "f")
    return digits.rstrip("0").rstrip(".") if "." in digits else digits


def age(now: datetime, then: datetime | None) -> float | None:
    return None if then is None else round(max(0.0, (now - then).total_seconds()), 3)


def day_text(open_ms: int | None) -> str | None:
    return None if open_ms is None else market.at(open_ms).date().isoformat()


def connect(engine=None):
    return (engine or get_engine()).connect().execution_options(isolation_level="REPEATABLE READ")


def database_now(connection: Any) -> datetime:
    return connection.execute(text("SELECT clock_timestamp()")).scalar_one()


def _pending() -> dict[str, Any]:
    return {"state": "SCHEMA_PENDING", "symbol": market.SYMBOL, "evaluated_at": None, "status": "UNAVAILABLE",
            "reason": "SCHEMA_PENDING", "stream_connected": False, "heartbeat_at": None, "book": None,
            "last_candle_at": None, "clock": None, "instrument": None, "daily": None, "history_checked_at": None,
            "labels": LABELS}


def market_view(engine=None) -> dict[str, Any]:
    if not ready():
        return _pending()
    with connect(engine) as connection:
        now = database_now(connection)
        state = connection.execute(text("""
            SELECT s.*, i.status AS instrument_status, i.usable, i.tick_size, i.step_size, i.min_qty, i.max_qty,
                   i.min_notional, i.max_notional
            FROM spot_feed_state s LEFT JOIN spot_instruments i ON i.id = s.instrument_id WHERE s.id = 1""")
        ).mappings().one()
        book = connection.execute(text(
            "SELECT second_at, bid, bid_qty, ask, ask_qty, bids, asks, received_at FROM spot_quotes "
            "ORDER BY second_at DESC LIMIT 1")).mappings().first()
        daily = connection.execute(text(
            "SELECT count(*) AS days, min(open_ms) AS first, max(open_ms) AS last FROM spot_daily_bars")
        ).mappings().one()
    status, reason = state["status"], state["reason"]
    heartbeat_age = age(now, state["heartbeat_at"])
    if heartbeat_age is None or heartbeat_age > HEARTBEAT_SECONDS:
        status, reason = "UNAVAILABLE", "FEED_SILENT"
    return {
        "state": "READY", "symbol": market.SYMBOL, "evaluated_at": iso(now), "status": status, "reason": reason,
        "stream_connected": state["stream_connected"], "heartbeat_at": iso(state["heartbeat_at"]),
        "book": None if book is None else {
            "bid": plain(book["bid"]), "bid_quantity": plain(book["bid_qty"]), "ask": plain(book["ask"]),
            "ask_quantity": plain(book["ask_qty"]),
            "bids": [[plain(Decimal(p)), plain(Decimal(q))] for p, q in book["bids"]],
            "asks": [[plain(Decimal(p)), plain(Decimal(q))] for p, q in book["asks"]],
            "second_at": iso(book["second_at"]), "received_at": iso(book["received_at"]),
            "age_seconds": age(now, book["received_at"])},
        "last_candle_at": iso(state["last_bar_at"]),
        "clock": {"verified": state["clock_verified"], "offset_ms": plain(state["clock_offset_ms"]),
                  "uncertainty_ms": plain(state["clock_uncertainty_ms"]),
                  "checked_at": iso(state["clock_checked_at"])},
        "instrument": None if state["instrument_id"] is None else {
            "status": state["instrument_status"], "usable": state["usable"], "tick_size": plain(state["tick_size"]),
            "step_size": plain(state["step_size"]), "min_quantity": plain(state["min_qty"]),
            "max_quantity": plain(state["max_qty"]), "min_notional": plain(state["min_notional"]),
            "max_notional": plain(state["max_notional"]), "checked_at": iso(state["instrument_checked_at"])},
        "daily": {"days": int(daily["days"]), "first_day": day_text(daily["first"]),
                  "last_day": day_text(daily["last"]), "checked_at": iso(state["daily_checked_at"])},
        "history_checked_at": iso(state["history_checked_at"]),
        "labels": LABELS,
    }


def system_status(engine=None) -> str:
    """Settings' "Market data": ``disabled`` until the feed has ever written; ``ready`` while it is connected with a
    book fresh enough to fill from."""
    view = market_view(engine)
    if view["state"] != "READY":
        return "unavailable"
    if view["heartbeat_at"] is None:
        return "disabled"
    book = view["book"]
    if view["status"] == "CONNECTED" and book is not None and book["age_seconds"] is not None \
            and book["age_seconds"] <= BOOK_FILL_SECONDS:
        return "ready"
    return "degraded" if view["status"] in ("CONNECTED", "DEGRADED") else "unavailable"


def _candle(open_ms: int, open_: Decimal, high: Decimal, low: Decimal, close: Decimal, volume: Decimal,
            minutes: int, expected: int, complete: bool) -> dict[str, Any]:
    return {"open_ms": open_ms, "open": plain(open_), "high": plain(high), "low": plain(low), "close": plain(close),
            "volume": plain(volume), "minutes": minutes, "expected_minutes": expected, "complete": complete}


def _bars(connection: Any, start: int) -> list[market.Bar]:
    rows = connection.execute(text(
        "SELECT open_ms, open, high, low, close, volume, quote_volume, trades, final FROM spot_bars "
        "WHERE open_ms >= :start ORDER BY open_ms"), {"start": start}).mappings().all()
    return [market.Bar(row["open_ms"], row["open"], row["high"], row["low"], row["close"], row["volume"],
                       row["quote_volume"], row["trades"], row["final"], None) for row in rows]


def _daily(connection: Any, now_ms: int, limit: int) -> list[dict[str, Any]]:
    """The newest final days and, after them, today's candle so far from the stored 1-minute candles (not complete)."""
    today = now_ms - now_ms % market.DAY_MS
    rows = connection.execute(text(
        "SELECT open_ms, open, high, low, close, volume FROM spot_daily_bars WHERE open_ms < :today "
        "ORDER BY open_ms DESC LIMIT :limit"), {"today": today, "limit": limit}).mappings().all()
    candles = [_candle(row["open_ms"], row["open"], row["high"], row["low"], row["close"], row["volume"], 1440, 1440,
                       True) for row in reversed(rows)]
    minutes = _bars(connection, today)
    if minutes:
        candles.append(_candle(today, minutes[0].open, max(bar.high for bar in minutes),
                               min(bar.low for bar in minutes), minutes[-1].close,
                               sum((bar.volume for bar in minutes), Decimal(0)), len(minutes), 1440, False))
    return candles[-limit:]


def candles(interval: str, limit: int, engine=None) -> dict[str, Any]:
    """The newest ``limit`` candles of ``interval``, ascending, the newest one possibly still open."""
    if interval not in INTERVALS or not 1 <= limit <= CANDLES_MAX:
        raise ValueError("invalid_candle_request")
    if not ready():
        return {"state": "SCHEMA_PENDING", "symbol": market.SYMBOL, "interval": interval, "evaluated_at": None,
                "candles": [], "labels": LABELS}
    interval_ms = INTERVALS[interval]
    with connect(engine) as connection:
        now = database_now(connection)
        now_ms = int(now.timestamp() * 1000)
        if interval == "1d":
            built = _daily(connection, now_ms, limit)
        else:
            start = now_ms - now_ms % interval_ms - (limit - 1) * interval_ms
            built = [_candle(c.open_ms, c.open, c.high, c.low, c.close, c.volume, c.minutes, c.expected, c.complete)
                     for c in aggregate(_bars(connection, start), interval_ms)[-limit:]]
    return {"state": "READY", "symbol": market.SYMBOL, "interval": interval, "evaluated_at": iso(now),
            "candles": built, "labels": LABELS}
