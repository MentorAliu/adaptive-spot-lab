"""Shared fixtures: the spot harness (``spot_support``) and the migration identity on an isolated ``asl_m1_``
database (ExecPlan 0060; the M2 market tests that held it are gone with the old market feed)."""

import os

import pytest
from spot_support import spot as spot  # noqa: F401  (pytest fixture)
from sqlalchemy import create_engine

from app.db import database_url


@pytest.fixture
def migration_engine(monkeypatch):
    if os.environ.get("ASL_TEST_ISOLATED") != "1" or not os.environ.get("ASL_DB_NAME", "").startswith("asl_m1_"):
        pytest.skip("Migration tests require an isolated asl_m1_ disposable database")
    monkeypatch.setenv("ASL_DB_ROLE", "migration")
    engine = create_engine(database_url(), pool_pre_ping=True)
    monkeypatch.setenv("ASL_DB_ROLE", "api")
    try:
        yield engine
    finally:
        engine.dispose()
