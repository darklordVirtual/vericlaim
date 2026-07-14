# SPDX-License-Identifier: Apache-2.0
"""Monetary-unit sampling (MUS / PPS) — selection and misstatement projection
per the AICPA Audit Sampling guide — reusable, claim-bound.

A pre-verified claimlib code artifact for audit. Monetary-unit sampling
treats every currency unit in a population as a sampling unit, so larger
items are proportionally more likely to be selected (probability-
proportional-to-size). This module implements the guide's fixed-interval
(systematic) selection and tainting-based projection:

    sampling interval  I = population book value / sample size
    selection points   start, start + I, start + 2I, ...   (1 <= start <= I)
    an item is selected when a selection point falls inside its cumulative
    book-value range; every item with book value >= I is ALWAYS selected
    (the "top stratum" — no selection start can skip over it).

    projection: a sampled item misstated by (book - audit) has tainting
    t = (book - audit) / book; non-top-stratum items project t * I each;
    top-stratum items project their ACTUAL misstatement.

All amounts are integer minor units; interval arithmetic is exact
(fractions.Fraction) — no float drift in a selection or a projection. That
the selection guarantees and the projection arithmetic hold exhaustively is
registered as a claim and proven by a committed evidence artifact.

Projection estimates the population misstatement from the sample; it is not
an opinion, and evaluating sufficiency remains the auditor's judgment.

Public API
----------
    interval(population_mu: int, sample_size: int) -> Fraction
    select(book_values_mu: list[int], sample_size: int, start_mu: int)
        -> list[int]                       # indices of selected items
    project(sampled: list[tuple[int, int]], interval_mu) -> int
        # [(book_mu, audit_mu)] -> projected misstatement, minor units

    >>> interval(50_000_000, 100)
    Fraction(500000, 1)
    >>> project([(300_000, 270_000)], Fraction(500_000))   # 10% tainting
    50000
"""
from __future__ import annotations

from fractions import Fraction


class MUSError(ValueError):
    """Invalid sampling input (fail closed)."""


def _check_int(x: int, name: str, minimum: int = 0) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise MUSError(f"{name} must be an int of minor units, got {x!r}")
    if x < minimum:
        raise MUSError(f"{name} must be >= {minimum}, got {x}")
    return x


def interval(population_mu: int, sample_size: int) -> Fraction:
    """The exact sampling interval: population / sample size."""
    p = _check_int(population_mu, "population_mu", 1)
    n = _check_int(sample_size, "sample_size", 1)
    if n > p:
        raise MUSError(f"sample size {n} exceeds population of {p} "
                       f"monetary units")
    return Fraction(p, n)


def select(book_values_mu: list, sample_size: int, start_mu: int) -> list:
    """Indices selected by fixed-interval PPS over *book_values_mu*.

    ``start_mu`` is the first selection point (1 <= start_mu <= interval).
    Zero-value items can never be selected (they contain no monetary units);
    negative book values are rejected — the guide samples them separately.
    """
    if not isinstance(book_values_mu, list) or not book_values_mu:
        raise MUSError("book_values_mu must be a non-empty list")
    total = 0
    for i, v in enumerate(book_values_mu):
        _check_int(v, f"book_values_mu[{i}]")
        total += v
    if total == 0:
        raise MUSError("population book value is zero")
    step = interval(total, sample_size)
    start = _check_int(start_mu, "start_mu", 1)
    if start > step:
        raise MUSError(f"start_mu must be within the first interval "
                       f"(<= {step}), got {start}")
    selected = []
    point = Fraction(start)
    cumulative = 0
    for i, v in enumerate(book_values_mu):
        upper = cumulative + v
        hit = False
        while point <= upper:
            if point > cumulative:
                hit = True
            point += step
        if hit:
            selected.append(i)
        cumulative = upper
    return selected


def project(sampled: list, interval_mu) -> int:
    """Projected misstatement (minor units) from [(book_mu, audit_mu)] pairs.

    Non-top-stratum items (book < interval) project tainting * interval,
    exactly; top-stratum items project their actual misstatement. The result
    is the banker's-rounded sum. Overstatements are positive.
    """
    if not isinstance(sampled, list):
        raise MUSError("sampled must be a list of (book_mu, audit_mu) pairs")
    step = Fraction(interval_mu)
    if step <= 0:
        raise MUSError(f"interval must be > 0, got {interval_mu!r}")
    total = Fraction(0)
    for k, pair in enumerate(sampled):
        if not isinstance(pair, tuple) or len(pair) != 2:
            raise MUSError(f"sampled[{k}] must be a (book_mu, audit_mu) "
                           f"tuple, got {pair!r}")
        book, audit = pair
        _check_int(book, f"sampled[{k}].book_mu", 1)
        _check_int(audit, f"sampled[{k}].audit_mu")
        misstatement = book - audit
        if book >= step:                       # top stratum: actual amount
            total += misstatement
        else:                                  # tainting * interval, exact
            total += Fraction(misstatement, book) * step
    return round(total)
