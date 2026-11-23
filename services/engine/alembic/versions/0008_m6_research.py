"""M6 isolated research catalog, source evidence and queued tool completions.

Revision ID: 0008_m6_research
Revises: 0007_m5_agent_runtime

No alteration, grant, foreign key, index or trigger targets an M1-M4 table. Only M5
agent checks/guards are expanded. New identities are NOLOGIN; seeds grant no approval.
Downgrade refuses owner/history rows, removes M6 seeds inside the migration transaction,
and restores the M5 checks and workflow guard. Use bounded deployment retries (200ms locks).
"""

import hashlib
import json
import os
from copy import deepcopy

from psycopg import sql

from alembic import op

revision = "0008_m6_research"
down_revision = "0007_m5_agent_runtime"
branch_labels = None
depends_on = None

# Frozen independent copy, not an import from changeable runtime code.
SEED_DOCUMENTS = json.loads(r'''
[
  {
    "id": "CANDIDATE_GRAMMAR_V1",
    "kind": "CANDIDATE_GRAMMAR",
    "version": 1,
    "status": "CODE_OWNED",
    "source": "ExecPlan 0023 sections 5.3 and 5.5",
    "shape": "FLAT_NON_RECURSIVE",
    "symbols": [
      "BTCUSDT",
      "SOLUSDT"
    ],
    "timeframe": "1h",
    "operators": [
      "CLOSE",
      "EMA",
      "SMA",
      "ATR",
      "RETURN",
      "HIGHEST",
      "LOWEST",
      "ZSCORE"
    ],
    "comparisons": [
      "GT",
      "LT",
      "CROSS_ABOVE",
      "CROSS_BELOW"
    ],
    "entry": "OR_OF_AND_GROUPS",
    "exit": "EXISTING_MANDATE_TEMPLATE_WITH_OPTIONAL_SIGNAL",
    "normalization": "SORT_GROUPS_AND_CONDITIONS_NORMALIZE_DECIMALS",
    "financial_authority": "NONE"
  },
  {
    "id": "RESEARCH_PROTOCOL_V1",
    "kind": "RESEARCH_PROTOCOL",
    "version": 1,
    "status": "CODE_OWNED",
    "source": "ExecPlan 0023 section 5.5",
    "partitions": {
      "DEV": "0.6",
      "VALIDATION": "0.2",
      "HOLDOUT": "0.2"
    },
    "gap": "MAXIMUM_HOLD_BETWEEN_PARTITIONS",
    "screening": {
      "partitions": [
        "DEV",
        "VALIDATION"
      ],
      "cost_scenarios": [
        "H1"
      ]
    },
    "full_test": {
      "partitions": [
        "DEV",
        "VALIDATION",
        "HOLDOUT"
      ],
      "cost_scenarios": [
        "H1",
        "H2_STRESS"
      ]
    },
    "evaluation_protocol": "EVALUATION_PROTOCOL_V1",
    "minimum_paired_hours": 168,
    "minimum_closed_positions": 10,
    "outcome_when_short": "INSUFFICIENT_SAMPLE",
    "holdout_evaluations_per_hypothesis": 1,
    "failed_holdout_retries": 1,
    "repeated_testing_correction": "NONE",
    "performance_acceptance_threshold": null,
    "contamination": "HISTORICAL_MODEL_MAY_KNOW_LATER_EVENTS",
    "fidelity": "SAMPLED_L1_TICKER_REDUCED_REPLAY_RULE"
  },
  {
    "id": "RESEARCH_ENVELOPE_V1",
    "kind": "RESEARCH_ENVELOPE",
    "version": 1,
    "status": "PROPOSED",
    "source": "ExecPlan 0023 section 5.5; measured B0 sizing 2026-10-03",
    "protocol_id": "RESEARCH_PROTOCOL_V1",
    "grammar_id": "CANDIDATE_GRAMMAR_V1",
    "protocol_sha256": null,
    "grammar_sha256": null,
    "modes": [
      "RECORDED_QUOTE_BACKTEST",
      "DEFERRED_REPLAY_SHADOW"
    ],
    "max_dataset_days": 21,
    "lookback": {
      "min": 2,
      "max": 200
    },
    "atr_period": {
      "min": 5,
      "max": 50
    },
    "warmup_bars_max": 300,
    "stop_multiple": {
      "min": "1.0",
      "max": "5.0",
      "step": "0.25"
    },
    "max_hold_hours": {
      "min": 6,
      "max": 168
    },
    "constants": {
      "min": "-10",
      "max": "10",
      "decimal_places_max": 4
    },
    "complexity": {
      "max_groups": 3,
      "max_conditions_per_group": 4,
      "max_distinct_features": 8
    },
    "trials": {
      "max_candidates_per_hypothesis": 12,
      "max_jobs_per_utc_day": 12,
      "max_queued_jobs": 4,
      "max_running_jobs": 1,
      "max_job_wall_seconds": 3600
    },
    "holdout": {
      "evaluations_per_hypothesis": 1,
      "failed_retries": 1,
      "roles": [
        "EVALUATOR",
        "COORDINATOR",
        "OWNER"
      ]
    },
    "shadows": {
      "max_active": 4,
      "max_days": 21,
      "advance": "DAILY",
      "minimum_paired_hours": 168,
      "minimum_closed_positions": 10
    },
    "stores": {
      "max_days": 49,
      "max_allocated_bytes": 21474836480,
      "min_available_bytes": 42949672960
    },
    "resources": {
      "research-postgres": {
        "cpus": "1.0",
        "memory_bytes": 1073741824,
        "pids": 128
      },
      "research-runner": {
        "cpus": "1.0",
        "memory_bytes": 805306368,
        "pids": 128
      },
      "research-bridge": {
        "cpus": "0.5",
        "memory_bytes": 268435456,
        "pids": 64
      },
      "source-fetcher": {
        "cpus": "0.5",
        "memory_bytes": 268435456,
        "pids": 64
      }
    },
    "quiet_window_utc": {
      "start": "HH:58:00",
      "end": "HH:07:00"
    },
    "owner_approval": "EXACT_HASH_REQUIRED"
  },
  {
    "id": "RELEASES_BITCOIN_V1",
    "kind": "SOURCE_VERSION",
    "version": 1,
    "status": "PROPOSED",
    "source": "ExecPlan 0023 section 5.7; B0 rights review 2026-10-03; B5 limits 2026-10-04",
    "name": "Bitcoin Core",
    "host": "api.github.com",
    "scheme": "https",
    "port": 443,
    "method": "GET",
    "redirects": "REFUSED",
    "path_template": "/repos/bitcoin/bitcoin/releases",
    "typed_filters": {
      "per_page": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100
      },
      "page": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      }
    },
    "poll_filters": {
      "per_page": 10,
      "page": 1
    },
    "parser": "GITHUB_RELEASES_V1",
    "authentication": "NONE",
    "response": {
      "content_type": "application/json",
      "max_bytes": 2097152,
      "deadline_seconds": 20
    },
    "extract_max_bytes": 16384,
    "symbols": [
      "BTCUSDT"
    ],
    "rate_limit_per_ip_per_hour": 60,
    "rate_limit_policy": "GITHUB_REST_V1",
    "budget": {
      "requests_per_hour": 6,
      "poll_interval_seconds": 3600,
      "refresh_interval_seconds": 600,
      "failure_backoff_seconds": 300,
      "unstated_limit_backoff_seconds": 3600
    },
    "trigger": {
      "family": "SOURCE_REVISION",
      "cooldown_seconds": 21600
    },
    "timestamps": {
      "publication": "published_at",
      "update": "updated_at_IF_RELEASE_SUPPLIES_IT",
      "receipt": "LOCAL_RECEIPT",
      "availability": "LOCAL_VALIDATED_AVAILABILITY"
    },
    "retention": {
      "basis": "GITHUB_TERMS_D6_REPOSITORY_LICENSE",
      "license": "MIT",
      "review": "docs/INTEGRATION_EVIDENCE.md M6 B0",
      "review_date": "2026-10-03",
      "terms": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
      "license_url": "https://github.com/bitcoin/bitcoin/blob/master/COPYING",
      "scope": "REPOSITORY_RELEASE_TEXT_ONLY",
      "attribution": "RETAIN_COPYRIGHT_LICENSE_AND_APPLICABLE_NOTICE_IDENTIFY_SHORTENED_EXTRACT",
      "expiry": null,
      "excluded": [
        "LINKED_ASSETS",
        "SEPARATELY_LICENSED_THIRD_PARTY_TEXT",
        "LINKED_DESTINATIONS"
      ]
    },
    "owner_approval": "EXACT_HASH_REQUIRED"
  },
  {
    "id": "RELEASES_AGAVE_V1",
    "kind": "SOURCE_VERSION",
    "version": 1,
    "status": "PROPOSED",
    "source": "ExecPlan 0023 section 5.7; B0 rights review 2026-10-03; B5 limits 2026-10-04",
    "name": "Agave",
    "host": "api.github.com",
    "scheme": "https",
    "port": 443,
    "method": "GET",
    "redirects": "REFUSED",
    "path_template": "/repos/anza-xyz/agave/releases",
    "typed_filters": {
      "per_page": {
        "type": "integer",
        "minimum": 1,
        "maximum": 100
      },
      "page": {
        "type": "integer",
        "minimum": 1,
        "maximum": 10
      }
    },
    "poll_filters": {
      "per_page": 10,
      "page": 1
    },
    "parser": "GITHUB_RELEASES_V1",
    "authentication": "NONE",
    "response": {
      "content_type": "application/json",
      "max_bytes": 2097152,
      "deadline_seconds": 20
    },
    "extract_max_bytes": 16384,
    "symbols": [
      "SOLUSDT"
    ],
    "rate_limit_per_ip_per_hour": 60,
    "rate_limit_policy": "GITHUB_REST_V1",
    "budget": {
      "requests_per_hour": 6,
      "poll_interval_seconds": 3600,
      "refresh_interval_seconds": 600,
      "failure_backoff_seconds": 300,
      "unstated_limit_backoff_seconds": 3600
    },
    "trigger": {
      "family": "SOURCE_REVISION",
      "cooldown_seconds": 21600
    },
    "timestamps": {
      "publication": "published_at",
      "update": "updated_at_IF_RELEASE_SUPPLIES_IT",
      "receipt": "LOCAL_RECEIPT",
      "availability": "LOCAL_VALIDATED_AVAILABILITY"
    },
    "retention": {
      "basis": "GITHUB_TERMS_D6_REPOSITORY_LICENSE",
      "license": "Apache-2.0",
      "review": "docs/INTEGRATION_EVIDENCE.md M6 B0",
      "review_date": "2026-10-03",
      "terms": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
      "license_url": "https://github.com/anza-xyz/agave/blob/master/LICENSE",
      "scope": "REPOSITORY_RELEASE_TEXT_ONLY",
      "attribution": "RETAIN_COPYRIGHT_LICENSE_AND_APPLICABLE_NOTICE_IDENTIFY_SHORTENED_EXTRACT",
      "expiry": null,
      "excluded": [
        "LINKED_ASSETS",
        "SEPARATELY_LICENSED_THIRD_PARTY_TEXT",
        "LINKED_DESTINATIONS"
      ]
    },
    "owner_approval": "EXACT_HASH_REQUIRED"
  }
]
''')

