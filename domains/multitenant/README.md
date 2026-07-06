# Domain: Multi-tenant SaaS (isolation)

Model the isolation invariant of a shared, multi-tenant claim service: a
row-scoped store plus one append-only hash chain per tenant. A property battery
proves no tenant can read another's rows and no two chains interleave.

- `src/multitenant.py` — the tenant store, per-tenant chain, and battery.
- `evidence.py` — writes `artifacts/isolation_report.json`. `docs/results.md` — gate-bound.

Reproduce: `python3 domains/multitenant/evidence.py` ·
Claim: `CLAIM-TENANT-001` · Evidence level: `benchmarked`.

Models the invariant only — a real deployment must enforce the same boundary at
the auth and storage layers.
