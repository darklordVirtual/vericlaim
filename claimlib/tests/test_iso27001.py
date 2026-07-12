# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``iso27001`` library (ISO/IEC 27001:2022 Annex A)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "iso27001"))

from iso27001 import THEMES, theme_of, is_valid_control, coverage, ISO27001Error  # noqa: E402


def test_four_themes_total_93():
    assert set(THEMES) == {"A.5", "A.6", "A.7", "A.8"}
    assert sum(count for _, count in THEMES.values()) == 93
    assert THEMES["A.5"] == ("Organizational", 37)


def test_control_validation():
    assert is_valid_control("A.5.1") is True
    assert is_valid_control("A.8.34") is True
    assert is_valid_control("A.6.9") is False    # People theme has only 8
    assert is_valid_control("A.9.1") is False
    assert theme_of("A.7.14") == "A.7"


def test_coverage_math():
    people = [f"A.6.{i}" for i in range(1, 9)]
    cov = coverage(people)
    assert cov["themes"]["A.6"]["coverage"] == 1.0
    assert cov["themes"]["A.5"]["coverage"] == 0.0
    assert coverage([])["overall"]["implemented"] == 0


def test_rejects_invalid_controls():
    with pytest.raises(ISO27001Error):
        coverage(["A.5.1", "A.6.99"])
    with pytest.raises(ISO27001Error):
        theme_of("nope")
