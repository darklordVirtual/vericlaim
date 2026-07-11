# SPDX-License-Identifier: Apache-2.0
"""Tests for the two Meyer/Eiffel-inspired features:

- provenance (attestation): every produced artifact records how it was made;
- reproduce-as-oracle: re-running the evidence must reproduce the artifact
  byte-for-byte (Eiffel's "contract as oracle", run continuously).
"""
from __future__ import annotations

import sys
from pathlib import Path

from vericlaim.config import Config
from vericlaim.gate import check_provenance, run
from vericlaim.provenance import SUFFIX, load, sidecar_path, stamp
from vericlaim.reproduce import reproduce


# ── provenance ──────────────────────────────────────────────────────────────

def test_stamp_and_load_roundtrip(tmp_path):
    art = tmp_path / "r.json"
    art.write_text("{}")
    stamp(art, script="python3 bench.py", produced_by="ci")
    rec = load(art)
    assert rec["script"] == "python3 bench.py"
    assert rec["produced_by"] == "ci"
    assert rec["artifact"] == "r.json"
    assert sidecar_path(art).name == "r.json" + SUFFIX


def test_stamp_is_idempotent_when_artifact_unchanged(tmp_path):
    """Re-stamping an unchanged artifact must not churn the sidecar, so running
    an evidence script (or `vericlaim reproduce`) leaves a clean working tree."""
    art = tmp_path / "r.json"
    art.write_text("{}")
    stamp(art, script="python3 bench.py", produced_by="ci")
    first = sidecar_path(art).read_text()
    stamp(art, script="python3 bench.py", produced_by="ci")
    assert sidecar_path(art).read_text() == first  # byte-identical, no drift
    # A real change to the artifact does move the stamp.
    art.write_text('{"x": 1}')
    stamp(art, script="python3 bench.py", produced_by="ci")
    assert sidecar_path(art).read_text() != first


def test_require_provenance_flags_missing_for_produced_claim(tmp_path):
    art = tmp_path / "r.json"
    art.write_text("{}")
    cfg = Config(root=tmp_path, require_provenance=True)
    claim = {"id": "C-1", "artifact": ["r.json"], "reproduce": "python3 x.py"}
    ids = [e for e, _ in check_provenance([claim], cfg)]
    assert ids == ["provenance-missing:C-1:r.json"]
    # add provenance -> clean
    stamp(art, script="python3 x.py")
    assert check_provenance([claim], cfg) == []


def test_static_source_claim_is_exempt(tmp_path):
    """A claim with no `reproduce` (backed by source files) needs no provenance."""
    (tmp_path / "pyproject.toml").write_text("[project]\n")
    cfg = Config(root=tmp_path, require_provenance=True)
    claim = {"id": "C-1", "artifact": ["pyproject.toml"]}  # no reproduce
    assert check_provenance([claim], cfg) == []


# ── reproduce-as-oracle ─────────────────────────────────────────────────────

def _project(tmp_path: Path, script_body: str) -> Config:
    (tmp_path / "claims").mkdir()
    # Single-quote the command: on Windows sys.executable contains backslashes,
    # which a DOUBLE-quoted YAML scalar would parse as escape sequences (\U, \A…)
    # and reject. Single-quoted YAML scalars take backslashes literally.
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: C-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - out.json\n    caveat: c\n"
        "    reproduce: '" + f"{sys.executable} gen.py" + "'\n")
    (tmp_path / "claims" / "baseline.json").write_text('{"known_violations": []}')
    (tmp_path / "gen.py").write_text(script_body)
    # These fixtures exercise the LEGACY string reproduce path, which is now an
    # explicit opt-in (adopt migration setting). strict would reject it.
    return Config(root=tmp_path, manifest=None, doc_globs=(),
                  baseline="claims/baseline.json", allow_legacy_shell=True)


def test_reproduce_passes_for_deterministic_script(tmp_path):
    cfg = _project(tmp_path, "open('out.json','w').write('{\"v\": 42}\\n')\n")
    (tmp_path / "out.json").write_text('{"v": 42}\n')  # committed artifact
    assert reproduce(cfg, quiet=True) == 0


def test_reproduce_fails_for_stale_artifact(tmp_path):
    # committed artifact says 42, but the script now writes 43 -> stale
    cfg = _project(tmp_path, "open('out.json','w').write('{\"v\": 43}\\n')\n")
    (tmp_path / "out.json").write_text('{"v": 42}\n')
    assert reproduce(cfg, quiet=True) == 1


def test_reproduce_fails_for_nondeterministic_script(tmp_path):
    cfg = _project(
        tmp_path,
        "import random; open('out.json','w').write(str(random.random()))\n")
    (tmp_path / "out.json").write_text("seed")
    assert reproduce(cfg, quiet=True) == 1


def test_gate_still_side_effect_free(tmp_path):
    """The default gate must NOT execute reproduce commands."""
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: C-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - out.json\n    caveat: c\n"
        "    reproduce: \"" + f"{sys.executable} -c \\\"open('SIDE','w').write('x')\\\"" + "\"\n")
    (tmp_path / "claims" / "baseline.json").write_text('{"known_violations": []}')
    (tmp_path / "out.json").write_text("{}")
    cfg = Config(root=tmp_path, manifest=None, doc_globs=())
    run(cfg, quiet=True)
    assert not (tmp_path / "SIDE").exists()  # gate never ran the command
