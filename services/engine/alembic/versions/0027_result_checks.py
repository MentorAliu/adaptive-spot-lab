"""ExecPlan 0045: where the results come from (a luck floor, an exit replay, the cost of each trade, the buy/sell split).

Revision ID: 0027_result_checks
Revises: 0026_committed_trader

ExecPlan 0045 sections 4.1 to 4.7. Additive: nothing of the owner's account, its journal, the futures engine, the
twins, the scores or the agents' definitions changes, and no agent reads what this adds. Each guard resolves names
under a fixed search path.

- ``perp_bars.taker_buy_volume``: Binance's taker buy volume of each 1-minute candle (stream ``V``, REST index 9),
  null when the provider's value is missing or out of range and for every candle stored before this migration (a final
  candle never changes). The market worker may update it while a candle is open, as it does the other columns.
  ``agent_read.futures_bars`` shows it as its last column; the trader's context names its columns, so what it reads is
  unchanged.
- ``RESULT_CHECKS_V1`` in ``execution_definitions`` (frozen here, checked against the code), its kind
  ``FUTURES_CHECKS``.
- ``futures_bar_outcomes``: one row per finished 15-minute bar, the modeled outcome of each side and each of the 30
  exits generation 10 allows, built in code by the agent identity (``app.agents.result_checks``) no earlier than the
  1,441 minutes after the bar (an ``INCOMPLETE`` one no earlier than seven days after that). It never changes.
- ``futures_check_results``: the daily results of the four checks (``DONE``, at most one a UTC day) and the failed
  attempts (``FAILED`` with the error's class), written by the agent identity on or after their day. They never change.

Downgrade refuses once a bar outcome or a result exists; otherwise it drops both tables, the view's column, the
column and the definition, and restores the definitions' kind check.
"""

import hashlib
import json

from alembic import op

revision = "0027_result_checks"
down_revision = "0026_committed_trader"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
# The definition kinds as migration 0026 left them, and the one this migration adds.
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET", "FUTURES_POLICY", "FUTURES_COST", "FUTURES_TWINS",
                    "FUTURES_SCORING")
KIND_ADDED = ("FUTURES_CHECKS",)

