import os
from functools import lru_cache
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

# ExecPlan 0060: the spot app reads only what migration 0041 creates. The update applies 0041 before it starts the new
# api, so readiness accepts 0041 alone, and every page reports the schema as pending until it is applied.
CURRENT_REVISION = "0041_spot"
SPOT_REVISIONS = frozenset({CURRENT_REVISION})
# The schemas readiness accepts. The update file reads this name from the code it built, to tell whether the new api
# can run before the migration (tools/update.ps1, step 5): keep the name.
ACCEPTED_REVISIONS = SPOT_REVISIONS


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    role = os.environ.get("ASL_DB_ROLE", "api")
    pool = {"pool_size": 5, "max_overflow": 5, "pool_timeout": 2} if role == "api" else {}
    return create_engine(database_url(), pool_pre_ping=True, hide_parameters=True,
                         connect_args=connection_options(role), **pool)


def connection_options(role: str) -> dict:
    # Worker I/O must not outlive the 10-second lease. Independent control and
    # writer connections are bounded even during lock contention or DB failure.
    options = {"connect_timeout": 3}
    if role in ("market_worker", "api", "execution"):
        options["options"] = "-c statement_timeout=2000 -c lock_timeout=1000 -c idle_in_transaction_session_timeout=3000"
    return options


def database_url() -> URL:
    role = os.environ.get("ASL_DB_ROLE", "api")
    identities = {
        "migration": ("asl", "/run/secrets/postgres_password"),
        "api": ("asl_api", "/run/secrets/api_db_password"),
        "market_worker": ("asl_market_worker", "/run/secrets/market_worker_password"),
        "execution": ("asl_execution", "/run/secrets/execution_db_password"),
    }
    if role not in identities:
        raise ValueError("Unknown database identity")
    username, default_file = identities[role]
    password_file = Path(os.environ.get("ASL_DB_PASSWORD_FILE", default_file))
    password = password_file.read_text(encoding="utf-8").strip()
    if not password:
        raise ValueError("Database identity is unavailable")
    return URL.create(
        "postgresql+psycopg",
        username=username,
        password=password,
        host=os.environ.get("ASL_DB_HOST", "postgres"),
        database=os.environ.get("ASL_DB_NAME", "asl"),
    )


def database_ready() -> bool:
    try:
        with get_engine().connect() as connection:
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
        return revision in ACCEPTED_REVISIONS
    except Exception:
        # Health responses must not disclose SQL or connection details.
        return False


def schema_revision() -> str | None:
    """The applied Alembic revision, or None when the database is unreachable."""
    try:
        with get_engine().connect() as connection:
            return connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    except Exception:
        return None
