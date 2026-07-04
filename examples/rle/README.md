# RLE example — Claim-Oriented Programming in a different domain

This example applies vericlaim to **lossless compression** — a domain
deliberately unrelated to where the method was distilled — to show that the
discipline is domain-independent.

## The loop

1. **Code** — a tiny run-length encoder (`src/rle.py`).
2. **Evidence** — a deterministic benchmark (`bench.py`) writes
   `artifacts/rle_bench.json`.
3. **Claims** — registered in [`../../claims/register.yaml`](../../claims/register.yaml)
   (`CLAIM-EX-001` compression ratio, `CLAIM-EX-002` losslessness), each backed
   by that artifact.
4. **Docs** — [`docs/results.md`](docs/results.md) states the numbers behind
   claim anchors bound to the register.
5. **Gate** — `python3 -m vericlaim` verifies (3)↔(4)↔(2) all agree; CI also
   re-runs `bench.py` and fails if the committed artifact changed.

## Try the drift

Change `8.0584` to `9.0` in `docs/results.md` and run `python3 -m vericlaim` from
the repo root — it fails with the exact file:line. Restore it and it passes.
Change the corpus in `bench.py`, rerun it, and the gate points you at every doc
number that no longer matches. The prose can never quietly diverge from the
evidence.

## Reproduce

```bash
python3 examples/rle/bench.py     # regenerate the artifact
pytest tests/test_rle_example.py # test the code + that the artifact is current
```
