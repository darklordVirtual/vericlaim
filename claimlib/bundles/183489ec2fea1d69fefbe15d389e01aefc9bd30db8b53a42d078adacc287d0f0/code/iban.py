# SPDX-License-Identifier: Apache-2.0
"""IBAN validation and check-digit generation (ISO 13616 / ISO 7064 MOD-97-10).

A pre-verified claimlib code artifact: a reusable, stdlib-only building block
whose key property -- that it classifies a fixed table of officially published
known-valid and deliberately corrupted IBANs correctly, and reconstructs the
embedded check digits of every valid one -- is registered as a claim and proven
by a committed evidence artifact. Vendoring carries that claim (and caveat).

An International Bank Account Number is validated by the MOD-97-10 rule (ISO
7064): move the first four characters (country code + 2 check digits) to the
end, replace each letter with two digits (A=10 .. Z=35), interpret the result
as a base-10 integer, and require that integer mod 97 == 1.

Public API
----------
    is_valid(iban: str) -> bool           # True iff format + MOD-97 both hold
    check_digits(country: str, bban: str) -> str  # the 2 ISO 7064 check digits
    electronic_format(iban: str) -> str    # upper-cased, spaces stripped

    >>> is_valid("GB82 WEST 1234 5698 7654 32")
    True
    >>> check_digits("GB", "WEST12345698765432")
    '82'
"""
from __future__ import annotations

import re

_IBAN_RE = re.compile(r"^[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}$")


class IBANError(ValueError):
    """The input is not a syntactically well-formed IBAN string."""


def electronic_format(iban: str) -> str:
    """Return *iban* upper-cased with all spaces removed (electronic format)."""
    if not isinstance(iban, str):
        raise IBANError("expected a string")
    return iban.replace(" ", "").upper()


def _to_number(s: str) -> int:
    """Translate an alphanumeric string to the MOD-97 integer (A=10 .. Z=35)."""
    digits = []
    for ch in s:
        if "0" <= ch <= "9":
            digits.append(ch)
        elif "A" <= ch <= "Z":
            digits.append(str(ord(ch) - 55))  # 'A' (65) -> 10
        else:
            raise IBANError(f"illegal character in IBAN: {ch!r}")
    return int("".join(digits))


def _well_formed(iban: str) -> bool:
    return 15 <= len(iban) <= 34 and _IBAN_RE.match(iban) is not None


def is_valid(iban: str) -> bool:
    """Return True iff *iban* is well-formed AND satisfies the MOD-97 check."""
    e = electronic_format(iban)
    if not _well_formed(e):
        return False
    rearranged = e[4:] + e[:4]
    try:
        return _to_number(rearranged) % 97 == 1
    except IBANError:
        return False


def check_digits(country: str, bban: str) -> str:
    """Return the two ISO 7064 check digits for *country* + *bban*.

    98 - (MOD-97 of the rearranged string with check digits set to "00").
    """
    country = country.upper()
    bban = bban.upper()
    if not re.match(r"^[A-Z]{2}$", country):
        raise IBANError(f"country code must be two letters: {country!r}")
    if not re.match(r"^[A-Z0-9]+$", bban):
        raise IBANError(f"BBAN must be alphanumeric: {bban!r}")
    remainder = _to_number(bban + country + "00") % 97
    return f"{98 - remainder:02d}"
