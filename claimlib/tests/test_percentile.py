# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``percentile`` library, cross-checked vs statistics."""
import statistics
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "percentile"))

from percentile import percentile, median, quantiles, PercentileError  # noqa: E402


def test_linear_agrees_with_statistics():
    for data in ([1, 2, 3, 4, 5], list(range(1, 101)), [3, 1, 4, 1, 5, 9, 2, 6]):
        oracle = statistics.quantiles(data, n=100, method="inclusive")
        for p in (1, 25, 50, 75, 90, 95, 99):
            assert abs(percentile(data, p) - oracle[p - 1]) < 1e-9


def test_median():
    assert median([1, 2, 3, 4]) == 2.5
    assert median([1, 2, 3, 4, 5]) == 3
    assert median([7]) == 7


def test_nearest_rank():
    data = [10, 20, 30, 40, 50]
    assert percentile(data, 90, method="nearest_rank") == 50
    assert percentile(data, 20, method="nearest_rank") == 10
    assert percentile(data, 100, method="nearest_rank") == 50


def test_quantiles_quartiles():
    q = quantiles([1, 2, 3, 4, 5], n=4)
    assert len(q) == 3
    assert q[1] == median([1, 2, 3, 4, 5])


def test_rejects_bad_input():
    with pytest.raises(PercentileError):
        percentile([], 50)
    with pytest.raises(PercentileError):
        percentile([1, 2], 101)
    with pytest.raises(PercentileError):
        percentile([1, 2], 50, method="cubic")
    with pytest.raises(PercentileError):
        quantiles([1, 2, 3], n=1)
