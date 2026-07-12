# SPDX-License-Identifier: Apache-2.0
"""Benford's Law leading-digit analysis -- a forensic-audit anomaly screen.

A pre-verified claimlib code artifact for audit & fraud detection. In many
natural datasets (financial amounts, populations, invoice totals) the leading
digit d occurs with probability log10(1 + 1/d), so 1 leads about 30.1% of the
time and 9 only 4.6%. Auditors flag datasets that deviate sharply from this
distribution. This module computes the leading digit, the expected and observed
distributions, and the chi-square and MAD conformance statistics. That the
expected distribution equals the Benford formula and the statistics are computed
correctly is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    first_digit(value: float) -> int                 # leading significant digit
    expected_distribution() -> dict[int, float]      # d -> log10(1 + 1/d)
    observed_distribution(data) -> dict[int, float]
    chi_square(data) -> float
    mad(data) -> float                               # mean absolute deviation
    conforms(data, mad_threshold=0.015) -> bool

    >>> round(expected_distribution()[1], 4)
    0.301
"""
from __future__ import annotations

import math
from collections.abc import Sequence


class BenfordError(ValueError):
    """Empty data or a value with no leading significant digit (zero)."""


def first_digit(value: float) -> int:
    """Return the leading significant digit (1..9) of ``abs(value)``."""
    v = abs(float(value))
    if v == 0 or v != v or v in (float("inf"), float("-inf")):
        raise BenfordError("value must be finite and non-zero")
    # Scientific notation puts the leading significant digit first: "d.dddde+xx".
    return int(f"{v:.15e}"[0])


def expected_distribution() -> dict[int, float]:
    """Return the Benford probability log10(1 + 1/d) for each digit 1..9."""
    return {d: math.log10(1 + 1 / d) for d in range(1, 10)}


def _counts(data: Sequence[float]) -> dict[int, int]:
    if len(data) == 0:
        raise BenfordError("data must be non-empty")
    counts = {d: 0 for d in range(1, 10)}
    for value in data:
        counts[first_digit(value)] += 1
    return counts


def observed_distribution(data: Sequence[float]) -> dict[int, float]:
    """Return the observed frequency of each leading digit 1..9."""
    counts = _counts(data)
    n = len(data)
    return {d: counts[d] / n for d in range(1, 10)}


def chi_square(data: Sequence[float]) -> float:
    """Return the chi-square statistic of *data* against the Benford expectation."""
    counts = _counts(data)
    n = len(data)
    expected = expected_distribution()
    stat = 0.0
    for d in range(1, 10):
        exp_count = n * expected[d]
        stat += (counts[d] - exp_count) ** 2 / exp_count
    return stat


def mad(data: Sequence[float]) -> float:
    """Return the mean absolute deviation of observed vs expected frequencies."""
    observed = observed_distribution(data)
    expected = expected_distribution()
    return sum(abs(observed[d] - expected[d]) for d in range(1, 10)) / 9


def conforms(data: Sequence[float], mad_threshold: float = 0.015) -> bool:
    """Return True iff the MAD is within *mad_threshold* (default 'close' per Nigrini)."""
    return mad(data) <= mad_threshold
