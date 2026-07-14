# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-META-001 — the project's own version, single-sourced.

vericlaim's most embarrassing possible bug is a version string that drifts
across pyproject.toml, __init__.py, CITATION.cff and the README — the exact
failure the tool exists to prevent. This script makes the version a first-class
claim: it reads the SINGLE source of truth (vericlaim.__version__) and writes it
to a committed artifact. The README binds to that artifact; a test
(test_version_consistency) holds the other files to it. Version drift then fails
the gate like any other drift.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from vericlaim import __version__  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402

ARTIFACT = ROOT / "claims" / "version.json"


def main() -> int:
    ARTIFACT.write_text(
        json.dumps({"version": __version__}, indent=2) + "\n",
        encoding="utf-8", newline="\n")
    stamp("claims/version.json", script="python3 tools/version_evidence.py")
    print(f"version = {__version__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
