# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-LTT-001 — the Learn-then-Test machinery is exact
and its error guarantees are ENUMERATED as exact probability calculations.

Oracles, none the module's own output: (1) the exact binomial tail p-value
against an independent Fraction re-derivation and hand anchors
(P(Bin(10, 1/2) <= 0) = 1/1024 exactly); (2) SUPER-UNIFORMITY ENUMERATED:
under the null R = alpha exactly, P(p <= u) <= u must hold for every
threshold u — verified by enumerating ALL n+1 binomial outcomes with exact
probabilities, for every (n, alpha) on a fixed grid (the property the LTT
guarantee rests on, proven by exhaustion, not sampled); (3) FWER
ENUMERATED: for K independent null grid points, the exact probability that
Bonferroni rejects ANY true null — summed over all (n+1)^K joint outcomes
as exact Fractions — is <= delta, and likewise for fixed-sequence testing
along any declared order; (4) procedure semantics: fixed-sequence stops at
the first non-rejection, Bonferroni is order-free, both return the honest
empty set when nothing is certifiable. Deterministic: same artifact always.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from learn_then_test import (  # noqa: E402
    LTTError, binom_tail_p, ltt_bonferroni, ltt_fixed_sequence,
)
from _util import emit  # noqa: E402


def pmf(n: int, a: Fraction, k: int) -> Fraction:
    return Fraction(comb(n, k)) * a ** k * (1 - a) ** (n - k)


def run() -> dict:
    hand = [
        binom_tail_p(10, 0, "0.5") == Fraction(1, 1024),
        binom_tail_p(10, 10, "0.5") == 1,
        binom_tail_p(4, 1, "0.5") == Fraction(5, 16),
        binom_tail_p(3, 0, "0.1") == Fraction(729, 1000),
        # independent re-derivation on a fixed pair
        binom_tail_p(7, 2, "0.3") == sum(
            pmf(7, Fraction(3, 10), i) for i in range(3)),
    ]
    hand_ok = sum(hand)

    # Super-uniformity, enumerated: under the null (true risk == alpha),
    # P(p <= u) <= u for all u — check at every achievable p-value.
    su_checks = 0
    su_ok = 0
    for n, alpha in [(6, Fraction(1, 4)), (9, Fraction(1, 2)),
                     (12, Fraction(1, 10))]:
        pvals = [binom_tail_p(n, k, alpha) for k in range(n + 1)]
        for u in sorted(set(pvals)):
            su_checks += 1
            mass = sum(pmf(n, alpha, k) for k in range(n + 1)
                       if pvals[k] <= u)
            if mass <= u:
                su_ok += 1

    # FWER, enumerated: K independent grid points, ALL true nulls
    # (true risk exactly alpha). Exact P(any rejection) over all joint
    # outcomes must be <= delta for Bonferroni; for fixed-sequence, the
    # first rejection already bounds the walk, so P(any false rejection)
    # = P(first test rejects) <= delta.
    n, K = 6, 3
    alpha = Fraction(1, 4)
    delta = Fraction(1, 10)
    lams = [f"l{j}" for j in range(K)]
    bonf_reject_any = Fraction(0)
    fixed_reject_any = Fraction(0)
    for outcome in product(range(n + 1), repeat=K):
        prob = Fraction(1)
        for k in outcome:
            prob *= pmf(n, alpha, k)
        fails = dict(zip(lams, outcome))
        if ltt_bonferroni(fails, n, alpha, delta):
            bonf_reject_any += prob
        if ltt_fixed_sequence(fails, lams, n, alpha, delta):
            fixed_reject_any += prob
    fwer_ok = int(bonf_reject_any <= delta) \
        + int(fixed_reject_any <= delta)

    # Procedure semantics on a fixed scenario: n=50, grid of 4 lambdas.
    fails = {"a": 0, "b": 2, "c": 12, "d": 1}
    semantics = [
        # Bonferroni at alpha=0.2, delta=0.05: p(0) tiny, p(12) huge
        "a" in ltt_bonferroni(fails, 50, "0.2", "0.05"),
        "c" not in ltt_bonferroni(fails, 50, "0.2", "0.05"),
        # fixed sequence stops at first non-rejection: with c early in the
        # order, later certifiable lambdas are never reached
        ltt_fixed_sequence(fails, ["a", "c", "b"], 50, "0.2", "0.05")
        == {"a"},
        ltt_fixed_sequence(fails, ["a", "b", "d", "c"], 50, "0.2", "0.05")
        == {"a", "b", "d"},
        # honest empty set when nothing is certifiable
        ltt_bonferroni({"x": 20, "y": 25}, 50, "0.2", "0.05") == set(),
        # Bonferroni is order-free (dict order cannot matter)
        ltt_bonferroni(dict(reversed(list(fails.items()))), 50, "0.2",
                       "0.05")
        == ltt_bonferroni(fails, 50, "0.2", "0.05"),
    ]
    semantics_ok = sum(semantics)

    rejects = 0
    for bad in (lambda: binom_tail_p(0, 0, "0.5"),
                lambda: binom_tail_p(5, 6, "0.5"),
                lambda: binom_tail_p(5, -1, "0.5"),
                lambda: binom_tail_p(5, 2, "0"),
                lambda: binom_tail_p(5, 2, "1"),
                lambda: ltt_bonferroni({}, 5, "0.2", "0.1"),
                lambda: ltt_bonferroni({"a": True}, 5, "0.2", "0.1"),
                lambda: ltt_fixed_sequence({"a": 1}, [], 5, "0.2", "0.1"),
                lambda: ltt_fixed_sequence({"a": 1}, ["a", "a"], 5, "0.2",
                                           "0.1"),
                lambda: ltt_fixed_sequence({"a": 1}, ["ghost"], 5, "0.2",
                                           "0.1")):
        try:
            bad()
        except LTTError:
            rejects += 1

    total = len(hand) + su_checks + 2 + len(semantics)
    matched = hand_ok + su_ok + fwer_ok + semantics_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "learn_then_test",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "hand_ok": hand_ok,
        "super_uniformity_checks": su_checks,
        "super_uniformity_ok": su_ok,
        "fwer_enumerations_ok": fwer_ok,
        "joint_outcomes_enumerated": (n + 1) ** K,
        "semantics_ok": semantics_ok,
        "reject_cases": 10,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "learn_then_test.json", obj,
         script="python3 claimlib/modules/learn_then_test/evidence.py")
    # claim:CLAIM-LIB-LTT-001 checks_matched
    # All 43 checks hold as exact probability calculations: 5 hand-computed
    # binomial p-values, super-uniformity enumerated at every achievable
    # threshold over three (n, alpha) settings, family-wise error for both
    # Bonferroni and fixed-sequence testing enumerated exactly over all
    # 343 joint outcomes of 3 independent nulls (both <= delta), and 6
    # procedure-semantics checks — mismatches = 0.
    print(f"learn_then_test: {obj['checks_matched']}/{obj['checks']} checks "
          f"(super-uniformity {obj['super_uniformity_ok']}/"
          f"{obj['super_uniformity_checks']}, FWER enumerations "
          f"{obj['fwer_enumerations_ok']}/2 over "
          f"{obj['joint_outcomes_enumerated']} outcomes); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
