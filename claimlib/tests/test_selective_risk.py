# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the selective_risk module."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "selective_risk"
_spec = importlib.util.spec_from_file_location(
    "claimlib_selective_risk", _MOD_DIR / "selective_risk.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_selective_risk"] = _m
_spec.loader.exec_module(_m)

SelectiveError = _m.SelectiveError
coverage = _m.coverage
selective_risk = _m.selective_risk
risk_coverage_curve = _m.risk_coverage_curve

PAIRS = [("0.9", 0), ("0.8", 1), ("0.6", 0), ("0.4", 1)]


def test_coverage_and_risk_exact():
    assert coverage(PAIRS, "0.7") == Fraction(1, 2)
    assert selective_risk(PAIRS, "0.7") == Fraction(1, 2)
    assert coverage(PAIRS, "0.4") == 1
    assert selective_risk(PAIRS, "0.4") == Fraction(1, 2)


def test_threshold_boundary_inclusive():
    assert coverage(PAIRS, "0.8") == Fraction(1, 2)  # 0.8 accepted at 0.8


def test_full_coverage_point_is_plain_mean():
    curve = risk_coverage_curve(PAIRS)
    assert curve[-1]["coverage"] == 1
    assert curve[-1]["risk"] == Fraction(1, 2)


def test_curve_descending_thresholds_increasing_coverage():
    curve = risk_coverage_curve(PAIRS)
    assert [p["threshold"] for p in curve] == sorted(
        (p["threshold"] for p in curve), reverse=True)
    assert all(a["coverage"] <= b["coverage"]
               for a, b in zip(curve, curve[1:]))


def test_zero_coverage_risk_fails_closed():
    with pytest.raises(SelectiveError):
        selective_risk(PAIRS, "0.95")


def test_nonbinary_losses_accepted():
    pairs = [(1, Fraction(3, 2)), (0.5, "0.5")]
    assert selective_risk(pairs, 0) == 1


def test_permutation_invariance():
    assert risk_coverage_curve(PAIRS) == \
        risk_coverage_curve(list(reversed(PAIRS)))


@pytest.mark.parametrize("call", [
    lambda: coverage([], 0.5),
    lambda: coverage([(0.5, 0, 1)], 0.5),
    lambda: coverage([(0.5, -0.1)], 0.5),
    lambda: coverage([(float("inf"), 0)], 0.5),
    lambda: coverage([(0.5, 0)], float("nan")),
    lambda: coverage([(True, 0)], 0.5),
    lambda: selective_risk([(0.5, False)], 0.4),
    lambda: risk_coverage_curve("nope"),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(SelectiveError):
        call()
