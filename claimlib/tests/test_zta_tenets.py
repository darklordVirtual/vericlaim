# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the zta_tenets module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "zta_tenets"
_spec = importlib.util.spec_from_file_location(
    "claimlib_zta_tenets", _MOD_DIR / "zta_tenets.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_zta_tenets"] = _m
_spec.loader.exec_module(_m)

ZTAError = _m.ZTAError
TENETS = _m.TENETS
coverage = _m.coverage


def test_seven_tenets_with_published_anchors():
    assert sorted(TENETS) == [1, 2, 3, 4, 5, 6, 7]
    assert "considered resources" in TENETS[1]
    assert "per-session basis" in TENETS[3]
    assert "dynamic policy" in TENETS[4]


def test_coverage_math():
    assert coverage(range(1, 8))["coverage_pct"] == 100.0
    got = coverage([1, 4])
    assert got["adhered"] == 2 and got["gaps"] == [2, 3, 5, 6, 7]
    assert coverage([])["adhered"] == 0


@pytest.mark.parametrize("bad", [[0], [8], [True], ["3"]])
def test_unknown_tenets_rejected(bad):
    with pytest.raises(ZTAError):
        coverage(bad)
