# IPv6 parsing + RFC 5952 compression

*Subject area: Telecom / IPv6 Addressing. Language: python. Vendorable bundle `41ece038a5f3`.*

IPv6 text has many spellings for one address, so RFC 5952 defines a single canonical form: lowercase hex, no leading zeros per group, and the longest run of zero groups (leftmost on a tie) collapsed to '::'. Getting that compression exactly right -- and never collapsing a lone zero group -- is the subtle part every implementation must match. This module parses and canonicalises IPv6 from scratch; the claim proves it agrees with Python's ipaddress across the battery, so you inherit a checked, dependency-free IPv6 formatter rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-IPV6-001 checks_matched -->
The vendored IPv6 parser / RFC 5952 compressor -- implemented DIRECTLY and never importing ipaddress -- agrees with Python's stdlib ipaddress on all 38 checks across a fixed battery of 12 addresses and 7 CIDRs (checks_matched = 38, mismatches = 0): compress(parse(s)) equals .compressed and explode(parse(s)) equals .exploded for each address, and the compressed network address plus total address count match for each CIDR, exercising the RFC 5952 edges (leftmost-longest zero run wins, a single zero group is never shortened to '::'). Verified value: <!-- v:CLAIM-LIB-IPV6-001.checks_matched -->**38**
(`checks_matched`), backed by [`modules/ipv6/artifacts/ipv6.json`](../modules/ipv6/artifacts/ipv6.json).

## Vendor it

Ships `ipv6.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/41ece038a5f3e9dff5919ffdf9a0e2598a48cbf5329021c61f72374b13d513de --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 4291** — IP Version 6 Addressing Architecture. [https://www.rfc-editor.org/info/rfc4291](https://www.rfc-editor.org/info/rfc4291)
- **RFC 5952** — A Recommendation for IPv6 Address Text Representation. [https://www.rfc-editor.org/info/rfc5952](https://www.rfc-editor.org/info/rfc5952)
