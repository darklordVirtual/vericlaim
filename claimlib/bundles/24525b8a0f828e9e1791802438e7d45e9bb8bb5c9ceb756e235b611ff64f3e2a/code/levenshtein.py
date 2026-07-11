# SPDX-License-Identifier: Apache-2.0
"""Levenshtein edit distance -- the minimum single-character edits between strings.

A pre-verified claimlib code artifact: a reusable, stdlib-only building block that
computes the classic Wagner-Fischer edit distance (insertions, deletions,
substitutions each cost 1). That it reproduces the published textbook distances
AND satisfies the metric axioms (identity, symmetry, triangle inequality) over a
fixed battery is registered as a claim and proven by a committed evidence
artifact. Vendoring carries that claim (and caveat).

Public API
----------
    distance(a: str, b: str) -> int

    >>> distance("kitten", "sitting")
    3
    >>> distance("flaw", "lawn")
    2
"""
from __future__ import annotations


class LevenshteinError(ValueError):
    """An argument was not a string."""


def distance(a: str, b: str) -> int:
    """Return the Levenshtein edit distance between *a* and *b*.

    Uses the two-row dynamic-programming formulation: O(len(a) * len(b)) time,
    O(min(len(a), len(b))) space.
    """
    if not isinstance(a, str) or not isinstance(b, str):
        raise LevenshteinError("both arguments must be strings")
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a                       # keep the inner row over the shorter string
    if len(b) == 0:
        return len(a)

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i] + [0] * len(b)
        for j, cb in enumerate(b, start=1):
            insert_cost = current[j - 1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (ca != cb)
            current[j] = min(insert_cost, delete_cost, replace_cost)
        previous = current
    return previous[len(b)]
