"""BTCUSDT's spot feed on a scratch database (ExecPlan 0060 section 6, R6): the writes as the market worker identity,
their guards and retention, and the whole feed against a stand-in provider, through to the backtest it makes due.
Every row is SYNTHETIC (``spot_market_support``)."""

import asyncio
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from spot_market_support import DAY, MINUTE, FakeSpot, depth, exchange_info, instrument_doc, kline
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.spot import backtest
from app.spot_market import feed, market, store

D = Decimal


def bar(open_ms: int, final: bool, close: str = "60010.00") -> market.Bar:
    return market.Bar(open_ms, D("60000"), max(D("60020"), D(close)), D("59990"), D(close), D("1"), D("60000"), 3,
                      final, None)


def day_bar(open_ms: int, close: str = "60000") -> market.DailyBar:
    return market.DailyBar(open_ms, D(close), D(close) + 100, D(close) - 100, D(close), D("1"), D("60000"), 3, True,
                           open_ms + DAY - 1)


def test_the_instrument_is_stored_once_per_answer_and_the_feed_points_at_it(spot):
    now = datetime.now(UTC)
    first = store.record_instrument(spot.market, market.parse_instrument(exchange_info()), now)
    again = store.record_instrument(spot.market, market.parse_instrument(exchange_info()), now + timedelta(minutes=30))
    halted = store.record_instrument(spot.market, market.parse_instrument(exchange_info(instrument_doc(
        status="HALT"))), now + timedelta(minutes=60))
    assert first == again != halted
    rows = spot.rows("SELECT id, status, usable, step_size, min_qty, max_qty, min_notional, max_notional, "
                     "document->>'symbol' AS symbol FROM spot_instruments ORDER BY id")
    assert [(r["status"], r["usable"]) for r in rows] == [("TRADING", True), ("HALT", False)]
    assert (rows[0]["step_size"], rows[0]["min_qty"], rows[0]["max_qty"], rows[0]["min_notional"],
            rows[0]["max_notional"], rows[0]["symbol"]) == (D("0.00001"), D("0.00001"), D("80"), D("5"),
                                                            D("9000000"), "BTCUSDT")
    state = spot.rows("SELECT instrument_id, instrument_checked_at FROM spot_feed_state")[0]
    assert state["instrument_id"] == halted and state["instrument_checked_at"] == now + timedelta(minutes=60)


def test_a_second_keeps_one_book_a_candle_changes_until_final_and_the_state_is_written(spot):
    received = datetime.now(UTC).replace(microsecond=250_000)
    quote = market.parse_stream(depth(update_id=9))[1]
    later = market.parse_stream(depth(update_id=10, bid="60001.00", ask="60001.01"))[1]
    minute = int(received.timestamp() * 1000) // MINUTE * MINUTE
    state = {"status": "CONNECTED", "reason": None, "stream_connected": True, "last_quote_at": received,
             "last_bar_at": received, "clock_verified": True, "heartbeat_at": received}
    connection = uuid4()
    store.write_second(spot.market, quotes=[(quote, received)], bars=[(bar(minute, False), received)],
                       connection_id=connection, state=state)
    store.write_second(spot.market, quotes=[(later, received + timedelta(milliseconds=500))],
                       bars=[(bar(minute, True, "60015.00"), received)], connection_id=connection, state=state)
    store.write_second(spot.market, quotes=[], bars=[(bar(minute, False, "59995.00"), received)],
                       connection_id=connection, state=state)
    books = spot.rows("SELECT update_id, bid, ask, jsonb_array_length(bids) AS levels FROM spot_quotes")
    assert books == [{"update_id": 9, "bid": D("60000.00"), "ask": D("60000.01"), "levels": 10}]
    assert spot.rows("SELECT close, final, source FROM spot_bars") == [
        {"close": D("60015.00"), "final": True, "source": "STREAM"}]
    assert spot.rows("SELECT status, stream_connected, clock_verified FROM spot_feed_state") == [
        {"status": "CONNECTED", "stream_connected": True, "clock_verified": True}]
    with pytest.raises(ValueError, match="unknown feed state field"):
        store.update_state(spot.market, {"instrument_id": 1})


def test_days_and_candles_are_stored_once_and_read_back_by_what_is_missing(spot):
    first = market.FIRST_DAY_MS
    received = datetime.now(UTC)
    assert store.write_daily(spot.market, [day_bar(first), day_bar(first + DAY)], received) == 2
    assert store.write_daily(spot.market, [day_bar(first + DAY, "500"), day_bar(first + 2 * DAY)], received) == 1
    assert spot.scalar("SELECT close FROM spot_daily_bars WHERE open_ms = :day", day=first + DAY) == D("60000")
    assert store.stored_days(spot.market, first, first + 3 * DAY) == {first, first + DAY, first + 2 * DAY}
    now = int(time.time() * 1000) // MINUTE * MINUTE
    store.write_history(spot.market, [bar(now - 3 * MINUTE, True), bar(now - MINUTE, True)], received, received)
    assert store.missing_minutes(spot.market, now - 3 * MINUTE, now) == [now - 2 * MINUTE]
    assert spot.scalar("SELECT history_checked_at FROM spot_feed_state") == received


