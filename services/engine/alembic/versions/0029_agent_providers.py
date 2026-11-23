"""ExecPlan 0049: the agents' provider, its usage and the daily spend cap.

Revision ID: 0029_agent_providers
Revises: 0028_leaner_trader

ExecPlan 0049 section 5.7. Additive; nothing of the futures engine, its account, the twins, the scores or the result
checks changes, and no secret is stored anywhere in the database (a key lives only in the runner's ``agent_keys``
volume).

- ``agent_provider_requests``: the owner's pick of the provider that runs the agents (Codex CLI, Claude CLI, Claude
  API, OpenAI API), idempotent and versioned like the owner's other agent requests. The agent worker settles each
  one with a runtime event: ``PROVIDER_REQUESTED`` when it starts the switch, ``PROVIDER_IN_FORCE`` once the test
  call passed, ``PROVIDER_REFUSED`` with the reason otherwise.
- ``agent_spend_caps``: the owner's daily cap in US dollars per paid API (NUMERIC); the newest row of a provider is in
  force.
- ``agent_usage_readings``: what a provider reported about its limits (the Codex app server's windows, the Claude
  CLI's rate-limit events, the APIs' rate-limit headers), as read, with the time.
- ``agent_provider_calls.runtime_provider``: which of the four ran the call (``provider`` keeps ``CODEX`` as the
  name of the live runner path); ``agent_provider_outcomes.cost_usd``: the call's cost calculated in code from its
  tokens and ``API_PRICES_V1`` (NUMERIC; null on the plans).
- Runtime events ``PROVIDER_REQUESTED``, ``PROVIDER_IN_FORCE``, ``PROVIDER_REFUSED``, ``CREDENTIAL_SAVED``,
  ``CREDENTIAL_REMOVED`` (the API records these two as the owner), ``SPEND_CAPPED`` and ``SPEND_CLEARED``.
- The definitions ``EGRESS_ALLOWLIST_V3``, ``MODEL_TABLE_V3``, ``MODEL_TABLE_V4`` and ``API_PRICES_V1`` (frozen here,
  checked against ``app.agents.provider_definitions``).

Downgrade refuses once any owner pick, cap, reading, priced call or call of another provider exists, or a runtime
profile names the new definitions; otherwise it removes all of it.
"""

import hashlib
import json

from alembic import op

revision = "0029_agent_providers"
down_revision = "0028_leaner_trader"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
PROVIDERS = ("CODEX_CLI", "CLAUDE_CLI", "ANTHROPIC_API", "OPENAI_API")
APIS = ("ANTHROPIC_API", "OPENAI_API")
SOURCES = ("CODEX_APP_SERVER", "CLAUDE_CLI_EVENTS", "API_HEADERS")
KINDS = ("EGRESS_ALLOWLIST", "MODEL_TABLE", "API_PRICES")
DEFINITION_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "FEATURE_REGISTRY", "TEMPLATES", "BUDGETS",
                    "EGRESS_ALLOWLIST", "PROMPT", "SOURCE_VERSION", "RESEARCH_ENVELOPE", "RESEARCH_PROTOCOL",
                    "CANDIDATE_GRAMMAR", "MODEL_TABLE")
EVENT_KINDS = ("REQUEST_APPLIED", "REQUEST_REJECTED", "STATE_CHANGED", "DISABLED_BY_OWNER", "EPOCH_INCREMENTED",
               "DISCOVERY_RECORDED", "PROFILE_DRAFTED", "AUTH_REQUIRED", "AUTH_RESTORED", "QUOTA_BLOCKED",
               "QUOTA_CLEARED", "CAPABILITY_LATCHED", "CAPABILITY_VERIFIED", "PROFILE_DRIFT", "WORKER_STARTED",
               "WORKFLOW_EXPIRED", "PROFILE_IN_FORCE")
