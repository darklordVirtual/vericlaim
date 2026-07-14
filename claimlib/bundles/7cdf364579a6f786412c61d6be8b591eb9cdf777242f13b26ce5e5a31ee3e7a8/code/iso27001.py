# SPDX-License-Identifier: Apache-2.0
"""ISO/IEC 27001:2022 Annex A coverage -- the 93 controls in four themes.

A pre-verified claimlib code artifact for compliance & audit. The 2022 revision
of ISO/IEC 27001 restructured Annex A into 93 controls grouped in four themes:
Organizational (A.5, 37 controls), People (A.6, 8), Physical (A.7, 14), and
Technological (A.8, 34). This module encodes that structure and scores coverage.
That the encoded themes and their control counts match the standard (they sum to
93) and that the coverage arithmetic is correct is registered as a claim and
proven by a committed evidence artifact.

Public API
----------
    THEMES: dict[str, tuple[str, int]]           # "A.5" -> (name, control_count)
    theme_of(control_id: str) -> str             # "A.8.5" -> "A.8"
    is_valid_control(control_id: str) -> bool
    coverage(implemented: Iterable[str]) -> dict  # per-theme + overall over 93

    >>> coverage(["A.5.1", "A.8.5"])["overall"]["implemented"]
    2
"""
from __future__ import annotations

import re
from collections.abc import Iterable

# Annex A:2022 themes: prefix -> (name, number of controls).
THEMES = {
    "A.5": ("Organizational", 37),
    "A.6": ("People", 8),
    "A.7": ("Physical", 14),
    "A.8": ("Technological", 34),
}
_CONTROL_RE = re.compile(r"^(A\.[5678])\.(\d+)$")


class ISO27001Error(ValueError):
    """An unknown theme or out-of-range control id."""


def theme_of(control_id: str) -> str:
    """Return the theme prefix (e.g. 'A.8') that owns *control_id*."""
    if not is_valid_control(control_id):
        raise ISO27001Error(f"invalid control id {control_id!r}")
    return _CONTROL_RE.match(control_id).group(1)


def is_valid_control(control_id: str) -> bool:
    """Return True iff *control_id* is a valid Annex A:2022 control (in range)."""
    if not isinstance(control_id, str):
        return False
    m = _CONTROL_RE.match(control_id)
    if not m:
        return False
    prefix, num = m.group(1), int(m.group(2))
    return prefix in THEMES and 1 <= num <= THEMES[prefix][1]


def coverage(implemented: Iterable[str]) -> dict:
    """Return per-theme and overall coverage for the *implemented* controls."""
    impl = set(implemented)
    invalid = {c for c in impl if not is_valid_control(c)}
    if invalid:
        raise ISO27001Error(f"invalid controls: {sorted(invalid)}")
    per_theme = {}
    for prefix, (name, count) in THEMES.items():
        done = sum(1 for c in impl if _CONTROL_RE.match(c).group(1) == prefix)
        per_theme[prefix] = {"name": name, "total": count, "implemented": done,
                             "coverage": round(done / count, 4)}
    total = sum(c for _, c in THEMES.values())
    done = len(impl)
    return {
        "themes": per_theme,
        "overall": {"total": total, "implemented": done,
                    "coverage": round(done / total, 4)},
    }
