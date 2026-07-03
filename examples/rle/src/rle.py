# SPDX-License-Identifier: Apache-2.0
"""A tiny run-length encoder — the worked example for Claim-Oriented Programming.

The point is NOT the algorithm; it is that the example lives in a domain
(lossless compression) completely unrelated to how vericlaim was distilled.
The claims we make about it (compression ratio, round-trip losslessness) are
registered, backed by a committed benchmark artifact, and bound to the docs.
"""
from __future__ import annotations


def encode(data: bytes) -> bytes:
    """Run-length encode: (count, byte) pairs, count in 1..255."""
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        run = 1
        while i + run < n and data[i + run] == b and run < 255:
            run += 1
        out.append(run)
        out.append(b)
        i += run
    return bytes(out)


def decode(data: bytes) -> bytes:
    """Inverse of :func:`encode`."""
    out = bytearray()
    for i in range(0, len(data), 2):
        count, b = data[i], data[i + 1]
        out.extend([b] * count)
    return bytes(out)


def ratio(data: bytes) -> float:
    """Compression ratio original/encoded (>1 means it shrank)."""
    enc = encode(data)
    return len(data) / len(enc) if enc else 1.0
