# seed/ — deterministic stress-test corpora for the gate

Two isolated VeriClaim workspaces that prove the gate holds up at scale and at
breadth. Every number in every claim is **computed** by the generator (never
typed by hand), every artifact carries a provenance sidecar, and regeneration
is byte-identical on every machine, forever — the corpora are therefore *not*
committed; they are rebuilt on demand:

```bash
python seed/generate.py                 # 300 claims (use --n 500 for more)
python -m vericlaim --root seed         # gate: green, 300 claims

python seed/enterprise/generate.py      # 30 claims across 16 enterprise domains
python -m vericlaim --root seed/enterprise
```

## seed/ — scale (one discipline × N documents)

`generate.py` derives a synthetic corpus from `sha256(seed || index)`: each
"document" gets real, measured properties — byte length, run-length compression
ratio, distinct byte count, lossless round-trip — bound through the register and
a doc anchor exactly as the discipline requires. Each claim also cites a
hash-locked synthetic literature work (`literature/work_XXXX.txt`), exercising
the literature-integrity check at scale. This answers: *does the gate stay
fast, exact, and fail-closed with hundreds of claims and citations?*

## seed/enterprise/ — breadth (16 disciplines × real methods)

`enterprise/generate.py` + `enterprise/domains.py` model real enterprise
disciplines — CVSS v3.1 scoring, control coverage, risk registers, IAM/SoD,
SLO arithmetic, FinOps, supply chain, DORA metrics, incident response,
continuity, privacy, ML governance, data quality, vendor risk, audit-trail
hash chains, workforce analytics — each computing genuine deterministic metrics
over fixed embedded fixtures. This answers: *can one register speak precisely
about many domains at once?* All fixtures are synthetic; the metrics grade the
**method**, not any live estimate — stated in every claim's caveat.

## Relationship to claimlib

`claimlib/` is the opposite trade: few, **real**, vendorable modules whose
claims cite real, hash-locked literature (`claimlib/literature/`). The seed
corpora are synthetic by design and say so in every statement and caveat —
what they share with claimlib is the contract: no claim without an artifact,
no artifact without provenance, no doc number unbound from the register.
