# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-JSONPOINTER-001 — the RFC 6901 JSON Pointer resolver
reproduces the published example results.

Runs the reusable ``jsonpointer`` module over the exact example document and the
12 example pointers from RFC 6901 section 5, comparing each result against the
value the RFC publishes (hand-transcribed here, independent of this module).
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (jsonpointer.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from jsonpointer import resolve  # noqa: E402
from _util import emit  # noqa: E402

# The exact RFC 6901 section 5 example document. In Python source the keys
# "i\\j" and "k\"l" denote the two-character-plus values i\j and k"l.
DOC = {
    "foo": ["bar", "baz"],
    "": 0,
    "a/b": 1,
    "c%d": 2,
    "e^f": 3,
    "g|h": 4,
    "i\\j": 5,
    "k\"l": 6,
    " ": 7,
    "m~n": 8,
}

# (pointer, published result). Each expected value is transcribed from RFC 6901
# section 5 — NOT produced by this resolver. The whole-document case ("") is
# expected to return DOC itself.
REFERENCE = [
    ("", DOC),
    ("/foo", ["bar", "baz"]),
    ("/foo/0", "bar"),
    ("/", 0),
    ("/a~1b", 1),
    ("/c%d", 2),
    ("/e^f", 3),
    ("/g|h", 4),
    ("/i\\j", 5),
    ("/k\"l", 6),
    ("/ ", 7),
    ("/m~0n", 8),
]


def run() -> dict:
    cases = []
    passed = 0
    for pointer, expected in REFERENCE:
        got = resolve(DOC, pointer)
        ok = (got == expected)
        passed += int(ok)
        cases.append({
            "pointer": pointer,
            "expected": expected,
            "computed": got,
            "match": ok,
        })
    return {
        "schema": "claimlib_jsonpointer_v1",
        "module": "jsonpointer",
        "reference_cases": len(REFERENCE),
        "reference_cases_passed": passed,
        "failures": len(REFERENCE) - passed,
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "jsonpointer.json", obj,
         script="python3 claimlib/modules/jsonpointer/evidence.py")
    # claim:CLAIM-LIB-JSONPOINTER-001 reference_cases_passed
    # All 12 published RFC 6901 section 5 example pointers resolve to their
    # published values, so reference_cases_passed = 12 and failures = 0.
    print(f"jsonpointer: {obj['reference_cases_passed']}/{obj['reference_cases']} "
          f"RFC 6901 example pointers reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
