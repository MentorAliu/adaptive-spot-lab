"""``SPOT_RULE_V1``'s daily reading (ExecPlan 0060 section 6, R1): pure functions on SYNTHETIC closes. Every close
here is made up for the test; none is a recorded market value."""

import math
from dataclasses import replace
from datetime import UTC, datetime
from decimal import ROUND_DOWN, Decimal

import pytest

from app.execution.numbers import CONTEXT
from app.spot import rule as spot_rule
from app.spot.definitions import DAY_MS, RULE, SPOT_RULE_V1

LAST = int(datetime(2026, 11, 1, tzinfo=UTC).timestamp() * 1000)


def line(last: int = LAST, *, days: int = 400, base: str = "40000", step: str = "50",
         wiggle: str = "400") -> dict[int, Decimal]:
    """A straight line of ``step`` a day ending on ``last``, with an alternating ``wiggle``."""
    first = last - (days - 1) * DAY_MS
    return {first + n * DAY_MS: Decimal(base) + Decimal(step) * n + Decimal(wiggle) * (1 if n % 2 else -1)
            for n in range(days)}


def float_volatility(closes: dict[int, Decimal], first: int, last: int) -> float:
    """The same estimate in binary floating point, written apart from the code under test."""
    days = sorted(day for day in closes if first <= day <= last)
    variance = None
    for earlier, later in zip(days, days[1:], strict=False):
        squared = math.log(float(closes[later]) / float(closes[earlier])) ** 2
        variance = squared if variance is None else (60 * variance + squared) / 61
    return math.sqrt(365 * variance)


def expected_target(signal: Decimal, volatility: Decimal) -> Decimal:
    target = (max(signal, Decimal(0)) * min(Decimal(1), Decimal("0.05") / volatility)).quantize(
        Decimal("0.001"), rounding=ROUND_DOWN)
    return Decimal(0) if target < Decimal("0.01") else target


def test_the_rule_reads_the_definition_it_was_approved_with():
    assert (RULE.id, RULE.lookbacks, RULE.tolerance_days, RULE.volatility_days) == ("SPOT_RULE_V1", (30, 91, 365), 7,
                                                                                     365)
    assert (RULE.centre_of_mass, RULE.annualization, RULE.minimum_days) == (60, 365, 300)
    assert (RULE.target, RULE.cap, RULE.step, RULE.flat, RULE.buffer) == (
        Decimal("0.05"), Decimal(1), Decimal("0.001"), Decimal("0.01"), Decimal("0.03"))
    assert (RULE.read_after_ms, RULE.retry_seconds) == (300_000, 900)
    assert SPOT_RULE_V1["direction"].endswith("NEVER_SHORT")


def test_a_rising_line_reads_long_sized_by_its_volatility():
    closes = line()
    found = spot_rule.target_of(closes, LAST)
    assert (found.result, found.reason, found.day_open_ms, found.close) == ("LONG", None, LAST, closes[LAST])
    assert [(a.lookback_days, a.day_open_ms, a.sign) for a in found.anchors] == [
        (30, LAST - 30 * DAY_MS, 1), (91, LAST - 91 * DAY_MS, 1), (365, LAST - 365 * DAY_MS, 1)]
    assert found.signal == 1 and found.days_stored == 366
    reference = float_volatility(closes, LAST - 365 * DAY_MS, LAST)
    assert math.isclose(float(found.volatility), reference, rel_tol=1e-12)
    assert 0 < found.target <= 1 and found.target == expected_target(found.signal, found.volatility)
    assert found.target == found.target.quantize(Decimal("0.001"))


def test_a_falling_line_reads_cash_and_never_short():
    found = spot_rule.target_of(line(step="-50"), LAST)
    assert (found.result, found.signal, found.target) == ("CASH", -1, 0)
    assert [a.sign for a in found.anchors] == [-1, -1, -1]
    assert found.features()["never_short"] is True


def test_the_signal_is_the_mean_of_the_three_signs_and_an_equal_close_counts_zero():
    closes = line()
    closes[LAST - 30 * DAY_MS] = closes[LAST] + 1  # above the day: -1
    found = spot_rule.target_of(closes, LAST)
    assert [a.sign for a in found.anchors] == [-1, 1, 1]
    assert found.signal == CONTEXT.divide(Decimal(1), Decimal(3))
    assert found.target == expected_target(found.signal, found.volatility)
    closes[LAST - 91 * DAY_MS] = closes[LAST]  # equal: 0
    found = spot_rule.target_of(closes, LAST)
    assert [a.sign for a in found.anchors] == [-1, 0, 1] and found.signal == 0 and found.result == "CASH"


def test_an_anchor_is_the_nearest_stored_day_within_seven_days_else_the_day_is_not_readable():
    closes = line()
    for back in range(30, 37):
        del closes[LAST - back * DAY_MS]
    found = spot_rule.target_of(closes, LAST)
    assert found.anchors[0].day_open_ms == LAST - 37 * DAY_MS and found.result == "LONG"
    del closes[LAST - 37 * DAY_MS]
    found = spot_rule.target_of(closes, LAST)
    assert (found.result, found.reason, found.target, found.anchors) == ("WARMUP", "ANCHOR_MISSING_30", None, ())
    assert spot_rule.act(found, Decimal("0.4"), True).action == "NO_CHANGE"


