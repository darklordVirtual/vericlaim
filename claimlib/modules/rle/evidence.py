# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-RLE-001 — the byte RLE codec round-trips losslessly.

Runs the reusable ``rle`` module over a fixed corpus of diverse byte strings
(long runs, sparse spikes, deterministic pseudo-random noise, structured text,
and the empty string) and checks that ``decode(encode(x)) == x`` for every
case. The pass criterion is independent of the codec: it is exact byte
equality against the ORIGINAL input, so a buggy codec cannot inflate the count.
Deterministic: the pseudo-random cases are derived from a fixed SHA-256 stream,
so the artifact is byte-identical on every run.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (rle.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from rle import encode, decode  # noqa: E402
from _util import emit  # noqa: E402


def _prng_bytes(seed: str, n: int) -> bytes:
    """Deterministic pseudo-random byte string of length *n* from *seed*.

    Uses a SHA-256 keystream (counter mode over the seed) so the corpus is
    fixed forever and needs no RNG state — reproducible across machines and
    Python versions.
    """
    out = bytearray()
    counter = 0
    while len(out) < n:
        block = hashlib.sha256(f"{seed}:{counter}".encode("utf-8")).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:n])


# A fixed, diverse reference corpus. Each entry is an independent input; the
# expected round-trip result is the input itself (byte equality), which is the
# ground truth RLE must satisfy regardless of implementation.
CORPUS = [
    b"",                                   # empty
    b"A",                                  # single byte
    b"\x00",                               # single NUL
    b"A" * 300,                            # run longer than one count byte (255)
    b"\xff" * 255,                         # run of exactly the max count
    b"\xff" * 256,                         # one past the max count (splits)
    b"aaaabbbc",                           # short mixed runs
    b"abcdefghijklmnopqrstuvwxyz",         # no runs (worst case: expands)
    b"\x00" * 1000 + b"\x01" + b"\x00" * 1000,  # sparse spike in zeros
    bytes(range(256)),                     # every byte value once
    bytes(range(256)) * 4,                 # every byte value, repeated blocks
    b"the quick brown fox jumps over the lazy dog. " * 8,  # structured text
    _prng_bytes("vericlaim-rle-noise-1", 4096),   # pseudo-random noise
    _prng_bytes("vericlaim-rle-noise-2", 777),    # odd-length noise
    _prng_bytes("vericlaim-rle-mixed", 2048),     # more noise
]


def run() -> dict:
    cases = []
    lossless = 0
    total_in = 0
    total_encoded = 0
    for idx, original in enumerate(CORPUS):
        encoded = encode(original)
        decoded = decode(encoded)
        ok = (decoded == original)
        lossless += int(ok)
        total_in += len(original)
        total_encoded += len(encoded)
        cases.append({
            "index": idx,
            "in_len": len(original),
            "encoded_len": len(encoded),
            "roundtrip_ok": ok,
        })
    # RLE can expand incompressible data, so total_encoded may exceed total_in;
    # guard against division by zero when the corpus is degenerate.
    ratio = round(total_in / total_encoded, 4) if total_encoded else 0.0
    return {
        "schema": "claimlib_rle_v1",
        "module": "rle",
        "n_cases": len(CORPUS),
        "roundtrip_lossless": lossless,
        "overall_ratio": ratio,
        "total_in_bytes": total_in,
        "total_encoded_bytes": total_encoded,
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "rle.json", obj,
         script="python3 claimlib/modules/rle/evidence.py")
    # claim:CLAIM-LIB-RLE-001 roundtrip_lossless
    # All 15 corpus cases satisfy decode(encode(x)) == x, so
    # roundtrip_lossless = 15 and equals n_cases (15) with zero failures.
    print(f"rle: {obj['roundtrip_lossless']}/{obj['n_cases']} cases round-trip "
          f"losslessly; overall_ratio={obj['overall_ratio']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
