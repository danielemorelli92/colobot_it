# Colobot: Gold Edition — Italian translation / Traduzione italiana

[English](#english) | [Italiano](#italiano)

## English

Italian translation of the interface, missions and SatCom, prepared for native
integration into the official `dev` branches.

Upstream discussion: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Contribution

- Native **Italiano** language selection: `it`, Italian UTF-8 locale and data
  language code `I`. Existing language identifiers are preserved.
- **146 catalogs and 5,188 translated entries**, with no empty or fuzzy entries
  and both Italian plural forms.
- Translated example comments, with executable code, identifiers and string
  literals preserved.
- Regenerated `help/cbot` and `help/generic` POT files to cover English source
  text missing from the pinned upstream templates.

The upstream commits are pinned in [upstream.json](upstream.json).

### Review and verification

- [Build, validate and export the contribution](docs/BUILDING.md)
- [Recorded Linux and Windows test results and limitations](docs/TESTING.md)
- [Italian terminology and code/markup preservation rules](docs/GLOSSARY.md)
- [Official translation guidelines](https://github.com/colobot/colobot/wiki/Working-with-translations)

Builds and all 205 enabled CTest tests passed on Linux and Windows. Local Windows
checks also covered Italian menus and SatCom, language persistence, and
saving/loading in the first mission. See the test report for the scope of these
checks and the two tests already disabled upstream.

### Repository layout

| Path | Purpose |
|---|---|
| [translations/colobot](translations/colobot) | Engine and desktop Italian catalogs for `colobot/colobot`. |
| [translations/colobot-data](translations/colobot-data) | Italian data catalogs and two updated templates for `colobot/colobot-data`. |
| [patches/colobot-dev-italian.patch](patches/colobot-dev-italian.patch) | Native language registration and two language tests. |
| [tools](tools) | Source preparation, localization checks and export of the two upstream patches. |

### License and provenance

GPL v3 or later, like Colobot and Colobot Data; see [LICENSE](LICENSE).
The translation was prepared with AI assistance and reviewed in game by an
Italian speaker. This repository contains a proposed contribution, not an
official Colobot release.

The earlier community Windows package for 0.2.2-alpha and its installation guide
remain available in the [archived 1.0 release](https://github.com/danielemorelli92/colobot_it/blob/italiano-v1.0/docs/RELEASE-1.0.md).

---

## Italiano

Traduzione italiana dell’interfaccia, delle missioni e del SatCom, preparata per
l’integrazione nativa nei rami `dev` ufficiali.

Discussione sul contributo: [colobot/colobot#1902](https://github.com/colobot/colobot/issues/1902).

### Contenuto del contributo

- Selezione nativa di **Italiano**: `it`, locale italiana UTF-8 e codice dei dati
  `I`. Gli identificatori delle lingue esistenti sono preservati.
- **146 cataloghi e 5.188 voci tradotte**, nessuna vuota o fuzzy ed entrambe le
  forme dei plurali italiani.
- Commenti degli esempi tradotti, preservando codice eseguibile, identificatori
  e stringhe dei programmi.
- POT `help/cbot` e `help/generic` rigenerati per includere i testi inglesi
  mancanti nei template dei commit ufficiali fissati.

I commit ufficiali di riferimento sono fissati in [upstream.json](upstream.json).

### Revisione e verifiche

La documentazione tecnica seguente è in inglese per facilitare la revisione dei
manutentori:

- [Compilare, validare ed esportare il contributo](docs/BUILDING.md)
- [Risultati e limiti dei test Linux e Windows](docs/TESTING.md)
- [Terminologia italiana e regole per codice e marcatori](docs/GLOSSARY.md)
- [Linee guida ufficiali per le traduzioni](https://github.com/colobot/colobot/wiki/Working-with-translations)

Compilazione e tutti i 205 test CTest abilitati sono riusciti su Linux e Windows.
Il collaudo locale Windows ha verificato anche menu e SatCom in italiano,
persistenza della lingua e salvataggio/ricaricamento nella prima missione.
Il rapporto dei test descrive l’ambito delle verifiche e i due test già
disabilitati dal progetto ufficiale.

### Struttura della repository

| Percorso | Contenuto |
|---|---|
| [translations/colobot](translations/colobot) | Cataloghi italiani del motore e del desktop per `colobot/colobot`. |
| [translations/colobot-data](translations/colobot-data) | Cataloghi italiani dei dati e due template aggiornati per `colobot/colobot-data`. |
| [patches/colobot-dev-italian.patch](patches/colobot-dev-italian.patch) | Registrazione nativa della lingua e due test delle lingue. |
| [tools](tools) | Preparazione dei sorgenti, controlli della traduzione ed esportazione delle due patch. |

### Licenza e provenienza

GPL v3 o successiva, come Colobot e Colobot Data; vedere [LICENSE](LICENSE).
La traduzione è stata preparata con assistenza AI e revisionata nel gioco da
un utente italofono. Questa repository contiene una proposta di contributo,
non una release ufficiale di Colobot.

Il precedente pacchetto comunitario Windows per la 0.2.2-alpha e la relativa guida
restano disponibili nella [versione 1.0 archiviata](https://github.com/danielemorelli92/colobot_it/blob/italiano-v1.0/docs/RELEASE-1.0.md).