NEW_EVENTS = ("PROVIDER_REQUESTED", "PROVIDER_IN_FORCE", "PROVIDER_REFUSED", "CREDENTIAL_SAVED", "CREDENTIAL_REMOVED",
              "SPEND_CAPPED", "SPEND_CLEARED")

# (id, kind, version, status, canonical JSON, SHA-256) from ``python -m app.agents.provider_definitions``; a test
# checks they match the code.
SEED_LINES = r"""
["EGRESS_ALLOWLIST_V3", "EGRESS_ALLOWLIST", 3, "CODE_OWNED", "{\"id\":\"EGRESS_ALLOWLIST_V3\",\"kind\":\"EGRESS_ALLOWLIST\",\"listeners\":{\"ANTHROPIC_API\":{\"hosts\":[\"api.anthropic.com\"],\"listen\":3130},\"CLAUDE_CLI\":{\"hosts\":[\"api.anthropic.com\"],\"listen\":3129},\"CODEX_CLI\":{\"hosts\":[\"auth.openai.com\",\"chatgpt.com\"],\"listen\":3128},\"OPENAI_API\":{\"hosts\":[\"api.openai.com\"],\"listen\":3131}},\"port\":443,\"refuse\":[\"IP_LITERALS\",\"PRIVATE\",\"LOOPBACK\",\"LINK_LOCAL\",\"METADATA\",\"HOST_GATEWAY\",\"NON_GLOBAL\"],\"source\":\"ExecPlan 0049 section 5.1\",\"status\":\"CODE_OWNED\",\"version\":3}", "867de75a4b8d9056a26236bb111538f29dc62cc2025ef707e0584db43b1763cd"]
["MODEL_TABLE_V3", "MODEL_TABLE", 3, "CODE_OWNED", "{\"id\":\"MODEL_TABLE_V3\",\"kind\":\"MODEL_TABLE\",\"roles\":{\"ANALYST\":[[\"claude-sonnet-5-5\",\"medium\"]],\"COORDINATOR\":[[\"claude-sonnet-5-5\",\"medium\"]],\"EVALUATOR\":[[\"claude-sonnet-5-5\",\"medium\"]],\"RESEARCHER\":[[\"claude-sonnet-5-5\",\"medium\"]]},\"rule\":\"PER_ROLE_THE_FIRST_PAIR_WHOSE_MODEL_THE_PROVIDER'S_MODEL_LIST_NAMES_THE_AGENTS_CHECK_PROVES_IT_ANSWERS\",\"source\":\"ExecPlan 0049 section 5.1\",\"status\":\"CODE_OWNED\",\"version\":3}", "3d22f533d4911ba0d3292ef5f9c0e04965838102c49aef33029f734d7db59a75"]
["MODEL_TABLE_V4", "MODEL_TABLE", 4, "CODE_OWNED", "{\"id\":\"MODEL_TABLE_V4\",\"kind\":\"MODEL_TABLE\",\"roles\":{\"ANALYST\":[[\"gpt-6.1-sol\",\"medium\"]],\"COORDINATOR\":[[\"gpt-6.1-sol\",\"medium\"]],\"EVALUATOR\":[[\"gpt-6.1-sol\",\"high\"]],\"RESEARCHER\":[[\"gpt-6.1-sol\",\"medium\"]]},\"rule\":\"PER_ROLE_THE_FIRST_PAIR_WHOSE_MODEL_THE_PROVIDER'S_MODEL_LIST_NAMES_THE_AGENTS_CHECK_PROVES_IT_ANSWERS\",\"source\":\"ExecPlan 0049 section 5.1\",\"status\":\"CODE_OWNED\",\"version\":4}", "4beb0404ab432a331f18791f7d320d13797b6b9651a2f1b825a4594842b0a598"]
["API_PRICES_V1", "API_PRICES", 1, "CODE_OWNED", "{\"id\":\"API_PRICES_V1\",\"kind\":\"API_PRICES\",\"models\":{\"claude-sonnet-5-5\":{\"cache_write\":\"2.50\",\"cached_input\":\"0.20\",\"input\":\"2.00\",\"output\":\"10.00\",\"page\":\"https://platform.claude.com/docs/en/about-claude/pricing\",\"provider\":\"ANTHROPIC_API\"},\"gpt-6.1-sol\":{\"cache_write\":\"2.00\",\"cached_input\":\"0.10\",\"input\":\"2.00\",\"output\":\"10.00\",\"page\":\"https://developers.openai.com/api/docs/pricing\",\"provider\":\"OPENAI_API\"}},\"observed_on\":\"2026-10-31\",\"source\":\"ExecPlan 0049 section 5.5\",\"status\":\"CODE_OWNED\",\"unit\":\"USD_PER_MILLION_TOKENS\",\"version\":1}", "e754c34d612c4cb029e886addf95d4b713e05b9e6f2a639da880fff4fc3aa261"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    """The frozen documents, each checked against its own hash."""
    rows = []
    for line in SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KINDS:
            raise RuntimeError("frozen provider definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0007's actor guard (search path fixed later), which here also lets the API record the owner's saved or removed
# credential (the event names the provider and the key's last four characters, never the key). Downgrade restores it.
ACTOR_GUARD = """
CREATE OR REPLACE FUNCTION asl_agent_actor_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF TG_TABLE_NAME = 'agent_runtime_requests' THEN
                IF NEW.actor = 'OWNER' AND current_user = 'asl_api' AND NEW.kind <> 'ACTIVATE' THEN RETURN NEW; END IF;
            ELSIF TG_TABLE_NAME = 'agent_runtime_events' THEN
                IF NEW.actor = 'OWNER' AND current_user = 'asl_api'
                        AND NEW.kind IN {owner_events} THEN RETURN NEW; END IF;
                IF NEW.actor = 'SYSTEM' AND current_user = 'asl_agent' THEN RETURN NEW; END IF;
            ELSIF TG_TABLE_NAME = 'agent_runtime_profiles' THEN
                IF NEW.source = 'OWNER' AND current_user = 'asl_api' THEN RETURN NEW; END IF;
                IF NEW.source = 'DISCOVERY' AND current_user = 'asl_agent' THEN RETURN NEW; END IF;
            END IF;
            RAISE EXCEPTION '% row is not permitted for %', TG_TABLE_NAME, current_user;
        END $$;
