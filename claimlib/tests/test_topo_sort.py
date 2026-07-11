# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the reusable ``topo_sort`` library (Kahn's algorithm)."""
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "modules" / "topo_sort"))

from topo_sort import topo_sort, has_cycle, CycleError, TopoSortError  # noqa: E402


def _respects_edges(nodes, edges, order):
    assert sorted(order) == sorted(nodes)
    pos = {n: i for i, n in enumerate(order)}
    return all(pos[u] < pos[v] for u, v in edges)


def test_chain_and_diamond():
    assert topo_sort(["a", "b", "c"], [("a", "b"), ("b", "c")]) == ["a", "b", "c"]
    edges = [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]
    assert _respects_edges(["a", "b", "c", "d"], edges, topo_sort(["a", "b", "c", "d"], edges))


def test_deterministic_tie_break():
    # No edges -> smallest-first order.
    assert topo_sort(["c", "a", "b"], []) == ["a", "b", "c"]


def test_cycle_detection():
    assert has_cycle(["a", "b"], [("a", "b"), ("b", "a")]) is True
    assert has_cycle(["a"], [("a", "a")]) is True
    assert has_cycle(["a", "b", "c"], [("a", "b"), ("b", "c")]) is False
    with pytest.raises(CycleError):
        topo_sort(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])


def test_unknown_node_edge_rejected():
    with pytest.raises(TopoSortError):
        topo_sort(["a", "b"], [("a", "z")])
