# EWMA + control-chart limits (Roberts / NIST)

*Subject area: Observability / Statistical Process Control. Language: python. Vendorable bundle `90e90a5cf636`.*

The EWMA z_i = lambda*x_i + (1-lambda)*z_{i-1} weights recent observations geometrically and is both the standard smoother behind latency/utilization dashboards and Roberts' control chart for detecting small process shifts, with limits that widen as sqrt(lambda/(2-lambda)*(1-(1-lambda)^(2i))) toward steady state. This module implements the recursion and the chart limits; the claim proves exact-rational agreement and the published NIST example, so you inherit checked smoothing math for monitoring pipelines.

## Claim

<!-- claim:CLAIM-LIB-EWMA-001 checks_matched -->
The vendored EWMA library passes all 150 checks with 0 mismatches: the float recursion matches exact rational (Fraction) recomputation to 12 decimal places on all 76 points, the control-limit width factors match on all 50, and it reproduces the NIST/SEMATECH e-Handbook's published worked example -- all 21 EWMA values of the 20-point dataset (lambda 0.3, target 50) and the published steady-state control limits. Verified value: <!-- v:CLAIM-LIB-EWMA-001.checks_matched -->**150**
(`checks_matched`), backed by [`modules/ewma/artifacts/ewma.json`](../modules/ewma/artifacts/ewma.json).

## Vendor it

Ships `ewma.py` into your project, byte-exact, with a generated binding test that
fails the moment you edit the vendored code:

```bash
python3 integrations/library/use_code.py --bundle claimlib/bundles/90e90a5cf6360f766d67cc0308c983791795bc170def3059116a2294ad3478bf --target .
```

## References

The standards this module implements, as hash-locked entries in [the claimlib bibliography](../literature/BIBLIOGRAPHY.md):

- **Technometrics, vol. 1, no. 3, pp. 239-250; doi:10.1080/00401706.1959.10489860** — Control Chart Tests Based on Geometric Moving Averages. [https://doi.org/10.1080/00401706.1959.10489860](https://doi.org/10.1080/00401706.1959.10489860)
- **doi:10.18434/M32189, section 6.3.2.4 (EWMA Control Charts)** — NIST/SEMATECH e-Handbook of Statistical Methods. [https://www.itl.nist.gov/div898/handbook/](https://www.itl.nist.gov/div898/handbook/)
