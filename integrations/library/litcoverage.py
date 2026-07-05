# SPDX-License-Identifier: Apache-2.0
"""Coverage — the canon measured against the catalog, fail-closed.

For every canon entry: is a registrar-verified work in the catalog that
actually IS this work (titles agree both ways, a canon surname appears among
the work's authors, the year matches)? Has its text been snapshotted, full
text fetched, chunked, vectorized (pushed), claim-linked?

Honesty rules:
- gaps are always visible — an unmatched entry is reported, never omitted;
- a drop silences a gap ONLY with a non-empty reason (drops.toml);
- `check` is what CI gates on: every entry matched or documented, else fail.

(Named litcoverage, not coverage: the ubiquitous coverage.py package would
shadow us inside any pytest-cov run.)
"""
from __future__ import annotations

import argparse
import json
import tomllib
from pathlib import Path

import canon as canonmod
from biblio_curate import titles_agree
from litindex import _load_links, _load_works

LIBDIR = Path(__file__).resolve().parent
DEFAULT_ROOT = LIBDIR / "literature"
DEFAULT_CANON = LIBDIR / "research" / "canon.toml"
DEFAULT_DROPS = LIBDIR / "research" / "drops.toml"
DEFAULT_PUSH = LIBDIR / "research" / "push_manifest.jsonl"


def _fsid(work_id: str) -> str:  # mirror litindex._fsid
    return work_id.replace(":", "_").replace("/", "_").replace(".", "-")


def _surname_present(surnames: list[str], authors: list[str]) -> bool:
    hay = " ".join(authors).lower()
    return any(s.strip().lower() in hay for s in surnames if s.strip())


def match(entry: dict, works: dict[str, dict]) -> str | None:
    """Return the work_id standing in for this canon entry, or None. The
    guard is title+author+year — title overlap alone let a 1989 sensor
    paper stand in for Guo 2017 live."""
    for wid, w in works.items():
        if not titles_agree(entry["title"], w.get("title", "")):
            continue
        if not _surname_present(entry["authors"], w.get("authors", [])):
            continue
        ey, wy = entry.get("year"), w.get("year")
        if ey is not None and wy is not None and abs(ey - wy) > 1:
            continue
        return wid
    return None


def _load_drops(path: Path) -> dict[str, str]:
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    drops: dict[str, str] = {}
    for d in raw.get("drop", []):
        did, reason = d.get("id", ""), (d.get("reason") or "").strip()
        if not did or not reason:
            raise ValueError(f"drop entry needs id and a non-empty reason: "
                             f"{did or d!r}")
        drops[did] = reason
    return drops


def _pushed_shas(push_manifest: Path | None) -> set[str]:
    if not push_manifest or not Path(push_manifest).exists():
        return set()
    shas: set[str] = set()
    for ln in Path(push_manifest).read_text().splitlines():
        if ln.strip():
            shas.add(json.loads(ln)["sha"])
    return shas


def _manifest_shas(root: Path, fsid: str) -> list[str] | None:
    p = Path(root) / "chunks" / f"{fsid}.jsonl"
    if not p.exists():
        return None
    lines = [json.loads(ln) for ln in p.read_text().splitlines() if ln.strip()]
    return [ln["sha256"] for ln in lines[1:]]  # line 0 is the header


def report(root: Path, canon_path: Path, drops_path: Path,
           push_manifest: Path | None) -> dict:
    entries = canonmod.load(canon_path)
    works = _load_works(root)
    links = _load_links(root)
    drops = _load_drops(drops_path)
    linked_work_ids = {ln["work_id"] for ln in links}
    pushed = _pushed_shas(push_manifest)

    out: dict[str, dict] = {}
    for e in entries:
        wid = match(e, works)
        row = {"verified": wid is not None, "work_id": wid, "text": False,
               "fulltext": False, "chunked": False, "vectorized": False,
               "claim_linked": False,
               "dropped_reason": drops.get(e["id"])}
        if wid:
            w = works[wid]
            row["text"] = bool(w.get("text_sha256"))
            row["fulltext"] = bool(w.get("fulltext_sha256"))
            shas = _manifest_shas(root, _fsid(wid))
            row["chunked"] = shas is not None and len(shas) > 0
            row["vectorized"] = bool(shas) and all(s in pushed for s in shas)
            row["claim_linked"] = wid in linked_work_ids
        out[e["id"]] = row

    verified = sum(1 for r in out.values() if r["verified"])
    return {
        "canon_total": len(entries),
        "verified": verified,
        "dropped": sum(1 for i in out if out[i]["dropped_reason"]),
        "fulltext": sum(1 for r in out.values() if r["fulltext"]),
        "chunked": sum(1 for r in out.values() if r["chunked"]),
        "vectorized": sum(1 for r in out.values() if r["vectorized"]),
        "entries": out,
        "drops": drops,
    }


def check(rep: dict) -> list[str]:
    """Canon ids that are neither verified in the catalog nor documented
    drops — the fail-closed gate."""
    return sorted(i for i, r in rep["entries"].items()
                  if not r["verified"] and not r["dropped_reason"])


def render_md(rep: dict) -> str:
    lines = ["| canon id | verified | fulltext | chunked | vectorized | "
             "claim-linked | note |",
             "|---|---|---|---|---|---|---|"]
    def tick(b: bool) -> str:
        return "x" if b else ""
    for cid, r in sorted(rep["entries"].items()):
        note = ("DROPPED: " + r["dropped_reason"]) if r["dropped_reason"] \
            else ("" if r["verified"] else "GAP")
        lines.append(f"| {cid} | {tick(r['verified'])} | {tick(r['fulltext'])}"
                     f" | {tick(r['chunked'])} | {tick(r['vectorized'])} | "
                     f"{tick(r['claim_linked'])} | {note} |")
    lines.append("")
    lines.append(f"canon={rep['canon_total']} verified={rep['verified']} "
                 f"dropped={rep['dropped']} fulltext={rep['fulltext']} "
                 f"chunked={rep['chunked']} vectorized={rep['vectorized']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="canon coverage over the catalog")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--canon", type=Path, default=DEFAULT_CANON)
    ap.add_argument("--drops", type=Path, default=DEFAULT_DROPS)
    ap.add_argument("--push-manifest", type=Path, default=DEFAULT_PUSH)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 on any undocumented gap")
    ap.add_argument("--md", action="store_true", help="render markdown table")
    ap.add_argument("--json", action="store_true", help="dump the full report")
    args = ap.parse_args()

    rep = report(args.root, args.canon, args.drops, args.push_manifest)
    if args.json:
        print(json.dumps(rep, indent=2, sort_keys=True))
    elif args.md:
        print(render_md(rep))
    else:
        print(f"canon={rep['canon_total']} verified={rep['verified']} "
              f"dropped={rep['dropped']} vectorized={rep['vectorized']}")
    failures = check(rep)
    if failures:
        print(f"UNDOCUMENTED GAPS ({len(failures)}): " + ", ".join(failures))
        if args.check:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
