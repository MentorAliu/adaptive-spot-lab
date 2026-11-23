"""The spot feed's writes, as the market worker identity (ExecPlan 0060 section 4.5; ``app.perp.store`` until then).

Each write is idempotent: a book is keyed by its second of receipt, a 1-minute candle by its open time and a day by
its open time, so a retried call or a second process writes nothing twice. A final candle and a stored day are never
replaced (migration 0041's guards), so an ``ON CONFLICT`` update names only open candles.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.spot_market import market

# Books are kept two days and 1-minute candles 30 days (migration 0041's guards refuse younger deletes); a margin
# keeps a delete clear of the guard's own clock.
QUOTE_RETENTION = "2 days 1 minute"
BAR_RETENTION_MS = 30 * market.DAY_MS + market.MINUTE_MS
RETENTION_BATCH = 5000
STATE_FIELDS = ("status", "reason", "stream_connected", "last_quote_at", "last_bar_at", "clock_verified",
                "clock_offset_ms", "clock_uncertainty_ms", "clock_checked_at", "history_checked_at",
                "daily_checked_at", "heartbeat_at")


def decimal_text(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def levels_json(levels: tuple[market.Level, ...]) -> str:
    return json.dumps([[decimal_text(price), decimal_text(quantity)] for price, quantity in levels])


def schema_ready(engine: Engine) -> bool:
    """Whether migration 0041 is applied: the feed waits for it."""
    with engine.connect() as connection:
        return connection.execute(text("SELECT to_regclass('spot_feed_state') IS NOT NULL")).scalar_one()


def record_instrument(engine: Engine, instrument: market.Instrument, checked_at: datetime) -> int:
    """Store the entry when it differs from the newest one; point the feed at it either way."""
    with engine.begin() as connection:
        newest = connection.execute(text(
            "SELECT id, sha256 FROM spot_instruments ORDER BY id DESC LIMIT 1")).mappings().first()
        if newest is not None and newest["sha256"] == instrument.sha256:
            identity = newest["id"]
        else:
            identity = connection.execute(text("""
                INSERT INTO spot_instruments (symbol, sha256, status, usable, tick_size, step_size, min_qty, max_qty,
                    min_notional, max_notional, document, checked_at)
                VALUES (:symbol, :sha256, :status, :usable, :tick_size, :step_size, :min_qty, :max_qty,
                    :min_notional, :max_notional, CAST(:document AS jsonb), :checked_at)
                RETURNING id"""), {
                "symbol": instrument.symbol, "sha256": instrument.sha256, "status": instrument.status,
                "usable": instrument.usable, "tick_size": instrument.tick_size, "step_size": instrument.step_size,
                "min_qty": instrument.min_qty, "max_qty": instrument.max_qty,
                "min_notional": instrument.min_notional, "max_notional": instrument.max_notional,
                "document": json.dumps(instrument.document, sort_keys=True), "checked_at": checked_at,
            }).scalar_one()
        connection.execute(text(
            "UPDATE spot_feed_state SET instrument_id = :id, instrument_checked_at = :at, "
            "updated_at = clock_timestamp() WHERE id = 1"), {"id": identity, "at": checked_at})
    return identity


def upsert_bar(connection, bar: market.Bar, source: str, received: datetime) -> None:
    connection.execute(text("""
        INSERT INTO spot_bars (open_ms, open, high, low, close, volume, quote_volume, trades, final, source, event_at,
            received_at)
        VALUES (:open_ms, :open, :high, :low, :close, :volume, :quote_volume, :trades, :final, :source, :event_at,
            :received)
        ON CONFLICT (open_ms) DO UPDATE SET open = EXCLUDED.open, high = EXCLUDED.high, low = EXCLUDED.low,
            close = EXCLUDED.close, volume = EXCLUDED.volume, quote_volume = EXCLUDED.quote_volume,
            trades = EXCLUDED.trades, final = EXCLUDED.final, source = EXCLUDED.source, event_at = EXCLUDED.event_at,
            received_at = EXCLUDED.received_at
        WHERE NOT spot_bars.final"""), {
        "open_ms": bar.open_ms, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
        "volume": bar.volume, "quote_volume": bar.quote_volume, "trades": bar.trades, "final": bar.final,
        "source": source, "event_at": market.at(bar.event_ms) if bar.event_ms is not None else None,
        "received": received})


def set_state(connection, fields: dict[str, Any]) -> None:
    if not fields:
        return
    unknown = set(fields) - set(STATE_FIELDS)
    if unknown:
        raise ValueError(f"unknown feed state field {sorted(unknown)[0]}")
    assignments = ", ".join(f"{name} = :{name}" for name in fields)
    connection.execute(text(f"UPDATE spot_feed_state SET {assignments}, updated_at = clock_timestamp() WHERE id = 1"),
                       fields)


def update_state(engine: Engine, fields: dict[str, Any]) -> None:
    with engine.begin() as connection:
        set_state(connection, fields)


def write_second(engine: Engine, *, quotes: list[tuple[market.Quote, datetime]],
                 bars: list[tuple[market.Bar, datetime]], connection_id: UUID, state: dict[str, Any]) -> None:
    """The newest book of each finished second, the candles that changed, and the feed's state, in one transaction."""
    with engine.begin() as connection:
        for item, received in quotes:
            connection.execute(text("""
                INSERT INTO spot_quotes (second_at, update_id, bid, bid_qty, ask, ask_qty, bids, asks, received_at,
                    connection_id)
                VALUES (date_trunc('second', CAST(:received AS timestamptz)), :update_id, :bid, :bid_qty, :ask,
                    :ask_qty, CAST(:bids AS jsonb), CAST(:asks AS jsonb), :received, :connection)
                ON CONFLICT (second_at) DO NOTHING"""), {
                "received": received, "update_id": item.update_id, "bid": item.bid, "bid_qty": item.bid_qty,
                "ask": item.ask, "ask_qty": item.ask_qty, "bids": levels_json(item.bids),
                "asks": levels_json(item.asks), "connection": connection_id})
        for bar, received in bars:
            upsert_bar(connection, bar, "STREAM", received)
        set_state(connection, state)


