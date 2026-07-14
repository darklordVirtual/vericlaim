# SPDX-License-Identifier: Apache-2.0
"""Pt100 RTD resistance <-> temperature per IEC 60751 (Callendar–Van Dusen)
— reusable, claim-bound.

A pre-verified claimlib code artifact. Industrial platinum resistance
thermometers follow the Callendar–Van Dusen equations standardized in
IEC 60751 with the standard coefficients (alpha = 0.00385 ohm/ohm/degC
sensors):

    t >= 0 degC:  R(t) = R0 * (1 + A*t + B*t**2)
    t <  0 degC:  R(t) = R0 * (1 + A*t + B*t**2 + C*(t - 100)*t**3)

    A = 3.9083e-3 /degC,  B = -5.775e-7 /degC**2,  C = -4.183e-12 /degC**4
    R0 = 100 ohm for a Pt100 (Pt500/Pt1000 scale R0).

The inverse (resistance -> temperature) uses the exact quadratic solution
above 0 degC and monotone bisection below. Valid range: -200..850 degC
(IEC 60751's span). That the polynomial reproduces the published standard
table points (100.0000 ohm at 0 degC, 138.5055 at 100, 18.5201 at -200,
175.8560 at 200, 390.4811 at 850) and that the inverse round-trips to
micro-degC precision is registered as a claim and proven by a committed
evidence artifact.

This is the STANDARD curve, not a calibration: a real sensor has tolerance
classes (AA/A/B/C) and drift — the caveat travels with the claim.

Public API
----------
    resistance(t_c: float, r0: float = 100.0) -> float   # ohm
    temperature(r_ohm: float, r0: float = 100.0) -> float  # degC

    >>> round(resistance(100.0), 4)
    138.5055
    >>> round(temperature(138.5055), 4)
    100.0
"""
from __future__ import annotations

A = 3.9083e-3
B = -5.775e-7
C = -4.183e-12

_T_MIN = -200.0
_T_MAX = 850.0


class Pt100Error(ValueError):
    """Input outside the IEC 60751 domain (fail closed)."""


def _check_num(x: float, name: str) -> float:
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise Pt100Error(f"{name} must be a number, got {x!r}")
    v = float(x)
    if v != v or v in (float("inf"), float("-inf")):
        raise Pt100Error(f"{name} must be finite, got {x!r}")
    return v


def _check_r0(r0: float) -> float:
    v = _check_num(r0, "r0")
    if v <= 0:
        raise Pt100Error(f"r0 must be > 0 ohm, got {r0!r}")
    return v


def resistance(t_c: float, r0: float = 100.0) -> float:
    """RTD resistance in ohm at *t_c* degC (IEC 60751 standard curve)."""
    t = _check_num(t_c, "t_c")
    r = _check_r0(r0)
    if not _T_MIN <= t <= _T_MAX:
        raise Pt100Error(f"temperature must be in [{_T_MIN}, {_T_MAX}] degC "
                         f"(IEC 60751 span), got {t_c!r}")
    poly = 1.0 + A * t + B * t * t
    if t < 0.0:
        poly += C * (t - 100.0) * t ** 3
    return r * poly


def temperature(r_ohm: float, r0: float = 100.0) -> float:
    """Temperature in degC for RTD resistance *r_ohm* (inverse curve).

    Above 0 degC the quadratic inverts exactly:
        t = (-A + sqrt(A**2 - 4*B*(1 - R/R0))) / (2*B)
    Below 0 degC the quartic is inverted by bisection (the curve is strictly
    monotone), to 1e-9 degC.
    """
    r = _check_num(r_ohm, "r_ohm")
    r0v = _check_r0(r0)
    r_min = resistance(_T_MIN, r0v)
    r_max = resistance(_T_MAX, r0v)
    if not r_min <= r <= r_max:
        raise Pt100Error(
            f"resistance must be in [{r_min:.4f}, {r_max:.4f}] ohm for "
            f"r0={r0v} (the -200..850 degC span), got {r_ohm!r}")
    if r >= r0v:  # t >= 0: exact quadratic solution
        ratio = r / r0v
        disc = A * A - 4.0 * B * (1.0 - ratio)
        return (-A + disc ** 0.5) / (2.0 * B)
    lo, hi = _T_MIN, 0.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if resistance(mid, r0v) < r:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    return (lo + hi) / 2.0
