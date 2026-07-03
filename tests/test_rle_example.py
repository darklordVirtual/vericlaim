# SPDX-License-Identifier: Apache-2.0
"""Tests for the RLE example — and that its committed artifact stays honest."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "examples" / "rle" / "src"))

from rle import decode, encode, ratio  # noqa: E402


def test_roundtrip_lossless_on_varied_inputs():
    for data in [b"", b"a", b"ab", b"a" * 300, bytes(range(256)),
                 b"xxxxyyyyzzzz" * 20, b"\x00" * 1000]:
        assert decode(encode(data)) == data


def test_ratio_ge_one_on_runny_data():
    assert ratio(b"a" * 100) > 1.0


def test_committed_artifact_matches_recomputation():
    """The claimed numbers must equal a fresh run — no stale artifact."""
    art = json.loads(
        (ROOT / "examples" / "rle" / "artifacts" / "rle_bench.json")
        .read_text(encoding="utf-8"))
    # Recompute overall ratio from the same corpus the bench uses.
    sys.path.insert(0, str(ROOT / "examples" / "rle"))
    import bench  # noqa: E402

    total_in = sum(len(d) for d in bench.CORPUS.values())
    total_enc = sum(len(encode(d)) for d in bench.CORPUS.values())
    assert round(total_in / total_enc, 4) == art["overall_ratio"]
    assert art["n_roundtrip_lossless"] == art["n_files"]
