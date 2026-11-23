"""M11 update 2, part B: the paper futures account and its trader.

Revision ID: 0020_futures
Revises: 0019_perp_market

ExecPlan 0039 section 5.3.1. Additive except for the journal, whose source and book-account checks widen; nothing of
the spot broker, its runs or its valuations changes. Each guard resolves names under a fixed search path.

- ``FUTURES_POLICY_V1`` and ``FUTURES_COST_V1`` in ``execution_definitions`` (frozen here, checked against the code).
- ``futures_runs`` and ``futures_run_events``: one run at a time, its causes, its own high-water NAV; the owner's
  requests in ``futures_owner_requests``, written by the API and answered once by the engine.
- ``futures_decisions`` (the trader's, written by the agent identity in the transaction that ends its workflow) and
  ``futures_decision_answers`` (the engine's, one each).
- ``futures_positions``, ``futures_fills`` and ``futures_funding``: at most one open position; the stop only tightens;
  a closed position, a fill and a posted funding never change.
- ``futures_ledger_events``: margin reserved and released (no postings), fees, realized P&L, funding and
  liquidation, each posting one journal transaction through the new source column ``futures_event_id``, which only
  the execution identity writes; the book accounts gain ``TRADING_PNL`` and ``FUNDING``.
- ``futures_valuations``, ``futures_daily_references`` and ``futures_latches``.
- ``agent_read`` views of the perpetual's market data, the futures account and the futures policies for the trader.
- Generation 7's agent definitions (the trader ``FUTURES_DECISION_V1``, frozen here, checked against the code), the
  artifact kind ``FUTURES_DECISION``, and the verification guard accepting a check bound to a futures policy.

Downgrade refuses once any futures record exists; otherwise it drops the tables and restores the journal's checks,
0015's artifact kinds and 0010's verification guard.
"""

import hashlib
import json

from alembic import op

revision = "0020_futures"
down_revision = "0019_perp_market"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET")
FUTURES_KINDS = ("FUTURES_POLICY", "FUTURES_COST")
AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# The artifact kinds as migration 0015 left them, and the one this migration adds.
ARTIFACT_KINDS = ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL",
                  "PORTFOLIO_DECISION", "COIN_NOTE")
ARTIFACT_ADDED = ("FUTURES_DECISION",)
TABLES = ("futures_valuations", "futures_daily_references", "futures_latches", "futures_ledger_events",
          "futures_funding", "futures_fills", "futures_decision_answers", "futures_positions", "futures_decisions",
          "futures_run_events", "futures_owner_requests", "futures_runs")
VIEWS = ("futures_quotes", "futures_marks", "futures_bars", "futures_funding_rates", "futures_instrument",
         "futures_feed", "futures_account", "futures_runs", "futures_positions", "futures_fills",
         "futures_funding", "futures_answers", "futures_valuations", "futures_policies")
OLD_ACCOUNTS = "('OWNER_CASH','OWNER_ASSET','VIRTUAL_CAPITAL','CLEARING','EXPENSE')"
NEW_ACCOUNTS = "('OWNER_CASH','OWNER_ASSET','VIRTUAL_CAPITAL','CLEARING','EXPENSE','TRADING_PNL','FUNDING')"
ASSETS = "('BTC','SOL','ZEC','NEAR','XRP')"

