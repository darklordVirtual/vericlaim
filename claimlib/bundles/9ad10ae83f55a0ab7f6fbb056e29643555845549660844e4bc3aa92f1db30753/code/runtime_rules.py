# SPDX-License-Identifier: Apache-2.0
"""Runtime rule enforcement for agent traces (AgentSpec-style) — reusable,
claim-bound.

A pre-verified claimlib code artifact for AI assurance. Runtime governance
frameworks for LLM agents (AgentSpec, ICSE 2026; MI9, 2025) converge on one
mechanism: declarative rules evaluated over the agent's event stream, each

    rule <id>  trigger <event kind>  check <predicates>  enforce <action>

AgentSpec's grammar defines exactly four enforcement kinds —
user_inspection, llm_self_examine, invoke_action, stop — and MI9 frames the
same idea as continuous conformance over agent-semantic telemetry. This
module implements the evaluation core: rules match an event by trigger
kind, their check predicates run over event attributes (missing attribute =
predicate false, fail closed), and the FIRST matching rule in declaration
order decides the enforcement. Events no rule matches PROCEED — rules are
overrides; pair with a default-deny tool policy (see the ``tool_guard``
module) when the baseline itself must be an allowlist.

Deterministic evaluation of declared rules, not intent understanding: a
behaviour no rule anticipates passes through, and enforcement here is a
DECISION — carrying it out (stopping the agent, invoking the user) is the
runtime's job. The caveat travels with the claim.

Public API
----------
    ENFORCEMENTS                        # the four AgentSpec kinds + proceed
    Rule(rule_id, trigger, check: dict, enforce)
    evaluate(rules, event: dict) -> Verdict(rule_id, enforce, reason)
    run_trace(rules, trace: list) -> list[Verdict]

    >>> r = Rule("r1", "tool_call", {"tool": "delete_file"}, "stop")
    >>> evaluate([r], {"kind": "tool_call", "tool": "delete_file"}).enforce
    'stop'
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

# AgentSpec's four enforcement kinds; "proceed" is this module's explicit
# no-rule-matched outcome (never a rule's own enforcement).
ENFORCEMENTS = ("user_inspection", "llm_self_examine", "invoke_action",
                "stop")

_PREDICATE_KINDS = ("eq", "gt", "lt", "contains")


class RuleError(ValueError):
    """Malformed rule (fail closed at construction)."""


@dataclass(frozen=True)
class Verdict:
    rule_id: str | None
    enforce: str          # one of ENFORCEMENTS, or "proceed"
    reason: str


def _as_decimal(value):
    if isinstance(value, bool) or not isinstance(value, (int, float, str,
                                                         Decimal)):
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


@dataclass(frozen=True)
class Rule:
    """trigger: the event kind this rule watches; check: attribute ->
    predicate ({"eq": v} | {"gt": n} | {"lt": n} | {"contains": s});
    enforce: one of the four AgentSpec enforcement kinds."""
    rule_id: str
    trigger: str
    check: dict
    enforce: str

    def __post_init__(self) -> None:
        for name, v in (("rule_id", self.rule_id), ("trigger", self.trigger)):
            if not isinstance(v, str) or not v:
                raise RuleError(f"{name} must be a non-empty str, got {v!r}")
        if self.enforce not in ENFORCEMENTS:
            raise RuleError(
                f"{self.rule_id}: enforce must be one of {ENFORCEMENTS}, "
                f"got {self.enforce!r}")
        if not isinstance(self.check, dict):
            raise RuleError(f"{self.rule_id}: check must be a dict of "
                            f"attribute -> predicate")
        for attr, pred in self.check.items():
            if not isinstance(attr, str) or not attr:
                raise RuleError(f"{self.rule_id}: attribute name must be a "
                                f"non-empty str")
            if not isinstance(pred, dict) or len(pred) != 1:
                raise RuleError(
                    f"{self.rule_id}.{attr}: predicate must be a single-key "
                    f"dict, one of {_PREDICATE_KINDS}")
            kind, spec = next(iter(pred.items()))
            if kind not in _PREDICATE_KINDS:
                raise RuleError(f"{self.rule_id}.{attr}: unknown predicate "
                                f"{kind!r}")
            if kind in ("gt", "lt") and _as_decimal(spec) is None:
                raise RuleError(f"{self.rule_id}.{attr}: {kind} needs a "
                                f"numeric bound")
            if kind == "contains" and not isinstance(spec, str):
                raise RuleError(f"{self.rule_id}.{attr}: contains needs a "
                                f"str")

    def matches(self, event: dict) -> bool:
        """True iff the trigger kind matches and EVERY predicate holds.
        A missing attribute makes its predicate FALSE (fail closed)."""
        if event.get("kind") != self.trigger:
            return False
        for attr, pred in self.check.items():
            if attr not in event:
                return False
            kind, spec = next(iter(pred.items()))
            value = event[attr]
            if kind == "eq":
                if not (value == spec and type(value) is type(spec)):
                    return False
            elif kind in ("gt", "lt"):
                v = _as_decimal(value)
                if v is None:
                    return False
                bound = Decimal(str(spec))
                if kind == "gt" and not v > bound:
                    return False
                if kind == "lt" and not v < bound:
                    return False
            else:  # contains
                if not isinstance(value, str) or spec not in value:
                    return False
        return True


def _check_rules(rules) -> list:
    if not isinstance(rules, (list, tuple)):
        raise RuleError("rules must be a list of Rule")
    seen = set()
    for r in rules:
        if not isinstance(r, Rule):
            raise RuleError(f"{r!r} is not a Rule")
        if r.rule_id in seen:
            raise RuleError(f"duplicate rule_id {r.rule_id!r}")
        seen.add(r.rule_id)
    return list(rules)


def evaluate(rules, event) -> Verdict:
    """The FIRST matching rule (declaration order) decides; no match means
    an explicit 'proceed' verdict."""
    rs = _check_rules(rules)
    if not isinstance(event, dict) or not isinstance(event.get("kind"), str):
        return Verdict(None, "stop",
                       "malformed event (needs a str 'kind') — fail closed")
    for r in rs:
        if r.matches(event):
            return Verdict(r.rule_id, r.enforce,
                           f"rule {r.rule_id!r} matched trigger "
                           f"{r.trigger!r}")
        # continue: first match wins, later rules only see unmatched events
    return Verdict(None, "proceed", "no rule matched")


def run_trace(rules, trace) -> list:
    """Evaluate every event of *trace* in order; a 'stop' verdict halts
    evaluation (the remaining events are never reached, exactly as a
    stopped agent never emits them)."""
    if not isinstance(trace, (list, tuple)):
        raise RuleError("trace must be a list of events")
    _check_rules(rules)   # validate up front — an empty trace must not
    out = []              # let a malformed rule set through unexamined
    for event in trace:
        v = evaluate(rules, event)
        out.append(v)
        if v.enforce == "stop":
            break
    return out
