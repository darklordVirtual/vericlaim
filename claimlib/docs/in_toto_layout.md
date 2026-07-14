# in-toto supply-chain layout / artifact-rule verification

*Subject area: AI Assurance / Supply Chain. Language: python. Vendorable bundle `c97a4a208485`.*

in-toto (Torres-Arias et al., USENIX Security 2019) secures a software/ML pipeline against tampering between steps: a signed LAYOUT declares the ordered steps, each step's authorized functionaries and signature threshold, and artifact rules over its expected materials and products; per-step signed LINK metadata records what each functionary actually consumed and produced, and verification checks the links against the layout. This module implements the seven-rule artifact-flow engine and step verification with fail-closed semantics; the claim proves each rule type against the spec and detects five distinct tamperings by enumeration, so a supply-chain verifier inherits a checked flow engine rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-INTOTO-001 checks_matched -->
The vendored in-toto artifact-rule engine passes all 20 checks with 0 mismatches: the SEVEN artifact-rule types (MATCH, CREATE, DELETE, MODIFY, ALLOW, DISALLOW, REQUIRE) each match their spec-derived PASS/FAIL verdict over 14 hand-built cases — including rule-ORDER sensitivity (ALLOW-then-DISALLOW passes what DISALLOW-first rejects) — the canonical clone -> build -> package layout verifies whole (clean_layout_ok = 1), and 5 independent tamperings (an unauthorized functionary, a below-threshold signature count, an un-sourced product, a cross-step MATCH hash mismatch, and a DISALLOW-guarded stray file) are each detected (tamperings_detected = 5), with 6/6 malformed inputs rejected. Verified value: <!-- v:CLAIM-LIB-INTOTO-001.checks_matched -->**20**
(`checks_matched`), backed by [`modules/in_toto_layout/artifacts/in_toto_layout.json`](../modules/in_toto_layout/artifacts/in_toto_layout.json).

## Vendor it

Ships `in_toto_layout.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/c97a4a2084853afd42f7f7fdb9b1e245b7ed084c6529b3d3139f4f5bff991e36 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **USENIX Security 2019, pp. 1393-1410** — in-toto: Providing farm-to-table guarantees for bits and bytes. [https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias](https://www.usenix.org/conference/usenixsecurity19/presentation/torres-arias)
- **SLSA v1.1** — Supply-chain Levels for Software Artifacts (SLSA) Specification v1.1. [https://slsa.dev/spec/v1.1/](https://slsa.dev/spec/v1.1/)
