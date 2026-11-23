"""M11 update 2, part A: the BTCUSDT perpetual's public market data.

Revision ID: 0019_perp_market
Revises: 0018_claude_runner

ExecPlan 0039 section 5.2. Additive: seven tables the market worker writes and the API reads; no other identity reaches them
(part B grants what its account and trader need). Nothing of the spot market data, the paper account or the agents
changes. Each guard resolves names under a fixed search path, as every function of the schema does.

- ``perp_instruments``: BTCUSDT's exchangeInfo entry, a new row whenever it differs from the newest one.
- ``perp_quotes`` and ``perp_marks``: the book's five best levels a side, and one mark price with the current
  funding rate, per second of receipt (the newest of that second). Kept seven days; a row is never changed.
- ``perp_bars``: 1-minute candles. A final candle is never changed or deleted; an open one is replaced until final.
- ``perp_funding_rates``: the settled funding rates, append-only.
- ``perp_feed_state`` (one row) and ``perp_feed_events``: the feed's state and its incidents.

Downgrade drops the seven tables and their functions.
"""

from alembic import op

revision = "0019_perp_market"
down_revision = "0018_claude_runner"
branch_labels = None
depends_on = None

TABLES = ("perp_feed_events", "perp_feed_state", "perp_funding_rates", "perp_bars", "perp_marks", "perp_quotes",
          "perp_instruments")
