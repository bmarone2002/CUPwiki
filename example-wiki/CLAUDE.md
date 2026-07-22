# Research KB — Schema della LLM Wiki

> Questo è un **esempio di `CLAUDE.md.template` compilato**, nel dominio fil rouge del kit (una KB personale di ricerca). Mostra come appare il template una volta riempito. Usalo come riferimento, non come tuo file di configurazione.

Questo file dice a Claude come è strutturata questa wiki e quali workflow eseguire (ingest, query, lint).

## Identità

Questa wiki è la **memoria di ricerca personale** di chi la tiene: persone (autori, esperti), organizzazioni (aziende, tool), temi che studio, i miei progetti e i documenti che leggo.

L'obiettivo è che **"tutto quello che so su X" sia sempre a una domanda di distanza**, e che ogni cosa imparata resti scritta e linkata invece di evaporare.

È una LLM Wiki in markdown puro (niente DB, niente RAG). Vedi `../BLUEPRINT.md` per il razionale.

## Architettura a 3 cerchi

1. **Raw** (immutabile): PDF dei paper, screenshot, note grezze in `../raw/`. Leggo, non modifico mai.
2. **Wiki** (`wiki/`): pagine markdown create e mantenute da Claude.
3. **Index/metadata**: non implementato (singolo utente, poche centinaia di pagine).

## Tipi di pagina

| `type` | Cos'è | Cartella |
|---|---|---|
| `entity` | Persone e organizzazioni (campo `subtype: person\|org`) | `entities/` |
| `project` | Le mie iniziative di ricerca | `projects/` |
| `topic` | Aree tematiche che studio | `topics/` |
| `concept` | Metodi, framework, sintesi derivate | `concepts/` |
| `source` | 1 documento letto = 1 file | `sources/` |
| `briefing` | Sintesi derivata da N pagine | `briefings/` |

### Regola fondamentale: `entity` ≠ `project`

Una cosa del mondo e un *mio* contesto su quella cosa sono due pagine distinte, linkate. Es: `entities/Niklas Luhmann.md` (fatti pubblici) ≠ `projects/Project Atlas.md` (il mio sforzo, che linka `[[Niklas Luhmann]]`).

## Naming

- Forma naturale con spazi: `Niklas Luhmann.md`, `Zettelkasten Method.md`.
- Temi: `kebab-case` → `knowledge-management.md`.
- Source: `YYYY-MM-DD <slug>.md`.

## Frontmatter

Comune: `type`, `tags`, `sensitivity`, `updated_at`. Le `source` aggiungono `source_path`, `ingested_at`, `as_of_date`, `bias`, `confidence`, `shelf_life_months`, `expires_at`.

## Tassonomia (`tags`)

Vocabolario controllato. Tag nuovo → chiedo conferma prima di crearlo.
- **Aree**: knowledge-management, note-taking, productivity, learning-science
- **Formati fonte**: book, paper, article, video, talk

## Sistema metadata

- **bias**: `neutral` (fonti indipendenti), `internal` (note mie), `partisan` (materiale promozionale).
- **confidence** (la certezza cresce salendo): `verified` (fonti primarie), `estimated` (stime con base), `claimed` (non verificato).
- **sensitivity**: `public` → `internal` → `confidential` → `restricted`. Default `internal`.
- **shelf_life_months**: oltre `expires_at` la pagina resta ma è stale per le query.

## Workflow: ingest

"ingerisci [file]" → leggo il raw → mostro 3–5 takeaway e **chiedo conferma** → creo la source page (summary 200–500 parole + takeaway, linkando le entità) → aggiorno/creo le entity/topic/concept (contraddizioni: tengo entrambe + "⚠ Contraddizioni da verificare", mai sovrascrivere) → aggiorno `index.md` → appendo a `log.md` → riassumo + suggerisco gap.

## Workflow: query

Domanda → leggo `index.md` → leggo per intero le pagine candidate → sintetizzo con citazioni `[[Page]]` (mai inventare; se non so, lo dico e propongo cosa ingerire) → **filing back**: se la risposta è di valore, propongo di salvarla come `concept`/`briefing` → appendo a `log.md`.

## Workflow: lint

Cerco: contraddizioni, pagine orfane, concept impliciti, temi sotto-coperti, stale claim, bias estremi. Report azionabile + `log.md`.

## Stile

- **Italiano** ovunque. Prosa concisa, niente marketing.
- Ogni claim importante con fonte: `... ([[Source]])`.
- **Linko aggressivamente** con `[[Page Name]]`. Un link a pagina inesistente è OK: segnala un buco.

## Governance

- Mai modificare i raw. Mai sovrascrivere claim senza note. HITL su nuovi tag / cancellazioni / declassificazione `sensitivity`. `bias: internal` va giustificato. `sensitivity` default `internal`.
