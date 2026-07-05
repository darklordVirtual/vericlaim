# SPDX-License-Identifier: Apache-2.0
"""Evidence for the research-layer claims — deterministic over the repo.

Recomputes, from committed state only (canon, catalog, drops, chunk
manifests, push manifest), the numbers the README quotes about the
literature RAG: canon size, verified works, honest drops, catalog size,
chunk totals, vectorized coverage. Writes the artifact + provenance stamp
so `vericlaim reproduce` fails the moment any quoted number drifts from
the committed catalog.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LIBDIR = Path(__file__).resolve().parent
ROOT = LIBDIR.parents[1]
sys.path.insert(0, str(LIBDIR))
sys.path.insert(0, str(ROOT))

import litcoverage  # noqa: E402
from litindex import _load_works  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402

ARTIFACT = LIBDIR / "artifacts" / "research_layer.json"


def main() -> int:
    root = LIBDIR / "literature"
    rep = litcoverage.report(root, litcoverage.DEFAULT_CANON,
                             litcoverage.DEFAULT_DROPS,
                             litcoverage.DEFAULT_PUSH)
    works = _load_works(root)
    manifests = sorted((root / "chunks").glob("*.jsonl"))
    chunk_shas: set[str] = set()
    for m in manifests:
        for ln in m.read_text().splitlines()[1:]:
            if ln.strip():
                chunk_shas.add(json.loads(ln)["sha256"])
    pushed = litcoverage._pushed_shas(litcoverage.DEFAULT_PUSH)

    out = {
        "canon_total": rep["canon_total"],
        "canon_verified": rep["verified"],
        "canon_dropped": rep["dropped"],
        "canon_fulltext": rep["fulltext"],
        "canon_vectorized": rep["vectorized"],
        "catalog_works": len(works),
        "catalog_works_fulltext": sum(
            1 for w in works.values() if w.get("fulltext_sha256")),
        "chunked_works": len(manifests),
        "chunks_total": len(chunk_shas),
        "chunks_pushed": len(chunk_shas & pushed),
        "undocumented_gaps": len(litcoverage.check(rep)),
    }
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    stamp(str(ARTIFACT.relative_to(ROOT)),
          script="python3 integrations/library/evidence_research_layer.py")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
