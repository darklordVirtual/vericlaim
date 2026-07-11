# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-LUHN-001 — the Luhn checksum classifies a fixed
table of published known-valid / known-invalid numbers correctly.

Runs the reusable ``luhn`` module over a battery of numbers whose Luhn status
is independently known (Wikipedia's worked example plus payment-card test
numbers published by card networks / processors, and deliberately corrupted
variants) and records how many are classified as expected. Deterministic:
same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (luhn.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from luhn import is_valid, check_digit  # noqa: E402
from _util import emit  # noqa: E402

# (number, expected_valid). The expected label is the INDEPENDENTLY KNOWN
# Luhn status, not this module's output:
#   * 79927398713 valid / ...714 invalid  -> Wikipedia "Luhn algorithm" example.
#   * 4111111111111111 (Visa), 5555555555554444 (Mastercard),
#     378282246310005 (Amex), 6011111111111117 (Discover),
#     371449635398431 (Amex), 30569309025904 (Diners) -> standard test card
#     numbers published by card networks / Stripe / PayPal docs; all are
#     documented as Luhn-valid.
#   * "0" -> single zero digit, trivially valid (checksum 0).
#   * The ...112 / ...714 / ...4445 rows are those valid numbers with the
#     final digit shifted by one, which by construction breaks the mod-10
#     residue -> invalid.
#   * "1234567890123456" -> a plain ascending sequence, not a valid Luhn
#     number.
REFERENCE = [
    ("4111111111111111", True),   # Visa test card
    ("5555555555554444", True),   # Mastercard test card
    ("378282246310005", True),    # American Express test card
    ("6011111111111117", True),   # Discover test card
    ("371449635398431", True),    # American Express test card
    ("30569309025904", True),     # Diners Club test card
    ("79927398713", True),        # Wikipedia Luhn example
    ("0", True),                  # trivial single-digit valid
    ("4111111111111112", False),  # Visa card, corrupted check digit
    ("5555555555554445", False),  # Mastercard card, corrupted check digit
    ("79927398714", False),       # Wikipedia example, off by one
    ("1234567890123456", False),  # ascending sequence, not Luhn-valid
]

# Numbers whose check digit is independently known, used to exercise
# check_digit(). "79927398713" is valid, so check_digit("7992739871") == 3
# (Wikipedia). The card test numbers above are valid, so stripping their last
# digit must reproduce it.
CHECK_DIGIT_CASES = [
    ("7992739871", 3),        # 79927398713 valid (Wikipedia) -> last digit 3
    ("411111111111111", 1),   # 4111111111111111 valid -> last digit 1
    ("555555555555444", 4),   # 5555555555554444 valid -> last digit 4
    ("37828224631000", 5),    # 378282246310005 valid -> last digit 5
]


def run() -> dict:
    rows = []
    correct = 0
    for number, expected in REFERENCE:
        got = is_valid(number)
        ok = (got == expected)
        correct += int(ok)
        rows.append({"number": number, "expected_valid": expected,
                     "computed_valid": got, "correct": ok})

    cd_rows = []
    cd_correct = 0
    for partial, expected in CHECK_DIGIT_CASES:
        got = check_digit(partial)
        ok = (got == expected)
        cd_correct += int(ok)
        cd_rows.append({"partial": partial, "expected_check_digit": expected,
                        "computed_check_digit": got, "correct": ok})

    n_cases = len(REFERENCE)
    errors = n_cases - correct
    return {
        "schema": "claimlib_luhn_v1",
        "module": "luhn",
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
    emit(HERE / "artifacts" / "luhn.json", obj,
         script="python3 claimlib/modules/luhn/evidence.py")
    # claim:CLAIM-LIB-LUHN-001 correct
    # All 12 reference numbers are classified correctly, so
    # correct = 12 and errors = 0 (n_cases = 12).
    print(f"luhn: {obj['correct']}/{obj['n_cases']} reference numbers "
          f"classified correctly ({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
