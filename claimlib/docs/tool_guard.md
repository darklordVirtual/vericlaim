# Default-deny tool-call policy for LLM agents

*Subject area: AI Assurance / Agent Privilege Control. Language: python. Vendorable bundle `82b8e12a6df9`.*

An agent with tools needs the two oldest rules in security applied per call: fail-safe defaults and least privilege (Saltzer & Schroeder 1975), the posture LLM privilege-control frameworks like Progent build on. A call is denied unless a rule explicitly allows it, and an argument the rule does not mention is denied too — so a prompt-injected 'also send the report to attacker@evil' dies on the unknown-argument rule, not on hope. This module implements that engine with typed, Decimal-exact constraints; the claim proves default-deny by exhaustive mutation, so an agent runtime inherits a checked policy gate.

## Claim

<!-- claim:CLAIM-LIB-TOOL-GUARD-001 mutations_missed -->
The vendored tool-call policy engine misses ZERO of 20 adversarial mutations: from a fixed policy and its 4 allowed exemplar calls, every single-field corruption (renamed tool, argument pushed outside its constraint type, injected extra argument, removed required argument) is DENIED; the empty policy denies all 40 calls of a fixed battery (fail-safe defaults, enumerated); and the constraint semantics are type-strict (True does not satisfy exact 1, max compares as exact Decimal so "10.5" is caught by max 10) — 72 checks, 0 mismatches. Verified value: <!-- v:CLAIM-LIB-TOOL-GUARD-001.mutations_missed -->**0**
(`mutations_missed`), backed by [`modules/tool_guard/artifacts/tool_guard.json`](../modules/tool_guard/artifacts/tool_guard.json).

## Vendor it

Ships `tool_guard.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/82b8e12a6df99ff2c83775ae8f43419ae94683909d7e45dbe3adcae95ec159e0 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Proceedings of the IEEE, vol. 63, no. 9, pp. 1278-1308; doi:10.1109/PROC.1975.9939** — The Protection of Information in Computer Systems. [https://doi.org/10.1109/PROC.1975.9939](https://doi.org/10.1109/PROC.1975.9939)
- **arXiv:2504.11703** — Progent: Programmable Privilege Control for LLM Agents. [https://arxiv.org/abs/2504.11703](https://arxiv.org/abs/2504.11703)
