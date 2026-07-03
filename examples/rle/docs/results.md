# RLE Example — Results

This document's numbers are **bound to the claim register** via the anchors
below. Change a number here without changing `claims/register.yaml` and the
vericlaim gate fails the build. That is Claim-Oriented Programming: the prose
cannot drift from the evidence.

## Compression

<!-- claim:CLAIM-EX-001 overall_ratio n -->
On the fixed example corpus of 4 files, the run-length encoder achieves an
overall compression ratio of **8.0584x**. This is a demonstration corpus chosen
for its run structure — on data with few runs, RLE can expand the input (that
caveat is part of the claim; see the register).

## Losslessness

<!-- claim:CLAIM-EX-002 n_roundtrip_lossless -->
Encoding then decoding reproduces the original bytes exactly: **4** of 4 files
round-trip losslessly.

Artifact: [`../artifacts/rle_bench.json`](../artifacts/rle_bench.json) ·
Reproduce: `python examples/rle/bench.py`
