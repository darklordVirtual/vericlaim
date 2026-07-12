# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``soc2`` library (AICPA Trust Services Criteria)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "soc2"))

from soc2 import CATEGORIES, COMMON_CRITERIA, is_valid_criterion, coverage, SOC2Error  # noqa: E402


def test_five_categories():
    assert set(CATEGORIES) == {"SEC", "AVL", "PIN", "CON", "PRI"}


def test_nine_common_criteria():
    assert set(COMMON_CRITERIA) == {f"CC{i}" for i in range(1, 10)}
    assert COMMON_CRITERIA["CC6"] == "Logical and Physical Access Controls"


def test_coverage_math():
    assert coverage([])["coverage"] == 0.0
    assert coverage(list(COMMON_CRITERIA))["coverage"] == 1.0
    cov = coverage(["CC1", "CC2", "CC3"])
    assert cov["coverage"] == round(3 / 9, 4)
    assert cov["implemented"] == 3


def test_validation():
    assert is_valid_criterion("CC1") is True
    assert is_valid_criterion("CC10") is False
    with pytest.raises(SOC2Error):
        coverage(["CC1", "CC99"])
