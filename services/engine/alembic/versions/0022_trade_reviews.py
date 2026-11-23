"""ExecPlan 0040 part 1: a review of every closed futures trade, and the coach's note for the trader.

Revision ID: 0022_trade_reviews
Revises: 0021_no_owner

ExecPlan 0040 section 4. Additive; nothing of the futures engine, its account or its positions changes, and the engine
reads none of it. Each guard resolves names under a fixed search path.

- ``trade_fact_sheets``: one fact sheet of each closed futures position, built in code by the agent identity from
  stored records (``app.agents.trade_facts``). Its canonical text, document and hash agree (0009's content guard); its
  scoreboard columns are its document's values and describe the closed position; it never changes.
- The artifact kinds ``TRADE_REVIEW`` and ``TRADE_ADVICE``, each written only by the agent identity for its own running
  workflow of its template: a review names a stored fact sheet by ID and hash and sits in the grid cell its grade and
  the sheet's result give; a note ends four hours after it is recorded. One review per fact sheet.
- The workflow purposes ``TRADE_REVIEW`` and ``TRADE_COACH``; the futures decision guard also accepts generation 8's
  trader ``FUTURES_DECISION_V2``.
- ``agent_read`` views the fact sheet reads: the fills' book levels and marks, the feed's events, the run's events and
  the latches.
- Generation 8's agent definitions (frozen here, checked against the code).

Downgrade refuses once any fact sheet, generation-8 workflow, review or note exists, or a runtime profile binds
generation 8 (as 0016's); otherwise it restores 0021's checks, views and futures decision guard.
"""

import hashlib
import json

from alembic import op

revision = "0022_trade_reviews"
down_revision = "0021_no_owner"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# The checks as migrations 0015 and 0020 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW", "COIN_NOTE")
PURPOSES_ADDED = ("TRADE_REVIEW", "TRADE_COACH")
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE", "FUTURES_DECISION")
ARTIFACTS_ADDED = ("TRADE_REVIEW", "TRADE_ADVICE")
TEMPLATES = ("FUTURES_DECISION_V2", "TRADE_REVIEW_V1", "TRADE_COACH_V1")
VIEWS = ("futures_feed_events", "futures_run_events", "futures_latches")

