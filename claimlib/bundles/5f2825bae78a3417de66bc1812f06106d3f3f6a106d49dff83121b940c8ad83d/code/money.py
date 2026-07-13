# SPDX-License-Identifier: Apache-2.0
"""Money arithmetic: banker's rounding + cent-exact allocation.

A pre-verified claimlib code artifact. Two properties make money math error
prone: how you round a half (float ``round`` and naive ``round half up`` both
bias totals), and how you split an amount into parts without losing or minting
a minor unit. This module rounds with ROUND_HALF_EVEN (banker's rounding, the
IEEE 754 / accounting default) and allocates by the *largest remainder* method,
whose defining invariant -- the parts sum EXACTLY back to the total -- is
registered as a claim and proven by a committed evidence artifact.

Work is done in integer minor units (cents, oere, pence) to avoid binary
floating point entirely; ``round_money`` uses :class:`decimal.Decimal`.

Public API
----------
    allocate(total_minor: int, weights: Sequence[int]) -> list[int]
    split_evenly(total_minor: int, parts: int) -> list[int]
    round_money(value, places: int = 2) -> Decimal   # ROUND_HALF_EVEN

    >>> allocate(100, [1, 1, 1])       # 100 cents, three equal shares
    [34, 33, 33]
    >>> sum(allocate(100, [1, 1, 1]))  # never loses a cent
    100
"""
from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal, ROUND_HALF_EVEN


class MoneyError(ValueError):
    """Invalid money argument (negative total, empty/negative weights, ...)."""


def allocate(total_minor: int, weights: Sequence[int]) -> list[int]:
    """Split *total_minor* into integer parts proportional to *weights*.

    Uses the largest-remainder (Hamilton) method: each part gets the floor of
    its exact proportional share, then the leftover minor units are handed out
    one each to the parts with the largest fractional remainders, ties broken
    by original position. The parts always sum EXACTLY to *total_minor*.
    """
    if not isinstance(total_minor, int) or isinstance(total_minor, bool):
        raise MoneyError("total_minor must be an int number of minor units")
    if total_minor < 0:
        raise MoneyError("total_minor must be non-negative")
    if len(weights) == 0:
        raise MoneyError("weights must be non-empty")
    if any((not isinstance(w, int)) or isinstance(w, bool) or w < 0 for w in weights):
        raise MoneyError("weights must be non-negative ints")
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise MoneyError("weights must not all be zero")

    numerators = [total_minor * w for w in weights]
    base = [num // weight_sum for num in numerators]
    remainder = total_minor - sum(base)
    # Fractional part of each exact share, as an integer numerator over weight_sum.
    order = sorted(range(len(weights)),
                   key=lambda i: (numerators[i] - base[i] * weight_sum, -i),
                   reverse=True)
    for i in range(remainder):
        base[order[i]] += 1
    return base


def split_evenly(total_minor: int, parts: int) -> list[int]:
    """Split *total_minor* into *parts* as-equal-as-possible integer shares."""
    if not isinstance(parts, int) or isinstance(parts, bool) or parts <= 0:
        raise MoneyError("parts must be a positive int")
    return allocate(total_minor, [1] * parts)


def round_money(value, places: int = 2) -> Decimal:
    """Round *value* to *places* decimals with banker's rounding (HALF_EVEN).

    *value* may be a str, int, or Decimal. Pass strings (e.g. "2.675") rather
    than floats to avoid binary-float representation error before rounding.
    """
    if not isinstance(places, int) or isinstance(places, bool) or places < 0:
        raise MoneyError("places must be a non-negative int")
    quantum = Decimal(1).scaleb(-places)
    return Decimal(str(value)).quantize(quantum, rounding=ROUND_HALF_EVEN)
