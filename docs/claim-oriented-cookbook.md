# The Claim-Oriented Programming cookbook

Practical recipes for making a project's claims about itself mechanically agree
with the evidence that produced them. Where [`manifesto.md`](manifesto.md)
argues *why* and [`getting-started.md`](getting-started.md) walks the first
claim, this is the day-to-day reference: the loop, the shapes, and reuse.

## The loop (memorize this)

Every claim is the same four moves, in this order:

1. **Produce evidence.** Write a deterministic script that *measures* the thing
   and writes a committed artifact (`results/*.json`). End it with `stamp()` so
   the artifact carries provenance. Never hand-type a result.
2. **Register it.** Add a claim to `claims/register.yaml` with an `id`, a
   conservatively-graded `evidence_level`, the committed `artifact` path, the
   `metrics` your docs will quote, and a `caveat`.
3. **Bind the docs.** Put `<!-- claim:ID field -->` immediately before the
   sentence that states the number; pin the literal with
   `<!-- v:ID.field -->**180**` when the paragraph holds other numbers.
4. **Run the gate.** `vericlaim` until it prints `[OK]`. When you changed code a
   benchmark depends on, also run `vericlaim reproduce`.

The order matters: artifact **first**, always. "I'll add the evidence later"
ships an unsourced claim, which is the exact failure the gate exists to catch.

## Scaffold a claim in one step

Typing the script, the register block and the anchor by hand is the friction
that makes people skip the discipline. `vericlaim new-claim` emits all three:

```bash
vericlaim new-claim CLAIM-PERF-001 \
    --statement "The parser handles the 10k-line fixture under 200 ms." \
    --metric p95_ms=180 --evidence-level benchmarked \
    --artifact results/parse_bench.json --script bench/parse_bench.py
```

It writes `bench/parse_bench.py` as a stub whose `measure()` you implement — it
**raises until you produce a real number**, so it can never fabricate one — and
prints the register block and the doc anchor to paste. It never edits your
register automatically, so it cannot corrupt it.

## Four claim shapes

Claims are not just benchmark numbers. The `examples/` gallery shows the same
discipline for four kinds of assertion; reach for the closest shape.

| Shape | Question it answers | Metric example | Evidence level |
|-------|--------------------|----------------|----------------|
| **capability count** | "supports how many?" | `n_languages: 6` | `measured` |
| **correctness** | "do all cases pass?" | `cases_passing: 12` | `benchmarked` |
| **benchmark ratio** | "how much better?" | `overall_ratio: 8.0584` | `benchmarked` |
| **proved theorem** | "does it verify?" | `steps_verified: 5` | `machine_checked` |

A benchmark's `caveat` is part of the claim: ship the number and its scope
together or neither. A count of only wins is untrustworthy — register the
negative results too.

## Grade evidence conservatively

Levels run weakest to strongest: `theoretical` < `measured` < `benchmarked` <
`reproduced` < `machine_checked` < `externally_validated`. A doc may never
describe a claim *above* the level it has earned; demotion is always allowed,
promotion needs new evidence. When you cannot back a number there are exactly
three honest moves: produce the artifact, register it as `theoretical` and say
so, or do not write the number.

## Bind numbers stated in code, too

Set `code_globs` in `vericlaim.toml` and a number in a source comment is held to
the register just like prose. The anchor is a whole-line comment; the value
lives in the comment block right after it (never in a code literal):

```python
# claim:CLAIM-CORE-001 n
# The engine handles 42 concurrent sessions before it sheds load.
MAX_SESSIONS = 42  # <- a literal here does NOT satisfy the claim; the comment does
```

Change the register to `n: 50` without editing the comment (or vice-versa) and
the gate fails with the exact `file:line`.

## Reuse verified code: the claim library

Beyond stating claims about *your* code, you can vendor code that already
carries its claim. [`claimlib/`](../claimlib/README.md) is a standard library of
small, stdlib-only building blocks — a CVSS scorer, a tamper-evident hash chain,
a Merkle tree, an RLE codec, a Luhn check, a SemVer resolver, a token-bucket
limiter, backoff, an RBAC/SoD checker, error-budget math — each packaged as a
content-addressed `bundle_v1` whose key property is a registered, evidence-
backed claim.

```bash
# Program with the claim behind you: vendor the byte-exact code + a binding test.
python3 integrations/library/use_code.py \
    --bundle claimlib/bundles/<bundle_id> --target .
# -> lib/<claim_slug>/<module>.py + tests/test_bundle_binding_<slug>.py
```

The generated binding test re-hashes the vendored files against the bundle
manifest, so **editing a vendored line fails your own test suite** — forking
becomes an explicit, visible decision (delete the binding test to own the
divergence). Prefer `import_bundle` instead when you want the claim itself
hash-locked into your register, so your own offline gate re-verifies its
provenance on every run.

The library is **distribution, not truth**: vendoring proves the code is
byte-exact to what produced the evidence and traceable to its source — it does
not re-validate the claim in your context. Read the module's caveat.

## What the gate does and does not prove

It proves the register, the evidence files, the bound docs and the reproduce
scripts stay **internally consistent and reproducible** on every commit. It does
*not* prove the benchmark reflects production, that evidence was not manipulated
before commit, that an `externally_validated` claim was truly external, or that
a bound sentence is *semantically* true — a paragraph anchor proves the number
is *present*, not that the prose around it is honest. Stay inside that boundary
when you describe the guarantee.
