# SPDX-License-Identifier: Apache-2.0
"""Command-line entry point for vericlaim.

    vericlaim                 run the gate (default)
    vericlaim init            scaffold config + register + baseline into a project
    vericlaim --root DIR ...  operate on another directory
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .gate import run
from .newclaim import add_parser as add_newclaim_parser
from .newclaim import run as run_newclaim
from .reproduce import reproduce
from .scaffold import init


def main(argv: list[str] | None = None) -> int:
    # Common flags live on a parent parser so they are accepted both before AND
    # after the subcommand (e.g. `vericlaim reproduce --profile strict`).
    # default=SUPPRESS is load-bearing: because this parser is a parent of BOTH
    # the top-level parser and every subparser, a real default here would let the
    # subparser's copy CLOBBER a value parsed before the subcommand
    # (`vericlaim --root X init` would silently reset root to cwd). With SUPPRESS
    # the subparser leaves the attribute unset when the flag is absent, so the
    # top-level value survives; defaults are applied once, after parsing.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", type=Path, default=argparse.SUPPRESS,
                        help="project root (default: current directory)")
    common.add_argument("--config", type=Path, default=argparse.SUPPRESS,
                        help="path to vericlaim.toml (default: <root>/vericlaim.toml)")
    common.add_argument("--quiet", action="store_true", default=argparse.SUPPRESS,
                        help="only print on failure")
    common.add_argument("--profile", choices=("adopt", "strict", "enterprise"),
                        default=argparse.SUPPRESS,
                        help="policy profile override (adopt|strict|enterprise); "
                             "strict is the recommended secure-by-default destination")

    parser = argparse.ArgumentParser(
        prog="vericlaim", parents=[common],
        description="Claim-Oriented Programming gate: verify a project's claims "
                    "against its committed artifacts and keep docs from drifting.",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", parents=[common],
                   help="scaffold Claim-Oriented Programming into this project")
    add_newclaim_parser(sub, [common])
    sub.add_parser("check", parents=[common],
                   help="run the gate (default when no command is given)")
    sub.add_parser("reproduce", parents=[common],
                   help="re-run each claim's reproduction and verify it still holds")
    sub.add_parser("improve", parents=[common],
                   help="PROPOSE-ONLY: audit this repo's own claims and print honest, "
                        "non-weakening improvement suggestions (never edits anything)")
    args = parser.parse_args(argv)

    # SUPPRESS means absent flags leave no attribute; apply defaults once here so
    # a flag given before OR after the subcommand wins and neither clobbers.
    root = getattr(args, "root", Path.cwd()).resolve()
    config = getattr(args, "config", None)
    quiet = getattr(args, "quiet", False)
    profile = getattr(args, "profile", None)
    if args.command == "init":
        return init(root)
    if args.command == "new-claim":
        args.root = root
        return run_newclaim(args)
    try:
        cfg = load_config(root, config, profile_override=profile)
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 1
    if args.command == "reproduce":
        return reproduce(cfg, quiet=quiet)
    if args.command == "improve":
        return _improve(cfg)
    if not quiet:
        print(f"[profile] {cfg.profile}"
              + ("" if cfg.strict_mode else " (permissive onboarding profile; "
                 "'strict' is the recommended destination)"))
    return run(cfg, quiet=quiet)


def _improve(cfg) -> int:
    """Propose-only self-improvement: audit our own claims, suggest honest,
    non-weakening improvements, and STOP. It edits nothing, commits nothing.
    A human decides what to act on. This is the defensible boundary — see
    docs/architecture/self-improvement.md."""
    from .selfimprove import propose, stopped
    if stopped(cfg):
        print("[HALT] self-improvement kill-switch present "
              "(claims/STOP_SELF_IMPROVEMENT) — refusing to run.")
        return 0
    suggestions = propose(cfg)
    print("vericlaim improve — PROPOSE-ONLY (no files changed, nothing committed)")
    if not suggestions:
        print("[OK] no improvements proposed; the register looks well-formed.")
        return 0
    print(f"[NOTE] {len(suggestions)} honest, non-weakening suggestion(s):")
    for s in suggestions:
        print(f"  - {s.claim_id} [{s.kind}]: {s.detail}")
    print("\nThese are proposals only. Produce real evidence and apply changes "
          "yourself; the gate and the non-weakening envelope guard any change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
