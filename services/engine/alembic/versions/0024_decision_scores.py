"""ExecPlan 0043 update 1: every decision, finished bar and twin entry scored against what the price did next.

Revision ID: 0024_decision_scores
Revises: 0023_twins

ExecPlan 0043 section 4.1. Additive: nothing of the owner's account, its journal, the futures engine, the twins or the
agents' definitions changes, and nothing reads the scores but the API. Each guard resolves names under a fixed search
path.

- ``DECISION_SCORING_V1`` in ``execution_definitions`` (frozen here, checked against the code), its kind
  ``FUTURES_SCORING``.
- ``futures_decision_scores``: one row per subject (a futures decision, a finished 15-minute bar or a twin entry) and
  checkpoint (15, 60, 240 or 1,440 minutes), built in code by the agent identity from stored candles and funding rates
  (``app.agents.decision_scores``). Its canonical text, document and hash agree (0009's content guard); every column
  but its time is generated from its document; it names the stored definition by its hash, describes its subject, is
  written no earlier than its checkpoint (an ``INCOMPLETE`` one no earlier than seven days after it), and never changes.
- ``agent_read`` views: the twins' candidates, and the run's events with the causes a run started with.

Downgrade refuses once any score exists; otherwise it drops the table and restores the definitions' kind check and
0022's run events view.
"""

import hashlib
import json

from alembic import op

revision = "0024_decision_scores"
down_revision = "0023_twins"
branch_labels = None
depends_on = None

SEARCH_PATH = "pg_catalog, public, pg_temp"
# The definition kinds as migration 0023 left them, and the one this migration adds.
DEFINITION_KINDS = ("RISK_POLICY", "STRATEGY", "COST_MODEL", "COST_SCENARIO", "VALUATION_POLICY", "FILTER_POLICY",
                    "EVALUATION_PROTOCOL", "BASELINE_SET", "FUTURES_POLICY", "FUTURES_COST", "FUTURES_TWINS")
KIND_ADDED = ("FUTURES_SCORING",)

