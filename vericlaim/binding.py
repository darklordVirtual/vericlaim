# SPDX-License-Identifier: Apache-2.0
"""Schema v2 metric bindings — explicit, typed, Decimal-safe.

The v1 metric check matches a register value against ANY identically-named
key in the artifact's JSON tree — good enough to catch typos, but an
identically-named key elsewhere can satisfy it. A **metric binding** removes
that ambiguity: it names the artifact, the exact location (RFC 6901 JSON
Pointer), the expected JSON type, and the comparator:

    metric_bindings:
      - metric: overall_ratio          # required: the metrics key it binds
        pointer: /overall_ratio        # required: RFC 6901 location
        artifact: results/bench.json   # optional when the claim cites
                                       #   exactly one .json artifact
        type: number                   # optional: number|integer|string|boolean
        unit: ratio                    # optional: recorded documentation
        comparator: exact              # exact (default) | minimum | maximum
                                       #   | bounded (needs tolerance)
        value: "8.0584"                # optional: defaults to metrics[metric];
                                       #   a string parses exactly as Decimal
        tolerance: "0.0001"            # bounded only: absolute tolerance

    Comparator semantics (artifact_value ⋄ register_value):
      exact    artifact == register
      minimum  artifact >= register   (the register states a floor)
      maximum  artifact <= register   (the register states a ceiling)
      bounded  |artifact - register| <= tolerance

Numeric comparison is exact decimal arithmetic: the artifact JSON is parsed
with ``parse_float=Decimal`` and the register value via ``Decimal(str(v))``,
so 8.0584 compares as the literal 8.0584 — no float representation drift.
A bound metric is EXEMPT from the v1 any-depth key scan (the binding is
strictly stronger); everything about a binding fails closed: an unresolvable
pointer, a wrong type, a missing tolerance, an ambiguous artifact — findings,
never skips. The list-of-flat-maps YAML shape parses identically under the
bundled zero-dependency parser and PyYAML (same contract as ``literature:``).
"""
from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .config import Config

Finding = tuple[str, str]

COMPARATORS = ("exact", "minimum", "maximum", "bounded")
TYPES = ("number", "integer", "string", "boolean")


class PointerError(ValueError):
    """The JSON Pointer does not resolve in the document."""


def resolve_pointer(doc: object, pointer: str) -> object:
    """Resolve an RFC 6901 JSON Pointer in *doc* — fail closed.

    "" is the whole document; each reference token is unescaped (``~1`` -> /,
    ``~0`` -> ~, in that order); array indices are strict (digits only, no
    leading zeros except "0", no ``-``).
    """
    if not isinstance(pointer, str):
        raise PointerError(f"pointer must be a string, got {pointer!r}")
    if pointer == "":
        return doc
    if not pointer.startswith("/"):
        raise PointerError(f"pointer must start with '/', got {pointer!r}")
    node = doc
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                raise PointerError(f"key {token!r} not found at {pointer!r}")
            node = node[token]
        elif isinstance(node, list):
            if not token.isdigit() or (len(token) > 1 and token[0] == "0"):
                raise PointerError(
                    f"array index {token!r} invalid at {pointer!r} "
                    f"(digits only, no leading zeros)")
            ix = int(token)
            if ix >= len(node):
                raise PointerError(f"index {ix} out of range at {pointer!r}")
            node = node[ix]
        else:
            raise PointerError(
                f"cannot descend into {type(node).__name__} at {pointer!r}")
    return node


def _type_ok(value: object, declared: str) -> bool:
    if declared == "boolean":
        return isinstance(value, bool)
    if declared == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if declared == "number":
        return isinstance(value, (int, float, Decimal)) and \
            not isinstance(value, bool)
    if declared == "string":
        return isinstance(value, str)
    return False  # unknown types are rejected by shape validation first


