"""M10 update 1: the daily coin scan's records, and generation 5 of the agent definitions (the coin note).

Revision ID: 0015_m10_coins
Revises: 0014_m9_agents

ExecPlan 0033 section 5.1. Additive.

- coin_scans, coin_scan_entries and coin_daily_bars: what the daily scan of Binance's spot listing
  found (app.coins). The source fetcher's identity (asl_source) writes them; the agent worker and the API
  read the scans and their entries (nothing of theirs reads the bars). Every row is append-only. A scan, a rank or a bar is research data: nothing here adds a coin to
  trading, a quote, a mark or a fill.
- The seven generation-5 documents, frozen below and mirrored by app.agents.definitions_v5: step schema v4,
  tool catalog v5, role grants v5, templates v5 (COIN_NOTE_V1 and its review COIN_NOTE_REVIEW_V1),
  budgets v5 and the analyst's and the evaluator's M10 prompts. The worker refuses to start unless every stored
  row equals the code (app.agents.worker), and the runtime profile binds them by hash; no operating policy
  names them.
- COIN_NOTE joins the workflow purposes and the artifact kinds. The note's review has purpose REVIEW.

Downgrade refuses while a scan, a coin-note workflow or a coin note exists, then restores the checks, drops the
three tables and removes the seven rows.
"""

import hashlib
import json

from alembic import op

revision = "0015_m10_coins"
down_revision = "0014_m9_agents"
branch_labels = None
depends_on = None