# Generated from app.agents.definitions_v8 (python -m app.agents.definitions_v8); tests/test_m11_reviews.py compares.
AGENT_SEED_LINES_V8 = r"""
["AGENT_STEP_SCHEMA_V7", "AGENT_STEP_SCHEMA", 7, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V7\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"ARTIFACT carries exactly the one record your role writes (decision, review or advice) and nulls; ABSTAIN carries only abstain.\",\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"advice\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The coach's note for the trader's next decisions. Each evidence item is a review ID or a scoreboard row key from trade_coach; the server adds their counts.\",\"properties\":{\"avoid\":{\"description\":\"At most 3 items. Each at most 160 characters.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"confidence\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 6 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"lean\":{\"enum\":[\"LONG\",\"SHORT\",\"EITHER\",\"SIT_OUT\"],\"type\":\"string\"},\"setup\":{\"additionalProperties\":false,\"description\":\"The setup to look for, in the features the trader sees; each choice from the policy's sets, or null.\",\"properties\":{\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"stop_atr_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"when\":{\"description\":\"At most 240 characters.\",\"type\":\"string\"}},\"required\":[\"when\",\"stop_atr_multiple\",\"take_profit_multiple\",\"leverage\",\"max_hold_hours\"],\"type\":\"object\"}},\"required\":[\"lean\",\"setup\",\"avoid\",\"evidence\",\"confidence\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The futures trader's decision. ENTER_LONG and ENTER_SHORT take leverage, stop_multiple and max_hold_hours, and take_profit_multiple or null; TIGHTEN_STOP takes stop_multiple only; EXIT, HOLD and ABSTAIN take none of them. Never a price, quantity or level. advice_use is NO_ADVICE exactly when no advice note was shown.\",\"properties\":{\"action\":{\"enum\":[\"ENTER_LONG\",\"ENTER_SHORT\",\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"advice_note\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"},\"advice_use\":{\"enum\":[\"FOLLOWED\",\"PARTLY\",\"IGNORED\",\"NO_ADVICE\"],\"type\":\"string\"},\"cites\":{\"description\":\"At most 8 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"rationale\":{\"description\":\"At most 600 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"SETUP_FOR_ENTRY\",\"PROTECT_POSITION\",\"TAKE_PROFIT_EARLY\",\"NO_EDGE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"LIMIT_OR_COOLDOWN\",\"RISK_EVENT_AHEAD\",\"OTHER\"],\"type\":\"string\"},\"stop_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"leverage\",\"stop_multiple\",\"take_profit_multiple\",\"max_hold_hours\",\"reason_code\",\"rationale\",\"invalidation\",\"uncertainty_level\",\"cites\",\"advice_use\",\"advice_note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"review\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The trade reviewer's review of the fact sheet in trade_review. Grade the decision as it could be judged when it was made, apart from its result; never a price, a number or a count of your own.\",\"properties\":{\"decision_quality\":{\"enum\":[\"GOOD\",\"OK\",\"POOR\"],\"type\":\"string\"},\"entry_reason_held\":{\"enum\":[\"YES\",\"PARTLY\",\"NO\"],\"type\":\"string\"},\"entry_reason_note\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"},\"fact_sheet_id\":{\"type\":\"string\"},\"fact_sheet_sha256\":{\"type\":\"string\"},\"factors\":{\"description\":\"1 to 6 items.\",\"items\":{\"additionalProperties\":false,\"description\":\"One factor of the trade. The tag is from the tag list of its side (where). Each evidence item is a path into the fact sheet (keys from its root joined by dots, a list item by its index) or the evidence ID of a feed item the fact sheet lists.\",\"properties\":{\"effect\":{\"enum\":[\"HELPED\",\"HURT\",\"NEUTRAL\"],\"type\":\"string\"},\"evidence\":{\"description\":\"1 to 3 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"note\":{\"description\":\"At most 160 characters.\",\"type\":\"string\"},\"tag\":{\"enum\":[\"WITH_TREND\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"THIN_MARKET\",\"LATE_ENTRY\",\"SLIPPAGE\",\"STOP_TOO_TIGHT\",\"STOP_TOO_WIDE\",\"TARGET_TOO_FAR\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"DATA_PROBLEM\",\"AGENT_UNAVAILABLE\",\"GOOD_EXECUTION\"],\"type\":\"string\"},\"where\":{\"enum\":[\"INSIDE\",\"OUTSIDE\"],\"type\":\"string\"}},\"required\":[\"where\",\"tag\",\"effect\",\"evidence\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"invalidation_seen\":{\"enum\":[\"YES\",\"NO\",\"NOT_STATED\"],\"type\":\"string\"},\"lesson\":{\"description\":\"At most 200 characters.\",\"type\":\"string\"},\"tags\":{\"description\":\"1 to 5 items.\",\"items\":{\"enum\":[\"WITH_TREND\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"THIN_MARKET\",\"LATE_ENTRY\",\"SLIPPAGE\",\"STOP_TOO_TIGHT\",\"STOP_TOO_WIDE\",\"TARGET_TOO_FAR\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"DATA_PROBLEM\",\"AGENT_UNAVAILABLE\",\"GOOD_EXECUTION\"],\"type\":\"string\"},\"type\":\"array\"}},\"required\":[\"fact_sheet_id\",\"fact_sheet_sha256\",\"decision_quality\",\"entry_reason_held\",\"entry_reason_note\",\"invalidation_seen\",\"factors\",\"tags\",\"lesson\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"decision\",\"review\",\"advice\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v7\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v7\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v8 and ExecPlan 0040 section 4\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":7}", "9cf06d25341a5d9f1b8091d553ae4451a984b86938a9f0f2337023eb42459c11"]
["TOOL_CATALOG_V8", "TOOL_CATALOG", 8, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V8\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v8 and ExecPlan 0040 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: ENTER_LONG, ENTER_SHORT, EXIT, TIGHTEN_STOP, HOLD or ABSTAIN, with only the choices that action takes, each from the policy's set, and how it used the coach's note (advice_use, NO_ADVICE exactly when none was shown). The server writes the run, the position it saw, the context's hash, the note it showed and the policy; the engine computes every price, quantity, stop level, fee and margin. A note is never an order and changes no check.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"},{\"arguments\":[],\"description\":\"FINISH only. EVALUATOR in a trade review. One review of the closed trade's fact sheet the job context holds: its ID and hash, the decision graded apart from its result, whether the entry's reason held, whether its invalidation was seen, one to six factors from the tag list with their evidence (fact-sheet paths or the feed items it lists), one to five tags and one lesson. The server places the trade in the call-and-luck grid from the grade and the computed result.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_trade_review\"},{\"arguments\":[],\"description\":\"FINISH only. ANALYST in a trade coach job. One advice note for the trader: a lean, a setup with choices from the policy's sets, up to three things to avoid, the review IDs and scoreboard row keys it rests on, and a confidence. The server adds each cited row's counts, holds the confidence at LOW while fewer than ten trades are reviewed, and ends the note after four hours or at the next note.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_trade_advice\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":8}", "0a4411f9f34a44219953ce2fcdc25b3a35f05adfe0922bcaf6786971a594155a"]
["ROLE_GRANTS_V8", "ROLE_GRANTS", 8, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"record_trade_advice\"],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[\"record_trade_review\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V8\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v8 and ExecPlan 0040 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"TRADE_COACH_V1\"],\"COORDINATOR\":[\"FUTURES_DECISION_V2\"],\"EVALUATOR\":[\"TRADE_REVIEW_V1\"],\"RESEARCHER\":[]},\"version\":8}", "eb5ac503ed62b07d3db859976d6c41df8c638f5f6d9e850edde0c08a49948915"]
["TEMPLATES_V8", "TEMPLATES", 8, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V8\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"TRADE_REVIEW_AND_TRADE_COACH_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v8 and ExecPlan 0040 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V2\":{\"advice\":{\"answers\":\"ADVICE_USE_AND_ONE_LINE_AT_EVERY_DECISION\",\"label\":\"MODEL_AUTHORED_ADVICE_NOT_A_RULE\",\"lessons\":\"EACH_RECENT_TRADE'S_GRID_TAGS_AND_LESSON\",\"shown\":\"THE_NEWEST_UNEXPIRED_TRADE_ADVICE_WITH_THE_SERVER'S_COUNTS\"},\"artifact\":\"FUTURES_DECISION\",\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_FILL_OR_SHARP_MOVE\"},\"prompt\":\"TRADER_PROMPT_M11_V2\",\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"replaces\":\"FUTURES_DECISION_V1\",\"role\":\"COORDINATOR\",\"schedule\":{\"bar\":\"EVERY_FINISHED_15M_BAR\",\"coalescing\":\"A_TRIGGER_IS_COVERED_BY_ANY_DECISION_STARTED_AFTER_ITS_EVENT\",\"fill\":\"RIGHT_AFTER_EACH_FILL\",\"open_at_once\":1,\"sharp_move\":\"A_MOVE_OF_MORE_THAN_THE_POLICY'S_ATR_MULTIPLE_WITHIN_ITS_WINDOW\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"},\"TRADE_COACH_V1\":{\"artifact\":\"TRADE_ADVICE\",\"cutoff\":\"THE_LAST_REVIEWS_AND_THE_SCOREBOARD_AS_OF_ITS_START_WITH_THEIR_HASH_AND_THE_POLICY'S_SETS\",\"follow_on\":\"NONE\",\"note\":{\"confidence_low_below_reviewed_trades\":10,\"counts\":\"WRITTEN_BY_THE_SERVER_FOR_EACH_CITED_ROW\",\"expires_after_hours\":4,\"or\":\"THE_NEXT_NOTE\"},\"parameters\":{\"review\":\"THE_NEWEST_REVIEW'S_ID\"},\"prompt\":\"COACH_PROMPT_M11_V1\",\"purpose\":\"TRADE_COACH\",\"quiet_window\":\"HH:59:30_TO_HH:06:00_UTC\",\"reviews_shown\":20,\"role\":\"ANALYST\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"end_before_the_next_15m_bar_seconds\":60,\"no_decision_queued_or_open\":true,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"open_at_once\":1,\"starts_per_review\":3,\"when\":\"AFTER_EACH_NEW_REVIEW_ONCE_NO_FACT_SHEET_WAITS_FOR_ONE\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_TRADE_ADVICE_ARTIFACT\"},\"TRADE_REVIEW_V1\":{\"artifact\":\"TRADE_REVIEW\",\"cutoff\":\"THE_FACT_SHEET_WITH_ITS_HASH_THE_POLICY_SUMMARY_AND_THE_TAG_LIST\",\"follow_on\":\"THE_COACH_ONCE_NO_FACT_SHEET_WAITS_FOR_A_REVIEW\",\"grid\":{\"cells\":{\"GOOD:LOSS\":\"GOOD_CALL_UNLUCKY\",\"GOOD:WIN\":\"GOOD_CALL_WON\",\"POOR:LOSS\":\"MISTAKE\",\"POOR:WIN\":\"POOR_CALL_LUCKY\"},\"otherwise\":\"MIXED\",\"result\":{\"FLAT\":\"OTHERWISE\",\"LOSS\":\"R_BELOW_-0.1\",\"WIN\":\"R_ABOVE_0.1\"}},\"parameters\":{\"fact_sheet\":\"ITS_ID_AND_SHA256\"},\"prompt\":\"REVIEWER_PROMPT_M11_V1\",\"purpose\":\"TRADE_REVIEW\",\"quiet_window\":\"HH:59:30_TO_HH:06:00_UTC\",\"role\":\"EVALUATOR\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"end_before_the_next_15m_bar_seconds\":60,\"no_decision_queued_or_open\":true,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"not_reviewed_after_hours\":48,\"open_at_once\":1,\"starts_per_fact_sheet\":3,\"when\":\"ONE_PER_FACT_SHEET_OLDEST_FIRST\"},\"started_by\":[\"SYSTEM\"],\"tags\":{\"inside\":[\"LATE_ENTRY\",\"SLIPPAGE\",\"STOP_TOO_TIGHT\",\"STOP_TOO_WIDE\",\"TARGET_TOO_FAR\",\"EXIT_TOO_EARLY\",\"HELD_TOO_LONG\",\"DATA_PROBLEM\",\"AGENT_UNAVAILABLE\",\"GOOD_EXECUTION\"],\"outside\":[\"WITH_TREND\",\"AGAINST_TREND\",\"RANGE_CHOP\",\"VOLATILITY_SPIKE\",\"NEWS_OR_RELEASE\",\"FUNDING_COST\",\"THIN_MARKET\"]},\"writes\":\"ONE_TRADE_REVIEW_ARTIFACT\"}},\"version\":8}", "328e9e317209fbd4b3016c259162e11e92e4871a3e4a8b1a85dbff1f437d36c6"]
["BUDGETS_V8", "BUDGETS", 8, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120,\"TRADE_COACH\":24,\"TRADE_REVIEW\":24},\"fact_sheet_max_bytes\":8192,\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V8\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"FUTURES_DECISION_V2\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":32768,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5; ExecPlan 0040 section 4.6\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V2\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"TRADE_COACH_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":300,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300},\"TRADE_REVIEW_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":300,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":8}", "c04b704f3f3bcfac2cb5cc6045721b1a83b0397e43f5ffc12de9cf2e98a0d523"]
["COACH_PROMPT_M11_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COACH_PROMPT_M11_V1\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"ee0c7a1f8adf71ed5dabab04081249306599c24dc9666366e82274ed4dcf2210\",\"source\":\"services/agent-runner/prompts/m11/coach.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "9f10869894ad37412842aeaf0f7309ac2f03ea8be4d707b2f415feb2037a85f2"]
["REVIEWER_PROMPT_M11_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"REVIEWER_PROMPT_M11_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"1e2e6cd020f5225b30eaf86f0f947dbba0745752321ecb9f8b96b94ae4620ad3\",\"source\":\"services/agent-runner/prompts/m11/reviewer.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "84147d0516cb4e11409a858cd8e27197151dfae34c5836cc0a66d17a500e01ad"]
["TRADER_PROMPT_M11_V2", "PROMPT", 2, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V2\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"971d2a8d194292fb1cd2fca94dade88112be440847bc7b1c2b2000a20cc012ae\",\"source\":\"services/agent-runner/prompts/m11/trader.v2.md\",\"status\":\"CODE_OWNED\",\"version\":2}", "91ecaf545d026e16dff9b73d06626d47fb030d2cde6c16d8aa5394571d07f72b"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    """The frozen generation-8 documents, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V8.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-8 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


