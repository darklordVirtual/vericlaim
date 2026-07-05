# SPDX-License-Identifier: Apache-2.0
"""Tests for the canonical research map — the coverage contract.

The canon is a machine-readable list of every work the library MUST either
hold (registrar-verified, snapshotted) or honestly drop with a reason. The
loader is fail-closed: a malformed entry stops the whole load, because a
coverage check against a silently-shrunk canon proves nothing.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import canon  # noqa: E402

GOOD = textwrap.dedent("""
    [[work]]
    id = "shannon-1948"
    collection = "01_uncertainty_and_routing"
    title = "A Mathematical Theory of Communication"
    authors = ["Shannon"]
    year = 1948
    kind = "paper"
    registrar = "crossref"
    p0 = true
""")


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "canon.toml"
    p.write_text(body, encoding="utf-8")
    return p


def test_load_valid_applies_defaults(tmp_path):
    entries = canon.load(_write(tmp_path, GOOD))
    assert len(entries) == 1
    e = entries[0]
    assert e["id"] == "shannon-1948"
    assert e["p0"] is True
    assert e["top15"] is False  # defaulted
    assert e["authors"] == ["Shannon"]


def test_duplicate_id_rejected(tmp_path):
    with pytest.raises(ValueError, match="shannon-1948"):
        canon.load(_write(tmp_path, GOOD + GOOD))


def test_unknown_collection_rejected(tmp_path):
    bad = GOOD.replace("01_uncertainty_and_routing", "99_nope")
    with pytest.raises(ValueError, match="99_nope"):
        canon.load(_write(tmp_path, bad))


def test_unknown_kind_rejected(tmp_path):
    bad = GOOD.replace('kind = "paper"', 'kind = "poem"')
    with pytest.raises(ValueError, match="kind"):
        canon.load(_write(tmp_path, bad))


def test_unknown_registrar_rejected(tmp_path):
    bad = GOOD.replace('registrar = "crossref"', 'registrar = "wikipedia"')
    with pytest.raises(ValueError, match="registrar"):
        canon.load(_write(tmp_path, bad))


def test_missing_authors_rejected(tmp_path):
    bad = GOOD.replace('authors = ["Shannon"]', "authors = []")
    with pytest.raises(ValueError, match="authors"):
        canon.load(_write(tmp_path, bad))


def test_missing_year_only_allowed_for_standards_and_specs(tmp_path):
    no_year = GOOD.replace("year = 1948\n", "")
    with pytest.raises(ValueError, match="year"):
        canon.load(_write(tmp_path, no_year))
    ok = no_year.replace('kind = "paper"', 'kind = "spec"')
    entries = canon.load(_write(tmp_path, ok))
    assert entries[0]["year"] is None


def test_real_canon_loads_and_covers_the_map():
    entries = canon.load(ROOT / "integrations/library/research/canon.toml")
    assert len(entries) >= 90
    assert sum(1 for e in entries if e["top15"]) >= 15
    assert {e["collection"] for e in entries} == set(canon.COLLECTIONS)
