# SPDX-License-Identifier: Apache-2.0
"""A tip calculator — a worked example of a *correctness* claim.

The claim is not "how fast" or "how many features," but "does it compute the
right answer?" Claim-Oriented Programming registers "all N example bills produce
the expected total," backs it with an artifact that records how many cases pass,
and binds the doc — so "all cases pass" can never quietly become "most cases."
"""
from __future__ import annotations


def total_with_tip(bill: float, tip_percent: float) -> float:
    """Total to pay including a percentage tip, rounded to cents."""
    tip = round(bill * tip_percent / 100, 2)
    return round(bill + tip, 2)