TABLE_SQL = """
CREATE TABLE trade_fact_sheets (
    id uuid PRIMARY KEY,
    position_id uuid NOT NULL UNIQUE REFERENCES futures_positions(id),
    run_id uuid NOT NULL REFERENCES futures_runs(id),
    opened_at timestamptz NOT NULL,
    closed_at timestamptz NOT NULL,
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    trend_1h varchar(7) NOT NULL CHECK (trend_1h IN ('UP','DOWN','FLAT','UNKNOWN')),
    leverage varchar(1) NOT NULL CHECK (leverage IN ('1','2')),
    stop_multiple varchar(3) NOT NULL CHECK (stop_multiple IN ('1.0','1.5','2.0','3.0')),
    ended_by varchar(12) NOT NULL,
    entry_hours varchar(5) NOT NULL CHECK (entry_hours IN ('00-08','08-16','16-24')),
    advice_use varchar(9) CHECK (advice_use IN ('FOLLOWED','PARTLY','IGNORED','NO_ADVICE')),
    result varchar(4) NOT NULL CHECK (result IN ('WIN','LOSS','FLAT')),
    r numeric,
    net_pnl numeric NOT NULL,
    risk numeric NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 8192),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX trade_fact_sheets_closed ON trade_fact_sheets (closed_at);
CREATE UNIQUE INDEX agent_artifacts_one_trade_review ON agent_artifacts ((document->>'fact_sheet_id'))
    WHERE kind = 'TRADE_REVIEW';
"""

