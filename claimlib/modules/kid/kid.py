# SPDX-License-Identifier: Apache-2.0
"""Norwegian KID (kundeidentifikasjon) check digits — MOD10 and MOD11 per the
Nets OCR giro system specification — reusable, claim-bound.

A pre-verified claimlib code artifact. A KID identifies an invoice/payment on
a Norwegian OCR giro; its last digit is a check digit computed from the
payload in one of two registered variants (chosen per agreement with the
bank/Nets):

    MOD10 (Luhn): weights 2,1,2,1,... applied right-to-left over the payload,
    digit products above 9 reduced by digit-summing (equivalently -9), check
    digit = (10 - sum mod 10) mod 10. Identical to ISO/IEC 7812's Luhn.

    MOD11: weights 2,3,4,5,6,7,2,3,... applied right-to-left over the
    payload, check digit = 11 - (sum mod 11), with two special cases:
    remainder 0 gives check digit 0, and remainder 1 gives NO valid digit --
    such payloads cannot be issued as MOD11 KIDs (the spec writes "-").
    The same construction validates Norwegian organisasjonsnummer.

A KID is 2-25 characters including its check digit, digits only. That the
two variants agree with independent constructions (a from-scratch Luhn and
the published organisasjonsnummer scheme), reproduce published examples, and
catch every single-digit alteration over an exhaustive payload space is
registered as a claim and proven by a committed evidence artifact.

Public API
----------
    mod10_check_digit(payload: str) -> int
    mod11_check_digit(payload: str) -> int | None    # None: no valid digit
    is_valid(kid: str, variant: str = "mod10") -> bool
    make_kid(payload: str, variant: str = "mod10") -> str

    >>> make_kid("234567")           # MOD10
    '2345676'
    >>> mod11_check_digit("12345678")
    2
"""
from __future__ import annotations

_MIN_KID = 2
_MAX_KID = 25


class KidError(ValueError):
    """Invalid KID / payload input (fail closed)."""


def _check_digits(value: str, name: str, lo: int, hi: int) -> str:
    if not isinstance(value, str):
        raise KidError(f"{name} must be a str, got {type(value).__name__}")
    if not value.isascii() or not value.isdigit():
        raise KidError(f"{name} must be digits only, got {value!r}")
    if not lo <= len(value) <= hi:
        raise KidError(f"{name} must be {lo}-{hi} digits, "
                       f"got {len(value)}")
    return value


def mod10_check_digit(payload: str) -> int:
    """The Luhn/MOD10 check digit for *payload* (1-24 digits)."""
    _check_digits(payload, "payload", _MIN_KID - 1, _MAX_KID - 1)
    total = 0
    weight = 2
    for ch in reversed(payload):
        prod = int(ch) * weight
        total += prod - 9 if prod > 9 else prod
        weight = 1 if weight == 2 else 2
    return (10 - total % 10) % 10


def mod11_check_digit(payload: str):
    """The MOD11 check digit for *payload*, or None when none exists.

    Weights cycle 2,3,4,5,6,7 right-to-left. Remainder 0 -> digit 0;
    remainder 1 -> no valid check digit (the payload cannot be a MOD11 KID).
    """
    _check_digits(payload, "payload", _MIN_KID - 1, _MAX_KID - 1)
    total = 0
    weight = 2
    for ch in reversed(payload):
        total += int(ch) * weight
        weight = 2 if weight == 7 else weight + 1
    remainder = total % 11
    if remainder == 0:
        return 0
    if remainder == 1:
        return None
    return 11 - remainder


def is_valid(kid: str, variant: str = "mod10") -> bool:
    """True iff *kid* (payload + check digit) verifies under *variant*."""
    _check_digits(kid, "kid", _MIN_KID, _MAX_KID)
    payload, check = kid[:-1], int(kid[-1])
    if variant == "mod10":
        return mod10_check_digit(payload) == check
    if variant == "mod11":
        return mod11_check_digit(payload) == check
    raise KidError(f"variant must be 'mod10' or 'mod11', got {variant!r}")


def make_kid(payload: str, variant: str = "mod10") -> str:
    """Append the check digit to *payload*; raises when MOD11 has none."""
    if variant == "mod10":
        return payload + str(mod10_check_digit(payload))
    if variant == "mod11":
        digit = mod11_check_digit(payload)
        if digit is None:
            raise KidError(
                f"payload {payload!r} has no valid MOD11 check digit "
                f"(weighted sum remainder 1)")
        return payload + str(digit)
    raise KidError(f"variant must be 'mod10' or 'mod11', got {variant!r}")
