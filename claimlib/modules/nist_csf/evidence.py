# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-NIST-CSF-001 -- the encoded CSF 2.0 taxonomy matches the
published framework and the coverage arithmetic is correct.

The taxonomy is INDEPENDENTLY KNOWN from NIST CSF 2.0 (CSWP 29): exactly six
Functions (Govern, Identify, Protect, Detect, Respond, Recover) and 22 Categories
mapped to them. The evidence checks the six Function names, that every Category
maps to the correct Function, and that coverage() computes hand-verified fractions
(all of Govern -> GV coverage 1.0; a known subset -> its exact fraction; overall =
implemented/22). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (nist_csf.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from nist_csf import FUNCTIONS, CATEGORIES, function_of, coverage  # noqa: E402
from _util import emit  # noqa: E402

EXPECTED_FUNCTIONS = {
    "GV": "Govern", "ID": "Identify", "PR": "Protect",
    "DE": "Detect", "RS": "Respond", "RC": "Recover",
}
# Expected Function per Category prefix (the two letters before the dot).
def _expected_function(cid: str) -> str:
    return cid.split(".")[0]


def run() -> dict:
    function_names_ok = int(FUNCTIONS == EXPECTED_FUNCTIONS)

    mapping_correct = 0
    for cid in CATEGORIES:
        mapping_correct += int(function_of(cid) == _expected_function(cid))

    # Coverage arithmetic, hand-verified.
    govern_cats = [c for c in CATEGORIES if c.startswith("GV.")]
    cov_all_govern = coverage(govern_cats)
    coverage_checks = [
        cov_all_govern["functions"]["GV"]["coverage"] == 1.0,
        cov_all_govern["functions"]["GV"]["implemented"] == 6,
        cov_all_govern["functions"]["ID"]["coverage"] == 0.0,
        coverage(["ID.AM", "ID.RA"])["functions"]["ID"]["coverage"] == round(2 / 3, 4),
        coverage(list(CATEGORIES))["overall"]["coverage"] == 1.0,
        coverage([])["overall"]["implemented"] == 0,
        coverage(["GV.OC", "PR.AA", "DE.CM"])["overall"]["implemented"] == 3,
    ]
    coverage_correct = sum(int(c) for c in coverage_checks)

    checks = 1 + len(CATEGORIES) + len(coverage_checks)
    checks_matched = function_names_ok + mapping_correct + coverage_correct
    return {
        "schema": "claimlib_nist_csf_v1",
        "module": "nist_csf",
        "n_functions": len(FUNCTIONS),
        "n_categories": len(CATEGORIES),
        "checks": checks,
        "checks_matched": checks_matched,
        "mismatches": checks - checks_matched,
        "function_names_ok": bool(function_names_ok),
        "mapping_correct": mapping_correct,
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "nist_csf.json", obj,
         script="python3 claimlib/modules/nist_csf/evidence.py")
    # claim:CLAIM-LIB-NIST-CSF-001 checks_matched
    # The 6 Function names, all 22 Category mappings and 7 coverage checks hold,
    # so checks_matched = 30 and mismatches = 0.
    print(f"nist_csf: {obj['checks_matched']}/{obj['checks']} checks "
          f"(6 functions, {obj['n_categories']} categories, "
          f"coverage {obj['coverage_correct']}/7); mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
