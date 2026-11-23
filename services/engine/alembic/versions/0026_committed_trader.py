"""ExecPlan 0044: a trader that commits (generation 10).

Revision ID: 0026_committed_trader
Revises: 0025_decision_reviews

ExecPlan 0044 section 4. Additive; nothing of the futures engine, its account, its positions, the twins or the scores
changes, and the engine reads none of it. Each guard resolves names under a fixed search path.

- The futures decision guard also accepts generation 10's trader ``FUTURES_DECISION_V4``, whose decisions carry a
  forecast as generation 9's do, and refuses on its rows a ``NO_VIEW`` outside ``ABSTAIN`` or a view with it, an entry
  against its forecast, and an entry's stop under 2 ATR or time exit under 4 hours (the confidence, the fourth rule of
  the finish, is in the artifact only).
- The trade review guard also accepts a note from generation 10's coach ``TRADE_COACH_V3``.
- Generation 10's agent definitions (frozen here, checked against the code).

Downgrade refuses once any generation-10 workflow exists or a runtime profile binds generation 10 (as 0025's);
otherwise it restores 0025's guards.
"""

import hashlib
import json

from alembic import op

revision = "0026_committed_trader"
down_revision = "0025_decision_reviews"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TEMPLATES = ("FUTURES_DECISION_V4", "TRADE_COACH_V3")

