**Whitepaper · Remora Research · Juli 2026**

# VeriClaim: et **evidence-first** utviklingsparadigme

Dokumentasjon, kode, litteratur og reproduksjon — kryptografisk bundet sammen og håndhevet i CI. Med et tverrprosjekt-bibliotek der verifisert kunnskap komponderer, og en casestudie som komponerer garantier fra uavhengige kilder.

---

## Executive summary

AI skriver kode og prosa raskere enn noen verifiserer den. Resultatet er en ny klasse systemfeil: prosjekter som **beskriver seg selv feil** — tall som drifter fra målingene, sitater som aldri fantes, dokumentasjon som var sann i fjor. Testing fanger kode som oppfører seg feil; ingenting konvensjonelt fanger dette.

VeriClaim løfter Design by Contract fra funksjoner til hele repositoriet: hver faktapåstand registreres som en **claim** med committet evidens, ærlig gradert bevisstyrke og obligatorisk forbehold. En fail-closed gate håndhever kontrakten på hver commit; `reproduce` beviser at tallene fortsatt stemmer i dag; ledgere forankres i offentlig git-historikk. Oppå kjernen: et bibliotek av immutable, hash-adresserte kunnskapsbundles — inkludert 20 teoremer bevist av Lean 4-kjernen fra modell-seedede forslag — og TrustGate, et kjørende system komponert av garantier fra to uavhengige kilder.

- **90** gjeldende claims · 4 repoer
- **455** immutable bundle-versjoner
- **20** Lean-kjerneverifiserte teoremer
- **16** offentlige vitner — alle intakte
- **3** egne overclaims fanget av systemet
## 1. Problemet: prosjekter som misdescriber seg selv

En LLM i utviklingsløpet produserer tre artefakter samtidig: kode, tall og prosa. Kun den første har et modent kontrollapparat. Tallene og prosaen — README-er, benchmarks, changelogs, siteringer — lever uten kontrakt, og drifter i stillhet. Vår erfaring fra REMORA-arbeidet var entydig: selv med disiplinerte prosesser gjenoppstår korrigerte formuleringer, benchmarks-tall overlever koden de målte, og plausible referanser viser seg å være fabrikkerte. Problemet er strukturelt, ikke moralsk: **det finnes ingen håndhevet binding mellom påstand og bevis.**

## 2. Paradigmet: én regel

> ## Ingen tall uten artefakt. Ingen dokumenttall som ikke er bundet til registeret. Ingen claim beskrevet over evidensen den har. **Og alt håndheves — fail closed.**

En claim er en kontrakt med seks elementer: **statement** (påstanden), **evidence_level** (ærlig gradert styrke), **artifact** (committede bevisfiler), **metrics** (tallene dokumenter binder seg til), **caveat** (forbeholdet — en del av claimen, aldri valgfritt) og **reproduce** (kommandoen som gjenskaper beviset). Evidensstigen har seks trinn — theoretical, measured, benchmarked, reproduced, machine_checked, externally_validated — med én asymmetri som bærer ærligheten: degradering er alltid lov; oppgradering krever ny evidens.

## 3. Gaten: ni sjekker, hver commit

 | Sjekk | Garanti |
|---|---|
 | Registerintegritet | Fail-closed parsing — en formatfeil kan aldri stille avskru gaten |
 | Artefakt-eksistens | Ingen claim uten committet bevis; stier kan ikke rømme repoet |
 | Proveniens | Hvert produserte artefakt vet hvilket skript som lagde det |
 | Manifest-hasher | Et stille redigert resultat oppdages byte for byte |
 | Dokument-ankre | Prosatall bundet til registerverdier |
 | Kode-ankre | Kodekommentarer holdes til samme kontrakt som prosa |
 | Value-tokens | Pinner ett spesifikt tall-literal — «target 180 / actual 900» kan ikke passere |
 | Evidensnivå-sitering | Docs kan aldri omtale en claim over dens earned nivå |
 | Litteraturintegritet | Hver sitering hash-låst til et committet ekstrakt |

> **[Figur: Dokument ankret med kjetting til hashet evidens]**

***Figur 1.** Ankermodellen: dokumentet skriver ikke tallet — det henger i det, via anker og value-token, ned til den hashede evidensfilen. Ryker ett ledd, feiler bygget med eksakt fil og linje.*

## 4. Kryptografisk forankring: tamper-evidens mot alle — inkludert eieren

Alle hendelser — claims og bibliotekbundles — appendes i hash-kjedede ledgere: `Hi = SHA-256(Hi−1 ‖ Recordi)`. Én endret rad brekker hvert etterfølgende ledd. Men en kjede alene beskytter ikke mot den som eier databasen: hele kjeden kan bygges om og selv-verifisere. Derfor **vitnes** kjedehodene i offentlig git-historikk, og verifikasjon skjer klient-side: hele eksporten lastes ned, hver hash regnes om lokalt, og dagens kjeder må *forlenge* hvert tidligere vitne. En ombygd, redigert eller trunkert historikk avsløres av ethvert eldre vitne.

