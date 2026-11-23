"""M4 approvals, experiments, controls, evaluation capture and reports.

Revision ID: 0006_m4_fixed_pilot
Revises: 0005_m3_paper_broker

Forward-only. Owner approvals, manifests, experiment events, latch resolutions,
evaluation marks and reports are append-only; experiments change state only through
a transition-and-actor guard. OWNER events come only from the API identity and SYSTEM
events only from the execution identity. The evaluation identity is created NOLOGIN
and may only insert reports. Nothing here approves, starts or activates anything.
"""

import json
import os

from psycopg import sql

from alembic import op

revision = "0006_m4_fixed_pilot"
down_revision = "0005_m3_paper_broker"
branch_labels = None
depends_on = None

# (id, kind, version, status, canonical JSON, SHA-256) from app.execution.definitions.m4_seed_rows()
SEED_LINES = r"""
["EVALUATION_PROTOCOL_V1", "EVALUATION_PROTOCOL", 1, "PROPOSED", "{\"acceptance_threshold\":null,\"annualization\":false,\"completeness\":\"GENERATE_ONLY_AFTER_EXECUTION_CHECKPOINT_PASSES_AS_OF\",\"cumulative_return\":\"LAST_VALID_NAV_OVER_START_NAV_MINUS_ONE_GAPS_INCLUDED\",\"gap_rule\":\"MISSING_INVALID_OR_LATE_POINT_IS_A_GAP\",\"grid\":\"HOURLY_UTC\",\"hourly_point_max_lateness_ms\":300000,\"id\":\"EVALUATION_PROTOCOL_V1\",\"kind\":\"EVALUATION_PROTOCOL\",\"metrics\":[\"CONTRIBUTIONS\",\"RUN_RELATIVE_RETURN\",\"RUN_MAX_DRAWDOWN\",\"ACCOUNT_DRAWDOWN_FROM_HIGH_WATER\",\"REALIZED_PNL\",\"UNREALIZED_PNL\",\"FEES_PER_ASSET\",\"BASE_FEES_VALUED_AT_FILL_PRICE_LABELED\",\"COSTS_SPREAD_TO_TOUCH_THEN_SLIPPAGE_AND_TICK\",\"TIME_IN_MARKET\",\"TURNOVER_GROSS_OVER_MEAN_VALID_EQUITY\",\"HOLDING_DURATIONS\",\"TRADE_OUTCOME_DISTRIBUTION\",\"SIGNAL_OUTCOMES_AND_REJECTIONS\",\"PLANNED_VERSUS_REALIZED_LOSS\",\"GAPS\",\"DOWNTIME\",\"OWNER_INTERVENTIONS\"],\"minimum_sample\":{\"closed_positions\":10,\"paired_hours\":168},\"paired_samples\":\"STRATEGY_MINUS_BASELINE_HOURLY_LOG_RETURN_BOTH_SIDES_CONSECUTIVE_VALID\",\"returns\":\"LOG_RETURN_BETWEEN_CONSECUTIVE_VALID_POINTS\",\"schedule\":{\"daily\":\"00:10_AS_OF_00:00\",\"final\":\"AT_STOPPED_AS_OF_STOP\",\"snapshot\":\"HH:05_AS_OF_HH:00\"},\"segments\":\"NEW_SEGMENT_ON_CODE_IDENTITY_CHANGE_NEVER_STITCHED\",\"sharpe\":false,\"source\":\"docs/EVALUATION.md with ExecPlan 0015 section 5.5 engineering proposals\",\"start_point\":\"STARTUP_VALUATION_AT_ACTIVATION\",\"status\":\"PROPOSED\",\"strategy_nav\":\"HOURLY_VALUATION_FIRST_STEP_AT_OR_AFTER_EACH_UTC_HOUR\",\"uncertainty\":{\"confidence\":\"0.90\",\"floats\":\"BOOTSTRAP_STATISTICS_ONLY\",\"generator\":\"PYTHON_RANDOM_RANDOM_METHOD_ONLY\",\"interval\":\"PERCENTILE_NEAREST_RANK\",\"mean_block_hours\":24,\"method\":\"STATIONARY_BOOTSTRAP_POLITIS_ROMANO_1994\",\"resamples\":2000,\"seed\":\"FIRST_64_BITS_SHA256_MANIFEST_PROTOCOL_BASELINE_BLOCK\",\"sensitivity_mean_block_hours\":[6,72],\"statistic\":\"MEAN_PAIRED_HOURLY_LOG_RETURN_DIFFERENCE\"},\"version\":1}", "5385feb9bdc9fe513edb06a08615d6e06cf8586bd688602b29f32cd1ed60db4c"]
["BASELINE_SET_V1", "BASELINE_SET", 1, "PROPOSED", "{\"arithmetic\":\"EXACT_DECIMAL\",\"baselines\":[{\"id\":\"B0\",\"label\":\"Cash (virtual USDT)\",\"weights\":{}},{\"id\":\"B1\",\"label\":\"100% BTC buy-and-hold\",\"weights\":{\"BTCUSDT\":\"1\"}},{\"id\":\"B2\",\"label\":\"100% SOL buy-and-hold\",\"weights\":{\"SOLUSDT\":\"1\"}},{\"id\":\"B3\",\"label\":\"50% BTC / 50% SOL buy-and-hold\",\"weights\":{\"BTCUSDT\":\"0.5\",\"SOLUSDT\":\"0.5\"}},{\"id\":\"B4\",\"label\":\"25% BTC / 25% SOL / 50% cash (the notional caps)\",\"weights\":{\"BTCUSDT\":\"0.25\",\"SOLUSDT\":\"0.25\"}}],\"commission\":\"RUN_TAKER_RATE_CHARGED_IN_RECEIVED_ASSET\",\"flow_marks\":\"FIRST_USABLE_QUOTE_AT_OR_AFTER_FLOW_TIME_PLUS_RUN_ARRIVAL_DELAY\",\"flows\":\"ACTIVATION_AND_EACH_POSTED_TOPUP_UNITS_AT_PREFLOW_BASELINE_NAV_THEN_PRO_RATA_PURCHASE\",\"id\":\"BASELINE_SET_V1\",\"kind\":\"BASELINE_SET\",\"marking\":\"HOURLY_MARKS_BEST_BID\",\"participation\":\"NOT_APPLIED_IDEALIZED_LABELED\",\"purchase_price\":\"ASK_TIMES_ONE_PLUS_RUN_ADVERSE_SLIPPAGE_CEIL_TO_TICK\",\"quantity\":\"FLOOR_TO_LOT_STEP\",\"rebalancing\":\"NEVER\",\"source\":\"docs/EVALUATION.md baselines with ExecPlan 0015 section 5.5 engineering proposals\",\"start\":\"STRATEGY_EQUITY_AND_UNITS_AT_ACTIVATION\",\"status\":\"PROPOSED\",\"style\":\"BUY_AND_HOLD\",\"version\":1}", "ed78ef720cdd5ea414c66b12fcfa5b33c6c0a62667e7b6e661cca12634e1e2f3"]
"""

