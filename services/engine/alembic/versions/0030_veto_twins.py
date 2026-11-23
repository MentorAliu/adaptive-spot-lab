"""ExecPlan 0041 part 2: the veto twin, the momentum twin, the entry veto (generation 12) and the placebo.

Revision ID: 0030_veto_twins
Revises: 0029_agent_providers

ExecPlan 0041 sections 4.1 and 4.3. Additive: nothing of the owner's account, its journal, its reservations, the
futures engine's tables, the trader or the three twins of part 1 changes. Each guard resolves names under a fixed search
path.

- ``TWIN_SET_V2`` in ``execution_definitions`` (frozen here, checked against the code): part 1's three twins carried
  with the same rules and values, and ``TREND_VETO`` and ``MOMENTUM_1W``.
- ``futures_twins`` takes the two new names and ``rule_day``, the UTC day whose momentum signal is spent; its events
  take ``DAY_SIGNAL``, the momentum rule's reading of each day; its candidates take the rule ``DAY_MOMENTUM`` and, for
  the veto twin, the verdict the twin applied (``GO``, ``HALVE``, ``VETO`` or ``NO_ANSWER``) and the request it
  answered.
- ``futures_twin_veto_requests``: each entry the veto twin held and asked about, with the candidate as its step planned
  it, its hash and its deadline; written by the execution identity alone, never changed.
- ``futures_twin_vetoes``: the veto agent's answer to one request, written by the agent identity alone from its own
  running ``ENTRY_VETO_V1`` workflow bound to that request; the time it was recorded is the database's.
- ``futures_twin_placebo``: once a UTC day, the placebo's comparison of the veto's answers with the plain rule and with
  random answers at its own rates, written by the agent identity alone.
- ``futures_decision_scores`` scores the new twins' candidates too; ``agent_read`` shows the requests and the verdicts
  the twin applied to the agent identity.
- The workflow purpose and artifact kind ``ENTRY_VETO``, and generation 12's agent definitions (frozen here, checked
  against the code).

Downgrade refuses once any request, answer, placebo row, new twin, momentum candidate or generation-12 workflow exists,
or a runtime profile binds generation 12; otherwise it removes all of it.
"""

import hashlib
import json

from alembic import op

revision = "0030_veto_twins"
down_revision = "0029_agent_providers"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
TWINS_V1 = ("HOLD", "TREND", "TREND_GATED")
TWINS_ADDED = ("TREND_VETO", "MOMENTUM_1W")
RULES_V1 = ("HOLD_START", "EMA_CROSS")
EVENTS_V1 = ("STARTED", "LATCHED", "LATCH_CLEARED", "STOPPED", "FAULTED", "DAILY_REFERENCE", "WALLET_CHECKED", "NOTE")
VETOES = ("GO", "HALVE", "VETO", "NO_ANSWER")
REASONS = ("RELEASE_WITHIN_2H", "FUNDING_EXTREME", "SPREAD_WIDE", "FEED_GAP", "HEADLINES_CONTRADICT", "TREND_WEAK",
           "NONE")
# The checks as migration 0025 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW", "COIN_NOTE", "TRADE_REVIEW", "TRADE_COACH",
            "DECISION_REVIEW")
PURPOSES_ADDED = ("ENTRY_VETO",)
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE", "FUTURES_DECISION", "TRADE_REVIEW", "TRADE_ADVICE",
                  "DECISION_REVIEW")
ARTIFACTS_ADDED = ("ENTRY_VETO",)
TEMPLATES = ("ENTRY_VETO_V1",)
TABLES = ("futures_twin_placebo", "futures_twin_vetoes", "futures_twin_veto_requests")

