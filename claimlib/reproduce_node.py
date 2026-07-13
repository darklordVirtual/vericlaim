# SPDX-License-Identifier: Apache-2.0
"""Declarative-reproduce shim for claimlib's TS/React evidence.

Node evidence prints its metrics JSON on stdout (build.py persists it as the
artifact). The declarative reproduce runner instead needs the artifact
CREATED inside an isolated ``--output-dir``; this shim runs the node evidence
and writes the artifact there with byte-identical formatting to build.py.

    python3 claimlib/reproduce_node.py <module_name> --output-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from MODULES import MODULES  # noqa: E402
from _util import write_json_lf  # noqa: E402

LANG = {
    "typescript": {"subdir": "ts", "evidence": "evidence.ts"},
    "react": {"subdir": "react", "evidence": "evidence.ts"},
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    mod = next((m for m in MODULES if m["name"] == args.module), None)
    if mod is None or mod.get("lang", "python") == "python":
        raise SystemExit(f"[repro-node] no node module named {args.module!r}")
    lg = LANG[mod["lang"]]
    ev = HERE / lg["subdir"] / mod["name"] / lg["evidence"]
    proc = subprocess.run(["node", str(ev)], capture_output=True, text=True,
                          cwd=HERE.parent)
    if proc.returncode != 0:
        raise SystemExit(f"[repro-node] evidence for {mod['name']} exited "
                         f"{proc.returncode}:\n{proc.stdout}{proc.stderr}")
    obj = json.loads(proc.stdout.strip().splitlines()[-1])
    write_json_lf(Path(args.output_dir) / mod["artifact"], obj)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
