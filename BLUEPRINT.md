# Blueprint — Costruire una LLM Wiki

> Documento-base, dominio-neutro, da dare a un agent AI (Claude Code, Cursor, …) perché costruisca **la tua** knowledge base interrogabile: una wiki in markdown puro che un LLM legge, scrive e mantiene, esposta come tool nativi via un server MCP.
>
> È la versione generalizzata di un sistema reale in produzione. I concetti sono astratti; un **esempio fil rouge** li àncora a un caso concreto (una KB personale di ricerca). Dove vedi il box 🧵 **Fil rouge**, è l'esempio che attraversa tutto il documento.

---

## 0. Come usare questo kit

Questo kit contiene 4 pezzi:

| Pezzo | Cos'è | Quando lo tocchi |
|---|---|---|
| **`BLUEPRINT.md`** (questo file) | Il concetto, l'architettura, l'hosting, l'MCP. La teoria + le decisioni. | Leggilo per primo, tutto. |
| **`CLAUDE.md.template`** | Il system prompt della tua wiki: dice all'agent come è strutturata e che workflow seguire. Da compilare. | Lo compili al passo 2 (sotto). |
| **`mcp-server/`** | Server MCP riusabile (7 tool, stdio + HTTP). Già funzionante, generico. | Lo configuri quando vuoi parlare alla wiki da Claude Desktop. |
| **`wiki/`** | Wiki d'esempio (dominio fil rouge): index, log e una pagina per tipo. | La copi come scheletro e la svuoti. |

**Percorso minimo (un pomeriggio):**