# The frozen set: ``python -m app.futures.twins v2`` prints it; tests/test_m11_veto_unit.py checks it.
TWIN_SEED_LINES_V2 = r"""
["TWIN_SET_V2", "FUTURES_TWINS", 2, "PROPOSED", "{\"carried\":{\"from\":\"TWIN_SET_V1\",\"new\":\"A_TWIN_OF_THIS_SET_THAT_HAS_NEVER_STARTED_STARTS_SEGMENT_1_UNDER_THIS_SET\",\"rule\":\"A_TWIN_WHOSE_RULE_AND_VALUES_ARE_UNCHANGED_GOES_ON_IN_THE_SEGMENT_IT_STARTED_UNDER_ITS_SET\",\"twins\":[\"HOLD\",\"TREND\",\"TREND_GATED\"]},\"comparison\":{\"bootstrap\":\"STATIONARY_POLITIS_ROMANO_1994\",\"confidence\":\"0.95\",\"day\":\"UTC\",\"gap_day\":\"EITHER_ACCOUNT_WITHOUT_A_VALID_VALUE_AT_A_MIDNIGHT_A_GAP_OVER_65_MIN_OR_AN_INVALID_ONE\",\"mean_block_days\":3,\"minimum\":{\"paired_days\":30,\"trader_closed_trades\":60},\"resamples\":2000,\"seed\":\"THE_SET'S_HASH_THE_TWIN'S_AND_THE_RUN'S_IDS\",\"statistic\":\"PAIRED_DAILY_LOG_RETURN_DIFFERENCES_TRADER_NAV_MINUS_TWIN_EQUITY\",\"threshold\":\"NONE_NOTHING_IS_PROMOTED_OR_CHANGED\"},\"cost\":\"FUTURES_COST_V1\",\"funding_filter\":{\"basis\":\"THREE_TIMES_BINANCE'S_DEFAULT_RATE_OF_0.01%\",\"max_abs_rate\":\"0.0003\",\"rate\":\"THE_MARK'S_ANNOUNCED_FUNDING_RATE\",\"refuse\":\"AN_ENTRY_ON_THE_PAYING_SIDE_WHILE_THE_RATE'S_MAGNITUDE_IS_ABOVE_THE_MAX\"},\"gate\":{\"distance\":\"THE_PLANNED_ENTRY_FILL_TO_THE_ROUNDED_STOP\",\"multiple\":\"3\",\"price\":\"THE_PLANNED_ENTRY_FILL\",\"refuse\":\"THE_STOP'S_DISTANCE_PER_UNIT_BELOW_MULTIPLE_X_THE_ROUND_TRIP_COST_PER_UNIT\",\"round_trip_cost_per_unit\":\"2_X_TAKER_X_PRICE_PLUS_2_X_SLIPPAGE_X_PRICE_PLUS_THE_QUOTE'S_SPREAD\"},\"id\":\"TWIN_SET_V2\",\"kind\":\"FUTURES_TWINS\",\"label\":\"ISOLATED_PAPER_ACCOUNTS_NOT_THE_OWNER'S_ACCOUNT\",\"ledger\":\"THEIR_OWN_ROWS_NO_JOURNAL_NO_RESERVATION_NO_ACCOUNT_STATE\",\"momentum\":{\"acts\":\"FLAT_ENTERS_THE_SIGNAL'S_SIDE_THE_OTHER_SIDE_FLIPS_THE_SAME_SIDE_HOLDS\",\"after_liquidation\":\"THE_NEXT_UTC_DAY'S_SIGNAL\",\"candles\":\"COMPLETE_UTC_DAYS_EACH_24_COMPLETE_1H_CANDLES_BUILT_FROM_FINAL_1M_CANDLES\",\"day_spent\":\"BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_COMPLETE_YET_OR_AN_OPERATIONAL_REFUSAL_TRIES_AGAIN_AT_THE_DAY'S_NEXT_BAR\",\"evaluated\":\"AT_THE_FIRST_FINISHED_15M_BAR_OF_EACH_UTC_DAY_THE_TWIN_READS_FROM_THE_DAY_AFTER_IT_STARTED\",\"exit\":\"ONLY_ON_A_FLIP_OR_A_LIQUIDATION\",\"flip\":\"THE_EXIT_ON_THE_BOOK_THEN_THE_ENTRY_ON_THE_LEVELS_THE_EXIT_LEFT\",\"leverage\":\"1\",\"limits\":\"NONE\",\"lookback_days\":8,\"signal\":\"LONG_IF_THE_LAST_COMPLETE_UTC_DAY'S_CLOSE_IS_ABOVE_THE_CLOSE_OF_THE_DAY_8_DAYS_BEFORE_IT_SHORT_IF_BELOW_NO_CHANGE_IF_EQUAL\",\"warmup\":\"BOTH_DAYS_COMPLETE_ELSE_READ_AGAIN_AT_THE_DAY'S_NEXT_BAR\"},\"placebo\":{\"arms\":{\"RANDOM\":\"EACH_ANSWERED_CANDIDATE_DRAWN_AT_THE_AGENT'S_OWN_GO_HALVE_VETO_RATES_NO_ANSWER_STAYS_GO\",\"TREND_ARM\":\"EVERY_CANDIDATE_GO\",\"VETO_ARM\":\"THE_AGENT'S_VERDICTS\"},\"candidates\":\"EVERY_TREND_VETO_CANDIDATE_ASKED_WHOSE_24H_HAS_PASSED\",\"minimum_candidates\":60,\"model\":\"1M_CANDLES: THE_ENTRY_AT_THE_PLANNED_PRICE_AT_THE_ASKED_QUOTE; THE_STOP_ON_THE_CANDLES_AT_ITS_LEVEL_OR_A_GAPPED_OPEN_WITH_THE_SLIPPAGE_AGAINST_IT; THE_OPPOSITE_RELATION_OF_THE_1H_EMAS_AT_THE_NEXT_HOUR'S_OPEN; THE_24H_TIME_EXIT; BOTH_TAKER_FEES; THE_SETTLED_FUNDING_CROSSED\",\"seed\":\"THE_SET'S_HASH_THE_TWIN'S_ID_AND_THE_NEWEST_CANDIDATE\",\"streams\":1000,\"success\":\"THE_VETO_ARM_BEATS_95%_OF_THE_STREAMS_AND_THE_PAIRED_DAILY_INTERVAL_OF_TREND_VETO_MINUS_TREND_IS_ABOVE_ZERO\",\"threshold\":\"NONE_NOTHING_IS_PROMOTED_OR_CHANGED\",\"unit\":\"R_THE_NET_OVER_THE_FULL_RISK_ENTRY'S_LOSS_AT_THE_STOP_WITH_BOTH_FEES_AND_SLIPPAGE\",\"weights\":{\"GO\":\"1\",\"HALVE\":\"0.5\",\"NO_ANSWER\":\"1\",\"VETO\":\"0\"},\"when\":\"ONCE_A_UTC_DAY_FROM_00:40\"},\"policy\":\"FUTURES_POLICY_V1\",\"protection\":\"EVERY_SECOND_AFTER_THE_OWNER'S_STEP_LIQUIDATION_STOP_TIME_EXIT_WHATEVER_THE_AGENTS_OR_THE_RUN\",\"shared\":\"THE_POLICY'S_SIZING_COOLDOWNS_ENTRIES_PER_UTC_DAY_AND_LATCHES_AND_THE_COST'S_FILLS_FEES_FUNDING_AND_LIQUIDATION_ON_THE_SAME_QUOTES_AND_MARKS\",\"source\":\"ExecPlan 0041 sections 4.1 and 4.3 (part 2), approved by the owner on 2026-11-02\",\"start_equity\":\"10000\",\"status\":\"PROPOSED\",\"step_errors\":{\"fault_after\":60,\"other\":\"FAULTS_THAT_TWIN_ALONE\",\"retried\":\"A_DATABASE_TIMEOUT_A_LOCK_WAIT_OR_A_DEADLOCK_THE_NEXT_SECOND\"},\"trend\":{\"atr\":\"THE_POLICY'S_15M_WILDER_ATR\",\"bar_max_age_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"candles\":\"COMPLETE_1H_CANDLES_BUILT_FROM_FINAL_1M_CANDLES_THE_NEWEST_CONTIGUOUS_RUN\",\"drawdown\":\"LATCHED_THEN_STOPPED_ONCE_FLAT_THE_SEGMENT_ENDS\",\"ema_seed\":\"SMA_OF_FIRST_COMPLETE_PERIOD\",\"evaluated\":\"ONCE_AT_EACH_FINISHED_15M_BAR_AFTER_ITS_LAST_MINUTE_IS_FINAL_OR_60_S\",\"exit\":\"AT_A_FINISHED_15M_BAR_WHEN_THE_HOUR_THAT_FINISHED_LAST_HAS_THE_FAST_EMA_AGAINST_THE_SIDE\",\"fast_ema\":20,\"interval_ms\":3600000,\"leverage\":\"1\",\"limits\":\"THE_POLICY'S_COOLDOWNS_ENTRIES_PER_UTC_DAY_DAILY_LOSS_AND_DRAWDOWN\",\"long_cross\":\"PREV_FAST_LTE_SLOW_AND_CUR_FAST_GT_SLOW\",\"max_hold_hours\":24,\"risk_fraction\":\"THE_POLICY'S\",\"run_window_max_hours\":720,\"short_cross\":\"PREV_FAST_GTE_SLOW_AND_CUR_FAST_LT_SLOW\",\"signal\":\"A_CROSS_ON_THE_HOUR_THAT_FINISHED_LAST_LIVE_AT_EACH_15M_BAR_OF_THE_NEXT_HOUR\",\"signal_spent\":\"BY_A_FILL_OR_A_REFUSAL_OF_THE_GATE_OR_THE_FUNDING_FILTER\",\"slow_ema\":50,\"stop_atr_multiple\":\"2.0\",\"take_profit\":null,\"warmup_hours\":100},\"twins\":[{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"HOLD\",\"latches\":\"NONE\",\"leverage\":\"1\",\"max_hold_hours\":null,\"reentry\":\"NEVER\",\"rule\":\"LONG_ONCE_AT_THE_FIRST_FINISHED_15M_BAR_THEN_HOLD\",\"size\":\"THE_WHOLE_WALLET_LESS_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE\",\"stop\":null,\"take_profit\":null},{\"funding_filter\":false,\"gate\":false,\"id\":\"TREND\",\"rule\":\"EMA_CROSS_1H\"},{\"funding_filter\":true,\"gate\":true,\"id\":\"TREND_GATED\",\"rule\":\"EMA_CROSS_1H\"},{\"entry\":\"EACH_ENTRY_PASSES_THE_VETO_AGENT_FIRST\",\"funding_filter\":false,\"gate\":false,\"id\":\"TREND_VETO\",\"rule\":\"EMA_CROSS_1H\"},{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"MOMENTUM_1W\",\"latches\":\"NONE\",\"leverage\":\"1\",\"max_hold_hours\":null,\"rule\":\"DAY_MOMENTUM\",\"size\":\"THE_WHOLE_WALLET_LESS_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE\",\"stop\":null,\"take_profit\":null}],\"valuation\":\"CASH_PLUS_THE_OPEN_POSITION'S_UNREALIZED_PNL_AT_THE_MARK_LESS_SETTLED_FUNDING_WAITING_FOR_THE_FREE_WALLET\",\"version\":2,\"veto\":{\"agent\":\"ENTRY_VETO_V1\",\"asked\":\"WHEN_THE_RULE'S_ENTRY_PASSES_EVERY_CHECK_AND_IS_SIZED_THE_TWIN_HOLDS_IT_AND_ASKS\",\"cost_of_asking\":\"THE_FILL_PRICE_AGAINST_THE_PRICE_PLANNED_AT_THE_ASKED_QUOTE\",\"deadline_seconds\":120,\"fill\":\"AT_THE_NEWEST_QUOTE_AFTER_THE_ANSWER_CHECKED_AND_SIZED_AGAIN_AT_MOST_THE_POLICY'S_DECISION_AGE_AFTER_THE_BAR\",\"open_at_once\":1,\"per_utc_day\":24,\"quiet_window\":\"NONE\",\"reason_none\":\"EXACTLY_WITH_GO\",\"reasons\":[\"RELEASE_WITHIN_2H\",\"FUNDING_EXTREME\",\"SPREAD_WIDE\",\"FEED_GAP\",\"HEADLINES_CONTRADICT\",\"TREND_WEAK\",\"NONE\"],\"shown\":\"THE_TRADER'S_MARKET_FEATURES_CANDLES_HEADLINES_AND_RELEASES_THE_TWIN'S_ACCOUNT_AND_THE_CANDIDATE\",\"silence\":\"NO_ANSWER_BY_THE_DEADLINE_IS_GO_RECORDED_NO_ANSWER\",\"slot\":\"AFTER_THE_TRADER: NOT_WHILE_A_TRADER_DECISION_IS_DUE_QUEUED_OR_OPEN; A_DECISION_QUEUED_MEANWHILE_CANCELS_THE_CALL\",\"started_by\":\"SYSTEM\",\"twin\":\"TREND_VETO\",\"verdicts\":{\"GO\":\"THE_RULE'S_ENTRY\",\"HALVE\":\"THE_ENTRY_AT_HALF_THE_POLICY'S_RISK_FRACTION\",\"VETO\":\"NO_ENTRY_THE_HOUR'S_CROSS_IS_SPENT\"}},\"wallet_check\":{\"every_seconds\":3600,\"fault\":\"STOPS_THAT_TWIN_ALONE\",\"formula\":\"START_PLUS_REALIZED_PNL_MINUS_FEES_PLUS_FUNDING_RESERVED_THE_OPEN_MARGIN\"}}", "ff907a4a55488e0459c4eec16316e57f33ae71fbcd95c41d42e3a191a41e2c29"]
"""

