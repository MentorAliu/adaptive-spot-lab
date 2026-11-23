"""Migration 0008's guard, from an empty database on a cluster whose identities can log in (kept by ExecPlan 0061,
which removed the futures app's clean start and its ``app.migrate --keep-logins``): 0008 adopts the source and research
identities only while they cannot log in, and refuses otherwise, as it stopped the first clean start on the owner's PC
on 2026-10-24. The case runs on a second, empty ``asl_m1_`` database of the test's name; the logins it changes, which
belong to the cluster, are put back as they were."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from psycopg import sql
from sqlalchemy import create_engine, text

ENGINE = Path(__file__).resolve().parents[1]
HEAD = "0041_spot"
# The identities migration 0008 refuses to adopt while they can log in.
KEPT_LOGINS = ("asl_research", "asl_source")


def statement(engine, command) -> None:
    # CREATE and DROP DATABASE cannot run inside a transaction block.
    with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
        connection.connection.driver_connection.execute(command)


def logins(engine) -> dict[str, bool]:
    with engine.connect() as connection:
        return dict(connection.execute(text(
            "SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname IN ('asl_research', 'asl_source')")).all())


def set_logins(engine, login: dict[str, bool]) -> None:
    with engine.begin() as connection:
        for role, value in login.items():
            connection.execute(text(f"ALTER ROLE {role} {'LOGIN' if value else 'NOLOGIN'}"))


def migrate(name: str, *options: str) -> subprocess.CompletedProcess:
    """The update's call, ``python -m app.migrate <head>``, on the database ``name``."""
    return subprocess.run([sys.executable, "-m", "app.migrate", *options, HEAD], cwd=ENGINE,
                          capture_output=True, text=True, timeout=600,
                          env=dict(os.environ, ASL_DB_NAME=name, ASL_DB_ROLE="migration"))


def schema(engine, name: str) -> str | None:
    """The database's revision, or None before the migrations reached it."""
    other = create_engine(engine.url.set(database=name))
    try:
        with other.connect() as connection:
            if connection.execute(text("SELECT to_regclass('public.alembic_version')")).scalar() is None:
                return None
            return connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    finally:
        other.dispose()


@pytest.fixture
def empty(migration_engine):
    name = os.environ["ASL_DB_NAME"] + "_clean"
    before = logins(migration_engine)
    assert set(before) == set(KEPT_LOGINS)
    statement(migration_engine, sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(name)))
    statement(migration_engine, sql.SQL("CREATE DATABASE {} OWNER asl").format(sql.Identifier(name)))
    try:
        yield name
    finally:
        set_logins(migration_engine, before)
        statement(migration_engine, sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(sql.Identifier(name)))


def test_the_plain_migration_refuses_identities_that_can_log_in(empty, migration_engine):
    """The PC's failure, kept as it was: 0008's guard is unchanged."""
    set_logins(migration_engine, {role: True for role in KEPT_LOGINS})
    result = migrate(empty)
    assert result.returncode != 0
    assert "M6 role has unexpected authority; refusing to adopt it" in result.stderr
    assert schema(migration_engine, empty) is None
    assert logins(migration_engine) == {role: True for role in KEPT_LOGINS}
