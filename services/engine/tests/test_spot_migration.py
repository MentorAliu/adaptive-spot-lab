"""Migration 0041 (ExecPlan 0060 section 6, R7): the frozen definitions, the futures run's retirement, the refusal
unless the futures account is flat, the archive, and the downgrade refused once a spot fill exists. Alembic runs in a
process of its own on the scratch database (``spot_support``); every row seeded here is SYNTHETIC."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from spot_support import CODE, T0, reset
from sqlalchemy import text

from app.spot import definitions

ENGINE = Path(__file__).resolve().parents[1]
MIGRATION = ENGINE / "alembic" / "versions" / "0041_spot.py"
READ_SCHEMAS = ("agent_read", "evaluation_read", "research_read")


def load():
    spec = importlib.util.spec_from_file_location("migration_0041", MIGRATION)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_frozen_definitions_equal_the_code():
    module = load()
    assert module.definition_rows() == definitions.seed_rows()
    assert [row["id"] for row in module.definition_rows()] == ["SPOT_RULE_V1", "SPOT_POLICY_V1", "SPOT_COST_V1"]


def seed_live_futures_run(spot) -> dict[str, object]:
    """A paused futures run at 0040 with an open daily-loss latch and a pending owner request, as a live run looks.
    The archive keeps an earlier test run's rows (the harness empties only ``public``): every key here is new."""
    ids = {"run": uuid4(), "valuation": uuid4(), "latch": uuid4(), "request": uuid4()}
    with spot.admin.begin() as connection:
        connection.execute(text(
            "INSERT INTO futures_runs (id, policy_id, policy_sha256, cost_id, cost_sha256, code_identity, started_by, "
            "state, causes, started_at, start_equity, start_nav, high_water_nav) VALUES (:run, 'FUTURES_POLICY_V2', "
            "(SELECT sha256 FROM execution_definitions WHERE id = 'FUTURES_POLICY_V2'), 'FUTURES_COST_V1', "
            "(SELECT sha256 FROM execution_definitions WHERE id = 'FUTURES_COST_V1'), :code, 'SYSTEM', 'PAUSED', "
            "ARRAY['DAILY_LOSS'], :at, 10000, 100, 100)"), {**ids, "code": CODE, "at": T0})
        connection.execute(text(
            "INSERT INTO futures_valuations (id, run_id, valued_at, purpose, cash, reserved, units, quality, "
            "account_version, equity, nav) VALUES (:valuation, :run, :at, 'LATCH', 10000, 0, 100, 'VALID', 1, 9790, "
            "97.9)"), {**ids, "at": T0})
        connection.execute(text(
            "INSERT INTO futures_latches (id, run_id, cause, latched_at, valuation_id, trigger) VALUES (:latch, :run, "
            "'DAILY_LOSS', :at, :valuation, '{}')"), {**ids, "at": T0})
        connection.execute(text(
            "INSERT INTO futures_owner_requests (id, kind, run_id, idempotency_key, request_hash) VALUES (:request, "
            "'RESUME', :run, :key, :hash)"), {**ids, "key": f"resume-{ids['request'].hex}", "hash": "a" * 64})
    return ids


def table_counts(spot, schema: str, names) -> dict[str, int]:
    with spot.admin.connect() as connection:
        return {name: connection.execute(text(f'SELECT count(*) FROM {schema}."{name}"')).scalar_one()
                for name in names}


