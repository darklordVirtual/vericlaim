# Multi-tenant Isolation — Results

A **property claim**: in a shared service mirroring many tenants' registers, no
tenant may read another's rows and no two per-tenant ledgers may interleave. The
battery writes distinct secrets for every tenant, then attempts every
cross-tenant read and re-derives every chain in isolation.

<!-- claim:CLAIM-TENANT-001 n_tenants -->
Across **5** tenants,

<!-- claim:CLAIM-TENANT-001 n_isolation_checks -->
the battery runs **85** isolation checks (every cross-tenant read plus a
per-tenant chain re-derivation).

<!-- claim:CLAIM-TENANT-001 cross_tenant_leaks -->
Result: **0** cross-tenant leaks (and 0 chain forks) — no tenant observed
another tenant's secret, and each chain head depends only on its own writes.

Artifact: [`../artifacts/isolation_report.json`](../artifacts/isolation_report.json) ·
Reproduce: `python3 domains/multitenant/evidence.py`

> Scope: models the isolation invariant in memory. A real SaaS must still
> enforce the same boundary at the auth and storage layers — this proves the
> scoping/chaining logic, not a deployment.
