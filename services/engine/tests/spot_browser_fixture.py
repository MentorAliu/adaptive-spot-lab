"""The browser suites' database (ExecPlan 0060 section 10): a funded spot account whose run #1 bought and was stopped
and sold, and whose run #2 bought; the daily history and the last 30 days of minutes; the backtest; and a SYNTHETIC
stand-in for Binance's public spot API that the real feed (``app.spot_market.feed``) reads while the suites run.

Every price, candle, book and filter here is made up: a deterministic walk (``log_close``), the same in every run, that
rises from August 2025 to mid-2027, so the rule holds some Bitcoin on any day of the suites' months. Nothing is a market
value, a fill of a real market or a result.

    python -m tests.spot_browser_fixture seed   # once, on a fresh asl_m1_*_browser database at head: prints a summary
    python -m tests.spot_browser_fixture feed   # the real feed on the stand-in, until SIGTERM

``seed`` writes what the feed would (the days to yesterday, the minutes, the instrument, the clock, a fresh book) and
runs the real engine, the real funding and the owner's real requests at the database's clock, as the API and the
worker would: the app funds the account, run #1 starts by itself and today's reading buys; the owner's Stop sells it
all; the owner's Start opens run #2, whose reading buys. Nothing is dated in the past. Then the backtest is worked out
as the worker does. While the suites run, ``feed`` keeps the book and the minutes fresh, and the execution worker
(``python -m app.execution.worker``) and the API run as on the PC.
"""

import argparse
import asyncio
import hashlib
import json
import math
import os
import signal
import sys
import time
from datetime import UTC, datetime
from decimal import ROUND_DOWN, Decimal
from pathlib import Path
from typing import Any
from uuid import uuid4

from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app import accounting, code_identity
from app.db import connection_options, database_url
from app.execution import store as xstore
from app.spot import backtest
from app.spot import requests as owner_requests
from app.spot.engine import SpotEngine
from app.spot_market import market
from app.spot_market import store as mstore
from app.spot_market.feed import SpotFeed
from tests.spot_market_support import FakeSocket, exchange_info, instrument_doc

DAY, MINUTE = market.DAY_MS, market.MINUTE_MS
CENT = Decimal("0.01")
# The slow cycle's low, in days since 2017-08-17 (August 2025): the walk rises from there for about two years.
TROUGH = 2938
HISTORY_DAYS = 30
BOOK_LEVELS = 10


# ---- the SYNTHETIC walk -------------------------------------------------------------------------------------------

def unit(seed: str) -> float:
    """A deterministic number in [-1, 1) from ``seed``: the walk's noise."""
    return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8], "big") / 2 ** 63 - 1.0


def index(open_ms: int) -> int:
    return (open_ms - market.FIRST_DAY_MS) // DAY


def log_close(day: int) -> float:
    """A day's made-up close in logs (``day`` in days since 2017-08-17): a drift, a slow cycle, a 97-day swing and
    noise of about 1.6% a day."""
    return (math.log(4000) + 2.7 * day / 3400 - 0.45 * math.cos(2 * math.pi * (day - TROUGH) / 1450)
            + 0.08 * math.sin(2 * math.pi * day / 97) + 0.02 * unit(f"day:{day}"))


def cents(value: float) -> Decimal:
    return Decimal(repr(round(math.exp(value), 2))).quantize(CENT)


def close_of(open_ms: int) -> Decimal:
    return cents(log_close(index(open_ms)))


def minute_log(open_ms: int, done: float = 1.0) -> float:
    """The made-up price, in logs, of the minute opening at ``open_ms`` once ``done`` of it has passed: from the day
    before's close to the day's close, with a four-hour swing and noise, ending on the day's close."""
    day = open_ms - open_ms % DAY
    minutes = (open_ms - day) // MINUTE + done  # minutes of the day passed, up to 1440
    start, end = log_close(index(day) - 1), log_close(index(day))
    swing = 0.004 * math.sin(2 * math.pi * minutes / 240)
    noise = 0.0006 * unit(f"minute:{open_ms}") * min(1.0, done) if minutes < 1440 else 0.0
    return start + (end - start) * minutes / 1440 + swing + noise


