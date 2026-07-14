# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the conformal_risk module (CRC)."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "conformal_risk"
_spec = importlib.util.spec_from_file_location(
    "claimlib_conformal_risk", _MOD_DIR / "conformal_risk.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_conformal_risk"] = _m
_spec.loader.exec_module(_m)

CRCError = _m.CRCError
lambda_hat = _m.lambda_hat
controlled_risk_bound = _m.controlled_risk_bound
loo_risk = _m.loo_risk

GRID = {0: [1, 1, 1], 1: [0, 1, 0], 2: [0, 0, 0]}


def test_lambda_hat_hand_computed():
    assert lambda_hat(GRID, "0.5", 1) == 1
    assert lambda_hat(GRID, "0.25", 1) == 2
    assert lambda_hat(GRID, "0.2", 1) is None


def test_lambda_hat_picks_smallest_qualifying():
    grid = {0: [0, 0], 1: [0, 0]}
    assert lambda_hat(grid, "0.5", 1) == 0


def test_controlled_risk_bound_algebra():
    assert controlled_risk_bound(3, "0.5", 1) == Fraction(1, 3)
    assert controlled_risk_bound(9, "0.1", 1) == 0


def test_loo_risk_theorem_on_monotone_pool():
    pool = {lam: [1 if lam < (i % 4) else 0 for i in range(8)]
            for lam in range(5)}
    for alpha in (Fraction(1, 4), Fraction(1, 2)):
        assert loo_risk(pool, alpha, 1) <= alpha


def test_reduction_to_conformal_prediction():
    scores = [Fraction(i, 3) for i in range(1, 10)]
    lams = sorted(set(scores))
    grid = {lam: [1 if s > lam else 0 for s in scores] for lam in lams}
    alpha = Fraction(1, 3)
    n = len(scores)
    k = int(-((-(n + 1) * (1 - alpha)) // 1))
    assert lambda_hat(grid, alpha, 1) == sorted(scores)[k - 1]


def test_fractional_losses_supported():
    grid = {0: ["3/4", "1/2"], 1: ["1/4", "0"], 2: [0, 0]}
    assert lambda_hat(grid, "0.5", 1) == 1


@pytest.mark.parametrize("call", [
    lambda: lambda_hat({0: [0, 0], 1: [1, 1]}, "0.5", 1),   # rising loss
    lambda: lambda_hat({0: [2]}, "0.5", 1),                  # above B
    lambda: lambda_hat({0: [-1]}, "0.5", 1),                 # below 0
    lambda: lambda_hat({0: [1, 1], 1: [0]}, "0.5", 1),       # ragged
    lambda: lambda_hat({0: []}, "0.5", 1),
    lambda: lambda_hat({}, "0.5", 1),
    lambda: lambda_hat({0: [0]}, "0.5", 0),
    lambda: lambda_hat({0: [0]}, "0.5", -1),
    lambda: lambda_hat({0: [0]}, float("inf"), 1),
    lambda: controlled_risk_bound(True, "0.5", 1),
    lambda: loo_risk({0: [0]}, "0.5", 1),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(CRCError):
        call()
