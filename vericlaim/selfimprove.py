# SPDX-License-Identifier: Apache-2.0
"""Bounded, verifiable, human-gated self-improvement for a claim repository.

Anthropic's note on recursive self-improvement
(https://www.anthropic.com/institute/recursive-self-improvement) frames the
danger of a system that *fully autonomously* designs its successor: **loss of
control** and **compounding misalignment** — rare errors amplifying as each
generation builds the next. Its recommended posture is bounded change,
transparent verification, and a reliable ability to stop.

This module implements the ONLY form of self-improvement that is defensible for a
verification tool: it can *propose* improvements to its own claims, and it
provides a **non-weakening safety envelope** — a guard that refuses any
self-proposed change unless every existing guarantee is preserved or
strengthened. The system can ratchet its own quality **up**, never down, and it
cannot edit its own verifier to pass. It does not apply changes, commit, push, or
merge — a human does. There is a kill-switch sentinel.

Mapping to the article's concerns:

- **loss of control** -> propose-only; no autonomous apply/commit/push; a STOP
  sentinel; the proposer modifies nothing.
- **compounding misalignment** -> `check_non_weakening`: a candidate is rejected
  unless it is monotonically non-weakening (no claim removed, no evidence level
  demoted, gate still green, tests not reduced, baseline not grown, and the
  trusted verifier core byte-unchanged). Errors cannot compound because a
  regression cannot pass the guard.
- **verification / transparent inspection** -> every proposal is a logged,
  deterministic artifact; the envelope re-checks against a captured baseline.
- **ability to stop** -> `STOP_SENTINEL`; propose-only means every step is a
  human decision.

Honest limit: this guards the *repository's declared guarantees*. It does not
make the tool smarter, does not prove semantic truth, and — being propose-only —
carries no autonomy risk to bound in the first place. The apply loop is
deliberately not implemented; that boundary is the safety mechanism.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .config import Config
from .register import RegisterError, load_register

# The trusted verification core. A self-improvement proposal that edits ANY of
# these is refused: the system must not be able to weaken or rewrite its own
# checker to make a change pass ("no changing the gate to pass the gate").
PROTECTED_CORE: tuple[str, ...] = (
    "vericlaim/gate.py",
    "vericlaim/pathsafe.py",
    "vericlaim/repro.py",
    "vericlaim/reproduce.py",
    "vericlaim/register.py",
    "vericlaim/provenance.py",
    "vericlaim/config.py",
    "vericlaim/selfimprove.py",
)

# Presence of this file disables self-improvement entirely (the kill switch).
STOP_SENTINEL = "claims/STOP_SELF_IMPROVEMENT"

# Rungs a proposer should flag for possible (evidence-backed) promotion.
_WEAK_RUNGS = ("theoretical", "measured")


@dataclass(frozen=True)
class Snapshot:
    """A capture of a repository's verifiable guarantees at one point in time."""
    claim_levels: dict[str, int]      # claim id -> evidence-ladder index
    test_count: int
    baseline_count: int
    core_hashes: dict[str, str]       # protected-core relpath -> sha256 (or "MISSING")
    gate_ok: bool

    @classmethod
    def capture(cls, cfg: Config, *, gate_ok: bool, test_count: int) -> Snapshot:
        ladder = {name: i for i, name in enumerate(cfg.evidence_levels)}
        claim_levels: dict[str, int] = {}
        reg = cfg.path(cfg.register)
        if reg.exists():
            try:
                for c in load_register(reg.read_text(encoding="utf-8")):
                    cid = str(c.get("id", "")).strip()
                    lvl = str(c.get("evidence_level", "")).strip()
                    if cid:
                        claim_levels[cid] = ladder.get(lvl, -1)
            except RegisterError:
                claim_levels = {}
                gate_ok = False  # an unparseable register is not a passing state
        baseline_count = _baseline_count(cfg)
        # Hash the ENTIRE trusted core package, not a hardcoded subset — so a
        # self-proposed change that ADDS a new core module or DELETES one is
        # detected too, not only edits to known files.
        core_hashes = _hash_tree(cfg.path("vericlaim"))
        return cls(claim_levels, test_count, baseline_count, core_hashes, gate_ok)


