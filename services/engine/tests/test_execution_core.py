"""The execution core the spot account keeps (M3's pure checks, kept by ExecPlan 0060): the exact Decimal operations,
the deterministic row identities, the canonical definition hash and the day's reference NAV. No database; every
number is SYNTHETIC."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation, localcontext
from uuid import uuid5

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.execution import lifecycle
from app.execution.definitions import canonical_json, definition_hash
from app.execution.numbers import (
    CONTEXT,
    NumberPolicyError,
    add,
    ceil_amount,
    dec,
    div,
    floor_to_step,
    is_multiple,
    mul,
    sub,
)
from app.execution.risk import daily_reference
from app.spot.definitions import POLICY

# --- the plain decimal operations (ExecPlan 0025 section 5.3) -----------------------------------
# ``mul``, ``div``, ``add`` and ``sub`` ask the one context directly. These tests fail when one of
# them gives another digit, another exponent or another error than the operator inside the context.

AWKWARD = [Decimal(value) for value in (
    "0", "-0", "1", "-1", "3", "0.1", "0.00000001", "1E+2", "1.5E-7", "0E-8", "123456789.123456789",
    "9" * 40 + "." + "9" * 70, "-" + "7" * 100, "1E-120", "1E+120")]


def by_operators(left: Decimal, right: Decimal) -> dict[str, str | None]:
    """The operators inside the context, exactly as the helpers were written before (a sum begins at zero
    and a product at one, which decides the sign of a zero): digits and exponent as text."""
    with localcontext(CONTEXT):
        return {"add": str(sum((left, right), Decimal(0))), "sub": str(left - right),
                "mul": str(Decimal(1) * left * right),
                "three": str(Decimal(1) * left * right * left), "sum": str(sum((left, right, left), Decimal(0))),
                "div": None if right == 0 else str(left / right)}


def by_helpers(left: Decimal, right: Decimal) -> dict[str, str | None]:
    return {"add": str(add(left, right)), "sub": str(sub(left, right)), "mul": str(mul(left, right)),
            "three": str(mul(left, right, left)), "sum": str(add(left, right, left)),
            "div": None if right == 0 else str(div(left, right))}


def test_the_plain_operations_give_what_the_operators_give_inside_the_context():
    for left in AWKWARD:
        for right in AWKWARD:
            assert by_helpers(left, right) == by_operators(left, right), (left, right)
    # Values longer than the context's precision are rounded by it, in both forms, already when alone.
    assert len(AWKWARD[11].as_tuple().digits) == 110 and len(mul(AWKWARD[11]).as_tuple().digits) == 96
    assert str(add(AWKWARD[11])) == str(mul(AWKWARD[11])) and str(add(Decimal("1.50"))) == "1.50"
    assert str(mul()) == "1" and str(add()) == "0"
    # Whole numbers, as some callers pass them.
    with localcontext(CONTEXT):
        expected = (Decimal("2.5") * 3, Decimal("2.5") + 3, 3 - Decimal("2.5"), Decimal("2.5") / 3)
    assert (mul(Decimal("2.5"), 3), add(Decimal("2.5"), 3), sub(3, Decimal("2.5")), div(Decimal("2.5"), 3)) == expected
    # The context of the calling thread decides nothing.
    with localcontext() as ambient:
        ambient.prec = 3
        assert str(mul(Decimal("1.23456"), Decimal("2"))) == "2.46912"
        assert str(add(Decimal("1.23456"), Decimal("2"))) == "3.23456"
        assert str(div(Decimal("1"), Decimal("3"))) == "0." + "3" * 96
    # What the context refuses is refused as before, and a float is no operand.
    with pytest.raises(NumberPolicyError, match="division_by_zero"):
        div(Decimal(1), Decimal(0))
    with pytest.raises(InvalidOperation):
        mul(Decimal("Infinity"), Decimal(0))
    with pytest.raises(InvalidOperation):
        sub(Decimal("Infinity"), Decimal("Infinity"))
    for refused in (lambda: mul(Decimal(1), 1.5), lambda: add(Decimal(1), 1.5), lambda: sub(Decimal(1), 1.5),
                    lambda: div(Decimal(1), 1.5)):
        with pytest.raises(TypeError):
            refused()


FINITE = st.decimals(min_value=Decimal("-1E30"), max_value=Decimal("1E30"), allow_nan=False, allow_infinity=False,
                     places=18)


@settings(max_examples=400, deadline=None)
@given(left=FINITE, right=FINITE)
def test_the_plain_operations_match_the_operators_for_any_amount(left, right):
    assert by_helpers(left, right) == by_operators(left, right)


def test_quantities_round_down_to_the_step_and_debits_round_up():
    assert floor_to_step(Decimal("0.123456789"), Decimal("0.00001")) == Decimal("0.12345")
    assert floor_to_step(Decimal("-1"), Decimal("0.00001")) == 0
    assert is_multiple(Decimal("0.12345"), Decimal("0.00001")) and not is_multiple(Decimal("0.123456"),
                                                                                    Decimal("0.00001"))
    assert ceil_amount(Decimal("0.000000001")) == Decimal("0.00000001")
    with pytest.raises(NumberPolicyError, match="nonpositive_step"):
        floor_to_step(Decimal(1), Decimal(0))
    for refused in (1.5, True, "NaN", "Infinity", "abc", None):
        with pytest.raises(NumberPolicyError):
            dec(refused)
    assert dec("12.5") == Decimal("12.5") and dec(3) == Decimal(3)


# --- the deterministic identities --------------------------------------------------------------------------------

def test_a_stable_id_is_deterministic():
    assert lifecycle.stable_id("fill", "o", 7) == lifecycle.stable_id("fill", "o", 7)
    assert lifecycle.stable_id("fill", "o", 7) != lifecycle.stable_id("fill", "o", 8)


@settings(max_examples=400, deadline=None)
@given(st.text(max_size=12), st.lists(st.one_of(st.text(max_size=40), st.integers(), st.none(), st.uuids(),
                                                 st.decimals(allow_nan=False, allow_infinity=False)), max_size=5))
def test_a_stable_id_is_the_uuid5_of_its_kind_and_parts(kind, parts):
    """``stable_id`` hashes as ``uuid.uuid5`` does, without its per-call import and checks (ExecPlan 0025 §5.9)."""
    expected = uuid5(lifecycle._NAMESPACE, kind + ":" + "|".join(str(part) for part in parts))
    made = lifecycle.stable_id(kind, *parts)
    assert made == expected and made.version == 5 and made.variant == expected.variant and str(made) == str(expected)


def test_a_definition_hashes_over_its_canonical_json():
    definition = {"b": "0.1", "a": {"z": 1, "y": [2, 3]}, "label": "é"}
    assert canonical_json(definition) == '{"a":{"y":[2,3],"z":1},"b":"0.1","label":"\\u00e9"}'
    assert definition_hash(definition) == definition_hash(dict(reversed(list(definition.items()))))
    assert len(definition_hash(definition)) == 64


# --- the day's reference NAV ------------------------------------------------------------------------------------

def test_daily_reference_timely_at_300s_and_conservative_when_late():
    assert POLICY.reference_timeliness_ms == 300_000
    midnight = datetime(2026, 9, 29, tzinfo=UTC)
    prior = [(midnight - timedelta(hours=2), Decimal("105")), (midnight - timedelta(hours=30), Decimal("200"))]
    timely = daily_reference(Decimal("100"), midnight + timedelta(seconds=300), prior, POLICY)
    assert timely.quality == "TIMELY" and timely.nav == Decimal("100")
    late = daily_reference(Decimal("100"), midnight + timedelta(seconds=300, milliseconds=1), prior, POLICY)
    assert late.quality == "LATE_CONSERVATIVE" and late.nav == Decimal("105")
