# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the calibration_ece module."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "calibration_ece"
_spec = importlib.util.spec_from_file_location(
    "claimlib_calibration_ece", _MOD_DIR / "calibration_ece.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_calibration_ece"] = _m
_spec.loader.exec_module(_m)

CalibrationError = _m.CalibrationError
bins = _m.bins
ece = _m.ece
mce = _m.mce


def test_hand_computed_two_predictions():
    # conf 0.8 twice, one correct: acc 1/2, conf 4/5, gap 3/10.
    assert ece([("0.8", True), ("0.8", False)]) == Fraction(3, 10)
    assert mce([("0.8", True), ("0.8", False)]) == Fraction(3, 10)


def test_perfectly_calibrated_is_zero():
    pairs = ([(Fraction(3, 4), True)] * 3 + [(Fraction(3, 4), False)]
             + [(Fraction(1, 2), True)] * 2 + [(Fraction(1, 2), False)] * 2)
    assert ece(pairs) == 0


def test_totally_miscalibrated_is_one():
    assert ece([(1, False)] * 5) == 1
    assert ece([(0, True)] * 5) == 1


def test_binning_edges_right_closed():
    b = bins([(Fraction(1, 10), True), (Fraction(11, 100), True),
              (0, False), (1, True)], 10)
    assert b[0]["n"] == 2      # 0.0 and 0.1 both in bin 0
    assert b[1]["n"] == 1      # 0.11 in bin 1
    assert b[9]["n"] == 1      # 1.0 in the last bin
    assert sum(x["n"] for x in b) == 4


def test_weighted_across_bins():
    # bin(0.7]: 2 pairs gap 1/5... construct: conf 0.65 x2, one correct
    # (acc 1/2, conf 13/20, gap 3/20); conf 0.15 x2, both correct
    # (acc 1, conf 3/20, gap 17/20). ECE = 1/2*3/20 + 1/2*17/20 = 1/2.
    pairs = [(Fraction(13, 20), True), (Fraction(13, 20), False),
             (Fraction(3, 20), True), (Fraction(3, 20), True)]
    assert ece(pairs) == Fraction(1, 2)
    assert mce(pairs) == Fraction(17, 20)


def test_permutation_invariant_and_bounds():
    pairs = [(Fraction(i, 20), i % 3 == 0) for i in range(21)]
    assert ece(pairs) == ece(list(reversed(pairs)))
    assert 0 <= ece(pairs) <= mce(pairs) <= 1


def test_float_confidences_accepted():
    assert ece([(0.8, True), (0.8, False)]) == pytest.approx(0.3, abs=1e-9)


@pytest.mark.parametrize("call", [
    lambda: ece([]),
    lambda: ece([(0.5, True)], n_bins=0),
    lambda: ece([(0.5, True)], n_bins=True),
    lambda: ece([(1.0001, True)]),
    lambda: ece([(-0.1, True)]),
    lambda: ece([(float("inf"), True)]),
    lambda: ece([(0.5, "yes")]),
    lambda: ece([(0.5, 1)]),
    lambda: ece([(True, True)]),
    lambda: ece([(0.5,)]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(CalibrationError):
        call()
