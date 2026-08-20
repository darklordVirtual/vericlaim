# SPDX-License-Identifier: Apache-2.0
"""Claim coverage — how much of the documentation is actually bound.

The gate proves that every number you *bind* agrees with the register. It says
nothing about the numbers you did not bind, and a green gate looks identical
whether a document is fully bound or bound nowhere. For AI-authored prose that
gap is the whole problem: an assistant adds three unsourced figures to the
README and every check stays green, because none of them is anchored.

This module measures the gap instead of assuming it away. It scans the same
``doc_globs`` the gate scans, classifies every numeric literal as **bound** (it
sits in a paragraph an anchor governs, or is pinned by a value token) or
**unbound**, and reports the ratio. Turning a silent hole into a number is what
lets ``[vericlaim.ratchet]`` hold it shut: unbound numbers may fall, never rise.

What it deliberately does NOT do is fail on an unbound number. Most numbers in
a repository are legitimately not claims — version strings, dates, RFC numbers,
list indices, table widths. Coverage is a measured property to hold a line
under, not a rule to obey.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .config import Config
from .evidence import emit

# A numeric literal in prose. Bare integers count: "supports 6 languages" is a
# claim shape, and excluding it would hide the most common unsourced assertion.
# An ISO date matches FIRST and as one token: read left to right it would
# otherwise split into three "numbers" (2026, -07, -14), which both inflates
# the count and puts the pieces beyond the reach of any date allowlist. The
# lookbehind keeps a hyphen from being read as a minus sign inside an
# identifier or a hyphenated word.
NUMBER_RE = re.compile(r"\d{4}-\d{2}-\d{2}|(?<![\w.-])-?\d+(?:[.,]\d+)*")
ANCHOR_RE = re.compile(r"<!--\s*claim:([A-Za-z0-9_.-]+)((?:\s+[A-Za-z0-9_.-]+)+)\s*-->")
VALUE_TOKEN_RE = re.compile(r"<!--\s*v:([A-Za-z0-9_.-]+?)\.([A-Za-z0-9_]+)\s*-->")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_TARGET_RE = re.compile(r"\]\([^)]*\)")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
IMAGE_BADGE_RE = re.compile(r"!\[[^\]]*\]")

# Numbers that are never claims. Each entry is a shape, not a value, so the
# allowlist cannot be used to launder a specific inconvenient figure.
DEFAULT_ALLOW = (
    r"^\d{4}-\d{2}-\d{2}$",           # ISO date
    r"^\d{4}$",                        # year
    r"^\d+\.\d+\.\d+$",               # semver
    r"^[0-9a-f]{7,}$",                # commit / hash fragment
)


def _allow_res(cfg: Config) -> list[re.Pattern]:
    return [re.compile(p) for p in (*DEFAULT_ALLOW, *cfg.coverage_allow)]


def _bound_line_spans(lines: list[str]) -> set[int]:
    """Line indices whose numbers are governed by an anchor or a value token.

    An anchor binds the paragraph that follows it (the gate's own rule), so the
    whole paragraph counts as bound: a figure inside a bound paragraph is under
    the register's authority even when the anchor names a different field.
    """
    bound: set[int] = set()
    in_fence = False
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            bound.add(idx)  # fenced code is not prose; excluded from the ratio
            continue
        if VALUE_TOKEN_RE.search(line):
            bound.add(idx)
            if idx + 1 < len(lines):
                bound.add(idx + 1)  # a token may pin a literal on the next line
        if not ANCHOR_RE.search(line):
            continue
        bound.add(idx)
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        while j < len(lines) and lines[j].strip():
            bound.add(j)
            j += 1
    return bound


ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s")


def _prose(line: str) -> str:
    """The part of a line where an unsourced number would actually mislead."""
    # An ordered-list marker is document structure, not an assertion.
    line = ORDERED_LIST_RE.sub("", line)
    line = HTML_COMMENT_RE.sub("", line)
    line = INLINE_CODE_RE.sub("", line)
    line = LINK_TARGET_RE.sub("]", line)
    line = IMAGE_BADGE_RE.sub("", line)
    return line


def scan_text(text: str, allow: list[re.Pattern]) -> tuple[int, int, list[tuple[int, str]]]:
    """Return ``(bound, unbound, [(lineno, literal), ...])`` for one document."""
    lines = text.splitlines()
    bound_lines = _bound_line_spans(lines)
    bound = unbound = 0
    misses: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        for literal in NUMBER_RE.findall(_prose(line)):
            if any(r.match(literal) for r in allow):
                continue
            if idx in bound_lines:
                bound += 1
            else:
                unbound += 1
                misses.append((idx + 1, literal))
    return bound, unbound, misses


def report(cfg: Config, doc_paths: list[Path]) -> dict:
    """Coverage over every configured doc, as a JSON-serialisable record."""
    allow = _allow_res(cfg)
    per_file: list[dict] = []
    total_bound = total_unbound = 0
    for path in sorted(doc_paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        bound, unbound, misses = scan_text(text, allow)
        if bound == unbound == 0:
            continue
        try:
            rel = path.relative_to(cfg.root).as_posix()
        except ValueError:
            rel = path.name
        total_bound += bound
        total_unbound += unbound
        per_file.append({
            "path": rel,
            "bound": bound,
            "unbound": unbound,
            "unbound_examples": [{"line": n, "literal": lit}
                                 for n, lit in misses[:5]],
        })
    total = total_bound + total_unbound
    pct = round(100.0 * total_bound / total, 2) if total else 100.0
    return {
        "schema": "vericlaim_coverage_v1",
        "numbers_total": total,
        "numbers_bound": total_bound,
        "numbers_unbound": total_unbound,
        "coverage_pct": pct,
        "files": per_file,
    }


def run(cfg: Config, doc_paths: list[Path], *, write: str | None = None,
        quiet: bool = False) -> int:
    """``vericlaim coverage`` — print the report, optionally commit it.

    Always exits 0: coverage is a measurement. The ratchet is what makes it
    binding, and the ratchet runs inside the gate.
    """
    rec = report(cfg, doc_paths)
    if write:
        # An absolute destination is the reproduction case (the runner hands
        # the command an isolated directory); a relative one is the committed
        # artifact, which gets a provenance sidecar like any other evidence.
        target = Path(write)
        if target.is_absolute():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(rec, indent=2) + "\n",
                              encoding="utf-8", newline="\n")
        else:
            emit(json.dumps(rec, indent=2) + "\n", cfg.path(write),
                 script="python3 -m vericlaim coverage --write "
                        f"{write}", output_dir=None)
    if quiet:
        return 0
    print(f"Claim coverage over {len(rec['files'])} document(s): "
          f"{rec['coverage_pct']}% "
          f"({rec['numbers_bound']} bound / {rec['numbers_total']} numbers)")
    for f in sorted(rec["files"], key=lambda x: -x["unbound"])[:10]:
        if not f["unbound"]:
            continue
        examples = ", ".join(f"{e['literal']}@L{e['line']}"
                             for e in f["unbound_examples"])
        print(f"  {f['unbound']:5d} unbound  {f['path']}  ({examples})")
    if write:
        print(f"[OK] wrote {write}")
    print("Unbound is not automatically wrong - most numbers are not claims. "
          "Set a ceiling in [vericlaim.ratchet] to stop it growing.")
    return 0
