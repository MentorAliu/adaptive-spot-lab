"""The spot engine's reads and writes (ExecPlan 0060 section 4.4), as the execution identity, inside its step.

Reads of the market data say how old they are by the step's database clock against the market worker's receipt time;
the engine decides what is fresh enough. Writes are plain inserts and the column updates migration 0041 grants; every
amount comes from ``app.spot.money`` and every posting from ``app.spot.ledger``.
"""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.execution.lifecycle import stable_id
from app.spot.definitions import BASE
from app.spot.money import Filters, Level

LIVE = ("RUNNING", "PAUSED", "STOPPING")


def jdump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def levels(raw: Any) -> list[Level]:
    return [(Decimal(price), Decimal(quantity)) for price, quantity in raw]


def levels_json(items: list[Level]) -> str:
    return json.dumps([[format(price, "f"), format(quantity, "f")] for price, quantity in items])


def age_ms(now: datetime, then: datetime) -> int:
    return int((now - then).total_seconds() * 1000)


# ---- the market ------------------------------------------------------------------------------------------------

def book(connection: Connection, now: datetime) -> dict[str, Any] | None:
    """The newest stored book received by ``now`` (the ten best levels of each side) and its age at ``now``: a fill
    never uses a book received after the step's time."""
    row = connection.execute(text(
        "SELECT second_at, update_id, bid, bid_qty, ask, ask_qty, bids, asks, received_at FROM spot_quotes "
        "WHERE received_at <= :now ORDER BY second_at DESC LIMIT 1"), {"now": now}).mappings().first()
    if row is None:
        return None
    return {**dict(row), "bids": levels(row["bids"]), "asks": levels(row["asks"]),
            "age_ms": age_ms(now, row["received_at"])}


def feed(connection: Connection, now: datetime) -> dict[str, Any]:
    """The feed's state with its current instrument (None when none is stored yet) and the instrument check's age."""
    state = dict(connection.execute(text("SELECT * FROM spot_feed_state WHERE id = 1")).mappings().one())
    instrument = None
    if state["instrument_id"] is not None:
        row = connection.execute(text(
            "SELECT id, symbol, status, usable, tick_size, step_size, min_qty, max_qty, min_notional, max_notional, "
            "checked_at FROM spot_instruments WHERE id = :id"), {"id": state["instrument_id"]}).mappings().one()
        instrument = dict(row)
    checked = state["instrument_checked_at"]
    return {**state, "instrument": instrument,
            "instrument_age_ms": age_ms(now, checked) if checked is not None else None}


def filters(instrument: dict[str, Any]) -> Filters:
    return Filters(step=instrument["step_size"], min_qty=instrument["min_qty"], max_qty=instrument["max_qty"],
                   min_notional=instrument["min_notional"], max_notional=instrument["max_notional"])


def daily_closes(connection: Connection, first_ms: int, last_ms: int) -> dict[int, Decimal]:
    """The stored final daily closes from ``first_ms`` to ``last_ms`` (both inclusive), by the day's open time."""
    rows = connection.execute(text(
        "SELECT open_ms, close FROM spot_daily_bars WHERE open_ms >= :first AND open_ms <= :last ORDER BY open_ms"),
        {"first": first_ms, "last": last_ms}).all()
    return {int(row[0]): row[1] for row in rows}


# ---- the account's records ---------------------------------------------------------------------------------------

def stored_definitions(connection: Connection, identities: tuple[str, ...]) -> dict[str, str]:
    rows = connection.execute(text("SELECT id, sha256 FROM execution_definitions WHERE id = ANY(:ids)"),
                              {"ids": list(identities)}).all()
    return {row[0]: row[1] for row in rows}


def holding(connection: Connection) -> dict[str, Decimal]:
    """The BTC holding, locked (the account row is locked first, by the fence)."""
    row = connection.execute(text(
        "SELECT quantity, reserved FROM account_holdings WHERE asset = :asset FOR UPDATE"),
        {"asset": BASE}).mappings().one()
    return {"quantity": row["quantity"], "reserved": row["reserved"]}


def current_run(connection: Connection) -> dict[str, Any] | None:
    """The newest run, locked."""
    row = connection.execute(text(
        "SELECT * FROM spot_runs ORDER BY seq DESC LIMIT 1 FOR UPDATE")).mappings().first()
    return dict(row) if row else None