def candle(open_ms: int, done: float = 1.0) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """A minute's open, high, low and close; ``done`` below 1 is the running minute's share passed."""
    opened = cents(minute_log(open_ms - MINUTE))
    closed = cents(minute_log(open_ms, done))
    high = (max(opened, closed) * Decimal("1.0003")).quantize(CENT)
    low = (min(opened, closed) * Decimal("0.9997")).quantize(CENT)
    return opened, high, low, closed


def volume(seed: str, base: float, spread: float) -> Decimal:
    return Decimal(repr(round(base + spread * unit(seed), 8))).quantize(Decimal("0.00000001"))


def daily_row(open_ms: int) -> list:
    """A day as ``GET /api/v3/klines`` answers it at ``1d``: twelve fields."""
    opened, closed = close_of(open_ms - DAY), close_of(open_ms)
    n = index(open_ms)
    high = (max(opened, closed) * Decimal(repr(1.006 + 0.004 * abs(unit(f"high:{n}"))))).quantize(CENT)
    low = (min(opened, closed) * Decimal(repr(0.994 - 0.004 * abs(unit(f"low:{n}"))))).quantize(CENT)
    traded = volume(f"volume:{n}", 20000, 8000)
    quote = (traded * closed).quantize(Decimal("0.00000001"))
    return [open_ms, str(opened), str(high), str(low), str(closed), str(traded), open_ms + DAY - 1, str(quote),
            900000, str((traded / 2).quantize(Decimal("0.00000001"))),
            str((quote / 2).quantize(Decimal("0.00000001"))), "0"]


def minute_row(open_ms: int, now_ms: int) -> list:
    """A minute as ``GET /api/v3/klines`` answers it at ``1m``; the running one as far as it has run."""
    opened, high, low, closed = candle(open_ms, min(1.0, (now_ms - open_ms) / MINUTE))
    traded = volume(f"minute-volume:{open_ms}", 14, 9)
    quote = (traded * closed).quantize(Decimal("0.00000001"))
    return [open_ms, str(opened), str(high), str(low), str(closed), str(traded), open_ms + MINUTE - 1, str(quote),
            600, str((traded / 2).quantize(Decimal("0.00000001"))),
            str((quote / 2).quantize(Decimal("0.00000001"))), "0"]


def book_levels(now_ms: int, update_id: int) -> tuple[list[list[str]], list[list[str]]]:
    """Ten made-up levels a side around the walk's price at ``now_ms``, a cent apart."""
    minute = now_ms - now_ms % MINUTE
    mid = Decimal(repr(math.exp(minute_log(minute, (now_ms - minute) / MINUTE))))
    bid = (mid - Decimal("0.005")).quantize(CENT, rounding=ROUND_DOWN)
    bids = [[str(bid - CENT * n), str(volume(f"bid:{update_id}:{n}", 0.85, 0.65))] for n in range(BOOK_LEVELS)]
    asks = [[str(bid + CENT * (n + 1)), str(volume(f"ask:{update_id}:{n}", 0.85, 0.65))]
            for n in range(BOOK_LEVELS)]
    return bids, asks


def depth_frame(now_ms: int, update_id: int) -> bytes:
    bids, asks = book_levels(now_ms, update_id)
    return json.dumps({"stream": market.BOOK_STREAM,
                       "data": {"lastUpdateId": update_id, "bids": bids, "asks": asks}}).encode()


def kline_frame(open_ms: int, event_ms: int, final: bool) -> bytes:
    row = minute_row(open_ms, open_ms + MINUTE if final else event_ms)
    k = {"t": open_ms, "T": open_ms + MINUTE - 1, "s": market.SYMBOL, "i": "1m", "f": 1, "L": 600,
         "o": row[1], "c": row[4], "h": row[2], "l": row[3], "v": row[5], "n": row[8], "x": final, "q": row[7],
         "V": row[9], "Q": row[10], "B": "0"}
    return json.dumps({"stream": market.KLINE_STREAM,
                       "data": {"e": "kline", "E": event_ms, "s": market.SYMBOL, "k": k}}).encode()


def now_ms() -> int:
    return int(time.time() * 1000)


