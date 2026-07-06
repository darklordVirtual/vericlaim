# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-RSI-001: the self-improvement safety envelope refuses every
weakening change and accepts every non-weakening one.

Runs `check_non_weakening` over a fixed adversarial battery of (before, after)
snapshot pairs and records, deterministically, that every weakening pair is
REFUSED and every non-weakening pair is ACCEPTED. Writes claims/selfimprove_envelope.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from vericlaim.provenance import stamp  # noqa: E402
from vericlaim.selfimprove import Snapshot, check_non_weakening  # noqa: E402

ART = Path(__file__).resolve().parents[1] / "claims" / "selfimprove_envelope.json"

_CORE = {"vericlaim/gate.py": "aaa", "vericlaim/pathsafe.py": "bbb"}


def _snap(levels, tests, baseline, core, gate_ok=True) -> Snapshot:
    return Snapshot(dict(levels), tests, baseline, dict(core), gate_ok)


# The trusted baseline every candidate is compared against.
BASE = _snap({"C-1": 3, "C-2": 1}, tests=250, baseline=0, core=_CORE, gate_ok=True)

# Each case: (name, candidate, must_be_refused)
WEAKENINGS = [
    ("remove_claim", _snap({"C-1": 3}, 250, 0, _CORE), True),
    ("demote_evidence", _snap({"C-1": 2, "C-2": 1}, 250, 0, _CORE), True),
    ("reduce_tests", _snap({"C-1": 3, "C-2": 1}, 249, 0, _CORE), True),
    ("grow_baseline", _snap({"C-1": 3, "C-2": 1}, 250, 1, _CORE), True),
    ("edit_gate_core", _snap({"C-1": 3, "C-2": 1}, 250, 0, {**_CORE, "vericlaim/gate.py": "HACKED"}), True),
    ("red_gate", _snap({"C-1": 3, "C-2": 1}, 250, 0, _CORE, gate_ok=False), True),
]
NON_WEAKENINGS = [
    ("identity", _snap({"C-1": 3, "C-2": 1}, 250, 0, _CORE), False),
    ("promote_evidence", _snap({"C-1": 4, "C-2": 1}, 250, 0, _CORE), False),
    ("add_claim", _snap({"C-1": 3, "C-2": 1, "C-3": 2}, 250, 0, _CORE), False),
    ("more_tests", _snap({"C-1": 3, "C-2": 1}, 260, 0, _CORE), False),
    ("shrink_baseline", _snap({"C-1": 3, "C-2": 1}, 250, 0, _CORE), False),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", default=None,
                    help="write the artifact here (basename) instead of the "
                         "committed path — used by declarative `vericlaim reproduce`")
    args = ap.parse_args()
    cases = WEAKENINGS + NON_WEAKENINGS
    weakenings_refused = 0
    non_weakenings_accepted = 0
    misclassifications = 0
    for _name, cand, must_refuse in cases:
        refused = bool(check_non_weakening(BASE, cand))
        if refused != must_refuse:
            misclassifications += 1
        elif must_refuse:
            weakenings_refused += 1
        else:
            non_weakenings_accepted += 1

    artifact = {
        "schema": "selfimprove_envelope_v1",
        "total_cases": len(cases),
        "weakenings_refused": weakenings_refused,
        "non_weakenings_accepted": non_weakenings_accepted,
        "misclassifications": misclassifications,
    }
    text = json.dumps(artifact, indent=2) + "\n"
    if args.output_dir:
        # Reproduce mode: emit into the isolated output dir; the committed sidecar
        # remains authoritative, so we don't stamp here.
        out = Path(args.output_dir) / ART.name
        out.write_text(text, encoding="utf-8")
    else:
        ART.write_text(text, encoding="utf-8")
        stamp(ART, script="python3 tools/selfimprove_evidence.py")
        out = ART
    print(f"[OK] wrote {out}")
    for k, v in artifact.items():
        if k != "schema":
            print(f"     {k}={v}")
    return 0 if misclassifications == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
