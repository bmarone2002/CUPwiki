#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "mcp-server" / "server.py"
WIKI_PATH = ROOT / "wiki"

spec = importlib.util.spec_from_file_location("wiki_server", SERVER_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
index = module.WikiIndex(WIKI_PATH)

scenarios = {
    "search_gas_italgas": {
        "query": "Italgas devoluzione gratuita Punto Fisco",
        "results": index.search("Italgas devoluzione gratuita Punto Fisco")[:3],
    },
    "search_idrico_fognatura": {
        "query": "acqua fognatura due distinti servizi",
        "results": index.search("acqua fognatura due distinti servizi")[:3],
    },
    "related_portici": {
        "page": "Comune di Portici (NA)",
        "results": index.list_related("Comune di Portici (NA)")[:6],
    },
    "get_briefing_energia": {
        "page": "Strategia difensiva — CUP servizi di rete (energia elettrica)",
        "result": index.get_page("Strategia difensiva — CUP servizi di rete (energia elettrica)", type_="briefing"),
    },
    "list_memorie": {
        "doc_type": "memoria",
        "results": index.list_sources("memoria", None)[:5],
    },
}

summary = {
    "search_gas_italgas_top": [x["name"] for x in scenarios["search_gas_italgas"]["results"]],
    "search_idrico_fognatura_top": [x["name"] for x in scenarios["search_idrico_fognatura"]["results"]],
    "related_portici_top": [x["name"] for x in scenarios["related_portici"]["results"]],
    "get_briefing_energia_found": scenarios["get_briefing_energia"]["result"] is not None,
    "list_memorie_top": [x["name"] for x in scenarios["list_memorie"]["results"]],
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
