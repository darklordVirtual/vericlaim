# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``pbkdf2`` library, cross-checked against hashlib."""
import hashlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "pbkdf2"))

from pbkdf2 import pbkdf2_hmac, PBKDF2Error  # noqa: E402


def test_rfc6070_vectors():
    assert pbkdf2_hmac("sha1", b"password", b"salt", 1, 20).hex() == \
        "0c60c80f961f0e71f3a9b524af6012062fe037a6"
    assert pbkdf2_hmac("sha1", b"password", b"salt", 2, 20).hex() == \
        "ea6c014dc72d6f8ccd1ed92ace1d41f0d8de8957"
    assert pbkdf2_hmac("sha1", b"password", b"salt", 4096, 20).hex() == \
        "4b007901b765489abead49d926f721d065a429c1"


def test_agrees_with_hashlib():
    for args in (("sha256", b"password", b"salt", 1000, 32),
                 ("sha256", b"pw", b"salt", 1, 64),
                 ("sha512", b"password", b"salt", 200, 64),
                 ("sha256", b"", b"salt", 50, 32)):
        assert pbkdf2_hmac(*args) == hashlib.pbkdf2_hmac(*args)


def test_default_dklen_is_hash_size():
    assert len(pbkdf2_hmac("sha256", b"pw", b"salt", 10)) == 32
    assert len(pbkdf2_hmac("sha1", b"pw", b"salt", 10)) == 20


def test_rejects_bad_input():
    with pytest.raises(PBKDF2Error):
        pbkdf2_hmac("md5-not-real", b"pw", b"salt", 1)
    with pytest.raises(PBKDF2Error):
        pbkdf2_hmac("sha256", b"pw", b"salt", 0)
    with pytest.raises(PBKDF2Error):
        pbkdf2_hmac("sha256", "not bytes", b"salt", 1)
    with pytest.raises(PBKDF2Error):
        pbkdf2_hmac("sha256", b"pw", b"salt", 1, 0)
