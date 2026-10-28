# Proposta per integrare ufficialmente l’italiano

Stato al 28 ottobre 2026: analisi del precedente e bozza della nuova issue.
La versione comunitaria 1.0 rimane invariata. Non sono state aperte issue o
pull request nei repository ufficiali con questo lavoro.

[Bozza in inglese: Italian translation and native language support](upstream/ISSUE-ITALIAN.md).
Il titolo è la prima riga del file; il resto è il testo da usare nella nuova
issue italiana. La bozza distingue il pacchetto della release dall’integrazione
nativa ancora da preparare e descrive esplicitamente l’assistenza AI nella
traduzione e i limiti della revisione umana riportata.

## Il precedente indicato dall’utente

[Issue #1124 — Translate to Brazilian Portuguese](https://github.com/colobot/colobot/issues/1124),
letta insieme ai commenti. La discussione è ancora aperta, ma le due proposte
collegate sono state integrate: lo stato dell’issue non coincide con quello
delle pull request.

| Fonte | Indicazione da applicare |
|---|---|
| [Commento di muzscaly](https://github.com/colobot/colobot/issues/1124#issuecomment-370910491) | I testi oltre all’interfaccia si trovano nel repository `colobot-data`. |
| [Commento di Erihel](https://github.com/colobot/colobot/issues/1124#issuecomment-370915777) | Usare come esempi la [PR motore ceca #1118](https://github.com/colobot/colobot/pull/1118) e la [PR dati #34](https://github.com/colobot/colobot-data/pull/34). |
| [Problema del catalogo portoghese](https://github.com/colobot/colobot/issues/1124#issuecomment-373001677) | Verificare locale effettiva e cartella del catalogo dopo l’installazione; la compilazione riuscita da sola non dimostra che venga caricata la traduzione. |
| [Due PR brasiliane](https://github.com/colobot/colobot/issues/1124#issuecomment-389192118) | Preparare due contributi coordinati: [motore #1167](https://github.com/colobot/colobot/pull/1167) e [dati #36](https://github.com/colobot/colobot-data/pull/36), entrambi integrati in `dev` l’8 settembre 2018. |
| [Collisione fra codici](https://github.com/colobot/colobot/issues/1124#issuecomment-392357201) | Allineare i codici del motore e del generatore dati: `pt` e `pl` producevano entrambi `P`; per il portoghese fu adottato `B`. |

Il precedente continua a essere indicato dal progetto: nella
[proposta spagnola #1883](https://github.com/colobot/colobot/issues/1883), Erihel
ha rimandato a #1124 e alle due PR brasiliane il 10 febbraio 2026.
Le [linee guida attuali](https://github.com/colobot/colobot/blob/dev/CONTRIBUTING.md#submitting-pull-requests)
richiedono PR verso `dev` e una discussione preventiva per nuove funzionalità.
La proposta italiana va in una nuova issue; i riferimenti storici servono come
precedenti, senza riutilizzare la discussione dedicata al portoghese.

## Confronto verificato con dev

Commit esaminati:

- `colobot`: `5c0fb16bb8caeba0e6bc27c700bc9119e1bcd03f`.
- `colobot-data`: `3efb490881a1e297666ac92d5530ee94114d08c2`.

Tutti i 146 cataloghi trovano il corrispondente POT e non risultano POT
aggiuntivi. Confrontando esattamente contesto, `msgid` e `msgid_plural`:

| Risultato | Voci |
|---|---:|
| Già presenti nella 1.0 e riutilizzabili | 5.172 |
| Nuove o modificate in dev | 1 |
| Rimosse da dev | 0 |
| Totale nei template dev | 5.173 |

L’unica voce nuova è nell’interfaccia:

> This save file is from a different version of the game and might not work correctly.
> Do you want to open it anyway?

[Rapporto per catalogo](upstream/catalog-comparison-2026-10-28.json).
Questo confronto non ha modificato né migrato i PO e non prova che il motore
nativo funzioni. Va aggiornato se i rami `dev` avanzano prima della proposta.

## Piano tecnico delle due PR

Nel motore attuale i file sono sotto `colobot-base/src/`, mentre la patch
0.2.2-alpha usa il vecchio percorso `src/`. Inoltre il valore 7 nell’enumerazione
delle lingue è già occupato da `LANGUAGE_MAGYAR`: l’italiano dovrà usare un
nuovo valore senza rinumerare le lingue esistenti. Non applicare alla cieca
la patch della 1.0 a `dev`.

Per la PR motore occorre adattare registrazione, conversione dei codici,
locale, selettore della lingua e cataloghi `po/it.po` e `desktop/po/it.po`.
Verificare generazione e installazione di `it/LC_MESSAGES/colobot.mo` e aggiungere
il nuovo messaggio sui salvataggi. L’obiettivo è selezionare **Italiano**
nell’eseguibile normale.

Per la PR dati occorre trasferire i PO nelle directory ufficiali. Il generatore
attuale mappa `it` in `I` attraverso la prima lettera maiuscola; deve coincidere
con il codice restituito dal motore. La regola speciale per `pt` -> `B` va
preservata. Non includere lo ZIP, l’overlay `F` o il launcher comunitario nelle
PR ufficiali. Valutare separatamente le correzioni di refusi e rimandi ereditati
registrate in `tools/review_rules.py`.

Prima di presentare le PR come pronte da integrare occorrono la build nativa,
i controlli del progetto e la prova della lingua italiana dopo l’installazione,
compreso il comportamento su Windows. Le prove della 1.0 tramite lo slot French
non sostituiscono questo collaudo.

## Materiale da rendere accessibile per la revisione

La visita anonima al repository `danielemorelli92/colobot_it` ha restituito
HTTP 404. Questo non prova da solo il motivo, ma non permette di assumere che
i manutentori possano leggere i link ai nostri file. La bozza non dipende da
quel collegamento: le future PR dovranno fornire i sorgenti in fork accessibili
o mediante il formato concordato con i manutentori. Non è stata cambiata
la visibilità del repository.

Prima dell’invio: ricontrollare eventuali proposte italiane già aperte, aggiornare
il confronto con `dev`, verificare titolo e testo della bozza e predisporre gli
allegati o i fork necessari. Pubblicare la proposta nei repository ufficiali
è un passaggio distinto dalla preparazione di questi documenti.
