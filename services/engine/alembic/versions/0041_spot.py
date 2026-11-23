"""ExecPlan 0060: spot trading only (M12). The futures account retires and the main account trades Bitcoin spot.

Revision ID: 0041_spot
Revises: 0040_main_rule

ExecPlan 0060 sections 4.3 to 4.7, in one transaction:

1. **Preconditions.** The futures account is flat: no open futures position, no pending futures funding payment, no
   active reservation and nothing reserved. Otherwise nothing changes and the migration says why. A coin's dust that
   M3 to M10's sales left in ``account_holdings`` (below the coin's minimum order) stays where it is, with its
   postings: BTC's is part of the spot account's holding, the other coins' are no longer valued (worth cents).
2. **The futures run retires.** A live futures run ends as ``SYSTEM``: ``STOPPED`` with ``NEW_POLICY`` (or the stop
   reason it already had), a run event ``FUTURES_RETIRED`` naming the spot definitions and their hashes, its open
   latches resolved and any pending owner request answered ``REJECTED``.
3. **The definitions.** ``SPOT_RULE_V1``, ``SPOT_POLICY_V1`` and ``SPOT_COST_V1`` (new kinds ``SPOT_RULE``,
   ``SPOT_POLICY``, ``SPOT_COST``), frozen here and checked against their own hashes; the execution worker starts only
   when the stored rows equal its code (``app.spot.definitions``).
4. **The archive.** Every table of ``public`` but the account's own (``KEPT``) moves into a schema ``archive`` with
   every row, and the views of ``agent_read``, ``evaluation_read`` and ``research_read`` with it (renamed
   ``<schema>__<view>``); ``archive.moved_objects`` records each move for the downgrade. Only the migration role reads
   the archive: no other role has a grant on its schema. Foreign keys between the kept and the archived tables keep
   working (the journal's ``fill_id`` and ``futures_event_id``, an incident's ``run_id``).
5. **The spot tables.** The market data the market worker writes (``spot_instruments``, ``spot_quotes`` kept two days,
   ``spot_bars`` kept 30 days, ``spot_daily_bars`` kept for good, ``spot_feed_state``, ``spot_feed_events``) and the
   account's records the execution worker writes (``spot_runs``, ``spot_owner_requests``, ``spot_run_events``,
   ``spot_fills``, ``spot_valuations``, ``spot_daily_references``, ``spot_latches``, ``spot_rule_readings``,
   ``spot_backtests``), with their guards and grants.
6. **The journal.** A new source, ``spot_fill_id``, which only the execution identity writes; the retired sources
   (M3's ``fill_id`` and the futures ``futures_event_id``) take no new transaction. ``account_holdings`` keeps its
   rows as they are.

Downgrade is refused once a spot fill exists: a rollback then goes forward, or restores the update's backup. Before
that it moves every archived object back, drops the spot tables (a spot run without a fill, its readings and its
backtests go with them), and restores the journal, the holdings and the definitions as 0040 had them. The retired
futures run stays stopped: its next run is the owner's Start, as after any stop.
"""

import hashlib
import json

from alembic import op

revision = "0041_spot"
down_revision = "0040_main_rule"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
# The account's own tables: everything else of ``public`` moves into ``archive``.
KEPT = ("account_holdings", "account_state", "alembic_version", "audit_events", "execution_definitions",
        "execution_incidents", "execution_lease", "funding_requests", "journal_postings", "journal_transactions",
        "outbox_events", "owner_decisions", "system_metadata")
READ_SCHEMAS = ("agent_read", "evaluation_read", "research_read")
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET", "FUTURES_POLICY", "FUTURES_COST", "FUTURES_TWINS",
                    "FUTURES_SCORING", "FUTURES_CHECKS", "MAIN_RULE")
KINDS_ADDED = ("SPOT_RULE", "SPOT_POLICY", "SPOT_COST")
MARKET_TABLES = ("spot_instruments", "spot_quotes", "spot_bars", "spot_daily_bars", "spot_feed_state",
                 "spot_feed_events")
ACCOUNT_TABLES = ("spot_runs", "spot_owner_requests", "spot_run_events", "spot_fills", "spot_valuations",
                  "spot_daily_references", "spot_latches", "spot_rule_readings", "spot_backtests")

