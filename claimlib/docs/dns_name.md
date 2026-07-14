# DNS hostname validation (RFC 1035/1123)

*Subject area: Telecom / DNS Naming. Language: python. Vendorable bundle `d6ee99ee235b`.*

A DNS hostname is a dot-separated sequence of LDH labels: 1-63 octets each, letters/digits/hyphens, no leading or trailing hyphen, at most 255 octets in wire form -- which is what limits the presentation form to 253 characters (each label costs a length octet plus a terminating root byte). RFC 1123 relaxed RFC 952 to allow digit-first labels. This module validates names against exactly those published rules and computes the wire length; the claim proves the boundaries sit precisely where the RFCs put them, so you inherit a checked validator instead of a regex approximation.

## Claim

<!-- claim:CLAIM-LIB-DNS-NAME-001 correct -->
The vendored DNS hostname validator classifies all 23 battery names correctly (correct = 23, mismatches = 0) -- the 63-octet label and 253-character presentation-name boundaries, the LDH letter-digit-hyphen rule with RFC 1123's digit-start allowance, hyphen edge cases and empty labels -- and passes all 6 wire-format length computations and 5 case-insensitive equality checks, with the label boundary cross-checked against Python's stdlib encoder. Verified value: <!-- v:CLAIM-LIB-DNS-NAME-001.correct -->**23**
(`correct`), backed by [`modules/dns_name/artifacts/dns_name.json`](../modules/dns_name/artifacts/dns_name.json).

## Vendor it

Ships `dns_name.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/d6ee99ee235b5a7b7bed3c1dcae683ea20200b87f13750acfd513e750365d3ac --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 1035 (STD 13)** — Domain names - implementation and specification. [https://www.rfc-editor.org/rfc/rfc1035](https://www.rfc-editor.org/rfc/rfc1035)
- **RFC 1123 (STD 3)** — Requirements for Internet Hosts - Application and Support. [https://www.rfc-editor.org/rfc/rfc1123](https://www.rfc-editor.org/rfc/rfc1123)
