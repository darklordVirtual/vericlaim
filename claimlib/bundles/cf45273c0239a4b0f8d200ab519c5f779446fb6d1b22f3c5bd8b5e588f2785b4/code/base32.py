# SPDX-License-Identifier: Apache-2.0
"""RFC 4648 base32 encode/decode — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that ``encode``/``decode`` are exact inverses and match
the RFC 4648 section 10 test vectors — is registered as a claim and proven by a
committed evidence artifact; vendoring this module carries that claim (and its
caveat) with it.

The algorithm is implemented from scratch (bit packing over the standard
alphabet); it does NOT call :mod:`base64`. base64 is used only as an independent
oracle in the evidence/tests, never inside this module.

Public API
----------
    encode(data: bytes) -> str    # RFC 4648 base32, with '=' padding
    decode(s: str) -> bytes       # exact inverse of encode

    >>> encode(b"foobar")
    'MZXW6YTBOI======'
    >>> decode("MZXW6YTBOI======")
    b'foobar'
    >>> decode(encode(b"\\x00\\xff\\x10")) == b"\\x00\\xff\\x10"
    True
"""
from __future__ import annotations

# RFC 4648 section 6, "The Base 32 Alphabet".
_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
_PAD = "="
# Reverse lookup: symbol -> 5-bit value.
_DECODE = {ch: i for i, ch in enumerate(_ALPHABET)}

# Number of trailing '=' pad chars for each (input length % 5).
# Groups of 5 input bytes -> 8 output symbols; a short final group is padded.
_PAD_FOR_REMAINDER = {0: 0, 1: 6, 2: 4, 3: 3, 4: 1}
# Valid encoded-block pad counts and how many bytes the final block yields.
_BYTES_FOR_PAD = {0: 5, 1: 4, 3: 3, 4: 2, 6: 1}


class Base32Error(ValueError):
    """The base32 string is malformed (bad symbol, length, or padding)."""


def encode(data: bytes) -> str:
    """Encode *data* to an RFC 4648 base32 string with ``=`` padding."""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("encode() requires bytes")
    if not data:
        return ""
    out: list[str] = []
    # Process each 5-byte group into 8 symbols.
    for i in range(0, len(data), 5):
        chunk = bytes(data[i:i + 5])
        n = len(chunk)
        # Pack up to 40 bits big-endian, zero-filling the short tail.
        acc = 0
        for b in chunk:
            acc = (acc << 8) | b
        acc <<= 8 * (5 - n)
        # Emit 8 five-bit symbols, most-significant first.
        syms = [(acc >> (35 - 5 * j)) & 0x1F for j in range(8)]
        pad = _PAD_FOR_REMAINDER[n % 5]
        keep = 8 - pad
        for j in range(keep):
            out.append(_ALPHABET[syms[j]])
        out.append(_PAD * pad)
    return "".join(out)


def decode(s: str) -> bytes:
    """Decode an RFC 4648 base32 string. Exact inverse of :func:`encode`.

    Raises :class:`Base32Error` on an invalid length, unknown symbol, or
    malformed padding — fail closed rather than return partial bytes.
    """
    if not isinstance(s, str):
        raise TypeError("decode() requires str")
    if s == "":
        return b""
    if len(s) % 8 != 0:
        raise Base32Error("length must be a multiple of 8")
    out = bytearray()
    for i in range(0, len(s), 8):
        block = s[i:i + 8]
        # Padding must be a contiguous run of '=' at the end of the block, and
        # may only appear in the final block.
        pad = block.count(_PAD)
        if pad:
            if i + 8 != len(s):
                raise Base32Error("padding before final block")
            if block[8 - pad:] != _PAD * pad or _PAD in block[:8 - pad]:
                raise Base32Error("non-trailing padding")
        if pad not in _BYTES_FOR_PAD:
            raise Base32Error(f"invalid padding count {pad}")
        acc = 0
        for ch in block[:8 - pad]:
            val = _DECODE.get(ch)
            if val is None:
                raise Base32Error(f"invalid symbol {ch!r}")
            acc = (acc << 5) | val
        # Left-align to 40 bits, then take the meaningful high bytes.
        acc <<= 5 * pad
        nbytes = _BYTES_FOR_PAD[pad]
        block_bytes = [(acc >> (32 - 8 * k)) & 0xFF for k in range(5)]
        out.extend(block_bytes[:nbytes])
    return bytes(out)
