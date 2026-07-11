# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``nis2`` library (NIS2 Article 21(2))."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "nis2"))

from nis2 import MEASURES, is_valid_measure, coverage, NIS2Error  # noqa: E402


def test_ten_measures():
    assert set(MEASURES) == set("abcdefghij")
    assert len(MEASURES) == 10


def test_coverage_math():
    assert coverage([])["coverage"] == 0.0
    assert coverage(list(MEASURES))["coverage"] == 1.0
    cov = coverage(["a", "b", "h", "j"])
    assert cov["coverage"] == 0.4
    assert cov["implemented"] == 4
    assert cov["missing"] == ["c", "d", "e", "f", "g", "i"]


def test_validation():
    assert is_valid_measure("a") is True
    assert is_valid_measure("z") is False
    with pytest.raises(NIS2Error):
        coverage(["a", "z"])
