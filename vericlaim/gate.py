# SPDX-License-Identifier: Apache-2.0
"""The vericlaim gate — Claim-Oriented Programming enforcement.

The gate is the executable contract for a project's *claims about itself*.
It runs in CI and fails the build when any of the following drift:

1. REGISTER INTEGRITY   — every claim has the required fields and a valid
                          evidence level.
2. ARTIFACT EXISTENCE   — every artifact a claim cites exists on disk
                          ("no claim without an artifact").
3. MANIFEST HASHES      — every SHA-256 in the manifest matches the file bytes
                          (LF-normalized; CRLF working trees pass with a note).
4. DOC BINDING          — claim anchors ``<!-- claim:ID field ... -->`` assert
                          that the register's value for each field appears in
                          the following paragraph, so prose cannot drift from
                          the register.
5. EVIDENCE CITATIONS   — a doc line naming a CLAIM id together with an
                          evidence-level term must agree with the register.
6. STALE STRINGS        — a configurable denylist of corrected strings that
                          must never reappear.

Known violations are grandfathered in the baseline file (reported as WARN);
anything new fails with a non-zero exit. This lets a project adopt the gate
incrementally without a big-bang cleanup.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .config import Config
from .register import load_register

ANCHOR_RE = re.compile(r"<!--\s*claim:([A-Za-z0-9_.-]+)((?:\s+[A-Za-z0-9_.-]+)+)\s*-->")
CLAIM_ID_RE = re.compile(r"\b[A-Z][A-Z0-9]*-\d+\b")
MANIFEST_ROW_RE = re.compile(
    r"^\|\s*`(?P<path>[^`]+)`\s*\|\s*`(?P<sha>[0-9a-fA-F]{64})`\s*\|"
)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")

Finding = tuple[str, str]  # (error_id, human message)


# --------------------------------------------------------------------------- #
# Checks
# --------------------------------------------------------------------------- #

def check_register(claims: list[dict], cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    if not claims:
        # A project legitimately starts with no claims (fresh `vericlaim init`).
        # This is a valid, passing state — run() prints a note.
        return out
    seen: set[str] = set()
    for c in claims:
        cid = c.get("id", "<missing-id>")
        if cid in seen:
            out.append((f"register-duplicate-id:{cid}", f"{cid}: duplicate claim id"))
        seen.add(cid)
        for f in cfg.required_fields:
            if f not in c or c[f] in (None, "", []):
                out.append((f"register-missing-field:{cid}:{f}",
                            f"{cid}: required field '{f}' missing or empty"))
        lvl = c.get("evidence_level")
        if lvl is not None and lvl not in cfg.evidence_levels:
            out.append((f"register-bad-level:{cid}",
                        f"{cid}: evidence_level '{lvl}' not in taxonomy"))
    return out


def check_artifacts(claims: list[dict], cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    for c in claims:
        cid = c.get("id", "<missing-id>")
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        for rel in arts:
            if not cfg.path(rel).exists():
                out.append((f"artifact-missing:{cid}:{rel}",
                            f"{cid}: cited artifact does not exist: {rel}"))
    return out


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_manifest(cfg: Config, notes: list[str]) -> list[Finding]:
    out: list[Finding] = []
    if not cfg.manifest:
        return out
    mpath = cfg.path(cfg.manifest)
    if not mpath.exists():
        return out
    for n, line in enumerate(mpath.read_text(encoding="utf-8").splitlines(), 1):
        row = MANIFEST_ROW_RE.match(line)
        if not row:
            continue
        rel, sha = row.group("path"), row.group("sha")
        if sha != sha.lower():
            out.append((f"manifest-hash-casing:{rel}",
                        f"{cfg.manifest}:{n}: non-canonical hash casing for {rel} "
                        f"(use lowercase hex)"))
        p = cfg.path(rel)
        if not p.exists():
            out.append((f"manifest-file-missing:{rel}",
                        f"{cfg.manifest}:{n}: manifest lists {rel} but the file is absent"))
            continue
        data = p.read_bytes()
        expected = sha.lower()
        if _sha256(data) == expected:
            continue
        if _sha256(data.replace(b"\r\n", b"\n")) == expected:
            notes.append(f"{rel}: CRLF working tree; LF-normalized hash matches")
            continue
        out.append((f"manifest-hash-mismatch:{rel}",
                    f"{cfg.manifest}:{n}: SHA-256 mismatch for {rel} "
                    f"(content differs from the manifested version)"))
    return out


def _display(cfg: Config, p: Path) -> str:
    try:
        return p.relative_to(cfg.root).as_posix()
    except ValueError:
        return p.name


def _paragraph_after(lines: list[str], idx: int) -> str:
    j = idx + 1
    while j < len(lines) and not lines[j].strip():
        j += 1
    block: list[str] = []
    while j < len(lines) and lines[j].strip():
        block.append(lines[j])
        j += 1
    return " ".join(block)


_INLINE_CODE_RE = re.compile(r"`[^`]*`")


def check_doc_anchors(cfg: Config, path: Path, text: str,
                      by_id: dict[str, dict]) -> list[Finding]:
    out: list[Finding] = []
    rel = _display(cfg, path)
    lines = text.splitlines()
    in_fence = False
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue  # anchors shown inside code fences are illustrative, not live
        # Blank inline-code spans so `<!-- claim:ID ... -->` shown as an example
        # in prose is not treated as a real anchor.
        scan = _INLINE_CODE_RE.sub("", line)
        for m in ANCHOR_RE.finditer(scan):
            cid, blob = m.group(1), m.group(2)
            claim = by_id.get(cid)
            if claim is None:
                out.append((f"anchor-unknown-claim:{rel}:{cid}",
                            f"{rel}:{idx+1}: anchor cites unknown claim {cid}"))
                continue
            paragraph = scan[m.end():] + " " + _paragraph_after(lines, idx)
            found = {float(t) for t in NUMBER_RE.findall(paragraph)}
            metrics = claim.get("metrics") or {}
            for key in blob.split():
                expected = claim.get("n") if key == "n" else (
                    metrics.get(key) if isinstance(metrics, dict) else None)
                if expected is None:
                    out.append((f"anchor-unknown-metric:{rel}:{cid}:{key}",
                                f"{rel}:{idx+1}: anchor metric '{key}' not defined "
                                f"in register for {cid}"))
                    continue
                if float(expected) not in found:
                    out.append((f"anchor-value-drift:{rel}:{cid}:{key}",
                                f"{rel}:{idx+1}: register says {cid}.{key}={expected} "
                                f"but that value is not in the anchored paragraph"))
    return out


def check_evidence_citations(cfg: Config, path: Path, text: str,
                             by_id: dict[str, dict]) -> list[Finding]:
    out: list[Finding] = []
    rel = _display(cfg, path)
    if rel in cfg.evidence_exclude:
        return out
    for n, line in enumerate(text.splitlines(), 1):
        ids = CLAIM_ID_RE.findall(line)
        if not ids:
            continue
        levels = [lv for lv in cfg.evidence_levels if lv in line]
        if not levels:
            continue
        for cid in set(ids):
            claim = by_id.get(cid)
            if claim is None:
                continue
            reg_level = claim.get("evidence_level")
            for lv in levels:
                if lv != reg_level:
                    out.append((f"evidence-level-drift:{rel}:{n}:{cid}",
                                f"{rel}:{n}: cites {cid} at evidence level '{lv}' "
                                f"but register says '{reg_level}'"))
    return out


def check_stale_strings(cfg: Config, path: Path, text: str) -> list[Finding]:
    out: list[Finding] = []
    rel = _display(cfg, path)
    if rel in cfg.stale_exclude:
        return out
    for n, line in enumerate(text.splitlines(), 1):
        for pattern, reason in cfg.stale_strings:
            if pattern in line:
                out.append((f"stale-string:{rel}:{pattern}",
                            f"{rel}:{n}: stale string {pattern!r} — {reason}"))
    return out


# --------------------------------------------------------------------------- #
# Runner
# --------------------------------------------------------------------------- #

def _load_baseline(cfg: Config) -> set[str]:
    p = cfg.path(cfg.baseline)
    if not p.exists():
        return set()
    data = json.loads(p.read_text(encoding="utf-8"))
    return {e["error_id"] for e in data.get("known_violations", [])}


def _doc_paths(cfg: Config) -> list[Path]:
    paths: list[Path] = []
    for pattern in cfg.doc_globs:
        paths.extend(sorted(cfg.root.glob(pattern)))
    # de-dup, files only
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        if p.is_file() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def run(cfg: Config, *, quiet: bool = False) -> int:
    """Run all checks. Returns 0 on success, 1 on a new (non-baselined) failure."""
    notes: list[str] = []
    findings: list[Finding] = []

    reg_path = cfg.path(cfg.register)
    if not reg_path.exists():
        print(f"[FAIL] missing claim register: {cfg.register}")
        return 1
    claims = load_register(reg_path.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in claims if "id" in c}
    if not claims and not quiet:
        print(f"[NOTE] {cfg.register}: no claims yet — add your first one "
              f"(see 'vericlaim init' output or the register spec).")

    findings += check_register(claims, cfg)
    findings += check_artifacts(claims, cfg)
    findings += check_manifest(cfg, notes)
    for doc in _doc_paths(cfg):
        text = doc.read_text(encoding="utf-8", errors="replace")
        findings += check_doc_anchors(cfg, doc, text, by_id)
        findings += check_evidence_citations(cfg, doc, text, by_id)
        findings += check_stale_strings(cfg, doc, text)

    baseline = _load_baseline(cfg)
    seen_ids = {eid for eid, _ in findings}
    new = [(e, m) for e, m in findings if e not in baseline]
    grandfathered = [(e, m) for e, m in findings if e in baseline]
    stale_baseline = sorted(baseline - seen_ids)

    if not quiet:
        for note in notes:
            print(f"[NOTE] {note}")
        for eid, msg in grandfathered:
            print(f"[WARN] (baselined) {msg}  [{eid}]")
        for eid in stale_baseline:
            print(f"[NOTE] baseline entry no longer occurs, remove it: {eid}")
    if new:
        print("Vericlaim gate FAILED:")
        for eid, msg in new:
            print(f" - {msg}  [{eid}]")
        return 1
    if not quiet:
        print(f"[OK] Vericlaim gate passed: {len(claims)} claims, "
              f"{len(grandfathered)} baselined, {len(stale_baseline)} stale baseline.")
    return 0
