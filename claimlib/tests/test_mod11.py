# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``mod11`` library.

The Norwegian organisasjonsnummer example (payload 12345678 -> check 5, so
123456785 is valid) is an independently computable reference.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "mod11"))

from mod11 import (  # noqa: E402
    check_digit, is_valid, is_valid_orgnr, Mod11Error, NORWEGIAN_ORGNR_WEIGHTS)

W = (2, 3, 4, 5)


def test_orgnr_reference():
    assert check_digit("12345678", NORWEGIAN_ORGNR_WEIGHTS) == 5
    assert is_valid_orgnr("123456785") is True
    assert is_valid_orgnr("123456784") is False


def test_round_trip_over_range():
    for value in range(0, 2000):
        payload = f"{value:04d}"
        try:
            c = check_digit(payload, W)
        except Mod11Error:
            continue
        assert is_valid(payload + str(c), W) is True


def test_every_single_digit_change_detected():
    payload = "1357"
    c = check_digit(payload, W)
    number = payload + str(c)
    for pos in range(len(number)):
        for d in "0123456789":
            if d == number[pos]:
                continue
            mutated = number[:pos] + d + number[pos + 1:]
            assert is_valid(mutated, W) is False


def test_check_digit_zero_case():
    # A payload whose weighted sum is a multiple of 11 has check digit 0.
    # 0000 -> sum 0 -> 11 - 0 -> 0.
    assert check_digit("0000", W) == 0
    assert is_valid("00000", W) is True


def test_rejects_bad_input():
    with pytest.raises(Mod11Error):
        check_digit("", W)
    with pytest.raises(Mod11Error):
        check_digit("12a4", W)
    with pytest.raises(Mod11Error):
        check_digit("123", W)  # length mismatch
    assert is_valid("1234", W) is False   # wrong length
    assert is_valid("abcde", W) is False  # non-digit


def test_undefined_check_digit_raises():
    # Find a payload whose check would be 10 and confirm it raises.
    found = False
    for value in range(10000):
        payload = f"{value:04d}"
        try:
            check_digit(payload, W)
        except Mod11Error:
            found = True
            assert is_valid(payload + "0", W) is False
            break
    assert found
