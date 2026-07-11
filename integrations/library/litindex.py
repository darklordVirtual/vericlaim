# SPDX-License-Identifier: Apache-2.0
"""The literature catalog — a systematic, hash-locked overview of every work.

Layout (committed to git, so the catalog itself is publicly anchored):

    <root>/works/<fsid>.json   one deduplicated record per work: verified
                               registrar metadata + retrieval provenance +
                               the sha256 of the stored text snapshot
    <root>/texts/<sha256>.txt  content-addressed abstract/extract snapshots
    <root>/links.jsonl         claim<->work links: method, score, timestamp

Honesty rules:
- a work enters the catalog only with registrar-verified metadata (litfetch);
- the first text snapshot wins — a work's stored text never mutates silently;
- links record HOW a match was made (auto:lexical + score, or curator:manual)
  so automated relevance is never dressed up as human judgment;
- `verify` is fail-closed over every hash and reference;
- `report` keeps gaps visible: a claim with no literature shows as empty,
  never omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _fsid(work_id: str) -> str:
    return work_id.replace(":", "_").replace("/", "_").replace(".", "-")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_work(root: Path, work: dict, retrieval: dict) -> str:
    """Add a registrar-verified work. Deduplicated by canonical id; the first
    stored snapshot wins so recorded texts never silently change."""
    root = Path(root)
    fsid = _fsid(work["work_id"])
    wpath = root / "works" / f"{fsid}.json"
    if wpath.exists():
        return fsid
    text = (work.get("abstract") or work.get("title") or "").strip()
    sha = _sha256(text.encode("utf-8"))
    tpath = root / "texts" / f"{sha}.txt"
    tpath.parent.mkdir(parents=True, exist_ok=True)
    if not tpath.exists():
        # newline="\n": the snapshot is content-addressed by sha256 of the LF
        # text; text-mode translation on Windows would write CRLF and break the
        # hash (verify() reads raw bytes).
        tpath.write_text(text, encoding="utf-8", newline="\n")
    record = {**work, "text_sha256": sha, "retrieval": retrieval}
    wpath.parent.mkdir(parents=True, exist_ok=True)
    wpath.write_text(json.dumps(record, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n", encoding="utf-8")
    return fsid


def add_fulltext(root: Path, work_id: str, text: str, retrieval: dict) -> str:
    """Attach a full-text snapshot to an existing work. Content-addressed
    like abstracts; first snapshot wins — a work's full text never mutates
    silently. Returns the (possibly pre-existing) fulltext sha."""
    root = Path(root)
    wpath = root / "works" / f"{_fsid(work_id)}.json"
    if not wpath.exists():
        raise KeyError(f"work not in catalog: {work_id}")
    record = json.loads(wpath.read_text(encoding="utf-8"))
    if record.get("fulltext_sha256"):
        return record["fulltext_sha256"]
    sha = _sha256(text.encode("utf-8"))
    tpath = root / "texts" / f"{sha}.txt"
    if not tpath.exists():
        # newline="\n": content-addressed by LF hash — see add_work above.
        tpath.write_text(text, encoding="utf-8", newline="\n")
    record["fulltext_sha256"] = sha
    record["fulltext_retrieval"] = retrieval
    wpath.write_text(json.dumps(record, indent=2, sort_keys=True,
                                ensure_ascii=False) + "\n", encoding="utf-8")
    return sha


def link(root: Path, claim_id: str, work_id: str, *, method: str,
         score: float, ts: str) -> None:
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    entry = {"claim_id": claim_id, "work_id": work_id, "method": method,
             "score": score, "linked_at": ts}
    with (root / "links.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")


def _load_links(root: Path) -> list[dict]:
    p = Path(root) / "links.jsonl"
    if not p.exists():
        return []
    return [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]


def _load_works(root: Path) -> dict[str, dict]:
    out: dict[str, dict] = {}
    wdir = Path(root) / "works"
    if wdir.is_dir():
        for p in sorted(wdir.glob("*.json")):
            w = json.loads(p.read_text(encoding="utf-8"))
            out[w["work_id"]] = w
    return out


def verify(root: Path) -> list[str]:
    """Fail-closed integrity: every stored text hashes to its name and its
    work's recorded sha; every link points at a cataloged work."""
    root = Path(root)
    problems: list[str] = []
    works = _load_works(root)
    for wid, w in works.items():
        sha = w.get("text_sha256", "")
        tpath = root / "texts" / f"{sha}.txt"
        if not tpath.exists():
            problems.append(f"{wid}: text snapshot missing ({sha[:12]}…)")
            continue
        actual = _sha256(tpath.read_bytes())
        if actual != sha:
            problems.append(f"{wid}: text snapshot hash mismatch — stored "
                            f"text was altered after cataloging")
        fsha = w.get("fulltext_sha256")
        if fsha:
            fpath = root / "texts" / f"{fsha}.txt"
            if not fpath.exists():
                problems.append(f"{wid}: fulltext snapshot missing "
                                f"({fsha[:12]}…)")
            elif _sha256(fpath.read_bytes()) != fsha:
                problems.append(f"{wid}: fulltext snapshot hash mismatch — "
                                f"stored text was altered after cataloging")
    for ln in _load_links(root):
        if ln["work_id"] not in works:
            problems.append(f"link {ln['claim_id']} -> {ln['work_id']}: "
                            f"work not in catalog")
    return problems


