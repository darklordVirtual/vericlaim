# OWASP Top 10 for LLM Applications 2025 taxonomy

*Subject area: AI Assurance / LLM Application Security. Language: python. Vendorable bundle `2551fd883ed6`.*

The OWASP Top 10 for LLM Applications is the shared vocabulary between AI engineering and security review: prompt injection, sensitive-information disclosure, supply chain, poisoning, improper output handling, excessive agency and the rest. A security review of an LLM product is at bottom a coverage map over this list. This module encodes the verified 2025 taxonomy with fail-closed coverage scoring; the claim proves the list matches the publication, so a review pipeline inherits a checked checklist skeleton.

## Claim

<!-- claim:CLAIM-LIB-OWASP-LLM-001 checks_matched -->
The vendored OWASP LLM Top 10 library passes all 9 checks with 0 mismatches: the encoded taxonomy matches the published Version 2025 list verbatim — ten entries LLM01..LLM10 with Prompt Injection ranked first, the 2025 additions System Prompt Leakage (LLM07) and Vector and Embedding Weaknesses (LLM08), and Unbounded Consumption as LLM10 — and mitigation-coverage arithmetic is Fraction-exact. Verified value: <!-- v:CLAIM-LIB-OWASP-LLM-001.checks_matched -->**9**
(`checks_matched`), backed by [`modules/owasp_llm10/artifacts/owasp_llm10.json`](../modules/owasp_llm10/artifacts/owasp_llm10.json).

## Vendor it

Ships `owasp_llm10.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/2551fd883ed62596dfdcde55857d98b7a57feede20feee90eab4a403f0d7a5a0 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **OWASP Top 10 for LLM Applications, Version 2025 (released 2024-11-18)** — OWASP Top 10 for LLM Applications 2025. [https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/](https://genai.owasp.org/resource/owasp-top-10-for-llm-applications-2025/)
