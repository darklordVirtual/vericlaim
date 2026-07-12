# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-INDEX-001 — the knowledge register, counted, not asserted.

claimlib is the knowledge-register half of vericlaim: reusable modules whose key
property is a claim, each citing the hash-locked literature it implements. This
script COUNTS that register — modules per language, literature works, citation
coverage — straight from MODULES.py and SOURCES.py (the same inputs the build
verifies), and writes the numbers to a committed artifact. The README binds to
that artifact; add a module or a work without regenerating and the gate fails.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "claimlib"))
sys.path.insert(0, str(ROOT / "claimlib" / "literature"))

from MODULES import MODULES  # noqa: E402
from SOURCES import SOURCES  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402

ARTIFACT = ROOT / "claims" / "claimlib_index.json"


def main() -> int:
    langs = {"python": 0, "typescript": 0, "react": 0}
    for mod in MODULES:
        langs[mod["lang"]] += 1
    cited = [m for m in MODULES if m.get("references")]
    payload = {
        "schema": "claimlib_index_v1",
        "modules_total": len(MODULES),
        "modules_python": langs["python"],
        "modules_typescript": langs["typescript"],
        "modules_react": langs["react"],
        "literature_works": len(SOURCES),
        "modules_cited": len(cited),
        "modules_uncited": len(MODULES) - len(cited),
        "citations_total": sum(len(m["references"]) for m in cited),
    }
    ARTIFACT.write_text(json.dumps(payload, indent=2) + "\n",
                        encoding="utf-8", newline="\n")
    stamp("claims/claimlib_index.json",
          script="python3 tools/claimlib_index_evidence.py")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
