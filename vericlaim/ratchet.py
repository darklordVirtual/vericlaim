# SPDX-License-Identifier: Apache-2.0
"""The ratchet — Eiffel's loop variant, applied to repository quality.

A loop variant in Eiffel is an integer expression that must strictly decrease
on every iteration; it is how a loop proves it terminates. A repository has the
same need and no such mechanism: the debt you tolerate today (claims still on
legacy shell reproduction, numbers nobody bound, findings parked in the
baseline) has nothing stopping it from growing tomorrow. Every individual
increase looks reasonable in review.

A ratchet is a declared ceiling on such a quantity:

    [vericlaim.ratchet]
    legacy_shell_claims = 14
    baselined_findings  = 0
    unbound_numbers     = 900

Exceeding a ceiling fails the gate. Coming in *under* one is reported as a note
telling you to tighten it, so the ceiling tracks reality downward and never
drifts back up. Unlike a target in a roadmap, this is checked on every commit,
which is exactly the difference between an intention and a contract.

Metrics are computed by the gate itself from things it already knows, so a
ratchet can never be satisfied by a stale hand-written artifact.
"""
from __future__ import annotations

from .config import Config

Finding = tuple[str, str]

# name -> one-line description, shown when a ceiling is breached.
METRICS = {
    "legacy_shell_claims":
        "claims still reproduced by an unstructured shell string rather than "
        "a declarative reproduce_argv spec",
    "baselined_findings":
        "pre-existing violations grandfathered in the baseline file",
    "claims_without_assumes":
        "claims that state a metric but declare no machine-readable "
        "precondition (`assumes`)",
    "claims_without_reproduce":
        "claims with no reproduction at all - their number cannot be shown to "
        "be still true today",
    "unbound_numbers":
        "numeric literals in the docs that no anchor or value token binds "
        "(see `vericlaim coverage`)",
}


def measure(claims: list[dict], cfg: Config, *, baselined: int,
            unbound_numbers: int | None) -> dict[str, int]:
    """Current value of every ratchet metric."""
    legacy = sum(1 for c in claims
                 if c.get("reproduce") and not c.get("reproduce_argv"))
    no_assumes = sum(1 for c in claims
                     if c.get("metrics") and not c.get("assumes"))
    no_repro = sum(1 for c in claims
                   if not c.get("reproduce") and not c.get("reproduce_argv"))
    out = {
        "legacy_shell_claims": legacy,
        "baselined_findings": baselined,
        "claims_without_assumes": no_assumes,
        "claims_without_reproduce": no_repro,
    }
    if unbound_numbers is not None:
        out["unbound_numbers"] = unbound_numbers
    return out


def check(actual: dict[str, int], cfg: Config,
          notes: list[str]) -> list[Finding]:
    out: list[Finding] = []
    for name, ceiling in cfg.ratchet:
        if name not in METRICS:
            out.append((f"ratchet-unknown-metric:{name}",
                        f"[vericlaim.ratchet] names unknown metric {name!r} "
                        f"(known: {', '.join(sorted(METRICS))})"))
            continue
        if name not in actual:
            notes.append(f"ratchet metric {name!r} was not measured this run "
                         f"(coverage metrics need `coverage_artifact` set)")
            continue
        value = actual[name]
        if value > ceiling:
            out.append((f"ratchet-regression:{name}",
                        f"ratchet {name}={value} exceeds its ceiling of "
                        f"{ceiling} - {METRICS[name]}. This quantity is only "
                        f"allowed to fall; fix the regression or state a "
                        f"deliberate, reviewed increase in vericlaim.toml"))
        elif value < ceiling:
            notes.append(f"ratchet {name}={value} is below its ceiling of "
                         f"{ceiling} - tighten it to {value} to lock the gain in")
    return out
