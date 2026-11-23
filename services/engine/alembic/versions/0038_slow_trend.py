"""ExecPlan 0057: the slow trend twin (``TWIN_SET_V3``) and the feed's daily candles.

Revision ID: 0038_slow_trend
Revises: 0036_claude_backtest

ExecPlan 0057 sections 4.2 and 4.3. Additive: nothing of the owner's account, its journal, its reservations, the
futures engine's tables, the trader, the five twins of ``TWIN_SET_V2`` or the backtests changes.

- ``TWIN_SET_V3`` in ``execution_definitions`` (frozen here, checked against the code): part 2's five twins carried
  with the same rules and values, and ``TREND_SLOW``, the slow trend rule sized to a volatility target.
- ``futures_twins.twin`` and ``futures_decision_scores.twin`` take ``TREND_SLOW``; ``futures_twin_candidates.rule``
  takes ``SLOW_TREND``. The twin's day is kept in 0030's ``rule_day``, its reading in a ``DAY_SIGNAL`` event.
- ``perp_daily_bars``: Binance's final 1-day candles of the BTCUSDT perpetual, one row per UTC day, written by the
  market worker's feed alone and never changed or deleted (migration 0019's ``asl_perp_append_only``); the slow trend
  twin reads 366 days of closes from it, which the seven-day 1-minute store cannot give.
- ``agent_read.futures_feed_events`` (0022's view, which the trade reviews' facts count in a trade's window) leaves
  out the daily job's notes, ``DAILY_STORED`` and ``DAILY_FAILED``: the twin's candles are nothing the trader or its
  agents read, so their facts stay as they were.

Downgrade is refused once a ``TREND_SLOW`` twin, one of its candidates or a daily candle exists; otherwise it removes
the table, the set and the names, and restores 0030's checks and 0022's view.
"""

import hashlib
import json

from alembic import op

revision = "0038_slow_trend"
down_revision = "0037_latest_backtest"
branch_labels = None
depends_on = None

TWINS_V2 = ("HOLD", "TREND", "TREND_GATED", "TREND_VETO", "MOMENTUM_1W")
TWINS_ADDED = ("TREND_SLOW",)
RULES_V2 = ("HOLD_START", "EMA_CROSS", "DAY_MOMENTUM")
RULES_ADDED = ("SLOW_TREND",)