# The frozen definition: ``python -m app.futures.scoring`` prints it; tests/test_m11_scores_db.py checks it.
SCORING_SEED_LINES = r"""
["DECISION_SCORING_V1", "FUTURES_SCORING", 1, "PROPOSED", "{\"checkpoints_minutes\":[15,60,240,1440],\"conditions\":{\"at\":\"THE_REFERENCE_WITH_THE_TRADER'S_OWN_FEATURES\",\"funding_rate\":\"THE_RATE_THE_NEWEST_MARK_ANNOUNCED_WITHIN_60_S_ELSE_UNKNOWN\",\"funding_sign\":[\"POSITIVE\",\"NEGATIVE\",\"ZERO\",\"UNKNOWN\"],\"hours_utc\":[\"00-08\",\"08-16\",\"16-24\"],\"trend_1h\":[\"UP\",\"DOWN\",\"FLAT\",\"UNKNOWN\"]},\"cost\":\"FUTURES_COST_V1\",\"headline_minutes\":60,\"held_position\":{\"against\":\"EXITING_AT_THE_REFERENCE\",\"band\":\"ONE_EXIT'S_COST_THE_TAKER_FEE_PLUS_THE_SLIPPAGE_SCENARIO_OF_THE_REFERENCE\",\"closed_before\":\"COUNTS_AS_FLAT\",\"hold\":\"THE_POSITION'S_OWN_STOP_TAKE_PROFIT_AND_TIME_LIMIT_AS_THEY_STOOD_AT_THE_DECISION\",\"measure\":\"PER_UNIT_WITH_EACH_EXIT'S_SLIPPAGE_AND_FEE_AND_THE_FUNDING_THE_HOLD_CROSSED\",\"time_limit\":\"AT_THE_OPEN_OF_THE_FIRST_MINUTE_AT_OR_AFTER_IT\",\"when\":\"A_DECISION_THAT_SAW_A_POSITION_STILL_OPEN_AT_ITS_TIME\"},\"id\":\"DECISION_SCORING_V1\",\"kind\":\"FUTURES_SCORING\",\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; MODELED_ON_1M_CANDLES; NOTHING_IS_CHANGED_BY_A_SCORE\",\"labels\":{\"BAR\":\"WHICH_TEST_TRADE_PAID\",\"ENTER_LONG\":{\"BOTH_PAID\":\"RIGHT_SIDE\",\"LONG_PAID\":\"RIGHT_SIDE\",\"NEITHER_PAID\":\"FEES_ONLY\",\"SHORT_PAID\":\"WRONG_SIDE\"},\"ENTER_SHORT\":{\"BOTH_PAID\":\"RIGHT_SIDE\",\"LONG_PAID\":\"WRONG_SIDE\",\"NEITHER_PAID\":\"FEES_ONLY\",\"SHORT_PAID\":\"RIGHT_SIDE\"},\"EXIT\":{\"AGAINST\":\"GOOD_EXIT\",\"NEITHER\":\"NEUTRAL_EXIT\",\"WITH\":\"EARLY_EXIT\"},\"TIGHTEN_STOP\":{\"AT_LEAST_THE_OLD_STOP'S\":\"SAVED\",\"NEW_STOP_NOT_TOUCHED\":\"NOT_HIT\",\"REFUSED\":\"NOT_APPLIED\",\"WORSE\":\"SHAKEN_OUT\"},\"chop\":\"NEITHER_PAID_WITH_BOTH_TEST_TRADES_STOPPED\",\"flat_wait\":{\"BOTH_PAID\":\"EITHER_WAY\",\"LONG_PAID\":\"MISSED_LONG\",\"NEITHER_PAID\":\"NOTHING_TO_CATCH\",\"SHORT_PAID\":\"MISSED_SHORT\"},\"in_position_wait\":{\"AGAINST\":\"HELD_INTO_LOSS\",\"NEITHER\":\"HOLD_FLAT\",\"WITH\":\"GOOD_HOLD\"},\"refused\":\"KEEPS_ITS_LABEL_WITH_EXECUTED_FALSE\",\"set_by\":\"CODE_ONLY\",\"waits\":\"HOLD_OR_ABSTAIN_AND_AN_EXIT_OR_TIGHTENING_WHOSE_POSITION_CLOSED_BEFORE_IT\",\"with_or_against\":\"THE_HOLD'S_ADVANTAGE_OVER_EXITING_BEYOND_THE_BAND\"},\"missing\":{\"incomplete_after_days\":7,\"never\":\"FILLED_OR_ESTIMATED\",\"scorer_failed\":\"TRIED_AGAIN_EVERY_5_MINUTES_THEN_INCOMPLETE_AS_SCORE_FAILED\",\"unanswered\":\"THE_POSITION_THE_DECISION_SAW_AND_EXECUTED_UNKNOWN\",\"waits\":\"A_MISSING_CANDLE_OR_FUNDING_RATE_AN_UNANSWERED_DECISION_OR_AN_UNFINISHED_JOB\"},\"path\":\"THE_FINAL_1M_CANDLES_FROM_THE_SUBJECT'S_MINUTE_TO_THE_CHECKPOINT_ONE_A_MINUTE\",\"policy\":\"FUTURES_POLICY_V1\",\"records\":{\"document_max_bytes\":8192,\"identity\":\"asl_agent\",\"immutable\":true,\"subjects_per_pass\":20,\"table\":\"futures_decision_scores\"},\"reference\":\"THE_CLOSE_OF_THE_FINAL_1M_CANDLE_ENDING_AT_THE_START_OF_THE_SUBJECT'S_MINUTE\",\"scorecard\":{\"as_of\":\"ONLY_THE_SCORES_RECORDED_BY_THEN\",\"atr_thirds\":\"OF_THE_WINDOW'S_SCORED_BARS\",\"by\":[\"trend_1h\",\"atr_third\",\"hours_utc\",\"funding_sign\",\"reason_code\",\"uncertainty_level\"],\"missed\":\"BARS_WITHOUT_A_DECISION_WHILE_THE_TRADER_WAS_EXPECTED_READ_AS_WAITS\",\"too_few_below\":30,\"windows\":[\"24H\",\"7D\",\"ALL\"]},\"source\":\"ExecPlan 0043 section 4, approved by the owner on 2026-10-26\",\"status\":\"PROPOSED\",\"subjects\":{\"BAR\":\"EVERY_FINISHED_15M_BAR_SINCE_THE_FIRST_FUTURES_RUN_STARTED_FROM_ITS_CLOSE\",\"DECISION\":\"EVERY_FUTURES_DECISION_FROM_ITS_RECORDED_TIME_ONCE_THE_ENGINE_ANSWERED_IT\",\"TWIN_ENTRY\":\"EVERY_TWIN_CANDIDATE_FROM_ITS_TIME\",\"bar_decision\":\"THE_DECISION_OF_THE_FIRST_TRADER_JOB_STARTED_FROM_THE_CLOSE_UNTIL_THE_NEXT_CLOSE\",\"bar_expected\":\"THE_RUN_RUNNING_WITHOUT_A_CAUSE_OR_A_POSITION_OPEN_AT_THE_CLOSE\"},\"test_trades\":{\"atr\":\"THE_POLICY'S_15M_WILDER_ATR_AT_THE_REFERENCE_TO_0.00000001\",\"both_touched\":\"THE_STOP\",\"entry\":\"THE_REFERENCE_WITH_THE_SLIPPAGE_SCENARIO_AGAINST_THE_SIDE_AND_THE_TAKER_FEE\",\"exit\":\"THE_STOP_THE_TARGET_OR_THE_CHECKPOINT'S_CLOSE_WITH_THE_SLIPPAGE_SCENARIO_AGAINST_IT_AND_THE_TAKER_FEE\",\"funding\":\"EACH_FUNDING_TIME_AFTER_THE_ENTRY_AND_AT_OR_BEFORE_THE_EXIT_AT_ITS_SETTLED_RATE_ON_ITS_MARK\",\"funding_mark\":\"THE_SETTLED_RATE'S_MARK_ELSE_THE_1M_CLOSE_ENDING_AT_IT\",\"funding_times\":\"EVERY_8_HOURS_FROM_00_UTC_EACH_NEEDING_ITS_SETTLED_RATE_AND_ANY_OTHER_SETTLED_RATE'S_TIME\",\"gap\":\"A_MINUTE_OPENING_BEYOND_THE_STOP_OR_THE_TARGET_ENDS_AT_ITS_OPEN\",\"levels\":\"TO_0.00000001_THE_STOP_AWAY_FROM_THE_ENTRY_THE_TARGET_TOWARD_IT; A_MEASURING_STICK_NOT_AN_ORDER\",\"leverage\":\"1\",\"liquidation\":\"NOT_MODELED_THE_POLICY_KEEPS_EVERY_STOP_INSIDE_IT\",\"paid\":\"NET_ABOVE_ZERO\",\"quantity\":\"1\",\"r\":\"NET_OVER_THE_LOSS_AT_THE_STOP_WITH_BOTH_FEES_AND_SLIPPAGE\",\"sides\":[\"LONG\",\"SHORT\"],\"stop_atr_multiple\":\"1.5\",\"target_stop_multiple\":\"2\"},\"version\":1}", "b61dae9fcb5a84df9bad5d6b57f369f3a4431c37e1e8ba4e33656af77bd09def"]
"""


