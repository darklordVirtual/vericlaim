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