def test_the_guards_keep_days_final_candles_and_recent_books(spot):
    received = datetime.now(UTC)
    store.write_daily(spot.market, [day_bar(market.FIRST_DAY_MS)], received)
    store.write_second(spot.market, quotes=[(market.parse_stream(depth())[1], received)],
                       bars=[(bar(int(received.timestamp() * 1000) // MINUTE * MINUTE, True), received)],
                       connection_id=uuid4(), state={})
    for sql, refusal in (("UPDATE spot_daily_bars SET close = 1", "permission denied"),
                         ("DELETE FROM spot_daily_bars", "permission denied"),
                         ("DELETE FROM spot_quotes", "within retention"),
                         ("DELETE FROM spot_bars", "within retention"),
                         ("UPDATE spot_bars SET close = 1", "final spot candle is immutable"),
                         ("UPDATE spot_quotes SET bid = 1", "permission denied"),
                         ("INSERT INTO spot_fills (id) VALUES (gen_random_uuid())", "permission denied"),
                         ("UPDATE account_state SET cash = 0", "permission denied")):
        with pytest.raises(DBAPIError, match=refusal):
            with spot.market.begin() as connection:
                connection.execute(text(sql))
    for sql in ("UPDATE spot_daily_bars SET close = 1", "DELETE FROM spot_daily_bars"):
        with pytest.raises(DBAPIError, match="append-only spot record"):
            with spot.admin.begin() as connection:
                connection.execute(text(sql))


def test_retention_removes_books_older_than_two_days_and_candles_older_than_thirty(spot):
    now = datetime.now(UTC).replace(microsecond=0)
    old_quote, kept_quote = now - timedelta(days=2, minutes=2), now - timedelta(days=1, hours=23)
    for at in (old_quote, kept_quote):
        store.write_second(spot.market, quotes=[(market.parse_stream(depth())[1], at)], bars=[],
                           connection_id=uuid4(), state={})
    now_ms = int(now.timestamp() * 1000) // MINUTE * MINUTE
    old_bar, kept_bar = now_ms - 30 * DAY - 2 * MINUTE, now_ms - 29 * DAY
    store.write_history(spot.market, [bar(old_bar, True), bar(kept_bar, True)], now, now)
    assert store.prune(spot.market) == 2
    assert spot.rows("SELECT second_at FROM spot_quotes") == [{"second_at": kept_quote}]
    assert spot.rows("SELECT open_ms FROM spot_bars") == [{"open_ms": kept_bar}]
    assert store.prune(spot.market) == 0


def test_the_feed_stores_the_book_the_candles_and_every_day_and_makes_the_backtest_due(spot, monkeypatch):
    """The whole feed for a few seconds against a stand-in provider: its parts, its transactions, its state and its
    events, as the market worker identity. History is asked for one day here (30 days in the app)."""
    monkeypatch.setattr(feed, "HISTORY_DAYS", 1)
    count = 0

    async def frames():
        nonlocal count
        await asyncio.sleep(0.05)
        count += 1
        now = int(time.time() * 1000)
        if count % 10 == 0:
            return kline(now - now % MINUTE, now, False).decode()
        return depth(update_id=count)

    fake = FakeSpot(now_ms=lambda: int(time.time() * 1000), frames=frames)
    states: list[str] = []

    async def run() -> None:
        spot_feed = feed.SpotFeed(spot.market, fake)
        task = asyncio.create_task(spot_feed.run())
        began = time.monotonic()
        while time.monotonic() - began < 60:
            await asyncio.sleep(0.5)
            row = spot.rows("SELECT status, daily_checked_at IS NOT NULL AS days, history_checked_at IS NOT NULL "
                            "AS history FROM spot_feed_state")[0]
            states.append(row["status"])
            if row["status"] == "CONNECTED" and row["days"] and row["history"]:
                break
        spot_feed.stop.set()
        await asyncio.wait_for(task, 30)

    asyncio.run(run())
    assert "CONNECTED" in states and fake.closed
    # The last final day: a day is final a minute after its close.
    yesterday = (int(time.time() * 1000) - 61_000) // DAY * DAY - DAY
    days = spot.rows("SELECT count(*) AS n, min(open_ms) AS first, max(open_ms) AS last FROM spot_daily_bars")[0]
    assert (days["first"], days["last"], days["n"]) == (market.FIRST_DAY_MS, yesterday,
                                                        (yesterday - market.FIRST_DAY_MS) // DAY + 1)
    assert [call[1] for call in fake.calls if call[0] == "klines"].count("1d") == 4
    assert spot.scalar("SELECT count(*) FROM spot_bars WHERE source = 'REST' AND final") >= 1400
    assert spot.scalar("SELECT count(*) FROM spot_quotes") >= 1
    state = spot.rows("SELECT status, reason, stream_connected, clock_verified, instrument_id IS NOT NULL AS "
                      "instrument FROM spot_feed_state")[0]
    assert state == {"status": "UNAVAILABLE", "reason": "FEED_STOPPED", "stream_connected": False,
                     "clock_verified": True, "instrument": True}
    codes = {row["code"] for row in spot.rows("SELECT code FROM spot_feed_events")}
    assert {"FEED_STARTED", "STREAM_CONNECTED", "CLOCK_VERIFIED", "INSTRUMENT_CHECKED", "DAILY_STORED",
            "HISTORY_STORED"} <= codes
    with spot.api.connect() as connection:
        need = backtest.due(connection, "c" * 64)
    assert need is not None and need["last_day_ms"] == yesterday and need["filters"].step == D("0.00001")
    stored = backtest.compute_and_store(spot.execution, "c" * 64, lambda: datetime.now(UTC))
    result = spot.rows("SELECT result FROM spot_backtests WHERE id = :id", id=stored)[0]["result"]
    assert result["data"]["first_day"] == "2017-08-17" and result["data"]["missing_days"] == 0
    since = result["windows"][0]
    assert (since["key"], since["first_day"]) == ("SINCE_2019", "2019-01-01") and since["rule"]["buys"] >= 1
    assert [row["year"] for row in since["rule"]["years"]][:2] == [2019, 2020]
