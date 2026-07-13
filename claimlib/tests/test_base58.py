# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the base58 module (Bitcoin alphabet)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "base58"
_spec = importlib.util.spec_from_file_location(
    "claimlib_base58", _MOD_DIR / "base58.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_base58"] = _m
_spec.loader.exec_module(_m)

Base58Error = _m.Base58Error
encode = _m.encode
decode = _m.decode


@pytest.mark.parametrize("data,expected", [
    (b"Hello World!", "2NEpo7TZRRrLZSi2U"),
    (b"", ""),
    (b"\x00", "1"),
    (b"\x00\x00", "11"),
    (bytes.fromhex("0000287fb4cd"), "11233QC4"),
    (b"\x00abc", "1ZiCa"),
])
def test_encode_known_vectors(data, expected):
    assert encode(data) == expected


def test_decode_inverts_encode():
    for data in (b"", b"\x00", b"\x00\x00\x01", b"any old bytes",
                 bytes(range(256)), b"\x00" * 5 + b"tail"):
        assert decode(encode(data)) == data


def test_leading_zero_bytes_map_to_ones():
    for n in (0, 1, 2, 10, 87):
        enc = encode(b"\x00" * n + b"\x01")
        assert enc.startswith("1" * n)
        assert not enc.startswith("1" * (n + 1))


def test_alphabet_excludes_ambiguous_chars():
    big = encode(bytes(range(1, 256)) * 3)
    assert not any(c in big for c in "0OIl")


@pytest.mark.parametrize("bad", ["0", "O", "I", "l", "abc!", "1 2"])
def test_decode_rejects_invalid_chars(bad):
    with pytest.raises(Base58Error):
        decode(bad)


def test_type_errors():
    with pytest.raises(Base58Error):
        encode("not bytes")  # type: ignore[arg-type]
    with pytest.raises(Base58Error):
        decode(b"not str")  # type: ignore[arg-type]
