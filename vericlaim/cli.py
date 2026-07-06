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
from .reproduce import reproduce
from .scaffold import init


def main(argv: list[str] | None = None) -> int:
    # Common flags live on a parent parser so they are accepted both before AND
    # after the subcommand (e.g. `vericlaim reproduce --profile strict`).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", type=Path, default=Path.cwd(),
                        help="project root (default: current directory)")
    common.add_argument("--config", type=Path, default=None,
                        help="path to vericlaim.toml (default: <root>/vericlaim.toml)")
    common.add_argument("--quiet", action="store_true", help="only print on failure")
    common.add_argument("--profile", choices=("adopt", "strict", "enterprise"),
                        default=None,
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
    sub.add_parser("check", parents=[common],
                   help="run the gate (default when no command is given)")
    sub.add_parser("reproduce", parents=[common],
                   help="re-run each claim's reproduction and verify it still holds")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if args.command == "init":
        return init(root)
    try:
        cfg = load_config(root, args.config, profile_override=args.profile)
    except ValueError as exc:
        print(f"[FAIL] {exc}")
        return 1
    if args.command == "reproduce":
        return reproduce(cfg, quiet=args.quiet)
    if not args.quiet:
        print(f"[profile] {cfg.profile}"
              + ("" if cfg.strict_mode else " (permissive onboarding profile; "
                 "'strict' is the recommended destination)"))
    return run(cfg, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
