"""M3 paper broker, risk state, mandates, protection and execution authority.

Revision ID: 0005_m3_paper_broker
Revises: 0004_m2_completion

Forward-only. Market tables are not altered. The execution identity is created
NOLOGIN: enabling it on the owner database is an M4 activation step.
"""

import json
import os

from psycopg import sql

from alembic import op

revision = "0005_m3_paper_broker"
down_revision = "0004_m2_completion"
branch_labels = None
depends_on = None

# Canonical definitions (id, kind, version, status, canonical JSON, SHA-256) as
# produced by app.execution.definitions.seed_rows() when this revision was written.
SEED_LINES = r"""
["PAPER_PILOT_V1", "RISK_POLICY", 1, "PROPOSED", "{\"aggregate_open_risk_fraction\":\"0.005\",\"borrowing\":false,\"comparisons\":\"INCLUSIVE\",\"cost_reserve_per_unit\":\"P_MAX_X_R_PLUS_STOP_X_R_PLUS_SLIP_PLUS_TICK\",\"daily_loss_trigger_fraction\":\"0.02\",\"daily_reference\":{\"late_rule\":\"MAX_OF_LAST_VALID_NAV_PRIOR_24H_AND_FIRST_POST_MIDNIGHT_NAV\",\"missing_rule\":\"BLOCK_NEW_ENTRIES\",\"timeliness_ms\":300000,\"timezone\":\"UTC\"},\"direction\":\"SPOT_LONG_ONLY\",\"drawdown_trigger_fraction\":\"0.08\",\"id\":\"PAPER_PILOT_V1\",\"kind\":\"RISK_POLICY\",\"latch_clearing\":\"OWNER_RESUME_M4_ONLY\",\"latch_effect\":\"BLOCK_ENTRIES_CANCEL_PENDING_ENTRIES_EXITS_CONTINUE\",\"passive_breach\":\"RECORD_BLOCK_NEW_EXPOSURE_NO_FORCED_EXIT\",\"per_asset_notional_fraction\":\"0.25\",\"per_position_risk_fraction\":\"0.0025\",\"planned_open_risk\":\"NET_QTY_X_MAX0_AVG_COST_MINUS_STOP_PLUS_NET_QTY_X_EXIT_RESERVE\",\"positions_per_symbol\":1,\"pyramiding\":false,\"quote_max_age_ms\":5000,\"source\":\"docs/RISK_POLICY.md PAPER_PILOT_V1 with ExecPlan 0011 interpretation fields\",\"status\":\"PROPOSED\",\"total_crypto_notional_fraction\":\"0.50\",\"universe\":[\"BTCUSDT\",\"SOLUSDT\"],\"valuation_policy\":\"VALUATION_BID_V1\",\"version\":1}", "25ba32b51808c0b13178c1fb551d782f90913d4e795e36906cc222e4bb6277d2"]
["TREND_REFERENCE_V1", "STRATEGY", 1, "PROPOSED", "{\"atr_method\":\"WILDER\",\"atr_period\":14,\"atr_seed\":\"MEAN_OF_FIRST_14_TRUE_RANGES_FROM_SECOND_BAR\",\"bars\":\"FINALIZED_ONLY_AVAILABLE_AT_DECISION\",\"checkpoint\":{\"max_wait_ms\":60000,\"priority\":[\"BTCUSDT\",\"SOLUSDT\"]},\"ema_seed\":\"SMA_OF_FIRST_COMPLETE_PERIOD\",\"entry\":\"PREV_FAST_LTE_SLOW_AND_CUR_FAST_GT_SLOW\",\"entry_reference\":\"SIGNAL_BAR_CLOSE\",\"entry_validity_ms\":600000,\"exit_precedence\":[\"PROTECTIVE_STOP\",\"TIME_EXIT\",\"TREND_EXIT\"],\"fast_ema\":20,\"gap_rule\":\"RESET_RUN_ON_MISSING_OR_UNCONFIRMED_HOUR\",\"id\":\"TREND_REFERENCE_V1\",\"kind\":\"STRATEGY\",\"late_bar\":\"INDICATORS_ONLY_SIGNAL_MISSED\",\"max_entry_attempts\":3,\"max_hold_seconds\":259200,\"policy_kind\":\"FIXED\",\"reentry\":\"NEW_UPWARD_CROSSING_ON_BAR_CLOSING_AFTER_POSITION_CLOSE\",\"retryable_expiry_reasons\":[\"NO_ELIGIBLE_QUOTE\",\"ZERO_LIQUIDITY\"],\"run_window_max_bars\":720,\"slow_ema\":50,\"source\":\"docs/STRATEGIES.md TREND_REFERENCE_V1 with ExecPlan 0011 execution settings\",\"status\":\"PROPOSED\",\"stop_atr_multiple\":\"2\",\"stop_policy\":\"ENGINE_TRIGGER_MARKET_EXIT_ON_BID\",\"time_exit\":\"FIRST_ELIGIBLE_OBSERVATION_AT_OR_AFTER_72H_FROM_FIRST_FILL\",\"timeframe\":\"1h\",\"trend_exit\":\"PREV_FAST_GTE_SLOW_AND_CUR_FAST_LT_SLOW\",\"universe\":[\"BTCUSDT\",\"SOLUSDT\"],\"version\":1,\"warmup_bars\":100}", "393a49502c0d5004f6c8b1342a2b3a566d714cbd09ef1ab57fafbb11f53e9e01"]
["PAPER_COST_V1", "COST_MODEL", 1, "PROPOSED", "{\"cash_rounding\":{\"buy_debit\":\"CEILING_8DP\",\"sell_proceeds\":\"FLOOR_8DP\"},\"commission\":{\"bnb_discount\":false,\"charged_in\":\"RECEIVED_ASSET\",\"liquidity\":\"TAKER\",\"rounding\":\"CEILING_TO_INSTRUMENT_COMMISSION_PRECISION\",\"source\":\"docs/REFERENCES.md#ex-04\"},\"execution_fidelity\":\"SAMPLED_L1_TICKER\",\"fill_price\":\"ADVERSE_SLIPPAGE_THEN_ADVERSE_TICK\",\"id\":\"PAPER_COST_V1\",\"kind\":\"COST_MODEL\",\"liquidity\":\"TOP_OF_BOOK_SINGLE_SNAPSHOT_IOC_WITH_LEVEL_DEPLETION\",\"parameters\":[\"taker_commission_rate\",\"arrival_delay_ms\",\"participation\",\"adverse_slippage_bps\",\"entry_envelope_bps\",\"entry_fill_window_ms\"],\"quantity_rounding\":\"FLOOR_TO_EFFECTIVE_STEP\",\"reservation\":\"QTY_X_ENVELOPE_PRICE_CEILING_8DP\",\"spread\":\"EXECUTABLE_SIDE_ONCE\",\"status\":\"PROPOSED\",\"unset_rule\":\"UNSET_BLOCKS_EVERY_NON_FIXTURE_ORDER_AND_FILL\",\"version\":1}", "9beb9aac8372dd778077a9b640cc28c284aaff374cb55c4ccb32cd49763b45b3"]
["COST_SCENARIO_HYPOTHETICAL_H1", "COST_SCENARIO", 1, "PROPOSED", "{\"adverse_slippage_bps\":\"1\",\"arrival_delay_ms\":1000,\"cost_model\":\"PAPER_COST_V1\",\"entry_envelope_bps\":\"20\",\"entry_fill_window_ms\":5000,\"id\":\"COST_SCENARIO_HYPOTHETICAL_H1\",\"kind\":\"COST_SCENARIO\",\"label\":\"HYPOTHETICAL: unsourced round sensitivity values; not Binance's schedule and not the owner's fee\",\"participation\":\"0.5\",\"status\":\"PROPOSED\",\"taker_commission_rate\":\"0.001\",\"version\":1}", "c3fe1259df180e1a4891c06eeb03d0e0bf2375e0cf43ba49a226f23ea09821a5"]
["COST_SCENARIO_HYPOTHETICAL_H2_STRESS", "COST_SCENARIO", 1, "PROPOSED", "{\"adverse_slippage_bps\":\"5\",\"arrival_delay_ms\":2000,\"cost_model\":\"PAPER_COST_V1\",\"entry_envelope_bps\":\"20\",\"entry_fill_window_ms\":5000,\"id\":\"COST_SCENARIO_HYPOTHETICAL_H2_STRESS\",\"kind\":\"COST_SCENARIO\",\"label\":\"HYPOTHETICAL STRESS: unsourced round sensitivity values; kept separate from H1\",\"participation\":\"0.25\",\"status\":\"PROPOSED\",\"taker_commission_rate\":\"0.002\",\"version\":1}", "eddc7ed3c48d333da65ea2a1fd2f94fa463651ca2950f3605b5a41743b77153a"]
["VALUATION_BID_V1", "VALUATION_POLICY", 1, "PROPOSED", "{\"equity_rounding\":\"FLOOR_8DP\",\"id\":\"VALUATION_BID_V1\",\"kind\":\"VALUATION_POLICY\",\"marks\":\"BEST_BID_OF_USABLE_QUOTE\",\"missing_mark\":\"VALUATION_INVALID\",\"nav_quantum\":\"1E-36_HALF_EVEN\",\"persist_every_ms\":60000,\"reference_sources\":\"FRESH_AT_PROCESSING_ONLY\",\"status\":\"PROPOSED\",\"version\":1}", "84c4a0fbc50be54b051c9724403951ee2be045db12a381f10cd1cd8aaf4071ab"]
["FILTER_POLICY_V1", "FILTER_POLICY", 1, "PROPOSED", "{\"applied\":[\"LOT_SIZE\",\"MARKET_LOT_SIZE\",\"MIN_NOTIONAL\",\"NOTIONAL\",\"PRICE_FILTER\",\"MAX_POSITION\",\"MAX_NUM_ORDERS\"],\"id\":\"FILTER_POLICY_V1\",\"kind\":\"FILTER_POLICY\",\"market_lot_size_zero_step_or_min\":\"NO_ADDITIONAL_CONSTRAINT_LOT_SIZE_APPLIES\",\"not_applicable\":[\"ICEBERG_PARTS\",\"MAX_NUM_ALGO_ORDERS\",\"MAX_NUM_ICEBERG_ORDERS\",\"MAX_NUM_ORDER_AMENDS\",\"MAX_NUM_ORDER_LISTS\",\"TRAILING_DELTA\"],\"not_modeled\":[\"PERCENT_PRICE\",\"PERCENT_PRICE_BY_SIDE\"],\"notional\":\"MIN_AND_MAX_APPLIED_TO_MARKET_ORDERS_AT_DECISION_EXECUTABLE_PRICE\",\"quantity\":\"ROUND_DOWN_MINIMUM_FAILURE_IS_NO_TRADE\",\"snapshots\":\"DECISION_AND_FILL_STRICTER_WINS\",\"source\":\"docs/REFERENCES.md#ex-03\",\"status\":\"PROPOSED\",\"unknown_filter\":\"INSTRUMENT_INELIGIBLE\",\"version\":1,\"zero_max\":\"INSTRUMENT_INELIGIBLE\"}", "00157b2619de4b23358dc351d15f6364c657e2b27032db9bdc155dc61fbdc023"]
"""

