# SPDX-License-Identifier: Apache-2.0
"""Apdex -- the Application Performance Index (a user-satisfaction score).

A pre-verified claimlib code artifact for observability. Given a target response
time T, Apdex buckets each sample as satisfied (<= T), tolerating (T < t <= 4T),
or frustrated (> 4T), and scores in [0, 1]:

    Apdex_T = (satisfied + tolerating / 2) / total

That the classification thresholds and the score match the published Apdex
definition over a fixed hand-computed battery is registered as a claim and proven
by a committed evidence artifact.

Public API
----------
    classify(response_time, threshold) -> str      # satisfied | tolerating | frustrated
    counts(response_times, threshold) -> dict
    apdex(response_times, threshold) -> float      # rounded to 4 dp

    >>> apdex([0.1, 0.2, 0.3, 1.0, 3.0], 0.5)
    0.7
"""
from __future__ import annotations

from collections.abc import Sequence


class ApdexError(ValueError):
    """Empty samples or a non-positive threshold."""


def _check_threshold(threshold: float) -> float:
    if threshold != threshold or threshold in (float("inf"), float("-inf")):
        raise ApdexError("threshold must be finite")
    if threshold <= 0:
        raise ApdexError("threshold must be positive")
    return threshold


def classify(response_time: float, threshold: float) -> str:
    """Bucket a single response time relative to *threshold* (Apdex zones)."""
    _check_threshold(threshold)
    if response_time <= threshold:
        return "satisfied"
    if response_time <= 4 * threshold:
        return "tolerating"
    return "frustrated"


def counts(response_times: Sequence[float], threshold: float) -> dict:
    """Return the satisfied / tolerating / frustrated counts and total."""
    _check_threshold(threshold)
    if len(response_times) == 0:
        raise ApdexError("response_times must be non-empty")
    tally = {"satisfied": 0, "tolerating": 0, "frustrated": 0}
    for rt in response_times:
        tally[classify(rt, threshold)] += 1
    tally["total"] = len(response_times)
    return tally


def apdex(response_times: Sequence[float], threshold: float) -> float:
    """Return the Apdex score in [0, 1] for *response_times* at *threshold*."""
    c = counts(response_times, threshold)
    score = (c["satisfied"] + c["tolerating"] / 2) / c["total"]
    return round(score, 4)
