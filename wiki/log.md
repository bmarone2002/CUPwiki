# Log — LLM Wiki CUP

Cronologia append-only delle operazioni sulla wiki.

## [2026-07-22] setup + ingest pilota | Berbenno c. WindTre (Telefonia)
- Rinominata la cartella dei materiali originali in `raw/` (Cerchio 1) e corretto il nome cartella con `:`.
- Creata la struttura `wiki/` curata (entities, topics, concepts, sources, contenziosi, briefings, templates) + `CLAUDE.md`.
- **Ingest** della memoria `raw/…/TELEFONIA/WIND/BERBENNO C- WIND TRE_revMaria.docx`.
- Pagine create:
  - entities: [[Comune di Berbenno (BG)]], [[WindTre]], [[Archivia Solution]], [[Avv. Maria Voccia De Felice]], [[AGCOM]]
  - topic: [[servizi-di-rete-telefonia]]
  - concepts: [[Soggettività passiva in via mediata]], [[Utilizzo materiale e accesso virtuale (VULA)]], [[Natura tributaria del CUP]], [[Metodo induttivo su dati AGCOM]]
  - sources: [[2026-05-01 Cass SS.UU. 12225 — natura tributaria CUP]], [[2026-04-28 Cass 11479 — VULA Wind]], [[2025-05-06 Trib Piacenza 207 — Vodafone soggettività mediata]], [[2025-11-25 Trib Bergamo 1523 — Fastweb]], [[2025-02-20 Trib Treviso 240 — appello]], [[2026-05-14 Memoria Berbenno c. WindTre (GdP Bergamo)]], [[Merciari — Soggettività passiva in via mediata (telefonia)]]
  - contenzioso: [[Comune di Berbenno c. WindTre — GdP Bergamo RG 3481-2025]]
  - briefing: [[Strategia difensiva — CUP servizi di rete (telefonia)]]
  - template: [[memoria-di-costituzione]]
- ⚠ Rilevati refusi nella memoria raw (riferimenti a "Cazzano di Tramigna" in atto intestato a Berbenno; data richiesta utenze divergente 12/11/2024 vs 17/07/2025). Registrati in [[2026-05-14 Memoria Berbenno c. WindTre (GdP Bergamo)]], da sanare.

## [2026-07-22] git init | versionamento
- Inizializzato repository git + `.gitignore`; primo commit dell'intero progetto (raw + wiki + CLAUDE.md).

## [2026-07-22] redazione memoria (demo) | Berbenno c. Vodafone
- **Ingest** dell'atto di citazione avversario `raw/…/TELEFONIA/VODAFONE/CITAZIONE OPPOSIZIONE VODAFONE C- COM. BERBENNO CUP 21-22-23-24.pdf`.
- Create: entity [[Vodafone]] (con controtesi + precedenti avversari), contenzioso [[Comune di Berbenno c. Vodafone — Trib. Bergamo (ord.) 2025]].
- Eseguito workflow `redazione memoria` → generata [[BOZZA — Comparsa Berbenno c. Vodafone]] (risposta ai 4 motivi, da validare).
- ⚠ Segnalato **rischio motivo IV** (sanzione 100% vs 30% ex art. 58 Reg. comunale) → verificare Regolamento ed eventuale autotutela.
- Arricchito il concept [[Soggettività passiva in via mediata]] con la sezione "Controtesi degli operatori".

## [2026-07-22] industrializzazione | pipeline deduplica + conversione corpus
- Creato ambiente `.venv` (pypdf) e script riusabile `tools/convert_and_dedup.py`.
- Eseguita pipeline su `raw/` → proiezione testuale in `raw_text/` + inventario `tools/manifest.csv`.
- **Numeri reali del corpus:**
  - 1.014 file totali → **592 unici** (per hash sha256), **422 duplicati esatti** (~42%: forte sovrapposizione tra le due cartelle originali, come previsto).
  - **585 convertiti** in testo (docx via textutil, pdf via pypdf, pptx via estrazione XML) = **11 MB** di testo in `raw_text/`.
  - **5 PDF da OCR** (scansioni, 0 caratteri): `Consiglio-di-Stato-Sez.V-8190-2025`, `RG_7546_2025_Decreto_PP`, `Scan2025-04-18`, `TAR_LAZIO`, `sentenza viadotti 22-07-2022`.
  - **2 file corrotti**: `AGCOM RELAZIONE ANNUALE 2024.pdf` (vuoto), `CITAZIONE OPPOSIZIONE FASTWEB COM. BERBENNO.pdf` in /VODAFONE (stream troncato → recuperare la copia integra).
