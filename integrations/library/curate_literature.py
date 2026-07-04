# SPDX-License-Identifier: Apache-2.0
"""Automated literature curation: find registrar-verified works for claims.

For every claim that lacks literature, this pipeline

1. builds a search query (explicit per-claim override in the mapping config
   wins; otherwise content words derived deterministically from the statement),
2. queries arXiv + Crossref (litfetch — metadata is registrar-verified,
   never model-recalled, with accreditation labeled honestly),
3. ranks candidates with the deterministic lexical scorer, keeps the top-k
   above a threshold, and REPORTS what it dropped — no silent caps,
4. records works and claim<->work links in the hash-locked catalog
   (litindex), and
5. writes an AUTO-CURATED note per claim for the next bundle harvest.

What automation cannot do is stated in every note it writes: a lexical match
supports *context*; it never proves a claim, and it is not a human judgment.
Curators upgrade links (method curator:manual) when they read the works.

    python3 integrations/library/curate_literature.py \\
        --library build/library --catalog integrations/library/literature \\
        --config integrations/library/mappings/remora.toml \\
        --notes integrations/library/mappings/lit/auto
"""
from __future__ import annotations

import argparse
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import load_bundle  # noqa: E402
from litfetch import _tokens, rank, search_all  # noqa: E402
from litindex import add_work, link, render_note, verify  # noqa: E402


def build_query(claim: dict, overrides: dict[str, str]) -> str:
    """Config override wins; otherwise the statement's distinctive content
    words, in order of first appearance (deterministic)."""
    cid = claim.get("id", "")
    if cid in overrides:
        return overrides[cid]
    seen: list[str] = []
    keep = _tokens(claim.get("statement", ""))
    for word in str(claim.get("statement", "")).lower().split():
        w = word.strip(".,;:()[]%")
        if w in keep and w not in seen and not w.isdigit():
            seen.append(w)
        if len(seen) >= 8:
            break
    return " ".join(seen)


def select(ranked: list[tuple[dict, float]], *, min_score: float,
           topk: int) -> tuple[list, list]:
    """Split ranked works into (chosen, dropped) — dropped stays visible."""
    chosen = [(w, s) for w, s in ranked if s >= min_score][:topk]
    chosen_ids = {w["work_id"] for w, _ in chosen}
    dropped = [(w, s) for w, s in ranked if w["work_id"] not in chosen_ids]
    return chosen, dropped


def curate(library_dir: Path, catalog: Path, cfg: dict, notes_dir: Path, *,
           min_score: float = 0.25, topk: int = 2,
           only_claims: set[str] | None = None) -> dict:
    overrides = cfg.get("lit_queries") or {}
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary: dict[str, dict] = {}
    for bdir in sorted(p for p in Path(library_dir).iterdir() if p.is_dir()):
        b = load_bundle(bdir)
        cid = b["claim"].get("id", "")
        if b["status"] != "verified":
            continue
        has_lit = any(f.startswith("literature/")
                      for f in b["manifest"]["files"])
        if only_claims is not None:
            if cid not in only_claims:
                continue
        elif has_lit:
            continue  # default: only fill gaps
        query = build_query(b["claim"], overrides)
        works = search_all(query, max_results=5)
        context = query + " " + str(b["claim"].get("statement", ""))
        chosen, dropped = select(rank(context, works),
                                 min_score=min_score, topk=topk)
        for w, score in chosen:
            add_work(catalog, w, {"query": query, "retrieved_at": ts})
            link(catalog, cid, w["work_id"],
                 method="auto:lexical(arxiv+crossref)", score=score, ts=ts)
        if chosen:
            notes_dir.mkdir(parents=True, exist_ok=True)
            (notes_dir / f"{cid.lower()}-auto.md").write_text(
                render_note(catalog, cid), encoding="utf-8")
        summary[cid] = {
            "query": query,
            "linked": [(w["work_id"], s) for w, s in chosen],
            "dropped": [(w["work_id"], s) for w, s in dropped],
        }
        print(f"[{cid}] query: {query!r}")
        for w, s in chosen:
            acc = "peer-reviewed" if w.get("accredited") else w.get("source_type")
            print(f"    + {w['work_id']} (score {s}, {acc}) {w.get('title', '')[:60]}")
        for w, s in dropped[:3]:
            print(f"    - dropped {w['work_id']} (score {s})")
    problems = verify(catalog)
    if problems:
        for pr in problems:
            print(f"[FAIL] {pr}")
        raise SystemExit(1)
    print(f"[OK] catalog verifies; curated {len(summary)} claim(s)")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--catalog", required=True, type=Path)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--notes", required=True, type=Path)
    ap.add_argument("--min-score", type=float, default=0.25)
    ap.add_argument("--topk", type=int, default=2)
    ap.add_argument("--claims", default=None,
                    help="comma-separated claim ids (default: all lacking literature)")
    args = ap.parse_args()
    cfg = tomllib.loads(args.config.read_text(encoding="utf-8"))
    only = set(args.claims.split(",")) if args.claims else None
    curate(args.library, args.catalog, cfg, args.notes,
           min_score=args.min_score, topk=args.topk, only_claims=only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
