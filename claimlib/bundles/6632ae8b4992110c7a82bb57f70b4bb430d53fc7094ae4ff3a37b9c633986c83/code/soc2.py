# SPDX-License-Identifier: Apache-2.0
"""SOC 2 Trust Services Criteria coverage (AICPA TSP section 100).

A pre-verified claimlib code artifact for compliance & audit readiness. A SOC 2
report is organized around five Trust Services Categories -- Security (the Common
Criteria), Availability, Processing Integrity, Confidentiality, and Privacy --
and Security is itself the nine Common Criteria series CC1..CC9. This module
encodes that taxonomy and scores coverage. That the encoded categories and Common
Criteria match the AICPA framework and that the coverage arithmetic is correct is
registered as a claim and proven by a committed evidence artifact.

Public API
----------
    CATEGORIES: dict[str, str]                  # code -> name (5 TSC categories)
    COMMON_CRITERIA: dict[str, str]             # CC1..CC9 -> name
    is_valid_criterion(code: str) -> bool       # a CC1..CC9 series code
    coverage(implemented: Iterable[str]) -> dict  # over the 9 Common Criteria

    >>> coverage(["CC1", "CC2"])["implemented"]
    2
"""
from __future__ import annotations

from collections.abc import Iterable

# The five Trust Services Categories (Security is always in scope via the CC).
CATEGORIES = {
    "SEC": "Security (Common Criteria)",
    "AVL": "Availability",
    "PIN": "Processing Integrity",
    "CON": "Confidentiality",
    "PRI": "Privacy",
}

# The nine Common Criteria series (the Security category).
COMMON_CRITERIA = {
    "CC1": "Control Environment",
    "CC2": "Communication and Information",
    "CC3": "Risk Assessment",
    "CC4": "Monitoring Activities",
    "CC5": "Control Activities",
    "CC6": "Logical and Physical Access Controls",
    "CC7": "System Operations",
    "CC8": "Change Management",
    "CC9": "Risk Mitigation",
}


class SOC2Error(ValueError):
    """An unknown Trust Services Category or Common Criteria code."""


def is_valid_criterion(code: str) -> bool:
    """Return True iff *code* is a Common Criteria series code (CC1..CC9)."""
    return code in COMMON_CRITERIA


def coverage(implemented: Iterable[str]) -> dict:
    """Return coverage of the nine Common Criteria for *implemented*."""
    impl = set(implemented)
    unknown = impl - set(COMMON_CRITERIA)
    if unknown:
        raise SOC2Error(f"unknown Common Criteria: {sorted(unknown)}")
    total = len(COMMON_CRITERIA)
    done = len(impl)
    return {
        "total": total,
        "implemented": done,
        "missing": sorted(set(COMMON_CRITERIA) - impl),
        "coverage": round(done / total, 4),
    }