# The frozen definitions: ``python -m app.futures.definitions`` prints them; tests/test_m11_futures_db.py checks them.
FUTURES_SEED_LINES = r"""
["FUTURES_POLICY_V1", "FUTURES_POLICY", 1, "PROPOSED", "{\"actions\":[\"ENTER_LONG\",\"ENTER_SHORT\",\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"atr\":{\"candles\":\"COMPLETE_15M_CANDLES_BUILT_FROM_FINAL_1M_CANDLES_THE_NEWEST_CONTIGUOUS_RUN\",\"interval_ms\":900000,\"method\":\"WILDER\",\"period\":14,\"window_candles\":96},\"cooldown_bars\":{\"after_other_exit\":1,\"after_stop\":2},\"cost\":\"FUTURES_COST_V1\",\"daily_loss_fraction\":\"0.02\",\"daily_reference\":{\"late_rule\":\"MAX_OF_LAST_VALID_NAV_PRIOR_24H_AND_FIRST_POST_MIDNIGHT_NAV\",\"timeliness_ms\":300000,\"timezone\":\"UTC\"},\"decision_max_age_seconds\":300,\"decision_schedule\":{\"after_fill\":true,\"bar_ms\":900000,\"max_open\":1,\"quiet_window\":null,\"sharp_move_atr\":\"1.5\",\"sharp_move_window_seconds\":300},\"decisions_per_utc_day\":120,\"drawdown_fraction\":\"0.08\",\"drawdown_measure\":\"THE_RUN'S_OWN_HIGH_WATER_NAV\",\"entries_per_utc_day\":24,\"funding_reserve\":{\"fraction_of_notional\":\"0.01\",\"kept\":\"THE_FREE_WALLET_AFTER_AN_ENTRY_COVERS_THE_EXIT_FEE_AND_THIS\",\"label\":\"THE_APP'S_OWN_BUFFER_NOT_A_PROVIDER_VALUE\"},\"id\":\"FUTURES_POLICY_V1\",\"instrument\":\"BTCUSDT_PERPETUAL_SIMULATED\",\"kind\":\"FUTURES_POLICY\",\"latch_effect\":\"NO_ENTRIES_EXITS_AND_PROTECTION_CONTINUE\",\"leverage_cap\":\"2\",\"leverage_choices\":[\"1\",\"2\"],\"liquidation_buffer\":\"3\",\"liquidation_rule\":\"THE_STOP_WITHIN_THE_FIRST_THIRD_OF_THE_WAY_TO_LIQUIDATION\",\"margin_mode\":\"ISOLATED\",\"max_hold_hours\":[1,4,12,24],\"no_agent\":\"NO_NEW_ENTRY_THE_POSITION_STAYS_PROTECTED_BY_CODE\",\"notional_cap\":\"LEVERAGE_X_EQUITY\",\"position_mode\":\"ONE_WAY\",\"positions\":1,\"reversal\":\"EXIT_THEN_THE_NEXT_DECISION\",\"risk_fraction\":\"0.0025\",\"risk_includes\":\"BOTH_TAKER_FEES_AND_THE_SLIPPAGE_SCENARIO\",\"source\":\"ExecPlan 0039 section 5.4, approved by the owner on 2026-10-23\",\"status\":\"PROPOSED\",\"stop_multiples\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\"],\"stop_rounding\":\"TO_THE_TICK_AWAY_FROM_THE_ENTRY\",\"take_profit_multiples\":[\"1\",\"1.5\",\"2\",\"3\"],\"take_profit_rounding\":\"TO_THE_TICK_TOWARD_THE_ENTRY\",\"tighten\":\"THE_SAME_MULTIPLES_FROM_THE_EXIT_SIDE_PRICE_ONLY_IF_TIGHTER\",\"valuation_seconds\":60,\"version\":1}", "b304ba5eb2e278fc6e8951aa1b260cdf8c057f3c7af9f0614388405f6aa44635"]
["FUTURES_COST_V1", "FUTURES_COST", 1, "PROPOSED", "{\"above_tier_1\":\"ENTRY_REFUSED\",\"bnb_discount\":false,\"book\":{\"depth_short\":\"ENTRY_REFUSED_EXIT_WAITS\",\"levels\":5,\"quote_max_age_ms\":2000,\"walk\":\"THE_FIVE_LEVELS_OF_THE_NEWEST_QUOTE\"},\"fee_rounding\":\"UP_TO_0.00000001\",\"fee_source\":{\"read_at\":\"2026-10-24T10:40:11Z\",\"row\":\"Regular User, USDT Maker / Taker 0.0200%/0.0500%\",\"url\":\"https://www.binance.com/en/fee/futureFee\"},\"fill_price_rounding\":\"TO_0.00000001_AGAINST_THE_ORDER\",\"funding\":{\"amount\":\"QUANTITY_X_THE_SETTLED_MARK_X_THE_SETTLED_RATE\",\"mark\":\"THE_SETTLED_RATE'S_MARK_ELSE_THE_MARK_STREAM_AT_IT_WITHIN_5_S\",\"open_at\":\"OPENED_BEFORE_AND_NOT_CLOSED_BEFORE_THE_FUNDING_TIME\",\"payment_rounding\":\"UP_TO_0.00000001\",\"rate_match_ms\":60000,\"receipt_rounding\":\"DOWN_TO_0.00000001\",\"sign\":\"A_POSITIVE_RATE_LONGS_PAY\",\"source\":\"https://www.binance.com/en/support/faq/introduction-to-binance-futures-funding-rates-360033525031\",\"times\":\"THE_MARK'S_ANNOUNCED_NEXT_FUNDING_TIMES_AND_THE_SETTLED_RATES'_TIMES\",\"unpayable\":\"WAITS_PENDING_UNTIL_THE_FREE_WALLET_COVERS_IT\",\"until_settled\":\"PENDING_NOTHING_GUESSED\"},\"id\":\"FUTURES_COST_V1\",\"kind\":\"FUTURES_COST\",\"liquidation\":{\"fixed_at\":\"ENTRY\",\"long\":\"(QUANTITY*ENTRY-MARGIN-AMOUNT)/(QUANTITY*(1-RATE))\",\"loss\":\"THE_WHOLE_MARGIN\",\"none_when\":\"THE_LONG'S_PRICE_IS_NOT_ABOVE_ZERO\",\"rounding\":\"TO_0.00000001_TOWARD_THE_ENTRY\",\"rule\":\"BINANCE_ISOLATED_MARGIN_ONE_WAY_MODE\",\"short\":\"(QUANTITY*ENTRY+MARGIN+AMOUNT)/(QUANTITY*(1+RATE))\",\"source\":{\"formula\":\"LP1=(WB-TMM1+UPNL1+cumB+cumL+cumS-Side1BOTH*Position1BOTH*EP1BOTH-Position1LONG*EP1LONG+Position1SHORT*EP1SHORT)/(Position1BOTH*MMRB+Position1LONG*MMRL+Position1SHORT*MMRS-Side1BOTH*Position1BOTH-Position1LONG+Position1SHORT)\",\"formula_image_sha256\":\"18d0f628aecc6ef289d81f68cd3fd516dc4a7b0f29850b26ac08608445360caa\",\"isolated\":\"WB is isolatedWalletBalance of the isolated position, TMM=0, UPNL=0\",\"read_at\":\"2026-10-24T10:41:13Z\",\"url\":\"https://www.binance.com/en/support/faq/detail/b3c689c1f50a44cabb3a84e663b81d93\"},\"trigger\":\"THE_MARK_PRICE_AT_OR_BEYOND_IT\",\"wallet_balance\":\"THE_POSITION'S_MARGIN_AT_ENTRY\"},\"maintenance_source\":{\"read_at\":\"2026-10-24T10:40:46Z\",\"row\":\"Tier1 | 0 - 300,000 | 150x | 0.40% | 0\",\"rules_last_update\":\"2025/08/19 08:36\",\"symbol\":\"BTCUSDT Perpetual\",\"url\":\"https://www.binance.com/en/futures/trading-parameters/perpetual/leverage-margin\"},\"maintenance_tiers\":[{\"amount\":\"0\",\"bracket_high\":\"300000\",\"bracket_low\":\"0\",\"max_leverage\":150,\"rate\":\"0.004\",\"tier\":1}],\"margin\":\"NOTIONAL_DIVIDED_BY_LEVERAGE_ROUNDED_UP_TO_0.00000001\",\"orders\":\"MARKET_ONLY\",\"pnl_rounding\":\"DOWN_TO_0.00000001\",\"promotions\":\"NOT_APPLIED\",\"quantity_rounding\":\"DOWN_TO_THE_STEP\",\"slippage\":{\"adverse_bps\":\"1\",\"applied\":\"TO_THE_WALKED_AVERAGE_PRICE\",\"label\":\"SCENARIO_NOT_OBSERVED\"},\"source\":\"ExecPlan 0039 section 5.3; Binance's pages read on 2026-10-24 (docs/INTEGRATION_EVIDENCE.md)\",\"status\":\"PROPOSED\",\"taker_fee_rate\":\"0.0005\",\"version\":1}", "83f613978081f35cb5b948570fed6cff8f8fed47ab2bc232ca87f18af364eb85"]
"""


