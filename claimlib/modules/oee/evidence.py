# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-OEE-001 -- the OEE calculator reproduces the canonical
published worked example and a table of hand-computed factor values.

The headline reference is the widely published OEE worked example (Vorne /
oee.com): Planned Production Time 420 min, Run Time 373 min, Ideal Cycle Time
1.0 s, Total Count 19271, Good Count 18848 ->
    Availability = 373/420           = 0.8881
    Performance  = 19271/(373*60)    = 0.8611
    Quality      = 18848/19271       = 0.9780
    OEE          = A*P*Q             = 0.7479
Each expected value below is hand-computed from those published inputs, NOT read
back from the module. Additional rows exercise the boundary (all factors 1.0)
and simple halves. Comparison is to 4 decimal places. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (oee.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from oee import oee  # noqa: E402
from _util import emit  # noqa: E402

# (label, kwargs, expected {availability, performance, quality, oee}) at 4 dp.
CASES = [
    ("published Vorne example",
     dict(planned_production_time=420 * 60, run_time=373 * 60,
          ideal_cycle_time=1.0, total_count=19271, good_count=18848),
     {"availability": 0.8881, "performance": 0.8611, "quality": 0.9780, "oee": 0.7479}),
    ("perfect line (all 1.0)",
     dict(planned_production_time=100.0, run_time=100.0,
          ideal_cycle_time=2.0, total_count=50, good_count=50),
     {"availability": 1.0, "performance": 1.0, "quality": 1.0, "oee": 1.0}),
    ("each factor one half",
     dict(planned_production_time=100.0, run_time=50.0,
          ideal_cycle_time=1.0, total_count=25, good_count=12.5),
     {"availability": 0.5, "performance": 0.5, "quality": 0.5, "oee": 0.125}),
]


def run() -> dict:
    rows = []
    correct = 0
    for label, kwargs, expected in CASES:
        got = oee(**kwargs)
        row = {"label": label, "expected": expected, "computed": {}, "match": True}
        for factor, exp in expected.items():
            g = round(got[factor], 4)
            row["computed"][factor] = g
            if g != round(exp, 4):
                row["match"] = False
        correct += int(row["match"])
        rows.append(row)

    return {
        "schema": "claimlib_oee_v1",
        "module": "oee",
        "n_cases": len(CASES),
        "correct": correct,
        "errors": len(CASES) - correct,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "oee.json", obj,
         script="python3 claimlib/modules/oee/evidence.py")
    # claim:CLAIM-LIB-OEE-001 correct
    # Every case reproduces its hand-computed factors, so correct = 3 and
    # errors = 0 (n_cases = 3), including the published OEE = 0.7479 example.
    print(f"oee: {obj['correct']}/{obj['n_cases']} reference cases reproduced "
          f"({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
