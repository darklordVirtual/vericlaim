# Sources for CLAIM-011 — time-uniform (anytime-valid) confidence sequence

Curated literature extract for the library bundle of REMORA-research
CLAIM-011. Hash-locked at harvest; our own summary of the cited literature.

Fixed-N Wilson intervals are not valid under continuous monitoring with
optional stopping; the claim therefore reports a time-uniform confidence
sequence for the REM-020 cycle-level false-accept indicator (0/168 cycles →
95% time-uniform upper bound 4.72%). The construction follows the
confidence-sequence literature cited by the source paper:

- Ville, J. (1939). *Étude critique de la notion de collectif.* (Ville's
  inequality — the martingale foundation.)
- Darling, D. A., & Robbins, H. (1967). *Confidence sequences for mean,
  variance, and median.* PNAS 58(1).
- Howard, S. R., Ramdas, A., McAuliffe, J., & Sekhon, J. (2021). *Time-uniform,
  nonparametric, nonasymptotic confidence sequences.* Annals of Statistics
  49(2).
- Ramdas, A., Grünwald, P., Vovk, V., & Shafer, G. (2023). *Game-theoretic
  statistics and safe anytime-valid inference.* Statistical Science 38(4).

The bundled code extract is the source repo's implementation that produced
`results/far_confidence_sequence_v1.json`.
