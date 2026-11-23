"""ExecPlan 0052: backtest the AI trader on history (generation 15 and the backtest's records).

Revision ID: 0032_ai_backtest
Revises: 0031_decision_replays

ExecPlan 0052 sections 4.3 to 4.5. Additive: nothing of the owner's account, its journal, its reservations, the
futures engine's tables, the trader, its decisions, the scores, the twins, the veto or the replay changes. Each guard
resolves names under a fixed search path.

- ``backtest_runs``: the one run ``BACKTEST_AI_V1:TWO_MONTHS``: its state (``RUNNING``, then ``FINISHED`` or
  ``STOPPED`` with a code, never back), each role's model pair (set once by its first answer, never changed) and the
  child process's summary at the end.
- ``backtest_steps``: what the simulated accounts asked, as the agent worker's child process printed it (the masked
  context and its hash, the reads, the account's state hash) and the probe's dates. Append-only. The sequence of
  trader and veto steps has no gap and no new step while its last one waits for an answer; a real-dates shadow
  pairs a trader step; a probe is one of 60.
- ``backtest_answers``: one per step: the model's answer from its own running backtest workflow bound to that step,
  with its ``BACKTEST_ANSWER`` artifact; or code's record that the model abstained (the workflow that ended so) or
  that the step was given up after three starts with none open. Append-only. Never a decision, an order or a fill.
- The workflow purpose ``BACKTEST`` and the artifact kind ``BACKTEST_ANSWER``, with a guard that the artifact names the
  step its own running backtest workflow was started for.
- Generation 15's agent definitions (frozen here, checked against the code).

Downgrade refuses once any backtest row, backtest workflow or backtest artifact exists, or a runtime profile binds
generation 15; otherwise it removes all of it.
"""

import hashlib
import json

from alembic import op

revision = "0032_ai_backtest"
down_revision = "0031_decision_replays"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# The checks as migration 0031 left them, and what this migration adds.
PURPOSES = ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH", "CANDIDATE_REVIEW", "PROMOTION",
            "DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW", "COIN_NOTE", "TRADE_REVIEW", "TRADE_COACH",
            "DECISION_REVIEW", "ENTRY_VETO", "REPLAY")
PURPOSES_ADDED = ("BACKTEST",)
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE", "FUTURES_DECISION", "TRADE_REVIEW", "TRADE_ADVICE",
                  "DECISION_REVIEW", "ENTRY_VETO", "DECISION_REPLAY")
ARTIFACTS_ADDED = ("BACKTEST_ANSWER",)
TEMPLATES = ("BACKTEST_TRADER_V1", "BACKTEST_REAL_DATES_V1", "BACKTEST_VETO_V1", "BACKTEST_MEMORY_PROBE_V1")
RUN_ID = "BACKTEST_AI_V1:TWO_MONTHS"
STARTS_PER_STEP = 3
PROBES = 60

