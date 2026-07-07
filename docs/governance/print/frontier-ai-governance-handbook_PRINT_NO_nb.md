![Framside](figures/no/cover-front.svg)

---
---

# Håndbok i styring av frontier-AI

### Evidensbundet styring for frontier-AI-systemer: trykkutgave

*Claim-Oriented Programming (påstandsorientert programmering) og VeriClaim av Stian Skogbrott.*

---

*En AI-agent skal til å handle i verden: lese en journal, sende en melding,
kjøre en kommando. Noen godkjente at den fikk lov. Så stiller en revisor det
eneste spørsmålet som betyr noe: «Hva visste du egentlig da du tillot det?» Er
svaret et policy-dokument som sier de riktige tingene, har du betryggelse. Er
svaret en påstand, bundet til evidens, på et oppgitt tillitsnivå, med grensene
skrevet ned, har du en sak. Denne boken handler om forskjellen, og om hvordan
man bygger styring som kan angripes og likevel står.*

---

## Forord: hva denne boken er, og ikke er

**Hvem den er for.** Tekniske styringsfagfolk, sikkerhets- og
enterprise-arkitekter, MLOps- og AI-plattformteam, og de regulatoriske
rådgiverne som jobber med dem. En leser som er komfortabel med
programvareleveranse vil føle seg hjemme; en leser som er ny til AI/ML får
kjernebegrepene forklart fra grunnen, selv om enkelte kapitler går i dybden.

**Hva den lover.** Én idé, grundig argumentert og demonstrert: at AI-styring
kan bygges som et system av *sjekkbare påstander* i stedet for en bunke
betryggende dokumenter, og at når den bygges slik, får en revisor en sterkere
posisjon, fordi påstandene kan angripes mekanisk og vises å holde.

**Hva den ikke lover.** Den er ikke juridisk rådgivning, ikke en sertifisering,
og ikke en garanti for at et bestemt system er trygt eller etterlevende. Den
oppgir, hele veien, grensen for hver påstand. Del VI («Ærlighet») finnes for å
si klart hva metoden *ikke* beviser. Husker du én ting, husk at boken bruker sin
egen disiplin på seg selv: hver sterk påstand her er en registrert påstand på et
oppgitt evidensnivå, ikke et slagord.

**Hvordan lese den.** De neste sidene er et forord på én side og en
begrepsnote. Les dem først. Deretter bygger Del I til III metoden og
kunnskapsbasen; Del IV til V setter den inn i enterprise-arkitektur og praksis; Del
VI oppgir grensene; Del VII til VIII dekker identitet/policy på tvers av skyer og
sikkerhetsdrift. Appendiksene er oppslagsstoff. Fem gjennomgående case-studier
bakerst viser metoden fra ende til ende; en travel leser kan begynne der.

---

## Les dette først: VeriClaim på én side

**Problemet.** Et styringsdokument kan si «overvåket for drift» enten noe
overvåker noe eller ikke. En leser kan ikke skille et samvittighetsfullt program
fra et kosmetisk, fordi begge leses likt. Selvtillit er ikke evidens.

**Ideen.** Behandle hver faktapåstand et system gjør om seg selv som en
**påstand** (en kontrakt mellom det som sies og evidens på disk), og nekt å
skrive en påstand du ikke kan stå inne for. Fem ord bærer metoden:

- **Påstand.** En énlinjes påstand med et oppgitt evidensnivå og et forbehold
  (dens omfang og begrensning).
- **Artefakt.** Den committede filen som etablerer påstanden: et
  benchmark-resultat, et bevisobjekt, en sjekkers utdata. Ingen tall uten en
  artefakt.
- **Register.** Listen over alle påstander. Den eneste sannhetskilden; når et
  dokument og registeret er uenige, vinner registeret.
- **Port.** En automatisk sjekk, kjørt ved hver endring, som feiler bygget hvis
  en påstand drifter fra artefakten sin, et dokument oppgir et tall registeret
  ikke støtter, eller en påstand beskrives over evidensnivået den har fortjent.
- **Fail-closed.** I tvil nekter porten. Et malformet register passerer ikke
  stille som «null påstander»; det stopper bygget. Sikkerhet er standarden.

**Hva den kjøper, presist.** Intern konsistens og reproduserbarhet: tallene er
til stede der de påstås, og reproduserer fortsatt i dag. **Hva den ikke kjøper:**
bevis for at et benchmark er realistisk, at evidens ikke ble manipulert før den
ble committet, eller at en setning prosa er sann. Porten beviser at *tallet* er
bundet til evidensen sin, ikke at fortellingen rundt er riktig. Å kjenne den
grensen er det som gjør metoden ærlig.

**Evidensstigen.** Påstander graderes, svakest til sterkest:

> theoretical  <  measured  <  benchmarked  <  reproduced  <  machine-checked  <  externally-validated

En påstand beskrives kun på nivået den har fortjent. Nedgradering er alltid
tillatt; oppgradering krever ny evidens. Denne stigen er bokens mest portable
idé: du kan ta den i bruk uten å ta i bruk noe annet.

---

## En note om terminologi

Denne boken vokste ut av et fungerende system, og den navngir delene sine. For å
holde hovedteksten lesbar, her er vokabularet én gang, enkelt:

- **VeriClaim.** Verktøyet som implementerer metoden: registerformatet, porten
  og reproduce-steget.
- **Claim-Oriented Programming (COP).** Praksisen med å designe etter påstander,
  slik Design by Contract designer etter pre-/post-betingelser, løftet fra
  enkeltfunksjoner til et helt prosjekt.
- **Port / reproduce.** Den bivirkningsfrie sjekken (port) og steget som
  re-kjører hver evidens-script for å bekrefte at et tall fortsatt holder
  (reproduce).
- **Ledger / witness.** En append-only, hash-kjedet historikk over påstander
  (ledger) og handlingen med å registrere et tamper-evident kontrollpunkt av den
  (et witness).
- **Påstandsbibliotek.** En delt katalog av gjenbrukbare, evidensbundne
  byggesteiner som prosjekter kan søke i og vendore.
- **REMORA / AROMER.** Et forskningsprogram om *runtime-håndheving*: et
  fail-closed policy-lag som blokkerer utrygge agent-handlinger (REMORA) og et
  ærlig negativresultat om grensene under nøytral metadata (AROMER). Når boken
  siterer funnene, siteres de som evidens med oppgitt omfang.
- **Cloudflare-sannhetslag / RAG / MCP.** En valgfri hostet tjeneste som
  speiler registeret til en søkbar, tamper-evident form; retrieval-augmentert
  generering (RAG) over den korpusen; og verktøyprotokollen (MCP) en assistent
  bruker for å spørre den. Alt i boken virker uten den.

**Påstandsidentifikatorer** (som `CLAIM-GOV-001`) står i klammer etter påstandene
de støtter. Behandle dem som fotnotemarkører: hver peker til en rad i appendikset
der eksakt evidensnivå, omfang og artefakt bor. Du kan lese rett forbi dem; de
er der så en skeptiker kan sjekke.

---

## En note om styrken i påstandene

Denne boken argumenterer for tesen sin bestemt. I et verk om å *ikke* overdrive påstandene
fortjener det et ord. To forpliktelser holder bestemtheten ærlig. For det første
er de sterke utsagnene komparative og mekanisme-baserte, ikke absolutte:
falsifiserbar styring er sterkere *som revisjonsposisjon*, fordi påstandene
kan angripes mekanisk og ikke lar seg bryte, ikke «bedre» i en umålt, generell
forstand. For det andre er hvert hovedfunn selv en registrert påstand på et oppgitt
evidensnivå, med forbeholdet sitt vedlagt; der evidensen er en demonstrasjon
snarere enn et feltresultat, sier teksten det. Les de sterke setningene som
invitasjoner til å sjekke, ikke som konklusjoner å godta.

---
---

# Håndbok i styring av frontier-AI

### Et VeriClaim-oppslagsverk for AI, styring, enterprise-arkitektur, programmering, påstandsbasert programmering og frontier-forskning

*Ett sted å slå opp. Hver kvantitative påstand er sporet til verifisert
evidens; hvert konsept er forklart på to nivåer: enkelt nok for en nykommer,
presist nok for en arkitekt. Les det fra perm til perm som et kurs, eller hopp
til hvilken som helst oppføring som i et leksikon.*

> **Status:** levende syntese / håndbok · **Autoritet:** VeriClaim-registeret
> (`claims/register.yaml`) og påstandsbiblioteket er sannhetens kilde ·
> **Siteringer:** hver `[ID]` løses opp via registeret, hovedboken
> (`/ledger/verify`) eller MCP-verktøyene (`search_claims`, `ask_research`,
> `get_claim_history`). Den engelske utgaven ligger i
> `frontier-ai-governance-master.md`.

---

## Ett-siders kart

▶ **Enkelt forklart:** håndboken har seks deler: *idéen* (hvorfor
falsifiserbar styring), *metoden* (påstandsbasert programmering),
*kunnskapen* (RAG-biblioteket og verifiserte byggesteiner), *reglene*
(regulering og standarder), *arkitekturen* (hvordan det kobles inn i et
enterprise) og *praksisen* (hvordan du faktisk gjør det daglig).

[Figure 1]
    • AI-styring håndbok
      • I Fundamenter
        • Hvorfor styring feiler
        • Påstandsbasert programmering
        • Evidensstigen
        • VeriClaim-porten
      • II Kunnskapsbase
        • Kanon 180 verk
        • Usikkerhet og konform
        • Verifiser-amplifikasjon
        • Beslutningsteori
        • Runtime-håndhevelse
        • Frontier og AGI
      • III Regler
        • NIST AI RMF
        • EU AI Act
        • ISO 42001
        • CSF 2.0 og Privacy
        • Kryssreferansen
        • Ti kontrollmål
      • IV Arkitektur
        • TOGAF ADM
        • Referansearkitektur
        • Operasjonsmodell
      • V Praksis
        • Bygg en styrt funksjon
        • Gjenbruk en byggestein
        • Mønstre og anti-mønstre
      • VI Ærlighet
        • Hva det IKKE beviser
        • Åpne problemer

---

## Innholdsfortegnelse

**Del I: Fundamenter**
1. Sammendrag: den enestående innsikten (see section 1)
2. Hva AI-styring er, og hvorfor det meste feiler (see section 2)
3. Påstandsbasert programmering fra grunnen (see section 3)
4. Evidensstigen (see section 4)
5. VeriClaim-porten: hva den sjekker (see section 5)
6. Cloudflare-sannhetslaget: RAG, hvelv, hovedbok, orakel (see section 6)

**Del II: Kunnskapsbasen**
7. Kanon: 180 verk over 15 kolleksjoner (see section 7)
8. Byggestein-familie 1: usikkerhet og selektiv prediksjon (see section 8)
9. Byggestein-familie 2: verifiser-amplifikasjon (see section 9)
10. Byggestein-familie 3: beslutningsteori under usikkerhet (see section 10)
11. Byggestein-familie 4: runtime-håndhevelse (REMORA/AROMER) (see section 11)
12. Frontier- og AGI-litteratur som styringsgrunnlag (see section 12)

**Del III. Regler: regulering og standarder**
13. Det regulatoriske landskapet forklart (see section 13)
14. Styringskryssreferansen (CLAIM-GOV-001) (see section 14)
15. De ti kontrollmålene: oppslag (see section 15)

