# Report smoke test MCP

## Ambiente usato
- runtime locale gestito con `uv`
- Python: `3.12.13`
- venv: `.venv-mcp`

## Comando eseguito
`/Users/bmarone/Desktop/llm-wiki-starter-kit/.venv-mcp/bin/python tests/smoke_mcp_read.py`

## Esito
```json
{
  "status": "ok",
  "search_portici_count": 4,
  "get_page_gas_briefing_found": true,
  "related_portici_count": 9,
  "list_sources_memoria_count": 20
}
```

## Verifiche coperte
- `wiki_search`
- `wiki_get_page`
- `wiki_list_related`
- controllo supplementare su `wiki_list_sources("memoria")`

## Nota tecnica emersa e corretta
Durante il primo run reale, `wiki_list_sources("memoria")` restituiva `0` risultati perché il server leggeva solo `doc_type`, mentre la wiki reale usa soprattutto `subtype`. Il server è stato corretto in `mcp-server/server.py` per supportare entrambi.

## Conclusione
Il server MCP è ora testato in lettura su runtime compatibile e risulta funzionante sui principali tool di consultazione della wiki reale.