class SyntheticBinance:
    """Stands in for ``app.spot_market.provider.PublicBinance``: its methods, the walk's answers, no network."""

    def __init__(self) -> None:
        self.update_id = 1_000_000
        self.bound = None

    def bind(self, *, stop, report) -> None:
        self.bound = (stop, report)

    async def close(self) -> None:
        return None

    async def best_clock(self, samples: int = 3) -> tuple[int, float, float]:
        return now_ms(), 0.0, 5.0

    async def instrument(self) -> bytes:
        return exchange_info(instrument_doc())

    async def klines(self, interval: str, start_ms: int, end_ms: int, limit: int) -> bytes:
        now = now_ms()
        step = DAY if interval == "1d" else MINUTE
        rows, at = [], start_ms
        while at <= end_ms and at <= now and len(rows) < limit:
            rows.append(daily_row(at) if interval == "1d" else minute_row(at, now))
            at += step
        return json.dumps(rows).encode()

    async def connect_stream(self) -> FakeSocket:
        """A book every 250 ms, the running minute's candle every second, and each minute's final candle once it
        closed, as the combined stream sends them."""
        pending: list[bytes] = []
        sent: dict[str, Any] = {"minute": None, "tick": 0}

        async def frames() -> bytes:
            if pending:
                return pending.pop(0)
            await asyncio.sleep(0.25)
            now = now_ms()
            minute = now - now % MINUTE
            if sent["minute"] is not None and minute > sent["minute"]:
                pending.append(kline_frame(sent["minute"], now, final=True))
            sent["minute"] = minute
            sent["tick"] += 1
            if sent["tick"] % 4 == 0:
                pending.append(kline_frame(minute, now, final=False))
            self.update_id += 1
            pending.append(depth_frame(now, self.update_id))
            return pending.pop(0)

        return FakeSocket(frames)


# ---- the database -------------------------------------------------------------------------------------------------

def guard() -> str:
    name = os.environ.get("ASL_DB_NAME", "")
    if os.environ.get("ASL_TEST_ISOLATED") != "1" or not name.startswith("asl_m1_") or not name.endswith("_browser"):
        raise SystemExit("spot_browser_fixture needs ASL_TEST_ISOLATED=1 and an asl_m1_*_browser database")
    return name


def role(name: str) -> Engine:
    """An engine of one of the app's identities, as its process would open it."""
    kept = os.environ.get("ASL_DB_ROLE")
    os.environ["ASL_DB_ROLE"] = name
    try:
        return create_engine(database_url(), pool_pre_ping=True, connect_args=connection_options(name))
    finally:
        if kept is None:
            os.environ.pop("ASL_DB_ROLE", None)
        else:
            os.environ["ASL_DB_ROLE"] = kept


def enable_execution_login(admin: Engine) -> None:
    """The execution identity is created NOLOGIN; a disposable database's cluster lets it log in (the owner's cluster
    gave it its login at M4's activation), as ``tests/spot_support.py`` does."""
    password = Path(os.environ.get("ASL_EXECUTION_PASSWORD_FILE", "/run/secrets/execution_db_password")).read_text(
        encoding="utf-8").strip()
    with admin.begin() as connection:
        with connection.connection.driver_connection.cursor() as cursor:
            cursor.execute(sql.SQL("ALTER ROLE asl_execution LOGIN PASSWORD {}").format(sql.Literal(password)))


def write_days(db: Engine, first: int, last: int, received: datetime) -> int:
    """The final days from ``first`` to ``last`` (opens, inclusive), as the feed stores them."""
    rows = []
    for open_ms in range(first, last + 1, DAY):
        row = daily_row(open_ms)
        rows.append({"open_ms": open_ms, "open": Decimal(row[1]), "high": Decimal(row[2]), "low": Decimal(row[3]),
                     "close": Decimal(row[4]), "volume": Decimal(row[5]), "quote_volume": Decimal(row[7]),
                     "trades": row[8], "received": received})
    with db.begin() as connection:
        connection.execute(text(
            "INSERT INTO spot_daily_bars (open_ms, open, high, low, close, volume, quote_volume, trades, received_at) "
            "VALUES (:open_ms, :open, :high, :low, :close, :volume, :quote_volume, :trades, :received) "
            "ON CONFLICT (open_ms) DO NOTHING"), rows)
        mstore.set_state(connection, {"daily_checked_at": received})
    return len(rows)