def report(root: Path, claims: list[str] | None = None) -> dict:
    works = _load_works(root)
    links = _load_links(root)
    coverage: dict[str, list[str]] = {}
    for ln in links:
        coverage.setdefault(ln["claim_id"], [])
        if ln["work_id"] not in coverage[ln["claim_id"]]:
            coverage[ln["claim_id"]].append(ln["work_id"])
    for cid in claims or []:
        coverage.setdefault(cid, [])  # gaps stay visible
    cited_by: dict[str, int] = {}
    for ln in links:
        cited_by[ln["work_id"]] = cited_by.get(ln["work_id"], 0) + 1
    return {
        "n_works": len(works),
        "n_links": len(links),
        "accredited_works": sum(1 for w in works.values() if w.get("accredited")),
        "coverage": coverage,
        "most_cited": sorted(cited_by.items(), key=lambda kv: (-kv[1], kv[0]))[:10],
    }


def render_note(root: Path, claim_id: str) -> str:
    """The AUTO-CURATED literature note for a claim's bundle: verified
    metadata only, method and score visible, honest about what a match means."""
    works = _load_works(root)
    lines = [
        f"# AUTO-CURATED literature for {claim_id}",
        "",
        "Bibliographic metadata below is registrar-verified (arXiv/Crossref) "
        "at retrieval time — never model-recalled. Relevance was scored by a "
        "deterministic lexical method; the score is curation metadata. A "
        "matched work supports *context* and does not prove the claim.",
        "",
    ]
    for ln in _load_links(root):
        if ln["claim_id"] != claim_id:
            continue
        w = works.get(ln["work_id"])
        if not w:
            continue
        authors = ", ".join(w.get("authors", [])[:4]) or "?"
        if len(w.get("authors", [])) > 4:
            authors += " et al."
        venue = w.get("venue") or "?"
        acc = "peer-reviewed" if w.get("accredited") else w.get("source_type", "?")
        lines.append(
            f"- **{w.get('title', '?')}** — {authors} ({w.get('year', '?')}), "
            f"*{venue}* [{acc}]. {w.get('url', '')}  \n"
            f"  matched by {ln['method']}, score {ln['score']}, "
            f"linked {ln['linked_at']}; text snapshot "
            f"sha256 {w.get('text_sha256', '')[:16]}…")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()
    if args.verify:
        problems = verify(args.root)
        for pr in problems:
            print(f"[FAIL] {pr}")
        print("[OK] catalog verifies" if not problems
              else f"[FAIL] {len(problems)} problem(s)")
        return 1 if problems else 0
    rep = report(args.root)
    print(json.dumps(rep, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
