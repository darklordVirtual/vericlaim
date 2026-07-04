# SPDX-License-Identifier: Apache-2.0
"""`vericlaim init` — scaffold Claim-Oriented Programming into a project.

Creates the three files a project needs to start (config, register, baseline)
without overwriting anything that already exists. After this, a project has a
green gate and a place to add its first claim.
"""
from __future__ import annotations

from pathlib import Path

_CONFIG = """\
# vericlaim gate configuration. Docs: https://github.com/darklordVirtual/vericlaim
[vericlaim]
register        = "claims/register.yaml"
baseline        = "claims/baseline.json"
# manifest      = "claims/manifest.md"      # optional SHA-256 manifest of artifacts
doc_globs       = ["README.md", "docs/*.md"]
# code_globs    = ["src/**/*.py"]            # bind code comments too: `# claim:ID field`
required_fields = ["id", "statement", "evidence_level", "artifact", "caveat"]
# Weakest -> strongest. Tailor to your domain.
evidence_levels = ["theoretical", "measured", "benchmarked", "reproduced", "machine_checked", "externally_validated"]
# require_provenance  = true   # every produced artifact must record how it was made
# require_git_tracked = true   # every artifact must be committed to git

# Strings you have corrected and never want to see again (drift guard).
[vericlaim.stale_strings]
# "old wording" = "why it is stale / use instead"
"""

_REGISTER = """\
---
# Your single source of truth for every claim this project makes about itself.
# Add a claim when a doc states a number or a capability. Update numbers HERE
# first; the gate then flags every doc paragraph that still shows the old value.
#
# Required per claim: id, statement, evidence_level, artifact, caveat.
# Optional: n, metrics (numbers docs bind to via <!-- claim:ID metric --> anchors).

schema_version: "1"

claims: []
# Example (delete the `[]` above and uncomment):
#
#  - id: CLAIM-CORE-001
#    statement: >
#      One-line description of what is claimed.
#    evidence_level: measured
#    artifact:
#      - results/example.json      # a committed file that establishes it
#    metrics:
#      value: 42                    # a number your docs can bind to
#    caveat: >
#      The scope and limitation — this is part of the claim.
#    reproduce: "python bench/example.py"
"""

_BASELINE = """\
{
  "schema": "vericlaim_baseline_v1",
  "description": "Known gate violations grandfathered during adoption. Each is reported as WARN and does not fail the gate. Remove entries as you fix them.",
  "known_violations": []
}
"""

FILES = {
    "vericlaim.toml": _CONFIG,
    "claims/register.yaml": _REGISTER,
    "claims/baseline.json": _BASELINE,
}


def init(root: Path) -> int:
    """Create the scaffold under *root*. Never overwrites existing files."""
    created, skipped = [], []
    for rel, content in FILES.items():
        p = root / rel
        if p.exists():
            skipped.append(rel)
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        created.append(rel)

    for rel in created:
        print(f"  created  {rel}")
    for rel in skipped:
        print(f"  skipped  {rel} (already exists)")
    print()
    print("Claim-Oriented Programming is set up. Next:")
    print("  1. Add your first claim to claims/register.yaml")
    print("  2. Bind a doc number with an anchor:  <!-- claim:CLAIM-CORE-001 value -->")
    print("  3. Run the gate:  vericlaim")
    print("  4. Add .github/workflows/claim-gate.yml to enforce it in CI")
    print()
    print("Guide: https://github.com/darklordVirtual/vericlaim#quickstart")
    return 0
