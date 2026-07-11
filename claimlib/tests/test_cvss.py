# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable cvss module (claimlib/modules/cvss)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "cvss"))

from cvss import CvssError, base_score, parse_vector, severity  # noqa: E402


def test_reference_scores():
    # Independently-known CVSS v3.1 base scores.
    assert base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H") == 9.8
    assert base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H") == 10.0
    assert base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N") == 6.1
    assert base_score("CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H") == 8.8


def test_no_impact_is_zero():
    assert base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:N") == 0.0


def test_severity_bands():
    assert severity(0.0) == "none"
    assert severity(3.9) == "low"
    assert severity(4.0) == "medium"
    assert severity(6.9) == "medium"
    assert severity(7.0) == "high"
    assert severity(8.9) == "high"
    assert severity(9.0) == "critical"
    assert severity(10.0) == "critical"


def test_vector_order_independent():
    a = base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    b = base_score("C:H/I:H/A:H/AV:N/AC:L/PR:N/UI:N/S:U")  # shuffled, no prefix
    assert a == b == 9.8


def test_parse_rejects_unknown_and_missing():
    with pytest.raises(CvssError):
        parse_vector("CVSS:3.1/AV:Z/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")  # bad value
    with pytest.raises(CvssError):
        parse_vector("AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H")  # missing A
    with pytest.raises(CvssError):
        parse_vector("")


def test_severity_of_reference():
    assert severity(base_score("CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")) == "critical"
