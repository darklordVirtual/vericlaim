# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable crc32 module (claimlib/modules/crc32)."""
from __future__ import annotations

import sys
import zlib
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "crc32"))

from crc32 import crc32  # noqa: E402


def test_published_reference_values():
    # Independently-known IEEE 802.3 CRC-32 check values.
    assert crc32(b"") == 0x00000000
    assert crc32(b"123456789") == 0xCBF43926
    assert crc32(b"The quick brown fox jumps over the lazy dog") == 0x414FA339


def test_result_is_unsigned_32bit():
    for data in (b"", b"a", b"\xff" * 5, bytes(range(256))):
        got = crc32(data)
        assert isinstance(got, int)
        assert 0 <= got <= 0xFFFFFFFF


def test_matches_zlib_oracle():
    # zlib.crc32 is an independent implementation in the standard library.
    cases = [b"", b"\x00", b"\xff", b"abc", b"hello world",
             bytes(range(256)), b"\xde\xad\xbe\xef" * 10]
    for data in cases:
        assert crc32(data) == (zlib.crc32(data) & 0xFFFFFFFF)


def test_matches_zlib_over_incremental_lengths():
    for n in range(0, 64):
        data = bytes((i * 37 + 11) & 0xFF for i in range(n))
        assert crc32(data) == (zlib.crc32(data) & 0xFFFFFFFF)


def test_accepts_bytes_like():
    assert crc32(bytearray(b"123456789")) == 0xCBF43926
    assert crc32(memoryview(b"123456789")) == 0xCBF43926


def test_rejects_non_bytes():
    with pytest.raises(TypeError):
        crc32("123456789")  # str, not bytes
    with pytest.raises(TypeError):
        crc32(123456789)
