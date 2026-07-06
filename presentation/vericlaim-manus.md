**VeriClaim · Remora Research · Foredragsmanus**

# Sannhet er ikke noe man påstår.
**Den opptjenes.**

Manus til 26-sliders presentasjonen · ca. 25 minutter + spørsmål · Alle tall i manuset er registrerte claims med committede artefakter. Regi-notater i grått, talt tekst i grønn boks — les den ikke ordrett, eier den.

## S1 · Tittel 0:00 — la den stå i 10 sek

*Poenget: sett tesen før du sier hei.*

>
Alt dere ser i dag følger én regel: en påstand får ikke eksistere før den har gjort seg fortjent til det. Ikke i dokumentasjonen, ikke i koden, ikke i denne presentasjonen — hvert eneste tall dere ser her har et kryptografisk bevis bak seg. Det er ikke en metafor. Det er systemet.

## S2 · Problemet 0:45

*Publikum må kjenne smerten før løsningen gir mening.*

>
Vi bruker AI som skriver kode og dokumentasjon fortere enn noen rekker å verifisere den. Og hva skjer? README-en sier ett tall, benchmarken et annet. Sitater finnes ikke. Tallene var riktige — i fjor.

Se på figuren: en prompt går inn i en svart boks, og ut kommer en snakkeboble med en terning i. Vi kaster bokstavelig talt terning om sannhet, i systemer vi setter i produksjon. Testing fanger kode som oppfører seg feil. **Ingenting konvensjonelt fanger et prosjekt som beskriver seg selv feil.**

## S3 · REMORA 2:00

*Etablér arven: dette kommer fra beslutningssiden.*

>
Utgangspunktet vårt er REMORA — et forskningsrammeverk for Decision Intelligence. Før en AI-agent får utføre en handling, rutes beslutningen gjennom et deterministisk policygulv, konsensus mellom orakler og usikkerhetsruting, og hver beslutning etterlater en signert, hash-kjedet DecisionEnvelope. REMORA svarte på spørsmålet: *kan vi stole på denne beslutningen?* Men det åpnet et nytt: kan vi stole på *påstandene* systemet hviler på? Det spørsmålet ble til VeriClaim.

**Regi:** Ikke dvel — REMORA-detaljene kommer tilbake i S19 og S23.

## S4 · Credoet 3:15 — pause etter sitatet

>
«Every statement must earn the right to exist.» Les den én gang til. Det betyr: du får ikke skrive «37 % raskere» i dokumentasjonen. Du får skrive det når det finnes et committet bevis — og da skriver systemet praktisk talt tallet for deg.

## S5 · Arkitekturen 4:00

*Én tegning, fem sekunder per boks.*

>
Alt samles i ett claim-register — én sannhetskilde. Hver claim binder seks ting: evidens, tallene, artefaktene, litteraturen, kommandoen som gjenskaper beviset, og — like viktig — forbeholdet. En gate kjører i CI på hver commit. Grønn hvis alt stemmer overens. Rød med **eksakt fil og linje** hvis noe som helst drifter.

## S6 · Registeret 5:15

>
Dette er en ekte claim fra kodebasen. Legg merke til tre ting. Tallet 8,0584 står i registeret fordi et skript målte det og committet resultatfilen — ingen har tastet det. Nivået er «benchmarked» — ikke mer, ikke mindre enn det beviset bærer. Og caveaten — «korpuset er håndplukket, RLE kan ekspandere virkelige data» — er en **del av claimen**. Skryt uten forbehold er ikke lov å publisere.

## S7 · Livssyklusen 6:30

>
Rekkefølgen er hele disiplinen: evidens først, claim etterpå, dokument til slutt. Ankerfiguren viser modellen — dokumentet *henger* i tallet sitt, i en kjetting ned til en hashet evidensfil. Skriver noen om tallet uten å bytte beviset, ryker kjettingen, og gaten sier fra.

## S8 · Fail closed 7:30

*Dette er design-filosofien — bruk tid her.*

>
Legg merke til bommen: den er *nede* som standard. Systemet feiler med vilje. Et malformet register kunne lest som «null claims — alt vel»; hos oss er det byggstopp. En verifikator man ikke kan stole på er verre enn ingen, for den produserer falsk trygghet med god samvittighet.

