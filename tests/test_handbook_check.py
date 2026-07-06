# SPDX-License-Identifier: Apache-2.0
"""The governance handbook lives outside doc_globs, so this test is what keeps
it from drifting (audit P0): register numbers must agree, collection counts
must sum, and internal links must resolve — for both editions."""
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


def test_slugify_keeps_double_hyphen_for_em_dash():
    # regression: an em dash leaves two spaces -> two hyphens (GitHub anchors).
    assert handbook_check._slugify("Appendix F — Reading paths") \
        == "appendix-f--reading-paths"
