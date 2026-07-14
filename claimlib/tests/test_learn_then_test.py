# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the learn_then_test module (LTT)."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "learn_then_test"
_spec = importlib.util.spec_from_file_location(
    "claimlib_learn_then_test", _MOD_DIR / "learn_then_test.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_learn_then_test"] = _m
_spec.loader.exec_module(_m)

LTTError = _m.LTTError
binom_tail_p = _m.binom_tail_p
ltt_bonferroni = _m.ltt_bonferroni
ltt_fixed_sequence = _m.ltt_fixed_sequence


def test_binomial_pvalue_exact_anchors():
    assert binom_tail_p(10, 0, "0.5") == Fraction(1, 1024)
    assert binom_tail_p(10, 10, "0.5") == 1
    assert binom_tail_p(2, 0, "0.1") == Fraction(81, 100)


def test_pvalue_monotone_in_failures():
    ps = [binom_tail_p(20, k, "0.3") for k in range(21)]
    assert all(a <= b for a, b in zip(ps, ps[1:]))
    assert ps[-1] == 1


def test_bonferroni_selects_only_strong_evidence():
    fails = {"good": 0, "bad": 15}
    got = ltt_bonferroni(fails, 50, "0.2", "0.05")
    assert got == {"good"}


def test_bonferroni_threshold_scales_with_grid_size():
    # One lambda at the edge: passes alone, fails inside a large grid.
    edge = {"e": 3}
    alone = ltt_bonferroni(edge, 50, "0.2", "0.05")
    padded = dict(edge, **{f"pad{i}": 50 for i in range(31)})
    crowded = ltt_bonferroni(padded, 50, "0.2", "0.05")
    assert "e" in alone and "e" not in crowded


def test_fixed_sequence_stops_at_first_failure():
    fails = {"a": 0, "block": 20, "b": 0}
    got = ltt_fixed_sequence(fails, ["a", "block", "b"], 40, "0.2", "0.05")
    assert got == {"a"}


def test_fixed_sequence_full_walk():
    fails = {"a": 0, "b": 1}
    got = ltt_fixed_sequence(fails, ["a", "b"], 40, "0.2", "0.05")
    assert got == {"a", "b"}


def test_empty_certification_is_honest():
    assert ltt_bonferroni({"x": 30}, 40, "0.2", "0.05") == set()
    assert ltt_fixed_sequence({"x": 30}, ["x"], 40, "0.2", "0.05") == set()


@pytest.mark.parametrize("call", [
    lambda: binom_tail_p(0, 0, "0.5"),
    lambda: binom_tail_p(5, 6, "0.5"),
    lambda: binom_tail_p(5, -1, "0.5"),
    lambda: binom_tail_p(5, 2.5, "0.5"),
    lambda: binom_tail_p(5, 2, "1"),
    lambda: binom_tail_p(5, 2, float("nan")),
    lambda: ltt_bonferroni({}, 5, "0.2", "0.1"),
    lambda: ltt_bonferroni({"a": 6}, 5, "0.2", "0.1"),
    lambda: ltt_bonferroni({"a": 1}, 5, "0.2", "0"),
    lambda: ltt_fixed_sequence({"a": 1}, [], 5, "0.2", "0.1"),
    lambda: ltt_fixed_sequence({"a": 1}, ["a", "a"], 5, "0.2", "0.1"),
    lambda: ltt_fixed_sequence({"a": 1}, ["b"], 5, "0.2", "0.1"),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(LTTError):
        call()
