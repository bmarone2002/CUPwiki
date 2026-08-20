#!/usr/bin/env python3
"""
wiki-mcp  —  server MCP generico per una LLM Wiki in markdown.

Espone 7 tool a Claude Desktop (o qualsiasi client MCP). È lo scheletro
riusabile del kit: dominio-neutro, niente token/URL reali. Adattalo cambiando
solo `_TYPE_DIRS` (sotto) e, se vuoi, i campi frontmatter mostrati nei risultati.

READ (4)
--------
  wiki_search(query, tags?, type?, sensitivity?)
    Cerca per keyword in nome file, frontmatter e contenuto di tutte le pagine.

  wiki_get_page(name, type?)
    Legge il contenuto completo di una pagina per nome esatto o fuzzy.

  wiki_list_related(name)
    Tutte le pagine collegate a una data: chi la linka via [[wikilink]],
    chi la referenzia nel frontmatter. È il "tutto quello che so su X".

  wiki_list_sources(doc_type?, max_age_months?)
    Lista le source page filtrate per tipo documento e/o età massima.

WRITE (3)
---------
  wiki_create_page(type, name, frontmatter, content, overwrite?)
    Crea una nuova pagina sotto la cartella corretta per tipo. Errore se esiste
    già (a meno di overwrite=true). Scrittura atomica.

  wiki_append_to_section(page_name, section_heading, content, create_if_missing?)
    Append a una sezione '## <heading>' di una pagina. La crea se manca.

  wiki_update_frontmatter(page_name, fields, remove_keys?)
    Patch field-level del frontmatter YAML (merge, non sovrascrive il corpo).
    'updated_at' bumpato automaticamente.

Safety
------
- Scritture validate per path traversal: il path risolto deve restare sotto WIKI_DIR.
- Filename sanitizzato (caratteri filesystem-forbidden rimossi, niente '..').
- Audit log su log.md (sibling della cartella wiki) con timestamp + operazione.
- Scrittura atomica: tempfile + rename, niente file corrotti su crash a metà.
- (Hosted) git auto-push opzionale via env MCP_GIT_AUTO_PUSH=true.

Setup rapido (stdio, locale) — claude_desktop_config.json:

    "mcpServers": {
      "my-wiki": {
        "command": "python",
        "args": ["<path>/mcp-server/server.py"],
        "env": { "WIKI_DIR": "<path>/wiki" }
      }
    }

Dipendenze: pip install -r requirements.txt   (mcp, pyyaml, python-frontmatter)
Per il transport HTTP servono anche: uvicorn, starlette.
"""

import argparse
import asyncio
import os
import re
import subprocess
from datetime import datetime, date
from pathlib import Path
from typing import Any

import frontmatter  # python-frontmatter
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------

# Default: la wiki d'esempio del kit (così il server gira out-of-the-box).
# In produzione, sovrascrivi con l'env var WIKI_DIR.
_DEFAULT_WIKI = Path(__file__).resolve().parent.parent / "example-wiki" / "wiki"
WIKI_DIR = Path(os.environ.get("WIKI_DIR", str(_DEFAULT_WIKI)))

SERVER_NAME       = os.environ.get("MCP_SERVER_NAME", "wiki-mcp")
MAX_EXCERPT_CHARS = 600   # lunghezza excerpt per pagina nei risultati di ricerca
MAX_RESULTS       = 15    # risultati massimi per query di ricerca

# ---------------------------------------------------------------------------
# Mapping type -> sotto-directory dentro la wiki.
#
#   >>> QUESTO È IL PUNTO DI ADATTAMENTO AL TUO DOMINIO <<<
#
# Cambia chiavi e cartelle qui per riflettere i tuoi tipi di pagina. Esempi:
#   - sotto-cartelle per entity:  "person": "entities/people", "org": "entities/orgs"
#   - dominio investimenti:       "target": "entities/targets", "deal": "deals"
# Nient'altro nel server è hard-coded sul dominio.
# ---------------------------------------------------------------------------

