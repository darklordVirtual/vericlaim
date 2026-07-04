# SPDX-License-Identifier: Apache-2.0
"""Tests for the claim-bundle format (integrations/library/bundlefmt.py).

A bundle is the library's unit of preservation: claim + evidence + code +
literature, content-addressed by the sha256 of its canonical manifest. The
format must be deterministic (same content -> same id) and verification must
be fail-closed: any tampered, missing, or extra byte is detected.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from bundlefmt import BundleError, build_bundle, bundle_id_of, verify_bundle  # noqa: E402

CLAIM = {"id": "CLAIM-X-001", "statement": "s", "evidence_level": "benchmarked",
         "artifact": ["artifacts/r.json"], "caveat": "c",
         "metrics": {"ratio": 2.5}}
PROV = {"source_repo": "github.com/x/y", "source_commit": "abc123",
        "source_claim_id": "CLAIM-X-001", "source_evidence_level": "internal_benchmark",
        "level_mapping": "internal_benchmark->benchmarked", "source_gate": "passed"}


def _build(tmp: Path, **over):
    files = over.pop("files", {"artifacts/r.json": b'{"ratio": 2.5}\n',
                               "code/bench.py": b"print('hi')\n",
                               "literature/note.md": b"# note\n"})
    return build_bundle(tmp / "out", claim=over.pop("claim", CLAIM),
                        provenance=over.pop("provenance", PROV),
                        files=files, status=over.pop("status", "verified"))


def test_build_writes_canonical_layout_and_returns_id(tmp_path):
    bid, bdir = _build(tmp_path)
    assert len(bid) == 64 and bid == bid.lower()
    assert bdir == tmp_path / "out" / bid
    for rel in ("claim.json", "provenance.json", "MANIFEST.json",
                "artifacts/r.json", "code/bench.py", "literature/note.md"):
        assert (bdir / rel).exists(), rel
    man = json.loads((bdir / "MANIFEST.json").read_text())
    assert man["schema"] == "bundle_v1"
    assert man["status"] == "verified"
    assert set(man["files"]) == {"claim.json", "provenance.json",
                                 "artifacts/r.json", "code/bench.py",
                                 "literature/note.md"}


def test_bundle_id_is_deterministic_and_content_sensitive(tmp_path):
    bid1, _ = _build(tmp_path / "a")
    bid2, _ = _build(tmp_path / "b")
    assert bid1 == bid2                      # same content -> same id
    bid3, _ = _build(tmp_path / "c",
                     files={"artifacts/r.json": b'{"ratio": 9.9}\n'})
    assert bid3 != bid1                      # any changed byte -> new id


def test_verify_roundtrip_passes(tmp_path):
    _, bdir = _build(tmp_path)
    report = verify_bundle(bdir)
    assert report["ok"] is True
    assert report["bundle_id"] == bundle_id_of(bdir)


def test_verify_detects_tampered_file(tmp_path):
    _, bdir = _build(tmp_path)
    (bdir / "artifacts" / "r.json").write_bytes(b'{"ratio": 9.9}\n')
    with pytest.raises(BundleError, match="artifacts/r.json"):
        verify_bundle(bdir)


def test_verify_detects_tampered_claim_and_missing_and_extra(tmp_path):
    _, bdir = _build(tmp_path)
    claim = json.loads((bdir / "claim.json").read_text())
    claim["metrics"]["ratio"] = 9.9
    (bdir / "claim.json").write_text(json.dumps(claim))
    with pytest.raises(BundleError, match="claim.json"):
        verify_bundle(bdir)

    _, bdir2 = _build(tmp_path / "m")
    (bdir2 / "code" / "bench.py").unlink()
    with pytest.raises(BundleError, match="code/bench.py"):
        verify_bundle(bdir2)

    _, bdir3 = _build(tmp_path / "x")
    (bdir3 / "artifacts" / "sneaked.json").write_bytes(b"{}")
    with pytest.raises(BundleError, match="sneaked"):
        verify_bundle(bdir3)


def test_dir_name_mismatch_is_detected(tmp_path):
    # Renaming a bundle dir cannot re-label its content.
    _, bdir = _build(tmp_path)
    renamed = bdir.parent / ("0" * 64)
    bdir.rename(renamed)
    with pytest.raises(BundleError, match="bundle_id"):
        verify_bundle(renamed)


def test_status_candidate_is_recorded_and_hashed(tmp_path):
    bid_v, _ = _build(tmp_path / "v", status="verified")
    bid_c, bdir_c = _build(tmp_path / "c", status="candidate")
    assert bid_v != bid_c                    # status is part of identity
    assert json.loads((bdir_c / "MANIFEST.json").read_text())["status"] == "candidate"
