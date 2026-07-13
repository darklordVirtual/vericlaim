# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-UUID-001 — the from-scratch UUID module reproduces
the RFC 9562 published example vectors and agrees with the independent stdlib
``uuid`` implementation over a fixed battery.

Three independent oracles, none produced by the module itself:

1. RFC 9562 Appendix A test vectors (verified against rfc-editor.org/rfc/
   rfc9562.txt): the UUIDv3 and UUIDv5 examples for the DNS namespace and
   name "www.example.com", plus the published v1/v4/v6/v7 example values
   whose version/variant fields are stated in the RFC, the four well-known
   namespace IDs of section 6.6, and the Nil/Max UUIDs of sections 5.9/5.10.
2. Python's stdlib ``uuid.uuid3`` / ``uuid.uuid5`` — a genuinely independent
   implementation — over a fixed battery of 32 (namespace, name) pairs.
3. Direct bit-placement checks: every generated UUID must carry its version
   in the high nibble of octet 6 and variant bits 0b10 in octet 8
   (RFC 9562 sections 4.1 and 4.2).

Deterministic: fixed batteries, fixed iteration order, no time/random input —
same artifact bytes on every run.
"""
from __future__ import annotations

import sys
import uuid as stdlib_uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (uuid_tools.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from uuid_tools import (  # noqa: E402
    MAX_UUID, NAMESPACE_DNS, NAMESPACE_OID, NAMESPACE_URL, NAMESPACE_X500,
    NIL_UUID, format_uuid, inspect, parse, uuid3, uuid5,
)
from _util import emit  # noqa: E402

# ---------------------------------------------------------------------------
# Oracle 1: RFC 9562 published values (Appendix A; sections 5.9, 5.10, 6.6).
# Every expected value below is transcribed from rfc-editor.org/rfc/rfc9562
# — none is produced by the module under test.
# ---------------------------------------------------------------------------

# Appendix A.2 / A.4: name-based examples for the DNS namespace and the name
# "www.example.com". The RFC also publishes the raw digests, which lets us
# check the ver/var bit-substitution independently of the hash computation:
#   MD5   = 5df418813aed051548a72f4a814cf09e            (Figure 17)
#   SHA-1 = 2ed6657de927468b55e12665a8aea6a22dee3e35    (Figure 22)
RFC_V3_EXPECTED = "5df41881-3aed-3515-88a7-2f4a814cf09e"   # Figure 18
RFC_V5_EXPECTED = "2ed6657d-e927-568b-95e1-2665a8aea6a2"   # Figure 23

# Published example values whose version/variant fields the RFC states.
# (uuid string as printed in the RFC, expected version, expected variant)
RFC_INSPECT_VECTORS = [
    ("C232AB00-9414-11EC-B3C8-9F6BDECED846", 1, "rfc9562"),  # A.1 UUIDv1
    ("919108f7-52d1-4320-9bac-f847db4148a8", 4, "rfc9562"),  # A.3 UUIDv4
    ("1EC9414C-232A-6B00-B3C8-9F6BDECED846", 6, "rfc9562"),  # A.5 UUIDv6
    ("017F22E2-79B0-7CC3-98C4-DC0C0C07398F", 7, "rfc9562"),  # A.6 UUIDv7
    # Section 6.6, Table 3: the four well-known namespace IDs are themselves
    # version-1, RFC-variant UUIDs (as published in RFC 4122 Appendix C).
    (NAMESPACE_DNS, 1, "rfc9562"),
    (NAMESPACE_URL, 1, "rfc9562"),
    (NAMESPACE_OID, 1, "rfc9562"),
    (NAMESPACE_X500, 1, "rfc9562"),
    # Sections 5.9 / 5.10: Nil (all zero bits -> NCS-range variant bits,
    # version not meaningful) and Max (all one bits -> future-range variant).
    (NIL_UUID, None, "ncs"),
    (MAX_UUID, None, "future"),
]

# ---------------------------------------------------------------------------
# Oracle 2: the stdlib uuid module over a fixed (namespace, name) battery.
# ---------------------------------------------------------------------------
STDLIB_NAMESPACES = [
    ("dns", NAMESPACE_DNS, stdlib_uuid.NAMESPACE_DNS),
    ("url", NAMESPACE_URL, stdlib_uuid.NAMESPACE_URL),
    ("oid", NAMESPACE_OID, stdlib_uuid.NAMESPACE_OID),
    ("x500", NAMESPACE_X500, stdlib_uuid.NAMESPACE_X500),
]
STDLIB_NAMES = [
    "www.example.com",
    "example.org",
    "python.org",
    "vericlaim",
    "claimlib/uuid_tools",
    "",                       # empty name is legal (hash of namespace only)
    "a",
    "blåbærsyltetøy ✓",       # non-ASCII: exercises the UTF-8 convention
]


def run() -> dict:
    # --- RFC 9562 vector battery -----------------------------------------
    rfc_rows = []

    got_v3 = uuid3(NAMESPACE_DNS, "www.example.com")
    rfc_rows.append({
        "vector": "A.2 uuid3(DNS, 'www.example.com')",
        "expected": RFC_V3_EXPECTED, "computed": got_v3,
        "correct": got_v3 == RFC_V3_EXPECTED,
    })
    got_v5 = uuid5(NAMESPACE_DNS, "www.example.com")
    rfc_rows.append({
        "vector": "A.4 uuid5(DNS, 'www.example.com')",
        "expected": RFC_V5_EXPECTED, "computed": got_v5,
        "correct": got_v5 == RFC_V5_EXPECTED,
    })

    for text, exp_version, exp_variant in RFC_INSPECT_VECTORS:
        info = inspect(text)
        round_trip = format_uuid(parse(text))
        ok = (info["version"] == exp_version
              and info["variant"] == exp_variant
              and round_trip == text.lower())
        rfc_rows.append({
            "vector": text,
            "expected": {"version": exp_version, "variant": exp_variant,
                         "canonical": text.lower()},
            "computed": {"version": info["version"],
                         "variant": info["variant"],
                         "canonical": round_trip},
            "correct": ok,
        })

    rfc_vectors = len(rfc_rows)
    rfc_vectors_matched = sum(int(r["correct"]) for r in rfc_rows)

    # --- stdlib cross-check + bit-placement battery ----------------------
    stdlib_rows = []
    stdlib_matched = 0
    bit_checks = 0
    bit_checks_ok = 0
    for ns_label, ns_str, ns_std in STDLIB_NAMESPACES:
        for name in STDLIB_NAMES:
            for ver, ours_fn, std_fn in (
                (3, uuid3, stdlib_uuid.uuid3),
                (5, uuid5, stdlib_uuid.uuid5),
            ):
                ours = ours_fn(ns_str, name)
                std = str(std_fn(ns_std, name))
                agree = ours == std
                stdlib_matched += int(agree)
                raw = parse(ours)
                version_bits_ok = (raw[6] >> 4) == ver          # RFC 9562 4.2
                variant_bits_ok = (raw[8] & 0xC0) == 0x80       # RFC 9562 4.1
                bit_checks += 2
                bit_checks_ok += int(version_bits_ok) + int(variant_bits_ok)
                stdlib_rows.append({
                    "namespace": ns_label, "name": name, "version": ver,
                    "computed": ours, "stdlib": std, "agree": agree,
                    "version_bits_ok": version_bits_ok,
                    "variant_bits_ok": variant_bits_ok,
                })
    stdlib_cross_checks = len(stdlib_rows)

    mismatches = ((rfc_vectors - rfc_vectors_matched)
                  + (stdlib_cross_checks - stdlib_matched)
                  + (bit_checks - bit_checks_ok))

    return {
        "schema": "claimlib_uuid_tools_v1",
        "module": "uuid_tools",
        "rfc_vectors": rfc_vectors,
        "rfc_vectors_matched": rfc_vectors_matched,
        "stdlib_cross_checks": stdlib_cross_checks,
        "stdlib_matched": stdlib_matched,
        "bit_checks": bit_checks,
        "bit_checks_ok": bit_checks_ok,
        "mismatches": mismatches,
        "rfc_detail": rfc_rows,
        "stdlib_detail": stdlib_rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "uuid_tools.json", obj,
         script="python3 claimlib/modules/uuid_tools/evidence.py")
    # claim:CLAIM-LIB-UUID-001 rfc_vectors_matched
    # All 12 RFC 9562 vector checks hold (rfc_vectors_matched = 12 of 12),
    # all 64 stdlib uuid3/uuid5 cross-checks agree (stdlib_matched = 64),
    # and all 128 version/variant bit-placement checks pass, mismatches = 0.
    print(f"uuid_tools: {obj['rfc_vectors_matched']}/{obj['rfc_vectors']} "
          f"RFC 9562 vectors, {obj['stdlib_matched']}/"
          f"{obj['stdlib_cross_checks']} stdlib cross-checks, "
          f"{obj['bit_checks_ok']}/{obj['bit_checks']} bit checks; "
          f"mismatches {obj['mismatches']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
