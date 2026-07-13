# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the slo_burnrate module (SRE Workbook ch. 5 arithmetic)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "slo_burnrate"
_spec = importlib.util.spec_from_file_location(
    "claimlib_slo_burnrate", _MOD_DIR / "slo_burnrate.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_slo_burnrate"] = _m
_spec.loader.exec_module(_m)

BurnRateError = _m.BurnRateError
burn_rate = _m.burn_rate
budget_consumed = _m.budget_consumed
error_rate = _m.error_rate
burn_rate_from_error_ratio = _m.burn_rate_from_error_ratio
budget_remaining = _m.budget_remaining
time_to_exhaustion = _m.time_to_exhaustion
short_window = _m.short_window
multiwindow_alert = _m.multiwindow_alert
GOOGLE_30D_POLICY = _m.GOOGLE_30D_POLICY

PERIOD_H = 720.0  # 30 days in hours


@pytest.mark.parametrize("frac,window_h,expected", [
    (0.02, 1.0, 14.4),
    (0.05, 6.0, 6.0),
    (0.10, 72.0, 1.0),
    (1.0, 720.0, 1.0),
])
def test_workbook_burn_rates(frac, window_h, expected):
    assert burn_rate(frac, window_h, PERIOD_H) == expected


def test_burn_rate_budget_consumed_are_inverse():
    for frac, w in [(0.02, 1.0), (0.05, 6.0), (0.1, 72.0)]:
        rate = burn_rate(frac, w, PERIOD_H)
        assert budget_consumed(rate, w, PERIOD_H) == pytest.approx(frac)


def test_error_rate_and_inverse():
    assert error_rate(10.0, 99.9) == 0.01
    assert burn_rate_from_error_ratio(0.01, 99.9) == 10.0
    assert error_rate(1.0, 100.0) == 0.0


def test_budget_remaining_and_exhaustion():
    assert budget_remaining(2.0, 360.0, PERIOD_H) == 0.0
    assert budget_remaining(0.0, 720.0, PERIOD_H) == 1.0
    assert time_to_exhaustion(1.0, PERIOD_H) == 720.0
    assert time_to_exhaustion(1000.0, PERIOD_H) == 0.72


def test_short_window_guideline():
    assert short_window(60.0) == 5.0
    assert short_window(360.0) == 30.0
    assert short_window(4320.0) == 360.0


def test_multiwindow_needs_both_windows():
    assert multiwindow_alert(0.02, 0.02, 14.4, 99.9)
    assert not multiwindow_alert(0.02, 0.001, 14.4, 99.9)
    assert not multiwindow_alert(0.001, 0.02, 14.4, 99.9)


def test_policy_is_self_consistent():
    for tier in GOOGLE_30D_POLICY:
        assert burn_rate(tier["budget_consumed"],
                         tier["long_window_minutes"], 720.0 * 60) == \
            tier["burn_rate"]
        assert short_window(tier["long_window_minutes"]) == \
            tier["short_window_minutes"]


@pytest.mark.parametrize("call", [
    lambda: burn_rate(-0.1, 1.0, PERIOD_H),
    lambda: burn_rate(1.1, 1.0, PERIOD_H),
    lambda: burn_rate(0.02, 0.0, PERIOD_H),
    lambda: burn_rate(0.02, 721.0, PERIOD_H),
    lambda: burn_rate_from_error_ratio(0.01, 100.0),
    lambda: time_to_exhaustion(0.0, PERIOD_H),
    lambda: budget_remaining(1.0, 800.0, PERIOD_H),
    lambda: error_rate(-1.0, 99.9),
    lambda: burn_rate(float("nan"), 1.0, PERIOD_H),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(BurnRateError):
        call()
