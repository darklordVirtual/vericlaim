# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SLSA-001 — the encoded Build track matches the
published SLSA v1.1 specification and level assessment is cumulative and
fail-closed, enumerated exhaustively.

Oracles, none the module's own output: (1) the published v1.1 Build-track
shape, verified against the spec's own source markdown (slsa.dev/spec/v1.1
and the releases/v1.1 branch): four levels with the published names
("Build L0: No guarantees" .. "Build L3: Hardened builds"), the published
one-line requirements and focus rows, and cumulativeness ("All of [Build
L1], plus:" — each level includes the one below); (2) EXHAUSTIVE
assessment: all 16 subsets of the four capability flags are enumerated and
each must yield exactly the level whose full requirement chain is met — in
particular, every subset containing a gap below a declared capability caps
at the gap (hardened_platform without signed_provenance is L1, not L3).
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from slsa_levels import CAPABILITIES, LEVELS, SLSAError, assess  # noqa: E402
from _util import emit  # noqa: E402


def expected_level(have: set) -> int:
    """Independent re-derivation of the cumulative rule."""
    chain = [{"provenance_exists"},
             {"provenance_exists", "hosted_platform", "signed_provenance"},
             {"provenance_exists", "hosted_platform", "signed_provenance",
              "hardened_platform"}]
    level = 0
    for n, needs in enumerate(chain, start=1):
        if needs <= have:
            level = n
        else:
            break
    return level


def run() -> dict:
    taxonomy = [
        len(LEVELS) == 4 and sorted(LEVELS) == [0, 1, 2, 3],
        LEVELS[0]["name"] == "Build L0: No guarantees",
        LEVELS[1]["name"] == "Build L1: Provenance exists",
        LEVELS[2]["name"] == "Build L2: Hosted build platform",
        LEVELS[3]["name"] == "Build L3: Hardened builds",
        LEVELS[2]["requirement"].startswith("signed provenance"),
        LEVELS[3]["requirement"] == "hardened build platform",
        LEVELS[2]["focus"] == "Tampering after the build",
        LEVELS[3]["focus"] == "Tampering during the build",
    ]
    taxonomy_ok = sum(taxonomy)

    enum_checks = 0
    enum_ok = 0
    for r in range(len(CAPABILITIES) + 1):
        for combo in combinations(CAPABILITIES, r):
            enum_checks += 1
            got = assess(combo)
            want = expected_level(set(combo))
            if got["level"] == want and got["name"] == LEVELS[want]["name"]:
                enum_ok += 1

    gap_ok = int(
        assess(["hardened_platform"])["level"] == 0
        and assess(["provenance_exists", "hardened_platform"])["level"] == 1
        and assess(["provenance_exists", "hosted_platform",
                    "hardened_platform"])["level"] == 1
        and assess(CAPABILITIES)["level"] == 3
        and assess([])["missing_for_next"] == ["provenance_exists"])

    rejects = 0
    for bad in (lambda: assess(["sbom"]),
                lambda: assess(["provenance_exists", "L3"])):
        try:
            bad()
        except SLSAError:
            rejects += 1

    total = len(taxonomy) + enum_checks + 1
    matched = taxonomy_ok + enum_ok + gap_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "slsa_levels",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "levels": len(LEVELS),
        "subsets_enumerated": enum_checks,
        "subsets_ok": enum_ok,
        "gap_capping_ok": gap_ok,
        "reject_cases": 2,
        "rejects_ok": rejects,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "slsa_levels.json", obj,
         script="python3 claimlib/modules/slsa_levels/evidence.py")
    # claim:CLAIM-LIB-SLSA-001 checks_matched
    # All 26 checks pass: the four published v1.1 Build levels with their
    # names, requirements and focus rows, all 16 capability subsets
    # enumerated against an independent re-derivation of the cumulative
    # rule, and gap-capping verified (hardened without signed caps at L1) —
    # checks_matched = 26, mismatches = 0.
    print(f"slsa_levels: {obj['checks_matched']}/{obj['checks']} checks "
          f"({obj['subsets_ok']}/{obj['subsets_enumerated']} subsets "
          f"exhaustive); rejects {obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
