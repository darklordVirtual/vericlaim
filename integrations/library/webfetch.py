# SPDX-License-Identifier: Apache-2.0
"""Tier-3 acquisition — hash-locked snapshots of works no registrar knows.

SLSA, in-toto's spec, W3C PROV-DM, the C4 model, Rules of ML… are real,
load-bearing works with no arXiv/Crossref record. They enter the catalog as
sha256-locked text snapshots of a curator-chosen URL with full retrieval
provenance — and are ALWAYS `accredited=False`, `registrar="web-snapshot"`.
A snapshot proves what a page said when we fetched it, nothing more.

The curator supplies the URL explicitly. This tool never guesses URLs, and
bibliographic fields (title, publisher, year) are the curator's assertion,
recorded as such — never a language model's memory dressed as a registrar.

Stdlib only. `strip_html` is shared with fulltext.py.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

from litindex import add_work

UA = "vericlaim-webfetch/1 (literature snapshots; contact: repo issues)"
_SKIP_TAGS = {"script", "style", "nav", "header", "footer", "math", "svg",
              "aside", "noscript"}
_HEADINGS = {"h1", "h2", "h3"}
_BLOCK_TAGS = {"p", "div", "li", "section", "article", "tr", "br",
               "blockquote", "pre", "td"} | _HEADINGS


class _Stripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._heading: list[str] | None = None
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1
        elif self._skip_depth == 0:
            if tag in _HEADINGS:
                self._heading = []
            elif tag in _BLOCK_TAGS:
                self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif self._skip_depth == 0 and tag in _HEADINGS:
            if self._heading is not None:
                title = re.sub(r"\s+", " ", "".join(self._heading)).strip()
                if title:
                    self._parts.append(f"\n## {title}\n")
                self._heading = None
        elif self._skip_depth == 0 and tag in _BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._heading is not None:
            self._heading.append(data)
        else:
            self._parts.append(data)

    def text(self) -> str:
        raw = "".join(self._parts)
        lines = [re.sub(r"\s+", " ", ln).strip() for ln in raw.splitlines()]
        out: list[str] = []
        for ln in lines:
            if ln:
                out.append(ln)
            elif out and out[-1] != "":
                out.append("")
        return "\n".join(out).strip() + "\n"


def strip_html(html: bytes | str) -> str:
    """HTML → plain text: h1-h3 become `## ` section lines; script/style/
    nav/header/footer/math subtrees are dropped; whitespace collapsed."""
    if isinstance(html, bytes):
        html = html.decode("utf-8", errors="replace")
    s = _Stripper()
    s.feed(html)
    return s.text()


def snapshot_work(root: Path, *, work_id: str, url: str, title: str,
                  publisher: str, year: int | None, html: bytes,
                  fetched_at: str) -> str:
    """Strip, hash-lock and catalog a web snapshot. First snapshot wins
    (litindex.add_work dedupes by work_id)."""
    text = strip_html(html)
    work = {
        "work_id": work_id,
        "registrar": "web-snapshot",
        "title": title,
        "abstract": text,
        "authors": [publisher],
        "year": year,
        "venue": publisher,
        "source_type": "web-snapshot",
        "accredited": False,
        "url": url,
    }
    retrieval = {"method": "web-snapshot", "url": url,
                 "fetched_at": fetched_at}
    return add_work(root, work, retrieval)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def main() -> int:
    ap = argparse.ArgumentParser(description="tier-3 web snapshot into the "
                                             "literature catalog")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent / "literature")
    ap.add_argument("--url", required=True)
    ap.add_argument("--work-id", required=True,
                    help='e.g. "web:slsa.dev/spec/v1.1/levels"')
    ap.add_argument("--title", required=True)
    ap.add_argument("--publisher", required=True)
    ap.add_argument("--year", type=int, default=None)
    args = ap.parse_args()

    html = fetch(args.url)
    fetched_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
    fsid = snapshot_work(args.root, work_id=args.work_id, url=args.url,
                         title=args.title, publisher=args.publisher,
                         year=args.year, html=html, fetched_at=fetched_at)
    print(f"snapshotted {args.work_id} -> {fsid} ({len(html)} bytes html)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
