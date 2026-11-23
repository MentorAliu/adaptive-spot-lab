"""A retention call looks for orphan payloads only where they can be, and five references are indexed.

Revision ID: 0017_market_retention_cost
Revises: 0016_m10_three_coins

ExecPlan 0038 section 4. The rules of retention do not change: what may be deleted, the call size of 500
observations, the lease check, the delete guard and the manifest are those of 0004.

- D1. The function of 0004 looked for orphan payloads among every payload older than seven days, in every call: about
  10,000 index lookups a call on the normal app on 2026-10-23, 1,700 of them for payloads that are kept for good, and
  the statement its two-second deadline ended most often. It now looks at the payloads of the observations the call
  has just deleted, and at most 200 others a call in a sweep that resumes where the previous call stopped
  (``market_retention_cursor``). The sweep finds what the first look cannot: a payload stored without an observation
  (an invalid frame) and the orphans the function of 0004 left behind. A kept payload is examined once, when the sweep
  passes it. The signature, owner, ``SECURITY DEFINER``, ``search_path`` and grant are unchanged, so a worker that is
  running when the migration is applied keeps calling it.
- D2. Five references to ``market_observations`` from M3 tables had no index, so every deleted observation scanned
  those tables (ExecPlan 0024 section 4.2). The tables are small, so each index builds at once; they are locked first,
  in the order the engine takes them (0016's ``LOCK_ORDER``).

Downgrade restores the function of 0004 and drops the cursor and the indexes. It deletes no market data.
"""

from alembic import op

revision = "0017_market_retention_cost"
down_revision = "0016_m10_three_coins"
branch_labels = None
depends_on = None

# (index, table, column): the five unindexed references of ExecPlan 0024 section 4.2.
INDEXES = (
    ("orders_decision_quote_observation", "orders", "decision_quote_observation_id"),
    ("orders_instrument_observation", "orders", "instrument_observation_id"),
    ("fills_quote_observation", "fills", "quote_observation_id"),
    ("fills_instrument_observation", "fills", "instrument_observation_id"),
    ("strategy_evaluations_bar_observation", "strategy_evaluations", "bar_observation_id"),
)
# The order in which the running engine takes these tables (0016's LOCK_ORDER).
LOCK_ORDER = ("orders", "fills", "strategy_evaluations")

# The sweep's start, and its position again if its row is ever missing.
ZERO = "00000000-0000-0000-0000-000000000000"

# Payloads the sweep examines in one call. The sweep walks only what retention keeps (about 96 payloads a day on the
# normal app) and what it has not yet found, so 200 a call keeps up with room to spare (ExecPlan 0038 section 4).
SWEEP = 200

# The body's line numbers are part of its evidence: PostgreSQL reports a failed statement by them, and the worker
# records that line in RETENTION_FAILED (ExecPlan 0024 D6). tests/test_m2_retention_faults.py names two of them.
FUNCTION = f"""
CREATE OR REPLACE FUNCTION asl_prune_market_evidence(p_owner uuid, p_epoch bigint)
RETURNS integer LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp AS $$
DECLARE
    observation_ids uuid[]; observation_text text; freed uuid[];
    after_at timestamptz; after_id uuid; last_at timestamptz; last_id uuid; examined uuid[];
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
        WITH deleted AS (DELETE FROM market_observations WHERE id = ANY(observation_ids) RETURNING payload_id)
        SELECT count(*), array_agg(DISTINCT payload_id) INTO observation_count, freed FROM deleted;
    END IF;
    SELECT c.received_at, c.payload_id INTO after_at, after_id FROM market_retention_cursor c WHERE c.id = 1 FOR UPDATE;
    IF NOT FOUND THEN after_at := '-infinity'; after_id := '{ZERO}'; INSERT INTO market_retention_cursor VALUES (1, after_at, after_id); END IF;
    SELECT array_agg(id), (array_agg(received_at ORDER BY received_at DESC, id DESC))[1],
        (array_agg(id ORDER BY received_at DESC, id DESC))[1] INTO examined, last_at, last_id FROM (
        SELECT p.id, p.received_at FROM market_payloads p
        WHERE p.received_at < now() - interval '7 days' AND (p.received_at, p.id) > (after_at, after_id)
        ORDER BY p.received_at, p.id LIMIT {SWEEP}
    ) swept;
    IF examined IS NOT NULL THEN
        UPDATE market_retention_cursor SET received_at = last_at, payload_id = last_id WHERE id = 1;
    END IF;
    SELECT array_agg(id), string_agg(id::text || ':' || sha256, '|' ORDER BY id)
    INTO payload_ids, payload_text FROM (
        SELECT p.id, p.sha256 FROM (SELECT DISTINCT unnest(coalesce(freed, '{{}}') || coalesce(examined, '{{}}')) AS id) c
        JOIN market_payloads p ON p.id = c.id
        WHERE p.received_at < now() - interval '7 days'
        AND NOT EXISTS (SELECT 1 FROM market_observations o WHERE o.payload_id = p.id)
        AND NOT EXISTS (SELECT 1 FROM market_candle_confirmations c WHERE c.payload_id = p.id)
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
"""

# The function of 0004, restored by the downgrade (the text of 0004_m2_completion.py).
FUNCTION_0004 = """
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
"""


def upgrade() -> None:
    # A lock the running app holds ends the attempt at once (55P03), and app.research.migrate tries it again, as 0016.
    op.execute("SET LOCAL lock_timeout = '200ms'")
    # The sweep's position: the last payload it examined, in (received_at, id) order. Only the function, which runs
    # as its owner, reads or writes it; no identity has a grant.
    op.execute("""
        CREATE TABLE market_retention_cursor (
            id smallint PRIMARY KEY CHECK (id = 1),
            received_at timestamptz NOT NULL,
            payload_id uuid NOT NULL
        )
    """)
    op.execute(f"INSERT INTO market_retention_cursor VALUES (1, '-infinity', '{ZERO}')")
    op.execute("REVOKE ALL ON market_retention_cursor FROM PUBLIC")
    op.execute(FUNCTION)
    op.execute(f"LOCK TABLE {', '.join(LOCK_ORDER)} IN SHARE MODE")
    for name, table, column in INDEXES:
        op.execute(f"CREATE INDEX {name} ON {table} ({column})")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '200ms'")
    op.execute(f"LOCK TABLE {', '.join(LOCK_ORDER)} IN SHARE MODE")
    for name, _table, _column in INDEXES:
        op.execute(f"DROP INDEX {name}")
    op.execute(FUNCTION_0004)
    op.execute("DROP TABLE market_retention_cursor")
