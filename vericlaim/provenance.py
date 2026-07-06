# SPDX-License-Identifier: Apache-2.0
"""Provenance for artifacts — where a number came from.

AI fabricates confidently. Existence of a file is not enough; you want to know
*how it was produced*. A provenance sidecar records the script, the commit, the
artifact's own SHA-256, and who/what produced each artifact.

This is provenance *recording* — a lightweight cousin of the SLSA / in-toto
attestation idea, scaled to a single JSON file. It is NOT cryptographic
attestation: the sidecar is not signed and `git_commit` is best-effort. Signed
DSSE envelopes (Sigstore / GitHub OIDC) are a deliberate enterprise-tier
extension, not a claim this file makes today.

Evidence scripts call `stamp()` after writing their artifact. The gate can then
require that every claimed artifact carries provenance (config
`require_provenance = true`).

Provenance sidecars are metadata, not evidence: they are not hashed in the
manifest and not compared by `vericlaim reproduce` (only the real artifact is).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SUFFIX = ".provenance.json"


def _git_commit(cwd: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=cwd, check=True,
        )
        return out.stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def sidecar_path(artifact: Path) -> Path:
    return artifact.with_name(artifact.name + SUFFIX)


def stamp(artifact: str | Path, *, script: str, produced_by: str = "human") -> Path:
    """Write a provenance sidecar next to *artifact* and return its path.

    Call this at the end of an evidence script:
        stamp("results/bench.json", script="python examples/rle/bench.py")
    """
    art = Path(artifact)
    art_sha = (hashlib.sha256(art.read_bytes()).hexdigest()
               if art.exists() else None)
    out = sidecar_path(art)
    # Idempotent re-stamp: if the artifact bytes are unchanged, preserve the
    # existing timestamp and commit so re-running an evidence script (or
    # `vericlaim reproduce`) does not churn the sidecar and dirty the working
    # tree. The stamp only moves when the artifact it describes actually moved.
    prev = load(art)
    if (prev is not None and art_sha is not None
            and prev.get("artifact_sha256") == art_sha
            and prev.get("script") == script
            and prev.get("produced_by") == produced_by):
        generated_at = prev.get("generated_at", datetime.now(timezone.utc).isoformat())
        git_commit = prev.get("git_commit")
    else:
        generated_at = datetime.now(timezone.utc).isoformat()
        git_commit = _git_commit(art.resolve().parent)
    record = {
        "schema": "vericlaim_provenance_v2",
        "artifact": art.name,
        "artifact_sha256": art_sha,   # what was produced (self-describing)
        "script": script,             # how it was produced
        "git_commit": git_commit,
        "generated_at": generated_at,
        "produced_by": produced_by,
    }
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return out


def load(artifact: str | Path) -> dict | None:
    """Read the provenance sidecar for *artifact*, or None if absent/invalid."""
    p = sidecar_path(Path(artifact))
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
