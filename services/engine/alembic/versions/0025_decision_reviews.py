"""ExecPlan 0043 update 2: the trader sees its scores and forecasts the next hour; a daily review of its decisions.

Revision ID: 0025_decision_reviews
Revises: 0024_decision_scores

ExecPlan 0043 section 4.5. Additive; nothing of the futures engine, its account, its positions, the twins or the
scores changes, and the engine reads none of it. Each guard resolves names under a fixed search path.

- The artifact kind ``DECISION_REVIEW``, written only by the agent identity for its own running workflow of
  ``DECISION_REVIEW_V1``: it names the day its workflow was started for and the hash of the cases bound at its start.
  One review per day.
- The workflow purpose ``DECISION_REVIEW``; the trade review guard also accepts a note from generation 9's coach
  ``TRADE_COACH_V2``.
- ``futures_decisions.expected_move``: the trader's forecast of the next hour (``UP``, ``DOWN`` or ``NO_VIEW``). The
  futures decision guard also accepts generation 9's trader ``FUTURES_DECISION_V3``, whose decisions carry a forecast;
  no other trader's do.
- Generation 9's agent definitions (frozen here, checked against the code).

Downgrade refuses once any generation-9 workflow, decision review or forecast exists, or a runtime profile binds
generation 9 (as 0022's); otherwise it restores 0024's checks and 0022's guards.
"""

import hashlib
import json

from alembic import op

revision = "0025_decision_reviews"
down_revision = "0024_decision_scores"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# The checks as migration 0022 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW", "COIN_NOTE", "TRADE_REVIEW", "TRADE_COACH")
PURPOSES_ADDED = ("DECISION_REVIEW",)
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE", "FUTURES_DECISION", "TRADE_REVIEW", "TRADE_ADVICE")
ARTIFACTS_ADDED = ("DECISION_REVIEW",)
TEMPLATES = ("FUTURES_DECISION_V3", "DECISION_REVIEW_V1", "TRADE_COACH_V2")

