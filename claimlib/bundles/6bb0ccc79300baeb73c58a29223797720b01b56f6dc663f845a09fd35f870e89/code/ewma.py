# SPDX-License-Identifier: Apache-2.0
"""EWMA -- exponentially weighted moving average and its control chart.

A pre-verified claimlib code artifact for observability and statistical
process control. The EWMA statistic (Roberts 1959, there called a geometric
moving average) smooths a series by folding each new observation into a
running average with weight lambda:

    z_i = lambda * x_i + (1 - lambda) * z_{i-1},        0 < lambda <= 1

so past observations decay geometrically. The EWMA control chart flags a
process shift when z_i leaves the limits (NIST/SEMATECH e-Handbook 6.3.2.4):

    mu0 +/- L * sigma * sqrt(lambda/(2-lambda) * (1 - (1-lambda)^(2i)))

whose bracketed factor grows from lambda^2 at i=1 to the steady-state value
lambda/(2-lambda) as i -> infinity. That the recursion matches exact rational
arithmetic and that the chart reproduces the published NIST/SEMATECH worked
example is registered as a claim and proven by a committed evidence artifact.

Public API
----------
    ewma_update(z_prev, x, lam) -> float
    ewma_series(values, lam, z0) -> list[float]        # z_1..z_n
    control_limits(mu0, sigma, lam, i, L=3.0) -> (lcl, ucl)   # exact, i >= 1
    steady_state_limits(mu0, sigma, lam, L=3.0) -> (lcl, ucl)
    chart(values, mu0, sigma, lam=0.3, L=3.0, exact_limits=True) -> dict

    >>> ewma_series([52.0, 47.0], 0.3, 50.0)
    [50.6, 49.52]
"""
from __future__ import annotations

import math
from collections.abc import Sequence


class EWMAError(ValueError):
    """Invalid smoothing constant, sigma, L, index, or observation."""


def _check_lambda(lam: float) -> float:
    if isinstance(lam, bool) or not isinstance(lam, (int, float)):
        raise EWMAError("lambda must be a real number")
    if not 0.0 < lam <= 1.0:
        raise EWMAError(f"lambda must be in (0, 1], got {lam!r}")
    return float(lam)


def _check_number(x: float, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise EWMAError(f"{name} must be a real number, got {x!r}")
    x = float(x)
    if not math.isfinite(x):
        raise EWMAError(f"{name} must be finite, got {x!r}")
    return x


def ewma_update(z_prev: float, x: float, lam: float) -> float:
    """Return z = lam*x + (1-lam)*z_prev -- one step of the EWMA recursion."""
    lam = _check_lambda(lam)
    z_prev = _check_number(z_prev, "z_prev")
    x = _check_number(x, "x")
    return lam * x + (1.0 - lam) * z_prev


def ewma_series(values: Sequence[float], lam: float, z0: float) -> list[float]:
    """Return [z_1, ..., z_n] for *values*, seeded with z_0 = *z0*.

    In control-chart use, *z0* is the process target mu0 (or the historical
    mean). The returned list has exactly ``len(values)`` entries; the seed is
    not included.
    """
    lam = _check_lambda(lam)
    z = _check_number(z0, "z0")
    if len(values) == 0:
        raise EWMAError("values must be non-empty")
    out: list[float] = []
    for k, x in enumerate(values):
        x = _check_number(x, f"values[{k}]")
        z = lam * x + (1.0 - lam) * z
        out.append(z)
    return out


def _check_chart_params(mu0: float, sigma: float, lam: float,
                        L: float) -> tuple[float, float, float, float]:
    mu0 = _check_number(mu0, "mu0")
    sigma = _check_number(sigma, "sigma")
    lam = _check_lambda(lam)
    L = _check_number(L, "L")
    if sigma <= 0.0:
        raise EWMAError(f"sigma must be > 0, got {sigma!r}")
    if L <= 0.0:
        raise EWMAError(f"L must be > 0, got {L!r}")
    return mu0, sigma, lam, L


def control_limits(mu0: float, sigma: float, lam: float, i: int,
                   L: float = 3.0) -> tuple[float, float]:
    """Return the exact (time-varying) (LCL, UCL) at observation index *i*.

    half-width = L * sigma * sqrt(lam/(2-lam) * (1 - (1-lam)^(2i))), i >= 1.
    At i=1 the factor under the root is exactly lam^2; it increases
    monotonically toward the steady-state value lam/(2-lam).
    """
    mu0, sigma, lam, L = _check_chart_params(mu0, sigma, lam, L)
    if isinstance(i, bool) or not isinstance(i, int) or i < 1:
        raise EWMAError(f"i must be an int >= 1, got {i!r}")
    factor = lam / (2.0 - lam) * (1.0 - (1.0 - lam) ** (2 * i))
    half = L * sigma * math.sqrt(factor)
    return (mu0 - half, mu0 + half)


def steady_state_limits(mu0: float, sigma: float, lam: float,
                        L: float = 3.0) -> tuple[float, float]:
    """Return the asymptotic (LCL, UCL): mu0 +/- L*sigma*sqrt(lam/(2-lam))."""
    mu0, sigma, lam, L = _check_chart_params(mu0, sigma, lam, L)
    half = L * sigma * math.sqrt(lam / (2.0 - lam))
    return (mu0 - half, mu0 + half)


def chart(values: Sequence[float], mu0: float, sigma: float,
          lam: float = 0.3, L: float = 3.0,
          exact_limits: bool = True) -> dict:
    """Run an EWMA control chart over *values*; z_0 = mu0.

    Returns {"points": [...], "out_of_control": [i, ...], "n": n}. Each point
    is {"i", "x", "z", "lcl", "ucl", "in_control"} with i counting from 1.
    ``exact_limits=True`` uses the time-varying limits; ``False`` uses the
    steady-state limits for every point.
    """
    mu0, sigma, lam, L = _check_chart_params(mu0, sigma, lam, L)
    zs = ewma_series(values, lam, mu0)
    points = []
    ooc = []
    for idx, (x, z) in enumerate(zip(values, zs), start=1):
        if exact_limits:
            lcl, ucl = control_limits(mu0, sigma, lam, idx, L)
        else:
            lcl, ucl = steady_state_limits(mu0, sigma, lam, L)
        in_control = lcl <= z <= ucl
        if not in_control:
            ooc.append(idx)
        points.append({"i": idx, "x": float(x), "z": z,
                       "lcl": lcl, "ucl": ucl, "in_control": in_control})
    return {"points": points, "out_of_control": ooc, "n": len(points)}
