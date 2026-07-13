# SPDX-License-Identifier: Apache-2.0
"""Erlang B — blocking probability for loss systems (telecom traffic
engineering) — reusable, claim-bound.

A pre-verified claimlib code artifact. The Erlang B formula gives the
probability that a call arriving at a group of N circuits offered A erlangs
of traffic finds all circuits busy (and is lost, not queued):

    B(N, A) = (A^N / N!) / sum_{x=0..N} (A^x / x!)

This module computes it with the numerically stable recursion

    B(0, A) = 1
    B(n, A) = A * B(n-1, A) / (n + A * B(n-1, A))

which avoids factorial overflow, plus the planner's inverse: the minimum
number of circuits for a target grade of service. That the recursion equals
the closed formula (verified in exact rational arithmetic) and reproduces
published Erlang-B traffic-table entries is registered as a claim and proven
by a committed evidence artifact. Vendoring carries that claim (and its
caveat) with it.

The model's assumptions (A. K. Erlang, 1917): Poisson arrivals, blocked calls
cleared (no retry, no queueing), infinite sources. Real traffic with retries
or bursty arrivals needs Erlang C or engineering margin on top.

Public API
----------
    erlang_b(circuits: int, offered_erlangs: float) -> float
    min_circuits(offered_erlangs: float, target_blocking: float) -> int

    >>> round(erlang_b(1, 1.0), 6)     # one circuit, 1 erlang: A/(1+A)
    0.5
    >>> min_circuits(5.092, 0.02)      # the classic 2% GoS row
    10
"""
from __future__ import annotations


class ErlangBError(ValueError):
    """Invalid traffic-engineering input (fail closed)."""


_MAX_CIRCUITS = 100_000


def _check_offered(offered_erlangs: float) -> float:
    if isinstance(offered_erlangs, bool) or \
            not isinstance(offered_erlangs, (int, float)):
        raise ErlangBError(f"offered load must be a number, "
                           f"got {offered_erlangs!r}")
    a = float(offered_erlangs)
    if a != a or a in (float("inf"), float("-inf")) or a < 0:
        raise ErlangBError(f"offered load must be finite and >= 0, "
                           f"got {offered_erlangs!r}")
    return a


def erlang_b(circuits: int, offered_erlangs: float) -> float:
    """Blocking probability B(N, A) for N circuits offered A erlangs.

    Computed with the standard stable recursion; exact for A == 0 (never
    blocks with at least one circuit) and monotone: more circuits always
    means less blocking, more traffic always means more.
    """
    if isinstance(circuits, bool) or not isinstance(circuits, int):
        raise ErlangBError(f"circuits must be an int, got {circuits!r}")
    if circuits < 0:
        raise ErlangBError(f"circuits must be >= 0, got {circuits}")
    if circuits > _MAX_CIRCUITS:
        raise ErlangBError(f"circuits capped at {_MAX_CIRCUITS} "
                           f"(got {circuits})")
    a = _check_offered(offered_erlangs)
    b = 1.0
    for n in range(1, circuits + 1):
        b = a * b / (n + a * b)
    return b


def min_circuits(offered_erlangs: float, target_blocking: float) -> int:
    """Minimum N with erlang_b(N, A) <= target_blocking (the planner's move).

    ``target_blocking`` must be in (0, 1). Runs the same recursion once,
    stopping at the first N that meets the grade of service.
    """
    a = _check_offered(offered_erlangs)
    if isinstance(target_blocking, bool) or \
            not isinstance(target_blocking, (int, float)):
        raise ErlangBError(f"target blocking must be a number, "
                           f"got {target_blocking!r}")
    t = float(target_blocking)
    if not 0.0 < t < 1.0:
        raise ErlangBError(f"target blocking must be in (0, 1), "
                           f"got {target_blocking!r}")
    if a == 0.0:
        return 0  # no offered traffic needs no circuits
    b = 1.0
    for n in range(1, _MAX_CIRCUITS + 1):
        b = a * b / (n + a * b)
        if b <= t:
            return n
    raise ErlangBError(
        f"no circuit count up to {_MAX_CIRCUITS} meets blocking "
        f"{target_blocking!r} for {offered_erlangs!r} erlangs")