# Generated from app.agents.definitions_v12 (python -m app.agents.definitions_v12); tests/test_m11_veto_unit.py
# compares.
AGENT_SEED_LINES_V12 = r"""
["AGENT_STEP_SCHEMA_V9", "AGENT_STEP_SCHEMA", 9, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V9\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"ARTIFACT carries the veto and a null abstain; ABSTAIN carries only abstain.\",\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"veto\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"Your answer on the held entry in entry_veto: request_id and request_sha256 copied exactly; GO lets it in, HALVE lets it in at half the risk, VETO keeps it out. reason is NONE exactly with GO.\",\"properties\":{\"confidence\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"note\":{\"description\":\"At most 160 characters.\",\"type\":\"string\"},\"reason\":{\"enum\":[\"RELEASE_WITHIN_2H\",\"FUNDING_EXTREME\",\"SPREAD_WIDE\",\"FEED_GAP\",\"HEADLINES_CONTRADICT\",\"TREND_WEAK\",\"NONE\"],\"type\":\"string\"},\"request_id\":{\"type\":\"string\"},\"request_sha256\":{\"type\":\"string\"},\"verdict\":{\"enum\":[\"GO\",\"HALVE\",\"VETO\"],\"type\":\"string\"}},\"required\":[\"request_id\",\"request_sha256\",\"verdict\",\"reason\",\"note\",\"confidence\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"veto\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v9\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The veto holds no tool: always null.\",\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v9\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v12 and ExecPlan 0041 section 4.3\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":9}", "dfc0c14f6f1d13a462b10619db83b1c3b15dc99db2f7661c57fea9296f54fad7"]
["TOOL_CATALOG_V12", "TOOL_CATALOG", 12, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V12\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v12 and ExecPlan 0041 section 4.3\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[],\"description\":\"FINISH only. EVALUATOR in an entry veto. One answer on the entry the TREND_VETO twin holds, named by the request's ID and hash: GO (the rule's entry), HALVE (the entry at half the policy's risk fraction) or VETO (no entry; the hour's cross is spent), a reason from VETO_REASONS_V1 (NONE exactly with GO), a one-line note and a confidence. Only that twin's step reads it; the twin checks, sizes and fills the entry itself, and no answer by the deadline is GO.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_entry_veto\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":12}", "dcda9c8fdc3526a2f997086adcf93a06626f069ea1efded1edaab0a252f81297"]
["ROLE_GRANTS_V12", "ROLE_GRANTS", 12, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[],\"EVALUATOR\":[\"record_entry_veto\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V12\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v12 and ExecPlan 0041 section 4.3\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[],\"EVALUATOR\":[\"ENTRY_VETO_V1\"],\"RESEARCHER\":[]},\"version\":12}", "20e9fe5223e8ff7ba36b718fca3a43bef3898d085578d994819bbb03f99f2e8e"]
["TEMPLATES_V12", "TEMPLATES", 12, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V12\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"ENTRY_VETO_WITH_THE_REVIEWS_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v12 and ExecPlan 0041 section 4.3\",\"status\":\"CODE_OWNED\",\"templates\":{\"ENTRY_VETO_V1\":{\"artifact\":\"ENTRY_VETO\",\"cutoff\":\"THE_REQUEST_WITH_ITS_HASH_AND_THE_TRADER'S_MARKET_BLOCKS_AS_OF_ITS_START\",\"deadline_seconds\":120,\"follow_on\":\"NONE\",\"parameters\":{\"request\":\"ITS_ID_AND_SHA256\"},\"prompt\":\"VETO_PROMPT_M11_V1\",\"purpose\":\"ENTRY_VETO\",\"quiet_window\":\"NONE\",\"reads_it\":\"ONLY_THE_TREND_VETO_TWIN'S_STEP\",\"reason_none\":\"EXACTLY_WITH_GO\",\"reasons\":[\"RELEASE_WITHIN_2H\",\"FUNDING_EXTREME\",\"SPREAD_WIDE\",\"FEED_GAP\",\"HEADLINES_CONTRADICT\",\"TREND_WEAK\",\"NONE\"],\"role\":\"EVALUATOR\",\"schedule\":{\"gate\":{\"no_decision_queued_or_open\":true,\"starts_per_request\":1,\"starts_while_seconds_left_at_least\":30,\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_CANCELED_AT_THE_RUNNER\"},\"open_at_once\":1,\"per_utc_day\":24,\"when\":\"ONE_PER_REQUEST_THE_TWIN_HOLDS_OPEN_OLDEST_FIRST\"},\"shown\":[\"THE_CANDIDATE\",\"THE_TWIN'S_ACCOUNT\",\"MARKET\",\"FEATURES\",\"CANDLES\",\"HEADLINES\",\"RELEASES\",\"THE_POLICY'S_SUMMARY\",\"THE_REASON_LIST\"],\"silence\":\"NO_ANSWER_IS_GO_AT_THE_REQUEST'S_DEADLINE\",\"started_by\":[\"SYSTEM\"],\"twin\":\"TREND_VETO\",\"twin_set\":\"TWIN_SET_V2\",\"verdicts\":[\"GO\",\"HALVE\",\"VETO\"],\"writes\":\"ONE_ENTRY_VETO_ARTIFACT_AND_ONE_TWIN_VERDICT_ROW\"}},\"version\":12}", "ea05c3c478a1b2946bc571facbc7e28d4180a76c56c6f842609d5c02a4f06f1a"]
["BUDGETS_V12", "BUDGETS", 12, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"ENTRY_VETO\":24},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V12\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[\"ENTRY_VETO_V1\"],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0041 section 4.3\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":110,\"system_queue_expiry_seconds\":300,\"templates\":{\"ENTRY_VETO_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":110,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":115}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":12}", "d2a858c1d482fe630f4298af57dc5c7def33c68b8cf896b072853fba7d2eed11"]
["VETO_PROMPT_M11_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"VETO_PROMPT_M11_V1\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"763f37422bb52297c6e5d1b51afff7263ac19bf7c2879a565bf4278dfb67c10b\",\"source\":\"services/agent-runner/prompts/m11/veto.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "454b765d196a2f90af12041f8fe4d95d1ec215f6516c46809e582407b30dd914"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def _frozen(lines, kinds, what):
    rows = []
    for line in lines.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in kinds:
            raise RuntimeError(f"frozen {what} is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def twin_rows():
    return _frozen(TWIN_SEED_LINES_V2, ("FUTURES_TWINS",), "twin set")


def agent_rows():
    return _frozen(AGENT_SEED_LINES_V12, AGENT_KINDS, "generation-12 agent definition")


TABLES_SQL = """
ALTER TABLE futures_twins ADD COLUMN rule_day date;

