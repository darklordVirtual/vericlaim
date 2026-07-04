# SPDX-License-Identifier: Apache-2.0
"""Registrar clients for automated literature curation — arXiv and Crossref.

THE ANTI-FABRICATION RULE: bibliographic metadata in the library comes ONLY
from parsing an authoritative registrar's response (arXiv's Atom API,
Crossref's REST API) at retrieval time — never from a language model's
memory, never hand-typed. Every returned work carries the registrar it came
from and is classified for accreditation:

    source_type: journal-article | proceedings-article | book-chapter | preprint | ...
    accredited:  True only for peer-reviewed venue types (Crossref); arXiv
                 preprints are first-class but honestly labeled preprint.

Relevance is a separate, deterministic, recorded judgment (`rank`) — lexical
term overlap with an accreditation tiebreak. A high score means "worth
attaching, with its score visible"; it NEVER means the work proves a claim.

Stdlib only. Politeness: callers should pause ~3s between arXiv requests
(their API terms); `search_all` does this.
"""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

UA = "vericlaim-litfetch/1 (claim-literature curation; contact: repo issues)"
ATOM = "{http://www.w3.org/2005/Atom}"

# Crossref types that indicate peer-reviewed publication venues.
ACCREDITED_TYPES = {"journal-article", "proceedings-article", "book-chapter",
                    "book", "reference-entry"}

_TAG_RE = re.compile(r"<[^>]+>")
_WORD_RE = re.compile(r"[a-z0-9][a-z0-9-]+")
_STOP = {"the", "a", "an", "and", "or", "of", "on", "in", "for", "with",
         "to", "from", "is", "are", "was", "were", "this", "that", "its",
         "by", "at", "as", "we", "our", "not", "no", "all", "any"}


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", _TAG_RE.sub("", text or "")).strip()


# --------------------------------------------------------------------------- #
# Parsers (pure, offline-testable)
# --------------------------------------------------------------------------- #

def parse_arxiv_atom(data: bytes) -> list[dict]:
    """Parse an arXiv Atom feed into verified work records."""
    root = ET.fromstring(data)
    works: list[dict] = []
    for entry in root.findall(f"{ATOM}entry"):
        raw_id = (entry.findtext(f"{ATOM}id") or "").rsplit("/", 1)[-1]
        arxiv_id = re.sub(r"v\d+$", "", raw_id)  # canonical, versionless
        if not arxiv_id:
            continue
        published = entry.findtext(f"{ATOM}published") or ""
        works.append({
            "work_id": f"arxiv:{arxiv_id}",
            "registrar": "arxiv",
            "title": _clean(entry.findtext(f"{ATOM}title") or ""),
            "abstract": _clean(entry.findtext(f"{ATOM}summary") or ""),
            "authors": [_clean(a.findtext(f"{ATOM}name") or "")
                        for a in entry.findall(f"{ATOM}author")],
            "year": int(published[:4]) if published[:4].isdigit() else None,
            "venue": "arXiv",
            "source_type": "preprint",
            "accredited": False,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
        })
    return works


def parse_crossref(data: bytes) -> list[dict]:
    """Parse a Crossref /works response into verified work records."""
    msg = json.loads(data).get("message", {})
    items = msg.get("items")
    if items is None:  # single-work lookup returns the work directly
        items = [msg]
    works: list[dict] = []
    for it in items:
        doi = (it.get("DOI") or "").lower()
        if not doi:
            continue
        title = _clean((it.get("title") or [""])[0])
        date_parts = (it.get("issued") or {}).get("date-parts") or [[None]]
        year = date_parts[0][0]
        stype = it.get("type") or "unknown"
        works.append({
            "work_id": f"doi:{doi}",
            "registrar": "crossref",
            "title": title,
            "abstract": _clean(it.get("abstract") or ""),
            "authors": [_clean(f"{a.get('given', '')} {a.get('family', '')}")
                        for a in (it.get("author") or [])],
            "year": year if isinstance(year, int) else None,
            "venue": _clean((it.get("container-title") or [""])[0]),
            "source_type": stype,
            "accredited": stype in ACCREDITED_TYPES,
            "url": f"https://doi.org/{doi}",
        })
    return works


# --------------------------------------------------------------------------- #
# Ranking (pure, deterministic, recorded)
# --------------------------------------------------------------------------- #

def _tokens(text: str) -> set[str]:
    return {t for t in _WORD_RE.findall(text.lower()) if t not in _STOP}


def rank(query: str, works: list[dict]) -> list[tuple[dict, float]]:
    """Score works by lexical overlap with the query. Deterministic: same
    inputs, same scores. Title matches weigh double; accredited works win
    ties. The score is curation metadata, not evidence."""
    q = _tokens(query)
    if not q:
        return [(w, 0.0) for w in works]
    scored = []
    for w in works:
        t_hit = len(q & _tokens(w.get("title", "")))
        a_hit = len(q & _tokens(w.get("abstract", "")))
        score = round((2 * t_hit + a_hit) / (2 * len(q)), 4)
        scored.append((w, score))
    return sorted(scored,
                  key=lambda p: (-p[1], not p[0].get("accredited"),
                                 p[0].get("work_id", "")))


# --------------------------------------------------------------------------- #
# Live clients
# --------------------------------------------------------------------------- #

def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"user-agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def arxiv_search(query: str, max_results: int = 5) -> list[dict]:
    url = ("https://export.arxiv.org/api/query?search_query="
           + urllib.parse.quote(f"all:{query}")
           + f"&max_results={max_results}&sortBy=relevance")
    return parse_arxiv_atom(_http_get(url))


def crossref_search(query: str, max_results: int = 5) -> list[dict]:
    url = ("https://api.crossref.org/works?query="
           + urllib.parse.quote(query)
           + f"&rows={max_results}&select=DOI,type,title,author,"
             "container-title,issued,abstract")
    return parse_crossref(_http_get(url))


def search_all(query: str, max_results: int = 5, *,
               pause_s: float = 3.0) -> list[dict]:
    """Query both registrars (arXiv politeness pause included), dedup by id."""
    works = crossref_search(query, max_results)
    time.sleep(pause_s)
    works += arxiv_search(query, max_results)
    seen: set[str] = set()
    out = []
    for w in works:
        if w["work_id"] not in seen:
            seen.add(w["work_id"])
            out.append(w)
    return out
