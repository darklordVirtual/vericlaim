# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``oee`` library.

Reference: the published OEE worked example (Vorne / oee.com) --
Availability 88.81%, Performance 86.11%, Quality 97.80%, OEE 74.79%.
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "oee"))

from oee import availability, performance, quality, oee, OEEError  # noqa: E402


def test_published_worked_example():
    result = oee(planned_production_time=420 * 60, run_time=373 * 60,
                 ideal_cycle_time=1.0, total_count=19271, good_count=18848)
    assert round(result["availability"], 4) == 0.8881
    assert round(result["performance"], 4) == 0.8611
    assert round(result["quality"], 4) == 0.9780
    assert round(result["oee"], 4) == 0.7479


def test_perfect_line_is_one():
    assert oee(100.0, 100.0, 2.0, 50, 50)["oee"] == 1.0


def test_factor_formulas():
    assert availability(50, 100) == 0.5
    assert quality(9, 10) == 0.9
    assert performance(1.0, 25, 50.0) == 0.5


def test_rejects_out_of_domain():
    with pytest.raises(OEEError):
        availability(150, 100)              # run > planned
    with pytest.raises(OEEError):
        quality(11, 10)                     # good > total
    with pytest.raises(OEEError):
        performance(10.0, 100, 50.0)        # performance > 1
    with pytest.raises(OEEError):
        availability(50, 0)                 # zero planned time
    with pytest.raises(OEEError):
        quality(1, 0)                       # zero total count
