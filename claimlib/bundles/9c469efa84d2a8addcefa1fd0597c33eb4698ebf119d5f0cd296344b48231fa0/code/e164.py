# SPDX-License-Identifier: Apache-2.0
"""E.164 phone-number format validation and country-calling-code extraction.

A pre-verified claimlib code artifact. ITU-T E.164 defines the international
public telephone numbering plan: a leading ``+``, a country calling code, then
the national number, at most 15 digits total, with no leading zero on the
country code. This module validates that format and extracts the calling code
by longest-prefix match against a curated table of published ITU assignments.
That it classifies a fixed battery of well-formed and malformed numbers, and
resolves their calling codes, correctly is registered as a claim and proven by a
committed evidence artifact.

Public API
----------
    is_valid_format(number: str) -> bool     # E.164 syntactic validity
    country_code(number: str) -> str | None  # longest known calling code, or None
    parse(number: str) -> dict               # {country_code, national_number}

    >>> is_valid_format("+4791234567")
    True
    >>> country_code("+4791234567")
    '47'
"""
from __future__ import annotations

import re

# Curated subset of published ITU-T E.164 country calling codes (not exhaustive;
# longest-prefix match, so multi-digit codes are tried before single-digit ones).
CALLING_CODES = {
    "1": "North American Numbering Plan",
    "7": "Russia / Kazakhstan",
    "20": "Egypt",
    "27": "South Africa",
    "31": "Netherlands",
    "33": "France",
    "34": "Spain",
    "39": "Italy",
    "44": "United Kingdom",
    "45": "Denmark",
    "46": "Sweden",
    "47": "Norway",
    "49": "Germany",
    "55": "Brazil",
    "61": "Australia",
    "81": "Japan",
    "86": "China",
    "91": "India",
    "234": "Nigeria",
    "351": "Portugal",
    "352": "Luxembourg",
    "358": "Finland",
    "971": "United Arab Emirates",
}

_E164_RE = re.compile(r"^\+[1-9][0-9]{6,14}$")   # + then 7..15 digits, no leading 0


class E164Error(ValueError):
    """The number is not a syntactically valid E.164 string."""


def is_valid_format(number: str) -> bool:
    """Return True iff *number* matches the E.164 syntax (+, 7..15 digits)."""
    return isinstance(number, str) and _E164_RE.match(number) is not None


def country_code(number: str) -> str | None:
    """Return the longest known calling code prefixing *number*, or None."""
    if not is_valid_format(number):
        return None
    digits = number[1:]
    for length in (3, 2, 1):                 # longest prefix wins
        if digits[:length] in CALLING_CODES:
            return digits[:length]
    return None


def parse(number: str) -> dict:
    """Return {country_code, national_number} for a valid, known-code number."""
    if not is_valid_format(number):
        raise E164Error(f"not a valid E.164 number: {number!r}")
    cc = country_code(number)
    if cc is None:
        raise E164Error(f"unknown country calling code in {number!r}")
    return {"country_code": cc, "national_number": number[1 + len(cc):]}
