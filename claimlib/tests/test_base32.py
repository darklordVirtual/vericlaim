# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable base32 module (claimlib/modules/base32)."""
from __future__ import annotations

import base64
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "base32"))

from base32 import Base32Error, decode, encode  # noqa: E402


# RFC 4648 section 10 test vectors (independent of the module).
RFC_VECTORS = [
    (b"", ""),
    (b"f", "MY======"),
    (b"fo", "MZXQ===="),
    (b"foo", "MZXW6==="),
    (b"foob", "MZXW6YQ="),
    (b"fooba", "MZXW6YTB"),
    (b"foobar", "MZXW6YTBOI======"),
]


@pytest.mark.parametrize("data,expected", RFC_VECTORS)
def test_rfc4648_encode(data, expected):
    assert encode(data) == expected


@pytest.mark.parametrize("data,expected", RFC_VECTORS)
def test_rfc4648_decode(data, expected):
    assert decode(expected) == data


def test_roundtrip_all_bytes():
    data = bytes(range(256))
    assert decode(encode(data)) == data


def test_cross_check_stdlib():
    # base64.b32encode is an independent oracle (not used inside the module).
    for data in [b"", b"\x00", b"\xff\xff\xff", b"Hello, World!",
                 bytes(range(256)), b"\xde\xad\xbe\xef"]:
        assert encode(data) == base64.b32encode(data).decode("ascii")
        assert decode(base64.b32encode(data).decode("ascii")) == data


def test_decode_rejects_bad_length():
    with pytest.raises(Base32Error):
        decode("MY=====")  # length 7, not a multiple of 8


def test_decode_rejects_bad_symbol():
    with pytest.raises(Base32Error):
        decode("M1======")  # '1' is not in the RFC 4648 alphabet


def test_decode_rejects_bad_padding():
    with pytest.raises(Base32Error):
        decode("M=======")  # 7 pad chars is not a valid block padding
    with pytest.raises(Base32Error):
        decode("========")  # all padding


def test_decode_rejects_padding_before_final_block():
    with pytest.raises(Base32Error):
        decode("MY======MZXW6YTB")  # padded block that is not last


def test_encode_requires_bytes():
    with pytest.raises(TypeError):
        encode("not bytes")


def test_decode_requires_str():
    with pytest.raises(TypeError):
        decode(b"MZXW6YTB")
