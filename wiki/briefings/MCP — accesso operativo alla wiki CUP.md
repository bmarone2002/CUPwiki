---
type: briefing
tags: [mcp, infrastruttura, claude-desktop]
sensitivity: internal
bias: internal
confidence: verified
updated_at: 2026-07-27
---

# MCP — accesso operativo alla wiki CUP

Playbook infrastrutturale: **come** collegare Claude Desktop (o altro client MCP) alla wiki markdown del progetto, e **quando** ha senso restare in locale vs passare a un server hostato.

## Risposta sintetica

**Oggi basta il locale.** Il server MCP in modalità **stdio** (processo Python sul PC dell'operatore) è già validato sulla wiki reale (`wiki/`) e copre query, lettura di briefing/concept/contenziosi e — con approvazione esplicita — scrittura.

**L'hosting non è un prerequisito** per far funzionare il sistema. Diventa utile solo quando servono **più persone** sulla **stessa wiki aggiornata** senza installare Python su ogni postazione, oppure quando si vuole un punto di accesso centralizzato con token condiviso.

## Due modalità (stesso codice, transport diverso)

| | **Locale (stdio)** — scelta attuale | **Hostato (HTTP)** — upgrade futuro |
|---|---|---|
| **Chi** | 1 operatore / 1 PC | Team, più analisti |
| **Setup client** | Python 3.10+ + blocco JSON in Claude Desktop | Solo URL + Bearer token (+ Node per `mcp-remote`) |
| **Dove vive la wiki** | Cartella `wiki/` sul disco locale (repo git) | Volume/container sul server; opz. sync git auto-push |
| **Stato CUP** | ✅ testato (smoke + 5 scenari operativi) | Codice presente, **non ancora deployato** per CUP |
| **Dati sensibili** | Restano sul PC; niente esposizione di rete | Richiede TLS, auth, valutazione GDPR/PA su dati `confidential` |
| **Quando preferirlo** | Uso quotidiano redazione/query, fase pilota | 3+ utenti, wiki unica condivisa, onboarding semplice |

Riferimento tecnico generico: [`mcp-server/README.md`](../../mcp-server/README.md), [`BLUEPRINT.md`](../../BLUEPRINT.md) §6–7.

## Setup locale attuale (validato)

- **Python:** 3.12 in `.venv-mcp/` (creato con `uv` locale in `tools/uv-bin/`).
- **Test:** `./tests/run_mcp_tests.sh` → smoke + demo operativa su gas, idrico, Portici, energia, memorie.
- **Config Claude Desktop:** blocco `cup-wiki` in [`mcp-server/claude_desktop_config_cup.json`](../../mcp-server/claude_desktop_config_cup.json).
- **Report:** [`tests/results/mcp_smoke_report.md`](../../tests/results/mcp_smoke_report.md), [`tests/results/mcp_operational_read_report.md`](../../tests/results/mcp_operational_read_report.md).

Dopo aver incollato la config e riavviato Claude (**Quit** completo, poi nuova chat), compaiono 7 tool `cup-wiki__wiki_*`.

## Criteri per passare all'hosting (Tier 2)

Valutare HTTP hostato **solo se** almeno uno di questi diventa vero:

1. **Più operatori** devono interrogare/aggiornare la stessa wiki senza clonare repo e venv.
2. **Onboarding** deve essere “incolla URL + token”, non “installa Python 3.12”.
3. Serve **write centralizzato** con `MCP_GIT_AUTO_PUSH=true` (ogni modifica MCP → commit+push automatico).
4. La wiki resta su **un solo server** mentre i client sono vari (anche fuori sede).

**Prima di hostare** su dati CUP (`sensitivity: confidential` su contenziosi e memorie):

- TLS obbligatorio (reverse proxy).
- Bearer token forte (`MCP_BEARER_TOKEN`).
- Policy su chi può scrivere (Claude chiede conferma, ma il token va protetto).
- Backup/versionamento: git + eventuale object storage (vedi BLUEPRINT Tier 1).

**Non hostare** solo “perché suona più professionale”: il locale è pienamente operativo e più semplice da governare in fase pilota.

## Sincronizzazione wiki tra locale e team

Con **solo locale**, ogni macchina ha la propria copia di `wiki/` nel repo git. Aggiornamenti = pull/push git tra operatori (come oggi con Obsidian/editor).

Con **hosting + git auto-push**, le write MCP sul server diventano commit sul remote; i locali fanno pull. È il modello da adottare quando il team cresce.

## Tool MCP disponibili (7)

**Lettura:** `wiki_search`, `wiki_get_page`, `wiki_list_related`, `wiki_list_sources`  
**Scrittura:** `wiki_create_page`, `wiki_append_to_section`, `wiki_update_frontmatter` (approvazione umana in Claude Desktop)

Affinamenti già applicati al server: supporto `subtype` oltre a `doc_type` per le memorie; esclusione di `log` e `index` da search/related (restano raggiungibili con get esplicito).

## Gap noti

- Corpus **energia elettrica** ancora sottile (1 contenzioso): il MCP funziona, ma le risposte su quella materia sono povere finché non si ingessano altri raw.
- Tool di **scrittura** MCP: non testati in produzione sulla wiki reale; usare solo dopo HITL o su sandbox (`example-wiki/`).
- **Dockerfile / deploy HTTP** per CUP: non ancora preparato (il codice HTTP in `server.py` c’è, manca il packaging operativo).

## Decisione operativa (2026-07-27)

**Restare in locale (stdio)** finché l’uso è principalmente di uno o pochi operatori sullo stesso repo git. Rivalutare l’hosting quando entra un secondo/terzo analista che deve usare Claude Desktop sulla wiki senza setup Python, o quando serve un unico corpus sempre aggiornato via MCP write centralizzato.
