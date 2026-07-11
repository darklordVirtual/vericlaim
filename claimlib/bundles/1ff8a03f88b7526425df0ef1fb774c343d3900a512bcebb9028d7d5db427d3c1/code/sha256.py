# SPDX-License-Identifier: Apache-2.0
"""SHA-256 (FIPS 180-4) implemented from scratch -- a reusable, claim-bound hash.

A pre-verified claimlib code artifact. This module computes the SHA-256 digest
DIRECTLY (message padding, the 64-word schedule, and the 64-round compression
function over pure 32-bit integer arithmetic) and never imports :mod:`hashlib`,
so it is a genuine independent implementation. That its digest reproduces the
published FIPS 180-4 check values AND agrees byte-for-byte with the stdlib
``hashlib.sha256`` over a fixed battery is registered as a claim and proven by a
committed evidence artifact. Vendoring carries that claim (and its caveat).

Public API
----------
    sha256(data: bytes) -> bytes      # the 32-byte digest
    hexdigest(data: bytes) -> str     # the digest as 64 lowercase hex chars

    >>> hexdigest(b"abc")
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
"""
from __future__ import annotations

_MASK = 0xFFFFFFFF

# First 32 bits of the fractional parts of the cube roots of the first 64 primes.
_K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1,
    0x923F82A4, 0xAB1C5ED5, 0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
    0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174, 0xE49B69C1, 0xEFBE4786,
    0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147,
    0x06CA6351, 0x14292967, 0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
    0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85, 0xA2BFE8A1, 0xA81A664B,
    0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A,
    0x5B9CCA4F, 0x682E6FF3, 0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
    0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)

# First 32 bits of the fractional parts of the square roots of the first 8 primes.
_H0 = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)


class SHA256Error(ValueError):
    """The input is not a bytes-like object."""


def _rotr(value: int, bits: int) -> int:
    return ((value >> bits) | (value << (32 - bits))) & _MASK


def sha256(data: bytes) -> bytes:
    """Return the 32-byte SHA-256 digest of *data*."""
    if not isinstance(data, (bytes, bytearray)):
        raise SHA256Error("data must be bytes or bytearray")
    message = bytearray(data)
    bit_len = (len(message) * 8) & 0xFFFFFFFFFFFFFFFF
    message.append(0x80)
    while len(message) % 64 != 56:
        message.append(0x00)
    message += bit_len.to_bytes(8, "big")

    h = list(_H0)
    for base in range(0, len(message), 64):
        block = message[base:base + 64]
        w = [int.from_bytes(block[i:i + 4], "big") for i in range(0, 64, 4)]
        for i in range(16, 64):
            s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK)

        a, b, c, d, e, f, g, hh = h
        for i in range(64):
            big_s1 = _rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25)
            ch = (e & f) ^ (~e & g)
            t1 = (hh + big_s1 + ch + _K[i] + w[i]) & _MASK
            big_s0 = _rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (big_s0 + maj) & _MASK
            hh, g, f, e, d, c, b, a = g, f, e, (d + t1) & _MASK, c, b, a, (t1 + t2) & _MASK

        for i, value in enumerate((a, b, c, d, e, f, g, hh)):
            h[i] = (h[i] + value) & _MASK

    return b"".join(x.to_bytes(4, "big") for x in h)


def hexdigest(data: bytes) -> str:
    """Return the SHA-256 digest of *data* as 64 lowercase hex characters."""
    return sha256(data).hex()