AGENT_SEED_LINES_V5 = r"""
["AGENT_STEP_SCHEMA_V4", "AGENT_STEP_SCHEMA", 4, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V4\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"assessment\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"expiry_hours\":{\"type\":\"integer\"},\"hypotheses\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"statement\",\"cites\",\"invalidation\"],\"type\":\"object\"},\"type\":\"array\"},\"missing_evidence\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"observations\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"kind\":{\"enum\":[\"OBSERVATION\",\"CALCULATION\"],\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"kind\",\"statement\",\"cites\"],\"type\":\"object\"},\"type\":\"array\"},\"research_question\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"type\":\"array\"},\"uncertainty\":{\"additionalProperties\":false,\"properties\":{\"level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"reasons\":{\"type\":\"string\"}},\"required\":[\"level\",\"reasons\"],\"type\":\"object\"}},\"required\":[\"symbols\",\"summary\",\"observations\",\"hypotheses\",\"uncertainty\",\"missing_evidence\",\"expiry_hours\",\"research_question\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"coin_note\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One note on the coin under params.coin. Its figures are in the job context; cite params.coin.scan_id.\",\"properties\":{\"hypotheses\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"statement\",\"cites\",\"invalidation\"],\"type\":\"object\"},\"type\":\"array\"},\"label\":{\"enum\":[\"WORTH_WATCHING\",\"NOT_NOW\",\"RULE_OUT\"],\"type\":\"string\"},\"observations\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"kind\":{\"enum\":[\"OBSERVATION\",\"CALCULATION\"],\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"kind\",\"statement\",\"cites\"],\"type\":\"object\"},\"type\":\"array\"},\"rule_out_if\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"summary\":{\"type\":\"string\"},\"symbol\":{\"type\":\"string\"},\"uncertainty\":{\"additionalProperties\":false,\"properties\":{\"level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"reasons\":{\"type\":\"string\"}},\"required\":[\"level\",\"reasons\"],\"type\":\"object\"},\"unknowns\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"worth_trading_if\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"}},\"required\":[\"symbol\",\"summary\",\"observations\",\"hypotheses\",\"uncertainty\",\"unknowns\",\"worth_trading_if\",\"rule_out_if\",\"label\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"owner_review_requested\":{\"type\":\"boolean\"},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"action\":{\"enum\":[\"ENTER\",\"EXIT\",\"CANCEL_ENTRY\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"intent_id\":{\"type\":[\"string\",\"null\"]},\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"EVIDENCE_SUPPORTS_ACTION\",\"INSUFFICIENT_EVIDENCE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"REVIEW_NOT_ACCEPTABLE\",\"LIMIT_OR_COOLDOWN\",\"PROTECT_POSITION\",\"NO_CHANGE_NEEDED\",\"REFUSED_BY_APPLICATION\",\"OTHER\"],\"type\":\"string\"},\"symbol\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"}},\"required\":[\"symbol\",\"action\",\"intent_id\",\"reason_code\",\"note\"],\"type\":\"object\"},\"type\":\"array\"}},\"required\":[\"summary\",\"symbols\",\"owner_review_requested\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"promotion\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_id\":{\"type\":\"string\"},\"candidate_sha256\":{\"type\":\"string\"},\"evidence_refs\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"rationale\":{\"type\":\"string\"}},\"required\":[\"candidate_id\",\"candidate_sha256\",\"evidence_refs\",\"rationale\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"research_proposal\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_ids\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"hypothesis_id\":{\"type\":\"string\"},\"limitations\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"nominated_candidate_id\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"}},\"required\":[\"hypothesis_id\",\"summary\",\"candidate_ids\",\"nominated_candidate_id\",\"cites\",\"limitations\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"review\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiencies\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiency_codes\":{\"items\":{\"enum\":[\"INSUFFICIENT_SAMPLE\",\"DATA_GAPS\",\"INTEGRITY_FAILURE\",\"COST_UNCERTAINTY\",\"HISTORICAL_CONTAMINATION\",\"MISSING_BASELINE\",\"INCOMPLETE_TEST_SET\",\"UNSUPPORTED_CLAIM\"],\"type\":\"string\"},\"type\":\"array\"},\"results\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"result_ref\":{\"type\":\"string\"},\"sha256\":{\"type\":\"string\"}},\"required\":[\"result_ref\",\"sha256\"],\"type\":\"object\"},\"type\":\"array\"},\"review_type\":{\"enum\":[\"ASSESSMENT_REVIEW\",\"CANDIDATE_REVIEW\",\"INTENT_REVIEW\",\"OUTCOME_REVIEW\",\"COIN_NOTE_REVIEW\"],\"type\":\"string\"},\"supported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\",\"intent\",\"outcome\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"target_artifact_id\":{\"type\":\"string\"},\"target_sha256\":{\"type\":\"string\"},\"unsupported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\",\"intent\",\"outcome\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"verdict\":{\"enum\":[\"ACCEPTABLE\",\"NEEDS_EVIDENCE\",\"REJECT\"],\"type\":\"string\"}},\"required\":[\"review_type\",\"target_artifact_id\",\"target_sha256\",\"verdict\",\"supported_claims\",\"unsupported_claims\",\"deficiencies\",\"cites\",\"results\",\"deficiency_codes\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"assessment\",\"review\",\"research_proposal\",\"promotion\",\"decision\",\"coin_note\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v4\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"artifact_id\":{\"type\":[\"string\",\"null\"]},\"as_of\":{\"type\":[\"string\",\"null\"]},\"candidate\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One flat CANDIDATE_GRAMMAR_V1 declaration. Operators, comparisons and domains are in the job context.\",\"properties\":{\"entry\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":\"array\"},\"exit\":{\"additionalProperties\":false,\"properties\":{\"atr_period\":{\"type\":\"integer\"},\"max_hold_hours\":{\"type\":\"integer\"},\"signal\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":[\"array\",\"null\"]},\"stop_multiple\":{\"type\":\"string\"}},\"required\":[\"atr_period\",\"stop_multiple\",\"max_hold_hours\",\"signal\"],\"type\":\"object\"},\"grammar_version\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"timeframe\":{\"type\":\"string\"},\"warmup_bars\":{\"type\":\"integer\"}},\"required\":[\"grammar_version\",\"symbols\",\"timeframe\",\"warmup_bars\",\"entry\",\"exit\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"candidate_id\":{\"type\":[\"string\",\"null\"]},\"dataset_id\":{\"type\":[\"string\",\"null\"]},\"experiment_id\":{\"type\":[\"string\",\"null\"]},\"feature_ids\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"filters\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"name\":{\"type\":\"string\"},\"value\":{\"type\":\"integer\"}},\"required\":[\"name\",\"value\"],\"type\":\"object\"},\"type\":[\"array\",\"null\"]},\"hypothesis\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"dataset_id\":{\"type\":\"string\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"dataset_id\",\"statement\",\"invalidation\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"hypothesis_id\":{\"type\":[\"string\",\"null\"]},\"intent\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One draft. Choices only from the policy's sets in the job context; never a price, quantity or level.\",\"properties\":{\"action\":{\"enum\":[\"ENTER\",\"EXIT\",\"CANCEL_ENTRY\",\"TIGHTEN_STOP\"],\"type\":\"string\"},\"basis_ref\":{\"type\":[\"string\",\"null\"]},\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"entry_basis\":{\"enum\":[\"ASSESSMENT\",\"CANDIDATE\",null],\"type\":[\"string\",\"null\"]},\"expiry_minutes\":{\"type\":\"integer\"},\"exposure_fraction\":{\"type\":[\"string\",\"null\"]},\"invalidation\":{\"type\":\"string\"},\"max_hold_hours\":{\"type\":[\"integer\",\"null\"]},\"position_id\":{\"type\":[\"string\",\"null\"]},\"rationale\":{\"type\":\"string\"},\"stop_multiple\":{\"type\":[\"string\",\"null\"]},\"symbol\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"tightening\":{\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"symbol\",\"position_id\",\"expiry_minutes\",\"exposure_fraction\",\"stop_multiple\",\"max_hold_hours\",\"tightening\",\"entry_basis\",\"basis_ref\",\"cites\",\"rationale\",\"invalidation\",\"uncertainty_level\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"intent_id\":{\"type\":[\"string\",\"null\"]},\"limit\":{\"type\":[\"integer\",\"null\"]},\"pause_cites\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"pause_reason\":{\"enum\":[\"EVIDENCE_CONFLICT\",\"DATA_QUALITY\",\"MARKET_DISLOCATION\",\"OUTCOME_CONCERN\",null],\"type\":[\"string\",\"null\"]},\"query\":{\"type\":[\"string\",\"null\"]},\"review_id\":{\"type\":[\"string\",\"null\"]},\"search_scope\":{\"enum\":[\"SOURCES\",\"ARTIFACTS\",null],\"type\":[\"string\",\"null\"]},\"source_id\":{\"type\":[\"string\",\"null\"]},\"symbol\":{\"type\":[\"string\",\"null\"]},\"view\":{\"enum\":[\"MARKET\",\"PORTFOLIO\",\"ACCOUNT\",null],\"type\":[\"string\",\"null\"]},\"window_hours\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"view\",\"as_of\",\"symbol\",\"feature_ids\",\"window_hours\",\"artifact_id\",\"search_scope\",\"query\",\"source_id\",\"filters\",\"limit\",\"hypothesis_id\",\"hypothesis\",\"candidate\",\"candidate_id\",\"dataset_id\",\"experiment_id\",\"intent\",\"intent_id\",\"review_id\",\"pause_reason\",\"pause_cites\"],\"type\":\"object\"},\"purpose\":{\"type\":\"string\"},\"tool_name\":{\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v4\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M10 tool catalog v5 and ExecPlan 0033 section 5.1\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":4}", "c0ee60a4118750e2f75d1cbaef125bb30627d8645191b4e5bd19ee29a57545b6"]
["TOOL_CATALOG_V5", "TOOL_CATALOG", 5, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V5\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M10 tool catalog v5 and ExecPlan 0033 section 5.1\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"artifact_id\"],\"description\":\"Reads one typed artifact in this workflow's scope, or one evidence item that a result of this workflow or an artifact in its scope returned. Any other ID is refused. What a role may not see is withheld: a tuning role gets only the verdict and deficiency codes of a review that consulted holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_artifact\"},{\"arguments\":[\"search_scope\",\"query\",\"source_id\",\"symbol\",\"limit\"],\"description\":\"ANALYST. Plain-term search of approved evidence. search_scope SOURCES returns at most 10 items of sources in force that were available by the job cutoff; ARTIFACTS returns references to earlier typed artifacts. source_id narrows a SOURCES search. In a coin note symbol must be null: the sources in force are filed under BTCUSDT and SOLUSDT, and every one of them is searched. Each returned item can be cited by its ID. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"search_evidence\"},{\"arguments\":[],\"description\":\"ANALYST only, through FINISH with finish.coin_note. Records an immutable CoinNote on the coin of params.coin; the server adds the scan's figures from the job's parameters.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_coin_note\"},{\"arguments\":[],\"description\":\"EVALUATOR only, through FINISH with finish.review. Records an immutable EvaluationReview of the coin note, bound to its exact hash.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_review\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":5}", "4f1cda4500188e9b208664b09f4e06e48ea53196374c8550eefc4784aa423668"]
["ROLE_GRANTS_V5", "ROLE_GRANTS", 5, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"read_artifact\",\"search_evidence\",\"record_coin_note\"],\"COORDINATOR\":[],\"EVALUATOR\":[\"read_artifact\",\"record_review\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V5\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M10 tool catalog v5 and ExecPlan 0033 section 5.1\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"COIN_NOTE_V1\"],\"COORDINATOR\":[],\"EVALUATOR\":[\"COIN_NOTE_REVIEW_V1\"],\"RESEARCHER\":[]},\"version\":5}", "dfb4a6f4a29c2a445e86f91de7b8eb7cd4d16b872a5d1a6ca2c0423a0e92e4d0"]
["TEMPLATES_V5", "TEMPLATES", 5, "CODE_OWNED", "{\"delegation\":\"NONE_MODEL_CHOSEN; FIXED_CHILD_ONLY\",\"id\":\"TEMPLATES_V5\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER\",\"DECISION\",\"PROMOTION\",\"BRIEF\",\"INVESTIGATION\",\"RESEARCH\",\"COIN_NOTE\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M10 tool catalog v5 and ExecPlan 0033 section 5.1\",\"status\":\"CODE_OWNED\",\"templates\":{\"COIN_NOTE_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"PARENT_CUTOFF\",\"parent\":\"COIN_NOTE_V1\",\"prompt\":\"EVALUATOR_PROMPT_M10_V1\",\"purpose\":\"REVIEW\",\"review_type\":\"COIN_NOTE_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_PARENT_FINISH\"},\"COIN_NOTE_V1\":{\"artifact\":\"COIN_NOTE\",\"child\":\"COIN_NOTE_REVIEW_V1\",\"citable\":\"THE_SCAN_ID_AND_WHAT_THIS_JOB_WAS_GIVEN\",\"cutoff\":\"FIXED_AT_START\",\"evidence\":\"THE_SOURCES_IN_FORCE_AND_EARLIER_ARTIFACTS; NO_NEW_SOURCE\",\"note_rule\":{\"label\":\"ENGINEERING_CHOICE_NOT_MEASURED\",\"max_scan_age_hours\":36,\"open_at_once\":1,\"order\":\"WATCHLIST_RANK\",\"renew_after_days\":7,\"retry_after_hours\":24,\"watchlist\":\"THE_NEWEST_SUCCEEDED_COIN_SCAN_NO_OLDER_THAN_MAX_SCAN_AGE\"},\"on_review\":\"NOTHING_STARTS; A_NOTE_ADDS_NO_COIN_TO_TRADING\",\"parameters\":{\"coin\":\"THE_WATCHLIST_ENTRY_AS_THE_SCAN_RECORDED_IT\",\"symbols\":\"NONE\"},\"prompt\":\"ANALYST_PROMPT_M10_V1\",\"purpose\":\"COIN_NOTE\",\"role\":\"ANALYST\",\"started_by\":[\"SYSTEM_ON_WATCHLIST\"]}},\"version\":5}", "f15227795074d23f64b384e8e159f7908a2bb9f690361cd5e25274d37193d068"]
["BUDGETS_V5", "BUDGETS", 5, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"COIN_NOTE\":3},\"final_output_max_bytes\":16384,\"handoff_depth\":1,\"id\":\"BUDGETS_V5\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"source\":\"ExecPlan 0033 section 5.1\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":7200,\"templates\":{\"COIN_NOTE_REVIEW_V1\":{\"max_model_steps\":4,\"max_tool_calls\":3,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":600},\"COIN_NOTE_V1\":{\"max_model_steps\":8,\"max_tool_calls\":6,\"wait_deadline_seconds\":3600,\"workflow_deadline_seconds\":1200}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":7200,\"version\":5}", "39364220ea14dbfab7f9e9b09512b892c053fb2cbbb32a74e79415a3c9ff76e2"]
["ANALYST_PROMPT_M10_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"ANALYST_PROMPT_M10_V1\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"5ea84bc463c2892477f569a0776c1f97b8bd05f261b6fb7ad428e05abb0453e9\",\"source\":\"services/agent-runner/prompts/m10/analyst.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "e47291979cce4ef3c6278c4cb91ceab1ff669d231c247d1d6d1a574d7730e384"]
["EVALUATOR_PROMPT_M10_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"EVALUATOR_PROMPT_M10_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"d55598400c96180a6a894cc7dffd6087662452c0a5dc96d09796bf9d469d7a28\",\"source\":\"services/agent-runner/prompts/m10/evaluator.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "f9ef775ae9f55c97b328dcbb0d5a36b29187beef5a68fac9ae62afe620080a5c"]
"""
KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("COIN_NOTE_V1", "COIN_NOTE_REVIEW_V1")
# The checks as migration 0009 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW")
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION")
ADDED = ("COIN_NOTE",)
TABLES = ("coin_scans", "coin_scan_entries", "coin_daily_bars")

