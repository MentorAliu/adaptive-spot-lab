"""ExecPlan 0041 part 1: the twins, three isolated paper accounts beside the trader.

Revision ID: 0023_twins
Revises: 0022_trade_reviews

ExecPlan 0041 section 4.1. Additive: nothing of the owner's account, its journal, its reservations, the futures
engine's tables or the agents changes. Each guard resolves names under a fixed search path.

- ``TWIN_SET_V1`` in ``execution_definitions`` (frozen here, checked against the code), its kind ``FUTURES_TWINS``.
- ``futures_twins``: one row per twin and segment, with its own wallet, reserved margin, high-water equity, day's
  reference and state (``RUNNING``, ``LATCHED``, ``STOPPED`` or ``FAULTED``). At most one live segment per twin; an
  ended segment never changes; the high-water equity never falls; the wallet never falls below the margin.
- ``futures_twin_candidates``: every bar at which a twin's rule signaled an entry, with the quote's five levels, the
  mark, the ATR, the sizing, the gate's and the filter's verdicts and the outcome, kept after the quotes are deleted.
- ``futures_twin_positions``, ``futures_twin_fills`` and ``futures_twin_funding``: as the trader's, with the same
  guards (a position's terms never change, a closed position never changes, a posted funding never changes); the
  hold twin's position has no stop and no time exit.
- ``futures_twin_valuations`` and ``futures_twin_events`` (starts, latches, references, wallet checks, faults, notes).

Only the execution identity writes them; the API reads them. Downgrade refuses once any twin exists; otherwise it
drops the tables and restores the definitions' kind check.
"""

import hashlib
import json

from alembic import op

revision = "0023_twins"
down_revision = "0022_trade_reviews"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
# The definition kinds as migration 0020 left them, and the one this migration adds.
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET", "FUTURES_POLICY", "FUTURES_COST")
KIND_ADDED = ("FUTURES_TWINS",)
TABLES = ("futures_twin_events", "futures_twin_valuations", "futures_twin_funding", "futures_twin_fills",
          "futures_twin_positions", "futures_twin_candidates", "futures_twins")

