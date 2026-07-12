# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SOC2-001 -- the encoded SOC 2 taxonomy matches the AICPA
Trust Services Criteria and the coverage arithmetic is correct.

The taxonomy is INDEPENDENTLY KNOWN from the AICPA Trust Services Criteria: five
categories (Security, Availability, Processing Integrity, Confidentiality,
Privacy) and the nine Common Criteria series CC1..CC9. The evidence checks the
five category codes, the nine CC series, and hand-verified coverage values (empty
-> 0.0, full -> 1.0, a 3-of-9 subset -> 0.3333 with the correct missing list).
Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (soc2.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from soc2 import CATEGORIES, COMMON_CRITERIA, coverage  # noqa: E402
from _util import emit  # noqa: E402


def run() -> dict:
    categories_ok = int(set(CATEGORIES) == {"SEC", "AVL", "PIN", "CON", "PRI"})
    criteria_ok = int(set(COMMON_CRITERIA) == {f"CC{i}" for i in range(1, 10)})

    checks = [
        coverage([])["coverage"] == 0.0,
        coverage(list(COMMON_CRITERIA))["coverage"] == 1.0,
        coverage(["CC1", "CC2", "CC3"])["coverage"] == round(3 / 9, 4),
        coverage(["CC1", "CC2", "CC3"])["implemented"] == 3,
        coverage(list(COMMON_CRITERIA))["missing"] == [],
        coverage(["CC6"])["missing"] == ["CC1", "CC2", "CC3", "CC4", "CC5", "CC7", "CC8", "CC9"],
    ]
    coverage_correct = sum(int(c) for c in checks)

    total = 2 + len(checks)
    matched = categories_ok + criteria_ok + coverage_correct
    return {
        "schema": "claimlib_soc2_v1",
        "module": "soc2",
        "n_categories": len(CATEGORIES),
        "n_common_criteria": len(COMMON_CRITERIA),
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "categories_ok": bool(categories_ok),
        "criteria_ok": bool(criteria_ok),
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "soc2.json", obj,
         script="python3 claimlib/modules/soc2/evidence.py")
    # claim:CLAIM-LIB-SOC2-001 checks_matched
    # The 5 categories, 9 Common Criteria and 6 coverage checks hold, so
    # checks_matched = 8 and mismatches = 0.
    print(f"soc2: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['n_categories']} categories, {obj['n_common_criteria']} CC, "
          f"coverage {obj['coverage_correct']}/6); mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
