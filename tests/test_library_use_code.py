# SPDX-License-Identifier: Apache-2.0
"""Tests for use_code — programming WITH a bundle's code behind you.

The story under test: vendor a bundle's code byte-exact (the code you run IS
the code that produced the evidence), record the binding in BINDING.json, and
generate a test that fails the target's OWN test suite if the vendored code
is ever edited — fork-and-own becomes an explicit, visible decision.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from bundlefmt import build_bundle  # noqa: E402
from use_code import UseRefused, use_code  # noqa: E402

CODE = b"def double(x):\n    return 2 * x\n"


def _bundle(tmp: Path, status="verified", with_code=True):
    files = {"artifacts/r.json": b"{}"}
    if with_code:
        files["code/pkg/mod.py"] = CODE
    _, bdir = build_bundle(
        tmp / "lib", claim={"id": "SRC-001", "statement": "s",
                            "evidence_level": "benchmarked",
                            "artifact": ["artifacts/r.json"], "caveat": "c"},
        provenance={"source_repo": "github.com/x/y", "source_commit": "abc",
                    "source_claim_id": "SRC-001"},
        files=files, status=status)
    return bdir


def test_use_code_vendors_byte_exact_with_binding_and_test(tmp_path):
    bdir = _bundle(tmp_path)
    target = tmp_path / "proj"
    target.mkdir()
    result = use_code(bdir, target)
    mod = target / result["dest"] / "pkg" / "mod.py"
    assert mod.read_bytes() == CODE                       # byte-exact
    binding = json.loads((target / result["dest"] / "BINDING.json").read_text())
    assert binding["claim_id"] == "SRC-001"
    assert binding["source_repo"] == "github.com/x/y"
    test_file = target / result["binding_test"]
    assert test_file.exists()
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q",
                           str(test_file)], cwd=target, capture_output=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_edited_vendored_code_fails_the_generated_test(tmp_path):
    bdir = _bundle(tmp_path)
    target = tmp_path / "proj"
    target.mkdir()
    result = use_code(bdir, target)
    mod = target / result["dest"] / "pkg" / "mod.py"
    mod.write_bytes(CODE + b"# sneaky edit\n")
    proc = subprocess.run([sys.executable, "-m", "pytest", "-q",
                           str(target / result["binding_test"])],
                          cwd=target, capture_output=True)
    assert proc.returncode != 0                           # fork made visible


def test_candidate_and_codeless_bundles_are_refused(tmp_path):
    target = tmp_path / "proj"
    target.mkdir()
    with pytest.raises(UseRefused, match="candidate"):
        use_code(_bundle(tmp_path / "a", status="candidate"), target)
    with pytest.raises(UseRefused, match="no code"):
        use_code(_bundle(tmp_path / "b", with_code=False), target)
