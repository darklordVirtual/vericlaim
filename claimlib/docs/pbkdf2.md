# PBKDF2 key derivation (RFC 8018)

*Subject area: Security / Password Hashing. Language: python. Vendorable bundle `2b8388b0e5ef`.*

PBKDF2 (RFC 8018 / PKCS#5) stretches a password into a cryptographic key by iterating an HMAC PRF thousands of times over the password and a per-user salt, so brute-forcing stolen hashes costs the attacker that same multiplier per guess. It is the classic password-hashing and key-derivation function (WPA2, disk encryption, many app login stores). This module implements the construction from scratch; the claim proves it matches the RFC 6070 vectors and agrees with hashlib.pbkdf2_hmac, so you inherit a checked KDF rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-PBKDF2-001 reference_vectors_matched -->
The vendored PBKDF2 -- which implements the RFC 8018 block function T_i = U_1 XOR ... XOR U_c DIRECTLY over an HMAC PRF and never calls hashlib.pbkdf2_hmac -- reproduces every value in an 11-vector reference set with 0 mismatches: the 3 published RFC 6070 PBKDF2-HMAC-SHA1 vectors (('password','salt',1,20) -> 0c60c80f...37a6, (...,2,20) -> ea6c014d...8957, (...,4096,20) -> 4b007901...29c1) plus 8 (hash, password, salt, iterations, dklen) cases over SHA-1/256/512 (multi-block output, empty password, empty salt) that agree byte-for-byte with the independent stdlib hashlib.pbkdf2_hmac. Verified value: <!-- v:CLAIM-LIB-PBKDF2-001.reference_vectors_matched -->**11**
(`reference_vectors_matched`), backed by [`modules/pbkdf2/artifacts/pbkdf2.json`](../modules/pbkdf2/artifacts/pbkdf2.json).

## Vendor it

Ships `pbkdf2.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/2b8388b0e5efb07690a587f2e8807ec9538cb68a384c7ae71fd2b61e9a2456c4 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 8018** — PKCS #5: Password-Based Cryptography Specification Version 2.1. [https://www.rfc-editor.org/rfc/rfc8018](https://www.rfc-editor.org/rfc/rfc8018)
- **RFC 6070** — PKCS #5 PBKDF2 Test Vectors. [https://www.rfc-editor.org/rfc/rfc6070](https://www.rfc-editor.org/rfc/rfc6070)
