# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-NIS2-001 -- the encoded NIS2 Article 21(2) measures match
the Directive and the coverage arithmetic is correct.

The set of ten measures is INDEPENDENTLY KNOWN from Article 21(2)(a)-(j) of
Directive (EU) 2022/2555. The evidence checks that exactly the codes a..j are
present and that coverage() computes hand-verified values: the empty set -> 0.0,
the full set -> 1.0, a 4-of-10 subset -> 0.4, and that the missing list is exactly
the complement. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (nis2.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from nis2 import MEASURES, coverage  # noqa: E402
from _util import emit  # noqa: E402


def run() -> dict:
    codes_ok = int(set(MEASURES) == set("abcdefghij"))

    checks = [
        coverage([])["coverage"] == 0.0,
        coverage(list(MEASURES))["coverage"] == 1.0,
        coverage(["a", "b", "h", "j"])["coverage"] == 0.4,
        coverage(["a", "b", "h", "j"])["implemented"] == 4,
        coverage(["a", "b", "h", "j"])["missing"] == ["c", "d", "e", "f", "g", "i"],
        coverage(list(MEASURES))["missing"] == [],
    ]
    coverage_correct = sum(int(c) for c in checks)

    total_checks = 1 + len(checks)
    matched = codes_ok + coverage_correct
    return {
        "schema": "claimlib_nis2_v1",
        "module": "nis2",
        "n_measures": len(MEASURES),
        "checks": total_checks,
        "checks_matched": matched,
        "mismatches": total_checks - matched,
        "measure_codes_ok": bool(codes_ok),
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "nis2.json", obj,
         script="python3 claimlib/modules/nis2/evidence.py")
    # claim:CLAIM-LIB-NIS2-001 checks_matched
    # The ten measure codes a..j and all 6 coverage checks hold, so
    # checks_matched = 7 and mismatches = 0.
    print(f"nis2: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['n_measures']} measures, coverage {obj['coverage_correct']}/6); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
