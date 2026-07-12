# BGP AS-path + ASN classification

*Subject area: Telecom / BGP Routing. Language: python. Vendorable bundle `f85e2208c93c`.*

Every BGP route carries an AS-path -- the list of Autonomous Systems it traversed -- and operators constantly reason about it: how long is it (shorter is preferred), who originated it, and are any ASNs private or reserved (which must not leak to the public Internet). The private, reserved, and documentation ASN ranges are fixed by RFCs 6996/7300/5398/7607/6793. This module parses the path and classifies ASNs against those ranges; the claim proves the classification matches the published boundaries, so you inherit a checked routing helper rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-ASPATH-001 correct -->
The vendored BGP AS-path library classifies every one of a fixed 17-ASN battery correctly against the published RFC allocations (correct = 17, errors = 0), pinning both sides of every boundary: private 64512-65534 and 4200000000-4294967294 (RFC 6996), reserved 0 (RFC 7607), 23456 AS_TRANS (RFC 6793), 65535 and 4294967295 last-ASN (RFC 7300), and documentation 64496-64511 and 65536-65551 (RFC 5398); and it parses an AS_SEQUENCE, measures its length, extracts the origin AS, and strips private ASNs. Verified value: <!-- v:CLAIM-LIB-ASPATH-001.correct -->**17**
(`correct`), backed by [`modules/aspath/artifacts/aspath.json`](../modules/aspath/artifacts/aspath.json).

## Vendor it

Ships `aspath.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/f85e2208c93c139650c84753ec454be90eabf0776832bc2040e156fdb489fa4b --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **RFC 4271** — A Border Gateway Protocol 4 (BGP-4). [https://www.rfc-editor.org/info/rfc4271](https://www.rfc-editor.org/info/rfc4271)
- **RFC 6996 (BCP 6)** — Autonomous System (AS) Reservation for Private Use. [https://www.rfc-editor.org/info/rfc6996](https://www.rfc-editor.org/info/rfc6996)
- **RFC 5398** — Autonomous System (AS) Number Reservation for Documentation Use. [https://www.rfc-editor.org/info/rfc5398](https://www.rfc-editor.org/info/rfc5398)
- **RFC 6793** — BGP Support for Four-Octet Autonomous System (AS) Number Space. [https://www.rfc-editor.org/info/rfc6793](https://www.rfc-editor.org/info/rfc6793)
