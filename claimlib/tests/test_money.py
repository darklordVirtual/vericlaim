# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``money`` library (allocation + banker's rounding)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "money"))

from money import allocate, split_evenly, round_money, MoneyError  # noqa: E402


def test_equal_split_is_cent_exact():
    parts = allocate(100, [1, 1, 1])
    assert parts == [34, 33, 33]
    assert sum(parts) == 100


def test_sum_invariant_holds_for_many_shapes():
    for total in (0, 1, 7, 100, 99991):
        for weights in ([1, 1, 1], [1, 2, 3, 4], [5, 1], [1], [0, 1, 0, 2]):
            assert sum(allocate(total, weights)) == total


def test_weighted_allocation():
    assert allocate(1000, [1, 2, 1]) == [250, 500, 250]
    assert allocate(5, [3, 1]) == [4, 1]


def test_split_evenly_matches_allocate_ones():
    assert split_evenly(100, 6) == allocate(100, [1, 1, 1, 1, 1, 1])
    assert split_evenly(100, 6) == [17, 17, 17, 17, 16, 16]


def test_banker_rounding_ties_to_even():
    assert str(round_money("0.5", 0)) == "0"
    assert str(round_money("1.5", 0)) == "2"
    assert str(round_money("2.5", 0)) == "2"
    assert str(round_money("3.5", 0)) == "4"
    assert str(round_money("2.675", 2)) == "2.68"
    assert str(round_money("1.005", 2)) == "1.00"


def test_rejects_bad_arguments():
    with pytest.raises(MoneyError):
        allocate(-1, [1])
    with pytest.raises(MoneyError):
        allocate(10, [])
    with pytest.raises(MoneyError):
        allocate(10, [0, 0])
    with pytest.raises(MoneyError):
        allocate(10, [1, -1])
    with pytest.raises(MoneyError):
        split_evenly(10, 0)
    with pytest.raises(MoneyError):
        round_money("1.0", -1)


def test_zero_total_gives_zeros():
    assert allocate(0, [3, 1, 2]) == [0, 0, 0]