CREATE TABLE futures_twin_veto_requests (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    twin_id uuid NOT NULL REFERENCES futures_twins(id),
    bar_open_ms bigint NOT NULL CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    signal_open_ms bigint NOT NULL CHECK (signal_open_ms >= 0 AND signal_open_ms % 3600000 = 0),
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    asked_at timestamptz NOT NULL,
    deadline_at timestamptz NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 16384),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (twin_id, bar_open_ms),
    CONSTRAINT futures_twin_veto_request_deadline CHECK (deadline_at > asked_at),
    CONSTRAINT futures_twin_veto_request_hash CHECK (sha256 = encode(sha256(convert_to(canonical, 'UTF8')), 'hex')
        AND document = CAST(canonical AS jsonb))
);

CREATE TABLE futures_twin_vetoes (
    id uuid PRIMARY KEY,
    request_id uuid NOT NULL UNIQUE REFERENCES futures_twin_veto_requests(id),
    workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id),
    artifact_sha256 varchar(64) NOT NULL CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    verdict varchar(5) NOT NULL CHECK (verdict IN ('GO','HALVE','VETO')),
    reason varchar(20) NOT NULL CHECK (reason IN {reasons}),
    note text NOT NULL CHECK (char_length(note) BETWEEN 1 AND 160),
    confidence varchar(6) NOT NULL CHECK (confidence IN ('LOW','MEDIUM','HIGH')),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_twin_veto_reason CHECK ((verdict = 'GO') = (reason = 'NONE'))
);