- `.venv/` e `raw_text/` esclusi da git (artefatti derivati, rigenerabili); `manifest.csv` versionato come inventario.

## [2026-07-22] ingest batch 1 Telefonia | Ivrea · Bolzano · MEF · Fastweb Berbenno
- HITL confermato su 5 documenti prioritari (non massivo).
- **Sources:** [[2025-09-29 Trib Ivrea 1255 — WindTre soggettività mediata]], [[2025-10-15 Trib Bolzano 908 — WindTre WLR]], [[2024-04-08 Trib Bolzano 431 — Vodafone soggettività mediata]], [[2026-05-22 Circolare MEF 1-DF — natura tributaria CUP]], [[2025-11-18 Note finali Berbenno c. Fastweb (Trib. Bergamo)]].
- **Entities:** [[Comune di Bosconero (TO)]], [[Comune di San Lorenzo di Sebato (BZ)]], [[Abaco]], [[Fastweb]].
- **Contenzioso:** [[Comune di Berbenno c. Fastweb — Trib. Bergamo RG 2320-2025]] (⚠ verificare nesso con [[2025-11-25 Trib Bergamo 1523 — Fastweb]]).
- Aggiornati: [[Natura tributaria del CUP]], [[WindTre]], [[Vodafone]], playbook [[Strategia difensiva — CUP servizi di rete (telefonia)]], `index.md`.
- Nota: Bolzano 431/2024 è **Vodafone** (non Wind), stesso Comune di Bolzano 908/2025.

## [2026-07-23] ingest batch 2 Telefonia | Piacenza 350 · Capriate · Montefalco · stub Napoli/Bergamo · gap Fastweb
- **Verified:** [[2025-07-16 Trib Piacenza 350 — WindTre appello]] (Vigolzone).
- **Claimed (PDF assente in raw):** [[2026-04-13 Trib Napoli 5948 — WindTre utilizzo materiale]], [[2026-03-21 Trib Bergamo 289 — Vodafone]] — massime da citazioni in memorie; da sostituire con PDF.
- **Memorie + contenziosi:** [[2026-07-16 Memoria Capriate c. WindTre (GdP Bergamo)]] / [[Comune di Capriate San Gervasio c. WindTre — GdP Bergamo RG 2714-2026]]; [[2026-07-16 Memoria Montefalco c. WindTre (CGT Perugia)]] / [[Comune di Montefalco c. WindTre — CGT Perugia 2026]].
- **Entities:** [[Comune di Capriate San Gervasio (BG)]], [[Comune di Montefalco (PG)]], [[Comune di Vigolzone]].
- **Gap chiuso:** [[2025-11-25 Trib Bergamo 1523 — Fastweb]] = esito di RG 2320/2025 → contenzioso Fastweb marcato `definito` / `favorevole-ente` (⚠ spese compensate anche per regolamento di altro ente depositato).
- Playbook + `index.md` aggiornati. **Nessun commit** (strutturazione in corso).

## [2026-07-27] ingest batch 3 Telefonia | Francavilla · Palagiano · dossier Vodafone
- **Partisan / controparte:** [[2025-12-01 Rassegna Vodafone — precedenti avversi CUP telefonia]] per mappare i precedenti spesi dagli operatori (Vicenza, Padova, Perugia, Rovigo, Cass. SS.UU. 8628/2020, Cons. Stato 2976/2021).
- **Memorie + contenziosi:** [[2026-07-27 Memoria Francavilla al Mare c. WindTre (CGT Chieti)]] / [[Comune di Francavilla al Mare c. WindTre — CGT Chieti 2026]]; [[2026-07-27 Memoria Palagiano c. Vodafone (bozza con refusi)]] / [[Comune di Palagiano c. Vodafone — Trib. Taranto 2026]].
- **Entities:** [[Comune di Francavilla al Mare]], [[Comune di Palagiano]], [[Risco S.r.l.]].
- Francavilla aggiunge due elementi utili: **concessionario diverso da Abaco** e replica specifica sulla **annualità 2025** in foro tributario.
- Palagiano registrato come **bozza non pulita**: placeholder, R.G. assente e refuso anagrafico Vodafone/Fastweb mantenuti come contraddizioni da verificare, non normalizzati in silenzio.
- Aggiornati: [[Vodafone]], [[Soggettività passiva in via mediata]], playbook [[Strategia difensiva — CUP servizi di rete (telefonia)]], `index.md`.

