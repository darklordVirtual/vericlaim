# SPDX-License-Identifier: Apache-2.0
"""Regenerate the RLE benchmark artifact.

This is the *evidence producer* for the example's claims. Run it to (re)create
examples/rle/artifacts/rle_bench.json; the gate then verifies the docs match
this artifact. Deterministic — no randomness, no network.

    python examples/rle/bench.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, for `import vericlaim`
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from rle import decode, encode, ratio  # noqa: E402

# A small, fixed corpus with the run structure RLE is good at.
CORPUS: dict[str, bytes] = {
    "runs":     b"a" * 100 + b"b" * 100 + b"c" * 55,
    "banner":   (b"#" * 40 + b"\n") * 6,
    "sparse":   b"\x00" * 500,
    "mixed":    b"xxxxyyyyzzzz" * 20,
}


def main() -> int:
    per_file = {}
    n_roundtrip_ok = 0
    total_in = total_enc = 0
    for name, data in CORPUS.items():
        enc = encode(data)
        ok = decode(enc) == data
        n_roundtrip_ok += int(ok)
        total_in += len(data)
        total_enc += len(enc)
        per_file[name] = {
            "bytes_in": len(data),
            "bytes_encoded": len(enc),
            "ratio": round(ratio(data), 4),
            "roundtrip_lossless": ok,
        }
    overall_ratio = round(total_in / total_enc, 4) if total_enc else 1.0
    artifact = {
        "schema": "rle_bench_v1",
        "n_files": len(CORPUS),
        "n_roundtrip_lossless": n_roundtrip_ok,
        "overall_ratio": overall_ratio,
        "per_file": per_file,
    }
    out = Path(__file__).resolve().parent / "artifacts" / "rle_bench.json"
    out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8",
                   newline="\n")
    from vericlaim.provenance import stamp
    stamp(out, script="python3 examples/rle/bench.py")
    print(f"[OK] wrote {out}")
    print(f"     overall_ratio={overall_ratio}x, "
          f"roundtrip_lossless={n_roundtrip_ok}/{len(CORPUS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
