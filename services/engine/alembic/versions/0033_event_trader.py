"""ExecPlan 0053: the trader every four hours and on events (generation 14).

Revision ID: 0033_event_trader
Revises: 0032_ai_backtest

ExecPlan 0053 section 4. Additive; nothing of the futures engine, its account, its positions, its policy, the twins,
the scores' definition or the result checks changes, and the engine reads none of it. The guard resolves names under a
fixed search path.

- A futures decision's ``trigger`` may also be one of generation 14's moments (``BAR_4H``, ``TRADE_CLOSED``, ``MOVE``,
  ``RANGE_BREAK``, ``FUNDING_JUMP``), on ``futures_decisions`` and on the scores' copy of it
  (``futures_decision_scores.trigger``); the column keeps its type, since every kind fits its 12 characters.
- The futures decision guard also accepts generation 14's trader ``FUTURES_DECISION_V6``, whose decisions carry a
  forecast as generations 9 to 11's do, and holds its rows to generation 10's rules under the same message.
- Generation 14's agent definitions (frozen here, checked against the code).

Downgrade refuses once any generation-14 workflow exists or a runtime profile binds generation 14 (as 0028's);
otherwise it restores 0028's guard and the two checks.
"""

import hashlib
import json

from alembic import op

revision = "0033_event_trader"
down_revision = "0032_ai_backtest"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("FUTURES_DECISION_V6",)
# The trigger kinds as 0020 and 0024 left them, and what this migration adds.
TRIGGERS = ("BAR", "FILL", "SHARP_MOVE")
TRIGGERS_ADDED = ("BAR_4H", "TRADE_CLOSED", "MOVE", "RANGE_BREAK", "FUNDING_JUMP")
# The two checks, by the names PostgreSQL gave their column constraints.
CHECKS = (("futures_decisions", "futures_decisions_trigger_check"),
          ("futures_decision_scores", "futures_decision_scores_trigger_check"))