# Generated from app.agents.definitions_v7 (python -m app.agents.definitions_v7); tests/test_m11_trader.py compares.
AGENT_SEED_LINES_V7 = r"""
["AGENT_STEP_SCHEMA_V6", "AGENT_STEP_SCHEMA", 6, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V6\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One decision. ENTER_LONG and ENTER_SHORT take leverage, stop_multiple and max_hold_hours, and take_profit_multiple or null; TIGHTEN_STOP takes stop_multiple only; EXIT, HOLD and ABSTAIN take none of them. Never a price, quantity or level.\",\"properties\":{\"action\":{\"enum\":[\"ENTER_LONG\",\"ENTER_SHORT\",\"EXIT\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"cites\":{\"description\":\"At most 8 items.\",\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"description\":\"At most 300 characters.\",\"type\":\"string\"},\"leverage\":{\"enum\":[\"1\",\"2\",null],\"type\":[\"string\",\"null\"]},\"max_hold_hours\":{\"enum\":[\"1\",\"4\",\"12\",\"24\",null],\"type\":[\"string\",\"null\"]},\"rationale\":{\"description\":\"At most 600 characters.\",\"type\":\"string\"},\"reason_code\":{\"enum\":[\"SETUP_FOR_ENTRY\",\"PROTECT_POSITION\",\"TAKE_PROFIT_EARLY\",\"NO_EDGE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"LIMIT_OR_COOLDOWN\",\"RISK_EVENT_AHEAD\",\"OTHER\"],\"type\":\"string\"},\"stop_multiple\":{\"enum\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\",null],\"type\":[\"string\",\"null\"]},\"take_profit_multiple\":{\"enum\":[\"1\",\"1.5\",\"2\",\"3\",null],\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"leverage\",\"stop_multiple\",\"take_profit_multiple\",\"max_hold_hours\",\"reason_code\",\"rationale\",\"invalidation\",\"uncertainty_level\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"}},\"required\":[\"outcome\",\"decision\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v6\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"candles\":{\"description\":\"From 1 to 96.\",\"type\":[\"integer\",\"null\"]},\"interval\":{\"enum\":[\"1m\",\"5m\",\"15m\",\"1h\",null],\"type\":[\"string\",\"null\"]},\"limit\":{\"description\":\"From 1 to 10.\",\"type\":[\"integer\",\"null\"]},\"query\":{\"description\":\"At most 200 characters.\",\"type\":[\"string\",\"null\"]}},\"required\":[\"interval\",\"candles\",\"query\",\"limit\"],\"type\":\"object\"},\"purpose\":{\"description\":\"At most 280 characters.\",\"type\":\"string\"},\"tool_name\":{\"enum\":[\"query_futures_candles\",\"read_headlines\"],\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v6\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v7 and ExecPlan 0039 section 5.3.1\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":6}", "18f0ad41309af6afb2b9db7f7062ddcae8bb23a4c5c5d26a6bb707e978f826c4"]
["TOOL_CATALOG_V7", "TOOL_CATALOG", 7, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V7\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v7 and ExecPlan 0039 section 5.3.1\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"interval\",\"candles\"],\"description\":\"COORDINATOR in a futures decision. The BTCUSDT perpetual's newest complete candles before the job cutoff, built from the stored final 1m candles: interval 1m, 5m, 15m or 1h; candles 1-96. Each row is open time, open, high, low, close and volume as exact decimal text. Returns nothing newer than the cutoff.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_futures_candles\"},{\"arguments\":[\"query\",\"limit\"],\"description\":\"COORDINATOR in a futures decision. Headlines of the sources in force filed under BTCUSDT that were available by the job cutoff: the newest when query is null, else the best matches of the plain query terms; limit 1-10. Each item has an evidence ID that can be cited. A headline proves that its publisher published it, not that it is true. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_headlines\"},{\"arguments\":[],\"description\":\"FINISH only. One decision on the BTCUSDT perpetual: ENTER_LONG, ENTER_SHORT, EXIT, TIGHTEN_STOP, HOLD or ABSTAIN, with only the choices that action takes, each from the policy's set. The server writes the run, the position it saw, the context's hash and the policy; the engine computes every price, quantity, stop level, fee and margin.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_futures_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":7}", "89547d243bde5fd3fe90cbd5431f95b2d0a1c586a03ef2f5fc3b91f959122bfe"]
["ROLE_GRANTS_V7", "ROLE_GRANTS", 7, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\"],\"grants\":{\"ANALYST\":[],\"COORDINATOR\":[\"query_futures_candles\",\"read_headlines\",\"record_futures_decision\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V7\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v7 and ExecPlan 0039 section 5.3.1\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[],\"COORDINATOR\":[\"FUTURES_DECISION_V1\"],\"EVALUATOR\":[],\"RESEARCHER\":[]},\"version\":7}", "dd97eeb606d6126ed9a529ccfdcf8b937f9118a20ffeadb7740ac1f283da5bdd"]
["TEMPLATES_V7", "TEMPLATES", 7, "CODE_OWNED", "{\"delegation\":\"NONE\",\"id\":\"TEMPLATES_V7\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER_OR_FIXTURE\",\"DECISION\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M11 tool catalog v7 and ExecPlan 0039 section 5.3.1\",\"status\":\"CODE_OWNED\",\"templates\":{\"FUTURES_DECISION_V1\":{\"artifact\":\"FUTURES_DECISION\",\"cutoff\":\"THE_CONTEXT_THE_SERVER_BUILT_WHEN_IT_STARTED_WITH_ITS_HASH\",\"follow_on\":\"NONE\",\"parameters\":{\"symbols\":[\"BTCUSDT\"],\"trigger\":\"BAR_FILL_OR_SHARP_MOVE\"},\"prompt\":\"TRADER_PROMPT_M11_V1\",\"purpose\":\"DECISION\",\"quiet_window\":\"NONE\",\"role\":\"COORDINATOR\",\"schedule\":{\"bar\":\"EVERY_FINISHED_15M_BAR\",\"coalescing\":\"A_TRIGGER_IS_COVERED_BY_ANY_DECISION_STARTED_AFTER_ITS_EVENT\",\"fill\":\"RIGHT_AFTER_EACH_FILL\",\"open_at_once\":1,\"sharp_move\":\"A_MOVE_OF_MORE_THAN_THE_POLICY'S_ATR_MULTIPLE_WITHIN_ITS_WINDOW\",\"stale_after_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"while\":\"THE_RUN_IS_RUNNING_OR_A_POSITION_IS_OPEN\"},\"started_by\":[\"DECISION_TRIGGER\"],\"writes\":\"ONE_FUTURES_DECISIONS_ROW_IN_THE_TRANSACTION_THAT_ENDS_IT; A_PROBE_WRITES_NONE\"}},\"version\":7}", "0dd7bf21c22d7ec8dfa2052b1a3fc143af6447ee76441cd4fded653bfee3214d"]
["BUDGETS_V7", "BUDGETS", 7, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"DECISION\":120},\"final_output_max_bytes\":16384,\"handoff_depth\":0,\"id\":\"BUDGETS_V7\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":null,\"rejected_output_retries\":1,\"snapshot_max_bytes\":24576,\"source\":\"ExecPlan 0039 sections 5.4 and 5.5\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":300,\"templates\":{\"FUTURES_DECISION_V1\":{\"max_model_steps\":3,\"max_tool_calls\":2,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":180}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":300,\"version\":7}", "c4d9f8b3690eecdc8de32588e0a02ee56eac4167b2c783fa99d8d5c263876584"]
["TRADER_PROMPT_M11_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"TRADER_PROMPT_M11_V1\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"9908c4125b22fa29ccd6e22db17a96ae426858fffb7e82390cf0b3e028535f9d\",\"source\":\"services/agent-runner/prompts/m11/trader.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "16a1555a2ec48ea61ad50f0196582a4e97a611d079d22bb048dd8867df8e9f07"]
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


def seed_rows():
    return _frozen(FUTURES_SEED_LINES, FUTURES_KINDS, "futures definition")


def agent_rows():
    """The frozen generation-7 documents, each checked against its own hash."""
    return _frozen(AGENT_SEED_LINES_V7, AGENT_KINDS, "generation-7 agent definition")


TABLES_SQL = """
CREATE TABLE futures_runs (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    cost_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    cost_sha256 varchar(64) NOT NULL CHECK (cost_sha256 ~ '^[0-9a-f]{64}$'),
    code_identity varchar(64) NOT NULL CHECK (code_identity ~ '^[0-9a-f]{64}$'),
    started_by varchar(8) NOT NULL CHECK (started_by IN ('SYSTEM','OWNER')),
    request_id uuid,
    state varchar(10) NOT NULL CHECK (state IN ('RUNNING','PAUSED','STOPPING','STOPPED')),
    causes text[] NOT NULL DEFAULT '{}'
        CHECK (causes <@ ARRAY['OWNER','DAILY_LOSS','DRAWDOWN','INTEGRITY']::text[]),
    started_at timestamptz NOT NULL,
    start_equity numeric(38,8) NOT NULL CHECK (start_equity > 0),
    start_nav numeric(72,36) NOT NULL CHECK (start_nav > 0),
    high_water_nav numeric(72,36) NOT NULL CHECK (high_water_nav >= start_nav),
    stopped_at timestamptz,
    stop_reason varchar(12) CHECK (stop_reason IN ('OWNER','DRAWDOWN')),
    version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_run_stopped CHECK ((state = 'STOPPED') = (stopped_at IS NOT NULL AND stop_reason IS NOT NULL)),
    CONSTRAINT futures_run_starter CHECK ((started_by = 'OWNER') = (request_id IS NOT NULL)),
    CONSTRAINT futures_run_causes CHECK ((state <> 'PAUSED' OR cardinality(causes) > 0)
        AND (state <> 'RUNNING' OR cardinality(causes) = 0))
);
CREATE UNIQUE INDEX futures_runs_one_live ON futures_runs ((true)) WHERE state <> 'STOPPED';

