"""M1 owner, journal, funding and reconciliation infrastructure.

Revision ID: 0002_m1_account
Revises: 0001_foundation
"""

import os
from pathlib import Path

import sqlalchemy as sa
from psycopg import sql
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "0002_m1_account"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None

money = sa.Numeric(38, 8, asdecimal=True)
precise = sa.Numeric(72, 36, asdecimal=True)


def upgrade() -> None:
    password_path = Path(os.environ.get("ASL_API_DB_PASSWORD_FILE", "/run/secrets/api_db_password"))
    password = password_path.read_text(encoding="utf-8").strip()
    if len(password) < 32:
        raise RuntimeError("API database identity is unavailable")

    op.create_table(
        "owner",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("failed_logins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="owner_singleton"),
    )
    op.create_table(
        "owner_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("token_hash", sa.String(64), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "account_state",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("version", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("fencing_epoch", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("initialized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("cash", money, nullable=False, server_default="0"),
        sa.Column("reserved", money, nullable=False, server_default="0"),
        sa.Column("contributions", money, nullable=False, server_default="0"),
        sa.Column("units", precise, nullable=False, server_default="0"),
        sa.Column("nav", precise),
        sa.Column("high_water_nav", precise),
        sa.Column("valuation_valid", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("paused", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reconciliation_failed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.CheckConstraint("id = 1", name="account_singleton"),
        sa.CheckConstraint("version >= 0 AND fencing_epoch >= 0", name="account_versions_positive"),
        sa.CheckConstraint("cash >= 0 AND reserved >= 0 AND cash >= reserved AND contributions >= 0 AND units >= 0", name="account_nonnegative"),
    )
    op.execute("INSERT INTO account_state(id) VALUES (1)")
    op.create_table(
        "funding_requests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("kind", sa.String(12), nullable=False),
        sa.Column("amount", money, nullable=False),
        sa.Column("idempotency_key", sa.String(80), unique=True, nullable=False),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("draft_hash", sa.String(64), nullable=False),
        sa.Column("expected_version", sa.BigInteger(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("preflow_equity", money),
        sa.Column("preflow_nav", precise),
        sa.Column("issued_units", precise),
        sa.Column("unit_residual", precise),
        sa.Column("journal_tx_id", UUID(as_uuid=True), unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("kind IN ('INITIALIZE','TOPUP')", name="funding_kind"),
        sa.CheckConstraint("status IN ('PENDING_VALUATION','POSTED','CANCELED')", name="funding_status"),
        sa.CheckConstraint("amount > 0 AND expected_version >= 0", name="funding_amount_version"),
    )
    op.create_table(
        "journal_transactions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("funding_request_id", UUID(as_uuid=True), sa.ForeignKey("funding_requests.id"), unique=True, nullable=False),
        sa.Column("account_version", sa.BigInteger(), nullable=False),
        sa.Column("event_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "journal_postings",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("tx_id", UUID(as_uuid=True), sa.ForeignKey("journal_transactions.id"), nullable=False),
        sa.Column("asset", sa.String(5), nullable=False),
        sa.Column("book_account", sa.String(32), nullable=False),
        sa.Column("amount", money, nullable=False),
        sa.CheckConstraint("asset IN ('USDT','BTC','SOL')", name="journal_asset"),
        sa.CheckConstraint("book_account IN ('OWNER_CASH','VIRTUAL_CAPITAL','CLEARING','EXPENSE')", name="journal_account"),
        sa.CheckConstraint("amount <> 0", name="journal_nonzero"),
    )
    op.create_index("journal_postings_tx_asset", "journal_postings", ["tx_id", "asset"])
    op.create_table(
        "reservations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("idempotency_key", sa.String(80), unique=True, nullable=False),
        sa.Column("asset", sa.String(5), nullable=False),
        sa.Column("amount", money, nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("fencing_epoch", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("asset IN ('USDT','BTC','SOL') AND amount > 0", name="reservation_valid"),
        sa.CheckConstraint("status IN ('ACTIVE','RELEASED')", name="reservation_status"),
    )
    op.create_table(
        "owner_decisions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("funding_request_id", UUID(as_uuid=True), sa.ForeignKey("funding_requests.id"), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("target_hash", sa.String(64), nullable=False),
        sa.Column("account_version", sa.BigInteger(), nullable=False),
        sa.Column("owner_id", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("action IN ('CONFIRM','RETRY','CANCEL')", name="owner_decision_action"),
        sa.CheckConstraint("owner_id = 1", name="owner_decision_identity"),
    )
    op.create_table(
        "audit_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("event", sa.String(60), nullable=False),
        sa.Column("correlation_id", sa.String(80), nullable=False),
        sa.Column("object_id", UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("event", sa.String(60), nullable=False),
        sa.Column("object_id", UUID(as_uuid=True), nullable=False),
        sa.Column("account_version", sa.BigInteger(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.execute("""
        CREATE FUNCTION asl_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN RAISE EXCEPTION 'append-only record'; END $$
    """)
    for table in ("journal_transactions", "journal_postings", "owner_decisions", "audit_events", "outbox_events"):
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    op.execute("""
        CREATE FUNCTION asl_check_journal_balance() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM journal_postings WHERE tx_id = NEW.tx_id
            GROUP BY asset HAVING SUM(amount) <> 0 OR COUNT(*) < 2
          ) THEN RAISE EXCEPTION 'unbalanced journal transaction'; END IF;
          RETURN NULL;
        END $$
    """)
    op.execute("""
        CREATE CONSTRAINT TRIGGER journal_balanced AFTER INSERT ON journal_postings
        DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION asl_check_journal_balance()
    """)

    raw = op.get_bind().connection.driver_connection
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_api'")
        if cursor.fetchone() is None:
            cursor.execute("CREATE ROLE asl_api LOGIN")
        cursor.execute(sql.SQL("ALTER ROLE asl_api PASSWORD {}").format(sql.Literal(password)))
    database_name = os.environ.get("ASL_DB_NAME", "asl")
    with raw.cursor() as cursor:
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO asl_api").format(sql.Identifier(database_name)))
    op.execute("GRANT USAGE ON SCHEMA public TO asl_api")
    op.execute("GRANT SELECT ON alembic_version, system_metadata, owner, owner_sessions, account_state, funding_requests, journal_transactions, journal_postings, reservations, owner_decisions, audit_events, outbox_events TO asl_api")
    op.execute("GRANT INSERT ON owner, owner_sessions, funding_requests, journal_transactions, journal_postings, reservations, owner_decisions, audit_events, outbox_events TO asl_api")
    op.execute("GRANT UPDATE (failed_logins, locked_until, password_hash) ON owner TO asl_api")
    op.execute("GRANT UPDATE (revoked_at) ON owner_sessions TO asl_api")
    op.execute("GRANT UPDATE (version, fencing_epoch, initialized, cash, reserved, contributions, units, nav, high_water_nav, valuation_valid, paused, reconciliation_failed) ON account_state TO asl_api")
    op.execute("GRANT UPDATE (status, preflow_equity, preflow_nav, issued_units, unit_residual, journal_tx_id, completed_at) ON funding_requests TO asl_api")
    op.execute("GRANT UPDATE (status) ON reservations TO asl_api")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE journal_postings_id_seq, outbox_events_id_seq TO asl_api")


def downgrade() -> None:
    raise RuntimeError("M1 financial history cannot be downgraded destructively")
