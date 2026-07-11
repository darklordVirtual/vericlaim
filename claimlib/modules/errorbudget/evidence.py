# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ERRORBUDGET-001 — the SLO / error-budget arithmetic
reproduces the textbook SRE formulas exactly.

Runs the reusable ``errorbudget`` module over a fixed battery of
(SLO, window, downtime) cases whose expected availability, error budget and
budget-remaining were computed BY HAND from the published formulas (Google SRE
Workbook, "Implementing SLOs"):

    availability% = (window - downtime) / window * 100
    budget (min)  = window * (1 - SLO/100)
    remaining%    = (budget - downtime) / budget * 100

The reference values below are the exact arithmetic results, NOT this module's
output, so a mismatch would mean the code is wrong. Deterministic: same artifact
on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (errorbudget.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from errorbudget import availability, budget_minutes, error_budget_remaining_pct  # noqa: E402
from _util import emit  # noqa: E402

# Common windows, in minutes.
DAY = 1440          # 1 day
WEEK = 10080        # 7 days
MONTH30 = 43200     # 30 days
YEAR = 525600       # 365 days

# Each row: (slo_pct, window_min, downtime_min, exp_availability, exp_budget,
# exp_remaining). Every expected value is worked out by hand from the formulas
# above and cited inline — independent of the code under test.
REFERENCE = [
    # 99.9% / 30d: budget = 43200*0.001 = 43.2 min. Half the budget spent.
    #   avail = (43200-21.6)/43200*100 = 99.95 ; rem = (43.2-21.6)/43.2*100 = 50
    (99.9, MONTH30, 21.6, 99.95, 43.2, 50.0),
    # 99.0% / 30d: budget = 43200*0.01 = 432 min. Budget exactly exhausted.
    #   avail = (43200-432)/43200*100 = 99.0 ; rem = (432-432)/432*100 = 0
    (99.0, MONTH30, 432.0, 99.0, 432.0, 0.0),
    # 99.9% / 7d: budget = 10080*0.001 = 10.08 min. Half spent.
    #   avail = (10080-5.04)/10080*100 = 99.95 ; rem = (10.08-5.04)/10.08*100 = 50
    (99.9, WEEK, 5.04, 99.95, 10.08, 50.0),
    # 99.99% / 365d: budget = 525600*0.0001 = 52.56 min. Exactly exhausted.
    #   avail = (525600-52.56)/525600*100 = 99.99 ; rem = 0
    (99.99, YEAR, 52.56, 99.99, 52.56, 0.0),
    # 99.5% / 30d: budget = 43200*0.005 = 216 min. Overspent by 1.5x.
    #   avail = (43200-324)/43200*100 = 99.25 ; rem = (216-324)/216*100 = -50
    (99.5, MONTH30, 324.0, 99.25, 216.0, -50.0),
    # 99.9% / 30d, zero downtime: full budget intact.
    #   avail = 100.0 ; rem = (43.2-0)/43.2*100 = 100
    (99.9, MONTH30, 0.0, 100.0, 43.2, 100.0),
    # 95.0% / 1d: budget = 1440*0.05 = 72 min. Half spent.
    #   avail = (1440-36)/1440*100 = 97.5 ; rem = (72-36)/72*100 = 50
    (95.0, DAY, 36.0, 97.5, 72.0, 50.0),
    # 99.9% / 30d, 10 min down: non-round case exercising 4-dp rounding.
    #   avail = (43200-10)/43200*100 = 99.976851... -> 99.9769
    #   rem = (43.2-10)/43.2*100 = 76.851851... -> 76.8519
    (99.9, MONTH30, 10.0, 99.9769, 43.2, 76.8519),
    # 90.0% / 1d: budget = 1440*0.1 = 144 min. Exactly exhausted.
    #   avail = (1440-144)/1440*100 = 90.0 ; rem = 0
    (90.0, DAY, 144.0, 90.0, 144.0, 0.0),
]


def run() -> dict:
    cases = []
    correct = 0
    for slo, window, downtime, exp_avail, exp_budget, exp_rem in REFERENCE:
        got_avail = availability(window, downtime)
        got_budget = budget_minutes(slo, window)
        got_rem = error_budget_remaining_pct(slo, window, downtime)
        ok = (got_avail == exp_avail and got_budget == exp_budget
              and got_rem == exp_rem)
        correct += int(ok)
        cases.append({
            "slo_pct": slo, "window_min": window, "downtime_min": downtime,
            "expected_availability": exp_avail, "computed_availability": got_avail,
            "expected_budget_min": exp_budget, "computed_budget_min": got_budget,
            "expected_remaining_pct": exp_rem, "computed_remaining_pct": got_rem,
            "match": ok,
        })
    n = len(REFERENCE)
    return {
        "schema": "claimlib_errorbudget_v1",
        "module": "errorbudget",
        "n_cases": n,
        "correct": correct,
        "errors": n - correct,
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "errorbudget.json", obj,
         script="python3 claimlib/modules/errorbudget/evidence.py")
    # claim:CLAIM-LIB-ERRORBUDGET-001 correct
    # All 9 hand-computed reference rows reproduce exactly, so
    # correct = 9 and errors = 0.
    print(f"errorbudget: {obj['correct']}/{obj['n_cases']} reference rows "
          f"reproduced ({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
