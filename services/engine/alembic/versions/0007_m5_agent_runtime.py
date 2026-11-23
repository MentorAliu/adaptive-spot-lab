"""M5 agent runtime: definitions, profiles, approvals, runtime control, workflows and records.

Revision ID: 0007_m5_agent_runtime
Revises: 0006_m4_fixed_pilot

Additive only (ExecPlan 0020 section 7). Every statement creates a new object: tables, views,
functions, triggers, the ``agent_read`` schema and the NOLOGIN role ``asl_agent``. Nothing here
alters, grants on, revokes on, indexes, triggers or references by foreign key any M1-M4 table,
so a live pilot's workers never wait behind this migration; ``tests/test_m5_schema.py`` checks the
statements. The ``agent_read`` views read market tables with the view owner's rights and add no
index; they exclude evidence pins and raw payloads.

The downgrade is guarded: it refuses while any non-seed agent row exists, then drops only agent
objects and the ``asl_agent`` role. It exists for the pre-M5-B rollback only.
"""

import json
import os

from psycopg import sql

from alembic import op

revision = "0007_m5_agent_runtime"
down_revision = "0006_m4_fixed_pilot"
branch_labels = None
depends_on = None

# (id, kind, version, status, canonical JSON, SHA-256) from app.agents.definitions.seed_rows()
SEED_LINES = r"""
["AGENT_STEP_SCHEMA_V1", "AGENT_STEP_SCHEMA", 1, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V1\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"assessment\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"expiry_hours\":{\"type\":\"integer\"},\"hypotheses\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"statement\",\"cites\",\"invalidation\"],\"type\":\"object\"},\"type\":\"array\"},\"missing_evidence\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"observations\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"kind\":{\"enum\":[\"OBSERVATION\",\"CALCULATION\"],\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"kind\",\"statement\",\"cites\"],\"type\":\"object\"},\"type\":\"array\"},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"type\":\"array\"},\"uncertainty\":{\"additionalProperties\":false,\"properties\":{\"level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"reasons\":{\"type\":\"string\"}},\"required\":[\"level\",\"reasons\"],\"type\":\"object\"}},\"required\":[\"symbols\",\"summary\",\"observations\",\"hypotheses\",\"uncertainty\",\"missing_evidence\",\"expiry_hours\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"review\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiencies\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"review_type\":{\"enum\":[\"ASSESSMENT_REVIEW\"],\"type\":\"string\"},\"supported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"target_artifact_id\":{\"type\":\"string\"},\"target_sha256\":{\"type\":\"string\"},\"unsupported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"verdict\":{\"enum\":[\"ACCEPTABLE\",\"NEEDS_EVIDENCE\",\"REJECT\"],\"type\":\"string\"}},\"required\":[\"review_type\",\"target_artifact_id\",\"target_sha256\",\"verdict\",\"supported_claims\",\"unsupported_claims\",\"deficiencies\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"assessment\",\"review\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v1\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"artifact_id\":{\"type\":[\"string\",\"null\"]},\"as_of\":{\"type\":[\"string\",\"null\"]},\"feature_ids\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"symbol\":{\"type\":[\"string\",\"null\"]},\"view\":{\"enum\":[\"MARKET\",\"PORTFOLIO\",\"ACCOUNT\",null],\"type\":[\"string\",\"null\"]},\"window_hours\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"view\",\"as_of\",\"symbol\",\"feature_ids\",\"window_hours\",\"artifact_id\"],\"type\":\"object\"},\"purpose\":{\"type\":\"string\"},\"tool_name\":{\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v1\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M5 tool catalog v1 and ExecPlan 0020 section 5\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":1}", "965c096d1c6851968d721d58ebd60d8a5df2859aa76d4c2cf425e56c87732467"]
["TOOL_CATALOG_V1", "TOOL_CATALOG", 1, "CODE_OWNED", "{\"absent_tools\":[\"search_evidence\",\"request_source_refresh\",\"register_candidate\",\"request_experiment\",\"read_experiment\",\"request_review\",\"draft_trade_intent\",\"submit_trade_intent\",\"request_entry_pause\",\"request_promotion\"],\"id\":\"TOOL_CATALOG_V1\",\"kind\":\"TOOL_CATALOG\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M5 tool catalog v1 and ExecPlan 0020 section 5\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"view\",\"as_of\"],\"description\":\"Market-only least-data view at the job cutoff: the latest quote per symbol with its age and quality, the latest finalized 1h candle, instrument status and feed health, with the snapshot's as-of time and publication watermark. view must be MARKET; as_of, when given, must not be after the job cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"get_snapshot\"},{\"arguments\":[\"symbol\",\"feature_ids\",\"window_hours\",\"as_of\"],\"description\":\"Registered features over finalized 1h candles for BTCUSDT or SOLUSDT, evaluated at the last finalized bar at or before as_of (default: the job cutoff). feature_ids: 1-6 registered IDs; window_hours: 1-168 (OHLCV_1H_V1: at most 72). Returns exact decimal strings with inputs, warm-up and quality.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_market_features\"},{\"arguments\":[\"artifact_id\"],\"description\":\"Reads one artifact of this workflow or its review target. Any other ID is refused.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_artifact\"},{\"arguments\":[],\"description\":\"ANALYST only, through FINISH with finish.assessment. Records an immutable MarketAssessment.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_assessment\"},{\"arguments\":[],\"description\":\"EVALUATOR only, through FINISH with finish.review. Records an immutable EvaluationReview bound to the exact target hash.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_review\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":1}", "781ca68670e8606c2ac400d9b44b5313c157f15235ec6caeb57550057f831242"]
["ROLE_GRANTS_V1", "ROLE_GRANTS", 1, "CODE_OWNED", "{\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"record_assessment\"],\"COORDINATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\"],\"EVALUATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"record_review\"],\"RESEARCHER\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\"]},\"id\":\"ROLE_GRANTS_V1\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M5 tool catalog v1 and ExecPlan 0020 section 5\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"MARKET_ASSESSMENT_V1\"],\"COORDINATOR\":[],\"EVALUATOR\":[\"ASSESSMENT_REVIEW_V1\"],\"RESEARCHER\":[]},\"version\":1}", "05ca5d4fba4105c40c1c749bad3e2d91ca7bb2d56bf7463ee4cdcfc6761324f2"]
["FEATURE_REGISTRY_V1", "FEATURE_REGISTRY", 1, "CODE_OWNED", "{\"evaluation_bar\":\"LAST_FINALIZED_BAR_WITH_CLOSE_AT_OR_BEFORE_AS_OF\",\"features\":[{\"id\":\"OHLCV_1H_V1\",\"max_window_hours\":72,\"output\":\"BARS_IN_WINDOW\",\"warmup_bars\":0},{\"id\":\"RETURN_1H_V1\",\"max_window_hours\":168,\"output\":\"CLOSE_T_OVER_CLOSE_T_MINUS_1_MINUS_1\",\"warmup_bars\":1},{\"id\":\"RETURN_24H_V1\",\"max_window_hours\":168,\"output\":\"CLOSE_T_OVER_CLOSE_T_MINUS_24_MINUS_1\",\"warmup_bars\":24},{\"id\":\"EMA20_1H_V1\",\"max_window_hours\":168,\"output\":\"EMA_CLOSE_20_SEED_SMA_LATEST_AND_WINDOW_START\",\"warmup_bars\":20},{\"id\":\"EMA50_1H_V1\",\"max_window_hours\":168,\"output\":\"EMA_CLOSE_50_SEED_SMA_LATEST_AND_WINDOW_START\",\"warmup_bars\":50},{\"id\":\"ATR14_1H_V1\",\"max_window_hours\":168,\"output\":\"WILDER_ATR_14_LATEST_AND_WINDOW_START\",\"warmup_bars\":15}],\"id\":\"FEATURE_REGISTRY_V1\",\"indicators\":\"app.strategies.indicators (exact Decimal EMA seeded by SMA; Wilder ATR)\",\"input\":\"FINALIZED_1H_CANDLES_VIA_AGENT_READ_VIEWS_AT_OR_BELOW_THE_JOB_WATERMARK_AND_CUTOFF\",\"kind\":\"FEATURE_REGISTRY\",\"quality\":{\"INSUFFICIENT\":\"GAP_OR_SHORT_HISTORY_VALUE_NULL\",\"VALID\":\"RUN_COVERS_WARMUP_AND_WINDOW\"},\"rounding\":{\"prices_and_indicators\":\"8_DECIMALS_HALF_EVEN\",\"returns\":\"10_DECIMALS_HALF_EVEN\"},\"run\":\"CONTIGUOUS_FINALIZED_BARS_ENDING_AT_THE_EVALUATION_BAR_AT_MOST_WINDOW_PLUS_200\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M5 tool catalog v1 and ExecPlan 0020 section 5\",\"status\":\"CODE_OWNED\",\"version\":1}", "e4e2dcc8d9dd0bed62f1daf39700766eb633039182f5623dd95905d02791d82c"]
["TEMPLATES_V1", "TEMPLATES", 1, "CODE_OWNED", "{\"delegation\":\"NONE_MODEL_CHOSEN; FIXED_CHILD_ONLY\",\"id\":\"TEMPLATES_V1\",\"kind\":\"TEMPLATES\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M5 tool catalog v1 and ExecPlan 0020 section 5\",\"status\":\"CODE_OWNED\",\"templates\":{\"ASSESSMENT_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"budget\":\"DRAWS_ON_PARENT\",\"parent\":\"MARKET_ASSESSMENT_V1\",\"prompt\":\"EVALUATOR_PROMPT_M5_V1\",\"purpose\":\"REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_PARENT_FINISH\"},\"MARKET_ASSESSMENT_V1\":{\"artifact\":\"MARKET_ASSESSMENT\",\"child\":\"ASSESSMENT_REVIEW_V1\",\"parameters\":{\"horizon_hours\":{\"maximum\":72,\"minimum\":1},\"symbols\":{\"items\":[\"BTCUSDT\",\"SOLUSDT\"],\"max_items\":2,\"min_items\":1,\"unique\":true}},\"prompt\":\"ANALYST_PROMPT_M5_V1\",\"purpose\":\"ASSESSMENT\",\"role\":\"ANALYST\",\"started_by\":\"OWNER\"}},\"version\":1}", "640cec83562393317910990f64774ae52de44de28c9a62c653992a90c7735fa6"]
["BUDGETS_V1", "BUDGETS", 1, "PROPOSED", "{\"daily_parent_workflows\":12,\"final_output_max_bytes\":16384,\"handoff_depth\":1,\"id\":\"BUDGETS_V1\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"max_model_steps\":8,\"max_tool_calls\":6,\"probe_call_budget\":40,\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"source\":\"ExecPlan 0020 section 5.5\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"tool_result_max_bytes\":16384,\"version\":1,\"workflow_deadline_seconds\":1200}", "ea20f474d1a36dca3da72e8ed0880510820efd46793cae61356272fd9f39780e"]
["EGRESS_ALLOWLIST_V1", "EGRESS_ALLOWLIST", 1, "PROPOSED", "{\"hosts\":[\"auth.openai.com\",\"chatgpt.com\"],\"id\":\"EGRESS_ALLOWLIST_V1\",\"kind\":\"EGRESS_ALLOWLIST\",\"port\":443,\"refuse\":[\"IP_LITERALS\",\"PRIVATE\",\"LOOPBACK\",\"LINK_LOCAL\",\"METADATA\",\"HOST_GATEWAY\",\"NON_GLOBAL\"],\"source\":\"ExecPlan 0020 section 7 trust boundaries\",\"status\":\"PROPOSED\",\"version\":1}", "64542800be8ad21d4b3bea841ebd5b74827a213c917418c63e7aed5e2b5574e7"]
["ANALYST_PROMPT_M5_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"ANALYST_PROMPT_M5_V1\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"8870ac9ec993fa651aaeab28320f640f042f453e86074afefcc8177b2a6b6e6c\",\"source\":\"services/agent-runner/prompts/m5/analyst.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "6d975dd713e0696bca0ef948045ed7654b59637ef26c2a044d7468bb1cfc7f0d"]
["EVALUATOR_PROMPT_M5_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"EVALUATOR_PROMPT_M5_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"c07c12d29ad1a8e35703443c74ee5c63b6099fbc29ba1ca5db111cfe823d906c\",\"source\":\"services/agent-runner/prompts/m5/evaluator.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "b3ac776c5b8bb9dd41967d8cdc98fd8049e5331d98ba2a61ce438511000a8529"]
"""

