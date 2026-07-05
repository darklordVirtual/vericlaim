# SPDX-License-Identifier: Apache-2.0
"""Deterministic, section-aware chunking — the retrieval unit.

Text (full text when we have it, abstract+extract otherwise) is split into
content-addressed chunks: greedy sentence packing toward a target size,
whole-sentence overlap between neighbors, section labels from `## ` heading
lines. Same text in, same shas out — no randomness, no timestamps.

The per-work manifest (literature/chunks/<fsid>.jsonl) records the source
text's sha; re-chunking a CHANGED source without --refresh is refused, so a
work's chunks never mutate silently.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from litindex import _fsid, _load_works

_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sentences(block: str, target: int) -> list[str]:
    """Split into sentences; hard-wrap any sentence longer than 2*target so
    no chunk can exceed the bound."""
    out: list[str] = []
    for s in _SENT_RE.split(block):
        s = s.strip()
        if not s:
            continue
        while len(s) > 2 * target:
            out.append(s[: 2 * target])
            s = s[2 * target:]
        if s:
            out.append(s)
    return out


def _pack(sentences: list[str], section: str, target: int, overlap: int,
          chunks: list[dict]) -> None:
    cur: list[str] = []
    cur_len = 0
    for s in sentences:
        if cur and cur_len + 1 + len(s) > target:
            text = " ".join(cur)
            chunks.append({"section": section, "text": text})
            # overlap: whole trailing sentences when they fit, else the
            # word-aligned character tail of the flushed text
            tail: list[str] = []
            tail_len = 0
            for prev in reversed(cur):
                if tail_len + len(prev) > overlap:
                    break
                tail.insert(0, prev)
                tail_len += len(prev) + 1
            if not tail and overlap > 0:
                frag = text[-overlap:]
                cut = frag.find(" ")
                frag = frag[cut + 1:] if cut != -1 else frag
                if frag:
                    tail = [frag]
            cur = tail[:]
            cur_len = sum(len(x) + 1 for x in cur)
        cur.append(s)
        cur_len += len(s) + 1
    if cur:
        chunks.append({"section": section, "text": " ".join(cur)})


def chunk(text: str, *, target: int = 1200, overlap: int = 200) -> list[dict]:
    """Split text into ordered chunks: {seq, section, text, sha256}."""
    sections: list[tuple[str, list[str]]] = [("", [])]
    for line in text.splitlines():
        if line.startswith("## "):
            sections.append((line[3:].strip(), []))
        else:
            sections[-1][1].append(line)
    raw: list[dict] = []
    for section, lines in sections:
        block = "\n".join(lines).strip()
        if not block:
            continue
        _pack(_sentences(block, target), section, target, overlap, raw)
    out: list[dict] = []
    for i, c in enumerate(raw):
        out.append({"seq": i, "section": c["section"], "text": c["text"],
                    "sha256": _sha256(c["text"])})
    return out


def write_manifest(root: Path, fsid: str, source_sha: str,
                   chunks: list[dict], *, target: int = 1200,
                   overlap: int = 200, refresh: bool = False) -> Path:
    """Write literature/chunks/<fsid>.jsonl (header + one line per chunk,
    texts NOT included — they live content-addressed in texts/). Refuses to
    replace a manifest built from a different source unless refresh=True."""
    cdir = Path(root) / "chunks"
    cdir.mkdir(parents=True, exist_ok=True)
    path = cdir / f"{fsid}.jsonl"
    if path.exists():
        head = json.loads(path.read_text().splitlines()[0])
        if head.get("source_sha256") != source_sha and not refresh:
            raise ValueError(
                f"{fsid}: manifest was built from a different source text; "
                f"pass refresh=True (--refresh) to re-chunk deliberately")
    lines = [json.dumps({"fsid": fsid, "source_sha256": source_sha,
                         "target": target, "overlap": overlap,
                         "n": len(chunks)}, sort_keys=True)]
    for c in chunks:
        lines.append(json.dumps({"seq": c["seq"], "section": c["section"],
                                 "sha256": c["sha256"]}, sort_keys=True))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _store_chunk_texts(root: Path, chunks: list[dict]) -> None:
    tdir = Path(root) / "texts"
    tdir.mkdir(parents=True, exist_ok=True)
    for c in chunks:
        p = tdir / f"{c['sha256']}.txt"
        if not p.exists():
            p.write_text(c["text"], encoding="utf-8")


def run_all(root: Path, *, target: int = 1200, overlap: int = 200,
            refresh: bool = False) -> dict[str, int]:
    """Chunk every catalog work (fulltext when present, else the abstract
    snapshot). Returns {work_id: n_chunks}."""
    root = Path(root)
    results: dict[str, int] = {}
    for wid, w in sorted(_load_works(root).items()):
        sha = w.get("fulltext_sha256") or w.get("text_sha256")
        if not sha:
            continue
        text = (root / "texts" / f"{sha}.txt").read_text(encoding="utf-8")
        chunks = chunk(text, target=target, overlap=overlap)
        if not chunks:
            continue
        _store_chunk_texts(root, chunks)
        write_manifest(root, _fsid(wid), sha, chunks, target=target,
                       overlap=overlap, refresh=refresh)
        results[wid] = len(chunks)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="chunk the literature catalog")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent / "literature")
    ap.add_argument("--all", action="store_true", required=True)
    ap.add_argument("--target", type=int, default=1200)
    ap.add_argument("--overlap", type=int, default=200)
    ap.add_argument("--refresh", action="store_true")
    args = ap.parse_args()

    results = run_all(args.root, target=args.target, overlap=args.overlap,
                      refresh=args.refresh)
    for wid, n in sorted(results.items()):
        print(f"{n:5d} chunks  {wid}")
    print(f"{sum(results.values())} chunks across {len(results)} works")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
