# SPDX-License-Identifier: Apache-2.0
"""ISO/IEC 42001:2023 AI management system structure + Statement of
Applicability scoring — reusable, claim-bound.

A pre-verified claimlib code artifact for AI governance in enterprise
environments. ISO/IEC 42001:2023 is the first certifiable AI management
system standard (AIMS). This module encodes its published shape: the
harmonized management-system clauses 4-10 (Context, Leadership, Planning,
Support, Operation, Performance evaluation, Improvement) and normative
Annex A — 38 reference controls organized into 9 control objectives
(A.2-A.10, from AI policies through third-party relationships) — plus
Statement-of-Applicability (SoA) accounting at the control-group level.

An SoA declares, per control, applicable/not-applicable with justification;
this module keeps the arithmetic honest (declared counts can never exceed
the group's published control count, percentages are exact). It encodes
the standard's structure, not its licensed text, and scoring a declaration
is not certification — an accredited audit is. The caveat travels with the
claim.

Public API
----------
    CLAUSES: dict[int, str]                # 4..10 -> official title
    ANNEX_A_GROUPS: dict[str, dict]        # "A.2".."A.10" -> name, controls
    ANNEX_A_TOTAL: int                     # 38
    soa(applicable: dict[str, int]) -> dict

    >>> ANNEX_A_TOTAL
    38
    >>> soa({"A.2": 2})["applicable"]
    2
"""
from __future__ import annotations

from fractions import Fraction

CLAUSES = {
    4: "Context of the organization",
    5: "Leadership",
    6: "Planning",
    7: "Support",
    8: "Operation",
    9: "Performance evaluation",
    10: "Improvement",
}

# Annex A control objectives (groups) with their published control counts.
# 38 controls across A.2-A.10 (ISO/IEC 42001:2023, Annex A, normative).
ANNEX_A_GROUPS = {
    "A.2": {"name": "Policies related to AI", "controls": 3},
    "A.3": {"name": "Internal organization", "controls": 2},
    "A.4": {"name": "Resources for AI systems", "controls": 5},
    "A.5": {"name": "Assessing impacts of AI systems", "controls": 4},
    "A.6": {"name": "AI system life cycle", "controls": 9},
    "A.7": {"name": "Data for AI systems", "controls": 5},
    "A.8": {"name": "Information for interested parties of AI systems",
            "controls": 4},
    "A.9": {"name": "Use of AI systems", "controls": 3},
    "A.10": {"name": "Third-party and customer relationships",
             "controls": 3},
}

ANNEX_A_TOTAL = sum(g["controls"] for g in ANNEX_A_GROUPS.values())


class AIMSError(ValueError):
    """Unknown clause/group or impossible SoA declaration (fail closed)."""


def clause_title(clause: int) -> str:
    """Official title of management-system clause 4..10."""
    if isinstance(clause, bool) or clause not in CLAUSES:
        raise AIMSError(f"clause must be 4..10, got {clause!r}")
    return CLAUSES[clause]


def soa(applicable: dict) -> dict:
    """Statement-of-Applicability accounting at the group level.

    ``applicable`` maps group ids ("A.2"..."A.10") to the number of that
    group's controls declared applicable. A count above the group's
    published control count is impossible and fails closed; omitted groups
    count as 0 applicable.
    """
    if not isinstance(applicable, dict):
        raise AIMSError("applicable must be a dict of group -> count")
    unknown = sorted(set(applicable) - set(ANNEX_A_GROUPS))
    if unknown:
        raise AIMSError(f"unknown Annex A group(s): {unknown}")
    per_group = {}
    total_applicable = 0
    for gid, meta in ANNEX_A_GROUPS.items():
        declared = applicable.get(gid, 0)
        if isinstance(declared, bool) or not isinstance(declared, int) \
                or declared < 0:
            raise AIMSError(f"{gid}: applicable count must be an int >= 0, "
                            f"got {declared!r}")
        if declared > meta["controls"]:
            raise AIMSError(
                f"{gid} ({meta['name']}) has {meta['controls']} controls; "
                f"cannot declare {declared} applicable")
        total_applicable += declared
        per_group[gid] = {
            "name": meta["name"],
            "controls": meta["controls"],
            "applicable": declared,
            "excluded": meta["controls"] - declared,
        }
    return {
        "groups": per_group,
        "controls_total": ANNEX_A_TOTAL,
        "applicable": total_applicable,
        "excluded": ANNEX_A_TOTAL - total_applicable,
        "applicable_pct": round(
            float(Fraction(total_applicable, ANNEX_A_TOTAL) * 100), 2),
    }
