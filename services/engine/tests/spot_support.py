"""The spot account's database harness (ExecPlan 0060 section 6): an isolated ``asl_m1_`` database at migration 0041,
the real roles, and SYNTHETIC market rows. Every price, quantity, filter and close here is made up for the tests; none
is a recorded market value.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest
from psycopg import sql
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

from app import accounting
from app.db import connection_options, database_url
from app.execution import store as xstore
from app.spot.definitions import DAY_MS
from app.spot.engine import SpotEngine

PRESERVED = frozenset({"alembic_version", "system_metadata", "execution_definitions"})
# Ten minutes after a UTC midnight, before these tests were written: the rule reads at the first step from 00:05, and a
# book the tests store at the database's clock (a top-up's valuation) is newer than every book stored for a step.
T0 = datetime(2026, 11, 2, 0, 10, tzinfo=UTC)
CODE = "c" * 64
STEP, MIN_QTY, MIN_NOTIONAL = "0.00001", "0.00001", "5"
COINS = ("BTC", "SOL", "ZEC", "NEAR", "XRP")


def ms(at: datetime) -> int:
    return int(at.timestamp() * 1000)


def day_open(at: datetime) -> int:
    value = ms(at)
    return value - value % DAY_MS


def role_engine(monkeypatch, role: str) -> Engine:
    monkeypatch.setenv("ASL_DB_ROLE", role)
    engine = create_engine(database_url(), pool_pre_ping=True, connect_args=connection_options(role))
    monkeypatch.setenv("ASL_DB_ROLE", "api")
    return engine


def require_disposable(connection: Connection) -> str:
    name = connection.execute(text("SELECT current_database()")).scalar_one()
    if os.environ.get("ASL_TEST_ISOLATED") != "1" or not name.startswith("asl_m1_") \
            or os.environ.get("ASL_DB_NAME") != name:
        raise PermissionError("spot_tests_require_a_disposable_asl_m1_database")
    return name


def enable_execution_login(admin: Engine) -> None:
    """The execution identity is created NOLOGIN; a disposable test database's cluster lets it log in (the owner's
    cluster gave it its login at M4's activation)."""
    password = Path(os.environ.get("ASL_EXECUTION_PASSWORD_FILE", "/run/secrets/execution_db_password")).read_text(
        encoding="utf-8").strip()
    with admin.begin() as connection:
        require_disposable(connection)
        with connection.connection.driver_connection.cursor() as cursor:
            cursor.execute(sql.SQL("ALTER ROLE asl_execution LOGIN PASSWORD {}").format(sql.Literal(password)))


