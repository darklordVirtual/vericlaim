# Byte run-length codec (lossless round-trip)

*Subject area: Data / Compression. Language: python. Vendorable bundle `c7b94d0314d5`.*

Run-length encoding is the simplest lossless compression scheme: it replaces each maximal run of identical symbols with a (count, symbol) pair, shrinking long uniform stretches (bitmaps, sparse buffers, padded records) while leaving a total, exactly invertible mapping. This module implements the classic byte-pair variant, splitting runs longer than 255 across pairs so any bytes input encodes and decodes back byte-for-byte. Vendor it when you need a dependency-free, auditable codec whose inverse is proven; the claim binds the round-trip property so you inherit a checked codec rather than a re-implementation to re-audit.

## Claim

<!-- claim:CLAIM-LIB-RLE-001 roundtrip_lossless -->
The vendored byte-oriented run-length codec round-trips losslessly on every case in a fixed, diverse corpus (long runs, sparse spikes, deterministic pseudo-random noise, structured text, and the empty string): decode(encode(x)) == x for all 15 cases (roundtrip_lossless == n_cases), verified by exact byte equality against the original input, not against the codec's own output. Verified value: <!-- v:CLAIM-LIB-RLE-001.roundtrip_lossless -->**15**
(`roundtrip_lossless`), backed by [`modules/rle/artifacts/rle.json`](../modules/rle/artifacts/rle.json).

## Vendor it

Ships `rle.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/c7b94d0314d5b22f69dadf16c7cd407722ed656270f8b663e15696bacb6f734f --target .
```
