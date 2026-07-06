# SPDX-License-Identifier: Apache-2.0
"""Evidence-graph builder: integrity queries and artifact agreement."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domains" / "evidence_graph" / "src"))
from evidence_graph import build_graph, metrics, orphan_claims  # noqa: E402

FIXTURE = json.loads(
    (ROOT / "domains/evidence_graph/data/sample_claims.json").read_text())["claims"]


def test_metrics_match_artifact():
    art = json.loads((ROOT / "domains/evidence_graph/artifacts/graph.json").read_text())
    for k, v in metrics(build_graph(FIXTURE)).items():
        assert art[k] == v


def test_orphan_claim_is_detected():
    g = build_graph([{"id": "X", "artifacts": [], "literature": [], "docs": ["d"]}])
    assert orphan_claims(g) == ["X"]
    assert metrics(g)["orphan_claims"] == 1


def test_shared_artifact_is_one_node():
    # CLAIM-A and CLAIM-E both cite a.json -> a single artifact node, two edges.
    g = build_graph(FIXTURE)
    art_nodes = [n for n in g.nodes if n[0] == "artifact" and n[1] == "a.json"]
    assert len(art_nodes) == 1
