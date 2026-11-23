"""The execution worker's fenced authority (M3's rules, kept by ExecPlan 0060 for the spot engine).

Every writer of the account runs inside a transaction that already holds the execution lease (FOR KEY SHARE) and the
account row (FOR UPDATE), in that fixed order, and re-verifies the lease just before COMMIT. Only the spot ledger
(``app.spot.ledger``) posts the journal; database triggers reject any other source for the execution role.
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine

from app.execution.lifecycle import stable_id
from app.execution.numbers import ZERO, add

LEASE_SECONDS = 10


class LostAuthority(RuntimeError):
    """The execution lease or fencing epoch no longer belongs to this worker."""


class IntegrityFailure(RuntimeError):
    """A deterministic invariant failed; the step must not be retried blindly."""


_JSON = json.JSONEncoder(sort_keys=True, separators=(",", ":"), default=str)


def jdump(value: Any) -> str:
    return _JSON.encode(value)


# --- execution lease --------------------------------------------------------------

def acquire_lease(owner_id: UUID, engine: Engine) -> int | None:
    with engine.begin() as connection:
        row = connection.execute(text(
            "UPDATE execution_lease SET owner_id = :owner, epoch = epoch + 1, "
            "expires_at = clock_timestamp() + interval '10 seconds' "
            "WHERE id = 1 AND (expires_at IS NULL OR expires_at <= clock_timestamp()) RETURNING epoch"
        ), {"owner": owner_id}).first()
        if row is None:
            return None
        epoch = int(row[0])
        # The account fencing epoch follows the lease; stale holders fail every write.
        connection.execute(text("SELECT id FROM account_state WHERE id = 1 FOR UPDATE"))
        connection.execute(text(
            "UPDATE account_state SET fencing_epoch = :epoch WHERE id = 1 AND fencing_epoch < :epoch"
        ), {"epoch": epoch})
        return epoch


def renew_lease(owner_id: UUID, epoch: int, engine: Engine) -> bool:
    with engine.begin() as connection:
        row = connection.execute(text(
            "UPDATE execution_lease SET expires_at = clock_timestamp() + interval '10 seconds' "
            "WHERE id = 1 AND owner_id = :owner AND epoch = :epoch AND expires_at > clock_timestamp() "
            "RETURNING epoch"
        ), {"owner": owner_id, "epoch": epoch}).first()
        return row is not None


def release_lease(owner_id: UUID, epoch: int, engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text(
            "UPDATE execution_lease SET expires_at = clock_timestamp() "
            "WHERE id = 1 AND owner_id = :owner AND epoch = :epoch"
        ), {"owner": owner_id, "epoch": epoch})


def fence(connection: Connection, owner_id: UUID, epoch: int) -> dict[str, Any]:
    """Lock lease (KEY SHARE) then account (UPDATE); verify authority; return the account."""
    lease = connection.execute(text(
        "SELECT owner_id, epoch, expires_at > clock_timestamp() AS valid "
        "FROM execution_lease WHERE id = 1 FOR KEY SHARE"
    )).mappings().one()
    if lease["owner_id"] != owner_id or lease["epoch"] != epoch or not lease["valid"]:
        raise LostAuthority("execution_lease_lost")
    account = dict(connection.execute(text(
        "SELECT * FROM account_state WHERE id = 1 FOR UPDATE"
    )).mappings().one())
    if account["fencing_epoch"] != epoch:
        raise LostAuthority("fencing_epoch_mismatch")
    return account


def recheck(connection: Connection, owner_id: UUID, epoch: int) -> None:
    """Re-verify authority immediately before COMMIT."""
    lease = connection.execute(text(
        "SELECT owner_id, epoch, expires_at > clock_timestamp() AS valid FROM execution_lease WHERE id = 1"
    )).mappings().one()
    if lease["owner_id"] != owner_id or lease["epoch"] != epoch or not lease["valid"]:
        raise LostAuthority("execution_lease_lost_before_commit")


def db_now(engine: Engine) -> datetime:
    with engine.connect() as connection:
        return connection.execute(text("SELECT clock_timestamp()")).scalar_one()


# --- locked state reads --------------------------------------------------------------

def incident(connection: Connection, mode: str, code: str, event: str, at: datetime,
             symbol: str | None = None, detail: dict[str, Any] | None = None, run_id: Any = None) -> None:
    connection.execute(text(
        "INSERT INTO execution_incidents (mode, code, symbol, event, at, detail, run_id) "
        "VALUES (:mode, :code, :symbol, :event, :at, CAST(:detail AS jsonb), :run)"
    ), {"mode": mode, "code": code[:64], "symbol": symbol, "event": event, "at": at,
        "detail": jdump(detail or {}), "run": run_id})


def audit_outbox(connection: Connection, event: str, object_id: UUID, version: int,
                 correlation: str, payload: dict[str, Any]) -> None:
    connection.execute(text(
        "INSERT INTO audit_events (id, event, correlation_id, object_id) VALUES (:id, :event, :correlation, :object)"
    ), {"id": stable_id("audit", event, object_id, correlation), "event": event[:60],
        "correlation": correlation[:80], "object": object_id})
    connection.execute(text(
        "INSERT INTO outbox_events (event, object_id, account_version, payload) "
        "VALUES (:event, :object, :version, CAST(:payload AS json))"
    ), {"event": event[:60], "object": object_id, "version": version, "payload": jdump(payload)})


def bump_account(connection: Connection, account: dict[str, Any], *, cash_delta: Decimal = ZERO,
                 reserved_delta: Decimal = ZERO) -> int:
    """Balance or reservation change: exact deltas and one account version increment."""
    new_cash = add(account["cash"], cash_delta)
    new_reserved = add(account["reserved"], reserved_delta)
    if new_cash < 0 or new_reserved < 0 or new_cash < new_reserved:
        raise IntegrityFailure("account_projection_negative")
    version = account["version"] + 1
    connection.execute(text(
        "UPDATE account_state SET cash = :cash, reserved = :reserved, version = :version WHERE id = 1"
    ), {"cash": new_cash, "reserved": new_reserved, "version": version})
    account.update(cash=new_cash, reserved=new_reserved, version=version)
    return version
