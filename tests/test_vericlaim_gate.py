# SPDX-License-Identifier: Apache-2.0
"""Tests for the vericlaim gate itself, including drift detection.

The most important test is test_doc_drift_is_caught: it proves the gate does
its one job — a number that drifts from the register fails the build.
"""
from __future__ import annotations

from pathlib import Path


from vericlaim.config import Config, load_config
from vericlaim.gate import (
    check_artifacts,
    check_doc_anchors,
    check_evidence_citations,
    check_manifest,
    check_register,
    check_stale_strings,
    run,
)
from vericlaim.register import load_register

ROOT = Path(__file__).resolve().parents[1]

REG = """\
claims:
  - id: CLAIM-1
    statement: >
      folded
      block.
    evidence_level: measured
    artifact:
      - a.json
    metrics:
      ratio: 2.5
    caveat: "x"
"""


def _cfg(tmp: Path, **over) -> Config:
    return Config(root=tmp, **over)


# ── register parsing ────────────────────────────────────────────────────────

def test_parse_subset():
    claims = load_register(REG)
    assert len(claims) == 1
    c = claims[0]
    assert c["id"] == "CLAIM-1"
    assert c["evidence_level"] == "measured"
    assert c["artifact"] == ["a.json"]
    assert c["metrics"] == {"ratio": 2.5}
    assert "folded block" in c["statement"]


def test_real_register_parses():
    claims = load_register((ROOT / "claims" / "register.yaml").read_text())
    ids = [c["id"] for c in claims]
    assert "CLAIM-EX-001" in ids and "CLAIM-CORE-001" in ids


# ── integrity ───────────────────────────────────────────────────────────────

def test_register_flags_missing_field_and_bad_level(tmp_path):
    cfg = _cfg(tmp_path)
    claims = [{"id": "C-1", "statement": "x", "evidence_level": "vibes",
               "artifact": [], "caveat": "c"}]
    ids = [e for e, _ in check_register(claims, cfg)]
    assert "register-bad-level:C-1" in ids
    assert "register-missing-field:C-1:artifact" in ids


def test_duplicate_id_flagged(tmp_path):
    cfg = _cfg(tmp_path)
    claims = [{"id": "C-1", "statement": "x", "evidence_level": "measured",
               "artifact": ["a"], "caveat": "c"}] * 2
    ids = [e for e, _ in check_register(claims, cfg)]
    assert any(e.startswith("register-duplicate-id") for e in ids)


def test_artifact_existence(tmp_path):
    (tmp_path / "present.json").write_text("{}")
    cfg = _cfg(tmp_path)
    claims = [{"id": "C-1", "artifact": ["present.json", "gone.json"]}]
    ids = [e for e, _ in check_artifacts(claims, cfg)]
    assert ids == ["artifact-missing:C-1:gone.json"]


# ── manifest ────────────────────────────────────────────────────────────────

def test_manifest_hash_match_and_mismatch(tmp_path):
    import hashlib
    (tmp_path / "r.json").write_bytes(b'{"a":1}\n')
    good = hashlib.sha256(b'{"a":1}\n').hexdigest()
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "manifest.md").write_text(
        f"| `r.json` | `{good}` |\n")
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    assert check_manifest(cfg, []) == []
    # tamper
    (tmp_path / "r.json").write_bytes(b'{"a":2}\n')
    ids = [e for e, _ in check_manifest(cfg, [])]
    assert ids == ["manifest-hash-mismatch:r.json"]


def test_manifest_crlf_note(tmp_path):
    import hashlib
    lf = b'{"a":1}\n'
    (tmp_path / "r.json").write_bytes(lf.replace(b"\n", b"\r\n"))
    sha = hashlib.sha256(lf).hexdigest()
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "manifest.md").write_text(f"| `r.json` | `{sha}` |\n")
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    notes: list[str] = []
    assert check_manifest(cfg, notes) == []
    assert notes and "CRLF" in notes[0]


def test_manifest_row_escaping_root_is_flagged(tmp_path):
    # A manifest must not point outside the repo (audit P1: containment).
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "manifest.md").write_text(
        "| `../secret.json` | `" + "0" * 64 + "` |\n")
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    ids = [e for e, _ in check_manifest(cfg, [])]
    assert any(i.startswith("manifest-escapes-root:") for i in ids)


def test_manifest_coverage_flags_unmanifested_reproduce_artifact(tmp_path):
    # A claim with reproduce whose artifact is absent from the manifest fails
    # the side-effect-free gate (audit P1: manifest coverage).
    from vericlaim.gate import check_manifest_coverage
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "claims").mkdir()
    h = "a" * 64
    (tmp_path / "claims" / "manifest.md").write_text(f"| `other.json` | `{h}` |\n")
    cfg = _cfg(tmp_path, manifest="claims/manifest.md")
    claims = [{"id": "C-9", "artifact": ["a.json"], "reproduce": "python x.py"}]
    ids = [e for e, _ in check_manifest_coverage(claims, cfg)]
    assert ids == ["manifest-uncovered:C-9:a.json"]
    # once manifested, it passes
    (tmp_path / "claims" / "manifest.md").write_text(f"| `a.json` | `{h}` |\n")
    assert check_manifest_coverage(claims, cfg) == []


# ── doc anchors (the drift guard) ───────────────────────────────────────────

