# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the dp_composition module."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "dp_composition"
_spec = importlib.util.spec_from_file_location(
    "claimlib_dp_composition", _MOD_DIR / "dp_composition.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_dp_composition"] = _m
_spec.loader.exec_module(_m)

DPError = _m.DPError
Mechanism = _m.Mechanism
Ledger = _m.Ledger
sequential = _m.sequential
parallel = _m.parallel
group_privacy = _m.group_privacy


def test_sequential_is_additive_and_exact():
    ms = [Mechanism("a", "0.5"), Mechanism("b", "0.25"),
          Mechanism("c", "0.125", "0.001")]
    assert sequential(ms) == (Fraction(7, 8), Fraction(1, 1000))


def test_parallel_is_max_and_never_exceeds_sequential():
    ms = [Mechanism("a", "0.5", "0.002"), Mechanism("b", "0.25", "0.003")]
    par, seq = parallel(ms), sequential(ms)
    assert par == (Fraction(1, 2), Fraction(3, 1000))
    assert par[0] <= seq[0] and par[1] <= seq[1]


def test_group_privacy_scales_linearly():
    assert group_privacy("0.1", 1) == Fraction(1, 10)
    assert group_privacy("0.1", 10) == 1
    assert group_privacy(Fraction(1, 3), 3) == 1


def test_ledger_spends_to_exact_exhaustion():
    ledger = Ledger("1"); ledger.spend(Mechanism("a", "0.75"))
    ledger.spend(Mechanism("b", "0.25"))
    assert ledger.remaining() == (Fraction(0), Fraction(0))


def test_ledger_refuses_tiny_overspend_without_recording():
    ledger = Ledger("1")
    ledger.spend(Mechanism("a", "1"))
    with pytest.raises(DPError):
        ledger.spend(Mechanism("b", Fraction(1, 10 ** 15)))
    assert len(ledger.spent) == 1


def test_ledger_guards_delta_budget_too():
    ledger = Ledger("10", "0.001")
    with pytest.raises(DPError):
        ledger.spend(Mechanism("a", "0.1", "0.01"))


def test_mechanism_params_are_exact_fractions():
    m = Mechanism("a", "0.1", "0.05")
    assert m.epsilon == Fraction(1, 10) and m.delta == Fraction(1, 20)


@pytest.mark.parametrize("call", [
    lambda: Mechanism("", "0.1"),
    lambda: Mechanism("a", "-0.1"),
    lambda: Mechanism("a", "0.1", "-0.1"),
    lambda: Mechanism("a", "0.1", "1.01"),
    lambda: Mechanism("a", float("inf")),
    lambda: Mechanism("a", True),
    lambda: Mechanism("a", "abc"),
    lambda: sequential([]),
    lambda: sequential([Mechanism("a", 1), "x"]),
    lambda: group_privacy("0.1", 0),
    lambda: group_privacy("0.1", True),
    lambda: Ledger("1").spend("not-a-mechanism"),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(DPError):
        call()
