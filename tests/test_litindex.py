# SPDX-License-Identifier: Apache-2.0
"""Tests for the literature catalog — the systematic overview.

One deduplicated record per work (keyed by canonical registrar id), abstract
text content-addressed by sha256, claim<->work links carrying the match
method and score, fail-closed integrity verification, and a coverage report
that makes the state of the literature visible at a glance.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from litindex import add_work, link, render_note, report, verify  # noqa: E402

WORK = {"work_id": "doi:10.1214/20-aos1991", "registrar": "crossref",
        "title": "Time-uniform confidence sequences",
        "abstract": "We develop confidence sequences...",
        "authors": ["Steven R. Howard", "Aaditya Ramdas"],
        "year": 2021, "venue": "The Annals of Statistics",
        "source_type": "journal-article", "accredited": True,
        "url": "https://doi.org/10.1214/20-aos1991"}
RETRIEVAL = {"query": "confidence sequences", "retrieved_at": "2026-07-04T21:00:00+00:00"}


def test_add_work_is_deduplicated_and_content_addressed(tmp_path):
    fsid1 = add_work(tmp_path, WORK, RETRIEVAL)
    fsid2 = add_work(tmp_path, {**WORK, "abstract": "changed later"}, RETRIEVAL)
    assert fsid1 == fsid2                       # same canonical id -> one record
    works = list((tmp_path / "works").glob("*.json"))
    assert len(works) == 1
    texts = list((tmp_path / "texts").glob("*.txt"))
    assert len(texts) == 1                      # first snapshot wins
    assert texts[0].stem in works[0].read_text()  # text sha recorded in work


def test_link_and_report_coverage(tmp_path):
    add_work(tmp_path, WORK, RETRIEVAL)
    link(tmp_path, "CLAIM-011", WORK["work_id"], method="auto:lexical",
         score=0.62, ts="2026-07-04T21:01:00+00:00")
    rep = report(tmp_path, claims=["CLAIM-011", "CLAIM-001"])
    assert rep["n_works"] == 1 and rep["n_links"] == 1
    assert rep["coverage"]["CLAIM-011"] == [WORK["work_id"]]
    assert rep["coverage"]["CLAIM-001"] == []   # the gap stays visible
    assert rep["accredited_works"] == 1


def test_verify_catches_tampered_text_and_dangling_link(tmp_path):
    add_work(tmp_path, WORK, RETRIEVAL)
    link(tmp_path, "C-1", WORK["work_id"], method="m", score=1.0, ts="t")
    assert verify(tmp_path) == []
    txt = next((tmp_path / "texts").glob("*.txt"))
    txt.write_text("tampered")
    problems = verify(tmp_path)
    assert problems and "hash" in problems[0]
    link(tmp_path, "C-2", "doi:does-not-exist", method="m", score=1.0, ts="t")
    assert any("does-not-exist" in p for p in verify(tmp_path))


def test_render_note_is_honest_about_method(tmp_path):
    add_work(tmp_path, WORK, RETRIEVAL)
    link(tmp_path, "CLAIM-011", WORK["work_id"], method="auto:lexical",
         score=0.62, ts="2026-07-04T21:01:00+00:00")
    note = render_note(tmp_path, "CLAIM-011")
    assert "AUTO-CURATED" in note
    assert "does not prove" in note.lower()
    assert "score 0.62" in note
    assert "The Annals of Statistics" in note    # verified venue, not invented
    assert "10.1214/20-aos1991" in note
