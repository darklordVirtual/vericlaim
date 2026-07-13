# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the tip calculator.

Runs every reference case through the function and records how many produce the
expected total. Deterministic.

    python examples/tipcalc/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for `import vericlaim`
sys.path.insert(0, str(HERE / "src"))
sys.path.insert(0, str(HERE))
from cases import CASES  # noqa: E402
from tipcalc import total_with_tip  # noqa: E402


def main() -> int:
    results = []
    passing = 0
    for bill, tip, expected in CASES:
        got = total_with_tip(bill, tip)
        ok = got == expected
        passing += int(ok)
        results.append({"bill": bill, "tip_percent": tip,
                        "expected": expected, "got": got, "pass": ok})
    artifact = {
        "schema": "tipcalc_v1",
        "cases_total": len(CASES),
        "cases_passing": passing,
        "cases": results,
    }
    out = HERE / "artifacts" / "tipcalc.json"
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8",
                   newline="\n")
    from vericlaim.provenance import stamp
    stamp(out, script="python3 examples/tipcalc/evidence.py")
    print(f"[OK] wrote {out}")
    print(f"     cases_passing={passing}/{len(CASES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
