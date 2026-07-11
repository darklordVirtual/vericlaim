# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``macaddr`` library."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "macaddr"))

from macaddr import (  # noqa: E402
    parse, format_mac, is_multicast, is_unicast, is_locally_administered,
    is_broadcast, oui, MACError)


def test_notation_equivalence():
    v = parse("aa:bb:cc:dd:ee:ff")
    assert parse("AA-BB-CC-DD-EE-FF") == v
    assert parse("aabb.ccdd.eeff") == v
    assert parse("aabbccddeeff") == v
    assert format_mac(v) == "aa:bb:cc:dd:ee:ff"


def test_ieee_flag_bits():
    assert is_multicast(parse("01:00:5e:00:00:fb")) is True
    assert is_unicast(parse("00:1a:2b:3c:4d:5e")) is True
    assert is_locally_administered(parse("02:00:00:00:00:01")) is True
    assert is_locally_administered(parse("00:1a:2b:3c:4d:5e")) is False
    assert is_broadcast(parse("ff:ff:ff:ff:ff:ff")) is True
    assert is_multicast(parse("ff:ff:ff:ff:ff:ff")) is True


def test_oui():
    assert oui(parse("00:1a:2b:3c:4d:5e")) == 0x001A2B


def test_format_separators():
    v = parse("00:1a:2b:3c:4d:5e")
    assert format_mac(v, "-") == "00-1a-2b-3c-4d-5e"


def test_rejects_bad_input():
    for bad in ("00:1a:2b:3c:4d", "gg:00:00:00:00:00", "001a2b3c4d",
                "00:1a:2b:3c:4d:5e:6f", "aabb.ccdd", ""):
        with pytest.raises(MACError):
            parse(bad)
