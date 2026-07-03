# Artifact Manifest

SHA-256 over committed (LF) file bytes. The gate recomputes each hash and fails
on mismatch, so a silently-edited result artifact is caught in CI. On a Windows
(CRLF) working tree the LF-normalized form is matched with a note.

| File | SHA-256 |
|------|---------|
| `examples/rle/artifacts/rle_bench.json` | `78566810996df27fd5c3fb0772b4d3929c9663c9ab984ef04a0d918ef6f869c7` |
