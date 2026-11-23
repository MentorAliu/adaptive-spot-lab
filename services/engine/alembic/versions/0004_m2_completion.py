"""Capture generations, measured queues and point-in-time candle confirmations."""

from alembic import op

revision = "0004_m2_completion"
down_revision = "0003_market_data"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        -- Epoch/owner updates must conflict with capture KEY SHARE locks;
        -- expiry-only heartbeat updates remain independent NO KEY UPDATEs.
        ALTER TABLE market_lease ADD CONSTRAINT market_lease_authority UNIQUE (id, owner_id, epoch);
        CREATE TABLE market_collections (
            id uuid PRIMARY KEY, owner_id uuid NOT NULL,
            lease_epoch bigint NOT NULL CHECK (lease_epoch > 0),
            started_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        ALTER TABLE market_observations
            ADD COLUMN collection_id uuid REFERENCES market_collections(id),
            ADD COLUMN instrument_id uuid REFERENCES market_observations(id);
        ALTER TABLE market_feed_state
            ADD COLUMN collection_id uuid REFERENCES market_collections(id),
            ADD COLUMN instrument_id uuid REFERENCES market_observations(id);
        CREATE TABLE market_worker_state (
            id smallint PRIMARY KEY CHECK (id = 1),
            collection_id uuid REFERENCES market_collections(id),
            owner_id uuid, lease_epoch bigint,
            sampled_at timestamptz,
            queue_count integer CHECK (queue_count BETWEEN 0 AND 4096),
            queue_bytes bigint CHECK (queue_bytes BETWEEN 0 AND 8388608),
            oldest_age_ms double precision,
            publication_lag_ms double precision,
            overloaded boolean NOT NULL DEFAULT false
        );
        INSERT INTO market_worker_state (id) VALUES (1);
        CREATE TABLE market_candle_confirmations (
            id uuid PRIMARY KEY,
            observation_id uuid NOT NULL REFERENCES market_observations(id),
            payload_id uuid NOT NULL REFERENCES market_payloads(id),
            collection_id uuid REFERENCES market_collections(id),
            symbol varchar(12) NOT NULL CHECK (symbol IN ('BTCUSDT','SOLUSDT')),
            open_ms bigint NOT NULL,
            through_sequence bigint NOT NULL CHECK (through_sequence > 0),
            requested_at timestamptz NOT NULL,
            received_at timestamptz NOT NULL CHECK (received_at >= requested_at)
        );
        ALTER TABLE market_publications ALTER COLUMN observation_id DROP NOT NULL;
        ALTER TABLE market_publications ADD COLUMN confirmation_id uuid UNIQUE
            REFERENCES market_candle_confirmations(id);
        ALTER TABLE market_publications ADD CONSTRAINT market_publication_subject
            CHECK (num_nonnulls(observation_id, confirmation_id) = 1);
        CREATE INDEX market_confirmations_interval ON market_candle_confirmations(symbol, open_ms);
        CREATE INDEX market_observations_instrument ON market_observations(instrument_id)
            WHERE instrument_id IS NOT NULL;
        CREATE INDEX market_observations_retention ON market_observations(received_at, id);
        CREATE INDEX market_observations_payload ON market_observations(payload_id);
        CREATE INDEX market_payloads_retention ON market_payloads(received_at, id);
        CREATE INDEX market_candles_final ON market_observations(symbol, open_ms)
            WHERE kind = 'CANDLE' AND is_final;
        CREATE INDEX market_candles_provisional ON market_observations
            (symbol, open_ms, source_event_at DESC NULLS LAST, received_at DESC)
            WHERE kind = 'CANDLE' AND NOT is_final;
        CREATE INDEX market_confirmations_payload ON market_candle_confirmations(payload_id);
        CREATE INDEX market_confirmations_observation ON market_candle_confirmations(observation_id);
        CREATE TRIGGER market_collections_immutable BEFORE UPDATE OR DELETE ON market_collections
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();
        CREATE TRIGGER market_confirmations_immutable BEFORE UPDATE OR DELETE ON market_candle_confirmations
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();
        GRANT SELECT ON market_collections, market_worker_state, market_candle_confirmations
            TO asl_market_worker, asl_api;
        GRANT INSERT ON market_collections, market_candle_confirmations TO asl_market_worker;
        GRANT UPDATE ON market_worker_state TO asl_market_worker;
        GRANT UPDATE (collection_id, instrument_id) ON market_feed_state TO asl_market_worker;
    """)
    # Retention never breaks new provenance or confirmations. Referenced revisions
    # and their raw payloads remain pinned by their foreign keys and these rules.
    op.execute("""
        CREATE OR REPLACE FUNCTION asl_prune_market_evidence(p_owner uuid, p_epoch bigint)
        RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp AS $$
        DECLARE
            observation_ids uuid[]; observation_text text;
            payload_ids uuid[]; payload_text text;
            observation_count integer := 0; payload_count integer := 0;
        BEGIN
            PERFORM 1 FROM market_lease WHERE id = 1 AND owner_id = p_owner
                AND epoch = p_epoch AND expires_at > clock_timestamp() FOR KEY SHARE;
            IF NOT FOUND THEN RAISE EXCEPTION 'market retention lease lost'; END IF;
            SELECT array_agg(id), string_agg(id::text || ':' || semantic_hash, '|' ORDER BY received_at, id)
            INTO observation_ids, observation_text FROM (
                SELECT o.id, o.semantic_hash, o.received_at FROM market_observations o
                WHERE o.received_at < now() - interval '7 days'
                AND (o.kind = 'QUOTE' OR (o.kind = 'CANDLE'
                    AND (NOT o.is_final OR o.received_at < now() - interval '730 days')))
                AND NOT EXISTS (SELECT 1 FROM market_evidence_pins p WHERE p.observation_id = o.id)
                AND NOT EXISTS (SELECT 1 FROM market_candle_confirmations c WHERE c.observation_id = o.id)
                AND NOT EXISTS (SELECT 1 FROM market_observations r WHERE r.instrument_id = o.id)
                ORDER BY o.received_at, o.id LIMIT 500
            ) selected;
            IF observation_ids IS NOT NULL THEN
                PERFORM set_config('asl.market_retention', '1', true);
                DELETE FROM market_publications WHERE observation_id = ANY(observation_ids);
                DELETE FROM market_observations WHERE id = ANY(observation_ids);
                GET DIAGNOSTICS observation_count = ROW_COUNT;
            END IF;
            SELECT array_agg(id), string_agg(id::text || ':' || sha256, '|' ORDER BY id)
            INTO payload_ids, payload_text FROM (
                SELECT p.id, p.sha256 FROM market_payloads p
                WHERE p.received_at < now() - interval '7 days'
                -- Keep this as a bounded indexed lookup: a hash anti-join can
                -- scan the entire high-frequency observation table per batch.
                AND (SELECT o.id FROM market_observations o WHERE o.payload_id = p.id LIMIT 1) IS NULL
                AND NOT EXISTS (SELECT 1 FROM market_candle_confirmations c WHERE c.payload_id = p.id)
                ORDER BY p.received_at, p.id LIMIT 500
            ) selected;
            IF payload_ids IS NOT NULL THEN
                PERFORM set_config('asl.market_retention', '1', true);
                DELETE FROM market_payloads WHERE id = ANY(payload_ids);
                GET DIAGNOSTICS payload_count = ROW_COUNT;
            END IF;
            IF observation_count + payload_count > 0 THEN
                INSERT INTO market_retention_manifests
                    (id, deleted_observations, deleted_payloads, sha256, replay_fidelity)
                VALUES (gen_random_uuid(), observation_count, payload_count,
                    encode(digest(convert_to(coalesce(observation_text, '') || '|' ||
                        coalesce(payload_text, ''), 'UTF8'), 'sha256'), 'hex'), 'CAPTURED_SAMPLING_ONLY');
            END IF;
            RETURN observation_count + payload_count;
        END; $$;
    """)


def downgrade() -> None:
    raise RuntimeError("M2 capture and confirmation evidence cannot be downgraded")
