"""ExecPlan 0058: the event calendar (generation 19).

Revision ID: 0039_event_calendar
Revises: 0038_slow_trend

ExecPlan 0058 section 4. Additive; nothing of the futures engine, its account, its positions, its policy, the twins,
the scores' definition, the result checks or the backtests changes, and the engine reads none of it. The guard resolves
names under a fixed search path.

- A futures decision's ``trigger`` may also be ``RELEASE_OUT``, generation 19's look after a first-rank release's
  entry window, on ``futures_decisions`` and on the scores' copy of it (``futures_decision_scores.trigger``); the
  column keeps its type, since the kind fits its 12 characters.
- The futures decision guard also accepts generation 19's trader ``FUTURES_DECISION_V7``, whose decisions carry a
  forecast as generations 9 to 11's and 14's do, and holds its rows to generation 10's rules under the same message.
- Generation 19's agent definitions (frozen here, checked against the code), which carry the event calendar
  ``EVENT_CALENDAR_V1`` and the window ``EVENT_WINDOW_V1`` inside the trader's schedule.

Downgrade refuses once any generation-19 workflow exists, a runtime profile binds generation 19 or a decision names
``RELEASE_OUT`` (as 0033's); otherwise it restores 0033's guard and the two checks.
"""

import hashlib
import json

from alembic import op

revision = "0039_event_calendar"
down_revision = "0038_slow_trend"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("FUTURES_DECISION_V7",)
# The trigger kinds as 0033 left them, and what this migration adds.
TRIGGERS = ("BAR", "FILL", "SHARP_MOVE", "BAR_4H", "TRADE_CLOSED", "MOVE", "RANGE_BREAK", "FUNDING_JUMP")
TRIGGERS_ADDED = ("RELEASE_OUT",)
# The two checks, by the names PostgreSQL gave their column constraints.
CHECKS = (("futures_decisions", "futures_decisions_trigger_check"),
          ("futures_decision_scores", "futures_decision_scores_trigger_check"))

