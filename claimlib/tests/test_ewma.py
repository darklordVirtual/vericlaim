# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``ewma`` library.

Reference values are independently known: the NIST/SEMATECH e-Handbook
section 6.3.2.4 worked example (lambda = 0.3, target 50, s = 2.0539, L = 3;
EWMA values 50.60, 49.52, 50.56, ...; steady-state UCL 52.5884 /
LCL 47.4115), exact rational arithmetic via fractions.Fraction, and the
algebraic identity that the limit factor at i = 1 is exactly lambda^2.
"""
import math
import sys
from fractions import Fraction
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "ewma"))

from ewma import (  # noqa: E402
    EWMAError,
    chart,
    control_limits,
    ewma_series,
    ewma_update,
    steady_state_limits,
)

NIST_DATA = [52.0, 47.0, 53.0, 49.3, 50.1, 47.0, 51.0, 50.1, 51.2, 50.5,
             49.6, 47.6, 49.9, 51.3, 47.8, 51.2, 52.6, 52.4, 53.6, 52.1]


def test_update_hand_computed():
    # 0.3*52 + 0.7*50 = 50.6 (NIST worked example, first step)
    assert ewma_update(50.0, 52.0, 0.3) == pytest.approx(50.6, abs=1e-12)
    # lambda = 1 reproduces the observation
    assert ewma_update(123.0, 10.0, 1.0) == 10.0


def test_series_matches_nist_first_values():
    zs = ewma_series(NIST_DATA[:3], 0.3, 50.0)
    assert [round(z, 2) for z in zs] == [50.60, 49.52, 50.56]


def test_series_matches_all_nist_values():
    published = [50.60, 49.52, 50.56, 50.18, 50.16, 49.21, 49.75, 49.85,
                 50.26, 50.33, 50.11, 49.36, 49.52, 50.05, 49.38, 49.92,
                 50.73, 51.23, 51.94, 51.99]
    zs = ewma_series(NIST_DATA, 0.3, 50.0)
    assert [round(z, 2) for z in zs] == published


def test_series_lambda_one_is_identity():
    data = [3.0, 1.0, 4.0, 1.0, 5.0]
    assert ewma_series(data, 1.0, 99.0) == data


def test_series_constant_input_is_fixed_point():
    assert ewma_series([5.0] * 10, 0.3, 5.0) == [5.0] * 10


def test_series_excludes_seed_and_has_input_length():
    zs = ewma_series([1.0, 2.0], 0.5, 10.0)
    assert len(zs) == 2
    assert zs[0] == pytest.approx(5.5)   # 0.5*1 + 0.5*10, not the seed


def test_series_matches_fraction_oracle():
    # Independent exact-arithmetic recomputation (data disjoint from evidence).
    values = ["4.2", "-1.5", "0.0", "3.3", "7.7", "-2.2", "5.5"]
    lam, z0 = "0.35", "1.1"
    z = Fraction(z0)
    exact = []
    for v in values:
        z = Fraction(lam) * Fraction(v) + (1 - Fraction(lam)) * z
        exact.append(z)
    got = ewma_series([float(v) for v in values], 0.35, 1.1)
    for g, w in zip(got, exact):
        assert abs(Fraction(g) - w) <= Fraction(1, 10 ** 12)


def test_limit_factor_at_i1_is_exactly_lambda():
    # 1-(1-lam)^2 = lam(2-lam), so the factor is lam^2 and half-width
    # collapses to L*sigma*lam.
    for lam in (0.05, 0.2, 0.3, 0.5, 1.0):
        lcl, ucl = control_limits(0.0, 1.0, lam, 1, 3.0)
        assert ucl == pytest.approx(3.0 * lam, rel=1e-12)
        assert lcl == pytest.approx(-3.0 * lam, rel=1e-12)


def test_limits_monotone_and_approach_steady_state():
    prev = 0.0
    for i in range(1, 201):
        _, ucl = control_limits(50.0, 2.0, 0.3, i)
        # Widening limits: strictly at first, then monotone non-decreasing once
        # (1-lam)^(2i) saturates to 0 in float and the limits sit at steady state.
        assert ucl > prev if i <= 10 else ucl >= prev
        prev = ucl
    _, steady_ucl = steady_state_limits(50.0, 2.0, 0.3)
    assert prev == pytest.approx(steady_ucl, rel=1e-12)
    assert control_limits(50.0, 2.0, 0.3, 1)[1] < steady_ucl


def test_steady_state_limits_match_nist():
    lcl, ucl = steady_state_limits(50.0, 2.0539, 0.3, 3.0)
    assert ucl == pytest.approx(52.5884, abs=1e-3)
    assert lcl == pytest.approx(47.4115, abs=1e-3)


def test_chart_nist_data_all_in_control():
    result = chart(NIST_DATA, 50.0, 2.0539, 0.3, 3.0, exact_limits=False)
    assert result["out_of_control"] == []
    assert result["n"] == 20
    assert all(p["in_control"] for p in result["points"])


def test_chart_flags_shifted_process():
    # In-control noise around 50, then a large sustained upward shift.
    data = [50.1, 49.9, 50.0, 50.2, 49.8, 60.0, 60.0, 60.0]
    result = chart(data, 50.0, 1.0, 0.3, 3.0)
    assert result["out_of_control"] != []
    assert min(result["out_of_control"]) >= 6  # only after the shift
    flagged = [p["i"] for p in result["points"] if not p["in_control"]]
    assert flagged == result["out_of_control"]


def test_chart_exact_limits_tighter_than_steady_state_early():
    exact = chart([50.0], 50.0, 2.0, 0.3)["points"][0]
    steady = chart([50.0], 50.0, 2.0, 0.3, exact_limits=False)["points"][0]
    assert exact["ucl"] < steady["ucl"]
    assert exact["lcl"] > steady["lcl"]


def test_symmetry_of_limits():
    lcl, ucl = control_limits(10.0, 1.5, 0.2, 7, 2.5)
    assert ucl - 10.0 == pytest.approx(10.0 - lcl, rel=1e-12)


def test_rejects_bad_lambda():
    for lam in (0.0, -0.1, 1.0001, 2, float("nan"), "0.3", None, True):
        with pytest.raises(EWMAError):
            ewma_series([1.0, 2.0], lam, 0.0)


def test_rejects_bad_sigma_and_L():
    with pytest.raises(EWMAError):
        control_limits(0.0, 0.0, 0.3, 1)
    with pytest.raises(EWMAError):
        control_limits(0.0, -1.0, 0.3, 1)
    with pytest.raises(EWMAError):
        steady_state_limits(0.0, 1.0, 0.3, L=0.0)
    with pytest.raises(EWMAError):
        chart([1.0], 0.0, 1.0, 0.3, L=-3.0)


def test_rejects_bad_index():
    for i in (0, -1, 1.5, True):
        with pytest.raises(EWMAError):
            control_limits(0.0, 1.0, 0.3, i)


def test_rejects_empty_and_non_finite_values():
    with pytest.raises(EWMAError):
        ewma_series([], 0.3, 0.0)
    with pytest.raises(EWMAError):
        ewma_series([1.0, float("nan")], 0.3, 0.0)
    with pytest.raises(EWMAError):
        ewma_series([1.0, float("inf")], 0.3, 0.0)
    with pytest.raises(EWMAError):
        ewma_series([1.0, "2.0"], 0.3, 0.0)
    with pytest.raises(EWMAError):
        ewma_update(float("nan"), 1.0, 0.3)
    with pytest.raises(EWMAError):
        ewma_series([1.0], 0.3, float("inf"))


def test_update_equals_series_step():
    z1 = ewma_update(50.0, 52.0, 0.3)
    z2 = ewma_update(z1, 47.0, 0.3)
    assert ewma_series([52.0, 47.0], 0.3, 50.0) == [z1, z2]
