# SPDX-License-Identifier: Apache-2.0
"""Multiwindow multi-burn-rate SLO alerting math — a reusable, stdlib-only
building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it reproduces the Google SRE Workbook's
canonical burn-rate alerting table and algebra exactly — is registered as a
claim and proven by a committed evidence artifact; vendoring this module
carries that claim (and its caveat) with it.

Definitions (Google SRE Workbook, ch. 5 "Alerting on SLOs")
-----------------------------------------------------------
Burn rate is how fast, relative to the SLO, a service consumes its error
budget: a burn rate of 1 spends exactly the whole budget over the SLO period;
a burn rate of 2 exhausts it in half the period.

    burn_rate          = budget_consumed_fraction * period / window
    budget_consumed    = burn_rate * window / period
    error_rate         = burn_rate * (1 - SLO/100)      (fraction of requests)
    time_to_exhaustion = period * remaining_fraction / burn_rate

The Workbook's recommended 30-day policy (``GOOGLE_30D_POLICY``):

    2%  of budget in 1 hour  -> burn rate 14.4 -> page
    5%  of budget in 6 hours -> burn rate 6    -> page
    10% of budget in 3 days  -> burn rate 1    -> ticket

with each short (confirmation) window 1/12 of its long window, and the alert
firing only when BOTH windows exceed the threshold error ratio (this is what
makes the alert reset quickly once the errors stop).

All window/period arguments are unit-agnostic: pass window and period in the
SAME unit (minutes, hours, ...). ``MINUTES_PER_30D`` / ``HOURS_PER_30D`` cover
the standard 30-day period.

Public API
----------
    burn_rate(budget_fraction, window, period) -> float
    budget_consumed(rate, window, period) -> float
    error_rate(rate, slo_pct) -> float
    burn_rate_from_error_ratio(error_ratio, slo_pct) -> float
    budget_remaining(rate, elapsed, period, initial_fraction=1.0) -> float
    time_to_exhaustion(rate, period, remaining_fraction=1.0) -> float
    short_window(long_window, divisor=12.0) -> float
    multiwindow_alert(long_ratio, short_ratio, threshold_rate, slo_pct) -> bool
    GOOGLE_30D_POLICY: tuple[dict, ...]   # the published three-tier table

    >>> burn_rate(0.02, 1, HOURS_PER_30D)
    14.4
    >>> time_to_exhaustion(10, HOURS_PER_30D)
    72.0
    >>> multiwindow_alert(0.02, 0.02, 14.4, 99.9)
    True
"""
from __future__ import annotations

__all__ = [
    "BurnRateError",
    "GOOGLE_30D_POLICY",
    "HOURS_PER_30D",
    "MINUTES_PER_30D",
    "budget_consumed",
    "budget_remaining",
    "burn_rate",
    "burn_rate_from_error_ratio",
    "error_rate",
    "multiwindow_alert",
    "short_window",
    "time_to_exhaustion",
]

# The standard 30-day SLO period in two common units.
MINUTES_PER_30D = 43200.0
HOURS_PER_30D = 720.0

# Rounding precision: rates / fractions / durations are rounded to 6 dp for
# byte-stable artifacts (absorbs binary-float noise, e.g. 0.05*720/6 ==
# 6.000000000000001). The alert threshold uses 12 dp so that a measured error
# ratio exactly AT the threshold compares deterministically (strict >).
_DP = 6
_THRESHOLD_DP = 12


class BurnRateError(ValueError):
    """An input is out of range (bad fraction, rate, window, or period)."""


def _num(name: str, x: float) -> float:
    if not isinstance(x, (int, float)) or isinstance(x, bool):
        raise BurnRateError(f"{name} must be a number, got {x!r}")
    x = float(x)
    # NaN/inf slip past every <,<=,> range check (nan<=0 and nan>100 are both
    # False), so validation that advertises fail-closed must reject them first.
    if x != x or x in (float("inf"), float("-inf")):
        raise BurnRateError(f"{name} must be finite, got {x!r}")
    return x


def _positive(name: str, x: float) -> float:
    v = _num(name, x)
    if v <= 0:
        raise BurnRateError(f"{name} must be > 0, got {x!r}")
    return v


def _fraction(name: str, x: float) -> float:
    v = _num(name, x)
    if v < 0 or v > 1:
        raise BurnRateError(f"{name} must be in [0, 1], got {x!r}")
    return v


def _rate(name: str, x: float) -> float:
    v = _num(name, x)
    if v < 0:
        raise BurnRateError(f"{name} must be >= 0, got {x!r}")
    return v


def _slo(slo_pct: float, *, allow_100: bool) -> float:
    v = _num("slo_pct", slo_pct)
    if v < 0 or v > 100:
        raise BurnRateError(f"slo_pct must be in [0, 100], got {slo_pct!r}")
    if not allow_100 and v == 100:
        raise BurnRateError(
            "slo_pct of 100 leaves a zero error budget; "
            "the burn rate for an error ratio is undefined")
    return v


def _window(name: str, window: float, period: float) -> float:
    w = _positive(name, window)
    if w > period:
        raise BurnRateError(
            f"{name} ({window!r}) exceeds the SLO period ({period!r})")
    return w


def burn_rate(budget_fraction: float, window: float, period: float) -> float:
    """Burn rate that spends *budget_fraction* of the budget in *window*.

        burn_rate = budget_fraction * period / window

    E.g. spending 2% of a 30-day budget in 1 hour is a burn rate of
    ``0.02 * 720 / 1 = 14.4``. *window* and *period* must be in the same time
    unit, with ``0 < window <= period``; *budget_fraction* in ``[0, 1]``.
    Rounded to 6 dp. Raises :class:`BurnRateError` on out-of-range input.
    """
    p = _positive("period", period)
    w = _window("window", window, p)
    f = _fraction("budget_fraction", budget_fraction)
    return round(f * p / w, _DP)