def pending_requests(connection: Connection) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(text(
        "SELECT * FROM spot_owner_requests WHERE status = 'PENDING' ORDER BY created_at, id FOR UPDATE"
    )).mappings().all()]


def answer_request(connection: Connection, request: dict[str, Any], status: str, reasons: list[str],
                   at: datetime) -> None:
    connection.execute(text(
        "UPDATE spot_owner_requests SET status = :status, reasons = :reasons, answered_at = :at WHERE id = :id"),
        {"status": status, "reasons": reasons, "at": at, "id": request["id"]})


def run_event(connection: Connection, run: dict[str, Any], kind: str, at: datetime, *, actor: str = "SYSTEM",
              request_id: UUID | None = None, detail: dict[str, Any] | None = None) -> None:
    connection.execute(text(
        "INSERT INTO spot_run_events (run_id, kind, actor, request_id, at, detail) "
        "VALUES (:run, :kind, :actor, :request, :at, CAST(:detail AS jsonb))"),
        {"run": run["id"], "kind": kind, "actor": actor, "request": request_id, "at": at,
         "detail": jdump(detail or {})})


def insert_run(connection: Connection, *, identity: UUID, rule: tuple[str, str], policy: tuple[str, str],
               cost: tuple[str, str], code_identity: str, started_by: str, request_id: UUID | None, at: datetime,
               equity: Decimal, nav: Decimal, causes: list[str]) -> dict[str, Any]:
    connection.execute(text(
        "INSERT INTO spot_runs (id, policy_id, policy_sha256, rule_id, rule_sha256, cost_id, cost_sha256, "
        "code_identity, started_by, request_id, state, causes, started_at, start_equity, start_nav, high_water_nav) "
        "VALUES (:id, :policy, :policy_sha, :rule, :rule_sha, :cost, :cost_sha, :code, :by, :request, :state, "
        ":causes, :at, :equity, :nav, :nav)"),
        {"id": identity, "policy": policy[0], "policy_sha": policy[1], "rule": rule[0], "rule_sha": rule[1],
         "cost": cost[0], "cost_sha": cost[1], "code": code_identity, "by": started_by, "request": request_id,
         "state": "PAUSED" if causes else "RUNNING", "causes": causes, "at": at, "equity": equity, "nav": nav})
    return dict(connection.execute(text("SELECT * FROM spot_runs WHERE id = :id FOR UPDATE"),
                                   {"id": identity}).mappings().one())


def update_run(connection: Connection, run: dict[str, Any], **fields: Any) -> None:
    fields["version"] = run["version"] + 1
    names = ", ".join(f"{name} = :{name}" for name in fields)
    connection.execute(text(f"UPDATE spot_runs SET {names} WHERE id = :id"), {**fields, "id": run["id"]})
    run.update(fields)


def unresolved_latches(connection: Connection, run_id: UUID) -> list[dict[str, Any]]:
    return [dict(row) for row in connection.execute(text(
        "SELECT * FROM spot_latches WHERE run_id = :run AND resolved_at IS NULL ORDER BY latched_at"),
        {"run": run_id}).mappings().all()]


def insert_latch(connection: Connection, *, run_id: UUID, cause: str, at: datetime, valuation_id: UUID,
                 trigger: dict[str, Any]) -> UUID:
    identity = stable_id("spot-latch", run_id, cause, at.isoformat())
    connection.execute(text(
        "INSERT INTO spot_latches (id, run_id, cause, latched_at, valuation_id, trigger) "
        "VALUES (:id, :run, :cause, :at, :valuation, CAST(:trigger AS jsonb))"),
        {"id": identity, "run": run_id, "cause": cause, "at": at, "valuation": valuation_id,
         "trigger": jdump(trigger)})
    return identity


def resolve_latch(connection: Connection, latch_id: UUID, at: datetime, resolution: dict[str, Any]) -> None:
    connection.execute(text(
        "UPDATE spot_latches SET resolved_at = :at, resolution = CAST(:resolution AS jsonb) WHERE id = :id"),
        {"id": latch_id, "at": at, "resolution": jdump(resolution)})


def reference(connection: Connection, day: date) -> dict[str, Any] | None:
    row = connection.execute(text("SELECT * FROM spot_daily_references WHERE utc_date = :day"),
                             {"day": day}).mappings().first()
    return dict(row) if row else None


def prior_navs(connection: Connection, since: datetime, until: datetime) -> list[tuple[datetime, Decimal]]:
    rows = connection.execute(text(
        "SELECT valued_at, nav FROM spot_valuations WHERE quality = 'VALID' AND valued_at >= :since "
        "AND valued_at < :until ORDER BY valued_at"), {"since": since, "until": until}).all()
    return [(row[0], row[1]) for row in rows]


