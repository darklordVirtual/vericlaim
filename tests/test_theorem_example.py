# SPDX-License-Identifier: Apache-2.0
"""Tests for the theorem example: a machine-checked proof as evidence.

The point of the example: a *proof object* is the strongest kind of committed
artifact — `vericlaim reproduce` re-runs the checker, so the claim "this
theorem is proved" is regenerated from the committed derivation every time,
never taken on faith. The checker must therefore be fail-closed: any step that
is not a genuine axiom instance or modus-ponens application raises.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / "examples" / "theorem"
sys.path.insert(0, str(EX / "src"))

from proofcheck import ProofError, check_file, verify_proof  # noqa: E402

IMP = lambda a, b: ["->", a, b]  # noqa: E731


def _committed_proof() -> dict:
    return json.loads((EX / "proofs" / "p_implies_p.json").read_text())


# ── the committed derivation verifies ────────────────────────────────────────

def test_committed_proof_of_p_implies_p_verifies():
    report = check_file(EX / "proofs" / "p_implies_p.json")
    assert report["qed"] is True
    assert report["steps_verified"] == 5
    assert report["theorem"] == IMP("p", "p")


# ── fail-closed: every way a "proof" can lie must raise ──────────────────────

def test_tampered_step_formula_is_rejected():
    proof = _committed_proof()
    proof["steps"][-1]["formula"] = IMP("p", "q")  # claim more than was derived
    with pytest.raises(ProofError):
        verify_proof(proof)


def test_non_axiom_claimed_as_axiom_is_rejected():
    proof = {"theorem": IMP("p", "q"),
             "steps": [{"formula": IMP("p", "q"), "rule": "A1"}]}
    with pytest.raises(ProofError):
        verify_proof(proof)


def test_mp_must_reference_earlier_steps_only():
    # Self/forward reference would allow circular justification.
    proof = _committed_proof()
    proof["steps"][2]["from"] = [2, 3]  # step 3 citing itself (1-indexed)
    with pytest.raises(ProofError):
        verify_proof(proof)


def test_mp_with_mismatched_premises_is_rejected():
    proof = {"theorem": "q", "steps": [
        {"formula": IMP("p", IMP("q", "p")), "rule": "A1"},
        {"formula": "q", "rule": "MP", "from": [1, 1]},
    ]}
    with pytest.raises(ProofError):
        verify_proof(proof)


def test_last_step_must_equal_declared_theorem():
    proof = _committed_proof()
    proof["theorem"] = IMP("q", "q")
    with pytest.raises(ProofError):
        verify_proof(proof)


# ── the committed artifact matches a fresh verification ─────────────────────

def test_artifact_matches_fresh_verification():
    artifact = json.loads(
        (EX / "artifacts" / "theorem.json").read_text())
    fresh = check_file(EX / "proofs" / "p_implies_p.json")
    assert artifact["steps_verified"] == fresh["steps_verified"]
    assert artifact["qed"] is fresh["qed"] is True
    assert artifact["theorem"] == fresh["theorem"]
