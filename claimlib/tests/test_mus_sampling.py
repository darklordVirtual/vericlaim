# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the mus_sampling module (monetary-unit sampling)."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "mus_sampling"
_spec = importlib.util.spec_from_file_location(
    "claimlib_mus_sampling", _MOD_DIR / "mus_sampling.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_mus_sampling"] = _m
_spec.loader.exec_module(_m)

MUSError = _m.MUSError
interval = _m.interval
select = _m.select
project = _m.project


def test_interval_is_exact_fraction():
    assert interval(50_000_000, 100) == Fraction(500_000)
    assert interval(10, 3) == Fraction(10, 3)


def test_top_stratum_always_selected():
    pop = [50, 900, 30, 20]   # total 1000, n=2 -> interval 500; 900 >= 500
    for start in range(1, 501):
        assert 1 in select(pop, 2, start)


def test_selection_is_deterministic_and_ordered():
    pop = [100, 200, 300, 400]
    picked = select(pop, 2, 250)
    assert picked == sorted(picked)
    assert picked == select(pop, 2, 250)


def test_zero_items_never_selected():
    pop = [0, 500, 0, 500]
    for start in range(1, 501):
        picked = select(pop, 2, start)
        assert 0 not in picked and 2 not in picked


def test_projection_tainting_example():
    # $3,000 item overstated $300 (10%) with $5,000 interval -> $500.
    assert project([(300_000, 270_000)], Fraction(500_000)) == 50_000


def test_projection_top_stratum_uses_actual():
    assert project([(700_000, 600_000)], Fraction(500_000)) == 100_000


def test_projection_understatement_negative():
    assert project([(100_000, 120_000)], Fraction(500_000)) == -100_000


def test_projection_zero_misstatement():
    assert project([(400_000, 400_000)], Fraction(500_000)) == 0


def test_projection_matches_fraction_recompute():
    sampled = [(123, 100), (999, 998), (450_000, 449_999)]
    step = Fraction(500_000)
    want = sum(Fraction(b - a, b) * step if b < step else Fraction(b - a)
               for b, a in sampled)
    assert project(sampled, step) == round(want)


@pytest.mark.parametrize("call", [
    lambda: interval(0, 5),
    lambda: interval(100, 0),
    lambda: interval(5, 6),
    lambda: select([], 1, 1),
    lambda: select([100, -1], 1, 1),
    lambda: select([100], 1, 0),
    lambda: select([100], 1, 101),
    lambda: select([0, 0], 1, 1),
    lambda: project([(0, 10)], Fraction(100)),
    lambda: project([(100, -1)], Fraction(100)),
    lambda: project([(100, 90)], Fraction(0)),
    lambda: project("nope", Fraction(100)),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(MUSError):
        call()
