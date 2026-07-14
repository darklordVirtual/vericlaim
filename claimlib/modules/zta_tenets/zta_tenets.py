# SPDX-License-Identifier: Apache-2.0
"""NIST SP 800-207 Zero Trust tenets — taxonomy + coverage — reusable,
claim-bound.

A pre-verified claimlib code artifact for AI assurance and enterprise
architecture. NIST SP 800-207 (2020) states seven tenets of zero trust —
the design posture in which no implicit trust is granted by network
location, and every access is evaluated per session against dynamic
policy. Agentic AI deployments inherit exactly this frame: every agent,
tool endpoint and data source is a resource; every call is an access
decision.

This module encodes the seven tenets (short labels faithful to section
2.1) and scores declared adherence. The tenets are an ideal-state design
goal — SP 800-207 itself notes a pure implementation may not be possible;
coverage is the caller's declaration. The caveat travels with the claim.

Public API
----------
    TENETS: dict[int, str]           # 1..7 -> tenet label
    coverage(adhered: Iterable[int]) -> dict

    >>> len(TENETS)
    7
"""
from __future__ import annotations

from collections.abc import Iterable
from fractions import Fraction

# The seven tenets of zero trust, NIST SP 800-207 section 2.1 (short labels).
TENETS = {
    1: "All data sources and computing services are considered resources",
    2: "All communication is secured regardless of network location",
    3: "Access to individual enterprise resources is granted on a "
       "per-session basis",
    4: "Access to resources is determined by dynamic policy, including "
       "observable client identity, application/service, and asset state",
    5: "The enterprise monitors and measures the integrity and security "
       "posture of all owned and associated assets",
    6: "All resource authentication and authorization are dynamic and "
       "strictly enforced before access is allowed",
    7: "The enterprise collects as much information as possible about the "
       "current state of assets, network infrastructure and communications "
       "and uses it to improve its security posture",
}


class ZTAError(ValueError):
    """Unknown tenet number (fail closed)."""


def coverage(adhered: Iterable[int]) -> dict:
    """Coverage of the seven tenets by a declared architecture."""
    have = set(adhered)
    unknown = sorted(t for t in have
                     if isinstance(t, bool) or t not in TENETS)
    if unknown:
        raise ZTAError(f"unknown tenet(s): {unknown} — expected 1..7")
    gaps = sorted(set(TENETS) - have)
    return {
        "tenets_total": len(TENETS),
        "adhered": len(have),
        "coverage_pct": round(float(Fraction(len(have), len(TENETS)) * 100),
                              2),
        "gaps": gaps,
    }
