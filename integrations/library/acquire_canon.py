# SPDX-License-Identifier: Apache-2.0
"""Acquire the canon — registrar verification of every missing entry.

For each canon entry not yet matched in the catalog:

    tier 1/2 (arxiv, crossref, doi): resolve DOI seed -> Crossref title
        (author-qualified) -> arXiv `ti:"…"` phrase search, in an order
        keyed by the entry's registrar hint. Every path ends at the same
        title+author+year guard. Optional `doi` fields in canon.toml are
        SEEDS — searched, never trusted; the registrar response decides.
    tier 3 (web): printed for the curator. This tool never guesses URLs —
        webfetch.py takes the curated URL explicitly.

Anything that fails everywhere is reported so it can become a documented
drop (drops.toml) — honest, visible, reversible.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import time
import urllib.parse
from pathlib import Path

import canon as canonmod
import litcoverage
from biblio_curate import titles_agree
from litfetch import _http_get, crossref_search, parse_arxiv_atom, \
    parse_crossref
from litindex import _load_works, add_work

LIBDIR = Path(__file__).resolve().parent


def _agrees(entry: dict, work: dict) -> bool:
    if not titles_agree(entry["title"], work.get("title", "")):
        return False
    hay = " ".join(work.get("authors", [])).lower()
    if not any(s.strip().lower() in hay for s in entry["authors"]):
        return False
    ey, wy = entry.get("year"), work.get("year")
    return ey is None or wy is None or abs(ey - wy) <= 1


def _try_doi(entry: dict) -> tuple[dict, str] | None:
    doi = entry.get("doi")
    if not doi:
        return None
    try:
        works = parse_crossref(_http_get(
            "https://api.crossref.org/works/" + urllib.parse.quote(doi)))
    except Exception as exc:  # noqa: BLE001 — fall through, reported later
        print(f"    doi seed failed: {exc}")
        return None
    if works and _agrees(entry, works[0]):
        return works[0], "doi"
    if works:
        print(f"    doi seed resolves to {works[0]['title']!r} — guard says no")
    return None


def _try_crossref(entry: dict) -> tuple[dict, str] | None:
    surname = entry["authors"][0]
    seen: set[str] = set()
    for q in (f"{entry['title']} {surname}", entry["title"]):
        try:
            candidates = crossref_search(q, 10)
        except Exception:  # noqa: BLE001
            continue
        for w in candidates:
            if w["work_id"] in seen:
                continue
            seen.add(w["work_id"])
            if _agrees(entry, w):
                return w, "crossref-title"
    return None


def _try_arxiv(entry: dict) -> tuple[dict, str] | None:
    q = urllib.parse.quote(f'ti:"{entry["title"]}"')
    try:
        works = parse_arxiv_atom(_http_get(
            "https://export.arxiv.org/api/query?search_query=" + q
            + "&max_results=5"))
    except Exception:  # noqa: BLE001
        return None
    for w in works:
        if _agrees(entry, w):
            return w, "arxiv-title-phrase"
    return None


def lookup(entry: dict) -> tuple[dict | None, str]:
    """Resolve one canon entry against the registrars. Returns
    (work, how) or (None, reason)."""
    hit = _try_doi(entry)
    if hit:
        return hit
    if entry["registrar"] == "arxiv":
        order = (_try_arxiv, _try_crossref)
    else:
        order = (_try_crossref, _try_arxiv)
    for i, attempt in enumerate(order):
        if i:
            time.sleep(3)  # arXiv politeness (and general niceness)
        hit = attempt(entry)
        if hit:
            return hit
    return None, "no registrar record with an agreeing title"


def main() -> int:
    ap = argparse.ArgumentParser(description="acquire missing canon works")
    ap.add_argument("--root", type=Path, default=LIBDIR / "literature")
    ap.add_argument("--canon", type=Path,
                    default=LIBDIR / "research" / "canon.toml")
    ap.add_argument("--drops", type=Path,
                    default=LIBDIR / "research" / "drops.toml")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--only", help="acquire a single canon id")
    args = ap.parse_args()

    entries = canonmod.load(args.canon)
    works = _load_works(args.root)
    drops = litcoverage._load_drops(args.drops)

    todo, manual = [], []
    for e in entries:
        if args.only and e["id"] != args.only:
            continue
        if e["id"] in drops or litcoverage.match(e, works):
            continue
        (manual if e["registrar"] == "web" else todo).append(e)

    print(f"{len(todo)} registrar gaps, {len(manual)} tier-3 (manual URL) gaps")
    for e in manual:
        print(f"  [tier-3] {e['id']}: {e['title'][:70]}")
    if args.dry_run:
        for e in todo:
            print(f"  [tier-1/2] {e['id']} via {e['registrar']}: "
                  f"{e['title'][:70]}")
        return 0

    ok, failed = 0, []
    for e in todo:
        found, how = lookup(e)
        if found is None:
            failed.append((e["id"], how))
            print(f"[MISS] {e['id']}: {how}")
        else:
            fetched_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
            add_work(args.root, found,
                     {"method": how, "canon_id": e["id"],
                      "fetched_at": fetched_at})
            ok += 1
            acc = ("peer-reviewed" if found.get("accredited")
                   else found.get("source_type", "?"))
            print(f"[OK]   {e['id']}: {found['work_id']} ({how}, {acc})")
        time.sleep(2)

    print(f"\nacquired {ok}, missed {len(failed)}, manual tier-3 {len(manual)}")
    for cid, reason in failed:
        print(f"  MISS {cid}: {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