CREATE TABLE futures_twin_placebo (
    id uuid PRIMARY KEY,
    day date NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 65536),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    set_sha256 text GENERATED ALWAYS AS (document->'set'->>'sha256') STORED NOT NULL,
    state text GENERATED ALWAYS AS (document->>'state') STORED NOT NULL CHECK (state IN ('DONE','FAILED')),
    error text GENERATED ALWAYS AS (document->>'error') STORED CHECK (char_length(error) <= 80),
    CONSTRAINT futures_twin_placebo_state CHECK (CASE state WHEN 'DONE' THEN error IS NULL ELSE error IS NOT NULL END),
    CONSTRAINT futures_twin_placebo_hash CHECK (sha256 = encode(sha256(convert_to(canonical, 'UTF8')), 'hex')
        AND document = CAST(canonical AS jsonb))
);
CREATE UNIQUE INDEX futures_twin_placebo_one_a_day ON futures_twin_placebo (day) WHERE state = 'DONE';
CREATE INDEX futures_twin_placebo_at ON futures_twin_placebo (created_at);

ALTER TABLE futures_twin_candidates
    ADD COLUMN veto varchar(9) CHECK (veto IN {vetoes}),
    ADD COLUMN veto_request_id uuid UNIQUE REFERENCES futures_twin_veto_requests(id),
    ADD CONSTRAINT futures_twin_candidate_veto CHECK ((veto IS NULL) = (veto_request_id IS NULL)
        AND (veto IS DISTINCT FROM 'VETO' OR (outcome = 'REFUSED' AND spent)));
