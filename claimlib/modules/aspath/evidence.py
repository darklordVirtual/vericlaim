# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-ASPATH-001 -- ASN classification matches the published
RFC allocation boundaries, and AS-path parsing round-trips.

Each ASN's expected (private, reserved) label is INDEPENDENTLY KNOWN from the
RFCs (6996 private, 7300 last-ASN, 5398 documentation, 7607 AS0, 6793 AS_TRANS).
The battery pins every boundary (first/last of each range and the value just
outside it). A second check parses a real-shaped AS-path, measures its length,
extracts the origin, and strips private ASNs. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (aspath.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from aspath import (  # noqa: E402
    parse, path_length, origin, is_private, is_reserved, is_public, strip_private)
from _util import emit  # noqa: E402

# (asn, expected_private, expected_reserved). Boundaries pinned on both sides.
CASES = [
    (15169, False, False),         # Google -- ordinary public
    (174, False, False),           # Cogent -- ordinary public
    (0, False, True),              # AS0 reserved (RFC 7607)
    (23456, False, True),          # AS_TRANS (RFC 6793)
    (64495, False, False),         # just below documentation range -> public
    (64496, False, True),          # doc range start (RFC 5398)
    (64511, False, True),          # doc range end
    (64512, True, False),          # 16-bit private start (RFC 6996)
    (65534, True, False),          # 16-bit private end
    (65535, False, True),          # last 16-bit ASN reserved (RFC 7300)
    (65536, False, True),          # 32-bit doc start (RFC 5398)
    (65551, False, True),          # 32-bit doc end
    (65552, False, False),         # just above doc -> public
    (4199999999, False, False),    # just below 32-bit private -> public
    (4200000000, True, False),     # 32-bit private start (RFC 6996)
    (4294967294, True, False),     # 32-bit private end
    (4294967295, False, True),     # last 32-bit ASN reserved (RFC 7300)
]


def run() -> dict:
    rows = []
    correct = 0
    for asn, exp_priv, exp_res in CASES:
        got_priv, got_res = is_private(asn), is_reserved(asn)
        # public is exactly "neither private nor reserved"
        exp_public = not (exp_priv or exp_res)
        ok = (got_priv == exp_priv and got_res == exp_res and is_public(asn) == exp_public)
        correct += int(ok)
        rows.append({"asn": asn, "expected_private": exp_priv, "computed_private": got_priv,
                     "expected_reserved": exp_res, "computed_reserved": got_res, "correct": ok})

    sample = "7018 64512 174 3356 15169"   # 64512 is the only private ASN here
    path = parse(sample)
    path_ok = (path == [7018, 64512, 174, 3356, 15169]
               and path_length(path) == 5
               and origin(path) == 15169
               and strip_private(path) == [7018, 174, 3356, 15169])

    return {
        "schema": "claimlib_aspath_v1",
        "module": "aspath",
        "n_cases": len(CASES),
        "correct": correct,
        "errors": len(CASES) - correct,
        "path_ops_ok": path_ok,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "aspath.json", obj,
         script="python3 claimlib/modules/aspath/evidence.py")
    # claim:CLAIM-LIB-ASPATH-001 correct
    # Every ASN classifies as its RFC label says, so correct = 17 and
    # errors = 0 (n_cases = 17); path parse/length/origin/strip all hold.
    print(f"aspath: {obj['correct']}/{obj['n_cases']} ASNs classified correctly "
          f"({obj['errors']} errors), path_ops_ok={obj['path_ops_ok']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