READERS = ("asl_api",)
SEARCH_PATH = "pg_catalog, public, pg_temp"


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    op.execute("""
        CREATE TABLE perp_instruments (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            symbol varchar(12) NOT NULL CHECK (symbol = 'BTCUSDT'),
            sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
            status varchar(24) NOT NULL,
            contract_type varchar(24) NOT NULL,
            margin_asset varchar(8) NOT NULL,
            usable boolean NOT NULL,
            tick_size numeric NOT NULL CHECK (tick_size > 0),
            min_price numeric NOT NULL CHECK (min_price >= 0),
            max_price numeric NOT NULL CHECK (max_price >= 0),
            step_size numeric NOT NULL CHECK (step_size > 0),
            min_qty numeric NOT NULL CHECK (min_qty >= 0),
            max_qty numeric NOT NULL CHECK (max_qty >= min_qty),
            market_step_size numeric NOT NULL CHECK (market_step_size > 0),
            market_min_qty numeric NOT NULL CHECK (market_min_qty >= 0),
            market_max_qty numeric NOT NULL CHECK (market_max_qty >= market_min_qty),
            min_notional numeric NOT NULL CHECK (min_notional > 0),
            liquidation_fee numeric CHECK (liquidation_fee >= 0),
            market_take_bound numeric CHECK (market_take_bound >= 0),
            document jsonb NOT NULL,
            checked_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE perp_quotes (
            second_at timestamptz PRIMARY KEY,
            update_id bigint NOT NULL,
            bid numeric(38,8) NOT NULL CHECK (bid > 0),
            bid_qty numeric(38,8) NOT NULL CHECK (bid_qty >= 0),
            ask numeric(38,8) NOT NULL CHECK (ask > bid),
            ask_qty numeric(38,8) NOT NULL CHECK (ask_qty >= 0),
            -- The five best levels of each side as [price, quantity] decimal strings, best first.
            bids jsonb NOT NULL CHECK (CASE WHEN jsonb_typeof(bids) = 'array'
                THEN jsonb_array_length(bids) BETWEEN 1 AND 20 ELSE false END),
            asks jsonb NOT NULL CHECK (CASE WHEN jsonb_typeof(asks) = 'array'
                THEN jsonb_array_length(asks) BETWEEN 1 AND 20 ELSE false END),
            event_at timestamptz NOT NULL,
            transaction_at timestamptz NOT NULL,
            received_at timestamptz NOT NULL,
            connection_id uuid NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT perp_quote_second CHECK (date_trunc('second', received_at) = second_at)
        );
        CREATE TABLE perp_marks (
            second_at timestamptz PRIMARY KEY,
            mark numeric(38,8) NOT NULL CHECK (mark > 0),
            index_price numeric(38,8) NOT NULL CHECK (index_price > 0),
            estimated_settle numeric(38,8) CHECK (estimated_settle >= 0),
            funding_rate numeric NOT NULL CHECK (funding_rate > -1 AND funding_rate < 1),
            next_funding_at timestamptz NOT NULL,
            event_at timestamptz NOT NULL,
            received_at timestamptz NOT NULL,
            connection_id uuid NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT perp_mark_second CHECK (date_trunc('second', received_at) = second_at)
        );
        CREATE TABLE perp_bars (
            open_ms bigint PRIMARY KEY CHECK (open_ms >= 0 AND open_ms % 60000 = 0),
            open numeric(38,8) NOT NULL CHECK (open > 0),
            high numeric(38,8) NOT NULL,
            low numeric(38,8) NOT NULL CHECK (low > 0),
            close numeric(38,8) NOT NULL CHECK (close > 0),
            volume numeric NOT NULL CHECK (volume >= 0),
            quote_volume numeric NOT NULL CHECK (quote_volume >= 0),
            trades integer NOT NULL CHECK (trades >= 0),
            final boolean NOT NULL,
            source varchar(8) NOT NULL CHECK (source IN ('STREAM','REST')),
            event_at timestamptz,
            received_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT perp_bar_range CHECK (high >= greatest(open, close) AND low <= least(open, close))
        );
        CREATE TABLE perp_funding_rates (
            funding_ms bigint PRIMARY KEY CHECK (funding_ms >= 0),
            rate numeric NOT NULL CHECK (rate > -1 AND rate < 1),
            mark numeric(38,8) CHECK (mark > 0),
            rate_type varchar(12),
            received_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE TABLE perp_feed_state (
            id smallint PRIMARY KEY CHECK (id = 1),
            status varchar(16) NOT NULL DEFAULT 'STARTING'
                CHECK (status IN ('STARTING','CONNECTED','DEGRADED','UNAVAILABLE')),
            reason varchar(80),
            public_connected boolean NOT NULL DEFAULT false,
            market_connected boolean NOT NULL DEFAULT false,
            last_quote_at timestamptz,
            last_mark_at timestamptz,
            last_bar_at timestamptz,
            clock_verified boolean NOT NULL DEFAULT false,
            clock_offset_ms numeric,
            clock_uncertainty_ms numeric,
            clock_checked_at timestamptz,
            instrument_id bigint REFERENCES perp_instruments(id),
            instrument_checked_at timestamptz,
            history_checked_at timestamptz,
            funding_checked_at timestamptz,
            heartbeat_at timestamptz,
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        INSERT INTO perp_feed_state (id) VALUES (1);
        CREATE TABLE perp_feed_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            code varchar(48) NOT NULL,
            at timestamptz NOT NULL,
            detail jsonb NOT NULL DEFAULT '{}',
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX perp_feed_events_at ON perp_feed_events(at);

        CREATE FUNCTION asl_perp_append_only() RETURNS trigger LANGUAGE plpgsql
            SET search_path = {SEARCH_PATH} AS $$
        BEGIN RAISE EXCEPTION 'append-only perpetual market record'; END $$;
        -- Quotes and marks: never changed; deleted only once seven days old (the feed's retention).
        CREATE FUNCTION asl_perp_retained() RETURNS trigger LANGUAGE plpgsql
            SET search_path = {SEARCH_PATH} AS $$
        BEGIN
          IF TG_OP = 'UPDATE' THEN RAISE EXCEPTION 'perpetual market record is immutable'; END IF;
          IF OLD.second_at > clock_timestamp() - interval '7 days' THEN
            RAISE EXCEPTION 'perpetual market record is within retention';
          END IF;
          RETURN OLD;
        END $$;
        -- A final candle is never changed or deleted; an open one is replaced until it is final.
        CREATE FUNCTION asl_perp_bar_guard() RETURNS trigger LANGUAGE plpgsql
            SET search_path = {SEARCH_PATH} AS $$
        BEGIN
          IF TG_OP = 'DELETE' OR OLD.final THEN RAISE EXCEPTION 'final perpetual candle is immutable'; END IF;
          IF NEW.open_ms <> OLD.open_ms THEN RAISE EXCEPTION 'perpetual candle identity is immutable'; END IF;
          RETURN NEW;
        END $$;
        CREATE TRIGGER perp_instruments_append_only BEFORE UPDATE OR DELETE ON perp_instruments
            FOR EACH ROW EXECUTE FUNCTION asl_perp_append_only();
        CREATE TRIGGER perp_funding_rates_append_only BEFORE UPDATE OR DELETE ON perp_funding_rates
            FOR EACH ROW EXECUTE FUNCTION asl_perp_append_only();
        CREATE TRIGGER perp_feed_events_append_only BEFORE UPDATE OR DELETE ON perp_feed_events
            FOR EACH ROW EXECUTE FUNCTION asl_perp_append_only();
        CREATE TRIGGER perp_quotes_retained BEFORE UPDATE OR DELETE ON perp_quotes
            FOR EACH ROW EXECUTE FUNCTION asl_perp_retained();
        CREATE TRIGGER perp_marks_retained BEFORE UPDATE OR DELETE ON perp_marks
            FOR EACH ROW EXECUTE FUNCTION asl_perp_retained();
        CREATE TRIGGER perp_bars_guard BEFORE UPDATE OR DELETE ON perp_bars
            FOR EACH ROW EXECUTE FUNCTION asl_perp_bar_guard();
        CREATE TRIGGER perp_feed_state_singleton BEFORE DELETE ON perp_feed_state
            FOR EACH ROW EXECUTE FUNCTION asl_perp_append_only();

        GRANT SELECT, INSERT ON perp_instruments, perp_quotes, perp_marks, perp_bars, perp_funding_rates,
            perp_feed_events TO asl_market_worker;
        GRANT DELETE ON perp_quotes, perp_marks TO asl_market_worker;
        GRANT UPDATE (open, high, low, close, volume, quote_volume, trades, final, source, event_at, received_at)
            ON perp_bars TO asl_market_worker;
        GRANT SELECT ON perp_feed_state TO asl_market_worker;
        GRANT UPDATE (status, reason, public_connected, market_connected, last_quote_at, last_mark_at, last_bar_at,
            clock_verified, clock_offset_ms, clock_uncertainty_ms, clock_checked_at, instrument_id,
            instrument_checked_at, history_checked_at, funding_checked_at, heartbeat_at, updated_at)
            ON perp_feed_state TO asl_market_worker;
        GRANT USAGE, SELECT ON SEQUENCE perp_instruments_id_seq, perp_feed_events_id_seq TO asl_market_worker;
    """.replace("{SEARCH_PATH}", SEARCH_PATH))
    for role in READERS:
        op.execute(f"GRANT SELECT ON {', '.join(TABLES)} TO {role}")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    op.execute(f"DROP TABLE {', '.join(TABLES)}")
    op.execute("DROP FUNCTION asl_perp_append_only(), asl_perp_retained(), asl_perp_bar_guard()")
