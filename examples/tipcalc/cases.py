# SPDX-License-Identifier: Apache-2.0
"""Reference cases for the tip calculator: (bill, tip_percent, expected_total).

Hand-verified, chosen to avoid rounding-boundary ambiguity. The evidence script
and the test both read these, so the claim "all cases pass" is checked against
one shared, committed source of truth.
"""
from __future__ import annotations

CASES: list[tuple[float, float, float]] = [
    (100.0, 15.0, 115.0),
    (100.0, 20.0, 120.0),
    (50.0, 10.0, 55.0),
    (50.0, 20.0, 60.0),
    (200.0, 15.0, 230.0),
    (80.0, 25.0, 100.0),
    (40.0, 5.0, 42.0),
    (25.0, 20.0, 30.0),
    (120.0, 10.0, 132.0),
    (60.0, 15.0, 69.0),
    (150.0, 18.0, 177.0),
    (90.0, 20.0, 108.0),
]
