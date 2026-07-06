# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the multi-tenant isolation domain.

    python3 domains/multitenant/evidence.py
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))              # repo root
sys.path.insert(0, str(HERE / "src"))
from multitenant import run_isolation_battery  # noqa: E402


def main() -> int:
    report = run_isolation_battery()
    artifact = {"schema": "multitenant_v1", **asdict(report)}
    out = HERE / "artifacts" / "isolation_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    from vericlaim.provenance import stamp
    stamp(out, script="python3 domains/multitenant/evidence.py")
    print(f"[OK] wrote {out}")
    for k, v in asdict(report).items():
        print(f"     {k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
