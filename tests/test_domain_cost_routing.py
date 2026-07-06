# SPDX-License-Identifier: Apache-2.0
"""Cost-aware routing: cheapest-that-clears-floor, sound, and cheaper."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "domains" / "cost_routing" / "src"))
from cost_routing import MODELS, WORKLOAD, cheapest_meeting, route  # noqa: E402


def test_route_matches_artifact():
    art = json.loads(
        (ROOT / "domains/cost_routing/artifacts/routing_report.json").read_text())
    result = route(MODELS, WORKLOAD)
    for k in ("n_requests", "savings_ratio", "quality_violations",
              "routed_cost", "baseline_cost"):
        assert art[k] == result[k]


def test_no_quality_violations_and_positive_saving():
    r = route(MODELS, WORKLOAD)
    assert r["quality_violations"] == 0
    assert 0 < r["savings_ratio"] < 1
    assert r["routed_cost"] < r["baseline_cost"]


def test_cheapest_meeting_picks_cheapest_eligible():
    m = cheapest_meeting(MODELS, 0.70)     # small(.72) and up qualify
    assert m.name == "small"
    assert cheapest_meeting(MODELS, 0.99) is None   # nothing clears 0.99
