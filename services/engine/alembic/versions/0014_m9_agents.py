"""M9 update 2: generation 4 of the agent definitions, and the PRICE_MOVE trigger family.

Revision ID: 0014_m9_agents
Revises: 0013_m9_news_feeds

ExecPlan 0032 section 5.2. Additive.

- The six generation-4 documents, frozen below and mirrored by ``app.agents.definitions_v4``: tool catalog v4,
  role grants v4, templates v4 (``EVENT_INVESTIGATION_V2`` and its review ``ASSESSMENT_REVIEW_V3``), budgets v4
  and the analyst's and the evaluator's M9 prompts. Generation 4 uses step schema v3 as migration 0009 seeded
  it. The worker refuses to start unless every stored row equals the code (``app.agents.worker``), and the
  runtime profile binds them by hash; no operating policy names them.
- ``PRICE_MOVE`` joins the trigger families (``app.agents.price_moves``).

Downgrade refuses while a generation-4 workflow or a ``PRICE_MOVE`` trigger exists, then restores the family
check and removes the six rows.
"""

import hashlib
import json

from alembic import op

revision = "0014_m9_agents"
down_revision = "0013_m9_news_feeds"
branch_labels = None
depends_on = None

AGENT_SEED_LINES_V4 = r"""
["TOOL_CATALOG_V4", "TOOL_CATALOG", 4, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V4\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M9 tool catalog v4 and ExecPlan 0032 section 5.2\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"view\",\"as_of\"],\"description\":\"view MARKET: the market-only least-data view at the job cutoff, as in catalog v2, and the scheduled releases of the calendar sources in force that start within 24 hours before or after the cutoff (newest revision of each event available by the cutoff, at most 12, nearest first, each an evidence item that can be opened and cited by its ID). A scheduled release is not its result. Any other view is refused.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"get_snapshot\",\"scheduled_releases\":{\"max_items\":12,\"order\":\"NEAREST_TO_THE_CUTOFF_FIRST\",\"revision\":\"NEWEST_AVAILABLE_BY_THE_CUTOFF\",\"sources\":\"IN_FORCE_ICALENDAR_V1\",\"window_hours\":24}},{\"arguments\":[\"symbol\",\"feature_ids\",\"window_hours\",\"as_of\"],\"description\":\"Registered features over finalized 1h candles for BTCUSDT or SOLUSDT, evaluated at the last finalized bar at or before as_of (default: the job cutoff). feature_ids: 1-6 registered IDs; window_hours: 1-168 (OHLCV_1H_V1: at most 72). Returns exact decimal strings with inputs, warm-up and quality.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_market_features\"},{\"arguments\":[\"artifact_id\"],\"description\":\"Reads one typed artifact in this workflow's scope, or one evidence item that a result of this workflow or an artifact in its scope returned. Any other ID is refused. What a role may not see is withheld: a tuning role gets only the verdict and deficiency codes of a review that consulted holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_artifact\"},{\"arguments\":[\"search_scope\",\"query\",\"source_id\",\"symbol\",\"limit\"],\"description\":\"ANALYST and RESEARCHER. Plain-term search of approved evidence. search_scope SOURCES returns at most 10 items of approved sources that were available by the job cutoff; ARTIFACTS returns references to earlier typed artifacts. source_id and symbol narrow a SOURCES search. Each returned item can be cited by its ID. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"search_evidence\"},{\"arguments\":[\"source_id\",\"filters\"],\"description\":\"ANALYST and RESEARCHER. Queues one fetch of a registered, approved source by its ID, with that source's typed integer filters. Never a URL, host or path. Returns ACCEPTED with a request reference; the workflow then waits and resumes with one completion.\",\"effect\":\"QUEUE_SOURCE_REFRESH\",\"finish_only\":false,\"name\":\"request_source_refresh\"},{\"arguments\":[\"experiment_id\"],\"description\":\"Reads one experiment or shadow by ID in the role's projection. A tuning role (ANALYST, RESEARCHER) reads screening results at or before its cutoff and never holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_experiment\"},{\"arguments\":[],\"description\":\"ANALYST only, through FINISH with finish.assessment. Records an immutable MarketAssessment; it may name one research question.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_assessment\"},{\"arguments\":[],\"description\":\"EVALUATOR only, through FINISH with finish.review. Records an immutable EvaluationReview of the investigation's assessment, bound to its exact hash.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_review\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":4}", "7aa1800d385b234ff24cad0c0543fb341a609757e8f4e684b73045a0b7bdd334"]
["ROLE_GRANTS_V4", "ROLE_GRANTS", 4, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\",\"QUEUE_SOURCE_REFRESH\"],\"grants\":{\"ANALYST\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"search_evidence\",\"request_source_refresh\",\"read_experiment\",\"record_assessment\"],\"COORDINATOR\":[],\"EVALUATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"read_experiment\",\"record_review\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V4\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M9 tool catalog v4 and ExecPlan 0032 section 5.2\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"EVENT_INVESTIGATION_V2\"],\"COORDINATOR\":[],\"EVALUATOR\":[\"ASSESSMENT_REVIEW_V3\"],\"RESEARCHER\":[]},\"version\":4}", "0e2c2cf9bace31bf42d7b17f22d36bd312d95f0290a83ddd27799bc43c613220"]
["TEMPLATES_V4", "TEMPLATES", 4, "CODE_OWNED", "{\"delegation\":\"NONE_MODEL_CHOSEN; FIXED_CHILD_ONLY\",\"id\":\"TEMPLATES_V4\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER\",\"DECISION\",\"PROMOTION\",\"BRIEF\",\"INVESTIGATION\",\"RESEARCH\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M9 tool catalog v4 and ExecPlan 0032 section 5.2\",\"status\":\"CODE_OWNED\",\"templates\":{\"ASSESSMENT_REVIEW_V3\":{\"artifact\":\"EVALUATION_REVIEW\",\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"PARENT_CUTOFF_AND_THE_ITEMS_ITS_REFRESH_DELIVERED\",\"parent\":\"EVENT_INVESTIGATION_V2\",\"prompt\":\"EVALUATOR_PROMPT_M9_V1\",\"purpose\":\"REVIEW\",\"review_type\":\"ASSESSMENT_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_PARENT_FINISH\"},\"EVENT_INVESTIGATION_V2\":{\"artifact\":\"MARKET_ASSESSMENT\",\"child\":\"ASSESSMENT_REVIEW_V3\",\"cutoff\":\"FIXED_AT_START; OWN_REFRESH_IS_DELIVERED_BY_ITS_COMPLETION_ONLY\",\"follow_on\":{\"budget\":\"DAILY_PARENT_WORKFLOWS_OF_GENERATIONS_1_AND_2\",\"context\":\"QUESTION_TEXT_WITHHELD_UNLESS_ITS_PROVENANCE_IS_AT_OR_BEFORE_THE_RESEARCH_CUTOFF\",\"template\":\"RESEARCH_V1\",\"when\":\"RESEARCH_QUESTION_NAMED_AND_REVIEW_NOT_REJECT\"},\"on_review\":\"ACCEPTABLE_RECORDS_AN_ASSESSMENT_READY_TRIGGER\",\"parameters\":{\"horizon_hours\":{\"maximum\":72,\"minimum\":1},\"symbols\":{\"items\":[\"BTCUSDT\",\"SOLUSDT\"],\"max_items\":1,\"min_items\":1,\"unique\":true}},\"price_trigger\":{\"atr_feature\":\"ATR14_1H_V1\",\"atr_multiple\":\"1\",\"checked\":\"AT_EACH_SCHEDULER_PASS_WHILE_THE_AGENTS_MAY_WORK; NOTHING_IS_CAUGHT_UP\",\"coalesce\":\"ONE_OPEN_PRICE_MOVE_INVESTIGATION_PER_SYMBOL\",\"cooldown_minutes\":60,\"horizon_hours\":24,\"label\":\"ENGINEERING_CHOICE_NOT_MEASURED\",\"max_per_symbol_per_utc_day\":4,\"mid\":\"HALF_THE_SUM_OF_BID_AND_ASK_OF_THE_NEWEST_RECORDED_QUOTE_VALID_AT_THAT_INSTANT\",\"rule\":\"ABS_MID_NOW_MINUS_MID_A_WINDOW_EARLIER_AT_LEAST_ATR_MULTIPLE_TIMES_THE_HOURLY_ATR\",\"symbols\":[\"BTCUSDT\",\"SOLUSDT\"],\"window_minutes\":15},\"prompt\":\"ANALYST_PROMPT_M9_V1\",\"purpose\":\"INVESTIGATION\",\"role\":\"ANALYST\",\"snapshot\":\"MARKET_VIEW_WITH_THE_SCHEDULED_RELEASES_24_HOURS_EITHER_SIDE_OF_THE_CUTOFF\",\"source_trigger\":{\"coalesce\":\"ONE_OPEN_INVESTIGATION_PER_SOURCE_AND_SYMBOL\",\"horizon_hours\":24,\"symbols\":\"THE_TRIGGER_SYMBOL\"},\"started_by\":[\"SOURCE_TRIGGER\",\"SYSTEM_ON_PRICE_MOVE\"]}},\"version\":4}", "c27928aff5e80e5e1777f35b50fa7fa49195ce6a46ca63045256de3b381b41e7"]
["BUDGETS_V4", "BUDGETS", 4, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"INVESTIGATION\":16},\"final_output_max_bytes\":16384,\"handoff_depth\":1,\"id\":\"BUDGETS_V4\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"source\":\"ExecPlan 0032 section 5.2\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":7200,\"templates\":{\"ASSESSMENT_REVIEW_V3\":{\"max_model_steps\":4,\"max_tool_calls\":3,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":600},\"EVENT_INVESTIGATION_V2\":{\"max_model_steps\":12,\"max_tool_calls\":10,\"wait_deadline_seconds\":3600,\"workflow_deadline_seconds\":1200}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":7200,\"version\":4}", "19bdcde33c11b365879efb899f8d0d7067729994b3ce9c866e1904b65e2f4198"]
["ANALYST_PROMPT_M9_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"ANALYST_PROMPT_M9_V1\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"4ba59226f18a654ef74ad6e9f3cc5cc65d7200b5c3964c6fa9910482ed778abe\",\"source\":\"services/agent-runner/prompts/m9/analyst.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "04fe43f608f2f134b6bfed3a1dd2a206a121c0d347e9ea3fd05b8b2fa91d4abb"]
["EVALUATOR_PROMPT_M9_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"EVALUATOR_PROMPT_M9_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"1def627ddfc21db222499f305297203f303705f37535afb5822c06bbafb5671d\",\"source\":\"services/agent-runner/prompts/m9/evaluator.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "479bc0a35de69e91f1d1f8d950eafc6c13cbcecc466345dddf3f9cabad90245d"]
"""
KINDS = ("TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("EVENT_INVESTIGATION_V2", "ASSESSMENT_REVIEW_V3")
# The trigger families as migration 0009 left them, and the one this migration adds.
FAMILIES = ("SOURCE_REVISION", "SCHEDULED_RESEARCH", "FOLLOW_ON", "BAR_CLOSE", "POSITION_EVENT", "ASSESSMENT_READY")
ADDED = ("PRICE_MOVE",)


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    """The frozen generation-4 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V4.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KINDS:
            raise RuntimeError("frozen M9 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _families(values):
    op.execute("ALTER TABLE agent_triggers DROP CONSTRAINT agent_triggers_family_check")
    op.execute(f"ALTER TABLE agent_triggers ADD CONSTRAINT agent_triggers_family_check CHECK (family IN {_quoted(values)})")


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    _families(FAMILIES + ADDED)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    if bind.exec_driver_sql(f"""
        SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)})
             + (SELECT count(*) FROM agent_triggers WHERE family IN {_quoted(ADDED)})
    """).scalar_one():
        raise RuntimeError("M9 agent records exist; downgrade refused; fix forward")
    _families(FAMILIES)
    # The definition store is immutable even for the migration role: relax only this trigger, inside this
    # transaction, and delete only the six frozen rows, which nothing names (checked above).
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M9 agent definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
