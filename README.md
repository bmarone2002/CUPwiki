# LLM Wiki CUP — Archivia Solution

Memoria operativa in **markdown puro** per supportare Enti Locali nella gestione, accertamento e contenzioso del **Canone Unico Patrimoniale (CUP)**, con focus sui **servizi di rete** (telefonia, gas, idrico, energia elettrica).

Questo repository è pensato per lavorare **a quattro mani** in Cursor (o Claude Code / altro agent): si fa `git pull`, si apre la cartella, si legge `CLAUDE.md`, e si continua su ingest / query / redazione / lint senza database e senza RAG.

> **Per l’agente AI:** leggi subito [`CLAUDE.md`](CLAUDE.md) (cervello operativo) e, se serve il razionale architetturale, [`BLUEPRINT.md`](BLUEPRINT.md). Non modificare mai i file in `raw/`.

---

## In cosa consiste (in 30 secondi)

| Cosa | Perché |
|---|---|
| Cartella `wiki/` di pagine `.md` linkate | Conoscenza **compilata** e citabile (concept, sentenze, casi, playbook) |
| Cartella `raw/` di PDF/DOCX originali | Fonte di verità **immutabile** (l’agent legge, non scrive) |
| `CLAUDE.md` | Dice all’assistente struttura, naming, workflow e regole non negoziabili |
| `mcp-server/` (opzionale) | Espone la wiki a Claude Desktop come 7 tool nativi |
| Git | Versionamento e sync tra colleghi |

**Non è** un Drive di atti. **È** una wiki interrogabile: “tutto su WindTre”, “strategia gas vs Italgas”, “precedenti su soggettività mediata”, con citazioni `[[…]]` verso pagine esistenti.

Il progetto nasce dallo [starter kit LLM Wiki](BLUEPRINT.md) (dominio-neutro) ed è stato **specializzato sul CUP** Archivia: la wiki reale vive in `wiki/`, non in `example-wiki/` (che resta solo come modello didattico del kit).

---

## Cosa puoi farci

1. **Query** — domande su normativa / giurisprudenza / prassi / casi, con citazioni.
2. **Ingest** — dai un raw (sentenza, memoria, articolo) → escono pagine `source` + aggiornamenti a entity/concept/contenzioso.
3. **Redazione memoria** — bozza di atto riusando playbook + precedenti già in wiki (sempre da validare da un avvocato).
4. **Lint** — manutenzione: link rotti, contraddizioni, orientamenti superati, gap di materia.

I dettagli operativi sono in [`CLAUDE.md`](CLAUDE.md).

---

## Stato attuale (agosto 2026)

### Cosa fa questa wiki (sostanza CUP)

Supporta Archivia su **accertamento e contenzioso CUP**, soprattutto **servizi di rete**. In pratica accumula e collega:

- **casi** Comune vs operatore/gestore (`contenziosi/`);
- **argomenti riusabili** (`concepts/`) e **playbook** per materia (`briefings/`);
- **fonti** ingerite: memorie nostre, sentenze, circolari, articoli (`sources/`), con link al `raw/`.

Temi già strutturati in wiki (non esaustivi; vedi `wiki/concepts/` e i playbook):

| Materia | Temi / concept già in wiki |
|---|---|
| Trasversale | Natura tributaria del CUP; sanzione per infedele dichiarazione distinta dall’omesso versamento |
| Telefonia | Soggettività passiva in via mediata; utilizzo materiale / VULA; metodo induttivo su dati AGCOM |
| Gas | Gestore distribuzione soggetto passivo; devoluzione gratuita parziale insufficiente; autoriduzione unilaterale del canone |
| Idrico | Gestore SII non esente; due distinti servizi (acqua / fognatura); rifiuto di dichiarare utenze e stima presuntiva |
| Energia | Rettifica autodichiarazione utenze; stima prudenziale POD su dati ARERA |

Catalogo vivo: [`wiki/index.md`](wiki/index.md). Diario operazioni: [`wiki/log.md`](wiki/log.md).

### Copertura per materia (wiki compilata)

