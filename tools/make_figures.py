# SPDX-License-Identifier: Apache-2.0
"""Generate the print-edition figures as deterministic, hand-authored SVG.

A governance handbook earns its illustrations by drawing its own ideas, not
decoration: the claim seal (front cover), a quiet companion mark and blurb (back
cover), and three interior figures, the evidence ladder, the gate pipeline, and
the provenance chain. Everything is vector and text, so it commits, diffs, prints
crisp at any size, and regenerates byte-identically (see tests/test_figures.py).

Style: geometric / bold, full colour. Output: docs/governance/print/figures/{en,no}/*.svg

Usage: python3 tools/make_figures.py            # writes all figures
       python3 tools/make_figures.py --check    # print output paths only
"""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "governance" / "print" / "figures"

# --- palette (full colour, bold) --------------------------------------------
PAPER = "#F5F0E6"
CARD = "#FBF8F1"
INK = "#0C1E33"
SLATE = "#4A5A6A"
TEAL = "#12B3A6"
BLUE = "#2F6BE0"
GREEN = "#2F9E44"
VIOLET = "#6C4AE0"
AMBER = "#F5A623"
CORAL = "#E4572E"

# rising confidence -> warmer / stronger colour
LEVEL_COLOURS = [SLATE, BLUE, TEAL, GREEN, VIOLET, AMBER]
LEVELS = ["theoretical", "measured", "benchmarked",
          "reproduced", "machine_checked", "externally_validated"]

STR = {
    "en": {
        "title": ["THE FRONTIER", "AI GOVERNANCE", "HANDBOOK"],
        "subtitle": "Evidence-bound governance for frontier AI systems",
        "author": "STIAN SKOGBROTT",
        "imprint": "Claim-Oriented Programming · VeriClaim",
        "seal": "VERIFIED CLAIM",
        "back_head": "Governance you can attack,\nand still stand behind.",
        "back_body": [
            "AI governance built as a system of checkable claims,",
            "not a stack of reassuring documents. Every strong",
            "statement is a registered claim at a stated evidence",
            "level, bound to committed evidence, checked on every",
            "commit. The book applies its own discipline to itself.",
        ],
        "back_foot": "The method is the point, not the numbers.",
        "fig_ladder": "The evidence ladder",
        "fig_ladder_cap": ("Describe a claim only at the level it has earned. "
                           "Demotion is always allowed; promotion needs new evidence."),
        "promote": "promotion needs new evidence",
        "demote": "demotion always allowed",
        "fig_gate": "The gate, on every commit",
        "gate_steps": ["Register\nintegrity", "Artifact\nexistence", "Path\ncontainment",
                       "Provenance", "Manifest\nhashes", "Doc\nbinding"],
        "gate_claim": "a claim",
        "gate_ok": "[OK]",
        "gate_fail": "drift\nfails the\nbuild",
        "fig_gate_cap": ("A claim runs every check on each commit. Any drift, a "
                         "changed number, a broken hash, a doc above its evidence, fails the build."),
        "fig_prov": "The provenance chain",
        "prov_nodes": ["Artifact", "SHA-256", "Sidecar", "Register", "Manifest"],
        "prov_sub": ["the number", "of its bytes", "how it was made",
                     "the claim", "the sealed set"],
        "fig_prov_cap": ("Every produced number records how it was made and is "
                         "checked to still hold: reproduce it, and the bytes must match."),
    },
    "no": {
        "title": ["HÅNDBOK I", "FRONTIER-AI-", "GOVERNANCE"],
        "subtitle": "Evidensbundet governance for frontier-AI-systemer",
        "author": "STIAN SKOGBROTT",
        "imprint": "Claim-Oriented Programming · VeriClaim",
        "seal": "VERIFISERT CLAIM",
        "back_head": "Governance som tåler angrep,\nog likevel står.",
        "back_body": [
            "AI-governance bygget som et system av sjekkbare",
            "claims, ikke en bunke betryggende dokumenter. Hver",
            "sterk påstand er en registrert claim på et oppgitt",
            "evidensnivå, bundet til committet evidens, sjekket ved",
            "hver commit. Boken bruker sin egen disiplin på seg selv.",
        ],
        "back_foot": "Metoden er poenget, ikke tallene.",
        "fig_ladder": "Evidensstigen",
        "fig_ladder_cap": ("Beskriv en claim bare på nivået den har fortjent. "
                           "Nedgradering er alltid tillatt; oppgradering krever ny evidens."),
        "promote": "oppgradering krever ny evidens",
        "demote": "nedgradering alltid tillatt",
        "fig_gate": "Gaten, ved hver commit",
        "gate_steps": ["Register-\nintegritet", "Artefakt-\neksistens", "Sti-\ninneslutning",
                       "Provenance", "Manifest-\nhasher", "Dok-\nbinding"],
        "gate_claim": "en claim",
        "gate_ok": "[OK]",
        "gate_fail": "drift\nfeiler\nbygget",
        "fig_gate_cap": ("En claim kjører hver sjekk ved hver commit. Enhver drift, et "
                         "endret tall, en brutt hash, en doc over sin evidens, feiler bygget."),
        "fig_prov": "Provenance-kjeden",
        "prov_nodes": ["Artefakt", "SHA-256", "Sidecar", "Register", "Manifest"],
        "prov_sub": ["tallet", "av bytene", "hvordan det ble laget",
                     "claimen", "det forseglede settet"],
        "fig_prov_cap": ("Hvert produsert tall registrerer hvordan det ble laget og "
                         "sjekkes at det fortsatt holder: kjør det på nytt, og bytene må stemme."),
    },
}