CREATE TABLE futures_owner_requests (
    id uuid PRIMARY KEY,
    kind varchar(8) NOT NULL CHECK (kind IN ('PAUSE','RESUME','STOP','START')),
    run_id uuid REFERENCES futures_runs(id),
    close_position boolean NOT NULL DEFAULT false,
    idempotency_key varchar(80) NOT NULL UNIQUE CHECK (idempotency_key ~ '^[A-Za-z0-9_-]{8,80}$'),
    request_hash varchar(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    status varchar(10) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','APPLIED','REJECTED')),
    reasons text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    answered_at timestamptz,
    CONSTRAINT futures_request_answer CHECK ((status = 'PENDING') = (answered_at IS NULL)),
    CONSTRAINT futures_request_close CHECK (NOT close_position OR kind = 'STOP'),
    CONSTRAINT futures_request_target CHECK ((kind = 'START') = (run_id IS NULL))
);
CREATE INDEX futures_owner_requests_pending ON futures_owner_requests (created_at) WHERE status = 'PENDING';
ALTER TABLE futures_runs ADD CONSTRAINT futures_runs_request_fkey
    FOREIGN KEY (request_id) REFERENCES futures_owner_requests(id);

CREATE TABLE futures_run_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES futures_runs(id),
    kind varchar(32) NOT NULL,
    actor varchar(8) NOT NULL CHECK (actor IN ('SYSTEM','OWNER')),
    request_id uuid REFERENCES futures_owner_requests(id),
    at timestamptz NOT NULL,
    detail jsonb NOT NULL DEFAULT '{}',
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_event_owner CHECK (actor = 'SYSTEM' OR request_id IS NOT NULL)
);
CREATE INDEX futures_run_events_run ON futures_run_events (run_id, id);

CREATE TABLE futures_decisions (
    id uuid PRIMARY KEY,
    workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id),
    run_id uuid REFERENCES futures_runs(id),
    trigger varchar(12) NOT NULL CHECK (trigger IN ('BAR','FILL','SHARP_MOVE')),
    bar_open_ms bigint CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    context_at timestamptz NOT NULL,
    context_sha256 varchar(64) NOT NULL CHECK (context_sha256 ~ '^[0-9a-f]{64}$'),
    seen_position_id uuid,
    action varchar(12) NOT NULL
        CHECK (action IN ('ENTER_LONG','ENTER_SHORT','EXIT','TIGHTEN_STOP','HOLD','ABSTAIN')),
    leverage numeric CHECK (leverage IN (1, 2)),
    stop_multiple numeric CHECK (stop_multiple IN (1.0, 1.5, 2.0, 3.0)),
    take_profit_multiple numeric CHECK (take_profit_multiple IN (1, 1.5, 2, 3)),
    max_hold_hours integer CHECK (max_hold_hours IN (1, 4, 12, 24)),
    rationale text NOT NULL CHECK (char_length(rationale) BETWEEN 1 AND 2000),
    policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_decision_shape CHECK (CASE action
        WHEN 'ENTER_LONG' THEN leverage IS NOT NULL AND stop_multiple IS NOT NULL AND max_hold_hours IS NOT NULL
            AND seen_position_id IS NULL
        WHEN 'ENTER_SHORT' THEN leverage IS NOT NULL AND stop_multiple IS NOT NULL AND max_hold_hours IS NOT NULL
            AND seen_position_id IS NULL
        WHEN 'EXIT' THEN seen_position_id IS NOT NULL AND leverage IS NULL AND stop_multiple IS NULL
            AND take_profit_multiple IS NULL AND max_hold_hours IS NULL
        WHEN 'TIGHTEN_STOP' THEN seen_position_id IS NOT NULL AND stop_multiple IS NOT NULL AND leverage IS NULL
            AND take_profit_multiple IS NULL AND max_hold_hours IS NULL
        ELSE leverage IS NULL AND stop_multiple IS NULL AND take_profit_multiple IS NULL AND max_hold_hours IS NULL
        END)
);
CREATE INDEX futures_decisions_created ON futures_decisions (created_at);

CREATE TABLE futures_positions (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    run_id uuid NOT NULL REFERENCES futures_runs(id),
    decision_id uuid NOT NULL UNIQUE REFERENCES futures_decisions(id),
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    leverage numeric NOT NULL CHECK (leverage IN (1, 2)),
    quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
    entry_price numeric(38,8) NOT NULL CHECK (entry_price > 0),
    notional numeric(38,8) NOT NULL CHECK (notional > 0),
    margin numeric(38,8) NOT NULL CHECK (margin > 0),
    maintenance_rate numeric NOT NULL CHECK (maintenance_rate > 0 AND maintenance_rate < 1),
    maintenance_amount numeric NOT NULL CHECK (maintenance_amount >= 0),
    liquidation_price numeric(38,8) CHECK (liquidation_price > 0),
    atr numeric NOT NULL CHECK (atr > 0),
    stop_multiple numeric NOT NULL CHECK (stop_multiple IN (1.0, 1.5, 2.0, 3.0)),
    take_profit_multiple numeric CHECK (take_profit_multiple IN (1, 1.5, 2, 3)),
    max_hold_hours integer NOT NULL CHECK (max_hold_hours IN (1, 4, 12, 24)),
    initial_stop numeric(38,8) NOT NULL CHECK (initial_stop > 0),
    stop_price numeric(38,8) NOT NULL CHECK (stop_price > 0),
    take_profit numeric(38,8) CHECK (take_profit > 0),
    risk numeric(38,8) NOT NULL CHECK (risk >= 0),
    risk_cap numeric(38,8) NOT NULL CHECK (risk_cap > 0 AND risk <= risk_cap),
    opened_at timestamptz NOT NULL,
    time_exit_at timestamptz NOT NULL CHECK (time_exit_at > opened_at),
    state varchar(6) NOT NULL CHECK (state IN ('OPEN','CLOSED')),
    closed_at timestamptz,
    close_reason varchar(12)
        CHECK (close_reason IN ('STOP','TAKE_PROFIT','TIME','LIQUIDATION','AGENT_EXIT','OWNER_STOP')),
    exit_price numeric(38,8) CHECK (exit_price > 0),
    realized_pnl numeric(38,8),
    fees numeric(38,8) NOT NULL CHECK (fees >= 0),
    version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
    CONSTRAINT futures_position_closed CHECK ((state = 'CLOSED') = (closed_at IS NOT NULL AND close_reason IS NOT NULL
        AND exit_price IS NOT NULL AND realized_pnl IS NOT NULL)),
    CONSTRAINT futures_position_initial_stop CHECK (CASE side WHEN 'LONG' THEN initial_stop < entry_price
        ELSE initial_stop > entry_price END),
    CONSTRAINT futures_position_take_profit CHECK (take_profit IS NULL OR CASE side
        WHEN 'LONG' THEN take_profit > entry_price ELSE take_profit < entry_price END),
    CONSTRAINT futures_position_liquidation CHECK (liquidation_price IS NULL OR CASE side
        WHEN 'LONG' THEN liquidation_price < initial_stop ELSE liquidation_price > initial_stop END)
);
CREATE UNIQUE INDEX futures_positions_one_open ON futures_positions ((true)) WHERE state = 'OPEN';
ALTER TABLE futures_decisions ADD CONSTRAINT futures_decisions_position_fkey
    FOREIGN KEY (seen_position_id) REFERENCES futures_positions(id);

