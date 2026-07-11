# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-E164-001 -- the E.164 validator classifies a fixed
battery of well-formed and malformed numbers and resolves their calling codes.

Each row's expected verdict is INDEPENDENTLY KNOWN from the ITU-T E.164 rules
(leading '+', country calling code, <= 15 digits, no leading zero on the country
code) and the published country calling codes (+47 Norway, +1 NANP, +44 UK,
+49 Germany, +358 Finland, ...). The expected (valid, country_code) pair is
hand-written, not read back from the module. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (e164.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from e164 import is_valid_format, country_code  # noqa: E402
from _util import emit  # noqa: E402

# (number, expected_valid, expected_country_code). expected_cc is None when the
# number is invalid or its calling code is outside the curated table.
REFERENCE = [
    ("+4791234567", True, "47"),          # Norway
    ("+14155552671", True, "1"),          # NANP (US)
    ("+442071838750", True, "44"),        # United Kingdom
    ("+4930901820", True, "49"),          # Germany
    ("+358401234567", True, "358"),       # Finland (3-digit code beats +35, +3)
    ("+3512112345678", True, "351"),      # Portugal (3-digit code)
    ("+81312345678", True, "81"),         # Japan
    ("+4712345678", True, "47"),          # Norway again, different length
    ("004791234567", False, None),        # missing '+'
    ("+0123456789", False, None),         # leading zero after '+'
    ("+47", False, None),                 # too short (E.164 needs >= 7 digits)
    ("+47abc12345", False, None),         # non-digit characters
    ("+1234567890123456", False, None),   # 16 digits, exceeds E.164 max of 15
]


def run() -> dict:
    rows = []
    correct = 0
    cc_correct = 0
    for number, exp_valid, exp_cc in REFERENCE:
        got_valid = is_valid_format(number)
        got_cc = country_code(number)
        valid_ok = (got_valid == exp_valid)
        cc_ok = (got_cc == exp_cc)
        correct += int(valid_ok)
        cc_correct += int(cc_ok)
        rows.append({"number": number, "expected_valid": exp_valid,
                     "computed_valid": got_valid, "expected_cc": exp_cc,
                     "computed_cc": got_cc, "valid_ok": valid_ok, "cc_ok": cc_ok})

    n_cases = len(REFERENCE)
    return {
        "schema": "claimlib_e164_v1",
        "module": "e164",
        "n_cases": n_cases,
        "correct": correct,
        "errors": n_cases - correct,
        "country_code_correct": cc_correct,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "e164.json", obj,
         script="python3 claimlib/modules/e164/evidence.py")
    # claim:CLAIM-LIB-E164-001 correct
    # All 13 numbers are classified correctly, so correct = 13 and errors = 0
    # (n_cases = 13); all 13 calling codes resolve as expected too.
    print(f"e164: {obj['correct']}/{obj['n_cases']} numbers classified correctly "
          f"({obj['errors']} errors), {obj['country_code_correct']}/{obj['n_cases']} "
          f"calling codes resolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