- **Hvis spurt — «blir ikke det slitsomt?»:** Adopsjon er inkrementell: kjente avvik grandfathres i en baseline som WARN; kun *nye* avvik feiler.
## S9 · Evidensstigen 8:45

>
Ikke alt bevis er likt, og systemet tvinger deg til å si hvor godt du faktisk vet noe. Seks trinn, fra teoretisk argument til eksternt validert. Regelen har en asymmetri som er poenget: **degradering er alltid lov, oppgradering krever ny evidens.** Et register med bare seiere er per definisjon mistenkelig.

## S10 · Value tokens 10:00

>
Her er en subtil klasse feil: «Målet er 180 ms; faktisk måling 900 ms.» Et naivt system godkjenner setningen — 180 står jo der! Value-tokenet pinner *akkurat det* tall-literalet til registerfeltet. Etter dette finnes det bare ett tall som kan stå på den plassen i dokumentet: det målte.

## S11 · Litteraturmotoren 11:00

>
Fabrikkerte sitater er dødssynden i alt kunnskapsarbeid — og det LLM-er er best i verden på. Vår regel: bibliografisk metadata kommer **kun** fra registraren — Crossref og arXiv — aldri fra modellens hukommelse. Og se stemplene: tittel, forfatter, årstall. Alle tre. Den vakten er ikke teoretisk: den har avvist et 2025-kritikkpaper som utga seg for å være «Attention Is All You Need», en bokanmeldelse som utga seg for å være boken, og et kalibrerings-paper fra 1989 om *sensorer*. Frø uten registrar-treff dør. Ærlig.

## S12 · Biblioteket 12:30

>
Så skalerer vi fra ett prosjekt til mange. Verifisert kunnskap pakkes i forseglede kasser — bundles — med claim, evidens, kode og litteratur, adressert av sin egen hash. Endrer du én byte, er det en annen kasse. I dag: 90 gjeldende claims, 455 immutable versjoner, fire kilderepoer. Og hovedprinsippet: biblioteket er **distribusjon, aldri sannhet** — alt verifiseres lokalt hos mottakeren, offline.

## S13 · Harvest 13:45

>
Hvordan kommer kunnskap inn? Én kommando, en repo-URL — og så avgjøres tilliten av hva repoet *er*. Har det egen gate, må den være grønn. Har det en nedskrevet kurateringspolicy, høstes det under den — og evidensnivåer oppgraderes aldri i oversettelsen. Alt annet havner i karantene som «kandidat»: synlig i søk, merket uverifisert, umulig å importere som claim. Automatikk skal aldri kunne blåse opp tillit.

## S14 · Kode-vendoring 15:00

>
Og her blir det programmering: koden som *produserte* et bevis kan hentes byte-eksakt inn i prosjektet ditt, med en generert bindingstest. Redigerer du én linje i den importerte koden, feiler din egen testsuite. Vil du forke? Greit — men da sletter du testen, og valget er synlig i historikken.

## S15 · Reproduce 15:45

>
Tvillingavtrykkene: i går og i dag, samme fingeravtrykk. `vericlaim reproduce` kjører hvert evidensskript på nytt og krever byte-identisk resultat. Det skiller «tallet var sant da vi målte» fra «tallet er sant **nå**» — og i vårt eget oppsett innebærer det faktisk å re-kjøre en teorembevis-kjerne.

## S16 · Truth layer 16:30

>
Alt dette lever også på kanten, som en levende tjeneste: semantisk søk over claims, en hash-kjedet ledger, et innholdsadressert evidenshvelv, en offentlig passport-side — og et orakel med én uvanlig egenskap: det **nekter å svare** når ingen claim dekker spørsmålet. Nektelsen er ikke en bug. Den er hele poenget.

## S17 · MCP 17:15

>
Og agentene kobles på samme disiplin: Claude spør registeret via seks skrivebeskyttede verktøy i stedet for å svare fra hukommelsen. Merk asymmetrien: et søketreff er aldri bevis. En claim er troverdig fordi gaten verifiserte den — ikke fordi den dukket opp i et søk.

## S18 · Tillitsgrafen 18:00 — rask

>
Zoomer vi ut, er hele systemet én kjede: claim, evidens, artefakt, litteratur, hash, vitne, ledger. Hvert ledd peker på beviset for det neste. Bryt ett — hvor som helst — og gaten navngir bruddet.

