# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``ipchecksum`` library.

Reference: the published IPv4 header checksum example (Wikipedia) == 0xb861.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "ipchecksum"))

from ipchecksum import checksum, checksum_bytes, verify, IPChecksumError  # noqa: E402

HEADER_NO_CKSUM = bytes.fromhex("45000073000040004011" "0000c0a80001c0a800c7")


def test_published_ipv4_header_checksum():
    assert checksum(HEADER_NO_CKSUM) == 0xB861


def test_insert_and_verify():
    full = HEADER_NO_CKSUM[:10] + checksum_bytes(HEADER_NO_CKSUM) + HEADER_NO_CKSUM[12:]
    assert verify(full) is True
    # Corrupt one byte -> no longer verifies.
    corrupt = bytes([full[0] ^ 0x01]) + full[1:]
    assert verify(corrupt) is False


def test_odd_length_padding():
    # Odd-length input is padded with a zero low byte.
    assert checksum(b"\x12\x34\x56") == checksum(b"\x12\x34\x56\x00")


def test_wire_bytes_big_endian():
    assert checksum_bytes(HEADER_NO_CKSUM) == bytes([0xB8, 0x61])


def test_rejects_non_bytes():
    with pytest.raises(IPChecksumError):
        checksum("not bytes")
