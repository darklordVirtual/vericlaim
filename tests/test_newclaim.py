# SPDX-License-Identifier: Apache-2.0
"""Tests for `vericlaim new-claim` scaffolding."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from vericlaim.newclaim import scaffold

ROOT = Path(__file__).resolve().parents[1]


def test_scaffold_writes_stub_and_blocks(tmp_path):
    out = scaffold(tmp_path, claim_id="CLAIM-X-001",
                   statement="It supports 6 languages.", evidence_level="measured",
                   artifact="results/x.json", script="tools/x.py",
                   metrics={"n_languages": "6"}, caveat="Example only.")
    assert out["script_created"]
    assert (tmp_path / "tools" / "x.py").exists()
    assert "- id: CLAIM-X-001" in out["register_block"]
    assert "n_languages: 6" in out["register_block"]           # numeric, unquoted
    assert "<!-- claim:CLAIM-X-001 n_languages -->" in out["doc_anchor"]
    assert "<!-- v:CLAIM-X-001.n_languages -->**6**" in out["doc_anchor"]


def test_refuses_unsafe_paths(tmp_path):
    with pytest.raises(ValueError):
        scaffold(tmp_path, claim_id="C-1", statement="s", evidence_level="measured",
                 artifact="../escape.json", script="tools/x.py", metrics={}, caveat="c")


def test_refuses_overwrite(tmp_path):
    kw = dict(claim_id="C-1", statement="s", evidence_level="measured",
              artifact="results/x.json", script="tools/x.py", metrics={}, caveat="c")
    scaffold(tmp_path, **kw)
    with pytest.raises(ValueError):
        scaffold(tmp_path, **kw)


def test_stub_measure_fails_until_implemented(tmp_path):
    scaffold(tmp_path, claim_id="C-1", statement="s", evidence_level="measured",
             artifact="results/x.json", script="tools/x.py",
             metrics={"v": "42"}, caveat="c")
    stub = (tmp_path / "tools" / "x.py").read_text()
    assert "raise NotImplementedError" in stub  # never fabricates a number


def test_end_to_end_scaffold_to_green_gate(tmp_path):
    # init a project
    assert subprocess.run([sys.executable, "-m", "vericlaim", "init",
                           "--root", str(tmp_path)], cwd=ROOT).returncode == 0
    out = scaffold(tmp_path, claim_id="CLAIM-CAP-001",
                   statement="It supports 6 languages.", evidence_level="measured",
                   artifact="results/cap.json", script="tools/cap.py",
                   metrics={"n_languages": "6"}, caveat="Example fixture only.")
    # implement measure() honestly and produce the artifact
    (tmp_path / "results").mkdir()
    (tmp_path / "results" / "cap.json").write_text(
        '{\n  "n_languages": 6\n}\n', encoding="utf-8", newline="\n")
    # paste the register block
    reg = tmp_path / "claims" / "register.yaml"
    reg.write_text(reg.read_text().replace("claims: []", "claims:\n")
                   + out["register_block"], encoding="utf-8", newline="\n")
    # bind the doc
    (tmp_path / "README.md").write_text(
        "# Demo\n\n<!-- claim:CLAIM-CAP-001 n_languages -->\n"
        "It supports 6 languages.\n", encoding="utf-8", newline="\n")
    (tmp_path / "vericlaim.toml").write_text(
        (tmp_path / "vericlaim.toml").read_text().replace(
            'doc_globs       = ["README.md", "docs/*.md"]',
            'doc_globs       = ["README.md"]'), encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-m", "vericlaim", "--root", str(tmp_path),
                        "--quiet"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
