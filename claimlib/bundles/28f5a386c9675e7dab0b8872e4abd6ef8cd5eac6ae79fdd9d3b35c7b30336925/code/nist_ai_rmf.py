# SPDX-License-Identifier: Apache-2.0
"""NIST AI Risk Management Framework 1.0 core taxonomy + coverage scoring —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance in enterprise
environments. Encodes the AI RMF 1.0 Core (NIST AI 100-1, January 2023):
four functions — GOVERN, MAP, MEASURE, MANAGE — with their published
category counts (6/5/4/4, 19 total) and subcategory counts (19/18/22/13,
72 total), plus the seven characteristics of trustworthy AI the framework
articulates. Coverage scoring reports, per function and overall, how many
categories a programme declares addressed.

The RMF is voluntary and outcome-oriented: this module encodes its SHAPE
(so counts and gaps are exact), not the category prose — pair it with the
NIST AI RMF Playbook for the actionable text. Coverage of a category is
the caller's declaration, not an assessment. The caveat travels with the
claim.

Public API
----------
    FUNCTIONS: tuple[str, ...]
    CATEGORIES: dict[str, int]        # function -> published category count
    SUBCATEGORIES: dict[str, int]     # function -> published subcategory count
    TRUSTWORTHY: tuple[str, ...]      # the seven characteristics
    category_ids(function) -> list[str]        # e.g. ["GOVERN 1", ...]
    coverage(addressed: Iterable[str]) -> dict # per-function + overall

    >>> CATEGORIES["GOVERN"]
    6
    >>> coverage(["GOVERN 1", "MAP 3"])["addressed"]
    2
"""
from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction

FUNCTIONS = ("GOVERN", "MAP", "MEASURE", "MANAGE")

# Published category / subcategory counts per function (AI RMF 1.0 Core).
CATEGORIES = {"GOVERN": 6, "MAP": 5, "MEASURE": 4, "MANAGE": 4}
SUBCATEGORIES = {"GOVERN": 19, "MAP": 18, "MEASURE": 22, "MANAGE": 13}

# The seven characteristics of trustworthy AI (AI RMF 1.0, section 3).
TRUSTWORTHY = (
    "Valid and Reliable",
    "Safe",
    "Secure and Resilient",
    "Accountable and Transparent",
    "Explainable and Interpretable",
    "Privacy-Enhanced",
    "Fair - with Harmful Bias Managed",
)


class RMFError(ValueError):
    """Unknown function or category id (fail closed)."""


def category_ids(function: str) -> list:
    """The category identifiers of *function*: 'GOVERN 1' .. 'GOVERN 6'."""
    if function not in CATEGORIES:
        raise RMFError(f"unknown AI RMF function {function!r}; "
                       f"expected one of {FUNCTIONS}")
    return [f"{function} {i}" for i in range(1, CATEGORIES[function] + 1)]


def _all_ids() -> list:
    out = []
    for fn in FUNCTIONS:
        out.extend(category_ids(fn))
    return out


def coverage(addressed: Iterable[str]) -> dict:
    """Coverage of the 19 Core categories by a declared programme.

    ``addressed`` holds category ids ('GOVERN 1', 'MAP 3', ...). Unknown
    ids fail closed. Percentages are exact (computed as Fractions, rounded
    for display only).
    """
    have = set(addressed)
    valid = set(_all_ids())
    unknown = sorted(have - valid)
    if unknown:
        raise RMFError(f"unknown category id(s): {unknown}")
    per_function = {}
    for fn in FUNCTIONS:
        ids = set(category_ids(fn))
        done = len(ids & have)
        per_function[fn] = {
            "total": CATEGORIES[fn],
            "addressed": done,
            "coverage_pct": round(
                float(Fraction(done, CATEGORIES[fn]) * 100), 2),
            "gaps": sorted(ids - have),
        }
    total = sum(CATEGORIES.values())
    return {
        "functions": per_function,
        "total": total,
        "addressed": len(have),
        "coverage_pct": round(float(Fraction(len(have), total) * 100), 2),
    }
