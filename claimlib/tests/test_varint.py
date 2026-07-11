# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``varint`` library (LEB128 + ZigZag)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "varint"))

from varint import (  # noqa: E402
    encode_uvarint, decode_uvarint, encode_varint, decode_varint,
    zigzag_encode, zigzag_decode, VarintError)


def test_published_leb128():
    assert encode_uvarint(300).hex() == "ac02"
    assert encode_uvarint(624485).hex() == "e58e26"
    assert encode_uvarint(0).hex() == "00"
    assert encode_uvarint(127).hex() == "7f"
    assert encode_uvarint(128).hex() == "8001"


def test_decode_returns_bytes_read():
    assert decode_uvarint(bytes.fromhex("ac02")) == (300, 2)
    # A varint embedded in a longer buffer decodes at an offset.
    assert decode_uvarint(bytes.fromhex("ffac02"), offset=1) == (300, 2)


def test_zigzag_mapping():
    for signed, unsigned in ((0, 0), (-1, 1), (1, 2), (-2, 3), (2, 4)):
        assert zigzag_encode(signed) == unsigned
        assert zigzag_decode(unsigned) == signed


def test_round_trip():
    for x in (0, 1, 127, 128, 300, 2 ** 63, 2 ** 64 - 1):
        assert decode_uvarint(encode_uvarint(x))[0] == x
    for x in (-1000, -1, 0, 1, 1000, 2 ** 31, -(2 ** 31)):
        assert decode_varint(encode_varint(x))[0] == x


def test_rejects_bad_input():
    with pytest.raises(VarintError):
        encode_uvarint(-1)
    with pytest.raises(VarintError):
        decode_uvarint(b"\x80\x80\x80")     # truncated (all continuation bits)
    with pytest.raises(VarintError):
        decode_uvarint(b"\xff" * 11)        # exceeds 64 bits