**Del IV: Enterprise-arkitektur**
16. Enterprise-arkitektur på 5 minutter (TOGAF, Zachman, ArchiMate) (see section 16)
17. Byggesteinene plassert i TOGAF ADM (see section 17)
18. En referansearkitektur for et styrt AI-system (see section 18)
19. Operasjonsmodell, roller og kadens (see section 19)

**Del V: Praksis**
20. Slik bygger du en styrt AI-funksjon (see section 20)
21. Slik gjenbruker du en byggestein (see section 21)
22. Mønstre og anti-mønstre (see section 22)
23. Assurance-argumentet (see section 23)

**Del VI: Ærlighet**
24. Hva dette IKKE beviser (see section 24)
25. Åpne problemer og ærlige hull (see section 25)

**Del VII: Identitet, policy og fler-sky-kobling**
26. Identitet, autentisering og arbeidslast-føderasjon (see section 26)
27. Policy-as-code og skillet mellom beslutning og håndheving (see section 27)
28. Fler-sky-koblingspunkter: de leverandørnøytrale skjøtene (see section 28)

**Del VIII: Sikkerhetsdrift og databeskyttelse**
29. Sikkerhetsdrift: å holde løftet (see section 29)
30. PII-skrubbing og databeskyttelse (see section 30)

**Appendikser**
- A: Kolleksjonsindeks (see Appendix A)
- B: Indeks over verifiserte teoremer (see Appendix B)
- C: Kryssreferansematrisen (see Appendix C)
- D: Ordliste (see Appendix D)
- E: Hurtigreferanse for påstands-IDer (see Appendix E)
- F: Leseløyper etter rolle (see Appendix F)

---
---

# Del I: Fundamenter

![evidence ladder](figures/no/fig-evidence-ladder.svg)

## 1. Sammendrag: den enestående innsikten

▶ **Enkelt forklart:** det meste av AI-styring er en bunke selvsikre
setninger i en PDF. Denne håndboken viser hvordan styring kan gjøres
*falsifiserbar* (hver påstand bundet til evidens en skeptiker kan sjekke) og
argumenterer for at falsifiserbar styring gir en sterkere *revisjonsposisjon*
enn overbevisende styring, fordi påstandene kan angripes mekanisk og ikke lar
seg bryte (ikke «bedre» i en umålt, generell forstand).

▷ **I dybden.** Når du kombinerer alt i biblioteket (de regulatoriske
rammeverkene, usikkerhetsteorien, verifikasjonsmatematikken,
runtime-håndhevelses-eksperimentene og de ærlige negativresultatene), trer én
tese frem: **styring kan gjøres falsifiserbar**, og et falsifiserbart program
slår et overbevisende ett fordi en fiendtlig anmelder kan angripe det og
*mislykkes i å bryte det*. Fire verifiserte funn komponerer tesen:

[Figure 2]
    Ærlighet er et optimum du kan BEVISE THM-SCORE-001 · 1028 par → Styring gjort FALSIFISERBAR = en kontrakt, ikke et narrativ
    Kapabilitet kommer fra VERIFISERING, ikke bare skala THM-ROUTE-001 · 87380 tabeller → Styring gjort FALSIFISERBAR = en kontrakt, ikke et narrativ
    Fail-closed floor gir HARD garanti, og navngir grensen REMORA CLAIM-001/002/009 → Styring gjort FALSIFISERBAR = en kontrakt, ikke et narrativ
    Hver plikt SPORES til en kontroll CLAIM-GOV-001 · full dekning → Styring gjort FALSIFISERBAR = en kontrakt, ikke et narrativ

- **Ærlighet er ikke en dyd du oppfordrer til; det er et optimum du kan bevise.**
  En proper scoring-regel gjør sannferdig sannsynlighetsrapportering til det
  unike minimum for forventet tap, verifisert eksakt over 1028
  (sann-fordeling, alternativ-rapport)-par [THM-SCORE-001]. Skår komponentene
  dine på kalibrering, og du belønner ærlighet *mekanisk*.
- **Kapabilitet kommer fra verifisering, ikke bare fra skala.** En
  verifiseringsport-styrt kaskade lar en billig generator pluss en selektiv sjekk
  dominere en monolitt på kost/nøyaktighet (over 87 380 uttømmende
  rutetabeller [THM-ROUTE-001]) med flertallsstemme-amplifikasjonen bevist *og*
  dens ærlige konvers (stemmegivning *degraderer* en dårligere-enn-tilfeldig
  velger) bevist også [THM-VOTE-002].
- **En fail-closed policy-floor gir et hardt, benchmark-avgrenset sikkerhetsgulv,
  og samme evidensbase navngir grensen.** REMORAs port ga **0,0 %** usikker-kjørerate på
  en 700-oppgavers adversariell benchmark mot 10 til 20 % for heuristikker [REMORA
  CLAIM-001], og blokkerte **alle 208** uavhengige AgentHarm-scenarier,
  *eksternt validert* [REMORA CLAIM-002]. AROMER-negativresultatet viser ærlig
  det residuale **30,7 %** falsk-aksept under nøytral metadata [REMORA
  CLAIM-009].
- **Hver regulatorisk plikt spores til en verifisert kontroll.** 29 elementer
  fra fem regimer avbildes til 10 kontrollmål med full toveis-dekning,
  fail-closed [CLAIM-GOV-001].

Kombinasjonen er poenget: usikkerhetsteori sier *når* man skal avstå;
verifikasjonsmatematikken sier at avståelse og ruting *gir kapabilitet*;
runtime-evidensen viser at en floor *virker og hvor den svikter*;
kryssreferansen viser *hvilken regulator hver kontroll svarer til*; og porten får
hele kjeden til å *nekte å beskrive seg selv over evidensen sin*.

---

## 2. Hva AI-styring er, og hvorfor det meste feiler

▶ **Enkelt forklart:** styring er settet av regler, roller og sjekker som
holder et AI-system trygt, rettferdig, lovlig og ansvarlig. Det meste feiler
fordi det er *ikke-falsifiserbart*: et dokument påstår gode egenskaper, og
ingen kan sjekke dem mekanisk.

▷ **I dybden.** AI-styring svarer på fire spørsmål: *Hvem er ansvarlig? Hva
kan gå galt? Hvordan vet vi at det virker? Hva skjer når det ikke gjør det?*
Tradisjonell styring svarer i prosa: en policy-perm, et modellkort, en
etikk-erklæring. Feilmodusen er strukturell: prosa akkumulerer *beroligelse*
uten *evidens*. Et modellkort kan si «overvåket for drift» enten noe overvåker
noe eller ikke. En revisor kan ikke skille et samvittighetsfullt program fra et
kosmetisk ved å lese dokumentet. Begge leser likt.

Innsikten denne håndboken operasjonaliserer er å gjøre hver
styringspåstand til en **påstand** med en committed artefakt, et evidensnivå og
et forbehold, eller å *nekte å skrive den*. Nektelsen er disiplinen. Et
styringsprogram som ikke stille kan akkumulere ustøttet beroligelse er ett en
revisor kan stole på.

[Figure 3]
    Policy-PDF påstår gode egenskaper → Leser stoler på PDF-en
    Leser stoler på PDF-en → Revisor kan ikke skille samvittighetsfull fra kosmetisk
    Påstand blir en CLAIM → Artefakt + evidensnivå + forbehold
    Artefakt + evidensnivå + forbehold → Porten verifiserer ved hver commit
    Porten verifiserer ved hver commit → Revisor angriper hver klausul; reproduce sier om den har driftet

**Hvorfor frontier-AI hever innsatsen.** Frontier-systemer er agentiske (de
handler gjennom verktøy), ugjennomsiktige (resonnementet er ikke direkte
inspiserbart) og hurtigskiftende (kapabilitet endres mellom releaser). Hver
egenskap slår ut en klassisk kontroll: agens slår ut «gjennomgå outputen»
(handlingen har alt skjedd), ugjennomsiktighet slår ut «forklar beslutningen»
(det finnes ingen lesbar regel), fart slår ut «sertifiser én gang» (det
sertifiserte systemet er alt utdatert). Svaret er ikke mer prosa: det er
*runtime*-håndhevelse (del II, familie 4), *selektiv* autonomi (familie 1 til 3) og
*kontinuerlig* verifisering (porten, §5).

---

## 3. Påstandsbasert programmering fra grunnen

▶ **Enkelt forklart:** påstandsbasert programmering (COP) er Design-by-Contract
løftet fra én funksjon til et helt prosjekt. En **påstand** er et løfte om
systemet støttet av en fil på disk, sjekket automatisk. Regelen er enkel: *ingen
tall uten en artefakt.*

▷ **I dybden.** Design by Contract (Meyer) fester for-betingelser,
etter-betingelser og invarianter til funksjoner. COP løfter det til prosjektet:
enhver faktapåstand et prosjekt gjør om *seg selv* (et benchmark-tall, en
kapabilitet, en samsvarsegenskap) er en kontrakt mellom ordene og evidensen,
sjekket i CI av VeriClaim-porten.

**Den ene regelen:**

> Ingen tall uten en artefakt. Ingen dok-tall som ikke er bundet til registeret.
> Ingen påstand beskrevet over evidensen den har.

**STOPP-refleksen.** I det øyeblikket du er i ferd med å skrive et faktatall,
stopp: (1) *Hvilken committed artefakt etablerer dette?* (2) *Er det i
registeret?* (3) *Stemmer registerverdien?* (4) *Bærer prosaen forbeholdet?* Kun
hvis alle fire passerer skriver du setningen. Finnes ingen artefakt har du tre
ærlige trekk: produser den, registrer påstanden på `theoretical` og si det, eller
ikke skriv tallet. Det finnes ikke et fjerde trekk.

[Figure 4]
    Skriv et deterministisk skript som MÅLER tingen → Commit artefakten det skriver + proveniensstempel
    Commit artefakten det skriver + proveniensstempel → Registrer påstanden nivå + metrikker + forbehold
    Registrer påstanden nivå + metrikker + forbehold → Bind dok-tallet med et anker
    Bind dok-tallet med et anker → S5
    S5 → Fiks DRIFTEN, aldri porten (FEIL: navngir driften)
    Fiks DRIFTEN, aldri porten → S5
    S5 → vericlaim reproduce byte-identisk? (OK)
    vericlaim reproduce byte-identisk? → Oppdater speil · vitne · push (fortsatt sant i dag)

**Formen på hver påstand:**

```yaml
- id: CLAIM-AREA-001
  statement: "Én linje: hva som påstås."
  evidence_level: benchmarked   # se stigen, §4
  artifact: [results/example.json]
  metrics: { value: 42 }        # tallene dokene kan sitere
  caveat: "Omfang og begrensning: del av claimen, ikke en fotnote."
  reproduce: "python3 bench/example.py"
```

**Hvorfor dette er et styringssubstrat, ikke bare en kodevane.** Hver klausul
i et styringsargument («policy håndhevet», «drift overvåket», «plikter
kartlagt») blir en påstand på et oppgitt evidensnivå. Styringsprogrammet *er*
registeret. Tilliten til det er ikke retorisk; den er utfallet av en port som
nekter drift.

---

## 4. Evidensstigen

▶ **Enkelt forklart:** ikke all evidens er lik. Stigen har seks trinn fra «vi
argumenterte for det» til «en uavhengig part bekreftet det». En påstand kan bare
*beskrives* på trinnet den har *fortjent*.

▷ **I dybden.** Stigen, svakest til sterkest:

[Figure 5]
    theoretical → measured
    benchmarked → reproduced
    machine_checked → externally_validated

