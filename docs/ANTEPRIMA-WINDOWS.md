# Anteprima Windows 0.2

Base: distribuzione ufficiale `colobot-gold-0.2.2-alpha-win64`.
Pacchetto: `dist/colobot-0.2.2-alpha-win64-italiano-anteprima-0.2.zip`.

## Compatibilità con la 0.1

Stesso launcher, stessa cartella `colobot-it-preview`, stesso nome interno della
mod (`mod`), stesso percorso dei salvataggi `%LOCALAPPDATA%\ColobotItalianPreview-0.1`.
La configurazione iniziale si copia soltanto se non esiste: nessuna sovrascrittura
di preferenze o salvataggi. Chiudere il gioco ed estrarre lo ZIP nello stesso
percorso usato per la 0.1, sostituendo i file dell’anteprima.

Lo slot resta French, non Italiano, perché il binario ufficiale non include
la nuova enumerazione. Il launcher usa le opzioni ufficiali `-langdir`, `-mod`,
`-datadir` e `-savedir`. Il catalogo italiano è nel percorso isolato
`lang/fr/LC_MESSAGES/colobot.mo`; l’overlay rimappa i testi dati I in F.
La patch per l’integrazione nativa `it` rimane distinta e non viene applicata
al binario Windows esistente.

Nessuna sostituzione di eseguibili, DLL o font. La cartella lang originale non
viene modificata. Per rimuovere: eliminare i file dell’anteprima; i salvataggi
separati possono essere conservati. L’avvio normale resta disponibile.

## Copertura

2.890 voci compilate su 5.172, contro 230 nella 0.1. Di queste, 202 sono
intenzionalmente identiche al sorgente (nomi, identificatori, codice e simili).
Interfaccia 659/659; campagna 878/878; aiuto generale 141/141; robot 176/176;
oggetti ed edifici 323/323. Rimane necessaria la revisione linguistica e visiva.
Non equivale a copertura completa di mod, testo non estraibile dai template o
esempi CBOT. Vedere coverage-0.2.json per i restanti 2.282 messaggi vuoti.

## Verifiche

- GNU gettext, lettura dei MO, confronto dei template e controllo di link,
  pulsanti, tasti, codice e separatori delle descrizioni: riusciti.
- Build completa dei dati ufficiali, parallelismo 2: riuscita.
- Tutte le 878 voci della campagna ritrovate negli output generati italiani.
- Parsing e serializzazione C++ della nuova lingua e lingue esistenti: riusciti.
- Lo ZIP confronta ogni scena con i dati sorgenti, ignorando solo le righe
  Title/Resume/ScriptName tradotte: nessuna modifica alla logica dei livelli.
- Archivio ZIP: controllo CRC e SHA256 dei file, verifica titolo e briefing.
- Launcher identico a quello della 0.1, per conservare comportamento e salvataggi.

La 0.1 è stata provata su Windows dall’utente. Dalle schermate risultano
funzionanti titolo, briefing e accenti; il formato si è sistemato al riavvio.
La 0.2 non è stata eseguita su Windows nell’ambiente di sviluppo. Il motore
completo e CTest restano non compilati/eseguiti qui per le dipendenze native
mancanti. Il confezionamento non richiede di ricompilare il motore.
