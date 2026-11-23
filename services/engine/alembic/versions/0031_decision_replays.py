"""ExecPlan 0050: replay past decisions offline (generation 13 and its replay rows).

Revision ID: 0031_decision_replays
Revises: 0030_veto_twins

ExecPlan 0050 section 4. Additive: nothing of the owner's account, its journal, its reservations, the futures engine's
tables, the trader, its decisions, the scores, the twins or the veto changes. Each guard resolves names under a fixed
search path.

- ``futures_decision_replays``: one replay agent's answer to one item of ``REPLAY_SET_V1`` (a decision of generation
  11's trader made before 2026-11-01 10:15 UTC, and an arm), written by the agent identity alone from its own running
  replay workflow of that arm bound to that decision, with its ``DECISION_REPLAY`` artifact; the time it was recorded
  is the database's. Append-only, one row per set, arm and decision. Labeled a replay: never a decision, an order or a
  fill; the futures decision guard already refuses a decision from any template but the trader's.
- The workflow purpose ``REPLAY`` and the artifact kind ``DECISION_REPLAY``, with a guard that the artifact names the
  item its own running replay workflow was started for.
- Generation 13's agent definitions (frozen here, checked against the code).

Downgrade refuses once any replay row, replay workflow or replay artifact exists, or a runtime profile binds
generation 13; otherwise it removes all of it.
"""

import hashlib
import json

from alembic import op

revision = "0031_decision_replays"
down_revision = "0030_veto_twins"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# The checks as migration 0030 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW", "COIN_NOTE", "TRADE_REVIEW", "TRADE_COACH",
            "DECISION_REVIEW", "ENTRY_VETO")
PURPOSES_ADDED = ("REPLAY",)
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE", "FUTURES_DECISION", "TRADE_REVIEW", "TRADE_ADVICE",
                  "DECISION_REVIEW", "ENTRY_VETO")
ARTIFACTS_ADDED = ("DECISION_REPLAY",)
TEMPLATES = ("DECISION_REPLAY_CONTROL_V1", "DECISION_REPLAY_NO_FEEDBACK_V1", "DECISION_REPLAY_CALL_4H_V1")
REASON_CODES = ("SETUP_FOR_ENTRY", "PROTECT_POSITION", "TAKE_PROFIT_EARLY", "NO_EDGE", "CONFLICTING_EVIDENCE",
                "DATA_STALE", "LIMIT_OR_COOLDOWN", "RISK_EVENT_AHEAD", "OTHER")

