# SPDX-License-Identifier: Apache-2.0
"""Luhn (mod-10) checksum — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it classifies a fixed table of published
known-valid and known-invalid numbers correctly — is registered as a claim
and proven by a committed evidence artifact; vendoring this module carries
that claim (and its caveat) with it.

The Luhn algorithm (a.k.a. the "mod 10" algorithm, ISO/IEC 7812-1) is the
check-digit formula used to validate payment card numbers, IMEIs, and many
national ID numbers. It catches all single-digit errors and most adjacent
transpositions. It is a checksum, NOT a cryptographic integrity check.

Public API
----------
    is_valid(number: str) -> bool     # True iff the mod-10 checksum is 0
    check_digit(partial: str) -> int  # 0-9 digit that makes partial+d valid
    checksum(number: str) -> int      # the raw mod-10 residue (0-9)

    >>> is_valid("79927398713")
    True
    >>> is_valid("79927398714")
    False
    >>> check_digit("7992739871")
    3
"""
from __future__ import annotations


class LuhnError(ValueError):
    """The input is not a non-empty string of decimal digits."""


def _digits(number: str) -> list[int]:
    """Validate and convert *number* to a list of int digits (fail closed)."""
    if not isinstance(number, str) or number == "":
        raise LuhnError("expected a non-empty string of digits")
    if not number.isdigit():
        # str.isdigit() also accepts some unicode digits; reject anything
        # that is not a plain ASCII 0-9 to keep behaviour unambiguous.
        raise LuhnError(f"non-digit character in input: {number!r}")
    out = []
    for ch in number:
        if ch not in "0123456789":
            raise LuhnError(f"non-ASCII digit in input: {number!r}")
        out.append(ord(ch) - 48)
    return out


def checksum(number: str) -> int:
    """Return the Luhn mod-10 residue (0-9) of a full digit string.

    Processing right-to-left, every second digit (the check digit itself is
    position 1 and is *not* doubled) is doubled; digits over 9 have 9
    subtracted (equivalently, their decimal digits summed). The residue is
    the running total modulo 10. A number is valid exactly when this is 0.
    """
    ds = _digits(number)
    total = 0
    for i, d in enumerate(reversed(ds)):
        if i % 2 == 1:          # every second digit from the right, doubled
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10


def is_valid(number: str) -> bool:
    """Return True iff *number*'s trailing check digit satisfies Luhn."""
    return checksum(number) == 0


def check_digit(partial: str) -> int:
    """Return the check digit (0-9) that, appended to *partial*, is valid.

    *partial* is the payload WITHOUT its trailing check digit. When the
    returned digit is appended it occupies position 1 (undoubled), so every
    digit of *partial* shifts one position and the rightmost payload digit
    becomes a doubled position.
    """
    ds = _digits(partial)
    total = 0
    for i, d in enumerate(reversed(ds)):
        if i % 2 == 0:          # payload shifts: its last digit is doubled
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - total % 10) % 10
