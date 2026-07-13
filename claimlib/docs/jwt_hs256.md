# JWS/JWT HS256 sign + strict verify (RFC 7515/7519)

*Subject area: Security / Authentication (JWT). Language: python. Vendorable bundle `f23728c1a640`.*

A JSON Web Token is two base64url-encoded JSON parts signed over 'header.payload' -- RFC 7515's JWS compact serialization with claim semantics from RFC 7519. Most JWT vulnerabilities are verifier bugs: accepting alg=none, letting the token pick the algorithm, or sloppy time handling. This module implements sign and a strict verifier (fixed algorithm allowlist, injected time, fail-closed parsing); the claim proves it reproduces the RFC's published example signature and rejects the classic confusion attacks, so you inherit a checked token core instead of another JWT pitfall.

## Claim

<!-- claim:CLAIM-LIB-JWT-HS256-001 checks_matched -->
The vendored JWS/JWT HS256 library passes all 37 checks with 0 mismatches: the RFC 7515 Appendix A.1 published example signature reproduces exactly (6 checks), the base64url codec matches its RFC 4648 vectors (12), exp/nbf validation with explicit injected time behaves per RFC 7519 at the boundaries (10), the adversarial battery -- alg 'none', asymmetric-alg confusion, tampered payloads, malformed tokens -- is rejected fail-closed (8), and signing is deterministic and round-trips (1). Verified value: <!-- v:CLAIM-LIB-JWT-HS256-001.checks_matched -->**37**
(`checks_matched`), backed by [`modules/jwt_hs256/artifacts/jwt_hs256.json`](../modules/jwt_hs256/artifacts/jwt_hs256.json).

## Vendor it

Ships `jwt_hs256.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/f23728c1a6407b4086ba75f23198f18d8f0f8e19434f9323a92690aec874d08b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 7515** — JSON Web Signature (JWS). [https://www.rfc-editor.org/rfc/rfc7515](https://www.rfc-editor.org/rfc/rfc7515)
- **RFC 7519** — JSON Web Token (JWT). [https://www.rfc-editor.org/rfc/rfc7519](https://www.rfc-editor.org/rfc/rfc7519)
- **RFC 4648** — The Base16, Base32, and Base64 Data Encodings. [https://www.rfc-editor.org/rfc/rfc4648](https://www.rfc-editor.org/rfc/rfc4648)
