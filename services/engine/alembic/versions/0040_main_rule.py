"""ExecPlan 0059: the slow rule trades the main account (``FUTURES_POLICY_V2`` and ``MAIN_RULE_V1``).

Revision ID: 0040_main_rule
Revises: 0039_event_calendar

ExecPlan 0059 sections 4.1 to 4.4. Nothing of the journal, the reservations, the twins, the backtests' records, the
trader's records or an existing position changes; every row written so far keeps every check it had.

- ``MAIN_RULE_V1`` (a new definition kind, ``MAIN_RULE``) and ``FUTURES_POLICY_V2`` in ``execution_definitions``
  (frozen here, checked against the code): the futures engine starts only when the stored rows equal its code.
- ``futures_positions``: ``opened_by`` (``AGENT`` for every row so far, or ``RULE``) and ``reading_id``. An agent's
  position keeps every term it had to have (its decision, ATR, stop, stop multiple, maximum hold and time exit); a rule's
  position is a long at 1x with its reading and none of those (``futures_position_opener``). Its close reasons add
  ``RULE_RESIZE`` and ``RULE_EXIT``, which only a rule's position takes (the money-path review); a fill's reasons add
  ``RULE_ENTRY`` too.
- ``futures_runs.stop_reason`` adds ``NEW_POLICY``: the run ``SYSTEM`` ends when it starts the next under the policy
  in force (the switch, ExecPlan 0059 section 4.4).
- ``futures_rule_readings``: the rule's readings, append-only, at most one that acted per run and UTC day, readable
  by the execution identity (which writes them) and the API; no agent reads them.
- ``backtest_runs.code`` adds ``TRADER_REPLACED``: the AI trader's backtest that is still running when the rule
  replaces the trader ends with it (the owner's 2026-11-10 "can everything stop").

Downgrade is refused once a rule reading, a rule position, a run under ``FUTURES_POLICY_V2``, a run stopped
``NEW_POLICY`` or a backtest stopped ``TRADER_REPLACED`` exists: a rollback goes forward (plan section 11).
"""

import hashlib
import json

from alembic import op

revision = "0040_main_rule"
down_revision = "0039_event_calendar"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET", "FUTURES_POLICY", "FUTURES_COST", "FUTURES_TWINS",
                    "FUTURES_SCORING", "FUTURES_CHECKS")
KIND_ADDED = ("MAIN_RULE",)
CLOSE_REASONS = ("STOP", "TAKE_PROFIT", "TIME", "LIQUIDATION", "AGENT_EXIT", "OWNER_STOP")
FILL_REASONS = ("AGENT_ENTRY", *CLOSE_REASONS)
RULE_CLOSES = ("RULE_RESIZE", "RULE_EXIT")
STOP_REASONS = ("OWNER", "DRAWDOWN")
STOP_ADDED = ("NEW_POLICY",)
RUNS = ("BACKTEST_AI_V1:TWO_MONTHS", "BACKTEST_AI_V1:TWO_MONTHS_CLAUDE", "BACKTEST_GEN14_V1:TWO_MONTHS_CLAUDE")
CODES = ("ARCHIVE_MISMATCH", "STATE_MISMATCH", "PROTOCOL", "CALLS_TOTAL_REACHED", "SPEND_CAP_REACHED")
CODES_ADDED = ("TRADER_REPLACED",)
# An agent's position keeps 0020's terms; these become NULL for a rule's.
AGENT_TERMS = ("decision_id", "atr", "stop_multiple", "max_hold_hours", "initial_stop", "stop_price", "time_exit_at")