# The frozen set: ``python -m app.futures.twins v3`` prints it; tests/test_m11_slow_trend_unit.py checks it.
TWIN_SEED_LINES_V3 = r"""
["TWIN_SET_V3", "FUTURES_TWINS", 3, "PROPOSED", "{\"carried\":{\"from\":\"TWIN_SET_V2\",\"new\":\"A_TWIN_OF_THIS_SET_THAT_HAS_NEVER_STARTED_STARTS_SEGMENT_1_UNDER_THIS_SET\",\"rule\":\"A_TWIN_WHOSE_RULE_AND_VALUES_ARE_UNCHANGED_GOES_ON_IN_THE_SEGMENT_IT_STARTED_UNDER_ITS_SET\",\"twins\":[\"HOLD\",\"TREND\",\"TREND_GATED\",\"TREND_VETO\",\"MOMENTUM_1W\"]},\"comparison\":{\"bootstrap\":\"STATIONARY_POLITIS_ROMANO_1994\",\"confidence\":\"0.95\",\"day\":\"UTC\",\"gap_day\":\"EITHER_ACCOUNT_WITHOUT_A_VALID_VALUE_AT_A_MIDNIGHT_A_GAP_OVER_65_MIN_OR_AN_INVALID_ONE\",\"mean_block_days\":3,\"minimum\":{\"paired_days\":30,\"trader_closed_trades\":60},\"resamples\":2000,\"seed\":\"THE_SET'S_HASH_THE_TWIN'S_AND_THE_RUN'S_IDS\",\"statistic\":\"PAIRED_DAILY_LOG_RETURN_DIFFERENCES_TRADER_NAV_MINUS_TWIN_EQUITY\",\"threshold\":\"NONE_NOTHING_IS_PROMOTED_OR_CHANGED\"},\"cost\":\"FUTURES_COST_V1\",\"funding_filter\":{\"basis\":\"THREE_TIMES_BINANCE'S_DEFAULT_RATE_OF_0.01%\",\"max_abs_rate\":\"0.0003\",\"rate\":\"THE_MARK'S_ANNOUNCED_FUNDING_RATE\",\"refuse\":\"AN_ENTRY_ON_THE_PAYING_SIDE_WHILE_THE_RATE'S_MAGNITUDE_IS_ABOVE_THE_MAX\"},\"gate\":{\"distance\":\"THE_PLANNED_ENTRY_FILL_TO_THE_ROUNDED_STOP\",\"multiple\":\"3\",\"price\":\"THE_PLANNED_ENTRY_FILL\",\"refuse\":\"THE_STOP'S_DISTANCE_PER_UNIT_BELOW_MULTIPLE_X_THE_ROUND_TRIP_COST_PER_UNIT\",\"round_trip_cost_per_unit\":\"2_X_TAKER_X_PRICE_PLUS_2_X_SLIPPAGE_X_PRICE_PLUS_THE_QUOTE'S_SPREAD\"},\"id\":\"TWIN_SET_V3\",\"kind\":\"FUTURES_TWINS\",\"label\":\"ISOLATED_PAPER_ACCOUNTS_NOT_THE_OWNER'S_ACCOUNT\",\"ledger\":\"THEIR_OWN_ROWS_NO_JOURNAL_NO_RESERVATION_NO_ACCOUNT_STATE\",\"momentum\":{\"acts\":\"FLAT_ENTERS_THE_SIGNAL'S_SIDE_THE_OTHER_SIDE_FLIPS_THE_SAME_SIDE_HOLDS\",\"after_liquidation\":\"THE_NEXT_UTC_DAY'S_SIGNAL\",\"candles\":\"COMPLETE_UTC_DAYS_EACH_24_COMPLETE_1H_CANDLES_BUILT_FROM_FINAL_1M_CANDLES\",\"day_spent\":\"BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_COMPLETE_YET_OR_AN_OPERATIONAL_REFUSAL_TRIES_AGAIN_AT_THE_DAY'S_NEXT_BAR\",\"evaluated\":\"AT_THE_FIRST_FINISHED_15M_BAR_OF_EACH_UTC_DAY_THE_TWIN_READS_FROM_THE_DAY_AFTER_IT_STARTED\",\"exit\":\"ONLY_ON_A_FLIP_OR_A_LIQUIDATION\",\"flip\":\"THE_EXIT_ON_THE_BOOK_THEN_THE_ENTRY_ON_THE_LEVELS_THE_EXIT_LEFT\",\"leverage\":\"1\",\"limits\":\"NONE\",\"lookback_days\":8,\"signal\":\"LONG_IF_THE_LAST_COMPLETE_UTC_DAY'S_CLOSE_IS_ABOVE_THE_CLOSE_OF_THE_DAY_8_DAYS_BEFORE_IT_SHORT_IF_BELOW_NO_CHANGE_IF_EQUAL\",\"warmup\":\"BOTH_DAYS_COMPLETE_ELSE_READ_AGAIN_AT_THE_DAY'S_NEXT_BAR\"},\"placebo\":{\"arms\":{\"RANDOM\":\"EACH_ANSWERED_CANDIDATE_DRAWN_AT_THE_AGENT'S_OWN_GO_HALVE_VETO_RATES_NO_ANSWER_STAYS_GO\",\"TREND_ARM\":\"EVERY_CANDIDATE_GO\",\"VETO_ARM\":\"THE_AGENT'S_VERDICTS\"},\"candidates\":\"EVERY_TREND_VETO_CANDIDATE_ASKED_WHOSE_24H_HAS_PASSED\",\"minimum_candidates\":60,\"model\":\"1M_CANDLES: THE_ENTRY_AT_THE_PLANNED_PRICE_AT_THE_ASKED_QUOTE; THE_STOP_ON_THE_CANDLES_AT_ITS_LEVEL_OR_A_GAPPED_OPEN_WITH_THE_SLIPPAGE_AGAINST_IT; THE_OPPOSITE_RELATION_OF_THE_1H_EMAS_AT_THE_NEXT_HOUR'S_OPEN; THE_24H_TIME_EXIT; BOTH_TAKER_FEES; THE_SETTLED_FUNDING_CROSSED\",\"seed\":\"THE_SET'S_HASH_THE_TWIN'S_ID_AND_THE_NEWEST_CANDIDATE\",\"streams\":1000,\"success\":\"THE_VETO_ARM_BEATS_95%_OF_THE_STREAMS_AND_THE_PAIRED_DAILY_INTERVAL_OF_TREND_VETO_MINUS_TREND_IS_ABOVE_ZERO\",\"threshold\":\"NONE_NOTHING_IS_PROMOTED_OR_CHANGED\",\"unit\":\"R_THE_NET_OVER_THE_FULL_RISK_ENTRY'S_LOSS_AT_THE_STOP_WITH_BOTH_FEES_AND_SLIPPAGE\",\"weights\":{\"GO\":\"1\",\"HALVE\":\"0.5\",\"NO_ANSWER\":\"1\",\"VETO\":\"0\"},\"when\":\"ONCE_A_UTC_DAY_FROM_00:40\"},\"policy\":\"FUTURES_POLICY_V1\",\"protection\":\"EVERY_SECOND_AFTER_THE_OWNER'S_STEP_LIQUIDATION_STOP_TIME_EXIT_WHATEVER_THE_AGENTS_OR_THE_RUN\",\"shared\":\"THE_POLICY'S_SIZING_COOLDOWNS_ENTRIES_PER_UTC_DAY_AND_LATCHES_AND_THE_COST'S_FILLS_FEES_FUNDING_AND_LIQUIDATION_ON_THE_SAME_QUOTES_AND_MARKS\",\"slow_trend\":{\"acts\":\"WHEN_THE_TARGET_IS_MORE_THAN_THE_BUFFER_FROM_HELD: THE_EXIT_ON_THE_BOOK_THEN_THE_TARGET'S_ENTRY_ON_THE_LEVELS_THE_EXIT_LEFT_WHEN_IT_TOOK_THE_SAME_SIDE_OF_THE_BOOK; ELSE_NO_CHANGE; AN_ENTRY_REFUSED_AFTER_ITS_EXIT_FILLED_IS_OWED_AT_THE_DAY'S_NEXT_BARS\",\"after_liquidation\":\"THE_NEXT_UTC_DAY'S_READING\",\"anchor\":\"THE_NEAREST_STORED_DAY_AT_OR_BEFORE_THE_LOOKBACK'S_DAY_WITHIN_THE_TOLERANCE_ELSE_NOT_READABLE\",\"anchor_tolerance_days\":7,\"annualization_days\":365,\"candles\":\"BINANCE'S_FINAL_1D_CANDLES_OF_THE_PERPETUAL_STORED_BY_THE_FEED_EACH_UTC_DAY'S_CLOSE\",\"day\":\"THE_LAST_COMPLETE_UTC_DAY_BEFORE_THE_BAR'S_DAY\",\"day_spent\":\"BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_READABLE_YET_OR_AN_OPERATIONAL_REFUSAL_TRIES_AGAIN_AT_THE_DAY'S_NEXT_BAR\",\"evaluated\":\"AT_THE_FIRST_FINISHED_15M_BAR_OF_EACH_UTC_DAY_THE_TWIN_READS_FROM_THE_DAY_AFTER_IT_STARTED\",\"exit\":\"ONLY_ON_A_RESIZE_A_FLIP_AN_EXIT_TO_FLAT_OR_A_LIQUIDATION\",\"flat_band\":\"0.05\",\"gap_return\":\"A_RETURN_ACROSS_MISSING_DAYS_COUNTS_ONCE\",\"held\":\"THE_OPEN_POSITION'S_NOTIONAL_AT_THE_FRESH_MARK_OVER_EQUITY_SIGNED_BY_ITS_SIDE_ZERO_WHEN_FLAT\",\"leverage\":\"1_WHEN_THE_TARGET'S_MAGNITUDE_IS_AT_MOST_1_ELSE_2\",\"leverage_cap\":\"2\",\"limits\":\"NONE\",\"lookback_days\":[30,91,365],\"minimum_days_stored\":300,\"rebalance_buffer\":\"0.25\",\"resize\":\"THE_WHOLE_POSITION_EXITS_AND_THE_TARGET_ENTERS_WHOLE_EACH_WITH_ITS_TAKER_FEE: A_TWIN_HOLDS_ONE_POSITION_AND_NEVER_CHANGES_ONE_IN_PART\",\"signal\":\"THE_MEAN_OF_THE_SIGNS_OF_THE_DAY'S_CLOSE_AGAINST_THE_CLOSE_EACH_LOOKBACK_BEFORE_IT_A_SIGN_IS_0_WHEN_EQUAL\",\"sources\":[\"TR-01\",\"TR-03\"],\"target\":\"SIGNAL_X_MIN(LEVERAGE_CAP, VOLATILITY_TARGET_/_VOLATILITY)_QUANTIZED_TOWARD_ZERO_TO_THE_STEP\",\"target_step\":\"0.01\",\"volatility\":\"THE_ANNUALIZED_EXPONENTIALLY_WEIGHTED_STANDARD_DEVIATION_OF_THE_DAILY_LOG_RETURNS_OF_THE_STORED_DAYS_FROM_THE_DAY_365_DAYS_BEFORE_TO_THE_DAY\",\"volatility_centre_of_mass_days\":60,\"volatility_days\":365,\"volatility_recursion\":\"VAR_NEXT_=_(60_X_VAR_+_RETURN_SQUARED)_/_61_SEEDED_WITH_THE_FIRST_RETURN_SQUARED\",\"volatility_target\":\"0.40\"},\"source\":\"ExecPlan 0057 section 4.1, approved by the owner on 2026-11-07\",\"start_equity\":\"10000\",\"status\":\"PROPOSED\",\"step_errors\":{\"fault_after\":60,\"other\":\"FAULTS_THAT_TWIN_ALONE\",\"retried\":\"A_DATABASE_TIMEOUT_A_LOCK_WAIT_OR_A_DEADLOCK_THE_NEXT_SECOND\"},\"trend\":{\"atr\":\"THE_POLICY'S_15M_WILDER_ATR\",\"bar_max_age_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"candles\":\"COMPLETE_1H_CANDLES_BUILT_FROM_FINAL_1M_CANDLES_THE_NEWEST_CONTIGUOUS_RUN\",\"drawdown\":\"LATCHED_THEN_STOPPED_ONCE_FLAT_THE_SEGMENT_ENDS\",\"ema_seed\":\"SMA_OF_FIRST_COMPLETE_PERIOD\",\"evaluated\":\"ONCE_AT_EACH_FINISHED_15M_BAR_AFTER_ITS_LAST_MINUTE_IS_FINAL_OR_60_S\",\"exit\":\"AT_A_FINISHED_15M_BAR_WHEN_THE_HOUR_THAT_FINISHED_LAST_HAS_THE_FAST_EMA_AGAINST_THE_SIDE\",\"fast_ema\":20,\"interval_ms\":3600000,\"leverage\":\"1\",\"limits\":\"THE_POLICY'S_COOLDOWNS_ENTRIES_PER_UTC_DAY_DAILY_LOSS_AND_DRAWDOWN\",\"long_cross\":\"PREV_FAST_LTE_SLOW_AND_CUR_FAST_GT_SLOW\",\"max_hold_hours\":24,\"risk_fraction\":\"THE_POLICY'S\",\"run_window_max_hours\":720,\"short_cross\":\"PREV_FAST_GTE_SLOW_AND_CUR_FAST_LT_SLOW\",\"signal\":\"A_CROSS_ON_THE_HOUR_THAT_FINISHED_LAST_LIVE_AT_EACH_15M_BAR_OF_THE_NEXT_HOUR\",\"signal_spent\":\"BY_A_FILL_OR_A_REFUSAL_OF_THE_GATE_OR_THE_FUNDING_FILTER\",\"slow_ema\":50,\"stop_atr_multiple\":\"2.0\",\"take_profit\":null,\"warmup_hours\":100},\"twins\":[{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"HOLD\",\"latches\":\"NONE\",\"leverage\":\"1\",\"max_hold_hours\":null,\"reentry\":\"NEVER\",\"rule\":\"LONG_ONCE_AT_THE_FIRST_FINISHED_15M_BAR_THEN_HOLD\",\"size\":\"THE_WHOLE_WALLET_LESS_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE\",\"stop\":null,\"take_profit\":null},{\"funding_filter\":false,\"gate\":false,\"id\":\"TREND\",\"rule\":\"EMA_CROSS_1H\"},{\"funding_filter\":true,\"gate\":true,\"id\":\"TREND_GATED\",\"rule\":\"EMA_CROSS_1H\"},{\"entry\":\"EACH_ENTRY_PASSES_THE_VETO_AGENT_FIRST\",\"funding_filter\":false,\"gate\":false,\"id\":\"TREND_VETO\",\"rule\":\"EMA_CROSS_1H\"},{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"MOMENTUM_1W\",\"latches\":\"NONE\",\"leverage\":\"1\",\"max_hold_hours\":null,\"rule\":\"DAY_MOMENTUM\",\"size\":\"THE_WHOLE_WALLET_LESS_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE\",\"stop\":null,\"take_profit\":null},{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"TREND_SLOW\",\"latches\":\"NONE\",\"leverage\":\"1_WHEN_THE_TARGET_IS_AT_MOST_1_ELSE_2\",\"max_hold_hours\":null,\"rule\":\"SLOW_TREND\",\"size\":\"THE_TARGET_FRACTION_OF_EQUITY_AS_NOTIONAL_ITS_MARGIN_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE_WITHIN_THE_FREE_WALLET\",\"stop\":null,\"take_profit\":null}],\"valuation\":\"CASH_PLUS_THE_OPEN_POSITION'S_UNREALIZED_PNL_AT_THE_MARK_LESS_SETTLED_FUNDING_WAITING_FOR_THE_FREE_WALLET\",\"version\":3,\"veto\":{\"agent\":\"ENTRY_VETO_V1\",\"asked\":\"WHEN_THE_RULE'S_ENTRY_PASSES_EVERY_CHECK_AND_IS_SIZED_THE_TWIN_HOLDS_IT_AND_ASKS\",\"cost_of_asking\":\"THE_FILL_PRICE_AGAINST_THE_PRICE_PLANNED_AT_THE_ASKED_QUOTE\",\"deadline_seconds\":120,\"fill\":\"AT_THE_NEWEST_QUOTE_AFTER_THE_ANSWER_CHECKED_AND_SIZED_AGAIN_AT_MOST_THE_POLICY'S_DECISION_AGE_AFTER_THE_BAR\",\"open_at_once\":1,\"per_utc_day\":24,\"quiet_window\":\"NONE\",\"reason_none\":\"EXACTLY_WITH_GO\",\"reasons\":[\"RELEASE_WITHIN_2H\",\"FUNDING_EXTREME\",\"SPREAD_WIDE\",\"FEED_GAP\",\"HEADLINES_CONTRADICT\",\"TREND_WEAK\",\"NONE\"],\"shown\":\"THE_TRADER'S_MARKET_FEATURES_CANDLES_HEADLINES_AND_RELEASES_THE_TWIN'S_ACCOUNT_AND_THE_CANDIDATE\",\"silence\":\"NO_ANSWER_BY_THE_DEADLINE_IS_GO_RECORDED_NO_ANSWER\",\"slot\":\"AFTER_THE_TRADER: NOT_WHILE_A_TRADER_DECISION_IS_DUE_QUEUED_OR_OPEN; A_DECISION_QUEUED_MEANWHILE_CANCELS_THE_CALL\",\"started_by\":\"SYSTEM\",\"twin\":\"TREND_VETO\",\"verdicts\":{\"GO\":\"THE_RULE'S_ENTRY\",\"HALVE\":\"THE_ENTRY_AT_HALF_THE_POLICY'S_RISK_FRACTION\",\"VETO\":\"NO_ENTRY_THE_HOUR'S_CROSS_IS_SPENT\"}},\"wallet_check\":{\"every_seconds\":3600,\"fault\":\"STOPS_THAT_TWIN_ALONE\",\"formula\":\"START_PLUS_REALIZED_PNL_MINUS_FEES_PLUS_FUNDING_RESERVED_THE_OPEN_MARGIN\"}}", "3168e6a71e4eba0e3b69bb1e96ab9dd7a1d4da6dd8d90e1aeb3030a8a23e3e89"]
"""

