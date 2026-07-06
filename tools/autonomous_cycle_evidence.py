# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-RSI-002: autonomous drift is bounded.

Runs the end-to-end autonomous cycle (tools/autonomous_cycle_demo.run_demo) on a
throwaway repo and records that all 8 safety properties hold — safe development
admitted, every drift vector blocked, real gate fails closed on corruption.
Writes claims/autonomous_cycle.json.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from autonomous_cycle_demo import run_demo  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402

ART = Path(__file__).resolve().parents[1] / "claims" / "autonomous_cycle.json"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="vericlaim-autocycle-") as tmp:
        # Silence the inner scaffold/gate chatter; we only record the verdicts.
        with contextlib.redirect_stdout(io.StringIO()):
            result = run_demo(Path(tmp))
    props = {k: v for k, v in result.items() if k != "ALL_SAFE"}
    artifact = {
        "schema": "autonomous_cycle_v1",
        "properties_checked": len(props),
        "failures": sum(1 for v in props.values() if not v),
        "all_safe": bool(result["ALL_SAFE"]),
    }
    ART.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    stamp(ART, script="python3 tools/autonomous_cycle_evidence.py")
    print(f"[OK] wrote {ART}")
    for k, v in artifact.items():
        if k != "schema":
            print(f"     {k}={v}")
    return 0 if artifact["failures"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