# The frozen definitions: ``python -m app.futures.definitions v2`` prints them; tests/test_m11_main_rule_unit.py checks.
MAIN_SEED_LINES = r"""
["MAIN_RULE_V1", "MAIN_RULE", 1, "PROPOSED", "{\"account\":\"THE_MAIN_FUTURES_ACCOUNT\",\"acts\":\"WHEN_THE_TARGET_IS_MORE_THAN_THE_BUFFER_FROM_HELD: THE_POSITION_EXITS_WHOLE_ON_THE_BOOK_THEN_THE_TARGET_ENTERS_WHOLE_IN_THE_SAME_STEP; ELSE_NO_CHANGE\",\"anchor\":\"THE_NEAREST_STORED_DAY_AT_OR_BEFORE_THE_LOOKBACK'S_DAY_WITHIN_THE_TOLERANCE_ELSE_NOT_READABLE\",\"anchor_tolerance_days\":7,\"annualization_days\":365,\"bar_wait_seconds\":60,\"candles\":\"BINANCE'S_FINAL_1D_CANDLES_OF_THE_PERPETUAL_STORED_BY_THE_FEED_EACH_UTC_DAY'S_CLOSE\",\"day\":\"THE_LAST_COMPLETE_UTC_DAY_BEFORE_THE_BAR'S_DAY\",\"day_spent\":\"BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_READABLE_YET_OR_A_REFUSAL_TRIES_AGAIN_AT_THE_DAY'S_NEXT_BAR\",\"decider\":\"CODE_NO_MODEL\",\"direction\":\"MAX(SIGNAL,_0): NEVER_SHORT\",\"entry_owed\":\"AN_ENTRY_REFUSED_AFTER_ITS_EXIT_FILLED_IS_ENTERED_AT_THE_DAY'S_NEXT_BARS_ALTHOUGH_INSIDE_THE_BUFFER\",\"evaluated\":\"AT_A_FINISHED_15M_BAR_ONCE_ITS_LAST_1M_CANDLE_IS_FINAL_OR_60_S_HAVE_PASSED_WITHIN_THE_POLICY'S_DECISION_MAX_AGE; THE_FIRST_SUCH_BAR_OF_EACH_UTC_DAY_FROM_THE_RUN'S_START\",\"exit_unfilled\":\"THE_DAY'S_NEXT_BAR_READS_AGAIN_AND_TRIES_THE_WHOLE_RESIZE_AGAIN\",\"exits\":\"THE_RULE'S_RESIZE_OR_EXIT_A_STOPPING_RUN'S_WHOLE_EXIT_AT_ONCE_THE_OWNER'S_STOP_AND_CLOSE_OR_A_LIQUIDATION\",\"flat\":\"A_TARGET_BELOW_THE_FLAT_BAND_IS_0; A_TARGET_WHOSE_NOTIONAL_IS_BELOW_THE_INSTRUMENT'S_MINIMUM_IS_REFUSED\",\"flat_band\":\"0.01\",\"gap_return\":\"A_RETURN_ACROSS_MISSING_DAYS_COUNTS_ONCE\",\"held\":\"THE_OPEN_POSITION'S_NOTIONAL_AT_THE_FRESH_MARK_OVER_EQUITY_ZERO_WHEN_FLAT\",\"id\":\"MAIN_RULE_V1\",\"instrument\":\"BTCUSDT_PERPETUAL_SIMULATED\",\"kind\":\"MAIN_RULE\",\"leverage\":\"1\",\"leverage_cap\":\"1\",\"lookback_days\":[30,91,365],\"minimum_days_stored\":300,\"position\":{\"max_hold_hours\":null,\"risk\":\"THE_NOTIONAL\",\"risk_cap\":\"THE_TARGET_X_EQUITY\",\"side\":\"LONG\",\"stop\":null,\"take_profit\":null,\"time_exit\":null},\"readings\":\"ONE_FUTURES_RULE_READINGS_ROW_PER_DAY_ACTED_ON; A_DAY_NOT_READABLE_OR_REFUSED_ONCE_A_DAY_PER_REASON\",\"rebalance_buffer\":\"0.03\",\"refused_entry\":\"A_LATCH_A_PAUSED_OR_STOPPING_RUN_AN_INTEGRITY_HOLD_A_STALE_QUOTE_OR_MARK_A_THIN_BOOK_OR_AN_UNUSABLE_INSTRUMENT: NO_ENTRY_AND_NO_INCREASE; AN_EXIT_OR_A_DECREASE_STILL_EXITS\",\"resize\":\"A_WHOLE_EXIT_AND_A_WHOLE_ENTRY_EACH_WITH_ITS_TAKER_FEE; NEVER_A_PART\",\"signal\":\"THE_MEAN_OF_THE_SIGNS_OF_THE_DAY'S_CLOSE_AGAINST_THE_CLOSE_EACH_LOOKBACK_BEFORE_IT_A_SIGN_IS_0_WHEN_EQUAL\",\"size\":\"THE_TARGET_FRACTION_OF_EQUITY_AS_NOTIONAL_AT_1X_ITS_MARGIN_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE_WITHIN_THE_FREE_WALLET\",\"size_chosen_by\":\"THE_LARGEST_OF_40_30_20_15_10_5%_A_YEAR_WHOSE_WORST_FALL_FROM_THE_HIGH_WATER_NAV_ON_DAILY_LOWS_2021_01_01_TO_2026_10_31_STAYS_AT_OR_BELOW_4%_HALF_THE_DRAWDOWN_STOP; WRITTEN_BEFORE_THE_SIZING_RUN\",\"source\":\"ExecPlan 0059 sections 4.1 and 4.2, approved by the owner on 2026-11-10\",\"sources\":[\"TR-01\",\"TR-03\",\"TR-10\",\"TR-12\"],\"status\":\"PROPOSED\",\"target\":\"MAX(SIGNAL,_0)_X_MIN(LEVERAGE_CAP,_VOLATILITY_TARGET_/_VOLATILITY)_QUANTIZED_TOWARD_ZERO_TO_THE_STEP\",\"target_step\":\"0.001\",\"version\":1,\"volatility\":\"THE_ANNUALIZED_EXPONENTIALLY_WEIGHTED_STANDARD_DEVIATION_OF_THE_DAILY_LOG_RETURNS_OF_THE_STORED_DAYS_FROM_THE_DAY_365_DAYS_BEFORE_TO_THE_DAY\",\"volatility_centre_of_mass_days\":60,\"volatility_days\":365,\"volatility_recursion\":\"VAR_NEXT_=_(60_X_VAR_+_RETURN_SQUARED)_/_61_SEEDED_WITH_THE_FIRST_RETURN_SQUARED\",\"volatility_target\":\"0.05\"}", "60f3d58e0fc4be81fb87f1a518d16ebe4deeeebd7af2342fe96df0c8dab8bf72"]
["FUTURES_POLICY_V2", "FUTURES_POLICY", 2, "PROPOSED", "{\"actions\":[\"RULE_ENTRY\",\"RULE_RESIZE\",\"RULE_EXIT\"],\"agent_decisions\":\"NONE_ASKED; EVERY_ONE_IS_REFUSED_POLICY_CHANGED_WHATEVER_ITS_POLICY_TAG\",\"agent_terms\":\"V1'S_STOP_TAKE_PROFIT_HOLD_COOLDOWN_AND_DECISION_VALUES_ARE_KEPT_FOR_A_POSITION_OPENED_UNDER_V1\",\"atr\":{\"candles\":\"COMPLETE_15M_CANDLES_BUILT_FROM_FINAL_1M_CANDLES_THE_NEWEST_CONTIGUOUS_RUN\",\"interval_ms\":900000,\"method\":\"WILDER\",\"period\":14,\"window_candles\":96},\"cooldown_bars\":{\"after_other_exit\":1,\"after_stop\":2},\"cost\":\"FUTURES_COST_V1\",\"daily_loss_fraction\":\"0.02\",\"daily_reference\":{\"late_rule\":\"MAX_OF_LAST_VALID_NAV_PRIOR_24H_AND_FIRST_POST_MIDNIGHT_NAV\",\"timeliness_ms\":300000,\"timezone\":\"UTC\"},\"decided_by\":\"SYSTEM_CODE_NO_MODEL\",\"decider\":\"MAIN_RULE_V1\",\"decision_max_age_seconds\":300,\"decision_schedule\":{\"after_fill\":true,\"bar_ms\":900000,\"max_open\":1,\"quiet_window\":null,\"sharp_move_atr\":\"1.5\",\"sharp_move_window_seconds\":300},\"decisions_per_utc_day\":120,\"drawdown_fraction\":\"0.08\",\"drawdown_measure\":\"THE_RUN'S_OWN_HIGH_WATER_NAV\",\"entries_per_utc_day\":24,\"funding_reserve\":{\"fraction_of_notional\":\"0.01\",\"kept\":\"THE_FREE_WALLET_AFTER_AN_ENTRY_COVERS_THE_EXIT_FEE_AND_THIS\",\"label\":\"THE_APP'S_OWN_BUFFER_NOT_A_PROVIDER_VALUE\"},\"id\":\"FUTURES_POLICY_V2\",\"instrument\":\"BTCUSDT_PERPETUAL_SIMULATED\",\"kind\":\"FUTURES_POLICY\",\"latch_effect\":\"NO_ENTRIES_EXITS_AND_PROTECTION_CONTINUE\",\"leverage_cap\":\"1\",\"leverage_choices\":[\"1\"],\"liquidation_buffer\":\"3\",\"liquidation_rule\":\"THE_STOP_WITHIN_THE_FIRST_THIRD_OF_THE_WAY_TO_LIQUIDATION\",\"margin_mode\":\"ISOLATED\",\"max_hold_hours\":[1,4,12,24],\"no_agent\":\"NO_NEW_ENTRY_THE_POSITION_STAYS_PROTECTED_BY_CODE\",\"notional_cap\":\"LEVERAGE_X_EQUITY\",\"position_mode\":\"ONE_WAY\",\"positions\":1,\"replaces\":\"FUTURES_POLICY_V1\",\"reversal\":\"EXIT_THEN_THE_NEXT_DECISION\",\"risk_fraction\":\"0.0025\",\"risk_includes\":\"BOTH_TAKER_FEES_AND_THE_SLIPPAGE_SCENARIO\",\"rule_position\":{\"max_hold_hours\":null,\"opened_by\":\"RULE\",\"protection\":\"ITS_SIZE_THE_LATCHES_A_STOPPING_RUN'S_WHOLE_EXIT_AT_ONCE_LIQUIDATION_AND_THE_OWNER'S_STOP_AND_CLOSE\",\"risk\":\"THE_NOTIONAL\",\"risk_cap\":\"THE_TARGET_X_EQUITY\",\"stop\":null,\"take_profit\":null,\"time_exit\":null},\"sides\":[\"LONG\"],\"source\":\"ExecPlan 0059 section 4.3, approved by the owner on 2026-11-10\",\"status\":\"PROPOSED\",\"stop_multiples\":[\"1.0\",\"1.5\",\"2.0\",\"3.0\"],\"stop_rounding\":\"TO_THE_TICK_AWAY_FROM_THE_ENTRY\",\"switch\":{\"by\":\"SYSTEM\",\"ends\":\"THE_RUN_UNDER_AN_EARLIER_POLICY_STOPPED_NEW_POLICY\",\"open_position\":\"KEEPS_ITS_STOP_TAKE_PROFIT_AND_TIME_EXIT_AND_CLOSES_BY_THEM_NO_FORCED_EXIT\",\"starts\":\"A_RUN_UNDER_THIS_POLICY_WHOSE_HIGH_WATER_NAV_STARTS_AT_THE_SWITCH\",\"waits\":\"A_CAUSE_OPEN_OR_A_STOPPING_RUN; A_STOPPED_RUN'S_NEXT_IS_THE_OWNER'S\",\"when\":\"THE_FIRST_FINISHED_15M_BAR_THE_RULE_READS_WITH_THE_ACCOUNT_FLAT_AND_THE_RUN_RUNNING_WITHOUT_A_CAUSE\"},\"take_profit_multiples\":[\"1\",\"1.5\",\"2\",\"3\"],\"take_profit_rounding\":\"TO_THE_TICK_TOWARD_THE_ENTRY\",\"tighten\":\"THE_SAME_MULTIPLES_FROM_THE_EXIT_SIDE_PRICE_ONLY_IF_TIGHTER\",\"valuation_seconds\":60,\"version\":2}", "08a6bd62cf64ca899917507e9d99e7c11dae50fc3c58c2674b42bb7e07eb6728"]
"""

