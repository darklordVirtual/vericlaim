# SPDX-License-Identifier: Apache-2.0
"""Tests for importing a library bundle into a target project.

The acceptance rule from the design: harvest -> import into a FRESH project ->
that project's own vericlaim gate is green, offline, with provenance intact —
and the gate catches any post-import tampering, because the imported material
is hash-locked through the register's literature entries.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from bundlefmt import build_bundle  # noqa: E402
from harvest import harvest_repo  # noqa: E402
from import_bundle import ImportRefused, import_bundle  # noqa: E402

from vericlaim.config import load_config  # noqa: E402
from vericlaim.gate import run  # noqa: E402
from vericlaim.register import load_register  # noqa: E402
from vericlaim.scaffold import init  # noqa: E402


def _harvested_bundle(tmp: Path) -> Path:
    src = tmp / "source"
    (src / "results").mkdir(parents=True)
    (src / "bench").mkdir()
    (src / "results" / "r.json").write_text('{"ratio": 2.5}\n')
    (src / "bench" / "run.py").write_text("print('bench')\n")
    (src / "register.yaml").write_text(
        "claims:\n"
        "  - id: SRC-001\n"
        "    statement: ratio is 2.5 on the source corpus\n"
        "    evidence_level: internal_benchmark\n"
        "    artifact:\n"
        "      - results/r.json\n"
        "    metrics:\n"
        "      ratio: 2.5\n"
        "    caveat: source-scope caveat\n"
        "    reproduce: python3 bench/run.py\n")
    results = harvest_repo(src, tmp / "lib", {
        "repo": "github.com/x/source", "register": "register.yaml",
        "gate_cmd": "", "level_map": {"internal_benchmark": "benchmarked"},
        "caveat_extra": "Harvested from source@{commit}."})
    return tmp / "lib" / results["SRC-001"]


def _fresh_target(tmp: Path) -> Path:
    target = tmp / "target"
    target.mkdir()
    init(target)
    (target / "README.md").write_text("# new project\n")
    return target


def test_roundtrip_import_into_fresh_project_gate_green(tmp_path):
    bdir = _harvested_bundle(tmp_path)
    target = _fresh_target(tmp_path)
    result = import_bundle(bdir, target)
    # vendored content in place
    vend = target / result["vendored_dir"]
    assert (vend / "artifacts" / "results" / "r.json").exists()
    assert (vend / "code" / "bench" / "run.py").exists()
    # register got a parseable entry with provenance-locked literature
    claims = load_register((target / "claims" / "register.yaml").read_text())
    assert len(claims) == 1
    c = claims[0]
    assert c["id"] == "SRC-001"
    assert c["evidence_level"] == "benchmarked"
    assert "source-scope caveat" in c["caveat"]
    lits = c["literature"]
    assert isinstance(lits, list) and len(lits) >= 1
    assert any("provenance.json" in (e.get("file") or "") for e in lits)
    # the target's own gate is green, offline
    assert run(load_config(target), quiet=True) == 0


def test_post_import_tampering_is_caught_by_target_gate(tmp_path):
    bdir = _harvested_bundle(tmp_path)
    target = _fresh_target(tmp_path)
    result = import_bundle(bdir, target)
    prov = target / result["vendored_dir"] / "provenance.json"
    prov.write_text(prov.read_text().replace("github.com/x/source",
                                             "github.com/x/other"))
    assert run(load_config(target), quiet=True) == 1  # literature hash mismatch


def test_candidate_bundle_is_refused(tmp_path):
    lib = tmp_path / "lib"
    _, bdir = build_bundle(
        lib, claim={"id": "CAND-1", "statement": "s",
                    "evidence_level": "theoretical", "artifact": [],
                    "caveat": "c"},
        provenance={"source_repo": "x", "source_gate": "none"},
        files={}, status="candidate")
    target = _fresh_target(tmp_path)
    with pytest.raises(ImportRefused, match="candidate"):
        import_bundle(bdir, target)


def test_tampered_bundle_is_refused_before_vendoring(tmp_path):
    bdir = _harvested_bundle(tmp_path)
    (bdir / "artifacts" / "results" / "r.json").write_text('{"ratio": 9.9}\n')
    target = _fresh_target(tmp_path)
    with pytest.raises(Exception, match="results/r.json"):
        import_bundle(bdir, target)
    assert not (target / "claims" / "imported").exists()


def test_double_import_is_refused(tmp_path):
    bdir = _harvested_bundle(tmp_path)
    target = _fresh_target(tmp_path)
    import_bundle(bdir, target)
    with pytest.raises(ImportRefused, match="already"):
        import_bundle(bdir, target)
