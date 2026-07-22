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
