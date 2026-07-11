# BGP AS-path + ASN classification

*Subject area: Telecom / BGP Routing. Language: python. Vendorable bundle `7829e3aad06c`.*

Every BGP route carries an AS-path -- the list of Autonomous Systems it traversed -- and operators constantly reason about it: how long is it (shorter is preferred), who originated it, and are any ASNs private or reserved (which must not leak to the public Internet). The private, reserved, and documentation ASN ranges are fixed by RFCs 6996/7300/5398/7607/6793. This module parses the path and classifies ASNs against those ranges; the claim proves the classification matches the published boundaries, so you inherit a checked routing helper rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-ASPATH-001 correct -->
The vendored BGP AS-path library classifies every one of a fixed 17-ASN battery correctly against the published RFC allocations (correct = 17, errors = 0), pinning both sides of every boundary: private 64512-65534 and 4200000000-4294967294 (RFC 6996), reserved 0 (RFC 7607), 23456 AS_TRANS (RFC 6793), 65535 and 4294967295 last-ASN (RFC 7300), and documentation 64496-64511 and 65536-65551 (RFC 5398); and it parses an AS_SEQUENCE, measures its length, extracts the origin AS, and strips private ASNs. Verified value: <!-- v:CLAIM-LIB-ASPATH-001.correct -->**17**
(`correct`), backed by [`modules/aspath/artifacts/aspath.json`](../modules/aspath/artifacts/aspath.json).

## Vendor it

Ships `aspath.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/7829e3aad06c9fd4a770fd4f97254e860e27061876df7f86b2b08af466e6fe84 --target .
```
