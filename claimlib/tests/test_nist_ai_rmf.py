# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the nist_ai_rmf module (NIST AI 100-1 Core)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "nist_ai_rmf"
_spec = importlib.util.spec_from_file_location(
    "claimlib_nist_ai_rmf", _MOD_DIR / "nist_ai_rmf.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_nist_ai_rmf"] = _m
_spec.loader.exec_module(_m)

RMFError = _m.RMFError
FUNCTIONS = _m.FUNCTIONS
CATEGORIES = _m.CATEGORIES
SUBCATEGORIES = _m.SUBCATEGORIES
TRUSTWORTHY = _m.TRUSTWORTHY
category_ids = _m.category_ids
coverage = _m.coverage


def test_published_core_shape():
    assert FUNCTIONS == ("GOVERN", "MAP", "MEASURE", "MANAGE")
    assert sum(CATEGORIES.values()) == 19
    assert sum(SUBCATEGORIES.values()) == 72
    assert len(TRUSTWORTHY) == 7


def test_category_ids_shape():
    assert category_ids("GOVERN")[0] == "GOVERN 1"
    assert category_ids("GOVERN")[-1] == "GOVERN 6"
    assert len(category_ids("MEASURE")) == 4


def test_full_and_empty_coverage():
    everything = [c for fn in FUNCTIONS for c in category_ids(fn)]
    assert coverage(everything)["coverage_pct"] == 100.0
    assert coverage([])["addressed"] == 0


def test_per_function_breakdown():
    got = coverage(["MAP 1", "MAP 2", "MAP 3", "MAP 4", "MAP 5"])
    assert got["functions"]["MAP"]["coverage_pct"] == 100.0
    assert got["functions"]["GOVERN"]["addressed"] == 0
    assert got["addressed"] == 5


def test_duplicates_count_once():
    assert coverage(["GOVERN 1", "GOVERN 1"])["addressed"] == 1


@pytest.mark.parametrize("call", [
    lambda: category_ids("AUDIT"),
    lambda: coverage(["GOVERN 0"]),
    lambda: coverage(["GOVERN 7"]),
    lambda: coverage(["MANAGE 5"]),
    lambda: coverage(["map 1"]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(RMFError):
        call()
