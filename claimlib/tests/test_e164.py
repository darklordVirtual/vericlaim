# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``e164`` library."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "e164"))

from e164 import is_valid_format, country_code, parse, E164Error  # noqa: E402


def test_valid_numbers():
    assert is_valid_format("+4791234567") is True
    assert is_valid_format("+14155552671") is True
    assert is_valid_format("+358401234567") is True


def test_invalid_numbers():
    assert is_valid_format("004791234567") is False   # no '+'
    assert is_valid_format("+0123456789") is False    # leading zero
    assert is_valid_format("+47") is False            # too short
    assert is_valid_format("+1234567890123456") is False  # 16 digits


def test_longest_prefix_country_code():
    assert country_code("+4791234567") == "47"
    assert country_code("+358401234567") == "358"   # 3-digit beats 2/1-digit
    assert country_code("+14155552671") == "1"


def test_parse_splits_national_number():
    assert parse("+4791234567") == {"country_code": "47", "national_number": "91234567"}
    assert parse("+358401234567") == {"country_code": "358", "national_number": "401234567"}


def test_parse_rejects_invalid_and_unknown():
    with pytest.raises(E164Error):
        parse("004791234567")           # invalid format
    with pytest.raises(E164Error):
        parse("+9991234567")            # unknown calling code (999 not assigned here)
