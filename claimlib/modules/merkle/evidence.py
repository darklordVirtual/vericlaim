# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-MERKLE-001 — the Merkle module's inclusion proofs
verify and leaf tampering is rejected.

Over a fixed battery of N leaves the script builds the root, then for EVERY leaf
(1) generates its inclusion proof and checks it verifies against the root
(``proofs_verified``), and (2) tampers with the leaf and checks the same proof
is now rejected (``tampered_rejected``), counting any tampering that still
verifies as a ``false_accepts``. As an independent cross-check that the tree is
genuinely SHA-256-correct (not merely self-consistent), the module's root is
compared to a from-scratch recursive reference computed with plain ``hashlib``.

Deterministic: SHA-256 over fixed inputs, so the artifact is byte-identical on
every run.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (merkle.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from merkle import build_root, inclusion_proof, verify_proof  # noqa: E402
from _util import emit  # noqa: E402

# Fixed reference battery: 9 leaves. Nine is odd and the tree halves to 5, then
# 3, then 2, then 1 — so the duplicate-last-node rule fires at three separate
# levels, exercising the odd-level path thoroughly.
LEAVES = [f"block-{i:02d}".encode("ascii") for i in range(9)]


def _reference_root(leaves):
    """Independent, from-scratch Merkle root using plain hashlib and recursion.

    Deliberately written differently from merkle.py (recursive, not iterative)
    so it acts as a genuine cross-check of the hashing scheme rather than a copy.
    Same documented rule: leaf = sha256(bytes); node = sha256(left||right);
    odd level duplicates the last node.
    """
    level = [hashlib.sha256(b).digest() for b in leaves]

    def fold(nodes):
        if len(nodes) == 1:
            return nodes[0]
        if len(nodes) % 2 == 1:
            nodes = nodes + [nodes[-1]]
        parents = [hashlib.sha256(nodes[i] + nodes[i + 1]).digest()
                   for i in range(0, len(nodes), 2)]
        return fold(parents)

    return fold(level).hex()


def run() -> dict:
    n = len(LEAVES)
    root = build_root(LEAVES)

    proofs_verified = 0
    tampered_rejected = 0
    false_accepts = 0
    cases = []
    for i, leaf in enumerate(LEAVES):
        proof = inclusion_proof(LEAVES, i)
        ok = verify_proof(leaf, i, proof, root)
        proofs_verified += int(ok)

        # Tamper: append a byte so the leaf digest changes, reuse the real proof.
        tampered = leaf + b"!"
        rejected = not verify_proof(tampered, i, proof, root)
        tampered_rejected += int(rejected)
        false_accepts += int(not rejected)

        cases.append({
            "index": i,
            "proof_len": len(proof),
            "verified": ok,
            "tamper_rejected": rejected,
        })

    independent_root_match = (root == _reference_root(LEAVES))

    return {
        "schema": "claimlib_merkle_v1",
        "module": "merkle",
        "hash": "sha256",
        "odd_level_rule": "duplicate-last-node",
        "n_leaves": n,
        "root": root,
        "proofs_verified": proofs_verified,
        "tampered_rejected": tampered_rejected,
        "false_accepts": false_accepts,
        "independent_root_match": independent_root_match,
        "cases": cases,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "merkle.json", obj,
         script="python3 claimlib/modules/merkle/evidence.py")
    # claim:CLAIM-LIB-MERKLE-001 proofs_verified
    # All 9 leaves in the fixed battery produce an inclusion proof that verifies
    # against the committed root, so proofs_verified = 9; every tampered leaf is
    # rejected (tampered_rejected = 9) with false_accepts = 0.
    print(f"merkle: {obj['proofs_verified']}/{obj['n_leaves']} proofs verified, "
          f"{obj['tampered_rejected']}/{obj['n_leaves']} tampers rejected, "
          f"false_accepts={obj['false_accepts']}, "
          f"independent_root_match={obj['independent_root_match']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
