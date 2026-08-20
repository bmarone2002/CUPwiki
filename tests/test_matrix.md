# Matrice di test operativa della wiki

## Scopo
Questa matrice serve a validare i due workflow principali della repo:
- `query`: recupero di risposte citate e coerenti;
- `redazione memoria`: composizione di una bozza difensiva a partire da `concepts/`, `sources/`, `briefings/` e `contenziosi/`.

## Criteri di esito
- `PASS`: la wiki orienta bene, recupera i nodi giusti e non mostra buchi critici.
- `PASS con gap`: la risposta è impostabile, ma manca una fonte, un link o un concept di supporto.
- `FAIL`: la wiki non consente una risposta affidabile o porta a errore sostanziale.

## Query test
| ID | Materia | Prompt di test | Atteso minimo |
|---|---|---|---|
| Q1 | telefonia | "Qual è la linea difensiva più forte sulla soggettività passiva in via mediata nel CUP telefonia?" | recupero di `[[Soggettività passiva in via mediata]]` e del playbook telefonia |
| Q2 | telefonia | "Se WindTre sostiene che il WLR non integra occupazione materiale, quali precedenti interni usiamo?" | collegamento a `[[Utilizzo materiale e accesso virtuale (VULA)]]` e alle source WindTre |
| Q3 | gas | "Come contrastiamo Italgas quando si auto-riduce il canone invocando la devoluzione gratuita?" | recupero di `[[Autoriduzione unilaterale del CUP gas da parte del gestore]]` e del playbook gas |
| Q4 | gas | "Se il gestore contesta Punto Fisco e il metodo presuntivo nel gas, cosa usiamo?" | casi Casagiove / Portici / Sessa Aurunca |
| Q5 | idrico | "Perché il gestore in house del SII non è esente dal CUP?" | recupero di `[[Gestore del servizio idrico integrato non esente dal CUP]]` e dei casi UniAcque / Pavia Acque |
| Q6 | idrico | "Perché acqua e fognatura possono contare come due servizi distinti ai fini del CUP?" | `[[Due distinti servizi di rete nel servizio idrico integrato]]` e il caso CAP Holding |
| Q7 | energia-elettrica | "Se E-Distribuzione riconosce un pagamento ma restano utenze sottodichiarate, come si difende l'accertamento?" | recupero dei due concept energia e del playbook energia |
| Q8 | trasversale | "Dopo SS.UU. 12225/2026 quando va eccepito il difetto di giurisdizione del giudice ordinario?" | richiamo a `[[Natura tributaria del CUP]]` e ai casi gas/idrico davanti al Tribunale |
| Q9 | trasversale | "Dimmi tutto quello che sappiamo su Comune di Portici" | aggregazione di casi gas e idrico e della entity comunale |
| Q10 | trasversale | "Quali materie hanno già un playbook difensivo?" | telefonia, gas, energia elettrica, idrico |

## Redazione memoria test
| ID | Caso | Prompt di test | Atteso minimo |
|---|---|---|---|
| D1 | gas | "Redigi una bozza per un Comune contro Italgas che eccepisce devoluzione gratuita e contesta Punto Fisco" | uso del playbook gas, dei concept su devoluzione e autoriduzione |
| D2 | idrico | "Redigi una bozza contro un gestore SII in house che rifiuta di dichiarare le utenze e nega il doppio servizio acqua/fognatura" | uso del playbook idrico e dei concept su in house, due servizi e stima presuntiva |
| D3 | telefonia | "Redigi una bozza contro WindTre che contesta soggettività passiva, VULA e natura tributaria" | uso del playbook telefonia e dei concept centrali |
| D4 | energia-elettrica | "Redigi una bozza contro E-Distribuzione su contraddittorio, autotutela parziale e POD sottodichiarati" | uso del playbook energia e dei concept energia |

## Note operative
- I test manuali si appoggiano alla wiki reale in `wiki/`.
- Gli smoke test MCP useranno solo tool di lettura e, se possibile, una wiki di esempio o accesso read-only logico.