BY_ID = {"C-1": {"id": "C-1", "n": 4, "metrics": {"ratio": 2.5}}}


def test_anchor_match(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("<!-- claim:C-1 ratio n -->\nThe ratio is 2.5 across 4 files.\n")
    cfg = _cfg(tmp_path)
    assert check_doc_anchors(cfg, doc, doc.read_text(), BY_ID) == []


def test_anchor_value_drift(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("<!-- claim:C-1 ratio -->\nThe ratio is 9.9 now.\n")
    cfg = _cfg(tmp_path)
    ids = [e for e, _ in check_doc_anchors(cfg, doc, doc.read_text(), BY_ID)]
    assert ids == ["anchor-value-drift:d.md:C-1:ratio"]


def test_anchor_unknown_claim_and_metric(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("<!-- claim:C-1 nope -->\ntext 1.0\n"
                   "<!-- claim:C-9 ratio -->\nother.\n")
    cfg = _cfg(tmp_path)
    ids = [e for e, _ in check_doc_anchors(cfg, doc, doc.read_text(), BY_ID)]
    assert "anchor-unknown-metric:d.md:C-1:nope" in ids
    assert "anchor-unknown-claim:d.md:C-9" in ids


# ── evidence citations & stale strings ──────────────────────────────────────

def test_evidence_level_drift(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("CLAIM-1 is externally_validated.\n")
    cfg = _cfg(tmp_path)
    by = {"CLAIM-1": {"id": "CLAIM-1", "evidence_level": "measured"}}
    ids = [e for e, _ in check_evidence_citations(cfg, doc, doc.read_text(), by)]
    assert ids == ["evidence-level-drift:d.md:1:CLAIM-1"]


def test_stale_string(tmp_path):
    doc = tmp_path / "d.md"
    doc.write_text("we still say old-name here\n")
    cfg = _cfg(tmp_path, stale_strings=(("old-name", "use new-name"),))
    ids = [e for e, _ in check_stale_strings(cfg, doc, doc.read_text())]
    assert ids == ["stale-string:d.md:old-name"]


# ── end-to-end on this repo + baseline behavior ─────────────────────────────

def test_gate_passes_on_this_repo():
    cfg = load_config(ROOT)
    assert run(cfg, quiet=True) == 0


def test_doc_drift_is_caught(tmp_path, monkeypatch):
    """The headline guarantee: edit a doc number, the gate fails."""
    # minimal project
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: C-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - r.json\n    metrics:\n      ratio: 2.5\n"
        "    caveat: c\n")
    (tmp_path / "claims" / "baseline.json").write_text(
        '{"known_violations": []}')
    (tmp_path / "r.json").write_text("{}")
    (tmp_path / "README.md").write_text(
        "<!-- claim:C-1 ratio -->\nThe ratio is 2.5.\n")
    cfg = Config(root=tmp_path, manifest=None, doc_globs=("README.md",))
    assert run(cfg, quiet=True) == 0            # in sync -> pass
    (tmp_path / "README.md").write_text(
        "<!-- claim:C-1 ratio -->\nThe ratio is 3.0.\n")
    assert run(cfg, quiet=True) == 1            # drift -> fail


def test_baseline_grandfathers(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: C-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - gone.json\n    caveat: c\n")
    (tmp_path / "claims" / "baseline.json").write_text(
        '{"known_violations": [{"error_id": "artifact-missing:C-1:gone.json",'
        ' "reason": "pending"}]}')
    cfg = Config(root=tmp_path, manifest=None, doc_globs=())
    assert run(cfg, quiet=True) == 0  # baselined -> WARN, not FAIL


def test_illustrative_anchors_in_code_are_ignored(tmp_path):
    """Anchors shown as examples (in fences or inline code) must NOT be treated
    as live anchors — otherwise a project documenting the syntax fails its own
    gate."""
    doc = tmp_path / "d.md"
    doc.write_text(
        "Use `<!-- claim:CLAIM-NOPE ratio -->` inline to bind a number.\n\n"
        "```markdown\n"
        "<!-- claim:CLAIM-ALSO-NOPE ratio -->\n"
        "The ratio is 2.5.\n"
        "```\n\n"
        "<!-- claim:C-1 ratio -->\nThe real one: 2.5.\n"
    )
    cfg = _cfg(tmp_path)
    findings = check_doc_anchors(cfg, doc, doc.read_text(), BY_ID)
    # only the real anchor is evaluated (and it matches) -> no findings
    assert findings == []


def test_init_scaffolds_and_fresh_project_passes(tmp_path):
    """Onboarding: `init` creates a working scaffold and a fresh project (no
    claims) passes the gate — a new user is never greeted by a failure."""
    from vericlaim.scaffold import FILES, init

    assert init(tmp_path) == 0
    for rel in FILES:
        assert (tmp_path / rel).exists()
    (tmp_path / "README.md").write_text("# my project\n")
    cfg = Config(root=tmp_path, manifest=None, doc_globs=("README.md",))
    assert run(cfg, quiet=True) == 0  # empty register is a valid, passing state


def test_init_never_overwrites(tmp_path):
    (tmp_path / "vericlaim.toml").write_text("KEEP ME")
    from vericlaim.scaffold import init

    init(tmp_path)
    assert (tmp_path / "vericlaim.toml").read_text() == "KEEP ME"
