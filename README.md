# Colobot: Gold Edition — Italian translation / Traduzione italiana

[English](#english) | [Italiano](#italiano)

## English

Italian translation of the interface, missions and SatCom, with sources prepared
for native integration into Colobot.

Upstream proposal: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Native integration in dev

The main branch contains the contribution for the official commits pinned in
[upstream.json](upstream.json). It includes **146 catalogs, 5,188 translated
entries, no empty or fuzzy entries**, both Italian plural forms, and a patch to
select **Italiano** in the standard executable (`it`, Italian UTF-8 locale,
data language code `I`). Existing language codes remain unchanged.

Building the data revealed that two upstream POT files were out of date with
the English sources. These templates have been regenerated, and the corresponding
entries, including `searchall` and loop labels, are translated. Executable code,
identifiers and program string literals are preserved; example comments are
translated.

- [Test results and limitations — in Italian](docs/VERIFICHE.md)
- [Glossary — in Italian](docs/GLOSSARIO.md)

The community Windows package has been tested in game. The native integration
has been built and run on Linux. Local Windows checks confirmed successful
compilation, installation, 205 automated tests and graphical startup, along with
Italian menus and SatCom, language persistence after restarting, and saving/loading
in the first mission. This is not an official Colobot distribution.

### Playing on Windows with 0.2.2-alpha

[Download the stable Italian translation 1.0](dist/colobot-0.2.2-alpha-win64-italiano-1.0.zip)
— on GitHub, click **Download raw file**.

Close the game, extract everything into the folder containing `colobot.exe` and
`data`, replace any files from the previous translation, and run
`Avvia-Italiano.cmd`. Keep **French** selected in the settings: this package uses
that language slot to work with the already released official executable.
Saves and settings remain in `%LOCALAPPDATA%\ColobotItalianPreview-0.1`.

[Installation and removal — in Italian](docs/RELEASE-1.0.md). The 1.0 ZIP and its
SHA256 are unchanged. Its sources and original tools are preserved in the
[`italiano-v1.0` tag](https://github.com/danielemorelli92/colobot_it/tree/italiano-v1.0).

### Preparing the sources

You need Python >=3.12, Git, CMake >=3.21, a C++20 compiler, GNU gettext and the
dependencies listed in the [project instructions](https://github.com/colobot/colobot/blob/dev/docs/README-dev.md).
On Debian/Ubuntu, also install `nlohmann-json3-dev` and `libgtest-dev` to use the
system libraries instead of the corresponding submodules. The commands below
are for Linux and build the engine and data with desktop integration and manpages
disabled. On Windows/MSYS2, use **`-DDESKTOP=ON`** to generate `colobot.rc`, which
the executable requires. The desktop catalog is checked by gettext regardless.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
git clone --branch dev https://github.com/colobot/colobot.git build/src/colobot
git clone --branch dev https://github.com/colobot/colobot-data.git build/src/colobot-data
.venv/bin/python tools/prepare.py --engine build/src/colobot --data build/src/colobot-data --output build/prepared
.venv/bin/python tools/validate.py --require-complete --engine build/prepared/colobot --data build/prepared/colobot-data
cmake -S build/prepared/colobot -B build/engine -DTESTS=ON -DDESKTOP=OFF -DPORTABLE=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PWD/build/install"
cmake --build build/engine --parallel 2
ctest --test-dir build/engine --output-on-failure
cmake --install build/engine
cmake -S build/prepared/colobot-data -B build/data -DTRANSLATIONS=ON -DCOLOBOT_INSTALL_DATA_DIR="$PWD/build/install/data"
cmake --build build/data --parallel 2
cmake --install build/data
.venv/bin/python tools/test_complete_data.py --build build/data --source build/prepared/colobot-data
.venv/bin/python tools/check_links.py --data-build build/data
.venv/bin/python tools/test_code_preservation.py
.venv/bin/python tools/test_code_comments.py
.venv/bin/python tools/test_localization_checks.py
```

The preparation tool uses archives of the pinned commits, applies the translations
and patch in a new destination, and preserves the original checkouts. To test
native startup from a graphical Linux session:

```sh
cd build/install
XDG_DATA_HOME="$PWD/xdg" LC_ALL=it_IT.UTF-8 ./colobot -savedir "$PWD/native-profile"
```

Run the program from the installation folder: this portable build resolves data
paths relative to the current working directory. In MSYS2, run `./colobot.exe`
from the same folder. The Italian locale must be available on Linux. You can also
select **Italiano** in the game settings. Use a test profile separate from your
0.2.2-alpha profile, since `dev` is a newer version of the engine.

### Exporting the patches

```sh
.venv/bin/python tools/export_upstream.py --engine build/src/colobot --data build/src/colobot-data --output build/prs
```

The command produces `colobot-italian.patch` and `colobot-data-italian.patch` for
application to the respective forks of the official repositories at the pinned
commits. The first contains language registration, engine catalogs and tests;
the second contains the data catalogs and the two regenerated POT files.
Outputs remain under `build/`.

### License and contributions

GPL v3 or later, like Colobot and Colobot Data; see [LICENSE](LICENSE).
The translation was prepared with AI assistance and reviewed in game by an
Italian speaker. Translation reports are welcome: include the version, game
mode, mission or exercise, page and text. For visual issues, also include the
resolution and a screenshot.

---

## Italiano

Traduzione italiana dell’interfaccia, delle missioni e del SatCom, con sorgenti
pronti per proporre l’integrazione nativa nel progetto Colobot.

Proposta di integrazione: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Integrazione nativa in dev

Il ramo principale contiene il contributo per i commit ufficiali fissati in
[upstream.json](upstream.json). Include **146 cataloghi, 5.188 voci compilate,
zero vuote o fuzzy**, entrambe le forme dei plurali italiani e la patch per
selezionare **Italiano** nell’eseguibile normale (`it`, locale italiana UTF-8,
codice dei dati `I`). I codici delle lingue esistenti restano invariati.

La build dei dati ha evidenziato due POT ufficiali arretrati rispetto ai testi
inglesi: sono stati rigenerati e le relative voci, fra cui `searchall` e le
etichette dei cicli, sono tradotte. Codice eseguibile, identificatori e stringhe
dei programmi sono preservati; i commenti degli esempi sono tradotti.

- [Risultati e limiti delle verifiche](docs/VERIFICHE.md)
- [Glossario](docs/GLOSSARIO.md)

La versione comunitaria Windows è stata provata dall’utente. L’integrazione
nativa è stata compilata e avviata su Linux. Sul PC Windows dell’utente sono
riuscite compilazione, installazione, 205 test automatici e avvio grafico;
l’utente ha confermato menu e SatCom in italiano, persistenza della lingua al
riavvio e salvataggio/ricaricamento nella prima missione. Questa non è una
distribuzione ufficiale di Colobot.

### Giocare su Windows con la 0.2.2-alpha

[Scarica la traduzione stabile 1.0](dist/colobot-0.2.2-alpha-win64-italiano-1.0.zip)
— su GitHub premi **Download raw file**.

Chiudi il gioco, estrai tutto nella cartella con `colobot.exe` e `data`,
sostituisci i file della traduzione precedente e avvia `Avvia-Italiano.cmd`.
Mantieni **French** nelle impostazioni: il pacchetto usa quello slot per
funzionare con l’eseguibile ufficiale già distribuito. Salvataggi e impostazioni
restano in `%LOCALAPPDATA%\ColobotItalianPreview-0.1`.

[Installazione e rimozione](docs/RELEASE-1.0.md). Lo ZIP 1.0 e il suo SHA256
sono invariati. I suoi sorgenti e gli strumenti originali sono conservati nel
[tag `italiano-v1.0`](https://github.com/danielemorelli92/colobot_it/tree/italiano-v1.0).

### Preparare i sorgenti

Servono Python >=3.12, Git, CMake >=3.21, un compilatore C++20, GNU gettext e
le dipendenze indicate nelle [istruzioni del progetto](https://github.com/colobot/colobot/blob/dev/docs/README-dev.md).
Su Debian/Ubuntu servono inoltre `nlohmann-json3-dev` e `libgtest-dev` per usare
le librerie di sistema al posto dei rispettivi submodule. I comandi seguenti
sono per Linux e compilano il motore e i dati con desktop e manpage disabilitati.
Su Windows/MSYS2 usare **`-DDESKTOP=ON`**: serve a generare `colobot.rc`,
richiesto dall’eseguibile. Il catalogo desktop viene comunque controllato da gettext.

```sh
python3 -m venv .venv
.venv/bin/pip install -r tools/requirements.txt
git clone --branch dev https://github.com/colobot/colobot.git build/src/colobot
git clone --branch dev https://github.com/colobot/colobot-data.git build/src/colobot-data
.venv/bin/python tools/prepare.py --engine build/src/colobot --data build/src/colobot-data --output build/prepared
.venv/bin/python tools/validate.py --require-complete --engine build/prepared/colobot --data build/prepared/colobot-data
cmake -S build/prepared/colobot -B build/engine -DTESTS=ON -DDESKTOP=OFF -DPORTABLE=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PWD/build/install"
cmake --build build/engine --parallel 2
ctest --test-dir build/engine --output-on-failure
cmake --install build/engine
cmake -S build/prepared/colobot-data -B build/data -DTRANSLATIONS=ON -DCOLOBOT_INSTALL_DATA_DIR="$PWD/build/install/data"
cmake --build build/data --parallel 2
cmake --install build/data
.venv/bin/python tools/test_complete_data.py --build build/data --source build/prepared/colobot-data
.venv/bin/python tools/check_links.py --data-build build/data
.venv/bin/python tools/test_code_preservation.py
.venv/bin/python tools/test_code_comments.py
.venv/bin/python tools/test_localization_checks.py
```

Il preparatore usa archivi dei commit fissati, applica le traduzioni e la patch
in una destinazione nuova e preserva i checkout originali. Per provare l’avvio
nativo da una sessione grafica Linux:

```sh
cd build/install
XDG_DATA_HOME="$PWD/xdg" LC_ALL=it_IT.UTF-8 ./colobot -savedir "$PWD/native-profile"
```

Avviare il programma dalla cartella di installazione: questa build portatile
cerca i dati rispetto alla cartella corrente. In MSYS2 usare `./colobot.exe`
dalla stessa cartella. La locale italiana deve essere disponibile su Linux. È possibile anche selezionare
**Italiano** nelle opzioni del gioco. Usare un profilo di prova distinto da quello
della 0.2.2-alpha, perché `dev` è una versione successiva del motore.

### Esportare le patch

```sh
.venv/bin/python tools/export_upstream.py --engine build/src/colobot --data build/src/colobot-data --output build/prs
```

Il comando produce `colobot-italian.patch` e `colobot-data-italian.patch`, da
applicare ai rispettivi fork dei repository ufficiali sui commit fissati.
La prima contiene registrazione, cataloghi del motore e test; la seconda i
cataloghi dei dati e i due POT rigenerati. Gli output restano in `build/`.

### Licenza e contributi

GPL v3 o successiva, come Colobot e Colobot Data; vedere [LICENSE](LICENSE).
La traduzione è stata preparata con assistenza AI e revisionata nel gioco da
un utente italofono. Le segnalazioni linguistiche restano benvenute: indicare
versione, modalità, missione o esercizio, pagina e frase; per problemi visivi
aggiungere risoluzione e screenshot.
