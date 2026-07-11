# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``merkle`` library.

Expected roots are computed independently of the module's tree traversal, by
applying the documented SHA-256 scheme directly with ``hashlib``:
    leaf  = sha256(bytes)
    node  = sha256(left_digest || right_digest)
    odd level duplicates the last node.
The literal digests in ``test_known_roots`` were hand-derived from that formula.
"""
import hashlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
MODDIR = HERE.parents[1] / "claimlib" / "modules" / "merkle"
if not MODDIR.exists():  # when tests/ sits inside claimlib/
    MODDIR = HERE.parent / "modules" / "merkle"
sys.path.insert(0, str(MODDIR))

from merkle import (  # noqa: E402
    MerkleError, build_root, hash_leaf, inclusion_proof, verify_proof,
)


def _h(b):
    return hashlib.sha256(b).digest()


def test_single_leaf_root_is_leaf_hash():
    # Documented rule: a one-leaf tree's root equals the leaf hash.
    assert build_root([b"a"]) == _h(b"a").hex()
    assert build_root([b"a"]) == hash_leaf(b"a").hex()


def test_known_roots_two_and_three_leaves():
    # Independently computed literals (see module docstring formula).
    assert build_root([b"a", b"b"]) == \
        "e5a01fee14e0ed5c48714f22180f25ad8365b53f9779f79dc4a3d7e93963f94a"
    # 3 leaves: last node (c) duplicated at the leaf level.
    assert build_root([b"a", b"b", b"c"]) == \
        "d31a37ef6ac14a2db1470c4316beb5592e6afd4465022339adafda76a18ffabe"


def test_two_leaf_root_matches_direct_formula():
    root = build_root([b"a", b"b"])
    assert root == hashlib.sha256(_h(b"a") + _h(b"b")).hexdigest()


def test_all_proofs_verify_odd_tree():
    # 7 leaves -> odd at two levels, exercising duplicate-last-node.
    leaves = [f"x{i}".encode() for i in range(7)]
    root = build_root(leaves)
    for i, leaf in enumerate(leaves):
        proof = inclusion_proof(leaves, i)
        assert verify_proof(leaf, i, proof, root) is True


def test_tampered_leaf_is_rejected():
    leaves = [f"x{i}".encode() for i in range(7)]
    root = build_root(leaves)
    for i, leaf in enumerate(leaves):
        proof = inclusion_proof(leaves, i)
        assert verify_proof(leaf + b"!", i, proof, root) is False


def test_wrong_root_is_rejected():
    leaves = [b"a", b"b", b"c", b"d"]
    proof = inclusion_proof(leaves, 2)
    bad_root = "00" * 32
    assert verify_proof(b"c", 2, proof, bad_root) is False


def test_proof_from_other_index_does_not_verify():
    # A valid proof for index 0 must not verify leaf 0 as if at index 1.
    leaves = [b"a", b"b", b"c", b"d"]
    root = build_root(leaves)
    proof0 = inclusion_proof(leaves, 0)
    # Reusing index-0's path for leaf b (index 1) should fail.
    assert verify_proof(b"b", 1, proof0, root) is False


def test_root_is_case_insensitive_hex():
    leaves = [b"a", b"b"]
    root = build_root(leaves)
    proof = inclusion_proof(leaves, 0)
    assert verify_proof(b"a", 0, proof, root.upper()) is True


def test_empty_tree_raises():
    with pytest.raises(MerkleError):
        build_root([])
    with pytest.raises(MerkleError):
        inclusion_proof([], 0)


def test_index_out_of_range_raises():
    with pytest.raises(MerkleError):
        inclusion_proof([b"a", b"b"], 2)
    with pytest.raises(MerkleError):
        inclusion_proof([b"a", b"b"], -1)


def test_invalid_proof_side_raises():
    with pytest.raises(MerkleError):
        verify_proof(b"a", 0, [("aa" * 32, "X")], "00" * 32)


def test_side_labels_are_l_or_r():
    leaves = [f"x{i}".encode() for i in range(5)]
    for i in range(5):
        for _sib, side in inclusion_proof(leaves, i):
            assert side in ("L", "R")