def write_minutes(db: Engine, first: int, last: int, received: datetime) -> int:
    """The final minutes from ``first`` to ``last`` (opens, inclusive), as the feed's REST history stores them."""
    now = now_ms()
    bars = []
    for open_ms in range(first, last + 1, MINUTE):
        row = minute_row(open_ms, now)
        bars.append({"open_ms": open_ms, "open": Decimal(row[1]), "high": Decimal(row[2]), "low": Decimal(row[3]),
                     "close": Decimal(row[4]), "volume": Decimal(row[5]), "quote_volume": Decimal(row[7]),
                     "trades": row[8], "received": received})
    with db.begin() as connection:
        connection.execute(text(
            "INSERT INTO spot_bars (open_ms, open, high, low, close, volume, quote_volume, trades, final, source, "
            "event_at, received_at) VALUES (:open_ms, :open, :high, :low, :close, :volume, :quote_volume, :trades, "
            "true, 'REST', NULL, :received) ON CONFLICT (open_ms) DO NOTHING"), bars)
        mstore.set_state(connection, {"history_checked_at": received})
    return len(bars)


def write_book(db: Engine, update_id: int) -> datetime:
    """One second's book at the database's clock, with the feed's state, as the feed's writer stores them."""
    with db.begin() as connection:
        at = connection.execute(text("SELECT clock_timestamp()")).scalar_one()
        bids, asks = book_levels(int(at.timestamp() * 1000), update_id)
        connection.execute(text(
            "INSERT INTO spot_quotes (second_at, update_id, bid, bid_qty, ask, ask_qty, bids, asks, received_at, "
            "connection_id) VALUES (date_trunc('second', CAST(:at AS timestamptz)), :id, :bid, :bid_qty, :ask, "
            ":ask_qty, CAST(:bids AS jsonb), CAST(:asks AS jsonb), :at, :connection) "
            "ON CONFLICT (second_at) DO NOTHING"),
            {"at": at, "id": update_id, "bid": Decimal(bids[0][0]), "bid_qty": Decimal(bids[0][1]),
             "ask": Decimal(asks[0][0]), "ask_qty": Decimal(asks[0][1]), "bids": json.dumps(bids),
             "asks": json.dumps(asks), "connection": uuid4()})
        mstore.set_state(connection, {"status": "CONNECTED", "reason": None, "stream_connected": True,
                                      "last_quote_at": at, "clock_verified": True, "clock_offset_ms": 0,
                                      "clock_uncertainty_ms": 5, "clock_checked_at": at, "heartbeat_at": at})
    return at


