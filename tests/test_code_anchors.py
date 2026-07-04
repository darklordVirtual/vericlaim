# SPDX-License-Identifier: Apache-2.0
"""Tests for claim anchors in source-code comments.

Code makes claims too — "supports 6 languages", "O(n) in the doc size" — and
they drift exactly like doc prose. A code anchor is a comment line containing
ONLY the anchor, bound to the contiguous comment block that follows it:

    # claim:CLAIM-X ratio
    # Achieves a 2.5x ratio on the fixed corpus.

The bound "paragraph" is the following comment lines (any recognized leader),
NEVER the code itself — a constant in code that happens to equal the register
value must not satisfy the binding.
"""
from __future__ import annotations

from pathlib import Path

from vericlaim.config import Config, load_config
from vericlaim.gate import check_code_anchors, run

BY_ID = {"C-1": {"id": "C-1", "n": 4, "metrics": {"ratio": 2.5}}}


def _cfg(tmp: Path, **over) -> Config:
    return Config(root=tmp, **over)


def _findings(tmp_path, text: str, by_id=BY_ID) -> list[str]:
    f = tmp_path / "mod.py"
    f.write_text(text)
    cfg = _cfg(tmp_path)
    return [e for e, _ in check_code_anchors(cfg, f, text, by_id)]


# ── binding against the following comment block ─────────────────────────────

def test_hash_anchor_value_in_following_comment_matches(tmp_path):
    assert _findings(
        tmp_path,
        "# claim:C-1 ratio\n"
        "# The encoder achieves a 2.5x ratio on the fixed corpus.\n"
        "X = 1\n",
    ) == []


def test_hash_anchor_value_drift_is_caught(tmp_path):
    assert _findings(
        tmp_path,
        "# claim:C-1 ratio\n"
        "# The encoder achieves a 9.9x ratio now.\n",
    ) == ["anchor-value-drift:mod.py:C-1:ratio"]


def test_slash_anchor_and_multiline_comment_block(tmp_path):
    text = (
        "// claim:C-1 ratio n\n"
        "// A 2.5x ratio was measured\n"
        "// across 4 input files.\n"
        "int x = 0;\n"
    )
    f = tmp_path / "mod.c"
    f.write_text(text)
    cfg = _cfg(tmp_path)
    assert check_code_anchors(cfg, f, text, BY_ID) == []


def test_number_in_code_does_not_satisfy_binding(tmp_path):
    # 2.5 appears in the code line, but the comment block claims nothing —
    # the binding must fail: the claim text itself has to carry the value.
    assert _findings(
        tmp_path,
        "# claim:C-1 ratio\n"
        "RATIO = 2.5\n",
    ) == ["anchor-value-drift:mod.py:C-1:ratio"]


def test_blank_comment_line_ends_the_paragraph(tmp_path):
    # An empty comment acts like a blank line in markdown: paragraph break.
    assert _findings(
        tmp_path,
        "# claim:C-1 ratio\n"
        "#\n"
        "# 2.5 lives in the next paragraph, too far away.\n",
    ) == ["anchor-value-drift:mod.py:C-1:ratio"]


# ── error reporting ──────────────────────────────────────────────────────────

def test_unknown_claim_and_metric(tmp_path):
    ids = _findings(
        tmp_path,
        "# claim:C-9 ratio\n"
        "# whatever\n"
        "# claim:C-1 nope\n"
        "# 1.0\n",
    )
    assert "anchor-unknown-claim:mod.py:C-9" in ids
    assert "anchor-unknown-metric:mod.py:C-1:nope" in ids


def test_prose_after_fields_is_not_a_field(tmp_path):
    # The anchor line must contain only `claim:ID field...` — a comment that
    # merely mentions claim:C-1 mid-sentence is not an anchor.
    assert _findings(
        tmp_path,
        "# see claim:C-1 for the ratio measurement\n"
        "def f(): pass\n",
    ) == []


# ── config + end-to-end wiring ───────────────────────────────────────────────

def test_code_globs_default_empty_and_loads_from_toml(tmp_path):
    assert Config(root=tmp_path).code_globs == ()
    (tmp_path / "vericlaim.toml").write_text(
        '[vericlaim]\ncode_globs = ["src/**/*.py"]\n')
    assert load_config(tmp_path).code_globs == ("src/**/*.py",)


def test_run_catches_code_drift_end_to_end(tmp_path):
    (tmp_path / "claims").mkdir()
    (tmp_path / "claims" / "register.yaml").write_text(
        "claims:\n  - id: C-1\n    statement: s\n    evidence_level: measured\n"
        "    artifact:\n      - r.json\n    metrics:\n      ratio: 2.5\n"
        "    caveat: c\n")
    (tmp_path / "r.json").write_text("{}")
    (tmp_path / "src").mkdir()
    code = tmp_path / "src" / "m.py"
    code.write_text("# claim:C-1 ratio\n# ratio is 2.5 here.\n")
    cfg = Config(root=tmp_path, manifest=None, doc_globs=(),
                 code_globs=("src/**/*.py",))
    assert run(cfg, quiet=True) == 0          # in sync -> pass
    code.write_text("# claim:C-1 ratio\n# ratio is 3.0 here.\n")
    assert run(cfg, quiet=True) == 1          # drift in code -> fail
