# HMAC-SHA256 (RFC 2104) from scratch

*Subject area: Security / Message Authentication. Language: python. Vendorable bundle `bbab36c3a422`.*

HMAC (RFC 2104) turns a plain hash into a keyed message authentication code: HMAC(K, m) = H((K XOR opad) || H((K XOR ipad) || m)). It lets two parties holding a shared secret verify that a message is authentic and untampered, and underpins TOTP/HOTP, JWT (HS256), AWS request signing, and webhook signatures. Verifying a tag must be constant-time so an attacker cannot forge one byte at a time. This module implements the construction from scratch; the claim proves it matches stdlib hmac and the RFC 4231 vector, so you inherit a checked MAC rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-HMAC-SHA256-001 reference_vectors_matched -->
The vendored HMAC-SHA256 -- which implements the RFC 2104 construction DIRECTLY (key normalization, ipad/opad, two-pass hash) over hashlib.sha256 and never calls the stdlib hmac module -- passes all 13 checks with 0 mismatches: it agrees byte-for-byte with stdlib hmac on all 10 battery inputs (the RFC 4231 HMAC-SHA256 test key/message pairs, including the oversized 131-byte key that must be hashed down, plus empty and block-sized keys), reproduces the published RFC 4231 Test Case 2 tag (5bdcc146...3843), and its constant-time verify accepts the correct tag and rejects a single flipped bit. Verified value: <!-- v:CLAIM-LIB-HMAC-SHA256-001.reference_vectors_matched -->**13**
(`reference_vectors_matched`), backed by [`modules/hmac_sha256/artifacts/hmac_sha256.json`](../modules/hmac_sha256/artifacts/hmac_sha256.json).

## Vendor it

Ships `hmac_sha256.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/bbab36c3a4224ca672257f197c535629b8f4d542f147d0d1c85da5b216dc36f4 --target .
```
