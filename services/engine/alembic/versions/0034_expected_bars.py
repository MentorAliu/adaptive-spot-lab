"""ExecPlan 0054: the scorer expects a decision at the schedule's moments (``DECISION_SCORING_V2``).

Revision ID: 0034_expected_bars
Revises: 0033_event_trader

ExecPlan 0054 section 4. Additive: one row in ``execution_definitions``, ``DECISION_SCORING_V2`` (kind
``FUTURES_SCORING``, allowed by 0024's kind check), frozen here with its SHA-256 and checked against the code
(``app.futures.scoring``; ``python -m app.futures.scoring`` prints the row). It is V1 with one change: a 15-minute
bar is expected to carry a decision only when its close is one of generation 14's four-hour moments and the run was
running without a cause or a position was open; V1 expected every such bar, which read about 88 bars a day as
missed under the four-hour schedule (ExecPlan 0053 section 11). Nothing else changes: no table, no guard, no view;
the scores already stored name V1 and stay as they are, and the scorer stores every new score under V2 (0024's
guard accepts any stored ``FUTURES_SCORING`` row).

Downgrade refuses once any score names V2 ("fix forward"); otherwise it removes the row, with the definition store's
immutability trigger relaxed inside the transaction as 0024 does.
"""

import hashlib
import json

from alembic import op

revision = "0034_expected_bars"
down_revision = "0033_event_trader"
branch_labels = None
depends_on = None

KIND = "FUTURES_SCORING"