# Generated from app.agents.definitions_v9 (python -m app.agents.definitions_v9); tests/test_m11_decision_reviews.py
# compares.
AGENT_SEED_LINES_V9 = r"""
["AGENT_STEP_SCHEMA_V8", "AGENT_STEP_SCHEMA", 8, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V8\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"ARTIFACT carries exactly the one record your role writes (decision, decision_review or advice) and nulls; ABSTAIN carries only abstain.\",\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"advice\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The coach's note for the trader's next decisions. Each evidence item is a trade review ID, a decision review ID, a scoreboard row key or a scorecard row key from trade_coach; the server adds their counts.\",\"properties\":{\"avoid\":{\"description\":\"At most 3 items. Each at most 160 characters.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"confidence\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 6 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"lean\":{\"enum\":[\"LONG\",\"SHORT\",\"EITHER\",\"SIT_OUT\"],\"type\":\"string\"},\"setup\":{\"additionalProperties\":false,\"description\":\"The setup to look for, in the features the trader sees; each choice from the policy's sets, or null.\",\"properties\":{\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"stop_atr_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"when\":{\"description\":\"At most 240 characters.\",\"type\":\"string\"}},\"required\":[\"when\",\"stop_atr_multiple\",\"take_profit_multiple\",\"leverage\",\"max_hold_hours\"],\"type\":\"object\"}},\"required\":[\"lean\",\"setup\",\"avoid\",\"evidence\",\"confidence\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The futures trader's decision. ENTER_LONG and ENTER_SHORT take leverage, stop_multiple and max_hold_hours, and take_profit_multiple or null; TIGHTEN_STOP takes stop_multiple only; EXIT, HOLD and ABSTAIN take none of them. Never a price, quantity or level. advice_use is NO_ADVICE exactly when no advice note was shown. expected_move is the direction you expect over the next hour, or NO_VIEW.\",\"properties\":{\"action\":{\"enum\":[\"ENTER_LONG\",\"ENTER_SHORT\",\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"advice_note\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"},\"advice_use\":{\"enum\":[\"FOLLOWED\",\"PARTLY\",\"IGNORED\",\"NO_ADVICE\"],\"type\":\"string\"},\"cites\":{\"description\":\"At most 8 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"expected_move\":{\"enum\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"type\":\"string\"},\"invalidation\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"rationale\":{\"description\":\"At most 600 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"SETUP_FOR_ENTRY\",\"PROTECT_POSITION\",\"TAKE_PROFIT_EARLY\",\"NO_EDGE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"LIMIT_OR_COOLDOWN\",\"RISK_EVENT_AHEAD\",\"OTHER\"],\"type\":\"string\"},\"stop_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"leverage\",\"stop_multiple\",\"take_profit_multiple\",\"max_hold_hours\",\"reason_code\",\"rationale\",\"invalidation\",\"uncertainty_level\",\"cites\",\"advice_use\",\"advice_note\",\"expected_move\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision_review\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The decision reviewer's review of the day in decision_review: every case once, judged from what the trader saw then; never a price, a number or a count of your own.\",\"properties\":{\"cases\":{\"description\":\"1 to 6 items.\",\"items\":{\"additionalProperties\":false,\"description\":\"One case of decision_review.cases, answered once. case_id is copied exactly. Each evidence item is a path into that case (keys from the case joined by dots, a list item by its index).\",\"properties\":{\"case_id\":{\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 3 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"knowable\":{\"enum\":[\"YES\",\"PARTLY\",\"NO\"],\"type\":\"string\"},\"note\":{\"description\":\"At most 160 characters.\",\"type\":\"string\"},\"tag\":{\"enum\":[\"TREND_MISSED\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"COSTS_ATE_THE_MOVE\",\"TOO_CAUTIOUS\",\"TOO_EAGER\",\"STOP_TOO_TIGHT\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"LIMIT_OR_COOLDOWN\",\"DATA_PROBLEM\",\"UNFORESEEABLE\"],\"type\":\"string\"}},\"required\":[\"case_id\",\"knowable\",\"tag\",\"evidence\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"cases_sha256\":{\"type\":\"string\"},\"day\":{\"type\":\"string\"},\"lesson\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"}},\"required\":[\"day\",\"cases_sha256\",\"cases\",\"lesson\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"}},\"required\":[\"outcome\",\"decision\",\"decision_review\",\"advice\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v8\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v8\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v9 and ExecPlan 0043 section 4.5\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":8}", "1fa828e8c9ba08d65288e470af2bb0809b7a7826f1c7bd45a1ddf625421a348f"]
["TOOL_CATALOG_V9", "TOOL_CATALOG", 9, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V9\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v9 and ExecPlan 0043 section 4.5\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: ENTER_LONG, ENTER_SHORT, EXIT, TIGHTEN_STOP, HOLD or ABSTAIN, with only the choices that action takes, each from the policy's set, how it used the coach's note (advice_use, NO_ADVICE exactly when none was shown) and the direction it expects over the next hour (expected_move: UP, DOWN or NO_VIEW). The server writes the run, the position it saw, the context's hash, the note it showed and the policy; the engine computes every price, quantity, stop level, fee and margin. A note, a score and the forecast are never an order and change no check.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"},{\"arguments\":[],\"description\":\"FINISH only. EVALUATOR in a decision review. One review of the UTC day the job context holds: its day and the cases' hash, every case once with whether its outcome was knowable then, a tag from the tag list, one to three paths into the case and a short note, and one lesson. Code chose the cases and computed every score; the review changes none of them.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_decision_review\"},{\"arguments\":[],\"description\":\"FINISH only. ANALYST in a trade coach job. One advice note for the trader: a lean, a setup with choices from the policy's sets, up to three things to avoid, the trade review IDs, decision review IDs, scoreboard row keys and scorecard row keys it rests on, and a confidence. The server adds each cited record's counts, holds the confidence at LOW while fewer than ten trades are reviewed and fewer than 288 decisions are scored at one hour, and ends the note after four hours or at the next note.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_trade_advice\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":9}", "7b988c62ff9b72e5bff9319190ac59708d0be4e98c5b9b3679e9ea126c7252d3"]
["ROLE_GRANTS_V9", "ROLE_GRANTS", 9, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"record_trade_advice\"],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[\"record_decision_review\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V9\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v9 and ExecPlan 0043 section 4.5\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"TRADE_COACH_V2\"],\"COORDINATOR\":[\"FUTURES_DECISION_V3\"],\"EVALUATOR\":[\"DECISION_REVIEW_V1\"],\"RESEARCHER\":[]},\"version\":9}", "2573b64e9e304e88ce88167cbe0c753326facac5fab5793e595cd74f54066d35"]
["TEMPLATES_V9", "TEMPLATES", 9, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V9\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_THEN_DECISION_REVIEW_THEN_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v9 and ExecPlan 0043 section 4.5\",\"status\":\"CODE_OWNED\",\"templates\":{\"DECISION_REVIEW_V1\":{\"answers\":{\"evidence\":\"1_TO_3_PATHS_INTO_ITS_CASE\",\"knowable\":[\"YES\",\"PARTLY\",\"NO\"],\"lesson_chars\":200,\"max_cases\":6,\"note_chars\":160,\"tags\":[\"TREND_MISSED\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"COSTS_ATE_THE_MOVE\",\"TOO_CAUTIOUS\",\"TOO_EAGER\",\"STOP_TOO_TIGHT\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"LIMIT_OR_COOLDOWN\",\"DATA_PROBLEM\",\"UNFORESEEABLE\"]},\"artifact\":\"DECISION_REVIEW\",\"cases\":{\"each\":\"WHAT_THE_TRADER_SAW_WHAT_IT_SAID_AND_WHAT_FOLLOWED\",\"from\":\"THE_DAY'S_DECISIONS_SCORED_AT_1H_BY_THE_START\",\"misses\":{\"by\":\"THE_NET_OF_THE_TEST_TRADE_THAT_PAID_LARGEST_FIRST\",\"count\":3,\"labels\":[\"MISSED_LONG\",\"MISSED_SHORT\"]},\"worst\":{\"by\":\"THE_MONEY_MISSED_OR_LOST_IN_PERCENT_OF_THE_REFERENCE_LARGEST_FIRST\",\"count\":3,\"labels\":[\"WRONG_SIDE\",\"FEES_ONLY\",\"HELD_INTO_LOSS\",\"EARLY_EXIT\",\"SHAKEN_OUT\"]}},\"cutoff\":\"THE_DAY'S_CASES_AND_1H_SCORECARD_WITH_THEIR_HASH_AND_THE_TAG_LIST\",\"follow_on\":\"THE_COACH\",\"parameters\":{\"day\":\"THE_UTC_DAY_REVIEWED\"},\"prompt\":\"DECISION_REVIEWER_PROMPT_M11_V1\",\"purpose\":\"DECISION_REVIEW\",\"quiet_window\":\"HH:59:30_TO_HH:06:00_UTC\",\"role\":\"EVALUATOR\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"end_before_the_next_15m_bar_seconds\":60,\"no_decision_queued_or_open\":true,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"not_reviewed_after_hours\":48,\"open_at_once\":1,\"skipped\":\"A_DAY_WITHOUT_A_CASE\",\"starts_per_day\":3,\"when\":\"ONCE_A_UTC_DAY_FOR_THE_DAY_BEFORE_FROM_01:30_UTC\",\"with\":\"THE_TRADE_REVIEWER_AND_THE_COACH_ONE_AT_A_TIME_AFTER_ANY_WAITING_FACT_SHEET\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_DECISION_REVIEW_ARTIFACT_PER_DAY\"},\"FUTURES_DECISION_V3\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60,\"read_by\":\"THE_SCORECARD_ONLY; NO_CODE_THAT_TRADES\"},\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_FILL_OR_SHARP_MOVE\"},\"prompt\":\"TRADER_PROMPT_M11_V3\",\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V2\",\"role\":\"COORDINATOR\",\"schedule\":{\"bar\":\"EVERY_FINISHED_15M_BAR\",\"coalescing\":\"A_TRIGGER_IS_COVERED_BY_ANY_DECISION_STARTED_AFTER_ITS_EVENT\",\"fill\":\"RIGHT_AFTER_EACH_FILL\",\"open_at_once\":1,\"sharp_move\":\"A_MOVE_OF_MORE_THAN_THE_POLICY'S_ATR_MULTIPLE_WITHIN_ITS_WINDOW\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"scores\":{\"count\":16,\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; NOT_A_RULE\",\"scorecard\":\"THE_1H_SCORECARD_OF_THE_LAST_24H_AND_7D_AS_OF_THE_CUTOFF\",\"shown\":\"THE_NEWEST_DECISIONS_WITH_A_1H_SCORE_RECORDED_BY_THE_CUTOFF\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"},\"TRADE_COACH_V2\":{\"artifact\":\"TRADE_ADVICE\",\"cutoff\":\"THE_LAST_REVIEWS_THE_SCOREBOARD_THE_LAST_DECISION_REVIEWS_AND_THE_SCORECARD_ROWS_AS_OF_ITS_START_WITH_THEIR_HASH_AND_THE_POLICY'S_SETS\",\"decision_reviews_shown\":3,\"follow_on\":\"NONE\",\"note\":{\"confidence_low_while_below\":{\"decisions_scored_at_1h\":288,\"reviewed_trades\":10},\"counts\":\"WRITTEN_BY_THE_SERVER_FOR_EACH_CITED_RECORD\",\"expires_after_hours\":4,\"or\":\"THE_NEXT_NOTE\"},\"parameters\":{\"review\":\"THE_NEWEST_TRADE_OR_DECISION_REVIEW'S_ID\"},\"prompt\":\"COACH_PROMPT_M11_V2\",\"purpose\":\"TRADE_COACH\",\"quiet_window\":\"HH:59:30_TO_HH:06:00_UTC\",\"replaces\":\"TRADE_COACH_V1\",\"reviews_shown\":20,\"role\":\"ANALYST\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"end_before_the_next_15m_bar_seconds\":60,\"no_decision_queued_or_open\":true,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"open_at_once\":1,\"starts_per_review\":3,\"when\":\"AFTER_EACH_NEW_TRADE_OR_DECISION_REVIEW_ONCE_NO_OTHER_REVIEW_WAITS\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_TRADE_ADVICE_ARTIFACT\"}},\"version\":9}", "5d5e3f5fdb18bbf6886030b17d5ec90263b7f4a0b3ad3f9ce3e6c63bf2f99743"]
["BUDGETS_V9", "BUDGETS", 9, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120,\"DECISION_REVIEW\":3,\"TRADE_COACH\":24},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V9\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V3\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":40960,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0040 section 4.6; ExecPlan 0043 section 4.5\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"DECISION_REVIEW_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":300,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300},\"FUTURES_DECISION_V3\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"TRADE_COACH_V2\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":300,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":9}", "23a9a8cf6c71b8878307cdb9401e52fc4477c50a92cb5d11d09668b6ab0a2f45"]
["COACH_PROMPT_M11_V2", "PROMPT", 2, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COACH_PROMPT_M11_V2\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"93f5b3d4a166c7c8ebb7d32fe796d1cac9c7f452766a7c0cd6e5457f501f1d2b\",\"source\":\"services/agent-runner/prompts/m11/coach.v2.md\",\"status\":\"CODE_OWNED\",\"version\":2}", "c7f85634d24625eeca97c25d4c8f047aff7b1e703902e29801c9c0dfee60e318"]
["DECISION_REVIEWER_PROMPT_M11_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"DECISION_REVIEWER_PROMPT_M11_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"eef55cd9d2b55d1703eff1b23cd8ab98fcde3389d770ec5799ab5a3d5aae1cf3\",\"source\":\"services/agent-runner/prompts/m11/decision-reviewer.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "20dc974c0086c048b7930082c226ca0e0484b929c008fa63c39c527c278d3916"]
["TRADER_PROMPT_M11_V3", "PROMPT", 3, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V3\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"8f3d6705024495320a6a10994b0e735f833b250c15af45b843643baf2eb833be\",\"source\":\"services/agent-runner/prompts/m11/trader.v3.md\",\"status\":\"CODE_OWNED\",\"version\":3}", "4cf1a89bfc602c550d320ddb86f36334c2a197199fc69059d034e6ee2e935ff1"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-9 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V9.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-9 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


TABLE_SQL = """
ALTER TABLE futures_decisions ADD COLUMN expected_move varchar(7)
    CONSTRAINT futures_decisions_expected_move CHECK (expected_move IN ('UP','DOWN','NO_VIEW'));
