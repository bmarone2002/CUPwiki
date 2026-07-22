# LLM Wiki CUP — Assistente per il Canone Unico Patrimoniale (servizi di rete)

Questo file È la configurazione del sistema. Dice all'assistente com'è strutturata questa wiki, quali convenzioni seguire e quali workflow eseguire. Co-evolve con l'uso. Vedi `BLUEPRINT.md` per il razionale generale.

## Identità

Questa wiki è la **memoria operativa di Archivia Solution S.p.A.** per il supporto agli Enti Locali (Comuni, Province, Città Metropolitane) nella gestione, accertamento e contenzioso del **Canone Unico Patrimoniale (CUP)**, con focus sui **canoni per i servizi di rete** (telefonia/TLC, energia elettrica, gas, servizio idrico integrato) e sugli altri presupposti (pubblicità/affissioni, occupazioni di suolo, passi carrabili, mercatale, viadotti).

L'obiettivo è che l'assistente possa: (1) **rispondere** a quesiti su normativa, giurisprudenza e prassi CUP citando sempre le fonti; (2) **redigere memorie, comparse e pareri** riusando gli argomenti e i precedenti già consolidati; (3) **accumulare** ogni nuovo caso come conoscenza collegata, così che "tutto quello che sappiamo su X" (un operatore, un Comune, un motivo di ricorso, una sentenza) sia sempre a una domanda di distanza.

È una LLM Wiki in **markdown puro** (niente DB, niente RAG): privilegia time-to-value, leggibilità, conoscenza compilata e citabilità sopra il retrieval semantico.

## Architettura a 3 cerchi

1. **Raw** (immutabile): i documenti originali in `raw/` (sentenze, normativa, articoli, memorie, quesiti, slide). L'assistente **legge ma non modifica mai** i raw.
2. **Wiki** (`wiki/`): pagine markdown curate, create e mantenute dall'assistente. È il delivery layer del valore.
3. **Index/metadata** (futuro): un indice/ricerca semantica sul corpus grezzo di giurisprudenza, da aggiungere solo quando il volume lo richiede (vedi `BLUEPRINT.md` §1).

## Struttura della repo

```
llm-wiki-cup/
├── CLAUDE.md                 ← questo file
├── raw/                      ← Cerchio 1: originali immutabili
│   ├── giurisprudenza-normativa-generale/
│   └── Memorie passate + template/
│       ├── CONTENZIOSO_Maria_Rosa/{ENERGIA,GAS,IDRICO,TELEFONIA}/...
│       ├── CUP_ARTICOLI MERCIARI/
│       ├── CUP_SENTENZE/
│       └── SLIDE/
└── wiki/                     ← Cerchio 2: markdown curato
    ├── index.md · log.md
    ├── entities/    ← Comuni, Operatori, Avvocati, Autorità, Tribunali
    ├── topics/      ← i settori/materie (telefonia, idrico, gas, energia, pubblicità…)
    ├── concepts/    ← i blocchi-argomento giuridici riusabili (il motore)
    ├── sources/     ← 1 file = 1 sentenza/norma/articolo/memoria (massima + sintesi + link al raw)
    ├── contenziosi/ ← 1 caso = Comune vs Operatore (stato, atti, esito) [= "project"]
    ├── briefings/   ← sintesi/playbook derivati da N pagine (es. strategia difensiva per materia)
    └── templates/   ← scheletri di memoria, comparsa, parere
```

## Tipi di pagina

| `type` | Cos'è | Cartella | Bias tipico |
|---|---|---|---|
| `entity` | Una "cosa" del mondo: Comune, Operatore di rete, Avvocato, Autorità (ARERA/AGCOM/MEF), Tribunale. | `entities/` | neutral |
| `topic` | Una materia/settore CUP. | `topics/` | neutral |
| `concept` | Conoscenza derivata: un **argomento giuridico riusabile** (una tesi, un orientamento, un criterio di calcolo). | `concepts/` | internal |
| `source` | 1 documento ingerito: sentenza, norma, circolare, articolo, **memoria**. Massima + sintesi + link al raw. | `sources/` | dipende |
| `contenzioso` | Un *caso* (project): un Comune contro un Operatore davanti a un giudice, con stato ed esito. | `contenziosi/` | internal |
| `briefing` | Output di valore filato come pagina: playbook/strategia per materia, sintesi comparativa. | `briefings/` | internal |

### Regola fondamentale: `entity` ≠ `contenzioso`

