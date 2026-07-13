# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-CHACHA20-001 — the from-scratch ChaCha20 reproduces
the published RFC 8439 reference vectors byte-exactly.

Every expected value below is transcribed from RFC 8439 itself (the quarter
round of section 2.1.1, the block-function keystream of section 2.3.2, the
Appendix A.1 all-zero keystream block, and the section 2.4.2 "sunscreen"
ciphertext) — the module's output is never its own oracle. Round-trip and
counter-overflow behaviour are exercised on top. Deterministic: same artifact
on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from chacha20 import (  # noqa: E402
    ChaCha20Error, chacha20_block, chacha20_decrypt, chacha20_encrypt,
    quarter_round,
)
from _util import emit  # noqa: E402

# ── RFC 8439 section 2.1.1: the quarter-round test vector ────────────────────
QR_IN = (0x11111111, 0x01020304, 0x9B8D6F43, 0x01234567)
QR_OUT = (0xEA2A92F4, 0xCB1CF8CE, 0x4581472E, 0x5881C4BB)

# ── RFC 8439 section 2.3.2: block function ───────────────────────────────────
# key = 00 01 02 ... 1f, nonce = 00:00:00:09:00:00:00:4a:00:00:00:00, ctr = 1.
BLOCK_KEY = bytes(range(32))
BLOCK_NONCE = bytes.fromhex("000000090000004a00000000")
BLOCK_COUNTER = 1
BLOCK_KEYSTREAM = bytes.fromhex(
    "10f1e7e4d13b5915500fdd1fa32071c4"
    "c7d1f4c733c068030422aa9ac3d46c4e"
    "d2826446079faa0914c2d705d98b02a2"
    "b5129cd1de164eb9cbd083e8a2503c4e"
)

# ── RFC 8439 Appendix A.1 test vector #1: all-zero key/nonce, counter 0 ──────
A1_KEYSTREAM = bytes.fromhex(
    "76b8e0ada0f13d90405d6ae55386bd28"
    "bdd219b8a08ded1aa836efcc8b770dc7"
    "da41597c5157488d7724e03fb8d84a37"
    "6a43b8f41518a11cc387b669b2ee6586"
)

# ── RFC 8439 section 2.4.2: the "sunscreen" encryption example ───────────────
# key = 00 01 02 ... 1f, nonce = 00:00:00:00:00:00:00:4a:00:00:00:00, ctr = 1.
SUN_KEY = bytes(range(32))
SUN_NONCE = bytes.fromhex("000000000000004a00000000")
SUN_COUNTER = 1
SUN_PLAINTEXT = (
    b"Ladies and Gentlemen of the class of '99: If I could offer you "
    b"only one tip for the future, sunscreen would be it."
)
SUN_CIPHERTEXT = bytes.fromhex(
    "6e2e359a2568f98041ba0728dd0d6981"
    "e97e7aec1d4360c20a27afccfd9fae0b"
    "f91b65c5524733ab8f593dabcd62b357"
    "1639d624e65152ab8f530c359f0861d8"
    "07ca0dbf500d6a6156a38e088a22b65e"
    "52bc514d16ccf806818ce91ab7793736"
    "5af90bbf74a35be6b40b8eedf2785e42"
    "874d"
)

# Round-trip battery: (counter, message) pairs of varied lengths incl. empty,
# sub-block, exact-block and multi-block messages.
ROUNDTRIP_CASES = [
    (0, b""),
    (0, b"a"),
    (1, b"claim-oriented programming"),
    (7, bytes(64)),
    (2, bytes(range(256)) * 2),
    (0, b"x" * 63),
    (0, b"y" * 65),
]


def run() -> dict:
    vectors = []

    got_qr = quarter_round(*QR_IN)
    vectors.append({"vector": "rfc8439 s2.1.1 quarter round",
                    "ok": got_qr == QR_OUT})

    got_block = chacha20_block(BLOCK_KEY, BLOCK_COUNTER, BLOCK_NONCE)
    vectors.append({"vector": "rfc8439 s2.3.2 block function keystream",
                    "ok": got_block == BLOCK_KEYSTREAM})

    got_a1 = chacha20_block(bytes(32), 0, bytes(12))
    vectors.append({"vector": "rfc8439 A.1 #1 all-zero keystream block",
                    "ok": got_a1 == A1_KEYSTREAM})

    got_sun = chacha20_encrypt(SUN_KEY, SUN_COUNTER, SUN_NONCE, SUN_PLAINTEXT)
    vectors.append({"vector": "rfc8439 s2.4.2 sunscreen ciphertext",
                    "ok": got_sun == SUN_CIPHERTEXT})

    matched = sum(1 for v in vectors if v["ok"])

    roundtrips_ok = 0
    for counter, msg in ROUNDTRIP_CASES:
        ct = chacha20_encrypt(SUN_KEY, counter, SUN_NONCE, msg)
        if chacha20_decrypt(SUN_KEY, counter, SUN_NONCE, ct) == msg \
                and (len(msg) == 0 or ct != msg):
            roundtrips_ok += 1

    # Fail-closed checks: bad key/nonce/counter and counter overflow reject.
    rejects = 0
    for bad in (lambda: chacha20_block(bytes(31), 0, bytes(12)),
                lambda: chacha20_block(bytes(32), 0, bytes(8)),
                lambda: chacha20_block(bytes(32), -1, bytes(12)),
                lambda: chacha20_block(bytes(32), 2 ** 32, bytes(12)),
                lambda: chacha20_encrypt(bytes(32), 2 ** 32 - 1, bytes(12),
                                         bytes(65))):
        try:
            bad()
        except ChaCha20Error:
            rejects += 1

    return {
        "schema": "claimlib_evidence_v1",
        "module": "chacha20",
        "reference_vectors": len(vectors),
        "reference_vectors_matched": matched,
        "mismatches": len(vectors) - matched,
        "roundtrips": len(ROUNDTRIP_CASES),
        "roundtrips_ok": roundtrips_ok,
        "reject_cases": 5,
        "rejects_ok": rejects,
        "vectors": vectors,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "chacha20.json", obj,
         script="python3 claimlib/modules/chacha20/evidence.py")
    # claim:CLAIM-LIB-CHACHA20-001 reference_vectors_matched
    # All 4 published RFC 8439 vectors reproduce byte-exactly, so
    # reference_vectors_matched = 4 and mismatches = 0.
    print(f"chacha20: {obj['reference_vectors_matched']}/"
          f"{obj['reference_vectors']} RFC 8439 vectors matched, "
          f"{obj['roundtrips_ok']}/{obj['roundtrips']} round-trips, "
          f"{obj['rejects_ok']}/{obj['reject_cases']} rejects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
