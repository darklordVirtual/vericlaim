# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PERCENTILE-001 -- the linear percentile agrees with
stdlib ``statistics`` and the nearest-rank percentile matches its definition.

``statistics.quantiles`` / ``statistics.median`` are independent implementations
this module never imports, so they are genuine oracles. For each dataset the
evidence checks percentile(data, p, "linear") against
statistics.quantiles(data, n=100, method="inclusive")[p-1] for every p in 1..99,
and median() against statistics.median. The nearest-rank method is checked
against a small hand-computed reference. Deterministic.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (percentile.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from percentile import percentile, median  # noqa: E402
from _util import emit  # noqa: E402

DATASETS = [
    list(range(1, 11)),
    [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5],
    [10.0, 20.0, 30.0, 40.0, 50.0],
    [2, 2, 2, 2, 2],                       # constant
    list(range(1, 101)),                   # 1..100
    [1000, 5, 5, 5, 5, 5, 5, 5, 5, 9999],  # skewed with outliers
]

# Hand-computed nearest-rank references for [10,20,30,40,50] (n=5):
#   ceil(p/100 * 5): p=90 -> 5 -> value 50; p=20 -> 1 -> 10; p=50 -> 3 -> 30.
NEAREST_RANK = [
    ([10, 20, 30, 40, 50], 90, 50),
    ([10, 20, 30, 40, 50], 20, 10),
    ([10, 20, 30, 40, 50], 50, 30),
    ([10, 20, 30, 40, 50], 100, 50),
    ([10, 20, 30, 40, 50], 0, 10),
]


def run() -> dict:
    checks = 0
    matched = 0
    for data in DATASETS:
        oracle = statistics.quantiles(data, n=100, method="inclusive")
        for p in range(1, 100):
            got = percentile(data, p, "linear")
            checks += 1
            matched += int(abs(got - oracle[p - 1]) < 1e-9)
        checks += 1
        matched += int(abs(median(data) - statistics.median(data)) < 1e-9)

    nearest_correct = 0
    for data, p, expected in NEAREST_RANK:
        nearest_correct += int(percentile(data, p, "nearest_rank") == expected)
    checks += len(NEAREST_RANK)
    matched += nearest_correct

    return {
        "schema": "claimlib_percentile_v1",
        "module": "percentile",
        "n_datasets": len(DATASETS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "nearest_rank_cases": len(NEAREST_RANK),
        "nearest_rank_correct": nearest_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "percentile.json", obj,
         script="python3 claimlib/modules/percentile/evidence.py")
    # claim:CLAIM-LIB-PERCENTILE-001 checks_matched
    # Every linear percentile matches statistics and every nearest-rank case
    # matches its definition, so checks_matched = 605 and mismatches = 0.
    print(f"percentile: {obj['checks_matched']}/{obj['checks']} checks agree with "
          f"statistics / definition ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