# --- svg helpers ------------------------------------------------------------
def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _svg(w: int, h: int, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" font-family="Helvetica, Arial, sans-serif">\n'
            f'{body}\n</svg>\n')


def rect(x, y, w, h, fill, rx=0, stroke="none", sw=0, opacity=1):
    s = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
         f'rx="{rx}" fill="{fill}"')
    if stroke != "none":
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    if opacity != 1:
        s += f' opacity="{opacity}"'
    return s + "/>"


def circle(cx, cy, r, fill, stroke="none", sw=0):
    s = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"'
    if stroke != "none":
        s += f' stroke="{stroke}" stroke-width="{sw}"'
    return s + "/>"


def line(x1, y1, x2, y2, stroke, sw, cap="butt"):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"/>')


def poly(pts, fill, stroke="none", sw=0):
    p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    s = f'<polygon points="{p}" fill="{fill}"'
    if stroke != "none":
        s += f' stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"'
    return s + "/>"


def text(x, y, s, size, fill, weight="normal", anchor="start", spacing=0, italic=False):
    extra = f' letter-spacing="{spacing}"' if spacing else ""
    it = ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}{it}>{esc(s)}</text>')


def multitext(x, y, lines, size, fill, weight="normal", anchor="middle", lh=1.25):
    out = []
    for i, ln in enumerate(lines):
        out.append(text(x, y + i * size * lh, ln, size, fill, weight, anchor))
    return "\n".join(out)


def hexagon(cx, cy, r, rot=math.pi / 2):
    return [(cx + r * math.cos(rot + k * math.pi / 3),
             cy + r * math.sin(rot + k * math.pi / 3)) for k in range(6)]


