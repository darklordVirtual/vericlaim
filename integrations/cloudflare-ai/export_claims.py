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
metrics). Search is a discovery aid over these; it does not change what the
gate proves.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from vericlaim.config import load_config
from vericlaim.register import load_register

FIELDS = ("id", "statement", "evidence_level", "artifact", "caveat", "metrics")


def export(root: Path) -> list[dict]:
    cfg = load_config(root)
    claims = load_register(cfg.path(cfg.register).read_text(encoding="utf-8"))
    out = []
    for c in claims:
        out.append({k: c[k] for k in FIELDS if k in c})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", type=Path, help="repo root (has vericlaim.toml)")
    ap.add_argument("--push", metavar="URL", help="Worker base URL to POST /index to")
    ap.add_argument("--token", help="INDEX_TOKEN bearer secret (required with --push)")
    args = ap.parse_args()

    claims = export(args.root)
    payload = {"claims": claims}

    if not args.push:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    if not args.token:
        print("error: --token is required with --push", file=sys.stderr)
        return 2
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        args.push.rstrip("/") + "/index", data=body, method="POST",
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {args.token}",
                 # A real User-Agent: Cloudflare's edge blocks the default
                 # "Python-urllib/..." UA with a 403 before the Worker runs.
                 "user-agent": "vericlaim-export/0.1.4"})
    with urllib.request.urlopen(req) as resp:
        print(resp.read().decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
