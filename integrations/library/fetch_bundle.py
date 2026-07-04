# SPDX-License-Identifier: Apache-2.0
"""Fetch a bundle from the Worker library and verify it locally.

The library is DISTRIBUTION, not truth: after download, the bundle is
reassembled on disk and verified with bundlefmt.verify_bundle — every file
against the manifest, the manifest against the bundle id, the id against the
directory name. Only then is it safe to `import_bundle` into a project.

    python3 integrations/library/fetch_bundle.py --url https://... \\
        --bundle <bundle_id> --out build/fetched
    python3 integrations/library/import_bundle.py \\
        --bundle build/fetched/<bundle_id> --target .
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import verify_bundle  # noqa: E402


def _get(url: str) -> bytes:
    # A real UA: workers.dev bot heuristics 403 the default Python-urllib
    # agent before the Worker ever runs.
    req = urllib.request.Request(
        url, headers={"user-agent": "vericlaim-library-fetch/1"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def fetch(url: str, bundle_id: str, out_root: Path) -> Path:
    base = url.rstrip("/")
    meta = json.loads(_get(f"{base}/library/bundle/{bundle_id}"))
    bdir = Path(out_root) / bundle_id
    for rel, sha in meta["manifest"]["files"].items():
        dest = bdir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(_get(f"{base}/library/file/{sha}"))
    (bdir / "MANIFEST.json").write_text(
        json.dumps(meta["manifest"], sort_keys=True, indent=2) + "\n",
        encoding="utf-8")
    report = verify_bundle(bdir)  # fail-closed: raises on any mismatch
    print(f"[OK] fetched + locally verified bundle {report['bundle_id'][:12]}… "
          f"({report['n_files']} files, status {report['status']}) -> {bdir}")
    if report["status"] != "verified":
        print("[NOTE] status is not 'verified' — this bundle is a quarantined "
              "candidate and cannot be imported as a claim.")
    return bdir


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    fetch(args.url, args.bundle, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