CREATE TABLE futures_fills (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    position_id uuid NOT NULL REFERENCES futures_positions(id),
    kind varchar(12) NOT NULL CHECK (kind IN ('ENTRY','EXIT','LIQUIDATION')),
    reason varchar(12) NOT NULL
        CHECK (reason IN ('AGENT_ENTRY','STOP','TAKE_PROFIT','TIME','LIQUIDATION','AGENT_EXIT','OWNER_STOP')),
    order_side varchar(4) NOT NULL CHECK (order_side IN ('BUY','SELL')),
    quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
    price numeric(38,8) NOT NULL CHECK (price > 0),
    average_price numeric NOT NULL CHECK (average_price > 0),
    slippage_bps numeric NOT NULL CHECK (slippage_bps >= 0),
    fee numeric(38,8) NOT NULL CHECK (fee >= 0),
    fee_rate numeric NOT NULL CHECK (fee_rate >= 0),
    -- The book levels taken, [price, quantity] decimal strings best first (empty for a liquidation, on the mark).
    levels jsonb NOT NULL CHECK (jsonb_typeof(levels) = 'array'),
    quote_second timestamptz,
    mark_second timestamptz,
    mark_price numeric(38,8),
    filled_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_fill_source CHECK (CASE kind WHEN 'LIQUIDATION' THEN mark_second IS NOT NULL
        AND mark_price IS NOT NULL AND fee = 0 ELSE quote_second IS NOT NULL END)
);
CREATE UNIQUE INDEX futures_fills_entry ON futures_fills (position_id) WHERE kind = 'ENTRY';
CREATE UNIQUE INDEX futures_fills_close ON futures_fills (position_id) WHERE kind <> 'ENTRY';
CREATE INDEX futures_fills_filled ON futures_fills (filled_at);

CREATE TABLE futures_funding (
    id uuid PRIMARY KEY,
    position_id uuid NOT NULL REFERENCES futures_positions(id),
    funding_ms bigint NOT NULL CHECK (funding_ms > 0),
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
    status varchar(8) NOT NULL CHECK (status IN ('PENDING','POSTED')),
    rate numeric CHECK (rate > -1 AND rate < 1),
    mark numeric(38,8) CHECK (mark > 0),
    mark_source varchar(12) CHECK (mark_source IN ('SETTLED_RATE','MARK_STREAM')),
    amount numeric(38,8),
    recorded_at timestamptz NOT NULL,
    posted_at timestamptz,
    UNIQUE (position_id, funding_ms),
    CONSTRAINT futures_funding_posted CHECK ((status = 'POSTED') = (rate IS NOT NULL AND mark IS NOT NULL
        AND mark_source IS NOT NULL AND amount IS NOT NULL AND posted_at IS NOT NULL))
);
CREATE INDEX futures_funding_pending ON futures_funding (funding_ms) WHERE status = 'PENDING';

CREATE TABLE futures_ledger_events (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    kind varchar(18) NOT NULL CHECK (kind IN ('MARGIN_RESERVED','MARGIN_RELEASED','TRADING_FEE','REALIZED_PNL',
        'FUNDING_PAID','FUNDING_RECEIVED','LIQUIDATION')),
    position_id uuid NOT NULL REFERENCES futures_positions(id),
    fill_id uuid REFERENCES futures_fills(id),
    funding_id uuid UNIQUE REFERENCES futures_funding(id),
    cash_delta numeric(38,8) NOT NULL,
    margin_delta numeric(38,8) NOT NULL,
    account_version bigint NOT NULL CHECK (account_version > 0),
    at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (fill_id, kind),
    CONSTRAINT futures_ledger_shape CHECK (CASE kind
        WHEN 'MARGIN_RESERVED' THEN cash_delta = 0 AND margin_delta > 0 AND fill_id IS NOT NULL AND funding_id IS NULL
        WHEN 'MARGIN_RELEASED' THEN cash_delta = 0 AND margin_delta < 0 AND fill_id IS NOT NULL AND funding_id IS NULL
        WHEN 'TRADING_FEE' THEN cash_delta < 0 AND margin_delta = 0 AND fill_id IS NOT NULL AND funding_id IS NULL
        WHEN 'REALIZED_PNL' THEN cash_delta <> 0 AND margin_delta = 0 AND fill_id IS NOT NULL AND funding_id IS NULL
        WHEN 'LIQUIDATION' THEN cash_delta < 0 AND margin_delta = 0 AND fill_id IS NOT NULL AND funding_id IS NULL
        WHEN 'FUNDING_PAID' THEN cash_delta < 0 AND margin_delta = 0 AND fill_id IS NULL AND funding_id IS NOT NULL
        ELSE cash_delta > 0 AND margin_delta = 0 AND fill_id IS NULL AND funding_id IS NOT NULL END)
);
CREATE INDEX futures_ledger_events_position ON futures_ledger_events (position_id);

CREATE TABLE futures_decision_answers (
    decision_id uuid PRIMARY KEY REFERENCES futures_decisions(id),
    outcome varchar(8) NOT NULL CHECK (outcome IN ('FILLED','APPLIED','NOTED','REFUSED')),
    codes text[] NOT NULL DEFAULT '{}',
    position_id uuid REFERENCES futures_positions(id),
    fill_id uuid REFERENCES futures_fills(id),
    detail jsonb NOT NULL DEFAULT '{}',
    answered_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_answer_codes CHECK ((outcome = 'REFUSED') = (cardinality(codes) > 0))
);

