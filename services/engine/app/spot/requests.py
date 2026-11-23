"""The owner's run requests for the spot account (ExecPlan 0060 section 4.9; ``app.futures.requests`` until then):
Pause, Resume, Stop and sell, and Start.

The API records a request; the spot engine applies it in its fenced step and answers it once (``APPLIED`` or
``REJECTED`` with its reasons), so a request returns "accepted", never "done". Each is idempotent by key and bound to
the run the owner saw; the checks here only refuse what the engine would refuse anyway, early and with a clear code.
``STOP`` always sells: a stopping run sells the BTC it holds at once and stops once only USDT (or unsellable dust) is
held, whoever stopped it (``SPOT_POLICY_V1``).
"""

import hashlib
import json
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import IntegrityError

from app.db import get_engine
from app.spot_market.views import iso, ready

KINDS = ("PAUSE", "RESUME", "STOP", "START")


class SpotError(Exception):
    def __init__(self, code: str, status: int = 400):
        self.code = code
        self.status = status
        super().__init__(code)


def request_hash(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _audit(connection: Connection, event: str, object_id: UUID, correlation: str, payload: dict[str, Any]) -> None:
    version = connection.execute(text("SELECT version FROM account_state WHERE id = 1")).scalar_one()
    connection.execute(text(
        "INSERT INTO audit_events (id, event, correlation_id, object_id) VALUES (:id, :event, :correlation, :object)"
    ), {"id": uuid4(), "event": event, "correlation": correlation[:80], "object": object_id})
    connection.execute(text(
        "INSERT INTO outbox_events (event, object_id, account_version, payload) "
        "VALUES (:event, :object, :version, CAST(:payload AS json))"
    ), {"event": event, "object": object_id, "version": version,
        "payload": json.dumps(payload, sort_keys=True, default=str)})


def _view(row: Any) -> dict[str, Any]:
    return {"id": str(row["id"]), "kind": row["kind"], "run_id": None if row["run_id"] is None else str(row["run_id"]),
            "idempotency_key": row["idempotency_key"], "status": row["status"], "reasons": list(row["reasons"]),
            "created_at": iso(row["created_at"]), "answered_at": iso(row["answered_at"])}


def _existing(connection: Connection, key: str, digest: str) -> dict[str, Any] | None:
    row = connection.execute(text("SELECT * FROM spot_owner_requests WHERE idempotency_key = :key"),
                             {"key": key}).mappings().first()
    if row is None:
        return None
    if row["request_hash"] != digest:
        raise SpotError("IDEMPOTENCY_CONFLICT", 409)
    return _view(row)


def submit(*, kind: str, run_id: UUID | None, key: str, correlation: str) -> dict[str, Any]:
    if not ready():
        raise SpotError("SPOT_SCHEMA_PENDING", 409)
    if kind not in KINDS:
        raise SpotError("UNKNOWN_REQUEST", 422)
    if (kind == "START") != (run_id is None):
        raise SpotError("RUN_REQUIRED" if run_id is None else "START_TAKES_NO_RUN", 422)
    payload = {"kind": kind, "run_id": None if run_id is None else str(run_id)}
    digest = request_hash(payload)
    try:
        with get_engine().begin() as connection:
            found = _existing(connection, key, digest)
            if found is not None:
                return found
            run = connection.execute(text(
                "SELECT id, state FROM spot_runs ORDER BY seq DESC LIMIT 1")).mappings().first()
            live = run is not None and run["state"] != "STOPPED"
            if kind == "START":
                if live:
                    raise SpotError("RUN_LIVE", 409)
                if not connection.execute(text("SELECT initialized FROM account_state WHERE id = 1")).scalar_one():
                    raise SpotError("NOT_FUNDED", 409)
            elif not live:
                raise SpotError("RUN_NOT_LIVE", 409)
            elif run["id"] != run_id:
                raise SpotError("RUN_CHANGED", 409)
            elif kind == "PAUSE" and run["state"] == "STOPPING":
                raise SpotError("RUN_STOPPING", 409)
            identity = uuid4()
            row = connection.execute(text(
                "INSERT INTO spot_owner_requests (id, kind, run_id, idempotency_key, request_hash) "
                "VALUES (:id, :kind, :run, :key, :hash) RETURNING *"),
                {"id": identity, "kind": kind, "run": run_id, "key": key, "hash": digest}).mappings().one()
            _audit(connection, f"SPOT_{kind}_REQUESTED", identity, correlation, payload)
            return _view(row)
    except IntegrityError:
        # A concurrent request with the same key committed first: answer with it.
        with get_engine().connect() as connection:
            found = _existing(connection, key, digest)
        if found is None:
            raise
        return found


def by_key(key: str) -> dict[str, Any] | None:
    if not ready():
        return None
    with get_engine().connect() as connection:
        row = connection.execute(text("SELECT * FROM spot_owner_requests WHERE idempotency_key = :key"),
                                 {"key": key}).mappings().first()
    return None if row is None else _view(row)
