# SPDX-License-Identifier: Apache-2.0
"""Tests for the chunker — deterministic, section-aware, content-addressed.

Chunks are the retrieval unit of the research layer. Same text in, same
shas out — always; manifests refuse to silently re-chunk a changed source.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import chunker  # noqa: E402

TEXT = (
    "Intro sentence one. Intro sentence two follows here.\n\n"
    "## 2 Methods\n"
    + " ".join(f"Method sentence number {i} with some padding words to "
               f"reach realistic sentence length overall." for i in range(60))
    + "\n## 3 Results\n"
    "The result was measured. It held under repetition."
)


def test_deterministic():
    a = chunker.chunk(TEXT)
    b = chunker.chunk(TEXT)
    assert [c["sha256"] for c in a] == [b2["sha256"] for b2 in b]
    assert [c["seq"] for c in a] == list(range(len(a)))


def test_sections_follow_headings():
    chunks = chunker.chunk(TEXT)
    sections = {c["section"] for c in chunks}
    assert "" in sections            # preamble before the first heading
    assert "2 Methods" in sections
    assert "3 Results" in sections


def test_size_bounds_and_shas():
    chunks = chunker.chunk(TEXT, target=300, overlap=80)
    for c in chunks:
        assert len(c["text"]) <= 2 * 300
        assert c["sha256"] == hashlib.sha256(
            c["text"].encode("utf-8")).hexdigest()


def test_overlap_between_consecutive_chunks_in_section():
    chunks = chunker.chunk(TEXT, target=300, overlap=80)
    methods = [c for c in chunks if c["section"] == "2 Methods"]
    assert len(methods) >= 2
    for prev, nxt in zip(methods, methods[1:]):
        # the next chunk starts with the tail of the previous one
        assert nxt["text"][:40] in prev["text"]


def test_manifest_roundtrip_and_source_lock(tmp_path):
    chunks = chunker.chunk(TEXT, target=300, overlap=80)
    src_sha = hashlib.sha256(TEXT.encode("utf-8")).hexdigest()
    path = chunker.write_manifest(tmp_path, "some_work", src_sha, chunks,
                                  target=300, overlap=80)
    lines = [json.loads(ln) for ln in path.read_text().splitlines()]
    head, rows = lines[0], lines[1:]
    assert head["fsid"] == "some_work" and head["n"] == len(chunks)
    assert head["source_sha256"] == src_sha
    assert [r["sha256"] for r in rows] == [c["sha256"] for c in chunks]
    assert "text" not in rows[0]  # texts live content-addressed, not here
    # same source: idempotent overwrite is fine
    chunker.write_manifest(tmp_path, "some_work", src_sha, chunks,
                           target=300, overlap=80)
    # changed source without refresh: refused
    with pytest.raises(ValueError, match="refresh"):
        chunker.write_manifest(tmp_path, "some_work", "ff" * 32, chunks,
                               target=300, overlap=80)
    chunker.write_manifest(tmp_path, "some_work", "ff" * 32, chunks,
                           target=300, overlap=80, refresh=True)


def test_long_sentence_hard_wrapped():
    long_sentence = "x" * 1000
    chunks = chunker.chunk(long_sentence, target=300, overlap=80)
    assert all(len(c["text"]) <= 600 for c in chunks)
    assert "".join(c["text"] for c in chunks).count("x") >= 1000
