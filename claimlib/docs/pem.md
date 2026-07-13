# PEM textual encoding (RFC 7468)

*Subject area: Security / TLS & PKI. Language: python. Vendorable bundle `8857aa9bfeff`.*

PEM is the ubiquitous text form of TLS material: a certificate or key is DER (binary ASN.1), base64-encoded and wrapped between '-----BEGIN CERTIFICATE-----' and '-----END CERTIFICATE-----' lines so it survives copy-paste and config files. Getting the label matching and 64-column wrapping right matters for interoperability. This module encodes and decodes the envelope with zero dependencies; the claim proves it round-trips DER and matches the stdlib base64, so you inherit a checked codec for handling certs and keys in mTLS tooling rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-PEM-001 checks_matched -->
The vendored PEM codec (RFC 7468) passes all 11 checks with 0 mismatches: for a fixed set of DER blobs (a small SEQUENCE, empty, single byte, and long payloads) decode(encode(der, label)) round-trips to (label, der), the base64 body matches the stdlib base64 and every line wraps at 64 characters, and a two-block PEM parses into the correct list of (label, der) pairs -- the codec implements the envelope itself and never imports the csv/pem parts of the stdlib beyond base64. Verified value: <!-- v:CLAIM-LIB-PEM-001.checks_matched -->**11**
(`checks_matched`), backed by [`modules/pem/artifacts/pem.json`](../modules/pem/artifacts/pem.json).

## Vendor it

Ships `pem.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/8857aa9bfeffac6c1dfc7c50d918d99b3459fe0dbacec4e17e6ac97a7cbd55d0 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 7468** — Textual Encodings of PKIX, PKCS, and CMS Structures. [https://www.rfc-editor.org/rfc/rfc7468](https://www.rfc-editor.org/rfc/rfc7468)
- **RFC 5280** — Internet X.509 Public Key Infrastructure Certificate and CRL Profile. [https://www.rfc-editor.org/rfc/rfc5280](https://www.rfc-editor.org/rfc/rfc5280)
