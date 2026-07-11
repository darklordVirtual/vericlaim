# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``hamming74`` library (exhaustive correctness)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "hamming74"))

from hamming74 import encode, decode, HammingError  # noqa: E402


def test_clean_round_trip_all_nibbles():
    for nibble in range(16):
        recovered, err = decode(encode(nibble))
        assert recovered == nibble
        assert err == 0


def test_corrects_every_single_bit_error():
    for nibble in range(16):
        code = encode(nibble)
        for pos in range(1, 8):
            received = code ^ (1 << (pos - 1))
            recovered, err = decode(received)
            assert recovered == nibble
            assert err == pos


def test_codewords_have_min_distance_three():
    codes = [encode(n) for n in range(16)]
    for i in range(16):
        for j in range(i + 1, 16):
            assert bin(codes[i] ^ codes[j]).count("1") >= 3


def test_rejects_out_of_range():
    with pytest.raises(HammingError):
        encode(16)
    with pytest.raises(HammingError):
        encode(-1)
    with pytest.raises(HammingError):
        decode(128)
