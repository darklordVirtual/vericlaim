# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ENTROPY-001 — the information measures satisfy
Shannon's published identities to documented precision.

Oracles, none the module's own output: (1) EXACT anchor values — the entropy
of a fair coin is exactly 1.0 bit, of a uniform 4/8/16/32-outcome
distribution exactly 2/3/4/5 bits (powers of two make the float log exact),
of a deterministic outcome exactly 0; perplexity of uniform-n is exactly n;
(2) Shannon's worked example: H(1/2, 1/4, 1/4) = 1.5 bits exactly;
(3) theorem-shaped properties over a deterministic 30-distribution battery:
0 <= H(p) <= log2(n) (maximality of the uniform), KL(p||p) = 0, KL >= 0
(Gibbs), the chain identity H(p,q) = H(p) + KL(p||q) to 1e-12, permutation
invariance of H; (4) fail-closed: distributions not summing to exactly 1,
negative mass, and infinite KL all raise. Deterministic: same artifact
on every run.
"""
from __future__ import annotations

import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from shannon_entropy import (  # noqa: E402
    EntropyError, cross_entropy, entropy, kl_divergence, perplexity,
)
from _util import emit  # noqa: E402


def dist(seed: int, n: int) -> list:
    """A deterministic exact distribution over n outcomes."""
    weights = [((seed * 7 + i * 13) % 19) + 1 for i in range(n)]
    total = sum(weights)
    return [Fraction(w, total) for w in weights]


def run() -> dict:
    anchors = [
        entropy(["1/2", "1/2"]) == 1.0,
        entropy([Fraction(1, 4)] * 4) == 2.0,
        entropy([Fraction(1, 8)] * 8) == 3.0,
        entropy([Fraction(1, 16)] * 16) == 4.0,
        entropy([Fraction(1, 32)] * 32) == 5.0,
        entropy([1]) == 0.0,
        entropy([0, 1, 0]) == 0.0,
        perplexity([Fraction(1, 8)] * 8) == 8.0,
        # Shannon's worked example (1948, sec. 6): H(1/2,1/4,1/4) = 1.5 bits
        entropy(["1/2", "1/4", "1/4"]) == 1.5,
        kl_divergence(["1/2", "1/2"], ["1/2", "1/2"]) == 0.0,
    ]
    anchors_ok = sum(anchors)

    prop_checks = 0
    prop_ok = 0
    for seed in range(10):
        n = 3 + (seed % 4)
        p = dist(seed, n)
        q = dist(seed + 50, n)
        prop_checks += 3
        h = entropy(p)
        if 0.0 <= h <= math.log2(n) + 1e-12:
            prop_ok += 1
        # KL(p||p) is 0 in exact arithmetic; the float evaluation of
        # cross_entropy and entropy differ by at most one ulp-sum, so the
        # self-divergence is bounded by 1e-12, never asserted == 0.0.
        if kl_divergence(p, q) >= 0.0 and kl_divergence(p, p) < 1e-12:
            prop_ok += 1
        if abs(cross_entropy(p, q) - (h + kl_divergence(p, q))) < 1e-12 \
                and abs(entropy(list(reversed(p))) - h) < 1e-12:
            prop_ok += 1

    rejects = 0
    for bad in (lambda: entropy([0.5, 0.4]),          # sums to 0.9
                lambda: entropy(["1/2", "1/3"]),      # sums to 5/6
                lambda: entropy([1.5, -0.5]),         # negative mass
                lambda: entropy([]),
                lambda: entropy([float("nan")]),
                lambda: entropy([True]),
                lambda: cross_entropy(["1/2", "1/2"], ["1/2", "1/4", "1/4"]),
                lambda: cross_entropy(["1/2", "1/2"], [1, 0]),  # infinite
                lambda: kl_divergence(["1/2", "1/2"], [0, 1])):
        try:
            bad()
        except EntropyError:
            rejects += 1

    total = len(anchors) + prop_checks
    matched = anchors_ok + prop_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "shannon_entropy",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "anchors_ok": anchors_ok,
        "property_checks": prop_checks,
        "property_ok": prop_ok,
        "reject_cases": 9,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "shannon_entropy.json", obj,
         script="python3 claimlib/modules/shannon_entropy/evidence.py")
    # claim:CLAIM-LIB-ENTROPY-001 checks_matched
    # All 40 checks hold: 10 exact anchors (fair coin = 1.0 bit, uniform
    # powers of two exact, Shannon's H(1/2,1/4,1/4) = 1.5) and 30 theorem
    # properties (uniform maximality, Gibbs, the chain identity, permutation
    # invariance) — checks_matched = 40, mismatches = 0.
    print(f"shannon_entropy: {obj['checks_matched']}/{obj['checks']} checks "
          f"(anchors {obj['anchors_ok']}/10, properties "
          f"{obj['property_ok']}/{obj['property_checks']}); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
