# SPDX-License-Identifier: Apache-2.0
"""Tests for generic extraction (arbitrary repos), gaps, and scaffolding.

The quarantine rule under test: assertions extracted from a repo WITHOUT a
gate-verified register become `candidate` bundles — never verified claims.
They carry a quarantine caveat, cite their exact file:line, and get a
scaffolded evidence script that FAILS until a curator completes it — the
tooling never fabricates evidence.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from bundlefmt import load_bundle  # noqa: E402
from extract_candidates import extract_repo, scaffold_evidence  # noqa: E402
from gaps import gaps_report  # noqa: E402


def _mk_repo(tmp: Path) -> Path:
    repo = tmp / "wild"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text(
        "# wildproj\n\n"
        "Our parser is 3.5x faster than v1 on the internal corpus.\n\n"
        "It supports 12 file formats.\n\n"
        "Some prose without any numeric assertion at all.\n\n"
        "```\nfake example: 99x faster inside a fence\n```\n")
    (repo / "docs" / "notes.md").write_text(
        "Accuracy reaches 91.2% on the eval set.\n")
    return repo


def test_extract_builds_quarantined_candidates(tmp_path):
    repo = _mk_repo(tmp_path)
    out = tmp_path / "lib"
    results = extract_repo(repo, out, {"repo": "github.com/x/wild"})
    assert len(results) == 3          # two README lines + one docs line, no fence
    bundles = [load_bundle(out / bid) for bid in results.values()]
    for b in bundles:
        assert b["status"] == "candidate"
        assert b["claim"]["evidence_level"] == "theoretical"
        assert "NOT verified" in b["claim"]["caveat"]
        assert b["claim"]["artifact"] == []          # no artifact — that is the point
        assert b["provenance"]["source_gate"] == "none"
        assert ":" in b["provenance"]["extracted_from"]  # file:line
    statements = {b["claim"]["statement"] for b in bundles}
    assert any("3.5x faster" in s for s in statements)
    assert any("supports 12 file formats" in s for s in statements)
    assert any("91.2%" in s for s in statements)
    assert not any("99x" in s for s in statements)   # fenced example ignored


def test_candidate_ids_are_stable(tmp_path):
    repo = _mk_repo(tmp_path)
    r1 = extract_repo(repo, tmp_path / "a", {"repo": "x"})
    r2 = extract_repo(repo, tmp_path / "b", {"repo": "x"})
    assert list(r1) == list(r2)       # same ids for same content


def test_scaffold_evidence_fails_until_completed(tmp_path):
    claim = {"id": "CAND-WILD-001", "statement": "parser is 3.5x faster",
             "evidence_level": "theoretical", "artifact": [], "caveat": "c"}
    script = scaffold_evidence(claim, tmp_path)
    assert script.exists()
    text = script.read_text()
    assert "CAND-WILD-001" in text and "stamp(" in text
    proc = subprocess.run([sys.executable, str(script)], capture_output=True)
    assert proc.returncode != 0       # unmodified scaffold must not "pass"
    assert b"complete" in proc.stderr.lower() or b"notimplemented" in proc.stderr.lower()


def test_gaps_report_lists_curation_worklist(tmp_path):
    from bundlefmt import build_bundle
    lib = tmp_path / "lib"
    build_bundle(lib, claim={"id": "V-1", "statement": "s",
                             "evidence_level": "benchmarked",
                             "artifact": ["artifacts/r.json"], "caveat": "c"},
                 provenance={"source_repo": "x"},
                 files={"artifacts/r.json": b"{}"}, status="verified")
    build_bundle(lib, claim={"id": "C-1", "statement": "s2",
                             "evidence_level": "theoretical",
                             "artifact": [], "caveat": "c"},
                 provenance={"source_repo": "y"},
                 files={}, status="candidate")
    rep = gaps_report(lib)
    assert rep["n_bundles"] == 2
    assert "V-1" in rep["missing_literature"]      # verified but unsourced
    assert "C-1" in rep["candidates_pending_evidence"]
    assert "V-1" not in rep["candidates_pending_evidence"]
