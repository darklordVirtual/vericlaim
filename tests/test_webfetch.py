# SPDX-License-Identifier: Apache-2.0
"""Tests for tier-3 web snapshots — hash-locked, honestly non-accredited.

Standards and specs without registrar records (SLSA, PROV-DM, C4, …) enter
the catalog as sha256-locked snapshots of a curated URL, explicitly marked
accredited=False. They are never dressed up as peer-reviewed.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "integrations" / "library"))

import webfetch  # noqa: E402
from litindex import verify  # noqa: E402

FIXTURE_HTML = b"""<!doctype html><html><head><title>SLSA levels</title>
<script>tracking();</script><style>.x{}</style></head><body>
<nav><a href="/">Home</a><a href="/spec">Spec</a></nav>
<header>Site header cruft</header>
<h1>Security levels</h1>
<p>SLSA is organized into a series of levels.</p>
<h2>Build L1</h2>
<p>Provenance exists. It <b>must</b> be generated.</p>
<math><mi>x</mi><mo>+</mo><mn>1</mn></math>
<footer>Copyright</footer>
</body></html>"""


def test_strip_html_keeps_body_drops_noise():
    text = webfetch.strip_html(FIXTURE_HTML)
    assert "## Security levels" in text
    assert "## Build L1" in text
    assert "Provenance exists. It must be generated." in text
    assert "tracking" not in text
    assert "Home" not in text and "Site header cruft" not in text
    assert "Copyright" not in text
    assert "x" != text.strip()[0]  # math subtree dropped


def test_snapshot_work_is_hash_locked_and_honest(tmp_path):
    litroot = tmp_path / "literature"
    fsid = webfetch.snapshot_work(
        litroot, work_id="web:slsa.dev/spec/v1.1/levels",
        url="https://slsa.dev/spec/v1.1/levels", title="SLSA levels",
        publisher="SLSA / OpenSSF", year=None, html=FIXTURE_HTML,
        fetched_at="2026-07-05T00:00:00Z")
    rec = json.loads((litroot / "works" / f"{fsid}.json").read_text())
    assert rec["accredited"] is False
    assert rec["registrar"] == "web-snapshot"
    assert rec["source_type"] == "web-snapshot"
    assert rec["retrieval"]["method"] == "web-snapshot"
    assert rec["retrieval"]["url"] == "https://slsa.dev/spec/v1.1/levels"
    stored = (litroot / "texts" / f"{rec['text_sha256']}.txt").read_text()
    assert "## Security levels" in stored
    assert verify(litroot) == []


def test_first_snapshot_wins(tmp_path):
    litroot = tmp_path / "literature"
    kw = dict(work_id="web:example.org/spec", url="https://example.org/spec",
              title="Spec", publisher="Example", year=None,
              fetched_at="2026-07-05T00:00:00Z")
    fsid = webfetch.snapshot_work(litroot, html=b"<p>version one</p>", **kw)
    rec1 = json.loads((litroot / "works" / f"{fsid}.json").read_text())
    webfetch.snapshot_work(litroot, html=b"<p>version TWO changed</p>", **kw)
    rec2 = json.loads((litroot / "works" / f"{fsid}.json").read_text())
    assert rec1["text_sha256"] == rec2["text_sha256"]
