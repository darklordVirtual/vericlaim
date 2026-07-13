# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the iso_42001 module (ISO/IEC 42001:2023 AIMS)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "iso_42001"
_spec = importlib.util.spec_from_file_location(
    "claimlib_iso_42001", _MOD_DIR / "iso_42001.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_iso_42001"] = _m
_spec.loader.exec_module(_m)

AIMSError = _m.AIMSError
CLAUSES = _m.CLAUSES
ANNEX_A_GROUPS = _m.ANNEX_A_GROUPS
ANNEX_A_TOTAL = _m.ANNEX_A_TOTAL
clause_title = _m.clause_title
soa = _m.soa


def test_published_structure():
    assert sorted(CLAUSES) == [4, 5, 6, 7, 8, 9, 10]
    assert len(ANNEX_A_GROUPS) == 9
    assert ANNEX_A_TOTAL == 38
    assert sum(g["controls"] for g in ANNEX_A_GROUPS.values()) == 38


def test_clause_titles():
    assert clause_title(4) == "Context of the organization"
    assert clause_title(8) == "Operation"
    assert clause_title(10) == "Improvement"


def test_full_soa():
    full = soa({g: m["controls"] for g, m in ANNEX_A_GROUPS.items()})
    assert full["applicable"] == 38
    assert full["excluded"] == 0
    assert full["applicable_pct"] == 100.0


def test_partial_soa_and_omitted_groups():
    got = soa({"A.2": 1})
    assert got["applicable"] == 1 and got["excluded"] == 37
    assert got["groups"]["A.9"]["applicable"] == 0


def test_soa_boundary_full_group_allowed():
    assert soa({"A.6": 9})["groups"]["A.6"]["excluded"] == 0


@pytest.mark.parametrize("call", [
    lambda: soa({"A.1": 1}),
    lambda: soa({"A.11": 1}),
    lambda: soa({"A.2": 4}),
    lambda: soa({"A.6": 10}),
    lambda: soa({"A.5": -1}),
    lambda: soa({"A.5": 1.5}),
    lambda: soa({"A.5": True}),
    lambda: soa(["A.2"]),
    lambda: clause_title(3),
    lambda: clause_title(True),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(AIMSError):
        call()
