"""The day's reference NAV (RISK_POLICY's daily reference, M3's rule, kept by ExecPlan 0060 for ``SPOT_POLICY_V1``).

Exact Decimal; nothing here reads a database or a clock: the caller passes one consistent, locked snapshot.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Protocol


class ReferencePolicy(Protocol):
    reference_timeliness_ms: int


@dataclass(frozen=True)
class ReferenceChoice:
    nav: Decimal
    quality: str  # TIMELY or LATE_CONSERVATIVE
    lateness_ms: int


def midnight(at: datetime) -> datetime:
    return at.replace(hour=0, minute=0, second=0, microsecond=0)


def daily_reference(first_nav: Decimal, first_at: datetime, prior_navs: Sequence[tuple[datetime, Decimal]],
                    policy: ReferencePolicy) -> ReferenceChoice:
    """First valid NAV at/after 00:00 UTC; if late, the conservative max with the prior 24 h."""
    day_start = midnight(first_at)
    lateness = int((first_at - day_start).total_seconds() * 1000)
    if lateness <= policy.reference_timeliness_ms:
        return ReferenceChoice(first_nav, "TIMELY", lateness)
    window_start = day_start - timedelta(hours=24)
    prior = [value for at, value in prior_navs if window_start <= at < day_start]
    return ReferenceChoice(max([first_nav, *prior]), "LATE_CONSERVATIVE", lateness)
