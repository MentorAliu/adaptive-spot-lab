"""M8 update 2: in-force records, the model table, and pauses and latches that clear themselves.

Revision ID: 0011_m8_in_force
Revises: 0010_m8_short_check

ExecPlan 0031 sections 4.2, 4.5 and 9. Additive; nothing is written but the model table's seed row.

- ``owner_approvals`` and ``agent_approvals`` take an ``actor``: ``OWNER``, as every existing row is, or
  ``SYSTEM``, an in-force record the agent worker writes for what the installed code ships. A ``SYSTEM`` row
  carries no owner session and only ever approves. On ``owner_approvals`` it names a stored execution definition
  by its hash and is written only through ``asl_m8_record_definition`` (``asl_agent`` holds no privilege on that
  M4 table); on ``agent_approvals`` every check of 0009's guard applies to it as to the owner's record, and a
  runtime profile it names is one the app composed (``source`` ``SYSTEM``, nothing unset). The owner's rows are
  still written by ``asl_api`` only.
- ``MODEL_TABLE_V1`` (``app.agents.model_table``), frozen below, is the agent definitions' new kind; the runtime
  profile binds its hash with the others.
- An entry pause may be ended by ``SYSTEM``: the agent worker writes the resume 24 hours after the engine
  opened the pause, and the engine closes it as it closes the owner's.
- The execution engine may clear the account's integrity latch, both flags together; it does so only after a
  reconciliation that passes (``app.execution.engine``).

Downgrade refuses any ``SYSTEM`` row, then restores 0010's tables, triggers and grants.
"""

import hashlib
import json

from alembic import op

revision = "0011_m8_in_force"
down_revision = "0010_m8_short_check"
branch_labels = None
depends_on = None

AGENT_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "FEATURE_REGISTRY", "TEMPLATES", "BUDGETS",
               "EGRESS_ALLOWLIST", "PROMPT", "SOURCE_VERSION", "RESEARCH_ENVELOPE", "RESEARCH_PROTOCOL",
               "CANDIDATE_GRAMMAR")
APPROVALS = ("owner_approvals", "agent_approvals")
RUNTIME_EVENTS = ("REQUEST_APPLIED", "REQUEST_REJECTED", "STATE_CHANGED", "DISABLED_BY_OWNER", "EPOCH_INCREMENTED",
                  "DISCOVERY_RECORDED", "PROFILE_DRAFTED", "AUTH_REQUIRED", "AUTH_RESTORED", "QUOTA_BLOCKED",
                  "QUOTA_CLEARED", "CAPABILITY_LATCHED", "CAPABILITY_VERIFIED", "PROFILE_DRIFT", "WORKER_STARTED",
                  "WORKFLOW_EXPIRED")
# (table, trigger, events, 0010's function, 0011's function)
REPLACED = (("agent_approvals", "agent_approvals_m6_guard", "INSERT", "asl_m7_approval_guard", "asl_m8_approval_guard"),
            ("agent_runtime_profiles", "agent_runtime_profiles_actor", "INSERT", "asl_agent_actor_guard",
             "asl_m8_profile_actor_guard"),
            ("decision_pause_requests", "decision_pause_requests_guard", "INSERT", "asl_m7_pause_guard",
             "asl_m8_pause_guard"),
            ("account_state", "account_state_guard", "UPDATE", "asl_account_state_guard", "asl_m8_account_state_guard"))