def check_non_weakening(before: Snapshot, after: Snapshot) -> list[str]:
    """Return the list of ways *after* WEAKENS *before*. Empty list == safe to
    consider. A self-proposed change may be applied (by a human) only if this
    returns no violations. Fail closed — any doubt is a violation.

    TRUST MODEL (important): this is a pure comparator over two snapshots. It does
    NOT itself run the gate or count tests — it trusts the ``gate_ok`` and
    ``test_count`` recorded in *after*. Its guarantee is therefore only as honest
    as the capture that produced *after*; ``Snapshot.capture`` derives them from
    the real repo (and forces ``gate_ok=False`` on an unparseable register), but a
    caller that hand-builds a snapshot with ``gate_ok=True`` can defeat it. This is
    why self-improvement is PROPOSE-ONLY and human-gated: the envelope is a
    guardrail against accidental regression, not an autonomous gatekeeper that can
    withstand a dishonest caller."""
    violations: list[str] = []

    # 1. The candidate must itself pass the gate. A red gate is never an
    #    improvement, no matter what else it changes.
    if not after.gate_ok:
        violations.append("candidate does not pass the gate (fail-closed)")

    # 2. No claim may disappear.
    removed = set(before.claim_levels) - set(after.claim_levels)
    if removed:
        violations.append(f"claims removed: {sorted(removed)}")

    # 3. No shared claim may be demoted on the evidence ladder.
    for cid, lvl in before.claim_levels.items():
        after_lvl = after.claim_levels.get(cid)
        if after_lvl is not None and after_lvl < lvl:
            violations.append(f"claim {cid} demoted on the evidence ladder ({lvl} -> {after_lvl})")

    # 4. Test coverage may not shrink.
    if after.test_count < before.test_count:
        violations.append(f"test count reduced ({before.test_count} -> {after.test_count})")

    # 5. Grandfathered-violation debt may not grow.
    if after.baseline_count > before.baseline_count:
        violations.append(
            f"baseline (known_violations) grew ({before.baseline_count} -> {after.baseline_count})")

    # 6. The trusted verifier core must be byte-identical — no file under the
    #    vericlaim/ package may be modified, ADDED, or REMOVED by a self-proposed
    #    change (it must not edit, extend, or delete its own checker).
    if before.core_hashes != after.core_hashes:
        b, a = before.core_hashes, after.core_hashes
        added = sorted(set(a) - set(b))
        removed = sorted(set(b) - set(a))
        modified = sorted(k for k in set(a) & set(b) if a[k] != b[k])
        detail = []
        if modified:
            detail.append(f"modified={modified}")
        if added:
            detail.append(f"added={added}")
        if removed:
            detail.append(f"removed={removed}")
        violations.append("trusted verifier core changed (" + ", ".join(detail) +
                          ") — a self-improvement may not edit, extend, or delete its own checker")
    return violations


@dataclass(frozen=True)
class Suggestion:
    """One advisory, evidence-honest improvement the tool proposes. It is never
    auto-applied and never fabricates evidence."""
    claim_id: str
    kind: str
    detail: str


def propose(cfg: Config) -> list[Suggestion]:
    """Scan the repository's OWN claims and propose concrete, honest improvements.

    This modifies nothing. It never invents evidence, never auto-promotes an
    evidence level, and never suggests weakening anything — promotion always
    requires real new evidence a human/agent produces in a gated repo."""
    reg = cfg.path(cfg.register)
    if not reg.exists():
        return []
    try:
        claims = load_register(reg.read_text(encoding="utf-8"))
    except RegisterError:
        return []
    out: list[Suggestion] = []
    for c in sorted(claims, key=lambda c: str(c.get("id", ""))):
        cid = str(c.get("id", "")).strip()
        level = str(c.get("evidence_level", "")).strip()
        if level in _WEAK_RUNGS:
            out.append(Suggestion(
                cid, "promote-with-evidence",
                f"at '{level}': if stronger evidence exists, produce the artifact and "
                f"promote — never promote without it."))
        if not c.get("reproduce"):
            out.append(Suggestion(
                cid, "add-reproduce",
                "no reproduce spec: add a declarative reproduce so the number is "
                "re-checkable from scratch."))
        if not c.get("metrics"):
            out.append(Suggestion(
                cid, "add-metrics",
                "no metrics: if the claim quotes numbers, register them so docs can "
                "bind to them."))
    return out


def stopped(cfg: Config) -> bool:
    """True if the kill-switch sentinel is present — self-improvement is disabled."""
    return cfg.path(STOP_SENTINEL).exists()


def _baseline_count(cfg: Config) -> int:
    import json
    p = cfg.path(cfg.baseline)
    if not p.exists():
        return 0
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        kv = data.get("known_violations", [])
        return len(kv) if isinstance(kv, list) else 0
    except (json.JSONDecodeError, OSError):
        return 0


def _hash_file(p: Path) -> str:
    if not p.exists():
        return "MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _hash_tree(root: Path) -> dict[str, str]:
    """Map every source file under *root* (posix relpath) to its sha256. Skips
    __pycache__ and compiled artifacts. Empty dict if *root* does not exist."""
    if not root.is_dir():
        return {}
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        out[p.relative_to(root).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out
