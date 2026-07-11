# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MACADDR-001 -- MAC flag decoding matches the IEEE 802
bit definitions and all four notations parse to the same value.

Each row's expected flags are INDEPENDENTLY KNOWN from the IEEE 802 address
format: the least-significant bit of the first octet is the I/G (multicast) bit
and the next bit is the U/L (locally administered) bit. The reference MACs are
well-known: 01:00:5e:.. (IPv4 multicast), 33:33:.. (IPv6 multicast),
ff:ff:ff:ff:ff:ff (broadcast), 02:.. and 52:54:00:.. (locally administered),
and ordinary vendor-OUI unicast addresses. A second battery checks that the
colon, hyphen, Cisco-dotted, and bare-hex spellings of one address all parse to
the same 48-bit integer. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (macaddr.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from macaddr import (  # noqa: E402
    parse, format_mac, is_multicast, is_locally_administered, is_broadcast, oui)
from _util import emit  # noqa: E402

# (mac, {multicast, local, broadcast}) with the expected flags written by hand
# from the IEEE 802 bit rules.
CASES = [
    ("01:00:5e:00:00:fb", {"multicast": True, "local": False, "broadcast": False}),
    ("33:33:00:00:00:01", {"multicast": True, "local": True, "broadcast": False}),
    ("ff:ff:ff:ff:ff:ff", {"multicast": True, "local": True, "broadcast": True}),
    ("02:00:00:00:00:01", {"multicast": False, "local": True, "broadcast": False}),
    ("52:54:00:12:34:56", {"multicast": False, "local": True, "broadcast": False}),
    ("00:1a:2b:3c:4d:5e", {"multicast": False, "local": False, "broadcast": False}),
    ("00:00:00:00:00:00", {"multicast": False, "local": False, "broadcast": False}),
]

# Every spelling of this address must parse to the same integer.
EQUIV = ["aa:bb:cc:dd:ee:ff", "AA-BB-CC-DD-EE-FF", "aabb.ccdd.eeff", "aabbccddeeff"]


def run() -> dict:
    rows = []
    correct = 0
    for mac, expected in CASES:
        value = parse(mac)
        got = {"multicast": is_multicast(value),
               "local": is_locally_administered(value),
               "broadcast": is_broadcast(value)}
        ok = (got == expected)
        correct += int(ok)
        rows.append({"mac": mac, "expected": expected, "computed": got, "correct": ok})

    equiv_values = {parse(form) for form in EQUIV}
    forms_agree = (len(equiv_values) == 1)
    canonical = format_mac(next(iter(equiv_values)))
    oui_ok = (oui(parse("00:1a:2b:3c:4d:5e")) == 0x001A2B)

    return {
        "schema": "claimlib_macaddr_v1",
        "module": "macaddr",
        "n_cases": len(CASES),
        "correct": correct,
        "errors": len(CASES) - correct,
        "notation_forms_tested": len(EQUIV),
        "notation_forms_agree": forms_agree,
        "canonical_form": canonical,
        "oui_reference_ok": oui_ok,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "macaddr.json", obj,
         script="python3 claimlib/modules/macaddr/evidence.py")
    # claim:CLAIM-LIB-MACADDR-001 correct
    # Every reference MAC's flags match the IEEE bit rules, so correct = 7 and
    # errors = 0 (n_cases = 7); all 4 notations parse to one value.
    print(f"macaddr: {obj['correct']}/{obj['n_cases']} flag sets match "
          f"({obj['errors']} errors), notations agree={obj['notation_forms_agree']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
