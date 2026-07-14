# SPDX-License-Identifier: Apache-2.0
"""Shannon entropy, cross-entropy, KL divergence and perplexity — reusable,
claim-bound.

A pre-verified claimlib code artifact for AI assurance. Shannon (1948)
defined the information content of a distribution:

    H(p)      = -sum_i p_i log2 p_i          (bits; 0 log 0 = 0)
    H(p, q)   = -sum_i p_i log2 q_i          (cross-entropy)
    KL(p||q)  = H(p, q) - H(p) = sum p_i log2 (p_i / q_i)
    PPL(p)    = 2 ** H(p)                     (perplexity)

These are the units AI evaluation is written in: language-model loss IS a
cross-entropy, perplexity its exponential, and KL the drift measure between
a model and a reference. Probabilities are validated EXACTLY (Fractions
summing to exactly 1, every term >= 0); the log arithmetic is float with
documented tolerance, and structural identities (uniform, deterministic,
Gibbs) are enforced by the evidence.

KL(p||q) is +infinity when q assigns 0 where p does not — this module FAILS
CLOSED there rather than returning a number. The caveat travels with the
claim.

Public API
----------
    entropy(probs) -> float                  # bits
    cross_entropy(p, q) -> float             # bits
    kl_divergence(p, q) -> float             # bits, >= 0
    perplexity(probs) -> float

    >>> entropy([0.5, 0.5])
    1.0
"""
from __future__ import annotations

import math
from fractions import Fraction


class EntropyError(ValueError):
    """Invalid distribution (fail closed)."""


def _dist(probs, what: str = "probs") -> list:
    if not isinstance(probs, (list, tuple)) or not probs:
        raise EntropyError(f"{what} must be a non-empty sequence")
    out = []
    for i, p in enumerate(probs):
        if isinstance(p, bool) or not isinstance(p, (int, float, str,
                                                     Fraction)):
            raise EntropyError(f"{what}[{i}] must be a number, got {p!r}")
        if isinstance(p, float) and (p != p or p in (float("inf"),
                                                     float("-inf"))):
            raise EntropyError(f"{what}[{i}] must be finite")
        try:
            f = Fraction(str(p)) if isinstance(p, (float, str)) else Fraction(p)
        except (ValueError, ZeroDivisionError) as exc:
            raise EntropyError(f"{what}[{i}]: bad probability {p!r}") from exc
        if f < 0:
            raise EntropyError(f"{what}[{i}] must be >= 0, got {p!r}")
        out.append(f)
    if sum(out) != 1:
        raise EntropyError(
            f"{what} must sum to exactly 1, got {float(sum(out))!r} — "
            f"pass exact strings/Fractions if float rounding is the cause")
    return out


def entropy(probs) -> float:
    """H(p) in bits, with the 0 log 0 = 0 convention. Exact validation."""
    p = _dist(probs)
    return -sum(float(pi) * math.log2(float(pi)) for pi in p if pi > 0)


def cross_entropy(p, q) -> float:
    """H(p, q) in bits; fails closed when q_i = 0 while p_i > 0."""
    pp = _dist(p, "p")
    qq = _dist(q, "q")
    if len(pp) != len(qq):
        raise EntropyError(f"p and q must have equal length "
                           f"({len(pp)} != {len(qq)})")
    total = 0.0
    for i, (pi, qi) in enumerate(zip(pp, qq)):
        if pi == 0:
            continue
        if qi == 0:
            raise EntropyError(
                f"cross-entropy is infinite: q[{i}] = 0 where p[{i}] > 0")
        total -= float(pi) * math.log2(float(qi))
    return total


def kl_divergence(p, q) -> float:
    """KL(p || q) in bits — clamped at 0 so float noise can never make the
    provably non-negative divergence (Gibbs' inequality) come out negative."""
    return max(0.0, cross_entropy(p, q) - entropy(p))


def perplexity(probs) -> float:
    """2 ** H(p): the effective number of equally-likely outcomes."""
    return 2.0 ** entropy(probs)