def test_a_missing_close_and_too_short_a_history_are_not_readable():
    closes = line()
    assert spot_rule.target_of(closes, LAST + DAY_MS).reason == "CLOSE_MISSING"
    assert spot_rule.target_of(line(days=365), LAST).reason == "ANCHOR_MISSING_365"
    assert spot_rule.target_of(line(days=366), LAST).result == "LONG"


def test_at_least_300_of_the_366_days_must_be_stored_and_a_gap_return_counts_once():
    closes = line()
    for back in range(100, 166):  # 66 days gone: 300 stored
        del closes[LAST - back * DAY_MS]
    found = spot_rule.target_of(closes, LAST)
    assert (found.result, found.days_stored) == ("LONG", 300)
    assert math.isclose(float(found.volatility), float_volatility(closes, LAST - 365 * DAY_MS, LAST), rel_tol=1e-12)
    del closes[LAST - 166 * DAY_MS]
    found = spot_rule.target_of(closes, LAST)
    assert (found.result, found.reason, found.days_stored) == ("WARMUP", "TOO_FEW_DAYS_299", 299)


def test_the_target_is_quantized_down_capped_at_one_and_zero_below_the_band():
    calm = spot_rule.target_of(line(step="10", wiggle="1"), LAST)
    assert calm.volatility < Decimal("0.05") and calm.target == 1 and calm.result == "LONG"
    found = spot_rule.target_of(line(), LAST)
    # A volatility target that makes the size 0.0105 of equity reads 0.010; 0.0099 reads 0.009, below the band: 0.
    just_above = replace(RULE, target=found.volatility * Decimal("0.0105"))
    assert spot_rule.target_of(line(), LAST, just_above).target == Decimal("0.010")
    just_below = replace(RULE, target=found.volatility * Decimal("0.0099"))
    below = spot_rule.target_of(line(), LAST, just_below)
    assert (below.result, below.target) == ("CASH", 0)


def test_the_action_trades_only_outside_the_buffer_and_sells_all_at_zero_unless_only_dust_is_held():
    half = spot_rule.Reading("LONG", LAST, target=Decimal("0.500"), signal=Decimal(1), volatility=Decimal("0.1"))
    for held, holding, action in (("0.48", True, "NO_CHANGE"), ("0.47", True, "NO_CHANGE"), ("0.4699", True, "BUY"),
                                  ("0", False, "BUY"), ("0.53", True, "NO_CHANGE"), ("0.5301", True, "SELL")):
        acted = spot_rule.act(half, Decimal(held), holding)
        assert (acted.action, acted.held) == (action, Decimal(held)), held
    small = replace(half, target=Decimal("0.020"))
    assert spot_rule.act(small, Decimal(0), False).action == "NO_CHANGE"
    cash = replace(half, result="CASH", target=Decimal(0))
    assert spot_rule.act(cash, Decimal("0.0001"), True).action == "SELL_ALL"
    assert spot_rule.act(cash, Decimal("0.00001"), False).action == "NO_CHANGE"  # dust: nothing to sell
    assert spot_rule.act(cash, Decimal(0), False).action == "NO_CHANGE"


def test_the_reading_for_a_day_reads_the_day_before():
    closes = line()
    morning = LAST + DAY_MS + 5 * 60_000
    found = spot_rule.reading(closes, morning, Decimal("0.25"), True)
    assert found.day_open_ms == LAST
    assert found == spot_rule.act(spot_rule.target_of(closes, LAST), Decimal("0.25"), True)
    assert spot_rule.utc_day_open(morning) == LAST + DAY_MS


def test_the_held_fraction_is_floored_and_needs_a_valuation():
    assert spot_rule.held_fraction(Decimal(0), None, None) == 0
    assert spot_rule.held_fraction(Decimal("0.1"), Decimal("60000"), Decimal("10000")) == Decimal("0.6")
    assert spot_rule.held_fraction(Decimal("0.1"), Decimal("60000.123456789"), Decimal("10000")) == \
        Decimal("0.60000123")
    for bid, equity in ((None, Decimal("10000")), (Decimal("60000"), None), (Decimal("60000"), Decimal(0))):
        with pytest.raises(ValueError, match="held_fraction_needs_a_valuation"):
            spot_rule.held_fraction(Decimal("0.1"), bid, equity)


def test_the_features_record_the_rule_and_every_input():
    found = spot_rule.act(spot_rule.target_of(line(), LAST), Decimal("0.1"), True)
    features = found.features()
    assert (features["rule"], features["rule_sha256"], features["action"]) == (RULE.id, RULE.sha256, "BUY")
    assert features["close"] == format(found.close, "f") and len(features["anchors"]) == 3
    assert Decimal(features["target"]) == found.target and Decimal(features["volatility"]) == found.volatility
    assert features["held"] == "0.1" and features["days_stored"] == 366


def test_a_log_return_is_the_same_memoized():
    first = spot_rule.log_return(Decimal("41000"), Decimal("40000"))
    assert first == CONTEXT.ln(CONTEXT.divide(Decimal("41000"), Decimal("40000")))
    assert spot_rule.log_return(Decimal("41000"), Decimal("40000")) is first
    assert math.isclose(float(first), math.log(41000 / 40000), rel_tol=1e-13)  # the float's own error near 1
