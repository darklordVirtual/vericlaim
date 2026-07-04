# Sources for CLAIM-002 — AgentHarm external benchmark

Curated literature extract for the library bundle of REMORA-research
CLAIM-002. Hash-locked at harvest; this note is our own summary of the cited
public sources, not a copy of them.

- **AgentHarm**: Andriushchenko, M., et al. (2024). *AgentHarm: A Benchmark
  for Measuring Harmfulness of LLM Agents.* arXiv:2410.09024. The dataset is a
  red-teaming evaluation suite developed by the UK AI Safety Institute and
  Gray Swan AI; REMORA evaluates 44 harmful + 44 harmless agent tasks (and a
  208-scenario harmful superset for the blocking claim).

## Scope note carried from the source

REMORA's AgentHarm result is an **intent-gating** result: the system routes
the agent's proposed action string (VERIFY/ESCALATE); it does not intercept
AgentHarm's internal tool dispatch. Routing accuracy, not verified tool
interception (source: REMORA paper §10.7 scope caveat).
