# IPv6 parsing + RFC 5952 compression

*Subject area: Telecom / IPv6 Addressing. Language: python. Vendorable bundle `9ec9ae00764d`.*

IPv6 text has many spellings for one address, so RFC 5952 defines a single canonical form: lowercase hex, no leading zeros per group, and the longest run of zero groups (leftmost on a tie) collapsed to '::'. Getting that compression exactly right -- and never collapsing a lone zero group -- is the subtle part every implementation must match. This module parses and canonicalises IPv6 from scratch; the claim proves it agrees with Python's ipaddress across the battery, so you inherit a checked, dependency-free IPv6 formatter rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-IPV6-001 checks_matched -->
The vendored IPv6 parser / RFC 5952 compressor -- implemented DIRECTLY and never importing ipaddress -- agrees with Python's stdlib ipaddress on all 38 checks across a fixed battery of 12 addresses and 7 CIDRs (checks_matched = 38, mismatches = 0): compress(parse(s)) equals .compressed and explode(parse(s)) equals .exploded for each address, and the compressed network address plus total address count match for each CIDR, exercising the RFC 5952 edges (leftmost-longest zero run wins, a single zero group is never shortened to '::'). Verified value: <!-- v:CLAIM-LIB-IPV6-001.checks_matched -->**38**
(`checks_matched`), backed by [`modules/ipv6/artifacts/ipv6.json`](../modules/ipv6/artifacts/ipv6.json).

## Vendor it

Ships `ipv6.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/9ec9ae00764df535516eff011f7736677986dd4522dda3720f3099c52ad7c6ca --target .
```
