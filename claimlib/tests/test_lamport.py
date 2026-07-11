# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``lamport`` library (hash-based one-time signatures)."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "lamport"))

from lamport import keygen, sign, verify, public_key_bytes  # noqa: E402


def test_sign_verify_round_trip():
    sk, pk = keygen(b"seed")
    for message in (b"", b"hello", bytes(range(256)), b"transfer 100"):
        assert verify(message, sign(message, sk), pk) is True


def test_signature_does_not_carry_to_other_message():
    sk, pk = keygen(b"seed")
    sig = sign(b"pay alice 100", sk)
    assert verify(b"pay bob 100", sig, pk) is False


def test_tampered_signature_rejected():
    sk, pk = keygen(b"seed")
    sig = sign(b"msg", sk)
    bad = list(sig)
    bad[5] = bytes([bad[5][0] ^ 0xFF]) + bad[5][1:]
    assert verify(b"msg", bad, pk) is False


def test_wrong_key_rejected():
    sk, _ = keygen(b"seed-a")
    _, pk_b = keygen(b"seed-b")
    assert verify(b"msg", sign(b"msg", sk), pk_b) is False


def test_malformed_signature_rejected():
    sk, pk = keygen(b"seed")
    assert verify(b"msg", sign(b"msg", sk)[:-1], pk) is False   # wrong length
    assert verify(b"msg", "not a list", pk) is False


def test_public_key_serialization_size():
    _, pk = keygen(b"seed")
    assert len(public_key_bytes(pk)) == 2 * 256 * 32
