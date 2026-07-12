# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``pci_dss`` library (PCI DSS v4.0)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "pci_dss"))

from pci_dss import GOALS, REQUIREMENTS, goal_of, is_valid_requirement, coverage, PCIDSSError  # noqa: E402


def test_six_goals_twelve_requirements():
    assert set(GOALS) == set(range(1, 7))
    assert set(REQUIREMENTS) == set(range(1, 13))


def test_goal_mapping():
    assert goal_of(1) == 1 and goal_of(2) == 1
    assert goal_of(9) == 4
    assert goal_of(12) == 6


def test_coverage_math():
    assert coverage([])["overall"]["coverage"] == 0.0
    assert coverage(list(range(1, 13)))["overall"]["coverage"] == 1.0
    assert coverage([7, 8, 9])["goals"][4]["coverage"] == 1.0
    assert coverage([1])["goals"][1]["coverage"] == 0.5


def test_validation():
    assert is_valid_requirement(1) is True
    assert is_valid_requirement(13) is False
    assert is_valid_requirement(True) is False
    with pytest.raises(PCIDSSError):
        goal_of(99)
    with pytest.raises(PCIDSSError):
        coverage([1, 13])
