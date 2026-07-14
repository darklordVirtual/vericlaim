# Runtime rule enforcement for agent traces (AgentSpec-style)

*Subject area: AI Assurance / Runtime Governance. Language: python. Vendorable bundle `9ad10ae83f55`.*

Runtime governance frameworks for LLM agents — AgentSpec (ICSE 2026) and MI9's continuous conformance over agent-semantic telemetry — converge on declarative rules over the agent's event stream: trigger on an event kind, check predicates over its attributes, enforce one of four actions from full stop to user inspection. This module implements that evaluation core with fail-closed semantics and exact numeric boundaries; the claim proves the grammar matches the published one and the semantics by permutation and mutation, so an agent runtime inherits a checked enforcement kernel.

## Claim

<!-- claim:CLAIM-LIB-RUNTIME-RULES-001 checks_matched -->
The vendored runtime rule engine passes all 22 checks with 0 mismatches: AgentSpec's four enforcement kinds (user_inspection, llm_self_examine, invoke_action, stop) are encoded verbatim and any other — including 'skip', which the paper does not define — is rejected; 12 deterministic-semantics checks hold (first-match-wins verified under rule permutation, Decimal-exact numeric boundaries where 5000 is not > 5000 but "5000.01" is, missing attributes failing predicates closed, malformed events failing closed to stop); the trace evaluator halts exactly at a stop verdict; and every one of 7 single-field mutations of a matching event flips the verdict (mutations_missed = 0). Verified value: <!-- v:CLAIM-LIB-RUNTIME-RULES-001.checks_matched -->**22**
(`checks_matched`), backed by [`modules/runtime_rules/artifacts/runtime_rules.json`](../modules/runtime_rules/artifacts/runtime_rules.json).

## Vendor it

Ships `runtime_rules.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/9ad10ae83f55a0ab7f6fbb056e29643555845549660844e4bc3aa92f1db30753 --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **arXiv:2503.18666** — AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents. [https://arxiv.org/abs/2503.18666](https://arxiv.org/abs/2503.18666)
- **arXiv:2508.03858** — MI9: An Integrated Runtime Governance Framework for Agentic AI. [https://arxiv.org/abs/2508.03858](https://arxiv.org/abs/2508.03858)
