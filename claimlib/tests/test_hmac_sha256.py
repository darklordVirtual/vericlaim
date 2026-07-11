# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``hmac_sha256`` library, cross-checked against stdlib hmac."""
import hashlib
import hmac as stdlib_hmac
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "hmac_sha256"))

from hmac_sha256 import hmac_sha256, hexdigest, verify, HMACError  # noqa: E402


def test_rfc4231_tc2_published_tag():
    assert hexdigest(b"Jefe", b"what do ya want for nothing?") == \
        "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"


def test_agrees_with_stdlib_hmac():
    for key, msg in ((b"\x0b" * 20, b"Hi There"), (b"\xaa" * 131, b"big key"),
                     (b"", b""), (b"k", bytes(range(256)))):
        assert hmac_sha256(key, msg) == stdlib_hmac.new(key, msg, hashlib.sha256).digest()


def test_verify_accept_and_reject():
    tag = hmac_sha256(b"secret", b"payload")
    assert verify(b"secret", b"payload", tag) is True
    assert verify(b"secret", b"payload", bytes([tag[0] ^ 0x01]) + tag[1:]) is False
    assert verify(b"wrong", b"payload", tag) is False
    assert verify(b"secret", b"payload", tag[:-1]) is False   # wrong length


def test_rejects_non_bytes():
    with pytest.raises(HMACError):
        hmac_sha256("key", b"msg")
    with pytest.raises(HMACError):
        verify(b"k", b"m", "not bytes")