## [2026-07-27] lint Telefonia | qualità prima di allargare materie
- Scelta: **non** aggiungere subito batch 4; consolidare coerenza del filone già popolato.
- **Correzioni applicate:**
  - Stub [[2026-03-21 Trib Bergamo 289 — Vodafone]] e [[2026-04-13 Trib Napoli 5948 — WindTre utilizzo materiale]]: tolto `orientamento: consolidato` con `confidence: claimed` (evitare overclaim finché manca PDF).
  - [[2026-05-01 Cass SS.UU. 12225 — natura tributaria CUP]]: chiarito che il PDF manca in `raw/`, ma il principio è ancorato alla [[2026-05-22 Circolare MEF 1-DF — natura tributaria CUP]].
  - Topic [[servizi-di-rete-telefonia]] allineato ai 7 contenziosi + link entity operatori.
  - [[WindTre]] → aggiunto [[Comune di Francavilla al Mare c. WindTre — CGT Chieti 2026]].
  - [[Soggettività passiva in via mediata]] → link a [[Merciari — Soggettività passiva in via mediata (telefonia)]] (era orfano dai concept).
  - Playbook: link wiki per Napoli/onere prova, Bergamo 289, rassegna partisan Vodafone.
- **Aperti (non risolvibili senza nuovi raw):**
  - PDF Napoli 5948 e Bergamo 289.
  - PDF integrale Cass. SS.UU. 12225.
  - R.G. da completare: Montefalco, Francavilla, Palagiano.
  - Refusi già tracciati: Cazzano/Berbenno; Palagiano CF Fastweb; sanzione 100% vs 30% Berbenno/Vodafone; regolamento altro ente in Fastweb 1523.
- **Nessun commit** (strutturazione ancora in corso).


## [2026-07-27] avvio filone Idrico | Capriate c. UniAcque
- Scelta strategica: aprire **Idrico** prima di `Gas`, perché nel raw è più ricco (dottrina + giurisprudenza + memorie).
- Creati topic e concept: [[servizi-di-rete-idrico]], [[Gestore del servizio idrico integrato non esente dal CUP]], [[Due distinti servizi di rete nel servizio idrico integrato]].
- Ingerite sources: [[Merciari — Aziende municipalizzate SII pagano il CUP]], [[Merciari — Due distinti servizi di rete nel SII]], [[2024-11-22 Trib Rovigo 889-2023 — Acquevenete esenzione devoluzione]], [[2026-05-04 Memoria Capriate c. UniAcque (Trib. Bergamo)]].
- Entity / contenzioso: [[UniAcque S.p.A.]], [[Comune di Capriate San Gervasio c. UniAcque — Trib. Bergamo RG 1928-2026]].
- Nodo giuridico centrale del pilota: **in house non equivale a esenzione**; **restituzione di reti già pubbliche ≠ devoluzione gratuita**.
- `index.md` e entity [[Comune di Capriate San Gervasio (BG)]] aggiornati.

## [2026-07-27] batch 2 Idrico | Aquara · Palagiano
- Aggiunti due casi idrici ulteriori per evitare che il filone resti ancorato al solo precedente UniAcque/Capriate.
- **Sources:** [[2026-07-27 Memoria Aquara c. ASIS (Trib. Salerno)]], [[2026-07-27 Memoria Palagiano c. Acquedotto Pugliese (Trib. Taranto)]].
- **Entities:** [[Comune di Aquara]], [[ASIS Salernitana Reti e Impianti S.p.A.]], [[Acquedotto Pugliese S.p.A.]].
- **Contenziosi:** [[Comune di Aquara c. ASIS — Trib. Salerno 2026]], [[Comune di Palagiano c. Acquedotto Pugliese — Trib. Taranto 2026]].
- Aquara aggiunge sottotemi utili: strade provinciali, cumulo materiale sanzioni, distinzione interessi pregressi/oneri futuri.
- Palagiano rafforza il blocco AQP: reti pubbliche, ruolo dell'AIP, restituzione ≠ devoluzione gratuita, accertamento induttivo per mancate dichiarazioni.
- `index.md` e [[Comune di Palagiano]] aggiornati.

