# Report d'uso reale del server MCP

## Ambiente
- runtime locale gestito con `uv`
- Python `3.12.13`
- venv dedicato: `.venv-mcp`
- wiki testata: `wiki/` reale del progetto

## Scenari eseguiti

### 1. Ricerca gas / Italgas
**Input simulato:** `wiki_search("Italgas devoluzione gratuita Punto Fisco")`

**Top risultati:**
1. `Strategia difensiva — CUP servizi di rete (gas)`
2. `Devoluzione gratuita parziale degli impianti gas non basta`
3. `2026-07-27 Memoria Sessa Aurunca c. Italgas Reti (Trib. Santa Maria Capua Vetere)`

**Valutazione:** molto buona. Il server porta prima sul briefing e poi sul concept giusto.

### 2. Ricerca idrico / acqua-fognatura
**Input simulato:** `wiki_search("acqua fognatura due distinti servizi")`

**Top risultati:**
1. `Merciari — Due distinti servizi di rete nel SII`
2. `Due distinti servizi di rete nel servizio idrico integrato`
3. `Strategia difensiva — CUP servizi di rete (idrico)`

**Valutazione:** buona. Il risultato è utile e coerente; l'articolo Merciari emerge prima del concept, ma resta una risposta sensata.

### 3. Aggregazione per entity
**Input simulato:** `wiki_list_related("Comune di Portici (NA)")`

**Top risultati:**
1. `Comune di Portici (NA)`
2. `2025-10-30 Memoria GE.SE.T. Portici c. Italgas Reti (Trib. Napoli)`
3. `2025-10-03 Comparsa Portici c. GORI (Trib. Napoli)`
4. `GE.SE.T. Italia S.p.A.`
5. `GORI S.p.A.`
6. `Comune di Portici c. GORI — Trib. Napoli RG 15429-2025`

**Valutazione:** buona. Dopo la correzione del server, `log` e `index` non inquinano più search/related (restano raggiungibili con `wiki_get_page` esplicito).

### 4. Apertura di un briefing
**Input simulato:** `wiki_get_page("Strategia difensiva — CUP servizi di rete (energia elettrica)", type="briefing")`

**Esito:** trovato correttamente.

**Valutazione:** buona. Il tool individua il playbook di materia come atteso.

### 5. Lista fonti per subtipo memoria
**Input simulato:** `wiki_list_sources("memoria")`

**Top risultati:**
1. `2026-07-08 Memoria Cinisello Balsamo c. CAP Holding (CGT Milano)`
2. `2026-07-27 Memoria Aquara c. ASIS (Trib. Salerno)`
3. `2026-07-27 Memoria Cinisello Balsamo c. Unareti (CGT Milano)`
4. `2026-07-27 Memoria Bitritto c. E-Distribuzione (CGT Bari)`
5. `2025-10-30 Memoria GE.SE.T. Portici c. Italgas Reti (Trib. Napoli)`

**Valutazione:** buona. Questo scenario ha anche confermato la correzione del bug `doc_type` / `subtype` nel server.

## Correzioni fatte durante il test
- supporto a `subtype` oltre a `doc_type` in `mcp-server/server.py` per `wiki_list_sources`
- esclusione di `log` e `index` dai risultati di `search()` / `list_related()` nel server MCP

## Valutazione finale
Il layer MCP di lettura è già abbastanza solido per un primo uso reale. I risultati sono coerenti con la struttura della wiki e portano in alto briefing, concept e casi effettivamente utili.

## Gap residui
- l'efficacia di `energia-elettrica` resta vincolata alla povertà del corpus, non al server.