| Area | Stato wiki | Note |
|---|---|---|
| **Telefonia** | Operativa | Playbook + concept forti + più contenziosi (WindTre, Vodafone, Fastweb). In `raw/` ci sono **molte altre** memorie/fascicoli non ancora ingeriti. |
| **Gas** | Solida | Playbook + pattern Italgas (e Unareti). Buona copertura delle memorie principali in `raw/…/GAS/`. |
| **Idrico** | Multi-caso | Playbook + più gestori (UniAcque, ASIS, AQP, GORI, CAP, Pavia Acque). In `raw/` restano atti e sentenze non tutti in wiki. |
| **Energia elettrica** | Minima | 1 caso pilota (Bitritto c. E-Distribuzione) = allineato al fatto che in `raw/…/ENERGIA/` c’è **una** memoria. |
| **Altre materie CUP** (pubblicità, affissioni, passi carrabili, mercatale, occupazioni, viadotti, …) | Wiki **non** popolata | In `raw/` esistono soprattutto **articoli Merciari** (e sentenze in `CUP_SENTENZE` / `giurisprudenza-normativa-generale`). **Non** c’è un fascicolo `CONTENZIOSO_…` dedicato come per i servizi di rete. |
| MCP lettura (locale) | Validato | `tests/run_mcp_tests.sh` |
| MCP scrittura / hosting HTTP | Non necessario per Cursor | Codice presente; hosting = upgrade futuro |

**Numeri wiki (verificati):** 33 entities · 20 contenziosi · 38 sources · 13 concepts · 4 topic · 4 playbook di materia (+ 1 briefing MCP) · 1 template · 1 bozza.

### Wiki vs magazzino `raw/` (il gap materiale vero)

Il sistema **già funziona** su ciò che è in `wiki/`. Ciò che “manca” per una copertura completa non è l’infrastruttura: è **ingest** (portare in markdown curato ciò che è ancora solo in `raw/`).

Ordini di grandezza sul disco (file in `raw/`, non tutti da ingerire uno a uno; molti sono duplicati/versioni):

| Zona raw | ~file | In wiki oggi |
|---|---|---|
| `CONTENZIOSO_…/TELEFONIA/` | ~86 | Solo una parte dei casi/atti → 20 contenziosi totali su **tutte** le materie |
| `CONTENZIOSO_…/GAS/` | ~9 | Copertura buona delle memorie principali |
| `CONTENZIOSO_…/IDRICO/` | ~33 | Multi-caso, ma atti/sentenze ancora fuori wiki |
| `CONTENZIOSO_…/ENERGIA/` | 1 | 1 caso (coerente) |
| `CUP_SENTENZE/` | ~122 | Solo una frazione in `sources/` |
| `CUP_ARTICOLI MERCIARI/` | ~275 | Poche `source` Merciari |
| `giurisprudenza-normativa-generale/` | ~482 | In gran parte non ingerita (e in parte sovrapposta alle altre cartelle) |

Esempi di raw **presenti** e **non** (o solo parzialmente) riflessi in `wiki/contenziosi/` — utili per priorità di ingest, non lista chiusa:

- Telefonia: memorie Fastweb/Vodafone/Wind per comuni oltre il set già strutturato (es. filoni Palestro / Aquara / Cinisello / Montefalco / Sessa / Capriate Fastweb; Castelsaraceno; Cappelle sul Tavo; Santa Croce Camerina; Palagiano Wind; …).
- Idrico: es. Belforte c. Marche Multiservizi; Bitritto c. Acquedotto Pugliese; varie sentenze nella cartella IDRICO.
- Gas: Capriate c. Italgas ha una `source` in wiki, ma **non** una pagina dedicata in `contenziosi/` come gli altri casi Italgas.
- Stub `claimed` (citati in memorie, PDF assente o non verificato in `raw/`): es. Trib. Bergamo 289 Vodafone; Trib. Napoli 5948 WindTre — già segnalati in `sources/`.

---

## Avvio collaboratore (Cursor, ~10 minuti)

### 1. Clona / pull

```bash
git clone https://github.com/bmarone2002/CUPwiki.git
cd CUPwiki
# oppure, se già clonato:
git pull
```

