# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CIDR-001 -- the from-scratch IPv4 CIDR math agrees with
Python's stdlib ``ipaddress`` on every operation across a fixed battery.

``ipaddress`` is a completely independent implementation that this module never
imports, so it is a genuine oracle. For every CIDR in the battery the evidence
compares, field by field: network address, broadcast address, netmask, total
address count, usable host count, and the first/last usable host -- plus a
membership sweep (addresses inside vs. just outside the block). All comparisons
use ``ipaddress``'s O(1) properties and indexing (never enumerating hosts of a
wide block); small blocks additionally cross-check the full ``hosts()`` count.
Every field that matches counts toward ``checks_matched``. Deterministic.
"""
from __future__ import annotations

import ipaddress
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (cidr.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from cidr import (  # noqa: E402
    ip_to_str, parse_cidr, netmask, network_address,
    broadcast_address, num_addresses, num_usable_hosts, host_range, contains)
from _util import emit  # noqa: E402

# A spread of prefixes and offsets, incl. the RFC 3021 /31 and single-host /32.
BATTERY = [
    "192.0.2.0/24", "192.0.2.130/25", "10.0.0.0/8", "172.16.5.4/22",
    "203.0.113.7/28", "198.51.100.0/30", "192.168.1.1/31", "8.8.8.8/32",
    "0.0.0.0/0", "255.255.255.128/25", "100.64.0.0/10", "169.254.0.0/16",
]


def _expected_hosts(oracle) -> tuple[str, str, int]:
    """(first_host, last_host, usable_count) from ipaddress, via O(1) indexing."""
    prefix = oracle.prefixlen
    if prefix <= 30:
        return str(oracle[1]), str(oracle[-2]), oracle.num_addresses - 2
    if prefix == 31:                       # RFC 3021: both addresses usable
        return str(oracle[0]), str(oracle[1]), 2
    return str(oracle[0]), str(oracle[0]), 1  # /32 single host


def run() -> dict:
    checks = 0
    matched = 0
    rows = []
    for cidr in BATTERY:
        net_int, prefix = parse_cidr(cidr)
        oracle = ipaddress.ip_network(cidr, strict=False)
        exp_first, exp_last, exp_usable = _expected_hosts(oracle)
        first, last = host_range(net_int, prefix)
        pairs = {
            "network": (ip_to_str(network_address(net_int, prefix)),
                        str(oracle.network_address)),
            "broadcast": (ip_to_str(broadcast_address(net_int, prefix)),
                          str(oracle.broadcast_address)),
            "netmask": (ip_to_str(netmask(prefix)), str(oracle.netmask)),
            "num_addresses": (num_addresses(prefix), oracle.num_addresses),
            "usable_hosts": (num_usable_hosts(prefix), exp_usable),
            "first_host": (ip_to_str(first), exp_first),
            "last_host": (ip_to_str(last), exp_last),
        }
        row = {"cidr": cidr, "fields": {}}
        for name, (got, exp) in pairs.items():
            ok = str(got) == str(exp)
            checks += 1
            matched += int(ok)
            row["fields"][name] = ok
        rows.append(row)

    # Small blocks: additionally verify the FULL hosts() enumeration count
    # (cheap; a fully independent second check for narrow prefixes).
    enum_checks = 0
    enum_ok = 0
    for cidr in BATTERY:
        oracle = ipaddress.ip_network(cidr, strict=False)
        if oracle.num_addresses > 4096:
            continue
        net_int, prefix = parse_cidr(cidr)
        enum_checks += 1
        enum_ok += int(num_usable_hosts(prefix) == len(list(oracle.hosts())))

    # Membership sweep: network and broadcast are inside; the addresses just
    # below the network and just above the broadcast are outside.
    membership_checks = 0
    membership_ok = 0
    for cidr in BATTERY:
        net_int, prefix = parse_cidr(cidr)
        oracle = ipaddress.ip_network(cidr, strict=False)
        probes = [network_address(net_int, prefix),
                  broadcast_address(net_int, prefix),
                  (network_address(net_int, prefix) - 1) & 0xFFFFFFFF,
                  (broadcast_address(net_int, prefix) + 1) & 0xFFFFFFFF]
        for probe in probes:
            got = contains(net_int, prefix, probe)
            exp = ipaddress.ip_address(probe) in oracle
            membership_checks += 1
            membership_ok += int(got == exp)

    checks += enum_checks + membership_checks
    matched += enum_ok + membership_ok
    return {
        "schema": "claimlib_cidr_v1",
        "module": "cidr",
        "n_networks": len(BATTERY),
        "checks": checks,
        "checks_matched": matched,
        "mismatches": checks - matched,
        "enum_checks": enum_checks,
        "enum_matched": enum_ok,
        "membership_checks": membership_checks,
        "membership_matched": membership_ok,
        "field_detail": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "cidr.json", obj,
         script="python3 claimlib/modules/cidr/evidence.py")
    # claim:CLAIM-LIB-CIDR-001 checks_matched
    # Every field, enumeration and membership check agrees with the ipaddress
    # oracle, so checks_matched = 140 and mismatches = 0.
    print(f"cidr: {obj['checks_matched']}/{obj['checks']} checks agree with the "
          f"ipaddress oracle ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
