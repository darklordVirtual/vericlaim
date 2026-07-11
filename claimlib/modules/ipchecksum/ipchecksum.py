# SPDX-License-Identifier: Apache-2.0
"""RFC 1071 Internet checksum -- the header checksum of IPv4, ICMP, UDP and TCP.

A pre-verified claimlib code artifact for the packet-processing / management
plane. The Internet checksum is the 16-bit one's-complement of the one's-
complement sum of the data taken as 16-bit big-endian words (odd length is
zero-padded). That this implementation reproduces the published IPv4-header
checksum 0xb861 and agrees with an independent computation is registered as a
claim and proven by a committed evidence artifact.

Public API
----------
    checksum(data: bytes) -> int       # 16-bit RFC 1071 checksum
    verify(data: bytes) -> bool        # True iff data already carries its checksum
    checksum_bytes(data: bytes) -> bytes  # the checksum as 2 big-endian bytes

    >>> hex(checksum(bytes.fromhex("45000073000040004011"
    ...                            "0000c0a80001c0a800c7")))
    '0xb861'
"""
from __future__ import annotations


class IPChecksumError(ValueError):
    """The input is not a bytes-like object."""


def checksum(data: bytes) -> int:
    """Return the RFC 1071 Internet checksum of *data* (0..0xFFFF)."""
    if not isinstance(data, (bytes, bytearray)):
        raise IPChecksumError("data must be bytes or bytearray")
    total = 0
    # Sum 16-bit big-endian words; pad a final odd byte with a zero low byte.
    for i in range(0, len(data) - 1, 2):
        total += (data[i] << 8) | data[i + 1]
    if len(data) & 1:
        total += data[-1] << 8
    # Fold carries out of the low 16 bits until none remain.
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def checksum_bytes(data: bytes) -> bytes:
    """Return the checksum as its 2-byte big-endian wire form."""
    return checksum(data).to_bytes(2, "big")


def verify(data: bytes) -> bool:
    """Return True iff *data* (checksum field included) has a valid checksum.

    A correct one's-complement sum over the whole datagram is 0xFFFF, whose
    complement is 0, so a valid frame checksums to 0.
    """
    return checksum(data) == 0
