# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-AI-RMF-001 — the encoded AI RMF Core matches the
published framework and the coverage arithmetic is exact.

Oracle: the published shape of NIST AI 100-1 (AI RMF 1.0, January 2023),
verified against the primary PDF and NIST's own airc.nist.gov rendering,
identifier by identifier: four functions (GOVERN/MAP/MEASURE/MANAGE),
category counts 6/5/4/4 totalling 19, subcategory counts 19/18/22/13
totalling 72, and the seven characteristics of trustworthy AI. Coverage
percentages are recomputed with exact Fraction arithmetic on three fixed
programmes. Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from nist_ai_rmf import (  # noqa: E402
    CATEGORIES, FUNCTIONS, SUBCATEGORIES, TRUSTWORTHY, RMFError,
    category_ids, coverage,
)
from _util import emit  # noqa: E402


def run() -> dict:
    taxonomy = [
        FUNCTIONS == ("GOVERN", "MAP", "MEASURE", "MANAGE"),
        CATEGORIES == {"GOVERN": 6, "MAP": 5, "MEASURE": 4, "MANAGE": 4},
        sum(CATEGORIES.values()) == 19,
        SUBCATEGORIES == {"GOVERN": 19, "MAP": 18, "MEASURE": 22,
                          "MANAGE": 13},
        sum(SUBCATEGORIES.values()) == 72,
        len(TRUSTWORTHY) == 7,
        TRUSTWORTHY[0] == "Valid and Reliable",
        category_ids("GOVERN") == [f"GOVERN {i}" for i in range(1, 7)],
        len(category_ids("MANAGE")) == 4,
    ]
    taxonomy_ok = sum(taxonomy)

    full = coverage([cid for fn in FUNCTIONS for cid in category_ids(fn)])
    empty = coverage([])
    partial = coverage(["GOVERN 1", "GOVERN 2", "MAP 3", "MEASURE 4"])
    cov = [
        full["addressed"] == 19 and full["coverage_pct"] == 100.0,
        all(f["gaps"] == [] for f in full["functions"].values()),
        empty["addressed"] == 0 and empty["coverage_pct"] == 0.0,
        partial["addressed"] == 4,
        partial["coverage_pct"] == round(float(Fraction(4, 19) * 100), 2),
        partial["functions"]["GOVERN"]["addressed"] == 2,
        partial["functions"]["GOVERN"]["coverage_pct"] == round(
            float(Fraction(2, 6) * 100), 2),
        partial["functions"]["MANAGE"]["addressed"] == 0,
        len(partial["functions"]["MAP"]["gaps"]) == 4,
    ]
    cov_ok = sum(cov)

    rejects = 0
    for bad in (lambda: category_ids("OVERSEE"),
                lambda: coverage(["GOVERN 7"]),
                lambda: coverage(["MAP 0"]),
                lambda: coverage(["govern 1"])):
        try:
            bad()
        except RMFError:
            rejects += 1

    total = len(taxonomy) + len(cov)
    matched = taxonomy_ok + cov_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "nist_ai_rmf",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "functions": len(FUNCTIONS),
        "categories_total": sum(CATEGORIES.values()),
        "subcategories_total": sum(SUBCATEGORIES.values()),
        "trustworthy_characteristics": len(TRUSTWORTHY),
        "reject_cases": 4,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "nist_ai_rmf.json", obj,
         script="python3 claimlib/modules/nist_ai_rmf/evidence.py")
    # claim:CLAIM-LIB-AI-RMF-001 checks_matched
    # All 18 checks pass: the four functions with published category counts
    # 6/5/4/4 (19 total) and subcategory counts 19/18/22/13 (72 total), the
    # seven trustworthy-AI characteristics, and Fraction-exact coverage on
    # three fixed programmes — checks_matched = 18, mismatches = 0.
    print(f"nist_ai_rmf: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['functions']} functions, {obj['categories_total']} "
          f"categories, {obj['subcategories_total']} subcategories, "
          f"{obj['trustworthy_characteristics']} characteristics); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
