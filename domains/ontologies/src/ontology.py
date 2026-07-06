# SPDX-License-Identifier: Apache-2.0
"""A domain ontology for claims, and a validator that a register conforms.

The knowledge domain is *ontology*: an evidence assurance system needs a shared,
machine-readable vocabulary — what evidence levels exist and in what order, and
what KINDS of claim there are (a capability count is not a benchmark is not a
machine-checked theorem). This module defines that ontology and validates a
register against it: every claim's level must be known, and every claim must
classify into exactly one claim type by an explicit rule.

The taxonomy is a PROPOSAL, not a standard; conformance is checked over a
committed fixture. It shows the shape of ontology-driven validation, not that
this particular vocabulary is canonical.
"""
from __future__ import annotations

# Ordered weakest -> strongest; mirrors vericlaim's own evidence ladder.
EVIDENCE_LEVELS: tuple[str, ...] = (
    "theoretical", "measured", "benchmarked", "reproduced",
    "machine_checked", "externally_validated",
)

# Claim types, each with the rule that classifies a claim into it. Order matters:
# the first matching rule wins, so the vocabulary is a total function on claims.
CLAIM_TYPES: tuple[str, ...] = (
    "theorem",      # machine_checked level
    "correctness",  # a pass/fail count (cases_total / cases_passing)
    "capability",   # a count of supported things (n_* with no ratio)
    "benchmark",    # a measured ratio/score
    "roadmap",      # theoretical level, no artifact numbers
)


def classify(claim: dict) -> str | None:
    """Return the claim type, or None if no rule matches (non-conforming)."""
    level = claim.get("evidence_level")
    metrics = claim.get("metrics") or {}
    if level == "machine_checked":
        return "theorem"
    if any(k in metrics for k in ("cases_total", "cases_passing", "n_roundtrip_lossless")):
        return "correctness"
    if level == "theoretical":
        return "roadmap"
    if any("ratio" in k or k.endswith("_f1") or k.endswith("_accuracy")
           or k == "savings_ratio" for k in metrics):
        return "benchmark"
    if any(k.startswith("n_") or k.startswith("canon_") or k.startswith("chunks_")
           or k.endswith("_dependencies") for k in metrics):
        return "capability"
    return None


def validate(claims: list[dict]) -> dict[str, int]:
    """Check every claim: level in the ontology, and a claim type assigned."""
    nonconforming = 0
    for c in claims:
        level_ok = c.get("evidence_level") in EVIDENCE_LEVELS
        typed = classify(c) is not None
        if not (level_ok and typed):
            nonconforming += 1
    return {
        "n_levels": len(EVIDENCE_LEVELS),
        "n_claim_types": len(CLAIM_TYPES),
        "n_claims_checked": len(claims),
        "nonconforming": nonconforming,
    }
