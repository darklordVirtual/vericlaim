# SPDX-License-Identifier: Apache-2.0
"""Register-level contract checks — the Design-by-Contract layer.

``gate.py`` checks that a claim's *evidence* exists and that docs quote it
without drift. This module checks the parts of the contract that Meyer's
Eiffel makes explicit but a claim register usually leaves as prose:

``assumes``      the claim's PRECONDITION (Eiffel ``require``). A ``caveat`` is
                 free text nothing can verify; an ``assumes`` entry is a named
                 scope condition, and when it carries a JSON Pointer it is
                 resolved in the evidence and compared. The scope stops being a
                 promise and becomes a check.
``status``       claim LIFECYCLE. ``superseded`` claims are never deleted — they
                 keep their artifact and name their replacement — and may not be
                 quoted on a front-page document.
``retired_values`` the strings a claim's numbers used to be written as. They
                 become an automatically derived stale-string denylist, so a
                 re-issued number cannot survive anywhere in the docs.
``blindness``    the MEASUREMENT CONDITION, orthogonal to evidence level: was
                 this measured once on a sealed set, or on data the system had
                 already seen? A sealed set is spent after one use, so two
                 active claims may not share one.
``rate``         a rate claim must carry its sample size and the upper bound
                 that size supports. "0.0% failures" from n=70 is an overclaim
                 by construction; the gate computes the Wilson upper bound and
                 refuses a register that states the point estimate alone.
``derived_from`` contract VARIANCE for reuse (Liskov, as Meyer formalised it):
                 a claim vendored from a claimlib bundle may be demoted freely
                 but never promoted above the evidence level of its source.

Every check fails closed: an unresolvable pointer, an unknown status, a
superseded claim with no replacement, a bundle whose bytes moved — findings,
never skips.
"""
from __future__ import annotations

import hashlib
import json
from decimal import Decimal, InvalidOperation

from .binding import resolve_pointer
from .config import Config

Finding = tuple[str, str]

STATUSES = ("active", "superseded")
BLINDNESS = ("blind", "development", "omitted")
# Two-sided 95% normal quantile: the Wilson interval's z. Fixed, not
# configurable — a claim that needs a different confidence level should say so
# in its caveat rather than quietly widening its own bound.
WILSON_Z = Decimal("1.959963984540054")


# -- Eiffel `require`: machine-checkable preconditions ----------------------

def _artifact_list(claim: dict) -> list[str]:
    art = claim.get("artifact")
    if isinstance(art, str):
        return [art]
    return [a for a in (art or []) if isinstance(a, str)]


def _load_json(cfg: Config, rel: str) -> object | None:
    p = cfg.path(rel)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"), parse_float=Decimal)
    except (json.JSONDecodeError, OSError):
        return None


