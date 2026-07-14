# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the datasheet module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "datasheet"
_spec = importlib.util.spec_from_file_location(
    "claimlib_datasheet", _MOD_DIR / "datasheet.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_datasheet"] = _m
_spec.loader.exec_module(_m)

SECTIONS = _m.SECTIONS
DatasheetError = _m.DatasheetError
completeness = _m.completeness


def test_seven_lifecycle_sections():
    assert len(SECTIONS) == 7
    assert SECTIONS[0] == "Motivation"
    assert SECTIONS[-1] == "Maintenance"


def test_empty_sheet_is_zero_covered():
    got = completeness({})
    assert got["covered"] == 0 and got["completeness_pct"] == 0.0
    assert not got["complete"]


def test_full_sheet_is_complete():
    got = completeness({s: "documented" for s in SECTIONS})
    assert got["complete"] and got["completeness_pct"] == 100.0


def test_justified_na_counts_as_covered():
    got = completeness({"Composition": {"na": True, "reason": "no people"}})
    assert got["covered"] == 1 and got["not_applicable"] == 1
    assert got["answered"] == 0


def test_unjustified_na_is_a_gap():
    got = completeness({"Composition": {"na": True, "reason": "  "}})
    assert got["covered"] == 0
    assert "Composition" in got["missing"]


def test_empty_answer_is_a_gap():
    got = completeness({"Uses": "   "})
    assert got["answered"] == 0 and "Uses" in got["missing"]


def test_mixed_coverage_count():
    got = completeness({"Motivation": "why", "Uses": "how",
                        "Maintenance": {"na": True, "reason": "frozen"}})
    assert got["covered"] == 3 and got["answered"] == 2
    assert got["not_applicable"] == 1


@pytest.mark.parametrize("call", [
    lambda: completeness("notadict"),
    lambda: completeness({"Bogus": "x"}),
    lambda: completeness({"Uses": 123}),
    lambda: completeness({"Uses": {"reason": "missing na flag"}}),
    lambda: completeness({"Uses": {"na": "yes", "reason": "x"}}),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(DatasheetError):
        call()