# The frozen set: ``python -m app.futures.twins`` prints it; tests/test_m11_twins_db.py checks it.
TWIN_SEED_LINES = r"""
["TWIN_SET_V1", "FUTURES_TWINS", 1, "PROPOSED", "{\"comparison\":{\"bootstrap\":\"STATIONARY_POLITIS_ROMANO_1994\",\"confidence\":\"0.95\",\"day\":\"UTC\",\"gap_day\":\"EITHER_ACCOUNT_WITHOUT_A_VALID_VALUE_AT_A_MIDNIGHT_A_GAP_OVER_65_MIN_OR_AN_INVALID_ONE\",\"mean_block_days\":3,\"minimum\":{\"paired_days\":30,\"trader_closed_trades\":60},\"resamples\":2000,\"seed\":\"THE_SET'S_HASH_THE_TWIN'S_AND_THE_RUN'S_IDS\",\"statistic\":\"PAIRED_DAILY_LOG_RETURN_DIFFERENCES_TRADER_NAV_MINUS_TWIN_EQUITY\",\"threshold\":\"NONE_NOTHING_IS_PROMOTED_OR_CHANGED\"},\"cost\":\"FUTURES_COST_V1\",\"funding_filter\":{\"basis\":\"THREE_TIMES_BINANCE'S_DEFAULT_RATE_OF_0.01%\",\"max_abs_rate\":\"0.0003\",\"rate\":\"THE_MARK'S_ANNOUNCED_FUNDING_RATE\",\"refuse\":\"AN_ENTRY_ON_THE_PAYING_SIDE_WHILE_THE_RATE'S_MAGNITUDE_IS_ABOVE_THE_MAX\"},\"gate\":{\"distance\":\"THE_PLANNED_ENTRY_FILL_TO_THE_ROUNDED_STOP\",\"multiple\":\"3\",\"price\":\"THE_PLANNED_ENTRY_FILL\",\"refuse\":\"THE_STOP'S_DISTANCE_PER_UNIT_BELOW_MULTIPLE_X_THE_ROUND_TRIP_COST_PER_UNIT\",\"round_trip_cost_per_unit\":\"2_X_TAKER_X_PRICE_PLUS_2_X_SLIPPAGE_X_PRICE_PLUS_THE_QUOTE'S_SPREAD\"},\"id\":\"TWIN_SET_V1\",\"kind\":\"FUTURES_TWINS\",\"label\":\"ISOLATED_PAPER_ACCOUNTS_NOT_THE_OWNER'S_ACCOUNT\",\"ledger\":\"THEIR_OWN_ROWS_NO_JOURNAL_NO_RESERVATION_NO_ACCOUNT_STATE\",\"policy\":\"FUTURES_POLICY_V1\",\"protection\":\"EVERY_SECOND_AFTER_THE_OWNER'S_STEP_LIQUIDATION_STOP_TIME_EXIT_WHATEVER_THE_AGENTS_OR_THE_RUN\",\"shared\":\"THE_POLICY'S_SIZING_COOLDOWNS_ENTRIES_PER_UTC_DAY_AND_LATCHES_AND_THE_COST'S_FILLS_FEES_FUNDING_AND_LIQUIDATION_ON_THE_SAME_QUOTES_AND_MARKS\",\"source\":\"ExecPlan 0041 section 4.1, approved by the owner on 2026-10-25\",\"start_equity\":\"10000\",\"status\":\"PROPOSED\",\"step_errors\":{\"fault_after\":60,\"other\":\"FAULTS_THAT_TWIN_ALONE\",\"retried\":\"A_DATABASE_TIMEOUT_A_LOCK_WAIT_OR_A_DEADLOCK_THE_NEXT_SECOND\"},\"trend\":{\"atr\":\"THE_POLICY'S_15M_WILDER_ATR\",\"bar_max_age_seconds\":\"THE_POLICY'S_DECISION_MAX_AGE\",\"candles\":\"COMPLETE_1H_CANDLES_BUILT_FROM_FINAL_1M_CANDLES_THE_NEWEST_CONTIGUOUS_RUN\",\"drawdown\":\"LATCHED_THEN_STOPPED_ONCE_FLAT_THE_SEGMENT_ENDS\",\"ema_seed\":\"SMA_OF_FIRST_COMPLETE_PERIOD\",\"evaluated\":\"ONCE_AT_EACH_FINISHED_15M_BAR_AFTER_ITS_LAST_MINUTE_IS_FINAL_OR_60_S\",\"exit\":\"AT_A_FINISHED_15M_BAR_WHEN_THE_HOUR_THAT_FINISHED_LAST_HAS_THE_FAST_EMA_AGAINST_THE_SIDE\",\"fast_ema\":20,\"interval_ms\":3600000,\"leverage\":\"1\",\"limits\":\"THE_POLICY'S_COOLDOWNS_ENTRIES_PER_UTC_DAY_DAILY_LOSS_AND_DRAWDOWN\",\"long_cross\":\"PREV_FAST_LTE_SLOW_AND_CUR_FAST_GT_SLOW\",\"max_hold_hours\":24,\"risk_fraction\":\"THE_POLICY'S\",\"run_window_max_hours\":720,\"short_cross\":\"PREV_FAST_GTE_SLOW_AND_CUR_FAST_LT_SLOW\",\"signal\":\"A_CROSS_ON_THE_HOUR_THAT_FINISHED_LAST_LIVE_AT_EACH_15M_BAR_OF_THE_NEXT_HOUR\",\"signal_spent\":\"BY_A_FILL_OR_A_REFUSAL_OF_THE_GATE_OR_THE_FUNDING_FILTER\",\"slow_ema\":50,\"stop_atr_multiple\":\"2.0\",\"take_profit\":null,\"warmup_hours\":100},\"twins\":[{\"funding\":\"PAID_AND_RECEIVED_AS_THE_TRADER'S\",\"id\":\"HOLD\",\"latches\":\"NONE\",\"leverage\":\"1\",\"max_hold_hours\":null,\"reentry\":\"NEVER\",\"rule\":\"LONG_ONCE_AT_THE_FIRST_FINISHED_15M_BAR_THEN_HOLD\",\"size\":\"THE_WHOLE_WALLET_LESS_THE_ENTRY_FEE_THE_EXIT_FEE_AND_THE_POLICY'S_FUNDING_RESERVE\",\"stop\":null,\"take_profit\":null},{\"funding_filter\":false,\"gate\":false,\"id\":\"TREND\",\"rule\":\"EMA_CROSS_1H\"},{\"funding_filter\":true,\"gate\":true,\"id\":\"TREND_GATED\",\"rule\":\"EMA_CROSS_1H\"}],\"valuation\":\"CASH_PLUS_THE_OPEN_POSITION'S_UNREALIZED_PNL_AT_THE_MARK_LESS_SETTLED_FUNDING_WAITING_FOR_THE_FREE_WALLET\",\"version\":1,\"wallet_check\":{\"every_seconds\":3600,\"fault\":\"STOPS_THAT_TWIN_ALONE\",\"formula\":\"START_PLUS_REALIZED_PNL_MINUS_FEES_PLUS_FUNDING_RESERVED_THE_OPEN_MARGIN\"}}", "07012eb928f5e8cb616e0e505dde252fcd48046de095c4c0948f157e940900ff"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    rows = []
    for line in TWIN_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KIND_ADDED:
            raise RuntimeError("frozen twin set is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


TABLES_SQL = """
CREATE TABLE futures_twins (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    twin varchar(12) NOT NULL CHECK (twin IN ('HOLD','TREND','TREND_GATED')),
    segment integer NOT NULL CHECK (segment >= 1),
    set_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    set_sha256 varchar(64) NOT NULL CHECK (set_sha256 ~ '^[0-9a-f]{64}$'),
    policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    cost_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    cost_sha256 varchar(64) NOT NULL CHECK (cost_sha256 ~ '^[0-9a-f]{64}$'),
    code_identity varchar(64) NOT NULL CHECK (code_identity ~ '^[0-9a-f]{64}$'),
    state varchar(8) NOT NULL CHECK (state IN ('RUNNING','LATCHED','STOPPED','FAULTED')),
    causes text[] NOT NULL DEFAULT '{}' CHECK (causes <@ ARRAY['DAILY_LOSS','DRAWDOWN']::text[]),
    start_equity numeric(38,8) NOT NULL CHECK (start_equity > 0),
    cash numeric(38,8) NOT NULL,
    reserved numeric(38,8) NOT NULL CHECK (reserved >= 0),
    high_water numeric(38,8) NOT NULL CHECK (high_water >= start_equity),
    reference_date date,
    reference_equity numeric(38,8) CHECK (reference_equity > 0),
    last_bar_ms bigint CHECK (last_bar_ms >= 0 AND last_bar_ms % 900000 = 0),
    wallet_checked_at timestamptz,
    started_at timestamptz NOT NULL,
    ended_at timestamptz,
    end_reason varchar(12) CHECK (end_reason IN ('DRAWDOWN','FAULT')),
    fault jsonb,
    version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (twin, segment),
    CONSTRAINT futures_twin_wallet CHECK (cash >= reserved),
    CONSTRAINT futures_twin_ended CHECK ((state IN ('STOPPED','FAULTED')) = (ended_at IS NOT NULL AND end_reason IS NOT NULL)),
    CONSTRAINT futures_twin_fault CHECK ((state = 'FAULTED') = (fault IS NOT NULL)
        AND (state <> 'FAULTED' OR end_reason = 'FAULT') AND (state <> 'STOPPED' OR end_reason = 'DRAWDOWN')),
    CONSTRAINT futures_twin_causes CHECK ((state <> 'LATCHED' OR cardinality(causes) > 0)
        AND (state <> 'RUNNING' OR cardinality(causes) = 0)),
    CONSTRAINT futures_twin_reference CHECK ((reference_date IS NULL) = (reference_equity IS NULL))
);
CREATE UNIQUE INDEX futures_twins_one_live ON futures_twins (twin) WHERE state IN ('RUNNING','LATCHED');

