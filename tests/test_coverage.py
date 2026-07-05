# SPDX-License-Identifier: Apache-2.0
"""Tests for coverage — canon vs catalog, fail-closed.

Every canon entry must be matched to a registrar-verified work in the
catalog OR documented as a drop with a reason. The matcher reuses the
titles-agree guard plus author-surname and year checks, because title
overlap alone let imitations through live (the Guo-2017 lesson).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import litcoverage as coverage  # noqa: E402
from litindex import add_work, link  # noqa: E402

GUO = {"id": "guo-2017", "collection": "01_uncertainty_and_routing",
       "title": "On Calibration of Modern Neural Networks",
       "authors": ["Guo"], "year": 2017, "kind": "paper",
       "registrar": "arxiv", "p0": True, "top15": False}

GUO_WORK = {"work_id": "arxiv:1706.04599", "registrar": "arxiv",
            "title": "On calibration of modern neural networks",
            "abstract": "Confidence calibration...",
            "authors": ["Chuan Guo", "Geoff Pleiss"], "year": 2017,
            "venue": "arXiv", "source_type": "preprint", "accredited": False,
            "url": "https://arxiv.org/abs/1706.04599"}


def test_match_requires_title_author_and_year():
    works = {"arxiv:1706.04599": dict(GUO_WORK)}
    assert coverage.match(GUO, works) == "arxiv:1706.04599"
    # wrong year: the 1989 sensor-paper failure mode
    works["arxiv:1706.04599"]["year"] = 1989
    assert coverage.match(GUO, works) is None
    # right year, wrong authors
    works["arxiv:1706.04599"]["year"] = 2017
    works["arxiv:1706.04599"]["authors"] = ["A. Stranger"]
    assert coverage.match(GUO, works) is None


def test_match_yearless_canon_entry_ignores_year():
    entry = dict(GUO, year=None)
    works = {"arxiv:1706.04599": dict(GUO_WORK, year=1989)}
    assert coverage.match(entry, works) == "arxiv:1706.04599"


def _setup_catalog(tmp_path: Path) -> Path:
    litroot = tmp_path / "literature"
    add_work(litroot, GUO_WORK, {"method": "test"})
    return litroot


def _canon_file(tmp_path: Path, extra: str = "") -> Path:
    p = tmp_path / "canon.toml"
    p.write_text("""
[[work]]
id = "guo-2017"
collection = "01_uncertainty_and_routing"
title = "On Calibration of Modern Neural Networks"
authors = ["Guo"]
year = 2017
kind = "paper"
registrar = "arxiv"

[[work]]
id = "iso-42001"
collection = "05_ai_governance"
title = "ISO/IEC 42001:2023 Artificial intelligence management system"
authors = ["ISO"]
year = 2023
kind = "standard"
registrar = "web"
""" + extra, encoding="utf-8")
    return p


def test_report_marks_gaps_and_check_fails_on_them(tmp_path):
    litroot = _setup_catalog(tmp_path)
    drops = tmp_path / "drops.toml"
    drops.write_text("drop = []\n", encoding="utf-8")
    rep = coverage.report(litroot, _canon_file(tmp_path), drops, None)
    assert rep["entries"]["guo-2017"]["verified"] is True
    assert rep["entries"]["iso-42001"]["verified"] is False
    failures = coverage.check(rep)
    assert failures == ["iso-42001"]


def test_documented_drop_is_not_a_failure(tmp_path):
    litroot = _setup_catalog(tmp_path)
    drops = tmp_path / "drops.toml"
    drops.write_text('[[drop]]\nid = "iso-42001"\n'
                     'reason = "no registrar record; paywalled standard"\n',
                     encoding="utf-8")
    rep = coverage.report(litroot, _canon_file(tmp_path), drops, None)
    assert coverage.check(rep) == []
    assert rep["drops"]["iso-42001"].startswith("no registrar")


def test_drop_without_reason_is_rejected(tmp_path):
    litroot = _setup_catalog(tmp_path)
    drops = tmp_path / "drops.toml"
    drops.write_text('[[drop]]\nid = "iso-42001"\nreason = ""\n',
                     encoding="utf-8")
    try:
        coverage.report(litroot, _canon_file(tmp_path), drops, None)
    except ValueError as e:
        assert "iso-42001" in str(e)
    else:
        raise AssertionError("empty drop reason must be rejected")


def test_pipeline_columns(tmp_path):
    litroot = _setup_catalog(tmp_path)
    # fulltext marker on the record
    fsid = "arxiv_1706-04599"
    wpath = litroot / "works" / f"{fsid}.json"
    rec = json.loads(wpath.read_text())
    rec["fulltext_sha256"] = "ab" * 32
    wpath.write_text(json.dumps(rec))
    # chunk manifest with two shas
    chunks = litroot / "chunks"
    chunks.mkdir()
    (chunks / f"{fsid}.jsonl").write_text(
        '{"fsid": "%s", "source_sha256": "%s", "target": 1200, "overlap": 200, "n": 2}\n'
        '{"seq": 0, "section": "", "sha256": "aa"}\n'
        '{"seq": 1, "section": "", "sha256": "bb"}\n' % (fsid, "ab" * 32))
    # push manifest covering only one sha -> not fully vectorized
    push = tmp_path / "push_manifest.jsonl"
    push.write_text('{"sha": "aa", "pushed_at": "2026-07-05"}\n')
    link(litroot, "CLAIM-XYZ", "arxiv:1706.04599",
         method="curator:manual", score=1.0, ts="2026-07-05")
    drops = tmp_path / "drops.toml"
    drops.write_text("drop = []\n")
    rep = coverage.report(litroot, _canon_file(tmp_path), drops, push)
    e = rep["entries"]["guo-2017"]
    assert e["fulltext"] is True and e["chunked"] is True
    assert e["vectorized"] is False  # bb was never pushed
    assert e["claim_linked"] is True
    push.write_text('{"sha": "aa"}\n{"sha": "bb"}\n')
    rep = coverage.report(litroot, _canon_file(tmp_path), drops, push)
    assert rep["entries"]["guo-2017"]["vectorized"] is True
