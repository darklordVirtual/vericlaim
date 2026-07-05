# Presentasjonsmateriell

Redigerbare kilder for VeriClaim-presentasjonen, foredragsmanuset og
whitepaperet. Alt er selvforsynt — ingen byggesteg, ingen eksterne
avhengigheter.

| Fil | Hva | Rediger slik |
|-----|-----|--------------|
| `vericlaim-deck.html` | 26-sliders presentasjon (mørk, piltast-navigasjon) | Åpne i nettleser for forhåndsvisning; rediger HTML direkte — hver slide er en `<section class="slide">`, all CSS ligger øverst i filen. Illustrasjonene er inline SVG. |
| `vericlaim-manus.html` / `.md` | Foredragsmanus (~25 min) med talt tekst, regi og Q&A | Rediger `.md`-versjonen for tekstarbeid; `.html` er den formaterte utgaven. |
| `vericlaim-whitepaper.html` / `.md` | Whitepaper med executive summary, funn F1–F5 og nøkkeltall | Samme mønster: `.md` for tekst, `.html` for det delbare uttrykket. |
| `library-catalog.md` | Katalog over claims-biblioteket — unike oppføringer, gruppert per kilde | GENERERES: `python3 integrations/library/catalog.py --url <worker> --out presentation/library-catalog.md` — håndrediger aldri. |

**Forhåndsvisning:** åpne HTML-filene rett i nettleser (`open presentation/vericlaim-deck.html`).
**PDF:** nettleserens print-dialog — filene er print-tilpasset.

## Om tallene i materiellet

Disse filene ligger utenfor gatens `doc_globs` og er derfor IKKE
anker-bundet — de er presentasjonsmateriell, ikke claim-bærende docs.
Alle tall er hentet fra registrerte claims per 2026-07-05; whitepaperets
§11 angir kilde-claim per tall (vericlaim, claimlib-seeds,
trustgate-demo, samt `/library/summary` live). Oppdaterer du et tall her,
sjekk kilden først — aldri omvendt.