# The frozen definition: ``python -m app.futures.checks`` prints it; tests/test_m11_checks_db.py checks it.
CHECKS_SEED_LINES = r"""
["RESULT_CHECKS_V1", "FUTURES_CHECKS", 1, "PROPOSED", "{\"bar_outcomes\":{\"atr\":\"THE_TRADER'S_15M_WILDER_ATR_14_AT_THE_BAR_AS_THE_SCORER_READS_IT\",\"bars\":\"EVERY_FINISHED_15M_BAR_SINCE_THE_FIRST_FUTURES_RUN_STARTED_ONCE_THE_1441_MINUTES_AFTER_IT_ARE_FINAL\",\"cost_r\":\"FEES_PLUS_SLIPPAGE_MINUS_FUNDING_RECEIVED_OVER_THAT_RISK\",\"exits\":{\"max_hold_hours\":[4,12,24],\"order\":\"STOP_THEN_TAKE_PROFIT_THEN_HOURS\",\"stop_multiples\":[\"2.0\",\"3.0\"],\"take_profit_multiples\":[null,\"1\",\"1.5\",\"2\",\"3\"]},\"gate\":\"NO_DECISION_QUEUED_OR_OPEN\",\"horizon_minutes\":1441,\"incomplete_after_days\":7,\"left_out\":\"THE_LEVERAGE_CAP_THE_QUANTITY'S_STEP_AND_THE_TICK\",\"model\":\"ONE_UNIT_ENTRY_AT_THE_REFERENCE_WITH_THE_SLIPPAGE_SCENARIO; STOP_AT_MULTIPLE_X_ATR_FROM_THE_ENTRY_FILL; TARGET_AT_ITS_MULTIPLE_OF_THE_STOP'S_DISTANCE; DECISION_SCORING_V1'S_WALK_FROM_THE_NEXT_MINUTE; STOP_FIRST_WHEN_A_MINUTE_TOUCHES_BOTH; A_MINUTE_OPENING_BEYOND_EITHER_FILLS_AT_ITS_OPEN; THE_TIME_EXIT_AT_THE_OPEN_OF_THE_FIRST_MINUTE_AT_OR_AFTER_IT; BOTH_TAKER_FEES; THE_SETTLED_FUNDING_CROSSED\",\"per_pass\":20,\"r\":\"NET_OVER_THE_LOSS_AT_THE_STOP_WITH_BOTH_FEES_AND_SLIPPAGE\",\"r_places\":\"0.0001\",\"reference\":\"THE_BAR'S_LAST_1M_CLOSE\",\"retry_minutes\":5,\"share_places\":\"0.000001\",\"sides\":[\"LONG\",\"SHORT\"],\"taker_buy_share\":\"THE_BAR'S_15_MINUTES'_TAKER_BUY_VOLUME_OVER_THEIR_VOLUME; NULL_WHEN_ANY_LACKS_IT_OR_NO_VOLUME\"},\"buy_sell\":{\"bars\":\"THE_BARS_WITH_A_TAKER_BUY_SHARE\",\"bootstrap\":{\"confidence\":\"0.95\",\"mean_block\":16,\"over\":\"THE_BARS_IN_TIME_ORDER_WITH_THE_THIRDS'_BOUNDS_FIXED\",\"resamples\":2000},\"minimum_days\":30,\"outcome\":\"THE_LONG'S_NET_R_MINUS_THE_SHORT'S\",\"reference_exit\":{\"max_hold_hours\":4,\"stop_multiple\":\"2.0\",\"take_profit_multiple\":\"2\"},\"statistic\":\"TOP_THIRD_MEAN_MINUS_BOTTOM_THIRD_MEAN\",\"thirds\":\"BOTTOM_AT_OR_BELOW_THE_NEAREST_RANK_ONE_THIRD_CUT; TOP_ABOVE_THE_TWO_THIRDS_CUT\"},\"cost\":\"FUTURES_COST_V1\",\"costs\":{\"costs\":\"FEES_PLUS_SLIPPAGE_AGAINST_THE_TOP_OF_THE_BOOK_PLUS_FUNDING_PAID_NET_OF_RECEIVED\",\"planned\":\"TWIN_SET_V1'S_GATE_ROUND_TRIP_WITH_THE_ENTRY'S_SPREAD_FROM_ITS_FACT_SHEET_OVER_RISK_PER_UNIT\",\"r_before_costs\":\"NET_R_PLUS_THE_SHARE\",\"share\":\"COSTS_OVER_THE_RISK_AT_THE_STOP\",\"would_refuse\":\"TWIN_SET_V1'S_GATE_MULTIPLE_3_ON_THE_TRADER'S_ENTRY; A_MEASUREMENT_ONLY\"},\"daily\":{\"from_utc\":\"00:20\",\"gate\":\"NO_DECISION_QUEUED_OR_OPEN\",\"identity\":\"asl_agent\",\"retry_minutes\":15,\"table\":\"futures_check_results\"},\"exit_replay\":{\"bootstrap\":{\"confidence\":\"0.95\",\"mean_block\":5,\"resamples\":2000},\"calibration\":\"THE_FACT_SHEET'S_NET_R_MINUS_THE_CHOSEN_EXIT'S_MODELED_R_FOR_ENTRIES_ENDED_BY_STOP_TAKE_PROFIT_OR_TIME_WITH_NO_EARLY_EXIT_OR_TIGHTENING\",\"check\":\"THE_PICK'S_MEAN_DELTA_OVER_THE_LATER_ENTRIES\",\"check_minimum_entries\":30,\"delta\":\"AN_EXIT'S_NET_R_MINUS_THE_CHOSEN_EXIT'S_ON_THE_SAME_ENTRY\",\"early_exits\":\"DECISION_SCORING_V1'S_1440_MINUTE_SCORES_OF_THE_WINDOW'S_APPLIED_EXITS_AND_TIGHTENINGS; THE_GAIN_OVER_HOLDING_IN_THE_POSITION'S_R\",\"pick\":\"THE_HIGHEST_MEAN_DELTA_OVER_ENTRIES_1_TO_30_TIES_TO_THE_EARLIER_EXIT; STORED_ONCE\",\"pick_at_entries\":30},\"id\":\"RESULT_CHECKS_V1\",\"kind\":\"FUTURES_CHECKS\",\"label\":\"HINDSIGHT_ON_TRADES_MODELED_ON_1M_CANDLES; NOTHING_HERE_CHANGES_A_RULE_OR_REACHES_AN_AGENT\",\"luck_floor\":{\"above_at_or_over\":\"0.95\",\"bar\":\"UNIFORM_AMONG_THE_SAME_UTC_DAY'S_SCORED_BARS\",\"below_at_or_under\":\"0.05\",\"exits\":\"THE_ENTRY'S_OWN\",\"minimum_entries\":30,\"percentile\":\"SHARE_OF_STREAMS_BELOW_PLUS_HALF_THE_TIES\",\"secondary_side\":\"THE_TRADER'S_OWN\",\"seed\":\"THE_DEFINITION'S_HASH_THE_TEMPLATE_AND_THE_NEWEST_ENTRY\",\"side\":\"A_FAIR_COIN\",\"statistic\":\"TOTAL_NET_R\",\"streams\":1000},\"source\":\"ExecPlan 0045 section 4, approved by the owner on 2026-10-27\",\"status\":\"PROPOSED\",\"version\":1,\"window\":{\"bar\":\"THE_DECISION'S_BAR_ELSE_THE_NEWEST_FINISHED_15M_BAR_BEFORE_ITS_CONTEXT_TIME\",\"counted\":\"IN_FILL_ORDER_AN_ENTRY_WHOSE_BAR_IS_SCORED_ONCE_EVERY_BAR_OF_ITS_UTC_DAY_THE_BUILDER_BUILDS_IS_STORED; ONE_THAT_WAITS_HOLDS_THE_LATER_ONES\",\"entries\":\"FILLED_ENTRIES_OF_THE_NEWEST_TRADER_TEMPLATE_IN_FILL_ORDER_ACROSS_RUNS\"}}", "5c924ba651cde07af0c17e5222755aeb956bda9e500e63393a787755d3013e40"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    rows = []
    for line in CHECKS_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KIND_ADDED:
            raise RuntimeError("frozen checks definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


# 0020's view of the candles, with the taker buy volume as its last column; downgrade makes 0020's again.
BARS_VIEW = """
CREATE OR REPLACE VIEW agent_read.futures_bars WITH (security_barrier = true) AS
    SELECT open_ms, open, high, low, close, volume, quote_volume, trades, final{columns} FROM perp_bars;
