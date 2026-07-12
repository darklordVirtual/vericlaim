# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``audit_sampling`` library (attribute sampling)."""
import math
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "audit_sampling"))

from audit_sampling import (  # noqa: E402
    reliability_factor, sample_size, upper_deviation_rate, SamplingError)


def test_zero_deviation_factor_matches_poisson():
    for confidence in (0.90, 0.95, 0.99):
        assert abs(reliability_factor(confidence, 0) - (-math.log(1 - confidence))) < 0.01


def test_standard_sample_sizes():
    assert sample_size(0.05, confidence=0.95, expected_deviations=0) == 60
    assert sample_size(0.10, confidence=0.95, expected_deviations=0) == 30


def test_upper_deviation_rate_within_tolerable():
    n = sample_size(0.05, 0.95, 0)
    assert upper_deviation_rate(n, 0, 0.95) <= 0.05


def test_monotonic_in_expected_deviations():
    sizes = [sample_size(0.05, 0.95, k) for k in range(4)]
    assert sizes == sorted(sizes) and len(set(sizes)) == 4


def test_rejects_bad_input():
    with pytest.raises(SamplingError):
        reliability_factor(0.80, 0)          # unsupported confidence
    with pytest.raises(SamplingError):
        sample_size(1.5)                     # rate out of range
    with pytest.raises(SamplingError):
        reliability_factor(0.95, 9)          # deviation count not tabulated
