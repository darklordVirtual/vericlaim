# SPDX-License-Identifier: Apache-2.0
"""Shared helpers for claimlib evidence scripts (NOT vendored — only each
module's own <name>.py ships in a bundle).

Keeps every artifact byte-reproducible across OSes: JSON is written with LF
endings (Windows text mode would inject CRLF and break the provenance hash),
and provenance is stamped with the canonical vericlaim stamper.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from vericlaim.provenance import stamp  # noqa: E402


def write_json_lf(path: Path, obj: dict) -> str:
    """Write *obj* as pretty JSON with LF endings; return its sha256 hex."""
    text = json.dumps(obj, indent=2, sort_keys=True) + "\n"
    Path(path).write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def emit(artifact_path: Path, obj: dict, *, script: str) -> str:
    """Write an evidence artifact + its provenance sidecar. Returns sha256.

    *script* is the repo-relative command that reproduces it, e.g.
    ``python3 claimlib/modules/cvss/evidence.py``.
    """
    artifact_path = Path(artifact_path)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    sha = write_json_lf(artifact_path, obj)
    stamp(artifact_path, script=script, produced_by="claimlib")
    return sha