def insert_reference(connection: Connection, *, day: date, valuation_id: UUID, nav: Decimal, quality: str,
                     lateness_ms: int, basis: dict[str, Any]) -> None:
    connection.execute(text(
        "INSERT INTO spot_daily_references (utc_date, valuation_id, nav, quality, lateness_ms, basis) "
        "VALUES (:day, :valuation, :nav, :quality, :lateness, CAST(:basis AS jsonb))"),
        {"day": day, "valuation": valuation_id, "nav": nav, "quality": quality, "lateness": lateness_ms,
         "basis": jdump(basis)})


def insert_valuation(connection: Connection, *, identity: UUID, run_id: UUID | None, at: datetime, purpose: str,
                     account: dict[str, Any], quantity: Decimal, bid: dict[str, Any] | None, equity: Decimal | None,
                     nav: Decimal | None, quality: str, reason: str | None) -> None:
    connection.execute(text(
        "INSERT INTO spot_valuations (id, run_id, valued_at, purpose, cash, quantity, bid, bid_second, equity, units, "
        "nav, quality, reason, account_version) VALUES (:id, :run, :at, :purpose, :cash, :quantity, :bid, "
        ":bid_second, :equity, :units, :nav, :quality, :reason, :version)"),
        {"id": identity, "run": run_id, "at": at, "purpose": purpose, "cash": account["cash"], "quantity": quantity,
         "bid": bid["bid"] if bid and quantity > 0 else None,
         "bid_second": bid["second_at"] if bid and quantity > 0 else None, "equity": equity,
         "units": account["units"], "nav": nav, "quality": quality, "reason": reason, "version": account["version"]})


def last_valuation_at(connection: Connection) -> datetime | None:
    return connection.execute(text("SELECT max(valued_at) FROM spot_valuations")).scalar_one()


def last_valuation_version(connection: Connection) -> int | None:
    """The account version the newest valuation saw (the order the account's reads use)."""
    return connection.execute(text(
        "SELECT account_version FROM spot_valuations ORDER BY valued_at DESC, recorded_at DESC LIMIT 1")).scalar()


def hourly_valued(connection: Connection, hour: datetime) -> bool:
    return connection.execute(text(
        "SELECT EXISTS (SELECT 1 FROM spot_valuations WHERE purpose = 'HOURLY' AND valued_at >= :hour "
        "AND valued_at < :next)"), {"hour": hour, "next": hour + timedelta(hours=1)}).scalar_one()


def update_nav(connection: Connection, account: dict[str, Any], nav: Decimal) -> None:
    high = account["high_water_nav"]
    raised = high is None or nav > high
    connection.execute(text("UPDATE account_state SET nav = :nav, high_water_nav = :high WHERE id = 1"),
                       {"nav": nav, "high": nav if raised else high})
    account.update(nav=nav, high_water_nav=nav if raised else high)


def insert_fill(connection: Connection, values: dict[str, Any]) -> None:
    values = {**values, "levels": levels_json(values["levels"])}
    names = ", ".join(values)
    placeholders = ", ".join("CAST(:levels AS jsonb)" if name == "levels" else ":" + name for name in values)
    connection.execute(text(f"INSERT INTO spot_fills ({names}) VALUES ({placeholders})"), values)


# ---- the rule's daily readings ------------------------------------------------------------------------------------

def rule_readings(connection: Connection, run_id: UUID, day: date) -> list[dict[str, Any]]:
    """The run's readings of a UTC day, oldest first (a few at most: one per outcome, reason and codes)."""
    return [dict(row) for row in connection.execute(text(
        "SELECT id, outcome, reason, codes, spent FROM spot_rule_readings "
        "WHERE run_id = :run AND utc_date = :day ORDER BY seq"), {"run": run_id, "day": day}).mappings().all()]


def insert_reading(connection: Connection, values: dict[str, Any]) -> None:
    values = {**values, "features": jdump(values["features"]), "detail": jdump(values["detail"])}
    names = ", ".join(values)
    placeholders = ", ".join(f"CAST(:{name} AS jsonb)" if name in ("features", "detail") else ":" + name
                             for name in values)
    connection.execute(text(f"INSERT INTO spot_rule_readings ({names}) VALUES ({placeholders})"), values)
