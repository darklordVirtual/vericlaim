# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``cis_controls`` library (CIS Controls v8.1).

Reference values are independently known from the CIS Critical Security
Controls v8.1 guide (June 2024): 18 Controls, 153 Safeguards, cumulative
Implementation Group totals IG1 = 56, IG2 = 130 (+74), IG3 = 153 (+23).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "cis_controls"))

from cis_controls import (  # noqa: E402
    CONTROLS, IMPLEMENTATION_GROUPS, CISError,
    is_valid_control, title_of, safeguard_counts, ig_totals, coverage, gaps,
)


def test_eighteen_controls_numbered_1_to_18():
    assert set(CONTROLS) == set(range(1, 19))
    assert len(CONTROLS) == 18


def test_published_titles_spot_checks():
    assert title_of(1) == "Inventory and Control of Enterprise Assets"
    assert title_of(3) == "Data Protection"
    assert title_of(13) == "Network Monitoring and Defense"
    assert title_of(18) == "Penetration Testing"


def test_framework_totals_match_published_counts():
    totals = ig_totals()
    assert totals["total"] == 153
    assert totals["IG1"] == 56
    assert totals["IG2"] == 130          # IG1 + 74
    assert totals["IG3"] == 153          # IG2 + 23
    assert totals["IG2"] - totals["IG1"] == 74
    assert totals["IG3"] - totals["IG2"] == 23


def test_ig_counts_are_cumulative_and_ig3_is_total():
    for number in CONTROLS:
        c = safeguard_counts(number)
        assert 0 <= c["IG1"] <= c["IG2"] <= c["IG3"] == c["total"]


def test_per_control_published_rows_spot_checks():
    # Control 1: 5 safeguards, 2 in IG1, 4 in IG2 (cumulative).
    assert safeguard_counts(1) == {"total": 5, "IG1": 2, "IG2": 4, "IG3": 5}
    # Control 13 and 16 and 18 have NO IG1 safeguards.
    assert safeguard_counts(13)["IG1"] == 0
    assert safeguard_counts(16)["IG1"] == 0
    assert safeguard_counts(18)["IG1"] == 0
    # Control 14 is almost entirely IG1 (8 of 9).
    assert safeguard_counts(14) == {"total": 9, "IG1": 8, "IG2": 9, "IG3": 9}


def test_implementation_groups_order():
    assert IMPLEMENTATION_GROUPS == ("IG1", "IG2", "IG3")


def test_coverage_empty_and_full():
    empty = coverage([])
    assert empty["controls"]["implemented"] == 0
    assert empty["controls"]["coverage"] == 0.0
    assert empty["controls"]["missing"] == list(range(1, 19))
    for ig in IMPLEMENTATION_GROUPS:
        assert empty["safeguards"][ig]["coverage"] == 0.0

    full = coverage(list(CONTROLS))
    assert full["controls"]["coverage"] == 1.0
    assert full["controls"]["missing"] == []
    for ig in IMPLEMENTATION_GROUPS:
        assert full["safeguards"][ig]["coverage"] == 1.0
        assert full["safeguards"][ig]["implemented"] == \
            full["safeguards"][ig]["total"]


def test_coverage_hand_verified_fractions():
    cov = coverage([1, 2])
    assert cov["controls"]["implemented"] == 2
    assert cov["controls"]["coverage"] == 0.1111       # 2/18
    assert cov["safeguards"]["IG1"]["implemented"] == 5   # 2 + 3
    assert cov["safeguards"]["IG1"]["coverage"] == 0.0893  # 5/56
    assert cov["safeguards"]["IG2"]["implemented"] == 10  # 4 + 6
    assert cov["safeguards"]["IG2"]["coverage"] == 0.0769  # 10/130
    assert cov["safeguards"]["IG3"]["implemented"] == 12  # 5 + 7
    assert cov["safeguards"]["IG3"]["coverage"] == 0.0784  # 12/153


def test_coverage_controls_without_ig1_safeguards():
    # 13, 16, 18 contribute nothing at IG1 but 11 + 14 + 5 = 30 at IG3.
    cov = coverage([13, 16, 18])
    assert cov["safeguards"]["IG1"]["implemented"] == 0
    assert cov["safeguards"]["IG1"]["coverage"] == 0.0
    assert cov["safeguards"]["IG3"]["implemented"] == 30
    assert cov["controls"]["coverage"] == 0.1667       # 3/18


def test_coverage_missing_list_is_sorted_complement():
    cov = coverage([18, 2, 9])
    assert cov["controls"]["missing"] == [
        1, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17]


def test_coverage_collapses_duplicates():
    cov = coverage([1, 1, 2, 2, 2])
    assert cov["controls"]["implemented"] == 2


def test_gaps_lists_missing_controls_with_counts():
    missing = gaps(list(range(1, 17)))     # 1..16 implemented
    assert [g["control"] for g in missing] == [17, 18]
    assert missing[0]["title"] == "Incident Response Management"
    assert missing[0]["safeguards"] == 9
    assert missing[1] == {"control": 18, "title": "Penetration Testing",
                          "safeguards": 5, "IG1": 0, "IG2": 3, "IG3": 5}
    assert gaps(list(CONTROLS)) == []
    assert len(gaps([])) == 18


def test_is_valid_control():
    assert is_valid_control(1) is True
    assert is_valid_control(18) is True
    assert is_valid_control(0) is False
    assert is_valid_control(19) is False
    assert is_valid_control("1") is False
    assert is_valid_control(True) is False   # bool must not alias Control 1


def test_rejects_unknown_and_malformed_inputs():
    with pytest.raises(CISError):
        coverage([0])
    with pytest.raises(CISError):
        coverage([19])
    with pytest.raises(CISError):
        coverage(["1"])
    with pytest.raises(CISError):
        coverage([1.0])       # float, even if integral
    with pytest.raises(CISError):
        coverage([True])      # bool is not a control number
    with pytest.raises(CISError):
        gaps([None])
    with pytest.raises(CISError):
        title_of(42)
    with pytest.raises(CISError):
        safeguard_counts(-3)


def test_deterministic_output():
    assert coverage([5, 3, 1]) == coverage([1, 3, 5])
    assert gaps([2, 4]) == gaps([4, 2])
