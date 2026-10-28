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

## Prova locale Windows

Risultati riportati dall’utente sul proprio PC Windows 64 bit con MSYS2 UCRT64:
GCC 16.2.0, CMake 4.4.4 e Python 3.14.9. Sorgenti preparati sui commit fissati,
cataloghi validati: 5.188 voci tradotte, nessuna vuota o fuzzy.

- Configurazione con `DESKTOP=ON`, `PORTABLE=ON`, `PORTABLE_SAVES=ON` e test abilitati.
- Compilazione del gioco completata (311 target) e dei dati completata (144 target).
- CTest: **205 test superati in 14,75 secondi**. `CBotUT.PublicClasses` e
  `CBotUT.StringAsArray` sono già disabilitati dal progetto e non sono stati eseguiti.
- Installazione di gioco e dati nella cartella di prova riuscita senza errori.
- Avvio grafico riuscito dalla cartella di installazione; caricata la prima missione
  e letta la home del SatCom in italiano. Inizializzazione OpenGL e audio riuscita.
- Corretti due titoli descrittivi rimasti inglesi nella home del SatCom:
  «Type» -> «Tipi» e «Constants» -> «Costanti», preservando i marcatori di stile.
- Persistenza della lingua e prova di salvataggio/ricaricamento ancora da confermare.

Questa verifica è locale sul PC dell’utente, non un’esecuzione GitHub Actions.

## Limiti del collaudo

- La prova Windows conferma avvio e SatCom; il collaudo completo della partita
  resta aperto. I messaggi sui file musicali mancanti sono previsti con `MUSIC=OFF`,
  usato per velocizzare questa build di prova. È stato riportato anche il fallback
  della locale C++: il caricamento dei dati italiani del SatCom è confermato.
- Desktop/manpage non generati nella build Linux; il relativo PO compila
  con gettext. Le risorse audio opzionali non sono state collaudate.
- Le prove automatiche e l’avvio della prima missione non sostituiscono
  una partita completa o una revisione linguistica di ogni schermata.

La traduzione è stata preparata con assistenza AI e revisionata nel gioco da
un utente italofono. I comandi per riprodurre i controlli sono nel [README](../README.md).
