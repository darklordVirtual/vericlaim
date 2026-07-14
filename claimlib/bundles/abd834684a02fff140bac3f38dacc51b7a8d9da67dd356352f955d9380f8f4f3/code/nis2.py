# SPDX-License-Identifier: Apache-2.0
"""EU NIS2 Directive Article 21 coverage -- the ten minimum security measures.

A pre-verified claimlib code artifact for security compliance. Article 21(2) of
Directive (EU) 2022/2555 (NIS2) enumerates ten minimum cybersecurity risk-
management measures that essential and important entities must implement. This
module encodes those measures and scores coverage against them. That the encoded
measures match the Directive and that the coverage arithmetic is correct is
registered as a claim and proven by a committed evidence artifact.

Public API
----------
    MEASURES: dict[str, str]                       # "a".."j" -> measure text
    is_valid_measure(code: str) -> bool
    coverage(implemented: Iterable[str]) -> dict   # implemented / 10

    >>> coverage(["a", "b", "h", "j"])["implemented"]
    4
"""
from __future__ import annotations

from collections.abc import Iterable

# Article 21(2) (a)-(j) of Directive (EU) 2022/2555.
MEASURES = {
    "a": "Policies on risk analysis and information system security",
    "b": "Incident handling",
    "c": "Business continuity: backup management, disaster recovery, crisis management",
    "d": "Supply chain security",
    "e": "Security in acquisition, development and maintenance, incl. vulnerability handling and disclosure",
    "f": "Policies to assess the effectiveness of cybersecurity risk-management measures",
    "g": "Basic cyber hygiene practices and cybersecurity training",
    "h": "Policies and procedures on the use of cryptography and, where appropriate, encryption",
    "i": "Human resources security, access control policies and asset management",
    "j": "Multi-factor authentication, secured communications, and secured emergency communication systems",
}


class NIS2Error(ValueError):
    """An unknown Article 21(2) measure code."""


def is_valid_measure(code: str) -> bool:
    """Return True iff *code* is one of the ten Article 21(2) measure codes."""
    return code in MEASURES


def coverage(implemented: Iterable[str]) -> dict:
    """Return coverage of the ten Article 21(2) measures for *implemented*."""
    impl = set(implemented)
    unknown = impl - set(MEASURES)
    if unknown:
        raise NIS2Error(f"unknown measures: {sorted(unknown)}")
    total = len(MEASURES)
    done = len(impl)
    return {
        "total": total,
        "implemented": done,
        "missing": sorted(set(MEASURES) - impl),
        "coverage": round(done / total, 4),
    }
