# Colobot: Gold Edition — italiano

**Candidata 1.0 RC1 per Colobot Gold 0.2.2-alpha Windows 64 bit.**

[Scarica lo ZIP](dist/colobot-0.2.2-alpha-win64-italiano-1.0-rc1.zip).
Apri il file su GitHub e premi **Download raw file**.

## Installare o aggiornare

1. Chiudi il gioco.
2. Estrai tutto lo ZIP nella cartella che contiene `colobot.exe` e `data`.
3. Se hai una precedente anteprima, accetta la sostituzione dei suoi file.
4. Avvia `Avvia-Italiano.cmd`.

La RC1 riutilizza `%LOCALAPPDATA%\ColobotItalianPreview-0.1`:
**conserva i salvataggi e le impostazioni delle anteprime**. Il launcher è
identico a quello della 0.4 e copia la configurazione soltanto al primo avvio.

Per compatibilità con l’eseguibile ufficiale, scegli **French** nelle impostazioni.
Il pacchetto carica il catalogo italiano e i dati tramite le opzioni ufficiali
`-langdir` e `-mod`. Non sostituisce eseguibili, DLL, font o la cartella `lang`
originale. I salvataggi dell’avvio normale di Colobot restano separati.
La patch sorgente per integrare nativamente `it`/`it_IT.utf8` è inclusa, ma
non viene compilata nello ZIP.

## Cosa cambia nella RC1

Revisionate **40 voci in 23 cataloghi** rispetto alla 0.4:

- Uniformati alcuni nomi e didascalie del SatCom, inclusa «Stazione radar».
- Chiarite le spiegazioni su variabili, funzioni, movimento, mira e altitudine.
- Corretti rimandi originali a Houston, convertitore, radar e tipo float.
- Corrette la descrizione del robot rilevatore a zampe e la modalità di
  aggiunta ai file nella documentazione, errate anche nel testo originale.
- Tradotte didascalie monospaziate che non sono istruzioni CBOT.

Il nuovo controllo percorre **3.534 collegamenti in 452 documenti**, comprese
le due occorrenze con ancore nominate, e richiede destinazioni italiane esistenti.
Viene eseguito anche leggendo lo ZIP finale.

[Note della RC1](docs/ANTEPRIMA-WINDOWS.md) ·
[Prove finali su Windows](docs/COLLAUDO-1.0-RC1.md) ·
[Registro delle correzioni](docs/revision-1.0-rc1.json).

## Copertura e limiti

**146 cataloghi, 5.172 voci compilate, zero vuote e zero fuzzy.**
Coperti interfaccia, campagna, esercizi, sfide, battaglie, gioco libero,
missioni aggiuntive, SatCom, robot, oggetti, edifici, riferimento CBOT,
programmi e catalogo desktop/manuale. Le due voci con plurali contengono
entrambe le forme italiane. [Copertura per catalogo](docs/coverage-1.0-rc1.json).

700 voci restano identiche al sorgente: codice, identificatori, immagini,
nomi propri e crediti. I commenti degli esempi sono tradotti; istruzioni,
nomi dei programmi e stringhe del codice sono preservati.
Il sorgente contiene solo `TODO` per il robot disegnatore: la pagina italiana
avvisa che la documentazione non è disponibile in questa versione del gioco.
I metadati non gettext dell’addon AltTextures e le mod esterne non sono inclusi.
Il catalogo desktop è nei sorgenti; lo ZIP Windows non modifica l’installatore
né genera una pagina man Unix.

La revisione ha combinato controlli sull’intero catalogo e lettura mirata delle
spiegazioni e della terminologia. La RC1 resta **da collaudare nel gioco**,
in particolare per impaginazione e salvataggi; non è ancora la stabile 1.0
né una release ufficiale approvata dagli sviluppatori di Colobot.

## Verifiche

- Tutti i PO compilano con GNU gettext `--check --check-format`.
- Lookup MO e plurali verificati per 0, 1, 2 e 10.
- Marcatori, tasti, pulsanti, link, ancore e rientri controllati.
- Build completa dei dati con gli script ufficiali: tutte le 4.455 voci dei
  dati ritrovate negli output italiani; incluse le 878 voci della campagna.
- 542 esempi di codice, riferimenti a immagini e nomi di programmi verificati.
- Logica delle 173 scene e titoli di capitolo nel pacchetto confrontata con
  l’originale, escludendo soltanto le righe di testo localizzate.
- ZIP verificato con CRC, SHA256 dei file e risoluzione dei link SatCom.
- Test C++ della mappatura delle lingue riuscito.

L’utente ha confermato il funzionamento delle anteprime, inclusa la 0.4.
La RC1 non è stata avviata su Windows nell’ambiente di sviluppo. La build
completa del motore è bloccata dalle dipendenze OpenGL mancanti; CTest del
gioco non eseguito. Il pacchetto usa l’eseguibile già installato dall’utente.
[Registro delle verifiche](docs/verification.json).

## Sorgenti e ricostruzione

Servono Python >=3.12, Git, GNU gettext, CMake >=3.16 e compilatore C++17.
I pin delle release ufficiali sono in `tools/prepare.py`.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
git clone https://github.com/colobot/colobot.git ../colobot
git clone https://github.com/colobot/colobot-data.git ../colobot-data
.venv/bin/python tools/prepare.py --engine ../colobot --data ../colobot-data --output build/prepared
.venv/bin/python tools/validate.py --require-complete --engine build/prepared/colobot --data build/prepared/colobot-data
.venv/bin/python tools/test_localization_checks.py
.venv/bin/python tools/test_code_comments.py
.venv/bin/python tools/test_code_preservation.py
.venv/bin/python tools/test_package_links.py
g++ -std=c++17 -I build/prepared/colobot/src build/prepared/colobot/src/common/language.cpp tools/test_language.cpp -o build/test_language
build/test_language
cmake -S build/prepared/colobot-data -B build/data -DTRANSLATIONS=ON
cmake --build build/data -j2
COLOBOT_DATA_SOURCE=build/prepared/colobot-data .venv/bin/python tools/package_windows_preview.py --data-build build/data --data-source build/prepared/colobot-data --output dist/colobot-0.2.2-alpha-win64-italiano-1.0-rc1.zip
.venv/bin/python tools/test_package_links.py --archive dist/colobot-0.2.2-alpha-win64-italiano-1.0-rc1.zip
```

Il preparatore usa archivi dei commit fissati, preserva i checkout originali
e rifiuta di sovrascrivere la destinazione. Il confezionatore verifica anche
la corrispondenza tra cataloghi e dati generati. Per ricostruire lo ZIP dai
sorgenti inclusi, usa lo stesso layout di cartelle descritto sopra.

Per una versione nativa, installare le dipendenze indicate nell’[analisi](docs/ANALISI.md),
applicare la patch, rendere disponibile la locale `it_IT.UTF-8`, compilare il
motore ed eseguire CTest e le prove di selezione/rendering.
Nessuna modifica è stata inviata ai repository ufficiali.

[Glossario](docs/GLOSSARIO.md).
Licenza GPL v3 o successiva, come i progetti upstream. Per nuove release,
aggiornare i pin dopo il confronto dei sorgenti e usare `msgmerge`, revisionando
le voci fuzzy e le correzioni esplicite in `tools/review_rules.py`.