CREATE TABLE futures_twin_candidates (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    twin_id uuid NOT NULL REFERENCES futures_twins(id),
    bar_open_ms bigint NOT NULL CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    rule varchar(12) NOT NULL CHECK (rule IN ('HOLD_START','EMA_CROSS')),
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    signal_open_ms bigint CHECK (signal_open_ms >= 0 AND signal_open_ms % 3600000 = 0),
    signal jsonb NOT NULL,
    atr numeric CHECK (atr > 0),
    quote_second timestamptz,
    bid numeric(38,8) CHECK (bid > 0),
    ask numeric(38,8) CHECK (ask > 0),
    -- The quote's five levels of each side as [price, quantity] decimal strings, best first.
    bids jsonb CHECK (bids IS NULL OR jsonb_typeof(bids) = 'array'),
    asks jsonb CHECK (asks IS NULL OR jsonb_typeof(asks) = 'array'),
    mark_second timestamptz,
    mark numeric(38,8) CHECK (mark > 0),
    funding_rate numeric CHECK (funding_rate > -1 AND funding_rate < 1),
    plan jsonb NOT NULL DEFAULT '{}',
    gate varchar(12) NOT NULL CHECK (gate IN ('PASSED','REFUSED','NOT_APPLIED','NOT_REACHED')),
    gate_detail jsonb NOT NULL DEFAULT '{}',
    funding_filter varchar(12) NOT NULL CHECK (funding_filter IN ('PASSED','REFUSED','NOT_APPLIED','NOT_REACHED')),
    outcome varchar(8) NOT NULL CHECK (outcome IN ('FILLED','REFUSED')),
    codes text[] NOT NULL DEFAULT '{}',
    spent boolean NOT NULL,
    at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (twin_id, bar_open_ms),
    CONSTRAINT futures_twin_candidate_codes CHECK ((outcome = 'REFUSED') = (cardinality(codes) > 0)),
    CONSTRAINT futures_twin_candidate_spent CHECK (outcome = 'REFUSED' OR spent),
    CONSTRAINT futures_twin_candidate_rule CHECK ((rule = 'HOLD_START') = (signal_open_ms IS NULL))
);
CREATE INDEX futures_twin_candidates_signal ON futures_twin_candidates (twin_id, signal_open_ms);

