# SPDX-License-Identifier: Apache-2.0
"""Tests for value tokens — semantic binding of ONE specific number.

Paragraph anchors prove a value is *present somewhere* in the paragraph;
"target is 180 ms; actual is 900 ms" contains 180 and passes. A value token
pins the NEXT number literal to a register field, closing exactly that gap:

    <!-- v:CLAIM-PERF-001.p95_ms -->**180 ms**

The first number after the token must equal the register value — other
numbers in the paragraph are irrelevant, and a drifted pinned number fails
even if the correct value appears nearby.
"""
from __future__ import annotations


from vericlaim.config import Config
from vericlaim.gate import check_value_tokens

BY_ID = {"C-1": {"id": "C-1", "n": 4, "metrics": {"ratio": 2.5, "p95_ms": 180}}}


def _findings(tmp_path, text: str) -> list[str]:
    doc = tmp_path / "d.md"
    doc.write_text(text)
    return [e for e, _ in check_value_tokens(Config(root=tmp_path), doc,
                                             text, BY_ID)]


def test_pinned_value_matches(tmp_path):
    assert _findings(tmp_path,
                     "The p95 is <!-- v:C-1.p95_ms -->**180 ms** today.\n") == []


def test_markdown_and_unit_wrapping_is_tolerated(tmp_path):
    assert _findings(tmp_path,
                     "Ratio: <!-- v:C-1.ratio -->2.5x overall.\n") == []


def test_semantic_gap_is_closed(tmp_path):
    # The classic failure of paragraph anchors: the right number is present,
    # but the PINNED number drifted. Value tokens must catch it.
    ids = _findings(tmp_path,
                    "Target is 180 ms; actual is <!-- v:C-1.p95_ms -->900 ms.\n")
    assert ids == ["value-token-drift:d.md:C-1:p95_ms"]


def test_number_may_wrap_to_next_line(tmp_path):
    assert _findings(tmp_path,
                     "The measured ratio is <!-- v:C-1.ratio -->\n2.5 overall.\n") == []


def test_missing_number_after_token(tmp_path):
    ids = _findings(tmp_path,
                    "Ratio: <!-- v:C-1.ratio -->is great.\nAnd no digits here.\n")
    assert ids == ["value-token-no-number:d.md:C-1:ratio"]


def test_n_binding_and_unknowns(tmp_path):
    assert _findings(tmp_path, "All <!-- v:C-1.n -->4 files pass.\n") == []
    ids = _findings(tmp_path,
                    "<!-- v:C-9.ratio -->1.0 and <!-- v:C-1.nope -->1.0\n")
    assert "value-token-unknown-claim:d.md:C-9" in ids
    assert "value-token-unknown-metric:d.md:C-1:nope" in ids


def test_fenced_and_inline_code_tokens_are_illustrative(tmp_path):
    assert _findings(
        tmp_path,
        "Use `<!-- v:C-1.ratio -->9.9` to pin a value.\n\n"
        "```markdown\n<!-- v:C-1.ratio -->9.9\n```\n\n"
        "Real one: <!-- v:C-1.ratio -->2.5 here.\n") == []
