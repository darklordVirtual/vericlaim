# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``imei`` library.

Reference: the GSMA / Wikipedia example IMEI 490154203237518 (Luhn-valid).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "imei"))

from imei import is_valid, check_digit, parse, IMEIError  # noqa: E402


def test_published_imei_valid():
    assert is_valid("490154203237518") is True


def test_corrupted_imei_invalid():
    assert is_valid("490154203237519") is False
    assert is_valid("490154203237508") is False


def test_check_digit_reconstruction():
    assert check_digit("49015420323751") == 8
    # Completing the body with its check digit must validate.
    body = "49015420323751"
    assert is_valid(body + str(check_digit(body))) is True


def test_parse_fields():
    p = parse("490154203237518")
    assert p == {"tac": "49015420", "serial": "323751", "check_digit": 8}


def test_length_and_charset_rejected():
    assert is_valid("35693803564380") is False    # 14 digits
    assert is_valid("4901542032375180") is False  # 16 digits
    assert is_valid("49015420323751a") is False    # non-digit
    with pytest.raises(IMEIError):
        check_digit("123")                          # wrong length
    with pytest.raises(IMEIError):
        parse("490154203237519")                    # invalid IMEI cannot be parsed
