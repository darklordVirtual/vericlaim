# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the gdpr module (Regulation (EU) 2016/679 taxonomy)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "gdpr"
_spec = importlib.util.spec_from_file_location(
    "claimlib_gdpr", _MOD_DIR / "gdpr.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_gdpr"] = _m
_spec.loader.exec_module(_m)

GDPRError = _m.GDPRError
CHAPTERS = _m.CHAPTERS
PRINCIPLES = _m.PRINCIPLES
ART32_MEASURES = _m.ART32_MEASURES
N_ARTICLES = _m.N_ARTICLES
chapter_of = _m.chapter_of
principle_coverage = _m.principle_coverage
art32_coverage = _m.art32_coverage


def test_chapters_partition_all_articles():
    for article in range(1, N_ARTICLES + 1):
        owners = [ch for ch, (_, lo, hi) in CHAPTERS.items()
                  if lo <= article <= hi]
        assert len(owners) == 1


def test_structure_counts():
    assert len(CHAPTERS) == 11
    assert N_ARTICLES == 99
    assert len(PRINCIPLES) == 7
    assert len(ART32_MEASURES) == 4


@pytest.mark.parametrize("article,chapter", [
    (1, 1), (5, 2), (12, 3), (17, 3), (24, 4), (33, 4),
    (44, 5), (51, 6), (60, 7), (83, 8), (85, 9), (92, 10), (99, 11),
])
def test_known_articles_resolve(article, chapter):
    assert chapter_of(article) == chapter


def test_principle_coverage_math():
    full = principle_coverage(list(PRINCIPLES))
    assert full["implemented"] == 7 and full["coverage_pct"] == 100.0
    assert full["gaps"] == []
    partial = principle_coverage(["a", "c"])
    assert partial["implemented"] == 2
    assert partial["coverage_pct"] == round(200 / 7, 2)
    assert "b" in partial["gaps"]


def test_art32_coverage_math():
    got = art32_coverage(["b"])
    assert got["implemented"] == 1 and got["coverage_pct"] == 25.0
    assert got["gaps"] == ["a", "c", "d"]


def test_duplicate_codes_count_once():
    assert principle_coverage(["a", "a", "a"])["implemented"] == 1


@pytest.mark.parametrize("call", [
    lambda: chapter_of(0),
    lambda: chapter_of(100),
    lambda: chapter_of("5"),
    lambda: chapter_of(True),
    lambda: principle_coverage(["g"]),
    lambda: art32_coverage(["accountability"]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(GDPRError):
        call()
