# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the punycode module (RFC 3492)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "punycode"
_spec = importlib.util.spec_from_file_location(
    "claimlib_punycode", _MOD_DIR / "punycode.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_punycode"] = _m
_spec.loader.exec_module(_m)

PunycodeError = _m.PunycodeError
encode = _m.encode
decode = _m.decode


@pytest.mark.parametrize("text,expected", [
    ("bücher", "bcher-kva"),
    ("Pročprostěnemluvíčesky", "Proprostnemluvesky-uyb24dma41a"),
    ("そのスピードで", "d9juau41awczczp"),
    ("-> $1.00 <-", "-> $1.00 <--"),
    ("", ""),
    ("plain", "plain-"),
])
def test_encode_known(text, expected):
    assert encode(text) == expected


def test_decode_inverts_encode():
    for text in ("bücher", "æøå", "MajiでKoiする5秒前", "café", "x", ""):
        assert decode(encode(text)) == text


def test_decoder_accepts_uppercase_digits():
    assert decode("BCHER-KVA".lower()) == "bücher"
    # digit letters are case-insensitive on decode (RFC 3492 section 5)
    assert decode("bcher-KVA") == "bücher"


def test_agrees_with_stdlib_codec():
    for text in ("bücher", "münchen", "日本語テスト", "Ålesund", "היי"):
        stdlib = text.encode("punycode").decode("ascii")
        assert encode(text) == stdlib
        assert decode(stdlib) == text


def test_non_string_and_overflow_rejected():
    with pytest.raises(PunycodeError):
        decode("999999999999a")
    with pytest.raises(PunycodeError):
        encode(None)  # type: ignore[arg-type]
    with pytest.raises(PunycodeError):
        decode(None)  # type: ignore[arg-type]


def test_decode_rejects_non_ascii_input():
    with pytest.raises(PunycodeError):
        decode("bücher-kva")
