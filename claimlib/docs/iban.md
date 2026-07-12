# IBAN validation (ISO 13616 / MOD-97-10)

*Subject area: Finance / Payments & Banking. Language: python. Vendorable bundle `e24c85c0e954`.*

An IBAN wraps a national bank account number with a two-letter country code and two check digits so cross-border transfers can be validated before money moves. The check is ISO 7064 MOD-97-10: move the first four characters to the end, map letters to numbers (A=10..Z=35), and require the resulting integer to be congruent to 1 modulo 97 -- a scheme that catches all single-digit errors and most transpositions. Vendor this module to validate AND to generate the check digits of IBANs with zero dependencies; the claim proves it matches the published registry examples, so you inherit a checked validator rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-IBAN-001 correct -->
The vendored IBAN validator (ISO 13616 / ISO 7064 MOD-97-10) classifies every entry in a fixed 12-row table of officially published IBANs correctly (correct = 12, errors = 0): 8 canonical registry / Wikipedia example IBANs (GB82WEST12345698765432, DE89370400440532013000, NO9386011117947, ES9121000418450200051332, ...) are accepted and 4 single-digit-mutated variants are rejected; independently, recomputing the two check digits from the BBAN reproduces the embedded check digits of all 5 tested valid IBANs. Verified value: <!-- v:CLAIM-LIB-IBAN-001.correct -->**12**
(`correct`), backed by [`modules/iban/artifacts/iban.json`](../modules/iban/artifacts/iban.json).

## Vendor it

Ships `iban.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/e24c85c0e954905c4c7ff2af19461e40907caa11379f5aaba38f9812ce05670e --target .
```