| Trinn | Betydning | Eksempel i biblioteket |
|---|---|---|
| **theoretical** | argumentert fra prinsipper eller en bibliografisk peker; ingen måling | en litteraturreferanse [REF-051] |
| **measured** | en deterministisk måling over en committed artefakt | styringskryssreferansens dekning [CLAIM-GOV-001] |
| **benchmarked** | målt på en definert benchmark med oppgitt protokoll | REMORAs 700-oppgavers resultat [REMORA CLAIM-001] |
| **reproduced** | reprodusert *uavhengig* (annen maskin, person eller konfigurasjon) | ikke hevdet for en egen-påstand; `vericlaim reproduce` re-verifiserer byte-identitet løpende, men det er selv-verifisering, ikke den uavhengige reproduksjonen dette trinnet krever |
| **machine_checked** | verifisert ved uttømmende/eksakt beregning | teorem-batteriene [THM-ROUTE-001] |
| **externally_validated** | bekreftet av en uavhengig part eller uavhengige data | AgentHarm datasett-uavhengighet [REMORA CLAIM-002] |

Gradering er **konservativ**: beskriv en påstand kun på nivået den har fortjent.
Nedgradering er alltid tillatt; oppgradering krever ny evidens. Stigen er
styringsprogrammets ærlighetsskala, og porten håndhever den (et dokument kan
ikke beskrive en påstand over det fortjente nivået).

> **⚠️ Et subtilt poeng.** `machine_checked` er *sterkere* enn `benchmarked` for
> egenskapen den dekker, men dekker en *mindre* egenskap: et eksakt matematisk
> faktum på avgrensede instanser, ikke et virkelig-verden-utfall.
> `externally_validated` er det sterkeste *verdslige* trinnet. Ingen av dem
> dominerer den andre på tvers av alle spørsmål; les hva hver påstand faktisk
> dekker.

---

## 5. VeriClaim-porten: hva den sjekker

▶ **Enkelt forklart:** porten er en automatisk sjekker som kjører ved hver commit
og nekter å la prosjektets ord løpe forbi evidensen.

▷ **I dybden.** Standardporten er bivirkningsfri og sjekker ni ting:

