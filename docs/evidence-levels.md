# Evidence levels

Every claim carries an **evidence level** — how strongly it is established. A
claim may never be described above its earned level, and a demotion is always
allowed. The ladder is configured in `vericlaim.toml` (`evidence_levels`);
tailor it to your domain. The default ladder, weakest to strongest:

| Level | Meaning | Typical artifact |
|-------|---------|------------------|
| `theoretical` | An argument or derivation; not measured. | a proof note, a spec |
| `measured` | Observed once, in-house, on your own inputs. | a result JSON from one run |
| `benchmarked` | Measured on a defined benchmark/corpus, reproducibly. | a committed benchmark artifact + reproduce command |
| `reproduced` | Reproduced independently (another machine/person/config). | a second run's artifact, provenance recorded |
| `machine_checked` | Formally verified by a checker for the whole stated scope — a proof object, exhaustive model check, or SMT proof, re-run by `reproduce`. | a committed proof object + the checker's verdict artifact |
| `externally_validated` | Confirmed by a party outside the project. | an external report, third-party benchmark |

`machine_checked` sits above `reproduced` because a proof covers its *entire
stated scope*, not just the runs you happened to make — but it is still the
project grading itself, which is why `externally_validated` stays on top. Grade
it honestly: a Lean/Coq artifact earns it outright; a bespoke checker (like the
theorem example's) earns it only with the caveat saying the checker itself is
not an audited kernel. Mathematical theorems are the archetype — see
[`examples/theorem/`](../examples/theorem/) — but an exhaustive model check or
an SMT-verified invariant qualifies the same way: commit the proof/model as the
artifact and let `reproduce` re-run the checker.

## Rules the gate enforces

1. A claim's `evidence_level` must be one of the configured levels
   (unknown level → fail).
2. If a document names a claim id **and** an evidence-level word on the same
   line, they must agree with the register (e.g. calling a `measured` claim
   `externally_validated` in prose → fail). The taxonomy doc itself is excluded
   via `evidence_exclude`.

## Rules the gate cannot enforce (your discipline)

- Choosing the honest level in the first place. The gate checks *consistency*,
  not *truthfulness of the grade*. Grade conservatively.
- Demoting when a result weakens. If external replication fails, drop the level
  and say so — the gate will not stop you, and honesty is the point.

## Why levels, not just true/false

A binary "verified / not" tempts a project to call everything verified. A ladder
forces an explicit, visible judgment: *how well do we actually know this?* The
highest levels — reproduced, externally-validated — are the ones a reviewer
trusts, and they are exactly the ones a project cannot grant itself. Keeping the
distinction in the register makes the strength of each claim legible at a
glance.
