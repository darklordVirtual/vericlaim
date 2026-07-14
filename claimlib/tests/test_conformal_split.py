# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the conformal_split module."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "conformal_split"
_spec = importlib.util.spec_from_file_location(
    "claimlib_conformal_split", _MOD_DIR / "conformal_split.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_conformal_split"] = _m
_spec.loader.exec_module(_m)

ConformalError = _m.ConformalError
quantile_index = _m.quantile_index
conformal_quantile = _m.conformal_quantile
prediction_set = _m.prediction_set
loo_coverage = _m.loo_coverage


def test_quantile_index_published_examples():
    assert quantile_index(100, "0.1") == 91
    assert quantile_index(10, "0.1") == 10
    assert quantile_index(4, "0.1") is None   # ceil(5*0.9)=5 > 4
    assert quantile_index(1, "0.5") == 1      # ceil(2*0.5)=1


def test_quantile_uses_kth_smallest_no_interpolation():
    assert conformal_quantile([5, 1, 9, 3], "0.5") == 5   # k=ceil(5*.5)=3
    assert conformal_quantile([1], "0.5") == 1


def test_coverage_theorem_exact_on_distinct_pool():
    pool = [Fraction(i, 3) for i in range(1, 11)]  # 10 distinct scores
    for alpha in (Fraction(1, 10), Fraction(1, 4), Fraction(1, 2)):
        cov = loo_coverage(pool, alpha)
        assert 1 - alpha <= cov <= 1 - alpha + Fraction(1, len(pool))


def test_coverage_never_below_target_with_ties():
    pool = [1, 1, 1, 2, 2, 3]
    for alpha in (Fraction(1, 5), Fraction(1, 2)):
        assert loo_coverage(pool, alpha) >= 1 - alpha


def test_prediction_set_monotone_in_alpha():
    cal = list(range(1, 21))
    cands = {c: s for c, s in zip("abcdefghij", range(0, 30, 3))}
    small = prediction_set(cal, "0.05", cands)
    large_alpha = prediction_set(cal, "0.5", cands)
    assert large_alpha <= small


def test_vacuous_set_when_calibration_too_small():
    cands = {"a": 1, "b": 99}
    assert prediction_set([1, 2], "0.1", cands) == {"a", "b"}


@pytest.mark.parametrize("call", [
    lambda: quantile_index(0, "0.1"),
    lambda: quantile_index(10, "0"),
    lambda: quantile_index(10, "1"),
    lambda: quantile_index(10, -0.1),
    lambda: quantile_index(True, "0.1"),
    lambda: conformal_quantile([], "0.1"),
    lambda: conformal_quantile([1, "x"], "0.1"),
    lambda: conformal_quantile([1, float("inf")], "0.1"),
    lambda: prediction_set([1, 2, 3], "0.1", {}),
    lambda: loo_coverage([1], "0.1"),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(ConformalError):
        call()
