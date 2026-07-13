# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-DNS-NAME-001 — the DNS LDH-hostname validator
classifies a fixed battery of independently justified names correctly and
reproduces the RFC 1035 wire-length arithmetic.

Every expected value is INDEPENDENTLY KNOWN, never produced by the module:

* Label/name size limits come verbatim from RFC 1035 section 2.3.4
  ("labels 63 octets or less", "names 255 octets or less") and section 3.1
  ("the total length of a domain name (i.e., label octets and label length
  octets) is restricted to 255 octets or less").
* The 255-wire vs 253-presentation arithmetic: on the wire each of the N
  labels costs len(label) + 1 octets (one length octet each) and the root
  adds one zero length octet, while the presentation form (no trailing
  dot) has sum(len) + N - 1 characters (N-1 dots). So
  wire = presentation + 2, and wire <= 255 <=> presentation <= 253:
  a 253-character name encodes to exactly 255 octets and passes; a
  254-character name encodes to 256 octets and fails.
* Syntax expectations come from the RFC 1035 section 2.3.1 grammar (labels
  start with a letter, end with a letter or digit, interior hyphens only)
  as relaxed by RFC 1123 section 2.1 (first character may be a digit).
* Case-insensitivity expectations come from RFC 4343 (only ASCII
  0x41-0x5A / 0x61-0x7A fold).
* Wire lengths are additionally cross-checked against an independent
  byte-level encoder written here from the RFC 1035 section 3.1 definition,
  and the 63-octet label boundary against the Python stdlib's
  encodings.idna.ToASCII (which accepts ASCII labels of 1..63 octets and
  rejects empty/64+ ones) — a genuinely independent oracle.

