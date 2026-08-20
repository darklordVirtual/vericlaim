# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the eval-harness domain.

    python3 domains/eval_harness/evidence.py

Deterministic: it scores the committed system-under-test against the committed
gold set and writes exactly the numbers the scorer computes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root
from vericlaim.evidence import emit, output_dir_arg  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from eval_harness import GOLD, PREDICTIONS, evaluate  # noqa: E402


def main() -> int:
    scores = evaluate(GOLD, PREDICTIONS)
    artifact = {"schema": "eval_harness_v1", **scores}
    out = Path(__file__).resolve().parent / "artifacts" / "eval_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    emit(json.dumps(artifact, indent=2) + "\n", out,
         script="python3 domains/eval_harness/evidence.py",
         output_dir=output_dir_arg())
    print(f"[OK] wrote {out}")
    for k, v in scores.items():
        print(f"     {k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
