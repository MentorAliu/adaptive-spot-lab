"""M11: no owner sign-in and no setup.

Revision ID: 0021_no_owner
Revises: 0020_futures

ExecPlan 0042 section 4.2. The owner uses the app alone on the PC and asked on 2026-10-25 for no sign-in and no setup.
The sign-in's tables go, and an owner's request no longer names a session:

- ``owner_approvals.session_id``'s foreign key, then ``owner_sessions`` and ``owner`` (the passphrase's hash and the
  sessions, with their grants), are dropped.
- Seven checks that made an ``OWNER`` row carry a session are replaced by the same checks without it: an owner
  request still needs its idempotency key and request hash (and its correlation id where it did), and on the two
  approval tables a row that is not the owner's still carries no session. The ``session_id`` columns stay, nullable:
  a row written before keeps its value, and nothing writes one any more.

Downgrade refuses while an ``OWNER`` row without a session exists (the old checks cannot hold for it) or an owner
approval names a session (the sessions are gone, so the foreign key cannot be restored); otherwise it restores the
two tables (empty), their grants, the foreign key and the old checks.
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision = "0021_no_owner"
down_revision = "0020_futures"
branch_labels = None
depends_on = None

# (table, the old check's name, its definition, the new check's name, its definition or None to drop it). The old
# definitions are those of the migrations that made them (0007, 0008, 0009 and 0011); two of their names are the ones
# PostgreSQL gave them.
CHECKS = (
    ("owner_approvals", "owner_approvals_actor_session", "(actor = 'OWNER') = (session_id IS NOT NULL)",
     "owner_approvals_actor_session", "actor = 'OWNER' OR session_id IS NULL"),
    ("agent_approvals", "agent_approvals_actor_session", "(actor = 'OWNER') = (session_id IS NOT NULL)",
     "agent_approvals_actor_session", "actor = 'OWNER' OR session_id IS NULL"),
    ("agent_runtime_profiles", "agent_profile_owner_key",
     "source <> 'OWNER' OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL)",
     "agent_profile_owner_key", "source <> 'OWNER' OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL)"),
    ("agent_workflows", "agent_workflow_owner_key",
     "created_by <> 'OWNER' OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL)",
     "agent_workflow_owner_key", "created_by <> 'OWNER' OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL)"),
    ("agent_runtime_requests", "agent_request_owner_session", "actor <> 'OWNER' OR session_id IS NOT NULL",
     "agent_request_owner_session", None),
    ("source_refresh_requests", "source_refresh_requests_check",
     "actor <> 'OWNER' OR (session_id IS NOT NULL AND request_hash IS NOT NULL AND idempotency_key IS NOT NULL)",
     "source_refresh_requests_owner_key",
     "actor <> 'OWNER' OR (request_hash IS NOT NULL AND idempotency_key IS NOT NULL)"),
    ("decision_pause_requests", "decision_pause_requests_check3",
     "actor <> 'OWNER' OR (num_nulls(session_id, idempotency_key, request_hash, correlation_id) = 0 "
     "AND num_nonnulls(workflow_id, tool_call_id, reason, cites, permission_epoch) = 0)",
     "decision_pause_requests_owner_shape",
     "actor <> 'OWNER' OR (num_nulls(idempotency_key, request_hash, correlation_id) = 0 "
     "AND num_nonnulls(workflow_id, tool_call_id, reason, cites, permission_epoch) = 0)"),
)
# The column that says a row is the owner's, per table.
OWNER_COLUMN = {"agent_runtime_profiles": "source", "agent_workflows": "created_by"}


def _check_named(bind, table: str, name: str) -> None:
    """The check this migration replaces must be the one that named the session; anything else is not touched."""
    found = bind.exec_driver_sql(
        "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
        "WHERE conrelid = %(table)s::regclass AND conname = %(name)s AND contype = 'c'",
        {"table": table, "name": name}).scalar_one_or_none()
    if found is None or "session_id" not in found:
        raise RuntimeError(f"{table}: the check {name} is not the one that required a session; nothing changed")


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    for table, old, _old_definition, new, definition in CHECKS:
        _check_named(bind, table, old)
        change = f"ALTER TABLE {table} DROP CONSTRAINT {old}"
        if definition is not None:
            change += f", ADD CONSTRAINT {new} CHECK ({definition})"
        op.execute(change)
    op.execute("ALTER TABLE owner_approvals DROP CONSTRAINT owner_approvals_session_id_fkey")
    op.execute("DROP TABLE owner_sessions, owner")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    sessionless = " + ".join(
        f"(SELECT count(*) FROM {table} WHERE {OWNER_COLUMN.get(table, 'actor')} = 'OWNER' AND session_id IS NULL)"
        for table, *_rest in CHECKS)
    if bind.exec_driver_sql(f"SELECT {sessionless}").scalar_one():
        raise RuntimeError("owner records without a session exist; downgrade refused; fix forward")
    if bind.exec_driver_sql("SELECT count(*) FROM owner_approvals WHERE session_id IS NOT NULL").scalar_one():
        raise RuntimeError("owner approvals name sessions this migration dropped; downgrade refused; fix forward")
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
    # 0002's grants on the two tables, as they were.
    op.execute("GRANT SELECT, INSERT ON owner, owner_sessions TO asl_api")
    op.execute("GRANT UPDATE (password_hash, failed_logins, locked_until) ON owner TO asl_api")
    op.execute("GRANT UPDATE (revoked_at) ON owner_sessions TO asl_api")
    op.execute("ALTER TABLE owner_approvals ADD CONSTRAINT owner_approvals_session_id_fkey "
               "FOREIGN KEY (session_id) REFERENCES owner_sessions(id)")
    for table, old, old_definition, new, definition in CHECKS:
        change = f"ALTER TABLE {table} "
        if definition is not None:
            change += f"DROP CONSTRAINT {new}, "
        op.execute(change + f"ADD CONSTRAINT {old} CHECK ({old_definition})")