# Generated from app.futures.scoring (python -m app.futures.scoring); tests/test_m11_scores_unit.py compares.
SCORING_SEED_LINES_V2 = r"""
["DECISION_SCORING_V2", "FUTURES_SCORING", 2, "PROPOSED", "{\"carried\":{\"changed\":[\"subjects.bar_expected\",\"subjects.bar_moments\",\"scorecard.missed\"],\"else\":\"UNCHANGED; EVERY_SCORE_RECORDED_UNDER_V1_STAYS_AS_RECORDED_NAMING_V1\",\"from\":\"DECISION_SCORING_V1\"},\"checkpoints_minutes\":[15,60,240,1440],\"conditions\":{\"at\":\"THE_REFERENCE_WITH_THE_TRADER'S_OWN_FEATURES\",\"funding_rate\":\"THE_RATE_THE_NEWEST_MARK_ANNOUNCED_WITHIN_60_S_ELSE_UNKNOWN\",\"funding_sign\":[\"POSITIVE\",\"NEGATIVE\",\"ZERO\",\"UNKNOWN\"],\"hours_utc\":[\"00-08\",\"08-16\",\"16-24\"],\"trend_1h\":[\"UP\",\"DOWN\",\"FLAT\",\"UNKNOWN\"]},\"cost\":\"FUTURES_COST_V1\",\"headline_minutes\":60,\"held_position\":{\"against\":\"EXITING_AT_THE_REFERENCE\",\"band\":\"ONE_EXIT'S_COST_THE_TAKER_FEE_PLUS_THE_SLIPPAGE_SCENARIO_OF_THE_REFERENCE\",\"closed_before\":\"COUNTS_AS_FLAT\",\"hold\":\"THE_POSITION'S_OWN_STOP_TAKE_PROFIT_AND_TIME_LIMIT_AS_THEY_STOOD_AT_THE_DECISION\",\"measure\":\"PER_UNIT_WITH_EACH_EXIT'S_SLIPPAGE_AND_FEE_AND_THE_FUNDING_THE_HOLD_CROSSED\",\"time_limit\":\"AT_THE_OPEN_OF_THE_FIRST_MINUTE_AT_OR_AFTER_IT\",\"when\":\"A_DECISION_THAT_SAW_A_POSITION_STILL_OPEN_AT_ITS_TIME\"},\"id\":\"DECISION_SCORING_V2\",\"kind\":\"FUTURES_SCORING\",\"label\":\"HINDSIGHT_COMPUTED_IN_CODE; MODELED_ON_1M_CANDLES; NOTHING_IS_CHANGED_BY_A_SCORE\",\"labels\":{\"BAR\":\"WHICH_TEST_TRADE_PAID\",\"ENTER_LONG\":{\"BOTH_PAID\":\"RIGHT_SIDE\",\"LONG_PAID\":\"RIGHT_SIDE\",\"NEITHER_PAID\":\"FEES_ONLY\",\"SHORT_PAID\":\"WRONG_SIDE\"},\"ENTER_SHORT\":{\"BOTH_PAID\":\"RIGHT_SIDE\",\"LONG_PAID\":\"WRONG_SIDE\",\"NEITHER_PAID\":\"FEES_ONLY\",\"SHORT_PAID\":\"RIGHT_SIDE\"},\"EXIT\":{\"AGAINST\":\"GOOD_EXIT\",\"NEITHER\":\"NEUTRAL_EXIT\",\"WITH\":\"EARLY_EXIT\"},\"TIGHTEN_STOP\":{\"AT_LEAST_THE_OLD_STOP'S\":\"SAVED\",\"NEW_STOP_NOT_TOUCHED\":\"NOT_HIT\",\"REFUSED\":\"NOT_APPLIED\",\"WORSE\":\"SHAKEN_OUT\"},\"chop\":\"NEITHER_PAID_WITH_BOTH_TEST_TRADES_STOPPED\",\"flat_wait\":{\"BOTH_PAID\":\"EITHER_WAY\",\"LONG_PAID\":\"MISSED_LONG\",\"NEITHER_PAID\":\"NOTHING_TO_CATCH\",\"SHORT_PAID\":\"MISSED_SHORT\"},\"in_position_wait\":{\"AGAINST\":\"HELD_INTO_LOSS\",\"NEITHER\":\"HOLD_FLAT\",\"WITH\":\"GOOD_HOLD\"},\"refused\":\"KEEPS_ITS_LABEL_WITH_EXECUTED_FALSE\",\"set_by\":\"CODE_ONLY\",\"waits\":\"HOLD_OR_ABSTAIN_AND_AN_EXIT_OR_TIGHTENING_WHOSE_POSITION_CLOSED_BEFORE_IT\",\"with_or_against\":\"THE_HOLD'S_ADVANTAGE_OVER_EXITING_BEYOND_THE_BAND\"},\"missing\":{\"incomplete_after_days\":7,\"never\":\"FILLED_OR_ESTIMATED\",\"scorer_failed\":\"TRIED_AGAIN_EVERY_5_MINUTES_THEN_INCOMPLETE_AS_SCORE_FAILED\",\"unanswered\":\"THE_POSITION_THE_DECISION_SAW_AND_EXECUTED_UNKNOWN\",\"waits\":\"A_MISSING_CANDLE_OR_FUNDING_RATE_AN_UNANSWERED_DECISION_OR_AN_UNFINISHED_JOB\"},\"path\":\"THE_FINAL_1M_CANDLES_FROM_THE_SUBJECT'S_MINUTE_TO_THE_CHECKPOINT_ONE_A_MINUTE\",\"policy\":\"FUTURES_POLICY_V1\",\"records\":{\"document_max_bytes\":8192,\"identity\":\"asl_agent\",\"immutable\":true,\"subjects_per_pass\":20,\"table\":\"futures_decision_scores\"},\"reference\":\"THE_CLOSE_OF_THE_FINAL_1M_CANDLE_ENDING_AT_THE_START_OF_THE_SUBJECT'S_MINUTE\",\"scorecard\":{\"as_of\":\"ONLY_THE_SCORES_RECORDED_BY_THEN\",\"atr_thirds\":\"OF_THE_WINDOW'S_SCORED_BARS\",\"by\":[\"trend_1h\",\"atr_third\",\"hours_utc\",\"funding_sign\",\"reason_code\",\"uncertainty_level\"],\"missed\":\"SCHEDULED_BARS_WITHOUT_A_DECISION_WHILE_THE_TRADER_WAS_EXPECTED_READ_AS_WAITS\",\"too_few_below\":30,\"windows\":[\"24H\",\"7D\",\"ALL\"]},\"source\":\"ExecPlan 0043 section 4, approved by the owner on 2026-10-26; ExecPlan 0054 section 4 (the expected bars), approved by the owner on 2026-11-03\",\"status\":\"PROPOSED\",\"subjects\":{\"BAR\":\"EVERY_FINISHED_15M_BAR_SINCE_THE_FIRST_FUTURES_RUN_STARTED_FROM_ITS_CLOSE\",\"DECISION\":\"EVERY_FUTURES_DECISION_FROM_ITS_RECORDED_TIME_ONCE_THE_ENGINE_ANSWERED_IT\",\"TWIN_ENTRY\":\"EVERY_TWIN_CANDIDATE_FROM_ITS_TIME\",\"bar_decision\":\"THE_DECISION_OF_THE_FIRST_TRADER_JOB_STARTED_FROM_THE_CLOSE_UNTIL_THE_NEXT_CLOSE\",\"bar_expected\":\"THE_RUN_RUNNING_WITHOUT_A_CAUSE_OR_A_POSITION_OPEN_AT_A_CLOSE_THAT_IS_A_MOMENT_OF_THE_INSTALLED_TRADER'S_SCHEDULE\",\"bar_moments\":\"EVERY_4H_AND_EVENTS_V1: THE_4H_BOUNDARIES_FROM_00_UTC; AN_EVENT'S_BAR_IS_DECIDED_NOT_EXPECTED; A_MOMENT_DECIDED_IN_A_LATER_BAR_LEAVES_ITS_OWN_BAR_MISSED\"},\"test_trades\":{\"atr\":\"THE_POLICY'S_15M_WILDER_ATR_AT_THE_REFERENCE_TO_0.00000001\",\"both_touched\":\"THE_STOP\",\"entry\":\"THE_REFERENCE_WITH_THE_SLIPPAGE_SCENARIO_AGAINST_THE_SIDE_AND_THE_TAKER_FEE\",\"exit\":\"THE_STOP_THE_TARGET_OR_THE_CHECKPOINT'S_CLOSE_WITH_THE_SLIPPAGE_SCENARIO_AGAINST_IT_AND_THE_TAKER_FEE\",\"funding\":\"EACH_FUNDING_TIME_AFTER_THE_ENTRY_AND_AT_OR_BEFORE_THE_EXIT_AT_ITS_SETTLED_RATE_ON_ITS_MARK\",\"funding_mark\":\"THE_SETTLED_RATE'S_MARK_ELSE_THE_1M_CLOSE_ENDING_AT_IT\",\"funding_times\":\"EVERY_8_HOURS_FROM_00_UTC_EACH_NEEDING_ITS_SETTLED_RATE_AND_ANY_OTHER_SETTLED_RATE'S_TIME\",\"gap\":\"A_MINUTE_OPENING_BEYOND_THE_STOP_OR_THE_TARGET_ENDS_AT_ITS_OPEN\",\"levels\":\"TO_0.00000001_THE_STOP_AWAY_FROM_THE_ENTRY_THE_TARGET_TOWARD_IT; A_MEASURING_STICK_NOT_AN_ORDER\",\"leverage\":\"1\",\"liquidation\":\"NOT_MODELED_THE_POLICY_KEEPS_EVERY_STOP_INSIDE_IT\",\"paid\":\"NET_ABOVE_ZERO\",\"quantity\":\"1\",\"r\":\"NET_OVER_THE_LOSS_AT_THE_STOP_WITH_BOTH_FEES_AND_SLIPPAGE\",\"sides\":[\"LONG\",\"SHORT\"],\"stop_atr_multiple\":\"1.5\",\"target_stop_multiple\":\"2\"},\"version\":2}", "e2809f2287c0c786cc6d1f8d8a744d837554fd60579dd6a6f171424a638cbfd7"]
"""