# Agent definitions v2 (B6; ExecPlan 0023 section 5.8): schema, catalog, grants, templates, budgets and the
# four M6 prompts. (id, kind, version, status, canonical JSON, SHA-256) as printed by
# ``python -m app.agents.definitions_v2``; a frozen copy, compared with the code by a test. They are
# added beside the M5 rows, which stay. Seeding approves nothing: the runtime profile that binds
# these hashes is a new document the owner has not approved.
AGENT_SEED_LINES = r"""
["AGENT_STEP_SCHEMA_V2", "AGENT_STEP_SCHEMA", 2, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V2\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"assessment\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"expiry_hours\":{\"type\":\"integer\"},\"hypotheses\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"statement\",\"cites\",\"invalidation\"],\"type\":\"object\"},\"type\":\"array\"},\"missing_evidence\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"observations\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"kind\":{\"enum\":[\"OBSERVATION\",\"CALCULATION\"],\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"kind\",\"statement\",\"cites\"],\"type\":\"object\"},\"type\":\"array\"},\"research_question\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"type\":\"array\"},\"uncertainty\":{\"additionalProperties\":false,\"properties\":{\"level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"reasons\":{\"type\":\"string\"}},\"required\":[\"level\",\"reasons\"],\"type\":\"object\"}},\"required\":[\"symbols\",\"summary\",\"observations\",\"hypotheses\",\"uncertainty\",\"missing_evidence\",\"expiry_hours\",\"research_question\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"promotion\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_id\":{\"type\":\"string\"},\"candidate_sha256\":{\"type\":\"string\"},\"evidence_refs\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"rationale\":{\"type\":\"string\"}},\"required\":[\"candidate_id\",\"candidate_sha256\",\"evidence_refs\",\"rationale\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"research_proposal\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_ids\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"hypothesis_id\":{\"type\":\"string\"},\"limitations\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"nominated_candidate_id\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"}},\"required\":[\"hypothesis_id\",\"summary\",\"candidate_ids\",\"nominated_candidate_id\",\"cites\",\"limitations\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"review\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiencies\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiency_codes\":{\"items\":{\"enum\":[\"INSUFFICIENT_SAMPLE\",\"DATA_GAPS\",\"INTEGRITY_FAILURE\",\"COST_UNCERTAINTY\",\"HISTORICAL_CONTAMINATION\",\"MISSING_BASELINE\",\"INCOMPLETE_TEST_SET\",\"UNSUPPORTED_CLAIM\"],\"type\":\"string\"},\"type\":\"array\"},\"results\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"result_ref\":{\"type\":\"string\"},\"sha256\":{\"type\":\"string\"}},\"required\":[\"result_ref\",\"sha256\"],\"type\":\"object\"},\"type\":\"array\"},\"review_type\":{\"enum\":[\"ASSESSMENT_REVIEW\",\"CANDIDATE_REVIEW\"],\"type\":\"string\"},\"supported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"target_artifact_id\":{\"type\":\"string\"},\"target_sha256\":{\"type\":\"string\"},\"unsupported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"verdict\":{\"enum\":[\"ACCEPTABLE\",\"NEEDS_EVIDENCE\",\"REJECT\"],\"type\":\"string\"}},\"required\":[\"review_type\",\"target_artifact_id\",\"target_sha256\",\"verdict\",\"supported_claims\",\"unsupported_claims\",\"deficiencies\",\"cites\",\"results\",\"deficiency_codes\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"assessment\",\"review\",\"research_proposal\",\"promotion\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v2\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"artifact_id\":{\"type\":[\"string\",\"null\"]},\"as_of\":{\"type\":[\"string\",\"null\"]},\"candidate\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One flat CANDIDATE_GRAMMAR_V1 declaration. Operators, comparisons and domains are in the job context.\",\"properties\":{\"entry\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":\"array\"},\"exit\":{\"additionalProperties\":false,\"properties\":{\"atr_period\":{\"type\":\"integer\"},\"max_hold_hours\":{\"type\":\"integer\"},\"signal\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":[\"array\",\"null\"]},\"stop_multiple\":{\"type\":\"string\"}},\"required\":[\"atr_period\",\"stop_multiple\",\"max_hold_hours\",\"signal\"],\"type\":\"object\"},\"grammar_version\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"timeframe\":{\"type\":\"string\"},\"warmup_bars\":{\"type\":\"integer\"}},\"required\":[\"grammar_version\",\"symbols\",\"timeframe\",\"warmup_bars\",\"entry\",\"exit\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"candidate_id\":{\"type\":[\"string\",\"null\"]},\"dataset_id\":{\"type\":[\"string\",\"null\"]},\"experiment_id\":{\"type\":[\"string\",\"null\"]},\"feature_ids\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"filters\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"name\":{\"type\":\"string\"},\"value\":{\"type\":\"integer\"}},\"required\":[\"name\",\"value\"],\"type\":\"object\"},\"type\":[\"array\",\"null\"]},\"hypothesis\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"dataset_id\":{\"type\":\"string\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"dataset_id\",\"statement\",\"invalidation\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"hypothesis_id\":{\"type\":[\"string\",\"null\"]},\"limit\":{\"type\":[\"integer\",\"null\"]},\"query\":{\"type\":[\"string\",\"null\"]},\"search_scope\":{\"enum\":[\"SOURCES\",\"ARTIFACTS\",null],\"type\":[\"string\",\"null\"]},\"source_id\":{\"type\":[\"string\",\"null\"]},\"symbol\":{\"type\":[\"string\",\"null\"]},\"view\":{\"enum\":[\"MARKET\",\"PORTFOLIO\",\"ACCOUNT\",null],\"type\":[\"string\",\"null\"]},\"window_hours\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"view\",\"as_of\",\"symbol\",\"feature_ids\",\"window_hours\",\"artifact_id\",\"search_scope\",\"query\",\"source_id\",\"filters\",\"limit\",\"hypothesis_id\",\"hypothesis\",\"candidate\",\"candidate_id\",\"dataset_id\",\"experiment_id\"],\"type\":\"object\"},\"purpose\":{\"type\":\"string\"},\"tool_name\":{\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v2\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M6 tool catalog v2 and ExecPlan 0023 section 5.8\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":2}", "f08bdb2860bc5b8615663d649ac8b8b111cfdd367d7c4b9a9dc47c5fb013bcef"]
["TOOL_CATALOG_V2", "TOOL_CATALOG", 2, "CODE_OWNED", "{\"absent_tools\":[\"request_review\",\"draft_trade_intent\",\"submit_trade_intent\",\"request_entry_pause\"],\"id\":\"TOOL_CATALOG_V2\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M6 tool catalog v2 and ExecPlan 0023 section 5.8\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"view\",\"as_of\"],\"description\":\"Market-only least-data view at the job cutoff: the latest quote per symbol with its age and quality, the latest finalized 1h candle, instrument status and feed health, with the snapshot's as-of time and publication watermark. view must be MARKET; as_of, when given, must not be after the job cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"get_snapshot\"},{\"arguments\":[\"symbol\",\"feature_ids\",\"window_hours\",\"as_of\"],\"description\":\"Registered features over finalized 1h candles for BTCUSDT or SOLUSDT, evaluated at the last finalized bar at or before as_of (default: the job cutoff). feature_ids: 1-6 registered IDs; window_hours: 1-168 (OHLCV_1H_V1: at most 72). Returns exact decimal strings with inputs, warm-up and quality.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_market_features\"},{\"arguments\":[\"artifact_id\"],\"description\":\"Reads one typed artifact in this workflow's scope, or one evidence item that a result of this workflow or an artifact in its scope returned. Any other ID is refused. What a role may not see is withheld: a tuning role gets only the verdict and deficiency codes of a review that consulted holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_artifact\"},{\"arguments\":[\"search_scope\",\"query\",\"source_id\",\"symbol\",\"limit\"],\"description\":\"ANALYST and RESEARCHER. Plain-term search of approved evidence. search_scope SOURCES returns at most 10 items of approved sources that were available by the job cutoff; ARTIFACTS returns references to earlier typed artifacts. source_id and symbol narrow a SOURCES search. Each returned item can be cited by its ID. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"search_evidence\"},{\"arguments\":[\"source_id\",\"filters\"],\"description\":\"ANALYST and RESEARCHER. Queues one fetch of a registered, approved source by its ID, with that source's typed integer filters. Never a URL, host or path. Returns ACCEPTED with a request reference; the workflow then waits and resumes with one completion.\",\"effect\":\"QUEUE_SOURCE_REFRESH\",\"finish_only\":false,\"name\":\"request_source_refresh\"},{\"arguments\":[\"hypothesis\",\"hypothesis_id\",\"candidate\"],\"description\":\"RESEARCHER. Records this workflow's hypothesis (first call: hypothesis; later calls: hypothesis_id) and one declaration in CANDIDATE_GRAMMAR_V1 inside the approved envelope's domains. Returns the candidate ID and normalized hash, or the existing candidate. Registration tests nothing and grants nothing.\",\"effect\":\"RECORD_RESEARCH\",\"finish_only\":false,\"name\":\"register_candidate\"},{\"arguments\":[\"candidate_id\",\"dataset_id\"],\"description\":\"RESEARCHER. Queues the registered screening set (DEV and VALIDATION, cost scenario H1) for one of this workflow's candidates on its bound dataset. Returns ACCEPTED with an experiment reference; the workflow then waits and resumes with one completion. The holdout cannot be requested.\",\"effect\":\"QUEUE_RESEARCH_JOB\",\"finish_only\":false,\"name\":\"request_experiment\"},{\"arguments\":[\"experiment_id\"],\"description\":\"Reads one experiment or shadow by ID in the role's projection. A tuning role (ANALYST, RESEARCHER) reads screening results at or before its cutoff and never holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_experiment\"},{\"arguments\":[],\"description\":\"ANALYST only, through FINISH with finish.assessment. Records an immutable MarketAssessment; it may name one research question.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_assessment\"},{\"arguments\":[],\"description\":\"EVALUATOR only, through FINISH with finish.review. Records an immutable EvaluationReview bound to the exact target hash and, for a candidate review, to the exact result hashes.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_review\"},{\"arguments\":[],\"description\":\"RESEARCHER only, through FINISH with finish.research_proposal. Records an immutable ResearchProposal and may nominate one tested candidate for the fixed review.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_research_proposal\"},{\"arguments\":[],\"description\":\"COORDINATOR only, through FINISH with finish.promotion. Records a PENDING promotion request for the owner. Refused unless the candidate is EVIDENCE_READY. Nothing in this release approves one.\",\"effect\":\"QUEUE_OWNER_PROPOSAL\",\"finish_only\":true,\"name\":\"request_promotion\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":2}", "e8c0a0ec29db749352e79e97f5357bc0605dba2d61182a1b05a5ca7e12fce3e7"]
["ROLE_GRANTS_V2", "ROLE_GRANTS", 2, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\",\"QUEUE_SOURCE_REFRESH\",\"RECORD_RESEARCH\",\"QUEUE_RESEARCH_JOB\",\"QUEUE_OWNER_PROPOSAL\"],\"grants\":{\"ANALYST\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"search_evidence\",\"request_source_refresh\",\"read_experiment\",\"record_assessment\"],\"COORDINATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"read_experiment\",\"request_promotion\"],\"EVALUATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"read_experiment\",\"record_review\"],\"RESEARCHER\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"search_evidence\",\"request_source_refresh\",\"register_candidate\",\"request_experiment\",\"read_experiment\",\"record_research_proposal\"]},\"id\":\"ROLE_GRANTS_V2\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M6 tool catalog v2 and ExecPlan 0023 section 5.8\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"EVENT_INVESTIGATION_V1\"],\"COORDINATOR\":[\"PROMOTION_V1\"],\"EVALUATOR\":[\"ASSESSMENT_REVIEW_V2\",\"CANDIDATE_REVIEW_V1\"],\"RESEARCHER\":[\"RESEARCH_V1\"]},\"version\":2}", "f421f2bfc60d25ff95ea2d7d916d1ad8f4601ef1ee955c74e5bd27a9d3799cf7"]
["TEMPLATES_V2", "TEMPLATES", 2, "CODE_OWNED", "{\"delegation\":\"NONE_MODEL_CHOSEN; FIXED_CHILD_ONLY\",\"id\":\"TEMPLATES_V2\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER\",\"PROMOTION\",\"INVESTIGATION\",\"RESEARCH\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M6 tool catalog v2 and ExecPlan 0023 section 5.8\",\"status\":\"CODE_OWNED\",\"templates\":{\"ASSESSMENT_REVIEW_V2\":{\"artifact\":\"EVALUATION_REVIEW\",\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"PARENT_CUTOFF_AND_THE_ITEMS_ITS_REFRESH_DELIVERED\",\"parent\":\"EVENT_INVESTIGATION_V1\",\"prompt\":\"EVALUATOR_PROMPT_M6_V2\",\"purpose\":\"REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_PARENT_FINISH\"},\"CANDIDATE_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"binds\":[\"PROPOSAL_SHA256\",\"RESULT_SHA256S\"],\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"FIXED_AT_ITS_OWN_START\",\"parent\":\"RESEARCH_V1\",\"prompt\":\"EVALUATOR_PROMPT_M6_V2\",\"purpose\":\"CANDIDATE_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_AFTER_THE_FULL_TEST\"},\"EVENT_INVESTIGATION_V1\":{\"artifact\":\"MARKET_ASSESSMENT\",\"child\":\"ASSESSMENT_REVIEW_V2\",\"cutoff\":\"FIXED_AT_START; OWN_REFRESH_IS_DELIVERED_BY_ITS_COMPLETION_ONLY\",\"follow_on\":{\"budget\":\"DAILY_PARENT_WORKFLOWS\",\"context\":\"QUESTION_TEXT_WITHHELD_UNLESS_ITS_PROVENANCE_IS_AT_OR_BEFORE_THE_RESEARCH_CUTOFF\",\"template\":\"RESEARCH_V1\",\"when\":\"RESEARCH_QUESTION_NAMED_AND_REVIEW_NOT_REJECT\"},\"parameters\":{\"horizon_hours\":{\"maximum\":72,\"minimum\":1},\"symbols\":{\"items\":[\"BTCUSDT\",\"SOLUSDT\"],\"max_items\":2,\"min_items\":1,\"unique\":true}},\"prompt\":\"ANALYST_PROMPT_M6_V2\",\"purpose\":\"INVESTIGATION\",\"role\":\"ANALYST\",\"source_trigger\":{\"coalesce\":\"ONE_OPEN_INVESTIGATION_PER_SOURCE_AND_SYMBOL\",\"horizon_hours\":24,\"symbols\":\"THE_TRIGGER_SYMBOL\"},\"started_by\":[\"OWNER\",\"SOURCE_TRIGGER\"]},\"PROMOTION_V1\":{\"artifact\":\"PROMOTION_PROPOSAL\",\"cutoff\":\"FIXED_AT_START\",\"outcome\":\"PENDING_PROMOTION_OR_ABSTENTION; NO_APPROVAL_PATH_IN_THIS_RELEASE\",\"parameters\":{\"candidate_id\":{\"type\":\"uuid\"}},\"prompt\":\"COORDINATOR_PROMPT_M6_V1\",\"purpose\":\"PROMOTION\",\"role\":\"COORDINATOR\",\"started_by\":[\"OWNER\",\"SYSTEM_ON_EVIDENCE_READY\"]},\"RESEARCH_V1\":{\"artifact\":\"RESEARCH_PROPOSAL\",\"child\":\"CANDIDATE_REVIEW_V1\",\"cutoff\":\"HOLDOUT_START_OF_THE_NEWEST_SEALED_DATASET_AT_START\",\"on_nomination\":\"SYSTEM_QUEUES_THE_FULL_TEST_ONCE_THEN_FIXED_CHILD_REVIEW\",\"parameters\":{\"symbols\":{\"items\":[\"BTCUSDT\",\"SOLUSDT\"],\"max_items\":2,\"min_items\":1,\"unique\":true}},\"prompt\":\"RESEARCHER_PROMPT_M6_V1\",\"purpose\":\"RESEARCH\",\"role\":\"RESEARCHER\",\"schedule\":{\"family\":\"SCHEDULED_RESEARCH\",\"max_per_utc_day\":1,\"requires\":[\"RUNTIME_ENABLED\",\"ENVELOPE_APPROVED\"],\"rule\":\"ONE_PER_NEWLY_SEALED_DATASET\"},\"started_by\":[\"OWNER\",\"SCHEDULE\",\"FOLLOW_ON\"]}},\"version\":2}", "6857f58a85e08a8f7a76218e379e7a02c6e14b2e1e672d4620e20c63c9b5b1b5"]
["BUDGETS_V2", "BUDGETS", 2, "PROPOSED", "{\"child_budget\":\"OWN\",\"child_max_model_steps\":4,\"child_max_tool_calls\":3,\"child_workflow_deadline_seconds\":600,\"daily_parent_workflows\":24,\"final_output_max_bytes\":16384,\"handoff_depth\":1,\"id\":\"BUDGETS_V2\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"max_experiments\":3,\"max_model_steps\":12,\"max_tool_calls\":10,\"probe_call_budget\":60,\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"source\":\"ExecPlan 0023 section 5.8\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":21600,\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":21600,\"version\":2,\"wait_deadline_seconds\":21600,\"workflow_deadline_seconds\":1200}", "cdf777b874ee0c7ed908577f598a52d3e1a4c9981b78d8b5a947d9b2f464e1ee"]
["ANALYST_PROMPT_M6_V2", "PROMPT", 2, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"ANALYST_PROMPT_M6_V2\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"559a21a388b55eeb7cb5cb2f6190e880c47e3115cc0c6971a23ed230d46da483\",\"source\":\"services/agent-runner/prompts/m6/analyst.v2.md\",\"status\":\"CODE_OWNED\",\"version\":2}", "00ca20fa91bb69e7fa2964f27c87e8372baae6b4bf04d14510378d5df63fcc23"]
["COORDINATOR_PROMPT_M6_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COORDINATOR_PROMPT_M6_V1\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"2d7b169d4a587beec37476d26319f80eeddc1f957d0fc4ca6843b564f5990b9d\",\"source\":\"services/agent-runner/prompts/m6/coordinator.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "e00083d77618acd6b1b98405c7f22bf66ff092ef095f5dbc63f89305eba75d02"]
["EVALUATOR_PROMPT_M6_V2", "PROMPT", 2, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"EVALUATOR_PROMPT_M6_V2\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"5f9a18239801b4ba3bf1413ce522996e02133ebf0163e35e38788355646bffd2\",\"source\":\"services/agent-runner/prompts/m6/evaluator.v2.md\",\"status\":\"CODE_OWNED\",\"version\":2}", "b75b7df17a910103a81c0712fe8b0d84cc21d9e4609ec877f29f80e3a68be2ea"]
["RESEARCHER_PROMPT_M6_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"RESEARCHER_PROMPT_M6_V1\",\"kind\":\"PROMPT\",\"role\":\"RESEARCHER\",\"sha256\":\"62f856c5ad6c4a6623fefe50e7e909bcc10cff78b1d006a8b6baabb0700cd78b\",\"source\":\"services/agent-runner/prompts/m6/researcher.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "cc7e433d73a8683e40fe0fcc54592a9959a7489f4d343c18763225bdaf341de2"]
"""