Deterministic: fixed battery, no time/random/hash-order dependence.
"""
from __future__ import annotations

import encodings.idna as _stdlib_idna
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from dns_name import is_hostname, is_label, wire_length, equal  # noqa: E402
from _util import emit  # noqa: E402

# 63.63.63.61 labels -> presentation 63*3 + 61 + 3 dots = 253 characters,
# wire 3*(63+1) + (61+1) + 1 = 255 octets  -> the largest legal name.
NAME_253 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 61])
# Same but last label 62 octets -> presentation 254, wire 256 -> illegal.
NAME_254 = ".".join(["a" * 63, "b" * 63, "c" * 63, "d" * 62])
# 127 one-octet labels: presentation 126*2 + 1 = 253, wire 127*2 + 1 = 255.
MANY_LABELS_OK = ".".join(["a"] * 127)
# 128 one-octet labels: presentation 255, wire 257 -> illegal.
MANY_LABELS_BAD = ".".join(["a"] * 128)

assert len(NAME_253) == 253 and len(NAME_254) == 254
assert len(MANY_LABELS_OK) == 253 and len(MANY_LABELS_BAD) == 255

# (name, expected_valid, why). Expected labels derive from the RFC texts
# cited above, not from this module's output.
REFERENCE = [
    ("a" * 63, True, "63-octet label: RFC 1035 s2.3.4 maximum"),
    ("a" * 64, False, "64-octet label exceeds RFC 1035 s2.3.4"),
    (NAME_253, True, "253-char presentation = 255 wire octets (max legal)"),
    (NAME_254, False, "254-char presentation = 256 wire octets (> 255)"),
    (MANY_LABELS_OK, True, "127 one-octet labels: wire exactly 255"),
    (MANY_LABELS_BAD, False, "128 one-octet labels: wire 257 (> 255)"),
    ("example.com", True, "plain two-label name"),
    ("example.com.", True, "trailing dot = FQDN rooted at the DNS root"),
    (".", False, "bare root: no host labels"),
    ("", False, "empty name"),
    ("a..b", False, "empty label between dots"),
    (".example.com", False, "leading dot = empty first label"),
    ("example.com..", False, "empty label before the root dot"),
    ("a-b.example", True, "interior hyphen allowed (RFC 1035 s2.3.1)"),
    ("-a.example", False, "label must not start with a hyphen"),
    ("a-.example", False, "label must end with a letter or digit"),
    ("3com.com", True, "digit-start label allowed (RFC 1123 s2.1)"),
    ("xn--nxasmq6b.example", True, "double interior hyphen (A-label shape)"),
    ("_dmarc.example.com", False, "underscore is not an LDH character"),
    ("exa mple.com", False, "space is not an LDH character"),
    ("bücher.example", False, "non-ASCII (IDN must be punycoded first)"),
    ("a", True, "single-label host name"),
    ("A.EXAMPLE.COM", True, "uppercase ASCII letters are legal LDH"),
]

# (name, expected_wire_octets) hand-computed from RFC 1035 s3.1:
# sum over labels of (1 length octet + label octets), plus the root's
# zero length octet. e.g. "example.com" -> 1+7 + 1+3 + 1 = 13.
WIRE_CASES = [
    ("a", 3),
    ("example.com", 13),
    ("www.example.com", 17),
    ("a" * 63, 65),
    (NAME_253, 255),
    ("example.com.", 13),   # trailing root dot: same wire form
]

# RFC 4343: ASCII case is insignificant; trailing root dot is not part of
# the owner name proper, so it must not affect equality.
EQUALITY_CASES = [
    ("ExAmPle.COM", "example.com", True),
    ("EXAMPLE.COM.", "example.com", True),
    ("example.com", "example.org", False),
    ("A" * 63, "a" * 63, True),
    ("a-b.example", "A-B.EXAMPLE.", True),
]

# (label, expected_accept) for the 1..63-octet label boundary; checked
# against BOTH is_label() and the stdlib encodings.idna.ToASCII oracle.
STDLIB_LABEL_CASES = [
    ("a", True),
    ("a" * 63, True),
    ("a" * 64, False),
    ("", False),
]


def _wire_encode(name: str) -> bytes:
    """Independent RFC 1035 s3.1 encoder (length-prefixed labels + root)."""
    if name.endswith("."):
        name = name[:-1]
    out = b""
    for lab in name.split("."):
        out += bytes([len(lab)]) + lab.encode("ascii")
    return out + b"\x00"


def _stdlib_accepts(label: str) -> bool:
    try:
        _stdlib_idna.ToASCII(label)
        return True
    except UnicodeError:
        return False


def run() -> dict:
    rows = []
    correct = 0
    for name, expected, why in REFERENCE:
        got = is_hostname(name)
        ok = (got == expected)
        correct += int(ok)
        rows.append({"name": name, "expected_valid": expected,
                     "computed_valid": got, "correct": ok, "why": why})

    wire_rows = []
    wire_matched = 0
    for name, expected in WIRE_CASES:
        got = wire_length(name)
        oracle = len(_wire_encode(name))
        ok = (got == expected == oracle)
        wire_matched += int(ok)
        wire_rows.append({"name": name, "expected_octets": expected,
                          "computed_octets": got, "encoder_octets": oracle,
                          "correct": ok})

    eq_rows = []
    eq_matched = 0
    for a, b, expected in EQUALITY_CASES:
        got = equal(a, b)
        ok = (got == expected)
        eq_matched += int(ok)
        eq_rows.append({"a": a, "b": b, "expected_equal": expected,
                        "computed_equal": got, "correct": ok})

    lab_rows = []
    lab_matched = 0
    for label, expected in STDLIB_LABEL_CASES:
        got = is_label(label)
        oracle = _stdlib_accepts(label)
        ok = (got == expected == oracle)
        lab_matched += int(ok)
        lab_rows.append({"label_octets": len(label),
                         "expected_accept": expected, "computed": got,
                         "stdlib_idna": oracle, "correct": ok})

    n_cases = len(REFERENCE)
    return {
        "schema": "claimlib_dns_name_v1",
        "module": "dns_name",
        "n_cases": n_cases,
        "correct": correct,
        "mismatches": n_cases - correct,
        "wire_checks": len(WIRE_CASES),
        "wire_matched": wire_matched,
        "equality_checks": len(EQUALITY_CASES),
        "equality_matched": eq_matched,
        "stdlib_label_checks": len(STDLIB_LABEL_CASES),
        "stdlib_label_matched": lab_matched,
        "cases": rows,
        "wire_detail": wire_rows,
        "equality_detail": eq_rows,
        "stdlib_label_detail": lab_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "dns_name.json", obj,
         script="python3 claimlib/modules/dns_name/evidence.py")
    # claim:CLAIM-LIB-DNS-NAME-001 correct
    # All 23 reference names are classified correctly (correct = 23,
    # mismatches = 0); all 6 wire lengths match both the hand-derived
    # values and the independent byte encoder; all 5 RFC 4343 equality
    # cases and all 4 stdlib label-boundary cases match.
    print(f"dns_name: {obj['correct']}/{obj['n_cases']} names classified "
          f"correctly ({obj['mismatches']} mismatches); "
          f"wire {obj['wire_matched']}/{obj['wire_checks']}, "
          f"equality {obj['equality_matched']}/{obj['equality_checks']}, "
          f"stdlib label boundary "
          f"{obj['stdlib_label_matched']}/{obj['stdlib_label_checks']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
