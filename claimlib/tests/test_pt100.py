# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the pt100 module (IEC 60751 Callendar–Van Dusen)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "pt100"
_spec = importlib.util.spec_from_file_location(
    "claimlib_pt100", _MOD_DIR / "pt100.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_pt100"] = _m
_spec.loader.exec_module(_m)

Pt100Error = _m.Pt100Error
resistance = _m.resistance
temperature = _m.temperature


@pytest.mark.parametrize("t,r", [
    (0.0, 100.0),
    (100.0, 138.5055),
    (-200.0, 18.52008),
    (200.0, 175.856),
    (850.0, 390.481125),
])
def test_standard_table_points(t, r):
    assert resistance(t) == pytest.approx(r, abs=1e-4)


def test_inverse_roundtrip_precise():
    for t in (-200.0, -123.456, -0.5, 0.0, 0.5, 37.0, 419.53, 850.0):
        assert temperature(resistance(t)) == pytest.approx(t, abs=1e-6)


def test_monotone_over_full_span():
    prev = resistance(-200.0)
    t = -199.0
    while t <= 850.0:
        cur = resistance(t)
        assert cur > prev
        prev = cur
        t += 7.0


def test_pt1000_scaling():
    for t in (-100.0, 0.0, 250.0):
        assert resistance(t, 1000.0) == pytest.approx(10 * resistance(t),
                                                      abs=1e-9)
    assert temperature(1385.055, 1000.0) == pytest.approx(100.0, abs=1e-6)


@pytest.mark.parametrize("call", [
    lambda: resistance(-200.001),
    lambda: resistance(850.001),
    lambda: resistance(float("nan")),
    lambda: resistance(0.0, 0.0),
    lambda: resistance(0.0, -5.0),
    lambda: temperature(18.0),        # below -200 degC resistance
    lambda: temperature(391.0),       # above 850 degC resistance
    lambda: temperature(float("inf")),
    lambda: resistance(True),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(Pt100Error):
        call()
