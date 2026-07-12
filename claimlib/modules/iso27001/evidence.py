# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ISO27001-001 -- the encoded Annex A:2022 themes and
control counts match the standard and the coverage arithmetic is correct.

The structure is INDEPENDENTLY KNOWN from ISO/IEC 27001:2022 Annex A: four themes
with 37 (Organizational), 8 (People), 14 (Physical), and 34 (Technological)
controls that sum to 93. The evidence checks the four theme names and counts,
that they total 93, control-id validation (range + prefix), and hand-verified
coverage (a full theme -> 1.0; a known subset -> its exact fraction; overall =
implemented/93). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (iso27001.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from iso27001 import THEMES, theme_of, is_valid_control, coverage  # noqa: E402
from _util import emit  # noqa: E402

EXPECTED = {"A.5": ("Organizational", 37), "A.6": ("People", 8),
            "A.7": ("Physical", 14), "A.8": ("Technological", 34)}


def run() -> dict:
    themes_ok = int(THEMES == EXPECTED)
    total_is_93 = int(sum(c for _, c in THEMES.values()) == 93)

    validation_checks = [
        is_valid_control("A.5.1") is True,
        is_valid_control("A.8.34") is True,
        is_valid_control("A.6.9") is False,       # People has only 8
        is_valid_control("A.9.1") is False,       # no A.9 theme
        is_valid_control("A.5.0") is False,
        theme_of("A.8.5") == "A.8",
    ]
    validation_correct = sum(int(c) for c in validation_checks)

    people = [f"A.6.{i}" for i in range(1, 9)]     # all 8 People controls
    coverage_checks = [
        coverage(people)["themes"]["A.6"]["coverage"] == 1.0,
        coverage(people)["themes"]["A.5"]["coverage"] == 0.0,
        coverage(["A.5.1", "A.5.2"])["themes"]["A.5"]["coverage"] == round(2 / 37, 4),
        coverage([])["overall"]["implemented"] == 0,
        coverage(["A.5.1", "A.6.1", "A.7.1", "A.8.1"])["overall"]["implemented"] == 4,
    ]
    coverage_correct = sum(int(c) for c in coverage_checks)

    checks = 2 + len(validation_checks) + len(coverage_checks)
    matched = themes_ok + total_is_93 + validation_correct + coverage_correct
    return {
        "schema": "claimlib_iso27001_v1",
        "module": "iso27001",
        "n_themes": len(THEMES),
        "n_controls": sum(c for _, c in THEMES.values()),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "themes_ok": bool(themes_ok),
        "validation_correct": validation_correct,
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "iso27001.json", obj,
         script="python3 claimlib/modules/iso27001/evidence.py")
    # claim:CLAIM-LIB-ISO27001-001 checks_matched
    # The 4 themes, the 93-control total, 6 validation and 5 coverage checks all
    # hold, so checks_matched = 13 and mismatches = 0.
    print(f"iso27001: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['n_themes']} themes, {obj['n_controls']} controls); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
