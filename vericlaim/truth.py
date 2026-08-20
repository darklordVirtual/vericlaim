# SPDX-License-Identifier: Apache-2.0
"""The capability contract — roadmap may not be presented as shipped.

A claim register stops a *number* from drifting. It does nothing about the
other half of documentation drift: a capability that is designed, prototyped or
merely intended, written up in the present tense on the front page. That is the
most common way an otherwise honest project overstates itself, and it is the
one an AI assistant reproduces most readily, because roadmap prose and shipped
prose look identical to a language model summarising a repository.

REMORA solves this with a product truth contract: every advertised capability
is classified, and CI refuses documentation that presents a non-core capability
as part of the canonical path. This is the same idea sized for vericlaim:

    [vericlaim.capabilities]
    "declarative reproduce" = "shipped"
    "sandboxed runner"      = "designed"
    "signed attestation"    = "designed"

Rules, both mechanical:

1. A term classified anything other than ``shipped`` may not appear in a
   front-page document unless the sentence around it carries a hedge word
   (``roadmap``, ``planned``, ``designed``, ``not yet``, ``proposed`` ...).
   Naming a future capability is fine; naming it as if it existed is not.
2. Every roadmap entry must be classified. The roadmap file and the capability
   table cannot drift apart, because an unclassified roadmap item is a finding.

The check never guesses at tense. It looks for a declared term and a declared
hedge, which is why it produces almost no false positives - and why the
capability table has to be written by hand, deliberately, once per capability.
"""
from __future__ import annotations

import re

from .config import Config

Finding = tuple[str, str]

SHIPPED = "shipped"
# Words that mark a sentence as speaking about the future. Kept short and
# explicit: a longer list would start excusing genuinely misleading prose.
DEFAULT_HEDGES = (
    "roadmap", "planned", "plan to", "designed", "not yet", "proposed",
    "future", "intend", "would", "will be", "upcoming", "todo",
)
# Roadmap bullets: `- STATUS **Term.** rest` — the bold run is the capability.
ROADMAP_ITEM_RE = re.compile(r"^\s*[-*]\s+(?P<status>\S+)?\s*\*\*(?P<term>[^*]+?)\.?\*\*")


def _hedged(window: str, cfg: Config) -> bool:
    low = window.lower()
    return any(h in low for h in (*DEFAULT_HEDGES, *cfg.capability_hedges))


def check_capability_claims(cfg: Config, rel: str, text: str) -> list[Finding]:
    """Rule 1: an unshipped capability may not be stated as present."""
    if not cfg.capabilities or rel not in cfg.front_page:
        return []
    out: list[Finding] = []
    lines = text.splitlines()
    in_fence = False
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        low = line.lower()
        for term, cls in cfg.capabilities:
            if cls == SHIPPED or term.lower() not in low:
                continue
            # The hedge may sit in the sentence before or after: read the line
            # and its neighbours, which is the unit a reader takes meaning from.
            window = " ".join(lines[max(0, idx - 1):idx + 2])
            if _hedged(window, cfg):
                continue
            out.append((f"capability-overstated:{rel}:{term}",
                        f"{rel}:{idx+1}: '{term}' is classified '{cls}', not "
                        f"'{SHIPPED}', but this line states it with no marker "
                        f"that it is future work - say so, or ship it and "
                        f"reclassify it in [vericlaim.capabilities]"))
    return out


def check_roadmap_classified(cfg: Config) -> list[Finding]:
    """Rule 2: every roadmap entry appears in the capability table."""
    if not cfg.roadmap or not cfg.capabilities:
        return []
    path = cfg.path(cfg.roadmap)
    if not path.exists():
        return [(f"roadmap-missing:{cfg.roadmap}",
                 f"{cfg.roadmap}: configured roadmap file does not exist")]
    known = {term.lower() for term, _ in cfg.capabilities}
    out: list[Finding] = []
    in_fence = False
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = ROADMAP_ITEM_RE.match(line)
        if not m:
            continue
        term = m.group("term").strip()
        if any(k in term.lower() or term.lower() in k for k in known):
            continue
        out.append((f"roadmap-unclassified:{term}",
                    f"{cfg.roadmap}:{idx+1}: roadmap item '{term}' is not "
                    f"classified in [vericlaim.capabilities] - an unclassified "
                    f"item is one the front-page check cannot protect against"))
    return out
