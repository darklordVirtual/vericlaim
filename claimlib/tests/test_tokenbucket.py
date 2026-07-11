# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable tokenbucket library (CLAIM-LIB-TOKENBUCKET-001).

Asserts correctness on concrete, hand-verified cases: burst behaviour, refill,
the capacity clamp, cost handling, and input validation / error handling.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str((HERE.parents[0] / "modules" / "tokenbucket")))

from tokenbucket import TokenBucket, TokenBucketError  # noqa: E402


def test_starts_full_and_bursts_to_capacity():
    # capacity 3 => exactly 3 immediate grants at t=0, 4th denied.
    b = TokenBucket(capacity=3, refill_per_sec=1)
    assert [b.allow(0.0) for _ in range(4)] == [True, True, True, False]


def test_refill_grants_after_elapsed_time():
    b = TokenBucket(capacity=2, refill_per_sec=1)
    assert b.allow(0.0) and b.allow(0.0)   # drain the 2 starting tokens
    assert b.allow(0.0) is False           # empty
    assert b.allow(1.0) is True            # 1s -> +1 token
    assert b.allow(1.0) is False           # empty again


def test_capacity_clamp_prevents_banking_idle_time():
    # After a long idle gap the level is clamped to capacity, not 100 tokens.
    b = TokenBucket(capacity=5, refill_per_sec=1)
    b.allow(0.0)  # 5 -> 4 (clock set at t=0)
    assert b.available(100.0) == 5.0            # min(5, 4 + 100) == 5, not 104
    # so only `capacity` grants are possible immediately after the gap:
    assert [b.allow(100.0) for _ in range(6)] == [True, True, True, True, True, False]


def test_available_does_not_consume():
    b = TokenBucket(capacity=2, refill_per_sec=1)
    assert b.available(0.0) == 2.0
    assert b.available(0.0) == 2.0   # idempotent, no consumption
    assert b.tokens == 2.0


def test_fractional_refill_rate():
    # 0.5 tokens/sec: empty bucket needs 2s to earn one token.
    b = TokenBucket(capacity=1, refill_per_sec=0.5)
    assert b.allow(0.0) is True     # 1 -> 0
    assert b.allow(1.0) is False    # +0.5 -> 0.5 < 1
    assert b.allow(2.0) is True     # +0.5 -> 1.0 >= 1


def test_cost_greater_than_one():
    b = TokenBucket(capacity=10, refill_per_sec=1)
    assert b.allow(0.0, cost=7) is True    # 10 -> 3
    assert b.allow(0.0, cost=7) is False   # 3 < 7, unchanged
    assert b.allow(0.0, cost=3) is True    # 3 -> 0
    # zero-cost requests are always allowed and consume nothing
    assert b.allow(0.0, cost=0) is True
    assert b.tokens == 0.0


def test_non_monotonic_time_raises():
    b = TokenBucket(capacity=2, refill_per_sec=1)
    b.allow(5.0)
    with pytest.raises(TokenBucketError):
        b.allow(4.0)   # time went backwards


def test_invalid_construction_raises():
    with pytest.raises(TokenBucketError):
        TokenBucket(capacity=0, refill_per_sec=1)      # capacity must be > 0
    with pytest.raises(TokenBucketError):
        TokenBucket(capacity=-1, refill_per_sec=1)
    with pytest.raises(TokenBucketError):
        TokenBucket(capacity=5, refill_per_sec=-1)     # negative refill
    with pytest.raises(TokenBucketError):
        TokenBucket(capacity=True, refill_per_sec=1)   # bool is not a valid number


def test_negative_cost_raises():
    b = TokenBucket(capacity=2, refill_per_sec=1)
    with pytest.raises(TokenBucketError):
        b.allow(0.0, cost=-1)