# Generated from app.agents.definitions_v19 (python -m app.agents.definitions_v19); tests/test_m11_event_calendar.py
# compares.
AGENT_SEED_LINES_V19 = r"""
["TOOL_CATALOG_V19", "TOOL_CATALOG", 19, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V19\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v19 and ExecPlan 0058 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: an action with only the choices it takes from the policy's sets, advice_use, expected_move and uncertainty_level, under the rules of the trader's prompt; an entry they do not allow is refused. The server records the context it was made in; the engine computes every price, quantity, stop level, fee and margin, and reads no forecast, note or score.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":19}", "8b03188f296da8ff934d5a33b0190958abd62b9925543c115c2a7ecc464add7b"]
["ROLE_GRANTS_V19", "ROLE_GRANTS", 19, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V19\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v19 and ExecPlan 0058 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[\"FUTURES_DECISION_V7\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":19}", "302326aba756df6e65f75592fa25ca13a961d4cd36658e18a6630910a2b7d378"]
["TEMPLATES_V19", "TEMPLATES", 19, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V19\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_THEN_DECISION_REVIEW_THEN_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v19 and ExecPlan 0058 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V7\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"finish_rules_added\":[\"ENTRY_IN_EVENT_WINDOW\"],\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60,\"read_by\":\"THE_SCORECARD_ONLY; NO_CODE_THAT_TRADES\"},\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_4H_OR_AN_EVENT\"},\"prompt\":\"TRADER_PROMPT_M11_V7\",\"prompt_layout\":{\"job_context\":\"COMPACT_JSON\",\"output_schema\":\"ONLY_AS_THE_STRUCTURED_OUTPUT_FORMAT\"},\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V6\",\"role\":\"COORDINATOR\",\"schedule\":{\"at\":\"A_FINISHED_15M_BAR_ONCE_ITS_LAST_1M_CANDLE_IS_FINAL_WITHIN_THE_POLICY'S_DECISION_MAX_AGE\",\"base\":{\"every_hours\":4,\"from_utc\":\"00:00\",\"late_up_to_seconds\":3600},\"calendar\":{\"bls\":{\"ahead_days\":60,\"behind_hours\":12,\"read\":\"THE_CALENDAR_SOURCES_IN_FORCE; EACH_EVENT'S_NEWEST_REVISION_AVAILABLE_BY_THE_CUTOFF; TITLE_EQUAL; STATUS_CANCELLED_LEFT_OUT\"},\"events\":{\"CPI\":{\"after_minutes\":45,\"name\":\"US CPI\",\"source\":\"CALENDAR_BLS_V1\",\"title\":\"Consumer Price Index\"},\"FED\":{\"after_minutes\":120,\"checked\":{\"on\":\"2026-11-09\",\"page\":\"https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm\",\"tentative\":\"UNTIL_THE_MEETING_BEFORE_EACH\"},\"eastern\":\"14:00 America/New_York\",\"name\":\"Fed decision\",\"source\":\"THIS_TABLE\",\"statements\":[{\"at\":\"2026-12-09T19:00:00Z\",\"date\":\"2026-12-09\"},{\"at\":\"2027-01-27T19:00:00Z\",\"date\":\"2027-01-27\"},{\"at\":\"2027-03-17T18:00:00Z\",\"date\":\"2027-03-17\"},{\"at\":\"2027-04-28T18:00:00Z\",\"date\":\"2027-04-28\"},{\"at\":\"2027-06-09T18:00:00Z\",\"date\":\"2027-06-09\"},{\"at\":\"2027-07-28T18:00:00Z\",\"date\":\"2027-07-28\"},{\"at\":\"2027-09-15T18:00:00Z\",\"date\":\"2027-09-15\"},{\"at\":\"2027-10-27T18:00:00Z\",\"date\":\"2027-10-27\"},{\"at\":\"2027-12-08T19:00:00Z\",\"date\":\"2027-12-08\"},{\"at\":\"2028-01-26T19:00:00Z\",\"date\":\"2028-01-26\"}]},\"JOBS\":{\"after_minutes\":30,\"name\":\"US jobs report\",\"source\":\"CALENDAR_BLS_V1\",\"title\":\"Employment Situation\"}},\"id\":\"EVENT_CALENDAR_V1\",\"label\":\"SCHEDULED_TIMES_FROM_THE_PUBLISHERS; NOT_RESULTS_OR_FORECASTS\",\"rank_2\":\"SHOWN_IN_RELEASES_AS_BEFORE; NO_WINDOW\",\"unscheduled\":\"THE_ENGINE'S_STOP_THE_SIZE_AND_THE_MOVE_TRIGGER\"},\"coalescing\":\"A_FINISHED_BAR_IS_COVERED_BY_ANY_DECISION_STARTED_AT_OR_AFTER_ITS_CLOSE; A_LATE_MOMENT_BY_ANY_DECISION_STARTED_AT_OR_AFTER_IT\",\"counted\":\"THIS_TEMPLATE'S_DECISIONS_ONLY; THE_POLICY'S_DECISIONS_A_DAY_COUNT_EVERY_TRADER'S\",\"events\":{\"FUNDING_JUMP\":{\"mark_max_age_seconds\":60,\"step\":\"0.0001\",\"when\":\"THE_FUNDING_RATE_OF_THE_NEWEST_MARK_AT_THE_BAR'S_CLOSE_MOVED_BY_AT_LEAST_THE_STEP_FROM_THE_NEWEST_MARK'S_WHEN_THE_LAST_DECISION_STARTED\"},\"MOVE\":{\"atr_multiple\":\"4\",\"when\":\"THE_BAR'S_CLOSE_IS_AT_LEAST_THE_MULTIPLE_X_THE_15M_ATR14_AT_IT_FROM_THE_CLOSE_OF_THE_BAR_ENDED_AT_OR_BEFORE_THE_LAST_DECISION_STARTED\"},\"RANGE_BREAK\":{\"hours\":24,\"late_up_to_seconds\":900,\"when\":\"A_1H_CANDLE_CLOSED_ABOVE_THE_HIGHEST_HIGH_OR_BELOW_THE_LOWEST_LOW_OF_THE_COMPLETE_1H_CANDLES_BEFORE_IT_AND_THE_HOUR_BEFORE_IT_DID_NOT_IN_THAT_DIRECTION\"},\"RELEASE_OUT\":{\"calendar\":\"EVENT_CALENDAR_V1\",\"late_up_to_seconds\":3600,\"when\":\"THE_FIRST_FINISHED_15M_BAR_AT_OR_AFTER_A_FIRST_RANK_RELEASE'S_WINDOW_ENDED\",\"window\":\"EVENT_WINDOW_V1\"},\"TRADE_CLOSED\":{\"late_up_to_seconds\":3600,\"when\":\"THE_ENTRY_COOLDOWN_AFTER_THE_LAST_CLOSED_POSITION_ENDED_AND_THE_ACCOUNT_IS_FLAT\"}},\"extends\":\"EVERY_4H_AND_EVENTS_V1\",\"id\":\"EVERY_4H_AND_EVENTS_V2\",\"missing_data\":\"AN_EVENT_WITHOUT_ITS_CANDLES_ATR_OR_FRESH_MARKS_IS_NOT_DUE; THE_4H_DECISION_STILL_IS\",\"named\":{\"order\":[\"BAR_4H\",\"TRADE_CLOSED\",\"RELEASE_OUT\",\"MOVE\",\"RANGE_BREAK\",\"FUNDING_JUMP\"],\"rule\":\"THE_FIRST_DUE_NAMES_THE_DECISION; THE_OTHERS_DUE_ARE_LISTED_AS_ALSO\"},\"not_started\":[\"AT_EVERY_FINISHED_15M_BAR\",\"RIGHT_AFTER_A_FILL\",\"ON_THE_POLICY'S_SHARP_MOVE\"],\"open_at_once\":1,\"per_utc_day\":32,\"protection\":\"THE_ENGINE'S_STOP_TAKE_PROFIT_TIME_EXIT_AND_LIQUIDATION_EVERY_SECOND_WHATEVER_THE_SCHEDULE\",\"shown\":\"THE_CONTEXT'S_SCHEDULE_BLOCK; ITS_EVENTS_BLOCK: THE_WINDOW_THE_NEXT_AND_THE_LAST_FIRST_RANK_RELEASE\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\",\"window\":{\"after_minutes\":{\"CPI\":45,\"FED\":120,\"JOBS\":30},\"before_minutes\":240,\"checked\":[\"AGAINST_THE_BOUND_CONTEXT\",\"AGAINST_THE_CALENDAR_AT_THE_FINISH\"],\"closed\":\"NO_NEW_ENTRY_FROM_THE_START_INCLUSIVE_TO_THE_END_EXCLUSIVE; WINDOWS_THAT_TOUCH_ARE_JOINED\",\"id\":\"EVENT_WINDOW_V1\",\"measured\":\"BINANCE_BTCUSDT_PERPETUAL_1M_2022_01_TO_2026_10; 57_CPI_57_JOBS_38_FED; ExecPlan 0058 section 2\",\"open\":[\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"position\":\"KEEPS_ITS_STOP_TAKE_PROFIT_TIME_EXIT_AND_LIQUIDATION\",\"refusal\":\"ENTRY_IN_EVENT_WINDOW\",\"unread\":\"A_CALENDAR_THAT_CANNOT_BE_READ_CLOSES_ENTRIES\"}},\"scores\":{\"count\":8,\"fields\":[\"at\",\"action\",\"expected_move\",\"uncertainty_level\",\"call\",\"label\",\"reason\",\"move_1h_percent\",\"long_net_percent\",\"short_net_percent\"],\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; NOT_A_RULE\",\"per_window\":\"THE_1H_DIRECTION_CALLS_OVERALL_BY_CONFIDENCE_AND_BY_TREND_1H_AND_THE_BASE_RATE\",\"shown\":\"THE_NEWEST_DECISIONS_WITH_A_1H_SCORE_RECORDED_BY_THE_CUTOFF\",\"windows\":\"THE_LAST_24H_AND_7D_AS_OF_THE_CUTOFF\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"}},\"version\":19}", "3de35b099b01fb78b5b42275c3b681283e278f3af5712864be4a860186036c51"]
["BUDGETS_V19", "BUDGETS", 19, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V19\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V7\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0046 section 4.3; ExecPlan 0053 section 4.1; ExecPlan 0058\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V7\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":19}", "fc437b172042b30cbbdc9accfbd80a5e322188193737573b93872029a8204d96"]
["TRADER_PROMPT_M11_V7", "PROMPT", 7, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V7\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"ab66f4355382e7dc24c157e1d1019aa5b13fe17e4b8f4813c86a069b24450890\",\"source\":\"services/agent-runner/prompts/m11/trader.v7.md\",\"status\":\"CODE_OWNED\",\"version\":7}", "fdadd82c5396bfb7e1ca219422161f616dbdb561670616dfabf377699f58fc93"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-19 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V19.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-19 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0033's futures decision guard, which also accepts generation 19's trader and holds its rows to generation 10's rules.
# Downgrade restores 0033's text exactly.
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
TRADERS_V6 = ("NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4',"
              "'FUTURES_DECISION_V5','FUTURES_DECISION_V6')")
TRADERS_V7 = ("NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4',"
              "'FUTURES_DECISION_V5','FUTURES_DECISION_V6','FUTURES_DECISION_V7')")
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
FORECAST_V7 = """
    IF (w.template_id IN ('FUTURES_DECISION_V3','FUTURES_DECISION_V4','FUTURES_DECISION_V5','FUTURES_DECISION_V6','FUTURES_DECISION_V7'))
            <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9 to 11''s traders and generation 14 and 19''s, and no other'; END IF;
    IF w.template_id IN ('FUTURES_DECISION_V4','FUTURES_DECISION_V5','FUTURES_DECISION_V6','FUTURES_DECISION_V7') AND (
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
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V7)
               .replace("{forecast}", FORECAST_V7))
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 19 by hash would bind definitions that no longer exist (as 0033's); a
    # generation-19 workflow is the only writer of the added trigger kind.
    generation19 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        f"SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation19}) "
        f"+ (SELECT count(*) FROM futures_decisions WHERE trigger IN {_quoted(TRIGGERS_ADDED)})"
    ).scalar_one()
    if held:
        raise RuntimeError("generation-19 records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-19 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V6)
               .replace("{forecast}", FORECAST_V6))
    _checks(TRIGGERS)
