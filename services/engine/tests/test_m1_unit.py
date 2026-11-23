from decimal import Decimal

import pytest
from hypothesis import given, settings
from hypothesis.strategies import decimals

from app import accounting


@given(
    amount=decimals(min_value="0.01", max_value="1000000", places=8, allow_nan=False, allow_infinity=False),
    equity=decimals(min_value="100", max_value="1000000", places=8, allow_nan=False, allow_infinity=False),
    units=decimals(min_value="1", max_value="10000", places=8, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100)
def test_unitization_property(amount, equity, units):
    nav_before, issued, residual, nav_after = accounting.unitize(amount, equity, units)
    assert issued > 0
    assert abs(nav_after - nav_before) <= Decimal("0.000000000000000000000000000001")
    assert abs(residual) <= nav_before * accounting.PRECISE


def test_large_accepted_amount_keeps_eight_places_without_default_context_failure():
    assert accounting.parse_amount("9999999999999999999999") == Decimal(
        "9999999999999999999999.00000000"
    )


def test_numeric_column_bounds_are_rejected_before_database_rounding():
    with pytest.raises(accounting.AccountingError, match="NUMERIC_LIMIT"):
        accounting._fit(Decimal("1" + "0" * 30), accounting.AMOUNT, accounting.MONEY_MAX)
    with pytest.raises(accounting.AccountingError, match="NUMERIC_LIMIT"):
        accounting._fit(Decimal("1.000000001"), accounting.AMOUNT, accounting.MONEY_MAX)