"""

GUARDS_SQL = """
-- A request comes only from the execution identity, for the veto twin's own live segment.
CREATE FUNCTION asl_futures_twin_veto_request_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE t record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_execution' THEN RAISE EXCEPTION 'a veto request comes only from the twin step'; END IF;
    SELECT twin, state INTO t FROM futures_twins WHERE id = NEW.twin_id;
    IF NOT FOUND OR t.twin <> 'TREND_VETO' OR t.state NOT IN ('RUNNING','LATCHED') THEN
        RAISE EXCEPTION 'a veto request comes from the live veto twin'; END IF;
    RETURN NEW;
END $$;

-- An answer comes only from the agent identity, for its own running entry veto workflow bound to that request by its
-- ID and hash; the time it was recorded is the database's.
CREATE FUNCTION asl_futures_twin_veto_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; r record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a veto comes only from its agent'; END IF;
    NEW.recorded_at := clock_timestamp();
    SELECT template_id, purpose, role, state, parent_id, params INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL
            OR (w.template_id, w.purpose, w.role) <> ('ENTRY_VETO_V1', 'ENTRY_VETO', 'EVALUATOR') THEN
        RAISE EXCEPTION 'a veto needs its own running entry veto workflow'; END IF;
    SELECT id, sha256 INTO r FROM agent_read.futures_twin_veto_requests WHERE id = NEW.request_id;
    IF NOT FOUND OR w.params->'request'->>'id' IS DISTINCT FROM NEW.request_id::text
            OR w.params->'request'->>'sha256' IS DISTINCT FROM r.sha256 THEN
        RAISE EXCEPTION 'a veto answers the request its workflow was started for'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_artifacts WHERE workflow_id = NEW.workflow_id AND kind = 'ENTRY_VETO'
            AND sha256 = NEW.artifact_sha256) THEN
        RAISE EXCEPTION 'a veto is its workflow''s recorded artifact'; END IF;
    RETURN NEW;