def reset(connection: Connection) -> None:
    """Empty every table of the public schema but the migration's and the definitions, and seed the singletons."""
    require_disposable(connection)
    tables = [row[0] for row in connection.execute(text(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")).all()
        if row[0] not in PRESERVED]
    connection.execute(text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE"))
    connection.execute(text("INSERT INTO account_state (id) VALUES (1)"))
    # BTC, and the four coins M10 traded (their rows stay; migration 0041 changes none).
    connection.execute(text("INSERT INTO account_holdings (asset) VALUES " + ", ".join(f"('{asset}')" for asset in COINS)))
    connection.execute(text("INSERT INTO execution_lease (id) VALUES (1)"))
    connection.execute(text("INSERT INTO spot_feed_state (id) VALUES (1)"))


def trend(last_day_ms: int, *, days: int = 400, base: str = "40000", step: str = "50",
          wiggle: str = "400") -> dict[int, Decimal]:
    """SYNTHETIC daily closes ending on ``last_day_ms``: a straight line of ``step`` a day from ``base`` with an
    alternating ``wiggle`` (a volatility of about 30% a year at these numbers). A positive step reads LONG (each
    anchor's sign +1), a negative one CASH."""
    first = last_day_ms - (days - 1) * DAY_MS
    closes = {}
    for n in range(days):
        sign = 1 if n % 2 else -1
        closes[first + n * DAY_MS] = Decimal(base) + Decimal(step) * n + Decimal(wiggle) * sign
    return closes


@dataclass
class Spot:
    admin: Engine
    execution: Engine
    api: Engine
    market: Engine
    engine: SpotEngine | None = None
    owner: UUID | None = None

    # ---- reads ---------------------------------------------------------------------------------------------------

    def rows(self, sql: str, **params) -> list[dict[str, Any]]:
        with self.admin.connect() as connection:
            return [dict(row) for row in connection.execute(text(sql), params).mappings()]

    def scalar(self, sql: str, **params):
        with self.admin.connect() as connection:
            return connection.execute(text(sql), params).scalar_one()

    def account(self) -> dict[str, Any]:
        return self.rows("SELECT * FROM account_state WHERE id = 1")[0]

    def btc(self) -> Decimal:
        return self.scalar("SELECT quantity FROM account_holdings WHERE asset = 'BTC'")

    def run(self) -> dict[str, Any] | None:
        rows = self.rows("SELECT * FROM spot_runs ORDER BY seq DESC LIMIT 1")
        return rows[0] if rows else None

    def fills(self) -> list[dict[str, Any]]:
        return self.rows("SELECT * FROM spot_fills ORDER BY seq")

    def readings(self) -> list[dict[str, Any]]:
        return self.rows("SELECT * FROM spot_rule_readings ORDER BY seq")

    def events(self) -> list[str]:
        return [row["kind"] for row in self.rows("SELECT kind FROM spot_run_events ORDER BY id")]

    # ---- the engine ----------------------------------------------------------------------------------------------

    def start(self) -> SpotEngine:
        self.owner = uuid4()
        epoch = xstore.acquire_lease(self.owner, self.execution)
        assert epoch is not None, "execution lease unavailable"
        self.engine = SpotEngine(self.execution, self.owner, epoch, identity=CODE)
        self.engine.start()
        return self.engine

    def restart(self) -> SpotEngine:
        """A new worker after the old one's lease lapsed: a higher epoch, an engine without memory."""
        self.raw("UPDATE execution_lease SET expires_at = clock_timestamp() - interval '1 second' WHERE id = 1")
        return self.start()

    def renew(self) -> None:
        assert xstore.renew_lease(self.owner, self.engine.epoch, self.execution)

    def step(self, at: datetime) -> list[dict[str, Any]]:
        self.renew()
        return self.engine.step(at)

    def reconcile(self, at: datetime) -> dict[str, Any]:
        self.renew()
        return self.engine.reconcile(at)

    # ---- the account ---------------------------------------------------------------------------------------------

    def fund(self) -> dict[str, Any]:
        """The app's own initial contribution, as the API posts it at its start (10,000 virtual USDT)."""
        return accounting.fund_by_itself()

    def top_up(self, amount: str) -> dict[str, Any]:
        """The owner's top-up, drafted and confirmed as the API does."""
        draft = accounting.draft("TOPUP", amount)
        return accounting.confirm("TOPUP", amount, draft["version"], draft["draft_hash"], f"top-up-{uuid4().hex}",
                                  "test")

    def request(self, kind: str, run: UUID | None | str = "current") -> UUID:
        """The owner's request as the API writes it (the API identity)."""
        identity = uuid4()
        run_id = (self.run() or {}).get("id") if run == "current" else run
        with self.api.begin() as connection:
            connection.execute(text(
                "INSERT INTO spot_owner_requests (id, kind, run_id, idempotency_key, request_hash) "
                "VALUES (:id, :kind, :run, :key, :hash)"),
                {"id": identity, "kind": kind, "run": None if kind == "START" else run_id,
                 "key": f"test-{identity}", "hash": hashlib.sha256(str(identity).encode()).hexdigest()})
        return identity

    # ---- SYNTHETIC market rows, as the market worker writes them ---------------------------------------------------

    def instrument(self, at: datetime = T0, *, usable: bool = True, step: str = STEP, min_qty: str = MIN_QTY,
                   min_notional: str = MIN_NOTIONAL, clock_verified: bool = True) -> int:
        with self.market.begin() as connection:
            identity = connection.execute(text(
                "INSERT INTO spot_instruments (symbol, sha256, status, usable, tick_size, step_size, min_qty, max_qty, "
                "min_notional, max_notional, document, checked_at) VALUES ('BTCUSDT', :sha, :status, :usable, 0.01, "
                ":step, :min_qty, 9000, :min_notional, 9000000, '{}', :at) RETURNING id"),
                {"sha": hashlib.sha256(f"{at}{usable}{step}{min_qty}{min_notional}".encode()).hexdigest(),
                 "status": "TRADING" if usable else "BREAK", "usable": usable, "step": Decimal(step),
                 "min_qty": Decimal(min_qty), "min_notional": Decimal(min_notional), "at": at}).scalar_one()
            connection.execute(text(
                "UPDATE spot_feed_state SET instrument_id = :id, instrument_checked_at = :at, status = 'CONNECTED', "
                "clock_verified = :clock, clock_checked_at = :at, heartbeat_at = :at WHERE id = 1"),
                {"id": identity, "at": at, "clock": clock_verified})
        return identity

    def clock(self, verified: bool) -> None:
        with self.market.begin() as connection:
            connection.execute(text("UPDATE spot_feed_state SET clock_verified = :verified WHERE id = 1"),
                               {"verified": verified})

    def book(self, at: datetime, bid: str = "60000.00", ask: str = "60000.01", quantity: str = "2",
             levels: int = 10) -> None:
        """One second's book, received at ``at``: ``levels`` a side, 0.01 apart, ``quantity`` BTC each."""
        bids = [[format(Decimal(bid) - Decimal("0.01") * n, "f"), quantity] for n in range(levels)]
        asks = [[format(Decimal(ask) + Decimal("0.01") * n, "f"), quantity] for n in range(levels)]
        with self.market.begin() as connection:
            connection.execute(text(
                "INSERT INTO spot_quotes (second_at, update_id, bid, bid_qty, ask, ask_qty, bids, asks, received_at, "
                "connection_id) VALUES (date_trunc('second', CAST(:at AS timestamptz)), 1, :bid, :qty, :ask, :qty, "
                "CAST(:bids AS jsonb), CAST(:asks AS jsonb), :at, :connection)"),
                {"at": at, "bid": Decimal(bid), "ask": Decimal(ask), "qty": Decimal(quantity),
                 "bids": json.dumps(bids), "asks": json.dumps(asks), "connection": uuid4()})

    def daily(self, closes: dict[int, Decimal], received: datetime = T0) -> None:
        """Final daily candles with these closes (open, high and low around them)."""
        with self.market.begin() as connection:
            for open_ms, close in sorted(closes.items()):
                connection.execute(text(
                    "INSERT INTO spot_daily_bars (open_ms, open, high, low, close, volume, quote_volume, trades, "
                    "received_at) VALUES (:open_ms, :close, :high, :low, :close, 1, :close, 1, :at)"),
                    {"open_ms": open_ms, "close": close, "high": close + 100, "low": close - 100, "at": received})

    def raw(self, sql: str, **params) -> None:
        with self.admin.begin() as connection:
            connection.execute(text(sql), params)

    def ready(self, at: datetime = T0, closes: dict[int, Decimal] | None = None) -> dict[int, Decimal]:
        """A funded account, a usable instrument, a verified clock, the closes up to the day before ``at``'s day
        (rising unless given) and a fresh book: what the first reading needs."""
        self.fund()
        self.instrument(at)
        closes = closes if closes is not None else trend(day_open(at) - DAY_MS)
        self.daily(closes)
        self.book(at - timedelta(milliseconds=500))
        return closes


@pytest.fixture
def spot(monkeypatch):
    if os.environ.get("ASL_TEST_ISOLATED") != "1" or not os.environ.get("ASL_DB_NAME", "").startswith("asl_m1_"):
        pytest.skip("Spot integration requires an isolated asl_m1_ disposable database")
    admin = role_engine(monkeypatch, "migration")
    with admin.begin() as connection:
        reset(connection)
    enable_execution_login(admin)
    harness = Spot(admin, role_engine(monkeypatch, "execution"), role_engine(monkeypatch, "api"),
                   role_engine(monkeypatch, "market_worker"))
    try:
        yield harness
    finally:
        for engine in (harness.execution, harness.api, harness.market):
            engine.dispose()
        with admin.begin() as connection:
            reset(connection)
        admin.dispose()


__all__ = ["CODE", "DAY_MS", "T0", "Spot", "day_open", "ms", "reset", "spot", "timedelta", "trend"]
