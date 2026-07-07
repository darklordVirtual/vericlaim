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
