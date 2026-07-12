# Tamper-evident append-only hash chain

*Subject area: Security / Data Integrity. Language: python. Vendorable bundle `66b33dc73981`.*

A hash chain makes an append-only log self-authenticating: each record's hash folds in the previous record's hash, so the head digest commits to the entire ordered history -- the same idea behind Git commit graphs and blockchain blocks. Changing, inserting, deleting or reordering any past entry changes that record's hash and every hash after it, so recomputing the chain from the claimed entries and comparing digests reveals the tampering. Vendor it to get an integrity-checked audit log or ledger; the claim proves the construction catches the enumerated mutations, so you inherit a checked primitive rather than a re-implementation to re-audit. For untrusted storage, sign or HMAC the head so the chain itself cannot be silently rewritten.

## Claim

<!-- claim:CLAIM-LIB-HASHCHAIN-001 tamper_detected -->
The vendored append-only hash chain (record hash = sha256(prev || entry)) detects every single-entry mutation over a fixed 64-entry battery: all 192 mutations tested (64 entries x 3 deterministic kinds -- full replace, byte prepend, first-byte bitflip) are caught, with tamper_missed = 0. The untampered chain verifies True, and correctness is cross-checked against an independent raw-hashlib oracle. Verified value: <!-- v:CLAIM-LIB-HASHCHAIN-001.tamper_detected -->**192**
(`tamper_detected`), backed by [`modules/hashchain/artifacts/hashchain.json`](../modules/hashchain/artifacts/hashchain.json).

## Vendor it

Ships `hashchain.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/66b33dc73981f81507ddc21305039ea4195cd340882cbbe7dd0a4a88bac730c6 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Journal of Cryptology, vol. 3, no. 2, pp. 99-111; doi:10.1007/BF00196791** — How to Time-Stamp a Digital Document. [https://doi.org/10.1007/BF00196791](https://doi.org/10.1007/BF00196791)
- **FIPS PUB 180-4** — Secure Hash Standard (SHS). [https://csrc.nist.gov/publications/detail/fips/180/4/final](https://csrc.nist.gov/publications/detail/fips/180/4/final)
