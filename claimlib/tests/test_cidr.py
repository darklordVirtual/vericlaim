# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``cidr`` library, cross-checked against stdlib ipaddress."""
import ipaddress
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "cidr"))

from cidr import (  # noqa: E402
    parse_ip, ip_to_str, parse_cidr, netmask, network_address,
    broadcast_address, num_addresses, num_usable_hosts, host_range, contains, CIDRError)


def test_known_values():
    net, prefix = parse_cidr("192.0.2.10/24")
    assert ip_to_str(net) == "192.0.2.0"
    assert ip_to_str(broadcast_address(net, prefix)) == "192.0.2.255"
    assert ip_to_str(netmask(24)) == "255.255.255.0"
    assert num_usable_hosts(24) == 254
    assert num_addresses(24) == 256


def test_agrees_with_ipaddress():
    for cidr in ("10.0.0.0/8", "172.16.5.4/22", "203.0.113.7/28",
                 "198.51.100.0/30", "192.168.1.1/31", "8.8.8.8/32", "0.0.0.0/0"):
        net, prefix = parse_cidr(cidr)
        o = ipaddress.ip_network(cidr, strict=False)
        assert ip_to_str(network_address(net, prefix)) == str(o.network_address)
        assert ip_to_str(broadcast_address(net, prefix)) == str(o.broadcast_address)
        assert num_addresses(prefix) == o.num_addresses
        # Enumerate hosts() only for small blocks (never materialize a /8 or /0).
        if o.num_addresses <= 4096:
            assert num_usable_hosts(prefix) == len(list(o.hosts()))


def test_rfc3021_and_host_routes():
    net, prefix = parse_cidr("192.168.1.0/31")
    assert num_usable_hosts(31) == 2
    assert host_range(net, prefix) == (net, net + 1)
    assert num_usable_hosts(32) == 1


def test_membership():
    net, prefix = parse_cidr("192.0.2.0/24")
    assert contains(net, prefix, parse_ip("192.0.2.200")) is True
    assert contains(net, prefix, parse_ip("192.0.3.1")) is False


def test_parse_round_trip():
    for ip in ("0.0.0.0", "255.255.255.255", "1.2.3.4", "192.168.100.1"):
        assert ip_to_str(parse_ip(ip)) == ip


def test_rejects_bad_input():
    for bad in ("192.168.1", "256.0.0.1", "1.2.3.4.5", "1.2.3.04", "a.b.c.d", ""):
        with pytest.raises(CIDRError):
            parse_ip(bad)
    with pytest.raises(CIDRError):
        parse_cidr("192.0.2.0/33")
    with pytest.raises(CIDRError):
        parse_cidr("192.0.2.0")
