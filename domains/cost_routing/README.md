# Domain: Cost-aware Routing

Route each request to the cheapest model that clears its quality floor; measure
the saving against an always-premium baseline while proving no request is served
below its floor. Directly models the fix for the audit's unbounded-AI-cost
finding on the Cloudflare worker.

- `src/cost_routing.py` — model catalogue, workload, and router.
- `evidence.py` — writes `artifacts/routing_report.json`. `docs/results.md` — gate-bound.

Reproduce: `python3 domains/cost_routing/evidence.py` ·
Claim: `CLAIM-ROUTE-001` · Evidence level: `benchmarked`.

Price table, quality scores and workload are synthetic and fixed.
