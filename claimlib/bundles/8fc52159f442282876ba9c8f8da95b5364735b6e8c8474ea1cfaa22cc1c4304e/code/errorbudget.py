# SPDX-License-Identifier: Apache-2.0
"""SLO / error-budget arithmetic — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that its availability and error-budget arithmetic
matches the textbook SRE formulas exactly — is registered as a claim and proven
by a committed evidence artifact; vendoring this module carries that claim (and
its caveat) with it.

Definitions (Google SRE Workbook, "Implementing SLOs")
-------------------------------------------------------
Given a measurement *window* (minutes) and an availability target *SLO* (percent):

    availability%        = (window - downtime) / window * 100
    error budget (min)   = window * (1 - SLO/100)
    budget remaining%    = (budget - downtime) / budget * 100

The error budget is the amount of unavailability the SLO permits over the
window. "Budget remaining" is what fraction of that allowance is still unspent;
it goes negative once you have burned through more downtime than the SLO allows.

Public API
----------
    availability(window_min, downtime_min) -> float          # rounded to 4 dp
    budget_minutes(slo_pct, window_min) -> float             # rounded to 6 dp
    error_budget_remaining_pct(slo_pct, window_min, downtime_min) -> float  # 4 dp

    >>> availability(43200, 21.6)          # 30-day window, 21.6 min down
    99.95
    >>> budget_minutes(99.9, 43200)        # 99.9% over 30 days
    43.2
    >>> error_budget_remaining_pct(99.9, 43200, 21.6)
    50.0
"""
from __future__ import annotations

__all__ = [
    "ErrorBudgetError",
    "availability",
    "budget_minutes",
    "error_budget_remaining_pct",
]

# Rounding precision. Availability and remaining% are reported to 4 decimals;
# the raw budget in minutes to 6, which is well below one second of a minute and
# absorbs binary-float noise (e.g. 43200*(1-99.9/100) == 43.20000000000004).
_PCT_DP = 4
_BUDGET_DP = 6


class ErrorBudgetError(ValueError):
    """An input is out of range (bad window, SLO, or downtime)."""


def _finite(name: str, x: float) -> None:
    # NaN/inf slip past every <,<=,> range check (nan<=0 and nan>100 are both
    # False), so validation that advertises fail-closed must reject them first.
    if x != x or x in (float("inf"), float("-inf")):
        raise ErrorBudgetError(f"{name} must be finite, got {x!r}")


def _check_window(window_min: float) -> float:
    if not isinstance(window_min, (int, float)) or isinstance(window_min, bool):
        raise ErrorBudgetError(f"window_min must be a number, got {window_min!r}")
    _finite("window_min", window_min)
    if window_min <= 0:
        raise ErrorBudgetError(f"window_min must be > 0, got {window_min!r}")
    return float(window_min)


def _check_downtime(downtime_min: float, window_min: float) -> float:
    if not isinstance(downtime_min, (int, float)) or isinstance(downtime_min, bool):
        raise ErrorBudgetError(f"downtime_min must be a number, got {downtime_min!r}")
    _finite("downtime_min", downtime_min)
    if downtime_min < 0:
        raise ErrorBudgetError(f"downtime_min must be >= 0, got {downtime_min!r}")
    if downtime_min > window_min:
        raise ErrorBudgetError(
            f"downtime_min ({downtime_min}) exceeds window_min ({window_min})")
    return float(downtime_min)


def _check_slo(slo_pct: float, *, allow_100: bool) -> float:
    if not isinstance(slo_pct, (int, float)) or isinstance(slo_pct, bool):
        raise ErrorBudgetError(f"slo_pct must be a number, got {slo_pct!r}")
    _finite("slo_pct", slo_pct)
    if slo_pct < 0 or slo_pct > 100:
        raise ErrorBudgetError(f"slo_pct must be in [0, 100], got {slo_pct!r}")
    if not allow_100 and slo_pct == 100:
        raise ErrorBudgetError(
            "slo_pct of 100 leaves a zero error budget; "
            "budget-remaining is undefined")
    return float(slo_pct)


def availability(window_min: float, downtime_min: float) -> float:
    """Observed availability as a percentage, rounded to 4 decimal places.

        availability% = (window - downtime) / window * 100

    ``window_min`` must be > 0; ``downtime_min`` in ``[0, window_min]``.
    Raises :class:`ErrorBudgetError` on out-of-range input.
    """
    window = _check_window(window_min)
    downtime = _check_downtime(downtime_min, window)
    return round((window - downtime) / window * 100, _PCT_DP)


def budget_minutes(slo_pct: float, window_min: float) -> float:
    """Error budget in minutes for ``slo_pct`` over ``window_min``, rounded 6 dp.

        budget = window * (1 - SLO/100)

    ``slo_pct`` in ``[0, 100]`` (100 yields a zero budget); ``window_min`` > 0.
    Raises :class:`ErrorBudgetError` on out-of-range input.
    """
    window = _check_window(window_min)
    slo = _check_slo(slo_pct, allow_100=True)
    return round(window * (1 - slo / 100), _BUDGET_DP)


def error_budget_remaining_pct(slo_pct: float, window_min: float,
                               downtime_min: float) -> float:
    """Percent of the error budget still unspent, rounded to 4 decimal places.

        remaining% = (budget - downtime) / budget * 100

    Returns 100.0 with no downtime, 0.0 when downtime exactly equals the
    budget, and a negative value once the budget is overspent. ``slo_pct`` must
    be in ``[0, 100)`` — an SLO of exactly 100 has a zero budget for which this
    ratio is undefined and raises :class:`ErrorBudgetError`.
    """
    window = _check_window(window_min)
    slo = _check_slo(slo_pct, allow_100=False)
    downtime = _check_downtime(downtime_min, window)
    budget = window * (1 - slo / 100)
    return round((budget - downtime) / budget * 100, _PCT_DP)
