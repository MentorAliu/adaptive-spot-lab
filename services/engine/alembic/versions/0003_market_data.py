"""Public market observations, publication and a separate ingestion identity.

Revision ID: 0003_market_data
Revises: 0002_m1_account
"""

import os
from pathlib import Path

import sqlalchemy as sa
from psycopg import sql
from sqlalchemy.dialects.postgresql import JSONB, UUID

from alembic import op

revision = "0003_market_data"
down_revision = "0002_m1_account"
branch_labels = None
depends_on = None


def upgrade() -> None:
    password_path = Path(
        os.environ.get("ASL_MARKET_DB_PASSWORD_FILE", "/run/secrets/market_worker_password")
    )
    password = password_path.read_text(encoding="utf-8").strip()
    if len(password) < 32:
        raise RuntimeError("Market worker database identity is unavailable")

    op.create_table(
        "market_lease",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("owner_id", UUID(as_uuid=True)),
        sa.Column("epoch", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("id = 1 AND epoch >= 0", name="market_lease_valid"),
    )
    op.execute("INSERT INTO market_lease (id) VALUES (1)")
    op.create_table(
        "market_payloads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("source", sa.String(80), nullable=False),
        sa.Column("acquisition", sa.String(24), nullable=False),
        sa.Column("symbol", sa.String(12), nullable=False),
        sa.Column("schema_version", sa.SmallInteger(), nullable=False),
        sa.Column("body", sa.LargeBinary(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("source_event_at", sa.DateTime(timezone=True)),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("validation", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(80)),
        sa.CheckConstraint("octet_length(body) <= 2097152", name="market_payload_bound"),
        sa.CheckConstraint(
            "acquisition IN ('STREAM','HISTORICAL_REST','FIXTURE')",
            name="market_payload_acquisition",
        ),
        sa.CheckConstraint("validation IN ('VALID','INVALID')", name="market_payload_validation"),
    )
    op.create_index("market_payloads_received", "market_payloads", ["received_at"])
    op.create_table(
        "market_observations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("payload_id", UUID(as_uuid=True), sa.ForeignKey("market_payloads.id"), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False),
        sa.Column("symbol", sa.String(12), nullable=False),
        sa.Column("semantic_key", sa.String(100), nullable=False),
        sa.Column("semantic_hash", sa.String(64), nullable=False),
        sa.Column("acquisition", sa.String(24), nullable=False),
        sa.Column("source_event_at", sa.DateTime(timezone=True)),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open_ms", sa.BigInteger()),
        sa.Column("close_ms", sa.BigInteger()),
        sa.Column("open_price", sa.Numeric()),
        sa.Column("high_price", sa.Numeric()),
        sa.Column("low_price", sa.Numeric()),
        sa.Column("close_price", sa.Numeric()),
        sa.Column("volume", sa.Numeric()),
        sa.Column("bid_price", sa.Numeric()),
        sa.Column("bid_quantity", sa.Numeric()),
        sa.Column("ask_price", sa.Numeric()),
        sa.Column("ask_quantity", sa.Numeric()),
        sa.Column("instrument", JSONB()),
        sa.Column("is_final", sa.Boolean()),
        sa.Column("quality", sa.String(16), nullable=False),
        sa.Column("reason", sa.String(80)),
        sa.UniqueConstraint(
            "kind", "symbol", "semantic_key", "semantic_hash",
            name="market_observation_identity",
        ),
        sa.CheckConstraint("kind IN ('INSTRUMENT','CANDLE','QUOTE')", name="market_kind"),
        sa.CheckConstraint(
            "quality IN ('VALID','PROVISIONAL','CONFLICT')", name="market_quality"
        ),
        sa.CheckConstraint("symbol IN ('BTCUSDT','SOLUSDT')", name="market_symbol"),
    )
    op.create_index(
        "market_observations_candles",
        "market_observations",
        ["symbol", "open_ms", "received_at"],
        postgresql_where=sa.text("kind = 'CANDLE'"),
    )
    op.create_index(
        "market_observations_quotes",
        "market_observations",
        ["symbol", "source_event_at", "received_at"],
        postgresql_where=sa.text("kind = 'QUOTE'"),
    )
    op.create_table(
        "market_publications",
        sa.Column("sequence", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column(
            "observation_id", UUID(as_uuid=True),
            sa.ForeignKey("market_observations.id"), unique=True, nullable=False,
        ),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("lease_epoch", sa.BigInteger(), nullable=False),
        sa.CheckConstraint("lease_epoch > 0", name="market_publication_fenced"),
    )
    op.create_index("market_publications_time", "market_publications", ["available_at"])
    op.create_table(
        "market_feed_state",
        sa.Column("symbol", sa.String(12), primary_key=True),
        sa.Column("status", sa.String(24), nullable=False, server_default="DISABLED"),
        sa.Column("last_message_at", sa.DateTime(timezone=True)),
        sa.Column("last_quote_at", sa.DateTime(timezone=True)),
        sa.Column("last_final_open_ms", sa.BigInteger()),
        sa.Column("last_clock_check_at", sa.DateTime(timezone=True)),
        sa.Column("clock_offset_ms", sa.Numeric()),
        sa.Column("clock_uncertainty_ms", sa.Numeric()),
        sa.Column("last_instrument_check_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.String(80)),
        sa.Column("retry_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("symbol IN ('BTCUSDT','SOLUSDT')", name="market_feed_symbol"),
    )
    op.execute("INSERT INTO market_feed_state (symbol) VALUES ('BTCUSDT'), ('SOLUSDT')")
    op.create_table(
        "market_incidents",
        sa.Column("id", sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column("symbol", sa.String(12)),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("detail", JSONB(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "symbol IS NULL OR symbol IN ('BTCUSDT','SOLUSDT')", name="market_incident_symbol"
        ),
    )
    op.create_index("market_incidents_time", "market_incidents", ["occurred_at"])
    op.create_table(
        "market_evidence_pins",
        sa.Column("observation_id", UUID(as_uuid=True), sa.ForeignKey("market_observations.id"), primary_key=True),
        sa.Column("reference", sa.String(120), nullable=False),
        sa.Column("pinned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "market_retention_manifests",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("deleted_observations", sa.Integer(), nullable=False),
        sa.Column("deleted_payloads", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("replay_fidelity", sa.String(32), nullable=False),
        sa.CheckConstraint("deleted_observations >= 0 AND deleted_payloads >= 0", name="market_retention_counts"),
    )
    for table in ("market_incidents", "market_evidence_pins", "market_retention_manifests"):
        op.execute(
            f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION asl_immutable()"
        )
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    op.execute("""
        CREATE FUNCTION asl_market_retention_delete_guard() RETURNS trigger
        LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP = 'DELETE' AND current_user = 'asl'
                AND current_setting('asl.market_retention', true) = '1' THEN
                RETURN OLD;
            END IF;
            RAISE EXCEPTION 'market evidence is immutable outside bounded retention';
        END;
        $$
    """)
    for table in ("market_payloads", "market_observations", "market_publications"):
        op.execute(
            f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
            "FOR EACH ROW EXECUTE FUNCTION asl_market_retention_delete_guard()"
        )
    op.execute("""
        CREATE FUNCTION asl_prune_market_evidence(p_owner uuid, p_epoch bigint) RETURNS integer
        LANGUAGE plpgsql SECURITY DEFINER SET search_path = public, pg_temp AS $$
        DECLARE
            observation_ids uuid[];
            observation_text text;
            payload_ids uuid[];
            payload_text text;
            observation_count integer := 0;
            payload_count integer := 0;
        BEGIN
            PERFORM 1 FROM market_lease
            WHERE id = 1 AND owner_id = p_owner AND epoch = p_epoch
              AND expires_at > clock_timestamp() FOR UPDATE;
            IF NOT FOUND THEN
                RAISE EXCEPTION 'market retention lease lost';
            END IF;
            SELECT array_agg(id),
                   string_agg(id::text || ':' || semantic_hash, '|' ORDER BY received_at, id)
            INTO observation_ids, observation_text
            FROM (
                SELECT o.id, o.semantic_hash, o.received_at
                FROM market_observations o
                WHERE (
                    (o.kind = 'QUOTE' AND o.received_at < now() - interval '7 days')
                    OR (o.kind = 'CANDLE' AND NOT o.is_final
                        AND o.received_at < now() - interval '7 days')
                    OR (o.kind = 'CANDLE' AND o.is_final
                        AND o.received_at < now() - interval '730 days')
                )
                AND NOT EXISTS (
                    SELECT 1 FROM market_evidence_pins pin WHERE pin.observation_id = o.id
                )
                ORDER BY o.received_at, o.id LIMIT 1000
            ) selected;
            IF observation_ids IS NOT NULL THEN
                PERFORM set_config('asl.market_retention', '1', true);
                DELETE FROM market_publications WHERE observation_id = ANY(observation_ids);
                DELETE FROM market_observations WHERE id = ANY(observation_ids);
                GET DIAGNOSTICS observation_count = ROW_COUNT;
            END IF;
            SELECT array_agg(id), string_agg(id::text || ':' || sha256, '|' ORDER BY id)
            INTO payload_ids, payload_text
            FROM (
                SELECT p.id, p.sha256
                FROM market_payloads p
                WHERE p.received_at < now() - interval '7 days'
                  AND NOT EXISTS (
                      SELECT 1 FROM market_observations o WHERE o.payload_id = p.id
                  )
                ORDER BY p.received_at, p.id LIMIT 1000
            ) selected;
            IF payload_ids IS NOT NULL THEN
                PERFORM set_config('asl.market_retention', '1', true);
                DELETE FROM market_payloads WHERE id = ANY(payload_ids);
                GET DIAGNOSTICS payload_count = ROW_COUNT;
            END IF;
            IF observation_count + payload_count > 0 THEN
                INSERT INTO market_retention_manifests
                    (id, deleted_observations, deleted_payloads, sha256, replay_fidelity)
                VALUES (
                    gen_random_uuid(), observation_count, payload_count,
                    encode(digest(convert_to(
                        coalesce(observation_text, '') || '|' || coalesce(payload_text, ''),
                        'UTF8'), 'sha256'), 'hex'),
                    'CAPTURED_SAMPLING_ONLY'
                );
            END IF;
            RETURN observation_count + payload_count;
        END;
        $$
    """)
    op.execute("REVOKE ALL ON FUNCTION asl_prune_market_evidence(uuid, bigint) FROM PUBLIC")

    raw = op.get_bind().connection.driver_connection
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_market_worker'")
        if cursor.fetchone() is None:
            cursor.execute("CREATE ROLE asl_market_worker LOGIN")
        cursor.execute(sql.SQL("ALTER ROLE asl_market_worker PASSWORD {}").format(sql.Literal(password)))
        database_name = os.environ.get("ASL_DB_NAME", "asl")
        cursor.execute(
            sql.SQL("GRANT CONNECT ON DATABASE {} TO asl_market_worker").format(
                sql.Identifier(database_name)
            )
        )
    op.execute("GRANT USAGE ON SCHEMA public TO asl_market_worker")
    market_write_tables = "market_payloads, market_observations, market_publications, market_incidents"
    market_read_tables = (
        market_write_tables + ", market_lease, market_feed_state, "
        "market_evidence_pins, market_retention_manifests"
    )
    op.execute(f"GRANT SELECT ON {market_read_tables} TO asl_market_worker, asl_api")
    op.execute(f"GRANT INSERT ON {market_write_tables} TO asl_market_worker")
    op.execute("GRANT UPDATE (owner_id, epoch, expires_at) ON market_lease TO asl_market_worker")
    op.execute(
        "GRANT UPDATE (status, last_message_at, last_quote_at, last_final_open_ms, "
        "last_clock_check_at, clock_offset_ms, clock_uncertainty_ms, "
        "last_instrument_check_at, last_error, retry_at, updated_at) "
        "ON market_feed_state TO asl_market_worker"
    )
    op.execute(
        "GRANT USAGE, SELECT ON SEQUENCE market_publications_sequence_seq, "
        "market_incidents_id_seq TO asl_market_worker"
    )
    op.execute("GRANT EXECUTE ON FUNCTION asl_prune_market_evidence(uuid, bigint) TO asl_market_worker")


def downgrade() -> None:
    raise RuntimeError("M2 market evidence cannot be downgraded destructively")
