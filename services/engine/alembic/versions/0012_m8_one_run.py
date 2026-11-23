"""M8 update 3: AGENT_POLICY_V2, and the main run the app keeps going.

Revision ID: 0012_m8_one_run
Revises: 0011_m8_in_force

ExecPlan 0031 sections 4.6 and 9. Additive.

- ``AGENT_POLICY_V2``, frozen below, is installed as the install command installs a policy (through
  ``asl_m7_install_definition``), unless a forward run of a strategy that is not an operating policy is open, which
  that function refuses; the agent worker then records it in force as it records every definition the code ships.
- The execution worker may write a run's ``SYSTEM`` records, as the owner's API writes the owner's: the next run's
  draft (``CREATED``), its readiness (``MARKED_READY``), the discard of a draft or ready run that never started
  (``DISCARDED``), ``START_REQUESTED`` and ``STOP_REQUESTED``. The engine applies the requests as it applies the
  owner's. A ``SYSTEM`` stop never flattens.
- ``asl_execution`` may insert a draft and its manifest and, for a run of an operating policy only, move a draft to
  ``READY`` once its manifest is in force and discard a draft or a ready run (to ``STOPPED``; neither ever
  started). The manifest's in-force record is written through ``asl_m8_record_manifest`` only: one ``SYSTEM``
  approval of a draft's manifest whose strategy is an installed operating policy in force, never over the owner's
  no.

Downgrade refuses any ``SYSTEM`` run record and any record of ``AGENT_POLICY_V2``, then restores 0011's
constraint, guard and grants and removes the uninstalled policy.
"""

import hashlib
import json

from alembic import op

revision = "0012_m8_one_run"
down_revision = "0011_m8_in_force"
branch_labels = None
depends_on = None

OWNER_EVENTS = ("CREATED", "MARKED_READY", "DISCARDED", "START_REQUESTED", "PAUSE_REQUESTED",
                "RESUME_REQUESTED", "FLATTEN_REQUESTED", "STOP_REQUESTED")
SYSTEM_EVENTS = ("ACTIVATED", "START_REJECTED", "PAUSE_APPLIED", "FLATTEN_APPLIED", "STOP_APPLIED",
                 "RESUME_APPLIED", "RESUME_REJECTED", "CAUSE_OPENED", "CAUSE_CLOSED", "PAUSED", "RESUMED",
                 "STOPPING", "STOPPED", "COMPLETED", "FAILED", "SEGMENT_STARTED", "EXECUTION_DOWNTIME",
                 "DRAWDOWN_UNRECOVERABLE")
