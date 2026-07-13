# Support

**Purpose.** Where to get help, and what to expect. This is a research-grade
open-source project, not a supported commercial product.

## Getting help

1. **Read the docs first** — start at the [documentation index](docs/README.md)
   and the [configuration reference](docs/reference/configuration.md).
2. **Adopting vericlaim?** See
   [`docs/getting-started.md`](docs/getting-started.md)
   and run `vericlaim init` then `vericlaim --profile adopt`.
3. **Found a bug or have a question?** Open a GitHub issue with: your OS, Python
   version, `vericlaim` commit, the exact command, and the full output.
4. **Security issue?** Do **not** open a public issue — see
   [`SECURITY.md`](SECURITY.md).

## What is supported

- The zero-dependency core gate (`vericlaim/`) on Python 3.11+.
- The documented profiles, config, and CLI.

## What is best-effort / experimental

- The Cloudflare and library integrations are optional surfaces; see their
  READMEs and `ROADMAP.md`. They may change or require redeployment.

## Response expectations

Best-effort, no SLA. Well-scoped issues with a reproduction are handled first.
