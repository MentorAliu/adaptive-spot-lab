"""M7 hand-off tables, policy-run views, the epoch hold and the guarded definition install.

Revision ID: 0009_m7_agent_decisions
Revises: 0008_m6_research

ExecPlan 0026 sections 5.3 and 12. No table, constraint, index, trigger or grant of M1-M4 changes, and
nothing is written into one: M1-M4 tables are named only inside the bodies of views and functions. The ten
``decision_`` tables are insert-only and reference no M1-M4 table by foreign key; guard triggers check what
a key would, reading without locking. Agent rows are written by ``asl_agent`` (the owner's resume of a pause
by ``asl_api``), engine rows by ``asl_execution``. ``asl_agent`` reads the policy's own run through
``agent_read`` views; ``asl_execution`` reads four agent tables and holds the permission epoch through one
function. The operating policy and its protocol are installed at the experiment boundary by
``asl_m7_install_definition`` as the migration identity (``python -m app.execution.identity
install-definitions``), never by this migration. Only M5/M6 agent checks widen; the two guards M6 left for
this migration are added (R25). Downgrade refuses any M7 record or installed definition, then restores 0008.
Later M7 batches may amend this revision before its first deployment (ExecPlan 0026 section 9).

B5 adds: the generation-3 agent definitions (a frozen seed beside the M5 and M6 rows), the probe run's suite
with the policy a decision suite runs on, the owner's ``DECISION_PROBE`` request, the verification guard's
check of that suite, and the brief as an assessment an entry may cite.

B6b adds ``evaluation_read`` (section 5.11): column-limited views of a run's decision records for
``asl_evaluation``, which computes the decision measures of ``EVALUATION_PROTOCOL_V2`` from them. They carry
codes, states, counts and times, never a document's text; ``asl_evaluation`` gains no grant on any agent or
decision table.

B6c adds the control replay (section 5.11): a deferred replay of the reference over each agent run's window,
in periods of a shadow's longest window. ``research_read.agent_runs`` shows ``asl_research`` the main account's
activated agent-driven runs (their identity, policy, state, activation and end, nothing of their account);
``research_controls`` and ``research_control_marks`` hold the periods and their immutable marks; and
``research_jobs`` takes ``CONTROL`` work, which names no hypothesis or candidate, as ``research_results``
then does. One M7 function guards control work on all four tables.

B6 adds promotion approval (section 5.10): the promotion's ``APPROVED`` and ``REVOKED`` states, the
candidate's ``MAIN_APPROVED`` with the owner's approval row, and the entry on an approved candidate. Three M7
functions replace 0008's checks of a promotion, of its owner decision and of a candidate's transition on those
three tables only; 0008's functions keep guarding every other table, and the downgrade restores them.

B7 adds the owner's starts of the three generation-3 templates that name OWNER as a starter (section 5.12):
0008's workflow guard, unchanged but for its owner pairs, which the downgrade restores.
"""

import hashlib
import json

from alembic import op

revision = "0009_m7_agent_decisions"
down_revision = "0008_m6_research"
branch_labels = None
depends_on = None

TABLES = ("decision_snapshots", "decision_intents", "decision_submissions", "decision_withdrawals",
          "decision_verifications", "decision_pause_requests", "decision_events", "decision_position_terms",
          "decision_stop_updates", "decision_outcomes")
AGENT_WRITTEN = ("decision_snapshots", "decision_intents", "decision_submissions", "decision_withdrawals",
                 "decision_verifications", "decision_pause_requests", "decision_outcomes")
EXECUTION_WRITTEN = ("decision_events", "decision_position_terms", "decision_stop_updates")
DOCUMENTED = ("decision_snapshots", "decision_intents", "decision_outcomes")
# What the engine reads of the agents' tables (section 5.3): requests it validates, nothing else.
EXECUTION_READS = ("decision_intents", "decision_submissions", "decision_withdrawals", "decision_pause_requests")
GUARDED = {"decision_snapshots": "asl_m7_snapshot_guard", "decision_intents": "asl_m7_intent_guard",
           "decision_submissions": "asl_m7_submission_guard", "decision_withdrawals": "asl_m7_withdrawal_guard",
           "decision_verifications": "asl_m7_verification_guard", "decision_pause_requests": "asl_m7_pause_guard",
           "decision_events": "asl_m7_event_guard", "decision_position_terms": "asl_m7_terms_guard",
           "decision_stop_updates": "asl_m7_stop_guard", "decision_outcomes": "asl_m7_outcome_guard"}
FUNCTIONS = ("asl_m7_content_guard()", "asl_m7_owner_shape_guard()", *(name + "()" for name in GUARDED.values()),
             "asl_m7_control_guard()")
OWNER_SHAPED = ("research_jobs", "research_shadows", "source_refresh_requests")
VIEWS = tuple("agent_read." + name for name in (
    "policy_runs", "policy_definitions", "policy_approvals", "policy_run_events", "policy_positions",
    "policy_position_events", "policy_orders", "policy_order_events", "policy_fills", "policy_exit_obligations",
    "policy_evaluations", "policy_risk_decisions", "policy_valuations", "policy_account", "policy_holdings",
    "policy_daily_references", "policy_latches", "engine_decision_events", "engine_position_terms",
    "engine_stop_updates"))
# B6b: what the evaluation identity reads of a run's decisions (section 5.11), in creation order.
EVALUATION_VIEWS = tuple("evaluation_read." + name for name in (
    "decision_intents", "decision_submissions", "decision_events", "decision_withdrawals",
    "decision_pause_requests", "decision_workflows", "decision_steps", "decision_tool_calls", "decision_reviews",
    "decision_documents", "runtime_events"))
# B6c: the control replay's tables, the research identity's view of the agent runs, and the M6 tables whose
# rows its work also writes (section 5.11).
CONTROL_TABLES = ("research_controls", "research_control_marks")
RESEARCH_VIEWS = ("research_read.agent_runs",)
CONTROL_WORK = ("research_jobs", "research_results")
M6_JOB_KINDS = ("SCREEN", "FULL", "SHADOW")
M7_JOB_KINDS = (*M6_JOB_KINDS, "CONTROL")
OPEN_WORKFLOW = "('QUEUED','RUNNING','WAITING_TOOL','WAITING_REVIEW')"
OPEN_EXPERIMENT = "('DRAFT','READY','RUNNING','PAUSED','STOPPING')"
INSTALL = "asl_m7_install_definition(text,text,integer,text,text,text)"
HOLD = "decision_hold_permission_epoch()"

# The M5/M6 agent checks as 0008 left them, and what generation 3 adds (section 5.6). Owner-startable
# template pairs (B7), the probe-run suite (B5) and the promotion's APPROVED state (B6) came with the batches that
# use them.
M6_VALUES = {
    ("agent_workflows", "purpose"): ("ASSESSMENT", "REVIEW", "PROBE", "INVESTIGATION", "RESEARCH",
                                     "CANDIDATE_REVIEW", "PROMOTION"),
    ("agent_workflows", "created_by"): ("OWNER", "ORCHESTRATOR", "PROBE_RUN", "FIXTURE", "SYSTEM", "SOURCE_TRIGGER",
                                        "SCHEDULE", "FOLLOW_ON"),
    ("agent_artifacts", "kind"): ("MARKET_ASSESSMENT", "EVALUATION_REVIEW", "RESEARCH_PROPOSAL", "PROMOTION_PROPOSAL"),
    ("agent_triggers", "family"): ("SOURCE_REVISION", "SCHEDULED_RESEARCH", "FOLLOW_ON"),
}
M7_ADDED = {
    ("agent_workflows", "purpose"): ("DECISION", "BRIEF", "INTENT_REVIEW", "OUTCOME_REVIEW"),
    ("agent_workflows", "created_by"): ("DECISION_TRIGGER",),
    ("agent_artifacts", "kind"): ("PORTFOLIO_DECISION",),
    ("agent_triggers", "family"): ("BAR_CLOSE", "POSITION_EVENT", "ASSESSMENT_READY"),
}
M6_CHILDREN = ("REVIEW", "CANDIDATE_REVIEW")
M7_CHILDREN = ("REVIEW", "CANDIDATE_REVIEW", "INTENT_REVIEW")
# 0007's request kinds, and the owner's request for the decision suite (B5).
M6_REQUEST_KINDS = ("ACTIVATE", "ENABLE", "DISABLE", "PROBE", "CANCEL_WORKFLOW")
M7_REQUEST_KINDS = (*M6_REQUEST_KINDS, "DECISION_PROBE")
SEED_KINDS = ("AGENT_STEP_SCHEMA", "TOOL_CATALOG", "ROLE_GRANTS", "TEMPLATES", "BUDGETS", "PROMPT")
# B6: the promotion's states, and the three triggers whose M6 functions the M7 ones replace (section 5.10).
M6_PROMOTION_STATES = ("PENDING", "REJECTED", "WITHDRAWN")
M7_PROMOTION_STATES = ("PENDING", "APPROVED", "REJECTED", "WITHDRAWN", "REVOKED")
REPLACED = (("research_promotions", "research_promotions_guard", "INSERT OR UPDATE", "asl_m6_transition_guard",
             "asl_m7_promotion_guard"),
            ("research_candidate_events", "research_candidate_events_guard", "INSERT", "asl_m6_candidate_guard",
             "asl_m7_candidate_guard"),
            ("agent_approvals", "agent_approvals_m6_guard", "INSERT", "asl_m6_approval_guard",
             "asl_m7_approval_guard"))


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


# B7 (section 5.12): the owner starts the three generation-3 templates whose definitions name OWNER as a
# starter. 0008's workflow guard, unchanged but for its owner pairs; the downgrade restores 0008's four.
M6_OWNER_PAIRS = (("MARKET_ASSESSMENT_V1", "ASSESSMENT", "ANALYST"),
                  ("EVENT_INVESTIGATION_V1", "INVESTIGATION", "ANALYST"),
                  ("RESEARCH_V1", "RESEARCH", "RESEARCHER"), ("PROMOTION_V1", "PROMOTION", "COORDINATOR"))
M7_OWNER_PAIRS = (*M6_OWNER_PAIRS, ("MARKET_BRIEF_V1", "BRIEF", "ANALYST"),
                  ("PORTFOLIO_DECISION_V1", "DECISION", "COORDINATOR"), ("PROMOTION_V2", "PROMOTION", "COORDINATOR"))


def _workflow_guard(m7):
    owner_pairs = "(" + "\n                     OR ".join(
        f"(NEW.template_id = '{template}' AND NEW.purpose = '{purpose}' AND NEW.role = '{role}')"
        for template, purpose, role in (M7_OWNER_PAIRS if m7 else M6_OWNER_PAIRS)) + ")"
    terminal = _quoted(("SUCCEEDED", "ABSTAINED", "REJECTED_OUTPUT", "EXPIRED", "AUTH_REQUIRED", "QUOTA_BLOCKED",
                        "FAILED", "CANCELED"))
    op.execute(f"""
        CREATE OR REPLACE FUNCTION asl_agent_workflow_guard() RETURNS trigger LANGUAGE plpgsql AS $$
        DECLARE pair text;
        BEGIN
            IF asl_is_superuser() THEN RETURN NEW; END IF;
            IF TG_OP = 'INSERT' THEN
                IF NEW.mode = 'OFFLINE_TEST' AND current_database() NOT LIKE 'asl\\_m1\\_%' THEN
                    RAISE EXCEPTION 'OFFLINE_TEST agent workflows require a disposable asl_m1_ database'; END IF;
                IF NEW.version <> 0 THEN RAISE EXCEPTION 'agent workflows start at version 0'; END IF;
                IF current_user = 'asl_api' AND NEW.created_by = 'OWNER' AND NEW.state = 'QUEUED'
                        AND NEW.parent_id IS NULL AND {owner_pairs}
                        AND NEW.provider = 'CODEX' AND NEW.permission_epoch IS NULL
                        AND NEW.cutoff IS NULL AND NEW.started_at IS NULL THEN RETURN NEW; END IF;
                IF current_user = 'asl_agent' AND NEW.created_by <> 'OWNER' AND NEW.state IN ('QUEUED','RUNNING') THEN
                    RETURN NEW; END IF;
                RAISE EXCEPTION 'agent workflow insert is not permitted for %', current_user;
            END IF;
            pair := OLD.state || '>' || NEW.state;
            IF NEW.id <> OLD.id OR NEW.seq <> OLD.seq OR NEW.parent_id IS DISTINCT FROM OLD.parent_id
                    OR NEW.template_id <> OLD.template_id OR NEW.role <> OLD.role OR NEW.purpose <> OLD.purpose
                    OR NEW.mode <> OLD.mode OR NEW.provider <> OLD.provider OR NEW.created_by <> OLD.created_by
                    OR NEW.params <> OLD.params OR NEW.idempotency_key IS DISTINCT FROM OLD.idempotency_key
                    OR NEW.request_hash IS DISTINCT FROM OLD.request_hash OR NEW.created_at <> OLD.created_at
                    OR NEW.queued_until <> OLD.queued_until THEN
                RAISE EXCEPTION 'agent workflow identity is immutable'; END IF;
            IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'only the agent worker changes workflows'; END IF;
            IF OLD.state IN {terminal} THEN RAISE EXCEPTION 'terminal agent workflow cannot change'; END IF;
            IF NEW.version <> OLD.version + 1 THEN RAISE EXCEPTION 'agent workflow version must increase by one'; END IF;
            IF OLD.permission_epoch IS NOT NULL AND NEW.permission_epoch IS DISTINCT FROM OLD.permission_epoch THEN
                RAISE EXCEPTION 'agent workflow epoch binding is immutable'; END IF;
            IF OLD.cutoff IS NOT NULL AND NEW.cutoff IS DISTINCT FROM OLD.cutoff THEN
                RAISE EXCEPTION 'agent workflow cutoff is immutable'; END IF;
            IF NEW.state = OLD.state THEN RETURN NEW; END IF;
            IF pair IN ('QUEUED>RUNNING','RUNNING>WAITING_TOOL','WAITING_TOOL>RUNNING','RUNNING>WAITING_REVIEW')
                    OR (OLD.state = 'QUEUED' AND NEW.state IN ('EXPIRED','CANCELED','FAILED'))
                    OR (OLD.state IN ('RUNNING','WAITING_TOOL') AND NEW.state IN {terminal})
                    OR (OLD.state = 'WAITING_REVIEW' AND NEW.state IN ('SUCCEEDED','CANCELED','FAILED','EXPIRED')) THEN
                RETURN NEW; END IF;
            RAISE EXCEPTION 'agent workflow transition % is not allowed', pair;
        END $$;
    """)


def _checks(m7):
    for (table, column), values in M6_VALUES.items():
        name = table + "_" + column + "_check"
        allowed = values + M7_ADDED[(table, column)] if m7 else values
        op.execute(f"ALTER TABLE {table} DROP CONSTRAINT {name}")
        op.execute(f"ALTER TABLE {table} ADD CONSTRAINT {name} CHECK ({column} IN {_quoted(allowed)})")
    op.execute("ALTER TABLE agent_workflows DROP CONSTRAINT agent_workflow_child")
    children = M7_CHILDREN if m7 else M6_CHILDREN
    op.execute("ALTER TABLE agent_workflows ADD CONSTRAINT agent_workflow_child "
               f"CHECK ((purpose IN {_quoted(children)}) = (parent_id IS NOT NULL))")
    kinds = M7_REQUEST_KINDS if m7 else M6_REQUEST_KINDS
    op.execute("ALTER TABLE agent_runtime_requests DROP CONSTRAINT agent_runtime_requests_kind_check")
    op.execute("ALTER TABLE agent_runtime_requests ADD CONSTRAINT agent_runtime_requests_kind_check "
               f"CHECK (kind IN {_quoted(kinds)})")
    states = M7_PROMOTION_STATES if m7 else M6_PROMOTION_STATES
    op.execute("ALTER TABLE research_promotions DROP CONSTRAINT research_promotions_state_check")
    op.execute("ALTER TABLE research_promotions ADD CONSTRAINT research_promotions_state_check "
               f"CHECK (state IN {_quoted(states)})")


def _promotion_guards(m7):
    """B6: the trigger of each table in ``REPLACED`` runs the M7 function, or 0008's again."""
    for table, trigger, events, m6_function, m7_function in REPLACED:
        op.execute(f"DROP TRIGGER {trigger} ON {table}")
        op.execute(f"CREATE TRIGGER {trigger} BEFORE {events} ON {table} "
                   f"FOR EACH ROW EXECUTE FUNCTION {m7_function if m7 else m6_function}()")


