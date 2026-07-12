# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``benford`` library (Benford's Law digit analysis)."""
import math
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "benford"))

from benford import (  # noqa: E402
    first_digit, expected_distribution, chi_square, mad, conforms, BenfordError)


def test_expected_is_log_formula():
    exp = expected_distribution()
    for d in range(1, 10):
        assert abs(exp[d] - math.log10(1 + 1 / d)) < 1e-12
    assert abs(sum(exp.values()) - 1.0) < 1e-9
    assert round(exp[1], 3) == 0.301


def test_first_digit():
    assert first_digit(0.00123) == 1
    assert first_digit(4567) == 4
    assert first_digit(-812) == 8
    assert first_digit(9) == 9


def test_conformity_detection():
    benford_like = [2 ** n for n in range(1, 500)]
    non_benford = [9, 90, 900, 95, 98] * 40
    assert conforms(benford_like, mad_threshold=0.015) is True
    assert conforms(non_benford) is False
    assert mad(non_benford) > mad(benford_like)
    assert chi_square(non_benford) > chi_square(benford_like)


def test_rejects_bad_input():
    with pytest.raises(BenfordError):
        first_digit(0)
    with pytest.raises(BenfordError):
        mad([])
    with pytest.raises(BenfordError):
        first_digit(float("inf"))
