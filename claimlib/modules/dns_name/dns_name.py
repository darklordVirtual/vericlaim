# SPDX-License-Identifier: Apache-2.0
"""DNS hostname (LDH) validation — a reusable, stdlib-only building block.

A pre-verified code artifact from the VeriClaim claim library. The property
that makes it trustworthy — that it classifies a fixed battery of
independently justified valid/invalid names correctly and reproduces the
RFC 1035 wire-length arithmetic — is registered as a claim and proven by a
committed evidence artifact; vendoring this module carries that claim (and
its caveat) with it.

Rules implemented (the classic "LDH hostname" profile):

* RFC 1035 section 2.3.4 size limits: labels are 1..63 octets; and per
  section 3.1 the total wire-format length of a name (label octets plus
  label length octets, including the root's zero-length octet) is at most
  255 octets — which caps the dotted presentation form (without trailing
  dot) at 253 characters.
* RFC 1035 section 2.3.1 preferred name syntax (letters, digits, hyphen;
  no leading or trailing hyphen in a label), with the RFC 1123 section 2.1
  relaxation that the FIRST character of a label may be a digit.
* Trailing-dot handling: one trailing dot marks a fully-qualified name
  rooted at the DNS root ("example.com.") and is accepted and stripped.
* RFC 4343 case-insensitive comparison: only ASCII 0x41-0x5A / 0x61-0x7A
  are folded; DNS names compare equal regardless of ASCII letter case.

Wire-format arithmetic (RFC 1035 section 3.1): each label is encoded as a
one-octet length followed by the label octets, and the name is terminated
by the root's zero length octet. For a name of N labels whose presentation
form (no trailing dot) has P characters, the wire form has
P - (N-1) label octets + N length octets + 1 root octet = P + 2 octets.
Hence wire <= 255  <=>  presentation <= 253.

Public API
----------
    is_label(label: str) -> bool        # one LDH label, 1..63 octets
    is_hostname(name: str) -> bool      # full name, trailing dot allowed
    validate(name: str) -> dict         # labels/fqdn/lengths, raises on bad
    wire_length(name: str) -> int       # RFC 1035 s3.1 encoded octet count
    normalize(name: str) -> str         # ASCII-lowercase, trailing dot gone
    equal(a: str, b: str) -> bool       # RFC 4343 case-insensitive compare

    >>> is_hostname("example.com.")
    True
    >>> wire_length("example.com")
    13
    >>> equal("ExAmPle.COM.", "example.com")
    True
"""
from __future__ import annotations

MAX_LABEL_OCTETS = 63          # RFC 1035 s2.3.4: "labels 63 octets or less"
MAX_NAME_WIRE_OCTETS = 255     # RFC 1035 s2.3.4 / s3.1 (wire format)
MAX_NAME_PRESENTATION = 253    # derived: wire = presentation + 2 (see above)

_LETTERS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
_DIGITS = frozenset("0123456789")
_LET_DIG = _LETTERS | _DIGITS
_LDH = _LET_DIG | {"-"}


class DNSNameError(ValueError):
    """The input is not a syntactically valid LDH hostname."""


def _require_str(value: object, what: str) -> str:
    if not isinstance(value, str):
        raise DNSNameError(f"expected {what} as str, got {type(value).__name__}")
    return value


def is_label(label: str) -> bool:
    """True iff *label* is one valid LDH label (1..63 octets).

    RFC 1035 s2.3.1 grammar with the RFC 1123 s2.1 relaxation: characters
    are ASCII letters, digits and hyphen; the first character may be a
    letter or a digit (not a hyphen); the last character must be a letter
    or a digit. All-ASCII only — every character is one octet.
    """
    _require_str(label, "a label")
    if not 1 <= len(label) <= MAX_LABEL_OCTETS:
        return False
    if label[0] not in _LET_DIG:       # RFC 1123: letter OR digit first
        return False
    if label[-1] not in _LET_DIG:      # must end with let-dig (no hyphen)
        return False
    return all(ch in _LDH for ch in label)


def _split(name: str) -> tuple[list[str], bool]:
    """Split *name* into labels; strip one trailing (root) dot.

    Returns (labels, fqdn). Raises DNSNameError for the empty name, the
    bare root ".", and any empty label (consecutive dots / leading dot).
    """
    _require_str(name, "a hostname")
    if name == "":
        raise DNSNameError("empty name")
    fqdn = name.endswith(".")
    if fqdn:
        name = name[:-1]               # "example.com." -> "example.com"
        if name == "":
            raise DNSNameError("the bare root '.' is not a hostname")
    labels = name.split(".")
    if any(lab == "" for lab in labels):
        raise DNSNameError(f"empty label in {name!r}")
    return labels, fqdn


def validate(name: str) -> dict:
    """Validate *name* and return its parts; raise DNSNameError if invalid.

    Returns {"labels", "fqdn", "presentation_length", "wire_length"} where
    presentation_length is measured WITHOUT the trailing dot and
    wire_length is the RFC 1035 s3.1 encoded size (label octets + length
    octets + terminating zero octet).
    """
    labels, fqdn = _split(name)
    for lab in labels:
        if not is_label(lab):
            raise DNSNameError(f"invalid label {lab!r} in {name!r}")
    # RFC 1035 s3.1: sum of label octets and label length octets <= 255.
    wire = sum(len(lab) + 1 for lab in labels) + 1   # +1 = root zero octet
    if wire > MAX_NAME_WIRE_OCTETS:
        raise DNSNameError(
            f"name is {wire} octets on the wire (> {MAX_NAME_WIRE_OCTETS})")
    presentation = sum(len(lab) for lab in labels) + len(labels) - 1
    return {
        "labels": labels,
        "fqdn": fqdn,
        "presentation_length": presentation,
        "wire_length": wire,
    }


def is_hostname(name: str) -> bool:
    """True iff *name* is a valid LDH hostname (trailing root dot allowed)."""
    _require_str(name, "a hostname")
    try:
        validate(name)
    except DNSNameError:
        return False
    return True


def wire_length(name: str) -> int:
    """RFC 1035 s3.1 wire-format octet count of *name* (validates first)."""
    return validate(name)["wire_length"]


def _fold_ascii(s: str) -> str:
    """Lowercase ONLY ASCII A-Z (0x41-0x5A), per RFC 4343."""
    return "".join(
        chr(ord(ch) + 32) if "A" <= ch <= "Z" else ch for ch in s)


def normalize(name: str) -> str:
    """Canonical comparison form: validated, ASCII-lowercased (RFC 4343),
    without the trailing root dot."""
    labels = validate(name)["labels"]
    return _fold_ascii(".".join(labels))


def equal(a: str, b: str) -> bool:
    """RFC 4343 case-insensitive name equality (trailing dot insignificant).

    Both names must be valid LDH hostnames; raises DNSNameError otherwise.
    """
    return normalize(a) == normalize(b)
