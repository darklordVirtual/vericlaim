# Configuration reference

**Purpose.** Document every `vericlaim.toml` setting and the three policy
profiles. Scope: the core gate configuration (`vericlaim/config.py`).

## Profiles

Set `profile` in `[vericlaim]`, or override with `--profile` on the CLI.

| Profile | Purpose | Key behavior |
|---------|---------|--------------|
| `adopt` | Low-friction onboarding for an existing repo | Permissive; baseline entries and legacy metric inference allowed; legacy shell reproduce allowed **only** with `allow_legacy_shell = true`; provenance/git-tracking optional |
| `strict` | Recommended production destination — **secure by default** | Forces `require_provenance` and `require_git_tracked` on; **rejects** legacy shell reproduce; declarative reproduction only |
| `enterprise` | Regulated / externally audited projects | Strict controls **plus** roadmap items: signed/attested provenance, sandboxed runners, SBOM, zero expired baselines (see `../../ROADMAP.md`) |

`strict` and `enterprise` **ignore** file settings that would weaken security:
`allow_legacy_shell` is forced false, and provenance/git-tracking are forced on,
regardless of what the file requests. Secure-by-default is not overridable
downward by the file — only `adopt` is permissive.

## Settings

| Key | Type | Default | Meaning |
|-----|------|---------|---------|
| `profile` | string | `adopt` | `adopt` \| `strict` \| `enterprise` |
| `allow_legacy_shell` | bool | `false` | Honor legacy string `reproduce` commands (adopt only) |
| `register` | path | `claims/register.yaml` | The claim register |
| `baseline` | path | `claims/baseline.json` | Grandfathered violations. Each entry grandfathers exactly `count` occurrences of its `error_id` (default 1) — a new occurrence of a baselined problem still fails. |
| `manifest` | path | *(unset — off)* | Artifact SHA-256 manifest. OPT-IN: unset means the manifest checks are explicitly off. Once configured, a missing file is a **hard failure** (deleting the manifest cannot silently disable hash verification). `strict`/`enterprise` additionally require a manifest whenever any claim is reproducible. |
| `doc_globs` | list | `["README.md","docs/**/*.md"]` | Docs scanned for anchors/value tokens |
| `code_globs` | list | `[]` | Source files scanned for comment anchors |
| `required_fields` | list | id/statement/evidence_level/artifact/caveat | Fields every claim must have |
| `evidence_levels` | list | the six-rung ladder | Ordered weakest→strongest |
| `evidence_exclude` | list | `[]` | Docs exempt from the evidence-citation check |
| `stale_exclude` | list | `[]` | Docs exempt from stale-string checks |
| `require_provenance` | bool | `false` (adopt) / `true` (strict) | Produced artifacts need a provenance sidecar |
| `require_git_tracked` | bool | `false` (adopt) / `true` (strict) | Artifacts must be git-tracked |
| `[vericlaim.stale_strings]` | table | `{}` | `"forbidden" = "why / use instead"` |
| `require_assumes` | bool | `false` (adopt/strict) / `true` (enterprise) | A claim stating a metric must declare a machine-readable `assumes` precondition, not scope-in-prose only |
| `front_page` | list | `["README.md"]` | Documents where an unshipped capability may not be stated as present, and where a superseded claim may not be anchored |
| `roadmap` | path | *(unset — off)* | Roadmap file whose every entry must be classified in `[vericlaim.capabilities]` |
| `coverage_allow` | list | `[]` | Extra regexes for numeric shapes coverage must not count as claims (on top of ISO dates, years, semver, hash fragments) |
| `coverage_artifact` | path | *(unset — off)* | Where `vericlaim coverage --write` stores its report, and where the gate reads `unbound_numbers` for the ratchet |
| `[vericlaim.capabilities]` | table | `{}` | `"capability" = "shipped"` \| any other class. A non-shipped capability may not be stated as present on a front-page document |
| `[vericlaim.ratchet]` | table | `{}` | `metric = ceiling`. Quantities allowed to fall, never to rise — see below |

## The ratchet

Eiffel's loop variant is an integer that must strictly decrease; it is how a
loop proves it terminates. A repository has the same need and no such
mechanism, so the debt you tolerate today has nothing stopping it from growing
tomorrow — every individual increase looks reasonable in review.

```toml
[vericlaim.ratchet]
legacy_shell_claims      = 0    # claims still reproduced by a shell string
baselined_findings       = 0    # violations parked in the baseline
claims_without_reproduce = 2    # claims whose number cannot be re-checked
claims_without_assumes   = 13   # claims whose scope is prose only
unbound_numbers          = 44   # doc literals no anchor binds
```

Exceeding a ceiling **fails the gate**, and ratchet findings are never
grandfathered by the baseline: a ceiling you can baseline past is not a
ceiling. Coming in *under* one prints a note telling you to tighten it, so the
ceiling tracks reality downward. `unbound_numbers` is read from
`coverage_artifact`; if that is unset or unreadable the metric is reported as
**unmeasured**, never as zero.

## The capability contract

A claim register stops a *number* from drifting. It does nothing about a
capability that is designed, prototyped or merely intended being written up in
the present tense — the most common way an honest project overstates itself,
and the one an assistant reproduces most readily, because roadmap prose and
shipped prose look identical to a model summarising a repository.

```toml
roadmap = "ROADMAP.md"
[vericlaim.capabilities]
"declarative reproduce" = "shipped"
"sandboxed runner"      = "designed"
```

Two mechanical rules: a term classified anything but `shipped` may not appear
on a front-page document unless the surrounding sentences carry a hedge
(`roadmap`, `planned`, `designed`, `not yet`, `proposed`, ...); and every
roadmap entry must be classified, so the roadmap and the table cannot drift
apart. The check never guesses at tense — it looks for a declared term and a
declared hedge, which is why it produces almost no false positives.

## Example — recommended strict config

```toml
[vericlaim]
profile = "strict"
register = "claims/register.yaml"
manifest = "claims/manifest.md"
doc_globs = ["README.md", "docs/**/*.md"]
code_globs = ["src/**/*.py"]
```

Under `strict`, `allow_legacy_shell` cannot re-enable shell reproduction, and
`require_provenance` / `require_git_tracked` are on even if omitted here.
