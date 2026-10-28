# Verifiche dell’integrazione nativa

Eseguite il 28 ottobre 2026 sui commit `dev` fissati in
[upstream.json](../upstream.json), con la patch e i cataloghi di questo repository.
Ambiente: Debian 13, GCC 14.2, C++20, CMake 4.4.4, GNU gettext 0.23.1.

| Controllo | Risultato |
|---|---|
| Cataloghi gettext | 146 cataloghi, 5.188 voci compilate, nessuna vuota o fuzzy; plurali e lookup MO verificati. |
| Dati ufficiali rigenerati | Tutte le 4.470 voci dei dati ritrovate nei file italiani generati. |
| Codice e riferimenti | 546 esempi, nomi di programmi e riferimenti a immagini controllati; codice e stringhe eseguibili preservati. |
| SatCom | 3.550 collegamenti in 453 documenti italiani risolti, comprese due occorrenze con ancore. |
| Motore Linux | Configurazione, compilazione Release e installazione riuscite con `TESTS=ON`, `DESKTOP=OFF`, `PORTABLE=ON`. |
| CTest | 205 test eseguiti e superati, compresi i due nuovi test delle lingue; due test CBOT già disabilitati upstream non eseguiti. |
| Locale e catalogo installato | Avvio con locale di sistema italiana e avvio da locale inglese con `Language.Lang=it`: entrambi caricano il MO italiano e completano la prima missione con `-scenetest`, codice di uscita 0. |
| Interfaccia nativa | Controllati visivamente il selettore Italiano, il SatCom e le opzioni in una sessione Xvfb con rendering software, a 1280×800. |
| Patch per i due repository | Applicazione verificata sui rispettivi commit originali; checkout di origine preservati. |

I test nativi usano i cataloghi installati sotto `lang/it/LC_MESSAGES` e i dati
italiani `I`, senza mod o rimappatura nello slot French. La prova visiva ha
permesso anche di accorciare «Distanza visiva», evitando una sovrapposizione
nella schermata delle opzioni grafiche.

La rigenerazione ha rilevato che i POT `help/cbot` e `help/generic` del commit
ufficiale non contenevano tutti i testi inglesi attuali. I due template sono
inclusi aggiornati, insieme alle traduzioni di `searchall` e delle etichette
dei cicli. Il confronto iniziale con i soli POT committati non rilevava queste
voci: i conteggi sopra riguardano i dati rigenerati.

## Limiti del collaudo

- La nuova integrazione `dev` non è stata compilata o avviata su Windows.
  L’utente ha provato il pacchetto comunitario 1.0 con il binario 0.2.2-alpha.
- Desktop/manpage non generati nella build nativa; il relativo PO compila
  con gettext. Le risorse audio opzionali non sono state collaudate.
- Le prove automatiche e l’avvio della prima missione non sostituiscono
  una partita completa o una revisione linguistica di ogni schermata.

La traduzione è stata preparata con assistenza AI e revisionata nel gioco da
un utente italofono. I comandi per riprodurre i controlli sono nel [README](../README.md).
