# HKDF key derivation (RFC 5869)

*Subject area: Security / Key Derivation. Language: python. Vendorable bundle `e292721b70fb`.*

HKDF (RFC 5869) is the modern key-derivation function used by TLS 1.3, the Signal protocol, and Noise: 'extract' concentrates the entropy of an input keying material into a uniform pseudorandom key PRK = HMAC(salt, IKM), and 'expand' stretches PRK into any number of independent output keys via a counter-chained HMAC, with an info label for domain separation. This module implements both steps; the claim proves it reproduces the official RFC 5869 vectors (including the 82-byte case), so you inherit a checked KDF rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-HKDF-001 reference_vectors_matched -->
The vendored HKDF (extract-then-expand) reproduces the published RFC 5869 SHA-256 test vectors exactly (reference_vectors_matched = 9, mismatches = 0): across Test Case 1 (basic), Test Case 2 (longer inputs, L=82), and Test Case 3 (zero-length salt and info) it matches the RFC's PRK and OKM hex, and the standalone expand(PRK) step reproduces each OKM -- all three checks per case, hand-written verbatim from the RFC. Verified value: <!-- v:CLAIM-LIB-HKDF-001.reference_vectors_matched -->**9**
(`reference_vectors_matched`), backed by [`modules/hkdf/artifacts/hkdf.json`](../modules/hkdf/artifacts/hkdf.json).

## Vendor it

Ships `hkdf.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e292721b70fb44e9d867cef8b5ffaae41d9592c36586e4a01423d831506c00f0 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 5869** — HMAC-based Extract-and-Expand Key Derivation Function (HKDF). [https://www.rfc-editor.org/rfc/rfc5869](https://www.rfc-editor.org/rfc/rfc5869)
- **RFC 8446** — The Transport Layer Security (TLS) Protocol Version 1.3. [https://www.rfc-editor.org/rfc/rfc8446](https://www.rfc-editor.org/rfc/rfc8446)
