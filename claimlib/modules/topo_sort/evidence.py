# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-TOPOSORT-001 -- every ordering respects all edges and
every cyclic graph is detected.

The correctness property is self-verifying and needs no external oracle: for a
DAG, a valid topological order must contain each node exactly once AND place the
tail of every edge before its head. Over a fixed battery of DAGs the evidence
checks exactly that. Over a fixed battery of cyclic graphs it checks that
``has_cycle`` is True and ``topo_sort`` raises. Deterministic.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))              # the module under test (topo_sort.py)
sys.path.insert(0, str(HERE.parents[1]))   # claimlib/ for _util

from topo_sort import topo_sort, has_cycle, CycleError  # noqa: E402
from _util import emit  # noqa: E402

# (nodes, edges) directed acyclic graphs.
DAGS = [
    (["a", "b", "c"], [("a", "b"), ("b", "c")]),                     # chain
    (["a", "b", "c", "d"], [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")]),  # diamond
    (["x"], []),                                                     # single node
    (["p", "q", "r"], []),                                           # no edges
    (["1", "2", "3", "4", "5"],
     [("1", "2"), ("1", "3"), ("3", "4"), ("2", "4"), ("4", "5")]),  # build graph
    (["compile", "link", "test", "package"],
     [("compile", "link"), ("link", "test"), ("test", "package")]),
]

# (nodes, edges) graphs that DO contain a cycle.
CYCLIC = [
    (["a", "b"], [("a", "b"), ("b", "a")]),          # 2-cycle
    (["a"], [("a", "a")]),                            # self-loop
    (["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")]),  # 3-cycle
    (["a", "b", "c", "d"], [("a", "b"), ("b", "c"), ("c", "b"), ("c", "d")]),
]


def _valid_order(nodes, edges, order) -> bool:
    if sorted(order) != sorted(nodes):
        return False                       # every node exactly once
    position = {n: i for i, n in enumerate(order)}
    return all(position[u] < position[v] for u, v in edges)


def run() -> dict:
    valid_orderings = 0
    for nodes, edges in DAGS:
        order = topo_sort(nodes, edges)
        valid_orderings += int(_valid_order(nodes, edges, order))

    cycles_detected = 0
    raised = 0
    for nodes, edges in CYCLIC:
        if has_cycle(nodes, edges):
            cycles_detected += 1
        try:
            topo_sort(nodes, edges)
        except CycleError:
            raised += 1

    return {
        "schema": "claimlib_topo_sort_v1",
        "module": "topo_sort",
        "n_dags": len(DAGS),
        "valid_orderings": valid_orderings,
        "invalid_orderings": len(DAGS) - valid_orderings,
        "n_cyclic": len(CYCLIC),
        "cycles_detected": cycles_detected,
        "cycles_raised": raised,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "topo_sort.json", obj,
         script="python3 claimlib/modules/topo_sort/evidence.py")
    # claim:CLAIM-LIB-TOPOSORT-001 valid_orderings
    # Every DAG produces an edge-respecting order, so valid_orderings = 6 and
    # invalid_orderings = 0 (n_dags = 6); all cyclic graphs are detected.
    print(f"topo_sort: {obj['valid_orderings']}/{obj['n_dags']} valid orderings, "
          f"{obj['cycles_detected']}/{obj['n_cyclic']} cycles detected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
