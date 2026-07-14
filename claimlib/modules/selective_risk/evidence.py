# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SELECTIVE-001 — the selective-classification
measurements are exact and carry the definitions' structural properties.

Oracles, none the module's own output: (1) hand-computed exact values on a
fixed 8-point audit (coverage 1/2 at theta 0.7, selective risk exactly 1/4
on the accepted half, full-coverage risk exactly 3/8 = the plain mean);
(2) the definitions' properties verified over a deterministic 40-point
battery: the curve's last point has coverage exactly 1 with risk exactly the
overall mean loss, coverage is monotone non-increasing in the threshold,
every risk lies in [0, max loss], the curve is permutation-invariant, and
accepting everything reproduces the unconditional mean; (3) zero-coverage
selective risk fails closed (undefined, never 0). All checks are exact
Fraction equalities. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from selective_risk import (  # noqa: E402
    SelectiveError, coverage, risk_coverage_curve, selective_risk,
)
from _util import emit  # noqa: E402

AUDIT = [("0.95", 0), ("0.9", 0), ("0.8", 1), ("0.75", 0),
         ("0.6", 1), ("0.5", 0), ("0.3", 1), ("0.2", 0)]


def battery(n: int) -> list:
    return [(Fraction((i * 17 + 5) % 97, 100),
             Fraction((i * 23 + 7) % 5, 4)) for i in range(n)]


def run() -> dict:
    hand = [
        coverage(AUDIT, "0.7") == Fraction(1, 2),
        selective_risk(AUDIT, "0.7") == Fraction(1, 4),
        coverage(AUDIT, "0.2") == 1,
        selective_risk(AUDIT, "0.2") == Fraction(3, 8),
        coverage(AUDIT, "0.99") == 0,
        selective_risk(AUDIT, "0.95") == 0,
    ]
    hand_ok = sum(hand)

    pts = battery(40)
    curve = risk_coverage_curve(pts)
    mean_loss = sum(loss for _, loss in pts) / Fraction(len(pts))
    max_loss = max(loss for _, loss in pts)
    props = [
        curve[-1]["coverage"] == 1,
        curve[-1]["risk"] == mean_loss,
        all(a["coverage"] <= b["coverage"]
            for a, b in zip(curve, curve[1:])),
        all(a["threshold"] > b["threshold"]
            for a, b in zip(curve, curve[1:])),
        all(0 <= p["risk"] <= max_loss for p in curve),
        risk_coverage_curve(list(reversed(pts))) == curve,
        selective_risk(pts, min(c for c, _ in pts)) == mean_loss,
        len(curve) == len({c for c, _ in pts}),
    ]
    props_ok = sum(props)

    undefined_ok = 0
    try:
        selective_risk(AUDIT, "0.99")
    except SelectiveError:
        undefined_ok = 1

    rejects = 0
    for bad in (lambda: coverage([], "0.5"),
                lambda: coverage([(0.5,)], "0.5"),
                lambda: coverage([(0.5, -1)], "0.5"),
                lambda: coverage([(float("nan"), 0)], "0.5"),
                lambda: coverage([(0.5, 0)], float("inf")),
                lambda: coverage([(True, 0)], "0.5"),
                lambda: selective_risk("nope", "0.5")):
        try:
            bad()
        except SelectiveError:
            rejects += 1

    total = len(hand) + len(props) + 1
    matched = hand_ok + props_ok + undefined_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "selective_risk",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_ok": hand_ok,
        "property_ok": props_ok,
        "undefined_fails_closed": undefined_ok,
        "battery_points": len(pts),
        "reject_cases": 7,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "selective_risk.json", obj,
         script="python3 claimlib/modules/selective_risk/evidence.py")
    # claim:CLAIM-LIB-SELECTIVE-001 checks_matched
    # All 15 checks hold as exact Fraction equalities: 6 hand-computed
    # audit values, 8 structural properties of the risk-coverage curve over
    # a 40-point battery (full-coverage point equals the plain mean,
    # monotone coverage, permutation invariance), and the zero-coverage
    # case failing closed — checks_matched = 15, mismatches = 0.
    print(f"selective_risk: {obj['checks_matched']}/{obj['checks']} exact "
          f"checks (hand {obj['hand_ok']}/6, properties "
          f"{obj['property_ok']}/8); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
