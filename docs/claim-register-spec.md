# Claim register specification

The register (`claims/register.yaml`) is the single source of truth for every
claim a project makes about itself.

## Structure

```yaml
schema_version: "1"

claims:
  - id: CLAIM-XXX-001          # unique; convention: CLAIM-<AREA>-<n>
    statement: >               # what is claimed, in prose
      folded block scalar joined with spaces ...
    evidence_level: benchmarked
    artifact:                  # one or more committed files that establish it
      - results/x.json
    n: 100                     # optional: a sample size docs can bind to
    metrics:                   # optional: machine-readable numbers docs bind to
      p95_ms: 180
      accuracy_pct: 88.0
    caveat: >                  # the scope/limitation; part of the claim
      ...
    reproduce: "python bench/x.py"   # optional: how to regenerate the artifact
```

## Required fields

`id`, `statement`, `evidence_level`, `artifact`, `caveat`. Configurable via
`required_fields` in `vericlaim.toml`.

- **id** — unique across the register. Duplicate ids fail the gate.
- **statement** — the claim in words.
- **evidence_level** — one of the ordered levels in `vericlaim.toml`
  (see [`evidence-levels.md`](evidence-levels.md)).
- **artifact** — a string or list of repo-relative paths that must exist. This
  is the "no claim without an artifact" rule.
- **caveat** — the scope and limitation. A claim without a caveat is not done.

## Optional fields

- **n** — a sample size; anchors can bind to it with the key `n`.
- **metrics** — a flat map of `name -> number`. Anchors bind doc prose to these
  values; this is how documentation is prevented from drifting.
- **reproduce** — the command that regenerates the artifact. It powers two
  checks: `vericlaim reproduce` re-runs it and requires the artifact to come
  out byte-identical (the number still holds), and — when `require_provenance`
  is on — a claim with a `reproduce` command must carry a provenance sidecar
  for each artifact (source-file-only claims are exempt).

## Anchors: binding docs to the register

In any doc under `doc_globs`, an HTML comment ties following prose to a claim:

```markdown
<!-- claim:CLAIM-XXX-001 p95_ms n -->
The parser handles all 100 fixtures with a p95 of 180 ms.
```

Rule: for each field listed in the anchor, that field's value from the register
must appear as a number in the paragraph immediately after the anchor. `n` binds
to the `n` field; every other name binds to `metrics[name]`. A missing value, an
unknown metric, or an unknown claim id fails the gate.

## Supported file format

The bundled parser handles a restricted YAML subset: `claims:` at the top level,
`- id:` items, scalar fields, `>`/`|` folded block scalars, string lists, and
one-level `key: value` maps (for `metrics`). This keeps the gate
zero-dependency. If PyYAML is installed, it is used automatically and the full
YAML grammar is available.

## Discipline

Update numbers **in the register first**, then update the anchored docs — the
gate will tell you exactly which doc paragraphs still carry the old value.
Never edit an artifact by hand; regenerate it from its `reproduce` command so
the number and the file always agree.
