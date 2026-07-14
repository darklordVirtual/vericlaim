# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-CATALOG-001 — the AI-assurance literature catalogue,
validated row by row and mapped to the knowledge register.

The catalogue (docs/reference/ai_assurance_literature_catalog_2026-07-14_
enriched.csv) is the curated map of the AI-assurance literature this project
draws on: 10 sections from uncertainty quantification to runtime governance.
This script makes the catalogue itself claim-bound: it validates EVERY row
mechanically (unique non-empty ids, known section/type/source vocabularies,
sane years — versionless living specs may omit one — and at least one https
URL per row), counts the published shape, and maps which catalogue entries
are additionally DEEP-SEEDED as cited works in claimlib's hash-locked
literature layer (via an explicit, committed alias table — no fuzzy
matching). A malformed row fails the script, so the register can never
describe a catalogue that does not parse.

    python3 tools/ai_catalog_evidence.py [--output-dir DIR]
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "claimlib"))
sys.path.insert(0, str(ROOT / "claimlib" / "literature"))

from SOURCES import SOURCES  # noqa: E402
from vericlaim.provenance import stamp  # noqa: E402

CSV_PATH = ROOT / "docs" / "reference" / \
    "ai_assurance_literature_catalog_2026-07-14_enriched.csv"
ARTIFACT = ROOT / "claims" / "ai_catalog.json"

SECTIONS = {str(i) for i in range(1, 11)}
TYPES = {"paper", "report", "spec", "standard", "book"}
SOURCES_VOCAB = {"arxiv", "crossref", "doi", "web"}

# Catalogue id -> claimlib literature id, where the same WORK is deep-seeded
# as a cited entry in claimlib/literature (identical ids omitted — they map
# to themselves). Explicit and committed: an alias is a curatorial claim.
ALIASES = {
    "guo-calibration-2017": "guo-2017",
    "model-cards-2019": "mitchell-2019",
    "iso-42001-2023": "iso-iec-42001-2023",
    "nist-ai-rmf-2023": "nist-ai-rmf-1-0-2023",
    "eu-ai-act-2024": "eu-ai-act-2024-1689",
    "gdpr-2016": "gdpr-2016-679",
    "equality-opportunity-2016": "hardt-2016",
    "saltzer-schroeder-1975": "saltzer-1975",
    "slsa-v1": "slsa-v1-1",
    # NOT aliased: calibrating-noise-2006 (Dwork 2006) is a different work
    # than the Dwork-Roth 2014 book claimlib cites — same-work mapping only.
    "ct-rfc6962-2013": "rfc-6962",
    "dbc-1992": None,   # Meyer's DbC: cited in docs/manifesto, not claimlib
}

# Living specifications published without a fixed year — the only rows
# allowed an empty year field.
VERSIONLESS_OK = {"c4-model", "event-sourcing", "rules-of-ml", "c2pa-spec",
                  "cyclonedx-mlbom", "model-transparency-spec", "slsa-v1",
                  "spiffe-spec", "gsn-standard"}


def fail(msg: str) -> None:
    raise SystemExit(f"[catalog] {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    rows = list(csv.DictReader(CSV_PATH.open(encoding="utf-8-sig")))
    if not rows:
        fail("catalogue is empty")

    seen: set = set()
    per_section: dict = {s: 0 for s in sorted(SECTIONS, key=int)}
    per_type: dict = {}
    per_source: dict = {}
    p0 = 0
    with_pdf = 0
    for n, r in enumerate(rows, start=2):   # header is line 1
        rid = (r.get("id") or "").strip()
        if not rid:
            fail(f"line {n}: empty id")
        if rid in seen:
            fail(f"line {n}: duplicate id {rid!r}")
        seen.add(rid)
        if r["section"] not in SECTIONS:
            fail(f"{rid}: unknown section {r['section']!r}")
        if r["type"] not in TYPES:
            fail(f"{rid}: unknown type {r['type']!r}")
        if r["source"] not in SOURCES_VOCAB:
            fail(f"{rid}: unknown source {r['source']!r}")
        year = (r.get("year") or "").strip()
        if year:
            y = float(year)
            if not 1700 <= y <= 2026:
                fail(f"{rid}: implausible year {year!r}")
        elif rid not in VERSIONLESS_OK:
            fail(f"{rid}: missing year (not a known versionless spec)")
        pdf = (r.get("pdf_url") or "").strip()
        landing = (r.get("landing_url") or "").strip()
        if not pdf and not landing:
            fail(f"{rid}: no URL at all")
        for u in (pdf, landing):
            if u and not u.startswith("https://"):
                fail(f"{rid}: non-https URL {u!r}")
        per_section[r["section"]] += 1
        per_type[r["type"]] = per_type.get(r["type"], 0) + 1
        per_source[r["source"]] = per_source.get(r["source"], 0) + 1
        if r["priority"] == "p0":
            p0 += 1
        if pdf:
            with_pdf += 1

    lib_ids = {s["id"] for s in SOURCES}
    unknown_aliases = sorted(v for v in ALIASES.values()
                             if v is not None and v not in lib_ids)
    if unknown_aliases:
        fail(f"alias targets not in claimlib literature: {unknown_aliases}")
    stale_aliases = sorted(k for k in ALIASES if k not in seen)
    if stale_aliases:
        fail(f"alias keys not in the catalogue: {stale_aliases}")
    deep = {rid for rid in seen if rid in lib_ids}
    deep |= {k for k, v in ALIASES.items() if v is not None}

    payload = {
        "schema": "ai_catalog_v1",
        "csv": "docs/reference/"
               "ai_assurance_literature_catalog_2026-07-14_enriched.csv",
        "works_total": len(rows),
        "sections": len(per_section),
        "per_section": per_section,
        "per_type": dict(sorted(per_type.items())),
        "per_source": dict(sorted(per_source.items())),
        "p0_count": p0,
        "with_pdf": with_pdf,
        "deep_seeded_in_claimlib": len(deep),
        "deep_seeded_ids": sorted(deep),
        "duplicate_ids": 0,
        "rows_invalid": 0,
    }
    if args.output_dir:
        out = Path(args.output_dir) / ARTIFACT.name
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                       encoding="utf-8", newline="\n")
    else:
        ARTIFACT.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8", newline="\n")
        stamp("claims/ai_catalog.json",
              script="python3 tools/ai_catalog_evidence.py")
    print(f"catalog: {payload['works_total']} works / "
          f"{payload['sections']} sections validated; p0={p0}; "
          f"deep-seeded in claimlib: {payload['deep_seeded_in_claimlib']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