READINGS_SQL = """
CREATE TABLE futures_rule_readings (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    run_id uuid NOT NULL REFERENCES futures_runs(id),
    utc_date date NOT NULL,
    bar_open_ms bigint NOT NULL CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    at timestamptz NOT NULL,
    rule_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    rule_sha256 varchar(64) NOT NULL CHECK (rule_sha256 ~ '^[0-9a-f]{64}$'),
    result varchar(6) NOT NULL CHECK (result IN ('LONG','FLAT','WARMUP')),
    reason varchar(32),
    signal numeric CHECK (signal >= -1 AND signal <= 1),
    volatility numeric CHECK (volatility >= 0),
    target numeric CHECK (target >= 0 AND target <= 1),
    held numeric CHECK (held >= 0),
    action varchar(9) CHECK (action IN ('RESIZE','NO_CHANGE')),
    outcome varchar(12) NOT NULL CHECK (outcome IN ('NOT_READABLE','NO_CHANGE','FILLED','REFUSED','OWED')),
    codes text[] NOT NULL DEFAULT '{}',
    spent boolean NOT NULL,
    exit_fill_id uuid UNIQUE REFERENCES futures_fills(id),
    features jsonb NOT NULL CHECK (jsonb_typeof(features) = 'object'),
    detail jsonb NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(detail) = 'object'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_rule_reading_shape CHECK (CASE outcome
        WHEN 'NOT_READABLE' THEN result = 'WARMUP' AND NOT spent AND action IS NULL AND exit_fill_id IS NULL
        WHEN 'NO_CHANGE' THEN result <> 'WARMUP' AND spent AND action = 'NO_CHANGE' AND exit_fill_id IS NULL
            AND cardinality(codes) = 0
        WHEN 'FILLED' THEN result <> 'WARMUP' AND spent AND action = 'RESIZE' AND cardinality(codes) = 0
        WHEN 'REFUSED' THEN result <> 'WARMUP' AND NOT spent AND action IS NOT NULL AND exit_fill_id IS NULL
            AND cardinality(codes) > 0
        ELSE result = 'LONG' AND NOT spent AND action = 'RESIZE' AND exit_fill_id IS NOT NULL
            AND cardinality(codes) > 0
        END),
    CONSTRAINT futures_rule_reading_values CHECK (result = 'WARMUP' OR (signal IS NOT NULL
        AND volatility IS NOT NULL AND target IS NOT NULL AND held IS NOT NULL))
);
CREATE UNIQUE INDEX futures_rule_readings_acted ON futures_rule_readings (run_id, utc_date) WHERE spent;
CREATE INDEX futures_rule_readings_run ON futures_rule_readings (run_id, utc_date, seq);
CREATE TRIGGER futures_rule_readings_append_only BEFORE UPDATE OR DELETE ON futures_rule_readings
    FOR EACH ROW EXECUTE FUNCTION asl_futures_append_only();
GRANT SELECT, INSERT ON futures_rule_readings TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE futures_rule_readings_seq_seq TO asl_execution;
GRANT SELECT ON futures_rule_readings TO asl_api;

ALTER TABLE futures_positions
    ADD COLUMN opened_by varchar(5) NOT NULL DEFAULT 'AGENT' CHECK (opened_by IN ('AGENT','RULE')),
    ADD COLUMN reading_id uuid UNIQUE REFERENCES futures_rule_readings(id);
ALTER TABLE futures_positions {nullable};
ALTER TABLE futures_positions ADD CONSTRAINT futures_position_opener CHECK (CASE opened_by
    WHEN 'AGENT' THEN reading_id IS NULL AND decision_id IS NOT NULL AND atr IS NOT NULL AND stop_multiple IS NOT NULL
        AND max_hold_hours IS NOT NULL AND initial_stop IS NOT NULL AND stop_price IS NOT NULL
        AND time_exit_at IS NOT NULL AND (close_reason IS NULL OR close_reason NOT IN ('RULE_RESIZE','RULE_EXIT'))
    ELSE reading_id IS NOT NULL AND decision_id IS NULL AND side = 'LONG' AND leverage = 1 AND atr IS NULL
        AND stop_multiple IS NULL AND take_profit_multiple IS NULL AND max_hold_hours IS NULL AND initial_stop IS NULL
        AND stop_price IS NULL AND take_profit IS NULL AND time_exit_at IS NULL AND risk = notional
        AND close_reason IS DISTINCT FROM 'AGENT_EXIT'
    END);
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def definition_rows():
    """The frozen ``MAIN_RULE_V1`` and ``FUTURES_POLICY_V2``, each checked against its own hash."""
    rows = []
    for line in MAIN_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in ("MAIN_RULE", "FUTURES_POLICY"):
            raise RuntimeError("frozen main rule definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _checks(kinds, closes, fills, stops, codes):
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(kinds)})")
    op.execute("ALTER TABLE futures_positions DROP CONSTRAINT futures_positions_close_reason_check, "
               f"ADD CONSTRAINT futures_positions_close_reason_check CHECK (close_reason IN {_quoted(closes)})")
    op.execute("ALTER TABLE futures_fills DROP CONSTRAINT futures_fills_reason_check, "
               f"ADD CONSTRAINT futures_fills_reason_check CHECK (reason IN {_quoted(fills)})")
    op.execute("ALTER TABLE futures_runs DROP CONSTRAINT futures_runs_stop_reason_check, "
               f"ADD CONSTRAINT futures_runs_stop_reason_check CHECK (stop_reason IN {_quoted(stops)})")
    op.execute("ALTER TABLE backtest_runs DROP CONSTRAINT backtest_runs_code_check, "
               f"ADD CONSTRAINT backtest_runs_code_check CHECK (code IN {_quoted(codes)})")


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    _checks((*DEFINITION_KINDS, *KIND_ADDED), (*CLOSE_REASONS, *RULE_CLOSES), (*FILL_REASONS, "RULE_ENTRY", *RULE_CLOSES),
            (*STOP_REASONS, *STOP_ADDED), (*CODES, *CODES_ADDED))
    for row in definition_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    nullable = ", ".join(f"ALTER COLUMN {column} DROP NOT NULL" for column in AGENT_TERMS)
    op.execute(READINGS_SQL.replace("{nullable}", nullable))


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    held = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_rule_readings) "
        "+ (SELECT count(*) FROM futures_positions WHERE opened_by <> 'AGENT') "
        "+ (SELECT count(*) FROM futures_runs WHERE policy_id = 'FUTURES_POLICY_V2' OR stop_reason = 'NEW_POLICY') "
        "+ (SELECT count(*) FROM backtest_runs WHERE code = 'TRADER_REPLACED')").scalar_one()
    if held:
        raise RuntimeError("main rule records exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE futures_positions DROP CONSTRAINT futures_position_opener")
    op.execute("ALTER TABLE futures_positions "
               + ", ".join(f"ALTER COLUMN {column} SET NOT NULL" for column in AGENT_TERMS))
    op.execute("ALTER TABLE futures_positions DROP COLUMN reading_id, DROP COLUMN opened_by")
    op.execute("DROP TABLE futures_rule_readings")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen rows, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in definition_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("main rule definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    _checks(DEFINITION_KINDS, CLOSE_REASONS, FILL_REASONS, STOP_REASONS, CODES)
