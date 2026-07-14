# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the slsa_levels module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "slsa_levels"
_spec = importlib.util.spec_from_file_location(
    "claimlib_slsa_levels", _MOD_DIR / "slsa_levels.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_slsa_levels"] = _m
_spec.loader.exec_module(_m)

SLSAError = _m.SLSAError
LEVELS = _m.LEVELS
CAPABILITIES = _m.CAPABILITIES
assess = _m.assess


def test_published_level_names():
    assert LEVELS[0]["name"] == "Build L0: No guarantees"
    assert LEVELS[3]["name"] == "Build L3: Hardened builds"


def test_cumulative_ladder():
    assert assess([])["level"] == 0
    assert assess(["provenance_exists"])["level"] == 1
    assert assess(["provenance_exists", "hosted_platform",
                   "signed_provenance"])["level"] == 2
    assert assess(CAPABILITIES)["level"] == 3


def test_gap_caps_the_level():
    # Hardened platform declared, but provenance unsigned: capped at L1.
    got = assess(["provenance_exists", "hosted_platform",
                  "hardened_platform"])
    assert got["level"] == 1
    assert "signed_provenance" in got["missing_for_next"]


def test_missing_for_next_at_top_is_empty():
    assert assess(CAPABILITIES)["missing_for_next"] == []


@pytest.mark.parametrize("bad", [["sbom"], ["provenance"], ["L1"]])
def test_unknown_capabilities_rejected(bad):
    with pytest.raises(SLSAError):
        assess(bad)
