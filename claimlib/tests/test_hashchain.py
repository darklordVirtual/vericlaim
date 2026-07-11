# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable hashchain library.

Correctness oracle: an INDEPENDENT re-implementation of the chain using raw
hashlib (see ``_ref_chain``), computed here rather than taken from the module
under test, plus known-good structural facts (digest width, genesis value).
"""
import hashlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODDIR = HERE.parents[0] / "modules" / "hashchain"
sys.path.insert(0, str(MODDIR))

import hashchain  # noqa: E402
from hashchain import HashChain, build_chain, record_hash, verify, GENESIS  # noqa: E402


def _ref_chain(entries):
    """Independent oracle: recompute the chain of hex head digests by hand."""
    prev = b"\x00" * 32
    out = []
    for e in entries:
        prev = hashlib.sha256(prev + e).digest()
        out.append(prev.hex())
    return out


def test_genesis_is_32_zero_bytes():
    # Known-good: SHA-256 digest width is 32 bytes.
    assert GENESIS == b"\x00" * 32
    assert len(GENESIS) == 32


def test_head_matches_independent_oracle():
    entries = [b"alpha", b"beta", b"gamma"]
    c = HashChain()
    for e in entries:
        c.append(e)
    assert c.hashes == _ref_chain(entries)
    assert c.head == _ref_chain(entries)[-1]


def test_record_hash_matches_raw_sha256():
    # record_hash(prev, entry) must be exactly sha256(prev || entry).
    prev = GENESIS
    entry = b"hello"
    assert record_hash(prev, entry) == hashlib.sha256(prev + entry).digest()


def test_append_returns_64_hex_chars():
    c = HashChain()
    head = c.append(b"x")
    assert isinstance(head, str)
    assert len(head) == 64
    int(head, 16)  # parses as hex


def test_verify_accepts_untampered_chain():
    entries = [b"a", b"b", b"c", b"d"]
    chain = build_chain(entries)
    assert verify(entries, chain) is True


def test_verify_rejects_single_entry_change():
    entries = [b"a", b"b", b"c", b"d"]
    chain = build_chain(entries)
    tampered = [b"a", b"B", b"c", b"d"]  # one byte changed in entry 1
    assert verify(tampered, chain) is False


def test_verify_rejects_reorder():
    entries = [b"a", b"b", b"c"]
    chain = build_chain(entries)
    assert verify([b"b", b"a", b"c"], chain) is False


def test_verify_rejects_truncation_and_extension():
    entries = [b"a", b"b", b"c"]
    chain = build_chain(entries)
    assert verify(entries[:-1], chain) is False          # dropped last entry
    assert verify(entries + [b"d"], chain) is False       # appended an entry


def test_verify_rejects_mutated_chain_hash():
    entries = [b"a", b"b", b"c"]
    chain = build_chain(entries)
    bad = list(chain)
    bad[0] = "0" * 64  # forge a head digest
    assert verify(entries, bad) is False


def test_empty_chain_verifies_and_head_is_genesis():
    c = HashChain()
    assert len(c) == 0
    assert c.head == GENESIS.hex()
    assert verify([], []) is True


def test_append_rejects_non_bytes():
    c = HashChain()
    with pytest.raises(TypeError):
        c.append("not-bytes")  # str is refused on purpose
    with pytest.raises(TypeError):
        record_hash(GENESIS, 123)


def test_full_mutation_battery_all_detected():
    # Mirror the evidence claim on a small scale: every single-entry mutation
    # over the whole list is detected.
    entries = [f"rec-{i:03d}".encode() for i in range(16)]
    chain = build_chain(entries)
    detected = 0
    tested = 0
    for i in range(len(entries)):
        for new_value in (b"TAMPER", b"\x00" + entries[i],
                          bytes([entries[i][0] ^ 0x01]) + entries[i][1:]):
            assert new_value != entries[i]
            mutated = list(entries)
            mutated[i] = new_value
            tested += 1
            if verify(mutated, chain) is False:
                detected += 1
    assert tested == 48
    assert detected == 48  # zero missed
