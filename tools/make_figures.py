# SPDX-License-Identifier: Apache-2.0
"""Generate the print-edition figures as deterministic, hand-authored SVG.

A governance handbook earns its illustrations by drawing its own ideas, not
decoration: the claim seal (front cover), a quiet companion mark and blurb (back
cover), and three interior figures, the evidence ladder, the gate pipeline, and
the provenance chain. Everything is vector and text, so it commits, diffs, prints
crisp at any size, and regenerates byte-identically (see tests/test_figures.py).

Art direction: editorial, an antique-press palette (brass, pine, terracotta,
aubergine on warm ivory), double-keyline cover frames, restrained type. No ISBN
or barcode is drawn, because none has been assigned.

Output: docs/governance/print/figures/{en,no}/*.svg

Usage: python3 tools/make_figures.py            # writes all figures
       python3 tools/make_figures.py --check    # print output paths only
"""
from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs" / "governance" / "print" / "figures"

# --- palette (curated editorial, full colour) -------------------------------
PAPER = "#F1EBDD"       # warm ivory ground
CARD = "#F8F3E8"        # figure card
INK = "#182530"         # charcoal navy
SLATE = "#57636D"       # neutral, biased warm
GOLD = "#B4832B"        # antique brass (the seal)
GOLD_SOFT = "#D8B871"   # lit brass
PINE = "#1C6E62"        # deep teal-green
STEEL = "#3D6784"       # slate blue
SAGE = "#5C8158"        # muted green
PLUM = "#6B4E77"        # aubergine
CLAY = "#AE5637"        # terracotta (refusal)
HAIR = "#DED4C0"        # hairline on ivory

# rising confidence: cool and quiet -> warm and rich, ending in brass
LEVEL_COLOURS = [SLATE, STEEL, PINE, SAGE, PLUM, GOLD]
LEVELS = ["theoretical", "measured", "benchmarked",
          "reproduced", "machine_checked", "externally_validated"]

