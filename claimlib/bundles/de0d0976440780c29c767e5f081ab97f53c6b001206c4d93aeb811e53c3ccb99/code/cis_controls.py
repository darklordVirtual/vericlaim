# SPDX-License-Identifier: Apache-2.0
"""CIS Critical Security Controls v8.1 coverage -- 18 Controls, 153 Safeguards.

A pre-verified claimlib code artifact for security governance. The CIS Critical
Security Controls Version 8.1 (Center for Internet Security, June 2024) is a
prioritized set of 18 Controls decomposed into 153 Safeguards. Each Safeguard
is assigned to one of three cumulative Implementation Groups: IG1 ("essential
cyber hygiene", 56 Safeguards), IG2 (adds 74, for 130), and IG3 (adds 23, for
all 153). This module encodes the 18 Controls with their official titles and
per-IG Safeguard counts, and scores control-level and safeguard-weighted
coverage against them. That the encoded taxonomy matches the published v8.1
counts and that the coverage arithmetic is correct is registered as a claim and
proven by a committed evidence artifact.

Public API
----------
    CONTROLS: dict[int, tuple[str, int, int, int, int]]
        # number -> (title, total safeguards, IG1, IG2, IG3); IG counts are
        # CUMULATIVE (IG2 includes IG1's safeguards, IG3 includes IG2's).
    IMPLEMENTATION_GROUPS: tuple[str, str, str]      # ("IG1", "IG2", "IG3")
    is_valid_control(number: int) -> bool
    title_of(number: int) -> str
    safeguard_counts(number: int) -> dict            # per-control counts
    ig_totals() -> dict                              # framework-wide totals
    coverage(implemented: Iterable[int]) -> dict     # controls + per-IG
    gaps(implemented: Iterable[int]) -> list[dict]   # missing controls

    >>> ig_totals()["IG1"]
    56
    >>> coverage([1, 2])["controls"]["implemented"]
    2
"""
from __future__ import annotations

from collections.abc import Iterable

# The three Implementation Groups, in ascending (cumulative) order.
IMPLEMENTATION_GROUPS = ("IG1", "IG2", "IG3")

# The 18 CIS Controls v8.1: number -> (title, total, IG1, IG2, IG3).
# Titles and counts are transcribed from the CIS Critical Security Controls
# v8.1 guide (June 2024), per-control "Safeguards: N | IG1: a/N | IG2: b/N |
# IG3: N/N" headers. IG counts are cumulative; IG3 always equals the total.
CONTROLS = {
    1: ("Inventory and Control of Enterprise Assets", 5, 2, 4, 5),
    2: ("Inventory and Control of Software Assets", 7, 3, 6, 7),
    3: ("Data Protection", 14, 6, 12, 14),
    4: ("Secure Configuration of Enterprise Assets and Software", 12, 7, 11, 12),
    5: ("Account Management", 6, 4, 6, 6),
    6: ("Access Control Management", 8, 5, 7, 8),
    7: ("Continuous Vulnerability Management", 7, 4, 7, 7),
    8: ("Audit Log Management", 12, 3, 11, 12),
    9: ("Email and Web Browser Protections", 7, 2, 6, 7),
    10: ("Malware Defenses", 7, 3, 7, 7),
    11: ("Data Recovery", 5, 4, 5, 5),
    12: ("Network Infrastructure Management", 8, 1, 7, 8),
    13: ("Network Monitoring and Defense", 11, 0, 6, 11),
    14: ("Security Awareness and Skills Training", 9, 8, 9, 9),
    15: ("Service Provider Management", 7, 1, 4, 7),
    16: ("Application Software Security", 14, 0, 11, 14),
    17: ("Incident Response Management", 9, 3, 8, 9),
    18: ("Penetration Testing", 5, 0, 3, 5),
}


class CISError(ValueError):
    """An unknown CIS Control number or malformed input."""


def _check_control(number: int) -> int:
    """Validate *number* as a CIS Control number (fail closed)."""
    # bool is a subclass of int; True would silently alias Control 1.
    if isinstance(number, bool) or not isinstance(number, int):
        raise CISError(f"control number must be an int, got {number!r}")
    if number not in CONTROLS:
        raise CISError(f"unknown CIS Control number: {number!r} (valid: 1..18)")
    return number


def is_valid_control(number: int) -> bool:
    """Return True iff *number* is a CIS Control number (1..18)."""
    return (not isinstance(number, bool) and isinstance(number, int)
            and number in CONTROLS)


def title_of(number: int) -> str:
    """Return the official v8.1 title of Control *number*."""
    return CONTROLS[_check_control(number)][0]


def safeguard_counts(number: int) -> dict:
    """Return Control *number*'s safeguard counts (IG counts cumulative)."""
    _, total, ig1, ig2, ig3 = CONTROLS[_check_control(number)]
    return {"total": total, "IG1": ig1, "IG2": ig2, "IG3": ig3}


def ig_totals() -> dict:
    """Return framework-wide safeguard totals, summed over all 18 Controls.

    For CIS Controls v8.1 this is {"total": 153, "IG1": 56, "IG2": 130,
    "IG3": 153} -- the published counts, derived here by summation so the
    evidence can check the derivation against the published numbers.
    """
    out = {"total": 0, "IG1": 0, "IG2": 0, "IG3": 0}
    for number in sorted(CONTROLS):
        _, total, ig1, ig2, ig3 = CONTROLS[number]
        out["total"] += total
        out["IG1"] += ig1
        out["IG2"] += ig2
        out["IG3"] += ig3
    return out


def _validated_set(implemented: Iterable[int]) -> set:
    impl = set()
    for number in implemented:
        impl.add(_check_control(number))
    return impl


def coverage(implemented: Iterable[int]) -> dict:
    """Score a declared-implemented set of Control numbers against v8.1.

    *implemented* lists the Controls the enterprise declares fully
    implemented (all of that Control's Safeguards). Returns control-level
    coverage (implemented / 18, with the sorted missing list) and
    safeguard-weighted coverage per Implementation Group: the sum of the
    implemented Controls' IG-level safeguard counts over that IG's
    framework-wide total (56 / 130 / 153). Fractions rounded to 4 dp.
    """
    impl = _validated_set(implemented)
    totals = ig_totals()

    done = len(impl)
    n = len(CONTROLS)
    result = {
        "controls": {
            "total": n,
            "implemented": done,
            "missing": sorted(set(CONTROLS) - impl),
            "coverage": round(done / n, 4),
        },
        "safeguards": {},
    }
    for i, ig in enumerate(IMPLEMENTATION_GROUPS):
        got = sum(CONTROLS[c][2 + i] for c in impl)
        result["safeguards"][ig] = {
            "total": totals[ig],
            "implemented": got,
            "coverage": round(got / totals[ig], 4),
        }
    return result


def gaps(implemented: Iterable[int]) -> list[dict]:
    """List the Controls NOT in *implemented*, ascending by number.

    Each entry carries the Control's number, official title and safeguard
    counts, so the gap list doubles as a remediation worksheet.
    """
    impl = _validated_set(implemented)
    out = []
    for number in sorted(set(CONTROLS) - impl):
        title, total, ig1, ig2, ig3 = CONTROLS[number]
        out.append({"control": number, "title": title, "safeguards": total,
                    "IG1": ig1, "IG2": ig2, "IG3": ig3})
    return out