GUARDS_SQL = """
-- A fact sheet comes only from the agent identity, describes its closed position, and its columns are its document's.
CREATE FUNCTION asl_trade_fact_sheet_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE p record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a fact sheet is written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT run_id, side, leverage, stop_multiple, opened_at, closed_at, close_reason, state INTO p
        FROM agent_read.futures_positions WHERE id = NEW.position_id;
    IF NOT FOUND OR p.state <> 'CLOSED' OR p.run_id <> NEW.run_id OR p.side <> NEW.side
            OR p.leverage <> CAST(NEW.leverage AS numeric) OR p.stop_multiple <> CAST(NEW.stop_multiple AS numeric)
            OR p.opened_at <> NEW.opened_at OR p.closed_at <> NEW.closed_at OR p.close_reason <> NEW.ended_by THEN
        RAISE EXCEPTION 'a fact sheet describes its closed futures position'; END IF;
    IF d->>'schema' IS DISTINCT FROM 'TRADE_FACT_SHEET_V1' OR d->>'fact_sheet_id' IS DISTINCT FROM NEW.id::text
            OR d->>'position_id' IS DISTINCT FROM NEW.position_id::text
            OR d->>'run_id' IS DISTINCT FROM NEW.run_id::text
            OR CAST(d->'trade'->>'opened_at' AS timestamptz) IS DISTINCT FROM NEW.opened_at
            OR CAST(d->'trade'->>'closed_at' AS timestamptz) IS DISTINCT FROM NEW.closed_at
            OR d->'trade'->>'side' IS DISTINCT FROM NEW.side
            OR d->'trade'->>'leverage' IS DISTINCT FROM NEW.leverage
            OR d->'trade'->'stop'->>'multiple' IS DISTINCT FROM NEW.stop_multiple
            OR d->'trade'->>'ended_by' IS DISTINCT FROM NEW.ended_by
            OR d->'trade'->>'entry_hours_utc' IS DISTINCT FROM NEW.entry_hours
            OR d->'outside'->'at_entry'->>'trend_1h' IS DISTINCT FROM NEW.trend_1h
            OR d->'inside'->'entry_decision'->>'advice_use' IS DISTINCT FROM NEW.advice_use
            OR d->'result'->>'class' IS DISTINCT FROM NEW.result
            OR CAST(d->'result'->>'r' AS numeric) IS DISTINCT FROM NEW.r
            OR CAST(d->'result'->>'net_pnl' AS numeric) IS DISTINCT FROM NEW.net_pnl
            OR CAST(d->'result'->>'risk' AS numeric) IS DISTINCT FROM NEW.risk THEN
        RAISE EXCEPTION 'a fact sheet''s columns are its document''s values'; END IF;
    RETURN NEW;
END $$;

-- A review or a note comes only from the agent identity, for its own running workflow of its template. A review names
-- a stored fact sheet by its ID and hash and sits in the grid cell its grade and that sheet's result give; a note ends
-- four hours after it is recorded.
CREATE FUNCTION asl_trade_review_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; s record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a trade review or note comes only from its agent'; END IF;
    SELECT template_id, purpose, role, state, parent_id INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL
            OR (NEW.kind = 'TRADE_REVIEW'
                AND (w.template_id, w.purpose, w.role) <> ('TRADE_REVIEW_V1', 'TRADE_REVIEW', 'EVALUATOR'))
            OR (NEW.kind = 'TRADE_ADVICE'
                AND (w.template_id, w.purpose, w.role) <> ('TRADE_COACH_V1', 'TRADE_COACH', 'ANALYST')) THEN
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

CREATE TRIGGER trade_fact_sheets_content BEFORE INSERT ON trade_fact_sheets
    FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard();
CREATE TRIGGER trade_fact_sheets_guard BEFORE INSERT ON trade_fact_sheets
    FOR EACH ROW EXECUTE FUNCTION asl_trade_fact_sheet_guard();
CREATE TRIGGER trade_fact_sheets_immutable BEFORE UPDATE OR DELETE ON trade_fact_sheets
    FOR EACH ROW EXECUTE FUNCTION asl_immutable();
CREATE TRIGGER agent_artifacts_trade_review BEFORE INSERT ON agent_artifacts
    FOR EACH ROW WHEN (NEW.kind IN ('TRADE_REVIEW','TRADE_ADVICE')) EXECUTE FUNCTION asl_trade_review_guard();
"""

