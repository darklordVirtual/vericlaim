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
    parser = argparse.ArgumentParser(
        prog="vericlaim",
        description="Claim-Oriented Programming gate: verify a project's claims "
                    "against its committed artifacts and keep docs from drifting.",
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="project root (default: current directory)")
    parser.add_argument("--config", type=Path, default=None,
                        help="path to vericlaim.toml (default: <root>/vericlaim.toml)")
    parser.add_argument("--quiet", action="store_true", help="only print on failure")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("init", help="scaffold Claim-Oriented Programming into this project")
    sub.add_parser("check", help="run the gate (default when no command is given)")
    sub.add_parser("reproduce",
                   help="re-run each claim's reproduce command and verify the "
                        "artifact is unchanged (executes shell commands)")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    if args.command == "init":
        return init(root)
    cfg = load_config(root, args.config)
    if args.command == "reproduce":
        return reproduce(cfg, quiet=args.quiet)
    return run(cfg, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
