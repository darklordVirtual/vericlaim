---
name: claim-oriented-programming
description: >
  Keep a project's claims backed by evidence and its documentation free of
  drift, using vericlaim. Use this skill whenever you add or change a number,
  benchmark result, accuracy figure, latency, capability statement, or any
  factual assertion in a README, doc, paper, or code comment — and always when
  working in a repository that contains a vericlaim.toml. It enforces "no claim
  without an artifact" and prevents docs from silently disagreeing with the
  evidence.
---

# Claim-Oriented Programming (with vericlaim)

Design by Contract, lifted from functions to the whole project: a **claim** is
a contract between what the project says about itself and the evidence on disk,
checked in CI. Your job, whenever you touch a factual assertion, is to keep that
contract intact.

## The one rule

**Never state a number or capability that is not a registered claim backed by a
committed artifact.** If you cannot point to an artifact, either produce one, or
downgrade the statement to `theoretical` and say so, or do not state it.

## When this skill applies

- You are about to write "X% accuracy", "N× faster", "handles M items",
  "0 failures", "supports Y", or any similar factual assertion — in any file.
- You are editing a repository that has a `vericlaim.toml`.
- You are asked to update a result, benchmark, or capability.

## The workflow (follow in order)

1. **Produce the evidence first.** Write or run a deterministic script that
   measures the thing and commit the artifact it writes (e.g. a `results/*.json`).
   Never hand-write a result number — regenerate it so the file and the number
   always agree.

2. **Register the claim** in the register (`claims/register.yaml` by default):
   ```yaml
   - id: CLAIM-AREA-001
     statement: "One line describing what is claimed."
     evidence_level: benchmarked      # theoretical|measured|benchmarked|reproduced|externally_validated
     artifact: [results/example.json] # the committed file that establishes it
     metrics: { value: 42 }           # numbers your docs will quote
     caveat: "Scope and limitation — this is part of the claim."
     reproduce: "python bench/example.py"
   ```
   Grade `evidence_level` **conservatively**. You may never describe a claim
   above its earned level; a demotion is always allowed. The `caveat` is
   mandatory — a number without its scope is a liability.

3. **Bind the doc to the claim** with an anchor immediately before the prose:
   ```markdown
   <!-- claim:CLAIM-AREA-001 value -->
   The measured value is **42** on the reference corpus.
   ```
   Each field in the anchor (`value`, or `n` for the sample size) must appear as
   that exact number in the following paragraph.

4. **Run the gate**: `vericlaim` (or `python -m vericlaim`). It must print
   `[OK]`. If it fails, it names the exact file:line and what drifted — fix that,
   do not work around it.

5. **When you change a number, change the register FIRST.** Then update every
   anchored doc paragraph the gate flags. The gate is the source of the list of
   places to fix — trust it.

## Hard "don'ts"

- Do not invent a plausible-looking number, benchmark, or citation. If it is not
  measured and committed, it does not go in.
- Do not quote a number without its caveat. Ship both or neither.
- Do not remove negative results or caveats to make something look better —
  a register of only wins is not trustworthy.
- Do not edit `claims/manifest.md` hashes by hand to make the gate pass;
  regenerate the artifact instead.
- Do not delete or weaken a claim's `evidence_level` silently; if evidence
  weakens, demote and note it.

## Incremental adoption

If you must land a change before its evidence exists, add the gate's reported
`error_id` to `claims/baseline.json` with a reason and date — this reports it as
a WARN instead of failing. New violations still fail. Remove baseline entries as
you fix them; the gate tells you when one is no longer needed.

## Setting it up from scratch

```bash
pip install vericlaim      # or copy the zero-dependency vericlaim/ folder in
vericlaim init             # scaffolds vericlaim.toml + claims/ (won't overwrite)
vericlaim                  # a fresh project with no claims yet passes
```

## References

- Methodology and Design-by-Contract lineage: `docs/manifesto.md`
- Register format: `docs/claim-register-spec.md`
- Evidence taxonomy: `docs/evidence-levels.md`
- Worked example: `examples/rle/`

---

*Claim-Oriented Programming and vericlaim by Stian Skogbrott. Cite as in
`CITATION.cff`.*
