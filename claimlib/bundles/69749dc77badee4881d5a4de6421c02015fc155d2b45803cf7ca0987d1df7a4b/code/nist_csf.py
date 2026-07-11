# SPDX-License-Identifier: Apache-2.0
"""NIST Cybersecurity Framework 2.0 coverage -- the six Functions and Categories.

A pre-verified claimlib code artifact for security governance. NIST CSF 2.0
organizes cyber risk into six Functions -- Govern, Identify, Protect, Detect,
Respond, Recover -- each decomposed into Categories. This module encodes that
taxonomy and scores how much of it a program covers. That the encoded Functions
and Categories match the published framework and that the coverage arithmetic is
correct is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    FUNCTIONS: dict[str, str]                          # code -> name
    CATEGORIES: dict[str, tuple[str, str]]             # id -> (function, name)
    function_of(category_id: str) -> str
    is_valid_category(category_id: str) -> bool
    coverage(implemented: Iterable[str]) -> dict       # per-function + overall

    >>> coverage(["GV.OC", "GV.RM"])["overall"]["implemented"]
    2
"""
from __future__ import annotations

from collections.abc import Iterable

# The six CSF 2.0 Functions (NIST CSWP 29).
FUNCTIONS = {
    "GV": "Govern",
    "ID": "Identify",
    "PR": "Protect",
    "DE": "Detect",
    "RS": "Respond",
    "RC": "Recover",
}

# The 22 CSF 2.0 Categories: id -> (function code, category name).
CATEGORIES = {
    "GV.OC": ("GV", "Organizational Context"),
    "GV.RM": ("GV", "Risk Management Strategy"),
    "GV.RR": ("GV", "Roles, Responsibilities, and Authorities"),
    "GV.PO": ("GV", "Policy"),
    "GV.OV": ("GV", "Oversight"),
    "GV.SC": ("GV", "Cybersecurity Supply Chain Risk Management"),
    "ID.AM": ("ID", "Asset Management"),
    "ID.RA": ("ID", "Risk Assessment"),
    "ID.IM": ("ID", "Improvement"),
    "PR.AA": ("PR", "Identity Management, Authentication, and Access Control"),
    "PR.AT": ("PR", "Awareness and Training"),
    "PR.DS": ("PR", "Data Security"),
    "PR.PS": ("PR", "Platform Security"),
    "PR.IR": ("PR", "Technology Infrastructure Resilience"),
    "DE.CM": ("DE", "Continuous Monitoring"),
    "DE.AE": ("DE", "Adverse Event Analysis"),
    "RS.MA": ("RS", "Incident Management"),
    "RS.AN": ("RS", "Incident Analysis"),
    "RS.CO": ("RS", "Incident Response Reporting and Communication"),
    "RS.MI": ("RS", "Incident Mitigation"),
    "RC.RP": ("RC", "Incident Recovery Plan Execution"),
    "RC.CO": ("RC", "Incident Recovery Communication"),
}


class CSFError(ValueError):
    """An unknown Function or Category id."""


def is_valid_category(category_id: str) -> bool:
    """Return True iff *category_id* is a CSF 2.0 Category id."""
    return category_id in CATEGORIES


def function_of(category_id: str) -> str:
    """Return the Function code that owns *category_id*."""
    if category_id not in CATEGORIES:
        raise CSFError(f"unknown CSF category {category_id!r}")
    return CATEGORIES[category_id][0]


def _categories_in(function_code: str) -> list[str]:
    return [cid for cid, (fn, _) in CATEGORIES.items() if fn == function_code]


def coverage(implemented: Iterable[str]) -> dict:
    """Return per-Function and overall coverage for the *implemented* categories."""
    impl = set(implemented)
    unknown = impl - set(CATEGORIES)
    if unknown:
        raise CSFError(f"unknown categories: {sorted(unknown)}")
    per_function = {}
    for code, name in FUNCTIONS.items():
        cats = _categories_in(code)
        done = sum(1 for c in cats if c in impl)
        per_function[code] = {
            "name": name,
            "total": len(cats),
            "implemented": done,
            "coverage": round(done / len(cats), 4),
        }
    total = len(CATEGORIES)
    done = len(impl)
    return {
        "functions": per_function,
        "overall": {"total": total, "implemented": done,
                    "coverage": round(done / total, 4)},
    }
