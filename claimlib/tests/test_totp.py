# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``totp`` library (RFC 6238 test vectors)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "totp"))

from totp import totp, TOTPError  # noqa: E402

SECRET = b"12345678901234567890"


def test_rfc6238_appendix_b_sha1():
    vectors = [(59, "94287082"), (1111111109, "07081804"), (1111111111, "14050471"),
               (1234567890, "89005924"), (2000000000, "69279037"),
               (20000000000, "65353130")]
    for unix_time, expected in vectors:
        assert totp(SECRET, unix_time, digits=8, algorithm="sha1") == expected


def test_counter_derivation():
    # Same 30s window -> same code; next window -> may differ.
    assert totp(SECRET, 30) == totp(SECRET, 59)
    assert totp(SECRET, 0) == totp(SECRET, 29)


def test_rejects_bad_input():
    with pytest.raises(TOTPError):
        totp("not bytes", 59)
    with pytest.raises(TOTPError):
        totp(SECRET, 59, time_step=0)
    with pytest.raises(TOTPError):
        totp(SECRET, 59, algorithm="md5")
    with pytest.raises(TOTPError):
        totp(SECRET, -100)
