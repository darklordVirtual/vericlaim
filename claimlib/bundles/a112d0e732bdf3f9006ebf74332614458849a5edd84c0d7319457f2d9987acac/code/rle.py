# SPDX-License-Identifier: Apache-2.0
"""Byte-oriented run-length codec — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that ``decode`` is an exact inverse of ``encode``
for arbitrary byte input — is registered as a claim and proven by a committed
evidence artifact; vendoring this module carries that claim (and its caveat)
with it.

Public API
----------
    encode(data: bytes) -> bytes    # run-length compress
    decode(data: bytes) -> bytes    # exact inverse of encode

Wire format
-----------
The stream is a sequence of ``(count, byte)`` pairs. ``count`` is a single
byte in the range 1..255 and ``byte`` is the repeated value, so the pair
``\\x04A`` decodes to ``b'AAAA'``. Runs longer than 255 are split into
consecutive maximal pairs. The empty input encodes to the empty output.

This is the classic *packbits-free* byte-pair RLE: every symbol occupies two
output bytes, which makes the codec trivially correct and its inverse total,
at the cost of doubling the size of incompressible data (see the caveat in the
registered claim).

    >>> encode(b'aaaabbbc')
    b'\\x04a\\x03b\\x01c'
    >>> decode(encode(b'aaaabbbc'))
    b'aaaabbbc'
    >>> decode(encode(b'')) == b''
    True
"""
from __future__ import annotations

# Maximum run length representable in a single count byte.
_MAX_RUN = 255


class RleError(ValueError):
    """The encoded stream is malformed (truncated pair or zero count)."""


def encode(data: bytes) -> bytes:
    """Run-length encode *data* into a sequence of ``(count, byte)`` pairs.

    Consecutive identical bytes are collapsed into a count-prefixed pair. A
    run longer than 255 is emitted as several maximal pairs. Accepts any
    ``bytes``/``bytearray``; returns ``bytes``. The empty input maps to the
    empty output.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"encode expects bytes, got {type(data).__name__}")
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        b = data[i]
        run = 1
        # Extend the run while the next byte matches and we have headroom.
        while i + run < n and data[i + run] == b and run < _MAX_RUN:
            run += 1
        out.append(run)
        out.append(b)
        i += run
    return bytes(out)


def decode(data: bytes) -> bytes:
    """Decode an RLE stream produced by :func:`encode` back to raw bytes.

    Reads the stream as ``(count, byte)`` pairs. Raises :class:`RleError` on a
    truncated stream (odd length) or a zero count, both of which are
    unreachable from :func:`encode` output and signal corruption. Returns
    ``bytes``; the empty input maps to the empty output.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError(f"decode expects bytes, got {type(data).__name__}")
    if len(data) % 2 != 0:
        raise RleError("truncated RLE stream: odd number of bytes")
    out = bytearray()
    for i in range(0, len(data), 2):
        count = data[i]
        if count == 0:
            raise RleError(f"invalid zero run length at offset {i}")
        out.extend(bytes([data[i + 1]]) * count)
    return bytes(out)
