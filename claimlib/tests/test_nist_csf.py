# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``nist_csf`` library (NIST CSF 2.0)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "nist_csf"))

from nist_csf import FUNCTIONS, CATEGORIES, function_of, is_valid_category, coverage, CSFError  # noqa: E402


def test_six_functions():
    assert set(FUNCTIONS) == {"GV", "ID", "PR", "DE", "RS", "RC"}
    assert FUNCTIONS["GV"] == "Govern"
    assert FUNCTIONS["RC"] == "Recover"


def test_categories_map_to_prefix_function():
    assert len(CATEGORIES) == 22
    for cid in CATEGORIES:
        assert function_of(cid) == cid.split(".")[0]


def test_coverage_math():
    govern = [c for c in CATEGORIES if c.startswith("GV.")]
    cov = coverage(govern)
    assert cov["functions"]["GV"]["coverage"] == 1.0
    assert cov["functions"]["GV"]["implemented"] == 6
    assert cov["functions"]["ID"]["coverage"] == 0.0
    assert coverage(list(CATEGORIES))["overall"]["coverage"] == 1.0
    assert coverage([])["overall"]["implemented"] == 0


def test_validation():
    assert is_valid_category("GV.OC") is True
    assert is_valid_category("XX.YY") is False
    with pytest.raises(CSFError):
        function_of("XX.YY")
    with pytest.raises(CSFError):
        coverage(["GV.OC", "not-a-category"])
