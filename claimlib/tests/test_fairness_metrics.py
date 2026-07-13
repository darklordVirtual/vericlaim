# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the fairness_metrics module."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "fairness_metrics"
_spec = importlib.util.spec_from_file_location(
    "claimlib_fairness_metrics", _MOD_DIR / "fairness_metrics.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_fairness_metrics"] = _m
_spec.loader.exec_module(_m)

FairnessError = _m.FairnessError
GroupCounts = _m.GroupCounts
selection_rate = _m.selection_rate
tpr = _m.tpr
fpr = _m.fpr
demographic_parity_difference = _m.demographic_parity_difference
disparate_impact_ratio = _m.disparate_impact_ratio
four_fifths_ok = _m.four_fifths_ok
equalized_odds_difference = _m.equalized_odds_difference

A = GroupCounts(tp=40, fp=10, fn=10, tn=40)   # rate 1/2
B = GroupCounts(tp=20, fp=5, fn=30, tn=45)    # rate 1/4


def test_rates_are_exact_fractions():
    assert selection_rate(A) == Fraction(1, 2)
    assert tpr(A) == Fraction(4, 5)
    assert fpr(B) == Fraction(1, 10)
    assert isinstance(selection_rate(A), Fraction)


def test_demographic_parity_and_disparate_impact():
    groups = {"a": A, "b": B}
    assert demographic_parity_difference(groups) == Fraction(1, 4)
    assert disparate_impact_ratio(groups) == Fraction(1, 2)
    assert not four_fifths_ok(groups)


def test_four_fifths_boundary_passes_at_exactly_0_8():
    groups = {"x": GroupCounts(4, 0, 1, 5),   # rate 2/5
              "y": GroupCounts(5, 0, 0, 5)}   # rate 1/2 -> ratio 4/5
    assert disparate_impact_ratio(groups) == Fraction(4, 5)
    assert four_fifths_ok(groups)


def test_equalized_odds_zero_iff_equal_rates():
    same = {"a": A, "b": A}
    assert equalized_odds_difference(same) == 0
    assert equalized_odds_difference({"a": A, "b": B}) == Fraction(2, 5)


def test_perfect_classifier_satisfies_equalized_odds():
    groups = {"x": GroupCounts(9, 0, 0, 1), "y": GroupCounts(1, 0, 0, 9)}
    assert equalized_odds_difference(groups) == 0


def test_metrics_invariant_under_relabeling():
    g = {"a": A, "b": B}
    h = {"b": B, "a": A}
    assert demographic_parity_difference(g) == demographic_parity_difference(h)
    assert disparate_impact_ratio(g) == disparate_impact_ratio(h)


def test_three_groups_use_extremes():
    mid = GroupCounts(tp=30, fp=10, fn=20, tn=40)   # rate 2/5
    groups = {"a": A, "b": B, "c": mid}
    assert demographic_parity_difference(groups) == Fraction(1, 4)


@pytest.mark.parametrize("call", [
    lambda: GroupCounts(-1, 0, 0, 1),
    lambda: GroupCounts(1.5, 0, 0, 1),
    lambda: GroupCounts(True, 0, 0, 1),
    lambda: GroupCounts(0, 0, 0, 0),
    lambda: demographic_parity_difference({"only": A}),
    lambda: demographic_parity_difference({"a": A, "b": "not-counts"}),
    lambda: tpr(GroupCounts(0, 1, 0, 1)),
    lambda: fpr(GroupCounts(1, 0, 1, 0)),
    lambda: disparate_impact_ratio({"x": GroupCounts(0, 0, 1, 1),
                                    "y": GroupCounts(0, 0, 1, 1)}),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(FairnessError):
        call()
