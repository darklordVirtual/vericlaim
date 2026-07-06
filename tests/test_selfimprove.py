# SPDX-License-Identifier: Apache-2.0
"""Tests for the bounded self-improvement safety envelope (vericlaim.selfimprove).

The load-bearing property: `check_non_weakening` REFUSES every weakening change
and ACCEPTS every non-weakening one. This is the mechanism that keeps a
self-improvement loop from compounding regressions — a change that degrades any
guarantee cannot pass the guard.
"""
from __future__ import annotations

from vericlaim.config import Config
from vericlaim.selfimprove import (
    PROTECTED_CORE,
    STOP_SENTINEL,
    Snapshot,
    check_non_weakening,
    propose,
    stopped,
)

_CORE = {rel: f"hash-{i}" for i, rel in enumerate(PROTECTED_CORE)}


def _snap(levels, tests=100, baseline=0, core=None, gate_ok=True):
    return Snapshot(dict(levels), tests, baseline, dict(core or _CORE), gate_ok)


BASE = _snap({"C-1": 3, "C-2": 1})


# ── the envelope refuses weakenings ─────────────────────────────────────────

def test_identity_is_accepted():
    assert check_non_weakening(BASE, BASE) == []


def test_removing_a_claim_is_refused():
    v = check_non_weakening(BASE, _snap({"C-1": 3}))
    assert any("removed" in m for m in v)


def test_demoting_evidence_is_refused():
    v = check_non_weakening(BASE, _snap({"C-1": 2, "C-2": 1}))
    assert any("demoted" in m for m in v)


def test_reducing_tests_is_refused():
    v = check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1}, tests=99))
    assert any("test count reduced" in m for m in v)


def test_growing_baseline_is_refused():
    v = check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1}, baseline=1))
    assert any("baseline" in m for m in v)


def test_editing_the_verifier_core_is_refused():
    hacked = {**_CORE, "vericlaim/gate.py": "HACKED"}
    v = check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1}, core=hacked))
    assert any("protected verifier core modified" in m for m in v)


def test_red_gate_candidate_is_refused():
    v = check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1}, gate_ok=False))
    assert any("does not pass the gate" in m for m in v)


def test_multiple_weakenings_all_reported():
    bad = _snap({"C-1": 2}, tests=1, baseline=9, gate_ok=False)
    v = check_non_weakening(BASE, bad)
    assert len(v) >= 4  # gate + removal + demotion + tests + baseline


# ── the envelope accepts genuine strengthenings ─────────────────────────────

def test_promotion_is_accepted():
    assert check_non_weakening(BASE, _snap({"C-1": 4, "C-2": 1})) == []


def test_adding_a_claim_is_accepted():
    assert check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1, "C-3": 2})) == []


def test_more_tests_and_less_baseline_accepted():
    assert check_non_weakening(BASE, _snap({"C-1": 3, "C-2": 1}, tests=500, baseline=0)) == []


# ── capture round-trips against a real project ──────────────────────────────

def test_capture_reads_register_and_hashes_core(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: X-1\n    statement: s\n    evidence_level: benchmarked\n"
        "    artifact:\n      - a.json\n    caveat: c\n")
    (tmp_path / "claims" / "baseline.json").write_text('{"known_violations": []}')
    cfg = Config(root=tmp_path)
    snap = Snapshot.capture(cfg, gate_ok=True, test_count=42)
    assert snap.claim_levels.get("X-1") == cfg.evidence_levels.index("benchmarked")
    assert snap.test_count == 42 and snap.baseline_count == 0
    # protected core files don't exist under tmp -> recorded as MISSING, not crash
    assert all(h == "MISSING" for h in snap.core_hashes.values())


def test_unparseable_register_is_not_a_passing_state(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text("claims:\n  - id: [broken\n")
    cfg = Config(root=tmp_path)
    snap = Snapshot.capture(cfg, gate_ok=True, test_count=1)
    assert snap.gate_ok is False  # capture refuses to call a broken register "ok"


# ── proposer is advisory and honest ─────────────────────────────────────────

def test_propose_flags_weak_rung_and_missing_reproduce(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: W-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - a.json\n    caveat: c\n")
    cfg = Config(root=tmp_path)
    kinds = {s.kind for s in propose(cfg)}
    assert "promote-with-evidence" in kinds
    assert "add-reproduce" in kinds


def test_stop_sentinel_disables_self_improvement(tmp_path):
    cfg = Config(root=tmp_path)
    assert stopped(cfg) is False
    (tmp_path / STOP_SENTINEL).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / STOP_SENTINEL).write_text("halt")
    assert stopped(cfg) is True
