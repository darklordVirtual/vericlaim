# SPDX-License-Identifier: Apache-2.0
"""Percentiles / quantiles -- the p50 / p95 / p99 of latency observability.

A pre-verified claimlib code artifact. It computes exact percentiles two standard
ways: linear interpolation between order statistics (the "inclusive" / numpy
default, matching :func:`statistics.quantiles`) and the nearest-rank method.
That the linear method agrees with the stdlib ``statistics`` module and the
nearest-rank method matches its definition over a fixed battery is registered as
a claim and proven by a committed evidence artifact.

Public API
----------
    percentile(data, p, method="linear") -> float   # p in 0..100
    median(data) -> float
    quantiles(data, n=4, method="linear") -> list[float]

    >>> percentile([1, 2, 3, 4], 50)
    2.5
    >>> percentile([1, 2, 3, 4, 5], 90, method="nearest_rank")
    5
"""
from __future__ import annotations

import math
from collections.abc import Sequence


class PercentileError(ValueError):
    """Empty data, out-of-range p, or unknown method."""


def percentile(data: Sequence[float], p: float, method: str = "linear") -> float:
    """Return the *p*-th percentile (0..100) of *data*.

    ``linear``: interpolate between the two nearest order statistics at rank
    ``p/100 * (n-1)`` -- identical to ``statistics.quantiles(..., method=
    'inclusive')``. ``nearest_rank``: the smallest value at or below which at
    least ``p`` percent of the data falls (ceil(p/100 * n)).
    """
    if not data:
        raise PercentileError("data must be non-empty")
    if not 0 <= p <= 100:
        raise PercentileError("p must be in 0..100")
    ordered = sorted(data)
    n = len(ordered)
    if method == "linear":
        if n == 1:
            return ordered[0]
        rank = (p / 100) * (n - 1)
        low = math.floor(rank)
        frac = rank - low
        if low + 1 >= n:
            return ordered[-1]
        return ordered[low] + frac * (ordered[low + 1] - ordered[low])
    if method == "nearest_rank":
        if p == 0:
            return ordered[0]
        idx = math.ceil(p / 100 * n)
        return ordered[min(idx, n) - 1]
    raise PercentileError(f"unknown method {method!r}")


def median(data: Sequence[float]) -> float:
    """Return the median (50th percentile, linear) of *data*."""
    return percentile(data, 50, "linear")


def quantiles(data: Sequence[float], n: int = 4, method: str = "linear") -> list[float]:
    """Return the *n*-1 cut points dividing *data* into *n* equal groups."""
    if not isinstance(n, int) or isinstance(n, bool) or n < 2:
        raise PercentileError("n must be an int >= 2")
    return [percentile(data, i * 100 / n, method) for i in range(1, n)]
