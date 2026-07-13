# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CIS-001 -- the encoded CIS Controls v8.1 taxonomy
matches the published framework and the coverage arithmetic is correct.

The taxonomy is INDEPENDENTLY KNOWN from the CIS Critical Security Controls
v8.1 guide (Center for Internet Security, June 2024): 18 Controls, 153
Safeguards, with cumulative Implementation Group totals IG1 = 56, IG2 = 130
(IG1 + 74) and IG3 = 153 (IG2 + 23), and per-control counts published in each
Control's "Safeguards: N | IG1: a/N | IG2: b/N | IG3: N/N" header. The
evidence checks that exactly Controls 1..18 are present, that every Control's
title and (total, IG1, IG2, IG3) row matches the published table with the
cumulative-IG invariant 0 <= IG1 <= IG2 <= IG3 = total, that the summed
totals reproduce the published framework-wide counts, and that coverage()
computes hand-verified values (e.g. Controls {1, 2} -> 5/56 IG1 safeguards ->
0.0893). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (cis_controls.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from cis_controls import CONTROLS, coverage, ig_totals  # noqa: E402
from _util import emit  # noqa: E402

# Published per-control rows: number -> (title, total, IG1, IG2, IG3).
# Transcribed from the CIS Controls v8.1 guide (June 2024), one header line
# per Control ("Safeguards: 5 | IG1: 2/5 | IG2: 4/5 | IG3: 5/5" etc.); the
# titles also match the CIS Controls list at cisecurity.org.
EXPECTED_CONTROLS = {
    1: ("Inventory and Control of Enterprise Assets", 5, 2, 4, 5),
    2: ("Inventory and Control of Software Assets", 7, 3, 6, 7),
    3: ("Data Protection", 14, 6, 12, 14),
    4: ("Secure Configuration of Enterprise Assets and Software", 12, 7, 11, 12),
    5: ("Account Management", 6, 4, 6, 6),
    6: ("Access Control Management", 8, 5, 7, 8),
    7: ("Continuous Vulnerability Management", 7, 4, 7, 7),
    8: ("Audit Log Management", 12, 3, 11, 12),
    9: ("Email and Web Browser Protections", 7, 2, 6, 7),
    10: ("Malware Defenses", 7, 3, 7, 7),
    11: ("Data Recovery", 5, 4, 5, 5),
    12: ("Network Infrastructure Management", 8, 1, 7, 8),
    13: ("Network Monitoring and Defense", 11, 0, 6, 11),
    14: ("Security Awareness and Skills Training", 9, 8, 9, 9),
    15: ("Service Provider Management", 7, 1, 4, 7),
    16: ("Application Software Security", 14, 0, 11, 14),
    17: ("Incident Response Management", 9, 3, 8, 9),
    18: ("Penetration Testing", 5, 0, 3, 5),
}

# Published framework-wide totals (CIS Controls v8.1 / implementation-groups
# page): 153 Safeguards; IG1 = 56; IG2 adds 74 -> 130; IG3 adds 23 -> 153.
PUBLISHED_TOTAL = 153
PUBLISHED_IG1 = 56
PUBLISHED_IG2 = 130
PUBLISHED_IG3 = 153
PUBLISHED_IG2_INCREMENT = 74
PUBLISHED_IG3_INCREMENT = 23


def run() -> dict:
    # 1 check: exactly Controls 1..18 are present.
    control_numbers_ok = int(set(CONTROLS) == set(range(1, 19)))

    # 18 checks: each Control's row matches the published table AND satisfies
    # the cumulative-IG invariant 0 <= IG1 <= IG2 <= IG3 = total.
    taxonomy_correct = 0
    for number in sorted(EXPECTED_CONTROLS):
        row = CONTROLS.get(number)
        expected = EXPECTED_CONTROLS[number]
        if row == expected:
            _, total, ig1, ig2, ig3 = row
            if 0 <= ig1 <= ig2 <= ig3 == total:
                taxonomy_correct += 1

    # 6 checks: the summed totals reproduce the published counts.
    totals = ig_totals()
    totals_checks = [
        totals["total"] == PUBLISHED_TOTAL,
        totals["IG1"] == PUBLISHED_IG1,
        totals["IG2"] == PUBLISHED_IG2,
        totals["IG3"] == PUBLISHED_IG3,
        totals["IG2"] - totals["IG1"] == PUBLISHED_IG2_INCREMENT,
        totals["IG3"] - totals["IG2"] == PUBLISHED_IG3_INCREMENT,
    ]
    totals_correct = sum(int(c) for c in totals_checks)

    # 13 checks: coverage arithmetic, hand-verified.
    #   {1, 2}: IG1 safeguards 2 + 3 = 5 -> 5/56 = 0.0893; IG3 5 + 7 = 12 ->
    #   12/153 = 0.0784; controls 2/18 = 0.1111.
    #   {13, 16, 18} have zero IG1 safeguards -> IG1 coverage 0.0; their IG3
    #   safeguards 11 + 14 + 5 = 30.
    empty = coverage([])
    full = coverage(sorted(CONTROLS))
    two = coverage([1, 2])
    no_ig1 = coverage([13, 16, 18])
    all_but_18 = coverage(list(range(1, 18)))
    coverage_checks = [
        empty["controls"]["implemented"] == 0,
        empty["safeguards"]["IG1"]["coverage"] == 0.0,
        full["controls"]["coverage"] == 1.0,
        full["safeguards"]["IG1"]["coverage"] == 1.0,
        full["safeguards"]["IG2"]["coverage"] == 1.0,
        full["safeguards"]["IG3"]["coverage"] == 1.0,
        two["controls"]["coverage"] == 0.1111,
        two["safeguards"]["IG1"]["implemented"] == 5,
        two["safeguards"]["IG1"]["coverage"] == 0.0893,
        two["safeguards"]["IG3"]["coverage"] == 0.0784,
        no_ig1["safeguards"]["IG1"]["coverage"] == 0.0,
        no_ig1["safeguards"]["IG3"]["implemented"] == 30,
        all_but_18["controls"]["missing"] == [18],
    ]
    coverage_correct = sum(int(c) for c in coverage_checks)

    checks = 1 + len(EXPECTED_CONTROLS) + len(totals_checks) + len(coverage_checks)
    checks_matched = (control_numbers_ok + taxonomy_correct
                      + totals_correct + coverage_correct)
    return {
        "schema": "claimlib_cis_controls_v1",
        "module": "cis_controls",
        "n_controls": len(CONTROLS),
        "n_safeguards": totals["total"],
        "ig1_safeguards": totals["IG1"],
        "ig2_safeguards": totals["IG2"],
        "ig3_safeguards": totals["IG3"],
        "checks": checks,
        "checks_matched": checks_matched,
        "mismatches": checks - checks_matched,
        "control_numbers_ok": bool(control_numbers_ok),
        "taxonomy_correct": taxonomy_correct,
        "totals_correct": totals_correct,
        "coverage_correct": coverage_correct,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "cis_controls.json", obj,
         script="python3 claimlib/modules/cis_controls/evidence.py")
    # claim:CLAIM-LIB-CIS-001 checks_matched
    # Controls 1..18 present, all 18 published rows match, all 6 framework
    # totals (153 / 56 / 130 / 153, +74, +23) and 13 coverage checks hold, so
    # checks_matched = 38 and mismatches = 0.
    print(f"cis_controls: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['n_controls']} controls, {obj['n_safeguards']} safeguards, "
          f"IG1 {obj['ig1_safeguards']} / IG2 {obj['ig2_safeguards']} / "
          f"IG3 {obj['ig3_safeguards']}; taxonomy {obj['taxonomy_correct']}/18, "
          f"totals {obj['totals_correct']}/6, coverage {obj['coverage_correct']}/13); "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
