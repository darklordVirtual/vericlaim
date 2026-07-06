# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the domain-ontologies module.

    python3 domains/ontologies/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))              # repo root
sys.path.insert(0, str(HERE / "src"))
from ontology import validate  # noqa: E402


def main() -> int:
    fixture = json.loads((HERE / "data" / "sample_register.json").read_text())
    result = validate(fixture["claims"])
    artifact = {"schema": "ontology_v1", **result}
    out = HERE / "artifacts" / "ontology_conformance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    from vericlaim.provenance import stamp
    stamp(out, script="python3 domains/ontologies/evidence.py")
    print(f"[OK] wrote {out}")
    for k, v in result.items():
        print(f"     {k}={v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
