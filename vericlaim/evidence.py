# SPDX-License-Identifier: Apache-2.0
"""The evidence-script side of declarative reproduction.

A declarative ``reproduce_argv`` spec hands the script an isolated, empty
directory and byte-compares what it creates against the committed artifact. A
no-op cannot pass, because there is no stale file to fall back on — which is
the whole reason the declarative form is the only one ``strict`` accepts.

Every evidence script therefore needs the same two-mode ending: write into
``--output-dir`` when reproducing, or write the committed artifact and stamp
its provenance when producing. Repeating that by hand in a dozen scripts is how
the two modes drift apart, so it lives here once.

    from vericlaim.evidence import emit, output_dir_arg

    def main() -> int:
        payload = ...
        emit(json.dumps(payload, indent=2) + "\\n", ARTIFACT,
             script="python3 tools/x_evidence.py", output_dir=output_dir_arg())

``emit`` always writes with ``newline="\\n"``. Byte-comparison is the contract,
and on a CRLF platform the default translation would rewrite every line ending
and fail a reproduction that is in fact correct.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .provenance import stamp


def output_dir_arg(argv: list[str] | None = None) -> str | None:
    """Parse ``--output-dir`` from the command line, tolerating other flags."""
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--output-dir", default=None)
    known, _ = ap.parse_known_args(argv)
    return known.output_dir


def emit(text: str, artifact: str | Path, *, script: str,
         output_dir: str | None) -> Path:
    """Write *text* as the artifact, in whichever of the two modes applies.

    Reproduction mode (``output_dir`` given) writes only into that directory
    and never stamps: provenance describes the committed run, and re-stamping
    during a verification would let the check rewrite the thing it checks.
    """
    art = Path(artifact)
    if output_dir:
        out = Path(output_dir) / art.name
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="\n")
        return out
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_text(text, encoding="utf-8", newline="\n")
    stamp(art, script=script)
    return art
