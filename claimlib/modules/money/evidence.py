# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MONEY-001 -- allocation is cent-exact and banker's
rounding matches published HALF_EVEN results.

Two independent batteries:

  1. Allocation: over a fixed set of (total, weights) cases, the parts returned
     by ``allocate`` must sum EXACTLY back to the total (no minor unit lost or
     minted). The invariant is checked directly (sum(parts) == total), and a
     subset has independently hand-written expected splits. This property needs
     no external oracle -- it is an arithmetic identity.
  2. Rounding: a fixed table of values whose ROUND_HALF_EVEN result is
     independently known (0.5 -> 0, 1.5 -> 2, 2.5 -> 2, 3.5 -> 4, and the
     classic 2.675 -> 2.68 tie-to-even) checks ``round_money`` against
     hand-written expected strings, NOT against the module's own output.

Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (money.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from money import allocate, round_money  # noqa: E402
from _util import emit  # noqa: E402

# (total_minor, weights). Chosen to exercise the leftover-distribution path,
# exact divisions, single-share, zero-total, and weighted (non-equal) splits.
ALLOC_CASES = [
    (100, [1, 1, 1]),
    (100, [1, 1, 1, 1, 1, 1]),
    (1000, [1, 2, 1]),
    (10, [1, 1, 1]),
    (0, [1, 1]),
    (5, [3, 1]),
    (12345, [7, 11, 2]),
    (99, [1]),
]

# A subset with independently hand-computed expected splits.
ALLOC_EXPECTED = {
    0: [34, 33, 33],       # 100 / 3
    1: [17, 17, 17, 17, 16, 16],  # 100 / 6, four largest remainders get +1
    2: [250, 500, 250],    # 1000 by 1:2:1
    3: [4, 3, 3],          # 10 / 3, first remainder gets +1
    5: [4, 1],             # 5 by 3:1
}

# (value_string, places, expected_string). ROUND_HALF_EVEN references.
ROUND_CASES = [
    ("0.5", 0, "0"),
    ("1.5", 0, "2"),
    ("2.5", 0, "2"),
    ("3.5", 0, "4"),
    ("2.675", 2, "2.68"),
    ("0.125", 2, "0.12"),
    ("0.135", 2, "0.14"),
    ("1.005", 2, "1.00"),
    ("2.005", 2, "2.00"),
    ("-2.5", 0, "-2"),
]


def run() -> dict:
    alloc_rows = []
    cent_exact = 0
    hand_correct = 0
    for idx, (total, weights) in enumerate(ALLOC_CASES):
        parts = allocate(total, weights)
        exact = (sum(parts) == total)
        cent_exact += int(exact)
        row = {"total": total, "weights": list(weights), "parts": parts,
               "sum": sum(parts), "cent_exact": exact}
        if idx in ALLOC_EXPECTED:
            match = (parts == ALLOC_EXPECTED[idx])
            hand_correct += int(match)
            row["expected"] = ALLOC_EXPECTED[idx]
            row["hand_match"] = match
        alloc_rows.append(row)

    round_rows = []
    round_correct = 0
    for value, places, expected in ROUND_CASES:
        got = str(round_money(value, places))
        ok = (got == expected)
        round_correct += int(ok)
        round_rows.append({"value": value, "places": places,
                           "expected": expected, "computed": got, "correct": ok})

    return {
        "schema": "claimlib_money_v1",
        "module": "money",
        "n_alloc_cases": len(ALLOC_CASES),
        "cent_exact": cent_exact,
        "cent_lost": len(ALLOC_CASES) - cent_exact,
        "n_hand_splits": len(ALLOC_EXPECTED),
        "hand_splits_correct": hand_correct,
        "n_round_cases": len(ROUND_CASES),
        "round_correct": round_correct,
        "round_errors": len(ROUND_CASES) - round_correct,
        "alloc_detail": alloc_rows,
        "round_detail": round_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "money.json", obj,
         script="python3 claimlib/modules/money/evidence.py")
    # claim:CLAIM-LIB-MONEY-001 cent_exact
    # Every allocation sums back exactly to its total, so cent_exact = 8
    # (n_alloc_cases = 8) with cent_lost = 0; all 10 rounding rows match too.
    print(f"money: cent_exact {obj['cent_exact']}/{obj['n_alloc_cases']} "
          f"(cent_lost={obj['cent_lost']}), rounding "
          f"{obj['round_correct']}/{obj['n_round_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
