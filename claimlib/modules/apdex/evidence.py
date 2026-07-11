# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-APDEX-001 -- the Apdex score reproduces a fixed table of
hand-computed reference values.

Each expected value is computed INDEPENDENTLY by hand from the Apdex definition
(satisfied <= T, tolerating in (T, 4T], frustrated > 4T; score = (satisfied +
tolerating/2)/total), not read back from the module. The battery pins the zone
boundaries (a sample exactly at T is satisfied; exactly at 4T is tolerating) and
the all-satisfied (1.0) and all-frustrated (0.0) extremes. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (apdex.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from apdex import apdex, classify, counts  # noqa: E402
from _util import emit  # noqa: E402

# (samples, threshold, expected_score). Expected computed by hand.
CASES = [
    # 3 satisfied, 1 tolerating (1.0 in (0.5,2.0]), 1 frustrated (3.0 > 2.0)
    ([0.1, 0.2, 0.3, 1.0, 3.0], 0.5, round((3 + 1 / 2) / 5, 4)),   # 0.7
    ([0.1, 0.2, 0.3, 0.4], 0.5, 1.0),                              # all satisfied
    ([10.0, 20.0, 30.0], 0.5, 0.0),                                # all frustrated
    ([0.5, 2.0], 0.5, round((1 + 1 / 2) / 2, 4)),                  # boundary: =T sat, =4T tol -> 0.75
    ([1, 1, 1, 1, 4, 4, 16, 16], 1, round((4 + 2 / 2) / 8, 4)),    # 4 sat, 2 tol, 2 frust -> 0.625
]

# Zone classification boundary checks (T = 2): <=2 satisfied, (2,8] tolerating, >8 frustrated.
ZONES = [
    (2.0, 2, "satisfied"),
    (2.0001, 2, "tolerating"),
    (8.0, 2, "tolerating"),
    (8.0001, 2, "frustrated"),
]


def run() -> dict:
    rows = []
    correct = 0
    for samples, threshold, expected in CASES:
        got = apdex(samples, threshold)
        ok = (got == expected)
        correct += int(ok)
        rows.append({"threshold": threshold, "expected": expected, "computed": got,
                     "counts": counts(samples, threshold), "correct": ok})

    zone_correct = 0
    for rt, threshold, expected in ZONES:
        zone_correct += int(classify(rt, threshold) == expected)

    return {
        "schema": "claimlib_apdex_v1",
        "module": "apdex",
        "n_cases": len(CASES),
        "correct": correct,
        "errors": len(CASES) - correct,
        "zone_cases": len(ZONES),
        "zone_correct": zone_correct,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "apdex.json", obj,
         script="python3 claimlib/modules/apdex/evidence.py")
    # claim:CLAIM-LIB-APDEX-001 correct
    # Every hand-computed Apdex score reproduces, so correct = 5 and errors = 0
    # (n_cases = 5); all 4 zone-boundary classifications hold too.
    print(f"apdex: {obj['correct']}/{obj['n_cases']} scores reproduced "
          f"({obj['errors']} errors), zones {obj['zone_correct']}/{obj['zone_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
