# SPDX-License-Identifier: Apache-2.0
"""`vericlaim reproduce` — re-run each claim's evidence and prove it still holds.

The gate checks that an artifact *exists* and matches its manifest hash. This
goes further: it runs each claim's `reproduce` command and checks the artifact
is byte-identical afterwards. If it changed, either the committed artifact was
stale (the code moved on and the number is now wrong) or the script is
non-deterministic — both are failures you want CI to catch.

This is Eiffel's "contract as oracle" idea: the reproduce command is the oracle,
run continuously, so a registered number is not just present but *still true
today*.

SECURITY: this executes the shell commands in your register's `reproduce`
fields — the same trust level as running your own test suite. The default gate
(`vericlaim`) never executes anything; only this subcommand does.
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from .config import Config
from .register import RegisterError, load_register
from .repro import ReproError, ReproSpec, run_declarative


def _sha256(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def _run_legacy(cfg: Config, cmd: str, arts: list[str], failures: list[str],
                *, quiet: bool) -> None:
    """The legacy byte-compare path (adopt only): run the shell string in the
    repo and check the artifact is unchanged. WEAKER than declarative — a no-op
    passes because the old artifact is still there. Documented as such."""
    before = {a: _sha256(cfg.path(a)) for a in arts}
    if not quiet:
        print(f"[run:legacy] {cmd}")
    try:
        r = subprocess.run(cmd, shell=True, cwd=cfg.root,  # noqa: S602 (adopt-only, trusted register)
                           capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        failures.append(f"{cmd!r} did not run ({type(exc).__name__}: {exc})")
        return
    if r.returncode != 0:
        failures.append(f"{cmd!r} exited {r.returncode}: {(r.stderr or r.stdout).strip()[:200]}")
        return
    for a in arts:
        after = _sha256(cfg.path(a))
        if before[a] is None:
            failures.append(f"{a}: not produced by `{cmd}`")
        elif after != before[a]:
            failures.append(f"{a}: changed after re-running `{cmd}` — stale artifact "
                            f"or non-deterministic script.")


def reproduce(cfg: Config, *, quiet: bool = False) -> int:
    """Re-run each claim's reproduction and fail if any does not hold.

    Declarative specs run in an isolated output dir (from-scratch or fail);
    legacy string commands use the weaker byte-compare path and are allowed only
    under the adopt profile with allow_legacy_shell. strict/enterprise reject
    legacy commands outright."""
    reg = cfg.path(cfg.register)
    if not reg.exists():
        print(f"[FAIL] missing claim register: {cfg.register}")
        return 1
    try:
        claims = load_register(reg.read_text(encoding="utf-8"))
    except RegisterError as exc:
        print(f"[FAIL] {cfg.register}: {exc}")
        return 1

    failures: list[str] = []
    n_declarative = n_legacy = 0
    legacy_by_cmd: dict[str, list[str]] = {}

    for c in claims:
        # Declarative form (parser-friendly flat fields the zero-dep parser can
        # express): reproduce_argv + reproduce_outputs. Falls back to the legacy
        # `reproduce` string when absent.
        argv = c.get("reproduce_argv")
        if argv is not None:
            raw: object = {"argv": argv, "outputs": c.get("reproduce_outputs") or []}
            if c.get("reproduce_timeout"):
                raw["timeout_seconds"] = c["reproduce_timeout"]  # type: ignore[index]
        else:
            raw = c.get("reproduce")
            if raw is None:
                continue
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        try:
            spec = ReproSpec.parse(raw, allow_legacy_shell=cfg.legacy_shell_allowed)
        except ReproError as exc:
            failures.append(f"{c.get('id', '?')}: {exc}")
            continue
        if spec.is_legacy:
            # Group identical legacy commands so a shared producer runs once.
            legacy_by_cmd.setdefault(spec.legacy_shell, [])
            for a in arts:
                if a not in legacy_by_cmd[spec.legacy_shell]:
                    legacy_by_cmd[spec.legacy_shell].append(a)
            continue
        n_declarative += 1
        if not quiet:
            print(f"[run] {' '.join(spec.argv)}")
        res = run_declarative(cfg, spec)
        if not res.ok:
            failures.append(f"{c.get('id', '?')}: {res.reason}")

    for cmd, arts in legacy_by_cmd.items():
        n_legacy += 1
        _run_legacy(cfg, cmd, arts, failures, quiet=quiet)

    if failures:
        print("Reproduce FAILED:")
        for f in failures:
            print(f" - {f}")
        return 1
    total = n_declarative + n_legacy
    if total == 0:
        if not quiet:
            print("[NOTE] no claims have a `reproduce` spec.")
        return 0
    if not quiet:
        legacy_note = f" ({n_legacy} legacy, weaker)" if n_legacy else ""
        print(f"[OK] reproduce: {total} spec(s) re-run{legacy_note}, "
              f"every registered number still holds.")
    return 0