MODES = "('FORWARD_PAPER','OFFLINE_TEST','HISTORICAL_RESEARCH')"
SYMBOLS = "('BTCUSDT','SOLUSDT')"
ORDER_STATUSES = (
    "('PENDING_VALIDATION','ACCEPTED','PARTIALLY_FILLED','CANCEL_PENDING','REJECTED',"
    "'FILLED','CANCELED','EXPIRED','RECONCILIATION_REQUIRED')"
)
APPEND_ONLY = (
    "execution_definitions", "execution_steps", "execution_incidents", "strategy_evaluations",
    "signal_outcomes", "risk_decisions", "position_mandates", "position_events", "order_events",
    "fills", "valuations", "daily_references", "risk_latches", "risk_breach_events",
)
MODE_GUARDED = (
    "execution_steps", "execution_incidents", "strategy_evaluations", "risk_decisions",
    "position_mandates", "positions", "exit_obligations", "orders", "fills", "valuations",
    "daily_references", "risk_latches", "risk_breach_events", "execution_checkpoints",
)


def upgrade() -> None:
    # Bound DDL lock waits on a live owner database; the rollout stops writers first.
    op.execute("SET LOCAL lock_timeout = '10s'")
    op.execute(f"""
        CREATE TABLE execution_definitions (
            id varchar(64) PRIMARY KEY,
            kind varchar(24) NOT NULL CHECK (kind IN ('RISK_POLICY','STRATEGY','COST_MODEL',
                'COST_SCENARIO','VALUATION_POLICY','FILTER_POLICY')),
            version integer NOT NULL CHECK (version > 0),
            status varchar(16) NOT NULL CHECK (status IN ('PROPOSED','FIXTURE_ONLY')),
            definition jsonb NOT NULL,
            canonical text NOT NULL,
            sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE execution_lease (
            id smallint PRIMARY KEY CHECK (id = 1),
            owner_id uuid,
            epoch bigint NOT NULL DEFAULT 0 CHECK (epoch >= 0),
            expires_at timestamptz,
            CONSTRAINT execution_lease_authority UNIQUE (id, owner_id, epoch)
        );
        INSERT INTO execution_lease (id) VALUES (1);
        CREATE TABLE execution_checkpoints (
            mode varchar(24) PRIMARY KEY CHECK (mode IN {MODES}),
            last_sequence bigint NOT NULL DEFAULT 0 CHECK (last_sequence >= 0),
            last_step_at timestamptz,
            lease_epoch bigint,
            state jsonb NOT NULL DEFAULT '{{}}',
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE execution_steps (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            lease_epoch bigint NOT NULL,
            trigger_kind varchar(16) NOT NULL CHECK (trigger_kind IN ('PUBLICATION','TIMER','RECOVERY')),
            trigger_sequence bigint,
            decided_at timestamptz NOT NULL,
            watermark bigint NOT NULL CHECK (watermark >= 0),
            eligibility jsonb NOT NULL,
            outcome jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX execution_steps_time ON execution_steps(mode, decided_at);
        CREATE TABLE execution_incidents (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            code varchar(64) NOT NULL,
            symbol varchar(12) CHECK (symbol IS NULL OR symbol IN {SYMBOLS}),
            event varchar(8) NOT NULL CHECK (event IN ('START','END','POINT')),
            at timestamptz NOT NULL,
            detail jsonb NOT NULL DEFAULT '{{}}',
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX execution_incidents_time ON execution_incidents(mode, at);
        CREATE TABLE account_holdings (
            asset varchar(5) PRIMARY KEY CHECK (asset IN ('BTC','SOL')),
            quantity numeric(38,8) NOT NULL DEFAULT 0,
            reserved numeric(38,8) NOT NULL DEFAULT 0,
            CONSTRAINT account_holdings_nonnegative
                CHECK (quantity >= 0 AND reserved >= 0 AND quantity >= reserved)
        );
        INSERT INTO account_holdings (asset) VALUES ('BTC'), ('SOL');
        CREATE TABLE strategy_evaluations (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            strategy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            symbol varchar(12) NOT NULL CHECK (symbol IN {SYMBOLS}),
            bar_open_ms bigint NOT NULL CHECK (bar_open_ms >= 0 AND bar_open_ms % 3600000 = 0),
            bar_observation_id uuid NOT NULL REFERENCES market_observations(id),
            bar_available_at timestamptz NOT NULL,
            watermark bigint NOT NULL,
            decided_at timestamptz NOT NULL,
            result varchar(24) NOT NULL CHECK (result IN ('ENTRY_SIGNAL','TREND_EXIT_SIGNAL',
                'NO_SIGNAL','WARMUP_INCOMPLETE','LATE_BAR')),
            features jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT strategy_evaluation_once UNIQUE (mode, strategy_id, symbol, bar_open_ms)
        );
        CREATE TABLE signal_outcomes (
            evaluation_id uuid PRIMARY KEY REFERENCES strategy_evaluations(id),
            outcome varchar(32) NOT NULL CHECK (outcome IN ('ENTERED','MISSED','REJECTED',
                'SUPPRESSED_POSITION_OPEN','EXHAUSTED','EXPIRED_FINAL','EXIT_OBLIGATION',
                'NO_POSITION')),
            reason varchar(64),
            decided_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE risk_decisions (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            evaluation_id uuid REFERENCES strategy_evaluations(id),
            attempt integer NOT NULL CHECK (attempt >= 1),
            decided_at timestamptz NOT NULL,
            account_version bigint NOT NULL,
            risk_policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            cost_scenario_id varchar(64) NOT NULL,
            result varchar(8) NOT NULL CHECK (result IN ('ACCEPT','REJECT','DEFER')),
            primary_reason varchar(64),
            reasons jsonb NOT NULL,
            inputs jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX risk_decisions_evaluation ON risk_decisions(evaluation_id);
        CREATE TABLE position_mandates (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            symbol varchar(12) NOT NULL CHECK (symbol IN {SYMBOLS}),
            strategy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            strategy_sha256 varchar(64) NOT NULL,
            evaluation_id uuid NOT NULL UNIQUE REFERENCES strategy_evaluations(id),
            entry_reason varchar(64) NOT NULL,
            entry_reference numeric NOT NULL CHECK (entry_reference > 0),
            stop_price numeric NOT NULL CHECK (stop_price > 0 AND stop_price < entry_reference),
            atr numeric NOT NULL CHECK (atr > 0),
            stop_policy varchar(40) NOT NULL,
            max_hold_seconds integer NOT NULL CHECK (max_hold_seconds > 0),
            trend_exit_rule varchar(64) NOT NULL,
            envelope_price numeric(38,8) NOT NULL CHECK (envelope_price > 0),
            unit_risk numeric NOT NULL CHECK (unit_risk > 0),
            risk_policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            risk_policy_sha256 varchar(64) NOT NULL,
            cost_scenario_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            cost_scenario_sha256 varchar(64) NOT NULL,
            created_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE positions (
            id uuid PRIMARY KEY REFERENCES position_mandates(id),
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            symbol varchar(12) NOT NULL CHECK (symbol IN {SYMBOLS}),
            state varchar(20) NOT NULL CHECK (state IN ('PENDING_ENTRY','OPEN','CLOSING','CLOSED',
                'CLOSED_WITH_DUST','VOID')),
            quantity numeric(38,8) NOT NULL DEFAULT 0 CHECK (quantity >= 0),
            cost_basis numeric(38,8) NOT NULL DEFAULT 0 CHECK (cost_basis >= 0),
            bought_quantity numeric(38,8) NOT NULL DEFAULT 0 CHECK (bought_quantity >= 0),
            sold_quantity numeric(38,8) NOT NULL DEFAULT 0 CHECK (sold_quantity >= 0),
            quote_spent numeric(38,8) NOT NULL DEFAULT 0 CHECK (quote_spent >= 0),
            quote_received numeric(38,8) NOT NULL DEFAULT 0 CHECK (quote_received >= 0),
            fees_base numeric(38,8) NOT NULL DEFAULT 0 CHECK (fees_base >= 0),
            fees_quote numeric(38,8) NOT NULL DEFAULT 0 CHECK (fees_quote >= 0),
            realized_pnl numeric(38,8) NOT NULL DEFAULT 0,
            dust_quantity numeric(38,8) NOT NULL DEFAULT 0 CHECK (dust_quantity >= 0),
            first_fill_at timestamptz,
            time_exit_at timestamptz,
            closed_at timestamptz,
            version bigint NOT NULL DEFAULT 0,
            created_at timestamptz NOT NULL
        );
        CREATE UNIQUE INDEX positions_one_live_per_symbol ON positions(mode, symbol)
            WHERE state IN ('PENDING_ENTRY','OPEN','CLOSING');
        CREATE TABLE position_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            position_id uuid NOT NULL REFERENCES positions(id),
            event varchar(40) NOT NULL,
            at timestamptz NOT NULL,
            detail jsonb NOT NULL DEFAULT '{{}}',
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX position_events_position ON position_events(position_id, id);
        CREATE TABLE exit_obligations (
            id uuid PRIMARY KEY,
            position_id uuid NOT NULL UNIQUE REFERENCES positions(id),
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            reason varchar(20) NOT NULL CHECK (reason IN ('PROTECTIVE_STOP','TIME_EXIT','TREND_EXIT')),
            triggered_at timestamptz NOT NULL,
            trigger_evidence jsonb NOT NULL,
            state varchar(12) NOT NULL CHECK (state IN ('ACTIVE','COMPLETED','RESIDUAL')),
            attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            suppressed jsonb NOT NULL DEFAULT '[]',
            completed_at timestamptz,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE orders (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            account_id smallint NOT NULL DEFAULT 1 REFERENCES account_state(id),
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            activation_kind varchar(16) NOT NULL CHECK (activation_kind IN ('MAIN','FIXTURE','REPLAY')),
            run_ref varchar(64),
            client_order_id varchar(32) NOT NULL UNIQUE,
            origin varchar(20) NOT NULL CHECK (origin IN ('ENTRY','PROTECTIVE_STOP','TIME_EXIT','TREND_EXIT')),
            attempt integer NOT NULL CHECK (attempt >= 1),
            side varchar(4) NOT NULL CHECK (side IN ('BUY','SELL')),
            symbol varchar(12) NOT NULL CHECK (symbol IN {SYMBOLS}),
            position_id uuid NOT NULL REFERENCES positions(id),
            evaluation_id uuid REFERENCES strategy_evaluations(id),
            obligation_id uuid REFERENCES exit_obligations(id),
            risk_decision_id uuid REFERENCES risk_decisions(id),
            strategy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            risk_policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            cost_scenario_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            definition_hashes jsonb NOT NULL,
            requested_qty numeric(38,8) NOT NULL CHECK (requested_qty > 0),
            quantity_interpretation varchar(24) NOT NULL DEFAULT 'BASE_QUANTITY_EXACT'
                CHECK (quantity_interpretation = 'BASE_QUANTITY_EXACT'),
            envelope_price numeric(38,8),
            stop_price numeric,
            decision_quote jsonb NOT NULL,
            decision_quote_observation_id uuid NOT NULL REFERENCES market_observations(id),
            decision_watermark bigint NOT NULL,
            instrument_observation_id uuid NOT NULL REFERENCES market_observations(id),
            filters jsonb NOT NULL,
            decided_at timestamptz NOT NULL,
            arrival_at timestamptz NOT NULL,
            fill_deadline timestamptz,
            status varchar(24) NOT NULL CHECK (status IN {ORDER_STATUSES}),
            status_reason varchar(64),
            filled_qty numeric(38,8) NOT NULL DEFAULT 0
                CHECK (filled_qty >= 0 AND filled_qty <= requested_qty),
            reserved_asset varchar(5) CHECK (reserved_asset IN ('USDT','BTC','SOL')),
            reserved_amount numeric(38,8) CHECK (reserved_amount >= 0),
            execution_fidelity varchar(24) NOT NULL DEFAULT 'SAMPLED_L1_TICKER',
            terminal_at timestamptz,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT order_side_origin CHECK ((side = 'BUY') = (origin = 'ENTRY'))
        );
        CREATE UNIQUE INDEX orders_one_open_per_symbol ON orders(mode, symbol)
            WHERE status IN ('PENDING_VALIDATION','ACCEPTED','PARTIALLY_FILLED','CANCEL_PENDING');
        CREATE INDEX orders_status ON orders(mode, status, seq);
        CREATE TABLE order_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            order_id uuid NOT NULL REFERENCES orders(id),
            from_status varchar(24),
            to_status varchar(24) NOT NULL CHECK (to_status IN {ORDER_STATUSES}),
            reason varchar(64),
            at timestamptz NOT NULL,
            lease_epoch bigint NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX order_events_order ON order_events(order_id, id);
        CREATE TABLE fills (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            order_id uuid NOT NULL REFERENCES orders(id),
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            symbol varchar(12) NOT NULL CHECK (symbol IN {SYMBOLS}),
            side varchar(4) NOT NULL CHECK (side IN ('BUY','SELL')),
            quantity numeric(38,8) NOT NULL CHECK (quantity > 0),
            price numeric(38,8) NOT NULL CHECK (price > 0),
            gross numeric(38,8) NOT NULL CHECK (gross > 0),
            fee numeric(38,8) NOT NULL CHECK (fee >= 0),
            fee_asset varchar(5) NOT NULL CHECK (fee_asset IN ('USDT','BTC','SOL')),
            quote_observation_id uuid NOT NULL REFERENCES market_observations(id),
            quote_sequence bigint NOT NULL,
            quote jsonb NOT NULL,
            displayed_qty numeric NOT NULL,
            depleted_qty numeric NOT NULL,
            participation numeric NOT NULL,
            instrument_observation_id uuid NOT NULL REFERENCES market_observations(id),
            filters jsonb NOT NULL,
            cost_scenario_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            execution_rule varchar(24) NOT NULL DEFAULT 'PAPER_FILL_V1',
            execution_fidelity varchar(24) NOT NULL DEFAULT 'SAMPLED_L1_TICKER',
            evidence_acquisition varchar(24) NOT NULL,
            modeled_at timestamptz NOT NULL,
            available_at timestamptz NOT NULL,
            lease_epoch bigint NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT fill_once_per_quote UNIQUE (order_id, quote_sequence)
        );
        CREATE INDEX fills_order ON fills(order_id);
        CREATE TABLE valuations (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            valued_at timestamptz NOT NULL,
            purpose varchar(20) NOT NULL CHECK (purpose IN ('PERIODIC','FILL','HIGH_WATER',
                'DAILY_REFERENCE','LATCH','TOPUP','STARTUP')),
            account_version bigint NOT NULL,
            cash numeric(38,8) NOT NULL,
            holdings jsonb NOT NULL,
            equity numeric(38,8),
            units numeric(72,36) NOT NULL,
            nav numeric(72,36),
            quality varchar(8) NOT NULL CHECK (quality IN ('VALID','INVALID')),
            reason varchar(64),
            policy_id varchar(64) NOT NULL REFERENCES execution_definitions(id),
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT valuation_valid_values CHECK (quality = 'INVALID' OR (equity IS NOT NULL AND nav IS NOT NULL))
        );
        CREATE INDEX valuations_time ON valuations(mode, valued_at);
        CREATE TABLE daily_references (
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            utc_date date NOT NULL,
            valuation_id uuid NOT NULL REFERENCES valuations(id),
            nav numeric(72,36) NOT NULL CHECK (nav > 0),
            quality varchar(20) NOT NULL CHECK (quality IN ('TIMELY','LATE_CONSERVATIVE')),
            lateness_ms bigint NOT NULL CHECK (lateness_ms >= 0),
            basis jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            PRIMARY KEY (mode, utc_date)
        );
        CREATE TABLE risk_latches (
            id uuid PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            cause varchar(16) NOT NULL CHECK (cause IN ('DAILY_LOSS','DRAWDOWN')),
            latched_at timestamptz NOT NULL,
            valuation_id uuid NOT NULL REFERENCES valuations(id),
            trigger jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE risk_breach_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            mode varchar(24) NOT NULL CHECK (mode IN {MODES}),
            cap varchar(24) NOT NULL CHECK (cap IN ('ASSET_NOTIONAL_BTC','ASSET_NOTIONAL_SOL',
                'TOTAL_NOTIONAL','AGGREGATE_RISK')),
            event varchar(8) NOT NULL CHECK (event IN ('STARTED','ENDED')),
            at timestamptz NOT NULL,
            detail jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
    """)

    # Journal: each transaction has exactly one source (funding XOR fill); postings may
    # only be added in the transaction that created their header.
    op.execute("""
        ALTER TABLE journal_transactions ALTER COLUMN funding_request_id DROP NOT NULL;
        ALTER TABLE journal_transactions ADD COLUMN fill_id uuid UNIQUE REFERENCES fills(id);
        ALTER TABLE journal_transactions ADD COLUMN created_txid bigint;
        ALTER TABLE journal_transactions ALTER COLUMN created_txid
            SET DEFAULT ((pg_current_xact_id())::text)::bigint;
        ALTER TABLE journal_transactions ADD CONSTRAINT journal_single_source
            CHECK (num_nonnulls(funding_request_id, fill_id) = 1) NOT VALID;
        ALTER TABLE journal_transactions VALIDATE CONSTRAINT journal_single_source;
        ALTER TABLE journal_postings DROP CONSTRAINT journal_account;
        ALTER TABLE journal_postings ADD CONSTRAINT journal_account CHECK (book_account IN
            ('OWNER_CASH','OWNER_ASSET','VIRTUAL_CAPITAL','CLEARING','EXPENSE')) NOT VALID;
        ALTER TABLE journal_postings VALIDATE CONSTRAINT journal_account;
        ALTER TABLE journal_postings ADD CONSTRAINT journal_account_asset CHECK (
            (book_account NOT IN ('OWNER_CASH','VIRTUAL_CAPITAL') OR asset = 'USDT')
            AND (book_account <> 'OWNER_ASSET' OR asset IN ('BTC','SOL'))) NOT VALID;
        ALTER TABLE journal_postings VALIDATE CONSTRAINT journal_account_asset;
        ALTER TABLE reservations ADD COLUMN order_id uuid UNIQUE REFERENCES orders(id);
        ALTER TABLE reservations ADD COLUMN consumed_amount numeric(38,8) NOT NULL DEFAULT 0;
        ALTER TABLE reservations ADD COLUMN released_amount numeric(38,8) NOT NULL DEFAULT 0;
        ALTER TABLE reservations ADD COLUMN closed_at timestamptz;
        ALTER TABLE reservations DROP CONSTRAINT reservation_status;
        ALTER TABLE reservations ADD CONSTRAINT reservation_status
            CHECK (status IN ('ACTIVE','RELEASED','CONSUMED')) NOT VALID;
        ALTER TABLE reservations VALIDATE CONSTRAINT reservation_status;
        ALTER TABLE reservations ADD CONSTRAINT reservation_amounts CHECK (
            consumed_amount >= 0 AND released_amount >= 0
            AND consumed_amount + released_amount <= amount) NOT VALID;
        ALTER TABLE reservations VALIDATE CONSTRAINT reservation_amounts;
    """)

    op.execute("""
        CREATE FUNCTION asl_is_superuser() RETURNS boolean LANGUAGE sql STABLE AS $$
            SELECT rolsuper FROM pg_roles WHERE rolname = current_user
        $$;

        CREATE FUNCTION asl_journal_source_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF current_user = 'asl_api' AND NEW.funding_request_id IS NOT NULL
                AND NEW.fill_id IS NULL THEN RETURN NEW; END IF;
            IF current_user = 'asl_execution' AND NEW.fill_id IS NOT NULL
                AND NEW.funding_request_id IS NULL THEN RETURN NEW; END IF;
            RAISE EXCEPTION 'journal source not permitted for this role';
        END $$;
        CREATE TRIGGER journal_transactions_source BEFORE INSERT ON journal_transactions
            FOR EACH ROW EXECUTE FUNCTION asl_journal_source_guard();

        CREATE FUNCTION asl_posting_source_guard() RETURNS trigger LANGUAGE plpgsql AS $$
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
        CREATE TRIGGER journal_postings_source BEFORE INSERT ON journal_postings
            FOR EACH ROW EXECUTE FUNCTION asl_posting_source_guard();

        CREATE FUNCTION asl_account_state_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF OLD.paused AND NOT NEW.paused THEN
                RAISE EXCEPTION 'pause latch cannot be cleared by an application role'; END IF;
            IF OLD.reconciliation_failed AND NOT NEW.reconciliation_failed THEN
                RAISE EXCEPTION 'reconciliation latch cannot be cleared by an application role'; END IF;
            IF OLD.high_water_nav IS NOT NULL AND (NEW.high_water_nav IS NULL
                    OR NEW.high_water_nav < OLD.high_water_nav) THEN
                RAISE EXCEPTION 'high-water NAV cannot decrease'; END IF;
            IF NEW.fencing_epoch < OLD.fencing_epoch THEN
                RAISE EXCEPTION 'fencing epoch cannot decrease'; END IF;
            IF current_user <> 'asl_api' AND (NEW.units IS DISTINCT FROM OLD.units
                    OR NEW.contributions IS DISTINCT FROM OLD.contributions
                    OR NEW.initialized IS DISTINCT FROM OLD.initialized) THEN
                RAISE EXCEPTION 'units, contributions and initialization change only through funding'; END IF;
            IF current_user = 'asl_api' AND NEW.fencing_epoch <> OLD.fencing_epoch THEN
                RAISE EXCEPTION 'fencing epoch belongs to the execution authority'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER account_state_guard BEFORE UPDATE ON account_state
            FOR EACH ROW EXECUTE FUNCTION asl_account_state_guard();

        CREATE FUNCTION asl_order_transition_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.status IN ('REJECTED','FILLED','CANCELED','EXPIRED','RECONCILIATION_REQUIRED') THEN
                RAISE EXCEPTION 'terminal or frozen order cannot change'; END IF;
            IF NEW.status <> OLD.status AND (OLD.status, NEW.status) NOT IN (
                ('PENDING_VALIDATION','ACCEPTED'), ('PENDING_VALIDATION','REJECTED'),
                ('ACCEPTED','FILLED'), ('ACCEPTED','PARTIALLY_FILLED'),
                ('PARTIALLY_FILLED','CANCELED'), ('ACCEPTED','CANCEL_PENDING'),
                ('PARTIALLY_FILLED','CANCEL_PENDING'), ('CANCEL_PENDING','CANCELED'),
                ('ACCEPTED','EXPIRED'), ('PENDING_VALIDATION','RECONCILIATION_REQUIRED'),
                ('ACCEPTED','RECONCILIATION_REQUIRED'), ('PARTIALLY_FILLED','RECONCILIATION_REQUIRED'),
                ('CANCEL_PENDING','RECONCILIATION_REQUIRED')) THEN
                RAISE EXCEPTION 'order transition % -> % is not allowed', OLD.status, NEW.status; END IF;
            IF (to_jsonb(NEW) - ARRAY['status','status_reason','filled_qty','terminal_at','reserved_asset','reserved_amount'])
                    IS DISTINCT FROM (to_jsonb(OLD) - ARRAY['status','status_reason','filled_qty','terminal_at','reserved_asset','reserved_amount']) THEN
                RAISE EXCEPTION 'order identity and decision fields are immutable'; END IF;
            IF (NEW.reserved_asset IS DISTINCT FROM OLD.reserved_asset
                    OR NEW.reserved_amount IS DISTINCT FROM OLD.reserved_amount)
                    AND NOT (OLD.status = 'PENDING_VALIDATION' AND OLD.reserved_amount IS NULL) THEN
                RAISE EXCEPTION 'reservation terms are fixed once set'; END IF;
            IF NEW.filled_qty < OLD.filled_qty THEN
                RAISE EXCEPTION 'filled quantity cannot decrease'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER orders_transition BEFORE UPDATE ON orders
            FOR EACH ROW EXECUTE FUNCTION asl_order_transition_guard();

        CREATE FUNCTION asl_position_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.state IN ('CLOSED','CLOSED_WITH_DUST','VOID') THEN
                RAISE EXCEPTION 'closed position cannot change'; END IF;
            IF NEW.id <> OLD.id OR NEW.mode <> OLD.mode OR NEW.symbol <> OLD.symbol
                    OR NEW.created_at <> OLD.created_at THEN
                RAISE EXCEPTION 'position identity is immutable'; END IF;
            IF OLD.first_fill_at IS NOT NULL AND NEW.first_fill_at IS DISTINCT FROM OLD.first_fill_at THEN
                RAISE EXCEPTION 'first fill time is immutable'; END IF;
            IF OLD.time_exit_at IS NOT NULL AND NEW.time_exit_at IS DISTINCT FROM OLD.time_exit_at THEN
                RAISE EXCEPTION 'time exit is part of the original mandate'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER positions_guard BEFORE UPDATE ON positions
            FOR EACH ROW EXECUTE FUNCTION asl_position_guard();

        CREATE FUNCTION asl_obligation_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.state <> 'ACTIVE' THEN RAISE EXCEPTION 'completed obligation cannot change'; END IF;
            IF NEW.id <> OLD.id OR NEW.position_id <> OLD.position_id OR NEW.reason <> OLD.reason
                    OR NEW.triggered_at <> OLD.triggered_at
                    OR NEW.trigger_evidence <> OLD.trigger_evidence OR NEW.attempts < OLD.attempts THEN
                RAISE EXCEPTION 'obligation trigger is immutable'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER exit_obligations_guard BEFORE UPDATE ON exit_obligations
            FOR EACH ROW EXECUTE FUNCTION asl_obligation_guard();

        CREATE FUNCTION asl_execution_mode_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.mode <> 'FORWARD_PAPER' AND current_database() NOT LIKE 'asl\\_m1\\_%' THEN
                RAISE EXCEPTION 'test and replay modes require a disposable asl_m1_ database';
            END IF;
            RETURN NEW;
        END $$;

        CREATE FUNCTION asl_definition_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF NEW.status = 'FIXTURE_ONLY' AND current_database() NOT LIKE 'asl\\_m1\\_%' THEN
                RAISE EXCEPTION 'fixture definitions require a disposable asl_m1_ database';
            END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER execution_definitions_fixture BEFORE INSERT ON execution_definitions
            FOR EACH ROW EXECUTE FUNCTION asl_definition_guard();
    """)
    for table in APPEND_ONLY:
        op.execute(
            f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION asl_immutable()"
        )
    for table in MODE_GUARDED:
        op.execute(
            f"CREATE TRIGGER {table}_mode BEFORE INSERT OR UPDATE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION asl_execution_mode_guard()"
        )

    bind = op.get_bind()
    for line in SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, digest = json.loads(line)
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            # Separate parameters: a shared placeholder would be typed jsonb and the
            # text column would store jsonb's normalized spacing instead.
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), "
            "%(canonical)s, %(sha)s)",
            {"id": identity, "kind": kind, "version": version, "status": status,
             "definition": canonical, "canonical": canonical, "sha": digest},
        )
    bind.exec_driver_sql("""
        DO $$ BEGIN
            IF EXISTS (SELECT 1 FROM execution_definitions
                       WHERE encode(digest(convert_to(canonical, 'UTF8'), 'sha256'), 'hex') <> sha256) THEN
                RAISE EXCEPTION 'seeded definition hash mismatch';
            END IF;
        END $$
    """)

    raw = bind.connection.driver_connection
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_execution'")
        if cursor.fetchone() is None:
            # NOLOGIN until an explicit activation step grants a password.
            cursor.execute("CREATE ROLE asl_execution NOLOGIN")
        database_name = os.environ.get("ASL_DB_NAME", "asl")
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO asl_execution").format(
            sql.Identifier(database_name)))
    m3_tables = (
        "execution_definitions, execution_lease, execution_checkpoints, execution_steps, "
        "execution_incidents, account_holdings, strategy_evaluations, signal_outcomes, "
        "risk_decisions, position_mandates, positions, position_events, exit_obligations, "
        "orders, order_events, fills, valuations, daily_references, risk_latches, risk_breach_events"
    )
    op.execute("GRANT USAGE ON SCHEMA public TO asl_execution")
    op.execute(f"GRANT SELECT ON {m3_tables} TO asl_execution, asl_api")
    op.execute(
        "GRANT SELECT ON alembic_version, system_metadata, account_state, funding_requests, "
        "journal_transactions, journal_postings, reservations, audit_events, outbox_events, "
        "market_observations, market_publications, market_feed_state, market_lease, "
        "market_worker_state, market_collections, market_candle_confirmations, market_incidents, "
        "market_evidence_pins TO asl_execution"
    )
    op.execute(
        "GRANT INSERT ON execution_checkpoints, execution_steps, execution_incidents, "
        "strategy_evaluations, signal_outcomes, risk_decisions, position_mandates, positions, "
        "position_events, exit_obligations, orders, order_events, fills, valuations, "
        "daily_references, risk_latches, risk_breach_events, journal_transactions, "
        "journal_postings, reservations, audit_events, outbox_events, market_evidence_pins "
        "TO asl_execution"
    )
    op.execute(
        "GRANT UPDATE (version, fencing_epoch, cash, reserved, nav, high_water_nav, paused, "
        "reconciliation_failed) ON account_state TO asl_execution"
    )
    op.execute("GRANT UPDATE (quantity, reserved) ON account_holdings TO asl_execution")
    op.execute("GRANT UPDATE (owner_id, epoch, expires_at) ON execution_lease TO asl_execution")
    op.execute(
        "GRANT UPDATE (last_sequence, last_step_at, lease_epoch, state, updated_at) "
        "ON execution_checkpoints TO asl_execution"
    )
    op.execute(
        "GRANT UPDATE (status, consumed_amount, released_amount, closed_at) "
        "ON reservations TO asl_execution"
    )
    op.execute(
        "GRANT UPDATE (status, status_reason, filled_qty, terminal_at, reserved_asset, reserved_amount) "
        "ON orders TO asl_execution"
    )
    op.execute(
        "GRANT UPDATE (state, quantity, cost_basis, bought_quantity, sold_quantity, quote_spent, "
        "quote_received, fees_base, fees_quote, realized_pnl, dust_quantity, first_fill_at, "
        "time_exit_at, closed_at, version) ON positions TO asl_execution"
    )
    op.execute(
        "GRANT UPDATE (state, attempts, suppressed, completed_at) ON exit_obligations TO asl_execution"
    )
    op.execute(
        "GRANT USAGE, SELECT ON SEQUENCE journal_postings_id_seq, outbox_events_id_seq, "
        "execution_incidents_id_seq, position_events_id_seq, orders_seq_seq, "
        "order_events_id_seq, risk_breach_events_id_seq, positions_seq_seq, fills_seq_seq TO asl_execution"
    )
    # The API never creates orders or reservations and never moves the fencing epoch.
    op.execute("REVOKE INSERT ON reservations FROM asl_api")
    op.execute("REVOKE UPDATE (status) ON reservations FROM asl_api")
    op.execute("REVOKE UPDATE (fencing_epoch) ON account_state FROM asl_api")


def downgrade() -> None:
    raise RuntimeError("M3 financial and execution history cannot be downgraded destructively")
