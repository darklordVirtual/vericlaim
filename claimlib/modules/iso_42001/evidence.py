# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ISO-42001-001 — the encoded AIMS structure matches
the published standard and the SoA arithmetic is exact and fail-closed.

Oracle: the published shape of ISO/IEC 42001:2023 — the harmonized
management-system clauses 4-10 and normative Annex A's 38 controls in 9
control objectives A.2-A.10 — verified against the standard's own table of
contents (clause and annex titles) with the per-group control counts
cross-checked against two independent identifier-level listings
(A.2: A.2.2-A.2.4; A.4: A.4.2-A.4.6; A.6: A.6.1.2-A.6.1.3 +
A.6.2.2-A.6.2.8; ...), which agree and sum to the normative total of 38.
SoA percentages are recomputed with exact Fraction arithmetic, and an SoA
declaring more controls applicable than a group contains is rejected.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from iso_42001 import (  # noqa: E402
    ANNEX_A_GROUPS, ANNEX_A_TOTAL, CLAUSES, AIMSError, clause_title, soa,
)
from _util import emit  # noqa: E402

PUBLISHED_COUNTS = {"A.2": 3, "A.3": 2, "A.4": 5, "A.5": 4, "A.6": 9,
                    "A.7": 5, "A.8": 4, "A.9": 3, "A.10": 3}


def run() -> dict:
    taxonomy = [
        len(CLAUSES) == 7 and sorted(CLAUSES) == list(range(4, 11)),
        CLAUSES[4] == "Context of the organization"
        and CLAUSES[10] == "Improvement",
        len(ANNEX_A_GROUPS) == 9,
        ANNEX_A_TOTAL == 38,
        {g: m["controls"] for g, m in ANNEX_A_GROUPS.items()}
        == PUBLISHED_COUNTS,
        ANNEX_A_GROUPS["A.6"]["name"] == "AI system life cycle",
        clause_title(9) == "Performance evaluation",
    ]
    taxonomy_ok = sum(taxonomy)

    full = soa({g: m["controls"] for g, m in ANNEX_A_GROUPS.items()})
    empty = soa({})
    partial = soa({"A.2": 3, "A.6": 4})
    soa_checks = [
        full["applicable"] == 38 and full["applicable_pct"] == 100.0
        and full["excluded"] == 0,
        empty["applicable"] == 0 and empty["excluded"] == 38,
        partial["applicable"] == 7,
        partial["applicable_pct"] == round(float(Fraction(7, 38) * 100), 2),
        partial["groups"]["A.6"]["excluded"] == 5,
        partial["groups"]["A.10"]["applicable"] == 0,
        sum(g["controls"] for g in full["groups"].values()) == 38,
    ]
    soa_ok = sum(soa_checks)

    rejects = 0
    for bad in (lambda: soa({"A.1": 1}),
                lambda: soa({"A.2": 4}),          # only 3 controls in A.2
                lambda: soa({"A.10": 4}),         # only 3 in A.10
                lambda: soa({"A.3": -1}),
                lambda: soa({"A.3": True}),
                lambda: soa("nope"),
                lambda: clause_title(3),
                lambda: clause_title(11)):
        try:
            bad()
        except AIMSError:
            rejects += 1

    total = len(taxonomy) + len(soa_checks)
    matched = taxonomy_ok + soa_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "iso_42001",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "clauses": len(CLAUSES),
        "annex_a_groups": len(ANNEX_A_GROUPS),
        "annex_a_controls": ANNEX_A_TOTAL,
        "reject_cases": 8,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "iso_42001.json", obj,
         script="python3 claimlib/modules/iso_42001/evidence.py")
    # claim:CLAIM-LIB-ISO-42001-001 checks_matched
    # All 14 checks pass: clauses 4-10 with their official titles, Annex A's
    # 38 controls in 9 objectives with per-group counts matching the
    # identifier-level listings, and Fraction-exact fail-closed SoA
    # accounting — checks_matched = 14, mismatches = 0.
    print(f"iso_42001: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['clauses']} clauses, {obj['annex_a_controls']} controls "
          f"in {obj['annex_a_groups']} objectives); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