CREATE TABLE futures_twin_positions (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    twin_id uuid NOT NULL REFERENCES futures_twins(id),
    candidate_id uuid NOT NULL UNIQUE REFERENCES futures_twin_candidates(id),
    side varchar(5) NOT NULL CHECK (side IN ('LONG','SHORT')),
    leverage numeric NOT NULL CHECK (leverage IN (1, 2)),
    quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
    entry_price numeric(38,8) NOT NULL CHECK (entry_price > 0),
    notional numeric(38,8) NOT NULL CHECK (notional > 0),
    margin numeric(38,8) NOT NULL CHECK (margin > 0),
    maintenance_rate numeric NOT NULL CHECK (maintenance_rate > 0 AND maintenance_rate < 1),
    maintenance_amount numeric NOT NULL CHECK (maintenance_amount >= 0),
    liquidation_price numeric(38,8) CHECK (liquidation_price > 0),
    atr numeric CHECK (atr > 0),
    stop_multiple numeric CHECK (stop_multiple IN (1.0, 1.5, 2.0, 3.0)),
    max_hold_hours integer CHECK (max_hold_hours IN (1, 4, 12, 24)),
    initial_stop numeric(38,8) CHECK (initial_stop > 0),
    stop_price numeric(38,8) CHECK (stop_price > 0),
    risk numeric(38,8) CHECK (risk >= 0),
    risk_cap numeric(38,8) CHECK (risk_cap > 0 AND risk <= risk_cap),
    opened_at timestamptz NOT NULL,
    time_exit_at timestamptz CHECK (time_exit_at > opened_at),
    state varchar(6) NOT NULL CHECK (state IN ('OPEN','CLOSED')),
    closed_at timestamptz,
    close_reason varchar(12) CHECK (close_reason IN ('STOP','TIME','LIQUIDATION','SIGNAL_EXIT')),
    exit_price numeric(38,8) CHECK (exit_price > 0),
    realized_pnl numeric(38,8),
    fees numeric(38,8) NOT NULL CHECK (fees >= 0),
    version integer NOT NULL DEFAULT 0 CHECK (version >= 0),
    CONSTRAINT futures_twin_position_closed CHECK ((state = 'CLOSED') = (closed_at IS NOT NULL
        AND close_reason IS NOT NULL AND exit_price IS NOT NULL AND realized_pnl IS NOT NULL)),
    -- A stopped position (the trend twins') has its stop, ATR, risk and time exit; the hold twin's has none of them.
    CONSTRAINT futures_twin_position_terms CHECK (CASE WHEN initial_stop IS NULL
        THEN stop_price IS NULL AND atr IS NULL AND stop_multiple IS NULL AND risk IS NULL AND risk_cap IS NULL
            AND max_hold_hours IS NULL AND time_exit_at IS NULL
        ELSE stop_price IS NOT NULL AND atr IS NOT NULL AND stop_multiple IS NOT NULL AND risk IS NOT NULL
            AND risk_cap IS NOT NULL AND max_hold_hours IS NOT NULL AND time_exit_at IS NOT NULL END),
    CONSTRAINT futures_twin_position_initial_stop CHECK (initial_stop IS NULL OR CASE side
        WHEN 'LONG' THEN initial_stop < entry_price ELSE initial_stop > entry_price END),
    CONSTRAINT futures_twin_position_liquidation CHECK (liquidation_price IS NULL OR initial_stop IS NULL OR CASE side
        WHEN 'LONG' THEN liquidation_price < initial_stop ELSE liquidation_price > initial_stop END)
);
CREATE UNIQUE INDEX futures_twin_positions_one_open ON futures_twin_positions (twin_id) WHERE state = 'OPEN';
CREATE INDEX futures_twin_positions_twin ON futures_twin_positions (twin_id, seq);

CREATE TABLE futures_twin_fills (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    position_id uuid NOT NULL REFERENCES futures_twin_positions(id),
    kind varchar(12) NOT NULL CHECK (kind IN ('ENTRY','EXIT','LIQUIDATION')),
    reason varchar(12) NOT NULL CHECK (reason IN ('RULE_ENTRY','STOP','TIME','LIQUIDATION','SIGNAL_EXIT')),
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
    quote_bid numeric(38,8),
    quote_ask numeric(38,8),
    mark_second timestamptz,
    mark_price numeric(38,8),
    filled_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_twin_fill_source CHECK (CASE kind WHEN 'LIQUIDATION' THEN mark_second IS NOT NULL
        AND mark_price IS NOT NULL AND fee = 0
        ELSE quote_second IS NOT NULL AND quote_bid IS NOT NULL AND quote_ask IS NOT NULL END)
);
CREATE UNIQUE INDEX futures_twin_fills_entry ON futures_twin_fills (position_id) WHERE kind = 'ENTRY';
CREATE UNIQUE INDEX futures_twin_fills_close ON futures_twin_fills (position_id) WHERE kind <> 'ENTRY';

CREATE TABLE futures_twin_funding (
    id uuid PRIMARY KEY,
    position_id uuid NOT NULL REFERENCES futures_twin_positions(id),
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
    CONSTRAINT futures_twin_funding_posted CHECK ((status = 'POSTED') = (rate IS NOT NULL AND mark IS NOT NULL
        AND mark_source IS NOT NULL AND amount IS NOT NULL AND posted_at IS NOT NULL))
);
CREATE INDEX futures_twin_funding_pending ON futures_twin_funding (funding_ms) WHERE status = 'PENDING';

CREATE TABLE futures_twin_valuations (
    id uuid PRIMARY KEY,
    twin_id uuid NOT NULL REFERENCES futures_twins(id),
    valued_at timestamptz NOT NULL,
    purpose varchar(16) NOT NULL CHECK (purpose IN ('START','FILL','FUNDING','PERIODIC','HOURLY','DAILY_REFERENCE',
        'HIGH_WATER','LATCH','STOP')),
    cash numeric(38,8) NOT NULL,
    reserved numeric(38,8) NOT NULL,
    position_id uuid REFERENCES futures_twin_positions(id),
    mark numeric(38,8),
    mark_second timestamptz,
    unrealized numeric(38,8),
    pending_funding integer NOT NULL DEFAULT 0 CHECK (pending_funding >= 0),
    funding_owed numeric(38,8) NOT NULL DEFAULT 0 CHECK (funding_owed <= 0),
    equity numeric(38,8),
    quality varchar(8) NOT NULL CHECK (quality IN ('VALID','INVALID')),
    reason varchar(48),
    twin_version integer NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_twin_valuation_quality CHECK ((quality = 'VALID') = (equity IS NOT NULL)),
    CONSTRAINT futures_twin_valuation_mark CHECK (position_id IS NULL OR quality = 'INVALID'
        OR (mark IS NOT NULL AND unrealized IS NOT NULL))
);
CREATE INDEX futures_twin_valuations_twin ON futures_twin_valuations (twin_id, valued_at);

CREATE TABLE futures_twin_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    twin_id uuid NOT NULL REFERENCES futures_twins(id),
    kind varchar(16) NOT NULL CHECK (kind IN ('STARTED','LATCHED','LATCH_CLEARED','STOPPED','FAULTED',
        'DAILY_REFERENCE','WALLET_CHECKED','NOTE')),
    code varchar(48),
    at timestamptz NOT NULL,
    detail jsonb NOT NULL DEFAULT '{}',
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT futures_twin_event_code CHECK ((kind = 'NOTE') = (code IS NOT NULL))
);
CREATE INDEX futures_twin_events_twin ON futures_twin_events (twin_id, id);
"""

GUARDS_SQL = """
CREATE FUNCTION asl_futures_twin_append_only() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN RAISE EXCEPTION 'append-only twin record'; END $$;

