# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``dns_name`` library.

Reference values are independently known from the RFC texts:
RFC 1035 s2.3.4 (labels <= 63 octets, names <= 255 wire octets),
RFC 1035 s3.1 (wire encoding: length-prefixed labels + zero root octet),
RFC 1035 s2.3.1 grammar as relaxed by RFC 1123 s2.1 (digit-start labels),
and RFC 4343 (ASCII-only case-insensitive comparison).
"""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "dns_name"))

from dns_name import (  # noqa: E402
    DNSNameError,
    MAX_LABEL_OCTETS,
    MAX_NAME_PRESENTATION,
    MAX_NAME_WIRE_OCTETS,
    equal,
    is_hostname,
    is_label,
    normalize,
    validate,
    wire_length,
)

# 63.63.63.61-octet labels -> presentation 253 chars, wire 255 octets.
NAME_253 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 61])
NAME_254 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 62])


# ---------------------------------------------------------------- labels

def test_label_63_octets_passes_64_fails():
    assert is_label("a" * 63) is True     # RFC 1035 s2.3.4 boundary
    assert is_label("a" * 64) is False


def test_label_hyphen_edges():
    assert is_label("a-b") is True
    assert is_label("a--b") is True       # double interior hyphen is legal
    assert is_label("-a") is False        # no leading hyphen
    assert is_label("a-") is False        # must end with letter or digit
    assert is_label("-") is False


def test_label_digit_start_allowed_rfc1123():
    assert is_label("3com") is True
    assert is_label("0a") is True
    assert is_label("999") is True        # all-numeric is syntactically LDH


def test_label_rejects_non_ldh_characters():
    for bad in ("", "_x", "a b", "a.b", "café", "a\x00b", "ａｂｃ"):
        assert is_label(bad) is False


# ------------------------------------------------------------ name limits

def test_253_char_presentation_passes_254_fails():
    assert len(NAME_253) == MAX_NAME_PRESENTATION == 253
    assert is_hostname(NAME_253) is True
    assert len(NAME_254) == 254
    assert is_hostname(NAME_254) is False


def test_wire_arithmetic_presentation_plus_two():
    # RFC 1035 s3.1: wire = presentation + 2 (N length octets replace the
    # N-1 dots and add one, plus the root's zero octet).
    for name in ("a", "example.com", NAME_253):
        info = validate(name)
        assert info["wire_length"] == info["presentation_length"] + 2
    assert wire_length(NAME_253) == MAX_NAME_WIRE_OCTETS == 255


def test_known_wire_lengths():
    assert wire_length("a") == 3                    # 1+1 + 1
    assert wire_length("example.com") == 13         # 1+7 + 1+3 + 1
    assert wire_length("www.example.com") == 17     # 1+3 + 1+7 + 1+3 + 1
    assert wire_length("a" * 63) == 65              # 1+63 + 1


def test_max_label_count_boundary():
    # 127 one-octet labels: wire 127*2 + 1 = 255 -> legal;
    # 128 labels: wire 257 -> illegal.
    assert is_hostname(".".join(["a"] * 127)) is True
    assert is_hostname(".".join(["a"] * 128)) is False


# ------------------------------------------------------- dots and labels

def test_trailing_dot_fqdn_handling():
    assert is_hostname("example.com.") is True
    assert validate("example.com.")["fqdn"] is True
    assert validate("example.com")["fqdn"] is False
    # The trailing dot is not an extra label: same labels, same wire form.
    assert validate("example.com.")["labels"] == ["example", "com"]
    assert wire_length("example.com.") == wire_length("example.com")


def test_empty_labels_and_root_rejected():
    for bad in ("", ".", "..", "a..b", ".example.com", "example.com.."):
        assert is_hostname(bad) is False


def test_validate_raises_with_reason():
    with pytest.raises(DNSNameError):
        validate("-a.example")
    with pytest.raises(DNSNameError):
        validate(NAME_254)
    with pytest.raises(DNSNameError):
        validate("")


# --------------------------------------------------------- case / RFC 4343

def test_equal_is_ascii_case_insensitive():
    assert equal("ExAmPle.COM", "example.com") is True
    assert equal("EXAMPLE.COM.", "example.com") is True   # FQDN dot ignored
    assert equal("example.com", "example.org") is False
    assert equal("A" * 63, "a" * 63) is True


def test_normalize_lowercases_and_strips_root_dot():
    assert normalize("WWW.Example.ORG.") == "www.example.org"
    assert normalize("a-B.c") == "a-b.c"


def test_equal_requires_valid_names():
    with pytest.raises(DNSNameError):
        equal("example.com", "-bad.example")
    with pytest.raises(DNSNameError):
        equal("", "example.com")


# ------------------------------------------------------------- adversarial

def test_rejects_non_string_input():
    with pytest.raises(DNSNameError):
        is_hostname(42)
    with pytest.raises(DNSNameError):
        is_label(None)
    with pytest.raises(DNSNameError):
        validate(b"example.com")


def test_rejects_unicode_lookalikes():
    # Fullwidth letters, dot lookalikes and IDN must all fail (only the
    # punycoded A-label form, e.g. xn--..., is LDH-valid).
    assert is_hostname("ｅｘａｍｐｌｅ.com") is False
    assert is_hostname("bücher.example") is False
    assert is_hostname("example。com") is False
    assert is_hostname("xn--bcher-kva.example") is True


def test_underscore_service_labels_rejected():
    assert is_hostname("_dmarc.example.com") is False
    assert is_hostname("_sip._tcp.example.com") is False


def test_all_numeric_name_is_syntactically_valid():
    # RFC 1123 s2.1 allows digit-start labels, so "1.2.3.4" is LDH-valid
    # syntax; distinguishing it from an IPv4 literal is caller policy
    # (RFC 1123 tells resolvers to check dotted-decimal shape first).
    assert is_hostname("1.2.3.4") is True


def test_max_label_constant_matches_rfc():
    assert MAX_LABEL_OCTETS == 63