1. Leggi questo blueprint.
2. Copia `CLAUDE.md.template` → `CLAUDE.md` nella root del tuo repo e compilalo (sezioni §3, §4 sotto ti dicono cosa).
3. Copia la cartella `wiki/` d'esempio, cancella le pagine di esempio, tieni `index.md` + `log.md` vuoti.
4. `git init` + apri la cartella in [Obsidian](https://obsidian.md). **Hai già una LLM wiki usabile** (tier 0, §6).
5. Quando vuoi, configura `mcp-server/` (§7) per leggere/scrivere la wiki da Claude.

Il resto del documento spiega il *perché* di ogni scelta, così l'agent (e tu) potete adattarlo invece di copiarlo a scatola chiusa.

---

## 1. Il concetto: cos'è una LLM Wiki (e perché markdown, non RAG)

Una **LLM Wiki** è una raccolta di file markdown — uno per "cosa" (una persona, un'organizzazione, un progetto, un tema, un'idea, un documento) — fittamente collegati tra loro con `[[wikilink]]`, con metadati strutturati in testa a ogni file (frontmatter YAML). Un LLM la legge per rispondere a domande, e la scrive per accumulare conoscenza nel tempo.

Non è un Drive di file. È **memoria interrogabile**: risponde a "tutto quello che so su X", "confronta X e Y", "cos'è cambiato da quando ho visto Z".

### Perché markdown puro e non un RAG (vector DB)?

La tentazione, oggi, è: PDF dentro → chunking → embedding → vector search. Per molti casi è la scelta sbagliata, o almeno prematura. Confronto onesto:

| Dimensione | RAG / Vector DB | LLM Wiki (markdown) |
|---|---|---|
| Unità di recupero | Frammenti (chunk di 500–1500 char) | Pagine intere, coerenti |
| Schema | Implicito, auto-estratto, opaco | Esplicito, scelto da te (frontmatter) |
| Recupero | Probabilistico (similarità) | Deterministico (grep + filtri) + il tuo cervello |
| Conoscenza derivata | Nessuna: ri-cerca ogni volta | **Compilata**: sintetizzi una volta, resta scritta |
| Leggibilità umana | Bassa (vettori) | Totale: sono file di testo, apribili in Obsidian |
| Portabilità | Lock-in sul DB/formato | Massima: sono `.md`, vivono ovunque |
| Costo/infra Day 1 | DB + pipeline embedding | Una cartella e `git` |
| Soglia di dolore | Scala a milioni di doc | Sotto ~150–500 pagine `grep` basta; oltre, valuta indici |

Il punto chiave: una wiki **compila la conoscenza**. In un RAG, "qual è il metodo migliore per prendere appunti?" rifà retrieval ogni volta sui chunk grezzi. In una wiki, la prima volta che rispondi bene a quella domanda **scrivi una pagina concept** — e da lì in poi la risposta è già lì, curata, linkata, migliorabile a mano. Le esplorazioni *compoundano* invece di evaporare.

> 🧵 **Fil rouge** — In questo blueprint l'esempio è una **KB personale di ricerca**: tieni traccia di persone (autori, esperti), organizzazioni (aziende, tool, istituzioni), tuoi progetti, temi che studi, concetti/metodi che impari, e documenti che leggi. Il filo concreto che useremo: il tema *knowledge-management*, la persona *Niklas Luhmann*, l'organizzazione *Obsidian*, il tuo *Project Atlas* (costruire la KB), il concetto *Zettelkasten Method*, e una source (il libro *How to Take Smart Notes*).

### Quando NON usare questa impostazione

Sii onesto sui limiti. Una LLM Wiki markdown **non** è la scelta giusta se: hai centinaia di migliaia di documenti da subito; ti serve ricerca semantica fuzzy come funzione primaria; i contenuti sono per lo più tabelle/binari non testuali; o ti serve accesso concorrente multi-utente con permessi fini al Day 1. In quei casi parti da un vero datastore (Postgres + pgvector + object storage). Puoi sempre iniziare wiki e migrare: i `.md` sono il formato più facile da esportare che esista.

---

## 2. Architettura a 3 cerchi

Separa tre cose che vengono spesso confuse:

```
┌─ Cerchio 1 — RAW (immutabile) ─────────────────────────┐
│  I documenti originali: PDF, docx, email, foto, dump.   │
│  L'agent LEGGE, non modifica MAI. È la fonte di verità  │
│  grezza. Vive dove vuoi (una cartella, un cloud).       │
└────────────────────────┬────────────────────────────────┘
                         │ ingest (l'agent legge, sintetizza)
                         ▼
┌─ Cerchio 2 — WIKI (il valore) ─────────────────────────┐
│  Pagine markdown create e mantenute dall'agent.         │
│  È il delivery layer: ciò che interroghi. Questo repo.  │
│  Markdown + frontmatter + [[wikilink]]. Niente DB.      │
└────────────────────────┬────────────────────────────────┘
                         │ (opzionale, quando scali)
                         ▼
┌─ Cerchio 3 — INDEX/METADATA (futuro, opzionale) ───────┐
│  Un DB (Postgres) per foreign key verso altri sistemi,  │
│  audit trail, ricerca strutturata su volumi grandi.     │
│  NON serve al Day 1. Aggiungilo solo quando il dolore   │
│  reale lo richiede (vedi §1 "quando NON usare").        │
└──────────────────────────────────────────────────────────┘
```

**Regola d'oro del Cerchio 1:** mai modificare i raw. La wiki è una *proiezione curata* dei raw, non un loro rimpiazzo. Se cancelli una pagina wiki, il raw resta; puoi sempre ri-ingerire.

> 🧵 **Fil rouge** — Cerchio 1 = la cartella dove tieni i PDF dei paper e i tuoi screenshot. Cerchio 2 = la wiki che l'agent costruisce leggendoli. Cerchio 3 = non ti serve: sei un singolo utente con qualche centinaio di note.

---

## 3. Modello dei contenuti

Ogni pagina ha un **tipo**, dichiarato nel frontmatter (`type:`) e riflesso nella cartella in cui vive. Sei tipi coprono quasi tutto:

| `type` | Cos'è | Cartella | Bias prevalente |
|---|---|---|---|
| `entity` | Una "cosa" del mondo: persona, organizzazione, prodotto, tool. | `entities/` | neutral |
| `project` | Una *tua* iniziativa/contesto in cui le entity si incontrano col tuo lavoro. | `projects/` | internal |
| `topic` | Un'area tematica, una tassonomia di dominio. | `topics/` | neutral |
| `concept` | Conoscenza *derivata*: metodi, framework, sintesi, confronti. | `concepts/` | internal |
| `source` | **1 file = 1 documento ingerito.** Riassunto + link al raw. | `sources/` | dipende dalla fonte |
| `briefing` | Output di una query di valore, "filato" come pagina (sintesi di N pagine). | `briefings/` | internal |

Le entity possono avere un sotto-tipo nel frontmatter (`subtype: person | org | product | …`) invece di sotto-cartelle, per tenere il file system piatto e semplice. (Se preferisci le sotto-cartelle, è un edit di una riga nel server MCP — vedi §7.)

### La regola fondamentale: `entity` ≠ `project`

Questa è la decisione di modellazione più importante, e la più facile da sbagliare.

**Una cosa del mondo e un tuo contesto su quella cosa sono due pagine distinte, linkate.**

Perché? Perché la stessa cosa vive in più contesti, e i contesti cambiano nel tempo, mentre la cosa resta. Se fondi i due, perdi la capacità di chiedere "tutto quello che so su X" attraverso i progetti.

> 🧵 **Fil rouge** — *Niklas Luhmann* (entity, persona) è una cosa del mondo: fatti pubblici, neutri, stabili. *Project Atlas* (project) è il tuo sforzo di costruire una KB col suo metodo: appunti tuoi, decisioni, stato, bias interno. `Project Atlas` linka `[[Niklas Luhmann]]`. Domani potresti avviare *Project Borealis* che pure cita Luhmann — e la pagina di Luhmann li serve entrambi senza duplicarsi.

Stessa logica per: un'azienda vs. un tuo progetto con quell'azienda; un autore vs. la tua recensione di un suo libro; un tool vs. la tua valutazione di quel tool.

### Naming

- Nomi in **forma naturale con spazi**, leggibili: `Niklas Luhmann.md`, `Project Atlas.md`, `Zettelkasten Method.md`. Obsidian gestisce gli spazi nei wikilink nativamente.
- Temi/tassonomie: `kebab-case` o `snake_case` se preferisci, purché coerente: `knowledge-management.md`.
- Source: prefisso data ISO per ordinamento cronologico: `YYYY-MM-DD <slug>.md` → `2026-05-29 Ahrens - How to Take Smart Notes.md`.
- Omonimia: disambigua tra parentesi: `John Smith (Acme).md`.

---

## 4. Frontmatter e sistema di metadata

Ogni pagina inizia con frontmatter YAML. È lo **schema esplicito** che rende le query deterministiche (filtra per tag, per tipo, per affidabilità) senza bisogno di un DB.

Campi comuni a tutti i tipi:

```yaml
---
type: entity            # entity | project | topic | concept | source | briefing
tags: [knowledge-management, note-taking]   # la tua tassonomia, multi-valore
sensitivity: public     # public | internal | confidential | restricted
updated_at: 2026-05-29  # data ultima manutenzione (l'MCP la bumpa da solo)
---
```

Campi aggiuntivi per `source` (il tipo con più metadata, perché traccia la provenienza):

```yaml
---
type: source
source_path: "../raw/ahrens-smart-notes.pdf"   # link al Cerchio 1 (raw)
ingested_at: 2026-05-29
as_of_date: 2017-02-01      # data a cui si riferisce il contenuto
bias: neutral               # vedi sotto
confidence: verified        # vedi sotto
shelf_life_months: 24       # dopo, la pagina è "stale" per le query
expires_at: 2028-05-29
tags: [knowledge-management]
sensitivity: public
---
```

### I tre assi di qualità del dato

Sono il cuore del sistema. Definiscili una volta, **applicali con coerenza**.

**`bias`** — l'orientamento della fonte. Tiene onesta la KB.
- `neutral` — fonti indipendenti (articoli, paper, report di terzi).
- `internal` — output tuo (le tue sintesi, analisi, note).
- `partisan` — fonti con un interesse (materiale promozionale, una parte in causa). *Personalizza i valori sul tuo dominio.*

**`confidence`** — quanto è affidabile il dato. (Scegli una convenzione e **non invertirla mai** — è l'errore classico.) Qui: più sali, più sei certo.
- `verified` — fatti verificabili da fonti primarie/autorevoli.
- `estimated` — stime con base quantitativa, non confermate.
- `claimed` — affermazioni non verificate o da fonte di parte. *Marcare `claimed` non è negativo: è onesto.*

**`sensitivity`** — chi può vederlo.
- `public` → `internal` → `confidential` → `restricted`. Default a `internal` quando in dubbio; mai assumere `public` senza evidenza.

**`shelf_life_months` / `expires_at`** — la freschezza. Oltre `expires_at` la pagina **resta** (l'archivio storico è prezioso) ma le query la considerano stale e la de-prioritizzano. Tipici: 12 mesi (report di mercato), 24 (analisi tue), nessuna scadenza (fatti stabili).

> 🧵 **Fil rouge** — Il libro di Ahrens: `bias: neutral`, `confidence: verified`, `shelf_life: 24`. Una tua nota "credo che il metodo X funzioni meglio per me": `bias: internal`, `confidence: claimed`. Un post di marketing di un tool: `bias: partisan`, `confidence: claimed`.

### Densità di link = valore

**Linka aggressivamente con `[[Page Name]]`.** La densità dei link *è* il valore: è ciò che permette a "tutto quello che so su X" di funzionare (l'agent segue i link). Un `[[Nome]]` che punta a una pagina non ancora creata va benissimo: segnala un buco da riempire, non è un errore. Ogni numero/claim importante dovrebbe citare la source tra parentesi: `il metodo nasce negli anni '60 ([[2026-05-29 Ahrens - How to Take Smart Notes]])`.

---

## 5. I workflow dell'agent

Il `CLAUDE.md` (che compili dal template) insegna all'agent tre workflow. Riassunto del *cosa*; il template ha il *come* dettagliato.

### `ingest` — dai un documento, esce conoscenza strutturata
1. L'agent legge il raw (Cerchio 1).
2. Ti mostra 3–5 takeaway e **chiede conferma** prima di scrivere (human-in-the-loop).
3. Crea la **source page** (`sources/`) con frontmatter completo + riassunto + takeaway, linkando ogni entità menzionata.
4. Crea/aggiorna le **entity/project/topic/concept page** toccate. Se nuove info **contraddicono** quelle esistenti, non sovrascrive in silenzio: tiene entrambe e aggiunge una nota "⚠ Contraddizione da verificare".
5. Aggiorna `index.md` (catalogo) e appende a `log.md` (cronologia).

### `query` — fai una domanda, ottieni una risposta citata
1. L'agent legge `index.md` per orientarsi, identifica le pagine candidate, **le legge per intero**.
2. Sintetizza con citazioni `[[Page]]` per ogni claim. **Mai inventare**: se la wiki non sa, lo dichiara e propone cosa ingerire.
3. **Filing back**: se la risposta è di valore, propone di salvarla come pagina `concept`/`briefing`. Così le esplorazioni compoundano.

### `lint` — manutenzione periodica
Cerca: contraddizioni tra pagine; pagine orfane (senza link entranti); concetti impliciti ricorrenti senza pagina dedicata; temi sotto-coperti; claim scaduti (`expires_at` passato); bias estremi (un tema coperto al 100% da fonti `partisan`). Produce un report azionabile.

### Governance (le regole non negoziabili)
- **Mai modificare i raw** (Cerchio 1).
- **Mai sovrascrivere claim in silenzio**: le contraddizioni si registrano, non si risolvono di nascosto.
- **Human-in-the-loop** sulle decisioni strutturali: nuovi tag di tassonomia, cancellazioni, declassificazione di `sensitivity`.
- **`bias: internal` va giustificato**: se un'info potrebbe essere `neutral`, classificala così, non `internal` cieco (eviti l'echo chamber).

---

## 6. Hosting — la scala

Non esiste "un" modo di hostare. C'è una **scala**: sali solo quanto ti serve. La maggior parte degli usi personali si ferma al Tier 0.

### Tier 0 — Locale: `git` + Obsidian (zero infrastruttura)

La wiki *è* una cartella di `.md`. Questo basta:
- **`git`** per versionare e fare backup (push su GitHub/GitLab privato). Ogni modifica è tracciata, ogni stato è ripristinabile. Questo *è* il tuo disaster recovery.
- **[Obsidian](https://obsidian.md)** punta alla cartella: ottieni grafo dei link, ricerca, editing comodo, backlink automatici. Gratis, locale, i file restano tuoi.
- L'agent (Claude Code nella cartella, o Claude Desktop via MCP §7) legge e scrive i `.md`.

Per un singolo utente, **questo è tutto ciò che serve**. Niente server, niente account, niente costi.

### Tier 1 — Web app self-hosted (per condividere con un team)

Quando più persone devono accedere senza clonare un repo, metti una piccola web app davanti alla wiki. Lo stack collaudato e a basso costo:

```
Internet ──HTTPS──> Cloudflare (DNS proxied, TLS)
                      │
                      └──> Reverse proxy (es. Traefik via Coolify)
                                  └──> container app (legge/scrive wiki/)
                                          ├── auth (es. GoTrue) — invite-only
                                          └── storage durabile (vedi sotto)
```

- **[Coolify](https://coolify.io)** (PaaS self-hosted su un VPS, es. Hetzner ~€5–15/mese): orchestratore Docker + reverse proxy + TLS automatico. Deploy da un Dockerfile, push-to-deploy via webhook.
- **Cloudflare**: DNS + TLS + protezione. Un record `A` proxied verso il VPS.
- **Auth invite-only** (es. [GoTrue](https://github.com/supabase/auth)): email+password, JWT in cookie HttpOnly. Per pochi utenti basta e avanza.
- **Branch di deploy**: tieni `main` per lo sviluppo e un branch `prod` come gate di rilascio (promuovi `main → prod` con `git merge --ff-only`). Eviti deploy accidentali.

### Lo storage deve essere data-loss-proof (vale dal Tier 1 in su)

⚠️ **Trappola classica:** i volumi di un VPS vivono finché vive il VPS. Se il server muore (o lo ricrei), il filesystem va perso — incluse le scritture runtime fatte dall'agent. Se 50 pagine vengono create di mattina e il VPS muore di pomeriggio, sono perse.

**Soluzione:** usa un **object storage** (Cloudflare R2, AWS S3, Backblaze B2 — durabilità ~11×9) come *primary persistent storage*, non solo backup:
- **Sync on-write**: dopo ogni scrittura, replica il file su object storage in async (fire-and-forget, latenza UI invariata).
- **Restore on cold-boot**: al primo avvio di un container con volumi vuoti, scarica tutto dall'object storage prima di servire richieste.
- **Snapshot periodico** (`tar.gz` giornaliero sotto un prefix `snapshots/`) come rete di sicurezza per il point-in-time restore ("rivoglio la wiki di 3 giorni fa").

Con `git` (Tier 0) come versionamento *e* object storage (Tier 1) come storage runtime, la perdita dati diventa strutturalmente impossibile.

### Tier 2 — MCP server hostato

Per far parlare la wiki a Claude Desktop/Claude.ai senza che ognuno installi Python: hosti il server MCP (§7) come container e gli utenti incollano solo un URL. Vedi §7.

---

## 7. L'MCP server

[MCP (Model Context Protocol)](https://modelcontextprotocol.io) è lo standard aperto con cui un LLM scopre e chiama tool esterni. Il server MCP di questo kit (`mcp-server/server.py`) espone la tua wiki come **7 tool nativi** dentro Claude Desktop/Claude.ai: parli in italiano normale e Claude legge/scrive la wiki senza che tu apra file o spieghi struttura.

### I 7 tool

**Lettura (4):**
| Tool | Cosa fa |
|---|---|
| `wiki_search` | Ricerca keyword su contenuto + frontmatter, con filtri (tag, tipo, sensitivity). |
| `wiki_get_page` | Apre il contenuto completo di una pagina per nome (esatto o fuzzy). |
| `wiki_list_related` | Tutte le pagine collegate a una data (backlink + riferimenti frontmatter). Il "tutto su X". |
| `wiki_list_sources` | Le source con filtri per tipo documento ed età massima (trova lo stale). |

**Scrittura (3):**
| Tool | Cosa fa |
|---|---|
| `wiki_create_page` | Crea una pagina nel tipo/cartella giusto. Errore se esiste già. |
| `wiki_append_to_section` | Append a una sezione `## <heading>` (es. un bullet alla "Cronologia"). La crea se manca. |
| `wiki_update_frontmatter` | Patch field-level del frontmatter (merge, non sovrascrive il corpo). Bumpa `updated_at`. |

### Due modi di esecuzione

- **stdio (locale)**: il server gira sul tuo PC, parla a Claude Desktop via stdin/stdout. Zero cloud, zero account. È il default per uso personale. Config: `command` + `args` + `WIKI_DIR` nel `claude_desktop_config.json`.
- **HTTP (hostato)**: un container centrale (stesso VPS Coolify del Tier 1), gli utenti incollano un URL + un Bearer token. Nessuna installazione Python lato client. (Claude Desktop oggi parla solo stdio: il ponte è `npx mcp-remote` che fa da proxy stdio↔HTTP — vedi `mcp-server/README.md`.)

### Safety (già implementata nello scheletro)

- **Anti path-traversal**: ogni scrittura risolve il path e verifica che resti dentro `WIKI_DIR`. `../../etc/passwd` è rifiutato.
- **Scrittura atomica**: tempfile + rename. Un crash a metà non lascia file corrotti.
- **Audit log**: ogni write loggata su `log.md` con timestamp UTC.
- **Conferma umana**: Claude Desktop chiede approvazione esplicita prima di ogni tool di scrittura.
- **Git auto-push opzionale**: in modalità hostata, ogni write può fare commit+push automatico (env `MCP_GIT_AUTO_PUSH=true`), così le modifiche si propagano al repo.

### Niente embedding/RAG in v1

Sotto ~150 pagine, `grep` + parsing frontmatter bastano e sono *istantanei*. Non aggiungere un vector index finché la ricerca keyword non ti delude davvero. È la stessa filosofia del §1: complessità solo quando il dolore è reale.

---

## 8. Come adattarlo al tuo dominio

Il kit è generico di proposito. Per renderlo *tuo*, tre punti in cui mettere le mani — in ordine di importanza:

1. **La tassonomia (`tags`) e i tipi.** È la decisione di dominio numero uno. Quali "cose" tieni? Per la KB di ricerca: persone, org, temi. Per un fondo d'investimento: target, advisor, deal, settori. Per un team prodotto: feature, clienti, competitor, release. Definisci i tuoi `type` e il vocabolario dei `tags` nel `CLAUDE.md`.
2. **`CLAUDE.md`.** È il cervello operativo. Compila: identità della KB, tipi, tassonomia, convenzioni di naming, i tre workflow. Il template ti guida con `{{PLACEHOLDER}}`.
3. **Il server MCP** (solo se cambi i nomi dei tipi/cartelle). Un'unica struttura dati da editare in `server.py`:
   ```python
   _TYPE_DIRS = {
       "entity":   "entities",
       "project":  "projects",
       "topic":    "topics",
       "concept":  "concepts",
       "source":   "sources",
       "briefing": "briefings",
   }
   ```
   Cambia chiavi e cartelle qui (es. aggiungi `"target": "entities/targets"` per sotto-cartelle) e il server segue. Nient'altro è hard-coded sul dominio.

> 🧵 **Fil rouge → il tuo dominio.** Sostituisci mentalmente: *persona/org* → le entità che ti interessano; *Project Atlas* → le tue iniziative; *knowledge-management* → i tuoi temi; *Zettelkasten Method* → i tuoi metodi/framework; *il libro di Ahrens* → i tuoi documenti. La struttura non cambia.

---

## 9. Checklist per l'agent (partire da zero)

Se sei l'agent che costruisce questa wiki, ecco i passi concreti:

- [ ] Chiedi all'utente: **dominio**, quali **tipi di "cose"** tiene, il **vocabolario di tag** iniziale, e il livello di **hosting** voluto (Tier 0/1/2).
- [ ] Crea la struttura cartelle: `wiki/{entities,projects,topics,concepts,sources,briefings}/`, più `index.md` e `log.md` vuoti.
- [ ] Compila `CLAUDE.md` dal template con le risposte dell'utente. È la cosa più importante: senza, i workflow non sono definiti.
- [ ] `git init`, primo commit. Suggerisci di aprire la cartella in Obsidian.
- [ ] Se l'utente ha già documenti: proponi di **ingerirne uno** come prova end-to-end (workflow `ingest`), mostrando i takeaway prima di scrivere.
- [ ] Se vuole l'MCP: configura `mcp-server/` (stdio per personale, HTTP per team) seguendo `mcp-server/README.md`.
- [ ] Dopo qualche ingest, proponi un `lint` per validare la coerenza.
- [ ] **Non** introdurre un DB o embedding finché l'utente non incontra un limite reale di scala (vedi §1, §7).

---

## Appendice — Glossario

- **Frontmatter** — blocco YAML in testa a un `.md` con i metadati strutturati.
- **Wikilink** — `[[Nome Pagina]]`, collegamento interno. La densità dei link è il valore della wiki.
- **Ingest** — il processo di leggere un raw e produrne una source page + aggiornare le entity.
- **Filing back** — salvare una buona risposta a una query come pagina `concept`/`briefing`, così la conoscenza si accumula.
- **MCP (Model Context Protocol)** — standard aperto Anthropic per connettere tool esterni a un LLM (<https://modelcontextprotocol.io>).
- **stdio / HTTP transport** — i due modi in cui un client MCP parla al server: processo locale (stdio) vs URL remoto (HTTP).
- **Shelf-life** — durata di validità di una pagina; oltre, è "stale" e de-prioritizzata nelle query (ma non cancellata).
- **Human-in-the-loop (HITL)** — l'agent chiede conferma umana prima di azioni strutturali o irreversibili.
- **Object storage (S3/R2)** — storage di file scalabile e durabile; usato come primary persistent storage nel Tier 1 per essere data-loss-proof.
- **Cerchio 1/2/3** — raw immutabili / wiki markdown / index DB opzionale (§2).

---

*Questo blueprint è la versione generalizzata di un sistema reale in produzione. Adattalo, non venerarlo: le scelte qui sono buone default, non dogmi. Quando cambi una decisione, scrivi il perché — la prossima persona (o agent) che eredita la KB te ne sarà grata.*
