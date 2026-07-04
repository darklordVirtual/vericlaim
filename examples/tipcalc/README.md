# tipcalc — a correctness claim

A tip calculator. The claim is about **correctness**: all reference bills
produce the expected total.

- **Code:** `src/tipcalc.py` — total including a percentage tip, to the cent.
- **Cases:** `cases.py` — 12 hand-verified `(bill, tip%, expected)` rows, the
  shared source of truth for the evidence and the test.
- **Evidence:** `evidence.py` writes `artifacts/tipcalc.json` (how many pass).
- **Claim:** `CLAIM-TIP-001` in the [register](../../claims/register.yaml).
- **Doc:** [`docs/results.md`](docs/results.md), bound with a claim anchor.

Try it: break the rounding in `total_with_tip`, rerun the evidence, run
`vericlaim` — `cases_passing` drops and the gate fails until the docs stop
claiming all 12 pass.
