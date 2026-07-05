# SPDX-License-Identifier: Apache-2.0
"""arXiv full text — the hybrid content policy's open half.

For catalog works with an `arxiv:` id we fetch the paper's HTML rendering
(arxiv.org/html, falling back to ar5iv) and store the stripped plain text
content-addressed via litindex.add_fulltext (first snapshot wins). Works
without a fetchable rendering fall back HONESTLY to abstract+extract — the
outcome is printed and simply leaves `fulltext_sha256` absent; coverage
shows the hole.

Politeness: ≥3 s between fetches; explicit User-Agent.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import time
import urllib.error
import urllib.request
from pathlib import Path

from litindex import _load_works, add_fulltext
from webfetch import strip_html

UA = "vericlaim-fulltext/1 (literature full text; contact: repo issues)"
_MIN_FULLTEXT_CHARS = 2000  # a real paper body, not an error page


def fetch_arxiv_html(arxiv_id: str, opener=urllib.request.urlopen
                     ) -> tuple[str, str]:
    """Return (plain text, source url) for an arXiv paper's HTML rendering.
    Tries arxiv.org/html first, then ar5iv. Raises LookupError when neither
    serves usable HTML."""
    urls = (f"https://arxiv.org/html/{arxiv_id}",
            f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}")
    last = "no attempt"
    for url in urls:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with opener(req, timeout=60) as resp:
                text = strip_html(resp.read())
            if len(text) >= _MIN_FULLTEXT_CHARS or "## " in text:
                return text, url
            last = f"{url}: too short to be a paper body"
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
            last = f"{url}: {e}"
    raise LookupError(f"no HTML rendering for {arxiv_id} ({last})")


def run_all(root: Path, *, pause: float = 3.0,
            opener=urllib.request.urlopen) -> dict[str, str]:
    """Fetch full text for every arXiv work lacking one. Returns
    {work_id: 'fetched'|'fallback-abstract-only'|'already'}."""
    results: dict[str, str] = {}
    works = _load_works(root)
    todo = [(wid, w) for wid, w in sorted(works.items())
            if wid.startswith("arxiv:")]
    for i, (wid, w) in enumerate(todo):
        if w.get("fulltext_sha256"):
            results[wid] = "already"
            continue
        arxiv_id = wid.split(":", 1)[1]
        try:
            text, source = fetch_arxiv_html(arxiv_id, opener=opener)
        except LookupError:
            results[wid] = "fallback-abstract-only"
        else:
            fetched_at = _dt.datetime.now(_dt.timezone.utc).isoformat()
            add_fulltext(root, wid, text,
                         {"method": "arxiv-html", "url": source,
                          "fetched_at": fetched_at})
            results[wid] = "fetched"
        if i + 1 < len(todo):
            time.sleep(pause)
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="fetch arXiv full text for the "
                                             "literature catalog")
    ap.add_argument("--root", type=Path,
                    default=Path(__file__).resolve().parent / "literature")
    ap.add_argument("--all", action="store_true", required=True)
    args = ap.parse_args()

    results = run_all(args.root)
    for wid, status in sorted(results.items()):
        print(f"{status:24s} {wid}")
    n = sum(1 for s in results.values() if s == "fetched")
    print(f"fetched {n}/{len(results)} "
          f"(already: {sum(1 for s in results.values() if s == 'already')}, "
          f"fallback: {sum(1 for s in results.values() if s == 'fallback-abstract-only')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