# Generated from app.agents.definitions_v10 (python -m app.agents.definitions_v10); tests/test_m11_committed_trader.py
# compares.
AGENT_SEED_LINES_V10 = r"""
["TOOL_CATALOG_V10", "TOOL_CATALOG", 10, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V10\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v10 and ExecPlan 0044 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: ENTER_LONG, ENTER_SHORT, EXIT, TIGHTEN_STOP, HOLD or ABSTAIN, with only the choices that action takes, each from the policy's set, how it used the coach's note (advice_use, NO_ADVICE exactly when none was shown) and the direction it expects over the next hour (expected_move: UP or DOWN; NO_VIEW only with ABSTAIN), with uncertainty_level as its confidence in that call. An entry goes the way of its call (ENTER_LONG with UP, ENTER_SHORT with DOWN), at MEDIUM or HIGH, with stop_multiple 2.0 or 3.0 and max_hold_hours 4, 12 or 24; any other is refused. The server writes the run, the position it saw, the context's hash, the note it showed and the policy; the engine computes every price, quantity, stop level, fee and margin. A note, a score and the forecast are never an order and change no check.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"},{\"arguments\":[],\"description\":\"FINISH only. ANALYST in a trade coach job. One advice note for the trader: a lean, a setup with choices from the policy's sets, up to three things to avoid, the trade review IDs, decision review IDs, scoreboard row keys and scorecard row keys it rests on, and a confidence. The lean SIT_OUT is refused while fewer than ten trades are reviewed. The server adds each cited record's counts, holds the confidence at LOW while fewer than ten trades are reviewed and fewer than 288 decisions are scored at one hour, and ends the note after four hours or at the next note.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_trade_advice\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":10}", "3c74dfa998d9ccbf1be6680304838420f93f34ee488adcacca5e0459df3c55ff"]
["ROLE_GRANTS_V10", "ROLE_GRANTS", 10, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"record_trade_advice\"],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V10\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v10 and ExecPlan 0044 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"TRADE_COACH_V3\"],\"COORDINATOR\":[\"FUTURES_DECISION_V4\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":10}", "87c5dda1a135b3b8c1c2c0f47c72b3bd22e1bae27ac8bed414349e00eb1223cc"]
["TEMPLATES_V10", "TEMPLATES", 10, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V10\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_THEN_DECISION_REVIEW_THEN_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v10 and ExecPlan 0044 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V4\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60,\"read_by\":\"THE_SCORECARD_ONLY; NO_CODE_THAT_TRADES\"},\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_FILL_OR_SHARP_MOVE\"},\"prompt\":\"TRADER_PROMPT_M11_V4\",\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V3\",\"role\":\"COORDINATOR\",\"schedule\":{\"bar\":\"EVERY_FINISHED_15M_BAR\",\"coalescing\":\"A_TRIGGER_IS_COVERED_BY_ANY_DECISION_STARTED_AFTER_ITS_EVENT\",\"fill\":\"RIGHT_AFTER_EACH_FILL\",\"open_at_once\":1,\"sharp_move\":\"A_MOVE_OF_MORE_THAN_THE_POLICY'S_ATR_MULTIPLE_WITHIN_ITS_WINDOW\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"scores\":{\"count\":16,\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; NOT_A_RULE\",\"scorecard\":\"THE_1H_SCORECARD_OF_THE_LAST_24H_AND_7D_AS_OF_THE_CUTOFF\",\"shown\":\"THE_NEWEST_DECISIONS_WITH_A_1H_SCORE_RECORDED_BY_THE_CUTOFF\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"},\"TRADE_COACH_V3\":{\"artifact\":\"TRADE_ADVICE\",\"cutoff\":\"THE_LAST_REVIEWS_THE_SCOREBOARD_THE_LAST_DECISION_REVIEWS_AND_THE_SCORECARD_ROWS_AS_OF_ITS_START_WITH_THEIR_HASH_AND_THE_POLICY'S_SETS\",\"decision_reviews_shown\":3,\"follow_on\":\"NONE\",\"note\":{\"confidence_low_while_below\":{\"decisions_scored_at_1h\":288,\"reviewed_trades\":10},\"counts\":\"WRITTEN_BY_THE_SERVER_FOR_EACH_CITED_RECORD\",\"expires_after_hours\":4,\"or\":\"THE_NEXT_NOTE\"},\"parameters\":{\"review\":\"THE_NEWEST_TRADE_OR_DECISION_REVIEW'S_ID\"},\"prompt\":\"COACH_PROMPT_M11_V3\",\"purpose\":\"TRADE_COACH\",\"quiet_window\":\"HH:59:30_TO_HH:06:00_UTC\",\"replaces\":\"TRADE_COACH_V2\",\"reviews_shown\":20,\"role\":\"ANALYST\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"end_before_the_next_15m_bar_seconds\":60,\"no_decision_queued_or_open\":true,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"open_at_once\":1,\"starts_per_review\":3,\"when\":\"AFTER_EACH_NEW_TRADE_OR_DECISION_REVIEW_ONCE_NO_OTHER_REVIEW_WAITS\"},\"sit_out\":{\"code\":\"SIT_OUT_NEEDS_TRADES\",\"refused_below_reviewed_trades\":10},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_TRADE_ADVICE_ARTIFACT\"}},\"version\":10}", "50140e4f6f5cdb93720c1b28925cc0ed78db37bf3f2f90d2ab205ef8bff65d77"]
["BUDGETS_V10", "BUDGETS", 10, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120,\"TRADE_COACH\":24},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V10\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V4\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0040 section 4.6; ExecPlan 0043 section 4.5; ExecPlan 0044 section 4.3\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V4\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"TRADE_COACH_V3\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":300,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":10}", "1e9e9d536a31d75821813efdb10c4b4bdddf0427c05a5f176b7944b4fb56ba7b"]
["COACH_PROMPT_M11_V3", "PROMPT", 3, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COACH_PROMPT_M11_V3\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"b55ab2ffafa494563fc56461ec2af8195ea721296266fc34d9f3f79a9f5b8ea7\",\"source\":\"services/agent-runner/prompts/m11/coach.v3.md\",\"status\":\"CODE_OWNED\",\"version\":3}", "ddaf2fa4006950a157a263d9fb7f9c8e2982317fc2672ebc66be9dd6afe1c881"]
["TRADER_PROMPT_M11_V4", "PROMPT", 4, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V4\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"ea58b111872277af28b304039c2fa8090309d7056cc0cf49a46a0121d2b706f9\",\"source\":\"services/agent-runner/prompts/m11/trader.v4.md\",\"status\":\"CODE_OWNED\",\"version\":4}", "e0ef361cbccfebaf4565cace025018565d31661b0c7a7463c7e46ece7d2b2346"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-10 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V10.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-10 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0022's trade review guard as 0025 left it, whose note may also come from generation 10's coach. Downgrade restores
# 0025's text exactly.
TRADE_REVIEW_GUARD = """
CREATE OR REPLACE FUNCTION asl_trade_review_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; s record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a trade review or note comes only from its agent'; END IF;
    SELECT template_id, purpose, role, state, parent_id INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL
            OR (NEW.kind = 'TRADE_REVIEW'
                AND (w.template_id, w.purpose, w.role) <> ('TRADE_REVIEW_V1', 'TRADE_REVIEW', 'EVALUATOR'))
            OR (NEW.kind = 'TRADE_ADVICE'
                AND {coach}) THEN
        RAISE EXCEPTION 'a trade review or note needs its own running workflow'; END IF;
    IF NEW.kind = 'TRADE_REVIEW' THEN
        SELECT position_id, sha256, result INTO s FROM trade_fact_sheets WHERE id::text = d->>'fact_sheet_id';
        IF NOT FOUND OR s.sha256 IS DISTINCT FROM d->>'fact_sheet_sha256'
                OR s.position_id::text IS DISTINCT FROM d->>'position_id' OR s.result IS DISTINCT FROM d->>'result'
                -- PL/pgSQL ends an IF condition at its first THEN outside parentheses, so the CASE is parenthesized.
                OR d->>'grid' IS DISTINCT FROM (CASE (d->>'decision_quality') || ':' || s.result
                    WHEN 'GOOD:WIN' THEN 'GOOD_CALL_WON' WHEN 'GOOD:LOSS' THEN 'GOOD_CALL_UNLUCKY'
                    WHEN 'POOR:WIN' THEN 'POOR_CALL_LUCKY' WHEN 'POOR:LOSS' THEN 'MISTAKE' ELSE 'MIXED' END) THEN
            RAISE EXCEPTION 'a trade review is placed in the grid from its stored fact sheet'; END IF;
    ELSIF CAST(d->>'expires_at' AS timestamptz) IS DISTINCT FROM CAST(d->>'recorded_at' AS timestamptz)
            + interval '4 hours' THEN
        RAISE EXCEPTION 'a note ends four hours after it is recorded'; END IF;
    RETURN NEW;