TYPE_DIRS = {
    "entity":   "entities",
    "project":  "projects",
    "topic":    "topics",
    "concept":  "concepts",
    "source":   "sources",
    "briefing": "briefings",
}

# ---------------------------------------------------------------------------
# Indicizzazione in memoria
# ---------------------------------------------------------------------------

class WikiIndex:
    """Carica tutte le pagine wiki in memoria e offre metodi di lettura/scrittura."""

    _FORBIDDEN_CHARS = '<>:"/\\|?*\x00'  # caratteri vietati nei nomi file cross-platform
    _AUXILIARY_PAGES = {"log", "index"}

    def __init__(self, wiki_dir: Path):
        self.wiki_dir = wiki_dir
        self.pages: list[dict] = []
        self.load()

    def load(self):
        """Legge tutti i .md sotto wiki_dir e costruisce l'indice."""
        self.pages = []
        if not self.wiki_dir.exists():
            return
        for md_path in self.wiki_dir.rglob("*.md"):
            try:
                post = frontmatter.load(str(md_path))
                # path relativo includendo il nome della cartella wiki (es. "wiki/...")
                relative = md_path.relative_to(self.wiki_dir.parent)
                self.pages.append({
                    "path":    str(relative).replace("\\", "/"),
                    "name":    md_path.stem,
                    "meta":    dict(post.metadata),
                    "content": post.content,
                    "mtime":   md_path.stat().st_mtime,
                })
            except Exception:
                pass  # un file malformato non deve far cadere l'indice intero

    def reload(self):
        self.load()

    # =======================================================================
    # READ
    # =======================================================================

    def search(self, query: str, tags: list[str] | None = None,
               type_: str | None = None, sensitivity: str | None = None) -> list[dict]:
        """Cerca query in nome, frontmatter e contenuto. Ordina per score."""
        self.reload()
        query_lower = query.lower()
        keywords = [w for w in re.split(r"[\s,;]+", query_lower) if len(w) > 2]

        results = []
        for page in self.pages:
            meta = page["meta"]
            if page["name"].lower() in self._AUXILIARY_PAGES:
                continue

            # Filtri opzionali
            if tags:
                page_tags = meta.get("tags", [])
                if isinstance(page_tags, str):
                    page_tags = [page_tags]
                page_tags_lower = [str(x).lower() for x in page_tags]
                if not any(t.lower() in page_tags_lower for t in tags):
                    continue
            if type_ and str(meta.get("type", "")).lower() != type_.lower():
                continue
            if sensitivity and str(meta.get("sensitivity", "")).lower() != sensitivity.lower():
                continue

            # Score: nome (10) > frontmatter (5) > occorrenze nel corpo (1 each)
            score = 0
            name_lower = page["name"].lower()
            content_lower = page["content"].lower()
            meta_str = str(meta).lower()
            for kw in keywords:
                if kw in name_lower:
                    score += 10
                if kw in meta_str:
                    score += 5
                score += content_lower.count(kw)
            if score == 0:
                continue

            results.append({
                "name":        page["name"],
                "path":        page["path"],
                "type":        meta.get("type", ""),
                "tags":        meta.get("tags", []),
                "sensitivity": meta.get("sensitivity", ""),
                "updated_at":  str(meta.get("updated_at", "")),
                "score":       score,
                "excerpt":     self._extract_excerpt(page["content"], keywords),
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:MAX_RESULTS]

    def get_page(self, name: str, type_: str | None = None) -> dict | None:
        """Trova la pagina più simile al nome richiesto (esatto, poi fuzzy)."""
        self.reload()
        name_lower = name.lower()

        for page in self.pages:  # match esatto
            if page["name"].lower() == name_lower:
                if type_ is None or str(page["meta"].get("type", "")).lower() == type_.lower():
                    return self._full_page(page)

        candidates = []  # match parziale
        for page in self.pages:
            pname = page["name"].lower()
            if name_lower in pname or pname in name_lower:
                if type_ is None or str(page["meta"].get("type", "")).lower() == type_.lower():
                    candidates.append(page)
        if candidates:
            candidates.sort(key=lambda p: len(p["name"]))  # preferisci il più specifico
            return self._full_page(candidates[0])
        return None

    def list_related(self, name: str) -> list[dict]:
        """Tutte le pagine collegate a `name`: la pagina stessa + chi la linka
        via [[wikilink]] o la referenzia nel frontmatter."""
        self.reload()
        nm = name.lower()
        results = []
        for page in self.pages:
            meta = page["meta"]
            if page["name"].lower() in self._AUXILIARY_PAGES:
                continue
            content_lower = page["content"].lower()
            meta_str = str(meta).lower()
            is_self = page["name"].lower() == nm
            # [[name]], [[name|alias]], [[name#section]] -> tutti iniziano con "[[name"
            linked = f"[[{nm}" in content_lower
            in_meta = nm in meta_str and not is_self
            if is_self or linked or in_meta:
                results.append({
                    "name":       page["name"],
                    "path":       page["path"],
                    "type":       meta.get("type", ""),
                    "updated_at": str(meta.get("updated_at", "")),
                    "self":       is_self,
                    "excerpt":    self._extract_excerpt(page["content"], [nm]),
                })
        # Ordina: prima la pagina stessa, poi per tipo
        type_order = {"project": 0, "source": 1, "entity": 2, "concept": 3, "topic": 4, "briefing": 5}
        results.sort(key=lambda x: (0 if x["self"] else 1, type_order.get(x["type"], 9)))
        return results

    def list_sources(self, doc_type: str | None = None,
                     max_age_months: int | None = None) -> list[dict]:
        """Lista le source page con filtri opzionali per tipo documento ed età."""
        self.reload()
        results = []
        today = date.today()
        for page in self.pages:
            meta = page["meta"]
            if meta.get("type") != "source":
                continue
            source_kind = meta.get("doc_type", meta.get("subtype", ""))
            if doc_type and str(source_kind).lower() != doc_type.lower():
                continue
            if max_age_months:
                ingested = meta.get("ingested_at")
                if ingested:
                    try:
                        ing = date.fromisoformat(ingested) if isinstance(ingested, str) else ingested
                        if (today - ing).days / 30 > max_age_months:
                            continue
                    except Exception:
                        pass
            results.append({
                "name":        page["name"],
                "path":        page["path"],
                "doc_type":    source_kind,
                "bias":        meta.get("bias", ""),
                "confidence":  meta.get("confidence", ""),
                "ingested_at": str(meta.get("ingested_at", "")),
                "expires_at":  str(meta.get("expires_at", "")),
                "sensitivity": meta.get("sensitivity", ""),
            })
        results.sort(key=lambda x: x["ingested_at"], reverse=True)
        return results

    # -----------------------------------------------------------------------
    # Helper di lettura
    # -----------------------------------------------------------------------

    def _extract_excerpt(self, content: str, keywords: list[str]) -> str:
        lines = content.split("\n")
        for line in lines:
            if any(kw in line.lower() for kw in keywords) and len(line.strip()) > 20:
                start = lines.index(line)
                return "\n".join(lines[start:start + 8]).strip()[:MAX_EXCERPT_CHARS]
        for line in lines:  # fallback: primo paragrafo non-vuoto, non-header
            if len(line.strip()) > 30 and not line.startswith("#"):
                return line.strip()[:MAX_EXCERPT_CHARS]
        return content[:MAX_EXCERPT_CHARS]

    def _full_page(self, page: dict) -> dict:
        return {"name": page["name"], "path": page["path"],
                "meta": page["meta"], "content": page["content"]}

    # =======================================================================
    # WRITE  (tutto sotto WIKI_DIR; atomico; loggato)
    # =======================================================================

    def _safe_filename(self, name: str) -> str:
        """Mantieni gli spazi (Obsidian-friendly), rimuovi caratteri vietati FS.
        Nessun path traversal possibile."""
        cleaned = "".join(c for c in (name or "").strip() if c not in self._FORBIDDEN_CHARS)
        cleaned = re.sub(r"\s+", " ", cleaned)
        if not cleaned:
            raise ValueError("Nome pagina vuoto o non valido dopo la sanitizzazione")
        if cleaned.startswith("."):
            raise ValueError("Il nome pagina non può iniziare con un punto")
        return cleaned

    def _resolve_path(self, page_type: str, name: str) -> Path:
        """(type, name) -> path assoluto sotto la wiki, garantito dentro WIKI_DIR."""
        if page_type not in TYPE_DIRS:
            raise ValueError(
                f"Tipo '{page_type}' non valido. Consentiti: {', '.join(sorted(TYPE_DIRS))}"
            )
        path = (self.wiki_dir / TYPE_DIRS[page_type] / f"{self._safe_filename(name)}.md").resolve()
        try:
            path.relative_to(self.wiki_dir.resolve())  # anti path-traversal
        except ValueError:
            raise ValueError("Tentativo di scrittura fuori da WIKI_DIR — rifiutato.")
        return path

    def _atomic_write(self, path: Path, content: str) -> None:
        """Scrittura atomica via tempfile + replace: un crash a metà non corrompe."""
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        try:
            tmp.write_text(content, encoding="utf-8", newline="\n")
            os.replace(tmp, path)
        finally:
            if tmp.exists():
                try: tmp.unlink()
                except OSError: pass

    def _audit_log(self, op: str, page_path: Path, details: str = "") -> None:
        """Append a log.md (sibling della wiki). Best-effort: errori swallow-ati."""
        log_path = self.wiki_dir.parent / "log.md"
        try:
            relative = page_path.relative_to(self.wiki_dir.parent).as_posix()
        except ValueError:
            relative = str(page_path)
        ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"\n## [{ts}] mcp_{op} | `{relative}`\n"
        if details:
            line += f"- {details}\n"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError:
            pass

    def _git_propagate(self, op: str, page_path: Path, details: str = "") -> None:
        """Auto commit+push delle modifiche al remote (solo se MCP_GIT_AUTO_PUSH=true).
        Best-effort: ogni step è try/except, gli errori vanno su stderr senza
        bloccare la write. Pensato per la modalità hostata (container)."""
        if os.environ.get("MCP_GIT_AUTO_PUSH", "").lower() not in ("true", "1", "yes"):
            return
        repo_root = self.wiki_dir.parent
        branch = os.environ.get("MCP_GIT_BRANCH", "main")
        try:
            relative = page_path.relative_to(repo_root).as_posix()
        except ValueError:
            relative = str(page_path)

        def _run(cmd: list[str]) -> tuple[int, str]:
            try:
                p = subprocess.run(cmd, cwd=str(repo_root), capture_output=True,
                                   text=True, timeout=30,
                                   env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
                return p.returncode, (p.stdout + p.stderr).strip()
            except (subprocess.TimeoutExpired, OSError) as e:
                return 1, f"exec error: {e}"

        rc, out = _run(["git", "pull", "--rebase", "--autostash", "origin", branch])
        if rc != 0:
            _run(["git", "rebase", "--abort"])
            print(f"[mcp git] pull rebase fallito: {out[:200]}", flush=True)
            return
        rc, _ = _run(["git", "add", "-A"])
        if rc != 0:
            print("[mcp git] add fallito", flush=True)
            return
        msg = f"[mcp] {op} | {relative}" + (f"\n\n{details}" if details else "")
        rc, out = _run(["git", "commit", "-m", msg])
        if rc != 0:
            if "nothing to commit" not in out.lower():
                print(f"[mcp git] commit fallito: {out[:200]}", flush=True)
            return
        rc, out = _run(["git", "push", "origin", branch])
        if rc != 0 and "rejected" in out.lower():
            _run(["git", "pull", "--rebase", "--autostash", "origin", branch])
            rc, out = _run(["git", "push", "origin", branch])
        if rc != 0:
            print(f"[mcp git] push fallito: {out[:200]}", flush=True)
        else:
            print(f"[mcp git] OK push: {msg.splitlines()[0]}", flush=True)

    def _find_page(self, page_name: str) -> dict:
        """Trova una pagina per nome (esatto, poi fuzzy). Solleva se non c'è."""
        nm = page_name.strip().lower()
        target = next((p for p in self.pages if p["name"].lower() == nm), None)
        if not target:
            cands = [p for p in self.pages if nm in p["name"].lower()]
            if cands:
                cands.sort(key=lambda p: len(p["name"]))
                target = cands[0]
        if not target:
            raise FileNotFoundError(f"Pagina '{page_name}' non trovata nella wiki.")
        return target

    def _page_abspath(self, target_page: dict) -> Path:
        path = (self.wiki_dir.parent / target_page["path"]).resolve()
        try:
            path.relative_to(self.wiki_dir.resolve())
        except ValueError:
            raise ValueError("Path target fuori da WIKI_DIR — rifiutato.")
        return path

    def create_page(self, page_type: str, name: str, fm: dict, content: str,
                    overwrite: bool = False) -> dict:
        path = self._resolve_path(page_type, name)
        if path.exists() and not overwrite:
            raise FileExistsError(
                f"Pagina '{name}' ({page_type}) esiste già. Usa overwrite=true per "
                f"sovrascrivere (sconsigliato — meglio append/update)."
            )
        fm = dict(fm or {})
        fm.setdefault("type", page_type)
        fm["updated_at"] = date.today().isoformat()
        post = frontmatter.Post(content=content or f"# {name}\n\n_TBD_\n", **fm)
        text = frontmatter.dumps(post)
        if not text.endswith("\n"):
            text += "\n"
        self._atomic_write(path, text)
        self._audit_log("create_page", path, f"type={page_type}, frontmatter_keys={list(fm.keys())}")
        self._git_propagate("create_page", path, f"type={page_type}")
        self.reload()
        return {"ok": True, "path": str(path), "name": name, "type": page_type}

    def append_to_section(self, page_name: str, section_heading: str,
                          content: str, create_if_missing: bool = True) -> dict:
        self.reload()
        target_page = self._find_page(page_name)
        path = self._page_abspath(target_page)
        post = frontmatter.load(str(path))  # re-read fresco (evita race)
        body = post.content

        section_re = re.compile(rf"^(##\s+{re.escape(section_heading)}\s*)$",
                                flags=re.MULTILINE | re.IGNORECASE)
        m = section_re.search(body)
        if m:
            next_m = re.compile(r"^##\s+", flags=re.MULTILINE).search(body, pos=m.end())
            insert_at = next_m.start() if next_m else len(body)
            new_body = body[:insert_at].rstrip() + "\n\n" + content.rstrip() + "\n\n" + body[insert_at:]
        elif create_if_missing:
            new_body = body.rstrip() + f"\n\n## {section_heading}\n\n{content.rstrip()}\n"
        else:
            raise ValueError(
                f"Sezione '## {section_heading}' non trovata in '{page_name}'. "
                f"Usa create_if_missing=true per crearla."
            )

        post.content = new_body
        post.metadata["updated_at"] = date.today().isoformat()
        self._atomic_write(path, frontmatter.dumps(post) + "\n")
        self._audit_log("append_to_section", path, f"section='{section_heading}', +{len(content)} char")
        self._git_propagate("append_to_section", path, f"section='{section_heading}'")
        self.reload()
        return {"ok": True, "path": str(path), "name": target_page["name"],
                "section": section_heading, "section_existed": bool(m)}

    def update_frontmatter(self, page_name: str, fields: dict,
                           remove_keys: list[str] | None = None) -> dict:
        self.reload()
        target_page = self._find_page(page_name)
        path = self._page_abspath(target_page)
        post = frontmatter.load(str(path))
        old_fm = dict(post.metadata)
        for k, v in (fields or {}).items():
            post.metadata[k] = v
        for k in (remove_keys or []):
            post.metadata.pop(k, None)
        post.metadata["updated_at"] = date.today().isoformat()
        self._atomic_write(path, frontmatter.dumps(post) + "\n")
        changed_keys = list((fields or {}).keys()) + list(remove_keys or [])
        changed = {k: post.metadata.get(k) for k in changed_keys}
        self._audit_log("update_frontmatter", path, f"fields_changed={list(changed.keys())}")
        self._git_propagate("update_frontmatter", path, f"fields_changed={list(changed.keys())}")
        self.reload()
        return {"ok": True, "path": str(path), "name": target_page["name"],
                "changed": changed, "previous": {k: old_fm.get(k) for k in changed_keys}}


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------

app   = Server(SERVER_NAME)
index = WikiIndex(WIKI_DIR)

_TYPE_ENUM = sorted(TYPE_DIRS.keys())


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="wiki_search",
            description=("Cerca nella wiki per keyword (nome, frontmatter, contenuto). "
                         "Ritorna pagine con excerpt e metadati. Filtri opzionali: tags, type, sensitivity."),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword di ricerca."},
                    "tags": {"type": "array", "items": {"type": "string"},
                             "description": "Filtra per tag (es. ['knowledge-management']). Opzionale."},
                    "type": {"type": "string", "enum": _TYPE_ENUM,
                             "description": "Filtra per tipo pagina. Opzionale."},
                    "sensitivity": {"type": "string",
                                    "enum": ["public", "internal", "confidential", "restricted"],
                                    "description": "Filtra per sensitivity. Opzionale."},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="wiki_get_page",
            description="Legge il contenuto completo di una pagina per nome (esatto o fuzzy).",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome della pagina."},
                    "type": {"type": "string", "enum": _TYPE_ENUM,
                             "description": "Tipo per disambiguare omonimie. Opzionale."},
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="wiki_list_related",
            description=("Tutte le pagine collegate a una data: chi la linka via [[wikilink]] o la "
                         "referenzia nel frontmatter. È il 'tutto quello che so su X'."),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome della pagina di riferimento."},
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="wiki_list_sources",
            description=("Lista le source page con filtri opzionali per tipo documento ed età. "
                         "Utile per trovare cosa è stato ingerito e cosa è ormai stale."),
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_type": {"type": "string", "description": "Tipo documento (book, paper, article, ...)."},
                    "max_age_months": {"type": "integer", "description": "Solo source più recenti di N mesi."},
                },
            },
        ),

        # ──────────────────────── WRITE ────────────────────────
        types.Tool(
            name="wiki_create_page",
            description=("Crea una nuova pagina sotto la cartella corretta per il tipo. "
                         "Errore se esiste già (usa append/update per modifiche). Scrittura atomica."),
            inputSchema={
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": _TYPE_ENUM,
                             "description": "Tipo della pagina (determina la cartella)."},
                    "name": {"type": "string",
                             "description": "Nome senza estensione (.md aggiunto automaticamente). Spazi OK."},
                    "frontmatter": {"type": "object", "additionalProperties": True,
                                    "description": "Campi YAML (tags, sensitivity, bias, confidence, ...). "
                                                   "'type' e 'updated_at' iniettati automaticamente."},
                    "content": {"type": "string",
                                "description": "Corpo markdown. Convenzione: '# <Name>', sezioni '## ...', "
                                               "link [[Page Name]]."},
                    "overwrite": {"type": "boolean", "default": False,
                                  "description": "Se true sovrascrive (sconsigliato)."},
                },
                "required": ["type", "name", "content"],
            },
        ),
        types.Tool(
            name="wiki_append_to_section",
            description=("Append di contenuto in una sezione '## <heading>' di una pagina. "
                         "Se la sezione non esiste viene creata in fondo (salvo create_if_missing=false)."),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {"type": "string", "description": "Nome pagina target (esatto preferito)."},
                    "section_heading": {"type": "string", "description": "Titolo sezione dopo '## '."},
                    "content": {"type": "string", "description": "Contenuto da appendere (bullet o prosa)."},
                    "create_if_missing": {"type": "boolean", "default": True,
                                          "description": "Crea la sezione se manca."},
                },
                "required": ["page_name", "section_heading", "content"],
            },
        ),
        types.Tool(
            name="wiki_update_frontmatter",
            description=("Patch del frontmatter YAML: merge field-level (il corpo resta intatto). "
                         "'updated_at' bumpato. remove_keys per togliere campi."),
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {"type": "string", "description": "Nome pagina target."},
                    "fields": {"type": "object", "additionalProperties": True,
                               "description": "Campi da aggiungere/aggiornare."},
                    "remove_keys": {"type": "array", "items": {"type": "string"},
                                    "description": "Chiavi da rimuovere. Opzionale."},
                },
                "required": ["page_name", "fields"],
            },
        ),
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    import json

    if name == "wiki_search":
        results = index.search(arguments["query"], arguments.get("tags"),
                               arguments.get("type"), arguments.get("sensitivity"))
        if not results:
            text = f"Nessun risultato per: '{arguments['query']}'"
        else:
            lines = [f"## Ricerca: '{arguments['query']}' — {len(results)} pagine\n"]
            for r in results:
                lines.append(f"### {r['name']} `[{r['type']}]`")
                lines.append(f"**Path**: `{r['path']}`")
                if r.get("tags"):
                    lines.append(f"**Tag**: {r['tags']}")
                if r.get("updated_at"):
                    lines.append(f"**Aggiornato**: {r['updated_at']}")
                lines.append(f"\n{r['excerpt']}\n\n---")
            text = "\n".join(lines)
        return [types.TextContent(type="text", text=text)]

    elif name == "wiki_get_page":
        page = index.get_page(arguments["name"], arguments.get("type"))
        if not page:
            text = f"Pagina non trovata: '{arguments['name']}'"
        else:
            meta_str = json.dumps(page["meta"], ensure_ascii=False, indent=2, default=str)
            text = (f"# {page['name']}\n**Path**: `{page['path']}`\n\n"
                    f"## Frontmatter\n```yaml\n{meta_str}\n```\n\n## Contenuto\n\n{page['content']}")
        return [types.TextContent(type="text", text=text)]

    elif name == "wiki_list_related":
        results = index.list_related(arguments["name"])
        if not results:
            text = f"Nessuna pagina collegata a: '{arguments['name']}'"
        else:
            lines = [f"## Collegate a '{arguments['name']}' — {len(results)} pagine\n"]
            for r in results:
                tag = " ← questa" if r["self"] else ""
                lines.append(f"- **{r['name']}** `[{r['type']}]`{tag} — `{r['path']}`")
                if r.get("excerpt"):
                    lines.append(f"  > {r['excerpt'][:200]}")
            text = "\n".join(lines)
        return [types.TextContent(type="text", text=text)]

    elif name == "wiki_list_sources":
        results = index.list_sources(arguments.get("doc_type"), arguments.get("max_age_months"))
        if not results:
            text = "Nessuna source trovata con i filtri specificati."
        else:
            lines = [f"## Source — {len(results)} documenti\n",
                     "| Documento | Tipo | Bias | Confidence | Ingerito | Scade |",
                     "|---|---|---|---|---|---|"]
            for r in results:
                lines.append(f"| {r['name'][:40]} | {r['doc_type']} | {r['bias']} | "
                             f"{r['confidence']} | {r['ingested_at']} | {r['expires_at']} |")
            text = "\n".join(lines)
        return [types.TextContent(type="text", text=text)]

    # ──────────────────────── WRITE handlers ────────────────────────

    elif name == "wiki_create_page":
        try:
            r = index.create_page(arguments["type"], arguments["name"],
                                  arguments.get("frontmatter", {}) or {},
                                  arguments.get("content", ""),
                                  bool(arguments.get("overwrite", False)))
            text = f"OK: pagina '{r['name']}' creata.\n- type: {r['type']}\n- path: `{r['path']}`"
        except (FileExistsError, ValueError) as e:
            text = f"ERRORE: {type(e).__name__}: {e}"
        return [types.TextContent(type="text", text=text)]

    elif name == "wiki_append_to_section":
        try:
            r = index.append_to_section(arguments["page_name"], arguments["section_heading"],
                                        arguments["content"],
                                        bool(arguments.get("create_if_missing", True)))
            verb = "sezione esistente" if r["section_existed"] else "sezione creata"
            text = (f"OK: '{r['name']}' aggiornata ({verb}).\n"
                    f"- path: `{r['path']}`\n- section: ## {r['section']}")
        except (FileNotFoundError, ValueError) as e:
            text = f"ERRORE: {type(e).__name__}: {e}"
        return [types.TextContent(type="text", text=text)]

    elif name == "wiki_update_frontmatter":
        try:
            r = index.update_frontmatter(arguments["page_name"],
                                         arguments.get("fields", {}) or {},
                                         arguments.get("remove_keys") or [])
            changes = []
            for k, new in r["changed"].items():
                old = r["previous"].get(k)
                changes.append(f"- {k}: rimosso (era: {old!r})" if new is None
                               else f"- {k}: {old!r} -> {new!r}")
            text = (f"OK: frontmatter di '{r['name']}' aggiornato.\n- path: `{r['path']}`\n"
                    + ("\n".join(changes) if changes else "- nessun cambio"))
        except (FileNotFoundError, ValueError) as e:
            text = f"ERRORE: {type(e).__name__}: {e}"
        return [types.TextContent(type="text", text=text)]

    return [types.TextContent(type="text", text=f"Tool non riconosciuto: {name}")]


