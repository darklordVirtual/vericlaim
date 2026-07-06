# SPDX-License-Identifier: Apache-2.0
"""Build an evidence graph from a claim register and check its integrity.

The knowledge domain is *evidence as a graph*: claims, the artifacts that back
them, the literature they cite, and the docs that bind them are nodes; "binds",
"backed_by" and "cites" are edges. Once the evidence is a graph you can ask
structural questions a flat register cannot answer — is any claim an orphan
(bound in a doc but backed by no artifact)? what is the deepest evidence chain?

Operates on a committed fixture (`data/sample_claims.json`) so the artifact is
byte-stable regardless of the surrounding repo; the same builder runs on a real
register exported to the same shape.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Graph:
    nodes: set[tuple[str, str]] = field(default_factory=set)   # (kind, id)
    edges: set[tuple[tuple, str, tuple]] = field(default_factory=set)  # (src, rel, dst)

    def add_node(self, kind: str, ident: str) -> tuple[str, str]:
        node = (kind, ident)
        self.nodes.add(node)
        return node

    def add_edge(self, src: tuple, rel: str, dst: tuple) -> None:
        self.edges.add((src, rel, dst))


def build_graph(claims: list[dict]) -> Graph:
    """Nodes: claim / artifact / literature / doc. Edges: doc-binds->claim,
    claim-backed_by->artifact, claim-cites->literature."""
    g = Graph()
    for c in claims:
        claim = g.add_node("claim", c["id"])
        for art in c.get("artifacts", []):
            g.add_edge(claim, "backed_by", g.add_node("artifact", art))
        for lit in c.get("literature", []):
            g.add_edge(claim, "cites", g.add_node("literature", lit))
        for doc in c.get("docs", []):
            g.add_edge(g.add_node("doc", doc), "binds", claim)
    return g


def orphan_claims(g: Graph) -> list[str]:
    """Claim ids with no outgoing 'backed_by' edge — a claim with no artifact."""
    backed = {src[1] for src, rel, _ in g.edges if rel == "backed_by"}
    return sorted(ident for kind, ident in g.nodes
                  if kind == "claim" and ident not in backed)


def max_evidence_depth(g: Graph) -> int:
    """Longest simple path length (in edges) — the deepest doc->claim->artifact
    chain. The graph is a shallow DAG, so a plain DFS over successors suffices."""
    succ: dict[tuple, list[tuple]] = {}
    for src, _rel, dst in g.edges:
        succ.setdefault(src, []).append(dst)

    def depth(node: tuple, seen: frozenset) -> int:
        if node in seen:
            return 0
        best = 0
        for nxt in succ.get(node, ()):
            best = max(best, 1 + depth(nxt, seen | {node}))
        return best

    return max((depth(n, frozenset()) for n in g.nodes), default=0)


def metrics(g: Graph) -> dict[str, int]:
    return {
        "n_nodes": len(g.nodes),
        "n_edges": len(g.edges),
        "n_claims": sum(1 for k, _ in g.nodes if k == "claim"),
        "orphan_claims": len(orphan_claims(g)),
        "max_evidence_depth": max_evidence_depth(g),
    }
