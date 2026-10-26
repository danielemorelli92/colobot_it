# Colobot: Gold Edition — italiano

**Anteprima 0.4 con cataloghi completi per Colobot Gold 0.2.2-alpha Windows 64 bit.**

[Scarica lo ZIP](dist/colobot-0.2.2-alpha-win64-italiano-anteprima-0.4.zip)
Apri il file su GitHub e premi **Download raw file**.

## Installare o aggiornare

1. Chiudi il gioco.
2. Estrai tutto lo ZIP nella cartella che contiene `colobot.exe` e `data`.
3. Se hai la 0.1 o 0.2, accetta la sostituzione dei file dell’anteprima.
4. Avvia sempre `Avvia-Italiano.cmd`.

Non sostituire la cartella `lang` originale. La 0.4 riutilizza
`%LOCALAPPDATA%\ColobotItalianPreview-0.1`: **conserva salvataggi e impostazioni
precedenti**. Il launcher è identico a quello della 0.1 e 0.2.

Per compatibilità con l’eseguibile ufficiale, l’anteprima continua a usare lo
slot **French**: è normale leggerlo nelle impostazioni. La vera integrazione
`it`/`it_IT.utf8` è disponibile nella patch sorgente, ma non serve per lo ZIP.
Non vengono distribuiti o sostituiti eseguibili, DLL o font.

## Copertura completata

**146 cataloghi, 5.172 voci compilate, zero vuote e zero fuzzy.**
Sono tradotti interfaccia, campagna, esercizi, sfide, battaglie, gioco libero,
missioni aggiuntive, aiuto generale, robot, edifici, oggetti, riferimento CBOT,
descrizioni dei programmi e catalogo desktop/manuale.

Sono inclusi entrambi i plurali italiani delle due voci che li richiedono:
il numero di voci non coincide quindi con il numero di forme tradotte.
702 voci sono intenzionalmente identiche al sorgente: codice, identificatori,
nomi, riferimenti alle immagini, crediti e simili. I nomi tecnici dei programmi
restano coerenti con gli esempi. Il codice eseguibile resta invariato; i commenti degli esempi sono tradotti.

[Copertura per catalogo](docs/coverage-0.4.json).
Il 100% riguarda i cataloghi della release, non promette l’assenza di qualsiasi
parola inglese: oltre al codice, restano i nomi delle lingue nel binario e i
metadati non gettext dell’addon AltTextures. Le mod esterne non sono incluse.
Il catalogo desktop è tradotto nei sorgenti; lo ZIP Windows non sostituisce
l’installatore né genera una pagina man Unix.

## Stato del collaudo

Questa è la prima stesura completa, **da collaudare nel gioco e revisionare
linguisticamente**, non una release ufficiale approvata dagli sviluppatori.
L’utente ha confermato l’avvio della 0.1 e 0.2 su Windows. Su sua richiesta,
il collaudo interattivo esteso viene rinviato a questa versione completa.
La 0.4 non è ancora stata avviata su Windows nell’ambiente di sviluppo.

Controlli automatici eseguiti:

- GNU gettext: tutti i PO compilano con `--check --check-format`.
- Plurali: validazione delle due forme e lookup MO per 0, 1, 2 e 10.
- Marcatori, collegamenti, tasti, pulsanti e blocchi di codice verificati.
- Build completa dei dati ufficiali riuscita; tutte le 4.455 voci dei dati
  ritrovate nei file italiani generati.
- 542 esempi di codice, riferimenti a immagini e nomi di programmi preservati;
  le intestazioni testuali dei rapporti monospaziati vengono tradotte.
- Confronto della logica di tutte le scene e dei titoli di capitolo nel pacchetto:
  cambiano solo le righe localizzate, non gli oggetti o le condizioni di vittoria.
- Archivio ZIP verificato con CRC e SHA256 dei contenuti.

La compilazione completa del motore si ferma alle dipendenze OpenGL mancanti;
CTest del gioco e prove interattive non sono stati eseguiti qui. Lo ZIP riusa
l’eseguibile già installato dall’utente.

## Sorgenti e ricostruzione

Servono Python >=3.12, Git, GNU gettext, CMake >=3.16 e compilatore C++17.
Usa il checkout esistente: il cloud è già isolato e non serve creare worktree.
I pin sono in `tools/prepare.py`: release ufficiali, nessun uso implicito di dev.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
git clone https://github.com/colobot/colobot.git ../colobot
git clone https://github.com/colobot/colobot-data.git ../colobot-data
.venv/bin/python tools/prepare.py --engine ../colobot --data ../colobot-data --output build/prepared
.venv/bin/python tools/validate.py --require-complete --engine build/prepared/colobot --data build/prepared/colobot-data
.venv/bin/python tools/test_localization_checks.py
.venv/bin/python tools/test_code_preservation.py
g++ -std=c++17 -I build/prepared/colobot/src build/prepared/colobot/src/common/language.cpp tools/test_language.cpp -o build/test_language
build/test_language
cmake -S build/prepared/colobot-data -B build/data -DTRANSLATIONS=ON
cmake --build build/data -j2
COLOBOT_DATA_SOURCE=build/prepared/colobot-data .venv/bin/python tools/test_generated.py build/data
.venv/bin/python tools/test_complete_data.py --build build/data --source build/prepared/colobot-data
COLOBOT_DATA_SOURCE=build/prepared/colobot-data .venv/bin/python tools/package_windows_preview.py --data-build build/data --data-source build/prepared/colobot-data --output dist/colobot-0.2.2-alpha-win64-italiano-anteprima-0.4.zip
```

Il preparatore usa archivi dei commit ufficiali, preserva i checkout originali
e rifiuta di sovrascrivere la destinazione. La generazione usa gli script ufficiali.

Per una versione nativa, installare le dipendenze indicate nell’[analisi](docs/ANALISI.md),
applicare la patch, rendere disponibile la locale `it_IT.UTF-8`, compilare il
motore ed eseguire CTest e le prove di selezione/rendering. Nessuna modifica
è stata inviata ai repository ufficiali.

[Glossario](docs/GLOSSARIO.md) · [Note Windows](docs/ANTEPRIMA-WINDOWS.md)

Licenza GPL v3 o successiva, come i progetti upstream. Per nuove release,
aggiornare i pin dopo il confronto dei sorgenti, rigenerare la patch e usare
`msgmerge`, revisionando le voci fuzzy prima di distribuire un nuovo pacchetto.
