# SPDX-License-Identifier: Apache-2.0
"""Default-deny tool-call policy for LLM agents — least privilege as code —
reusable, claim-bound.

A pre-verified claimlib code artifact for AI assurance. An agent that can
call tools needs the two oldest rules in computer security applied to every
call (Saltzer & Schroeder 1975: fail-safe defaults, least privilege), the
posture privilege-control frameworks for LLM agents build on (Progent 2025):

    - a call is DENIED unless a rule explicitly allows it (default deny)
    - a rule allows ONE tool with per-argument constraints; an argument the
      rule does not mention is DENIED (unknown-argument fail-closed)

Constraints per argument:
    {"exact": v}           the argument must equal v
    {"enum": [v1, v2]}     the argument must be one of the listed values
    {"prefix": s}          string argument must start with s
    {"max": n}             numeric argument must be <= n (exact Decimal/int)

This is deterministic input-space restriction, not intent understanding: a
policy cannot judge whether an ALLOWED call is wise, and prompt injection
that stays inside the allowed envelope passes. Scope the envelope tightly.
The caveat travels with the claim.

Public API
----------
    Rule(tool, constraints: dict[str, dict])
    Policy(rules: list[Rule])
    Policy.evaluate(tool, args: dict) -> Decision(allowed, reason)

    >>> p = Policy([Rule("read_file", {"path": {"prefix": "docs/"}})])
    >>> p.evaluate("read_file", {"path": "docs/a.md"}).allowed
    True
    >>> p.evaluate("delete_file", {"path": "docs/a.md"}).allowed
    False
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

_CONSTRAINT_KINDS = ("exact", "enum", "prefix", "max")


class PolicyError(ValueError):
    """Malformed rule/policy (fail closed at construction)."""


@dataclass(frozen=True)
class Decision:
    allowed: bool
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
    """Allow one tool, constraining every argument it may receive."""
    tool: str
    constraints: dict

    def __post_init__(self) -> None:
        if not isinstance(self.tool, str) or not self.tool:
            raise PolicyError(f"tool must be a non-empty str, "
                              f"got {self.tool!r}")
        if not isinstance(self.constraints, dict):
            raise PolicyError(f"{self.tool}: constraints must be a dict of "
                              f"arg -> constraint")
        for arg, c in self.constraints.items():
            if not isinstance(arg, str) or not arg:
                raise PolicyError(f"{self.tool}: argument name must be a "
                                  f"non-empty str, got {arg!r}")
            if not isinstance(c, dict) or len(c) != 1:
                raise PolicyError(
                    f"{self.tool}.{arg}: constraint must be a single-key "
                    f"dict, one of {_CONSTRAINT_KINDS}")
            kind, spec = next(iter(c.items()))
            if kind not in _CONSTRAINT_KINDS:
                raise PolicyError(f"{self.tool}.{arg}: unknown constraint "
                                  f"{kind!r} (fail closed, not permissive)")
            if kind == "enum" and (not isinstance(spec, (list, tuple))
                                   or not spec):
                raise PolicyError(f"{self.tool}.{arg}: enum needs a "
                                  f"non-empty list")
            if kind == "prefix" and not isinstance(spec, str):
                raise PolicyError(f"{self.tool}.{arg}: prefix must be a str")
            if kind == "max" and _as_decimal(spec) is None:
                raise PolicyError(f"{self.tool}.{arg}: max must be a number")

    def _check_arg(self, arg: str, value) -> str | None:
        """None = pass; otherwise the denial reason."""
        kind, spec = next(iter(self.constraints[arg].items()))
        if kind == "exact":
            return None if value == spec and type(value) is type(spec) \
                else f"{arg} must equal {spec!r}"
        if kind == "enum":
            return None if any(value == s and type(value) is type(s)
                               for s in spec) \
                else f"{arg} must be one of {list(spec)!r}"
        if kind == "prefix":
            if not isinstance(value, str):
                return f"{arg} must be a string for a prefix constraint"
            return None if value.startswith(spec) \
                else f"{arg} must start with {spec!r}"
        # max
        v = _as_decimal(value)
        if v is None:
            return f"{arg} must be numeric for a max constraint"
        return None if v <= Decimal(str(next(iter(
            self.constraints[arg].values())))) \
            else f"{arg} exceeds the maximum"


class Policy:
    """A default-deny allowlist of Rules (first matching rule decides)."""

    def __init__(self, rules) -> None:
        if not isinstance(rules, (list, tuple)):
            raise PolicyError("rules must be a list of Rule")
        for r in rules:
            if not isinstance(r, Rule):
                raise PolicyError(f"{r!r} is not a Rule")
        self.rules = list(rules)

    def evaluate(self, tool, args) -> Decision:
        """Default deny; a call passes only via an explicit rule whose every
        constraint holds AND which mentions every supplied argument."""
        if not isinstance(tool, str) or not isinstance(args, dict):
            return Decision(False, "malformed call (tool must be str, "
                                   "args a dict)")
        candidates = [r for r in self.rules if r.tool == tool]
        if not candidates:
            return Decision(False, f"no rule allows tool {tool!r} "
                                   f"(default deny)")
        reasons = []
        for rule in candidates:
            unknown = sorted(set(args) - set(rule.constraints))
            if unknown:
                reasons.append(f"argument(s) {unknown} not covered by the "
                               f"rule (unknown-argument fail-closed)")
                continue
            missing = sorted(set(rule.constraints) - set(args))
            if missing:
                reasons.append(f"required argument(s) {missing} missing")
                continue
            denial = None
            for arg in sorted(rule.constraints):
                denial = rule._check_arg(arg, args[arg])
                if denial:
                    break
            if denial is None:
                return Decision(True, f"allowed by rule for {tool!r}")
            reasons.append(denial)
        return Decision(False, "; ".join(reasons))
