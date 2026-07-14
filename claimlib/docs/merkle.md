# Merkle tree SHA-256 inclusion proofs

*Subject area: Security / Cryptographic Integrity. Language: python. Vendorable bundle `ad4cf682bcea`.*

A Merkle tree hashes an ordered list of leaves pairwise up to a single root digest, so any party holding the root can verify that a given leaf is included via a short O(log n) audit path of sibling hashes rather than re-hashing the whole set. This module uses sha256 with the Bitcoin-style duplicate-last-node rule for odd levels (documented explicitly so proofs are portable), exposing build_root, inclusion_proof, and verify_proof. Vendor it for tamper-evident logs, transparency/commitment schemes, or content addressing; the claim proves proofs verify and leaf tampering is caught, so you inherit a checked implementation rather than an unaudited re-write.

## Claim

<!-- claim:CLAIM-LIB-MERKLE-001 proofs_verified -->
The vendored SHA-256 binary Merkle tree produces inclusion proofs that all verify against the committed root (proofs_verified = n_leaves) over a fixed 9-leaf battery, and rejects every single-leaf tamper (tampered_rejected = 9) with false_accepts = 0; the built root is additionally cross-checked byte-for-byte against an independent from-scratch reference computation. Verified value: <!-- v:CLAIM-LIB-MERKLE-001.proofs_verified -->**9**
(`proofs_verified`), backed by [`modules/merkle/artifacts/merkle.json`](../modules/merkle/artifacts/merkle.json).

## Vendor it

Ships `merkle.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/ad4cf682bcea8545916fd9339dd98ef311f11d0eae1f97713e6c52f4fc0391dc --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Advances in Cryptology — CRYPTO '87, LNCS 293, pp. 369-378; doi:10.1007/3-540-48184-2_32** — A Digital Signature Based on a Conventional Encryption Function. [https://doi.org/10.1007/3-540-48184-2_32](https://doi.org/10.1007/3-540-48184-2_32)
- **RFC 6962** — Certificate Transparency. [https://www.rfc-editor.org/info/rfc6962](https://www.rfc-editor.org/info/rfc6962)
- **FIPS PUB 180-4** — Secure Hash Standard (SHS). [https://csrc.nist.gov/publications/detail/fips/180/4/final](https://csrc.nist.gov/publications/detail/fips/180/4/final)