CREATE TABLE futures_valuations (
    id uuid PRIMARY KEY,
    run_id uuid REFERENCES futures_runs(id),
    valued_at timestamptz NOT NULL,
    purpose varchar(16) NOT NULL CHECK (purpose IN ('START','FILL','FUNDING','PERIODIC','HOURLY','DAILY_REFERENCE',
        'HIGH_WATER','LATCH','STOP')),
    cash numeric(38,8) NOT NULL,
    reserved numeric(38,8) NOT NULL,
    position_id uuid REFERENCES futures_positions(id),
    mark numeric(38,8),
    mark_second timestamptz,
    unrealized numeric(38,8),
    pending_funding integer NOT NULL DEFAULT 0 CHECK (pending_funding >= 0),
    equity numeric(38,8),
    units numeric(72,36) NOT NULL,
    nav numeric(72,36),
    quality varchar(8) NOT NULL CHECK (quality IN ('VALID','INVALID')),
    reason varchar(48),
    account_version bigint NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_valuation_quality CHECK ((quality = 'VALID') = (equity IS NOT NULL AND nav IS NOT NULL)),
    CONSTRAINT futures_valuation_mark CHECK (position_id IS NULL OR quality = 'INVALID'
        OR (mark IS NOT NULL AND unrealized IS NOT NULL))
);
CREATE INDEX futures_valuations_valued ON futures_valuations (valued_at DESC);

CREATE TABLE futures_daily_references (
    utc_date date PRIMARY KEY,
    valuation_id uuid NOT NULL REFERENCES futures_valuations(id),
    nav numeric(72,36) NOT NULL CHECK (nav > 0),
    quality varchar(20) NOT NULL CHECK (quality IN ('TIMELY','LATE_CONSERVATIVE')),
    lateness_ms bigint NOT NULL CHECK (lateness_ms >= 0),
    basis jsonb NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE futures_latches (
    id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES futures_runs(id),
    cause varchar(12) NOT NULL CHECK (cause IN ('DAILY_LOSS','DRAWDOWN')),
    latched_at timestamptz NOT NULL,
    valuation_id uuid NOT NULL REFERENCES futures_valuations(id),
    trigger jsonb NOT NULL,
    resolved_at timestamptz,
    resolution jsonb,
    CONSTRAINT futures_latch_resolution CHECK ((resolved_at IS NULL) = (resolution IS NULL))
);
CREATE UNIQUE INDEX futures_latches_open ON futures_latches (run_id, cause) WHERE resolved_at IS NULL;
"""

GUARDS_SQL = """
CREATE FUNCTION asl_futures_append_only() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN RAISE EXCEPTION 'append-only futures record'; END $$;

-- A run: its identity and start never change; a stopped run never changes; its high-water NAV never falls.
CREATE FUNCTION asl_futures_run_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.state = 'STOPPED' THEN RAISE EXCEPTION 'stopped futures run cannot change'; END IF;
    IF (NEW.id, NEW.seq, NEW.policy_id, NEW.policy_sha256, NEW.cost_id, NEW.cost_sha256, NEW.code_identity,
            NEW.started_by, NEW.request_id, NEW.started_at, NEW.start_equity, NEW.start_nav, NEW.recorded_at)
            IS DISTINCT FROM (OLD.id, OLD.seq, OLD.policy_id, OLD.policy_sha256, OLD.cost_id, OLD.cost_sha256,
            OLD.code_identity, OLD.started_by, OLD.request_id, OLD.started_at, OLD.start_equity, OLD.start_nav,
            OLD.recorded_at) THEN
        RAISE EXCEPTION 'futures run identity is immutable'; END IF;
    IF NEW.high_water_nav < OLD.high_water_nav THEN RAISE EXCEPTION 'run high-water NAV cannot decrease'; END IF;
    IF OLD.state = 'STOPPING' AND NEW.state IN ('RUNNING','PAUSED') THEN
        RAISE EXCEPTION 'a stopping futures run cannot resume'; END IF;
    RETURN NEW;
END $$;

-- An owner request is answered once by the engine; nothing else of it changes.
CREATE FUNCTION asl_futures_request_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.status <> 'PENDING' THEN RAISE EXCEPTION 'answered owner request cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['status','reasons','answered_at'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','reasons','answered_at']) THEN
        RAISE EXCEPTION 'owner request is immutable'; END IF;
    RETURN NEW;
END $$;

-- A position: its terms never change, the stop only tightens, and a closed position never changes.
CREATE FUNCTION asl_futures_position_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.state = 'CLOSED' THEN RAISE EXCEPTION 'closed futures position cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['stop_price','state','closed_at','close_reason','exit_price','realized_pnl','fees',
            'version']) IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['stop_price','state','closed_at','close_reason',
            'exit_price','realized_pnl','fees','version']) THEN
        RAISE EXCEPTION 'futures position terms are immutable'; END IF;
    IF (OLD.side = 'LONG' AND NEW.stop_price < OLD.stop_price)
            OR (OLD.side = 'SHORT' AND NEW.stop_price > OLD.stop_price) THEN
        RAISE EXCEPTION 'a futures stop only tightens'; END IF;
    IF NEW.fees < OLD.fees THEN RAISE EXCEPTION 'position fees cannot decrease'; END IF;
    RETURN NEW;
END $$;

-- A funding record is posted once with its rate and mark; a posted one never changes.
CREATE FUNCTION asl_futures_funding_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.status <> 'PENDING' THEN RAISE EXCEPTION 'posted funding cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['status','rate','mark','mark_source','amount','posted_at'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','rate','mark','mark_source','amount','posted_at']) THEN
        RAISE EXCEPTION 'funding record identity is immutable'; END IF;
    RETURN NEW;
END $$;

-- A latch is resolved once.
CREATE FUNCTION asl_futures_latch_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.resolved_at IS NOT NULL THEN RAISE EXCEPTION 'resolved latch cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['resolved_at','resolution'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['resolved_at','resolution']) THEN
        RAISE EXCEPTION 'latch identity is immutable'; END IF;
    RETURN NEW;
END $$;

-- The trader's decision comes only from the agent identity, for its own running workflow of the futures template,
-- never from a probe; the engine reads it in its own fenced step.
CREATE FUNCTION asl_futures_decision_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE w record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a futures decision comes only from the trader'; END IF;
    SELECT template_id, purpose, state INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.template_id <> 'FUTURES_DECISION_V1' OR w.purpose <> 'DECISION' OR w.state <> 'RUNNING' THEN
        RAISE EXCEPTION 'a futures decision needs its running futures decision workflow'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_runs_guard BEFORE UPDATE ON futures_runs
    FOR EACH ROW EXECUTE FUNCTION asl_futures_run_guard();
CREATE TRIGGER futures_owner_requests_guard BEFORE UPDATE ON futures_owner_requests
    FOR EACH ROW EXECUTE FUNCTION asl_futures_request_guard();
CREATE TRIGGER futures_positions_guard BEFORE UPDATE ON futures_positions
    FOR EACH ROW EXECUTE FUNCTION asl_futures_position_guard();
CREATE TRIGGER futures_funding_guard BEFORE UPDATE ON futures_funding
    FOR EACH ROW EXECUTE FUNCTION asl_futures_funding_guard();
CREATE TRIGGER futures_latches_guard BEFORE UPDATE ON futures_latches
    FOR EACH ROW EXECUTE FUNCTION asl_futures_latch_guard();
CREATE TRIGGER futures_decisions_source BEFORE INSERT ON futures_decisions
    FOR EACH ROW EXECUTE FUNCTION asl_futures_decision_guard();