## [2026-07-27] avvio filone Gas | Bitritto · Cinisello Balsamo
- Aperto il topic [[servizi-di-rete-gas]] con due concept riusabili: [[Gestore della distribuzione gas soggetto passivo del CUP]] e [[Devoluzione gratuita parziale degli impianti gas non basta]].
- Ingerite le memorie [[2026-07-03 Memoria Bitritto c. Italgas Reti (Trib. Bari)]] e [[2026-07-27 Memoria Cinisello Balsamo c. Unareti (CGT Milano)]].
- Create le entities [[Comune di Bitritto]], [[Comune di Cinisello Balsamo]], [[Italgas Reti S.p.A.]], [[Unareti S.p.A.]].
- Creati i contenziosi [[Comune di Bitritto c. Italgas Reti — Trib. Bari RG 5469-2026]] e [[Comune di Cinisello Balsamo c. Unareti — CGT Milano 2026]].
- Gas si differenzia nettamente da Telefonia: qui la separazione infrastruttura/vendita è strutturale e il focus è sul **gestore titolare dell'affidamento** e sulle esenzioni da devoluzione solo parziale / non gratuita.
- `index.md` aggiornato.

## [2026-07-27] lint trasversale multi-materia | Telefonia · Idrico · Gas
- Verificati link, naming, metadati e stub sui tre filoni aperti.
- Correzione azionabile applicata: creato [[2026-04-24 Memoria Capriate c. Italgas Reti (Trib. Bergamo)]] per chiudere un link rotto nel concept gas.
- Esito: nessun `claimed + orientamento consolidato`; nessun link rotto residuo rilevato dal controllo esatto.
- Restano aperti solo gap sostanziali (R.G. mancanti, PDF stub da acquisire, refusi già registrati), non incoerenze strutturali della wiki.

