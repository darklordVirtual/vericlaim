# Security model — what vericlaim proves, and what it does not

**Purpose.** State precisely the guarantees the vericlaim core provides, the
threats it addresses, and — just as important — the guarantees it deliberately
does **not** make. This page is the honesty contract; every other doc defers to
it. Scope: the trusted core (`vericlaim/`). Integrations have their own models.

## The core statement

> vericlaim is a policy-governed, evidence-bound verification layer for
> repository claims. It detects specified classes of drift and integrity failure
> between a project's register, artifacts, provenance, documentation, and code.
> It does **not** claim to prove semantic truth, real-world validity, or external
> validation unless the required evidence and attestation are explicitly present
> and verified.

## What it proves (mechanically, fail-closed)

| Guarantee | Mechanism |
|-----------|-----------|
| Every cited artifact exists and lives inside the repo | artifact existence + `pathsafe` containment |
| No path traversal or symlink escape can name an artifact/manifest/bundle file | one central `pathsafe` policy, adversarially tested |
| A produced artifact records how it was made, and the recorded hash matches the file | provenance sidecar + hash verification |
| A register metric equals the value in its JSON artifact | `check_metrics_match_artifact` |
| A committed artifact matches its manifest SHA-256 | manifest hashing |
| A doc number equals its registered value (drift fails the build) | doc anchors + value tokens |
| A claim is not described above its registered evidence level | evidence-citation check |
| Under strict `reproduce`, a declared output is re-created **from scratch** | isolated-workspace declarative runner (a no-op fails) |
| A corrected wording cannot silently reappear | stale-string denylist |
| A cited literature source still hashes to its registered digest | literature integrity |

All parsing, schema, path, and policy decisions **fail closed**: an unparseable
register raises rather than reading zero claims; an unsafe path is rejected, not
normalized.

## What it does NOT prove (by design)

- **Semantic truth.** Doc binding proves a *number is present and matches the
  register*, not that the surrounding sentence is true.
- **Real-world validity / production readiness.** A benchmark passing on a fixed
  corpus says nothing about production data. Scope lives in each claim's caveat.
- **That evidence wasn't manipulated before commit.** The gate verifies internal
  consistency and reproducibility, not the honesty of the author who produced the
  artifact.
- **Cryptographic attestation.** Provenance sidecars are recorded metadata, not
  signed DSSE/Sigstore envelopes. Signing is an enterprise-tier roadmap item.
- **Ledger rewrite resistance (Cloudflare integration).** The unkeyed hash chain
  detects *partial* edits; a full rewrite by a D1 writer is not detectable by the
  chain alone — external witnesses and the optional HMAC head raise that bar.
- **Network isolation during reproduction.** The declarative runner isolates
  *outputs* and blocks shell parsing; it does **not** sandbox the filesystem or
  network. `network: disabled` is recorded as *requested*, never *enforced*
  (`network_enforced` is always false). True OS-level sandboxing is deferred.
- **`externally_validated` without an external party.** A project cannot grant
  itself external validation; the top rung stays empty until real external
  evidence exists.

## Trust boundaries (summary)

The **trusted core** is the zero-dependency Python gate. Everything else is an
*input* to be verified, not trusted: the register, artifacts, docs, and code are
repository-controlled inputs; remote bundles and literature are untrusted network
inputs verified after download; the Cloudflare edge and its public endpoints are
a separate optional surface. See
[`../diagrams/trust-boundaries.md`](../diagrams/trust-boundaries.md).

## Reporting

See [`../../SECURITY.md`](../../SECURITY.md) for how to report a vulnerability.
