# SPDX-License-Identifier: Apache-2.0
"""Bibliography-driven curation: match claims to the source paper's own refs.

A gate-verified project's paper bibliography is a *pre-curated, web-verified*
matching pool — far higher precision than open web search. This pipeline:

1. parses the source paper's reference list (ids extracted only when
   literally present — an entry without arXiv/DOI never gets one invented);
2. ranks the pool against each claim's statement (deterministic, lexical);
3. verifies every candidate against the registrar (arXiv id / DOI lookup, or
   title search as a last resort) and REQUIRES the registrar title to agree
   with the bibliography title — a mismatch is a miscitation signal and is
   reported, never attached;
4. records works + links (method ``biblio:source-paper``) in the catalog and
   writes AUTO-CURATED notes for the next harvest.

    python3 integrations/library/biblio_curate.py \\
        --paper ~/REMORA-research/paper/remora_paper.md \\
        --library build/library --catalog integrations/library/literature \\
        --notes integrations/library/mappings/lit/auto
"""
from __future__ import annotations

import argparse
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import load_bundle  # noqa: E402
from litfetch import (  # noqa: E402
    _http_get, _tokens, crossref_search, parse_arxiv_atom, parse_crossref,
)
from litindex import add_work, link, render_note, verify  # noqa: E402

_YEAR_RE = re.compile(r"\((\d{4})\)")
_ARXIV_RE = re.compile(r"arXiv:\s*(\d{4}\.\d{4,5})", re.IGNORECASE)
_DOI_RE = re.compile(r"doi:?\s*(10\.\d{4,9}/[^\s,;]+?)[.,;]?(?:\s|$)",
                     re.IGNORECASE)
_TITLE_STOP_RE = re.compile(r"\.\s+(?:\*|arXiv:|doi:|ISBN)", re.IGNORECASE)


def parse_bibliography(text: str) -> list[dict]:
    """Parse `- Author, A. (year). Title. *Venue*. ids.` reference entries."""
    entries: list[dict] = []
    block: list[str] = []
    in_refs = False
    for line in text.splitlines() + [""]:
        if re.match(r"^#{1,3}\s*References", line):
            in_refs = True
            continue
        if not in_refs:
            continue
        if line.startswith("- "):
            block = [line[2:].strip()]
        elif line.strip() and block:
            block.append(line.strip())
        elif block:
            entry = _parse_entry(" ".join(block))
            if entry:
                entries.append(entry)
            block = []
    return entries


def _parse_entry(raw: str) -> dict | None:
    ym = _YEAR_RE.search(raw)
    if not ym:
        return None
    year = int(ym.group(1))
    rest = raw[ym.end():].lstrip(". ")
    stop = _TITLE_STOP_RE.search(rest)
    title = (rest[:stop.start()] if stop else rest).strip().rstrip(".")
    am = _ARXIV_RE.search(raw)
    dm = _DOI_RE.search(raw)
    first_author = raw[:ym.start()].split(",")[0].strip().split()[-1] \
        if raw[:ym.start()].strip() else ""
    vm = re.search(r"\*([^*]+)\*", rest)
    return {
        "raw": raw,
        "first_author": first_author,
        "year": year,
        "title": title,
        "venue": vm.group(1).strip() if vm else "",
        "arxiv_id": am.group(1) if am else None,
        "doi": dm.group(1).lower().rstrip(".") if dm else None,
    }


def match_bib(claim: dict, entries: list[dict]) -> list[tuple[dict, float]]:
    """Rank bibliography entries against a claim, deterministically."""
    q = _tokens(str(claim.get("statement", "")) + " " +
                str(claim.get("caveat", "")))
    scored = []
    for e in entries:
        t = _tokens(e["title"] + " " + e.get("venue", ""))
        if not t:
            continue
        score = round(len(q & t) / (len(t) ** 0.5), 4)
        scored.append((e, score))
    return sorted(scored, key=lambda p: (-p[1], p[0]["title"]))


def titles_agree(bib_title: str, registrar_title: str) -> bool:
    """Guard against miscitation: the registrar record may only stand in for
    a bib entry when the titles share most of their tokens BOTH ways.

    Normalizing by max(len) — not min — is load-bearing: with min, a short
    title agrees with any longer title containing it (caught live: Guo 2017
    'On calibration of modern neural networks' passed against a 1989 'Sensor
    calibration using artificial neural networks')."""
    a, b = _tokens(bib_title), _tokens(registrar_title)
    if not a or not b:
        return False
    return len(a & b) / max(len(a), len(b)) >= 0.7


# --------------------------------------------------------------------------- #
# Registrar verification (live)
# --------------------------------------------------------------------------- #

