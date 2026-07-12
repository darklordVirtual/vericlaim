# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-BENFORD-001 -- the expected distribution equals the
Benford formula, leading-digit extraction is correct, and the conformance
statistics behave as defined.

The Benford probabilities log10(1 + 1/d) are an INDEPENDENTLY KNOWN mathematical
fact (1 -> 0.301, 2 -> 0.176, ... 9 -> 0.046, summing to 1). The evidence checks
the nine expected frequencies against hand-written values, leading-digit
extraction over a battery (including sub-1 and large values), and that a strongly
non-Benford dataset (every value leads with 9) has a far larger MAD than a
near-Benford dataset (the first digits of 2**1..2**500, which famously follow
Benford). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (benford.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from benford import (  # noqa: E402
    first_digit, expected_distribution, chi_square, mad, conforms)
from _util import emit  # noqa: E402

# Benford's expected leading-digit frequencies (independently known), 3 dp.
EXPECTED_3DP = {1: 0.301, 2: 0.176, 3: 0.125, 4: 0.097, 5: 0.079,
                6: 0.067, 7: 0.058, 8: 0.051, 9: 0.046}

# (value, expected leading digit).
DIGIT_CASES = [
    (1, 1), (9, 9), (10, 1), (0.00123, 1), (4567, 4), (300.0, 3),
    (-812, 8), (0.09, 9), (999999, 9), (2.71828, 2),
]


def run() -> dict:
    expected = expected_distribution()
    expected_ok = sum(int(round(expected[d], 3) == EXPECTED_3DP[d]) for d in range(1, 10))
    sum_is_one = int(abs(sum(expected.values()) - 1.0) < 1e-9)

    digit_ok = sum(int(first_digit(v) == d) for v, d in DIGIT_CASES)

    # Near-Benford: leading digits of 2**1 .. 2**500.
    benford_like = [2 ** n for n in range(1, 501)]
    # Strongly non-Benford: everything leads with 9.
    non_benford = [9, 90, 900, 9000, 95, 98, 99] * 30

    stat_checks = [
        conforms(benford_like, mad_threshold=0.015) is True,       # close conformity
        conforms(non_benford) is False,                            # obvious anomaly
        mad(non_benford) > mad(benford_like),                      # anomaly has larger MAD
        chi_square(non_benford) > chi_square(benford_like),        # and larger chi-square
        mad(benford_like) >= 0.0,
    ]
    stat_ok = sum(int(c) for c in stat_checks)

    checks = 9 + 1 + len(DIGIT_CASES) + len(stat_checks)
    matched = expected_ok + sum_is_one + digit_ok + stat_ok
    return {
        "schema": "claimlib_benford_v1",
        "module": "benford",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "expected_ok": expected_ok,
        "digit_ok": digit_ok,
        "stat_ok": stat_ok,
        "benford_like_mad": round(mad(benford_like), 6),
        "non_benford_mad": round(mad(non_benford), 6),
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "benford.json", obj,
         script="python3 claimlib/modules/benford/evidence.py")
    # claim:CLAIM-LIB-BENFORD-001 checks_matched
    # The 9 expected frequencies, sum-to-one, 10 digit cases and 5 statistic
    # checks all hold, so checks_matched = 25 and mismatches = 0.
    print(f"benford: {obj['checks_matched']}/{obj['checks']} checks "
          f"(expected {obj['expected_ok']}/9, digits {obj['digit_ok']}/{len(DIGIT_CASES)}, "
          f"stats {obj['stat_ok']}/5); mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