# Generated from app.agents.definitions_v13 (python -m app.agents.definitions_v13); tests/test_m11_replay_unit.py
# compares.
AGENT_SEED_LINES_V13 = r"""
["AGENT_STEP_SCHEMA_V8_CALL_4H", "AGENT_STEP_SCHEMA", 8, "CODE_OWNED", "{\"changed\":\"THE_DECISION'S_DESCRIPTION_NAMES_THE_NEXT_4_HOURS; PARSED_AS_STEP_SCHEMA_V8\",\"id\":\"AGENT_STEP_SCHEMA_V8_CALL_4H\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"ARTIFACT carries exactly the one record your role writes (decision, decision_review or advice) and nulls; ABSTAIN carries only abstain.\",\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"advice\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The coach's note for the trader's next decisions. Each evidence item is a trade review ID, a decision review ID, a scoreboard row key or a scorecard row key from trade_coach; the server adds their counts.\",\"properties\":{\"avoid\":{\"description\":\"At most 3 items. Each at most 160 characters.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"confidence\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 6 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"lean\":{\"enum\":[\"LONG\",\"SHORT\",\"EITHER\",\"SIT_OUT\"],\"type\":\"string\"},\"setup\":{\"additionalProperties\":false,\"description\":\"The setup to look for, in the features the trader sees; each choice from the policy's sets, or null.\",\"properties\":{\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"stop_atr_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"when\":{\"description\":\"At most 240 characters.\",\"type\":\"string\"}},\"required\":[\"when\",\"stop_atr_multiple\",\"take_profit_multiple\",\"leverage\",\"max_hold_hours\"],\"type\":\"object\"}},\"required\":[\"lean\",\"setup\",\"avoid\",\"evidence\",\"confidence\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The futures trader's decision. ENTER_LONG and ENTER_SHORT take leverage, stop_multiple and max_hold_hours, and take_profit_multiple or null; TIGHTEN_STOP takes stop_multiple only; EXIT, HOLD and ABSTAIN take none of them. Never a price, quantity or level. advice_use is NO_ADVICE exactly when no advice note was shown. expected_move is the direction you expect over the next 4 hours, or NO_VIEW.\",\"properties\":{\"action\":{\"enum\":[\"ENTER_LONG\",\"ENTER_SHORT\",\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"advice_note\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"},\"advice_use\":{\"enum\":[\"FOLLOWED\",\"PARTLY\",\"IGNORED\",\"NO_ADVICE\"],\"type\":\"string\"},\"cites\":{\"description\":\"At most 8 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"expected_move\":{\"enum\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"type\":\"string\"},\"invalidation\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"rationale\":{\"description\":\"At most 600 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"SETUP_FOR_ENTRY\",\"PROTECT_POSITION\",\"TAKE_PROFIT_EARLY\",\"NO_EDGE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"LIMIT_OR_COOLDOWN\",\"RISK_EVENT_AHEAD\",\"OTHER\"],\"type\":\"string\"},\"stop_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"leverage\",\"stop_multiple\",\"take_profit_multiple\",\"max_hold_hours\",\"reason_code\",\"rationale\",\"invalidation\",\"uncertainty_level\",\"cites\",\"advice_use\",\"advice_note\",\"expected_move\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision_review\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The decision reviewer's review of the day in decision_review: every case once, judged from what the trader saw then; never a price, a number or a count of your own.\",\"properties\":{\"cases\":{\"description\":\"1 to 6 items.\",\"items\":{\"additionalProperties\":false,\"description\":\"One case of decision_review.cases, answered once. case_id is copied exactly. Each evidence item is a path into that case (keys from the case joined by dots, a list item by its index).\",\"properties\":{\"case_id\":{\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 3 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"knowable\":{\"enum\":[\"YES\",\"PARTLY\",\"NO\"],\"type\":\"string\"},\"note\":{\"description\":\"At most 160 characters.\",\"type\":\"string\"},\"tag\":{\"enum\":[\"TREND_MISSED\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"COSTS_ATE_THE_MOVE\",\"TOO_CAUTIOUS\",\"TOO_EAGER\",\"STOP_TOO_TIGHT\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"LIMIT_OR_COOLDOWN\",\"DATA_PROBLEM\",\"UNFORESEEABLE\"],\"type\":\"string\"}},\"required\":[\"case_id\",\"knowable\",\"tag\",\"evidence\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"cases_sha256\":{\"type\":\"string\"},\"day\":{\"type\":\"string\"},\"lesson\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"}},\"required\":[\"day\",\"cases_sha256\",\"cases\",\"lesson\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"}},\"required\":[\"outcome\",\"decision\",\"decision_review\",\"advice\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v8\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v8\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v13 and ExecPlan 0050 section 4\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"variant_of\":\"AGENT_STEP_SCHEMA_V8\",\"version\":8}", "477b98b450fd68159035eaad801431086812bee8415440589b08b7de99159779"]
["TOOL_CATALOG_V13", "TOOL_CATALOG", 13, "CODE_OWNED", "{\"absent_tools\":[],\"finish_records\":\"IN_GENERATION_13_ONE_DECISION_REPLAY_ARTIFACT_AND_ONE_REPLAY_ROW; NEVER_A_DECISION_OR_A_FILL\",\"id\":\"TOOL_CATALOG_V13\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"reads_at\":\"THE_ORIGINAL_DECISION'S_CUTOFF\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v13 and ExecPlan 0050 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: an action with only the choices it takes from the policy's sets, advice_use, expected_move and uncertainty_level, under the rules of the trader's prompt; an entry they do not allow is refused. The server records the context it was made in; the engine computes every price, quantity, stop level, fee and margin, and reads no forecast, note or score.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":13}", "d53c64dbc726da20b44b440f76d052a6eec69afdb832f92bbf9f7744ed528ff8"]
["ROLE_GRANTS_V13", "ROLE_GRANTS", 13, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V13\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v13 and ExecPlan 0050 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[\"DECISION_REPLAY_CONTROL_V1\",\"DECISION_REPLAY_NO_FEEDBACK_V1\",\"DECISION_REPLAY_CALL_4H_V1\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":13}", "4182efcadeda3db5ebd71d25dc32b369ba5c9041801c5a614a723561c0da724c"]
["TEMPLATES_V13", "TEMPLATES", 13, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V13\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"ENTRY_VETO_WITH_THE_REVIEWS\",\"REPLAY_LAST\"],\"replay_set\":{\"abstention\":\"THE_MODEL'S_OWN_ABSTAIN_IS_ITS_ANSWER_NO_VIEW\",\"arms\":{\"CALL_4H\":{\"dropped_blocks\":[\"scores\",\"advice\"],\"dropped_from_each_recent_trade\":[\"review\"],\"horizon_minutes\":240,\"prompt\":\"TRADER_PROMPT_M11_CALL_4H_V1\",\"template\":\"DECISION_REPLAY_CALL_4H_V1\"},\"CONTROL\":{\"dropped_blocks\":[],\"dropped_from_each_recent_trade\":[],\"horizon_minutes\":60,\"prompt\":\"TRADER_PROMPT_M11_V5\",\"template\":\"DECISION_REPLAY_CONTROL_V1\"},\"NO_FEEDBACK\":{\"dropped_blocks\":[\"scores\",\"advice\"],\"dropped_from_each_recent_trade\":[\"review\"],\"horizon_minutes\":60,\"prompt\":\"TRADER_PROMPT_M11_NO_FEEDBACK_V1\",\"template\":\"DECISION_REPLAY_NO_FEEDBACK_V1\"}},\"contexts\":{\"context_at_before\":\"2026-11-01T10:15:00Z\",\"purpose\":\"DECISION\",\"stored\":\"THE_WORKFLOW'S_CUTOFF.FUTURES.CONTEXT\",\"template\":\"FUTURES_DECISION_V5\"},\"control_sample\":{\"rule\":\"THE_SMALLEST_SHA256_OF_'REPLAY_SET_V1|CONTROL|'_PLUS_THE_DECISION_ID\",\"size\":100},\"id\":\"REPLAY_SET_V1\",\"measure\":{\"band_percent\":\"0.12\",\"bootstrap\":\"STATIONARY_POLITIS_ROMANO_1994\",\"complete_share\":\"0.95\",\"confidence\":\"0.975\",\"move\":\"THE_ORIGINAL_DECISION'S_FUTURES_DECISION_SCORES.MOVE_PERCENT_AT_THE_HORIZON_SCORED\",\"order\":\"CONTEXT_AT\",\"primary\":{\"P1\":{\"against\":\"LAST_HOUR\",\"arm\":\"NO_FEEDBACK\",\"mean_block\":8,\"minutes\":60,\"seed\":\"P1\"},\"P2\":{\"against\":\"LAST_4_HOURS\",\"arm\":\"CALL_4H\",\"mean_block\":16,\"minutes\":240,\"seed\":\"P2\"}},\"resamples\":2000,\"rules\":{\"LAST_4_HOURS\":\"THE_SIGN_OF_THE_STORED_FEATURES.RETURNS_PERCENT.4H\",\"LAST_HOUR\":\"THE_SIGN_OF_THE_STORED_FEATURES.RETURNS_PERCENT.1H\",\"zero\":\"NO_CALL_SCORES_0\"},\"score\":\"THE_MOVE_AT_THE_HORIZON_IN_THE_CALLED_DIRECTION: +MOVE_FOR_UP, -MOVE_FOR_DOWN, 0_FOR_NO_VIEW\",\"secondary_confidence\":\"0.95\",\"verdict\":{\"INCOMPLETE\":\"FEWER_THAN_95%_OF_THE_ARM'S_ITEMS_ANSWERED\",\"NO_DIFFERENCE\":\"OTHERWISE\",\"PASS\":\"THE_INTERVAL'S_LOWER_END_ABOVE_0\",\"WORSE\":\"THE_INTERVAL'S_UPPER_END_BELOW_0\"}},\"order\":\"SHA256_OF_'REPLAY_SET_V1|'_PLUS_THE_DECISION_ID; EACH_CONTEXT'S_ARMS_CONTROL_NO_FEEDBACK_CALL_4H\",\"starts_per_item\":3},\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v13 and ExecPlan 0050 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"DECISION_REPLAY_CALL_4H_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V8_CALL_4H\",\"arm\":\"CALL_4H\",\"artifact\":\"DECISION_REPLAY\",\"checked\":\"THE_TRADER'S_FINISH_RULES_BUT_THE_AGENTS'_CHECK_WHICH_GATES_ONLY_LIVE_ENTRIES\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"context\":\"THE_STORED_CONTEXT_WITHOUT_SCORES_ADVICE_AND_EACH_TRADE'S_REVIEW\",\"cutoff\":\"THE_ORIGINAL_DECISION'S_AS_OF_WATERMARK_AND_FEEDS\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":240},\"label\":\"REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"replay\":\"THE_SET_THE_ARM_AND_THE_ORIGINAL_DECISION'S_ID\",\"symbols\":\"THE_ORIGINAL'S\",\"trigger\":\"THE_ORIGINAL'S\"},\"prompt\":\"TRADER_PROMPT_M11_CALL_4H_V1\",\"purpose\":\"REPLAY\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_REPLAY_REPORT_ONLY\",\"role\":\"COORDINATOR\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"THE_ORIGINAL_DECISION'S\",\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_REPLAY\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"when\":\"ONE_AT_A_TIME_THE_NEXT_UNANSWERED_ITEM_OF_THE_SET\"},\"set\":\"REPLAY_SET_V1\",\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_DECISION_REPLAY_ARTIFACT_AND_ONE_FUTURES_DECISION_REPLAYS_ROW\"},\"DECISION_REPLAY_CONTROL_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V8\",\"arm\":\"CONTROL\",\"artifact\":\"DECISION_REPLAY\",\"checked\":\"THE_TRADER'S_FINISH_RULES_BUT_THE_AGENTS'_CHECK_WHICH_GATES_ONLY_LIVE_ENTRIES\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"context\":\"THE_STORED_CONTEXT\",\"cutoff\":\"THE_ORIGINAL_DECISION'S_AS_OF_WATERMARK_AND_FEEDS\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60},\"label\":\"REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"replay\":\"THE_SET_THE_ARM_AND_THE_ORIGINAL_DECISION'S_ID\",\"symbols\":\"THE_ORIGINAL'S\",\"trigger\":\"THE_ORIGINAL'S\"},\"prompt\":\"TRADER_PROMPT_M11_V5\",\"purpose\":\"REPLAY\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_REPLAY_REPORT_ONLY\",\"role\":\"COORDINATOR\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"THE_ORIGINAL_DECISION'S\",\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_REPLAY\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"when\":\"ONE_AT_A_TIME_THE_NEXT_UNANSWERED_ITEM_OF_THE_SET\"},\"set\":\"REPLAY_SET_V1\",\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_DECISION_REPLAY_ARTIFACT_AND_ONE_FUTURES_DECISION_REPLAYS_ROW\"},\"DECISION_REPLAY_NO_FEEDBACK_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V8\",\"arm\":\"NO_FEEDBACK\",\"artifact\":\"DECISION_REPLAY\",\"checked\":\"THE_TRADER'S_FINISH_RULES_BUT_THE_AGENTS'_CHECK_WHICH_GATES_ONLY_LIVE_ENTRIES\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"context\":\"THE_STORED_CONTEXT_WITHOUT_SCORES_ADVICE_AND_EACH_TRADE'S_REVIEW\",\"cutoff\":\"THE_ORIGINAL_DECISION'S_AS_OF_WATERMARK_AND_FEEDS\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60},\"label\":\"REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"replay\":\"THE_SET_THE_ARM_AND_THE_ORIGINAL_DECISION'S_ID\",\"symbols\":\"THE_ORIGINAL'S\",\"trigger\":\"THE_ORIGINAL'S\"},\"prompt\":\"TRADER_PROMPT_M11_NO_FEEDBACK_V1\",\"purpose\":\"REPLAY\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_REPLAY_REPORT_ONLY\",\"role\":\"COORDINATOR\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"THE_ORIGINAL_DECISION'S\",\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_REPLAY\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"when\":\"ONE_AT_A_TIME_THE_NEXT_UNANSWERED_ITEM_OF_THE_SET\"},\"set\":\"REPLAY_SET_V1\",\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_DECISION_REPLAY_ARTIFACT_AND_ONE_FUTURES_DECISION_REPLAYS_ROW\"}},\"version\":13}", "48d7aa0c7439b3df651a222cf7c47c4149557f8d66c3205e1b80a928d1f0b5c4"]
["BUDGETS_V13", "BUDGETS", 13, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"REPLAY\":192},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V13\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0050 sections 4.2 and 4.3\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"DECISION_REPLAY_CALL_4H_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"DECISION_REPLAY_CONTROL_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"DECISION_REPLAY_NO_FEEDBACK_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":13}", "6f506eab7c5501cd33c1ba69a0e2baed0b6285d35ba3545d2dc32b058f8a454a"]
["TRADER_PROMPT_M11_CALL_4H_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_CALL_4H_V1\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"51a5d5595aa63394fe96d1dc911f85e7ad917c8e27afdb7e743a45a6a2397ab0\",\"source\":\"services/agent-runner/prompts/m11/trader-replay.call-4h.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "654ac72b0ca17255d553564a045a096d5368a175a950d7b8542fbaf11ef94d53"]
["TRADER_PROMPT_M11_NO_FEEDBACK_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_NO_FEEDBACK_V1\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"5361f08bda72f861fa19f11f5479b90d9f94fd1a5deb952c7db4564a46f8d94d\",\"source\":\"services/agent-runner/prompts/m11/trader-replay.no-feedback.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "69fbbb2fceed0c2e9f80f375a6e16c30858a404126ae589d22cfdd1d03c98b96"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    rows = []
    for line in AGENT_SEED_LINES_V13.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-13 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


TABLES_SQL = """
CREATE TABLE futures_decision_replays (
    id uuid PRIMARY KEY,
    set_id varchar(32) NOT NULL CHECK (set_id IN ('REPLAY_SET_V1')),
    arm varchar(12) NOT NULL CHECK (arm IN ('CONTROL','NO_FEEDBACK','CALL_4H')),
    decision_id uuid NOT NULL REFERENCES futures_decisions(id),
    workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id),
    artifact_sha256 varchar(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    context_at timestamptz NOT NULL,
    context_sha256 varchar(64) NOT NULL CHECK (context_sha256 ~ '^[0-9a-f]{64}$'),
    action varchar(12) NOT NULL
        CHECK (action IN ('ENTER_LONG','ENTER_SHORT','EXIT','TIGHTEN_STOP','HOLD','ABSTAIN')),
    expected_move varchar(7) NOT NULL CHECK (expected_move IN ('UP','DOWN','NO_VIEW')),
    uncertainty_level varchar(6) NOT NULL CHECK (uncertainty_level IN ('LOW','MEDIUM','HIGH')),
    reason_code varchar(32) NOT NULL CHECK (reason_code IN {reasons}),
    horizon_minutes integer NOT NULL CHECK (horizon_minutes IN (60, 240)),
    model varchar(128),
    effort varchar(32),
    rule_1h varchar(4) NOT NULL CHECK (rule_1h IN ('UP','DOWN','NONE')),
    rule_4h varchar(4) NOT NULL CHECK (rule_4h IN ('UP','DOWN','NONE')),
    original_expected_move varchar(7) CHECK (original_expected_move IN ('UP','DOWN','NO_VIEW')),
    label text NOT NULL DEFAULT 'REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL'
        CHECK (label = 'REPLAY; MODEL_AUTHORED; NEVER_A_DECISION_OR_A_FILL'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (set_id, arm, decision_id),
    CONSTRAINT futures_decision_replay_view CHECK ((expected_move = 'NO_VIEW') = (action = 'ABSTAIN')),
    CONSTRAINT futures_decision_replay_horizon CHECK ((arm = 'CALL_4H') = (horizon_minutes = 240))
);
CREATE INDEX futures_decision_replays_decision ON futures_decision_replays (decision_id);
"""

GUARDS_SQL = """
-- A replay comes only from the agent identity, for its own running replay workflow of that arm bound to that item, and
-- answers a decision of the set at that decision's time, as its workflow's recorded artifact; the time it was recorded
-- is the database's.
CREATE FUNCTION asl_futures_decision_replay_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; o record; arm_template text;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a replay comes only from its agent'; END IF;
    NEW.recorded_at := clock_timestamp();
    arm_template := CASE NEW.arm WHEN 'CONTROL' THEN 'DECISION_REPLAY_CONTROL_V1'
        WHEN 'NO_FEEDBACK' THEN 'DECISION_REPLAY_NO_FEEDBACK_V1' WHEN 'CALL_4H' THEN 'DECISION_REPLAY_CALL_4H_V1' END;
    SELECT template_id, purpose, role, state, parent_id, params INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL OR (w.purpose, w.role) <> ('REPLAY', 'COORDINATOR')
            OR w.template_id IS DISTINCT FROM arm_template THEN
        RAISE EXCEPTION 'a replay needs its own running replay workflow of its arm'; END IF;
    IF w.params->'replay'->>'set' IS DISTINCT FROM NEW.set_id OR w.params->'replay'->>'arm' IS DISTINCT FROM NEW.arm
            OR w.params->'replay'->>'decision_id' IS DISTINCT FROM NEW.decision_id::text THEN
        RAISE EXCEPTION 'a replay answers the item its workflow was started for'; END IF;
    SELECT fd.context_at, ow.template_id, ow.purpose INTO o FROM futures_decisions fd
        JOIN agent_workflows ow ON ow.id = fd.workflow_id WHERE fd.id = NEW.decision_id;
    IF NOT FOUND OR o.template_id <> 'FUTURES_DECISION_V5' OR o.purpose <> 'DECISION'
            OR o.context_at >= TIMESTAMPTZ '2026-11-01 10:15:00+00' OR NEW.context_at IS DISTINCT FROM o.context_at THEN
        RAISE EXCEPTION 'a replay answers a decision of its set, at that decision''s time'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_artifacts WHERE workflow_id = NEW.workflow_id AND kind = 'DECISION_REPLAY'
            AND sha256 = NEW.artifact_sha256) THEN
        RAISE EXCEPTION 'a replay is its workflow''s recorded artifact'; END IF;
    RETURN NEW;
