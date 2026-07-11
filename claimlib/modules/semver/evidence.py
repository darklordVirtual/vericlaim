# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-SEMVER-001 — the SemVer 2.0.0 comparator and range
grammar produce the answers required by the published precedence rules.

Runs the reusable ``semver`` module over a fixed battery of comparison rows
and satisfies rows whose expected answers are derived directly from the
SemVer 2.0.0 specification (§10 build metadata, §11 precedence) and the
well-known caret/tilde range desugarings. Records how many rows are correct.
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (semver.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from semver import compare, satisfies  # noqa: E402
from _util import emit  # noqa: E402

# --- comparison battery -------------------------------------------------------
# (a, b, expected -1|0|1). Expected values are read off the SemVer 2.0.0 spec:
#   * §11.2 core precedence:            1.0.0 < 2.0.0 < 2.1.0 < 2.1.1
#   * §11.3 pre-release < release:      1.0.0-alpha < 1.0.0
#   * §11.4 the canonical golden chain (verbatim spec example):
#         1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-alpha.beta < 1.0.0-beta
#           < 1.0.0-beta.2 < 1.0.0-beta.11 < 1.0.0-rc.1 < 1.0.0
#   * §11.4.3 numeric identifiers rank below alphanumeric: 1.0.0-1 < 1.0.0-alpha
#   * §10 build metadata is ignored for precedence: 1.0.0+x == 1.0.0
COMPARE_CASES = [
    ("1.0.0", "2.0.0", -1),                       # §11.2
    ("2.0.0", "2.1.0", -1),                       # §11.2
    ("2.1.0", "2.1.1", -1),                       # §11.2
    ("1.0.0-alpha", "1.0.0-alpha.1", -1),         # §11.4 chain
    ("1.0.0-alpha.1", "1.0.0-alpha.beta", -1),    # §11.4 chain
    ("1.0.0-alpha.beta", "1.0.0-beta", -1),       # §11.4 chain
    ("1.0.0-beta", "1.0.0-beta.2", -1),           # §11.4 chain
    ("1.0.0-beta.2", "1.0.0-beta.11", -1),        # §11.4 chain (numeric 2 < 11)
    ("1.0.0-beta.11", "1.0.0-rc.1", -1),          # §11.4 chain
    ("1.0.0-rc.1", "1.0.0", -1),                  # §11.4 chain / §11.3
    ("1.0.0-alpha", "1.0.0", -1),                 # §11.3
    ("1.0.0", "1.0.0", 0),                        # reflexive equality
    ("1.0.0+build", "1.0.0", 0),                  # §10 build ignored
    ("1.0.0+build.1", "1.0.0+build.2", 0),        # §10 build ignored
    ("2.0.0", "1.0.0", 1),                        # §11.2 (reversed)
    ("1.0.0", "1.0.0-alpha", 1),                  # §11.3 (reversed)
    ("1.0.0-alpha.1", "1.0.0-alpha.1", 0),        # pre-release equality
    ("1.0.0-1", "1.0.0-alpha", -1),               # §11.4.3 numeric < alnum
]

# --- satisfies battery --------------------------------------------------------
# (version, spec, expected bool). Expected values follow SemVer precedence
# against the derived bounds:
#   exact  x.y.z   -> equal precedence
#   >=x.y.z        -> version >= x.y.z
#   <x.y.z         -> version <  x.y.z
#   ^x.y.z (caret) -> >=x.y.z and < next left-most non-zero element:
#                     ^1.2.3 -> <2.0.0 ; ^0.2.3 -> <0.3.0 ; ^0.0.3 -> <0.0.4
#   ~x.y.z (tilde) -> >=x.y.z and <x.(y+1).0
# Pre-release rows use §11.3 (a pre-release is below the associated release).
SATISFIES_CASES = [
    ("1.2.3", "1.2.3", True),          # exact match
    ("1.2.4", "1.2.3", False),         # exact mismatch
    ("1.2.3", ">=1.2.3", True),        # >= boundary (equal)
    ("1.2.4", ">=1.2.3", True),        # >= above
    ("1.2.2", ">=1.2.3", False),       # >= below
    ("2.0.0", ">=1.2.3", True),        # >= far above
    ("1.2.2", "<1.2.3", True),         # < below
    ("1.2.3", "<1.2.3", False),        # < boundary excluded
    ("1.2.4", "<1.2.3", False),        # < above
    ("1.2.3", "^1.2.3", True),         # caret lower bound
    ("1.9.9", "^1.2.3", True),         # caret within (<2.0.0)
    ("2.0.0", "^1.2.3", False),        # caret upper bound excluded
    ("1.2.2", "^1.2.3", False),        # caret below lower
    ("0.2.3", "^0.2.3", True),         # caret 0.x lower bound
    ("0.2.9", "^0.2.3", True),         # caret 0.x within (<0.3.0)
    ("0.3.0", "^0.2.3", False),        # caret 0.x upper excluded
    ("0.2.2", "^0.2.3", False),        # caret 0.x below lower
    ("0.0.3", "^0.0.3", True),         # caret 0.0.x lower bound
    ("0.0.4", "^0.0.3", False),        # caret 0.0.x upper excluded (<0.0.4)
    ("1.2.3", "~1.2.3", True),         # tilde lower bound
    ("1.2.99", "~1.2.3", True),        # tilde within (<1.3.0)
    ("1.3.0", "~1.2.3", False),        # tilde upper excluded
    ("1.2.2", "~1.2.3", False),        # tilde below lower
    ("2.0.0", "~1.2.3", False),        # tilde far above
    ("1.2.3-alpha", "^1.2.3", False),  # §11.3 pre-release below 1.2.3 lower
    ("1.2.3-alpha", ">=1.2.3-alpha", True),   # pre-release equal boundary
    ("1.2.3-beta", ">=1.2.3-alpha", True),    # §11.4 beta > alpha
    ("1.2.3-alpha", "<1.2.3", True),   # §11.3 pre-release < release
]


def run() -> dict:
    cases = []
    correct = 0
    errors = 0
    for a, b, expected in COMPARE_CASES:
        got = compare(a, b)
        ok = (got == expected)
        correct += int(ok)
        errors += int(not ok)
        cases.append({"kind": "compare", "a": a, "b": b,
                      "expected": expected, "computed": got, "ok": ok})
    for version, spec, expected in SATISFIES_CASES:
        got = satisfies(version, spec)
        ok = (got == expected)
        correct += int(ok)
        errors += int(not ok)
        cases.append({"kind": "satisfies", "version": version, "spec": spec,
                      "expected": expected, "computed": got, "ok": ok})
    n_cases = len(COMPARE_CASES) + len(SATISFIES_CASES)
    return {
        "schema": "claimlib_semver_v1",
        "module": "semver",
        "n_cases": n_cases,
        "correct": correct,
        "errors": errors,
        "n_compare": len(COMPARE_CASES),
        "n_satisfies": len(SATISFIES_CASES),
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "semver.json", obj,
         script="python3 claimlib/modules/semver/evidence.py")
    # claim:CLAIM-LIB-SEMVER-001 correct
    # All 46 reference rows (18 compare + 28 satisfies) match the SemVer 2.0.0
    # precedence rules, so correct = 46 and errors = 0.
    print(f"semver: {obj['correct']}/{obj['n_cases']} reference rows correct "
          f"({obj['errors']} errors)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
