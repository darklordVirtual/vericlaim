# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``luhn`` library.

Reference values are independently known: the Wikipedia Luhn worked example
(79927398713 valid, check digit 3) and payment-card test numbers published by
card networks / processors (all documented as Luhn-valid).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "luhn"))

from luhn import is_valid, check_digit, checksum, LuhnError  # noqa: E402


def test_wikipedia_valid_number():
    assert is_valid("79927398713") is True


def test_wikipedia_off_by_one_invalid():
    assert is_valid("79927398714") is False


def test_published_test_cards_are_valid():
    for card in ("4111111111111111", "5555555555554444",
                 "378282246310005", "6011111111111117"):
        assert is_valid(card) is True


def test_corrupted_cards_are_invalid():
    assert is_valid("4111111111111112") is False
    assert is_valid("5555555555554445") is False


def test_check_digit_matches_wikipedia():
    assert check_digit("7992739871") == 3


def test_check_digit_completes_valid_cards():
    # Stripping a valid number's last digit and recomputing must reproduce it.
    for card in ("79927398713", "4111111111111111", "378282246310005"):
        assert check_digit(card[:-1]) == int(card[-1])
        assert is_valid(card[:-1] + str(check_digit(card[:-1])))


def test_check_digit_range_and_checksum_zero():
    # check_digit is always 0-9 and always yields a valid number.
    for partial in ("0", "7", "123456", "999999999999999"):
        d = check_digit(partial)
        assert 0 <= d <= 9
        assert checksum(partial + str(d)) == 0


def test_single_zero_is_valid():
    assert is_valid("0") is True
    assert checksum("0") == 0


def test_rejects_empty_and_non_digit_input():
    with pytest.raises(LuhnError):
        is_valid("")
    with pytest.raises(LuhnError):
        is_valid("12 34")
    with pytest.raises(LuhnError):
        check_digit("12a4")
    with pytest.raises(LuhnError):
        is_valid(1234)  # not a string


def test_rejects_unicode_digits():
    # str.isdigit() accepts e.g. superscript/fullwidth digits; we must not.
    with pytest.raises(LuhnError):
        is_valid("１２３")  # fullwidth 123
