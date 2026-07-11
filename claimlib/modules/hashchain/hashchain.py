# SPDX-License-Identifier: Apache-2.0
"""Tamper-evident append-only hash chain — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. Each record commits
to the entire history before it, exactly like a Git commit or a block in a
blockchain: the record's hash folds in the previous record's hash, so changing,
inserting, deleting or reordering *any* past entry changes the head and every
hash after it. The property that makes it trustworthy — that it detects every
single-entry mutation over a reference battery — is registered as a claim and
proven by a committed evidence artifact; vendoring this module carries that claim
(and its caveat) with it.

The construction
----------------
    record_hash(prev, entry) = SHA-256( prev_digest || entry_bytes )

with a fixed 32-byte zero *genesis* prev-hash for the first record. The chain of
per-record head digests is the authenticator: to verify, recompute the chain from
the claimed entries and compare digest-for-digest.

Public API
----------
    GENESIS                                    # 32-byte genesis prev-hash
    record_hash(prev: bytes, entry: bytes) -> bytes
    class HashChain:
        append(entry: bytes) -> str            # returns new head as hex
        head -> str                            # current head digest, hex
        hashes -> list[str]                    # per-record head digests, hex
        __len__() -> int
    build_chain(entries) -> list[str]          # hex head digest per entry
    verify(entries, chain) -> bool             # recompute and compare

    >>> c = HashChain()
    >>> _ = c.append(b"alpha"); head1 = c.append(b"beta")
    >>> verify([b"alpha", b"beta"], c.hashes)
    True
    >>> verify([b"alpha", b"BETA"], c.hashes)   # one entry changed
    False

No third-party imports, no I/O, no global mutable state. Security note: this
detects *accidental or unauthenticated* tampering. For an adversary who can also
rewrite the stored chain, wrap it in an HMAC or sign the head — see the caveat.
"""
from __future__ import annotations

import hashlib
from typing import Iterable, List, Sequence

# The prev-hash mixed into the very first record. A fixed 32-byte zero string,
# i.e. the SHA-256 digest size, so record_hash sees a uniform prev-hash width
# for every record including the first.
GENESIS: bytes = b"\x00" * 32


def _as_bytes(entry: object) -> bytes:
    """Coerce an entry to immutable bytes, or raise TypeError.

    Only bytes-like inputs are accepted. Refusing str is deliberate: text would
    need an encoding choice, and a silent default is how two honest parties end
    up computing different chains for "the same" data.
    """
    if isinstance(entry, bytes):
        return entry
    if isinstance(entry, bytearray):
        return bytes(entry)
    raise TypeError(
        f"entry must be bytes or bytearray, got {type(entry).__name__}")


def record_hash(prev: bytes, entry: bytes) -> bytes:
    """Return SHA-256(prev || entry) as raw digest bytes.

    *prev* is the previous record's digest (use :data:`GENESIS` for the first).
    *entry* is the record payload. Both must be bytes-like.
    """
    prev = _as_bytes(prev)
    entry = _as_bytes(entry)
    return hashlib.sha256(prev + entry).digest()


class HashChain:
    """An append-only, tamper-evident chain of records.

    Records are added with :meth:`append`; the current :attr:`head` is a digest
    that commits to the entire ordered history. The chain keeps no copy of the
    entries themselves — only the running head and the per-record digests — so it
    is cheap to hold and safe to publish.
    """

    def __init__(self) -> None:
        self._head: bytes = GENESIS
        self._hashes: List[bytes] = []

    def append(self, entry: bytes) -> str:
        """Append *entry*; return the new head digest as a 64-char hex string."""
        digest = record_hash(self._head, _as_bytes(entry))
        self._head = digest
        self._hashes.append(digest)
        return digest.hex()

    @property
    def head(self) -> str:
        """Current head digest as hex. Equals ``GENESIS.hex()`` when empty."""
        return self._head.hex()

    @property
    def head_bytes(self) -> bytes:
        """Current head digest as raw bytes."""
        return self._head

    @property
    def hashes(self) -> List[str]:
        """The per-record head digests, in order, as hex strings."""
        return [h.hex() for h in self._hashes]

    def __len__(self) -> int:
        return len(self._hashes)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"HashChain(len={len(self._hashes)}, head={self.head[:12]}...)"


def build_chain(entries: Iterable[bytes]) -> List[str]:
    """Build a chain over *entries*; return the list of per-record hex digests."""
    chain = HashChain()
    return [chain.append(e) for e in entries]


def verify(entries: Sequence[bytes], chain: Sequence[str]) -> bool:
    """Return True iff *chain* is exactly the hash chain of *entries*.

    Recomputes the chain from *entries* and compares digest-for-digest against
    the claimed *chain* (a sequence of hex head digests). Returns False on any
    difference — a changed, inserted, deleted or reordered entry, a length
    mismatch, or a malformed hex digest. Fails closed: anything it cannot line
    up cleanly is treated as tampering.
    """
    if len(entries) != len(chain):
        return False
    prev = GENESIS
    for entry, claimed in zip(entries, chain):
        try:
            digest = record_hash(prev, entry)
        except TypeError:
            return False
        if not isinstance(claimed, str) or digest.hex() != claimed:
            return False
        prev = digest
    return True
