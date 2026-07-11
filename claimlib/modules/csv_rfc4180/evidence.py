# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CSV-RFC4180-001 -- the CSV parser agrees with the stdlib
``csv`` module and the writer round-trips.

The stdlib ``csv`` module is an independent implementation this module never
imports, so it is a genuine oracle. For each input the evidence checks that
parse(text) equals list(csv.reader(StringIO(text))), across quoted fields,
embedded delimiters / newlines / doubled quotes, empty fields, and multiple
records. A second battery checks the round-trip: parse(format_rows(rows)) == rows
for a set of records (including fields that require quoting). Deterministic.
"""
from __future__ import annotations

import csv
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (csv_rfc4180.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from csv_rfc4180 import parse, format_rows  # noqa: E402
from _util import emit  # noqa: E402

# Inputs cross-checked against csv.reader (all unambiguous RFC 4180).
INPUTS = [
    "a,b,c",
    "a,b,c\r\nd,e,f",
    "a,b,c\nd,e,f",
    'a,"b,c",d',
    '"a""b",c',
    '"line1\nline2",x',
    "a,,c",
    "1,2,3\r\n4,5,6\r\n7,8,9",
    'name,"Doe, John",42',
    '"quoted",plain,"with ""quotes"""',
    "single",
    "trailing,\r\n",
]

# Records round-tripped through format_rows -> parse.
ROWS = [
    [["a", "b", "c"]],
    [["a", "b,c", "d"], ["e", "f", "g"]],
    [["has \"quote\"", "plain"]],
    [["line\nbreak", "x"], ["y", "z"]],
    [["", "", ""]],
]


def run() -> dict:
    parse_checks = 0
    parse_matched = 0
    for text in INPUTS:
        oracle = list(csv.reader(io.StringIO(text)))
        parse_checks += 1
        parse_matched += int(parse(text) == oracle)

    roundtrip_checks = 0
    roundtrip_matched = 0
    for rows in ROWS:
        roundtrip_checks += 1
        roundtrip_matched += int(parse(format_rows(rows)) == rows)

    checks = parse_checks + roundtrip_checks
    matched = parse_matched + roundtrip_matched
    return {
        "schema": "claimlib_csv_rfc4180_v1",
        "module": "csv_rfc4180",
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "parse_cases": parse_checks,
        "parse_matched": parse_matched,
        "roundtrip_cases": roundtrip_checks,
        "roundtrip_matched": roundtrip_matched,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "csv_rfc4180.json", obj,
         script="python3 claimlib/modules/csv_rfc4180/evidence.py")
    # claim:CLAIM-LIB-CSV-RFC4180-001 checks_matched
    # Every parse matches csv.reader and every round-trip holds, so
    # checks_matched = 17 and mismatches = 0.
    print(f"csv_rfc4180: {obj['checks_matched']}/{obj['checks']} checks agree with "
          f"stdlib csv / round-trip ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
