# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CONFORMAL-001 — the split-conformal machinery
satisfies the published quantile rule and the coverage theorem, enumerated.

Oracles, none the module's own output: (1) the published quantile rule
qhat = ceil((n+1)(1-alpha))-th smallest score (Angelopoulos & Bates 2021) —
hand-computed indices including the classic n=100, alpha=0.1 -> rank 91;
(2) THE COVERAGE THEOREM, ENUMERATED: over fixed exchangeable pools of
distinct scores, exhaustive leave-one-out coverage (every choice of held-out
point) must land in [1-alpha, 1-alpha + 1/n] as an EXACT Fraction — for
every alpha on a fixed grid; ties must never push coverage below 1-alpha;
(3) prediction-set semantics: monotone in alpha (smaller alpha -> superset),
the too-few-calibration-points case honestly returns everything.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from conformal_split import (  # noqa: E402
    ConformalError, conformal_quantile, loo_coverage, prediction_set,
    quantile_index,
)
from _util import emit  # noqa: E402

ALPHAS = [Fraction(1, 10), Fraction(1, 5), Fraction(1, 4), Fraction(1, 3),
          Fraction(1, 2)]

# Deterministic pools of DISTINCT scores (sizes 5, 12, 21).
POOLS = [
    [((7 * i + 3) % 53) + Fraction(i, 100) for i in range(n)]
    for n in (5, 12, 21)
]
TIED_POOL = [1, 2, 2, 2, 3, 3, 4, 5, 5, 6]


def run() -> dict:
    hand = [
        quantile_index(100, "0.1") == 91,      # ceil(101*0.9) = 91
        quantile_index(9, "0.1") == 9,         # ceil(10*0.9) = 9 <= 9
        quantile_index(10, "0.1") == 10,       # ceil(11*0.9) = 10
        quantile_index(4, "0.1") is None,      # ceil(5*0.9) = 5 > 4
        conformal_quantile([3, 1, 2], "0.25") == 3,
        conformal_quantile([3, 1, 2], "0.5") == 2,
    ]
    hand_ok = sum(hand)

    theorem_checks = 0
    theorem_ok = 0
    for pool in POOLS:
        n = len(pool)
        for alpha in ALPHAS:
            theorem_checks += 1
            cov = loo_coverage(pool, alpha)
            lo = 1 - alpha
            hi = 1 - alpha + Fraction(1, n)
            if lo <= cov <= hi:
                theorem_ok += 1
    ties_ok = 0
    for alpha in ALPHAS:
        if loo_coverage(TIED_POOL, alpha) >= 1 - alpha:
            ties_ok += 1

    cal = [Fraction(i, 7) for i in range(1, 15)]
    cands = {f"y{i}": Fraction(i, 9) for i in range(12)}
    sets_ok = 0
    prev = None
    for alpha in sorted(ALPHAS):          # increasing alpha -> shrinking set
        s = prediction_set(cal, alpha, cands)
        if prev is None or s <= prev:
            sets_ok += 1
        prev = s
    vacuous = prediction_set([1, 2], "0.1", cands)   # n too small
    vacuous_ok = int(vacuous == set(cands))

    rejects = 0
    for bad in (lambda: quantile_index(0, "0.1"),
                lambda: quantile_index(10, "0"),
                lambda: quantile_index(10, "1"),
                lambda: quantile_index(10, 1.5),
                lambda: conformal_quantile([], "0.1"),
                lambda: conformal_quantile([1, float("nan")], "0.1"),
                lambda: prediction_set([1], "0.1", {}),
                lambda: loo_coverage([1], "0.1")):
        try:
            bad()
        except ConformalError:
            rejects += 1

    total = len(hand) + theorem_checks + len(ALPHAS) + len(ALPHAS) + 1
    matched = hand_ok + theorem_ok + ties_ok + sets_ok + vacuous_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "conformal_split",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_ok": hand_ok,
        "theorem_checks": theorem_checks,
        "theorem_ok": theorem_ok,
        "ties_ok": ties_ok,
        "monotone_ok": sets_ok,
        "vacuous_ok": vacuous_ok,
        "reject_cases": 8,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "conformal_split.json", obj,
         script="python3 claimlib/modules/conformal_split/evidence.py")
    # claim:CLAIM-LIB-CONFORMAL-001 checks_matched
    # All 32 checks hold: 6 hand-computed quantile ranks (incl. the classic
    # n=100/alpha=0.1 -> 91), the coverage theorem enumerated exhaustively
    # over 15 pool x alpha combinations as exact Fractions inside
    # [1-alpha, 1-alpha + 1/n], 5 tie cases never below 1-alpha, 5 monotone
    # prediction sets and the honest vacuous case — checks_matched = 32,
    # mismatches = 0.
    print(f"conformal_split: {obj['checks_matched']}/{obj['checks']} checks "
          f"(theorem {obj['theorem_ok']}/{obj['theorem_checks']} exact, "
          f"hand {obj['hand_ok']}/6); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
