# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``apdex`` library."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "apdex"))

from apdex import apdex, classify, counts, ApdexError  # noqa: E402


def test_reference_score():
    assert apdex([0.1, 0.2, 0.3, 1.0, 3.0], 0.5) == 0.7


def test_extremes():
    assert apdex([0.1, 0.2], 0.5) == 1.0
    assert apdex([10.0, 20.0], 0.5) == 0.0


def test_zone_boundaries():
    assert classify(2.0, 2) == "satisfied"      # exactly T
    assert classify(8.0, 2) == "tolerating"     # exactly 4T
    assert classify(8.0001, 2) == "frustrated"


def test_counts():
    c = counts([1, 1, 4, 16], 1)
    assert c == {"satisfied": 2, "tolerating": 1, "frustrated": 1, "total": 4}


def test_rejects_bad_input():
    with pytest.raises(ApdexError):
        apdex([], 1)
    with pytest.raises(ApdexError):
        apdex([1, 2], 0)
    with pytest.raises(ApdexError):
        classify(1, -1)
