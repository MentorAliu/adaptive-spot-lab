"""Exact Decimal policy for execution arithmetic.

Quantities round down, cash debits/fees round against the account and nothing is
converted through binary floating point. Every helper uses one explicit context.

The four plain operations (``mul``, ``div``, ``add``, ``sub``) ask that context
directly: its methods give what the operators give inside ``localcontext(CONTEXT)``,
the same digits, exponent, rounding and traps, without a copy of the context for
every operation (ExecPlan 0025 section 5.3). A step with a position asks some thirty
of them.
"""

from decimal import (
    ROUND_CEILING,
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    Context,
    Decimal,
    InvalidOperation,
    localcontext,
)

AMOUNT = Decimal("0.00000001")
PRECISE = Decimal("0.000000000000000000000000000000000001")
CONTEXT = Context(prec=96, rounding=ROUND_HALF_EVEN)
ZERO = Decimal(0)
ONE = Decimal(1)
BPS = Decimal(10000)


class NumberPolicyError(ValueError):
    pass


def dec(value: object) -> Decimal:
    """Accept Decimal, int or canonical decimal text; never float."""
    if isinstance(value, bool) or isinstance(value, float):
        raise NumberPolicyError("float_or_bool_rejected")
    if isinstance(value, Decimal):
        number = value
    elif isinstance(value, int):
        number = Decimal(value)
    elif isinstance(value, str):
        try:
            number = Decimal(value)
        except InvalidOperation as exc:
            raise NumberPolicyError("invalid_decimal") from exc
    else:
        raise NumberPolicyError("unsupported_number")
    if not number.is_finite():
        raise NumberPolicyError("nonfinite_decimal")
    return number


def floor_to_step(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        raise NumberPolicyError("nonpositive_step")
    if value <= 0:
        return ZERO
    with localcontext(CONTEXT):
        return (value / step).to_integral_value(rounding=ROUND_FLOOR) * step


def is_multiple(value: Decimal, step: Decimal) -> bool:
    if step <= 0:
        raise NumberPolicyError("nonpositive_step")
    with localcontext(CONTEXT):
        return (value / step) == (value / step).to_integral_value(rounding=ROUND_FLOOR)


def ceil_amount(value: Decimal) -> Decimal:
    with localcontext(CONTEXT):
        return value.quantize(AMOUNT, rounding=ROUND_CEILING)


def nav(equity: Decimal, units: Decimal) -> Decimal:
    if units <= 0:
        raise NumberPolicyError("nonpositive_units")
    with localcontext(CONTEXT):
        return (equity / units).quantize(PRECISE, rounding=ROUND_HALF_EVEN)


def mul(*values: Decimal) -> Decimal:
    result = ONE
    for value in values:
        result = CONTEXT.multiply(result, value)
    return result


def div(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        raise NumberPolicyError("division_by_zero")
    return CONTEXT.divide(numerator, denominator)


def add(*values: Decimal) -> Decimal:
    result = ZERO
    for value in values:
        result = CONTEXT.add(result, value)
    return result


def sub(left: Decimal, right: Decimal) -> Decimal:
    return CONTEXT.subtract(left, right)


def text(value: Decimal | None) -> str | None:
    """Canonical plain decimal text for storage/JSON (no exponent)."""
    return None if value is None else format(value, "f")
