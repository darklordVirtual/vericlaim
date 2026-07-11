# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``retry`` library (CLAIM-LIB-RETRY-001)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE_DIR = HERE.parents[1] / "claimlib" / "modules" / "retry"
if not MODULE_DIR.exists():
    MODULE_DIR = HERE.parent / "modules" / "retry"
sys.path.insert(0, str(MODULE_DIR))

from retry import (  # noqa: E402
    RetryError,
    backoff_ceiling,
    backoff_delay,
    jitter_fraction,
)


def test_ceiling_is_capped_exponential():
    # Reference: min(cap, base * 2**attempt), computed by hand.
    assert backoff_ceiling(0, 1.0, 60.0) == 1.0    # base*1
    assert backoff_ceiling(3, 1.0, 60.0) == 8.0    # base*8
    assert backoff_ceiling(6, 1.0, 60.0) == 60.0   # base*64 -> capped at 60
    assert backoff_ceiling(20, 1.0, 60.0) == 60.0  # far past the cap


def test_delay_always_within_bounds():
    # The core invariant across a range of attempts and seeds.
    for seed in (0, 1, 1337, 99999):
        for attempt in range(0, 20):
            ceiling = backoff_ceiling(attempt, 1.0, 60.0)
            delay = backoff_delay(attempt, 1.0, 60.0, seed)
            assert 0.0 <= delay <= ceiling


def test_jitter_fraction_in_unit_interval():
    for attempt in range(0, 50):
        frac = jitter_fraction("seed", attempt)
        assert 0.0 <= frac < 1.0


def test_deterministic_same_seed_same_delay():
    a = backoff_delay(5, 1.0, 60.0, 1337)
    b = backoff_delay(5, 1.0, 60.0, 1337)
    assert a == b


def test_different_seeds_decorrelate():
    # Different seeds should (overwhelmingly) give different delays; check the
    # jitter fraction differs so we are not accidentally returning a constant.
    f1 = jitter_fraction(1, 7)
    f2 = jitter_fraction(2, 7)
    assert f1 != f2


def test_jitter_varies_with_attempt():
    # Same seed, different attempt -> different fraction (not a fixed constant).
    assert jitter_fraction(1337, 0) != jitter_fraction(1337, 1)


def test_does_not_use_random_module_state():
    # Determinism must not depend on the global RNG: seeding random differently
    # between two identical calls must not change the result.
    import random
    random.seed(1)
    first = backoff_delay(4, 1.0, 60.0, 42)
    random.seed(2)
    second = backoff_delay(4, 1.0, 60.0, 42)
    assert first == second


def test_full_jitter_can_approach_ceiling():
    # Over many attempts at least one draw should exceed half the ceiling,
    # confirming the jitter spans the window rather than hugging zero.
    hits = 0
    for attempt in range(0, 30):
        ceiling = backoff_ceiling(attempt, 1.0, 1e9)  # large cap: ceiling grows
        if backoff_delay(attempt, 1.0, 1e9, 2024) > 0.5 * ceiling:
            hits += 1
    assert hits > 0


def test_invalid_parameters_raise():
    with pytest.raises(RetryError):
        backoff_ceiling(-1, 1.0, 60.0)
    with pytest.raises(RetryError):
        backoff_ceiling(0, 0.0, 60.0)      # base must be > 0
    with pytest.raises(RetryError):
        backoff_ceiling(0, 1.0, 0.0)       # cap must be > 0
    with pytest.raises(RetryError):
        backoff_delay(-5, 1.0, 60.0, 1)
    with pytest.raises(RetryError):
        jitter_fraction("s", -1)


def test_bool_attempt_rejected():
    # bool is a subclass of int; reject it to avoid True/False sneaking in.
    with pytest.raises(RetryError):
        backoff_ceiling(True, 1.0, 60.0)
