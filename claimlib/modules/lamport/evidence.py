# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-LAMPORT-001 -- every valid Lamport signature verifies and
every tampering is rejected.

The correctness and unforgeability properties are self-verifying and need no
external oracle: over a fixed battery of (seed, message) pairs the evidence checks
that verify(m, sign(m, sk), pk) is True; that verifying against a DIFFERENT message
fails (a signature does not carry over); that flipping one byte of one signature
element fails; and that verifying under a different key pair fails. The count of
accepted forgeries must be 0. Deterministic (keys derived from the seed).
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (lamport.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from lamport import keygen, sign, verify  # noqa: E402
from _util import emit  # noqa: E402

CASES = [
    (b"seed-0", b""),
    (b"seed-1", b"hello world"),
    (b"seed-2", b"The quick brown fox jumps over the lazy dog"),
    (b"seed-3", bytes(range(256))),
    (b"seed-4", b"transfer 100 to alice"),
]


def run() -> dict:
    valid_ok = 0
    tamper_msg_detected = 0
    tamper_sig_detected = 0
    wrongkey_detected = 0
    forgeries_accepted = 0

    other_sk, other_pk = keygen(b"a-different-key")
    for seed, message in CASES:
        sk, pk = keygen(seed)
        sig = sign(message, sk)

        valid_ok += int(verify(message, sig, pk) is True)

        # Tamper the message: the same signature must not verify a changed message.
        altered = message + b"!"
        if verify(altered, sig, pk):
            forgeries_accepted += 1
        else:
            tamper_msg_detected += 1

        # Tamper one signature element (flip a byte).
        bad_sig = list(sig)
        bad_sig[0] = bytes([bad_sig[0][0] ^ 0x01]) + bad_sig[0][1:]
        if verify(message, bad_sig, pk):
            forgeries_accepted += 1
        else:
            tamper_sig_detected += 1

        # Verify under a different public key.
        if verify(message, sig, other_pk):
            forgeries_accepted += 1
        else:
            wrongkey_detected += 1

    return {
        "schema": "claimlib_lamport_v1",
        "module": "lamport",
        "n_cases": len(CASES),
        "valid_ok": valid_ok,
        "tamper_msg_detected": tamper_msg_detected,
        "tamper_sig_detected": tamper_sig_detected,
        "wrongkey_detected": wrongkey_detected,
        "forgeries_accepted": forgeries_accepted,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "lamport.json", obj,
         script="python3 claimlib/modules/lamport/evidence.py")
    # claim:CLAIM-LIB-LAMPORT-001 valid_ok
    # Every valid signature verifies (valid_ok = 5) and all 15 tampering attempts
    # are rejected, so forgeries_accepted = 0 (n_cases = 5).
    print(f"lamport: valid_ok {obj['valid_ok']}/{obj['n_cases']}, "
          f"forgeries_accepted {obj['forgeries_accepted']} "
          f"(msg {obj['tamper_msg_detected']}, sig {obj['tamper_sig_detected']}, "
          f"key {obj['wrongkey_detected']} detected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
