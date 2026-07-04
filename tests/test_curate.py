# SPDX-License-Identifier: Apache-2.0
"""Tests for the curation pipeline glue (query building + selection)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from curate_literature import build_query, select  # noqa: E402


def test_build_query_prefers_config_override():
    claim = {"id": "C-1", "statement": "REMORA blocks 208 harmful scenarios"}
    assert build_query(claim, {"C-1": "agent safety benchmark"}) == \
        "agent safety benchmark"


def test_build_query_derives_content_words_deterministically():
    claim = {"id": "C-2", "statement":
             "The parser handles all of the 700 adversarial tool-call "
             "benchmark tasks with a deterministic policy gate"}
    q1, q2 = build_query(claim, {}), build_query(claim, {})
    assert q1 == q2
    assert "adversarial" in q1 and "the" not in q1.split()


def test_select_applies_threshold_and_topk_and_reports_dropped():
    ranked = [({"work_id": "doi:a"}, 0.61), ({"work_id": "doi:b"}, 0.42),
              ({"work_id": "arxiv:c"}, 0.12)]
    chosen, dropped = select(ranked, min_score=0.25, topk=2)
    assert [w["work_id"] for w, _ in chosen] == ["doi:a", "doi:b"]
    assert [w["work_id"] for w, _ in dropped] == ["arxiv:c"]  # visible, not silent
