# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-HAMMING74-001 -- Hamming(7,4) corrects EVERY single-bit
error, verified exhaustively over the complete input space.

The (data, single-bit-error) space is finite and small: 16 possible 4-bit values
x 8 error patterns (no error, plus a flip at each of the 7 codeword positions) =
128 trials. This script enumerates ALL of them: for every nibble it encodes the
codeword, applies each error pattern, decodes, and requires that the recovered
nibble equals the original AND (for the flip cases) that the reported error
position is exactly the flipped position. Because the whole space is covered,
``corrected == 128`` is a proof by enumeration, not a sample.

A second, independent check: the 16 codewords have minimum Hamming distance 3
(so any single-bit error stays closer to the true codeword than to any other).
Deterministic: same artifact on every run.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (hamming74.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from hamming74 import encode, decode  # noqa: E402
from _util import emit  # noqa: E402


def run() -> dict:
    trials = 0
    corrected = 0
    miscorrected = 0
    position_correct = 0
    for nibble in range(16):
        codeword = encode(nibble)
        # error pattern 0 = no error; 1..7 = flip that 1-indexed position.
        for error_pos in range(0, 8):
            trials += 1
            received = codeword if error_pos == 0 else codeword ^ (1 << (error_pos - 1))
            recovered, reported = decode(received)
            if recovered == nibble:
                corrected += 1
            else:
                miscorrected += 1
            if reported == error_pos:
                position_correct += 1

    # Independent property: minimum Hamming distance between the 16 codewords is 3.
    codewords = [encode(n) for n in range(16)]
    min_distance = min(
        bin(codewords[i] ^ codewords[j]).count("1")
        for i in range(16) for j in range(i + 1, 16)
    )

    return {
        "schema": "claimlib_hamming74_v1",
        "module": "hamming74",
        "n_data_values": 16,
        "n_error_patterns": 8,
        "trials": trials,
        "corrected": corrected,
        "miscorrected": miscorrected,
        "error_position_correct": position_correct,
        "min_code_distance": min_distance,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "hamming74.json", obj,
         script="python3 claimlib/modules/hamming74/evidence.py")
    # claim:CLAIM-LIB-HAMMING74-001 corrected
    # Every one of the 16 x 8 = 128 (data, single-bit-error) trials recovers the
    # original nibble, so corrected = 128 and miscorrected = 0.
    print(f"hamming74: {obj['corrected']}/{obj['trials']} trials recovered the "
          f"original nibble ({obj['miscorrected']} miscorrected), "
          f"min code distance = {obj['min_code_distance']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