WORKFLOW_STATES = ("QUEUED", "RUNNING", "WAITING_TOOL", "WAITING_REVIEW", "SUCCEEDED", "ABSTAINED",
                   "REJECTED_OUTPUT", "EXPIRED", "AUTH_REQUIRED", "QUOTA_BLOCKED", "FAILED", "CANCELED")
TERMINAL_STATES = ("SUCCEEDED", "ABSTAINED", "REJECTED_OUTPUT", "EXPIRED", "AUTH_REQUIRED", "QUOTA_BLOCKED",
                   "FAILED", "CANCELED")
STEP_OUTCOMES = ("TOOL_REQUEST", "FINISH", "REJECTED_OUTPUT", "OUTCOME_UNKNOWN", "TIMEOUT", "CANCELED",
                 "REVOKED", "AUTH_REQUIRED", "QUOTA_BLOCKED", "PROVIDER_UNAVAILABLE", "BUDGET_EXHAUSTED",
                 "CAPABILITY_VIOLATION", "EXPIRED", "LATE")
REQUEST_KINDS = ("ACTIVATE", "ENABLE", "DISABLE", "PROBE", "CANCEL_WORKFLOW")
RUNTIME_EVENTS = ("REQUEST_APPLIED", "REQUEST_REJECTED", "STATE_CHANGED", "DISABLED_BY_OWNER", "EPOCH_INCREMENTED",
                  "DISCOVERY_RECORDED", "PROFILE_DRAFTED", "AUTH_REQUIRED", "AUTH_RESTORED", "QUOTA_BLOCKED",
                  "QUOTA_CLEARED", "CAPABILITY_LATCHED", "CAPABILITY_VERIFIED", "PROFILE_DRIFT", "WORKER_STARTED",
                  "WORKFLOW_EXPIRED")
