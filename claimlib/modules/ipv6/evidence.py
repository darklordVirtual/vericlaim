# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-IPV6-001 -- the from-scratch IPv6 parser / RFC 5952
compressor agrees with Python's stdlib ``ipaddress`` over a fixed battery.

``ipaddress`` is an independent implementation this module never imports.
For every address the evidence checks that ``compress(parse(s))`` equals
``ipaddress.ip_address(s).compressed`` and ``explode(parse(s))`` equals
``.exploded``; for every CIDR it checks the compressed network address and the
total address count. The battery exercises the RFC 5952 edges: full and already
compressed forms, ``::`` and ``::1``, a single embedded zero group (must NOT
compress), and two equal-length zero runs (leftmost must win). Deterministic.
"""
from __future__ import annotations

import ipaddress
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (ipv6.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from ipv6 import parse, compress, explode, parse_cidr, network_address, num_addresses  # noqa: E402
from _util import emit  # noqa: E402

ADDRESSES = [
    "2001:0db8:0000:0000:0000:ff00:0042:8329",  # full -> compresses
    "2001:db8::ff00:42:8329",                    # already canonical
    "::1",
    "::",
    "fe80::1",
    "2001:db8:0:0:1:0:0:1",                       # two equal zero runs: leftmost wins
    "0:0:0:0:0:0:0:0",
    "1:2:3:4:5:6:7:8",                            # no zeros -> no '::'
    "2001:db8::",
    "ff02::1:ff00:0",
    "2001:db8:0:1:1:1:1:1",                        # single zero group -> NOT compressed
    "a:b:c:d:e:f:0:0",
]

CIDRS = [
    "2001:db8::/32", "fe80::/10", "::/0", "2001:db8:abcd:12::/64",
    "ff00::/8", "2001:db8:1:2:3:4:5:6/128", "64:ff9b::/96",
]


def run() -> dict:
    checks = 0
    matched = 0
    addr_rows = []
    for s in ADDRESSES:
        value = parse(s)
        oracle = ipaddress.ip_address(s)
        got_c, exp_c = compress(value), oracle.compressed
        got_e, exp_e = explode(value), oracle.exploded
        for got, exp in ((got_c, exp_c), (got_e, exp_e)):
            checks += 1
            matched += int(got == exp)
        addr_rows.append({"input": s, "compress": got_c, "compress_ok": got_c == exp_c,
                          "explode_ok": got_e == exp_e})

    cidr_rows = []
    for s in CIDRS:
        net_int, prefix = parse_cidr(s)
        oracle = ipaddress.ip_network(s, strict=False)
        got_net = compress(network_address(net_int, prefix))
        exp_net = oracle.network_address.compressed
        got_n, exp_n = num_addresses(prefix), oracle.num_addresses
        for got, exp in ((got_net, exp_net), (got_n, exp_n)):
            checks += 1
            matched += int(str(got) == str(exp))
        cidr_rows.append({"cidr": s, "network": got_net, "network_ok": got_net == exp_net,
                          "num_addresses_ok": got_n == exp_n})

    return {
        "schema": "claimlib_ipv6_v1",
        "module": "ipv6",
        "n_addresses": len(ADDRESSES),
        "n_cidrs": len(CIDRS),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "address_detail": addr_rows,
        "cidr_detail": cidr_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "ipv6.json", obj,
         script="python3 claimlib/modules/ipv6/evidence.py")
    # claim:CLAIM-LIB-IPV6-001 checks_matched
    # Every compress/explode/network/count check agrees with the ipaddress
    # oracle, so checks_matched = 38 and mismatches = 0.
    print(f"ipv6: {obj['checks_matched']}/{obj['checks']} checks agree with the "
          f"ipaddress oracle ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
