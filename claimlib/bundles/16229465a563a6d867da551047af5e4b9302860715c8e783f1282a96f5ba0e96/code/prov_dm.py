# SPDX-License-Identifier: Apache-2.0
"""PROV-DM core provenance-graph validation (W3C PROV Data Model) —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. W3C PROV-DM (2013)
is the standard model for provenance — who made what, from what, how. Its
CORE comprises three types and exactly seven relations with strict
endpoint typing:

    entity    a thing (a model file, a dataset, a report)
    activity  something that happens (a training run, an evaluation)
    agent     something responsible (a person, a service, an agent)

    used(activity -> entity)               Usage
    wasGeneratedBy(entity -> activity)     Generation
    wasInformedBy(activity -> activity)    Communication
    wasDerivedFrom(entity -> entity)       Derivation
    wasAttributedTo(entity -> agent)       Attribution
    wasAssociatedWith(activity -> agent)   Association
    actedOnBehalfOf(agent -> agent)        Delegation

(Start/End belong to PROV-DM's EXPANDED structures, not the core — this
module implements the core.) The validator type-checks every edge
fail-closed and rejects cyclic derivation and delegation chains (an entity
cannot be its own ancestor). Structural validity never proves the recorded
provenance is TRUE — signing/attestation is a separate layer. The caveat
travels with the claim.

Public API
----------
    TYPES, RELATIONS                       # the core taxonomy
    ProvDocument(elements: dict[str, str],
                 relations: list[tuple[str, str, str]])  # (rel, from, to)
    validate(doc) -> list[str]             # [] = structurally valid
    is_valid(doc) -> bool

    >>> doc = ProvDocument({"m": "entity", "t": "activity"},
    ...                    [("wasGeneratedBy", "m", "t")])
    >>> is_valid(doc)
    True
"""
from __future__ import annotations

from dataclasses import dataclass, field

TYPES = ("entity", "activity", "agent")

# relation -> (subject type, object type); W3C PROV-DM core structures.
RELATIONS = {
    "used": ("activity", "entity"),
    "wasGeneratedBy": ("entity", "activity"),
    "wasInformedBy": ("activity", "activity"),
    "wasDerivedFrom": ("entity", "entity"),
    "wasAttributedTo": ("entity", "agent"),
    "wasAssociatedWith": ("activity", "agent"),
    "actedOnBehalfOf": ("agent", "agent"),
}

# Relations whose transitive closure must be acyclic: a derivation or
# delegation loop asserts something is its own ancestor.
_ACYCLIC = ("wasDerivedFrom", "actedOnBehalfOf")


class ProvError(ValueError):
    """Malformed document object (fail closed before validation starts)."""


@dataclass(frozen=True)
class ProvDocument:
    """A PROV core document: typed elements and typed relation triples."""
    elements: dict
    relations: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.elements, dict) or not self.elements:
            raise ProvError("elements must be a non-empty dict of id -> type")
        for eid, kind in self.elements.items():
            if not isinstance(eid, str) or not eid:
                raise ProvError(f"element id must be a non-empty str, "
                                f"got {eid!r}")
            if kind not in TYPES:
                raise ProvError(f"{eid}: unknown PROV type {kind!r} "
                                f"(expected one of {TYPES})")
        if not isinstance(self.relations, (list, tuple)):
            raise ProvError("relations must be a list of "
                            "(relation, from, to) triples")
        for r in self.relations:
            if not isinstance(r, tuple) or len(r) != 3:
                raise ProvError(f"relation {r!r} must be a "
                                f"(relation, from, to) triple")


def validate(doc: ProvDocument) -> list:
    """Every structural violation in *doc* (empty list = valid).

    Checks: relation names are core PROV-DM relations; both endpoints
    exist; endpoint types match the relation's signature; derivation and
    delegation are acyclic.
    """
    problems: list = []
    kinds = doc.elements

    for rel, src, dst in doc.relations:
        if rel not in RELATIONS:
            problems.append(f"{rel}({src}, {dst}): not a PROV-DM core "
                            f"relation")
            continue
        want_s, want_o = RELATIONS[rel]
        ks, kd = kinds.get(src), kinds.get(dst)
        if ks is None or kd is None:
            problems.append(f"{rel}({src}, {dst}): unknown element id")
            continue
        if ks != want_s or kd != want_o:
            problems.append(
                f"{rel}({src}, {dst}): signature is "
                f"{rel}({want_s} -> {want_o}), got ({ks} -> {kd})")

    for rel_name in _ACYCLIC:
        adj: dict = {}
        for rel, src, dst in doc.relations:
            if rel == rel_name and src in kinds and dst in kinds:
                adj.setdefault(src, []).append(dst)
        state: dict = {}

        def dfs(node, stack, adj=adj, state=state, rel_name=rel_name):
            state[node] = 1
            for nxt in adj.get(node, []):
                if state.get(nxt) == 1:
                    cyc = stack[stack.index(nxt):] if nxt in stack else [nxt]
                    problems.append(f"{rel_name} cycle: "
                                    + " -> ".join(cyc + [nxt]))
                elif state.get(nxt) is None:
                    dfs(nxt, stack + [nxt])
            state[node] = 2

        for eid in sorted(adj):
            if state.get(eid) is None:
                dfs(eid, [eid])

    return problems


def is_valid(doc: ProvDocument) -> bool:
    """True iff validate() finds nothing."""
    return not validate(doc)