# Generated from app.agents.definitions_v15 (python -m app.agents.definitions_v15); tests/test_backtest_lane_unit.py
# compares.
AGENT_SEED_LINES_V15 = r"""
["AGENT_STEP_SCHEMA_V10", "AGENT_STEP_SCHEMA", 10, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V10\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"ARTIFACT carries the memory_probe and a null abstain; ABSTAIN carries only abstain.\",\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"memory_probe\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"What you remember of the date in memory_probe: the price at 00:00 UTC as plain decimal digits, or null if you do not remember it; YES, NO or UNKNOWN for higher seven days later; how sure you are; one line of note.\",\"properties\":{\"confidence\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"higher_in_7_days\":{\"enum\":[\"YES\",\"NO\",\"UNKNOWN\"],\"type\":\"string\"},\"note\":{\"description\":\"At most 160 characters.\",\"type\":\"string\"},\"price_usdt\":{\"type\":[\"string\",\"null\"]}},\"required\":[\"price_usdt\",\"higher_in_7_days\",\"confidence\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"}},\"required\":[\"outcome\",\"memory_probe\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v10\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"The memory probe holds no tool: always null.\",\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v10\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v15 and ExecPlan 0052 section 4\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":10}", "84afc4cd185c813cb090f27ef21708174fe16647dd75a998737c4937a9fbed6e"]
["TOOL_CATALOG_V15", "TOOL_CATALOG", 15, "CODE_OWNED", "{\"absent_tools\":[],\"finish_records\":\"IN_GENERATION_15_ONE_BACKTEST_ANSWER_ARTIFACT_AND_ONE_BACKTEST_ANSWERS_ROW; NEVER_A_DECISION_OR_A_FILL\",\"id\":\"TOOL_CATALOG_V15\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"reads_at\":\"THE_STEP'S_STORED_READS; NEVER_A_LIVE_TABLE\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v15 and ExecPlan 0052 section 4\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: an action with only the choices it takes from the policy's sets, advice_use, expected_move and uncertainty_level, under the rules of the trader's prompt; an entry they do not allow is refused. The server records the context it was made in; the engine computes every price, quantity, stop level, fee and margin, and reads no forecast, note or score.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"},{\"arguments\":[],\"description\":\"FINISH only. EVALUATOR in an entry veto. One answer on the entry the TREND_VETO twin holds, named by the request's ID and hash: GO (the rule's entry), HALVE (the entry at half the policy's risk fraction) or VETO (no entry; the hour's cross is spent), a reason from VETO_REASONS_V1 (NONE exactly with GO), a one-line note and a confidence. Only that twin's step reads it; the twin checks, sizes and fills the entry itself, and no answer by the deadline is GO.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_entry_veto\"},{\"arguments\":[],\"description\":\"FINISH only. ANALYST in a backtest memory probe. What you remember of BTC's price at 00:00 UTC on the date given: the price or null, whether it was higher seven days later (YES, NO or UNKNOWN), how sure you are and a one-line note. Only the backtest's report reads it.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_memory_probe\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":15}", "ce15c963511242b62b866d9f3ee80d95e7555e484f7ef1b0447e56b93ad932e6"]
["ROLE_GRANTS_V15", "ROLE_GRANTS", 15, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[\"record_memory_probe\"],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[\"record_entry_veto\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V15\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v15 and ExecPlan 0052 section 4\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"BACKTEST_MEMORY_PROBE_V1\"],\"COORDINATOR\":[\"BACKTEST_TRADER_V1\",\"BACKTEST_REAL_DATES_V1\"],\"EVALUATOR\":[\"BACKTEST_VETO_V1\"],\"RESEARCHER\":[]},\"version\":15}", "9ce777dfc8e43258b93d7cd7a59cdf686e35d5074f45d23ef95090d77a706665"]
["TEMPLATES_V15", "TEMPLATES", 15, "CODE_OWNED", "{\"backtest\":{\"accounts\":{\"TRADER\":\"THE_TRADER'S_MODEL_EACH_FINISHED_HOUR_10000_USDT_FUTURES_POLICY_V1_FUTURES_COST_V1\",\"TREND_VETO\":\"TWIN_SET_V2'S_TREND_RULE_EACH_HELD_ENTRY_ANSWERED_BY_THE_VETO'S_MODEL\",\"code_only_in_the_report\":[\"HOLD\",\"TREND\",\"TREND_GATED\",\"MOMENTUM_1W\",\"PLACEBO_200\"]},\"answers_apply\":\"AT_THE_NEXT_MINUTE'S_OPEN; UNANSWERED_OR_ABSTAINED_IS_A_HOLD_OR_THE_VETO'S_SILENCE\",\"archive\":{\"files\":[{\"bytes\":2125,\"path\":\"exchangeinfo-btcusdt.json\",\"sha256\":\"a2e4a634d095b4d37ceb4f410bc59ccc26d9cabe596e1cb5cc6b45efd9a04ab7\"},{\"bytes\":896,\"path\":\"funding/BTCUSDT-fundingRate-2026-08.zip\",\"sha256\":\"7c108b3a02bd6dc7345ca7323e3a49664edcea0afdcf780ffb3b44762c45a964\"},{\"bytes\":98,\"path\":\"funding/BTCUSDT-fundingRate-2026-08.zip.CHECKSUM\",\"sha256\":\"d6627a40174fc8ba4a7943985995bf51df098efe53a2f190ec86a3bca846a96f\"},{\"bytes\":924,\"path\":\"funding/BTCUSDT-fundingRate-2026-09.zip\",\"sha256\":\"913cd31b8f924a06717a2fac17f3df6132c24ccded209eb3e4ae7d83e1b247f2\"},{\"bytes\":98,\"path\":\"funding/BTCUSDT-fundingRate-2026-09.zip.CHECKSUM\",\"sha256\":\"e2087ea6fbbff16a0458aeaf64c1edd5169abb9f2ef82560d2a0cdb5e35fdb4f\"},{\"bytes\":943,\"path\":\"funding/BTCUSDT-fundingRate-2026-10.zip\",\"sha256\":\"9c09b0bc6d8a57da06c34ec41add7dc9917dcb45dd83f7393ab0b3c2a2c34e5e\"},{\"bytes\":98,\"path\":\"funding/BTCUSDT-fundingRate-2026-10.zip.CHECKSUM\",\"sha256\":\"5843ff6b76e35a827db6aeadf3449ef93935d03116293423744e1d0bfa50e3f0\"},{\"bytes\":1817920,\"path\":\"klines/BTCUSDT-1m-2026-08.zip\",\"sha256\":\"adfd0846ea580681aeb18a6bdf06660dcfcc1a7b6819ea2eecfc3c53240ec67a\"},{\"bytes\":89,\"path\":\"klines/BTCUSDT-1m-2026-08.zip.CHECKSUM\",\"sha256\":\"285e684f9ecfbdab2d3f6bc5ef3b968459fb6f47fa017ad3b6feda1a14cdb91e\"},{\"bytes\":1796984,\"path\":\"klines/BTCUSDT-1m-2026-09.zip\",\"sha256\":\"e1a821b5bf6b48d57da01c3e390b8a467a698155def5c18c2c63c0eb044a3247\"},{\"bytes\":89,\"path\":\"klines/BTCUSDT-1m-2026-09.zip.CHECKSUM\",\"sha256\":\"43d42342358eeacb311d77a14bc9e1b2ee612af1ea5a85a064bf750540cfac35\"},{\"bytes\":1783009,\"path\":\"klines/BTCUSDT-1m-2026-10.zip\",\"sha256\":\"580bbf821130c6516f0b15819292beae79fd3d08498a0965fe8529308babf16b\"},{\"bytes\":89,\"path\":\"klines/BTCUSDT-1m-2026-10.zip.CHECKSUM\",\"sha256\":\"6f4ba59e7673d55c7d12ed850a6c59f3dd3b81f8e5334c7a865e8797bf3ad833\"},{\"bytes\":1011901,\"path\":\"mark/BTCUSDT-1m-2026-08.zip\",\"sha256\":\"3bd0556d903ce14f833ed58c78fd8d3309bc1a3804bb401c9fa2dd9d902f2c37\"},{\"bytes\":89,\"path\":\"mark/BTCUSDT-1m-2026-08.zip.CHECKSUM\",\"sha256\":\"7574bc9f05d8233d2ad92a9f7726e0a0977a62c08454d7416d4e4f7f40885e3f\"},{\"bytes\":1003436,\"path\":\"mark/BTCUSDT-1m-2026-09.zip\",\"sha256\":\"68dfd75f32b99bd8019e914395d2a7d60d5c1a74a700fde9991bf19b0c39322e\"},{\"bytes\":89,\"path\":\"mark/BTCUSDT-1m-2026-09.zip.CHECKSUM\",\"sha256\":\"46997b291e2ee8ce9c21d1fd1fa451c47350d8b66d1e3f6929d9289bcaea3d3d\"},{\"bytes\":956649,\"path\":\"mark/BTCUSDT-1m-2026-10.zip\",\"sha256\":\"77cfb0dfc8681aa0084abcbceb94d764955fbf4fdb85d18b28289302f6fce783\"},{\"bytes\":89,\"path\":\"mark/BTCUSDT-1m-2026-10.zip.CHECKSUM\",\"sha256\":\"31776e9106a6a396e27d244cd44aeff379c044b3127cd5e1fa60be0fa7eec3d1\"}],\"id\":\"BACKTEST_ARCHIVE_V1\",\"source\":\"https://data.binance.vision/data/futures/um/monthly/ (klines, markPriceKlines, fundingRate; BTCUSDT)\"},\"c1\":{\"days\":60,\"draw\":\"THE_SMALLEST_SHA256_OF_'BACKTEST_AI_V1|C1|'_PLUS_DATE\",\"first\":\"2025-11-01\",\"last\":\"2026-10-24\",\"remembers\":{\"direction_wilson_95_lower_above\":\"0.5\",\"median_price_error_below\":\"0.03\"}},\"c2\":{\"asked\":\"RIGHT_AFTER_ITS_MASKED_STEP\",\"draw\":\"THE_SMALLEST_SHA256_OF_'BACKTEST_AI_V1|C2|'_PLUS_THE_HOUR'S_CONTEXT_INSTANT_MS\",\"hours\":250,\"leaks\":\"THE_95%_LOWER_END_OF_REAL_MINUS_MASKED_ABOVE_0\"},\"id\":\"BACKTEST_AI_V1\",\"mask\":{\"factor\":\"2.907\",\"factor_rule\":\"SHA256_OF_'BACKTEST_MASK_V1|F'_MAPPED_INTO_[2.5,3.5]\",\"id\":\"BACKTEST_MASK_V1\",\"shift_days\":1820,\"shown\":\"NEVER_IN_A_CONTEXT_OR_A_READ\"},\"measures\":{\"M1\":\"MAKES_MONEY\",\"M2\":\"BEATS_HOLD\",\"M3\":\"BEATS_RULE\",\"M4\":\"PASS\",\"bootstrap\":\"STATIONARY_POLITIS_ROMANO_1994\",\"fail_confidence\":\"0.95\",\"mean_block_days\":3,\"mean_block_steps\":8,\"pass_confidence\":\"0.9875\",\"plan\":\"docs/plans/0052-backtest-the-ai-trader-on-history.md#48-the-measures-pre-registered\",\"resamples\":2000},\"reads\":{\"candles\":\"THE_COMPLETE_CANDLES_THE_LIVE_TOOL_HOLDS_BEFORE_THE_STEP_96_OF_1M_5M_AND_15M_25_OF_1H_STORED_WITH_IT\",\"headlines\":\"NONE_IN_THE_ARCHIVE\"},\"run\":\"BACKTEST_AI_V1:TWO_MONTHS\",\"window\":{\"end\":\"2026-11-01T00:00:00Z\",\"id\":\"TWO_MONTHS\",\"start\":\"2026-09-01T00:00:00Z\",\"warmup_days\":31}},\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V15\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\",\"ENTRY_VETO_WITH_THE_REVIEWS\",\"REPLAY_AND_BACKTEST_LAST\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v15 and ExecPlan 0052 section 4\",\"status\":\"CODE_OWNED\",\"templates\":{\"BACKTEST_MEMORY_PROBE_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V10\",\"applied\":\"NEVER\",\"artifact\":\"BACKTEST_ANSWER\",\"checked\":\"THE_ANSWER'S_FORMAT\",\"context\":\"A_REAL_DATE_AND_THE_INSTRUMENT_ONLY\",\"cutoff\":\"THE_STEP'S_OWN_INSTANT_MASKED_OR_REAL_AS_IT_IS_SHOWN; NO_LIVE_FEED\",\"follow_on\":\"NONE\",\"kind\":\"PROBE\",\"label\":\"BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"backtest\":\"THE_RUN_AND_THE_STEP'S_ID_AND_KIND\"},\"prompt\":\"BACKTEST_MEMORY_PROBE_PROMPT_V1\",\"purpose\":\"BACKTEST\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_BACKTEST'S_CHILD_PROCESS_AND_REPORT_ONLY\",\"role\":\"ANALYST\",\"run\":\"BACKTEST_AI_V1:TWO_MONTHS\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"calls_counted\":\"EACH_BACKTEST_WORKFLOW_STARTED_A_YIELDED_ONE_TOO\",\"calls_total\":2200,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"EACH_ROLE'S_PAIR_PINNED_BY_ITS_FIRST_ANSWER; THE_PROBE'S_ANALYST_ONLY_AT_THE_TRADER'S_PAIR, WHICH_ITS_FIRST_ANSWER_PINS_FOR_THE_TRADER_TOO\",\"none_while_a_replay_is_open\":true,\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"run_end\":\"CANCELS_ITS_OPEN_WORKFLOW_AND_STOPS_THE_CHILD_PROCESS\",\"turns_with_the_replay\":\"NEITHER_QUEUES_WHILE_THE_NEWEST_OF_THE_TWO_KINDS_IS_ITS_OWN_AND_THE_OTHER_WAITS\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_BACKTEST_CALL\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"starts_per_step\":3,\"when\":\"ONE_AT_A_TIME_THE_PROBES_FIRST_THEN_THE_OLDEST_STEP_WITHOUT_AN_ANSWER\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_BACKTEST_ANSWER_ARTIFACT_AND_ONE_BACKTEST_ANSWERS_ROW\"},\"BACKTEST_REAL_DATES_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V8\",\"applied\":\"NEVER\",\"artifact\":\"BACKTEST_ANSWER\",\"checked\":\"THE_TRADER'S_FINISH_RULES_BUT_THE_AGENTS'_CHECK_WHICH_GATES_ONLY_LIVE_ENTRIES\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"context\":\"THE_SAME_CONTEXT_UNMASKED_AT_ONE_OF_C2'S_HOURS\",\"cutoff\":\"THE_STEP'S_OWN_INSTANT_MASKED_OR_REAL_AS_IT_IS_SHOWN; NO_LIVE_FEED\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60},\"kind\":\"REAL_DATES\",\"label\":\"BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"backtest\":\"THE_RUN_AND_THE_STEP'S_ID_AND_KIND\"},\"prompt\":\"TRADER_PROMPT_M11_NO_FEEDBACK_V1\",\"purpose\":\"BACKTEST\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_BACKTEST'S_CHILD_PROCESS_AND_REPORT_ONLY\",\"role\":\"COORDINATOR\",\"run\":\"BACKTEST_AI_V1:TWO_MONTHS\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"calls_counted\":\"EACH_BACKTEST_WORKFLOW_STARTED_A_YIELDED_ONE_TOO\",\"calls_total\":2200,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"EACH_ROLE'S_PAIR_PINNED_BY_ITS_FIRST_ANSWER; THE_PROBE'S_ANALYST_ONLY_AT_THE_TRADER'S_PAIR, WHICH_ITS_FIRST_ANSWER_PINS_FOR_THE_TRADER_TOO\",\"none_while_a_replay_is_open\":true,\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"run_end\":\"CANCELS_ITS_OPEN_WORKFLOW_AND_STOPS_THE_CHILD_PROCESS\",\"turns_with_the_replay\":\"NEITHER_QUEUES_WHILE_THE_NEWEST_OF_THE_TWO_KINDS_IS_ITS_OWN_AND_THE_OTHER_WAITS\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_BACKTEST_CALL\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"starts_per_step\":3,\"when\":\"ONE_AT_A_TIME_THE_PROBES_FIRST_THEN_THE_OLDEST_STEP_WITHOUT_AN_ANSWER\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_BACKTEST_ANSWER_ARTIFACT_AND_ONE_BACKTEST_ANSWERS_ROW\"},\"BACKTEST_TRADER_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V8\",\"applied\":\"TO_THE_SIMULATED_TRADER_ACCOUNT_AT_THE_NEXT_MINUTE'S_OPEN\",\"artifact\":\"BACKTEST_ANSWER\",\"checked\":\"THE_TRADER'S_FINISH_RULES_BUT_THE_AGENTS'_CHECK_WHICH_GATES_ONLY_LIVE_ENTRIES\",\"commit\":{\"entry\":{\"confidence\":[\"MEDIUM\",\"HIGH\"],\"max_hold_hours\":[\"4\",\"12\",\"24\"],\"stop_multiples\":[\"2.0\",\"3.0\"],\"with\":\"THE_FORECAST'S_DIRECTION\"},\"forecast\":\"UP_OR_DOWN_AT_EVERY_DECISION; NO_VIEW_ONLY_WITH_ABSTAIN\",\"not_forced\":\"A_FLAT_HOLD_AT_MEDIUM_OR_HIGH_IS_ACCEPTED\",\"refused\":{\"ENTRY_AGAINST_FORECAST\":\"ENTER_LONG_WITHOUT_UP_OR_ENTER_SHORT_WITHOUT_DOWN\",\"ENTRY_CONFIDENCE_LOW\":\"AN_ENTRY_AT_LOW\",\"ENTRY_TOO_SHORT\":\"AN_ENTRY'S_STOP_UNDER_2_ATR_OR_TIME_EXIT_UNDER_4_HOURS\",\"FORECAST_REQUIRED\":\"NO_VIEW_WITHOUT_ABSTAIN_OR_A_VIEW_WITH_ABSTAIN\"}},\"context\":\"THE_TRADER'S_CONTEXT_FROM_THE_SIMULATED_ACCOUNT_MASKED_WITHOUT_SCORES_ADVICE_AND_EACH_TRADE'S_REVIEW\",\"cutoff\":\"THE_STEP'S_OWN_INSTANT_MASKED_OR_REAL_AS_IT_IS_SHOWN; NO_LIVE_FEED\",\"follow_on\":\"NONE\",\"forecast\":{\"choices\":[\"UP\",\"DOWN\",\"NO_VIEW\"],\"field\":\"expected_move\",\"horizon_minutes\":60},\"kind\":\"TRADER\",\"label\":\"BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"backtest\":\"THE_RUN_AND_THE_STEP'S_ID_AND_KIND\"},\"prompt\":\"TRADER_PROMPT_M11_NO_FEEDBACK_V1\",\"purpose\":\"BACKTEST\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_BACKTEST'S_CHILD_PROCESS_AND_REPORT_ONLY\",\"role\":\"COORDINATOR\",\"run\":\"BACKTEST_AI_V1:TWO_MONTHS\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"calls_counted\":\"EACH_BACKTEST_WORKFLOW_STARTED_A_YIELDED_ONE_TOO\",\"calls_total\":2200,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"EACH_ROLE'S_PAIR_PINNED_BY_ITS_FIRST_ANSWER; THE_PROBE'S_ANALYST_ONLY_AT_THE_TRADER'S_PAIR, WHICH_ITS_FIRST_ANSWER_PINS_FOR_THE_TRADER_TOO\",\"none_while_a_replay_is_open\":true,\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"run_end\":\"CANCELS_ITS_OPEN_WORKFLOW_AND_STOPS_THE_CHILD_PROCESS\",\"turns_with_the_replay\":\"NEITHER_QUEUES_WHILE_THE_NEWEST_OF_THE_TWO_KINDS_IS_ITS_OWN_AND_THE_OTHER_WAITS\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_BACKTEST_CALL\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"starts_per_step\":3,\"when\":\"ONE_AT_A_TIME_THE_PROBES_FIRST_THEN_THE_OLDEST_STEP_WITHOUT_AN_ANSWER\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_BACKTEST_ANSWER_ARTIFACT_AND_ONE_BACKTEST_ANSWERS_ROW\"},\"BACKTEST_VETO_V1\":{\"answer_format\":\"AGENT_STEP_SCHEMA_V9\",\"applied\":\"TO_THE_SIMULATED_TREND_VETO_TWIN_AT_THE_NEXT_MINUTE'S_OPEN\",\"artifact\":\"BACKTEST_ANSWER\",\"checked\":\"THE_REQUEST'S_ID_AND_SHA256_AND_THE_VERDICT'S_REASON\",\"context\":\"THE_VETO'S_CONTEXT_OF_THE_SIMULATED_TREND_VETO_TWIN'S_HELD_ENTRY_MASKED\",\"cutoff\":\"THE_STEP'S_OWN_INSTANT_MASKED_OR_REAL_AS_IT_IS_SHOWN; NO_LIVE_FEED\",\"follow_on\":\"NONE\",\"kind\":\"VETO\",\"label\":\"BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL\",\"parameters\":{\"backtest\":\"THE_RUN_AND_THE_STEP'S_ID_AND_KIND\"},\"prompt\":\"VETO_PROMPT_M11_V1\",\"purpose\":\"BACKTEST\",\"quiet_window\":\"KEPT\",\"reads_it\":\"THE_BACKTEST'S_CHILD_PROCESS_AND_REPORT_ONLY\",\"role\":\"EVALUATOR\",\"run\":\"BACKTEST_AI_V1:TWO_MONTHS\",\"schedule\":{\"gate\":{\"after_a_decision_ended_seconds\":30,\"after_the_trader_reviewers_coach_and_veto\":true,\"calls_counted\":\"EACH_BACKTEST_WORKFLOW_STARTED_A_YIELDED_ONE_TOO\",\"calls_total\":2200,\"end_before_the_next_15m_bar_seconds\":60,\"model_and_effort\":\"EACH_ROLE'S_PAIR_PINNED_BY_ITS_FIRST_ANSWER; THE_PROBE'S_ANALYST_ONLY_AT_THE_TRADER'S_PAIR, WHICH_ITS_FIRST_ANSWER_PINS_FOR_THE_TRADER_TOO\",\"none_while_a_replay_is_open\":true,\"not_in_the_quiet_window\":true,\"one_open_at_once\":true,\"per_15m_bar\":2,\"provider\":\"CODEX_CLI\",\"run_end\":\"CANCELS_ITS_OPEN_WORKFLOW_AND_STOPS_THE_CHILD_PROCESS\",\"turns_with_the_replay\":\"NEITHER_QUEUES_WHILE_THE_NEWEST_OF_THE_TWO_KINDS_IS_ITS_OWN_AND_THE_OTHER_WAITS\",\"usage\":{\"every_window_below_percent\":50,\"no_reading\":\"NO_BACKTEST_CALL\",\"none_reached\":true,\"reading_max_age_seconds\":1200},\"yields_to\":\"A_QUEUED_OR_RUNNING_DECISION_OR_A_WAITING_VETO_CANCELED_AT_THE_RUNNER\"},\"per_utc_day\":192,\"starts_per_step\":3,\"when\":\"ONE_AT_A_TIME_THE_PROBES_FIRST_THEN_THE_OLDEST_STEP_WITHOUT_AN_ANSWER\"},\"started_by\":[\"SYSTEM\"],\"writes\":\"ONE_BACKTEST_ANSWER_ARTIFACT_AND_ONE_BACKTEST_ANSWERS_ROW\"}},\"version\":15}", "2444646ef1a63c8c88ac526ca777423021e94d1023c69ef972202d2fa9c2b70d"]
["BUDGETS_V15", "BUDGETS", 15, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"BACKTEST\":192},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V15\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"except\":[],\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":36864,\"source\":\"ExecPlan 0052 section 4.4\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"BACKTEST_MEMORY_PROBE_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":110,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":115},\"BACKTEST_REAL_DATES_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"BACKTEST_TRADER_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180},\"BACKTEST_VETO_V1\":{\"max_model_steps\":2,\"max_tool_calls\":0,\"step_deadline_seconds\":110,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":115}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":15}", "6de4782e4a60d6a582c012339baeb07d99f2b4193c76462cd9b02dae10c56e35"]
["BACKTEST_MEMORY_PROBE_PROMPT_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"BACKTEST_MEMORY_PROBE_PROMPT_V1\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"b3a127337bde229e7e3b245ff22373485d032693698924e3fdce03fd44e84cf0\",\"source\":\"services/agent-runner/prompts/m11/backtest-memory-probe.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "3680b90216106f03ac1191ffc63aa48a2365926b258a9afac3491c94d1105786"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def agent_rows():
    rows = []
    for line in AGENT_SEED_LINES_V15.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in AGENT_KINDS:
            raise RuntimeError("frozen generation-15 agent definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


TABLES_SQL = """
CREATE TABLE backtest_runs (
    id varchar(48) PRIMARY KEY CHECK (id = '{run}'),
    state varchar(8) NOT NULL DEFAULT 'RUNNING' CHECK (state IN ('RUNNING','FINISHED','STOPPED')),
    code varchar(32) CHECK (code IN ('ARCHIVE_MISMATCH','STATE_MISMATCH','PROTOCOL','CALLS_TOTAL_REACHED')),
    detail varchar(300),
    pairs jsonb NOT NULL DEFAULT '{}'::jsonb CHECK (jsonb_typeof(pairs) = 'object'),
    summary jsonb,
    label text NOT NULL DEFAULT 'BACKTEST; MODELED; NEVER_THE_OWNER''S_ACCOUNT'
        CHECK (label = 'BACKTEST; MODELED; NEVER_THE_OWNER''S_ACCOUNT'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    ended_at timestamptz,
    CONSTRAINT backtest_run_end CHECK ((state = 'RUNNING') = (ended_at IS NULL)),
    CONSTRAINT backtest_run_code CHECK ((state = 'STOPPED') = (code IS NOT NULL))
);

CREATE TABLE backtest_steps (
    id uuid PRIMARY KEY,
    n bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    run_id varchar(48) NOT NULL REFERENCES backtest_runs(id),
    kind varchar(10) NOT NULL CHECK (kind IN ('TRADER','VETO','REAL_DATES','PROBE')),
    seq integer NOT NULL CHECK (seq >= 0),
    at timestamptz NOT NULL,
    context jsonb NOT NULL CHECK (jsonb_typeof(context) = 'object'),
    context_sha256 varchar(64) NOT NULL CHECK (context_sha256 ~ '^[0-9a-f]{64}$'),
    reads jsonb CHECK (reads IS NULL OR jsonb_typeof(reads) = 'object'),
    state_sha256 varchar(64) CHECK (state_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (run_id, kind, seq),
    CONSTRAINT backtest_step_reads CHECK ((reads IS NOT NULL) = (kind IN ('TRADER','REAL_DATES'))),
    CONSTRAINT backtest_step_state CHECK ((state_sha256 IS NOT NULL) = (kind IN ('TRADER','VETO'))),
    CONSTRAINT backtest_step_probe CHECK (kind <> 'PROBE' OR seq < {probes})
);

CREATE TABLE backtest_answers (
    step_id uuid PRIMARY KEY REFERENCES backtest_steps(id),
    run_id varchar(48) NOT NULL REFERENCES backtest_runs(id),
    outcome varchar(10) NOT NULL CHECK (outcome IN ('ANSWERED','ABSTAINED','UNANSWERED')),
    answer jsonb CHECK (answer IS NULL OR jsonb_typeof(answer) = 'object'),
    workflow_id uuid UNIQUE REFERENCES agent_workflows(id),
    artifact_sha256 varchar(64) CHECK (artifact_sha256 ~ '^[0-9a-f]{64}$'),
    model varchar(128),
    effort varchar(32),
    label text NOT NULL DEFAULT 'BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL'
        CHECK (label = 'BACKTEST; MODEL_AUTHORED; MASKED_HISTORY; NEVER_A_DECISION_OR_A_FILL'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT backtest_answer_body CHECK (
        (outcome = 'ANSWERED') = (answer IS NOT NULL) AND (outcome = 'ANSWERED') = (artifact_sha256 IS NOT NULL)),
    CONSTRAINT backtest_answer_workflow CHECK ((outcome = 'UNANSWERED') = (workflow_id IS NULL))
);
"""

GUARDS_SQL = """
-- The run: one, created RUNNING; it ends once (FINISHED, with its summary and every step answered, or STOPPED with its
-- code), its summary and a role's model pair are each set once and never changed, and nothing else moves.
CREATE FUNCTION asl_backtest_run_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE role_name text;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'the backtest run is the agent worker''s'; END IF;
    IF TG_OP = 'INSERT' THEN
        IF NEW.state <> 'RUNNING' OR NEW.pairs <> '{}'::jsonb OR NEW.summary IS NOT NULL THEN
            RAISE EXCEPTION 'a backtest run starts running with nothing recorded'; END IF;
        NEW.created_at := clock_timestamp();
        RETURN NEW;
    END IF;
    IF NEW.id <> OLD.id OR NEW.created_at <> OLD.created_at OR NEW.label <> OLD.label THEN
        RAISE EXCEPTION 'a backtest run keeps its identity'; END IF;
    IF OLD.state <> 'RUNNING' AND (NEW.state, NEW.code, NEW.detail, NEW.pairs, NEW.summary, NEW.ended_at)
            IS DISTINCT FROM (OLD.state, OLD.code, OLD.detail, OLD.pairs, OLD.summary, OLD.ended_at) THEN
        RAISE EXCEPTION 'an ended backtest run does not change'; END IF;
    FOR role_name IN SELECT jsonb_object_keys(OLD.pairs) LOOP
        IF NEW.pairs -> role_name IS DISTINCT FROM OLD.pairs -> role_name THEN
            RAISE EXCEPTION 'a role''s model pair is set once'; END IF;
    END LOOP;
    IF OLD.summary IS NOT NULL AND NEW.summary IS DISTINCT FROM OLD.summary THEN
        RAISE EXCEPTION 'a backtest run''s summary is set once'; END IF;
    IF OLD.state = 'RUNNING' AND NEW.state = 'FINISHED' AND (NEW.summary IS NULL OR EXISTS (
            SELECT 1 FROM backtest_steps s WHERE s.run_id = NEW.id
            AND NOT EXISTS (SELECT 1 FROM backtest_answers a WHERE a.step_id = s.id))) THEN
        RAISE EXCEPTION 'a backtest run finishes with its summary and every step answered'; END IF;
    IF OLD.state = 'RUNNING' AND NEW.state <> 'RUNNING' THEN NEW.ended_at := clock_timestamp(); END IF;
    RETURN NEW;
END $$;

-- A step: the run is running; the trader and veto steps follow one another with no gap and none while the last waits
-- for its answer; a real-dates shadow pairs a trader step; the time it was written is the database's.
CREATE FUNCTION asl_backtest_step_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE last record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a backtest step is the agent worker''s'; END IF;
    PERFORM 1 FROM backtest_runs WHERE id = NEW.run_id AND state = 'RUNNING' FOR UPDATE;
    IF NOT FOUND THEN RAISE EXCEPTION 'a backtest step needs its run running'; END IF;
    NEW.created_at := clock_timestamp();
    IF NEW.kind IN ('TRADER','VETO') THEN
        SELECT s.seq, EXISTS (SELECT 1 FROM backtest_answers a WHERE a.step_id = s.id) AS answered INTO last
            FROM backtest_steps s WHERE s.run_id = NEW.run_id AND s.kind IN ('TRADER','VETO')
            ORDER BY s.seq DESC LIMIT 1;
        IF NOT FOUND THEN
            IF NEW.seq <> 0 THEN RAISE EXCEPTION 'the first backtest step is step 0'; END IF;
        ELSIF NEW.seq <> last.seq + 1 OR NOT last.answered THEN
            RAISE EXCEPTION 'a backtest step follows the last one once it has its answer'; END IF;
    ELSIF NEW.kind = 'REAL_DATES' THEN
        IF NOT EXISTS (SELECT 1 FROM backtest_steps WHERE run_id = NEW.run_id AND kind = 'TRADER'
                AND seq = NEW.seq) THEN
            RAISE EXCEPTION 'a real-dates shadow pairs a trader step'; END IF;
    END IF;
    RETURN NEW;
END $$;

-- An answer: the model's comes only from its own running backtest workflow of the step's template bound to that step,
-- as its workflow's recorded artifact with the same answer; an abstention names the workflow that ended so; a step is
-- given up only after its starts (a start canceled to make way for a decision not counted) with none open. The time it
-- was recorded is the database's.
CREATE FUNCTION asl_backtest_answer_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE s record; w record; template text;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a backtest answer is the agent worker''s'; END IF;
    NEW.recorded_at := clock_timestamp();
    SELECT st.run_id, st.kind INTO s FROM backtest_steps st WHERE st.id = NEW.step_id;
    IF NOT FOUND OR s.run_id <> NEW.run_id THEN RAISE EXCEPTION 'a backtest answer answers a step of its run'; END IF;
    PERFORM 1 FROM backtest_runs WHERE id = NEW.run_id AND state = 'RUNNING';
    IF NOT FOUND THEN RAISE EXCEPTION 'a backtest answer needs its run running'; END IF;
    template := CASE s.kind WHEN 'TRADER' THEN 'BACKTEST_TRADER_V1' WHEN 'REAL_DATES' THEN 'BACKTEST_REAL_DATES_V1'
        WHEN 'VETO' THEN 'BACKTEST_VETO_V1' WHEN 'PROBE' THEN 'BACKTEST_MEMORY_PROBE_V1' END;
    IF NEW.outcome = 'UNANSWERED' THEN
        IF EXISTS (SELECT 1 FROM agent_workflows WHERE template_id = template
                AND params->'backtest'->>'step_id' = NEW.step_id::text
                AND state IN ('QUEUED','RUNNING','WAITING_TOOL','WAITING_REVIEW'))
                OR (SELECT count(*) FROM agent_workflows WHERE template_id = template
                    AND params->'backtest'->>'step_id' = NEW.step_id::text
                    AND (started_at IS NOT NULL OR state = 'FAILED')
                    AND NOT (state = 'CANCELED' AND COALESCE(terminal_reason, '') = 'YIELDED_TO_DECISION'))
                    < {starts} THEN
            RAISE EXCEPTION 'a backtest step is given up only after its starts, with none open'; END IF;
        RETURN NEW;
    END IF;
    SELECT template_id, purpose, state, parent_id, created_by, params INTO w FROM agent_workflows
        WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.purpose <> 'BACKTEST' OR w.parent_id IS NOT NULL OR w.created_by <> 'SYSTEM'
            OR w.template_id IS DISTINCT FROM template
            OR w.params->'backtest'->>'step_id' IS DISTINCT FROM NEW.step_id::text
            OR w.params->'backtest'->>'run' IS DISTINCT FROM NEW.run_id THEN
        RAISE EXCEPTION 'a backtest answer comes from the workflow started for its step'; END IF;
    IF NEW.outcome = 'ABSTAINED' THEN
        IF w.state <> 'ABSTAINED' THEN RAISE EXCEPTION 'an abstention names the workflow that abstained'; END IF;
        RETURN NEW;
    END IF;
    IF w.state <> 'RUNNING' THEN RAISE EXCEPTION 'a backtest answer comes from its running workflow'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_artifacts WHERE workflow_id = NEW.workflow_id AND kind = 'BACKTEST_ANSWER'
            AND sha256 = NEW.artifact_sha256 AND document -> 'answer' = NEW.answer) THEN
        RAISE EXCEPTION 'a backtest answer is its workflow''s recorded artifact'; END IF;
    RETURN NEW;
END $$;

-- The backtest artifact names the step its own running backtest workflow was started for.
CREATE FUNCTION asl_backtest_artifact_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record; d jsonb := NEW.document;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a backtest answer comes only from its agent'; END IF;
    SELECT template_id, purpose, state, parent_id, params INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.state <> 'RUNNING' OR w.parent_id IS NOT NULL OR w.purpose <> 'BACKTEST'
            OR w.template_id NOT IN {templates} THEN
        RAISE EXCEPTION 'a backtest answer needs its own running backtest workflow'; END IF;
    IF d->>'step_id' IS DISTINCT FROM w.params->'backtest'->>'step_id'
            OR d->>'run' IS DISTINCT FROM w.params->'backtest'->>'run' THEN
        RAISE EXCEPTION 'a backtest answer names the step its workflow was started for'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER backtest_runs_guard BEFORE INSERT OR UPDATE ON backtest_runs
    FOR EACH ROW EXECUTE FUNCTION asl_backtest_run_guard();
CREATE TRIGGER backtest_runs_no_delete BEFORE DELETE ON backtest_runs
    FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only();
CREATE TRIGGER backtest_steps_guard BEFORE INSERT ON backtest_steps
    FOR EACH ROW EXECUTE FUNCTION asl_backtest_step_guard();
CREATE TRIGGER backtest_steps_append_only BEFORE UPDATE OR DELETE ON backtest_steps
    FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only();
CREATE TRIGGER backtest_answers_guard BEFORE INSERT ON backtest_answers
    FOR EACH ROW EXECUTE FUNCTION asl_backtest_answer_guard();
CREATE TRIGGER backtest_answers_append_only BEFORE UPDATE OR DELETE ON backtest_answers
    FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only();
CREATE TRIGGER agent_artifacts_backtest_answer BEFORE INSERT ON agent_artifacts
    FOR EACH ROW WHEN (NEW.kind = 'BACKTEST_ANSWER') EXECUTE FUNCTION asl_backtest_artifact_guard();
"""

GRANTS_SQL = """
GRANT SELECT, INSERT ON backtest_runs, backtest_steps, backtest_answers TO asl_agent;
GRANT UPDATE (state, code, detail, pairs, summary) ON backtest_runs TO asl_agent;
GRANT SELECT ON backtest_runs, backtest_steps, backtest_answers TO asl_api;
"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute(TABLES_SQL.replace("{run}", RUN_ID).replace("{probes}", str(PROBES)))
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               "ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN "
               f"{_quoted((*PURPOSES, *PURPOSES_ADDED))})")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               "ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN "
               f"{_quoted((*ARTIFACT_KINDS, *ARTIFACTS_ADDED))})")
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH).replace("{templates}", _quoted(TEMPLATES))
               .replace("{starts}", str(STARTS_PER_STEP)))
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
    op.execute("LOCK TABLE backtest_runs, backtest_steps, backtest_answers IN ACCESS EXCLUSIVE MODE")
    # A runtime profile that binds generation 15 by hash would bind definitions that no longer exist (as 0031's).
    generation15 = [row["id"] for row in agent_rows()]
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM backtest_runs) + (SELECT count(*) FROM backtest_steps) "
        "+ (SELECT count(*) FROM backtest_answers) "
        f"+ (SELECT count(*) FROM agent_workflows WHERE template_id IN {_quoted(TEMPLATES)} "
        f"OR purpose IN {_quoted(PURPOSES_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_artifacts WHERE kind IN {_quoted(ARTIFACTS_ADDED)}) "
        f"+ (SELECT count(*) FROM agent_runtime_profiles WHERE profile -> 'definitions' ?| ARRAY{generation15})"
    ).scalar_one()
    if held:
        raise RuntimeError("AI backtest records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("generation-15 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("DROP TRIGGER agent_artifacts_backtest_answer ON agent_artifacts")
    op.execute("DROP TABLE backtest_answers, backtest_steps, backtest_runs")
    op.execute("DROP FUNCTION asl_backtest_run_guard(), asl_backtest_step_guard(), asl_backtest_answer_guard(), "
               "asl_backtest_artifact_guard()")
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflows_purpose_check, "
               f"ADD CONSTRAINT agent_workflows_purpose_check CHECK (purpose IN {_quoted(PURPOSES)})")
