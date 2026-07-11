# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the vendored ``semver`` library (CLAIM-LIB-SEMVER-001).

Asserts correctness of parse / compare / satisfies on concrete cases and
edge cases drawn from the SemVer 2.0.0 spec, plus error handling.
"""
import sys
from pathlib import Path

import pytest

MODULE_DIR = Path(__file__).resolve().parents[1] / "modules" / "semver"
sys.path.insert(0, str(MODULE_DIR))

import semver  # noqa: E402


def test_parse_basic():
    assert semver.parse("1.2.3") == (1, 2, 3, ())


def test_parse_prerelease_mixed_identifiers():
    # Numeric identifiers -> int, alphanumeric -> str (SemVer §9).
    assert semver.parse("1.0.0-alpha.1") == (1, 0, 0, ("alpha", 1))
    assert semver.parse("1.0.0-x.7.z.92") == (1, 0, 0, ("x", 7, "z", 92))


def test_parse_ignores_build_metadata():
    # Build metadata is validated then discarded (§10).
    assert semver.parse("1.2.3-beta+exp.sha.5114f85") == (1, 2, 3, ("beta",))
    assert semver.parse("1.2.3+build.1") == (1, 2, 3, ())


def test_parse_rejects_leading_zeros_and_malformed():
    for bad in ["01.0.0", "1.02.3", "1.2", "1.2.3.4", "", "v1.2.3",
                "1.2.3-01", "1.2.3-", "1.2.3-beta..1", "-1.2.3"]:
        with pytest.raises(semver.SemverError):
            semver.parse(bad)


def test_compare_core_precedence():
    # §11.2: 1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
    assert semver.compare("1.0.0", "2.0.0") == -1
    assert semver.compare("2.1.1", "2.1.0") == 1
    assert semver.compare("2.0.0", "2.0.0") == 0


def test_compare_prerelease_lower_than_release():
    # §11.3
    assert semver.compare("1.0.0-alpha", "1.0.0") == -1
    assert semver.compare("1.0.0", "1.0.0-alpha") == 1


def test_compare_golden_chain():
    # §11.4 verbatim spec ordering — every consecutive pair is strictly less.
    chain = ["1.0.0-alpha", "1.0.0-alpha.1", "1.0.0-alpha.beta", "1.0.0-beta",
             "1.0.0-beta.2", "1.0.0-beta.11", "1.0.0-rc.1", "1.0.0"]
    for lo, hi in zip(chain, chain[1:]):
        assert semver.compare(lo, hi) == -1
        assert semver.compare(hi, lo) == 1


def test_compare_numeric_below_alphanumeric():
    # §11.4.3: numeric identifiers always rank below alphanumeric ones.
    assert semver.compare("1.0.0-1", "1.0.0-alpha") == -1
    # numeric compare is numeric, not lexical: 2 < 11
    assert semver.compare("1.0.0-beta.2", "1.0.0-beta.11") == -1


def test_compare_build_metadata_ignored():
    # §10
    assert semver.compare("1.0.0+build.1", "1.0.0+build.999") == 0


def test_satisfies_exact_and_inequalities():
    assert semver.satisfies("1.2.3", "1.2.3") is True
    assert semver.satisfies("1.2.4", "1.2.3") is False
    assert semver.satisfies("1.2.3", ">=1.2.3") is True
    assert semver.satisfies("1.2.2", ">=1.2.3") is False
    assert semver.satisfies("1.2.2", "<1.2.3") is True
    assert semver.satisfies("1.2.3", "<1.2.3") is False


def test_satisfies_caret():
    # ^1.2.3 -> >=1.2.3 <2.0.0
    assert semver.satisfies("1.9.9", "^1.2.3") is True
    assert semver.satisfies("2.0.0", "^1.2.3") is False
    # ^0.2.3 -> >=0.2.3 <0.3.0
    assert semver.satisfies("0.2.9", "^0.2.3") is True
    assert semver.satisfies("0.3.0", "^0.2.3") is False
    # ^0.0.3 -> >=0.0.3 <0.0.4
    assert semver.satisfies("0.0.3", "^0.0.3") is True
    assert semver.satisfies("0.0.4", "^0.0.3") is False


def test_satisfies_tilde():
    # ~1.2.3 -> >=1.2.3 <1.3.0
    assert semver.satisfies("1.2.99", "~1.2.3") is True
    assert semver.satisfies("1.3.0", "~1.2.3") is False
    assert semver.satisfies("1.2.2", "~1.2.3") is False


def test_satisfies_prerelease_below_release_bound():
    # §11.3: 1.2.3-alpha is below the 1.2.3 lower bound of ^1.2.3.
    assert semver.satisfies("1.2.3-alpha", "^1.2.3") is False
    assert semver.satisfies("1.2.3-alpha", "<1.2.3") is True
    assert semver.satisfies("1.2.3-beta", ">=1.2.3-alpha") is True


def test_satisfies_rejects_bad_spec():
    with pytest.raises(semver.SemverError):
        semver.satisfies("1.2.3", "")
    with pytest.raises(semver.SemverError):
        semver.satisfies("1.2.3", ">=not.a.version")
