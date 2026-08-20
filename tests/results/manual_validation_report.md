# Report di validazione manuale

## Esiti
| ID | Esito | Evidenze | Gap / azioni |
|---|---|---|---|
| Q1 | PASS | Recuperati `[[Soggettività passiva in via mediata]]` e `[[Strategia difensiva — CUP servizi di rete (telefonia)]]`. | Nessuno critico. |
| Q3 | PASS | Recuperati playbook gas e concept su devoluzione/autorriduzione. | Nessuno critico. |
| Q5 | PASS | Recuperato `[[Gestore del servizio idrico integrato non esente dal CUP]]` e il briefing idrico. | Nessuno critico. |
| Q6 | PASS con gap | Recuperati concept e briefing corretti; emerso wikilink mancante alla Cassazione 2180/2020. | Corretto creando `[[Cassazione 2180 2020 — acqua e fognatura nel SII]]`. |
| Q7 | PASS | Recuperati caso Bitritto, entity E-Distribuzione, concept POD/ARERA e briefing energia. | Nessuno critico. |
| Q8 | PASS | Recuperati `[[Natura tributaria del CUP]]` e fonti SS.UU./MEF, più briefing idrico. | Nessuno critico. |
| Q9 | PASS con gap | `Comune di Portici` aggrega correttamente gas + idrico + concessionario. | Rumore da `log`/`index` nei risultati aggregati; da valutare in futuro come miglioramento del motore di ricerca. |
| Q10 | PASS | Recuperati i 4 playbook di materia. | Nessuno critico. |
| D1 | PASS | Il playbook gas è presente e centrale per la redazione. | Nessuno critico. |
| D2 | PASS | Il playbook idrico e i concept chiave sono presenti. | Nessuno critico. |
| D3 | PASS | Il playbook telefonia è reperibile insieme ai concept maggiori. | Nessuno critico. |
| D4 | PASS | Il playbook energia è presente, seppur ancora su corpus minimo. | Gap non strutturale: materia ancora sottile, da densificare quando entreranno altri raw. |

## Sintesi
- La wiki è già testabile come base di `query` e `redazione memoria`.
- Il maggiore gap contenutistico emerso nel ciclo è stato corretto durante il lint mirato.
- I gap residui sono soprattutto di ergonomia del motore di lettura (`log`/`index` troppo rumorosi) e di ampiezza del corpus in `energia-elettrica`.