## S19 · Komposisjonen 18:30

>
Nå lukker vi sirkelen til REMORA. DecisionEnvelope sa: denne beslutningen er sporbar. VeriClaim legger til: og påstandene den hviler på er intakte, reproduserbare og ærlig graderte. VeriClaim er evidensmotoren som kompletterer REMORAs beslutningsmotor — samme disiplin, to lag.

## S20–21 · Matematikken 19:00

>
To minutter matematikk, fordi den bærer alt. Først kryptografien: hver ledger-rad hasher den forrige — én endret rad, og hvert ledd etterpå brister synlig, som i figuren. Og fordi den som eier databasen kunne bygget hele kjeden på nytt, vitnes kjedehodene i offentlig git-historikk og re-verifiseres *klient-side*. Seksten vitner hittil. Alle forlenget.

Så teoremene — og her er spillereglene uvanlige: modellen får *foreslå* matematikk, men en maskin dømmer. Tjue teoremer er bevist i Lean 4 — universelt, for alle proposisjoner og alle naturlige tall — med aksiom-fotavtrykket registrert per bevis. Og kjernen har faktisk avvist ett av mine forslag underveis. Det er ikke flaut. Det er kontrakten.

## S22 · Sammenligningen 21:00 — kort

>
README-er og wikier håndhever ingenting. Fagfellevurdering håndhever sitering, litt proveniens — men ingen hash-binding og ingenting feiler automatisk. Kolonnen lengst til høyre er den som mangler i bransjen: fail closed.

## S23 · TrustGate 21:45 — casen, bruk tid

>
Beviser dette noe i praksis? Vi bygde TrustGate: en portvakt som *komponerer* to garantier fra to uavhengige kilder i biblioteket. Konform prediksjon fra teorembatteriet gir hvert svar et intervall med dekningsgaranti. REMORAs anytime-valide monitor overvåker feilraten kontinuerlig — og fordi grensen er tidsuniform, er det *matematisk lovlig* å sertifisere på et datadrevet tidspunkt. Kjøringen: 400 runder, dekning 373 av 400 mot et 0,90-mål, sertifisert i runde 94, null alarmer. Og underveis fanget byggingen en ekte defekt i biblioteket vårt — som ble fikset ved å gjøre påstanden sann, ikke ved å myke opp teksten. Systemet disiplinerer sin egen skaper.

## S24 · Filosofien 23:30 — stillhet etterpå

>
Truth is not asserted. Truth is earned.

## S25 · Begrensningene 24:00 — ikke hopp over

>
Og fordi dette er et anti-overclaim-verktøy, må jeg være presis om grensen. VeriClaim beviser intern konsistens, reproduksjon, proveniens, dokument- og sitatintegritet. Det beviser **ikke** at en benchmark ligner produksjon, at en algoritme er optimal, eller at en setning er semantisk sann. Den grensen står i hver eneste caveat. Og systemet har fanget mine egne overdrivelser tre ganger under byggingen — det er håndhevelsen, demonstrert på skaperen.

## S26 · Avslutning 25:00

>
Alt dere har sett er offentlig: tre repoer på GitHub, truth-layeret live, ledgerne forankret. Ikke ta mitt ord for noe av det — kjør gaten selv. Det er hele poenget. Takk.

## Q&A-beredskap

- **«Hva koster dette i utviklerfart?»** — Evidensskriptet er ofte testen du burde skrevet uansett; baseline-mekanismen gjør adopsjon inkrementell.
- **«Kan ikke eieren jukse?»** — Innenfor repoet: gaten fanger det. Historieomskriving: vitnene i offentlig git-historikk fanger det, klient-side. Det som gjenstår er evidens manipulert *før* første commit — det står ærlig i begrensningene.
- **«Fungerer det med LLM-utvikling?»** — Det er bygget for det: en Claude-skill håndhever disiplinen, og hele teorembiblioteket er modell-seedet og maskinverifisert — inkludert avvisningene.
- **«EverClaim eller VeriClaim?»** — «VeriClaim» er merke-/metodikknavnet i denne presentasjonen; selve repoet, pakken og CLI-en heter `vericlaim` (små bokstaver). Hold presentasjonen konsistent, men ikke påstå at repoene bruker stor V.