def _quoted(values):
    return "(" + ",".join("'" + value + "'" for value in values) + ")"


def seed_rows():
    rows = []
    for line in SCORING_SEED_LINES.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind not in KIND_ADDED:
            raise RuntimeError("frozen scoring definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


LABELS = ("LONG_PAID", "SHORT_PAID", "BOTH_PAID", "NEITHER_PAID", "MISSED_LONG", "MISSED_SHORT", "EITHER_WAY",
          "NOTHING_TO_CATCH", "RIGHT_SIDE", "WRONG_SIDE", "FEES_ONLY", "GOOD_HOLD", "HELD_INTO_LOSS", "HOLD_FLAT",
          "EARLY_EXIT", "GOOD_EXIT", "NEUTRAL_EXIT", "SAVED", "SHAKEN_OUT", "NOT_HIT", "NOT_APPLIED")
PAID = LABELS[:4]

# Every column but the subject's time is its document's value, so the two cannot disagree; the guard checks the
# time against the document and the document against the stored records.
TABLE_SQL = """
CREATE TABLE futures_decision_scores (
    id uuid PRIMARY KEY,
    subject_at timestamptz NOT NULL,
    canonical text NOT NULL CHECK (octet_length(canonical) <= 8192),
    document jsonb NOT NULL,
    sha256 varchar(64) NOT NULL CHECK (sha256 ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    scoring_sha256 text GENERATED ALWAYS AS (document->'scoring'->>'sha256') STORED NOT NULL,
    subject text GENERATED ALWAYS AS (document->'subject'->>'kind') STORED NOT NULL
        CHECK (subject IN ('DECISION','BAR','TWIN_ENTRY')),
    subject_key text GENERATED ALWAYS AS (document->'subject'->>'key') STORED NOT NULL,
    minutes integer GENERATED ALWAYS AS (CAST(document->>'minutes' AS integer)) STORED NOT NULL
        CHECK (minutes IN (15, 60, 240, 1440)),
    decision_id uuid GENERATED ALWAYS AS (CAST(document->'subject'->>'decision_id' AS uuid)) STORED
        REFERENCES futures_decisions(id),
    candidate_id uuid GENERATED ALWAYS AS (CAST(document->'subject'->>'candidate_id' AS uuid)) STORED
        REFERENCES futures_twin_candidates(id),
    bar_open_ms bigint GENERATED ALWAYS AS (CAST(document->'subject'->>'bar_open_ms' AS bigint)) STORED
        CHECK (bar_open_ms >= 0 AND bar_open_ms % 900000 = 0),
    trigger text GENERATED ALWAYS AS (document->'subject'->>'trigger') STORED
        CHECK (trigger IN ('BAR','FILL','SHARP_MOVE')),
    action text GENERATED ALWAYS AS (document->'subject'->>'action') STORED
        CHECK (action IN ('ENTER_LONG','ENTER_SHORT','EXIT','TIGHTEN_STOP','HOLD','ABSTAIN')),
    before text GENERATED ALWAYS AS (document->'subject'->>'before') STORED NOT NULL
        CHECK (before IN ('FLAT','LONG','SHORT')),
    executed boolean GENERATED ALWAYS AS (CAST(document->'subject'->>'executed' AS boolean)) STORED,
    decided boolean GENERATED ALWAYS AS (CAST(document->'subject'->>'decided' AS boolean)) STORED,
    expected boolean GENERATED ALWAYS AS (CAST(document->'subject'->>'expected' AS boolean)) STORED,
    why text GENERATED ALWAYS AS (document->'subject'->>'why') STORED,
    twin text GENERATED ALWAYS AS (document->'subject'->>'twin') STORED
        CHECK (twin IN ('HOLD','TREND','TREND_GATED')),
    reason_code text GENERATED ALWAYS AS (document->'subject'->>'reason_code') STORED,
    uncertainty_level text GENERATED ALWAYS AS (document->'subject'->>'uncertainty_level') STORED,
    state text GENERATED ALWAYS AS (document->>'state') STORED NOT NULL CHECK (state IN ('SCORED','INCOMPLETE')),
    reason text GENERATED ALWAYS AS (document->>'reason') STORED
        CHECK (reason IN ('MISSING_CANDLES','MISSING_FUNDING','NO_ATR','NO_ANSWER','JOB_UNFINISHED','SCORE_FAILED')),
    label text GENERATED ALWAYS AS (document->>'label') STORED CHECK (label IN {labels}),
    paid text GENERATED ALWAYS AS (document->>'paid') STORED CHECK (paid IN {paid}),
    move_percent numeric GENERATED ALWAYS AS (CAST(document->'path'->>'move_percent' AS numeric)) STORED,
    long_net_percent numeric GENERATED ALWAYS AS (CAST(document->'long'->>'net_percent' AS numeric)) STORED,
    short_net_percent numeric GENERATED ALWAYS AS (CAST(document->'short'->>'net_percent' AS numeric)) STORED,
    advantage_percent numeric GENERATED ALWAYS AS (CAST(document->'held'->>'advantage_percent' AS numeric)) STORED,
    atr_percent numeric GENERATED ALWAYS AS (CAST(document->'conditions'->>'atr_percent' AS numeric)) STORED,
    trend_1h text GENERATED ALWAYS AS (document->'conditions'->>'trend_1h') STORED
        CHECK (trend_1h IN ('UP','DOWN','FLAT','UNKNOWN')),
    hours_utc text GENERATED ALWAYS AS (document->'conditions'->>'hours_utc') STORED
        CHECK (hours_utc IN ('00-08','08-16','16-24')),
    funding_sign text GENERATED ALWAYS AS (document->'conditions'->>'funding_sign') STORED
        CHECK (funding_sign IN ('POSITIVE','NEGATIVE','ZERO','UNKNOWN')),
    UNIQUE (subject, subject_key, minutes),
    CONSTRAINT futures_decision_score_state CHECK (CASE state
        WHEN 'SCORED' THEN label IS NOT NULL AND reason IS NULL AND paid IS NOT NULL
        ELSE label IS NULL AND reason IS NOT NULL END),
    CONSTRAINT futures_decision_score_subject CHECK (CASE subject
        WHEN 'DECISION' THEN decision_id IS NOT NULL AND action IS NOT NULL
            AND (executed IS NOT NULL OR state = 'INCOMPLETE') AND candidate_id IS NULL AND (label IS NULL OR label NOT IN {paid})
        WHEN 'BAR' THEN bar_open_ms IS NOT NULL AND decided IS NOT NULL AND expected IS NOT NULL
            AND candidate_id IS NULL AND (label IS NULL OR label IN {paid})
        ELSE candidate_id IS NOT NULL AND twin IS NOT NULL AND action IN ('ENTER_LONG','ENTER_SHORT')
            AND executed IS NOT NULL AND decision_id IS NULL AND (label IS NULL OR label IN ('RIGHT_SIDE','WRONG_SIDE','FEES_ONLY'))
        END)
);
CREATE INDEX futures_decision_scores_at ON futures_decision_scores (subject_at);
CREATE INDEX futures_decision_scores_decision ON futures_decision_scores (decision_id) WHERE decision_id IS NOT NULL;
CREATE INDEX futures_decision_scores_bar ON futures_decision_scores (bar_open_ms) WHERE bar_open_ms IS NOT NULL;
"""

GUARD_SQL = """
-- A score comes only from the agent identity, names the stored scoring definition by its hash, has its subject's
-- time and describes that subject's stored record, and is written no earlier than its checkpoint (an INCOMPLETE one
-- no earlier than the definition's seven days after it).
CREATE FUNCTION asl_decision_score_guard() RETURNS trigger LANGUAGE plpgsql SET search_path = {path} AS $$
DECLARE d jsonb := NEW.document; s jsonb := NEW.document->'subject'; stored jsonb; r record;
        minute_ms bigint; checkpoint_at timestamptz;
BEGIN
    IF asl_is_superuser() THEN RETURN NEW; END IF;
    IF current_user <> 'asl_agent' THEN RAISE EXCEPTION 'a decision score is written by the agent worker'; END IF;
    NEW.created_at := clock_timestamp();
    stored := asl_m8_execution_definition(d->'scoring'->>'id', d->'scoring'->>'sha256');
    IF stored IS NULL OR stored->>'kind' <> 'FUTURES_SCORING' OR d->>'schema' IS DISTINCT FROM 'DECISION_SCORE_V1'
            OR d->>'score_id' IS DISTINCT FROM NEW.id::text THEN
        RAISE EXCEPTION 'a decision score names its stored scoring definition'; END IF;
    IF CAST(s->>'at' AS timestamptz) IS DISTINCT FROM NEW.subject_at THEN
        RAISE EXCEPTION 'a decision score''s time is its subject''s'; END IF;
    minute_ms := floor(extract(epoch FROM NEW.subject_at) * 1000 / 60000)::bigint * 60000;
    IF CAST(s->>'minute_ms' AS bigint) IS DISTINCT FROM minute_ms
            OR CAST(d->>'checkpoint_ms' AS bigint) IS DISTINCT FROM minute_ms + CAST(d->>'minutes' AS bigint) * 60000 THEN
        RAISE EXCEPTION 'a decision score''s checkpoint follows its subject''s minute'; END IF;
    checkpoint_at := to_timestamp(CAST(d->>'checkpoint_ms' AS bigint) / 1000.0);
    IF checkpoint_at > NEW.created_at
            OR (d->>'state' = 'INCOMPLETE' AND checkpoint_at + interval '7 days' > NEW.created_at) THEN
        RAISE EXCEPTION 'a decision score is written after its checkpoint, an incomplete one a week after'; END IF;
    IF s->>'kind' = 'DECISION' THEN
        SELECT created_at, action, trigger, bar_open_ms INTO r FROM futures_decisions
            WHERE id = CAST(s->>'decision_id' AS uuid);
        IF NOT FOUND OR s->>'key' IS DISTINCT FROM s->>'decision_id' OR r.created_at <> NEW.subject_at
                OR r.action IS DISTINCT FROM s->>'action' OR r.trigger IS DISTINCT FROM s->>'trigger'
                OR r.bar_open_ms IS DISTINCT FROM CAST(s->>'bar_open_ms' AS bigint) THEN
            RAISE EXCEPTION 'a decision''s score describes its stored decision'; END IF;
        IF d->>'state' = 'SCORED' AND NOT EXISTS (SELECT 1 FROM agent_read.futures_answers
                WHERE decision_id = CAST(s->>'decision_id' AS uuid)) THEN
            RAISE EXCEPTION 'a decision is scored once the engine answered it'; END IF;
    ELSIF s->>'kind' = 'BAR' THEN
        IF s->>'key' IS DISTINCT FROM s->>'bar_open_ms' OR NEW.subject_at
                <> to_timestamp((CAST(s->>'bar_open_ms' AS bigint) + 900000) / 1000.0) THEN
            RAISE EXCEPTION 'a bar''s score is at its close'; END IF;
        IF s->>'decision_id' IS NOT NULL THEN
            SELECT created_at, action INTO r FROM futures_decisions WHERE id = CAST(s->>'decision_id' AS uuid);
            IF NOT FOUND OR r.created_at < NEW.subject_at OR r.action IS DISTINCT FROM s->>'action' THEN
                RAISE EXCEPTION 'a bar''s decision is a stored decision after its close'; END IF;
        END IF;
    ELSE
        SELECT at, side, bar_open_ms, twin, outcome INTO r FROM agent_read.futures_twin_candidates
            WHERE id = CAST(s->>'candidate_id' AS uuid);
        IF NOT FOUND OR s->>'key' IS DISTINCT FROM s->>'candidate_id' OR r.at <> NEW.subject_at
                OR 'ENTER_' || r.side IS DISTINCT FROM s->>'action' OR r.twin IS DISTINCT FROM s->>'twin'
                OR r.bar_open_ms IS DISTINCT FROM CAST(s->>'bar_open_ms' AS bigint)
                OR (r.outcome = 'FILLED') IS DISTINCT FROM CAST(s->>'executed' AS boolean) THEN
            RAISE EXCEPTION 'a twin entry''s score describes its stored candidate'; END IF;
    END IF;
    RETURN NEW;
END $$;

CREATE TRIGGER futures_decision_scores_content BEFORE INSERT ON futures_decision_scores
    FOR EACH ROW EXECUTE FUNCTION asl_m7_content_guard();
CREATE TRIGGER futures_decision_scores_guard BEFORE INSERT ON futures_decision_scores
    FOR EACH ROW EXECUTE FUNCTION asl_decision_score_guard();
CREATE TRIGGER futures_decision_scores_immutable BEFORE UPDATE OR DELETE ON futures_decision_scores
    FOR EACH ROW EXECUTE FUNCTION asl_immutable();
"""

# 0022's run events view gains the causes a run started with, at its end; downgrade makes 0022's again.
RUN_EVENTS_VIEW = """
CREATE OR REPLACE VIEW agent_read.futures_run_events WITH (security_barrier = true) AS
    SELECT run_id, kind, at, detail->>'cause' AS cause{columns} FROM futures_run_events;
"""
RUN_EVENTS_COLUMNS = ", detail->'causes' AS causes"
CANDIDATES_VIEW = """
CREATE VIEW agent_read.futures_twin_candidates WITH (security_barrier = true) AS
    SELECT c.id, t.twin, c.bar_open_ms, c.rule, c.side, c.gate, c.funding_filter, c.outcome, c.codes, c.at
    FROM futures_twin_candidates c JOIN futures_twins t ON t.id = c.twin_id;
"""


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               "ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN "
               f"{_quoted((*DEFINITION_KINDS, *KIND_ADDED))})")
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})
    op.execute(RUN_EVENTS_VIEW.replace("{columns}", RUN_EVENTS_COLUMNS))
    op.execute(CANDIDATES_VIEW)
    op.execute(TABLE_SQL.replace("{labels}", _quoted(LABELS)).replace("{paid}", _quoted(PAID)))
    op.execute(GUARD_SQL.replace("{path}", SEARCH_PATH))
    op.execute("GRANT SELECT ON agent_read.futures_twin_candidates TO asl_agent")
    op.execute("GRANT SELECT, INSERT ON futures_decision_scores TO asl_agent")
    op.execute("GRANT SELECT ON futures_decision_scores TO asl_api")


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # No score can be stored between the count and the drop.
    op.execute("LOCK TABLE futures_decision_scores IN ACCESS EXCLUSIVE MODE")
    if bind.exec_driver_sql("SELECT count(*) FROM futures_decision_scores").scalar_one():
        raise RuntimeError("decision scores exist; downgrade refused; fix forward")
    op.execute("DROP TABLE futures_decision_scores")
    op.execute("DROP FUNCTION asl_decision_score_guard()")
    op.execute("DROP VIEW agent_read.futures_twin_candidates")
    # A view loses a column only by being made again; 0022's grant is restored with it.
    op.execute("DROP VIEW agent_read.futures_run_events")
    op.execute(RUN_EVENTS_VIEW.replace("{columns}", "").replace("CREATE OR REPLACE VIEW", "CREATE VIEW"))
    op.execute("GRANT SELECT ON agent_read.futures_run_events TO asl_agent")
    # The definition store is immutable even for the migration role: relax only its trigger, inside this
    # transaction, and delete only the frozen row, which nothing names any more.
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("scoring definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
    op.execute("ALTER TABLE execution_definitions DROP CONSTRAINT execution_definitions_kind_check, "
               f"ADD CONSTRAINT execution_definitions_kind_check CHECK (kind IN {_quoted(DEFINITION_KINDS)})")
