# The AI-assurance literature catalogue

**Purpose.** The curated reading map behind the knowledge register's AI
areas: which works this project draws on, section by section, and which of
them are additionally *deep-seeded* as cited, hash-locked entries in
[claimlib's literature layer](../../claimlib/literature/BIBLIOGRAPHY.md).

**The data.** One CSV, committed and claim-bound:
[`ai_assurance_literature_catalog_2026-07-14_enriched.csv`](ai_assurance_literature_catalog_2026-07-14_enriched.csv)
— columns: `id`, `section`, `title`, `authors`, `year`, `type`, `source`,
`priority`, `tags`, `pdf_url`, `landing_url`, `url_status`,
`catalog_status`, `notes`.

<!-- claim:CLAIM-CATALOG-001 works_total sections p0_count deep_seeded_in_claimlib -->
The catalogue holds <!-- v:CLAIM-CATALOG-001.works_total -->**231** works in
<!-- v:CLAIM-CATALOG-001.sections -->**10** sections, of which
<!-- v:CLAIM-CATALOG-001.p0_count -->**154** are marked priority p0 and
<!-- v:CLAIM-CATALOG-001.deep_seeded_in_claimlib -->**18** are deep-seeded
as cited works in claimlib (same-work aliases only — a lineage relation is
never an alias). Every row is mechanically validated by
[`tools/ai_catalog_evidence.py`](../../tools/ai_catalog_evidence.py); edit
the CSV without regenerating the evidence and the gate fails.

## Sections

| # | Theme | Feeds (examples) |
|---|-------|------------------|
| 1 | Uncertainty quantification & conformal prediction | `conformal_split`, `selective_risk`, `calibration_ece` |
| 2 | LLMs, agents & interpretability | context for the AI areas; MCP/A2A specs |
| 3 | Benchmarks & capability measurement | evaluation vocabulary (HELM, SWE-bench, AgentDojo, …) |
| 4 | Attacks, defenses & agent security | `tool_guard`, `owasp_llm10` |
| 5 | Governance, standards & policy | `eu_ai_act`, `nist_ai_rmf`, `iso_42001`, `model_card` |
| 6 | Engineering practice & ML systems | SRE/MLOps context (`slo_burnrate`, `ewma`) |
| 7 | Supply chain, provenance & attestation | `slsa_levels`; PROV-DM / in-toto / C2PA candidates |
| 8 | Formal methods & verified AI | future `theorem`-style modules |
| 9 | Privacy & fairness | `fairness_metrics`, `dp_composition`, `gdpr` |
| 10 | Runtime governance & assurance cases | `gsn_case`, `zta_tenets`; MI9/AgentSpec candidates |

## Tiers of seeding — honest vocabulary

1. **Cataloged** (all 231): the work is in the committed CSV, its row
   validated, its counts claim-bound. Proves the map exists and parses —
   never that a work's content is true or its URL still resolves.
2. **Deep-seeded** (18): the same work is a cited, hash-locked entry in
   `claimlib/literature/` — summary integrity-locked, cited by modules whose
   evidence implements it. The alias table in the evidence script is
   explicit; a fuzzy or lineage match is not an alias.
3. **RAG-ingested** (separate): the live research corpus (180 works, 9 805
   chunks) served by the Cloudflare oracle is a differently-governed
   collection with its own claims (`CLAIM-LIB-RAG-*`) — the catalogue does
   not assert membership there.

## Working with the catalogue

```bash
python3 tools/ai_catalog_evidence.py    # revalidate + regenerate the artifact
python3 -m vericlaim                    # the gate binds this page's numbers
```

To promote a cataloged work to deep-seeded: author a claimlib module whose
evidence implements it, add the literature entry (web-verified), and — if
the catalogue id differs — extend the alias table in the evidence script.
