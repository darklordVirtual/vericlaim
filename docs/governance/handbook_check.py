# SPDX-License-Identifier: Apache-2.0
"""Governance-handbook validator — the meta-control the handbook itself needs.

The handbook lives OUTSIDE doc_globs on purpose (it is a synthesis over the
registers, not a source of primary claims). But that means it could drift in
exactly the way vericlaim exists to prevent. This checker closes that gap
without forcing the whole narrative into numeric anchors.

It walks EVERY governance edition RECURSIVELY (`docs/governance/**/*.md`) — the
English and Norwegian masters, the print editions, and the executive/board/case-
study/front-matter editions — so a new or variant edition is validated
automatically and cannot drift uncaught. Per edition it verifies:

  1. Register-derived numbers agree — for a *full handbook* (master or print),
     every metric the handbook quotes from the CLAIM-LIB-RAG family (canon works,
     verified, drops, chunks) appears with the register's current value.
  2. The collection index is internally consistent — the Appendix A per-
     collection counts sum to the catalog_works total (full handbooks).
  3. Internal navigation is intact — every in-page link `](#slug)` resolves to a
     real heading (ALL editions).
  4. The coupling / SecOps crosswalks are internally consistent wherever they
     appear (self-guarded by claim id).

The shorter editions get checks 3–4 only: they were never meant to restate every
register metric, so requiring it would be a false failure, not a real one.

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


def _is_full_handbook(text: str) -> bool:
    """A "full handbook" (master or print edition) restates every register metric
    and carries the Appendix A collection table. The shorter editions (executive,
    board note, case studies, front matter) do not, so they get the universal
    checks only — never a false 'metric absent' failure for a number they were
    never meant to quote."""
    return bool(re.search(r"^\|\s*\d{2}\s*\|[^|]+\|\s*\d+\s*\|$", text, re.MULTILINE))


def check_edition(path: Path, metrics: dict[str, str]) -> list[str]:
    problems: list[str] = []
    text = path.read_text(encoding="utf-8")
    try:
        name = path.relative_to(HERE).as_posix()  # stable, folder-aware label
    except ValueError:
        name = path.name
    full = _is_full_handbook(text)

    if full:
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

    # 3. internal links resolve to a heading (EVERY edition, recursively).
    headings = {_slugify(h) for h in re.findall(r"^#{1,6}\s+(.*)$", text,
                                                re.MULTILINE)}
    for target in re.findall(r"\]\(#([^)]+)\)", text):
        if target not in headings:
            problems.append(f"{name}: internal link #{target} has no heading")

    # 4. cross-cloud coupling chapter (CLAIM-COUPLE-001) is internally
    # consistent — the crosswalk has 6 dimension rows and 13 standard rows, and
    # clouds*dimensions == cells, matching the headline numbers stated in prose.
    # CLAIM-COUPLE-001 lives in the claims-library register (a separate repo),
    # so we cannot bind it via the vericlaim register here; internal
    # consistency is the anti-drift guarantee for these numbers.
    if "CLAIM-COUPLE-001" in text:
        problems += _check_coupling(text, name)
    if "CLAIM-SECOPS-001" in text:
        problems += _check_secops(text, name)
    return problems


# Expected structure of the SecOps crosswalk, matching CLAIM-SECOPS-001.
_SECOPS = {"domains": 8, "standards": 13, "practices": 33}


def _check_secops(text: str, name: str) -> list[str]:
    out: list[str] = []
    s = _SECOPS
    m = re.search(r"^#{1,3}\s*29\.\s.*?(?=\n---\n---|\Z)",
                  text, re.MULTILINE | re.DOTALL)
    chapter = m.group(0) if m else ""
    if not chapter:
        out.append(f"{name}: SecOps chapter (29) not found")
        return out
    # the crosswalk table: rows whose last column names a control objective.
    dom_rows = re.findall(r"^\|[^|\n]+\|[^|\n]+\|[^|\n]+\|"
                          r"[^|\n]*(?:Accountability|Monitoring|Privacy|"
                          r"Robustness|Logging|oversight|risk)[^|\n]*\|$",
                          chapter, re.MULTILINE | re.IGNORECASE)
    if len(dom_rows) != s["domains"]:
        out.append(f"{name}: SecOps crosswalk has {len(dom_rows)} domain rows, "
                   f"expected {s['domains']}")
    for key in ("domains", "standards", "practices"):
        if not re.search(rf"(?<!\d){s[key]}(?!\d)", chapter):
            out.append(f"{name}: SecOps {key}={s[key]} not stated in chapter")
    return out


# Expected structure of the coupling crosswalk, matching CLAIM-COUPLE-001.
_COUPLING = {"clouds": 4, "dimensions": 6, "cells": 24, "standards": 13}


def _check_coupling(text: str, name: str) -> list[str]:
    out: list[str] = []
    c = _COUPLING
    if c["clouds"] * c["dimensions"] != c["cells"]:
        out.append(f"{name}: coupling arithmetic clouds*dimensions != cells")
    # Scope table checks to the coupling chapter only (heading 28 through the
    # part divider), so Appendix A's collection table cannot be miscounted.
    m = re.search(r"^#{1,3}\s*28\.\s.*?(?=\n---\n---|\Z)",
                  text, re.MULTILINE | re.DOTALL)
    chapter = m.group(0) if m else ""
    if not chapter:
        out.append(f"{name}: coupling chapter (28) not found")
        return out
    # the crosswalk table: rows whose last column is a "Portable seam".
    dim_rows = re.findall(r"^\|[^|\n]+\|[^|\n]+\|[^|\n]+\|[^|\n]+\|[^|\n]+\|"
                          r"[^|\n]*(?:OIDC|Rego|SPIFFE|OAuth|mTLS|OpenTelemetry)"
                          r"[^|\n]*\|$", chapter, re.MULTILINE)
    if len(dim_rows) != c["dimensions"]:
        out.append(f"{name}: coupling crosswalk has {len(dim_rows)} dimension "
                   f"rows, expected {c['dimensions']}")
    # the standards table: numbered rows 1..13.
    std_rows = re.findall(r"^\|\s*(\d+)\s*\|[^|\n]+\|[^|\n]+\|$", chapter,
                          re.MULTILINE)
    std_nums = sorted(int(n) for n in std_rows)
    if std_nums != list(range(1, c["standards"] + 1)):
        out.append(f"{name}: coupling standards table numbered {std_nums}, "
                   f"expected 1..{c['standards']}")
    for key in ("clouds", "dimensions", "cells", "standards"):
        if not re.search(rf"(?<!\d){c[key]}(?!\d)", chapter):
            out.append(f"{name}: coupling {key}={c[key]} not stated in chapter")
    return out


def _editions() -> list[Path]:
    """Every governance markdown file, discovered RECURSIVELY — so a new edition
    (or a print/executive variant) is validated automatically and cannot drift
    uncaught. 'Gold standard, recursively.'"""
    return sorted(HERE.rglob("*.md"))


def main() -> int:
    metrics = _register_metrics()
    editions = _editions()
    problems: list[str] = []
    n_full = 0
    for p in editions:
        text = p.read_text(encoding="utf-8")
        if _is_full_handbook(text):
            n_full += 1
        problems += check_edition(p, metrics)
    if problems:
        print("[FAIL] handbook drift:")
        for pr in problems:
            print(f" - {pr}")
        return 1
    print(f"[OK] {len(editions)} governance edition(s) consistent with the register "
          f"({n_full} full handbook(s) × {len(metrics)} bound metrics; links + "
          f"crosswalks checked in all).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
