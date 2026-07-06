# Security policy

## Reporting a vulnerability

Please report security issues **privately**, not in public issues.

- Use GitHub's **private vulnerability reporting** on this repository
  (Security → Report a vulnerability), or
- open a minimal private channel with the maintainer referenced in
  [`CITATION.cff`](CITATION.cff).

Include: affected file(s) and version/commit, a concrete reproduction, the
impact, and any suggested fix. Please allow a reasonable window for a fix before
public disclosure.

## Scope

The **trusted core** is the zero-dependency Python gate (`vericlaim/`). Its
security posture is defined in
[`docs/security/security-model.md`](docs/security/security-model.md) and the
threat model in [`docs/security/threat-model.md`](docs/security/threat-model.md).

Integrations (`integrations/cloudflare-ai/`, `integrations/library/`) are
**optional** product surfaces with their own threat models. A weakness in an
integration does not affect the trusted core, but is still in scope for reports.

## What we treat as a security bug

- Path traversal, symlink escape, or unsafe archive/bundle extraction.
- A way to make the gate **pass** while a specified integrity property is
  violated (drift-past-the-gate).
- Arbitrary command/code execution reachable from untrusted input in the core.
- SSRF or remote-write-before-verify in fetch/download paths.
- Authorization bypass, injection, or secret exposure in the Cloudflare edge.

## What is NOT a vulnerability

- The core does not prove semantic truth, external validation, or cryptographic
  attestation unless explicitly present — see the security model. "The tool did
  not catch a false-but-consistent claim" is a documented boundary, not a bug.
- Reproduction is not a syscall sandbox (`network_enforced` is always false).

## Every security fix ships with a regression test

Fixes land with an adversarial test that fails before and passes after — see
`tests/test_pathsafe.py`, `tests/test_repro.py`, and `tests/test_credibility_fixes.py`.
