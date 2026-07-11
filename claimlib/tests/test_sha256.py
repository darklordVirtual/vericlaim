# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``sha256`` library, cross-checked against hashlib."""
import hashlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "sha256"))

from sha256 import sha256, hexdigest, SHA256Error  # noqa: E402


def test_published_values():
    assert hexdigest(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert hexdigest(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_agrees_with_hashlib():
    for data in (b"", b"a", b"hello world", b"\x00" * 64, b"\x00" * 65,
                 b"\xff" * 500, bytes(range(256))):
        assert sha256(data).hex() == hashlib.sha256(data).hexdigest()


def test_block_boundary_lengths():
    # Padding edge cases around the 64-byte block boundary.
    for n in (55, 56, 57, 63, 64, 65, 119, 128):
        data = b"x" * n
        assert sha256(data) == hashlib.sha256(data).digest()


def test_digest_is_32_bytes():
    assert len(sha256(b"anything")) == 32


def test_rejects_non_bytes():
    with pytest.raises(SHA256Error):
        sha256("a string")
