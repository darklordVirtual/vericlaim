# SPDX-License-Identifier: Apache-2.0
"""External anchoring for the claim + library ledgers — witness and verify.

THE GAP THIS CLOSES: the D1 hash chains are tamper-EVIDENT, but whoever
controls the database (including the project owner) could rebuild an entire
chain that still self-verifies. Anchoring publishes the chain heads somewhere
the Worker cannot rewrite — this repo's public git history:

    python3 integrations/cloudflare-ai/witness.py --record --url $URL
        # verifies both chains CLIENT-side, then appends the heads to
        # claims/witness.jsonl — commit and push that file; the public git
        # history is the anchor.

    python3 integrations/cloudflare-ai/witness.py --verify --url $URL
        # downloads the FULL export, recomputes every hash locally (never
        # trusting the Worker's own /verify), and requires today's chains to
        # EXTEND every witnessed head at its witnessed length. A rebuilt,
        # edited, or truncated history fails against any prior witness.

Honest boundary: an anchor is only as public as the witness file. It proves
nothing until pushed, and it cannot detect a rebuild that happened BEFORE the
first witness was recorded. Record early, push always.

Stdlib only. Hashing mirrors src/hashchain.ts exactly (sorted-key canonical
JSON; sha256(prev + "\\n" + canonical(row))).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Row fields covered by entry_hash, per table — must mirror src/ledger.ts and
# src/library.ts exactly (order irrelevant: canonical() sorts keys).
CLAIM_FIELDS = ("ts", "claim_id", "statement", "evidence_level", "metrics",
                "caveat", "artifact", "artifact_sha256", "git_commit",
                "content_hash")
LIBRARY_FIELDS = ("ts", "bundle_id", "status", "source_repo",
                  "source_claim_id", "claim", "manifest", "provenance")

WITNESS_FILE = "claims/witness.jsonl"


def canonical(value) -> str:
    """Mirror of hashchain.ts canonical(): recursive sorted-key JSON with
    JSON.stringify's separators and unescaped non-ASCII."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def entry_hash(prev_hash: str, row: dict) -> str:
    data = (prev_hash + "\n" + canonical(row)).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def rewalk(rows: list[dict], fields: tuple[str, ...]) -> dict:
    """Recompute the whole chain locally. Returns ok/entries/head plus
    heads_at[n] = the head after n entries, for witness-extension checks."""
    prev = ""
    heads_at: dict[int, str] = {0: ""}
    for i, raw in enumerate(rows, 1):
        row = {f: raw.get(f) for f in fields}
        if raw.get("prev_hash") != prev:
            return {"ok": False, "broken_at": i, "entries": len(rows),
                    "head": prev, "heads_at": heads_at}
        eh = entry_hash(prev, row)
        if raw.get("entry_hash") != eh:
            return {"ok": False, "broken_at": i, "entries": len(rows),
                    "head": prev, "heads_at": heads_at}
        prev = eh
        heads_at[i] = eh
    return {"ok": True, "broken_at": None, "entries": len(rows),
            "head": prev, "heads_at": heads_at}


def check_witnesses(witnesses: list[dict], claims_walk: dict,
                    library_walk: dict) -> list[str]:
    """Every witnessed head must appear in today's chain at its witnessed
    length. Returns human-readable problems (empty = all anchors hold)."""
    problems: list[str] = []
    for i, w in enumerate(witnesses):
        for name, walk in (("claims", claims_walk), ("library", library_walk)):
            n = int(w.get(f"{name}_entries", 0))
            head = w.get(f"{name}_head", "")
            if n == 0:
                continue
            if walk["entries"] < n:
                problems.append(
                    f"witness[{i}]: {name} chain shrank — witnessed {n} "
                    f"entries,现 only {walk['entries']}".replace("现", "now"))
                continue
            if walk["heads_at"].get(n) != head:
                problems.append(
                    f"witness[{i}]: {name} chain was REBUILT — the head after "
                    f"{n} entries no longer equals the witnessed head "
                    f"{head[:12]}…")
    return problems


def _get_json(url: str) -> dict:
    req = urllib.request.Request(
        url, headers={"user-agent": "vericlaim-witness/1"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _load_witnesses(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(ln) for ln in path.read_text().splitlines() if ln.strip()]


def _walks(url: str) -> tuple[dict, dict]:
    export = _get_json(url.rstrip("/") + "/ledger/export")
    return (rewalk(export.get("claims", []), CLAIM_FIELDS),
            rewalk(export.get("library", []), LIBRARY_FIELDS))


def record(url: str, root: Path) -> int:
    claims_walk, library_walk = _walks(url)
    for name, walk in (("claims", claims_walk), ("library", library_walk)):
        if not walk["ok"]:
            print(f"[FAIL] refusing to witness: {name} chain does not verify "
                  f"client-side (broken at #{walk['broken_at']})")
            return 1
    wpath = root / WITNESS_FILE
    problems = check_witnesses(_load_witnesses(wpath), claims_walk, library_walk)
    if problems:
        for pr in problems:
            print(f"[FAIL] {pr}")
        print("[FAIL] refusing to witness a history that contradicts prior "
              "witnesses")
        return 1
    entry = {
        "witnessed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "url": url.rstrip("/"),
        "claims_entries": claims_walk["entries"],
        "claims_head": claims_walk["head"],
        "library_entries": library_walk["entries"],
        "library_head": library_walk["head"],
        "verified": "client-side rewalk of full export",
    }
    with wpath.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"[OK] witnessed claims={entry['claims_entries']} "
          f"(head {entry['claims_head'][:12]}…) "
          f"library={entry['library_entries']} "
          f"(head {entry['library_head'][:12]}…)")
    print(f"     appended to {WITNESS_FILE} — COMMIT AND PUSH it; "
          f"the public git history is the anchor.")
    return 0


def verify(url: str, root: Path) -> int:
    claims_walk, library_walk = _walks(url)
    ok = True
    for name, walk in (("claims", claims_walk), ("library", library_walk)):
        if walk["ok"]:
            print(f"[OK] {name} chain verifies client-side "
                  f"({walk['entries']} entries, head {walk['head'][:12]}…)")
        else:
            print(f"[FAIL] {name} chain broken at #{walk['broken_at']} "
                  f"(client-side rewalk)")
            ok = False
    witnesses = _load_witnesses(root / WITNESS_FILE)
    problems = check_witnesses(witnesses, claims_walk, library_walk)
    for pr in problems:
        print(f"[FAIL] {pr}")
        ok = False
    if ok:
        print(f"[OK] all {len(witnesses)} witness(es) extended — history has "
              f"not been rewritten since first anchor.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--url", required=True)
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parents[2])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--record", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    return record(args.url, args.root) if args.record else verify(args.url, args.root)


if __name__ == "__main__":
    raise SystemExit(main())
