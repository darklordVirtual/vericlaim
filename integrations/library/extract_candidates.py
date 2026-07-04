# SPDX-License-Identifier: Apache-2.0
"""Extract assertion-like statements from an arbitrary repo as CANDIDATES.

For repos WITHOUT a gate-verified claim register, this scans markdown docs for
factual-sounding numeric assertions ("3.5x faster", "supports 12 formats",
"91.2% accuracy") and preserves each as a **candidate** bundle:

- ``status: candidate`` — quarantined. A candidate is NOT a verified claim and
  must never be imported into a project as one.
- ``evidence_level: theoretical`` and an empty artifact list — extraction
  found an *assertion*, not evidence.
- The caveat states plainly that the statement is unverified; provenance
  records the exact file:line it came from.

The path from candidate to verified claim runs through evidence, never around
it: ``scaffold_evidence`` writes a deterministic evidence-script template that
FAILS until a curator implements the actual measurement — the tooling will not
fabricate a result.

    python3 integrations/library/extract_candidates.py --source <repo> --out build/library
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bundlefmt import build_bundle  # noqa: E402

# A line worth quarantining: contains a number AND an assertion cue.
_NUMBER = r"\d+(?:\.\d+)?"
ASSERTION_RE = re.compile(
    rf"(?i)(?:{_NUMBER}\s*(?:%|ms|s\b|x\s+faster|×)|"
    rf"supports?\s+{_NUMBER}|all\s+{_NUMBER}|accuracy|latency|"
    rf"{_NUMBER}\s+(?:languages|formats|cases|tests|files))")
_HAS_NUMBER_RE = re.compile(_NUMBER)

QUARANTINE_CAVEAT = (
    "Extracted assertion from an ungated repo — NOT verified: no artifact, no "
    "register, no gate ran. Quarantined as a candidate until evidence is "
    "produced (see the scaffolded evidence script) and the claim is registered "
    "in a gated project.")


def _git_commit(root: Path) -> str:
    try:
        out = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _assertion_lines(text: str):
    """Yield (lineno, line) for assertion-like prose lines, skipping fences."""
    in_fence = False
    for n, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence or not stripped:
            continue
        if _HAS_NUMBER_RE.search(stripped) and ASSERTION_RE.search(stripped):
            yield n, stripped


def _candidate_id(repo_name: str, rel: str, line: str) -> str:
    """Stable id derived from content, so re-extraction is idempotent."""
    digest = hashlib.sha256(f"{rel}\n{line}".encode()).hexdigest()[:10]
    slug = re.sub(r"[^A-Za-z0-9]+", "", repo_name.split("/")[-1]).upper()[:8]
    return f"CAND-{slug or 'REPO'}-{digest}"


def extract_repo(src: Path, out_root: Path, cfg: dict) -> dict[str, str]:
    """Scan *src* markdown docs; build candidate bundles. {cand_id: bundle_id}."""
    src = Path(src)
    repo_name = cfg.get("repo", src.name)
    commit = _git_commit(src)
    globs = cfg.get("doc_globs", ("README.md", "docs/**/*.md", "*.md"))
    seen: set[Path] = set()
    results: dict[str, str] = {}
    for pattern in globs:
        for doc in sorted(src.glob(pattern)):
            if not doc.is_file() or doc in seen:
                continue
            seen.add(doc)
            rel = doc.relative_to(src).as_posix()
            for lineno, line in _assertion_lines(
                    doc.read_text(encoding="utf-8", errors="replace")):
                cid = _candidate_id(repo_name, rel, line)
                if cid in results:
                    continue
                claim = {"id": cid, "statement": line,
                         "evidence_level": "theoretical",
                         "artifact": [], "caveat": QUARANTINE_CAVEAT}
                prov = {"source_repo": repo_name,
                        "source_commit": commit,
                        "source_claim_id": cid,
                        "source_evidence_level": None,
                        "level_mapping": "extracted->theoretical",
                        "source_gate": "none",
                        "extracted_from": f"{rel}:{lineno}",
                        "harvest_tool": "vericlaim-library extract_v1"}
                bid, _ = build_bundle(Path(out_root), claim=claim,
                                      provenance=prov, files={},
                                      status="candidate")
                results[cid] = bid
    return results


_SCAFFOLD = '''\
# SPDX-License-Identifier: Apache-2.0
"""Evidence script for {cid} — SCAFFOLD, must be completed by a curator.

Candidate statement (UNVERIFIED):
    {statement}

Complete measure() so it deterministically measures the statement above and
returns a JSON-serializable dict of the numbers the claim will register.
Until then this script FAILS — a scaffold must never look like evidence.
"""
from __future__ import annotations

import json
from pathlib import Path


def measure() -> dict:
    raise NotImplementedError(
        "complete measure() with the actual deterministic measurement for "
        "{cid} — the scaffold refuses to fabricate a result")


def main() -> int:
    result = measure()
    out = Path(__file__).resolve().parent / "artifacts" / "{artifact_name}"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\\n")
    from vericlaim.provenance import stamp
    stamp(out, script="python3 " + Path(__file__).name)
    print(f"[OK] wrote {{out}}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def scaffold_evidence(claim: dict, out_dir: Path) -> Path:
    """Write a failing-by-default evidence-script template for a candidate."""
    cid = claim["id"]
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    script = out_dir / f"evidence_{cid.lower().replace('-', '_')}.py"
    script.write_text(_SCAFFOLD.format(
        cid=cid, statement=claim.get("statement", ""),
        artifact_name=f"{cid.lower()}.json"), encoding="utf-8")
    return script


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--repo", default=None, help="repo name for provenance")
    ap.add_argument("--scaffold-dir", type=Path, default=None,
                    help="also write evidence-script scaffolds here")
    args = ap.parse_args()
    cfg = {"repo": args.repo or args.source.name}
    results = extract_repo(args.source, args.out, cfg)
    for cid, bid in results.items():
        print(f"[CANDIDATE] {cid} -> {bid}")
        if args.scaffold_dir:
            from bundlefmt import load_bundle
            b = load_bundle(args.out / bid)
            scaffold_evidence(b["claim"], args.scaffold_dir)
    print(f"[OK] extracted {len(results)} candidate(s) — quarantined, "
          f"not verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