def test_the_migration_retires_the_futures_run_and_rolls_back_only_until_a_spot_fill(spot):
    module = load()

    def alembic(*arguments: str) -> subprocess.CompletedProcess:
        for engine in (spot.execution, spot.api, spot.market, spot.admin):
            engine.dispose()
        return subprocess.run([sys.executable, "-m", "alembic", *arguments], cwd=ENGINE, capture_output=True,
                              text=True, timeout=600, env=dict(os.environ, ASL_DB_ROLE="migration"))

    def version() -> str:
        return spot.scalar("SELECT version_num FROM alembic_version")

    assert version() == module.revision
    spot.ready()
    spot.start()
    spot.step(T0)
    assert len(spot.fills()) == 1
    done = alembic("downgrade", module.down_revision)
    assert done.returncode != 0 and "a spot fill exists; downgrade refused" in done.stderr, done.stderr[-2000:]
    assert version() == module.revision and len(spot.fills()) == 1
    with spot.admin.begin() as connection:
        reset(connection)
    try:
        done = alembic("downgrade", module.down_revision)
        assert done.returncode == 0, done.stderr[-2000:]
        assert version() == module.down_revision
        assert spot.scalar("SELECT to_regnamespace('archive') IS NULL")
        assert spot.scalar("SELECT to_regclass('public.spot_fills') IS NULL AND to_regclass('public.futures_runs') "
                           "IS NOT NULL")
        assert spot.scalar("SELECT count(*) FROM execution_definitions WHERE kind LIKE 'SPOT_%'") == 0
        assert spot.scalar("SELECT count(*) FROM information_schema.columns WHERE table_name = "
                           "'journal_transactions' AND column_name = 'spot_fill_id'") == 0
        views = spot.scalar("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                            "WHERE n.nspname = ANY(:schemas) AND c.relkind IN ('v','m')", schemas=list(READ_SCHEMAS))
        ids = seed_live_futures_run(spot)
        spot.raw("UPDATE account_holdings SET quantity = 0.5, reserved = 0.1 WHERE asset = 'SOL'")
        refused = alembic("upgrade", "head")
        assert refused.returncode != 0 and "the futures account is not flat (a coin is reserved)" in refused.stderr, \
            refused.stderr[-2000:]
        assert version() == module.down_revision
        assert spot.scalar("SELECT state FROM futures_runs WHERE id = :id", id=ids["run"]) == "PAUSED"
        spot.raw("UPDATE account_holdings SET quantity = 0, reserved = 0 WHERE asset = 'SOL'")
        archived = [name for name in spot.rows(
            "SELECT relname FROM pg_class WHERE relnamespace = 'public'::regnamespace AND relkind IN ('r','p')")
            if name["relname"] not in module.KEPT]
        before = table_counts(spot, "public", [row["relname"] for row in archived])
    finally:
        restored = alembic("upgrade", "head")
    assert restored.returncode == 0, restored.stderr[-2000:]
    assert version() == module.revision
    # Every archived table kept every row; the run's retirement added its two events.
    after = table_counts(spot, "archive", before)
    assert after == before | {"futures_run_events": before["futures_run_events"] + 2}
    assert spot.scalar("SELECT count(*) FROM archive.moved_objects WHERE kind IN ('VIEW','MATVIEW')") == views
    assert spot.scalar("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                       "WHERE n.nspname = ANY(:schemas) AND c.relkind IN ('v','m')", schemas=list(READ_SCHEMAS)) == 0
    assert not spot.scalar("SELECT has_schema_privilege('asl_api', 'archive', 'USAGE') OR "
                           "has_schema_privilege('asl_execution', 'archive', 'USAGE')")
    run = spot.rows("SELECT state, stop_reason, stopped_at IS NOT NULL AS stopped FROM archive.futures_runs "
                    "WHERE id = :id", id=ids["run"])
    assert run == [{"state": "STOPPED", "stop_reason": "NEW_POLICY", "stopped": True}]
    events = spot.rows("SELECT kind, actor, detail FROM archive.futures_run_events WHERE run_id = :id ORDER BY id",
                       id=ids["run"])
    assert [(e["kind"], e["actor"]) for e in events] == [("FUTURES_RETIRED", "SYSTEM"), ("STOPPED", "SYSTEM")]
    hashes = {row["id"]: row["sha256"] for row in definitions.seed_rows()}
    assert events[0]["detail"] == {
        "stop_reason": "NEW_POLICY", "replaced": "FUTURES_POLICY_V2", "plan": "ExecPlan 0060",
        "policy": "SPOT_POLICY_V1", "policy_sha256": hashes["SPOT_POLICY_V1"],
        "rule": "SPOT_RULE_V1", "rule_sha256": hashes["SPOT_RULE_V1"],
        "cost": "SPOT_COST_V1", "cost_sha256": hashes["SPOT_COST_V1"]}
    assert spot.scalar("SELECT resolution->>'rule' FROM archive.futures_latches WHERE id = :id",
                       id=ids["latch"]) == "RUN_STOPPED"
    assert spot.rows("SELECT status, reasons FROM archive.futures_owner_requests WHERE id = :id",
                     id=ids["request"]) == [{"status": "REJECTED", "reasons": ["FUTURES_RETIRED"]}]
    stored = spot.rows("SELECT id, kind, version, status, canonical, sha256 FROM execution_definitions "
                       "WHERE kind LIKE 'SPOT_%' ORDER BY kind DESC")
    assert sorted(stored, key=lambda r: r["id"]) == sorted(definitions.seed_rows(), key=lambda r: r["id"])
