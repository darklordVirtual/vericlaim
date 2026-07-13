# Weighted MOD-11 check digits (Norwegian orgnr)

*Subject area: Finance / Identifiers & Validation. Language: python. Vendorable bundle `e03ab70bd0cd`.*

A weighted MOD-11 check digit is the integrity digit behind Norwegian organisation and bank account numbers, KID payment references, ISBN-10, and many national IDs: multiply each payload digit by a position weight, sum, reduce modulo 11, and take 11 minus that (11 -> 0). Because 11 is prime, every single-digit change alters the weighted sum modulo 11 and is detected -- a stronger guarantee than a plain sum. Vendor this module to validate and generate those identifiers with zero dependencies; the claim proves single-digit errors are caught exhaustively over the tested space, so you inherit a checked check-digit routine rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-MOD11-001 tamper_missed -->
The vendored weighted MOD-11 check-digit library detects EVERY single-digit alteration over the complete space of 4-digit payloads under weights (2,3,4,5): all 409095 single-digit mutations of the 9091 well-defined check-digited numbers are caught (tamper_detected = 409095, tamper_missed = 0), every one of those numbers round-trips (compute the check digit, then validate = True; roundtrip_valid = 9091), and the Norwegian organisasjonsnummer reference 123456785 (payload 12345678 under weights 3,2,7,6,5,4,3,2 -> check 5) validates while 123456784 does not. Verified value: <!-- v:CLAIM-LIB-MOD11-001.tamper_missed -->**0**
(`tamper_missed`), backed by [`modules/mod11/artifacts/mod11.json`](../modules/mod11/artifacts/mod11.json).

## Vendor it

Ships `mod11.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e03ab70bd0cdc20b2e2fdbc4b058987e31675b8d4edf2b07da70d357978d900c --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Brønnøysundregistrene: Om organisasjonsnummeret (rev. 13 Dec 2023)** — Om organisasjonsnummeret. [https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsnummeret/](https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsnummeret/)
