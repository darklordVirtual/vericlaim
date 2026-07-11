# HOTP one-time passwords (RFC 4226)

*Subject area: Security / Authentication (2FA). Language: python. Vendorable bundle `94c21c97c05b`.*

HOTP (RFC 4226) is the HMAC-based one-time-password algorithm behind hardware tokens and authenticator apps: it HMACs an incrementing counter with a shared secret, then 'dynamically truncates' the MAC to a short human-typable code. Each counter value yields a fresh single-use code, so an intercepted code is worthless once used. This module implements the generation and truncation exactly; the claim proves it reproduces the official RFC 4226 vectors, so you inherit a checked OTP generator rather than a re-implementation to re-audit (and TOTP builds directly on it).

## Claim

<!-- claim:CLAIM-LIB-HOTP-001 correct -->
The vendored HOTP generator reproduces every published RFC 4226 Appendix D test vector exactly (correct = 10, errors = 0): for the reference secret b"12345678901234567890" the 6-digit HOTP for counters 0..9 is 755224, 287082, 359152, 969429, 338314, 254676, 287922, 162583, 399871, 520489, computed via HMAC-SHA1 of the counter and the RFC 4226 dynamic-truncation to a 31-bit value reduced modulo 10**digits. Verified value: <!-- v:CLAIM-LIB-HOTP-001.correct -->**10**
(`correct`), backed by [`modules/hotp/artifacts/hotp.json`](../modules/hotp/artifacts/hotp.json).

## Vendor it

Ships `hotp.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/94c21c97c05b593e1262561c26b3de5388c3fe66637f286a191c8f0e8ef8e253 --target .
```
