# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``ipv6`` library, cross-checked against stdlib ipaddress."""
import ipaddress
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "ipv6"))

from ipv6 import (  # noqa: E402
    parse, compress, explode, parse_cidr, num_addresses, IPv6Error)


def test_canonical_compression():
    assert compress(parse("2001:0db8:0000:0000:0000:ff00:0042:8329")) == "2001:db8::ff00:42:8329"
    assert compress(parse("::1")) == "::1"
    assert compress(parse("0:0:0:0:0:0:0:0")) == "::"
    assert compress(parse("fe80::1")) == "fe80::1"


def test_leftmost_longest_zero_run():
    # Two equal-length zero runs -> the leftmost is compressed (RFC 5952).
    assert compress(parse("2001:db8:0:0:1:0:0:1")) == "2001:db8::1:0:0:1"


def test_single_zero_group_not_compressed():
    # A lone zero group must render as '0', never '::'.
    assert compress(parse("2001:db8:0:1:1:1:1:1")) == "2001:db8:0:1:1:1:1:1"


def test_agrees_with_ipaddress():
    for s in ("2001:db8::ff00:42:8329", "::", "ff02::1:ff00:0",
              "1:2:3:4:5:6:7:8", "a:b:c:d:e:f:0:0"):
        assert compress(parse(s)) == ipaddress.ip_address(s).compressed
        assert explode(parse(s)) == ipaddress.ip_address(s).exploded


def test_prefix_math():
    net, prefix = parse_cidr("2001:db8:abcd:12::/64")
    o = ipaddress.ip_network("2001:db8:abcd:12::/64")
    assert compress(net) == o.network_address.compressed
    assert num_addresses(prefix) == o.num_addresses
    assert num_addresses(128) == 1


def test_rejects_bad_input():
    for bad in ("", "1::2::3", "12345::", "gg::", "1:2:3:4:5:6:7", "::ffff:1.2.3.4"):
        with pytest.raises(IPv6Error):
            parse(bad)
    with pytest.raises(IPv6Error):
        parse_cidr("2001:db8::/129")
