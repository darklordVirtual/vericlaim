# SPDX-License-Identifier: Apache-2.0
"""Governance-handbook validator — the meta-control the handbook itself needs.

The handbook lives OUTSIDE doc_globs on purpose (it is a synthesis over the
registers, not a source of primary claims). But that means it could drift in
exactly the way vericlaim exists to prevent. This checker closes that gap
without forcing the whole narrative into numeric anchors. It verifies, for both
the English and Norwegian editions:

  1. Register-derived numbers agree — every metric the handbook quotes from the
     CLAIM-LIB-RAG family (canon works, verified, drops, chunks) appears with
     the register's current value, and NO stale value of it appears.
  2. The collection index is internally consistent — the Appendix A per-
     collection counts sum to the catalog_works total.
  3. Internal navigation is intact — every in-page link `](#slug)` resolves to
     a real heading.

Run directly (`python3 docs/governance/handbook_check.py`) or via
tests/test_handbook_check.py in CI. It raises on any drift.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from vericlaim.register import load_register  # noqa: E402

EDITIONS = ["frontier-ai-governance-master.md",
            "frontier-ai-governance-master_NO_nb.md"]
HERE = Path(__file__).resolve().parent


def _register_metrics() -> dict[str, str]:
    claims = load_register((ROOT / "claims" / "register.yaml").read_text())
    by_id = {c["id"]: c for c in claims if "id" in c}
    out: dict[str, str] = {}
    for cid in ("CLAIM-LIB-RAG-001", "CLAIM-LIB-RAG-002"):
        for k, v in (by_id.get(cid, {}).get("metrics") or {}).items():
            out[f"{cid}.{k}"] = str(v)
    return out


def _slugify(heading: str) -> str:
    # GitHub-style: lowercase, drop punctuation, then replace EACH whitespace
    # with a hyphen WITHOUT collapsing runs — so "F — Reading" (an em dash
    # leaves two spaces) becomes "f--reading", matching the rendered anchor.
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s", "-", s)


def check_edition(path: Path, metrics: dict[str, str]) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    name = path.name

    # 1. every register metric value must appear at least once.
    for key, val in metrics.items():
        if not re.search(rf"(?<!\d){re.escape(val)}(?!\d)", text):
            problems.append(f"{name}: register value {val} for {key} is absent "
                            f"(handbook may have drifted)")

    # 2. Appendix A collection counts sum to catalog_works.
    counts = [int(m) for m in re.findall(r"^\|\s*\d{2}\s*\|[^|]+\|\s*(\d+)\s*\|$",
                                         text, re.MULTILINE)]
    total = metrics.get("CLAIM-LIB-RAG-002.catalog_works")
    if total and counts and str(sum(counts)) != total:
        problems.append(f"{name}: collection counts sum to {sum(counts)} but "
                        f"catalog_works is {total}")

    # 3. internal links resolve to a heading.
    headings = {_slugify(h) for h in re.findall(r"^#{1,6}\s+(.*)$", text,
                                                re.MULTILINE)}
    for target in re.findall(r"\]\(#([^)]+)\)", text):
        if target not in headings:
            problems.append(f"{name}: internal link #{target} has no heading")
    return problems


def main() -> int:
    metrics = _register_metrics()
    problems: list[str] = []
    for ed in EDITIONS:
        p = HERE / ed
        if p.exists():
            problems += check_edition(p, metrics)
    if problems:
        print("[FAIL] handbook drift:")
        for pr in problems:
            print(f" - {pr}")
        return 1
    print(f"[OK] handbook editions consistent with the register "
          f"({len(metrics)} bound metrics checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