> **[Figur: Fem kjedede blokker der en endret blokk brekker alle etterfølgende ledd]**

***Figur 2.** Tamper-evidens i to lag: kjeden fanger redigering, de offentlige vitnene fanger ombygging. Status: 16 vitner, alle forlenget, null omskrivinger.*

## 5. Biblioteket: kunnskap som komponderer

Verifisert kunnskap pakkes i **bundles** — claim + evidens + genererende kode + litteratur — adressert av `bundle_id = SHA-256(kanonisk manifest)`. Immutabelt: enhver endring er en ny versjon; supersession *utledes* av det append-only registeret, så søk viser gjeldende versjoner mens hele historikken består. Tre tillitsprinsipper:

**1) Tillit avgjøres av hva kilden er.** Native repoer må ha grønn egen gate ved høsting; kartlagte repoer høstes under nedskrevet policy der evidensnivåer aldri oppgraderes; alt annet karantenesettes som *kandidater* — synlige, merkede, umulige å importere som claims. **2) Biblioteket er distribusjon, aldri sannhet.** Import verifiserer hver hash offline, og vendret innhold hash-låses gjennom mottakerprosjektets egen gate. **3) Koden du kjører er koden som lagde beviset.** Byte-eksakt vendoring med generert bindingstest gjør forking til et eksplisitt, synlig valg.

## 6. Automatisert litteraturkuratering — og missiteringsfangstene

Bibliografisk metadata hentes utelukkende fra registrarer (Crossref, arXiv) ved oppslagstid — aldri fra modellhukommelse. Et frø (tittel eller DOI) må passere tre vakter samtidig: **tittel-overlapp, forfatteretternavn og årstall (±2)**. Vaktene er ikke teoretiske — de herdet seg selv i drift:

 | Frøet søkte | Registraren returnerte | Utfall |
|---|---|---|
 | Attention Is All You Need (2017) | «Is Attention All You Need?» — kritikk, 2025 | Avvist på forfatter+år → korrekt arXiv-post funnet |
 | On Calibration of Modern Neural Networks | Sensor-kalibrerings-paper, 1989 | Avvist etter vaktherding; regresjonstest skrevet |
 | Gödel, Escher, Bach (1979) | Bokanmeldelse i tidsskrift, 1983 | Avvist på forfatter; ekte bokpost verifiserte senere |
| 8 bok-frø (bl.a. CLRS, Vovk) | Ingen post besto alle tre vaktene | **Døde ærlig** — ingen sitering fremfor feil sitering |

Fravær dokumenteres like høyt som nærvær: claims hvis standardreferanse ikke verifiserte, sier det eksplisitt i caveaten.

## 7. Modell-seedet kunnskap: Fable foreslår, maskinen dømmer

Kan en LLM fylle et kunnskapsbibliotek uten å forgifte det? Ja — hvis modellen aldri er autoritet. **Seeding-kontrakten:** modellforslag er frø; en uavhengig verifikator avgjør; det som feiler, blir aldri en claim. I praksis fire dommere: uttømmende decision procedures (12 tautologier), en fail-closed Hilbert-checker (7-stegs derivasjon), eksakt aritmetikk (25 bounded teorembatterier — fra Bayes-identiteten over 455 eksakte fordelinger til Max-Flow=Min-Cut over alle 4096 småneettverk), og **Lean 4-kjernen**: 20 teoremer bevist universelt — for alle proposisjoner, typer og naturlige tall — med **aksiom-fotavtrykk** registrert per bevis (10 fullt konstruktive). Kjernen avviste underveis et Lean-3-idiom fra modellens hukommelse; avvisningen står i historikken som kontraktens bevis.

## 8. Casestudie: TrustGate

TrustGate er første system **komponert** av verifiserte claims fra uavhengige kilder — uten å oppgradere ett evidensnivå. Konform prediksjon (fra teorembiblioteket; dekningsidentiteten maskinsjekket eksakt) bygger intervaller per svar; REMORAs anytime-valide confidence sequence (CLAIM-011) overvåker miscoverage kontinuerlig. Fordi grensen er tidsuniform, er sertifisering på et *datadrevet* tidspunkt matematisk gyldig — nøyaktig bruken som ugyldiggjør klassiske fixed-N-intervaller.

> **[Figur: Monitorkurve som faller under sertifiseringsterskelen ved runde 94]**

***Figur 3.** TrustGate-kjøringen: 400 runder, dekning 373/400 mot 0,90-mål, sertifisert i runde 94, null alarmer — og det importerte REMORA-artefaktet reproduserte eksakt under den vendrede koden.*

## 9. Funn