def seed_rows():
    """The frozen V2 row, checked against its own hash."""
    rows = []
    for line in SCORING_SEED_LINES_V2.strip().splitlines():
        identity, kind, version, status, canonical, sha256 = json.loads(line)
        if hashlib.sha256(canonical.encode()).hexdigest() != sha256 or kind != KIND:
            raise RuntimeError("frozen scoring definition is inconsistent")
        rows.append({"id": identity, "kind": kind, "version": version, "status": status,
                     "canonical": canonical, "sha256": sha256})
    return rows


def upgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    for row in seed_rows():
        bind.exec_driver_sql(
            "INSERT INTO execution_definitions (id, kind, version, status, definition, canonical, sha256) "
            "VALUES (%(id)s, %(kind)s, %(version)s, %(status)s, CAST(%(definition)s AS jsonb), %(canonical)s, "
            "%(sha256)s)", {**row, "definition": row["canonical"]})


def downgrade() -> None:
    op.execute("SET LOCAL lock_timeout = '10s'")
    bind = op.get_bind()
    # No score can be stored between the count and the delete.
    op.execute("LOCK TABLE futures_decision_scores IN ACCESS EXCLUSIVE MODE")
    for row in seed_rows():
        if bind.exec_driver_sql("SELECT count(*) FROM futures_decision_scores WHERE scoring_sha256 = %(sha256)s",
                                row).scalar_one():
            raise RuntimeError("scores under DECISION_SCORING_V2 exist; downgrade refused; fix forward")
    op.execute("ALTER TABLE execution_definitions DISABLE TRIGGER execution_definitions_immutable")
    for row in seed_rows():
        if bind.exec_driver_sql("DELETE FROM execution_definitions WHERE id = %(id)s AND sha256 = %(sha256)s",
                                row).rowcount != 1:
            raise RuntimeError("scoring definition mismatch; downgrade refused")
    op.execute("ALTER TABLE execution_definitions ENABLE TRIGGER execution_definitions_immutable")
