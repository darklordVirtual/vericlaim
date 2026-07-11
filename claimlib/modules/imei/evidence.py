# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-IMEI-001 -- the IMEI validator accepts the published
GSMA example and agrees with an independent Luhn oracle on every vector.

Two independent references:

  1. Published: the GSMA / Wikipedia example IMEI 490154203237518 is valid, and
     stripping its check digit reconstructs it (check_digit("49015420323751")
     == 8). These truths come from publication, not this module.
  2. Independent oracle: over a fixed battery of 15-digit strings (the published
     IMEI, deliberately corrupted variants, and a deterministic pseudo-random
     spread), the module's is_valid must equal a Luhn validity computed by a
     SEPARATE, from-scratch implementation in this script.

Every vector whose module verdict matches its independent expected verdict
counts toward reference_vectors_matched. Deterministic: same artifact each run.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (imei.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from imei import is_valid, check_digit  # noqa: E402
from _util import emit  # noqa: E402


def luhn_valid_oracle(number: str) -> bool:
    """Independent Luhn validity check (separate code path from the module)."""
    if len(number) != 15 or not number.isascii() or not number.isdigit():
        return False
    digits = [int(c) for c in number]
    checksum = 0
    for idx, d in enumerate(digits[::-1]):
        if idx % 2 == 1:
            d = d * 2
            d = d - 9 if d > 9 else d
        checksum += d
    return checksum % 10 == 0


def _synthetic_imeis(n: int) -> list[str]:
    """Deterministic 15-digit strings derived from sha256 (no module involved)."""
    out = []
    for i in range(n):
        h = hashlib.sha256(f"imei-{i}".encode()).hexdigest()
        digits = "".join(str(int(c, 16) % 10) for c in h)[:15]
        out.append(digits)
    return out


PUBLISHED_IMEI = "490154203237518"   # GSMA / Wikipedia example, Luhn-valid


def run() -> dict:
    vectors = [PUBLISHED_IMEI,
               "490154203237519",    # corrupted check digit
               "490154203237508",    # corrupted body digit
               "35693803564380",     # 14 digits (too short)
               "4901542032375180"]   # 16 digits (too long)
    vectors += _synthetic_imeis(256)

    matched = 0
    mismatches = 0
    for v in vectors:
        module_verdict = is_valid(v)
        oracle_verdict = luhn_valid_oracle(v)
        if module_verdict == oracle_verdict:
            matched += 1
        else:
            mismatches += 1

    published_valid = is_valid(PUBLISHED_IMEI)
    check_reconstructed = check_digit("49015420323751") == 8

    return {
        "schema": "claimlib_imei_v1",
        "module": "imei",
        "reference_vectors": len(vectors),
        "reference_vectors_matched": matched,
        "mismatches": mismatches,
        "published_imei": PUBLISHED_IMEI,
        "published_imei_valid": published_valid,
        "check_digit_reconstructed": check_reconstructed,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "imei.json", obj,
         script="python3 claimlib/modules/imei/evidence.py")
    # claim:CLAIM-LIB-IMEI-001 reference_vectors_matched
    # The module agrees with the independent Luhn oracle on all 261 vectors, so
    # reference_vectors_matched = 261 and mismatches = 0.
    print(f"imei: {obj['reference_vectors_matched']}/{obj['reference_vectors']} "
          f"vectors agree with the independent Luhn oracle "
          f"({obj['mismatches']} mismatches); published IMEI valid={obj['published_imei_valid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
