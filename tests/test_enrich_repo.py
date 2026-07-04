# SPDX-License-Identifier: Apache-2.0
"""Tests for enrich_repo — one command from repo URL to enriched library.

Auto-detection rules under test:
- a repo with vericlaim.toml + register is NATIVE: harvested with its own
  gate, levels pass through;
- a repo matching a mapping config (by repo name) is MAPPED: harvested with
  that curation policy;
- anything else is UNGATED: extracted as quarantined candidates — never
  verified claims, fully automatic but never trust-inflating.
- bibliography auto-discovery picks the markdown file with the most
  parseable reference entries.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

from enrich_repo import detect_source, enrich, find_bibliography  # noqa: E402


def _native_repo(tmp: Path) -> Path:
    src = tmp / "native"
    (src / "claims").mkdir(parents=True)
    (src / "results").mkdir()
    (src / "results" / "r.json").write_text('{"v": 1}\n')
    (src / "vericlaim.toml").write_text(
        '[vericlaim]\nregister = "claims/register.yaml"\n'
        'baseline = "claims/baseline.json"\ndoc_globs = []\n')
    (src / "claims" / "baseline.json").write_text('{"known_violations": []}')
    (src / "claims" / "register.yaml").write_text(
        "claims:\n  - id: NAT-001\n    statement: value is 1\n"
        "    evidence_level: measured\n    artifact:\n      - results/r.json\n"
        "    caveat: c\n")
    return src


def _ungated_repo(tmp: Path) -> Path:
    src = tmp / "wild"
    src.mkdir()
    (src / "README.md").write_text("Handles 12 formats, 3.5x faster.\n")
    return src


def test_detect_native(tmp_path):
    kind, cfg = detect_source(_native_repo(tmp_path), tmp_path / "maps",
                              "https://github.com/x/native")
    assert kind == "native"
    assert cfg["register"] == "claims/register.yaml"


def test_detect_mapped_by_repo_name(tmp_path):
    maps = tmp_path / "maps"
    maps.mkdir()
    (maps / "foo.toml").write_text(
        'repo = "github.com/org/foo-research"\nregister = "reg.yaml"\n')
    src = tmp_path / "clone"
    src.mkdir()
    kind, cfg = detect_source(src, maps, "https://github.com/org/foo-research.git")
    assert kind == "mapped"
    assert cfg["repo"] == "github.com/org/foo-research"


def test_detect_ungated_falls_back(tmp_path):
    kind, _ = detect_source(_ungated_repo(tmp_path), tmp_path / "maps",
                            "https://github.com/x/wild")
    assert kind == "ungated"


def test_find_bibliography_picks_richest_file(tmp_path):
    src = tmp_path / "r"
    (src / "docs").mkdir(parents=True)
    (src / "README.md").write_text("## References\n\n- One, A. (2020). T. *V*.\n")
    (src / "docs" / "paper.md").write_text(
        "## References\n\n- Two, B. (2021). T2. *V*.\n\n"
        "- Three, C. (2022). T3. *V*.\n")
    assert find_bibliography(src).name == "paper.md"
    assert find_bibliography(tmp_path / "nope") is None


def test_enrich_native_builds_verified_and_ungated_builds_candidates(tmp_path):
    out = tmp_path / "lib"
    r1 = enrich(_native_repo(tmp_path), "https://github.com/x/native",
                out, mappings_dir=tmp_path / "maps")
    assert r1["kind"] == "native" and r1["verified"] == 1 and r1["candidates"] == 0
    r2 = enrich(_ungated_repo(tmp_path), "https://github.com/x/wild",
                out, mappings_dir=tmp_path / "maps")
    assert r2["kind"] == "ungated" and r2["verified"] == 0 and r2["candidates"] >= 1