- **F1 — Systemet disiplinerer sin egen skaper.** Tre overclaims fra modellen som bygde systemet ble fanget av systemets egne mekanismer: en bundle-caveat som lovet kode bundelen ikke bar (fanget av demo-byggingen; fikset ved å gjøre påstanden sann), en foreldet «referansen er fraværende»-caveat (fanget etter re-kuratering), og et lint-hull i verifiseringsritualet. Håndhevelse er ikke aspirasjon.
- **F2 — Tittel-match alene er utilstrekkelig for sitatintegritet.** Tre plausible feiltreff passerte tittelvakten i drift; forfatter+år-vaktene er nødvendige, og «ingen sitering» må være et førsteklasses, dokumentert utfall.
- **F3 — Modell-seeding er trygg under maskinell dom.** 100+ modellforeslåtte matematiske utsagn ble claims kun via uavhengig verifisering; forslagene som feilet (Lean-3-idiom, feil truth-tabell-konvensjon, feilhusket tillukningsstørrelse) ble avvist av sjekkerne — to av dem korrigerte skaperens forventning, ikke omvendt.
- **F4 — Garantier komponerer på tvers av prosjekter uten tillits-inflasjon.** TrustGate kombinerte claims fra to kilder med bevart proveniens og uendrede evidensnivåer — og komposisjonens matematikk (tidsuniformitet) formet gate-semantikken: sertifisér under terskel, ikke alarm over.
- **F5 — Utledet versjonering bevarer både renhet og historie.** Supersession beregnet fra append-only-registeret ga eksakt regnskap (81, senere 90 gjeldende identiteter) uten skjemaendring — hash-kjeder og eldre vitner forble gyldige.
## 10. Begrensninger — presist

### VeriClaim beviser

- Intern konsistens register ↔ evidens ↔ docs
- Reproduksjon — tallet holder i dag
- Proveniens — hvor hvert tall kom fra
- Dokument- og kodeintegritet
- Sitatintegritet — hash-låst litteratur
- Historikk-integritet — vitnet, klient-verifisert
### VeriClaim beviser ikke

- At en benchmark representerer produksjon
- At en algoritme er optimal
- At en modell har rett
- At prosa er semantisk sann
- At evidens ikke ble manipulert *før* første commit
Grensen er en del av produktet: den står i README-en, i Claude-skillen og i hver caveat. Et anti-overclaim-verktøy som overclaimer seg selv, er verdiløst.

## 11. Verifiserte nøkkeltall

 | Tall | Hva | Kilde |
|---|---|---|
 `/library/summary`| 90 / 455 | Gjeldende claims / immutable versjoner, 4 kilderepoer | , live |
 | 20 (10) | Lean-kjerneverifiserte teoremer (fullt konstruktive) | THM-LEAN-001..003, claimlib-seeds |
 | 880 | Eksakte konform-garantisjekker (identitet, ties, p-verdi) | THM-CONF-001..003 |
 | 373/400 · 94 | TrustGate-dekning · sertifiseringsrunde | DEMO-001/002, trustgate-demo |
 `claims/witness.jsonl`| 16 | Offentlige ledger-vitner, alle forlenget klient-side | , vericlaim |
 | 131 | Tester i vericlaim-kjernen (TDD, alle grønne ved release) | vericlaim v0.3.0 |

## 12. Utvalgte referanser (alle registrar-verifiserte i biblioteket)

- Howard, Ramdas, McAuliffe & Sekhon (2021). Time-uniform, nonparametric, nonasymptotic confidence sequences. *Annals of Statistics*. doi:10.1214/20-aos1991
- Angelopoulos & Bates (2021). A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification. arXiv:2107.07511
- Andriushchenko et al. (2024). AgentHarm. arXiv:2410.09024 · Geifman & El-Yaniv (2017). arXiv:1705.08500 · Guo et al. (2017). arXiv:1706.04599
- Gödel (1931). Über formal unentscheidbare Sätze… doi:10.1007/bf01700692 · Rice (1953). doi:10.1090/s0002-9947-1953-0053041-6
- Shannon (1948). A Mathematical Theory of Communication. doi:10.1002/j.1538-7305.1948.tb00917.x · Ford & Fulkerson (1956). doi:10.4153/cjm-1956-045-5
- de Moura & Ullrich (2021). The Lean 4 Theorem Prover and Programming Language. doi:10.1007/978-3-030-79876-5_37
- Wolpert (1996). doi:10.1162/neco.1996.8.7.1341 · Vapnik & Chervonenkis (1971). doi:10.1137/1116025 · Johnson & Lindenstrauss (1984). doi:10.1090/conm/026/737400
- Lipman et al. (2022). Flow Matching. arXiv:2210.02747 · Bronstein et al. (2021). Geometric Deep Learning. arXiv:2104.13478 · Carlsson (2009). Topology and Data. doi:10.1090/s0273-0979-09-01249-x
## 13. Etterprøvbarhet

Alt i dette dokumentet er offentlig og re-verifiserbart: `github.com/darklordVirtual/vericlaim` (rammeverket, v0.3.0, Apache-2.0), `…/claimlib-seeds` (den seedede kunnskapen), `…/trustgate-demo` (casestudien), og truth-layeret live på `vericlaim-claims.razorsharp.workers.dev/passport`. Kjør `vericlaim && vericlaim reproduce` i hvert repo — det er hele poenget.

 VeriClaim og Claim-Oriented Programming: Stian Skogbrott, Remora Research · 2026 · Hvert tall i dette dokumentet er en registrert claim med committet artefakt; tabellen i §11 angir kilden per tall.
