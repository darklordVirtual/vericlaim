# SPDX-License-Identifier: Apache-2.0
"""Fixed-capacity LRU (least-recently-used) cache — a reusable, stdlib-only
building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it returns the right value for every lookup
and evicts exactly the least-recently-used key at capacity — is registered as
a claim and proven by a committed evidence artifact; vendoring this module
carries that claim (and its caveat) with it.

An LRU cache stores at most ``capacity`` key/value pairs. Reading a key with
``get`` and writing one with ``put`` both mark that key as most-recently-used;
inserting a new key when the cache is full first evicts the key that has gone
longest without use. Both operations are O(1), backed by ``collections.OrderedDict``.

Public API
----------
    LRU(capacity: int)                 # capacity must be a positive int
    get(key) -> value | None           # None if absent; marks key as MRU
    put(key, value) -> None            # inserts/updates; evicts LRU at capacity
    __len__() -> int                   # current number of stored entries
    __contains__(key) -> bool          # membership WITHOUT touching recency
    keys() -> list                     # keys in LRU-to-MRU order

    >>> c = LRU(2)
    >>> c.put(1, 1); c.put(2, 2)
    >>> c.get(1)
    1
    >>> c.put(3, 3)          # cache full -> evicts key 2 (least recently used)
    >>> c.get(2) is None
    True
    >>> c.keys()
    [3, 1]
"""
from __future__ import annotations

from collections import OrderedDict


class LRUError(ValueError):
    """The requested capacity is not a positive integer."""


class LRU:
    """A fixed-capacity least-recently-used cache."""

    def __init__(self, capacity: int) -> None:
        # bool is a subclass of int; reject it so LRU(True) can't mean LRU(1).
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise LRUError(f"capacity must be an int, got {type(capacity).__name__}")
        if capacity <= 0:
            raise LRUError(f"capacity must be positive, got {capacity}")
        self.capacity = capacity
        self._store: "OrderedDict[object, object]" = OrderedDict()

    def get(self, key):
        """Return the value for *key*, or ``None`` if absent.

        A hit moves *key* to the most-recently-used position. A miss leaves
        recency order untouched.
        """
        if key not in self._store:
            return None
        self._store.move_to_end(key)          # mark most-recently-used
        return self._store[key]

    def put(self, key, value) -> None:
        """Insert or update *key* -> *value*, marking it most-recently-used.

        Updating an existing key never evicts. Inserting a new key when the
        cache is already at capacity first evicts the least-recently-used key
        (the front of the order).
        """
        if key in self._store:
            self._store[key] = value
            self._store.move_to_end(key)      # update refreshes recency
            return
        if len(self._store) >= self.capacity:
            self._store.popitem(last=False)   # evict least-recently-used
        self._store[key] = value              # new keys go to the MRU end

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key) -> bool:
        # Membership test must NOT change recency (unlike get()).
        return key in self._store

    def keys(self) -> list:
        """Current keys in least-recently-used to most-recently-used order."""
        return list(self._store.keys())