END $$;

-- The veto artifact names the request its own running workflow was started for.
CREATE FUNCTION asl_entry_veto_artifact_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a veto comes only from its agent'; END IF;
    SELECT template_id, purpose, role, state, parent_id, params INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL
            OR (w.template_id, w.purpose, w.role) <> ('ENTRY_VETO_V1', 'ENTRY_VETO', 'EVALUATOR') THEN
        RAISE EXCEPTION 'a veto needs its own running entry veto workflow'; END IF;
    IF d->>'request_id' IS DISTINCT FROM w.params->'request'->>'id'
            OR d->>'request_sha256' IS DISTINCT FROM w.params->'request'->>'sha256' THEN
        RAISE EXCEPTION 'a veto names the request its workflow was started for'; END IF;
    RETURN NEW;
END $$;

-- A day's placebo comes only from the agent identity, names the stored twin set by its hash, and is written on or
-- after its own UTC day.
CREATE FUNCTION asl_futures_twin_placebo_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE d jsonb := NEW.document; stored jsonb;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a placebo is written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    stored := asl_m8_execution_definition(d->'set'->>'id', d->'set'->>'sha256');
    IF stored IS NULL OR stored->>'kind' <> 'FUTURES_TWINS' THEN
        RAISE EXCEPTION 'a placebo names its stored twin set'; END IF;
    IF d->>'schema' IS DISTINCT FROM 'TWIN_PLACEBO_V1' OR d->>'day' IS DISTINCT FROM NEW.day::text
            OR d->>'placebo_id' IS DISTINCT FROM NEW.id::text OR NEW.day > (NEW.created_at AT TIME ZONE 'UTC')::date THEN
        RAISE EXCEPTION 'a placebo describes its own day'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_twin_veto_requests_guard BEFORE INSERT ON futures_twin_veto_requests
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_veto_request_guard();
CREATE TRIGGER futures_twin_vetoes_guard BEFORE INSERT ON futures_twin_vetoes
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_veto_guard();
CREATE TRIGGER agent_artifacts_entry_veto BEFORE INSERT ON agent_artifacts
    FOR EACH ROW WHEN (NEW.kind = 'ENTRY_VETO') EXECUTE FUNCTION asl_entry_veto_artifact_guard();
CREATE TRIGGER futures_twin_placebo_guard BEFORE INSERT ON futures_twin_placebo
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_placebo_guard();
"""
APPEND_ONLY = ("futures_twin_veto_requests", "futures_twin_vetoes", "futures_twin_placebo")

# 0024's view of the twins' candidates, with the verdict the veto twin applied and the request it answered (a view
# gains columns only at its end); downgrade makes 0024's again.
CANDIDATES_VIEW = """
CREATE OR REPLACE VIEW agent_read.futures_twin_candidates WITH (security_barrier = true) AS
    SELECT c.id, t.twin, c.bar_open_ms, c.rule, c.side, c.gate, c.funding_filter, c.outcome, c.codes, c.at{columns}
    FROM futures_twin_candidates c JOIN futures_twins t ON t.id = c.twin_id;
"""
CANDIDATE_COLUMNS = ", c.veto, c.veto_request_id, c.signal_open_ms"
REQUESTS_VIEW = """
CREATE VIEW agent_read.futures_twin_veto_requests WITH (security_barrier = true) AS
    SELECT r.id, t.twin, r.bar_open_ms, r.signal_open_ms, r.side, r.asked_at, r.deadline_at, r.document, r.sha256,
        c.id AS candidate_id, c.veto AS applied, c.at AS applied_at, t.state AS twin_state
    FROM futures_twin_veto_requests r JOIN futures_twins t ON t.id = r.twin_id
    LEFT JOIN futures_twin_candidates c ON c.veto_request_id = r.id;
