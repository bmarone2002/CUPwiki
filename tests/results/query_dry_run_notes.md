# Dry run di query reali

## Obiettivo
Simulare un primo utilizzo reale della wiki con 4 domande rappresentative, una per materia, per verificare se i playbook consentono già risposte sintetiche, citate e orientate alla redazione.

## Query 1 — Telefonia
**Domanda:** quale linea difensiva usiamo quando l'operatore TLC nega la soggettività passiva e sostiene che l'accesso è solo virtuale?

**Risposta sintetica attesa:**
La risposta forte combina `[[Soggettività passiva in via mediata]]` e `[[Utilizzo materiale e accesso virtuale (VULA)]]`: il CUP può colpire anche l'operatore che utilizza materialmente l'infrastruttura altrui per erogare il servizio, e la distinzione tra accesso “virtuale” e accesso tecnicamente appoggiato a reti fisiche non elimina il presupposto. I precedenti principali sono `[[2026-04-28 Cass 11479 — VULA Wind]]`, `[[2025-11-25 Trib Bergamo 1523 — Fastweb]]`, `[[2025-10-15 Trib Bolzano 908 — WindTre WLR]]` e `[[2025-09-29 Trib Ivrea 1255 — WindTre soggettività mediata]]`.

**Esito:** PASS.

## Query 2 — Gas
**Domanda:** come contrastiamo Italgas quando si auto-riduce il canone invocando la devoluzione gratuita e poi contesta Punto Fisco?

**Risposta sintetica attesa:**
La wiki porta correttamente su `[[Autoriduzione unilaterale del CUP gas da parte del gestore]]` e `[[Devoluzione gratuita parziale degli impianti gas non basta]]`. La linea difensiva è che il gestore non può auto-applicarsi una riduzione percentuale del canone né tradurre quote di rete in quote di utenze senza trasparenza del calcolo; inoltre l'esenzione del comma 833 lett. d) è tassativa e non opera per devoluzione parziale, onerosa o riferita a beni già pubblici. I casi forti sono `[[2026-07-27 Memoria Sessa Aurunca c. Italgas Reti (Trib. Santa Maria Capua Vetere)]]`, `[[2026-06-18 Memoria Casagiove c. Italgas Reti (Trib. Santa Maria Capua Vetere)]]`, `[[2025-10-30 Memoria GE.SE.T. Portici c. Italgas Reti (Trib. Napoli)]]` e `[[2026-07-27 Memoria Palagiano c. Italgas Reti (Trib. Taranto)]]`.

**Esito:** PASS.

## Query 3 — Idrico
**Domanda:** perché un gestore del SII in house non è esente dal CUP e perché acqua e fognatura possono contare separatamente?

**Risposta sintetica attesa:**
La wiki consente una risposta molto forte: `[[Gestore del servizio idrico integrato non esente dal CUP]]` chiarisce che l'in house non cancella l'alterità soggettiva del gestore e che la restituzione di reti già pubbliche non equivale a devoluzione gratuita; `[[Due distinti servizi di rete nel servizio idrico integrato]]` chiarisce poi che gestione unitaria del SII e occupazioni del suolo sono piani distinti. Le fonti principali sono `[[2026-07-03 Memoria Palestro c. Pavia Acque (Trib. Pavia)]]`, `[[2026-07-08 Memoria Cinisello Balsamo c. CAP Holding (CGT Milano)]]`, `[[2024-11-22 Trib Rovigo 889-2023 — Acquevenete esenzione devoluzione]]` e `[[Cassazione 2180 2020 — acqua e fognatura nel SII]]`.

**Esito:** PASS.

## Query 4 — Energia elettrica
**Domanda:** se E-Distribuzione dimostra un pagamento parziale ma restano POD sottodichiarati, come si difende l'accertamento?

**Risposta sintetica attesa:**
La wiki porta bene sui due concept `[[Rettifica dell'autodichiarazione utenze nel CUP energia]]` e `[[Stima prudenziale delle utenze POD su dati ARERA]]`: il Comune può riconoscere in autotutela il versamento non visto sui sistemi senza rinunciare al residuo dovuto, se permane una sottodichiarazione del numero di utenze/POD; inoltre un coefficiente prudenziale fondato su ARERA rafforza, non indebolisce, la tenuta dell'accertamento. La base resta `[[2026-07-27 Memoria Bitritto c. E-Distribuzione (CGT Bari)]]`.

**Esito:** PASS con gap.

## Gap emersi dal dry run
- `energia-elettrica` è già usabile, ma resta ancora troppo dipendente da un solo caso.
- Il motore di recupero, se usato in modo molto grezzo, tende a far emergere anche `log` e `index`; non è un problema della knowledge base, ma potrà valere un affinamento futuro del layer MCP/search.
- `idrico` meriterebbe in futuro un sotto-playbook dedicato solo al blocco `acqua/fognatura`.

## Valutazione complessiva
Il dry run conferma che la wiki è già passata da archivio a strumento operativo: gas, telefonia e idrico reggono bene; energia elettrica regge ma ha ancora bisogno di densificazione documentale.
