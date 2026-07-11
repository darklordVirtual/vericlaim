# SPDX-License-Identifier: Apache-2.0
"""OEE -- Overall Equipment Effectiveness (manufacturing productivity metric).

A pre-verified claimlib code artifact. OEE is the standard factory-floor measure
of how fully a machine is used: the product of three factors, each a ratio in
[0, 1].

    Availability = Run Time / Planned Production Time
    Performance  = (Ideal Cycle Time * Total Count) / Run Time
    Quality      = Good Count / Total Count
    OEE          = Availability * Performance * Quality

This module computes those factors; that they reproduce the canonical published
worked example (Availability 88.81%, Performance 86.11%, Quality 97.80%,
OEE 74.79%) is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    availability(run_time, planned_production_time) -> float
    performance(ideal_cycle_time, total_count, run_time) -> float
    quality(good_count, total_count) -> float
    oee(planned_production_time, run_time, ideal_cycle_time,
        total_count, good_count) -> dict   # all factors + oee

    >>> round(oee(420*60, 373*60, 1.0, 19271, 18848)["oee"], 4)
    0.7479
"""
from __future__ import annotations


class OEEError(ValueError):
    """A non-positive denominator or otherwise out-of-domain OEE input."""


def _positive(name: str, value: float) -> float:
    if value != value or value in (float("inf"), float("-inf")):
        raise OEEError(f"{name} must be finite")
    if value <= 0:
        raise OEEError(f"{name} must be positive, got {value}")
    return value


def _nonneg(name: str, value: float) -> float:
    if value != value or value in (float("inf"), float("-inf")):
        raise OEEError(f"{name} must be finite")
    if value < 0:
        raise OEEError(f"{name} must be non-negative, got {value}")
    return value


def availability(run_time: float, planned_production_time: float) -> float:
    """Fraction of planned time the equipment was actually running."""
    _nonneg("run_time", run_time)
    _positive("planned_production_time", planned_production_time)
    if run_time > planned_production_time:
        raise OEEError("run_time cannot exceed planned_production_time")
    return run_time / planned_production_time


def performance(ideal_cycle_time: float, total_count: float, run_time: float) -> float:
    """Fraction of the theoretical maximum throughput actually achieved."""
    _nonneg("ideal_cycle_time", ideal_cycle_time)
    _nonneg("total_count", total_count)
    _positive("run_time", run_time)
    result = (ideal_cycle_time * total_count) / run_time
    if result > 1:
        raise OEEError("performance exceeds 1 (ideal_cycle_time too large)")
    return result


def quality(good_count: float, total_count: float) -> float:
    """Fraction of produced units that met quality standards."""
    _nonneg("good_count", good_count)
    _positive("total_count", total_count)
    if good_count > total_count:
        raise OEEError("good_count cannot exceed total_count")
    return good_count / total_count


def oee(planned_production_time: float, run_time: float, ideal_cycle_time: float,
        total_count: float, good_count: float) -> dict:
    """Return the three OEE factors and their product."""
    a = availability(run_time, planned_production_time)
    p = performance(ideal_cycle_time, total_count, run_time)
    q = quality(good_count, total_count)
    return {"availability": a, "performance": p, "quality": q, "oee": a * p * q}
