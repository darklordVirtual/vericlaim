# Known issues — claims library / research layer

Tracked defects in the literature catalog and served research index. Listed here
rather than silently, per the project's honesty discipline.

## 1. The catalog's 180 ≠ the canon's 180 (different sets, equal count)

`CLAIM-LIB-RAG-001` counts **180 canon works** (the coverage contract in
`research/canon.toml`: verified works + documented drops). `CLAIM-LIB-RAG-002`
counts **180 catalog works** that are chunked and pushed to the live index.
These happen to be the same number but are **not the same set**: the canon's
documented drops are absent from the catalog, and the catalog instead contains
works harvested from external bibliographies (notably REMORA's) that were never
run through the canonical coverage guard.

Both claims' numbers are literally true and reproduce; the risk is that the equal
count reads as "the vetted corpus is exactly what is served," which is not the
case. The caveat on `CLAIM-LIB-RAG-002` now states this explicitly.

## 2. A registrar false-match is in the served index

`doi:10.1109/ijcnn.1989.118324` — "Sensor calibration using artificial neural
networks" (1989) — is the exact false-match that `biblio_curate.py` /
`litcoverage.py` are designed to catch and reject, yet it is present in the
committed catalog (`literature/works/doi_10-1109_ijcnn-1989-118324.json` and its
chunks) and therefore in the live index. It should be dropped.

## 3. Unvetted recent-arXiv works outside the canon

Several catalog works are future-dated arXiv entries harvested from external
bibliographies and never vetted by the canonical map, e.g. `arxiv:2603.07191`,
`2604.09529`, `2606.07822`, `2606.08539`. Their text is hash-locked and
retrieval-only (never evidence), but they are outside the coverage contract.

## Fix plan (requires the live pipeline)

Removing entries changes `chunks_total`/`chunks_pushed` and the
`research_layer.json` artifact, and must re-run the acquisition → chunk → push →
witness pipeline against the deployed Worker (network + `INDEX_TOKEN`). It cannot
be done as an offline edit without diverging the catalog from the live index.
The intended remediation:

1. Drop item 2 (and review item 3) from the catalog and record them in
   `research/drops.toml` with reasons.
2. Re-run `integrations/library/evidence_research_layer.py` and update the
   `CLAIM-LIB-RAG-001/002` metrics from the regenerated artifact.
3. Re-push and re-witness so the live index matches the catalog.

Until then, treat the served research index as "retrieval aid, hash-locked, not
a vetted corpus" — which is what the `CLAIM-LIB-RAG-*` caveats already say.
