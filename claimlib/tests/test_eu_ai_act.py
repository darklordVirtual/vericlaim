# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the eu_ai_act module (Regulation (EU) 2024/1689)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "eu_ai_act"
_spec = importlib.util.spec_from_file_location(
    "claimlib_eu_ai_act", _MOD_DIR / "eu_ai_act.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_eu_ai_act"] = _m
_spec.loader.exec_module(_m)

AIActError = _m.AIActError
STRUCTURE = _m.STRUCTURE
ART5_PROHIBITIONS = _m.ART5_PROHIBITIONS
ANNEX3_AREAS = _m.ANNEX3_AREAS
OPERATIVE_TIERS = _m.OPERATIVE_TIERS
is_prohibition = _m.is_prohibition
is_high_risk_area = _m.is_high_risk_area
prohibition_screen = _m.prohibition_screen
area_coverage = _m.area_coverage


def test_published_structure():
    assert STRUCTURE == {"chapters": 13, "articles": 113, "annexes": 13}
    assert sorted(ART5_PROHIBITIONS) == list("abcdefgh")
    assert sorted(ANNEX3_AREAS) == list(range(1, 9))
    assert len(OPERATIVE_TIERS) == 5


def test_membership():
    assert is_prohibition("a") and is_prohibition("h")
    assert not is_prohibition("i") and not is_prohibition("")
    assert is_high_risk_area(1) and is_high_risk_area(8)
    assert not is_high_risk_area(9) and not is_high_risk_area(True)


def test_screen_clean_inventory_compliant():
    got = prohibition_screen([])
    assert got["compliant"] and got["flagged"] == []


def test_screen_any_hit_fails():
    got = prohibition_screen(["h"])
    assert not got["compliant"]
    assert got["flagged"] == ["h"] and got["flagged_count"] == 1


def test_screen_deduplicates():
    assert prohibition_screen(["c", "c", "c"])["flagged_count"] == 1


def test_area_coverage_math():
    full = area_coverage(range(1, 9))
    assert full["coverage_pct"] == 100.0 and full["gaps"] == []
    part = area_coverage([2, 5])
    assert part["assessed"] == 2 and part["coverage_pct"] == 25.0
    assert part["gaps"] == [1, 3, 4, 6, 7, 8]


@pytest.mark.parametrize("call", [
    lambda: prohibition_screen(["x"]),
    lambda: prohibition_screen(["a", "z"]),
    lambda: area_coverage([0]),
    lambda: area_coverage([1, 9]),
    lambda: area_coverage(["1"]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(AIActError):
        call()