## [2026-07-27] avvio filone Energia elettrica | Bitritto c. E-Distribuzione
- Corpus minimo disponibile: una sola memoria, ma sufficiente per aprire il filone.
- Creati topic/concept: [[servizi-di-rete-energia-elettrica]], [[Rettifica dell'autodichiarazione utenze nel CUP energia]].
- Ingerita source: [[2026-07-27 Memoria Bitritto c. E-Distribuzione (CGT Bari)]].
- Entity / contenzioso: [[E-Distribuzione S.p.A.]], [[Comune di Bitritto c. E-Distribuzione — CGT Bari 2026]].
- Nodo giuridico del pilota: il Comune può riconoscere un pagamento parziale in autotutela ma mantenere il residuo per sottodichiarazione delle utenze/POD.
- `index.md` aggiornato.

## [2026-07-27] ingest lotto Gas | filone Italgas Campania
- Letti e strutturati i casi [[Comune di Sessa Aurunca c. Italgas Reti — Trib. Santa Maria Capua Vetere 2026]] e [[Comune di Casagiove c. Italgas Reti — Trib. Santa Maria Capua Vetere 2026]].
- Create le source [[2026-07-27 Memoria Sessa Aurunca c. Italgas Reti (Trib. Santa Maria Capua Vetere)]] e [[2026-06-18 Memoria Casagiove c. Italgas Reti (Trib. Santa Maria Capua Vetere)]].
- Nuovo concept trasversale: [[Autoriduzione unilaterale del CUP gas da parte del gestore]].
- Aggiornati [[Italgas Reti S.p.A.]] e [[servizi-di-rete-gas]] per riflettere il pattern seriale: esenzione per devoluzione parziale + contestazione `Punto Fisco` + auto-riduzione del dovuto.
- `index.md` aggiornato.

## [2026-07-27] ingest lotto Gas | Portici + Palagiano
- Ingerito il caso [[GE.SE.T. Portici c. Italgas Reti — Trib. Napoli RG 14673-2025]] con focus su concessionario esterno, `Punto Fisco` e sanzione per infedele dichiarazione.
- Ingerito il caso [[Comune di Palagiano c. Italgas Reti — Trib. Taranto 2026]]; segnalati in pagina i refusi/contrasti interni al raw senza sovrascriverli.
- Nuovo concept: [[Sanzione per infedele dichiarazione CUP distinta dall'omesso versamento]].
- Aggiornati [[Autoriduzione unilaterale del CUP gas da parte del gestore]], [[Italgas Reti S.p.A.]], [[Comune di Palagiano]], [[servizi-di-rete-gas]].
- `index.md` aggiornato.

## [2026-07-27] briefing | Strategia difensiva gas
- Creato [[Strategia difensiva — CUP servizi di rete (gas)]] come playbook operativo del filone gas, con mappa motivo → risposta → precedenti.
- Consolidati i pattern seriali del filone [[Italgas Reti S.p.A.]]: esenzione per devoluzione parziale, autoriduzione del canone, contestazione `Punto Fisco`, sanzioni, difetto di giurisdizione.
- Aggiornato [[servizi-di-rete-gas]] con collegamento al playbook.
- `index.md` aggiornato.

## [2026-07-27] briefing | Strategia difensiva energia elettrica
- Verificato che il corpus `Energia` oggi contiene un solo raw strutturato (Bitritto c. E-Distribuzione).
- Creato il concept [[Stima prudenziale delle utenze POD su dati ARERA]] a partire dal metodo difensivo emerso nel caso Bitritto.
- Creato [[Strategia difensiva — CUP servizi di rete (energia elettrica)]] come playbook iniziale di materia.
- Aggiornati [[Comune di Bitritto]], [[servizi-di-rete-energia-elettrica]] e `index.md`.

## [2026-07-27] ingest lotto Idrico | Portici + Cinisello + Palestro
- Ingeriti i casi [[Comune di Portici c. GORI — Trib. Napoli RG 15429-2025]], [[Comune di Cinisello Balsamo c. CAP Holding — CGT Milano 2026]], [[Comune di Palestro c. Pavia Acque — Trib. Pavia RG 1584-2026]].
- Create le source [[2025-10-03 Comparsa Portici c. GORI (Trib. Napoli)]], [[2026-07-08 Memoria Cinisello Balsamo c. CAP Holding (CGT Milano)]], [[2026-07-03 Memoria Palestro c. Pavia Acque (Trib. Pavia)]].
- Nuovo concept trasversale: [[Rifiuto del gestore idrico di dichiarare le utenze e stima presuntiva]].
- Aggiornati [[servizi-di-rete-idrico]], [[Comune di Portici (NA)]], [[Comune di Cinisello Balsamo]] e `index.md`.
- Il filone idrico passa da pilota a materia multi-caso con più gestori (UniAcque, ASIS, AQP, GORI, CAP, Pavia Acque).

## [2026-07-27] briefing | Strategia difensiva idrico
- Creato [[Strategia difensiva — CUP servizi di rete (idrico)]] come playbook operativo del filone SII.
- Mappa difensiva strutturata per motivi ricorrenti: in house, uso gratuito / restituzione, devoluzione, doppio servizio acqua-fognatura, metodo presuntivo, concessionario, sottosuolo, giurisdizione.
- Aggiornato [[servizi-di-rete-idrico]] con collegamento al playbook.
- `index.md` aggiornato.

## [2026-07-27] mcp | client-ready + test runner
- Esclusi `log` e `index` da `search()` / `list_related()` in `mcp-server/server.py`.
- Aggiunto `mcp-server/claude_desktop_config_cup.json` (config pronta per wiki CUP reale).
- Aggiunto `tests/run_mcp_tests.sh` (smoke + demo operativa).
- `.gitignore`: `.venv-mcp/`, `tools/uv-bin/`, `tools/uv-install.sh`.
- Aggiornato `mcp-server/README.md` con sezione setup rapido repo CUP.

## [2026-07-27] briefing | MCP locale vs hostato
- Creato [[MCP — accesso operativo alla wiki CUP]]: decisione operativa = **locale sufficiente oggi**, hosting solo per team/multi-utente.
- Aggiornato `index.md`.

## [2026-08-20] docs | README collaborativo
- Riscritto `README.md` come onboarding per lavoro a quattro mani (clone → Cursor → CLAUDE.md → workflow).
- Chiarito: wiki CUP in `wiki/` (non `example-wiki/`); MCP opzionale; regole git/HITL/raw immutabili.
- Allineato `index.md`: elenco completo dei 4 playbook di materia + briefing MCP.

## [2026-08-20] docs | README — mappa materiale CUP
- Aggiornate sezioni *Stato* e *Cosa manca*: temi giuridici per materia, numeri wiki verificati, confronto `wiki/` vs volumi `raw/`, esempi di ingest residuo, gap operativi separati dal corpus.