# ---------------------------------------------------------------------------
# Entry point — due transport:
#   stdio (default, locale): Claude Desktop con command/args
#   http  (hostato):         URL-based, multi-utente, Bearer auth via env
# ---------------------------------------------------------------------------

async def run_stdio():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def run_http(host: str, port: int, bearer_token: str | None):
    """Transport via streamable HTTP (uvicorn + starlette). Espone /mcp,
    protetto da Bearer token se settato. /healthz è sempre pubblico."""
    import uvicorn
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import JSONResponse, PlainTextResponse
    from starlette.routing import Mount
    from contextlib import asynccontextmanager
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

    manager = StreamableHTTPSessionManager(app=app, event_store=None, json_response=False)

    async def handle_mcp(scope, receive, send):
        await manager.handle_request(scope, receive, send)

    class BearerAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            if request.url.path.rstrip("/") == "/healthz":
                return await call_next(request)
            if bearer_token:
                header = request.headers.get("authorization", "")
                if not header.lower().startswith("bearer "):
                    return JSONResponse({"error": "missing_bearer_token"}, status_code=401)
                if header[7:].strip() != bearer_token:
                    return JSONResponse({"error": "invalid_bearer_token"}, status_code=403)
            return await call_next(request)

    async def healthz(scope, receive, send):
        await PlainTextResponse("ok")(scope, receive, send)

    @asynccontextmanager
    async def lifespan(_app):
        async with manager.run():
            yield

    middleware = [Middleware(BearerAuthMiddleware)] if bearer_token else []
    starlette_app = Starlette(
        routes=[Mount("/mcp", app=handle_mcp), Mount("/healthz", app=healthz)],
        middleware=middleware, lifespan=lifespan,
    )
    auth = "Bearer auth ON" if bearer_token else "AUTH DISABLED (solo dev/test isolato!)"
    print(f"[mcp-http] http://{host}:{port}/mcp  ({auth})", flush=True)
    print(f"[mcp-http] WIKI_DIR={WIKI_DIR}", flush=True)
    uvicorn.run(starlette_app, host=host, port=port, log_level="info")


def main():
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} — MCP server per LLM Wiki")
    parser.add_argument("--transport", choices=["stdio", "http"], default="stdio",
                        help="stdio = locale (default); http = hostato (URL, multi-utente)")
    parser.add_argument("--host", default="0.0.0.0", help="Host bind per http")
    parser.add_argument("--port", type=int, default=8765, help="Porta per http")
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(run_stdio())
    else:
        bearer = os.environ.get("MCP_BEARER_TOKEN", "").strip() or None
        if not bearer:
            print("[mcp-http] WARN: MCP_BEARER_TOKEN non settato — nessuna auth!", flush=True)
        run_http(args.host, args.port, bearer)


if __name__ == "__main__":
    main()
