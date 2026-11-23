"""M8 update 1: the agents' short check.

Revision ID: 0010_m8_short_check
Revises: 0009_m7_agent_decisions

ExecPlan 0031 sections 4.7 and 9. Additive: no table, column, trigger or grant changes, and nothing is written.
A probe run takes a third suite, ``CHECK``: the short check the agent worker starts by itself after a change of
profile, definitions, policy or runner, after a failed check and after a usage-limit block. Its results carry
the ids ``SC-01`` and ``SC-02``. A check bound to the operating policy writes that policy's
``decision_verifications`` row, so the verification guard accepts a finished ``CHECK`` run beside a
``DECISION`` run, and compares the policy null-safely, since a check without a live policy binds none.
Downgrade refuses any check history, then restores 0009's three checks and its guard.
"""

from alembic import op

revision = "0010_m8_short_check"
down_revision = "0009_m7_agent_decisions"
branch_labels = None
depends_on = None

# (suites, the suite-policy rule, probe ids, the suites the guard accepts, its policy comparison)
BEFORE = ("('CAPABILITY','DECISION')",
          "num_nulls(policy_id, policy_sha256) = CASE WHEN suite = 'DECISION' THEN 0 ELSE 2 END",
          "'^CP-[0-9]{2}$'", "p.suite <> 'DECISION'",
          "p.policy_id <> NEW.policy_id OR p.policy_sha256 <> NEW.policy_sha256")
# A decision suite binds the policy, a capability suite none, a check either (it binds the live policy if any).
AFTER = ("('CAPABILITY','DECISION','CHECK')",
         "CASE suite WHEN 'DECISION' THEN num_nulls(policy_id, policy_sha256) = 0 WHEN 'CAPABILITY' THEN "
         "num_nulls(policy_id, policy_sha256) = 2 ELSE num_nulls(policy_id, policy_sha256) IN (0, 2) END",
         "'^(CP|SC)-[0-9]{2}$'", "p.suite NOT IN ('DECISION','CHECK')",
         "p.policy_id IS DISTINCT FROM NEW.policy_id OR p.policy_sha256 IS DISTINCT FROM NEW.policy_sha256")

GUARD = """
CREATE OR REPLACE FUNCTION asl_m7_verification_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = pg_catalog, public, pg_temp AS $$
DECLARE p record;
BEGIN
    IF current_user <> 'asl_agent' AND NOT asl_is_superuser() THEN
        RAISE EXCEPTION 'decision verifications are written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    SELECT profile_id, profile_sha256, state, suite, policy_id, policy_sha256 INTO p FROM agent_probe_runs
        WHERE id = NEW.probe_run_id;
    IF NOT FOUND OR p.profile_id <> NEW.profile_id OR p.profile_sha256 <> NEW.profile_sha256
            OR {suite} OR {policy}
            OR (NEW.status = 'VERIFIED' AND p.state <> 'PASSED')
            OR (NEW.status = 'FAILED' AND p.state NOT IN ('FAILED','CANCELED')) THEN
        RAISE EXCEPTION 'a decision verification records its finished decision probe run'; END IF;
    IF NOT EXISTS (SELECT 1 FROM agent_read.policy_definitions WHERE id = NEW.policy_id
                   AND sha256 = NEW.policy_sha256 AND kind = 'STRATEGY') THEN
        RAISE EXCEPTION 'a decision verification names an installed operating policy'; END IF;
    RETURN NEW;
END $$;
"""


def _apply(values: tuple[str, ...]) -> None:
    suites, rule, ids, suite, policy = values
    op.execute(f"""
        ALTER TABLE agent_probe_runs DROP CONSTRAINT agent_probe_runs_suite_check,
            ADD CONSTRAINT agent_probe_runs_suite_check CHECK (suite IN {suites}),
            DROP CONSTRAINT agent_probe_runs_suite_policy,
            ADD CONSTRAINT agent_probe_runs_suite_policy CHECK ({rule});
        ALTER TABLE agent_probe_results DROP CONSTRAINT agent_probe_results_probe_id_check,
            ADD CONSTRAINT agent_probe_results_probe_id_check CHECK (probe_id ~ {ids});
    """)
    op.execute(GUARD.format(suite=suite, policy=policy))


def upgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    _apply(AFTER)


def downgrade():
    op.execute("SET LOCAL lock_timeout = '200ms'")
    if op.get_bind().exec_driver_sql(
            "SELECT (SELECT count(*) FROM agent_probe_runs WHERE suite = 'CHECK') "
            "+ (SELECT count(*) FROM agent_probe_results WHERE probe_id !~ '^CP-')").scalar_one():
        raise RuntimeError("M8 check history exists; downgrade refused; fix forward")
    _apply(BEFORE)
