"""ExecPlan 0046: leaner agents (generation 11).

Revision ID: 0028_leaner_trader
Revises: 0027_result_checks

ExecPlan 0046 section 4. Additive; nothing of the futures engine, its account, its positions, the twins, the scores or
the result checks changes, and the engine reads none of it. The guard resolves names under a fixed search path.

- The futures decision guard also accepts generation 11's trader ``FUTURES_DECISION_V5``, whose decisions carry a
  forecast as generations 9 and 10's do, and holds its rows to generation 10's rules under the same message: no
  ``NO_VIEW`` outside ``ABSTAIN`` and no view with it, no entry against its forecast, and no entry's stop under 2 ATR
  or time exit under 4 hours (the confidence, the fourth rule of the finish, is in the artifact only).
- Generation 11's agent definitions (frozen here, checked against the code).

Downgrade refuses once any generation-11 workflow exists or a runtime profile binds generation 11 (as 0026's);
otherwise it restores 0026's guard.
"""

import hashlib
import json

from alembic import op

revision = "0028_leaner_trader"
down_revision = "0027_result_checks"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("FUTURES_DECISION_V5",)

# Generated from app.agents.definitions_v11 (python -m app.agents.definitions_v11); tests/test_m11_leaner_trader.py
# compares.
AGENT_SEED_LINES_V11 = r"""
["TOOL_CATALOG_V11", "TOOL_CATALOG", 11, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V11\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v11 and ExecPlan 0046 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: an action with only the choices it takes from the policy's sets, advice_use, expected_move and uncertainty_level, under the rules of the trader's prompt; an entry they do not allow is refused. The server records the context it was made in; the engine computes every price, quantity, stop level, fee and margin, and reads no forecast, note or score.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":11}", "c36fcd05c3bf37a90b7e9d00a1327051b429518b07684633bd1951611a8143e7"]
["ROLE_GRANTS_V11", "ROLE_GRANTS", 11, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V11\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v11 and ExecPlan 0046 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[\"FUTURES_DECISION_V5\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":11}", "2787e3e4997f01e9ef26cc11b5c0c3b611c2c1f98d2aac484ef3be00a5945379"]
["TEMPLATES_V11", "TEMPLATES", 11, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V11\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_THEN_DECISION_REVIEW_THEN_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v11 and ExecPlan 0046 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V5\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60,\"read_by\":\"THE_SCORECARD_ONLY; NO_CODE_THAT_TRADES\"},\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_FILL_OR_SHARP_MOVE\"},\"prompt\":\"TRADER_PROMPT_M11_V5\",\"prompt_layout\":{\"job_context\":\"COMPACT_JSON\",\"output_schema\":\"ONLY_AS_THE_STRUCTURED_OUTPUT_FORMAT\"},\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V4\",\"role\":\"COORDINATOR\",\"schedule\":{\"bar\":\"EVERY_FINISHED_15M_BAR\",\"coalescing\":\"A_TRIGGER_IS_COVERED_BY_ANY_DECISION_STARTED_AFTER_ITS_EVENT\",\"fill\":\"RIGHT_AFTER_EACH_FILL\",\"open_at_once\":1,\"sharp_move\":\"A_MOVE_OF_MORE_THAN_THE_POLICY'S_ATR_MULTIPLE_WITHIN_ITS_WINDOW\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"scores\":{\"count\":8,\"fields\":[\"at\",\"action\",\"expected_move\",\"uncertainty_level\",\"call\",\"label\",\"reason\",\"move_1h_percent\",\"long_net_percent\",\"short_net_percent\"],\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; NOT_A_RULE\",\"per_window\":\"THE_1H_DIRECTION_CALLS_OVERALL_BY_CONFIDENCE_AND_BY_TREND_1H_AND_THE_BASE_RATE\",\"shown\":\"THE_NEWEST_DECISIONS_WITH_A_1H_SCORE_RECORDED_BY_THE_CUTOFF\",\"windows\":\"THE_LAST_24H_AND_7D_AS_OF_THE_CUTOFF\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"}},\"version\":11}", "0f2a41459fdc17f73e6c1793fecd8336bb2ad84f408acce136669f0c59653c09"]
["BUDGETS_V11", "BUDGETS", 11, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V11\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V5\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0044 section 4.3; ExecPlan 0046 section 4.3\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V5\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":11}", "0ac272a2a847521ad762a3e2fd75df0d40c4e7bb25410ab914dbf0d1f22c90df"]
["TRADER_PROMPT_M11_V5", "PROMPT", 5, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V5\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"dfe7c0c865d7d2c9af9fba9775090797609b694f35bf0a734989aabd497189fe\",\"source\":\"services/agent-runner/prompts/m11/trader.v5.md\",\"status\":\"CODE_OWNED\",\"version\":5}", "85b553f4a50c99e987f6f86429826731695f439d5b53772d2d4f549b74dd1e32"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-11 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V11.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-11 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0022's futures decision guard as 0026 left it, which also accepts generation 11's trader and holds its rows to
# generation 10's rules. Downgrade restores 0026's text exactly.
DECISION_GUARD = """
CREATE OR REPLACE FUNCTION asl_futures_decision_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a futures decision comes only from the trader'; END IF;
    SELECT template_id, purpose, state INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.template_id {templates} OR w.purpose <> 'DECISION' OR w.state <> 'RUNNING' THEN
        RAISE EXCEPTION 'a futures decision needs its running futures decision workflow'; END IF;{forecast}
    RETURN NEW;