# The run records the app writes from M8 (app.experiments.runs), beside the events it always wrote.
SYSTEM_REQUESTS = ("CREATED", "MARKED_READY", "DISCARDED", "START_REQUESTED", "STOP_REQUESTED")
RECORDER = "asl_m8_record_manifest(uuid, text, text)"
POLICY_LINES = r"""
["AGENT_POLICY_V2", "STRATEGY", 2, "PROPOSED", "{\"action_limits\":{\"accepted_entries_per_symbol\":1,\"accepted_entries_total\":2,\"entry_after_cancellation\":\"NOT_ON_THAT_BAR_OR_THE_NEXT\",\"notional\":\"COMMITTED_ENTRY_PLUS_FILLED_EXIT_NOTIONAL\",\"notional_fraction_of_equity\":\"0.75\",\"protective_exits\":\"NEVER_BLOCKED_BY_A_LIMIT_THEIR_FILLED_NOTIONAL_COUNTS\",\"reentry_cooldown_bars\":2,\"reentry_cooldown_bars_after_protective_stop\":6,\"submissions\":6,\"suppressed_protective_stop_counts\":true,\"window_hours\":24},\"adaptation\":\"NONE_A_CHANGED_VALUE_IS_A_NEW_VERSION_WITH_ITS_OWN_OWNER_APPROVAL\",\"agent_definitions\":{\"generation\":3,\"grants_sha256\":\"d221a70368b3820e6aa21a2302af4d2fc4514db35da531d3862468d13a796548\",\"prompts_sha256\":\"8ccbb7260a9d8d976eeffa70dc58fc1c94efbcfebc4d3f9b5bd893e183a2368a\",\"step_schema_sha256\":\"f112077d1bf3b19e03f3b14582ed8c6a4da8cc34d09f31b8922be1ca9a3abb9e\",\"templates_sha256\":\"92a32817ad911ac07da995fb00f8a062f5c1d37cad0aca85ae8e4be5a89d34cf\",\"tool_catalog_sha256\":\"f509c37073057f6d7088ad68c7826e56bfeb1c970f23352d9912d65bb60caa95\",\"work_budgets_sha256\":\"91aa828f6cba0cde9f0322849ca1d716857cb50656b3ecd041dd90bb1e8916e3\"},\"borrowing\":false,\"cadence\":{\"coalescing\":\"NEWEST_WAITING_TRIGGER_KEPT_OLDER_ONES_RECORDED_AS_SUPERSEDED\",\"cooldown_exempt\":[\"POSITION_EVENT\"],\"decision_after\":[\"REVIEWED_ASSESSMENT\",\"BAR_CLOSE_EVERY_FINALIZED_HOUR\",\"ENTRY_FILL\",\"POSITION_END\"],\"decision_start_cooldown_minutes\":10,\"market_brief_bar_close_hours_utc\":[0,6,12,18],\"open_decision_workflows\":1,\"staleness_minutes\":{\"ASSESSMENT_READY\":30,\"BAR_CLOSE\":20,\"POSITION_EVENT\":30},\"superseded\":\"A_NEWER_FINALIZED_BAR_BEFORE_SUBMISSION_ENDS_THE_WORKFLOW_EXPIRED_BAR_SUPERSEDED\"},\"decision_bar\":\"LATEST_FINALIZED_1H_BAR_CLOSED_AFTER_ACTIVATION_VALID_WHILE_IT_IS_THE_LATEST\",\"decisions\":[\"HOLD\",\"ABSTAIN\"],\"deviation\":{\"between\":\"ASK_IN_THE_DECIDING_STEP_AND_ASK_AT_THE_WORKFLOW_CUTOFF\",\"max_bps\":\"50\"},\"direction\":\"SPOT_LONG_ONLY\",\"entry_envelope\":\"COST_SCENARIO_ENVELOPE_OVER_THE_ENTRY_REFERENCE\",\"entry_evidence\":{\"alternative_basis\":\"APPROVED_CANDIDATE\",\"assessment\":\"MARKET_ASSESSMENT_OF_THE_SYMBOL_WITH_AN_ACCEPTABLE_REVIEW_INSIDE_ITS_OWN_EXPIRY\",\"assessment_max_age_hours\":12,\"enforced\":\"AT_SUBMISSION_BY_THE_DISPATCHER_AND_THE_DATABASE_GUARD\",\"feature_result\":\"OF_THE_OWN_WORKFLOW_FOR_THE_SYMBOL_AND_THE_DECISION_BAR\"},\"entry_reference\":\"BEST_ASK_OF_A_USABLE_QUOTE_IN_THE_STEP_THAT_TAKES_THE_INTENT\",\"evidence_conflict\":\"MISSING_OR_CONFLICTING_EVIDENCE_MEANS_NO_NEW_EXPOSURE\",\"execution\":{\"max_entry_attempts\":3,\"retryable_expiry_reasons\":[\"NO_ELIGIBLE_QUOTE\",\"ZERO_LIQUIDITY\"],\"signal_validity_ms\":3600000},\"exit_precedence\":[\"PROTECTIVE_STOP\",\"TIME_EXIT\",\"TREND_EXIT\"],\"exposure\":{\"fractions_of_equity\":[\"0.05\",\"0.10\",\"0.15\",\"0.20\",\"0.25\"],\"rule\":\"UPPER_BOUND_CODE_TAKES_THE_SMALLEST_OF_IT_AND_EVERY_RISK_LIMIT\"},\"failure\":\"NO_MODEL_REVIEWER_QUOTA_LOGIN_OR_REQUIRED_EVIDENCE_MEANS_NO_NEW_EXPOSURE_AND_NO_FALLBACK_POLICY\",\"id\":\"AGENT_POLICY_V2\",\"intent_expiry_minutes\":[10,20,30],\"intents\":[\"ENTER\",\"EXIT\",\"CANCEL_ENTRY\",\"TIGHTEN_STOP\"],\"kind\":\"STRATEGY\",\"label\":\"V1's PROPOSED engineering defaults with hourly entry checks; no measurement stands behind them\",\"max_hold_hours\":[24,48,72],\"model\":\"A_RUNTIME_PROFILE_THE_OWNER_APPROVED_FOR_EXACTLY_THESE_DEFINITIONS\",\"objective\":\"MANAGE_THE_PAPER_ACCOUNT_INSIDE_THIS_POLICY_WITHOUT_A_RETURN_TARGET\",\"policy_kind\":\"AGENT_DRIVEN\",\"position_terms\":{\"breakeven\":\"AVERAGE_COST_PER_UNIT_OF_THE_POSITION\",\"early_exit\":true,\"early_exit_obligation\":\"TREND_EXIT\",\"entry_rule\":\"AGENT_DISCRETIONARY_ENTRY_V1\",\"exit_rule\":\"AGENT_DISCRETIONARY_EXIT_V1\",\"never\":[\"LOOSEN_A_STOP\",\"EXTEND_A_HOLD\",\"CHANGE_THE_OWNER\"],\"stop_template\":\"LATEST_FINALIZED_CLOSE_MINUS_THE_POSITIONS_MULTIPLE_X_ATR\",\"stop_tightening\":[\"BREAKEVEN\",\"STOP_TEMPLATE\"],\"tightening\":\"STRICTLY_ABOVE_THE_STOP_IN_FORCE_AND_BELOW_THE_BID_AFTER_THE_FIRST_FILL\"},\"positions_per_symbol\":1,\"protective_stop\":{\"atr_method\":\"WILDER\",\"atr_period\":14,\"atr_seed\":\"MEAN_OF_FIRST_14_TRUE_RANGES_FROM_SECOND_BAR\",\"bars\":\"FINALIZED_1H_CONTIGUOUS_RUN_ENDING_AT_THE_DECISION_BAR\",\"gap_rule\":\"RESET_RUN_ON_MISSING_OR_UNCONFIRMED_HOUR\",\"min_bars\":15,\"multiples\":[\"1.5\",\"2.0\",\"2.5\",\"3.0\"],\"rule\":\"ENTRY_REFERENCE_MINUS_MULTIPLE_X_ATR\",\"run_window_max_bars\":720,\"stop_policy\":\"ENGINE_TRIGGER_MARKET_EXIT_ON_BID\",\"template\":\"ATR_STOP_V1\"},\"pyramiding\":false,\"reporting\":{\"baselines\":\"BASELINE_SET_V1\",\"protocol\":\"EVALUATION_PROTOCOL_V2\"},\"review\":{\"entry\":\"ACCEPTABLE_INTENT_REVIEW_OF_THE_EXACT_DRAFT_VALID_UNTIL_ITS_EXPIRY_WHILE_THE_STATE_KEY_HOLDS\",\"exit_cancel_tighten\":\"NONE\"},\"source\":\"docs/STRATEGIES.md AGENT_POLICY_V2: V1 with a decision at every finalized hourly bar (ExecPlan 0031)\",\"sources\":\"ITEMS_OF_SOURCE_VERSIONS_APPROVED_WHEN_THEY_WERE_FETCHED\",\"status\":\"PROPOSED\",\"symbol_priority\":[\"BTCUSDT\",\"SOLUSDT\"],\"time_exit\":\"FIRST_ELIGIBLE_OBSERVATION_AT_OR_AFTER_THE_CHOSEN_HOLD_FROM_FIRST_FILL\",\"timeframe\":\"1h\",\"universe\":[\"BTCUSDT\",\"SOLUSDT\"],\"version\":2}", "28182ce16d0ccfa70032bf3de74cd86cee9d0c7279d17bb03211147ac2ee55db"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def policy_rows():
    """The frozen policy row, checked against its own hash."""
    rows = []
    for line in POLICY_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind != "STRATEGY":
            raise RuntimeError("frozen AGENT_POLICY_V2 is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _events(m8):
    system = (*SYSTEM_EVENTS, *SYSTEM_REQUESTS) if m8 else SYSTEM_EVENTS
    op.execute(f"""
        ALTER TABLE experiment_events DROP CONSTRAINT experiment_event_actor_kind,
            ADD CONSTRAINT experiment_event_actor_kind CHECK (
                (actor = 'OWNER' AND kind IN {_quoted(OWNER_EVENTS)})
                OR (actor = 'SYSTEM' AND kind IN {_quoted(system)}))
    """)


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    _events(True)
    op.execute("ALTER TABLE experiment_events ADD CONSTRAINT experiment_event_system_stop_keeps_positions "
               "CHECK (actor = 'OWNER' OR kind <> 'STOP_REQUESTED' OR detail->'flatten' = 'false'::jsonb)")
    op.execute(FUNCTIONS)
    op.execute("DROP TRIGGER experiments_guard ON experiments")
    op.execute("CREATE TRIGGER experiments_guard BEFORE UPDATE ON experiments "
               "FOR EACH ROW EXECUTE FUNCTION asl_m8_experiment_guard()")
    op.execute(GRANTS)
    # As the install command installs a policy; 0009's function refuses while a forward run of a strategy that is
    # not an operating policy is open (the M4 pilot's kind). V2 is then not installed, and the app keeps the run
    # it has: nothing newer is in force.
    other = bind.exec_driver_sql("""
        SELECT count(*) FROM experiments x JOIN experiment_manifests m ON m.id = x.manifest_id
            LEFT JOIN execution_definitions s ON s.id = m.manifest #>> '{definitions,strategy,id}'
            WHERE x.mode = 'FORWARD_PAPER' AND x.state IN ('DRAFT','READY','RUNNING','PAUSED','STOPPING')
              AND (s.id IS NULL OR s.kind <> 'STRATEGY' OR s.definition->>'policy_kind' IS DISTINCT FROM 'AGENT_DRIVEN')
    """).scalar_one()
    if not other:
        for row in policy_rows():
            bind.exec_driver_sql(
                "SELECT asl_m7_install_definition(%(id)s, %(kind)s, %(version)s, %(status)s, %(canonical)s, "
                "%(sha256)s)", row)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    ids = [row["id"] for row in policy_rows()]
    if bind.exec_driver_sql(f"""
        SELECT (SELECT count(*) FROM experiment_events WHERE actor = 'SYSTEM' AND kind IN {_quoted(SYSTEM_REQUESTS)})
             + (SELECT count(*) FROM owner_approvals WHERE target_kind = 'EXPERIMENT_MANIFEST' AND actor = 'SYSTEM')
             + (SELECT count(*) FROM owner_approvals WHERE target_kind = 'DEFINITION' AND target_id IN {_quoted(ids)})
             + (SELECT count(*) FROM experiment_manifests WHERE manifest #>> '{{definitions,strategy,id}}' IN
                    {_quoted(ids)})
    """).scalar_one():
        raise RuntimeError("M8 run records exist; downgrade refused; fix forward")
    op.execute(REVOKES)
    op.execute("DROP TRIGGER experiments_guard ON experiments")
    op.execute("CREATE TRIGGER experiments_guard BEFORE UPDATE ON experiments "
               "FOR EACH ROW EXECUTE FUNCTION asl_experiment_guard()")
    op.execute(f"DROP FUNCTION asl_m8_experiment_guard(), {RECORDER}")
    op.execute("ALTER TABLE experiment_events DROP CONSTRAINT experiment_event_system_stop_keeps_positions")
    _events(False)
    # The definition store is immutable even for the migration role: relax only this trigger, inside this
    # transaction, and delete only the frozen, verified policy, which nothing names (checked above).
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in policy_rows():
        bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s", row)
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")


FUNCTIONS = """
-- 0006's guard, with three more transitions for the execution worker (app.experiments.runs), only for a run of an
-- operating policy: a draft to READY once its manifest is in force, and a draft or a ready run (neither ever
-- started) discarded. The reference's runs keep 0006's rules. Every other rule is 0006's.
CREATE FUNCTION asl_m8_experiment_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE pair text := OLD.state || '>' || NEW.state; m record;
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
    IF current_user = 'asl_execution' AND pair IN ('DRAFT>READY','DRAFT>STOPPED','READY>STOPPED') THEN
        SELECT x.id, x.sha256, d.definition->>'policy_kind' AS policy_kind INTO m
            FROM experiment_manifests x LEFT JOIN execution_definitions d
                ON d.id = x.manifest #>> '{definitions,strategy,id}'
                AND d.sha256 = x.manifest #>> '{definitions,strategy,sha256}' AND d.kind = 'STRATEGY'
            WHERE x.id = NEW.manifest_id;
        IF m.policy_kind IS DISTINCT FROM 'AGENT_DRIVEN' THEN
            RAISE EXCEPTION 'the app readies or discards only a run of an operating policy'; END IF;
        IF pair = 'DRAFT>READY' AND (SELECT a.action FROM owner_approvals a WHERE a.target_kind = 'EXPERIMENT_MANIFEST'
                AND a.target_id = m.id::text AND a.target_sha256 = m.sha256 ORDER BY a.seq DESC LIMIT 1)
                IS DISTINCT FROM 'APPROVE' THEN
            RAISE EXCEPTION 'the app marks a draft ready only once its manifest is in force'; END IF;
        RETURN NEW;
    END IF;
    IF current_user = 'asl_execution' AND (pair IN ('READY>RUNNING','RUNNING>PAUSED','PAUSED>RUNNING',
            'RUNNING>STOPPING','PAUSED>STOPPING','STOPPING>STOPPED','STOPPED>COMPLETED')
            OR (NEW.state = 'FAILED' AND OLD.state IN ('READY','RUNNING','PAUSED','STOPPING'))) THEN
        RETURN NEW; END IF;
    RAISE EXCEPTION 'experiment transition % is not allowed for %', pair, current_user;
