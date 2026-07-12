# SPDX-License-Identifier: Apache-2.0
"""PCI DSS v4.0 coverage -- the twelve requirements across six goals.

A pre-verified claimlib code artifact for payment-card compliance & audit. The
Payment Card Industry Data Security Standard v4.0 groups twelve requirements
under six goals. This module encodes that structure and scores coverage. That the
encoded requirements and their goal grouping match the standard and that the
coverage arithmetic is correct is registered as a claim and proven by a committed
evidence artifact.

Public API
----------
    GOALS: dict[int, str]                        # 1..6 -> goal name
    REQUIREMENTS: dict[int, tuple[int, str]]     # 1..12 -> (goal, title)
    goal_of(requirement: int) -> int
    is_valid_requirement(requirement: int) -> bool
    coverage(implemented: Iterable[int]) -> dict  # per-goal + overall over 12

    >>> coverage([1, 3, 12])["overall"]["implemented"]
    3
"""
from __future__ import annotations

from collections.abc import Iterable

GOALS = {
    1: "Build and Maintain a Secure Network and Systems",
    2: "Protect Account Data",
    3: "Maintain a Vulnerability Management Program",
    4: "Implement Strong Access Control Measures",
    5: "Regularly Monitor and Test Networks",
    6: "Maintain an Information Security Policy",
}

# requirement number -> (goal, title)
REQUIREMENTS = {
    1: (1, "Install and maintain network security controls"),
    2: (1, "Apply secure configurations to all system components"),
    3: (2, "Protect stored account data"),
    4: (2, "Protect cardholder data with strong cryptography during transmission"),
    5: (3, "Protect all systems and networks from malicious software"),
    6: (3, "Develop and maintain secure systems and software"),
    7: (4, "Restrict access to system components and cardholder data by business need to know"),
    8: (4, "Identify users and authenticate access to system components"),
    9: (4, "Restrict physical access to cardholder data"),
    10: (5, "Log and monitor all access to system components and cardholder data"),
    11: (5, "Test security of systems and networks regularly"),
    12: (6, "Support information security with organizational policies and programs"),
}


class PCIDSSError(ValueError):
    """An unknown PCI DSS requirement or goal number."""


def is_valid_requirement(requirement: int) -> bool:
    """Return True iff *requirement* is a PCI DSS requirement number (1..12)."""
    return isinstance(requirement, int) and not isinstance(requirement, bool) \
        and requirement in REQUIREMENTS


def goal_of(requirement: int) -> int:
    """Return the goal (1..6) that owns *requirement*."""
    if not is_valid_requirement(requirement):
        raise PCIDSSError(f"unknown requirement {requirement!r}")
    return REQUIREMENTS[requirement][0]


def coverage(implemented: Iterable[int]) -> dict:
    """Return per-goal and overall coverage for the *implemented* requirements."""
    impl = set(implemented)
    unknown = {r for r in impl if not is_valid_requirement(r)}
    if unknown:
        raise PCIDSSError(f"unknown requirements: {sorted(unknown)}")
    per_goal = {}
    for goal, name in GOALS.items():
        reqs = [r for r, (g, _) in REQUIREMENTS.items() if g == goal]
        done = sum(1 for r in reqs if r in impl)
        per_goal[goal] = {"name": name, "total": len(reqs), "implemented": done,
                          "coverage": round(done / len(reqs), 4)}
    total = len(REQUIREMENTS)
    done = len(impl)
    return {
        "goals": per_goal,
        "overall": {"total": total, "implemented": done,
                    "coverage": round(done / total, 4)},
    }
