# SPDX-License-Identifier: Apache-2.0
"""Enrich the claims library from ANY repo — one command, fully automatic.

    python3 integrations/library/enrich_repo.py --url <git-url> --out build/library \\
        [--push <worker-url> --token "$INDEX_TOKEN"] [--witness]

Pipeline: shallow-clone -> detect what the repo is -> preserve honestly:

- NATIVE  (has vericlaim.toml + register): its own gate runs and must be
  green; claims harvested with levels passing through unchanged.
- MAPPED  (a mappings/*.toml matches the repo name): harvested under that
  written-down curation policy — explicit level map, exclusions, caveats.
- UNGATED (anything else): assertion mining only; everything lands as
  ``status: candidate`` — quarantined, labeled in search, refused by import.
  Automation never inflates trust: an ungated repo cannot produce a
  verified claim, no matter how confident its README sounds.

If the repo carries a parseable reference list (auto-discovered: the
markdown file with the most `- Author (year). Title.` entries), the
bibliography-driven curation runs over the harvested claims with the strict
registrar/miscitation guard. With --push, bundles upload (server re-hashes
everything); with --witness, the ledger heads are re-witnessed afterwards —
commit and push claims/witness.jsonl to complete the anchor.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from biblio_curate import curate as biblio_curate_run  # noqa: E402
from biblio_curate import parse_bibliography  # noqa: E402
from extract_candidates import extract_repo  # noqa: E402
from harvest import harvest_repo  # noqa: E402

VERICLAIM_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAPPINGS = Path(__file__).resolve().parent / "mappings"


def _repo_name(url: str) -> str:
    name = url.rstrip("/").removesuffix(".git")
    return name.split("://")[-1]


def detect_source(root: Path, mappings_dir: Path,
                  url: str) -> tuple[str, dict]:
    """Classify a cloned repo: native / mapped / ungated (+ its config)."""
    root = Path(root)
    toml_path = root / "vericlaim.toml"
    if toml_path.exists():
        v = tomllib.loads(toml_path.read_text(encoding="utf-8")).get(
            "vericlaim", {})
        register = str(v.get("register", "claims/register.yaml"))
        if (root / register).exists():
            return "native", {
                "repo": _repo_name(url),
                "register": register,
                # run the source repo's own gate using OUR vericlaim (the
                # clone need not have it installed): PYTHONPATH is injected
                # in enrich() before harvest_repo shells out.
                "gate_cmd": f"{sys.executable} -m vericlaim",
                "level_map": {},
                "caveat_extra": ("Harvested from {repo}@{commit} (own vericlaim "
                                 "gate green at harvest)."
                                 .format(repo=_repo_name(url),
                                         commit="{commit}")),
            }
    name = _repo_name(url).lower()
    if mappings_dir.is_dir():
        for mpath in sorted(mappings_dir.glob("*.toml")):
            cfg = tomllib.loads(mpath.read_text(encoding="utf-8"))
            repo = str(cfg.get("repo", "")).lower()
            if repo and (repo in name or name.endswith(repo)):
                lit = {cid: [str(mpath.parent / p) for p in paths]
                       for cid, paths in (cfg.get("literature") or {}).items()}
                cfg["literature"] = lit
                return "mapped", cfg
    return "ungated", {"repo": _repo_name(url)}


def find_bibliography(root: Path) -> Path | None:
    """The repo's richest parseable reference list, if any."""
    root = Path(root)
    if not root.is_dir():
        return None
    best, best_n = None, 0
    for pattern in ("README.md", "*.md", "docs/**/*.md", "paper/**/*.md"):
        for p in root.glob(pattern):
            if not p.is_file():
                continue
            try:
                n = len(parse_bibliography(
                    p.read_text(encoding="utf-8", errors="replace")))
            except Exception:  # noqa: BLE001 — a bad file is just not a bib
                continue
            if n > best_n:
                best, best_n = p, n
    return best


def clone(url: str, cache_dir: Path) -> Path:
    dest = Path(cache_dir) / _repo_name(url).replace("/", "__")
    if dest.exists():
        subprocess.run(["git", "-C", str(dest), "pull", "--ff-only"],
                       check=False, capture_output=True)
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "clone", "--depth", "1", url, str(dest)],
                   check=True, capture_output=True, text=True)
    return dest


def enrich(root: Path, url: str, out: Path, *,
           mappings_dir: Path = DEFAULT_MAPPINGS,
           catalog: Path | None = None, notes: Path | None = None) -> dict:
    kind, cfg = detect_source(root, mappings_dir, url)
    print(f"[OK] {url} -> {kind}")
    result = {"kind": kind, "verified": 0, "candidates": 0, "bundles": {}}
    if kind == "ungated":
        bundles = extract_repo(root, out, cfg)
        result["candidates"] = len(bundles)
        print(f"[OK] {len(bundles)} QUARANTINED candidate(s) — an ungated "
              f"repo cannot produce verified claims")
    else:
        # native gate needs our vericlaim importable inside the clone
        env_prev = os.environ.get("PYTHONPATH", "")
        os.environ["PYTHONPATH"] = (str(VERICLAIM_ROOT) +
                                    (os.pathsep + env_prev if env_prev else ""))
        try:
            bundles = harvest_repo(root, out, cfg)
        finally:
            os.environ["PYTHONPATH"] = env_prev
        result["verified"] = len(bundles)
        bib = find_bibliography(root)
        if bib is not None and catalog is not None and notes is not None:
            print(f"[OK] bibliography found: {bib.relative_to(root)}")
            biblio_curate_run(bib, out, catalog, notes,
                              only_claims=set(bundles))
    result["bundles"] = bundles
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cache", type=Path,
                    default=Path(tempfile.gettempdir()) / "vericlaim-enrich")
    ap.add_argument("--catalog", type=Path,
                    default=Path(__file__).resolve().parent / "literature")
    ap.add_argument("--notes", type=Path,
                    default=Path(__file__).resolve().parent / "mappings" / "lit" / "auto")
    ap.add_argument("--push", metavar="WORKER_URL")
    ap.add_argument("--token")
    ap.add_argument("--witness", action="store_true")
    args = ap.parse_args()

    root = clone(args.url, args.cache)
    result = enrich(root, args.url, args.out,
                    catalog=args.catalog, notes=args.notes)
    print(f"[OK] enrich: {result['verified']} verified bundle(s), "
          f"{result['candidates']} candidate(s)")

    if args.push:
        if not args.token:
            print("error: --token required with --push", file=sys.stderr)
            return 2
        from push_bundles import push
        rc = push(args.out, args.push, args.token)
        if rc:
            return rc
        if args.witness:
            witness = VERICLAIM_ROOT / "integrations" / "cloudflare-ai" / "witness.py"
            subprocess.run([sys.executable, str(witness), "--record",
                            "--url", args.push], check=True,
                           cwd=VERICLAIM_ROOT)
            print("[NOTE] commit and push claims/witness.jsonl to complete "
                  "the public anchor.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