END $$;
"""
COACHES_V2 = ("(w.template_id NOT IN ('TRADE_COACH_V1','TRADE_COACH_V2') "
              "OR (w.purpose, w.role) <> ('TRADE_COACH', 'ANALYST'))")
COACHES_V3 = ("(w.template_id NOT IN ('TRADE_COACH_V1','TRADE_COACH_V2','TRADE_COACH_V3') "
              "OR (w.purpose, w.role) <> ('TRADE_COACH', 'ANALYST'))")

# 0022's futures decision guard as 0025 left it, which also accepts generation 10's trader and holds its rows to its
# rules. Downgrade restores 0025's text exactly.
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
TRADERS_V3 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3')"
TRADERS_V4 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3','FUTURES_DECISION_V4')"
FORECAST_V3 = """
    IF (w.template_id = 'FUTURES_DECISION_V3') <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9''s trader and no other'; END IF;"""
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


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute(TRADE_REVIEW_GUARD.replace("{path}", SEARCH_PATH).replace("{coach}", COACHES_V3))
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V4)
               .replace("{forecast}", FORECAST_V4))
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 10 by hash would bind definitions that no longer exist (as 0025's).
    generation10 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        f"SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation10})"
    ).scalar_one()
    if held:
        raise RuntimeError("generation-10 records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-10 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V3)
               .replace("{forecast}", FORECAST_V3))
    op.execute(TRADE_REVIEW_GUARD.replace("{path}", SEARCH_PATH).replace("{coach}", COACHES_V2))
