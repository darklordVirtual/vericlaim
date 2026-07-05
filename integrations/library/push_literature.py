# SPDX-License-Identifier: Apache-2.0
"""Push the literature catalog to the Worker's research layer.

build_batches is pure: it walks works + chunk manifests, re-verifies every
chunk text against its content address BEFORE it enters a request body
(fail-closed — a locally tampered text never reaches the wire), and maps
work records to the Worker's WorkIn shape (tier = retrieval method, honest
accreditation, claim links from links.jsonl).

Dedupe is server-side (/research/index skips known shas), so re-pushing the
whole catalog is always safe and idempotent. Every indexed-or-skipped sha is
appended to research/push_manifest.jsonl — litcoverage's `vectorized` column
reads that manifest, so coverage never claims more than what was pushed.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import urllib.request
from pathlib import Path

from litindex import _fsid, _load_links, _load_works

UA = "vericlaim-push-literature/1 (research-layer ingest)"
LIBDIR = Path(__file__).resolve().parent


def _work_in(work_id: str, w: dict, links: dict[str, list[str]]) -> dict:
    return {
        "fsid": _fsid(work_id),
        "work_id": work_id,
        "title": w.get("title", ""),
        "authors": w.get("authors", []),
        "year": w.get("year"),
        "venue": w.get("venue", ""),
        "kind": w.get("kind") or w.get("source_type", "paper"),
        "tier": (w.get("retrieval") or {}).get("method", "unknown"),
        "accredited": bool(w.get("accredited")),
        "url": w.get("url", ""),
        "linked_claims": sorted(links.get(work_id, [])),
    }


def build_batches(root: Path, batch_chunks: int = 30) -> list[dict]:
    """Request bodies for POST /research/index. Fail-closed: every chunk
    text is re-hashed against its manifest sha before inclusion."""
    root = Path(root)
    works = _load_works(root)
    links: dict[str, list[str]] = {}
    for ln in _load_links(root):
        links.setdefault(ln["work_id"], [])
        if ln["claim_id"] not in links[ln["work_id"]]:
            links[ln["work_id"]].append(ln["claim_id"])

    batches: list[dict] = []
    cur_works: list[dict] = []
    cur_chunks: list[dict] = []

    def flush() -> None:
        nonlocal cur_works, cur_chunks
        if cur_chunks or cur_works:
            batches.append({"works": cur_works, "chunks": cur_chunks})
            cur_works, cur_chunks = [], []

    for work_id, w in sorted(works.items()):
        fsid = _fsid(work_id)
        manifest = root / "chunks" / f"{fsid}.jsonl"
        if not manifest.exists():
            continue
        rows = [json.loads(ln)
                for ln in manifest.read_text().splitlines() if ln.strip()]
        cur_works.append(_work_in(work_id, w, links))
        for row in rows[1:]:  # row 0 is the manifest header
            sha = row["sha256"]
            tpath = root / "texts" / f"{sha}.txt"
            if not tpath.exists():
                raise ValueError(f"{fsid} chunk {row['seq']}: text missing "
                                 f"for {sha[:12]}…")
            text = tpath.read_text(encoding="utf-8")
            actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if actual != sha:
                raise ValueError(f"{fsid} chunk {row['seq']}: text hash "
                                 f"mismatch — catalog was altered locally")
            cur_chunks.append({"sha": sha, "fsid": fsid, "seq": row["seq"],
                               "section": row.get("section", ""),
                               "text": text})
            if len(cur_chunks) >= batch_chunks:
                flush()
                # the work record rides in every batch containing its chunks
                cur_works = [_work_in(work_id, w, links)]
        flush()
    return batches


def _post(url: str, token: str, body: dict) -> dict:
    req = urllib.request.Request(
        url.rstrip("/") + "/research/index",
        data=json.dumps(body).encode("utf-8"),
        headers={"content-type": "application/json",
                 "authorization": f"Bearer {token}", "User-Agent": UA},
        method="POST")
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser(description="push literature to the Worker")
    ap.add_argument("--root", type=Path, default=LIBDIR / "literature")
    ap.add_argument("--push", metavar="URL", required=True)
    ap.add_argument("--token-file", type=Path,
                    default=Path.home() / ".vericlaim_index_token")
    ap.add_argument("--manifest", type=Path,
                    default=LIBDIR / "research" / "push_manifest.jsonl")
    ap.add_argument("--batch-chunks", type=int, default=30)
    args = ap.parse_args()

    token = args.token_file.read_text().strip()
    batches = build_batches(args.root, batch_chunks=args.batch_chunks)
    n_chunks = sum(len(b["chunks"]) for b in batches)
    print(f"{len(batches)} batches, {n_chunks} chunks")

    indexed = skipped = 0
    rejected: list[dict] = []
    pushed_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.manifest.open("a", encoding="utf-8") as mf:
        for i, b in enumerate(batches):
            res = _post(args.push, token, b)
            indexed += res.get("indexed", 0)
            skipped += res.get("skipped", 0)
            rejected.extend(res.get("rejected", []))
            rejected_shas = {r["sha"] for r in res.get("rejected", [])}
            for c in b["chunks"]:
                if c["sha"] not in rejected_shas:
                    mf.write(json.dumps({"sha": c["sha"],
                                         "pushed_at": pushed_at}) + "\n")
            print(f"  batch {i + 1}/{len(batches)}: "
                  f"indexed={res.get('indexed', 0)} "
                  f"skipped={res.get('skipped', 0)} "
                  f"rejected={len(res.get('rejected', []))}")

    print(f"total: indexed={indexed} skipped={skipped} rejected={len(rejected)}")
    for r in rejected:
        print(f"  REJECTED {r['sha'][:12]}…: {r['reason']}")
    return 1 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main())