# 0020's futures decision guard, which also accepts generation 8's trader. Downgrade restores 0020's text exactly.
DECISION_GUARD = """
CREATE OR REPLACE FUNCTION asl_futures_decision_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a futures decision comes only from the trader'; END IF;
    SELECT template_id, purpose, state INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.template_id {templates} OR w.purpose <> 'DECISION' OR w.state <> 'RUNNING' THEN
        RAISE EXCEPTION 'a futures decision needs its running futures decision workflow'; END IF;
    RETURN NEW;
END $$;
"""
TRADERS_V1 = "<> 'FUTURES_DECISION_V1'"
TRADERS_V2 = "NOT IN ('FUTURES_DECISION_V1','FUTURES_DECISION_V2')"

# What the fact sheet reads that 0020's views do not show: each fill's book levels and marks, the feed's events, the
# run's events and the latches. 0020's fills view gains columns at its end only.
FILLS_VIEW = """
CREATE OR REPLACE VIEW agent_read.futures_fills WITH (security_barrier = true) AS
    SELECT id, seq, position_id, kind, reason, order_side, quantity, price, fee, filled_at{columns} FROM futures_fills;
"""
FILLS_COLUMNS = ", average_price, levels, quote_second, mark_second, mark_price"
VIEWS_SQL = """
CREATE VIEW agent_read.futures_feed_events WITH (security_barrier = true) AS
    SELECT code, at FROM perp_feed_events;
CREATE VIEW agent_read.futures_run_events WITH (security_barrier = true) AS
    SELECT run_id, kind, at, detail->>'cause' AS cause FROM futures_run_events;
CREATE VIEW agent_read.futures_latches WITH (security_barrier = true) AS
    SELECT run_id, cause, latched_at, resolved_at FROM futures_latches;
"""


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
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V2))
    op.execute(FILLS_VIEW.replace("{columns}", FILLS_COLUMNS))
    op.execute(VIEWS_SQL)
    op.execute(f"GRANT SELECT ON {', '.join('agent_read.' + view for view in VIEWS)} TO asl_agent")
    op.execute("GRANT SELECT, INSERT ON trade_fact_sheets TO asl_agent")
    op.execute("GRANT SELECT ON trade_fact_sheets TO asl_api")
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # A runtime profile that binds generation 8 by hash would bind definitions that no longer exist (as 0016's).
    generation8 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM trade_fact_sheets) "
        f"+ (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} "
        f"OR purpose IN {_quoted(PURPOSES_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ARTIFACTS_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation8})"
    ).scalar_one()
    if held:
        raise RuntimeError("trade review records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-8 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(f"DROP VIEW {', '.join('agent_read.' + view for view in VIEWS)}")
    # A view loses columns only by being made again; 0020's grant is restored with it.
    op.execute("DROP VIEW agent_read.futures_fills")
    op.execute(FILLS_VIEW.replace("{columns}", "").replace("CREATE OR REPLACE VIEW", "CREATE VIEW"))
    op.execute("GRANT SELECT ON agent_read.futures_fills TO asl_agent")
    op.execute(DECISION_GUARD.replace("{path}", SEARCH_PATH).replace("{templates}", TRADERS_V1))
    op.execute("DROP TRIGGER agent_artifacts_trade_review ON agent_artifacts")
    op.execute("DROP INDEX agent_artifacts_one_trade_review")
    op.execute("DROP TABLE trade_fact_sheets")
    op.execute("DROP FUNCTION asl_trade_fact_sheet_guard(), asl_trade_review_guard()")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               f"ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(PURPOSES)})")
