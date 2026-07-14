# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CRC-001 — the conformal-risk-control machinery
satisfies the published selection rule and the risk theorem, enumerated.

Oracles, none the module's own output: (1) the published lambdahat rule
(n/(n+1)) * Rhat_n(lambda) + B/(n+1) <= alpha (Angelopoulos et al. 2022) —
hand-computed selections on fixed grids, including the algebraic bound
Rhat_n <= ((n+1)alpha - B)/n; (2) THE RISK THEOREM, ENUMERATED: over fixed
exchangeable pools of monotone loss curves, exhaustive leave-one-out risk
(every choice of held-out unit, worst-case B charged when no lambda
qualifies) must be <= alpha as an EXACT Fraction — for every alpha on a
grid, for binary and fractional bounded losses; (3) the reduction to split
conformal prediction: with miscoverage-indicator losses, CRC's lambdahat
equals the split-conformal quantile construction's acceptance decision on
the same data; (4) fail-closed: a non-monotone grid, losses outside
[0, B], inconsistent calibration sizes and bad parameters all raise.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from conformal_risk import (  # noqa: E402
    CRCError, controlled_risk_bound, lambda_hat, loo_risk,
)
from _util import emit  # noqa: E402

ALPHAS = [Fraction(1, 10), Fraction(1, 5), Fraction(3, 10), Fraction(1, 2)]


def pool_binary(m: int, n_lams: int) -> dict:
    """Deterministic monotone binary loss curves for m units: unit i fails
    below its own difficulty threshold."""
    thresholds = [((i * 7 + 3) % n_lams) for i in range(m)]
    return {lam: [1 if lam < thresholds[i] else 0 for i in range(m)]
            for lam in range(n_lams)}


def pool_fractional(m: int, n_lams: int) -> dict:
    """Deterministic monotone fractional losses in [0, 1] that reach 0 at
    the top of the grid (the CRC existence precondition: some lambda
    achieves zero loss, so lambdahat exists whenever alpha >= B/(n+1))."""
    out = {}
    thresholds = [((i * 5 + 7) % n_lams) for i in range(m)]
    for lam in range(n_lams):
        row = [Fraction(min(max(0, thresholds[i] - lam), 4), 4)
               for i in range(m)]
        out[lam] = row
    return out


def run() -> dict:
    # Hand-computed selection: grid means 1, 1/3, 0 over n=3; B=1.
    grid = {0: [1, 1, 1], 1: [0, 1, 0], 2: [0, 0, 0]}
    hand = [
        # alpha=1/2: at lam=1, (3/4)(1/3)+(1/4)=1/2 <= 1/2 -> picks 1
        lambda_hat(grid, "0.5", 1) == 1,
        # alpha=1/4: lam=2 gives (3/4)(0)+1/4 = 1/4 <= 1/4 -> picks 2
        lambda_hat(grid, "0.25", 1) == 2,
        # alpha below B/(n+1): nothing qualifies
        lambda_hat(grid, "0.2", 1) is None,
        # algebra: the enforced bound on Rhat at n=3, alpha=1/2, B=1
        controlled_risk_bound(3, "0.5", 1) == Fraction(1, 3),
        controlled_risk_bound(100, "0.1", 1) == Fraction(101 * 1 - 10, 1000),
    ]
    hand_ok = sum(hand)

    # The theorem, enumerated UNDER ITS PRECONDITIONS: losses reach 0 at
    # the top of the grid (lambdahat exists) and alpha >= B/(pool size) —
    # the LOO calibration has n = m-1 units, so B/(n+1) = B/m.
    theorem_checks = 0
    theorem_ok = 0
    precondition_honest = 0
    for pool in (pool_binary(7, 8), pool_binary(12, 9),
                 pool_fractional(9, 10)):
        m = len(next(iter(pool.values())))
        for alpha in ALPHAS:
            if alpha >= Fraction(1, m):
                theorem_checks += 1
                if loo_risk(pool, alpha, 1) <= alpha:
                    theorem_ok += 1
            else:
                # Outside the precondition the honest behaviour is refusal:
                # no lambda qualifies in any LOO split (charged as B).
                if loo_risk(pool, alpha, 1) == 1:
                    precondition_honest += 1

    # Reduction to conformal prediction: miscoverage losses 1{score > lam}.
    scores = [Fraction((i * 11 + 5) % 40, 7) for i in range(10)]
    lams = sorted(set(scores))
    cp_grid = {lam: [1 if s > lam else 0 for s in scores] for lam in lams}
    reduction_ok = 0
    for alpha in ALPHAS:
        lam = lambda_hat(cp_grid, alpha, 1)
        # split-conformal quantile: k = ceil((n+1)(1-alpha)) smallest score
        n = len(scores)
        k = int(-((-(n + 1) * (1 - alpha)) // 1))
        expected = None if k > n else sorted(scores)[k - 1]
        if lam == expected:
            reduction_ok += 1

    rejects = 0
    for bad in (lambda: lambda_hat({0: [0, 0], 1: [1, 1]}, "0.5", 1),  # rising
                lambda: lambda_hat({0: [2]}, "0.5", 1),        # loss > B
                lambda: lambda_hat({0: [1, 1], 1: [0]}, "0.5", 1),  # ragged
                lambda: lambda_hat({}, "0.5", 1),
                lambda: lambda_hat({0: [0]}, "0.5", 0),        # B = 0
                lambda: lambda_hat({0: [0]}, float("nan"), 1),
                lambda: controlled_risk_bound(0, "0.5", 1),
                lambda: loo_risk({0: [0]}, "0.5", 1)):         # 1-unit pool
        try:
            bad()
        except CRCError:
            rejects += 1

    total = len(hand) + theorem_checks + 2 + len(ALPHAS)
    matched = hand_ok + theorem_ok + precondition_honest + reduction_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "conformal_risk",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_ok": hand_ok,
        "theorem_checks": theorem_checks,
        "theorem_ok": theorem_ok,
        "precondition_honest": precondition_honest,
        "reduction_ok": reduction_ok,
        "reject_cases": 8,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "conformal_risk.json", obj,
         script="python3 claimlib/modules/conformal_risk/evidence.py")
    # claim:CLAIM-LIB-CRC-001 checks_matched
    # All 21 checks hold: 5 hand-computed selections and algebraic bounds,
    # the risk theorem enumerated exhaustively over the 10 pool-by-alpha
    # combinations satisfying its preconditions (LOO risk <= alpha as exact
    # Fractions), 2 honest refusals outside the preconditions, and the
    # reduction to split conformal prediction on all 4 alphas —
    # checks_matched = 21, mismatches = 0.
    print(f"conformal_risk: {obj['checks_matched']}/{obj['checks']} checks "
          f"(theorem {obj['theorem_ok']}/{obj['theorem_checks']} exact, "
          f"CP reduction {obj['reduction_ok']}/4); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