"""
OWNER_EVENTS = ("DISABLED_BY_OWNER", "EPOCH_INCREMENTED")
OWNER_EVENTS_0029 = (*OWNER_EVENTS, "CREDENTIAL_SAVED", "CREDENTIAL_REMOVED")


def _guard(owner_events) -> str:
    return ACTOR_GUARD.replace("{path}", SEARCH_PATH).replace("{owner_events}", _quoted(owner_events))


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    providers, apis = _quoted(PROVIDERS), _quoted(APIS)
    op.execute(f"""
        CREATE TABLE agent_provider_requests (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            provider varchar(16) NOT NULL CHECK (provider IN {providers}),
            actor varchar(8) NOT NULL CHECK (actor = 'OWNER'),
            expected_version bigint NOT NULL CHECK (expected_version >= 0),
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{{64}}$'),
            correlation_id varchar(80) NOT NULL,
            at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE agent_spend_caps (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            provider varchar(16) NOT NULL CHECK (provider IN {apis}),
            cap_usd numeric(12,2) NOT NULL CHECK (cap_usd > 0 AND cap_usd <= 1000),
            actor varchar(8) NOT NULL CHECK (actor = 'OWNER'),
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{{64}}$'),
            correlation_id varchar(80) NOT NULL,
            at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_spend_caps_newest ON agent_spend_caps (provider, id DESC);
        CREATE TABLE agent_usage_readings (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            provider varchar(16) NOT NULL CHECK (provider IN {providers}),
            source varchar(24) NOT NULL CHECK (source IN {_quoted(SOURCES)}),
            ok boolean NOT NULL,
            call_key varchar(80),
            document jsonb NOT NULL CHECK (octet_length(document::text) <= 16384),
            read_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_usage_readings_newest ON agent_usage_readings (provider, id DESC);
        ALTER TABLE agent_provider_calls ADD COLUMN runtime_provider varchar(16)
            CHECK (runtime_provider IS NULL OR runtime_provider IN {providers});
        ALTER TABLE agent_provider_outcomes ADD COLUMN cost_usd numeric(14,6) CHECK (cost_usd IS NULL OR cost_usd >= 0);
        CREATE INDEX agent_provider_calls_runtime ON agent_provider_calls (runtime_provider, created_at)
            WHERE runtime_provider IS NOT NULL;
    """)
    for table in ("agent_provider_requests", "agent_spend_caps", "agent_usage_readings"):
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    op.execute("ALTER TABLE agent_runtime_events DROP CONSTRAINT agent_runtime_events_kind_check, "
               f"ADD CONSTRAINT agent_runtime_events_kind_check CHECK (kind IN {_quoted((*EVENT_KINDS, *NEW_EVENTS))})")
    op.execute("ALTER TABLE agent_definitions DROP CONSTRAINT agent_definitions_kind_check, "
               f"ADD CONSTRAINT agent_definitions_kind_check CHECK (kind IN {_quoted((*DEFINITION_KINDS, 'API_PRICES'))})")
    # The worker reads the provider events every tick; they are few among many.
    op.execute(f"CREATE INDEX agent_events_provider ON agent_runtime_events (id DESC) WHERE kind IN {_quoted(NEW_EVENTS)}")
    op.execute(_guard(OWNER_EVENTS_0029))
    op.execute("GRANT SELECT ON agent_provider_requests, agent_spend_caps, agent_usage_readings TO asl_agent, asl_api")
    op.execute("GRANT INSERT ON agent_provider_requests, agent_spend_caps TO asl_api")
    op.execute("GRANT INSERT ON agent_usage_readings TO asl_agent")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE agent_provider_requests_id_seq, agent_spend_caps_id_seq TO asl_api")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE agent_usage_readings_id_seq TO asl_agent")
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    ids = [row["id"] for row in seed_rows()]
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM agent_provider_requests) + (SELECT count(*) FROM agent_spend_caps) "
        "+ (SELECT count(*) FROM agent_usage_readings) "
        "+ (SELECT count(*) FROM agent_provider_outcomes WHERE cost_usd IS NOT NULL) "
        "+ (SELECT count(*) FROM agent_provider_calls WHERE runtime_provider IS DISTINCT FROM 'CODEX_CLI' "
        "   AND runtime_provider IS NOT NULL) "
        f"+ (SELECT count(*) FROM agent_runtime_events WHERE kind IN {_quoted(NEW_EVENTS)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{ids})"
    ).scalar_one()
    if held:
        raise RuntimeError("provider records exist; downgrade refused; fix forward")
    op.execute(_guard(OWNER_EVENTS))
    op.execute("DROP INDEX agent_events_provider")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("provider definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("ALTER TABLE agent_definitions DROP CONSTRAINT agent_definitions_kind_check, "
               f"ADD CONSTRAINT agent_definitions_kind_check CHECK (kind IN {_quoted(DEFINITION_KINDS)})")
    op.execute("ALTER TABLE agent_runtime_events DROP CONSTRAINT agent_runtime_events_kind_check, "
               f"ADD CONSTRAINT agent_runtime_events_kind_check CHECK (kind IN {_quoted(EVENT_KINDS)})")
    op.execute("""
        DROP INDEX agent_provider_calls_runtime;
        ALTER TABLE agent_provider_outcomes DROP COLUMN cost_usd;
        ALTER TABLE agent_provider_calls DROP COLUMN runtime_provider;
        DROP TABLE agent_usage_readings;
        DROP TABLE agent_spend_caps;
        DROP TABLE agent_provider_requests;
    """)
