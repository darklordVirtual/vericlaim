# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``iban`` library.

Reference values are the canonical published IBAN examples from the ISO 13616 /
SWIFT registry and Wikipedia (GB82WEST..., DE89370400..., NO9386011117947).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "iban"))

from iban import is_valid, check_digits, electronic_format, IBANError  # noqa: E402


def test_published_valid_ibans():
    for iban in ("GB82 WEST 1234 5698 7654 32",
                 "DE89 3704 0044 0532 0130 00",
                 "NO93 8601 1117 947",
                 "ES91 2100 0418 4502 0005 1332"):
        assert is_valid(iban) is True


def test_single_digit_mutation_is_invalid():
    assert is_valid("NO93 8601 1117 948") is False
    assert is_valid("DE89 3704 0044 0532 0130 01") is False


def test_check_digits_reconstruct_embedded():
    assert check_digits("GB", "WEST12345698765432") == "82"
    assert check_digits("NO", "86011117947") == "93"
    assert check_digits("DE", "370400440532013000") == "89"


def test_electronic_format_normalizes():
    assert electronic_format("no93 8601 1117 947") == "NO9386011117947"


def test_rejects_malformed_shapes():
    assert is_valid("") is False
    assert is_valid("GB!2WEST12345698765432") is False   # illegal char
    assert is_valid("G82WEST12345698765432") is False    # 1-letter country
    assert is_valid("GB82") is False                      # too short


def test_check_digits_reject_bad_country():
    with pytest.raises(IBANError):
        check_digits("G1", "WEST12345698765432")


def test_check_digit_round_trip():
    # Rebuilding an IBAN from its BBAN + computed check digits must be valid.
    country, bban = "GB", "WEST12345698765432"
    cd = check_digits(country, bban)
    assert is_valid(country + cd + bban) is True
