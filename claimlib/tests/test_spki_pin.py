# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``spki_pin`` library (RFC 7469)."""
import base64
import hashlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "spki_pin"))

from spki_pin import pin_sha256, pin_directive, matches, SPKIPinError  # noqa: E402


def test_pin_equals_base64_sha256():
    for spki in (b"", b"key", bytes(range(64))):
        assert pin_sha256(spki) == base64.b64encode(hashlib.sha256(spki).digest()).decode()


def test_matches_accept_and_reject():
    spki = b"a public key"
    pin = pin_sha256(spki)
    assert matches(spki, [pin]) is True
    assert matches(spki, ["backup-pin-placeholder==", pin]) is True   # backup present
    assert matches(spki, ["wrong-pin"]) is False
    assert matches(spki, []) is False


def test_directive_form():
    assert pin_directive(b"k") == f'pin-sha256="{pin_sha256(b"k")}"'


def test_rejects_bad_input():
    with pytest.raises(SPKIPinError):
        pin_sha256("not bytes")
    with pytest.raises(SPKIPinError):
        matches(b"k", [123])
