# SPDX-License-Identifier: Apache-2.0
"""Topological sort with cycle detection (Kahn's algorithm).

A pre-verified claimlib code artifact: a reusable, stdlib-only building block that
orders a directed acyclic graph so every dependency comes before what depends on
it -- the primitive behind build systems, task schedulers, migration ordering,
and package resolution. Ties are broken deterministically (smallest node first),
and a cyclic graph fails closed. That every output respects all edges and that
cycles are always detected is registered as a claim and proven by a committed
evidence artifact.

Edges are ``(u, v)`` pairs meaning "u must come before v".

Public API
----------
    topo_sort(nodes, edges) -> list   # deterministic order; raises on a cycle
    has_cycle(nodes, edges) -> bool

    >>> topo_sort(["shirt", "tie", "jacket"], [("shirt", "tie"), ("tie", "jacket")])
    ['shirt', 'tie', 'jacket']
"""
from __future__ import annotations

import heapq
from collections.abc import Iterable


class TopoSortError(ValueError):
    """An edge references an unknown node."""


class CycleError(TopoSortError):
    """The graph contains a cycle, so no topological order exists."""


def _build(nodes, edges):
    node_list = list(nodes)
    node_set = set(node_list)
    indegree = {n: 0 for n in node_list}
    adjacency: dict = {n: [] for n in node_list}
    for edge in edges:
        u, v = edge
        if u not in node_set or v not in node_set:
            raise TopoSortError(f"edge {edge!r} references an unknown node")
        adjacency[u].append(v)
        indegree[v] += 1
    return node_list, indegree, adjacency


def topo_sort(nodes: Iterable, edges: Iterable) -> list:
    """Return a topological ordering of *nodes* honoring *edges*.

    Ready nodes are emitted smallest-first (a min-heap) so the order is
    deterministic. Raises :class:`CycleError` if the graph is cyclic.
    """
    node_list, indegree, adjacency = _build(nodes, edges)
    ready = [n for n in node_list if indegree[n] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        n = heapq.heappop(ready)
        order.append(n)
        for m in adjacency[n]:
            indegree[m] -= 1
            if indegree[m] == 0:
                heapq.heappush(ready, m)
    if len(order) != len(node_list):
        raise CycleError("graph contains a cycle")
    return order


def has_cycle(nodes: Iterable, edges: Iterable) -> bool:
    """Return True iff the directed graph contains a cycle."""
    try:
        topo_sort(nodes, edges)
        return False
    except CycleError:
        return True
