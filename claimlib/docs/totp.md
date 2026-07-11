# TOTP one-time passwords (RFC 6238)

*Subject area: Security / Authentication (2FA). Language: python. Vendorable bundle `bcb90277f182`.*

TOTP (RFC 6238) is HOTP with the counter replaced by the current time divided into fixed steps (usually 30 s), so the code rotates automatically without a stored counter -- the '6-digit code' in Google Authenticator, Authy, and most 2FA. The verifier recomputes the expected code for the current window (often allowing one step of clock skew) and compares. This module computes TOTP with selectable digest and digit count; the claim proves it reproduces the official RFC 6238 vectors, so you inherit a checked TOTP generator rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-TOTP-001 correct -->
The vendored TOTP generator reproduces every published RFC 6238 Appendix B (SHA-1) test vector exactly (correct = 6, errors = 0): for the reference secret b"12345678901234567890" with 8 digits and a 30-second step, the TOTP at Unix times 59, 1111111109, 1111111111, 1234567890, 2000000000 and 20000000000 is 94287082, 07081804, 14050471, 89005924, 69279037 and 65353130, derived as HOTP over the time counter floor((now - T0) / step). Verified value: <!-- v:CLAIM-LIB-TOTP-001.correct -->**6**
(`correct`), backed by [`modules/totp/artifacts/totp.json`](../modules/totp/artifacts/totp.json).

## Vendor it

Ships `totp.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/bcb90277f1821459fb0b6bc2c807eb07534a1a5024ad90b7d0c41ed994fe530c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 6238** — TOTP: Time-Based One-Time Password Algorithm. [https://www.rfc-editor.org/rfc/rfc6238](https://www.rfc-editor.org/rfc/rfc6238)
- **RFC 4226** — HOTP: An HMAC-Based One-Time Password Algorithm. [https://www.rfc-editor.org/rfc/rfc4226](https://www.rfc-editor.org/rfc/rfc4226)
