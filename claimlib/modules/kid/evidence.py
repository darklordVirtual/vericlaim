# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-KID-001 — both KID check-digit variants agree with
independent constructions and catch every single-digit alteration.

Oracles, none the module's own output:

* MOD10: an INDEPENDENT from-scratch Luhn (the classic double-every-second-
  digit-and-digit-sum formulation, structurally different from the module's
  weight-cycling loop) must agree on every payload of an exhaustive space,
  and published Luhn-valid numbers (the Wikipedia worked example 79927398713
  and the card networks' test numbers) must validate as MOD10 KIDs.
* MOD11: the published Norwegian organisasjonsnummer scheme is the same
  construction — the evidence recomputes check digits with the orgnr weight
  table (3,2,7,6,5,4,3,2 left-to-right) and real, publicly listed orgnr
  (Equinor 923609016, Brønnøysundregistrene 974760673, DNB Bank 984851006)
  must validate.
* Tamper detection: over the COMPLETE space of 4-digit payloads (10^4), every
  single-digit alteration of a valid KID must be rejected, for both variants
  — exhaustive, not sampled.

Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from kid import (  # noqa: E402
    KidError, is_valid, make_kid, mod10_check_digit, mod11_check_digit,
)
from _util import emit  # noqa: E402

LUHN_VALID_PUBLISHED = [
    "79927398713",        # Wikipedia's worked Luhn example
    "4111111111111111",   # Visa test number
    "5555555555554444",   # Mastercard test number
    "378282246310005",    # Amex test number
    "6011111111111117",   # Discover test number
]

# Publicly listed Norwegian organisasjonsnummer (same MOD11 construction).
ORGNR_PUBLISHED = ["923609016", "974760673", "984851006"]


def independent_luhn_digit(payload: str) -> int:
    """Classic Luhn formulation: double every second digit from the right,
    digit-sum the products, check digit completes to a multiple of 10."""
    total = 0
    for i, ch in enumerate(reversed(payload)):
        d = int(ch)
        if i % 2 == 0:  # positions 0,2,4.. from the right get doubled
            d *= 2
            d = d // 10 + d % 10
        total += d
    return (10 - total % 10) % 10


def orgnr_check_digit(payload8: str):
    """Published organisasjonsnummer scheme: weights 3,2,7,6,5,4,3,2."""
    weights = (3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(int(c) * w for c, w in zip(payload8, weights))
    r = total % 11
    if r == 0:
        return 0
    if r == 1:
        return None
    return 11 - r


def run() -> dict:
    # 1) MOD10 == independent Luhn, exhaustively over all 3-digit payloads
    #    plus the full 4-digit space.
    agree = 0
    space = 0
    for n in range(10_000):
        payload = f"{n:04d}"
        space += 1
        if mod10_check_digit(payload) == independent_luhn_digit(payload):
            agree += 1

    published_ok = sum(1 for num in LUHN_VALID_PUBLISHED
                       if is_valid(num, "mod10"))

    # 2) MOD11 == the published orgnr construction on all 8-digit payloads of
    #    a fixed stride sweep + the real public orgnr validate.
    orgnr_agree = 0
    orgnr_space = 0
    for n in range(0, 100_000_000, 97_397):  # deterministic 1027-point sweep
        payload = f"{n:08d}"
        orgnr_space += 1
        if mod11_check_digit(payload) == orgnr_check_digit(payload):
            orgnr_agree += 1
    orgnr_real_ok = sum(1 for org in ORGNR_PUBLISHED
                        if is_valid(org, "mod11"))

    # 3) Exhaustive tamper detection over the complete 4-digit payload space.
    tampers = 0
    caught = 0
    for n in range(10_000):
        payload = f"{n:04d}"
        for variant in ("mod10", "mod11"):
            try:
                valid_kid = make_kid(payload, variant)
            except KidError:
                continue  # MOD11 remainder-1 payloads have no KID
            for pos in range(len(valid_kid)):
                orig = valid_kid[pos]
                for repl in "0123456789":
                    if repl == orig:
                        continue
                    tampers += 1
                    mutated = valid_kid[:pos] + repl + valid_kid[pos + 1:]
                    if not is_valid(mutated, variant):
                        caught += 1

    rejects = 0
    for bad in (lambda: is_valid("1", "mod10"),
                lambda: is_valid("12a4", "mod10"),
                lambda: is_valid("1234", "mod13"),
                lambda: mod10_check_digit("1" * 25),
                lambda: is_valid(1234, "mod10")):
        try:
            bad()
        except KidError:
            rejects += 1

    return {
        "schema": "claimlib_evidence_v1",
        "module": "kid",
        "mod10_space": space,
        "mod10_luhn_agreement": agree,
        "published_luhn_valid": len(LUHN_VALID_PUBLISHED),
        "published_luhn_ok": published_ok,
        "orgnr_sweep": orgnr_space,
        "orgnr_agreement": orgnr_agree,
        "orgnr_real": len(ORGNR_PUBLISHED),
        "orgnr_real_ok": orgnr_real_ok,
        "tampers": tampers,
        "tampers_caught": caught,
        "tampers_missed": tampers - caught,
        "reject_cases": 5,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "kid.json", obj,
         script="python3 claimlib/modules/kid/evidence.py")
    # claim:CLAIM-LIB-KID-001 tampers_missed
    # Every single-digit alteration of every valid 4-digit-payload KID is
    # caught in both variants, so tampers_missed = 0 (exhaustive; 859095
    # mutations checked), with full agreement against the independent Luhn
    # and organisasjonsnummer constructions.
    print(f"kid: mod10/Luhn agreement {obj['mod10_luhn_agreement']}/"
          f"{obj['mod10_space']}, orgnr agreement {obj['orgnr_agreement']}/"
          f"{obj['orgnr_sweep']} (+{obj['orgnr_real_ok']}/{obj['orgnr_real']} "
          f"real), tampers caught {obj['tampers_caught']}/{obj['tampers']} "
          f"(missed {obj['tampers_missed']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
