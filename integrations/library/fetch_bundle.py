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
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for vericlaim.*
from bundlefmt import verify_bundle  # noqa: E402
from vericlaim.pathsafe import PathSafetyError, check_bundle_id, safe_join  # noqa: E402


def _get(url: str) -> bytes:
    # A real UA: workers.dev bot heuristics 403 the default Python-urllib
    # agent before the Worker ever runs.
    req = urllib.request.Request(
        url, headers={"user-agent": "vericlaim-library-fetch/1"})
    with urllib.request.urlopen(req) as resp:
        return resp.read()


def fetch(url: str, bundle_id: str, out_root: Path) -> Path:
    base = url.rstrip("/")
    # The bundle id names a directory — it is UNTRUSTED input. Validate it as
    # strict sha256 hex before it ever touches the filesystem.
    check_bundle_id(bundle_id)
    meta = json.loads(_get(f"{base}/library/bundle/{bundle_id}"))
    files = meta.get("manifest", {}).get("files")
    if not isinstance(files, dict):
        raise ValueError("bundle response has no manifest.files map")

    out_root = Path(out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    final = out_root / bundle_id
    # Download into a PRIVATE staging dir named <bundle_id>, so a manifest path
    # can never be written before it is validated and the bundle verified. Every
    # manifest key is resolved with safe_join (rejects ../, absolute, backslash,
    # Windows drive, symlink escape) BEFORE any byte is written. The staging dir
    # is created INSIDE out_root (same filesystem) so the final move is a true
    # atomic rename, not a cross-filesystem copy+delete.
    staging_parent = Path(tempfile.mkdtemp(prefix=".vericlaim-fetch-", dir=out_root))
    stage = staging_parent / bundle_id
    stage.mkdir(parents=True)
    try:
        for rel, sha in files.items():
            try:
                dest = safe_join(stage, str(rel))
            except PathSafetyError as exc:
                raise ValueError(f"unsafe manifest path {rel!r}: {exc}") from exc
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(_get(f"{base}/library/file/{sha}"))
        (stage / "MANIFEST.json").write_text(
            json.dumps(meta["manifest"], sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
        report = verify_bundle(stage)  # fail-closed: raises on any mismatch
        if final.exists():
            shutil.rmtree(final)
        shutil.move(str(stage), str(final))  # same filesystem -> atomic rename
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)
    bdir = final
    print(f"[OK] fetched + locally verified bundle {report['bundle_id'][:12]}… "
          f"({report['n_files']} files, status {report['status']}) -> {bdir}")
    if meta.get("superseded_by"):
        print(f"[NOTE] SUPERSEDED: a newer version of this claim exists — "
              f"bundle {str(meta['superseded_by'])[:12]}… ; prefer it unless "
              f"you are auditing history.")
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