# Generated from app.agents.definitions_v14 (python -m app.agents.definitions_v14); tests/test_m11_event_trader.py
# compares.
AGENT_SEED_LINES_V14 = r"""
["TOOL_CATALOG_V14", "TOOL_CATALOG", 14, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V14\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v14 and ExecPlan 0053 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: an action with only the choices it takes from the policy's sets, advice_use, expected_move and uncertainty_level, under the rules of the trader's prompt; an entry they do not allow is refused. The server records the context it was made in; the engine computes every price, quantity, stop level, fee and margin, and reads no forecast, note or score.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":14}", "62f0cf44a72b845c56f11f4c3d063a4484d59bab261f85e72dc53c8325458f08"]
["ROLE_GRANTS_V14", "ROLE_GRANTS", 14, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V14\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v14 and ExecPlan 0053 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[\"FUTURES_DECISION_V6\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":14}", "235eea3c0c29275eabf5515c1023eb827049d3dccc74714a0ea9f2249f36d2c9"]
["TEMPLATES_V14", "TEMPLATES", 14, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V14\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_THEN_DECISION_REVIEW_THEN_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v14 and ExecPlan 0053 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V6\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60,\"read_by\":\"THE_SCORECARD_ONLY; NO_CODE_THAT_TRADES\"},\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_4H_OR_AN_EVENT\"},\"prompt\":\"TRADER_PROMPT_M11_V6\",\"prompt_layout\":{\"job_context\":\"COMPACT_JSON\",\"output_schema\":\"ONLY_AS_THE_STRUCTURED_OUTPUT_FORMAT\"},\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V5\",\"role\":\"COORDINATOR\",\"schedule\":{\"at\":\"A_FINISHED_15M_BAR_ONCE_ITS_LAST_1M_CANDLE_IS_FINAL_WITHIN_THE_POLICY'S_DECISION_MAX_AGE\",\"base\":{\"every_hours\":4,\"from_utc\":\"00:00\",\"late_up_to_seconds\":3600},\"coalescing\":\"A_FINISHED_BAR_IS_COVERED_BY_ANY_DECISION_STARTED_AT_OR_AFTER_ITS_CLOSE; A_LATE_MOMENT_BY_ANY_DECISION_STARTED_AT_OR_AFTER_IT\",\"counted\":\"THIS_TEMPLATE'S_DECISIONS_ONLY; THE_POLICY'S_DECISIONS_A_DAY_COUNT_EVERY_TRADER'S\",\"events\":{\"FUNDING_JUMP\":{\"mark_max_age_seconds\":60,\"step\":\"0.0001\",\"when\":\"THE_FUNDING_RATE_OF_THE_NEWEST_MARK_AT_THE_BAR'S_CLOSE_MOVED_BY_AT_LEAST_THE_STEP_FROM_THE_NEWEST_MARK'S_WHEN_THE_LAST_DECISION_STARTED\"},\"MOVE\":{\"atr_multiple\":\"4\",\"when\":\"THE_BAR'S_CLOSE_IS_AT_LEAST_THE_MULTIPLE_X_THE_15M_ATR14_AT_IT_FROM_THE_CLOSE_OF_THE_BAR_ENDED_AT_OR_BEFORE_THE_LAST_DECISION_STARTED\"},\"RANGE_BREAK\":{\"hours\":24,\"late_up_to_seconds\":900,\"when\":\"A_1H_CANDLE_CLOSED_ABOVE_THE_HIGHEST_HIGH_OR_BELOW_THE_LOWEST_LOW_OF_THE_COMPLETE_1H_CANDLES_BEFORE_IT_AND_THE_HOUR_BEFORE_IT_DID_NOT_IN_THAT_DIRECTION\"},\"TRADE_CLOSED\":{\"late_up_to_seconds\":3600,\"when\":\"THE_ENTRY_COOLDOWN_AFTER_THE_LAST_CLOSED_POSITION_ENDED_AND_THE_ACCOUNT_IS_FLAT\"}},\"id\":\"EVERY_4H_AND_EVENTS_V1\",\"missing_data\":\"AN_EVENT_WITHOUT_ITS_CANDLES_ATR_OR_FRESH_MARKS_IS_NOT_DUE; THE_4H_DECISION_STILL_IS\",\"named\":{\"order\":[\"BAR_4H\",\"TRADE_CLOSED\",\"MOVE\",\"RANGE_BREAK\",\"FUNDING_JUMP\"],\"rule\":\"THE_FIRST_DUE_NAMES_THE_DECISION; THE_OTHERS_DUE_ARE_LISTED_AS_ALSO\"},\"not_started\":[\"AT_EVERY_FINISHED_15M_BAR\",\"RIGHT_AFTER_A_FILL\",\"ON_THE_POLICY'S_SHARP_MOVE\"],\"open_at_once\":1,\"per_utc_day\":32,\"protection\":\"THE_ENGINE'S_STOP_TAKE_PROFIT_TIME_EXIT_AND_LIQUIDATION_EVERY_SECOND_WHATEVER_THE_SCHEDULE\",\"shown\":\"THE_CONTEXT'S_SCHEDULE_BLOCK: THE_NEXT_4H_DECISION_AND_WHAT_WOULD_START_ONE_SOONER\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"scores\":{\"count\":8,\"fields\":[\"at\",\"action\",\"expected_move\",\"uncertainty_level\",\"call\",\"label\",\"reason\",\"move_1h_percent\",\"long_net_percent\",\"short_net_percent\"],\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; NOT_A_RULE\",\"per_window\":\"THE_1H_DIRECTION_CALLS_OVERALL_BY_CONFIDENCE_AND_BY_TREND_1H_AND_THE_BASE_RATE\",\"shown\":\"THE_NEWEST_DECISIONS_WITH_A_1H_SCORE_RECORDED_BY_THE_CUTOFF\",\"windows\":\"THE_LAST_24H_AND_7D_AS_OF_THE_CUTOFF\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"}},\"version\":14}", "a4378f342a3e955df930309042aae890ca9ed39fdf61c0235f6d07cb13180284"]
["BUDGETS_V14", "BUDGETS", 14, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V14\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V6\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0046 section 4.3; ExecPlan 0053 section 4.1\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V6\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":14}", "f7695ae083bd4327c97c5b304b61094ef7006beaf09ca9ba198666999d37dd75"]
["TRADER_PROMPT_M11_V6", "PROMPT", 6, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V6\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"7843b2d6a6b7123d1a9b21eadb1884cec5c976541d6761abdd5dc668a7f5d27d\",\"source\":\"services/agent-runner/prompts/m11/trader.v6.md\",\"status\":\"CODE_OWNED\",\"version\":6}", "6da50a0329cd633f8722a97a68c8e0a168a6a30596a8416021a66046d68cbbb6"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-14 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V14.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-14 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0028's futures decision guard, which also accepts generation 14's trader and holds its rows to generation 10's rules.
# Downgrade restores 0028's text exactly.
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
TRADERS_V5 = ("NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4',"
              "'FUTURES_DECISION_V5')")
TRADERS_V6 = ("NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4',"
              "'FUTURES_DECISION_V5','FUTURES_DECISION_V6')")
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
FORECAST_V6 = """
    IF (w.template_id IN ('FUTURES_DECISION_V3','FUTURES_DECISION_V4','FUTURES_DECISION_V5','FUTURES_DECISION_V6'))
            <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9 to 11''s traders and generation 14''s, and no other'; END IF;
    IF w.template_id IN ('FUTURES_DECISION_V4','FUTURES_DECISION_V5','FUTURES_DECISION_V6') AND (
            (NEW.expected_move = 'NO_VIEW') <> (NEW.action = 'ABSTAIN')
            OR (NEW.action = 'ENTER_LONG' AND NEW.expected_move <> 'UP')
            OR (NEW.action = 'ENTER_SHORT' AND NEW.expected_move <> 'DOWN')
            OR (NEW.action IN ('ENTER_LONG','ENTER_SHORT')
                AND (NEW.stop_multiple IS NULL OR NEW.stop_multiple NOT IN (2.0, 3.0)
                     OR NEW.max_hold_hours IS NULL OR NEW.max_hold_hours NOT IN (4, 12, 24)))) THEN
        RAISE EXCEPTION 'a generation-10 decision has a view unless it abstains and enters only with it, 2 or 3 ATR, 4 h or more'; END IF;"""


def _checks(triggers) -> None:
    for table, name in CHECKS:
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {name}, "
                   f"ADD CONSTRAINT {name} CHECK (trigger IN {_quoted(triggers)})")


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    _checks((*TRIGGERS, *TRIGGERS_ADDED))
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V6)
               .replace("{forecast}", FORECAST_V6))
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 14 by hash would bind definitions that no longer exist (as 0028's); a
    # generation-14 workflow is the only writer of the added trigger kinds.
    generation14 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        f"SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation14}) "
        f"+ (SELECT count(*) FROM futures_decisions WHERE trigger IN {_quoted(TRIGGERS_ADDED)})"
    ).scalar_one()
    if held:
        raise RuntimeError("generation-14 records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-14 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V5)
               .replace("{forecast}", FORECAST_V5))
    _checks(TRIGGERS)
