# SPDX-License-Identifier: Apache-2.0
"""Produce the evidence artifact for the theorem example.

Deterministic: the artifact is the checker's verdict on the committed proof
object, so the claim "p -> p is machine-checked" is regenerated from the
derivation itself — never asserted by hand.

    python3 examples/theorem/evidence.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for `import vericlaim`
from vericlaim.evidence import emit, output_dir_arg  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from proofcheck import check_file  # noqa: E402


def main() -> int:
    here = Path(__file__).resolve().parent
    proof = here / "proofs" / "p_implies_p.json"
    report = check_file(proof)  # raises ProofError -> no artifact on failure
    artifact = {
        "schema": "theorem_v1",
        "proof": "examples/theorem/proofs/p_implies_p.json",
        "system": "Lukasiewicz A1-A3 + modus ponens",
        **report,
    }
    out = here / "artifacts" / "theorem.json"
    out.parent.mkdir(exist_ok=True)
    emit(json.dumps(artifact, indent=2) + "\n", out,
         script="python3 examples/theorem/evidence.py",
         output_dir=output_dir_arg())
    print(f"[OK] wrote {out}")
    print(f"     steps_verified={report['steps_verified']} qed={report['qed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