-- A twin: its identity and start never change; an ended segment never changes; its high-water equity never falls.
CREATE FUNCTION asl_futures_twin_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.state IN ('STOPPED','FAULTED') THEN RAISE EXCEPTION 'an ended twin segment cannot change'; END IF;
    IF (NEW.id, NEW.seq, NEW.twin, NEW.segment, NEW.set_id, NEW.set_sha256, NEW.policy_id, NEW.policy_sha256,
            NEW.cost_id, NEW.cost_sha256, NEW.code_identity, NEW.start_equity, NEW.started_at, NEW.recorded_at)
            IS DISTINCT FROM (OLD.id, OLD.seq, OLD.twin, OLD.segment, OLD.set_id, OLD.set_sha256, OLD.policy_id,
            OLD.policy_sha256, OLD.cost_id, OLD.cost_sha256, OLD.code_identity, OLD.start_equity, OLD.started_at,
            OLD.recorded_at) THEN
        RAISE EXCEPTION 'twin identity is immutable'; END IF;
    IF NEW.high_water < OLD.high_water THEN RAISE EXCEPTION 'twin high-water equity cannot decrease'; END IF;
    RETURN NEW;
END $$;

-- A twin's position: its terms never change and a closed position never changes (no twin tightens its stop).
CREATE FUNCTION asl_futures_twin_position_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.state = 'CLOSED' THEN RAISE EXCEPTION 'closed twin position cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['state','closed_at','close_reason','exit_price','realized_pnl','fees','version'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['state','closed_at','close_reason','exit_price','realized_pnl',
            'fees','version']) THEN
        RAISE EXCEPTION 'twin position terms are immutable'; END IF;
    IF NEW.fees < OLD.fees THEN RAISE EXCEPTION 'twin position fees cannot decrease'; END IF;
    RETURN NEW;
