# SPDX-License-Identifier: Apache-2.0
"""Evidence for CLAIM-LIB-PT100-001 — the IEC 60751 curve reproduces the
published standard table points and inverts to micro-degC precision.

Oracles, none the module's own output: (1) published Pt100 standard-table
resistances (every IEC 60751 table prints them): 18.5201 ohm at -200 degC,
60.2558 at -100, 100.0000 at 0, 119.3971 at 50, 138.5055 at 100, 175.8560
at 200, 280.9775 at 500, 390.4811 at 850; (2) the same values recomputed
INDEPENDENTLY from the standard coefficients with the decimal module at
50-digit precision (the polynomial is exact arithmetic — transcription of
either the coefficients or the table would fail against the other); (3) the
inverse: |t - temperature(resistance(t))| < 1e-6 degC over a fixed 1-degC
sweep of the full -200..850 span. Deterministic: same artifact always.
"""
from __future__ import annotations

import sys
from decimal import Decimal, getcontext
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from pt100 import Pt100Error, resistance, temperature  # noqa: E402
from _util import emit  # noqa: E402

getcontext().prec = 50

DA = Decimal("3.9083e-3")
DB = Decimal("-5.775e-7")
DC = Decimal("-4.183e-12")

# (temperature degC, published standard-table resistance in ohm, printed dp)
TABLE = [
    (-200, "18.5201", 4),
    (-100, "60.2558", 4),
    (0, "100.0000", 4),
    (50, "119.3971", 4),
    (100, "138.5055", 4),
    (200, "175.8560", 4),
    (500, "280.9775", 4),
    (850, "390.4811", 4),
]


def decimal_resistance(t: int) -> Decimal:
    """Independent 50-digit evaluation of the Callendar–Van Dusen polynomial."""
    td = Decimal(t)
    poly = 1 + DA * td + DB * td * td
    if td < 0:
        poly += DC * (td - 100) * td ** 3
    return Decimal(100) * poly


def run() -> dict:
    rows = []
    table_ok = 0
    decimal_ok = 0
    for t, published, dp in TABLE:
        got = resistance(float(t))
        pub = float(published)
        ok = abs(got - pub) < 10 ** -dp / 2 + 1e-9
        table_ok += ok
        # the published table value must equal the independent 50-digit
        # polynomial, rounded to the printed precision
        dec = decimal_resistance(t)
        dec_ok = str(dec.quantize(Decimal(published))) == published
        decimal_ok += dec_ok
        rows.append({"t_c": t, "published_ohm": published,
                     "computed_ohm": round(got, 6), "table_ok": bool(ok),
                     "decimal_ok": bool(dec_ok)})

    sweep_points = 0
    roundtrip_ok = 0
    worst = 0.0
    t = -200.0
    while t <= 850.0:
        sweep_points += 1
        back = temperature(resistance(t))
        err = abs(back - t)
        worst = max(worst, err)
        if err < 1e-6:
            roundtrip_ok += 1
        t += 1.0

    # r0 scaling: a Pt1000 is exactly 10x a Pt100 everywhere.
    scale_ok = int(all(
        abs(resistance(t, 1000.0) - 10.0 * resistance(t)) < 1e-9
        for t in (-200.0, -37.5, 0.0, 68.2, 850.0)))

    rejects = 0
    for bad in (lambda: resistance(-201.0), lambda: resistance(851.0),
                lambda: resistance(float("nan")),
                lambda: temperature(18.0), lambda: temperature(391.0),
                lambda: resistance(0.0, 0.0), lambda: resistance(0.0, -1.0)):
        try:
            bad()
        except Pt100Error:
            rejects += 1

    total = 2 * len(TABLE) + 1 + 1
    matched = table_ok + decimal_ok + int(roundtrip_ok == sweep_points) \
        + scale_ok
    return {
        "schema": "claimlib_evidence_v1",
        "module": "pt100",
        "checks": total,
        "checks_matched": matched,
        "mismatches": total - matched,
        "table_points": len(TABLE),
        "table_ok": table_ok,
        "decimal_ok": decimal_ok,
        "sweep_points": sweep_points,
        "roundtrip_ok": roundtrip_ok,
        "worst_roundtrip_degc": float(f"{worst:.2e}"),
        "scale_ok": scale_ok,
        "reject_cases": 7,
        "rejects_ok": rejects,
        "table_detail": rows,
    }


def main() -> int:
    obj = run()
    emit(HERE / "artifacts" / "pt100.json", obj,
         script="python3 claimlib/modules/pt100/evidence.py")
    # claim:CLAIM-LIB-PT100-001 checks_matched
    # All 18 checks pass: 8 published table points matched, the same 8
    # re-derived exactly from the standard coefficients at 50-digit
    # precision, a 1051-point full-span round-trip under 1e-6 degC, and
    # exact Pt1000 scaling — checks_matched = 18, mismatches = 0.
    print(f"pt100: {obj['checks_matched']}/{obj['checks']} checks "
          f"(table {obj['table_ok']}/{obj['table_points']}, decimal "
          f"{obj['decimal_ok']}/{obj['table_points']}, roundtrip "
          f"{obj['roundtrip_ok']}/{obj['sweep_points']} worst "
          f"{obj['worst_roundtrip_degc']} degC); rejects "
          f"{obj['rejects_ok']}/{obj['reject_cases']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