ACTIVE_STATES = "('DRAFT','READY','RUNNING','PAUSED','STOPPING')"
OWNER_EVENTS = ("CREATED", "MARKED_READY", "DISCARDED", "START_REQUESTED", "PAUSE_REQUESTED",
                "RESUME_REQUESTED", "FLATTEN_REQUESTED", "STOP_REQUESTED")
SYSTEM_EVENTS = ("ACTIVATED", "START_REJECTED", "PAUSE_APPLIED", "FLATTEN_APPLIED", "STOP_APPLIED",
                 "RESUME_APPLIED", "RESUME_REJECTED", "CAUSE_OPENED", "CAUSE_CLOSED", "PAUSED", "RESUMED",
                 "STOPPING", "STOPPED", "COMPLETED", "FAILED", "SEGMENT_STARTED", "EXECUTION_DOWNTIME",
                 "DRAWDOWN_UNRECOVERABLE")
CAUSES = "('OWNER','DAILY_LOSS','DRAWDOWN','INTEGRITY','APPROVAL_REVOKED')"
APPEND_ONLY = ("owner_approvals", "experiment_manifests", "experiment_events", "risk_latch_resolutions",
               "evaluation_marks", "evaluation_reports")
MODE_GUARDED = ("experiments",)


def _quoted(values: tuple[str, ...]) -> str:
    return "(" + ",".join(f"'{value}'" for value in values) + ")"


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    if bind.exec_driver_sql("SELECT EXISTS (SELECT 1 FROM orders WHERE run_ref IS NOT NULL)").scalar_one():
        raise RuntimeError("orders.run_ref is populated; M4 migration refuses to reinterpret it")

    op.execute("""
        ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check;
        ALTER TABLE execution_definitions ADD CONSTRAINT execution_definitions_kind_check
            CHECK (kind IN ('RISK_POLICY','STRATEGY','COST_MODEL','COST_SCENARIO','VALUATION_POLICY',
                'FILTER_POLICY','EVALUATION_PROTOCOL','BASELINE_SET')) NOT VALID;
        ALTER TABLE execution_definitions VALIDATE CONSTRAINT execution_definitions_kind_check;

        CREATE TABLE owner_approvals (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            target_kind varchar(24) NOT NULL CHECK (target_kind IN ('DEFINITION','EXPERIMENT_MANIFEST')),
            target_id varchar(64) NOT NULL,
            target_sha256 varchar(64) NOT NULL CHECK (target_sha256 ~ '^[0-9a-f]{64}$'),
            action varchar(8) NOT NULL CHECK (action IN ('APPROVE','REJECT','REVOKE')),
            owner_id smallint NOT NULL DEFAULT 1 CHECK (owner_id = 1),
            session_id uuid NOT NULL REFERENCES owner_sessions(id),
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL,
            expected_version bigint NOT NULL CHECK (expected_version >= 0),
            correlation_id varchar(80) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE INDEX owner_approvals_target ON owner_approvals(target_kind, target_id, target_sha256, seq);

        CREATE TABLE experiment_manifests (
            id uuid PRIMARY KEY,
            sha256 varchar(64) NOT NULL UNIQUE CHECK (sha256 ~ '^[0-9a-f]{64}$'),
            canonical text NOT NULL,
            manifest jsonb NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
    """)
    op.execute(f"""
        CREATE TABLE experiments (
            id uuid PRIMARY KEY,
            seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
            mode varchar(24) NOT NULL CHECK (mode IN ('FORWARD_PAPER','OFFLINE_TEST','HISTORICAL_RESEARCH')),
            manifest_id uuid NOT NULL REFERENCES experiment_manifests(id),
            state varchar(12) NOT NULL CHECK (state IN ('DRAFT','READY','RUNNING','PAUSED','STOPPING',
                'STOPPED','COMPLETED','FAILED')),
            version bigint NOT NULL DEFAULT 0 CHECK (version >= 0),
            idempotency_key varchar(80) NOT NULL UNIQUE,
            request_hash varchar(64) NOT NULL,
            created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE UNIQUE INDEX experiments_one_active_per_mode ON experiments(mode) WHERE state IN {ACTIVE_STATES};

        CREATE TABLE experiment_events (
            id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            experiment_id uuid NOT NULL REFERENCES experiments(id),
            actor varchar(8) NOT NULL CHECK (actor IN ('OWNER','SYSTEM')),
            kind varchar(32) NOT NULL CHECK (kind IN {_quoted(OWNER_EVENTS + SYSTEM_EVENTS)}),
            cause varchar(20) CHECK (cause IS NULL OR cause IN {CAUSES}),
            request_id bigint REFERENCES experiment_events(id),
            idempotency_key varchar(80) UNIQUE,
            request_hash varchar(64),
            detail jsonb NOT NULL DEFAULT '{{}}',
            at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT experiment_event_actor_kind CHECK (
                (actor = 'OWNER' AND kind IN {_quoted(OWNER_EVENTS)})
                OR (actor = 'SYSTEM' AND kind IN {_quoted(SYSTEM_EVENTS)})),
            CONSTRAINT experiment_event_owner_key CHECK (
                actor = 'SYSTEM' OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL))
        );
        CREATE INDEX experiment_events_experiment ON experiment_events(experiment_id, id);
        CREATE INDEX experiment_events_cause ON experiment_events(experiment_id, cause, id) WHERE cause IS NOT NULL;
        -- Each owner request is applied (or rejected) by the SYSTEM exactly once.
        CREATE UNIQUE INDEX experiment_events_applied_once ON experiment_events(request_id)
            WHERE request_id IS NOT NULL AND kind IN ('ACTIVATED','START_REJECTED','PAUSE_APPLIED',
                'FLATTEN_APPLIED','STOP_APPLIED','RESUME_APPLIED','RESUME_REJECTED');

        CREATE TABLE risk_latch_resolutions (
            id uuid PRIMARY KEY,
            latch_id uuid NOT NULL UNIQUE REFERENCES risk_latches(id),
            experiment_id uuid NOT NULL REFERENCES experiments(id),
            request_event_id bigint NOT NULL REFERENCES experiment_events(id),
            valuation_id uuid NOT NULL REFERENCES valuations(id),
            resolved_at timestamptz NOT NULL,
            detail jsonb NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );

        CREATE TABLE evaluation_marks (
            id uuid PRIMARY KEY,
            experiment_id uuid NOT NULL REFERENCES experiments(id),
            purpose varchar(8) NOT NULL CHECK (purpose IN ('HOURLY','FLOW')),
            symbol varchar(12) NOT NULL CHECK (symbol IN ('BTCUSDT','SOLUSDT')),
            mark_ref varchar(64) NOT NULL,
            mark_at timestamptz NOT NULL,
            observation_id uuid,
            sequence bigint,
            bid numeric(38,8),
            bid_qty numeric(38,8),
            ask numeric(38,8),
            ask_qty numeric(38,8),
            source_event_at timestamptz,
            received_at timestamptz,
            available_at timestamptz,
            quality varchar(12) NOT NULL,
            reason varchar(64),
            lot_step numeric(38,8),
            tick_size numeric(38,8),
            commission_precision smallint,
            captured_at timestamptz NOT NULL,
            recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
            CONSTRAINT evaluation_mark_once UNIQUE (experiment_id, purpose, symbol, mark_ref)
        );
        CREATE INDEX evaluation_marks_time ON evaluation_marks(experiment_id, purpose, mark_at);

        CREATE TABLE evaluation_reports (
            id uuid PRIMARY KEY,
            experiment_id uuid NOT NULL REFERENCES experiments(id),
            kind varchar(8) NOT NULL CHECK (kind IN ('SNAPSHOT','DAILY','FINAL','FAILURE')),
            as_of timestamptz NOT NULL,
            watermark bigint NOT NULL CHECK (watermark >= 0),
            protocol_sha256 varchar(64) NOT NULL,
            generator_identity varchar(64) NOT NULL,
            canonical text NOT NULL,
            sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{{64}}$'),
            created_at timestamptz NOT NULL DEFAULT clock_timestamp()
        );
        CREATE UNIQUE INDEX evaluation_reports_once ON evaluation_reports(experiment_id, kind, as_of)
            WHERE kind <> 'FAILURE';
        CREATE INDEX evaluation_reports_latest ON evaluation_reports(experiment_id, created_at DESC);
    """)

    # Run linkage: forward orders and mandates must name their experiment.
    op.execute("""
        ALTER TABLE orders DROP COLUMN run_ref;
        ALTER TABLE orders ADD COLUMN run_id uuid REFERENCES experiments(id);
        ALTER TABLE orders ADD CONSTRAINT orders_forward_run CHECK (mode <> 'FORWARD_PAPER' OR run_id IS NOT NULL) NOT VALID;
        ALTER TABLE orders VALIDATE CONSTRAINT orders_forward_run;
        ALTER TABLE position_mandates ADD COLUMN run_id uuid REFERENCES experiments(id);
        ALTER TABLE position_mandates ADD CONSTRAINT mandates_forward_run
            CHECK (mode <> 'FORWARD_PAPER' OR run_id IS NOT NULL) NOT VALID;
        ALTER TABLE position_mandates VALIDATE CONSTRAINT mandates_forward_run;
        ALTER TABLE strategy_evaluations ADD COLUMN run_id uuid REFERENCES experiments(id);
        ALTER TABLE risk_decisions ADD COLUMN run_id uuid REFERENCES experiments(id);
        ALTER TABLE valuations ADD COLUMN run_id uuid REFERENCES experiments(id);
        ALTER TABLE execution_incidents ADD COLUMN run_id uuid REFERENCES experiments(id);
        CREATE INDEX orders_run ON orders(run_id, seq) WHERE run_id IS NOT NULL;
        CREATE INDEX position_mandates_run ON position_mandates(run_id) WHERE run_id IS NOT NULL;
        CREATE INDEX valuations_run ON valuations(run_id, purpose, valued_at) WHERE run_id IS NOT NULL;
        CREATE INDEX strategy_evaluations_run ON strategy_evaluations(run_id) WHERE run_id IS NOT NULL;

        ALTER TABLE exit_obligations DROP CONSTRAINT exit_obligations_reason_check;
        ALTER TABLE exit_obligations ADD CONSTRAINT exit_obligations_reason_check CHECK (reason IN
            ('PROTECTIVE_STOP','OWNER_FLATTEN','TIME_EXIT','TREND_EXIT')) NOT VALID;
        ALTER TABLE exit_obligations VALIDATE CONSTRAINT exit_obligations_reason_check;
        ALTER TABLE orders DROP CONSTRAINT orders_origin_check;
        ALTER TABLE orders ADD CONSTRAINT orders_origin_check CHECK (origin IN
            ('ENTRY','PROTECTIVE_STOP','OWNER_FLATTEN','TIME_EXIT','TREND_EXIT')) NOT VALID;
        ALTER TABLE orders VALIDATE CONSTRAINT orders_origin_check;
        ALTER TABLE valuations DROP CONSTRAINT valuations_purpose_check;
        ALTER TABLE valuations ADD CONSTRAINT valuations_purpose_check CHECK (purpose IN ('PERIODIC','FILL',
            'HIGH_WATER','DAILY_REFERENCE','LATCH','TOPUP','STARTUP','HOURLY','RESUME')) NOT VALID;
        ALTER TABLE valuations VALIDATE CONSTRAINT valuations_purpose_check;
    """)

    op.execute("""
        CREATE FUNCTION asl_experiment_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE pair text := OLD.state || '>' || NEW.state;
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF NEW.id <> OLD.id OR NEW.seq <> OLD.seq OR NEW.mode <> OLD.mode
                    OR NEW.manifest_id <> OLD.manifest_id OR NEW.created_at <> OLD.created_at
                    OR NEW.idempotency_key <> OLD.idempotency_key OR NEW.request_hash <> OLD.request_hash THEN
                RAISE EXCEPTION 'experiment identity is immutable'; END IF;
            IF OLD.state IN ('COMPLETED','FAILED') THEN
                RAISE EXCEPTION 'terminal experiment cannot change'; END IF;
            IF NEW.version <> OLD.version + 1 THEN
                RAISE EXCEPTION 'experiment version must increase by exactly one'; END IF;
            IF NEW.state = OLD.state THEN RETURN NEW; END IF;
            IF current_user = 'asl_api' AND pair IN ('DRAFT>READY','DRAFT>STOPPED','READY>STOPPED') THEN
                RETURN NEW; END IF;
            IF current_user = 'asl_execution' AND (pair IN ('READY>RUNNING','RUNNING>PAUSED','PAUSED>RUNNING',
                    'RUNNING>STOPPING','PAUSED>STOPPING','STOPPING>STOPPED','STOPPED>COMPLETED')
                    OR (NEW.state = 'FAILED' AND OLD.state IN ('READY','RUNNING','PAUSED','STOPPING'))) THEN
                RETURN NEW; END IF;
            RAISE EXCEPTION 'experiment transition % is not allowed for %', pair, current_user;
        END $$;
        CREATE TRIGGER experiments_guard BEFORE UPDATE ON experiments
            FOR EACH ROW EXECUTE FUNCTION asl_experiment_guard();
        CREATE TRIGGER experiments_no_delete BEFORE DELETE ON experiments
            FOR EACH ROW EXECUTE FUNCTION asl_immutable();

        CREATE FUNCTION asl_experiment_event_actor() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF NEW.actor = 'OWNER' AND current_user = 'asl_api' THEN RETURN NEW; END IF;
            IF NEW.actor = 'SYSTEM' AND current_user = 'asl_execution' THEN RETURN NEW; END IF;
            RAISE EXCEPTION 'experiment event actor % is not permitted for %', NEW.actor, current_user;
        END $$;
        CREATE TRIGGER experiment_events_actor BEFORE INSERT ON experiment_events
            FOR EACH ROW EXECUTE FUNCTION asl_experiment_event_actor();

        CREATE FUNCTION asl_experiment_insert_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF NEW.state <> 'DRAFT' OR NEW.version <> 0 THEN
                RAISE EXCEPTION 'experiments start as version 0 drafts'; END IF;
            RETURN NEW;
        END $$;
        CREATE TRIGGER experiments_insert_guard BEFORE INSERT ON experiments
            FOR EACH ROW EXECUTE FUNCTION asl_experiment_insert_guard();
    """)
    for table in APPEND_ONLY:
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    for table in MODE_GUARDED:
        op.execute(f"CREATE TRIGGER {table}_mode BEFORE INSERT OR UPDATE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_execution_mode_guard()")

    for line in SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, digest = json.loads(line)
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
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
    database_name = os.environ.get("ASL_DB_NAME", "asl")
    with raw.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'asl_evaluation'")
        if cursor.fetchone() is None:
            # NOLOGIN until an explicit owner-instructed activation step grants a password.
            cursor.execute("CREATE ROLE asl_evaluation NOLOGIN")
        cursor.execute(sql.SQL("GRANT CONNECT ON DATABASE {} TO asl_evaluation").format(
            sql.Identifier(database_name)))
    m4_tables = ("owner_approvals, experiment_manifests, experiments, experiment_events, "
                 "risk_latch_resolutions, evaluation_marks, evaluation_reports")
    op.execute(f"GRANT SELECT ON {m4_tables} TO asl_api, asl_execution")
    op.execute("GRANT INSERT ON owner_approvals, experiment_manifests, experiments, experiment_events TO asl_api")
    op.execute("GRANT UPDATE (state, version, updated_at) ON experiments TO asl_api, asl_execution")
    op.execute("GRANT INSERT ON experiment_events, risk_latch_resolutions, evaluation_marks TO asl_execution")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE owner_approvals_seq_seq, experiments_seq_seq, "
               "experiment_events_id_seq TO asl_api")
    op.execute("GRANT USAGE, SELECT ON SEQUENCE experiment_events_id_seq TO asl_execution")
    op.execute("GRANT USAGE ON SCHEMA public TO asl_evaluation")
    op.execute(
        "GRANT SELECT ON alembic_version, execution_definitions, experiments, experiment_manifests, "
        "experiment_events, evaluation_marks, evaluation_reports, valuations, orders, fills, positions, "
        "position_mandates, position_events, strategy_evaluations, signal_outcomes, risk_decisions, "
        "execution_incidents, risk_latches, risk_latch_resolutions, funding_requests, execution_checkpoints, "
        "execution_steps TO asl_evaluation")
    op.execute("GRANT INSERT ON evaluation_reports TO asl_evaluation")


def downgrade() -> None:
    raise RuntimeError("M4 approvals, experiments and evaluation history cannot be downgraded destructively")
