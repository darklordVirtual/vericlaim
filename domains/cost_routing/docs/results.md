# Cost-aware Routing — Results

A **benchmark claim**: route each request to the cheapest model that still
clears its quality floor, and measure the saving against an always-premium
baseline — while proving no request is served below its floor. (This is the
policy the audit recommends for the worker's unbounded AI endpoints.)

<!-- claim:CLAIM-ROUTE-001 n_requests -->
Over **8** requests against a 4-model catalogue,

<!-- claim:CLAIM-ROUTE-001 savings_ratio -->
cost-aware routing costs **0.8059** less than always-premium — a ~81% saving
(routed 5.94 vs baseline 30.6, synthetic units).

<!-- claim:CLAIM-ROUTE-001 quality_violations -->
Soundness: **0** quality violations — every request was served by a model at or
above its quality floor.

Artifact: [`../artifacts/routing_report.json`](../artifacts/routing_report.json) ·
Reproduce: `python3 domains/cost_routing/evidence.py`

> Scope: the price table, quality scores and workload are synthetic and fixed.
> This demonstrates the routing policy and its saving/soundness guarantees, not
> real model prices or real model quality.