# The frozen definitions: ``python -m app.spot.definitions`` prints them; tests/test_spot_migration.py checks them.
SPOT_SEED_LINES = r"""
["SPOT_RULE_V1", "SPOT_RULE", 1, "PROPOSED", "{\"account\":\"THE_MAIN_SPOT_ACCOUNT\",\"acts\":\"A_TARGET_OF_0_WITH_BTC_HELD: SELL_ALL; ELSE_WHEN_THE_TARGET_IS_MORE_THAN_THE_BUFFER_FROM_HELD: BUY_OR_SELL_THE_DIFFERENCE_(TARGET_-_HELD)_X_EQUITY_AT_THE_BOOK; ELSE_NO_CHANGE\",\"anchor\":\"THE_NEAREST_STORED_DAY_AT_OR_BEFORE_THE_LOOKBACK'S_DAY_WITHIN_THE_TOLERANCE_ELSE_NOT_READABLE\",\"anchor_tolerance_days\":7,\"annualization_days\":365,\"candles\":\"BINANCE'S_FINAL_1D_SPOT_CANDLES_STORED_BY_THE_FEED\",\"day\":\"THE_LAST_COMPLETE_UTC_DAY_BEFORE_THE_READING'S_DAY\",\"day_spent\":\"BY_A_FILL_OR_A_READING_THAT_CHANGES_NOTHING; A_DAY_NOT_READABLE_YET_OR_A_REFUSAL_TRIES_AGAIN_EVERY_15_MINUTES\",\"decider\":\"CODE_NO_MODEL\",\"direction\":\"MAX(SIGNAL,_0): LONG_OR_CASH_NEVER_SHORT\",\"evaluated\":\"AT_THE_ENGINE'S_FIRST_STEP_AT_OR_AFTER_00:05_UTC_ONCE_THE_DAY'S_FINAL_CANDLE_IS_STORED\",\"exits\":\"THE_RULE'S_SELLS_A_STOPPING_RUN'S_SELL_OF_EVERYTHING_AT_ONCE_AND_THE_OWNER'S_STOP_AND_SELL\",\"flat\":\"A_TARGET_BELOW_THE_FLAT_BAND_IS_0\",\"flat_band\":\"0.01\",\"fraction_cap\":\"1\",\"gap_return\":\"A_RETURN_ACROSS_MISSING_DAYS_COUNTS_ONCE\",\"gates\":\"A_LATCH_A_PAUSED_RUN_OR_AN_INTEGRITY_HOLD: NO_BUY_AND_A_SELL_STILL_SELLS; A_STALE_BOOK_A_THIN_BOOK_AN_UNVERIFIED_CLOCK_OR_AN_UNUSABLE_INSTRUMENT: NO_TRADE_REFUSED_WITH_ITS_CODE_AND_TRIED_AGAIN\",\"held\":\"THE_BTC_HELD_AT_THE_FRESH_BEST_BID_OVER_EQUITY_TO_0.00000001_DOWN\",\"held_unknown\":\"BTC_HELD_WITHOUT_A_FRESH_BEST_BID: REFUSED_BID_STALE_AND_TRIED_AGAIN\",\"holding\":\"BTC_THAT_CAN_BE_SOLD: A_SALE_OF_ALL_OF_IT_ON_THE_BOOK_THE_VALUATION_READS_PASSES_THE_SALE'S_OWN_MINIMUM_QUANTITY_AND_NOTIONAL_CHECKS_(THE_NOTIONAL_AT_THE_FILL_PRICE); WITHOUT_THAT_BOOK_THE_MINIMUM_QUANTITY_ALONE; LESS_IS_DUST_AND_COUNTS_AS_NOTHING_HELD_FOR_SELL_ALL\",\"id\":\"SPOT_RULE_V1\",\"instrument\":\"BTCUSDT_SPOT_PAPER\",\"kind\":\"SPOT_RULE\",\"lookback_days\":[30,91,365],\"minimum_days_stored\":300,\"no_stop\":\"NO_STOP_TAKE_PROFIT_OR_TIME_EXIT_ON_THE_HOLDING: ITS_SIZE_AND_THE_LATCHES_PROTECT_IT\",\"quantity\":\"|TARGET_-_HELD|_X_EQUITY_/_THE_BEST_BID_DOWN_TO_THE_STEP; A_SELL_AT_MOST_THE_BTC_HELD\",\"read_after_ms\":300000,\"readings\":\"ONE_SPOT_RULE_READINGS_ROW_PER_DAY_ACTED_ON; A_DAY_NOT_READABLE_OR_REFUSED_ONCE_A_DAY_PER_REASON\",\"rebalance_buffer\":\"0.03\",\"retry_seconds\":900,\"signal\":\"THE_MEAN_OF_THE_SIGNS_OF_THE_DAY'S_CLOSE_AGAINST_THE_CLOSE_EACH_LOOKBACK_BEFORE_IT_A_SIGN_IS_0_WHEN_EQUAL\",\"size_chosen_by\":\"THE_LARGEST_OF_40_30_20_15_10_5%_A_YEAR_WHOSE_WORST_FALL_FROM_THE_HIGH_ON_DAILY_LOWS_STAYS_AT_OR_BELOW_4%_HALF_THE_DRAWDOWN_STOP (EXECPLAN_0059_SECTION_4.2)\",\"source\":\"ExecPlan 0060 sections 4.1 and 4.2, approved by the owner on 2026-11-12\",\"sources\":[\"TR-01\",\"TR-03\",\"TR-10\",\"TR-12\",\"TR-35\"],\"status\":\"PROPOSED\",\"stopping_run\":\"NO_READING: A_STOPPING_RUN_SELLS_EVERYTHING_AT_ONCE\",\"target\":\"MAX(SIGNAL,_0)_X_MIN(CAP,_VOLATILITY_TARGET_/_VOLATILITY)_QUANTIZED_TOWARD_ZERO_TO_THE_STEP\",\"target_step\":\"0.001\",\"version\":1,\"volatility\":\"THE_ANNUALIZED_EXPONENTIALLY_WEIGHTED_STANDARD_DEVIATION_OF_THE_DAILY_LOG_RETURNS_OF_THE_STORED_DAYS_FROM_THE_DAY_365_DAYS_BEFORE_TO_THE_DAY\",\"volatility_centre_of_mass_days\":60,\"volatility_days\":365,\"volatility_recursion\":\"VAR_NEXT_=_(60_X_VAR_+_RETURN_SQUARED)_/_61_SEEDED_WITH_THE_FIRST_RETURN_SQUARED\",\"volatility_target\":\"0.05\"}", "ac8b5e9899855e1d4ab7f3eaf0e1ce34ea462bb9dbf8ba5456dfcb4caf2cfc2a"]
["SPOT_POLICY_V1", "SPOT_POLICY", 1, "PROPOSED", "{\"actions\":[\"RULE_BUY\",\"RULE_SELL\",\"STOP_SELL\"],\"assets\":[\"USDT\",\"BTC\"],\"borrowing\":false,\"cost\":\"SPOT_COST_V1\",\"daily_loss_clears\":\"AT_THE_NEXT_UTC_DAY'S_REFERENCE\",\"daily_loss_fraction\":\"0.02\",\"daily_reference\":{\"late_rule\":\"MAX_OF_LAST_VALID_NAV_PRIOR_24H_AND_FIRST_POST_MIDNIGHT_NAV\",\"timeliness_ms\":300000,\"timezone\":\"UTC\"},\"data\":{\"bid_max_age_ms\":5000,\"book_max_age_ms\":2000,\"clock\":\"VERIFIED_BY_THE_FEED\",\"instrument\":\"USABLE_AND_CHECKED_IN_THE_LAST_HOUR\",\"missing\":\"A_STALE_OR_MISSING_PRICE_REFUSES_THE_TRADE_WITH_ITS_CODE_AND_INVALIDATES_THE_VALUATION\"},\"decided_by\":\"SYSTEM_CODE_NO_MODEL\",\"decider\":\"SPOT_RULE_V1\",\"direction\":\"LONG_OR_CASH\",\"drawdown_fraction\":\"0.08\",\"drawdown_measure\":\"THE_RUN'S_OWN_HIGH_WATER_NAV\",\"dust\":{\"btc\":\"PART_OF_THE_HOLDING_VALUED_AT_THE_BEST_BID\",\"other_coins\":\"M3_TO_M10'S_SALES_LEFT_DUST_OF_SOL_ZEC_NEAR_OR_XRP_BELOW_THEIR_MINIMUM_ORDER: KEPT_IN_THE_HOLDINGS_WITH_ITS_POSTINGS_AND_NOT_VALUED (NO_FEED; WORTH_CENTS)\"},\"id\":\"SPOT_POLICY_V1\",\"instrument\":\"BTCUSDT_SPOT_PAPER\",\"kind\":\"SPOT_POLICY\",\"latch_effect\":\"NO_BUY; SELLS_CONTINUE; THE_DRAWDOWN_STOP_MAKES_THE_RUN_STOPPING_WHICH_SELLS_ALL_AT_ONCE_AND_STOPS_ONCE_ONLY_USDT_IS_HELD\",\"leverage\":\"NONE_1X_BY_CONSTRUCTION\",\"replaces\":\"FUTURES_POLICY_V2\",\"rule\":\"SPOT_RULE_V1\",\"runs\":{\"dust\":\"BTC_A_SALE_OF_ALL_OF_IT_WOULD_PUT_BELOW_THE_INSTRUMENT'S_MINIMUM_QUANTITY_OR_NOTIONAL_AT_ITS_FILL_PRICE_CANNOT_BE_SOLD\",\"first\":\"STARTS_BY_ITSELF_ONCE_FUNDED\",\"later\":\"THE_OWNER'S_START\",\"owner\":[\"PAUSE\",\"RESUME\",\"STOP_AND_SELL\",\"START\"],\"states\":[\"RUNNING\",\"PAUSED\",\"STOPPING\",\"STOPPED\"],\"stop\":\"THE_DRAWDOWN_STOP_OR_THE_OWNER'S_STOP: NO_BUY; THE_BTC_HELD_IS_SOLD_AT_ONCE; STOPPED_ONCE_ONLY_USDT_OR_UNSELLABLE_DUST_IS_HELD\"},\"shorting\":false,\"size\":\"THE_RULE'S_TARGET; A_BUY_AT_MOST_THE_FREE_USDT_AFTER_ITS_FEE_AND_SLIPPAGE; A_SELL_AT_MOST_THE_BTC_HELD\",\"source\":\"ExecPlan 0060 section 4.3, approved by the owner on 2026-11-12\",\"status\":\"PROPOSED\",\"top_ups\":\"NAV_NEUTRAL_AT_A_VALID_VALUATION\",\"valuation\":\"VALUATION_BID_V1\",\"valuation_every_seconds_while\":\"BTC_THAT_CAN_BE_SOLD_IS_HELD\",\"valuation_otherwise\":\"HOURLY_AT_EACH_FILL_EACH_DAY'S_REFERENCE_EACH_NEW_HIGH_AND_THE_FIRST_STEP_AFTER_A_TOP_UP\",\"valuation_rule\":\"CASH_PLUS_BTC_AT_THE_BEST_BID_FLOORED_TO_0.00000001\",\"valuation_seconds\":60,\"version\":1}", "f424c2a0437309536fcc81951e9683ba510effa21fa30c2e551591bbf3ca455c"]
["SPOT_COST_V1", "SPOT_COST", 1, "PROPOSED", "{\"bnb_discount\":false,\"book\":{\"buy_side\":\"ASKS\",\"depth_short\":\"REFUSED_DEPTH_SHORT\",\"levels\":10,\"max_age_ms\":2000,\"sell_side\":\"BIDS\",\"walk\":\"THE_TEN_LEVELS_OF_THE_NEWEST_STORED_BOOK\"},\"fee_asset\":\"USDT\",\"fee_note\":\"BINANCE_TAKES_THE_FEE_IN_THE_ASSET_RECEIVED; THE_SAME_VALUE_IS_CHARGED_IN_USDT_SO_BTC_STAYS_IN_WHOLE_LOT_STEPS\",\"fee_rounding\":\"UP_TO_0.00000001\",\"fee_source\":{\"page_updated\":\"2026-01-06\",\"read_at\":\"2026-11-12\",\"row\":\"Regular user: 0.1% trading fee; 25% off when paid in BNB\",\"url\":\"https://www.binance.com/en/support/faq/how-to-calculate-binance-spot-trading-fees-e85d6e703b874674840122196b89780a\"},\"fill_price_rounding\":\"TO_0.00000001_AGAINST_THE_ORDER\",\"filters\":{\"notional\":\"NOTIONAL_MIN_AND_MAX_AT_THE_FILL_PRICE\",\"quantity\":\"LOT_SIZE_AND_MARKET_LOT_SIZE_(A_ZERO_MARKET_STEP_OR_MINIMUM_ADDS_NO_CONSTRAINT)\",\"read\":\"FROM_THE_INSTRUMENT_AT_THE_TRADE\"},\"gross_rounding\":\"A_BUY'S_UP_A_SELL'S_DOWN_TO_0.00000001\",\"id\":\"SPOT_COST_V1\",\"kind\":\"SPOT_COST\",\"orders\":\"MARKET_ONLY\",\"promotions\":\"NOT_APPLIED\",\"quantity_rounding\":\"DOWN_TO_THE_STEP\",\"slippage\":{\"adverse_bps\":\"1\",\"applied\":\"TO_THE_WALKED_AVERAGE_PRICE\",\"label\":\"SCENARIO_NOT_OBSERVED\"},\"source\":\"ExecPlan 0060 section 4.3; Binance's spot fee page read on 2026-11-12 (section 7)\",\"status\":\"PROPOSED\",\"taker_fee_rate\":\"0.001\",\"version\":1}", "ae7f8a3610dc13d7e907cc6b47e320c8e4d9645631ec8c63f4cb6be822d2ae05"]
"""