SCHEMA = """
CREATE TABLE coin_scans (
    id uuid PRIMARY KEY,
    rules_id varchar(32) NOT NULL CHECK (rules_id = 'COIN_SCAN_V1'),
    rules_sha256 varchar(64) NOT NULL CHECK (rules_sha256 ~ '^[0-9a-f]{64}$'),
    started_at timestamptz NOT NULL,
    completed_at timestamptz NOT NULL,
    state varchar(16) NOT NULL CHECK (state IN ('SUCCEEDED','FAILED')),
    failure varchar(64),
    weight integer NOT NULL CHECK (weight >= 0),
    requests integer NOT NULL CHECK (requests >= 0),
    summary jsonb NOT NULL CHECK (jsonb_typeof(summary) = 'object'),
    CHECK ((state = 'FAILED') = (failure IS NOT NULL))
);
CREATE INDEX coin_scan_history ON coin_scans(started_at);
CREATE TABLE coin_scan_entries (
    scan_id uuid NOT NULL REFERENCES coin_scans(id),
    symbol varchar(20) NOT NULL CHECK (symbol ~ '^[A-Z0-9]{2,20}$'),
    base_asset varchar(20) NOT NULL,
    position integer NOT NULL CHECK (position >= 1),
    status varchar(16) NOT NULL CHECK (status IN ('WATCHLIST','LEFT_OUT')),
    rank smallint CHECK (rank BETWEEN 1 AND 8),
    reason varchar(32) CHECK (reason IN ('BTC_OR_SOL','STABLE_FIAT_OR_COMMODITY','WRAPPED_OR_STAKED','LEVERAGED_TOKEN','MISSING_FIELD','NOT_LISTED','NOT_TRADING','SPOT_NOT_ALLOWED','QUOTE_MISMATCH','NO_QUOTE','SPREAD_TOO_WIDE','BARS_UNAVAILABLE','TOO_FEW_DAILY_BARS','STABLE_PRICE','TRACKS_BTC_OR_SOL','BELOW_TOP_8')),
    figures jsonb NOT NULL CHECK (jsonb_typeof(figures) = 'object'),
    received jsonb NOT NULL CHECK (jsonb_typeof(received) = 'object'),
    PRIMARY KEY (scan_id, symbol),
    UNIQUE (scan_id, position),
    UNIQUE (scan_id, rank),
    CHECK ((status = 'WATCHLIST') = (rank IS NOT NULL)),
    CHECK ((status = 'LEFT_OUT') = (reason IS NOT NULL))
);
CREATE TABLE coin_daily_bars (
    symbol varchar(20) NOT NULL CHECK (symbol ~ '^[A-Z0-9]{2,20}$'),
    open_ms bigint NOT NULL CHECK (open_ms % 86400000 = 0),
    close_ms bigint NOT NULL,
    open numeric NOT NULL, high numeric NOT NULL, low numeric NOT NULL, close numeric NOT NULL,
    volume numeric NOT NULL CHECK (volume >= 0),
    quote_volume numeric NOT NULL CHECK (quote_volume >= 0),
    trades bigint NOT NULL CHECK (trades >= 0),
    received_at timestamptz NOT NULL,
    scan_id uuid NOT NULL REFERENCES coin_scans(id),
    PRIMARY KEY (symbol, open_ms),
    CHECK (close_ms = open_ms + 86399999),
    CHECK (low > 0 AND low <= open AND low <= close AND high >= open AND high >= close)
);
GRANT SELECT, INSERT ON coin_scans, coin_scan_entries, coin_daily_bars TO asl_source;
GRANT SELECT ON coin_scans, coin_scan_entries TO asl_agent, asl_api;
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    """The frozen generation-5 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V5.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KINDS:
            raise RuntimeError("frozen M10 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _checks(purposes, kinds):
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check")
    op.execute(f"ALTER TABLE agent_workflows ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(purposes)})")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check")
    op.execute(f"ALTER TABLE agent_artifacts ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(kinds)})")


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    op.execute(SCHEMA)
    for table in TABLES:
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    bind = op.get_bind()
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    _checks(PURPOSES + ADDED, ARTIFACT_KINDS + ADDED)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    if bind.exec_driver_sql(f"""
        SELECT (SELECT count(*) FROM coin_scans)
             + (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} OR purpose IN {_quoted(ADDED)})
             + (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ADDED)})
    """).scalar_one():
        raise RuntimeError("M10 coin records exist; downgrade refused; fix forward")
    _checks(PURPOSES, ARTIFACT_KINDS)
    for table in reversed(TABLES):
        op.execute(f"DROP TABLE {table}")
    # The definition store is immutable even for the migration role: relax only this trigger, inside this
    # transaction, and delete only the seven frozen rows, which nothing names (checked above).
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M10 agent definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
