# SPDX-License-Identifier: Apache-2.0
"""Base58 (Bitcoin alphabet) encode/decode — a reusable, stdlib-only block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that ``encode``/``decode`` are exact inverses,
preserve leading zero bytes, and match the published test vectors of
draft-msporny-base58-03 and Bitcoin Core — is registered as a claim and
proven by a committed evidence artifact; vendoring this module carries that
claim (and its caveat) with it.

Base58 treats the input bytes as one big-endian integer and rewrites it in
base 58 over an alphabet that omits the visually ambiguous characters
0 (zero), O (capital o), I (capital i) and l (lower-case L), plus all
non-alphanumerics. Because leading 0x00 bytes vanish in integer arithmetic,
each one is encoded explicitly as a leading '1' (the zero symbol) — the rule
that distinguishes a correct implementation from a subtly lossy one. This is
the Bitcoin/IPFS/DID alphabet; Ripple and Flickr use different orderings that
are NOT interchangeable with this module.

Base58 is an encoding, not encryption and not an integrity check; Bitcoin
addresses layer a separate checksum (Base58Check) on top, which is out of
scope here.

Public API
----------
    ALPHABET: str                 # the 58-character Bitcoin alphabet
    encode(data: bytes) -> str    # Base58 string, leading 0x00 -> '1'
    decode(s: str) -> bytes       # exact inverse of encode

    >>> encode(b"Hello World!")
    '2NEpo7TZRRrLZSi2U'
    >>> decode("2NEpo7TZRRrLZSi2U")
    b'Hello World!'
    >>> encode(b"\\x00\\x00\\x28\\x7f\\xb4\\xcd")
    '11233QC4'
"""
from __future__ import annotations

# draft-msporny-base58-03 section 2 (the Bitcoin alphabet).
ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
# Reverse lookup: character -> value 0..57.
_DECODE = {ch: i for i, ch in enumerate(ALPHABET)}


class Base58Error(ValueError):
    """The base58 string contains a character outside the alphabet."""


def encode(data: bytes) -> str:
    """Encode *data* to a Base58 string (Bitcoin alphabet).

    Each leading 0x00 byte becomes a leading ``'1'``; the remaining bytes are
    interpreted as a big-endian integer and written in base 58, most
    significant digit first. ``encode(b"") == ""``.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise Base58Error("encode() requires bytes")
    data = bytes(data)
    zeros = 0
    for b in data:
        if b != 0:
            break
        zeros += 1
    n = int.from_bytes(data, "big")
    syms: list[str] = []
    while n:
        n, r = divmod(n, 58)
        syms.append(ALPHABET[r])
    return "1" * zeros + "".join(reversed(syms))


def decode(s: str) -> bytes:
    """Decode a Base58 string. Exact inverse of :func:`encode`.

    Each leading ``'1'`` becomes a 0x00 byte; the whole string is evaluated
    as a base-58 positional number and rendered big-endian. Raises
    :class:`Base58Error` on any character outside the alphabet — fail closed
    rather than guess (in particular ``0``, ``O``, ``I`` and ``l`` are
    invalid by design). ``decode("") == b""``.
    """
    if not isinstance(s, str):
        raise Base58Error("decode() requires str")
    ones = 0
    for ch in s:
        if ch != "1":
            break
        ones += 1
    n = 0
    for ch in s:
        val = _DECODE.get(ch)
        if val is None:
            raise Base58Error(f"invalid base58 character {ch!r}")
        n = n * 58 + val
    payload = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\x00" * ones + payload
