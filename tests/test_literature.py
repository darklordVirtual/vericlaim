# SPDX-License-Identifier: Apache-2.0
"""Tests for literature references on claims.

A literature entry ties a claim to an external source (paper, standard, book)
in a hash-verified way: the gate can prove the cited document is *the same
document* you registered — never that the document is right, and never as a
substitute for a reproducible artifact. `artifact` stays required regardless.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from vericlaim.config import Config
from vericlaim.gate import check_literature
from vericlaim.register import load_register

GOOD_SHA = "a" * 64


def _cfg(tmp: Path, **over) -> Config:
    return Config(root=tmp, **over)


def _claim(lit) -> list[dict]:
    return [{"id": "C-1", "statement": "s", "evidence_level": "measured",
             "artifact": ["r.json"], "caveat": "c", "literature": lit}]


# ── subset parser: list of maps ──────────────────────────────────────────────

def test_subset_parser_reads_literature_list_of_maps():
    reg = (
        "claims:\n"
        "  - id: C-1\n"
        "    statement: s\n"
        "    evidence_level: measured\n"
        "    artifact:\n"
        "      - r.json\n"
        "    caveat: c\n"
        "    literature:\n"
        "      - source: \"doi:10.1000/xyz\"\n"
        f"        sha256: {GOOD_SHA}\n"
        "        file: refs/paper-note.md\n"
        "        locator: \"Theorem 3.2\"\n"
        "      - source: https://example.org/spec\n"
        f"        sha256: {GOOD_SHA}\n"
    )
    claims = load_register(reg)
    assert len(claims) == 1
    lit = claims[0]["literature"]
    assert isinstance(lit, list) and len(lit) == 2
    assert lit[0]["source"] == "doi:10.1000/xyz"
    assert lit[0]["file"] == "refs/paper-note.md"
    assert lit[0]["locator"] == "Theorem 3.2"
    assert lit[1] == {"source": "https://example.org/spec", "sha256": GOOD_SHA}


# ── gate check ───────────────────────────────────────────────────────────────

def test_valid_entry_without_file_passes(tmp_path):
    claims = _claim([{"source": "doi:10.1000/xyz", "sha256": GOOD_SHA}])
    assert check_literature(claims, _cfg(tmp_path)) == []


def test_missing_source_and_sha256_flagged(tmp_path):
    ids = [e for e, _ in check_literature(_claim([{}]), _cfg(tmp_path))]
    assert "literature-missing-field:C-1:0:source" in ids
    assert "literature-missing-field:C-1:0:sha256" in ids


def test_malformed_sha256_flagged(tmp_path):
    claims = _claim([{"source": "x", "sha256": "ABC123"}])
    ids = [e for e, _ in check_literature(claims, _cfg(tmp_path))]
    assert ids == ["literature-bad-sha256:C-1:0"]


def test_entry_not_a_map_flagged(tmp_path):
    ids = [e for e, _ in check_literature(_claim(["just-a-string"]),
                                          _cfg(tmp_path))]
    assert ids == ["literature-not-a-map:C-1:0"]


def test_committed_file_hash_match_and_mismatch(tmp_path):
    doc = b"axioms A1-A3 as stated by Lukasiewicz\n"
    (tmp_path / "refs").mkdir()
    (tmp_path / "refs" / "note.md").write_bytes(doc)
    sha = hashlib.sha256(doc).hexdigest()
    claims = _claim([{"source": "doi:x", "sha256": sha, "file": "refs/note.md"}])
    cfg = _cfg(tmp_path)
    assert check_literature(claims, cfg) == []
    # tamper with the committed copy -> the citation no longer verifies
    (tmp_path / "refs" / "note.md").write_bytes(b"altered\n")
    ids = [e for e, _ in check_literature(claims, cfg)]
    assert ids == ["literature-hash-mismatch:C-1:refs/note.md"]


def test_file_missing_and_escaping_root_flagged(tmp_path):
    claims = _claim([
        {"source": "x", "sha256": GOOD_SHA, "file": "refs/gone.md"},
        {"source": "y", "sha256": GOOD_SHA, "file": "../outside.md"},
    ])
    ids = [e for e, _ in check_literature(claims, _cfg(tmp_path))]
    assert "literature-file-missing:C-1:refs/gone.md" in ids
    assert "literature-escapes-root:C-1:../outside.md" in ids


def test_single_map_entry_is_normalized(tmp_path):
    # PyYAML-style `literature: {source: ..., sha256: ...}` (one entry, no list)
    claims = _claim({"source": "doi:x", "sha256": GOOD_SHA})
    assert check_literature(claims, _cfg(tmp_path)) == []
