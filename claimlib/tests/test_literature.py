# SPDX-License-Identifier: Apache-2.0
"""The literature layer is integrity-checked: every entry's summary is hash-locked
and every module reference resolves.

This is the citation half of Claim-Oriented Programming -- the bibliography is
committed and bound to code, so a drifted summary or a dangling reference fails
the suite exactly like a drifted evidence number fails the gate.
"""
import hashlib
import json
import sys
from pathlib import Path

CLAIMLIB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLAIMLIB))
sys.path.insert(0, str(CLAIMLIB / "literature"))

from SOURCES import SOURCES  # noqa: E402
from MODULES import MODULES  # noqa: E402

LIT_DIR = CLAIMLIB / "literature"
IDS = {s["id"] for s in SOURCES}


def test_every_source_written_and_hash_locked():
    for src in SOURCES:
        path = LIT_DIR / f"{src['id']}.json"
        assert path.exists(), f"missing literature file for {src['id']}"
        rec = json.loads(path.read_text(encoding="utf-8"))
        # The committed summary_sha256 must match a fresh hash of the summary.
        assert rec["summary_sha256"] == hashlib.sha256(
            src["summary"].encode("utf-8")).hexdigest(), f"summary drift in {src['id']}"
        assert rec["title"] == src["title"]
        assert rec["identifier"] == src["identifier"]


def test_index_matches_sources():
    index = json.loads((LIT_DIR / "INDEX.json").read_text(encoding="utf-8"))
    assert set(index) == IDS
    for src in SOURCES:
        assert index[src["id"]]["summary_sha256"] == hashlib.sha256(
            src["summary"].encode("utf-8")).hexdigest()


def test_no_duplicate_ids():
    ids = [s["id"] for s in SOURCES]
    assert len(ids) == len(set(ids))


def test_every_module_reference_resolves():
    for mod in MODULES:
        for ref in mod.get("references", []):
            assert ref in IDS, f"{mod['name']} cites unknown literature id {ref!r}"


def test_bibliography_generated():
    biblio = (LIT_DIR / "BIBLIOGRAPHY.md").read_text(encoding="utf-8")
    for src in SOURCES:
        assert src["identifier"] in biblio
