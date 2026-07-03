# SPDX-License-Identifier: Apache-2.0
"""Command-line entry point for the vericlaim gate.

Usage:
    python -m vericlaim [--root DIR] [--config FILE] [--quiet]
    vericlaim ...            (if installed as a console script)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .gate import run


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
    parser.add_argument("--quiet", action="store_true",
                        help="only print on failure")
    args = parser.parse_args(argv)

    cfg = load_config(args.root.resolve(), args.config)
    return run(cfg, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
