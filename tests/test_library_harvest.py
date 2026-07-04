# SPDX-License-Identifier: Apache-2.0
"""Tests for harvesting claims from a gate-verified source repo into bundles.

The harvest honesty rules under test:
- refuse the whole harvest if the source repo's own gate fails
- refuse a claim whose foreign evidence level has no explicit mapping
- never lose the caveat — it is *extended* with harvest provenance
- exclude denylisted (withdrawn) claims
- identify code extracts from the claim's `reproduce` command
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from bundlefmt import load_bundle  # noqa: E402
from harvest import HarvestError, harvest_repo  # noqa: E402

LEVEL_MAP = {"internal_benchmark": "benchmarked",
             "internal_simulation": "measured"}


def _mk_source(tmp: Path, *, level="internal_benchmark", gate_ok=True) -> Path:
    src = tmp / "source"
    (src / "results").mkdir(parents=True)
    (src / "bench").mkdir()
    (src / "results" / "r.json").write_text('{"ratio": 2.5}\n')
    (src / "bench" / "run.py").write_text("print('bench')\n")
    (src / "register.yaml").write_text(
        "claims:\n"
        "  - id: SRC-001\n"
        "    statement: ratio is 2.5\n"
        f"    evidence_level: {level}\n"
        "    artifact:\n"
        "      - results/r.json\n"
        "    metrics:\n"
        "      ratio: 2.5\n"
        "    caveat: original scope caveat\n"
        "    reproduce: python3 bench/run.py\n")
    (src / "gate.py").write_text(
        f"import sys; sys.exit({0 if gate_ok else 1})\n")
    return src


def _cfg(**over) -> dict:
    cfg = {"repo": "github.com/x/source",
           "register": "register.yaml",
           "gate_cmd": "python3 gate.py",
           "level_map": dict(LEVEL_MAP),
           "exclude": [],
           "caveat_extra": "Harvested from source@{commit}; see provenance."}
    cfg.update(over)
    return cfg


def test_harvest_builds_verified_bundle_with_mapping_and_code(tmp_path):
    src = _mk_source(tmp_path)
    out = tmp_path / "lib"
    results = harvest_repo(src, out, _cfg())
    assert list(results) == ["SRC-001"]
    b = load_bundle(out / results["SRC-001"])
    claim, prov = b["claim"], b["provenance"]
    assert b["status"] == "verified"
    assert claim["evidence_level"] == "benchmarked"          # mapped, not copied
    assert claim["caveat"].startswith("original scope caveat")  # never trimmed
    assert "Harvested from source@" in claim["caveat"]          # extended
    assert prov["source_evidence_level"] == "internal_benchmark"
    assert prov["source_claim_id"] == "SRC-001"
    assert prov["source_gate"] == "passed"
    # evidence + the reproduce script are preserved byte-exact
    assert "artifacts/results/r.json" in b["manifest"]["files"]
    assert "code/bench/run.py" in b["manifest"]["files"]


def test_red_source_gate_refuses_whole_harvest(tmp_path):
    src = _mk_source(tmp_path, gate_ok=False)
    with pytest.raises(HarvestError, match="gate"):
        harvest_repo(src, tmp_path / "lib", _cfg())


def test_unmapped_evidence_level_is_refused(tmp_path):
    src = _mk_source(tmp_path, level="vibes_checked")
    with pytest.raises(HarvestError, match="vibes_checked"):
        harvest_repo(src, tmp_path / "lib", _cfg())


def test_native_vericlaim_levels_pass_without_map(tmp_path):
    src = _mk_source(tmp_path, level="benchmarked")
    results = harvest_repo(src, tmp_path / "lib", _cfg(level_map={}))
    b = load_bundle(tmp_path / "lib" / results["SRC-001"])
    assert b["claim"]["evidence_level"] == "benchmarked"


def test_excluded_claim_is_skipped_with_reason(tmp_path):
    src = _mk_source(tmp_path)
    results = harvest_repo(src, tmp_path / "lib",
                           _cfg(exclude=["SRC-001"]))
    assert results == {}


def test_missing_artifact_refuses(tmp_path):
    src = _mk_source(tmp_path)
    (src / "results" / "r.json").unlink()
    with pytest.raises(HarvestError, match="results/r.json"):
        harvest_repo(src, tmp_path / "lib", _cfg())


def test_register_literature_files_are_bundled_automatically(tmp_path):
    # A native vericlaim register can carry hash-verified literature entries;
    # harvest must preserve the committed literature file in the bundle.
    src = _mk_source(tmp_path, level="benchmarked")
    (src / "refs").mkdir()
    (src / "refs" / "note.md").write_text("# source note\n")
    reg = (src / "register.yaml").read_text().rstrip("\n")
    (src / "register.yaml").write_text(reg + (
        "\n    literature:\n"
        "      - source: \"doi:10.1/x\"\n"
        f"        sha256: {'a' * 64}\n"
        "        file: refs/note.md\n"))
    results = harvest_repo(src, tmp_path / "lib", _cfg(level_map={}))
    b = load_bundle(tmp_path / "lib" / results["SRC-001"])
    assert "literature/refs/note.md" in b["manifest"]["files"]
    assert b["claim"]["literature"][0]["source"] == "doi:10.1/x"


def test_curated_literature_is_attached(tmp_path):
    src = _mk_source(tmp_path)
    lit = tmp_path / "curation" / "src-001-sources.md"
    lit.parent.mkdir()
    lit.write_text("# Sources\nDataset X, DOI ...\n")
    results = harvest_repo(src, tmp_path / "lib",
                           _cfg(literature={"SRC-001": [str(lit)]}))
    b = load_bundle(tmp_path / "lib" / results["SRC-001"])
    assert "literature/src-001-sources.md" in b["manifest"]["files"]
