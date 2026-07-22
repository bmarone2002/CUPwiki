# LLM Wiki — Starter Kit

Una **base da dare a un agent AI** (Claude Code, Cursor, Copilot, …) perché ti costruisca la tua knowledge base interrogabile: una wiki in **markdown puro** che un LLM legge, scrive e mantiene, esposta come tool nativi via un **server MCP**.

È la versione generalizzata e dominio-neutra di un sistema reale in produzione. Niente RAG, niente database obbligatorio al Day 1: una cartella di `.md`, `git`, [Obsidian](https://obsidian.md) e (quando vuoi) un server MCP.

> 🤖 **Sei un agente AI che apre questo kit?**
> 1. Leggi **[`BLUEPRINT.md`](BLUEPRINT.md)** per intero — è il concetto, l'architettura, l'hosting e l'MCP.
> 2. Segui la **checklist §9** del blueprint per costruire la wiki dell'utente.
> 3. Compila **[`CLAUDE.md.template`](CLAUDE.md.template)** col dominio dell'utente: è il cervello operativo della loro wiki.
> 4. Usa **[`example-wiki/`](example-wiki/)** come modello concreto già funzionante.

## Cosa c'è dentro

```
llm-wiki-starter-kit/
├── README.md              ← questo file (entry point)
├── BLUEPRINT.md           ← ⭐ il documento principale: concetto + architettura + hosting + MCP
├── CLAUDE.md.template     ← system prompt da compilare col tuo dominio
├── mcp-server/            ← server MCP riusabile (7 tool, stdio + HTTP), generico
│   ├── server.py
│   ├── requirements.txt
│   ├── README.md          ← install + hosting dell'MCP
│   └── claude_desktop_config_snippet.json
└── example-wiki/          ← una wiki d'esempio completa e auto-consistente (KB di ricerca)
    ├── CLAUDE.md          ← il template, già compilato (esempio)
    ├── index.md · log.md
    └── wiki/              ← entities / projects / topics / concepts / sources, fittamente linkate
```

## I 4 pezzi, in una riga

| Pezzo | A cosa serve |
|---|---|
| **`BLUEPRINT.md`** | Capire *cos'è* una LLM Wiki e *come* costruirla/hostarla. Leggilo per primo. |
| **`CLAUDE.md.template`** | Insegna all'agent la struttura e i workflow della *tua* wiki. Da compilare. |
| **`mcp-server/`** | Far leggere/scrivere la wiki a Claude Desktop in linguaggio naturale. |
| **`example-wiki/`** | Un modello concreto: copialo, svuotalo, riempilo col tuo dominio. |

## Quick start (umano, ~un pomeriggio)

1. **Leggi [`BLUEPRINT.md`](BLUEPRINT.md).** È corto e spiega tutte le scelte.
2. **Crea il tuo repo wiki**: copia `example-wiki/` come base (o parti da zero con le cartelle `wiki/{entities,projects,topics,concepts,sources,briefings}/`).
3. **Compila `CLAUDE.md`**: copia `CLAUDE.md.template` → `CLAUDE.md` nella root del tuo repo e riempi i `{{PLACEHOLDER}}` (dominio, tipi, tag, lingua).
4. **`git init`** + apri la cartella in [Obsidian](https://obsidian.md). **Hai già una LLM wiki usabile** (Tier 0 del blueprint, zero infrastruttura).
5. **(Opzionale) Collega l'MCP**: segui [`mcp-server/README.md`](mcp-server/README.md) per parlare alla wiki da Claude Desktop.

## Come darlo a un agent

Apri l'agent nella cartella del kit (o del tuo nuovo repo) e digli, ad esempio:

> «Leggi `BLUEPRINT.md` e `CLAUDE.md.template`. Voglio costruire una LLM wiki per **\<il tuo dominio\>**. Fammi le domande della checklist §9, poi imposta la struttura e compila il mio `CLAUDE.md`.»

Da lì l'agent può eseguire i workflow **ingest** (dai un documento → ne esce conoscenza strutturata), **query** (domanda → risposta citata) e **lint** (manutenzione), tutti definiti nel `CLAUDE.md`.

## Provare subito l'MCP sull'esempio

Il server gira out-of-the-box sulla `example-wiki/`:

```bash
pip install -r mcp-server/requirements.txt
# configura claude_desktop_config.json (vedi mcp-server/README.md), poi in Claude Desktop:
#   "Cerca nella wiki cosa sappiamo su zettelkasten"
#   "Mostrami tutto quello collegato a Project Atlas"
```

## Filosofia (in 5 punti)

1. **Time-to-value sopra purezza architetturale.** Una cartella di `.md` batte un DB che non hai ancora.
2. **Conoscenza compilata.** Sintetizzi una volta, resta scritta e linkata. Le esplorazioni *compoundano*.
3. **Schema esplicito.** Il frontmatter rende le query deterministiche senza un database.
4. **Niente magia.** Markdown, git, grep, un piccolo server Python. Tutto ispezionabile e portabile.
5. **Complessità solo quando il dolore è reale.** RAG/embedding/DB si aggiungono dopo, se e quando servono.

Dettagli, trade-off e scala di hosting: tutto in [`BLUEPRINT.md`](BLUEPRINT.md).
