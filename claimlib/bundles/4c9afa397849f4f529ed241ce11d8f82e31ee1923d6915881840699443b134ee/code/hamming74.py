# SPDX-License-Identifier: Apache-2.0
"""Hamming(7,4) single-error-correcting code -- forward error correction for
noisy telecom / storage channels.

A pre-verified claimlib code artifact. The Hamming(7,4) code protects 4 data
bits with 3 parity bits so that ANY single-bit error in the resulting 7-bit
codeword can be located and corrected. This module encodes and decodes; that it
recovers the original 4 bits under every single-bit error, verified EXHAUSTIVELY
over the entire input space, is registered as a claim and proven by a committed
evidence artifact.

Bit layout (1-indexed positions, even parity):
    position: 1  2  3  4  5  6  7
    role:     p1 p2 d1 p4 d2 d3 d4
    p1 covers 1,3,5,7 | p2 covers 2,3,6,7 | p4 covers 4,5,6,7

Public API
----------
    encode(nibble: int) -> int              # 0..15 data -> 0..127 codeword
    decode(codeword: int) -> tuple[int, int] # (nibble, error_position 0=none)

    >>> code = encode(0b1011)
    >>> decode(code ^ 0b0000100)            # flip one bit
    (11, 3)
"""
from __future__ import annotations


class HammingError(ValueError):
    """The nibble is out of 0..15 or the codeword is out of 0..127."""


def _bit(value: int, position: int) -> int:
    """Return the bit at 1-indexed *position* (position 1 = least significant)."""
    return (value >> (position - 1)) & 1


def encode(nibble: int) -> int:
    """Encode a 4-bit value (0..15) into its 7-bit Hamming codeword."""
    if not isinstance(nibble, int) or isinstance(nibble, bool) or not 0 <= nibble <= 15:
        raise HammingError("nibble must be an int in 0..15")
    d1 = (nibble >> 0) & 1
    d2 = (nibble >> 1) & 1
    d3 = (nibble >> 2) & 1
    d4 = (nibble >> 3) & 1
    p1 = d1 ^ d2 ^ d4          # covers positions 3,5,7
    p2 = d1 ^ d3 ^ d4          # covers positions 3,6,7
    p4 = d2 ^ d3 ^ d4          # covers positions 5,6,7
    # Assemble bits at 1-indexed positions 1..7.
    return (p1 << 0) | (p2 << 1) | (d1 << 2) | (p4 << 3) | \
           (d2 << 4) | (d3 << 5) | (d4 << 6)


def decode(codeword: int) -> tuple[int, int]:
    """Decode a 7-bit codeword, correcting any single-bit error.

    Returns ``(nibble, error_position)`` where *error_position* is the 1-indexed
    position that was corrected, or 0 if the codeword had no detectable error.
    """
    if not isinstance(codeword, int) or isinstance(codeword, bool) or not 0 <= codeword <= 127:
        raise HammingError("codeword must be an int in 0..127")
    s1 = _bit(codeword, 1) ^ _bit(codeword, 3) ^ _bit(codeword, 5) ^ _bit(codeword, 7)
    s2 = _bit(codeword, 2) ^ _bit(codeword, 3) ^ _bit(codeword, 6) ^ _bit(codeword, 7)
    s4 = _bit(codeword, 4) ^ _bit(codeword, 5) ^ _bit(codeword, 6) ^ _bit(codeword, 7)
    syndrome = s1 | (s2 << 1) | (s4 << 2)   # 1-indexed error position, 0 = none
    if syndrome != 0:
        codeword ^= 1 << (syndrome - 1)
    d1 = _bit(codeword, 3)
    d2 = _bit(codeword, 5)
    d3 = _bit(codeword, 6)
    d4 = _bit(codeword, 7)
    nibble = d1 | (d2 << 1) | (d3 << 2) | (d4 << 3)
    return nibble, syndrome
