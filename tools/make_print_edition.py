# SPDX-License-Identifier: Apache-2.0
"""Generate a PRINT edition of the governance handbook.

A physical book has no clickable links and cannot render Mermaid. This script
transforms a handbook edition into print-ready Markdown:

  * `[text](#anchor)` and `[text](url)` -> plain `text` (cross-references become
    "(see Part/section N)" where the anchor encodes a number).
  * the table of contents keeps its numbers but drops the links.
  * every ```mermaid``` block becomes a text "Figure" — node labels and arrows
    rendered as an indented flow, so the information survives in print.
  * HTML comments and screen-only markers are removed.

It then wraps the transformed body with hand-authored front matter (preface,
a one-page primer, a terminology note, and a note on the strength of claims)
and a worked case-studies appendix. The result is a self-contained manuscript,
deterministic from its inputs, committed alongside the digital editions.

Usage: python3 tools/make_print_edition.py <edition.md> <front.md> <cases.md> <out.md>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_FIG = [0]


def _clean_label(text: str) -> str:
    text = re.sub(r"<br\s*/?>", " ", text)
    text = text.strip().strip('([{"\'}])').strip()
    return re.sub(r"\s+", " ", text)


def _mermaid_to_text(block: str) -> str:
    """Render a Mermaid diagram as a print-friendly text figure. Mindmaps become
    an indented outline (their hierarchy IS indentation); flowcharts become an
    edge list 'label -> label (edge text)'."""
    _FIG[0] += 1
    raw = [ln for ln in block.splitlines() if ln.strip()]
    kind = raw[0].strip().split()[0].lower() if raw else ""
    out: list[str] = [f"[Figure {_FIG[0]}]"]

    if kind == "mindmap":
        base = None
        for ln in raw[1:]:
            indent = len(ln) - len(ln.lstrip())
            if base is None:
                base = indent
            depth = max(0, (indent - base) // 2)
            label = _clean_labelmm(ln.strip())
            if label:
                out.append("    " + "  " * depth + "• " + label)
        return "\n".join(out)

    # flowchart / graph: id -> label map, then edges.
    labels: dict[str, str] = {}
    for m in re.finditer(r'(\w+)\s*(?:\[\(|\(\[|\{\{|\[|\()\s*(.*?)\s*(?:\)\]|\]\)|\}\}|\]|\))',
                         block):
        nid, lbl = m.group(1), _clean_label(m.group(2))
        if lbl and nid not in labels:
            labels[nid] = lbl
    # Strip inline node shapes so 'A[label] --> B' becomes 'A --> B' for edge
    # matching (labels were already captured above).
    stripped = re.sub(
        r'(\w+)(?:\[\([^\])]*\)\]|\(\[[^\])]*\]\)|\{\{[^}]*\}\}|\[[^\]]*\]|\([^)]*\))',
        r'\1', block)
    seen = False
    for m in re.finditer(r'(\w+)\s*(?:--?>|---)\s*(?:\|"?(.*?)"?\|\s*)?(\w+)', stripped):
        a, mid, b = m.group(1), m.group(2), m.group(3)
        if a not in labels and b not in labels:
            continue  # skip style/class lines that look edge-ish
        arrow = f" —[{mid.strip()}]→" if mid else " →"
        out.append(f"    {labels.get(a, a)}{arrow} {labels.get(b, b)}")
        seen = True
    if not seen:
        for lbl in labels.values():
            out.append(f"    • {lbl}")
    return "\n".join(out)


def _clean_labelmm(line: str) -> str:
    # a mindmap node: optional id, then text possibly wrapped in shape syntax.
    m = re.match(r"^\w*\s*(?:\(\(|\[|\()\s*(.*?)\s*(?:\)\)|\]|\))\s*$", line)
    if m:
        return _clean_label(m.group(1))
    return _clean_label(line)


def _anchor_ref(anchor: str) -> str:
    """Turn an in-page anchor into a readable cross-reference where possible."""
    m = re.match(r"(\d+)-", anchor)
    if m:
        return f" (see section {m.group(1)})"
    if anchor.startswith("appendix") or anchor.startswith("appendiks"):
        letter = re.search(r"appendi[kx]s?-([a-z])", anchor)
        if letter:
            return f" (see Appendix {letter.group(1).upper()})"
    return ""


def transform(text: str) -> str:
    # strip HTML comments / screen-only markers
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # mermaid blocks -> text figures
    text = re.sub(r"```mermaid\n(.*?)```",
                  lambda m: _mermaid_to_text(m.group(1)), text, flags=re.DOTALL)

    # links: [text](#anchor) -> text (+ cross-ref); [text](url) -> text
    def _link(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if target.startswith("#"):
            return label + _anchor_ref(target[1:])
        return label
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)

    # collapse 3+ blank lines left by removals
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    edition, front, cases, out = (Path(a) for a in sys.argv[1:])
    _FIG[0] = 0
    body = transform(edition.read_text(encoding="utf-8"))
    parts = [front.read_text(encoding="utf-8").rstrip(),
             "\n---\n---\n",
             body.strip(),
             "\n---\n---\n",
             cases.read_text(encoding="utf-8").rstrip(), ""]
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"[OK] print edition -> {out} ({_FIG[0]} figures rendered as text)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