END $$;

-- A twin's funding record is posted once with its rate and mark; a posted one never changes.
CREATE FUNCTION asl_futures_twin_funding_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.status <> 'PENDING' THEN RAISE EXCEPTION 'posted twin funding cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['status','rate','mark','mark_source','amount','posted_at'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','rate','mark','mark_source','amount','posted_at']) THEN
        RAISE EXCEPTION 'twin funding record identity is immutable'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_twins_guard BEFORE UPDATE ON futures_twins
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_guard();
CREATE TRIGGER futures_twin_positions_guard BEFORE UPDATE ON futures_twin_positions
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_position_guard();
CREATE TRIGGER futures_twin_funding_guard BEFORE UPDATE ON futures_twin_funding
    FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_funding_guard();
"""

APPEND_ONLY = ("futures_twin_candidates", "futures_twin_fills", "futures_twin_valuations", "futures_twin_events")
NO_DELETE = ("futures_twins", "futures_twin_positions", "futures_twin_funding")

GRANTS_SQL = """
GRANT SELECT, INSERT ON futures_twins, futures_twin_candidates, futures_twin_positions, futures_twin_fills,
    futures_twin_funding, futures_twin_valuations, futures_twin_events TO asl_execution;
GRANT UPDATE (state, causes, cash, reserved, high_water, reference_date, reference_equity, last_bar_ms,
    wallet_checked_at, ended_at, end_reason, fault, version) ON futures_twins TO asl_execution;