def check(cx, cy, s, colour, sw):
    p = (f'M {cx - s:.1f} {cy:.1f} L {cx - s*0.25:.1f} {cy + s*0.7:.1f} '
         f'L {cx + s:.1f} {cy - s*0.8:.1f}')
    return (f'<path d="{p}" fill="none" stroke="{colour}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


# --- the claim seal (shared by both covers) ---------------------------------
def seal(cx, cy, r, *, quiet=False):
    b = []
    face = "none" if quiet else INK
    # scalloped wax-seal edge: bumps around the rim
    if not quiet:
        bumps = 40
        for i in range(bumps):
            a = 2 * math.pi * i / bumps
            b.append(circle(cx + r * math.cos(a), cy + r * math.sin(a), r * 0.075, AMBER))
        b.append(circle(cx, cy, r, AMBER))
    # milled tick ring (hash motif)
    ticks = 60
    for i in range(ticks):
        a = 2 * math.pi * i / ticks
        r0, r1 = r * 0.80, r * 0.90
        col = INK if not quiet else SLATE
        b.append(line(cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                      cx + r1 * math.cos(a), cy + r1 * math.sin(a), col, r * 0.018))
    # inner disc
    b.append(circle(cx, cy, r * 0.78, face if not quiet else "none",
                    stroke=INK if quiet else "none", sw=r * 0.03))
    b.append(circle(cx, cy, r * 0.70, "none", stroke=(SLATE if quiet else TEAL), sw=r * 0.02))
    # inner hexagon + rising rungs + check
    hx = hexagon(cx, cy, r * 0.60)
    b.append(poly(hx, "none", stroke=(INK if quiet else AMBER), sw=r * 0.02))
    # three rising rungs under the check
    base = cy + r * 0.30
    for i, col in enumerate([TEAL, GREEN, AMBER]):
        bw = r * 0.16
        bx = cx - r * 0.26 + i * r * 0.20
        bh = r * 0.10 + i * r * 0.10
        b.append(rect(bx, base - bh, bw * 0.8, bh, (SLATE if quiet else col), rx=r * 0.015))
    # bold check above the rungs
    b.append(check(cx, cy - r * 0.10, r * 0.30, (INK if quiet else PAPER), r * 0.09))
    return "\n".join(b)


# --- figures ----------------------------------------------------------------
def cover_front(s: dict) -> str:
    W, H = 1200, 1800
    b = [rect(0, 0, W, H, PAPER)]
    # top ink band with title
    b.append(rect(0, 0, W, 620, INK))
    # geometric accent squares
    for i, c in enumerate([TEAL, AMBER, CORAL]):
        b.append(rect(90 + i * 70, 90, 52, 52, c, rx=6))
    for i, ln in enumerate(s["title"]):
        b.append(text(90, 300 + i * 104, ln, 92, PAPER, "800"))
    b.append(text(92, 560, s["subtitle"], 33, TEAL, "600"))
    # seal
    b.append(seal(600, 1075, 330))
    b.append(text(600, 1500, s["seal"], 40, INK, "800", "middle", spacing=8))
    # foot
    b.append(rect(90, 1600, 380, 8, TEAL))
    b.append(text(90, 1680, s["author"], 46, INK, "800", spacing=2))
    b.append(text(90, 1730, s["imprint"], 30, SLATE, "600"))
    return _svg(W, H, "\n".join(b))


def cover_back(s: dict) -> str:
    W, H = 1200, 1800
    b = [rect(0, 0, W, H, PAPER)]
    b.append(rect(0, 0, W, 60, INK))
    b.append(rect(0, H - 60, W, 60, INK))
    # quiet companion mark, top
    b.append(seal(600, 360, 210, quiet=True))
    # heading
    for i, ln in enumerate(s["back_head"].split("\n")):
        b.append(text(600, 700 + i * 66, ln, 54, INK, "800", "middle"))
    # body
    for i, ln in enumerate(s["back_body"]):
        b.append(text(600, 860 + i * 52, ln, 32, SLATE, "500", "middle"))
    b.append(text(600, 1200, s["back_foot"], 34, TEAL, "700", "middle", italic=True))
    # mini evidence-ladder motif
    for i, c in enumerate(LEVEL_COLOURS):
        bw, bh = 120, 26 + i * 22
        bx = 600 - (3 * 130) + i * 130 + 65
        b.append(rect(bx, 1480 - bh, bw, bh, c, rx=5))
    # ISBN placeholder barcode
    b.append(rect(430, 1560, 340, 150, CARD, rx=8, stroke=INK, sw=2))
    bx = 470
    widths = [4, 2, 6, 2, 4, 8, 2, 4, 2, 6, 4, 2, 8, 2, 4, 2, 6, 2, 4, 6, 2, 4, 2, 8]
    for w in widths:
        b.append(rect(bx, 1585, w, 90, INK))
        bx += w + 6
    b.append(text(600, 1695, "ISBN 000-0-000000-0-0", 22, SLATE, "600", "middle"))
    b.append(text(600, H - 22, s["imprint"], 24, PAPER, "600", "middle"))
    return _svg(W, H, "\n".join(b))


def _fig_frame(W, H, s, title):
    b = [rect(0, 0, W, H, CARD, rx=24, stroke="#E4DCC9", sw=3)]
    b.append(rect(56, 54, 14, 46, TEAL, rx=3))
    b.append(text(88, 92, title, 44, INK, "800"))
    return b


def fig_ladder(s: dict) -> str:
    W, H = 1400, 900
    b = _fig_frame(W, H, s, s["fig_ladder"])
    x0, base = 140, 690
    step_w, step_dx = 168, 175
    for i, (lv, col) in enumerate(zip(LEVELS, LEVEL_COLOURS)):
        h = 90 + i * 78
        x = x0 + i * step_dx
        y = base - h
        b.append(rect(x, y, step_w, h, col, rx=10))
        b.append(rect(x, y, step_w, 12, "#FFFFFF", rx=6, opacity=0.35))
        # number chip
        b.append(circle(x + 30, y + 34, 22, "#FFFFFF"))
        b.append(text(x + 30, y + 42, str(i + 1), 26, col, "800", "middle"))
        # level name, rotated up the step
        b.append(f'<text x="{x + step_w/2:.0f}" y="{base - 18:.0f}" font-size="23" '
                 f'fill="#FFFFFF" font-weight="700" text-anchor="start" '
                 f'transform="rotate(-90 {x + step_w/2:.0f} {base - 18:.0f})">{esc(lv)}</text>')
    # rising arrow
    ax0, ay0 = x0 - 30, base + 6
    ax1, ay1 = x0 + 5 * step_dx + step_w + 30, base - (90 + 5 * 78) + 6
    b.append(line(ax0, ay0, ax1, ay1, INK, 6, "round"))
    ang = math.atan2(ay1 - ay0, ax1 - ax0)
    for da in (math.radians(150), math.radians(-150)):
        b.append(line(ax1, ay1, ax1 + 26 * math.cos(ang + da),
                      ay1 + 26 * math.sin(ang + da), INK, 6, "round"))
    b.append(text(x0 - 20, base + 54, s["demote"] + "  ↓", 24, CORAL, "700"))
    b.append(text(W - 60, 150, "↑  " + s["promote"], 24, GREEN, "700", "end"))
    b.append(text(88, H - 44, s["fig_ladder_cap"], 25, SLATE, "500"))
    return _svg(W, H, "\n".join(b))


def fig_gate(s: dict) -> str:
    W, H = 1600, 720
    b = _fig_frame(W, H, s, s["fig_gate"])
    cy = 340
    # claim token
    b.append(circle(120, cy, 66, TEAL))
    b.append(multitext(120, cy - 4, s["gate_claim"].split(" "), 26, "#FFFFFF", "800"))
    x = 250
    gw, gap = 176, 30
    for i, step in enumerate(s["gate_steps"]):
        b.append(line(x - gap - 4, cy, x - 6, cy, INK, 5, "round"))
        b.append(line(x - 16, cy - 9, x - 6, cy, INK, 5, "round"))
        b.append(line(x - 16, cy + 9, x - 6, cy, INK, 5, "round"))
        col = [BLUE, VIOLET, TEAL, AMBER, GREEN, CORAL][i]
        b.append(rect(x, cy - 78, gw, 156, INK, rx=14))
        b.append(rect(x, cy - 78, gw, 12, col, rx=6))
        b.append(rect(x, cy - 78, 12, 156, col, rx=6))
        b.append(multitext(x + gw / 2, cy - 6, step.split("\n"), 28, PAPER, "700"))
        b.append(text(x + gw / 2, cy + 58, str(i + 1), 22, col, "800", "middle"))
        x += gw + gap
    # arrow to OK
    b.append(line(x - gap - 4, cy, x - 6, cy, INK, 5, "round"))
    b.append(line(x - 16, cy - 9, x - 6, cy, INK, 5, "round"))
    b.append(line(x - 16, cy + 9, x - 6, cy, INK, 5, "round"))
    b.append(circle(x + 66, cy, 66, GREEN))
    b.append(text(x + 66, cy + 10, s["gate_ok"], 34, "#FFFFFF", "800", "middle"))
    # fail branch
    b.append(line(x - gw / 2 - gap, cy + 78, x - gw / 2 - gap, cy + 150, CORAL, 5, "round"))
    b.append(rect(x - gw / 2 - gap - 120, cy + 150, 240, 96, "#FBE8E2", rx=12, stroke=CORAL, sw=3))
    b.append(multitext(x - gw / 2 - gap, cy + 186, s["gate_fail"].split("\n"), 24, CORAL, "700"))
    b.append(text(x - gw / 2 - gap + 92, cy + 210, "✗", 40, CORAL, "800", "middle"))
    b.append(text(88, H - 40, s["fig_gate_cap"], 24, SLATE, "500"))
    return _svg(W, H, "\n".join(b))


def fig_prov(s: dict) -> str:
    W, H = 1600, 620
    b = _fig_frame(W, H, s, s["fig_prov"])
    cy = 300
    nodes = s["prov_nodes"]
    subs = s["prov_sub"]
    cols = [AMBER, INK, TEAL, BLUE, VIOLET]
    nw, gap = 232, 66
    x = 120
    centers = []
    for i, (n, sub, col) in enumerate(zip(nodes, subs, cols)):
        b.append(rect(x, cy - 62, nw, 124, col, rx=16))
        b.append(rect(x, cy - 62, nw, 10, "#FFFFFF", rx=5, opacity=0.4))
        fg = PAPER if col == INK else "#FFFFFF"
        b.append(text(x + nw / 2, cy - 4, n, 34, fg, "800", "middle"))
        b.append(text(x + nw / 2, cy + 34, sub, 21, fg, "500", "middle"))
        centers.append((x, x + nw))
        x += nw + gap
    # chain links between nodes
    for i in range(len(nodes) - 1):
        x1 = centers[i][1]
        x2 = centers[i + 1][0]
        b.append(line(x1 + 6, cy, x2 - 6, cy, INK, 6, "round"))
        b.append(rect((x1 + x2) / 2 - 15, cy - 15, 30, 30, CARD, rx=8, stroke=INK, sw=5))
        b.append(line(x2 - 18, cy - 9, x2 - 6, cy, INK, 6, "round"))
        b.append(line(x2 - 18, cy + 9, x2 - 6, cy, INK, 6, "round"))
    b.append(text(88, H - 42, s["fig_prov_cap"], 24, SLATE, "500"))
    return _svg(W, H, "\n".join(b))


FIGURES = {
    "cover-front.svg": cover_front,
    "cover-back.svg": cover_back,
    "fig-evidence-ladder.svg": fig_ladder,
    "fig-gate-pipeline.svg": fig_gate,
    "fig-provenance-chain.svg": fig_prov,
}


def build() -> list[Path]:
    written = []
    for lang, strings in STR.items():
        d = OUT / lang
        d.mkdir(parents=True, exist_ok=True)
        for name, fn in FIGURES.items():
            p = d / name
            p.write_text(fn(strings), encoding="utf-8")
            written.append(p)
    return written


def main(argv: list[str]) -> int:
    if "--check" in argv:
        for lang in STR:
            for name in FIGURES:
                print(OUT / lang / name)
        return 0
    written = build()
    print(f"[OK] wrote {len(written)} figures under {OUT}")
    return 0


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
