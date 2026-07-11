# SPDX-License-Identifier: Apache-2.0
"""Weighted MOD-11 check digits (Norwegian organisasjonsnummer / ISO 7064 style).

A pre-verified claimlib code artifact. A MOD-11 check digit is the standard
integrity digit behind Norwegian organisation numbers, bank account numbers and
KID references, ISBN-10, and many national identifiers: each payload digit is
multiplied by a position weight, the weighted sum is reduced modulo 11, and the
check digit is ``11 - (sum % 11)`` (a result of 11 means the digit is 0). Its
strength -- that every single-digit alteration changes the weighted sum modulo
the prime 11 and is therefore caught -- is registered as a claim and proven by a
committed evidence artifact that verifies the property exhaustively.

Public API
----------
    check_digit(payload: str, weights: Sequence[int]) -> int
    is_valid(number: str, weights: Sequence[int]) -> bool   # number = payload+check
    is_valid_orgnr(number: str) -> bool                      # 9-digit NO org number

    >>> check_digit("12345678", NORWEGIAN_ORGNR_WEIGHTS)
    5
    >>> is_valid_orgnr("123456785")
    True
"""
from __future__ import annotations

from collections.abc import Sequence

# Norwegian organisasjonsnummer: 8 payload digits, weights applied left-to-right,
# 9th digit is the MOD-11 check (Brreg / "Organisasjonsnummer").
NORWEGIAN_ORGNR_WEIGHTS = (3, 2, 7, 6, 5, 4, 3, 2)


class Mod11Error(ValueError):
    """Invalid input, or a payload whose MOD-11 check digit would be 10."""


def _digits(payload: str, weights: Sequence[int]) -> list[int]:
    if not isinstance(payload, str) or payload == "":
        raise Mod11Error("payload must be a non-empty digit string")
    for ch in payload:
        if ch not in "0123456789":
            raise Mod11Error(f"non-digit in payload: {payload!r}")
    if len(payload) != len(weights):
        raise Mod11Error(
            f"payload length {len(payload)} != weight count {len(weights)}")
    return [ord(c) - 48 for c in payload]


def check_digit(payload: str, weights: Sequence[int]) -> int:
    """Return the MOD-11 check digit (0-9) for *payload* under *weights*.

    Raises :class:`Mod11Error` when the result would be 10, which has no single
    decimal digit (Norwegian numbering rejects such payloads; ISBN-10 would use
    'X', which this numeric-only module deliberately does not emit).
    """
    ds = _digits(payload, weights)
    total = sum(d * w for d, w in zip(ds, weights))
    check = 11 - (total % 11)
    if check == 11:
        return 0
    if check == 10:
        raise Mod11Error("no single-digit MOD-11 check exists for this payload")
    return check


def is_valid(number: str, weights: Sequence[int]) -> bool:
    """Return True iff *number*'s last digit is its MOD-11 check under *weights*.

    *number* is the full identifier: ``len(weights)`` payload digits followed by
    one check digit. A payload whose check would be 10 can never be valid.
    """
    if not isinstance(number, str) or len(number) != len(weights) + 1:
        return False
    if any(c not in "0123456789" for c in number):
        return False
    try:
        return check_digit(number[:-1], weights) == int(number[-1])
    except Mod11Error:
        return False


def is_valid_orgnr(number: str) -> bool:
    """Return True iff *number* is a valid 9-digit Norwegian organisation number."""
    return is_valid(number, NORWEGIAN_ORGNR_WEIGHTS)
