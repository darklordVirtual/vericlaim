# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``errorbudget`` library.

Reference values are computed by hand from the SRE error-budget formulas, not
taken from the code under test.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODULE_DIR = HERE.parents[1] / "claimlib" / "modules" / "errorbudget"
if not MODULE_DIR.exists():
    # tests/ lives inside claimlib/, so modules/ is a sibling.
    MODULE_DIR = HERE.parent / "modules" / "errorbudget"
sys.path.insert(0, str(MODULE_DIR))

from errorbudget import (  # noqa: E402
    ErrorBudgetError,
    availability,
    budget_minutes,
    error_budget_remaining_pct,
)


def test_availability_half_budget():
    # (43200-21.6)/43200*100 = 99.95
    assert availability(43200, 21.6) == 99.95


def test_availability_perfect():
    assert availability(43200, 0) == 100.0


def test_availability_rounds_to_4dp():
    # (43200-10)/43200*100 = 99.976851851... -> 99.9769
    assert availability(43200, 10) == 99.9769


def test_budget_minutes_three_nines_month():
    # 43200 * (1 - 99.9/100) = 43.2 (float noise absorbed by 6-dp rounding)
    assert budget_minutes(99.9, 43200) == 43.2


def test_budget_minutes_four_nines_year():
    # 525600 * 0.0001 = 52.56
    assert budget_minutes(99.99, 525600) == 52.56


def test_budget_minutes_100_is_zero():
    # A 100% SLO permits zero downtime.
    assert budget_minutes(100, 43200) == 0.0


def test_remaining_half_spent():
    # budget 43.2, downtime 21.6 -> (43.2-21.6)/43.2*100 = 50
    assert error_budget_remaining_pct(99.9, 43200, 21.6) == 50.0


def test_remaining_exhausted():
    # downtime equals budget -> 0
    assert error_budget_remaining_pct(99.0, 43200, 432.0) == 0.0


def test_remaining_overspent_is_negative():
    # budget 216, downtime 324 -> (216-324)/216*100 = -50
    assert error_budget_remaining_pct(99.5, 43200, 324.0) == -50.0


def test_remaining_full_with_no_downtime():
    assert error_budget_remaining_pct(99.9, 43200, 0) == 100.0


def test_remaining_rejects_slo_100():
    # Zero budget -> division undefined -> must raise, not divide by zero.
    with pytest.raises(ErrorBudgetError):
        error_budget_remaining_pct(100, 43200, 0)


def test_rejects_nonpositive_window():
    with pytest.raises(ErrorBudgetError):
        availability(0, 0)
    with pytest.raises(ErrorBudgetError):
        budget_minutes(99.9, -1)


def test_rejects_negative_downtime():
    with pytest.raises(ErrorBudgetError):
        availability(1440, -5)


def test_rejects_downtime_exceeding_window():
    with pytest.raises(ErrorBudgetError):
        availability(1440, 1441)


def test_rejects_slo_out_of_range():
    with pytest.raises(ErrorBudgetError):
        budget_minutes(101, 1440)
    with pytest.raises(ErrorBudgetError):
        budget_minutes(-0.1, 1440)


def test_rejects_bool_inputs():
    # bool is a subclass of int; must not be accepted as a numeric arg.
    with pytest.raises(ErrorBudgetError):
        availability(True, 0)