CREATE UNIQUE INDEX agent_artifacts_one_decision_review ON agent_artifacts ((document->>'day'))
    WHERE kind = 'DECISION_REVIEW';
"""

GUARDS_SQL = """
-- A decision review comes only from the agent identity, for its own running workflow of its template, and names the day
-- that workflow was started for and the hash of the cases bound at its start.
CREATE FUNCTION asl_decision_review_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a decision review comes only from its agent'; END IF;
    SELECT template_id, purpose, role, state, parent_id, params, cutoff INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL
            OR (w.template_id, w.purpose, w.role) <> ('DECISION_REVIEW_V1', 'DECISION_REVIEW', 'EVALUATOR') THEN
        RAISE EXCEPTION 'a decision review needs its own running workflow'; END IF;
    IF d->>'day' IS NULL OR d->>'day' IS DISTINCT FROM w.params->'day'->>'id'
            OR d->>'cases_sha256' IS NULL
            OR d->>'cases_sha256' IS DISTINCT FROM w.cutoff->'decision_review'->>'cases_sha256' THEN
        RAISE EXCEPTION 'a decision review names its day and the cases bound at its start'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER agent_artifacts_decision_review BEFORE INSERT ON agent_artifacts
    FOR EACH ROW WHEN (NEW.kind = 'DECISION_REVIEW') EXECUTE FUNCTION asl_decision_review_guard();
