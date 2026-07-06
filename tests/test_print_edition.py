# SPDX-License-Identifier: Apache-2.0
"""The print editions are GENERATED from the handbook by
tools/make_print_edition.py. This test regenerates them and asserts they match
what is committed — so a handbook edit that is not carried into the print
edition fails CI, and the print edition can never silently drift. It also
re-checks the core print invariants: no clickable links, no Mermaid fences."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEN = ROOT / "tools" / "make_print_edition.py"
P = ROOT / "docs" / "governance" / "print"

EDITIONS = [
    ("frontier-ai-governance-master.md", "frontmatter_en.md", "casestudies_en.md",
     "frontier-ai-governance-handbook_PRINT_en.md"),
    ("frontier-ai-governance-master_NO_nb.md", "frontmatter_no.md",
     "casestudies_no.md", "frontier-ai-governance-handbook_PRINT_NO_nb.md"),
]


def _regenerate(edition, front, cases) -> str:
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "out.md"
        subprocess.run(
            [sys.executable, str(GEN),
             str(ROOT / "docs" / "governance" / edition),
             str(P / front), str(P / cases), str(out)],
            check=True, capture_output=True)
        return out.read_text(encoding="utf-8")


def test_print_editions_match_committed():
    for edition, front, cases, printed in EDITIONS:
        regenerated = _regenerate(edition, front, cases)
        committed = (P / printed).read_text(encoding="utf-8")
        assert regenerated == committed, (
            f"{printed} is stale — re-run tools/make_print_edition.py")


def test_print_editions_have_no_links_or_mermaid():
    for *_, printed in EDITIONS:
        text = (P / printed).read_text(encoding="utf-8")
        assert "](#" not in text and "](http" not in text, \
            f"{printed} still has clickable links"
        assert "```mermaid" not in text, f"{printed} still has Mermaid fences"
