"""Strict parsing of Binance's public answers: exact decimals, UTC millisecond times, bounded JSON (M2's rules,
``app.market_data.parse`` until ExecPlan 0060). Anything that does not have the documented shape is refused
(``PayloadError``), never guessed."""

import json
import re
from datetime import UTC, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Any

PLAIN_DECIMAL = re.compile(r"^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$")


class PayloadError(ValueError):
    """A public answer cannot be used as a market observation."""


def utc_from_ms(value: Any) -> datetime:
    if type(value) is not int or value < 0 or value > 253402300799999:
        raise PayloadError("invalid_millisecond_timestamp")
    try:
        return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(milliseconds=value)
    except (OverflowError, ValueError) as exc:
        raise PayloadError("invalid_millisecond_timestamp") from exc


def exact_decimal(value: Any, *, positive: bool = False) -> Decimal:
    if not isinstance(value, str) or len(value) > 80 or not PLAIN_DECIMAL.fullmatch(value):
        raise PayloadError("invalid_decimal")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise PayloadError("invalid_decimal") from exc
    if not number.is_finite() or (positive and number <= 0):
        raise PayloadError("invalid_decimal")
    return number


def decode_json(body: bytes, max_bytes: int = 2_097_152) -> Any:
    if len(body) > max_bytes:
        raise PayloadError("payload_too_large")
    try:
        return json.loads(
            body,
            parse_constant=lambda _value: (_ for _ in ()).throw(PayloadError("invalid_json_constant")),
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PayloadError("invalid_json") from exc


def declared_request_weight(body: bytes) -> int | None:
    """The provider's REQUEST_WEIGHT allowance per one minute, as an exchangeInfo answer declares it in its
    ``rateLimits`` array. None unless exactly one entry has the documented shape; the caller then keeps what it
    knew."""
    try:
        data = decode_json(body)
    except PayloadError:
        return None
    limits = data.get("rateLimits") if isinstance(data, dict) else None
    if not isinstance(limits, list):
        return None
    declared = [
        item.get("limit") for item in limits
        if isinstance(item, dict) and item.get("rateLimitType") == "REQUEST_WEIGHT"
        and item.get("interval") == "MINUTE" and type(item.get("intervalNum")) is int and item["intervalNum"] == 1
    ]
    if len(declared) != 1 or type(declared[0]) is not int or not 0 < declared[0] <= 10_000_000:
        return None
    return declared[0]


def spot_permitted(item: dict[str, Any]) -> bool:
    """Whether a SPOT-only account may trade the symbol: Binance documents alternatives inside each of
    ``permissionSets`` and AND across them; without them, ``permissions`` must name SPOT."""
    permissions = item.get("permissions")
    permission_sets = item.get("permissionSets")
    if permission_sets is not None:
        return isinstance(permission_sets, list) and bool(permission_sets) and all(
            isinstance(clause, list) and "SPOT" in clause for clause in permission_sets)
    return isinstance(permissions, list) and "SPOT" in permissions