class Seeder:
    def __init__(self) -> None:
        self.market = role("market_worker")
        self.execution = role("execution")
        self.admin = role("migration")
        self.owner = uuid4()
        self.engine: SpotEngine | None = None
        self.update_id = 1

    def rows(self, query: str) -> list[dict[str, Any]]:
        with self.admin.connect() as connection:
            return [dict(row) for row in connection.execute(text(query)).mappings()]

    def step(self, note: str) -> list[dict[str, Any]]:
        """A fresh book, then one engine step at the database's clock, as the worker's loop does."""
        self.update_id += 1
        write_book(self.market, self.update_id)
        assert self.engine is not None
        assert xstore.renew_lease(self.owner, self.engine.epoch, self.execution), "execution lease lost"
        effects = self.engine.step(xstore.db_now(self.execution))
        print(json.dumps({"step": note, "effects": [effect["kind"] for effect in effects]}, default=str),
              file=sys.stderr)
        return effects

    def until(self, note: str, done, steps: int = 10) -> None:
        for _ in range(steps):
            self.step(note)
            if done():
                return
            time.sleep(0.3)
        raise SystemExit(f"spot_browser_fixture: {note} did not happen")

    def run(self) -> dict[str, Any]:
        return self.rows("SELECT id, seq, state FROM spot_runs ORDER BY seq DESC LIMIT 1")[0]

    def seed(self) -> dict[str, Any]:
        name = guard()
        # The API's own engine (``app.db.get_engine``) posts the funding and the owner's requests, as at the PC.
        os.environ["ASL_DB_ROLE"] = "api"
        found = self.rows("SELECT (SELECT initialized FROM account_state WHERE id = 1) AS funded, "
                          "(SELECT count(*) FROM spot_runs) AS runs, (SELECT count(*) FROM spot_daily_bars) AS days")
        if found[0]["funded"] or found[0]["runs"] or found[0]["days"]:
            raise SystemExit("spot_browser_fixture seed needs a fresh database at head")
        enable_execution_login(self.admin)
        # Today's reading is due from 00:05 UTC: just after midnight, wait for it.
        clock = xstore.db_now(self.execution)
        due = clock.replace(hour=0, minute=5, second=30, microsecond=0)
        if clock < due:
            print(json.dumps({"waiting_until": due.isoformat()}), file=sys.stderr)
            time.sleep((due - clock).total_seconds())
            clock = xstore.db_now(self.execution)
        today = int(clock.timestamp() * 1000) // DAY * DAY
        minute = int(clock.timestamp() * 1000) // MINUTE * MINUTE
        days = write_days(self.market, market.FIRST_DAY_MS, today - DAY, clock)
        minutes = write_minutes(self.market, minute - HISTORY_DAYS * DAY, minute - MINUTE, clock)
        mstore.record_instrument(self.market, market.parse_instrument(exchange_info(instrument_doc())), clock)
        funded = accounting.fund_by_itself()
        if funded["status"] != "POSTED":
            raise SystemExit(f"spot_browser_fixture: funding {funded['status']}")

        epoch = xstore.acquire_lease(self.owner, self.execution)
        if epoch is None:
            raise SystemExit("spot_browser_fixture: the execution lease is held")
        self.engine = SpotEngine(self.execution, self.owner, epoch)
        self.engine.start()
        try:
            # Run #1 starts by itself and today's reading buys.
            self.until("run 1 buys", lambda: bool(self.rows("SELECT 1 FROM spot_fills WHERE side = 'BUY'")))
            first = self.run()
            # The owner's Stop: run #1 sells everything and stops.
            owner_requests.submit(kind="STOP", run_id=first["id"], key=f"fixture-stop-{uuid4().hex[:12]}",
                                  correlation="spot-browser-fixture")
            self.until("run 1 stops", lambda: self.run()["state"] == "STOPPED")
            # The owner's Start: run #2, whose first reading buys today's target again.
            owner_requests.submit(kind="START", run_id=None, key=f"fixture-start-{uuid4().hex[:12]}",
                                  correlation="spot-browser-fixture")
            self.until("run 2 buys", lambda: len(self.rows("SELECT 1 FROM spot_fills WHERE side = 'BUY'")) == 2)
            for _ in range(3):
                self.step("settle")
            reconciled = self.engine.reconcile(xstore.db_now(self.execution))
            if reconciled["status"] != "OK":
                raise SystemExit(f"spot_browser_fixture: reconciliation {reconciled['failed_checks']}")
        finally:
            xstore.release_lease(self.owner, epoch, self.execution)

        stored = backtest.compute_and_store(self.execution, code_identity.current(),
                                            lambda: xstore.db_now(self.execution))
        fills = self.rows("SELECT side, reason, trim_scale(quantity)::text AS quantity, trim_scale(price)::text AS price "
                          "FROM spot_fills ORDER BY seq")
        readings = self.rows("SELECT result, action, outcome FROM spot_rule_readings ORDER BY seq")
        return {
            "database": name,
            "day": datetime.fromtimestamp(today / 1000, UTC).date().isoformat(),
            "days": days,
            "minutes": minutes,
            "run": self.run()["seq"],
            "fills": fills,
            "readings": readings,
            "backtest": str(stored) if stored else None,
            "btc": self.rows("SELECT trim_scale(quantity)::text AS q FROM account_holdings WHERE asset = 'BTC'")[0]["q"],
        }


def seed() -> None:
    summary = Seeder().seed()
    text_out = json.dumps(summary, indent=2, default=str)
    target = os.environ.get("ASL_SPOT_BROWSER_SUMMARY")
    if target:
        Path(target).write_text(text_out + "\n", encoding="utf-8")
    print(text_out)


def feed() -> None:
    guard()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    stop = asyncio.Event()
    for signame in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(signame, stop.set)
    try:
        loop.run_until_complete(SpotFeed(role("market_worker"), client=SyntheticBinance(), stop=stop).run())
    finally:
        loop.close()


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m tests.spot_browser_fixture")
    parser.add_argument("command", choices=("seed", "feed"))
    command = parser.parse_args().command
    seed() if command == "seed" else feed()


if __name__ == "__main__":
    main()


__all__ = ["SyntheticBinance", "candle", "close_of", "daily_row", "log_close", "minute_row"]
