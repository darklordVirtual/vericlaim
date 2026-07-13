# SPDX-License-Identifier: Apache-2.0
"""Binary Merkle tree with SHA-256 inclusion proofs — a reusable, stdlib-only
building block.

A pre-verified code artifact from the VeriClaim claim library. The property that
makes it trustworthy — that every leaf's inclusion proof verifies against the
committed root, and that any tampering with a leaf is rejected — is registered as
a claim and proven by a committed evidence artifact; vendoring this module
carries that claim (and its caveat) with it.

Public API
----------
    build_root(leaves) -> str
        SHA-256 Merkle root of an ordered list of ``bytes`` leaves, hex-encoded.
    inclusion_proof(leaves, index) -> list[tuple[str, str]]
        Audit path for ``leaves[index]``: a list of ``(sibling_hex, side)`` where
        ``side`` is ``"L"`` (sibling is the left input) or ``"R"`` (right input).
    verify_proof(leaf_bytes, index, proof, root) -> bool
        Recompute the root from a leaf + its proof and compare to ``root``.

Hashing scheme (fixed and explicit so proofs are portable)
----------------------------------------------------------
* Leaf hash:     ``H(leaf) = sha256(leaf_bytes)``.
* Internal node: ``H(left, right) = sha256(left_digest || right_digest)`` over
  the raw 32-byte digests (not their hex).
* Odd level rule (**duplicate-last-node**, the Bitcoin convention): when a level
  has an odd number of nodes, the final node is paired with a copy of itself
  before hashing up to the parent level. A single-leaf tree therefore has
  ``root == H(leaf)``.

This scheme does **not** apply RFC 6962 leaf/node domain-separation tags, so it
must not be treated as second-preimage resistant across trees of different
shapes; see the module claim's caveat.

    >>> root = build_root([b"a", b"b"])
    >>> proof = inclusion_proof([b"a", b"b"], 0)
    >>> verify_proof(b"a", 0, proof, root)
    True
    >>> verify_proof(b"tampered", 0, proof, root)
    False
"""
from __future__ import annotations

import hashlib
from typing import List, Sequence, Tuple

__all__ = ["MerkleError", "hash_leaf", "build_root", "inclusion_proof",
           "verify_proof"]

Proof = List[Tuple[str, str]]


class MerkleError(ValueError):
    """The leaves or proof are malformed (empty tree, bad index, bad side)."""


def _sha256(data: bytes) -> bytes:
    """Raw 32-byte SHA-256 digest of ``data``."""
    return hashlib.sha256(data).digest()


def hash_leaf(leaf_bytes: bytes) -> bytes:
    """Return the raw SHA-256 leaf digest for ``leaf_bytes``."""
    if not isinstance(leaf_bytes, (bytes, bytearray)):
        raise MerkleError("leaf must be bytes")
    return _sha256(bytes(leaf_bytes))


def _levels(leaf_digests: Sequence[bytes]) -> List[List[bytes]]:
    """Build every tree level bottom-up from the leaf digests.

    Returns a list ``[leaves, ..., [root]]``. The odd-level duplicate-last-node
    rule is applied by pairing the final node with itself when a level has an
    odd length.
    """
    if not leaf_digests:
        raise MerkleError("cannot build a Merkle tree from zero leaves")
    levels: List[List[bytes]] = [list(leaf_digests)]
    while len(levels[-1]) > 1:
        cur = levels[-1]
        nxt: List[bytes] = []
        for i in range(0, len(cur), 2):
            left = cur[i]
            right = cur[i + 1] if i + 1 < len(cur) else cur[i]  # duplicate last
            nxt.append(_sha256(left + right))
        levels.append(nxt)
    return levels


def build_root(leaves: Sequence[bytes]) -> str:
    """Return the hex-encoded SHA-256 Merkle root of ``leaves``.

    ``leaves`` is an ordered sequence of ``bytes``. Raises :class:`MerkleError`
    on an empty sequence (a tree needs at least one leaf).
    """
    leaf_digests = [hash_leaf(leaf) for leaf in leaves]
    return _levels(leaf_digests)[-1][0].hex()


def inclusion_proof(leaves: Sequence[bytes], index: int) -> Proof:
    """Return the audit path proving ``leaves[index]`` is in the tree.

    The result is a bottom-up list of ``(sibling_hex, side)`` steps. ``side`` is
    ``"R"`` when the sibling is the right-hand input to the parent hash (so the
    running digest goes on the left), and ``"L"`` when the sibling is on the
    left. For the duplicated last node of an odd level the sibling is the node
    itself, recorded with side ``"R"``.

    Raises :class:`MerkleError` on an empty tree or an out-of-range index.
    """
    if not leaves:
        raise MerkleError("cannot prove membership in an empty tree")
    n = len(leaves)
    if not isinstance(index, int) or index < 0 or index >= n:
        raise MerkleError(f"index {index!r} out of range for {n} leaves")
    levels = _levels([hash_leaf(leaf) for leaf in leaves])
    proof: Proof = []
    idx = index
    for level in levels[:-1]:  # every level except the root
        if idx % 2 == 0:
            sib = idx + 1 if idx + 1 < len(level) else idx  # duplicate self
            side = "R"
        else:
            sib = idx - 1
            side = "L"
        proof.append((level[sib].hex(), side))
        idx //= 2
    return proof


def verify_proof(leaf_bytes: bytes, index: int, proof: Proof, root: str) -> bool:
    """Return ``True`` iff ``leaf_bytes`` at ``index`` hashes up to ``root``.

    Recomputes the root from the leaf digest and the audit path, folding in each
    sibling on the side named by the proof. ``index`` is accepted for API
    symmetry and validated to be non-negative; direction is taken from each
    step's recorded ``side``. Returns ``False`` on any mismatch (wrong leaf,
    wrong path, wrong root). Raises :class:`MerkleError` only on a structurally
    invalid proof (bad side label or non-hex sibling).
    """
    if not isinstance(index, int) or index < 0:
        raise MerkleError(f"index {index!r} must be a non-negative int")
    cur = hash_leaf(leaf_bytes)
    for sibling_hex, side in proof:
        try:
            sibling = bytes.fromhex(sibling_hex)
        except (ValueError, TypeError) as exc:
            raise MerkleError(f"invalid sibling hex {sibling_hex!r}") from exc
        if side == "R":
            cur = _sha256(cur + sibling)
        elif side == "L":
            cur = _sha256(sibling + cur)
        else:
            raise MerkleError(f"invalid proof side {side!r}; expected 'L' or 'R'")
    if not isinstance(root, str):
        raise MerkleError("root must be a hex string")
    return cur.hex() == root.lower()
