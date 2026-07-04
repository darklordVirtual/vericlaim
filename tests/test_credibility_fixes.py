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
    _load_baseline,
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


# ── 4. the baseline fails CLOSED too ────────────────────────────────────────
# A malformed baseline must not crash the gate (uncaught traceback) nor be read
# as "no baseline" — either would silently change what the gate enforces.

def test_missing_baseline_is_empty(tmp_path):
    cfg = Config(root=tmp_path, baseline="nope.json")
    assert _load_baseline(cfg) == set()


def test_baseline_invalid_json_raises(tmp_path):
    (tmp_path / "baseline.json").write_text("{not json")
    cfg = Config(root=tmp_path, baseline="baseline.json")
    with pytest.raises(RegisterError):
        _load_baseline(cfg)


def test_baseline_entries_must_be_objects_with_error_id(tmp_path):
    # a list of bare strings used to raise TypeError (uncaught crash)
    (tmp_path / "baseline.json").write_text(
        '{"known_violations": ["stale-string:d.md:x"]}')
    cfg = Config(root=tmp_path, baseline="baseline.json")
    with pytest.raises(RegisterError):
        _load_baseline(cfg)


def test_baseline_known_violations_must_be_list(tmp_path):
    (tmp_path / "baseline.json").write_text('{"known_violations": {}}')
    cfg = Config(root=tmp_path, baseline="baseline.json")
    with pytest.raises(RegisterError):
        _load_baseline(cfg)


def test_wellformed_baseline_loads(tmp_path):
    (tmp_path / "baseline.json").write_text(
        '{"known_violations": [{"error_id": "stale-string:d.md:x", '
        '"reason": "legacy", "date": "2026-07-04"}]}')
    cfg = Config(root=tmp_path, baseline="baseline.json")
    assert _load_baseline(cfg) == {"stale-string:d.md:x"}


def test_gate_fails_cleanly_on_bad_baseline(tmp_path):
    # end-to-end: valid register, malformed baseline -> clean [FAIL], not a crash
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        'schema_version: "1"\nclaims: []\n')
    (tmp_path / "claims" / "baseline.json").write_text(
        '{"known_violations": ["bare-string-not-an-object"]}')
    cfg = Config(root=tmp_path, manifest=None, doc_globs=())
    assert run(cfg, quiet=True) == 1


# ── 5. single-pass id matcher (O(lines*claims) -> linear; no regex-cache thrash)
# The combined alternation must keep the exact whole-token semantics, including
# when one id is a token-prefix of another.

def test_id_matcher_whole_token_and_prefix_safe():
    by_id = {"CLAIM-1": {}, "CLAIM-EX-001": {}, "CLAIM-EX-0011": {},
             "ORG.PRODUCT-2026-001": {}}
    for cid in by_id:
        # '.' is part of the id-token class (ORG.PRODUCT-...), so delimit with a space
        assert _claim_ids_in_line(f"see {cid} here", by_id) == {cid}
    # a shorter id that is a token-prefix of a longer one must not match inside it
    assert _claim_ids_in_line("CLAIM-EX-0011 only", by_id) == {"CLAIM-EX-0011"}
    # a bare tail still must not match
    assert _claim_ids_in_line("EX-001 alone", by_id) == set()
    # empty register -> no matches, no crash
    assert _claim_ids_in_line("anything CLAIM-1", {}) == set()


def test_evidence_check_scales_without_cache_thrash(tmp_path):
    # >512 distinct ids used to thrash the interpreter regex cache and go
    # quadratic; assert it stays correct and quick on a large register.
    n = 800
    by_id = {f"CLAIM-{i:04d}": {"id": f"CLAIM-{i:04d}",
                                "evidence_level": "measured"} for i in range(n)}
    doc = tmp_path / "d.md"
    # one genuine drift line among many plain lines
    lines = [f"Item {i} is fine." for i in range(n)]
    lines.append("CLAIM-0500 is externally_validated here.")
    doc.write_text("\n".join(lines))
    cfg = Config(root=tmp_path)
    out = check_evidence_citations(cfg, doc, doc.read_text(), by_id)
    assert [e for e, _ in out] == [f"evidence-level-drift:d.md:{n + 1}:CLAIM-0500"]