"""

GRANTS_SQL = """
GRANT SELECT, INSERT ON futures_twin_veto_requests TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE futures_twin_veto_requests_seq_seq TO asl_execution;
GRANT UPDATE (rule_day) ON futures_twins TO asl_execution;
GRANT SELECT ON futures_twin_vetoes TO asl_execution;
GRANT SELECT, INSERT ON futures_twin_vetoes, futures_twin_placebo TO asl_agent;
GRANT SELECT ON agent_read.futures_twin_veto_requests TO asl_agent;
GRANT SELECT ON futures_twin_veto_requests, futures_twin_vetoes, futures_twin_placebo TO asl_api;
"""


def _checks(twins, rules, events):
    op.execute("ALTER TABLE futures_twins DROP CONSTRAINT futures_twins_twin_check, "
               f"ADD CONSTRAINT futures_twins_twin_check CHECK (twin IN {_quoted(twins)})")
    op.execute("ALTER TABLE futures_twin_candidates DROP CONSTRAINT futures_twin_candidates_rule_check, "
               f"ADD CONSTRAINT futures_twin_candidates_rule_check CHECK (rule IN {_quoted(rules)})")
    op.execute("ALTER TABLE futures_twin_events DROP CONSTRAINT futures_twin_events_kind_check, "
               f"ADD CONSTRAINT futures_twin_events_kind_check CHECK (kind IN {_quoted(events)})")
    op.execute("ALTER TABLE futures_decision_scores DROP CONSTRAINT futures_decision_scores_twin_check, "
               f"ADD CONSTRAINT futures_decision_scores_twin_check CHECK (twin IN {_quoted(twins)})")


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    for row in twin_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    _checks((*TWINS_V1, *TWINS_ADDED), (*RULES_V1, "DAY_MOMENTUM"), (*EVENTS_V1, "DAY_SIGNAL"))
    op.execute(TABLES_SQL.replace("{reasons}", _quoted(REASONS)).replace("{vetoes}", _quoted(VETOES)))
    op.execute(CANDIDATES_VIEW.replace("{columns}", CANDIDATE_COLUMNS))
    op.execute(REQUESTS_VIEW)
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               "ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN "
               f"{_quoted((*PURPOSES, *PURPOSES_ADDED))})")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               "ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN "
               f"{_quoted((*ARTIFACT_KINDS, *ARTIFACTS_ADDED))})")
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH))
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_append_only()")
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
    op.execute("LOCK TABLE futures_twins, futures_twin_candidates, futures_twin_veto_requests, futures_twin_vetoes, "
               "futures_twin_placebo IN ACCESS EXCLUSIVE MODE")
    # A runtime profile that binds generation 12 by hash would bind definitions that no longer exist (as 0028's).
    generation12 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_twin_veto_requests) + (SELECT count(*) FROM futures_twin_vetoes) "
        "+ (SELECT count(*) FROM futures_twin_placebo) "
        f"+ (SELECT count(*) FROM futures_twins WHERE twin IN {_quoted(TWINS_ADDED)} OR rule_day IS NOT NULL) "
        "+ (SELECT count(*) FROM futures_twin_candidates WHERE rule = 'DAY_MOMENTUM' OR veto IS NOT NULL) "
        "+ (SELECT count(*) FROM futures_twin_events WHERE kind = 'DAY_SIGNAL') "
        f"+ (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} "
        f"OR purpose IN {_quoted(PURPOSES_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ARTIFACTS_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation12})"
    ).scalar_one()
    if held:
        raise RuntimeError("veto twin records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-12 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("DROP TRIGGER agent_artifacts_entry_veto ON agent_artifacts")
    op.execute("DROP VIEW agent_read.futures_twin_veto_requests")
    # A view loses a column only by being made again; 0024's grant is restored with it.
    op.execute("DROP VIEW agent_read.futures_twin_candidates")
    op.execute(CANDIDATES_VIEW.replace("{columns}", "").replace("CREATE OR REPLACE VIEW", "CREATE VIEW"))
    op.execute("GRANT SELECT ON agent_read.futures_twin_candidates TO asl_agent")
    op.execute("ALTER TABLE futures_twin_candidates DROP CONSTRAINT futures_twin_candidate_veto, "
               "DROP COLUMN veto_request_id, DROP COLUMN veto")
    op.execute(f"DROP TABLE {', '.join(TABLES)}")
    op.execute("DROP FUNCTION asl_futures_twin_veto_request_guard(), asl_futures_twin_veto_guard(), "
               "asl_entry_veto_artifact_guard(), asl_futures_twin_placebo_guard()")
    op.execute("ALTER TABLE futures_twins DROP COLUMN rule_day")
    _checks(TWINS_V1, RULES_V1, EVENTS_V1)
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               f"ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(PURPOSES)})")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen row, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in twin_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("twin set definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
