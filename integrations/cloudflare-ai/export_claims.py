#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Export a vericlaim register as the JSON the Cloudflare add-on ingests.

Zero extra dependencies — it reuses vericlaim's own loader, so the exported
claims are exactly what the gate verifies. By default it prints the payload to
stdout; with --push it POSTs to the Worker's /index endpoint.

    python3 export_claims.py                         # print {"claims": [...]}
    python3 export_claims.py --push https://vericlaim-claims.example.workers.dev \\
                            --token "$INDEX_TOKEN"    # rebuild the live index

Only claims are exported (id, statement, evidence_level, artifact, caveat,
metrics, literature). Search is a discovery aid over these; it does not change
what the gate proves.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from vericlaim.config import load_config
from vericlaim.register import load_register

FIELDS = ("id", "statement", "evidence_level", "artifact", "caveat", "metrics",
          "literature")


def _git_commit(root: Path) -> str | None:
    try:
        import subprocess
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip() or None
    except Exception:
        return None


def export(root: Path) -> list[dict]:
    cfg = load_config(root)
    claims = load_register(cfg.path(cfg.register).read_text(encoding="utf-8"))
    commit = _git_commit(root)
    out = []
    for c in claims:
        rec = {k: c[k] for k in FIELDS if k in c}
        if commit:
            rec["git_commit"] = commit
        # Attach the primary artifact's bytes (base64) for the content-addressed
        # evidence vault, so the ledger can prove exactly what backed the claim.
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        for rel in arts:
            f = cfg.path(rel)
            if f.exists() and f.is_file():
                import base64
                rec["artifact_b64"] = base64.b64encode(f.read_bytes()).decode()
                break
        out.append(rec)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", type=Path, help="repo root (has vericlaim.toml)")
    ap.add_argument("--push", metavar="URL", help="Worker base URL to POST /index to")
    ap.add_argument("--token", help="INDEX_TOKEN bearer secret (required with --push)")
    ap.add_argument("--no-gate", action="store_true",
                    help="skip the pre-push gate (NOT recommended; use only when "
                         "the gate was already run in this CI job)")
    args = ap.parse_args()

    claims = export(args.root)
    payload = {"claims": claims}

    if not args.push:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.token:
        print("error: --token is required with --push", file=sys.stderr)
        return 2

    # Never push an ungated register: refuse to publish a state the gate has
    # not accepted (audit P1 — the exporter is a publish step, so the same
    # fail-closed discipline applies). --no-gate is an explicit opt-out for
    # callers that already ran the gate in the same job.
    if not args.no_gate:
        try:
            from vericlaim.config import load_config
            from vericlaim.gate import run as run_gate
            if run_gate(load_config(args.root), quiet=True) != 0:
                print("error: gate failed — refusing to push an ungated register "
                      "(fix the drift, or pass --no-gate if already gated in CI)",
                      file=sys.stderr)
                return 3
        except Exception as exc:  # noqa: BLE001 — gate must not be silently skipped
            print(f"error: could not run the pre-push gate ({exc}); "
                  "pass --no-gate only if the gate already ran", file=sys.stderr)
            return 3
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        args.push.rstrip("/") + "/index", data=body, method="POST",
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {args.token}",
                 # A real User-Agent: Cloudflare's edge blocks the default
                 # "Python-urllib/..." UA with a 403 before the Worker runs.
                 "user-agent": "vericlaim-export/0.2.0"})
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
