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


def _sha256(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def reproduce(cfg: Config, *, quiet: bool = False) -> int:
    """Run every claim's reproduce command; fail if any artifact changed."""
    reg = cfg.path(cfg.register)
    if not reg.exists():
        print(f"[FAIL] missing claim register: {cfg.register}")
        return 1
    try:
        claims = load_register(reg.read_text(encoding="utf-8"))
    except RegisterError as exc:
        print(f"[FAIL] {cfg.register}: {exc}")
        return 1

    # Group artifacts by their reproduce command (skip claims without one).
    by_cmd: dict[str, list[str]] = {}
    for c in claims:
        cmd = c.get("reproduce")
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        if isinstance(cmd, str) and cmd.strip() and arts:
            by_cmd.setdefault(cmd.strip(), [])
            for a in arts:
                if a not in by_cmd[cmd.strip()]:
                    by_cmd[cmd.strip()].append(a)

    if not by_cmd:
        if not quiet:
            print("[NOTE] no claims have a `reproduce` command with artifacts.")
        return 0

    failures: list[str] = []
    for cmd, arts in by_cmd.items():
        before = {a: _sha256(cfg.path(a)) for a in arts}
        if not quiet:
            print(f"[run] {cmd}")
        try:
            r = subprocess.run(cmd, shell=True, cwd=cfg.root,
                               capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{cmd!r} did not run ({type(exc).__name__}: {exc})")
            continue
        if r.returncode != 0:
            failures.append(f"{cmd!r} exited {r.returncode}: "
                            f"{(r.stderr or r.stdout).strip()[:200]}")
            continue
        for a in arts:
            after = _sha256(cfg.path(a))
            if before[a] is None:
                failures.append(f"{a}: not produced by `{cmd}`")
            elif after != before[a]:
                failures.append(
                    f"{a}: changed after re-running `{cmd}` — the committed "
                    f"artifact is stale or the script is non-deterministic. "
                    f"Commit the regenerated artifact (and update docs the gate flags).")

    if failures:
        print("Reproduce FAILED:")
        for f in failures:
            print(f" - {f}")
        return 1
    if not quiet:
        print(f"[OK] reproduce: {len(by_cmd)} command(s) re-run, "
              f"all artifacts byte-identical — every registered number still holds.")
    return 0
