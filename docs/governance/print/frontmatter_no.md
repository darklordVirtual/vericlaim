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
