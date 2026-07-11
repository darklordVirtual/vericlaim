# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-IBAN-001 -- the IBAN validator classifies a fixed
table of officially published IBANs and deliberately corrupted variants
correctly, and reconstructs the embedded check digits of every valid one.

The expected label of each row is INDEPENDENTLY KNOWN: the valid IBANs are the
canonical published examples from the ISO 13616 / SWIFT IBAN registry and the
national examples on Wikipedia's "International Bank Account Number" page; the
invalid rows are those same numbers with a single mutated digit (which breaks
the MOD-97 residue by construction). The check-digit reconstruction is an
independent cross-check: recomputing the two check digits from the BBAN must
reproduce the digits actually embedded in each published IBAN. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (iban.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from iban import is_valid, check_digits, electronic_format  # noqa: E402
from _util import emit  # noqa: E402

# (iban, expected_valid). Valid rows are the canonical published registry /
# Wikipedia example IBANs; invalid rows mutate exactly one digit of a valid one.
REFERENCE = [
    ("GB82 WEST 1234 5698 7654 32", True),        # United Kingdom (registry example)
    ("DE89 3704 0044 0532 0130 00", True),        # Germany
    ("FR14 2004 1010 0505 0001 3M02 606", True),  # France
    ("NO93 8601 1117 947", True),                 # Norway
    ("ES91 2100 0418 4502 0005 1332", True),      # Spain
    ("CH93 0076 2011 6238 5295 7", True),         # Switzerland
    ("NL91 ABNA 0417 1643 00", True),             # Netherlands
    ("BE68 5390 0754 7034", True),                # Belgium
    ("GB00 WEST 1234 5698 7654 32", False),       # UK, check digits zeroed
    ("DE89 3704 0044 0532 0130 01", False),       # Germany, last digit +1
    ("NO93 8601 1117 948", False),                # Norway, last digit +1
    ("BE68 5390 0754 7035", False),               # Belgium, last digit +1
]

# Each valid IBAN's BBAN + country must reconstruct its embedded check digits.
# (country, bban, embedded_check) drawn from the valid rows above.
CHECK_DIGIT_CASES = [
    ("GB", "WEST12345698765432", "82"),
    ("DE", "370400440532013000", "89"),
    ("NO", "86011117947", "93"),
    ("ES", "21000418450200051332", "91"),
    ("BE", "539007547034", "68"),
]


def run() -> dict:
    rows = []
    correct = 0
    for iban, expected in REFERENCE:
        got = is_valid(iban)
        ok = (got == expected)
        correct += int(ok)
        rows.append({"iban": electronic_format(iban), "expected_valid": expected,
                     "computed_valid": got, "correct": ok})

    cd_rows = []
    cd_correct = 0
    for country, bban, embedded in CHECK_DIGIT_CASES:
        got = check_digits(country, bban)
        ok = (got == embedded)
        cd_correct += int(ok)
        cd_rows.append({"country": country, "bban": bban,
                        "embedded_check": embedded, "computed_check": got,
                        "correct": ok})

    n_cases = len(REFERENCE)
    errors = n_cases - correct
    return {
        "schema": "claimlib_iban_v1",
        "module": "iban",
        "n_cases": n_cases,
        "correct": correct,
        "errors": errors,
        "check_digit_cases": len(CHECK_DIGIT_CASES),
        "check_digit_correct": cd_correct,
        "cases": rows,
        "check_digit_detail": cd_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "iban.json", obj,
         script="python3 claimlib/modules/iban/evidence.py")
    # claim:CLAIM-LIB-IBAN-001 correct
    # All 12 reference IBANs are classified correctly, so correct = 12 and
    # errors = 0 (n_cases = 12); all 5 check-digit reconstructions match too.
    print(f"iban: {obj['correct']}/{obj['n_cases']} reference IBANs classified "
          f"correctly ({obj['errors']} errors), "
          f"{obj['check_digit_correct']}/{obj['check_digit_cases']} check digits reconstructed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
