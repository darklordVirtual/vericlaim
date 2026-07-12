# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PCI-DSS-001 -- the encoded PCI DSS v4.0 requirements and
goal grouping match the standard and the coverage arithmetic is correct.

The structure is INDEPENDENTLY KNOWN from PCI DSS v4.0: twelve requirements under
six goals, with requirements 1-2 under goal 1, 3-4 under goal 2, 5-6 under goal 3,
7-9 under goal 4, 10-11 under goal 5, and 12 under goal 6. The evidence checks the
six goals, the twelve requirements, the goal-of mapping, and hand-verified
coverage values. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (pci_dss.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from pci_dss import GOALS, REQUIREMENTS, goal_of, coverage  # noqa: E402
from _util import emit  # noqa: E402

EXPECTED_GOAL = {1: 1, 2: 1, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 4, 10: 5, 11: 5, 12: 6}


def run() -> dict:
    goals_ok = int(set(GOALS) == set(range(1, 7)))
    reqs_ok = int(set(REQUIREMENTS) == set(range(1, 13)))

    mapping_correct = sum(int(goal_of(r) == EXPECTED_GOAL[r]) for r in REQUIREMENTS)

    coverage_checks = [
        coverage([])["overall"]["coverage"] == 0.0,
        coverage(list(range(1, 13)))["overall"]["coverage"] == 1.0,
        coverage([7, 8, 9])["goals"][4]["coverage"] == 1.0,        # all of goal 4
        coverage([1])["goals"][1]["coverage"] == 0.5,              # 1 of 2 in goal 1
        coverage([1, 3, 5, 7, 10, 12])["overall"]["implemented"] == 6,
        coverage([12])["goals"][6]["coverage"] == 1.0,             # goal 6 has 1 req
    ]
    coverage_correct = sum(int(c) for c in coverage_checks)

    checks = 2 + len(REQUIREMENTS) + len(coverage_checks)
    matched = goals_ok + reqs_ok + mapping_correct + coverage_correct
    return {
        "schema": "claimlib_pci_dss_v1",
        "module": "pci_dss",
        "n_goals": len(GOALS),
        "n_requirements": len(REQUIREMENTS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "mapping_correct": mapping_correct,
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "pci_dss.json", obj,
         script="python3 claimlib/modules/pci_dss/evidence.py")
    # claim:CLAIM-LIB-PCI-DSS-001 checks_matched
    # The goals/requirements structure (2), 12 goal-mappings and 6 coverage
    # checks all hold, so checks_matched = 20 and mismatches = 0.
    print(f"pci_dss: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['n_goals']} goals, {obj['n_requirements']} requirements); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
