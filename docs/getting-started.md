# Getting started

Adopt Claim-Oriented Programming in an existing project in about 15 minutes.

## 1. Install and scaffold — one command each

```bash
pip install vericlaim        # or copy the zero-dependency vericlaim/ folder in
vericlaim init               # creates vericlaim.toml + claims/ (won't overwrite)
```

`vericlaim init` writes three files and nothing else:
`vericlaim.toml` (config), `claims/register.yaml` (empty register),
`claims/baseline.json` (empty baseline). Run `vericlaim` now — a project with no
claims yet is a valid, **passing** state, so you are never greeted by a failure.

Open `vericlaim.toml` and point `doc_globs` at the docs you want guarded:

```toml
[vericlaim]
doc_globs = ["README.md", "docs/*.md"]
```

## 2. Write your first claim

Whenever a doc states a number, register it. Put the number in
`claims/register.yaml` as the single source of truth:

```yaml
claims:
  - id: CLAIM-PERF-001
    statement: >
      The parser handles the 10k-line fixture in under 200 ms on CI hardware.
    evidence_level: benchmarked
    artifact:
      - results/parse_bench.json
    metrics:
      p95_ms: 180
    caveat: >
      CI hardware only; single fixture; not a latency guarantee under load.
    reproduce: "python bench/parse.py"
```

Commit the artifact it points to (`results/parse_bench.json`) — produced by a
deterministic script, not by hand.

## 3. Bind the doc to the claim

In your doc, anchor the number so it can't drift:

```markdown
<!-- claim:CLAIM-PERF-001 p95_ms -->
The parser processes the 10k-line fixture with a p95 latency of **180 ms**.
```

The anchor says: "the value of `CLAIM-PERF-001.p95_ms` (=180) must appear in the
paragraph that follows." Change the prose to 190 without updating the register
and the gate fails.

## 4. Run the gate

```bash
python -m vericlaim
```

It prints `[OK]` or a precise list of what drifted, with file:line.

## 5. Grandfather what you can't fix yet

Large existing projects will have violations on day one. Put their `error_id`s
in `claims/baseline.json` so they report as WARN, not FAIL:

```json
{
  "known_violations": [
    { "error_id": "artifact-missing:CLAIM-OLD-003:results/legacy.json",
      "reason": "artifact lives in the private data repo; restore in Q3",
      "added": "2026-07-03" }
  ]
}
```

New violations still fail. The gate also tells you when a baseline entry no
longer occurs, so you can delete it.

## 6. Wire it into CI

Copy `.github/workflows/claim-gate.yml`. It regenerates evidence artifacts,
fails if they changed (evidence must be committed and current), runs the gate,
tests, and lint. From now on, no PR can merge a claim its evidence doesn't
support.

## Next

- The methodology and its Design-by-Contract lineage: [`manifesto.md`](manifesto.md)
- The register format in detail: [`claim-register-spec.md`](claim-register-spec.md)
- The evidence taxonomy: [`evidence-levels.md`](evidence-levels.md)
- A full worked example: [`../examples/rle/`](../examples/rle/)
