# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``hotp`` library (RFC 4226 test vectors)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "hotp"))

from hotp import hotp, HOTPError  # noqa: E402

SECRET = b"12345678901234567890"


def test_rfc4226_appendix_d():
    expected = ["755224", "287082", "359152", "969429", "338314",
                "254676", "287922", "162583", "399871", "520489"]
    for counter, exp in enumerate(expected):
        assert hotp(SECRET, counter) == exp


def test_digit_lengths():
    assert len(hotp(SECRET, 0, digits=8)) == 8
    assert hotp(SECRET, 0, digits=8).endswith("755224")   # 8-digit contains the 6-digit tail


def test_rejects_bad_input():
    with pytest.raises(HOTPError):
        hotp("not bytes", 0)
    with pytest.raises(HOTPError):
        hotp(SECRET, -1)
    with pytest.raises(HOTPError):
        hotp(SECRET, 0, digits=0)
    with pytest.raises(HOTPError):
        hotp(SECRET, 0, digits=11)
