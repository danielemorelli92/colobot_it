# Colobot: Gold Edition — italiano

**Anteprima 0.2 per la versione ufficiale 0.2.2-alpha Windows 64 bit.**

[Scarica lo ZIP](dist/colobot-0.2.2-alpha-win64-italiano-anteprima-0.2.zip)
Apri il file su GitHub e premi **Download raw file**.

## Installare o aggiornare

1. Chiudi il gioco.
2. Estrai tutto lo ZIP nella cartella che contiene `colobot.exe` e `data`.
3. Se hai già la 0.1, accetta la sostituzione dei file dell’anteprima.
4. Avvia `Avvia-Italiano.cmd` come prima.

Non sostituire i file della cartella `lang` originale. La 0.2 conserva la cartella
separata `%LOCALAPPDATA%\ColobotItalianPreview-0.1`: **salvataggi e impostazioni
dell’anteprima precedente restano disponibili**. L’avvio normale resta separato.

L’anteprima usa temporaneamente lo slot **French** del gioco ufficiale: è normale
leggere questo nome nelle impostazioni. La vera integrazione della lingua `it`
è nella patch sorgente, ma non è necessaria per provare questo ZIP.

## Cosa è tradotto

- Interfaccia: 659/659 voci, compresi comandi, impostazioni e messaggi d’errore.
- Campagna principale: 878/878 voci nei 37 cataloghi, dalla Terra a Terranova;
  briefing, rapporti satellitari e soluzioni disponibili nei sorgenti.
- Aiuto generale SatCom: 141/141 voci.
- Schede dei robot: 176/176; oggetti, edifici e creature: 323/323.
- Testi identici riutilizzati nei cataloghi degli altri livelli e dell’aiuto.

Copertura complessiva: **2.890/5.172 voci compilate (55,9%)**, contro 230 nella
0.1. Il numero comprende ripetizioni, nomi propri, riferimenti a immagini e
identificatori/codice lasciati invariati: non significa che il 55,9% delle parole
sia stato tradotto. [Conteggio dettagliato](docs/coverage-0.2.json).

Restano parziali esercizi di programmazione, sfide, battaglie, missioni aggiuntive,
riferimento dettagliato CBOT e manuale desktop. Gli identificatori e i programmi
CBOT non vengono tradotti. Le voci mancanti conservano il testo inglese.
La traduzione richiede ancora una revisione linguistica e prove visive estese.

## Verifiche

La 0.1 è stata provata dall’utente su Windows: avvio, prima missione e SatCom
italiano confermati; il formato dei testi si è sistemato dopo il riavvio.

Per la 0.2 sono stati eseguiti gettext, controlli su marcatori/segnaposto,
compilazione completa dei dati e riscontro di tutte le 878 voci della campagna
negli output italiani generati. Non è stata ancora provata su Windows.
Nessuna modifica ai font, all’eseguibile o alla logica delle missioni.

## Sorgenti e riproduzione

Python >=3.12, Git, GNU gettext, CMake >=3.16 e compilatore C++17.
Usare il checkout esistente: il cloud è già isolato e non serve creare worktree.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
git clone https://github.com/colobot/colobot.git ../colobot
git clone https://github.com/colobot/colobot-data.git ../colobot-data
.venv/bin/python tools/prepare.py --engine ../colobot --data ../colobot-data --output build/prepared
.venv/bin/python tools/validate.py --engine build/prepared/colobot --data build/prepared/colobot-data
.venv/bin/python tools/test_localization_checks.py
g++ -std=c++17 -I build/prepared/colobot/src build/prepared/colobot/src/common/language.cpp tools/test_language.cpp -o build/test_language
build/test_language
cmake -S build/prepared/colobot-data -B build/data -DTRANSLATIONS=ON
cmake --build build/data -j2
COLOBOT_DATA_SOURCE=build/prepared/colobot-data .venv/bin/python tools/test_generated.py build/data
COLOBOT_DATA_SOURCE=build/prepared/colobot-data .venv/bin/python tools/package_windows_preview.py --data-build build/data --data-source build/prepared/colobot-data --output dist/colobot-0.2.2-alpha-win64-italiano-anteprima-0.2.zip
```

Il preparatore usa archivi Git di commit ufficiali fissati, lascia inalterati i
checkout originali e rifiuta di sovrascrivere l’output esistente. I pin sono in
`tools/prepare.py`. Gli script generano i dati con la pipeline ufficiale.

La compilazione completa del motore richiede inoltre le dipendenze grafiche e
native indicate nell’[analisi iniziale](docs/ANALISI.md). In questo ambiente
si è fermata a OpenGL mancante; il pacchetto Windows usa il binario già installato.
Per una futura versione nativa, applicare la patch italiana, installare la locale
`it_IT.UTF-8`, compilare il motore, eseguire CTest e verificare selezione e rendering.
Non sono state inviate modifiche ai repository ufficiali.

## Continuare il lavoro

[Glossario](docs/GLOSSARIO.md), [analisi iniziale](docs/ANALISI.md) e
[note dell’anteprima](docs/ANTEPRIMA-WINDOWS.md).
Le traduzioni seguono la licenza GPL v3 o successiva dei progetti upstream.
Per nuove release aggiornare i pin dopo il confronto, rigenerare la patch,
usare `msgmerge` e revisionare le voci fuzzy prima di creare nuovi pacchetti.
