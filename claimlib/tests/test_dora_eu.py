# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the dora_eu module (Regulation (EU) 2022/2554)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MOD_DIR = Path(__file__).resolve().parents[1] / "modules" / "dora_eu"
_spec = importlib.util.spec_from_file_location(
    "claimlib_dora_eu", _MOD_DIR / "dora_eu.py")
_m = importlib.util.module_from_spec(_spec)
sys.modules["claimlib_dora_eu"] = _m
_spec.loader.exec_module(_m)

DORAError = _m.DORAError
CHAPTERS = _m.CHAPTERS
PILLARS = _m.PILLARS
N_ARTICLES = _m.N_ARTICLES
chapter_of = _m.chapter_of
pillar_of = _m.pillar_of
pillar_coverage = _m.pillar_coverage


def test_chapters_partition_all_articles():
    for article in range(1, N_ARTICLES + 1):
        owners = [ch for ch, (_, lo, hi) in CHAPTERS.items()
                  if lo <= article <= hi]
        assert len(owners) == 1


def test_structure_counts():
    assert len(CHAPTERS) == 9
    assert N_ARTICLES == 64
    assert len(PILLARS) == 5


@pytest.mark.parametrize("article,chapter", [
    (1, 1), (5, 2), (16, 2), (17, 3), (23, 3), (24, 4), (27, 4),
    (28, 5), (44, 5), (45, 6), (46, 7), (56, 7), (57, 8), (58, 9), (64, 9),
])
def test_known_articles_resolve(article, chapter):
    assert chapter_of(article) == chapter


def test_pillar_names_match_chapter_titles():
    for meta in PILLARS.values():
        assert meta["name"] == CHAPTERS[meta["chapter"]][0]


def test_pillar_of_boundaries():
    assert pillar_of(5) == "ict_risk"
    assert pillar_of(45) == "info_sharing"
    assert pillar_of(1) is None
    assert pillar_of(64) is None


def test_pillar_coverage_math():
    assert pillar_coverage(list(PILLARS))["coverage_pct"] == 100.0
    got = pillar_coverage(["testing"])
    assert got["implemented"] == 1 and got["coverage_pct"] == 20.0
    assert "ict_risk" in got["gaps"]


@pytest.mark.parametrize("call", [
    lambda: chapter_of(0),
    lambda: chapter_of(65),
    lambda: chapter_of(True),
    lambda: pillar_coverage(["cyber"]),
])
def test_invalid_inputs_rejected(call):
    with pytest.raises(DORAError):
        call()
