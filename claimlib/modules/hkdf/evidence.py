# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-HKDF-001 -- HKDF reproduces the published RFC 5869
SHA-256 test vectors exactly.

The RFC 5869 Appendix A test vectors are the INDEPENDENTLY KNOWN truth: for each
case the evidence checks both the extracted PRK and the expanded OKM against the
hex written verbatim from the RFC (not produced by this module). Covered:
Test Case 1 (basic), Test Case 2 (longer inputs, L=82), and Test Case 3
(zero-length salt and info). Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (hkdf.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from hkdf import extract, expand, hkdf  # noqa: E402
from _util import emit  # noqa: E402

# RFC 5869 Appendix A (SHA-256). Each: ikm, salt, info, length, PRK, OKM.
VECTORS = [
    {  # Test Case 1
        "ikm": bytes.fromhex("0b" * 22),
        "salt": bytes.fromhex("000102030405060708090a0b0c"),
        "info": bytes.fromhex("f0f1f2f3f4f5f6f7f8f9"),
        "length": 42,
        "prk": "077709362c2e32df0ddc3f0dc47bba63"
               "90b6c73bb50f9c3122ec844ad7c2b3e5",
        "okm": "3cb25f25faacd57a90434f64d0362f2a"
               "2d2d0a90cf1a5a4c5db02d56ecc4c5bf"
               "34007208d5b887185865",
    },
    {  # Test Case 2 (longer inputs)
        "ikm": bytes(range(0x00, 0x50)),
        "salt": bytes(range(0x60, 0xb0)),
        "info": bytes(range(0xb0, 0x100)),
        "length": 82,
        "prk": "06a6b88c5853361a06104c9ceb35b45c"
               "ef760014904671014a193f40c15fc244",
        "okm": "b11e398dc80327a1c8e7f78c596a4934"
               "4f012eda2d4efad8a050cc4c19afa97c"
               "59045a99cac7827271cb41c65e590e09"
               "da3275600c2f09b8367793a9aca3db71"
               "cc30c58179ec3e87c14c01d5c1f3434f"
               "1d87",
    },
    {  # Test Case 3 (zero-length salt / info)
        "ikm": bytes.fromhex("0b" * 22),
        "salt": b"",
        "info": b"",
        "length": 42,
        "prk": "19ef24a32c717b167f33a91d6f648bdf"
               "96596776afdb6377ac434c1c293ccb04",
        "okm": "8da4e775a563c18f715f802a063c5a31"
               "b8a11f5c5ee1879ec3454e5f3c738d2d"
               "9d201395faa4b61a96c8",
    },
]


def run() -> dict:
    checks = 0
    matched = 0
    rows = []
    for i, v in enumerate(VECTORS, start=1):
        prk = extract(v["salt"], v["ikm"])
        okm = hkdf(v["salt"], v["ikm"], v["info"], v["length"])
        prk_ok = (prk.hex() == v["prk"])
        okm_ok = (okm.hex() == v["okm"])
        # expand(PRK) must equal the one-shot hkdf too.
        expand_ok = (expand(prk, v["info"], v["length"]).hex() == v["okm"])
        for ok in (prk_ok, okm_ok, expand_ok):
            checks += 1
            matched += int(ok)
        rows.append({"case": i, "prk_ok": prk_ok, "okm_ok": okm_ok, "expand_ok": expand_ok})

    return {
        "schema": "claimlib_hkdf_v1",
        "module": "hkdf",
        "n_vectors": len(VECTORS),
        "checks": checks,
        "reference_vectors_matched": matched,
        "mismatches": checks - matched,
        "cases": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "hkdf.json", obj,
         script="python3 claimlib/modules/hkdf/evidence.py")
    # claim:CLAIM-LIB-HKDF-001 reference_vectors_matched
    # All 3 RFC 5869 cases match on PRK, OKM and the expand step, so
    # reference_vectors_matched = 9 and mismatches = 0.
    print(f"hkdf: {obj['reference_vectors_matched']}/{obj['checks']} RFC 5869 "
          f"checks reproduced ({obj['mismatches']} mismatches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
