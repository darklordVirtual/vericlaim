# SPDX-License-Identifier: Apache-2.0
"""Tests for registrar clients (arXiv, Crossref) — offline, on fixtures.

The anti-fabrication rule under test: bibliographic metadata comes ONLY from
parsing an authoritative registrar response. The parsers must extract ids,
titles, authors, venue and type faithfully, classify accreditation
(peer-reviewed venue vs preprint), and the ranker must be deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from litfetch import parse_arxiv_atom, parse_crossref, rank  # noqa: E402

ARXIV_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2410.09024v2</id>
    <title>AgentHarm: A Benchmark for Measuring Harmfulness of LLM Agents</title>
    <summary>We propose AgentHarm, a benchmark of harmful agent tasks...</summary>
    <published>2024-10-11T00:00:00Z</published>
    <author><name>Maksym Andriushchenko</name></author>
    <author><name>Alexandra Souly</name></author>
  </entry>
</feed>
"""

CROSSREF = """{
  "message": {
    "items": [
      {
        "DOI": "10.1214/20-aos1991",
        "type": "journal-article",
        "title": ["Time-uniform, nonparametric, nonasymptotic confidence sequences"],
        "author": [{"given": "Steven R.", "family": "Howard"},
                   {"given": "Aaditya", "family": "Ramdas"}],
        "container-title": ["The Annals of Statistics"],
        "issued": {"date-parts": [[2021]]},
        "abstract": "<jats:p>We develop confidence sequences...</jats:p>"
      }
    ]
  }
}"""


def test_arxiv_parser_extracts_verified_metadata():
    works = parse_arxiv_atom(ARXIV_ATOM.encode())
    assert len(works) == 1
    w = works[0]
    assert w["work_id"] == "arxiv:2410.09024"          # canonical, versionless
    assert w["title"].startswith("AgentHarm")
    assert w["authors"][0] == "Maksym Andriushchenko"
    assert w["year"] == 2024
    assert w["source_type"] == "preprint"
    assert w["accredited"] is False                     # preprint != peer-reviewed
    assert "benchmark of harmful agent tasks" in w["abstract"]
    assert w["url"] == "https://arxiv.org/abs/2410.09024"


def test_crossref_parser_extracts_verified_metadata():
    works = parse_crossref(CROSSREF.encode())
    assert len(works) == 1
    w = works[0]
    assert w["work_id"] == "doi:10.1214/20-aos1991"
    assert w["source_type"] == "journal-article"
    assert w["accredited"] is True                      # peer-reviewed venue
    assert w["venue"] == "The Annals of Statistics"
    assert w["year"] == 2021
    assert w["authors"] == ["Steven R. Howard", "Aaditya Ramdas"]
    assert "<jats:p>" not in w["abstract"]              # JATS markup stripped


def test_rank_is_deterministic_and_prefers_term_overlap():
    works = [
        {"work_id": "doi:x", "title": "Confidence sequences for monitoring",
         "abstract": "time-uniform anytime-valid bounds under optional stopping",
         "accredited": True},
        {"work_id": "doi:y", "title": "A survey of houseplants",
         "abstract": "watering schedules", "accredited": True},
    ]
    q = "anytime-valid time-uniform confidence sequence false accept monitoring"
    ranked = rank(q, works)
    assert [w["work_id"] for w, _ in ranked] == ["doi:x", "doi:y"]
    score_x = ranked[0][1]
    assert score_x > ranked[1][1]
    assert rank(q, works)[0][1] == score_x              # deterministic


def test_rank_gives_accredited_tiebreak():
    a = {"work_id": "doi:a", "title": "confidence sequences",
         "abstract": "", "accredited": True}
    b = {"work_id": "arxiv:b", "title": "confidence sequences",
         "abstract": "", "accredited": False}
    ranked = rank("confidence sequences", [b, a])
    assert ranked[0][0]["work_id"] == "doi:a"           # accredited first on tie