def _control_work(m7):
    """B6c: research jobs take CONTROL work, which names no hypothesis or candidate; so does its result."""
    kinds = M7_JOB_KINDS if m7 else M6_JOB_KINDS
    if not m7:
        op.execute("ALTER TABLE research_jobs DROP CONSTRAINT research_jobs_control_subject")
    op.execute("ALTER TABLE research_jobs DROP CONSTRAINT research_jobs_kind_check")
    op.execute(f"ALTER TABLE research_jobs ADD CONSTRAINT research_jobs_kind_check CHECK (kind IN {_quoted(kinds)})")
    nulls = "DROP NOT NULL" if m7 else "SET NOT NULL"
    op.execute(f"ALTER TABLE research_jobs ALTER COLUMN hypothesis_id {nulls}, ALTER COLUMN candidate_id {nulls}")
    op.execute(f"ALTER TABLE research_results ALTER COLUMN candidate_id {nulls}")
    if m7:
        op.execute("ALTER TABLE research_jobs ADD CONSTRAINT research_jobs_control_subject "
                   "CHECK (num_nulls(hypothesis_id, candidate_id) = CASE WHEN kind = 'CONTROL' THEN 2 ELSE 0 END)")


def agent_seed_rows():
    """The frozen generation-3 rows, each checked against its own hash."""
    rows = []
    for line in AGENT_SEED_LINES_V3.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in SEED_KINDS:
            raise RuntimeError("frozen agent seed is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    # R25's unique index below cannot be built over two open promotions of one candidate; say so by name.
    if op.get_bind().exec_driver_sql(
            "SELECT count(*) FROM (SELECT 1 FROM agent_workflows WHERE purpose = 'PROMOTION' AND state IN "
            + OPEN_WORKFLOW + " GROUP BY params->>'candidate_id' HAVING count(*) > 1) duplicated").scalar_one():
        raise RuntimeError("a candidate has two open promotion workflows; end one, then migrate")
    _checks(True)
    _workflow_guard(True)
    op.execute(PROBE_SUITE)
    bind = op.get_bind()
    for row in agent_seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO agent_definitions (id,kind,version,status,definition,canonical,sha256) "
            "VALUES (%(id)s,%(kind)s,%(version)s,%(status)s,CAST(%(document)s AS jsonb),%(canonical)s,%(sha256)s)",
            {**row, "document": row["canonical"]})
    op.execute(DDL)
    op.execute(VIEW_SQL)
    op.execute(EVALUATION_VIEW_SQL)
    op.execute(GUARDS)
    op.execute(PROMOTION_GUARDS)
    _promotion_guards(True)
    op.execute(FUNCTION_SQL)
    _control_work(True)
    op.execute(CONTROL_SQL)
    for table in TABLES:
        op.execute(f"CREATE TRIGGER {table}_guard BEFORE INSERT ON {table} "
                   f"FOR EACH ROW EXECUTE FUNCTION {GUARDED[table]}()")
        op.execute(f"CREATE TRIGGER {table}_immutable BEFORE UPDATE OR DELETE ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    for table in AGENT_WRITTEN:
        op.execute(f"CREATE TRIGGER {table}_fixture BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m6_fixture_guard()")
    for table in EXECUTION_WRITTEN:
        op.execute(f"CREATE TRIGGER {table}_mode BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_execution_mode_guard()")
    for table in DOCUMENTED:
        op.execute(f"CREATE TRIGGER {table}_content BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard()")
    # R25 (ExecPlan 0023 B7 review, left for this migration): no identity can shape a row like an owner
    # request, and one open promotion workflow per candidate. The scheduler and the owner route answer the
    # unique violation (app.agents.workflows, app.agents.controls).
    for table in OWNER_SHAPED:
        op.execute(f"CREATE TRIGGER {table}_owner_shape BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m7_owner_shape_guard()")
    op.execute("CREATE UNIQUE INDEX agent_workflows_one_open_promotion ON agent_workflows ((params->>'candidate_id')) "
               f"WHERE purpose = 'PROMOTION' AND state IN {OPEN_WORKFLOW}")
    for table in CONTROL_TABLES:
        op.execute(f"CREATE TRIGGER {table}_fixture BEFORE INSERT ON {table} "
                   "FOR EACH ROW EXECUTE FUNCTION asl_m6_fixture_guard()")
    op.execute("CREATE TRIGGER research_controls_guard BEFORE INSERT OR UPDATE ON research_controls "
               "FOR EACH ROW EXECUTE FUNCTION asl_m7_control_guard()")
    op.execute("CREATE TRIGGER research_controls_no_delete BEFORE DELETE ON research_controls "
               "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    op.execute("CREATE TRIGGER research_control_marks_guard BEFORE INSERT ON research_control_marks "
               "FOR EACH ROW EXECUTE FUNCTION asl_m7_control_guard()")
    op.execute("CREATE TRIGGER research_control_marks_content BEFORE INSERT ON research_control_marks "
               "FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard()")
    op.execute("CREATE TRIGGER research_control_marks_immutable BEFORE UPDATE OR DELETE ON research_control_marks "
               "FOR EACH ROW EXECUTE FUNCTION asl_immutable()")
    op.execute("CREATE TRIGGER research_jobs_control BEFORE INSERT OR UPDATE ON research_jobs "
               "FOR EACH ROW EXECUTE FUNCTION asl_m7_control_guard()")
    op.execute("CREATE TRIGGER research_results_control BEFORE INSERT ON research_results "
               "FOR EACH ROW EXECUTE FUNCTION asl_m7_control_guard()")
    op.execute(GRANTS)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    bind = op.get_bind()
    for table in AGENT_WRITTEN:
        if bind.exec_driver_sql(f"SELECT count(*) FROM {table} WHERE NOT fixture").scalar_one():
            raise RuntimeError("non-fixture M7 records exist; downgrade refused; fix forward")
    for table in EXECUTION_WRITTEN:
        if bind.exec_driver_sql(f"SELECT count(*) FROM {table}").scalar_one():
            raise RuntimeError("M7 engine records exist; downgrade refused; fix forward")
    added = {key: _quoted(values) for key, values in M7_ADDED.items()}
    history = bind.exec_driver_sql(f"""
        SELECT (SELECT count(*) FROM agent_workflows WHERE purpose IN {added[("agent_workflows", "purpose")]}
                   OR created_by IN {added[("agent_workflows", "created_by")]}
                   OR template_id IN {_quoted(tuple(GENERATION_3_TEMPLATES))})
             + (SELECT count(*) FROM agent_artifacts WHERE kind IN {added[("agent_artifacts", "kind")]})
             + (SELECT count(*) FROM agent_triggers WHERE family IN {added[("agent_triggers", "family")]})
             + (SELECT count(*) FROM agent_probe_runs WHERE suite <> 'CAPABILITY')
             + (SELECT count(*) FROM agent_runtime_requests WHERE kind = 'DECISION_PROBE')
             + (SELECT count(*) FROM research_promotions WHERE state NOT IN {_quoted(M6_PROMOTION_STATES)})
             + (SELECT count(*) FROM research_candidate_events WHERE state = 'MAIN_APPROVED')
             + (SELECT count(*) FROM agent_approvals WHERE target_kind = 'PROMOTION' AND action <> 'REJECT')
    """).scalar_one()
    if history:
        raise RuntimeError("M7 agent history exists; downgrade refused; fix forward")
    if bind.exec_driver_sql("SELECT (SELECT count(*) FROM research_controls) "
                            "+ (SELECT count(*) FROM research_jobs WHERE kind = 'CONTROL')").scalar_one():
        raise RuntimeError("control replay records exist; downgrade refused; fix forward")
    installed = bind.exec_driver_sql("""
        SELECT count(*) FROM execution_definitions WHERE (kind = 'STRATEGY'
            AND definition->>'policy_kind' = 'AGENT_DRIVEN') OR (kind = 'EVALUATION_PROTOCOL'
            AND id <> 'EVALUATION_PROTOCOL_V1')
    """).scalar_one()
    if installed:
        raise RuntimeError("an M7 definition is installed; downgrade refused; fix forward")
    op.execute("DROP INDEX agent_workflows_one_open_promotion")
    for table in CONTROL_WORK:
        op.execute(f"DROP TRIGGER {table}_control ON {table}")
    op.execute("DROP VIEW " + ", ".join(RESEARCH_VIEWS))
    op.execute("DROP TABLE " + ", ".join(reversed(CONTROL_TABLES)))
    _control_work(False)
    for table in OWNER_SHAPED:
        op.execute(f"DROP TRIGGER {table}_owner_shape ON {table}")
    op.execute("DROP VIEW " + ", ".join(reversed(EVALUATION_VIEWS)))
    op.execute("DROP SCHEMA evaluation_read")
    op.execute("DROP VIEW " + ", ".join(reversed(VIEWS)))
    op.execute(f"DROP FUNCTION {INSTALL}, {HOLD}")
    op.execute("DROP TABLE " + ", ".join(reversed(TABLES)))
    _promotion_guards(False)
    op.execute("DROP FUNCTION " + ", ".join(FUNCTIONS + tuple(item[4] + "()" for item in REPLACED)))
    # The seed store is immutable even for the migration role. Relax only this trigger, inside this
    # transaction, and delete only the frozen, verified generation-3 identities, as 0008's downgrade does.
    op.execute("ALTER TABLE agent_definitions DISABLE TRIGGER agent_definitions_immutable")
    for row in agent_seed_rows():
        if bind.exec_driver_sql("DELETE FROM agent_definitions WHERE id=%(id)s AND sha256=%(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("M7 seed mismatch; downgrade refused")
    op.execute("ALTER TABLE agent_definitions ENABLE TRIGGER agent_definitions_immutable")
    op.execute("ALTER TABLE agent_probe_runs DROP CONSTRAINT agent_probe_runs_suite_policy, DROP COLUMN policy_sha256, "
               "DROP COLUMN policy_id, DROP COLUMN suite")
    _workflow_guard(False)
    _checks(False)


# The decision suite is a probe run of its own (section 5.6); a capability run binds no policy. Column grants
# from 0007 leave the new columns insert-only for the agent worker.
PROBE_SUITE = """
ALTER TABLE agent_probe_runs ADD COLUMN suite varchar(12) NOT NULL DEFAULT 'CAPABILITY'
        CHECK (suite IN ('CAPABILITY','DECISION')),
    ADD COLUMN policy_id varchar(64), ADD COLUMN policy_sha256 varchar(64) CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    ADD CONSTRAINT agent_probe_runs_suite_policy
        CHECK (num_nulls(policy_id, policy_sha256) = CASE WHEN suite = 'DECISION' THEN 0 ELSE 2 END);
"""
GENERATION_3_TEMPLATES = ("MARKET_BRIEF_V1", "BRIEF_REVIEW_V1", "PORTFOLIO_DECISION_V1", "INTENT_REVIEW_V1",
                          "OUTCOME_REVIEW_V1", "PROMOTION_V2")

DDL = """
CREATE TABLE decision_snapshots (
    id uuid PRIMARY KEY, workflow_id uuid NOT NULL UNIQUE REFERENCES agent_workflows(id),
    run_id uuid, policy_id varchar(64), policy_sha256 varchar(64) CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    state_key varchar(64) NOT NULL CHECK (state_key ~ '^[0-9a-f]{64}$'),
    canonical text NOT NULL CHECK (octet_length(canonical) <= 8192), document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK (num_nulls(run_id, policy_id, policy_sha256) IN (0, 3))
);
CREATE TABLE decision_intents (
    id uuid PRIMARY KEY, workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
    tool_call_id uuid NOT NULL UNIQUE REFERENCES agent_tool_calls(id),
    snapshot_id uuid NOT NULL REFERENCES decision_snapshots(id), snapshot_sha256 varchar(64) NOT NULL,
    run_id uuid NOT NULL, policy_id varchar(64) NOT NULL, policy_sha256 varchar(64) NOT NULL,
    action varchar(16) NOT NULL CHECK (action IN ('ENTER','EXIT','CANCEL_ENTRY','TIGHTEN_STOP')),
    symbol varchar(12) NOT NULL CHECK (symbol IN ('BTCUSDT','SOLUSDT')), position_id uuid,
    entry_basis varchar(12) CHECK (entry_basis IN ('ASSESSMENT','CANDIDATE')),
    candidate_id uuid REFERENCES research_candidates(id),
    decision_bar_open_ms bigint NOT NULL CHECK (decision_bar_open_ms >= 0 AND decision_bar_open_ms % 3600000 = 0),
    expires_at timestamptz NOT NULL, permission_epoch bigint NOT NULL,
    operation_key varchar(160) NOT NULL UNIQUE,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 16384), document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK ((action = 'ENTER') = (entry_basis IS NOT NULL)),
    CHECK ((candidate_id IS NOT NULL) = (entry_basis IS NOT DISTINCT FROM 'CANDIDATE')),
    CHECK ((position_id IS NOT NULL) = (action IN ('EXIT','TIGHTEN_STOP'))),
    CHECK (expires_at > created_at AND expires_at <= created_at + interval '1 hour')
);
CREATE INDEX decision_intents_workflow ON decision_intents(workflow_id);
CREATE INDEX decision_intents_run ON decision_intents(run_id, created_at);
CREATE TABLE decision_submissions (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    intent_id uuid NOT NULL UNIQUE REFERENCES decision_intents(id), intent_sha256 varchar(64) NOT NULL,
    workflow_id uuid NOT NULL REFERENCES agent_workflows(id),
    tool_call_id uuid NOT NULL UNIQUE REFERENCES agent_tool_calls(id), run_id uuid NOT NULL,
    review_id uuid REFERENCES agent_artifacts(id), review_sha256 varchar(64),
    assessment_id uuid REFERENCES agent_artifacts(id), assessment_sha256 varchar(64),
    candidate_id uuid REFERENCES research_candidates(id), candidate_sha256 varchar(64), candidate_declaration jsonb,
    candidate_approval_id uuid REFERENCES agent_approvals(id),
    permission_epoch bigint NOT NULL, profile_sha256 varchar(64) NOT NULL CHECK (profile_sha256 ~ '^[0-9a-f]{64}$'),
    state_key varchar(64) NOT NULL CHECK (state_key ~ '^[0-9a-f]{64}$'),
    cutoff_watermark bigint NOT NULL CHECK (cutoff_watermark >= 0),
    context_key varchar(64) NOT NULL CHECK (context_key ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK ((review_id IS NULL) = (review_sha256 IS NULL)),
    CHECK ((assessment_id IS NULL) = (assessment_sha256 IS NULL)),
    CHECK (num_nulls(candidate_id, candidate_sha256, candidate_declaration) IN (0, 3)),
    CHECK (candidate_approval_id IS NULL OR candidate_id IS NOT NULL)
);
CREATE INDEX decision_submissions_run ON decision_submissions(run_id, seq);
CREATE TABLE decision_withdrawals (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    submission_id uuid NOT NULL UNIQUE REFERENCES decision_submissions(id),
    workflow_id uuid NOT NULL REFERENCES agent_workflows(id), run_id uuid NOT NULL,
    reason varchar(12) NOT NULL CHECK (reason IN ('CANCELED','EXPIRED','FAILED','UNAPPROVED')),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE INDEX decision_withdrawals_run ON decision_withdrawals(run_id, seq);
CREATE TABLE decision_verifications (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    probe_run_id uuid NOT NULL UNIQUE REFERENCES agent_probe_runs(id),
    profile_id uuid NOT NULL REFERENCES agent_runtime_profiles(id), profile_sha256 varchar(64) NOT NULL,
    policy_id varchar(64) NOT NULL, policy_sha256 varchar(64) NOT NULL,
    status varchar(8) NOT NULL CHECK (status IN ('VERIFIED','FAILED')), detail jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE INDEX decision_verifications_binding ON decision_verifications(profile_sha256, policy_sha256, seq);
CREATE TABLE decision_pause_requests (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    kind varchar(8) NOT NULL CHECK (kind IN ('PAUSE','RESUME')),
    actor varchar(8) NOT NULL CHECK (actor IN ('AGENT','OWNER')), run_id uuid NOT NULL,
    pause_id uuid REFERENCES decision_pause_requests(id),
    workflow_id uuid REFERENCES agent_workflows(id), tool_call_id uuid UNIQUE REFERENCES agent_tool_calls(id),
    reason varchar(32), cites jsonb, permission_epoch bigint,
    session_id uuid, idempotency_key varchar(80) UNIQUE, request_hash varchar(64), correlation_id varchar(80),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    CHECK ((kind = 'PAUSE') = (actor = 'AGENT')),
    CHECK ((kind = 'RESUME') = (pause_id IS NOT NULL)),
    CHECK (actor <> 'AGENT' OR (num_nulls(workflow_id, tool_call_id, reason, cites, permission_epoch) = 0
                                AND num_nonnulls(session_id, idempotency_key, request_hash, correlation_id) = 0)),
    CHECK (actor <> 'OWNER' OR (num_nulls(session_id, idempotency_key, request_hash, correlation_id) = 0
                                AND num_nonnulls(workflow_id, tool_call_id, reason, cites, permission_epoch) = 0))
);
CREATE UNIQUE INDEX decision_pause_resumed_once ON decision_pause_requests(pause_id) WHERE pause_id IS NOT NULL;
CREATE INDEX decision_pause_requests_run ON decision_pause_requests(run_id, seq);
CREATE TABLE decision_events (
    id uuid PRIMARY KEY, seq bigint GENERATED ALWAYS AS IDENTITY UNIQUE,
    mode varchar(24) NOT NULL CHECK (mode IN ('FORWARD_PAPER','OFFLINE_TEST','HISTORICAL_RESEARCH')),
    run_id uuid NOT NULL,
    kind varchar(16) NOT NULL CHECK (kind IN ('ACCEPTED','REJECTED','EXPIRED','CANCELED','PAUSE_OPENED','PAUSE_CLOSED')),
    submission_id uuid REFERENCES decision_submissions(id),
    pause_request_id uuid REFERENCES decision_pause_requests(id),
    order_id uuid, obligation_id uuid, evaluation_id uuid, stop_update_id uuid,
    codes jsonb NOT NULL DEFAULT '[]', detail jsonb NOT NULL DEFAULT '{}',
    lease_epoch bigint NOT NULL, permission_epoch bigint, at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK ((kind IN ('ACCEPTED','REJECTED','EXPIRED','CANCELED')) = (submission_id IS NOT NULL)),
    CHECK ((kind IN ('PAUSE_OPENED','PAUSE_CLOSED')) = (pause_request_id IS NOT NULL)),
    CHECK (jsonb_typeof(codes) = 'array' AND (kind <> 'REJECTED' OR jsonb_array_length(codes) > 0))
);
CREATE UNIQUE INDEX decision_events_one_answer ON decision_events(submission_id) WHERE submission_id IS NOT NULL;
CREATE UNIQUE INDEX decision_events_pause_once ON decision_events(pause_request_id) WHERE pause_request_id IS NOT NULL;
CREATE INDEX decision_events_run ON decision_events(run_id, seq);
CREATE TABLE decision_position_terms (
    mandate_id uuid PRIMARY KEY,
    mode varchar(24) NOT NULL CHECK (mode IN ('FORWARD_PAPER','OFFLINE_TEST','HISTORICAL_RESEARCH')),
    run_id uuid NOT NULL, symbol varchar(12) NOT NULL CHECK (symbol IN ('BTCUSDT','SOLUSDT')),
    policy_id varchar(64) NOT NULL, policy_sha256 varchar(64) NOT NULL,
    intent_id uuid NOT NULL REFERENCES decision_intents(id),
    submission_id uuid NOT NULL UNIQUE REFERENCES decision_submissions(id),
    entry_basis varchar(12) NOT NULL CHECK (entry_basis IN ('ASSESSMENT','CANDIDATE')),
    candidate_id uuid REFERENCES research_candidates(id), candidate_approval_id uuid REFERENCES agent_approvals(id),
    stop_template varchar(24) NOT NULL, stop_multiple numeric NOT NULL CHECK (stop_multiple > 0),
    max_hold_hours integer NOT NULL CHECK (max_hold_hours > 0),
    exit_allowed boolean NOT NULL, tighten_allowed boolean NOT NULL,
    tighten_templates jsonb NOT NULL CHECK (jsonb_typeof(tighten_templates) = 'array'),
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    CHECK ((candidate_id IS NOT NULL) = (entry_basis = 'CANDIDATE')),
    CHECK (candidate_approval_id IS NULL OR candidate_id IS NOT NULL)
);
CREATE INDEX decision_position_terms_run ON decision_position_terms(run_id);
CREATE TABLE decision_stop_updates (
    id uuid PRIMARY KEY,
    mode varchar(24) NOT NULL CHECK (mode IN ('FORWARD_PAPER','OFFLINE_TEST','HISTORICAL_RESEARCH')),
    run_id uuid NOT NULL, position_id uuid NOT NULL REFERENCES decision_position_terms(mandate_id),
    version integer NOT NULL CHECK (version >= 1),
    stop_price numeric NOT NULL CHECK (stop_price > 0), previous_stop numeric NOT NULL CHECK (previous_stop > 0),
    template varchar(24) NOT NULL,
    intent_id uuid NOT NULL REFERENCES decision_intents(id),
    submission_id uuid NOT NULL UNIQUE REFERENCES decision_submissions(id),
    quote_observation_id uuid NOT NULL, quote_bid numeric(38,8) NOT NULL CHECK (quote_bid > 0),
    quote_source_at timestamptz NOT NULL, at timestamptz NOT NULL,
    recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    UNIQUE (position_id, version),
    CHECK (stop_price > previous_stop AND stop_price < quote_bid)
);
CREATE TABLE decision_outcomes (
    id uuid PRIMARY KEY, position_id uuid NOT NULL UNIQUE, run_id uuid NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 65536), document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false
);
CREATE INDEX decision_outcomes_run ON decision_outcomes(run_id, created_at);
"""

# The policy's own run, for asl_agent (section 5.8). The migration identity owns these views, so asl_agent
# needs no grant on any M3/M4 table; they take only the share lock every read takes. A run is the policy's
# when its manifest names an AGENT_DRIVEN strategy definition by id and hash; the pilot's run names the
# FIXED reference and is never in them. Account-wide values (cash, holdings, latches, daily references)
# are shown only while such a run is live. Owner sessions, keys and request hashes are never selected.
VIEW_SQL = """
CREATE VIEW agent_read.policy_runs WITH (security_barrier = true) AS
    SELECT x.id AS run_id, x.mode, x.state, x.state IN ('RUNNING','PAUSED','STOPPING') AS live,
           d.id AS policy_id, d.sha256 AS policy_sha256, x.manifest_id, m.sha256 AS manifest_sha256,
           x.created_at, x.updated_at
    FROM experiments x
    JOIN experiment_manifests m ON m.id = x.manifest_id
    JOIN execution_definitions d ON d.id = m.manifest #>> '{definitions,strategy,id}'
        AND d.sha256 = m.manifest #>> '{definitions,strategy,sha256}'
    WHERE d.kind = 'STRATEGY' AND d.definition->>'policy_kind' = 'AGENT_DRIVEN';
CREATE VIEW agent_read.policy_definitions WITH (security_barrier = true) AS
    SELECT d.id, d.kind, d.version, d.status, d.definition, d.sha256, d.created_at
    FROM execution_definitions d
    WHERE (d.kind = 'STRATEGY' AND d.definition->>'policy_kind' = 'AGENT_DRIVEN')
       OR EXISTS (SELECT 1 FROM agent_read.policy_runs r JOIN experiment_manifests m ON m.id = r.manifest_id
                  CROSS JOIN LATERAL jsonb_each(m.manifest->'definitions') AS slot(name, value)
                  WHERE jsonb_typeof(slot.value) = 'object' AND slot.value->>'id' = d.id
                    AND slot.value->>'sha256' = d.sha256);
CREATE VIEW agent_read.policy_approvals WITH (security_barrier = true) AS
    SELECT a.seq, a.target_kind, a.target_id, a.target_sha256, a.action, a.created_at
    FROM owner_approvals a
    WHERE (a.target_kind = 'DEFINITION' AND EXISTS (SELECT 1 FROM execution_definitions d WHERE d.id = a.target_id
              AND d.kind = 'STRATEGY' AND d.definition->>'policy_kind' = 'AGENT_DRIVEN'))
       OR (a.target_kind = 'EXPERIMENT_MANIFEST'
           AND a.target_id IN (SELECT manifest_id::text FROM agent_read.policy_runs));
CREATE VIEW agent_read.policy_run_events WITH (security_barrier = true) AS
    SELECT e.id, e.experiment_id AS run_id, e.actor, e.kind, e.cause, e.at
    FROM experiment_events e WHERE e.experiment_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_positions WITH (security_barrier = true) AS
    SELECT p.id AS position_id, md.run_id, p.mode, p.symbol, p.state, p.quantity, p.cost_basis,
           p.bought_quantity, p.sold_quantity, p.quote_spent, p.quote_received, p.fees_base, p.fees_quote,
           p.realized_pnl, p.dust_quantity, p.first_fill_at, p.time_exit_at, p.closed_at, p.version, p.created_at,
           md.strategy_id, md.strategy_sha256, md.evaluation_id, md.entry_reason, md.entry_reference,
           md.stop_price, md.atr, md.stop_policy, md.max_hold_seconds, md.trend_exit_rule, md.envelope_price,
           md.unit_risk, md.risk_policy_id, md.cost_scenario_id
    FROM positions p JOIN position_mandates md ON md.id = p.id
    WHERE md.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_position_events WITH (security_barrier = true) AS
    SELECT e.id, e.position_id, md.run_id, e.event, e.at, e.detail
    FROM position_events e JOIN position_mandates md ON md.id = e.position_id
    WHERE md.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_orders WITH (security_barrier = true) AS
    SELECT o.id, o.seq, o.run_id, o.mode, o.origin, o.attempt, o.side, o.symbol, o.position_id, o.evaluation_id,
           o.obligation_id, o.risk_decision_id, o.strategy_id, o.requested_qty, o.envelope_price, o.stop_price,
           o.decision_quote, o.decision_watermark, o.decided_at, o.arrival_at, o.fill_deadline, o.status,
           o.status_reason, o.filled_qty, o.reserved_asset, o.reserved_amount, o.terminal_at
    FROM orders o WHERE o.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_order_events WITH (security_barrier = true) AS
    SELECT e.id, e.order_id, o.run_id, e.from_status, e.to_status, e.reason, e.at
    FROM order_events e JOIN orders o ON o.id = e.order_id
    WHERE o.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_fills WITH (security_barrier = true) AS
    SELECT f.id, f.seq, f.order_id, o.run_id, f.mode, f.symbol, f.side, f.quantity, f.price, f.gross, f.fee,
           f.fee_asset, f.quote_sequence, f.displayed_qty, f.depleted_qty, f.participation, f.cost_scenario_id,
           f.execution_rule, f.execution_fidelity, f.modeled_at, f.available_at
    FROM fills f JOIN orders o ON o.id = f.order_id
    WHERE o.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_exit_obligations WITH (security_barrier = true) AS
    SELECT b.id, b.position_id, md.run_id, b.mode, b.reason, b.triggered_at, b.trigger_evidence, b.state,
           b.attempts, b.suppressed, b.completed_at
    FROM exit_obligations b JOIN position_mandates md ON md.id = b.position_id
    WHERE md.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_evaluations WITH (security_barrier = true) AS
    SELECT e.id, e.run_id, e.mode, e.strategy_id, e.symbol, e.bar_open_ms, e.bar_available_at, e.watermark,
           e.decided_at, e.result, e.features, s.outcome, s.reason AS outcome_reason,
           s.decided_at AS outcome_decided_at
    FROM strategy_evaluations e LEFT JOIN signal_outcomes s ON s.evaluation_id = e.id
    WHERE e.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_risk_decisions WITH (security_barrier = true) AS
    SELECT r.id, r.run_id, r.mode, r.evaluation_id, r.attempt, r.decided_at, r.result, r.primary_reason,
           r.reasons, r.inputs
    FROM risk_decisions r WHERE r.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.policy_valuations WITH (security_barrier = true) AS
    SELECT v.id, v.run_id, v.mode, v.valued_at, v.purpose, v.cash, v.holdings, v.equity, v.nav, v.quality,
           v.reason
    FROM valuations v WHERE v.run_id IN (SELECT run_id FROM agent_read.policy_runs WHERE live);
CREATE VIEW agent_read.policy_account WITH (security_barrier = true) AS
    SELECT r.run_id, a.version AS account_version, a.cash, a.reserved, a.nav, a.high_water_nav,
           a.valuation_valid, a.paused, a.reconciliation_failed
    FROM account_state a CROSS JOIN agent_read.policy_runs r WHERE a.id = 1 AND r.live;
CREATE VIEW agent_read.policy_holdings WITH (security_barrier = true) AS
    SELECT r.run_id, h.asset, h.quantity, h.reserved
    FROM account_holdings h CROSS JOIN agent_read.policy_runs r WHERE r.live;
CREATE VIEW agent_read.policy_daily_references WITH (security_barrier = true) AS
    SELECT r.run_id, d.mode, d.utc_date, d.nav, d.quality
    FROM daily_references d JOIN agent_read.policy_runs r ON r.mode = d.mode WHERE r.live;
CREATE VIEW agent_read.policy_latches WITH (security_barrier = true) AS
    SELECT r.run_id, l.id, l.mode, l.cause, l.latched_at,
           EXISTS (SELECT 1 FROM risk_latch_resolutions z WHERE z.latch_id = l.id) AS resolved
    FROM risk_latches l JOIN agent_read.policy_runs r ON r.mode = l.mode WHERE r.live;
CREATE VIEW agent_read.engine_decision_events WITH (security_barrier = true) AS
    SELECT e.* FROM decision_events e WHERE e.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.engine_position_terms WITH (security_barrier = true) AS
    SELECT t.* FROM decision_position_terms t WHERE t.run_id IN (SELECT run_id FROM agent_read.policy_runs);
CREATE VIEW agent_read.engine_stop_updates WITH (security_barrier = true) AS
    SELECT u.* FROM decision_stop_updates u WHERE u.run_id IN (SELECT run_id FROM agent_read.policy_runs);
"""

# A run's decision records for asl_evaluation (section 5.11), owned by the migration identity like the
# agent_read views: codes, states, counts and times only, never an intent's, a review's or a decision's text.
# A tool call's name is the model's request; a name outside the catalog (UNKNOWN_TOOL) is shown as none.
# A run's workflows are its decisions (named by their trigger or their snapshot), their children and the
# reviews of its positions' outcomes; probes and briefs are no run's. Rows are filtered by run and as-of time
# in ``app.evaluation.measures``; a workflow's state counts only once its finish time is within the report.
EVALUATION_VIEW_SQL = """
CREATE SCHEMA evaluation_read;
CREATE VIEW evaluation_read.decision_intents WITH (security_barrier = true) AS
    SELECT i.id, i.run_id, i.workflow_id, i.action, i.symbol, i.entry_basis, i.created_at FROM decision_intents i;
CREATE VIEW evaluation_read.decision_submissions WITH (security_barrier = true) AS
    SELECT s.id, s.seq, s.intent_id, s.workflow_id, s.run_id, s.review_id IS NOT NULL AS reviewed,
           s.assessment_id IS NOT NULL AS assessed, s.candidate_id IS NOT NULL AS on_candidate, s.context_key,
           s.created_at
    FROM decision_submissions s;
CREATE VIEW evaluation_read.decision_events WITH (security_barrier = true) AS
    SELECT e.seq, e.run_id, e.kind, e.submission_id, e.pause_request_id, e.order_id, e.codes, e.at
    FROM decision_events e;
CREATE VIEW evaluation_read.decision_withdrawals WITH (security_barrier = true) AS
    SELECT w.submission_id, w.run_id, w.reason, w.created_at FROM decision_withdrawals w;
CREATE VIEW evaluation_read.decision_pause_requests WITH (security_barrier = true) AS
    SELECT p.id, p.seq, p.kind, p.actor, p.run_id, p.pause_id, p.reason, p.created_at FROM decision_pause_requests p;
CREATE VIEW evaluation_read.decision_workflows WITH (security_barrier = true) AS
    WITH decisions AS (
        SELECT w.id, COALESCE(s.run_id, CASE WHEN t.detail->>'run_id'
                   ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
                   THEN (t.detail->>'run_id')::uuid END) AS run_id,
               t.family AS trigger_family, t.detail->>'event_at' AS trigger_event_at
        FROM agent_workflows w
        LEFT JOIN agent_triggers t ON t.id::text = w.params #>> '{trigger,id}'
        LEFT JOIN decision_snapshots s ON s.workflow_id = w.id
        WHERE w.purpose = 'DECISION' AND w.created_by <> 'PROBE_RUN'
    ), linked AS (
        SELECT d.id AS workflow_id, d.id AS decision_id, d.run_id, d.trigger_family, d.trigger_event_at
        FROM decisions d
        UNION ALL
        SELECT c.id, d.id, d.run_id, NULL, NULL FROM agent_workflows c JOIN decisions d ON d.id = c.parent_id
        UNION ALL
        SELECT w.id, NULL, o.run_id, NULL, NULL FROM agent_workflows w
            JOIN decision_outcomes o ON o.id::text = w.params #>> '{outcome,outcome_id}'
        WHERE w.purpose = 'OUTCOME_REVIEW' AND w.created_by <> 'PROBE_RUN'
    )
    SELECT l.workflow_id, l.decision_id, l.run_id, w.parent_id, w.template_id, w.purpose, w.state,
           w.terminal_reason, w.created_at, w.started_at, w.finished_at, l.trigger_family, l.trigger_event_at
    FROM linked l JOIN agent_workflows w ON w.id = l.workflow_id WHERE l.run_id IS NOT NULL;
CREATE VIEW evaluation_read.decision_steps WITH (security_barrier = true) AS
    SELECT s.workflow_id, l.decision_id, l.run_id, s.step_no, s.attempt, s.outcome, s.error_code, s.created_at,
           s.completed_at
    FROM agent_steps s JOIN evaluation_read.decision_workflows l ON l.workflow_id = s.workflow_id;
CREATE VIEW evaluation_read.decision_tool_calls WITH (security_barrier = true) AS
    SELECT c.workflow_id, l.decision_id, l.run_id,
           CASE WHEN c.decision_code = 'UNKNOWN_TOOL' THEN NULL ELSE c.tool_name END AS tool_name, c.decision,
           c.decision_code, c.created_at
    FROM agent_tool_calls c JOIN evaluation_read.decision_workflows l ON l.workflow_id = c.workflow_id;
CREATE VIEW evaluation_read.decision_reviews WITH (security_barrier = true) AS
    SELECT x.workflow_id, l.decision_id, l.run_id, x.document->>'review_type' AS review_type,
           x.document->>'verdict' AS verdict,
           CASE WHEN jsonb_typeof(x.document->'unsupported_claims') = 'array'
                THEN jsonb_array_length(x.document->'unsupported_claims') END AS unsupported_claims, x.created_at
    FROM agent_artifacts x JOIN evaluation_read.decision_workflows l ON l.workflow_id = x.workflow_id
    WHERE x.kind = 'EVALUATION_REVIEW';
CREATE VIEW evaluation_read.decision_documents WITH (security_barrier = true) AS
    SELECT x.workflow_id, l.run_id, e.item->>'symbol' AS symbol, e.item->>'action' AS action,
           e.item->>'reason_code' AS reason_code, x.created_at
    FROM agent_artifacts x JOIN evaluation_read.decision_workflows l ON l.workflow_id = x.workflow_id
    CROSS JOIN LATERAL jsonb_array_elements(CASE WHEN jsonb_typeof(x.document->'symbols') = 'array'
                                                 THEN x.document->'symbols' ELSE '[]'::jsonb END) AS e(item)
    WHERE x.kind = 'PORTFOLIO_DECISION';
CREATE VIEW evaluation_read.runtime_events WITH (security_barrier = true) AS
    SELECT r.id, r.kind, r.actor, r.at FROM agent_runtime_events r
    WHERE r.kind IN ('AUTH_REQUIRED','QUOTA_BLOCKED','EPOCH_INCREMENTED');
"""

# Each guard checks one table's insert. An identity check exempts only the migration identity, which owns
# disposable fixtures; every binding and content check applies to it too. Reads take no row lock. Every
# function has a fixed search path, so a temporary table of the writer's session cannot stand in for a
# table a guard reads. An agent row is recorded at the database's clock, whatever the writer sent, and an
# intent's validity is measured from it. A cited assessment is an M5/M6 artifact whose creation time its
# writer could choose: one dated in the future is refused, and its age counts from the time it states.
GUARDS = """
CREATE FUNCTION asl_m7_content_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    IF NEW.canonical::jsonb <> NEW.document
            OR encode(digest(convert_to(NEW.canonical,'UTF8'),'sha256'),'hex') <> NEW.sha256 THEN
        RAISE EXCEPTION 'M7 canonical document/hash mismatch'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_owner_shape_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    -- One branch per table: a field of another table's row is never named.
    IF TG_TABLE_NAME = 'research_jobs' THEN
        IF NEW.owner_cancel_request IS NOT NULL THEN
            RAISE EXCEPTION 'a new research job carries no owner cancel request'; END IF;
    ELSIF TG_TABLE_NAME = 'research_shadows' THEN
        IF NEW.owner_stop_request IS NOT NULL THEN
            RAISE EXCEPTION 'a new shadow carries no owner stop request'; END IF;
    ELSIF NEW.actor <> 'OWNER' AND num_nonnulls(NEW.idempotency_key, NEW.session_id, NEW.request_hash) > 0 THEN
        RAISE EXCEPTION 'only an owner request carries an owner key, session or request hash';
    END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_snapshot_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE w record;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'decision snapshots are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT role, purpose INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.role <> 'COORDINATOR' OR w.purpose NOT IN ('DECISION','PROBE') THEN
        RAISE EXCEPTION 'a snapshot belongs to a coordinator decision workflow'; END IF;
    IF NEW.run_id IS NULL THEN
        IF w.purpose <> 'PROBE' THEN RAISE EXCEPTION 'only a probe decides without a policy run'; END IF;
    ELSIF NOT EXISTS (SELECT 1 FROM agent_read.policy_runs WHERE run_id = NEW.run_id
                      AND policy_id = NEW.policy_id AND policy_sha256 = NEW.policy_sha256) THEN
        RAISE EXCEPTION 'snapshot run is not a run of this operating policy'; END IF;
    IF NEW.document->>'workflow_id' IS DISTINCT FROM NEW.workflow_id::text
            OR NEW.document->>'run_id' IS DISTINCT FROM NEW.run_id::text
            OR NEW.document->>'policy_id' IS DISTINCT FROM NEW.policy_id
            OR NEW.document->>'policy_sha256' IS DISTINCT FROM NEW.policy_sha256
            OR NEW.document->>'state_key' IS DISTINCT FROM NEW.state_key THEN
        RAISE EXCEPTION 'a snapshot''s columns must equal its hashed document'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_intent_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE w record; c record; s record; d jsonb := NEW.document;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'trade intents are drafted by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT role, purpose, state INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF NOT FOUND OR w.role <> 'COORDINATOR' OR w.purpose NOT IN ('DECISION','PROBE') THEN
        RAISE EXCEPTION 'a draft belongs to a coordinator decision workflow'; END IF;
    IF w.state NOT IN ('RUNNING','WAITING_TOOL','WAITING_REVIEW') THEN
        RAISE EXCEPTION 'a draft comes from a workflow that is still running'; END IF;
    SELECT workflow_id, tool_name, decision, permission_epoch INTO c FROM agent_tool_calls WHERE id = NEW.tool_call_id;
    IF NOT FOUND OR c.workflow_id <> NEW.workflow_id OR c.tool_name <> 'draft_trade_intent'
            OR c.decision <> 'AUTHORIZED' OR c.permission_epoch <> NEW.permission_epoch THEN
        RAISE EXCEPTION 'a draft binds its own authorized draft_trade_intent call'; END IF;
    SELECT workflow_id, sha256, run_id, policy_id, policy_sha256 INTO s FROM decision_snapshots
        WHERE id = NEW.snapshot_id;
    IF NOT FOUND OR s.workflow_id <> NEW.workflow_id OR s.sha256 <> NEW.snapshot_sha256
            OR s.run_id IS DISTINCT FROM NEW.run_id OR s.policy_id IS DISTINCT FROM NEW.policy_id
            OR s.policy_sha256 IS DISTINCT FROM NEW.policy_sha256 THEN
        RAISE EXCEPTION 'a draft binds the snapshot of its own workflow and policy run'; END IF;
    -- What the engine and the guards read from columns is exactly what the review's hash covers.
    IF d->>'workflow_id' IS DISTINCT FROM NEW.workflow_id::text OR d->>'run_id' IS DISTINCT FROM NEW.run_id::text
            OR d->>'policy_id' IS DISTINCT FROM NEW.policy_id OR d->>'policy_sha256' IS DISTINCT FROM NEW.policy_sha256
            OR d->>'snapshot_sha256' IS DISTINCT FROM NEW.snapshot_sha256 OR d->>'action' IS DISTINCT FROM NEW.action
            OR d->>'symbol' IS DISTINCT FROM NEW.symbol OR d->>'position_id' IS DISTINCT FROM NEW.position_id::text
            OR d->>'entry_basis' IS DISTINCT FROM NEW.entry_basis
            OR d->>'candidate_id' IS DISTINCT FROM NEW.candidate_id::text
            OR d->>'decision_bar_open_ms' IS DISTINCT FROM NEW.decision_bar_open_ms::text
            OR (d->>'expires_at')::timestamptz IS DISTINCT FROM NEW.expires_at THEN
        RAISE EXCEPTION 'a draft''s columns must equal its hashed document'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_submission_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE i record; w record; c record; r record; a record; e record; pr record; latest text; max_age numeric;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'submissions are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT * INTO i FROM decision_intents WHERE id = NEW.intent_id;
    IF NOT FOUND OR i.sha256 <> NEW.intent_sha256 OR i.workflow_id <> NEW.workflow_id OR i.run_id <> NEW.run_id THEN
        RAISE EXCEPTION 'a submission carries its own draft''s hash, workflow and run'; END IF;
    IF i.expires_at <= clock_timestamp() THEN RAISE EXCEPTION 'the draft has expired'; END IF;
    SELECT purpose, state, permission_epoch, profile_sha256 INTO w FROM agent_workflows WHERE id = NEW.workflow_id;
    IF w.purpose <> 'DECISION' THEN RAISE EXCEPTION 'only a decision workflow submits; a probe never does'; END IF;
    IF w.state NOT IN ('RUNNING','WAITING_TOOL','WAITING_REVIEW') THEN
        RAISE EXCEPTION 'a submission comes from a workflow that is still running'; END IF;
    IF w.permission_epoch IS DISTINCT FROM NEW.permission_epoch OR w.profile_sha256 IS DISTINCT FROM NEW.profile_sha256 THEN
        RAISE EXCEPTION 'a submission carries its workflow''s epoch and profile'; END IF;
    SELECT workflow_id, tool_name, decision, permission_epoch INTO c FROM agent_tool_calls WHERE id = NEW.tool_call_id;
    IF NOT FOUND OR c.workflow_id <> NEW.workflow_id OR c.tool_name <> 'submit_trade_intent'
            OR c.decision <> 'AUTHORIZED' OR c.permission_epoch <> NEW.permission_epoch THEN
        RAISE EXCEPTION 'a submission binds its own authorized submit_trade_intent call'; END IF;
    IF NOT EXISTS (SELECT 1 FROM decision_snapshots WHERE id = i.snapshot_id AND state_key = NEW.state_key) THEN
        RAISE EXCEPTION 'a submission carries its snapshot''s state key'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_read.policy_runs WHERE run_id = i.run_id AND policy_id = i.policy_id
                   AND policy_sha256 = i.policy_sha256 AND state = 'RUNNING') THEN
        RAISE EXCEPTION 'the policy''s run is not RUNNING'; END IF;
    SELECT action INTO latest FROM agent_read.policy_approvals WHERE target_kind = 'DEFINITION'
        AND target_id = i.policy_id AND target_sha256 = i.policy_sha256 ORDER BY seq DESC LIMIT 1;
    IF latest IS DISTINCT FROM 'APPROVE' THEN RAISE EXCEPTION 'the operating policy is not approved'; END IF;
    IF i.action = 'ENTER' OR NEW.review_id IS NOT NULL THEN
        SELECT x.sha256, x.document, rw.parent_id, rw.purpose INTO r FROM agent_artifacts x
            JOIN agent_workflows rw ON rw.id = x.workflow_id WHERE x.id = NEW.review_id AND x.kind = 'EVALUATION_REVIEW';
        IF NOT FOUND OR r.sha256 <> NEW.review_sha256 OR r.parent_id IS DISTINCT FROM i.workflow_id
                OR r.purpose <> 'INTENT_REVIEW' OR r.document->>'review_type' IS DISTINCT FROM 'INTENT_REVIEW'
                OR r.document->>'target_artifact_id' IS DISTINCT FROM i.id::text
                OR r.document->>'target_sha256' IS DISTINCT FROM i.sha256
                OR r.document->>'verdict' IS DISTINCT FROM 'ACCEPTABLE' THEN
            RAISE EXCEPTION 'an entry needs an ACCEPTABLE intent review of this exact draft'; END IF;
    END IF;
    IF i.action <> 'ENTER' THEN
        IF num_nonnulls(NEW.assessment_id, NEW.candidate_id) > 0 THEN
            RAISE EXCEPTION 'only an entry carries an entry basis'; END IF;
    ELSIF i.entry_basis = 'ASSESSMENT' THEN
        IF NEW.assessment_id IS NULL OR NEW.candidate_id IS NOT NULL THEN
            RAISE EXCEPTION 'an entry on an assessment cites one assessment'; END IF;
        SELECT x.sha256, x.document, x.created_at, x.workflow_id INTO a FROM agent_artifacts x
            JOIN agent_workflows aw ON aw.id = x.workflow_id
            WHERE x.id = NEW.assessment_id AND x.kind = 'MARKET_ASSESSMENT' AND aw.role = 'ANALYST'
            AND aw.purpose IN ('ASSESSMENT','INVESTIGATION','BRIEF');
        IF NOT FOUND OR a.sha256 <> NEW.assessment_sha256 OR NOT COALESCE(a.document->'symbols' ? i.symbol, false) THEN
            RAISE EXCEPTION 'the cited assessment does not cover this symbol'; END IF;
        IF a.created_at > clock_timestamp() THEN
            RAISE EXCEPTION 'the cited assessment is dated in the future'; END IF;
        IF a.document->>'expiry_hours' IS NULL
                OR a.created_at + make_interval(hours => (a.document->>'expiry_hours')::integer) <= clock_timestamp() THEN
            RAISE EXCEPTION 'the cited assessment is past its own expiry'; END IF;
        SELECT (definition #>> '{entry_evidence,assessment_max_age_hours}')::numeric INTO max_age
            FROM agent_read.policy_definitions WHERE id = i.policy_id AND sha256 = i.policy_sha256;
        IF max_age IS NULL OR a.created_at <= clock_timestamp() - max_age * interval '1 hour' THEN
            RAISE EXCEPTION 'the cited assessment is older than the policy allows'; END IF;
        -- The review is the assessment workflow's own review child, as M5 and M6 run it.
        IF NOT EXISTS (SELECT 1 FROM agent_artifacts v JOIN agent_workflows vw ON vw.id = v.workflow_id
                       WHERE v.kind = 'EVALUATION_REVIEW' AND vw.parent_id = a.workflow_id AND vw.purpose = 'REVIEW'
                       AND vw.role = 'EVALUATOR' AND v.target_artifact_id = NEW.assessment_id
                       AND v.document->>'review_type' = 'ASSESSMENT_REVIEW'
                       AND v.document->>'target_sha256' = a.sha256 AND v.document->>'verdict' = 'ACCEPTABLE') THEN
            RAISE EXCEPTION 'the cited assessment has no ACCEPTABLE review'; END IF;
    ELSE
        IF NEW.candidate_id IS DISTINCT FROM i.candidate_id OR NEW.assessment_id IS NOT NULL
                OR NEW.candidate_approval_id IS NULL THEN
            RAISE EXCEPTION 'an entry on a candidate names the draft''s candidate and its approval only'; END IF;
        -- B6 (section 5.10): the candidate is MAIN_APPROVED on the owner's approval this submission names, that
        -- approval is still the latest owner record of its promotion, and the promotion is for this policy.
        SELECT state, gate_evidence INTO e FROM research_candidate_events WHERE candidate_id = NEW.candidate_id
            ORDER BY seq DESC LIMIT 1;
        IF e.state IS DISTINCT FROM 'MAIN_APPROVED'
                OR e.gate_evidence->>'approval_id' IS DISTINCT FROM NEW.candidate_approval_id::text THEN
            RAISE EXCEPTION 'a candidate basis needs a current main approval of that candidate'; END IF;
        SELECT p.id, p.sha256, p.document INTO pr FROM research_promotions p
            WHERE p.id::text = e.gate_evidence->>'promotion_id' AND p.candidate_id = NEW.candidate_id
            AND p.state = 'APPROVED';
        IF NOT FOUND OR pr.document->>'policy_id' IS DISTINCT FROM i.policy_id
                OR pr.document->>'policy_sha256' IS DISTINCT FROM i.policy_sha256 THEN
            RAISE EXCEPTION 'the candidate is approved for another policy'; END IF;
        IF (SELECT x.id FROM agent_approvals x WHERE x.target_kind = 'PROMOTION' AND x.target_id = pr.id::text
                AND x.target_sha256 = pr.sha256 ORDER BY x.seq DESC LIMIT 1) IS DISTINCT FROM NEW.candidate_approval_id
                OR (SELECT x.action FROM agent_approvals x WHERE x.id = NEW.candidate_approval_id)
                    IS DISTINCT FROM 'APPROVE' THEN
            RAISE EXCEPTION 'the approval of the candidate is no longer the owner''s latest record'; END IF;
        IF NOT EXISTS (SELECT 1 FROM research_candidates WHERE id = NEW.candidate_id
                       AND normalized_sha256 = NEW.candidate_sha256 AND declaration = NEW.candidate_declaration) THEN
            RAISE EXCEPTION 'the candidate declaration is not the approved candidate'; END IF;
        IF NOT COALESCE(NEW.candidate_declaration->'symbols' ? i.symbol, false)
                OR (i.document #>> '{choices,stop_multiple}')::numeric
                    IS DISTINCT FROM (NEW.candidate_declaration #>> '{exit,stop_multiple}')::numeric
                OR (i.document #>> '{choices,max_hold_hours}')::integer
                    IS DISTINCT FROM (NEW.candidate_declaration #>> '{exit,max_hold_hours}')::integer THEN
            RAISE EXCEPTION 'an entry on a candidate takes its stop multiple and hold, for one of its symbols'; END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_withdrawal_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE s record; ended text;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'withdrawals are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT workflow_id, run_id, candidate_id, candidate_approval_id INTO s FROM decision_submissions
        WHERE id = NEW.submission_id;
    IF NOT FOUND OR s.workflow_id <> NEW.workflow_id OR s.run_id <> NEW.run_id THEN
        RAISE EXCEPTION 'a withdrawal binds its own submission'; END IF;
    IF NEW.reason = 'UNAPPROVED' THEN
        -- An entry on a candidate that left MAIN_APPROVED (a research suspension raises no epoch), whatever
        -- its decision's state (ExecPlan 0026 section 5.10).
        IF s.candidate_id IS NULL OR EXISTS (
                SELECT 1 FROM (SELECT e.state, e.gate_evidence FROM research_candidate_events e
                               WHERE e.candidate_id = s.candidate_id ORDER BY e.seq DESC LIMIT 1) latest
                WHERE latest.state = 'MAIN_APPROVED'
                  AND latest.gate_evidence->>'approval_id' = s.candidate_approval_id::text) THEN
            RAISE EXCEPTION 'an entry is withdrawn as unapproved only once its candidate has left MAIN_APPROVED'; END IF;
        RETURN NEW;
    END IF;
    SELECT w.state INTO ended FROM agent_workflows w WHERE w.id = NEW.workflow_id;
    IF ended IS DISTINCT FROM NEW.reason THEN
        RAISE EXCEPTION 'a withdrawal is written as its workflow ends canceled, expired or failed'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_verification_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE p record;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'decision verifications are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT profile_id, profile_sha256, state, suite, policy_id, policy_sha256 INTO p FROM agent_probe_runs
        WHERE id = NEW.probe_run_id;
    IF NOT FOUND OR p.profile_id <> NEW.profile_id OR p.profile_sha256 <> NEW.profile_sha256
            OR p.suite <> 'DECISION' OR p.policy_id <> NEW.policy_id OR p.policy_sha256 <> NEW.policy_sha256
            OR (NEW.status = 'VERIFIED' AND p.state <> 'PASSED')
            OR (NEW.status = 'FAILED' AND p.state NOT IN ('FAILED','CANCELED')) THEN
        RAISE EXCEPTION 'a decision verification records its finished decision probe run'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_read.policy_definitions WHERE id = NEW.policy_id
                   AND sha256 = NEW.policy_sha256 AND kind = 'STRATEGY') THEN
        RAISE EXCEPTION 'a decision verification names an installed operating policy'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_pause_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
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
        IF current_user <> 'asl_api' AND NOT asl_is_superuser() THEN
            RAISE EXCEPTION 'only the owner resumes an entry pause'; END IF;
        SELECT kind, run_id INTO p FROM decision_pause_requests WHERE id = NEW.pause_id;
        IF NOT FOUND OR p.kind <> 'PAUSE' OR p.run_id <> NEW.run_id THEN
            RAISE EXCEPTION 'a resume names one pause of the same run'; END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_event_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE bound_run uuid; request_kind text;
BEGIN
    IF current_user <> 'asl_execution' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'decision events are written by the execution engine'; END IF;
    IF NEW.submission_id IS NOT NULL THEN
        SELECT s.run_id INTO bound_run FROM decision_submissions s WHERE s.id = NEW.submission_id;
        IF bound_run IS DISTINCT FROM NEW.run_id THEN
            RAISE EXCEPTION 'an answer belongs to its submission''s run'; END IF;
    ELSE
        SELECT p.run_id, p.kind INTO bound_run, request_kind FROM decision_pause_requests p
            WHERE p.id = NEW.pause_request_id;
        IF bound_run IS DISTINCT FROM NEW.run_id
                OR (NEW.kind = 'PAUSE_OPENED') IS DISTINCT FROM (request_kind = 'PAUSE') THEN
            RAISE EXCEPTION 'a pause opens on a pause request and closes on a resume of the same run'; END IF;
    END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_terms_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE m record; i record;
BEGIN
    IF current_user <> 'asl_execution' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'position terms are written by the execution engine'; END IF;
    SELECT run_id, mode, symbol, strategy_id, strategy_sha256 INTO m FROM position_mandates WHERE id = NEW.mandate_id;
    IF NOT FOUND OR m.run_id IS DISTINCT FROM NEW.run_id OR m.mode <> NEW.mode OR m.symbol <> NEW.symbol
            OR m.strategy_id <> NEW.policy_id OR m.strategy_sha256 <> NEW.policy_sha256 THEN
        RAISE EXCEPTION 'terms bind their own mandate under this operating policy'; END IF;
    SELECT x.*, s.candidate_approval_id AS approval_id INTO i FROM decision_intents x
        JOIN decision_submissions s ON s.intent_id = x.id WHERE x.id = NEW.intent_id AND s.id = NEW.submission_id;
    IF NOT FOUND OR i.action <> 'ENTER' OR i.run_id <> NEW.run_id OR i.symbol <> NEW.symbol
            OR i.policy_id <> NEW.policy_id OR i.policy_sha256 <> NEW.policy_sha256
            OR i.entry_basis <> NEW.entry_basis OR i.candidate_id IS DISTINCT FROM NEW.candidate_id
            OR i.approval_id IS DISTINCT FROM NEW.candidate_approval_id THEN
        RAISE EXCEPTION 'terms bind the submitted entry that opened the position'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_stop_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE t record; p record; i record; latest_update record; in_force numeric;
BEGIN
    IF current_user <> 'asl_execution' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'stop updates are written by the execution engine'; END IF;
    SELECT run_id, mode, tighten_allowed INTO t FROM decision_position_terms WHERE mandate_id = NEW.position_id;
    IF NOT FOUND OR NOT t.tighten_allowed OR t.run_id <> NEW.run_id OR t.mode <> NEW.mode THEN
        RAISE EXCEPTION 'the position''s terms do not allow tightening'; END IF;
    SELECT x.state, x.first_fill_at, m.stop_price INTO p FROM positions x JOIN position_mandates m ON m.id = x.id
        WHERE x.id = NEW.position_id;
    IF NOT FOUND OR p.state <> 'OPEN' OR p.first_fill_at IS NULL THEN
        RAISE EXCEPTION 'a stop is tightened only on an open, filled position'; END IF;
    SELECT x.* INTO i FROM decision_intents x JOIN decision_submissions s ON s.intent_id = x.id
        WHERE x.id = NEW.intent_id AND s.id = NEW.submission_id;
    IF NOT FOUND OR i.action <> 'TIGHTEN_STOP' OR i.position_id <> NEW.position_id THEN
        RAISE EXCEPTION 'a stop update binds its own submitted tightening'; END IF;
    SELECT version, stop_price INTO latest_update FROM decision_stop_updates WHERE position_id = NEW.position_id
        ORDER BY version DESC LIMIT 1;
    in_force := COALESCE(latest_update.stop_price, p.stop_price);
    IF NEW.version <> COALESCE(latest_update.version, 0) + 1 OR NEW.previous_stop <> in_force OR NEW.stop_price <= in_force THEN
        RAISE EXCEPTION 'a stop update is one version on and strictly above the stop in force'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_outcome_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'outcome records are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    IF NOT EXISTS (SELECT 1 FROM agent_read.policy_positions WHERE position_id = NEW.position_id
                   AND run_id = NEW.run_id AND state IN ('CLOSED','CLOSED_WITH_DUST')) THEN
        RAISE EXCEPTION 'an outcome record is written once its policy position has closed'; END IF;
    IF NEW.document->>'position_id' IS DISTINCT FROM NEW.position_id::text
            OR NEW.document->>'run_id' IS DISTINCT FROM NEW.run_id::text THEN
        RAISE EXCEPTION 'an outcome''s columns must equal its hashed document'; END IF;
    RETURN NEW;
END $$;
"""

# B6 (section 5.10). Each replaces 0008's function on one table (``REPLACED``); every rule of 0008 for that
# table is kept, and the promotion's approval, its revocation and the candidate's MAIN_APPROVED are added.
# The candidate's lock key (608) is 0008's, so a request, a transition and its approval are serialized per
# candidate. Owner decisions are written by asl_api, transitions by asl_agent as SYSTEM.
PROMOTION_GUARDS = """
CREATE FUNCTION asl_m7_approval_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE expected_hash text; p record; latest text; declaration jsonb; policy jsonb; candidate uuid;
BEGIN
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
                SELECT definition INTO policy FROM execution_definitions WHERE kind = 'STRATEGY'
                    AND id = p.document->>'policy_id' AND sha256 = p.document->>'policy_sha256';
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
    ELSE RETURN NEW;
    END IF;
    IF expected_hash IS NULL OR expected_hash <> NEW.target_sha256 THEN
        RAISE EXCEPTION 'M6 approval target/hash mismatch'; END IF;
    IF current_user <> 'asl_api' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'M6 approvals are owner records'; END IF;
    RETURN NEW;
END $$;
CREATE FUNCTION asl_m7_candidate_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE previous text; p record; latest record;
BEGIN
    IF current_user NOT IN ('asl_agent','asl_research') AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'candidate transitions require SYSTEM authority'; END IF;
    PERFORM pg_advisory_xact_lock(hashtextextended(NEW.candidate_id::text,608));
    SELECT state INTO previous FROM research_candidate_events WHERE candidate_id=NEW.candidate_id ORDER BY seq DESC LIMIT 1;
    IF NEW.previous_state IS DISTINCT FROM previous THEN RAISE EXCEPTION 'candidate transition is stale'; END IF;
    IF NEW.state = 'MAIN_APPROVED' THEN
        -- Only the agent worker applies the owner's approval, and only the approval that is still current.
        IF previous IS DISTINCT FROM 'MAIN_APPROVAL_PENDING' OR (current_user <> 'asl_agent' AND NOT asl_is_superuser()) THEN
            RAISE EXCEPTION 'MAIN_APPROVED follows MAIN_APPROVAL_PENDING and is applied by the agent worker'; END IF;
        SELECT r.id, r.sha256 INTO p FROM research_promotions r JOIN agent_workflows w ON w.id = r.workflow_id
            WHERE r.id::text = NEW.gate_evidence->>'promotion_id' AND r.candidate_id = NEW.candidate_id
            AND r.state = 'APPROVED' AND w.template_id = 'PROMOTION_V2';
        IF NOT FOUND THEN RAISE EXCEPTION 'MAIN_APPROVED needs the owner''s current approval of its promotion'; END IF;
        SELECT x.id, x.action INTO latest FROM agent_approvals x WHERE x.target_kind = 'PROMOTION'
            AND x.target_id = p.id::text AND x.target_sha256 = p.sha256 ORDER BY x.seq DESC LIMIT 1;
        IF latest.action IS DISTINCT FROM 'APPROVE'
                OR latest.id::text IS DISTINCT FROM NEW.gate_evidence->>'approval_id' THEN
            RAISE EXCEPTION 'MAIN_APPROVED needs the owner''s current approval of its promotion'; END IF;
        RETURN NEW;
    END IF;
    IF previous IS NULL AND NEW.state='DRAFT' THEN RETURN NEW; END IF;
    IF (previous || '>' || NEW.state) IN ('DRAFT>VALIDATED','VALIDATED>TEST_QUEUED','TEST_QUEUED>TESTED',
          'TESTED>SHADOW_ELIGIBLE','SHADOW_ELIGIBLE>SHADOW_RUNNING','SHADOW_RUNNING>EVIDENCE_READY',
          'EVIDENCE_READY>MAIN_APPROVAL_PENDING','SUSPENDED>RETIRED')
          OR (previous IS NOT NULL AND previous NOT IN ('REJECTED','RETIRED') AND NEW.state IN ('REJECTED','SUSPENDED','RETIRED')) THEN
        IF NEW.gate_evidence='{}'::jsonb THEN RAISE EXCEPTION 'candidate transition requires gate evidence'; END IF;
        RETURN NEW;
    END IF;
    RAISE EXCEPTION 'candidate transition is not allowed';
END $$;
CREATE FUNCTION asl_m7_promotion_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE template text; current_state text; latest text; pair text; owner_decided boolean := false; allowed boolean := false;
BEGIN
    IF TG_OP='INSERT' THEN
        IF NEW.version <> 0 THEN RAISE EXCEPTION 'M6 records start at version zero'; END IF;
        IF NEW.state<>'PENDING' THEN RAISE EXCEPTION 'promotion starts pending'; END IF;
        IF current_user<>'asl_agent' AND NOT asl_is_superuser() THEN RAISE EXCEPTION 'promotion requires coordinator workflow'; END IF;
        SELECT template_id INTO template FROM agent_workflows WHERE id=NEW.workflow_id AND role='COORDINATOR'
            AND template_id IN ('PROMOTION_V1','PROMOTION_V2');
        IF NOT FOUND THEN RAISE EXCEPTION 'promotion workflow role mismatch'; END IF;
        PERFORM pg_advisory_xact_lock(hashtextextended(NEW.candidate_id::text,608));
        SELECT state INTO current_state FROM research_candidate_events WHERE candidate_id=NEW.candidate_id
            ORDER BY seq DESC LIMIT 1;
        IF template = 'PROMOTION_V2' THEN
            IF NEW.document->>'requested_scope' IS DISTINCT FROM 'ENTRY_BASIS_UNDER_AGENT_POLICY_V1' THEN
                RAISE EXCEPTION 'an entry-basis request carries the scope the server writes'; END IF;
            IF EXISTS (SELECT 1 FROM research_promotions r JOIN agent_workflows w ON w.id = r.workflow_id
                       WHERE r.candidate_id = NEW.candidate_id AND w.template_id = 'PROMOTION_V2'
                       AND r.state IN ('PENDING','APPROVED')) THEN
                RAISE EXCEPTION 'the candidate has an open entry-basis request'; END IF;
            -- A pending request for consideration alone may be superseded; SYSTEM withdraws it in this transaction.
            -- One the owner has decided is not: the decision is applied first.
            IF current_state IS DISTINCT FROM 'EVIDENCE_READY' AND NOT (current_state = 'MAIN_APPROVAL_PENDING'
                    AND EXISTS (SELECT 1 FROM research_promotions r WHERE r.candidate_id = NEW.candidate_id
                                AND r.state = 'PENDING')) THEN
                RAISE EXCEPTION 'promotion requires EVIDENCE_READY'; END IF;
            IF EXISTS (SELECT 1 FROM research_promotions r JOIN agent_approvals x ON x.target_kind = 'PROMOTION'
                       AND x.target_id = r.id::text WHERE r.candidate_id = NEW.candidate_id AND r.state = 'PENDING') THEN
                RAISE EXCEPTION 'the owner decided the pending request; the decision is applied first'; END IF;
        ELSIF current_state IS DISTINCT FROM 'EVIDENCE_READY' THEN
            RAISE EXCEPTION 'promotion requires EVIDENCE_READY';
        END IF;
        RETURN NEW;
    END IF;
    IF NEW.version<>OLD.version+1 THEN RAISE EXCEPTION 'M6 version must increase by one'; END IF;
    IF (to_jsonb(NEW)-ARRAY['state','version']) IS DISTINCT FROM (to_jsonb(OLD)-ARRAY['state','version']) THEN
        RAISE EXCEPTION 'M6 record identity is immutable'; END IF;
    pair:=OLD.state || '>' || NEW.state;
    SELECT action INTO latest FROM agent_approvals WHERE target_kind='PROMOTION' AND target_id=OLD.id::text
        AND target_sha256=OLD.sha256 ORDER BY seq DESC LIMIT 1;
    IF pair IN ('PENDING>APPROVED','PENDING>REVOKED','APPROVED>REVOKED') THEN
        -- Never without the owner's record, for any identity.
        SELECT template_id INTO template FROM agent_workflows WHERE id=OLD.workflow_id;
        owner_decided := template = 'PROMOTION_V2'
            AND latest IS NOT DISTINCT FROM (CASE WHEN NEW.state='APPROVED' THEN 'APPROVE' ELSE 'REVOKE' END);
        IF NOT owner_decided OR current_user<>'asl_agent' THEN
            RAISE EXCEPTION 'M6 transition % is not allowed for %',pair,current_user; END IF;
        RETURN NEW;
    END IF;
    allowed:=current_user='asl_agent' AND OLD.state='PENDING' AND NEW.state IN ('REJECTED','WITHDRAWN');
    IF pair = 'PENDING>WITHDRAWN' THEN
        -- The candidate's lock, then the owner's latest record: a rejection is applied, never withdrawn over.
        PERFORM pg_advisory_xact_lock(hashtextextended(OLD.candidate_id::text,608));
        SELECT action INTO latest FROM agent_approvals WHERE target_kind='PROMOTION' AND target_id=OLD.id::text
            AND target_sha256=OLD.sha256 ORDER BY seq DESC LIMIT 1;
        IF latest IS NOT DISTINCT FROM 'REJECT' THEN
            RAISE EXCEPTION 'the owner rejected the promotion; it is not withdrawn'; END IF;
    END IF;
    IF NOT allowed AND NOT (asl_is_superuser() AND OLD.fixture) THEN
        RAISE EXCEPTION 'M6 transition % is not allowed for %',pair,current_user; END IF;
    RETURN NEW;
END $$;
"""

FUNCTION_SQL = """
CREATE FUNCTION decision_hold_permission_epoch() RETURNS bigint
LANGUAGE sql SECURITY DEFINER SET search_path = pg_catalog, public, pg_temp AS $$
    SELECT epoch FROM public.agent_permission_epoch WHERE id = 1 FOR KEY SHARE SKIP LOCKED
$$;
REVOKE ALL ON FUNCTION decision_hold_permission_epoch() FROM PUBLIC;
CREATE FUNCTION asl_m7_install_definition(p_id text, p_kind text, p_version integer, p_status text,
                                          p_canonical text, p_sha256 text) RETURNS text
LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE document jsonb; stored text; open_run uuid;
BEGIN
    IF NOT asl_is_superuser() THEN RAISE EXCEPTION 'definitions are installed by the migration identity'; END IF;
    IF p_kind NOT IN ('STRATEGY','EVALUATION_PROTOCOL') THEN
        RAISE EXCEPTION 'only an operating policy or an evaluation protocol is installed here'; END IF;
    IF encode(digest(convert_to(p_canonical,'UTF8'),'sha256'),'hex') IS DISTINCT FROM p_sha256 THEN
        RAISE EXCEPTION 'definition hash mismatch'; END IF;
    document := p_canonical::jsonb;
    IF document->>'id' IS DISTINCT FROM p_id OR document->>'kind' IS DISTINCT FROM p_kind
            OR document->>'version' IS DISTINCT FROM p_version::text OR document->>'status' IS DISTINCT FROM p_status THEN
        RAISE EXCEPTION 'definition fields differ from its document'; END IF;
    IF p_kind = 'STRATEGY' AND document->>'policy_kind' IS DISTINCT FROM 'AGENT_DRIVEN' THEN
        RAISE EXCEPTION 'only an agent-driven operating policy is installed here'; END IF;
    SELECT sha256 INTO stored FROM execution_definitions WHERE id = p_id;
    IF FOUND THEN
        IF stored <> p_sha256 THEN RAISE EXCEPTION 'definition % exists with another hash', p_id; END IF;
        RETURN 'PRESENT';
    END IF;
    SELECT x.id INTO open_run FROM experiments x JOIN experiment_manifests m ON m.id = x.manifest_id
        LEFT JOIN execution_definitions s ON s.id = m.manifest #>> '{definitions,strategy,id}'
        WHERE x.mode = 'FORWARD_PAPER' AND x.state IN ('DRAFT','READY','RUNNING','PAUSED','STOPPING')
          AND (s.id IS NULL OR s.kind <> 'STRATEGY' OR s.definition->>'policy_kind' IS DISTINCT FROM 'AGENT_DRIVEN')
        LIMIT 1;
    IF open_run IS NOT NULL THEN
        RAISE EXCEPTION 'a forward experiment of another strategy is open; nothing is installed'; END IF;
    INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256)
        VALUES (p_id, p_kind, p_version, p_status, document, p_canonical, p_sha256);
    RETURN 'INSTALLED';
END $$;
REVOKE ALL ON FUNCTION asl_m7_install_definition(text,text,integer,text,text,text) FROM PUBLIC;
"""

# B6c: the control replay (section 5.11). A period is frozen at the run's activation plus a whole number of
# 21-day periods, holds at most 21 days and ends with the run; one period of a run is open at a time. No
# key names an M1-M4 table: the guard reads the run through the research identity's own view. 21 days are
# written as 504 hours: a day interval follows the session's time zone across a daylight-saving change.
CONTROL_SQL = """
CREATE TABLE research_controls (
    id uuid PRIMARY KEY, run_id uuid NOT NULL, period integer NOT NULL CHECK (period >= 0),
    policy_id varchar(64) NOT NULL, policy_sha256 varchar(64) NOT NULL CHECK (policy_sha256 ~ '^[0-9a-f]{64}$'),
    reference_id varchar(64) NOT NULL CHECK (reference_id = 'TREND_REFERENCE_V1'),
    reference_sha256 varchar(64) NOT NULL CHECK (reference_sha256 ~ '^[0-9a-f]{64}$'),
    envelope_sha256 varchar(64) NOT NULL, activated_at timestamptz NOT NULL, frozen_at timestamptz NOT NULL,
    end_at timestamptz NOT NULL, run_ended_at timestamptz,
    virtual_funding numeric NOT NULL CHECK (virtual_funding = 10000),
    state varchar(12) NOT NULL DEFAULT 'QUEUED' CHECK (state IN ('QUEUED','RUNNING','SUCCEEDED','INCOMPLETE','SUSPENDED')),
    version bigint NOT NULL DEFAULT 0 CHECK (version >= 0), last_available_at timestamptz, prefix_fingerprint varchar(64),
    detail jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    UNIQUE (run_id, period),
    CHECK (frozen_at = activated_at + period * interval '504 hours' AND end_at = frozen_at + interval '504 hours'),
    CHECK (run_ended_at IS NULL OR run_ended_at > activated_at)
);
CREATE UNIQUE INDEX research_controls_one_open ON research_controls(run_id) WHERE state IN ('QUEUED','RUNNING');
CREATE TABLE research_control_marks (
    id uuid PRIMARY KEY, control_id uuid NOT NULL REFERENCES research_controls(id),
    job_id uuid NOT NULL UNIQUE REFERENCES research_jobs(id), available_through timestamptz NOT NULL,
    prefix_fingerprint varchar(64) NOT NULL, canonical text NOT NULL, document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(), fixture boolean NOT NULL DEFAULT false,
    UNIQUE (control_id, available_through)
);
CREATE VIEW research_read.agent_runs WITH (security_barrier = true) AS
    SELECT x.id AS run_id, x.state, d.id AS policy_id, d.sha256 AS policy_sha256,
           (SELECT min(a.at) FROM experiment_events a WHERE a.experiment_id = x.id AND a.kind = 'ACTIVATED')
               AS activated_at,
           (SELECT min(e.at) FROM experiment_events e WHERE e.experiment_id = x.id AND e.kind IN ('STOPPED','FAILED'))
               AS ended_at
    FROM experiments x
    JOIN experiment_manifests m ON m.id = x.manifest_id
    JOIN execution_definitions d ON d.id = m.manifest #>> '{definitions,strategy,id}'
        AND d.sha256 = m.manifest #>> '{definitions,strategy,sha256}'
    WHERE x.mode = 'FORWARD_PAPER' AND d.kind = 'STRATEGY' AND d.definition->>'policy_kind' = 'AGENT_DRIVEN'
        AND EXISTS (SELECT 1 FROM experiment_events a WHERE a.experiment_id = x.id AND a.kind = 'ACTIVATED');
CREATE FUNCTION asl_m7_control_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE r record; job record; pair text;
    mutable text[] := ARRAY['state','version','last_available_at','prefix_fingerprint','run_ended_at','detail'];
BEGIN
    -- One branch per table: a field of another table's row is never named.
    IF TG_TABLE_NAME = 'research_jobs' THEN
        IF NEW.kind <> 'CONTROL' THEN RETURN NEW; END IF;
        IF TG_OP = 'INSERT' THEN
            IF current_user <> 'asl_research' AND NOT asl_is_superuser() THEN
                RAISE EXCEPTION 'control work is queued by the research identity'; END IF;
            IF NOT EXISTS (SELECT 1 FROM research_controls c WHERE c.id::text = NEW.reservation->>'control_id'
                           AND c.state IN ('QUEUED','RUNNING')) THEN
                RAISE EXCEPTION 'control work needs its open control period'; END IF;
        ELSIF NEW.owner_cancel_request IS NOT NULL THEN
            RAISE EXCEPTION 'control work takes no owner cancel request';
        END IF;
        RETURN NEW;
    ELSIF TG_TABLE_NAME = 'research_results' THEN
        SELECT kind INTO job FROM research_jobs WHERE id = NEW.job_id;
        IF (NEW.candidate_id IS NULL) IS DISTINCT FROM (job.kind = 'CONTROL') THEN
            RAISE EXCEPTION 'a result names its candidate unless it is control work'; END IF;
        RETURN NEW;
    ELSIF TG_TABLE_NAME = 'research_control_marks' THEN
        IF current_user <> 'asl_research' AND NOT asl_is_superuser() THEN
            RAISE EXCEPTION 'a control mark is recorded by the research identity'; END IF;
        IF NOT EXISTS (SELECT 1 FROM research_jobs j WHERE j.id = NEW.job_id AND j.kind = 'CONTROL'
                       AND j.reservation->>'control_id' = NEW.control_id::text) THEN
            RAISE EXCEPTION 'a control mark binds control work of its own period'; END IF;
        RETURN NEW;
    END IF;
    SELECT * INTO r FROM research_read.agent_runs WHERE run_id = NEW.run_id;
    IF TG_OP = 'INSERT' THEN
        IF current_user <> 'asl_research' AND NOT asl_is_superuser() THEN
            RAISE EXCEPTION 'a control period is started by the research identity'; END IF;
        IF NEW.version <> 0 OR NEW.state <> 'QUEUED' THEN
            RAISE EXCEPTION 'a control period starts queued at version zero'; END IF;
        IF r.run_id IS NULL OR r.policy_id <> NEW.policy_id OR r.policy_sha256 <> NEW.policy_sha256
                OR r.activated_at <> NEW.activated_at THEN
            RAISE EXCEPTION 'a control period binds an activated agent run, its policy and its activation'; END IF;
        IF NEW.run_ended_at IS DISTINCT FROM r.ended_at OR NEW.run_ended_at <= NEW.frozen_at
                OR NEW.frozen_at > clock_timestamp() THEN
            RAISE EXCEPTION 'a control period starts after its freeze and before its run ended'; END IF;
        IF NEW.period > 0 AND NOT EXISTS (SELECT 1 FROM research_controls c WHERE c.run_id = NEW.run_id
                AND c.period = NEW.period - 1 AND c.state NOT IN ('QUEUED','RUNNING')) THEN
            RAISE EXCEPTION 'a control period follows its ended predecessor'; END IF;
        RETURN NEW;
    END IF;
    IF NEW.version <> OLD.version + 1 THEN RAISE EXCEPTION 'a control period''s version increases by one'; END IF;
    IF current_user <> 'asl_research' AND NOT (asl_is_superuser() AND OLD.fixture) THEN
        RAISE EXCEPTION 'a control period is moved by the research identity'; END IF;
    IF (to_jsonb(NEW) - mutable) IS DISTINCT FROM (to_jsonb(OLD) - mutable) THEN
        RAISE EXCEPTION 'a control period''s identity is immutable'; END IF;
    pair := OLD.state || '>' || NEW.state;
    IF NOT (pair IN ('QUEUED>QUEUED','QUEUED>RUNNING','RUNNING>RUNNING','RUNNING>SUCCEEDED')
            OR (OLD.state IN ('QUEUED','RUNNING') AND NEW.state IN ('INCOMPLETE','SUSPENDED'))) THEN
        RAISE EXCEPTION 'control period transition % is not allowed', pair; END IF;
    IF NEW.last_available_at < OLD.last_available_at THEN
        RAISE EXCEPTION 'a control period''s watermark cannot decrease'; END IF;
    IF OLD.run_ended_at IS NOT NULL AND NEW.run_ended_at IS DISTINCT FROM OLD.run_ended_at THEN
        RAISE EXCEPTION 'a run''s end is recorded once'; END IF;
    IF OLD.run_ended_at IS NULL AND NEW.run_ended_at IS NOT NULL
            AND (NEW.run_ended_at IS DISTINCT FROM r.ended_at OR NEW.run_ended_at <= NEW.frozen_at) THEN
        RAISE EXCEPTION 'a control period records its run''s recorded end, after its freeze'; END IF;
    RETURN NEW;
END $$;
"""

GRANTS = """
GRANT SELECT ON decision_snapshots, decision_intents, decision_submissions, decision_withdrawals,
    decision_verifications, decision_pause_requests, decision_events, decision_position_terms,
    decision_stop_updates, decision_outcomes TO asl_api;
GRANT SELECT, INSERT ON decision_snapshots, decision_intents, decision_submissions, decision_withdrawals,
    decision_verifications, decision_pause_requests, decision_outcomes TO asl_agent;
GRANT INSERT ON decision_pause_requests TO asl_api;
GRANT SELECT ON decision_intents, decision_submissions, decision_withdrawals, decision_pause_requests TO asl_execution;
GRANT SELECT, INSERT ON decision_events, decision_position_terms, decision_stop_updates TO asl_execution;
GRANT USAGE, SELECT ON SEQUENCE decision_submissions_seq_seq, decision_withdrawals_seq_seq,
    decision_verifications_seq_seq, decision_pause_requests_seq_seq TO asl_agent;
GRANT USAGE, SELECT ON SEQUENCE decision_pause_requests_seq_seq TO asl_api;
GRANT USAGE, SELECT ON SEQUENCE decision_events_seq_seq TO asl_execution;
GRANT SELECT ON agent_read.policy_runs, agent_read.policy_definitions, agent_read.policy_approvals,
    agent_read.policy_run_events, agent_read.policy_positions, agent_read.policy_position_events,
    agent_read.policy_orders, agent_read.policy_order_events, agent_read.policy_fills,
    agent_read.policy_exit_obligations, agent_read.policy_evaluations, agent_read.policy_risk_decisions,
    agent_read.policy_valuations, agent_read.policy_account, agent_read.policy_holdings,
    agent_read.policy_daily_references, agent_read.policy_latches, agent_read.engine_decision_events,
    agent_read.engine_position_terms, agent_read.engine_stop_updates TO asl_agent;
GRANT EXECUTE ON FUNCTION decision_hold_permission_epoch() TO asl_execution;
GRANT USAGE ON SCHEMA evaluation_read TO asl_evaluation;
GRANT SELECT ON evaluation_read.decision_intents, evaluation_read.decision_submissions,
    evaluation_read.decision_events, evaluation_read.decision_withdrawals, evaluation_read.decision_pause_requests,
    evaluation_read.decision_workflows, evaluation_read.decision_steps, evaluation_read.decision_tool_calls,
    evaluation_read.decision_reviews, evaluation_read.decision_documents, evaluation_read.runtime_events
    TO asl_evaluation;
GRANT SELECT ON research_read.agent_runs TO asl_research;
GRANT SELECT, INSERT ON research_controls, research_control_marks TO asl_research;
GRANT UPDATE (state, version, last_available_at, prefix_fingerprint, run_ended_at, detail) ON research_controls
    TO asl_research;
"""

# Agent definitions v3 (B5; ExecPlan 0026 section 5.6): schema, catalog, grants, templates, budgets and the three
# M7 prompts. (id, kind, version, status, canonical JSON, SHA-256) as printed by
# ``python -m app.agents.definitions_v3``; a frozen copy, compared with the code by a test. They are added beside
# the M5 and M6 rows, which stay. Seeding approves nothing: a runtime profile that binds these hashes is a new
# document the owner has not approved.
AGENT_SEED_LINES_V3 = r"""
["AGENT_STEP_SCHEMA_V3", "AGENT_STEP_SCHEMA", 3, "CODE_OWNED", "{\"id\":\"AGENT_STEP_SCHEMA_V3\",\"kind\":\"AGENT_STEP_SCHEMA\",\"schema\":{\"additionalProperties\":false,\"description\":\"Exactly one application step: a TOOL_REQUEST or a FINISH. Echo job_id, step_id and input_hash.\",\"properties\":{\"finish\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"abstain\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"INSUFFICIENT_EVIDENCE\",\"DATA_STALE\",\"CAPABILITY_UNAVAILABLE\",\"OTHER\"],\"type\":\"string\"}},\"required\":[\"reason_code\",\"note\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"assessment\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"expiry_hours\":{\"type\":\"integer\"},\"hypotheses\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"statement\",\"cites\",\"invalidation\"],\"type\":\"object\"},\"type\":\"array\"},\"missing_evidence\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"observations\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"kind\":{\"enum\":[\"OBSERVATION\",\"CALCULATION\"],\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"kind\",\"statement\",\"cites\"],\"type\":\"object\"},\"type\":\"array\"},\"research_question\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"type\":\"array\"},\"uncertainty\":{\"additionalProperties\":false,\"properties\":{\"level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"},\"reasons\":{\"type\":\"string\"}},\"required\":[\"level\",\"reasons\"],\"type\":\"object\"}},\"required\":[\"symbols\",\"summary\",\"observations\",\"hypotheses\",\"uncertainty\",\"missing_evidence\",\"expiry_hours\",\"research_question\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"decision\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"owner_review_requested\":{\"type\":\"boolean\"},\"summary\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"action\":{\"enum\":[\"ENTER\",\"EXIT\",\"CANCEL_ENTRY\",\"TIGHTEN_STOP\",\"HOLD\",\"ABSTAIN\"],\"type\":\"string\"},\"intent_id\":{\"type\":[\"string\",\"null\"]},\"note\":{\"type\":\"string\"},\"reason_code\":{\"enum\":[\"EVIDENCE_SUPPORTS_ACTION\",\"INSUFFICIENT_EVIDENCE\",\"CONFLICTING_EVIDENCE\",\"DATA_STALE\",\"REVIEW_NOT_ACCEPTABLE\",\"LIMIT_OR_COOLDOWN\",\"PROTECT_POSITION\",\"NO_CHANGE_NEEDED\",\"REFUSED_BY_APPLICATION\",\"OTHER\"],\"type\":\"string\"},\"symbol\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"}},\"required\":[\"symbol\",\"action\",\"intent_id\",\"reason_code\",\"note\"],\"type\":\"object\"},\"type\":\"array\"}},\"required\":[\"summary\",\"symbols\",\"owner_review_requested\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"outcome\":{\"enum\":[\"ARTIFACT\",\"ABSTAIN\"],\"type\":\"string\"},\"promotion\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_id\":{\"type\":\"string\"},\"candidate_sha256\":{\"type\":\"string\"},\"evidence_refs\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"rationale\":{\"type\":\"string\"}},\"required\":[\"candidate_id\",\"candidate_sha256\",\"evidence_refs\",\"rationale\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"research_proposal\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"candidate_ids\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"hypothesis_id\":{\"type\":\"string\"},\"limitations\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"nominated_candidate_id\":{\"type\":[\"string\",\"null\"]},\"summary\":{\"type\":\"string\"}},\"required\":[\"hypothesis_id\",\"summary\",\"candidate_ids\",\"nominated_candidate_id\",\"cites\",\"limitations\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"review\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiencies\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"deficiency_codes\":{\"items\":{\"enum\":[\"INSUFFICIENT_SAMPLE\",\"DATA_GAPS\",\"INTEGRITY_FAILURE\",\"COST_UNCERTAINTY\",\"HISTORICAL_CONTAMINATION\",\"MISSING_BASELINE\",\"INCOMPLETE_TEST_SET\",\"UNSUPPORTED_CLAIM\"],\"type\":\"string\"},\"type\":\"array\"},\"results\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"result_ref\":{\"type\":\"string\"},\"sha256\":{\"type\":\"string\"}},\"required\":[\"result_ref\",\"sha256\"],\"type\":\"object\"},\"type\":\"array\"},\"review_type\":{\"enum\":[\"ASSESSMENT_REVIEW\",\"CANDIDATE_REVIEW\",\"INTENT_REVIEW\",\"OUTCOME_REVIEW\"],\"type\":\"string\"},\"supported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\",\"intent\",\"outcome\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"target_artifact_id\":{\"type\":\"string\"},\"target_sha256\":{\"type\":\"string\"},\"unsupported_claims\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"index\":{\"type\":\"integer\"},\"note\":{\"type\":\"string\"},\"section\":{\"enum\":[\"observations\",\"hypotheses\",\"proposal\",\"results\",\"intent\",\"outcome\"],\"type\":\"string\"}},\"required\":[\"section\",\"index\",\"note\"],\"type\":\"object\"},\"type\":\"array\"},\"verdict\":{\"enum\":[\"ACCEPTABLE\",\"NEEDS_EVIDENCE\",\"REJECT\"],\"type\":\"string\"}},\"required\":[\"review_type\",\"target_artifact_id\",\"target_sha256\",\"verdict\",\"supported_claims\",\"unsupported_claims\",\"deficiencies\",\"cites\",\"results\",\"deficiency_codes\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"outcome\",\"assessment\",\"review\",\"research_proposal\",\"promotion\",\"decision\",\"abstain\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"input_hash\":{\"type\":\"string\"},\"job_id\":{\"type\":\"string\"},\"kind\":{\"enum\":[\"TOOL_REQUEST\",\"FINISH\"],\"type\":\"string\"},\"schema_version\":{\"enum\":[\"asl.agent_step.v3\"],\"type\":\"string\"},\"step_id\":{\"type\":\"string\"},\"tool_request\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"arguments\":{\"additionalProperties\":false,\"description\":\"Every field a tool does not use must be null.\",\"properties\":{\"artifact_id\":{\"type\":[\"string\",\"null\"]},\"as_of\":{\"type\":[\"string\",\"null\"]},\"candidate\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One flat CANDIDATE_GRAMMAR_V1 declaration. Operators, comparisons and domains are in the job context.\",\"properties\":{\"entry\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":\"array\"},\"exit\":{\"additionalProperties\":false,\"properties\":{\"atr_period\":{\"type\":\"integer\"},\"max_hold_hours\":{\"type\":\"integer\"},\"signal\":{\"items\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"left\":{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},\"operator\":{\"type\":\"string\"},\"right_constant\":{\"type\":[\"string\",\"null\"]},\"right_feature\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"operator\":{\"type\":\"string\"},\"period\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"operator\",\"period\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"left\",\"operator\",\"right_feature\",\"right_constant\"],\"type\":\"object\"},\"type\":\"array\"},\"type\":[\"array\",\"null\"]},\"stop_multiple\":{\"type\":\"string\"}},\"required\":[\"atr_period\",\"stop_multiple\",\"max_hold_hours\",\"signal\"],\"type\":\"object\"},\"grammar_version\":{\"type\":\"string\"},\"symbols\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"timeframe\":{\"type\":\"string\"},\"warmup_bars\":{\"type\":\"integer\"}},\"required\":[\"grammar_version\",\"symbols\",\"timeframe\",\"warmup_bars\",\"entry\",\"exit\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"candidate_id\":{\"type\":[\"string\",\"null\"]},\"dataset_id\":{\"type\":[\"string\",\"null\"]},\"experiment_id\":{\"type\":[\"string\",\"null\"]},\"feature_ids\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"filters\":{\"items\":{\"additionalProperties\":false,\"properties\":{\"name\":{\"type\":\"string\"},\"value\":{\"type\":\"integer\"}},\"required\":[\"name\",\"value\"],\"type\":\"object\"},\"type\":[\"array\",\"null\"]},\"hypothesis\":{\"anyOf\":[{\"additionalProperties\":false,\"properties\":{\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"dataset_id\":{\"type\":\"string\"},\"invalidation\":{\"type\":\"string\"},\"statement\":{\"type\":\"string\"}},\"required\":[\"dataset_id\",\"statement\",\"invalidation\",\"cites\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"hypothesis_id\":{\"type\":[\"string\",\"null\"]},\"intent\":{\"anyOf\":[{\"additionalProperties\":false,\"description\":\"One draft. Choices only from the policy's sets in the job context; never a price, quantity or level.\",\"properties\":{\"action\":{\"enum\":[\"ENTER\",\"EXIT\",\"CANCEL_ENTRY\",\"TIGHTEN_STOP\"],\"type\":\"string\"},\"basis_ref\":{\"type\":[\"string\",\"null\"]},\"cites\":{\"items\":{\"type\":\"string\"},\"type\":\"array\"},\"entry_basis\":{\"enum\":[\"ASSESSMENT\",\"CANDIDATE\",null],\"type\":[\"string\",\"null\"]},\"expiry_minutes\":{\"type\":\"integer\"},\"exposure_fraction\":{\"type\":[\"string\",\"null\"]},\"invalidation\":{\"type\":\"string\"},\"max_hold_hours\":{\"type\":[\"integer\",\"null\"]},\"position_id\":{\"type\":[\"string\",\"null\"]},\"rationale\":{\"type\":\"string\"},\"stop_multiple\":{\"type\":[\"string\",\"null\"]},\"symbol\":{\"enum\":[\"BTCUSDT\",\"SOLUSDT\"],\"type\":\"string\"},\"tightening\":{\"type\":[\"string\",\"null\"]},\"uncertainty_level\":{\"enum\":[\"LOW\",\"MEDIUM\",\"HIGH\"],\"type\":\"string\"}},\"required\":[\"action\",\"symbol\",\"position_id\",\"expiry_minutes\",\"exposure_fraction\",\"stop_multiple\",\"max_hold_hours\",\"tightening\",\"entry_basis\",\"basis_ref\",\"cites\",\"rationale\",\"invalidation\",\"uncertainty_level\"],\"type\":\"object\"},{\"type\":\"null\"}]},\"intent_id\":{\"type\":[\"string\",\"null\"]},\"limit\":{\"type\":[\"integer\",\"null\"]},\"pause_cites\":{\"items\":{\"type\":\"string\"},\"type\":[\"array\",\"null\"]},\"pause_reason\":{\"enum\":[\"EVIDENCE_CONFLICT\",\"DATA_QUALITY\",\"MARKET_DISLOCATION\",\"OUTCOME_CONCERN\",null],\"type\":[\"string\",\"null\"]},\"query\":{\"type\":[\"string\",\"null\"]},\"review_id\":{\"type\":[\"string\",\"null\"]},\"search_scope\":{\"enum\":[\"SOURCES\",\"ARTIFACTS\",null],\"type\":[\"string\",\"null\"]},\"source_id\":{\"type\":[\"string\",\"null\"]},\"symbol\":{\"type\":[\"string\",\"null\"]},\"view\":{\"enum\":[\"MARKET\",\"PORTFOLIO\",\"ACCOUNT\",null],\"type\":[\"string\",\"null\"]},\"window_hours\":{\"type\":[\"integer\",\"null\"]}},\"required\":[\"view\",\"as_of\",\"symbol\",\"feature_ids\",\"window_hours\",\"artifact_id\",\"search_scope\",\"query\",\"source_id\",\"filters\",\"limit\",\"hypothesis_id\",\"hypothesis\",\"candidate\",\"candidate_id\",\"dataset_id\",\"experiment_id\",\"intent\",\"intent_id\",\"review_id\",\"pause_reason\",\"pause_cites\"],\"type\":\"object\"},\"purpose\":{\"type\":\"string\"},\"tool_name\":{\"type\":\"string\"}},\"required\":[\"tool_name\",\"arguments\",\"purpose\"],\"type\":\"object\"},{\"type\":\"null\"}]}},\"required\":[\"schema_version\",\"job_id\",\"step_id\",\"input_hash\",\"kind\",\"tool_request\",\"finish\"],\"type\":\"object\"},\"schema_version\":\"asl.agent_step.v3\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M7 tool catalog v3 and ExecPlan 0026 sections 5.6 to 5.9\",\"status\":\"CODE_OWNED\",\"validation\":\"STRICT_JSON_THEN_PYDANTIC_FORBID_UNKNOWN_FIELDS\",\"version\":3}", "f112077d1bf3b19e03f3b14582ed8c6a4da8cc34d09f31b8922be1ca9a3abb9e"]
["TOOL_CATALOG_V3", "TOOL_CATALOG", 3, "CODE_OWNED", "{\"absent_tools\":[],\"id\":\"TOOL_CATALOG_V3\",\"kind\":\"TOOL_CATALOG\",\"queued_status\":\"ACCEPTED\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M7 tool catalog v3 and ExecPlan 0026 sections 5.6 to 5.9\",\"status\":\"CODE_OWNED\",\"tools\":[{\"arguments\":[\"view\",\"as_of\"],\"description\":\"view MARKET: the market-only least-data view at the job cutoff, as in catalog v2. view PORTFOLIO (COORDINATOR in a decision; EVALUATOR in an intent review): the portfolio snapshot stored once when the decision workflow started, with its hash and state key; every read in the workflow returns the same snapshot and as_of must be null. Any other view, or PORTFOLIO in another workflow, is refused.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"get_snapshot\"},{\"arguments\":[\"symbol\",\"feature_ids\",\"window_hours\",\"as_of\"],\"description\":\"Registered features over finalized 1h candles for BTCUSDT or SOLUSDT, evaluated at the last finalized bar at or before as_of (default: the job cutoff). feature_ids: 1-6 registered IDs; window_hours: 1-168 (OHLCV_1H_V1: at most 72). Returns exact decimal strings with inputs, warm-up and quality.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"query_market_features\"},{\"arguments\":[\"artifact_id\"],\"description\":\"Reads one typed artifact in this workflow's scope, or one evidence item that a result of this workflow or an artifact in its scope returned. Any other ID is refused. What a role may not see is withheld: a tuning role gets only the verdict and deficiency codes of a review that consulted holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_artifact\"},{\"arguments\":[\"search_scope\",\"query\",\"source_id\",\"symbol\",\"limit\"],\"description\":\"ANALYST and RESEARCHER. Plain-term search of approved evidence. search_scope SOURCES returns at most 10 items of approved sources that were available by the job cutoff; ARTIFACTS returns references to earlier typed artifacts. source_id and symbol narrow a SOURCES search. Each returned item can be cited by its ID. Never a URL or a web search.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"search_evidence\"},{\"arguments\":[\"source_id\",\"filters\"],\"description\":\"ANALYST and RESEARCHER. Queues one fetch of a registered, approved source by its ID, with that source's typed integer filters. Never a URL, host or path. Returns ACCEPTED with a request reference; the workflow then waits and resumes with one completion.\",\"effect\":\"QUEUE_SOURCE_REFRESH\",\"finish_only\":false,\"name\":\"request_source_refresh\"},{\"arguments\":[\"hypothesis\",\"hypothesis_id\",\"candidate\"],\"description\":\"RESEARCHER. Records this workflow's hypothesis (first call: hypothesis; later calls: hypothesis_id) and one declaration in CANDIDATE_GRAMMAR_V1 inside the approved envelope's domains. Returns the candidate ID and normalized hash, or the existing candidate. Registration tests nothing and grants nothing.\",\"effect\":\"RECORD_RESEARCH\",\"finish_only\":false,\"name\":\"register_candidate\"},{\"arguments\":[\"candidate_id\",\"dataset_id\"],\"description\":\"RESEARCHER. Queues the registered screening set (DEV and VALIDATION, cost scenario H1) for one of this workflow's candidates on its bound dataset. Returns ACCEPTED with an experiment reference; the workflow then waits and resumes with one completion. The holdout cannot be requested.\",\"effect\":\"QUEUE_RESEARCH_JOB\",\"finish_only\":false,\"name\":\"request_experiment\"},{\"arguments\":[\"experiment_id\"],\"description\":\"Reads one experiment or shadow by ID in the role's projection. A tuning role (ANALYST, RESEARCHER) reads screening results at or before its cutoff and never holdout or shadow results.\",\"effect\":\"READ\",\"finish_only\":false,\"name\":\"read_experiment\"},{\"arguments\":[\"intent\"],\"description\":\"COORDINATOR in a decision workflow. Records one immutable draft of ENTER, EXIT, CANCEL_ENTRY or TIGHTEN_STOP for BTCUSDT or SOLUSDT under the approved policy. Every choice is a member of the policy's set in the job context: expiry_minutes always; for ENTER exposure_fraction, stop_multiple (decimal text as listed) and max_hold_hours, with entry_basis ASSESSMENT and basis_ref a reviewed assessment in scope, or entry_basis CANDIDATE and basis_ref an approved candidate in scope whose stop_multiple and max_hold_hours the entry takes; for TIGHTEN_STOP the tightening template. position_id names a live position for EXIT and TIGHTEN_STOP. A price, quantity, stop level, fee or balance is never an argument. Returns the draft's ID and hash. At most two drafts a workflow.\",\"effect\":\"RECORD_INTENT_DRAFT\",\"finish_only\":false,\"name\":\"draft_trade_intent\"},{\"arguments\":[\"intent_id\"],\"description\":\"COORDINATOR. Starts the intent review of one of this workflow's drafts, bound to the draft's, the policy's and the snapshot's hashes. Returns ACCEPTED with the review reference; the workflow then waits and resumes with the review's verdict. A second request for the same draft returns the first.\",\"effect\":\"QUEUE_REVIEW\",\"finish_only\":false,\"name\":\"request_review\"},{\"arguments\":[\"intent_id\",\"review_id\"],\"description\":\"COORDINATOR. Submits one of this workflow's drafts to the execution engine. An ENTER needs its ACCEPTABLE intent review (review_id); any other action may carry one. Checked now: the policy approved and its run live, the draft unexpired, its decision bar still the latest, the review bound to it and to the current state, the basis still valid, nothing else of this workflow outstanding. Returns ACCEPTED with the submission reference; the workflow then waits and resumes with the engine's answer. The engine checks everything again against current state and may refuse.\",\"effect\":\"QUEUE_MAIN_INTENT\",\"finish_only\":false,\"name\":\"submit_trade_intent\"},{\"arguments\":[\"pause_reason\",\"pause_cites\"],\"description\":\"COORDINATOR in a decision workflow. Requests the discretionary entry pause with one enumerated reason and 1-8 cited records of this workflow. Existing positions keep their protection; only the owner resumes entries.\",\"effect\":\"QUEUE_ENTRY_PAUSE\",\"finish_only\":false,\"name\":\"request_entry_pause\"},{\"arguments\":[],\"description\":\"ANALYST only, through FINISH with finish.assessment. Records an immutable MarketAssessment; it may name one research question.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_assessment\"},{\"arguments\":[],\"description\":\"EVALUATOR only, through FINISH with finish.review. Records an immutable EvaluationReview bound to the exact target hash: an assessment, a draft (with the policy's and the snapshot's hashes) or an outcome record.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_review\"},{\"arguments\":[],\"description\":\"RESEARCHER only, through FINISH with finish.research_proposal. Records an immutable ResearchProposal and may nominate one tested candidate for the fixed review.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_research_proposal\"},{\"arguments\":[],\"description\":\"COORDINATOR only, in PROMOTION_V2, through FINISH with finish.promotion. Records a PENDING promotion request for the owner, whose scope the server writes: an entry basis under AGENT_POLICY_V1. Refused unless the candidate is EVIDENCE_READY (or holds only a pending consideration request) and its exit values lie in the policy's sets. Only the owner approves one, by its exact hash.\",\"effect\":\"QUEUE_OWNER_PROPOSAL\",\"finish_only\":true,\"name\":\"request_promotion\"},{\"arguments\":[],\"description\":\"COORDINATOR only, through FINISH with finish.decision. Records the immutable PortfolioDecision: per symbol the action taken or none, the draft it names, the reason code, and whether the owner's review is asked for. The server writes what became of each draft.\",\"effect\":\"RECORD_AGENT_ARTIFACT\",\"finish_only\":true,\"name\":\"record_decision\"}],\"unknown_tool\":\"UNKNOWN_TOOL\",\"version\":3}", "f509c37073057f6d7088ad68c7826e56bfeb1c970f23352d9912d65bb60caa95"]
["ROLE_GRANTS_V3", "ROLE_GRANTS", 3, "CODE_OWNED", "{\"authority\":\"docs/AUTONOMY_MATRIX.md\",\"effects_allowed\":[\"READ\",\"RECORD_AGENT_ARTIFACT\",\"QUEUE_SOURCE_REFRESH\",\"RECORD_RESEARCH\",\"QUEUE_RESEARCH_JOB\",\"QUEUE_OWNER_PROPOSAL\",\"RECORD_INTENT_DRAFT\",\"QUEUE_REVIEW\",\"QUEUE_MAIN_INTENT\",\"QUEUE_ENTRY_PAUSE\"],\"grants\":{\"ANALYST\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"search_evidence\",\"request_source_refresh\",\"read_experiment\",\"record_assessment\"],\"COORDINATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"read_experiment\",\"draft_trade_intent\",\"request_review\",\"submit_trade_intent\",\"request_entry_pause\",\"request_promotion\",\"record_decision\"],\"EVALUATOR\":[\"get_snapshot\",\"query_market_features\",\"read_artifact\",\"read_experiment\",\"record_review\"],\"RESEARCHER\":[]},\"id\":\"ROLE_GRANTS_V3\",\"kind\":\"ROLE_GRANTS\",\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M7 tool catalog v3 and ExecPlan 0026 sections 5.6 to 5.9\",\"status\":\"CODE_OWNED\",\"templates_by_role\":{\"ANALYST\":[\"MARKET_BRIEF_V1\"],\"COORDINATOR\":[\"PORTFOLIO_DECISION_V1\",\"PROMOTION_V2\"],\"EVALUATOR\":[\"BRIEF_REVIEW_V1\",\"INTENT_REVIEW_V1\",\"OUTCOME_REVIEW_V1\"],\"RESEARCHER\":[]},\"version\":3}", "d221a70368b3820e6aa21a2302af4d2fc4514db35da531d3862468d13a796548"]
["TEMPLATES_V3", "TEMPLATES", 3, "CODE_OWNED", "{\"delegation\":\"NONE_MODEL_CHOSEN; FIXED_CHILD_OR_THE_REVIEW_OF_ONE_OWN_DRAFT\",\"id\":\"TEMPLATES_V3\",\"kind\":\"TEMPLATES\",\"priority\":[\"PROBE\",\"OWNER\",\"DECISION\",\"PROMOTION\",\"BRIEF\",\"INVESTIGATION\",\"RESEARCH\"],\"source\":\"docs/AGENT_TOOL_CONTRACTS.md M7 tool catalog v3 and ExecPlan 0026 sections 5.6 to 5.9\",\"status\":\"CODE_OWNED\",\"templates\":{\"BRIEF_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"PARENT_CUTOFF_AND_THE_ITEMS_ITS_REFRESH_DELIVERED\",\"parent\":\"MARKET_BRIEF_V1\",\"prompt\":\"EVALUATOR_PROMPT_M7_V3\",\"purpose\":\"REVIEW\",\"review_type\":\"ASSESSMENT_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_PARENT_FINISH\"},\"INTENT_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"binds\":[\"INTENT_SHA256\",\"POLICY_SHA256\",\"SNAPSHOT_SHA256\"],\"budget\":\"OWN_CHILD_BUDGET\",\"cutoff\":\"PARENT_CUTOFF\",\"on_finish\":\"RESUMES_ITS_PARENT_WITH_A_COMPLETION\",\"parent\":\"PORTFOLIO_DECISION_V1\",\"prompt\":\"EVALUATOR_PROMPT_M7_V3\",\"purpose\":\"INTENT_REVIEW\",\"review_type\":\"INTENT_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":\"ORCHESTRATOR_ON_REQUEST_REVIEW\"},\"MARKET_BRIEF_V1\":{\"artifact\":\"MARKET_ASSESSMENT\",\"child\":\"BRIEF_REVIEW_V1\",\"cutoff\":\"FIXED_AT_START; OWN_REFRESH_IS_DELIVERED_BY_ITS_COMPLETION_ONLY\",\"follow_on\":\"NONE\",\"on_review\":\"ACCEPTABLE_RECORDS_AN_ASSESSMENT_READY_TRIGGER\",\"parameters\":{\"symbols\":{\"items\":[\"BTCUSDT\",\"SOLUSDT\"],\"max_items\":2,\"min_items\":1,\"unique\":true}},\"prompt\":\"ANALYST_PROMPT_M7_V3\",\"purpose\":\"BRIEF\",\"role\":\"ANALYST\",\"schedule\":{\"key\":\"ONE_PER_BRIEF_BAR\",\"rule\":\"THE_POLICY_CADENCE_BRIEF_HOURS_UTC_WHILE_ITS_RUN_IS_LIVE\",\"symbols\":\"BOTH\"},\"started_by\":[\"OWNER\",\"SCHEDULE\"]},\"OUTCOME_REVIEW_V1\":{\"artifact\":\"EVALUATION_REVIEW\",\"binds\":[\"OUTCOME_SHA256\"],\"context\":\"THE_OUTCOME_RECORD_AND_THE_ORIGINAL_DRAFT_AND_REVIEW_ONLY\",\"cutoff\":\"FIXED_AT_START\",\"parameters\":{},\"prompt\":\"EVALUATOR_PROMPT_M7_V3\",\"purpose\":\"OUTCOME_REVIEW\",\"review_type\":\"OUTCOME_REVIEW\",\"role\":\"EVALUATOR\",\"started_by\":[\"SYSTEM\"]},\"PORTFOLIO_DECISION_V1\":{\"artifact\":\"PORTFOLIO_DECISION\",\"cutoff\":\"FIXED_AT_START_WITH_THE_LATEST_FINAL_BAR_PER_SYMBOL\",\"on_end\":\"OUTSTANDING_SUBMISSIONS_ARE_WITHDRAWN_WHEN_IT_ENDS_CANCELED_EXPIRED_OR_FAILED\",\"parameters\":{},\"prompt\":\"COORDINATOR_PROMPT_M7_V2\",\"purpose\":\"DECISION\",\"requires\":[\"POLICY_INSTALLED_AND_APPROVED\",\"POLICY_RUN_RUNNING\",\"DECISION_SUITE_VERIFIED\"],\"review_child\":\"INTENT_REVIEW_V1\",\"role\":\"COORDINATOR\",\"scope\":\"THE_NEWEST_REVIEWED_ASSESSMENT_PER_SYMBOL_AND_THE_NEWEST_OUTCOME_REVIEWS\",\"snapshot\":\"STORED_ONCE_AT_START_FROM_THE_AGENT_READ_PORTFOLIO_VIEWS\",\"started_by\":[\"OWNER\",\"DECISION_TRIGGER\"],\"superseded\":\"EXPIRED_BAR_SUPERSEDED_WHEN_A_NEWER_BAR_FINALIZES_BEFORE_A_SUBMISSION\",\"triggers\":[\"ASSESSMENT_READY\",\"BAR_CLOSE\",\"POSITION_EVENT\"]},\"PROMOTION_V2\":{\"artifact\":\"PROMOTION_PROPOSAL\",\"cutoff\":\"FIXED_AT_START\",\"daily\":\"COUNTED_WITH_THE_PARENTS_OF_GENERATIONS_1_AND_2\",\"outcome\":\"PENDING_PROMOTION_OR_ABSTENTION; ONLY_THE_OWNER_APPROVES_REJECTS_OR_REVOKES_BY_EXACT_HASH\",\"parameters\":{\"candidate_id\":{\"type\":\"uuid\"}},\"prompt\":\"COORDINATOR_PROMOTION_PROMPT_M7_V1\",\"purpose\":\"PROMOTION\",\"requires\":[\"AGENT_POLICY_V1_INSTALLED\",\"CANDIDATE_EXIT_VALUES_IN_THE_POLICY_SETS\"],\"role\":\"COORDINATOR\",\"scope\":\"ENTRY_BASIS_UNDER_AGENT_POLICY_V1; WRITTEN_BY_THE_SERVER\",\"started_by\":[\"OWNER\",\"SYSTEM_ON_EVIDENCE_READY\"],\"supersedes\":\"A_PENDING_PROMOTION_V1_OF_THE_CANDIDATE_IS_WITHDRAWN_WHEN_THIS_REQUEST_IS_RECORDED\"}},\"version\":3}", "92a32817ad911ac07da995fb00f8a062f5c1d37cad0aca85ae8e4be5a89d34cf"]
["BUDGETS_V3", "BUDGETS", 3, "PROPOSED", "{\"child_budget\":\"OWN\",\"daily_by_purpose\":{\"BRIEF\":4,\"DECISION\":36,\"OUTCOME_REVIEW\":8},\"decision_probe_call_budget\":40,\"final_output_max_bytes\":16384,\"handoff_depth\":1,\"id\":\"BUDGETS_V3\",\"inference_slots\":1,\"jsonl_max_bytes\":2097152,\"kind\":\"BUDGETS\",\"probe_call_budget\":70,\"prompt_max_bytes\":65536,\"queue_expiry_seconds\":600,\"quiet_window_utc\":{\"end\":\"HH:06:00\",\"start\":\"HH:59:30\"},\"rejected_output_retries\":1,\"snapshot_max_bytes\":8192,\"source\":\"ExecPlan 0026 section 5.7\",\"status\":\"PROPOSED\",\"stderr_max_bytes\":262144,\"step_deadline_seconds\":120,\"system_queue_expiry_seconds\":21600,\"templates\":{\"BRIEF_REVIEW_V1\":{\"max_model_steps\":4,\"max_tool_calls\":3,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":600},\"INTENT_REVIEW_V1\":{\"max_model_steps\":4,\"max_tool_calls\":3,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":300},\"MARKET_BRIEF_V1\":{\"max_model_steps\":8,\"max_tool_calls\":6,\"wait_deadline_seconds\":21600,\"workflow_deadline_seconds\":1200},\"OUTCOME_REVIEW_V1\":{\"max_model_steps\":4,\"max_tool_calls\":3,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":600},\"PORTFOLIO_DECISION_V1\":{\"engine_answer_grace_seconds\":60,\"max_drafts\":2,\"max_model_steps\":10,\"max_submissions\":2,\"max_tool_calls\":8,\"review_wait_seconds\":300,\"wait_deadline_seconds\":5040,\"workflow_deadline_seconds\":900},\"PROMOTION_V2\":{\"max_model_steps\":12,\"max_tool_calls\":10,\"wait_deadline_seconds\":0,\"workflow_deadline_seconds\":1200}},\"tool_result_max_bytes\":16384,\"trigger_max_age_seconds\":21600,\"version\":3}", "91aa828f6cba0cde9f0322849ca1d716857cb50656b3ecd041dd90bb1e8916e3"]
["ANALYST_PROMPT_M7_V3", "PROMPT", 3, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"ANALYST_PROMPT_M7_V3\",\"kind\":\"PROMPT\",\"role\":\"ANALYST\",\"sha256\":\"02b16e0e925699fedb08309548a4f9ac6f1a8029617f305bb38390a85d282334\",\"source\":\"services/agent-runner/prompts/m7/analyst.v3.md\",\"status\":\"CODE_OWNED\",\"version\":3}", "e5fa9de7f9fb1d01b1d52f63d40d11d4215b6ad65b635d4c91dde68fe09dd297"]
["COORDINATOR_PROMOTION_PROMPT_M7_V1", "PROMPT", 1, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COORDINATOR_PROMOTION_PROMPT_M7_V1\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"2faa63c6573d54bf4bd48c043435899e2229f6613c1a66bddb44f28e4b370671\",\"source\":\"services/agent-runner/prompts/m7/coordinator-promotion.v1.md\",\"status\":\"CODE_OWNED\",\"version\":1}", "e68b7197289f8449c1d1d5a608da9694a72977cb3abef36761e015e5bac5a49d"]
["COORDINATOR_PROMPT_M7_V2", "PROMPT", 2, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"COORDINATOR_PROMPT_M7_V2\",\"kind\":\"PROMPT\",\"role\":\"COORDINATOR\",\"sha256\":\"868f3068786f3eeceb40f75e0f76caeb4bcb8714001ab77aeddd7ba96be4b818\",\"source\":\"services/agent-runner/prompts/m7/coordinator.v2.md\",\"status\":\"CODE_OWNED\",\"version\":2}", "d91b7ba597443e0eabbce3c6d21af140ed9880f7d1b3f2f9a6d91269b1c48d2d"]
["EVALUATOR_PROMPT_M7_V3", "PROMPT", 3, "CODE_OWNED", "{\"encoding\":\"UTF-8_LF\",\"id\":\"EVALUATOR_PROMPT_M7_V3\",\"kind\":\"PROMPT\",\"role\":\"EVALUATOR\",\"sha256\":\"c01bde3c873111dd6531d6ef963bb336968ecd64a38471c667ca42ab41287077\",\"source\":\"services/agent-runner/prompts/m7/evaluator.v3.md\",\"status\":\"CODE_OWNED\",\"version\":3}", "415527713b92acbd2b001bb5b46c7db46a205a6aa5609f4211b3f3c007d7acdb"]
"""