Una cosa del mondo e un *nostro caso* su quella cosa sono **due pagine distinte, linkate**. `entities/WindTre.md` (fatti stabili sull'operatore, ricorre in decine di cause) è distinto da `contenziosi/Comune di Berbenno c. WindTre — GdP Bergamo RG 3481-2025.md` (il singolo caso, datato, con esito). La pagina dell'operatore serve **tutti** i contenziosi contro di esso senza duplicarsi.

## Convenzioni di naming

- Entity in forma naturale: `Comune di Berbenno.md`, `WindTre.md`, `Avv. Maria Voccia De Felice.md`.
- Topic in kebab-case: `servizi-di-rete-telefonia.md`.
- Concept in forma naturale descrittiva: `Soggettività passiva in via mediata.md`.
- Source (sentenze/atti) con prefisso data ISO: `YYYY-MM-DD <corte> <numero> — <oggetto>.md`.
- Contenzioso: `<Comune> c. <Operatore> — <Giudice> <RG/anno>.md`.
- Omonimia Comuni: disambigua con la provincia: `Comune di San Giorgio (BA).md`.

## Frontmatter

Campi comuni a tutti i tipi:

```yaml
---
type: entity            # entity | topic | concept | source | contenzioso | briefing
materia: [telefonia]    # una o più materie CUP (vedi tassonomia)
tags: [soggettività-passiva-mediata, comma-831]
sensitivity: internal   # public | internal | confidential | restricted
updated_at: 2026-07-22
---
```

Campi aggiuntivi per `source` (traccia provenienza e qualità):

```yaml
---
type: source
subtype: sentenza       # sentenza | ordinanza | norma | circolare | articolo | memoria | quesito
source_path: "../../raw/…/file.pdf"   # link al Cerchio 1
corte: "Cass. SS.UU."   # organo giudicante (per la giurisprudenza)
numero: "12225/2026"
data_sentenza: 2026-05-01
esito: favorevole-ente  # favorevole-ente | favorevole-operatore | misto | n/a
bias: neutral           # neutral | internal | partisan
confidence: verified    # verified | estimated | claimed
orientamento: consolidato   # consolidato | controverso | isolato | superato
superseded_by:          # [[pagina]] se l'orientamento è stato superato
ingested_at: 2026-07-22
tags: [...]
sensitivity: public
---
```

## Tassonomia

**Materie (`materia`)** — vocabolario controllato:
`telefonia`, `energia-elettrica`, `gas`, `idrico`, `pubblicita-affissioni`, `passi-carrabili`, `occupazioni-suolo`, `mercatale`, `viadotti-autostrade`, `antenne-ripetitori`.

**Tag argomentativi** (esempi, cresce con l'uso, nuovi tag → HITL):
`soggettività-passiva-mediata`, `comma-831`, `natura-tributaria`, `giurisdizione`, `contraddittorio-preventivo`, `utilizzo-materiale`, `accesso-virtuale-vula`, `metodo-induttivo`, `dati-agcom`, `interpretazione-autentica-dl146-2021`, `onere-prova`, `prescrizione`, `sanzioni`, `minimo-forfettario`, `coefficiente-arera`.

## Sistema metadata (i 3 assi di qualità + il tempo)

- **`bias`**: `neutral` (sentenze, normativa, prassi di terzi); `internal` (nostre memorie, pareri, concept/tesi difensive); `partisan` (materiale di controparte, es. rassegne degli operatori). *Marcare `partisan` è utile: serve a modellare le controtesi.*
- **`confidence`** (la certezza cresce salendo): `verified` (fonti primarie: legge, Cassazione/SS.UU., sentenza depositata); `estimated` (dottrina, interpretazioni, stime di gettito); `claimed` (tesi di parte non ancora avallata, affermazioni di controparte).
- **`sensitivity`**: le memorie e i dati dei Comuni (importi, C.F./PEC di funzionari, numeri di RG) sono `confidential`. Sentenze, normativa e articoli pubblici sono `public`. Default `internal` in dubbio; mai assumere `public` senza evidenza. **Rilievo GDPR/PA.**
- **`orientamento`** (per la giurisprudenza): `consolidato` / `controverso` / `isolato` / `superato`. Una pronuncia superata **resta** in wiki (archivio storico) ma va marcata `superseded_by: [[…]]` e de-prioritizzata nelle risposte.

## Densità di link = valore

**Linka aggressivamente con `[[Pagina]]`.** Ogni tesi/claim importante cita la fonte: `l'accesso VULA è occupazione mediata ([[2026-04-28 Cass 11479 — VULA Wind]])`. Un `[[Nome]]` verso una pagina non ancora creata è OK: segnala un buco da riempire.

## Workflow: `ingest` (dai un documento → esce conoscenza strutturata)

Trigger: "ingerisci [path]".
1. **Leggi il raw** (docx via `textutil`, pdf via lettore integrato; scansioni → OCR quando disponibile). Mai modificarlo.
2. **Mostra 3–5 takeaway e chiedi conferma** (HITL) prima di scrivere.
3. **Crea la `source` page** con frontmatter completo, **massima/sintesi** (200–500 parole) e i punti chiave. Per le sentenze: riporta il principio di diritto testuale tra virgolette. Linka via `[[…]]` ogni entità/concept/materia toccati.
4. **Crea/aggiorna** entity/topic/concept e — se è una memoria — il `contenzioso`. Se nuove info **contraddicono** claim esistenti, **non sovrascrivere**: tieni entrambe + sezione "⚠ Contraddizioni/refusi da verificare". Nuovi tag → HITL.
5. **Aggiorna `index.md`** e **appendi a `log.md`**: `## [YYYY-MM-DD] ingest | <slug>`.
6. **Riassumi** cosa hai toccato e i gap aperti.

## Workflow: `query` (domanda → risposta citata, con fallback a 2 livelli)

Trigger: domanda libera o "query [domanda]".
1. **Leggi `index.md`** per orientarti.
2. **Livello 1 — memorie/esperienza**: cerca prima nei `contenziosi/` e `briefings/` (casi analoghi per operatore/materia) e nelle nostre `concepts/`.
3. **Livello 2 — giurisprudenza/normativa**: se insufficiente, scendi sulle `sources/` (sentenze, norme, articoli), **filtrando per `orientamento` aggiornato** (scarta/segnala il `superato`).
4. **Sintetizza** con citazioni `[[…]]` per ogni claim. **Mai inventare**: se la wiki non sa, dichiaralo e proponi cosa ingerire dal `raw/`.
5. **Filing back**: se la risposta è di valore, proponi di salvarla come `concept` o `briefing`.
6. **Appendi a `log.md`**.

## Workflow: `redazione memoria` (genera una memoria/comparsa/parere dal patrimonio)

Trigger: "redigi memoria per [Comune] c. [Operatore], materia [X], atto impugnato [Y], motivi [Z]".
1. **Inquadra il caso**: identifica Comune, Operatore, materia, giudice, atto impugnato e i motivi di ricorso avversari.
2. **Recupera i precedenti nostri**: `contenziosi/` e `briefings/` con stesso operatore o stessa materia (memorie passate da cui partire).
3. **Seleziona gli argomenti**: per ogni motivo avversario, prendi il `concept` di risposta pertinente e le `sources` (sentenze) a supporto, preferendo l'`orientamento: consolidato` e le pronunce più alte/recenti.
4. **Compila il `template`** appropriato (`templates/`), calando gli argomenti su Comune/Operatore/atti specifici, citando ogni tesi con `[[sentenza]]`.
5. **Segnala i rischi**: motivi avversari senza precedente forte, orientamenti controversi, dati mancanti.
6. **HITL**: presenta la bozza per la revisione dell'avvocato (il "rev" dei nostri file). Non depositare/finalizzare nulla senza approvazione.
7. **Filing back**: a caso concluso, salva il `contenzioso` (con esito) e la memoria come `source` (`subtype: memoria`), collegando entity/concept/source. Il patrimonio cresce.

## Workflow: `lint` (manutenzione periodica)

1. **Contraddizioni/refusi** tra pagine (date/importi/nomi divergenti sullo stesso caso — es. copia-incolla tra memorie di Comuni diversi).
2. **Orientamenti da aggiornare**: sentenze `superato` non marcate; nuove pronunce di Cassazione che consolidano/ribaltano.
3. **Pagine orfane** (senza link entranti) e **concept impliciti** ricorrenti senza pagina dedicata.
4. **Materie sotto-coperte** e **bias estremi** (una materia coperta solo da fonti `internal`/`partisan` senza giurisprudenza neutra).
5. **Scadenze**: normativa modificata, tariffe ISTAT annuali da aggiornare.
6. **Output**: report azionabile; appendi a `log.md`.

## Stile

- **Italiano** ovunque. Registro giuridico, preciso, senza enfasi.
- Ogni claim/numero con fonte tra parentesi `([[…]])`.
- Riporta i **principi di diritto** testualmente tra virgolette, con estremi esatti (corte, numero, data).
- **Linka aggressivamente**.

## Governance (regole non negoziabili)

- **Mai modificare i raw** (Cerchio 1).
- **Mai sovrascrivere claim in silenzio**: contraddizioni e refusi si registrano, non si nascondono.
- **HITL** su: redazione/finalizzazione di atti, nuovi tag di tassonomia, cancellazioni, declassificazione di `sensitivity`.
- **Mai spacciare una tesi (`claimed`) per fatto (`verified`)**: distingui sempre l'orientamento consolidato dalla posizione di parte.
- **`sensitivity` di default = `confidential`** per tutto ciò che contiene dati identificativi di Enti/funzionari/importi. Mai assumere `public` senza evidenza.
- **Disclaimer**: l'assistente supporta i professionisti, non li sostituisce. Ogni atto va validato da un avvocato prima del deposito.
