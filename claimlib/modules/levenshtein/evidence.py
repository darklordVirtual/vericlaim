# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-LEVENSHTEIN-001 -- edit distance reproduces the published
textbook values and satisfies the metric axioms.

Two independent references:
  1. Published distances: the canonical worked examples (kitten->sitting = 3,
     Saturday->Sunday = 3, flaw->lawn = 2, gumbo->gambol = 2, book->back = 2,
     ""->"abc" = 3). Each expected value is hand-written from the reference.
  2. Metric axioms: over all ordered pairs of a fixed word set the distance must
     satisfy identity (d(x,x)=0), symmetry (d(x,y)=d(y,x)), and the triangle
     inequality (d(x,z) <= d(x,y) + d(y,z)). These hold for a true metric
     independently of this implementation, so violating any would expose a bug.
Deterministic.
"""
from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (levenshtein.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from levenshtein import distance  # noqa: E402
from _util import emit  # noqa: E402

REFERENCE = [
    ("kitten", "sitting", 3),
    ("Saturday", "Sunday", 3),
    ("flaw", "lawn", 2),
    ("gumbo", "gambol", 2),
    ("book", "back", 2),
    ("", "abc", 3),
    ("abc", "abc", 0),
    ("distance", "distance", 0),
]

WORDS = ["", "a", "abc", "kitten", "sitting", "flaw", "lawn", "book", "back", "banana"]


def run() -> dict:
    reference_correct = 0
    rows = []
    for a, b, expected in REFERENCE:
        got = distance(a, b)
        ok = (got == expected)
        reference_correct += int(ok)
        rows.append({"a": a, "b": b, "expected": expected, "computed": got, "correct": ok})

    identity_ok = all(distance(w, w) == 0 for w in WORDS)
    symmetry_checks = symmetry_ok = 0
    for x, y in product(WORDS, WORDS):
        symmetry_checks += 1
        symmetry_ok += int(distance(x, y) == distance(y, x))
    triangle_checks = triangle_ok = 0
    for x, y, z in product(WORDS, WORDS, WORDS):
        triangle_checks += 1
        triangle_ok += int(distance(x, z) <= distance(x, y) + distance(y, z))

    return {
        "schema": "claimlib_levenshtein_v1",
        "module": "levenshtein",
        "n_reference": len(REFERENCE),
        "reference_correct": reference_correct,
        "reference_errors": len(REFERENCE) - reference_correct,
        "identity_holds": identity_ok,
        "symmetry_checks": symmetry_checks,
        "symmetry_ok": symmetry_ok,
        "triangle_checks": triangle_checks,
        "triangle_ok": triangle_ok,
        "reference_detail": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "levenshtein.json", obj,
         script="python3 claimlib/modules/levenshtein/evidence.py")
    # claim:CLAIM-LIB-LEVENSHTEIN-001 reference_correct
    # Every published distance reproduces, so reference_correct = 8 and
    # reference_errors = 0 (n_reference = 8); the metric axioms all hold.
    print(f"levenshtein: {obj['reference_correct']}/{obj['n_reference']} published "
          f"distances ({obj['reference_errors']} errors); "
          f"symmetry {obj['symmetry_ok']}/{obj['symmetry_checks']}, "
          f"triangle {obj['triangle_ok']}/{obj['triangle_checks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