"""

# 0022's trade review guard, whose note may also come from generation 9's coach. Downgrade restores 0022's text exactly.
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
COACH_V1 = "(w.template_id, w.purpose, w.role) <> ('TRADE_COACH_V1', 'TRADE_COACH', 'ANALYST')"
COACHES_V2 = ("(w.template_id NOT IN ('TRADE_COACH_V1','TRADE_COACH_V2') "
              "OR (w.purpose, w.role) <> ('TRADE_COACH', 'ANALYST'))")

# 0022's futures decision guard, which also accepts generation 9's trader, whose decisions alone carry a forecast.
# Downgrade restores 0022's text exactly.
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
TRADERS_V2 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2')"
TRADERS_V3 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2','FUTURES_DECISION_V3')"
FORECAST = """
    IF (w.template_id = 'FUTURES_DECISION_V3') <> (NEW.expected_move IS NOT NULL) THEN
        RAISE EXCEPTION 'a forecast comes with each decision of generation 9''s trader and no other'; END IF;"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               "ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN "
               f"{_quoted((*PURPOSES, *PURPOSES_ADDED))})")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               "ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN "
               f"{_quoted((*ARTIFACT_KINDS, *ARTIFACTS_ADDED))})")
    op.execute(TABLE_SQL)
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH))
    op.execute(TRADE_REVIEW_GUARD.replace("{path}", SEARCH_PATH).replace("{coach}", COACHES_V2))
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V3)
               .replace("{forecast}", FORECAST))
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 9 by hash would bind definitions that no longer exist (as 0022's).
    generation9 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        f"SELECT (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} "
        f"OR purpose IN {_quoted(PURPOSES_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ARTIFACTS_ADDED)}) "
        "+ (SELECT count(*) FROM futures_decisions WHERE expected_move IS NOT NULL) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation9})"
    ).scalar_one()
    if held:
        raise RuntimeError("decision review records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-9 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V2)
               .replace("{forecast}", ""))
    op.execute(TRADE_REVIEW_GUARD.replace("{path}", SEARCH_PATH).replace("{coach}", COACH_V1))
    op.execute("DROP TRIGGER agent_artifacts_decision_review ON agent_artifacts")
    op.execute("DROP FUNCTION asl_decision_review_guard()")
    op.execute("DROP INDEX agent_artifacts_one_decision_review")
    op.execute("ALTER TABLE futures_decisions DROP COLUMN expected_move")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               f"ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(PURPOSES)})")
