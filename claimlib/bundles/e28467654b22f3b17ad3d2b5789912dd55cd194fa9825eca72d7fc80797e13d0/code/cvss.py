# SPDX-License-Identifier: Apache-2.0
"""CVSS v3.1 base-score scoring — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that it reproduces the published CVSS v3.1 reference
scores — is registered as a claim and proven by a committed evidence artifact;
vendoring this module carries that claim (and its caveat) with it.

Public API
----------
    parse_vector(vector: str) -> dict          # "CVSS:3.1/AV:N/..." -> metrics
    base_score(metrics: dict | str) -> float   # 0.0-10.0, rounded up to 1 dp
    severity(score: float) -> str              # qualitative band

Only the *base* metric group is implemented (no temporal/environmental
modifiers). The formula is the published CVSS v3.1 specification, section 7.

    >>> base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    9.8
    >>> severity(9.8)
    'critical'
"""
from __future__ import annotations

import math

# Published CVSS v3.1 metric weights (spec section 7.4).
AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
AC = {"L": 0.77, "H": 0.44}
PR_UNCHANGED = {"N": 0.85, "L": 0.62, "H": 0.27}
PR_CHANGED = {"N": 0.85, "L": 0.68, "H": 0.5}
UI = {"N": 0.85, "R": 0.62}
CIA = {"H": 0.56, "L": 0.22, "N": 0.0}
SCOPE = {"U", "C"}

_ORDER = ("AV", "AC", "PR", "UI", "S", "C", "I", "A")
_DOMAINS = {"AV": set(AV), "AC": set(AC), "PR": set(PR_UNCHANGED), "UI": set(UI),
            "S": SCOPE, "C": set(CIA), "I": set(CIA), "A": set(CIA)}


class CvssError(ValueError):
    """The CVSS vector string is malformed or uses an unknown metric value."""


def parse_vector(vector: str) -> dict:
    """Parse a ``CVSS:3.1/AV:N/AC:L/...`` base vector into a metrics dict.

    Accepts the eight base metrics in any order, with an optional ``CVSS:3.x``
    prefix. Raises :class:`CvssError` on unknown metrics or values, or on a
    missing base metric — fail closed rather than score a partial vector.
    """
    if not isinstance(vector, str) or not vector.strip():
        raise CvssError("empty CVSS vector")
    parts = [p for p in vector.strip().split("/") if p]
    metrics: dict[str, str] = {}
    for part in parts:
        if ":" not in part:
            raise CvssError(f"malformed component {part!r}")
        key, _, val = part.partition(":")
        if key == "CVSS":
            if val not in ("3.0", "3.1"):
                raise CvssError(f"unsupported CVSS version {val!r}")
            continue
        if key not in _DOMAINS:
            raise CvssError(f"unknown base metric {key!r}")
        if val not in _DOMAINS[key]:
            raise CvssError(f"invalid value {val!r} for metric {key}")
        if key in metrics:
            raise CvssError(f"duplicate base metric {key!r}")
        metrics[key] = val
    missing = [k for k in _ORDER if k not in metrics]
    if missing:
        raise CvssError(f"missing base metric(s): {', '.join(missing)}")
    return metrics


def _roundup(x: float) -> float:
    """CVSS v3.1 Roundup: least value with 1-dp precision >= x (spec 7.5)."""
    scaled = int(round(x * 100000))
    if scaled % 10000 == 0:
        return scaled / 100000.0
    return (math.floor(scaled / 10000) + 1) / 10.0


def base_score(metrics: dict | str) -> float:
    """CVSS v3.1 base score (0.0-10.0) for a metrics dict or vector string."""
    if isinstance(metrics, str):
        metrics = parse_vector(metrics)
    scope = metrics["S"]
    iss = 1 - (1 - CIA[metrics["C"]]) * (1 - CIA[metrics["I"]]) * (1 - CIA[metrics["A"]])
    if scope == "U":
        impact = 6.42 * iss
    else:
        impact = 7.52 * (iss - 0.029) - 3.25 * (iss - 0.02) ** 15
    pr = (PR_CHANGED if scope == "C" else PR_UNCHANGED)[metrics["PR"]]
    exploitability = 8.22 * AV[metrics["AV"]] * AC[metrics["AC"]] * pr * UI[metrics["UI"]]
    if impact <= 0:
        return 0.0
    if scope == "U":
        return _roundup(min(impact + exploitability, 10))
    return _roundup(min(1.08 * (impact + exploitability), 10))


def severity(score: float) -> str:
    """CVSS v3.1 qualitative severity rating for a base score."""
    if score <= 0:
        return "none"
    if score < 4.0:
        return "low"
    if score < 7.0:
        return "medium"
    if score < 9.0:
        return "high"
    return "critical"
