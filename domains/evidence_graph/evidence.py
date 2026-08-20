# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the evidence-graph domain.

    python3 domains/evidence_graph/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))              # repo root
sys.path.insert(0, str(HERE / "src"))
from vericlaim.evidence import emit, output_dir_arg  # noqa: E402
from evidence_graph import build_graph, metrics  # noqa: E402


def main() -> int:
    fixture = json.loads((HERE / "data" / "sample_claims.json").read_text())
    g = build_graph(fixture["claims"])
    artifact = {"schema": "evidence_graph_v1", **metrics(g)}
    out = HERE / "artifacts" / "graph.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    emit(json.dumps(artifact, indent=2) + "\n", out,
         script="python3 domains/evidence_graph/evidence.py",
         output_dir=output_dir_arg())
    print(f"[OK] wrote {out}")
    for k, v in metrics(g).items():
        print(f"     {k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
