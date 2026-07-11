# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MOD11-001 -- the weighted MOD-11 check digit round-trips
and catches every single-digit alteration, verified EXHAUSTIVELY.

Over the complete space of 4-digit payloads (0000..9999) under a fixed weight
vector (2, 3, 4, 5):

  * round-trip: for every payload whose check digit is defined (i.e. not the
    ~1/11 whose check would be 10), appending the computed check digit yields a
    number that ``is_valid`` accepts;
  * tamper: for every such valid 5-digit number, changing ANY single digit to
    ANY of the 9 other values must make ``is_valid`` return False. Because 11 is
    prime and no weight is a multiple of 11, this holds for the entire space --
    the evidence checks all of it, so ``tamper_missed`` is 0 by enumeration, not
    by sampling.

Independent cross-check: the Norwegian organisasjonsnummer example 123456785
(payload 12345678, weights 3,2,7,6,5,4,3,2 -> check 5) is validated separately.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (mod11.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from mod11 import (  # noqa: E402
    check_digit, is_valid, is_valid_orgnr, Mod11Error, NORWEGIAN_ORGNR_WEIGHTS)
from _util import emit  # noqa: E402

WEIGHTS = (2, 3, 4, 5)


def run() -> dict:
    n_payloads = 0
    defined = 0
    roundtrip_valid = 0
    tamper_mutations = 0
    tamper_detected = 0
    for value in range(10000):
        n_payloads += 1
        payload = f"{value:04d}"
        try:
            c = check_digit(payload, WEIGHTS)
        except Mod11Error:
            continue  # check digit would be 10 -> undefined, skip
        defined += 1
        number = payload + str(c)
        if is_valid(number, WEIGHTS):
            roundtrip_valid += 1
        # Single-digit tamper over all 5 positions x 9 alternative digits.
        for pos in range(len(number)):
            original = number[pos]
            for d in "0123456789":
                if d == original:
                    continue
                tamper_mutations += 1
                mutated = number[:pos] + d + number[pos + 1:]
                if not is_valid(mutated, WEIGHTS):
                    tamper_detected += 1

    orgnr_ok = (
        check_digit("12345678", NORWEGIAN_ORGNR_WEIGHTS) == 5
        and is_valid_orgnr("123456785") is True
        and is_valid_orgnr("123456784") is False
    )

    return {
        "schema": "claimlib_mod11_v1",
        "module": "mod11",
        "weights": list(WEIGHTS),
        "n_payloads": n_payloads,
        "checkdigit_defined": defined,
        "roundtrip_valid": roundtrip_valid,
        "roundtrip_failures": defined - roundtrip_valid,
        "tamper_mutations": tamper_mutations,
        "tamper_detected": tamper_detected,
        "tamper_missed": tamper_mutations - tamper_detected,
        "orgnr_reference_ok": orgnr_ok,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "mod11.json", obj,
         script="python3 claimlib/modules/mod11/evidence.py")
    # claim:CLAIM-LIB-MOD11-001 tamper_missed
    # Over the entire 4-digit payload space, every single-digit alteration is
    # caught, so tamper_missed = 0 (roundtrip_failures = 0 too).
    print(f"mod11: roundtrip {obj['roundtrip_valid']}/{obj['checkdigit_defined']}, "
          f"tamper_detected {obj['tamper_detected']}/{obj['tamper_mutations']} "
          f"(missed={obj['tamper_missed']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
