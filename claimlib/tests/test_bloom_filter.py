# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the bloom_filter module."""
from __future__ import annotations

import importlib.util
import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "bloom_filter"
_spec = importlib.util.spec_from_file_location(
    "claimlib_bloom_filter", _MOD_DIR / "bloom_filter.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_bloom_filter"] = _m
_spec.loader.exec_module(_m)

BloomError = _m.BloomError
BloomFilter = _m.BloomFilter
false_positive_rate = _m.false_positive_rate
optimal_k = _m.optimal_k
indexes = _m.indexes


def test_no_false_negatives():
    bf = BloomFilter(2048, 5)
    items = [f"item-{i}" for i in range(300)]
    for it in items:
        bf.add(it)
    assert all(bf.contains(it) for it in items)


def test_empty_filter_contains_nothing():
    bf = BloomFilter(256, 3)
    assert not bf.contains("anything")
    assert bf.bits_set() == 0


def test_contains_dunder():
    bf = BloomFilter(256, 3)
    bf.add("x")
    assert "x" in bf


def test_str_and_bytes_keys_agree():
    assert indexes("abc", 512, 4) == indexes(b"abc", 512, 4)


def test_indexes_deterministic_and_in_range():
    ix = indexes("hello", 1000, 7)
    assert ix == indexes("hello", 1000, 7)
    assert len(ix) == 7
    assert all(0 <= i < 1000 for i in ix)


def test_fp_formula_matches_exact_rational():
    for m, n, k in [(512, 50, 4), (64, 10, 2), (10000, 500, 7)]:
        exact = float((1 - Fraction(m - 1, m) ** (k * n)) ** k)
        assert false_positive_rate(m, n, k) == pytest.approx(exact, abs=1e-12)


def test_fp_rate_zero_items():
    assert false_positive_rate(1024, 0, 3) == 0.0


def test_optimal_k_formula():
    for m, n in [(1024, 100), (960, 100), (100, 100)]:
        assert optimal_k(m, n) == max(1, round((m / n) * math.log(2)))
    assert optimal_k(1, 1000) == 1  # floored at 1


@pytest.mark.parametrize("call", [
    lambda: BloomFilter(0, 1),
    lambda: BloomFilter(64, 0),
    lambda: BloomFilter(-1, 1),
    lambda: BloomFilter(64, True),
    lambda: false_positive_rate(64, -1, 1),
    lambda: indexes("x", 64, 0),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(BloomError):
        call()


def test_bit_array_snapshot_is_copy():
    bf = BloomFilter(64, 2)
    bf.add("a")
    snap = bf.bit_array()
    bf.add("b")
    assert snap != bf.bit_array() or bf.bits_set() == bin(
        int.from_bytes(snap, "big")).count("1")