APPEND_ONLY = ("agent_definitions", "agent_runtime_profiles", "agent_approvals", "agent_capability_verifications",
               "agent_runtime_requests", "agent_runtime_events", "agent_capability_grants", "agent_provider_calls",
               "agent_provider_outcomes", "agent_tool_calls", "agent_tool_results", "agent_artifacts",
               "agent_blobs", "agent_runtime_observations", "agent_probe_results")
AGENT_TABLES = ("agent_definitions", "agent_runtime_observations", "agent_runtime_profiles", "agent_approvals",
                "agent_runtime_state", "agent_permission_epoch", "agent_probe_runs",
                "agent_capability_verifications", "agent_workflows", "agent_runtime_requests",
                "agent_runtime_events", "agent_orchestrator_lease", "agent_capability_grants", "agent_blobs",
                "agent_steps", "agent_provider_calls", "agent_provider_outcomes", "agent_provider_details",
                "agent_tool_calls", "agent_tool_results", "agent_artifacts", "agent_probe_results")
VIEWS = ("agent_read.market_watermark", "agent_read.market_quotes", "agent_read.market_candles",
         "agent_read.market_candle_confirmations", "agent_read.market_instruments", "agent_read.market_feeds")


def _quoted(values: tuple[str, ...]) -> str:
    return "(" + ",".join(f"'{value}'" for value in values) + ")"