def check_assumes(claims: list[dict], cfg: Config) -> list[Finding]:
    """Verify each claim's preconditions.

    An entry is ``{key, value}``; adding ``pointer`` (and optionally
    ``artifact``) makes it *enforced* — the value is resolved in the evidence
    and must match. Under ``require_assumes`` every claim that states a metric
    must carry at least one entry, so scope can never be prose-only.
    """
    out: list[Finding] = []
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        entries = claim.get("assumes")
        if entries is None:
            if cfg.require_assumes and claim.get("metrics"):
                out.append((f"assumes-missing:{cid}",
                            f"{cid}: states metrics but declares no `assumes` "
                            f"precondition - under this profile a claim's scope "
                            f"must be machine-readable, not caveat prose only"))
            continue
        for i, entry in enumerate(entries):
            label = f"{cid}.assumes[{i}]"
            key = entry.get("key")
            if not isinstance(key, str) or not key:
                out.append((f"assumes-no-key:{cid}:{i}",
                            f"{label}: every precondition needs a `key`"))
                continue
            if "value" not in entry:
                out.append((f"assumes-no-value:{cid}:{key}",
                            f"{label}: precondition '{key}' declares no `value`"))
                continue
            pointer = entry.get("pointer")
            if pointer is None:
                continue  # declared but not machine-bound; documented as such
            arts = ([entry["artifact"]] if isinstance(entry.get("artifact"), str)
                    else [a for a in _artifact_list(claim) if a.endswith(".json")])
            if len(arts) != 1:
                out.append((f"assumes-ambiguous-artifact:{cid}:{key}",
                            f"{label}: pointer given but the artifact is "
                            f"ambiguous ({len(arts)} candidates) - name it "
                            f"explicitly with `artifact:`"))
                continue
            doc = _load_json(cfg, arts[0])
            if doc is None:
                out.append((f"assumes-artifact-unreadable:{cid}:{key}",
                            f"{label}: cannot read evidence {arts[0]} to verify "
                            f"precondition '{key}'"))
                continue
            try:
                actual = resolve_pointer(doc, pointer)
            except (KeyError, IndexError, ValueError, TypeError) as exc:
                out.append((f"assumes-pointer-unresolved:{cid}:{key}",
                            f"{label}: pointer {pointer!r} does not resolve in "
                            f"{arts[0]} ({exc})"))
                continue
            if str(actual) != str(entry["value"]):
                out.append((f"assumes-violated:{cid}:{key}",
                            f"{label}: precondition '{key}' assumes "
                            f"{entry['value']!r} but the evidence records "
                            f"{actual!r} - the claim was measured outside the "
                            f"scope it declares"))
    return out


# -- Lifecycle: superseded claims are archived, never deleted ---------------

