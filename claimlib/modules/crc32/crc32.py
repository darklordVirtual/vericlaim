# SPDX-License-Identifier: Apache-2.0
"""CRC-32 (IEEE 802.3) checksum — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that it reproduces the published CRC-32 reference values
and agrees byte-for-byte with the reference implementation in the standard
library — is registered as a claim and proven by a committed evidence artifact;
vendoring this module carries that claim (and its caveat) with it.

This is the ubiquitous "CRC-32" used by zip, gzip, PNG and Ethernet (IEEE
802.3): the reflected generator polynomial 0xEDB88320, input and output
reflected, initial value 0xFFFFFFFF, final XOR 0xFFFFFFFF. The result is an
unsigned 32-bit integer in the range 0 .. 2**32 - 1.

No ``zlib`` is used here — the algorithm is implemented directly. ``zlib.crc32``
is only the *independent* oracle in the evidence and tests.

Public API
----------
    crc32(data: bytes) -> int          # unsigned 0 .. 2**32 - 1

    >>> hex(crc32(b"123456789"))
    '0xcbf43926'
    >>> crc32(b"")
    0
"""
from __future__ import annotations

# Reflected CRC-32 generator polynomial (IEEE 802.3): 0xEDB88320.
_POLY = 0xEDB88320


def _make_table() -> tuple[int, ...]:
    """Precompute the 256-entry byte-wise CRC-32 lookup table."""
    table = []
    for n in range(256):
        crc = n
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ _POLY
            else:
                crc >>= 1
        table.append(crc)
    return tuple(table)


_TABLE = _make_table()


def crc32(data: bytes) -> int:
    """CRC-32 (IEEE 802.3) of *data* as an unsigned 32-bit integer.

    Uses the standard reflected algorithm with init/final value 0xFFFFFFFF,
    matching the checksum used by zip/gzip/PNG and ``zlib.crc32``.
    """
    if not isinstance(data, (bytes, bytearray, memoryview)):
        raise TypeError("crc32() requires a bytes-like object")
    crc = 0xFFFFFFFF
    for byte in bytes(data):
        crc = (crc >> 8) ^ _TABLE[(crc ^ byte) & 0xFF]
    return crc ^ 0xFFFFFFFF
