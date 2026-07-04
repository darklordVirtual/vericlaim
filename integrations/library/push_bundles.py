# SPDX-License-Identifier: Apache-2.0
"""Push locally-built bundles to the Worker's /library/index endpoint.

Every bundle is verified locally (fail-closed) before upload; the Worker then
independently re-hashes every file and recomputes the bundle id on ingest, so
a corrupted upload cannot enter the library. Pushing is idempotent: bundles
are immutable and already-known ids are reported as unchanged.

    python3 integrations/library/push_bundles.py --library build/library \\
        --url https://vericlaim-claims.example.workers.dev --token "$INDEX_TOKEN"
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import load_bundle  # noqa: E402


def _payload_for(bdir: Path) -> dict:
    b = load_bundle(bdir)  # raises on any local tampering
    files = {rel: base64.b64encode((bdir / rel).read_bytes()).decode()
             for rel in b["manifest"]["files"]}
    return {"bundle_id": b["bundle_id"], "status": b["status"],
            "claim": b["claim"], "manifest": b["manifest"],
            "provenance": b["provenance"], "files": files}


def push(library_dir: Path, url: str, token: str) -> int:
    bundles = sorted(p for p in Path(library_dir).iterdir() if p.is_dir())
    stored = unchanged = rejected = 0
    for bdir in bundles:
        body = json.dumps({"bundles": [_payload_for(bdir)]}).encode()
        req = urllib.request.Request(
            url.rstrip("/") + "/library/index", data=body, method="POST",
            headers={"content-type": "application/json",
                     "authorization": f"Bearer {token}",
                     # A real UA: workers.dev bot heuristics 403 the default
                     # Python-urllib agent before the Worker ever runs.
                     "user-agent": "vericlaim-library-push/1"})
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
        stored += result.get("stored", 0)
        unchanged += result.get("unchanged", 0)
        for rej in result.get("rejected", []):
            rejected += 1
            print(f"[REJECTED] {rej['bundle_id'][:12]}: {rej['error']}",
                  file=sys.stderr)
    print(f"[OK] pushed: {stored} stored, {unchanged} unchanged, "
          f"{rejected} rejected of {len(bundles)} bundle(s)")
    return 1 if rejected else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--url", required=True)
    ap.add_argument("--token", required=True)
    args = ap.parse_args()
    return push(args.library, args.url, args.token)


if __name__ == "__main__":
    raise SystemExit(main())
