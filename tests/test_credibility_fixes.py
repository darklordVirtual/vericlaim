# SPDX-License-Identifier: Apache-2.0
"""Tests for the credibility-release fixes (external review, v0.1):

1. multi-segment claim-id matching in the evidence-level check;
2. artifact paths cannot escape the repository root (+ optional git-tracking);
3. the register fails CLOSED — a misparse never silently disables the gate.
"""
from __future__ import annotations

import pytest

from vericlaim.config import Config
from vericlaim.gate import (
    _claim_ids_in_line,
    check_artifacts,
    check_evidence_citations,
    run,
)
from vericlaim.register import RegisterError, load_register


# ── 1. multi-segment claim ids ──────────────────────────────────────────────

def test_claim_ids_match_whole_multisegment():
    by_id = {"CLAIM-1": {}, "CLAIM-EX-001": {}, "CLAIM-CORE-001": {},
             "ORG.PRODUCT-2026-001": {}}
    for cid in by_id:
        assert _claim_ids_in_line(f"see {cid} for details", by_id) == {cid}
    # a tail must NOT match on its own
    assert _claim_ids_in_line("EX-001 alone", by_id) == set()


def test_evidence_level_drift_detected_for_multisegment_id(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("CLAIM-EX-001 is externally_validated.\n")
    by_id = {"CLAIM-EX-001": {"id": "CLAIM-EX-001", "evidence_level": "benchmarked"}}
    cfg = Config(root=tmp_path)
    ids = [e for e, _ in check_evidence_citations(cfg, doc, doc.read_text(), by_id)]
    assert ids == ["evidence-level-drift:d.md:1:CLAIM-EX-001"]  # was silently skipped before


# ── 2. path containment ─────────────────────────────────────────────────────

def test_artifact_escaping_root_is_flagged(tmp_path):
    outside = tmp_path.parent / "outside.json"
    outside.write_text("{}")
    proj = tmp_path / "proj"
    proj.mkdir()
    cfg = Config(root=proj)
    claim = {"id": "C-1", "artifact": ["../outside.json"]}
    ids = [e for e, _ in check_artifacts([claim], cfg)]
    assert ids == ["artifact-escapes-root:C-1:../outside.json"]


def test_absolute_path_is_flagged(tmp_path):
    cfg = Config(root=tmp_path)
    claim = {"id": "C-1", "artifact": ["/etc/hosts"]}
    ids = [e for e, _ in check_artifacts([claim], cfg)]
    assert ids == ["artifact-escapes-root:C-1:/etc/hosts"]


def test_in_repo_artifact_ok(tmp_path):
    (tmp_path / "r.json").write_text("{}")
    cfg = Config(root=tmp_path)
    assert check_artifacts([{"id": "C-1", "artifact": ["r.json"]}], cfg) == []


def test_untracked_artifact_flagged_when_required(tmp_path):
    (tmp_path / "r.json").write_text("{}")  # not a git repo -> not tracked
    cfg = Config(root=tmp_path, require_git_tracked=True)
    ids = [e for e, _ in check_artifacts([{"id": "C-1", "artifact": ["r.json"]}], cfg)]
    assert ids == ["artifact-untracked:C-1:r.json"]


# ── 3. fail-closed register parsing ─────────────────────────────────────────

def test_empty_register_is_valid():
    assert load_register("schema_version: \"1\"\nclaims: []\n") == []


def test_unsupported_schema_version_fails():
    # Parser-agnostic: checked before parsing.
    with pytest.raises(RegisterError):
        load_register("schema_version: \"99\"\nclaims: []\n")


def test_pyyaml_parse_error_fails_closed():
    pytest.importorskip("yaml")
    with pytest.raises(RegisterError):
        load_register("claims:\n  - id: C-1\n  bad: : :\n")


def test_bundled_parser_undercount_fails_closed(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "yaml", None)  # force the bundled parser
    # `- id:` present but at an indent the bundled parser drops -> 0 claims.
    with pytest.raises(RegisterError):
        load_register("claims:\n- id: C-1\n  statement: x\n")


def test_gate_fails_closed_on_bad_register(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "schema_version: \"99\"\nclaims: []\n")  # parser-agnostic hard reject
    (tmp_path / "claims" / "baseline.json").write_text('{"known_violations": []}')
    cfg = Config(root=tmp_path, manifest=None, doc_globs=())
    assert run(cfg, quiet=True) == 1  # hard failure, not a silent green
