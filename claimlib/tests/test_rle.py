# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``rle`` byte run-length codec.

Assertions target CORRECTNESS on concrete cases: known-good wire-format
encodings computed by hand, round-trip inverse over edge cases (empty, single
byte, runs crossing the 255 count boundary, incompressible data), and error
handling on malformed streams.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

# Load under a UNIQUE name via importlib rather than `import rle`: the examples/
# workspace also ships a bare `rle` module, and a shared sys.modules would make
# whichever imported first win when both test suites run in one pytest process.
_PATH = Path(__file__).resolve().parents[1] / "modules" / "rle" / "rle.py"
_spec = importlib.util.spec_from_file_location("claimlib_rle", _PATH)
rle = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rle)


def test_encode_known_wire_format():
    # Hand-computed: 'aaaa'->(4,a), 'bbb'->(3,b), 'c'->(1,c).
    assert rle.encode(b"aaaabbbc") == b"\x04a\x03b\x01c"


def test_empty_roundtrips_to_empty():
    assert rle.encode(b"") == b""
    assert rle.decode(b"") == b""


def test_single_byte():
    assert rle.encode(b"A") == b"\x01A"
    assert rle.decode(b"\x01A") == b"A"


def test_run_at_max_count():
    # A run of exactly 255 is a single pair (0xff, value).
    assert rle.encode(b"\xff" * 255) == b"\xff\xff"
    assert rle.decode(b"\xff\xff") == b"\xff" * 255


def test_run_over_max_count_splits():
    # 300 = 255 + 45, so two maximal pairs.
    assert rle.encode(b"A" * 300) == b"\xffA\x2dA"
    assert rle.decode(b"\xffA\x2dA") == b"A" * 300


def test_incompressible_expands_but_roundtrips():
    data = bytes(range(256))  # every byte distinct -> no runs
    encoded = rle.encode(data)
    assert len(encoded) == 2 * len(data)  # two output bytes per symbol
    assert rle.decode(encoded) == data


def test_roundtrip_over_many_inputs():
    import hashlib
    samples = [b"", b"\x00", b"\x00" * 1000, b"abcabcabc",
               b"\x00" * 500 + b"\x01" + b"\x00" * 500]
    for i in range(8):
        samples.append(hashlib.sha256(str(i).encode()).digest() * 3)
    for s in samples:
        assert rle.decode(rle.encode(s)) == s


def test_decode_rejects_truncated_stream():
    # Odd-length streams are impossible from encode(); must fail closed.
    try:
        rle.decode(b"\x03")
        assert False, "expected RleError on odd-length input"
    except rle.RleError:
        pass


def test_decode_rejects_zero_count():
    # A zero run length never appears in valid output.
    try:
        rle.decode(b"\x00A")
        assert False, "expected RleError on zero count"
    except rle.RleError:
        pass


def test_encode_type_error():
    try:
        rle.encode("not bytes")  # type: ignore[arg-type]
        assert False, "expected TypeError on str input"
    except TypeError:
        pass
