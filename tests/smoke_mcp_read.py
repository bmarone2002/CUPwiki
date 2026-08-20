#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "mcp-server" / "server.py"
WIKI_PATH = ROOT / "wiki"

if sys.version_info < (3, 10):
    print(json.dumps({
        "status": "blocked",
        "reason": "mcp package requires Python >= 3.10",
        "python_version": sys.version.split()[0],
    }, ensure_ascii=False, indent=2))
    raise SystemExit(0)

spec = importlib.util.spec_from_file_location("wiki_server", SERVER_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

index = module.WikiIndex(WIKI_PATH)
summary = {
    "status": "ok",
    "search_portici_count": len(index.search("Portici", type_="entity")),
    "get_page_gas_briefing_found": index.get_page("Strategia difensiva — CUP servizi di rete (gas)", type_="briefing") is not None,
    "related_portici_count": len(index.list_related("Comune di Portici (NA)")),
    "list_sources_memoria_count": len(index.list_sources("memoria", None)),
}
print(json.dumps(summary, ensure_ascii=False, indent=2))
