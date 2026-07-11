# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``hkdf`` library (RFC 5869 test vectors)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "hkdf"))

from hkdf import extract, expand, hkdf, HKDFError  # noqa: E402


def test_rfc5869_test_case_1():
    ikm = bytes.fromhex("0b" * 22)
    salt = bytes.fromhex("000102030405060708090a0b0c")
    info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
    prk = extract(salt, ikm)
    assert prk.hex() == "077709362c2e32df0ddc3f0dc47bba6390b6c73bb50f9c3122ec844ad7c2b3e5"
    assert hkdf(salt, ikm, info, 42).hex() == (
        "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865")


def test_rfc5869_test_case_3_zero_salt_info():
    ikm = bytes.fromhex("0b" * 22)
    assert hkdf(b"", ikm, b"", 42).hex() == (
        "8da4e775a563c18f715f802a063c5a31b8a11f5c5ee1879ec3454e5f3c738d2d9d201395faa4b61a96c8")


def test_expand_length_and_bounds():
    prk = extract(b"salt", b"ikm")
    assert len(expand(prk, b"info", 100)) == 100
    with pytest.raises(HKDFError):
        expand(prk, b"info", 255 * 32 + 1)   # exceeds max output length


def test_rejects_bad_input():
    with pytest.raises(HKDFError):
        extract(b"salt", "not bytes")
    with pytest.raises(HKDFError):
        hkdf(b"s", b"i", b"info", 0)
    with pytest.raises(HKDFError):
        extract(b"salt", b"ikm", "md5-not-real")