def _verify_entry(entry: dict, arxiv_cache: dict[str, dict]) -> tuple[dict | None, str]:
    """Return (registrar work, how) or (None, reason). Never invents ids."""
    if entry["arxiv_id"]:
        w = arxiv_cache.get(entry["arxiv_id"])
        if w and titles_agree(entry["title"], w["title"]):
            return w, "arxiv-id"
        if w:
            return None, (f"MISCITATION? arXiv:{entry['arxiv_id']} title is "
                          f"{w['title']!r}, bibliography says {entry['title']!r}")
        return None, f"arXiv:{entry['arxiv_id']} not found"
    if entry["doi"]:
        try:
            works = parse_crossref(_http_get(
                "https://api.crossref.org/works/" + entry["doi"]))
        except Exception as exc:  # noqa: BLE001 — record, don't crash the run
            return None, f"doi lookup failed: {exc}"
        if works and titles_agree(entry["title"], works[0]["title"]):
            return works[0], "doi"
        if works:
            return None, (f"MISCITATION? doi:{entry['doi']} resolves to "
                          f"{works[0]['title']!r}")
        return None, f"doi:{entry['doi']} not found"
    # last resort: title search, strict agreement required
    try:
        time.sleep(0.5)
        works = crossref_search(entry["title"], 3)
    except Exception as exc:  # noqa: BLE001
        return None, f"title search failed: {exc}"
    for w in works:
        if titles_agree(entry["title"], w["title"]):
            return w, "title-search"
    return None, "no registrar record with an agreeing title"


def _prefetch_arxiv(entries: list[dict]) -> dict[str, dict]:
    ids = sorted({e["arxiv_id"] for e in entries if e["arxiv_id"]})
    if not ids:
        return {}
    url = ("https://export.arxiv.org/api/query?id_list=" + ",".join(ids)
           + f"&max_results={len(ids)}")
    works = parse_arxiv_atom(_http_get(url))
    return {w["work_id"].split(":", 1)[1]: w for w in works}


def curate(paper: Path, library_dir: Path, catalog: Path, notes_dir: Path, *,
           topk: int = 3, min_score: float = 0.6,
           only_claims: set[str] | None = None) -> dict:
    entries = parse_bibliography(paper.read_text(encoding="utf-8"))
    print(f"[OK] parsed {len(entries)} bibliography entries from {paper.name}")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    seen_bundle_claims: set[str] = set()
    summary: dict[str, list] = {}
    claims: list[dict] = []
    for bdir in sorted(p for p in Path(library_dir).iterdir() if p.is_dir()):
        b = load_bundle(bdir)
        cid = b["claim"].get("id", "")
        if b["status"] != "verified" or cid in seen_bundle_claims:
            continue
        seen_bundle_claims.add(cid)
        if only_claims and cid not in only_claims:
            continue
        claims.append(b["claim"])

    needed = [e for c in claims for e, s in match_bib(c, entries)[:topk]
              if s >= min_score]
    arxiv_cache = _prefetch_arxiv(needed)  # ONE polite arXiv call for all ids
    time.sleep(3.0)

    for claim in claims:
        cid = claim["id"]
        summary[cid] = []
        for entry, score in match_bib(claim, entries)[:topk]:
            if score < min_score:
                print(f"[{cid}] - below threshold: {entry['title'][:50]!r} "
                      f"(score {score})")
                continue
            work, how = _verify_entry(entry, arxiv_cache)
            if work is None:
                print(f"[{cid}] ! not attached: {entry['title'][:50]!r} — {how}")
                summary[cid].append(("skipped", entry["title"], how))
                continue
            add_work(catalog, work, {
                "query": f"bibliography of {paper.name}",
                "retrieved_at": ts})
            link(catalog, cid, work["work_id"],
                 method=f"biblio:source-paper+{how}", score=score, ts=ts)
            acc = "peer-reviewed" if work.get("accredited") else work.get("source_type")
            print(f"[{cid}] + {work['work_id']} (match {score}, {how}, {acc}) "
                  f"{work['title'][:55]}")
            summary[cid].append(("linked", work["work_id"], score))
        if any(kind == "linked" for kind, *_ in summary[cid]):
            notes_dir.mkdir(parents=True, exist_ok=True)
            (notes_dir / f"{cid.lower()}-auto.md").write_text(
                render_note(catalog, cid), encoding="utf-8")

    problems = verify(catalog)
    if problems:
        for pr in problems:
            print(f"[FAIL] {pr}")
        raise SystemExit(1)
    linked = sum(1 for v in summary.values()
                 if any(k == "linked" for k, *_ in v))
    print(f"[OK] catalog verifies; bibliography-linked literature for "
          f"{linked}/{len(summary)} claim(s)")
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--paper", required=True, type=Path)
    ap.add_argument("--library", required=True, type=Path)
    ap.add_argument("--catalog", required=True, type=Path)
    ap.add_argument("--notes", required=True, type=Path)
    ap.add_argument("--topk", type=int, default=3)
    ap.add_argument("--min-score", type=float, default=0.6)
    ap.add_argument("--claims", default=None)
    args = ap.parse_args()
    only = set(args.claims.split(",")) if args.claims else None
    curate(args.paper, args.library, args.catalog, args.notes,
           topk=args.topk, min_score=args.min_score, only_claims=only)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
