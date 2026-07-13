# SPKI public-key pins (RFC 7469)

*Subject area: Security / TLS & PKI. Language: python. Vendorable bundle `1e8c29304df8`.*

Certificate pinning narrows trust from 'any CA the system trusts' to 'this specific public key (or its backup)'. An RFC 7469 pin is base64(SHA-256(SubjectPublicKeyInfo)); a client stores it and refuses a connection whose chain presents no matching pinned key, defeating a mis-issued-but-technically-valid certificate. This module computes and verifies pins with a constant-time compare; the claim proves the pin equals the hash-of-SPKI and that matching accepts/rejects correctly, so you inherit a checked pinning primitive rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-SPKI-PIN-001 checks_matched -->
The vendored SPKI pinning library passes all 16 checks with 0 mismatches: for each SPKI sample the pin equals base64(sha256(spki)) computed independently via the stdlib hashlib/base64, matches() accepts the correct pin even when it is the backup among several, rejects a wrong pin, and the pin-sha256="..." directive form is well-shaped -- with a constant-time comparison that scans all pins without an early exit. Verified value: <!-- v:CLAIM-LIB-SPKI-PIN-001.checks_matched -->**16**
(`checks_matched`), backed by [`modules/spki_pin/artifacts/spki_pin.json`](../modules/spki_pin/artifacts/spki_pin.json).

## Vendor it

Ships `spki_pin.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/1e8c29304df8009fe6a5ec57f212847ded783c6d92a4f2026d2426fcb97843de --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 7469** — Public Key Pinning Extension for HTTP (HPKP). [https://www.rfc-editor.org/rfc/rfc7469](https://www.rfc-editor.org/rfc/rfc7469)
- **RFC 8446** — The Transport Layer Security (TLS) Protocol Version 1.3. [https://www.rfc-editor.org/rfc/rfc8446](https://www.rfc-editor.org/rfc/rfc8446)
