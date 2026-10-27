# Traduzione italiana 1.0

Versione stabile per la distribuzione ufficiale
`colobot-gold-0.2.2-alpha-win64`. Pubblicata il 27 ottobre 2026 nel repository
[danielemorelli92/colobot_it](https://github.com/danielemorelli92/colobot_it).

[Scarica il pacchetto 1.0](../dist/colobot-0.2.2-alpha-win64-italiano-1.0.zip).
Su GitHub apri il file e premi **Download raw file**. Accanto allo ZIP è
presente il file `.sha256` per verificarne l’integrità.

## Dalla RC1 alla stabile

La 1.0 contiene gli stessi testi, dati di gioco, launcher e configurazione
della candidata RC1 accettata dall’utente. Sono aggiornati l’etichetta di
versione della mod, la documentazione e i metadati del pacchetto.
Non ci sono nuove traduzioni o modifiche alla logica di gioco.

I contenuti utilizzati dal gioco, escluso il manifesto con la versione,
sono confrontati byte per byte con lo ZIP della RC1. Sono verificati anche
i cataloghi sorgente inclusi. Il confezionamento ricontrolla i dati generati,
la preservazione del codice, i collegamenti e l’integrità dell’archivio.

L’accettazione dell’utente è generale: non è stato fornito un esito distinto
per ogni prova della checklist. Nessun collaudo interattivo Windows è stato
eseguito nell’ambiente di sviluppo. Il progetto resta aperto a segnalazioni
linguistiche o visive durante il gioco.

## Installare, aggiornare e rimuovere

1. Chiudi Colobot.
2. Estrai tutto lo ZIP nella cartella con `colobot.exe` e `data`.
3. Accetta la sostituzione dei file della traduzione precedente, se presente.
4. Avvia `Avvia-Italiano.cmd` e mantieni **French** nelle impostazioni.

I salvataggi e le impostazioni delle anteprime e della RC1 restano in
`%LOCALAPPDATA%\ColobotItalianPreview-0.1`. Il launcher è identico e copia la
configurazione iniziale solo se non esiste già. Non eliminare questa cartella.
Se hai già la RC1 puoi continuare a giocare con quella: l’aggiornamento alla
1.0 serve a conservare il pacchetto definitivo.

Per rimuovere la traduzione elimina `Avvia-Italiano.cmd`, `LEGGIMI-ITALIANO.txt`
e `colobot-it-preview`; puoi conservare la cartella dei salvataggi.
L’avvio normale con `colobot.exe` e i suoi salvataggi restano separati.

## Contenuti e compatibilità

146 cataloghi con 5.172 voci compilate; nessuna vuota o fuzzy. Incluse entrambe
le forme dei plurali italiani. Tradotti interfaccia, missioni, esercizi,
sfide, battaglie, gioco libero, livelli aggiuntivi, SatCom e commenti degli
esempi. Le 40 correzioni introdotte nella RC1 sono elencate nel
[registro della revisione](revision-1.0-rc1.json).

Il pacchetto usa lo slot French perché il binario ufficiale non comprende
ancora la lingua italiana. Non sostituisce eseguibili, DLL, font o i cataloghi
originali. La patch per integrare nativamente l’italiano è inclusa nei sorgenti,
ma non è un nuovo eseguibile compilato.

Codice, identificatori, nomi tecnici e stringhe dei programmi restano invariati.
La pagina originale del robot disegnatore contiene solo `TODO`: la traduzione
segnala l’assenza di documentazione. I metadati non gettext di AltTextures e
le mod esterne non sono compresi. Il catalogo desktop/manuale è nei sorgenti;
lo ZIP Windows non sostituisce l’installatore o una pagina man Unix.

Questa è una traduzione della comunità, distribuita sotto GPL v3 o successiva;
non è una release ufficiale approvata dagli sviluppatori di Colobot.

## Manutenzione

Per segnalare un problema, indica versione del pacchetto, modalità, capitolo,
missione o esercizio, pagina e frase esatta. Per difetti visivi allega screenshot
e risoluzione; per errori di avvio conserva il messaggio visualizzato.

Le eventuali correzioni successive potranno essere distribuite come 1.0.1.
Il supporto a una nuova versione del gioco richiederà un confronto dei sorgenti
e un nuovo collaudo: questa 1.0 è destinata alla 0.2.2-alpha.