HELPER = "asl_m8_execution_definition(text, text)"
RECORDER = "asl_m8_record_definition(text, text, text, text)"


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def model_table_rows():
    """The frozen model table row, checked against its own hash."""
    rows = []
    for line in MODEL_TABLE_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind != "MODEL_TABLE":
            raise RuntimeError("frozen model table seed is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def _events(m8):
    """The runtime event of the app moving the owner's switch to the profile in force (``app.agents.in_force``)."""
    kinds = (*RUNTIME_EVENTS, "PROFILE_IN_FORCE") if m8 else RUNTIME_EVENTS
    op.execute("ALTER TABLE agent_runtime_events DROP CONSTRAINT agent_runtime_events_kind_check, "
               f"ADD CONSTRAINT agent_runtime_events_kind_check CHECK (kind IN {_quoted(kinds)})")


def _triggers(m8):
    for table, trigger, events, before, after in REPLACED:
        op.execute(f"DROP TRIGGER {trigger} ON {table}")
        op.execute(f"CREATE TRIGGER {trigger} BEFORE {events} ON {table} "
                   f"FOR EACH ROW EXECUTE FUNCTION {after if m8 else before}()")


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    op.execute("ALTER TABLE agent_definitions DROP CONSTRAINT agent_definitions_kind_check, "
               f"ADD CONSTRAINT agent_definitions_kind_check CHECK (kind IN {_quoted((*AGENT_KINDS, 'MODEL_TABLE'))})")
    for row in model_table_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    for table in APPROVALS:
        op.execute(f"""
            ALTER TABLE {table} ADD COLUMN actor varchar(8) NOT NULL DEFAULT 'OWNER'
                    CHECK (actor IN ('OWNER','SYSTEM')),
                ALTER COLUMN session_id DROP NOT NULL,
                ADD CONSTRAINT {table}_actor_session CHECK ((actor = 'OWNER') = (session_id IS NOT NULL)),
                ADD CONSTRAINT {table}_system_approves CHECK (actor = 'OWNER' OR action = 'APPROVE')
        """)
    op.execute("""
        ALTER TABLE agent_runtime_profiles DROP CONSTRAINT agent_runtime_profiles_source_check,
            ADD CONSTRAINT agent_runtime_profiles_source_check CHECK (source IN ('DISCOVERY','OWNER','SYSTEM')),
            DROP CONSTRAINT agent_profile_owner_key,
            ADD CONSTRAINT agent_profile_owner_key CHECK (source <> 'OWNER'
                OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL)),
            ADD CONSTRAINT agent_profile_system_shape CHECK (source <> 'SYSTEM'
                OR num_nonnulls(idempotency_key, request_hash, session_id) = 0);
        ALTER TABLE decision_pause_requests DROP CONSTRAINT decision_pause_requests_actor_check,
            ADD CONSTRAINT decision_pause_requests_actor_check CHECK (actor IN ('AGENT','OWNER','SYSTEM')),
            ADD CONSTRAINT decision_pause_requests_system_shape CHECK (actor <> 'SYSTEM'
                OR num_nonnulls(workflow_id, tool_call_id, reason, cites, permission_epoch, session_id,
                                idempotency_key, request_hash, correlation_id) = 0);
    """)
    _events(True)
    op.execute(FUNCTIONS)
    _triggers(True)
    op.execute("CREATE TRIGGER owner_approvals_actor BEFORE INSERT ON owner_approvals "
               "FOR EACH ROW EXECUTE FUNCTION asl_m8_owner_approval_guard()")
    op.execute(GRANTS)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    if bind.exec_driver_sql("""
        SELECT (SELECT count(*) FROM owner_approvals WHERE actor = 'SYSTEM')
             + (SELECT count(*) FROM agent_approvals WHERE actor = 'SYSTEM')
             + (SELECT count(*) FROM agent_runtime_profiles WHERE source = 'SYSTEM')
             + (SELECT count(*) FROM decision_pause_requests WHERE actor = 'SYSTEM')
             + (SELECT count(*) FROM agent_runtime_events WHERE kind = 'PROFILE_IN_FORCE')
    """).scalar_one():
        raise RuntimeError("M8 in-force records exist; downgrade refused; fix forward")
    op.execute(REVOKES)
    op.execute("DROP TRIGGER owner_approvals_actor ON owner_approvals")
    _triggers(False)
    op.execute(f"DROP FUNCTION asl_m8_owner_approval_guard(), {HELPER}, {RECORDER}, "
               + ", ".join(item[4] + "()" for item in REPLACED))
    op.execute("""
        ALTER TABLE decision_pause_requests DROP CONSTRAINT decision_pause_requests_system_shape,
            DROP CONSTRAINT decision_pause_requests_actor_check,
            ADD CONSTRAINT decision_pause_requests_actor_check CHECK (actor IN ('AGENT','OWNER'));
        ALTER TABLE agent_runtime_profiles DROP CONSTRAINT agent_profile_system_shape,
            DROP CONSTRAINT agent_profile_owner_key,
            ADD CONSTRAINT agent_profile_owner_key CHECK (source = 'DISCOVERY'
                OR (idempotency_key IS NOT NULL AND request_hash IS NOT NULL AND session_id IS NOT NULL)),
            DROP CONSTRAINT agent_runtime_profiles_source_check,
            ADD CONSTRAINT agent_runtime_profiles_source_check CHECK (source IN ('DISCOVERY','OWNER'));
    """)
    _events(False)
    for table in APPROVALS:
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {table}_system_approves, "
                   f"DROP CONSTRAINT {table}_actor_session, DROP COLUMN actor, ALTER COLUMN session_id SET NOT NULL")
    # The seed store is immutable even for the migration role: relax only this trigger, inside this transaction,
    # and delete only the frozen, verified model table, as 0009's downgrade does.
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in model_table_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id=%(id)s AND sha256=%(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M8 seed mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("ALTER TABLE agent_definitions DROP CONSTRAINT agent_definitions_kind_check, "
               f"ADD CONSTRAINT agent_definitions_kind_check CHECK (kind IN {_quoted(AGENT_KINDS)})")


# The agent worker holds no grant on execution_definitions (0009 section 5.8); this one lookup, owned by the
# migration identity, gives a guard the definition stored with an id and hash, with its kind and status.
FUNCTIONS = """
CREATE FUNCTION asl_m8_execution_definition(p_id text, p_sha256 text) RETURNS jsonb
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp AS $$
    SELECT jsonb_build_object('kind', d.kind, 'status', d.status, 'definition', d.definition)
    FROM public.execution_definitions d WHERE d.id = p_id AND d.sha256 = p_sha256
$$;
REVOKE ALL ON FUNCTION asl_m8_execution_definition(text, text) FROM PUBLIC;
-- The app's in-force record of an execution definition. asl_agent holds no privilege on owner_approvals (an M4
-- relation): it records only through this function, which writes one SYSTEM approval of a stored, non-fixture
-- definition by its exact hash, under the key app.agents.in_force derives, and never over the owner's latest
-- REJECT or REVOKE of that target.
CREATE FUNCTION asl_m8_record_definition(p_id text, p_sha256 text, p_request_hash text, p_correlation text)
RETURNS boolean LANGUAGE plpgsql SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE v_status text; v_latest text; v_inserted uuid;
BEGIN
    -- The owner route's lock (app.experiments.approvals.LOCK_KEY): an owner's revocation lands before or after.
    PERFORM pg_advisory_xact_lock(4004001);
    SELECT d.status INTO v_status FROM public.execution_definitions d WHERE d.id = p_id AND d.sha256 = p_sha256;
    IF NOT FOUND OR v_status = 'FIXTURE_ONLY' THEN
        RAISE EXCEPTION 'the app records in force only a definition installed with that hash'; END IF;
    IF p_request_hash !~ '^[0-9a-f]{64}$' THEN RAISE EXCEPTION 'a request hash is 64 hex digits'; END IF;
    SELECT a.action INTO v_latest FROM public.owner_approvals a WHERE a.target_kind = 'DEFINITION'
        AND a.target_id = p_id AND a.target_sha256 = p_sha256 ORDER BY a.seq DESC LIMIT 1;
    IF v_latest IN ('REJECT','REVOKE') THEN RETURN false; END IF;
    INSERT INTO public.owner_approvals (id, target_kind, target_id, target_sha256, action, actor, session_id,
            idempotency_key, request_hash, expected_version, correlation_id)
        VALUES (gen_random_uuid(), 'DEFINITION', p_id, p_sha256, 'APPROVE', 'SYSTEM', NULL,
            'SYSTEM:' || encode(sha256(convert_to('DEFINITION|' || p_id || '|' || p_sha256, 'UTF8')), 'hex'),
            p_request_hash, 0, p_correlation)
        ON CONFLICT (idempotency_key) DO NOTHING RETURNING id INTO v_inserted;
    RETURN v_inserted IS NOT NULL;
END $$;
REVOKE ALL ON FUNCTION asl_m8_record_definition(text, text, text, text) FROM PUBLIC;
CREATE FUNCTION asl_m8_owner_approval_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF NEW.actor = 'OWNER' THEN
        IF current_user <> 'asl_api' THEN RAISE EXCEPTION 'an owner approval is the owner''s record'; END IF;
        RETURN NEW;
    END IF;
    -- asl_m8_record_definition writes the app's record as the migration owner; no identity writes one directly.
    RAISE EXCEPTION 'an in-force record is written by the agent worker through asl_m8_record_definition';
END $$;
CREATE FUNCTION asl_m8_profile_actor_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF NEW.source = 'OWNER' AND current_user = 'asl_api' THEN RETURN NEW; END IF;
    IF NEW.source IN ('DISCOVERY','SYSTEM') AND current_user = 'asl_agent' THEN RETURN NEW; END IF;
    RAISE EXCEPTION '% row is not permitted for %', TG_TABLE_NAME, current_user;
END $$;
CREATE FUNCTION asl_m8_pause_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE w record; c record; p record;
BEGIN
    NEW.created_at := clock_timestamp();
    IF NEW.kind = 'PAUSE' THEN
        IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
            RAISE EXCEPTION 'an entry pause is requested by the agent worker'; END IF;
        SELECT role, purpose, state INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
        IF NOT FOUND OR w.role <> 'COORDINATOR' OR w.purpose <> 'DECISION' THEN
            RAISE EXCEPTION 'only a coordinator decision workflow requests a pause; a probe never does'; END IF;
        IF w.state NOT IN ('RUNNING','WAITING_TOOL','WAITING_REVIEW') THEN
            RAISE EXCEPTION 'a pause comes from a workflow that is still running'; END IF;
        SELECT workflow_id, tool_name, decision, permission_epoch INTO c FROM agent_tool_calls
            WHERE id = NEW.tool_call_id;
        IF NOT FOUND OR c.workflow_id <> NEW.workflow_id OR c.tool_name <> 'request_entry_pause'
                OR c.decision <> 'AUTHORIZED' OR c.permission_epoch <> NEW.permission_epoch THEN
            RAISE EXCEPTION 'a pause binds its own authorized request_entry_pause call'; END IF;
        IF NOT EXISTS (SELECT 1 FROM decision_snapshots WHERE workflow_id = NEW.workflow_id AND run_id = NEW.run_id) THEN
            RAISE EXCEPTION 'a pause names its workflow''s own policy run'; END IF;
    ELSE
        IF NEW.actor = 'SYSTEM' THEN
            -- M8: the pause ends 24 hours after the engine opened it, by the agent worker's record.
            IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
                RAISE EXCEPTION 'the app ends an entry pause from the agent worker'; END IF;
            IF NOT EXISTS (SELECT 1 FROM agent_read.engine_decision_events e WHERE e.pause_request_id = NEW.pause_id
                           AND e.kind = 'PAUSE_OPENED' AND e.recorded_at <= NEW.created_at - interval '24 hours') THEN
                RAISE EXCEPTION 'the app ends an entry pause 24 hours after the engine opened it'; END IF;
        ELSIF current_user <> 'asl_api' AND NOT asl_is_superuser() THEN
            RAISE EXCEPTION 'only the owner resumes an entry pause'; END IF;
        SELECT kind, run_id INTO p FROM decision_pause_requests WHERE id = NEW.pause_id;
        IF NOT FOUND OR p.kind <> 'PAUSE' OR p.run_id <> NEW.run_id THEN
            RAISE EXCEPTION 'a resume names one pause of the same run'; END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m8_account_state_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    -- M8: the execution engine clears the integrity latch, both flags in one update, after a passing
    -- reconciliation (app.execution.engine.Engine.reconcile). No other role clears either flag.
    IF ((OLD.paused AND NOT NEW.paused) OR (OLD.reconciliation_failed AND NOT NEW.reconciliation_failed))
            AND (current_user <> 'asl_execution' OR NEW.paused OR NEW.reconciliation_failed) THEN
        IF OLD.paused AND NOT NEW.paused THEN
            RAISE EXCEPTION 'pause latch cannot be cleared by an application role'; END IF;
        RAISE EXCEPTION 'reconciliation latch cannot be cleared by an application role';
    END IF;
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
-- 0009's guard, with each record's actor: the owner's from asl_api, the app's from asl_agent. Every check of a
-- target applies to both. A runtime profile the app records is one it composed, with nothing unset.
CREATE FUNCTION asl_m8_approval_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE expected_hash text; p record; latest text; declaration jsonb; policy jsonb; stored jsonb; candidate uuid;
BEGIN
    IF NOT asl_is_superuser() THEN
        IF NEW.actor = 'OWNER' AND current_user <> 'asl_api' THEN
            RAISE EXCEPTION 'M6 approvals are owner records'; END IF;
        IF NEW.actor = 'SYSTEM' AND current_user <> 'asl_agent' THEN
            RAISE EXCEPTION 'an in-force record is written by the agent worker'; END IF;
    END IF;
    -- The app never records over the owner's no: a SYSTEM approval of a target whose latest decision is a
    -- rejection or revocation is refused (the agent worker checks this first, under the owner route's lock).
    IF NEW.actor = 'SYSTEM' AND (SELECT a.action FROM agent_approvals a WHERE a.target_kind = NEW.target_kind
            AND a.target_id = NEW.target_id AND a.target_sha256 = NEW.target_sha256
            ORDER BY a.seq DESC LIMIT 1) IN ('REJECT','REVOKE') THEN
        RAISE EXCEPTION 'the owner''s latest decision on this target is no'; END IF;
    IF NEW.target_kind = 'PROMOTION' THEN
        SELECT r.candidate_id INTO candidate FROM research_promotions r WHERE r.id::text = NEW.target_id;
        IF NOT FOUND THEN RAISE EXCEPTION 'M6 approval target/hash mismatch'; END IF;
        -- The candidate's lock first, then the request's state: a request SYSTEM withdraws in a transaction
        -- holding it (a superseded request for consideration) is read as it ends, not as it was.
        PERFORM pg_advisory_xact_lock(hashtextextended(candidate::text,608));
        SELECT r.sha256, r.state, r.candidate_id, r.document, w.template_id INTO p FROM research_promotions r
            JOIN agent_workflows w ON w.id = r.workflow_id WHERE r.id::text = NEW.target_id;
        expected_hash := p.sha256;
        SELECT action INTO latest FROM agent_approvals WHERE target_kind = 'PROMOTION' AND target_id = NEW.target_id
            AND target_sha256 = NEW.target_sha256 ORDER BY seq DESC LIMIT 1;
        IF NEW.action = 'REVOKE' THEN
            IF p.template_id <> 'PROMOTION_V2' OR latest IS DISTINCT FROM 'APPROVE'
                    OR p.state NOT IN ('PENDING','APPROVED') THEN
                RAISE EXCEPTION 'only an approved entry-basis promotion can be revoked'; END IF;
        ELSE
            IF p.state <> 'PENDING' OR latest IS NOT NULL THEN
                RAISE EXCEPTION 'a promotion is decided once, while it is pending'; END IF;
            IF NEW.action = 'APPROVE' THEN
                IF p.template_id <> 'PROMOTION_V2' THEN
                    RAISE EXCEPTION 'a request for consideration can only be rejected'; END IF;
                IF (SELECT state FROM research_candidate_events WHERE candidate_id = p.candidate_id
                        ORDER BY seq DESC LIMIT 1) IS DISTINCT FROM 'MAIN_APPROVAL_PENDING' THEN
                    RAISE EXCEPTION 'the candidate is not waiting for this approval'; END IF;
                stored := asl_m8_execution_definition(p.document->>'policy_id', p.document->>'policy_sha256');
                policy := CASE WHEN stored->>'kind' = 'STRATEGY' THEN stored->'definition' END;
                IF policy IS NULL OR p.document->>'requested_scope' IS DISTINCT FROM 'ENTRY_BASIS_UNDER_AGENT_POLICY_V1' THEN
                    RAISE EXCEPTION 'the promotion names no installed operating policy'; END IF;
                SELECT c.declaration INTO declaration FROM research_candidates c WHERE c.id = p.candidate_id;
                IF (declaration #>> '{exit,atr_period}') IS DISTINCT FROM (policy #>> '{protective_stop,atr_period}')
                        OR NOT EXISTS (SELECT 1 FROM jsonb_array_elements_text(policy #> '{protective_stop,multiples}') m(v)
                                       WHERE m.v::numeric = (declaration #>> '{exit,stop_multiple}')::numeric)
                        OR NOT EXISTS (SELECT 1 FROM jsonb_array_elements_text(policy -> 'max_hold_hours') h(v)
                                       WHERE h.v = (declaration #>> '{exit,max_hold_hours}')) THEN
                    RAISE EXCEPTION 'the candidate''s exit values lie outside the policy''s sets'; END IF;
            END IF;
        END IF;
    ELSIF NEW.target_kind IN ('SOURCE_VERSION','RESEARCH_ENVELOPE') THEN
        -- B5 of M6: a decision on a source version waits for a publication of evidence in flight, and a
        -- publication started later sees the decision. The key is app.sources.store.LOCK.
        IF NEW.target_kind = 'SOURCE_VERSION' THEN PERFORM pg_advisory_xact_lock(6005001); END IF;
        SELECT sha256 INTO expected_hash FROM agent_definitions WHERE id=NEW.target_id AND kind=NEW.target_kind;
    ELSIF NEW.actor = 'SYSTEM' THEN
        SELECT sha256 INTO expected_hash FROM agent_runtime_profiles WHERE id::text = NEW.target_id
            AND source = 'SYSTEM' AND jsonb_typeof(profile->'unset') = 'array'
            AND jsonb_array_length(profile->'unset') = 0;
    ELSE RETURN NEW;
    END IF;
    IF expected_hash IS NULL OR expected_hash <> NEW.target_sha256 THEN
        RAISE EXCEPTION 'M6 approval target/hash mismatch'; END IF;
    RETURN NEW;
END $$;
"""

GRANTS = """
GRANT EXECUTE ON FUNCTION asl_m8_execution_definition(text, text) TO asl_agent, asl_api;
GRANT EXECUTE ON FUNCTION asl_m8_record_definition(text, text, text, text) TO asl_agent;
GRANT INSERT ON agent_approvals TO asl_agent;
GRANT USAGE, SELECT ON SEQUENCE agent_approvals_seq_seq TO asl_agent;
"""
REVOKES = """
REVOKE USAGE, SELECT ON SEQUENCE agent_approvals_seq_seq FROM asl_agent;
REVOKE INSERT ON agent_approvals FROM asl_agent;
"""

# (id, kind, version, status, canonical JSON, SHA-256) from ``python -m app.agents.model_table``; a test checks
# that the code still prints this line.
MODEL_TABLE_LINES = r"""
["MODEL_TABLE_V1", "MODEL_TABLE", 1, "CODE_OWNED", "{\"id\":\"MODEL_TABLE_V1\",\"kind\":\"MODEL_TABLE\",\"roles\":{\"ANALYST\":[[\"gpt-6.1-sol\",\"medium\"],[\"gpt-6-sol\",\"medium\"],[\"gpt-5.6-sol\",\"medium\"]],\"COORDINATOR\":[[\"gpt-6.1-sol\",\"medium\"],[\"gpt-6-sol\",\"medium\"],[\"gpt-5.6-sol\",\"medium\"]],\"EVALUATOR\":[[\"gpt-6.1-sol\",\"high\"],[\"gpt-6-sol\",\"high\"],[\"gpt-5.6-sol\",\"high\"],[\"gpt-6.1-sol\",\"medium\"]],\"RESEARCHER\":[[\"gpt-6.1-sol\",\"medium\"],[\"gpt-6-sol\",\"medium\"],[\"gpt-5.6-sol\",\"medium\"]]},\"rule\":\"PER_ROLE_THE_FIRST_PAIR_WHOSE_MODEL_DISCOVERY_LISTS_AS_CODE_MODE_ONLY_WITH_THAT_EFFORT\",\"source\":\"ExecPlan 0030 sections 4.1 and 4.2\",\"status\":\"CODE_OWNED\",\"version\":1}", "f2030f16cb6ff3704ecc165f240c685298b8a412f583f39f4402efa5b0f4bfd1"]
"""