"""

APPEND_ONLY = ("futures_run_events", "futures_decisions", "futures_fills", "futures_ledger_events",
               "futures_decision_answers", "futures_valuations", "futures_daily_references")
NO_DELETE = ("futures_runs", "futures_owner_requests", "futures_positions", "futures_funding", "futures_latches")

JOURNAL_SQL = """
ALTER TABLE journal_transactions ADD COLUMN futures_event_id uuid UNIQUE REFERENCES futures_ledger_events(id);
ALTER TABLE journal_transactions DROP CONSTRAINT journal_single_source,
    ADD CONSTRAINT journal_single_source CHECK (num_nonnulls(funding_request_id, fill_id, futures_event_id) = 1);
ALTER TABLE journal_postings DROP CONSTRAINT journal_account,
    ADD CONSTRAINT journal_account CHECK (book_account IN {new_accounts});
ALTER TABLE journal_postings DROP CONSTRAINT journal_account_asset,
    ADD CONSTRAINT journal_account_asset CHECK (
        (book_account NOT IN ('OWNER_CASH','VIRTUAL_CAPITAL','TRADING_PNL','FUNDING') OR asset = 'USDT')
        AND (book_account <> 'OWNER_ASSET' OR asset IN {assets}));

CREATE OR REPLACE FUNCTION asl_journal_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user = 'asl_api' AND NEW.funding_request_id IS NOT NULL
        AND NEW.fill_id IS NULL AND NEW.futures_event_id IS NULL THEN RETURN NEW; END IF;
    IF current_user = 'asl_execution' AND NEW.fill_id IS NOT NULL
        AND NEW.funding_request_id IS NULL AND NEW.futures_event_id IS NULL THEN RETURN NEW; END IF;
    -- M11: a futures ledger event, from the execution identity alone.
    IF current_user = 'asl_execution' AND NEW.futures_event_id IS NOT NULL
        AND NEW.funding_request_id IS NULL AND NEW.fill_id IS NULL THEN RETURN NEW; END IF;
    RAISE EXCEPTION 'journal source not permitted for this role';
END $$;

CREATE OR REPLACE FUNCTION asl_posting_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE header record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    SELECT funding_request_id, fill_id, futures_event_id, created_txid INTO header
        FROM journal_transactions WHERE id = NEW.tx_id;
    IF NOT FOUND OR header.created_txid IS DISTINCT FROM
            ((pg_current_xact_id())::text)::bigint THEN
        RAISE EXCEPTION 'postings must be written with their journal header';
    END IF;
    IF current_user = 'asl_api' AND header.funding_request_id IS NOT NULL THEN RETURN NEW; END IF;
    IF current_user = 'asl_execution' AND (header.fill_id IS NOT NULL OR header.futures_event_id IS NOT NULL) THEN
        RETURN NEW; END IF;
    RAISE EXCEPTION 'posting source not permitted for this role';
END $$;
"""

JOURNAL_DOWN_SQL = """
CREATE OR REPLACE FUNCTION asl_journal_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user = 'asl_api' AND NEW.funding_request_id IS NOT NULL
        AND NEW.fill_id IS NULL THEN RETURN NEW; END IF;
    IF current_user = 'asl_execution' AND NEW.fill_id IS NOT NULL
        AND NEW.funding_request_id IS NULL THEN RETURN NEW; END IF;
    RAISE EXCEPTION 'journal source not permitted for this role';
END $$;

CREATE OR REPLACE FUNCTION asl_posting_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE header record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    SELECT funding_request_id, fill_id, created_txid INTO header
        FROM journal_transactions WHERE id = NEW.tx_id;
    IF NOT FOUND OR header.created_txid IS DISTINCT FROM
            ((pg_current_xact_id())::text)::bigint THEN
        RAISE EXCEPTION 'postings must be written with their journal header';
    END IF;
    IF current_user = 'asl_api' AND header.funding_request_id IS NOT NULL THEN RETURN NEW; END IF;
    IF current_user = 'asl_execution' AND header.fill_id IS NOT NULL THEN RETURN NEW; END IF;
    RAISE EXCEPTION 'posting source not permitted for this role';
END $$;

ALTER TABLE journal_postings DROP CONSTRAINT journal_account_asset,
    ADD CONSTRAINT journal_account_asset CHECK (
        (book_account NOT IN ('OWNER_CASH','VIRTUAL_CAPITAL') OR asset = 'USDT')
        AND (book_account <> 'OWNER_ASSET' OR asset IN {assets}));
ALTER TABLE journal_postings DROP CONSTRAINT journal_account,
    ADD CONSTRAINT journal_account CHECK (book_account IN {old_accounts});
ALTER TABLE journal_transactions DROP CONSTRAINT journal_single_source,
    ADD CONSTRAINT journal_single_source CHECK (num_nonnulls(funding_request_id, fill_id) = 1);
ALTER TABLE journal_transactions DROP COLUMN futures_event_id;
"""

# The trader reads the perpetual's market data and the futures account through these, as it reads the spot ones.
VIEWS_SQL = """
CREATE VIEW agent_read.futures_quotes WITH (security_barrier = true) AS
    SELECT second_at, bid, bid_qty, ask, ask_qty, bids, asks, event_at FROM perp_quotes;
CREATE VIEW agent_read.futures_marks WITH (security_barrier = true) AS
    SELECT second_at, mark, index_price, funding_rate, next_funding_at, event_at FROM perp_marks;
CREATE VIEW agent_read.futures_bars WITH (security_barrier = true) AS
    SELECT open_ms, open, high, low, close, volume, quote_volume, trades, final FROM perp_bars;
CREATE VIEW agent_read.futures_funding_rates WITH (security_barrier = true) AS
    SELECT funding_ms, rate, mark FROM perp_funding_rates;
CREATE VIEW agent_read.futures_instrument WITH (security_barrier = true) AS
    SELECT id, status, usable, tick_size, step_size, min_qty, market_max_qty, min_notional, checked_at
    FROM perp_instruments;
CREATE VIEW agent_read.futures_feed WITH (security_barrier = true) AS
    SELECT status, reason, last_quote_at, last_mark_at, clock_verified, heartbeat_at FROM perp_feed_state;
CREATE VIEW agent_read.futures_account WITH (security_barrier = true) AS
    SELECT version AS account_version, initialized, cash, reserved, contributions, units, nav, high_water_nav,
           valuation_valid, paused, reconciliation_failed FROM account_state WHERE id = 1;
CREATE VIEW agent_read.futures_runs WITH (security_barrier = true) AS
    SELECT id, seq, policy_id, policy_sha256, state, causes, started_at, start_nav, high_water_nav, stopped_at,
           stop_reason FROM futures_runs;
CREATE VIEW agent_read.futures_positions WITH (security_barrier = true) AS
    SELECT id, seq, run_id, decision_id, side, leverage, quantity, entry_price, notional, margin, liquidation_price,
           atr, stop_multiple, take_profit_multiple, max_hold_hours, initial_stop, stop_price, take_profit, risk,
           opened_at, time_exit_at, state, closed_at, close_reason, exit_price, realized_pnl, fees
    FROM futures_positions;
