# SPDX-License-Identifier: Apache-2.0
"""Multi-tenant isolation: no cross-tenant reads, no chain interleave."""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domains" / "multitenant" / "src"))
from multitenant import CrossTenantError, TenantStore, run_isolation_battery  # noqa: E402


def test_battery_matches_artifact():
    art = json.loads(
        (ROOT / "domains/multitenant/artifacts/isolation_report.json").read_text())
    for k, v in asdict(run_isolation_battery()).items():
        assert art[k] == v


def test_cross_tenant_read_is_refused():
    s = TenantStore()
    s.put("a", "k", "a-secret")
    assert s.get("a", "k") == "a-secret"
    with pytest.raises(CrossTenantError):
        s.get("b", "k")            # tenant b never wrote k


def test_chains_do_not_interleave():
    s = TenantStore()
    ha1 = s.put("a", "k", "v")
    s.put("b", "k", "v")           # b's write must not change a's head
    ha2 = s.put("a", "k2", "v")
    assert s.head("a") == ha2 and ha2 != ha1
    assert s.head("b") != s.head("a")
