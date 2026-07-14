# NIST SP 800-207 Zero Trust tenets

*Subject area: AI Assurance / Zero Trust Architecture. Language: python. Vendorable bundle `9a38f2f428b8`.*

NIST SP 800-207's seven tenets define zero trust: nothing is trusted by network location, every access is a per-session decision under dynamic policy, and the enterprise continuously measures what it owns. Agentic AI deployments inherit this frame wholesale — every agent, tool endpoint and memory store is a resource, every tool call an access decision. This module encodes the verified tenets with exact coverage scoring; the claim proves the encoding matches the publication, so an architecture review inherits a checked frame.

## Claim

<!-- claim:CLAIM-LIB-ZTA-001 checks_matched -->
The vendored Zero Trust library passes all 5 checks with 0 mismatches: the encoded seven tenets match NIST SP 800-207 section 2.1, anchored by their published phrases (all data sources and computing services are considered resources; per-session access; dynamic policy; posture monitoring; dynamic, strictly-enforced authentication; telemetry-driven improvement), and coverage arithmetic is Fraction-exact. Verified value: <!-- v:CLAIM-LIB-ZTA-001.checks_matched -->**5**
(`checks_matched`), backed by [`modules/zta_tenets/artifacts/zta_tenets.json`](../modules/zta_tenets/artifacts/zta_tenets.json).

## Vendor it

Ships `zta_tenets.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/9a38f2f428b857702e5b66d3a04e8aa9e211cc2942ae3e1b4f438d3a3e7e42f8 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **NIST SP 800-207** — Zero Trust Architecture. [https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-207.pdf)