END $$;
-- The app's in-force record of a run's manifest. asl_execution holds no privilege on owner_approvals: it records
-- only through this function, which writes one SYSTEM approval of a forward draft's manifest, by its exact hash,
-- when the manifest sets every slot and its strategy is an installed operating policy whose latest decision is an
-- approval, under the key app.experiments.runs derives, and never over the owner's latest REJECT or REVOKE.
CREATE FUNCTION asl_m8_record_manifest(p_manifest_id uuid, p_request_hash text, p_correlation text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE m record; s record; v_latest text; v_inserted uuid;
BEGIN
    -- The owner route's lock (app.experiments.approvals.LOCK_KEY): an owner's decision lands before or after.
    PERFORM pg_advisory_xact_lock(4004001);
    SELECT id, sha256, manifest INTO m FROM public.experiment_manifests WHERE id = p_manifest_id;
    IF NOT FOUND OR NOT EXISTS (SELECT 1 FROM public.experiments x WHERE x.manifest_id = m.id
                                AND x.mode = 'FORWARD_PAPER' AND x.state = 'DRAFT') THEN
        RAISE EXCEPTION 'the app records in force only the manifest of a forward draft'; END IF;
    IF jsonb_typeof(m.manifest->'unset') IS DISTINCT FROM 'array' OR jsonb_array_length(m.manifest->'unset') <> 0 THEN
        RAISE EXCEPTION 'a manifest with unset fields is never in force'; END IF;
    SELECT d.id, d.sha256, d.status, d.kind, d.definition INTO s FROM public.execution_definitions d
        WHERE d.id = m.manifest #>> '{definitions,strategy,id}' AND d.sha256 = m.manifest #>> '{definitions,strategy,sha256}';
    IF NOT FOUND OR s.kind <> 'STRATEGY' OR s.definition->>'policy_kind' IS DISTINCT FROM 'AGENT_DRIVEN'
            OR s.status = 'FIXTURE_ONLY' THEN
        RAISE EXCEPTION 'the app starts only a run of an installed operating policy'; END IF;
    IF (SELECT a.action FROM public.owner_approvals a WHERE a.target_kind = 'DEFINITION' AND a.target_id = s.id
            AND a.target_sha256 = s.sha256 ORDER BY a.seq DESC LIMIT 1) IS DISTINCT FROM 'APPROVE' THEN
        RAISE EXCEPTION 'the run''s policy is not in force'; END IF;
    IF p_request_hash !~ '^[0-9a-f]{64}$' THEN RAISE EXCEPTION 'a request hash is 64 hex digits'; END IF;
    SELECT a.action INTO v_latest FROM public.owner_approvals a WHERE a.target_kind = 'EXPERIMENT_MANIFEST'
        AND a.target_id = m.id::text AND a.target_sha256 = m.sha256 ORDER BY a.seq DESC LIMIT 1;
    IF v_latest IN ('REJECT','REVOKE') THEN RETURN false; END IF;
    INSERT INTO public.owner_approvals (id, target_kind, target_id, target_sha256, action, actor, session_id,
            idempotency_key, request_hash, expected_version, correlation_id)
        VALUES (gen_random_uuid(), 'EXPERIMENT_MANIFEST', m.id::text, m.sha256, 'APPROVE', 'SYSTEM', NULL,
            'SYSTEM:' || encode(sha256(convert_to('EXPERIMENT_MANIFEST|' || m.id::text || '|' || m.sha256, 'UTF8')),
                                'hex'),
            p_request_hash, 0, p_correlation)
        ON CONFLICT (idempotency_key) DO NOTHING RETURNING id INTO v_inserted;
    RETURN v_inserted IS NOT NULL;
END $$;
REVOKE ALL ON FUNCTION asl_m8_record_manifest(uuid, text, text) FROM PUBLIC;
"""

GRANTS = """
GRANT INSERT ON experiments, experiment_manifests TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE experiments_seq_seq TO asl_execution;
GRANT EXECUTE ON FUNCTION asl_m8_record_manifest(uuid, text, text) TO asl_execution;
"""

REVOKES = """
REVOKE EXECUTE ON FUNCTION asl_m8_record_manifest(uuid, text, text) FROM asl_execution;
REVOKE USAGE, SELECT ON SEQUENCE experiments_seq_seq FROM asl_execution;
REVOKE INSERT ON experiments, experiment_manifests FROM asl_execution;
"""
