# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``uuid_tools`` library.

Reference values are independently known: the RFC 9562 Appendix A test
vectors (A.2 UUIDv3 and A.4 UUIDv5 for the DNS namespace and name
"www.example.com", plus the published v1/v4/v6/v7 examples), the section 6.6
namespace IDs, and Python's stdlib ``uuid`` module as an independent
implementation of the same construction.
"""
import sys
import uuid as stdlib_uuid
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "uuid_tools"))

from uuid_tools import (  # noqa: E402
    MAX_UUID, NAMESPACE_DNS, NAMESPACE_OID, NAMESPACE_URL, NAMESPACE_X500,
    NIL_UUID, UUIDError, format_uuid, inspect, parse, uuid3, uuid5,
    variant, version,
)

RFC_V1_EXAMPLE = "C232AB00-9414-11EC-B3C8-9F6BDECED846"   # RFC 9562 A.1


# --- RFC 9562 published vectors -------------------------------------------

def test_rfc9562_v5_dns_example():
    # RFC 9562 Appendix A.4, Figure 23.
    assert uuid5(NAMESPACE_DNS, "www.example.com") == \
        "2ed6657d-e927-568b-95e1-2665a8aea6a2"


def test_rfc9562_v3_dns_example():
    # RFC 9562 Appendix A.2, Figure 18.
    assert uuid3(NAMESPACE_DNS, "www.example.com") == \
        "5df41881-3aed-3515-88a7-2f4a814cf09e"


def test_rfc9562_published_examples_version_and_variant():
    # (uuid, version, variant) as stated in RFC 9562 Appendix A.
    for text, ver in [(RFC_V1_EXAMPLE, 1),
                      ("919108f7-52d1-4320-9bac-f847db4148a8", 4),
                      ("1EC9414C-232A-6B00-B3C8-9F6BDECED846", 6),
                      ("017F22E2-79B0-7CC3-98C4-DC0C0C07398F", 7)]:
        assert version(text) == ver
        assert variant(text) == "rfc9562"


def test_nil_and_max_uuids():
    nil = inspect(NIL_UUID)
    assert nil["is_nil"] and not nil["is_max"]
    assert nil["version"] is None and nil["variant"] == "ncs"
    mx = inspect(MAX_UUID)
    assert mx["is_max"] and not mx["is_nil"]
    assert mx["version"] is None and mx["variant"] == "future"


def test_namespace_ids_match_rfc_table3():
    assert NAMESPACE_DNS == "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
    assert NAMESPACE_URL == "6ba7b811-9dad-11d1-80b4-00c04fd430c8"
    assert NAMESPACE_OID == "6ba7b812-9dad-11d1-80b4-00c04fd430c8"
    assert NAMESPACE_X500 == "6ba7b814-9dad-11d1-80b4-00c04fd430c8"


# --- stdlib as an independent oracle ---------------------------------------

def test_uuid5_matches_stdlib_battery():
    for ns_str, ns_std in [(NAMESPACE_DNS, stdlib_uuid.NAMESPACE_DNS),
                           (NAMESPACE_URL, stdlib_uuid.NAMESPACE_URL),
                           (NAMESPACE_OID, stdlib_uuid.NAMESPACE_OID),
                           (NAMESPACE_X500, stdlib_uuid.NAMESPACE_X500)]:
        for name in ("www.example.com", "", "æøå", "a" * 100):
            assert uuid5(ns_str, name) == str(stdlib_uuid.uuid5(ns_std, name))
            assert uuid3(ns_str, name) == str(stdlib_uuid.uuid3(ns_std, name))


def test_parse_matches_stdlib_bytes():
    for text in (RFC_V1_EXAMPLE, NAMESPACE_DNS, NIL_UUID, MAX_UUID):
        assert parse(text) == stdlib_uuid.UUID(text).bytes


# --- parse / format behaviour ----------------------------------------------

def test_parse_accepts_urn_braces_and_mixed_case():
    raw = parse(NAMESPACE_DNS)
    assert parse("urn:uuid:" + NAMESPACE_DNS) == raw
    assert parse("{" + NAMESPACE_DNS + "}") == raw
    assert parse(NAMESPACE_DNS.upper()) == raw
    assert parse("URN:UUID:" + NAMESPACE_DNS.upper()) == raw


def test_format_is_canonical_lowercase_and_round_trips():
    s = format_uuid(parse(RFC_V1_EXAMPLE))
    assert s == RFC_V1_EXAMPLE.lower()
    assert parse(s) == parse(RFC_V1_EXAMPLE)


def test_parse_rejects_malformed_inputs():
    bad = [
        "",                                            # empty
        "not-a-uuid",
        "6ba7b8109dad11d180b400c04fd430c8",            # no hyphens
        "6ba7b810-9dad-11d1-80b4-00c04fd430c",         # last group short
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8a",       # last group long
        "6ba7b810-9dad-11d1-80b4-00c04fd430g8",        # non-hex char
        "6ba7b810-9dad-11d1-80b4_00c04fd430c8",        # wrong separator
        " 6ba7b810-9dad-11d1-80b4-00c04fd430c8",       # leading whitespace
        "6ba7b810-9dad-11d1-80b4-00c04fd430c8 ",       # trailing whitespace
        "6ba7-b8109dad-11d1-80b4-00c04fd430c8",        # regrouped
        "{6ba7b810-9dad-11d1-80b4-00c04fd430c8",       # unbalanced brace
    ]
    for text in bad:
        with pytest.raises(UUIDError):
            parse(text)
    with pytest.raises(UUIDError):
        parse(12345)  # not a string


def test_format_rejects_wrong_length():
    with pytest.raises(UUIDError):
        format_uuid(b"\x00" * 15)
    with pytest.raises(UUIDError):
        format_uuid(b"\x00" * 17)
    with pytest.raises(UUIDError):
        format_uuid("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # str, not bytes


# --- generation behaviour ---------------------------------------------------

def test_uuid5_is_deterministic_and_name_sensitive():
    a = uuid5(NAMESPACE_DNS, "www.example.com")
    b = uuid5(NAMESPACE_DNS, "www.example.com")
    c = uuid5(NAMESPACE_DNS, "www.example.org")
    d = uuid5(NAMESPACE_URL, "www.example.com")
    assert a == b          # same inputs -> same UUID
    assert a != c          # different name -> different UUID
    assert a != d          # different namespace -> different UUID


def test_str_name_is_utf8_of_bytes_name():
    # The str convention is UTF-8: bytes input must agree with str input.
    assert uuid5(NAMESPACE_DNS, "blåbær") == \
        uuid5(NAMESPACE_DNS, "blåbær".encode("utf-8"))
    assert uuid3(NAMESPACE_OID, b"\x00\xff\x10") == \
        uuid3(NAMESPACE_OID, b"\x00\xff\x10")


def test_namespace_accepts_raw_bytes_and_any_parse_form():
    raw = parse(NAMESPACE_DNS)
    expected = uuid5(NAMESPACE_DNS, "x")
    assert uuid5(raw, "x") == expected
    assert uuid5("urn:uuid:" + NAMESPACE_DNS, "x") == expected
    assert uuid5(NAMESPACE_DNS.upper(), "x") == expected


def test_generated_uuids_have_correct_bits():
    for name in ("", "x", "www.example.com"):
        for fn, ver in ((uuid3, 3), (uuid5, 5)):
            raw = parse(fn(NAMESPACE_DNS, name))
            assert raw[6] >> 4 == ver          # version nibble, octet 6
            assert raw[8] & 0xC0 == 0x80       # variant bits 0b10, octet 8
            assert version(raw) == ver
            assert variant(raw) == "rfc9562"


def test_generation_rejects_bad_inputs():
    with pytest.raises(UUIDError):
        uuid5("not-a-uuid", "name")
    with pytest.raises(UUIDError):
        uuid5(b"\x00" * 15, "name")            # namespace not 16 bytes
    with pytest.raises(UUIDError):
        uuid5(NAMESPACE_DNS, 42)               # name neither str nor bytes


# --- variant classification --------------------------------------------------

def test_variant_table_boundaries():
    # Build 16-byte UUIDs whose octet 8 exercises each RFC 9562 4.1 range.
    def with_octet8(value):
        return bytes([0] * 8 + [value] + [0] * 7)

    assert variant(with_octet8(0x00)) == "ncs"        # 0xxx
    assert variant(with_octet8(0x7F)) == "ncs"
    assert variant(with_octet8(0x80)) == "rfc9562"    # 10xx
    assert variant(with_octet8(0xBF)) == "rfc9562"
    assert variant(with_octet8(0xC0)) == "microsoft"  # 110x
    assert variant(with_octet8(0xDF)) == "microsoft"
    assert variant(with_octet8(0xE0)) == "future"     # 111x
    assert variant(with_octet8(0xFF)) == "future"


def test_variant_agrees_with_stdlib():
    mapping = {
        stdlib_uuid.RESERVED_NCS: "ncs",
        stdlib_uuid.RFC_4122: "rfc9562",
        stdlib_uuid.RESERVED_MICROSOFT: "microsoft",
        stdlib_uuid.RESERVED_FUTURE: "future",
    }
    for octet8 in range(0, 256, 7):
        raw = bytes([0] * 8 + [octet8] + [0] * 7)
        std = stdlib_uuid.UUID(bytes=raw)
        assert variant(raw) == mapping[std.variant]
        # version semantics mirror stdlib: None unless RFC variant.
        assert version(raw) == std.version