END $$;

-- The replay artifact names the item its own running replay workflow was started for.
CREATE FUNCTION asl_decision_replay_artifact_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a replay comes only from its agent'; END IF;
    SELECT template_id, purpose, role, state, parent_id, params INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL OR (w.purpose, w.role) <> ('REPLAY', 'COORDINATOR')
            OR w.template_id NOT IN {templates} THEN
        RAISE EXCEPTION 'a replay needs its own running replay workflow'; END IF;
    IF d->>'set' IS DISTINCT FROM w.params->'replay'->>'set' OR d->>'arm' IS DISTINCT FROM w.params->'replay'->>'arm'
            OR d->>'decision_id' IS DISTINCT FROM w.params->'replay'->>'decision_id' THEN
        RAISE EXCEPTION 'a replay names the item its workflow was started for'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_decision_replays_guard BEFORE INSERT ON futures_decision_replays
    FOR EACH ROW EXECUTE FUNCTION asl_futures_decision_replay_guard();
CREATE TRIGGER futures_decision_replays_append_only BEFORE UPDATE OR DELETE ON futures_decision_replays
    FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only();
CREATE TRIGGER agent_artifacts_decision_replay BEFORE INSERT ON agent_artifacts
    FOR EACH ROW WHEN (NEW.kind = 'DECISION_REPLAY') EXECUTE FUNCTION asl_decision_replay_artifact_guard();
