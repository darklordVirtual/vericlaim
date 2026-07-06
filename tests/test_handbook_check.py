# SPDX-License-Identifier: Apache-2.0
"""The governance handbook lives outside doc_globs, so this test is what keeps
it from drifting (audit P0): register numbers must agree, collection counts must
sum, and internal links must resolve — across ALL editions, recursively."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "handbook_check", ROOT / "docs" / "governance" / "handbook_check.py")
handbook_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(handbook_check)


def test_handbook_editions_consistent_with_register():
    assert handbook_check.main() == 0


def test_validator_covers_every_governance_markdown_recursively():
    # Guard against silently narrowing back to only the two masters: the walk
    # must reach the print + executive editions too, incl. nested folders.
    covered = {p.relative_to(handbook_check.HERE).as_posix()
               for p in handbook_check._editions()}
    on_disk = {p.relative_to(handbook_check.HERE).as_posix()
               for p in handbook_check.HERE.rglob("*.md")}
    assert covered == on_disk, "some governance .md is not validated"
    assert any(p.startswith("print/") for p in covered), "print editions uncovered"
    assert sum(1 for p in handbook_check.HERE.rglob("*.md")
               if handbook_check._is_full_handbook(p.read_text(encoding="utf-8"))) >= 4


def test_the_recursive_check_actually_bites():
    # A full handbook (has the Appendix A collection row) that fails to restate a
    # register metric is flagged; a broken internal link in ANY edition is flagged.
    import tempfile
    from pathlib import Path as _P
    metrics = handbook_check._register_metrics()
    with tempfile.TemporaryDirectory() as d:
        drifted = _P(d) / "handbook.md"  # full handbook, but quotes no metrics
        drifted.write_text("# H\n\n| 01 | c | 5 |\n\nno register numbers here\n",
                           encoding="utf-8")
        assert handbook_check._is_full_handbook(drifted.read_text())
        assert handbook_check.check_edition(drifted, metrics), "metric drift not caught"

        broken = _P(d) / "short.md"  # short edition, bad internal link
        broken.write_text("# Title\n\nSee [x](#no-such-heading).\n", encoding="utf-8")
        assert not handbook_check._is_full_handbook(broken.read_text())
        assert handbook_check.check_edition(broken, metrics), "bad link not caught"


def test_slugify_keeps_double_hyphen_for_em_dash():
    # regression: an em dash leaves two spaces -> two hyphens (GitHub anchors).
    assert handbook_check._slugify("Appendix F — Reading paths") \
        == "appendix-f--reading-paths"