def upgrade() -> None:
    # A DDL statement waiting in the lock queue would stall the pilot workers' 1 s lock timeouts; this
    # migration touches only new objects, and the deploy retries a bounded number of times.
    op.execute("SET LOCAL lock_timeout = '200ms'")
    op.execute(f"""
        CREATE TABLE agent_definitions (
            id varchar(64) PRIMARY KEY,
            kind varchar(32) NOT NULL CHECK (kind IN ('AGENT_STEP_SCHEMA','TOOL_CATALOG','ROLE_GRANTS',
                'FEATURE_REGISTRY','TEMPLATES','BUDGETS','EGRESS_ALLOWLIST','PROMPT')),
            version integer NOT NULL CHECK (version >= 1),
            status varchar(16) NOT NULL CHECK (status IN ('CODE_OWNED','PROPOSED')),
            definition jsonb NOT NULL,
            canonical text NOT NULL,
            sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_runtime_observations (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            kind varchar(16) NOT NULL CHECK (kind IN ('DISCOVERY','RUNNER_STATUS','USAGE','INCIDENT','QUOTA')),
            binary_digest varchar(80),
            config_hash varchar(64),
            account_id_hash varchar(64),
            inventory_hash varchar(64),
            detail jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_observations_kind ON agent_runtime_observations(kind, seq);

        CREATE TABLE agent_runtime_profiles (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            sha256 varchar(64) NOT NULL UNIQUE CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            canonical text NOT NULL,
            profile jsonb NOT NULL,
            source varchar(16) NOT NULL CHECK (source IN ('DISCOVERY','OWNER')),
            observation_id uuid NOT NULL REFERENCES agent_runtime_observations(id),
            idempotency_key varchar(80) UNIQUE,
            request_hash varchar(64),
            session_id uuid,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT agent_profile_owner_key CHECK (source = 'DISCOVERY'
                OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL))
        );

        CREATE TABLE agent_approvals (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            target_kind varchar(24) NOT NULL CHECK (target_kind IN ('RUNTIME_PROFILE')),
            target_id varchar(64) NOT NULL,
            target_sha256 varchar(64) NOT NULL CHECK (target_sha256 ~ '^[0-9a-f]{{64}}$'),
            action varchar(8) NOT NULL CHECK (action IN ('APPROVE','REJECT','REVOKE')),
            owner_id smallint NOT NULL DEFAULT 1 CHECK (owner_id = 1),
            -- The owner session is recorded without a foreign key: adding one would lock owner_sessions.
            session_id uuid NOT NULL,
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL,
            expected_version bigint NOT NULL CHECK (expected_version >= 0),
            correlation_id varchar(80) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_approvals_target ON agent_approvals(target_kind, target_id, target_sha256, seq);

        CREATE TABLE agent_probe_runs (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            profile_id uuid NOT NULL REFERENCES agent_runtime_profiles(id),
            profile_sha256 varchar(64) NOT NULL,
            state varchar(12) NOT NULL CHECK (state IN ('QUEUED','RUNNING','PASSED','FAILED','CANCELED')),
            calls_budget integer NOT NULL CHECK (calls_budget BETWEEN 1 AND 200),
            calls_used integer NOT NULL DEFAULT 0 CHECK (calls_used >= 0 AND calls_used <= calls_budget),
            version bigint NOT NULL DEFAULT 0,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            finished_at timestamptz
        );

        CREATE TABLE agent_capability_verifications (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            profile_id uuid NOT NULL REFERENCES agent_runtime_profiles(id),
            profile_sha256 varchar(64) NOT NULL,
            binary_digest varchar(80) NOT NULL,
            config_hash varchar(64) NOT NULL,
            account_id_hash varchar(64) NOT NULL,
            inventory_hash varchar(64) NOT NULL,
            status varchar(8) NOT NULL CHECK (status IN ('VERIFIED','FAILED')),
            probe_run_id uuid NOT NULL REFERENCES agent_probe_runs(id),
            detail jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_runtime_state (
            id smallint PRIMARY KEY CHECK (id = 1),
            state varchar(16) NOT NULL CHECK (state IN ('DISABLED','LOGIN_REQUIRED','PROBE_ONLY','ENABLED')),
            auth_state varchar(12) NOT NULL DEFAULT 'UNKNOWN'
                CHECK (auth_state IN ('UNKNOWN','PRESENT','MISSING','REFUSED')),
            quota_state varchar(12) NOT NULL DEFAULT 'UNKNOWN' CHECK (quota_state IN ('UNKNOWN','OK','BLOCKED')),
            capability_latched boolean NOT NULL DEFAULT false,
            approved_profile_id uuid REFERENCES agent_runtime_profiles(id),
            approved_profile_sha256 varchar(64),
            verification_id uuid REFERENCES agent_capability_verifications(id),
            first_left_disabled_at timestamptz,
            reason varchar(80),
            version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            worker_id uuid,
            worker_heartbeat_at timestamptz,
            runner jsonb,
            runner_checked_at timestamptz
        );
        INSERT INTO agent_runtime_state (id, state, reason) VALUES (1, 'DISABLED', 'INITIAL');

        CREATE TABLE agent_permission_epoch (
            id smallint PRIMARY KEY CHECK (id = 1),
            epoch bigint NOT NULL DEFAULT 0 CHECK (epoch >= 0),
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            -- An epoch change is a key update, so it conflicts with every FOR KEY SHARE commit check.
            CONSTRAINT agent_permission_epoch_key UNIQUE (id, epoch)
        );
        INSERT INTO agent_permission_epoch (id) VALUES (1);

        CREATE TABLE agent_orchestrator_lease (
            id smallint PRIMARY KEY CHECK (id = 1),
            owner_id uuid,
            epoch bigint NOT NULL DEFAULT 0 CHECK (epoch >= 0),
            expires_at timestamptz,
            CONSTRAINT agent_lease_authority UNIQUE (id, owner_id, epoch)
        );
        INSERT INTO agent_orchestrator_lease (id) VALUES (1);

        CREATE TABLE agent_workflows (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            parent_id uuid REFERENCES agent_workflows(id),
            template_id varchar(40) NOT NULL,
            role varchar(16) NOT NULL CHECK (role IN ('ANALYST','EVALUATOR','COORDINATOR','RESEARCHER')),
            purpose varchar(12) NOT NULL CHECK (purpose IN ('ASSESSMENT','REVIEW','PROBE')),
            mode varchar(16) NOT NULL CHECK (mode IN ('FORWARD_PAPER','OFFLINE_TEST')),
            provider varchar(12) NOT NULL CHECK (provider IN ('CODEX','RECORDED')),
            created_by varchar(16) NOT NULL CHECK (created_by IN ('OWNER','ORCHESTRATOR','PROBE_RUN','FIXTURE')),
            state varchar(16) NOT NULL CHECK (state IN {_quoted(WORKFLOW_STATES)}),
            version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
            params jsonb NOT NULL,
            idempotency_key varchar(80) UNIQUE,
            request_hash varchar(64),
            session_id uuid,
            correlation_id varchar(80),
            probe_run_id uuid REFERENCES agent_probe_runs(id),
            probe_id varchar(8),
            permission_epoch bigint,
            profile_id uuid REFERENCES agent_runtime_profiles(id),
            profile_sha256 varchar(64),
            cutoff jsonb,
            deadline_at timestamptz,
            queued_until timestamptz NOT NULL,
            review_status varchar(12) CHECK (review_status IS NULL OR review_status IN
                ('PENDING','COMPLETED','UNAVAILABLE','CANCELED')),
            usage jsonb NOT NULL DEFAULT '{{}}',
            terminal_reason varchar(48),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            started_at timestamptz,
            finished_at timestamptz,
            CONSTRAINT agent_workflow_owner_key CHECK (created_by <> 'OWNER'
                OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL)),
            CONSTRAINT agent_workflow_child CHECK ((purpose = 'REVIEW') = (parent_id IS NOT NULL)),
            CONSTRAINT agent_workflow_recorded CHECK (provider <> 'RECORDED' OR mode = 'OFFLINE_TEST'),
            CONSTRAINT agent_workflow_fixture CHECK (created_by <> 'FIXTURE' OR mode = 'OFFLINE_TEST')
        );
        CREATE INDEX agent_workflows_open ON agent_workflows(state, seq)
            WHERE state IN ('QUEUED','RUNNING','WAITING_TOOL','WAITING_REVIEW');
        CREATE INDEX agent_workflows_parent ON agent_workflows(parent_id) WHERE parent_id IS NOT NULL;
        CREATE INDEX agent_workflows_created ON agent_workflows(created_at);

        CREATE TABLE agent_runtime_requests (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            kind varchar(16) NOT NULL CHECK (kind IN {_quoted(REQUEST_KINDS)}),
            actor varchar(8) NOT NULL CHECK (actor IN ('OWNER','ADMIN')),
            target varchar(16) CHECK (target IS NULL OR target IN ('ENABLED','PROBE_ONLY')),
            profile_sha256 varchar(64),
            workflow_id uuid REFERENCES agent_workflows(id),
            expected_version bigint CHECK (expected_version IS NULL OR expected_version >= 0),
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL,
            session_id uuid,
            correlation_id varchar(80) NOT NULL,
            detail jsonb NOT NULL DEFAULT '{{}}',
            at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT agent_request_owner_session CHECK (actor <> 'OWNER' OR session_id IS NOT NULL),
            CONSTRAINT agent_request_cancel CHECK ((kind = 'CANCEL_WORKFLOW') = (workflow_id IS NOT NULL))
        );
        CREATE INDEX agent_requests_workflow ON agent_runtime_requests(workflow_id) WHERE workflow_id IS NOT NULL;

        CREATE TABLE agent_runtime_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            kind varchar(24) NOT NULL CHECK (kind IN {_quoted(RUNTIME_EVENTS)}),
            actor varchar(8) NOT NULL CHECK (actor IN ('SYSTEM','OWNER')),
            request_id bigint REFERENCES agent_runtime_requests(id),
            detail jsonb NOT NULL DEFAULT '{{}}',
            at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        -- Each request is applied or rejected by the SYSTEM at most once.
        CREATE UNIQUE INDEX agent_events_applied_once ON agent_runtime_events(request_id)
            WHERE request_id IS NOT NULL AND kind IN ('REQUEST_APPLIED','REQUEST_REJECTED');
        CREATE INDEX agent_events_time ON agent_runtime_events(id DESC);

        CREATE TABLE agent_capability_grants (
            id uuid PRIMARY KEY,
            workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id),
            role varchar(16) NOT NULL,
            tools jsonb NOT NULL,
            grant_sha256 varchar(64) NOT NULL,
            catalog_sha256 varchar(64) NOT NULL,
            grants_sha256 varchar(64) NOT NULL,
            permission_epoch bigint NOT NULL,
            profile_sha256 varchar(64),
            expires_at timestamptz NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_blobs (
            sha256 varchar(64) PRIMARY KEY CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            content text NOT NULL,
            bytes integer NOT NULL CHECK (bytes BETWEEN 0 AND 262144),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_steps (
            id uuid PRIMARY KEY,
            workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
            step_no smallint NOT NULL CHECK (step_no BETWEEN 1 AND 64),
            attempt smallint NOT NULL DEFAULT 1 CHECK (attempt BETWEEN 1 AND 4),
            state varchar(12) NOT NULL CHECK (state IN ('PENDING','SENT','COMPLETED')),
            outcome varchar(24) CHECK (outcome IS NULL OR outcome IN {_quoted(STEP_OUTCOMES)}),
            input_hash varchar(64) NOT NULL,
            prompt_sha256 varchar(64) NOT NULL REFERENCES agent_blobs(sha256),
            output_sha256 varchar(64) REFERENCES agent_blobs(sha256),
            error_code varchar(48),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            completed_at timestamptz,
            CONSTRAINT agent_step_once UNIQUE (workflow_id, step_no, attempt),
            CONSTRAINT agent_step_terminal CHECK ((state = 'COMPLETED') = (outcome IS NOT NULL))
        );

        CREATE TABLE agent_provider_calls (
            id uuid PRIMARY KEY,
            step_id uuid NOT NULL UNIQUE REFERENCES agent_steps(id),
            call_key varchar(80) NOT NULL UNIQUE,
            provider varchar(12) NOT NULL CHECK (provider IN ('CODEX','RECORDED')),
            variant varchar(24) NOT NULL,
            cli_version varchar(40),
            binary_digest varchar(80),
            requested_model varchar(80),
            reasoning_effort varchar(16),
            argv_sha256 varchar(64),
            config_hash varchar(64),
            prompt_sha256 varchar(64) NOT NULL,
            schema_sha256 varchar(64) NOT NULL,
            profile_sha256 varchar(64),
            permission_epoch bigint NOT NULL,
            deadline_at timestamptz NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_provider_outcomes (
            id uuid PRIMARY KEY,
            call_id uuid NOT NULL UNIQUE REFERENCES agent_provider_calls(id),
            status varchar(16) NOT NULL CHECK (status IN ('COMPLETED','FAILED','TIMEOUT','KILLED',
                'OUTCOME_UNKNOWN','CANCELED')),
            late boolean NOT NULL,
            reported_model varchar(80),
            usage jsonb NOT NULL DEFAULT '{{}}',
            timings jsonb NOT NULL DEFAULT '{{}}',
            item_counts jsonb NOT NULL DEFAULT '{{}}',
            violations jsonb NOT NULL DEFAULT '[]',
            exit_code integer,
            error_class varchar(40),
            final_sha256 varchar(64) REFERENCES agent_blobs(sha256),
            auth_copyback varchar(16),
            received_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        -- Bounded, redacted stderr and JSONL summaries; the only agent rows retention may delete (90 days).
        CREATE TABLE agent_provider_details (
            call_id uuid PRIMARY KEY REFERENCES agent_provider_calls(id),
            stderr_summary text CHECK (stderr_summary IS NULL OR octet_length(stderr_summary) <= 262144),
            jsonl_summary jsonb,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE agent_tool_calls (
            id uuid PRIMARY KEY,
            workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
            step_id uuid NOT NULL UNIQUE REFERENCES agent_steps(id),
            tool_name varchar(64) NOT NULL,
            arguments jsonb NOT NULL,
            arguments_sha256 varchar(64) NOT NULL,
            decision varchar(12) NOT NULL CHECK (decision IN ('AUTHORIZED','DENIED')),
            decision_code varchar(40),
            operation_key varchar(160) NOT NULL UNIQUE,
            permission_epoch bigint NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT agent_tool_denial_code CHECK ((decision = 'DENIED') = (decision_code IS NOT NULL))
        );
        CREATE INDEX agent_tool_calls_workflow ON agent_tool_calls(workflow_id, created_at);

        CREATE TABLE agent_tool_results (
            id uuid PRIMARY KEY,
            tool_call_id uuid NOT NULL UNIQUE REFERENCES agent_tool_calls(id),
            workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
            status varchar(12) NOT NULL CHECK (status IN ('SUCCEEDED','REJECTED','UNAVAILABLE')),
            result_ref varchar(40) NOT NULL UNIQUE,
            envelope jsonb NOT NULL,
            output_sha256 varchar(64) NOT NULL,
            bytes integer NOT NULL CHECK (bytes BETWEEN 0 AND 65536),
            elapsed_ms integer NOT NULL CHECK (elapsed_ms >= 0),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_tool_results_workflow ON agent_tool_results(workflow_id);

        CREATE TABLE agent_artifacts (
            id uuid PRIMARY KEY,
            workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
            kind varchar(20) NOT NULL CHECK (kind IN ('MARKET_ASSESSMENT','EVALUATION_REVIEW')),
            operation_key varchar(160) NOT NULL UNIQUE,
            canonical text NOT NULL,
            sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            document jsonb NOT NULL,
            cites jsonb NOT NULL,
            target_artifact_id uuid REFERENCES agent_artifacts(id),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX agent_artifacts_workflow ON agent_artifacts(workflow_id);

        CREATE TABLE agent_probe_results (
            id uuid PRIMARY KEY,
            probe_run_id uuid NOT NULL REFERENCES agent_probe_runs(id),
            probe_id varchar(8) NOT NULL CHECK (probe_id ~ '^CP-[0-9]{{2}}$'),
            workflow_id uuid REFERENCES agent_workflows(id),
            passed boolean NOT NULL,
            detail jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT agent_probe_once UNIQUE (probe_run_id, probe_id)
        );
    """)

    op.execute(f"""
        CREATE FUNCTION asl_agent_workflow_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE pair text;
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF TG_OP = 'INSERT' THEN
                IF NEW.mode = 'OFFLINE_TEST' AND current_database() NOT LIKE 'asl\\_m1\\_%' THEN
                    RAISE EXCEPTION 'OFFLINE_TEST agent workflows require a disposable asl_m1_ database'; END IF;
                IF NEW.version <> 0 THEN RAISE EXCEPTION 'agent workflows start at version 0'; END IF;
                IF current_user = 'asl_api' AND NEW.created_by = 'OWNER' AND NEW.state = 'QUEUED'
                        AND NEW.parent_id IS NULL AND NEW.purpose = 'ASSESSMENT' AND NEW.role = 'ANALYST'
                        AND NEW.provider = 'CODEX' AND NEW.template_id = 'MARKET_ASSESSMENT_V1'
                        AND NEW.permission_epoch IS NULL AND NEW.cutoff IS NULL AND NEW.started_at IS NULL THEN
                    RETURN NEW; END IF;
                IF current_user = 'asl_agent' AND NEW.created_by <> 'OWNER' AND NEW.state IN ('QUEUED','RUNNING') THEN
                    RETURN NEW; END IF;
                RAISE EXCEPTION 'agent workflow insert is not permitted for %', current_user;
            END IF;
            pair := OLD.state || '>' || NEW.state;
            IF NEW.id <> OLD.id OR NEW.seq <> OLD.seq OR NEW.parent_id IS DISTINCT FROM OLD.parent_id
                    OR NEW.template_id <> OLD.template_id OR NEW.role <> OLD.role OR NEW.purpose <> OLD.purpose
                    OR NEW.mode <> OLD.mode OR NEW.provider <> OLD.provider OR NEW.created_by <> OLD.created_by
                    OR NEW.params <> OLD.params OR NEW.idempotency_key IS DISTINCT FROM OLD.idempotency_key
                    OR NEW.request_hash IS DISTINCT FROM OLD.request_hash OR NEW.created_at <> OLD.created_at
                    OR NEW.queued_until <> OLD.queued_until THEN
                RAISE EXCEPTION 'agent workflow identity is immutable'; END IF;
            IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'only the agent worker changes workflows'; END IF;
            IF OLD.state IN {_quoted(TERMINAL_STATES)} THEN RAISE EXCEPTION 'terminal agent workflow cannot change'; END IF;
            IF NEW.version <> OLD.version + 1 THEN RAISE EXCEPTION 'agent workflow version must increase by one'; END IF;
            IF OLD.permission_epoch IS NOT NULL AND NEW.permission_epoch IS DISTINCT FROM OLD.permission_epoch THEN
                RAISE EXCEPTION 'agent workflow epoch binding is immutable'; END IF;
            IF OLD.cutoff IS NOT NULL AND NEW.cutoff IS DISTINCT FROM OLD.cutoff THEN
                RAISE EXCEPTION 'agent workflow cutoff is immutable'; END IF;
            IF NEW.state = OLD.state THEN RETURN NEW; END IF;
            IF pair IN ('QUEUED>RUNNING','RUNNING>WAITING_TOOL','WAITING_TOOL>RUNNING','RUNNING>WAITING_REVIEW')
                    OR (OLD.state = 'QUEUED' AND NEW.state IN ('EXPIRED','CANCELED','FAILED'))
                    OR (OLD.state IN ('RUNNING','WAITING_TOOL') AND NEW.state IN {_quoted(TERMINAL_STATES)})
                    OR (OLD.state = 'WAITING_REVIEW' AND NEW.state IN ('SUCCEEDED','CANCELED','FAILED','EXPIRED')) THEN
                RETURN NEW; END IF;
            RAISE EXCEPTION 'agent workflow transition % is not allowed', pair;
        END $$;
        CREATE TRIGGER agent_workflows_guard BEFORE INSERT OR UPDATE ON agent_workflows
            FOR EACH ROW EXECUTE FUNCTION asl_agent_workflow_guard();
        CREATE TRIGGER agent_workflows_no_delete BEFORE DELETE ON agent_workflows
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_agent_step_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF OLD.state = 'COMPLETED' THEN RAISE EXCEPTION 'a completed agent step is immutable'; END IF;
            IF NEW.id <> OLD.id OR NEW.workflow_id <> OLD.workflow_id OR NEW.step_no <> OLD.step_no
                    OR NEW.attempt <> OLD.attempt OR NEW.input_hash <> OLD.input_hash
                    OR NEW.prompt_sha256 <> OLD.prompt_sha256 OR NEW.created_at <> OLD.created_at THEN
                RAISE EXCEPTION 'agent step identity is immutable'; END IF;
            IF NOT ((OLD.state = 'PENDING' AND NEW.state IN ('SENT','COMPLETED'))
                    OR (OLD.state = 'SENT' AND NEW.state = 'COMPLETED')) THEN
                RAISE EXCEPTION 'agent step transition %>% is not allowed', OLD.state, NEW.state; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER agent_steps_guard BEFORE UPDATE ON agent_steps
            FOR EACH ROW EXECUTE FUNCTION asl_agent_step_guard();
        CREATE TRIGGER agent_steps_no_delete BEFORE DELETE ON agent_steps
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_agent_runtime_state_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF NEW.state <> OLD.state OR NEW.approved_profile_id IS DISTINCT FROM OLD.approved_profile_id
                    OR NEW.approved_profile_sha256 IS DISTINCT FROM OLD.approved_profile_sha256
                    OR NEW.verification_id IS DISTINCT FROM OLD.verification_id
                    OR NEW.capability_latched <> OLD.capability_latched OR NEW.auth_state <> OLD.auth_state
                    OR NEW.quota_state <> OLD.quota_state THEN
                IF NEW.version <> OLD.version + 1 THEN
                    RAISE EXCEPTION 'runtime state version must increase by one'; END IF;
            ELSIF NEW.version <> OLD.version THEN
                RAISE EXCEPTION 'runtime state version changes only with the state'; END IF;
            IF OLD.first_left_disabled_at IS NOT NULL
                    AND NEW.first_left_disabled_at IS DISTINCT FROM OLD.first_left_disabled_at THEN
                RAISE EXCEPTION 'first_left_disabled_at is immutable once set'; END IF;
            IF current_user = 'asl_api' THEN
                -- The owner's Disable only: the state becomes DISABLED and nothing else changes.
                IF NEW.state <> 'DISABLED' OR NEW.approved_profile_id IS DISTINCT FROM OLD.approved_profile_id
                        OR NEW.approved_profile_sha256 IS DISTINCT FROM OLD.approved_profile_sha256
                        OR NEW.verification_id IS DISTINCT FROM OLD.verification_id
                        OR NEW.capability_latched <> OLD.capability_latched OR NEW.auth_state <> OLD.auth_state
                        OR NEW.quota_state <> OLD.quota_state
                        OR NEW.worker_id IS DISTINCT FROM OLD.worker_id
                        OR NEW.worker_heartbeat_at IS DISTINCT FROM OLD.worker_heartbeat_at
                        OR NEW.runner IS DISTINCT FROM OLD.runner THEN
                    RAISE EXCEPTION 'the API may only disable the agent runtime'; END IF;
                RETURN NEW;
            END IF;
            IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'runtime state is written by the agent worker'; END IF;
            IF NEW.state = 'ENABLED' AND NOT EXISTS (
                    SELECT 1 FROM agent_capability_verifications v WHERE v.id = NEW.verification_id
                    AND v.status = 'VERIFIED' AND v.profile_sha256 = NEW.approved_profile_sha256
                    AND v.profile_id = NEW.approved_profile_id) THEN
                RAISE EXCEPTION 'ENABLED requires a VERIFIED capability record for the approved profile'; END IF;
            IF NEW.state = 'ENABLED' AND NEW.capability_latched THEN
                RAISE EXCEPTION 'a latched capability cannot be ENABLED'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER agent_runtime_state_guard BEFORE UPDATE ON agent_runtime_state
            FOR EACH ROW EXECUTE FUNCTION asl_agent_runtime_state_guard();
        CREATE TRIGGER agent_runtime_state_no_delete BEFORE INSERT OR DELETE ON agent_runtime_state
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_agent_epoch_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF NEW.id <> OLD.id OR NEW.epoch <> OLD.epoch + 1 THEN
                RAISE EXCEPTION 'the permission epoch only increases by one'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER agent_permission_epoch_guard BEFORE UPDATE ON agent_permission_epoch
            FOR EACH ROW EXECUTE FUNCTION asl_agent_epoch_guard();
        CREATE TRIGGER agent_permission_epoch_no_delete BEFORE INSERT OR DELETE ON agent_permission_epoch
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_agent_actor_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF TG_TABLE_NAME = 'agent_runtime_requests' THEN
                IF NEW.actor = 'OWNER' AND current_user = 'asl_api' AND NEW.kind <> 'ACTIVATE' THEN RETURN NEW; END IF;
            ELSIF TG_TABLE_NAME = 'agent_runtime_events' THEN
                IF NEW.actor = 'OWNER' AND current_user = 'asl_api'
                        AND NEW.kind IN ('DISABLED_BY_OWNER','EPOCH_INCREMENTED') THEN RETURN NEW; END IF;
                IF NEW.actor = 'SYSTEM' AND current_user = 'asl_agent' THEN RETURN NEW; END IF;
            ELSIF TG_TABLE_NAME = 'agent_runtime_profiles' THEN
                IF NEW.source = 'OWNER' AND current_user = 'asl_api' THEN RETURN NEW; END IF;
                IF NEW.source = 'DISCOVERY' AND current_user = 'asl_agent' THEN RETURN NEW; END IF;
            END IF;
            RAISE EXCEPTION '% row is not permitted for %', TG_TABLE_NAME, current_user;
        END $$;
        CREATE TRIGGER agent_runtime_requests_actor BEFORE INSERT ON agent_runtime_requests
            FOR EACH ROW EXECUTE FUNCTION asl_agent_actor_guard();
        CREATE TRIGGER agent_runtime_events_actor BEFORE INSERT ON agent_runtime_events
            FOR EACH ROW EXECUTE FUNCTION asl_agent_actor_guard();
        CREATE TRIGGER agent_runtime_profiles_actor BEFORE INSERT ON agent_runtime_profiles
            FOR EACH ROW EXECUTE FUNCTION asl_agent_actor_guard();

        CREATE FUNCTION asl_agent_probe_run_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF OLD.state IN ('PASSED','FAILED','CANCELED') THEN RAISE EXCEPTION 'a finished probe run is immutable'; END IF;
            IF NEW.id <> OLD.id OR NEW.profile_id <> OLD.profile_id OR NEW.profile_sha256 <> OLD.profile_sha256
                    OR NEW.calls_budget <> OLD.calls_budget OR NEW.calls_used < OLD.calls_used
                    OR NEW.version <> OLD.version + 1 THEN
                RAISE EXCEPTION 'probe run identity, budget and usage are monotonic'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER agent_probe_runs_guard BEFORE UPDATE ON agent_probe_runs
            FOR EACH ROW EXECUTE FUNCTION asl_agent_probe_run_guard();
        CREATE TRIGGER agent_probe_runs_no_delete BEFORE DELETE ON agent_probe_runs
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_agent_detail_retention() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'UPDATE' THEN RAISE EXCEPTION 'provider details are immutable'; END IF;
            IF asl_is_superuser() THEN RETURN OLD; END IF;
            IF OLD.created_at > clock_timestamp() - interval '90 days' THEN
                RAISE EXCEPTION 'provider details are kept for 90 days'; END IF;
            RETURN OLD;
        END $$;
        CREATE TRIGGER agent_provider_details_retention BEFORE UPDATE OR DELETE ON agent_provider_details
            FOR EACH ROW EXECUTE FUNCTION asl_agent_detail_retention();
    """)
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")

    # Least-data market views. The migration role owns them, so asl_agent needs no grant on any market
    # table; evidence pins and raw payloads are not reachable through them.
    op.execute("""
        CREATE SCHEMA agent_read;
        CREATE VIEW agent_read.market_watermark WITH (security_barrier = true) AS
            SELECT COALESCE(max(sequence), 0)::bigint AS watermark FROM market_publications;
        CREATE VIEW agent_read.market_quotes WITH (security_barrier = true) AS
            SELECT o.id AS observation_id, o.symbol, o.acquisition, o.quality, o.source_event_at, o.received_at,
                   o.bid_price, o.bid_quantity, o.ask_price, o.ask_quantity, o.collection_id, o.instrument_id,
                   p.sequence, p.available_at
            FROM market_observations o JOIN market_publications p ON p.observation_id = o.id
            WHERE o.kind = 'QUOTE';
        CREATE VIEW agent_read.market_candles WITH (security_barrier = true) AS
            SELECT o.id AS observation_id, o.symbol, o.acquisition, o.quality, o.source_event_at, o.received_at,
                   o.open_ms, o.close_ms, o.open_price, o.high_price, o.low_price, o.close_price, o.volume,
                   o.is_final, o.collection_id, o.instrument_id, p.sequence, p.available_at
            FROM market_observations o JOIN market_publications p ON p.observation_id = o.id
            WHERE o.kind = 'CANDLE';
        CREATE VIEW agent_read.market_candle_confirmations WITH (security_barrier = true) AS
            SELECT c.id AS confirmation_id, c.observation_id, c.symbol, c.open_ms, c.through_sequence,
                   p.sequence, p.available_at
            FROM market_candle_confirmations c JOIN market_publications p ON p.confirmation_id = c.id;
        CREATE VIEW agent_read.market_instruments WITH (security_barrier = true) AS
            SELECT o.id AS observation_id, o.symbol, o.acquisition, o.quality, o.received_at,
                   o.instrument->>'status' AS status, o.instrument->>'baseAsset' AS base_asset,
                   o.instrument->>'quoteAsset' AS quote_asset,
                   (o.instrument->>'isSpotTradingAllowed')::boolean AS spot_allowed,
                   o.instrument->'permissions' AS permissions, o.instrument->'permissionSets' AS permission_sets,
                   p.sequence, p.available_at
            FROM market_observations o JOIN market_publications p ON p.observation_id = o.id
            WHERE o.kind = 'INSTRUMENT';
        CREATE VIEW agent_read.market_feeds WITH (security_barrier = true) AS
            SELECT f.symbol, f.status, f.last_message_at, f.last_quote_at, f.last_final_open_ms,
                   f.last_clock_check_at, f.clock_offset_ms, f.clock_uncertainty_ms, f.last_instrument_check_at,
                   f.collection_id, f.instrument_id, l.epoch AS lease_epoch,
                   l.expires_at > clock_timestamp() AS worker_lease_valid,
                   (w.sampled_at > clock_timestamp() - interval '6 seconds'
                    AND w.lease_epoch = l.epoch AND w.owner_id = l.owner_id
                    AND NOT w.overloaded AND (w.queue_count = 0 OR
                    w.oldest_age_ms + extract(epoch FROM clock_timestamp() - w.sampled_at) * 1000 <= 1000))
                    AS telemetry_valid,
                   clock_timestamp() AS observed_at
            FROM market_feed_state f CROSS JOIN market_lease l CROSS JOIN market_worker_state w;
    """)

    bind = op.get_bind()
    for line in SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, digest = json.loads(line)
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, %(sha)s)",
            {"id": identity, "kind": kind, "version": version, "status": status,
             "definition": canonical, "canonical": canonical, "sha": digest},
        )
    bind.exec_driver_sql("""
        DO $$ BEGIN
            IF (SELECT count(*) FROM agent_definitions) = 0 OR EXISTS (SELECT 1 FROM agent_definitions
                    WHERE encode(digest(convert_to(canonical, 'UTF8'), 'sha256'), 'hex') <> sha256) THEN
                RAISE EXCEPTION 'seeded agent definition hash mismatch';
            END IF;
        END $$
    """)

    raw = bind.connection.driver_connection
    database_name = os.environ.get("ASL_DB_NAME", "asl")
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_agent'")
        if cursor.fetchone() is None:
            # NOLOGIN until the owner-instructed M5-B step sets a SCRAM verifier (app.agents.identity).
            cursor.execute("CREATE ROLE asl_agent NOLOGIN")
        cursor.execute("ALTER ROLE asl_agent SET statement_timeout = '2s'")
        cursor.execute("ALTER ROLE asl_agent SET lock_timeout = '1s'")
        cursor.execute("ALTER ROLE asl_agent SET idle_in_transaction_session_timeout = '5s'")
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO asl_agent").format(sql.Identifier(database_name)))
    tables = ", ".join(AGENT_TABLES)
    op.execute("GRANT USAGE ON SCHEMA public TO asl_agent")
    op.execute("GRANT USAGE ON SCHEMA agent_read TO asl_agent")
    op.execute(f"GRANT SELECT ON {', '.join(VIEWS)} TO asl_agent")
    op.execute(f"GRANT SELECT ON {tables} TO asl_agent, asl_api")
    op.execute(
        "GRANT INSERT ON agent_runtime_observations, agent_runtime_profiles, agent_probe_runs, "
        "agent_capability_verifications, agent_workflows, agent_runtime_events, agent_capability_grants, "
        "agent_blobs, agent_steps, agent_provider_calls, agent_provider_outcomes, agent_provider_details, "
        "agent_tool_calls, agent_tool_results, agent_artifacts, agent_probe_results TO asl_agent")
    op.execute("GRANT UPDATE (state, auth_state, quota_state, capability_latched, approved_profile_id, "
               "approved_profile_sha256, verification_id, first_left_disabled_at, reason, version, updated_at, "
               "worker_id, worker_heartbeat_at, runner, runner_checked_at) ON agent_runtime_state TO asl_agent")
    op.execute("GRANT UPDATE (epoch, updated_at) ON agent_permission_epoch TO asl_agent, asl_api")
    op.execute("GRANT UPDATE (owner_id, epoch, expires_at) ON agent_orchestrator_lease TO asl_agent")
    op.execute("GRANT UPDATE (state, version, permission_epoch, profile_id, profile_sha256, cutoff, deadline_at, "
               "review_status, usage, terminal_reason, started_at, finished_at) ON agent_workflows TO asl_agent")
    op.execute("GRANT UPDATE (state, outcome, output_sha256, error_code, completed_at) ON agent_steps TO asl_agent")
    op.execute("GRANT UPDATE (state, calls_used, version, finished_at) ON agent_probe_runs TO asl_agent")
    op.execute("GRANT DELETE ON agent_provider_details TO asl_agent")
    op.execute("GRANT INSERT ON agent_approvals, agent_runtime_profiles, agent_runtime_requests, agent_workflows, "
               "agent_runtime_events TO asl_api")
    op.execute("GRANT UPDATE (state, reason, version, updated_at) ON agent_runtime_state TO asl_api")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE agent_runtime_observations_seq_seq, agent_runtime_profiles_seq_seq, "
               "agent_probe_runs_seq_seq, agent_capability_verifications_seq_seq, agent_workflows_seq_seq, "
               "agent_runtime_events_id_seq TO asl_agent")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE agent_approvals_seq_seq, agent_runtime_profiles_seq_seq, "
               "agent_runtime_requests_id_seq, agent_workflows_seq_seq, agent_runtime_events_id_seq TO asl_api")


