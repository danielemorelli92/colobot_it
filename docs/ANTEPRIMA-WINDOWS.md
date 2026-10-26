# Anteprima Windows 0.3 — cataloghi completi

Base: `colobot-gold-0.2.2-alpha-win64` ufficiale. Download in `dist/`.
Estrarre nello stesso percorso della 0.1/0.2 e sostituire i file dell’anteprima.
La cartella dei salvataggi resta `%LOCALAPPDATA%\ColobotItalianPreview-0.1`:
non eliminarla. Launcher e configurazione iniziale non cambiano.

Tutti i 146 cataloghi sono completi: 5.172 voci, zero vuote e zero fuzzy.
Delle voci compilate, 777 sono identiche al sorgente per mantenere codice,
identificatori, nomi, immagini e crediti. Due messaggi hanno entrambe le forme
plurali italiane. Vedere `coverage-0.3.json` e `verification.json`.

Il pacchetto resta compatibile con il binario ufficiale grazie allo slot French.
Il launcher usa `-langdir`, `-mod`, `-datadir` e `-savedir`; catalogo isolato in
`lang/fr/LC_MESSAGES/colobot.mo`, dati I rimappati in F nell’overlay.
Non modifica font, DLL, eseguibile, cartella lang originale o logica dei livelli.
L’avvio normale resta disponibile e separato. La configurazione iniziale è
copiata soltanto se non esiste, senza sovrascrivere preferenze o salvataggi.

## Verifiche della 0.3

Gettext, formati, entrambe le forme plurali, lookup dei MO, marcatori e
collegamenti: riusciti. Build dati completa: riuscita. Tutte le 4.455 voci dei
cataloghi dati sono presenti negli output italiani generati. Il pacchetto
confronta tutte le scene con i sorgenti, escludendo solo le righe di testo
localizzate; verifica anche CRC e SHA256 dei contenuti.

Il test di preservazione controlla 542 esempi di codice, nomi di programmi e
riferimenti a immagini. Tre intestazioni dei rapporti e una tabella di esempio
numerico sono prosa monospaziata, anche se l’estrattore le chiama Source code:
vengono tradotte preservando marcatori e numeri.

Le anteprime 0.1/0.2 sono state avviate su Windows dall’utente. Su sua richiesta,
le prove estese nel gioco vengono fatte dopo la traduzione completa. La 0.3
rimane da collaudare interattivamente; nessuna dichiarazione di test Windows,
CTest o compilazione completa del motore non eseguiti.

## Ambito

Completati i cataloghi della release fissata. La descrizione non gettext
dell’addon AltTextures resta inglese, i nomi delle lingue sono nel binario
ufficiale e codice/commenti/esempi non vengono riscritti. Le mod esterne sono
fuori ambito. La traduzione completa richiede ancora revisione linguistica e
verifica visiva: completamento dei cataloghi e qualità collaudata sono distinti.
