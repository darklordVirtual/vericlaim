# greetings — a capability claim

The simplest possible example. The library greets people in several languages;
the claim is a **capability count**, not a benchmark.

- **Code:** `src/greetings.py` — greet in 6 languages.
- **Evidence:** `evidence.py` writes `artifacts/greetings.json` (the languages
  it actually supports).
- **Claim:** `CLAIM-GREET-001` in the [register](../../claims/register.yaml).
- **Doc:** [`docs/results.md`](docs/results.md), bound with a claim anchor.

Try it: add `"it": "Ciao"` to `GREETINGS`, rerun `python examples/greetings/evidence.py`,
and run `vericlaim` — the gate fails until the register and doc say **7**.