END $$;
"""
TRADERS_V4 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4')"
TRADERS_V5 = ("NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4',"
              "'FUTURES_DECISION_V5')")
FORECAST_V4 = """
    IF (w.template_id IN ('FUTURES_DECISION_V3','FUTURES_DECISION_V4')) <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9 and 10''s traders and no other'; END IF;
    IF w.template_id = 'FUTURES_DECISION_V4' AND (
            (NEW.expected_move = 'NO_VIEW') <> (NEW.action = 'ABSTAIN')
            OR (NEW.action = 'ENTER_LONG' AND NEW.expected_move <> 'UP')
            OR (NEW.action = 'ENTER_SHORT' AND NEW.expected_move <> 'DOWN')
            OR (NEW.action IN ('ENTER_LONG','ENTER_SHORT')
                AND (NEW.stop_multiple IS NULL OR NEW.stop_multiple NOT IN (2.0, 3.0)
                     OR NEW.max_hold_hours IS NULL OR NEW.max_hold_hours NOT IN (4, 12, 24)))) THEN
        RAISE EXCEPTION 'a generation-10 decision has a view unless it abstains and enters only with it, 2 or 3 ATR, 4 h or more'; END IF;"""
FORECAST_V5 = """
    IF (w.template_id IN ('FUTURES_DECISION_V3','FUTURES_DECISION_V4','FUTURES_DECISION_V5'))
            <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9 to 11''s traders and no other'; END IF;
    IF w.template_id IN ('FUTURES_DECISION_V4','FUTURES_DECISION_V5') AND (
            (NEW.expected_move = 'NO_VIEW') <> (NEW.action = 'ABSTAIN')
            OR (NEW.action = 'ENTER_LONG' AND NEW.expected_move <> 'UP')
            OR (NEW.action = 'ENTER_SHORT' AND NEW.expected_move <> 'DOWN')
            OR (NEW.action IN ('ENTER_LONG','ENTER_SHORT')
                AND (NEW.stop_multiple IS NULL OR NEW.stop_multiple NOT IN (2.0, 3.0)
                     OR NEW.max_hold_hours IS NULL OR NEW.max_hold_hours NOT IN (4, 12, 24)))) THEN
        RAISE EXCEPTION 'a generation-10 decision has a view unless it abstains and enters only with it, 2 or 3 ATR, 4 h or more'; END IF;"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V5)
               .replace("{forecast}", FORECAST_V5))
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 11 by hash would bind definitions that no longer exist (as 0026's).
    generation11 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        f"SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation11})"
    ).scalar_one()
    if held:
        raise RuntimeError("generation-11 records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-11 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V4)
               .replace("{forecast}", FORECAST_V4))