def write_history(engine: Engine, bars: list[market.Bar], received: datetime, checked_at: datetime) -> None:
    with engine.begin() as connection:
        for bar in bars:
            upsert_bar(connection, bar, "REST", received)
        set_state(connection, {"history_checked_at": checked_at})


def record_event(engine: Engine, code: str, at: datetime, detail: dict[str, Any] | None = None) -> None:
    with engine.begin() as connection:
        connection.execute(text(
            "INSERT INTO spot_feed_events (code, at, detail) VALUES (:code, :at, CAST(:detail AS jsonb))"),
            {"code": code[:48], "at": at, "detail": json.dumps(detail or {}, sort_keys=True, default=str)})


def missing_minutes(engine: Engine, start_ms: int, end_ms: int) -> list[int]:
    """The open times in ``[start_ms, end_ms)`` without a final candle, ascending."""
    with engine.connect() as connection:
        have = set(connection.execute(text(
            "SELECT open_ms FROM spot_bars WHERE final AND open_ms >= :start AND open_ms < :end"),
            {"start": start_ms, "end": end_ms}).scalars())
    return [minute for minute in range(start_ms, end_ms, market.MINUTE_MS) if minute not in have]


def stored_days(engine: Engine, start_ms: int, end_ms: int) -> set[int]:
    """The day opens in ``[start_ms, end_ms)`` with a stored daily candle."""
    with engine.connect() as connection:
        return set(connection.execute(text(
            "SELECT open_ms FROM spot_daily_bars WHERE open_ms >= :start AND open_ms < :end"),
            {"start": start_ms, "end": end_ms}).scalars())


def write_daily(engine: Engine, bars: list[market.DailyBar], received: datetime) -> int:
    """Store the final days not stored yet; a stored day is never changed (the table's guard). Returns the number
    stored."""
    stored = 0
    with engine.begin() as connection:
        for bar in bars:
            if not bar.final:
                continue
            stored += connection.execute(text("""
                INSERT INTO spot_daily_bars (open_ms, open, high, low, close, volume, quote_volume, trades,
                    received_at)
                VALUES (:open_ms, :open, :high, :low, :close, :volume, :quote_volume, :trades, :received)
                ON CONFLICT (open_ms) DO NOTHING"""), {
                "open_ms": bar.open_ms, "open": bar.open, "high": bar.high, "low": bar.low, "close": bar.close,
                "volume": bar.volume, "quote_volume": bar.quote_volume, "trades": bar.trades,
                "received": received}).rowcount
    return stored


def prune(engine: Engine) -> int:
    """Delete one batch of books older than two days and of 1-minute candles older than 30 days; returns the rows
    deleted."""
    with engine.begin() as connection:
        removed = connection.execute(text(f"""
            DELETE FROM spot_quotes WHERE second_at IN (
                SELECT second_at FROM spot_quotes WHERE second_at < clock_timestamp() - interval '{QUOTE_RETENTION}'
                ORDER BY second_at LIMIT {RETENTION_BATCH})""")).rowcount
        removed += connection.execute(text(f"""
            DELETE FROM spot_bars WHERE open_ms IN (
                SELECT open_ms FROM spot_bars
                WHERE open_ms < (extract(epoch FROM clock_timestamp()) * 1000)::bigint - {BAR_RETENTION_MS}
                ORDER BY open_ms LIMIT {RETENTION_BATCH})""")).rowcount
    return removed
