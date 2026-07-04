# SPDX-License-Identifier: Apache-2.0
"""Curation worklist over a local library directory of bundles.

Reports what the library is still missing — honestly, so the next curation
round is driven by gaps rather than vibes:

- ``candidates_pending_evidence`` — quarantined candidates that need a
  completed evidence script before they can ever become claims.
- ``missing_literature`` — verified bundles with no literature/ entry: the
  claim stands on its artifact, but its scholarly context is unsourced.
- ``missing_code`` — verified bundles whose generating code was not captured.

    python3 integrations/library/gaps.py --library build/library
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import BundleError, load_bundle  # noqa: E402


def gaps_report(library_dir: Path) -> dict:
    library_dir = Path(library_dir)
    report = {"n_bundles": 0, "invalid": [],
              "candidates_pending_evidence": [],
              "missing_literature": [], "missing_code": []}
    for bdir in sorted(p for p in library_dir.iterdir() if p.is_dir()):
        try:
            b = load_bundle(bdir)
        except (BundleError, OSError) as exc:
            report["invalid"].append({"dir": bdir.name, "error": str(exc)})
            continue
        report["n_bundles"] += 1
        cid = b["claim"].get("id", bdir.name)
        files = b["manifest"]["files"]
        if b["status"] == "candidate":
            report["candidates_pending_evidence"].append(cid)
            continue
        if not any(f.startswith("literature/") for f in files):
            report["missing_literature"].append(cid)
        if not any(f.startswith("code/") for f in files):
            report["missing_code"].append(cid)
    return report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = gaps_report(args.library)
    if args.json:
        print(json.dumps(rep, indent=2, sort_keys=True))
        return 0
    print(f"bundles: {rep['n_bundles']}  invalid: {len(rep['invalid'])}")
    for key in ("candidates_pending_evidence", "missing_literature",
                "missing_code"):
        for cid in rep[key]:
            print(f"[{key}] {cid}")
    for inv in rep["invalid"]:
        print(f"[INVALID] {inv['dir']}: {inv['error']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
