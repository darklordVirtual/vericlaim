# SPDX-License-Identifier: Apache-2.0
"""The canonical research map — the library's coverage contract.

`research/canon.toml` lists every work the literature catalog is expected to
hold: title, author surnames, year, kind and which registrar should be able
to verify it. Coverage (coverage.py) is measured against THIS file, so the
loader is fail-closed: one malformed entry aborts the load. A coverage
number computed against a silently-shrunk canon proves nothing.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

COLLECTIONS = (
    "01_uncertainty_and_routing",
    "02_llm_and_agent_architectures",
    "03_evaluation_and_calibration",
    "04_agent_security",
    "05_ai_governance",
    "06_mlops_and_enterprise_architecture",
    "07_provenance_and_supply_chain",
    "08_formal_methods",
    "09_fairness_privacy_and_human_impact",
    "10_assurance_cases_and_runtime_verification",
)

KINDS = {"paper", "book", "standard", "spec", "report"}
REGISTRARS = {"arxiv", "crossref", "doi", "web"}
_YEARLESS_KINDS = {"standard", "spec"}


def load(path: Path) -> list[dict]:
    """Load and validate the canon. Raises ValueError naming the offending
    entry on the first problem found."""
    raw = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    entries: list[dict] = []
    seen: set[str] = set()
    for i, work in enumerate(raw.get("work", [])):
        wid = work.get("id")
        if not wid or not isinstance(wid, str):
            raise ValueError(f"work #{i}: missing id")
        if wid in seen:
            raise ValueError(f"duplicate canon id: {wid}")
        seen.add(wid)
        collection = work.get("collection")
        if collection not in COLLECTIONS:
            raise ValueError(f"{wid}: unknown collection {collection!r}")
        title = work.get("title")
        if not title or not isinstance(title, str):
            raise ValueError(f"{wid}: missing title")
        authors = work.get("authors")
        if not authors or not isinstance(authors, list):
            raise ValueError(f"{wid}: authors must be a non-empty list")
        kind = work.get("kind")
        if kind not in KINDS:
            raise ValueError(f"{wid}: unknown kind {kind!r}")
        registrar = work.get("registrar")
        if registrar not in REGISTRARS:
            raise ValueError(f"{wid}: unknown registrar {registrar!r}")
        year = work.get("year")
        if year is None and kind not in _YEARLESS_KINDS:
            raise ValueError(f"{wid}: year required for kind {kind!r}")
        if year is not None and not isinstance(year, int):
            raise ValueError(f"{wid}: year must be an integer")
        entries.append({
            "id": wid, "collection": collection, "title": title,
            "authors": [str(a) for a in authors], "year": year,
            "kind": kind, "registrar": registrar,
            "p0": bool(work.get("p0", False)),
            "top15": bool(work.get("top15", False)),
            # optional acquisition seeds — NEVER trusted, only searched;
            # the title+author+year guard decides against the registrar
            "doi": work.get("doi"),
            "url": work.get("url"),
        })
    return entries
