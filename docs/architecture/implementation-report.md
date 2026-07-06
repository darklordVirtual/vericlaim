# Gold-standard lift — implementation report

**Purpose.** The single accountable record of what this lift changed, what it
proves, and what it deliberately still does not. Read with
[`gold-standard-plan.md`](gold-standard-plan.md) (the phased plan) and
[`../security/security-model.md`](../security/security-model.md) (the guarantees).

## Executive summary

The lift hardened the trusted core along three axes without adding a runtime
dependency:

1. **One fail-closed path policy.** All untrusted-string→path handling — gate
   artifacts, manifest rows, literature, and remote bundle read/write — now goes
   through a single adversarially-tested module (`vericlaim/pathsafe.py`),
   closing a real bundle traversal-write vector on both the read and write side.
2. **Reproduction that cannot be faked by a no-op.** A declarative runner
   (`vericlaim/repro.py`) executes a spec in an empty isolated directory where
   every declared output must be created from scratch — the core weakness of the
   legacy "artifact unchanged" check is gone. Shell parsing is removed
   (`shell=False`); timeouts kill the whole process group.
3. **Secure-by-default profiles.** `adopt` / `strict` / `enterprise`: strict and
   enterprise force provenance + git-tracking on and reject legacy shell
   reproduction, regardless of what the config file requests.

Everything is verified green: **257 tests**, gate passes under both `adopt` and
`strict`, `ruff check` clean.

## Changed files by phase

| Phase | Files |
|-------|-------|
| 1.1 path safety | `vericlaim/pathsafe.py` (new), `vericlaim/gate.py`, `integrations/library/bundlefmt.py`, `integrations/library/import_bundle.py`, `tests/test_pathsafe.py` (new), `tests/test_library_import.py` |
| 1.2 declarative reproduce | `vericlaim/repro.py` (new), `vericlaim/reproduce.py`, `tests/test_repro.py` (new), `tests/test_provenance_and_reproduce.py` |
| 3 profiles | `vericlaim/config.py`, `vericlaim/cli.py`, `vericlaim.toml` |
| 4 docs & policy | `docs/README.md`, `docs/security/security-model.md`, `docs/architecture/reproduction-model.md`, `docs/reference/configuration.md`, `SECURITY.md`, `ROADMAP.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`, `SUPPORT.md` |
| 5 diagrams | `docs/diagrams/trust-boundaries.md`, `docs/diagrams/reproduction-sandbox-sequence.md` |

## Security findings addressed

| # | Finding | Severity | Fix | Regression test |
|---|---------|----------|-----|-----------------|
| S1 | Bundle manifest key like `../escape` could make `import_bundle` **write outside** the vendor dir | High | `safe_join` on every write path + `check_bundle_id` | `test_library_import.py::test_malicious_manifest_path_is_rejected`, `test_pathsafe.py` |
| S2 | `verify_bundle` never rejected unsafe manifest keys — the **read** side of the same vector | High | `check_relpath` on every manifest key before any path is built | `test_library_import.py::test_malicious_manifest_path_is_rejected` |
| S3 | Symlink escape could name an artifact/manifest path outside the repo | Medium | `pathsafe.safe_join` symlink-aware containment | `test_pathsafe.py` (file + dir symlink escape) |
| S4 | A no-op `reproduce` command passed because the stale artifact was unchanged | Medium | declarative runner: output must be created from scratch in an empty dir | `test_repro.py::test_noop_command_fails` |
| S5 | Legacy shell reproduction ran unstructured shell in all modes | Medium | `shell=False` argv; strict/enterprise reject legacy shell | `test_repro.py::test_legacy_string_rejected_in_strict` |
| S6 | Config could not express a secure baseline | Low | strict/enterprise force provenance + git-tracking, ignore weakening flags | covered by gate runs under `--profile strict` |

(Earlier in the cycle, also closed: unbalanced-fence drift, unverified provenance
hash, unchecked register metrics, and the Cloudflare P1/P2 set — see `CHANGELOG.md`.)

## Migration guide

- **Existing adopters:** nothing breaks. The default profile stays `adopt`. If
  your register uses string `reproduce` commands, set `allow_legacy_shell = true`
  in `vericlaim.toml` (as this repo now does) — otherwise `reproduce` will refuse
  them as a nudge toward the declarative form.
- **Moving to strict:** run `vericlaim --profile strict`. Expect it to require
  provenance sidecars and git-tracked artifacts, and to reject legacy shell
  reproduction. Convert `reproduce` entries to the declarative form (see the
  reproduction model) before `reproduce --profile strict` will pass.

## Documentation map

Start at [`../README.md`](../README.md). Security truth:
[`security-model.md`](../security/security-model.md). Reproduction:
[`reproduction-model.md`](reproduction-model.md). Config & profiles:
[`../reference/configuration.md`](../reference/configuration.md). Deferred work:
[`../../ROADMAP.md`](../../ROADMAP.md).

## Diagram inventory

| Diagram | Purpose | Source |
|---------|---------|--------|
| Trust boundaries | which inputs are untrusted | `docs/diagrams/trust-boundaries.md` |
| Reproduction sandbox sequence | why a no-op can't pass | `docs/diagrams/reproduction-sandbox-sequence.md` |

Both are GitHub-renderable Mermaid with purpose, assumptions, legend, and an
alt-text narrative. Pinned-CLI CI render validation is a roadmap item.

## Commands that must pass

```bash
python3 -m vericlaim                       # gate, adopt      -> [OK] 15 claims
python3 -m vericlaim --profile strict      # gate, strict     -> [OK]
python3 -m vericlaim reproduce             # adopt, legacy allowed -> [OK]
python3 -m pytest -q                       # 257 passed
python3 -m ruff check .                    # clean
```

`python3 -m vericlaim reproduce --profile strict` **intentionally fails today**:
it correctly refuses the register's legacy shell commands. Making it pass
requires converting the register to declarative specs — blocked on the parser
contract (below) and tracked in the roadmap.

## Deferred (honest, tracked)

See [`../../ROADMAP.md`](../../ROADMAP.md). The load-bearing deferrals:

- **Full strict-reproduce dogfooding** — blocked: the zero-dependency register
  parser cannot represent the nested `reproduce:` map without PyYAML. Coupled to
  the parser-contract decision.
- **Schema-v2 metric bindings** (JSON Pointer + comparators + Decimal),
  typed-dataclass migration, parser contract.
- **True sandboxed runner** — until then `network_enforced` is always false.
- **Signed provenance / attestation, SBOM, CI render/scan pipeline, SSRF
  controls, Cloudflare scoped-token model.**

## What this lift still cannot prove

The gate proves **internal consistency and reproducibility**, not truth. It does
not prove a benchmark is production-realistic, that evidence was not manipulated
before commit, that `externally_validated` was externally validated, or that a
*sentence* is correct — doc binding proves a number is present and matches the
register, not that the surrounding prose is true. Reproduction isolates outputs
and blocks shell parsing but is not an OS sandbox. Where a stronger guarantee is
named but not implemented, it lives in the roadmap, never in the README.
