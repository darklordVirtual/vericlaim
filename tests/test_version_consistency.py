# SPDX-License-Identifier: Apache-2.0
"""vericlaim must not let its OWN version drift — the failure it exists to
prevent. vericlaim/__init__.__version__ is the single source of truth; every
other occurrence must equal it. This test is the enforcement the gate cannot do
for files outside doc_globs (pyproject.toml, CITATION.cff, package metadata)."""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from vericlaim import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_derives_version_dynamically():
    """pyproject must NOT hardcode a version — it derives from __init__."""
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    project = data["project"]
    assert "version" not in project, (
        "pyproject.toml hardcodes a version; it must be dynamic "
        "([tool.hatch.version] path = vericlaim/__init__.py)")
    assert "version" in project.get("dynamic", [])
    assert data["tool"]["hatch"]["version"]["path"] == "vericlaim/__init__.py"


def test_citation_matches_source():
    text = (ROOT / "CITATION.cff").read_text()
    m = re.search(r"^version:\s*(\S+)\s*$", text, re.MULTILINE)
    assert m, "CITATION.cff has no version field"
    assert m.group(1) == __version__, (
        f"CITATION.cff version {m.group(1)} != __version__ {__version__}")


def test_version_artifact_matches_source():
    art = json.loads((ROOT / "claims" / "version.json").read_text())
    assert art["version"] == __version__, (
        "claims/version.json is stale — run tools/version_evidence.py")


def test_readme_version_matches_source():
    text = (ROOT / "README.md").read_text()
    # Strip HTML comments (claim/value anchors) so an anchor between "v" and the
    # number does not hide it, then check every vX.Y.Z token equals the source.
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    cited = set(re.findall(r"v(\d+\.\d+\.\d+)", text))
    assert cited, "README cites no version"
    assert cited == {__version__}, (
        f"README cites {cited}, expected only {{{__version__}}}")
