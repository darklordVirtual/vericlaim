# SPDX-License-Identifier: Apache-2.0
"""Varint (LEB128) integer encoding -- the wire format of Protocol Buffers.

A pre-verified claimlib code artifact for compact, self-delimiting integer
serialization. It encodes an unsigned integer as base-128 little-endian groups
with a continuation bit (LEB128), and signed integers via ZigZag mapping so small
magnitudes stay small. That it reproduces the published LEB128 reference vectors
and round-trips losslessly is registered as a claim and proven by a committed
evidence artifact.

Public API
----------
    encode_uvarint(value: int) -> bytes
    decode_uvarint(data: bytes, offset=0) -> tuple[int, int]   # (value, bytes_read)
    zigzag_encode(n: int) -> int
    zigzag_decode(z: int) -> int
    encode_varint(value: int) -> bytes            # signed, via ZigZag
    decode_varint(data: bytes, offset=0) -> tuple[int, int]

    >>> encode_uvarint(300).hex()
    'ac02'
    >>> decode_uvarint(bytes.fromhex('ac02'))
    (300, 2)
"""
from __future__ import annotations


class VarintError(ValueError):
    """Invalid or truncated varint, or a negative unsigned value."""


def encode_uvarint(value: int) -> bytes:
    """Encode a non-negative integer as an unsigned LEB128 varint."""
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise VarintError("value must be a non-negative int")
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)         # continuation bit set
        else:
            out.append(byte)
            return bytes(out)


def decode_uvarint(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Decode an unsigned LEB128 varint. Returns (value, bytes_read)."""
    if not isinstance(data, (bytes, bytearray)):
        raise VarintError("data must be bytes")
    result = 0
    shift = 0
    pos = offset
    while True:
        if pos >= len(data):
            raise VarintError("truncated varint")
        byte = data[pos]
        result |= (byte & 0x7F) << shift
        pos += 1
        if not byte & 0x80:
            return result, pos - offset
        shift += 7
        if shift > 63:
            raise VarintError("varint too long (exceeds 64 bits)")


def zigzag_encode(n: int) -> int:
    """Map a signed integer to an unsigned one, keeping small magnitudes small."""
    if not isinstance(n, int) or isinstance(n, bool):
        raise VarintError("n must be an int")
    return 2 * n if n >= 0 else -2 * n - 1


def zigzag_decode(z: int) -> int:
    """Inverse of :func:`zigzag_encode`."""
    if not isinstance(z, int) or isinstance(z, bool) or z < 0:
        raise VarintError("z must be a non-negative int")
    return z >> 1 if z % 2 == 0 else -((z + 1) >> 1)


def encode_varint(value: int) -> bytes:
    """Encode a signed integer via ZigZag then unsigned LEB128."""
    return encode_uvarint(zigzag_encode(value))


def decode_varint(data: bytes, offset: int = 0) -> tuple[int, int]:
    """Decode a signed ZigZag LEB128 varint. Returns (value, bytes_read)."""
    z, read = decode_uvarint(data, offset)
    return zigzag_decode(z), read
