# SPDX-License-Identifier: Apache-2.0
"""Attribute-sampling sample sizes for audit tests of controls (Poisson method).

A pre-verified claimlib code artifact for audit. When testing a control, an
auditor picks a sample large enough that, at a chosen confidence, the observed
deviation rate bounds the true rate below the tolerable rate. The Poisson (AICPA
Audit Guide) method sizes the sample from a reliability factor R: the sample size
is ceil(R / tolerable_rate), and after testing, the achieved upper deviation rate
is R / sample_size. This module encodes the reliability factors and the sizing;
that the factors match their Poisson basis, that the sizes reproduce the standard
worked examples, and that the arithmetic is self-consistent is registered as a
claim and proven by a committed evidence artifact.

Public API
----------
    reliability_factor(confidence: float, expected_deviations: int = 0) -> float
    sample_size(tolerable_rate, confidence=0.95, expected_deviations=0) -> int
    upper_deviation_rate(sample_size, deviations, confidence=0.95) -> float

    >>> sample_size(0.05, confidence=0.95, expected_deviations=0)
    60
"""
from __future__ import annotations

import math

# AICPA Audit Guide Poisson reliability factors: confidence -> {deviations: R}.
# The 0-deviation factors equal -ln(1 - confidence) (rounded); see the evidence.
POISSON_FACTORS = {
    0.90: {0: 2.31, 1: 3.89, 2: 5.33, 3: 6.69},
    0.95: {0: 3.00, 1: 4.75, 2: 6.30, 3: 7.76},
    0.99: {0: 4.61, 1: 6.64, 2: 8.41, 3: 10.05},
}


class SamplingError(ValueError):
    """An unsupported confidence, out-of-range rate, or deviation count."""


def reliability_factor(confidence: float, expected_deviations: int = 0) -> float:
    """Return the Poisson reliability factor R for *confidence* and expected deviations."""
    if confidence not in POISSON_FACTORS:
        raise SamplingError(f"confidence must be one of {sorted(POISSON_FACTORS)}")
    table = POISSON_FACTORS[confidence]
    if not isinstance(expected_deviations, int) or isinstance(expected_deviations, bool) \
            or expected_deviations not in table:
        raise SamplingError(f"expected_deviations must be one of {sorted(table)}")
    return table[expected_deviations]


def sample_size(tolerable_rate: float, confidence: float = 0.95,
                expected_deviations: int = 0) -> int:
    """Return the attribute-sampling sample size: ceil(R / tolerable_rate)."""
    if not 0 < tolerable_rate < 1:
        raise SamplingError("tolerable_rate must be a fraction in (0, 1)")
    factor = reliability_factor(confidence, expected_deviations)
    return math.ceil(factor / tolerable_rate)


def upper_deviation_rate(sample_size: int, deviations: int,
                         confidence: float = 0.95) -> float:
    """Return the achieved upper deviation rate R / sample_size after testing."""
    if not isinstance(sample_size, int) or isinstance(sample_size, bool) or sample_size < 1:
        raise SamplingError("sample_size must be a positive int")
    factor = reliability_factor(confidence, deviations)
    return factor / sample_size
