# SPDX-License-Identifier: Apache-2.0
"""Bloom filter — probabilistic set membership with SHA-256 double hashing.

A pre-verified code artifact from the VeriClaim claim library. The properties
that make it trustworthy — zero false negatives over a fixed 500-element
battery, a deterministic measured false-positive count over a disjoint probe
set, and the false-positive-rate formula matching exact rational arithmetic —
are registered as a claim and proven by a committed evidence artifact;
vendoring this module carries that claim (and its caveat) with it.

A Bloom filter (Bloom, CACM 13(7), 1970) represents a set with an m-bit array
and k hash functions: ``add`` sets the k bits an item hashes to, ``contains``
answers True iff all k are set. Membership queries can return false POSITIVES
(an absent item whose k bits were all set by others) but never false
NEGATIVES: an added item's bits stay set. Under the classical
independent-hashing analysis, the false-positive probability after inserting
n items is

    p = (1 - (1 - 1/m)**(k*n))**k          # exact form of the analysis

and the k minimising p for given m, n is (m/n)·ln 2 (rounded to an integer
here, floored at 1).

Hash derivation (documented so evidence can recompute it independently):
the 32-byte SHA-256 digest of the item (str is UTF-8-encoded first) is split
into two 128-bit big-endian halves h1 = digest[0:16], h2 = digest[16:32].
Both are reduced mod m; if h2 mod m == 0 it is set to 1 so the probe sequence
advances. The k bit indexes are (h1 + i*h2) mod m for i = 0..k-1 — the
Kirsch–Mitzenmacher double-hashing scheme, which preserves the asymptotic
false-positive probability of k independent hash functions.

Public API
----------
    BloomFilter(m_bits, k)                 # m-bit array, k derived hashes
        .add(item)                         # item: str | bytes
        .contains(item)  /  item in bf
        .bits_set() -> int                 # population count
        .bit_array() -> bytes              # snapshot of the backing bits
    indexes(item, m_bits, k) -> list[int]  # the k bit positions for item
    false_positive_rate(m_bits, n_items, k) -> float
    optimal_k(m_bits, n_items) -> int      # max(1, round((m/n) ln 2))

    >>> bf = BloomFilter(m_bits=4096, k=6)
    >>> bf.add("alice")
    >>> "alice" in bf
    True
    >>> optimal_k(4096, 500)
    6
"""
from __future__ import annotations

import hashlib
import math


class BloomError(ValueError):
    """Invalid Bloom-filter parameter or unsupported item type."""


def _check_positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise BloomError(f"{name} must be an int, got {value!r}")
    if value < 1:
        raise BloomError(f"{name} must be >= 1, got {value}")
    return value


def _key_bytes(item: object) -> bytes:
    """Return the canonical byte form of *item* (str is UTF-8-encoded)."""
    if isinstance(item, bytes):
        return item
    if isinstance(item, str):
        return item.encode("utf-8")
    raise BloomError(f"item must be str or bytes, got {type(item).__name__}")


def indexes(item: str | bytes, m_bits: int, k: int) -> list[int]:
    """Return the k bit indexes for *item* in an m_bits-wide filter.

    Kirsch–Mitzenmacher double hashing over the SHA-256 digest: h1 is the
    first 16 digest bytes, h2 the last 16 (big-endian), both mod m_bits;
    h2 is forced to 1 when it reduces to 0. Index i is (h1 + i*h2) mod m_bits.
    """
    _check_positive_int(m_bits, "m_bits")
    _check_positive_int(k, "k")
    digest = hashlib.sha256(_key_bytes(item)).digest()
    h1 = int.from_bytes(digest[:16], "big") % m_bits
    h2 = int.from_bytes(digest[16:32], "big") % m_bits
    if h2 == 0:
        h2 = 1  # keep the probe sequence advancing
    return [(h1 + i * h2) % m_bits for i in range(k)]


class BloomFilter:
    """An m_bits-wide Bloom filter using k SHA-256-derived hash functions."""

    __slots__ = ("m_bits", "k", "_bits")

    def __init__(self, m_bits: int, k: int) -> None:
        self.m_bits = _check_positive_int(m_bits, "m_bits")
        self.k = _check_positive_int(k, "k")
        self._bits = bytearray((m_bits + 7) // 8)

    def add(self, item: str | bytes) -> None:
        """Insert *item*: set all k of its bit positions."""
        for ix in indexes(item, self.m_bits, self.k):
            self._bits[ix >> 3] |= 1 << (ix & 7)

    def contains(self, item: str | bytes) -> bool:
        """True iff all k bit positions for *item* are set.

        A True answer may be a false positive; a False answer is definitive
        (Bloom filters have no false negatives).
        """
        return all(
            (self._bits[ix >> 3] >> (ix & 7)) & 1
            for ix in indexes(item, self.m_bits, self.k)
        )

    __contains__ = contains

    def bits_set(self) -> int:
        """Number of 1-bits currently set (population count)."""
        return sum(bin(b).count("1") for b in self._bits)

    def bit_array(self) -> bytes:
        """Immutable snapshot of the backing bit array (LSB-first per byte)."""
        return bytes(self._bits)


def false_positive_rate(m_bits: int, n_items: int, k: int) -> float:
    """Classical false-positive probability p = (1 - (1 - 1/m)**(k*n))**k.

    This is the standard independent-hashing analysis (Bloom 1970; survey
    form as in Broder–Mitzenmacher): after n insertions a given bit is still
    0 with probability (1 - 1/m)**(k*n), so a query on an absent item finds
    all k of its bits set with probability p. n_items may be 0 (p is 0.0).
    """
    _check_positive_int(m_bits, "m_bits")
    _check_positive_int(k, "k")
    if isinstance(n_items, bool) or not isinstance(n_items, int):
        raise BloomError(f"n_items must be an int, got {n_items!r}")
    if n_items < 0:
        raise BloomError(f"n_items must be >= 0, got {n_items}")
    if n_items == 0:
        return 0.0
    return (1.0 - (1.0 - 1.0 / m_bits) ** (k * n_items)) ** k


def optimal_k(m_bits: int, n_items: int) -> int:
    """The k minimising the false-positive rate: max(1, round((m/n)·ln 2)).

    (m/n)·ln 2 is the real-valued optimum; a filter needs an integer k >= 1,
    so the value is rounded half-to-even (Python round) and floored at 1.
    """
    _check_positive_int(m_bits, "m_bits")
    _check_positive_int(n_items, "n_items")
    return max(1, round((m_bits / n_items) * math.log(2)))
