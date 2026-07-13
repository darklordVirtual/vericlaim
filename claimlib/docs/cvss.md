# CVSS v3.1 base scoring

*Subject area: Security / Vulnerability Management. Language: python. Vendorable bundle `f720a2b821ea`.*

CVSS v3.1 turns an attack vector, complexity, privileges, user interaction, scope and CIA impact into a 0.0-10.0 base score. This module parses the standard `CVSS:3.1/...` vector string and applies the published FIRST formula (impact, exploitability, scope, Roundup). Vendor it to score vulnerabilities consistently; the claim proves the arithmetic matches the reference, so you inherit a checked scorer, not a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-CVSS-001 reference_vectors_matched -->
The vendored CVSS v3.1 base-score scorer reproduces all published reference base scores in a fixed set exactly, with 0 mismatches — including scope change and the v3.1 Roundup rule. Verified value: <!-- v:CLAIM-LIB-CVSS-001.reference_vectors_matched -->**9**
(`reference_vectors_matched`), backed by [`modules/cvss/artifacts/cvss.json`](../modules/cvss/artifacts/cvss.json).

## Vendor it

Ships `cvss.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/f720a2b821ead2e43bd632c4b3e800c9308a1a822c1fb5cb9902260597e95c8e --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **CVSS v3.1 Specification Document (Revision 1, June 2019)** — Common Vulnerability Scoring System version 3.1: Specification Document. [https://www.first.org/cvss/v3.1/specification-document](https://www.first.org/cvss/v3.1/specification-document)