def definition_rows():
    """The frozen ``SPOT_RULE_V1``, ``SPOT_POLICY_V1`` and ``SPOT_COST_V1``, each checked against its own hash."""
    rows = []
    for line in SPOT_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KINDS_ADDED:
            raise RuntimeError("frozen spot definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    if [row["kind"] for row in rows] != list(KINDS_ADDED):
        raise RuntimeError("frozen spot definitions are incomplete")
    return rows


MARKET_SQL = """
CREATE TABLE spot_instruments (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    symbol varchar(12) NOT NULL CHECK (symbol = 'BTCUSDT'),
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    status varchar(24) NOT NULL,
    usable boolean NOT NULL,
    -- A market order's filters, as app.spot_market.market combines LOT_SIZE, MARKET_LOT_SIZE and NOTIONAL.
    tick_size numeric NOT NULL CHECK (tick_size > 0),
    step_size numeric NOT NULL CHECK (step_size > 0),
    min_qty numeric NOT NULL CHECK (min_qty >= 0),
    max_qty numeric NOT NULL CHECK (max_qty > 0 AND max_qty >= min_qty),
    min_notional numeric NOT NULL CHECK (min_notional >= 0),
    max_notional numeric CHECK (max_notional > 0),
    document jsonb NOT NULL CHECK (jsonb_typeof(document) = 'object'),
    checked_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE TABLE spot_quotes (
    second_at timestamptz PRIMARY KEY,
    update_id bigint NOT NULL,
    bid numeric(38,8) NOT NULL CHECK (bid > 0),
    bid_qty numeric(38,8) NOT NULL CHECK (bid_qty > 0),
    ask numeric(38,8) NOT NULL CHECK (ask > bid),
    ask_qty numeric(38,8) NOT NULL CHECK (ask_qty > 0),
    -- The ten best levels of each side as [price, quantity] decimal strings, best first.
    bids jsonb NOT NULL CHECK (CASE WHEN jsonb_typeof(bids) = 'array'
        THEN jsonb_array_length(bids) BETWEEN 1 AND 20 ELSE false END),
    asks jsonb NOT NULL CHECK (CASE WHEN jsonb_typeof(asks) = 'array'
        THEN jsonb_array_length(asks) BETWEEN 1 AND 20 ELSE false END),
    received_at timestamptz NOT NULL,
    connection_id uuid NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_quote_second CHECK (date_trunc('second', received_at) = second_at)
);
CREATE TABLE spot_bars (
    open_ms bigint PRIMARY KEY CHECK (open_ms >= 0 AND open_ms % 60000 = 0),
    open numeric(38,8) NOT NULL CHECK (open > 0),
    high numeric(38,8) NOT NULL,
    low numeric(38,8) NOT NULL CHECK (low > 0),
    close numeric(38,8) NOT NULL CHECK (close > 0),
    volume numeric NOT NULL CHECK (volume >= 0),
    quote_volume numeric NOT NULL CHECK (quote_volume >= 0),
    trades bigint NOT NULL CHECK (trades >= 0),
    final boolean NOT NULL,
    source varchar(8) NOT NULL CHECK (source IN ('STREAM','REST')),
    event_at timestamptz,
    received_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_bar_range CHECK (high >= greatest(open, close) AND low <= least(open, close))
);
CREATE TABLE spot_daily_bars (
    open_ms bigint PRIMARY KEY CHECK (open_ms >= 0 AND open_ms % 86400000 = 0),
    open numeric(38,8) NOT NULL CHECK (open > 0),
    high numeric(38,8) NOT NULL,
    low numeric(38,8) NOT NULL CHECK (low > 0),
    close numeric(38,8) NOT NULL CHECK (close > 0),
    volume numeric NOT NULL CHECK (volume >= 0),
    quote_volume numeric NOT NULL CHECK (quote_volume >= 0),
    trades bigint NOT NULL CHECK (trades >= 0),
    received_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_daily_bar_range CHECK (high >= greatest(open, close) AND low <= least(open, close))
);
CREATE TABLE spot_feed_state (
    id smallint PRIMARY KEY CHECK (id = 1),
    status varchar(16) NOT NULL DEFAULT 'STARTING'
        CHECK (status IN ('STARTING','CONNECTED','DEGRADED','UNAVAILABLE')),
    reason varchar(80),
    stream_connected boolean NOT NULL DEFAULT false,
    last_quote_at timestamptz,
    last_bar_at timestamptz,
    clock_verified boolean NOT NULL DEFAULT false,
    clock_offset_ms numeric,
    clock_uncertainty_ms numeric,
    clock_checked_at timestamptz,
    instrument_id bigint REFERENCES spot_instruments(id),
    instrument_checked_at timestamptz,
    history_checked_at timestamptz,
    daily_checked_at timestamptz,
    heartbeat_at timestamptz,
    updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
INSERT INTO spot_feed_state (id) VALUES (1);
CREATE TABLE spot_feed_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code varchar(48) NOT NULL,
    at timestamptz NOT NULL,
    detail jsonb NOT NULL DEFAULT '{}',
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX spot_feed_events_at ON spot_feed_events (at);
"""

ACCOUNT_SQL = """
CREATE TABLE spot_runs (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    rule_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    rule_sha256 varchar(64) NOT NULL CHECK (rule_sha256 ~ '^[0-9a-f]{64}$'),
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
    CONSTRAINT spot_run_stopped CHECK ((state = 'STOPPED') = (stopped_at IS NOT NULL)),
    CONSTRAINT spot_run_stop_reason CHECK (state NOT IN ('STOPPING','STOPPED') OR stop_reason IS NOT NULL),
    CONSTRAINT spot_run_starter CHECK ((started_by = 'OWNER') = (request_id IS NOT NULL)),
    CONSTRAINT spot_run_causes CHECK ((state <> 'PAUSED' OR cardinality(causes) > 0)
        AND (state <> 'RUNNING' OR cardinality(causes) = 0))
);
CREATE UNIQUE INDEX spot_runs_one_live ON spot_runs ((true)) WHERE state <> 'STOPPED';

CREATE TABLE spot_owner_requests (
    id uuid PRIMARY KEY,
    kind varchar(8) NOT NULL CHECK (kind IN ('PAUSE','RESUME','STOP','START')),
    run_id uuid REFERENCES spot_runs(id),
    idempotency_key varchar(80) NOT NULL UNIQUE CHECK (idempotency_key ~ '^[A-Za-z0-9_-]{8,80}$'),
    request_hash varchar(64) NOT NULL CHECK (request_hash ~ '^[0-9a-f]{64}$'),
    status varchar(10) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','APPLIED','REJECTED')),
    reasons text[] NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    answered_at timestamptz,
    CONSTRAINT spot_request_answer CHECK ((status = 'PENDING') = (answered_at IS NULL)),
    CONSTRAINT spot_request_target CHECK ((kind = 'START') = (run_id IS NULL))
);
CREATE INDEX spot_owner_requests_pending ON spot_owner_requests (created_at) WHERE status = 'PENDING';
ALTER TABLE spot_runs ADD CONSTRAINT spot_runs_request_fkey
    FOREIGN KEY (request_id) REFERENCES spot_owner_requests(id);

CREATE TABLE spot_run_events (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES spot_runs(id),
    kind varchar(32) NOT NULL,
    actor varchar(8) NOT NULL CHECK (actor IN ('SYSTEM','OWNER')),
    request_id uuid REFERENCES spot_owner_requests(id),
    at timestamptz NOT NULL,
    detail jsonb NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(detail) = 'object'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_event_owner CHECK (actor = 'SYSTEM' OR request_id IS NOT NULL)
);
CREATE INDEX spot_run_events_run ON spot_run_events (run_id, id);

-- One market order's simulated fill: the rule's buy or sell, or a stopping run's sell of everything.
CREATE TABLE spot_fills (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    run_id uuid NOT NULL REFERENCES spot_runs(id),
    reason varchar(9) NOT NULL CHECK (reason IN ('RULE_BUY','RULE_SELL','STOP_SELL')),
    side varchar(4) NOT NULL CHECK (side IN ('BUY','SELL')),
    quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
    price numeric(38,8) NOT NULL CHECK (price > 0),
    average_price numeric NOT NULL CHECK (average_price > 0),
    slippage_bps numeric NOT NULL CHECK (slippage_bps >= 0),
    gross numeric(38,8) NOT NULL CHECK (gross > 0),
    fee numeric(38,8) NOT NULL CHECK (fee >= 0),
    fee_rate numeric NOT NULL CHECK (fee_rate >= 0 AND fee_rate < 1),
    fee_asset varchar(5) NOT NULL DEFAULT 'USDT' CHECK (fee_asset = 'USDT'),
    levels jsonb NOT NULL CHECK (jsonb_typeof(levels) = 'array'),
    quote_second timestamptz NOT NULL,
    instrument_id bigint NOT NULL REFERENCES spot_instruments(id),
    cash_after numeric(38,8) NOT NULL CHECK (cash_after >= 0),
    quantity_after numeric(38,8) NOT NULL CHECK (quantity_after >= 0),
    account_version bigint NOT NULL CHECK (account_version > 0),
    filled_at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_fill_side CHECK ((reason = 'RULE_BUY') = (side = 'BUY'))
);
CREATE INDEX spot_fills_filled ON spot_fills (filled_at DESC, seq DESC);

CREATE TABLE spot_valuations (
    id uuid PRIMARY KEY,
    run_id uuid REFERENCES spot_runs(id),
    valued_at timestamptz NOT NULL,
    purpose varchar(16) NOT NULL CHECK (purpose IN ('START','FILL','PERIODIC','HOURLY','DAILY_REFERENCE',
        'HIGH_WATER','LATCH','STOP','ACCOUNT_CHANGE')),
    cash numeric(38,8) NOT NULL,
    quantity numeric(38,8) NOT NULL CHECK (quantity >= 0),
    bid numeric(38,8) CHECK (bid > 0),
    bid_second timestamptz,
    equity numeric(38,8),
    units numeric(72,36) NOT NULL,
    nav numeric(72,36),
    quality varchar(8) NOT NULL CHECK (quality IN ('VALID','INVALID')),
    reason varchar(48),
    account_version bigint NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_valuation_quality CHECK ((quality = 'VALID') = (equity IS NOT NULL AND nav IS NOT NULL)),
    CONSTRAINT spot_valuation_bid CHECK (quantity = 0 OR quality = 'INVALID'
        OR (bid IS NOT NULL AND bid_second IS NOT NULL))
);
CREATE INDEX spot_valuations_valued ON spot_valuations (valued_at DESC);

CREATE TABLE spot_daily_references (
    utc_date date PRIMARY KEY,
    valuation_id uuid NOT NULL REFERENCES spot_valuations(id),
    nav numeric(72,36) NOT NULL CHECK (nav > 0),
    quality varchar(20) NOT NULL CHECK (quality IN ('TIMELY','LATE_CONSERVATIVE')),
    lateness_ms bigint NOT NULL CHECK (lateness_ms >= 0),
    basis jsonb NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE spot_latches (
    id uuid PRIMARY KEY,
    run_id uuid NOT NULL REFERENCES spot_runs(id),
    cause varchar(12) NOT NULL CHECK (cause IN ('DAILY_LOSS','DRAWDOWN')),
    latched_at timestamptz NOT NULL,
    valuation_id uuid NOT NULL REFERENCES spot_valuations(id),
    trigger jsonb NOT NULL,
    resolved_at timestamptz,
    resolution jsonb,
    CONSTRAINT spot_latch_resolution CHECK ((resolved_at IS NULL) = (resolution IS NULL))
);
CREATE UNIQUE INDEX spot_latches_open ON spot_latches (run_id, cause) WHERE resolved_at IS NULL;

-- The rule's daily readings: at most one that spent its UTC day per run; one a day per outcome, reason and codes
-- for a day not readable yet or refused.
CREATE TABLE spot_rule_readings (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    run_id uuid NOT NULL REFERENCES spot_runs(id),
    utc_date date NOT NULL,
    day_open_ms bigint NOT NULL CHECK (day_open_ms >= 0 AND day_open_ms % 86400000 = 0),
    at timestamptz NOT NULL,
    rule_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    rule_sha256 varchar(64) NOT NULL CHECK (rule_sha256 ~ '^[0-9a-f]{64}$'),
    result varchar(6) NOT NULL CHECK (result IN ('LONG','CASH','WARMUP')),
    reason varchar(32),
    close numeric(38,8) CHECK (close > 0),
    signal numeric CHECK (signal >= -1 AND signal <= 1),
    volatility numeric CHECK (volatility >= 0),
    target numeric CHECK (target >= 0 AND target <= 1),
    held numeric CHECK (held >= 0),
    action varchar(9) CHECK (action IN ('BUY','SELL','SELL_ALL','NO_CHANGE')),
    outcome varchar(12) NOT NULL CHECK (outcome IN ('NOT_READABLE','NO_CHANGE','FILLED','REFUSED')),
    codes text[] NOT NULL DEFAULT '{}',
    spent boolean NOT NULL,
    fill_id uuid UNIQUE REFERENCES spot_fills(id),
    features jsonb NOT NULL CHECK (jsonb_typeof(features) = 'object'),
    detail jsonb NOT NULL DEFAULT '{}' CHECK (jsonb_typeof(detail) = 'object'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CONSTRAINT spot_rule_reading_day CHECK (
        day_open_ms = (extract(epoch FROM (utc_date::timestamp AT TIME ZONE 'UTC')) * 1000)::bigint - 86400000),
    CONSTRAINT spot_rule_reading_shape CHECK (CASE outcome
        WHEN 'NOT_READABLE' THEN result = 'WARMUP' AND NOT spent AND action IS NULL AND fill_id IS NULL
            AND cardinality(codes) = 0
        WHEN 'NO_CHANGE' THEN result <> 'WARMUP' AND spent AND action = 'NO_CHANGE' AND fill_id IS NULL
            AND cardinality(codes) = 0
        WHEN 'FILLED' THEN result <> 'WARMUP' AND spent AND action IN ('BUY','SELL','SELL_ALL')
            AND fill_id IS NOT NULL AND cardinality(codes) = 0
        ELSE result <> 'WARMUP' AND NOT spent AND fill_id IS NULL AND cardinality(codes) > 0
            AND (action IN ('BUY','SELL','SELL_ALL') OR (action IS NULL AND held IS NULL))
        END),
    CONSTRAINT spot_rule_reading_values CHECK (result = 'WARMUP' OR (close IS NOT NULL AND signal IS NOT NULL
        AND volatility IS NOT NULL AND target IS NOT NULL AND (held IS NOT NULL OR outcome = 'REFUSED')))
);
CREATE UNIQUE INDEX spot_rule_readings_spent ON spot_rule_readings (run_id, utc_date) WHERE spent;
CREATE INDEX spot_rule_readings_run ON spot_rule_readings (run_id, utc_date, seq);
CREATE INDEX spot_rule_readings_at ON spot_rule_readings (at DESC, seq DESC);

-- The rule's backtest on the stored daily candles (SPOT_BACKTEST_V1): one row per computation. Only the newest
-- row keeps its daily series; an older one's is cleared, its summaries stay.
CREATE TABLE spot_backtests (
    id uuid PRIMARY KEY,
    seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    computed_at timestamptz NOT NULL,
    method varchar(24) NOT NULL CHECK (method = 'SPOT_BACKTEST_V1'),
    label varchar(32) NOT NULL CHECK (label = 'BACKTEST_MODELED_NOT_FILLED'),
    rule_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    rule_sha256 varchar(64) NOT NULL CHECK (rule_sha256 ~ '^[0-9a-f]{64}$'),
    policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    cost_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
    cost_sha256 varchar(64) NOT NULL CHECK (cost_sha256 ~ '^[0-9a-f]{64}$'),
    code_identity varchar(64) NOT NULL CHECK (code_identity ~ '^[0-9a-f]{64}$'),
    first_day_ms bigint NOT NULL CHECK (first_day_ms >= 0 AND first_day_ms % 86400000 = 0),
    last_day_ms bigint NOT NULL CHECK (last_day_ms >= first_day_ms AND last_day_ms % 86400000 = 0),
    days integer NOT NULL CHECK (days > 0),
    candles_sha256 varchar(64) NOT NULL CHECK (candles_sha256 ~ '^[0-9a-f]{64}$'),
    result jsonb NOT NULL CHECK (jsonb_typeof(result) = 'object'),
    series jsonb CHECK (series IS NULL OR jsonb_typeof(series) = 'object'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
);
CREATE UNIQUE INDEX spot_backtests_input ON spot_backtests (rule_sha256, policy_sha256, cost_sha256, code_identity,
    last_day_ms, candles_sha256);
"""

GUARDS_SQL = """
CREATE FUNCTION asl_spot_append_only() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN RAISE EXCEPTION 'append-only spot record'; END $$;

-- A book row: never changed; deleted only once two days old (the feed's retention).
CREATE FUNCTION asl_spot_quote_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN RAISE EXCEPTION 'spot book record is immutable'; END IF;
    IF OLD.second_at > clock_timestamp() - interval '2 days' THEN
        RAISE EXCEPTION 'spot book record is within retention'; END IF;
    RETURN OLD;
END $$;

-- A 1-minute candle: an open one is replaced until it is final, a final one never changes; deleted only once 30
-- days old (the feed's retention, for the chart).
CREATE FUNCTION asl_spot_bar_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        IF OLD.open_ms > (extract(epoch FROM clock_timestamp()) * 1000)::bigint - 30 * 86400000::bigint THEN
            RAISE EXCEPTION 'spot candle is within retention'; END IF;
        RETURN OLD;
    END IF;
    IF OLD.final THEN RAISE EXCEPTION 'final spot candle is immutable'; END IF;
    IF NEW.open_ms <> OLD.open_ms THEN RAISE EXCEPTION 'spot candle identity is immutable'; END IF;
    RETURN NEW;
END $$;

-- A run: its identity and start never change; a stopped run never changes; its high-water NAV never falls; a
-- stopping run never runs again.
CREATE FUNCTION asl_spot_run_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.state = 'STOPPED' THEN RAISE EXCEPTION 'stopped spot run cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['state','causes','high_water_nav','stopped_at','stop_reason','version'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['state','causes','high_water_nav','stopped_at','stop_reason',
            'version']) THEN
        RAISE EXCEPTION 'spot run identity is immutable'; END IF;
    IF NEW.high_water_nav < OLD.high_water_nav THEN RAISE EXCEPTION 'run high-water NAV cannot decrease'; END IF;
    IF OLD.state = 'STOPPING' AND NEW.state IN ('RUNNING','PAUSED') THEN
        RAISE EXCEPTION 'a stopping spot run cannot resume'; END IF;
    RETURN NEW;
END $$;

-- An owner request is answered once by the engine; nothing else of it changes.
CREATE FUNCTION asl_spot_request_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.status <> 'PENDING' THEN RAISE EXCEPTION 'answered owner request cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['status','reasons','answered_at'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','reasons','answered_at']) THEN
        RAISE EXCEPTION 'owner request is immutable'; END IF;
    RETURN NEW;
END $$;

-- A latch is resolved once.
CREATE FUNCTION asl_spot_latch_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF OLD.resolved_at IS NOT NULL THEN RAISE EXCEPTION 'resolved latch cannot change'; END IF;
    IF (to_jsonb(NEW) - ARRAY['resolved_at','resolution'])
            IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['resolved_at','resolution']) THEN
        RAISE EXCEPTION 'latch identity is immutable'; END IF;
    RETURN NEW;
END $$;

-- A backtest's record never changes but for its daily series, which is cleared once a newer row has one.
CREATE FUNCTION asl_spot_backtest_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF NEW.series IS NOT NULL OR (to_jsonb(NEW) - 'series') IS DISTINCT FROM (to_jsonb(OLD) - 'series') THEN
        RAISE EXCEPTION 'a spot backtest only clears its series'; END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER spot_quotes_guard BEFORE UPDATE OR DELETE ON spot_quotes
    FOR EACH ROW EXECUTE FUNCTION asl_spot_quote_guard();
CREATE TRIGGER spot_bars_guard BEFORE UPDATE OR DELETE ON spot_bars
    FOR EACH ROW EXECUTE FUNCTION asl_spot_bar_guard();
CREATE TRIGGER spot_runs_guard BEFORE UPDATE ON spot_runs
    FOR EACH ROW EXECUTE FUNCTION asl_spot_run_guard();
CREATE TRIGGER spot_owner_requests_guard BEFORE UPDATE ON spot_owner_requests
    FOR EACH ROW EXECUTE FUNCTION asl_spot_request_guard();
CREATE TRIGGER spot_latches_guard BEFORE UPDATE ON spot_latches
    FOR EACH ROW EXECUTE FUNCTION asl_spot_latch_guard();
CREATE TRIGGER spot_backtests_guard BEFORE UPDATE ON spot_backtests
    FOR EACH ROW EXECUTE FUNCTION asl_spot_backtest_guard();
"""

APPEND_ONLY = ("spot_instruments", "spot_daily_bars", "spot_feed_events", "spot_run_events", "spot_fills",
               "spot_valuations", "spot_daily_references", "spot_rule_readings")
NO_DELETE = ("spot_feed_state", "spot_runs", "spot_owner_requests", "spot_latches", "spot_backtests")

GRANTS_SQL = """
GRANT SELECT, INSERT ON spot_instruments, spot_quotes, spot_bars, spot_daily_bars, spot_feed_events
    TO asl_market_worker;
GRANT DELETE ON spot_quotes, spot_bars TO asl_market_worker;
GRANT UPDATE (open, high, low, close, volume, quote_volume, trades, final, source, event_at, received_at)
    ON spot_bars TO asl_market_worker;
GRANT SELECT ON spot_feed_state TO asl_market_worker;
GRANT UPDATE (status, reason, stream_connected, last_quote_at, last_bar_at, clock_verified, clock_offset_ms,
    clock_uncertainty_ms, clock_checked_at, instrument_id, instrument_checked_at, history_checked_at,
    daily_checked_at, heartbeat_at, updated_at) ON spot_feed_state TO asl_market_worker;
GRANT USAGE, SELECT ON SEQUENCE spot_instruments_id_seq, spot_feed_events_id_seq TO asl_market_worker;

GRANT SELECT ON spot_instruments, spot_quotes, spot_bars, spot_daily_bars, spot_feed_state TO asl_execution;
GRANT SELECT, INSERT ON spot_runs, spot_run_events, spot_fills, spot_valuations, spot_daily_references,
    spot_latches, spot_rule_readings, spot_backtests TO asl_execution;
GRANT SELECT ON spot_owner_requests TO asl_execution;
GRANT UPDATE (state, causes, high_water_nav, stopped_at, stop_reason, version) ON spot_runs TO asl_execution;
GRANT UPDATE (status, reasons, answered_at) ON spot_owner_requests TO asl_execution;
GRANT UPDATE (resolved_at, resolution) ON spot_latches TO asl_execution;
GRANT UPDATE (series) ON spot_backtests TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE spot_runs_seq_seq, spot_run_events_id_seq, spot_fills_seq_seq,
    spot_rule_readings_seq_seq, spot_backtests_seq_seq TO asl_execution;

GRANT SELECT ON spot_instruments, spot_quotes, spot_bars, spot_daily_bars, spot_feed_state, spot_feed_events,
    spot_runs, spot_owner_requests, spot_run_events, spot_fills, spot_valuations, spot_daily_references,
    spot_latches, spot_rule_readings, spot_backtests TO asl_api;
GRANT INSERT (id, kind, run_id, idempotency_key, request_hash) ON spot_owner_requests TO asl_api;
"""

JOURNAL_SQL = """
ALTER TABLE journal_transactions ADD COLUMN spot_fill_id uuid UNIQUE REFERENCES spot_fills(id);
ALTER TABLE journal_transactions DROP CONSTRAINT journal_single_source,
    ADD CONSTRAINT journal_single_source
    CHECK (num_nonnulls(funding_request_id, fill_id, futures_event_id, spot_fill_id) = 1);

CREATE OR REPLACE FUNCTION asl_journal_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user = 'asl_api' AND NEW.funding_request_id IS NOT NULL AND NEW.fill_id IS NULL
        AND NEW.futures_event_id IS NULL AND NEW.spot_fill_id IS NULL THEN RETURN NEW; END IF;
    -- ExecPlan 0060: a spot fill, from the execution identity alone. The retired sources (M3's spot fills and the
    -- futures account's events) take no new transaction.
    IF current_user = 'asl_execution' AND NEW.spot_fill_id IS NOT NULL AND NEW.funding_request_id IS NULL
        AND NEW.fill_id IS NULL AND NEW.futures_event_id IS NULL THEN RETURN NEW; END IF;
    RAISE EXCEPTION 'journal source not permitted for this role';
END $$;

CREATE OR REPLACE FUNCTION asl_posting_source_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE header record;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    SELECT funding_request_id, spot_fill_id, created_txid INTO header
        FROM journal_transactions WHERE id = NEW.tx_id;
    IF NOT FOUND OR header.created_txid IS DISTINCT FROM
            ((pg_current_xact_id())::text)::bigint THEN
        RAISE EXCEPTION 'postings must be written with their journal header';
    END IF;
    IF current_user = 'asl_api' AND header.funding_request_id IS NOT NULL THEN RETURN NEW; END IF;
    IF current_user = 'asl_execution' AND header.spot_fill_id IS NOT NULL THEN RETURN NEW; END IF;
    RAISE EXCEPTION 'posting source not permitted for this role';
END $$;
"""

# 0020's guards, which 0040 had: restored by the downgrade.
JOURNAL_DOWN_SQL = """
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

ALTER TABLE journal_transactions DROP CONSTRAINT journal_single_source,
    ADD CONSTRAINT journal_single_source CHECK (num_nonnulls(funding_request_id, fill_id, futures_event_id) = 1);
ALTER TABLE journal_transactions DROP COLUMN spot_fill_id;
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def _ident(name: str) -> str:
    if not name or len(name) > 63 or '"' in name:
        raise RuntimeError(f"unexpected object name {name!r}")
    return '"' + name + '"'


def _kinds(kinds) -> None:
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(kinds)})")


def _refuse_unless_flat(bind) -> None:
    """The futures account must be flat, with nothing reserved (ExecPlan 0060 section 4.7)."""
    found = bind.exec_driver_sql(
        "SELECT (SELECT count(*) FROM futures_positions WHERE state = 'OPEN'), "
        "(SELECT count(*) FROM futures_funding WHERE status = 'PENDING'), "
        "(SELECT count(*) FROM reservations WHERE status = 'ACTIVE'), "
        "(SELECT reserved FROM account_state WHERE id = 1), "
        "(SELECT count(*) FROM account_holdings WHERE reserved <> 0)").one()
    reasons = [text for text, bad in (
        ("a futures position is open", found[0] > 0), ("a futures funding payment is pending", found[1] > 0),
        ("a reservation is active", found[2] > 0), ("cash is reserved", found[3] != 0),
        ("a coin is reserved", found[4] > 0)) if bad]
    if reasons:
        raise RuntimeError("the futures account is not flat (" + "; ".join(reasons)
                           + "): stop and close it in Settings, then update again; nothing changed")


def _retire_futures_run(bind, rows) -> None:
    """A live futures run ends as SYSTEM, as 0059's switch ended run #1 (ExecPlan 0060 section 4.7)."""
    hashes = {row["id"]: row["sha256"] for row in rows}
    run = bind.exec_driver_sql(
        "SELECT id, policy_id, state, stop_reason FROM futures_runs WHERE state <> 'STOPPED' "
        "ORDER BY seq DESC LIMIT 1").mappings().first()
    bind.exec_driver_sql(
        "UPDATE futures_owner_requests SET status = 'REJECTED', reasons = ARRAY['FUTURES_RETIRED'], "
        "answered_at = clock_timestamp() WHERE status = 'PENDING'")
    if run is None:
        return
    detail = {"stop_reason": run["stop_reason"] or "NEW_POLICY", "replaced": run["policy_id"],
              "policy": "SPOT_POLICY_V1", "policy_sha256": hashes["SPOT_POLICY_V1"],
              "rule": "SPOT_RULE_V1", "rule_sha256": hashes["SPOT_RULE_V1"],
              "cost": "SPOT_COST_V1", "cost_sha256": hashes["SPOT_COST_V1"], "plan": "ExecPlan 0060"}
    bind.exec_driver_sql(
        "UPDATE futures_latches SET resolved_at = clock_timestamp(), resolution = CAST(%(resolution)s AS jsonb) "
        "WHERE run_id = %(run)s AND resolved_at IS NULL",
        {"run": run["id"], "resolution": json.dumps({"rule": "RUN_STOPPED", "stop_reason": detail["stop_reason"]})})
    bind.exec_driver_sql(
        "UPDATE futures_runs SET state = 'STOPPED', stopped_at = clock_timestamp(), "
        "stop_reason = COALESCE(stop_reason, 'NEW_POLICY'), version = version + 1 WHERE id = %(run)s",
        {"run": run["id"]})
    for kind, payload in (("FUTURES_RETIRED", detail), ("STOPPED", {"stop_reason": detail["stop_reason"]})):
        bind.exec_driver_sql(
            "INSERT INTO futures_run_events (run_id, kind, actor, at, detail) "
            "VALUES (%(run)s, %(kind)s, 'SYSTEM', clock_timestamp(), CAST(%(detail)s AS jsonb))",
            {"run": run["id"], "kind": kind, "detail": json.dumps(payload, sort_keys=True)})


def _archive(bind) -> None:
    """Every table of ``public`` but ``KEPT``, its sequences with it, and the read schemas' views, into
    ``archive``; each move recorded for the downgrade."""
    op.execute("CREATE SCHEMA archive")
    op.execute("REVOKE ALL ON SCHEMA archive FROM PUBLIC")
    op.execute("CREATE TABLE archive.moved_objects (seq integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY, "
               "kind varchar(8) NOT NULL CHECK (kind IN ('TABLE','SEQUENCE','VIEW','MATVIEW')), "
               "from_schema name NOT NULL, from_name name NOT NULL, to_name name NOT NULL, "
               "moved_at timestamptz NOT NULL DEFAULT clock_timestamp())")

    def record(kind: str, schema: str, name: str, new: str) -> None:
        bind.exec_driver_sql("INSERT INTO archive.moved_objects (kind, from_schema, from_name, to_name) "
                             "VALUES (%(kind)s, %(schema)s, %(name)s, %(new)s)",
                             {"kind": kind, "schema": schema, "name": name, "new": new})

    tables = bind.exec_driver_sql(
        "SELECT relname FROM pg_class WHERE relnamespace = 'public'::regnamespace AND relkind IN ('r','p') "
        "ORDER BY relname").scalars().all()
    for name in tables:
        if name in KEPT:
            continue
        op.execute(f"ALTER TABLE public.{_ident(name)} SET SCHEMA archive")
        record("TABLE", "public", name, name)
    # A sequence no kept table owns (an owned one moved with its table).
    sequences = bind.exec_driver_sql(
        "SELECT c.relname FROM pg_class c WHERE c.relnamespace = 'public'::regnamespace AND c.relkind = 'S' "
        "AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.objid = c.oid AND d.classid = 'pg_class'::regclass "
        "AND d.refclassid = 'pg_class'::regclass AND d.deptype IN ('a','i')) ORDER BY c.relname").scalars().all()
    for name in sequences:
        op.execute(f"ALTER SEQUENCE public.{_ident(name)} SET SCHEMA archive")
        record("SEQUENCE", "public", name, name)
    views = bind.exec_driver_sql(
        "SELECT n.nspname, c.relname, c.relkind::text FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = ANY(%(schemas)s) AND c.relkind IN ('v','m') ORDER BY n.nspname, c.relname",
        {"schemas": list(READ_SCHEMAS)}).all()
    for schema, name, relkind in views:
        new = f"{schema}__{name}"
        kind, word = ("VIEW", "VIEW") if relkind == "v" else ("MATVIEW", "MATERIALIZED VIEW")
        op.execute(f"ALTER {word} {_ident(schema)}.{_ident(name)} RENAME TO {_ident(new)}")
        op.execute(f"ALTER {word} {_ident(schema)}.{_ident(new)} SET SCHEMA archive")
        record(kind, schema, name, new)


def _unarchive(bind) -> None:
    moved = bind.exec_driver_sql(
        "SELECT kind, from_schema, from_name, to_name FROM archive.moved_objects ORDER BY seq DESC").all()
    for kind, schema, name, new in moved:
        if kind == "TABLE":
            op.execute(f"ALTER TABLE archive.{_ident(name)} SET SCHEMA public")
        elif kind == "SEQUENCE":
            op.execute(f"ALTER SEQUENCE archive.{_ident(name)} SET SCHEMA public")
        else:
            word = "VIEW" if kind == "VIEW" else "MATERIALIZED VIEW"
            op.execute(f"ALTER {word} archive.{_ident(new)} SET SCHEMA {_ident(schema)}")
            op.execute(f"ALTER {word} {_ident(schema)}.{_ident(new)} RENAME TO {_ident(name)}")
    op.execute("DROP TABLE archive.moved_objects")
    op.execute("DROP SCHEMA archive")


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    rows = definition_rows()
    _refuse_unless_flat(bind)
    _retire_futures_run(bind, rows)
    _kinds((*DEFINITION_KINDS, *KINDS_ADDED))
    for row in rows:
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    _archive(bind)
    op.execute(MARKET_SQL)
    op.execute(ACCOUNT_SQL)
    op.execute(GUARDS_SQL.replace("{path}", SEARCH_PATH))
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_append_only BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_spot_append_only()")
    for table in NO_DELETE:
        op.execute(f"CREATE TRIGGER {table}_no_delete BEFORE DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_spot_append_only()")
    op.execute(GRANTS_SQL)
    op.execute(JOURNAL_SQL.replace("{path}", SEARCH_PATH))
    op.execute("INSERT INTO account_holdings (asset, quantity, reserved) VALUES ('BTC', 0, 0) "
               "ON CONFLICT (asset) DO NOTHING")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    if bind.exec_driver_sql("SELECT count(*) FROM spot_fills").scalar_one():
        raise RuntimeError("a spot fill exists; downgrade refused; fix forward or restore the backup")
    if bind.exec_driver_sql("SELECT count(*) FROM journal_transactions WHERE spot_fill_id IS NOT NULL").scalar_one():
        raise RuntimeError("a spot journal transaction exists; downgrade refused")
    op.execute(JOURNAL_DOWN_SQL.replace("{path}", SEARCH_PATH))
    op.execute("ALTER TABLE spot_runs DROP CONSTRAINT spot_runs_request_fkey")
    for table in reversed(MARKET_TABLES + ACCOUNT_TABLES):
        op.execute(f"DROP TABLE {table}")
    for function in ("asl_spot_append_only", "asl_spot_quote_guard", "asl_spot_bar_guard", "asl_spot_run_guard",
                     "asl_spot_request_guard", "asl_spot_latch_guard", "asl_spot_backtest_guard"):
        op.execute(f"DROP FUNCTION {function}()")
    _unarchive(bind)
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen rows, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in definition_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("spot definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    _kinds(DEFINITION_KINDS)