LEGACY_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "FEATURE_REGISTRY",
                "TEMPLATES", "BUDGETS", "EGRESS_ALLOWLIST", "PROMPT")
M6_KINDS = ("SOURCE_VERSION", "RESEARCH_ENVELOPE", "RESEARCH_PROTOCOL", "CANDIDATE_GRAMMAR")
TABLES = ("agent_tool_completions", "source_refresh_requests", "source_fetches", "evidence_items",
          "agent_triggers", "research_datasets", "research_hypotheses", "research_candidates",
          "research_candidate_events", "research_jobs", "research_results", "research_trials",
          "research_shadows", "research_shadow_marks", "research_staging_runs", "research_promotions")
APPEND_ONLY = ("agent_tool_completions", "source_fetches", "evidence_items", "research_datasets",
               "research_hypotheses", "research_candidates", "research_candidate_events",
               "research_results", "research_trials", "research_shadow_marks", "research_staging_runs")
VIEWS = tuple("research_read." + name for name in
              ("market_collections", "market_payloads", "market_observations",
               "market_candle_confirmations", "market_publications"))
STATES = ("DRAFT", "VALIDATED", "TEST_QUEUED", "TESTED", "SHADOW_ELIGIBLE", "SHADOW_RUNNING",
          "EVIDENCE_READY", "MAIN_APPROVAL_PENDING", "MAIN_APPROVED", "REJECTED", "SUSPENDED", "RETIRED")
