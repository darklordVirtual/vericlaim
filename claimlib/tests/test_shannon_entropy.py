# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the shannon_entropy module."""
from __future__ import annotations

import importlib.util
import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "shannon_entropy"
_spec = importlib.util.spec_from_file_location(
    "claimlib_shannon_entropy", _MOD_DIR / "shannon_entropy.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_shannon_entropy"] = _m
_spec.loader.exec_module(_m)

EntropyError = _m.EntropyError
entropy = _m.entropy
cross_entropy = _m.cross_entropy
kl_divergence = _m.kl_divergence
perplexity = _m.perplexity


def test_exact_anchor_values():
    assert entropy(["1/2", "1/2"]) == 1.0
    assert entropy([Fraction(1, 4)] * 4) == 2.0
    assert entropy([1]) == 0.0
    assert entropy([0, 0, 1]) == 0.0
    assert entropy(["1/2", "1/4", "1/4"]) == 1.5   # Shannon's worked example


def test_perplexity_of_uniform_is_n():
    assert perplexity([Fraction(1, 8)] * 8) == 8.0
    assert perplexity([1]) == 1.0


def test_uniform_maximizes_entropy():
    skewed = entropy(["7/10", "1/10", "1/10", "1/10"])
    assert skewed < entropy([Fraction(1, 4)] * 4) <= math.log2(4) + 1e-12


def test_gibbs_inequality_and_chain_identity():
    p = ["1/2", "1/3", "1/6"]
    q = ["1/3", "1/3", "1/3"]
    kl = kl_divergence(p, q)
    assert kl >= 0
    assert abs(cross_entropy(p, q) - (entropy(p) + kl)) < 1e-12
    assert kl_divergence(p, p) < 1e-12


def test_cross_entropy_asymmetric():
    p = ["9/10", "1/10"]
    q = ["1/2", "1/2"]
    assert kl_divergence(p, q) != kl_divergence(q, p)


def test_floats_read_at_printed_decimal_value():
    # Floats convert via str(): 0.1 is read as exactly 1/10, so ten of them
    # sum to exactly 1 — the friendly interpretation, documented here.
    assert entropy([0.1] * 10) == pytest.approx(math.log2(10), abs=1e-12)
    assert entropy(["1/10"] * 10) == pytest.approx(math.log2(10), abs=1e-12)
    # ...but a genuinely deficient distribution still fails closed.
    with pytest.raises(EntropyError):
        entropy([0.3, 0.3, 0.3])


@pytest.mark.parametrize("call", [
    lambda: entropy([]),
    lambda: entropy(["1/2", "1/3"]),
    lambda: entropy(["3/2", "-1/2"]),
    lambda: entropy([float("inf")]),
    lambda: entropy([True]),
    lambda: cross_entropy(["1/2", "1/2"], ["1/3", "1/3", "1/3"]),
    lambda: cross_entropy(["1/2", "1/2"], [1, 0]),
    lambda: kl_divergence(["1/2", "1/2"], [0, 1]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(EntropyError):
        call()
