# SPDX-License-Identifier: Apache-2.0
"""GSN assurance-case structure validation (Goal Structuring Notation) —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. Safety and assurance
cases for AI systems are increasingly written in GSN (GSN Community Standard
v3, SCSC; applied to frontier AI by Clymer et al. 2024): a graph of

    goal          a claim to be supported
    strategy      how a goal is decomposed into sub-goals
    solution      the evidence terminating a branch
    context / assumption / justification   contextual elements

connected by two relations with STRICT type rules:

    supported_by:   goal -> goal | strategy | solution;  strategy -> goal
    in_context_of:  goal | strategy -> context | assumption | justification

This module validates an assurance case's STRUCTURE fail-closed: every edge
type-checked, the supported_by graph acyclic (a circular argument is not an
argument), every goal either supported or explicitly marked undeveloped,
solutions and contextual elements terminal, exactly ONE root goal (a GSN
module argues one top-level claim) with everything reachable from it.
Structural validity is machine-checkable; the STRENGTH of an argument
is not — a well-formed case can still argue from weak evidence. The caveat
travels with the claim.

Public API
----------
    Case(elements: dict[str, str], supported_by, in_context_of,
         undeveloped: set)
    validate(case) -> list[str]          # [] = structurally valid
    is_valid(case) -> bool

    >>> tiny = Case({"G1": "goal", "S1": "solution"},
    ...             [("G1", "S1")], [], set())
    >>> is_valid(tiny)
    True
"""
from __future__ import annotations

from dataclasses import dataclass, field

ELEMENT_KINDS = ("goal", "strategy", "solution", "context", "assumption",
                 "justification")

_SUPPORTED_BY = {
    "goal": {"goal", "strategy", "solution"},
    "strategy": {"goal"},
}
_IN_CONTEXT_OF = {
    "goal": {"context", "assumption", "justification"},
    "strategy": {"context", "assumption", "justification"},
}


class GSNError(ValueError):
    """Malformed case object (fail closed before validation even starts)."""


@dataclass(frozen=True)
class Case:
    """An assurance case: elements by id, typed edges, undeveloped marks."""
    elements: dict
    supported_by: list = field(default_factory=list)
    in_context_of: list = field(default_factory=list)
    undeveloped: frozenset = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.elements, dict) or not self.elements:
            raise GSNError("elements must be a non-empty dict of id -> kind")
        for eid, kind in self.elements.items():
            if not isinstance(eid, str) or not eid:
                raise GSNError(f"element id must be a non-empty str, "
                               f"got {eid!r}")
            if kind not in ELEMENT_KINDS:
                raise GSNError(f"{eid}: unknown element kind {kind!r} "
                               f"(expected one of {ELEMENT_KINDS})")
        for name, edges in (("supported_by", self.supported_by),
                            ("in_context_of", self.in_context_of)):
            if not isinstance(edges, (list, tuple)):
                raise GSNError(f"{name} must be a list of (from, to) pairs")
            for e in edges:
                if not isinstance(e, tuple) or len(e) != 2:
                    raise GSNError(f"{name} edge {e!r} must be a "
                                   f"(from, to) tuple")
        object.__setattr__(self, "undeveloped", frozenset(self.undeveloped))


def validate(case: Case) -> list:
    """Every structural violation in *case* (empty list = valid).

    Checks: edge endpoints exist; edge types legal per the GSN relation
    rules; the supported_by graph is acyclic; every goal is supported or
    marked undeveloped (never both); only goals may be undeveloped;
    solutions and contextual elements have no outgoing edges; every element
    is reachable from the root goal.
    """
    problems: list = []
    kinds = case.elements

    def kind_of(eid) -> str | None:
        return kinds.get(eid)

    for src, dst in case.supported_by:
        ks, kd = kind_of(src), kind_of(dst)
        if ks is None or kd is None:
            problems.append(f"supported_by edge {src}->{dst}: unknown "
                            f"element id")
            continue
        if ks not in _SUPPORTED_BY or kd not in _SUPPORTED_BY[ks]:
            problems.append(f"supported_by {src}->{dst}: {ks} may not be "
                            f"supported by {kd}")
    for src, dst in case.in_context_of:
        ks, kd = kind_of(src), kind_of(dst)
        if ks is None or kd is None:
            problems.append(f"in_context_of edge {src}->{dst}: unknown "
                            f"element id")
            continue
        if ks not in _IN_CONTEXT_OF or kd not in _IN_CONTEXT_OF[ks]:
            problems.append(f"in_context_of {src}->{dst}: {ks} may not take "
                            f"{kd} as context")

    # Acyclicity of supported_by (a circular argument supports nothing).
    adj: dict = {}
    for src, dst in case.supported_by:
        adj.setdefault(src, []).append(dst)
    state: dict = {}

    def dfs(node, stack) -> None:
        state[node] = 1
        for nxt in adj.get(node, []):
            if state.get(nxt) == 1:
                cyc = stack[stack.index(nxt):] if nxt in stack else [nxt]
                problems.append("circular argument: " +
                                " -> ".join(cyc + [nxt]))
            elif state.get(nxt) is None:
                dfs(nxt, stack + [nxt])
        state[node] = 2

    for eid in sorted(kinds):
        if state.get(eid) is None:
            dfs(eid, [eid])

    supported = {src for src, _ in case.supported_by}
    for eid in sorted(kinds):
        if kinds[eid] != "goal":
            if eid in case.undeveloped:
                problems.append(f"{eid}: only goals may be marked "
                                f"undeveloped ({kinds[eid]})")
            continue
        has_support = eid in supported
        if has_support and eid in case.undeveloped:
            problems.append(f"{eid}: marked undeveloped but has support — "
                            f"pick one")
        if not has_support and eid not in case.undeveloped:
            problems.append(f"{eid}: goal is neither supported nor marked "
                            f"undeveloped")

    for src, _ in list(case.supported_by) + list(case.in_context_of):
        if kind_of(src) in ("solution", "context", "assumption",
                            "justification"):
            problems.append(f"{src}: {kind_of(src)} must be terminal "
                            f"(no outgoing edges)")

    # Reachability from THE root: a GSN module argues one top-level claim,
    # so exactly one goal may lack incoming supported_by edges. Zero roots
    # is a circular case; two or more means a disconnected argument island.
    targets = {dst for _, dst in case.supported_by}
    roots = [eid for eid in sorted(kinds)
             if kinds[eid] == "goal" and eid not in targets]
    if not roots:
        problems.append("no root goal (every goal is a support target)")
    elif len(roots) > 1:
        problems.append(f"multiple root goals {roots} — a GSN module argues "
                        f"exactly one top-level claim")
    else:
        seen: set = set()
        frontier = list(roots)
        ctx_adj: dict = {}
        for src, dst in case.in_context_of:
            ctx_adj.setdefault(src, []).append(dst)
        while frontier:
            node = frontier.pop()
            if node in seen:
                continue
            seen.add(node)
            frontier.extend(adj.get(node, []))
            frontier.extend(ctx_adj.get(node, []))
        for eid in sorted(kinds):
            if eid not in seen:
                problems.append(f"{eid}: unreachable from any root goal")

    return problems


def is_valid(case: Case) -> bool:
    """True iff validate() finds nothing."""
    return not validate(case)
