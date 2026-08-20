# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the cost-aware routing domain.

    python3 domains/cost_routing/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))              # repo root
sys.path.insert(0, str(HERE / "src"))
from vericlaim.evidence import emit, output_dir_arg  # noqa: E402
from cost_routing import MODELS, WORKLOAD, route  # noqa: E402


def main() -> int:
    result = route(MODELS, WORKLOAD)
    artifact = {"schema": "cost_routing_v1", **result}
    out = HERE / "artifacts" / "routing_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    emit(json.dumps(artifact, indent=2) + "\n", out,
         script="python3 domains/cost_routing/evidence.py",
         output_dir=output_dir_arg())
    print(f"[OK] wrote {out}")
    for k, v in result.items():
        if k != "decisions":
            print(f"     {k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
