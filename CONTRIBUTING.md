# Contributing

This project is built with Claim-Oriented Programming, so contributing has one
rule beyond the usual:

> **Every number or capability you state in a doc must be a registered claim
> backed by a committed artifact.**

## The workflow

1. **Produce evidence first.** Write the deterministic script that measures the
   thing, run it, and commit the artifact it produces. Never hand-write a
   result number.
2. **Register the claim** in `claims/register.yaml` (id, statement,
   evidence_level, artifact, caveat; add `metrics`/`n` for anything a doc will
   quote). Grade the evidence level honestly — conservatively.
3. **Bind the docs** to the claim with `<!-- claim:ID field ... -->` anchors.
4. **Run the gate**: `python -m vericlaim`. It must print `[OK]`.
5. **Run tests and lint**: `pytest -q` and `ruff check .`.

If you change a number, change it **in the register first**; the gate lists
every doc paragraph that still carries the old value.

## Non-negotiables

- No claim without an artifact. If you can't produce one, don't state the
  number — or register it at `theoretical` and say so.
- The caveat is part of the claim. Ship both or neither.
- Don't remove negative results or caveats to make something look better.
- Don't edit `claims/manifest.md` hashes by hand to make the gate pass;
  regenerate the artifact.
- Add a fixed defect to the stale-string denylist in `vericlaim.toml` when you
  correct a recurring wording so it can never come back.

## Adopting incrementally

If you must land a change before its evidence exists, add the gate's `error_id`
to `claims/baseline.json` with a reason and a date. New violations fail; the
baseline is for known, tracked debt only — and the gate tells you when an entry
is no longer needed.