GRANT UPDATE (state, closed_at, close_reason, exit_price, realized_pnl, fees, version)
    ON futures_twin_positions TO asl_execution;
GRANT UPDATE (status, rate, mark, mark_source, amount, posted_at) ON futures_twin_funding TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE futures_twins_seq_seq, futures_twin_candidates_seq_seq,
    futures_twin_positions_seq_seq, futures_twin_fills_seq_seq, futures_twin_events_id_seq TO asl_execution;
GRANT SELECT ON futures_twins, futures_twin_candidates, futures_twin_positions, futures_twin_fills,
    futures_twin_funding, futures_twin_valuations, futures_twin_events TO asl_api;
"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               "ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN "
               f"{_quoted((*DEFINITION_KINDS, *KIND_ADDED))})")
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    op.execute(TABLES_SQL)
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH))
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_append_only()")
    for table in NO_DELETE:
        op.execute(f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_futures_twin_append_only()")
    op.execute(GRANTS_SQL)


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    if bind.exec_driver_sql("SELECT count(*) FROM futures_twins").scalar_one():
        raise RuntimeError("twin records exist; downgrade refused; fix forward")
    op.execute(f"DROP TABLE {', '.join(TABLES)}")
    op.execute("DROP FUNCTION asl_futures_twin_append_only(), asl_futures_twin_guard(), "
               "asl_futures_twin_position_guard(), asl_futures_twin_funding_guard()")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen row, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("twin set definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(DEFINITION_KINDS)})")
