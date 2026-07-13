# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the erlang_b module (traffic engineering)."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "erlang_b"
_spec = importlib.util.spec_from_file_location(
    "claimlib_erlang_b", _MOD_DIR / "erlang_b.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_erlang_b"] = _m
_spec.loader.exec_module(_m)

ErlangBError = _m.ErlangBError
erlang_b = _m.erlang_b
min_circuits = _m.min_circuits


def _closed_form(n: int, a: Fraction) -> float:
    fact = 1
    terms = []
    for x in range(n + 1):
        if x:
            fact *= x
        terms.append(Fraction(a ** x, fact))
    return float(terms[-1] / sum(terms))


def test_single_circuit_identity():
    for a in (0.25, 1.0, 3.5, 10.0):
        assert erlang_b(1, a) == pytest.approx(a / (1 + a), abs=1e-15)


def test_matches_closed_form_exactly():
    for n, a in [(2, Fraction(1)), (5, Fraction(3)), (10, Fraction(7, 2)),
                 (15, Fraction(12))]:
        assert erlang_b(n, float(a)) == pytest.approx(
            _closed_form(n, a), abs=1e-12)


def test_published_table_row():
    # Standard engineering table: 10 circuits carry 5.092 E at 2% blocking.
    assert erlang_b(10, 5.092) == pytest.approx(0.02, rel=0.01)


def test_edge_cases():
    assert erlang_b(0, 5.0) == 1.0
    assert erlang_b(8, 0.0) == 0.0
    assert min_circuits(0.0, 0.5) == 0


def test_monotone_in_circuits_and_traffic():
    blocks = [erlang_b(n, 6.0) for n in range(1, 15)]
    assert all(b1 > b2 for b1, b2 in zip(blocks, blocks[1:]))
    grows = [erlang_b(8, float(a)) for a in range(1, 12)]
    assert all(g1 < g2 for g1, g2 in zip(grows, grows[1:]))


def test_min_circuits_meets_target_and_is_minimal():
    for a, t in [(5.0, 0.01), (20.0, 0.02), (1.0, 0.1)]:
        n = min_circuits(a, t)
        assert erlang_b(n, a) <= t
        assert erlang_b(n - 1, a) > t


@pytest.mark.parametrize("call", [
    lambda: erlang_b(-1, 1.0),
    lambda: erlang_b(2, -0.5),
    lambda: erlang_b(True, 1.0),
    lambda: erlang_b(1, float("nan")),
    lambda: erlang_b(1, float("inf")),
    lambda: erlang_b(200_000, 1.0),
    lambda: min_circuits(1.0, 0.0),
    lambda: min_circuits(1.0, 1.5),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(ErlangBError):
        call()
