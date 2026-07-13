# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the chacha20 module (RFC 8439)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "chacha20"
_spec = importlib.util.spec_from_file_location(
    "claimlib_chacha20", _MOD_DIR / "chacha20.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_chacha20"] = _m
_spec.loader.exec_module(_m)

ChaCha20Error = _m.ChaCha20Error
chacha20_block = _m.chacha20_block
chacha20_encrypt = _m.chacha20_encrypt
chacha20_decrypt = _m.chacha20_decrypt
quarter_round = _m.quarter_round

KEY = bytes(range(32))
NONCE = bytes.fromhex("000000000000004a00000000")


def test_quarter_round_rfc_vector():
    assert quarter_round(0x11111111, 0x01020304, 0x9B8D6F43, 0x01234567) == \
        (0xEA2A92F4, 0xCB1CF8CE, 0x4581472E, 0x5881C4BB)


def test_block_all_zero_vector():
    assert chacha20_block(bytes(32), 0, bytes(12)).hex().startswith(
        "76b8e0ada0f13d90405d6ae55386bd28")


def test_block_is_64_bytes():
    assert len(chacha20_block(KEY, 0, NONCE)) == 64


def test_encrypt_decrypt_roundtrip():
    for msg in (b"", b"a", b"hello world", bytes(64), bytes(range(200))):
        ct = chacha20_encrypt(KEY, 1, NONCE, msg)
        assert chacha20_decrypt(KEY, 1, NONCE, ct) == msg


def test_encrypt_matches_blockwise_composition():
    msg = bytes(range(150))
    whole = chacha20_encrypt(KEY, 5, NONCE, msg)
    parts = (chacha20_encrypt(KEY, 5, NONCE, msg[:64])
             + chacha20_encrypt(KEY, 6, NONCE, msg[64:128])
             + chacha20_encrypt(KEY, 7, NONCE, msg[128:]))
    assert whole == parts


def test_different_nonce_differs():
    msg = b"same message"
    a = chacha20_encrypt(KEY, 1, NONCE, msg)
    b = chacha20_encrypt(KEY, 1, bytes.fromhex("000000000000004b00000000"), msg)
    assert a != b


@pytest.mark.parametrize("key,counter,nonce", [
    (bytes(31), 0, bytes(12)),
    (bytes(33), 0, bytes(12)),
    (bytes(32), 0, bytes(11)),
    (bytes(32), -1, bytes(12)),
    (bytes(32), 2 ** 32, bytes(12)),
    (bytes(32), True, bytes(12)),
])
def test_bad_inputs_rejected(key, counter, nonce):
    with pytest.raises(ChaCha20Error):
        chacha20_block(key, counter, nonce)


def test_counter_overflow_rejected():
    with pytest.raises(ChaCha20Error):
        chacha20_encrypt(bytes(32), 2 ** 32 - 1, bytes(12), bytes(65))


def test_quarter_round_rejects_out_of_range():
    with pytest.raises(ChaCha20Error):
        quarter_round(-1, 0, 0, 0)
    with pytest.raises(ChaCha20Error):
        quarter_round(2 ** 32, 0, 0, 0)