def check_lifecycle(claims: list[dict], cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    ids = {c.get("id") for c in claims}
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        status = claim.get("status", "active")
        if status not in STATUSES:
            out.append((f"status-unknown:{cid}",
                        f"{cid}: unknown status {status!r} "
                        f"(expected one of {', '.join(STATUSES)})"))
            continue
        replacement = claim.get("superseded_by")
        if status == "superseded":
            if not replacement:
                out.append((f"superseded-no-replacement:{cid}",
                            f"{cid}: status is 'superseded' but names no "
                            f"`superseded_by` - a replaced result must say what "
                            f"replaced it, or the reader has nowhere to go"))
            elif replacement not in ids:
                out.append((f"superseded-unknown-replacement:{cid}",
                            f"{cid}: superseded_by names {replacement} which is "
                            f"not in the register"))
            elif replacement == cid:
                out.append((f"superseded-self:{cid}",
                            f"{cid}: superseded_by points at itself"))
        elif replacement:
            out.append((f"superseded-by-on-active:{cid}",
                        f"{cid}: names `superseded_by` but its status is "
                        f"'{status}' - set status: superseded, or drop the field"))
        retired = claim.get("retired_values")
        if retired is not None and not all(isinstance(r, str) and r for r in retired):
            out.append((f"retired-values-shape:{cid}",
                        f"{cid}: every `retired_values` entry must be a "
                        f"non-empty string"))
    return out


def retired_denylist(claims: list[dict]) -> list[tuple[str, str]]:
    """The stale-string denylist DERIVED from the register.

    ``vericlaim.toml``'s ``stale_strings`` is hand-curated and only as complete
    as someone's memory. These entries are produced at re-issue time by the
    claim that owns the number, so the first CI run after a re-benchmark
    enumerates every document still showing the old value.
    """
    out: list[tuple[str, str]] = []
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        for value in claim.get("retired_values") or []:
            if isinstance(value, str) and value:
                out.append((value, f"retired value of {cid} - quote the current "
                                   f"registered value instead"))
    return out


def superseded_ids(claims: list[dict]) -> set[str]:
    return {c.get("id") for c in claims
            if c.get("status", "active") == "superseded" and c.get("id")}


# -- Measurement condition: a sealed set is spent after one use -------------

def check_blindness(claims: list[dict], cfg: Config) -> list[Finding]:
    out: list[Finding] = []
    sealed: dict[str, str] = {}
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        blindness = claim.get("blindness", "omitted")
        if blindness not in BLINDNESS:
            out.append((f"blindness-unknown:{cid}",
                        f"{cid}: unknown blindness {blindness!r} "
                        f"(expected one of {', '.join(BLINDNESS)})"))
            continue
        set_id = claim.get("sealed_set")
        if blindness != "blind":
            continue
        if not isinstance(set_id, str) or not set_id:
            out.append((f"blind-no-sealed-set:{cid}",
                        f"{cid}: blindness 'blind' requires a `sealed_set` "
                        f"identifier - a blind measurement is only blind with "
                        f"respect to a named, sealed evaluation set"))
            continue
        if claim.get("status", "active") != "active":
            continue  # a superseded round legitimately keeps its set id
        prior = sealed.get(set_id)
        if prior is not None:
            out.append((f"sealed-set-reused:{cid}:{set_id}",
                        f"{cid}: sealed set {set_id!r} was already spent by "
                        f"{prior} - a set is blind exactly once; re-measuring on "
                        f"it is a 'development' measurement, not a blind one"))
        else:
            sealed[set_id] = cid
    return out


# -- Statistical honesty: no point estimate without the bound its n supports -

def wilson_upper(successes: int, n: int) -> Decimal:
    """Upper end of the two-sided 95% Wilson score interval, as a proportion.

    Chosen over the normal approximation because the interesting claims sit at
    p=0: the normal interval collapses to [0, 0] and would certify a zero
    failure rate from any sample size at all, which is exactly the overclaim
    this check exists to stop.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    n_d, k = Decimal(n), Decimal(successes)
    p = k / n_d
    z2 = WILSON_Z * WILSON_Z
    denom = 1 + z2 / n_d
    centre = p + z2 / (2 * n_d)
    radius = WILSON_Z * ((p * (1 - p) / n_d + z2 / (4 * n_d * n_d)).sqrt())
    return min(Decimal(1), (centre + radius) / denom)


def _quantize_like(value: Decimal, stated: Decimal) -> Decimal:
    """Round *value* to the number of decimal places *stated* was written with,
    so a register may report 0.0 or 0.00 without the gate inventing digits."""
    places = max(0, -stated.as_tuple().exponent)
    return value.quantize(Decimal(1).scaleb(-places))


def check_rates(claims: list[dict], cfg: Config) -> list[Finding]:
    """A ``rate:`` block ties a percentage to the sample that produced it."""
    out: list[Finding] = []
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        rate = claim.get("rate")
        if rate is None:
            continue
        if not isinstance(rate, dict):
            out.append((f"rate-shape:{cid}", f"{cid}: `rate` must be a mapping"))
            continue
        metrics = claim.get("metrics") or {}
        metric = rate.get("metric")
        bound_metric = rate.get("bound_metric")
        try:
            n = int(rate["n"])
            successes = int(rate["successes"])
        except (KeyError, TypeError, ValueError):
            out.append((f"rate-no-sample:{cid}",
                        f"{cid}: a `rate` block requires integer `n` and "
                        f"`successes` - a percentage without its sample size "
                        f"states nothing about what it generalises to"))
            continue
        if n <= 0 or successes < 0 or successes > n:
            out.append((f"rate-invalid-sample:{cid}",
                        f"{cid}: rate sample is impossible "
                        f"(successes={successes}, n={n})"))
            continue
        if not isinstance(metric, str) or metric not in metrics:
            out.append((f"rate-unknown-metric:{cid}",
                        f"{cid}: rate.metric {metric!r} is not a registered "
                        f"metric of this claim"))
            continue
        if not isinstance(bound_metric, str) or bound_metric not in metrics:
            out.append((f"rate-no-bound:{cid}",
                        f"{cid}: rate declares no `bound_metric` present in "
                        f"`metrics` - the point estimate may not be registered "
                        f"without the upper bound its n supports"))
            continue
        point = (Decimal(successes) / Decimal(n)) * 100
        upper = wilson_upper(successes, n) * 100
        for name, computed in ((metric, point), (bound_metric, upper)):
            try:
                stated = Decimal(str(metrics[name]))
            except (InvalidOperation, TypeError):
                out.append((f"rate-non-numeric:{cid}:{name}",
                            f"{cid}: metric {name!r} is not numeric"))
                continue
            if stated != _quantize_like(computed, stated):
                out.append((f"rate-mismatch:{cid}:{name}",
                            f"{cid}: metric {name}={metrics[name]} but "
                            f"{successes}/{n} gives "
                            f"{_quantize_like(computed, stated)} "
                            f"(95% Wilson) - recompute or restate"))
    return out


def rate_pairs(claims: list[dict]) -> dict[str, tuple[str, str]]:
    """claim id -> (point metric, bound metric) for every rate claim.

    The gate uses this to refuse a doc anchor that quotes the point estimate
    without the bound alongside it.
    """
    out: dict[str, tuple[str, str]] = {}
    for claim in claims:
        rate = claim.get("rate")
        cid = claim.get("id")
        if isinstance(rate, dict) and isinstance(cid, str):
            metric, bound = rate.get("metric"), rate.get("bound_metric")
            if isinstance(metric, str) and isinstance(bound, str):
                out[cid] = (metric, bound)
    return out


# -- Contract variance: a vendored claim may be demoted, never promoted -----

def check_inheritance(claims: list[dict], cfg: Config) -> list[Finding]:
    """Liskov for reused knowledge.

    A claim imported from a claimlib bundle inherits a contract. Meyer's rule
    for redeclaration says a descendant may weaken a precondition but never a
    postcondition; here the postcondition is the evidence level, so an imported
    claim may be *demoted* freely and promoted only with its own new evidence.
    The bundle's own bytes are re-verified at the same time: inheriting from a
    source that has silently moved is not inheritance.
    """
    out: list[Finding] = []
    levels = {name: i for i, name in enumerate(cfg.evidence_levels)}
    for claim in claims:
        cid = claim.get("id", "<unknown>")
        source = claim.get("derived_from")
        if not source:
            continue
        if not isinstance(source, str):
            out.append((f"derived-from-shape:{cid}",
                        f"{cid}: `derived_from` must be the repo-relative path "
                        f"of the source bundle"))
            continue
        bundle = cfg.path(source)
        manifest_p, claim_p = bundle / "MANIFEST.json", bundle / "claim.json"
        if not claim_p.exists() or not manifest_p.exists():
            out.append((f"derived-from-missing:{cid}",
                        f"{cid}: derived_from {source} is not a bundle "
                        f"(MANIFEST.json + claim.json expected)"))
            continue
        try:
            manifest = json.loads(manifest_p.read_text(encoding="utf-8"))
            source_claim = json.loads(claim_p.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            out.append((f"derived-from-unreadable:{cid}",
                        f"{cid}: cannot read bundle {source}: {exc}"))
            continue
        for rel, expected in (manifest.get("files") or {}).items():
            f = bundle / rel
            if not f.exists():
                out.append((f"derived-bundle-missing-file:{cid}:{rel}",
                            f"{cid}: source bundle {source} is missing {rel}"))
                continue
            actual = hashlib.sha256(f.read_bytes()).hexdigest()
            if actual != expected:
                out.append((f"derived-bundle-tampered:{cid}:{rel}",
                            f"{cid}: source bundle file {rel} hashes {actual} "
                            f"but its manifest records {expected} - the "
                            f"inherited contract's own evidence has moved"))
        own, src = claim.get("evidence_level"), source_claim.get("evidence_level")
        if own in levels and src in levels and levels[own] > levels[src]:
            out.append((f"derived-level-promoted:{cid}",
                        f"{cid}: evidence_level '{own}' is stronger than its "
                        f"source's '{src}' ({source}). A vendored claim may be "
                        f"demoted freely but promoted only on new evidence of "
                        f"its own - register that evidence as a separate claim"))
    return out


def run_contract_checks(claims: list[dict], cfg: Config) -> list[Finding]:
    """Every register-level contract check, in one call for the gate."""
    return (check_assumes(claims, cfg)
            + check_lifecycle(claims, cfg)
            + check_blindness(claims, cfg)
            + check_rates(claims, cfg)
            + check_inheritance(claims, cfg))
