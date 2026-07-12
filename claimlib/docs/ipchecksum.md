# RFC 1071 Internet checksum

*Subject area: Telecom / Packet Processing. Language: python. Vendorable bundle `22183fde2f3d`.*

The Internet checksum (RFC 1071) protects IPv4, ICMP, UDP and TCP headers: sum the data as 16-bit big-endian words in one's-complement arithmetic (folding carries back in), then take the complement; a receiver that sums the whole datagram including the checksum gets all-ones, whose complement is zero. This module computes and verifies it directly; the claim proves it reproduces the published IPv4 example and agrees with an independent implementation, so you inherit a checked, dependency-free checksum for packet tooling rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-IPCHECKSUM-001 reference_vectors_matched -->
The vendored RFC 1071 Internet checksum reproduces every value in a fixed 268-vector reference set with 0 mismatches: the published IPv4-header worked example (header 4500 0073 0000 4000 4011 0000 c0a8 0001 c0a8 00c7 checksums to 0xb861), the verify round-trip (inserting 0xb861 makes the full header checksum to 0), and 266 byte strings (empty, odd/even lengths, all-zero / all-0xFF, and every single byte value 0..255) that agree with an independent struct-based implementation computed in the evidence. Verified value: <!-- v:CLAIM-LIB-IPCHECKSUM-001.reference_vectors_matched -->**268**
(`reference_vectors_matched`), backed by [`modules/ipchecksum/artifacts/ipchecksum.json`](../modules/ipchecksum/artifacts/ipchecksum.json).

## Vendor it

Ships `ipchecksum.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/22183fde2f3d3dc60d26924117a78a42b607b0f852cdcdb67fe52fd6d261ee9f --target .
```
