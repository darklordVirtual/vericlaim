---
name: claim-oriented-programming
description: >
  Enforce Claim-Oriented Programming with vericlaim: never state a number,
  benchmark, accuracy, latency, cost, "supports X", "0 failures", "N× faster",
  or any factual assertion — in a README, doc, paper, changelog, or code comment
  — unless it is a registered claim backed by a committed artifact. Use this
  skill BEFORE writing any such assertion, whenever you update a result or
  capability, and always in a repository that contains a vericlaim.toml. It
  prevents fabricated numbers and stops documentation from silently drifting
  from the evidence.
---

# Claim-Oriented Programming (with vericlaim)

A **claim** is a contract between what a project says about itself and the
evidence on disk. Design by Contract, lifted from functions to the whole
project, checked in CI. Your job, every time you write or change a factual
assertion, is to keep that contract intact — and to *refuse* to write one you
cannot back.

## The one rule

> **No number without an artifact. No doc number that isn't bound to the
> register. No claim described above the evidence it has.**

If you cannot point to a committed artifact, you have three honest moves —
produce the artifact, register the claim at `theoretical` and say so, or do not
write the number. There is no fourth move.

## STOP — the reflex

The instant you are about to type a factual figure or capability, stop and ask:

1. **What committed artifact establishes this?** If none exists, you are about to
   fabricate. Go produce it, or don't write the number.
2. **Is it in the register?** If not, register it first.
3. **Does the register value match what I'm about to write?** If not, the
   register wins — change the register first, then the prose.
4. **Does the prose carry the caveat?** A number without its scope is a liability.

Only after all four pass do you write the sentence.

## Rationalizations that mean STOP

If you catch yourself thinking any of these, you are about to break the contract:

| The thought | The reality |
|-------------|-------------|
| "This number is obviously about right." | "About right" is fabrication. Measure it. |
| "I'll add the benchmark artifact later." | Later never comes; the claim ships unsourced. Artifact first. |
| "It's just a rough figure in the README." | The README is where readers trust you most. Source it or cut it. |
| "The paper already says 2.8×, I'll match it." | Match the *artifact*, not another doc. If they disagree, the artifact decides. |
| "A plausible citation is better than none." | A fabricated citation is a review-killer. No source → no citation. |
| "I'll tweak the prose number, it's faster than re-running." | That IS the drift the gate exists to stop. Change the register, regenerate, rebind. |
| "The caveat makes it look weaker." | The caveat is part of the claim. Ship both or neither. |
| "The gate is being pedantic; I'll work around it." | The gate names the exact drift. Fix the drift, never the gate. |

## The procedure

1. **Produce the evidence first.** Run or write a *deterministic* script that
   measures the thing and commit the artifact it writes (e.g. `results/*.json`).
   Never hand-type a result — regenerate it so the file and the number always
   agree.

2. **Register the claim** (`claims/register.yaml`):
   ```yaml
   - id: CLAIM-AREA-001
     statement: "One line: what is claimed."
     evidence_level: benchmarked   # theoretical < measured < benchmarked < reproduced < externally_validated
     artifact: [results/example.json]
     metrics: { value: 42 }        # numbers the docs will quote
     caveat: "Scope and limitation — part of the claim."
     reproduce: "python bench/example.py"
   ```
   Grade `evidence_level` **conservatively**: describe a claim only at the level
   it has earned. Demotion is always allowed; promotion needs new evidence.

3. **Bind the doc** with an anchor immediately before the prose:
   ```markdown
   <!-- claim:CLAIM-AREA-001 value -->
   The measured value is **42** on the reference corpus.
   ```
   Every field in the anchor (a `metrics` key, or `n` for sample size) must
   appear as that exact number in the paragraph that follows.

4. **Run the gate:** `vericlaim` (or `python -m vericlaim`). It must print `[OK]`.

## Right vs wrong

**Wrong** — an unsourced number typed straight into a doc:
```markdown
Our encoder compresses data by about 8× on typical inputs.
```
"about 8×", "typical inputs" — no artifact, no scope, no register entry.

**Right** — evidence, register, bound doc:
```markdown
<!-- claim:CLAIM-EX-001 overall_ratio -->
The encoder achieves 8.0584× overall compression on the fixed example corpus
(a demonstration corpus chosen for its run structure; RLE can expand
low-redundancy data — see the register caveat).
```

## When the gate fails

It tells you the exact `file:line` and what drifted. **Fix the drift, never the
gate.** If a number legitimately changed: change the register first, regenerate
the artifact, then update every doc paragraph the gate lists. The gate is your
to-do list of places to fix — trust it.

## Hard don'ts

- Do not invent a plausible-looking number, benchmark, or citation.
- Do not quote a number without its caveat.
- Do not delete negative results or caveats to look better — a register of only
  wins is not trustworthy.
- Do not hand-edit `claims/manifest.md` hashes to pass the gate; regenerate the
  artifact.
- Do not silently weaken an `evidence_level`; if evidence weakens, demote and
  note it.

## Incremental adoption

Landing a change before its evidence exists? Add the gate's reported `error_id`
to `claims/baseline.json` with a reason and date — it becomes a WARN, not a
failure. New violations still fail; the gate tells you when a baseline entry is
no longer needed so you can delete it. The baseline is for known, tracked debt
only — never a way to silence a fresh problem.

## Setup from scratch

```bash
pip install vericlaim      # or copy the zero-dependency vericlaim/ folder in
vericlaim init             # scaffolds vericlaim.toml + claims/ (never overwrites)
vericlaim                  # a fresh project with no claims yet passes
```

## References

- Methodology and Design-by-Contract lineage: `docs/manifesto.md`
- Register format and anchors: `docs/claim-register-spec.md`
- Evidence taxonomy and demotion rules: `docs/evidence-levels.md`
- Worked example (a different domain): `examples/rle/`

---

*Claim-Oriented Programming and vericlaim by Stian Skogbrott. Cite as in
`CITATION.cff`.*