TABLES_SQL = """
CREATE TABLE perp_daily_bars (
    open_ms bigint PRIMARY KEY CHECK (open_ms >= 0 AND open_ms % 86400000 = 0),
    open numeric(38,8) NOT NULL CHECK (open > 0),
    high numeric(38,8) NOT NULL,
    low numeric(38,8) NOT NULL CHECK (low > 0),
    close numeric(38,8) NOT NULL CHECK (close > 0),
    volume numeric NOT NULL CHECK (volume >= 0),
    quote_volume numeric NOT NULL CHECK (quote_volume >= 0),
    trades integer NOT NULL CHECK (trades >= 0),
    source varchar(8) NOT NULL CHECK (source IN ('REST')),
    received_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT perp_daily_bar_range CHECK (high >= greatest(open, close) AND low <= least(open, close))
);
CREATE TRIGGER perp_daily_bars_append_only BEFORE UPDATE OR DELETE ON perp_daily_bars
    FOR EACH ROW EXECUTE FUNCTION asl_perp_append_only();
GRANT SELECT, INSERT ON perp_daily_bars TO asl_market_worker;
GRANT SELECT ON perp_daily_bars TO asl_api, asl_execution;
"""
DAILY_CODES = ("DAILY_STORED", "DAILY_FAILED")  # the feed's notes of its daily job (app.perp.feed)
FEED_VIEW = """
CREATE OR REPLACE VIEW agent_read.futures_feed_events WITH (security_barrier = true) AS
    SELECT code, at FROM perp_feed_events{where};
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
    return _frozen(TWIN_SEED_LINES_V3, ("FUTURES_TWINS",), "twin set")


def _checks(twins, rules):
    op.execute("ALTER TABLE futures_twins DROP CONSTRAINT futures_twins_twin_check, "
               f"ADD CONSTRAINT futures_twins_twin_check CHECK (twin IN {_quoted(twins)})")
    op.execute("ALTER TABLE futures_twin_candidates DROP CONSTRAINT futures_twin_candidates_rule_check, "
               f"ADD CONSTRAINT futures_twin_candidates_rule_check CHECK (rule IN {_quoted(rules)})")
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
    _checks((*TWINS_V2, *TWINS_ADDED), (*RULES_V2, *RULES_ADDED))
    op.execute(TABLES_SQL)
    op.execute(FEED_VIEW.format(where=f" WHERE code NOT IN {_quoted(DAILY_CODES)}"))


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    records = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_twins WHERE twin = 'TREND_SLOW') "
        "+ (SELECT count(*) FROM futures_twin_candidates WHERE rule = 'SLOW_TREND') "
        "+ (SELECT count(*) FROM perp_daily_bars)").scalar_one()
    if records:
        raise RuntimeError("slow trend records exist; downgrade refused; fix forward")
    op.execute(FEED_VIEW.format(where=""))
    op.execute("DROP TABLE perp_daily_bars")
    _checks(TWINS_V2, RULES_V2)
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen row, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in twin_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("twin set definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
