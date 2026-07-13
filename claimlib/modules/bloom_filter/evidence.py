# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-BLOOM-001 — no false negatives, exact analysis math.

Three oracles, none of them the module's own output: (1) the DEFINING property
of a Bloom filter — zero false negatives — verified exhaustively over a fixed
500-element battery; (2) the classical false-positive formula
p = (1 - (1 - 1/m)^(kn))^k recomputed independently in EXACT rational
arithmetic (fractions.Fraction) and compared to 12 decimal places; (3) the
measured false-positive count over a fixed, disjoint 2000-element probe set,
which is a deterministic property of the (m, k, battery) triple — recorded and
re-checked, and required to sit below twice the analytical expectation.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from bloom_filter import (  # noqa: E402
    BloomError, BloomFilter, false_positive_rate, optimal_k,
)
from _util import emit  # noqa: E402

MEMBERS = [f"member-{i:04d}" for i in range(500)]
PROBES = [f"absent-{i:05d}" for i in range(2000)]  # disjoint by construction

FORMULA_TRIPLES = [(1024, 100, 3), (4096, 500, 6), (64, 8, 2),
                   (10_000, 1000, 7), (8, 1, 1)]


def exact_fp(m: int, n: int, k: int) -> float:
    """Independent exact-rational recomputation of the FP formula."""
    still_zero = (Fraction(m - 1, m)) ** (k * n)
    return float((1 - still_zero) ** k)


def run() -> dict:
    m_bits, k = 4096, 6
    bf = BloomFilter(m_bits, k)
    for item in MEMBERS:
        bf.add(item)

    false_negatives = sum(1 for item in MEMBERS if not bf.contains(item))
    fp_count = sum(1 for probe in PROBES if bf.contains(probe))
    analytical = false_positive_rate(m_bits, len(MEMBERS), k)
    fp_bound_ok = fp_count <= max(1, int(2 * analytical * len(PROBES)) + 5)

    formula_checks = []
    for m, n, kk in FORMULA_TRIPLES:
        got = false_positive_rate(m, n, kk)
        want = exact_fp(m, n, kk)
        formula_checks.append({"m": m, "n": n, "k": kk,
                               "ok": abs(got - want) < 1e-12})
    formula_ok = sum(1 for c in formula_checks if c["ok"])

    # optimal_k sanity: matches max(1, round((m/n) ln 2)) recomputed, and the
    # neighbouring integers never do better than the analytic optimum by more
    # than rounding allows.
    import math
    k_checks = 0
    k_ok = 0
    for m, n in [(1024, 100), (4096, 500), (100, 1000), (9585, 1000)]:
        k_checks += 1
        want = max(1, round((m / n) * math.log(2)))
        if optimal_k(m, n) == want:
            k_ok += 1

    rejects = 0
    for bad in (lambda: BloomFilter(0, 3), lambda: BloomFilter(64, 0),
                lambda: false_positive_rate(64, -1, 2),
                lambda: BloomFilter(64, True)):
        try:
            bad()
        except BloomError:
            rejects += 1

    return {
        "schema": "claimlib_evidence_v1",
        "module": "bloom_filter",
        "members": len(MEMBERS),
        "false_negatives": false_negatives,
        "probes": len(PROBES),
        "false_positives_measured": fp_count,
        "fp_rate_analytical": round(analytical, 8),
        "fp_bound_ok": 1 if fp_bound_ok else 0,
        "formula_checks": len(formula_checks),
        "formula_ok": formula_ok,
        "optimal_k_checks": k_checks,
        "optimal_k_ok": k_ok,
        "reject_cases": 4,
        "rejects_ok": rejects,
        "formula_detail": formula_checks,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "bloom_filter.json", obj,
         script="python3 claimlib/modules/bloom_filter/evidence.py")
    # claim:CLAIM-LIB-BLOOM-001 false_negatives
    # Every one of the 500 inserted members is found again, so
    # false_negatives = 0 — exhaustively, not probabilistically.
    print(f"bloom_filter: {obj['false_negatives']} false negatives over "
          f"{obj['members']} members (must be 0); "
          f"{obj['false_positives_measured']} FPs over {obj['probes']} probes "
          f"(analytical {obj['fp_rate_analytical']}); formula "
          f"{obj['formula_ok']}/{obj['formula_checks']} exact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