STR = {
    "en": {
        "title": ["THE FRONTIER", "AI GOVERNANCE", "HANDBOOK"],
        "subtitle": "Evidence-bound governance for frontier AI systems",
        "author": "STIAN SKOGBROTT",
        "imprint": "CLAIM-ORIENTED PROGRAMMING · VERICLAIM",
        "seal": "VERIFIED CLAIM",
        "back_head": ["Governance you can attack,", "and still stand behind."],
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
        "gate_ok": "OK",
        "gate_fail": ["drift", "fails the build"],
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
        "title": ["HÅNDBOK I", "STYRING AV", "FRONTIER-AI"],
        "subtitle": "Evidensbundet styring for frontier-AI-systemer",
        "author": "STIAN SKOGBROTT",
        "imprint": "CLAIM-ORIENTED PROGRAMMING · VERICLAIM",
        "seal": "VERIFISERT PÅSTAND",
        "back_head": ["Styring som tåler angrep,", "og likevel står."],
        "back_body": [
            "AI-styring bygget som et system av sjekkbare",
            "påstander, ikke en bunke betryggende dokumenter.",
            "Hver sterk påstand er en registrert påstand på et",
            "oppgitt evidensnivå, bundet til committet evidens,",
            "sjekket ved hver commit. Boken bruker sin egen disiplin.",
        ],
        "back_foot": "Metoden er poenget, ikke tallene.",
        "fig_ladder": "Evidensstigen",
        "fig_ladder_cap": ("Beskriv en påstand bare på nivået den har fortjent. "
                           "Nedgradering er alltid tillatt; oppgradering krever ny evidens."),
        "promote": "oppgradering krever ny evidens",
        "demote": "nedgradering alltid tillatt",
        "fig_gate": "Porten, ved hver commit",
        "gate_steps": ["Register-\nintegritet", "Artefakt-\neksistens", "Sti-\ninneslutning",
                       "Proveniens", "Manifest-\nhasher", "Dok-\nbinding"],
        "gate_claim": "en påstand",
        "gate_ok": "OK",
        "gate_fail": ["drift", "feiler bygget"],
        "fig_gate_cap": ("En påstand kjører hver sjekk ved hver commit. Enhver drift, et "
                         "endret tall, en brutt hash, et dokument over sin evidens, feiler bygget."),
        "fig_prov": "Proveniens-kjeden",
        "prov_nodes": ["Artefakt", "SHA-256", "Følgefil", "Register", "Manifest"],
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


def multitext(x, y, lines, size, fill, weight="normal", anchor="middle", lh=1.2):
    return "\n".join(text(x, y + i * size * lh, ln, size, fill, weight, anchor)
                     for i, ln in enumerate(lines))


def hexagon(cx, cy, r, rot=math.pi / 2):
    return [(cx + r * math.cos(rot + k * math.pi / 3),
             cy + r * math.sin(rot + k * math.pi / 3)) for k in range(6)]


def check(cx, cy, s, colour, sw):
    p = (f'M {cx - s:.1f} {cy:.1f} L {cx - s*0.28:.1f} {cy + s*0.66:.1f} '
         f'L {cx + s:.1f} {cy - s*0.78:.1f}')
    return (f'<path d="{p}" fill="none" stroke="{colour}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def keyline(w, h, m=46):
    return "\n".join([
        rect(m, m, w - 2 * m, h - 2 * m, "none", stroke=INK, sw=2),
        rect(m + 13, m + 13, w - 2 * m - 26, h - 2 * m - 26, "none", stroke=GOLD, sw=1.2),
    ])


def arrowhead(x, y, ang, size, colour, sw):
    return "\n".join(
        line(x, y, x + size * math.cos(ang + da), y + size * math.sin(ang + da),
             colour, sw, "round")
        for da in (math.radians(148), math.radians(-148)))


# --- the claim seal (shared by both covers) ---------------------------------
def seal(cx, cy, r, *, quiet=False):
    b = []
    if not quiet:
        # finely scalloped brass edge
        bumps = 52
        for i in range(bumps):
            a = 2 * math.pi * i / bumps
            b.append(circle(cx + r * math.cos(a), cy + r * math.sin(a), r * 0.052, GOLD))
        b.append(circle(cx, cy, r * 0.985, GOLD))
        b.append(circle(cx, cy, r * 0.90, INK))
    # fine milled tick ring (hash motif)
    ticks = 72
    tcol = GOLD_SOFT if not quiet else SLATE
    for i in range(ticks):
        a = 2 * math.pi * i / ticks
        long = (i % 6 == 0)
        r0 = r * (0.74 if long else 0.78)
        b.append(line(cx + r0 * math.cos(a), cy + r0 * math.sin(a),
                      cx + r * 0.84 * math.cos(a), cy + r * 0.84 * math.sin(a),
                      tcol, r * (0.014 if long else 0.008)))
    # twin keylines
    b.append(circle(cx, cy, r * 0.68, "none", stroke=(SLATE if quiet else GOLD_SOFT), sw=r * 0.012))
    b.append(circle(cx, cy, r * 0.64, "none", stroke=(SLATE if quiet else GOLD_SOFT), sw=r * 0.006))
    # inner hexagon
    b.append(poly(hexagon(cx, cy, r * 0.56), "none",
                  stroke=(INK if quiet else GOLD), sw=r * 0.016))
    # three rising rungs
    base = cy + r * 0.30
    rung_cols = [PINE, SAGE, GOLD] if not quiet else [SLATE, SLATE, SLATE]
    for i, col in enumerate(rung_cols):
        bw = r * 0.13
        bx = cx - r * 0.24 + i * r * 0.19
        bh = r * 0.11 + i * r * 0.09
        b.append(rect(bx, base - bh, bw, bh, col, rx=r * 0.012))
    # the check, sitting above the rungs
    b.append(check(cx, cy - r * 0.12, r * 0.28, (INK if quiet else PAPER), r * 0.075))
    return "\n".join(b)


# --- covers -----------------------------------------------------------------
def cover_front(s: dict) -> str:
    W, H = 1200, 1800
    M = 132
    b = [rect(0, 0, W, H, PAPER), keyline(W, H)]
    # imprint eyebrow + rule
    b.append(text(M, 190, s["imprint"], 22, SLATE, "600", "start", spacing=3))
    b.append(line(M, 214, M + 300, 214, GOLD, 2))
    # title
    for i, ln in enumerate(s["title"]):
        b.append(text(M, 348 + i * 100, ln, 82, INK, "800", "start", spacing=0.5))
    b.append(text(M, 348 + 3 * 100 + 4, s["subtitle"], 28, PINE, "600", "start"))
    # seal, the hero
    b.append(seal(600, 1170, 300))
    b.append(text(600, 1556, s["seal"], 30, INK, "700", "middle", spacing=11))
    # foot
    b.append(line(M, 1652, W - M, 1652, GOLD, 1.5))
    b.append(text(M, 1712, s["author"], 36, INK, "800", "start", spacing=2))
    return _svg(W, H, "\n".join(b))


def cover_back(s: dict) -> str:
    W, H = 1200, 1800
    M = 132
    b = [rect(0, 0, W, H, PAPER), keyline(W, H)]
    # quiet companion mark
    b.append(seal(600, 330, 165, quiet=True))
    b.append(line(600 - 90, 560, 600 + 90, 560, GOLD, 1.5))
    # headline
    for i, ln in enumerate(s["back_head"]):
        b.append(text(600, 700 + i * 62, ln, 50, INK, "800", "middle"))
    # blurb
    for i, ln in enumerate(s["back_body"]):
        b.append(text(600, 866 + i * 52, ln, 30, SLATE, "500", "middle"))
    # tagline
    b.append(text(600, 1206, s["back_foot"], 33, PINE, "700", "middle", italic=True))
    # a quiet evidence-ladder motif
    n = len(LEVEL_COLOURS)
    bw, gap = 118, 26
    total = n * bw + (n - 1) * gap
    x0 = 600 - total / 2
    base = 1520
    for i, c in enumerate(LEVEL_COLOURS):
        bh = 32 + i * 26
        b.append(rect(x0 + i * (bw + gap), base - bh, bw, bh, c, rx=6))
    # foot imprint
    b.append(line(M, 1636, W - M, 1636, GOLD, 1.5))
    b.append(text(600, 1694, s["imprint"], 22, SLATE, "600", "middle", spacing=3))
    return _svg(W, H, "\n".join(b))


# --- interior figures -------------------------------------------------------
def _frame(W, H, title):
    return [rect(6, 6, W - 12, H - 12, CARD, rx=22, stroke=HAIR, sw=2),
            rect(60, 58, 6, 42, GOLD, rx=3),
            text(84, 92, title, 40, INK, "800"),
            line(60, 120, W - 60, 120, HAIR, 1.5)]


def fig_ladder(s: dict) -> str:
    W, H = 1400, 900
    b = _frame(W, H, s["fig_ladder"])
    x0, base = 150, 706
    step_w, step_dx = 162, 172
    for i, (lv, col) in enumerate(zip(LEVELS, LEVEL_COLOURS)):
        h = 92 + i * 74
        x = x0 + i * step_dx
        y = base - h
        # riser connecting to the previous step, quiet
        if i:
            b.append(line(x, y, x, base, HAIR, 1.5))
        b.append(rect(x, y, step_w, h, col, rx=9))
        b.append(circle(x + 30, y + 32, 19, CARD))
        b.append(text(x + 30, y + 39, str(i + 1), 23, col, "800", "middle"))
        b.append(f'<text x="{x + step_w/2:.0f}" y="{base - 20:.0f}" font-size="21" '
                 f'fill="{CARD}" font-weight="700" text-anchor="start" '
                 f'transform="rotate(-90 {x + step_w/2:.0f} {base - 20:.0f})">{esc(lv)}</text>')
    b.append(line(x0 - 34, base, x0 + 6 * step_dx, base, INK, 2))
    # a slim upward arrow, above the steps
    ax0, ay0 = x0 + 30, 250
    ax1, ay1 = x0 + 5 * step_dx + step_w - 20, 250
    b.append(line(ax0, ay0, ax1, ay1, GOLD, 3, "round"))
    b.append(arrowhead(ax1, ay1, 0, 22, GOLD, 3))
    b.append(text(ax0, ay0 - 20, s["promote"], 22, GOLD, "700", "start"))
    b.append(text(x0 - 6, base + 46, s["demote"], 22, CLAY, "700", "start"))
    b.append(text(84, H - 46, s["fig_ladder_cap"], 24, SLATE, "500"))
    return _svg(W, H, "\n".join(b))


def _connector(x, cy, colour):
    return "\n".join([line(x, cy, x + 34, cy, colour, 2, "round"),
                      arrowhead(x + 34, cy, 0, 13, colour, 2)])


def fig_gate(s: dict) -> str:
    W, H = 1600, 720
    b = _frame(W, H, s["fig_gate"])
    cy = 372
    accents = [STEEL, PLUM, PINE, GOLD, SAGE, CLAY]
    # claim token, an outlined disc (quiet, lets the gate blocks lead)
    b.append(circle(118, cy, 60, "none", stroke=PINE, sw=4))
    b.append(multitext(118, cy - 2, s["gate_claim"].split(" "), 24, PINE, "700"))
    x = 240
    gw, gap = 178, 34
    for i, step in enumerate(s["gate_steps"]):
        b.append(_connector(x - gap - 2, cy, INK))
        b.append(rect(x, cy - 74, gw, 148, INK, rx=13))
        b.append(rect(x + 22, cy - 74, gw - 44, 5, accents[i]))
        b.append(multitext(x + gw / 2, cy - 8, step.split("\n"), 27, PAPER, "600"))
        b.append(text(x + gw / 2, cy + 54, str(i + 1), 20, accents[i], "800", "middle"))
        x += gw + gap
    b.append(_connector(x - gap - 2, cy, INK))
    b.append(circle(x + 60, cy, 60, PINE))
    b.append(text(x + 60, cy + 9, s["gate_ok"], 34, PAPER, "800", "middle"))
    # quiet refusal branch
    fx = 240 + 2 * (gw + gap) + gw / 2
    b.append(line(fx, cy + 74, fx, cy + 128, CLAY, 2, "round"))
    b.append(arrowhead(fx, cy + 128, math.pi / 2, 12, CLAY, 2))
    b.append(rect(fx - 118, cy + 138, 236, 74, "none", rx=11, stroke=CLAY, sw=1.6))
    b.append(multitext(fx, cy + 172, s["gate_fail"], 23, CLAY, "600"))
    b.append(text(84, H - 42, s["fig_gate_cap"], 23, SLATE, "500"))
    return _svg(W, H, "\n".join(b))


def fig_prov(s: dict) -> str:
    W, H = 1600, 620
    b = _frame(W, H, s["fig_prov"])
    cy = 336
    cols = [GOLD, INK, PINE, STEEL, PLUM]
    nw, gap = 232, 64
    x = 118
    spans = []
    for n, sub, col in zip(s["prov_nodes"], s["prov_sub"], cols):
        b.append(rect(x, cy - 60, nw, 120, col, rx=14))
        b.append(rect(x + 20, cy - 60, nw - 40, 4, GOLD_SOFT if col != GOLD else INK))
        fg = PAPER if col in (INK,) else "#FFFFFF"
        b.append(text(x + nw / 2, cy - 4, n, 33, fg, "800", "middle"))
        b.append(text(x + nw / 2, cy + 32, sub, 20, fg, "500", "middle"))
        spans.append((x, x + nw))
        x += nw + gap
    for i in range(len(spans) - 1):
        x1, x2 = spans[i][1], spans[i + 1][0]
        b.append(line(x1 + 4, cy, x2 - 4, cy, INK, 2, "round"))
        b.append(rect((x1 + x2) / 2 - 13, cy - 13, 26, 26, CARD, rx=7, stroke=INK, sw=3))
        b.append(arrowhead(x2 - 4, cy, 0, 12, INK, 2))
    b.append(text(84, H - 44, s["fig_prov_cap"], 23, SLATE, "500"))
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