"""
BARS_COLUMNS = ", taker_buy_volume"

# Every column but the times is its document's value, so the two cannot disagree.
TABLES_SQL = """
CREATE TABLE futures_bar_outcomes (
    bar_open_ms bigint PRIMARY KEY CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    canonical text NOT NULL CHECK (octet_length(canonical) <= 16384),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    checks_sha256 text GENERATED ALWAYS AS (document->'checks'->>'sha256') STORED NOT NULL,
    state text GENERATED ALWAYS AS (document->>'state') STORED NOT NULL CHECK (state IN ('SCORED','INCOMPLETE')),
    reason text GENERATED ALWAYS AS (document->>'reason') STORED
        CHECK (reason IN ('MISSING_CANDLES','MISSING_FUNDING','NO_ATR','BUILD_FAILED')),
    taker_buy_share numeric GENERATED ALWAYS AS (CAST(document->>'taker_buy_share' AS numeric)) STORED
        CHECK (taker_buy_share >= 0 AND taker_buy_share <= 1),
    CONSTRAINT futures_bar_outcome_state CHECK (CASE state
        WHEN 'SCORED' THEN reason IS NULL AND jsonb_typeof(document->'outcomes') = 'object'
        ELSE reason IS NOT NULL AND jsonb_typeof(document->'outcomes') = 'null' END)
);
CREATE INDEX futures_bar_outcomes_share ON futures_bar_outcomes (bar_open_ms) WHERE taker_buy_share IS NOT NULL;
CREATE TABLE futures_check_results (
    id uuid PRIMARY KEY,
    day date NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 65536),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    checks_sha256 text GENERATED ALWAYS AS (document->'checks'->>'sha256') STORED NOT NULL,
    state text GENERATED ALWAYS AS (document->>'state') STORED NOT NULL CHECK (state IN ('DONE','FAILED')),
    error text GENERATED ALWAYS AS (document->>'error') STORED CHECK (char_length(error) <= 80),
    template text GENERATED ALWAYS AS (document->'window'->>'template') STORED,
    CONSTRAINT futures_check_result_state CHECK (CASE state WHEN 'DONE' THEN error IS NULL ELSE error IS NOT NULL END)
);
CREATE UNIQUE INDEX futures_check_results_one_a_day ON futures_check_results (day) WHERE state = 'DONE';
CREATE INDEX futures_check_results_at ON futures_check_results (created_at);
"""

GUARD_SQL = """
-- A bar's outcomes and a day's result come only from the agent identity and name the stored checks definition by its
-- hash. A bar's outcomes are written no earlier than the 1,441 minutes after its close (an INCOMPLETE one no earlier
-- than seven days after that); a result on or after its own UTC day.
CREATE FUNCTION asl_result_checks_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE d jsonb := NEW.document; stored jsonb; ready_at timestamptz;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a result check is written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    stored := asl_m8_execution_definition(d->'checks'->>'id', d->'checks'->>'sha256');
    IF stored IS NULL OR stored->>'kind' <> 'FUTURES_CHECKS' THEN
        RAISE EXCEPTION 'a result check names its stored checks definition'; END IF;
    IF TG_TABLE_NAME = 'futures_bar_outcomes' THEN
        IF d->>'schema' IS DISTINCT FROM 'BAR_OUTCOMES_V1'
                OR CAST(d->>'bar_open_ms' AS bigint) IS DISTINCT FROM NEW.bar_open_ms THEN
            RAISE EXCEPTION 'a bar''s outcomes describe their bar'; END IF;
        ready_at := to_timestamp((NEW.bar_open_ms + 900000 + 1441 * 60000) / 1000.0);
        IF ready_at > NEW.created_at
                OR (d->>'state' = 'INCOMPLETE' AND ready_at + interval '7 days' > NEW.created_at) THEN
            RAISE EXCEPTION 'a bar''s outcomes are written after their horizon, incomplete ones a week after'; END IF;
    ELSE
        IF d->>'schema' IS DISTINCT FROM 'RESULT_CHECKS_RESULT_V1' OR d->>'result_id' IS DISTINCT FROM NEW.id::text
                OR d->>'day' IS DISTINCT FROM to_char(NEW.day, 'YYYY-MM-DD') THEN
            RAISE EXCEPTION 'a result describes its day'; END IF;
        IF NEW.day > (NEW.created_at AT TIME ZONE 'UTC')::date THEN
            RAISE EXCEPTION 'a result is written on or after its day'; END IF;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_bar_outcomes_content BEFORE INSERT ON futures_bar_outcomes
    FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard();