"""

GRANTS_SQL = """
GRANT SELECT, INSERT ON futures_decision_replays TO asl_agent;
GRANT SELECT ON futures_decision_replays TO asl_api;
"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute(TABLES_SQL.replace("{reasons}", _quoted(REASON_CODES)))
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               "ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN "
               f"{_quoted((*PURPOSES, *PURPOSES_ADDED))})")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               "ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN "
               f"{_quoted((*ARTIFACT_KINDS, *ARTIFACTS_ADDED))})")
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH).replace("{templates}", _quoted(TEMPLATES)))
    op.execute(GRANTS_SQL)
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # Nothing new can be stored between the count and the drop.
    op.execute("LOCK TABLE futures_decision_replays IN ACCESS EXCLUSIVE MODE")
    # A runtime profile that binds generation 13 by hash would bind definitions that no longer exist (as 0030's).
    generation13 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_decision_replays) "
        f"+ (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} "
        f"OR purpose IN {_quoted(PURPOSES_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ARTIFACTS_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation13})"
    ).scalar_one()
    if held:
        raise RuntimeError("decision replay records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-13 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("DROP TRIGGER agent_artifacts_decision_replay ON agent_artifacts")
    op.execute("DROP TABLE futures_decision_replays")
    op.execute("DROP FUNCTION asl_futures_decision_replay_guard(), asl_decision_replay_artifact_guard()")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               f"ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(PURPOSES)})")
