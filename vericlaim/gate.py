# SPDX-License-Identifier: Apache-2.0
"""The vericlaim gate — Claim-Oriented Programming enforcement.

The gate is the executable contract for a project's *claims about itself*.
It reads files only (no side effects) and fails the build when any of the
following drift:

1. REGISTER INTEGRITY   — required fields, valid evidence level, no duplicate
                          ids. The register parses FAIL-CLOSED: a misparse
                          raises rather than silently seeing zero claims.
2. ARTIFACT EXISTENCE   — every cited artifact exists ("no claim without an
                          artifact").
3. PATH CONTAINMENT     — artifacts live inside the repo (no absolute paths,
                          ``..``, or symlink escapes); optionally git-tracked.
4. PROVENANCE           — when required, each produced artifact carries a
                          sidecar recording how it was made.
5. MANIFEST HASHES      — every SHA-256 in the manifest matches the file bytes
                          (LF-normalized; CRLF working trees pass with a note).
6. DOC BINDING          — claim anchors ``<!-- claim:ID field ... -->`` assert
                          that the register's value appears in the following
                          paragraph, so numbers cannot drift from the register.
                          Source files under ``code_globs`` are bound the same
                          way via comment anchors (``# claim:ID field``), whose
                          values must appear in the following comment block.
7. EVIDENCE CITATIONS   — a doc line naming a registered claim id together with
                          an evidence-level term must agree with the register.
8. STALE STRINGS        — a configurable denylist of corrected strings that
                          must never reappear.
9. LITERATURE           — hash-verified external sources: each ``literature:``
                          entry carries the SHA-256 of the cited document, and
                          a committed copy must still hash to it. Proves the
                          citation is intact, never that the source is right —
                          and never substitutes for a reproducible artifact.

Known violations are grandfathered in the baseline file (reported as WARN);
anything new fails with a non-zero exit. This lets a project adopt the gate
incrementally without a big-bang cleanup. The heavier reproduce-as-oracle check
(which executes commands) is the separate ``vericlaim reproduce``.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .config import Config
from .register import RegisterError, load_register

ANCHOR_RE = re.compile(r"<!--\s*claim:([A-Za-z0-9_.-]+)((?:\s+[A-Za-z0-9_.-]+)+)\s*-->")
# A source-comment line: leader, then content. `*` covers C-block continuation
# lines; `;` covers Lisp/asm/ini, `--` SQL/Haskell/Lua, `%` TeX/Prolog/Erlang.
CODE_COMMENT_RE = re.compile(r"^\s*(?:#|//|--|;+|%+|\*)\s?(.*)$")
# A code anchor is a comment whose ENTIRE content is `claim:ID field...` —
# prose mentioning a claim id mid-sentence is a citation, not an anchor.
CODE_ANCHOR_RE = re.compile(r"^claim:([A-Za-z0-9_.-]+)((?:\s+[A-Za-z0-9_.-]+)+)\s*$")
MANIFEST_ROW_RE = re.compile(
    r"^\|\s*`(?P<path>[^`]+)`\s*\|\s*`(?P<sha>[0-9a-fA-F]{64})`\s*\|"
)
NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")

Finding = tuple[str, str]  # (error_id, human message)


def _compile_id_matcher(by_id: dict[str, dict]) -> re.Pattern | None:
    """Compile ONE regex that matches any registered id as a whole token.

    Building a single alternation and compiling it once — instead of one
    ``re.search`` per id per line — keeps the evidence check linear in the doc
    size rather than O(lines x claims), and avoids thrashing the interpreter's
    regex cache (which holds only 512 distinct patterns) once a register grows
    past a few hundred claims. Longest ids first so the alternation prefers the
    fuller match; the boundary lookarounds match the source of truth exactly,
    never a truncated tail. Returns None for an empty register.
    """
    if not by_id:
        return None
    alt = "|".join(re.escape(cid) for cid in sorted(by_id, key=len, reverse=True))
    return re.compile(rf"(?<![A-Za-z0-9_.-])(?:{alt})(?![A-Za-z0-9_.-])")


def _claim_ids_in_line(line: str, by_id: dict[str, dict]) -> set[str]:
    """Return the registered claim ids that appear in *line*, matched whole.

    Uses the register as the source of truth rather than guessing an id shape
    with a regex — so CLAIM-EX-001, CLAIM-CORE-001, ORG.PRODUCT-2026-001 all
    match in full, not as a truncated tail. For hot paths compile the matcher
    once with `_compile_id_matcher` and reuse it; this helper is the convenience
    form used in tests.
    """
    matcher = _compile_id_matcher(by_id)
    if matcher is None:
        return set()
    return {m.group(0) for m in matcher.finditer(line)}


def _resolve_within_root(cfg: Config, rel: str) -> Path | None:
    """Resolve *rel* under the repo root, or None if it escapes the root.

    Blocks absolute paths, ``..`` traversal, and symlinks that point outside the
    repository — so "committed artifact" cannot quietly mean a file in another
    project or outside the checkout.
    """
    root = cfg.root.resolve()
    candidate = (cfg.root / rel).resolve()
    if candidate == root:
        return None
    if root not in candidate.parents:
        return None
    return candidate


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
            resolved = _resolve_within_root(cfg, rel)
            if resolved is None:
                out.append((f"artifact-escapes-root:{cid}:{rel}",
                            f"{cid}: artifact path {rel!r} is absolute or escapes "
                            f"the repository root — evidence must live inside the repo"))
                continue
            if not resolved.exists():
                out.append((f"artifact-missing:{cid}:{rel}",
                            f"{cid}: cited artifact does not exist: {rel}"))
                continue
            if cfg.require_git_tracked and not _is_git_tracked(cfg, rel):
                out.append((f"artifact-untracked:{cid}:{rel}",
                            f"{cid}: artifact {rel} is not tracked by git — "
                            f"a 'committed artifact' must be committed"))
    return out


def _is_git_tracked(cfg: Config, rel: str) -> bool:
    try:
        import subprocess
        subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel],
                       cwd=cfg.root, check=True, capture_output=True)
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def check_provenance(claims: list[dict], cfg: Config) -> list[Finding]:
    """When require_provenance is on, every artifact must carry a provenance
    sidecar recording how it was produced (script + commit)."""
    out: list[Finding] = []
    if not cfg.require_provenance:
        return out
    from .provenance import load as load_provenance

    for c in claims:
        cid = c.get("id", "<missing-id>")
        # Provenance applies to *produced* evidence — artifacts a script
        # regenerates. A claim backed by static source files (no `reproduce`
        # command) is a structural fact, not a produced number, and is exempt.
        if not c.get("reproduce"):
            continue
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        for rel in arts:
            art = cfg.path(rel)
            if not art.exists():
                continue  # artifact-existence check already reports this
            prov = load_provenance(art)
            if prov is None:
                out.append((f"provenance-missing:{cid}:{rel}",
                            f"{cid}: artifact {rel} has no provenance sidecar "
                            f"({rel}.provenance.json) — record how it was produced"))
            elif not prov.get("script"):
                # `script` (how it was produced) is essential. `git_commit` is
                # best-effort — it is null when produced outside a git checkout.
                out.append((f"provenance-incomplete:{cid}:{rel}",
                            f"{cid}: provenance for {rel} is missing 'script'"))
    return out


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def check_literature(claims: list[dict], cfg: Config) -> list[Finding]:
    """Hash-verified external sources on a claim (`literature:` entries).

    Each entry needs a `source` (DOI/URL/citation) and the `sha256` of the
    cited document; an optional `file` points at a committed copy or extract,
    which must then exist inside the repo and hash to `sha256`. This proves
    the citation is intact — the cited document is the one registered — never
    that the document is correct. Literature SUPPLEMENTS evidence: `artifact`
    remains required and `reproduce` remains the only path to a reproducible
    number.
    """
    out: list[Finding] = []
    for c in claims:
        cid = c.get("id", "<missing-id>")
        lit = c.get("literature")
        if lit is None:
            continue
        if isinstance(lit, dict):
            lit = [lit]  # a single un-listed entry is fine; normalize
        if not isinstance(lit, list):
            out.append((f"literature-not-a-list:{cid}",
                        f"{cid}: 'literature' must be a list of entries"))
            continue
        for i, entry in enumerate(lit):
            if not isinstance(entry, dict):
                out.append((f"literature-not-a-map:{cid}:{i}",
                            f"{cid}: literature[{i}] must be a map with "
                            f"'source' and 'sha256'"))
                continue
            for f in ("source", "sha256"):
                if not entry.get(f):
                    out.append((f"literature-missing-field:{cid}:{i}:{f}",
                                f"{cid}: literature[{i}] is missing '{f}'"))
            sha = entry.get("sha256")
            sha_ok = bool(sha) and bool(_SHA256_HEX_RE.match(str(sha)))
            if sha and not sha_ok:
                out.append((f"literature-bad-sha256:{cid}:{i}",
                            f"{cid}: literature[{i}] sha256 must be 64 "
                            f"lowercase hex chars"))
            rel = entry.get("file")
            if not rel:
                continue
            resolved = _resolve_within_root(cfg, rel)
            if resolved is None:
                out.append((f"literature-escapes-root:{cid}:{rel}",
                            f"{cid}: literature file {rel!r} is absolute or "
                            f"escapes the repository root"))
                continue
            if not resolved.exists():
                out.append((f"literature-file-missing:{cid}:{rel}",
                            f"{cid}: literature file does not exist: {rel}"))
                continue
            if cfg.require_git_tracked and not _is_git_tracked(cfg, rel):
                out.append((f"literature-untracked:{cid}:{rel}",
                            f"{cid}: literature file {rel} is not tracked by git"))
            if sha_ok:
                data = resolved.read_bytes()
                expected = str(sha)
                if (_sha256(data) != expected
                        and _sha256(data.replace(b"\r\n", b"\n")) != expected):
                    out.append((f"literature-hash-mismatch:{cid}:{rel}",
                                f"{cid}: literature file {rel} does not hash to "
                                f"its registered sha256 — the cited document "
                                f"changed after registration"))
    return out


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


def _check_anchor_fields(rel: str, lineno: int, cid: str, blob: str,
                         claim: dict, paragraph: str) -> list[Finding]:
    """The binding rule, shared by doc and code anchors: every field named in
    the anchor must appear as that exact number in the bound paragraph."""
    out: list[Finding] = []
    found = {float(t) for t in NUMBER_RE.findall(paragraph)}
    metrics = claim.get("metrics") or {}
    for key in blob.split():
        expected = claim.get("n") if key == "n" else (
            metrics.get(key) if isinstance(metrics, dict) else None)
        if expected is None:
            out.append((f"anchor-unknown-metric:{rel}:{cid}:{key}",
                        f"{rel}:{lineno}: anchor metric '{key}' not defined "
                        f"in register for {cid}"))
            continue
        if float(expected) not in found:
            out.append((f"anchor-value-drift:{rel}:{cid}:{key}",
                        f"{rel}:{lineno}: register says {cid}.{key}={expected} "
                        f"but that value is not in the anchored paragraph"))
    return out


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
            out += _check_anchor_fields(rel, idx + 1, cid, blob, claim, paragraph)
    return out


def _comment_content(line: str) -> str | None:
    """The content of a source-comment line, or None for a non-comment line."""
    m = CODE_COMMENT_RE.match(line)
    return m.group(1) if m else None


def _comment_paragraph_after(lines: list[str], idx: int) -> str:
    """The contiguous comment block after *idx* — and ONLY the comment block.

    Binding stops at the first non-comment or empty-comment line, so a number
    sitting in code (`RATIO = 2.5`) can never satisfy a claim binding: the
    claim text itself must carry the value, exactly as in markdown prose.
    An empty comment (`#`) is the code analogue of a blank line.
    """
    block: list[str] = []
    for line in lines[idx + 1:]:
        content = _comment_content(line)
        if content is None or not content.strip():
            break
        block.append(content)
    return " ".join(block)


def check_code_anchors(cfg: Config, path: Path, text: str,
                       by_id: dict[str, dict]) -> list[Finding]:
    """Claim anchors in source comments: `# claim:ID field` (or //, --, ;, %, *).

    Code states facts about itself — complexity, capability counts, invariants —
    and those drift exactly like doc prose. The anchor line must contain only
    the anchor; the assertion lives in the comment block that follows.
    """
    out: list[Finding] = []
    rel = _display(cfg, path)
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        content = _comment_content(line)
        if content is None:
            continue
        m = CODE_ANCHOR_RE.match(content.strip())
        if not m:
            continue
        cid, blob = m.group(1), m.group(2)
        claim = by_id.get(cid)
        if claim is None:
            out.append((f"anchor-unknown-claim:{rel}:{cid}",
                        f"{rel}:{idx+1}: anchor cites unknown claim {cid}"))
            continue
        paragraph = _comment_paragraph_after(lines, idx)
        out += _check_anchor_fields(rel, idx + 1, cid, blob, claim, paragraph)
    return out


def check_evidence_citations(cfg: Config, path: Path, text: str,
                             by_id: dict[str, dict]) -> list[Finding]:
    out: list[Finding] = []
    rel = _display(cfg, path)
    if rel in cfg.evidence_exclude:
        return out
    matcher = _compile_id_matcher(by_id)  # compile once, reuse across all lines
    if matcher is None:
        return out
    for n, line in enumerate(text.splitlines(), 1):
        # An evidence-level drift needs BOTH a level word and a claim id on the
        # line. The level-word test is a cheap substring scan, so do it first
        # and only run the id regex on the few lines that could drift.
        levels = [lv for lv in cfg.evidence_levels if lv in line]
        if not levels:
            continue
        # Match KNOWN claim ids from the register, not a regex guess — a
        # multi-segment id like CLAIM-EX-001 must match in full, not as EX-001.
        ids = {m.group(0) for m in matcher.finditer(line)}
        if not ids:
            continue
        for cid in ids:
            claim = by_id[cid]
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
    """Load grandfathered violation ids, fail-closed.

    A malformed baseline must not crash the gate or be read as "no baseline" —
    either would silently change what the gate enforces. On any structural
    problem we raise RegisterError so the runner reports a clean [FAIL].
    """
    p = cfg.path(cfg.baseline)
    if not p.exists():
        return set()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RegisterError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise RegisterError("top level must be an object")
    entries = data.get("known_violations", [])
    if not isinstance(entries, list):
        raise RegisterError("'known_violations' must be a list")
    ids: set[str] = set()
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or "error_id" not in e:
            raise RegisterError(
                f"known_violations[{i}] must be an object with an 'error_id' "
                f"field (got {type(e).__name__})")
        ids.add(e["error_id"])
    return ids


def _glob_paths(cfg: Config, globs: tuple[str, ...]) -> list[Path]:
    paths: list[Path] = []
    for pattern in globs:
        paths.extend(sorted(cfg.root.glob(pattern)))
    # de-dup, files only
    seen: set[Path] = set()
    out: list[Path] = []
    for p in paths:
        if p.is_file() and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _doc_paths(cfg: Config) -> list[Path]:
    return _glob_paths(cfg, cfg.doc_globs)


def run(cfg: Config, *, quiet: bool = False) -> int:
    """Run all checks. Returns 0 on success, 1 on a new (non-baselined) failure."""
    notes: list[str] = []
    findings: list[Finding] = []

    reg_path = cfg.path(cfg.register)
    if not reg_path.exists():
        print(f"[FAIL] missing claim register: {cfg.register}")
        return 1
    try:
        claims = load_register(reg_path.read_text(encoding="utf-8"))
    except RegisterError as exc:
        print(f"[FAIL] {cfg.register}: {exc}")
        return 1
    by_id = {c["id"]: c for c in claims if "id" in c}
    if not claims and not quiet:
        print(f"[NOTE] {cfg.register}: no claims yet — add your first one "
              f"(see 'vericlaim init' output or the register spec).")

    findings += check_register(claims, cfg)
    findings += check_artifacts(claims, cfg)
    findings += check_provenance(claims, cfg)
    findings += check_literature(claims, cfg)
    findings += check_manifest(cfg, notes)
    docs = _doc_paths(cfg)
    for doc in docs:
        text = doc.read_text(encoding="utf-8", errors="replace")
        findings += check_doc_anchors(cfg, doc, text, by_id)
        findings += check_evidence_citations(cfg, doc, text, by_id)
        findings += check_stale_strings(cfg, doc, text)
    doc_set = set(docs)
    for src in _glob_paths(cfg, cfg.code_globs):
        if src in doc_set:
            continue  # already checked with doc semantics
        text = src.read_text(encoding="utf-8", errors="replace")
        findings += check_code_anchors(cfg, src, text, by_id)
        findings += check_evidence_citations(cfg, src, text, by_id)
        findings += check_stale_strings(cfg, src, text)

    try:
        baseline = _load_baseline(cfg)
    except RegisterError as exc:
        print(f"[FAIL] {cfg.baseline}: {exc}")
        return 1
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