[Figure 6]
    1 Register-integritet fail-closed parsing → 2 Artefakt-eksistens
    2 Artefakt-eksistens → 3 Sti-inneslutning ingen .. ingen absolutt ingen symlink
    3 Sti-inneslutning ingen .. ingen absolutt ingen symlink → 4 Proveniens-følgefiler hvordan hver artefakt ble laget
    4 Proveniens-følgefiler hvordan hver artefakt ble laget → 5 Manifest-hasher SHA-256 stemmer
    5 Manifest-hasher SHA-256 stemmer → 6 Dok-binding prosa + kodekommentarer til registeret
    6 Dok-binding prosa + kodekommentarer til registeret → 7 Evidensnivå-ærlighet
    7 Evidensnivå-ærlighet → 8 Undertrykking av utdaterte strenger
    8 Undertrykking av utdaterte strenger → 9 Litteratur-integritet kilden hasher fortsatt til registrert SHA
    vericlaim (hver commit → OK

En separat kommando, `vericlaim reproduce`, *kjører* hvert evidensskript og
feiler med mindre artefakten er byte-identisk: tallet er *fortsatt sant i dag*.

**Hva porten beviser, og ikke.** Den beviser *intern konsistens og
reproduserbarhet*. Den beviser **ikke** at en benchmark er
produksjonsrealistisk, at evidens ikke ble manipulert før commit, at
`externally_validated` faktisk var eksternt, eller at en *setning* er korrekt:
dok-binding beviser at et tall er **til stede og register-matchet**, ikke at
den omkringliggende prosaen er sann. Å holde seg innenfor den grensen er selv en
del av disiplinen (§24).

---

## 6. Cloudflare-sannhetslaget: RAG, hvelv, hovedbok, orakel

▶ **Enkelt forklart:** en valgfri edge-tjeneste som gjør registeret om til en
søkbar, tamper-evident, hash-kjedet post: pluss en litteratur-RAG som *nekter*
å svare når den ikke har grunnlag.

▷ **I dybden.** Sannhetslaget speiler det autoritative registeret inn i en
Cloudflare-stack og legger til en litteratur-RAG. Det er strengt *additivt*:
registeret + porten forblir sannhetens kilde; edge kan være utdatert og blokkerer
aldri.

[Figure 7]
    Register autoritativt → D1 metadata (eksport/push)
    Register autoritativt → Hovedbok hash-kjedet + vitne
    D1 metadata → Vectorize embeddings
    R2-hvelv innholdsadressert → Forsknings-orakel rerank + NEKT
    Vectorize embeddings → Forsknings-orakel rerank + NEKT
    Workers AI rerank · query-expand → Forsknings-orakel rerank + NEKT
    Hovedbok hash-kjedet + vitne → /ledger/verify/
    Forsknings-orakel rerank + NEKT → MCP-verktøy search · ask · verify

**Tre ærlighetsegenskaper:**
1. **Gjenfinning, aldri evidens.** Søkbarhet beviser at et verk var
   registrar-verifisert eller ærlig snapshottet og hash-låst, *ikke* at
   innholdet er sant. Tier følger hvert treff.
2. **Nektelse ved grensen.** Orakelet nekter når ingen chunk klarer
   relevansbaren; nektelsen skåres kun mot *klarerte* fraseringer av spørringen,
   så en prompt-injisert spørring kan ikke manufakturere relevans: den
   forankrede generatoren er den autoritative vakten mot overpåstand.
3. **Tamper-evidens.** Hovedboken er append-only og hash-kjedet; klient-
   verifikatoren bekrefter at den ikke er omskrevet siden første anker.
   Bibliotek-hovedboken står nå på 1408 oppføringer over 192 verifiserte
   bundles.

---
---

# Del II: Kunnskapsbasen

![gate pipeline](figures/no/fig-gate-pipeline.svg)

## 7. Kanon: 180 verk over 15 kolleksjoner

▶ **Enkelt forklart:** et kuratert, hash-låst bibliotek på 180 forskningsverk og
standarder, vektorisert så du kan stille det spørsmål, og det svarer bare når
det har grunnlag.

▷ **I dybden.** Alle skala-tall er fra CLAIM-LIB-RAG-familien:

| Egenskap | Verdi | Sitering |
|---|---|---|
| Kanon-verk | 180 over 15 kolleksjoner | [CLAIM-LIB-RAG-001] |
| Registrar-verifisert inn i katalogen | 171 | [CLAIM-LIB-RAG-001] |
| Dokumenterte drops (ærlige hull) | 9, med 0 udokumenterte | [CLAIM-LIB-RAG-001] |
| Innholdsadresserte chunks, alle live | 9805 | [CLAIM-LIB-RAG-002] |
| Live forsknings-endepunkter verifisert | ende-til-ende | [CLAIM-LIB-RAG-003] |
| Bibliotek-hovedbok oppføringer / bundles | 1408 / 192 | hovedbok `/summary` |

**Slik virker gjenfinning + nektelse** (hvorfor du kan stole på et svar):

[Figure 8]
    • oversett + kanonisk vokabular
    • ærlig: "ikke grunnlag

Full kolleksjonsindeks er Appendiks A. De fire verifiserte *byggestein*-familiene
(§§8-11) er den gjenbrukbare, maskinsjekkede kjernen; litteraturen (§§12-13) er
konteksten de hviler på.

---

## 8. Byggestein-familie 1: usikkerhet og selektiv prediksjon

▶ **Enkelt forklart:** matematikken som lar et system *vite når det ikke vet* og
avstå i stedet for å gjette, med en dekningsgaranti som holder uten å anta
datafordelingen.

▷ **I dybden.** Konform prediksjon pakker enhver prediktor til å gi et *sett*
(eller intervall) som inneholder sannheten med en valgt sannsynlighet,
fordelingsfritt og endelig-utvalg. Den eksakte kombinatorikken i
dekningsgarantien er maskinsjekket [THM-CONF-001], og en kjørt
runtime-demonstrasjon viser konforme intervaller som dekker sannheten i **373 av
400** runder (0,9325 mot et mål på 0,9) [DEMO-001].

**Hvorfor styring trenger dette.** «Systemet vet når det ikke vet» er
forutsetningen for *selektiv autonomi*: handle når sikker, avstå og eskaler når
ikke. Det innløser EU AI Act artikkel 15-kravet til nøyaktighet/robusthet og
NIST AI RMF MEASURE-funksjonen.

> **Nykommerens intuisjon.** Tenk deg en værapp som, i stedet for alltid å si
> «70 % regn», av og til sier «denne klarer jeg ikke å kalle. Spør et
> menneske». En konform innpakning er den prinsippfaste versjonen: den er
> *garantert* å ha rett om hvor ofte den har rett, så avståelsene er til å stole
> på.

**Ærlig grense.** Garantien er *marginal* (over fordelingen), ikke per-instans;
den antar utvekslbare data; og demonstrasjonen [DEMO-001] er én seedet,
deterministisk kjøring med en fast prediktor, forenlig med garantien, ikke mer.

---

## 9. Byggestein-familie 2: verifiser-amplifikasjon

▶ **Enkelt forklart:** å sjekke et svar er ofte billigere og mer pålitelig enn å
produsere det, så en billig produsent pluss en god sjekker kan slå en dyr
produsent. Dette er *hvorfor* «rut vanskelige tilfeller til sterkere
gjennomgang» virker.

▷ **I dybden.** Tre maskinsjekkede resultater:

- **Best-of-n er en eksakt identitet.** Med n uavhengige forsøk hver med
  suksess-sannsynlighet p er sjansen for at minst ett lykkes 1 − (1−p)ⁿ,
  verifisert eksakt ved enumerasjon [THM-VOTE-001].
- **Flertallsstemme amplifiserer, og degraderer ærlig.** Med uavhengige
  velgere bedre enn tilfeldig stiger flertallets nøyaktighet mot 1 (Condorcet);
  med velgere *dårligere* enn tilfeldig faller den mot 0. Begge retninger er
  bevist [THM-VOTE-002]. Konversen er den ærlige halvdelen de fleste
  fremstillinger utelater.
- **Verifiseringsport-styrte kaskader dominerer monolitter.** Å rute hvert element til en
  stor modell kun når en billig verifikator er usikker, slår alltid-stor og
  alltid-liten på kost/nøyaktighet-fronten, etablert over 87 380 uttømmende
  rutetabeller [THM-ROUTE-001].

[Figure 9]
    Input → Billig modell svarer
    Billig modell svarer → V
    V → Aksepter billig svar (ja)
    V → Eskaler til sterk modell / menneske (nei)
    Eskaler til sterk modell / menneske → Aksepter eskalert svar

**Hvorfor styring trenger dette.** Det er den formelle lisensen for
menneske-tilsyn (art. 14) og MANAGE (AI RMF)-kontrollene: avstå-og-eskaler er
ikke et kostnadssenter, det er på den effektive fronten. Det underbygger også
tesen «kapabilitet fra verifisering, ikke skala» i §1.

---

## 10. Byggestein-familie 3: beslutningsteori under usikkerhet

▶ **Enkelt forklart:** de små, eksakte resultatene bak gode beslutninger,
inkludert beviset for at *å fortelle sannheten om din egen sikkerhet er den
optimale strategien*.

▷ **I dybden.** Fire eksakte (rasjonal-aritmetiske) resultater:

- **Brier-properness: ærlighet er optimalt.** Å rapportere dine *sanne*
  sannsynligheter minimerer entydig forventet Brier-skår; enhver annen rapport
  skårer strengt dårligere, verifisert over 1028 (sann-fordeling,
  alternativ-rapport)-par [THM-SCORE-001]. Dette er den formelle grunnen til at
  et kalibrerings-skåret program belønner ærlighet.
- **Sekretær optimal stopping.** Den optimale utforsk-så-forplikt-terskelen og
  dens eksakte vinnersannsynlighet stemmer ved DP for hver n ≤ 20
  [THM-STOP-001].
- **Minimax = maximin.** Hvert 2×2 heltalls-utbetalings nullsumspill har én
  verdi begge spillere kan sikre, over alle 6561 spill [THM-GAME-001]. Dette
  underbygger verste-fall-(adversariell) planlegging.
- **Jensen / varians ≥ 0.** Ulikheten bak hver forventningsgrense, eksakt over
  rutenettet [THM-JENSEN-001].

> **Hvorfor THM-SCORE-001 er det stille tyngdepunktet.** Styring ber stadig
> mennesker og modeller om å «være ærlige om usikkerhet». Proper scoring gjør
> det fra en oppfordring til en *likevekt*: under en proper skår er det
> entydig-beste trekket å si det du faktisk tror. Bygg evalueringen din på en
> proper skår, og du har gjort ærlighet til den dominante strategien.

---

## 11. Byggestein-familie 4: runtime-håndhevelse (REMORA/AROMER)

▶ **Enkelt forklart:** en policy-som-kode-port som blokkerer usikre
agent-handlinger *før* de kjører, bevist å virke, og ærlig om nøyaktig hvor den
slutter å virke.

▷ **I dybden.** REMORA-research-prosjektet leverer runtime-styringsevidensen,
port-verifisert i sitt eget repo og innhentet i biblioteket.

**Floor-en virker.** REMORAs fulle policy-port ga **0,0 %** usikker-kjørerate på
en 700-oppgavers adversariell verktøykall-benchmark, mot 10 til 20 % for hver
heuristisk baseline; Wilson 95 % KI på falsk-aksept [0,00 %, 0,55 %] [REMORA
CLAIM-001]. Avgjørende: floor-en kommer fra **Stage-1 hard-block
policy-invarianter**, ikke fra konsensus-maskineriet; påstanden forbyr å sitere
den som evidens for konsensuslaget.

**Eksternt validert.** På AgentHarm (arxiv:2410.09024) blokkerte REMORA **alle
208** uavhengige skadelige scenarier, FAR 0,0 %, Wilson [0,00 %, 1,81 %],
gradert `externally_validated` ved datasett-uavhengighet [REMORA CLAIM-002].

**Grensen er publisert, ikke skjult.** Under *nøytralt utseende* trust-metadata
(trust=0,70) er den strukturelle policyens falsk-aksept-rate **43,0 %**
(kun strukturell), fallende til **30,7 %** etter semantisk berikelse, et
residualt gap som krever runtime-kjøringsovervåking [REMORA CLAIM-009]. Merket et
NEGATIVT RESULTAT som «må IKKE fjernes eller undertrykkes».

[Figure 10]
    Agent foreslår et verktøykall → P
    P → NEKT, fail-closed 0,0% usikker på benchmark (bryter invariant)
    M → Residual 30,7% FA trenger runtime-overvåking (nøytral / adversariell)
    M → VERIFY / ABSTAIN ruting (nøyaktig høyrisiko)
    Residual 30,7% FA trenger runtime-overvåking → Runtime-kjøringsovervåking + anytime-valid drift
    VERIFY / ABSTAIN ruting → Tillat / eskaler
    Runtime-kjøringsovervåking + anytime-valid drift → Tillat / eskaler

**Den sammensatte lærdommen (en styrt påstand, ikke en mening):** forsvar i
dybden. En fail-closed floor er *nødvendig* for en hard garanti, men
*utilstrekkelig* mot motstandere som leverer godartet-utseende metadata, så den
må parres med runtime-overvåking og drift-deteksjon: nøyaktig art. 15 + art. 14
+ post-market-komposisjonen det regulatoriske laget krever, kommet frem til
empirisk.

---

## 12. Frontier- og AGI-litteratur som styringsgrunnlag

▶ **Enkelt forklart:** du kan ikke styre det du ikke forstår, så biblioteket
sporer fronten (resonneringsmodeller, agenter, verdensmodeller, tolkbarhet) og
inkluderer bevisst også de *skeptiske* artiklene.

▷ **I dybden.** Kolleksjon 15 (28 verk) er balansert med ærlige motstykker:

| Tema | Representative verk | Styringsrelevans |
|---|---|---|
| Resonnering / test-time compute | zero-shot reasoning; DeepSeek-R1 (arxiv:2501.12948); RAP; graph-of-thoughts | risiko flyttes fra trening til inferens: overvåking må følge |
| Agenter | Voyager; generative agents; SWE-agent; AutoGen | autonom verktøybruk er flaten REMORA styrer: trusselmodellen |
| Verdensmodeller | MuZero; DreamerV3; decision transformer | planleggende agenter internaliserer mål: tilsyn må nå inn i loopen |
| Arkitekturer | Mamba/S4; RWKV; ViT; CLIP; Flamingo | lang kontekst + multimodal utvider kapabilitet *og* angrepsflate |
| Tolkbarhet | induction heads; representation engineering; influence functions; Platonic-hypotesen | gjør transparens (art. 13) + tilsyn (art. 14) håndterbart |
| AGI-framing + grenser | Sparks (arxiv:2303.12712); Levels (arxiv:2311.02462); scalable oversight (arxiv:2211.03540); *«Emergent Abilities a Mirage?»* | den skeptiske artikkelen står ved siden av AGI-påstands-artikkelen: samme disiplin som å publisere AROMER-negativresultatet |

Agendaen om verifiserbare påstander som hele systemet operasjonaliserer er selv i
kanon: «Toward Trustworthy AI Development: Mechanisms for Supporting Verifiable
Claims» (arxiv:2004.07213) [REF-051], ved siden av «Open Problems in Technical
AI Governance» (arxiv:2407.14981) [REF-057].

---
---

# Del III. Regler: regulering og standarder

![provenance chain](figures/no/fig-provenance-chain.svg)

## 13. Det regulatoriske landskapet forklart

▶ **Enkelt forklart:** en håndfull rammeverk styrer AI. De overlapper mer enn de
skiller seg; knepet er å se dem som ulike *rapporteringsvinkler* på de samme
underliggende kontrollmålene.

▷ **I dybden.** Regimene denne håndboken kartlegger (kanon-kolleksjon 05-06):

- **NIST AI RMF 1.0**: et *frivillig, risikobasert* amerikansk rammeverk. Fire
  funksjoner: **GOVERN** (kultur/ansvar), **MAP** (kontekst/risikoforståelse),
  **MEASURE** (analyser/spor), **MANAGE** (prioriter/respons). Ikke en
  sjekkliste, en livssyklus.
- **EU AI Act**: *bindende EU-lov*, risiko-lagdelt. For **høyrisiko**-systemer
  krever artikkel 9 til 15 et risikostyringssystem, datastyring, teknisk
  dokumentasjon, journalføring, transparens, menneskelig tilsyn og
  nøyaktighet/robusthet/cybersikkerhet. Det mest preskriptive regimet her.
- **ISO/IEC 42001**: en *sertifiserbar AI-styringssystem-standard* (som ISO
  27001 for infosikkerhet). Plan-Do-Check-Act over klausul 4 til 10 (kontekst,
  ledelse, planlegging, støtte, drift, ytelsesevaluering, forbedring).
- **NIST CSF 2.0**: *cybersikkerhets*-rammeverket, nå med en GOVERN-funksjon:
  GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND, RECOVER. AI-systemer er
  programvaresystemer; CSF gjelder fortsatt.
- **NIST Privacy Framework**: personvern-risiko-følgesvenn til CSF: IDENTIFY-P,
  GOVERN-P, CONTROL-P, COMMUNICATE-P, PROTECT-P.
- **GDPR / NIS2** (kanon-kolleksjon 05): EU personvern- og
  nettverks/informasjonssikkerhets-lov; det juridiske gulvet under datastyring
  og sikkerhet.

> **Det forenende trekket.** I stedet for å kjøre fem samsvarsprogrammer,
> avbild alle fem på ett sett **kontrollmål** og tilfredsstill dem. §14 gjør
> nettopp det, med et fail-closed dekningsbevis.

---

## 14. Styringskryssreferansen (CLAIM-GOV-001)

▶ **Enkelt forklart:** ett kart som kobler hvert rammeverks deler til ti delte
kontrollmål, med en sjekker som *nekter å kompilere* hvis noen del er ukartlagt
eller noe mål udekket.

▷ **I dybden.** [CLAIM-GOV-001] koder den offentlige toppstrukturen til fem
regimer (29 elementer) og avbilder dem til 10 delte kontrollmål via 42 kanter,
verifisert for **full toveis-dekning** (ingen foreldreløse elementer, ingen
udekte mål, hvert mål krevet av ≥2 rammeverk), fail-closed.

[Figure 11]
    NIST AI RMF → Risikostyring
    NIST AI RMF → Menneskelig tilsyn
    NIST AI RMF → Robusthet & nøyaktighet
    NIST CSF 2.0 → Styring & ansvar
    NIST CSF 2.0 → Logging & sporbarhet
    EU AI Act → Transparens & dokumentasjon
    EU AI Act → Robusthet & nøyaktighet
    ISO/IEC 42001 → Styring & ansvar
    ISO/IEC 42001 → Overvåking & post-market
    NIST Privacy → Personvern & databeskyttelse

*(Diagrammet viser representative kanter; hele 42-kanters-matrisen er Appendiks
C.)*

**Hva det er / ikke er.** En gjenbrukbar sporbarhets-byggestein et prosjekt
vendorer for å se hvilke mål hvert regime krever og sjekke sitt eget
kontrollsett: **ikke** juridisk rådgivning, **ikke** sertifisering, **ikke**
bevis på at noen kontroll er korrekt implementert. Artikkel/klausul-spesifikker
under toppnivået er utenfor omfang. Den grensen er en del av påstanden.

---

## 15. De ti kontrollmålene: oppslag

For hvert mål: en enkel definisjon, hvilke rammeverk krever det (fra den
fail-closede kryssreferansen [CLAIM-GOV-001]), hvilken VeriClaim-byggestein
operasjonaliserer det, og det ærlige evidensnivået.

1. **Styring & ansvar**: AI RMF GOVERN, CSF GOVERN, ISO
   kontekst/ledelse/støtte, Privacy GOVERN-P. *Operasjonalisert av:* registeret
   + hovedboken som den ansvarlige posten. *Nivå:* measured.
2. **Risikostyring**: AI RMF GOVERN/MAP/MANAGE, CSF IDENTIFY, EU
   risikostyringssystem, ISO planlegging. *Operasjonalisert av:* verifiseringsport-styrt
   ruting [THM-ROUTE-001] + konform avståelse [THM-CONF-001]. *Nivå:*
   machine_checked (matematikken) / benchmarked (anvendelsen).
3. **Datastyring**: AI RMF MAP, CSF IDENTIFY, EU datastyring, Privacy
   IDENTIFY-P. *Operasjonalisert av:* proveniens/supply-chain-kolleksjon (07) +
   innholdsadressert hvelv. *Nivå:* measured.
4. **Transparens & dokumentasjon**: AI RMF MAP, EU teknisk-dok/transparens,
   Privacy COMMUNICATE-P. *Operasjonalisert av:* påstandsforbehold + evidensnivå +
   dok-bindings-porten. *Nivå:* measured.
5. **Menneskelig tilsyn**: AI RMF MANAGE, EU menneskelig-tilsyn, ISO drift.
   *Operasjonalisert av:* verifiseringsport-styrt eskalering [THM-ROUTE-001]; REMORA
   VERIFY/ABSTAIN-ruting. *Nivå:* machine_checked / benchmarked.
6. **Robusthet & nøyaktighet**: AI RMF MEASURE, CSF PROTECT, EU
   nøyaktighet/robusthet, ISO drift. *Operasjonalisert av:* den fail-closede
   policy-flooren [REMORA CLAIM-001/002]. *Nivå:* benchmarked /
   externally_validated.
7. **Logging & sporbarhet**: CSF DETECT, EU journalføring. *Operasjonalisert
   av:* den hash-kjedede vitne-hovedboken + proveniens-følgefiler. *Nivå:*
   measured.
8. **Overvåking & post-market**: AI RMF MEASURE/MANAGE, CSF
   DETECT/RESPOND/RECOVER, ISO ytelsesevaluering/forbedring. *Operasjonalisert
   av:* `vericlaim reproduce`; anytime-valid overvåking (REMORA REM-020).
   *Nivå:* measured.
9. **Rettferdighet & ikke-diskriminering**: AI RMF MEASURE, EU datastyring.
   *Operasjonalisert av:* rettferdighet/personvern-kolleksjonen (09). *Nivå:*
   theoretical→measured, **det tynneste trinnet** (se §25).
10. **Personvern & databeskyttelse**: CSF PROTECT, Privacy
    IDENTIFY-P/CONTROL-P/PROTECT-P. *Operasjonalisert av:* personvern-
    kolleksjonen (09) + GDPR/NIS2-litteratur (05). *Nivå:* measured.

---
---

# Del IV: Enterprise-arkitektur

## 16. Enterprise-arkitektur på 5 minutter (TOGAF, Zachman, ArchiMate)

▶ **Enkelt forklart:** enterprise-arkitektur (EA) er disiplinen med å designe en
organisasjons systemer som en sammenhengende helhet. TOGAF er den vanligste
*metoden*; Zachman er et *klassifiseringsrutenett*; ArchiMate er et
*modelleringsspråk*. Styring lykkes når den kobles inn i det virksomheten
allerede bruker.

▷ **I dybden.**
- **TOGAF ADM**: Architecture Development Method, en syklus av faser
  (Preliminary, A-H) med Requirements Management i sentrum. Svarer på *hvordan*
  utvikle og styre arkitektur over tid.
- **Zachman-rammeverket**: et 6×6-rutenett (Hva/Hvordan/Hvor/Hvem/Når/Hvorfor ×
  perspektiver). Svarer på *hvilke artefakter* en komplett arkitekturbeskrivelse
  inneholder, nyttig som fullstendighets-sjekkliste.
- **ArchiMate**: en notasjon med forretnings/applikasjons/teknologi-lag. Svarer
  på *hvordan tegne* arkitekturen entydig.

Denne håndboken avbilder VeriClaim-byggesteinene på **TOGAF ADM** (§17) fordi
ADMs fasestruktur passer naturlig til en styringslivssyklus, og dens
Requirements-Management-ryggrad avbildes på registeret.

---

## 17. Byggesteinene plassert i TOGAF ADM

▶ **Enkelt forklart:** hver fase i den standard arkitekturmetoden får en
*falsifiserbar* leveranse i stedet for en prosa-leveranse.

▷ **I dybden.**

[Figure 12]
    Preliminary porten = styringsmekanisme → A Visjon 10 mål = NFR-er
    A Visjon 10 mål = NFR-er → B Forretning ansvar · RACI
    B Forretning ansvar · RACI → C Data & App proveniens · hvelv
    C Data & App proveniens · hvelv → D Teknologi konform · REMORA · edge
    D Teknologi konform · REMORA · edge → E Løsninger kontrollbibliotek
    E Løsninger kontrollbibliotek → F Migrasjon REMORA TOGAF-utrullingsplan
    F Migrasjon REMORA TOGAF-utrullingsplan → G Impl.-styring porten i CI · PDP/PEP
    G Impl.-styring porten i CI · PDP/PEP → H Endringsledelse reproduce · hovedbok · drift
    H Endringsledelse reproduce · hovedbok · drift → A Visjon 10 mål = NFR-er

| ADM-fase | Styringshensyn | VeriClaim-byggestein | Rammeverksanker |
|---|---|---|---|
| **Preliminary** | Etabler kapabiliteten | Porten som arkitektur-styringsmekanisme; registeret som krav-repositorium | ISO 42001 ledelse; AI RMF GOVERN |
| **A: Visjon** | Risikoappetitt, mål | De 10 kontrollmålene [CLAIM-GOV-001] som ikke-funksjonelle krav | EU AI Act art. 9; AI RMF MAP |
| **B: Forretning** | Roller, ansvar | `governance_accountability`; RACI over registeret | ISO 42001 ledelse; CSF GOVERN |
| **C: Data & Applikasjon** | Datakvalitet, proveniens, dok | Proveniens-kolleksjon (07); innholdsadressert hvelv | EU AI Act art. 10-11 |
| **D: Teknologi** | Robusthet, runtime | Konform [THM-CONF/DEMO-001]; REMORA [CLAIM-001/002]; edge | EU AI Act art. 15; CSF PROTECT |
| **E: Løsninger** | Hvilke kontroller å bygge | Det verifiserte kontrollbiblioteket (§§8-11) | AI RMF MEASURE/MANAGE |
| **F: Migrasjon** | Utrullingssekvens | REMORA enterprise TOGAF-utrullingsplan | ISO 42001 planlegging |
| **G: Impl.-styring** | Håndhevelse i leveranse | Porten i CI; fail-closed PDP/PEP [REMORA CLAIM-001] | EU AI Act art. 14; CSF DETECT |
| **H: Endringsledelse** | Drift, overvåking | `reproduce`; vitne-hovedbok; anytime-valid overvåking | EU AI Act art. 15; CSF RESPOND/RECOVER |
| **Requirements Mgmt** | Sannhetens kilde | Register + kryssreferanse | alle fem regimer |

---

## 18. En referansearkitektur for et styrt AI-system

▶ **Enkelt forklart:** tegningen: data kommer inn, en modell handler, en
fail-closed port står mellom modellen og verden, og alt logges til en
tamper-evident hovedbok og re-verifiseres kontinuerlig.

▷ **I dybden.**

[Figure 13]
    Styrte data proveniens · kvalitet → Modell / agent
    Modell / agent → CONF
    CONF → Avstå / eskaler menneskelig tilsyn (nei)
    PEP → Blokkert + logget (nekt)
    PEP → Handling i verden (tillat)
    Handling i verden → Runtime-overvåking + drift-deteksjon
    Blokkert + logget → Hash-kjedet hovedbok revisjonsspor
    Handling i verden → Hash-kjedet hovedbok revisjonsspor
    Runtime-overvåking + drift-deteksjon → Hash-kjedet hovedbok revisjonsspor
    Hash-kjedet hovedbok revisjonsspor → Periodisk reproduce tall fortsatt sanne?

Hvert element avbildes på et kontrollmål (§15) og en byggestein (§§8-11).
Arkitekturens definerende egenskap er at **porten er i handlings-stien**, ikke
ved siden av: en ukjent handling nekter som standard (fail-closed), og
nektelsen er selv en revisjonshendelse.

---

## 19. Operasjonsmodell, roller og kadens

▶ **Enkelt forklart:** hvem gjør hva, hvor ofte, så styring forblir sann over
tid i stedet for å råtne til utdatert dokumentasjon.

▷ **I dybden.**

| Kadens | Aktivitet | Eier |
|---|---|---|
| **Kontinuerlig (CI)** | Porten ved hver commit; fail-closed | hver bidragsyter |
| **Per release** | `reproduce` over hele registeret; speil-oppdatering; vitne | release-ingeniør |
| **Periodisk (styringsgjennomgang)** | Re-kjør kryssreferanse-dekning; gjennomgå evidensnivå for drift/nedgradering; sjekk ærlig-hull-listen (§25) | den ansvarlige styringsrollen (ISO 42001 ledelse) |
| **Ved hendelse** | Hovedbokens append-only-historikk er revisjonssporet; `reproduce` re-etablerer hvilke tall som fortsatt holder | hendelseseier |

**RACI, minimalt:** *registeret* er Accountable til styringsrollen,
Responsible til hver bidragsyter, Consulted med arkitekturpraksisen (TOGAF), og
Informed til revisorer/regulatorer via hovedboken.

---
---

# Del V: Praksis

## 20. Slik bygger du en styrt AI-funksjon

▶ **Enkelt forklart:** mål først, påstand andre, skriv prosaen sist, og la porten
ta deg hvis du drifter.

▷ **I dybden**, som en sjekkliste:

1. **Produser evidensen.** Skriv et *deterministisk* skript som måler
   egenskapen; commit artefakten det skriver med et proveniensstempel.
2. **Registrer påstanden** på dens *fortjente* nivå, med metrikker og et forbehold.
3. **Bind hvert dok-tall** med et ``-anker.
4. **Kjør `vericlaim`**: må skrive `[OK]`; den navngir enhver drift med
   `fil:linje`.
5. **Kjør `vericlaim reproduce`** når kode en benchmark avhenger av endret.
6. **Oppdater edge-speilet**; for bibliotek-endringer, **vitne** og push
   `claims/witness.jsonl`.

> **Refleksen som betyr mest:** når du er i ferd med å skrive et tall og ingen
> artefakt finnes, stopp. Produser den, eller registrer på `theoretical` og si
> det, eller ikke skriv det.

---

## 21. Slik gjenbruker du en byggestein

▶ **Enkelt forklart:** du kan gjenbruke en verifisert kontroll fra biblioteket
uten å re-utlede den, og du arver dens ærlighet (nivå + forbehold) uendret.

▷ **I dybden.** `fetch_bundle` → `import_bundle` (offline hash-verifisering) →
`use_code` (byte-eksakt vendoring med en bindende test). Et konsumerende
prosjekt arver påstandens evidensnivå og forbehold; en importør kan **nedgradere,
men aldri stille oppgradere**. Eksempelmål: den konforme innpakningen
[THM-CONF], den verifiseringsport-styrte ruteren [THM-ROUTE-001], styringskryssreferansen
[CLAIM-GOV-001], beslutningsteori-batteriet [THM-SCORE/STOP/GAME/JENSEN].

[Figure 14]
    • id
    • påstand + kode + artefakt

---

## 22. Mønstre og anti-mønstre

| ✅ Mønster | ❌ Anti-mønster |
|---|---|
| Mål, så påstand, så skriv | «Dette tallet er omtrent riktig» |
| Registrer forbeholdet med tallet | Siter tallet, dropp omfanget |
| Avstå-og-eskaler under usikkerhet | Tving alltid et selvsikkert svar |
| Fail-closed standard (nekt det ukjente) | Fail-open («tillat med mindre blokkert») |
| Publiser negativresultatet [REMORA CLAIM-009] | Slett resultater som ser dårlige ut |
| Grader konservativt; nedgrader når evidens svekkes | Stille oppgradering til et penere nivå |
| Ett sett kontrollmål, mange rapporteringsvinkler | Fem parallelle samsvarspermer |
| Fiks driften porten navngir | «Omgå porten» |

---

## 23. Assurance-argumentet

▶ **Enkelt forklart:** hele håndboken, komprimert til én påstand du kan angripe.

▷ **I dybden.**

[Figure 15]
    Regulatoriske plikter sporet til kontroller CLAIM-GOV-001 → Et frontier-AI-system styrt til en evidensforankret referansestandard , og hver klausul er falsifiserbar
    Hver kontroll verifisert på et oppgitt nivå §§8-11 → Et frontier-AI-system styrt til en evidensforankret referansestandard , og hver klausul er falsifiserbar
    Runtime fail-closed + eksternt validert REMORA CLAIM-002 → Et frontier-AI-system styrt til en evidensforankret referansestandard , og hver klausul er falsifiserbar
    Grenser oppgitt REMORA CLAIM-009 · §24 → Et frontier-AI-system styrt til en evidensforankret referansestandard , og hver klausul er falsifiserbar
    Hele kjeden reproduce-sjekket + hash-kjedet §5-6 → Et frontier-AI-system styrt til en evidensforankret referansestandard , og hver klausul er falsifiserbar

> *Et frontier-AI-system når denne evidensforankrede referansestandarden når hver
> regulatorisk plikt er sporet til en kontroll [CLAIM-GOV-001], hver kontroll er
> verifisert på et oppgitt evidensnivå (§§8-11), runtime er fail-closed med en
> eksternt-validert sikkerhets-floor [REMORA CLAIM-002] hvis grenser er oppgitt
> [REMORA CLAIM-009], og hele kjeden holdes i et append-only, reproduce-sjekket,
> hash-kjedet register som nekter å beskrive seg selv over evidensen sin
> (§§5-6).*

Assurance-saken er ikke «stol på dette dokumentet»; den er «angrip hvilken som
helst klausul: porten, hovedboken og reproduce-ritualet forteller deg om den har
driftet».

---
---

# Del VI: Ærlighet

## 24. Hva dette IKKE beviser

▶ **Enkelt forklart:** grunnen til å stole på de sterke påstandene er at de
svake punktene oppgis like tydelig.

▷ **I dybden.**
- **Porten beviser konsistens og reproduserbarhet, ikke sannhet.** Dok-binding
  beviser at et tall er *til stede og register-matchet*, ikke at setningen er
  korrekt, benchmarken realistisk, eller evidensen umanipulert før commit.
- **Kryssreferansen er strukturell, ikke juridisk** [CLAIM-GOV-001]: ikke
  samsvars-sertifisering; ikke legg den frem for en regulator som
  konformitetsevidens.
- **Runtime-resultater er simulator-scoped**: REMORA kjører ingen ekte
  shell/nettverk/DB/fil-mutasjoner [REMORA CLAIM-001]; AgentHarm-ekstern-
  validiteten er intensjons-gating, ikke verifisert verktøykall-avskjæring
  [REMORA CLAIM-002].
- **Maskinsjekkede teoremer er avgrensede instanser**: eksakte innenfor
  oppgitte grenser (87 380 tabeller [THM-ROUTE-001]; 6561 spill [THM-GAME-001]);
  de generelle asymptotiske utsagnene forblir litteratur.
- **Litteratursiteringer er bibliografiske**: en [REF-NNN] fastslår at
  registrar-posten finnes og ekstraktet er hash-låst, ingenting om verkets
  korrekthet.

## 25. Åpne problemer og ærlige hull

- **Rettferdighet er den tynneste byggesteinen** (§15.9): litteratur-forankret,
  men ingen maskinsjekket rettferdighets-primitiv sammenlignbar med de konforme
  eller verifiser-matematiske batteriene. Navngitt, ikke bortforklart.
- **Feltvalidering av runtime-flooren** står igjen: de 0,0 % er benchmark-scoped
  [REMORA CLAIM-001]; ekte verktøykall-avskjæring er fremtidig arbeid.
- **Kryssreferansen stopper ved toppnivå-struktur**: artikkel/klausul-nivå
  sporbarhet er en naturlig neste byggestein.
- **Assurance-steg med en menneskelig port** (uavhengig gjennomgang av runtime-
  prosjektet) er det høyeste-innflytelse neste steget for de sterkeste
  evidenstrinnene.

Disse definerer perimeteret; et styringsprogram som kjenner sitt eget
perimeter er det som er verdt å stole på innenfor det.

---
---

# Del VII: Identitet, policy og fler-sky-kobling

> Styring er bare ekte hvis den *håndheves*, og håndheves likt uansett hvor
> systemet kjører. Denne delen kobler de abstrakte kontrollmålene (§15) til de
> konkrete skjøtene som bærer identitet og policy på tvers av skyer. Tallene er
> verifisert av **CLAIM-COUPLE-001** (`governance/identity_coupling.py` i
> påstandsbiblioteket), og standardene er bevart hash-låst som litteratur under
> den påstanden.

## 26. Identitet, autentisering og arbeidslast-føderasjon

▶ **Enkelt forklart:** før et system kan håndheve *hva* som er tillatt, må det
vite *hvem* som spør: enten «hvem» er et menneske som logger inn eller én
arbeidslast som kaller en annen. Trikset som gjør dette portabelt er å aldri
sende langlevde hemmeligheter: en arbeidslast beviser hvem den er med et
kortlevd, signert token som alle skyer allerede forstår.

▷ **I dybden.** Identitet deler seg i to problemer med samme løsning.

**Menneskelig autentisering** hviler på **OAuth 2.0** (RFC 6749, delegert
autorisasjon) med **OpenID Connect** (OIDC Core 1.0) lagt oppå for å svare på
*hvem som autentiserte seg*. En OIDC-identitetstilbyder utsteder et signert
**ID-token** (en JWT, RFC 7519) hvis utsteder, publikum og utløp en relying
party verifiserer mot et publisert nøkkelsett. Livssyklus
(inn/endring/ut) bæres av **SCIM 2.0** (RFC 7643/7644), slik at deaktivering
propagerer som en kontroll, ikke en manuell oppgave. **SAML 2.0** er fortsatt
det etablerte assertion-formatet, og alle store IdP-er bygger bro mellom de to.

**Arbeidslast-identitetsføderasjon** fjerner den siste statiske hemmeligheten.
En arbeidslast (en Kubernetes/OpenShift-pod, en CI-jobb) presenterer et
OIDC-token fra en betrodd utsteder; skyen bytter det, via **OAuth 2.0 Token
Exchange** (RFC 8693), mot et kortlevd, snevert scoped sky-credential. Dette er
nøyaktig hva GCP Workload Identity Federation, AWS
`AssumeRoleWithWebIdentity`/IAM Roles Anywhere og Azure federated credentials
hver implementerer. Der sertifikater er identiteten gir **mTLS med X.509**
(RFC 8705, sertifikat-bundne tokens) og **SPIFFE/SPIRE** (portable `spiffe://`
SVID-er) samme garanti for tjeneste-til-tjeneste-kall.

[Figure 16]
    Arbeidslast → OIDC-utsteder + JWKS (1 · OIDC ID-token (JWT))
    OIDC-utsteder + JWKS → Sky-STS AWS · Azure · GCP (2 · token exchange · RFC 8693)
    Sky-STS AWS · Azure · GCP → Sky-ressurs (3 · kortlevd, scoped credential)

*Én utsteder, tre skyer, samme standard: ingen distribuerte statiske nøkler.
Sikkerheten hviler på publikums-begrensning, påstandsbetingelser og korte TTL-er;
en feil-scoped tillitspolicy fødererer mer enn tiltenkt (se forbeholdet i
CLAIM-COUPLE-001).*

## 27. Policy-as-code og skillet mellom beslutning og håndheving

▶ **Enkelt forklart:** skriv regelen én gang, som kode, og håndhev den likt
overalt. Skill delen som *bestemmer* («er dette tillatt?») fra delen som
*håndhever* den, slik at regelen kan testes, versjoneres og revideres som all
annen kode.

▷ **I dybden.** **NIST SP 800-207 (Zero Trust Architecture)** navngir formen: et
**Policy Decision Point (PDP)** bestemmer hver forespørsel ut fra autentisert
identitet, kontekst og policy; et **Policy Enforcement Point (PEP)** utfører
beslutningen ved ressursen. Ingen implisitt tillit fra nettverksplassering;
hver forespørsel evalueres eksplisitt og etter minste-privilegium.

Policy-as-code fyller PDP-en. **Open Policy Agent** med språket **Rego** er det
portable substratet: samme Rego kjører som en Kubernetes admission controller
(Gatekeeper) på EKS, AKS, GKE og OpenShift, som en tjeneste-følgefil, og i CI.
**Cedar** (åpnet kildekode, bak Amazon Verified Permissions) tilbyr et
formelt-analyserbart autorisasjonsspråk for beslutninger på applikasjonsnivå.
**CEL** (Common Expression Language) bærer portable betingelser (GCP IAM
Conditions, Kubernetes admission). Kontrollregister-sjekkene i §15 uttrykkes
naturlig her: et kontrollmål blir en policy en maskin kan evaluere.

[Figure 17]
    Forespørsel + identitets-påstander / SPIFFE-ID → PEP mesh · gateway · admission
    PEP mesh · gateway · admission → PDP · policy-as-code OPA/Rego · Cedar · CEL (spør)
    PDP · policy-as-code OPA/Rego · Cedar · CEL → PEP mesh · gateway · admission (tillat / nekt + forpliktelser)
    PEP mesh · gateway · admission → Revisjon · OpenTelemetry (beslutningslogg)

*PDP-en identifiserer ingenting og PEP-en bestemmer ingenting: det skillet er
det som lar én Rego-policy være styringsregelen på hver plattform. En policy
er bare så god som testene og inndataene sine; beslutningslogging gjør den
reviderbar.*

## 28. Fler-sky-koblingspunkter: de leverandørnøytrale skjøtene

▶ **Enkelt forklart:** en virksomhet lever sjelden på én sky. Hvis styring er
koblet med hver skys proprietære knapper, må den bygges på nytt, og vil drifte,
på neste sky. Utveien er å koble på de åpne standardene hver sky allerede
snakker, og behandle hver skys native tjeneste som en *adapter*.

▷ **I dybden.** CLAIM-COUPLE-001 koder dette som en fail-closed kryssreferanse:
på tvers av **4** skyer (AWS, Azure, GCP, OpenShift) og **6**
koblingsdimensjoner navngir alle **24** celler en konkret native mekanisme og
kobler på **13** åpne standarder. Sjekkeren håndhever egenskapen som gjør skjøten
til å stole på: **hver dimensjon er forankret av minst én åpen standard delt på
tvers av to eller flere skyer**, så portabilitet er verifisert, ikke påstått.

| Koblingsdimensjon | AWS | Azure | GCP | OpenShift | Portabel skjøt |
|---|---|---|---|---|---|
| Arbeidslast-identitetsføderasjon | STS AssumeRoleWithWebIdentity · IAM Roles Anywhere · IRSA | Entra Workload Identity Federation · Managed Identities | Workload Identity Federation | SA projected tokens (OIDC-utsteder) | OIDC · RFC 8693 · JWT |
| Menneskelig autentisering | IAM Identity Center · Cognito | Microsoft Entra ID | Cloud Identity | OpenShift OAuth-server | OIDC · OAuth2 · SAML2 · SCIM2 |
| Autorisasjonspolicy | IAM/SCP · Verified Permissions (Cedar) · Gatekeeper | Azure Policy · Gatekeeper på AKS | IAM Conditions (CEL) · Org Policy · Gatekeeper | K8s RBAC · Gatekeeper · Kyverno | Rego/OPA · Cedar · CEL |
| Hemmelighetshåndtering | Secrets Manager · Parameter Store | Key Vault | Secret Manager | Secrets + CSI-driver · cert-manager | OIDC · mTLS/X.509 |
| Observabilitet & revisjon | CloudTrail · ADOT | Azure Monitor · Activity Log | Cloud Audit Logs | K8s audit · OTel Operator | OpenTelemetry · CloudEvents |
| Tjeneste-til-tjeneste-mTLS | Private CA · App Mesh | Istio/OSM på AKS | CA Service · Anthos SM | Service Mesh (Istio) · cert-manager | mTLS/X.509 · SPIFFE |

De tretten åpne standardene, hver bevart hash-låst som litteratur under
CLAIM-COUPLE-001:

| # | Standard | Koblingsrolle |
|---|---|---|
| 1 | OpenID Connect Core 1.0 | Føderert identitet via signerte ID-tokens |
| 2 | OAuth 2.0 (RFC 6749) | Delegert autorisasjon |
| 3 | OAuth 2.0 Token Exchange (RFC 8693) | STS-stil arbeidslast-føderasjon |
| 4 | SAML 2.0 | SSO-assertions for virksomheter |
| 5 | SCIM 2.0 (RFC 7643/7644) | Provisjonering på tvers av domener |
| 6 | JWT (RFC 7519) | Signert, verifiserbart påstandstoken |
| 7 | mTLS / X.509 (RFC 8705) | Gjensidig-TLS klientidentitet, bundne tokens |
| 8 | SPIFFE/SPIRE | Portabel arbeidslast-identitet (SVID) |
| 9 | Open Policy Agent / Rego | Portabel policy-as-code |
| 10 | Cedar | Analyserbart autorisasjonsspråk |
| 11 | CEL | Portable betingelsesuttrykk |
| 12 | OpenTelemetry | Leverandørnøytral telemetri & revisjonseksport |
| 13 | CloudEvents | Portabel hendelseskonvolutt |

[Figure 18]
    AWS-adaptere → Åpen-standard koblingslag (portabelt
    Azure-adaptere → Åpen-standard koblingslag (portabelt
    GCP-adaptere → Åpen-standard koblingslag (portabelt
    OpenShift-adaptere → Åpen-standard koblingslag (portabelt
    Åpen-standard koblingslag (portabelt → Ett styrt kontrollplan skriv én gang · håndhev overalt

**Hva dette er og ikke er.** Det er et arkitektur-sporbarhetshjelpemiddel over
offentlig dokumenterte mekanismer: ikke en sikkerhets-designgjennomgang, ikke
en sertifisering, og ikke bevis for at en gitt utrulling er riktig konfigurert.
Native tjenestenavn er gjeldende ved skrivetidspunkt; skyer omdøper og legger
til tjenester. Den sjekkbare egenskapen er intern fullstendighet og
standard-deling på tvers av skyer; standardene er autoriteten. Brukt ærlig er
det det konkrete svaret på leverandøruavhengighets-kravet i §18-§19: samme
styring, beviselig portabel.

---
---

# Del VIII: Sikkerhetsdrift og databeskyttelse

> Styring navngir løftet; sikkerhetsdrift *holder* det, dag for dag. Denne
> delen gir hvert kontrollmål et driftsmessig hjem og behandler persondata som
> en førsteklasses fare. Tallene er verifisert av **CLAIM-SECOPS-001**
> (`governance/security_operations.py` i påstandsbiblioteket); standardene er
> bevart hash-låst som litteratur.

## 29. Sikkerhetsdrift: å holde løftet

▶ **Enkelt forklart:** et kontrollmål som «vi logger alt» eller «vi oppdager
hendelser» er bare ekte hvis noen faktisk *kjører* driften bak det, hver dag,
mot en anerkjent standard. Denne seksjonen kobler hvert driftsdomene
(tjenestestyring, observabilitet, logging, sårbarhetshåndtering, deteksjon,
hemmeligheter, robusthet) til praksisene og standardene som holder det.

▷ **I dybden.** CLAIM-SECOPS-001 koder en fail-closed dekningskryssreferanse:
**8** driftsdomener navngir **33** konkrete praksiser kjørt mot **13** offentlige
standarder, og sjekkeren verifiserer at hvert *driftsmessige* kontrollmål har
minst ett domene som holder det, så «logging & sporbarhet» er ikke en setning i
en policy, men en loggstyrings-praksis mot NIST SP 800-92, og «overvåking &
etter-marked» er observabilitet mot NIST SP 800-137 pluss deteksjon kartlagt mot
MITRE ATT&CK.

| Domene | Nøkkelpraksiser | Standarder | Holder mål |
|---|---|---|---|
| IT-tjenestestyring (ITSM) | Hendelse · endring · problem · SLM | ISO/IEC 20000-1 · ITIL 4 · NIST SP 800-61 | Accountability · monitoring |
| Observabilitet | Metrikker · tracing · SLO-er · driftdeteksjon | OpenTelemetry · NIST SP 800-137 | Monitoring · robustness |
| Logging & revisjon | Sentrale logger · tamper-evident spor · retensjon · tidssync | NIST SP 800-92 · ISO/IEC 27001 · OpenTelemetry | Logging & traceability |
| PII databeskyttelse | Oppdagelse · skrubbing · minimering · DSAR | ISO/IEC 27701 · GDPR · NIST SP 800-53 | Privacy · datastyring |
| Sårbarhetshåndtering | Skanning · patch-SLA-er · SBOM · pentest | CIS Controls v8 · OWASP ASVS · NIST SP 800-53 | Robustness · risk |
| Deteksjon & respons | SIEM-deteksjoner · SOAR · IR-øvelser | MITRE ATT&CK · NIST SP 800-61 · CIS v8 | Monitoring · human oversight |
| Hemmeligheter & nøkler | Rotasjon · HSM-nøkler · kortlevde creds | NIST SP 800-53 · CIS v8 | Robustness · accountability |
| Robusthet & backup/DR | Immutable backups · restore-testing · RTO/RPO | ISO/IEC 27001 · NIST SP 800-53 | Robustness · risk |

[Figure 19]
    Logging & sporbarhet → Logging & revisjon NIST 800-92
    Overvåking & etter-marked → Observabilitet + deteksjon OTel · 800-137 · ATT&CK
    Personvern & databeskyttelse → PII-beskyttelse ISO 27701 · GDPR
    Robusthet & nøyaktighet → Sårbarhet + robusthet CIS · 800-53

*Fire mål (transparens, menneskelig tilsyn, rettferdighet og ansvarlighet) er
styrings- og avslørings-temaer eid av kontrollregisteret (§15), ikke driftsdomener;
kryssreferansen oppgir den utelatelsen eksplisitt i stedet for å late som om
hvert mål er en driftsoppgave.*

## 30. PII-skrubbing og databeskyttelse

▶ **Enkelt forklart:** persondata er radioaktivt: nyttig, men farlig hvis det
lekker inn i logger, prompter eller en modells minne. Behandle det som en fare
med sin egen pipeline: finn det, fjern eller masker det før det lagres eller
sendes til en modell, behold kun det du må, og respekter folks rettigheter over
det.

▷ **I dybden.** For et AI-system kommer PII inn via prompter, hentet kontekst og
logger: tre flater et tradisjonelt databeskyttelsesprogram ofte overser. En
forsvarlig pipeline kjører, i rekkefølge: **oppdagelse og klassifisering** (vit
hvor PII er), **skrubbing/redaksjon eller pseudonymisering** før lagring eller
modell-input, **minimering og retensjon** (behold minst mulig, kortest mulig),
og **den registrertes rettigheter** (DSAR, sletting). ISO/IEC 27701 utvider et
ISO 27001-ISMS til et personverns-styringssystem kartlagt mot **GDPR**; NIST SP
800-53 leverer de detaljerte personvern-kontrollene.

[Figure 20]
    Prompter · kontekst · logger → Oppdag & klassifiser PII
    Oppdag & klassifiser PII → Skrubb / rediger / pseudonymiser
    Skrubb / rediger / pseudonymiser → Minimert lager retensjon håndhevet
    Minimert lager retensjon håndhevet → DSAR & sletting

*Redaksjon er best-effort og må testes mot realistiske data; pseudonymisering er
ikke anonymisering, og telemetri/logger er en vanlig lekkasjevei (§29s
loggingsdomene og dette deler ansvar). Den ærlige holdningen: minimer det du
samler inn slik at skrubbe-pipelinen har mindre å fange.*

---
---

# Appendikser

## Appendiks A: kolleksjonsindeks

180 kanon-verk over 15 kolleksjoner [CLAIM-LIB-RAG-001]:

| # | Kolleksjon | Verk |
|---|---|---|
| 01 | Usikkerhet og ruting | 13 |
| 02 | LLM- og agent-arkitekturer | 19 |
| 03 | Evaluering og kalibrering | 11 |
| 04 | Agent-sikkerhet | 12 |
| 05 | AI-styring | 18 |
| 06 | MLOps og enterprise-arkitektur | 13 |
| 07 | Proveniens og supply chain | 12 |
| 08 | Formelle metoder | 7 |
| 09 | Rettferdighet, personvern og menneskelig innvirkning | 9 |
| 10 | Assurance-saker og runtime-verifisering | 3 |
| 11 | ML-trening og systemer | 14 |
| 12 | Programvareteknikk og SaaS | 10 |
| 13 | Marketing og vekst | 5 |
| 14 | Finans | 6 |
| 15 | Frontier-resonnering og AGI | 28 |

## Appendiks B: indeks over verifiserte teoremer

Maskinsjekkede byggesteiner (påstandsbiblioteket, `machine_checked` med mindre
annet er oppgitt), gruppert etter familie:

- **Usikkerhet:** konform kombinatorikk [THM-CONF-001..004]; runtime-
  demonstrasjon [DEMO-001, benchmarked].
- **Verifiser-amplifikasjon:** best-of-n-identitet [THM-VOTE-001]; flertalls-
  amplifikasjon + ærlig degradering [THM-VOTE-002]; verifiseringsport-styrt
  kaskade-dominans, 87 380 tabeller [THM-ROUTE-001].
- **Beslutningsteori:** Brier-properness [THM-SCORE-001]; sekretær-stopping
  [THM-STOP-001]; minimax=maximin, 6561 spill [THM-GAME-001]; Jensen/varians
  [THM-JENSEN-001].
- **Klassiske fundamenter (utvalg):** Chernoff-Hoeffding [THM-CH-001];
  CLT-demonstrasjon [THM-CLT-001, benchmarked]; Johnson-Lindenstrauss
  [THM-JL-001]; KKT [THM-KKT-001]; maks-flyt/min-snitt [THM-MFMC-001];
  no-free-lunch [THM-NFL-001]; universell approksimasjon [THM-UAT-001];
  VC-dimensjon [THM-VC-001]; Bayes/posterior [THM-BAYES-001, THM-POST-001];
  Lean-verifisert sett [THM-LEAN-001..003].

Eksakt grad og omfang står i hver påstands registeroppføring; tallene over er
uttømmende-sjekk-størrelsene registrert i evidensartefaktene.

## Appendiks C: kryssreferansematrisen

Dekning av de 10 kontrollmålene av de 5 rammeverkene [CLAIM-GOV-001]:

| Mål | AI RMF | CSF 2.0 | EU AI Act | ISO 42001 | Privacy |
|---|---|---|---|---|---|
| Styring & ansvar | GOVERN | GOVERN | - | kontekst/ledelse/støtte | GOVERN-P |
| Risikostyring | GOVERN/MAP/MANAGE | IDENTIFY | risk-mgmt-system | planlegging | - |
| Datastyring | MAP | IDENTIFY | data-governance | - | IDENTIFY-P |
| Transparens & dokumentasjon | MAP | - | tech-doc/transparency | - | COMMUNICATE-P |
| Menneskelig tilsyn | MANAGE | - | human-oversight | drift | - |
| Robusthet & nøyaktighet | MEASURE | PROTECT | accuracy/robustness | drift | - |
| Logging & sporbarhet | - | DETECT | record-keeping | - | - |
| Overvåking & post-market | MEASURE/MANAGE | DETECT/RESPOND/RECOVER | - | perf-eval/improvement | - |
| Rettferdighet & ikke-diskriminering | MEASURE | - | data-governance | - | - |
| Personvern & databeskyttelse | - | PROTECT | - | - | IDENTIFY-P/CONTROL-P/PROTECT-P |

Verifisert: 29 elementer, 42 kanter, ingen foreldreløse elementer, ingen udekte
mål, hvert mål dekket av ≥2 rammeverk, sjekket fail-closed [CLAIM-GOV-001].

## Appendiks D: ordliste

- **Påstand**: en kontrakt mellom et oppgitt faktum og en committed artefakt,
  sjekket av porten.
- **Evidensnivå**: ærlighetstrinnet en påstand har fortjent: theoretical <
  measured < benchmarked < reproduced < machine_checked < externally_validated.
- **Fail-closed**: standarden ved enhver ukjent input er nekt/avslå.
- **Kontrollmål**: ett av de 10 delte temaene [CLAIM-GOV-001].
- **Kanon**: den hash-låste litteraturkatalogen (180 verk) servert som RAG.
- **Hovedbok / vitne**: den append-only, hash-kjedede offentlige posten over
  hver bibliotek-påstand; uavhengig verifiserbar.
- **Byggestein**: en gjenbrukbar, forhåndsverifisert påstand + kode, konsumert via
  `import_bundle` / `use_code` med nivå og forbehold intakt.
- **PDP / PEP**: Policy Decision Point / Policy Enforcement Point; den
  fail-closede porten i handlings-stien.
- **TOGAF ADM**: Architecture Development Method; fasesyklusen denne håndboken
  avbilder byggesteinene på (§17).

## Appendiks E: hurtigreferanse for påstands-IDer

| ID | Hva den etablerer | Nivå |
|---|---|---|
| CLAIM-LIB-RAG-001 | 180 kanon-verk / 15 kolleksjoner / 171 verifisert / 9 drops | measured |
| CLAIM-LIB-RAG-002 | 9805 innholdsadresserte chunks, alle pushet live | measured |
| CLAIM-LIB-RAG-003 | live forsknings-endepunkter verifisert ende-til-ende | measured |
| CLAIM-GOV-001 | 5 rammeverk → 10 mål, full dekning, fail-closed | measured |
| CLAIM-COUPLE-001 | 4 skyer × 6 koblingsdimensjoner → 13 åpne standarder, hver skjøt leverandørnøytral, fail-closed | measured |
| CLAIM-SECOPS-001 | 8 sikkerhetsdrift-domener × 33 praksiser → 13 standarder, hvert driftsmål har et hjem, fail-closed | measured |
| THM-SCORE-001 | Brier-properness: ærlighet er optimalt (1028 par) | machine_checked |
| THM-ROUTE-001 | verifiseringsport-styrt kaskade-dominans (87 380 tabeller) | machine_checked |
| THM-VOTE-001/002 | best-of-n-identitet; amplifikasjon + ærlig degradering | machine_checked |
| THM-GAME-001 | minimax=maximin (6561 spill) | machine_checked |
| THM-STOP-001 | sekretær optimal stopping (n ≤ 20) | machine_checked |
| THM-JENSEN-001 | varians ≥ 0 (Jensen) | machine_checked |
| THM-CONF-001 | konform dekningskombinatorikk | machine_checked |
| DEMO-001 | konform runtime-demo (373/400, 0,9325 mot 0,9) | benchmarked |
| REMORA CLAIM-001 | 0,0 % usikker på 700-oppgaver (Wilson [0,00 %, 0,55 %]) | benchmarked |
| REMORA CLAIM-002 | 208/208 AgentHarm blokkert, FAR 0,0 % | externally_validated |
| REMORA CLAIM-009 | AROMER negativ: 43,0 %→30,7 % FA under nøytral metadata | benchmarked |

## Appendiks F: leseløyper etter rolle

- **Regulator / revisor:** §13 → §14 → §15 → Appendiks C → §24.
- **Enterprise-arkitekt:** §16 → §17 → §18 → §19.
- **Forsker / bygger:** §3 → §§8-11 → §12 → Appendiks B.
- **Nykommer:** §2 → §3 (kun de enkle linjene) → §7 → §23, følg så nysgjerrigheten.
- **Leder:** §1 → §23 → §24 (fem minutter, hele tesen og dens perimeter).

---

*Kompilert som en VeriClaim-syntese / håndbok. Hver sitering løses opp mot en
registrert, portverifisert påstand eller et hash-låst kanon-verk; registrene er
autoritative. Påstandsbasert programmering (Claim-Oriented Programming) og
VeriClaim av Stian Skogbrott.*

---
---

# Appendiks G: Fem gjennomgående case-studier

Hvert case følger samme bue: hva som *påstås*, hvilken *evidens* påstanden
trenger, hvordan påstanden *registreres*, hvordan *porten* ville feile ved drift,
hvordan den *fikses*, og hva som fortsatt er *ubevist*. De er illustrerende
sammensetninger, ikke rapporter om navngitte utrullinger. Disiplinen er poenget,
ikke tallene.

## Case 1: En banks AI-kundeserviceagent

- **Påstått.** «Agenten avslører aldri en annen kundes data.»
- **Evidens trengs.** Et red-team-benchmark av kryss-konto-sonder med målt
  lekkasjerate, pluss retrieval-filteret som håndhever konto-scoping.
- **Registrert.** `CLAIM` på `benchmarked`: lekkasjerate 0/N på sondesettet, med
  forbehold om at benchmarket er adversarisk-men-endelig og ikke dekker ny
  formulering.
- **Porten feiler når.** Noen redigerer markedssiden til å si «kan beviselig ikke
  lekke data», en påstand over evidensen. Porten flagger setningen.
- **Fikses ved.** Å omformulere til «ingen lekkasje observert over N adversariske
  sonder (se forbeholdet)», eller å produsere sterkere evidens.
- **Fortsatt ubevist.** At benchmarket reflekterer reell angriperatferd; at
  modellen oppfører seg likt på input utenfor sondefordelingen.

## Case 2: En intern utvikleragent med shell-tilgang

- **Påstått.** «Agenten kan ikke kjøre en destruktiv kommando uten menneskelig
  godkjenning.»
- **Evidens trengs.** Et runtime-policy-lag som feiler lukket, og et benchmark av
  utrygge-handling-forsøk med blokkert-rate (REMORA-resultatet).
- **Registrert.** `CLAIM` på `benchmarked`: 0.0 % utrygg-eksekvering på et
  700-oppgavers adversarisk sett, forbehold som navngir benchmarket og
  restfalsk-aksept-raten ærlig.
- **Porten feiler når.** Restfalsk-aksept-tallet stilltiende fjernes for å få
  kontrollen til å se perfekt ut. Portens «ingen slettede negativresultater»-regel
  og stale-string-sjekk fanger utelatelsen.
- **Fikses ved.** Å beholde negativresultatet i påstanden: en kontroll som
  navngir sin egen feilrate er mer troverdig enn en som skjuler den.
- **Fortsatt ubevist.** Sikkerhet mot angrep som ikke er representert i
  benchmarket; riktig konfigurasjon i et bestemt miljø.

## Case 3: Et høyrisiko klinisk beslutningsstøttesystem

- **Påstått.** «Hver regulatorisk plikt for dette høyrisikosystemet er adressert
  av en navngitt kontroll.»
- **Evidens trengs.** En kryssreferanse fra regimets krav til kontrollmål til
  konkrete kontroller med eiere og tester.
- **Registrert.** `CLAIM` på `measured`: full toveisdekning, verifisert
  fail-closed; forbehold om at kryssreferansen kartlegger *offentlig struktur*,
  ikke klausul-spesifikk innhold, og ikke er sertifisering.
- **Porten feiler når.** En kontroll fjernes, men dekningspåstanden oppdateres
  ikke, og dekningssjekkeren rapporterer et udekket mål og bygget stopper.
- **Fikses ved.** Å gjenopprette kontrollen eller ærlig innsnevre påstanden.
- **Fortsatt ubevist.** At hver kontroll er riktig *implementert* i den kliniske
  settingen. Det er per-utrullings-evidens (en assurance case), og klinisk
  validering er en separat, høyere terskel.

## Case 4: Et fler-sky enterprise-AI-kontrollplan

- **Påstått.** «Vår identitets- og policy-styring porter på tvers av AWS,
  Azure, GCP og OpenShift uten lock-in.»
- **Evidens trengs.** En koblingskryssreferanse som viser hver skys mekanisme
  koblet på delte åpne standarder, sjekket så hver skjøt er leverandørnøytral.
- **Registrert.** `CLAIM` på `measured`: 4 skyer × 6 dimensjoner på 13 åpne
  standarder, hver dimensjon forankret av en standard delt på tvers av minst to
  skyer; forbehold om at native tjenestenavn er gjeldende ved skrivetidspunkt.
- **Porten feiler når.** En dimensjon kobles til en enkelt-skys proprietær
  mekanisme uten delt standard: sjekkeren rapporterer en ikke-portabel skjøt.
- **Fikses ved.** Å koble den skjøten på en åpen standard (OIDC, SPIFFE,
  OPA/Rego) og behandle den native tjenesten som en adapter.
- **Fortsatt ubevist.** At en gitt utrulling er riktig konfigurert;
  kryssreferansen er et arkitektur-sporbarhetshjelpemiddel, ikke en
  sikkerhetsgjennomgang.

## Case 5: En RAG-assistent over regulatoriske dokumenter

- **Påstått.** «Assistenten svarer kun fra siterte interne kilder og nekter når
  den ikke har dekning.»
- **Evidens trengs.** En live-test av grunnede svar og av nektelser på
  utenfor-korpus-spørsmål, pluss retrieval-og-siterings-sjekken som håndhever
  det.
- **Registrert.** `CLAIM` på `measured`: grunnet-svar- og korrekt-nektelse-atferd
  verifisert ende-til-ende; forbehold om at grunning håndheves av retrieval pluss
  en siteringssjekk, ikke et bevis for at hver setning følger av kilden sin.
- **Porten feiler når.** README-en påstår at assistenten «svarer kun fra påstander»
  som en garanti. Den ærlige formuleringen (*designet for å* svare fra kilder,
  med grunning *håndhevet av* retrieval og en siteringssjekk) er det som
  passerer.
- **Fikses ved.** Å matche formuleringen til mekanismen.
- **Fortsatt ubevist.** At retrieval aldri overser en relevant kilde; at en
  målrettet prompt-injeksjon ikke kan påvirke et svar.

---

*På tvers av alle fem er mønsteret identisk: påstanden bærer evidensnivået sitt og
grensen sin, porten nekter drift og nekter beskrivelse over evidens, og det som er
ubevist oppgis i stedet for å skjules. Den nektelsen, å akkumulere ustøttet
betryggelse, er hele metoden.*

---
---

![Bakside](figures/no/cover-back.svg)

