# Artifact Manifest

SHA-256 over committed (LF) file bytes. The gate recomputes each hash and fails
on mismatch, so a silently-edited result artifact is caught in CI. On a Windows
(CRLF) working tree the LF-normalized form is matched with a note.

| File | SHA-256 |
|------|---------|
| `examples/rle/artifacts/rle_bench.json` | `78566810996df27fd5c3fb0772b4d3929c9663c9ab984ef04a0d918ef6f869c7` |
| `examples/greetings/artifacts/greetings.json` | `2759c18e03d9482e66e9a820ffd26dfd0b4811dabdeb214bd9f8f9619ad98fe2` |
| `examples/tipcalc/artifacts/tipcalc.json` | `65cdc526f3c0e3f973141ec1a732f13872af4e401e62ae1fa0a8738838311965` |
| `examples/theorem/artifacts/theorem.json` | `178ce1c1d30982e45e964bfa0430d2c76b01910e7bf41ea2f4fbb77126bbeed5` |
| `claims/version.json` | `da9da2c003b8eee13e6a8b295dadb7e37740a6616eadf890d60a353cc33d37d1` |
| `integrations/library/artifacts/research_layer.json` | `5ca046ba2c5f3914cdc9280fee76c1151f54bdcc4a87284199d56be726f558a9` |
