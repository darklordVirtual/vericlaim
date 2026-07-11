# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable lru module (claimlib/modules/lru)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "lru"))

from lru import LRU, LRUError  # noqa: E402


def test_leetcode146_sequence():
    # Canonical LeetCode-146 example, capacity 2. Expected returns are the
    # published, independently-known answers.
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1        # hit
    c.put(3, 3)                 # evicts key 2
    assert c.get(2) is None     # 2 was evicted
    c.put(4, 4)                 # evicts key 1
    assert c.get(1) is None     # 1 was evicted
    assert c.get(3) == 3
    assert c.get(4) == 4
    assert sorted(c.keys()) == [3, 4]


def test_evicts_least_recently_used_not_least_recently_inserted():
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    c.get(1)                    # 1 is now MRU, 2 is LRU
    c.put(3, 3)                 # must evict 2, NOT 1
    assert 1 in c
    assert 2 not in c
    assert c.get(1) == 1


def test_update_existing_key_refreshes_and_does_not_evict():
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    c.put(1, 100)               # update -> 1 becomes MRU, value replaced
    assert len(c) == 2          # no eviction on update
    c.put(3, 3)                 # evicts LRU=2 (not the just-updated 1)
    assert c.get(1) == 100
    assert c.get(2) is None


def test_membership_does_not_change_recency():
    c = LRU(2)
    c.put(1, 1)
    c.put(2, 2)
    assert (1 in c) is True     # __contains__ must NOT refresh recency
    c.put(3, 3)                 # 1 still LRU -> evicted
    assert 1 not in c
    assert 2 in c


def test_size_never_exceeds_capacity():
    c = LRU(3)
    for k in range(100):
        c.put(k, k * 10)
        assert len(c) <= 3
    assert sorted(c.keys()) == [97, 98, 99]


def test_capacity_one():
    c = LRU(1)
    c.put(1, 1)
    c.put(2, 2)                 # evicts 1 immediately
    assert c.get(1) is None
    assert c.get(2) == 2
    assert len(c) == 1


def test_invalid_capacity_rejected():
    with pytest.raises(LRUError):
        LRU(0)
    with pytest.raises(LRUError):
        LRU(-1)
    with pytest.raises(LRUError):
        LRU(True)               # bool must not masquerade as capacity 1
    with pytest.raises(LRUError):
        LRU(2.0)                # float is not an int


def test_keys_ordered_lru_to_mru():
    c = LRU(3)
    c.put(1, 1)
    c.put(2, 2)
    c.put(3, 3)
    c.get(1)                    # 1 -> MRU
    assert c.keys() == [2, 3, 1]