> Repo: [github.com/bmarone2002/CUPwiki](https://github.com/bmarone2002/CUPwiki). Contiene memorie e dati di contenzioso (`sensitivity` spesso `confidential`): il repository deve restare **privato**; invita il collega come collaborator, non pubblicare in chiaro.

### 2. Apri in Cursor

`File → Open Folder…` → seleziona la root del repo (quella che contiene `CLAUDE.md`, `wiki/`, `raw/`).

Cursor (e gli agent) caricano automaticamente le regole da `CLAUDE.md` / workspace rules: **non serve** installare un database.

### 3. (Consigliato) Obsidian sulla stessa cartella

Apri Obsidian → *Open folder as vault* → punta a questa root **oppure** solo a `wiki/` (a seconda di come preferite navigare i wikilink). I file restano gli stessi; Obsidian aiuta grafo e lettura umana.

### 4. Prima chat utile all’agent

Esempi di prompt:

```text
Leggi CLAUDE.md e wiki/index.md. Fammi un punto sullo stato della wiki e i gap aperti.
```

```text
Query: quali argomenti usiamo contro l’esenzione per devoluzione gratuita nel gas?
```

```text
Ingerisci raw/.../NOME_FILE.docx (workflow ingest, HITL sui takeaway).
```

### 5. Prerequisiti tecnici

| Serve | Per |
|---|---|
| Git + Cursor | Collaborazione quotidiana |
| Niente Python | Query / ingest / redazione **dentro Cursor** |
| Python **≥ 3.10** (solo se vuoi MCP / test) | Claude Desktop + `tests/run_mcp_tests.sh` |

macOS spesso ha solo Python 3.9 di sistema: per l’MCP usare un venv 3.12 (vedi sezione MCP sotto).

---

## Struttura del repository

```
llm-wiki-starter-kit/          ← (nome cartella storica; contenuto = wiki CUP)
├── README.md                  ← questo file (onboarding umano)
├── CLAUDE.md                  ← ⭐ regole + workflow per l’agent (CUP)
├── BLUEPRINT.md               ← razionale generico LLM Wiki + hosting/MCP
├── CLAUDE.md.template         ← template dominio-neutro (riferimento kit)
├── raw/                       ← Cerchio 1: originali IMMUTABILI
│   ├── giurisprudenza-normativa-generale/
│   └── Memorie passate + template/
│       └── CONTENZIOSO_…/{TELEFONIA,GAS,IDRICO,ENERGIA}/…
├── wiki/                      ← Cerchio 2: markdown curato (IL VALORE)
│   ├── index.md               ← catalogo
│   ├── log.md                 ← diario append-only delle operazioni
│   ├── entities/              ← Comuni, operatori, autorità, …
│   ├── topics/                ← materie (telefonia, gas, idrico, energia)
│   ├── concepts/              ← argomenti giuridici riusabili
│   ├── sources/               ← 1 doc ingerito = 1 pagina
│   ├── contenziosi/           ← 1 causa = 1 pagina
│   ├── briefings/             ← playbook / sintesi
│   ├── templates/             ← scheletri atti
│   └── bozze/                 ← bozze generate, da validare
├── mcp-server/                ← server MCP (stdio locale / HTTP opzionale)
├── tests/                     ← smoke MCP + report validazione
├── example-wiki/              ← esempio didattico del kit (NON è la wiki CUP)
└── tools/                     ← helper locali (es. uv, se presente; spesso gitignored)
```

### Tipi di pagina (regola d’oro)

| Tipo | Cartella | Esempio |
|---|---|---|
| `entity` | `wiki/entities/` | `WindTre.md` — fatti stabili sull’operatore |
| `contenzioso` | `wiki/contenziosi/` | `Comune di Berbenno c. WindTre — …` — **il singolo caso** |
| `concept` | `wiki/concepts/` | `Soggettività passiva in via mediata.md` |
| `source` | `wiki/sources/` | `2026-05-01 Cass SS.UU. 12225 — …` |
| `topic` / `briefing` | `topics/` / `briefings/` | materia / playbook |

**`entity` ≠ `contenzioso`:** non fondere l’operatore col singolo fascicolo.

---

## Come collaborare a quattro mani

### Git (sync tra macchine)

1. Prima di lavorare: `git pull`.
2. Lavorare su branch corti se toccate pezzi diversi (es. `ingest/gas-…`, `docs/readme`).
3. Commit **solo quando richiesto / concordato**; messaggi chiari sul *perché*.
4. Preferire commit separati: contenuti wiki vs. codice MCP/test vs. docs.
5. Non committare segreti, `.venv*`, path macchina-specifici inutili.

File tipicamente **ignorati** (vedi `.gitignore`): `.venv/`, `.venv-mcp/`, `tools/uv-bin/`, `raw_text/`.

### Divisione del lavoro consigliata

| Ruolo | Lavora su | Evitare |
|---|---|---|
| Analista / legale | `wiki/` (ingest, query, bozze) | Modificare `raw/` |
| Tecnico | `mcp-server/`, `tests/`, docs | Sovrascrivere claim wiki senza HITL |
| Entrambi | `wiki/log.md` (append), `wiki/index.md` | Cancellare pagine “per ripulire” senza accordo |

### Regole non negoziabili (riassunto)

- **Mai modificare `raw/`.**
- **Mai sovrascrivere claim in silenzio:** se due atti si contraddicono, tenere entrambe le versioni + sezione “⚠ Contraddizioni/refusi”.
- **HITL** su: finalizzazione atti, nuovi tag di tassonomia, cancellazioni, declassificazione `sensitivity`.
- Distinguere sempre `verified` / `estimated` / `claimed` e `bias` (`neutral` / `internal` / `partisan`).
- Default `sensitivity: confidential` su dati enti / funzionari / importi / RG.
- L’assistente **supporta** i professionisti: ogni atto va validato da un avvocato prima del deposito.

### Conflitti tipici e come evitarli

- Due persone che ingeriscono lo stesso raw → prima verificare se esiste già una `source` in `wiki/sources/`.
- Due persone che editano lo stesso `index.md` / `log.md` → fare pull frequente; su `log.md` solo **append** in coda.
- Path assoluti in config MCP → ogni macchina adatta `claude_desktop_config_cup.json` in locale (non forzare i path dell’altro).

---

## Workflow operativi (come parlarne all’agent)

| Trigger | Cosa fa |
|---|---|
| `ingerisci [path in raw/]` | Legge raw → takeaway HITL → crea/aggiorna source + pagine collegate → aggiorna index/log |
| `query [domanda]` | Prima contenziosi/briefings/concepts, poi sources; cita `[[…]]`; non inventa |
| `redigi memoria per Comune c. Operatore…` | Parte dai playbook + template; bozza in HITL |
| `lint` | Report gap/contraddizioni/orientamenti |

Playbook di materia già in wiki:

- [`wiki/briefings/Strategia difensiva — CUP servizi di rete (telefonia).md`](wiki/briefings/Strategia%20difensiva%20—%20CUP%20servizi%20di%20rete%20(telefonia).md)
- [`wiki/briefings/Strategia difensiva — CUP servizi di rete (gas).md`](wiki/briefings/Strategia%20difensiva%20—%20CUP%20servizi%20di%20rete%20(gas).md)
- [`wiki/briefings/Strategia difensiva — CUP servizi di rete (idrico).md`](wiki/briefings/Strategia%20difensiva%20—%20CUP%20servizi%20di%20rete%20(idrico).md)
- [`wiki/briefings/Strategia difensiva — CUP servizi di rete (energia elettrica).md`](wiki/briefings/Strategia%20difensiva%20—%20CUP%20servizi%20di%20rete%20(energia%20elettrica).md)

Infrastruttura MCP (locale vs hostato): [`wiki/briefings/MCP — accesso operativo alla wiki CUP.md`](wiki/briefings/MCP%20—%20accesso%20operativo%20alla%20wiki%20CUP.md).

---

## MCP (opzionale — non serve per Cursor)

Per collaborare in Cursor **non** serve Claude Desktop né Python. L’MCP serve se volete parlare alla stessa wiki da **Claude Desktop** con tool nativi.

**Decisione attuale:** basta il **locale (stdio)**. L’hosting HTTP è un upgrade per team multi-utente senza venv (vedi briefing MCP).

### Setup rapido locale

```bash
# Python 3.10+ obbligatorio (consigliato 3.12)
python3.12 -m venv .venv-mcp
source .venv-mcp/bin/activate   # Windows: .venv-mcp\Scripts\activate
pip install -r mcp-server/requirements.txt

# Test lettura sulla wiki reale
chmod +x tests/run_mcp_tests.sh
./tests/run_mcp_tests.sh
```

Poi copia il blocco `cup-wiki` da [`mcp-server/claude_desktop_config_cup.json`](mcp-server/claude_desktop_config_cup.json) nel tuo `claude_desktop_config.json`, **adattando i path assoluti** alla tua macchina, riavvia Claude (Quit completo) e apri una **nuova** chat.

Dettagli: [`mcp-server/README.md`](mcp-server/README.md).

---

## Cosa manca / prossimi passi utili

Separare due piani: **materiale** (corpus) vs **operatività** (git / client). Per “far funzionare” query e redazione sulle 4 materie servizi di rete **non** serve altro materiale minimo: serve decidere *cosa ingerire dopo*.

### A — Materiale (priorità contenuto)

1. **Ingest residuo servizi di rete** — portare in wiki i fascicoli/memorie ancora solo in `raw/CONTENZIOSO_…`, partendo da telefonia (magazzino più grosso) e dagli atti idrici mancanti; gas quasi allineato; energia già allineata al raw disponibile (1 memoria).
2. **Chiudere gap strutturali già noti** — es. contenzioso Capriate c. Italgas (source sì / pagina `contenziosi/` no); refusi segnalati nelle `source` (HITL, non overwrite silenzioso).
3. **Sentenze / stub** — ingerire PDF presenti in `raw/` ma non in `sources/`; recuperare o declassare i precedenti ancora `claimed` senza file.
4. **Dottrina Merciari e altre materie CUP** — popolare pubblicità / passi / mercatale / viadotti / occupazioni **solo quando servono operativamente**, partendo dagli articoli già in `CUP_ARTICOLI MERCIARI/` (non c’è un contenzioso-folder dedicato come per le reti).
5. **Energia** — densificare *se* arrivano nuovi raw; oggi il collo di bottiglia è l’assenza di altri atti in `ENERGIA/`, non il tooling.

### B — Operatività collaborazione

1. **Remote git privato** + primo snapshot condiviso (molto lavoro può essere ancora locale/untracked).
2. **Claude Desktop + MCP locale** — solo se volete i tool fuori da Cursor; path da adattare per macchina.
3. **Test MCP write** — solo su `example-wiki/` o con approvazione esplicita; non sulla wiki CUP a freddo.
4. Hosting HTTP MCP — **non** richiesto finché collaborare = clone + Cursor + git.

---

## Mappa documenti (cosa leggere quando)

| Documento | Quando |
|---|---|
| **Questo README** | Onboarding collega / “cos’è il progetto” |
| [`CLAUDE.md`](CLAUDE.md) | Ogni sessione agent: regole, tipi, workflow |
| [`wiki/index.md`](wiki/index.md) | Orientarsi nel contenuto |
| [`wiki/log.md`](wiki/log.md) | Cosa è stato fatto di recente |
| [`BLUEPRINT.md`](BLUEPRINT.md) | Perché markdown, hosting, filosofia kit |
| [`mcp-server/README.md`](mcp-server/README.md) | Install MCP / HTTP |
| `tests/results/*` | Esiti validazione query/MCP |

---

## Disclaimer

Questo sistema supporta il lavoro professionale di Archivia Solution; **non** sostituisce il giudizio dell’avvocato. Ogni atto processuale generato o aggiornato tramite agent va rivisto e approvato prima del deposito. Trattare i contenuti con attenzione a privacy e riservatezza degli Enti.
