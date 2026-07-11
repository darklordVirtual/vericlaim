# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``aspath`` library (BGP AS-path + ASN ranges)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "aspath"))

from aspath import (  # noqa: E402
    parse, path_length, origin, is_private, is_reserved, is_public,
    strip_private, ASPathError)


def test_private_ranges():
    assert is_private(64512) is True
    assert is_private(65534) is True
    assert is_private(4200000000) is True
    assert is_private(4294967294) is True
    assert is_private(64511) is False
    assert is_private(15169) is False


def test_reserved_values():
    for asn in (0, 23456, 65535, 4294967295, 64496, 64511, 65536, 65551):
        assert is_reserved(asn) is True
    assert is_reserved(15169) is False


def test_public_is_neither():
    assert is_public(15169) is True
    assert is_public(64512) is False   # private
    assert is_public(65535) is False   # reserved


def test_path_operations():
    path = parse("7018 64512 174 3356 15169")   # 64512 is the only private ASN
    assert path_length(path) == 5
    assert origin(path) == 15169
    assert strip_private(path) == [7018, 174, 3356, 15169]


def test_rejects_bad_input():
    with pytest.raises(ASPathError):
        parse("65001 abc 174")
    with pytest.raises(ASPathError):
        parse("4294967296")            # above 32-bit max
    with pytest.raises(ASPathError):
        origin([])
    with pytest.raises(ASPathError):
        is_private(-1)
