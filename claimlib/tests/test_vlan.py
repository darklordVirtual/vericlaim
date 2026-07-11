# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``vlan`` library (802.1Q VLAN IDs + ranges)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "vlan"))

from vlan import is_valid, parse_range, format_range, VLANError  # noqa: E402


def test_validity_boundaries():
    assert is_valid(0) is False        # priority-tagged, not assignable
    assert is_valid(1) is True
    assert is_valid(4094) is True
    assert is_valid(4095) is False     # reserved
    assert is_valid(4096) is False


def test_parse_range():
    assert parse_range("1,10-12,4094") == [1, 10, 11, 12, 4094]
    assert parse_range("3,2,1") == [1, 2, 3]
    assert parse_range("5,5,6,6,7") == [5, 6, 7]


def test_format_range_collapses_runs():
    assert format_range([1, 2, 3]) == "1-3"
    assert format_range([1, 3, 5]) == "1,3,5"
    assert format_range([1, 10, 11, 12, 4094]) == "1,10-12,4094"


def test_round_trip():
    for text in ("1", "1,10-12,4094", "1-3", "1,3,5,7"):
        parsed = parse_range(text)
        assert parse_range(format_range(parsed)) == parsed


def test_rejects_bad_input():
    for bad in ("0", "4095", "1,,2", "10-9", "a", "1-4095"):
        with pytest.raises(VLANError):
            parse_range(bad)
    with pytest.raises(VLANError):
        format_range([0])
