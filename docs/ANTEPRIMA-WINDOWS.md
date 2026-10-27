# Italiano 1.0 RC1 per Windows — note storiche

La RC1 è stata accettata dall’utente e promossa alla [stabile 1.0](RELEASE-1.0.md)
con gli stessi testi e dati. Questa pagina conserva lo stato della candidata.

Base: `colobot-gold-0.2.2-alpha-win64` ufficiale.
Pacchetto: `dist/colobot-0.2.2-alpha-win64-italiano-1.0-rc1.zip`.

Estrarre nella cartella del gioco, sostituire i file della precedente anteprima
e avviare `Avvia-Italiano.cmd`. La cartella dei salvataggi rimane
`%LOCALAPPDATA%\ColobotItalianPreview-0.1`: non eliminarla.
Launcher e configurazione iniziale sono identici alla 0.4; la configurazione
non viene ricopiata se esiste già. Il gioco originale e il suo avvio normale
restano disponibili.

## Revisione dalla 0.4

40 voci corrette in 23 cataloghi. La lettura mirata e il confronto con gli
originali hanno chiarito spiegazioni di variabili, funzioni, movimento e mira,
uniformato didascalie e nomi e tradotto alcune etichette monospaziate.
Il robot rilevatore a zampe non viene più descritto come tiratore. La tabella
di apertura dei file usa correttamente `a` per l’aggiunta, anziché ripetere `w`:
è una correzione della documentazione, non una modifica dei programmi.

Corretti alcuni errori ereditati dai sorgenti:

| Rimando originale | Destinazione italiana corretta |
|---|---|
| `object\Huston` | `object\huston` |
| `cbot\convert` | `object\convert` |
| `cbot\radar()` | `cbot\radar` |
| `\object\radar` | `object\radar` |
| testo `float` collegato a `cbot\bool` | `cbot\float` |

Le eccezioni del validatore sono elencate in `tools/review_rules.py` e sono
limitate a questi rimandi, alle didascalie di prosa e alla specifica tabella
errata. Restano rifiutate modifiche arbitrarie a codice, stringhe e marcatori.
`docs/revision-1.0-rc1.json` elenca tutte le voci modificate.

## Verifiche della candidata

146 cataloghi, 5.172 voci compilate, zero vuote e zero fuzzy. 700 voci sono
identiche al sorgente per mantenere codice, nomi, immagini e crediti.
Gettext, entrambe le forme plurali e lookup dei MO passano i controlli.
Build dati completa riuscita: tutte le 4.455 voci presenti nei file generati.
542 esempi, immagini e identificatori controllati; logica di tutte le 173 scene
e titoli di capitolo del pacchetto confrontata con i sorgenti.

Il nuovo controllo verifica i 3.534 collegamenti dei 452 documenti italiani
distribuiti, incluse le due occorrenze che puntano ad ancore nominate. Simula
la risoluzione dei percorsi del gioco, incluse `%lvl%` e `%lng%`, richiede
pagine italiane e viene ripetuto sullo ZIP finale. Non verifica visivamente
l’area cliccabile, la cronologia del SatCom o la disposizione del testo.
Il pacchetto verifica anche CRC e SHA256 dei file.

La 0.4 è stata dichiarata funzionante dall’utente. La RC1 è nuova e richiede
il [collaudo finale](COLLAUDO-1.0-RC1.md). Nessun avvio Windows o CTest del
motore è stato eseguito qui; la build completa del motore resta bloccata
dalle dipendenze OpenGL mancanti.

## Limiti

Per compatibilità con il binario ufficiale, il catalogo è in
`lang/fr/LC_MESSAGES/colobot.mo` e i dati italiani `I` sono rimappati in `F`.
Scegliere **French** nelle impostazioni. Nessuna sostituzione di eseguibile,
DLL o font. Lo ZIP non contiene una nuova versione compilata del gioco.

La pagina originale del robot disegnatore contiene solo `TODO`: ora viene
segnalata chiaramente l’assenza della documentazione. Le stringhe dei programmi
restano in inglese per preservare gli esempi; i commenti sono tradotti.
Metadati non gettext di AltTextures e mod esterne non sono inclusi.
La copertura dei cataloghi non equivale a un collaudo di ogni schermata.
