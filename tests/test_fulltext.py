# SPDX-License-Identifier: Apache-2.0
"""Tests for arXiv full text — content-addressed, first snapshot wins.

Full text is a second, optional snapshot on a work record: fetched from
arXiv's HTML rendering (ar5iv fallback), stripped to plain text, stored
content-addressed next to abstracts. Failure falls back honestly to
abstract-only — recorded, never hidden.
"""
from __future__ import annotations

import json
import sys
import urllib.error
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import fulltext  # noqa: E402
from litindex import add_fulltext, add_work, verify  # noqa: E402

WORK = {"work_id": "arxiv:1706.04599", "registrar": "arxiv",
        "title": "On calibration of modern neural networks",
        "abstract": "Confidence calibration...", "authors": ["Chuan Guo"],
        "year": 2017, "venue": "arXiv", "source_type": "preprint",
        "accredited": False, "url": "https://arxiv.org/abs/1706.04599"}

# A realistic paper body clears the 2000-char floor; heading presence alone
# must NOT let a short page through (that was a fail-closed hole).
_BODY = "Temperature scaling calibrates the softmax outputs. " * 60
PAPER_HTML = (b"<html><body><h1>On calibration</h1>"
              b"<p>Intro paragraph.</p><h2>2 Methods</h2><p>"
              + _BODY.encode() + b"</p></body></html>")

SHORT_ERROR_HTML = b"""<html><body><h1>HTML is not available</h1>
<p>Conversion failed for this paper.</p></body></html>"""


def test_add_fulltext_first_wins_and_verifies(tmp_path):
    litroot = tmp_path / "literature"
    add_work(litroot, WORK, {"method": "test"})
    sha1 = add_fulltext(litroot, "arxiv:1706.04599", "the full text v1",
                        {"method": "arxiv-html", "url": "u1"})
    sha2 = add_fulltext(litroot, "arxiv:1706.04599", "CHANGED text",
                        {"method": "arxiv-html", "url": "u2"})
    assert sha1 == sha2  # first snapshot wins
    rec = json.loads(
        (litroot / "works" / "arxiv_1706-04599.json").read_text())
    assert rec["fulltext_sha256"] == sha1
    assert rec["fulltext_retrieval"]["url"] == "u1"
    assert verify(litroot) == []


def test_add_fulltext_unknown_work_fails(tmp_path):
    litroot = tmp_path / "literature"
    with pytest.raises(KeyError):
        add_fulltext(litroot, "arxiv:0000.00000", "text", {"method": "t"})


def test_verify_catches_tampered_fulltext(tmp_path):
    litroot = tmp_path / "literature"
    add_work(litroot, WORK, {"method": "test"})
    sha = add_fulltext(litroot, "arxiv:1706.04599", "full text",
                       {"method": "arxiv-html", "url": "u"})
    (litroot / "texts" / f"{sha}.txt").write_text("tampered")
    problems = verify(litroot)
    assert problems and "1706.04599" in " ".join(problems)


def test_fetch_arxiv_html_falls_back_to_ar5iv():
    calls = []

    def opener(req, timeout=60):
        url = req.get_full_url()
        calls.append(url)
        if url.startswith("https://arxiv.org/html"):
            raise urllib.error.HTTPError(url, 404, "nf", {}, None)

        class R:
            def read(self):
                return PAPER_HTML
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        return R()

    text, source = fulltext.fetch_arxiv_html("1706.04599", opener=opener)
    assert "## 2 Methods" in text
    assert "ar5iv" in source and len(calls) == 2


def test_fetch_arxiv_html_both_fail_raises():
    def opener(req, timeout=60):
        raise urllib.error.HTTPError(req.get_full_url(), 404, "nf", {}, None)

    with pytest.raises(LookupError):
        fulltext.fetch_arxiv_html("1706.04599", opener=opener)


def test_short_error_page_with_heading_is_rejected():
    """A conversion-failure page carrying a single h1 must NOT pass the floor
    just because it has a '## ' line — heading presence is not an escape
    hatch, else junk would become the work's permanent hash-locked text."""
    def opener(req, timeout=60):
        class R:
            def read(self):
                return SHORT_ERROR_HTML
            def __enter__(self):
                return self
            def __exit__(self, *a):
                return False
        return R()

    with pytest.raises(LookupError):
        fulltext.fetch_arxiv_html("1706.04599", opener=opener)
