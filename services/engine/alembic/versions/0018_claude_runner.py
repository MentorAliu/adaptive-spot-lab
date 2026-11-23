"""M11 update 1: the definitions of Claude Code's runner.

Revision ID: 0018_claude_runner
Revises: 0017_market_retention_cost

ExecPlan 0039 section 5.6. Additive: two code-owned agent definitions, frozen below and mirrored by
app.agents.claude_definitions, which the runtime profile (version 5) binds by hash:

- ``MODEL_TABLE_V2``: every role on ``claude-sonnet-5-5`` at ``medium``, the first pair taken (Claude Code lists no
  catalog; the agents' check proves the model answers).
- ``EGRESS_ALLOWLIST_V2``: ``api.anthropic.com`` and ``platform.claude.com`` on port 443, the document the egress gateway
  bakes.

The worker refuses to start unless every stored row equals the code, so the rows come with the code that names them.
Nothing else changes: the provider column keeps ``CODEX`` as the name of the live runner path, and each call's profile
names the CLI.

Downgrade refuses while a runtime profile names either definition, then removes the two rows.
"""

import hashlib
import json

from alembic import op

revision = "0018_claude_runner"
down_revision = "0017_market_retention_cost"
branch_labels = None
depends_on = None

KINDS = ("MODEL_TABLE", "EGRESS_ALLOWLIST")


def seed_rows():
    """The frozen documents, each checked against its own hash."""
    rows = []
    for line in SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KINDS:
            raise RuntimeError("frozen Claude runner definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    ids = [row["id"] for row in seed_rows()]
    if bind.exec_driver_sql(
            f"SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{ids}").scalar_one():
        raise RuntimeError("a runtime profile names the Claude runner's definitions; downgrade refused; fix forward")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this transaction,
    # and delete only the frozen rows, which nothing names (checked above).
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("Claude runner definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")


# (id, kind, version, status, canonical JSON, SHA-256) from ``python -m app.agents.claude_definitions``; a test checks
# they match the code.
SEED_LINES = r"""
["MODEL_TABLE_V2", "MODEL_TABLE", 2, "CODE_OWNED", "{\"id\":\"MODEL_TABLE_V2\",\"kind\":\"MODEL_TABLE\",\"roles\":{\"ANALYST\":[[\"claude-sonnet-5-5\",\"medium\"]],\"COORDINATOR\":[[\"claude-sonnet-5-5\",\"medium\"]],\"EVALUATOR\":[[\"claude-sonnet-5-5\",\"medium\"]],\"RESEARCHER\":[[\"claude-sonnet-5-5\",\"medium\"]]},\"rule\":\"PER_ROLE_THE_FIRST_PAIR_THE_CLI_LISTS_NO_CATALOG_THE_AGENTS_CHECK_PROVES_IT_ANSWERS\",\"source\":\"ExecPlan 0039 section 5.6\",\"status\":\"CODE_OWNED\",\"version\":2}", "d937796545b51fa6193f99983f5fe8e0897f300124547b3b44c5e7295a947fc0"]
["EGRESS_ALLOWLIST_V2", "EGRESS_ALLOWLIST", 2, "CODE_OWNED", "{\"hosts\":[\"api.anthropic.com\",\"platform.claude.com\"],\"id\":\"EGRESS_ALLOWLIST_V2\",\"kind\":\"EGRESS_ALLOWLIST\",\"port\":443,\"refuse\":[\"IP_LITERALS\",\"PRIVATE\",\"LOOPBACK\",\"LINK_LOCAL\",\"METADATA\",\"HOST_GATEWAY\",\"NON_GLOBAL\"],\"source\":\"ExecPlan 0039 section 5.6\",\"status\":\"CODE_OWNED\",\"version\":2}", "f30376891f9ac46ee92c2c64e153460e5a13e35e06d8a94da46185cadcba015b"]
"""