CREATE TRIGGER futures_bar_outcomes_guard BEFORE INSERT ON futures_bar_outcomes
    FOR EACH ROW EXECUTE FUNCTION asl_result_checks_guard();
CREATE TRIGGER futures_bar_outcomes_immutable BEFORE UPDATE OR DELETE ON futures_bar_outcomes
    FOR EACH ROW EXECUTE FUNCTION asl_immutable();
CREATE TRIGGER futures_check_results_content BEFORE INSERT ON futures_check_results
    FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard();
CREATE TRIGGER futures_check_results_guard BEFORE INSERT ON futures_check_results
    FOR EACH ROW EXECUTE FUNCTION asl_result_checks_guard();
CREATE TRIGGER futures_check_results_immutable BEFORE UPDATE OR DELETE ON futures_check_results
    FOR EACH ROW EXECUTE FUNCTION asl_immutable();
"""

VIEW_LOCK = "LOCK TABLE agent_read.futures_bars IN ACCESS EXCLUSIVE MODE"  # locks perp_bars after it


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # The view first, as its readers take it, and through it its table: no lock-order inversion with an agent's read.
    op.execute(VIEW_LOCK)
    op.execute("ALTER TABLE perp_bars ADD COLUMN taker_buy_volume numeric "
               "CONSTRAINT perp_bar_taker_buy CHECK (taker_buy_volume >= 0 AND taker_buy_volume <= volume)")
    # The feed replaces an open candle with ON CONFLICT DO UPDATE, which needs the new column's UPDATE (0019 grants
    # UPDATE column by column); its table-wide INSERT already covers it. Dropping the column drops the grant.
    op.execute("GRANT UPDATE (taker_buy_volume) ON perp_bars TO asl_market_worker")
    op.execute(BARS_VIEW.replace("{columns}", BARS_COLUMNS))
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               "ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN "
               f"{_quoted((*DEFINITION_KINDS, *KIND_ADDED))})")
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    op.execute(TABLES_SQL)
    op.execute(GUARD_SQL.replace("{path}", SEARCH_PATH))
    op.execute("GRANT SELECT, INSERT ON futures_bar_outcomes, futures_check_results TO asl_agent")
    op.execute("GRANT SELECT ON futures_bar_outcomes, futures_check_results TO asl_api")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # Nothing can be stored between the count and the drop.
    op.execute("LOCK TABLE futures_bar_outcomes, futures_check_results IN ACCESS EXCLUSIVE MODE")
    op.execute(VIEW_LOCK)
    if bind.exec_driver_sql("SELECT (SELECT count(*) FROM futures_bar_outcomes) "
                            "+ (SELECT count(*) FROM futures_check_results)").scalar_one():
        raise RuntimeError("result checks exist; downgrade refused; fix forward")
    op.execute("DROP TABLE futures_bar_outcomes, futures_check_results")
    op.execute("DROP FUNCTION asl_result_checks_guard()")
    # A view loses a column only by being made again; 0020's grant is restored with it.
    op.execute("DROP VIEW agent_read.futures_bars")
    op.execute(BARS_VIEW.replace("{columns}", "").replace("CREATE OR REPLACE VIEW", "CREATE VIEW"))
    op.execute("GRANT SELECT ON agent_read.futures_bars TO asl_agent")
    op.execute("ALTER TABLE perp_bars DROP COLUMN taker_buy_volume")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen row, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("checks definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(DEFINITION_KINDS)})")