def downgrade() -> None:
    """Guarded pre-M5-B rollback: refuses while any non-seed agent row exists."""
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    populated = bind.exec_driver_sql("""
        SELECT (SELECT count(*) FROM agent_runtime_observations) + (SELECT count(*) FROM agent_runtime_profiles)
             + (SELECT count(*) FROM agent_approvals) + (SELECT count(*) FROM agent_workflows)
             + (SELECT count(*) FROM agent_runtime_requests) + (SELECT count(*) FROM agent_runtime_events)
             + (SELECT count(*) FROM agent_probe_runs) + (SELECT count(*) FROM agent_blobs)
             + (SELECT count(*) FROM agent_permission_epoch WHERE epoch <> 0)
             + (SELECT count(*) FROM agent_runtime_state WHERE state <> 'DISABLED' OR version <> 0
                OR worker_heartbeat_at IS NOT NULL)
    """).scalar_one()
    if populated:
        raise RuntimeError("agent records exist; the M5 downgrade is refused (fix forward instead)")
    op.execute(f"DROP VIEW {', '.join(VIEWS)}")
    op.execute("DROP SCHEMA agent_read")
    op.execute(f"DROP TABLE {', '.join(reversed(AGENT_TABLES))}")
    op.execute("DROP FUNCTION asl_agent_workflow_guard(), asl_agent_step_guard(), asl_agent_runtime_state_guard(), "
               "asl_agent_epoch_guard(), asl_agent_actor_guard(), asl_agent_probe_run_guard(), "
               "asl_agent_detail_retention()")
    raw = bind.connection.driver_connection
    database_name = os.environ.get("ASL_DB_NAME", "asl")
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_agent'")
        if cursor.fetchone() is not None:
            cursor.execute(sql.SQL("REVOKE CONNECT ON DATABASE {} FROM asl_agent").format(
                sql.Identifier(database_name)))
            cursor.execute("DROP OWNED BY asl_agent")
            cursor.execute("DROP ROLE asl_agent")
