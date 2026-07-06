# SPDX-License-Identifier: Apache-2.0
"""Tenant isolation for a multi-tenant SaaS — the invariant, in-memory.

The knowledge domain is *isolation*: in a shared service that mirrors many
customers' claim registers, tenant A must never read tenant B's rows, and the
per-tenant append-only ledgers must never interleave. This models exactly that
invariant with a row-scoped store and one hash chain per tenant — no network, no
database, so the property battery is fully reproducible.

It is a MODEL of the isolation invariant, not a SaaS: there is no authn, no
transport, no persistence. It proves the scoping/chaining logic is sound; a real
deployment must still enforce the same boundary at the auth and storage layers.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


class CrossTenantError(KeyError):
    """Raised when a read/write names a tenant that does not own the row."""


def _canon(row: dict) -> str:
    return "|".join(f"{k}={row[k]}" for k in sorted(row))


@dataclass
class TenantStore:
    """A key->value store scoped by tenant, plus a per-tenant hash chain.

    Every row is keyed by (tenant_id, key); no API path returns a row for a
    tenant other than the caller's. Each append extends only the caller's chain.
    """
    _rows: dict[tuple[str, str], str] = field(default_factory=dict)
    _heads: dict[str, str] = field(default_factory=dict)  # tenant -> chain head

    def put(self, tenant: str, key: str, value: str) -> str:
        self._rows[(tenant, key)] = value
        prev = self._heads.get(tenant, "genesis")
        # Bind the tenant into the chain entry so two tenants with identical
        # write sequences still get distinct heads — the ledger is per-tenant.
        entry = _canon({"tenant": tenant, "key": key, "value": value, "prev": prev})
        head = hashlib.sha256(entry.encode()).hexdigest()
        self._heads[tenant] = head
        return head

    def get(self, tenant: str, key: str) -> str:
        try:
            return self._rows[(tenant, key)]
        except KeyError:
            raise CrossTenantError(f"tenant {tenant!r} has no row {key!r}") from None

    def head(self, tenant: str) -> str:
        return self._heads.get(tenant, "genesis")

    def can_read(self, tenant: str, key: str) -> bool:
        return (tenant, key) in self._rows


@dataclass
class IsolationReport:
    n_tenants: int
    n_isolation_checks: int
    cross_tenant_leaks: int
    n_chain_forks: int


def run_isolation_battery(n_tenants: int = 5, keys_per_tenant: int = 4) -> IsolationReport:
    """Write distinct rows for each tenant, then assert no tenant can read
    another's rows and each chain reflects only its own writes."""
    store = TenantStore()
    tenants = [f"tenant-{i}" for i in range(n_tenants)]
    keys = [f"k{j}" for j in range(keys_per_tenant)]
    for t in tenants:
        for k in keys:
            store.put(t, k, f"{t}:{k}:secret")

    checks = leaks = forks = 0
    # Cross-tenant reads must all be refused.
    for owner in tenants:
        for other in tenants:
            if other == owner:
                continue
            for k in keys:
                checks += 1
                if store.can_read(other, k) and store.get(other, k).startswith(owner):
                    leaks += 1  # other tenant sees owner's secret — a leak

    # Each tenant's head must depend only on its own writes: re-deriving a
    # tenant's chain in isolation must reproduce its head.
    for t in tenants:
        solo = TenantStore()
        for k in keys:
            solo.put(t, k, f"{t}:{k}:secret")
        checks += 1
        if solo.head(t) != store.head(t):
            forks += 1

    return IsolationReport(len(tenants), checks, leaks, forks)