M6_TEMPLATES = ("EVENT_INVESTIGATION_V1", "RESEARCH_V1", "ASSESSMENT_REVIEW_V2",
                "CANDIDATE_REVIEW_V1", "PROMOTION_V1")


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    documents = deepcopy(SEED_DOCUMENTS)
    def canonical(document):
        return json.dumps(document, ensure_ascii=True, sort_keys=True, separators=(",", ":"))

    hashes = {d["id"]: hashlib.sha256(canonical(d).encode()).hexdigest()
              for d in documents if d["kind"] != "RESEARCH_ENVELOPE"}
    for document in documents:
        if document["kind"] == "RESEARCH_ENVELOPE":
            document["protocol_sha256"] = hashes[document["protocol_id"]]
            document["grammar_sha256"] = hashes[document["grammar_id"]]
    return [{"id": d["id"], "kind": d["kind"], "version": d["version"], "status": d["status"],
             "canonical": canonical(d), "sha256": hashlib.sha256(canonical(d).encode()).hexdigest()}
            for d in documents]


def agent_seed_rows():
    rows = []
    for line in AGENT_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in LEGACY_KINDS:
            raise RuntimeError("frozen agent seed is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _checks(m6):
    kinds = LEGACY_KINDS + M6_KINDS if m6 else LEGACY_KINDS
    targets = ("RUNTIME_PROFILE", "RESEARCH_ENVELOPE", "SOURCE_VERSION", "PROMOTION") if m6 else ("RUNTIME_PROFILE",)
    purposes = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION") if m6 else (
        "ASSESSMENT", "REVIEW", "PROBE")
    creators = ("OWNER", "ORCHESTRATOR", "PROBE_RUN", "FIXTURE", "SYSTEM", "SOURCE_TRIGGER", "SCHEDULE", "FOLLOW_ON") if m6 else (
        "OWNER", "ORCHESTRATOR", "PROBE_RUN", "FIXTURE")
    statuses = ("SUCCEEDED", "REJECTED", "UNAVAILABLE", "QUEUED") if m6 else ("SUCCEEDED", "REJECTED", "UNAVAILABLE")
    artifacts = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL") if m6 else (
        "MARKET_ASSESSMENT", "EVALUATION_REVIEW")
    for table, column, values in (("agent_definitions", "kind", kinds),
                                  ("agent_approvals", "target_kind", targets),
                                  ("agent_workflows", "purpose", purposes),
                                  ("agent_workflows", "created_by", creators),
                                  ("agent_tool_results", "status", statuses),
                                  ("agent_artifacts", "kind", artifacts)):
        name = table + "_" + column + "_check"
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {name}")
        op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} CHECK ({column} IN {_quoted(values)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflow_child")
    child = "purpose IN ('REVIEW','CANDIDATE_REVIEW')" if m6 else "purpose = 'REVIEW'"
    op.execute(f"ALTER TABLE agent_workflows ADD CONSTRAINT agent_workflow_child CHECK (({child}) = (parent_id IS NOT NULL))")


# Preserve every M5 immutable/transition check. Only owner-startable template pairs grow.
def _workflow_guard(m6):
    owner_pairs = """(NEW.template_id = 'MARKET_ASSESSMENT_V1' AND NEW.purpose = 'ASSESSMENT' AND NEW.role = 'ANALYST')"""
    if m6:
        owner_pairs = """((NEW.template_id = 'MARKET_ASSESSMENT_V1' AND NEW.purpose = 'ASSESSMENT' AND NEW.role = 'ANALYST')
                     OR (NEW.template_id = 'EVENT_INVESTIGATION_V1' AND NEW.purpose = 'INVESTIGATION' AND NEW.role = 'ANALYST')
                     OR (NEW.template_id = 'RESEARCH_V1' AND NEW.purpose = 'RESEARCH' AND NEW.role = 'RESEARCHER')
                     OR (NEW.template_id = 'PROMOTION_V1' AND NEW.purpose = 'PROMOTION' AND NEW.role = 'COORDINATOR'))"""
    terminal = _quoted(("SUCCEEDED", "ABSTAINED", "REJECTED_OUTPUT", "EXPIRED", "AUTH_REQUIRED", "QUOTA_BLOCKED", "FAILED", "CANCELED"))
    op.execute(f"""
        CREATE OR REPLACE FUNCTION asl_agent_workflow_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE pair text;
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF TG_OP = 'INSERT' THEN
                IF NEW.mode = 'OFFLINE_TEST' AND current_database() NOT LIKE 'asl\\_m1\\_%' THEN
                    RAISE EXCEPTION 'OFFLINE_TEST agent workflows require a disposable asl_m1_ database'; END IF;
                IF NEW.version <> 0 THEN RAISE EXCEPTION 'agent workflows start at version 0'; END IF;
                IF current_user = 'asl_api' AND NEW.created_by = 'OWNER' AND NEW.state = 'QUEUED'
                        AND NEW.parent_id IS NULL AND {owner_pairs}
                        AND NEW.provider = 'CODEX' AND NEW.permission_epoch IS NULL
                        AND NEW.cutoff IS NULL AND NEW.started_at IS NULL THEN RETURN NEW; END IF;
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
            IF OLD.state IN {terminal} THEN RAISE EXCEPTION 'terminal agent workflow cannot change'; END IF;
            IF NEW.version <> OLD.version + 1 THEN RAISE EXCEPTION 'agent workflow version must increase by one'; END IF;
            IF OLD.permission_epoch IS NOT NULL AND NEW.permission_epoch IS DISTINCT FROM OLD.permission_epoch THEN
                RAISE EXCEPTION 'agent workflow epoch binding is immutable'; END IF;
            IF OLD.cutoff IS NOT NULL AND NEW.cutoff IS DISTINCT FROM OLD.cutoff THEN
                RAISE EXCEPTION 'agent workflow cutoff is immutable'; END IF;
            IF NEW.state = OLD.state THEN RETURN NEW; END IF;
            IF pair IN ('QUEUED>RUNNING','RUNNING>WAITING_TOOL','WAITING_TOOL>RUNNING','RUNNING>WAITING_REVIEW')
                    OR (OLD.state = 'QUEUED' AND NEW.state IN ('EXPIRED','CANCELED','FAILED'))
                    OR (OLD.state IN ('RUNNING','WAITING_TOOL') AND NEW.state IN {terminal})
                    OR (OLD.state = 'WAITING_REVIEW' AND NEW.state IN ('SUCCEEDED','CANCELED','FAILED','EXPIRED')) THEN
                RETURN NEW; END IF;
            RAISE EXCEPTION 'agent workflow transition % is not allowed', pair;
        END $$;
    """)


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    op.execute("ALTER TABLE agent_workflows ALTER COLUMN purpose TYPE varchar(32)")
    _checks(True)
    _workflow_guard(True)
    op.execute(DDL)
    op.execute(GUARDS)
    op.execute(CONTENT_GUARD)
    # Row locks require UPDATE privilege; expose only a fixed lock/read instead.
    op.execute("""
        CREATE FUNCTION research_hold_permission_epoch() RETURNS bigint
        LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp AS $$
            SELECT epoch FROM public.agent_permission_epoch WHERE id=1 FOR SHARE
        $$;
        REVOKE ALL ON FUNCTION research_hold_permission_epoch() FROM PUBLIC;
    """)
    for table in TABLES:
        op.execute(f"CREATE TRIGGER {table}_fixture BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m6_fixture_guard()")
        op.execute(f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    for table in ("agent_tool_completions", "research_datasets", "research_hypotheses", "research_candidates",
                  "research_results", "research_shadow_marks", "research_promotions"):
        op.execute(f"CREATE TRIGGER {table}_content BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m6_content_guard()")
    for table in ("source_refresh_requests", "agent_triggers", "research_jobs", "research_shadows", "research_promotions"):
        op.execute(f"CREATE TRIGGER {table}_guard BEFORE INSERT OR UPDATE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m6_transition_guard()")
    op.execute("CREATE TRIGGER research_candidate_events_guard BEFORE INSERT ON research_candidate_events "
               "FOR EACH ROW EXECUTE FUNCTION asl_m6_candidate_guard()")
    op.execute("CREATE TRIGGER agent_approvals_m6_guard BEFORE INSERT ON agent_approvals "
               "FOR EACH ROW EXECUTE FUNCTION asl_m6_approval_guard()")
    op.execute(VIEW_SQL)
    bind = op.get_bind()
    for row in [*seed_rows(), *agent_seed_rows()]:
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    bind.exec_driver_sql("""DO $$ BEGIN
        IF EXISTS (SELECT 1 FROM agent_definitions WHERE
                   encode(digest(convert_to(canonical,'UTF8'),'sha256'),'hex') <> sha256) THEN
            RAISE EXCEPTION 'seeded definition hash mismatch'; END IF;
        END $$""")
    raw = bind.connection.driver_connection
    with raw.cursor() as cursor:
        for role in ("asl_research", "asl_source"):
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (role,))
            if cursor.fetchone() is None:
                cursor.execute(sql.SQL("CREATE ROLE {} NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT").format(sql.Identifier(role)))
            else:
                # Roles belong to the cluster, not one database. Successive working stores
                # reuse only the inert identity created by this same migration.
                cursor.execute("SELECT rolcanlogin OR rolsuper OR rolcreatedb OR rolcreaterole OR rolinherit "
                               "OR rolreplication OR rolbypassrls FROM pg_roles WHERE rolname=%s", (role,))
                if cursor.fetchone()[0]:
                    raise RuntimeError("M6 role has unexpected authority; refusing to adopt it")
            cursor.execute(sql.SQL("ALTER ROLE {} SET statement_timeout = '2s'").format(sql.Identifier(role)))
            cursor.execute(sql.SQL("ALTER ROLE {} SET lock_timeout = '200ms'").format(sql.Identifier(role)))
            cursor.execute(sql.SQL("ALTER ROLE {} SET idle_in_transaction_session_timeout = '5s'").format(sql.Identifier(role)))
            cursor.execute(sql.SQL("ALTER ROLE {} SET jit = off").format(sql.Identifier(role)))
            cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(
                sql.Identifier(os.environ.get("ASL_DB_NAME", "asl")), sql.Identifier(role)))
    op.execute(GRANTS)
    # B5: the source fetcher holds the same fixed share lock when it commits a fetch result.
    op.execute("GRANT EXECUTE ON FUNCTION research_hold_permission_epoch() TO asl_agent,asl_research,asl_source")


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    for table in TABLES:
        if bind.exec_driver_sql(f"SELECT count(*) FROM {table} WHERE NOT fixture").scalar_one():
            raise RuntimeError("non-fixture M6 records exist; downgrade refused; fix forward")
    extra = bind.exec_driver_sql("""
        SELECT (SELECT count(*) FROM agent_approvals WHERE target_kind <> 'RUNTIME_PROFILE')
             + (SELECT count(*) FROM agent_workflows WHERE template_id IN
                ('EVENT_INVESTIGATION_V1','RESEARCH_V1','ASSESSMENT_REVIEW_V2','CANDIDATE_REVIEW_V1','PROMOTION_V1'))
             + (SELECT count(*) FROM agent_tool_results WHERE status = 'QUEUED')
             + (SELECT count(*) FROM agent_artifacts WHERE kind IN ('RESEARCH_PROPOSAL','PROMOTION_PROPOSAL'))
    """).scalar_one()
    if extra:
        raise RuntimeError("M6 agent history exists; downgrade refused; fix forward")
    op.execute("DROP TRIGGER agent_approvals_m6_guard ON agent_approvals")
    op.execute("DROP VIEW " + ", ".join(VIEWS))
    op.execute("DROP SCHEMA research_read")
    op.execute("DROP FUNCTION research_hold_permission_epoch()")
    op.execute("DROP TABLE " + ", ".join(reversed(TABLES)))
    op.execute("DROP FUNCTION asl_m6_fixture_guard(), asl_m6_transition_guard(), "
               "asl_m6_candidate_guard(), asl_m6_approval_guard(), asl_m6_content_guard()")
    # The seed store is immutable even for the migration role. Relax only this trigger,
    # inside this transaction, and delete only the frozen, verified M6 seed identities.
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in [*seed_rows(), *agent_seed_rows()]:
        result = bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id=%(id)s AND sha256=%(sha256)s", row)
        if result.rowcount != 1:
            raise RuntimeError("M6 seed mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    _checks(False)
    _workflow_guard(False)
    op.execute("ALTER TABLE agent_workflows ALTER COLUMN purpose TYPE varchar(12)")
    with bind.connection.driver_connection.cursor() as cursor:
        for role in ("asl_research", "asl_source"):
            cursor.execute(sql.SQL("DROP OWNED BY {}").format(sql.Identifier(role)))
            cursor.execute(sql.SQL("DROP ROLE {}").format(sql.Identifier(role)))


DDL = """
CREATE TABLE agent_tool_completions (
    id uuid PRIMARY KEY, tool_call_id uuid NOT NULL UNIQUE REFERENCES agent_tool_calls(id),
    workflow_id uuid NOT NULL REFERENCES agent_workflows(id), result_ref varchar(40) NOT NULL UNIQUE,
    status varchar(12) NOT NULL CHECK (status IN ('SUCCEEDED','REJECTED','UNAVAILABLE','CANCELED','EXPIRED')),
    envelope jsonb NOT NULL, output_sha256 varchar(64) NOT NULL CHECK (output_sha256 ~ '^[0-9a-f]{64}$'),
    bytes integer NOT NULL CHECK (bytes BETWEEN 0 AND 65536), permission_epoch bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE source_refresh_requests (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    source_id varchar(64) NOT NULL REFERENCES agent_definitions(id), source_sha256 varchar(64) NOT NULL,
    actor varchar(8) NOT NULL CHECK (actor IN ('OWNER','AGENT','SYSTEM')),
    workflow_id uuid REFERENCES agent_workflows(id), tool_call_id uuid UNIQUE REFERENCES agent_tool_calls(id),
    filters jsonb NOT NULL, dedupe_key varchar(160) NOT NULL UNIQUE, permission_epoch bigint NOT NULL,
    state varchar(12) NOT NULL DEFAULT 'QUEUED' CHECK (state IN ('QUEUED','RUNNING','SUCCEEDED','FAILED','CANCELED','EXPIRED')),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0), outcome jsonb,
    session_id uuid, request_hash varchar(64), idempotency_key varchar(80) UNIQUE,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), updated_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    fixture boolean NOT NULL DEFAULT false,
    CHECK (actor <> 'OWNER' OR (session_id IS NOT NULL AND request_hash IS NOT NULL AND idempotency_key IS NOT NULL)),
    CHECK (actor <> 'AGENT' OR (workflow_id IS NOT NULL AND tool_call_id IS NOT NULL))
);
CREATE INDEX source_refresh_queue ON source_refresh_requests(state,seq);
CREATE TABLE source_fetches (
    id uuid PRIMARY KEY, request_id uuid NOT NULL UNIQUE REFERENCES source_refresh_requests(id),
    source_id varchar(64) NOT NULL REFERENCES agent_definitions(id), source_sha256 varchar(64) NOT NULL,
    outcome varchar(24) NOT NULL, detail jsonb NOT NULL, bytes bigint NOT NULL CHECK (bytes >= 0),
    started_at timestamptz NOT NULL, completed_at timestamptz NOT NULL, next_allowed_at timestamptz,
    fixture boolean NOT NULL DEFAULT false, CHECK (completed_at >= started_at)
);
CREATE INDEX source_fetch_history ON source_fetches(source_id,completed_at);
CREATE TABLE evidence_items (
    id uuid PRIMARY KEY, source_id varchar(64) NOT NULL REFERENCES agent_definitions(id),
    source_sha256 varchar(64) NOT NULL, fetch_id uuid NOT NULL REFERENCES source_fetches(id),
    external_id varchar(160) NOT NULL, revision_sha256 varchar(64) NOT NULL CHECK (revision_sha256 ~ '^[0-9a-f]{64}$'),
    published_at timestamptz, updated_at timestamptz, received_at timestamptz NOT NULL, available_at timestamptz NOT NULL,
    title text NOT NULL, extract text NOT NULL, external_url text NOT NULL, attribution jsonb NOT NULL,
    symbols jsonb NOT NULL, search_vector tsvector NOT NULL,
    fixture boolean NOT NULL DEFAULT false, CHECK (available_at >= received_at),
    CHECK (octet_length(title) <= 2048 AND octet_length(extract) <= 16384 AND octet_length(external_url) <= 2048),
    UNIQUE (source_id,source_sha256,external_id,revision_sha256)
);
CREATE INDEX evidence_search ON evidence_items USING gin(search_vector);
CREATE INDEX evidence_cutoff ON evidence_items(source_id,available_at,id);
CREATE TABLE agent_triggers (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    family varchar(24) NOT NULL CHECK (family IN ('SOURCE_REVISION','SCHEDULED_RESEARCH','FOLLOW_ON')),
    dedupe_key varchar(160) NOT NULL UNIQUE, cooldown_until timestamptz NOT NULL, detail jsonb NOT NULL,
    state varchar(12) NOT NULL DEFAULT 'QUEUED' CHECK (state IN ('QUEUED','CONSUMED','REFUSED','CANCELED')),
    version bigint NOT NULL DEFAULT 0, outcome jsonb, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    fixture boolean NOT NULL DEFAULT false
);
CREATE INDEX agent_triggers_queue ON agent_triggers(state,seq);
CREATE TABLE research_datasets (
    id uuid PRIMARY KEY, store_version varchar(63) NOT NULL CHECK (store_version LIKE 'asl\\_m1\\_replay\\_%'),
    state varchar(8) NOT NULL DEFAULT 'SEALED' CHECK (state = 'SEALED'),
    first_sequence bigint NOT NULL, last_sequence bigint NOT NULL,
    start_at timestamptz NOT NULL, end_at timestamptz NOT NULL, holdout_start_at timestamptz NOT NULL,
    protocol_sha256 varchar(64) NOT NULL, envelope_sha256 varchar(64) NOT NULL,
    manifest jsonb NOT NULL, canonical text NOT NULL, sha256 varchar(64) NOT NULL UNIQUE CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    sealed_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    purpose text GENERATED ALWAYS AS (manifest->>'purpose') STORED,
    CHECK (first_sequence > 0 AND last_sequence >= first_sequence),
    CHECK (end_at > start_at AND holdout_start_at > start_at AND holdout_start_at <= end_at)
);
CREATE TABLE research_hypotheses (
    id uuid PRIMARY KEY, workflow_id uuid REFERENCES agent_workflows(id),
    dataset_id uuid NOT NULL REFERENCES research_datasets(id), information_cutoff timestamptz NOT NULL,
    statement text NOT NULL, provenance jsonb NOT NULL, envelope_sha256 varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE research_candidates (
    id uuid PRIMARY KEY, hypothesis_id uuid NOT NULL REFERENCES research_hypotheses(id),
    grammar_id varchar(64) NOT NULL REFERENCES agent_definitions(id), grammar_sha256 varchar(64) NOT NULL,
    envelope_sha256 varchar(64) NOT NULL, declaration jsonb NOT NULL, canonical text NOT NULL,
    normalized_sha256 varchar(64) NOT NULL UNIQUE CHECK (normalized_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE research_candidate_events (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    candidate_id uuid NOT NULL REFERENCES research_candidates(id),
    actor varchar(8) NOT NULL CHECK (actor = 'SYSTEM'), previous_state varchar(24), state varchar(24) NOT NULL,
    gate_evidence jsonb NOT NULL, operation_key varchar(160) NOT NULL UNIQUE,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK (state IN ('DRAFT','VALIDATED','TEST_QUEUED','TESTED','SHADOW_ELIGIBLE','SHADOW_RUNNING',
                     'EVIDENCE_READY','MAIN_APPROVAL_PENDING','MAIN_APPROVED','REJECTED','SUSPENDED','RETIRED'))
);
CREATE INDEX research_candidate_history ON research_candidate_events(candidate_id,seq);
CREATE TABLE research_jobs (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    kind varchar(12) NOT NULL CHECK (kind IN ('SCREEN','FULL','SHADOW')),
    hypothesis_id uuid NOT NULL REFERENCES research_hypotheses(id), candidate_id uuid NOT NULL REFERENCES research_candidates(id),
    dataset_id uuid NOT NULL REFERENCES research_datasets(id), input_sha256 varchar(64) NOT NULL,
    code_identity varchar(64) NOT NULL, envelope_sha256 varchar(64) NOT NULL, permission_epoch bigint NOT NULL,
    workflow_id uuid REFERENCES agent_workflows(id), tool_call_id uuid UNIQUE REFERENCES agent_tool_calls(id),
    operation_key varchar(160) NOT NULL UNIQUE, reservation jsonb NOT NULL,
    state varchar(12) NOT NULL DEFAULT 'QUEUED' CHECK (state IN ('QUEUED','DISPATCHED','RUNNING','SUCCEEDED','FAILED','CANCELED','EXPIRED')),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0), lease_owner uuid, lease_epoch bigint NOT NULL DEFAULT 0,
    lease_until timestamptz, deadline_at timestamptz NOT NULL, resources jsonb NOT NULL DEFAULT '{}', outcome jsonb,
    owner_cancel_request jsonb, created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    started_at timestamptz, completed_at timestamptz, fixture boolean NOT NULL DEFAULT false,
    CHECK (lease_epoch >= 0 AND deadline_at > created_at),
    CHECK (kind <> 'FULL' OR (reservation ? 'holdout_attempt' AND reservation->>'holdout_attempt' IN ('0','1')))
);
CREATE UNIQUE INDEX research_one_active_job ON research_jobs((1)) WHERE state IN ('DISPATCHED','RUNNING');
CREATE INDEX research_job_queue ON research_jobs(state,seq);
CREATE UNIQUE INDEX research_holdout_once ON research_jobs(hypothesis_id, ((reservation->>'holdout_attempt')::integer))
    WHERE kind = 'FULL';
CREATE TABLE research_results (
    id uuid PRIMARY KEY, job_id uuid NOT NULL UNIQUE REFERENCES research_jobs(id),
    candidate_id uuid NOT NULL REFERENCES research_candidates(id), dataset_id uuid NOT NULL REFERENCES research_datasets(id),
    input_sha256 varchar(64) NOT NULL, code_identity varchar(64) NOT NULL, portable_fingerprint varchar(64) NOT NULL,
    canonical text NOT NULL, document jsonb NOT NULL, sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    integrity varchar(12) NOT NULL CHECK (integrity IN ('VALID','FAILED','INCOMPLETE')),
    fidelity varchar(32) NOT NULL CHECK (fidelity = 'SAMPLED_L1_TICKER'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE research_trials (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    hypothesis_id uuid NOT NULL REFERENCES research_hypotheses(id), candidate_id uuid REFERENCES research_candidates(id),
    dataset_id uuid NOT NULL REFERENCES research_datasets(id), job_id uuid REFERENCES research_jobs(id),
    outcome varchar(24) NOT NULL, input_sha256 varchar(64) NOT NULL, operation_key varchar(160) NOT NULL UNIQUE,
    detail jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE TABLE research_shadows (
    id uuid PRIMARY KEY, candidate_id uuid NOT NULL REFERENCES research_candidates(id),
    hypothesis_id uuid NOT NULL REFERENCES research_hypotheses(id), envelope_sha256 varchar(64) NOT NULL,
    frozen_at timestamptz NOT NULL, end_at timestamptz NOT NULL,
    virtual_funding numeric NOT NULL CHECK (virtual_funding = 10000),
    state varchar(12) NOT NULL DEFAULT 'QUEUED' CHECK (state IN ('QUEUED','RUNNING','SUCCEEDED','INCOMPLETE','SUSPENDED','STOPPED')),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0), last_available_at timestamptz, prefix_fingerprint varchar(64),
    owner_stop_request jsonb, detail jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK (end_at > frozen_at AND end_at <= frozen_at + interval '21 days')
);
CREATE TABLE research_shadow_marks (
    id uuid PRIMARY KEY, shadow_id uuid NOT NULL REFERENCES research_shadows(id),
    job_id uuid NOT NULL REFERENCES research_jobs(id), available_through timestamptz NOT NULL,
    prefix_fingerprint varchar(64) NOT NULL, canonical text NOT NULL, document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    UNIQUE (shadow_id,available_through)
);
CREATE TABLE research_staging_runs (
    id uuid PRIMARY KEY, store_version varchar(63) NOT NULL CHECK (store_version LIKE 'asl\\_m1\\_replay\\_%'),
    first_sequence bigint NOT NULL, last_sequence bigint NOT NULL, rows_copied bigint NOT NULL CHECK (rows_copied >= 0),
    outcome varchar(16) NOT NULL, gaps jsonb NOT NULL, detail jsonb NOT NULL,
    started_at timestamptz NOT NULL, completed_at timestamptz NOT NULL,
    fixture boolean NOT NULL DEFAULT false, CHECK (completed_at >= started_at)
);
CREATE INDEX research_staging_journal_time ON research_staging_runs(completed_at);
CREATE INDEX research_staging_journal_store ON research_staging_runs(store_version,outcome,last_sequence);
CREATE TABLE research_promotions (
    id uuid PRIMARY KEY, candidate_id uuid NOT NULL REFERENCES research_candidates(id),
    workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id), actor varchar(16) NOT NULL CHECK (actor = 'COORDINATOR'),
    canonical text NOT NULL, document jsonb NOT NULL, sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    state varchar(12) NOT NULL DEFAULT 'PENDING' CHECK (state IN ('PENDING','REJECTED','WITHDRAWN')),
    version bigint NOT NULL DEFAULT 0, gate_evidence jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
"""

VIEW_SQL = """
CREATE SCHEMA research_read;
CREATE VIEW research_read.market_observations WITH (security_barrier = true) AS
    SELECT o.* FROM market_observations o WHERE EXISTS (SELECT 1 FROM market_publications p WHERE p.observation_id=o.id);
CREATE VIEW research_read.market_payloads WITH (security_barrier = true) AS
    SELECT b.* FROM market_payloads b WHERE EXISTS
        (SELECT 1 FROM market_observations o JOIN market_publications p ON p.observation_id=o.id WHERE o.payload_id=b.id)
        OR EXISTS (SELECT 1 FROM market_candle_confirmations f JOIN market_publications p ON p.confirmation_id=f.id
                   WHERE f.payload_id=b.id);
CREATE VIEW research_read.market_collections WITH (security_barrier = true) AS
    SELECT c.* FROM market_collections c WHERE EXISTS
        (SELECT 1 FROM market_observations o JOIN market_publications p ON p.observation_id=o.id WHERE o.collection_id=c.id)
        OR EXISTS (SELECT 1 FROM market_candle_confirmations f JOIN market_publications p ON p.confirmation_id=f.id
                   WHERE f.collection_id=c.id);
CREATE VIEW research_read.market_candle_confirmations WITH (security_barrier = true) AS
    SELECT f.* FROM market_candle_confirmations f WHERE EXISTS (SELECT 1 FROM market_publications p WHERE p.confirmation_id=f.id);
CREATE VIEW research_read.market_publications WITH (security_barrier = true) AS SELECT p.* FROM market_publications p;
"""

GUARDS = """
CREATE FUNCTION asl_m6_fixture_guard() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF NEW.fixture AND (NOT asl_is_superuser() OR current_database() NOT LIKE 'asl\\_m1\\_%') THEN
        RAISE EXCEPTION 'fixture rows require a disposable database and migration identity'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m6_approval_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE expected_hash text;
BEGIN
    IF NEW.target_kind = 'PROMOTION' THEN
        IF NEW.action <> 'REJECT' THEN RAISE EXCEPTION 'M6 promotions can only be rejected'; END IF;
        SELECT sha256 INTO expected_hash FROM research_promotions WHERE id::text=NEW.target_id AND state='PENDING';
    ELSIF NEW.target_kind IN ('SOURCE_VERSION','RESEARCH_ENVELOPE') THEN
        -- B5: a decision on a source version waits for a publication of evidence in flight, and a
        -- publication started later sees the decision. The key is app.sources.store.LOCK.
        IF NEW.target_kind = 'SOURCE_VERSION' THEN PERFORM pg_advisory_xact_lock(6005001); END IF;
        SELECT sha256 INTO expected_hash FROM agent_definitions WHERE id=NEW.target_id AND kind=NEW.target_kind;
    ELSE RETURN NEW;
    END IF;
    IF expected_hash IS NULL OR expected_hash <> NEW.target_sha256 THEN
        RAISE EXCEPTION 'M6 approval target/hash mismatch'; END IF;
    IF current_user <> 'asl_api' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'M6 approvals are owner records'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m6_candidate_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE previous text;
BEGIN
    IF NEW.state='MAIN_APPROVED' THEN RAISE EXCEPTION 'MAIN_APPROVED is unreachable in M6'; END IF;
    IF current_user NOT IN ('asl_agent','asl_research') AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'candidate transitions require SYSTEM authority'; END IF;
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.candidate_id::text,608));
    SELECT state INTO previous FROM research_candidate_events WHERE candidate_id=NEW.candidate_id ORDER BY seq DESC LIMIT 1;
    IF NEW.previous_state IS DISTINCT FROM previous THEN RAISE EXCEPTION 'candidate transition is stale'; END IF;
    IF previous IS NULL AND NEW.state='DRAFT' THEN RETURN NEW; END IF;
    IF (previous || '>' || NEW.state) IN ('DRAFT>VALIDATED','VALIDATED>TEST_QUEUED','TEST_QUEUED>TESTED',
          'TESTED>SHADOW_ELIGIBLE','SHADOW_ELIGIBLE>SHADOW_RUNNING','SHADOW_RUNNING>EVIDENCE_READY',
          'EVIDENCE_READY>MAIN_APPROVAL_PENDING','SUSPENDED>RETIRED')
          OR (previous IS NOT NULL AND previous NOT IN ('REJECTED','RETIRED') AND NEW.state IN ('REJECTED','SUSPENDED','RETIRED')) THEN
        IF NEW.gate_evidence='{}'::jsonb THEN RAISE EXCEPTION 'candidate transition requires gate evidence'; END IF;
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'candidate transition is not allowed';
END $$;
CREATE FUNCTION asl_m6_transition_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE mutable text[]; allowed boolean := false; pair text;
BEGIN
    IF TG_OP='INSERT' THEN
        IF NEW.version <> 0 THEN RAISE EXCEPTION 'M6 records start at version zero'; END IF;
        IF TG_TABLE_NAME='research_promotions' THEN
            IF NEW.state<>'PENDING' THEN RAISE EXCEPTION 'promotion starts pending'; END IF;
            IF current_user<>'asl_agent' AND NOT asl_is_superuser() THEN RAISE EXCEPTION 'promotion requires coordinator workflow'; END IF;
            IF NOT EXISTS (SELECT 1 FROM agent_workflows WHERE id=NEW.workflow_id AND role='COORDINATOR') THEN
                RAISE EXCEPTION 'promotion workflow role mismatch'; END IF;
            IF (SELECT state FROM research_candidate_events WHERE candidate_id=NEW.candidate_id ORDER BY seq DESC LIMIT 1)
                    IS DISTINCT FROM 'EVIDENCE_READY' THEN RAISE EXCEPTION 'promotion requires EVIDENCE_READY'; END IF;
        ELSIF NEW.state<>'QUEUED' THEN RAISE EXCEPTION 'M6 work starts queued';
        END IF;
        IF TG_TABLE_NAME='source_refresh_requests' THEN
            IF (NEW.actor='OWNER' AND current_user<>'asl_api')
                OR (NEW.actor='AGENT' AND current_user<>'asl_agent')
                OR (NEW.actor='SYSTEM' AND current_user NOT IN ('asl_source','asl_agent')) THEN
                IF NOT asl_is_superuser() THEN RAISE EXCEPTION 'source request actor mismatch'; END IF;
            END IF;
        END IF;
        IF TG_TABLE_NAME='research_jobs' THEN
            IF NEW.kind='FULL' AND NEW.reservation->>'holdout_attempt'='1'
                    AND NOT EXISTS (SELECT 1 FROM research_jobs WHERE hypothesis_id=NEW.hypothesis_id AND kind='FULL'
                        AND reservation->>'holdout_attempt'='0' AND state IN ('FAILED','EXPIRED')) THEN
                RAISE EXCEPTION 'holdout retry requires a failed first evaluation'; END IF;
        END IF;
        RETURN NEW;
    END IF;
    IF NEW.version<>OLD.version+1 THEN RAISE EXCEPTION 'M6 version must increase by one'; END IF;
    pair:=OLD.state || '>' || NEW.state;
    CASE TG_TABLE_NAME
        WHEN 'source_refresh_requests' THEN
            mutable:=ARRAY['state','version','outcome','updated_at'];
            allowed:=current_user='asl_source' AND (pair IN ('QUEUED>RUNNING','RUNNING>SUCCEEDED','RUNNING>FAILED')
                OR (OLD.state IN ('QUEUED','RUNNING') AND NEW.state IN ('CANCELED','EXPIRED')));
        WHEN 'agent_triggers' THEN
            mutable:=ARRAY['state','version','outcome'];
            allowed:=current_user='asl_agent' AND OLD.state='QUEUED' AND NEW.state IN ('CONSUMED','REFUSED','CANCELED');
        WHEN 'research_jobs' THEN
            mutable:=ARRAY['state','version','lease_owner','lease_epoch','lease_until','resources','outcome',
                           'owner_cancel_request','started_at','completed_at'];
            allowed:=current_user='asl_research' AND (pair IN ('QUEUED>DISPATCHED','DISPATCHED>RUNNING','RUNNING>SUCCEEDED',
                      'QUEUED>CANCELED','DISPATCHED>CANCELED','RUNNING>CANCELED','DISPATCHED>QUEUED')
                OR (OLD.state IN ('QUEUED','DISPATCHED','RUNNING') AND NEW.state IN ('FAILED','EXPIRED'))
                OR (OLD.state=NEW.state AND OLD.state IN ('DISPATCHED','RUNNING')));
            IF NEW.lease_epoch<OLD.lease_epoch THEN RAISE EXCEPTION 'research fencing epoch cannot decrease'; END IF;
            IF OLD.owner_cancel_request IS NOT NULL AND NEW.owner_cancel_request IS DISTINCT FROM OLD.owner_cancel_request THEN
                RAISE EXCEPTION 'owner cancellation is immutable'; END IF;
            IF current_user='asl_api' THEN
                mutable:=ARRAY['version','owner_cancel_request'];
                allowed:=OLD.state IN ('QUEUED','DISPATCHED','RUNNING') AND OLD.owner_cancel_request IS NULL
                         AND NEW.owner_cancel_request IS NOT NULL;
            END IF;
        WHEN 'research_shadows' THEN
            mutable:=ARRAY['state','version','last_available_at','prefix_fingerprint','owner_stop_request','detail'];
            allowed:=current_user='asl_research' AND (pair IN ('QUEUED>RUNNING','RUNNING>SUCCEEDED')
                OR (OLD.state IN ('QUEUED','RUNNING') AND NEW.state IN ('STOPPED','INCOMPLETE','SUSPENDED'))
                OR pair='RUNNING>RUNNING');
            IF NEW.last_available_at<OLD.last_available_at THEN RAISE EXCEPTION 'shadow watermark cannot decrease'; END IF;
            IF OLD.owner_stop_request IS NOT NULL AND NEW.owner_stop_request IS DISTINCT FROM OLD.owner_stop_request THEN
                RAISE EXCEPTION 'owner stop is immutable'; END IF;
            IF current_user='asl_api' THEN
                mutable:=ARRAY['version','owner_stop_request'];
                allowed:=OLD.state IN ('QUEUED','RUNNING') AND OLD.owner_stop_request IS NULL AND NEW.owner_stop_request IS NOT NULL;
            END IF;
        WHEN 'research_promotions' THEN
            mutable:=ARRAY['state','version'];
            allowed:=current_user='asl_agent' AND OLD.state='PENDING' AND NEW.state IN ('REJECTED','WITHDRAWN');
    END CASE;
    IF (to_jsonb(NEW)-mutable) IS DISTINCT FROM (to_jsonb(OLD)-mutable) THEN
        RAISE EXCEPTION 'M6 record identity is immutable'; END IF;
    IF NOT allowed AND NOT (asl_is_superuser() AND OLD.fixture) THEN
        RAISE EXCEPTION 'M6 transition % is not allowed for %',pair,current_user; END IF;
    RETURN NEW;
END $$;
"""

CONTENT_GUARD = """
CREATE FUNCTION asl_m6_content_guard() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE body jsonb; expected_hash text; actual_hash text; cutoff timestamptz; row_data jsonb;
BEGIN
    IF TG_TABLE_NAME='agent_tool_completions' THEN
        IF NOT EXISTS (SELECT 1 FROM agent_tool_calls c JOIN agent_tool_results r ON r.tool_call_id=c.id
            WHERE c.id=NEW.tool_call_id AND c.workflow_id=NEW.workflow_id AND c.permission_epoch=NEW.permission_epoch
            AND r.status='QUEUED' AND c.decision='AUTHORIZED' AND r.result_ref<>NEW.result_ref) THEN
            RAISE EXCEPTION 'completion must bind its authorized queued call'; END IF;
        IF EXISTS (SELECT 1 FROM agent_tool_results WHERE result_ref=NEW.result_ref) THEN
            RAISE EXCEPTION 'completion requires its own result reference'; END IF;
        RETURN NEW;
    END IF;
    IF TG_TABLE_NAME='research_hypotheses' THEN
        SELECT holdout_start_at INTO cutoff FROM research_datasets WHERE id=NEW.dataset_id
            AND envelope_sha256=NEW.envelope_sha256;
        IF cutoff IS NULL OR NEW.information_cutoff<>cutoff THEN
            RAISE EXCEPTION 'hypothesis cutoff must be its immutable dataset holdout start'; END IF;
        RETURN NEW;
    END IF;
    row_data:=to_jsonb(NEW);
    IF TG_TABLE_NAME='research_datasets' THEN body:=NEW.manifest;
    ELSIF TG_TABLE_NAME='research_candidates' THEN
        body:=NEW.declaration;
        IF NOT EXISTS (SELECT 1 FROM agent_definitions WHERE id=NEW.grammar_id
                        AND kind='CANDIDATE_GRAMMAR' AND sha256=NEW.grammar_sha256)
            OR NOT EXISTS (SELECT 1 FROM research_hypotheses WHERE id=NEW.hypothesis_id
                            AND envelope_sha256=NEW.envelope_sha256) THEN
            RAISE EXCEPTION 'candidate definition binding mismatch'; END IF;
    ELSE body:=NEW.document;
    END IF;
    actual_hash:=encode(digest(convert_to(NEW.canonical,'UTF8'),'sha256'),'hex');
    expected_hash:=COALESCE(row_data->>'sha256',row_data->>'normalized_sha256');
    IF NEW.canonical::jsonb<>body OR actual_hash<>expected_hash THEN
        RAISE EXCEPTION 'M6 canonical document/hash mismatch'; END IF;
    RETURN NEW;
END $$;
"""

GRANTS = """
GRANT USAGE ON SCHEMA public TO asl_research,asl_source;
GRANT USAGE ON SCHEMA research_read TO asl_research;
GRANT SELECT ON research_read.market_collections,research_read.market_payloads,research_read.market_observations,
    research_read.market_candle_confirmations,research_read.market_publications TO asl_research;
GRANT SELECT ON agent_definitions,agent_approvals,agent_runtime_state,agent_permission_epoch,agent_workflows,
    agent_artifacts,agent_tool_calls,agent_tool_results TO asl_research,asl_source;
GRANT SELECT ON agent_tool_completions,source_refresh_requests,source_fetches,evidence_items,agent_triggers,
    research_datasets,research_hypotheses,research_candidates,research_candidate_events,research_jobs,research_results,
    research_trials,research_shadows,research_shadow_marks,research_staging_runs,research_promotions TO asl_api,asl_agent,asl_research;
GRANT SELECT ON agent_tool_completions,source_refresh_requests,source_fetches,evidence_items,agent_triggers TO asl_source;
GRANT INSERT ON source_refresh_requests,research_hypotheses,research_candidates,research_jobs,research_trials,
    research_promotions,agent_triggers,research_candidate_events,agent_tool_completions TO asl_agent;
GRANT INSERT ON source_refresh_requests TO asl_api;
GRANT INSERT ON source_refresh_requests,source_fetches,evidence_items,agent_triggers,agent_tool_completions TO asl_source;
GRANT INSERT ON research_datasets,research_candidate_events,research_jobs,research_results,research_trials,
    research_shadows,research_shadow_marks,research_staging_runs,agent_triggers,agent_tool_completions TO asl_research;
GRANT UPDATE (state,version,outcome,updated_at) ON source_refresh_requests TO asl_source;
GRANT UPDATE (state,version,outcome) ON agent_triggers TO asl_agent;
GRANT UPDATE (state,version) ON research_promotions TO asl_agent;
GRANT UPDATE (state,version,lease_owner,lease_epoch,lease_until,resources,outcome,started_at,completed_at)
    ON research_jobs TO asl_research;
GRANT UPDATE (version,owner_cancel_request) ON research_jobs TO asl_api;
GRANT UPDATE (state,version,last_available_at,prefix_fingerprint,detail) ON research_shadows TO asl_research;
GRANT UPDATE (version,owner_stop_request) ON research_shadows TO asl_api;
GRANT USAGE,SELECT ON SEQUENCE source_refresh_requests_seq_seq TO asl_api,asl_agent,asl_source;
GRANT USAGE,SELECT ON SEQUENCE agent_triggers_seq_seq TO asl_source,asl_agent,asl_research;
GRANT USAGE,SELECT ON SEQUENCE research_candidate_events_seq_seq,research_jobs_seq_seq,research_trials_seq_seq TO asl_agent,asl_research;
"""
