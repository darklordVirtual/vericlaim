# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the kid module (Norwegian KID MOD10/MOD11)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "kid"
_spec = importlib.util.spec_from_file_location(
    "claimlib_kid", _MOD_DIR / "kid.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_kid"] = _m
_spec.loader.exec_module(_m)

KidError = _m.KidError
mod10_check_digit = _m.mod10_check_digit
mod11_check_digit = _m.mod11_check_digit
is_valid = _m.is_valid
make_kid = _m.make_kid


def test_mod10_matches_luhn_examples():
    # Luhn-valid published numbers validate as MOD10 KIDs.
    for num in ("79927398713", "4111111111111111", "378282246310005"):
        assert is_valid(num, "mod10")
    assert mod10_check_digit("7992739871") == 3


def test_mod11_matches_orgnr_scheme():
    # Publicly listed organisasjonsnummer use the same MOD11 construction.
    for org in ("923609016", "974760673", "984851006"):
        assert is_valid(org, "mod11")


def test_mod11_remainder_special_cases():
    # Find a payload with remainder 0 (digit 0) and one with remainder 1
    # (no digit) deterministically.
    saw_zero = saw_none = False
    for n in range(2000):
        digit = mod11_check_digit(f"{n:04d}")
        if digit == 0:
            saw_zero = True
        if digit is None:
            saw_none = True
        if saw_zero and saw_none:
            break
    assert saw_zero and saw_none


def test_make_kid_roundtrip_both_variants():
    for payload in ("234567", "0001", "9" * 24):
        kid10 = make_kid(payload, "mod10")
        assert kid10.startswith(payload) and is_valid(kid10, "mod10")
    kid11 = make_kid("12345678", "mod11")
    assert is_valid(kid11, "mod11")


def test_make_kid_mod11_rejects_remainder_one_payload():
    for n in range(2000):
        payload = f"{n:04d}"
        if mod11_check_digit(payload) is None:
            with pytest.raises(KidError):
                make_kid(payload, "mod11")
            return
    pytest.fail("no remainder-1 payload found in range")


def test_single_digit_tamper_detected():
    kid = make_kid("31415926", "mod10")
    for pos in range(len(kid)):
        for repl in "0123456789":
            if repl == kid[pos]:
                continue
            assert not is_valid(kid[:pos] + repl + kid[pos + 1:], "mod10")


@pytest.mark.parametrize("call", [
    lambda: is_valid("1", "mod10"),          # too short
    lambda: is_valid("1" * 26, "mod10"),     # too long
    lambda: is_valid("12x4", "mod10"),       # non-digit
    lambda: is_valid("1234", "mod12"),       # unknown variant
    lambda: is_valid(1234, "mod10"),         # not a str
    lambda: mod10_check_digit(""),           # empty payload
    lambda: make_kid("½234", "mod10"),       # non-ascii digit
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(KidError):
        call()
