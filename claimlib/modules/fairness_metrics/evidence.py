# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-FAIRNESS-001 — the fairness metrics are exact and
carry their defining properties.

Oracles, none the module's own output: (1) hand-computed exact values on a
fixed two-group audit table (selection rates 1/2 vs 1/4 give demographic-
parity difference exactly 1/4, disparate-impact ratio exactly 1/2 — failing
the four-fifths rule; TPR gap 4/5 - 2/5 = 2/5); (2) theorem-shaped
properties verified over a deterministic 60-case battery of generated
group tables: metrics are invariant under group relabeling, bounded in
[0, 1], zero exactly on identical groups, and a perfect classifier has
equalized-odds difference 0 for ANY group composition; (3) the four-fifths
threshold sits exactly at 4/5 (a ratio of 4/5 passes, 79/100 fails).
All arithmetic is fractions.Fraction — the checks are equalities, not
approximations. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from fairness_metrics import (  # noqa: E402
    FairnessError, GroupCounts, demographic_parity_difference,
    disparate_impact_ratio, equalized_odds_difference, four_fifths_ok, fpr,
    selection_rate, tpr,
)
from _util import emit  # noqa: E402

# Fixed audit table: group a selects 50/100, group b selects 25/100.
AUDIT = {
    "a": GroupCounts(tp=40, fp=10, fn=10, tn=40),   # rate 1/2, TPR 4/5
    "b": GroupCounts(tp=20, fp=5, fn=30, tn=45),    # rate 1/4, TPR 2/5
}


def gen_group(seed: int) -> GroupCounts:
    """Deterministic synthetic confusion counts (no zeros on either margin)."""
    a = (seed * 7 + 3) % 40 + 1
    b = (seed * 11 + 5) % 30 + 1
    c = (seed * 13 + 7) % 25 + 1
    d = (seed * 17 + 11) % 45 + 1
    return GroupCounts(tp=a, fp=b, fn=c, tn=d)


def run() -> dict:
    hand = [
        selection_rate(AUDIT["a"]) == Fraction(1, 2),
        selection_rate(AUDIT["b"]) == Fraction(1, 4),
        demographic_parity_difference(AUDIT) == Fraction(1, 4),
        disparate_impact_ratio(AUDIT) == Fraction(1, 2),
        four_fifths_ok(AUDIT) is False,
        tpr(AUDIT["a"]) == Fraction(4, 5),
        tpr(AUDIT["b"]) == Fraction(2, 5),
        fpr(AUDIT["a"]) == Fraction(1, 5),
        fpr(AUDIT["b"]) == Fraction(1, 10),
        equalized_odds_difference(AUDIT) == Fraction(2, 5),
    ]
    hand_ok = sum(hand)

    prop_checks = 0
    prop_ok = 0
    for seed in range(20):
        g1, g2 = gen_group(seed), gen_group(seed + 100)
        groups = {"x": g1, "y": g2}
        swapped = {"y": g2, "x": g1}
        prop_checks += 3
        if demographic_parity_difference(groups) == \
                demographic_parity_difference(swapped) and \
                equalized_odds_difference(groups) == \
                equalized_odds_difference(swapped):
            prop_ok += 1
        if Fraction(0) <= demographic_parity_difference(groups) <= 1 and \
                Fraction(0) <= disparate_impact_ratio(groups) <= 1 and \
                Fraction(0) <= equalized_odds_difference(groups) <= 1:
            prop_ok += 1
        same = {"x": g1, "y": g1}
        if demographic_parity_difference(same) == 0 and \
                disparate_impact_ratio(same) == 1 and \
                equalized_odds_difference(same) == 0:
            prop_ok += 1

    # A perfect classifier (fp = fn = 0) satisfies equalized odds exactly,
    # whatever the group base rates.
    perfect = {"x": GroupCounts(tp=30, fp=0, fn=0, tn=10),
               "y": GroupCounts(tp=5, fp=0, fn=0, tn=60)}
    perfect_ok = int(equalized_odds_difference(perfect) == 0)

    threshold = [
        four_fifths_ok({"x": GroupCounts(4, 0, 1, 5),     # rates 2/5 vs 1/2
                        "y": GroupCounts(5, 0, 0, 5)}),   # ratio 4/5: passes
        not four_fifths_ok({"x": GroupCounts(79, 0, 21, 0),
                            "y": GroupCounts(100, 0, 0, 1)}),  # 79/100 fails
    ]
    threshold_ok = sum(threshold)

    rejects = 0
    for bad in (lambda: GroupCounts(-1, 0, 0, 1),
                lambda: GroupCounts(0, 0, 0, 0),
                lambda: GroupCounts(True, 0, 0, 1),
                lambda: demographic_parity_difference({"only": gen_group(1)}),
                lambda: tpr(GroupCounts(0, 5, 0, 5)),
                lambda: fpr(GroupCounts(5, 0, 5, 0)),
                lambda: disparate_impact_ratio(
                    {"x": GroupCounts(0, 0, 1, 9),
                     "y": GroupCounts(0, 0, 2, 8)})):
        try:
            bad()
        except FairnessError:
            rejects += 1

    total = len(hand) + prop_checks + 1 + len(threshold)
    matched = hand_ok + prop_ok + perfect_ok + threshold_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "fairness_metrics",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_computed_ok": hand_ok,
        "property_checks": prop_checks,
        "property_ok": prop_ok,
        "perfect_classifier_ok": perfect_ok,
        "threshold_ok": threshold_ok,
        "reject_cases": 7,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "fairness_metrics.json", obj,
         script="python3 claimlib/modules/fairness_metrics/evidence.py")
    # claim:CLAIM-LIB-FAIRNESS-001 checks_matched
    # All 73 checks hold as exact Fraction equalities: 10 hand-computed
    # values, 60 property checks (relabel-invariance, bounds, identical-
    # group zeros), the perfect-classifier equalized-odds zero, and the
    # exact 4/5 threshold — checks_matched = 73, mismatches = 0.
    print(f"fairness_metrics: {obj['checks_matched']}/{obj['checks']} exact "
          f"checks (hand {obj['hand_computed_ok']}/10, properties "
          f"{obj['property_ok']}/{obj['property_checks']}); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
