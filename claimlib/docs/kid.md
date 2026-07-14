# Norwegian KID check digits (MOD10 + MOD11, OCR giro)

*Subject area: Finance / Norwegian Payments (KID). Language: python. Vendorable bundle `1afa6fcf94d5`.*

Every Norwegian OCR giro payment carries a KID -- kundeidentifikasjon -- whose last digit is a check digit in one of two registered schemes: MOD10 (the Luhn algorithm, as on payment cards) or the weighted MOD11 (the same construction that protects organisasjonsnummer, where a weighted sum's remainder decides the digit and remainder 1 makes the payload unusable). This module computes, validates and generates both variants in one vendorable file; the claim proves exhaustive single-digit tamper detection and agreement with two independent constructions, so an invoicing system inherits checked payment-reference handling.

## Claim

<!-- claim:CLAIM-LIB-KID-001 tampers_missed -->
The vendored KID library misses ZERO of 859095 single-digit tamperings: over the complete space of 4-digit payloads, every single-digit alteration of every valid KID is rejected in BOTH registered variants (MOD10 and MOD11). Its MOD10 agrees with an independent from-scratch Luhn on all 10000 payloads of that space, and its MOD11 agrees with the published organisasjonsnummer construction on a 1027-point sweep with all 3 publicly listed orgnr (Equinor, Bronnoysundregistrene, DNB) validating. Verified value: <!-- v:CLAIM-LIB-KID-001.tampers_missed -->**0**
(`tampers_missed`), backed by [`modules/kid/artifacts/kid.json`](../modules/kid/artifacts/kid.json).

## Vendor it

Ships `kid.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/1afa6fcf94d5bbbe02cc9547fb0cf3013e5f5edbb1395555908c44f1329ff66e --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **OCR giro systemdokumentasjon, versjon 4.0 (2018)** — Systemspesifikasjon OCR giro. [https://www.mastercardpaymentservices.com/media/ruqn3ort/ocr-systemspesifikasjon_no_mps.pdf](https://www.mastercardpaymentservices.com/media/ruqn3ort/ocr-systemspesifikasjon_no_mps.pdf)
- **U.S. Patent 2,950,048** — Computer for Verifying Numbers. [https://patents.google.com/patent/US2950048A/en](https://patents.google.com/patent/US2950048A/en)
- **Brønnøysundregistrene: Om organisasjonsnummeret (rev. 13 Dec 2023)** — Om organisasjonsnummeret. [https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsnummeret/](https://www.brreg.no/om-oss/registrene-vare/om-enhetsregisteret/organisasjonsnummeret/)
