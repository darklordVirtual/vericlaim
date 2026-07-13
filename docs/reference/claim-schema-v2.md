# Claim schema v2 — explicit metric bindings

**Purpose.** The reference for `metric_bindings`: typed, location-exact,
Decimal-safe bindings between a register metric and the artifact value that
establishes it. This is the schema-v2 replacement for v1's key scanning.

**Why it exists.** The v1 check (`check_metrics_match_artifact`) matches a
register value against ANY identically-named key in the artifact's JSON tree.
That catches typos, but an identically-named key elsewhere in the tree can
satisfy it — the register can say `count: 10` while the relevant value is 9,
as long as a decoy `count: 10` exists anywhere. A binding removes the
ambiguity: it names the artifact, the exact location, the expected type, and
the comparison.

## Shape

```yaml
claims:
  - id: CLAIM-PERF-001
    artifact:
      - results/parse_bench.json
    metrics:
      p95_ms: 180
    metric_bindings:
      - metric: p95_ms                     # required: the metrics key it binds
        pointer: /latency/p95_ms           # required: RFC 6901 JSON Pointer
        artifact: results/parse_bench.json # optional when the claim cites
                                           #   exactly one .json artifact
        type: number                       # optional: number | integer |
                                           #   string | boolean
        unit: ms                           # optional: recorded documentation
        comparator: exact                  # optional, default exact
        value: "180"                       # optional: defaults to
                                           #   metrics[metric]; a string
                                           #   parses exactly as Decimal
        tolerance: "0.5"                   # bounded comparator only
```

The list-of-flat-maps shape parses **identically** under the bundled
zero-dependency parser and PyYAML (the same contract as `literature:`
entries) — no nesting beyond one map per list item.

## Semantics

| Field | Rule |
|-------|------|
| `metric` | Must be a string. When the claim also lists the metric under `metrics:`, doc anchors keep binding to `metrics:` — the binding verifies the artifact side. A bound metric is **exempt from the v1 key scan** (the binding is strictly stronger). |
| `pointer` | RFC 6901: `""` is the whole document, `/a/b/0` descends objects and arrays, `~0`/`~1` unescape to `~`/`/`. Array indices are strict — digits only, no leading zeros, no `-`. An unresolvable pointer is a finding, never a skip. |
| `artifact` | Must be listed in the claim's `artifact`. May be omitted only when the claim cites exactly one `.json` artifact; with several, an omitted `artifact` is a finding (`binding-artifact-ambiguous`). |
| `type` | `number` (int or float, never booleans), `integer` (never booleans), `string`, `boolean`. Declared type mismatch is a finding. |
| `unit` | Free-text documentation, recorded with the binding. Not verified against anything — say what the number means. |
| `comparator` | See below. Unknown comparators are findings. |
| `value` | The register-side value. Omitted: falls back to `metrics[metric]`; with neither, `binding-no-value`. **A string value parses exactly as a Decimal literal** — write `value: "8.0584"` when the YAML float round-trip worries you. |
| `tolerance` | Required by `bounded`, ignored otherwise. Absolute, `>= 0`. |

### Comparators (artifact value ⋄ register value)

| Comparator | Passes when |
|------------|-------------|
| `exact` (default) | artifact == register |
| `minimum` | artifact >= register — the register states a floor ("at least 90 pass") |
| `maximum` | artifact <= register — the register states a ceiling ("p95 under 200 ms") |
| `bounded` | \|artifact − register\| <= tolerance |

Numeric comparison is **exact decimal arithmetic**: the artifact JSON is
parsed with `parse_float=Decimal` and the register value via
`Decimal(str(v))`, so `8.0584` compares as the literal `8.0584` — float
representation drift can neither cause nor mask a mismatch. Booleans are
never numbers: a `true` in the artifact does not satisfy a numeric binding.

## Failure modes (all fail closed)

`binding-value-mismatch` · `binding-pointer-missing` ·
`binding-type-mismatch` · `binding-artifact-ambiguous` ·
`binding-artifact-unclaimed` · `binding-artifact-unreadable` ·
`binding-no-value` · `binding-bad-comparator` · `binding-bad-type` ·
`binding-missing-tolerance` — plus `RegisterError` at load time for
structurally malformed bindings (non-list, non-map entries, non-string
`metric`/`pointer`).

## Migration from v1

Nothing breaks: `metrics:` keeps driving doc anchors, and unbound metrics
keep the v1 behavior (any-depth key match; absent keys fail under
strict/enterprise). Add bindings claim by claim; each bound metric leaves
the v1 scan. claimlib's build emits a binding for every register metric of
all 88 modules, so the knowledge register is fully on v2.

## Not in v2 (yet)

Cross-artifact expressions, derived metrics (ratios of two pointers),
schema validation of whole artifacts, and per-binding provenance are out of
scope — see `ROADMAP.md`.