def _as_decimal(value: object) -> Decimal | None:
    """Exact Decimal for a numeric value; None when not numeric.

    Strings parse as Decimal literals (the exactness escape hatch for
    register-side values); booleans are NOT numbers here — a bound boolean
    compares as a boolean.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int):
        return Decimal(value)
    if isinstance(value, (float, str)):
        try:
            return Decimal(str(value))
        except InvalidOperation:
            return None
    return None


def _compare(artifact_val: object, register_val: object, comparator: str,
             tolerance: object) -> tuple[bool, str]:
    """(ok, detail). Numeric comparisons are exact decimal arithmetic."""
    a = _as_decimal(artifact_val)
    r = _as_decimal(register_val)
    if a is None or r is None:
        # Non-numeric: only exact equality is meaningful.
        if comparator != "exact":
            return False, (f"comparator '{comparator}' needs numeric values, "
                           f"got artifact={artifact_val!r} "
                           f"register={register_val!r}")
        if isinstance(artifact_val, bool) or isinstance(register_val, bool):
            return (artifact_val is register_val
                    or (isinstance(register_val, str)
                        and str(artifact_val).lower() == register_val.lower()),
                    f"artifact={artifact_val!r} register={register_val!r}")
        return (str(artifact_val) == str(register_val),
                f"artifact={artifact_val!r} register={register_val!r}")
    detail = f"artifact={a} register={r}"
    if comparator == "exact":
        return a == r, detail
    if comparator == "minimum":
        return a >= r, detail + " (artifact must be >= register)"
    if comparator == "maximum":
        return a <= r, detail + " (artifact must be <= register)"
    if comparator == "bounded":
        tol = _as_decimal(tolerance)
        if tol is None or tol < 0:
            return False, f"bounded comparator needs a tolerance >= 0, got {tolerance!r}"
        return abs(a - r) <= tol, detail + f" tolerance={tol}"
    return False, f"unknown comparator {comparator!r}"  # pragma: no cover


def bound_metric_names(claim: dict) -> set:
    """The metric names a claim binds explicitly (for v1-scan exemption)."""
    bindings = claim.get("metric_bindings")
    if not isinstance(bindings, list):
        return set()
    return {b.get("metric") for b in bindings
            if isinstance(b, dict) and isinstance(b.get("metric"), str)}


def check_metric_bindings(claims: list, cfg: Config) -> list:
    """Verify every metric binding — the schema-v2 replacement for key
    scanning. Every problem is a finding; nothing is skipped."""
    out: list[Finding] = []
    for c in claims:
        bindings = c.get("metric_bindings")
        if not bindings:
            continue
        cid = c.get("id", "<missing-id>")
        arts = c.get("artifact") or []
        if isinstance(arts, str):
            arts = [arts]
        json_arts = [a for a in arts if str(a).endswith(".json")]

        cache: dict[str, object] = {}

        def _load(rel: str, cid: str = cid) -> object:
            if rel in cache:
                return cache[rel]
            from .gate import _resolve_within_root
            resolved = _resolve_within_root(cfg, rel)
            if resolved is None or not resolved.exists():
                cache[rel] = None
                return None
            try:
                cache[rel] = json.loads(
                    Path(resolved).read_text(encoding="utf-8"),
                    parse_float=Decimal)
            except (json.JSONDecodeError, OSError):
                cache[rel] = None
            return cache[rel]

        for i, b in enumerate(bindings):
            label = f"{cid}.metric_bindings[{i}]"
            metric = b.get("metric")
            comparator = b.get("comparator", "exact")
            if comparator not in COMPARATORS:
                out.append((f"binding-bad-comparator:{cid}:{metric}",
                            f"{label}: comparator must be one of "
                            f"{COMPARATORS}, got {comparator!r}"))
                continue
            declared_type = b.get("type")
            if declared_type is not None and declared_type not in TYPES:
                out.append((f"binding-bad-type:{cid}:{metric}",
                            f"{label}: type must be one of {TYPES}, "
                            f"got {declared_type!r}"))
                continue
            if comparator == "bounded" and "tolerance" not in b:
                out.append((f"binding-missing-tolerance:{cid}:{metric}",
                            f"{label}: comparator 'bounded' requires a "
                            f"tolerance"))
                continue

            # Which artifact does this binding read?
            rel = b.get("artifact")
            if rel is None:
                if len(json_arts) == 1:
                    rel = json_arts[0]
                else:
                    out.append((f"binding-artifact-ambiguous:{cid}:{metric}",
                                f"{label}: claim cites {len(json_arts)} JSON "
                                f"artifacts — the binding must name one "
                                f"explicitly"))
                    continue
            elif rel not in arts:
                out.append((f"binding-artifact-unclaimed:{cid}:{metric}",
                            f"{label}: bound artifact {rel} is not in the "
                            f"claim's artifact list"))
                continue

            # Which value does the register assert?
            register_val = b.get("value")
            if register_val is None:
                metrics = c.get("metrics")
                if isinstance(metrics, dict) and metric in metrics:
                    register_val = metrics[metric]
                else:
                    out.append((f"binding-no-value:{cid}:{metric}",
                                f"{label}: no `value` and no metrics[{metric!r}] "
                                f"to bind against"))
                    continue

            doc = _load(rel)
            if doc is None:
                out.append((f"binding-artifact-unreadable:{cid}:{metric}",
                            f"{label}: artifact {rel} is missing or not "
                            f"readable JSON"))
                continue
            try:
                actual = resolve_pointer(doc, b.get("pointer"))
            except PointerError as exc:
                out.append((f"binding-pointer-missing:{cid}:{metric}",
                            f"{label}: pointer does not resolve in {rel} — "
                            f"{exc}"))
                continue
            if declared_type is not None and not _type_ok(actual, declared_type):
                out.append((f"binding-type-mismatch:{cid}:{metric}",
                            f"{label}: {rel}{b.get('pointer')} is "
                            f"{type(actual).__name__}, binding declares "
                            f"{declared_type}"))
                continue
            ok, detail = _compare(actual, register_val, comparator,
                                  b.get("tolerance"))
            if not ok:
                out.append((f"binding-value-mismatch:{cid}:{metric}",
                            f"{label}: {rel}{b.get('pointer')} fails "
                            f"'{comparator}': {detail}"))
    return out
