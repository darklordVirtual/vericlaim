# SPDX-License-Identifier: Apache-2.0
"""IMEI validation (15-digit mobile equipment identity with Luhn check digit).

A pre-verified claimlib code artifact. An IMEI is the 15-digit serial number
that identifies a GSM/UMTS/LTE handset: an 8-digit Type Allocation Code, a
6-digit serial, and a trailing Luhn (mod-10) check digit computed over the first
14 digits. This module validates the format and check digit; that it accepts the
published GSMA example IMEI 490154203237518 and agrees with an independent Luhn
computation is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    is_valid(imei: str) -> bool           # 15 digits AND Luhn-valid
    check_digit(imei14: str) -> int       # Luhn check digit for a 14-digit body
    parse(imei: str) -> dict              # {tac, serial, check_digit}

    >>> is_valid("490154203237518")
    True
    >>> check_digit("49015420323751")
    8
"""
from __future__ import annotations


class IMEIError(ValueError):
    """The input is not a string of the expected decimal-digit length."""


def _digits(number: str, length: int) -> list[int]:
    if not isinstance(number, str) or len(number) != length:
        raise IMEIError(f"expected a {length}-digit string")
    for ch in number:
        if ch not in "0123456789":
            raise IMEIError(f"non-digit character in input: {number!r}")
    return [ord(c) - 48 for c in number]


def _luhn_residue(ds: list[int]) -> int:
    """Luhn mod-10 residue: double every second digit from the right."""
    total = 0
    for i, d in enumerate(reversed(ds)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10


def check_digit(imei14: str) -> int:
    """Return the Luhn check digit (0-9) for a 14-digit IMEI body."""
    ds = _digits(imei14, 14)
    # Appending the check digit shifts positions: the body's last digit becomes
    # a doubled position, so double every second digit counting from the body's
    # right (i even here corresponds to the doubled slots in the final number).
    total = 0
    for i, d in enumerate(reversed(ds)):
        if i % 2 == 0:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return (10 - total % 10) % 10


def is_valid(imei: str) -> bool:
    """Return True iff *imei* is 15 digits and its Luhn checksum is 0."""
    try:
        ds = _digits(imei, 15)
    except IMEIError:
        return False
    return _luhn_residue(ds) == 0


def parse(imei: str) -> dict:
    """Return the structural fields of a valid IMEI (raises if invalid)."""
    if not is_valid(imei):
        raise IMEIError(f"not a valid IMEI: {imei!r}")
    return {"tac": imei[:8], "serial": imei[8:14], "check_digit": int(imei[14])}
