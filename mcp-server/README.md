# wiki-mcp — server MCP per la tua LLM Wiki

Server [MCP](https://modelcontextprotocol.io) che espone una wiki markdown come **7 tool nativi** dentro Claude Desktop (o qualsiasi client MCP). Parli a Claude in linguaggio normale e lui legge/scrive la wiki senza che tu apra file o spieghi struttura.

Generico e riusabile: l'unico punto di adattamento al tuo dominio è il dizionario `TYPE_DIRS` in `server.py`.

## I 7 tool

**Lettura:** `wiki_search`, `wiki_get_page`, `wiki_list_related`, `wiki_list_sources`
**Scrittura:** `wiki_create_page`, `wiki_append_to_section`, `wiki_update_frontmatter`

(Dettaglio nel docstring in testa a `server.py`.)

## Setup rapido — repo CUP (wiki reale)

Su questa macchina il server è già stato validato con **Python 3.12** in `.venv-mcp/` (creato via `uv` locale in `tools/uv-bin/`).

```bash
# Rigenera venv + dipendenze (se manca .venv-mcp)
tools/uv-bin/uv python install 3.12
tools/uv-bin/uv venv --python 3.12 .venv-mcp
tools/uv-bin/uv pip install --python .venv-mcp/bin/python -r mcp-server/requirements.txt

# Test di lettura (smoke + demo operativo)
chmod +x tests/run_mcp_tests.sh
./tests/run_mcp_tests.sh
```

**Claude Desktop:** incolla il blocco `cup-wiki` da [`claude_desktop_config_cup.json`](claude_desktop_config_cup.json) nel tuo `claude_desktop_config.json`, poi riavvia Claude completamente e apri una **nuova chat**. Dovresti vedere 7 tool `cup-wiki__*`.

Report test: `tests/results/mcp_smoke_report.md`, `tests/results/mcp_operational_read_report.md`.


| Modalità | Per chi | Setup |
|---|---|---|
| **stdio (locale)** | Uso personale, un solo PC | Python + pip install + blocco JSON con `command`/`args` |
| **HTTP (hostato)** | Team, accesso via URL | Un container centrale; gli utenti incollano solo un URL + token |

---

## Modalità stdio (locale) — la più semplice

### 1. Installa le dipendenze

Prerequisito: **Python 3.10+**. Il package `mcp` non supporta Python 3.9.

```bash
python3.10 -m pip install -r mcp-server/requirements.txt
```

(Per il solo stdio bastano `mcp`, `pyyaml`, `python-frontmatter`; `uvicorn`/`starlette` servono solo all'HTTP.)

### 2. Trova il path assoluto di Python

```bash
# Windows
where python
# macOS / Linux
which python
```

### 3. Configura Claude Desktop

Apri `claude_desktop_config.json`:

| OS | Path |
|---|---|
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

Aggiungi (o estendi se `mcpServers` esiste già) — vedi anche `claude_desktop_config_snippet.json`:

```json
{
  "mcpServers": {
    "my-wiki": {
      "command": "C:/path/assoluto/python.exe",
      "args": ["C:/path/al/repo/mcp-server/server.py"],
      "env": {
        "WIKI_DIR": "C:/path/al/repo/wiki",
        "MCP_SERVER_NAME": "my-wiki"
      }
    }
  }
}
```

⚠️ **Importante**:
- Usa **forward slash `/`** anche su Windows nei path JSON.
- `command` deve essere il path **assoluto** del `python.exe` (no `python` sciolto).
- `WIKI_DIR` punta alla cartella `wiki/` (quella che contiene `entities/`, `projects/`, …), non alla root del repo. Se ometti `WIKI_DIR`, il server usa la wiki d'esempio del kit.

### 4. Riavvia Claude Desktop completamente

Non basta la X: **Quit** dalla tray (Windows) o **⌘Q** (macOS), poi riapri. I tool MCP si caricano solo al boot, e solo in chat nuove.

### 5. Verifica

In una **nuova chat** dovresti vedere 7 tool `my-wiki__*`. Test sicuro (sola lettura):

```
Cerca nella wiki le pagine che parlano di "zettelkasten"
Apri la pagina Niklas Luhmann
Mostrami tutto quello che è collegato a Project Atlas
```

I tool di **scrittura** chiedono conferma esplicita (Approve/Reject) in Claude Desktop prima di eseguire.

---

## Modalità HTTP (hostato) — per un team

Hosti il server come container; gli analisti incollano un URL + token, **niente Python locale**.

### Lato server (admin, una tantum)

Avvia il server in transport HTTP con un Bearer token:

```bash
export MCP_BEARER_TOKEN="$(openssl rand -hex 32)"   # genera e annota questo token
export WIKI_DIR=/app/wiki
export MCP_GIT_AUTO_PUSH=true   # opzionale: ogni write committa+pusha al repo
export MCP_GIT_BRANCH=main
python mcp-server/server.py --transport http --port 8765
```

Mettilo dietro un reverse proxy con TLS (es. Coolify/Traefik su un VPS) su un dominio tipo `https://mcp.tuodominio.com`, e verifica:

```bash
curl https://mcp.tuodominio.com/healthz   # atteso: ok
```

Variabili d'ambiente rilevanti:

| Env | Cosa fa |
|---|---|
| `WIKI_DIR` | Path alla cartella `wiki/`. |
| `MCP_BEARER_TOKEN` | Token condiviso che passi agli utenti. Se assente, il server gira **senza auth** (solo dev). |
| `MCP_SERVER_NAME` | Nome mostrato del server (default `wiki-mcp`). |
| `MCP_GIT_AUTO_PUSH` | `true` → ogni write fa commit+push automatico al remote. |
| `MCP_GIT_BRANCH` | Branch su cui pushare (default `main`). |

> Un `Dockerfile` non è incluso (dipende dal tuo hosting). Minimo: immagine Python 3.10+, `python -m pip install -r requirements.txt`, `CMD ["python","server.py","--transport","http","--port","8765"]`, `EXPOSE 8765`. Per il git auto-push, monta una credenziale git (PAT) nell'env del container.

### Lato client (utente)

Claude Desktop (oggi) parla solo stdio: il ponte verso un server HTTP è `npx mcp-remote`. Incolla nel `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-wiki": {
      "command": "npx",
      "args": [
        "-y", "mcp-remote",
        "https://mcp.tuodominio.com/mcp/",
        "--header", "Authorization:Bearer IL_TUO_TOKEN"
      ]
    }
  }
}
```

Prerequisito: Node.js (`npx --version` deve rispondere). Al primo lancio `npx` scarica `mcp-remote` (~10s), poi è cached.

---

## Safety

- **Anti path-traversal**: ogni scrittura resta sotto `WIKI_DIR`; `../` rifiutato.
- **Scrittura atomica**: tempfile + rename, niente file corrotti.
- **Audit log**: ogni write su `log.md` (sibling della wiki) con timestamp UTC.
- **Conferma umana**: Claude Desktop chiede approval per ogni write.
- **Create non distrugge**: `wiki_create_page` fallisce se la pagina esiste (serve `overwrite=true` esplicito).

## Troubleshooting

**Non vedo i tool** → Claude Desktop chiuso *completamente* (kill processo), riaperto, **nuova** chat. Controlla i log: `%APPDATA%\Claude\logs\mcp-server-my-wiki.log` (Win) / `~/Library/Logs/Claude/` (mac).

**`Server disconnected` + `UNABLE_TO_VERIFY_LEAF_SIGNATURE`** (rete aziendale con SSL inspection) → aggiungi `"env": {"NODE_TLS_REJECT_UNAUTHORIZED": "0"}` nel blocco JSON di `mcp-remote`. Soluzione pulita: chiedi all'IT di whitelistare il dominio (no SSL inspection).

**`npx: command not found`** → installa Node.js da [nodejs.org](https://nodejs.org) (LTS).

## Aggiungere un tool (per chi sviluppa)

1. Aggiungi un metodo a `WikiIndex` in `server.py`.
2. Aggiungi una `types.Tool(...)` in `handle_list_tools()` con il suo JSON Schema.
3. Aggiungi un branch `elif name == "wiki_xxx":` in `handle_call_tool()`.
4. Testa istanziando `WikiIndex(Path("example-wiki/wiki"))` direttamente in uno script.
