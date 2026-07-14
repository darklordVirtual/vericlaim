# SLSA v1.1 Build levels + cumulative assessment

*Subject area: AI Assurance / Supply-Chain Integrity. Language: python. Vendorable bundle `9ce2a6e25397`.*

SLSA grades how trustworthy an artifact's build is, on a cumulative ladder: provenance exists (L1), signed provenance from a hosted platform (L2), hardened isolated builds (L3). ML supply chains attach model artifacts to exactly this ladder — 'which level built this model file' is becoming a procurement question. This module encodes the verified v1.1 Build track and computes achieved levels fail-closed; the claim proves the ladder by exhaustive subset enumeration, so a supply-chain assessment inherits checked level logic.

## Claim

<!-- claim:CLAIM-LIB-SLSA-001 checks_matched -->
The vendored SLSA library passes all 26 checks with 0 mismatches: the four published v1.1 Build-track levels carry their published names, one-line requirements and focus rows (Build L0 No guarantees through Build L3 Hardened builds), and level assessment is verified EXHAUSTIVELY — all 16 subsets of the four capability flags yield exactly the level an independent re-derivation of the cumulative rule assigns, with gap-capping proven (a hardened platform without signed provenance assesses at L1, not L3). Verified value: <!-- v:CLAIM-LIB-SLSA-001.checks_matched -->**26**
(`checks_matched`), backed by [`modules/slsa_levels/artifacts/slsa_levels.json`](../modules/slsa_levels/artifacts/slsa_levels.json).

## Vendor it

Ships `slsa_levels.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/9ce2a6e25397a6dc79608c024742813dc0c471a594e0c99d08fc763e07c771ac --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **SLSA v1.1** — Supply-chain Levels for Software Artifacts (SLSA) Specification v1.1. [https://slsa.dev/spec/v1.1/](https://slsa.dev/spec/v1.1/)