def budget_consumed(rate: float, window: float, period: float) -> float:
    """Fraction of the error budget consumed burning at *rate* for *window*.

        budget_consumed = rate * window / period

    The inverse of :func:`burn_rate`. Can exceed 1.0 when the inputs imply
    more than the whole budget (overspend). Rounded to 6 dp.
    """
    p = _positive("period", period)
    w = _window("window", window, p)
    r = _rate("rate", rate)
    return round(r * w / p, _DP)


def error_rate(rate: float, slo_pct: float) -> float:
    """Error-rate fraction of requests corresponding to burn rate *rate*.

        error_rate = rate * (1 - slo_pct/100)

    E.g. burn rate 10 against a 99.9% SLO is a 1% error rate (0.01). Values
    above 1.0 mean the burn rate is infeasible for that SLO (a service cannot
    fail more than 100% of requests). Rounded to 6 dp.
    """
    r = _rate("rate", rate)
    s = _slo(slo_pct, allow_100=True)
    return round(r * (1 - s / 100), _DP)


def burn_rate_from_error_ratio(error_ratio: float, slo_pct: float) -> float:
    """Burn rate implied by a measured *error_ratio* (fraction of requests).

        rate = error_ratio / (1 - slo_pct/100)

    The inverse of :func:`error_rate`; this is the conversion an alerting rule
    applies to a measured window error ratio. *slo_pct* must be < 100 (a 100%
    SLO has a zero budget). Rounded to 6 dp.
    """
    e = _fraction("error_ratio", error_ratio)
    s = _slo(slo_pct, allow_100=False)
    return round(e / (1 - s / 100), _DP)


def budget_remaining(rate: float, elapsed: float, period: float,
                     initial_fraction: float = 1.0) -> float:
    """Budget fraction left after burning at *rate* for *elapsed* time.

        remaining = initial_fraction - rate * elapsed / period

    ``elapsed`` must be in ``[0, period]`` (same unit as *period*). Goes
    negative once the budget is overspent. Rounded to 6 dp.
    """
    p = _positive("period", period)
    e = _num("elapsed", elapsed)
    if e < 0 or e > p:
        raise BurnRateError(
            f"elapsed must be in [0, period], got {elapsed!r} "
            f"for period {period!r}")
    r = _rate("rate", rate)
    f = _fraction("initial_fraction", initial_fraction)
    return round(f - r * e / p, _DP)


def time_to_exhaustion(rate: float, period: float,
                       remaining_fraction: float = 1.0) -> float:
    """Time until the remaining budget is exhausted at constant *rate*.

        time = period * remaining_fraction / rate

    Returned in the same unit as *period*: burn rate 1 over a 720-hour period
    exhausts in 720 hours (30 days); burn rate 1000 in 0.72 hours (43.2 min —
    the Workbook prints this rounded as "43 minutes"). *rate* must be > 0 (a
    zero burn rate never exhausts; that raises rather than returning inf).
    Rounded to 6 dp.
    """
    p = _positive("period", period)
    r = _rate("rate", rate)
    if r == 0:
        raise BurnRateError("burn rate 0 never exhausts the budget")
    f = _fraction("remaining_fraction", remaining_fraction)
    return round(p * f / r, _DP)


def short_window(long_window: float, divisor: float = 12.0) -> float:
    """Confirmation (short) window for a long alert window.

    The Workbook guideline makes the short window 1/12 of the long window,
    e.g. 5 minutes for 1 hour, 30 minutes for 6 hours, 6 hours for 3 days.
    Same unit in, same unit out. Rounded to 6 dp.
    """
    w = _positive("long_window", long_window)
    d = _positive("divisor", divisor)
    return round(w / d, _DP)


def multiwindow_alert(long_ratio: float, short_ratio: float,
                      threshold_rate: float, slo_pct: float) -> bool:
    """Multiwindow alert condition: BOTH windows exceed the burn threshold.

    Implements the Workbook expression: fire iff the long-window error ratio
    AND the short-window error ratio are both strictly greater than
    ``threshold_rate * (1 - slo_pct/100)``. The short window stops the alert
    from firing (or keeps firing) once the error stops; the long window stops
    brief blips from paging. The threshold is rounded to 12 dp so a ratio
    exactly at the threshold deterministically does NOT alert.
    """
    lo = _fraction("long_ratio", long_ratio)
    sh = _fraction("short_ratio", short_ratio)
    r = _rate("threshold_rate", threshold_rate)
    s = _slo(slo_pct, allow_100=True)
    threshold = round(r * (1 - s / 100), _THRESHOLD_DP)
    return lo > threshold and sh > threshold


# The Google SRE Workbook ch. 5 recommended starting policy for a 30-day SLO
# period ("6: Multiwindow, Multi-Burn-Rate Alerts"). Windows in minutes so
# every value is exact. burn_rate values are the PUBLISHED numbers; evidence
# recomputes each from the formula and checks short == long / 12.
GOOGLE_30D_POLICY = (
    {"tier": 1, "budget_consumed": 0.02, "long_window_minutes": 60.0,
     "short_window_minutes": 5.0, "burn_rate": 14.4, "action": "page"},
    {"tier": 2, "budget_consumed": 0.05, "long_window_minutes": 360.0,
     "short_window_minutes": 30.0, "burn_rate": 6.0, "action": "page"},
    {"tier": 3, "budget_consumed": 0.10, "long_window_minutes": 4320.0,
     "short_window_minutes": 360.0, "burn_rate": 1.0, "action": "ticket"},
)
