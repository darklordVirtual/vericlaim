# SPDX-License-Identifier: Apache-2.0
"""Tests for the literature push — batches built purely from the catalog.

build_batches is pure and offline-testable: it walks works + chunk
manifests, re-verifies every chunk text against its content address before
it is allowed into a request body (fail-closed), and maps work records to
the Worker's WorkIn shape. Dedupe happens server-side; re-pushing the whole
catalog is always safe.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import chunker  # noqa: E402
import push_literature  # noqa: E402
from litindex import add_fulltext, add_work, link  # noqa: E402

WORK = {"work_id": "arxiv:2208.02814", "registrar": "arxiv",
        "title": "Conformal Risk Control", "abstract": "We extend...",
        "authors": ["Anastasios N. Angelopoulos"], "year": 2022,
        "venue": "arXiv", "source_type": "preprint", "accredited": False,
        "url": "https://arxiv.org/abs/2208.02814"}

TEXT = ("Conformal risk control. " +
        " ".join(f"Sentence {i} about controlling expected loss with "
                 f"conformal guarantees in deployment." for i in range(40)))


def _catalog(tmp_path: Path) -> Path:
    litroot = tmp_path / "literature"
    add_work(litroot, WORK, {"method": "arxiv-title-phrase",
                             "canon_id": "conformal-risk-2022"})
    sha = add_fulltext(litroot, WORK["work_id"], TEXT,
                       {"method": "arxiv-html", "url": "u"})
    chunks = chunker.chunk(TEXT, target=300, overlap=80)
    chunker._store_chunk_texts(litroot, chunks)
    chunker.write_manifest(litroot, "arxiv_2208-02814", sha, chunks,
                           target=300, overlap=80)
    link(litroot, "CLAIM-011", WORK["work_id"],
         method="curator:manual", score=1.0, ts="2026-07-05")
    return litroot


def test_build_batches_complete_and_verified(tmp_path):
    litroot = _catalog(tmp_path)
    batches = push_literature.build_batches(litroot, batch_chunks=4)
    all_chunks = [c for b in batches for c in b["chunks"]]
    manifest = (litroot / "chunks" / "arxiv_2208-02814.jsonl").read_text()
    n_expected = len(manifest.splitlines()) - 1
    assert len(all_chunks) == n_expected
    assert len({c["sha"] for c in all_chunks}) == n_expected
    for c in all_chunks:
        assert hashlib.sha256(c["text"].encode()).hexdigest() == c["sha"]
        assert c["fsid"] == "arxiv_2208-02814"
    for b in batches:
        assert len(b["chunks"]) <= 4
    # the work record rides along (at least once), mapped to WorkIn shape
    w = batches[0]["works"][0]
    assert w["fsid"] == "arxiv_2208-02814"
    assert w["work_id"] == "arxiv:2208.02814"
    assert w["tier"] == "arxiv-title-phrase"
    assert w["accredited"] is False
    assert w["linked_claims"] == ["CLAIM-011"]


def test_build_batches_fails_closed_on_tampered_chunk(tmp_path):
    litroot = _catalog(tmp_path)
    manifest = litroot / "chunks" / "arxiv_2208-02814.jsonl"
    lines = manifest.read_text().splitlines()
    import json
    row = json.loads(lines[1])
    (litroot / "texts" / f"{row['sha256']}.txt").write_text("tampered")
    with pytest.raises(ValueError, match="hash"):
        push_literature.build_batches(litroot, batch_chunks=4)


def test_web_snapshot_tier_mapping(tmp_path):
    litroot = tmp_path / "literature"
    add_work(litroot, {"work_id": "web:slsa.dev/spec", "registrar":
                       "web-snapshot", "title": "SLSA levels",
                       "abstract": "Levels of assurance. More text here.",
                       "authors": ["SLSA / OpenSSF"], "year": None,
                       "venue": "SLSA / OpenSSF",
                       "source_type": "web-snapshot", "accredited": False,
                       "url": "https://slsa.dev/spec"},
             {"method": "web-snapshot", "url": "https://slsa.dev/spec"})
    chunks = chunker.run_all(litroot, target=300, overlap=80)
    assert chunks
    batches = push_literature.build_batches(litroot, batch_chunks=10)
    w = batches[0]["works"][0]
    assert w["tier"] == "web-snapshot" and w["accredited"] is False