CREATE VIEW agent_read.futures_fills WITH (security_barrier = true) AS
    SELECT id, seq, position_id, kind, reason, order_side, quantity, price, fee, filled_at FROM futures_fills;
CREATE VIEW agent_read.futures_funding WITH (security_barrier = true) AS
    SELECT position_id, funding_ms, status, rate, mark, amount FROM futures_funding;
CREATE VIEW agent_read.futures_answers WITH (security_barrier = true) AS
    SELECT decision_id, outcome, codes, position_id, fill_id, detail, answered_at FROM futures_decision_answers;
CREATE VIEW agent_read.futures_valuations WITH (security_barrier = true) AS
    SELECT valued_at, purpose, equity, nav, unrealized, quality, reason FROM futures_valuations;
CREATE VIEW agent_read.futures_policies WITH (security_barrier = true) AS
    SELECT id, kind, version, status, sha256, created_at FROM execution_definitions WHERE kind = 'FUTURES_POLICY';
"""

# 0010's verification guard, which also accepts a check bound to an installed futures policy (the agents' check of
# the futures trader, app.agents.check). Downgrade restores 0010's text exactly.
VERIFICATION_GUARD = """
CREATE OR REPLACE FUNCTION asl_m7_verification_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE p record;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'decision verifications are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT profile_id, profile_sha256, state, suite, policy_id, policy_sha256 INTO p FROM agent_probe_runs
        WHERE id = NEW.probe_run_id;
    IF NOT FOUND OR p.profile_id <> NEW.profile_id OR p.profile_sha256 <> NEW.profile_sha256
            OR p.suite NOT IN ('DECISION','CHECK') OR p.policy_id IS DISTINCT FROM NEW.policy_id OR p.policy_sha256 IS DISTINCT FROM NEW.policy_sha256
            OR (NEW.status = 'VERIFIED' AND p.state <> 'PASSED')
            OR (NEW.status = 'FAILED' AND p.state NOT IN ('FAILED','CANCELED')) THEN
        RAISE EXCEPTION 'a decision verification records its finished decision probe run'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_read.policy_definitions WHERE id = NEW.policy_id
                   AND sha256 = NEW.policy_sha256 AND kind = 'STRATEGY'){futures} THEN
        RAISE EXCEPTION 'a decision verification names an installed operating policy'; END IF;
    RETURN NEW;
END $$;
"""
FUTURES_POLICY_RULE = (" AND NOT (p.suite = 'CHECK' AND EXISTS (SELECT 1 FROM agent_read.futures_policies "
                       "WHERE id = NEW.policy_id AND sha256 = NEW.policy_sha256))")

GRANTS_SQL = """
GRANT SELECT ON perp_instruments, perp_quotes, perp_marks, perp_bars, perp_funding_rates, perp_feed_state
    TO asl_execution;
GRANT SELECT, INSERT ON futures_runs, futures_run_events, futures_positions, futures_fills, futures_funding,
    futures_ledger_events, futures_decision_answers, futures_valuations, futures_daily_references, futures_latches
    TO asl_execution;
GRANT SELECT ON futures_owner_requests, futures_decisions TO asl_execution;
GRANT UPDATE (state, causes, high_water_nav, stopped_at, stop_reason, version) ON futures_runs TO asl_execution;
GRANT UPDATE (status, reasons, answered_at) ON futures_owner_requests TO asl_execution;
GRANT UPDATE (stop_price, state, closed_at, close_reason, exit_price, realized_pnl, fees, version)
    ON futures_positions TO asl_execution;
GRANT UPDATE (status, rate, mark, mark_source, amount, posted_at) ON futures_funding TO asl_execution;
GRANT UPDATE (resolved_at, resolution) ON futures_latches TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE futures_runs_seq_seq, futures_run_events_id_seq, futures_positions_seq_seq,
    futures_fills_seq_seq, futures_ledger_events_seq_seq TO asl_execution;
GRANT SELECT ON futures_runs, futures_run_events, futures_owner_requests, futures_decisions, futures_positions,
    futures_fills, futures_funding, futures_ledger_events, futures_decision_answers, futures_valuations,
    futures_daily_references, futures_latches TO asl_api;
GRANT INSERT ON futures_owner_requests TO asl_api;
GRANT SELECT, INSERT ON futures_decisions TO asl_agent;
"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               "ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN "
               f"{_quoted((*DEFINITION_KINDS, *FUTURES_KINDS))})")
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})  # one name per use: each has its own type
    op.execute(TABLES_SQL)
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH))
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only()")
    for table in NO_DELETE:
        op.execute(f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only()")
    op.execute("LOCK TABLE journal_transactions, journal_postings IN ACCESS EXCLUSIVE MODE")
    op.execute(JOURNAL_SQL.replace("{path}", SEARCH_PATH).replace("{new_accounts}", NEW_ACCOUNTS)
               .replace("{assets}", ASSETS))
    op.execute(VIEWS_SQL)
    op.execute(f"GRANT SELECT ON {', '.join('agent_read.' + view for view in VIEWS)} TO asl_agent")
    op.execute(GRANTS_SQL)
    for row in agent_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               "ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN "
               f"{_quoted((*ARTIFACT_KINDS, *ARTIFACT_ADDED))})")
    op.execute(VERIFICATION_GUARD.replace("{futures}", FUTURES_POLICY_RULE))


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_runs) + (SELECT count(*) FROM futures_decisions) "
        "+ (SELECT count(*) FROM futures_owner_requests) "
        "+ (SELECT count(*) FROM journal_transactions WHERE futures_event_id IS NOT NULL) "
        "+ (SELECT count(*) FROM agent_artifacts WHERE kind = 'FUTURES_DECISION') "
        "+ (SELECT count(*) FROM agent_workflows WHERE template_id = 'FUTURES_DECISION_V1') "
        "+ (SELECT count(*) FROM decision_verifications WHERE policy_id = 'FUTURES_POLICY_V1')").scalar_one()
    if held:
        raise RuntimeError("futures records exist; downgrade refused; fix forward")
    op.execute(VERIFICATION_GUARD.replace("{futures}", ""))
    op.execute("ALTER TABLE agent_artifacts DROP CONSTRAINT agent_artifacts_kind_check, "
               f"ADD CONSTRAINT agent_artifacts_kind_check CHECK (kind IN {_quoted(ARTIFACT_KINDS)})")
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M11 generation-7 definition mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute(f"DROP VIEW {', '.join('agent_read.' + view for view in VIEWS)}")
    op.execute("LOCK TABLE journal_transactions, journal_postings IN ACCESS EXCLUSIVE MODE")
    op.execute(JOURNAL_DOWN_SQL.replace("{path}", SEARCH_PATH).replace("{old_accounts}", OLD_ACCOUNTS)
               .replace("{assets}", ASSETS))
    op.execute(f"DROP TABLE {', '.join(TABLES)}")
    op.execute("DROP FUNCTION asl_futures_append_only(), asl_futures_run_guard(), asl_futures_request_guard(), "
               "asl_futures_position_guard(), asl_futures_funding_guard(), asl_futures_latch_guard(), "
               "asl_futures_decision_guard()")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen rows, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in seed_rows():
        bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s", row)
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(DEFINITION_KINDS)})")
